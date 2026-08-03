# -*- coding: utf-8 -*-
"""Фігури до кроку «Модульний моноліт як дефолт»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_burden_gate():
    """Ворота дефолту на кожному контексті: чи є ВИМІРЯНИЙ драйвер платити за мережу.
    Ні → лишається модулем у моноліті + записана розтяжка. Так → виносимо по шву."""
    W, H = 1140, 600
    frags = []

    b, _, _ = textbox(570, 84, "Новий контекст / нова спромога", size=13,
                      fill=FILL, min_w=360)
    frags.append(b)
    frags.append(arrow(570, 106, 570, 176, color=LINE, sw=1.8))

    # ворота-питання
    b, _, _ = textbox(570, 212,
                      "Чи має САМЕ ЦЕЙ контекст виміряний драйвер платити за мережу?\n"
                      "(окремий масштаб · окрема команда · окрема доступність + число)",
                      size=13, fill="#eef2fb", stroke=NEG, min_w=560)
    frags.append(b)

    # ліва гілка «ні»
    frags.append(arrow(455, 244, 300, 344, color=FIELD, sw=1.8))
    frags.append(text(356, 288, "ні", size=14, color=FIELD, bold=True))
    b, _, _ = textbox(288, 366, "лишається модулем у моноліті", size=13,
                      fill="#eafaf0", stroke=FIELD, bold=True, min_w=300)
    frags.append(b)
    frags.append(arrow(288, 392, 288, 462, color=FIELD, sw=1.7))
    b, _, _ = textbox(288, 494, "запиши сигнальну розтяжку:\n"
                      "число під моніторингом (фітнес-функція)", size=12,
                      fill="#f7f9fc", stroke=MUTED, min_w=360)
    frags.append(b)

    # права гілка «так»
    frags.append(arrow(685, 244, 838, 344, color=POS, sw=1.8))
    frags.append(text(788, 288, "так", size=14, color=POS, bold=True))
    b, _, _ = textbox(852, 366, "виносимо в сервіс", size=13,
                      fill="#fdecea", stroke=POS, bold=True, min_w=250)
    frags.append(b)
    frags.append(mtext(852, 420, ["по вже накресленому шву (strangler-fig);",
                                  "назви драйвер і виміряй його"], size=12, color=MUTED))

    render(os.path.join(IMG, "burden-gate.svg"), W, H, *frags,
           title="Ворота дефолту: мережа з'являється лише там, де драйвер її купує")


def fig_one_way_door():
    """Асиметрія зворотності: межа-модуль — двобічні двері (дешевий рефакторинг);
    межа-сервіс на мережі — однобічні (опублікований контракт). Повернення дороге."""
    W, H = 1180, 480
    frags = []

    x0, x1 = 110, 1070
    axis_y = 322

    # ── forward / back між маркерами (у чистій середній смузі) ──
    frags.append(arrow(448, 98, 738, 98, color=INK, sw=2.4))
    frags.append(text(592, 84, "перше розгортання по мережі  →", size=12.5,
                      color=INK, bold=True))

    # ── маркери ──
    b, _, _ = textbox(296, 168, "межа-модуль у моноліті\n"
                      "(рефакторинг за півдня · бачиш лише ти)", size=12.5,
                      fill="#eafaf0", stroke=FIELD, bold=False, min_w=340)
    frags.append(b)
    b, _, _ = textbox(866, 168, "межа-сервіс на мережі\n"
                      "(опублікований контракт · на ньому чужі клієнти)", size=12.5,
                      fill="#fdecea", stroke=POS, bold=False, min_w=380)
    frags.append(b)

    # back-arrow нижче маркерів, над віссю
    frags.append(line(738, 238, 452, 238, color=MUTED, sw=1.6, dash="6,6"))
    frags.append('<path d="M462 233 L450 238 L462 243" fill="none" stroke="%s" '
                 'stroke-width="1.6"/>' % MUTED)
    frags.append(text(592, 260, "повернення дороге: Segment 140 сервісів → 1",
                      size=12.5, color=MUTED))

    # ── вісь зворотності ──
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=1.8))
    frags.append(line(296, 198, 296, axis_y - 2, color=FIELD, sw=1.3, dash="3,4"))
    frags.append(line(866, 198, 866, axis_y - 2, color=POS, sw=1.3, dash="3,4"))
    frags.append(mtext(x0 + 6, axis_y + 28, ["зворотне", "двобічні двері"],
                       size=12, color=MUTED, anchor="start"))
    frags.append(mtext(x1 - 6, axis_y + 28, ["незворотне", "однобічні двері"],
                       size=12, color=MUTED, anchor="end"))
    frags.append(text((x0 + x1) / 2, axis_y + 30, "росте ціна незворотності  →",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "one-way-door.svg"), W, H, *frags,
           title="Асиметрія дверей: модуль вертається дешево, сервіс на мережі — ні")


def fig_pendulum():
    """Маятник моди: народження терміна → хвиля → застереження ЗАЗДАЛЕГІДЬ (2015)
    → два публічні відкати (Segment 2018, Prime Video 2023). Головне — monolith-first
    стоїть на осі РАНІШЕ за обидва повернення."""
    W, H = 1260, 600
    frags = []
    x0, x1, axis_y = 120, 1140, 300

    def xof(year):
        return 140 + (year - 2011) / 12.0 * 980.0

    # вісь часу
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.0))
    frags.append(text(x1 + 4, axis_y + 5, "час →", size=13, color=MUTED, anchor="start"))

    # вузли: (рік, бік, колір, рядки, cy)
    nodes = [
        (2011, "up",   INK,   ["2011 · Венеція", "народжується термін", "«мікросервіси»"], 138),
        (2014, "up",   INK,   ["2014", "стаття Люїса–Фаулера", "хвиля моди міцніє"],        138),
        (2015, "down", FIELD, ["2015 · Фаулер", "monolith-first +", "microservice premium",
                               "застереження — ЗАЗДАЛЕГІДЬ"],                                430),
        (2018, "down", POS,   ["2018 · Segment", "140 сервісів → 1", "(Centrifuge)"],       505),
        (2023, "up",   POS,   ["2023 · Prime Video", "конвеєр → 1 процес, −90%",
                               "дебат DHH ↔ Cockcroft"],                                     150),
    ]
    fills = {INK: FILL, FIELD: "#eafaf0", POS: "#fdecea"}
    for year, side, col, lines, cy in nodes:
        x = xof(year)
        frags.append(circle(x, axis_y, 6, fill=col, stroke=col, sw=1.5))
        b, w, h = textbox(x, cy, "\n".join(lines), size=12,
                          fill=fills[col], stroke=col, min_w=190)
        # з'єднувач від рамки до вузла на осі
        if side == "up":
            frags.append(line(x, cy + h / 2, x, axis_y - 7, color=col, sw=1.3, dash="3,4"))
        else:
            frags.append(line(x, axis_y + 7, x, cy - h / 2, color=col, sw=1.3, dash="3,4"))
        frags.append(b)

    # дві фази під усім
    frags.append(text(560, 566, "розгін моди — копіюють картинку, а не механізм",
                      size=12.5, color=MUTED))
    frags.append(text(1000, 566, "відкат і тверезіння", size=12.5, color=MUTED))
    frags.append(arrow(800, 561, 880, 561, color=MUTED, sw=1.4))

    render(os.path.join(IMG, "pendulum.svg"), W, H, *frags,
           title="Маятник моди: застереження передувало відкату")


def fig_prime_collapse():
    """Куди поділися 90%: розподілений конвеєр (Step Functions + Lambda + S3 щокроку)
    згортається в один процес одного ECS-таска з кадрами в пам'яті."""
    W, H = 1280, 650
    frags = []

    # ── ліва панель: розподілений конвеєр ──
    b, _, _ = textbox(305, 70, "Розподілений конвеєр\n(Step Functions + Lambda + S3)",
                      size=13, fill=FILL, stroke=LINE, bold=True, min_w=380)
    frags.append(b)

    b, sfw, sfh = textbox(305, 140, "Step Functions — оркестратор", size=12.5,
                          fill="#eef2fb", stroke=NEG, min_w=320)
    frags.append(b)
    frags.append(text(400, 182, "плата за кожен перехід стану", size=11, color=MUTED))

    dets = [250, 325, 400]
    for i, y in enumerate(dets):
        b, dw, dh = textbox(230, y, "детектор %s" % "ABC"[i], size=12,
                            fill=FILL, stroke=LINE, min_w=150)
        frags.append(b)
    frags.append(arrow(305, 165, 230, 232, color=LINE, sw=1.5))
    frags.append(arrow(230, 264, 230, 310, color=LINE, sw=1.5))
    frags.append(arrow(230, 339, 230, 386, color=LINE, sw=1.5))

    # S3 збоку, кожен крок туди-сюди
    b, s3w, s3h = textbox(470, 325, "S3\nкадри між\nкроками", size=12,
                          fill="#f7f9fc", stroke=MUTED, min_w=120)
    for y in dets:
        frags.append(line(308, y, 412, 325, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(b)
    frags.append(text(470, 388, "кадр у S3 і назад — щокроку", size=10.5, color=MUTED))

    b, _, _ = textbox(305, 480, "стеля на ~5% навантаження · дорого", size=12.5,
                      fill="#fdecea", stroke=POS, bold=True, min_w=340)
    frags.append(b)

    # ── стрілка згортання ──
    frags.append(arrow(566, 300, 726, 300, color=INK, sw=2.6))
    frags.append(text(646, 285, "згортання", size=13, color=INK, bold=True))

    # ── права панель: один процес ──
    b, _, _ = textbox(985, 70, "Один процес в одному ECS-таску", size=13,
                      fill=FILL, stroke=LINE, bold=True, min_w=380)
    frags.append(b)

    # ghost-клон позаду (натяк на масштаб клонуванням)
    frags.append(rect(786, 132, 452, 300, fill="none", stroke=MUTED, sw=1.2, rx=10))
    # головний контейнер
    frags.append(rect(770, 118, 452, 300, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(996, 150, "ECS-таск: один процес", size=12.5, color=INK, bold=True))

    rcx = [858, 996, 1134]
    for i, cx in enumerate(rcx):
        b, _, _ = textbox(cx, 250, "детектор %s" % "ABC"[i], size=12,
                          fill=FILL, stroke=LINE, min_w=96)
        frags.append(b)
    frags.append(arrow(906, 250, 948, 250, color=LINE, sw=1.5))
    frags.append(arrow(1044, 250, 1086, 250, color=LINE, sw=1.5))
    frags.append(text(996, 340, "кадри лишаються в RAM — без S3", size=12, color=FIELD, bold=True))
    frags.append(text(996, 372, "оркестрація — виклики в пам'яті, без Step Functions",
                      size=11, color=MUTED))

    b, _, _ = textbox(996, 480, "−90% вартості", size=13,
                      fill="#eafaf0", stroke=FIELD, bold=True, min_w=200)
    frags.append(b)
    frags.append(text(996, 528, "масштаб — клонуванням стеку, потоки діляться між копіями",
                      size=11, color=MUTED))

    render(os.path.join(IMG, "prime-collapse.svg"), W, H, *frags,
           title="Куди поділися 90%: конвеєр по мережі згортається в один процес")


def _lnpdf(x, mu, s):
    """Щільність логнормалі — для малюнка хвостів (не гарячий шлях, чистий Python)."""
    if x <= 0 or s <= 0:
        return 0.0
    return math.exp(-(math.log(x) - mu) ** 2 / (2 * s * s)) / (x * s * math.sqrt(2 * math.pi))


def _area(pts):
    """SVG-path з полігона точок (для заливки під кривою)."""
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:]) + " Z"
    return d


def fig_premium_tail():
    """Хвіст не додається лінійно. Дві щільності на спільній осі мс: один мережевий
    стрибок (p50=1, p99=15) і шлях із трьох стрибків поспіль (p50≈4, p99≈28).
    Медіани додаються майже втричі; p99 шляху — між p99 одного (15) і потрійним (45)."""
    W, H = 1240, 660
    frags = []
    x0, x1 = 130, 1150
    xmax = 52.0
    sx = (x1 - x0) / xmax
    xof = lambda ms: x0 + ms * sx
    yA, yB = 320, 582            # базові лінії двох рядків (один стрибок / шлях)
    AMP = 118                    # висота кривої в px (кожна нормована окремо — схема)

    Z99 = 2.326
    # один стрибок: логнормаль, підігнана під p50=1, p99=15
    mu1, s1 = math.log(1.0), math.log(15.0 / 1.0) / Z99
    # шлях = сума трьох (Фентон–Вілкінсон): збігаються середнє й дисперсія
    m = math.exp(mu1 + s1 * s1 / 2)
    v = (math.exp(s1 * s1) - 1) * math.exp(2 * mu1 + s1 * s1)
    M, V = 3 * m, 3 * v
    sig2 = math.log(1 + V / (M * M))
    muP, sP = math.log(M) - sig2 / 2, math.sqrt(sig2)

    def curve(mu, s, base_y, fill, stroke):
        xs = [0.05 + i * 0.1 for i in range(int(xmax / 0.1))]
        ys = [_lnpdf(x, mu, s) for x in xs]
        peak = max(ys) or 1.0
        pts = [(xof(x), base_y - (y / peak) * AMP) for x, y in zip(xs, ys)]
        pts = [(xof(0.05), base_y)] + pts + [(xof(xs[-1]), base_y)]
        return ('<path d="%s" fill="%s" stroke="%s" stroke-width="1.6" '
                'opacity="0.92"/>' % (_area(pts), fill, stroke))

    # осьова лінія часу під нижнім рядком
    frags.append(line(x0, yB, x1 + 8, yB, color=INK, sw=1.6))
    for t in (0, 10, 20, 30, 40, 50):
        frags.append(line(xof(t), yB, xof(t), yB + 7, color=MUTED, sw=1.2))
        frags.append(text(xof(t), yB + 24, "%d" % t, size=12, color=MUTED))
    frags.append(text(x1 + 14, yB + 24, "мс", size=12, color=MUTED, anchor="start"))

    # дві вертикалі крізь обидва рядки: p99 шляху (суцільна) і 3×p99 (штрих, ілюзія)
    xp99 = xof(28.4)
    x3 = xof(45.0)
    frags.append(line(xp99, 150, xp99, yB, color=INK, sw=1.8))
    frags.append(line(x3, 150, x3, yB, color=POS, sw=1.6, dash="7,6"))
    b, _, _ = textbox(xp99, 126, "p99 шляху ≈ 28 мс", size=12.5, fill="#eef2fb",
                      stroke=NEG, bold=True, min_w=180)
    frags.append(b)
    b, _, _ = textbox(x3, 126, "3×p99 = 45 мс\n(лінійна ілюзія — хвіст так не додається)",
                      size=12, fill="#fdecea", stroke=POS, min_w=240)
    frags.append(b)

    # рядок А: один стрибок
    frags.append(curve(mu1, s1, yA, "#eafaf0", FIELD))
    frags.append(text(x0 + 4, yA - AMP - 14, "один мережевий стрибок (RPC)",
                      size=13, color=FIELD, anchor="start", bold=True))
    # p50=1, p99=15 на верхньому рядку
    frags.append(line(xof(1), yA, xof(1), yA + 16, color=FIELD, sw=1.5))
    frags.append(text(xof(1), yA + 32, "p50=1", size=11.5, color=FIELD))
    frags.append(line(xof(15), yA, xof(15), yA - 58, color=INK, sw=1.4, dash="3,4"))
    frags.append(text(xof(15) + 6, yA - 46, "p99 одного = 15 мс", size=11.5,
                      color=INK, anchor="start"))

    # рядок Б: шлях = 3 стрибки поспіль
    frags.append(curve(muP, sP, yB, "#fdecea", POS))
    frags.append(text(x0 + 4, yB - AMP - 14, "шлях: 3 стрибки поспіль (ідентичність→твін→керування)",
                      size=13, color=POS, anchor="start", bold=True))
    frags.append(line(xof(4.22), yB, xof(4.22), yB - 40, color=POS, sw=1.5))
    frags.append(text(xof(4.22), yB - 48, "p50≈4 мс", size=11.5, color=POS))

    # висновок у вільній смузі між рядками (між вертикалями xp99 і x3)
    b, _, _ = textbox(852, 442,
                      "медіани додаються: 1 → 4 мс\n"
                      "хвіст — ні: p99 шляху = 1.9× p99 одного,\n"
                      "але 6.7× власної медіани шляху", size=12,
                      fill=FILL, stroke=LINE, min_w=282)
    frags.append(b)

    render(os.path.join(IMG, "premium-tail.svg"), W, H, *frags,
           title="Хвіст не складається лінійно: p99 шляху лежить між одним стрибком і потрійним")


def fig_premium_surface():
    """Операційна поверхня = фіксований податок на КОЖЕН окремо-розгортуваний сервіс.
    1 деплой проти 9 проти 2 (моноліт + винесена телеметрія). Що коштує — не модулі,
    а зовнішні коробки-деплої: конвеєр · дашборди · чергування на кожну."""
    W, H = 1340, 640
    frags = []

    def deploy(cx, y, w, h, label, color, fillc, cells, ccols):
        out = [rect(cx - w / 2, y, w, h, fill=fillc, stroke=color, sw=2.4, rx=9)]
        out.append(text(cx, y + 22, label, size=12.5, color=INK, bold=True))
        n = len(cells)
        crows = (n + ccols - 1) // ccols
        pad, gap = 16, 10
        gy = y + 34
        cw = (w - 2 * pad - (ccols - 1) * gap) / ccols
        ch = (h - 34 - pad - (crows - 1) * gap) / crows
        for i, nm in enumerate(cells):
            r, c = divmod(i, ccols)
            x = cx - w / 2 + pad + c * (cw + gap)
            yy = gy + r * (ch + gap)
            out.append(fitbox(x, yy, cw, ch, nm, size=11, fill="#ffffff",
                              stroke=MUTED, sw=1.1))
        return "".join(out)

    NINE = ["ідентич.", "твін", "керуван.", "автомат.", "телеметр.",
            "відео", "сповіщ.", "білінг", "хаб"]

    # ── моноліт: ОДНА зовнішня коробка, 9 модулів усередині ──
    frags.append(deploy(250, 96, 320, 320, "1 деплой · 9 модулів", FIELD, "#eafaf0",
                        NINE, 3))
    b, _, _ = textbox(250, 470, "1 конвеєр · 1 набір дашбордів · 1 чергування",
                      size=12.5, fill="#eafaf0", stroke=FIELD, min_w=360)
    frags.append(b)
    frags.append(text(250, 520, "24 год/міс операційного податку", size=13, bold=True))
    frags.append(text(250, 546, "≈ 2% часу команди з 6 інженерів", size=12, color=MUTED))

    # ── повний розкол: ДЕВʼЯТЬ зовнішніх коробок ──
    gx, gy0 = 670, 96
    bw, bh, gp = 118, 92, 14
    for i, nm in enumerate(NINE):
        r, c = divmod(i, 3)
        x = gx + (c - 1) * (bw + gp)
        y = gy0 + r * (bh + gp)
        frags.append(rect(x - bw / 2, y, bw, bh, fill="#fdecea", stroke=POS, sw=2.2, rx=8))
        frags.append(text(x, y + 20, nm, size=11, color=INK, bold=True))
        frags.append(mtext(x, y + 44, ["конвеєр · дашборд", "чергування · патчі"],
                           size=9, color=MUTED, lh=1.35))
    b, _, _ = textbox(gx, 470, "9 конвеєрів · 9 наборів дашбордів · 9 чергувань",
                      size=12.5, fill="#fdecea", stroke=POS, min_w=380)
    frags.append(b)
    frags.append(text(gx, 520, "216 год/міс операційного податку", size=13, bold=True))
    frags.append(text(gx, 546, "≈ 22% часу команди — до першої фічі", size=12, color=POS))

    # ── частковий: ДВІ коробки (моноліт 8 модулів + телеметрія) ──
    cx = 1090
    frags.append(deploy(cx, 96, 300, 214, "моноліт · 8 модулів", FIELD, "#eafaf0",
                        [n for n in NINE if n != "телеметр."], 4))
    frags.append(rect(cx - 150, 330, 300, 78, fill="#fdecea", stroke=POS, sw=2.4, rx=9))
    frags.append(text(cx, 356, "телеметрія", size=12.5, color=INK, bold=True))
    frags.append(text(cx, 384, "власний драйвер запису → окремо", size=11, color=POS))
    b, _, _ = textbox(cx, 470, "2× (конвеєр · дашборди · чергування)",
                      size=12.5, fill="#eef2fb", stroke=NEG, min_w=340)
    frags.append(b)
    frags.append(text(cx, 520, "48 год/міс операційного податку", size=13, bold=True))
    frags.append(text(cx, 546, "≈ 5% часу команди", size=12, color=MUTED))

    render(os.path.join(IMG, "premium-surface.svg"), W, H, *frags,
           title="Операційна поверхня: податок береться з КОЖНОГО деплою, не з кожного модуля")


def fig_premium_crossover():
    """Крива окупності. Вісь X — власний драйвер контексту (додаткові повні репліки,
    що їх вимагає його пік). Дві прямі: тримати в моноліті (u·повна репліка) і
    винести (премія + u·тонка репліка). Перетин — поріг; телеметрія праворуч, читання зліва."""
    W, H = 1200, 620
    frags = []
    x0, x1 = 150, 1090
    yb, yt = 512, 92
    umax, cmax = 16.0, 5600.0
    xof = lambda u: x0 + (u / umax) * (x1 - x0)
    yof = lambda c: yb - (c / cmax) * (yb - yt)

    PREMIUM, C_FULL, C_SLICE = 1920, 350, 110
    keep = lambda u: u * C_FULL
    split = lambda u: PREMIUM + u * C_SLICE
    be = PREMIUM / (C_FULL - C_SLICE)      # 8.0

    # зони ліворуч/праворуч від порогу
    frags.append(rect(x0, yt, xof(be) - x0, yb - yt, fill="#eafaf0", stroke="none", rx=0))
    frags.append(rect(xof(be), yt, x1 - xof(be), yb - yt, fill="#fdecea", stroke="none", rx=0))

    # осі
    frags.append(line(x0, yb, x1 + 8, yb, color=INK, sw=1.8))
    frags.append(line(x0, yb, x0, yt - 8, color=INK, sw=1.8))
    for u in range(0, 17, 2):
        frags.append(line(xof(u), yb, xof(u), yb + 7, color=MUTED, sw=1.1))
        frags.append(text(xof(u), yb + 24, "%d" % u, size=11.5, color=MUTED))
    for c in range(0, 5601, 1400):
        frags.append(line(x0 - 7, yof(c), x0, yof(c), color=MUTED, sw=1.1))
        frags.append(text(x0 - 12, yof(c) + 4, "$%d" % c, size=11, color=MUTED, anchor="end"))
    frags.append(text((x0 + x1) / 2, yb + 46,
                      "власний драйвер контексту — додаткові повні репліки, що їх вимагає пік  →",
                      size=12.5, color=MUTED))
    frags.append(text(x0 - 40, yt - 20, "$/міс", size=12, color=MUTED, anchor="start"))

    # прямі
    frags.append(line(xof(0), yof(keep(0)), xof(umax), yof(keep(umax)), color=POS, sw=2.6))
    frags.append(line(xof(0), yof(split(0)), xof(umax), yof(split(umax)), color=NEG, sw=2.6))

    # поріг — тик униз від перетину, підпис під віссю
    frags.append(line(xof(be), yof(keep(be)), xof(be), yb, color=INK, sw=1.5, dash="6,6"))
    frags.append(circle(xof(be), yof(keep(be)), 5.5, fill=INK, stroke=INK))
    b, _, _ = textbox(xof(be), 210, "поріг = 8 реплік\n= премія / (повна − тонка репліка)",
                      size=11.5, fill="#ffffff", stroke=INK, min_w=252)
    frags.append(b)

    # підписи прямих — біля правих кінців, короткі
    frags.append(text(x1 - 6, yof(keep(15.4)) - 12, "тримати в моноліті",
                      size=12.5, color=POS, anchor="end", bold=True))
    frags.append(text(x1 - 6, yof(split(15.6)) + 26, "винести в сервіс",
                      size=12.5, color=NEG, anchor="end", bold=True))

    # телеметрія: дві точки на прямих + анотація в нижній вільній зоні
    frags.append(circle(xof(12), yof(keep(12)), 5.5, fill=POS, stroke=POS))
    frags.append(circle(xof(12), yof(split(12)), 5.5, fill=NEG, stroke=NEG))
    frags.append(line(xof(12), yof(keep(12)), xof(12), 372, color=MUTED, sw=1.2, dash="3,4"))
    b, _, _ = textbox(892, 406, "телеметрія: драйвер 12\n"
                      "тримати $4200 · винести $3240\n"
                      "→ виносити: −$960/міс і геть із гарячого шляху",
                      size=11.5, fill="#fdecea", stroke=POS, min_w=300)
    frags.append(b)

    # читання: кластер біля нуля, анотація в нижній лівій вільній зоні
    frags.append(circle(xof(0.6), yof(keep(0.6)) + 8, 5, fill=FIELD, stroke=FIELD))
    b, _, _ = textbox(340, 250, "ідентичність · білінг · твін · керування\n"
                      "драйвер 0–1 → частка премії дорожча за виграш\n→ лишаються модулями",
                      size=11.5, fill="#eafaf0", stroke=FIELD, min_w=300)
    frags.append(b)

    render(os.path.join(IMG, "premium-crossover.svg"), W, H, *frags,
           title="Крива окупності: контекст заслуговує розколу, коли власний драйвер переважить премію")


if __name__ == "__main__":
    fig_burden_gate()
    fig_one_way_door()
    fig_pendulum()
    fig_prime_collapse()
    fig_premium_tail()
    fig_premium_surface()
    fig_premium_crossover()
    print("OK: burden-gate.svg, one-way-door.svg, pendulum.svg, prime-collapse.svg, "
          "premium-tail.svg, premium-surface.svg, premium-crossover.svg")
