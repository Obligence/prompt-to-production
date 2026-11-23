#!/usr/bin/env python3
"""Prompt to Production lesson builder.

Usage:
  python3 template/build.py lessons/<slug>.py --preview      # key frames only (build/<slug>/preview_*.png), no audio
  python3 template/build.py lessons/<slug>.py                # narration + full 1080p30 video + cover + SRT + chapters

Outputs: videos/<slug>.mp4, covers/<slug>.jpg, captions/<slug>.srt, meta/<slug>_chapters.txt
See PRODUCTION.md for the lesson file format.
"""
import os, sys, re, json, subprocess, importlib.util, argparse
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pygments.lexers import PythonLexer, BashLexer, JsonLexer
from pygments.styles import get_style_by_name

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache")
W, H, FPS, SR = 1920, 1080, 30, 24000
VOICE, SPEED = "am_fenrir", 1.05
CHANNEL, HANDLE = "Prompt to Production", "@prompt-production"
COURSE = "How to Become an AI Application Engineer"

FG = (238, 240, 248); MUTED = (150, 156, 180)
VIOLET = (139, 108, 255); TEAL = (45, 212, 191); AMBER = (255, 166, 77); RED = (255, 99, 99)
PANEL = (22, 25, 40)
COLORS = {"fg": FG, "muted": MUTED, "violet": (196, 182, 255), "teal": TEAL, "amber": AMBER, "red": RED}
CHIP = {"user": (98, 76, 214), "bot": (20, 150, 132), "tool": (190, 110, 40), "system": (70, 78, 110), "data": (40, 110, 190)}
INTER = "/usr/share/fonts/opentype/inter/"
JB = os.path.join(CACHE, "fonts") + "/"
STYLE = get_style_by_name("monokai")
_fc = {}

def F(name, s):
    if (name, s) not in _fc:
        _fc[(name, s)] = ImageFont.truetype((JB if name.startswith("JetBrains") else INTER) + name, s)
    return _fc[(name, s)]

def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def mixc(c, bg, a):
    return tuple(int(bg[i] + (c[i] - bg[i]) * a) for i in range(3))

def hexrgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

# ---------------------------------------------------------------- background and helpers
def make_bg():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32)
    top, bot = np.array([10, 12, 22]), np.array([14, 16, 30])
    base += top + (bot - top) * (y / H)[..., None]
    for cx, cy, r, col, s in [(250, 80, 520, VIOLET, 0.20), (1750, 1020, 560, TEAL, 0.12)]:
        base += np.exp(-(((x - cx) ** 2 + (y - cy) ** 2) / (2 * r * r)))[..., None] * np.array(col) * s
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    for gx in range(40, W, 48):
        for gy in range(40, H, 48):
            d.point((gx, gy), fill=(255, 255, 255, 22))
    return im

BG = None

def paste_alpha(base, layer, pos, alpha=1.0):
    if alpha <= 0: return
    a = layer.getchannel("A")
    if alpha < 1: a = a.point(lambda v: int(v * alpha))
    base.paste(layer.convert("RGB"), (int(pos[0]), int(pos[1])), a)

def gradient_text(text, font, c1, c2):
    l, t, r, b = font.getbbox(text)
    w, h = r - l + 4, b - t + 4
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((-l + 2, -t + 2), text, font=font, fill=255)
    g = np.linspace(0, 1, w)[None, :, None]
    arr = (np.array(c1) * (1 - g) + np.array(c2) * g).repeat(h, 0).astype(np.uint8)
    img = Image.fromarray(arr).convert("RGBA"); img.putalpha(mask)
    return img

def fit_font(name, text, size, maxw):
    while size > 20 and F(name, size).getlength(text) > maxw: size -= 2
    return F(name, size)

def logo_mark(d, x, y, s=1.0):
    """Channel mark: a prompt chevron '>' turning into a rocket-ish arrow, as two rounded bars."""
    d.rounded_rectangle([x, y, x + 44 * s, y + 44 * s], radius=int(12 * s), fill=VIOLET)
    d.line([(x + 12 * s, y + 13 * s), (x + 22 * s, y + 22 * s), (x + 12 * s, y + 31 * s)], fill=(255, 255, 255), width=int(5 * s))
    d.line([(x + 26 * s, y + 31 * s), (x + 34 * s, y + 31 * s)], fill=TEAL, width=int(5 * s))

