# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Зумер (окремий)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

HOT = "#c0392b"
COLD = "#2457d6"
CER = "#d6a419"     # кераміка (жовта)
MET = "#9aa4b0"     # металева пластина


def dc_symbol(f, cx, cy):
    """Позначка сталого «плюса» (DC): пряма лінія над пунктиром."""
    f.append(line(cx - 14, cy - 3, cx + 14, cy - 3, color=INK, sw=2.2))
    f.append(line(cx - 14, cy + 3, cx + 14, cy + 3, color=INK, sw=1.4, dash="4 3"))


def square_symbol(f, cx, cy, col=INK):
    """Позначка прямокутної хвилі (AC-пачки): дві періоди меандра."""
    a = 9    # півамплітуда
    w = 8    # піврядок
    x = cx - 2 * w
    y0 = cy
    pts = [(x, y0 + a)]
    for i in range(4):
        pts.append((x, y0 - a) if i % 2 == 0 else (x, y0 + a))
        x += w
        pts.append((x, y0 - a) if i % 2 == 0 else (x, y0 + a))
    d = "M" + " L".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, col))


def sound_waves(f, cx, cy, col=HOT, n=3, r0=16, step=11):
    """Дуги-звук, що розходяться праворуч від точки (cx,cy)."""
    for i in range(n):
        r = r0 + i * step
        f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (cx, cy - r, r, r, cx, cy + r, col))


