# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODE_BG = "#0f1b14"   # темна заливка код-блоків у фігурах
CODE_FG = "#eaf6ee"   # світлий текст коду
ASM_BG  = "#13202a"   # асемблер
ASM_FG  = "#7fe0a0"
NUM_BG  = "#101418"    # голі числа


def codebox(x, y, w, h, s, fg=CODE_FG, bg=CODE_BG, size=12):
    """Темна рамка з моноширинним рядком, вирівняним ліворуч (для коду у фігурах)."""
    out = rect(x, y, w, h, fill=bg, stroke="#0a120d", sw=1.4, rx=8)
    out += ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', monospace" '
            'font-size="%d" fill="%s" text-anchor="start" font-weight="700">%s</text>'
            % (x + 16, y + h / 2 + size * 0.35, size, fg, esc(s)))
    return out


# ── three-stages: оглядовий конвеєр препроцесор → компілятор → асемблер ────────
# Ідея: один файл коду спускається трьома стадіями в один об'єктний файл; на
# кожній межі підписано, ЩО тече далі (форма даних міняється).

def fig_three_stages():
    W, H = 820, 300
    p = []
    y = 150
    bh = 80
    # вузли: вхід, три стадії, вихід (x, ширина, підпис, заливка, колір, кегль)
    nodes = [
        (20, 116, "файл коду\n(.c / .cpp)", "#eef6ef", FIELD, 11),
        (180, 150, "Препроцесор", BG, INK, 12),
        (360, 150, "Компілятор", BG, INK, 12),
        (540, 150, "Асемблер", BG, INK, 12),
        (700, 104, "об'єктний\nфайл .o", "#eef4ff", NEG, 11),
    ]
    spans = []
    for x, w, lab, fill, col, sz in nodes:
        p.append(fitbox(x, y - bh / 2, w, bh, lab, size=sz, fill=fill, stroke=col, sw=1.8, bold=True, color=col))
        spans.append((x, x + w))
    # стрілки між вузлами з підписом форми даних на межі
    edge_lbl = ["розгорнутий\nтекст", "асемблер", "числа", ""]
    for i in range(len(spans) - 1):
        x1 = spans[i][1]
        x2 = spans[i + 1][0]
        p.append(arrow(x1 + 2, y, x2 - 2, y, color=INK, sw=2.2))
        if edge_lbl[i]:
            p.append(mtext((x1 + x2) / 2, y - 22, edge_lbl[i], size=9, color=MUTED, bold=True))
    p.append(text(W / 2, H - 40, "кожна стадія опускає код на щабель нижче (lowering)",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, H - 20, "один файл коду → один об'єктний файл", size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "three-stages.svg"), W, H, *p,
           title="Три стадії: препроцесор → компілятор → асемблер")


# ── preprocessor: суто текстові операції #include / #define / #ifdef ───────────
# Ідея: показати три директиви як механічні дії над текстом; на виході — чистий
# код без «#».

def fig_preprocessor():
    W, H = 720, 320
    p = []
    cx = W / 2
    # три директиви як рядки-операції
    ops = [
        (90, "#include", "вклеїти весь текст заголовка сюди", "#eef4ff", NEG),
        (160, "#define", "підставити: LED → 2 скрізь у тексті", "#eef6ef", FIELD),
        (230, "#ifdef", "лишити або викинути шматок коду", "#fdf6e3", "#b8860b"),
    ]
    for y, name, what, fill, col in ops:
        b, bw, bh = textbox(150, y, name, size=13, bold=True, fill=fill, stroke=col, sw=1.8, color=col, min_w=120)
        p.append(b)
        p.append(text(230, y + 4, what, size=11, color=INK, anchor="start"))
    # стрілка вниз до результату
    p.append(arrow(cx, 270, cx, 296, color=INK, sw=2.0))
    p.append(text(cx, 312, "один суцільний текст без жодної «#»-директиви (одиниця трансляції)",
                  size=11, color=INK, bold=True))
    p.append(text(cx, 50, "препроцесор ріже й клеїть ТЕКСТ — сенсу коду не розуміє",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "preprocessor.svg"), W, H, *p,
           title="Препроцесор: суто текстові операції")


# ── compiler-internals: фронт / мід / бек і фази всередині компілятора ─────────
# Ідея: «компілятор» — не один крок, а ланцюг фаз; згруповані у фронт (мова),
# мід (IR-оптимізація, нейтральна до заліза) і бек (під конкретне ядро).
# На стиках фронт→мід і мід→бек стоїть IR — точка розчеплення.

