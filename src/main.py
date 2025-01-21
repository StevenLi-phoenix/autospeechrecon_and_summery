import os
from recorder import AudioRecorder
from transcriber import WhisperTranscriber
from summarizer import Summarizer
from config import Config
import time
from pathlib import Path
from tqdm import tqdm

class VoiceSummaryApp:
    def __init__(self, api_key=None, config_path="config.json"):
        self.config = Config(config_path)
        
        # 初始化各个组件
        self.recorder = AudioRecorder(
            save_dir=self.config["recording"]["save_dir"],
            chunk=self.config["recording"]["chunk"],
            channels=self.config["recording"]["channels"],
            rate=self.config["recording"]["rate"],
            interval=self.config["recording"]["interval"]
        )
        
        self.transcriber = WhisperTranscriber(
            model_name=self.config["whisper"]["model_name"],
            device=self.config["whisper"]["device"],
            language=self.config["whisper"]["language"]
        )
        
        self.summarizer = Summarizer(api_key, self.config)
        self.save_dir = Path(self.config["recording"]["save_dir"])
        
    def start(self):
        print(f"使用Whisper模型: {self.config['whisper']['model_name']}")
        print(f"使用LLM类型: {self.config['llm']['api_type']} - {self.config['llm']['model']}")
        print(f"笔记保存位置: {self.config['output']['summary_dir']}")
        print("\n=== 课堂笔记记录系统已启动 ===")
        print("提示：按 Ctrl+C 停止记录")
        print("\n正在记录中...")
        
        self.recorder.start_recording()
        interval = self.config["recording"]["interval"]
        
        try:
            while True:
                # 使用tqdm显示录音间隔的进度条
                for _ in tqdm(range(interval), 
                            desc="录音进行中", 
                            bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [剩余 {remaining}]',
                            ncols=80):
                    time.sleep(1)
                
                # 获取最新的录音文件
                audio_files = sorted(self.save_dir.glob("*.wav"))
                if not audio_files:
                    continue
                    
                latest_file = audio_files[-1]
                
                # 转录
                print(f"\n处理文件: {latest_file.name}")
                segments = self.transcriber.transcribe_with_timestamps(latest_file)
                
                # 智能分段
                segment_groups = self.summarizer.smart_cut(segments)
                
                # 对每个分段进行总结
                for i, segment_group in enumerate(segment_groups):
                    text = " ".join([seg["text"] for seg in segment_group])
                    summary = self.summarizer.summarize(text)
                    
                    print(f"\n时间段 {i+1} 总结:")
                    print(summary)
                    print("-" * 50)
                
        except KeyboardInterrupt:
            print("\n停止录音和总结...")
            self.recorder.stop_recording()
            
            # 处理最后一段录音
            audio_files = sorted(self.save_dir.glob("*.wav"))
            if audio_files:
                latest_file = audio_files[-1]
                print(f"\n处理最后一段录音: {latest_file.name}")
                segments = self.transcriber.transcribe_with_timestamps(latest_file)
                segment_groups = self.summarizer.smart_cut(segments)
                
                for i, segment_group in enumerate(segment_groups):
                    text = " ".join([seg["text"] for seg in segment_group])
                    summary = self.summarizer.summarize(text)
                    print(f"\n最后时间段 {i+1} 总结:")
                    print(summary)
                    print("-" * 50)
            
            # 生成整体总结
            print("\n生成课程整体总结...")
            final_summary = self.summarizer.summarize_all()
            print("\n=== 课程整体总结 ===")
            print(final_summary)
            print("\n=== 记录完成 ===")

def main():
    config_path = os.getenv("CONFIG_PATH", "config.json")
    config = Config(config_path)
    
    # 优先使用配置文件中的 API Key，如果没有则尝试使用环境变量
    api_key = config.config["llm"]["api_key"] or os.getenv("OPENAI_API_KEY")
    
    if not api_key and config.config["llm"]["api_type"] == "openai":
        raise ValueError("需要在配置文件或环境变量中设置 OpenAI API Key")
    
    app = VoiceSummaryApp(api_key, config_path)
    app.start()

if __name__ == "__main__":
    main() 