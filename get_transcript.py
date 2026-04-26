#!/usr/bin/env python3
"""Fetch and save the transcript for a YouTube video."""

import sys
import re
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled


def extract_video_id(url: str) -> str:
    patterns = [
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"youtube\.com/watch\?.*v=([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    # Treat bare 11-char strings as video IDs directly
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url
    raise ValueError(f"Could not extract video ID from: {url}")


def fetch_transcript(video_id: str) -> list[dict]:
    api = YouTubeTranscriptApi()
    try:
        fetched = api.fetch(video_id, languages=["en", "en-US", "en-GB"])
        return list(fetched)
    except NoTranscriptFound:
        # Fall back to any available language
        transcript_list = api.list(video_id)
        transcript = next(iter(transcript_list))
        return list(transcript.fetch())


def format_transcript(entries: list[dict], timestamps: bool = False) -> str:
    lines = []
    for entry in entries:
        text = entry["text"].strip()
        if not text:
            continue
        if timestamps:
            secs = int(entry["start"])
            lines.append(f"[{secs // 60:02d}:{secs % 60:02d}] {text}")
        else:
            lines.append(text)
    return "\n".join(lines)


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://youtu.be/ag589INxdDk"
    video_id = extract_video_id(url)
    print(f"Fetching transcript for video ID: {video_id}")

    entries = fetch_transcript(video_id)
    transcript_text = format_transcript(entries, timestamps=True)

    output_file = f"transcript_{video_id}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcript_text)

    print(f"Transcript saved to: {output_file}")
    print(f"Total lines: {len(entries)}\n")
    print(transcript_text)


if __name__ == "__main__":
    main()
