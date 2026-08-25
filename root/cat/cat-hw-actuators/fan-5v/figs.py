# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «5V безколекторні вентилятори».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що всередині: магніт-дзвін + котушки + мікросхема з Холлом ──────────────
def fig_fan_inside():
    W, H = 900, 520
    f = [text(W / 2, 30, "Усередині вентилятора: магніт-ротор, котушки й одна мікросхема",
              size=16, bold=True)]

    # Ротор-дзвін: зовнішнє кільце з магнітними полюсами N/S по колу
    cx, cy = 250, 270
    Rout, Rin = 130, 96
    f.append(circle(cx, cy, Rout, fill="#f4f6f8", stroke=INK, sw=2.0))
    f.append(circle(cx, cy, Rin, fill=BG, stroke=MUTED, sw=1.4))
    # чотири полюси по колу (2 пари) — N червоні, S сині, з запасом між написами
    import math
    poles = [("N", 90, POS), ("S", 0, NEG), ("N", 270, POS), ("S", 180, NEG)]
    for tag, ang, col in poles:
        a = math.radians(ang)
        rr = (Rout + Rin) / 2
        px = cx + rr * math.cos(a)
        py = cy - rr * math.sin(a)
        f.append(text(px, py + 6, tag, size=17, bold=True, color=col))
    f.append(text(cx, cy - Rout - 12, "ротор — кільцевий магніт (крильчатка зверху)",
                  size=11, bold=True))

    # Статор усередині — чотири зубці з обмоткою
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        x1 = cx + 20 * math.cos(a); y1 = cy - 20 * math.sin(a)
        x2 = cx + 70 * math.cos(a); y2 = cy - 70 * math.sin(a)
        f.append(line(x1, y1, x2, y2, color=FIELD, sw=6))
    f.append(circle(cx, cy, 20, fill="#eef6ef", stroke=FIELD, sw=1.6))
    f.append(text(cx, cy + 4, "вісь", size=9, color="#1e5631"))
    f.append(text(cx, cy + Rin - 14, "статор:", size=10, bold=True, color="#1e5631"))
    f.append(text(cx, cy + Rin + 1, "котушки", size=10, bold=True, color="#1e5631"))

    # Мікросхема-драйвер праворуч
    dx, dy = 640, 200
    dw, dh = 190, 110
    f.append(rect(dx - dw / 2, dy - dh / 2, dw, dh, fill="#eef2f8", stroke=NEG, sw=1.9, rx=10))
    f.append(text(dx, dy - 30, "драйвер-мікросхема", size=12, bold=True, color=NEG))
    f.append(text(dx, dy - 12, "(H-міст + логіка)", size=9.5, color=MUTED))
    # Холл усередині драйвера
    f.append(rect(dx - 40, dy + 2, 80, 30, fill=BG, stroke=POS, sw=1.5, rx=6))
    f.append(text(dx, dy + 21, "давач Холла", size=10, bold=True, color=POS))

    # стрілка: Холл «бачить» полюс ротора
    f.append(arrow(dx - dw / 2 - 6, dy + 16, cx + Rout + 8, cy - 30, color=POS, sw=1.8))
    f.append(text((dx - dw / 2 + cx + Rout) / 2 + 4, dy - 6,
                  "бачить, який полюс поруч", size=9.5, color=POS, bold=True))

    # стрілка: драйвер жене струм у котушки
    f.append(arrow(dx - dw / 2 - 6, dy + 44, cx + 40, cy + 60, color=FIELD, sw=2.2))
    f.append(text((dx - dw / 2 + cx) / 2 + 30, dy + 78,
                  "перемикає струм", size=9.5, color=FIELD, bold=True))
    f.append(text((dx - dw / 2 + cx) / 2 + 30, dy + 93,
                  "у котушках", size=9.5, color=FIELD, bold=True))

    # Живлення до драйвера
    f.append(text(dx, dy + dh / 2 + 24, "+5 В / GND", size=11, bold=True, color=INK))

    b, _, _ = textbox(W / 2, H - 34,
                      "полюс наблизився → Холл це відчув → драйвер штовхнув котушку в потрібний бік → ротор крутиться далі",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "fan-inside.svg"), W, H, *f)