# ---------------------------------------------------------------- chrome
def chrome(im, L, sc, si, n):
    d = ImageDraw.Draw(im, "RGBA")
    f = F("Inter-SemiBold.otf", 22)
    label = f"MODULE {L['module']}  ·  LESSON {L['number']}  ·  {L['title'].upper()}"
    w = f.getlength(label) + 40
    d.rounded_rectangle([100, 64, 100 + w, 104], radius=20, fill=(139, 108, 255, 34), outline=(139, 108, 255, 120), width=2)
    d.text((120, 84), label, font=f, fill=(196, 182, 255), anchor="lm")
    d.text((W - 100, 84), f"{si:02d} / {n - 1:02d}", font=F("JetBrainsMono-Medium.ttf", 24), fill=MUTED, anchor="rm")
    d.text((100, 128), sc["title"], font=fit_font("InterDisplay-Bold.otf", sc["title"], 64, W - 200), fill=FG)
    # footer brand
    logo_mark(d, 100, H - 58, 0.6)
    d.text((140, H - 45), f"{CHANNEL}  ·  {HANDLE}", font=F("Inter-Medium.otf", 20), fill=(110, 116, 140), anchor="lm")

def progress(im, frac):
    d = ImageDraw.Draw(im)
    d.rectangle([0, H - 8, W, H], fill=(30, 33, 52))
    x1 = int(W * frac)
    if x1 > 1:
        g = Image.linear_gradient("L").rotate(90).resize((x1, 8)).transpose(Image.FLIP_LEFT_RIGHT)
        im.paste(Image.composite(Image.new("RGB", g.size, TEAL), Image.new("RGB", g.size, VIOLET), g), (0, H - 8))

# ---------------------------------------------------------------- code
def tokens_for(code, lang):
    lex = {"bash": BashLexer, "json": JsonLexer}.get(lang, PythonLexer)()
    out, cur = [], []
    for ttype, val in lex.get_tokens(code):
        t = ttype
        while not STYLE.style_for_token(t)["color"] and t.parent is not None: t = t.parent
        c = STYLE.style_for_token(t)["color"]
        col = hexrgb(c) if c else (248, 248, 242)
        for pi, p in enumerate(val.split("\n")):
            if pi > 0: out.append(cur); cur = []
            if p: cur.append((p, col))
    if cur: out.append(cur)
    while out and not out[-1]: out.pop()
    return out

