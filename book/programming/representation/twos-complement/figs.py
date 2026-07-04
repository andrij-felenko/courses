# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── type-lens: ті самі біти 0xFB, два типи → два числа ────────────────────────
# Ідея: сам байт не знає знаку; тип-«лінза» вирішує, читати старший біт як вагу
# 128 чи як мінус. Ліворуч біти, від них дві стрілки до двох тлумачень.
def fig_type_lens():
    W, H = 720, 340
    p = []
    # центральний байт у пам'яті
    cx = W / 2
    p.append(text(cx, 44, "той самий байт у пам'яті", size=13, color=MUTED))
    bits = "11111011"
    bw, bh = 34, 40
    total = bw * 8
    x0 = cx - total / 2
    for i, ch in enumerate(bits):
        col = "#f2ecf8" if i == 0 else FILL
        p.append(rect(x0 + i * bw, 58, bw, bh, fill=col, stroke=LINE, sw=1.4, rx=4))
        p.append(text(x0 + i * bw + bw / 2, 84, ch, size=17, bold=True))
    p.append(text(cx, 122, "0xFB   =   1111 1011", size=13, bold=True, color=INK))
    p.append(text(x0 + bw / 2, 50, "старший", size=9, color="#8a5fb0"))

    # дві стрілки вниз до двох тлумачень
    lx, rx = cx - 180, cx + 180
    p.append(arrow(cx - 40, 130, lx, 168, color=NEG, sw=2))
    p.append(arrow(cx + 40, 130, rx, 168, color=POS, sw=2))

    # ЛІВО: uint8_t → +251
    p.append(fitbox(lx - 150, 172, 300, 118,
                    "як uint8_t  (беззнаковий)\n\nстарший біт важить +128\n128+64+32+16+8+2+1\n=  +251",
                    size=13, fill="#eef4ff", stroke=NEG, sw=1.8, color=INK))
    # ПРАВО: int8_t → −5
    p.append(fitbox(rx - 150, 172, 300, 118,
                    "як int8_t  (знаковий)\n\nстарший біт важить −128\n−128+64+32+16+8+2+1\n=  −5",
                    size=13, fill="#fdecea", stroke=POS, sw=1.8, color=INK))

    p.append(text(cx, 322, "біти однакові — число вирішує ТИП змінної, а не дані",
                  size=12, color=INK, italic=True))
    render(os.path.join(OUT, "type-lens.svg"), W, H, *p,
           title="Той самий байт 0xFB: uint8_t дає +251, int8_t дає −5")


