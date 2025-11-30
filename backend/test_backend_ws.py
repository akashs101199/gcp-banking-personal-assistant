import asyncio
import websockets
import json
import base64
import os
import sys

# Configuration
API_KEY = "secret-demo-key-12345"  # Matching .env
WS_URL = f"ws://localhost:8080/ws/chat?key={API_KEY}&user_id=user_001"

async def test_websocket():
    print(f"Connecting to {WS_URL}...")
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✓ Connected to WebSocket")
            
            # 1. Wait for initial greeting (Proactive Insights)
            print("Waiting for initial response...")
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(response)
                if "audio" in data:
                    print("✓ Received audio response (Greeting/Insights)")
                if "text" in data:
                    print(f"✓ Received text response: {data['text']}")
            except asyncio.TimeoutError:
                print("! Timed out waiting for initial greeting")

            # 2. Send a text message (simulated audio input trigger or direct text if supported)
            # Note: The backend expects audio stream, but let's see if we can trigger it or if we need to send mock audio.
            # Looking at banking_service.py, process_audio_stream expects audio bytes.
            # Let's send a simple "ping" or empty audio frame to see if it keeps connection alive.
            
            # For this test, we might just verify connection and initial insight generation.
            # To truly test "chat", we'd need to send valid audio or modify service to accept text input for testing.
            # Drain the audio message (proactive insight audio)
            try:
                audio_msg = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"Received audio bytes: {len(audio_msg)} bytes")
            except asyncio.TimeoutError:
                print("No audio message received")

            # Send a text message
            print("Sending text message: 'What is my balance?'")
            await websocket.send(json.dumps({"text": json.dumps({"text": "What is my balance?"})}))
            
            # Loop to receive multiple streaming responses
            print("Waiting for streaming responses...")
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    if isinstance(response, bytes):
                        print(f"✓ Received audio bytes: {len(response)} bytes")
                        break # Success!
                    else:
                        print(f"Received response: {response}")
            except asyncio.TimeoutError:
                print("! Timed out waiting for audio")
            
            # Send mock audio end signal (not needed for text test, but keeping structure)
            # await websocket.send(json.dumps({"text": json.dumps({"type": "ping"})}))
            
            print("Closing connection...")
            await websocket.close()
            print("✓ Connection closed cleanly")
            return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    # Ensure API_KEY matches what the server expects
    if not os.getenv("API_KEY"):
        os.environ["API_KEY"] = API_KEY
        
    try:
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        print("\nTest interrupted")
