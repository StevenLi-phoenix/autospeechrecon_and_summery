from openai import OpenAI
import json
from pathlib import Path
import time
from datetime import datetime

class BaseLLM:
    def generate(self, prompt, max_tokens):
        raise NotImplementedError

class OpenAILLM(BaseLLM):
    def __init__(self, api_key, config):
        self.client = OpenAI(
            api_key=api_key,
            base_url=config["llm"]["api_base"]
        )
        self.config = config["llm"]

    def generate(self, prompt, max_tokens=None):
        if max_tokens is None:
            max_tokens = self.config["max_tokens"]

        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": """You are an expert class note taker. Your task is to:
1. Identify and structure key concepts and ideas from the lecture
2. Organize information in a clear, hierarchical format
3. Highlight important definitions, theories, and examples
4. Include any mentioned references or resources
5. Note any assignments or important dates mentioned

Format your notes in markdown with:
- Clear headings for main topics
- Bullet points for key details
- Code blocks for technical content
- *Emphasis* for important terms
- > Blockquotes for direct quotes or important statements"""},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=self.config["temperature"]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"笔记生成失败: {str(e)}"

class LocalLLM(BaseLLM):
    def __init__(self, config):
        # 这里可以初始化本地LLM，比如llama.cpp或其他本地模型
        self.config = config["llm"]
        
    def generate(self, prompt, max_tokens=None):
        # 实现本地LLM的调用
        pass

class Summarizer:
    def __init__(self, api_key, config):
        self.config = config
        if config["llm"]["api_type"] == "openai":
            self.llm = OpenAILLM(api_key, config)
        elif config["llm"]["api_type"] == "local":
            self.llm = LocalLLM(config)
        
        if config["output"]["save_summary"]:
            self.summary_dir = Path(config["output"]["summary_dir"])
            self.summary_dir.mkdir(exist_ok=True)

    def summarize(self, text, max_tokens=None):
        summary = self.llm.generate(text, max_tokens)
        
        if self.config["output"]["save_summary"]:
            self._save_summary(text, summary)
            
        return summary

    def _save_summary(self, text, summary):
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H-%M-%S")
        
        # 创建日期文件夹
        date_dir = self.summary_dir / date_str
        date_dir.mkdir(exist_ok=True)
        
        # 保存markdown格式的笔记
        note_file = date_dir / f"lecture_note_{time_str}.md"
        with open(note_file, 'w', encoding='utf-8') as f:
            f.write(f"# Lecture Notes - {date_str} {time_str}\n\n")
            f.write(summary)
            f.write("\n\n---\n")
            f.write("## Original Transcript\n\n")
            f.write("```\n")
            f.write(text)
            f.write("\n```\n")
        
        # 同时保存JSON格式的原始数据
        data_file = date_dir / f"lecture_data_{time_str}.json"
        data = {
            "timestamp": timestamp.isoformat(),
            "original_text": text,
            "summary": summary
        }
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def smart_cut(self, segments):
        """
        智能分段：基于课堂内容的自然停顿和主题转换
        """
        current_segment = []
        segments_groups = []
        
        for segment in segments:
            current_segment.append(segment)
            
            # 调整分段策略：
            # 1. 如果超过5分钟
            # 2. 遇到较长停顿（可能是主题转换）
            # 3. 检测到可能的主题转换标记词（如 "next", "moving on", "let's talk about"）
            if (segment["end"] - segment["start"] >= 300 or  # 5分钟
                (len(current_segment) > 1 and 
                 current_segment[-1]["start"] - current_segment[-2]["end"] > 2.0) or  # 2秒停顿
                any(marker in segment["text"].lower() 
                    for marker in ["next", "moving on", "now let's", "let's talk about"])):
                
                segments_groups.append(current_segment)
                current_segment = []
        
        if current_segment:
            segments_groups.append(current_segment)
            
        return segments_groups

    def summarize_all(self, date_str=None):
        """
        总结指定日期或当天的所有笔记，并合并录音文件
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            
        date_dir = self.summary_dir / date_str
        if not date_dir.exists():
            return "没有找到今天的笔记"
            
        # 收集所有的JSON数据文件
        data_files = sorted(date_dir.glob("lecture_data_*.json"))
        if not data_files:
            return "没有找到任何笔记数据"
            
        # 收集所有文本
        all_texts = []
        for data_file in data_files:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_texts.append(data["original_text"])
                
        # 合并所有文本并生成总结
        combined_text = "\n\n---\n\n".join(all_texts)
        final_summary = self.llm.generate(
            f"这是一整节课的内容，请总结主要内容，并突出重点和关键概念：\n\n{combined_text}",
            max_tokens=1000  # 为整体总结提供更多token
        )
        
        # 保存总结
        time_str = datetime.now().strftime('%H-%M-%S')
        summary_file = date_dir / f"lecture_summary_{time_str}.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# 课程总结 - {date_str}\n\n")
            f.write(final_summary)
            
        # 合并录音文件
        recordings_dir = Path(self.config["recording"]["save_dir"])
        audio_files = sorted(recordings_dir.glob("*.wav"))
        if audio_files:
            import wave
            import os
            
            # 创建合并后的音频文件
            merged_file = date_dir / f"lecture_recording_{time_str}.wav"
            
            # 获取第一个文件的参数
            with wave.open(str(audio_files[0]), 'rb') as first_file:
                params = first_file.getparams()
            
            # 创建合并后的文件
            with wave.open(str(merged_file), 'wb') as output:
                output.setparams(params)
                
                # 合并所有音频文件
                for audio_file in audio_files:
                    with wave.open(str(audio_file), 'rb') as w:
                        output.writeframes(w.readframes(w.getnframes()))
            
            print(f"\n已合并所有录音到: {merged_file}")
            
            # 清理原始录音文件
            for audio_file in audio_files:
                os.remove(audio_file)
            
        return final_summary