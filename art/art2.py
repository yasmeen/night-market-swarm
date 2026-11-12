import sys, random
from PIL import Image, ImageDraw, ImageChops
import market as M
from market import R, box, block, sh, OUT, CREAM, AMBER, RED, person, plant, WOOD_T, WOOD_F
from scenes import FRONT
import night as N

OUTD = sys.argv[1]
W = 424


def save(im, name):
    im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(f"{OUTD}/{name}.png")


def tint(im, col):
    r, g, b, a = im.split()
    rgb = ImageChops.multiply(Image.merge("RGB", (r, g, b)), Image.new("RGB", im.size, col))
    return Image.merge("RGBA", (*rgb.split(), a))


# ---------- night market: head, segment, foot, extra stalls ----------
bg = Image.open(f"{OUTD}/bg.png")
bg.crop((0, 0, 1272, 702)).save(f"{OUTD}/nm_head.png")
bg.crop((0, 702, 1272, 792)).save(f"{OUTD}/nm_foot.png")

SEG = 96
M.late.clear(); M.lights.clear()
day = Image.new("RGB", (W, SEG))
d = ImageDraw.Draw(day)
base = (150, 146, 158)
R(d, 0, 0, W, SEG, base)
rnd = random.Random(9)
for _ in range(900):
    R(d, rnd.randrange(W), rnd.randrange(SEG), rnd.choice([1, 2]), 1, sh(base, rnd.choice([0.92, 0.95, 1.05])))
d.ellipse([190, 40, 232, 52], fill=(128, 150, 190)); R(d, 200, 45, 12, 1, (176, 196, 226))
plant(d, 82, 60); plant(d, 332, 60); M.gas(d, 166, 58); M.gas(d, 250, 58, (120, 170, 200))
for sx, sy, c in [(176, 76, RED), (240, 72, (70, 120, 200))]:
    box(d, sx, sy, 7, 7, c); R(d, sx + 2, sy + 2, 3, 2, sh(c, 1.25))
M.string(d, 80, [0, 140, 284, W], 5, "lantern", 15)
night = ImageChops.multiply(day, Image.new("RGB", day.size, (180, 166, 216)))
warm = ImageChops.multiply(day, Image.new("RGB", day.size, (255, 246, 226)))
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
save(out, "nm_seg")

lady = lambda **k: (lambda d, x, y: person(d, x, y, **k))
EXTRA = {
    "docs": ("tw", lady(hair=(150, 96, 70), shirt=(200, 190, 220), acc=("glasses",)), M.g_plan, (150, 110, 190)),
    "research": ("yg", lady(hair=(40, 40, 52), shirt=(240, 200, 120), skin=(206, 160, 122), acc=("bun",)), N.g_curios, (240, 200, 90)),
    "marketing": ("pw", lady(hair=(232, 190, 110), shirt=(240, 120, 110), acc=("band",)), N.g_scrolls, (240, 120, 110)),
    "data": ("nb", lady(hair=(90, 90, 110), shirt=(150, 200, 190), skin=(206, 160, 122), acc=("glasses", "apron")), None, (130, 136, 150)),
}
import importlib.util
for key, (tarp, who, goods, panel) in EXTRA.items():
    M.late.clear(); M.lights.clear()
    im = Image.new("RGBA", (76, 52), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if goods is None:
        def goods(d, x, y):
            box(d, x, y - 3, 22, 13, CREAM)
            for k, hh in enumerate([4, 7, 3, 8, 5]):
                R(d, x + 2 + k * 4, y + 8 - hh, 3, hh, [(110, 190, 170), (250, 200, 90), (236, 110, 130), (84, 164, 124), (130, 150, 220)][k])
            box(d, x + 28, y + 1, 12, 9, (80, 78, 96)); R(d, x + 30, y + 3, 8, 4, (150, 226, 190))
            box(d, x + 44, y + 3, 5, 7, (236, 180, 176)); box(d, x + 51, y + 3, 5, 7, (176, 212, 220))
    M.stall(d, 6, -11, None, tarp, who, goods, panel=panel)
    lit = tint(im, (255, 246, 226)); dl = ImageDraw.Draw(lit)
    for f in M.late: f(dl)
    dim = im.copy(); dm = ImageDraw.Draw(dim)
    for f in M.late: f(dm)
    save(lit, f"stall_{key}_lit"); save(tint(dim, (150, 140, 196)), f"stall_{key}_dim")
