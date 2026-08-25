# -*- coding: utf-8 -*-
"""下载全部头像(带Referer) -> 压缩到96px -> _imgs/face_*.jpg, 输出 face_manifest.json"""
import json, os, hashlib, io, glob
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

BASE = r'C:/Users/Jerry/WorkBuddy/2026-08-25-15-05-40'
IMGDIR = os.path.join(BASE, '_imgs')

FILES = [p for p in glob.glob(r'C:/Users/Jerry/Downloads/ep*_archive.json') if '(1)' not in p]
faces = set()
for p in FILES:
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
    for x in d['data']:
        if x.get('face'):
            faces.add(x['face'])
faces = sorted(faces)
print(f'待下载头像: {len(faces)}')

from PIL import Image

def fetch(url):
    req = urllib.request.Request(url, headers={
        'Referer': 'https://www.bilibili.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36',
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
    except Exception as e:
        return url, None, str(e)
    if len(data) < 500:
        return url, None, f'内容过小({len(data)}B)'
    try:
        im = Image.open(io.BytesIO(data)).convert('RGB')
        im = im.resize((96, 96), Image.LANCZOS)
        key = hashlib.md5(url.encode()).hexdigest()[:12]
        fname = f'face_{key}.jpg'
        im.save(os.path.join(IMGDIR, fname), 'JPEG', quality=85)
        return url, fname, None
    except Exception as e:
        return url, None, f'处理失败: {e}'

manifest, fails, done = {}, [], 0
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(fetch, u): u for u in faces}
    for fut in as_completed(futs):
        url, fname, err = fut.result()
        if fname:
            manifest[url] = fname
            done += 1
        else:
            fails.append((url, err))

with open(os.path.join(IMGDIR, 'face_manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False)

sz = sum(os.path.getsize(os.path.join(IMGDIR, v)) for v in manifest.values()) // 1024
print(f'完成: {done}/{len(faces)} | 失败: {len(fails)} | 总大小 {sz//1024} MB')
for u, e in fails:
    print(' FAIL', e, u[:70])
