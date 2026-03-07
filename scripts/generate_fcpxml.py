#!/usr/bin/env python3
import sys, subprocess, json
from pathlib import Path

def get_duration_seconds(filepath):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", filepath],
            capture_output=True, text=True)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except:
        return 0.0

def seconds_to_fcp_time(seconds):
    frames = round(seconds * 30)
    return f"{frames}/30s"

def generate_fcpxml(output_dir, fcpxml_path):
    mp3_files = sorted(Path(output_dir).glob("*.mp3"))
    if not mp3_files:
        print("No MP3 files found in output/")
        return
    print(f"   Found {len(mp3_files)} MP3 files")

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<!DOCTYPE fcpxml>')
    lines.append('<fcpxml version="1.9">')
    lines.append('  <resources>')
    lines.append('    <format id="r1" name="FFVideoFormat1080p30" frameDuration="1001/30000s" width="1920" height="1080"/>')

    asset_ids, durations = [], []
    for i, mp3 in enumerate(mp3_files):
        asset_id = f"r{i+2}"
        dur = get_duration_seconds(str(mp3))
        url = f"file://{mp3.resolve()}"
        fcp_dur = seconds_to_fcp_time(dur)
        name = mp3.stem.replace('"', '&quot;').replace('&', '&amp;')
        lines.append(f'    <asset id="{asset_id}" name="{name}" uid="{asset_id}" start="0s" duration="{fcp_dur}" hasAudio="1" audioSources="1" audioChannels="2" audioRate="44100">')
        lines.append(f'      <media-rep kind="original-media" src="{url}"/>')
        lines.append(f'    </asset>')
        asset_ids.append(asset_id)
        durations.append(dur)
        print(f"   + {mp3.stem} ({dur:.1f}s)")

    lines.append('  </resources>')
    lines.append('  <library>')
    lines.append('    <event name="Playlist">')
    lines.append('      <project name="Playlist">')

    total = seconds_to_fcp_time(sum(durations))
    lines.append(f'        <sequence format="r1" duration="{total}" tcStart="0s" tcFormat="NDF" audioLayout="stereo">')
    lines.append('          <spine>')

    offset = 0.0
    for asset_id, dur in zip(asset_ids, durations):
        lines.append(f'            <audio ref="{asset_id}" offset="{seconds_to_fcp_time(offset)}" duration="{seconds_to_fcp_time(dur)}" start="0s" role="music.music"/>')
        offset += dur

    lines.append('          </spine>')
    lines.append('        </sequence>')
    lines.append('      </project>')
    lines.append('    </event>')
    lines.append('  </library>')
    lines.append('</fcpxml>')

    with open(fcpxml_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"   FCPXML saved: {fcpxml_path}")

if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    fcpxml_path = sys.argv[2] if len(sys.argv) > 2 else "playlist.fcpxml"
    generate_fcpxml(output_dir, fcpxml_path)
