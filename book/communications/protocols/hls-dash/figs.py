# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

KEY  = "#c0392b"     # ключовий кадр — гарячий
KEYF = "#fdecea"
DEP  = "#2457d6"     # залежний кадр
DEPF = "#eaf0fd"
OKC  = "#27ae60"
OKF  = "#eafaf0"
BADF = "#f8f8f8"


# ── segment-cut: чому різати можна лише перед ключовим кадром ────────────────
# Ідея: кадри посилаються назад; розріз, що перетинає посилання, робить шматок
# нерозбірним. Лише перед ключовим кадром жодного посилання не перетнуто.

def fig_cut():
    W, H = 1000, 460
    p = []

    def strip(y, cut_at, label, ok):
        """Смуга з 10 кадрів; cut_at — індекс кадра, ПЕРЕД яким проходить розріз."""
        x0, bw, gap = 90, 68, 12
        out = []
        kinds = [0, 1, 1, 1, 1, 0, 1, 1, 1, 1]   # 0 — ключовий, 1 — залежний
        for i, k in enumerate(kinds):
            x = x0 + i * (bw + gap)
            if k == 0:
                out.append(rect(x, y, bw, 46, fill=KEYF, stroke=KEY, sw=2))
                out.append(text(x + bw / 2, y + 30, "ключ", size=13, color=KEY, bold=True))
            else:
                out.append(rect(x, y, bw, 46, fill=DEPF, stroke=DEP, sw=1.4))
                out.append(text(x + bw / 2, y + 30, "різн.", size=13, color=DEP))
        # дуги-посилання назад: кожен залежний дивиться на попередній
        for i, k in enumerate(kinds):
            if k == 0:
                continue
            xa = x0 + i * (bw + gap) + 6
            xb = x0 + (i - 1) * (bw + gap) + bw - 6
            out.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
                       'stroke="%s" stroke-width="1.4" marker-end="url(#arrow)"/>'
                       % (xa, y - 6, xa, y - 34, xb, y - 34, xb, y - 6, DEP))
        # розріз
        xc = x0 + cut_at * (bw + gap) - gap / 2
        col = OKC if ok else KEY
        out.append(line(xc, y - 46, xc, y + 66, color=col, sw=3, dash="7 5"))
        out.append(text(xc, y + 86, label, size=13, color=col, bold=True))
        return "".join(out)

    p.append(text(60, 46, "Розріз посеред групи — посилання ведуть у нікуди",
                  size=15, anchor="start", bold=True, color=KEY))
    p.append(strip(120, 3, "тут шматок не відкриється", ok=False))

    p.append(text(60, 286, "Розріз перед ключовим кадром — жодного перетнутого посилання",
                  size=15, anchor="start", bold=True, color=OKC))
    p.append(strip(360, 5, "тут шматок самодостатній", ok=True))

    p.append(text(60, 176, "посилання назад", size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "segment-cut.svg"), W, H, *p)


# ── abr-ladder: взаємозамінні сегменти й вибір копії на кожному стику ────────
# Ідея: копії вирівняні до кадра, тож маршрут клієнта може стрибати рядками.

def fig_ladder():
    W, H = 1020, 430
    x0, sw_, gap = 250, 112, 10
    rows = [
        ("висока  5 Мбіт/с  1080p", 110, "#eafaf0", OKC),
        ("середня 2 Мбіт/с   720p", 210, "#fdf6e3", "#b08900"),
        ("низька  0.7 Мбіт/с 360p", 310, DEPF, DEP),
    ]
    p = []
    p.append(text(x0, 58, "той самий час, три копії", size=14, color=MUTED, anchor="start"))

    for i in range(6):
        x = x0 + i * (sw_ + gap)
        p.append(text(x + sw_ / 2, 84, "сегмент %d" % (i + 1), size=12, color=MUTED))

    for name, y, fill, col in rows:
        p.append(text(x0 - 24, y + 28, name, size=13, anchor="end"))
        for i in range(6):
            x = x0 + i * (sw_ + gap)
            p.append(rect(x, y, sw_, 46, fill=fill, stroke=col, sw=1.4))

    # маршрут клієнта: 1-2 середня, 3-4 висока, 5-6 низька
    route = [(0, 210), (1, 210), (2, 110), (3, 110), (4, 310), (5, 310)]
    pts = []
    for i, y in route:
        x = x0 + i * (sw_ + gap) + sw_ / 2
        pts.append((x, y + 23))
    d = "M %.1f %.1f" % pts[0]
    for q in pts[1:]:
        d += " L %.1f %.1f" % q
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.5" opacity="0.85"/>' % (d, KEY))
    for x, y in pts:
        p.append(circle(x, y, 7, fill=KEY, stroke=KEY, sw=1))

    p.append(text(x0, 388, "червона нитка — що саме завантажив клієнт; вибір робиться заново на кожному стику",
                  size=13, color=KEY, anchor="start"))

    render(os.path.join(OUT, "abr-ladder.svg"), W, H, *p)


