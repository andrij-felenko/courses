# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def gear(cx, cy, r, teeth, color=LINE, fill="#e8edf3", sw=1.3):
    """Проста шестерня — коло з трикутними зубцями, щоб показати редуктор."""
    pts = []
    n = teeth * 2
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r if i % 2 == 0 else r * 0.82
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d = "M %.2f %.2f " % pts[0] + " ".join("L %.2f %.2f" % p for p in pts[1:]) + " Z"
    out = '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, color, sw)
    out += circle(cx, cy, r * 0.22, fill=BG, stroke=color, sw=sw)
    return out


def fig_inside():
    """Що всередині серва: сигнал → мозок (компаратор) → мотор → редуктор →
    вал + потенціометр, і зворотний зв'язок від потенціометра назад у мозок.
    Це замкнена петля позиціювання — серце будь-якого хобі-серва.
    Ланцюг тримаємо в один рядок зверху, зворотний зв'язок ведемо низом
    порожнім коридором — жодна лінія не перетинає напис."""
    W, H = 860, 430
    frags = []
    frags.append(text(W / 2, 30, "Що всередині: замкнена петля за положенням", size=17, bold=True))

    row = 150  # головний ряд блоків

    # --- вхід сигналу ---
    frags.append(text(40, row - 22, "сигнал", size=11, bold=True, color=FIELD, anchor="start"))
    frags.append(text(40, row - 7, "1520 мкс", size=10.5, color=FIELD, anchor="start"))
    frags.append(arrow(42, row + 8, 120, row + 8, color=FIELD, sw=2))

    # --- блок «мозок» (керувальна плата / компаратор) ---
    bx, by, bw, bh = 122, 120, 168, 92
    frags.append(rect(bx, by, bw, bh, fill="#eef2ff", stroke=NEG, sw=1.6))
    frags.append(text(bx + bw / 2, by + 26, "Керувальна плата", size=13, bold=True, color=NEG))
    frags.append(text(bx + bw / 2, by + 48, "порівнює ціль ↔ факт", size=10.5, color=INK))
    frags.append(text(bx + bw / 2, by + 68, "«де маю / де я є»", size=10.5, color=MUTED))

    # --- мотор ---
    mcx, mcy, mr = 400, row + 15, 40
    frags.append(circle(mcx, mcy, mr, fill="#fff1f0", stroke=POS, sw=1.6))
    frags.append(text(mcx, mcy - 5, "DC", size=15, bold=True, color=POS))
    frags.append(text(mcx, mcy + 15, "мотор", size=12, color=POS))
    frags.append(arrow(bx + bw, by + 34, mcx - mr - 2, mcy, color=POS, sw=2))
    frags.append(text((bx + bw + mcx - mr) / 2, by + 22, "струм на мотор", size=10, color=POS))

    # --- редуктор (дві шестерні) ---
    gx, gy = 540, row + 40
    frags.append(gear(gx, gy, 28, 12))
    frags.append(gear(gx + 48, gy - 30, 20, 9))
    frags.append(arrow(mcx + mr + 2, mcy, gx - 22, gy, color=LINE, sw=1.8))
    frags.append(text(gx - 4, gy + 52, "редуктор", size=11, bold=True, color=MUTED))
    frags.append(text(gx - 4, gy + 68, "оберти → сила", size=10, color=MUTED))

    # --- вихідний вал + ріг ---
    sx, sy = 700, row + 8
    frags.append(circle(sx, sy, 26, fill="#e8edf3", stroke=LINE, sw=1.5))
    frags.append(circle(sx, sy, 9, fill=BG, stroke=LINE, sw=1.3))
    frags.append(text(sx, sy - 40, "вихідний вал", size=12, bold=True))
    frags.append(text(sx, sy - 24, "(сюди — ріг)", size=10, color=MUTED))
    frags.append(arrow(gx + 68, gy - 30, sx - 22, sy, color=LINE, sw=1.8))

    # --- потенціометр під валом (спільна вісь) ---
    px, py, pw, ph = sx - 78, sy + 48, 156, 42
    frags.append(rect(px, py, pw, ph, fill="#f0fff4", stroke=FIELD, sw=1.5))
    frags.append(text(px + pw / 2, py + 18, "потенціометр", size=12, bold=True, color=FIELD))
    frags.append(text(px + pw / 2, py + 34, "міряє кут валу", size=10, color=INK))
    frags.append(line(sx, sy + 26, sx, py, color=FIELD, sw=1.6, dash="3 3"))

    # --- зворотний зв'язок: потенціометр → низ → мозок (порожній коридор) ---
    corr = 380  # горизонтальний коридор під усім
    frags.append(line(px, py + ph / 2, px - 40, py + ph / 2, color=FIELD, sw=2))
    frags.append(line(px - 40, py + ph / 2, px - 40, corr, color=FIELD, sw=2))
    frags.append(line(px - 40, corr, bx + 40, corr, color=FIELD, sw=2))
    frags.append(arrow(bx + 40, corr, bx + 40, by + bh, color=FIELD, sw=2))
    b, _, _ = textbox(W / 2, corr, "зворотний зв'язок: фактичний кут повертається у плату; вона крутить мотор, доки факт не зійдеться з ціллю",
                      size=11, color=INK, pad=9, min_w=430, fill="#f0fff4", stroke=FIELD)
    frags.append(b)

    render(os.path.join(OUT, 'inside.svg'), W, H, *frags)


