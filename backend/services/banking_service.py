import os
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime

from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Tool, FunctionDeclaration, Content
from fastapi import WebSocket, WebSocketDisconnect

from backend.tools.banking_tools import BankingTools
from backend.models.schemas import ChatSession, ChatMessage

class BankingAIService:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_REGION", "us-central1")
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        self.dataset_id = os.getenv("BQ_DATASET_ID", "nova_banking_data_v2")
        
        # Initialize clients
        self.speech_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()
        self.bq_client = bigquery.Client(project=self.project_id)
        
        # Initialize MCP Server (Local Integration)
        from backend.mcp_server import MCPBankingServer
        self.mcp_server = MCPBankingServer()
        
        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(
            "gemini-2.0-flash-001",
            tools=[self._get_vertex_tools()]
        )
        
        self.sessions: Dict[str, ChatSession] = {}

    def _get_vertex_tools(self) -> Tool:
        """Convert MCP tools to Vertex AI FunctionDeclarations"""
        mcp_tools = self.mcp_server.get_available_tools()
        
        declarations = []
        for tool in mcp_tools:
            # Convert JSON schema types to Vertex AI types (simplified mapping)
            # Vertex AI expects specific schema structure
            
            # Handle both object and dict access for robustness
            name = tool.name if hasattr(tool, 'name') else tool['name']
            description = tool.description if hasattr(tool, 'description') else tool['description']
            input_schema = tool.input_schema if hasattr(tool, 'input_schema') else tool['input_schema']
            
            declarations.append(
                FunctionDeclaration(
                    name=name,
                    description=description,
                    parameters=input_schema
                )
            )
            
        return Tool(function_declarations=declarations)

    async def execute_function(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool functions via MCP"""
        try:
            print(f"Executing MCP tool: {function_name} with args: {args}")
            return await self.mcp_server.handle_tool_call(function_name, args)
        except Exception as e:
            print(f"MCP Execution Error: {e}")
            return {"error": str(e)}

    async def check_proactive_insights(self, user_id: str) -> Optional[str]:
        """Check for anomalies or cashflow issues to proactively notify user"""
        try:
            # Run checks in parallel
            anomalies_task = self.banking_tools.detect_anomalies({"user_id": user_id, "sensitivity": 7.0})
            cashflow_task = self.banking_tools.predict_cashflow({"user_id": user_id, "forecast_days": 30})
            
            anomalies, cashflow = await asyncio.gather(anomalies_task, cashflow_task)
            
            insights = []
            
            if anomalies.get("count", 0) > 0:
                insights.append(f"I noticed {anomalies['count']} unusual transactions recently.")
                
            if cashflow.get("status") == "risk":
                insights.append("Your projected balance might dip below zero in the next 30 days based on current spending.")
                
            if insights:
                return "By the way, " + " ".join(insights)
                
        except Exception as e:
            print(f"Error checking insights: {e}")
            
        return None

    async def stream_response(self, websocket: WebSocket, session_id: str, text_input: str):
        """Helper to stream text and audio response"""
        full_response_text = ""
        sentence_buffer = ""
        print(f"Streaming response for: {text_input}")
        
        async for chunk in self.process_with_vertex(session_id, text_input):
            print(f"Chunk received: {chunk}")
            full_response_text += chunk
            sentence_buffer += chunk
            
            # Simple sentence detection (split by . ! ?)
            # If buffer contains a sentence ending, process it
            if any(punct in sentence_buffer for punct in [".", "!", "?", "\n"]):
                # Split into sentences, keep delimiters
                # Regex: Split by .!? followed by space or end of string, OR newline
                # This avoids splitting "3.50" or "Mr. Smith" (mostly)
                import re
                sentences = re.split(r'([.!?](?:\s+|$)|[\n]+)', sentence_buffer)
                
                # Process all complete sentences
                for i in range(0, len(sentences) - 1, 2):
                    sentence = sentences[i] + sentences[i+1]
                    if sentence.strip():
                        # Send text chunk
                        await websocket.send_json({"type": "response", "text": sentence})
                        
                        # Synthesize and send audio immediately
                        audio_response = await self.synthesize_speech(sentence)
                        await websocket.send_bytes(audio_response)
                
                # Keep the remainder in buffer
                sentence_buffer = sentences[-1]
        
        # Process any remaining text in buffer
        if sentence_buffer.strip():
             await websocket.send_json({"type": "response", "text": sentence_buffer})
             audio_response = await self.synthesize_speech(sentence_buffer)
             await websocket.send_bytes(audio_response)

    async def process_audio_stream(self, websocket: WebSocket, user_id: str):
        """Handle bidirectional audio streaming"""
        session_id = str(uuid.uuid4())
        
        # Create session
        self.sessions[session_id] = ChatSession(
            session_id=session_id,
            user_id=user_id,
            history=[
                ChatMessage(
                    role="user", 
                    content=f"""System Context: 
You are Nova, an advanced AI Banking Assistant. 
Your goal is to help the user with their banking needs efficiently and securely.
The current user ID is '{user_id}'. Use this ID for all tool calls.

Guidelines:
1. **Voice-First**: You are speaking to the user. Keep responses CONCISE and conversational. Avoid long lists or markdown formatting unless necessary.
2. **Proactive**: If you see an issue (like low balance), mention it gently.
3. **Secure**: Never ask for passwords. For sensitive actions (transfers), ask for confirmation.
4. **Tools**: You have access to real-time data. Use `get_account_balance`, `get_recent_transactions`, etc. to answer questions accurately.
5. **Personality**: Professional, warm, and helpful.

Examples:
User: "What is my balance?"
Nova: "Your current checking account balance is $5,200.50."

User: "Transfer 500 dollars to Mom."
Nova: "I can help with that. Just to confirm, you want to transfer $500 to 'Mom'? Please provide your PIN to proceed."

User: "How much did I spend on coffee?"
Nova: "I found 3 recent transactions for coffee totaling $45.20."

Do not ask the user for their ID. You already have it."""
                ),
                ChatMessage(
                    role="model",
                    content="Understood. I am Nova. I will follow these guidelines and examples to provide concise, voice-optimized banking assistance."
                )
            ]
        )
        
        try:
            # Check for proactive insights on connection
            # proactive_msg = await self.check_proactive_insights(user_id)
            # if proactive_msg:
            #      # Synthesize and send proactive message
            #     audio_response = await self.synthesize_speech(proactive_msg)
            #     await websocket.send_json({"type": "response", "text": proactive_msg})
            #     await websocket.send_bytes(audio_response)

            while True:
                data = await websocket.receive()
                
                if "bytes" in data:
                    audio_data = data["bytes"]
                    transcript = await self.transcribe_audio(audio_data)
                    
                    if transcript:
                        # Log user message
                        await self.log_conversation(user_id, transcript, "")
                        
                        await websocket.send_json({"type": "transcript", "text": transcript})
                        
                        # Use shared streaming helper
                        await self.stream_response(websocket, session_id, transcript)
                
                elif "text" in data:
                    # Handle text ping/pong and user messages
                    message = json.loads(data["text"])
                    if message.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                    elif message.get("text"):
                        user_text = message["text"]
                        
                        # Log user message
                        await self.log_conversation(user_id, user_text, "")
                        
                        # Use shared streaming helper (now includes Audio!)
                        await self.stream_response(websocket, session_id, user_text)

        except WebSocketDisconnect:
            print(f"Session {session_id} disconnected")
        except Exception as e:
            print(f"Error in session {session_id}: {e}")
        finally:
            if session_id in self.sessions:
                del self.sessions[session_id]

    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000, # WebM Opus is usually 48kHz
            language_code="en-US",
            enable_automatic_punctuation=True,
            model="latest_long"
        )
        audio = speech.RecognitionAudio(content=audio_data)
        
        try:
            response = self.speech_client.recognize(config=config, audio=audio)
            if response.results:
                return response.results[0].alternatives[0].transcript
        except Exception as e:
            print(f"Transcription error: {e}")
        return None

    async def process_with_vertex(self, session_id: str, text: str) -> AsyncGenerator[str, None]:
        session = self.sessions[session_id]
        
        # Add user message to history
        session.history.append(ChatMessage(role="user", content=text))
        
        full_response = ""
        
        try:
            # Convert history to Gemini format
            history_gemini = [
                Content(role=msg.role, parts=[Part.from_text(msg.content)])
                for msg in session.history[:-1] # Exclude current
            ]
            
            chat = self.model.start_chat(history=history_gemini)
            # Use stream=True for streaming response
            responses = await chat.send_message_async(text, stream=True)
            
            async for response in responses:
                # Handle function calls (usually come in the first chunk if applicable)
                if response.candidates and response.candidates[0].content.parts:
                    part = response.candidates[0].content.parts[0]
                    
                    if part.function_call:
                        # Function calls usually don't stream well in V1, so we might need to accumulate or handle differently
                        # For simplicity in this demo, if function call is detected, we might need to wait for full response or handle it.
                        # However, send_message_async with stream=True yields chunks.
                        # If it's a function call, the first chunk usually contains it.
                        
                        func_name = part.function_call.name
                        func_args = dict(part.function_call.args)
                        func_args["user_id"] = session.user_id
                        
                        result = await self.execute_function(func_name, func_args)
                        
                        # Send function result back to model and get streaming response
                        function_response_stream = await chat.send_message_async(
                            Part.from_function_response(
                                name=func_name,
                                response=result
                            ),
                            stream=True
                        )
                        
                        async for chunk in function_response_stream:
                            if chunk.text:
                                # Filter out raw tool outputs or JSON
                                text_chunk = chunk.text.strip()
                                if text_chunk.startswith("```tool_outputs") or text_chunk.startswith('{"'):
                                    print(f"Filtered raw tool output: {text_chunk}")
                                    continue
                                    
                                full_response += chunk.text
                                yield chunk.text
                        return # End after function response

                    elif part.text:
                        full_response += part.text
                        yield part.text

            session.history.append(ChatMessage(role="model", content=full_response))

        except Exception as e:
            print(f"Vertex AI Error: {e}")
            # Fallback for disabled API
            fallback_text = "I'm having trouble connecting to Vertex AI. "
            
            text_lower = text.lower()
            if "balance" in text_lower:
                balance = await self.banking_tools.get_account_balance({"user_id": session.user_id})
                fallback_text += f"But I can check your balance directly: ${balance['balance']:,.2f}"
            elif "transaction" in text_lower:
                txs = await self.banking_tools.get_recent_transactions({"user_id": session.user_id, "limit": 3})
                fallback_text += f"Here are your recent transactions: {len(txs)} found."
            elif "hi" in text_lower or "hello" in text_lower:
                fallback_text += "Please enable the Vertex AI API in Google Cloud Console to chat with me properly."
            else:
                fallback_text += "Please enable the Vertex AI API to use full features."
                
            session.history.append(ChatMessage(role="model", content=fallback_text))
            yield fallback_text


    async def synthesize_speech(self, text: str) -> bytes:
        if not self.tts_client:
            return b""
            
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Journey-D", # Premium Journey voice
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = self.tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        return response.audio_content

    async def log_conversation(self, user_id: str, user_message: str, ai_response: str):
        rows_to_insert = [{
            "conversation_id": str(uuid.uuid4()),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "ai_response": ai_response,
            "intent": "banking_query",
            "sentiment": 0.0
        }]
        table_ref = f"{self.project_id}.{self.dataset_id}.conversations"
        try:
            errors = self.bq_client.insert_rows_json(table_ref, rows_to_insert)
            if errors:
                print(f"BigQuery insert errors: {errors}")
        except Exception as e:
            print(f"Error logging conversation: {e}")
