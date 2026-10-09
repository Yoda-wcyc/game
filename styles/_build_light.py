# -*- coding: utf-8 -*-
"""從 yoda-styles/gallery.html 產生輕量部署版：抽出 base64 圖、壓縮成 WebP、改相對路徑。
用法：python _build_light.py   （新增風格後重跑即可）"""
import base64, io, os, re, sys
from PIL import Image, features

SRC = os.path.expanduser(r"~/.claude/skills/yoda-styles/gallery.html")
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
MAXW = 1200

def main():
    s = io.open(SRC, encoding="utf-8").read()
    os.makedirs(IMG, exist_ok=True)
    for f in os.listdir(IMG):
        os.remove(os.path.join(IMG, f))
    webp_ok = features.check("webp")
    n = [0]; total = [0]

    def fix(m):
        n[0] += 1
        im = Image.open(io.BytesIO(base64.b64decode(m.group(2))))
        if im.width > MAXW:
            im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
        name = "%02d" % n[0]
        if webp_ok:
            name += ".webp"
            im.save(os.path.join(IMG, name), "WEBP", quality=80, method=6)
        else:
            name += ".jpg"
            im.convert("RGB").save(os.path.join(IMG, name), "JPEG", quality=82, optimize=True)
        total[0] += os.path.getsize(os.path.join(IMG, name))
        return 'img/' + name + m.group(3)

    # 例外：「誌頁」範例是含原作者帳號疊字的社群截圖，公開頁不放圖（之後換成自產樣片時刪掉這兩行即可）
    zb = base64.b64encode(open(os.path.join(os.path.dirname(SRC), "image-styles", "previews", "zhiye-editorial-flat.png"), "rb").read()).decode()
    s = s.replace('<img class="pv" src="data:image/png;base64,%s" alt="preview">' % zb, '<div class="pv nopv">尚無公開預覽</div>')
    # src="data:image/...;base64,XXX"
    s = re.sub(r'data:image/([a-z+]+);base64,([A-Za-z0-9+/=\s]+)(["\')])', fix, s)
    s = re.sub(r'<img(?![^>]*loading=)', '<img loading="lazy" decoding="async"', s)
    if 'name="robots"' not in s:
        s = s.replace('<head>', '<head>\n<meta name="robots" content="noindex,nofollow">', 1)
    out = os.path.join(HERE, "index.html")
    io.open(out, "w", encoding="utf-8", newline="").write(s)
    print("images:", n[0], "img_total:", total[0], "index:", os.path.getsize(out))

if __name__ == "__main__":
    main()
