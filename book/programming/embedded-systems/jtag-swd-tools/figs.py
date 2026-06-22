# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── why-special: ПК (видно все) проти МК (запечатаний, мовчить) ───────────────
# Ідея: на ПК програма біжить на тій самій машині — спинив, зазирнув; на МК код
# виконується на окремому чипі, нутро не видно, а впавши, він мовчить.
def fig_why_special():
    W, H = 700, 330
    p = []
    p.append(text(W / 2, 30, "Те саме відлагодження — два світи", size=17, bold=True))

    # ── ПК: прозорий, видно стек, змінні ──
    p.append(text(180, 66, "ПК: програма на вашій машині", size=13, bold=True, color=FIELD))
    p.append(rect(60, 80, 240, 200, fill="#f1fbf4", stroke=FIELD, sw=2))
    # «вікно» зі змінними — видно все
    for i, (nm, vl) in enumerate([("x = 5", True), ("buf[ ] ✓", True), ("стек ✓", True)]):
        p.append(rect(82, 104 + i * 46, 196, 34, fill=BG, stroke="#9cd3b0", sw=1.2))
        p.append(text(180, 126 + i * 46, nm, size=13, color=INK))
    p.append(text(180, 268, "спинити · крок · будь-яка змінна", size=11, color=MUTED, italic=True))

    # ── МК: запечатана коробка, видно лише ніжки ──
    p.append(text(520, 66, "МК: окремий запечатаний чіп", size=13, bold=True, color=POS))
    p.append(rect(420, 80, 220, 200, fill="#1f1f1f", stroke=INK, sw=2))
    p.append(text(530, 150, "?", size=64, bold=True, color="#555", anchor="middle"))
    p.append(text(530, 196, "зсередини не видно", size=12, color="#cfcfcf"))
    p.append(text(530, 218, "впав → мовчить", size=12, color="#e6a6a0"))
    # ніжки чипа
    for i in range(6):
        x = 432 + i * 36
        p.append(line(x, 280, x, 296, color=INK, sw=2))
        p.append(line(x + 18, 80, x + 18, 64, color=INK, sw=2)) if i < 5 else None
    # око, що впирається в стінку
    p.append(text(530, 312, "потрібне вікно в нутро", size=11, color=POS, italic=True))

    render(os.path.join(OUT, "why-special.svg"), W, H, *p)


# ── serial: розкидати println у код → монітор порту на ПК ────────────────────
# Ідея: маркери в коді шлють значення тим самим дротом у монітор; видно, доки чіп
# іде крихтами і де збивається.
def fig_serial():
    W, H = 700, 320
    p = []
    p.append(text(W / 2, 30, "Serial: лишай хлібні крихти, читай у моніторі", size=17, bold=True))

    # код з крихтами
    p.append(rect(50, 60, 250, 210, fill="#1f1f1f", stroke=INK, sw=1.5))
    p.append(text(60, 82, "чіп (ваш код)", size=12, color="#cfcfcf"))
    rows = ['init();',
            'Serial.println("A");',
            'x = read();',
            'Serial.println(x);',
            'step();',
            'Serial.println("B");']
    for i, r in enumerate(rows):
        col = "#7fd49a" if "println" in r else "#cccccc"
        p.append(text(66, 110 + i * 26, r, size=12.5, color=col, anchor="start"))

    # дріт
    p.append(arrow(300, 165, 410, 165, color=POS, sw=2.2))
    p.append(text(355, 153, "один дріт", size=11, color=POS, italic=True))
    p.append(text(355, 184, "(UART)", size=11, color=MUTED, italic=True))

    # монітор порту
    p.append(rect(410, 60, 240, 210, fill="#0c1c34", stroke="#2457d6", sw=1.5))
    p.append(text(420, 82, "монітор порту (ПК)", size=12, color="#9db8f0"))
    out = ["A", "1023", "B", "A", "1023", "B"]
    for i, r in enumerate(out):
        p.append(text(426, 110 + i * 26, "> " + r, size=12.5, color="#a8e6c0", anchor="start"))

    p.append(text(W / 2, 300, "просто й завжди — та сповільнює, змінює час і показує лиш надруковане",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "serial.svg"), W, H, *p)


