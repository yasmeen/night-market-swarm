import sys, random
from PIL import Image, ImageDraw, ImageChops
import market as M
from market import R, box, block, sh, OUT, CREAM, AMBER, RED, W, H, person, plant, crate, cat, bubble, paper

OUTD = sys.argv[1]
S = 3
NIGHT, WARM = (180, 166, 216), (255, 246, 226)


def tint(im, col):
    r, g, b, a = im.split()
    rgb = ImageChops.multiply(Image.merge("RGB", (r, g, b)), Image.new("RGB", im.size, col))
    return Image.merge("RGBA", (*rgb.split(), a))


def save(im, name):
    im.resize((im.width * S, im.height * S), Image.NEAREST).save(f"{OUTD}/{name}.png")


def g_lock(d, x, y):
    for k, c in enumerate([(240, 200, 110), (190, 196, 210), (240, 200, 110)]):
        box(d, x + k * 11, y + 3, 9, 7, c)
        d.arc([x + k * 11 + 1, y - 2, x + k * 11 + 7, y + 6], 180, 360, fill=OUT)
        R(d, x + k * 11 + 4, y + 5, 1, 2, OUT)
    box(d, x + 36, y - 2, 13, 12, (80, 110, 180))
    R(d, x + 38, y, 9, 1, CREAM)
    R(d, x + 40, y + 2, 5, 5, (240, 200, 110))
    box(d, x + 51, y + 3, 5, 7, (120, 124, 140))


def g_paint(d, x, y):
    for k, c in enumerate([(236, 110, 130), (250, 200, 90), (110, 190, 170), (130, 150, 220)]):
        box(d, x + k * 8, y + 3, 7, 7, (236, 240, 244))
        R(d, x + k * 8 + 1, y + 4, 5, 2, c)
    box(d, x + 34, y - 4, 16, 13, CREAM)
    R(d, x + 36, y - 2, 5, 4, (236, 110, 130))
    R(d, x + 42, y - 2, 6, 2, (130, 150, 220))
    R(d, x + 36, y + 3, 12, 1, (110, 190, 170))
    R(d, x + 36, y + 5, 8, 1, (250, 200, 90))
    R(d, x + 53, y - 3, 1, 9, (150, 106, 72))
    R(d, x + 52, y - 5, 3, 3, (236, 110, 130))
    box(d, x + 51, y + 5, 5, 5, (120, 150, 200))


def g_seo(d, x, y):
    box(d, x, y - 3, 20, 13, CREAM)
    for k, hh in enumerate([3, 5, 4, 8]):
        R(d, x + 3 + k * 4, y + 8 - hh, 3, hh, [(110, 190, 170), (250, 200, 90), (236, 110, 130), (84, 164, 124)][k])
    d.ellipse([x + 26, y - 1, x + 35, y + 8], fill=(190, 226, 240), outline=OUT)
    R(d, x + 34, y + 7, 4, 2, OUT)
    R(d, x + 28, y + 2, 2, 1, (240, 250, 255))
    for k in range(3):
        box(d, x + 42, y + 7 - k * 4, 13, 4, [(250, 244, 230), (236, 226, 190), (250, 244, 230)][k])
        R(d, x + 44, y + 8 - k * 4, 8, 1, (120, 130, 150))


def lady(**k):
    return lambda d, x, y: person(d, x, y, **k)


