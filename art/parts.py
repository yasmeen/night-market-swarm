"""Booth parts for in-browser composition: base, counter, and goods sprites (day colors, untinted)."""
import sys, random
from PIL import Image, ImageDraw
import market as M
from market import R, box, block, sh, OUT, CREAM
import night as N
sys.argv = [sys.argv[0], sys.argv[1]]
OUTD = sys.argv[1]

def save1(im, name): im.save(f"{OUTD}/{name}.png")

im = Image.new("RGBA", (76, 52), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
R(d, 8, 11, 60, 20, (98, 78, 88)); R(d, 10, 19, 56, 1, (140, 110, 100))
rnd = random.Random(3)
for bx in range(12, 62, 5):
    if abs(bx - 38) > 9: R(d, bx, 14, 3, 5, rnd.choice([(150, 200, 170), (240, 200, 120), (230, 140, 130), (170, 190, 230)]))
box(d, 7, 11, 3, 32, (120, 124, 140)); box(d, 66, 11, 3, 32, (120, 124, 140))
save1(im, "b_base")

im = Image.new("RGBA", (76, 52), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
block(d, 6, 29, 64, 15, (218, 224, 232), (156, 166, 182), 8)
box(d, 11, 43, 6, 5, (70, 64, 78)); box(d, 59, 43, 6, 5, (70, 64, 78))
save1(im, "b_counter")

def g_chart(d, x, y):
    box(d, x, y - 3, 22, 13, CREAM)
    for k, hh in enumerate([4, 7, 3, 8, 5]):
        R(d, x + 2 + k * 4, y + 8 - hh, 3, hh, [(110, 190, 170), (250, 200, 90), (236, 110, 130), (84, 164, 124), (130, 150, 220)][k])
    box(d, x + 28, y + 1, 12, 9, (80, 78, 96)); R(d, x + 30, y + 3, 8, 4, (150, 226, 190))
    box(d, x + 44, y + 3, 5, 7, (236, 180, 176)); box(d, x + 51, y + 3, 5, 7, (176, 212, 220))

def g_fruit(d, x, y):
    for k, c in enumerate([(250, 200, 80), (240, 110, 140), (140, 200, 110), (250, 150, 70), (200, 90, 90)]):
        box(d, x + k * 11, y + 3, 10, 7, (236, 240, 244))
        d.ellipse([x + k * 11 + 1, y + 1, x + k * 11 + 5, y + 5], fill=c, outline=OUT)
        d.ellipse([x + k * 11 + 5, y + 2, x + k * 11 + 9, y + 6], fill=c, outline=OUT)

def g_boba(d, x, y):
    for k, c in enumerate([(214, 170, 130), (240, 190, 200), (170, 210, 170), (214, 170, 130), (190, 170, 220)]):
        box(d, x + k * 9, y + 1, 7, 9, (246, 244, 240)); R(d, x + k * 9 + 1, y + 3, 5, 4, c)
        R(d, x + k * 9 + 2, y + 7, 1, 1, (60, 40, 40)); R(d, x + k * 9 + 4, y + 7, 1, 1, (60, 40, 40))
        R(d, x + k * 9 + 4, y - 3, 1, 5, (220, 90, 90))
    box(d, x + 47, y + 2, 8, 8, (120, 124, 140)); R(d, x + 49, y + 4, 4, 2, (150, 226, 190))

import importlib
L = importlib.import_module  # layers.py runs as a script; pull its goods functions by exec
ns = {}
src = open("layers.py").read()
exec(src[src.index("def g_lock"):src.index("def lady")], {**M.__dict__, "person": M.person}, ns)
GOODS = {"orders": M.g_orders, "lock": ns["g_lock"], "paint": ns["g_paint"], "seo": ns["g_seo"], "wok": M.g_wok, "parcels": M.g_ship,
         "bowls": M.g_review, "plan": M.g_plan, "curios": N.g_curios, "scrolls": N.g_scrolls, "chart": g_chart, "fruit": g_fruit, "boba": g_boba}
for k, fn in GOODS.items():
    M.late.clear()
    im = Image.new("RGBA", (62, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fn(d, 0, 14)
    for f in M.late: f(d)
    save1(im, "goods_" + k)
print(sorted(GOODS))
