import whisper
from pathlib import Path

class WhisperTranscriber:
    def __init__(self, model_name="turbo", device="cpu", language="zh"):
        self.model = whisper.load_model(model_name).to(device)
        self.language = language
    
    def transcribe(self, audio_file):
        """
        转录音频文件
        """
        result = self.model.transcribe(
            str(audio_file),
            language=self.language
        )
        return result["text"]
    
    def transcribe_with_timestamps(self, audio_file):
        """
        转录音频文件并返回带时间戳的段落
        """
        result = self.model.transcribe(
            str(audio_file),
            language=self.language,
            verbose=False
        )
        return result["segments"] 