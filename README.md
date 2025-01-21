# 课堂笔记记录系统

一个基于 AI 的自动课堂笔记记录和总结系统。

## 功能特点

- 🎤 实时录音：自动分段录制课堂音频
- 🤖 语音识别：使用 OpenAI Whisper 进行准确的语音转文字
- 📝 智能总结：使用 GPT 模型生成结构化的课堂笔记
- ⏱️ 实时处理：每个录音片段都会立即处理并生成总结
- 📊 智能分段：基于内容和停顿自动进行内容分段
- 📑 完整记录：保存原始音频、转录文本和总结笔记

## 使用的技术

- **语音识别**: OpenAI Whisper
- **文本总结**: OpenAI GPT-4/3.5
- **音频处理**: PyAudio
- **进度显示**: tqdm
- **开发环境**: Cursor IDE

## 致谢

本项目使用 [Cursor](https://cursor.sh) - The AI-first Code Editor 开发。

特别感谢以下开源项目：
- [OpenAI Whisper](https://github.com/openai/whisper)
- [OpenAI GPT](https://openai.com/gpt-4)
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
- [tqdm](https://github.com/tqdm/tqdm)

## 许可证

MIT License

## 系统要求

- Python 3.8+
- FFmpeg
- OpenAI API密钥（如果使用OpenAI GPT）
- 足够的磁盘空间用于存储录音和笔记

## 安装步骤

1. 克隆仓库：
```bash
git clone [repository_url]
cd ai-lecture-note-taker
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 安装FFmpeg：
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows (使用Chocolatey)
choco install ffmpeg
```

4. 配置：
```bash
# 复制示例配置文件
cp config.json.example config.json

# 设置OpenAI API密钥
export OPENAI_API_KEY='your-api-key'
```

## 配置说明

配置文件 `config.json` 包含以下主要设置：

```json
{
    "whisper": {
        "model_name": "turbo",    # Whisper模型选择
        "device": "cpu",          # 使用CPU或CUDA
        "language": "en"          # 识别语言
    },
    "recording": {
        "save_dir": "lecture_recordings",
        "interval": 300           # 录音分段间隔(秒)
    },
    "llm": {
        "api_type": "openai",     # LLM类型：openai或local
        "model": "gpt-4",         # 使用的模型
        "max_tokens": 250         # 输出长度限制
    }
}
```

## 使用方法

1. 启动程序：
```bash
./run.py
```

2. 程序会自动：
   - 开始录音
   - 每5分钟保存一段录音
   - 使用Whisper转录语音
   - 生成结构化笔记
   - 保存到指定目录

3. 按 `Ctrl+C` 停止记录

## 输出文件结构

```
lecture_notes/
└── 2024-03-21/
    ├── lecture_note_14-30-00.md  # Markdown格式的笔记
    └── lecture_data_14-30-00.json # 原始数据
```

笔记格式包括：
- 课程主题和时间戳
- 结构化的内容概要
- 重要概念和定义
- 作业和重要日期提醒
- 原始转录文本（用于参考）

## 项目结构

```
.
├── run.py                 # 程序入口
├── src/
│   ├── recorder.py       # 录音模块
│   ├── transcriber.py    # Whisper转录模块
│   ├── summarizer.py     # GPT总结模块
│   ├── config.py         # 配置管理
│   └── main.py          # 主程序逻辑
├── config.json           # 配置文件
└── requirements.txt      # 依赖列表
```

## 主要模块说明

- **recorder.py**: 处理实时录音，支持定时分段保存
- **transcriber.py**: 使用Whisper进行本地语音转文字
- **summarizer.py**: 处理笔记生成，支持多种LLM后端
- **config.py**: 管理配置文件和默认设置
- **main.py**: 协调各模块工作，处理主程序流程

## 注意事项

1. 确保麦克风正常工作并已正确配置
2. 需要足够的磁盘空间存储录音文件
3. 首次运行Whisper时会下载模型文件
4. 使用OpenAI API需要确保网络连接正常
5. 建议在使用前测试录音质量

## 开发计划

- [ ] 添加图形用户界面
- [ ] 支持更多本地LLM模型
- [ ] 添加实时转录预览
- [ ] 支持笔记导出为更多格式
- [ ] 添加语音活动检测
- [ ] 优化智能分段算法

## 贡献指南

欢迎提交Issue和Pull Request！

## 联系方式

[您的联系信息] 