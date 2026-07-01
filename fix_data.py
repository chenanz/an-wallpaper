"""修复 an-wallpaper data.js：删除图片不存在的条目，重新编号 id"""
import os
import json
import re

BASE_DIR = r"D:\风\hermes\an-app"
DATA_JS = os.path.join(BASE_DIR, "src", "data.js")
IMAGES_DIR = os.path.join(BASE_DIR, "public", "images")

# 1. 读取图片目录中的所有文件
existing_images = set(os.listdir(IMAGES_DIR))
print(f"图片目录中共有 {len(existing_images)} 个文件")

# 2. 读取 data.js
with open(DATA_JS, "r", encoding="utf-8") as f:
    content = f.read()

# 3. 提取 GAMES 部分和 wallpaperData 之前的内容
# 找到 wallpaperData 数组的起始位置
# 格式: export const wallpaperData = [
wp_start_pattern = r'(export const wallpaperData = \[)'
wp_start_match = re.search(wp_start_pattern, content)
if not wp_start_match:
    print("ERROR: 未找到 wallpaperData 数组定义")
    exit(1)

# 分割：header（GAMES + STYLES 等）和后面的部分
header_end = wp_start_match.end()
before_wp = content[:header_end]  # 包含 "export const wallpaperData = ["

# 找到 wallpaperData 数组的结束位置 "];"
# 从数组开始往后找第一个独立的 "];"
after_start = content[header_end:]
# 找到数组结束的 "];"
bracket_close = after_start.find("\n];")
if bracket_close == -1:
    print("ERROR: 未找到 wallpaperData 数组的结束 ];")
    exit(1)

array_body = after_start[:bracket_close]  # 数组内容（不含 ];）
# footer 是 ]; 之后的所有内容
footer = after_start[bracket_close:]  # 包含 "\n];" 及后续内容

# 4. 解析数组内容为 JSON
# 把 JS 数组体包装成 JSON 数组来解析
json_array_str = "[" + array_body + "]"
# 处理 JS 特有的：尾部逗号、可能有的注释等
# 先尝试直接解析
try:
    wallpaper_data = json.loads(json_array_str)
except json.JSONDecodeError as e:
    print(f"JSON 解析失败: {e}")
    print("尝试清理后重新解析...")
    # 移除尾部逗号（在 ] 或 } 前的逗号）
    json_array_str = re.sub(r',\s*([}\]])', r'\1', json_array_str)
    # 移除单行注释
    json_array_str = re.sub(r'//.*?$', '', json_array_str, flags=re.MULTILINE)
    wallpaper_data = json.loads(json_array_str)

original_count = len(wallpaper_data)
print(f"data.js 中共有 {original_count} 条壁纸记录")

# 5. 过滤：只保留 imageFile 对应文件存在的条目
kept = []
removed = 0
for item in wallpaper_data:
    image_file = item.get("imageFile", "")
    if image_file in existing_images:
        kept.append(item)
    else:
        removed += 1

# 6. 重新编号 id（从1开始）
for i, item in enumerate(kept, start=1):
    item["id"] = i

# 7. 重建 data.js
# 生成 wallpaperData 数组内容
array_lines = []
for item in kept:
    # 用 json.dumps 保证格式，然后缩进
    item_json = json.dumps(item, ensure_ascii=False, indent=2)
    # 缩进2格
    indented = "\n".join("  " + line for line in item_json.split("\n"))
    array_lines.append(indented)

array_content = ",\n".join(array_lines)

# 组合完整文件
new_content = before_wp + "\n" + array_content + footer

# 8. 写回
with open(DATA_JS, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\n===== 修复完成 =====")
print(f"保留了 {len(kept)} 条")
print(f"删除了 {removed} 条")
print(f"data.js 已更新")
