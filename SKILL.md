---
name: video-to-obsidian
description: "Use when the user wants to transcribe a video file into text and convert it into a structured Obsidian note. Covers the full pipeline: audio extraction, speech recognition, content extraction, and note generation."
version: 2.1.0
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

## Complete Workflow

The pipeline includes **pre-flight checks** and **post-pipeline synthesis** — not just transcription.

### Step 0: Pre-Flight Check (Run Once Per Session)

Before starting ANY video processing, verify the Obsidian environment:

```
0a. Check Obsidian installation
    → Try: ls "$OBSIDIAN_VAULT_PATH" or check common paths
    → If NOT installed:
      → Ask user: "Obsidian not detected. Install from https://obsidian.md/?"
      → If yes: help install (OS-specific instructions)
      → Save answer to agent memory (do NOT ask again)

0b. Check obsidian-skills plugin
    → Check: <vault>/.obsidian/plugins/obsidian-skills/
    → If missing:
      → Install from: https://github.com/kepano/obsidian-skills
      → Clone into vault's .obsidian/plugins/ directory
      → No need to ask user — install silently
```

**Memory keys used:**
- `obsidian_install_asked` → set to `true` after first ask
- Only ask the user ONCE ever about installing Obsidian

### Step 1: Resolve Vault Path (Run Every Pipeline)

Before writing any note, resolve where to save:

```
1a. Check agent memory for saved vault path
    → Key: "obsidian_vault_path"
    → If found and path exists → use it

1b. If no saved path OR path doesn't exist:
    → Ask user: "您的Obsidian知识库保存在哪个目录？"
    → Save answer to memory: obsidian_vault_path = <user's answer>
    → Use this path for all future runs unless user changes it
```

### Step 2-5: Core Pipeline (Per Video)

```
Step 2: Download video (if URL) → Stage 1: FFmpeg audio extraction
Step 3: Stage 2: GPU transcription (faster-whisper or whisper.cpp)
Step 4: Stage 3: LLM extraction → write Obsidian note
Step 5: Post-pipeline cleanup
```

### Step 5: Post-Pipeline Cleanup

After the note is written:

```
5a. If video was DOWNLOADED (not a local file):
    → Ask user: "转录完成。是否删除下载的视频文件？[保留/删除]"
    → If delete: remove the .mp4 file from temp directory

5b. Always delete the temporary WAV audio file (was extracted from video)

5c. Increment pipeline completion counter in memory:
    → Key: "pipeline_run_count"
    → If counter >= 2: trigger Step 6
```

### Step 6: Cross-Note Synthesis (Conditional)

When `pipeline_run_count >= 2` for the **same category** (e.g., 护肤知识, 理财认知):

```
6a. Ask user:
    "您已在「{category}」分类下积累了 {count} 篇笔记。
     是否需要我分析这些笔记的核心观点，创建一篇「观点串联」笔记？
     内容包括：观点一致/不同/冲突的标注，以及 Obsidian 链接。"

6b. If user says YES:
    1. Read ALL notes in the target category
    2. Extract core viewpoints from each note
    3. Create a synthesis note with this structure:

       ---
       title: "{category}·观点串联——{date}"
       tags: [观点串联, {category_tags}]
       ---

       # {category} · 观点串联

       ## 涉及笔记
       | # | 笔记 | 创作者 | 核心观点 |
       |---|------|--------|----------|
       | 1 | [[笔记1]] | @作者1 | 观点摘要 |
       | 2 | [[笔记2]] | @作者2 | 观点摘要 |

       ## 观点一致 ✅
       - 笔记A 和 笔记B 在「某某观点」上一致
       - ...

       ## 观点不同 🔀
       - 笔记A 认为 X，笔记B 认为 Y
       - ...

       ## 观点冲突 ⚡
       - 笔记C 主张 X，笔记D 明确反对 X
       - ...

       ## 知识缺口 🕳️
       - 该主题尚未覆盖的角度：...

    4. Add [[wikilink]] from the synthesis note to EVERY source note
    5. Add [[wikilink]] from each source note BACK to the synthesis note
    6. Reset counter for that category

6c. If user says NO:
    → Skip, keep counter for next time
```

---

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
7. **Vault path not set:** If agent can't find vault, ask user explicitly. Save to memory.
8. **obsidian-skills missing:** Install silently from GitHub — no need to ask user.
9. **Synthesis noise:** Only synthesize when category has ≥2 notes with meaningful compare/contrast potential.

## Verification Checklist

- [ ] **Step 0:** Obsidian installed (or user confirmed skip)
- [ ] **Step 0:** obsidian-skills plugin present in vault
- [ ] **Step 1:** Vault path saved to agent memory
- [ ] `ffmpeg -version` succeeds
- [ ] GPU driver installed (NVIDIA: `nvidia-smi`, AMD: `vulkaninfo`)
- [ ] Transcription backend installed (faster-whisper or whisper.cpp)
- [ ] Model downloaded (`large-v3` recommended for Chinese)
- [ ] Transcript output is non-empty and in expected language
- [ ] Generated note has valid YAML frontmatter
- [ ] Note written to correct Obsidian vault subdirectory
- [ ] **Step 5:** Temp WAV deleted; video cleanup offered
- [ ] **Step 6:** (if count ≥ 2) Synthesis offered and completed or skipped