# ── what-to-print: три види крихт — значення · маркери · помилки ──────────────
def fig_what_to_print():
    W, H = 700, 300
    p = []
    p.append(text(W / 2, 30, "Три види крихт — спершу гіпотеза, тоді крихта", size=17, bold=True))

    cards = [
        ("значення", FIELD, '"x =", x', "перевірити\nприпущення про дані"),
        ("маркери", "#2457d6", '"дійшов сюди"', "куди тече потік\nі де спинився"),
        ("помилки", POS, '"не мало статись"', "гілки, що не\nмали б трапитись"),
    ]
    cw, gap = 196, 22
    x0 = (W - (cw * 3 + gap * 2)) / 2
    for i, (title, col, code, sub) in enumerate(cards):
        x = x0 + i * (cw + gap)
        p.append(rect(x, 70, cw, 150, fill=FILL, stroke=col, sw=2))
        p.append(text(x + cw / 2, 100, title, size=15, bold=True, color=col))
        p.append(rect(x + 16, 116, cw - 32, 36, fill="#1f1f1f", stroke=col, sw=1))
        p.append(text(x + cw / 2, 139, code, size=12.5, color="#a8e6c0"))
        p.append(mtext(x + cw / 2, 178, sub, size=11.5, color=MUTED, lh=1.25))

    p.append(text(W / 2, 256, "поділ навпіл: один маркер посередині → баг далі чи раніше → ділимо ще",
                  size=12, color=INK))
    p.append(text(W / 2, 278, "кожна крихта вдвічі звужує область — двійковий пошук причини",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "what-to-print.svg"), W, H, *p)


# ── jtag: зонд дотягується всередину живого чипа ──────────────────────────────
# Ідея: окремий зонд по відлагоджувальних ніжках (JTAG/SWD) робить чіп прозорим:
# спинити, крок, будь-яка змінна/регістр, точка зупину, сторожок.
def fig_jtag():
    W, H = 700, 330
    p = []
    p.append(text(W / 2, 30, "Апаратний налагоджувач: зонд зазирає в живий чіп", size=17, bold=True))

    # ПК
    p.append(rect(40, 120, 130, 90, fill="#f1fbf4", stroke=FIELD, sw=2))
    p.append(text(105, 160, "ПК", size=14, bold=True, color=FIELD))
    p.append(text(105, 184, "(GDB)", size=12, color=MUTED))
    p.append(arrow(170, 165, 230, 165, color=INK, sw=2))

    # зонд
    p.append(rect(230, 130, 110, 70, fill=FILL, stroke=INK, sw=1.8))
    p.append(text(285, 170, "зонд", size=14, bold=True))
    p.append(arrow(340, 165, 400, 165, color=POS, sw=2.2))
    p.append(text(370, 153, "JTAG/SWD", size=10.5, color=POS, italic=True))

    # чіп — тепер «прозорий», видно нутро
    p.append(rect(400, 90, 250, 175, fill="#0c1c34", stroke="#2457d6", sw=2))
    p.append(text(525, 112, "живий чіп — прозорий", size=12.5, color="#9db8f0"))
    caps = ["спинити (halt)", "крок по рядку (step)",
            "будь-яка змінна й регістр", "точка зупину (breakpoint)",
            "сторожок на дані (watchpoint)"]
    for i, c in enumerate(caps):
        p.append(text(420, 138 + i * 24, "• " + c, size=12, color="#a8e6c0", anchor="start"))
    # ніжки
    for i in range(6):
        x = 412 + i * 40
        p.append(line(x, 265, x, 282, color=INK, sw=2))

    p.append(text(W / 2, 312, "те, що на ПК буденне, тут робить зонд — ціною зайвого заліза й налаштування",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "jtag.svg"), W, H, *p)


