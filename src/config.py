from pathlib import Path
import json
import os

class Config:
    DEFAULT_CONFIG = {
        "whisper": {
            "model_name": "turbo",
            "device": "cpu",  # 或 "cuda" 如果有GPU
            "language": "zh"  # 默认中文
        },
        "recording": {
            "save_dir": "recordings",
            "chunk": 1024,
            "channels": 1,
            "rate": 16000,
            "interval": 60  # 录音间隔(秒)
        },
        "llm": {
            "api_type": "openai",  # 可选: openai, local
            "api_base": "https://api.openai.com/v1",  # 如果使用本地服务器，修改为相应地址
            "api_key": os.getenv("OPENAI_API_KEY", ""),  # 从环境变量获取 API Key
            "model": "gpt-4",
            "max_tokens": 150,
            "temperature": 0.7
        },
        "output": {
            "save_summary": True,
            "summary_dir": "summaries"
        }
    }

    def __init__(self, config_path="config.json"):
        self.config_path = Path(config_path)
        self.load_config()

    def load_config(self):
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                self.config = self._merge_configs(self.DEFAULT_CONFIG, user_config)
        else:
            self.config = self.DEFAULT_CONFIG
            self.save_config()

    def save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def _merge_configs(self, default, user):
        merged = default.copy()
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged

    def __getitem__(self, key):
        return self.config[key] 