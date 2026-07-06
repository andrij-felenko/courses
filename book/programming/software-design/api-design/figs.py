# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. API — шов між «моїм» і «чужим»: видиме тримає обіцянку, приховане вільне ──
def fig_seam():
    W, H = 820, 400
    p = []
    p.append(text(W / 2, 30, "API — це шов: видиме публічне тримає обіцянку, приховане вільне", size=15, bold=True))

    # ліва половина — те, що НАЗОВНІ (API)
    p.append(rect(60, 70, 300, 250, fill="#eaf6ef", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(210, 98, "видиме назовні (API)", size=13, color=FIELD, bold=True))
    p.append(text(210, 118, "обіцянка тим, хто викликає", size=10.5, color=MUTED, italic=True))
    for i, s in enumerate(["open(path) -> Handle",
                           "read(Handle, buf, n)",
                           "close(Handle)"]):
        p.append(rect(80, 140 + i * 46, 260, 36, fill=BG, stroke=FIELD, sw=1.3, rx=6))
        p.append(text(210, 163 + i * 46, s, size=12, color=INK))
    p.append(text(210, 300, "мінятимеш — ламаєш чужий код", size=10.5, color=POS, bold=True))

    # права половина — те, що ПРИХОВАНЕ (реалізація)
    p.append(rect(460, 70, 300, 250, fill=FILL, stroke=MUTED, sw=1.6, rx=10, ))
    p.append(text(610, 98, "приховане (реалізація)", size=13, color=INK, bold=True))
    p.append(text(610, 118, "твоя приватна свобода", size=10.5, color=MUTED, italic=True))
    for i, s in enumerate(["буфер, кеш, блокування",
                           "структура File усередині",
                           "алгоритм читання з диска"]):
        p.append(rect(480, 140 + i * 46, 260, 36, fill="#ffffff", stroke="#d7dbe0", sw=1.2, rx=6))
        p.append(text(610, 163 + i * 46, s, size=11.5, color=MUTED))
    p.append(text(610, 300, "переписуй будь-коли — ніхто не помітить", size=10.5, color=FIELD, bold=True))

    # шов між ними
    p.append(line(410, 74, 410, 316, color=INK, sw=2.2, dash="7,5"))
    p.append(text(410, 350, "рівно по цій лінії проходить рішення: що обіцяти, а що лишити собі",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "seam.svg"), W, H, *p)


# ── 2. Асиметрія дверей: додати — вперед і назад; прибрати — тільки вперед ──
def fig_one_way():
    W, H = 820, 360
    p = []
    p.append(text(W / 2, 30, "Асиметрія: додати до API легко, забрати — майже неможливо", size=15, bold=True))

    # ЛІВОРУЧ: додавання — двобічні двері
    p.append(rect(70, 70, 320, 210, fill="#eaf6ef", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(230, 98, "ДОДАТИ метод / поле", size=13, color=FIELD, bold=True))
    p.append(text(230, 120, "двобічні двері", size=11, color=FIELD, italic=True))
    p.append(arrow(150, 165, 310, 165, color=FIELD, sw=2.2))
    p.append(arrow(310, 200, 150, 200, color=FIELD, sw=2.2))
    p.append(text(230, 240, "старий код працює як був,", size=11, color=INK))
    p.append(text(230, 258, "новий отримує більше", size=11, color=INK))

    # ПРАВОРУЧ: видалення — однобічні двері
    p.append(rect(430, 70, 320, 210, fill="#fdecea", stroke=POS, sw=1.6, rx=10))
    p.append(text(590, 98, "ЗАБРАТИ / ЗМІНИТИ зміст", size=13, color=POS, bold=True))
    p.append(text(590, 120, "однобічні двері", size=11, color=POS, italic=True))
    p.append(arrow(510, 175, 670, 175, color=POS, sw=2.4))
    p.append(text(590, 210, "кожен, хто це кличе,", size=11, color=INK))
    p.append(text(590, 228, "ламається — і мовчки, і гучно", size=11, color=INK))
    p.append(text(590, 256, "назад ходу немає", size=11, color=POS, bold=True))

    p.append(text(W / 2, 320, "Тому «коли вагаєшся — не додавай»: невключене додаси потім, зайве вже не прибереш.",
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "one_way.svg"), W, H, *p)


# ── 3. Той самий шов на трьох масштабах — функція, модуль, сервіс ──
def fig_scales():
    W, H = 860, 340
    p = []
    p.append(text(W / 2, 30, "Один принцип, три масштаби: скрізь це контракт через межу", size=15, bold=True))

    cols = [
        ("виклик функції", "сигнатура + що вона\nобіцяє й що псує", "#eaf6ef", FIELD,
         "правиш аргументи —\nправиш усі виклики"),
        ("модуль / бібліотека", "публічні класи,\nзаголовки, семвер", "#eaf0fd", NEG,
         "правиш API —\nправиш чужі збірки"),
        ("сервіс по мережі", "REST / події /\nсхема повідомлень", "#fef6e9", "#8a6508",
         "правиш формат —\nправиш живі системи"),
    ]
    n = len(cols)
    bw, gap = 240, 26
    total = n * bw + (n - 1) * gap
    x = (W - total) / 2 + bw / 2
    for i, (tag, body, fc, sc, warn) in enumerate(cols):
        bx = x - bw / 2
        p.append(rect(bx, 70, bw, 150, fill=fc, stroke=sc, sw=1.7, rx=10))
        p.append(text(x, 98, tag, size=13.5, color=sc, bold=True))
        p.append(mtext(x, 132, body, size=12, color=INK))
        p.append(line(bx + 20, 176, bx + bw - 20, 176, color=sc, sw=1))
        wl = warn.split("\n")
        p.append(text(x, 194, wl[0], size=11, color=MUTED, italic=True))
        p.append(text(x, 210, wl[1], size=11, color=MUTED, italic=True))
        if i < n - 1:
            ax = x + bw / 2 + gap / 2
            p.append(text(ax, 146, "той самий", size=10, color=MUTED, italic=True))
            p.append(text(ax, 160, "закон", size=10, color=MUTED, italic=True))
        x += bw + gap

    p.append(rect(70, 250, W - 140, 66, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(W / 2, 276, "Що ширша аудиторія межі, то дорожча зміна: аргумент правиш за хвилину,",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 298, "формат події між сервісами — місяцями й з узгодженням чужих команд.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "scales.svg"), W, H, *p)


# ── 4. Вартість зміни як функція N: адитивна пласка нуль, ламка — пряма N·c ──
def fig_cost_lines():
    W, H = 860, 460
    p = []
    p.append(text(W / 2, 30, "Вартість зміни від числа викликів N: адитивна ≈ 0, ламка росте як N·c", size=15, bold=True))

    # осі
    ox, oy = 110, 380          # початок координат
    ax_w, ax_h = 660, 300      # довжина осей
    p.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))            # X
    p.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))           # Y
    p.append(text(ox + ax_w, oy + 26, "N — кількість місць-викликів (call sites)", size=12, color=INK, anchor="end"))
    # підпис осі Y — вертикально, ліворуч від осі
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">вартість зміни (год-люд)</text>'
             % (34, oy - ax_h / 2, FONT, INK, 34, oy - ax_h / 2))

    # ламка пряма C = N·c
    x2, y2 = ox + ax_w - 40, oy - ax_h + 30
    p.append(line(ox, oy, x2, y2, color=POS, sw=2.6))
    p.append(text(x2 - 6, y2 - 14, "ламка зміна:  C(N) = N · c", size=12.5, color=POS, bold=True, anchor="end"))
    # точка «нахил = c» на прямій
    mx, my = ox + (x2 - ox) * 0.45, oy + (y2 - oy) * 0.45
    p.append(circle(mx, my, 4, fill=POS, stroke=POS))
    p.append(text(mx + 12, my + 4, "нахил = c (ціна одного виклику)", size=11, color=POS, anchor="start"))

    # адитивна пласка лінія на нулі
    p.append(line(ox, oy - 6, ox + ax_w - 40, oy - 6, color=FIELD, sw=2.6, dash="8,5"))
    p.append(text(ox + ax_w - 44, oy - 16, "адитивна зміна:  C ≈ 0 (старі виклики дійсні)", size=12.5, color=FIELD, bold=True, anchor="end"))

    # вертикальна «прірва» на прикладному N
    xg = ox + (x2 - ox) * 0.72
    yg = oy + (y2 - oy) * 0.72
    p.append(line(xg, oy, xg, yg, color=MUTED, sw=1.2, dash="3,4"))
    p.append(circle(xg, yg, 4, fill=BG, stroke=POS, sw=2))
    p.append(circle(xg, oy - 6, 4, fill=BG, stroke=FIELD, sw=2))
    p.append(text(xg, oy + 20, "те саме N", size=10.5, color=MUTED))
    # розрив між двома точками = ціна ламкості
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="start">↕ розрив = ціна ламкості</text>' % (xg + 8, (oy + yg) / 2, FONT, MUTED))

    p.append(text(W / 2, 438, "Обидві дії стартують з однієї точки, та адитивна лишається на підлозі, а ламка тим вища, чим більше N.",
                  size=11.5, color=INK))
    render(os.path.join(OUT, "cost_lines.svg"), W, H, *p)


