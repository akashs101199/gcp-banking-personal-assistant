from google.cloud import speech
import os

class STTService:
    def __init__(self):
        self.client = speech.SpeechClient()

    def transcribe_audio(self, audio_content: bytes) -> str:
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="en-US",
        )

        response = self.client.recognize(config=config, audio=audio)

        if not response.results:
            return ""

        # Just return the first alternative of the first result
        return response.results[0].alternatives[0].transcript
