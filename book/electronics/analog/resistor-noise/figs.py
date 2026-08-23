# -*- coding: utf-8 -*-
"""Фігури до теми «Тепловий шум» (аналогова електроніка, кутом теорії кіл).
Три фігури:
  noise-source.svg   — модель резистора: ідеальний R + послідовне джерело шумової ЕРС
  signal-chain.svg   — шум опору джерела стоїть ПЕРЕД підсилювачем, послідовно з сигналом
  vn-in.svg          — два «бруски» шуму ОП (eₙ і iₙ·R) і яка з них головна за різних R
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def noise_source():
    """Реальний резистор = ідеальний (безшумний) R послідовно з джерелом шумової ЕРС."""
    W, H = 700, 320
    p = []
    # Ліворуч: реальний резистор-«чорна скринька»
    bx, by, bw, bh = 70, 120, 150, 80
    p.append(rect(bx, by, bw, bh, fill=FILL))
    p.append(text(bx + bw / 2, by - 14, "реальний резистор R", size=14, bold=True))
    p.append(text(bx + bw / 2, by + bh / 2 + 5, "R", size=22, bold=True))
    # виводи
    p.append(line(bx - 30, by + bh / 2, bx, by + bh / 2))
    p.append(line(bx + bw, by + bh / 2, bx + bw + 30, by + bh / 2))
    p.append(circle(bx - 30, by + bh / 2, 4, fill=INK, stroke=INK))
    p.append(circle(bx + bw + 30, by + bh / 2, 4, fill=INK, stroke=INK))

    # Стрілка «дорівнює моделі»
    p.append(arrow(bx + bw + 50, by + bh / 2, bx + bw + 130, by + bh / 2, color=INK, sw=2.2))
    p.append(text(bx + bw + 90, by + bh / 2 - 12, "=", size=20, bold=True))

    # Праворуч: модель = безшумний R + джерело шуму eₙ
    mx = 420
    cy = by + bh / 2
    # безшумний R (прямокутник-резистор)
    rx0 = mx
    p.append(rect(rx0, cy - 16, 70, 32, fill=BG))
    p.append(text(rx0 + 35, cy + 5, "R", size=16, bold=True))
    p.append(text(rx0 + 35, cy - 28, "безшумний", size=11, color=MUTED))
    # дріт до джерела
    p.append(line(rx0 + 70, cy, rx0 + 110, cy))
    # джерело шумової ЕРС — коло з «~»
    sx = rx0 + 140
    p.append(circle(sx, cy, 26, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(sx, cy + 6, "~", size=24, color=POS, bold=True))
    p.append(text(sx, cy + 52, "eₙ = √(4kTR)", size=14, color=POS, bold=True))
    p.append(text(sx, cy + 70, "на корінь з герца", size=11, color=MUTED))
    # виводи моделі
    p.append(line(rx0 - 30, cy, rx0, cy))
    p.append(line(sx + 26, cy, sx + 56, cy))
    p.append(circle(rx0 - 30, cy, 4, fill=INK, stroke=INK))
    p.append(circle(sx + 56, cy, 4, fill=INK, stroke=INK))

    b, _, _ = textbox(W / 2, 280, "Опір лишається опором; уся «шумність» зібрана\nв окреме послідовне джерело напруги eₙ.",
                      size=13, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'noise-source.svg'), W, H, *p,
           title="Модель шумного резистора: безшумний R + джерело шумової ЕРС")


def signal_chain():
    """Шум опору джерела — послідовно з корисним сигналом, ще ДО входу підсилювача."""
    W, H = 720, 300
    p = []
    cy = 150
    # Давач: джерело сигналу Vs
    sx = 70
    p.append(circle(sx, cy, 24, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(sx, cy + 6, "Vs", size=15, color=NEG, bold=True))
    p.append(text(sx, cy - 40, "давач (сигнал)", size=12, bold=True))
    # послідовно: опір джерела Rs (резистор-прямокутник)
    p.append(line(sx + 24, cy, sx + 60, cy))
    rxx = sx + 60
    p.append(rect(rxx, cy - 15, 64, 30, fill=BG))
    p.append(text(rxx + 32, cy + 5, "Rs", size=15, bold=True))
    p.append(text(rxx + 32, cy - 26, "опір джерела", size=11, color=MUTED))
    # послідовно: джерело шуму eₙ (того ж Rs)
    p.append(line(rxx + 64, cy, rxx + 100, cy))
    nx = rxx + 126
    p.append(circle(nx, cy, 22, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(nx, cy + 6, "~", size=22, color=POS, bold=True))
    p.append(text(nx, cy - 34, "шум Rs", size=12, color=POS, bold=True))
    p.append(text(nx, cy + 46, "eₙ = √(4kT·Rs·B)", size=12, color=POS))
    # дріт до підсилювача
    p.append(line(nx + 22, cy, nx + 70, cy))
    # підсилювач — трикутник
    ax = nx + 70
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (ax, cy - 40, ax, cy + 40, ax + 80, cy, FILL, LINE))
    p.append(text(ax + 28, cy + 6, "×G", size=18, bold=True))
    p.append(text(ax + 30, cy - 52, "підсилювач", size=12, bold=True))
    # вихід
    p.append(line(ax + 80, cy, ax + 130, cy))
    p.append(circle(ax + 130, cy, 4, fill=INK, stroke=INK))
    p.append(text(ax + 130, cy - 14, "вихід", size=12, color=MUTED))
    # земля під сигнальною лінією
    p.append(line(sx, cy + 24, sx, cy + 70))
    p.append(line(sx, cy + 70, ax + 130, cy + 70))
    p.append(line(ax + 130, cy + 70, ax + 130, cy))
    p.append(text((sx + ax) / 2, cy + 86, "спільний провід (земля)", size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 262,
                      "Сигнал і шум Rs ідуть однією лінією й множаться на те саме G.\n"
                      "Підсилювач не «додає» цей шум — він приходить уже з джерела.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'signal-chain.svg'), W, H, *p,
           title="Тепловий шум опору джерела стоїть ПЕРЕД підсилювачем")


def vn_in():
    """Два внески шуму підсилювача: eₙ (стала) і iₙ·R (росте з R) — хто головний за різних R."""
    W, H = 700, 380
    p = []
    # осі
    ox, oy = 90, 300          # початок координат
    ax_w, ax_h = 540, 230
    p.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))        # X
    p.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))        # Y
    p.append(text(ox + ax_w / 2, oy + 46, "опір джерела R (лог. шкала) →", size=13, bold=True))
    p.append(text(ox - 60, oy - ax_h / 2, "внесок", size=13, bold=True, anchor="middle"))
    p.append(text(ox - 60, oy - ax_h / 2 + 18, "у шум", size=13, bold=True, anchor="middle"))

    # eₙ — горизонтальна полиця (не залежить від R)
    en_y = oy - 70
    p.append(line(ox, en_y, ox + ax_w, en_y, color=NEG, sw=2.6))
    p.append(text(ox + ax_w - 4, en_y - 10, "eₙ  — шум напруги ОП (стала)", size=13, color=NEG, bold=True, anchor="end"))

    # iₙ·R — росте з R (пряма вгору в лог-лог)
    p.append(line(ox + 10, oy - 8, ox + ax_w - 10, oy - ax_h + 18, color=POS, sw=2.6))
    p.append(text(ox + 16, oy - ax_h + 36, "iₙ·R — шум струму на R (росте)", size=13, color=POS, bold=True, anchor="start"))

    # тепловий шум самого R: √(4kTR) — теж росте, але як корінь (пунктир)
    p.append(line(ox + 10, oy - 30, ox + ax_w - 10, oy - 150, color=FIELD, sw=2.4, dash="7 5"))
    p.append(text(ox + ax_w - 10, oy - 150 - 8, "√(4kTR) — шум самого R", size=12, color=FIELD, bold=True, anchor="end"))

    # точка перетину eₙ та iₙ·R — оптимальний R
    cxr = ox + ax_w * 0.52
    p.append(circle(cxr, en_y, 5, fill=INK, stroke=INK))
    p.append(line(cxr, en_y, cxr, oy, color=MUTED, sw=1, dash="3 3"))
    p.append(text(cxr, oy + 22, "R_opt = eₙ / iₙ", size=12, color=INK, bold=True))

    # зони
    p.append(text(ox + 70, oy - ax_h + 10, "малий R:\nкерує eₙ", size=11, color=NEG, anchor="middle"))
    p.append(text(ox + ax_w - 70, oy - ax_h + 10, "великий R:\nкерує iₙ·R", size=11, color=POS, anchor="middle"))

    b, _, _ = textbox(W / 2, 350,
                      "Сумарний шум — корінь із суми квадратів цих трьох. За малих R головний eₙ,\n"
                      "за великих — iₙ·R; найтихіше там, де R близький до R_opt = eₙ/iₙ.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'vn-in.svg'), W, H, *p,
           title="Який шум головний: напруги eₙ чи струму iₙ·R — залежить від опору джерела")


if __name__ == '__main__':
    noise_source()
    signal_chain()
    vn_in()
    print("OK: 3 figures ->", OUT)
