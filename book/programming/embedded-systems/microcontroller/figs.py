# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── what-is-mcu: цілий комп'ютер на одному чіпі, з ніжками у світ ──────────────
# Ідея: один кристал містить ядро, дві пам'яті, периферію й такт, з'єднані
# внутрішньою шиною; назовні стирчать лише ніжки до світу (входи й виходи).

def fig_what_is_mcu():
    W, H = 880, 540
    p = []

    # межа кристала
    p.append(text(280, 132, "ОДИН ЧІП (кристал)", size=12, color=FIELD, bold=True))
    p.append(rect(120, 150, 320, 300, fill="#cfd6e6", stroke=INK, sw=2.4, rx=10))

    # чотири блоки всередині
    p.append(rect(140, 176, 132, 64, fill="#fbecec", stroke=POS, sw=1.8, rx=4))
    p.append(text(206, 205, "Ядро (CPU)", size=12, bold=True))
    p.append(text(206, 221, "обчислення", size=10, color=MUTED))
    p.append(rect(288, 176, 132, 64, fill=BG, stroke=INK, sw=1.8, rx=4))
    p.append(text(354, 205, "Програмна пам'ять", size=12, bold=True))
    p.append(text(354, 221, "код", size=10, color=MUTED))
    p.append(rect(140, 300, 132, 64, fill=BG, stroke=INK, sw=1.8, rx=4))
    p.append(text(206, 329, "Пам'ять даних", size=12, bold=True))
    p.append(text(206, 345, "змінні", size=10, color=MUTED))
    p.append(rect(288, 300, 132, 64, fill=BG, stroke=INK, sw=1.8, rx=4))
    p.append(text(354, 329, "Периферія", size=12, bold=True))
    p.append(text(354, 345, "ввід-вивід", size=10, color=MUTED))
    p.append(rect(170, 384, 220, 46, fill=FILL, stroke=INK, sw=1.8, rx=4))
    p.append(text(280, 411, "Генератор такту · живлення", size=12, bold=True))

    # внутрішня шина
    p.append(line(150, 270, 410, 270, color=FIELD, sw=3))
    p.append(text(280, 262, "внутрішня шина", size=10, color=FIELD, bold=True))
    for bx in (206, 354):
        p.append(line(bx, 240, bx, 270, color=FIELD, sw=1.8))
        p.append(line(bx, 270, bx, 300, color=FIELD, sw=1.8))

    # живлення ззовні
    p.append(arrow(40, 230, 118, 230, color=POS, sw=2.6))
    p.append(text(44, 222, "живлення", size=11, color=POS, anchor="start", bold=True))

    # світ: входи (сині) і виходи (зелені)
    p.append(text(660, 150, "СВІТ", size=12, color=MUTED, bold=True))
    ins = [(196, "кнопка"), (266, "давач")]
    for yy, lab in ins:
        p.append(rect(440, yy - 4, 10, 8, fill="#9a9aa0", stroke=MUTED, sw=0.8, rx=0))
        p.append(rect(600, yy - 20, 120, 40, fill="#fbfbfb", stroke=INK, sw=1.6))
        p.append(text(660, yy + 4, lab, size=12, bold=True))
        p.append(line(598, yy, 452, yy, color=NEG, sw=2.2))
        p.append('<line x1="598" y1="%d" x2="454" y2="%d" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % (yy, yy, NEG))
    outs = [(336, "мотор"), (406, "світлодіод")]
    for yy, lab in outs:
        p.append(rect(440, yy - 4, 10, 8, fill="#9a9aa0", stroke=MUTED, sw=0.8, rx=0))
        p.append(rect(600, yy - 20, 120, 40, fill="#fbfbfb", stroke=INK, sw=1.6))
        p.append(text(660, yy + 4, lab, size=12, bold=True))
        p.append('<line x1="452" y1="%d" x2="596" y2="%d" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % (yy, yy, FIELD))

    p.append(text(250, 500, "сині стрілки — входи (читає світ)", size=11, color=NEG, bold=True))
    p.append(text(660, 500, "зелені — виходи (керує світом)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "what-is-mcu.svg"), W, H, *p,
           title="Мікроконтролер: цілий комп'ютер на одному чіпі")


# ── mp-vs-mc-board: розсип чипів проти одного чіпа ────────────────────────────
# Ідея: те саме завдання очима того, хто паяє плату. Зліва мікропроцесор — ядро
# плюс окремі чипи ПЗП/ОЗП/периферії/такту, з'єднані доріжками. Справа МК — усе
# на одному чипі, лишилося підвести живлення.

def _chip(p, x, y, w, h, label, fs=9):
    p.append(rect(x, y, w, h, fill="#2b2b2b", stroke="#000000", sw=1.2, rx=2))
    # ніжки з боків
    n = max(2, int(h // 16))
    for i in range(n):
        py = y + (i + 0.5) * h / n - 1.5
        p.append(rect(x - 6, py, 6, 3, fill="#9a9aa0", stroke=MUTED, sw=0.8, rx=0))
        p.append(rect(x + w, py, 6, 3, fill="#9a9aa0", stroke=MUTED, sw=0.8, rx=0))
    p.append(text(x + w / 2, y + h / 2 + 4, label, size=fs, color="#ffffff", bold=True))


def fig_mp_vs_mc_board():
    W, H = 920, 520
    p = []

    # ── ліворуч: мікропроцесор як ціла плата ──
    p.append(rect(36, 84, 420, 380, fill="#dfe7d8", stroke="#4f7a3a", sw=2, rx=12))
    p.append(text(246, 108, "Мікропроцесор: ціла плата", size=14, bold=True))
    # доріжки-шини від центру
    for x2, y2 in [(246, 172), (382, 282), (246, 392), (116, 282)]:
        p.append(line(246, 282, x2, y2, color=MUTED, sw=2))
    _chip(p, 198, 242, 96, 80, "MPU", fs=10)
    p.append(text(246, 340, "лише ядро", size=10.5, color=POS, bold=True))
    _chip(p, 211, 147, 70, 50, "ПЗП")
    _chip(p, 347, 257, 70, 50, "ОЗП")
    _chip(p, 211, 367, 70, 50, "I/O")
    _chip(p, 81, 257, 70, 50, "такт")
    p.append(text(246, 452, "+ десятки доріжок-шин", size=11.5, color=MUTED, italic=True))

    # ── праворуч: мікроконтролер як один чіп ──
    p.append(rect(484, 84, 400, 380, fill="none", stroke="#e4e4e4", sw=2, rx=12))
    p.append(text(684, 108, "Мікроконтролер: один чіп", size=14, bold=True))
    _chip(p, 609, 199, 150, 150, "MCU", fs=18)
    p.append(text(684, 280, "усе", size=11, color="#cfcfcf"))
    p.append(text(684, 296, "всередині", size=11, color="#cfcfcf"))
    p.append(arrow(556, 200, 602, 200, color=POS, sw=2.4))
    p.append(text(552, 192, "живлення", size=11, color=POS, anchor="end", bold=True))
    p.append(text(684, 452, "+ майже нічого більше", size=11.5, color=MUTED, italic=True))

    # підсумкова стрічка
    p.append(rect(70, 478, 780, 30, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(460, 498, "Один чіп замість плати чипів: менше з'єднань, місця й ціни — вища надійність.",
                  size=13, bold=True))

    render(os.path.join(OUT, "mp-vs-mc-board.svg"), W, H, *p,
           title="Мікропроцесор проти мікроконтролера — очима того, хто паяє плату")


# ── scale: порядки величин ПК проти МК ────────────────────────────────────────
# Ідея: чотири числові пари (частота, пам'ять, сховище, споживання) однією
# довгою синьою смугою (ПК) і короткою зеленою (МК) — різниця в тисячі-мільйони
# разів; п'ятий рядок (роль) найважливіший: багатозадачність проти однієї справи.

def fig_scale():
    W, H = 920, 480
    p = []

    # легенда
    p.append(rect(346, 70, 16, 12, fill="#e9eefb", stroke=NEG, sw=1.2, rx=0))
    p.append(text(368, 80, "ПК (мікропроцесор + ОС)", size=11.5, color=NEG, anchor="start", bold=True))
    p.append(rect(612, 70, 16, 12, fill="#eef6ef", stroke=FIELD, sw=1.2, rx=0))
    p.append(text(634, 80, "МК (мікроконтролер)", size=11.5, color=FIELD, anchor="start", bold=True))

    rows = [
        ("Тактова частота", 116, "~3 ГГц", "десятки–сотні МГц", "× у тисячі"),
        ("Пам'ять даних", 180, "~16 ГБ", "сотні КБ", "× у мільйони"),
        ("Сховище", 244, "~1 ТБ", "одиниці МБ", "× у сотні тисяч"),
        ("Споживання", 308, "десятки Вт", "мілівати", "× у тисячі"),
    ]
    for name, y, big, small, mult in rows:
        p.append(text(40, y + 12, name, size=13.5, anchor="start", bold=True))
        p.append(rect(210, y, 360, 16, fill="#e9eefb", stroke=NEG, sw=1.4, rx=3))
        p.append(text(578, y + 13, big, size=12, color=NEG, anchor="start", bold=True))
        p.append(rect(210, y + 22, 26, 16, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=3))
        p.append(text(244, y + 35, small, size=12, color=FIELD, anchor="start", bold=True))
        p.append(rect(666, y + 4, 124, 28, fill="#f7f4ea", stroke="#caa24a", sw=1.2, rx=8))
        p.append(text(728, y + 22, mult, size=11.5, bold=True))

    p.append(line(40, 376, 880, 376, color="#e4e4e4", sw=1.4))
    p.append(text(40, 402, "Роль", size=13.5, anchor="start", bold=True))
    p.append(text(210, 398, "багато застосунків під операційною системою",
                  size=12, color=NEG, anchor="start", bold=True))
    p.append(text(210, 418, "одна програма, що працює роками без перезавантажень",
                  size=12, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "scale.svg"), W, H, *p,
           title="Порядки величин: настільний комп'ютер проти мікроконтролера")


# ── boot: самодостатній старт проти завантаження ОС ───────────────────────────
# Ідея: дві доріжки кроків після ввімкнення. МК: скидання → читає код → працює
# (мілісекунди). Комп'ютер: довгий ланцюг завантаження (десятки секунд).

def _flow(p, x0, y, steps, color, fill, tail):
    x = x0
    bw, bh, gap = 104, 50, 16
    for i, lab in enumerate(steps):
        p.append(rect(x, y, bw, bh, fill=fill, stroke=color, sw=1.8, rx=6))
        p.append(mtext(x + bw / 2, y + bh / 2 - 3, lab, size=10.5, color=INK))
        if i < len(steps) - 1:
            ax = x + bw + 1
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
                     % (ax, y + bh / 2, ax + gap - 2, y + bh / 2, color))
        x += bw + gap
    # хвостова мітка часу
    p.append(rect(x, y + 8, 124, 34, fill=BG, stroke=color, sw=1.6, rx=8))
    p.append(text(x + 62, y + 30, tail, size=12, color=color, bold=True))


def fig_boot():
    W, H = 900, 430
    p = []

    p.append(text(40, 112, "Мікроконтролер", size=14, color=FIELD, anchor="start", bold=True))
    _flow(p, 50, 124, ["скидання", "читає код\nз пам'яті", "код\nпрацює"],
          FIELD, "#eef6ef", "≈ мілісекунди")

    p.append(text(40, 274, "Комп'ютер (мікропроцесор + ОС)", size=14, color=MUTED, anchor="start", bold=True))
    _flow(p, 50, 286, ["скидання", "заван-\nтажувач", "пошук\nдиска", "підняття\nОС",
                       "драй-\nвери", "робочий\nстіл"],
          MUTED, FILL, "≈ десятки с")

    p.append(text(450, 404, "МК не «вмикається» — він просто одразу Є; комп'ютер мусить спершу зібрати себе докупи.",
                  size=12, italic=True))

    render(os.path.join(OUT, "boot.svg"), W, H, *p,
           title="Самодостатній старт: МК біжить одразу, комп'ютер вантажить ОС")


# ── spectrum: неперервна шкала від крихітного МК до ПК, і де ESP32 ─────────────
# Ідея: одна вісь «обчислювальної ваги»; чотири точки-вузли; ESP32 виділено
# зеленим у мікроконтролерній частині, близько до межі з мікропроцесорами.

def fig_spectrum():
    W, H = 920, 380
    p = []

    # вісь
    p.append(line(70, 212, 850, 212, color=INK, sw=2.6))
    p.append(arrow(835, 212, 872, 212, color=INK, sw=2.6))
    p.append(text(460, 284, "обчислювальна вага →", size=12.5, bold=True))

    nodes = [
        (170, "простий 8-біт МК", "КБ пам'яті · центи", INK, "#fbfbfb", 7, False),
        (392, "потужний МК / SoC", "ESP32 · МБ · радіо", FIELD, "#eef6ef", 9, True),
        (612, "одноплатник з ОС", "Raspberry Pi · ГБ", INK, "#fbfbfb", 7, False),
        (812, "ПК / сервер", "багатоядерний · ОС", INK, "#fbfbfb", 7, False),
    ]
    for cx, t1, t2, col, fill, r, hi in nodes:
        p.append(circle(cx, 212, r, fill=BG, stroke=col, sw=3 if hi else 2.4))
        if hi:
            p.append(circle(cx, 212, 3.5, fill=col, stroke=col, sw=0))
        p.append(rect(cx - 92, 132, 184, 46, fill=fill, stroke=col, sw=2.4 if hi else 1.6, rx=8))
        p.append(text(cx, 154, t1, size=12.5, color=col if hi else INK, bold=True))
        p.append(text(cx, 170, t2, size=10.5, color=MUTED))
        p.append(line(cx, 178, cx, 204, color=col if hi else INK, sw=1.4, dash="2 3"))

    # підкреслення двох зон
    p.append(line(110, 240, 472, 240, color=FIELD, sw=2.4))
    p.append(text(291, 258, "МІКРОКОНТРОЛЕРИ (усе на чипі)", size=11.5, color=FIELD, bold=True))
    p.append(line(532, 240, 852, 240, color=MUTED, sw=2.4))
    p.append(text(692, 258, "МІКРОПРОЦЕСОРИ + ОС", size=11.5, color=MUTED, bold=True))

    render(os.path.join(OUT, "spectrum.svg"), W, H, *p,
           title="Шкала обчислювальної ваги: де на ній ESP32")


# ── budget: дві посудини пам'яті, заповнені на 4.4% і 14% ─────────────────────
# Ідея: код у програмну пам'ять (тонка смужка в широкій посудині), змінні — в
# пам'ять даних; обидві в кілобайтах, по вінця не заливають.

def fig_budget():
    W, H = 860, 430
    p = []

    # програмна пам'ять
    p.append(text(40, 102, "Програмна пам'ять (код)", size=14, anchor="start", bold=True))
    p.append(rect(40, 112, 700, 44, fill="#fbfbfb", stroke=INK, sw=1.8, rx=6))
    p.append(rect(40, 112, 30.8, 44, fill="#fbecec", stroke=POS, sw=1.6, rx=6))
    p.append(text(78.8, 138, "180 КБ", size=11.5, color=POS, anchor="start", bold=True))
    p.append(text(732, 102, "4.4% зайнято", size=11.5, color=POS, anchor="end", bold=True))
    p.append(text(732, 172, "ємність 4 МБ = 4096 КБ", size=11.5, color=MUTED, anchor="end"))

    # пам'ять даних
    p.append(text(40, 232, "Пам'ять даних (змінні)", size=14, anchor="start", bold=True))
    p.append(rect(40, 242, 700, 44, fill="#fbfbfb", stroke=INK, sw=1.8, rx=6))
    p.append(rect(40, 242, 98.4, 44, fill="#e9eefb", stroke=NEG, sw=1.6, rx=6))
    p.append(text(89.2, 268, "45 КБ", size=11.5, anchor="middle", bold=True))
    p.append(text(732, 232, "14.1% зайнято", size=11.5, color=NEG, anchor="end", bold=True))
    p.append(text(732, 302, "ємність 320 КБ", size=11.5, color=MUTED, anchor="end"))

    # урок
    p.append(rect(40, 330, 700, 72, fill="#f7f4ea", stroke="#caa24a", sw=1.6, rx=10))
    p.append(text(56, 354, "Урок:", size=13, anchor="start", bold=True))
    p.append(text(56, 374, "обидві посудини вимірюють у КБ, а не ГБ; заповнювати «по вінця» не можна —",
                  size=12, anchor="start"))
    p.append(text(56, 393, "лишають запас на стек і непередбачене. Складніша задача — і запас тане вмить.",
                  size=12, anchor="start"))

    render(os.path.join(OUT, "budget.svg"), W, H, *p,
           title="Бюджет пам'яті: чи влізе програма в мікроконтролер")


# ── hist timeline: ланцюг питань від «шафи» до ESP32 ──────────────────────────
# Ідея: п'ять вузлів-щаблів зліва направо, з'єднані стрілками; під кожним —
# хто/коли; передостанній (TMS1000) виділено червоним, останній (ESP32) зелений.

def fig_timeline():
    W, H = 980, 360
    p = []
    p.append(text(W / 2, 50, "кожен крок — нове питання, що штовхало далі",
                  size=12.5, color=MUTED, italic=True))

    nodes = [
        ("Комп'ютер =\nшафа", "до 1971", INK, "#fbfbfb", False),
        ("Калькуляторна\nгонка", "1960-ті · Busicom·TI·Sharp", INK, "#fbfbfb", False),
        ("Intel 4004", "1971 · Hoff·Faggin\nмікропроцесор", NEG, "#e9eefb", False),
        ("TI TMS0100", "1971 · Boone·Cochran\nмікроконтролер", FIELD, "#eef6ef", False),
        ("TMS1000", "1974 · програмований\nМК за долар", POS, "#fbecec", True),
        ("ESP32", "з чого МК складається\nй чим ESP32 особливий", FIELD, "#eef6ef", True),
    ]
    n = len(nodes)
    bw, bh = 138, 54
    cy = 150
    gap = (W - 40 - n * bw) / (n - 1)
    xs = []
    x = 20
    for i in range(n):
        xs.append(x)
        x += bw + gap
    # стрілки між вузлами
    for i in range(n - 1):
        ax1 = xs[i] + bw + 2
        ax2 = xs[i + 1] - 2
        p.append(arrow(ax1, cy + bh / 2, ax2, cy + bh / 2, color=MUTED, sw=2.2))
    # вузли
    for i, (t1, t2, col, fill, hi) in enumerate(nodes):
        x = xs[i]
        sw = 2.6 if hi else 1.8
        p.append(rect(x, cy, bw, bh, fill=fill, stroke=col, sw=sw, rx=8))
        p.append(mtext(x + bw / 2, cy + 22, t1, size=12, color=col if hi else INK, bold=True, lh=1.15))
        p.append(mtext(x + bw / 2, cy + bh + 18, t2, size=9.5, color=MUTED, lh=1.2))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Від «комп'ютер — це шафа» до «комп'ютер — це крихта за долар»")


# ── hist calculator: десятки чипів → один чіп ─────────────────────────────────
# Ідея: ліва зелена панель із сіткою дрібних «IC» (дорого), стрілка «стиснути»,
# права — один великий чіп, що його роблять мільйонами (під модель — інша програма).

def fig_calculator():
    W, H = 940, 470
    p = []

    # ── ліворуч: сітка дрібних чипів ──
    p.append(rect(40, 70, 360, 320, fill="none", stroke=FIELD, sw=2, rx=12))
    p.append(text(220, 96, "калькулятор кінця 1960-х", size=13, bold=True))
    cols, rows = 4, 3
    cw, ch = 64, 40
    gx, gy = 18, 22
    x0 = 220 - (cols * cw + (cols - 1) * gx) / 2
    y0 = 124
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * (cw + gx)
            y = y0 + r * (ch + gy)
            p.append(rect(x, y, cw, ch, fill="#2b2b2b", stroke="#000000", sw=1.1, rx=2))
            p.append(text(x + cw / 2, y + ch / 2 + 4, "IC", size=10, color="#ffffff", bold=True))
    p.append(text(220, 332, "десятки корпусів логіки,", size=10.5, color=MUTED))
    p.append(text(220, 348, "кожен — під одну модель", size=10.5, color=MUTED))
    p.append(text(220, 376, "дорого проєктувати, виробляти, паяти",
                  size=11, color=POS, bold=True))

    # ── центр: стрілка «стиснути» ──
    p.append(arrow(412, 230, 528, 230, color=INK, sw=3))
    p.append(text(470, 218, "стиснути", size=13, bold=True))

    # ── праворуч: один великий чіп ──
    p.append(rect(560, 70, 340, 320, fill="none", stroke="#e4e4e4", sw=2, rx=12))
    _chip(p, 660, 170, 140, 120, "1 ЧІП", fs=18)
    p.append(text(730, 320, "роблять мільйонами", size=12, bold=True))
    p.append(text(730, 360, "модель = інша програма в ПЗП",
                  size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "calculator.svg"), W, H, *p,
           title="Калькуляторна гонка стиснула десятки чипів в один")


# ── hist MCS-4: процесор окремо, пам'ять/периферія окремо ─────────────────────
# Ідея: у центрі великий блок 4004 (CPU) зі списком вузлів; три темні чипи-
# супутники (4001/4002/4003) на спільній «шині»; червоний підпис унизу.

def fig_mcs4_set():
    W, H = 940, 480
    p = []

    # шина (горизонтальна лінія, до якої все підключено)
    p.append(line(120, 250, 820, 250, color=FIELD, sw=3))
    p.append(text(470, 242, "шина", size=10.5, color=FIELD, bold=True))

    # центр: 4004 — мікропроцесор
    p.append(rect(360, 96, 220, 130, fill="#e9eefb", stroke=NEG, sw=2.4, rx=10))
    p.append(text(470, 122, "Intel 4004", size=15, color=NEG, bold=True))
    p.append(text(470, 142, "МІКРОПРОЦЕСОР (CPU)", size=11, color=NEG, bold=True))
    p.append(text(470, 166, "АЛП · регістри · керування", size=10.5, color=INK))
    p.append(text(470, 188, "≈ 2300 транзисторів", size=10.5, color=MUTED))
    p.append(line(470, 226, 470, 250, color=FIELD, sw=2))

    # три супутники-чипи
    sats = [(160, "4001", "ПЗП (програма)"), (400, "4002", "ОЗП (дані)"),
            (640, "4003", "порти (ввід-вивід)")]
    for sx, name, role in sats:
        cx = sx + 70
        p.append(line(cx, 250, cx, 300, color=FIELD, sw=2))
        _chip(p, sx, 300, 140, 64, name, fs=14)
        p.append(text(cx, 388, role, size=10.5, color=MUTED, bold=True))

    # підпис унизу
    p.append(rect(70, 412, 800, 50, fill="#fbecec", stroke=POS, sw=1.6, rx=10))
    p.append(text(470, 433,
                  "Мікропроцесор = «комп'ютер мінус пам'ять і периферія»:",
                  size=12, color=POS, bold=True))
    p.append(text(470, 452, "щоб ожити, 4004 потребує сусідів.",
                  size=12, color=POS, bold=True))

    render(os.path.join(OUT, "mcs4-set.svg"), W, H, *p,
           title="Intel MCS-4 (1971): процесор окремо, пам'ять окремо")


# ── hist МК vs МП у розрізі кристала ──────────────────────────────────────────
# Ідея: дві панелі. Ліва — мікропроцесор: ядро на кристалі, пам'ять/периферія
# окремими боксами ЗЗОВНІ на зовнішній шині. Права — мікроконтролер: усе на
# одному кристалі на внутрішній зеленій шині. Кольорові підписи внизу кожної.

def fig_mc_vs_mp_die():
    W, H = 980, 560
    p = []

    # ── ЛІВА: мікропроцесор ──
    p.append(text(250, 70, "Мікропроцесор (лінія 4004)", size=13.5, bold=True))
    # кристал з лише ядром
    p.append(rect(150, 92, 200, 92, fill="#cfd6e6", stroke=INK, sw=2.2, rx=8))
    p.append(text(250, 130, "Кристал", size=10, color=MUTED))
    p.append(rect(190, 116, 120, 52, fill="#e9eefb", stroke=NEG, sw=1.8, rx=4))
    p.append(text(250, 147, "Ядро (CPU)", size=12, color=NEG, bold=True))
    # зовнішня шина
    p.append(line(110, 250, 410, 250, color=MUTED, sw=3))
    p.append(text(250, 242, "шина — ЗЗОВНІ кристала", size=10, color=MUTED, bold=True))
    p.append(line(250, 184, 250, 250, color=MUTED, sw=2))
    # зовнішні бокси
    ext = [(120, "ПЗП"), (215, "ОЗП"), (310, "Периферія")]
    for ex, lab in ext:
        cx = ex + 40
        p.append(line(cx, 250, cx, 286, color=MUTED, sw=2))
        p.append(rect(ex, 286, 80, 46, fill=BG, stroke=INK, sw=1.6, rx=4))
        p.append(text(cx, 313, lab, size=11, bold=True))
    p.append(rect(70, 354, 360, 64, fill="#fbecec", stroke=POS, sw=1.6, rx=10))
    p.append(mtext(250, 378,
                   ["CPU на чипі — пам'ять і периферія окремо",
                    "→ «видимий» комп'ютер (ПК)"],
                   size=11, color=POS, bold=True, lh=1.3))

    # розділювач
    p.append(line(490, 60, 490, 470, color="#e4e4e4", sw=1.6))

    # ── ПРАВА: мікроконтролер ──
    p.append(text(730, 70, "Мікроконтролер (лінія TMS1000)", size=13.5, bold=True))
    # один кристал з усім
    p.append(rect(560, 92, 340, 220, fill="#dfe7d8", stroke=FIELD, sw=2.4, rx=10))
    p.append(text(730, 112, "ОДИН кристал", size=10.5, color=FIELD, bold=True))
    # внутрішня зелена шина
    p.append(line(585, 210, 875, 210, color=FIELD, sw=3))
    p.append(text(730, 202, "внутрішня шина", size=9.5, color=FIELD, bold=True))
    blocks = [
        (585, 126, "Ядро"), (700, 126, "ПЗП"), (815, 126, "ОЗП"),
        (585, 230, "Такт"), (700, 230, "Периферія"), (815, 230, "Порти"),
    ]
    for bx, by, lab in blocks:
        p.append(rect(bx, by, 80, 52, fill=BG, stroke=INK, sw=1.6, rx=4))
        p.append(text(bx + 40, by + 30, lab, size=11, bold=True))
        p.append(line(bx + 40, by + 52 if by < 200 else by, bx + 40, 210,
                      color=FIELD, sw=1.4))
    p.append(rect(560, 330, 340, 44, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(730, 357, "усе в одному → самодостатній комп'ютер",
                  size=11.5, color=FIELD, bold=True))
    p.append(text(730, 398, "саме цю праву колонку успадкує ESP32",
                  size=11.5, italic=True, color=INK))

    render(os.path.join(OUT, "mc-vs-mp-die.svg"), W, H, *p,
           title="Той самий вододіл, у розрізі кристала")


# ── hist lineages: дві лінії від 1971 ─────────────────────────────────────────
# Ідея: верхній бейдж «1971: комп'ютер на чипі»; від нього дві колонки вниз —
# сіра (мікропроцесор → ПК) і зелена (мікроконтролер → ESP32).

def fig_lineages():
    W, H = 940, 560
    p = []

    # верхній бейдж
    p.append(rect(360, 52, 220, 40, fill="#f7f4ea", stroke="#caa24a", sw=1.8, rx=10))
    p.append(text(470, 77, "1971: комп'ютер на чипі", size=13, bold=True))
    p.append(line(360, 72, 250, 110, color=MUTED, sw=1.6))
    p.append(line(580, 72, 690, 110, color=FIELD, sw=1.6))

    def column(cx, head, head_col, steps, last_col):
        p.append(text(cx, 124, head, size=13, color=head_col, bold=True))
        bw, bh = 280, 50
        y = 138
        for i, (lab, col, fill, hi) in enumerate(steps):
            x = cx - bw / 2
            sw = 2.4 if hi else 1.6
            p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=sw, rx=8))
            p.append(text(cx, y + bh / 2 + 4, lab, size=11.5,
                          color=col if hi else INK, bold=hi))
            if i < len(steps) - 1:
                p.append(arrow(cx, y + bh + 1, cx, y + bh + 17, color=last_col, sw=2.2))
            y += bh + 18

    column(250, "МІКРОПРОЦЕСОР", MUTED, [
        ("Intel 4004 (1971)", INK, "#fbfbfb", False),
        ("Intel 8080 (1974)", INK, "#fbfbfb", False),
        ("x86 (IBM PC і далі)", INK, "#fbfbfb", False),
        ("Персональний комп'ютер («видимий»)", INK, "#eeeeee", False),
    ], MUTED)

    column(690, "МІКРОКОНТРОЛЕР", FIELD, [
        ("Калькулятор-чип TMS0100 (1971)", INK, "#fbfbfb", False),
        ("TMS1000 (масовий МК, 1974)", INK, "#fbfbfb", False),
        ("8-біт МК (8048·PIC·AVR)", INK, "#fbfbfb", False),
        ("ESP32 («наш герой: МК + радіо»)", FIELD, "#eef6ef", True),
    ], FIELD)

    render(os.path.join(OUT, "lineages.svg"), W, H, *p,
           title="Дві лінії від 1971 року: видимі й невидимі комп'ютери")


# ── hist patents: клубок претензій на «перший» ────────────────────────────────
# Ідея: горизонтальна вісь часу з маркерами-подіями; унизу бокс із розв'язкою
# «перший роздвоюється за визначенням» (червоний / зелений пункти).

def fig_patents():
    W, H = 980, 540
    p = []

    # вісь часу
    axy = 300
    p.append(line(60, axy, 900, axy, color=INK, sw=2.6))
    p.append(arrow(885, axy, 922, axy, color=INK, sw=2.6))

    # події: (рік, x, текст-рядки, над/під, колір)
    events = [
        ("1969", 120, ["Boysel — AL1 (Four-Phase),", "8-біт процесор-чип"], "up", INK),
        ("1970", 280, ["Hyatt — заявка;", "Holt — обчислювач F-14", "(засекречено до 1998)"], "down", MUTED),
        ("1971", 450, ["Intel 4004 ‖ Boone — заявка", "(МП ‖ «мікрокомп'ютер»)"], "up", NEG),
        ("1973", 600, ["Boone — патент 3 757 306", "(комп'ютер на чипі)"], "down", FIELD),
        ("1990", 740, ["Hyatt — патент видано", "(сенсація…)"], "up", MUTED),
        ("1996", 870, ["пріоритет →", "Boone (TI)"], "down", FIELD),
    ]
    for year, x, lines, side, col in events:
        p.append(circle(x, axy, 5, fill=col, stroke=col, sw=0))
        p.append(text(x, axy + (-14 if side == "up" else 22), year, size=12, color=col, bold=True))
        if side == "up":
            ty = axy - 34 - (len(lines) - 1) * 14
            p.append(line(x, axy - 5, x, ty + 4, color=col, sw=1.2, dash="2 3"))
            p.append(mtext(x, ty, lines, size=9.5, color=INK, lh=1.25))
        else:
            ty = axy + 40
            p.append(line(x, axy + 5, x, ty - 12, color=col, sw=1.2, dash="2 3"))
            p.append(mtext(x, ty, lines, size=9.5, color=INK, lh=1.25))

    # розв'язка внизу
    p.append(rect(120, 430, 740, 92, fill=FILL, stroke=INK, sw=1.8, rx=10))
    p.append(text(490, 454, "Розв'язка: «перший» роздвоюється за визначенням",
                  size=13, bold=True))
    p.append(text(140, 482, "• процесор на чипі (продається окремо) → Intel 4004",
                  size=11.5, color=POS, anchor="start", bold=True))
    p.append(text(140, 506, "• комп'ютер на чипі (= мікроконтролер) → Boone / Texas Instruments",
                  size=11.5, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "patents.svg"), W, H, *p,
           title="Клубок претензій на «перший мікропроцесор»")


if __name__ == "__main__":
    fig_what_is_mcu()
    fig_mp_vs_mc_board()
    fig_scale()
    fig_boot()
    fig_spectrum()
    fig_budget()
    fig_timeline()
    fig_calculator()
    fig_mcs4_set()
    fig_mc_vs_mp_die()
    fig_lineages()
    fig_patents()
    print("OK: figures written to", OUT)
