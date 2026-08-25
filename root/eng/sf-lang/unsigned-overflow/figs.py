# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── modular-clock: беззнакова арифметика живе на колі з 2^N позицій ───────────
# Ідея: N-бітне беззнакове число — це позиція на циферблаті з 2^N поділок;
# додавання = крок за годинниковою стрілкою; «переповнення» = перехід через 0.
# Показуємо на прикладі 3-бітного (8 позицій), щоб було видно кожну поділку.
def fig_modular_clock():
    W, H = 720, 380
    p = []
    p.append(text(W / 2, 54, "3-бітне беззнакове: коло з 8 позицій (0…7)", size=14, bold=True))

    cx, cy, r = 250, 218, 118
    p.append(circle(cx, cy, r, fill=BG, stroke=LINE, sw=2))
    # 8 поділок; 0 угорі, далі за годинниковою
    for v in range(8):
        ang = -math.pi / 2 + 2 * math.pi * v / 8.0
        mx, my = cx + r * math.cos(ang), cy + r * math.sin(ang)
        lx, ly = cx + (r + 22) * math.cos(ang), cy + (r + 22) * math.sin(ang)
        col = POS if v == 0 else INK
        p.append(circle(mx, my, 4, fill=col, stroke=col, sw=1))
        p.append(text(lx, ly + 5, str(v), size=13, color=col, bold=(v == 0)))
    # стрілка-крок 6 → 7 → 0 (перехід через верх)
    a6 = -math.pi / 2 + 2 * math.pi * 6 / 8.0
    a0 = -math.pi / 2 + 2 * math.pi * 0.02 / 8.0
    p.append(arrow(cx + (r - 22) * math.cos(a6), cy + (r - 22) * math.sin(a6),
                   cx + (r - 22) * math.cos(a0 - 0.02), cy + (r - 22) * math.sin(a0 - 0.02),
                   color=POS, sw=2.6))
    p.append(text(cx, cy - 6, "+3", size=15, color=POS, bold=True))
    p.append(text(cx, cy + 16, "6 → 1", size=12, color=MUTED))

    # праворуч — сам закон
    rx = 452
    p.append(text(rx + 118, 96, "закон кола", size=13, bold=True, color=NEG))
    p.append(text(rx, 130, "6 + 3 = 9", size=15, color=INK, anchor="start"))
    p.append(text(rx, 158, "9 = 8 + 1", size=13, color=MUTED, anchor="start"))
    p.append(text(rx, 186, "9 mod 8 = 1", size=15, color=POS, anchor="start", bold=True))
    p.append(fitbox(rx - 6, 216, 250, 96,
                    "N бітів → модуль 2ᴺ\n\nсума завжди «довертається»\nна залишок від ділення на 2ᴺ\n— нічого не губиться, лише\nобертається по колу",
                    size=12, fill="#eef4ff", stroke=NEG, sw=1.6))

    render(os.path.join(OUT, "modular-clock.svg"), W, H, *p,
           title="Беззнакове число як позиція на колі: додавання йде за модулем 2ᴺ")


