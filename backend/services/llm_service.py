import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration
import os
import json
from data.mock_data import mock_db

class LLMService:
    def __init__(self):
        project_id = os.getenv("PROJECT_ID")
        location = os.getenv("LOCATION", "us-central1")
        vertexai.init(project=project_id, location=location)
        
        # Define Tools
        get_spend_analysis_func = FunctionDeclaration(
            name="get_spend_analysis",
            description="Get the user's spending analysis broken down by category for the last 90 days. Use this when the user asks about their spending, expenses, or budget.",
            parameters={
                "type": "object",
                "properties": {},
            },
        )

        get_credit_score_func = FunctionDeclaration(
            name="get_credit_score",
            description="Get the user's current credit score, history, and contributing factors. Use this when the user asks about their credit score or credit health.",
            parameters={
                "type": "object",
                "properties": {},
            },
        )

        get_offers_func = FunctionDeclaration(
            name="get_offers",
            description="Get personalized financial offers and recommendations for the user. Use this when the user asks for deals, offers, or recommendations.",
            parameters={
                "type": "object",
                "properties": {},
            },
        )

        banking_tool = Tool(
            function_declarations=[
                get_spend_analysis_func,
                get_credit_score_func,
                get_offers_func,
            ],
        )

        self.model = GenerativeModel(
            "gemini-1.5-flash-001",
            tools=[banking_tool],
        )
        self.chat = self.model.start_chat()

    def generate_response(self, text: str):
        response = self.chat.send_message(text)
        
        part = response.candidates[0].content.parts[0]
        
        # Check if it's a function call
        if part.function_call:
            function_name = part.function_call.name
            print(f"Function Call Triggered: {function_name}")
            
            api_response = {}
            ui_action = None
            
            if function_name == "get_spend_analysis":
                data = mock_db.get_spend_analysis()
                api_response = {"analysis": data}
                ui_action = {"type": "RENDER_CHART", "data": data, "title": "Spending Analysis (Last 90 Days)"}
                
            elif function_name == "get_credit_score":
                data = mock_db.get_credit_score_details()
                api_response = data
                ui_action = {"type": "RENDER_CREDIT", "data": data}
                
            elif function_name == "get_offers":
                data = mock_db.get_recommendations()
                api_response = {"offers": data}
                ui_action = {"type": "RENDER_OFFERS", "data": data}
            
            # Send the API response back to Gemini to get the natural language summary
            response = self.chat.send_message(
                vertexai.generative_models.Part.from_function_response(
                    name=function_name,
                    response=api_response,
                )
            )
            
            return {
                "text": response.text,
                "ui_action": ui_action
            }
            
        else:
            return {
                "text": response.text,
                "ui_action": None
            }
