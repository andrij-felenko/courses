# -*- coding: utf-8 -*-
# Фігури вставки-проєкту proj-int8-inference (тракт int8-виводу + реквантування).
# Окремий генератор, щоб не конфліктувати з figs.py при паралельному письмі;
# пише ті самі два SVG у ./img/. Стиль і svgkit — спільні (див. figs.py).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── datapath: int8 вивід одного шару — де живе кожен тип ──────────────────────
# Ідея: показати весь тракт даних одного нейрона в РОЗРЯДНОСТЯХ. int8-вага ×
# int8-активація (з відніманням zero-point) → доданок → сума в int32-акумуляторі
# (ось де чигає переповнення) → реквантування (×M0, ≫ n, округл.) → clamp у int8.
# Кольором — де 8 біт, а де 32; акумулятор навмисно ширший.
def fig_datapath():
    W, H = 900, 340
    p = []
    yrow = 132
    x0 = 34

    def cell(x, y, w, h, lab, col, fill, small=None):
        frs = [fitbox(x, y, w, h, lab, size=11, fill=fill, stroke=col, sw=1.4, color=INK, bold=True)]
        if small:
            frs.append(text(x + w / 2, y + h + 15, small, size=9, color=MUTED))
        return frs

    # int8 вага та активація зліва
    p += cell(x0, yrow - 62, 112, 38, "int8 вага\nq_w", NEG, "#eaf0fd", "1 байт")
    p += cell(x0, yrow + 24, 112, 38, "int8 актив.\nq_x", NEG, "#eaf0fd", "1 байт")

    # множник з відніманням zero-point активацій → доданок int32
    xm = x0 + 146
    p.append(arrow(x0 + 112, yrow - 43, xm, yrow - 18, color=INK, sw=1.5))
    p.append(arrow(x0 + 112, yrow + 43, xm, yrow + 4, color=INK, sw=1.5))
    p.append(text(xm + 56, yrow - 24, "(q_x − z_x) × q_w", size=11, color=POS, bold=True))
    p += cell(xm, yrow + 14, 112, 38, "доданок\nint32", FIELD, "#e9f8ef", "розширено до 32 біт")

    # int32-акумулятор
    xa = xm + 150
    p.append(arrow(xm + 112, yrow + 33, xa, yrow, color=INK, sw=1.8))
    p += cell(xa, yrow - 26, 156, 52, "int32-акумулятор\nΣ (q_x−z_x)·q_w", POS, "#fdecea",
              "сума по всіх входах — тут чатує переповнення")

    # реквантування
    xr = xa + 196
    p.append(arrow(xa + 156, yrow, xr, yrow, color=INK, sw=1.8))
    p.append(text((xa + 156 + xr) / 2, yrow - 11, "× M0, ≫ n", size=10, color=INK, bold=True))
    p += cell(xr, yrow - 30, 164, 60, "реквантування\n×M0, округл.\n≫ n, + z_вих", FIELD, "#e9f8ef",
              "цілий fixed-point, без float")

    # clamp у int8
    xc = xr + 190
    p.append(arrow(xr + 164, yrow, xc, yrow, color=INK, sw=1.8))
    p.append(text((xr + 164 + xc) / 2, yrow - 11, "clamp", size=10, color=INK, bold=True))
    p += cell(xc, yrow - 19, 92, 38, "int8\nвихід", NEG, "#eaf0fd", "1 байт")

    # легенда розрядності
    p.append(fitbox(x0, H - 62, W - 2 * x0, 46,
                    "Синє — 8 біт (вага, активація, вихід). Червоне й зелене — 32 біти. Уся вага множення тримається в int32-акумуляторі.\n"
                    "Єдина дробова величина — добуток масштабів — заздалегідь перетворена на цілий множник M0 і зсув n, тож float у гарячому циклі не з'являється.",
                    size=10.5, fill=FILL, stroke="#c9d2dc", sw=1.2, color=INK))

    render(os.path.join(OUT, "datapath.svg"), W, H, *p,
           title="Тракт int8-виводу одного шару: 8 біт → int32-акумулятор → назад у int8")


# ── requant: реквантування як цілий fixed-point (множник M = M0·2⁻ⁿ) ──────────
# Ідея: дробовий коефіцієнт M = s_w·s_x/s_вих (завжди 0<M<1) розкладають РАЗ, офлайн,
# на цілий множник M0 у [0.5,1) (як Q31) і правий зсув n. У рантаймі: подвоєне
# множення-з-округленням у старші 32 біти (VQRDMULH) + округлений правий зсув на n.
def fig_requant():
    W, H = 820, 348
    p = []
    x0 = 56
    boxw = 430
    stepy = 98
    y0 = 52

    steps = [
        ("Офлайн, раз при збірці",
         "M = s_w · s_x / s_вих   (0 < M < 1)\nрозклад: M = M0 · 2⁻ⁿ,  M0 ∈ [0.5, 1)",
         "M0 зберігають як ціле Q31 (int32), n — маленьке ціле. Жодного float у рантаймі.",
         FIELD, "#e9f8ef"),
        ("Крок 1 — подвоєне множення у старші біти",
         "t = VQRDMULH(acc, M0)  =  округл( acc · M0 · 2 / 2³² )",
         "int64-добуток, +2³⁰ на округлення, старші 32 біти; сатурація лише на acc = M0 = INT32_MIN.",
         POS, "#fdecea"),
        ("Крок 2 — округлений правий зсув на n",
         "y = round( t / 2ⁿ ) + z_вих,   далі clamp у [−128, 127]",
         "≫ додає +1, якщо відкинутий залишок > половини кроку — інакше зсув систематично занижує.",
         NEG, "#eaf0fd"),
    ]

    for i, (title, body, note, col, fill) in enumerate(steps):
        y = y0 + i * stepy
        p.append(text(x0, y - 7, title, size=12.5, color=col, bold=True, anchor="start"))
        p.append(fitbox(x0, y, boxw, 40, body, size=11.5, fill=fill, stroke=col, sw=1.4, color=INK, bold=True))
        p.append(text(x0, y + 58, note, size=9.5, color=MUTED, anchor="start"))
        if i < len(steps) - 1:
            p.append(arrow(x0 + boxw / 2, y + 40, x0 + boxw / 2, y + stepy - 7, color=INK, sw=1.7))

    render(os.path.join(OUT, "requant.svg"), W, H, *p,
           title="Реквантування як цілий fixed-point: M0·2⁻ⁿ, подвоєне множення, округлений зсув")


if __name__ == "__main__":
    fig_datapath()
    fig_requant()
    print("OK: proj figures written to", OUT)
