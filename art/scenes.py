from PIL import Image, ImageDraw
import random, sys

T = 16
OUT = (58, 46, 52)
W, H = 320, 224


def sh(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def R(d, x, y, w, h, f):
    if w > 0 and h > 0:
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=f)


def box(d, x, y, w, h, f, o=OUT):
    R(d, x, y, w, h, o)
    R(d, x + 1, y + 1, w - 2, h - 2, f)


def block(d, x, y, w, h, top, front, fh):
    box(d, x, y, w, h, top)
    R(d, x + 1, y + h - 1 - fh, w - 2, fh, front)
    R(d, x + 1, y + h - 2 - fh, w - 2, 1, sh(front, 0.82))
    R(d, x + 1, y + 1, w - 2, 1, sh(top, 1.1))


# ---------- floors ----------
def wood(d, x0, y0, w, h, base=(216, 180, 128)):
    seam, hi = sh(base, 0.84), sh(base, 1.06)
    R(d, x0, y0, w, h, base)
    for ry in range(h):
        if ry % 8 == 7:
            R(d, x0, y0 + ry, w, 1, seam)
        elif ry % 8 == 0:
            R(d, x0, y0 + ry, w, 1, hi)
    for r in range(h // 8 + 1):
        off = 5 if r % 2 == 0 else 17
        yy = y0 + r * 8
        for x in range(x0 + off, x0 + w, 24):
            R(d, x, yy, 1, min(7, y0 + h - yy), seam)


def checker(a, b):
    def f(d, x0, y0, w, h):
        R(d, x0, y0, w, h, a)
        for yy in range(0, h, 8):
            for xx in range(0, w, 8):
                if (xx // 8 + yy // 8) % 2:
                    R(d, x0 + xx, y0 + yy, min(8, w - xx), min(8, h - yy), b)
    return f


def carpet(c):
    def f(d, x0, y0, w, h):
        R(d, x0, y0, w, h, c)
        rnd = random.Random(7)
        for _ in range(w * h // 40):
            R(d, x0 + rnd.randrange(w), y0 + rnd.randrange(h), 1, 1, sh(c, 0.93))
    return f


def room(d, x, y, w, h, floor, wall, wh=14, cap=(242, 238, 230)):
    R(d, x, y, w, h, OUT)
    R(d, x + 1, y + 1, w - 2, h - 2, cap)
    R(d, x + 3, y + 3, w - 6, h - 6, OUT)
    ix, iy, iw, ih = x + 4, y + 4, w - 8, h - 8
    floor(d, ix, iy, iw, ih)
    if wh:
        R(d, ix, iy, iw, wh, wall)
        R(d, ix, iy, iw, 1, sh(wall, 1.08))
        R(d, ix, iy + wh - 3, iw, 2, sh(wall, 0.8))
        R(d, ix, iy + wh - 1, iw, 1, OUT)
    return ix, iy, iw, ih


def gap(d, x, y, w, h, col):
    R(d, x - 1, y, w + 2, h, OUT)
    R(d, x, y, w, h, col)


# ---------- furniture ----------
WOOD_T, WOOD_F = (204, 156, 106), (168, 120, 78)


def desk(d, x, y, w=28, screen=(150, 214, 196)):
    block(d, x, y + 8, w, 14, WOOD_T, WOOD_F, 6)
    R(d, x + 4, y + 18, 4, 1, sh(WOOD_F, 1.25))
    R(d, x + w - 8, y + 18, 4, 1, sh(WOOD_F, 1.25))
    mx = x + w // 2 - 7
    box(d, mx, y, 14, 10, (74, 72, 90))
    R(d, mx + 2, y + 2, 10, 6, screen)
    R(d, mx + 3, y + 3, 5, 1, sh(screen, 1.15))
    R(d, mx + 3, y + 5, 7, 1, sh(screen, 0.8))
    R(d, mx + 5, y + 10, 4, 2, (74, 72, 90))
    R(d, x + 3, y + 10, 4, 3, (246, 242, 234))  # paper


def bookshelf(d, x, y, w=30, h=28, seed=1):
    rnd = random.Random(seed)
    cols = [(196, 120, 110), (120, 150, 190), (150, 180, 130), (224, 196, 120), (170, 140, 190), (230, 222, 206)]
    box(d, x, y, w, h, (150, 106, 72))
    R(d, x + 1, y + 1, w - 2, 4, (196, 148, 102))
    for ry in (y + 6, y + 17):
        R(d, x + 2, ry, w - 4, 9, (92, 64, 50))
        bx = x + 3
        while bx < x + w - 4:
            hh = rnd.choice([6, 7, 7, 8])
            if rnd.random() < 0.88:
                R(d, bx, ry + 9 - hh, 2, hh, rnd.choice(cols))
            bx += 3
    R(d, x + 1, y + h - 2, w - 2, 1, (120, 84, 58))


def plant(d, x, y):
    box(d, x + 2, y + 9, 8, 7, (204, 136, 104))
    R(d, x + 3, y + 13, 6, 2, (176, 110, 84))
    d.ellipse([x, y, x + 11, y + 10], fill=(116, 170, 122), outline=OUT)
    d.ellipse([x + 2, y + 2, x + 6, y + 5], fill=(150, 196, 146))
    R(d, x + 7, y + 6, 2, 1, (92, 142, 104))


def rug(d, x, y, w, h, c):
    box(d, x, y, w, h, c, sh(c, 0.72))
    d.rectangle([x + 2, y + 2, x + w - 3, y + h - 3], outline=sh(c, 1.1))


def sofa(d, x, y, w=44, c=(150, 186, 214)):
    box(d, x, y, w, 20, sh(c, 0.86))
    R(d, x + 1, y + 1, w - 2, 6, c)
    R(d, x + 1, y + 1, w - 2, 1, sh(c, 1.12))
    box(d, x + 4, y + 7, w - 8, 10, sh(c, 1.1))
    R(d, x + w // 2, y + 8, 1, 8, sh(c, 0.86))
    R(d, x + 1, y + 16, w - 2, 3, sh(c, 0.72))


def table(d, x, y, w, h):
    block(d, x, y, w, h, WOOD_T, WOOD_F, 5)


def chair(d, x, y, c=(226, 150, 130)):
    box(d, x, y, 8, 8, c)
    R(d, x + 1, y + 5, 6, 2, sh(c, 0.8))


def paper(d, x, y, c=(246, 242, 234)):
    R(d, x, y, 6, 5, c)
    R(d, x + 1, y + 1, 4, 1, sh(c, 0.8))
    R(d, x + 1, y + 3, 3, 1, sh(c, 0.8))


def board(d, x, y, w=40, h=13, seed=3):
    rnd = random.Random(seed)
    box(d, x, y, w, h, (212, 176, 126), (118, 82, 58))
    cols = [(248, 244, 236), (244, 224, 150), (236, 180, 176), (176, 212, 220)]
    bx = x + 3
    while bx < x + w - 6:
        R(d, bx, y + 2 + rnd.randrange(3), 5, 6, rnd.choice(cols))
        R(d, bx + 2, y + 2, 1, 1, (196, 90, 80))
        bx += 7


def whiteboard(d, x, y, w=40, h=13):
    box(d, x, y, w, h, (248, 246, 240), (130, 130, 146))
    for i, c in enumerate([(120, 150, 190), (196, 120, 110), (140, 180, 140)]):
        box(d, x + 4 + i * 11, y + 3, 7, 5, c, sh(c, 0.7))
        if i < 2:
            R(d, x + 11 + i * 11, y + 5, 4, 1, (90, 90, 104))


def window(d, x, y, w=20, h=10):
    box(d, x, y, w, h, (248, 244, 236))
    R(d, x + 2, y + 2, w - 4, h - 4, (176, 216, 232))
    R(d, x + w // 2, y + 2, 1, h - 4, (248, 244, 236))
    R(d, x + 4, y + 3, 2, 1, (226, 242, 248))
    R(d, x + 5, y + 4, 2, 1, (226, 242, 248))


def rack(d, x, y, seed=2):
    rnd = random.Random(seed)
    block(d, x, y, 14, 24, (126, 128, 148), (88, 90, 110), 16)
    for r in range(4):
        R(d, x + 2, y + 9 + r * 4, 10, 1, (64, 66, 84))
        R(d, x + 3 + rnd.randrange(3), y + 10 + r * 4, 1, 1, (140, 230, 160))
        R(d, x + 8 + rnd.randrange(3), y + 10 + r * 4, 1, 1, (240, 200, 110))


def counter(d, x, y, w):
    block(d, x, y, w, 14, (244, 240, 232), (200, 200, 210), 6)
    box(d, x + 3, y - 7, 9, 10, (92, 90, 108))
    R(d, x + 5, y - 5, 5, 3, (150, 150, 168))
    R(d, x + 9, y, 1, 1, (232, 120, 110))
    box(d, x + 16, y - 1, 5, 5, (236, 180, 176))
    box(d, x + 23, y - 1, 5, 5, (176, 212, 220))


def chest(d, x, y, c=(194, 134, 84)):
    box(d, x, y, 14, 11, c)
    R(d, x + 1, y + 1, 12, 4, sh(c, 1.15))
    R(d, x + 1, y + 5, 12, 1, OUT)
    R(d, x + 6, y + 4, 2, 3, (242, 210, 112))


def crate(d, x, y):
    box(d, x, y, 12, 12, (214, 176, 128))
    R(d, x + 1, y + 1, 10, 3, (232, 198, 150))
    R(d, x + 1, y + 4, 10, 1, (150, 110, 74))
    R(d, x + 5, y + 5, 2, 6, (176, 136, 94))


def bottles(d, x, y):
    for i, c in enumerate([(232, 150, 150), (150, 200, 220), (170, 210, 150), (230, 206, 130)]):
        box(d, x + i * 6, y, 5, 7, c)
        R(d, x + i * 6 + 1, y - 2, 3, 2, OUT)


# ---------- characters ----------
FRONT = [
    "....OOOO....",
    "...OHHHHO...",
    "..OHHHHHHO..",
    "..OHHHHHHO..",
    "..OHSSSSHO..",
    "..OSeSSeSO..",
    "..OSSSSSSO..",
    "...OSSSSO...",
    "..OCCCCCCO..",
    ".OCCCCCCCCO.",
    ".OSCCCCCCSO.",
    ".OSCCCCCCSO.",
    "..OCCCCCCO..",
    "..OPPOOPPO..",
    "..OPPOOPPO..",
    "..OOO..OOO..",
]
BACK = FRONT[:4] + ["..OHHHHHHO..", "..OHHHHHHO..", "..OHHHHHHO..", "...OHHHHO..."] + FRONT[8:]


def char(d, x, y, hair, shirt, skin=(244, 208, 174), pants=(96, 98, 126), back=False):
    pal = {"O": OUT, "H": hair, "S": skin, "e": OUT, "C": shirt, "P": pants}
    for j, row in enumerate(BACK if back else FRONT):
        for i, ch in enumerate(row):
            if ch != ".":
                R(d, x + i, y + j, 1, 1, pal[ch])
    if not back:
        R(d, x + 3, y + 9, 6, 1, sh(shirt, 1.12))


def bubble(d, x, y, kind):
    box(d, x, y, 11, 8, (252, 250, 244))
    R(d, x + 4, y + 8, 2, 1, OUT)
    R(d, x + 4, y + 7, 2, 1, (252, 250, 244))
    if kind == "dots":
        for i in range(3):
            R(d, x + 2 + i * 3, y + 3, 1, 2, (92, 86, 100))
    elif kind == "bang":
        R(d, x + 5, y + 1, 1, 4, (220, 104, 92))
        R(d, x + 5, y + 6, 1, 1, (220, 104, 92))
    elif kind == "ok":
        for px, py in [(2, 4), (3, 5), (4, 6), (5, 5), (6, 4), (7, 3), (8, 2)]:
            R(d, x + px, y + py - 1, 1, 1, (86, 160, 110))
    elif kind == "z":
        R(d, x + 3, y + 2, 5, 1, (120, 130, 170))
        R(d, x + 6, y + 3, 1, 1, (120, 130, 170))
        R(d, x + 5, y + 4, 1, 1, (120, 130, 170))
        R(d, x + 3, y + 5, 5, 1, (120, 130, 170))


ROLE = {
    "lead": ((92, 70, 60), (236, 200, 116)),
    "arch": ((210, 190, 150), (180, 164, 216)),
    "b1": ((70, 62, 76), (132, 172, 216)),
    "b2": ((176, 110, 80), (132, 172, 216)),
    "scout": ((230, 150, 110), (144, 198, 152)),
    "rev": ((60, 80, 110), (234, 152, 132)),
    "you": ((52, 44, 60), (92, 170, 170)),
}


def agent(d, x, y, role, back=False, bub=None, skin=(244, 208, 174)):
    hair, shirt = ROLE[role]
    char(d, x, y, hair, shirt, skin=skin, back=back)
    if bub:
        bubble(d, x + 1, y - 10, bub)


# ---------- scene A: the flat ----------
def scene_a():
    im = Image.new("RGB", (W, H), OUT)
    d = ImageDraw.Draw(im)
    room(d, 0, 0, W, H, wood, (172, 206, 216), wh=22)
    window(d, 16, 9)
    window(d, 204, 9, 16, 10)
    board(d, 140, 8, 46, 14)
    sofa(d, 10, 24)
    rug(d, 10, 50, 58, 34, (226, 198, 202))
    table(d, 26, 58, 24, 13)
    box(d, 30, 60, 5, 5, (176, 212, 220))
    plant(d, 56, 16)
    desk(d, 76, 20)
    desk(d, 108, 20, screen=(170, 200, 232))
    desk(d, 196, 20, screen=(236, 214, 150))
    bookshelf(d, 242, 12, seed=4)
    bookshelf(d, 276, 12, seed=9)
    # planning table
    rug(d, 108, 84, 104, 62, (196, 214, 226))
    for cx in (130, 156, 182):
        chair(d, cx, 90)
    table(d, 122, 98, 76, 30)
    paper(d, 130, 103)
    paper(d, 142, 108, (244, 224, 150))
    paper(d, 170, 104)
    box(d, 184, 110, 5, 5, (236, 180, 176))
    for cx in (130, 182):
        chair(d, cx, 130, (150, 186, 214))
    # review nook
    rug(d, 228, 138, 82, 72, (192, 222, 198))
    desk(d, 240, 144, screen=(236, 170, 150))
    chest(d, 288, 152)
    chest(d, 288, 168, (170, 150, 190))
    plant(d, 232, 190)
    # utility corner
    counter(d, 12, 176, 40)
    rack(d, 60, 164)
    rack(d, 76, 164, seed=5)
    plant(d, 300, 52)
    # door
    rug(d, 144, 200, 32, 14, (220, 178, 138))
    gap(d, 150, 220, 20, 4, (220, 178, 138))
    # agents
    agent(d, 84, 42, "b1", back=True, bub="dots")
    agent(d, 116, 42, "b2", back=True, bub="dots", skin=(206, 160, 122))
    agent(d, 252, 40, "scout", back=True, bub="dots")
    agent(d, 154, 82, "arch", bub="dots", skin=(206, 160, 122))
    agent(d, 248, 166, "rev", back=True, bub="bang")
    agent(d, 26, 30, "lead", bub="z")
    agent(d, 154, 180, "you")
    return im


# ---------- scene B: the guild hall ----------
def scene_b():
    im = Image.new("RGB", (W, H), OUT)
    d = ImageDraw.Draw(im)
    runner = (214, 176, 168)
    room(d, 0, 0, W, H, carpet((226, 214, 196)), None, wh=0)
    rug(d, 8, 100, 304, 22, runner)
    wood(d, 108, 130, 104, 90, (222, 190, 140))
    # top rooms
    room(d, 0, 0, 108, 98, wood, (236, 204, 182))
    room(d, 104, 0, 112, 98, wood, (172, 206, 216))
    room(d, 212, 0, 108, 98, carpet((196, 214, 196)), (206, 198, 226))
    # bottom rooms
    room(d, 0, 126, 108, 98, checker((226, 238, 230), (206, 226, 214)), (186, 222, 202))
    room(d, 212, 126, 108, 98, checker((228, 226, 232), (212, 210, 220)), (238, 222, 174))
    # doors
    gap(d, 44, 94, 18, 4, (216, 180, 128))
    gap(d, 152, 94, 18, 4, (216, 180, 128))
    gap(d, 258, 94, 18, 4, (196, 214, 196))
    gap(d, 44, 126, 18, 18, (216, 228, 220))
    gap(d, 258, 126, 18, 18, (220, 218, 226))
    rug(d, 144, 202, 32, 14, (220, 178, 138))
    gap(d, 150, 220, 20, 4, (220, 178, 138))
    # study
    whiteboard(d, 14, 6)
    bookshelf(d, 68, 8, 30, 28, seed=6)
    agent(d, 30, 26, "arch", bub="dots", skin=(206, 160, 122))
    table(d, 14, 40, 46, 20)
    paper(d, 20, 43)
    paper(d, 32, 45, (244, 224, 150))
    paper(d, 46, 43)
    plant(d, 8, 74)
    rug(d, 62, 62, 34, 24, (226, 198, 202))
    # workshop
    window(d, 150, 6, 20, 9)
    desk(d, 112, 18)
    desk(d, 146, 18, screen=(170, 200, 232))
    desk(d, 180, 18, screen=(92, 90, 108))
    agent(d, 120, 40, "b1", back=True, bub="dots")
    agent(d, 154, 40, "b2", back=True, bub="dots", skin=(206, 160, 122))
    crate(d, 112, 76)
    crate(d, 126, 78)
    rack(d, 194, 60)
    # library
    bookshelf(d, 218, 8, 30, 28, seed=11)
    bookshelf(d, 250, 8, 30, 28, seed=12)
    bookshelf(d, 282, 8, 30, 28, seed=13)
    agent(d, 258, 36, "scout", back=True, bub="ok")
    table(d, 234, 62, 44, 18)
    paper(d, 240, 65)
    paper(d, 262, 66)
    chair(d, 286, 66, (150, 186, 214))
    plant(d, 300, 76)
    # lab
    desk(d, 68, 142, screen=(236, 170, 150))
    agent(d, 76, 164, "rev", back=True, bub="bang")
    table(d, 12, 176, 46, 18)
    bottles(d, 17, 172)
    whiteboard(d, 10, 132, 28, 11)
    plant(d, 90, 200)
    # hall
    board(d, 112, 134, 34, 13, seed=8)
    agent(d, 170, 138, "lead", bub="z")
    counter(d, 150, 152, 54)
    plant(d, 114, 196)
    plant(d, 194, 196)
    # vault
    rack(d, 220, 140)
    rack(d, 236, 140, seed=7)
    chest(d, 290, 148)
    chest(d, 290, 164, (170, 150, 190))
    chest(d, 274, 148, (150, 186, 170))
    crate(d, 220, 200)
    crate(d, 234, 202)
    crate(d, 226, 190)
    # you
    agent(d, 154, 102, "you")
    return im


# ---------- scene C: the village ----------
def tree(d, x, y):
    box(d, x + 6, y + 13, 5, 8, (150, 106, 72))
    d.ellipse([x, y, x + 16, y + 16], fill=(112, 166, 122), outline=OUT)
    d.ellipse([x + 3, y + 2, x + 10, y + 8], fill=(142, 190, 142))
    R(d, x + 10, y + 11, 2, 1, (88, 138, 104))
    R(d, x + 5, y + 12, 2, 1, (88, 138, 104))


def cottage(d, x, y, w, roof, wall=(244, 234, 214), sign=None, rh=20):
    box(d, x + w - 14, y - 4, 7, 9, (198, 178, 168))
    box(d, x, y, w, rh, roof)
    R(d, x + 1, y + 1, w - 2, 2, sh(roof, 1.1))
    for yy in range(y + 6, y + rh - 2, 5):
        R(d, x + 1, yy, w - 2, 1, sh(roof, 0.86))
        for xx in range(x + 4 + (yy % 2) * 4, x + w - 2, 8):
            R(d, xx, yy + 1, 1, 3, sh(roof, 0.86))
    R(d, x + 1, y + rh - 2, w - 2, 1, sh(roof, 0.72))
    box(d, x + 2, y + rh - 1, w - 4, 18, wall)
    R(d, x + 3, y + rh, w - 6, 2, sh(wall, 0.86))
    R(d, x + 3, y + rh + 14, w - 6, 2, sh(wall, 0.82))
    cx = x + w // 2
    box(d, cx - 4, y + rh + 4, 9, 13, (156, 110, 76))
    R(d, cx + 2, y + rh + 10, 1, 1, (242, 210, 112))
    box(d, x + 7, y + rh + 4, 9, 8, (176, 216, 232))
    R(d, x + 11, y + rh + 5, 1, 6, wall)
    box(d, x + w - 16, y + rh + 4, 9, 8, (176, 216, 232))
    R(d, x + w - 12, y + rh + 5, 1, 6, wall)
    if sign:
        box(d, cx - 5, y + rh - 5, 11, 7, sign)


def sand(d, x, y, w, h, c=(230, 212, 170)):
    R(d, x, y, w, h, c)
    rnd = random.Random(x * 31 + y)
    for _ in range(w * h // 30):
        R(d, x + rnd.randrange(w), y + rnd.randrange(h), 1, 1, sh(c, 0.9))


def scene_c():
    im = Image.new("RGB", (W, H), (170, 208, 162))
    d = ImageDraw.Draw(im)
    rnd = random.Random(21)
    for _ in range(260):
        x, y = rnd.randrange(W), rnd.randrange(H)
        R(d, x, y, 2, 1, (146, 190, 144))
        R(d, x + 1, y - 1, 1, 1, (146, 190, 144))
    for _ in range(40):
        x, y = rnd.randrange(W), rnd.randrange(H)
        R(d, x, y, 2, 2, rnd.choice([(244, 214, 220), (248, 236, 170), (250, 248, 240)]))
    # paths
    sand(d, 0, 104, W, 20)
    sand(d, 150, 44, 20, 180)
    sand(d, 118, 84, 84, 60)
    sand(d, 46, 61, 9, 43)
    sand(d, 266, 61, 9, 43)
    sand(d, 46, 177, 9, 23)
    sand(d, 46, 192, 104, 9)
    sand(d, 266, 177, 9, 23)
    sand(d, 170, 192, 105, 9)
    # pond
    d.ellipse([84, 64, 114, 82], fill=(170, 210, 226), outline=(120, 164, 190))
    R(d, 92, 70, 6, 1, (214, 236, 242))
    R(d, 100, 75, 5, 1, (214, 236, 242))
    # buildings
    cottage(d, 122, 6, 76, (154, 192, 164), sign=(236, 200, 116), rh=22)
    cottage(d, 20, 24, 60, (224, 168, 168), sign=(132, 172, 216))
    cottage(d, 240, 24, 60, (156, 188, 216), sign=(144, 198, 152))
    cottage(d, 20, 140, 60, (234, 212, 150), sign=(234, 152, 132))
    # plot under construction
    box(d, 240, 146, 60, 32, (214, 190, 150), (150, 116, 84))
    for px in (242, 262, 282, 294):
        box(d, px, 136, 4, 40, (204, 160, 110))
    box(d, 240, 140, 60, 4, (204, 160, 110))
    box(d, 240, 156, 60, 4, (204, 160, 110))
    crate(d, 250, 164)
    crate(d, 268, 166)
    # plaza
    board(d, 124, 88, 26, 12, seed=5)
    box(d, 128, 100, 3, 6, (118, 82, 58))
    box(d, 143, 100, 3, 6, (118, 82, 58))
    d.ellipse([176, 100, 196, 116], fill=(206, 204, 212), outline=OUT)
    d.ellipse([180, 103, 192, 113], fill=(170, 210, 226), outline=(120, 124, 140))
    # trees
    for tx, ty in [(2, 72), (96, 28), (206, 44), (302, 80), (98, 150), (206, 150), (2, 200), (300, 198), (112, 200), (0, 2), (84, 0), (304, 0), (220, 2)]:
        tree(d, tx, ty)
    # agents
    agent(d, 132, 106, "lead", bub="z")
    agent(d, 44, 64, "b1", back=True, bub="dots")
    agent(d, 92, 106, "b2", bub="dots", skin=(206, 160, 122))
    agent(d, 216, 108, "scout", bub="ok")
    agent(d, 264, 180, "arch", back=True, bub="dots", skin=(206, 160, 122))
    agent(d, 60, 180, "rev", bub="bang")
    agent(d, 154, 130, "you")
    return im


if __name__ == "__main__":
    out = sys.argv[1]
    for name, fn in (("a", scene_a), ("b", scene_b), ("c", scene_c)):
        im = fn()
        im.resize((W * 3, H * 3), Image.NEAREST).save(f"{out}/scene_{name}.png")
    sheet = Image.new("RGB", (W * 2 * 3 + 40, H * 2 + 10), (40, 40, 40))
    for i, fn in enumerate((scene_a, scene_b, scene_c)):
        sheet.paste(fn().resize((W * 2, H * 2), Image.NEAREST), (i * (W * 2 + 20), 5))
    sheet.save(f"{out}/sheet.png")
