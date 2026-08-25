# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── wrap-vs-sat: два кінці однакового переливу ───────────────────────────────
# Ідея: 250 + 10 у беззнаковому байті. Wrap перевалює через нуль (4),
# насичення впирається у стелю (255). Показуємо обидві траєкторії на осі.
def fig_wrap_vs_sat():
    W, H = 720, 340
    p = []
    # спільна вісь 0…255
    ox, oy = 70, 150
    aw = W - 140
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    for val in (0, 64, 128, 192, 255):
        x = ox + aw * val / 255.0
        p.append(line(x, oy - 5, x, oy + 5, color=INK, sw=1.4))
        p.append(text(x, oy + 22, str(val), size=11, color=INK))
    p.append(text(ox + aw / 2, oy - 60, "250 + 10  у беззнаковому байті (стеля 255)", size=13, bold=True))

    # старт 250
    xs = ox + aw * 250 / 255.0
    p.append(circle(xs, oy, 5, fill=INK, stroke=INK, sw=1))
    p.append(text(xs, oy - 16, "250", size=11, color=INK))

    # WRAP: перевалює за 255 → 4 (дуга вниз, назад до початку)
    xw = ox + aw * 4 / 255.0
    p.append(text(ox + 4, oy + 70, "wrap: перевалює через край", size=12, bold=True, color=POS, anchor="start"))
    # дуга від 250 вправо за межу і назад у 4
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
             % (xs, oy + 6, (xs + ox + aw) / 2 + 30, oy + 66, xw, oy + 6, POS))
    p.append(circle(xw, oy, 5, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(xw, oy + 40, "= 4", size=12, bold=True, color=POS))

    # SAT: впирається у 255 (коротка дуга вгору до стелі)
    xc = ox + aw * 255 / 255.0
    p.append(text(ox + 4, oy - 96, "saturate: впирається у стелю", size=12, bold=True, color=FIELD, anchor="start"))
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2.6" marker-end="url(#arrow)"/>'
             % (xs, oy - 6, (xs + xc) / 2, oy - 56, xc - 1, oy - 8, FIELD))
    p.append(circle(xc, oy, 5, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(xc, oy - 40, "= 255", size=12, bold=True, color=FIELD, anchor="end"))

    p.append(text(W / 2, H - 20, "той самий перелив — одне число «стрибає» назад, друге лишається біля правди",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "wrap-vs-sat.svg"), W, H, *p,
           title="Дві відповіді на переповнення: перевалити або впертися")


# ── audio-clip: чому у звуці wrap чутно як тріск, а насичення — м'яко ─────────
# Ідея: гучна синусоїда, що вилазить за межу. Wrap «перекидає» пік у низ —
# розрив; насичення зрізає верхівку — плаский, але без стрибка.
def fig_audio_clip():
    W, H = 720, 330
    p = []
    ox, oy = 60, 165           # вісь часу
    aw, amp = W - 120, 78
    top = oy - amp             # межа +повна шкала
    bot = oy + amp             # межа −повна шкала
    n = 220

    def sine(t):               # надто гучна: розмах 1.7 повної шкали
        return 1.7 * math.sin(2 * math.pi * 1.5 * t)

    # межі
    p.append(line(ox, top, ox + aw, top, color=MUTED, sw=1.2, dash="5 4"))
    p.append(line(ox, bot, ox + aw, bot, color=MUTED, sw=1.2, dash="5 4"))
    p.append(text(ox - 6, top + 4, "+max", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 6, bot + 4, "−max", size=10, color=MUTED, anchor="end"))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1))

    # ідеальна (тонка сіра) — для орієнтиру, обрізана до кадру
    ideal = []
    for i in range(n + 1):
        t = i / float(n)
        v = max(-1.2, min(1.2, sine(t)))
        ideal.append("%.1f,%.1f" % (ox + t * aw, oy - v * amp))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1" stroke-dasharray="3 3"/>' % (" ".join(ideal), MUTED))

    # WRAP: пік перекидається у протилежний край (за модулем) — рвані стрибки
    wrap = []
    for i in range(n + 1):
        t = i / float(n)
        v = sine(t)
        # емуляція wrap у діапазоні [−1,1): перенести по колу шириною 2
        w = ((v + 1.0) % 2.0) - 1.0
        wrap.append("%.1f,%.1f" % (ox + t * aw, oy - w * amp))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(wrap), POS))
    p.append(text(ox + aw * 0.5, top - 12, "wrap: пік «перекидається» у протилежний край → тріск",
                  size=11, bold=True, color=POS))

    # SAT: зрізаний верх/низ — плаский, без розриву
    sat = []
    for i in range(n + 1):
        t = i / float(n)
        v = max(-1.0, min(1.0, sine(t)))
        sat.append("%.1f,%.1f" % (ox + t * aw, oy - v * amp))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(sat), FIELD))
    p.append(text(ox + aw * 0.5, bot + 24, "saturate: верхівка зрізана рівно → лише глухіше, без стрибка",
                  size=11, bold=True, color=FIELD))

    render(os.path.join(OUT, "audio-clip.svg"), W, H, *p,
           title="Гучний звук за межею: wrap рве хвилю, насичення лише зрізає пік")


