# 🎵 mixtape

> Automating the boring parts of music curation — so I can focus on what actually matters: the music.

---

## Problem Statement

Music is central to my life. Since Q2 2025, I've been running a non-commercial YouTube playlist channel as a passion project — curating songs by theme, adding personal notes and reflections that reflect my taste and the intention behind each playlist.

The curation part? I love it. The technical part? Not so much.

**Here's what making one playlist video actually looked like:**

| Step | Task | Time |
|------|------|------|
| 1 | Manually search each song on YouTube | ~5 min/song |
| 2 | Extract MP3 using a converter site | ~3 min/song |
| 3 | Verify the file was correctly extracted | ~2 min/song |
| 4 | Open Final Cut Pro, import files | ~10 min |
| 5 | Arrange clips on the timeline | ~15 min |
| 6 | Export and upload to YouTube | ~20 min |

For a **mini playlist (6 songs)**: ~1.5 hours
For a **full playlist (13–20 songs)**: ~3–4 hours — essentially a full day commitment

This is why I could only publish once a month. The bottleneck wasn't the creative work — it was the repetitive, manual technical process surrounding it.

---

## Solution

Automate the extracting and importing steps so I can focus entirely on what I actually enjoy: selecting music, arranging it by theme, and writing the notes behind each playlist.

**Automation Roadmap:**

- [x] **Step 1** — Extract MP3 from YouTube by song title + artist name *(this repo)*
- [ ] **Step 2** — Auto-import into Final Cut Pro timeline *(in progress — FCPXML generation works, FCP import compatibility being resolved)*
- [ ] **Step 3** — Auto-arrange songs in FCP by BPM and theme
- [ ] **Step 4** — Export and upload directly to YouTube

This repo covers **Step 1**, with foundational work for Step 2.

---

## How It Works

```
songs.txt          →       download.sh        →      output/
(song list)           (yt-dlp + ffmpeg)           (MP3 files)
    ↓
generate_fcpxml.py
    ↓
playlist.fcpxml
(Final Cut Pro project)
```

---

## Setup

### Requirements