# ── serial-vs-jtag: за замовчуванням проти важких випадків ────────────────────
def fig_serial_vs_jtag():
    W, H = 700, 300
    p = []
    p.append(text(W / 2, 30, "Дві снасті — різні випадки", size=17, bold=True))

    # Serial
    p.append(rect(50, 64, 290, 196, fill="#f1fbf4", stroke=FIELD, sw=2))
    p.append(text(195, 92, "Serial — за замовчуванням", size=15, bold=True, color=FIELD))
    for i, c in enumerate(["легка, завжди напохваті", "значення, маркери",
                           "більшість багів (9 із 10)", "без зайвого заліза"]):
        p.append(text(72, 124 + i * 30, "• " + c, size=12.5, color=INK, anchor="start"))

    # JTAG
    p.append(rect(360, 64, 290, 196, fill="#fdf3f2", stroke=POS, sw=2))
    p.append(text(505, 92, "JTAG/SWD — для важких", size=15, bold=True, color=POS))
    for i, c in enumerate(["важка артилерія", "спинити, крок, будь-куди",
                           "аварія до першого друку", "тонкий час, глибокий стан"]):
        p.append(text(382, 124 + i * 30, "• " + c, size=12.5, color=INK, anchor="start"))

    p.append(text(W / 2, 284, "беруть Serial за замовчуванням, JTAG — коли він справді потрібен",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "serial-vs-jtag.svg"), W, H, *p)


# ── decode-crash: адреси backtrace → ваш рядок коду (той самий тулчейн) ───────
# Ідея: чіп друкує паніку з адресами; addr2line + ваш .elf обертають адресу назад
# у файл і рядок. Текст став адресами «туди» — адреси стають текстом «назад».
def fig_decode_crash():
    W, H = 700, 320
    p = []
    p.append(text(W / 2, 30, "Аварію розшифровує той самий тулчейн", size=17, bold=True))

    # паніка з адресами
    p.append(rect(40, 60, 300, 120, fill="#1f1f1f", stroke=POS, sw=1.8))
    p.append(text(54, 84, "чіп друкує паніку:", size=12, color="#e6a6a0", anchor="start"))
    p.append(text(54, 110, "Guru Meditation (LoadProhibited)", size=11.5, color="#cccccc", anchor="start"))
    p.append(text(54, 136, "Backtrace:", size=12, color="#cccccc", anchor="start"))
    p.append(text(54, 160, "0x400d1a3c  0x400d1b08 …", size=12.5, color="#f0c674", anchor="start"))

    # перетворювач
    p.append(arrow(340, 120, 400, 120, color=INK, sw=2))
    p.append(rect(400, 92, 130, 56, fill=FILL, stroke=INK, sw=1.8))
    p.append(text(465, 116, "addr2line", size=13, bold=True))
    p.append(text(465, 137, "+ ваш .elf", size=11.5, color=MUTED))

    # результат — рядок коду
    p.append(line(465, 148, 465, 196, color=FIELD, sw=2))
    p.append(arrow(465, 196, 465, 214, color=FIELD, sw=2.2))
    p.append(rect(330, 222, 270, 56, fill="#f1fbf4", stroke=FIELD, sw=1.8))
    p.append(text(465, 246, "sensor.cpp : 42", size=14, bold=True, color=INK))
    p.append(text(465, 268, "(читання з порожнього покажчика)", size=11, color=MUTED))

    p.append(text(200, 232, "текст → адреси «туди»", size=11.5, color=MUTED, italic=True))
    p.append(text(200, 254, "адреси → текст «назад»", size=11.5, color=FIELD, italic=True))
    render(os.path.join(OUT, "decode-crash.svg"), W, H, *p)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставок цієї теми
# ════════════════════════════════════════════════════════════════════════════

# ── proj-logging / log-anatomy: анатомія рядка + драбина рівнів із порогом ────
def fig_log_anatomy():
    W, H = 700, 380
    p = []
    p.append(text(W / 2, 30, "Лог-рядок і драбина рівнів", size=17, bold=True))

    # анатомія рядка: час · рівень · мітка · повідомлення
    parts = [("00:12.043", "час", "#2457d6"), ("INFO", "рівень", POS),
             ("[net]", "мітка", FIELD), ("link up", "повідомлення", INK)]
    x = 60
    for val, lab, col in parts:
        w = max(96, text_width(val, 13, True) + 24)
        p.append(rect(x, 64, w, 38, fill=FILL, stroke=col, sw=1.6))
        p.append(text(x + w / 2, 88, val, size=13, bold=True, color=INK))
        p.append(text(x + w / 2, 120, lab, size=11, color=col, italic=True))
        x += w + 12

    # драбина рівнів із порогом
    p.append(text(W / 2, 168, "поріг ділить балакучість", size=12.5, bold=True))
    levels = ["ERROR", "WARN", "INFO", "DEBUG", "VERBOSE"]
    bx, by, bw, bh = 200, 184, 300, 30
    thr = 2  # поріг між INFO та DEBUG
    for i, lv in enumerate(levels):
        y = by + i * (bh + 6)
        shown = i <= thr
        fill = "#f1fbf4" if shown else "#f0f0f0"
        col = INK if shown else MUTED
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=col, sw=1.3))
        p.append(text(bx + 14, y + 20, lv, size=12.5, color=col, anchor="start", bold=shown))
        p.append(text(bx + bw - 14, y + 20, "показуємо" if shown else "мовчимо",
                      size=11, color=col, anchor="end", italic=True))
    # лінія порога
    ty = by + (thr + 1) * (bh + 6) - 3
    p.append(line(bx - 16, ty, bx + bw + 16, ty, color=POS, sw=2, dash="6 4"))
    p.append(text(bx - 22, ty + 4, "поріг", size=11, color=POS, anchor="end", bold=True))

    render(os.path.join(OUT, "log-anatomy.svg"), W, H, *p)