# ── latency-budget: з чого складається запізнення і що міняють частини ───────
# Ідея: доданки затримки видно як відрізки однієї осі; дрібніші одиниці
# скорочують перші два доданки й дозволяють міряти буфер частками секунди.

def fig_latency():
    W, H = 1060, 400
    p = []

    def bar(y, title, items, scale):
        out = [text(60, y - 18, title, size=15, anchor="start", bold=True)]
        x = 60
        for label, secs, fill, col in items:
            w = secs * scale
            out.append(rect(x, y, w, 52, fill=fill, stroke=col, sw=1.6))
            out.append(text(x + w / 2, y + 32, label, size=13, color=col, bold=True))
            x += w
        out.append(text(x + 18, y + 32, "разом ≈ %.0f с" % sum(s for _, s, _, _ in items),
                        size=14, anchor="start", bold=True))
        return "".join(out), x

    seg = [("сегмент\n6 с", 6, KEYF, KEY),
           ("список\n3 с", 3, "#fdf6e3", "#b08900"),
           ("буфер 3 сегменти\n18 с", 18, DEPF, DEP)]
    # мітки в дві лінії робимо окремо, щоб не тиснути в вузьку рамку
    seg_flat = [("6 с", 6, KEYF, KEY), ("3 с", 3, "#fdf6e3", "#b08900"),
                ("18 с", 18, DEPF, DEP)]
    frag, endx = bar(96, "Цілими сегментами", seg_flat, 28)
    p.append(frag)
    names = [("чекаємо кінця сегмента", 6, 0), ("поява у списку", 3, 6), ("буфер відтворення", 18, 9)]
    for nm, secs, off in names:
        cx = 60 + (off + secs / 2) * 28
        p.append(text(cx, 176, nm, size=12, color=MUTED))

    llf = [("0.5 с", 0.5, KEYF, KEY), ("0 с", 0.4, "#fdf6e3", "#b08900"),
           ("2 с", 2.0, DEPF, DEP)]
    frag2, _ = bar(266, "Частинами по 0.5 с", llf, 28)
    p.append(frag2)
    p.append(text(60, 350, "частина дописується за півсекунди · список віддають у мить її появи · буфер міряють частинами",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "latency-budget.svg"), W, H, *p)


# ── history-timeline: три смуги подій — власницькі варіанти, стандарти, зближення
# Ідея: фрагментація йшла попереду стандартів, а зближення прийшло останнім.

