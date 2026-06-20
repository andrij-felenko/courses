# -*- coding: utf-8 -*-
"""Фігури до вставки «Body-діод у ключі навантаження».
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


if __name__ == "__main__":
    fig_body_diode()
    fig_back_to_back()
    print("OK: 2 figures ->", IMG)
