# -*- coding: utf-8 -*-
"""Фігури до вставки proj-link-calc.md («Калькулятор бюджету радіолінії на C»).
Окремий генератор (щоб не конфліктувати з figs.py, який пишуть паралельно).
Запуск:  python figs_link_calc.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b9770e"


# ── Конвеєр калькулятора бюджету ─────────────────────────────────────────────
def fig_calc_pipeline():
    W, H = 960, 470
    f = [text(W / 2, 30, "Калькулятор бюджету: як тече розрахунок", size=18, bold=True),
         text(W / 2, 52, "TX-сторона → EIRP з ОБРІЗАННЯМ стелею → мінус шлях; чутливість з фізики → запас → доступність",
              size=11, color=MUTED, italic=True)]

    # ── ліва колонка входів ──
    inx = 40
    f.append(fitbox(inx, 96, 150, 70, "P_tx, G_tx\nL_cable_tx",
                    size=12, fill="#eef2ff", stroke=NEG, bold=True))
    f.append(fitbox(inx, 200, 150, 70, "d, f\nL_misc, G_rx",
                    size=12, fill="#eef2ff", stroke=NEG, bold=True))
    f.append(fitbox(inx, 304, 150, 70, "B, NF\nSNR_min",
                    size=12, fill="#eef2ff", stroke=NEG, bold=True))
    f.append(text(inx + 75, 392, "параметри радіо", size=10.5, color=MUTED, italic=True))

    # ── блок EIRP з обрізанням (головний, золотий) ──
    ex, ey, ew, eh = 250, 96, 210, 84
    f.append(rect(ex, ey, ew, eh, fill="#fff4e6", stroke=GOLD, sw=2.4, rx=10))
    f.append(text(ex + ew / 2, ey + 24, "EIRP = P_tx − L + G_tx", size=12, color=INK, bold=True))
    f.append(text(ex + ew / 2, ey + 46, "ОБРІЗАТИ до стелі регіону:", size=10.5, color=GOLD, bold=True))
    f.append(text(ex + ew / 2, ey + 64, "ETSI +20 · FCC +36 дБм", size=10.5, color=INK))

    # ── блок FSPL/шлях ──
    px, py, pw, ph = 250, 214, 210, 60
    f.append(fitbox(px, py, pw, ph, "− FSPL(d,f) − L_misc\n+ G_rx − L_cable_rx",
                    size=11.5, fill="#fbfdfb", stroke=FIELD, bold=True))

    # ── блок чутливості ──
    sx, sy, sw2, sh = 250, 308, 210, 60
    f.append(fitbox(sx, sy, sw2, sh, "S_rx = −174 + 10logB\n+ NF + SNR_min",
                    size=11.5, fill="#f6f7f9", stroke=MUTED, bold=True))

    # стрілки входів у блоки
    f.append(arrow(inx + 150, 131, ex, ey + 30, color=NEG))
    f.append(arrow(inx + 150, 235, px, py + 20, color=NEG))
    f.append(arrow(inx + 150, 339, sx, sy + 20, color=NEG))

    # ── P_rx (зведення EIRP + шлях) ──
    rx, ry, rw, rh = 540, 150, 170, 70
    f.append(rect(rx, ry, rw, rh, fill="#eef7ff", stroke=NEG, sw=2, rx=10))
    f.append(text(rx + rw / 2, ry + 28, "P_rx", size=14, color=NEG, bold=True))
    f.append(text(rx + rw / 2, ry + 48, "на вході приймача", size=10, color=INK))
    f.append(arrow(ex + ew, ey + eh / 2, rx, ry + 24, color=GOLD))
    f.append(arrow(px + pw, py + ph / 2, rx, ry + 46, color=FIELD))

    # ── запас (P_rx − S_rx) ──
    mx, my, mw, mh = 540, 300, 170, 60
    f.append(rect(mx, my, mw, mh, fill="#eafaf0", stroke=FIELD, sw=2.2, rx=10))
    f.append(text(mx + mw / 2, my + 24, "запас = P_rx − S_rx", size=12, color=FIELD, bold=True))
    f.append(text(mx + mw / 2, my + 44, "скільки дБ над порогом", size=9.5, color=INK))
    f.append(arrow(rx + rw / 2, ry + rh, mx + mw / 2 - 20, my, color=NEG))
    f.append(arrow(sx + sw2, sy + sh / 2, mx, my + 40, color=MUTED))

    # ── доступність (фінал) ──
    ax, ay, aw, ah = 770, 300, 160, 60
    f.append(rect(ax, ay, aw, ah, fill="#fdecea", stroke=POS, sw=2.4, rx=10))
    f.append(text(ax + aw / 2, ay + 24, "доступність", size=12.5, color=POS, bold=True))
    f.append(text(ax + aw / 2, ay + 44, "1 − 10^(−M/10)", size=11, color=INK, bold=True))
    f.append(arrow(mx + mw, my + mh / 2, ax, ay + ah / 2, color=FIELD))

    f.append(text(W / 2, H - 14,
                  "Обрізання EIRP до легальної стелі — блок, якого нема в наївних калькуляторах; запас перекладаємо у % часу, коли лінія жива.",
                  size=10.5, color=INK, italic=True))
    return render(os.path.join(IMG, 'calc-pipeline.svg'), W, H, *f)


# ── Польове рішення: RSSI → запас → доступність → стан лінії ──────────────────
def fig_rssi_decision():
    W, H = 940, 430
    f = [text(W / 2, 30, "Польовий хід: від виміряного RSSI до рішення апарата", size=18, bold=True),
         text(W / 2, 52, "радіочип дає RSSI; калькулятор перекладає його на відсоток доступності, а той — на курс",
              size=11, color=MUTED, italic=True)]

    # ланцюг зліва направо
    y0 = 110
    f.append(fitbox(40, y0, 160, 60, "RSSI (дБм)\nз радіочипа", size=12, fill="#eef2ff", stroke=NEG, bold=True))
    f.append(fitbox(250, y0, 170, 60, "запас = RSSI − S_rx", size=11.5, fill="#eafaf0", stroke=FIELD, bold=True))
    f.append(fitbox(470, y0, 190, 60, "доступність =\n1 − 10^(−M/10)", size=11.5, fill="#fdecea", stroke=POS, bold=True))
    f.append(fitbox(710, y0, 190, 60, "стан лінії →\nрішення керування", size=11.5, fill="#fff4e6", stroke=GOLD, bold=True))
    f.append(arrow(200, y0 + 30, 250, y0 + 30, color=INK))
    f.append(arrow(420, y0 + 30, 470, y0 + 30, color=INK))
    f.append(arrow(660, y0 + 30, 710, y0 + 30, color=INK))

    # три стани-рішення (пороги за доступністю)
    ty = 230
    states = [
        ("≥ 20 дБ  (~99 %)", "ТРИМАТИ КУРС", "лінія певна, летимо далі", FIELD, "#eafaf0"),
        ("10–20 дБ (~90–99 %)", "НАБЛИЗИТИСЯ", "запас тане — обережно", GOLD, "#fff4e6"),
        ("< 10 дБ  (< ~90 %)", "РОЗВОРОТ НА БАЗУ", "провали часті — рветься", POS, "#fdecea"),
    ]
    bw = 280
    for i, (rng, act, note, col, fillc) in enumerate(states):
        bx = 40 + i * 300
        f.append(rect(bx, ty, bw, 120, fill=fillc, stroke=col, sw=2.2, rx=12))
        f.append(text(bx + bw / 2, ty + 30, rng, size=12.5, color=INK, bold=True))
        f.append(line(bx + 20, ty + 44, bx + bw - 20, ty + 44, color=col, sw=1.2))
        f.append(text(bx + bw / 2, ty + 72, act, size=15, color=col, bold=True))
        f.append(text(bx + bw / 2, ty + 98, note, size=10.5, color=INK, italic=True))

    f.append(text(W / 2, H - 14,
                  "Апарат питає не «є сигнал?», а «в який відсоток часу лінія жива?» — і саме це задає поведінку.",
                  size=10.5, color=INK, italic=True))
    return render(os.path.join(IMG, 'rssi-decision.svg'), W, H, *f)


if __name__ == '__main__':
    fig_calc_pipeline()
    fig_rssi_decision()
    print('OK: calc-pipeline.svg, rssi-decision.svg')