def fig_compiler_internals():
    W, H = 760, 340
    p = []
    # три зони-смуги
    zones = [
        (40, 220, "#eef6ef", FIELD, "ФРОНТ (залежить від мови)"),
        (270, 200, "#fff7e6", "#b8860b", "МІД (нейтральний до заліза)"),
        (480, 240, "#eef4ff", NEG, "БЕК (залежить від ядра)"),
    ]
    for zx, zw, fill, col, lab in zones:
        p.append(rect(zx, 64, zw, 220, fill=fill, stroke=col, sw=1.6, rx=10))
        p.append(text(zx + zw / 2, 84, lab, size=11, color=col, bold=True))
    # фази-коробочки усередині зон
    phases = [
        (150, "лексер\n(tokenizer)", FIELD),
        (150, None, None),  # placeholder spacing handled manually
    ]
    # ставимо фази вручну з координатами
    boxes = [
        (95, 150, "лексер\n(tokenizer)", FIELD, "#eafaf0"),
        (215, 150, "парсер →\nдерево (AST)", FIELD, "#eafaf0"),
        (370, 130, "семантика:\nтипи, імена", "#b8860b", "#fff3d6"),
        (370, 210, "оптимізатор\nна IR", "#b8860b", "#fff3d6"),
        (600, 150, "кодоген:\nасемблер ядра", NEG, "#e8efff"),
    ]
    centers = {}
    for bx, by, lab, col, fill in boxes:
        b, bw, bh = textbox(bx, by, lab, size=10.5, bold=True, color=col, fill=fill, stroke=col, sw=1.6, min_w=96)
        p.append(b)
        centers[(bx, by)] = (bw, bh)
    # потік стрілками: лексер→парсер→семантика→оптимізатор→кодоген
    seq = [(95, 150), (215, 150), (370, 130), (370, 210), (600, 150)]
    for i in range(len(seq) - 1):
        (x1, y1), (x2, y2) = seq[i], seq[i + 1]
        w1, h1 = centers[(x1, y1)]
        w2, h2 = centers[(x2, y2)]
        if y1 == y2:
            p.append(arrow(x1 + w1 / 2, y1, x2 - w2 / 2, y2, color=INK, sw=1.8))
        else:
            p.append(arrow(x1, y1 + h1 / 2, x2, y2 - h2 / 2, color=INK, sw=1.8))
    # позначка IR на стику мід (де живе проміжне подання)
    p.append(text(370, 178, "IR", size=13, color="#b8860b", bold=True))
    p.append(text(W / 2, H - 40, "IR — спільна проміжна мова: розчіплює «яку мову» від «під яке ядро»",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, H - 20, "одна передня частина + різні задні = той самий компілятор під багато ядер",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "compiler-internals.svg"), W, H, *p,
           title="Усередині компілятора: фронт · мід · бек")


# ── optimization: той самий результат меншими/швидшими командами ──────────────
# Ідея: ліворуч наївний код «у лоб», праворуч — оптимізований; результат той
# самий, шлях коротший.