def fig_timeline():
    W, H = 1300, 480
    p = []

    X0, XPY = 240.0, 78.3          # x року 2006 і крок на рік
    def xy(year):
        return X0 + (year - 2006) * XPY

    BW, BH = 154, 54               # коробка події

    lanes = [
        (110, ["власницькі", "варіанти"], "#f4f4f4", MUTED, [
            (2006, ["2006 · Move Networks", "плагін у браузері"]),
            (2008, ["2008 · Smooth Streaming", "Silverlight, Пекін"]),
            (2010, ["2010 · Adobe HDS", "Flash, формат F4F"]),
        ]),
        (240, ["стандарти"], DEPF, DEP, [
            (2009, ["2009 · HLS", "iPhone OS 3.0, чернетка"]),
            (2012, ["2012 · DASH", "ISO/IEC 23009-1"]),
            (2017, ["2017 · RFC 8216", "HLS як RFC"]),
        ]),
        (370, ["зближення"], OKF, OKC, [
            (2016, ["2016 · fMP4 у HLS", "заявка до MPEG"]),
            (2018, ["2018 · CMAF", "ISO/IEC 23000-19"]),
        ]),
    ]

    for y, cap, fill, stroke, events in lanes:
        p.append(line(210, y, 1255, y, color="#cccccc", sw=1.5))
        p.append(mtext(16, y - 2, cap, size=12, color=MUTED, anchor="start"))
        for year, lines in events:
            cx = xy(year)
            p.append(circle(cx, y, 6, fill=stroke, stroke=stroke, sw=1))
            p.append(line(cx, y - 6, cx, y - 19, color=stroke, sw=1.5))
            by = y - 19 - BH
            p.append(rect(cx - BW / 2, by, BW, BH, fill=fill, stroke=stroke, sw=1.5))
            p.append(mtext(cx, by + 22, lines, size=11, color=INK, lh=1.6))

    # вісь років
    p.append(line(210, 440, 1255, 440, color=LINE, sw=1.5))
    for year in range(2006, 2019, 2):
        cx = xy(year)
        p.append(line(cx, 440, cx, 447, color=LINE, sw=1.5))
        p.append(text(cx, 464, str(year), size=12, color=MUTED))

    render(os.path.join(OUT, "history-timeline.svg"), W, H, *p)


# ── manifest-shape: HLS — дерево файлів, DASH — дерево елементів ─────────────
# Ідея: та сама ієрархія «набір копій → копія → сегменти» в HLS розкладена по
# окремих ресурсах, а в DASH згорнута у вкладені елементи одного документа.

def fig_shape():
    W, H = 1100, 560
    STEP, BH = 56, 38

    def tree(x0, right, y0, indent, rows, stroke, fill, head):
        out = [text(x0, y0 - 26, head, size=15, anchor="start", bold=True, color=stroke)]
        geom = []          # (level, x, y)
        for i, (lvl, label, soft) in enumerate(rows):
            x = x0 + lvl * indent
            y = y0 + i * STEP
            w = right - x
            out.append(rect(x, y, w, BH, fill=(BADF if soft else fill),
                            stroke=("#b9b9b9" if soft else stroke),
                            sw=(1.2 if soft else 1.6)))
            out.append(fitbox(x, y, w, BH, label, size=12,
                              color=(MUTED if soft else INK)))
            # коліно від найближчого предка вище
            for j in range(i - 1, -1, -1):
                plvl, px, py = geom[j]
                if plvl == lvl - 1:
                    vx = px + 14
                    out.append(line(vx, py + BH, vx, y + BH / 2, color="#b0b0b0", sw=1.2))
                    out.append(line(vx, y + BH / 2, x, y + BH / 2, color="#b0b0b0", sw=1.2))
                    break
            geom.append((lvl, x, y))
        return "".join(out)

    hls = [
        (0, "master.m3u8 — мультиваріантний плейлист", False),
        (1, "v1080/index.m3u8 — медіаплейлист копії", False),
        (2, "init.mp4 · seg1427.m4s · seg1428.m4s …", True),
        (1, "v720/index.m3u8 — медіаплейлист копії", False),
        (2, "init.mp4 · seg1427.m4s · seg1428.m4s …", True),
        (1, "audio/uk.m3u8 — оголошений EXT-X-MEDIA", False),
        (2, "init.mp4 · seg1427.m4s · seg1428.m4s …", True),
    ]
    dash = [
        (0, "MPD  type=dynamic", False),
        (1, "Period  start=PT0S", False),
        (2, "AdaptationSet  contentType=video", False),
        (3, "SegmentTemplate  media=… duration=…", False),
        (3, "Representation  id=v1080  5.2 Мбіт/с", False),
        (3, "Representation  id=v720  2.1 Мбіт/с", False),
        (2, "AdaptationSet  contentType=audio lang=uk", False),
        (3, "Representation  id=a-uk  128 кбіт/с", False),
    ]

    p = [tree(50, 510, 90, 34, hls, DEP, DEPF, "HLS — по ресурсу на кожну доріжку"),
         tree(590, 1060, 90, 30, dash, OKC, OKF, "DASH — один документ, вкладені елементи")]

    p.append(mtext(50, 560, ["сірим — сегменти: у плейлисті вони перелічені",
                             "поіменно, рядок за рядком"],
                   size=12, color=MUTED, anchor="start"))
    p.append(mtext(590, 560, ["сегменти не перелічені зовсім: їхні адреси",
                              "клієнт складає з шаблона й номера"],
                   size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "manifest-shape.svg"), W, H, *p)


