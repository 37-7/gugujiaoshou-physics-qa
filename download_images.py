# -*- coding: utf-8 -*-
"""下载 B站题图(带 Referer) -> 压缩缩放到本地 _imgs/，输出 manifest.json (url -> 本地文件名)"""
import json, os, hashlib, io, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

BASE = r'C:/Users/Jerry/WorkBuddy/2026-08-25-15-05-40'
IMGDIR = os.path.join(BASE, '_imgs')
os.makedirs(IMGDIR, exist_ok=True)

FILES = [
    r'C:/Users/Jerry/Downloads/ep1_archive.json',
    r'C:/Users/Jerry/Downloads/ep2_archive.json',
    r'C:/Users/Jerry/Downloads/ep1773472304999_archive.json',
    r'C:/Users/Jerry/Downloads/ep1774677279463_archive.json',
    r'C:/Users/Jerry/Downloads/ep1775294076729_archive.json',
    r'C:/Users/Jerry/Downloads/ep1775882842744_archive.json',
    r'C:/Users/Jerry/Downloads/ep1776495656356_archive.json',
    r'C:/Users/Jerry/Downloads/ep1777092338561_archive.json',
    r'C:/Users/Jerry/Downloads/ep1777796135094_archive.json',
]

urls = set()
for p in FILES:
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
    for x in d['data']:
        for u in (x.get('images') or []):
            urls.add(u)
urls = sorted(urls)
print(f'待下载图片: {len(urls)}')

from PIL import Image

def fetch(url):
    req = urllib.request.Request(url, headers={
        'Referer': 'https://www.bilibili.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
    })
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            data = r.read()
    except Exception as e:
        return url, None, f'下载失败: {e}'
    if len(data) < 1000:
        return url, None, f'内容过小({len(data)}B)，可能被防盗链'
    key = hashlib.md5(url.encode()).hexdigest()[:12]
    magic = data[:4]
    is_gif = magic[:3] == b'GIF'
    fname = f'img_{key}.gif' if is_gif else f'img_{key}.jpg'
    fpath = os.path.join(IMGDIR, fname)
    if is_gif:
        with open(fpath, 'wb') as f:
            f.write(data)
        return url, fname, None
    # 非 GIF：缩放压缩为 JPEG q85
    try:
        im = Image.open(io.BytesIO(data))
        im = im.convert('RGB')
        w, h = im.size
        if max(w, h) > 1000:
            scale = 1000 / max(w, h)
            im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        im.save(fpath, 'JPEG', quality=85, optimize=True)
        return url, fname, None
    except Exception as e:
        return url, None, f'图片处理失败: {e}'

manifest = {}
fails = []
done = 0
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(fetch, u): u for u in urls}
    for i, fut in enumerate(as_completed(futs), 1):
        url, fname, err = fut.result()
        if fname:
            manifest[url] = fname
            done += 1
        else:
            fails.append((url, err))
        if i % 40 == 0:
            print(f'  进度 {i}/{len(urls)}')

with open(os.path.join(IMGDIR, 'manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=0)

total_kb = sum(os.path.getsize(os.path.join(IMGDIR, v)) for v in manifest.values()) // 1024
print(f'完成: {done}/{len(urls)} | 失败: {len(fails)} | 本地总大小约 {total_kb//1024} MB')
for u, e in fails:
    print('  FAIL', e, u[:80])