def fig_optimization():
    W, H = 720, 300
    p = []
    # ліва панель — як написано
    lx, rx, ty, bw, bh = 60, 400, 90, 260, 150
    p.append(rect(lx, ty, bw, bh, fill="#fdecea", stroke=POS, sw=1.6, rx=10))
    p.append(text(lx + bw / 2, ty - 12, "як написано (у лоб)", size=12, color=POS, bold=True))
    p.append(codebox(lx + 14, ty + 22, bw - 28, 30, "x = 2 + 3;", size=11))
    p.append(codebox(lx + 14, ty + 60, bw - 28, 30, "int t = a*b;  // не вжито", size=10))
    p.append(codebox(lx + 14, ty + 98, bw - 28, 30, "for(i..) sum+=i;", size=11))
    # права панель — що згенеровано
    p.append(rect(rx, ty, bw, bh, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(rx + bw / 2, ty - 12, "що згенеровано", size=12, color=FIELD, bold=True))
    p.append(codebox(rx + 14, ty + 22, bw - 28, 30, "x = 5;   // пораховано", size=11, bg="#13251a", fg=ASM_FG))
    p.append(codebox(rx + 14, ty + 60, bw - 28, 30, "(зникло)  // мертвий код", size=10, bg="#13251a", fg=ASM_FG))
    p.append(codebox(rx + 14, ty + 98, bw - 28, 30, "розгорнуто/злито", size=11, bg="#13251a", fg=ASM_FG))
    # стрілка між панелями
    p.append(arrow(lx + bw + 6, ty + bh / 2, rx - 6, ty + bh / 2, color=INK, sw=2.4))
    p.append(text((lx + bw + rx) / 2, ty + bh / 2 - 12, "те саме", size=10, color=MUTED, bold=True))
    p.append(text(W / 2, H - 26, "результат зобов'язаний збігтися — шлях до нього компілятор вільний переписати",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "optimization.svg"), W, H, *p,
           title="Оптимізація: той самий результат, коротший шлях")


# ── assembler: кожна мнемоніка → одна машинна команда-число ───────────────────
# Ідея: словникова заміна один-в-один; ніякого розбору, лише таблиця.

def fig_assembler():
    W, H = 720, 280
    p = []
    rows = [
        ("load  r1, [GPIO_OUT]", "3A 01 7C"),
        ("or    r1, r1, 0x04", "2B 01 04"),
        ("store [GPIO_OUT], r1", "3C 01 7C"),
    ]
    y = 90
    lh = 56
    lx, rx = 70, 470
    bw_l, bw_r = 330, 180
    p.append(text(lx + bw_l / 2, y - 16, "асемблер (мнемоніки)", size=12, color=INK, bold=True))
    p.append(text(rx + bw_r / 2, y - 16, "машинний код (числа)", size=12, color=NEG, bold=True))
    for mnem, num in rows:
        p.append(codebox(lx, y, bw_l, 40, mnem, size=12))
        p.append(arrow(lx + bw_l + 8, y + 20, rx - 8, y + 20, color=INK, sw=2.0))
        p.append(codebox(rx, y, bw_r, 40, num, size=12, bg=NUM_BG, fg=ASM_FG))
        y += lh
    p.append(text(W / 2, H - 26, "найпростіша стадія: ніякого розуму, лише словник «мнемоніка → число»",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "assembler.svg"), W, H, *p,
           title="Асемблер: дослівний переклад слів у числа")


# ── trace: один вираз крізь стадії — токени → AST → IR → асемблер → числа ──────
# Ідея: провести ОДИН вираз через усі форми, відкриваючи й нутрощі компілятора
# (токени, дерево, IR), а не лише вхід/вихід.

def fig_trace():
    W, H = 760, 620
    p = []
    x0, bw = 60, 640
    y = 64
    steps = [
        ("1 · вихідний код (з директивою)", "#define LED_PIN 2   ·   GPIO_OUT |= (1 << LED_PIN);", CODE_BG, CODE_FG, "препроцесор"),
        ("2 · після препроцесора (текст підставлено)", "GPIO_OUT |= (1 << 2);", CODE_BG, CODE_FG, "лексер"),
        ("3 · токени (лексер порізав на слова)", "[GPIO_OUT] [|=] [(] [1] [<<] [2] [)] [;]", "#1a2230", "#bcd0ff", "парсер"),
        ("4 · дерево розбору (AST)", "(|=  GPIO_OUT  (<<  1  2))", "#1a2230", "#bcd0ff", "семантика + IR"),
        ("5 · проміжний код (IR, 1<<2 згорнуто)", "t = GPIO_OUT ;  t = t | 4 ;  GPIO_OUT = t", "#2a230f", "#f0dca0", "кодоген (під ядро)"),
        ("6 · асемблер (мнемоніки ядра)", "load r1,[GPIO_OUT] · or r1,r1,0x04 · store [GPIO_OUT],r1", ASM_BG, ASM_FG, "асемблер"),
        ("7 · машинний код (числа)", "3A 01 7C    2B 01 04    3C 01 7C", NUM_BG, ASM_FG, None),
    ]
    bh = 44
    gap = 36
    for label, code, bg, fg, edge in steps:
        p.append(text(x0, y - 6, label, size=11, color=INK, anchor="start", bold=True))
        p.append(codebox(x0, y, bw, bh, code, size=11.5, bg=bg, fg=fg))
        ny = y + bh + gap
        if edge:
            ax = x0 + bw * 0.5
            p.append(arrow(ax, y + bh + 2, ax, ny - 6, color=INK, sw=2.0))
            p.append(text(ax + 14, y + bh + gap / 2 + 4, edge + " ↓", size=10, color=MUTED, anchor="start", bold=True))
        y = ny
    render(os.path.join(OUT, "trace.svg"), W, H, *p,
           title="Один вираз крізь стадії: токени → AST → IR → асемблер → числа")


# ── levels: -O0 / -O2 / -Os — три компроміси (для proj-optimizer) ─────────────
# Ідея: три колонки-картки; той самий сенс, різний машинний код під різну мету.

def fig_levels():
    W, H = 760, 320
    p = []
    cols = [
        (40, "-O0", "як написано", NEG, "#eef4ff",
         ["вірне, без переписувань", "велике й повільне", "ЗРУЧНЕ для відлагодження", "сюди — коли ловиш баг"]),
        (270, "-O2", "швидко", FIELD, "#eef6ef",
         ["переписане заради темпу", "менше й швидше", "важче відлагоджувати", "реліз, де треба швидкість"]),
        (500, "-Os", "компактно", "#b8860b", "#fff7e6",
         ["заради малого розміру", "економить Flash на МК", "важче відлагоджувати", "тісна пам'ять МК"]),
    ]
    cw = 220
    for cx, name, sub, col, fill, items in cols:
        p.append(rect(cx, 64, cw, 230, fill=fill, stroke=col, sw=2, rx=12))
        p.append(text(cx + cw / 2, 96, name, size=20, color=col, bold=True))
        p.append(text(cx + cw / 2, 116, sub, size=11, color=MUTED, italic=True))
        p.append(line(cx + 16, 128, cx + cw - 16, 128, color=col, sw=1.2))
        yy = 156
        for it in items:
            p.append(text(cx + 16, yy, "• " + it, size=10, color=INK, anchor="start"))
            yy += 32
    p.append(text(W / 2, H - 16, "однаковий сенс програми — різний машинний код під різну мету",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "levels.svg"), W, H, *p,
           title="Рівні оптимізації: -O0 · -O2 · -Os")


# ── vanish: згортання сталих, мертвий код, інлайн + пастка volatile ───────────
# Ідея: три рядки «джерело → оптимізований» і знизу — рамка про небезпеку на МК.

def fig_vanish():
    W, H = 760, 400
    p = []
    p.append(text(280, 78, "як написано", size=11, color=INK, bold=True))
    p.append(text(600, 78, "що згенеровано", size=11, color=INK, bold=True))
    rows = [
        ("Згортання сталих", "x = 2 + 3;", "x = 5;", "пораховано наперед", FIELD, "#eef6ef"),
        ("Мертвий код", "int t = a*b; // не вжито", "(зникло)", "ось чому «зник» код", POS, "#fdecea"),
        ("Інлайн функції", "y = sq(x);", "y = x*x;", "тіло вставлено в виклик", NEG, "#eef4ff"),
    ]
    y = 96
    for tag, src, dst, note, col, fill in rows:
        p.append(text(40, y + 26, tag, size=10, color=col, anchor="start", bold=True))
        p.append(codebox(180, y, 280, 40, src, size=10.5))
        p.append(arrow(466, y + 20, 516, y + 20, color=col, sw=2.2))
        p.append(codebox(524, y, 196, 40, dst, size=11, bg="#13251a", fg=ASM_FG))
        p.append(text(524, y + 56, note, size=9, color=MUTED, anchor="start"))
        y += 76
    # рамка-пастка
    p.append(rect(60, 320, 640, 64, fill="#fff7e6", stroke="#b8860b", sw=1.6, rx=10))
    p.append(mtext(380, 342,
                   ["Пастка на МК: порожній цикл-затримка зникає, а читання регістра компілятор «кешує».",
                    "Ліки — volatile: «це може змінитися саме — не оптимізуй доступ»."],
                   size=10, color=INK))
    render(os.path.join(OUT, "vanish.svg"), W, H, *p,
           title="Чому «зник» мій код: що робить оптимізатор")


# ── timeline: дорога GCC від GNU (1983) до кожного тулчейна (для hist-gcc) ─────
# Ідея: горизонтальна вісь часу з віхами, що чергуються вгору/вниз.

def fig_timeline():
    W, H = 820, 320
    p = []
    ax0, ax1, ay = 70, 760, 168
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=2.4))
    marks = [
        ("1983", "GNU", "вільна ОС", NEG),
        ("1985", "FSF", "фонд ПЗ", NEG),
        ("1987", "GCC 1.0", "компілятор C", FIELD),
        ("1989", "GPL", "копілефт", "#b8860b"),
        ("1997", "EGCS-форк", "пожвавив", POS),
        ("1999", "знову GCC", "форк офіційний", FIELD),
        ("тепер", "усюди", "будь-яке ядро", FIELD),
    ]
    n = len(marks)
    bw, bh = 108, 52
    for i, (yr, name, sub, col) in enumerate(marks):
        cx = ax0 + (ax1 - ax0) * i / (n - 1)
        up = (i % 2 == 0)
        p.append(circle(cx, ay, 6, fill=col, stroke=col, sw=1))
        if up:
            p.append(line(cx, ay - 6, cx, ay - 34, color=col, sw=1.6))
            by = ay - 34 - bh
        else:
            p.append(line(cx, ay + 6, cx, ay + 34, color=col, sw=1.6))
            by = ay + 34
        bx = min(max(cx - bw / 2, 4), W - bw - 4)
        p.append(rect(bx, by, bw, bh, fill="#fbfbff" if col == NEG else "#fbfffb", stroke=col, sw=1.6, rx=8))
        p.append(text(bx + bw / 2, by + 18, yr, size=11, color=col, bold=True))
        p.append(text(bx + bw / 2, by + 32, name, size=10, color=INK, bold=True))
        p.append(text(bx + bw / 2, by + 45, sub, size=9, color=MUTED))
    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Дорога GCC: від ідеї про свободу до кожного тулчейна")


