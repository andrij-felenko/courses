# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: ланцюг сигналу — генератор → щуп-конденсатор → детектор → DC ──
def fig_chain():
    W, H = 940, 340
    f = []
    yb = 150            # рівень блоків
    bh = 96             # висота блоків

    # 555 астабільний
    b1, w1, _ = textbox(120, yb, ["555 (TLC555)", "генератор", "≈1.5 МГц"], size=15,
                         min_w=170, fill="#eef4ff", stroke=NEG, sw=2)
    # щуп-конденсатор
    b2, w2, _ = textbox(360, yb, ["щуп", "C = ε·A/d", "30…400 пФ"], size=15,
                        min_w=170, fill="#eaf7ef", stroke=FIELD, sw=2)
    # діод + інтегратор
    b3, w3, _ = textbox(600, yb, ["діод +", "RC-інтегратор", "(піковий детектор)"], size=15,
                        min_w=175, fill=FILL, sw=1.8)
    # DC вихід
    b4, w4, _ = textbox(835, yb, ["AOUT", "DC 0…3 В", "→ АЦП"], size=15,
                        min_w=140, fill="#fdf5e6", stroke="#b9770e", sw=2)

    # стрілки між блоками (ведемо чітко по осі yb, повз написи)
    f.append(arrow(120 + w1/2, yb, 360 - w2/2, yb, sw=2))
    f.append(arrow(360 + w2/2, yb, 600 - w3/2, yb, sw=2))
    f.append(arrow(600 + w3/2, yb, 835 - w4/2, yb, sw=2))

    # підписи над стрілками — з ЗАПАСОМ над лінією
    f.append(text((120 + w1/2 + 360 - w2/2)/2, yb - 16, "меандр", size=13, color=MUTED))
    f.append(text((360 + w2/2 + 600 - w3/2)/2, yb - 16, "струм заряду", size=13, color=MUTED))
    f.append(text((600 + w3/2 + 835 - w4/2)/2, yb - 16, "рівна напруга", size=13, color=MUTED))

    f.append(b1); f.append(b2); f.append(b3); f.append(b4)

    # нижній рядок: напрям залежності
    yn = 300
    f.append(text(360, yn, "вологіше → більше ε → більша C → менша реактивність", size=14, color=FIELD, bold=True))
    f.append(text(720, yn, "→ нижча DC", size=14, color=POS, bold=True))

    render(os.path.join(IMG, 'chain.svg'), W, H, *f,
           title="Ланцюг сигналу: коливання перетворюються на рівну напругу")


# ── Фігура 2: копланарний конденсатор і крайове поле в ґрунті ───────────────
def fig_field():
    W, H = 900, 430
    f = []

    # дві половини: суха (ліворуч) і волога (праворуч)
    def half(x0, label, eps_txt, cap_txt, wet, box_color):
        g = []
        gw = 360
        # ґрунт-фон
        g.append(rect(x0, 150, gw, 210, fill=("#e9d9c3" if not wet else "#c9b79a"),
                      stroke="#9c8461", sw=1.5, rx=8))
        # текстоліт-щуп (вертикальна пластина в ґрунті)
        px = x0 + gw/2
        g.append(rect(px - 16, 120, 32, 200, fill="#2f6f3e", stroke=INK, sw=1.5, rx=4))
        # дві доріжки-«пальці» (копланарні) — символічно вертикальні смуги
        g.append(rect(px - 9, 150, 6, 150, fill="#c9a227", stroke=None, sw=0))
        g.append(rect(px + 3, 150, 6, 150, fill="#c9a227", stroke=None, sw=0))
        # крайові лінії поля — дуги з одного «пальця» в інший (повз написи)
        for i, r in enumerate((26, 44, 64)):
            depth = 150 + 40 + i*10
            g.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"%s/>'
                     % (px - 6, 175 + i*22, px, depth, px + 6, 175 + i*22,
                        (FIELD if wet else MUTED), (' stroke-dasharray="4 3"' if not wet else '')))
        # підпис ε — у своїй рамці, збоку, не на полі
        eb, _, _ = textbox(x0 + gw/2, 392, eps_txt, size=15, min_w=150,
                           fill=box_color, stroke=(FIELD if wet else MUTED), sw=1.8, bold=True)
        g.append(eb)
        # заголовок половини — над ґрунтом
        g.append(text(x0 + gw/2, 108, label, size=15, bold=True))
        # значення ємності — над заголовком, окремо
        cb, _, _ = textbox(x0 + gw/2, 80, cap_txt, size=14, min_w=130,
                          fill="#ffffff", stroke=INK, sw=1.4)
        g.append(cb)
        return g

    f += half(40,  "Сухий ґрунт", "ε ≈ 3…5", "мала C", False, "#f4f6f8")
    f += half(500, "Вологий ґрунт", "ε ≈ 25…40", "велика C", True, "#eaf7ef")

    render(os.path.join(IMG, 'field.svg'), W, H, *f,
           title="Крайове поле щупа тягнеться в ґрунт: вода піднімає ε, отже й ємність")


# ── Фігура 3: розпіновка й підключення пін-у-пін ───────────────────────────
def fig_wiring():
    W, H = 820, 380
    f = []

    # плата давача (ліворуч)
    f.append(rect(60, 90, 210, 200, fill="#2f6f3e", stroke=INK, sw=1.8, rx=10))
    f.append(text(165, 118, "щуп v1.2", size=15, color="#ffffff", bold=True))
    f.append(text(165, 140, "(3-контактний)", size=12, color="#d8ecdd"))

    pins = [("AOUT", "#b9770e"), ("VCC", POS), ("GND", NEG)]
    py0 = 175
    for i, (name, col) in enumerate(pins):
        y = py0 + i*44
        f.append(circle(270, y, 8, fill=col, stroke=INK, sw=1.4))
        pb, pw, _ = textbox(220, y, name, size=13, min_w=64, fill="#ffffff", stroke=col, sw=1.6, bold=True)
        f.append(pb)

    # плата МК (праворуч)
    f.append(rect(560, 90, 200, 200, fill="#26324a", stroke=INK, sw=1.8, rx=10))
    f.append(text(660, 122, "МК", size=16, color="#ffffff", bold=True))
    f.append(text(660, 146, "(Arduino / ESP32)", size=12, color="#c7cfdd"))

    mcu = [("A0 (ADC)", "#b9770e"), ("3V3 / 5V", POS), ("GND", NEG)]
    for i, (name, col) in enumerate(mcu):
        y = py0 + i*44
        f.append(circle(560, y, 8, fill=col, stroke=INK, sw=1.4))
        mb, mw, _ = textbox(660, y, name, size=13, min_w=110, fill="#ffffff", stroke=col, sw=1.6, bold=True)
        f.append(mb)

    # дроти пін-у-пін — прямі, рознесені по вертикалі, повз написи
    for i, (name, col) in enumerate(pins):
        y = py0 + i*44
        f.append(line(270, y, 560, y, color=col, sw=2.4))

    # застереження знизу
    wb, _, _ = textbox(410, 345, "живлення 3.3…5.5 В · AOUT: сухо ≈ вище, волого ≈ нижче", size=13,
                      min_w=560, fill="#fdf5e6", stroke="#b9770e", sw=1.6)
    f.append(wb)

    render(os.path.join(IMG, 'wiring.svg'), W, H, *f,
           title="Три контакти: живлення, земля й один аналоговий вихід")


if __name__ == '__main__':
    fig_chain()
    fig_field()
    fig_wiring()
    print("figures written to", IMG)