- macOS
- [Homebrew](https://brew.sh) — package manager for Mac

### Install dependencies (one-time)

```bash
brew install yt-dlp ffmpeg
```

### Clone this repo

```bash
git clone https://github.com/yourusername/playlist-downloader.git
cd playlist-downloader
chmod +x download.sh
```

---

## Usage

**1. Add your songs to `songs.txt`:**

```
# Format: Song Title - Artist Name
Blinding Lights - The Weeknd
Levitating - Dua Lipa
1000 - NCT WISH
```

**2. Run the downloader:**

Double-click `download.sh`
*(or in Terminal: `bash download.sh`)*

---

### ➕ Adding New Songs Later

Already set up? Adding new songs is simple — previously downloaded tracks are automatically skipped.

**Step 1 — Open `songs.txt` in a text editor:**

Example:
cd ~/Desktop/playlist-downloader
cd ~/Downloads/playlist-downloader

```
cd ~/[your-folder-path]/playlist-downloader
open -e songs.txt
```

Add your new songs at the bottom, one per line:

```
New Song Title - Artist Name
```

Save with **Cmd+S**, close with **Cmd+W**.

**Step 2 — Run the downloader again:**

```
bash download.sh
```

Only new songs will be downloaded. Existing files in `output/` are automatically skipped.

---

**3. Find your files:**

```
output/
├── The Weeknd_Blinding Lights.mp3
├── Dua Lipa_Levitating.mp3
└── NCT WISH_1000.mp3
```

**4. Import into Final Cut Pro** *(Step 2 — in progress)*

```
File → Import → XML → playlist.fcpxml
```

---

## File Structure

```
playlist-downloader/
├── SKILL.md                  ← AI agent instructions (Claude)
├── songs.txt                 ← Edit this with your song list
├── download.sh               ← Main runner script
├── scripts/
│   └── generate_fcpxml.py    ← Generates Final Cut Pro project file
├── output/                   ← Downloaded MP3s saved here (gitignored)
└── README.md                 ← This file
```

---

## Architecture Decisions

**Why `yt-dlp` over converter websites?**
Converter sites (like cnvmp3.com) require manual copy-paste per song and can't be automated. `yt-dlp` is a widely-used open-source CLI tool that supports search queries — meaning it can find and download a song given just a title and artist name, no URL needed.

**Why `ytsearch1:` instead of a direct URL?**
The goal is to minimize manual input. By using YouTube's search (`ytsearch1: Title Artist`), the tool picks the top result automatically. This introduces a trade-off (see Known Limitations below), but reduces friction enough to justify it.

**Why FCPXML for Final Cut Pro?**
FCPXML is Apple's official XML interchange format for Final Cut Pro. It allows external tools to define a full timeline — assets, sequence, clip order — that FCP can import directly. This is the intended path for Step 2 automation.

**Why MP3 over other formats?**
MP3 is universally compatible and the most common output from `yt-dlp`. Future versions may switch to AAC (`.m4a`) for better Final Cut Pro compatibility.

---

## Known Limitations

### ⚠️ Wrong song may be downloaded

`yt-dlp` uses `ytsearch1:` which picks the **first YouTube search result** for a given query. This result is not always the intended song — it may return a cover version, a remix, a live recording, or a compilation that happens to rank higher.

**Current workaround:**
After running `download.sh`, manually verify each file in the `output/` folder by listening. If a file is wrong, delete it and re-run with a more specific search query:

```bash
# Add "Official Audio" or "Official MV" for better accuracy
yt-dlp "ytsearch1:Blinding Lights The Weeknd Official Audio" \
  -x --audio-format mp3 --audio-quality 0 \
  -o "output/The Weeknd_Blinding Lights.mp3"
```

Or bypass search entirely with a direct YouTube URL:

```bash
yt-dlp "https://www.youtube.com/watch?v=XXXXXX" \
  -x --audio-format mp3 --audio-quality 0 \
  -o "output/The Weeknd_Blinding Lights.mp3"
```

**Potential future solution:**
Integrate with the YouTube Data API or MusicBrainz to verify the top result against known metadata (ISRC, duration, artist) before downloading. This would significantly reduce wrong-file errors. *Not yet implemented.*

### ⚠️ Final Cut Pro XML import compatibility

FCPXML generation is implemented but FCP import currently encounters media linking issues depending on file naming (special characters like `?`, `,` in song titles) and FCPXML version compatibility. Step 2 is actively being resolved.

### ⚠️ YouTube Terms of Service

This tool uses `yt-dlp` to extract audio from YouTube, which is technically against YouTube's Terms of Service. This project is strictly non-commercial. All copyright ownership is retained by the original artists and rights holders. If any revenue were to be generated from content using these files, it would go entirely to the copyright owners via YouTube's Content ID system.

---

## Copyright & Usage

This project is non-commercial. All music used in playlists remains the property of the respective copyright holders. No revenue is generated from this channel — if Content ID claims are filed, all ad revenue goes directly to the rights holders.

---

## Using with an AI Agent (SKILL.md)

This repo includes a `SKILL.md` file — a structured instruction set that lets AI agents like Claude run this workflow automatically on your behalf.

**What SKILL.md does:**
- Tells the AI agent exactly how to parse `songs.txt`
- Defines the correct `yt-dlp` commands, flags, and search query format
- Specifies file naming conventions and metadata tagging steps
- Guides the agent through FCPXML generation for Final Cut Pro
- Includes error handling logic (what to do if a download fails, file already exists, etc.)

**How to use it with Claude:**

Simply describe what you want in plain language:

> *"Download these songs and prepare them for Final Cut Pro: 1000 - NCT WISH, Sanctuary - Joji, Levitating - Dua Lipa"*

Claude will read `SKILL.md`, execute each step, and report back with a summary of what succeeded and what needs manual review.

**Why this matters:**
Most automation scripts are black boxes. `SKILL.md` makes the logic transparent and editable — you can read it, modify the behavior, or hand it to any AI agent that supports skill/instruction files. It's the difference between a script you run and a workflow you own.

---

## License

MIT
