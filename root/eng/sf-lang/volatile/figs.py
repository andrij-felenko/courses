# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8860b"   # акцент «увага» (мінливе значення, подія)
MONO = "Consolas, 'DejaVu Sans Mono', monospace"


def code_line(x, y, s, size=14, color="#e8e8e8", anchor="start", bold=True):
    """Рядок моноширинного коду на темному тлі."""
    w = ' font-weight="700"' if bold else ''
    a = ' text-anchor="%s"' % anchor
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s"%s%s>%s</text>'
            % (x, y, MONO, size, color, a, w, esc(s)))


# ── cached-in-register: цикл звіряється зі старою копією в регістрі ────────────
# Ідея: ISR пише flag=true в ПАМ'ЯТЬ; цикл читав flag раз, тримає копію в РЕГІСТРІ
# й крутить її — у пам'ять більше не зазирає, тож запис ISR для нього невидимий.

def fig_cached_in_register():
    W, H = 760, 340
    p = []
    # пам'ять
    p.append(rect(60, 80, 250, 110, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    p.append(text(185, 104, "ПАМ'ЯТЬ", size=12, color=FIELD, bold=True))
    p.append(rect(110, 122, 150, 44, fill=BG, stroke=FIELD, sw=1.6, rx=6))
    p.append(text(185, 142, "flag = true", size=12, color=INK, bold=True))
    p.append(text(185, 158, "(свіже значення)", size=9.5, color=MUTED))

    # регістр
    p.append(rect(450, 80, 250, 110, fill="#fdecea", stroke=POS, sw=2, rx=10))
    p.append(text(575, 104, "РЕГІСТР процесора", size=12, color=POS, bold=True))
    p.append(rect(500, 122, 150, 44, fill=BG, stroke=POS, sw=1.6, rx=6))
    p.append(text(575, 142, "flag = false", size=12, color=INK, bold=True))
    p.append(text(575, 158, "(застаріла копія)", size=9.5, color=POS))

    # ISR пише в пам'ять
    p.append(arrow(185, 250, 185, 192, color=FIELD, sw=2.4))
    p.append(text(185, 272, "обробник (ISR) записав", size=10.5, color=FIELD, bold=True))
    p.append(text(185, 288, "flag = true у пам'ять", size=10, color=INK))

    # цикл читає регістр
    p.append(arrow(575, 250, 575, 192, color=POS, sw=2.4))
    p.append(text(575, 272, "цикл while(!flag) звіряє", size=10.5, color=POS, bold=True))
    p.append(text(575, 288, "лише регістр → крутиться вічно", size=10, color=INK))

    # розрив між ними
    p.append(line(330, 135, 430, 135, color=MUTED, sw=2, dash="6 5"))
    p.append(text(380, 124, "не зазирає", size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "cached-in-register.svg"), W, H, *p,
           title="Без volatile цикл звіряється зі старою копією в регістрі")


# ── volatile-fix: з volatile кожна перевірка читає свіже з пам'яті ─────────────
def fig_volatile_fix():
    W, H = 760, 300
    p = []
    # пам'ять
    p.append(rect(255, 80, 250, 96, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    p.append(text(380, 104, "ПАМ'ЯТЬ", size=12, color=FIELD, bold=True))
    p.append(rect(305, 120, 150, 40, fill=BG, stroke=FIELD, sw=1.6, rx=6))
    p.append(text(380, 145, "flag = true", size=12, color=INK, bold=True))

    # ISR пише
    p.append(arrow(150, 128, 253, 128, color=FIELD, sw=2.4))
    p.append(text(95, 116, "ISR пише", size=10.5, color=FIELD, anchor="middle", bold=True))
    p.append(text(95, 140, "flag=true", size=10, color=INK, anchor="middle"))

    # цикл читає з пам'яті щоразу
    p.append(arrow(610, 128, 507, 128, color=NEG, sw=2.4))
    p.append(text(665, 116, "цикл читає", size=10.5, color=NEG, anchor="middle", bold=True))
    p.append(text(665, 140, "щоразу", size=10, color=INK, anchor="middle"))

    p.append(text(W / 2, 226, "volatile bool flag;  →  кожна перевірка !flag іде в пам'ять",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 256, "цикл бачить запис обробника й коректно виходить",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "volatile-fix.svg"), W, H, *p,
           title="З volatile кожна перевірка читає свіже значення з пам'яті")


# ── what-compiler-does: три типові оптимізації читань ──────────────────────────
def fig_what_compiler_does():
    W, H = 760, 320
    p = []
    cards = [
        (40, "У регістр", "часту змінну тримати\nв регістрі, не бігати\nщоразу в пам'ять"),
        (270, "Прибрати читання", "якщо між читаннями\nніхто не писав —\nнавіщо читати двічі?"),
        (500, "Переставити", "змінити порядок\nдоступів до пам'яті\nзадля швидкості"),
    ]
    for x, head, body in cards:
        p.append(rect(x, 70, 220, 130, fill=FILL, stroke=NEG, sw=1.8, rx=10))
        p.append(text(x + 110, 98, head, size=12.5, color=NEG, bold=True))
        for i, ln in enumerate(body.split("\n")):
            p.append(text(x + 110, 126 + i * 18, ln, size=10, color=INK))

    p.append(text(W / 2, 244, "Для звичайного коду це КОРЕКТНО — якщо змінну міняє лише видимий код.",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 272, "Обробник міняє її «за спиною» оптимізатора — і тут потрібен volatile.",
                  size=10.5, color=POS, italic=True))

    render(os.path.join(OUT, "what-compiler-does.svg"), W, H, *p,
           title="Три оптимізації читань: кешувати, прибирати, переставляти")


# ── when-to-use: кому потрібен volatile, а кому ні ─────────────────────────────
def fig_when_to_use():
    W, H = 760, 320
    p = []
    need = [
        "прапорець, що його ставить ISR",
        "лічильник подій із обробника",
        "індекс / буфер, спільний з ISR",
        "апаратний регістр периферії",
    ]
    no = [
        "локальна змінна функції",
        "тимчасове значення в обчисленні",
        "константа",
        "усе, чого обробник не чіпає",
    ]
    p.append(rect(40, 70, 330, 210, fill="#f3faf4", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(205, 98, "ПОТРІБЕН volatile", size=13, color=FIELD, bold=True))
    for i, s in enumerate(need):
        yy = 134 + i * 32
        p.append(text(62, yy, "✓", size=13, color=FIELD, anchor="start", bold=True))
        p.append(text(86, yy, s, size=10.5, color=INK, anchor="start"))

    p.append(rect(390, 70, 330, 210, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    p.append(text(555, 98, "НЕ ПОТРІБЕН", size=13, color=POS, bold=True))
    for i, s in enumerate(no):
        yy = 134 + i * 32
        p.append(text(412, yy, "✗", size=13, color=POS, anchor="start", bold=True))
        p.append(text(436, yy, s, size=10.5, color=INK, anchor="start"))

    p.append(text(W / 2, 304, "Позначають не «про всяк випадок», а лише там, де змінну міняють поза видимим кодом",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "when-to-use.svg"), W, H, *p,
           title="Спільні з ISR змінні потребують volatile; локальні — ні")


# ── not-atomic: volatile дає свіжість, але не неподільність ────────────────────
# Ідея: 64-бітне читання = дві операції (старша/молодша половина); ISR влітає МІЖ
# ними й міняє значення — основний код склеює стару половину з новою (розрив).

def fig_not_atomic():
    W, H = 760, 340
    p = []
    # вісь часу основного коду
    p.append(line(80, 150, 680, 150, color=INK, sw=2))
    p.append(text(80, 134, "основний код читає 64-бітну змінну:", size=10.5, color=INK, anchor="start", bold=True))

    # дві половини читання
    p.append(rect(150, 132, 150, 36, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(225, 154, "читає старшу", size=10.5, color=NEG, bold=True))
    p.append(rect(470, 132, 150, 36, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(545, 154, "читає молодшу", size=10.5, color=NEG, bold=True))

    # ISR влітає між половинами
    p.append(line(385, 96, 385, 204, color=POS, sw=2, dash="5 4"))
    p.append(rect(310, 210, 150, 36, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    p.append(text(385, 232, "ISR міняє все значення", size=10, color=POS, bold=True))
    p.append(arrow(385, 210, 385, 170, color=POS, sw=2))
    p.append(text(385, 90, "обробник влітає ТУТ", size=10, color=POS, anchor="middle", bold=True))

    # результат — розрив
    p.append(rect(210, 278, 340, 40, fill=FILL, stroke=GOLD, sw=2, rx=8))
    p.append(text(380, 296, "склеєно: стара половина + нова половина", size=10.5, color=INK, bold=True))
    p.append(text(380, 312, "= число, якого не існувало (розрив, tearing)", size=10, color=GOLD, bold=True))

    p.append(text(W / 2, 56, "volatile зробив кожну половину свіжою — але не зробив читання неподільним",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "not-atomic.svg"), W, H, *p,
           title="volatile дає свіжість, та не неподільність: багатобайтне читання можна перервати")


# ── before-after: той самий код у двох версіях ────────────────────────────────
def fig_before_after():
    W, H = 760, 340
    p = []
    # ліворуч — без volatile (зависає)
    p.append(rect(40, 70, 330, 210, fill="#0f1115", stroke=POS, sw=2, rx=10))
    p.append(text(205, 96, "без volatile — зависає", size=12, color="#ff8a80", bold=True))
    left = [
        "bool flag = false;",
        "void IRAM_ATTR isr(){",
        "  flag = true;",
        "}",
        "while (!flag) { }",
    ]
    for i, ln in enumerate(left):
        p.append(code_line(60, 128 + i * 26, ln, size=13.5))
    p.append(text(205, 268, "цикл вічний  ✗", size=12, color="#ff8a80", bold=True))

    # праворуч — з volatile (працює)
    p.append(rect(390, 70, 330, 210, fill="#0f1115", stroke=FIELD, sw=2, rx=10))
    p.append(text(555, 96, "з volatile — працює", size=12, color="#9be7b4", bold=True))
    right = [
        "volatile bool flag = false;",
        "void IRAM_ATTR isr(){",
        "  flag = true;",
        "}",
        "while (!flag) { }",
    ]
    for i, ln in enumerate(right):
        col = "#ffd479" if i == 0 else "#e8e8e8"
        p.append(code_line(410, 128 + i * 26, ln, size=12.5, color=col))
    p.append(text(555, 268, "виходить по події  ✓", size=12, color="#9be7b4", bold=True))

    p.append(text(W / 2, 308, "Різниця — одне слово volatile перед типом",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "before-after.svg"), W, H, *p,
           title="Одне слово volatile перетворює зависання на робочий код")


# ══ Фігури вставки proj-volatile-asm ══════════════════════════════════════════

# ── asm-contrast: де стоїть load — над циклом чи всередині ─────────────────────
def fig_asm_contrast():
    W, H = 760, 360
    p = []
    # без volatile — load над циклом
    p.append(rect(40, 70, 330, 250, fill="#0f1115", stroke=POS, sw=2, rx=10))
    p.append(text(205, 96, "без volatile", size=12.5, color="#ff8a80", bold=True))
    a = [
        ("  load r1, [flag]", "#ffd479", "читаємо ОДИН раз"),
        ("loop:", "#e8e8e8", ""),
        ("  test r1", "#e8e8e8", "перевіряє РЕГІСТР"),
        ("  beq  loop", "#e8e8e8", "→ вічний цикл"),
    ]
    for i, (ln, col, note) in enumerate(a):
        y = 132 + i * 30
        p.append(code_line(58, y, ln, size=13, color=col))
        if note:
            p.append(text(352, y, note, size=9, color=MUTED, anchor="end", italic=True))
    p.append(text(205, 300, "load НАД циклом → запис ISR невидимий",
                  size=9.6, color="#ff8a80", bold=True))

    # з volatile — load усередині
    p.append(rect(390, 70, 330, 250, fill="#0f1115", stroke=FIELD, sw=2, rx=10))
    p.append(text(555, 96, "з volatile", size=12.5, color="#9be7b4", bold=True))
    b = [
        ("loop:", "#e8e8e8", ""),
        ("  load r1, [flag]", "#ffd479", "читаємо ЩОРАЗУ"),
        ("  test r1", "#e8e8e8", "з пам'яті"),
        ("  beq  loop", "#e8e8e8", "→ побачить і вийде"),
    ]
    for i, (ln, col, note) in enumerate(b):
        y = 132 + i * 30
        p.append(code_line(408, y, ln, size=13, color=col))
        if note:
            p.append(text(702, y, note, size=9, color=MUTED, anchor="end", italic=True))
    p.append(text(555, 300, "load У циклі → зміну від ISR видно",
                  size=9.6, color="#9be7b4", bold=True))

    render(os.path.join(OUT, "asm-contrast.svg"), W, H, *p,
           title="Та сама програма: load над циклом проти load усередині")


# ── what-volatile: що робить і чого не робить ─────────────────────────────────
def fig_what_volatile():
    W, H = 760, 300
    p = []
    does = [
        "перечитувати з пам'яті щоразу",
        "не кешувати в регістрі",
        "не переставляти volatile-доступи",
    ]
    doesnt = [
        "не дає атомарності (рване значення)",
        "не ставить бар'єр між ядрами",
        "не замінює критичну секцію",
    ]
    p.append(rect(40, 70, 330, 170, fill="#f3faf4", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(205, 98, "РОБИТЬ", size=13, color=FIELD, bold=True))
    for i, s in enumerate(does):
        yy = 132 + i * 30
        p.append(text(62, yy, "✓", size=13, color=FIELD, anchor="start", bold=True))
        p.append(text(86, yy, s, size=10, color=INK, anchor="start"))

    p.append(rect(390, 70, 330, 170, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    p.append(text(555, 98, "НЕ РОБИТЬ", size=13, color=POS, bold=True))
    for i, s in enumerate(doesnt):
        yy = 132 + i * 30
        p.append(text(412, yy, "✗", size=13, color=POS, anchor="start", bold=True))
        p.append(text(436, yy, s, size=10, color=INK, anchor="start"))

    p.append(text(W / 2, 268, "volatile = «перечитуй», а не «зроби неподільним»",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "what-volatile.svg"), W, H, *p,
           title="volatile: що робить і чого не робить")


if __name__ == "__main__":
    fig_cached_in_register()
    fig_volatile_fix()
    fig_what_compiler_does()
    fig_when_to_use()
    fig_not_atomic()
    fig_before_after()
    fig_asm_contrast()
    fig_what_volatile()
    print("OK: figures written to", OUT)
