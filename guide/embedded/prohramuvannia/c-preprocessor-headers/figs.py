# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PRE  = "#8a5cc7"   # фіолетовий — препроцесор (текстова фаза)
CC   = POS         # червоний — компілятор
SRC  = NEG         # синій — вихідний код


# ── stage: препроцесор — окрема ТЕКСТОВА фаза перед компілятором ──────────────
# Ідея: до компілятора код проходить через препроцесор, який лише ріже текст.
def fig_stage():
    W, H = 780, 320
    p = []

    # вхідні файли
    b, w, h = textbox(105, 90, "main.c\n#include \"led.h\"\n…код…", size=11,
                      color=SRC, stroke=SRC, fill="#eef2fb", min_w=150)
    p.append(b)
    b, w, h = textbox(105, 195, "led.h\nоголошення", size=11,
                      color=SRC, stroke=SRC, fill="#eef2fb", min_w=150)
    p.append(b)

    # препроцесор
    b, w, h = textbox(360, 142, "ПРЕПРОЦЕСОР\nвставити · замінити\nвирізати", size=12.5,
                      color=PRE, stroke=PRE, fill="#f3edfb", bold=True, min_w=180)
    p.append(b)
    p.append(text(360, 210, "працює з ТЕКСТОМ, не з C", size=11, color=MUTED, italic=True))

    p.append(arrow(182, 96, 268, 130, color=SRC))
    p.append(arrow(182, 190, 268, 158, color=SRC))

    # один суцільний текст
    b, w, h = textbox(620, 142, "один суцільний\nтекст\n(модуль трансляції)", size=11.5,
                      color=INK, stroke=INK, fill=FILL, min_w=170)
    p.append(b)
    p.append(arrow(452, 142, 532, 142, color=PRE))

    # компілятор нижче
    b, w, h = textbox(620, 250, "КОМПІЛЯТОР\nбачить лише це", size=12, color=CC,
                      stroke=CC, fill="#fdecea", bold=True, min_w=170)
    p.append(b)
    p.append(arrow(620, 172, 620, 224, color=INK))

    render(os.path.join(OUT, "stage.svg"), W, H, *p,
           title="Препроцесор ріже текст ДО того, як компілятор побачить код")


# ── include: директива = буквальна вставка вмісту файлу ──────────────────────
# Ідея: #include не «підключає» — він фізично вклеює текст файлу на своє місце.
def fig_include():
    W, H = 780, 300
    p = []

    # ліворуч — як пишемо
    p.append(text(150, 44, "як пишемо (main.c)", size=12.5, color=SRC, bold=True))
    b, w, h = textbox(150, 130, "int add(int, int);", size=11, color=MUTED,
                      stroke="#c9d3e6", fill="#f7f9fd", min_w=250)
    # покажемо рядок #include окремо жирним
    p.append(rect(25, 150, 250, 46, fill="#f3edfb", stroke=PRE, sw=1.6, rx=6))
    p.append(text(150, 172, "#include \"math.h\"", size=12, color=PRE, bold=True))
    p.append(text(150, 189, "  ↑ один рядок", size=9.5, color=MUTED))
    p.append(text(150, 108, "int main(void) { … }", size=11, color=MUTED))

    # праворуч — що бачить компілятор
    p.append(text(620, 44, "що бачить компілятор", size=12.5, color=CC, bold=True))
    p.append(text(620, 108, "int main(void) { … }", size=11, color=MUTED))
    p.append(rect(495, 132, 250, 82, fill="#eef2fb", stroke=SRC, sw=1.6, rx=6))
    p.append(text(620, 152, "int mul(int, int);", size=10.5, color=SRC))
    p.append(text(620, 170, "int div(int, int);", size=10.5, color=SRC))
    p.append(text(620, 188, "#define PI 3.14159", size=10.5, color=SRC))
    p.append(text(620, 206, "← увесь вміст math.h", size=9.5, color=MUTED, italic=True))

    p.append(arrow(285, 173, 485, 173, color=PRE, sw=2.2))
    p.append(text(385, 160, "вклеєно", size=11, color=PRE, bold=True))

    render(os.path.join(OUT, "include.svg"), W, H, *p,
           title="#include — це буквальна вставка тексту файлу")


