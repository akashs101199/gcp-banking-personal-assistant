import os
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from backend.services.banking_service import BankingAIService
from backend.models.schemas import HealthCheckResponse

# Initialize GCP clients
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION", "us-central1")

# Setup observability
trace.set_tracer_provider(TracerProvider())
cloud_trace_exporter = CloudTraceSpanExporter()
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)
tracer = trace.get_tracer(__name__)

# FastAPI app
app = FastAPI(title="Nova Banking AI Assistant")

FastAPIInstrumentor.instrument_app(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service
banking_service = None

@app.on_event("startup")
async def startup_event():
    global banking_service
    banking_service = BankingAIService()
    print("Banking AI Service initialized")

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for voice chat"""
    
    api_key = websocket.query_params.get("key")
    user_id = websocket.query_params.get("user_id", "demo_user")
    
    expected_key = os.getenv("API_KEY")
    
    if not expected_key or api_key != expected_key:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    await websocket.accept()
    
    try:
        if banking_service:
            await banking_service.process_audio_stream(websocket, user_id)
        else:
            await websocket.close(code=1011, reason="Service not initialized")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "nova-banking-ai"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)