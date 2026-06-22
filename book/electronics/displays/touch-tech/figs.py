# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори матеріалів (поза основною палітрою svgkit, лише для «фізичних» шарів)
GLASS = "#cfe0ee"; GLASS_S = "#5d7e93"
SKIN  = "#f0d2b4"; SKIN_S  = "#b78a5a"
DRIVE = "#caa24a"; DRIVE_S = "#9a7d2e"   # привід
SENSE = "#5d7e93"; SENSE_S = "#3f5b6d"   # сенс


def finger(cx, top, w=30, h=78):
    """Стилізований палець: видовжена капсула."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
            'fill="%s" stroke="%s" stroke-width="1.5"/>'
            % (cx - w / 2, top, w, h, int(w / 2), SKIN, SKIN_S))


def layer(x, y, w, h, fill=GLASS, stroke=GLASS_S):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="0" '
            'fill="%s" stroke="%s" stroke-width="1.4"/>' % (x, y, w, h, fill, stroke))


# ── overview: дві фізики дотику поруч ─────────────────────────────────────────
# Ідея: ліворуч натиск змикає два шари (механіка), праворуч палець спотворює
# поле електрода (електрика). Одна картинка — джерело всієї подальшої різниці.

def fig_overview():
    W, H = 760, 300
    p = []

    # ── ліво: резистивний ──
    p.append(text(195, 70, "резистивний", size=14, color=INK, bold=True))
    p.append(layer(95, 168, 200, 9))                 # нижній шар
    p.append(layer(95, 130, 200, 9))                 # верхній шар (гнучкий)
    for dx in (40, 76, 124, 160):                     # дистанційні крапки
        p.append(circle(95 + dx, 152, 3, fill=MUTED, stroke=MUTED, sw=1))
    p.append(finger(195, 50, h=80))
    p.append(line(195, 139, 195, 168, color=POS, sw=2.6))  # прогин у точці
    p.append(text(195, 198, "натиск змикає два шари", size=11, color=MUTED))

    # ── право: ємнісний ──
    p.append(text(565, 70, "ємнісний", size=14, color=INK, bold=True))
    p.append(layer(465, 158, 200, 12, fill="#eaf3ff", stroke="#9bbdd6"))  # скло
    p.append(('<rect x="525.0" y="170.0" width="60.0" height="6.0" rx="0" '
              'fill="%s" stroke="%s" stroke-width="1.2"/>' % (DRIVE, DRIVE_S)))  # електрод
    p.append(finger(565, 64, h=78))
    # силові лінії, що тягнуться до пальця
    for ddx, q in ((-15, "M 550 142 Q 545 162 559 173"),
                   (0,   "M 565 142 Q 565 162 565 173"),
                   (15,  "M 580 142 Q 585 162 571 173")):
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4" '
                 'stroke-dasharray="3 3"/>' % (q, FIELD))
    p.append(text(565, 198, "палець міняє поле електрода", size=11, color=MUTED))

    # підсумок
    p.append(text(W / 2, 242, "Резистивний відчуває МЕХАНІЧНИЙ натиск; ємнісний — ЕЛЕКТРИЧНУ присутність пальця.",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 268, "Звідси й уся різниця: чим торкатися, чи є мультитач, яка міцність і чіткість.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "overview.svg"), W, H, *p,
           title="Дві фізики дотику: натиск проти ємності")


# ── resistive: контакт як подільник напруги ──────────────────────────────────
# Ідея: по одному шару — градієнт напруги, другий у точці контакту знімає
# випалу напругу; АЦП перетворює її на координату. Працює будь-чим.

def fig_resistive():
    W, H = 760, 350
    p = []

    # два шари в розрізі
    p.append(finger(240, 24, h=74))
    p.append(layer(90, 112, 380, 9))                  # верхній (гнучкий)
    p.append(text(478, 119, "верхній шар (гнучкий)", size=10, color=GLASS_S, anchor="start"))
    p.append(layer(90, 150, 380, 9))                  # нижній
    p.append(text(478, 157, "нижній шар", size=10, color=GLASS_S, anchor="start"))
    for dx in (40, 110, 180, 250, 320):
        p.append(circle(90 + dx, 134, 3, fill=MUTED, stroke=MUTED, sw=1))
    p.append(line(240, 121, 240, 150, color=POS, sw=2.6))   # точка контакту
    p.append(text(240, 176, "точка контакту", size=10, color=POS, bold=True))

    # градієнт-смуга з дотиком
    gx0, gx1, gy = 90, 470, 250
    p.append(text(90, 224, "по шару X — градієнт напруги:", size=11, color=INK, anchor="start"))
    p.append(line(gx0, gy, gx1, gy, color=INK, sw=3))
    p.append(plus(gx0, gy, r=8))
    p.append(text(gx0, gy + 24, "V₊ (3.3 В)", size=10, color=POS))
    p.append(minus(gx1, gy, r=8))
    p.append(text(gx1, gy + 24, "0 В", size=10, color=NEG))
    # дотик на 1/3 від «+»
    tx = gx0 + (gx1 - gx0) / 3.0
    p.append(line(tx, gy - 18, tx, gy + 10, color=FIELD, sw=2, dash="4 3"))
    p.append(text(tx, gy - 24, "дотик", size=10, color=FIELD, bold=True))
    p.append(line(tx, gy + 24, 560, gy + 24, color=FIELD, sw=1.8))
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (tx, gy + 24, 558, gy + 24, FIELD))
    p.append(text(640, gy - 4, "АЦП читає", size=11, color=INK))
    p.append(text(640, gy + 14, "≈ 2.2 В → X", size=11, color=FIELD, bold=True))
    p.append(text(640, gy + 36, "(потім міняють", size=10, color=MUTED))
    p.append(text(640, gy + 51, "ролі шарів → Y)", size=10, color=MUTED))

    p.append(text(W / 2, 332, "Два виміри подільника (X, тоді Y) дають координату. Працює з будь-чим: палець, рукавиця, стилус, бруд.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "resistive.svg"), W, H, *p,
           title="Резистивний дотик: контакт як подільник напруги")


# ── pcap-mutual: палець краде поле на перетині ────────────────────────────────
# Ідея: на перетині привід/сенс є взаємна ємність Cm (поле «перестрибує»);
# палець відтягує частину поля на себе — Cm падає, контролер бачить провал.

def fig_pcap_mutual():
    W, H = 760, 340
    p = []
    yb = 244  # рівень електродів

    def node(cx, label, touched):
        out = []
        dx, sx = cx - 50, cx + 2
        out.append(('<rect x="%.1f" y="%.1f" width="48" height="10" rx="0" '
                    'fill="%s" stroke="%s" stroke-width="1.2"/>' % (dx, yb, DRIVE, DRIVE_S)))
        out.append(('<rect x="%.1f" y="%.1f" width="48" height="10" rx="0" '
                    'fill="%s" stroke="%s" stroke-width="1.2"/>' % (sx, yb, SENSE, SENSE_S)))
        out.append(text(dx + 24, yb + 24, "привід", size=9.5, color=DRIVE_S))
        out.append(text(sx + 24, yb + 24, "сенс", size=9.5, color=SENSE_S))
        d0, s0 = dx + 24, sx + 24
        if not touched:
            for top in (yb - 60, yb - 100, yb - 140):
                out.append('<path d="M %.0f %d Q %.0f %d %.0f %d" fill="none" stroke="%s" stroke-width="1.5"/>'
                           % (d0, yb, cx, top, s0, yb, FIELD))
            out.append(text(cx, yb + 46, "повна взаємна ємність Cm", size=10.5, color=FIELD, bold=True))
        else:
            out.append(finger(cx, yb - 148, h=78))
            for top in (yb - 48, yb - 76):              # залишок поля
                out.append('<path d="M %.0f %d Q %.0f %d %.0f %d" fill="none" stroke="%s" stroke-width="1.5"/>'
                           % (d0, yb, cx, top, s0, yb, FIELD))
            # частина поля відтягнута на палець
            out.append('<path d="M %.0f %d Q %.0f %d %.0f %d" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 3"/>'
                       % (d0, yb, d0 + 16, yb - 96, cx - 13, yb - 72, POS))
            out.append('<path d="M %.0f %d Q %.0f %d %.0f %d" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 3"/>'
                       % (s0, yb, s0 - 16, yb - 96, cx + 13, yb - 72, POS))
            out.append(text(cx, yb + 46, "Cm падає → дотик помічено", size=10.5, color=POS, bold=True))
        return out

    p.append(text(228, 70, "без пальця", size=12.5, color=INK, bold=True))
    p += node(228, "ні", False)
    p.append(text(560, 70, "палець над перетином", size=12.5, color=INK, bold=True))
    p += node(560, "так", True)

    p.append(line(W / 2 - 6, 80, W / 2 - 6, 300, color="#e4e4e4", sw=1.4, dash="4 5"))
    p.append(text(W / 2, 322, "Контролер веде «привід», слухає «сенс» на кожному перетині рядок×стовпець; провал Cm видає, де торкнулися.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "pcap-mutual.svg"), W, H, *p,
           title="Проєктивно-ємнісний: палець краде поле на перетині")


# ── self-mutual: дві схеми вимірювання ────────────────────────────────────────
# Ідея: self міряє ємність електрода на землю (палець підвищує) — просто, але
# два пальці дають привиди; mutual міряє між рядком і стовпцем (палець знижує) —
# кожен перетин окремий, звідси справжній мультитач.

def fig_self_mutual():
    W, H = 760, 330
    p = []

    # self
    p.append(text(210, 74, "self — ємність на землю", size=12.5, color=INK, bold=True))
    p.append(finger(210, 42, h=78))
    p.append(('<rect x="160.0" y="150.0" width="100" height="9" rx="0" '
              'fill="%s" stroke="%s" stroke-width="1.2"/>' % (DRIVE, DRIVE_S)))
    p.append(text(210, 172, "електрод", size=9.5, color=DRIVE_S))
    for ex in (186, 210, 234):
        p.append('<path d="M %d 122 Q %d 138 %d 150" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="3 3"/>'
                 % (ex, ex, ex, FIELD))
    p.append(text(210, 200, "палець додає ємність до землі (Cs росте)", size=10, color=MUTED))
    p.append(text(210, 224, "просто, але два пальці → «привиди»", size=10.5, color="#b07d18", bold=True))

    # mutual
    p.append(text(560, 74, "mutual — ємність рядок↔стовпець", size=12.5, color=INK, bold=True))
    p.append(finger(560, 42, h=78))
    p.append(('<rect x="500.0" y="150.0" width="44" height="9" rx="0" '
              'fill="%s" stroke="%s" stroke-width="1.2"/>' % (DRIVE, DRIVE_S)))
    p.append(('<rect x="576.0" y="150.0" width="44" height="9" rx="0" '
              'fill="%s" stroke="%s" stroke-width="1.2"/>' % (SENSE, SENSE_S)))
    p.append('<path d="M 522 150 Q 560 120 598 150" fill="none" stroke="%s" stroke-width="1.5"/>' % FIELD)
    p.append('<path d="M 522 150 Q 548 126 552 124" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"/>' % POS)
    p.append(text(560, 200, "палець краде поле між ними (Cm падає)", size=10, color=MUTED))
    p.append(text(560, 224, "кожен перетин окремо → справжній мультитач", size=10.5, color=FIELD, bold=True))

    p.append(text(W / 2, 290, "Тому сучасні екрани — mutual: сітка рядків і стовпців дає повну 2D-карту дотиків, а не одну пляму.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "self-mutual.svg"), W, H, *p,
           title="Дві схеми вимірювання: self проти mutual")


# ── controller: хто робить виміри ─────────────────────────────────────────────
# Ідея: ємнісному потрібен розумний чип (веде сітку, ловить фемтофаради, віддає
# координати по I²C+INT); резистивному вистачає АЦП, аналогову роботу робить МК.

def fig_controller():
    W, H = 760, 330
    p = []

    # ── ємнісний рядок ──
    p.append(text(150, 84, "ємнісний", size=12.5, color=INK, bold=True))
    # сітка електродів
    gx, gy, gw, gh = 70, 100, 160, 70
    p.append(rect(gx, gy, gw, gh, fill="#fbfbfb", stroke=INK, sw=1.6, rx=4))
    for i in range(3):
        yy = gy + 16 + i * 18
        p.append(line(gx + 10, yy, gx + gw - 10, yy, color=DRIVE, sw=1.4))
    for i in range(5):
        xx = gx + 16 + i * 32
        p.append(line(xx, gy + 6, xx, gy + gh - 6, color=SENSE, sw=1.4))
    p.append(text(150, 184, "сітка електродів", size=10, color=MUTED))
    p.append('<line x1="230" y1="135" x2="298" y2="135" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>' % INK)
    p.append(fitbox(300, 104, 150, 62, "контролер\nдотику", size=12, fill="#eef2f5", stroke=INK, sw=1.8, bold=True))
    p.append('<line x1="450" y1="135" x2="538" y2="135" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>' % INK)
    p.append(text(494, 124, "I²C + INT", size=10, color=FIELD, bold=True))
    p.append(fitbox(540, 104, 120, 62, "МК\nчитає (x,y)", size=12, fill="#eef2f5", stroke=INK, sw=1.8, bold=True))
    p.append(text(W / 2 - 20, 196, "чип сам міряє фемтофаради, фільтрує, рахує центр дотику й видає координати",
                  size=10.5, color=MUTED, italic=True))

    # ── резистивний рядок ──
    p.append(text(150, 236, "резистивний", size=12.5, color=INK, bold=True))
    p.append(fitbox(70, 250, 120, 44, "4 дроти", size=11, fill="#fbfbfb", stroke=INK, sw=1.6))
    p.append('<line x1="190" y1="272" x2="248" y2="272" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>' % INK)
    p.append(fitbox(250, 250, 110, 44, "АЦП", size=12, fill="#eef2f5", stroke=INK, sw=1.8, bold=True))
    p.append('<line x1="360" y1="272" x2="418" y2="272" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>' % INK)
    p.append(fitbox(420, 250, 110, 44, "МК", size=12, fill="#eef2f5", stroke=INK, sw=1.8, bold=True))
    p.append(text(620, 272, "МК сам робить аналогову роботу", size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "controller.svg"), W, H, *p,
           title="Контролери: резистивний — АЦП; ємнісний — розумний чип")


# ── compare: карта вибору під виріб ───────────────────────────────────────────
# Ідея: профілі майже дзеркальні; таблиця колонок «чим торкатися / мультитач /
# натиск / чіткість-міцність / середовище» з кольоровими клітинками.

def fig_compare():
    W, H = 800, 280
    p = []
    cols = [
        ("", 120),
        ("Чим торкатися", 130),
        ("Мультитач", 110),
        ("Натиск", 110),
        ("Чіткість/міцність", 150),
        ("Середовище", 150),
    ]
    x0, hy = 20, 66
    # шапка
    x = x0
    xs = []
    for name, w in cols:
        xs.append((x, w))
        p.append(rect(x, hy, w, 36, fill="#eef0f2", stroke=MUTED, sw=1.2, rx=0))
        if name:
            p.append(text(x + w / 2, hy + 22, name, size=11.5, color=INK, bold=True))
        x += w

    GOK, GOKf = FIELD, "#e7f5ea"
    BAD, BADf = POS, "#fdeceb"
    WRN, WRNf = "#b07d18", "#fff8e8"

    def row(y, label, sub, cells):
        p.append(rect(xs[0][0], y, xs[0][1], 64, fill="#f6f7f8", stroke=MUTED, sw=1.2, rx=0))
        p.append(text(xs[0][0] + xs[0][1] / 2, y + (30 if sub else 36), label, size=11.5, color=INK, bold=True))
        if sub:
            p.append(text(xs[0][0] + xs[0][1] / 2, y + 47, sub, size=9.5, color=MUTED))
        for i, (txt, col, fill) in enumerate(cells, start=1):
            cx, cw = xs[i]
            p.append(rect(cx, y, cw, 64, fill=fill, stroke=MUTED, sw=1.2, rx=0))
            p.append(text(cx + cw / 2, y + 36, txt, size=10.5, color=col, bold=True))

    row(102, "резистивний", None, [
        ("будь-чим", GOK, GOKf), ("ні (базово)", BAD, BADf), ("так, тиск", WRN, WRNf),
        ("нижча, мʼякший", BAD, BADf), ("бруд, волога — ок", GOK, GOKf)])
    row(166, "ємнісний", "(PCAP)", [
        ("палець/спец.", WRN, WRNf), ("так", GOK, GOKf), ("ні (дотик)", WRN, WRNf),
        ("скло, чітке", GOK, GOKf), ("боїться води/завад", BAD, BADf)])

    p.append(text(W / 2, 262, "Промисловий пульт у рукавицях — резистивний; споживчий ґаджет із жестами — ємнісний.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "compare.svg"), W, H, *p,
           title="Резистивний проти ємнісного: що під виріб")


if __name__ == "__main__":
    fig_overview()
    fig_resistive()
    fig_pcap_mutual()
    fig_self_mutual()
    fig_controller()
    fig_compare()
    print("OK: figures written to", OUT)
