import aiohttp
import io
import numpy as np
import librosa
import soundfile as sf
import logging
import tempfile
import os
from urllib.parse import urlparse

logger = logging.getLogger("audio-processor")

async def process_url(url: str) -> bytes:
    """
    Download and process audio from URL with format validation
    Returns raw PCM data in 16kHz 16-bit mono format
    """
    try:
        # Validate URL scheme
        if urlparse(url).scheme not in ("http", "https"):
            raise ValueError("Invalid URL scheme")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError(f"HTTP error {response.status}")

                content_type = response.headers.get('Content-Type', '')
                if 'audio' not in content_type and 'octet-stream' not in content_type:
                    raise ValueError("Unsupported content type")

                # Download the audio data
                raw_data = await response.read()

        # Create a temporary file to save the audio data
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(raw_data)
            temp_file_path = temp_file.name

        try:
            # Load audio using librosa
            audio, sr = librosa.load(temp_file_path, sr=16000, mono=True)
            
            # Normalize the audio to [-1, 1]
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio))
            
            # Convert to 16-bit PCM
            audio_int16 = (audio * 32767).astype(np.int16)
            
            # Convert to bytes
            audio_bytes = audio_int16.tobytes()
            
            return audio_bytes
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"Audio processing failed: {str(e)}")
        raise RuntimeError(f"Audio processing error: {str(e)}") from e