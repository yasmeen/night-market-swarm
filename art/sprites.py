import sys
from PIL import Image, ImageDraw
import market as M
from market import R, box, OUT, CREAM
from scenes import FRONT, BACK
from night import cat

OUTD = sys.argv[1]
SIDE = FRONT[:4] + ["..OHHHSSSO..", "..OHHSSeSO..", "..OHHSSSSO..", "...OHSSSO..."] + FRONT[8:]


def frames(rows):
    a = list(rows); a[14] = "..OOOOOPPO.."; a[15] = ".......OOO.."
    b = list(rows); b[14] = "..OPPOOOOO.."; b[15] = "..OOO......."
    return {"s": rows, "a": a, "b": b}


def person(rows, hair, shirt, skin=(244, 208, 174), pants=(96, 98, 126), extra=None):
    im = Image.new("RGBA", (12, 17), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pal = {"O": OUT, "H": hair, "S": skin, "e": OUT, "C": shirt, "P": pants}
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != ".":
                R(d, i, j + 1, 1, 1, pal[ch])
    if extra:
        extra(d)
    return im


def save(im, name):
    im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(f"{OUTD}/{name}.png")


hair, hood = (52, 44, 60), (92, 170, 170)
for dname, rows in (("down", FRONT), ("up", BACK), ("right", SIDE)):
    for f, rr in frames(rows).items():
        ex = None
        if dname == "up":
            ex = lambda d: R(d, 5, 8, 2, 5, hair)
        if dname == "down":
            ex = lambda d: (R(d, 2, 3, 1, 5, hood), R(d, 9, 3, 1, 5, hood))
        save(person(rr, hair, hood, extra=ex), f"you_{dname}_{f}")

for f, rr in frames(SIDE).items():
    if f == "s":
        continue
    def tix(d):
        R(d, 3, 10, 6, 4, CREAM); R(d, 4, 9, 4, 1, CREAM)
        box(d, 8, 9, 5, 6, (250, 244, 230)); R(d, 9, 11, 3, 1, (200, 90, 80))
    save(person(rr, (150, 96, 70), (236, 200, 116), skin=(206, 160, 122), extra=tix), f"courier_{f}")

for f in "ab":
    im = Image.new("RGBA", (17, 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cat(d, 4, 2)
    if f == "b":
        R(d, 1, 3, 1, 2, OUT); R(d, 1, 5, 1, 1, (0, 0, 0, 0))
    save(im, f"cat_{f}")
    im = Image.new("RGBA", (18, 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    M.dog(d, 3, 2)
    if f == "b":
        R(d, 1, 2, 1, 2, OUT)
    save(im, f"dog_{f}")

im = Image.new("RGBA", (26, 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
M.late.clear(); M.lights.clear()
box(d, 10, 2, 7, 7, (244, 208, 174)); R(d, 11, 3, 5, 2, (70, 62, 76)); box(d, 10, 1, 7, 3, (214, 84, 76))
box(d, 9, 8, 9, 7, (132, 172, 216))
M.scooter(d, 2, 10, (250, 200, 90), boxc=(214, 84, 76))
R(d, 2, 13, 2, 2, (255, 244, 200))
save(im, "scooter")

im = Image.new("RGBA", (7, 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
for y, row in enumerate([".OO.OO.", "OHHOHHO", "OHHHHHO", ".OHHHO.", "..OHO..", "...O..."]):
    for x, ch in enumerate(row):
        if ch != ".":
            R(d, x, y, 1, 1, OUT if ch == "O" else (244, 120, 150))
save(im, "heart")
