# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

STAGES = ["В", "Д", "Ви", "П", "З"]  # Вибірка, Декодування, Виконання, Пам'ять, Запис
LANE_A = "#fdecea"   # світло-червона доріжка
LANE_B = "#eaf0fd"   # світло-синя доріжка
STAGE_FILL = "#f4f6f8"


# ── Фігура 1: скалярний конвеєр проти суперскалярного (дві доріжки) ──────────
def fig_two_lanes():
    cell = 46
    x0, y0 = 70, 70
    W, H = 760, 430

    def one_track(x, y, n_cycles, offsets, title, sub):
        """offsets: список зсувів початку команд (у тактах)."""
        out = [text(x + n_cycles * cell / 2, y - 34, title, size=15, bold=True)]
        out.append(text(x + n_cycles * cell / 2, y - 16, sub, size=11, color=MUTED))
        # шкала тактів
        for c in range(n_cycles):
            out.append(text(x + c * cell + cell / 2, y - 2, str(c + 1), size=10, color=MUTED))
        return out, x, y

    frags = []

    # --- скалярний конвеєр: одна команда стартує щотакту ---
    tx, ty = x0, y0
    frags.append(text(tx + 5 * cell / 2, ty - 30, "Скалярний конвеєр", size=15, bold=True))
    frags.append(text(tx + 5 * cell / 2, ty - 13, "одна команда сходить з лінії за такт (IPC = 1)", size=11, color=MUTED))
    for c in range(7):
        frags.append(text(tx + c * cell + cell / 2, ty - 1, str(c + 1), size=10, color=MUTED))
    for instr in range(3):
        start = instr * 1  # зсув на 1 такт
        for s in range(5):
            cx = tx + (start + s) * cell
            frags.append(rect(cx + 2, ty + instr * (cell) + 2, cell - 4, cell - 6, fill=LANE_A, stroke=POS, sw=1.2, rx=4))
            frags.append(text(cx + cell / 2, ty + instr * cell + cell / 2 + 3, STAGES[s], size=12, bold=True))
        frags.append(text(tx - 12, ty + instr * cell + cell / 2 + 4, "i%d" % (instr + 1), size=11, color=INK, anchor="end"))

    # --- суперскалярний: ДВІ команди стартують щотакту ---
    sy = y0 + 210
    frags.append(text(x0 + 5 * cell / 2, sy - 30, "Суперскалярний конвеєр (2 доріжки)", size=15, bold=True))
    frags.append(text(x0 + 5 * cell / 2, sy - 13, "дві команди сходять з лінії за такт (IPC = 2)", size=11, color=MUTED))
    for c in range(7):
        frags.append(text(x0 + c * cell + cell / 2, sy - 1, str(c + 1), size=10, color=MUTED))
    # пари команд: (i1,i2) старт 0, (i3,i4) старт 1, (i5,i6) старт 2
    pairs = [(0, "i1", LANE_A, POS), (0, "i2", LANE_B, NEG),
             (1, "i3", LANE_A, POS), (1, "i4", LANE_B, NEG)]
    row = 0
    for start, lbl, fill, stroke in pairs:
        for s in range(5):
            cx = x0 + (start + s) * cell
            yy = sy + row * (cell * 0.72)
            frags.append(rect(cx + 2, yy + 2, cell - 4, cell * 0.72 - 6, fill=fill, stroke=stroke, sw=1.2, rx=4))
            frags.append(text(cx + cell / 2, yy + cell * 0.72 / 2 + 3, STAGES[s], size=11, bold=True))
        frags.append(text(x0 - 12, sy + row * (cell * 0.72) + cell * 0.72 / 2 + 4, lbl, size=11, anchor="end"))
        row += 1

    # легенда стадій
    leg = "В — вибірка · Д — декодування · Ви — виконання · П — пам'ять · З — запис"
    frags.append(text(W / 2, H - 12, leg, size=11, color=MUTED))

    render(os.path.join(IMG, "two-lanes.svg"), W, H, *frags)


# ── Фігура 2: диспетчер розкидає команди по кількох виконавчих блоках ────────
def fig_dispatch():
    W, H = 720, 400
    frags = []

    # черга декодованих команд
    qx, qy = 40, 70
    frags.append(text(qx + 70, qy - 14, "Вікно команд", size=13, bold=True))
    labels = ["ADD", "LDR", "MUL", "FADD"]
    cols = [POS, FIELD, NEG, "#8e44ad"]
    for i, (lb, cc) in enumerate(zip(labels, cols)):
        frags.append(rect(qx, qy + i * 42, 140, 34, fill="#f4f6f8", stroke=cc, sw=1.6, rx=5))
        frags.append(text(qx + 70, qy + i * 42 + 22, lb, size=13, bold=True, color=cc))

    # диспетчер
    dbody, dw, dh = textbox(320, 165, ["Диспетчер", "(перевіряє", "залежності)"], size=13, bold=True,
                            fill="#fff8e1", stroke="#b7791f", pad=12)
    frags.append(dbody)

    # виконавчі блоки праворуч
    units = [("АЛП 1", 55, POS), ("АЛП 2", 130, POS), ("Load/Store", 205, FIELD), ("FPU", 280, "#8e44ad")]
    ux = 560
    for name, uy, cc in units:
        b = fitbox(ux, uy, 130, 46, name, size=13, bold=True, fill="#f4f6f8", stroke=cc, sw=1.6)
        frags.append(b)

    # стрілки: черга -> диспетчер
    for i in range(4):
        frags.append(arrow(qx + 140, qy + i * 42 + 17, 320 - dw / 2, 165, color=MUTED, sw=1.4))
    # диспетчер -> блоки
    tgt_y = [55 + 23, 205 + 23, 130 + 23, 280 + 23]  # ADD->АЛП1, LDR->LS, MUL->АЛП2, FADD->FPU
    for ty in tgt_y:
        frags.append(arrow(320 + dw / 2, 165, ux, ty, color=INK, sw=1.6))

    frags.append(text(W / 2, H - 14,
                      "Незалежні команди з вікна одночасно йдуть на свої блоки — паралелізм рівня команд",
                      size=11, color=MUTED))
    render(os.path.join(IMG, "dispatch.svg"), W, H, *frags)


