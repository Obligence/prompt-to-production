"""Channel brand images: profile picture (800x800) and banner (2560x1440, text inside the 1546x423 safe area)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "template"))
import build as B

OUT = os.path.dirname(os.path.abspath(__file__))

def bg(w, h):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    base = np.zeros((h, w, 3), np.float32) + np.array([11, 13, 24])
    for cx, cy, r, col, s in [(w * .3, h * .35, w * .22, B.VIOLET, .30), (w * .72, h * .7, w * .2, B.TEAL, .16)]:
        base += np.exp(-(((x - cx) ** 2 + (y - cy) ** 2) / (2 * r * r)))[..., None] * np.array(col) * s
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    step = max(24, w // 60)
    for gx in range(step // 2, w, step):
        for gy in range(step // 2, h, step):
            d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(255, 255, 255, 20))
    return im

def mark(size):
    """Logo: violet rounded square, white prompt chevron, teal cursor."""
    s = size / 100
    L = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    g = Image.new("L", (size, 1)); g.putdata([int(255 * i / (size - 1)) for i in range(size)]); g = g.resize((size, size))
    grad = Image.composite(Image.new("RGB", (size, size), (110, 80, 240)), Image.new("RGB", (size, size), (160, 130, 255)), g)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=int(26 * s), fill=255)
    L.paste(grad, (0, 0), m)
    d = ImageDraw.Draw(L)
    w = int(10 * s)
    d.line([(27 * s, 30 * s), (50 * s, 50 * s), (27 * s, 70 * s)], fill=(255, 255, 255), width=w, joint="curve")
    for cx, cy in [(27 * s, 30 * s), (50 * s, 50 * s), (27 * s, 70 * s)]:
        d.ellipse([cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2], fill=(255, 255, 255))
    d.rounded_rectangle([56 * s, 64 * s, 76 * s, 74 * s], radius=int(5 * s), fill=B.TEAL)
    return L

def profile():
    im = bg(800, 800)
    glow = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([150, 150, 650, 650], fill=B.VIOLET + (110,))
    B.paste_alpha(im, glow.filter(ImageFilter.GaussianBlur(80)), (0, 0))
    M = mark(440)
    B.paste_alpha(im, M, (180, 180))
    im.save(f"{OUT}/profile_picture.png")

def banner():
    W, H = 2560, 1440
    im = bg(W, H)
    d = ImageDraw.Draw(im)
    # YouTube safe area (shown on every device): 1546x423 centered -> x 507..2053, y 508..931
    msz, gap = 200, 50
    t = B.gradient_text("Prompt to Production", B.F("InterDisplay-Black.otf", 104), B.FG, (200, 190, 255))
    tag = "Build real AI apps with LLMs, from your first prompt to production."
    tf = B.F("Inter-Medium.otf", 36)
    P = B.pill("FREE FULL COURSES  ·  NEW LESSONS DAILY", 28, B.TEAL)
    textw = max(t.width, int(tf.getlength(tag)), P.width)
    x0 = (W - (msz + gap + textw)) // 2
    y0 = (H - msz) // 2
    B.paste_alpha(im, mark(msz), (x0, y0))
    tx = x0 + msz + gap
    B.paste_alpha(im, t, (tx, y0 - 14))
    d.text((tx + 4, y0 + 118), tag, font=tf, fill=(170, 176, 200))
    B.paste_alpha(im, P, (tx + 4, y0 + 178))
    assert x0 >= 507 and x0 + msz + gap + textw <= 2053, (x0, textw)
    im.save(f"{OUT}/channel_banner.png")

if __name__ == "__main__":
    profile(); banner(); print("ok")
