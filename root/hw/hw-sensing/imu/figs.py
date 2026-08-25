# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Інерційний вимірювальний блок (IMU)».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: що таке IMU — три давачі в одному корпусі ──────────────────────
# Головна ідея статті: IMU — це НЕ один давач, а кілька інерційних давачів в
# одному корпусі. Показуємо корпус-чип, у ньому три блоки (акс/гіро/маг) і що
# кожен віддає (вектор із трьох осей), + сумарний рахунок осей 3/6/9.
def fig_what_is_imu():
    W, H = 920, 470
    parts = []

    # корпус IMU (чип)
    cx, cy = W / 2, 250
    cw, ch = 560, 300
    parts.append(rect(cx - cw / 2, cy - ch / 2, cw, ch, fill="#eef2f7", stroke=INK, sw=2, rx=14))
    parts.append(text(cx, cy - ch / 2 - 14, "один корпус IMU (кремнієвий чип)",
                      size=15, bold=True, color=MUTED))

    # три внутрішні блоки
    bw, bh = 168, 150
    gap = (cw - 3 * bw) / 4
    bx0 = cx - cw / 2 + gap
    by = cy - bh / 2 + 14

    blocks = [
        ("акселерометр", "лінійне\nприскорення", "вектор a\n(aX, aY, aZ)", POS, "#fdecea"),
        ("гіроскоп", "кутова\nшвидкість", "вектор ω\n(ωX, ωY, ωZ)", NEG, "#eaf0fd"),
        ("магнітометр", "магнітне\nполе Землі", "вектор m\n(mX, mY, mZ)", FIELD, "#e9f7ef"),
    ]
    for i, (name, meas, out, col, fill) in enumerate(blocks):
        x = bx0 + i * (bw + gap)
        parts.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=2, rx=8))
        parts.append(text(x + bw / 2, by + 26, name, size=14, bold=True, color=col))
        parts.append(mtext(x + bw / 2, by + 54, "міряє:", size=11, color=MUTED))
        parts.append(mtext(x + bw / 2, by + 74, meas, size=12, color=INK))
        parts.append(mtext(x + bw / 2, by + 118, out, size=11.5, color=col, bold=True))

    # підсумок: 3 / 6 / 9 осей
    sy = cy + ch / 2 + 44
    box, bxw, bxh = textbox(cx, sy,
                            "3 осі (лише акс)   ·   6 осей (акс + гіро)   ·   9 осей (акс + гіро + маг)",
                            size=13, pad=12, fill=FILL)
    parts.append(box)

    render("img/what-is-imu.svg", W, H, *parts,
           title="IMU — кілька інерційних давачів в одному корпусі")


# ── Фігура 2: чому одного давача замало (дзеркальні вади) ────────────────────
# Серце мотивації фьюжну: кожен давач сам по собі має фатальну ваду, і вади
# ДЗЕРКАЛЬНІ. Дві колонки (акс / гіро) з «сильним» (зелене) і «слабким»
# (червоне) боком; стрілки навхрест показують, що сила одного латає ваду другого.
def fig_why_not_enough():
    W, H = 900, 480
    parts = []

    colw = 320
    lx = 170          # центр лівої колонки (акселерометр)
    rx = W - 170      # центр правої колонки (гіроскоп)
    top = 80

    def column(cx, name, strong, weak, col):
        out = []
        out.append(text(cx, top, name, size=16, bold=True, color=col))
        # сильний бік
        out.append(fitbox(cx - colw / 2, top + 22, colw, 88,
                          strong, size=13, fill="#e9f7ef", stroke=FIELD, sw=2))
        out.append(text(cx, top + 22 + 88 + 18, "сила", size=11, color=FIELD, bold=True))
        # слабкий бік
        out.append(fitbox(cx - colw / 2, top + 150, colw, 88,
                          weak, size=13, fill="#fdecea", stroke=POS, sw=2))
        out.append(text(cx, top + 150 + 88 + 18, "вада", size=11, color=POS, bold=True))
        return out

    parts += column(lx, "акселерометр",
                    "абсолютний нахил\n(сталий g не дрейфує)",
                    "шумить і бреше в русі\n(плутає g з прискоренням)", POS)
    parts += column(rx, "гіроскоп",
                    "точний і швидкий у русі\n(чисте обертання, бачить yaw)",
                    "дрейфує з часом\n(інтеграл зсуву нуля спливає)", NEG)

    # хрест-стрілки: сила одного → латає ваду другого
    ay = top + 150 + 44      # рівень «вади»
    sy = top + 22 + 44       # рівень «сили»
    # сила акс (ліво-верх) → вада гіро (право-низ)
    parts.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2.2" stroke-dasharray="6,5" marker-end="url(#arrow)"/>'
                 % (lx + colw / 2 - 6, sy, W / 2, sy, W / 2, ay, rx - colw / 2 + 6, ay, FIELD))
    # сила гіро (право-верх) → вада акс (ліво-низ)
    parts.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2.2" stroke-dasharray="6,5" marker-end="url(#arrow)"/>'
                 % (rx - colw / 2 + 6, sy, W / 2, sy, W / 2, ay, lx + colw / 2 - 6, ay, FIELD))

    parts.append(mtext(W / 2, top + 124, "вади\nдзеркальні", size=12, color=MUTED, bold=True))

    # висновок знизу
    box, bw, bh = textbox(W / 2, H - 34,
                          "жоден давач сам недостатній → їх ПОЄДНУЮТЬ (sensor fusion)",
                          size=14, pad=12, fill=FILL, bold=True)
    parts.append(box)

    render("img/why-not-enough.svg", W, H, *parts,
           title="Чому одного давача замало: вади дзеркальні")


