# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "Consolas, 'DejaVu Sans Mono', monospace"
GOLD = "#b8860b"


def code_line(x, y, s, size=13, color="#e8e8e8", anchor="start", bold=True):
    w = ' font-weight="700"' if bold else ''
    a = ' text-anchor="%s"' % anchor
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s"%s%s>%s</text>'
            % (x, y, MONO, size, color, a, w, esc(s)))


# ── inline: виклик проти вбудованого тіла ─────────────────────────────────────
def fig_inline():
    W, H = 760, 320
    p = []
    # ліворуч — звичайний виклик (ритуал)
    p.append(rect(40, 66, 330, 226, fill=FILL, stroke=POS, sw=2, rx=10))
    p.append(text(205, 92, "виклик функції", size=13, color=POS, bold=True))
    steps = [
        "кладе аргумент",
        "запам'ятовує адресу",
        "стрибає у функцію",
        "виконує корисну дію",
        "повертається назад",
    ]
    for i, s in enumerate(steps):
        yy = 122 + i * 30
        col = FIELD if i == 3 else INK
        mark = "•" if i != 3 else "★"
        p.append(text(64, yy, mark, size=12, color=col, anchor="start", bold=True))
        p.append(text(86, yy, s, size=11, color=col, anchor="start", bold=(i == 3)))
    p.append(text(205, 282, "самої дії — 1 крок із 5", size=10, color=MUTED, italic=True))

    # праворуч — вбудовано
    p.append(rect(390, 66, 330, 226, fill=FILL, stroke=FIELD, sw=2, rx=10))
    p.append(text(555, 92, "вбудовано (inline)", size=13, color=FIELD, bold=True))
    p.append(rect(430, 150, 250, 56, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(555, 174, "корисна дія", size=13, color=FIELD, bold=True))
    p.append(text(555, 194, "прямо на місці виклику", size=10, color=INK))
    p.append(text(555, 250, "жодного стрибка —", size=11, color=INK, bold=True))
    p.append(text(555, 268, "сама лише робота", size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "inline.svg"), W, H, *p,
           title="Вбудовування прибирає ритуал виклику")


# ── monomorphization: один зразок → конкретні версії ──────────────────────────
def fig_monomorphization():
    W, H = 760, 330
    p = []
    # зразок згори
    p.append(rect(255, 62, 250, 60, fill="#0f1115", stroke=NEG, sw=2, rx=10))
    p.append(code_line(380, 88, "template<typename T>", size=12, color="#ffd479", anchor="middle"))
    p.append(code_line(380, 108, "T maxof(T a, T b)", size=13, color="#e8e8e8", anchor="middle"))
    p.append(text(380, 140, "один зразок — ще не код", size=10.5, color=MUTED, italic=True))

    # три конкретні версії
    versions = [
        (70, "maxof<int>", "цілочисельне >"),
        (285, "maxof<float>", "порівняння з комою"),
        (500, "maxof<uint8_t>", "байтове >"),
    ]
    for x, head, note in versions:
        p.append(arrow(380, 150, x + 95, 196, color=INK, sw=1.8))
        p.append(rect(x, 200, 190, 78, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
        p.append(code_line(x + 95, 228, head, size=12.5, color="#1a1a1a", anchor="middle"))
        p.append(text(x + 95, 250, note, size=10, color=INK, anchor="middle"))
        p.append(text(x + 95, 268, "тип зашитий", size=9.5, color=FIELD, anchor="middle", bold=True))

    p.append(text(W / 2, 302, "компілятор штампує окрему версію під кожен ужитий тип — жодних перевірок під час виконання",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "monomorphization.svg"), W, H, *p,
           title="Мономорфізація: зразок → конкретні версії на етапі компіляції")


# ── static-vs-dynamic: пряме розв'язання проти таблиці методів ────────────────
def fig_static_vs_dynamic():
    W, H = 760, 330
    p = []
    # ліворуч — статичне
    p.append(rect(40, 66, 330, 232, fill="#f3faf4", stroke=FIELD, sw=2, rx=10))
    p.append(text(205, 92, "шаблон / inline", size=13, color=FIELD, bold=True))
    p.append(text(205, 112, "(рішення на компіляції)", size=10, color=MUTED, italic=True))
    p.append(rect(90, 132, 230, 40, fill=BG, stroke=FIELD, sw=1.6, rx=6))
    p.append(text(205, 157, "тип відомий наперед", size=11, color=INK, bold=True))
    p.append(arrow(205, 176, 205, 208, color=FIELD, sw=2.4))
    p.append(rect(90, 214, 230, 44, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(205, 234, "прямий вбудований код", size=11, color=INK, bold=True))
    p.append(text(205, 251, "без накладних", size=10, color=FIELD))
    p.append(text(205, 284, "нуль витрат", size=11, color=FIELD, bold=True))

    # праворуч — динамічне
    p.append(rect(390, 66, 330, 232, fill="#fdecea", stroke=POS, sw=2, rx=10))
    p.append(text(555, 92, "віртуальний виклик", size=13, color=POS, bold=True))
    p.append(text(555, 112, "(рішення на виконанні)", size=10, color=MUTED, italic=True))
    p.append(rect(440, 132, 230, 40, fill=BG, stroke=POS, sw=1.6, rx=6))
    p.append(text(555, 157, "тип відомий лише в рантаймі", size=10, color=INK, bold=True))
    p.append(arrow(555, 176, 555, 208, color=POS, sw=2.4))
    p.append(rect(440, 214, 230, 44, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    p.append(text(555, 234, "читає адресу з таблиці", size=10.5, color=INK, bold=True))
    p.append(text(555, 251, "→ непрямий стрибок", size=10, color=POS))
    p.append(text(555, 284, "платиш щоразу", size=11, color=POS, bold=True))

    render(os.path.join(OUT, "static-vs-dynamic.svg"), W, H, *p,
           title="Рішення на компіляції безкоштовне; рішення на виконанні коштує")


# ── same-machine-code: дві версії сходяться до однієї інструкції ──────────────
def fig_same_machine_code():
    W, H = 760, 350
    p = []
    # два входи
    p.append(rect(40, 66, 300, 64, fill="#0f1115", stroke=MUTED, sw=1.8, rx=10))
    p.append(text(190, 88, "голі біти", size=11, color="#bbbbbb", bold=True))
    p.append(code_line(190, 112, "GPIO.OUT_SET = 1u<<5", size=12, color="#e8e8e8", anchor="middle"))

    p.append(rect(420, 66, 300, 64, fill="#0f1115", stroke=NEG, sw=1.8, rx=10))
    p.append(text(570, 88, "клас-обгортка", size=11, color="#9fb0ff", bold=True))
    p.append(code_line(570, 112, "Pin<5>::high()", size=12, color="#ffd479", anchor="middle"))

    # три перетворення (тільки для правого)
    p.append(arrow(570, 132, 570, 162, color=INK, sw=1.8))
    passes = "мономорфізація  •  вбудовування  •  згортання константи"
    p.append(rect(360, 166, 360, 40, fill=FILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(540, 190, passes, size=9.5, color=INK, bold=True))

    # обидва сходяться донизу
    p.append(arrow(190, 132, 380, 234, color=INK, sw=1.8))
    p.append(arrow(570, 208, 380, 234, color=INK, sw=1.8))

    # результат — одна інструкція
    p.append(rect(200, 238, 360, 58, fill="#eafaf0", stroke=FIELD, sw=2.2, rx=10))
    p.append(code_line(380, 266, "GPIO.OUT_SET = 0x20", size=15, color="#1a1a1a", anchor="middle"))
    p.append(text(380, 286, "одна інструкція — байт у байт та сама", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, 328, "читабельність дісталася безкоштовно: абстракція розчинилась дощенту",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "same-machine-code.svg"), W, H, *p,
           title="Дві версії → одна інструкція після оптимізації")


# ── asm-o0-vs-o2: реальний асемблер тієї самої обгортки під -O0 і -O2 ──────────
def fig_asm_o0_vs_o2():
    W, H = 780, 384
    p = []
    # спільне джерело згори
    p.append(rect(250, 44, 280, 44, fill="#0f1115", stroke=NEG, sw=1.8, rx=8))
    p.append(code_line(390, 64, "Pin<5>::high();", size=13, color="#ffd479", anchor="middle"))
    p.append(text(390, 82, "той самий рядок C++", size=9.5, color="#bbbbbb", anchor="middle"))
    p.append(arrow(320, 90, 200, 120, color=INK, sw=1.6))
    p.append(arrow(460, 90, 585, 120, color=INK, sw=1.6))

    # ліворуч — -O0
    p.append(rect(30, 122, 340, 232, fill="#fdecea", stroke=POS, sw=2, rx=10))
    p.append(text(200, 146, "-O0  (debug)", size=13, color=POS, bold=True))
    o0 = [
        "push  {r7, lr}      ; пролог кадру",
        "add   r7, sp, #0",
        "bl    Pin<5>::high  ; РЕАЛЬНИЙ виклик",
        " ...                ; тіло high():",
        " ldr  r3, [pc,#..]  ; адреса GPIO",
        " movs r2, #32       ; 1<<5 = 0x20",
        " str  r2, [r3,#..]  ; запис",
        " bx   lr            ; повернення",
        "pop   {r7, pc}      ; епілог",
    ]
    for i, s in enumerate(o0):
        p.append(code_line(46, 172 + i * 19, s, size=10, color="#7a1f16", anchor="start", bold=False))
    p.append(text(200, 344, "виклик + кадр + тіло — багато тактів", size=9.5, color=POS, italic=True))

    # праворуч — -O2
    p.append(rect(410, 122, 340, 232, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    p.append(text(580, 146, "-O2  (release)", size=13, color=FIELD, bold=True))
    o2 = [
        "ldr  r3, [pc, #..]  ; адреса GPIO",
        "movs r2, #32        ; 0x20 (згорнуто)",
        "str  r2, [r3, #..]  ; єдиний запис",
    ]
    for i, s in enumerate(o2):
        p.append(code_line(426, 210 + i * 22, s, size=11, color="#155f38", anchor="start", bold=(i == 2)))
    p.append(rect(430, 286, 300, 34, fill=BG, stroke=FIELD, sw=1.4, rx=6))
    p.append(text(580, 307, "виклик, кадр, обгортка — зникли", size=10, color=FIELD, bold=True))
    p.append(text(580, 344, "лишилась гола корисна інструкція", size=9.5, color=FIELD, italic=True))

    render(os.path.join(OUT, "asm-o0-vs-o2.svg"), W, H, *p,
           title="Той самий рядок: -O0 тримає виклик, -O2 лишає одну інструкцію")


# ── bloat-tradeoff: мономорфізація множить копії у Flash ───────────────────────
def fig_bloat_tradeoff():
    W, H = 780, 360
    p = []
    # ліворуч — мономорфізація: багато копій
    p.append(rect(30, 60, 340, 268, fill=FILL, stroke=NEG, sw=2, rx=10))
    p.append(text(200, 84, "шаблон × багато типів", size=13, color=NEG, bold=True))
    p.append(text(200, 103, "(мономорфізація)", size=10, color=MUTED, italic=True))
    copies = ["sort<int>", "sort<float>", "sort<uint8_t>",
              "sort<Sample>", "sort<int16_t>", "sort<Point>"]
    for i, c in enumerate(copies):
        col = i % 2
        row = i // 2
        x = 52 + col * 155
        y = 128 + row * 46
        p.append(rect(x, y, 138, 36, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=6))
        p.append(code_line(x + 69, y + 23, c, size=11, color="#16307a", anchor="middle"))
    p.append(text(200, 300, "кожна — окремий машинний код у Flash", size=9.5, color=NEG, italic=True))
    p.append(text(200, 318, "швидко, але роздуває образ", size=10, color=POS, bold=True))

    # праворуч — одна спільна функція
    p.append(rect(410, 60, 340, 268, fill=FILL, stroke=FIELD, sw=2, rx=10))
    p.append(text(580, 84, "одна спільна функція", size=13, color=FIELD, bold=True))
    p.append(text(580, 103, "(тип за покажчиком/розміром)", size=10, color=MUTED, italic=True))
    p.append(rect(470, 150, 220, 70, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    p.append(code_line(580, 180, "sort(void*, n, size,", size=11, color="#155f38", anchor="middle"))
    p.append(code_line(580, 200, "         cmp_fn)", size=11, color="#155f38", anchor="middle"))
    p.append(text(580, 258, "один код на всі типи —", size=10, color=FIELD, bold=True))
    p.append(text(580, 276, "малий образ", size=10, color=FIELD, bold=True))
    p.append(text(580, 302, "але непрямий виклик cmp_fn", size=9.5, color=POS, italic=True))
    p.append(text(580, 318, "щоразу — плата в рантаймі", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "bloat-tradeoff.svg"), W, H, *p,
           title="Компроміс: багато швидких копій ⇄ один малий, але непрямий код")


if __name__ == "__main__":
    fig_inline()
    fig_monomorphization()
    fig_static_vs_dynamic()
    fig_same_machine_code()
    fig_asm_o0_vs_o2()
    fig_bloat_tradeoff()
    print("OK: figures written to", OUT)