# ── 5. Незворотність = чи N у твоєму контролі: двобічні двері vs однобічні ──
def fig_reversibility():
    W, H = 860, 420
    p = []
    p.append(text(W / 2, 30, "Незворотність = коли N поза твоїм контролем", size=15, bold=True))

    # ЛІВОРУЧ: N мале й відоме — контроль, зворотно
    p.append(rect(60, 70, 350, 280, fill="#eaf6ef", stroke=FIELD, sw=1.7, rx=10))
    p.append(text(235, 100, "N мале й відоме (твій контроль)", size=13, color=FIELD, bold=True))
    p.append(text(235, 122, "внутрішнє API — кличуть із твого ж репозиторію", size=10.5, color=MUTED, italic=True))
    p.append(fitbox(90, 145, 290, 44, "усі N викликів перелічені:\ngrep знаходить кожен", size=11.5,
                    fill=BG, stroke=FIELD, sw=1.3, color=INK))
    p.append(fitbox(90, 200, 290, 44, "полагодив усі → зламаного не лишилось", size=11.5,
                    fill=BG, stroke=FIELD, sw=1.3, color=INK))
    p.append(text(235, 278, "C = N · c скінченна й оплатна", size=12, color=FIELD, bold=True))
    p.append(text(235, 302, "двобічні двері — зміну можна відкотити", size=11, color=INK))
    p.append(text(235, 326, "рішення ЗВОРОТНЕ", size=12.5, color=FIELD, bold=True))

    # ПРАВОРУЧ: N поза контролем — незворотно
    p.append(rect(450, 70, 350, 280, fill="#fdecea", stroke=POS, sw=1.7, rx=10))
    p.append(text(625, 100, "N поза контролем (не твоє)", size=13, color=POS, bold=True))
    p.append(text(625, 122, "публічна бібліотека — тебе взяли тисячі незнайомців", size=10.5, color=MUTED, italic=True))
    p.append(fitbox(480, 145, 290, 44, "N невідоме й росте: багатьох викликів\nти навіть не бачиш", size=11.5,
                    fill=BG, stroke=POS, sw=1.3, color=INK))
    p.append(fitbox(480, 200, 290, 44, "полагодити чужі рядки ти не можеш —\nвони не в твоєму дереві", size=11.5,
                    fill=BG, stroke=POS, sw=1.3, color=INK))
    p.append(text(625, 278, "C = N · c — рахунок лягає на чужих", size=12, color=POS, bold=True))
    p.append(text(625, 302, "однобічні двері — назад ходу немає", size=11, color=INK))
    p.append(text(625, 326, "рішення НЕЗВОРОТНЕ", size=12.5, color=POS, bold=True))

    p.append(text(W / 2, 392, "Технічно файл однаково легко змінити з обох боків; різниця лише в тому, ХТО володіє множиною N.",
                  size=11.5, color=INK))
    render(os.path.join(OUT, "reversibility.svg"), W, H, *p)