def window(im, left, top, right, bottom, fname, panel=PANEL):
    sh = Image.new("RGBA", (right - left + 80, bottom - top + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([40, 50, right - left + 40, bottom - top + 40], radius=24, fill=(0, 0, 0, 120))
    paste_alpha(im, sh.filter(ImageFilter.GaussianBlur(22)), (left - 40, top - 40))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([left, top, right, bottom], radius=22, fill=panel, outline=(255, 255, 255, 22), width=2)
    d.rounded_rectangle([left, top, right, top + 58], radius=22, fill=(30, 34, 54))
    d.rectangle([left + 2, top + 36, right - 2, top + 58], fill=(30, 34, 54))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([left + 26 + i * 28, top + 22, left + 40 + i * 28, top + 36], fill=c)
    if fname:
        tf = F("Inter-Medium.otf", 22); tw = tf.getlength(fname) + 40
        d.rounded_rectangle([left + 130, top + 12, left + 130 + tw, top + 58], radius=10, fill=panel)
        d.rectangle([left + 130, top + 40, left + 130 + tw, top + 58], fill=panel)
        d.text((left + 150, top + 35), fname, font=tf, fill=(200, 204, 225), anchor="lm")
    return d

def code_scene(im, sc, k, ts):
    lines = tokens_for(sc["code"], sc.get("lang", "python"))
    n = len(lines)
    vis = min(sc["steps"][k][1], n)
    prev = 0 if k == 0 else min(sc["steps"][k - 1][1], n)
    size = 32 if n <= 12 else (28 if n <= 16 else (25 if n <= 19 else 22))
    lh = int(size * (1.55 if n <= 16 else 1.42))
    font = F("JetBrainsMono-Regular.ttf", size)
    top, left, right = 236, 100, W - 100
    bottom = min(top + n * lh + 100, H - 80)
    d = window(im, left, top, right, bottom, sc.get("file", "app.py"))
    y0, cw = top + 82, font.getlength("M")
    rdur = min(1.4, 0.09 * max(vis - prev, 1) + 0.2)
    shown = prev + (vis - prev) * ease(ts / rdur)
    act = [i for i in range(prev, vis) if lines[i]]
    if act:
        a0, a1, ba = act[0], act[-1], ease(ts / 0.5)
        d.rounded_rectangle([left + 14, y0 + a0 * lh - 8, right - 14, y0 + (a1 + 1) * lh - 6], radius=10, fill=(139, 108, 255, int(30 * ba)))
        d.rounded_rectangle([left + 14, y0 + a0 * lh - 8, left + 20, y0 + (a1 + 1) * lh - 6], radius=3, fill=(139, 108, 255, int(230 * ba)))
    for i, toks in enumerate(lines):
        a = max(0.0, min(1.0, shown - i))
        if a <= 0: continue
        y = y0 + i * lh + (1 - a) * 10
        d.text((left + 40, y), f"{i + 1:>2}", font=font, fill=mixc((80, 86, 110), PANEL, a))
        x = left + 40 + cw * 4
        for val, col in toks:
            d.text((x, y), val, font=font, fill=mixc(col, PANEL, a)); x += font.getlength(val)

def terminal_scene(im, sc, k, ts):
    rows = sc["lines"]  # list of [text, color-name]
    n = len(rows)
    vis = min(sc["steps"][k][1], n)
    prev = 0 if k == 0 else min(sc["steps"][k - 1][1], n)
    size = 30 if n <= 14 else 25
    lh = int(size * 1.5)
    font = F("JetBrainsMono-Regular.ttf", size)
    top, left, right = 236, 100, W - 100
    bottom = min(top + n * lh + 110, H - 80)
    bg = (14, 16, 26)
    d = window(im, left, top, right, bottom, sc.get("file", "terminal"), bg)
    shown = prev + (vis - prev) * ease(ts / min(1.6, 0.25 * max(vis - prev, 1) + 0.2))
    for i, (text, cname) in enumerate(rows):
        a = max(0.0, min(1.0, shown - i))
        if a <= 0: continue
        d.text((left + 40, top + 82 + i * lh), text, font=font, fill=mixc(COLORS.get(cname, FG), bg, a))
    if vis >= n or True:
        yy = top + 82 + min(int(shown), n) * lh
        if int(ts * 2) % 2 == 0 and yy < bottom - 30:
            d.rectangle([left + 40, yy + 4, left + 56, yy + size + 4], fill=TEAL)

# ---------------------------------------------------------------- bullets
def card_layer(i, text, style):
    f = fit_font("Inter-SemiBold.otf", text, 44, 900)
    w, h = 1060, 108
    L = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=20, fill=(255, 255, 255, 14), outline=(255, 255, 255, 30), width=2)
    col = {"goal": VIOLET, "warn": AMBER, "tip": TEAL}.get(style, VIOLET)
    d.rounded_rectangle([0, 0, 8, h - 1], radius=4, fill=col + (255,))
    d.ellipse([34, 24, 94, 84], fill=col + (255,))
    if style == "warn":
        d.text((64, 54), "!", font=F("Inter-Black.otf", 36), fill=(30, 20, 10), anchor="mm")
    else:
        d.text((64, 54), str(i + 1), font=F("Inter-Bold.otf", 30), fill=(255, 255, 255), anchor="mm")
    d.text((124, 54), text, font=f, fill=FG, anchor="lm")
    return L

def side_terminal(im, rows, tg):
    x0, y0, x1, y1 = 1260, 300, 1820, 800
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=(16, 18, 30), outline=(255, 255, 255, 26), width=2)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([x0 + 24 + i * 26, y0 + 22, x0 + 38 + i * 26, y0 + 36], fill=c)
    f = F("JetBrainsMono-Regular.ttf", 24)
    shown = int(tg / 1.6) + 1
    for i, (t, c) in enumerate(rows[:shown]):
        d.text((x0 + 30, y0 + 70 + i * 44), t, font=f, fill=COLORS.get(c, FG))
    if int(tg * 2) % 2 == 0:
        yy = y0 + 70 + min(shown, len(rows)) * 44
        if yy < y1 - 40: d.rectangle([x0 + 30, yy + 4, x0 + 44, yy + 30], fill=TEAL)