# ── defined-vs-ub: той самий wrap, але беззнаковий визначений, знаковий — UB ──
# Ідея: біти перевалюють однаково, та мова дає протилежні гарантії; ліворуч —
# тверда обіцянка модуля, праворуч — UB, на яке спиратися не можна.
def fig_defined_vs_ub():
    W, H = 720, 340
    p = []
    midx = W / 2
    p.append(line(midx, 46, midx, H - 24, color=MUTED, sw=1, dash="6 5"))

    # ЛІВОРУЧ — беззнаковий: визначено
    p.append(text(midx / 2, 62, "unsigned: ВИЗНАЧЕНО", size=14, bold=True, color=FIELD))
    p.append(fitbox(30, 82, midx - 60, 44,
                    "0xFFFFFFFF + 1  →  0", size=13, fill="#eafaf0", stroke=FIELD, sw=1.7, bold=True))
    p.append(text(midx / 2, 150, "стандарт гарантує:", size=11, color=MUTED))
    p.append(text(midx / 2, 172, "результат mod 2ᴺ", size=13, color=INK, bold=True))
    p.append(fitbox(30, 194, midx - 60, 96,
                    "на це МОЖНА покладатися:\nлічильники, геш, кільцевий\nіндекс, різниця часу.\nкод переносний і передбачний",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.4))

    # ПРАВОРУЧ — знаковий: UB
    p.append(text(midx + midx / 2, 62, "signed: UB", size=14, bold=True, color=POS))
    p.append(fitbox(midx + 30, 82, midx - 60, 44,
                    "INT_MAX + 1  →  ???", size=13, fill="#fdecea", stroke=POS, sw=1.7, bold=True))
    p.append(text(midx + midx / 2, 150, "стандарт не обіцяє:", size=11, color=MUTED))
    p.append(text(midx + midx / 2, 172, "нічого взагалі", size=13, color=INK, bold=True))
    p.append(fitbox(midx + 30, 194, midx - 60, 96,
                    "спиратися НЕ можна:\nоптимізатор має право\nвикинути вашу ж перевірку,\nвважаючи, що UB не буває",
                    size=11, fill="#fdecea", stroke=POS, sw=1.4))

    p.append(text(W / 2, H - 8, "біти перевалюють однаково — різниця живе в МОВІ, не в залізі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "defined-vs-ub.svg"), W, H, *p,
           title="Той самий перекот, дві гарантії: модуль ліворуч, порожнеча праворуч")


# ── promotion-trap: просування руйнує гарантію модуля 2^16 ────────────────────
# Ідея: uint16_t * uint16_t НЕ рахується за модулем 2^16 — операнди спершу
# піднімають до int (32 біти), тож дія йде в іншому модулі; результат «700*700»
# не перевалює на 16 бітах, а може навіть спричинити UB, якщо переросте int.
def fig_promotion_trap():
    W, H = 720, 360
    p = []
    p.append(text(W / 2, 54, "uint16_t a=50000, b=50000;   a * b = ?", size=15, bold=True))

    # очікування
    p.append(fitbox(40, 84, 300, 78,
                    "НАЇВНЕ сподівання\n\nдія «на 16 бітах»,\nрезультат mod 2¹⁶\n(2500000000 mod 65536)",
                    size=12, fill="#eef4ff", stroke=NEG, sw=1.6))
    # реальність
    p.append(fitbox(380, 84, 300, 78,
                    "ЩО РОБИТЬ C\n\nобидва → int (32 біти),\nдія в int; 2 500 000 000\n> INT_MAX → знакове UB!",
                    size=12, fill="#fdecea", stroke=POS, sw=1.6))

    p.append(arrow(W / 2, 168, W / 2, 196, color=INK, sw=2))
    p.append(fitbox(120, 200, 480, 52,
                    "гарантія модуля 2ᴺ діє в ШИРИНІ обчислення, а не оголошення:\nдо int — модуль зникає, і замість беззнакового wrap можна дістати UB",
                    size=12, fill="#f6f4ec", stroke=INK, sw=1.7))

    p.append(text(W / 2, 288, "рятунок: рахувати у явно широкому беззнаковому типі", size=12, color=INK, italic=True))
    p.append(text(W / 2, 316, "(uint32_t)a * b  або  (uint64_t)a * b  — тоді модуль справді 2³² чи 2⁶⁴",
                  size=12, color=FIELD, bold=True))
    render(os.path.join(OUT, "promotion-trap.svg"), W, H, *p,
           title="Просування ламає модуль: uint16·uint16 рахується в int, не в 16 бітах")


# ── ringbuf-mask: маска & (SIZE-1) обрізає індекс до кола розміром з буфер ─────
# Ідея: індекс, що росте, обрізається маскою до молодших k бітів — це рівно
# позиція на колі з 2^k поділок; & (SIZE-1) == % SIZE лише для степенів двійки.
def fig_ringbuf_mask():
    W, H = 720, 400
    p = []
    p.append(text(W / 2, 54, "Кільцевий буфер на 8: індекс  &  7  (двійково 0111)", size=15, bold=True))

    # коло-буфер з 8 комірок
    cx, cy, r = 210, 232, 108
    p.append(circle(cx, cy, r, fill=BG, stroke=LINE, sw=2))
    for v in range(8):
        ang = -math.pi / 2 + 2 * math.pi * v / 8.0
        mx, my = cx + r * math.cos(ang), cy + r * math.sin(ang)
        lx, ly = cx + (r + 22) * math.cos(ang), cy + (r + 22) * math.sin(ang)
        col = POS if v == 0 else INK
        p.append(circle(mx, my, 4, fill=col, stroke=col, sw=1))
        p.append(text(lx, ly + 5, str(v), size=13, color=col, bold=(v == 0)))
    # крок 6 → 7 → 0
    a6 = -math.pi / 2 + 2 * math.pi * 6 / 8.0
    a0 = -math.pi / 2 + 2 * math.pi * 0.02 / 8.0
    p.append(arrow(cx + (r - 20) * math.cos(a6), cy + (r - 20) * math.sin(a6),
                   cx + (r - 20) * math.cos(a0 - 0.02), cy + (r - 20) * math.sin(a0 - 0.02),
                   color=FIELD, sw=2.6))
    p.append(text(cx, cy - 4, "+1", size=15, color=FIELD, bold=True))
    p.append(text(cx, cy + 18, "7 → 0", size=12, color=MUTED))

    # праворуч — чому маска = остача
    rx = 396
    p.append(text(rx + 150, 96, "чому це остача", size=13, bold=True, color=NEG))
    p.append(text(rx, 130, "9 = 1001 (двійково)", size=13, color=INK, anchor="start"))
    p.append(text(rx, 156, "маска 7 = 0111", size=13, color=MUTED, anchor="start"))
    p.append(text(rx, 182, "9 & 7 = 0001 = 1", size=14, color=FIELD, anchor="start", bold=True))
    p.append(text(rx, 208, "9 mod 8 = 1  — те саме", size=13, color=INK, anchor="start"))
    p.append(fitbox(rx - 6, 232, 296, 118,
                    "& (SIZE−1)  ==  % SIZE\nЛИШЕ коли SIZE = 2ᵏ:\nтоді SIZE−1 — суцільна\nмаска молодших одиниць.\nкоштує 1 такт «І»\nзамість циклу ділення",
                    size=12, fill="#eafaf0", stroke=FIELD, sw=1.6))

    render(os.path.join(OUT, "ringbuf-mask.svg"), W, H, *p,
           title="Індекс кільцевого буфера маскою: & (SIZE−1) дешевше за % SIZE")


# ── timer-diff-wrap: різниця беззнакових таймерів переживає перекіт ────────────
# Ідея: start близько до стелі, now уже за нулем; now - start (mod 2^N) дає
# правильний проміжок, бо коло замикає розрив — поки інтервал < період.
def fig_timer_diff_wrap():
    W, H = 720, 380
    p = []
    p.append(text(W / 2, 54, "now − start  переживає переповнення лічильника", size=15, bold=True))

    # коло часу
    cx, cy, r = 200, 224, 104
    p.append(circle(cx, cy, r, fill=BG, stroke=LINE, sw=2))
    p.append(text(cx, cy - r - 12, "0", size=13, color=POS, bold=True))
    p.append(circle(cx, cy - r, 4, fill=POS, stroke=POS, sw=1))
    # start трохи ЛІВОРУЧ від верху (…F0), now трохи ПРАВОРУЧ (0x05)
    a_start = -math.pi / 2 - 0.42
    a_now = -math.pi / 2 + 0.22
    sx, sy = cx + r * math.cos(a_start), cy + r * math.sin(a_start)
    nx, ny = cx + r * math.cos(a_now), cy + r * math.sin(a_now)
    p.append(circle(sx, sy, 4, fill=NEG, stroke=NEG, sw=1))
    p.append(circle(nx, ny, 4, fill=INK, stroke=INK, sw=1))
    p.append(text(cx - r - 14, cy - r + 30, "start", size=12, color=NEG, anchor="end", bold=True))
    p.append(text(cx - r - 14, cy - r + 46, "…FFF0", size=11, color=MUTED, anchor="end"))
    p.append(text(cx + r + 14, cy - r + 30, "now", size=12, color=INK, anchor="start", bold=True))
    p.append(text(cx + r + 14, cy - r + 46, "0x05", size=11, color=MUTED, anchor="start"))
    # дуга-проміжок start → через 0 → now
    p.append(arrow(sx, sy, cx - 6, cy - r + 2, color=FIELD, sw=2.4))
    p.append(arrow(cx + 6, cy - r + 2, nx, ny, color=FIELD, sw=2.4))
    p.append(text(cx, cy + 6, "21", size=17, color=FIELD, bold=True))
    p.append(text(cx, cy + 26, "кроків", size=11, color=MUTED))

    # праворуч — арифметика
    rx = 402
    p.append(text(rx + 150, 92, "закон різниці", size=13, bold=True, color=NEG))
    p.append(text(rx, 124, "0x05 − 0xFFF0  (mod 2³²)", size=12, color=INK, anchor="start"))
    p.append(text(rx, 150, "= 5 − 65520 + 65536", size=12, color=MUTED, anchor="start"))
    p.append(text(rx, 176, "= 21  — точний проміжок", size=13, color=FIELD, anchor="start", bold=True))
    p.append(text(rx, 202, "(16 до кінця кола + 5 після 0)", size=11, color=MUTED, anchor="start"))
    p.append(fitbox(rx - 6, 226, 300, 100,
                    "правда, ПОКИ проміжок\nкоротший за період (2ᴺ):\nколо не лічить повні оберти.\nабсолютне now ≥ deadline\nтут збрехало б",
                    size=12, fill="#eafaf0", stroke=FIELD, sw=1.6))

    render(os.path.join(OUT, "timer-diff-wrap.svg"), W, H, *p,
           title="Різниця беззнакових таймерів правдива навіть після перекоту лічильника")


# ── fnv-mix: множення за модулем 2^32 розганяє біти по всьому слову ────────────
# Ідея: XOR вкидає байт у молодші біти, множення на просте перевалює за 2^32,
# старші біти завертаються назад — і за кілька кроків байт впливає на все слово.
def fig_fnv_mix():
    W, H = 720, 350
    p = []
    p.append(text(W / 2, 54, "FNV-1a: два кроки на байт, обидва на перекоті", size=15, bold=True))

    # крок XOR
    p.append(fitbox(40, 84, 300, 70,
                    "hash ^= байт\n\nвкидаємо новий байт\nу молодші біти слова",
                    size=12, fill="#eef4ff", stroke=NEG, sw=1.6))
    p.append(arrow(190, 158, 190, 186, color=INK, sw=2))
    # крок множення
    p.append(fitbox(40, 190, 300, 78,
                    "hash *= FNV_PRIME  (mod 2³²)\n\nдобуток перевалює за 2³²,\nстарші біти завертаються\nу молодші — перемішування",
                    size=12, fill="#eafaf0", stroke=FIELD, sw=1.6))

    # праворуч — константи й суть
    rx = 380
    p.append(text(rx + 160, 96, "32-бітні константи", size=13, bold=True, color=NEG))
    p.append(text(rx, 128, "OFFSET = 0x811C9DC5", size=13, color=INK, anchor="start"))
    p.append(text(rx, 154, "PRIME  = 0x01000193", size=13, color=INK, anchor="start"))
    p.append(fitbox(rx - 6, 178, 306, 96,
                    "саме перекіт mod 2³²\nрозганяє інформацію\nпо всіх 32 бітах.\nтип — тільки uint32_t,\nсуфікс u обовʼязковий",
                    size=12, fill="#f6f4ec", stroke=INK, sw=1.6))

    p.append(text(W / 2, H - 14, "знаковий тип → множення на перекоті стає UB, геш ламається",
                  size=12, color=POS, italic=True))
    render(os.path.join(OUT, "fnv-mix.svg"), W, H, *p,
           title="Геш FNV-1a: множення з wrap за модулем 2³² перемішує біти")


if __name__ == "__main__":
    fig_modular_clock()
    fig_defined_vs_ub()
    fig_promotion_trap()
    fig_ringbuf_mask()
    fig_timer_diff_wrap()
    fig_fnv_mix()
    print("OK: figures written to", OUT)