# ── guard: сторож проти подвійної вставки одного заголовка ───────────────────
# Ідея: прапорець-макрос ставиться при першій вставці; другу вставку сторож ріже.
def fig_guard():
    W, H = 780, 360
    p = []
    p.append(text(W/2, 52, "led.h потрапляє двічі — сторож пропускає лише перший раз",
                  size=12.5, color=INK, bold=True))

    # перша вставка — прохід
    b, w, h = textbox(200, 130, "1-ша вставка", size=12, color=FIELD, stroke=FIELD,
                      fill="#eaf6ee", bold=True, min_w=150)
    p.append(b)
    p.append(text(200, 172, "LED_H не визначено →", size=10.5, color=FIELD))
    p.append(text(200, 188, "заходимо, ставимо LED_H,", size=10.5, color=FIELD))
    p.append(text(200, 204, "тіло заголовка читається", size=10.5, color=FIELD))

    # друга вставка — зріз
    b, w, h = textbox(580, 130, "2-га вставка", size=12, color=POS, stroke=POS,
                      fill="#fdecea", bold=True, min_w=150)
    p.append(b)
    p.append(text(580, 172, "LED_H вже визначено →", size=10.5, color=POS))
    p.append(text(580, 188, "усе між #ifndef і #endif", size=10.5, color=POS))
    p.append(text(580, 204, "пропущено (нічого не читаємо)", size=10.5, color=POS))

    # прапорець посередині
    b, w, h = textbox(W/2, 270, "прапорець LED_H\n(порожній макрос)", size=11.5,
                      color=PRE, stroke=PRE, fill="#f3edfb", bold=True, min_w=180)
    p.append(b)
    p.append(arrow(200, 224, W/2-40, 250, color=FIELD))
    p.append(text(255, 250, "ставить", size=10, color=FIELD, bold=True))
    p.append(arrow(W/2+40, 250, 580, 224, color=POS))
    p.append(text(525, 250, "бачить", size=10, color=POS, bold=True))

    p.append(text(W/2, 320, "без сторожа — оголошення двічі → помилка «redefinition»",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "guard.svg"), W, H, *p)


# ── lineage: макротрадиція Bell Labs → препроцесор C (для вставки-історії) ────
# Ідея: одна безперервна лінія текстової підстановки від 1959 до ~1973.
def fig_lineage():
    W, H = 820, 250
    p = []
    p.append(text(W/2, 40, "Одна лінія: текстова підстановка за шаблоном",
                  size=13, color=INK, bold=True))

    y = 130
    # вісь часу утворюють стрілки між віхами (нижче) — суцільної лінії крізь
    # написи не малюємо, щоб текст лишався поза лініями

    # три віхи
    b, w, h = textbox(150, y, "1959\nмакроси в асемблері SAP\n(Іствуд, Макілрой,\nIBM 704)",
                      size=10.5, color=NEG, stroke=NEG, fill="#eef2fb", min_w=170)
    p.append(b)
    b, w, h = textbox(410, y, "1960-70-ті\nмакроси — мова\nтелефонної комутації\n(два десятиліття)",
                      size=10.5, color=MUTED, stroke=MUTED, fill=FILL, min_w=170)
    p.append(b)
    b, w, h = textbox(670, y, "~1973\nпрепроцесор C\n#include · #define\n(Рітчі, Снайдер)",
                      size=10.5, color=PRE, stroke=PRE, fill="#f3edfb", bold=True, min_w=170)
    p.append(b)

    p.append(arrow(238, y, 322, y, color=MUTED, sw=2))
    p.append(arrow(498, y, 582, y, color=MUTED, sw=2))

    p.append(text(W/2, 210, "суть незмінна: «побачив ім'я — підставив текст»",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "lineage.svg"), W, H, *p,
           title="Родовід препроцесора C: від макросів 1959 року")


