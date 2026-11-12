import random, sys
from PIL import Image, ImageDraw, ImageChops
from scenes import (R, box, block, sh, OUT, W, H, WOOD_T, WOOD_F, FRONT, BACK, bubble, plant, crate, paper, chest)

CREAM = (244, 236, 214)
AMBER = (250, 212, 124)
lights, late = [], []  # glow pools, things drawn after the night tint


def cobble(d):
    base = (150, 146, 164)
    R(d, 0, 0, W, H, base)
    rnd = random.Random(3)
    for row in range(0, H, 6):
        off = (row // 6 % 2) * 5
        for x in range(-off, W, 10):
            k = rnd.random()
            if k < 0.22:
                R(d, x, row, 9, 5, sh(base, 0.94))
            elif k < 0.4:
                R(d, x, row, 9, 5, sh(base, 1.05))
            R(d, x + 9, row, 1, 6, sh(base, 0.84))
        R(d, 0, row + 5, W, 1, sh(base, 0.84))


def facades(d):
    rnd = random.Random(11)
    x = 0
    cols = [(132, 122, 150), (150, 128, 140), (120, 132, 150), (140, 136, 128)]
    while x < W:
        bw = rnd.choice([36, 44, 52])
        c = rnd.choice(cols)
        box(d, x, 0, bw + 1, 25, c)
        R(d, x + 1, 1, bw - 1, 5, sh(c, 0.7))
        R(d, x + 1, 6, bw - 1, 1, sh(c, 0.55))
        for wx in range(x + 6, x + bw - 8, 11):
            lit = rnd.random() < 0.65
            late.append(lambda d, wx=wx, lit=lit: (
                box(d, wx, 11, 6, 8, AMBER if lit else (74, 80, 118)),
                R(d, wx + 3, 12, 1, 6, (120, 96, 70) if lit else (52, 56, 86))))
            if lit:
                lights.append((wx + 3, 20, 9))
        x += bw


def person(d, x, y, hair, shirt, skin=(244, 208, 174), back=False, acc=()):
    pal = {"O": OUT, "H": hair, "S": skin, "e": OUT, "C": shirt, "P": (96, 98, 126)}
    for j, row in enumerate(BACK if back else FRONT):
        for i, ch in enumerate(row):
            if ch != ".":
                R(d, x + i, y + j, 1, 1, pal[ch])
    for a in acc:
        if a == "straw":
            c = (236, 208, 140)
            R(d, x, y + 2, 12, 2, OUT)
            R(d, x + 1, y + 2, 10, 1, c)
            box(d, x + 3, y - 1, 6, 4, c)
            R(d, x + 4, y + 1, 4, 1, (200, 110, 100))
        elif a == "beanie":
            c = (224, 120, 110)
            R(d, x + 3, y + 1, 6, 1, c)
            R(d, x + 2, y + 2, 8, 2, c)
            R(d, x + 2, y + 3, 8, 1, sh(c, 0.8))
            box(d, x + 5, y - 2, 3, 3, CREAM)
        elif a == "bun":
            box(d, x + 4, y - 3, 4, 4, hair)
        elif a == "band":
            R(d, x + 2, y + 3, 8, 1, (120, 200, 190))
        elif a == "glasses" and not back:
            for gx in (3, 5, 6, 8):
                R(d, x + gx, y + 5, 1, 1, (210, 232, 244))
        elif a == "apron" and not back:
            R(d, x + 3, y + 9, 6, 4, CREAM)
            R(d, x + 4, y + 8, 4, 1, CREAM)
        elif a == "tail" and back:
            R(d, x + 5, y + 7, 2, 5, hair)
        elif a == "hood":
            R(d, x + 2, y + 2, 1, 5, shirt)
            R(d, x + 9, y + 2, 1, 5, shirt)
            R(d, x + 3, y + 1, 6, 1, shirt)


def lantern(x, y, c=AMBER, glow=0):
    def f(d):
        R(d, x + 1, y - 1, 3, 1, OUT)
        box(d, x, y, 5, 7, c)
        R(d, x + 1, y + 1, 1, 3, (255, 244, 210))
    late.append(f)
    if glow:
        lights.append((x + 2, y + 6, glow))


def stall(d, x, y, c1, who, goods, w=56, c2=CREAM, lit=40):
    R(d, x + 2, y + 10, w - 4, 20, (84, 70, 84))
    box(d, x + 1, y + 10, 3, 30, WOOD_F)
    box(d, x + w - 4, y + 10, 3, 30, WOOD_F)
    box(d, x - 2, y, w + 4, 13, c1)
    for sx in range(x + 3, x + w, 8):
        R(d, sx, y + 1, 4, 11, c2)
    R(d, x - 1, y + 1, w + 2, 1, sh(c1, 1.12))
    for i, sx in enumerate(range(x - 2, x + w + 2, 6)):
        box(d, sx, y + 11, 7, 5, c1 if i % 2 == 0 else c2)
    if who:
        who(d, x + w // 2 - 6, y + 15)
    block(d, x, y + 28, w, 14, WOOD_T, WOOD_F, 7)
    goods(d, x + 4, y + 23)
    lantern(x - 1, y + 16)
    lantern(x + w - 4, y + 16, (240, 150, 120))
    lights.append((x + w // 2, y + 30, lit))


def g_scrolls(d, x, y):
    for i, c in enumerate([(236, 240, 246), (170, 200, 232), (236, 240, 246)]):
        box(d, x + i * 9, y + 2, 8, 5, c)
        R(d, x + i * 9 + 1, y + 4, 6, 1, sh(c, 0.8))
    box(d, x + 34, y, 10, 8, (120, 150, 200))
    R(d, x + 36, y + 2, 6, 1, CREAM)
    R(d, x + 36, y + 4, 4, 1, CREAM)


def g_blocks(d, x, y):
    for i, c in enumerate([(232, 150, 130), (150, 200, 160), (236, 206, 130), (150, 180, 220)]):
        box(d, x + i * 7, y + 3, 7, 5, c)
    box(d, x + 4, y - 1, 7, 5, (150, 180, 220))
    box(d, x + 11, y - 1, 7, 5, (232, 150, 130))
    box(d, x + 36, y + 1, 9, 7, (110, 110, 130))
    R(d, x + 38, y + 3, 5, 3, (150, 220, 200))


def g_curios(d, x, y):
    for i, c in enumerate([(232, 190, 120), (170, 210, 150), (220, 160, 190)]):
        box(d, x + i * 7, y + 1, 6, 7, c)
        R(d, x + i * 7 + 1, y, 4, 1, OUT)
    box(d, x + 26, y + 2, 12, 6, (236, 224, 190))
    R(d, x + 28, y + 4, 3, 1, (200, 110, 100))
    R(d, x + 32, y + 5, 4, 1, (120, 150, 190))
    box(d, x + 41, y + 1, 5, 7, (150, 190, 220))


def g_checks(d, x, y):
    for i in range(3):
        box(d, x + i * 9, y + 1, 8, 7, (246, 242, 234))
        R(d, x + i * 9 + 2, y + 3, 1, 1, (86, 160, 110) if i < 2 else (220, 104, 92))
        R(d, x + i * 9 + 4, y + 3, 2, 1, (150, 150, 160))
        R(d, x + i * 9 + 2, y + 5, 4, 1, (150, 150, 160))
    box(d, x + 32, y, 3, 8, (190, 170, 120))
    box(d, x + 28, y + 1, 11, 2, (190, 170, 120))
    box(d, x + 27, y + 3, 4, 3, (236, 206, 130))
    box(d, x + 36, y + 3, 4, 3, (236, 206, 130))


def g_parcels(d, x, y):
    for i, c in enumerate([(214, 176, 128), (200, 160, 120), (224, 190, 146)]):
        box(d, x + i * 12, y + 1, 11, 7, c)
        R(d, x + i * 12 + 5, y + 2, 1, 5, (200, 110, 100))
    box(d, x + 38, y - 2, 9, 6, (214, 176, 128))


def table(d, x, y):
    block(d, x, y, 18, 13, WOOD_T, WOOD_F, 4)
    box(d, x - 8, y + 3, 7, 7, (224, 160, 150))
    box(d, x + 19, y + 3, 7, 7, (150, 190, 200))
    box(d, x + 3, y + 2, 4, 4, (236, 240, 246))
    box(d, x + 11, y + 4, 4, 4, (236, 240, 246))
    late.append(lambda d: (R(d, x + 8, y + 1, 2, 3, AMBER), R(d, x + 8, y, 2, 1, (255, 244, 210))))
    lights.append((x + 9, y + 6, 20))


def cart(d, x, y):
    box(d, x + 3, y + 17, 7, 7, (86, 76, 90))
    box(d, x + 21, y + 17, 7, 7, (86, 76, 90))
    block(d, x, y + 5, 31, 15, (226, 134, 116), (182, 100, 92), 7)
    box(d, x + 4, y, 11, 8, (160, 160, 178))
    box(d, x + 18, y + 2, 9, 6, (236, 206, 130))
    late.append(lambda d: [R(d, x + px, y + py, 1, 1, (222, 226, 240)) for px, py in
                           [(7, -3), (8, -5), (10, -4), (9, -8), (11, -7), (7, -10), (12, -11)]])
    lantern(x + 27, y - 4, glow=26)
    R(d, x + 29, y + 3, 1, 3, OUT)


def cat(d, x, y, c=(232, 160, 100)):
    R(d, x - 3, y + 3, 4, 1, OUT)
    box(d, x, y + 2, 9, 6, c)
    box(d, x + 6, y, 6, 6, c)
    R(d, x + 6, y - 1, 2, 1, OUT)
    R(d, x + 10, y - 1, 2, 1, OUT)
    R(d, x + 8, y + 2, 1, 1, OUT)
    R(d, x + 10, y + 2, 1, 1, OUT)
    R(d, x + 2, y + 4, 2, 1, sh(c, 0.8))


def string_lights(d, y0, xs, sag=7):
    cols = [AMBER, (244, 160, 140), (150, 220, 200)]
    n = 0
    for a, b in zip(xs, xs[1:]):
        for x in range(a, b):
            t = (x - a) / (b - a)
            y = int(y0 + sag * 4 * t * (1 - t))
            R(d, x, y, 1, 1, (60, 52, 70))
            if (x - a) % 9 == 4:
                c = cols[n % 3]
                n += 1
                late.append(lambda d, x=x, y=y, c=c: (R(d, x - 1, y + 1, 3, 3, OUT), R(d, x, y + 1, 1, 2, c), R(d, x - 1, y + 2, 3, 1, c)))
                lights.append((x, y + 6, 8))


def scene():
    day = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(day)
    cobble(d)
    facades(d)
    # canal
    R(d, 0, 207, W, 17, (96, 132, 176))
    box(d, -1, 204, W + 2, 5, (190, 186, 200))
    rnd = random.Random(5)
    for _ in range(40):
        R(d, rnd.randrange(W), 211 + rnd.randrange(12), 3 + rnd.randrange(4), 1, (120, 156, 196))
    box(d, 236, 212, 30, 9, WOOD_F)
    R(d, 238, 213, 26, 3, WOOD_T)
    lantern(262, 205, glow=16)
    for rx, rc in [(30, AMBER), (62, (244, 160, 140)), (128, AMBER), (176, (150, 220, 200)), (212, AMBER), (284, (244, 160, 140))]:
        late.append(lambda d, rx=rx, rc=rc: (R(d, rx, 213, 5, 1, rc), R(d, rx + 1, 216, 3, 1, rc), R(d, rx + 2, 219, 2, 1, rc)))

    string_lights(d, 74, [0, 104, 216, 320])

    A = lambda **k: (lambda d, x, y: person(d, x, y, **k))
    arch = A(hair=(214, 196, 160), shirt=(180, 164, 216), skin=(206, 160, 122), acc=("bun", "glasses"))
    b1 = A(hair=(70, 62, 76), shirt=(132, 172, 216), acc=("beanie",))
    b2 = A(hair=(176, 110, 80), shirt=(132, 172, 216), skin=(206, 160, 122), acc=("band", "apron"))
    scout = A(hair=(232, 150, 110), shirt=(144, 198, 152), acc=("hood",))
    rev = A(hair=(60, 80, 110), shirt=(234, 152, 132), acc=("glasses", "apron"))
    lead = A(hair=(92, 70, 60), shirt=(236, 200, 116), acc=("straw",))

    stall(d, 8, 30, (190, 172, 220), arch, g_scrolls)
    stall(d, 86, 30, (150, 184, 216), b1, g_blocks)
    stall(d, 178, 30, (226, 170, 170), b2, g_blocks)
    stall(d, 256, 30, (160, 200, 168), scout, g_curios)
    stall(d, 132, 86, (236, 204, 124), lead, lambda d, x, y: (paper(d, x + 2, y + 2), paper(d, x + 12, y + 3, (244, 224, 150)), box(d, x + 36, y, 8, 8, (200, 110, 100))), lit=48)
    stall(d, 20, 150, (232, 164, 144), rev, g_checks)
    stall(d, 244, 150, (170, 176, 210), None, g_parcels, lit=22)

    # lamp post between the top stalls
    box(d, 158, 44, 4, 28, (96, 92, 118))
    box(d, 155, 70, 10, 4, (96, 92, 118))
    late.append(lambda d: (box(d, 154, 34, 12, 11, AMBER), R(d, 156, 36, 2, 5, (255, 244, 210))))
    lights.append((160, 60, 30))

    table(d, 34, 104)
    table(d, 262, 104)
    cart(d, 104, 166)
    plant(d, 90, 148)
    plant(d, 224, 150)
    plant(d, 70, 52)
    plant(d, 240, 52)
    crate(d, 304, 178)
    crate(d, 306, 166)
    chest(d, 214, 186)
    cat(d, 196, 172)

    # couriers and you
    person(d, 154, 134, (52, 44, 60), (92, 170, 170), back=True, acc=("tail",))
    person(d, 204, 120, (150, 96, 70), (200, 190, 220), skin=(206, 160, 122), acc=("band",))
    box(d, 203, 128, 8, 7, (214, 176, 128))
    person(d, 96, 112, (60, 60, 70), (220, 190, 170), back=True)

    night = ImageChops.multiply(day, Image.new("RGB", day.size, (104, 106, 170)))
    warm = ImageChops.multiply(day, Image.new("RGB", day.size, (255, 240, 208)))
    mask = Image.new("L", day.size, 0)
    for cx, cy, r in lights:
        for f, v in ((1.0, 64), (0.72, 124), (0.44, 188)):
            layer = Image.new("L", day.size, 0)
            rr = r * f
            ImageDraw.Draw(layer).ellipse([cx - rr, cy - rr * 0.82, cx + rr, cy + rr * 0.82], fill=v)
            mask = ImageChops.lighter(mask, layer)
    out = Image.composite(warm, night, mask)
    d = ImageDraw.Draw(out)
    for f in late:
        f(d)
    bubble(d, 31, 34, "dots")
    bubble(d, 109, 34, "dots")
    bubble(d, 201, 34, "dots")
    bubble(d, 279, 34, "ok")
    bubble(d, 43, 154, "bang")
    bubble(d, 155, 90, "z")
    return out


if __name__ == "__main__":
    im = scene()
    im.resize((W * 3, H * 3), Image.NEAREST).save(sys.argv[1] + "/scene_d.png")
    im.resize((W * 4, H * 4), Image.NEAREST).save(sys.argv[1] + "/preview_d.png")
