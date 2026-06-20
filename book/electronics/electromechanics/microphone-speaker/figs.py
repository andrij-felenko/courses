# -*- coding: utf-8 -*-
"""Фігури до теми «Мікрофон і динамік».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Взаємність: те саме перетворення в обидва боки ────────────────────────
def fig_reciprocity():
    W, H = 760, 320
    f = [text(W / 2, 28, "Один перетворювач — два напрями", size=17, bold=True)]

    def transducer(cx, cy):
        # магніт (підкова) спрощено як дві полюсні щоки + котушка між ними
        f.append(rect(cx - 70, cy - 46, 22, 92, fill="#dfe6ee", stroke=LINE, sw=2))
        f.append(rect(cx + 48, cy - 46, 22, 92, fill="#dfe6ee", stroke=LINE, sw=2))
        f.append(text(cx - 59, cy - 54, "N", size=13, bold=True, color=NEG))
        f.append(text(cx + 59, cy - 54, "S", size=13, bold=True, color=POS))
        # лінії поля між полюсами
        for k in range(3):
            yy = cy - 26 + k * 26
            f.append(line(cx - 48, yy, cx + 48, yy, color=FIELD, sw=1.6))
        # котушка (овал) у полі
        f.append('<ellipse cx="%.1f" cy="%.1f" rx="20" ry="34" fill="none" '
                 'stroke="%s" stroke-width="3"/>' % (cx, cy, POS))
        f.append(text(cx, cy + 50, "котушка в полі магніту", size=11, color=MUTED))

    # ЛІВО: динамік — струм робить рух
    transducer(180, 150)
    b, _, _ = textbox(180, 232, "СТРУМ → РУХ\n(динамік, навушник)", size=12,
                      fill="#fdecea", stroke=POS, bold=True)
    f.append(b)
    f.append(text(180, 286, "сигнал жене струм → котушка штовхає мембрану → звук",
                  size=11, color=MUTED))

    # ПРАВО: динамічний мікрофон — рух робить струм
    transducer(580, 150)
    b, _, _ = textbox(580, 232, "РУХ → СТРУМ\n(динамічний мікрофон)", size=12,
                      fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(b)
    f.append(text(580, 286, "звук рухає мембрану → котушка наводить струм → сигнал",
                  size=11, color=MUTED))

    # двобічна стрілка посередині
    f.append(arrow(300, 150, 458, 150, color=INK, sw=2))
    f.append(arrow(458, 168, 300, 168, color=INK, sw=2))
    f.append(text(379, 138, "та сама фізика", size=12, bold=True, color=INK))
    f.append(text(379, 188, "індукція ⇄ сила", size=11, color=FIELD))

    render(os.path.join(IMG, 'reciprocity.svg'), W, H, *f)


# ── 2. Три типи мікрофонів: на чому тримається кожен ─────────────────────────
def fig_mic_types():
    W, H = 780, 430
    f = [text(W / 2, 28, "Три способи перетворити звук на струм", size=17, bold=True)]

    col_w = 240
    x0 = [20, 270, 520]

    def membrane(cx, cy, color=INK):
        # хвиля звуку, що тисне на мембрану
        f.append('<path d="M %.1f %.1f q 10 -12 20 0 q 10 12 20 0 q 10 -12 20 0" '
                 'fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (cx - 78, cy, FIELD))
        f.append(line(cx - 6, cy - 30, cx - 6, cy + 30, color=color, sw=3))  # мембрана

    # --- електретний ---
    cx = x0[0] + col_w / 2
    f.append(rect(x0[0], 50, col_w, 350, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    f.append(text(cx, 76, "Електретний", size=14, bold=True))
    membrane(cx, 150)
    f.append(line(cx + 18, 120, cx + 18, 180, color=LINE, sw=3))  # нерухома пластина
    f.append(plus(cx - 6, 110, 7)); f.append(minus(cx + 18, 110, 7))
    f.append(text(cx, 210, "конденсатор:\nмембрана + пластина", size=11, color=INK))
    b, _, _ = textbox(cx, 252, "заряд «вшито»\nв електрет", size=11,
                      fill="#eef6ef", stroke=FIELD)
    f.append(b)
    f.append(text(cx, 300, "рух → зміна C → напруга", size=10, color=MUTED))
    f.append(text(cx, 332, "потрібен FET-підсилювач", size=10, color=MUTED))
    f.append(text(cx, 364, "дешевий, всюди до ~2010-х", size=10, color=POS))

    # --- MEMS ---
    cx = x0[1] + col_w / 2
    f.append(rect(x0[1], 50, col_w, 350, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    f.append(text(cx, 76, "MEMS", size=14, bold=True))
    membrane(cx, 150)
    f.append(line(cx + 18, 120, cx + 18, 180, color=LINE, sw=3))
    f.append(plus(cx - 6, 110, 7)); f.append(minus(cx + 18, 110, 7))
    f.append(text(cx, 210, "той самий конденсатор,\nале на кремнії", size=11, color=INK))
    b, _, _ = textbox(cx, 252, "мембрана\nвитравлена в чипі", size=11,
                      fill="#eef6ef", stroke=FIELD)
    f.append(b)
    f.append(text(cx, 300, "підсилювач у тому ж корпусі", size=10, color=MUTED))
    f.append(text(cx, 332, "часто одразу цифровий вихід", size=10, color=MUTED))
    f.append(text(cx, 364, "у кожному телефоні", size=10, color=POS))

    # --- динамічний ---
    cx = x0[2] + col_w / 2
    f.append(rect(x0[2], 50, col_w, 350, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    f.append(text(cx, 76, "Динамічний", size=14, bold=True))
    membrane(cx, 150)
    f.append('<ellipse cx="%.1f" cy="150" rx="12" ry="22" fill="none" '
             'stroke="%s" stroke-width="3"/>' % (cx + 16, POS))  # котушка
    f.append(rect(cx + 30, 128, 14, 44, fill="#dfe6ee", stroke=LINE, sw=2))  # магніт
    f.append(text(cx, 210, "котушка на мембрані\nв полі магніту", size=11, color=INK))
    b, _, _ = textbox(cx, 252, "ніякого живлення\nй заряду", size=11,
                      fill="#eaf0fd", stroke=NEG)
    f.append(b)
    f.append(text(cx, 300, "рух котушки → індукція → струм", size=10, color=MUTED))
    f.append(text(cx, 332, "міцний, любить гучне", size=10, color=MUTED))
    f.append(text(cx, 364, "сцена, студія, рація", size=10, color=POS))

    render(os.path.join(IMG, 'mic-types.svg'), W, H, *f)


# ── 3. Імпеданс і резонанс динаміка ──────────────────────────────────────────
def fig_impedance():
    W, H = 720, 400
    f = [text(W / 2, 28, "Чому «8 Ом» — це не весь динамік", size=17, bold=True)]

    # осі
    ox, oy = 90, 330           # початок координат
    aw, ah = 560, 250          # довжина осей
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))      # частота →
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.8))      # імпеданс ↑
    f.append(text(ox + aw - 8, oy + 24, "частота (лог)", size=12, color=INK, anchor="end"))
    f.append(text(ox - 12, oy - ah + 4, "|Z|, Ом", size=12, color=INK, anchor="end"))

    # лінія номіналу 8 Ом
    yR = oy - 60
    f.append(line(ox, yR, ox + aw, yR, color=MUTED, sw=1.4, dash="6 5"))
    f.append(text(ox + aw, yR - 8, "Rₑ ≈ 8 Ом (номінал)", size=11, color=MUTED, anchor="end"))

    # крива імпедансу: пік резонансу зліва, потім рівень, потім ріст від індуктивності
    # точки (приблизний хід)
    pts = [(ox + 20, yR + 6), (ox + 70, oy - 200), (ox + 120, yR + 4),
           (ox + 230, yR - 2), (ox + 340, yR + 2), (ox + 430, oy - 100),
           (ox + 540, oy - 165)]
    d = "M %.1f %.1f" % pts[0]
    for i in range(1, len(pts)):
        px, py = pts[i]
        d += " S %.1f %.1f %.1f %.1f" % (px - 24, py, px, py)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, POS))

    # позначка резонансу
    f.append(line(ox + 70, oy - 200, ox + 70, oy, color=FIELD, sw=1.2, dash="3 4"))
    f.append(text(ox + 70, oy - 210, "пік на fₛ", size=12, bold=True, color=FIELD))
    f.append(text(ox + 70, oy + 22, "fₛ", size=12, color=FIELD))
    b, _, _ = textbox(ox + 190, oy - 215, "механічний резонанс:\nмембрана легко гойдається",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    # позначка індуктивного росту
    b, _, _ = textbox(ox + 430, oy - 230, "котушка індуктивна:\nна високих |Z| росте",
                      size=11, fill="#fdecea", stroke=POS)
    f.append(b)

    # підпис плато
    f.append(text(ox + 285, yR + 22, "у середині |Z| близький до Rₑ", size=11, color=MUTED))

    render(os.path.join(IMG, 'impedance.svg'), W, H, *f)


if __name__ == "__main__":
    fig_reciprocity()
    fig_mic_types()
    fig_impedance()
    print("OK: figures written to", IMG)
