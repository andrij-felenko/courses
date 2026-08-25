# -*- coding: utf-8 -*-
"""Фігури до теми «Узгодження caps»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Від множини до точки ────────────────────────────────────────────────
def fig_sets():
    W, H = 940, 600
    f = []

    bw, bh = 400, 130
    lx, rx_ = 40, 500
    ty = 60

    f.append(fitbox(lx, ty, bw, bh,
                    ["ДЖЕРЕЛО віддає (src)",
                     "video/x-raw, format={NV12, YUY2},",
                     "width=[320, 1920], height=[240, 1080],",
                     "framerate=[1/1, 60/1]"],
                    size=15, pad=14))
    f.append(fitbox(rx_, ty, bw, bh,
                    ["КОДЕР приймає (sink)",
                     "video/x-raw, format={I420, NV12},",
                     "width=[16, 4096], height=[16, 4096],",
                     "framerate=[0/1, 120/1]"],
                    size=15, pad=14))

    my = 250
    f.append(arrow(lx + bw / 2, ty + bh + 8, 470, my - 14))
    f.append(arrow(rx_ + bw / 2, ty + bh + 8, 470, my - 14))

    f.append(fitbox(150, my, 640, 110,
                    ["ПЕРЕТИН — що вміють обоє (ще множина)",
                     "video/x-raw, format=NV12,",
                     "width=[320, 1920], height=[240, 1080], framerate=[1/1, 60/1]"],
                    size=15, pad=14))

    fy = 430
    f.append(arrow(470, my + 110 + 10, 470, fy - 14))
    f.append(text(500, 400, "фіксація: з кожного поля беремо одне значення",
                  size=14, color=MUTED, anchor="start"))

    f.append(fitbox(150, fy, 640, 100,
                    ["ЗАФІКСОВАНІ caps — рівно один формат",
                     "video/x-raw, format=NV12,",
                     "width=1920, height=1080, framerate=30/1"],
                    size=15, pad=14, stroke=FIELD, sw=2.2))

    f.append(text(470, 572, "порожній перетин на цьому кроці = помилка not-negotiated",
                  size=14, color=POS))

    render(os.path.join(OUT, 'caps-sets.svg'), W, H, *f,
           title="Від множини можливостей до одного формату")


# ── 2. Хто кого питає ──────────────────────────────────────────────────────
def fig_flow():
    W, H = 980, 630
    f = []
    cols = [160, 490, 820]
    names = ["ДЖЕРЕЛО", "ПЕРЕТВОРЮВАЧ", "ПРИЙМАЧ"]
    top = 70

    for x, nm in zip(cols, names):
        b, bwv, bhv = textbox(x, top, nm, size=15, bold=True, min_w=200)
        f.append(b)
        f.append(line(x, top + bhv / 2, x, 552, color=MUTED, sw=1.2, dash="5,5"))

    def step(y, x1, x2, label, color=LINE, dashed=False):
        out = [mtext((x1 + x2) / 2, y - 15, label, size=13, color=color)]
        if dashed:
            out.append(line(x1, y, x2, y, color=color, sw=1.4, dash="6,4"))
            dx = 18 if x2 > x1 else -18
            out.append(arrow(x2 - dx, y, x2, y, color=color))
        else:
            out.append(arrow(x1, y, x2, y, color=color))
        return out

    f += step(190, cols[0] + 12, cols[1] - 12, "1. CAPS-запит: що ти приймаєш?")
    f += step(252, cols[1] + 12, cols[2] - 12, "2. той самий запит далі за течією")
    f += step(314, cols[2] - 12, cols[1] + 12, "3. відповідь: множина форматів",
              color=NEG, dashed=True)
    f += step(376, cols[1] - 12, cols[0] + 12, "4. відповідь, звужена самим перетворювачем",
              color=NEG, dashed=True)
    f += step(452, cols[0] + 12, cols[1] - 12, "5. подія CAPS: обрано NV12 1920×1080",
              color=FIELD)
    f += step(514, cols[1] + 12, cols[2] - 12, "6. подія CAPS далі, а за нею буфери",
              color=FIELD)

    f.append(text(30, 590, "штрихова стрілка — відповідь на запит;  суцільна — те, що йде каналом даних",
                  size=13, color=MUTED, anchor="start"))
    f.append(text(30, 614, "проти течії питають, за течією оголошують рішення",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'negotiation-flow.svg'), W, H, *f,
           title="Проти течії питають, за течією оголошують")


# ── 3. Ознаки caps: однаковий формат, різна пам'ять ────────────────────────
def fig_features():
    W, H = 900, 570
    f = []
    lanes = [
        (70, "memory:SystemMemory", "звичайна оперативна пам'ять", MUTED),
        (210, "memory:DMABuf", "буфер, яким володіє драйвер", NEG),
        (350, "memory:GLMemory", "текстура в пам'яті відеокарти", FIELD),
    ]
    for y, feat, note, col in lanes:
        f.append(rect(40, y, 820, 100, fill="#fbfcfd", stroke=col, sw=1.8))
        f.append(text(62, y + 30, feat, size=15, color=col, anchor="start", bold=True))
        f.append(text(62, y + 54, note, size=13, color=MUTED, anchor="start"))
        f.append(text(62, y + 84, "video/x-raw, format=NV12, width=1920, height=1080",
                      size=14, color=INK, anchor="start"))

    f.append(text(450, 195, "перетин порожній: перенести кадр може лише окремий елемент",
                  size=13, color=POS))
    f.append(text(450, 335, "те саме тут: glupload, мапування dmabuf, копія в пам'ять",
                  size=13, color=POS))

    f.append(text(450, 500, "рядок формату однаковий у всіх трьох — але це три різні типи",
                  size=14, color=INK))

    render(os.path.join(OUT, 'caps-features.svg'), W, H, *f,
           title="Ознака caps робить однакові формати несумісними")


# ── 4. Де живе формат: 0.10 проти 1.0 ──────────────────────────────────────
def fig_zero_ten_vs_one_zero():
    W, H = 980, 515
    f = []
    f.append(line(490, 24, 490, H - 30, color="#d0d5db", sw=1.4, dash="5,5"))

    # ── ліва колонка: 0.10 ──
    x0 = 30
    f.append(text(x0 + 220, 34, "GStreamer 0.10", size=17, color=INK, bold=True))
    f.append(text(x0 + 220, 56, "грудень 2005 — вересень 2012", size=12, color=MUTED))

    f.append(rect(x0 + 15, 78, 410, 112, fill="#fbfcfd", stroke="#c8cdd4", sw=1.4))
    f.append(text(x0 + 30, 100, "канал даних →", size=12, color=MUTED, anchor="start"))
    for i in range(3):
        f.append(fitbox(x0 + 28 + i * 128, 112, 118, 62,
                        ["буфер", "+ свої caps"], size=13, pad=8))

    f.append(rect(x0 + 15, 212, 410, 134, fill="#fff8f7", stroke=POS, sw=1.4))
    f.append(text(x0 + 28, 236, "поза каналом — виклики функцій пада",
                  size=13, color=POS, anchor="start", bold=True))
    for i, s in enumerate(["setcaps() — ось твій новий формат",
                           "getcaps() — які формати ти приймаєш?",
                           "acceptcaps() — а цей формат піде?",
                           "pad_alloc() — виділи буфер, і заразом домовмось"]):
        f.append(text(x0 + 28, 262 + i * 22, s, size=13, color=INK, anchor="start"))

    f.append(fitbox(x0 + 15, 372, 410, 88,
                    ["Формат живе у двох місцях:",
                     "на паді й на кожному буфері.",
                     "Обидва мусять збігатися."], size=13, pad=10))

    # ── права колонка: 1.0 ──
    x0 = 510
    f.append(text(x0 + 220, 34, "GStreamer 1.0", size=17, color=INK, bold=True))
    f.append(text(x0 + 220, 56, "24 вересня 2012", size=12, color=MUTED))

    f.append(rect(x0 + 15, 78, 410, 112, fill="#fbfcfd", stroke="#c8cdd4", sw=1.4))
    f.append(text(x0 + 30, 100, "канал даних →", size=12, color=MUTED, anchor="start"))
    f.append(fitbox(x0 + 25, 112, 152, 62, ["подія CAPS", "(липка)"],
                    size=13, pad=8, stroke=FIELD, sw=1.8))
    f.append(fitbox(x0 + 187, 112, 104, 62, ["буфер"], size=13, pad=8))
    f.append(fitbox(x0 + 301, 112, 104, 62, ["буфер"], size=13, pad=8))

    f.append(rect(x0 + 15, 212, 410, 134, fill="#f6fbf7", stroke=FIELD, sw=1.4))
    f.append(text(x0 + 28, 236, "у тому самому каналі — запити й події",
                  size=13, color=FIELD, anchor="start", bold=True))
    for i, s in enumerate(["запит CAPS (з фільтром) — що приймаєш?",
                           "запит ACCEPT_CAPS — а цей формат піде?",
                           "подія RECONFIGURE — перепитай, у нас змінилось",
                           "запит ALLOCATION — звідки брати пам'ять"]):
        f.append(text(x0 + 28, 262 + i * 22, s, size=13, color=INK, anchor="start"))

    f.append(fitbox(x0 + 15, 372, 410, 88,
                    ["Формат живе в одному місці:",
                     "липка подія в каналі даних.",
                     "Пізній пад дістає її одразу."], size=13, pad=10))

    render(os.path.join(OUT, 'nego-0-10-vs-1-0.svg'), W, H, *f,
           title="Де живе формат: 0.10 проти 1.0")


# ── 5. Розбір рядка caps на частини ────────────────────────────────────────
def fig_anatomy():
    W, H = 1080, 570
    f = []

    colw, gap, x0, ty, bh = 196, 13, 24, 62, 54
    frags = ["video/x-raw", "(memory:DMABuf)", "format={ NV12, I420 }",
             "width=[ 16, 4096, 16 ]", "framerate=30/1"]
    labels = [
        ["ім'я медіатипу", "чим є ці байти"],
        ["ознака (з 1.2)", "де байти лежать;", "без дужок —", "звичайна пам'ять"],
        ["поле: список", "{ } — одне з;", "порядок = перевага"],
        ["поле: діапазон", "[ мін, макс, крок ]", "крок — необов'язковий"],
        ["поле: дріб a/b", "одне значення —", "уже зафіксоване"],
    ]
    cols = [x0 + i * (colw + gap) for i in range(5)]

    for i, (x, s) in enumerate(zip(cols, frags)):
        stroke = FIELD if i == 1 else LINE
        f.append(fitbox(x, ty, colw, bh, s, size=14, pad=8, stroke=stroke,
                        sw=1.8 if i == 1 else 1.5))
        if i:
            f.append(text(x - gap / 2, ty + bh - 16, ",", size=16, color=MUTED))

    for x, lab in zip(cols, labels):
        f.append(arrow(x + colw / 2, ty + bh + 4, x + colw / 2, 148))
        f.append(fitbox(x, 152, colw, 92, lab, size=12, pad=8,
                        fill="#fbfcfd", stroke="#c8cdd4", sw=1.2, color=MUTED))

    f.append(text(x0, 292, "крапка з комою починає наступну структуру — рівноправну альтернативу:",
                  size=14, color=INK, anchor="start"))
    f.append(fitbox(x0, 308, 1032, 52,
                    "video/x-raw, format=NV12, width=1920 ;  video/x-bayer, format=bggr",
                    size=15, pad=12))

    f.append(fitbox(x0, 392, 506, 80,
                    ["ANY — годиться будь-що", "у рядку так і пишуть: ANY"],
                    size=14, pad=10, stroke=NEG, sw=1.8))
    f.append(fitbox(x0 + 526, 392, 506, 80,
                    ["EMPTY — не годиться нічого", "результат невдалого перетину"],
                    size=14, pad=10, stroke=POS, sw=1.8))

    f.append(text(W / 2, 512, "зафіксовані caps — рівно одна структура і жодних { } [ ] ANY",
                  size=14, color=INK))
    f.append(text(W / 2, 540, "перевіряє gst_caps_is_fixed()", size=13, color=MUTED))

    render(os.path.join(OUT, 'caps-anatomy.svg'), W, H, *f,
           title="З чого складається рядок caps")


# ── 6. Три рівні: caps → структура → значення ──────────────────────────────
def fig_objects():
    W, H = 1000, 615
    f = []

    box, bw, bh = textbox(W / 2, 82, ["GstCaps — упорядкований набір структур",
                                      "gst_caps_get_size() — скільки їх"],
                          size=15, pad=12, min_w=540)
    f.append(box)

    f.append(arrow(W / 2 - 120, 82 + bh / 2 + 4, 260, 166))
    f.append(arrow(W / 2 + 120, 82 + bh / 2 + 4, 740, 166))

    f.append(fitbox(60, 170, 400, 100,
                    ["структура 0",
                     "GstStructure  +  GstCapsFeatures",
                     "gst_caps_get_structure(caps, 0)",
                     "gst_caps_get_features(caps, 0)"],
                    size=13, pad=10, stroke=FIELD, sw=1.8))
    f.append(fitbox(540, 170, 400, 100,
                    ["структура 1 — альтернатива",
                     "устрій той самий",
                     "порядок структур = перевага,",
                     "перша найбажаніша"],
                    size=13, pad=10))

    f.append(arrow(260, 274, 260, 300))

    f.append(rect(60, 302, 880, 248, fill="#fbfcfd", stroke="#c8cdd4", sw=1.4))
    f.append(text(W / 2, 330, "поля структури 0 — кожне значення це GValue",
                  size=14, color=INK, bold=True))

    c1, c2, c3 = 80, 380, 660
    f.append(text(c1, 356, "поле = значення", size=12, color=MUTED, anchor="start"))
    f.append(text(c2, 356, "тип значення", size=12, color=MUTED, anchor="start"))
    f.append(text(c3, 356, "чим читати", size=12, color=MUTED, anchor="start"))
    f.append(line(72, 368, 928, 368, color="#d0d5db", sw=1.2))

    rows = [
        ("format = NV12", "рядок", "gst_structure_get_string()"),
        ("width = [ 16, 4096 ]", "діапазон цілих", "gst_structure_get_value()"),
        ("framerate = 30/1", "дріб", "gst_structure_get_fraction()"),
        ("interlace-mode = progressive", "рядок", "gst_structure_get_string()"),
    ]
    for i, (a, b, c) in enumerate(rows):
        y = 394 + i * 34
        f.append(text(c1, y, a, size=13, color=INK, anchor="start"))
        f.append(text(c2, y, b, size=13, color=MUTED, anchor="start"))
        f.append(text(c3, y, c, size=13, color=NEG, anchor="start"))

    f.append(text(W / 2, 578, "нема поля — нема обмеження: це «будь-яке значення», а не «типове»",
                  size=14, color=POS))

    render(os.path.join(OUT, 'caps-objects.svg'), W, H, *f,
           title="Три рівні: caps → структура → значення")


# ── Два сценарії переговорів того самого елемента ──────────────────────────
def fig_two_scenarios():
    W, H = 980, 640
    f = []

    lx = 30
    ax, aw = 210, 370
    bx, bw = 590, 370

    f.append(text(ax + aw / 2, 62, "A: далі приймач, якому байдуже",
                  size=14, color=FIELD, bold=True))
    f.append(text(bx + bw / 2, 62, "B: далі вимога 480×640",
                  size=14, color=NEG, bold=True))

    rows = [
        ("на sink-паді",
         ["зафіксовано 640×480"],
         ["зафіксовано 640×480"]),
        ("transform_caps",
         ["множина з іншого боку:", "640×480  або  480×640",
          "тотожність — першою"],
         ["множина з іншого боку:", "640×480  або  480×640",
          "тотожність — першою"]),
        ("перетин із сусідом",
         ["приймач бере будь-що:", "лишились обидві",
          "НЕ зафіксовано"],
         ["приймач хоче портрет:", "лишилась одна",
          "уже зафіксовано"]),
        ("fixate_caps",
         ["тримайся тотожності:", "обрано 640×480"],
         ["не викликається —", "обирати нема з чого"]),
        ("set_caps",
         ["640×480 → 640×480", "наскрізний режим"],
         ["640×480 → 480×640", "поворот кожного кадру"]),
    ]

    y = 88
    for label, a, b in rows:
        h = 46 + 22 * (len(a) - 1)
        f.append(text(lx, y + h / 2 + 5, label, size=13, color=MUTED, anchor="start"))
        f.append(fitbox(ax, y, aw, h, a, size=14, pad=10, stroke=FIELD, sw=1.6))
        f.append(fitbox(bx, y, bw, h, b, size=14, pad=10, stroke=NEG, sw=1.6))
        y += h + 18

    f.append(text(W / 2, y + 20,
                  "fixate_caps потрібен лише там, де після перетину лишилась свобода",
                  size=14, color=INK))
    f.append(text(W / 2, y + 46,
                  "у сценарії A елемент договорився до того, що йому нема чого робити",
                  size=13, color=MUTED))

    render(os.path.join(OUT, 'transform-two-scenarios.svg'), W, H, *f,
           title="Той самий елемент, два різні сусіди")


fig_sets()
fig_flow()
fig_features()
fig_zero_ten_vs_one_zero()
fig_anatomy()
fig_objects()
fig_two_scenarios()
print("ok")
