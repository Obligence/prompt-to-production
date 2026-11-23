#!/usr/bin/env bash
# One-time setup for a fresh machine or cloud session. Safe to run again.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p .cache/fonts
pip install --break-system-packages -q kokoro-onnx soundfile pillow numpy pygments
command -v ffmpeg >/dev/null || { echo "ffmpeg is required"; exit 1; }
REL=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -s .cache/kokoro-v1.0.onnx ] || curl -sSL -o .cache/kokoro-v1.0.onnx "$REL/kokoro-v1.0.onnx"
[ -s .cache/voices-v1.0.bin ]  || curl -sSL -o .cache/voices-v1.0.bin  "$REL/voices-v1.0.bin"
if [ ! -s .cache/fonts/JetBrainsMono-Regular.ttf ]; then
  curl -sSL -o .cache/jb.zip https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip
  unzip -q -o -j .cache/jb.zip "fonts/ttf/JetBrainsMono-Regular.ttf" "fonts/ttf/JetBrainsMono-Medium.ttf" -d .cache/fonts
  rm -f .cache/jb.zip
fi
ls /usr/share/fonts/opentype/inter/Inter-Bold.otf >/dev/null 2>&1 || echo "WARNING: Inter font not found at /usr/share/fonts/opentype/inter/"
echo "setup ok"