# ── phases: вісім фаз трансляції; препроцесор — фази 1–6 (детальна) ───────────
# Ідея: препроцесор не «одна дія», а перші шість фаз стандарту; компілятор і
# лінкувальник — останні дві. Показуємо межу препроцесор / компілятор / лінкер.
def fig_phases():
    W, H = 820, 470
    p = []
    p.append(text(W/2, 34, "Вісім фаз трансляції: де сидить препроцесор",
                  size=16, color=INK, bold=True))

    rows = [
        ("1", "мапа символів · заміна триграфів", PRE),
        ("2", "склейка рядків: «\\» + новий рядок → один рядок", PRE),
        ("3", "розбиття на препроцесорні токени (максимальне «відкушування»)", PRE),
        ("4", "директиви й розгортання макросів · #include тягне файл крізь 1–4", PRE),
        ("5", "escape-послідовності в літералах перетворено", PRE),
        ("6", "сусідні рядкові літерали склеєно", PRE),
        ("7", "КОМПІЛЯТОР: токени → синтаксис → код", CC),
        ("8", "ЛІНКУВАЛЬНИК: зовнішні посилання з'єднано", CC),
    ]
    x0, y0, rw, rh, gap = 70, 60, 680, 40, 8
    for i, (n, label, col) in enumerate(rows):
        y = y0 + i * (rh + gap)
        fill = "#f3edfb" if col == PRE else "#fdecea"
        p.append(rect(x0, y, rw, rh, fill=fill, stroke=col, sw=1.4, rx=6))
        p.append(circle(x0 + 22, y + rh/2, 13, fill=BG, stroke=col, sw=1.8))
        p.append(text(x0 + 22, y + rh/2 + 5, n, size=13, color=col, bold=True))
        p.append(text(x0 + 46, y + rh/2 + 5, label, size=11.5, color=INK, anchor="start"))

    # дужка «препроцесор» уздовж фаз 1–6
    ppr_top = y0
    ppr_bot = y0 + 6 * (rh + gap) - gap
    bx = x0 + rw + 16
    p.append(line(bx, ppr_top, bx, ppr_bot, color=PRE, sw=2.5))
    p.append(line(bx, ppr_top, bx - 8, ppr_top, color=PRE, sw=2.5))
    p.append(line(bx, ppr_bot, bx - 8, ppr_bot, color=PRE, sw=2.5))
    p.append(text(bx + 8, (ppr_top + ppr_bot)/2 - 8, "ПРЕ-", size=12, color=PRE, bold=True, anchor="start"))
    p.append(text(bx + 8, (ppr_top + ppr_bot)/2 + 8, "ПРОЦЕСОР", size=12, color=PRE, bold=True, anchor="start"))

    render(os.path.join(OUT, "phases.svg"), W, H, *p,
           title=None)