def fig_wiring():
    """Розводка трьох дротів пін-у-пін: серво ↔ МК/приймач. Кольори жил,
    хто дає струм, куди йде сигнал, і форма керувального імпульсу 1520 мкс."""
    W, H = 860, 500
    frags = []
    frags.append(text(W / 2, 30, "Три дроти: як під'єднати HD-1370A", size=17, bold=True))

    # --- корпус серва ---
    sv_x, sv_y, sv_w, sv_h = 60, 90, 150, 150
    frags.append(rect(sv_x, sv_y, sv_w, sv_h, fill="#f4f6f8", stroke=LINE, sw=1.8))
    frags.append(text(sv_x + sv_w / 2, sv_y + 26, "HD-1370A", size=14, bold=True))
    frags.append(text(sv_x + sv_w / 2, sv_y + 46, "серво", size=12, color=MUTED))
    frags.append(circle(sv_x + sv_w / 2, sv_y + 98, 20, fill="#e8edf3", stroke=LINE, sw=1.4))
    frags.append(circle(sv_x + sv_w / 2, sv_y + 98, 7, fill=BG, stroke=LINE, sw=1.2))
    frags.append(text(sv_x + sv_w / 2, sv_y + 134, "вал", size=10, color=MUTED))

    # --- контролер справа ---
    mc_x, mc_y, mc_w, mc_h = 630, 90, 170, 150
    frags.append(rect(mc_x, mc_y, mc_w, mc_h, fill="#eef2ff", stroke=NEG, sw=1.8))
    frags.append(text(mc_x + mc_w / 2, mc_y + 26, "МК / приймач", size=13, bold=True, color=NEG))
    frags.append(text(mc_x + mc_w / 2, mc_y + 48, "Arduino, RC-RX,", size=10, color=INK))
    frags.append(text(mc_x + mc_w / 2, mc_y + 64, "плата керування", size=10, color=INK))

    # три дроти між ними
    x_left = sv_x + sv_w
    x_right = mc_x
    xm = (x_left + x_right) / 2
    rows = [
        (118, "#8a5a2b", "коричн. — GND", "земля, мінус живлення", "GND", NEG),
        (160, "#c0392b", "червон. — живлення", "4.8 – 6.0 В", "5 В", POS),
        (202, "#e67e22", "жовтий — сигнал", "керувальний імпульс", "PWM", FIELD),
    ]
    for (yy, col, role, note, pin, tcol) in rows:
        frags.append(line(x_left, yy, x_right, yy, color=col, sw=4))
        frags.append(text(xm, yy - 9, role, size=11.5, bold=True, color=tcol))
        frags.append(text(xm, yy + 16, note, size=10, color=MUTED))
        frags.append(text(x_right + 7, yy + 4, pin, size=10, color=tcol, anchor="start"))

    # застереження про живлення окремо
    b, _, _ = textbox(W / 2, 285,
                      "живлення бери з окремого 5 В (BEC/UBEC), не з піна 5V плати: пусковий струм серва просаджує напругу й перезавантажує МК",
                      size=11, color=INK, pad=10, min_w=W - 130, fill="#fff7ed", stroke="#d9822b")
    frags.append(b)

    # --- форма імпульсу знизу ---
    base = 435
    frags.append(text(W / 2, 335, "Керувальний імпульс: ширина задає кут, кадр — кожні 20 мс (50 Гц)", size=13, bold=True))
    frags.append(line(80, base, 800, base, color=MUTED, sw=1.2))

    def pulse(x0, width_px, label, sub, col):
        top = base - 46
        frags.append(line(x0, base, x0, top, color=col, sw=2.2))
        frags.append(line(x0, top, x0 + width_px, top, color=col, sw=2.2))
        frags.append(line(x0 + width_px, top, x0 + width_px, base, color=col, sw=2.2))
        frags.append(text(x0 + width_px / 2, top - 10, label, size=11.5, bold=True, color=col))
        frags.append(text(x0 + width_px / 2, base + 18, sub, size=10.5, color=MUTED))

    pulse(130, 28, "1.0 мс", "−45° (край)", NEG)
    pulse(340, 42, "1.52 мс", "нейтраль", INK)
    pulse(560, 56, "2.0 мс", "+45° (край)", POS)

    # позначка періоду (нижче підписів країв, у порожньому коридорі)
    frags.append(line(130, base + 42, 340, base + 42, color=FIELD, sw=1.4, dash="4 3"))
    frags.append(text(235, base + 57, "20 мс між імпульсами (50 Гц)", size=10.5, color=FIELD))

    render(os.path.join(OUT, 'wiring.svg'), W, H, *frags)


