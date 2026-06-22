---
name: video-to-obsidian
description: "Use when the user wants to transcribe a video file into text and convert it into a structured Obsidian note. Covers the full pipeline: audio extraction, speech recognition, content extraction, and note generation."
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  tags: [video, transcription, obsidian, ffmpeg, whisper, note-taking, automation, amd, nvidia]
  platforms: [windows, macos, linux]
  gpu_support: [nvidia-cuda, amd-vulkan, apple-mps, intel-vulkan]
---

# Video → Obsidian Pipeline

Converts any video into a well-structured Obsidian note through a three-stage pipeline:

```
📹 Video ──FFmpeg──▶ 🎵 WAV ──Whisper──▶ 📝 Text ──LLM──▶ 📓 Obsidian Note
```

This skill is **agent-agnostic** — it documents the pipeline, not any specific agent's tools. See [Agent Setup](#agent-setup) for integration with your agent.

## Overview

- **Stage 1 (FFmpeg):** Extract mono 16kHz audio — lossless, fast, zero config.
- **Stage 2 (Speech Recognition):** Two GPU-accelerated options (see below).
- **Stage 3 (LLM):** Extract title, tags, summary, chapters, key points → write Obsidian note.

## When to Use

- User shares a video file (`.mp4`, `.mov`, `.mkv`, `.webm`) and wants it converted to text
- User wants a structured Obsidian note from video content
- Batch processing: multiple videos → multiple notes

**Don't use for:**
- YouTube/Bilibili URLs with existing subtitles — fetch subtitles directly
- Non-speech audio (music, sound effects)

## Prerequisites

### Required Tools (All Platforms)