# ── abr-oscillation: чому «дивитись лише на швидкість» гойдає якість ─────────
# Ідея: оцінка швидкості шумить довкола межі між двома копіями; правило-сходинка
# від шумного числа клацає на кожному перетині. Дві різні межі (угору й униз)
# роблять смугу нечутливості, і клацання зникає.

def fig_oscillation():
    W, H = 1150, 560
    p = []

    EST = [5.6, 4.8, 5.5, 4.7, 5.3, 4.9, 5.6, 4.6, 5.2, 5.0, 5.5, 4.8, 5.4, 5.1]
    X0, STEP = 150.0, 62.0
    xs = [X0 + i * STEP for i in range(len(EST))]
    yv = lambda v: 250.0 - (v - 4.0) * 50.0        # 4 Мбіт/с → 250, 7 → 100

    p.append(text(60, 62, "Оцінка швидкості по останніх завантаженнях гуляє довкола 5.2 Мбіт/с",
                  size=14, anchor="start", bold=True))

    # шкала
    for v in (4, 5, 6, 7):
        p.append(text(118, yv(v) + 4, str(v), size=11, color=MUTED, anchor="end"))
    p.append(text(118, 78, "Мбіт/с", size=11, color=MUTED, anchor="end"))

    # дві межі
    p.append(line(130, yv(5.0), 980, yv(5.0), color=KEY, sw=1.6, dash="7 5"))
    p.append(mtext(996, yv(5.0) - 4, ["5.0 Мбіт/с — бітрейт", "копії 1080p"],
                   size=11, color=KEY, anchor="start", lh=1.5))
    p.append(line(130, yv(6.25), 980, yv(6.25), color=OKC, sw=1.6, dash="7 5"))
    p.append(mtext(996, yv(6.25) - 4, ["6.25 Мбіт/с — стільки", "треба, щоб піднятись"],
                   size=11, color=OKC, anchor="start", lh=1.5))

    # крива оцінок
    pts = " ".join("%.1f,%.1f" % (x, yv(v)) for x, v in zip(xs, EST))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (pts, DEP))
    for x, v in zip(xs, EST):
        p.append(circle(x, yv(v), 4, fill=DEP, stroke=DEP, sw=1))

    # два рядки рішень
    def row(y, label, color, picks):
        out = [text(122, y - 16, label, size=13, anchor="start", bold=True, color=color)]
        for x, hi in zip(xs, picks):
            f, s, t = (DEPF, DEP, "1080") if hi else (BADF, MUTED, "720")
            out.append(rect(x - 27, y, 54, 44, fill=f, stroke=s, sw=1.4))
            out.append(text(x, y + 27, t, size=12, color=s))
        return "".join(out)

    naive = [v >= 5.0 for v in EST]                 # найвища копія з бітрейтом ≤ оцінки
    steady = [False] * len(EST)                     # угору треба 6.25 — жодна оцінка не дотягла

    p.append(row(316, "вибір за самою швидкістю — 11 перемикань на 14 сегментів", KEY, naive))
    p.append(row(434, "з гістерезисом і порогом буфера — жодного перемикання", OKC, steady))

    for i, x in enumerate(xs):
        p.append(text(x, 502, str(i + 1), size=11, color=MUTED))
    p.append(text(122, 530, "номер сегмента", size=11, anchor="start", color=MUTED))

    render(os.path.join(OUT, "abr-oscillation.svg"), W, H, *p)


fig_cut()
fig_ladder()
fig_latency()
fig_timeline()
fig_shape()
fig_oscillation()
print("ok")