def fig_map():
    """Карта «кут → мікросекунди» для КОДУ керування: справжня нейтраль 1520,
    робочий діапазон, м'які програмні межі, підтягнуті всередину від
    механічних стопорів, і червона зона за ними, де застрягле серво гріється.
    Це головна ідея коду — жити всередині безпечного вікна, не впираючись."""
    W, H = 880, 430
    frags = []
    frags.append(text(W / 2, 30, "Карта керування: кут → ширина імпульсу (мкс)", size=17, bold=True))

    # вісь мікросекунд
    ax_y = 150
    x0, x1 = 90, 790          # 900 … 2100 мкс
    us_lo, us_hi = 900, 2100

    def ux(us):
        return x0 + (us - us_lo) / (us_hi - us_lo) * (x1 - x0)

    frags.append(line(x0, ax_y, x1, ax_y, color=MUTED, sw=1.4))
    for us in (1000, 1200, 1400, 1520, 1600, 1800, 2000):
        xx = ux(us)
        frags.append(line(xx, ax_y - 5, xx, ax_y + 5, color=MUTED, sw=1.2))
        lab = "1520" if us == 1520 else str(us)
        col = FIELD if us == 1520 else MUTED
        frags.append(text(xx, ax_y + 22, lab, size=10, color=col, bold=(us == 1520)))
    frags.append(text(x1 + 4, ax_y + 4, "мкс", size=10, color=MUTED, anchor="start"))

    # червоні зони за механічними стопорами (край ходу ≈ 1000 і 2000)
    stop_lo, stop_hi = 1000, 2000
    frags.append(rect(x0, ax_y - 16, ux(stop_lo) - x0, 32, fill="#fdecea", stroke=POS, sw=1.2))
    frags.append(rect(ux(stop_hi), ax_y - 16, x1 - ux(stop_hi), 32, fill="#fdecea", stroke=POS, sw=1.2))

    # безпечне робоче вікно (м'які межі, підтягнуті всередину)
    soft_lo, soft_hi = 1100, 1940
    frags.append(rect(ux(soft_lo), ax_y - 12, ux(soft_hi) - ux(soft_lo), 24, fill="#eafaf1", stroke=FIELD, sw=1.6))

    # маркер нейтралі
    frags.append(line(ux(1520), ax_y - 34, ux(1520), ax_y + 12, color=FIELD, sw=2))
    frags.append(text(ux(1520), ax_y - 40, "нейтраль", size=11, bold=True, color=FIELD))

    # підписи механічних стопорів (над віссю, з запасом)
    frags.append(text(ux(stop_lo), ax_y - 26, "стопор", size=10, color=POS))
    frags.append(text(ux(stop_hi), ax_y - 26, "стопор", size=10, color=POS))

    # пояснювальні рамки під віссю (кожна у своєму коридорі, не перетинаються)
    b1, w1, _ = textbox(ux((soft_lo + soft_hi) / 2), ax_y + 66,
                        "робоче вікно коду: сюди затискаємо кут (constrain)",
                        size=11, color=INK, pad=9, fill="#eafaf1", stroke=FIELD)
    frags.append(b1)

    b2, _, _ = textbox(W / 2, ax_y + 128,
                       ["червоні краї — за механічним стопором: серво туди не дійде,",
                        "мотор стане під струмом і за хвилини згорить. НЕ давати таких кутів."],
                       size=11, color=INK, pad=10, fill="#fdecea", stroke=POS)
    frags.append(b2)

    # формула перерахунку збоку внизу
    b3, _, _ = textbox(W / 2, ax_y + 200,
                       "мкс = 1520 + кут · 11.1     (11.1 мкс на 1° — з ходу 90° на 1000 мкс)",
                       size=11.5, color=INK, pad=10, fill=FILL, stroke=LINE, bold=False)
    frags.append(b3)

    render(os.path.join(OUT, 'map.svg'), W, H, *frags)