| Tool | Check | Install |
|------|-------|---------|
| FFmpeg | `ffmpeg -version` | [ffmpeg.org](https://ffmpeg.org) |
| Python 3.10+ | `python --version` | [python.org](https://python.org) |

### GPU Transcription — Choose Your Path

This skill supports **two GPU backends**. Pick based on your hardware:

| GPU | Backend | Script | Install |
|-----|---------|--------|---------|
| 🟢 **NVIDIA** (RTX/GTX) | faster-whisper (CTranslate2 + CUDA) | `scripts/transcribe_faster_whisper.py` | `pip install faster-whisper` |
| 🍎 **Apple Silicon** (M1/M2/M3) | faster-whisper (CTranslate2 + MPS) | `scripts/transcribe_faster_whisper.py` | `pip install faster-whisper` |
| 🔴 **AMD** (RX 6000/7000) | whisper.cpp (Vulkan) | `scripts/transcribe_whisper_cpp.sh` | `git clone` + `make` |
| 🔵 **Intel Arc** | whisper.cpp (Vulkan) | `scripts/transcribe_whisper_cpp.sh` | `git clone` + `make` |

> CPU transcription is possible as a fallback (~30 min for 4 min video), but GPU is strongly recommended.

## Stage 1: Audio Extraction

```bash
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 output.wav
```

| Flag | Meaning |
|------|---------|
| `-vn` | Strip video track |
| `-acodec pcm_s16le` | Uncompressed 16-bit PCM |
| `-ar 16000` | 16kHz (optimal for Whisper) |
| `-ac 1` | Mono |

## Stage 2a: faster-whisper (NVIDIA CUDA / Apple MPS)

For **NVIDIA GPUs** or **Apple Silicon Macs**.

### Install

```bash
pip install faster-whisper
```

If you're in China, set the HuggingFace mirror first:

```bash
export HF_ENDPOINT=https://hf-mirror.com   # Linux/macOS
set HF_ENDPOINT=https://hf-mirror.com      # Windows CMD
$env:HF_ENDPOINT="https://hf-mirror.com"   # Windows PowerShell
```

### Run

```bash
# NVIDIA GPU
python scripts/transcribe_faster_whisper.py video.mp4 --device cuda

# Apple Silicon
python scripts/transcribe_faster_whisper.py video.mp4 --device auto

# Output JSON with segments + timestamps (default)
python scripts/transcribe_faster_whisper.py video.mp4 --output json

# Plain text (pipe to LLM)
python scripts/transcribe_faster_whisper.py video.mp4 --output text
```

**Model selection:**

| Model | Size | Speed (GPU) | Quality | Use Case |
|-------|------|-------------|---------|----------|
| large-v3 | ~3 GB | 2-5x realtime | Best | Chinese, important content |
| medium | ~1.5 GB | 5-10x realtime | Good | Most videos |
| tiny | ~150 MB | 30x+ realtime | Low | Quick tests |

## Stage 2b: whisper.cpp (AMD Vulkan / Intel Arc / NVIDIA)

For **AMD Radeon** or **Intel Arc** GPUs. Also works on NVIDIA and CPU.

### Install

```bash
# Clone and build
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
cmake -B build -DGGML_VULKAN=ON
cmake --build build --config Release

# Download model
bash models/download-ggml-model.sh large-v3
```

### Run

```bash
# AMD / Intel GPU (Vulkan)
./build/bin/whisper-cli -m models/ggml-large-v3.bin -f audio.wav -l zh

# NVIDIA GPU (CUDA, if built with -DGGML_CUDA=ON)
./build/bin/whisper-cli -m models/ggml-large-v3.bin -f audio.wav -l zh -ng

# Output formats
./build/bin/whisper-cli -m models/ggml-large-v3.bin -f audio.wav -l zh -oj   # JSON
./build/bin/whisper-cli -m models/ggml-large-v3.bin -f audio.wav -l zh -otxt # Text
./build/bin/whisper-cli -m models/ggml-large-v3.bin -f audio.wav -l zh -osrt # SRT
```

## Stage 3: Extract → Obsidian Note

Feed the transcript to your LLM agent with this prompt:

```
Extract a structured Obsidian note from this video transcript.

TRANSCRIPT: {full_text}

TASK:
1. Title (max 30 Chinese or 60 English chars)
2. 3-5 tags from: [理财, 认知提升, AI-Agent, 心理学, 穿搭审美, 职场进阶, 自媒体运营, 剪辑教程, 护肤知识]
3. Core summary (2-3 sentences)
4. Chapters with timestamps (format: "## MM:SS — Chapter Title")
5. 2-3 actionable takeaways with callouts

OUTPUT: Valid YAML frontmatter + markdown body
```

### Note Template

```markdown
---
title: {title}
date: {today}
tags: [{tags}]
aliases: []
status: 已整理
source: "[[{platform} @{creator}]]"
---

# {title}

> [!abstract] 核心概述
> {summary}

## 视频信息

| 属性 | 内容 |
|------|------|
| 作者 | {creator} |
| 时长 | {duration} |

## 章节要点

### MM:SS — Chapter Name
- Key point

## 关键洞察

> [!tip] Takeaway

## 参考来源
- {source link}
- 转录工具: {transcription backend used}
```

### Category Mapping

Choose the Obsidian vault subdirectory based on tags (see `references/category-mapping.md`).

### Connecting Notes

After writing, add `[[wikilink]]` connections to related existing notes in the vault.

---

## Agent Setup

This section maps the pipeline stages to specific agent capabilities.

### Stage 1 (Audio Extraction)

Any agent with shell/terminal access can run FFmpeg.

### Stage 2 (Transcription)

Any agent with shell access can run the transcription scripts.

### Stage 3 (Writing to Obsidian)

The agent needs **file write access** to the Obsidian vault directory.

### Video URL Extraction (Bonus: Download from Video Platforms)

For online video URLs (Douyin, Bilibili, etc.), the agent needs **browser automation** or **HTTP client with cookie support** to extract the video source URL and download it.

### Agent-Specific Examples

<details>
<summary>Hermes Agent</summary>

| Stage | Tool |
|-------|------|
| Browser extraction | `browser_navigate` + `browser_console` to get `video.currentSrc` |
| Video download | `execute_code` (Python `urllib` + Referer header) |
| FFmpeg | `terminal` |
| Transcription | `terminal` (run script) |
| Note writing | `write_file` to Obsidian vault |
| Category mapping | `references/category-mapping.md` bundled with skill |

</details>

<details>
<summary>Claude Code</summary>

| Stage | Tool |
|-------|------|
| Browser extraction | `Bash` with `playwright` or `puppeteer` |
| FFmpeg | `Bash` |
| Transcription | `Bash` |
| Note writing | `Write` / `Edit` to Obsidian vault |

</details>

<details>
<summary>Codex CLI</summary>

| Stage | Tool |
|-------|------|
| Browser extraction | `terminal` with curl + cookies |
| FFmpeg | `shell_command` |
| Transcription | `shell_command` |
| Note writing | `file_write` |

</details>

> Add your agent by mapping the same four capabilities: **shell access**, **file write**, **HTTP/browser**, and **LLM reasoning**.

---

## Common Pitfalls

1. **Empty/noisy transcript:** Video has no speech or heavy background music. Verify audio quality first.
2. **Wrong language:** Force with `--language zh` or `-l zh`.
3. **Out of memory on long videos:** Split audio: `ffmpeg -i long.mp4 -f segment -segment_time 1800 chunk_%03d.wav`
4. **HuggingFace blocked (China):** Set `HF_ENDPOINT=https://hf-mirror.com` before running faster-whisper.
5. **AMD Vulkan not found:** Install Vulkan SDK from [vulkan.lunarg.com](https://vulkan.lunarg.com).
6. **Model not downloaded:** First run auto-downloads ~3 GB. Pre-download to `models/` for offline use.

## Verification Checklist

- [ ] `ffmpeg -version` succeeds
- [ ] GPU driver installed (NVIDIA: `nvidia-smi`, AMD: `vulkaninfo`)
- [ ] Transcription backend installed (faster-whisper or whisper.cpp)
- [ ] Model downloaded (`large-v3` recommended for Chinese)
- [ ] Transcript output is non-empty and in expected language
- [ ] Generated note has valid YAML frontmatter
- [ ] Note written to correct Obsidian vault subdirectory
