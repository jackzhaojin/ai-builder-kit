#!/usr/bin/env python3
"""Dump a whisper JSON transcript (mlx_whisper / openai-whisper format) as readable timestamped lines.

Usage: python3 transcript_dump.py transcript.json > transcript.md

Each line: [mm:ss.s - mm:ss.s] text. This is the document the cut decisions get made from, so keep it
one segment per line: it makes 'find the sentence where the hosts introduce slide N' a text search.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import fmt_time

data = json.load(open(sys.argv[1]))
print(f"# Transcript ({os.path.basename(sys.argv[1])}, whisper segments with word timestamps)\n")
for seg in data["segments"]:
    print(f"[{fmt_time(seg['start'])} - {fmt_time(seg['end'])}] {seg['text'].strip()}")