def fig_smooth():
    """Чому рух роблять покроково: замість стрибка з кута A в кут B серво
    ведуть маленькими приростами раз на кадр (20 мс). Показуємо два профілі —
    миттєвий стрибок (наказ) і плавну сходинку (як веде код), на спільній осі часу."""
    W, H = 860, 400
    frags = []
    frags.append(text(W / 2, 30, "Плавний рух: маленький крок раз на кадр (20 мс)", size=17, bold=True))

    # осі
    ox, oy = 90, 300           # початок координат
    x_end, y_top = 780, 80
    frags.append(line(ox, oy, x_end, oy, color=MUTED, sw=1.4))   # час →
    frags.append(line(ox, oy, ox, y_top, color=MUTED, sw=1.4))   # кут ↑
    frags.append(text(x_end + 2, oy + 4, "час", size=10, color=MUTED, anchor="start"))
    frags.append(text(ox - 8, y_top - 6, "кут", size=10, color=MUTED, anchor="end"))

    # рівні A і B
    yA, yB = oy - 20, y_top + 40
    frags.append(line(ox, yA, x_end, yA, color=MUTED, sw=1, dash="3 4"))
    frags.append(line(ox, yB, x_end, yB, color=MUTED, sw=1, dash="3 4"))
    frags.append(text(ox - 8, yA + 4, "A", size=12, bold=True, color=NEG, anchor="end"))
    frags.append(text(ox - 8, yB + 4, "B", size=12, bold=True, color=POS, anchor="end"))

    # миттєвий стрибок (наказ write(B) відразу) — синій
    jx = ox + 70
    frags.append(line(ox, yA, jx, yA, color=NEG, sw=2.4))
    frags.append(line(jx, yA, jx, yB, color=NEG, sw=2.4))
    frags.append(line(jx, yB, x_end - 10, yB, color=NEG, sw=2.4))
    frags.append(text(jx + 8, yB - 12, "стрибок: ривок, кидок струму", size=11, color=NEG, anchor="start"))

    # плавна сходинка — зелена, кроки по кадрах
    steps = 9
    x_start = ox + 40
    x_stop = x_end - 60
    prevx, prevy = x_start, yA
    for i in range(1, steps + 1):
        t = i / steps
        nx = x_start + (x_stop - x_start) * t
        ny = yA + (yB - yA) * t
        frags.append(line(prevx, prevy, nx, prevy, color=FIELD, sw=2.4))  # горизонт: кадр стоїть
        frags.append(line(nx, prevy, nx, ny, color=FIELD, sw=2.4))        # приріст на крок
        frags.append(circle(nx, ny, 2.6, fill=FIELD, stroke=FIELD, sw=1))
        prevx, prevy = nx, ny
    frags.append(line(prevx, prevy, x_end - 10, prevy, color=FIELD, sw=2.4))
    frags.append(text(x_stop - 4, yB + 26, "плавно: приріст щокадру", size=11, color=FIELD, anchor="middle"))

    # позначка одного кадру
    fx0, fx1 = x_start, x_start + (x_stop - x_start) / steps
    frags.append(line(fx0, oy + 12, fx1, oy + 12, color=INK, sw=1.4))
    frags.append(line(fx0, oy + 8, fx0, oy + 16, color=INK, sw=1.2))
    frags.append(line(fx1, oy + 8, fx1, oy + 16, color=INK, sw=1.2))
    frags.append(text((fx0 + fx1) / 2, oy + 30, "1 кадр = 20 мс", size=10, color=INK))

    render(os.path.join(OUT, 'smooth.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_inside()
    fig_wiring()
    fig_map()
    fig_smooth()
    print("figs done")