# ── branchless: як зробити насичення без if, через маску знаку ───────────────
# Ідея: три способи від наочного (if) до безгіллястого (маска) і апаратного
# (одна інструкція). Стовпчик карток «як реалізувати».
def fig_branchless():
    W, H = 720, 320
    p = []
    cards = [
        ("Ширший тип + затиск", "int32 s = (int32)a + b;\nif (s>255) s=255; else if (s<0) s=0;",
         "наочно, переносно всюди", FIELD, "#eafaf0"),
        ("Порівняння з межею ДО", "if (a > 255 - b) r = 255;\nelse r = a + b;",
         "без ширшого типу; знак b — який бік", NEG, "#eef4ff"),
        ("Безгіллясто (маска знаку)", "s = a + b;\nr = s | -(s >> 8);   // клас DSP",
         "без розгалуження — рівний час", "#8a5fb0", "#f2ecf8"),
        ("Апаратна інструкція", "USAT / QADD (Cortex-M DSP)\n__QADD, __USAT — одна дія",
         "найшвидше, плюс прапорець Q", POS, "#fdecea"),
    ]
    cw, ch = 320, 116
    pos = [(40, 52), (370, 52), (40, 190), (370, 190)]
    for (x, y), (title, code, note, col, fill) in zip(pos, cards):
        p.append(rect(x, y, cw, ch, fill=fill, stroke=col, sw=1.8))
        p.append(text(x + 14, y + 26, title, size=13, bold=True, color=col, anchor="start"))
        p.append(mtext(x + 14, y + 50, code, size=11, color=INK, anchor="start", lh=1.35))
        p.append(text(x + 14, y + ch - 12, note, size=10, color=MUTED, anchor="start", italic=True))
    render(os.path.join(OUT, "branchless.svg"), W, H, *p,
           title="Чотири способи насичення: від наочного if до однієї інструкції")


# ── domains: де насичення доречне, а де ні ───────────────────────────────────
# Ідея: дві колонки. Ліворуч — сигнал/керування (насичення = правда), праворуч —
# лічба/адреси/криптографія (насичення = прихована брехня, треба wrap чи виявити).
def fig_domains():
    W, H = 720, 300
    p = []
    midx = W / 2
    p.append(line(midx, 44, midx, H - 20, color=MUTED, sw=1, dash="5 5"))

    p.append(text(midx / 2, 62, "Насичення — правильна межа", size=13, bold=True, color=FIELD))
    good = [
        "звук: гучніше за максимум\n= просто максимум, не тріск",
        "яскравість пікселя 0…255\nне «загортається» в чорне",
        "керування: сигнал на привід\nупертий у фізичну межу",
    ]
    y = 92
    for s in good:
        p.append(fitbox(28, y, midx - 56, 52, s, size=11, fill="#eafaf0", stroke=FIELD, sw=1.5))
        y += 62

    p.append(text(midx + midx / 2, 62, "Насичення тут — брехня", size=13, bold=True, color=POS))
    bad = [
        "лічба грошей/подій: 255+1\nмусить рости, не застрягти",
        "індекси, адреси, хеші:\nпотрібен wrap за модулем",
        "де важлива ТОЧНА сума —\nкраще виявити переповнення",
    ]
    y = 92
    for s in bad:
        p.append(fitbox(midx + 28, y, midx - 56, 52, s, size=11, fill="#fdecea", stroke=POS, sw=1.5))
        y += 62

    p.append(text(W / 2, H - 6, "питання одне: «застрягти на межі» — це правда про величину чи мовчазна втрата?",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "domains.svg"), W, H, *p,
           title="Коли впертися в межу — правда, а коли — прихована втрата")