# ── proj-logging / ring-log: кільцевий буфер, дамп при аварії ─────────────────
def fig_ring_log():
    W, H = 700, 320
    p = []
    p.append(text(W / 2, 30, "Кільцевий лог: останні слова пристрою", size=17, bold=True))

    cx, cy, r = 220, 180, 96
    n = 8
    import math
    p.append(circle(cx, cy, r, fill="none", stroke=MUTED, sw=1.2))
    for i in range(n):
        a = -math.pi / 2 + i * 2 * math.pi / n
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        newest = (i == n - 1)
        oldest = (i == 0)
        col = POS if newest else (MUTED if oldest else INK)
        p.append(circle(x, y, 17, fill="#fdf3f2" if newest else FILL, stroke=col, sw=2))
        p.append(text(x, y + 5, str(i), size=13, color=col, bold=newest))
    # стрілка «по колу»
    p.append(text(cx, cy - 4, "по колу", size=12, color=MUTED, italic=True))
    p.append(text(cx, cy + 16, "нове затирає", size=11, color=MUTED, italic=True))
    p.append(text(cx, cy + 34, "найстаріше", size=11, color=MUTED, italic=True))
    p.append(text(cx + r + 8, cy - r + 6, "новий", size=10.5, color=POS, anchor="start", bold=True))
    p.append(text(cx - r - 8, cy - r + 6, "старий", size=10.5, color=MUTED, anchor="end"))

    # дамп при аварії
    p.append(text(440, 78, "аварія →", size=14, bold=True, color=POS))
    p.append(arrow(360, 180, 430, 180, color=POS, sw=2.2))
    p.append(rect(430, 100, 230, 170, fill="#0c1c34", stroke="#2457d6", sw=1.6))
    p.append(text(444, 124, "скидаємо все кільце:", size=12, color="#9db8f0", anchor="start"))
    for i, ln in enumerate(["…", "read sensor", "i2c timeout", "retry", "PANIC"]):
        col = "#e6a6a0" if ln == "PANIC" else "#a8e6c0"
        p.append(text(444, 150 + i * 24, "> " + ln, size=12, color=col, anchor="start"))

    p.append(text(W / 2, 304, "передісторія збою жила в RAM, а не лише на екрані",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "ring-log.svg"), W, H, *p)