# ── 2. Скільки проводів: 2 / 3 / 4 — що додає кожен ────────────────────────────
def fig_wire_counts():
    W, H = 940, 470
    f = [text(W / 2, 30, "Скільки проводів у вентилятора й що додає кожен",
              size=16, bold=True)]

    panelW = 280
    gap = 25
    total = 3 * panelW + 2 * gap
    x0 = (W - total) / 2
    top = 62
    boxH = 330

    def panel(px, title, sub, accent, fill, wires, note):
        f.append(rect(px, top, panelW, boxH, fill=fill, stroke=accent, sw=1.8, rx=10))
        f.append(text(px + panelW / 2, top + 26, title, size=15, bold=True, color=accent))
        f.append(text(px + panelW / 2, top + 45, sub, size=10, color=MUTED))
        wy = top + 78
        for name, desc, col in wires:
            # кольорова точка + назва проводу + що це
            f.append(circle(px + 30, wy, 6, fill=col, stroke=col, sw=1))
            f.append(text(px + 46, wy + 4, name, size=11.5, bold=True, color=col, anchor="start"))
            f.append(text(px + 46, wy + 22, desc, size=9, color=MUTED, anchor="start"))
            wy += 50
        nb, _, _ = textbox(px + panelW / 2, top + boxH - 30, note,
                           size=10, fill=BG, stroke=accent)
        f.append(nb)

    panel(x0, "2 проводи", "найдешевший", NEG, "#eef2f8",
          [("+5 В (черв.)", "живлення", POS),
           ("GND (чорн.)", "земля", INK)],
          "крутиться на повну; ні\nкерування, ні зворотного зв'язку")

    panel(x0 + panelW + gap, "3 проводи", "+ тахометр", FIELD, "#eef6ef",
          [("+5 В (черв.)", "живлення", POS),
           ("GND (чорн.)", "земля", INK),
           ("TACH (жовт.)", "імпульси обертів", FIELD)],
          "видно швидкість; керувати —\nлише напругою живлення")

    panel(x0 + 2 * (panelW + gap), "4 проводи", "+ окремий PWM", POS, "#fdecea",
          [("+5 В (черв.)", "живлення (завжди)", POS),
           ("GND (чорн.)", "земля", INK),
           ("TACH (жовт.)", "імпульси обертів", FIELD),
           ("PWM (синій)", "керування швидкістю", NEG)],
          "живлення не рвемо; швидкість\nзадає окремий сигнал ~25 кГц")

    render(os.path.join(IMG, "wire-counts.svg"), W, H, *f)


