#!/usr/bin/env bash
# Video → Text Pipeline: FFmpeg → whisper.cpp (AMD Vulkan / NVIDIA CUDA / Intel Vulkan)
#
# Prerequisites:
#   1. Install whisper.cpp:  git clone https://github.com/ggerganov/whisper.cpp && cd whisper.cpp && cmake -B build -DGGML_VULKAN=ON && cmake --build build --config Release
#   2. Download model:        bash models/download-ggml-model.sh large-v3
#   3. FFmpeg installed:      ffmpeg -version
#
# Usage:
#   bash transcribe_whisper_cpp.sh video.mp4
#   bash transcribe_whisper_cpp.sh video.mp4 --model medium --language en --output text
#
# GPU Selection:
#   Default: Vulkan (AMD / Intel / NVIDIA)
#   Set WHISPER_CPP_DIR env var if whisper.cpp is not at ../whisper.cpp

set -euo pipefail

VIDEO="$1"
shift || { echo "Usage: $0 <video.mp4> [--model large-v3] [--language zh] [--output json|text|srt]"; exit 1; }

# ── Config ──────────────────────────────────────────────
MODEL_SIZE="large-v3"
LANGUAGE="zh"
OUTPUT_FORMAT="json"
WHISPER_CPP_DIR="${WHISPER_CPP_DIR:-${HOME}/whisper.cpp}"
KEEP_AUDIO=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --model)   MODEL_SIZE="$2"; shift 2 ;;
        --language) LANGUAGE="$2"; shift 2 ;;
        --output)  OUTPUT_FORMAT="$2"; shift 2 ;;
        --keep-audio) KEEP_AUDIO=true; shift ;;
        --whisper-dir) WHISPER_CPP_DIR="$2"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

# ── Validate ────────────────────────────────────────────
if [[ ! -f "$VIDEO" ]]; then
    echo "ERROR: Video not found: $VIDEO"
    exit 1
fi

WHISPER_BIN="$WHISPER_CPP_DIR/build/bin/whisper-cli"
if [[ ! -f "$WHISPER_BIN" ]]; then
    # Try other common locations
    for candidate in \
        "$WHISPER_CPP_DIR/build/bin/Release/whisper-cli.exe" \
        "$WHISPER_CPP_DIR/build/bin/whisper-cli.exe" \
        "$WHISPER_CPP_DIR/whisper-cli" \
        "$WHISPER_CPP_DIR/main"; do
        if [[ -f "$candidate" ]]; then
            WHISPER_BIN="$candidate"
            break
        fi
    done
fi

if [[ ! -f "$WHISPER_BIN" ]]; then
    echo "ERROR: whisper-cli not found at $WHISPER_BIN"
    echo "Set WHISPER_CPP_DIR to your whisper.cpp directory"
    exit 1
fi

MODEL_PATH="$WHISPER_CPP_DIR/models/ggml-${MODEL_SIZE}.bin"
if [[ ! -f "$MODEL_PATH" ]]; then
    echo "ERROR: Model not found: $MODEL_PATH"
    echo "Download: cd $WHISPER_CPP_DIR && bash models/download-ggml-model.sh $MODEL_SIZE"
    exit 1
fi

# ── Stage 1: Extract Audio ──────────────────────────────
echo "[1/2] Extracting audio from: $VIDEO"
AUDIO_WAV="${VIDEO%.*}_audio.wav"

ffmpeg -y -i "$VIDEO" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$AUDIO_WAV" 2>/dev/null

DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO" 2>/dev/null || echo "?")
echo "   Duration: ${DURATION}s"

# ── Stage 2: Transcribe ─────────────────────────────────
echo "[2/2] Transcribing with whisper.cpp ($MODEL_SIZE, $LANGUAGE)..."

# Build whisper-cli arguments
WHISPER_ARGS=(-m "$MODEL_PATH" -f "$AUDIO_WAV" -l "$LANGUAGE")

case "$OUTPUT_FORMAT" in
    json) WHISPER_ARGS+=(-oj) ;;
    text) WHISPER_ARGS+=(-otxt) ;;
    srt)  WHISPER_ARGS+=(-osrt) ;;
esac

# whisper.cpp outputs to stdout by default
"$WHISPER_BIN" "${WHISPER_ARGS[@]}" 2>/tmp/whisper_cpp_stderr.log
EXIT_CODE=$?

# ── Cleanup ─────────────────────────────────────────────
if [[ "$KEEP_AUDIO" != true ]]; then
    rm -f "$AUDIO_WAV"
fi

if [[ $EXIT_CODE -ne 0 ]]; then
    echo "ERROR: whisper.cpp failed (exit code $EXIT_CODE)"
    cat /tmp/whisper_cpp_stderr.log
    exit $EXIT_CODE
fi

echo ""
echo "Done."
