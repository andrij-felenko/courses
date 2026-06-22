# -*- coding: utf-8 -*-
"""Фігури теми «Load switch» та вставки «Body-діод у ключі навантаження».
  load-switch.md   →  load-switch.svg, gate-limit.svg
  comp-body-diode.md →  body-diode.svg, back-to-back.svg
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def pmos(cx, cy, on=False, label="P"):
    """Спрощений P-MOSFET: квадрат каналу + body-діод усередині.
    Витік (S) ліворуч на +Vin, стік (D) праворуч на навантаження.
    Body-діод: катод на витоку, анод на стоці (дивиться D→S)."""
    col = FIELD if on else MUTED
    fl = "#eef6ef" if on else "#f1f2f4"
    out = rect(cx - 26, cy - 30, 52, 60, fill=fl, stroke=col, sw=2, rx=6)
    out += text(cx, cy - 14, label, size=14, bold=True, color=col)
    # символ body-діода всередині: трикутник вістрям ліворуч (до витоку = катод)
    ax, ay = cx + 12, cy + 12     # анод (бік стоку)
    kx = cx - 12                  # катод (бік витоку)
    out += '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fdecea" stroke="%s" stroke-width="1.6"/>' % (
        ax, ay - 8, ax, ay + 8, kx + 2, ay, POS)
    out += line(kx + 2, ay - 9, kx + 2, ay + 9, color=POS, sw=2.2)   # риска-катод
    return out


# ── 1. Куди дивиться body-діод і коли він тече ───────────────────────────────
def fig_body_diode():
    W, H = 760, 380
    f = [text(W / 2, 26, "Body-діод P-MOSFET: дивиться зі стоку на витік — і тече, коли вихід підскочив вище +Vin",
              size=14.5, bold=True)]

    def panel(x0, title, vout_high, ok):
        col = POS if vout_high else FIELD
        f.append(rect(x0, 50, 350, 300, fill=BG, stroke=col, sw=2, rx=12))
        f.append(text(x0 + 175, 74, title, size=13, bold=True, color=INK))
        # шина +Vin зліва, навантаження справа
        sx, dx = x0 + 70, x0 + 280
        cy = 200
        f.append(plus(x0 + 36, cy, 11))
        f.append(text(x0 + 36, cy + 30, "+Vin", size=11, color=INK))
        f.append(line(x0 + 36, cy, sx - 26, cy, color=LINE, sw=2))
        f.append(pmos(sx, cy, on=False))     # ключ ВИМКНЕНО в обох панелях
        f.append(text(sx, cy + 48, "ключ ВИМКНЕНО", size=10.5, color=MUTED))
        f.append(line(sx + 26, cy, dx - 18, cy, color=LINE, sw=2))
        # навантаження як блок
        f.append(rect(dx - 18, cy - 26, 60, 52, fill="#e9edf2", stroke=LINE, sw=1.6, rx=4))
        f.append(text(dx + 12, cy + 4, "вузол", size=11, color=INK))
        if vout_high:
            # сторонній «плюс» на виході (інше джерело / зворотне живлення)
            f.append(plus(dx + 12, cy - 56, 10))
            f.append(text(dx + 12, cy - 74, "Vout > Vin", size=10.5, bold=True, color=POS))
            f.append(line(dx + 12, cy - 46, dx + 12, cy - 26, color=LINE, sw=1.8))
            # стрілка зворотного струму крізь діод: стік → витік → +Vin
            f.append(arrow(sx + 26, cy - 14, sx - 26, cy - 14, color=POS, sw=2.6))
            f.append(text(x0 + 175, cy + 92, "діод відкритий: струм тече назад", size=11.5, bold=True, color=POS))
            f.append(text(x0 + 175, cy + 110, "у джерело — повного відключення НЕМА", size=11.5, bold=True, color=POS))
        else:
            f.append(text(x0 + 175, cy + 92, "Vout < Vin: діод зворотно зміщений —", size=11.5, color=INK))
            f.append(text(x0 + 175, cy + 110, "мовчить, вузол справді відрізаний", size=11.5, color=INK))

    panel(20, "Норма: вихід нижчий за вхід", False, True)
    panel(400, "Біда: на виході чуже живлення", True, False)
    render(os.path.join(IMG, "body-diode.svg"), W, H, *f)


# ── 2. Два MOSFET спина-до-спини: діоди гасять один одного ───────────────────
def fig_back_to_back():
    W, H = 760, 360
    f = [text(W / 2, 26, "Спина-до-спини: два діоди дивляться назустріч — назад струм не пройде в жоден бік",
              size=14.5, bold=True)]

    cy = 170
    sx = 150            # витік першого (на +Vin)
    mx = 380            # спільна точка стоків
    ex = 610            # витік другого (на навантаження)

    # +Vin
    f.append(plus(70, cy, 12))
    f.append(text(70, cy + 32, "+Vin", size=12, color=INK))
    f.append(line(70, cy, sx - 26, cy, color=LINE, sw=2.2))

    # Q1: витік ліворуч (S→+Vin), стік праворуч (до спільної точки) — діод D→S дивиться вліво
    f.append(pmos(sx, cy, on=True, label="Q1"))
    f.append(line(sx + 26, cy, mx, cy, color=LINE, sw=2.2))

    # Q2 ДЗЕРКАЛЬНО: витік праворуч (S→навантаження), стік ліворуч (спільна точка)
    # малюємо власноруч, щоб діод дивився вправо (D→S = вправо)
    cxq = ex
    f.append(rect(cxq - 26, cy - 30, 52, 60, fill="#eef6ef", stroke=FIELD, sw=2, rx=6))
    f.append(text(cxq, cy - 14, "Q2", size=14, bold=True, color=FIELD))
    ax2, ay2 = cxq - 12, cy + 12      # анод (бік стоку, ліворуч)
    kx2 = cxq + 12                    # катод (бік витоку, праворуч)
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fdecea" stroke="%s" stroke-width="1.6"/>' % (
        ax2, ay2 - 8, ax2, ay2 + 8, kx2 - 2, ay2, POS))
    f.append(line(kx2 - 2, ay2 - 9, kx2 - 2, ay2 + 9, color=POS, sw=2.2))
    f.append(line(mx, cy, cxq - 26, cy, color=LINE, sw=2.2))

    # спільна точка стоків
    f.append(circle(mx, cy, 3.5, fill=LINE, stroke=LINE))
    f.append(text(mx, cy - 44, "спільні стоки", size=10.5, color=MUTED))

    # навантаження
    f.append(line(cxq + 26, cy, ex + 70, cy, color=LINE, sw=2.2))
    f.append(rect(ex + 70, cy - 26, 60, 52, fill="#e9edf2", stroke=LINE, sw=1.6, rx=4))
    f.append(text(ex + 100, cy + 4, "вузол", size=11, color=INK))

    # спільний затвор
    f.append(line(sx, cy + 30, sx, cy + 64, color=LINE, sw=1.6))
    f.append(line(cxq, cy + 30, cxq, cy + 64, color=LINE, sw=1.6))
    f.append(line(sx, cy + 64, cxq, cy + 64, color=LINE, sw=1.6))
    f.append(text((sx + cxq) / 2, cy + 80, "спільний затвор від драйвера (обидва відкриваються разом)",
                  size=10.5, color=MUTED))

    # підпис діодів: дивляться назустріч (стрілки)
    f.append(text(sx, cy + 48, "діод ◄", size=10.5, color=POS, bold=True))
    f.append(text(cxq, cy + 48, "► діод", size=10.5, color=POS, bold=True))

    # нижній висновок у рамці
    b, _, _ = textbox(W / 2, cy + 150,
                      "Хай куди не штовхай струм — один із двох діодів завжди закритий.\n"
                      "Ціна: подвійний Rds(on) (два канали послідовно).",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "back-to-back.svg"), W, H, *f)


def gnd(cx, y, label="GND"):
    """Символ землі: штрихи, що звужуються."""
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8)]
    out.append(line(cx - 13, y + 7, cx + 13, y + 7, color=INK, sw=2.4))
    out.append(line(cx - 8, y + 12, cx + 8, y + 12, color=INK, sw=2.0))
    out.append(line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8))
    if label:
        out.append(text(cx, y + 32, label, size=11, color=INK, bold=True))
    return "".join(out)


def nmos_small(cx, cy, label="Q2"):
    """Маленький N-ключ: квадрат каналу, стік угорі, витік унизу (на GND)."""
    out = [rect(cx - 22, cy - 26, 44, 52, fill="#eef6ef", stroke=FIELD, sw=2, rx=6)]
    out.append(text(cx, cy - 11, label, size=13, bold=True, color=FIELD))
    out.append(text(cx, cy + 14, "n", size=11, color=MUTED))
    return "".join(out)


# ── 3. Схема ключа: P-MOS + підтяжка + n-ключ Q2 від логіки ──────────────────
def fig_load_switch():
    W, H = 720, 430
    f = [text(W / 2, 28, "Ключ живлення на P-MOS: підтяжка тримає вимкненим, n-ключ перекидає затвор від логіки",
              size=14, bold=True)]

    # +Vin рейка (червона) і GND рейка
    railY, gndY = 70, 372
    f.append(line(90, railY, 560, railY, color=POS, sw=2.4))
    f.append(text(84, railY + 4, "+Vin", size=12, color=POS, bold=True, anchor="end"))
    f.append(line(90, gndY, 560, gndY, color=INK, sw=2))

    # P-MOS праворуч: витік (S) на +Vin, стік (D) на навантаження
    px, py = 440, 175
    f.append(pmos(px, py, on=True, label="P-MOS"))
    f.append(line(px, railY, px, py - 30, color=INK, sw=2))     # S → +Vin
    f.append(circle(px, railY, 3, fill=INK, stroke=INK))
    f.append(text(px + 32, py - 18, "S", size=11, color=INK, anchor="start"))
    f.append(text(px + 32, py + 22, "D", size=11, color=INK, anchor="start"))
    # стік → навантаження → GND
    f.append(line(px, py + 30, px, py + 70, color=INK, sw=2))
    f.append(rect(px - 30, py + 70, 60, 50, fill="#e9edf2", stroke=LINE, sw=1.6, rx=4))
    f.append(text(px, py + 99, "вузол", size=11, color=INK))
    f.append(line(px, py + 120, px, gndY, color=INK, sw=2))

    # затвор P-MOS ліворуч; підтяжка Rпу від затвора до +Vin
    gx = px - 80
    f.append(line(px - 26, py, gx, py, color=INK, sw=2))
    f.append(circle(gx, py, 3, fill=INK, stroke=INK))
    f.append(text(px - 26, py - 12, "G", size=11, color=INK, anchor="end"))
    # Rпу: вертикальний резистор від затвора вгору до +Vin
    rx, ryc = gx, (railY + py) / 2
    f.append(rect(rx - 8, ryc - 20, 16, 40, fill="#ffffff", stroke=INK, sw=1.6, rx=2))
    f.append(text(rx - 14, ryc + 4, "Rпу", size=11, color=INK, anchor="end"))
    f.append(line(rx, railY, rx, ryc - 20, color=INK, sw=2))
    f.append(circle(rx, railY, 3, fill=INK, stroke=INK))
    f.append(line(rx, ryc + 20, rx, py, color=INK, sw=2))

    # n-ключ Q2: стік до затвора P-MOS, витік на GND
    qx, qy = gx, py + 95
    f.append(nmos_small(qx, qy, "Q2"))
    f.append(line(qx, py, qx, qy - 26, color=INK, sw=2))
    f.append(line(qx, qy + 26, qx, gndY, color=INK, sw=2))
    f.append(circle(qx, gndY, 3, fill=INK, stroke=INK))

    # логічний вхід → затвор Q2 (зліва)
    f.append(rect(110, qy - 18, 84, 36, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=6))
    f.append(text(152, qy + 4, "лог. вхід", size=11, color=INK, bold=True))
    f.append(arrow(194, qy, qx - 22, qy, color=FIELD, sw=2))

    # нижній підсумок у рамці
    b, _, _ = textbox(W / 2, gndY + 38,
                      "лог. 1 → Q2 відкрив → затвор P-MOS донизу → Vgs ≈ −Vin → P-MOS відкрив → живлення є.\n"
                      "лог. 0 → Q2 закрив → Rпу підтягла затвор до витоку → Vgs = 0 → ВИМКНЕНО.",
                      size=11, fill="#f4f6f8", stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "load-switch.svg"), W, H, *f)


# ── 4. Берегти затвор при високому Vin: дві панелі ───────────────────────────
def fig_gate_limit():
    W, H = 700, 300
    f = [text(W / 2, 26, "Високе Vin: затвор P-MOS треба берегти", size=15, bold=True)]

    # ліва панель — небезпека
    f.append(rect(28, 50, 312, 226, fill=BG, stroke=POS, sw=1.8, rx=10))
    f.append(text(184, 74, "небезпека: Vin = 24 В", size=12.5, bold=True, color=INK))
    f.append(text(184, 102, "затвор тягнемо до 0 В", size=11, color=INK))
    f.append(text(184, 130, "Vgs = 0 − 24 = −24 В", size=13, bold=True, color=POS))
    f.append(text(184, 158, "межа затвора ≈ ±20 В", size=11, color=INK))
    f.append(text(184, 192, "✗ пробій оксиду затвора", size=12, bold=True, color=POS))
    f.append(text(184, 220, "(ізолятор у кілька десятків нм)", size=10, color=MUTED))

    # права панель — захист
    f.append(rect(360, 50, 312, 226, fill=BG, stroke=FIELD, sw=1.8, rx=10))
    f.append(text(516, 74, "захист: обмежити Vgs", size=12.5, bold=True, color=INK))
    f.append(text(516, 100, "стабілітрон затвір–витік", size=11, color=FIELD, bold=True))
    f.append(text(516, 118, "або дільник у колі затвора", size=11, color=FIELD, bold=True))
    f.append(text(516, 148, "тримають |Vgs| ≈ 10–12 В", size=12, color=INK))
    f.append(text(516, 184, "✓ затвор цілий,", size=12, bold=True, color=FIELD))
    f.append(text(516, 206, "P-MOS усе одно відкритий повністю", size=10.5, color=INK))
    f.append(text(516, 232, "(досить ~10 В перевищення)", size=10, color=MUTED))
    render(os.path.join(IMG, "gate-limit.svg"), W, H, *f)


if __name__ == "__main__":
    fig_body_diode()
    fig_back_to_back()
    fig_load_switch()
    fig_gate_limit()
    print("OK: 4 figures ->", IMG)
