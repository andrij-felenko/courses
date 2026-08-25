# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Темна заливка для «машинного» боку (числа/код) — поза палітрою svgkit,
# бо тут потрібен контраст «світ людини / світ машини».
DARK   = "#13202a"
DARKMC = "#101418"
GREENT = "#7fe0a0"   # моноширинні числа на темному
GREYT  = "#6f8fa0"   # коментарі на темному
PAPER  = "#f6f4ec"


# ════════════════════════ СТАТТЯ «Компіляція» ════════════════════════

# ── two-worlds: прірва між текстом-для-людини й числами-для-машини ─────────────
def fig_two_worlds():
    W, H = 720, 300
    p = []
    # ліворуч — вихідний текст
    lx, ly, lw, lh = 40, 70, 280, 170
    p.append(rect(lx, ly, lw, lh, fill=DARK, stroke=INK, sw=1.5, rx=8))
    p.append(text(lx + 16, ly + 28, "вихідний код (для людини)", size=11, color="#8fcf9f", anchor="start", bold=True))
    p.append(text(lx + 16, ly + 70, "OUT |= (1 << 2);", size=15, color="#eaf6ee", anchor="start", bold=True))
    p.append(text(lx + 16, ly + 96, "// увімкнути біт 2", size=12, color="#7a9a86", anchor="start", italic=True))
    p.append(text(lx + lw / 2, ly + lh - 16, "легко читає людина", size=11, color=MUTED, italic=True))

    # стрілки до «?» переклад
    cx = W / 2
    p.append(arrow(lx + lw + 6, ly + lh / 2, cx - 22, ly + lh / 2, color=POS, sw=2.4))
    p.append(text(cx, ly + lh / 2 + 10, "?", size=30, color=POS, bold=True))
    p.append(arrow(cx + 22, ly + lh / 2, W - 280 - 46, ly + lh / 2, color=POS, sw=2.4))
    p.append(text(cx, ly + lh / 2 + 40, "переклад", size=11, color=POS, bold=True))

    # праворуч — машинний код
    rx, rw = W - 280 - 40, 280
    p.append(rect(rx, ly, rw, lh, fill=DARKMC, stroke="#000000", sw=1.5, rx=8))
    p.append(text(rx + 16, ly + 28, "машинний код (для ядра)", size=11, color="#7fa6bf", anchor="start", bold=True))
    for i, s in enumerate(("3A 01 7C 4F", "2B 01 04 00", "3C 01 7C 4F")):
        p.append(text(rx + 16, ly + 62 + i * 26, s, size=14, color=GREENT, anchor="start", bold=True))
    p.append(text(rx + rw / 2, ly + lh - 16, "єдине, що розуміє кремній", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-worlds.svg"), W, H, *p,
           title="Той самий намір — два геть різні описи")


# ── what-is-compilation: текст → компілятор → різні числа під різні ядра ───────
def fig_what_is_compilation():
    W, H = 760, 320
    p = []
    # вихідний код
    sx, sy, sw_, sh = 30, 130, 180, 76
    p.append(rect(sx, sy, sw_, sh, fill=DARK, stroke=INK, sw=1.5, rx=8))
    p.append(text(sx + sw_ / 2, sy + 30, "вихідний код", size=12, color="#8fcf9f", bold=True))
    p.append(text(sx + sw_ / 2, sy + 56, "OUT |= (1<<2);", size=12, color="#eaf6ee", bold=True))

    # компілятор
    cx, cy = 330, 168
    box, bw, bh = textbox(cx, cy, "Компілятор\nперекладач", size=13, bold=True,
                          fill=PAPER, stroke=INK, sw=2.2, color=INK, pad=14)
    p.append(arrow(sx + sw_ + 2, sy + sh / 2, cx - bw / 2 - 4, cy, color=INK, sw=2.2))
    p.append(box)

    # два виходи
    x2 = 560
    for j, (lab, code, sub) in enumerate((
            ("для Xtensa (ESP32, S3):", "3A 01 7C…  2B 01 04…", "під Xtensa"),
            ("для RISC-V (C3, C6):", "0C 1A 04…  93 81 41…", "під RISC-V"))):
        oy = 88 + j * 110
        p.append(rect(x2, oy, 180, 70, fill=DARKMC, stroke="#000000", sw=1.5, rx=8))
        p.append(text(x2 + 12, oy + 26, lab, size=10, color="#7fa6bf", anchor="start", bold=True))
        p.append(text(x2 + 12, oy + 52, code, size=12, color=GREENT, anchor="start", bold=True))
        p.append(line(cx + bw / 2 + 2, cy - 12 + j * 24, x2 - 4, oy + 35, color=INK, sw=2.0))
        p.append(text((cx + bw / 2 + x2) / 2, oy + 35 + (-14 if j == 0 else 18), sub, size=9, color=MUTED))

    p.append(text(W / 2, H - 18, "Один текст → різні числа під різні ядра (звідси «зібрати під ESP32 / під C3»)",
                  size=11, color=FIELD, bold=True))
    render(os.path.join(OUT, "what-is-compilation.svg"), W, H, *p,
           title="Які саме числа — залежить від ядра")


# ── compiled-vs-interpreted: переклад раз наперед чи щоразу на ходу ────────────
def fig_compiled_vs_interpreted():
    W, H = 760, 340
    p = []
    # ── ліва панель: компільований ──
    p.append(rect(24, 58, 350, 262, fill="none", stroke="#dfeede", sw=2, rx=12))
    p.append(text(199, 84, "Компільований — переклад РАЗ наперед", size=12, color=FIELD, bold=True))
    p.append(rect(54, 116, 140, 48, fill=DARK, stroke=INK, sw=1.8, rx=4))
    p.append(text(124, 145, "вихідний код", size=12, color="#eaf6ee", bold=True))
    p.append(arrow(196, 140, 234, 140, color=INK, sw=2.2)); p.append(text(215, 131, "раз", size=9, color=MUTED))
    p.append(rect(236, 116, 140, 48, fill=DARKMC, stroke=INK, sw=1.8, rx=4))
    p.append(text(306, 145, "машинний код", size=12, color=GREENT, bold=True))
    p.append(arrow(306, 166, 306, 206, color=FIELD, sw=2.4))
    p.append(rect(236, 208, 140, 50, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    p.append(text(306, 232, "Чіп біжить", size=12, color=POS, bold=True))
    p.append(text(306, 250, "напряму", size=9, color=MUTED))
    p.append(text(199, 290, "швидко · мало пам'яті · без посередника", size=10, color=INK, bold=True))
    p.append(text(199, 310, "← так роблять мікроконтролери", size=11, color=FIELD, bold=True))

    # ── права панель: інтерпретований ──
    p.append(rect(390, 58, 350, 262, fill="none", stroke="#e4e4e4", sw=2, rx=12))
    p.append(text(565, 84, "Інтерпретований — переклад НА ХОДУ", size=12, color=NEG, bold=True))
    p.append(rect(414, 116, 130, 48, fill=DARK, stroke=INK, sw=1.8, rx=4))
    p.append(text(479, 145, "вихідний код", size=11, color="#eaf6ee", bold=True))
    p.append(arrow(546, 140, 584, 140, color=NEG, sw=2.2))
    p.append(rect(586, 110, 140, 58, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    p.append(text(656, 134, "Інтерпретатор", size=11, color=NEG, bold=True))
    p.append(text(656, 154, "у пам'яті чипа", size=9, color=MUTED))
    p.append(arrow(656, 170, 656, 208, color=NEG, sw=2.4)); p.append(text(700, 192, "щоразу", size=9, color=MUTED, anchor="start"))
    p.append(rect(586, 210, 140, 48, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    p.append(text(656, 234, "виконує рядок", size=11, color=INK, bold=True))
    p.append(text(656, 251, "за рядком", size=9, color=MUTED))
    p.append(text(565, 290, "гнучко, але повільніше й важче", size=10, color=INK, bold=True))
    p.append(text(565, 310, "(на МК — виняток: MicroPython)", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "compiled-vs-interpreted.svg"), W, H, *p,
           title="Мікроконтролери майже завжди обирають перший шлях")


# ── toolchain-pipeline: конвеєр інструментів від тексту до прошивки ────────────
def fig_toolchain_pipeline():
    W, H = 760, 250
    p = []
    y, bh = 96, 76
    stages = [
        ("вихідний\nкод", "текст", "#eef6ef", FIELD),
        ("Препроцесор", "готує текст", BG, INK),
        ("Компілятор", "→ команди", BG, INK),
        ("Асемблер", "→ числа", BG, INK),
        ("Лінкер", "зшиває все", BG, INK),
        ("Образ\nпрошивки", "готово", PAPER, "#a98a2a"),
    ]
    n = len(stages)
    gap = 12
    bw = (W - 48 - gap * (n - 1)) / n
    x = 24
    rights = []
    for i, (lab, sub, fill, col) in enumerate(stages):
        p.append(fitbox(x, y, bw, bh, lab, size=12, fill=fill, stroke=col,
                        sw=(2.2 if i in (0, n - 1) else 1.8), bold=True, color=col, rx=10))
        p.append(text(x + bw / 2, y + bh + 16, sub, size=9, color=MUTED))
        if i > 0:
            p.append(arrow(rights[-1] + 1, y + bh / 2, x - 3, y + bh / 2, color=INK, sw=2.2))
        rights.append(x + bw)
        x += bw + gap

    p.append(text(W / 2, H - 26, "Кожен крок — окремий інструмент зі своєю вузькою роботою; разом вони і є тулчейн",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "toolchain-pipeline.svg"), W, H, *p,
           title="«Скомпілювати» — це не один крок, а кілька злагоджених")


# ── cross-compilation: збираємо на ПК, виконуємо на чипі ───────────────────────
def fig_cross_compilation():
    W, H = 740, 300
    p = []
    # ПК
    p.append(rect(40, 80, 300, 180, fill="none", stroke="#e4e4e4", sw=2, rx=12))
    p.append(text(190, 106, "ПК (ядро x86)", size=13, color=INK, bold=True))
    p.append(rect(80, 130, 220, 64, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    p.append(text(190, 158, "Тулчейн працює тут", size=12, color=NEG, bold=True))
    p.append(text(190, 178, "(компілює, лінкує)", size=10, color=MUTED))
    p.append(text(190, 224, "✗ результат тут не запуститься", size=11, color=POS, bold=True))
    p.append(text(190, 242, "це «чужі» для ПК числа", size=9, color=MUTED))

    # стрілка з прошивкою
    p.append(arrow(344, 170, 420, 170, color=FIELD, sw=3.2))
    p.append(rect(352, 153, 64, 30, fill=PAPER, stroke="#a98a2a", sw=1.6, rx=6))
    p.append(text(384, 173, "прошивка", size=9, color="#7a6312", bold=True))

    # МК
    p.append(rect(420, 80, 300, 180, fill="none", stroke="#e4e4e4", sw=2, rx=12))
    p.append(text(570, 106, "Мікроконтролер", size=13, color=INK, bold=True))
    p.append(text(570, 124, "(Xtensa / RISC-V)", size=10, color=MUTED))
    p.append(rect(460, 144, 220, 64, fill="#eef6ef", stroke=FIELD, sw=2, rx=8))
    p.append(text(570, 172, "Код біжить тут", size=12, color=FIELD, bold=True))
    p.append(text(570, 192, "✓ це його рідні числа", size=10, color=FIELD, bold=True))
    p.append(text(570, 238, "для кожного чипа — своя «ціль» у тулчейні", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "cross-compilation.svg"), W, H, *p,
           title="Машина-будівельник і машина-ціль — різні")


# ── one-line-many: один рядок C → кілька команд → числа ────────────────────────
def fig_one_line_many():
    W, H = 720, 340
    p = []
    # рядок C
    p.append(rect(210, 58, 300, 48, fill=DARK, stroke=INK, sw=1.5, rx=8))
    p.append(text(360, 88, "OUT |= (1 << 2);", size=15, color="#eaf6ee", bold=True))
    p.append(text(522, 86, "← один рядок C", size=11, color=MUTED, anchor="start", italic=True))
    p.append(arrow(360, 108, 360, 134, color=INK, sw=2.4))

    # машинні команди
    p.append(rect(160, 138, 400, 104, fill=DARK, stroke=INK, sw=1.5, rx=8))
    rows = [("load  r1, [OUT]", "; прочитати"),
            ("or    r1, r1, 0x04", "; накласти маску 1<<2"),
            ("store [OUT], r1", "; записати назад")]
    for i, (a, c) in enumerate(rows):
        yy = 170 + i * 30
        p.append(text(180, yy, a, size=13, color=GREENT, anchor="start", bold=True))
        p.append(text(366, yy, c, size=10, color=GREYT, anchor="start"))
    p.append(text(572, 182, "← кілька", size=11, color=MUTED, anchor="start", italic=True))
    p.append(text(572, 200, "  машинних команд", size=11, color=MUTED, anchor="start", italic=True))
    p.append(arrow(360, 244, 360, 270, color=INK, sw=2.4))

    # числа
    p.append(rect(210, 272, 300, 44, fill=DARKMC, stroke="#000000", sw=1.5, rx=8))
    p.append(text(360, 300, "3A 01 ..  2B 01 04  3C 01 ..", size=13, color=GREENT, bold=True))
    p.append(text(522, 298, "← лише числа", size=11, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "one-line-many.svg"), W, H, *p,
           title="Один рядок → кілька машинних команд → числа")


# ════════════════════════ ВСТАВКА «Грейс Гоппер» ════════════════════════

# ── hopper-questions: ланцюг питань від чисел до компілятора ───────────────────
def fig_hopper_questions():
    W, H = 720, 300
    p = []
    steps = [
        ("Людина думає\nяк машина", "числами вручну", "#fdecea", POS),
        ("А чи може машина\nперекладати сама?", "зухвале питання", PAPER, "#a98a2a"),
        ("Машина перекладає\nза людину", "компілятор A-0", "#eef6ef", FIELD),
    ]
    n = len(steps)
    bw, bh = 180, 76
    gap = (W - 60 - n * bw) / (n - 1)
    x = 30
    rights = []
    cy = 130
    for i, (lab, sub, fill, col) in enumerate(steps):
        p.append(fitbox(x, cy, bw, bh, lab, size=12, fill=fill, stroke=col, sw=2.0, bold=True, color=col))
        p.append(text(x + bw / 2, cy + bh + 18, sub, size=10, color=MUTED, italic=True))
        if i > 0:
            p.append(arrow(rights[-1] + 2, cy + bh / 2, x - 4, cy + bh / 2, color=INK, sw=2.2))
        rights.append(x + bw)
        x += bw + gap
    p.append(text(W / 2, 250, "Кожен щабель — нове питання, що штовхало далі", size=12, color=INK, bold=True))
    render(os.path.join(OUT, "hopper-questions.svg"), W, H, *p,
           title="Від «людина думає як машина» до «машина перекладає за людину»")


# ── numbers-vs-human: ручний переклад наміру в стовпець чисел ──────────────────
def fig_numbers_vs_human():
    W, H = 720, 300
    p = []
    # людина бачить намір
    p.append(rect(40, 90, 270, 150, fill="#eef6ef", stroke=FIELD, sw=2, rx=10))
    p.append(text(175, 118, "Як бачить людина", size=12, color=FIELD, bold=True))
    p.append(text(175, 158, "«склади два числа", size=14, color=INK, bold=True))
    p.append(text(175, 182, "й поклади у C»", size=14, color=INK, bold=True))
    p.append(text(175, 218, "ясний намір", size=11, color=MUTED, italic=True))

    # ручний переклад
    cx = W / 2
    p.append(arrow(312, 165, cx - 18, 165, color=POS, sw=2.4))
    p.append(text(cx, 152, "ручний", size=10, color=POS, bold=True))
    p.append(text(cx, 188, "переклад", size=10, color=POS, bold=True))
    p.append(arrow(cx + 18, 165, W - 270 - 40 - 4, 165, color=POS, sw=2.4))

    # машина потребує чисел
    rx = W - 270 - 40
    p.append(rect(rx, 70, 270, 190, fill=DARKMC, stroke="#000000", sw=1.5, rx=10))
    p.append(text(rx + 135, 96, "Як подати машині", size=12, color="#7fa6bf", bold=True))
    for i, s in enumerate(("LOAD  A, [00]", "ADD   A, [01]", "STORE A, [02]")):
        p.append(text(rx + 30, 132 + i * 30, s, size=13, color=GREENT, anchor="start", bold=True))
    p.append(text(rx + 135, 238, "стовпець голих чисел за адресами", size=9, color=MUTED))

    render(os.path.join(OUT, "numbers-vs-human.svg"), W, H, *p,
           title="Праця програміста 1940-х — ручний переклад наміру в числа")


# ── moth-bug: аркуш журналу з метеликом ───────────────────────────────────────
def fig_moth_bug():
    W, H = 700, 300
    p = []
    # аркуш журналу
    px, py, pw, ph = 150, 60, 400, 200
    p.append(rect(px, py, pw, ph, fill="#fbfaf3", stroke="#cdbf8a", sw=2, rx=4))
    p.append(text(px + pw / 2, py + 32, "Робочий журнал — 9 вересня 1947", size=13, color=INK, bold=True))
    # лінії журналу
    for i in range(3):
        ly = py + 56 + i * 22
        p.append(line(px + 24, ly, px + pw - 24, ly, color="#e3dcc2", sw=1))
    # «метелик» — два овали-крила
    mx, my = px + pw / 2, py + 128
    p.append('<ellipse cx="%.1f" cy="%.1f" rx="22" ry="13" fill="#5a4632" stroke="#3a2c1e" stroke-width="1.2"/>' % (mx - 16, my))
    p.append('<ellipse cx="%.1f" cy="%.1f" rx="22" ry="13" fill="#5a4632" stroke="#3a2c1e" stroke-width="1.2"/>' % (mx + 16, my))
    p.append(line(mx, my - 12, mx, my + 12, color="#2a2018", sw=3))
    # скотч
    p.append('<rect x="%.1f" y="%.1f" width="40" height="16" fill="#d9e6f2" opacity="0.7" transform="rotate(-12 %.1f %.1f)"/>' % (mx - 20, my - 26, mx, my - 18))
    p.append(text(px + pw / 2, py + 178, "«First actual case of bug being found»", size=12, color="#5a4632", italic=True, bold=True))

    p.append(text(W / 2, H - 22, "Слово «bug» було й раніше — та саме цей випадок прославив його (і «дебаг»)",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "moth-bug.svg"), W, H, *p,
           title="Перший буквальний «баг»: метелик у реле Mark II")


# ── compiler-idea: переклад перекладається з людини на програму ───────────────
def fig_compiler_idea():
    W, H = 720, 280
    p = []
    # було: людина перекладає
    p.append(text(190, 70, "Було", size=13, color=POS, bold=True))
    p.append(rect(60, 86, 110, 50, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(115, 116, "людина", size=12, color=FIELD, bold=True))
    p.append(arrow(172, 111, 226, 111, color=POS, sw=2.4))
    p.append(text(199, 102, "повільно, з помилками", size=9, color=POS))
    p.append(rect(228, 86, 110, 50, fill=DARKMC, stroke=INK, sw=1.8, rx=8))
    p.append(text(283, 116, "числа", size=12, color=GREENT, bold=True))

    # стало: програма перекладає
    p.append(text(190, 176, "Стало (ідея Гоппер)", size=13, color=FIELD, bold=True))
    p.append(rect(60, 192, 110, 50, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(115, 222, "людина", size=12, color=FIELD, bold=True))
    p.append(arrow(172, 217, 214, 217, color=INK, sw=2.2))
    box, bw, bh = textbox(283, 217, "програма-\nперекладач", size=11, bold=True, fill=PAPER, stroke="#a98a2a", sw=2, color="#7a6312")
    p.append(box)
    p.append(arrow(283 + bw / 2 + 2, 217, 470, 217, color=INK, sw=2.2))
    p.append(rect(472, 192, 110, 50, fill=DARKMC, stroke=INK, sw=1.8, rx=8))
    p.append(text(527, 222, "числа", size=12, color=GREENT, bold=True))
    p.append(text(527, 258, "швидко, точно, щоразу однаково", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "compiler-idea.svg"), W, H, *p,
           title="Зерно компілятора: переклад вкладають у програму")


# ── a0-library: A-0 складає програму з бібліотеки підпрограм ───────────────────
def fig_a0_library():
    W, H = 720, 300
    p = []
    # вхід: послідовність номерів
    p.append(rect(40, 110, 150, 90, fill=DARK, stroke=INK, sw=1.5, rx=8))
    p.append(text(115, 134, "запис задачі", size=11, color="#8fcf9f", bold=True))
    for i, s in enumerate(("№ 7", "№ 3", "№ 7", "№ 12")):
        p.append(text(115, 158 + i * 0, s, size=12, color="#eaf6ee", bold=True)) if False else None
    p.append(text(115, 160, "№7 · №3 · №7 · №12", size=12, color="#eaf6ee", bold=True))
    p.append(text(115, 186, "номери підпрограм", size=9, color="#7a9a86", italic=True))

    # A-0
    box, bw, bh = textbox(330, 155, "A-0", size=18, bold=True, fill=PAPER, stroke="#a98a2a", sw=2.4, color="#7a6312", pad=16)
    p.append(arrow(192, 155, 330 - bw / 2 - 4, 155, color=INK, sw=2.2))
    p.append(box)
    p.append(text(330, 155 + bh / 2 + 16, "складач", size=10, color=MUTED))

    # бібліотека
    p.append(rect(250, 232, 160, 50, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(330, 256, "бібліотека підпрограм", size=10, color=FIELD, bold=True))
    p.append(text(330, 272, "(на стрічці)", size=9, color=MUTED))
    p.append(arrow(330, 232, 330, 155 + bh / 2 + 4, color=FIELD, sw=2.0))
    p.append(text(372, 212, "дістає", size=9, color=FIELD, anchor="start"))

    # вихід: єдина машинна програма
    p.append(arrow(330 + bw / 2 + 2, 155, 520, 155, color=INK, sw=2.2))
    p.append(rect(522, 110, 160, 90, fill=DARKMC, stroke="#000000", sw=1.5, rx=8))
    p.append(text(602, 134, "єдина програма", size=11, color="#7fa6bf", bold=True))
    for i, s in enumerate(("…склеєно", "за адресами", "в один код…")):
        p.append(text(602, 158 + i * 18, s, size=11, color=GREENT, bold=True))

    p.append(text(W / 2, H - 16, "Зародок і компілятора (переклад запису), і лінкера (зшивання шматків)",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "a0-library.svg"), W, H, *p,
           title="A-0: складач машинної програми з бібліотеки")


if __name__ == "__main__":
    # стаття
    fig_two_worlds()
    fig_what_is_compilation()
    fig_compiled_vs_interpreted()
    fig_toolchain_pipeline()
    fig_cross_compilation()
    fig_one_line_many()
    # вставка
    fig_hopper_questions()
    fig_numbers_vs_human()
    fig_moth_bug()
    fig_compiler_idea()
    fig_a0_library()
    print("OK: figures written to", OUT)