# ── sat-timeline: як насичення переїхало з аналогу в масові набори інструкцій ─
# Ідея: одна горизонтальна вісь часу з віхами. Спершу насичення — фізичний факт
# (аналоговий підсилювач, телефонія), тоді фіча спеціалізованих DSP, тоді стрибок
# у масові чипи: MMX (1997) і DSP-розширення Cortex-M4 (2010). Показуємо перехід
# «ідея (фізика) → фіча DSP → команда масового ISA».
def fig_sat_timeline():
    W, H = 760, 380
    p = []
    ox, oy = 60, 150
    aw = W - 120
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2.2))
    # стрілка часу
    p.append('<path d="M %.1f %.1f L %.1f %.1f" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (ox + aw - 2, oy, ox + aw + 14, oy, INK))
    p.append(text(ox + aw + 18, oy + 4, "час", size=11, color=MUTED, anchor="start"))

    # віхи: (частка_осі, рік, заголовок, підпис, колір, заливка, зверху?)
    marks = [
        (0.05, "фізика", "Аналог упирається сам",
         "підсилювач за межею\nпросто зрізає пік", MUTED, "#eef0f2", True),
        (0.26, "1960–70-ті", "Телефонія: G.711",
         "μ-law зрізає перевантаження\nу ±8159 (кліп, не переліт)", NEG, "#eef4ff", False),
        (0.50, "1980-ті", "DSP-чипи (TMS320, 1983)",
         "фіксована кома + насичення\nпроти overflow-осциляцій", FIELD, "#eafaf0", True),
        (0.74, "1997", "Intel MMX",
         "PADDSB/PADDUSB —\nнасичення в масовий x86", POS, "#fdecea", False),
        (0.93, "2010", "ARM Cortex-M4",
         "QADD/SSAT/USAT +\nлипкий прапорець Q", "#8a5fb0", "#f2ecf8", True),
    ]
    for frac, yr, title, note, col, fill, up in marks:
        x = ox + aw * frac
        p.append(circle(x, oy, 6, fill=fill, stroke=col, sw=2.2))
        if up:
            p.append(line(x, oy - 8, x, oy - 34, color=col, sw=1.4))
            p.append(text(x, oy - 42, yr, size=11, bold=True, color=col))
            p.append(fitbox(x - 88, oy - 118, 176, 66, title + "\n" + note,
                            size=10, fill=fill, stroke=col, sw=1.5))
        else:
            p.append(line(x, oy + 8, x, oy + 34, color=col, sw=1.4))
            p.append(text(x, oy + 48, yr, size=11, bold=True, color=col))
            p.append(fitbox(x - 88, oy + 54, 176, 66, title + "\n" + note,
                            size=10, fill=fill, stroke=col, sw=1.5))

    p.append(text(W / 2, H - 14,
                  "спершу фізичний факт аналогу → фіча спеціалізованих DSP → команда масових чипів",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "sat-timeline.svg"), W, H, *p,
           title="Шлях насичення: від аналогу до масових наборів інструкцій")


# ── sign-mask: арифметичний зсув розмазує знаковий біт у суцільну маску ───────
# Ідея (для вставки proj): s >> 31 арифметично дає 0x00000000 (плюс) або
# 0xFFFFFFFF (мінус). Показуємо два 32-бітні слова: біти до і після зсуву.
def fig_sign_mask():
    W, H = 720, 320
    p = []
    p.append(text(W / 2, 52, "s >> 31  (арифметичний зсув на всю ширину)", size=13, bold=True))

    cw = 15

    def bits(x, y, pattern, sign_col, cell_col):
        for i, ch in enumerate(pattern):
            bx = x + i * cw
            fill = "#eafaf0" if ch == "1" else "#ffffff"
            p.append(rect(bx, y, cw, 22, fill=fill, stroke=cell_col, sw=1.2, rx=2))
            p.append(text(bx + cw / 2, y + 16, ch, size=11, color=cell_col))
        # рамка навколо знакового біта (крайній лівий)
        p.append(rect(x - 2, y - 2, cw + 4, 26, fill="none", stroke=sign_col, sw=2, rx=3))

    ox = 150
    tx = ox + 32 * cw + 16
    # ── випадок «плюс» ───────────────────────────────────────────────
    y1 = 92
    p.append(text(40, y1 + 16, "s ≥ 0", size=12, bold=True, color=FIELD, anchor="start"))
    bits(ox, y1, "0" + "1010110" + "0" * 24, FIELD, INK)          # знак 0
    p.append(text(tx, y1 + 16, "знак = 0", size=11, color=MUTED, anchor="start"))
    y1b = y1 + 40
    bits(ox, y1b, "0" * 32, FIELD, FIELD)
    p.append(text(tx, y1b + 16, "→ 0x00000000", size=11, color=FIELD, anchor="start", bold=True))
    p.append(arrow(ox + 8 * cw, y1 + 24, ox + 8 * cw, y1b - 2, color=MUTED, sw=1.6))

    # ── випадок «мінус» ──────────────────────────────────────────────
    y2 = 200
    p.append(text(40, y2 + 16, "s < 0", size=12, bold=True, color=POS, anchor="start"))
    bits(ox, y2, "1" + "0011010" + "1" * 24, POS, INK)            # знак 1
    p.append(text(tx, y2 + 16, "знак = 1", size=11, color=MUTED, anchor="start"))
    y2b = y2 + 40
    bits(ox, y2b, "1" * 32, POS, POS)
    p.append(text(tx, y2b + 16, "→ 0xFFFFFFFF", size=11, color=POS, anchor="start", bold=True))
    p.append(arrow(ox + 8 * cw, y2 + 24, ox + 8 * cw, y2b - 2, color=MUTED, sw=1.6))

    p.append(text(W / 2, H - 12, "один знаковий біт (у рамці) розмазується в усі 32 — виходить маска знаку",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "sign-mask.svg"), W, H, *p,
           title="Знаковий зсув робить із числа суцільну маску 0 або всі-одиниці")


# ── branchless-flow: дві гілки (межа + маска) сходяться у виборі без if ───────
# Ідея (proj): ліворуч рахуємо межу зі знаку доданків, праворуч — маску
# переповнення двома XOR; фінал змішує межу й суму без розгалуження.
def fig_branchless_flow():
    W, H = 720, 360
    p = []
    bx0, w0, h0 = textbox(W / 2, 58, "доданки  a,  b   (сума s = a + b)", size=12,
                          fill=FILL, stroke=INK, sw=1.6, bold=True)
    p.append(bx0)

    lx, rx = 175, 545
    yb = 152
    bl, wl, hl = textbox(lx, yb, ["знак доданків: a >> 31", "плюс → межа = INT_MAX", "мінус → межа = INT_MIN"],
                         size=11, fill="#eef4ff", stroke=NEG, sw=1.6)
    p.append(bl)
    br, wr, hr = textbox(rx, yb, ["переповнення?", "(a^b) | ~(b^s) → знак", "сталось? всі-1 : 0"],
                         size=11, fill="#f2ecf8", stroke="#8a5fb0", sw=1.6)
    p.append(br)

    p.append(arrow(W / 2 - 40, 58 + h0 / 2, lx, yb - hl / 2 - 2, color=MUTED, sw=1.6))
    p.append(arrow(W / 2 + 40, 58 + h0 / 2, rx, yb - hr / 2 - 2, color=MUTED, sw=1.6))

    yf = 268
    bf, wf, hf = textbox(W / 2, yf, "r = (межа & маска) | (сума & ~маска)", size=13,
                         fill="#eafaf0", stroke=FIELD, sw=2, bold=True, color=FIELD)
    p.append(bf)
    p.append(arrow(lx, yb + hl / 2, W / 2 - 70, yf - hf / 2 - 2, color=MUTED, sw=1.6))
    p.append(arrow(rx, yb + hr / 2, W / 2 + 70, yf - hf / 2 - 2, color=MUTED, sw=1.6))

    p.append(text(W / 2, H - 14, "переповнення → береться межа; нема → береться сума. Жодного if — рівний час.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "branchless-flow.svg"), W, H, *p,
           title="Безгіллясте знакове насичення: дві гілки сходяться у виборі маскою")


if __name__ == "__main__":
    fig_wrap_vs_sat()
    fig_audio_clip()
    fig_branchless()
    fig_domains()
    fig_sat_timeline()
    fig_sign_mask()
    fig_branchless_flow()
    print("OK: figures written to", OUT)
