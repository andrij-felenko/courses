# -*- coding: utf-8 -*-
"""Фігури до теми «Узгодження сигналів керування» (вихідний каскад: серво й мотори).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Сигнал серво: ширина імпульсу = кут ───────────────────────────────────
def fig_signal():
    """Три імпульси різної ширини й відповідні положення качалки: 1000 мкс —
    один край, 1500 — центр, 2000 — інший; кадр ~20 мс (50 Гц). Показує, що
    носій кута — сама ширина імпульсу, а не його частота."""
    W, H = 760, 360
    f = [text(W / 2, 30, "Мова серво: ширина імпульсу кодує кут", size=17, bold=True)]

    ox, oy = 70, 150        # базова лінія імпульсів
    f.append(line(ox, oy, ox + 620, oy, color=LINE, sw=1.4))
    f.append(text(ox + 620, oy + 18, "час →", size=12, color=MUTED, anchor="end"))

    # три імпульси різної ширини на спільній осі
    cases = [(0, 26, "1000 мкс", "край", NEG),
             (210, 60, "1500 мкс", "центр", FIELD),
             (420, 96, "2000 мкс", "інший край", POS)]
    top = oy - 60
    for dx, w, lab, sub, col in cases:
        x = ox + dx + 10
        f.append(line(x, oy, x, top, color=col, sw=2.4))
        f.append(line(x, top, x + w, top, color=col, sw=2.4))
        f.append(line(x + w, top, x + w, oy, color=col, sw=2.4))
        f.append(text(x + w / 2, top - 8, lab, size=12, bold=True, color=col))
        f.append(text(x + w / 2, oy + 18, sub, size=11, color=MUTED))

    # позначка періоду кадру
    fr0, fr1 = ox + 10, ox + 10 + 200
    f.append(line(fr0, oy + 40, fr1, oy + 40, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text((fr0 + fr1) / 2, oy + 58, "кадр ~20 мс (50 Гц)", size=11, color=MUTED))

    f.append(text(W / 2, H - 22,
                  "положення задає ШИРИНА імпульсу; кадр лише визначає, як часто його оновлюють",
                  size=12, color=INK))
    return render(os.path.join(IMG, "signal.svg"), W, H, *f)


# ── 2. Від оберту до відхилення: качалка й тяга ──────────────────────────────
def fig_linkage():
    """Серво повертає качалку, жорстка тяга штовхає качалку керма, поверхня
    відхиляється на шарнірі. Довжини качалок задають передачу ходу й силу."""
    W, H = 760, 360
    f = [text(W / 2, 30, "Від оберту серво до відхилення поверхні", size=17, bold=True)]

    # корпус серво
    f.append(rect(70, 170, 120, 110, fill=FILL, stroke=LINE, sw=1.6))
    f.append(text(130, 230, "серво", size=13, bold=True))
    # вісь і качалка серво
    sx, sy = 190, 200
    f.append(circle(sx, sy, 7, fill="#fff", stroke=INK, sw=2))
    f.append(line(sx, sy, sx + 30, sy - 34, color=NEG, sw=4))   # качалка серво (важіль)
    f.append(text(sx + 6, sy - 46, "качалка серво", size=11, bold=True, color=NEG, anchor="start"))

    # жорстка тяга (пушрод)
    hx, hy = 520, 150       # вісь качалки керма
    f.append(line(sx + 30, sy - 34, hx - 26, hy + 30, color=INK, sw=3))
    f.append(text(360, 150, "жорстка тяга (пушрод)", size=12, bold=True, color=INK))

    # шарнір керма + качалка керма + поверхня
    f.append(circle(hx, hy, 7, fill="#fff", stroke=INK, sw=2))
    f.append(line(hx, hy, hx - 26, hy + 30, color=POS, sw=4))   # качалка керма
    f.append(text(hx - 30, hy + 50, "качалка керма", size=11, bold=True, color=POS, anchor="middle"))
    # поверхня (відхилена): від шарніра дві позиції
    f.append(line(hx, hy, hx + 150, hy, color=MUTED, sw=2, dash="6 5"))   # нейтраль
    f.append(line(hx, hy, hx + 146, hy - 36, color=FIELD, sw=5))          # відхилена
    f.append(text(hx + 150, hy - 44, "поверхня", size=12, bold=True, color=FIELD, anchor="middle"))
    f.append(text(hx + 150, hy + 18, "нейтраль", size=11, color=MUTED, anchor="middle"))

    f.append(text(W / 2, H - 22,
                  "довша качалка серво або коротша качалка керма → більший хід, але менша сила на поверхні",
                  size=12, color=INK))
    return render(os.path.join(IMG, "linkage.svg"), W, H, *f)


# ── 3. Вихідний каскад: бажаний рух → мікшер → виходи з узгодженням ───────────
def fig_outputs():
    """Контролер видає бажаний рух (крен/тангаж/курс/тяга); мікшер розкладає
    його за геометрією апарата; кожен вихід проходить узгодження (масштаб,
    реверс, трим, failsafe) і йде до свого виконавця — мотора через ESC або
    серво. Для контролера обидва типи — просто пронумеровані «виходи»."""
    W, H = 900, 430
    f = [text(W / 2, 30, "Вихідний каскад: бажаний рух стає сигналом кожному виконавцю", size=17, bold=True)]

    # лівий блок: бажаний рух
    f.append(rect(40, 110, 180, 230, fill="#eef6ef", stroke=FIELD, sw=1.7))
    f.append(text(130, 134, "бажаний рух", size=13, bold=True, color=FIELD))
    f.append(text(130, 150, "(від керування)", size=10, color=MUTED))
    for i, lab in enumerate(["крен (roll)", "тангаж (pitch)", "курс (yaw)", "загальна тяга"]):
        yy = 168 + i * 40
        f.append(rect(58, yy, 144, 30, fill=BG, stroke=FIELD, sw=1.1))
        f.append(text(130, yy + 20, lab, size=11))

    # мікшер
    f.append(fitbox(300, 175, 150, 100, "МІКШЕР\nрозкладає за\nгеометрією апарата",
                    size=12, bold=True, fill="#fbeee6", stroke=POS))
    f.append(arrow(220, 225, 298, 225))

    # виходи з узгодженням
    f.append(arrow(450, 225, 528, 225))
    outs = [("вихід 1 → ESC → мотор", NEG),
            ("вихід 2 → ESC → мотор", NEG),
            ("вихід 3 → серво (елерон)", FIELD),
            ("вихід 4 → серво (кермо)", FIELD)]
    for i, (lab, col) in enumerate(outs):
        yy = 120 + i * 56
        f.append(rect(530, yy, 330, 46, fill=BG, stroke=col, sw=1.4))
        f.append(text(546, yy + 20, lab, size=12, bold=True, color=col, anchor="start"))
        f.append(text(546, yy + 38, "узгодження: масштаб · реверс · трим · failsafe",
                      size=10, color=MUTED, anchor="start"))

    f.append(text(W / 2, H - 18,
                  "для контролера мотори (через ESC) і серво — однакові пронумеровані «виходи»",
                  size=12, color=INK))
    return render(os.path.join(IMG, "outputs.svg"), W, H, *f)


# ── 4. Мікшування: елевони літаючого крила ───────────────────────────────────
def fig_mixing():
    """Дві поверхні крила роблять і тангаж, і крен разом: обидві вгору — ніс
    угору (тангаж), різнойменно — крен. Один приклад того, як мікшер ховає
    геометрію апарата за абстракцією «виходів»."""
    W, H = 760, 380
    f = [text(W / 2, 30, "Мікшування на прикладі елевонів «літаючого крила»", size=17, bold=True)]

    # формули мікшера
    f.append(fitbox(60, 80, 300, 96,
                    "лівий елевон  = тангаж + крен\nправий елевон = тангаж − крен",
                    size=13, bold=True, fill=FILL, stroke=LINE))

    # дві ілюстрації крила
    def wing(cx, cy, l_up, r_up, title):
        # стрілки вгору (+) чи вниз (−) для лівої/правої поверхні
        f.append(text(cx, cy - 70, title, size=12, bold=True))
        # силует крила (трикутник)
        f.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
                 % (cx, cy - 30, cx - 110, cy + 30, cx + 110, cy + 30, FILL, LINE))
        f.append(text(cx, cy + 10, "крило", size=11, color=MUTED))
        # ліва поверхня
        col_l = POS if l_up > 0 else NEG
        f.append(line(cx - 80, cy + 30, cx - 80, cy + 30 - 34 * l_up, color=col_l, sw=4))
        f.append(arrow(cx - 80, cy + 30, cx - 80, cy + 30 - 34 * l_up, color=col_l, sw=4))
        # права поверхня
        col_r = POS if r_up > 0 else NEG
        f.append(line(cx + 80, cy + 30, cx + 80, cy + 30 - 34 * r_up, color=col_r, sw=4))
        f.append(arrow(cx + 80, cy + 30, cx + 80, cy + 30 - 34 * r_up, color=col_r, sw=4))

    wing(250, 250, 1, 1, "обидві вгору → підняти ніс (тангаж)")
    wing(560, 250, 1, -1, "різнойменно → накренити (крен)")

    f.append(text(W / 2, H - 18,
                  "ті самі дві поверхні несуть і тангаж, і крен — мікшер ховає цю геометрію",
                  size=12, color=INK))
    return render(os.path.join(IMG, "mixing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_signal()
    fig_linkage()
    fig_outputs()
    fig_mixing()
    print("OK: 4 фігури у", IMG)
