#!/usr/bin/env python3
"""
Video → Text Pipeline: FFmpeg audio extraction → faster-whisper transcription.

GPU-first: NVIDIA CUDA or Apple MPS recommended.
CPU available as fallback with --device cpu.

Usage:
    python transcribe_faster_whisper.py video.mp4
    python transcribe_faster_whisper.py video.mp4 --device cuda --model medium
    python transcribe_faster_whisper.py video.mp4 --device auto --language en --output text
"""

import argparse, json, os, subprocess, sys, tempfile, time


def extract_audio(video_path: str, output_wav: str) -> float:
    """Extract audio from video as 16kHz mono WAV. Returns duration in seconds."""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        output_wav
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        for line in result.stderr.split('\n'):
            if 'Duration' in line:
                dur_str = line.split('Duration:')[1].split(',')[0].strip()
                h, m, s = dur_str.split(':')
                return float(h)*3600 + float(m)*60 + float(s)
        raise RuntimeError(f"FFmpeg failed:\n{result.stderr[-500:]}")
    
    cmd2 = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    r2 = subprocess.run(cmd2, capture_output=True, text=True)
    try:
        return float(r2.stdout.strip())
    except:
        return 0.0


def detect_device(requested: str) -> str:
    """Resolve device: 'auto' detects best available GPU, 'cuda'/'mps'/'cpu' passed through."""
    if requested != "auto":
        return requested
    
    # Try CUDA
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    
    # Try MPS (Apple Silicon)
    try:
        import torch
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"  # Note: faster-whisper uses "auto" for MPS, we handle below
    except ImportError:
        pass
    
    return "cpu"


def transcribe(audio_path: str, model_size: str = "large-v3",
               language: str = "zh", device: str = "auto") -> dict:
    """Transcribe audio with faster-whisper. Returns structured result."""
    from faster_whisper import WhisperModel
    
    resolved = detect_device(device)
    
    # HuggingFace mirror for users in China
    if 'HF_ENDPOINT' not in os.environ:
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    
    if resolved == "cuda":
        compute_type = "float16"
    elif resolved == "mps":
        compute_type = "float16"
        resolved = "auto"  # faster-whisper uses "auto" for MPS
    else:
        compute_type = "int8"
    
    print(f"   Device: {resolved} ({compute_type})", file=sys.stderr)
    
    model = WhisperModel(model_size, device=resolved, compute_type=compute_type)
    
    segments_out = []
    full_text = []
    
    segments, info = model.transcribe(
        audio_path,
        language=language,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=500,
            speech_pad_ms=400
        )
    )
    
    for seg in segments:
        segments_out.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip()
        })
        full_text.append(seg.text.strip())
    
    return {
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "full_text": " ".join(full_text),
        "segments": segments_out,
        "backend": f"faster-whisper ({resolved}/{compute_type})"
    }


def format_srt(result: dict) -> str:
    """Convert result to SRT subtitle format."""
    lines = []
    for i, seg in enumerate(result["segments"], 1):
        start = _fmt_time(seg["start"])
        end = _fmt_time(seg["end"])
        lines.append(f"{i}\n{start} --> {end}\n{seg['text']}\n")
    return "\n".join(lines)


def _fmt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    parser = argparse.ArgumentParser(
        description="Video → Text via FFmpeg + faster-whisper (NVIDIA CUDA / Apple MPS)"
    )
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--device", default="auto",
                        choices=["auto", "cuda", "mps", "cpu"],
                        help="Device: auto (detect), cuda (NVIDIA), mps (Apple), cpu (fallback)")
    parser.add_argument("--model", default="large-v3",
                        help="Whisper model size (large-v3, medium, small, base, tiny)")
    parser.add_argument("--language", default="zh", help="Language code")
    parser.add_argument("--output", default="json",
                        choices=["json", "text", "srt"])
    parser.add_argument("--keep-audio", action="store_true",
                        help="Keep extracted WAV file")
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"ERROR: Video not found: {args.video}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Extracting audio from: {args.video}", file=sys.stderr)
    t0 = time.time()
    
    if args.keep_audio:
        wav_path = os.path.splitext(args.video)[0] + "_audio.wav"
    else:
        fd, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
    
    try:
        duration = extract_audio(args.video, wav_path)
        print(f"   Duration: {duration:.0f}s", file=sys.stderr)
        
        print(f"Transcribing with {args.model} ({args.language})...", file=sys.stderr)
        result = transcribe(wav_path, args.model, args.language, args.device)
        
        elapsed = time.time() - t0
        speed = duration / elapsed if elapsed > 0 else 0
        print(f"Done in {elapsed:.0f}s ({speed:.1f}x realtime)", file=sys.stderr)
        
        if args.output == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.output == "text":
            print(result["full_text"])
        elif args.output == "srt":
            print(format_srt(result))
        
    finally:
        if not args.keep_audio and os.path.exists(wav_path):
            os.unlink(wav_path)


if __name__ == "__main__":
    main()
