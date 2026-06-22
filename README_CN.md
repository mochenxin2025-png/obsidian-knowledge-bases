# 🎬 Video → Obsidian · 知识库管道

> 把任何视频自动转化为结构化 Obsidian 笔记。

[![许可证: MIT](https://img.shields.io/badge/许可证-MIT-green.svg)](LICENSE)
[![平台](https://img.shields.io/badge/平台-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)]()
[![English](https://img.shields.io/badge/English-blue)](README_EN.md)

---

## 这是什么？

一个三阶段管道，将任何视频转化为结构丰富的 Obsidian 笔记：

```
📹 视频 ──FFmpeg──▶ 🎵 WAV ──Whisper──▶ 📝 文本 ──LLM──▶ 📓 Obsidian 笔记
```

- **阶段1：** 提取音频（FFmpeg，16kHz 单声道 WAV）
- **阶段2：** GPU 加速语音识别（支持 NVIDIA、AMD、Apple）
- **阶段3：** LLM 提炼标题、标签、章节、关键洞察 → 写入 Obsidian

## ⬇️ 下载安装

### 方式一：Git 克隆

```bash
git clone https://github.com/mochenxin2025-png/obsidian-knowledge-bases.git
cd obsidian-knowledge-bases
```

### 方式二：下载 ZIP

[![下载 ZIP](https://img.shields.io/badge/下载-ZIP-brightgreen?style=for-the-badge)](https://github.com/mochenxin2025-png/obsidian-knowledge-bases/archive/refs/heads/main.zip)

### 方式三：Hermes CLI

```bash
hermes skills install video-to-obsidian
```

## 🖥️ GPU 支持

| 显卡 | 后端 | 速度（4分钟视频） |
|------|------|-------------------|
| 🟢 NVIDIA RTX/GTX | faster-whisper (CUDA) | ~1-2 分钟 |
| 🍎 Apple M1/M2/M3 | faster-whisper (MPS) | ~5-10 分钟 |
| 🔴 AMD RX 6000/7000 | whisper.cpp (Vulkan) | ~5-10 分钟 |
| ⚪ CPU 后备 | faster-whisper (int8) | ~30 分钟 |

## 🚀 快速开始

### NVIDIA / Apple Silicon

```bash
pip install faster-whisper
python scripts/transcribe_faster_whisper.py video.mp4
```

### AMD Radeon

```bash
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp && cmake -B build -DGGML_VULKAN=ON && cmake --build build --config Release
bash models/download-ggml-model.sh large-v3
cd ..
bash scripts/transcribe_whisper_cpp.sh video.mp4
```

### 国内用户 🇨🇳

运行 faster-whisper 前设置 HuggingFace 镜像：

```bash
# Linux / macOS
export HF_ENDPOINT=https://hf-mirror.com

# Windows PowerShell
$env:HF_ENDPOINT="https://hf-mirror.com"
```

## 📂 项目结构

```
obsidian-knowledge-bases/
├── README.md              # 语言选择器
├── README_EN.md           # 英文文档
├── README_CN.md           # 中文文档（本文件）
├── LICENSE                # MIT
├── SKILL.md               # Agent 通用 Skill 定义
├── scripts/
│   ├── transcribe_faster_whisper.py   # NVIDIA CUDA / Apple MPS
│   └── transcribe_whisper_cpp.sh      # AMD Vulkan / NVIDIA / Intel GPU
└── references/
    └── category-mapping.md            # Obsidian 分类映射规则
```

## 🔌 Agent 集成

此 Skill 是 **Agent 通用的**。适配任何具备以下能力的 AI Agent：

1. **Shell 访问** — 运行 FFmpeg 和转录脚本
2. **文件写入** — 将 `.md` 文件写入 Obsidian 知识库
3. **HTTP/浏览器** — 从在线平台下载视频
4. **LLM 推理** — 从转录文本提炼结构化内容

详见 [SKILL.md](SKILL.md) 中的 Hermes Agent、Claude Code、Codex CLI 集成示例。

## 📝 支持平台

| 平台 | 提取方式 |
|------|----------|
| 抖音 | 浏览器自动化 → 视频源URL → 下载 |
| B站 | API / yt-dlp |
| YouTube | yt-dlp |
| 本地文件 | 直接 FFmpeg 处理 |

## 📄 许可证

MIT — 详见 [LICENSE](LICENSE)。