# ── retarget: один GCC → багато ядер (для hist-gcc) ───────────────────────────
# Ідея: одне джерело-ядро GCC, від нього стрілки до кожної архітектури.

def fig_retarget():
    W, H = 760, 360
    p = []
    # центральний вузол
    b, bw, bh = textbox(150, 180, "GCC\nодин вільний\nкомпілятор", size=12, bold=True,
                        fill="#eef6ef", stroke=FIELD, sw=2.2, color=FIELD, min_w=150)
    p.append(b)
    targets = ["AVR", "ARM", "Xtensa", "RISC-V", "x86"]
    tx = 470
    n = len(targets)
    for i, t in enumerate(targets):
        ty = 90 + (260) * i / (n - 1)
        tb, tbw, tbh = textbox(tx, ty, t, size=11, bold=True, fill=BG, stroke=INK, sw=1.4, min_w=110)
        p.append(line(150 + bw / 2, 180, tx - tbw / 2, ty, color=FIELD, sw=1.8))
        p.append(tb)
        p.append(text(tx + tbw / 2 + 8, ty + 4, "→ свій GCC", size=9, color=MUTED, anchor="start"))
    p.append(text(W / 2, H - 22, "переносність: задню частину доточують під нове ядро — і чіп дістає вільний компілятор",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "retarget.svg"), W, H, *p,
           title="GCC переносний: один компілятор під будь-який чіп")


