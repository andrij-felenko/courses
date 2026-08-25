# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Дзеркальні сильні й слабкі сторони камери та IMU ──────────────────────
def fig_complementary():
    W, H = 720, 340
    frags = []
    frags.append(text(W/2, 28, "Камера й IMU: сила одного — там, де слабкість іншого", size=17, bold=True))

    # дві колонки
    colW = 300
    xL, xR = 40, W - 40 - colW
    yTop = 60
    frags.append(fitbox(xL, yTop, colW, 40, "КАМЕРА (візуальна одометрія)",
                        size=15, bold=True, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(xR, yTop, colW, 40, "IMU (гіроскоп + акселерометр)",
                        size=15, bold=True, fill="#fdecea", stroke=POS))

    rows = [
        ("не дрейфує на текстурі",  "дрейф росте з часом"),
        ("бачить масштаб? НІ",      "дає метричний масштаб"),
        ("повільна, ~30 Гц",        "швидка, ~1000 Гц"),
        ("сліпне на розмитті/пітьмі","працює завжди"),
    ]
    y = yTop + 56
    for a, b in rows:
        frags.append(fitbox(xL, y, colW, 40, a, size=13, fill="#f4f6f8", stroke=NEG, sw=1.2))
        frags.append(fitbox(xR, y, colW, 40, b, size=13, fill="#f4f6f8", stroke=POS, sw=1.2))
        y += 48

    # стрілки-«доповнення» між рядками
    for i in range(len(rows)):
        yy = yTop + 56 + i*48 + 20
        frags.append(line(xL+colW+6, yy, xR-6, yy, color=MUTED, sw=1.2, dash="4 3"))

    frags.append(text(W/2, H-12,
                      "Злиття бере від кожного лише те, у чому воно сильне.",
                      size=13, color=MUTED, italic=True))
    render(os.path.join(IMG, "vio-complementary.svg"), W, H, *frags)


# ── 2. Дві петлі частот: швидке передбачення IMU, рідка корекція камерою ──────
def fig_two_rates():
    W, H = 720, 300
    frags = []
    frags.append(text(W/2, 26, "Швидка петля IMU веде оцінку, рідкий кадр її підправляє", size=16, bold=True))

    x0, x1 = 60, W-40
    ybase = 200
    frags.append(line(x0, ybase, x1, ybase, color=LINE, sw=1.5))
    frags.append(text(x1, ybase+22, "час", size=13, color=MUTED, anchor="end"))

    # багато дрібних тиків IMU
    n_imu = 40
    for i in range(n_imu+1):
        xx = x0 + (x1-x0)*i/n_imu
        frags.append(line(xx, ybase-6, xx, ybase, color=NEG, sw=1.2))

    # рідкі кадри камери (кожен 8-й)
    frame_ys = 90
    for i in range(0, n_imu+1, 8):
        xx = x0 + (x1-x0)*i/n_imu
        frags.append(line(xx, frame_ys, xx, ybase, color=POS, sw=1.6, dash="5 4"))
        frags.append(circle(xx, frame_ys, 7, fill="#fdecea", stroke=POS, sw=2))

    frags.append(text(x0, ybase-16, "IMU ~1000/с: інтегрує рух між кадрами",
                      size=13, color=NEG, anchor="start"))
    frags.append(text(x0, frame_ys-16, "кадр камери ~30/с: скидає накопичений дрейф",
                      size=13, color=POS, anchor="start"))
    render(os.path.join(IMG, "vio-two-rates.svg"), W, H, *frags)


# ── 3. Масштаб: камера дає напрям, IMU дає, наскільки далеко ──────────────────
def fig_scale():
    W, H = 720, 320
    frags = []
    frags.append(text(W/2, 26, "Камера бачить форму шляху, але не його розмір", size=16, bold=True))

    # ліворуч: маленька траєкторія
    def path(cx, cy, s, color, label):
        pts = [(0,0),(1,-0.6),(2,-0.4),(2.6,0.5),(1.6,1.1),(0.4,0.7)]
        out = ""
        prev = None
        for (px,py) in pts:
            X = cx + px*s
            Y = cy + py*s
            frags.append(circle(X, Y, 3.5, fill=color, stroke=color, sw=1))
            if prev:
                out_line = line(prev[0], prev[1], X, Y, color=color, sw=1.8)
                frags.append(out_line)
            prev = (X, Y)
        frags.append(text(cx+1.3*s, cy+1.6*s, label, size=13, color=color, anchor="middle", bold=True))

    path(120, 150, 30, NEG, "камера: масштаб A")
    path(430, 130, 55, POS, "камера: масштаб B")

    frags.append(text(275, 250, "Той самий візерунок точок пасує будь-якому масштабу —",
                      size=13, color=INK, anchor="middle"))
    frags.append(text(275, 272, "камера не може обрати, який правильний.",
                      size=13, color=INK, anchor="middle"))

    frags.append(fitbox(W-230, 130, 200, 70,
                        "IMU знає прискорення в м/с² — а це реальні метри. Він і задає єдиний правильний масштаб.",
                        size=12, fill="#fdecea", stroke=POS))
    render(os.path.join(IMG, "vio-scale.svg"), W, H, *frags)


# ── 4. MSCKF: класичний стан росте з прикметами / MSCKF тримає лише пози ──────
def fig_msckf_state():
    W, H = 720, 380
    frags = []
    frags.append(text(W/2, 26, "Що фільтр тримає в стані: карту прикмет чи лише свої пози",
                      size=16, bold=True))

    colW = 300
    xL, xR = 40, W - 40 - colW
    yTop = 54
    frags.append(fitbox(xL, yTop, colW, 38, "Класичний EKF-SLAM",
                        size=15, bold=True, fill="#fdecea", stroke=POS))
    frags.append(fitbox(xR, yTop, colW, 38, "MSCKF: пози, не карта",
                        size=15, bold=True, fill="#eaf0fd", stroke=NEG))

    # ── ЛІВОРУЧ: поза + купа прикмет, стан пухне ──
    yb = yTop + 60
    frags.append(fitbox(xL, yb, colW, 30, "поза апарата", size=12,
                        fill="#f4f6f8", stroke=INK, sw=1.4))
    # прикмети в стані — рядок за рядком, «і так далі»
    fy = yb + 40
    for i in range(4):
        frags.append(fitbox(xL, fy, colW, 26, "координати прикмети %d (x,y,z)" % (i+1),
                            size=11, fill="#fdecea", stroke=POS, sw=1.1))
        fy += 30
    frags.append(text(xL + colW/2, fy + 8, "… + сотні таких — стан росте як N²",
                      size=12, color=POS, italic=True))

    # ── ПРАВОРУЧ: ковзне вікно поз, прикмети лише проходять ──
    frags.append(fitbox(xR, yb, colW, 30, "поза (кадр t)", size=12,
                        fill="#eaf0fd", stroke=NEG, sw=1.3))
    frags.append(fitbox(xR, yb + 34, colW, 30, "поза (кадр t−1)", size=12,
                        fill="#eaf0fd", stroke=NEG, sw=1.3))
    frags.append(fitbox(xR, yb + 68, colW, 30, "поза (кадр t−2)", size=12,
                        fill="#eaf0fd", stroke=NEG, sw=1.3))
    frags.append(text(xR + colW/2, yb + 120, "мале ковзне вікно — стан не росте",
                      size=12, color=NEG, italic=True))

    # прикмета «пролітає крізь» і зникає (нуль-простір)
    fy2 = yb + 150
    frags.append(fitbox(xR, fy2, colW, 28, "прикмета → обмеження на пози → зникає",
                        size=11, fill="#f4f6f8", stroke=FIELD, sw=1.3))
    frags.append(text(xR + colW/2, fy2 + 46, "(проєкція в нуль-простір: у стані її нема)",
                      size=11, color=FIELD))

    frags.append(text(W/2, H-14,
                      "Ліворуч кожна прикмета осідає в стані назавжди; праворуч — лише свідчить і йде.",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "msckf-state.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_complementary()
    fig_two_rates()
    fig_scale()
    fig_msckf_state()
    print("ok")