def side_icon(im, kind):
    cx, cy = 1540, 540
    col = AMBER if kind == "warning" else TEAL
    glow = Image.new("RGBA", (700, 700), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([150, 150, 550, 550], fill=col + (70,))
    paste_alpha(im, glow.filter(ImageFilter.GaussianBlur(70)), (cx - 350, cy - 350))
    d = ImageDraw.Draw(im)
    if kind == "warning":
        d.polygon([(cx, cy - 190), (cx + 210, cy + 170), (cx - 210, cy + 170)], fill=AMBER)
        d.text((cx, cy + 40), "!", font=F("Inter-Black.otf", 220), fill=(20, 14, 8), anchor="mm")
    else:  # check
        d.ellipse([cx - 180, cy - 180, cx + 180, cy + 180], fill=TEAL)
        d.line([(cx - 90, cy), (cx - 20, cy + 75), (cx + 100, cy - 80)], fill=(10, 30, 28), width=38, joint="curve")

def bullets_scene(im, sc, k, ts, tg):
    items = [s[1] for s in sc["steps"][:k + 1] if s[1]]
    style = sc.get("style", "goal")
    for i, t in enumerate(items):
        is_new = i == len(items) - 1 and sc["steps"][k][1] == t
        a = ease(ts / 0.45) if is_new else 1
        paste_alpha(im, card_layer(i, t, style), (100 + (1 - a) * 70, 250 + i * 140), a)
    side = sc.get("side")
    if isinstance(side, dict) and "terminal" in side: side_terminal(im, side["terminal"], tg)
    elif side in ("warning", "check"): side_icon(im, side)

# ---------------------------------------------------------------- rows diagram
def chip_layer(label, col):
    f = F("Inter-SemiBold.otf", 30); w = int(f.getlength(label) + 48)
    L = Image.new("RGBA", (w, 66), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([0, 0, w - 1, 65], radius=18, fill=col + (255,))
    d.text((w / 2, 33), label, font=f, fill=(255, 255, 255), anchor="mm")
    return L

def rows_scene(im, sc, k, ts):
    stage = sc["steps"][k][1]
    d = ImageDraw.Draw(im, "RGBA")
    if sc.get("subtitle"):
        d.text((100, 222), sc["subtitle"], font=F("Inter-Medium.otf", 38), fill=MUTED)
    if stage == 1:
        a = ease(ts / 0.6)
        L = gradient_text(sc["headline"], F("InterDisplay-Black.otf", 190), VIOLET, TEAL)
        paste_alpha(im, L, ((W - L.width) / 2, 470 + (1 - a) * 40), a)
        if sc.get("headline_sub"):
            d.text((W / 2, 760), sc["headline_sub"], font=F("Inter-Medium.otf", 44), fill=mixc(MUTED, (12, 14, 26), a), anchor="mm")
        return
    y, idx = 340, 0
    for r, row in enumerate(sc["rows"]):
        d.text((100, y + 33), row["label"], font=F("Inter-Bold.otf", 36), fill=FG, anchor="lm")
        x = 290
        for lab, kind in row["chips"]:
            a = ease((ts - idx * 0.07) / 0.35) if stage == 2 else 1
            L = chip_layer(lab, CHIP.get(kind, CHIP["system"]))
            paste_alpha(im, L, (x, y + (1 - a) * 20), a); x += L.width + 14; idx += 1
        if row.get("arrow"):
            d.text((x + 12, y + 33), "→  " + row["arrow"], font=F("Inter-SemiBold.otf", 34), fill=MUTED, anchor="lm")
        if stage >= 3 and sc.get("bar_label"):
            g = ease((ts - r * 0.15) / 0.8)
            frac = row.get("bar", len(row["chips"]) / max(len(rr["chips"]) for rr in sc["rows"]))
            d.rounded_rectangle([1360, y + 14, 1820, y + 52], radius=12, fill=(255, 255, 255, 16))
            bw = int(460 * frac * g)
            if bw > 24: d.rounded_rectangle([1360, y + 14, 1360 + bw, y + 52], radius=12, fill=AMBER)
        y += 150
    if stage >= 3:
        if sc.get("bar_label"): d.text((1360, 290), sc["bar_label"].upper(), font=F("Inter-Bold.otf", 26), fill=AMBER)
        if sc.get("callout"):
            a = ease((ts - 0.6) / 0.5)
            d.rounded_rectangle([100, 820, 1820, 920], radius=20, fill=(255, 166, 77, int(26 * a)), outline=(255, 166, 77, int(120 * a)), width=2)
            d.text((140, 870), sc["callout"], font=fit_font("Inter-Medium.otf", sc["callout"], 36, 1640), fill=mixc(FG, (30, 26, 30), a), anchor="lm")

# ---------------------------------------------------------------- flow diagram
def flow_scene(im, sc, k, ts):
    boxes = sc["boxes"]  # list of [title, caption, kind]
    vis = min(sc["steps"][k][1], len(boxes))
    prev = 0 if k == 0 else min(sc["steps"][k - 1][1], len(boxes))
    d = ImageDraw.Draw(im, "RGBA")
    if sc.get("subtitle"):
        d.text((100, 222), sc["subtitle"], font=F("Inter-Medium.otf", 38), fill=MUTED)
    n = len(boxes); gap = 70
    bw = min(380, (W - 200 - gap * (n - 1)) // n); bh = 260
    total = n * bw + (n - 1) * gap; x0 = (W - total) // 2; y0 = 440
    for i, (title, cap, kind) in enumerate(boxes):
        if i >= vis: break
        a = ease((ts - (i - prev) * 0.25) / 0.45) if i >= prev else 1
        x = x0 + i * (bw + gap)
        col = CHIP.get(kind, VIOLET)
        L = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        ld.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=24, fill=(255, 255, 255, 16), outline=col + (255,), width=3)
        ld.rounded_rectangle([0, 0, bw - 1, 12], radius=6, fill=col + (255,))
        ld.text((bw / 2, 95), title, font=fit_font("InterDisplay-Bold.otf", title, 44, bw - 40), fill=FG + (255,), anchor="mm")
        words, lines_, cur = cap.split(), [], ""
        cf = F("Inter-Medium.otf", 28)
        for w_ in words:
            if cf.getlength(cur + " " + w_) > bw - 50 and cur: lines_.append(cur); cur = w_
            else: cur = (cur + " " + w_).strip()
        lines_.append(cur)
        for j, ln in enumerate(lines_[:3]):
            ld.text((bw / 2, 160 + j * 36), ln, font=cf, fill=MUTED + (255,), anchor="mm")
        paste_alpha(im, L, (x, y0 + (1 - a) * 30), a)
        if i > 0:
            ax = x - gap + 12
            d.line([(ax, y0 + bh / 2), (x - 14, y0 + bh / 2)], fill=mixc(MUTED, (14, 16, 28), a), width=5)
            d.polygon([(x - 10, y0 + bh / 2), (x - 26, y0 + bh / 2 - 12), (x - 26, y0 + bh / 2 + 12)], fill=mixc(MUTED, (14, 16, 28), a))
    if sc.get("callout") and vis >= n:
        a = ease((ts - 0.8) / 0.5) if prev < n else 1
        d.rounded_rectangle([100, 820, 1820, 920], radius=20, fill=(45, 212, 191, int(22 * a)), outline=(45, 212, 191, int(120 * a)), width=2)
        d.text((140, 870), sc["callout"], font=fit_font("Inter-Medium.otf", sc["callout"], 36, 1640), fill=mixc(FG, (20, 30, 34), a), anchor="lm")

# ---------------------------------------------------------------- title / outro / endcard
def glow_center(im, col=VIOLET):
    g = Image.new("RGBA", (1400, 700), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([250, 150, 1150, 550], fill=col + (60,))
    paste_alpha(im, g.filter(ImageFilter.GaussianBlur(90)), (260, 200))

def pill(text, size=28, col=VIOLET):
    f = F("Inter-SemiBold.otf", size); w = int(f.getlength(text) + 60)
    L = Image.new("RGBA", (w, 56), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([0, 0, w - 1, 55], radius=28, fill=col + (40,), outline=col + (160,), width=2)
    d.text((w / 2, 28), text, font=f, fill=mixc(col, (255, 255, 255), 0.55), anchor="mm")
    return L

def title_scene(im, L, sc, tg):
    glow_center(im)
    d = ImageDraw.Draw(im)
    a = ease((tg - 0.0) / 0.6)
    logo_mark(d, 100, 70, 1.0)
    d.text((160, 92), CHANNEL, font=F("Inter-Bold.otf", 30), fill=mixc(FG, (20, 20, 40), a), anchor="lm")
    a = ease((tg - 0.1) / 0.7)
    P = pill(COURSE.upper()); paste_alpha(im, P, ((W - P.width) / 2, 330 + (1 - a) * 20), a)
    a = ease((tg - 0.35) / 0.7)
    T = gradient_text(L["title"], fit_font("InterDisplay-Black.otf", L["title"], 150, W - 200), FG, (200, 190, 255))
    paste_alpha(im, T, ((W - T.width) / 2, 430 + (1 - a) * 30), a)
    a = ease((tg - 0.6) / 0.7)
    sub = f"Module {L['module']}  ·  Lesson {L['number']}"
    S = Image.new("RGBA", (1000, 70), (0, 0, 0, 0))
    ImageDraw.Draw(S).text((500, 35), sub, font=F("Inter-Medium.otf", 44), fill=MUTED + (255,), anchor="mm")
    paste_alpha(im, S, ((W - 1000) / 2, 640), a)
    bw = int(260 * a)
    d.rounded_rectangle([W / 2 - bw / 2, 740, W / 2 + bw / 2, 746], radius=3, fill=TEAL)

def outro_scene(im, L, sc, k, ts, tg):
    glow_center(im)
    a = ease((tg - 0.1) / 0.7)
    P = pill(f"LESSON {L['number']}  ·  RECAP"); paste_alpha(im, P, ((W - P.width) / 2, 300 + (1 - a) * 20), a)
    a = ease((tg - 0.35) / 0.7)
    T = gradient_text(sc.get("title", "Your homework"), F("InterDisplay-Black.otf", 140), FG, (200, 190, 255))
    paste_alpha(im, T, ((W - T.width) / 2, 400 + (1 - a) * 30), a)
    tasks = sc["tasks"]
    f2 = F("Inter-SemiBold.otf", 34 if len(tasks) <= 3 else 28)
    widths = [f2.getlength(t) + 110 for t in tasks]
    x = (W - (sum(widths) + 30 * (len(tasks) - 1))) / 2
    for i, t in enumerate(tasks):
        aa = ease((tg - 0.6 - i * 0.2) / 0.7)
        C = Image.new("RGBA", (int(widths[i]), 76), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
        cd.rounded_rectangle([0, 0, widths[i] - 1, 75], radius=38, fill=(255, 255, 255, 16), outline=(45, 212, 191, 150), width=2)
        cd.ellipse([22, 22, 54, 54], outline=TEAL + (255,), width=3)
        cd.line([(30, 38), (36, 45), (47, 31)], fill=TEAL + (255,), width=4)
        cd.text((72, 38), t, font=f2, fill=FG + (255,), anchor="lm")
        paste_alpha(im, C, (x, 610 + (1 - aa) * 20), aa); x += widths[i] + 30
    if k >= 1 and L.get("next"):
        aa = ease(ts / 0.6)
        txt = "NEXT  ·  " + L["next"] + "  →"
        nf = fit_font("Inter-SemiBold.otf", txt, 32, 1500); nw = int(nf.getlength(txt) + 80)
        N = Image.new("RGBA", (nw, 90), (0, 0, 0, 0)); nd = ImageDraw.Draw(N)
        nd.rounded_rectangle([0, 0, nw - 1, 89], radius=20, fill=(139, 108, 255, 50))
        nd.text((nw / 2, 45), txt, font=nf, fill=FG + (255,), anchor="mm")
        paste_alpha(im, N, ((W - nw) / 2, 780 + (1 - aa) * 20), aa)
    d = ImageDraw.Draw(im)
    d.text((W / 2, H - 70), f"Code for this lesson: github.com/Obligence/prompt-to-production  ·  Subscribe: {HANDLE}",
           font=F("Inter-Medium.otf", 24), fill=(120, 126, 150), anchor="mm")

# ---------------------------------------------------------------- frame dispatcher
def draw(L, scenes, si, k, ts, tg):
    sc = scenes[si]
    im = BG.copy()
    kind = sc["kind"]
    if kind == "title": title_scene(im, L, sc, tg)
    elif kind == "outro": outro_scene(im, L, sc, k, ts, tg)
    else:
        chrome(im, L, sc, si, len(scenes))
        {"code": lambda: code_scene(im, sc, k, ts), "terminal": lambda: terminal_scene(im, sc, k, ts),
         "bullets": lambda: bullets_scene(im, sc, k, ts, tg), "rows": lambda: rows_scene(im, sc, k, ts),
         "flow": lambda: flow_scene(im, sc, k, ts)}[kind]()
    return im

def animated_all_the_time(sc):
    return (sc["kind"] == "bullets" and isinstance(sc.get("side"), dict)) or sc["kind"] == "terminal"

# ---------------------------------------------------------------- audio
def sentences(text):
    return [x for x in re.split(r"(?<=[.?!])\s+", text.strip()) if x]

def tts(scenes, adir):
    from kokoro_onnx import Kokoro
    k = None
    meta = {}
    for si, sc in enumerate(scenes):
        for j, (text, _) in enumerate(sc["steps"]):
            p = f"{adir}/a_{si:02d}_{j}.wav"; mp = p + ".json"
            key = f"{VOICE}|{SPEED}|{text}"
            if os.path.exists(p) and os.path.exists(mp) and json.load(open(mp))["key"] == key:
                meta[(si, j)] = json.load(open(mp))["sents"]; continue
            if k is None: k = Kokoro(f"{CACHE}/kokoro-v1.0.onnx", f"{CACHE}/voices-v1.0.bin")
            parts, sents, t = [], [], 0.0
            for s in sentences(text):
                a, sr = k.create(s, voice=VOICE, speed=SPEED, lang="en-us")
                sents.append([t, t + len(a) / SR, s]); t += len(a) / SR + 0.28
                parts += [a, np.zeros(int(0.28 * SR), np.float32)]
            sf.write(p, np.concatenate(parts[:-1]), SR)
            json.dump({"key": key, "sents": sents}, open(mp, "w"))
            meta[(si, j)] = sents
    return meta

GAP, LEAD, TAIL, FADE = 0.45, 0.5, 0.9, 0.3

def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def spoken_for_srt(s):
    return s  # narration is written for the voice; keep as is

# ---------------------------------------------------------------- main
def load_lesson(path):
    spec = importlib.util.spec_from_file_location("lesson", path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.LESSON, mod.SCENES

def main():
    global BG
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson"); ap.add_argument("--preview", action="store_true")
    ap.add_argument("--scenes", default="", help="comma list of scene indexes to re-render (others reused)")
    args = ap.parse_args()
    L, scenes = load_lesson(args.lesson)
    slug = L["slug"]
    bdir = f"{ROOT}/build/{slug}"; os.makedirs(bdir, exist_ok=True)
    BG = make_bg()
    if args.preview:
        for si, sc in enumerate(scenes):
            for k in range(len(sc["steps"])):
                draw(L, scenes, si, k, 3.0, 5.0 + 3 * k).save(f"{bdir}/preview_{si:02d}_{k}.png")
        make_cover(L, f"{bdir}/preview_cover.jpg")
        print("previews in", bdir); return
    meta = tts(scenes, bdir)
    audio, srt, chapters, durs_all, t0 = [], [], [], [], 0.0
    for si, sc in enumerate(scenes):
        durs = []
        audio.append(np.zeros(int(LEAD * SR), np.float32)); t = t0 + LEAD
        for j in range(len(sc["steps"])):
            a, _ = sf.read(f"{bdir}/a_{si:02d}_{j}.wav", dtype="float32")
            for s0, s1, s in meta[(si, j)]: srt.append((t + s0, t + s1, s))
            pad = TAIL if j == len(sc["steps"]) - 1 else GAP
            audio += [a, np.zeros(int(pad * SR), np.float32)]
            d_ = len(a) / SR + pad + (LEAD if j == 0 else 0)
            # keep the audio sample-accurate with the frame grid
            durs.append(d_); t += len(a) / SR + pad
        chapters.append((t0, sc.get("chapter", sc.get("title", L["title"]) if sc["kind"] != "title" else "Intro")))
        durs_all.append(durs); t0 += sum(durs)
    total_all = t0
    sf.write(f"{bdir}/narration.wav", np.concatenate(audio), SR)
    only = {int(x) for x in args.scenes.split(",") if x != ""}
    files, tb = [], 0.0
    for si, sc in enumerate(scenes):
        mp4 = f"{bdir}/scene_{si:02d}.mp4"; files.append(mp4)
        if only and si not in only and os.path.exists(mp4): tb += sum(durs_all[si]); continue
        render_scene(L, scenes, si, durs_all[si], tb, total_all, mp4)
        print("scene", si, "done", flush=True)
        tb += sum(durs_all[si])
    with open(f"{bdir}/list.txt", "w") as fh:
        for f_ in files: fh.write(f"file '{f_}'\n")
    os.makedirs(f"{ROOT}/videos", exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{bdir}/list.txt", "-c", "copy", f"{bdir}/video_only.mp4"])
    tmp = f"{bdir}/final_tmp.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{bdir}/video_only.mp4", "-i", f"{bdir}/narration.wav", "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", tmp])
    os.replace(tmp, f"{ROOT}/videos/{slug}.mp4")
    os.makedirs(f"{ROOT}/captions", exist_ok=True); os.makedirs(f"{ROOT}/meta", exist_ok=True); os.makedirs(f"{ROOT}/covers", exist_ok=True)
    with open(f"{ROOT}/captions/{slug}.srt", "w") as fh:
        for i, (a, b, s) in enumerate(srt, 1): fh.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{spoken_for_srt(s)}\n\n")
    with open(f"{ROOT}/meta/{slug}_chapters.txt", "w") as fh:
        for t, name in chapters: fh.write(f"{int(t // 60)}:{int(t % 60):02d} {name}\n")
    make_cover(L, f"{ROOT}/covers/{slug}.jpg")
    print("done:", f"videos/{slug}.mp4", f"{total_all:.1f}s")

def run(cmd):
    subprocess.run(cmd, check=True)

def render_scene(L, scenes, si, durs, t_before, total_all, mp4):
    sc = scenes[si]; total = sum(durs); nfr = int(round(total * FPS))
    starts = np.cumsum([0] + durs[:-1])
    tmp = mp4[:-4] + "_tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    cache, always = {}, animated_all_the_time(sc)
    for fi in range(nfr):
        t = fi / FPS
        k = int(np.searchsorted(starts, t, side="right") - 1); ts = t - starts[k]
        static = ts > 1.8 and not always and not (sc["kind"] in ("title", "outro") and t < 2.6)
        if static and k in cache: fr = cache[k].copy()
        else:
            fr = draw(L, scenes, si, k, ts, t)
            if static: cache[k] = fr.copy()
        progress(fr, (t_before + t) / total_all)
        if t < FADE: fr = Image.blend(BG, fr, t / FADE)
        elif t > total - FADE: fr = Image.blend(BG, fr, max(0.0, (total - t) / FADE))
        p.stdin.write(fr.tobytes())
    p.stdin.close()
    if p.wait() != 0: raise SystemExit(f"ffmpeg failed on scene {si}")
    os.replace(tmp, mp4)

def make_cover(L, path):
    """YouTube thumbnail 1280x720: big short title, lesson number, channel mark."""
    global BG
    if BG is None: BG = make_bg()
    im = BG.copy(); glow_center(im)
    d = ImageDraw.Draw(im)
    logo_mark(d, 100, 80, 1.6)
    d.text((190, 116), CHANNEL, font=F("Inter-Bold.otf", 44), fill=FG, anchor="lm")
    P = pill(f"LESSON {L['number']}  ·  FREE COURSE", 34, TEAL); paste_alpha(im, P, (100, 230))
    words = L.get("cover_text", L["title"]).upper().split("|")
    y = 340
    for i, line in enumerate(words):
        f = fit_font("InterDisplay-Black.otf", line, 210, W - 200)
        T = gradient_text(line, f, FG if i == 0 else VIOLET, (210, 200, 255) if i == 0 else TEAL)
        paste_alpha(im, T, (100, y)); y += T.height + 30
    im.resize((1280, 720), Image.LANCZOS).save(path, quality=92)

if __name__ == "__main__":
    main()
