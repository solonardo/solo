#!/usr/bin/env bash
# Construit la pub finale : image (Chromium) + bande-son (numpy) -> MP4 H.264/AAC 1080x1920.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out
python3 audio.py out/soundtrack.wav
node render.js video out/video_muette.mp4 "${WORKERS:-4}"
# H.264 deux passes ~9 Mb/s (format réseaux sociaux), son déjà normalisé (-14 LUFS / -2.5 dBTP)
V="-c:v libx264 -preset slow -b:v 9M -maxrate 12M -bufsize 18M -profile:v high -pix_fmt yuv420p -r 30"
ffmpeg -y -loglevel error -i out/video_muette.mp4 $V -pass 1 -an -f null /dev/null
ffmpeg -y -loglevel error -i out/video_muette.mp4 -i out/soundtrack.wav $V -pass 2 \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest out/Beaufort_Lager_Pub_30s_9x16.mp4
ffmpeg -y -loglevel error -ss 25.8 -i out/Beaufort_Lager_Pub_30s_9x16.mp4 -frames:v 1 -q:v 2 out/miniature.jpg
rm -f ffmpeg2pass* out/video_muette.mp4 out/soundtrack.wav
echo "OK -> out/Beaufort_Lager_Pub_30s_9x16.mp4"