# ── proj-binary-logging / binary-vs-text: друк тексту проти ID + сирих байтів ─
def fig_binary_vs_text():
    W, H = 700, 340
    p = []
    p.append(text(W / 2, 28, "Текстовий друк проти бінарного логу", size=17, bold=True))

    # ── зверху: текст ──
    p.append(text(60, 62, "текст: усе на чипі", size=13, bold=True, color=POS, anchor="start"))
    p.append(rect(60, 74, 150, 52, fill="#1f1f1f", stroke=POS, sw=1.4))
    p.append(text(135, 96, 'шаблон у Flash', size=11.5, color="#cccccc"))
    p.append(text(135, 114, '"temp=%d mV"', size=11, color="#f0c674"))
    p.append(arrow(210, 100, 256, 100, color=INK, sw=1.8))
    p.append(rect(256, 74, 110, 52, fill=FILL, stroke=POS, sw=1.4))
    p.append(text(311, 96, "printf на CPU", size=11.5))
    p.append(text(311, 114, "(ділення /10)", size=10.5, color=MUTED))
    p.append(arrow(366, 100, 412, 100, color=POS, sw=2))
    p.append(rect(412, 78, 240, 44, fill="#0c1c34", stroke=POS, sw=1.4))
    p.append(text(532, 105, '"temp=2350 mV"  ~25 Б', size=12, color="#e6a6a0"))

    # ── знизу: бінарний ──
    p.append(text(60, 178, "бінарний: текст збирає ХОСТ", size=13, bold=True, color=FIELD, anchor="start"))
    p.append(rect(60, 190, 150, 52, fill="#1f1f1f", stroke=FIELD, sw=1.4))
    p.append(text(135, 212, "у Flash лише ID", size=11.5, color="#cccccc"))
    p.append(text(135, 230, "0, 1, 2 …", size=11, color="#7fd49a"))
    p.append(arrow(210, 216, 256, 216, color=FIELD, sw=2))
    p.append(rect(256, 190, 110, 52, fill=FILL, stroke=FIELD, sw=1.4))
    p.append(text(311, 212, "чіп шле байти", size=11.5))
    p.append(text(311, 230, "[ID·аргум.]", size=10.5, color=MUTED))
    p.append(arrow(366, 216, 412, 216, color=FIELD, sw=2.2))
    p.append(rect(412, 194, 110, 44, fill="#0c1c34", stroke=FIELD, sw=1.4))
    p.append(text(467, 221, "~6 Б у дріт", size=12, color="#a8e6c0"))
    p.append(arrow(522, 216, 560, 216, color=INK, sw=1.8))
    p.append(rect(560, 190, 92, 52, fill="#f1fbf4", stroke=FIELD, sw=1.6))
    p.append(text(606, 210, "ХОСТ", size=12, bold=True, color=FIELD))
    p.append(text(606, 230, "+ .elf", size=11, color=MUTED))

    p.append(text(W / 2, 290, "форматування переїхало з чипа на ПК; трафік у дроті впав учетверо",
                  size=12, color=INK))
    p.append(text(W / 2, 314, "ціна: сирий потік без декодера й .elf не прочитати",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "binary-vs-text.svg"), W, H, *p)


# ── proj-binary-logging / binary-frame: один кадр побайтно ───────────────────
def fig_binary_frame():
    W, H = 700, 280
    p = []
    p.append(text(W / 2, 30, "Один бінарний кадр — побайтно", size=17, bold=True))

    cells = [("0x7E", "маркер-\nпочаток", "#2457d6"),
             ("0x01", "ID\nшаблону", FIELD),
             ("0x02", "довжина\nn", MUTED),
             ("0x2E", "арг. байт 0", POS),
             ("0x09", "арг. байт 1", POS),
             ("XOR", "контроль", "#2457d6")]
    cw, gap = 100, 6
    x0 = (W - (cw * len(cells) + gap * (len(cells) - 1))) / 2
    for i, (val, lab, col) in enumerate(cells):
        x = x0 + i * (cw + gap)
        p.append(rect(x, 84, cw, 50, fill=FILL, stroke=col, sw=1.8))
        p.append(text(x + cw / 2, 114, val, size=14, bold=True, color=INK))
        p.append(mtext(x + cw / 2, 152, lab, size=10.5, color=col))

    # пояснення little-endian
    midx = x0 + 3 * (cw + gap) + cw - gap / 2
    p.append(line(midx, 84, midx, 196, color=POS, sw=1, dash="4 4"))
    p.append(text(W / 2, 214, "int16_t 2350 = 0x092E у пам'яті → [0x2E, 0x09] (little-endian, НЕ ASCII)",
                  size=12, color=INK))
    p.append(text(W / 2, 244, "маркер і контроль дають ловити межі кадру й помилки на шумній лінії",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "binary-frame.svg"), W, H, *p)