# ── 1. Дві осі вибору: активний/пасивний і п'єзо/електромагнітний ─────────────
def fig_families():
    W, H = 900, 560
    f = [text(W / 2, 30, "Дві незалежні осі: чим керуємо і чим звучить",
              size=16, bold=True)]

    # ── верх: активний проти пасивного (як керуємо) ──
    f.append(text(W / 2, 62, "1) Що подати на виводи", size=12.5, bold=True, color=MUTED))

    # активний
    ax, ay, aw, ah = 60, 82, 360, 150
    f.append(rect(ax, ay, aw, ah, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(ax + aw / 2, ay + 26, "Активний зумер", size=13, bold=True, color=FIELD))
    dc_symbol(f, ax + 60, ay + 74)
    f.append(text(ax + 60, ay + 100, "сталий +", size=10, color=MUTED))
    # коробочка з генератором усередині
    gx, gy, gw, gh = ax + 130, ay + 52, 110, 46
    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    f.append(text(gx + gw / 2, gy + 20, "генератор", size=10, bold=True))
    f.append(text(gx + gw / 2, gy + 36, "усередині", size=9, color=MUTED))
    sound_waves(f, gx + gw + 22, gy + gh / 2, col=FIELD, n=3, r0=14, step=9)
    f.append(text(ax + aw / 2, ay + ah - 14,
                  "подав живлення → сталий писк однієї ноти", size=10.5, color=INK))

    # пасивний
    px, py, pw, ph = 480, 82, 360, 150
    f.append(rect(px, py, pw, ph, fill="#eef2f8", stroke=COLD, sw=1.8, rx=10))
    f.append(text(px + pw / 2, py + 26, "Пасивний зумер", size=13, bold=True, color=COLD))
    square_symbol(f, px + 60, py + 74, col=COLD)
    f.append(text(px + 60, py + 100, "меандр f", size=10, color=MUTED))
    # гола пластина (без генератора)
    bx2, by2, bw2, bh2 = px + 130, py + 52, 110, 46
    f.append(rect(bx2, by2, bw2, bh2, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    f.append(text(bx2 + bw2 / 2, by2 + 20, "гола", size=10, bold=True))
    f.append(text(bx2 + bw2 / 2, by2 + 36, "пластина", size=9, color=MUTED))
    sound_waves(f, bx2 + bw2 + 22, by2 + bh2 / 2, col=COLD, n=3, r0=14, step=9)
    f.append(text(px + pw / 2, py + ph - 14,
                  "нота = частота меандра → мелодія можлива", size=10.5, color=INK))

    # ── низ: п'єзо проти електромагнітного (чим звучить) ──
    f.append(text(W / 2, 288, "2) Що коливає повітря", size=12.5, bold=True, color=MUTED))

    # п'єзо — розріз диска
    zx, zy, zw, zh = 60, 306, 360, 210
    f.append(rect(zx, zy, zw, zh, fill="#fffaf0", stroke=CER, sw=1.8, rx=10))
    f.append(text(zx + zw / 2, zy + 26, "П'єзо: керамічний диск гнеться",
                  size=12.5, bold=True, color="#9a7400"))
    # розріз: латунна пластина (внизу) + керамічний шар (зверху), вигнуті
    ccx = zx + zw / 2
    baseY = zy + 150
    # латунна пластина (дуга)
    f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="5"/>'
             % (ccx - 110, baseY, ccx, baseY - 34, ccx + 110, baseY, MET))
    # керамічний шар над нею (тонша дуга)
    f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="9"/>'
             % (ccx - 88, baseY - 10, ccx, baseY - 42, ccx + 88, baseY - 10, CER))
    f.append(text(zx + zw - 16, baseY + 6, "латунь", size=9.5, color=MUTED, anchor="end"))
    f.append(text(zx + zw - 16, baseY - 40, "кераміка", size=9.5, color="#9a7400", anchor="end"))
    # стрілки вигину вгору/вниз
    f.append(text(ccx, baseY - 58, "↕", size=22, bold=True, color=HOT))
    f.append(text(ccx, zy + zh - 16,
                  "напруга розтягує кераміку → диск бринить", size=10.5, color=INK))

    # електромагнітний — котушка + мембрана
    ex, ey, ew, eh = 480, 306, 360, 210
    f.append(rect(ex, ey, ew, eh, fill="#f4f6f8", stroke=MET, sw=1.8, rx=10))
    f.append(text(ex + ew / 2, ey + 26, "Електромагнітний: котушка тягне залізо",
                  size=12, bold=True, color="#5a6570"))
    # котушка (кілька витків) + осердя
    coilx = ex + 90
    coilcy = ey + 120
    for i in range(4):
        f.append('<path d="M %.1f %.1f a 9 13 0 1 1 0.1 0" fill="none" '
                 'stroke="%s" stroke-width="2.4"/>' % (coilx + i * 16, coilcy - 13, COLD))
    f.append(line(coilx - 6, coilcy + 15, coilx + 4 * 16, coilcy + 15, color=INK, sw=3))
    f.append(text(coilx + 26, coilcy + 34, "котушка", size=9.5, color=COLD))
    # мембрана-язичок над котушкою
    memy = coilcy - 30
    f.append(line(ex + 60, memy, ex + ew - 40, memy, color="#7a848f", sw=4))
    f.append(text(ex + ew - 44, memy - 8, "залізна мембрана", size=9.5,
                  color="#5a6570", anchor="end"))
    f.append(text(coilx + 4 * 16 + 30, memy + 6, "↕", size=20, bold=True, color=HOT))
    f.append(text(ex + ew / 2, ey + eh - 16,
                  "струм намагнічує → мембрану притягує й відпускає", size=10, color=INK))

    render(os.path.join(IMG, "families.svg"), W, H, *f)


# ── 2. Розводка: активний прямо на GPIO; сильний/електромагн. — через ключ ─────
def fig_wiring():
    W, H = 980, 540
    f = [text(W / 2, 30, "Як під'єднати: слабкий — прямо, гучний — через транзистор",
              size=16, bold=True)]

    # ── ліва схема: активний/п'єзо прямо на вивід ──
    lx = 60
    f.append(text(lx + 175, 66, "Малострумний (п'єзо, кілька мА)",
                  size=12.5, bold=True, color=FIELD))
    # МК
    mx, my, mw, mh = lx, 88, 120, 150
    f.append(rect(mx, my, mw, mh, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(mx + mw / 2, my + 26, "МК", size=13, bold=True))
    f.append(text(mx + mw / 2, my + 46, "вивід IO", size=10, color=MUTED))
    ppy = my + 95
    f.append(circle(mx + mw, ppy, 4, fill=NEG, stroke="none", sw=0))
    f.append(text(mx + mw - 12, ppy - 10, "IO", size=10, color=INK, anchor="end"))
    # провід до «+» зумера
    zx = lx + 250
    f.append(line(mx + mw, ppy, zx, ppy, color=HOT, sw=1.8))
    # зумер (кружечок з + і хвилями)
    f.append(circle(zx + 30, ppy, 30, fill="#ffffff", stroke=INK, sw=2))
    f.append(text(zx + 30, ppy - 4, "BUZ", size=11, bold=True))
    f.append(plus(zx + 12, ppy - 18, r=7))
    sound_waves(f, zx + 62, ppy, col=FIELD, n=2, r0=12, step=8)
    # «−» зумера на землю
    gy = my + mh + 20
    f.append(line(zx + 30, ppy + 30, zx + 30, gy, color=INK, sw=1.8))
    f.append(text(zx + 44, ppy + 46, "−", size=15, bold=True, color=COLD))
    # земля
    def gnd(gx, gyy, col=INK):
        f.append(line(gx, gyy, gx, gyy + 12, color=col, sw=2))
        f.append(line(gx - 14, gyy + 12, gx + 14, gyy + 12, color=col, sw=2.4))
        f.append(line(gx - 9, gyy + 18, gx + 9, gyy + 18, color=col, sw=2.4))
        f.append(line(gx - 4, gyy + 24, gx + 4, gyy + 24, color=col, sw=2.4))
    gnd(zx + 30, gy)
    f.append(text(zx + 30, gy + 40, "GND", size=10, bold=True, color=MUTED))
    b1, _, _ = textbox(lx + 165, 300,
                       "струм < межі виводу → «+» на IO, «−» на GND.\nРезистор не потрібен.",
                       size=10.5, fill="#eef6ef", stroke=FIELD, min_w=320)
    f.append(b1)

    # ── права схема: сильний/електромагнітний через транзистор + діод ──
    rx = 560
    f.append(text(rx + 165, 66, "Сильнострумний (електромагн., 30+ мА)",
                  size=12, bold=True, color=HOT))
    mx2 = rx
    f.append(rect(mx2, my, mw, mh, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(mx2 + mw / 2, my + 26, "МК", size=13, bold=True))
    f.append(text(mx2 + mw / 2, my + 46, "вивід IO", size=10, color=MUTED))
    f.append(circle(mx2 + mw, ppy, 4, fill=NEG, stroke="none", sw=0))
    f.append(text(mx2 + mw - 12, ppy - 10, "IO", size=10, color=INK, anchor="end"))
    # базовий резистор
    br_l, br_r = mx2 + mw + 18, mx2 + mw + 88
    f.append(line(mx2 + mw, ppy, br_l, ppy, color=INK, sw=1.7))
    f.append(rect(br_l, ppy - 9, br_r - br_l, 18, fill="#fff6e5", stroke="#b8860b", sw=1.5, rx=4))
    f.append(text((br_l + br_r) / 2, ppy + 4, "1k", size=10, bold=True, color="#8a6d00"))
    # транзистор (база зліва, колектор угору, емітер униз)
    tx = br_r + 46
    f.append(line(br_r, ppy, tx - 16, ppy, color=INK, sw=1.7))
    f.append(line(tx - 16, ppy - 22, tx - 16, ppy + 22, color=INK, sw=3))  # база-бар
    f.append(line(tx - 16, ppy - 12, tx + 14, ppy - 24, color=INK, sw=1.7))  # колектор
    f.append(line(tx - 16, ppy + 12, tx + 14, ppy + 24, color=INK, sw=1.7))  # емітер
    f.append(text(tx + 20, ppy + 30, "NPN", size=10, bold=True, color=INK))
    # емітер на землю
    f.append(line(tx + 14, ppy + 24, tx + 14, gy, color=INK, sw=1.7))
    gnd(tx + 14, gy)
    # колектор → зумер → +V
    cy_top = my - 8
    f.append(line(tx + 14, ppy - 24, tx + 14, cy_top + 40, color=HOT, sw=1.7))
    # зумер угорі
    bzx = tx + 14
    f.append(circle(bzx, cy_top + 18, 20, fill="#ffffff", stroke=INK, sw=2))
    f.append(text(bzx, cy_top + 22, "BUZ", size=9.5, bold=True))
    # +V шина
    vy = cy_top - 6
    f.append(line(bzx, cy_top - 2, bzx, vy, color=HOT, sw=1.7))
    f.append(line(rx + 40, vy, rx + 300, vy, color=HOT, sw=2))
    f.append(text(rx + 40, vy - 8, "+V", size=11, bold=True, color=HOT))
    # діод-гасник паралельно зумеру (катод до +V)
    ddx = bzx + 70
    f.append(line(bzx, cy_top + 40, ddx, cy_top + 40, color=COLD, sw=1.5))
    f.append(line(ddx, cy_top + 40, ddx, vy, color=COLD, sw=1.5))
    f.append(line(ddx, vy, bzx, vy, color=COLD, sw=1.5))
    # трикутник діода
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (ddx - 7, cy_top + 30, ddx + 7, cy_top + 30, ddx, cy_top + 20, COLD))
    f.append(line(ddx - 8, cy_top + 20, ddx + 8, cy_top + 20, color=COLD, sw=2.2))
    f.append(text(ddx + 26, cy_top + 34, "діод", size=9.5, color=COLD))

    b2, _, _ = textbox(rx + 165, 330,
                       "транзистор бере струм на себе;\nдіод гасить кидок котушки. IO не жаримо.",
                       size=10.5, fill="#fdecea", stroke=HOT, min_w=330)
    f.append(b2)

    b3, _, _ = textbox(W / 2, 430,
                       "Правило: спершу глянь у datasheet струм зумера. Менший за межу виводу — прямо;\nбільший, або будь-який електромагнітний — через ключ і з діодом.",
                       size=11, fill=FILL, stroke=LINE, min_w=760)
    f.append(b3)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 3. Історія: два боки п'єзоефекту (прямий/зворотний) + хто що зробив ────────
def fig_piezo_two_way():
    W, H = 940, 560
    f = [text(W / 2, 32, "Два боки одного ефекту — і хто який відкрив",
              size=16, bold=True)]

    def crystal(cx, cy, bent=0, col=CER):
        """Керамічний диск на латунній пластині; bent<0 — вигин угору, >0 — вниз."""
        half = 78
        # латунна пластина (пряма чи вигнута дугою)
        my = cy
        f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="5"/>'
                 % (cx - half, my, cx, my + bent, cx + half, my, MET))
        # шар кераміки над нею
        f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="9"/>'
                 % (cx - half + 12, my - 9, cx, my - 9 + bent * 1.15,
                    cx + half - 12, my - 9, col))

    # ── ЛІВОРУЧ: прямий ефект (тиск → заряд) ──
    lx, ly, lw, lh = 48, 60, 400, 300
    f.append(rect(lx, ly, lw, lh, fill="#fffaf0", stroke=CER, sw=1.8, rx=12))
    f.append(text(lx + lw / 2, ly + 30, "Прямий ефект", size=14.5, bold=True, color="#9a7400"))
    f.append(text(lx + lw / 2, ly + 52, "тиск  →  заряд", size=12.5, bold=True, color=INK))
    ccx, ccy = lx + lw / 2, ly + 150
    crystal(ccx, ccy, bent=0)
    # стрілки тиску згори (палець тисне)
    f.append(arrow(ccx - 46, ccy - 62, ccx - 46, ccy - 24, color=HOT, sw=2.4))
    f.append(arrow(ccx + 46, ccy - 62, ccx + 46, ccy - 24, color=HOT, sw=2.4))
    f.append(text(ccx, ccy - 70, "стиск", size=11, bold=True, color=HOT))
    # заряди на гранях (виступають)
    f.append(plus(ccx - 92, ccy - 4, r=11))
    f.append(minus(ccx + 92, ccy - 4, r=11))
    f.append(text(lx + lw / 2, ly + lh - 66,
                  "стиснув кристал → на гранях виступає заряд",
                  size=11, color=INK))
    b1, _, _ = textbox(lx + lw / 2, ly + lh - 34,
                       "запальничка, мікрофон, датчик удару",
                       size=10.5, fill="#fff6e0", stroke=CER, min_w=300)
    f.append(b1)

    # ── ПРАВОРУЧ: зворотний ефект (напруга → вигин) ──
    rx, ry, rw, rh = 492, 60, 400, 300
    f.append(rect(rx, ry, rw, rh, fill="#eef2f8", stroke=COLD, sw=1.8, rx=12))
    f.append(text(rx + rw / 2, ry + 30, "Зворотний ефект", size=14.5, bold=True, color=COLD))
    f.append(text(rx + rw / 2, ry + 52, "напруга  →  деформація", size=12.5, bold=True, color=INK))
    rcx, rcy = rx + rw / 2, ry + 150
    crystal(rcx, rcy, bent=-30, col=CER)
    # джерело напруги ліворуч від диска
    f.append(plus(rcx - 96, rcy - 6, r=11))
    f.append(minus(rcx - 96, rcy + 22, r=11))
    f.append(line(rcx - 84, rcy - 6, rcx - 60, rcy - 6, color=HOT, sw=1.8))
    f.append(line(rcx - 84, rcy + 22, rcx - 60, rcy + 22, color=COLD, sw=1.8))
    f.append(text(rcx - 96, rcy + 46, "напруга", size=10.5, bold=True, color=INK))
    # стрілка вигину вгору
    f.append(text(rcx + 96, rcy - 26, "↑ вигин", size=12, bold=True, color=HOT))
    f.append(text(rx + rw / 2, ry + rh - 66,
                  "подав напругу → диск сам вигинається, штовхає повітря",
                  size=10.5, color=INK))
    b2, _, _ = textbox(rx + rw / 2, ry + rh - 34,
                       "ЗУМЕР — саме цей бік",
                       size=11, bold=True, fill="#dfeafc", stroke=COLD, min_w=300)
    f.append(b2)

    # двобічна стрілка «оборотність» між панелями
    my = ly + 150
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
             'stroke-width="2.6" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
             % (lx + lw + 6, my, rx - 6, my, MUTED))
    f.append(text((lx + lw + rx) / 2, my - 12, "оборотно", size=10.5, bold=True, color=MUTED))

    # ── стрічка атрибуції внизу ──
    yb = 400
    f.append(text(W / 2, yb, "Хто що зробив — честь спільна", size=13, bold=True, color=MUTED))
    c1, _, _ = textbox(210, yb + 62,
                       "БРАТИ КЮРІ, 1880\n(французи, Париж)\nпрямий ефект:\nідея з симетрії + дослід",
                       size=10.5, fill="#fffaf0", stroke=CER, min_w=250)
    f.append(c1)
    c2, _, _ = textbox(W / 2, yb + 62,
                       "ЛІППМАН, 1881\nпередбачив зворотний\nефект — із термодинаміки\n(на папері, не руками)",
                       size=10.5, fill="#eef2f8", stroke=COLD, min_w=250)
    f.append(c2)
    c3, _, _ = textbox(W - 210, yb + 62,
                       "БРАТИ КЮРІ, 1881\nпідтвердили зворотний\nдослідом і довели\nповну оборотність",
                       size=10.5, fill="#fffaf0", stroke=CER, min_w=250)
    f.append(c3)

    render(os.path.join(IMG, "piezo-two-way.svg"), W, H, *f)


