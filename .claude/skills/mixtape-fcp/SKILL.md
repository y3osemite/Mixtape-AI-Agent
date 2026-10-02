---
name: mixtape-fcp
description: Build the Final Cut Pro project (playlist.fcpxml) from the MP3s already in output/. Use only when the user asks for the Final Cut Pro / FCP / FCPXML project, the timeline, or to "get it ready for editing". Downloading songs is the separate mixtape skill.
---

# Mixtape → Final Cut Pro project

This step takes the MP3s already in `output/` and writes `playlist.fcpxml`, which Final Cut Pro imports as a timeline. It does not download anything. If songs are missing, use the `mixtape` skill first.

All paths are relative to the repo root (the folder containing `download.sh`).

## 1. Check what will go on the timeline

`scripts/generate_fcpxml.py` puts **every** `*.mp3` directly inside `output/` on the timeline, **in the same order as `songs.txt`**. It matches each line to its `<Artist>_<Title>.mp3` file. MP3s that don't match any line (e.g. renamed or added by hand) go at the end, alphabetically. If the user wants a different order, reorder the lines in `songs.txt` (with their OK) and rebuild.

Before building, list `output/*.mp3` for the user, in that order, and check:
- Are there leftover songs from an older playlist? If so, ask whether to move them into a dated folder (e.g. `output/archive-YYYY-MM-DD/`) first. Files in subfolders are ignored.
- Are any songs from `songs.txt` missing from `output/`? Mention them and offer to download them first.
- Are any MP3s going to land at the end because they don't match a `songs.txt` line? Point them out.
- Do any file names contain `?`, `,`, `:`, `&`, `"` or `#`? These are known to cause Final Cut Pro media-linking problems (README "Known Limitations"). Offer to rename those files to a plain version first, e.g. `Joji_Whats Up.mp3` instead of `Joji_What's Up?.mp3`, and update the matching `songs.txt` line the same way so the order still matches.

If everything looks fine, go ahead without asking.

## 2. Build

```bash
python3 scripts/generate_fcpxml.py output playlist.fcpxml
```

`ffprobe` (part of ffmpeg) must be installed. If it isn't, every song's length comes out as 0 and the timeline is broken. If the script prints a length of `0.0s` for any song, report it and don't tell the user the project is ready.

## 3. Report back

Tell the user:
- how many songs are on the timeline and the total running time,
- the order they'll appear in (the `songs.txt` order, plus any unmatched files at the end),
- how to import: in Final Cut Pro, **File → Import → XML…** and choose `playlist.fcpxml` in the project folder.

Be upfront that this step is still a work in progress: Final Cut Pro may fail to link some files. If the user reports an import error, ask for the exact message and look at `scripts/generate_fcpxml.py` together with them. Don't rewrite the script unprompted.

## Things not to do

- Don't download, delete or re-download songs here; that's the `mixtape` skill.
- Don't commit `playlist.fcpxml` to git; it contains absolute paths from the user's Mac.
