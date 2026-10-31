#!/usr/bin/env bash
# Construit la pub finale : image (Chromium) + bande-son (numpy) -> MP4 H.264/AAC 1080x1920.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out
python3 audio.py out/soundtrack.wav
node render.js video out/video_muette.mp4 "${WORKERS:-4}"
ffmpeg -y -loglevel error -i out/video_muette.mp4 -i out/soundtrack.wav \
  -c:v libx264 -preset slow -crf 17 -profile:v high -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 256k -ar 48000 -af "loudnorm=I=-14:TP=-1:LRA=9" \
  -movflags +faststart -shortest out/Beaufort_Lager_Pub_30s_9x16.mp4
ffmpeg -y -loglevel error -ss 25.8 -i out/Beaufort_Lager_Pub_30s_9x16.mp4 -frames:v 1 out/miniature.jpg
rm -f out/video_muette.mp4 out/soundtrack.wav
echo "OK -> out/Beaufort_Lager_Pub_30s_9x16.mp4"