# ── 6. Opaque handle: у заголовку лише вказівник, поля сховані в .c ──
def fig_opaque():
    W, H = 860, 430
    p = []
    p.append(text(W / 2, 30, "Opaque handle: клієнт бачить лише вказівник, поля сховані в .c",
                  size=15, bold=True))

    # заголовок sensor.h — те, що бачить клієнт
    p.append(rect(60, 66, 330, 300, fill="#eaf6ef", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(225, 92, "sensor.h  (бачить клієнт)", size=13, color=FIELD, bold=True))
    for i, s in enumerate(["typedef struct sensor sensor_t;",
                           "",
                           "sensor_t *sensor_open(int pin);",
                           "float sensor_read(sensor_t *s);",
                           "void sensor_close(sensor_t *s);"]):
        if s:
            p.append(rect(78, 108 + i * 40, 294, 30, fill=BG, stroke=FIELD, sw=1.1, rx=5))
            p.append(text(225, 128 + i * 40, s, size=11, color=INK))
    p.append(text(225, 330, "неповний тип: розмір і поля невідомі —", size=10.5, color=MUTED, italic=True))
    p.append(text(225, 348, "лише вказівник, дерефом не дотягнешся", size=10.5, color=MUTED, italic=True))

    # реалізація sensor.c — сховані поля
    p.append(rect(470, 66, 330, 300, fill=FILL, stroke=MUTED, sw=1.6, rx=10))
    p.append(text(635, 92, "sensor.c  (сховане нутро)", size=13, color=INK, bold=True))
    p.append(text(635, 112, "struct sensor {", size=11.5, color=INK))
    for i, s in enumerate(["int   pin;",
                           "float scale, offset;",
                           "uint16_t buf[64];  // кеш",
                           "uint32_t last_us;"]):
        p.append(rect(500, 126 + i * 38, 270, 28, fill="#ffffff", stroke="#d7dbe0", sw=1.1, rx=5))
        p.append(text(635, 145 + i * 38, s, size=11, color=MUTED))
    p.append(text(635, 300, "};", size=11.5, color=INK))
    p.append(text(635, 330, "переставляй, додавай, викидай поля —", size=10.5, color=FIELD, italic=True))
    p.append(text(635, 348, "заголовок не змінюється, клієнт не перезбирається", size=9.6, color=FIELD, italic=True))

    p.append(arrow(392, 216, 468, 216, color=INK, sw=2))
    p.append(text(430, 205, "лише *", size=9.5, color=MUTED, italic=True))

    p.append(text(W / 2, 400, "Ширина схованого = міра свободи міняти нутро без перезбирання клієнтів.",
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "opaque.svg"), W, H, *p)


# ── 7. Versioned struct: поле size першим, нові поля — тільки в кінець ──
def fig_versioned():
    W, H = 900, 470
    p = []
    p.append(text(W / 2, 30, "Versioned struct: поле size першим, нові поля — тільки в кінець",
                  size=15, bold=True))

    rows_v1 = [("size_t size;", "мітка: скільки байтів дав клієнт", True),
               ("int   pin;", "", False),
               ("uint32_t rate_hz;", "", False)]
    rows_add = [("uint8_t gain;", "додано у v2"),
                ("float offset;", "додано у v2")]

    x0, y0, bw, bh = 70, 78, 300, 30
    # ── v1-клієнт (стара збірка) ──
    p.append(text(x0 + bw / 2, y0 - 10, "заповнив клієнт, зібраний під v1", size=12, color=NEG, bold=True))
    y = y0
    for s, note, mark in rows_v1:
        p.append(rect(x0, y, bw, bh, fill="#eaf0fd" if mark else BG,
                      stroke=NEG if mark else "#c9cfd6", sw=1.4 if mark else 1.1, rx=5))
        p.append(text(x0 + bw / 2, y + 20, s, size=11, color=INK))
        if note:
            p.append(text(x0 + bw / 2, y + bh + 15, note, size=9.5, color=MUTED, italic=True))
        y += bh + 8
    y += 14
    p.append(rect(x0, y, bw, bh, fill="#f0f0f0", stroke="#c9cfd6", sw=1.1, rx=5))
    p.append(text(x0 + bw / 2, y + 20, "( полів gain / offset немає )", size=10.5, color=MUTED, italic=True))
    p.append(text(x0 + bw / 2, y + bh + 24, "size = 16 байтів", size=11.5, color=NEG, bold=True))

    # ── v2-структура (нова бібліотека) ──
    x1 = 530
    p.append(text(x1 + bw / 2, y0 - 10, "struct у новій бібліотеці (v2)", size=12, color=POS, bold=True))
    y = y0
    for s, note, mark in rows_v1:
        p.append(rect(x1, y, bw, bh, fill="#eaf0fd" if mark else BG,
                      stroke=NEG if mark else "#c9cfd6", sw=1.4 if mark else 1.1, rx=5))
        p.append(text(x1 + bw / 2, y + 20, s, size=11, color=INK))
        y += bh + 8
    p.append(line(x1 - 6, y + 3, x1 + bw + 6, y + 3, color=POS, sw=1.4, dash="5,4"))
    p.append(text(x1 + bw + 14, y + 7, "межа v1", size=9, color=POS, anchor="start", italic=True))
    y += 10
    for s, note in rows_add:
        p.append(rect(x1, y, bw, bh, fill="#fdecea", stroke=POS, sw=1.3, rx=5))
        p.append(text(x1 + bw / 2, y + 20, s, size=11, color=INK))
        p.append(text(x1 + bw + 14, y + 20, note, size=9.5, color=POS, anchor="start", italic=True))
        y += bh + 8
    p.append(text(x1 + bw / 2, y + 16, "новий клієнт: size = 25 байтів", size=11.5, color=POS, bold=True))

    # висновок-рамка
    bx, byy = 70, 396
    p.append(rect(bx, byy, W - 140, 60, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(W / 2, byy + 24, "Бібліотека дивиться на size: клієнт дав 16 — читає лише перші три поля,",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, byy + 44, "gain / offset бере за замовчуванням. Старі виклики цілі — нові поля тільки в кінці.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "versioned.svg"), W, H, *p)


# ── 8. Тихий злом ABI: поле в середину — зсуви «пливуть», старий клієнт читає не те ──
def fig_traps():
    W, H = 900, 440
    p = []
    p.append(text(W / 2, 28, "Тихий злом: поле в середину — зсуви «пливуть», старий клієнт читає не те",
                  size=14.5, bold=True))

    def stack(x, title, tcol, rows):
        frag = [text(x + 100, 66, title, size=12, color=tcol, bold=True)]
        y = 82
        for name, ofs, col in rows:
            frag.append(rect(x, y, 200, 30, fill=col[0], stroke=col[1], sw=1.3, rx=5))
            frag.append(text(x + 100, y + 20, name, size=10.5, color=INK))
            frag.append(text(x - 12, y + 20, ofs, size=9.5, color=MUTED, anchor="end"))
            y += 36
        return frag

    OKF = ("#eaf6ef", FIELD)
    BAD = ("#fdecea", POS)
    NEU = (BG, "#c9cfd6")

    # чого чекає старий клієнт
    p += stack(90, "чого чекає v1-клієнт", NEG,
               [("pin   @0", "0", NEU), ("rate  @4", "4", NEU), ("gain  @8", "8", NEU)])
    p.append(text(190, 210, "читає gain за зсувом 8", size=10, color=NEG, italic=True))

    # що зробила бібліотека — вставка в СЕРЕДИНУ
    p += stack(410, "бібліотека вставила поле в СЕРЕДИНУ", POS,
               [("pin    @0", "0", OKF), ("mode  @4  ← нове", "4", BAD),
                ("rate   @8", "8", BAD), ("gain  @12", "12", BAD)])
    p.append(text(510, 246, "gain з'їхав на 12 — клієнт", size=10, color=POS, italic=True))
    p.append(text(510, 262, "за зсувом 8 бере rate", size=10, color=POS, italic=True))

    # стрілка розбіжності
    p.append(arrow(300, 150, 406, 150, color=POS, sw=2))
    p.append(text(353, 138, "той самий", size=9, color=MUTED, italic=True))
    p.append(text(353, 166, "заголовок?", size=9, color=MUTED, italic=True))

    # три правила внизу
    y = 312
    for i, s in enumerate([("Зсув поля = сума розмірів усього ДО нього: посунув одне — «попливло» все нижче.", POS),
                           ("Тихо змінив зміст (ті самі байти означають інше) — компілятор мовчить, поведінка бреше.", POS),
                           ("Правило: нове поле — тільки в КІНЕЦЬ; порядок і зміст наявних не чіпати ніколи.", FIELD)]):
        txt, col = s
        p.append(text(70, y, "•", size=13, color=col, anchor="start", bold=True))
        p.append(text(90, y, txt, size=11, color=INK if col is POS else FIELD, anchor="start", bold=(col is FIELD)))
        y += 30
    render(os.path.join(OUT, "traps.svg"), W, H, *p)


# ── 9. Родовід ідеї: Парнас → Блох → Гікі, три оберти однієї думки ──────────
def fig_lineage():
    W, H = 980, 470
    p = []
    p.append(text(W / 2, 32, "Один закон, троє й через півстоліття: межа переживає реалізацію",
                  size=15, bold=True))

    ax_y = 150                       # рівень осі часу
    x0, x1 = 90, W - 90
    p.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2.2))
    p.append(arrow(x1 - 30, ax_y, x1, ax_y, color=INK, sw=2.2))
    p.append(text(x1, ax_y - 12, "час", size=11.5, color=MUTED, italic=True, anchor="end"))

    # три віхи: (x, рік, ім'я, роль, три рядки суті, колір)
    milestones = [
        (245, "1972", "Девід Парнас", "НАВІЩО межа",
         ["ділити за прихованим", "рішенням, не за потоком;", "інтерфейс виказує мінімум"], FIELD),
        (500, "2006", "Джошуа Блох", "ЯК її проектувати",
         ["усі ми — проектувальники API;", "публічне API — назавжди;", "додати можна, забрати — ні"], NEG),
        (760, "2016", "Річ Гікі", "ЩО робити при зміні",
         ["нарощування проти ламання;", "вимагай менше / давай більше;", "зламав — зробив іншу річ"], POS),
    ]
    box_w = 248
    for mx, year, who, role, body, col in milestones:
        # позначка на осі
        p.append(circle(mx, ax_y, 6, fill=BG, stroke=col, sw=2.6))
        p.append(text(mx, ax_y - 16, year, size=14, color=col, bold=True))
        # тонкий стояк від осі до картки
        by = ax_y + 42
        p.append(line(mx, ax_y + 6, mx, by, color=col, sw=1.2, dash="3,4"))
        # картка під віссю
        bx = mx - box_w / 2
        bh = 152
        p.append(rect(bx, by, box_w, bh, fill=FILL, stroke=col, sw=1.7, rx=10))
        p.append(text(mx, by + 26, who, size=13.5, color=INK, bold=True))
        p.append(text(mx, by + 47, role, size=11.5, color=col, bold=True, italic=True))
        p.append(line(bx + 18, by + 60, bx + box_w - 18, by + 60, color=col, sw=1))
        for i, ln in enumerate(body):
            p.append(text(mx, by + 82 + i * 20, ln, size=10.6, color=INK))

    # наскрізний висновок під усім
    p.append(fitbox(x0, H - 68, x1 - x0, 46,
                    "Спільний стрижень: межа коду — оприлюднене рішення, що переживає свою реалізацію, "
                    "і тихо забрати його назад не можна.",
                    size=12.5, fill="#eef4ff", stroke=NEG, sw=1.5, color=INK, bold=True))
    render(os.path.join(OUT, "lineage.svg"), W, H, *p)


if __name__ == "__main__":
    fig_seam()
    fig_one_way()
    fig_scales()
    fig_cost_lines()
    fig_reversibility()
    fig_opaque()
    fig_versioned()
    fig_traps()
    fig_lineage()
    print("OK: figs written to", OUT)
