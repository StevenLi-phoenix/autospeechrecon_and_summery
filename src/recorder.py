import pyaudio
import wave
import threading
import time
from pathlib import Path

class AudioRecorder:
    def __init__(self, save_dir="recordings", chunk=1024, format=pyaudio.paFloat32,
                 channels=1, rate=16000, interval=60):
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        self.interval = interval  # 录音间隔(秒)
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.is_recording = False
        
    def start_recording(self):
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()
    
    def stop_recording(self):
        self.is_recording = False
        self.recording_thread.join()
    
    def _record(self):
        stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        start_time = time.time()
        
        while self.is_recording:
            self.frames.append(stream.read(self.chunk))
            
            # 每隔interval秒保存一段录音
            if time.time() - start_time >= self.interval:
                self._save_segment(start_time)
                self.frames = []
                start_time = time.time()
        
        stream.stop_stream()
        stream.close()
    
    def _save_segment(self, timestamp):
        filename = self.save_dir / f"recording_{int(timestamp)}.wav"
        wf = wave.open(str(filename), 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        return filename 