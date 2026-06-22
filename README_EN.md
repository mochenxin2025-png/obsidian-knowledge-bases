# 🎬 Video → Obsidian · Knowledge Base Pipeline

> Turn any video into a structured Obsidian note — automatically.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)]()
[![中文](https://img.shields.io/badge/中文-简体-red)](README_CN.md)

---

## What Is This?

A three-stage pipeline that converts any video into a rich, structured Obsidian note:

```
📹 Video ──FFmpeg──▶ 🎵 WAV ──Whisper──▶ 📝 Text ──LLM──▶ 📓 Obsidian Note
```

- **Stage 1:** Extract audio (FFmpeg, 16kHz mono WAV)
- **Stage 2:** GPU-accelerated speech recognition (NVIDIA, AMD, or Apple)
- **Stage 3:** LLM extracts titles, tags, chapters, and key insights → writes to Obsidian

## ⬇️ Download & Install

### Option 1: Clone via Git

```bash
git clone https://github.com/mochenxin2025-png/obsidian-knowledge-bases.git
cd obsidian-knowledge-bases
```

### Option 2: Download ZIP

[![Download ZIP](https://img.shields.io/badge/Download-ZIP-brightgreen?style=for-the-badge)](https://github.com/mochenxin2025-png/obsidian-knowledge-bases/archive/refs/heads/main.zip)

### Option 3: Hermes CLI

```bash
hermes skills install video-to-obsidian
```

## 🖥️ GPU Support

| GPU | Backend | Speed (4 min video) |
|-----|---------|---------------------|
| 🟢 NVIDIA RTX/GTX | faster-whisper (CUDA) | ~1-2 min |
| 🍎 Apple M1/M2/M3 | faster-whisper (MPS) | ~5-10 min |
| 🔴 AMD RX 6000/7000 | whisper.cpp (Vulkan) | ~5-10 min |
| ⚪ CPU Fallback | faster-whisper (int8) | ~30 min |

## 🚀 Quick Start

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

### For users in China 🇨🇳

Set HuggingFace mirror before running faster-whisper:

```bash
# Linux / macOS
export HF_ENDPOINT=https://hf-mirror.com

# Windows PowerShell
$env:HF_ENDPOINT="https://hf-mirror.com"
```

## 📂 Project Structure

```
obsidian-knowledge-bases/
├── README.md              # Language selector
├── README_EN.md           # English docs (this file)
├── README_CN.md           # Chinese docs
├── LICENSE                # MIT
├── SKILL.md               # Agent-agnostic skill definition
├── scripts/
│   ├── transcribe_faster_whisper.py   # NVIDIA CUDA / Apple MPS
│   └── transcribe_whisper_cpp.sh      # AMD Vulkan / NVIDIA / Intel GPU
└── references/
    └── category-mapping.md            # Obsidian category rules
```

## 🔌 Agent Integration

This skill is **agent-agnostic**. It works with any AI agent that has:

1. **Shell access** — to run FFmpeg and transcription scripts
2. **File write access** — to write `.md` files to your Obsidian vault
3. **HTTP/browser capability** — to download videos from online platforms
4. **LLM reasoning** — to extract structured content from transcripts

See [SKILL.md](SKILL.md) for integration examples with Hermes Agent, Claude Code, and Codex CLI.

## 📝 Supported Platforms

| Platform | Extraction Method |
|----------|-------------------|
| Douyin (抖音) | Browser automation → video source URL → download |
| Bilibili (B站) | API / yt-dlp |
| YouTube | yt-dlp |
| Local files | Direct FFmpeg access |

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
