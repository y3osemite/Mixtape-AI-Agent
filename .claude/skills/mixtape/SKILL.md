---
name: mixtape
description: Download songs as MP3s for a playlist video. Use whenever the user gives a list of songs (pasted text, a screenshot, a copied Spotify/Apple Music list, or "Title - Artist" lines) and wants them downloaded, added to the playlist, re-downloaded, or checked. Also use for "run the downloader", "add these songs", "fix the wrong song". Does not build the Final Cut Pro project; that is the separate mixtape-fcp skill.
---

# Mixtape: song list → MP3s

This skill turns a list of songs into MP3 files in `output/`. Building the Final Cut Pro project (`playlist.fcpxml`) is a separate step handled by the `mixtape-fcp` skill. Don't run it as part of downloading; do it only when the user asks. The user curates; you do the mechanical work and report back clearly. The user is not a terminal person, so keep the final report plain and friendly.

All paths below are relative to the repo root (the folder containing `download.sh`).

## 0. Check the environment (once per session)

Run `command -v yt-dlp ffmpeg ffprobe python3`.

- If `yt-dlp` or `ffmpeg` is missing: tell the user to run `brew install yt-dlp ffmpeg` (ffprobe comes with ffmpeg). Don't install Homebrew packages yourself without asking.
- If this is not macOS (e.g. a cloud/Linux container), warn the user: the MP3s will not end up on their laptop, and YouTube often blocks downloads from cloud servers. Suggest using the Claude desktop app with this folder open on their Mac instead, and continue only if they still want to.
- If downloads start failing with "Sign in to confirm you're not a bot" or HTTP 403, suggest `brew upgrade yt-dlp` first — an outdated yt-dlp is the usual cause.

## 1. Turn the user's list into `songs.txt` lines

`songs.txt` format is one song per line: `Song Title - Artist Name`. Lines starting with `#` and blank lines are ignored.

Normalize whatever the user gives you:
- "Artist - Title", "Title by Artist", "Title (Artist)", numbered lists, screenshots → `Title - Artist`. If you can't tell which part is the artist, ask rather than guess.
- `download.sh` splits on the **first** ` - ` for the title and the **last** `- ` for the artist, so the title and artist must not themselves contain ` - `. Drop that part or replace it with a space (e.g. `Song - Remastered 2011` → `Song Remastered 2011`).
- Remove `/` from titles and artists (it breaks file paths). Avoid `?`, `,`, `:`, `"` where you can — they cause Final Cut Pro import problems (see README "Known Limitations").
- Keep feature credits out of the artist field unless needed to find the right track (`Title - Artist`, not `Title - Artist feat. X`).

Then update `songs.txt`:
- **Append** new songs at the bottom. Never delete or reorder the user's existing lines unless they ask — `songs.txt` is their running playlist.
- Skip songs already in the file (compare case-insensitively) and tell the user which ones were already there.
- If the user says this is a **new playlist** / "start fresh", ask whether to clear the old list and whether to move the existing `output/` MP3s into a dated folder (e.g. `output/archive-YYYY-MM-DD/`), so `output/` holds only the new playlist.

Show the user the lines you added before running the download if there was any ambiguity in the conversion.

## 2. Download

Run:

```bash
bash download.sh
```

It downloads each song with `yt-dlp "ytsearch1:<Title> <Artist> official audio"`, saves it as `output/<Artist>_<Title>.mp3`, and skips files that already exist. It prints ✅/⚠️ per song and a summary. Downloads can take a while (roughly 10–30 s per song); use a long timeout (e.g. 10 minutes) for big lists.

Record from the output which songs were downloaded now, which were skipped as already existing, and which failed.

## 3. Check the new files

`ytsearch1` takes the first YouTube result, which is sometimes a live version, cover, sped-up edit, or hour-long compilation. For each **newly downloaded** file, get its length:

```bash
ffprobe -v quiet -show_entries format=duration -of csv=p=0 "output/<Artist>_<Title>.mp3"
```

Flag a file as **"please listen to check"** when:
- it's shorter than ~1:30 or longer than ~7:00, or
- the embedded title (`ffprobe -v quiet -show_entries format_tags=title -of csv=p=0 <file>`) contains words like live, cover, remix, sped up, slowed, karaoke, instrumental, 1 hour, loop, reaction, lyrics video in another language — unless the user's request asked for that version.

You can't hear the audio, so don't claim a file is definitely correct — say it "looks right" based on length and title.

## 4. Fix failures and suspicious files

For a failed or flagged song, retry once with a more specific search. Delete the bad file first if there is one, then:

```bash
yt-dlp "ytsearch1:<Title> <Artist> official MV" \
  -x --audio-format mp3 --audio-quality 0 \
  --embed-thumbnail --add-metadata \
  -o "output/<Artist>_<Title>.%(ext)s" --no-playlist \
  --match-filter "duration < 600"
```

Other useful search variations: `<Title> <Artist> audio`, `<Title> <Artist> topic` (YouTube's auto-generated "Artist - Topic" channel uploads are usually the studio version).

If it still fails or still looks wrong, stop retrying and ask the user for a YouTube link. With a link:

```bash
yt-dlp "<URL>" -x --audio-format mp3 --audio-quality 0 \
  --embed-thumbnail --add-metadata \
  -o "output/<Artist>_<Title>.%(ext)s" --no-playlist
```

The filename must stay exactly `<Artist>_<Title>.mp3` (matching the `songs.txt` line) so `download.sh` recognizes it next time and skips it.

## 5. Report back

End with a short summary like:

```
🎵 Mixtape update
✅ Downloaded (5): Sanctuary – Joji, 1000 – NCT WISH, ...
⏭️ Already had (2): Your Man – Joji, ...
👂 Please listen to check (1): Afterthought – Joji (8:42 — might be a live version)
⚠️ Couldn't find (1): 404 – KiiKii → send me a YouTube link and I'll grab it
📁 Files are in the output/ folder
```

Use song names, not file paths, and don't paste the raw script output. When nothing is left to check or fix, add one line offering to build the Final Cut Pro project next (the `mixtape-fcp` skill). Don't build it unprompted.

## Things not to do

- Don't commit or push MP3s or `output/` to git.
- Don't delete files in `output/` except a file you've confirmed is the wrong song and are replacing.
- Don't edit `download.sh` or `generate_fcpxml.py` as part of a normal download request — if they seem broken, explain the problem and ask first.
