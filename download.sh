#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SONGS_FILE="$SCRIPT_DIR/songs.txt"
OUTPUT_DIR="$SCRIPT_DIR/output"

echo "🎵 Playlist Downloader Starting..."
echo "────────────────────────────────────"

if ! command -v yt-dlp &>/dev/null; then
  echo "❌ yt-dlp not found. Run: brew install yt-dlp"
  exit 1
fi

if ! command -v ffmpeg &>/dev/null; then
  echo "❌ ffmpeg not found. Run: brew install ffmpeg"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
SUCCESS=0; FAILED=0; FAILED_SONGS=()

while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -z "$line" || "$line" == \#* ]] && continue
  TITLE=$(echo "$line" | sed 's/ - .*//' | xargs)
  ARTIST=$(echo "$line" | sed 's/.*- //' | xargs)
  echo ""
  echo "⬇️  Downloading: $TITLE — $ARTIST"
  SAFE_FILENAME="${ARTIST}_${TITLE}"
  OUTPUT_PATH="$OUTPUT_DIR/${SAFE_FILENAME}.%(ext)s"
  if ls "$OUTPUT_DIR/${SAFE_FILENAME}".mp3 &>/dev/null 2>&1; then
    echo "   ✅ Already exists, skipping."
    ((SUCCESS++))
    continue
  fi
  yt-dlp "ytsearch1:${TITLE} ${ARTIST} official audio" \
    -x --audio-format mp3 --audio-quality 0 \
    --embed-thumbnail --add-metadata \
    -o "$OUTPUT_PATH" --no-playlist \
    --match-filter "duration < 600" \
    --quiet --progress 2>/dev/null
  if ls "$OUTPUT_DIR/${SAFE_FILENAME}".mp3 &>/dev/null 2>&1; then
    echo "   ✅ Done"
    ((SUCCESS++))
  else
    echo "   ⚠️  Failed"
    ((FAILED++))
    FAILED_SONGS+=("$line")
  fi
done < "$SONGS_FILE"

echo ""
echo "🎬 Generating FCPXML..."
python3 "$SCRIPT_DIR/scripts/generate_fcpxml.py" "$OUTPUT_DIR" "$SCRIPT_DIR/playlist.fcpxml"

echo ""
echo "════════════════════════════════════"
echo "  ✅ Downloaded : $SUCCESS songs"
echo "  ⚠️  Failed    : $FAILED songs"
echo "  📁 Output     : $OUTPUT_DIR"
echo "  🎬 FCPXML     : $SCRIPT_DIR/playlist.fcpxml"
echo "════════════════════════════════════"