# ── comp-debug-probes / probe-link: зонд між ПК і чипом, GDB-сервер ───────────
def fig_probe_link():
    W, H = 700, 280
    p = []
    p.append(text(W / 2, 30, "Зонд керує ядром — не «слухає друк»", size=17, bold=True))

    # ПК + GDB
    p.append(rect(50, 96, 150, 90, fill="#f1fbf4", stroke=FIELD, sw=2))
    p.append(text(125, 134, "ПК", size=14, bold=True, color=FIELD))
    p.append(text(125, 158, "GDB", size=12.5, color=INK))
    p.append(arrow(200, 141, 256, 141, color=INK, sw=2))
    p.append(text(228, 129, "USB", size=10.5, color=MUTED, italic=True))

    # зонд із GDB-сервером
    p.append(rect(256, 90, 170, 102, fill=FILL, stroke=INK, sw=2))
    p.append(text(341, 120, "зонд", size=15, bold=True))
    p.append(rect(272, 132, 138, 44, fill="#eef4ff", stroke="#2457d6", sw=1.3))
    p.append(text(341, 159, "GDB-сервер", size=12.5, color=INK))
    p.append(arrow(426, 141, 482, 141, color=POS, sw=2.2))
    p.append(text(454, 129, "JTAG/SWD", size=10, color=POS, italic=True))

    # чіп — порт відлагодження
    p.append(rect(482, 90, 168, 102, fill="#0c1c34", stroke="#2457d6", sw=2))
    p.append(text(566, 116, "чіп", size=14, bold=True, color="#9db8f0"))
    for i, c in enumerate(["спинити · крок", "точки зупину", "пам'ять, регістри"]):
        p.append(text(498, 140 + i * 20, "• " + c, size=11.5, color="#a8e6c0", anchor="start"))

    p.append(text(W / 2, 232, "усе наживо, без жодного print у коді — на відміну від USB-UART моста",
                  size=12, color=INK))
    p.append(text(W / 2, 258, "усередині зонда — GDB-сервер, до якого під'єднується GDB на ПК",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "probe-link.svg"), W, H, *p)


# ── comp-debug-probes / jtag-vs-swd: 4 лінії проти 2 ─────────────────────────
def fig_jtag_vs_swd():
    W, H = 700, 300
    p = []
    p.append(text(W / 2, 30, "JTAG (4 лінії) проти SWD (2 лінії)", size=17, bold=True))

    # JTAG
    p.append(rect(50, 64, 290, 200, fill="#fdf3f2", stroke=POS, sw=2))
    p.append(text(195, 92, "JTAG — старша, потужніша", size=14, bold=True, color=POS))
    for i, (sig, lab) in enumerate([("TCK", "такт"), ("TMS", "вибір стану"),
                                    ("TDI", "дані в"), ("TDO", "дані з")]):
        y = 116 + i * 30
        p.append(rect(72, y, 70, 24, fill=BG, stroke=POS, sw=1.2))
        p.append(text(107, y + 17, sig, size=12.5, bold=True, color=INK))
        p.append(text(154, y + 17, lab, size=11.5, color=MUTED, anchor="start"))
    p.append(text(195, 250, "+ земля · можна зчіпляти чипи в ланцюг", size=10.5, color=MUTED, italic=True))

    # SWD
    p.append(rect(360, 64, 290, 200, fill="#f1fbf4", stroke=FIELD, sw=2))
    p.append(text(505, 92, "SWD — компактна (ARM)", size=14, bold=True, color=FIELD))
    for i, (sig, lab) in enumerate([("SWCLK", "такт"), ("SWDIO", "дані (двобічно)")]):
        y = 128 + i * 34
        p.append(rect(382, y, 84, 26, fill=BG, stroke=FIELD, sw=1.2))
        p.append(text(424, y + 18, sig, size=12.5, bold=True, color=INK))
        p.append(text(478, y + 18, lab, size=11.5, color=MUTED, anchor="start"))
    p.append(text(505, 222, "+ земля · ланцюг зчепити не можна", size=10.5, color=MUTED, italic=True))
    p.append(text(505, 244, "ESP32 — по JTAG; ARM Cortex-M — по SWD", size=10.5, color=INK))

    p.append(text(W / 2, 288, "пастка ESP32: піни JTAG — це й звичайні GPIO; зайняв їх — JTAG зник",
                  size=11, color=POS, italic=True))
    render(os.path.join(OUT, "jtag-vs-swd.svg"), W, H, *p)


if __name__ == "__main__":
    # стаття
    fig_why_special()
    fig_serial()
    fig_what_to_print()
    fig_jtag()
    fig_serial_vs_jtag()
    fig_decode_crash()
    # вставки
    fig_log_anatomy()
    fig_ring_log()
    fig_binary_vs_text()
    fig_binary_frame()
    fig_probe_link()
    fig_jtag_vs_swd()
    print("ok: 12 figures ->", OUT)
