# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── unsigned-wrap: 255 + 1 = 0 на колі-одометрі ──────────────────────────────
# Ідея: дев'ятий біт переносу випадає за межу байта, лишаються вісім нулів;
# показуємо як коло, що «перевалює» з верху в нуль.
def fig_unsigned_wrap():
    W, H = 700, 330
    p = []
    # ліворуч — стовпчик бітів
    bx = 64
    p.append(text(bx + 70, 52, "255 + 1 у 8-бітному байті", size=13, bold=True, anchor="middle"))
    rows = [
        ("11111111", "= 255", INK),
        ("+      1", "", NEG),
        ("100000000", "9 бітів!", POS),
        ("00000000", "= 0", FIELD),
    ]
    y = 88
    for bits, note, col in rows:
        p.append(text(bx, y, bits, size=16, color=col, anchor="start"))
        if note:
            p.append(text(bx + 150, y, note, size=12, color=MUTED, anchor="start"))
        y += 30
    # рамка навколо зайвого біта
    p.append(rect(bx - 4, 148 - 18, 16, 24, fill="none", stroke=POS, sw=2, rx=3))
    p.append(text(bx + 4, 222, "старший біт випадає за межу", size=11, color=POS, anchor="start"))

    # праворуч — коло-одометр
    cx, cy, r = 520, 178, 96
    p.append(circle(cx, cy, r, fill=BG, stroke=LINE, sw=2))
    # позначки 0, 64, 128, 192, 255 по колу
    marks = [(0, "0"), (64, "64"), (128, "128"), (192, "192"), (255, "255")]
    for val, lab in marks:
        ang = -math.pi / 2 + 2 * math.pi * val / 256.0
        mx, my = cx + r * math.cos(ang), cy + r * math.sin(ang)
        lx, ly = cx + (r + 18) * math.cos(ang), cy + (r + 18) * math.sin(ang)
        p.append(circle(mx, my, 3, fill=INK, stroke=INK, sw=1))
        p.append(text(lx, ly + 4, lab, size=11, color=INK))
    # дуга-стрілка через верх: 255 → 0 (перескок)
    a1 = -math.pi / 2 + 2 * math.pi * 250 / 256.0
    p.append(arrow(cx + r * math.cos(a1), cy + r * math.sin(a1),
                   cx + r * math.cos(-math.pi / 2 + 0.06), cy + r * math.sin(-math.pi / 2 + 0.06),
                   color=POS, sw=2.4))
    p.append(text(cx, cy - 4, "+1", size=14, color=POS, bold=True))
    p.append(text(cx, cy + 16, "255 → 0", size=12, color=MUTED))

    render(os.path.join(OUT, "unsigned-wrap.svg"), W, H, *p,
           title="Беззнакове переповнення: лічильник «перевалює» через нуль")


# ── signed-wrap: +127 + 1 = −128, перекидання знаку ──────────────────────────
# Ідея: старший біт стає знаковим; сума двох додатних дає від'ємне на колі
# доповняльного коду, де верх (+127) межує з низом (−128).
def fig_signed_wrap():
    W, H = 700, 330
    p = []
    bx = 64
    p.append(text(bx + 70, 52, "+127 + 1 у знаковому байті", size=13, bold=True, anchor="middle"))
    rows = [
        ("01111111", "= +127", NEG),
        ("+      1", "", INK),
        ("10000000", "знак → 1", POS),
        ("= −128", "(доповн. код)", POS),
    ]
    y = 88
    for bits, note, col in rows:
        p.append(text(bx, y, bits, size=16, color=col, anchor="start"))
        if note:
            p.append(text(bx + 150, y, note, size=12, color=MUTED, anchor="start"))
        y += 30
    p.append(text(bx, 222, "два додатні дали від'ємне", size=11, color=POS, anchor="start"))

    # коло доповняльного коду: 0 угорі, +127 праворуч-внизу межує з −128
    cx, cy, r = 520, 178, 96
    p.append(circle(cx, cy, r, fill=BG, stroke=LINE, sw=2))
    marks = [(0, "0", INK), (63, "+63", NEG), (127, "+127", NEG),
             (128, "−128", POS), (192, "−64", POS)]
    for val, lab, col in marks:
        ang = -math.pi / 2 + 2 * math.pi * val / 256.0
        mx, my = cx + r * math.cos(ang), cy + r * math.sin(ang)
        lx, ly = cx + (r + 20) * math.cos(ang), cy + (r + 20) * math.sin(ang)
        p.append(circle(mx, my, 3, fill=col, stroke=col, sw=1))
        p.append(text(lx, ly + 4, lab, size=11, color=col))
    # стрілка через стик +127 → −128 (нижня частина кола)
    a1 = -math.pi / 2 + 2 * math.pi * 124 / 256.0
    a2 = -math.pi / 2 + 2 * math.pi * 131 / 256.0
    p.append(arrow(cx + r * math.cos(a1), cy + r * math.sin(a1),
                   cx + r * math.cos(a2), cy + r * math.sin(a2), color=POS, sw=2.6))
    p.append(text(cx, cy - 2, "+1", size=14, color=POS, bold=True))
    p.append(text(cx, cy + 18, "знак перевернувся", size=11, color=MUTED))

    render(os.path.join(OUT, "signed-wrap.svg"), W, H, *p,
           title="Знакове переповнення: верхня межа межує з найменшою від'ємною")


