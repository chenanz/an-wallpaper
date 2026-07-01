#!/usr/bin/env python
"""Quick test: re-running the crawler should skip already downloaded images"""
import re
text = open('D:/风/hermes/an-app/src/data.js', encoding='utf-8').read()
feet_count = len(re.findall(r'"game": "足社"', text))
feet_files = len(re.findall(r'"imageFile": "feet_', text))
import os
imgdir = 'D:/风/hermes/an-app/public/images'
actual_files = len([f for f in os.listdir(imgdir) if f.startswith('feet_') and f.endswith('.jpg')])

print(f'data.js 足社 entries: {feet_count}')
print(f'data.js feet_ imageFile: {feet_files}')
print(f'Actual feet_*.jpg files: {actual_files}')
print(f'Match: {feet_count == feet_files == actual_files}')