# ── 3. Розводка 4-проводового 5V-вентилятора до мікроконтролера ────────────────
def fig_wiring():
    W, H = 920, 560
    f = [text(W / 2, 30, "Розводка 4-проводового 5V-вентилятора до мікроконтролера",
              size=16, bold=True)]

    # Вентилятор ліворуч — колонка з чотирма проводами
    lx = 70
    boxW = 165
    pins = [
        ("+5 В  (черв.)", "5V живлення", POS),
        ("GND  (чорн.)", "GND", INK),
        ("PWM  (синій)", "вивід МК (PWM ~25 кГц)", NEG),
        ("TACH  (жовт.)", "вивід МК (вхід-лічильник)", FIELD),
    ]
    n = len(pins)
    rowH = 62
    top = 96
    f.append(rect(lx - 12, top - 16, boxW + 24, n * rowH + 20, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(lx + boxW / 2, top - 28, "5V вентилятор", size=12, bold=True, color="#1e5631"))

    rx = lx + boxW + 300
    f.append(rect(rx - 12, top - 16, 210, n * rowH + 20, fill="#eef2f8", stroke=INK, sw=1.6, rx=10))
    f.append(text(rx + 95, top - 28, "мікроконтролер", size=12, bold=True))

    for i, (pin, dest, col) in enumerate(pins):
        y = top + i * rowH + rowH / 2
        f.append(text(lx + 2, y + 4, pin, size=11, bold=True, anchor="start"))
        px_out = lx + boxW
        f.append(circle(px_out, y, 4, fill=col, stroke=col, sw=1))
        f.append(text(rx + 6, y + 4, dest, size=10, color=col, anchor="start", bold=True))
        px_in = rx
        f.append(circle(px_in, y, 4, fill=col, stroke=col, sw=1))
        f.append(line(px_out, y, px_in, y, color=col, sw=1.9))

    # Підтяжка на лінії TACH — окрема позначка над проміжком проводу TACH
    tachY = top + 3 * rowH + rowH / 2
    midx = (px_out + rx) / 2
    f.append(text(midx, tachY - 16, "підтяжка", size=9, color=FIELD, bold=True))
    f.append(text(midx, tachY - 3, "до +3.3/5 В", size=9, color=FIELD, bold=True))

    # Ноти внизу — дві акуратні смуги
    b1, _, _ = textbox(W / 2, H - 70,
                       "PWM живить вивід керування, а НЕ рве +5 В — живлення до вентилятора йде постійно",
                       size=11, fill="#eef2f8", stroke=NEG)
    f.append(b1)
    b2, _, _ = textbox(W / 2, H - 34,
                       "TACH — відкритий колектор: без підтяжки до плюса на вході буде тиша; лічи 2 імпульси на оберт",
                       size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. Пастка 3-проводового: низом рвати живлення НЕ можна, верхом — можна ──────
def fig_lowside_highside():
    W, H = 940, 520
    f = [text(W / 2, 30, "Керування 3-проводовим: чому ключ ставлять ЗВЕРХУ, а не знизу",
              size=16, bold=True)]

    panelW = 400
    gap = 60
    x0 = (W - 2 * panelW - gap) / 2
    top = 62
    boxH = 360

    def rail(px, y, label, col):
        f.append(line(px + 30, y, px + panelW - 30, y, color=col, sw=2.2))
        f.append(text(px + 30, y - 8, label, size=10, bold=True, color=col, anchor="start"))

    # -- ЛІВА: низом (погано) --
    lx = x0
    f.append(rect(lx, top, panelW, boxH, fill="#fdecea", stroke=POS, sw=1.9, rx=10))
    f.append(text(lx + panelW / 2, top + 26, "ключ знизу — тахометр ламається",
                  size=13.5, bold=True, color=POS))
    # +5 зверху, вентилятор, ключ між GND-вентилятора і землею
    v5y = top + 70
    rail(lx, v5y, "+5 В", POS)
    fanx = lx + 130
    fanTop = v5y + 20
    f.append(rect(fanx, fanTop, 140, 70, fill=BG, stroke=INK, sw=1.7, rx=8))
    f.append(text(fanx + 70, fanTop + 30, "вентилятор", size=11, bold=True))
    f.append(text(fanx + 70, fanTop + 48, "(3 проводи)", size=9, color=MUTED))
    f.append(line(fanx + 70, v5y, fanx + 70, fanTop, color=POS, sw=2))
    # ключ нижче вентилятора
    swy = fanTop + 70
    f.append(line(fanx + 70, fanTop + 70, fanx + 70, swy + 10, color=INK, sw=2))
    f.append(rect(fanx + 40, swy + 10, 60, 40, fill="#eef2f8", stroke=NEG, sw=1.7, rx=6))
    f.append(text(fanx + 70, swy + 34, "ключ", size=10, bold=True, color=NEG))
    gndy = swy + 90
    rail(lx, gndy, "GND (плати)", INK)
    f.append(line(fanx + 70, swy + 50, fanx + 70, gndy, color=INK, sw=2))
    # TACH виходить, але його «земля» відв'язана в паузі
    f.append(circle(fanx + 140, fanTop + 20, 4, fill=FIELD, stroke=FIELD, sw=1))
    f.append(line(fanx + 140, fanTop + 20, lx + panelW - 24, fanTop + 20, color=FIELD, sw=1.8))
    f.append(text(lx + panelW - 24, fanTop + 16, "TACH", size=10, bold=True, color=FIELD, anchor="end"))
    b1, _, _ = textbox(lx + panelW / 2, top + boxH - 34,
                       "у паузі PWM «земля» вентилятора висить —\nтахометр і Холл втрачають опору",
                       size=10, fill=BG, stroke=POS)
    f.append(b1)

    # -- ПРАВА: зверху (добре) --
    rx = x0 + panelW + gap
    f.append(rect(rx, top, panelW, boxH, fill="#eef6ef", stroke=FIELD, sw=1.9, rx=10))
    f.append(text(rx + panelW / 2, top + 26, "ключ зверху — тахометр цілий",
                  size=13.5, bold=True, color="#1e5631"))
    v5y2 = top + 70
    rail(rx, v5y2, "+5 В", POS)
    fanx2 = rx + 130
    # ключ між +5 і вентилятором
    swy2 = v5y2 + 20
    f.append(line(fanx2 + 70, v5y2, fanx2 + 70, swy2, color=POS, sw=2))
    f.append(rect(fanx2 + 40, swy2, 60, 40, fill="#fdecea", stroke=POS, sw=1.7, rx=6))
    f.append(text(fanx2 + 70, swy2 + 24, "ключ", size=10, bold=True, color=POS))
    fanTop2 = swy2 + 60
    f.append(line(fanx2 + 70, swy2 + 40, fanx2 + 70, fanTop2, color=POS, sw=2))
    f.append(rect(fanx2, fanTop2, 140, 70, fill=BG, stroke=INK, sw=1.7, rx=8))
    f.append(text(fanx2 + 70, fanTop2 + 30, "вентилятор", size=11, bold=True))
    f.append(text(fanx2 + 70, fanTop2 + 48, "(3 проводи)", size=9, color=MUTED))
    gndy2 = fanTop2 + 110
    rail(rx, gndy2, "GND (плати)", INK)
    f.append(line(fanx2 + 70, fanTop2 + 70, fanx2 + 70, gndy2, color=INK, sw=2))
    # TACH — земля стабільна
    f.append(circle(fanx2 + 140, fanTop2 + 20, 4, fill=FIELD, stroke=FIELD, sw=1))
    f.append(line(fanx2 + 140, fanTop2 + 20, rx + panelW - 24, fanTop2 + 20, color=FIELD, sw=1.8))
    f.append(text(rx + panelW - 24, fanTop2 + 16, "TACH", size=10, bold=True, color=FIELD, anchor="end"))
    b2, _, _ = textbox(rx + panelW / 2, top + boxH - 34,
                       "земля вентилятора завжди на місці —\nтахометр читається чисто",
                       size=10, fill=BG, stroke=FIELD)
    f.append(b2)

    render(os.path.join(IMG, "lowside-highside.svg"), W, H, *f)


# ── 5. Чому 25 кГц: шкала частот — слух, старий писк ШІМ і вікно Intel ──────────
def fig_pwm_frequency():
    W, H = 960, 430
    f = [text(W / 2, 30, "Чому 25 кГц: керувальну частоту винесли ЗА поріг слуху",
              size=16, bold=True)]

    # Логарифмічна вісь частот від 100 Гц до 40 кГц
    import math
    axX0, axX1 = 90, W - 60          # ліва й права межі осі
    axY = 250                        # рівень осі
    fmin, fmax = 100.0, 40000.0
    lmin, lmax = math.log10(fmin), math.log10(fmax)

    def fx(hz):
        return axX0 + (math.log10(hz) - lmin) / (lmax - lmin) * (axX1 - axX0)

    # Смуга чутного (20 Гц..20 кГц) — тут показуємо від краю осі до 20 кГц
    hear_x1 = fx(20000)
    f.append(rect(axX0, axY - 26, hear_x1 - axX0, 52, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    f.append(text((axX0 + hear_x1) / 2, axY - 34, "чутно людині", size=11, bold=True, color=POS))

    # Смуга «нечутно» (20..40 кГц) — зелена, сюди й цілить стандарт
    f.append(rect(hear_x1, axY - 26, axX1 - hear_x1, 52, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=6))
    # підпис зсунуто до правого краю смуги, щоб маркер «ціль 25 кГц» його не перетинав
    f.append(text((hear_x1 + axX1) / 2 + 34, axY - 34, "вище слуху", size=11, bold=True, color="#1e5631"))

    # Вісь із поділками
    f.append(line(axX0, axY, axX1, axY, color=INK, sw=2))
    for hz, lab in [(100, "100 Гц"), (1000, "1 кГц"), (10000, "10 кГц"),
                    (20000, "20 кГц"), (40000, "40 кГц")]:
        x = fx(hz)
        f.append(line(x, axY - 5, x, axY + 5, color=INK, sw=1.6))
        f.append(text(x, axY + 22, lab, size=10, color=MUTED))

    # Позначка порога слуху ~20 кГц (пунктир від смуг до осі; нижче — тик-підпис, тож не заходимо на нього)
    xh = fx(20000)
    f.append(line(xh, axY - 60, xh, axY - 6, color=INK, sw=1.3, dash="4,4"))
    f.append(text(xh, axY - 66, "≈ 20 кГц — стеля слуху", size=10, bold=True, color=INK))

    # Старий грубий ШІМ: кількасот Гц .. ~1 кГц — глибоко в чутному
    ox = fx(400)
    f.append(circle(ox, axY, 6, fill=POS, stroke=POS, sw=1))
    b_old, _, _ = textbox(fx(320), axY + 96,
                          "старий спосіб: рвати живлення\nна сотнях Гц → чутний писк",
                          size=10, fill="#fdecea", stroke=POS)
    f.append(b_old)
    f.append(line(ox, axY + 8, fx(320), axY + 96 - 20, color=POS, sw=1.4))

    # Вікно Intel: 21..28 кГц, ціль 25 кГц — уже в зеленому
    wx1, wx2 = fx(21000), fx(28000)
    f.append(rect(wx1, axY - 16, wx2 - wx1, 32, fill=BG, stroke=FIELD, sw=2, rx=5))
    xc = fx(25000)
    f.append(line(xc, axY - 16, xc, axY + 16, color=FIELD, sw=2.4))   # тик точної позиції 25 кГц у вікні
    f.append(text(xc, axY - 74, "ціль 25 кГц", size=11, bold=True, color="#1e5631"))
    f.append(line(xc, axY - 68, xc, axY - 18, color=FIELD, sw=1.3, dash="3,3"))  # підпис → вікно (смугу-напис зсунуто вбік)
    b_new, _, _ = textbox(fx(24000), axY + 96,
                          "стандарт Intel: вікно 21–28 кГц\n→ вентилятор мовчить на керуванні",
                          size=10, fill="#eef6ef", stroke=FIELD)
    f.append(b_new)
    f.append(line(xc, axY + 16, fx(24000), axY + 96 - 20, color=FIELD, sw=1.4))

    render(os.path.join(IMG, "pwm-frequency.svg"), W, H, *f)


# ── 6. High-side ключ через перемикач рівня: 3.3-В ніжка ганяє P-MOSFET ─────────
def fig_highside_levelshift():
    W, H = 900, 560
    f = [text(W / 2, 30, "High-side ключ на 5 В: 3.3-В ніжка керує P-MOSFET через NPN",
              size=16, bold=True)]

    # Верхня шина +5 В
    railTop = 90
    f.append(line(120, railTop, W - 80, railTop, color=POS, sw=2.4))
    f.append(text(130, railTop - 10, "+5 В", size=12, bold=True, color=POS, anchor="start"))

    # Нижня шина GND
    railBot = 480
    f.append(line(120, railBot, W - 80, railBot, color=INK, sw=2.4))
    f.append(text(130, railBot + 22, "GND (спільна з МК)", size=11, bold=True, color=INK, anchor="start"))

    # --- Права гілка: P-MOSFET (верхній ключ) + вентилятор ---
    pmx = 660
    # витік на +5 В
    f.append(line(pmx, railTop, pmx, 150, color=POS, sw=2))
    f.append(rect(pmx - 55, 150, 110, 74, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    f.append(text(pmx, 178, "P-MOSFET", size=12, bold=True, color=POS))
    f.append(text(pmx, 196, "верхній ключ", size=9.5, color=MUTED))
    f.append(text(pmx + 60, 165, "витік (+5 В)", size=9, color=POS, anchor="start"))
    f.append(text(pmx + 60, 214, "стік", size=9, color=INK, anchor="start"))
    # стік → вентилятор → GND
    f.append(line(pmx, 224, pmx, 300, color=INK, sw=2))
    f.append(rect(pmx - 60, 300, 120, 74, fill=BG, stroke="#1e5631", sw=1.9, rx=8))
    f.append(text(pmx, 330, "вентилятор", size=12, bold=True, color="#1e5631"))
    f.append(text(pmx, 348, "(2–3 проводи)", size=9, color=MUTED))
    f.append(line(pmx, 374, pmx, railBot, color=INK, sw=2))

    # Діод-глушник паралельно вентилятору (катод до +, анод до −)
    ddx = pmx + 120
    f.append(line(pmx, 288, ddx, 288, color=NEG, sw=1.6))
    f.append(line(ddx, 288, ddx, 386, color=NEG, sw=1.6))
    f.append(line(pmx, 386, ddx, 386, color=NEG, sw=1.6))
    # трикутник діода
    f.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f z" fill="%s" stroke="%s"/>'
             % (ddx - 9, 348, ddx + 9, 348, ddx, 330, "#eaf0fd", NEG))
    f.append(line(ddx - 9, 330, ddx + 9, 330, color=NEG, sw=2))  # смуга катода
    f.append(text(ddx + 14, 344, "діод-", size=9, color=NEG, anchor="start", bold=True))
    f.append(text(ddx + 14, 356, "глушник", size=9, color=NEG, anchor="start", bold=True))

    # затвор P-MOSFET
    gateY = 187
    f.append(line(pmx - 55, gateY, 470, gateY, color=INK, sw=1.8))
    f.append(circle(pmx - 55, gateY, 3, fill=INK, stroke=INK, sw=1))
    f.append(text(pmx - 120, gateY - 8, "затвор", size=9.5, color=INK, bold=True))

    # Підтяжка затвора до +5 В (закриває ключ, коли NPN вимкнено)
    rupx = 560
    f.append(line(rupx, railTop, rupx, gateY, color=MUTED, sw=1.6))
    f.append(line(rupx, gateY, 470, gateY, color=INK, sw=0.1))  # з'єднання на лінії затвора
    f.append(rect(rupx - 12, 118, 24, 40, fill=BG, stroke=MUTED, sw=1.5, rx=3))
    f.append(text(rupx + 40, 128, "Rпідтяжки", size=9, color=MUTED, anchor="middle", bold=True))
    f.append(text(rupx + 40, 141, "~10 кОм", size=9, color=MUTED))
    f.append(circle(rupx, gateY, 3, fill=INK, stroke=INK, sw=1))

    # --- Ліва гілка: NPN-перемикач рівня ---
    npx = 300
    # колектор NPN тягне лінію затвора вниз
    f.append(line(470, gateY, npx, gateY, color=INK, sw=1.8))
    f.append(line(npx, gateY, npx, 300, color=INK, sw=1.8))
    f.append(rect(npx - 50, 300, 100, 70, fill="#eef2f8", stroke=NEG, sw=1.8, rx=8))
    f.append(text(npx, 328, "NPN", size=12, bold=True, color=NEG))
    f.append(text(npx, 346, "перемикач рівня", size=9, color=MUTED))
    f.append(text(npx - 58, 312, "колектор", size=9, color=INK, anchor="end"))
    # емітер → GND
    f.append(line(npx, 370, npx, railBot, color=INK, sw=1.8))
    f.append(text(npx - 58, 362, "емітер", size=9, color=INK, anchor="end"))

    # база ← ніжка МК через резистор
    baseY = 335
    f.append(line(npx - 50, baseY, 190, baseY, color=INK, sw=1.8))
    f.append(rect(190 - 44, baseY - 11, 44, 22, fill=BG, stroke=INK, sw=1.4, rx=3))
    f.append(text(190 - 22, baseY - 18, "Rбази", size=9, color=INK, bold=True))
    f.append(line(146, baseY, 90, baseY, color=NEG, sw=1.8))
    f.append(circle(90, baseY, 4, fill=NEG, stroke=NEG, sw=1))
    f.append(text(84, baseY + 20, "ніжка МК", size=10, bold=True, color=NEG, anchor="middle"))
    f.append(text(84, baseY + 34, "(3.3 В)", size=9, color=MUTED, anchor="middle"))

    b, _, _ = textbox(W / 2, H - 30,
                      "ніжка «1» → NPN відкритий → тягне затвор до GND → P-MOSFET відкритий, +5 В на вентилятор\n"
                      "ніжка «0» → NPN закритий → підтяжка тягне затвор до +5 В → P-MOSFET закритий",
                      size=10, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "highside-levelshift.svg"), W, H, *f)


# ── 7. Дві епохи керування: рвати живлення (до 2004) vs окремий дріт PWM (2004) ─
def fig_two_eras():
    W, H = 940, 560
    f = [text(W / 2, 30, "Дві епохи керування швидкістю вентилятора", size=17, bold=True)]

    # Спільна геометрія двох колонок
    col_l = 235   # центр лівої колонки
    col_r = 705   # центр правої колонки
    fan_y = 150   # ряд вентиляторів
    fan_w, fan_h = 150, 78

    # ── ЛІВА КОЛОНКА: старий спосіб — рвати саме живлення ──────────────────────
    f.append(text(col_l, 62, "ДО: три дроти, керуємо напругою", size=13.5, bold=True, color=POS))
    f.append(text(col_l, 80, "живлення то є, то нема", size=10.5, color=MUTED))

    # джерело +12 з ключем, що рве лінію
    f.append(fitbox(col_l - 190, fan_y - 16, 70, 34, "+12 В", size=12, bold=True,
                    fill="#fdecea", stroke=POS, color=POS))
    # рваний провід: пунктир через «ключ»
    f.append(line(col_l - 120, fan_y + 1, col_l - 92, fan_y + 1, color=POS, sw=2.4))
    f.append(text(col_l - 106, fan_y - 12, "ключ", size=9, color=POS))
    f.append(line(col_l - 92, fan_y - 12, col_l - 78, fan_y + 10, color=POS, sw=2.0))  # розімкнений важіль
    f.append(line(col_l - 78, fan_y + 1, col_l - fan_w / 2, fan_y + 1, color=POS, sw=2.4))

    # вентилятор ліворуч
    f.append(rect(col_l - fan_w / 2, fan_y - fan_h / 2, fan_w, fan_h,
                  fill="#f4f6f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(col_l, fan_y - 12, "вентилятор", size=12, bold=True))
    f.append(text(col_l, fan_y + 6, "мотор + драйвер", size=9.5, color=MUTED))
    f.append(text(col_l, fan_y + 22, "живиться ривками", size=9.5, color=POS, bold=True))

    # три симптоми-наслідки
    sy = fan_y + 78
    for i, (t, sub) in enumerate([
            ("свист", "чути частоту рвання"),
            ("поганий старт", "драйвер гасне в паузі"),
            ("тахо бреше", "лічильник без живлення")]):
        yy = sy + i * 64
        f.append(fitbox(col_l - 175, yy, 350, 50,
                        t + "\n" + sub, size=11, bold=True, color=POS,
                        fill="#fff5f5", stroke=POS, sw=1.4))

    # ── ПРАВА КОЛОНКА: 2004 — живлення постійне, окремий дріт PWM ──────────────
    f.append(text(col_r, 62, "ПІСЛЯ: четвертий дріт — сигнал PWM", size=13.5, bold=True, color=FIELD))
    f.append(text(col_r, 80, "живлення завжди повне", size=10.5, color=MUTED))

    # постійне +12
    f.append(fitbox(col_r - 190, fan_y - 16, 70, 34, "+12 В", size=12, bold=True,
                    fill="#eafaf1", stroke=FIELD, color="#1e7d46"))
    f.append(line(col_r - 120, fan_y + 1, col_r - fan_w / 2, fan_y + 1, color=FIELD, sw=2.6))
    f.append(text(col_r - 95, fan_y - 12, "без розривів", size=9, color="#1e7d46"))

    # вентилятор праворуч
    f.append(rect(col_r - fan_w / 2, fan_y - fan_h / 2, fan_w, fan_h,
                  fill="#f4f6f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(col_r, fan_y - 12, "вентилятор", size=12, bold=True))
    f.append(text(col_r, fan_y + 6, "той самий драйвер", size=9.5, color=MUTED))
    f.append(text(col_r, fan_y + 22, "живлення стабільне", size=9.5, color="#1e7d46", bold=True))

    # окремий керувальний дріт знизу до вентилятора
    ctrl_y = fan_y + 96
    f.append(fitbox(col_r - 220, ctrl_y - 20, 150, 40, "керунок\n25 кГц, шпаруватість",
                    size=10, bold=True, color=NEG, fill="#eef2fd", stroke=NEG))
    f.append(arrow(col_r - 70, ctrl_y, col_r - fan_w / 4, fan_y + fan_h / 2 + 2, color=NEG, sw=2.0))
    f.append(text(col_r + 40, ctrl_y - 4, "→ 4-й дріт PWM", size=10.5, bold=True, color=NEG))
    f.append(text(col_r + 40, ctrl_y + 12, "шепоче драйверу", size=9.5, color=NEG))

    # три наслідки-переваги
    sy2 = fan_y + 150
    for i, (t, sub) in enumerate([
            ("тиша", "25 кГц вище слуху")]):
        yy = sy2 + i * 64
        f.append(fitbox(col_r - 175, yy, 350, 50,
                        t + "\n" + sub, size=11, bold=True, color="#1e7d46",
                        fill="#f2fbf6", stroke=FIELD, sw=1.4))
    f.append(fitbox(col_r - 175, sy2 + 64, 350, 50,
                    "певний старт\nживлення не зникає", size=11, bold=True, color="#1e7d46",
                    fill="#f2fbf6", stroke=FIELD, sw=1.4))
    f.append(fitbox(col_r - 175, sy2 + 128, 350, 50,
                    "тахо чесний\nдрайвер завжди живий", size=11, bold=True, color="#1e7d46",
                    fill="#f2fbf6", stroke=FIELD, sw=1.4))

    # роздільник посередині
    f.append(line(W / 2, 52, W / 2, H - 20, color=MUTED, sw=1.2, dash="6,6"))

    render(os.path.join(IMG, "two-eras.svg"), W, H, *f)


if __name__ == "__main__":
    fig_fan_inside()
    fig_wire_counts()
    fig_wiring()
    fig_lowside_highside()
    fig_pwm_frequency()
    fig_highside_levelshift()
    fig_two_eras()
    print("OK: 7 figures ->", IMG)