# ── flags-cv: прапорці C і V на тому самому додаванні ─────────────────────────
# Ідея: ті самі біти, два різні тлумачення; C ловить беззнакове, V — знакове.
def fig_flags_cv():
    W, H = 700, 300
    p = []
    # дві колонки: C (беззнакове) і V (знакове)
    colA, colB = 200, 500
    p.append(text(colA, 56, "Прапорець C (Carry)", size=13, bold=True, color=POS))
    p.append(text(colB, 56, "Прапорець V (oVerflow)", size=13, bold=True, color=NEG))

    p.append(fitbox(colA - 130, 76, 260, 50,
                    "переніс «випав» за старший біт", size=12, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(fitbox(colB - 130, 76, 260, 50,
                    "переніс У старший біт ≠ переніс З нього", size=12, fill="#eef4ff", stroke=NEG, sw=1.6))

    p.append(text(colA, 152, "ознака БЕЗЗНАКОВОГО", size=11, color=MUTED))
    p.append(text(colB, 152, "ознака ЗНАКОВОГО", size=11, color=MUTED))

    p.append(text(colA, 184, "255 + 1 → C = 1", size=14, bold=True, color=POS))
    p.append(text(colB, 184, "127 + 1 → V = 1", size=14, bold=True, color=NEG))

    # спільний низ: ті самі біти
    p.append(line(80, 214, W - 80, 214, color=MUTED, sw=1, dash="5 4"))
    p.append(text(W / 2, 240, "суматор додає біти однаково — різняться лише прапорці-сторожі",
                  size=12, color=INK, italic=True))
    p.append(text(W / 2, 264, "обидва живуть у регістрі стану; за замовчуванням їх ніхто не перевіряє",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "flags-cv.svg"), W, H, *p,
           title="Два прапорці на одне додавання: C — беззнакове, V — знакове")


# ── disasters: чотири знамениті катастрофи переповнення ──────────────────────
# Ідея: 2×2 картки, кожна — реальний випадок із типом, що переповнився.
def fig_disasters():
    W, H = 720, 320
    p = []
    cards = [
        (40, 56, "Ariane 5 (1996)", "float64 → int16; ракета\n≈370 млн $ за ≈37 с", POS, "#fdecea"),
        (370, 56, "«Gangnam Style» (2014)", "int32-лічильник переглядів\nдійшов до ≈2.1 млрд", "#8a5fb0", "#f2ecf8"),
        (40, 190, "Проблема 2038", "Unix-час = int32 секунд;\n19.01.2038 «стрибне» в 1901", NEG, "#eef4ff"),
        (370, 190, "Pac-Man, рівень 256", "8-бітний лічильник рівнів\nпереповнюється — екран псується", FIELD, "#eafaf0"),
    ]
    cw, ch = 310, 104
    for x, y, title, body, col, fill in cards:
        p.append(rect(x, y, cw, ch, fill=fill, stroke=col, sw=1.8))
        p.append(text(x + 14, y + 26, title, size=13, bold=True, color=col, anchor="start"))
        p.append(mtext(x + 14, y + 52, body, size=11, color=INK, anchor="start", lh=1.3))
    render(os.path.join(OUT, "disasters.svg"), W, H, *p,
           title="Межі типів реальні: чотири знамениті переповнення")


# ── avoiding: ліворуч убезпечитися, праворуч wrap як фіча ─────────────────────
# Ідея: дві колонки — захист (ширший тип / перевірка / насичення) проти
# свідомого wrap (таймери / кільцеві буфери / різниця часу).
def fig_avoiding():
    W, H = 720, 320
    p = []
    midx = W / 2
    p.append(line(midx, 44, midx, H - 24, color=MUTED, sw=1, dash="5 5"))

    p.append(text(midx / 2, 60, "Убезпечитися", size=14, bold=True, color=FIELD))
    safe = [
        "ширший тип (8→16→32→64)\nіз запасом",
        "перевірка меж або прапорців",
        "насичення: 255 + 1 = 255\n(впертися, не перевалити)",
    ]
    y = 92
    for s in safe:
        p.append(fitbox(30, y, midx - 60, 56, s, size=11, fill="#eafaf0", stroke=FIELD, sw=1.5))
        y += 70

    p.append(text(midx + midx / 2, 60, "Wrap — це фіча", size=14, bold=True, color=NEG))
    feat = [
        "таймери й лічильники\nпо колу",
        "кільцеві буфери: індекс\nза модулем",
        "різниця часу t₂ − t₁\nу беззнакових — вірна",
    ]
    y = 92
    for s in feat:
        p.append(fitbox(midx + 30, y, midx - 60, 56, s, size=11, fill="#eef4ff", stroke=NEG, sw=1.5))
        y += 70

    p.append(text(W / 2, H - 8, "різниця одна: чи передбачив переповнення інженер",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "avoiding.svg"), W, H, *p,
           title="Те саме «перевалювання»: загроза ліворуч, користь праворуч")


# ════════════════ proj-overflow-checks ════════════════

# ── post-check-trap: компілятор викидає перевірку ПІСЛЯ знакового переповнення ─
# Ідея: ланцюг міркувань оптимізатора, що стирає вартового `if (y < x)`.
def fig_post_check_trap():
    W, H = 720, 300
    p = []
    p.append(text(W / 2, 56, "int y = x + 1;  if (y < x) overflow();", size=15, bold=True))
    chain = [
        ("UB: знакове не переповнюється", "припущення стандарту", NEG),
        ("отже y завжди > x", "наслідок", INK),
        ("отже (y < x) завжди хибне", "висновок", INK),
        ("перевірку викинуто з коду", "вартовий зник", POS),
    ]
    y = 96
    bw = 420
    cxs = W / 2
    prev = None
    for lab, note, col in chain:
        b = fitbox(cxs - bw / 2, y, bw, 40, lab, size=12, fill="#f4f6f8", stroke=col, sw=1.7, color=col, bold=True)
        p.append(b)
        p.append(text(cxs + bw / 2 + 12, y + 24, note, size=10, color=MUTED, anchor="start"))
        if prev is not None:
            p.append(arrow(cxs, prev + 40, cxs, y - 2, color=MUTED, sw=1.6))
        prev = y
        y += 56
    render(os.path.join(OUT, "post-check-trap.svg"), W, H, *p,
           title="Перевірка ПІСЛЯ: оптимізатор стирає її ще на компіляції")


# ── pre-check-rules: перевірка ДО операції, різниця межі й доданка ────────────
# Ідея: переставлена нерівність — звіряємо a з межею, з якої відняли b; сама
# різниця безпечна. Беззнаковий випадок один, знаковий — два боки.
def fig_pre_check_rules():
    W, H = 720, 300
    p = []
    p.append(text(W / 2, 52, "Питаємо ДО: чи лишилося місце для a + b?", size=13, bold=True))

    # беззнаковий
    p.append(fitbox(40, 78, 300, 86,
                    "Беззнаковий: один бік\n\na > UINT_MAX − b  →  вилізе\n(різниця безпечна: b ≤ UINT_MAX)",
                    size=11, fill="#eef4ff", stroke=NEG, sw=1.6))
    # знаковий
    p.append(fitbox(380, 78, 300, 86,
                    "Знаковий: два боки\n\nb>0 та a > INT_MAX − b → зверху\nb<0 та a < INT_MIN − b → знизу",
                    size=11, fill="#fdecea", stroke=POS, sw=1.6))

    p.append(text(W / 2, 200, "знак b підказує, яку межу звіряти", size=12, color=INK, italic=True))
    p.append(text(W / 2, 232, "жодна з цих перевірок сама не переповнюється — дію не виконуємо, поки не впевнились",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "pre-check-rules.svg"), W, H, *p,
           title="Перевірка ДО додавання: переставлена нерівність безпечна")


# ── toolbox: чим ловити переповнення, від надійного до ручного ────────────────
# Ідея: чотири підходи від «ширший тип» до ручної перевірки, з нотаткою застосовності.
def fig_toolbox():
    W, H = 720, 320
    p = []
    tools = [
        ("Ширший тип", "порахувати в int64, тоді\nзвузити з перевіркою", FIELD, "#eafaf0"),
        ("__builtin_*_overflow", "GCC/Clang: робить дію й каже,\nчи вилізло — найнадійніше", NEG, "#eef4ff"),
        ("Беззнаковий домен", "wrap навмисний (лічильники,\nгеш, різниця часу) — можна", "#8a5fb0", "#f2ecf8"),
        ("Ручна перевірка ДО", "a > INT_MAX − b; переносно\nбудь-куди, без розширень", INK, "#f4f6f8"),
    ]
    cw, ch = 320, 110
    pos = [(40, 56), (370, 56), (40, 192), (370, 192)]
    for (x, y), (title, body, col, fill) in zip(pos, tools):
        p.append(rect(x, y, cw, ch, fill=fill, stroke=col, sw=1.8))
        p.append(text(x + 14, y + 28, title, size=13, bold=True, color=col, anchor="start"))
        p.append(mtext(x + 14, y + 54, body, size=11, color=INK, anchor="start", lh=1.3))
    render(os.path.join(OUT, "toolbox.svg"), W, H, *p,
           title="Чим ловити переповнення: від найнадійнішого до найручнішого")


# ════════════════ hist-ariane5 ════════════════

# ── conversion: фатальне float64 → int16, виняток Ada ────────────────────────
# Ідея: широке 64-бітне дійсне не влазить у 16-бітне вікно; Ada кидає виняток,
# а не тихо перевалює (на відміну від C).
def fig_conversion():
    W, H = 720, 300
    p = []
    # широке дійсне
    p.append(rect(80, 64, 560, 40, fill="#eef4ff", stroke=NEG, sw=1.8))
    p.append(text(W / 2, 89, "BH — горизонтальний зсув: float64 (величезний діапазон)", size=13, bold=True, color=NEG))
    p.append(arrow(W / 2, 110, W / 2, 138, color=INK, sw=2))
    # вузьке ціле
    p.append(rect(240, 142, 240, 40, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(W / 2, 167, "int16: лише −32768 … +32767", size=13, bold=True, color=POS))
    p.append(text(W / 2, 206, "на Ariane 5 значення виросло за +32767 — старші біти не вмістились",
                  size=11, color=MUTED))
    # ключова відмінність — рамка
    p.append(fitbox(120, 226, 480, 50,
                    "мова Ada кинула виняток Operand Error — не тиха «перевалка» по колу, як у C, а зупинка",
                    size=11, fill="#f6f4ec", stroke=INK, sw=1.6))
    render(os.path.join(OUT, "conversion.svg"), W, H, *p,
           title="Фатальне перетворення: ширше дійсне не влізло у вузьке ціле")


# ── cascade: ланцюг із восьми ланок від біта до вибуху ───────────────────────
# Ідея: жодної поломки заліза — лише послідовність «логічних» рішень; розірвати
# можна було на будь-якій ланці.
def fig_cascade():
    W, H = 720, 360
    p = []
    steps = [
        "1. код Ariane 4 перенесли як є",
        "2. марна після старту функція рахує BH",
        "3. BH переповнює int16",
        "4. Ada кидає необроблений виняток",
        "5. обидва SRI «здаються»",
        "6. бортовий комп'ютер бере аварійний код за дані",
        "7. різко вивертає сопла",
        "8. потік ламає справну ракету",
    ]
    y = 56
    bw = 520
    cxs = W / 2
    cols = [INK, MUTED, POS, POS, POS, "#8a5fb0", NEG, POS]
    for i, s in enumerate(steps):
        p.append(fitbox(cxs - bw / 2, y, bw, 30, s, size=12,
                        fill="#f4f6f8", stroke=cols[i], sw=1.5, color=INK))
        if i < len(steps) - 1:
            p.append(arrow(cxs, y + 30, cxs, y + 36, color=MUTED, sw=1.5))
        y += 38
    render(os.path.join(OUT, "cascade.svg"), W, H, *p,
           title="Ланцюг відмови: жодної поломки заліза, лише вісім «логічних» ланок")


# ── reuse: та сама величина, дві траєкторії; 4 із 7 захищені ─────────────────
# Ідея: на пологій Ariane 4 BH під межею, на крутій Ariane 5 вилазить; із семи
# перетворень захистили чотири, фатальне лишили без захисту через бюджет ЦП.
def fig_reuse():
    W, H = 720, 388
    p = []
    # ліворуч — графік двох траєкторій BH проти межі int16
    ox, oy = 70, 250
    aw, ah = 300, 180
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 18, "час", size=11, italic=True))
    p.append(text(ox - 8, oy - ah - 4, "BH", size=11, bold=True, anchor="end", italic=True))
    # межа int16
    lim = oy - ah * 0.6
    p.append(line(ox, lim, ox + aw, lim, color=MUTED, sw=1.4, dash="6 4"))
    p.append(text(ox + aw + 2, lim + 4, "+32767", size=10, color=MUTED, anchor="start"))
    # Ariane 4 — пологий, під межею
    pts4 = []
    for i in range(0, 101):
        t = i / 100.0
        v = 0.5 * (1 - math.exp(-1.6 * t))
        pts4.append("%.1f,%.1f" % (ox + t * aw, oy - v * ah))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts4), NEG))
    p.append(text(ox + aw * 0.62, oy - ah * 0.36, "Ariane 4", size=10, color=NEG, anchor="start"))
    # Ariane 5 — крутий, за межу
    pts5 = []
    for i in range(0, 101):
        t = i / 100.0
        v = 0.95 * (1 - math.exp(-3.2 * t))
        pts5.append("%.1f,%.1f" % (ox + t * aw, oy - v * ah))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts5), POS))
    p.append(text(ox + aw * 0.34, oy - ah * 0.82, "Ariane 5", size=10, color=POS, bold=True, anchor="start"))

    # праворуч — 7 перетворень: 4 захищені, 3 ні
    rx = 430
    p.append(text(rx + 120, 64, "7 перетворень float→int", size=12, bold=True))
    p.append(text(rx + 120, 84, "захистили лише 4", size=11, color=MUTED))
    for i in range(7):
        cyi = 108 + i * 30
        protected = i < 4
        col = FIELD if protected else POS
        p.append(circle(rx + 30, cyi, 9, fill=("#eafaf0" if protected else "#fdecea"), stroke=col, sw=2))
        p.append(text(rx + 30, cyi + 4, "✓" if protected else "✗", size=12, color=col, bold=True))
        lab = "перевірка є" if protected else ("BH — без захисту" if i == 4 else "без захисту")
        p.append(text(rx + 52, cyi + 4, lab, size=11, color=INK, anchor="start"))
    p.append(fitbox(rx - 10, 332, 270, 46,
                    "три лишили без захисту,\nщоб утримати ЦП ≤ ≈80%",
                    size=11, fill="#f6f4ec", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "reuse.svg"), W, H, *p,
           title="Припущення пережило ракету: під межею на Ariane 4, за нею на Ariane 5")


if __name__ == "__main__":
    fig_unsigned_wrap()
    fig_signed_wrap()
    fig_flags_cv()
    fig_disasters()
    fig_avoiding()
    fig_post_check_trap()
    fig_pre_check_rules()
    fig_toolbox()
    fig_conversion()
    fig_cascade()
    fig_reuse()
    print("OK: figures written to", OUT)