# ── expand: механіка розгортання макроса (preexpand → підстановка → фарба → rescan)
# Ідея: аргументи розгортаються ДО підстановки; ім'я, що розгортається, «фарбується»
# й повторно не чіпається; результат пересканюється на нові макроси.
def fig_expand():
    W, H = 820, 430
    p = []
    p.append(text(W/2, 34, "Як препроцесор розгортає виклик макроса",
                  size=16, color=INK, bold=True))

    # 4 кроки згори вниз
    steps = [
        ("1. беремо виклик", "F(G(2))", NEG, "#eef2fb"),
        ("2. АРГУМЕНТ розгортаємо перший", "G(2) → 20 + 2", "#8a5cc7", "#f3edfb"),
        ("3. підставляємо в тіло F", "F(x)=((x)+1) → ((20 + 2)+1)", "#8a5cc7", "#f3edfb"),
        ("4. пересканюємо результат", "жодного макроса → ((20 + 2)+1)", FIELD, "#eaf6ee"),
    ]
    x0, y0, bw, bh, gap = 130, 66, 560, 66, 20
    for i, (cap, body, col, fill) in enumerate(steps):
        y = y0 + i * (bh + gap)
        p.append(rect(x0, y, bw, bh, fill=fill, stroke=col, sw=1.6, rx=8))
        p.append(text(x0 + 16, y + 24, cap, size=12, color=col, anchor="start", bold=True))
        p.append(text(x0 + 16, y + 48, body, size=13, color=INK, anchor="start"))
        if i < len(steps) - 1:
            p.append(arrow(x0 + bw/2, y + bh, x0 + bw/2, y + bh + gap, color=MUTED, sw=2))

    # виноска про «синю фарбу» справа
    note = ("«синя фарба»:\nпоки ім'я F\nрозгортається,\nповторне F\nусередині —\nне чіпається\n(нема нескінченної\nрекурсії)")
    b, w, h = textbox(W - 92, 200, note, size=10.5, color=POS, stroke=POS,
                      fill="#fdecea", min_w=150)
    p.append(b)

    render(os.path.join(OUT, "expand.svg"), W, H, *p, title=None)


# ── xmacro: один список-джерело → три узгоджені форми через різні X (proj) ────
# Ідея: єдиний CMD_TABLE(X) тричі проходить крізь різні визначення X і породжує
# enum, масив назв і таблицю обробників. Додав рядок у список — оновилося все.
def fig_xmacro():
    W, H = 860, 470
    p = []
    p.append(text(W/2, 34, "Один список — три узгоджені форми",
                  size=16, color=INK, bold=True))

    # ── джерело ліворуч ──────────────────────────────────────────────────────
    src = ("CMD_TABLE(X)\n"
           "  X(0x01, PING,   …)\n"
           "  X(0x02, ARM,    …)\n"
           "  X(0x03, DISARM, …)")
    b, w, h = textbox(150, 235, src, size=11, color=PRE, stroke=PRE,
                      fill="#f3edfb", bold=False, min_w=210)
    p.append(b)
    p.append(text(150, 150, "єдине джерело", size=12, color=PRE, bold=True))
    p.append(text(150, 320, "додав рядок — оновило все", size=10, color=MUTED, italic=True))

    # ── три визначення X (середня колонка) ───────────────────────────────────
    defs = [
        (120, "#define X … CMD_##id = code", NEG, "#eef2fb"),
        (235, "#define X … [CMD_##id] = name", FIELD, "#eaf6ee"),
        (350, "#define X … [CMD_##id] = handler", POS, "#fdecea"),
    ]
    xd = 505
    for cy, label, col, fill in defs:
        p.append(fitbox(xd - 150, cy - 22, 300, 44, label, size=11,
                        color=col, stroke=col, fill=fill, sw=1.5))
        # стрілка від джерела до визначення (входить у ліву грань рамки)
        p.append(arrow(262, 235, xd - 152, cy, color=PRE, sw=1.6))

    # ── три результати праворуч ──────────────────────────────────────────────
    res = [
        (120, "enum:\nCMD_PING=0x01,\nCMD_ARM=0x02, …", NEG, "#eef2fb"),
        (235, "назви:\n[CMD_PING]=\"PING\",\n…", FIELD, "#eaf6ee"),
        (350, "обробники:\n[CMD_PING]=handle_ping,\n…", POS, "#fdecea"),
    ]
    xr = 762
    for cy, body, col, fill in res:
        b, w, h = textbox(xr, cy, body, size=10, color=INK, stroke=col,
                          fill=fill, min_w=180)
        p.append(b)
        p.append(arrow(xd + 152, cy, xr - 92, cy, color=col, sw=1.8))

    render(os.path.join(OUT, "xmacro.svg"), W, H, *p, title=None)


if __name__ == "__main__":
    fig_stage()
    fig_include()
    fig_guard()
    fig_lineage()
    fig_phases()
    fig_expand()
    fig_xmacro()
    print("figs done")