# ── fork: розкол EGCS і повернення офіційним GCC (для hist-gcc) ────────────────
# Ідея: гілка відходить від загальмованого GCC, жвавішає й повертається офіційною.

def fig_fork():
    W, H = 760, 320
    p = []
    a, aw, ah = textbox(150, 180, "GCC (FSF)\nстабільність понад усе\nпатчі копичаться", size=10.5,
                        bold=False, fill="#eef4ff", stroke=NEG, sw=1.8, color=INK, min_w=200)
    p.append(text(150, 180 - 38, "GCC (FSF)", size=12, color=NEG, bold=True))
    p.append(a)
    b, bw, bh = textbox(420, 130, "EGCS-форк (1997)\nCygnus + спільнота\nшвидше; нові мови", size=10.5,
                        bold=False, fill="#fdecea", stroke=POS, sw=1.8, color=INK, min_w=200)
    p.append(text(420, 130 - 30, "EGCS-форк (1997)", size=12, color=POS, bold=True))
    p.append(b)
    c, cw, ch = textbox(640, 210, "знову GCC (1999)\nфорк став офіційним\nвідкритіша модель", size=10,
                        bold=False, fill="#eef6ef", stroke=FIELD, sw=1.8, color=INK, min_w=180)
    p.append(text(640, 210 - 28, "знову GCC (1999)", size=11.5, color=FIELD, bold=True))
    p.append(c)
    p.append(arrow(150 + aw / 2, 168, 420 - bw / 2, 138, color=POS, sw=2.2))
    p.append(arrow(420 + bw / 2, 150, 640 - cw / 2, 200, color=FIELD, sw=2.2))
    p.append(line(150 + aw / 2, 196, 640 - cw / 2 - 4, 220, color=MUTED, sw=1.4, dash="4 3"))
    p.append(text(330, 250, "(стара гілка згасає)", size=9, color=MUTED))
    p.append(text(W / 2, H - 20, "проєкт переріс контроль однієї людини чи фонду: GCC — праця тисяч",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "fork.svg"), W, H, *p,
           title="Розкол EGCS: форк, що переміг і повернувся")


if __name__ == "__main__":
    fig_three_stages()
    fig_preprocessor()
    fig_compiler_internals()
    fig_optimization()
    fig_assembler()
    fig_trace()
    fig_levels()
    fig_vanish()
    fig_timeline()
    fig_retarget()
    fig_fork()
    print("OK: figures written to", OUT)
