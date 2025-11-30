import asyncio
import json
import os
import base64
from google.cloud import speech, texttospeech
import vertexai
from vertexai.generative_models import GenerativeModel
from sqlalchemy import create_engine, text
from data.db import DATABASE_URL
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class GeminiLiveService:
    def __init__(self):
        project_id = os.getenv("PROJECT_ID")
        location = os.getenv("LOCATION", "us-central1")
        vertexai.init(project=project_id, location=location)
        
        self.model = GenerativeModel("gemini-1.5-flash-001")
        self.chat = self.model.start_chat()
        
        self.stt_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()
        
        self.db_engine = create_engine(DATABASE_URL)

    async def process_audio_stream(self, websocket):
        print("Client connected to Live Service (Instrumented)")
        buffer = bytearray()
        
        try:
            async for message in websocket.iter_text():
                data = json.loads(message)
                
                if "text" in data:
                    # Direct text input (Chatbot mode)
                    user_query = data["text"]
                    print(f"Received text input: {user_query}")
                    
                    # Run pipeline directly
                    with tracer.start_as_current_span("process_text_input"):
                        await self._process_text_request(websocket, user_query)

                elif "audio" in data:
                    chunk = base64.b64decode(data["audio"])
                    buffer.extend(chunk)
                    
                    if len(buffer) > 32000: # ~1 second
                        with tracer.start_as_current_span("process_audio_chunk"):
                            await self._process_buffer(websocket, buffer)
                        buffer = bytearray()
                        
                elif "type" in data and data["type"] == "interrupt":
                    buffer = bytearray()
                    print("Interrupted! Clearing buffer.")
                    await websocket.send_json({"type": "interrupt_ack"})

                elif "type" in data and data["type"] == "end_of_speech":
                    print("End of speech detected. Flushing buffer.")
                    if buffer:
                        with tracer.start_as_current_span("flush_audio_buffer"):
                            await self._process_buffer(websocket, buffer)
                        buffer = bytearray()

        except Exception as e:
            print(f"WebSocket error: {e}")

    async def _process_text_request(self, websocket, user_query):
        # Agentic SQL & LLM
        response_text = ""
        ui_action = None
        
        with tracer.start_as_current_span("agentic_pipeline") as span:
            response_text, ui_action = self._run_agentic_pipeline(user_query)
            span.set_attribute("response_text", response_text)
        
        # Send Text Response
        await websocket.send_json({"type": "text_response", "text": response_text})

        if ui_action:
             await websocket.send_json({"type": "ui_action", "data": ui_action})

        # Optional: TTS for text input too? 
        # For now, let's assume text-in -> text-out + audio-out (for consistency with "Assistant" persona)
        if response_text:
            with tracer.start_as_current_span("text_to_speech"):
                synthesis_input = texttospeech.SynthesisInput(text=response_text)
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US", name="en-US-Journey-F"
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                    sample_rate_hertz=24000
                )
                
                tts_response = self.tts_client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )
                
                audio_b64 = base64.b64encode(tts_response.audio_content).decode('utf-8')
                await websocket.send_json({"type": "audio", "data": audio_b64})

    async def _process_buffer(self, websocket, audio_data):
        transcript = ""
        
        # 1. STT
        with tracer.start_as_current_span("speech_to_text") as span:
            audio = speech.RecognitionAudio(content=bytes(audio_data))
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )
            response = self.stt_client.recognize(config=config, audio=audio)
            
            if not response.results:
                return

            transcript = response.results[0].alternatives[0].transcript
            span.set_attribute("transcript", transcript)
            print(f"Heard: {transcript}")
            await websocket.send_json({"type": "transcript", "text": transcript})

        # 2. Agentic SQL & LLM
        response_text = ""
        ui_action = None
        
        with tracer.start_as_current_span("agentic_pipeline") as span:
            response_text, ui_action = self._run_agentic_pipeline(transcript)
            span.set_attribute("response_text", response_text)
        
        if ui_action:
             await websocket.send_json({"type": "ui_action", "data": ui_action})

        # 3. TTS
        if response_text:
            with tracer.start_as_current_span("text_to_speech"):
                synthesis_input = texttospeech.SynthesisInput(text=response_text)
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US", name="en-US-Journey-F"
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                    sample_rate_hertz=24000
                )
                
                tts_response = self.tts_client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )
                
                audio_b64 = base64.b64encode(tts_response.audio_content).decode('utf-8')
                await websocket.send_json({"type": "audio", "data": audio_b64})

    def _run_agentic_pipeline(self, user_query):
        needs_db = any(word in user_query.lower() for word in ["spend", "cost", "how much", "credit", "score", "offer", "deal", "transaction"])
        
        sql_result = None
        ui_action = None
        
        if needs_db:
            with tracer.start_as_current_span("generate_sql") as span:
                print("Agent: Decided to query database.")
                schema_info = """
                Tables:
                - users (id, name, credit_score, account_balance)
                - transactions (id, user_id, date, merchant, category, amount)
                - offers (id, title, description, match_score)
                """
                
                prompt = f"""
                You are a SQL Expert. Convert the user's question into a PostgreSQL query.
                Schema: {schema_info}
                User Question: "{user_query}"
                Return ONLY the SQL query, no markdown, no explanation.
                """
                
                try:
                    sql_response = self.model.generate_content(prompt)
                    sql_query = sql_response.text.strip().replace("```sql", "").replace("```", "")
                    span.set_attribute("generated_sql", sql_query)
                    print(f"Agent Generated SQL: {sql_query}")
                    
                    with tracer.start_as_current_span("execute_sql") as db_span:
                        with self.db_engine.connect() as conn:
                            result = conn.execute(text(sql_query))
                            rows = [dict(row) for row in result.mappings()]
                            sql_result = rows
                            db_span.set_attribute("row_count", len(rows))
                            print(f"DB Result: {sql_result}")
                        
                        # Determine UI Action
                        if "spend" in user_query.lower() and rows:
                            if "category" in rows[0] and "amount" in rows[0]:
                                 chart_data = [{"name": r["category"], "value": r["amount"]} for r in rows]
                                 ui_action = {"type": "RENDER_CHART", "data": chart_data, "title": "Spending Analysis"}
                            elif len(rows[0]) == 2:
                                 keys = list(rows[0].keys())
                                 chart_data = [{"name": r[keys[0]], "value": r[keys[1]]} for r in rows]
                                 ui_action = {"type": "RENDER_CHART", "data": chart_data, "title": "Analysis"}

                        elif "credit" in user_query.lower() and rows:
                            score = rows[0].get("credit_score", 700)
                            ui_action = {"type": "RENDER_CREDIT", "data": {"score": score, "history": [], "factors": []}}
                            
                        elif "offer" in user_query.lower() and rows:
                            ui_action = {"type": "RENDER_OFFERS", "data": rows}

                except Exception as e:
                    print(f"SQL Agent Error: {e}")
                    span.record_exception(e)
                    sql_result = "Error executing database query."

        # Final Response Generation
        with tracer.start_as_current_span("generate_response"):
            context = f"User Query: {user_query}\n"
            if sql_result:
                context += f"Database Data: {sql_result}\n"
            
            response = self.chat.send_message(context)
            return response.text, ui_action