# ── 4. Блокувальна (delay) vs неблокувальна (millis) мелодія на осі часу ──────
def fig_nonblocking():
    W, H = 940, 470
    f = [text(W / 2, 32, "Мелодія з delay() глушить пристрій; на millis() — ні",
              size=16, bold=True)]

    # спільна геометрія трьох нот на осі часу
    t0 = 120                 # ліва межа осі
    tW = 640                 # повна ширина осі
    # три ноти різної тривалості (частки повної осі) + хвіст «тиша»
    segs = [0.28, 0.20, 0.34, 0.18]     # нота1, нота2, нота3, вільно
    names = ["нота: мі 300 мс", "фа 200 мс", "соль 350 мс", ""]
    xs = [t0]
    for s in segs:
        xs.append(xs[-1] + s * tW)

    # ── верхня доріжка: delay() ──
    topY = 96
    f.append(text(t0 - 8, topY - 26, "З delay():", size=12.5, bold=True,
                  color=HOT, anchor="start"))
    barH = 30
    # суцільні смуги «зумер грає + процесор глухий» на кожну ноту
    for i in range(3):
        x, w = xs[i], xs[i + 1] - xs[i]
        f.append(rect(x, topY, w, barH, fill="#fdecea", stroke=HOT, sw=1.6, rx=5))
        f.append(text(x + w / 2, topY + 20, "зумер + процесор ЗАЙНЯТИЙ",
                      size=9, color="#a02", bold=False)
                 if w > 150 else
                 text(x + w / 2, topY + 20, "зайнято", size=9, color="#a02"))
    # підписи нот НАД смугами (з запасом, кожен над своєю)
    for i in range(3):
        cx = (xs[i] + xs[i + 1]) / 2
        f.append(text(cx, topY - 8, names[i], size=9.5, color=MUTED))
    # вирок унизу доріжки
    f.append(text(t0 - 8, topY + barH + 22,
                  "кнопки/датчики/зв'язок стоять весь цей час",
                  size=10, color="#a02", anchor="start", italic=True))

    # ── нижня доріжка: millis() ──
    botY = 236
    f.append(text(t0 - 8, botY - 26, "На millis():", size=12.5, bold=True,
                  color=FIELD, anchor="start"))
    # тонка вісь часу
    f.append(line(t0, botY + 14, t0 + tW, botY + 14, color=INK, sw=2))
    f.append(text(t0 + tW + 8, botY + 18, "час", size=10, color=MUTED, anchor="start"))
    # позначки «перемкнув ноту» на межах нот (тонкі, майже нуль часу)
    tick_names = ["мі", "фа", "соль", "стоп"]
    for i in range(4):
        x = xs[i]
        f.append(line(x, botY + 4, x, botY + 24, color=FIELD, sw=2.4))
        f.append(text(x, botY - 2, "↧", size=13, color=FIELD, bold=True))
        f.append(text(x, botY - 14, tick_names[i], size=9, color=FIELD))
    # у ПРОМІЖКАХ між нотами процесор вільний → дрібні справи
    tasks = ["читає кнопку", "опитує датчик", "веде зв'язок"]
    for i in range(3):
        cx = (xs[i] + xs[i + 1]) / 2
        f.append(circle(cx, botY + 40, 3.5, fill=FIELD, stroke="none", sw=0))
        f.append(text(cx, botY + 58, tasks[i], size=9, color="#1a7a44"))
    f.append(text(t0 - 8, botY + 40, "вільно:", size=9.5, color="#1a7a44",
                  anchor="start", italic=True))

    # легенда-висновок під обома доріжками (широкі рамки, текст не тисне)
    b1, w1, _ = textbox(t0 + 175, 360,
                        "delay(200) — це «нічого не роби 200 мс».\nУвесь час ноти процесор глухий.",
                        size=10.5, fill="#fdecea", stroke=HOT, min_w=340)
    f.append(b1)
    b2, w2, _ = textbox(t0 + 175, 424,
                        "update() лише зазирає на годинник і йде.\nМіж нотами пристрій робить своє.",
                        size=10.5, fill="#eef6ef", stroke=FIELD, min_w=340)
    f.append(b2)

    render(os.path.join(IMG, "nonblocking.svg"), W, H, *f)


if __name__ == "__main__":
    fig_families()
    fig_wiring()
    fig_piezo_two_way()
    fig_nonblocking()
    print("OK: 4 figures ->", IMG)
