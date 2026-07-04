# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: що всередині чипа — блок-схема тракту ─────────────────────────
def fig_inside():
    W, H = 780, 470
    f = []
    f.append(text(W/2, 26, "Що всередині MPU-6050: два давачі, АЦП, DMP, FIFO — на одному кристалі", size=16, bold=True))

    # межа кристала
    dx, dy, dw, dh = 40, 55, 560, 360
    f.append(rect(dx, dy, dw, dh, fill="#f7f9fc", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(dx+14, dy+22, "кремнієвий кристал", size=11, color=MUTED, anchor="start"))

    # два давачі зліва
    ax_ = dx+30
    b_acc = textbox(ax_+70, dy+95, "Акселерометр\n3 осі (X Y Z)", size=12, pad=10, fill="#e8f0fe", stroke=NEG, bold=True)
    f.append(b_acc[0])
    b_gyr = textbox(ax_+70, dy+185, "Гіроскоп\n3 осі (X Y Z)", size=12, pad=10, fill="#fdecea", stroke=POS, bold=True)
    f.append(b_gyr[0])
    b_tmp = textbox(ax_+70, dy+270, "Температура\n(1 канал)", size=12, pad=10, fill="#eafaf1", stroke=FIELD)
    f.append(b_tmp[0])

    # АЦП посередині
    adcx = dx+250
    b_adc = textbox(adcx, dy+185, "16-бітні\nАЦП\n×6", size=12, pad=12, fill="#fff8e1", stroke=POS, bold=True)
    f.append(b_adc[0])

    # стрілки давачі → АЦП
    for by in (dy+95, dy+185, dy+270):
        f.append(arrow(ax_+70+b_acc[1]/2, by, adcx-b_adc[1]/2, dy+185, color=MUTED, sw=1.6))

    # регістри/FIFO + DMP справа
    regx = dx+430
    b_reg = textbox(regx, dy+120, "Регістри\nданих +\nFIFO-буфер", size=12, pad=11, fill=FILL, stroke=LINE, bold=True)
    f.append(b_reg[0])
    b_dmp = textbox(regx, dy+255, "DMP\n(цифровий\nпроцесор\nруху)", size=11, pad=11, fill="#eafaf1", stroke=FIELD, bold=True)
    f.append(b_dmp[0])

    # АЦП → регістри
    f.append(arrow(adcx+b_adc[1]/2, dy+185, regx-b_reg[1]/2, dy+120, color=INK, sw=1.8))
    # АЦП ↔ DMP (двобічно: DMP читає давачі й пише в FIFO)
    f.append(arrow(adcx+b_adc[1]/2, dy+185, regx-b_dmp[1]/2, dy+255, color=FIELD, sw=1.6))
    f.append(arrow(regx, dy+255-b_dmp[2]/2, regx, dy+120+b_reg[2]/2, color=FIELD, sw=1.6))

    # шина I2C назовні
    busx = dx+dw
    f.append(line(regx+b_reg[1]/2, dy+120, busx+40, dy+120, color=INK, sw=2))
    f.append(arrow(busx+40, dy+120, busx+40, dy+180, color=INK, sw=2))
    b_i2c = textbox(busx+95, dy+210, "Шина I2C\nSCL / SDA\n(до МК)", size=12, pad=10, fill="#e8f0fe", stroke=NEG, bold=True)
    f.append(b_i2c[0])

    # висновок унизу
    concl = ("Обидва давачі вимірюються одночасно й оцифровуються на місці.\n"
             "МК читає готові числа по I2C; DMP може сам зливати осі в кути й класти у FIFO.")
    f.append(fitbox(40, 425, 700, 34, concl, size=12, pad=8, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG, 'inside.svg'), W, H, *f)


# ── Фігура 2: розводка GY-521 пін-у-пін до 5 В МК по I2C ────────────────────
def fig_wiring():
    W, H = 780, 470
    f = []
    f.append(text(W/2, 26, "Підключення GY-521 до 5-вольтового мікроконтролера по I2C", size=16, bold=True))

    # плата GY-521 зліва
    bx, by, bw, bh = 60, 78, 210, 320
    f.append(rect(bx, by, bw, bh, fill="#e8f0fe", stroke=NEG, sw=2, rx=8))
    f.append(text(bx+bw/2, by-10, "GY-521 (модуль MPU-6050)", size=13, bold=True))
    f.append(text(bx+bw/2, by+20, "на борту: LDO 3.3 В", size=11, color=MUTED))
    f.append(text(bx+bw/2, by+37, "+ підтяжки I2C до 3.3 В", size=11, color=MUTED))

    pins = ["VCC", "GND", "SCL", "SDA", "XDA", "XCL", "AD0", "INT"]
    py0 = by+70; step = (bh-92) / (len(pins)-1)
    pin_y = {}
    for i, p in enumerate(pins):
        yy = py0 + i*step
        pin_y[p] = yy
        f.append(circle(bx+bw-14, yy, 6, fill=BG, stroke=INK, sw=1.6))
        f.append(text(bx+bw-34, yy+4, p, size=13, bold=True, anchor="end"))

    # МК справа
    mx, my, mw, mh = 540, 78, 180, 320
    f.append(rect(mx, my, mw, mh, fill="#f4f6f8", stroke=LINE, sw=2, rx=8))
    f.append(text(mx+mw/2, my-10, "МК / плата (5 В)", size=13, bold=True))
    mrows = ["5V", "GND", "SCL", "SDA", "—", "—", "GND", "GPIO"]
    mrow_y = {}
    for i, p in enumerate(mrows):
        yy = py0 + i*step
        mrow_y[i] = yy
        if p != "—":
            f.append(circle(mx+14, yy, 6, fill=BG, stroke=INK, sw=1.6))
            f.append(text(mx+34, yy+4, p, size=13, bold=True, anchor="start"))

    # зʼєднання
    def wire(p, mi, col, lbl):
        x1 = bx+bw-8; y1 = pin_y[p]; x2 = mx+8; y2 = mrow_y[mi]
        midx = (x1+x2)/2 - 40 + 12*mi   # розводимо вертикалі, щоб траси не зливались
        d = "M %.1f %.1f H %.1f V %.1f H %.1f" % (x1, y1, midx, y2, x2)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, col))
        f.append(text(midx-8, y1-6, lbl, size=10, color=col, anchor="end"))
    wire("VCC", 0, POS, "5 В")
    wire("GND", 1, INK, "земля")
    wire("SCL", 2, NEG, "такт I2C")
    wire("SDA", 3, NEG, "дані I2C")
    wire("AD0", 6, MUTED, "адреса 0x68")
    wire("INT", 7, FIELD, "переривання")

    # XDA/XCL лишаємо вільними
    f.append(text(bx+bw+20, pin_y["XDA"]+4, "→ вільні (доп. I2C)", size=10, color=MUTED, anchor="start"))
    f.append(text(bx+bw+20, pin_y["XCL"]+4, "→ для магнетометра", size=10, color=MUTED, anchor="start"))

    note = ("VCC → 5 В (вбудований LDO дає чипу 3.3 В). SCL/SDA — двопровідна шина I2C.\n"
            "AD0 на землю → адреса 0x68 (на 3.3 В → 0x69). INT — необовʼязковий сигнал «дані готові».")
    f.append(fitbox(60, 420, 660, 34, note, size=11, pad=7, fill="#fff8e1", stroke=POS))

    render(os.path.join(IMG, 'wiring.svg'), W, H, *f)


