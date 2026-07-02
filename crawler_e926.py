#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crawler_e926.py
- 从 e926.net 抓取图片
- 过滤 male 标签，优先保留 female 角色
- 增量更新，支持缓存
- 国内可直连（需要 User-Agent）
"""

import os
import sys
import json
import hashlib
import time
import re
import requests
from pathlib import Path
from urllib.parse import urlparse

# === 配置 ===
E926_API = "https://e926.net/posts.json"
HEADERS = {
    "User-Agent": "an-wallpaper-crawler/1.0 (chenanz)",
    "Accept": "application/json",
}

# 脚本所在目录
SCRIPT_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = SCRIPT_DIR / "data_e926"
PAGES_DIR = OUTPUT_DIR / "pages"
OUTPUT_FILE = OUTPUT_DIR / "posts_e926.json"
LAST_ID_FILE = OUTPUT_DIR / ".last_id"

# male 标签黑名单
MALE_TAGS = {
    "male", "1boy", "2boys", "3boys", "4boys", "males", "boy", "boys", "shota",
    "trap", "femboy", "otoko", "man", "men",
}

# female 标签白名单
FEMALE_TAGS = {
    "1girl", "2girls", "3girls", "4girls", "solo_female", "females", "girl", "girls",
    "female", "woman", "women", "kemonomimi", "catgirl", "foxgirl",
}

# 最小需要 female 标签数量
MIN_FEMALE_TAG = 1


def log(msg):
    print(f"[E926] {msg}")


def load_last_id():
    if LAST_ID_FILE.exists():
        try:
            return int(LAST_ID_FILE.read_text().strip())
        except Exception:
            pass
    return 0


def save_last_id(last_id):
    LAST_ID_FILE.write_text(str(last_id), encoding="utf-8")


def get_page_cache(page_num):
    cache_path = PAGES_DIR / f"page_{page_num}.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def save_page_cache(page_num, data):
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = PAGES_DIR / f"page_{page_num}.json"
    cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def has_male_tags(tags_str):
    if not tags_str:
        return False
    tags = set(t.lower().strip() for t in tags_str.split())
    return bool(tags & MALE_TAGS)


def has_female_tags(tags_str):
    if not tags_str:
        return False
    tags = set(t.lower().strip() for t in tags_str.split())
    return bool(tags & FEMALE_TAGS)


def fetch_posts(page_num, retries=3):
    params = {
        "tags": "girls_und_panzer",
        "limit": 100,
        "page": page_num + 1,  # e926 pages are 1-indexed
    }

    for attempt in range(retries):
        try:
            resp = requests.get(
                E926_API,
                params=params,
                headers=HEADERS,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            posts = data.get("posts", [])
            if not posts:
                log(f"Page {page_num}: no posts")
                return []
            return posts
        except requests.RequestException as e:
            log(f"Page {page_num} attempt {attempt + 1}/{retries} error: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise


def process_post(post):
    post_id = post.get("id")
    file_url = post.get("file", {}).get("url")
    preview_url = post.get("preview", {}).get("url")
    tags_all = post.get("tags", {})
    general_tags = tags_all.get("general", []) if isinstance(tags_all, dict) else []
    tags_str = " ".join(general_tags)

    # 过滤 male 标签
    if has_male_tags(tags_str):
        return None

    # 优先 female 标签
    if not has_female_tags(tags_str):
        return None

    return {
        "id": post_id,
        "file_url": file_url,
        "preview_url": preview_url,
        "tags": tags_str,
        "rating": post.get("rating", "general"),
        "score": post.get("score", 0),
        "source": "e926",
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    last_id = load_last_id()
    log(f"Last fetched post ID: {last_id}")

    all_posts = []
    page_num = 0
    max_id = last_id

    while True:
        posts = fetch_posts(page_num)
        if not posts:
            break

        for post in posts:
            post_id = post.get("id")
            if post_id and (last_id == 0 or post_id > last_id):
                processed = process_post(post)
                if processed:
                    all_posts.append(processed)
                    if post_id > max_id:
                        max_id = post_id

        log(f"Page {page_num}: fetched {len(posts)} posts, total kept: {len(all_posts)}")

        # Save incremental results
        if all_posts:
            existing = []
            if OUTPUT_FILE.exists():
                try:
                    existing = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
                except Exception:
                    pass
            existing.extend(all_posts)
            OUTPUT_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
            log(f"Saved {len(existing)} posts to {OUTPUT_FILE}")
            all_posts = []

        if len(posts) < 100:
            log("Last page reached")
            break

        page_num += 1
        time.sleep(1)

    if max_id > last_id:
        save_last_id(max_id)
        log(f"Updated last_id to {max_id}")

    log("Done")


if __name__ == "__main__":
    main()