# ── width-ladder: де сидить знаковий біт і межі для кожної ширини ─────────────
# Ідея: знаковий біт — це завжди найстарший; його вага росте з шириною, і від
# неї прямо випливають межі типу. Драбина 8→16→32→64.
def fig_width_ladder():
    W, H = 720, 340
    p = []
    p.append(text(W / 2, 40, "знаковий біт — завжди найстарший; його вага задає межі типу",
                  size=13, bold=True))
    rows = [
        ("int8_t",  "8",  "−128", "−128 … +127"),
        ("int16_t", "16", "−32 768", "−32 768 … +32 767"),
        ("int32_t", "32", "−2³¹", "≈ −2.1 млрд … +2.1 млрд"),
        ("int64_t", "64", "−2⁶³", "≈ ±9.2 · 10¹⁸"),
    ]
    y = 72
    rh = 58
    for name, w, wt, rng in rows:
        # брусок ширини (пропорційно, але з мінімумом видимості)
        bx = 150
        # знаковий біт-клітинка
        p.append(rect(bx, y, 30, 34, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
        p.append(text(bx + 15, y + 22, "S", size=14, bold=True, color=POS))
        # решта бітів — суцільний брус
        p.append(rect(bx + 34, y, 150, 34, fill=FILL, stroke=LINE, sw=1.3, rx=4))
        p.append(text(bx + 34 + 75, y + 22, w + " бітів", size=12, color=MUTED))
        # назва типу зліва
        p.append(text(bx - 12, y + 22, name, size=14, bold=True, color=INK, anchor="end"))
        # вага знаку та діапазон справа
        p.append(text(bx + 200, y + 15, "вага S = " + wt, size=11, color=POS, anchor="start"))
        p.append(text(bx + 200, y + 32, rng, size=12, color=INK, anchor="start", bold=True))
        y += rh
    p.append(text(W / 2, H - 14, "старший біт «1» → число від'ємне; додатних на одне менше (нуль з їхнього боку)",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "width-ladder.svg"), W, H, *p,
           title="Знаковий біт і межі: від int8_t до int64_t")


# ── ub-vs-defined: знакове переповнення — UB; беззнакове — визначене mod 2ⁿ ───
# Ідея: єдина найважливіша для програміста відмінність. Дві колонки: ліворуч
# знакове (демони UB), праворуч беззнакове (чесний модуль).
def fig_ub_vs_defined():
    W, H = 720, 330
    p = []
    midx = W / 2
    p.append(line(midx, 44, midx, H - 46, color=MUTED, sw=1, dash="5 5"))

    # ЛІВО — знакове: UB
    p.append(text(midx / 2, 62, "ЗНАКОВЕ переповнення", size=13, bold=True, color=POS))
    p.append(fitbox(30, 80, midx - 60, 52,
                    "INT_MAX + 1  →  невизначена\nповедінка (UB)", size=12,
                    fill="#fdecea", stroke=POS, sw=1.8, color=INK))
    p.append(mtext(midx / 2, 156,
                   "стандарт НЕ обіцяє нічого:\nкомпілятор має право\nвикинути перевірку, зламати логіку",
                   size=11, color=INK, lh=1.35))
    p.append(text(midx / 2, 232, "≈ 90% таких переповнень —", size=11, color=MUTED))
    p.append(text(midx / 2, 248, "це справжня помилка", size=11, color=MUTED))

    # ПРАВО — беззнакове: визначене
    p.append(text(midx + midx / 2, 62, "БЕЗЗНАКОВЕ переповнення", size=13, bold=True, color=NEG))
    p.append(fitbox(midx + 30, 80, midx - 60, 52,
                    "UINT_MAX + 1  =  0\nчесний залишок mod 2ⁿ", size=12,
                    fill="#eef4ff", stroke=NEG, sw=1.8, color=INK))
    p.append(mtext(midx + midx / 2, 156,
                   "поведінка ГАРАНТОВАНА:\nколо замикається в нуль,\nна це можна покладатися",
                   size=11, color=INK, lh=1.35))
    p.append(text(midx + midx / 2, 232, "лічильники, геш, різниця часу —", size=11, color=MUTED))
    p.append(text(midx + midx / 2, 248, "wrap тут навмисний", size=11, color=MUTED))

    p.append(text(W / 2, H - 18, "C++20/C23 закріпили доповняльний код — але знакове переповнення лишили UB",
                  size=11, color=INK, italic=True))
    render(os.path.join(OUT, "ub-vs-defined.svg"), W, H, *p,
           title="Головна відмінність у коді: знакове переповнення — UB, беззнакове — визначене")


# ── intmin-trap: асиметрія −128, чому −INT_MIN не існує ───────────────────────
# Ідея: діапазон несиметричний, тож дзеркального додатного для найменшого нема;
# −x, abs(x), x/−1 на INT_MIN перевалюють. Числова вісь із діркою праворуч.
def fig_intmin_trap():
    W, H = 720, 300
    p = []
    p.append(text(W / 2, 42, "діапазон знакового несиметричний: −128 є, +128 — нема",
                  size=13, bold=True))
    # вісь
    ox, oy = 90, 130
    axw = W - 180
    p.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    # позначки
    marks = [(0.0, "−128", POS), (0.5, "0", INK), (1.0, "+127", NEG)]
    for t, lab, col in marks:
        x = ox + t * axw
        p.append(line(x, oy - 6, x, oy + 6, color=INK, sw=1.6))
        p.append(text(x, oy + 24, lab, size=12, bold=True, color=col))
    # дірка там, де мав би бути +128
    hx = ox + axw + 34
    p.append(circle(hx, oy, 12, fill=BG, stroke=POS, sw=2))
    p.append(text(hx, oy + 5, "×", size=15, bold=True, color=POS))
    p.append(text(hx, oy + 28, "+128", size=11, color=POS))
    p.append(text(hx, oy - 20, "нема куди", size=10, color=MUTED))
    # стрілка-дзеркало 128 → 128 упирається в дірку
    p.append(arrow(ox + 6, oy - 22, hx - 12, oy - 10, color=MUTED, sw=1.6))
    p.append(text((ox + hx) / 2, oy - 30, "−(−128) хотіло б сюди", size=10, color=MUTED))

    # наслідки в коді
    p.append(fitbox(120, 196, 480, 78,
                    "на INT_MIN перевалюють (UB для знакового):\n"
                    "−x     abs(x)     x / −1     x % −1",
                    size=12, fill="#fdecea", stroke=POS, sw=1.7, color=INK))
    render(os.path.join(OUT, "intmin-trap.svg"), W, H, *p,
           title="Пастка найменшого: −INT_MIN не має дзеркала й перевалює")


if __name__ == "__main__":
    fig_type_lens()
    fig_width_ladder()
    fig_ub_vs_defined()
    fig_intmin_trap()
    print("OK: figures written to", OUT)
