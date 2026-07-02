#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crawler_safebooru.py
- 从 safebooru.org 抓取 girls_und_panzer 标签图片
- 过滤 male 标签，优先保留 female 角色
- 增量更新，支持缓存
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
BASE_DIR = Path(r"D:\风\hermes\an-app")
PAGES_DIR = BASE_DIR / "pages" / "safebooru"
OUTPUT_FILE = BASE_DIR / "data_r18_safebooru.json"
LAST_ID_FILE = BASE_DIR / ".last_id_safebooru"

# API
SAFEBOORU_API = "https://safebooru.org/index.php"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0"

# 请求头
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://safebooru.org/",
}

# 标签过滤
MALE_TAGS = {
    "1boy", "2boys", "3boys", "4boys", "5boys", "6+boys",
    "male", "males", "boys", "boy", "shota", "trap",
    "male_focus", "male_only", "yaoi", "bara",
    "man", "men", "guy", "guys",
}

FEMALE_TAGS = {
    "1girl", "2girls", "3girls", "4girls", "5girls", "6+girls",
    "solo_female", "female", "females", "girl", "girls",
    "female_focus", "yuri",
}

# 最小需要 female 标签数量（用于优先 female）
MIN_FEMALE_TAG = 1


def log(msg):
    print(f"[Safebooru] {msg}")


def load_last_id():
    """读取上次抓取的最大 post id"""
    if LAST_ID_FILE.exists():
        try:
            return int(LAST_ID_FILE.read_text().strip())
        except Exception:
            pass
    return 0


def save_last_id(last_id):
    """保存最大 post id"""
    LAST_ID_FILE.write_text(str(last_id), encoding="utf-8")


def get_page_cache(page_num):
    """读取页面缓存"""
    cache_path = PAGES_DIR / f"page_{page_num}.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def save_page_cache(page_num, data):
    """保存页面缓存"""
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = PAGES_DIR / f"page_{page_num}.json"
    cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def has_male_tags(tags_str):
    """检查是否包含 male 相关标签"""
    if not tags_str:
        return False
    tags = set(t.lower().strip() for t in tags_str.split())
    return bool(tags & MALE_TAGS)


def has_female_tags(tags_str):
    """检查是否包含 female 相关标签"""
    if not tags_str:
        return False
    tags = set(t.lower().strip() for t in tags_str.split())
    return bool(tags & FEMALE_TAGS)


def fetch_posts(page_num, retries=3):
    """从 Safebooru API 获取帖子"""
    params = {
        "page": "dapi",
        "s": "post",
        "q": "index",
        "json": "1",
        "tags": "girls_und_panzer",
        "limit": 100,
        "pid": page_num,
    }
    
    for attempt in range(retries):
        try:
            resp = requests.get(
                SAFEBOORU_API,
                params=params,
                headers=HEADERS,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data
        except requests.exceptions.RequestException as e:
            log(f"请求失败 (尝试 {attempt + 1}/{retries}): {e}")
            time.sleep(2 ** attempt)
        except json.JSONDecodeError as e:
            log(f"JSON 解析失败: {e}")
            break
    return None


def post_to_record(post):
    """将 API post 转为标准记录格式"""
    return {
        "id": post.get("id"),
        "file_url": post.get("file_url") or post.get("sample_url") or f"https://safebooru.org/images/{post.get('directory', '')}/{post.get('image', '')}",
        "preview_url": post.get("preview_url") or post.get("sample_url"),
        "tags": post.get("tags", ""),
        "score": post.get("score", 0),
        "rating": post.get("rating", "s"),
    }


def load_existing_data():
    """加载已有的输出数据"""
    if OUTPUT_FILE.exists():
        try:
            data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
            return data.get("posts", []), {p["id"] for p in data.get("posts", [])}
        except Exception as e:
            log(f"读取已有数据失败: {e}")
    return [], set()


def main():
    log("开始抓取 Safebooru girls_und_panzer ...")
    
    # 加载已有数据
    existing_posts, existing_ids = load_existing_data()
    log(f"已有数据: {len(existing_posts)} 条")
    
    # 加载上次最大 id
    last_id = load_last_id()
    log(f"上次最大 id: {last_id}")
    
    # 用于去重的集合
    seen_ids = existing_ids.copy()
    seen_md5 = set()
    for p in existing_posts:
        if p.get("file_url"):
            seen_md5.add(hashlib.md5(p["file_url"].encode()).hexdigest())
    
    new_posts = []
    page_num = 0
    max_pages = 50  # 最多抓 50 页
    
    while page_num < max_pages:
        log(f"抓取第 {page_num + 1} 页...")
        
        # 尝试读缓存
        data = get_page_cache(page_num)
        if data is None:
            data = fetch_posts(page_num)
            if data is None:
                log(f"第 {page_num + 1} 页获取失败，跳过")
                page_num += 1
                continue
            save_page_cache(page_num, data)
        else:
            log(f"  使用缓存")
        
        # Safebooru 返回的是列表
        if not isinstance(data, list) or len(data) == 0:
            log("没有更多数据了")
            break
        
        page_new = 0
        for post in data:
            post_id = post.get("id")
            tags = post.get("tags", "")
            
            # 去重
            if post_id in seen_ids:
                continue
            
            # 过滤 male 标签
            if has_male_tags(tags):
                continue
            
            # 优先保留 female
            if not has_female_tags(tags):
                continue
            
            record = post_to_record(post)
            
            # MD5 去重
            file_url = record.get("file_url", "")
            if file_url:
                file_md5 = hashlib.md5(file_url.encode()).hexdigest()
                if file_md5 in seen_md5:
                    continue
                seen_md5.add(file_md5)
            
            seen_ids.add(post_id)
            new_posts.append(record)
            page_new += 1
        
        log(f"  本页新增: {page_new} 条")
        
        # 更新 last_id
        if data:
            current_max = max(p.get("id", 0) for p in data)
            if current_max > last_id:
                last_id = current_max
        
        # 如果一页都没有新增，说明可能已经抓完了
        if page_new == 0 and page_num > 0:
            log("本页无新增，结束抓取")
            break
        
        page_num += 1
        time.sleep(1.5)  # 礼貌延时
    
    # 合并数据
    all_posts = existing_posts + new_posts
    
    # 按 id 去重排序
    unique_posts = {}
    for p in all_posts:
        unique_posts[p["id"]] = p
    all_posts = sorted(unique_posts.values(), key=lambda x: x["id"])
    
    # 保存输出
    output = {"posts": all_posts}
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # 保存 last_id
    save_last_id(last_id)
    
    log(f"完成! 新增: {len(new_posts)} 条, 总计: {len(all_posts)} 条")
    log(f"输出: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