# ── Фігура 3: залежність рве паралелізм ─────────────────────────────────────
def fig_dependency():
    W, H = 700, 320
    frags = []
    frags.append(text(W / 2, 30, "Дві пари команд, той самий 2-канальний конвеєр", size=14, bold=True))

    def box(x, y, txt, cc):
        frags.append(rect(x, y, 150, 40, fill="#f4f6f8", stroke=cc, sw=1.6, rx=5))
        frags.append(text(x + 75, y + 25, txt, size=12, bold=True, color=cc))

    # ліворуч: незалежні -> паралельно
    frags.append(text(180, 70, "Незалежні → разом", size=13, bold=True, color=FIELD))
    box(30, 95, "a = b + c", FIELD)
    box(30, 150, "x = y + z", FIELD)
    frags.append(text(180, 220, "обидві в одному такті", size=11, color=MUTED))
    frags.append(text(180, 238, "IPC = 2", size=13, bold=True, color=FIELD))

    # роздільник
    frags.append(line(350, 60, 350, 260, color="#cccccc", sw=1.2, dash="4,4"))

    # праворуч: залежні -> послідовно
    frags.append(text(530, 70, "Залежні → по черзі", size=13, bold=True, color=POS))
    box(380, 95, "a = b + c", POS)
    box(380, 150, "d = a + e", POS)
    frags.append(arrow(455, 135, 455, 150, color=POS, sw=1.8))
    frags.append(text(600, 128, "чекає a", size=11, color=POS, anchor="start"))
    frags.append(text(530, 220, "друга чекає результат першої", size=11, color=MUTED))
    frags.append(text(530, 238, "IPC = 1", size=13, bold=True, color=POS))

    frags.append(text(W / 2, H - 12,
                      "Виграш суперскаляра впирається в те, скільки сусідніх команд справді незалежні",
                      size=11, color=MUTED))
    render(os.path.join(IMG, "dependency.svg"), W, H, *frags)


# ── Фігура для hist-вставки: тридцять років дороги до суперскаляра ───────────
def fig_hist_timeline():
    W, H = 860, 380
    frags = []
    frags.append(text(W / 2, 30, "Тридцять років до суперскаляра: залізо → механізм → ідея → назва → кремній",
                      size=14, bold=True))

    axis_y = 205
    x_lo, x_hi = 60, 800
    frags.append(line(x_lo, axis_y, x_hi, axis_y, color=INK, sw=2))
    # стрілка часу праворуч
    frags.append(arrow(x_hi - 2, axis_y, x_hi + 8, axis_y, color=INK, sw=2))

    # (рік, підпис, колір мітки, зверху?, чи це «задум/назва» — пунктирний вусик)
    events = [
        (1964, ["CDC 6600", "10 блоків", "(Крей)"], POS, True, False),
        (1967, ["Model 91", "алг. Томасуло"], NEG, False, False),
        (1967.9, ["ACS-1: задум", "видачі — закрито"], MUTED, True, True),
        (1987, ["назва", "«суперскаляр»", "(звіт RC 12434)"], "#8e44ad", False, True),
        (1989, ["i960CA", "1-й на кристалі"], FIELD, True, False),
        (1991, ["MC88110"], FIELD, False, False),
        (1993, ["Pentium", "1-й масовий,", "1-й x86"], POS, True, False),
    ]

    def year_to_x(yr):
        return x_lo + (yr - 1962) / (1994 - 1962) * (x_hi - x_lo - 20)

    for yr, lines, cc, top, dashed in events:
        x = year_to_x(yr)
        # точка на осі
        frags.append(circle(x, axis_y, 6, fill="#ffffff", stroke=cc, sw=2.5))
        # рік біля осі
        yr_lbl = str(int(yr)) if abs(yr - round(yr)) < 0.05 else str(int(yr))
        frags.append(text(x, axis_y + (22 if top else -14), yr_lbl, size=12, bold=True, color=INK))
        # вусик до підпису
        stub = 34
        ty = axis_y - stub if top else axis_y + stub
        frags.append(line(x, axis_y, x, ty, color=cc, sw=1.4,
                          dash="3,3" if dashed else None))
        # підпис-рамка
        label = "\n".join(lines)
        if top:
            body, w, h = textbox(x, ty - len(lines) * 8 - 6, label, size=11,
                                 fill="#f4f6f8", stroke=cc, sw=1.4, pad=7)
        else:
            body, w, h = textbox(x, ty + len(lines) * 8 + 6, label, size=11,
                                 fill="#f4f6f8", stroke=cc, sw=1.4, pad=7)
        frags.append(body)

    # легенда пунктиру
    frags.append(text(W / 2, H - 14,
                      "суцільний вусик — збудоване залізо · пунктир — задум / назва (ще без кремнію)",
                      size=11, color=MUTED))
    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_two_lanes()
    fig_dispatch()
    fig_dependency()
    fig_hist_timeline()
    print("ok")
