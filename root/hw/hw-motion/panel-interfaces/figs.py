# -*- coding: utf-8 -*-
"""Фігури до теми «Інтерфейси панелей» та її математичної вставки.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Колір «труби» за щаблями: вузька → широка
THIN  = "#9aa0a6"   # SPI — найвужче
MID   = "#2457d6"   # 8080
WIDE  = "#27ae60"   # RGB
TOP   = "#7c3aed"   # MIPI-DSI — найшвидше
WIRE  = "#b08900"   # дроти/лінії даних


# ── 1. Бюджет: попит різних роздільностей проти стелі інтерфейсів ─────────────
# Ідея: на логарифмічній осі видно, що попит росте з площею×FPS, а кожна труба
# має свою стелю; SPI ледь годує дрібне, великі роздільності — лише RGB/DSI.
def fig_demand():
    W, H = 760, 430
    f = [text(W / 2, 28, "Скільки треба проти того, що дає труба (лог. шкала, Мбіт/с)", size=16, bold=True)]

    # геометрія осі (логарифмічна 1 … 10000 Мбіт/с)
    import math
    ax0, ax1 = 150.0, W - 40.0
    lo, hi = 1.0, 10000.0
    def X(v):
        return ax0 + (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (ax1 - ax0)

    # вісь із поділками-степенями десятки
    axy = H - 56
    f.append(line(ax0, axy, ax1, axy, color=INK, sw=1.6))
    for p in range(0, 5):
        v = 10 ** p
        f.append(line(X(v), axy - 4, X(v), axy + 4, color=INK, sw=1.4))
        lab = {1: "1", 10: "10", 100: "100", 1000: "1000", 10000: "10000"}[v]
        f.append(text(X(v), axy + 20, lab, size=10, color=MUTED))

    # ПОПИТ (трикутники зверху) — потрібно для роздільності @60
    f.append(text(ax0 - 8, 64, "потрібно @60:", size=11, color=INK, bold=True, anchor="end"))
    demand = [("128×64 OLED", 0.79, MUTED),
              ("320×240", 73.7, THIN),
              ("480×320", 147.0, MID),
              ("800×480", 369.0, WIDE),
              ("1280×720", 885.0, TOP)]
    y = 76
    for lab, v, c in demand:
        x = X(v)
        f.append(line(x, y, x, axy, color=c, sw=1.0, dash="2,4"))
        f.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="%s" stroke-width="1.3"/>' % (x, y, c, INK))
        f.append(text(x, y - 9, lab, size=10, color=c, bold=True))
        y += 30

    # СТЕЛЯ інтерфейсів (смуги знизу) — типова максимальна ємність
    f.append(text(ax0 - 8, 232, "стеля шини:", size=11, color=INK, bold=True, anchor="end"))
    caps = [("SPI ~80 МГц", 80.0, THIN),
            ("8080 16-біт", 320.0, MID),
            ("RGB 24-біт", 1500.0, WIDE),
            ("MIPI-DSI ×4", 6000.0, TOP)]
    y = 244
    for lab, v, c in caps:
        x = X(v)
        f.append(rect(ax0, y - 9, x - ax0, 18, fill=c, stroke=INK, sw=1.0, rx=4))
        f.append(text(x + 8, y + 4, lab, size=10.5, color=INK, anchor="start"))
        y += 28

    f.append(text(W / 2, H - 14,
                  "Площа×FPS жене попит праворуч; SPI ледь дотягує до дрібних панелей, великі роздільності годує лише RGB або MIPI-DSI.",
                  size=11.5, color=MUTED))
    render(os.path.join(IMG, "bw-demand.svg"), W, H, *f)


# ── 2. SPI: кілька дротів, панель із власною памʼяттю кадру ───────────────────
# Ідея: тонка послідовна шина, але панель сама тримає кадр (GRAM) і освіжає
# скло без МК → по SPI можна слати лише ЗМІНИ.
def fig_spi():
    W, H = 760, 360
    f = [text(W / 2, 28, "SPI: три-пʼять дротів; панель тримає кадр сама", size=16, bold=True)]

    # хост
    hb = rect(60, 110, 150, 110, fill=FILL, stroke=INK, sw=1.8, rx=8)
    f.append(hb)
    f.append(text(135, 150, "Мікроконтролер", size=13, bold=True))
    f.append(text(135, 172, "шле лише", size=11, color=MUTED))
    f.append(text(135, 188, "зміни", size=12, color=POS, bold=True))

    # панель із GRAM + скло
    pb = rect(540, 80, 170, 200, fill=FILL, stroke=INK, sw=1.8, rx=8)
    f.append(pb)
    f.append(text(625, 104, "Панель", size=13, bold=True))
    f.append(rect(560, 116, 130, 46, fill="#eef0ff", stroke=MID, sw=1.6, rx=6))
    f.append(text(625, 138, "контролер +", size=11, color=INK, bold=True))
    f.append(text(625, 153, "памʼять кадру (GRAM)", size=9.5, color=INK))
    f.append(rect(560, 176, 130, 86, fill="#1a1a1a", stroke=INK, sw=1.4, rx=4))
    f.append(text(625, 210, "скло", size=11, color="#ffffff", bold=True))
    f.append(text(625, 228, "освіжає сам", size=9.5, color="#cfd3da"))

    # лінії SPI між ними
    lines = [("MOSI — дані", THIN), ("SCK — такт", INK), ("CS — вибір", MUTED),
             ("DC — команда/дані", WIRE), ("RST — скид", MUTED)]
    ly = 128
    for lab, c in lines:
        f.append(line(212, ly, 538, ly, color=c, sw=2.0))
        f.append(text(375, ly - 6, lab, size=9.5, color=c))
        ly += 24

    f.append(text(W / 2, H - 30,
                  "SPI жене по одному біту за такт — труба вузька. Але контролер панелі сам освіжає скло з GRAM,",
                  size=11.5, color=MUTED))
    f.append(text(W / 2, H - 13,
                  "тож хост шле не весь кадр 60 разів на секунду, а лише те, що змінилося.",
                  size=11.5, color=MUTED))
    render(os.path.join(IMG, "spi.svg"), W, H, *f)


# ── 3. Паралельний 8080: ціле слово фіксується на фронті строба WR ───────────
# Ідея: вісім/шістнадцять ліній даних, на фронті WR контролер «защіпає» слово →
# у 8/16 разів ширше за SPI при тій самій частоті.
def fig_8080():
    W, H = 760, 380
    f = [text(W / 2, 28, "Паралельний 8080: ціле слово за один строб WR", size=16, bold=True)]

    # ліворуч: 16 ліній даних як шина
    bx = 90
    f.append(text(bx + 70, 62, "лінії даних D0..D15", size=11, color=WIRE, bold=True))
    for i in range(8):
        yy = 76 + i * 12
        f.append(line(bx, yy, bx + 150, yy, color=WIRE, sw=1.6))
    f.append(text(bx + 70, 76 + 8 * 12 + 6, "(8 чи 16 розрядів)", size=9.5, color=MUTED))

    # стрілка до контролера
    f.append(arrow(bx + 152, 122, bx + 210, 122, color=INK, sw=2.0))

    # контролер защіпає слово
    cb = rect(bx + 214, 86, 160, 96, fill=FILL, stroke=INK, sw=1.8, rx=8)
    f.append(cb)
    f.append(text(bx + 294, 120, "контролер", size=12, bold=True))
    f.append(text(bx + 294, 140, "«защіпає» слово", size=10.5, color=INK))
    f.append(text(bx + 294, 158, "на фронті WR", size=10.5, color=POS, bold=True))

    # сигнал WR (строб) під шиною — прямокутні імпульси
    wy = 250
    f.append(text(bx, wy - 14, "WR (строб):", size=11, color=POS, bold=True, anchor="start"))
    x = bx + 100
    seg = 34
    pts = []
    hi, loo = wy - 22, wy
    cur = hi
    for i in range(7):
        pts.append((x, cur))
        x2 = x + seg
        pts.append((x2, cur))
        cur = loo if cur == hi else hi
        x = x2
    path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path, POS))
    # позначити фронт, де фіксується слово
    fx = bx + 100 + seg * 2
    f.append(line(fx, wy - 34, fx, wy + 10, color=INK, sw=1.0, dash="2,3"))
    f.append(text(fx, wy + 26, "фронт → слово фіксується", size=9.5, color=INK))

    f.append(text(W / 2, H - 30,
                  "За один строб проходить 8 або 16 біт — у стільки ж разів ширша труба за SPI, що жене по біту.",
                  size=11.5, color=MUTED))
    f.append(text(W / 2, H - 13,
                  "Платять пінами: 12–24 проводи проти трьох. Усередині — той самий контролер із GRAM, що й у SPI.",
                  size=11.5, color=MUTED))
    render(os.path.join(IMG, "p8080.svg"), W, H, *f)


# ── 4. RGB-паралельний: панель без памʼяті, безперервний растровий скан ───────
# Ідея: панель «дурна», без GRAM; хост мусить безупинно видавати весь растр під
# PCLK, з порожніми полями (porch) між видимими ділянками.
def fig_rgb():
    W, H = 760, 390
    f = [text(W / 2, 28, "RGB-паралельний: панель без памʼяті, скан без упину", size=16, bold=True)]

    # хост із контролером дисплея + кадровий буфер
    hb = rect(56, 92, 180, 150, fill=FILL, stroke=INK, sw=1.8, rx=8)
    f.append(hb)
    f.append(text(146, 116, "Хост", size=13, bold=True))
    f.append(rect(74, 128, 144, 40, fill="#eafaf0", stroke=WIDE, sw=1.6, rx=6))
    f.append(text(146, 146, "кадровий буфер", size=10.5, color=INK, bold=True))
    f.append(text(146, 161, "(памʼять — тут!)", size=9.5, color=INK))
    f.append(rect(74, 178, 144, 48, fill="#eef0ff", stroke=MID, sw=1.6, rx=6))
    f.append(text(146, 198, "контролер дисплея", size=10.5, color=INK, bold=True))
    f.append(text(146, 214, "вичитує через DMA", size=9.5, color=INK))

    # шина RGB
    f.append(text(390, 92, "PCLK + R/G/B + HSYNC/VSYNC/DE", size=10.5, color=WIDE, bold=True))
    for i in range(6):
        yy = 104 + i * 11
        f.append(line(238, yy, 540, yy, color=WIDE, sw=1.6))
    f.append(text(390, 104 + 6 * 11 + 6, "широка безперервна шина (28–40 пінів)", size=9.5, color=MUTED))

    # «дурна» панель: растровий скан рядок за рядком + porch
    pb = rect(540, 92, 170, 170, fill="#1a1a1a", stroke=INK, sw=1.6, rx=6)
    f.append(pb)
    f.append(text(625, 112, "панель без GRAM", size=10.5, color="#ffffff", bold=True))
    # рядки скану
    for i in range(5):
        yy = 126 + i * 16
        f.append(line(556, yy, 678, yy, color="#3a6df0" if i < 4 else "#6b7280", sw=2.2))
    # porch як штрихова «зворотна» паузa
    f.append(line(678, 126, 556, 142, color=POS, sw=1.0, dash="2,3"))
    f.append(text(625, 232, "хтось мусить лити", size=9.5, color="#cfd3da"))
    f.append(text(625, 247, "весь растр щокадру", size=9.5, color="#ff8a80", bold=True))

    f.append(text(W / 2, H - 46,
                  "Панель лише засвічує те, що зараз на лініях. Зупиниш потік — картинка розсиплеться.",
                  size=11.5, color=MUTED))
    f.append(text(W / 2, H - 29,
                  "Контролер дисплея безперервно сканує кадр, видаючи пікселі під PCLK; між видимими ділянками —",
                  size=11.5, color=MUTED))
    f.append(text(W / 2, H - 13,
                  "порожні «поля» (porch) для гасіння. Памʼ ять під кадровий буфер — у самому хості.",
                  size=11.5, color=MUTED))
    render(os.path.join(IMG, "rgb.svg"), W, H, *f)


# ── 5. MIPI-DSI: кілька диференційних пар несуть гігабіти ─────────────────────
# Ідея: послідовний, як SPI, але по диференційних парах на дуже високій частоті;
# менше дротів за RGB, а несе набагато більше.
def fig_dsi():
    W, H = 760, 360
    f = [text(W / 2, 28, "MIPI-DSI: кілька диференційних пар несуть гігабіти", size=16, bold=True)]

    hb = rect(70, 110, 150, 120, fill=FILL, stroke=INK, sw=1.8, rx=8)
    f.append(hb)
    f.append(text(145, 152, "Потужний хост", size=12, bold=True))
    f.append(text(145, 172, "(SoC із DSI)", size=10.5, color=MUTED))
    f.append(text(145, 196, "пакетний протокол", size=9.5, color=INK))

    pb = rect(560, 110, 150, 120, fill=FILL, stroke=INK, sw=1.8, rx=8)
    f.append(pb)
    f.append(text(635, 158, "Панель", size=12, bold=True))
    f.append(text(635, 178, "телефонна", size=10.5, color=MUTED))
    f.append(text(635, 194, "роздільність", size=10.5, color=MUTED))

    # пари: тактова + до 4 смуг даних (по два проводи протифазно)
    pairs = [("тактова пара", TOP, 132), ("смуга даних 1", MID, 156),
             ("смуга даних 2", MID, 180), ("…до 4 смуг", MUTED, 204)]
    for lab, c, yy in pairs:
        f.append(line(222, yy - 3, 558, yy - 3, color=c, sw=1.8))
        f.append(line(222, yy + 3, 558, yy + 3, color=c, sw=1.8))
        f.append(text(390, yy - 8, lab, size=9.5, color=c, bold=True))
    f.append(text(390, 222, "кожна смуга — гігабіти за секунду", size=10, color=TOP, bold=True))

    f.append(text(W / 2, H - 46,
                  "Менше дротів за паралельний RGB, а несе набагато більше — завдяки диференційній передачі на дуже високій частоті.",
                  size=11.5, color=MUTED))
    f.append(text(W / 2, H - 29,
                  "Відеорежим — панель без памʼяті, хост ллє кадри без упину; командний — панель має GRAM, хост шле лише зміни.",
                  size=11.5, color=MUTED))
    f.append(text(W / 2, H - 13,
                  "Ціна — складність: пакетний протокол, жорстке розведення пар, і DSI вміють лише потужні МК та системи-на-кристалі.",
                  size=11.5, color=MUTED))
    render(os.path.join(IMG, "dsi.svg"), W, H, *f)


# ── 6. Карта чотирьох інтерфейсів: піни / смуга / памʼять / ноша на хост ──────
# Ідея: що ширша труба, то або більше дротів (RGB), або складніший хост (DSI);
# дешеві SPI/8080 кладуть клопіт на контролер панелі, широкі — на хост.
def fig_compare():
    W, H = 780, 420
    f = [text(W / 2, 28, "Чотири інтерфейси поруч: за швидкість платять пінами або складністю", size=15, bold=True)]

    cols = [("SPI", THIN, "3–5", "десятки\nМбіт/с", "у панелі", "лише зміни", "дрібні"),
            ("8080", MID, "12–24", "сотні\nМбіт/с", "у панелі", "лише зміни", "середні"),
            ("RGB", WIDE, "28–40", "до ~1.5\nГбіт/с", "у ХОСТІ", "весь кадр\nщоразу", "великі"),
            ("MIPI-DSI", TOP, "кілька\nпар", "гігабіти\n/смугу", "хост або\nпанель", "режим\nвирішує", "телефонні")]

    rows = ["піни", "стеля смуги", "памʼять кадру", "що шлемо", "для чого"]
    colw = 168
    x0 = 70
    rowh = 56
    y0 = 70

    # шапка-колонки
    for i, (name, c, *_rest) in enumerate(cols):
        cx = x0 + i * colw
        f.append(rect(cx, y0, colw - 12, 30, fill=c, stroke=INK, sw=1.4, rx=6))
        f.append(text(cx + (colw - 12) / 2, y0 + 20, name, size=12.5, color="#ffffff", bold=True))

    # рядки-властивості
    for r, rlab in enumerate(rows):
        ry = y0 + 38 + r * rowh
        f.append(text(x0 - 12, ry + rowh / 2, rlab, size=10.5, color=INK, bold=True, anchor="end"))
        for i, col in enumerate(cols):
            cx = x0 + i * colw
            val = col[2 + r]
            f.append(fitbox(cx, ry, colw - 12, rowh - 8, val, size=11, fill=FILL,
                            stroke=MUTED, color=INK))

    f.append(text(W / 2, H - 14,
                  "Дешеві SPI й 8080 перекладають клопіт на контролер панелі; широкі RGB і DSI — на хост, що сам тримає кадр і безупинно його гонить.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "compare.svg"), W, H, *f)


# ── 7. (математична вставка) Бюджет: попит із накладними проти ємности шини ───
# Ідея: повний кадр 320×240@60 не влазить у SPI; розумна панель шле лише вікно
# зміни й влазить із величезним запасом.
def fig_budget():
    W, H = 760, 380
    f = [text(W / 2, 28, "Бюджет: потрібно (з накладними) проти того, що дає шина", size=15, bold=True)]

    import math
    ax0, ax1 = 220.0, W - 50.0
    lo, hi = 0.3, 200.0
    def X(v):
        return ax0 + (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (ax1 - ax0)

    axy = H - 60
    f.append(line(ax0, 70, ax0, axy, color=INK, sw=1.4))
    f.append(line(ax0, axy, ax1, axy, color=INK, sw=1.6))
    for v in (1, 10, 100):
        f.append(line(X(v), axy - 4, X(v), axy + 4, color=INK, sw=1.2))
        f.append(text(X(v), axy + 18, str(v), size=10, color=MUTED))
    f.append(text((ax0 + ax1) / 2, axy + 38, "Мбіт/с (лог. шкала)", size=10.5, color=MUTED))

    bars = [
        ("повний кадр 320×240@60 + накладні", 92.0, POS, "потрібно ≈92"),
        ("SPI 40 МГц, ефективно ×0.8", 32.0, THIN, "дає ≈32  →  НЕ влазить"),
        ("розумна панель: лише вікно 100×40@10", 0.64, FIELD, "потрібно 0.64  →  влазить легко"),
    ]
    by = 84
    bh = 30
    gap = 46
    for lab, v, c, note in bars:
        f.append(text(ax0 - 10, by + bh / 2 + 4, lab, size=9.5, color=INK, bold=True, anchor="end"))
        f.append(rect(ax0, by, max(2.0, X(v) - ax0), bh, fill=c, stroke=INK, sw=1.0, rx=4))
        f.append(text(X(v) + 8, by + bh / 2 + 4, note, size=10, color=INK, anchor="start"))
        by += gap

    # лінія межі SPI
    f.append(line(X(32.0), 76, X(32.0), axy, color=THIN, sw=1.0, dash="3,3"))
    f.append(text(X(32.0), 74, "межа SPI", size=9, color=THIN))

    f.append(text(W / 2, H - 16,
                  "Повний кадр просить ≈92 (74 + накладні) і не влазить у SPI (≈32). Часткове оновлення розумної панелі — менш ніж мегабіт.",
                  size=10.5, color=MUTED))
    render(os.path.join(IMG, "budget.svg"), W, H, *f)


if __name__ == "__main__":
    fig_demand()
    fig_spi()
    fig_8080()
    fig_rgb()
    fig_dsi()
    fig_compare()
    fig_budget()
    print("OK: 7 SVG у", IMG)
