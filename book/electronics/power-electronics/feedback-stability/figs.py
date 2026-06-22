# -*- coding: utf-8 -*-
"""Фігури для теми feedback-stability (зворотний зв'язок і стабільність).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5).
Підписи фігур живуть у Markdown, не в SVG — тут лише сама графіка."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8860b"   # «на межі» / агресивний — бурштиновий


def fig_loop():
    """Чотири ланки контуру: силова частина → дільник → підсилювач похибки
    (з опорною) → контролер, і петля D назад. Той самий цикл, що в ПІД."""
    W, H = 900, 330
    frags = []
    # верхня лінія — силова частина й вузол Vвих
    b1 = fitbox(70, 120, 150, 64, "силова частина\n(ключ + котушка)", size=13,
                fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(b1)
    frags.append(line(220, 152, 320, 152, color=INK, sw=2))
    frags.append(circle(320, 152, 4, fill=INK, stroke=INK))
    frags.append(text(320, 138, "Vвих", size=13, color=POS, bold=True))
    frags.append(line(320, 152, 420, 152, color=INK, sw=2))
    # дільник
    frags.append(fitbox(360, 210, 120, 56, "дільник\n→ FB", size=13, fill="#eef7f0",
                        stroke=FIELD, bold=True))
    frags.append(line(320, 152, 320, 238, color=INK, sw=2))
    frags.append(line(320, 238, 360, 238, color=INK, sw=2))
    # підсилювач похибки
    frags.append(fitbox(520, 208, 150, 60, "підсилювач\nпохибки", size=13,
                        fill="#fdf3e3", stroke=GOLD, bold=True))
    frags.append(line(480, 238, 520, 238, color=INK, sw=2))
    frags.append(text(595, 300, "Vоп (еталон)", size=12, color=MUTED))
    frags.append(line(595, 292, 595, 270, color=MUTED, sw=1.6))
    # контролер
    frags.append(fitbox(720, 208, 140, 60, "контролер\nзадає D", size=13,
                        fill="#eaf0fd", stroke=NEG, bold=True))
    frags.append(arrow(670, 238, 720, 238, color=INK))
    # петля назад
    frags.append(line(790, 208, 790, 95, color=MUTED, sw=2))
    frags.append(line(790, 95, 145, 95, color=MUTED, sw=2))
    frags.append(arrow(145, 95, 145, 120, color=MUTED))
    frags.append(text(467, 87, "підправлена шпаруватість D", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "loop.svg"), W, H, *frags,
           title="Контур: виміряти → порівняти → виправити")


def fig_divider():
    """Дільник Rверх/Rниз від Vвих до FB; контролер тримає FB = Vоп, тож
    дільник і задає Vвих. Формула + числовий приклад збоку."""
    W, H = 880, 330
    frags = []
    cx = 250
    frags.append(circle(cx, 100, 4, fill=INK, stroke=INK))
    frags.append(text(cx, 86, "Vвих = 5 В", size=13, color=POS, bold=True))
    frags.append(line(cx, 100, cx, 140, color=INK, sw=2))
    frags.append(rect(cx - 22, 140, 44, 52, fill=BG, stroke=INK, sw=2, rx=3))
    frags.append(text(cx + 34, 170, "Rверх", size=12, color=INK, anchor="start", bold=True))
    frags.append(line(cx, 192, cx, 226, color=INK, sw=2))
    frags.append(circle(cx, 226, 4, fill=INK, stroke=INK))
    frags.append(text(cx - 12, 230, "FB", size=12, color=FIELD, anchor="end", bold=True))
    frags.append(text(cx + 12, 226, "= Vоп (0.8 В)", size=11, color=FIELD, anchor="start", bold=True))
    frags.append(rect(cx - 22, 258, 44, 52, fill=BG, stroke=INK, sw=2, rx=3))
    frags.append(text(cx + 34, 288, "Rниз", size=12, color=INK, anchor="start", bold=True))
    frags.append(line(cx, 310, cx, 322, color=INK, sw=2))
    frags.append(line(cx - 16, 322, cx + 16, 322, color=INK, sw=2))
    # відведення FB до підсилювача
    frags.append(line(cx, 226, 400, 226, color=FIELD, sw=2))
    frags.append(fitbox(400, 208, 84, 38, "підсил.", size=11, fill="#fdf3e3", stroke=GOLD, bold=True))
    # формула й приклад
    box, bw, bh = textbox(690, 175,
                          ["Vвих = Vоп · (1 + Rверх/Rниз)", "",
                           "5 В при Vоп = 0.8 В:",
                           "Rверх/Rниз = 5/0.8 − 1 = 5.25",
                           "напр. Rверх = 52.5 к, Rниз = 10 к"],
                          size=12, fill="#f4f6f8", stroke=MUTED)
    frags.append(box)
    render(os.path.join(OUT, "divider.svg"), W, H, *frags,
           title="Дільник задає вихідну напругу")


def _scope_panel(x, y, w, h, title, color, pts):
    """Панель-осцилограма: рамка, ціль-пунктир, вісь, крива pts (нормовані 0..1)."""
    out = [rect(x, y, w, h, fill=BG, stroke="#e2e2e2", sw=2, rx=10)]
    out.append(text(x + w / 2, y + 26, title, size=13, color=color, bold=True))
    ax = x + 26
    aytop, aybot = y + 46, y + h - 30
    base = y + h * 0.46            # рівень цілі
    out.append(line(ax, base, x + w - 18, base, color=MUTED, sw=1.2, dash="5,4"))
    out.append(line(ax, aytop, ax, aybot, color=INK, sw=1.3))
    span = (x + w - 24) - ax
    amp = (aybot - base)
    poly = []
    for t, v in pts:
        px = ax + t * span
        py = base + v * amp        # v>0 — нижче цілі (провал)
        poly.append("%.1f,%.1f" % (px, py))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
               'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(poly), color))
    return "".join(out)


def fig_speed_vs_stability():
    """Три реакції на той самий стрибок: заповільний (глибокий млявий провал),
    здоровий (малий провал, чисто), агресивний (дзвенить)."""
    W, H = 900, 300
    pw, ph, y = 280, 230, 56
    slow = [(0, 0), (0.18, 0), (0.22, 0.95), (0.55, 0.5), (1, 0.08)]
    good = [(0, 0), (0.18, 0), (0.22, 0.55), (0.34, 0.05), (1, 0)]
    fast = [(0, 0), (0.16, 0), (0.20, 0.7), (0.30, -0.55), (0.42, 0.45),
            (0.54, -0.32), (0.66, 0.22), (0.80, -0.1), (1, 0)]
    frags = [
        _scope_panel(15, y, pw, ph, "Заповільний", POS, slow),
        _scope_panel(310, y, pw, ph, "Здоровий", FIELD, good),
        _scope_panel(605, y, pw, ph, "Агресивний", GOLD, fast),
    ]
    render(os.path.join(OUT, "speed-vs-stability.svg"), W, H, *frags,
           title="Три реакції на той самий стрибок навантаження")


def fig_ringing():
    """Цикл перекорекції із запізненням (4 вузли по колу) + аналогія з водієм."""
    W, H = 900, 340
    frags = []
    ccx, ccy, r = 245, 195, 92
    nodes = [(ccx, ccy - r, "вихід просів", "middle", -14),
             (ccx + r, ccy, "СИЛЬНО додав D", "start", 0),
             (ccx, ccy + r, "вихід перескочив", "middle", 26),
             (ccx - r, ccy, "різко прибрав D", "end", 0)]
    for nx, ny, lbl, anch, dy in nodes:
        frags.append(circle(nx, ny, 6, fill=GOLD, stroke=GOLD))
    # підписи вузлів
    frags.append(text(ccx, ccy - r - 14, "вихід просів", size=11, color=INK, bold=True))
    frags.append(text(ccx + r + 12, ccy + 4, "СИЛЬНО додав D", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(ccx, ccy + r + 24, "вихід перескочив", size=11, color=INK, bold=True))
    frags.append(text(ccx - r - 12, ccy + 4, "різко прибрав D", size=11, color=INK, anchor="end", bold=True))
    # дуги по колу зі стрілками
    rr = r - 14
    frags.append('<path d="M %.0f %.0f A %d %d 0 0 1 %.0f %.0f" fill="none" stroke="%s" '
                 'stroke-width="2.4" marker-end="url(#arrow)"/>'
                 % (ccx + 22, ccy - rr + 4, rr, rr, ccx + rr - 4, ccy - 22, GOLD))
    frags.append('<path d="M %.0f %.0f A %d %d 0 0 1 %.0f %.0f" fill="none" stroke="%s" '
                 'stroke-width="2.4" marker-end="url(#arrow)"/>'
                 % (ccx + rr - 4, ccy + 22, rr, rr, ccx + 22, ccy + rr - 4, GOLD))
    frags.append('<path d="M %.0f %.0f A %d %d 0 0 1 %.0f %.0f" fill="none" stroke="%s" '
                 'stroke-width="2.4" marker-end="url(#arrow)"/>'
                 % (ccx - 22, ccy + rr - 4, rr, rr, ccx - rr + 4, ccy + 22, GOLD))
    frags.append('<path d="M %.0f %.0f A %d %d 0 0 1 %.0f %.0f" fill="none" stroke="%s" '
                 'stroke-width="2.4" marker-end="url(#arrow)"/>'
                 % (ccx - rr + 4, ccy - 22, rr, rr, ccx - 22, ccy - rr + 4, GOLD))
    # панель аналогії
    frags.append(rect(500, 80, 380, 210, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=12))
    frags.append(text(690, 108, "Аналогія: водій на слизькому", size=13, color=FIELD, bold=True))
    for i, ln in enumerate(["занесло вліво →",
                            "різко крутить кермо вправо →",
                            "заносить вправо →",
                            "крутить вліво… і так гойдається."]):
        frags.append(text(520, 138 + i * 22, ln, size=12, color=INK, anchor="start"))
    frags.append(text(520, 244, "Спокійніший (повільніший) водій", size=12, color=FIELD, anchor="start", bold=True))
    frags.append(text(520, 264, "не перекручує — і занос гасне.", size=12, color=FIELD, anchor="start", bold=True))
    render(os.path.join(OUT, "ringing.svg"), W, H, *frags,
           title="Чому контур дзвенить: перекорекція із запізненням")


def fig_load_step():
    """Тест стрибком навантаження: три осцилограми виходу — здоровий, на межі,
    нестійкий."""
    W, H = 900, 300
    pw, ph, y = 280, 230, 56
    good = [(0, 0), (0.20, 0), (0.24, 0.6), (0.36, 0.05), (1, 0)]
    edge = [(0, 0), (0.20, 0), (0.24, 0.7), (0.34, -0.5), (0.46, 0.4),
            (0.58, -0.28), (0.70, 0.16), (0.84, -0.06), (1, 0)]
    unst = [(0, 0), (0.18, 0), (0.24, 0.85), (0.34, -0.75), (0.44, 0.85),
            (0.54, -0.75), (0.64, 0.85), (0.74, -0.75), (0.84, 0.85), (0.94, -0.75)]
    frags = [
        _scope_panel(15, y, pw, ph, "Здоровий", FIELD, good),
        _scope_panel(310, y, pw, ph, "На межі", GOLD, edge),
        _scope_panel(605, y, pw, ph, "Нестійкий", POS, unst),
    ]
    render(os.path.join(OUT, "load-step.svg"), W, H, *frags,
           title="Тест стрибком навантаження на осцилографі")


def fig_output_cap():
    """Підступ: компенсацію зашито під певні C та ESR виходу; ESR часто додає
    стійкості, гола кераміка може розхитати. Дві панелі."""
    W, H = 900, 300
    frags = []
    frags.append(rect(45, 70, 380, 190, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=12))
    frags.append(text(235, 98, "Компенсацію зашито під", size=13, color=FIELD, bold=True))
    frags.append(text(235, 117, "певні C та ESR виходу", size=13, color=FIELD, bold=True))
    for i, ln in enumerate(["• ESR часто ДОДАЄ стійкості",
                            "• гола кераміка (ESR ≈ 0) —",
                            "   навпаки, може розхитати",
                            "• інша ємність зсуває швидкість"]):
        frags.append(text(66, 150 + i * 24, ln, size=12, color=INK, anchor="start"))
    frags.append(rect(475, 70, 380, 190, fill="#fdecea", stroke=POS, sw=1.8, rx=12))
    frags.append(text(665, 98, "Поміняв кондер — перевір!", size=13, color=POS, bold=True))
    for i, ln in enumerate(["Заміна електроліта на кераміку",
                            "(менший ESR) може розхитати",
                            "стійкий контур — і навпаки."]):
        frags.append(text(496, 128 + i * 22, ln, size=12, color=INK, anchor="start"))
    frags.append(text(496, 202, "Після зміни вихідного кондера —", size=12, color=INK, anchor="start", bold=True))
    frags.append(text(496, 222, "знову тест load-step.", size=12, color=INK, anchor="start", bold=True))
    frags.append(text(496, 246, "Даташит часто задає діапазон C/ESR.", size=11, color=MUTED, anchor="start"))
    render(os.path.join(OUT, "output-cap.svg"), W, H, *frags,
           title="Вихідний конденсатор впливає на стійкість")


def fig_load_step_numbers():
    """Вставка: стрибок струму → миттєвий ESR-крок + просадка ємності = провал;
    далі дзвін лічать у циклах. Осцилограма струму згори, напруги знизу."""
    W, H = 900, 380
    frags = []
    ax = 100
    # струм навантаження
    frags.append(text(ax - 14, 92, "Iнаван", size=11, color=INK, anchor="end", bold=True))
    frags.append(line(ax, 120, 320, 120, color="#b5763a", sw=2.4))
    frags.append(line(320, 120, 320, 92, color="#b5763a", sw=2.4))
    frags.append(line(320, 92, 820, 92, color="#b5763a", sw=2.4))
    frags.append(text(210, 136, "0.5 А", size=10, color=MUTED))
    frags.append(text(560, 82, "3 А   (ΔI = 2.5 А)", size=10, color=MUTED))
    # напруга виходу
    frags.append(text(ax - 14, 196, "Vвих", size=11, color=INK, anchor="end", bold=True))
    base = 240
    frags.append(line(ax, base, 820, base, color=MUTED, sw=1.3, dash="6,4"))
    frags.append(text(826, base + 4, "ціль", size=10, color=MUTED, anchor="start"))
    poly = ["100,240", "320,240", "323,258", "340,310", "360,282", "382,306",
            "404,290", "428,300", "456,294", "490,298", "560,250", "820,242"]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
                 'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(poly), NEG))
    # ESR-крок
    frags.append(line(323, 240, 323, 258, color=POS, sw=1.8, dash="3,2"))
    frags.append(text(300, 252, "ESR-крок = ΔI·ESR", size=10, color=POS, anchor="end", bold=True))
    # просадка
    frags.append('<line x1="346" y1="240" x2="346" y2="310" stroke="%s" stroke-width="1.6" '
                 'marker-end="url(#arrow)"/>' % GOLD)
    frags.append(text(356, 326, "провал ≈ ΔI·ESR + ΔI·tвідгук/C", size=11, color=GOLD, anchor="start", bold=True))
    # рамка з лічбою циклів
    box, bw, bh = textbox(680, 150,
                          ["Лічба «на пальцях»:",
                           "0 циклів → добрий запас",
                           "1–2 цикли → на межі",
                           "не вгаває → нестійко"],
                          size=12, fill="#f4f6f8", stroke=MUTED)
    frags.append(box)
    render(os.path.join(OUT, "load-step-numbers.svg"), W, H, *frags,
           title="Провал і дзвін на стрибку: глибина + цикли")


if __name__ == "__main__":
    fig_loop()
    fig_divider()
    fig_speed_vs_stability()
    fig_ringing()
    fig_load_step()
    fig_output_cap()
    fig_load_step_numbers()
    print("ok figs")