STALLS = {
    "orders": ("gold", lady(hair=(92, 70, 60), shirt=(236, 200, 116), acc=("straw",)), M.g_orders, (244, 204, 96)),
    "security": ("nb", lady(hair=(60, 80, 110), shirt=(120, 140, 200), acc=("glasses",)), g_lock, (70, 92, 168)),
    "design": ("pw", lady(hair=(214, 196, 160), shirt=(236, 150, 180), skin=(206, 160, 122), acc=("bun", "glasses")), g_paint, (238, 142, 164)),
    "seo": ("yg", lady(hair=(232, 150, 110), shirt=(144, 198, 152), acc=("hood",)), g_seo, (84, 164, 124)),
    "code": ("rwb", lady(hair=(70, 62, 76), shirt=(132, 172, 216), acc=("beanie", "apron")), M.g_wok, (214, 84, 76)),
    "backlog": ("ow", lady(hair=(176, 110, 80), shirt=(244, 170, 110), skin=(206, 160, 122), acc=("band", "apron")), M.g_ship, (244, 154, 74)),
    "review": ("tw", lady(hair=(120, 110, 130), shirt=(234, 152, 132), acc=("glasses", "apron")), M.g_review, (72, 172, 172)),
    "spare": ("rwb", None, M.g_ship, (120, 124, 140)),
}

for key, (tarp, who, goods, panel) in STALLS.items():
    M.late.clear(); M.lights.clear()
    im = Image.new("RGBA", (76, 52), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    M.stall(d, 6, -11, None, tarp, who, goods, panel=panel)
    lit = tint(im, WARM)
    dl = ImageDraw.Draw(lit)
    for f in M.late:
        f(dl)
    dim = im.copy()
    dd = ImageDraw.Draw(dim)
    for f in M.late:
        f(dd)
    save(lit, f"stall_{key}_lit")
    save(tint(dim, (150, 140, 196)), f"stall_{key}_dim")

for kind in ("dots", "bang", "ok", "z"):
    im = Image.new("RGBA", (11, 9), (0, 0, 0, 0))
    bubble(ImageDraw.Draw(im), 0, 0, kind)
    save(im, f"bubble_{kind}")

g = Image.new("RGBA", (130, 104), (0, 0, 0, 0))
for f, a in ((1.0, 30), (0.74, 54), (0.48, 80)):
    layer = Image.new("RGBA", g.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse([65 - 64 * f, 52 - 51 * f, 65 + 64 * f, 52 + 51 * f], fill=(255, 226, 160, a))
    g = Image.alpha_composite(g, layer) if False else Image.composite(layer, g, layer.split()[3].point(lambda v: 255 if v else 0))
save(g, "glow")

# background
M.late.clear(); M.lights.clear()
day = Image.new("RGB", (W, H))
d = ImageDraw.Draw(day)
M.ground(d)
M.facades(d)
M.gate(d, title=None)
M.gas(d, 162, 96); M.gas(d, 254, 96, (120, 170, 200))
plant(d, 82, 96); plant(d, 332, 96)
M.string(d, 114, [0, 140, 284, W], 7, "lantern", 15)
M.table(d, 118, 150); M.table(d, 278, 150)
M.scooter(d, 300, 220, (90, 180, 150), boxc=(84, 164, 124))
crate(d, 100, 214); crate(d, 406, 196)
plant(d, 164, 200); plant(d, 250, 160)
for sx, sy, c in [(104, 190, RED), (214, 216, (70, 120, 200)), (286, 206, RED)]:
    box(d, sx, sy, 7, 7, c); R(d, sx + 2, sy + 2, 3, 2, sh(c, 1.25))
M.string(d, 224, [0, 212, W], 5, "bulb", 10)
M.scooter(d, 352, 222, (120, 150, 210)); M.scooter(d, 376, 222, (236, 150, 170))
night = ImageChops.multiply(day, Image.new("RGB", day.size, NIGHT))
warm = ImageChops.multiply(day, Image.new("RGB", day.size, WARM))
mask = Image.new("L", day.size, 0)
for cx, cy, r in M.lights:
    for f, v in ((1.0, 70), (0.74, 138), (0.48, 204)):
        layer = Image.new("L", day.size, 0)
        rr = r * f
        ImageDraw.Draw(layer).ellipse([cx - rr, cy - rr * 0.84, cx + rr, cy + rr * 0.84], fill=v)
        mask = ImageChops.lighter(mask, layer)
out = Image.composite(warm, night, mask)
dd = ImageDraw.Draw(out)
for f in M.late:
    f(dd)
save(out, "bg")