# ── Фігура 3: діапазон vs роздільність — драбина повної шкали ────────────────
def fig_scale():
    W, H = 780, 420
    f = []
    f.append(text(W/2, 26, "Ширший діапазон — грубша роздільність: та сама 16-бітна шкала", size=16, bold=True))

    # ліворуч акселерометр, праворуч гіроскоп — дві колонки
    def ladder(x0, title, rows, unit):
        f.append(text(x0+150, 66, title, size=14, bold=True))
        # заголовки колонок
        f.append(text(x0+55, 92, "діапазон", size=11, color=MUTED))
        f.append(text(x0+205, 92, "1 крок (LSB)", size=11, color=MUTED))
        yy = 112
        for rng, lsb, res in rows:
            f.append(rect(x0, yy, 300, 44, fill=FILL, stroke=LINE, sw=1.2, rx=6))
            f.append(text(x0+55, yy+27, "±%s %s" % (rng, unit), size=13, bold=True))
            f.append(line(x0+110, yy+6, x0+110, yy+38, color=LINE, sw=1))
            f.append(text(x0+205, yy+20, "%s LSB/%s" % (lsb, unit), size=11, color=NEG))
            f.append(text(x0+205, yy+36, res, size=10, color=MUTED))
            yy += 52

    acc_rows = [
        ("2",  "16384", "≈ 0.06 mg/крок"),
        ("4",  "8192",  "≈ 0.12 mg/крок"),
        ("8",  "4096",  "≈ 0.24 mg/крок"),
        ("16", "2048",  "≈ 0.49 mg/крок"),
    ]
    gyr_rows = [
        ("250",  "131.0", "≈ 0.0076 °/s"),
        ("500",  "65.5",  "≈ 0.015 °/s"),
        ("1000", "32.8",  "≈ 0.030 °/s"),
        ("2000", "16.4",  "≈ 0.061 °/s"),
    ]
    ladder(40, "Акселерометр (g)", acc_rows, "g")
    ladder(430, "Гіроскоп (°/s)", gyr_rows, "°/s")

    concl = ("16 біт = 65536 сходинок ділять обраний діапазон. Вужчий діапазон → дрібніший крок (точніше),\n"
             "але сильний удар/оберт вилазить за край і насичується. Обирай найвужчий, що вмістить рух.")
    f.append(fitbox(40, 372, 700, 34, concl, size=12, pad=8, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG, 'scale.svg'), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_wiring()
    fig_scale()
    print("ok")