# ── Фігура 3: фьюжн як поділ за частотою ────────────────────────────────────
# ЯК саме поєднують: швидку (динамічну) частину беруть від гіроскопа, повільну
# (опорну) — від акселерометра/магнітометра, і складають у одну оцінку.
# Вісь часу/частоти: ліворуч «коротко» (гіро добрий), праворуч «довго» (акс/маг).
def fig_fusion_split():
    W, H = 900, 430
    parts = []

    ox, oy = 90, 250
    axis_len = 720
    parts.append(arrow(ox, oy, ox + axis_len, oy, color=INK, sw=1.8))
    parts.append(text(ox + axis_len + 6, oy + 5, "час", size=14, bold=True, anchor="start"))
    parts.append(text(ox, oy + 34, "коротко (мс…с)", size=12, color=MUTED, anchor="start"))
    parts.append(text(ox + axis_len, oy + 34, "довго (с…∞)", size=12, color=MUTED, anchor="end"))

    mid = ox + axis_len * 0.52

    # смуга гіроскопа — добрий накоротко (ліва частина)
    parts.append(rect(ox, oy - 90, mid - ox, 56, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    parts.append(mtext((ox + mid) / 2, oy - 56,
                       "ГІРОСКОП — швидка, гладка динаміка\n(точний на секунди, потім дрейфує)",
                       size=12, color=NEG, bold=True))

    # смуга акс/маг — добрий надовго (права частина)
    parts.append(rect(mid, oy + 34, ox + axis_len - mid, 56, fill="#e9f7ef", stroke=FIELD, sw=2, rx=8))
    parts.append(mtext((mid + ox + axis_len) / 2, oy + 68,
                       "АКСЕЛЕРОМЕТР + МАГНІТОМЕТР — абсолютна\nприв'язка (повільні, зате не дрейфують)",
                       size=12, color=FIELD, bold=True))

    # вертикаль поділу
    parts.append(line(mid, oy - 100, mid, oy + 100, color=MUTED, sw=1.2, dash="4,5"))

    # стрілки «складаємо в одне»
    parts.append(arrow((ox + mid) / 2, oy - 30, W / 2, oy - 6, color=NEG, sw=1.8))
    parts.append(arrow((mid + ox + axis_len) / 2, oy + 30, W / 2, oy + 6, color=FIELD, sw=1.8))

    # результат
    box, bw, bh = textbox(W / 2, H - 36,
                          "разом → одна надійна оцінка орієнтації на ВСІХ інтервалах",
                          size=14, pad=12, fill=FILL, bold=True)
    parts.append(box)

    render("img/fusion-split.svg", W, H, *parts,
           title="Поєднання: швидке від гіроскопа, опорне від акс/маг")


# ── Фігура 4: осі тіла й вихід орієнтації ───────────────────────────────────
# Практична картина: IMU міряє у ВЛАСНІЙ системі осей (тіло), а на виході —
# орієнтація відносно СВІТУ (крен/тангаж/курс). Показуємо корпус апарата з
# трьома осями й трьома обертаннями навколо них.
def fig_axes_orientation():
    W, H = 900, 470
    cx, cy = 340, 250
    parts = []

    # «корпус апарата» — простий паралелепіпед (ізометрія)
    s = 110
    dx, dy = 60, -34
    # передня грань
    fx, fy = cx - s / 2, cy - s / 2
    front = "M %.1f %.1f h %.1f v %.1f h %.1f z" % (fx, fy, s, s, -s)
    parts.append('<path d="%s" fill="#eef2f7" stroke="%s" stroke-width="2"/>' % (front, INK))
    # верхня грань
    top = "M %.1f %.1f h %.1f l %.1f %.1f h %.1f z" % (fx, fy, s, dx, dy, -s)
    parts.append('<path d="%s" fill="#dfe6ee" stroke="%s" stroke-width="2"/>' % (top, INK))
    # права грань
    right = "M %.1f %.1f v %.1f l %.1f %.1f v %.1f z" % (fx + s, fy, s, dx, dy, -s)
    parts.append('<path d="%s" fill="#cdd6e0" stroke="%s" stroke-width="2"/>' % (right, INK))
    parts.append(text(cx + 4, cy + 4, "корпус", size=12, color=MUTED))

    # три осі тіла з початком у центрі корпусу
    o = (fx + s / 2 + dx / 2, fy + s / 2 + dy / 2)
    # X — вперед (праворуч)
    parts.append(arrow(o[0], o[1], o[0] + 150, o[1], color=POS, sw=2.4))
    parts.append(text(o[0] + 160, o[1] + 5, "X", size=15, bold=True, color=POS, anchor="start"))
    parts.append(text(o[0] + 150, o[1] + 22, "крен (roll)", size=11, color=POS, anchor="middle"))
    # Y — вліво/вгору-вбік
    parts.append(arrow(o[0], o[1], o[0] + 70, o[1] - 120, color=NEG, sw=2.4))
    parts.append(text(o[0] + 78, o[1] - 128, "Y", size=15, bold=True, color=NEG, anchor="start"))
    parts.append(text(o[0] + 78, o[1] - 110, "тангаж (pitch)", size=11, color=NEG, anchor="start"))
    # Z — вгору
    parts.append(arrow(o[0], o[1], o[0], o[1] - 150, color=FIELD, sw=2.4))
    parts.append(text(o[0] + 6, o[1] - 158, "Z", size=15, bold=True, color=FIELD, anchor="start"))
    parts.append(text(o[0] - 6, o[1] - 158, "курс (yaw)", size=11, color=FIELD, anchor="end"))

    # «світ»: вектори вниз (g) і на північ (N) — абсолютні орієнтири
    wx, wy = 740, 250
    parts.append(text(wx, wy - 150, "система СВІТУ", size=13, bold=True, color=MUTED))
    parts.append(arrow(wx, wy - 120, wx, wy + 20, color=POS, sw=2.2))
    parts.append(text(wx + 8, wy + 16, "g (вниз)", size=12, color=POS, anchor="start"))
    parts.append(arrow(wx, wy - 60, wx + 110, wy - 90, color=FIELD, sw=2.2))
    parts.append(text(wx + 116, wy - 92, "північ", size=12, color=FIELD, anchor="start"))

    # стрілка-перерахунок тіло → світ
    parts.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2" stroke-dasharray="6,5" marker-end="url(#arrow)"/>'
                 % (cx + 200, cy - 60, 560, cy - 120, 620, wy - 120, wx - 40, wy - 100, INK))
    parts.append(mtext(560, cy - 134, "переклад\nтіло → світ", size=12, color=INK, bold=True, anchor="middle"))

    # підпис знизу
    box, bw, bh = textbox(W / 2, H - 30,
                          "IMU міряє в осях ТІЛА; орієнтацію дають відносно СВІТУ (крен · тангаж · курс)",
                          size=13, pad=12, fill=FILL)
    parts.append(box)

    render("img/axes-orientation.svg", W, H, *parts,
           title="Осі тіла й вихідна орієнтація апарата")


if __name__ == "__main__":
    fig_what_is_imu()
    fig_why_not_enough()
    fig_fusion_split()
    fig_axes_orientation()
    print("OK: what-is-imu, why-not-enough, fusion-split, axes-orientation")
