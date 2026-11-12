import random, sys
from PIL import Image, ImageDraw, ImageChops
from scenes import R, box, block, sh, OUT, WOOD_T, WOOD_F, bubble, plant, crate, paper
from night import person, cat

W, H = 424, 264
CREAM = (250, 240, 214)
AMBER = (252, 214, 124)
RED = (224, 74, 64)
lights, late = [], []

F = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "G": "01110 10001 10000 10111 10001 10001 01110",
    "H": "10001 10001 10001 11111 10001 10001 10001", "I": "11111 00100 00100 00100 00100 00100 11111",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "R": "11110 10001 10001 11110 10100 10010 10001", "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100", "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100", "W": "10001 10001 10001 10101 10101 11011 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "1": "00100 01100 00100 00100 00100 00100 01110", "2": "01110 10001 00001 00010 00100 01000 11111",
}


def text(d, x, y, s, c):
    for ch in s:
        if ch != " ":
            for j, row in enumerate(F[ch].split()):
                for i, b in enumerate(row):
                    if b == "1":
                        R(d, x + i, y + j, 1, 1, c)
        x += 6


def sign(x, y, w, name, bg, fg):
    tw = len(name) * 6 - 1
    sx = x + (w - tw - 8) // 2

    def f(d):
        box(d, sx, y, tw + 8, 11, bg)
        R(d, sx + 1, y + 1, tw + 6, 1, sh(bg, 1.12))
        text(d, sx + 4, y + 2, name, fg)
    late.append(f)
    lights.append((x + w // 2, y + 10, 20))


def rlantern(x, y, glow=12):
    def f(d):
        R(d, x + 1, y - 1, 3, 1, (240, 200, 110))
        box(d, x - 1, y, 7, 7, RED)
        R(d, x, y + 1, 5, 1, (244, 120, 100))
        R(d, x + 2, y + 1, 1, 5, (190, 50, 50))
        R(d, x + 1, y + 7, 3, 1, (240, 200, 110))
    late.append(f)
    if glow:
        lights.append((x + 2, y + 8, glow))


def string(d, y0, xs, sag, kind, every):
    cols = [AMBER, (250, 150, 150), (140, 226, 210), (250, 240, 200)]
    n = 0
    for a, b in zip(xs, xs[1:]):
        for x in range(a, b):
            t = (x - a) / (b - a)
            y = int(y0 + sag * 4 * t * (1 - t))
            late.append(lambda d, x=x, y=y: R(d, x, y, 1, 1, (54, 44, 62)))
            if (x - a) % every == every // 2:
                if kind == "lantern":
                    rlantern(x - 2, y + 2)
                else:
                    c = cols[n % 4]
                    n += 1
                    late.append(lambda d, x=x, y=y, c=c: (R(d, x - 1, y + 1, 3, 3, OUT), R(d, x, y + 1, 1, 2, c), R(d, x - 1, y + 2, 3, 1, c)))
                    lights.append((x, y + 6, 9))


def ground(d):
    base = (150, 146, 158)
    R(d, 0, 0, W, H, base)
    rnd = random.Random(2)
    for _ in range(2600):
        x, y = rnd.randrange(W), rnd.randrange(H)
        R(d, x, y, rnd.choice([1, 2]), 1, sh(base, rnd.choice([0.92, 0.95, 1.05])))
    for x in range(22, W, 44):  # parking-lot bay lines
        R(d, x, 214, 1, 22, (206, 204, 210))
    for cx, cy, rw, rh in [(150, 222, 26, 7), (300, 128, 20, 6), (66, 130, 16, 5)]:
        d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(128, 150, 190))
        R(d, cx - rw // 2, cy - 1, rw // 2, 1, (176, 196, 226))
    box(d, 252, 216, 10, 8, (110, 108, 122))
    for i in range(3):
        R(d, 254, 218 + i * 2, 6, 1, (70, 68, 82))
    # road
    R(d, 0, 240, W, 24, (120, 116, 132))
    box(d, -1, 236, W + 2, 5, (196, 192, 200))
    for x in range(6, W, 26):
        R(d, x, 252, 12, 2, (226, 198, 110))


def facades(d):
    rnd = random.Random(8)
    walls = [(196, 214, 200), (232, 206, 184), (236, 226, 196), (190, 206, 224), (224, 196, 200)]
    x = 0
    while x < W:
        bw = rnd.choice([44, 52, 60])
        c = rnd.choice(walls)
        box(d, x, -1, bw + 1, 46, c)
        for sy in range(4, 24, 5):
            R(d, x + 1, sy, bw - 1, 1, sh(c, 0.93))
        R(d, x + 1, 24, bw - 1, 2, sh(c, 0.74))
        for wx in range(x + 6, x + bw - 12, 16):
            lit = rnd.random() < 0.55
            box(d, wx, 6, 10, 12, (96, 104, 140))
            R(d, wx + 5, 7, 1, 10, sh(c, 0.8))
            if lit:
                late.append(lambda d, wx=wx: (R(d, wx + 1, 7, 4, 10, AMBER), R(d, wx + 6, 7, 3, 10, AMBER), R(d, wx + 1, 12, 8, 1, (190, 140, 80))))
                lights.append((wx + 5, 16, 10))
        box(d, x + bw - 12, 14, 9, 7, (214, 216, 222))  # AC unit
        R(d, x + bw - 10, 16, 5, 3, (130, 136, 150))
        if rnd.random() < 0.5:  # roll shutter
            box(d, x + 4, 27, bw - 7, 19, (170, 176, 188))
            for sy in range(29, 45, 3):
                R(d, x + 5, sy, bw - 9, 1, (136, 142, 158))
        else:  # open shop, lit
            box(d, x + 4, 27, bw - 7, 19, (236, 200, 150))
            for k in range(3):
                box(d, x + 8 + k * 12, 31 + (k % 2) * 3, 8, 6, rnd.choice([(214, 110, 100), (120, 170, 150), (236, 220, 170)]))
            box(d, x + 4, 26, bw - 7, 5, rnd.choice([(204, 80, 72), (70, 140, 130), (232, 180, 80)]))
            lights.append((x + bw // 2, 44, 26))
        vc = rnd.choice([(226, 70, 66), (250, 214, 110), (90, 190, 170), (250, 240, 214)])
        vx = x + bw - 4
        late.append(lambda d, vx=vx, vc=vc: (box(d, vx, 2, 8, 24, vc), [R(d, vx + 2, 5 + k * 5, 4, 3, sh(vc, 0.55)) for k in range(4)]))
        lights.append((vx + 4, 22, 12))
        x += bw
    for y0, sag in ((3, 5), (7, 7)):
        for a, b in ((0, 150), (150, 290), (290, W)):
            for xx in range(a, b):
                t = (xx - a) / (b - a)
                late.append(lambda d, xx=xx, yy=int(y0 + sag * 4 * t * (1 - t)): R(d, xx, yy, 1, 1, (40, 34, 50)))


def gate(d, x=166, w=92, title="NIGHT MARKET"):
    stone, red, tile = (190, 186, 196), (204, 72, 64), (232, 140, 86)
    for px in (x, x + w - 9):
        box(d, px - 1, 50, 11, 6, stone)
        box(d, px, 18, 9, 34, red)
        R(d, px + 1, 19, 2, 32, (232, 110, 96))
        R(d, px + 1, 30, 7, 2, (240, 200, 110))
    box(d, x - 4, 14, w + 8, 9, red)
    R(d, x - 3, 15, w + 6, 1, (232, 110, 96))
    for k in range(x, x + w - 2, 8):
        box(d, k, 21, 5, 4, (70, 150, 130))
    box(d, x - 12, 3, w + 24, 12, tile)
    R(d, x - 11, 4, w + 22, 2, (250, 176, 110))
    for k in range(x - 10, x + w + 10, 5):
        R(d, k, 6, 1, 8, sh(tile, 0.8))
    R(d, x - 11, 12, w + 22, 2, (70, 150, 130))
    box(d, x - 16, 0, 7, 7, tile)
    box(d, x + w + 9, 0, 7, 7, tile)
    box(d, x + 6, -1, w - 12, 5, (70, 150, 130))
    R(d, x + 7, 0, w - 14, 1, (130, 200, 170))
    box(d, x + w // 2 - 4, -2, 8, 5, (240, 200, 110))
    cx = x + w // 2

    def plaque(d):
        box(d, cx - 40, 13, 80, 12, (64, 36, 44), (240, 200, 110))
        if title:
            text(d, cx - len(title) * 3, 16, title, (250, 214, 124))
    late.append(plaque)
    for k in range(5):
        rlantern(x + 16 + k * 14, 28, glow=13)
    lights.append((cx, 46, 34))


TARPS = {
    "rwb": [(214, 84, 76), (246, 240, 232), (76, 116, 196), (246, 240, 232)],
    "yg": [(244, 204, 96), (84, 164, 124)],
    "pw": [(238, 142, 164), (250, 240, 236)],
    "tw": [(72, 172, 172), (250, 244, 230)],
    "ow": [(244, 154, 74), (252, 240, 214)],
    "gold": [(244, 204, 96), (204, 72, 64)],
    "nb": [(70, 92, 168), (250, 244, 230)],
}


def awning(d, x, y, w, cols):
    R(d, x - 3, y, w + 6, 13, OUT)
    for i, sx in enumerate(range(x - 2, x + w + 2, 4)):
        c = cols[i % len(cols)]
        ww = min(4, x + w + 2 - sx)
        R(d, sx, y + 1, ww, 11, c)
        R(d, sx, y + 1, ww, 1, sh(c, 1.1))
        R(d, sx, y + 9, ww, 3, sh(c, 0.84))
    for i, sx in enumerate(range(x - 3, x + w + 1, 6)):
        box(d, sx, y + 12, 7, 4, cols[(i * 2) % len(cols)] if len(cols) > 2 else cols[i % 2])


def stall(d, x, y, name, tarp, who, goods, w=64, signc=(CREAM, (196, 52, 52)), lit=46, panel=(214, 84, 76)):
    R(d, x + 2, y + 22, w - 4, 20, (98, 78, 88))
    R(d, x + 4, y + 30, w - 8, 1, (140, 110, 100))
    rnd = random.Random(x)
    for bx in range(x + 6, x + w - 8, 5):
        if abs(bx - (x + w // 2)) > 9:
            R(d, bx, y + 25, 3, 5, rnd.choice([(150, 200, 170), (240, 200, 120), (230, 140, 130), (170, 190, 230)]))
    box(d, x + 1, y + 22, 3, 32, (120, 124, 140))
    box(d, x + w - 4, y + 22, 3, 32, (120, 124, 140))
    awning(d, x, y + 11, w, TARPS[tarp])
    if who:
        who(d, x + w // 2 - 6, y + 27)
    block(d, x, y + 40, w, 15, (218, 224, 232), (156, 166, 182), 8)
    R(d, x + 3, y + 48, w - 6, 5, panel)
    box(d, x + 6, y + 47, 14, 7, CREAM)
    R(d, x + 8, y + 49, 8, 1, (190, 90, 80))
    R(d, x + 8, y + 51, 6, 1, (120, 130, 150))
    box(d, x + 5, y + 54, 6, 5, (70, 64, 78))
    box(d, x + w - 11, y + 54, 6, 5, (70, 64, 78))
    goods(d, x + 4, y + 34)
    if name:
        sign(x, y, w, name, *signc)
    if lit > 30:
        for k in (10, w - 15):
            rlantern(x + k, y + 28, glow=0)
    lights.append((x + w // 2, y + 44, lit))


def steam(x, y):
    late.append(lambda d: [R(d, x + px, y + py, 1, 1, (232, 234, 244)) for px, py in [(0, 0), (1, -2), (3, -1), (2, -4), (4, -5), (1, -7), (5, -8), (3, -10)]])


def g_wok(d, x, y):
    d.ellipse([x, y + 1, x + 15, y + 8], fill=(66, 64, 78), outline=OUT)
    R(d, x + 4, y + 3, 3, 2, (240, 170, 80))
    R(d, x + 8, y + 4, 3, 2, (130, 190, 120))
    R(d, x + 6, y + 2, 2, 1, (230, 110, 90))
    R(d, x + 15, y + 4, 5, 1, OUT)
    late.append(lambda d: (R(d, x + 2, y + 8, 2, 2, (250, 150, 60)), R(d, x + 6, y + 9, 3, 1, (250, 210, 90)), R(d, x + 11, y + 8, 2, 2, (250, 150, 60))))
    steam(x + 5, y - 2)
    for k in range(3):
        box(d, x + 26, y + 5 - k * 4, 13, 5, (220, 186, 126))
        R(d, x + 27, y + 7 - k * 4, 11, 1, (170, 130, 84))
    steam(x + 30, y - 8)
    box(d, x + 44, y + 1, 5, 8, (230, 120, 110))
    box(d, x + 50, y + 3, 5, 6, (240, 210, 120))


def g_plan(d, x, y):
    box(d, x, y - 4, 16, 13, (70, 110, 96))
    R(d, x + 2, y - 2, 10, 1, CREAM)
    R(d, x + 2, y + 1, 8, 1, CREAM)
    R(d, x + 2, y + 4, 11, 1, (240, 200, 120))
    paper(d, x + 20, y + 3)
    paper(d, x + 28, y + 2, (176, 206, 236))
    paper(d, x + 36, y + 4, (246, 226, 150))
    box(d, x + 47, y + 1, 6, 8, (120, 150, 200))
    R(d, x + 48, y - 2, 1, 3, (240, 200, 110))
    R(d, x + 51, y - 3, 1, 4, (230, 120, 110))


def g_review(d, x, y):
    for k, c in enumerate([(240, 170, 90), (200, 120, 90), (150, 190, 130)]):
        d.ellipse([x + k * 12, y + 2, x + k * 12 + 10, y + 9], fill=(246, 244, 240), outline=OUT)
        R(d, x + k * 12 + 3, y + 4, 5, 2, c)
    box(d, x + 38, y + 1, 9, 8, (176, 200, 214))
    R(d, x + 47, y + 3, 3, 1, OUT)
    R(d, x + 41, y - 1, 3, 2, OUT)
    steam(x + 40, y - 3)
    box(d, x + 50, y - 2, 6, 11, CREAM)
    for k, c in enumerate([(86, 160, 110), (86, 160, 110), (220, 104, 92)]):
        R(d, x + 51, y + k * 3, 2, 1, c)
        R(d, x + 54, y + k * 3, 1, 1, (150, 150, 160))


def g_orders(d, x, y):
    box(d, x, y + 1, 14, 9, (80, 78, 96))
    R(d, x + 2, y + 3, 8, 3, (150, 226, 190))
    box(d, x + 18, y + 4, 8, 5, (240, 200, 110))
    R(d, x + 21, y + 2, 2, 2, (240, 200, 110))
    R(d, x + 34, y - 2, 1, 11, OUT)
    paper(d, x + 31, y + 2)
    paper(d, x + 32, y + 5, (246, 226, 150))
    box(d, x + 44, y + 2, 10, 7, (214, 84, 76))
    R(d, x + 46, y + 4, 6, 1, CREAM)


def g_ship(d, x, y):
    for k, c in enumerate([(220, 184, 134), (204, 164, 122), (230, 196, 150)]):
        box(d, x + k * 13, y + 1, 12, 9, c)
        R(d, x + k * 13 + 5, y + 2, 2, 7, (200, 110, 100))
    box(d, x + 6, y - 6, 12, 8, (220, 184, 134))
    box(d, x + 42, y, 7, 10, (246, 240, 232))
    R(d, x + 44, y - 2, 3, 2, OUT)
    box(d, x + 50, y + 2, 7, 8, (250, 220, 190))
    R(d, x + 52, y, 3, 2, OUT)


def umbrella(d, cx, cy, r, c1, c2):
    for k in range(8):
        d.pieslice([cx - r, cy - r, cx + r, cy + r], k * 45, k * 45 + 45, fill=c1 if k % 2 else c2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=OUT)
    d.ellipse([cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3], outline=sh(c1, 0.8))
    box(d, cx - 1, cy - 1, 3, 3, (240, 200, 110))


def fruit_cart(d, x, y):
    box(d, x + 3, y + 22, 7, 7, (70, 64, 78))
    box(d, x + 27, y + 22, 7, 7, (70, 64, 78))
    block(d, x, y + 8, 38, 16, (218, 224, 232), (84, 164, 124), 8)
    for k, c in enumerate([(250, 200, 80), (240, 110, 140), (140, 200, 110), (250, 150, 70)]):
        box(d, x + 2 + k * 9, y + 9, 8, 6, (236, 240, 244))
        R(d, x + 3 + k * 9, y + 10, 3, 2, c)
        R(d, x + 6 + k * 9, y + 12, 3, 2, c)
    R(d, x + 4, y + 18, 16, 3, CREAM)
    R(d, x + 19, y - 8, 2, 16, (120, 124, 140))
    umbrella(d, x + 20, y - 6, 17, (238, 142, 164), (250, 244, 230))
    lights.append((x + 20, y + 14, 36))
    late.append(lambda d: (R(d, x + 34, y + 2, 3, 4, AMBER), R(d, x + 35, y, 1, 2, OUT)))


def scooter(d, x, y, c, boxc=None, lamp=False):
    d.ellipse([x, y + 7, x + 6, y + 13], fill=(56, 52, 64), outline=OUT)
    d.ellipse([x + 14, y + 7, x + 20, y + 13], fill=(56, 52, 64), outline=OUT)
    box(d, x + 3, y + 5, 14, 6, c)
    box(d, x + 1, y + 1, 5, 9, c)
    R(d, x + 2, y + 2, 1, 6, sh(c, 1.15))
    R(d, x - 1, y, 6, 1, OUT)
    box(d, x + 8, y + 2, 9, 4, (66, 60, 74))
    if boxc:
        box(d, x + 12, y - 5, 10, 8, boxc)
        R(d, x + 14, y - 3, 6, 1, CREAM)
    if lamp:
        late.append(lambda d: R(d, x, y + 3, 2, 2, (255, 244, 200)))
        lights.append((x - 8, y + 8, 16))


def table(d, x, y):
    block(d, x, y, 24, 13, (206, 212, 222), (150, 158, 174), 4)
    for sx, sy, c in [(-8, 2, RED), (25, 3, (70, 120, 200)), (3, -8, (70, 120, 200)), (14, 14, RED)]:
        box(d, x + sx, y + sy, 7, 7, c)
        R(d, x + sx + 2, y + sy + 2, 3, 2, sh(c, 1.25))
    d.ellipse([x + 3, y + 1, x + 10, y + 6], fill=(246, 244, 240), outline=OUT)
    R(d, x + 5, y + 3, 3, 1, (240, 170, 90))
    box(d, x + 15, y + 2, 4, 5, (236, 200, 170))
    lights.append((x + 12, y + 8, 24))


def gas(d, x, y, c=(226, 96, 84)):
    box(d, x, y + 2, 7, 10, c)
    R(d, x + 1, y + 3, 1, 8, sh(c, 1.2))
    box(d, x + 2, y, 3, 3, (120, 124, 140))


def dog(d, x, y, c=(206, 170, 120)):
    box(d, x, y + 3, 11, 6, c)
    box(d, x + 8, y, 6, 6, c)
    R(d, x + 8, y - 1, 2, 2, sh(c, 0.7))
    R(d, x + 12, y + 2, 1, 1, OUT)
    R(d, x - 2, y + 2, 3, 1, OUT)
    R(d, x + 1, y + 8, 2, 2, OUT)
    R(d, x + 8, y + 8, 2, 2, OUT)


def scene():
    day = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(day)
    ground(d)
    facades(d)
    gate(d)

    A = lambda **k: (lambda d, x, y: person(d, x, y, **k))
    arch = A(hair=(214, 196, 160), shirt=(180, 164, 216), skin=(206, 160, 122), acc=("bun", "glasses"))
    b1 = A(hair=(70, 62, 76), shirt=(132, 172, 216), acc=("beanie", "apron"))
    b2 = A(hair=(176, 110, 80), shirt=(244, 170, 110), skin=(206, 160, 122), acc=("band", "apron"))
    rev = A(hair=(60, 80, 110), shirt=(234, 152, 132), acc=("glasses", "apron"))
    lead = A(hair=(92, 70, 60), shirt=(236, 200, 116), acc=("straw",))

    stall(d, 14, 50, "PLAN", "tw", arch, g_plan, panel=(72, 172, 172))
    stall(d, 96, 50, "BUILD 1", "rwb", b1, g_wok)
    stall(d, 264, 50, "BUILD 2", "ow", b2, g_wok, panel=(244, 154, 74))
    stall(d, 346, 50, "REVIEW", "pw", rev, g_review, panel=(238, 142, 164))
    gas(d, 162, 96)
    gas(d, 254, 96, (120, 170, 200))
    plant(d, 82, 92)
    plant(d, 332, 92)

    string(d, 114, [0, 140, 284, W], 7, "lantern", 15)

    table(d, 58, 142)
    table(d, 116, 166)
    stall(d, 180, 128, "ORDERS", "gold", lead, g_orders, signc=((204, 60, 56), (252, 232, 170)), lit=56, panel=(244, 204, 96))
    late.append(lambda d: (R(d, 184, 163, 56, 1, (54, 44, 62)), [box(d, 188 + k * 9, 163, 6, 7, c) for k, c in enumerate([CREAM, (246, 226, 150), CREAM, (250, 190, 180)])]))
    stall(d, 330, 150, "SHIP", "yg", None, g_ship, lit=24, signc=((230, 226, 214), (90, 96, 120)), panel=(84, 164, 124))
    scooter(d, 300, 196, (90, 180, 150), boxc=(84, 164, 124))
    scooter(d, 398, 198, (230, 120, 110))
    crate(d, 316, 214)
    crate(d, 398, 176)

    fruit_cart(d, 24, 196)
    sign(22, 170, 44, "SCOUT", (252, 232, 150), (70, 110, 80))
    person(d, 70, 204, (232, 150, 110), (144, 198, 152), acc=("hood",))
    box(d, 78, 212, 7, 6, (250, 200, 80))

    dog(d, 258, 190)
    cat(d, 140, 204)
    plant(d, 164, 200)
    plant(d, 250, 150)
    for sx, sy, c in [(104, 206, RED), (214, 214, (70, 120, 200)), (286, 222, RED)]:
        box(d, sx, sy, 7, 7, c)
        R(d, sx + 2, sy + 2, 3, 2, sh(c, 1.25))

    string(d, 224, [0, 212, W], 5, "bulb", 10)
    scooter(d, 118, 243, (250, 200, 90), boxc=(214, 84, 76), lamp=True)
    scooter(d, 352, 222, (120, 150, 210))
    scooter(d, 376, 222, (236, 150, 170))

    person(d, 206, 190, (52, 44, 60), (92, 170, 170), back=True, acc=("tail",))

    night = ImageChops.multiply(day, Image.new("RGB", day.size, (180, 166, 216)))
    warm = ImageChops.multiply(day, Image.new("RGB", day.size, (255, 246, 226)))
    mask = Image.new("L", day.size, 0)
    for cx, cy, r in lights:
        for f, v in ((1.0, 70), (0.74, 138), (0.48, 204)):
            layer = Image.new("L", day.size, 0)
            rr = r * f
            ImageDraw.Draw(layer).ellipse([cx - rr, cy - rr * 0.84, cx + rr, cy + rr * 0.84], fill=v)
            mask = ImageChops.lighter(mask, layer)
    out = Image.composite(warm, night, mask)
    d = ImageDraw.Draw(out)
    for f in late:
        f(d)
    for bx, by, kind in [(41, 66, "dots"), (123, 66, "dots"), (291, 66, "dots"), (373, 66, "bang"), (207, 144, "z"), (71, 193, "ok")]:
        bubble(d, bx, by, kind)
    return out


if __name__ == "__main__":
    im = scene()
    im.resize((W * 3, H * 3), Image.NEAREST).save(sys.argv[1] + "/scene_d2.png")
