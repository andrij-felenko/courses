# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8860b"   # акцент «увага» (відкладена робота, подія)


# ── isr-on-hold: поки ISR працює, усе чекає ───────────────────────────────────
# Ідея: смуга часу основного коду розривається блоком ISR; інша подія, що прийшла
# під час ISR, обслуговується лише після його завершення — видно «висіння».

def fig_on_hold():
    W, H = 720, 250
    p = []
    y = 120
    # смуга основного коду
    p.append(line(70, y, 270, y, color=NEG, sw=3))
    p.append(text(70, y - 16, "основний код", size=11, color=NEG, anchor="start", bold=True))
    # блок ISR
    p.append(rect(270, y - 18, 250, 36, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(395, y + 5, "обробник (ISR) виконується", size=11, color=POS, bold=True))
    # продовження основного коду
    p.append(line(520, y, 690, y, color=NEG, sw=3))
    p.append(text(605, y - 10, "далі", size=10, color=NEG))

    # інша подія прийшла під час ISR
    p.append(line(360, 196, 360, y + 18, color=MUTED, sw=2, dash="3 3"))
    p.append(circle(360, 196, 4, fill=GOLD, stroke=GOLD, sw=0))
    p.append(text(360, 216, "інша подія прийшла тут…", size=10, color=GOLD, bold=True))
    p.append(arrow(360, 188, 520, 188, color=GOLD, sw=2))
    p.append(text(528, 192, "…обслужать аж тут", size=10, color=GOLD, anchor="start", bold=True))
    p.append(line(520, 196, 520, y + 18, color=GOLD, sw=1.4, dash="3 3"))

    render(os.path.join(OUT, "isr-on-hold.svg"), W, H, *p,
           title="Доки обробник працює, основний код і інші події чекають")


# ── short-vs-long: короткий встигає, довгий губить події ───────────────────────
# Ідея: дві часові осі з трьома однаковими подіями. Угорі короткий ISR опрацьовує
# кожну; унизу довгий ISR ще зайнятий першою — друга й третя губляться.

def fig_short_vs_long():
    W, H = 720, 300
    p = []
    xs = [180, 330, 480]

    # короткий
    p.append(text(70, 80, "Короткий ISR", size=12, color=FIELD, anchor="start", bold=True))
    yt = 110
    p.append(line(120, yt, 650, yt, color=INK, sw=1.6))
    for x in xs:
        p.append(line(x, yt - 30, x, yt, color=FIELD, sw=2))
        p.append(circle(x, yt - 30, 4, fill=FIELD, stroke=FIELD, sw=0))
        p.append(rect(x, yt - 12, 24, 24, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(385, yt + 30, "кожну подію опрацьовано вмить", size=10, color=FIELD, bold=True))

    # довгий
    p.append(text(70, 200, "Довгий ISR", size=12, color=POS, anchor="start", bold=True))
    yb = 230
    p.append(line(120, yb, 650, yb, color=INK, sw=1.6))
    for x in xs:
        col = FIELD if x == xs[0] else POS
        p.append(line(x, yb - 30, x, yb, color=col, sw=2))
        p.append(circle(x, yb - 30, 4, fill=col, stroke=col, sw=0))
    # довгий блок-обробник накриває другу й третю позначки
    p.append(rect(xs[0], yb - 13, 170, 26, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(xs[0] + 85, yb + 4, "довгий обробник", size=9.5, color=POS, bold=True))
    p.append(text(410, yb - 40, "ці дві — проґавлено", size=10, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "short-vs-long.svg"), W, H, *p,
           title="Короткий обробник встигає все; довгий губить наступні події")


# ── dos-donts: що можна й чого не можна в ISR ─────────────────────────────────
# Ідея: дві колонки — зелена «можна» (швидке/безпечне) проти червоної «не можна»
# (повільне/блокувальне). Правило внизу: сумнів — у loop().

def fig_dos_donts():
    W, H = 720, 320
    p = []
    can = [
        "прапорець: flag = true;",
        "лічильник: count++;",
        "читання / скидання регістра",
        "мітка часу: micros()",
        "подія в чергу (…FromISR)",
    ]
    cant = [
        "delay() чи активне очікування",
        "Serial.print(…) — повільно",
        "мережа, файли, блокувальний I2C/SPI",
        "malloc / new (замок купи)",
        "важка математика, float",
    ]
    # ліва колонка — можна
    p.append(rect(40, 70, 310, 210, fill="#f3faf4", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(195, 96, "МОЖНА", size=13, color=FIELD, bold=True))
    for i, s in enumerate(can):
        yy = 130 + i * 30
        p.append(text(62, yy, "✓", size=13, color=FIELD, anchor="start", bold=True))
        p.append(text(86, yy, s, size=10.5, color=INK, anchor="start"))
    # права колонка — не можна
    p.append(rect(370, 70, 310, 210, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    p.append(text(525, 96, "НЕ МОЖНА", size=13, color=POS, bold=True))
    for i, s in enumerate(cant):
        yy = 130 + i * 30
        p.append(text(392, yy, "✗", size=13, color=POS, anchor="start", bold=True))
        p.append(text(416, yy, s, size=10.5, color=INK, anchor="start"))

    p.append(text(W / 2, 304, "Сумнів — виноси в loop(): обробник лише ВІДМІЧАЄ подію, а не обробляє її",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "dos-donts.svg"), W, H, *p,
           title="Що в обробнику можна, а чого — ні")


# ── deferred-pattern: відмітити в ISR, обробити в loop ─────────────────────────
# Ідея: червоний блок ISR (мікросекунди, лише прапорець) сигналить зеленому
# блоку loop()/задачі (важка робота без поспіху).

def fig_deferred():
    W, H = 720, 240
    p = []
    y = 130
    # ISR
    b1 = fitbox(60, y - 50, 230, 100,
                "обробник (ISR)\n\nflag = true;\n\nмікросекунди",
                size=11, fill="#fdecea", stroke=POS, sw=1.8, color=INK, bold=True)
    p.append(b1)
    # стрілка-прапорець
    p.append(arrow(290, y, 400, y, color=GOLD, sw=2.6))
    p.append(text(345, y - 12, "прапорець", size=9.5, color=GOLD, bold=True))
    # loop
    b2 = fitbox(400, y - 50, 260, 100,
                "loop() / задача\n\nif (flag) { … }\n\nдрук, обчислення, мережа",
                size=11, fill="#eafaf0", stroke=FIELD, sw=1.8, color=INK, bold=True)
    p.append(b2)

    p.append(text(W / 2, 214, "ISR не блокує систему; важка робота діється потім, без поспіху",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "deferred-pattern.svg"), W, H, *p,
           title="Золотий патерн: обробник відмічає, loop() робить важке")


# ── iram-attr: обробник у RAM, доступній завжди ───────────────────────────────
# Ідея: ліворуч небезпека (ISR у флеші, флеш зайнятий → краш); праворуч рятунок
# (ISR в IRAM, зайнятість флеша байдужа).

def fig_iram():
    W, H = 720, 300
    p = []
    # ліворуч — ризик
    p.append(rect(40, 70, 310, 200, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    p.append(text(195, 96, "Без IRAM_ATTR — ризик", size=12, color=POS, bold=True))
    p.append(fitbox(70, 120, 120, 70, "флеш\n(тут код,\nтут ISR)", size=10, fill=BG, stroke=INK, sw=1.5, color=INK, bold=True))
    p.append(fitbox(210, 120, 110, 70, "флеш\nЗАЙНЯТА\n(запис/кеш)", size=9.5, fill="#fdecea", stroke=POS, sw=1.5, color=POS, bold=True))
    p.append(arrow(130, 210, 130, 196, color=POS, sw=2))
    p.append(text(195, 232, "переривання → код ISR недосяжний", size=9.5, color=INK))
    p.append(text(195, 252, "→ ЗБІЙ (краш)", size=11, color=POS, bold=True))
    # праворуч — рятунок
    p.append(rect(370, 70, 310, 200, fill="#f3faf4", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(525, 96, "З IRAM_ATTR — надійно", size=12, color=FIELD, bold=True))
    p.append(fitbox(400, 120, 120, 70, "IRAM (ОЗП)\nISR тут —\nзавжди доступний", size=9.5, fill="#eafaf0", stroke=FIELD, sw=1.5, color=FIELD, bold=True))
    p.append(fitbox(540, 120, 110, 70, "флеш\nЗАЙНЯТА —\nбайдуже", size=9.5, fill=BG, stroke=INK, sw=1.5, color=INK, bold=True))
    p.append(text(525, 232, "void IRAM_ATTR myISR() { … }", size=10.5, color=INK, bold=True))
    p.append(text(525, 252, "слово кладе обробник у швидку RAM", size=9.5, color=MUTED))

    render(os.path.join(OUT, "iram-attr.svg"), W, H, *p,
           title="IRAM_ATTR кладе обробник у RAM, доступну завжди")


# ── isr-anatomy: чотири ознаки доброго ISR ────────────────────────────────────
# Ідея: код-блок із короткого ISR у центрі, під ним три картки-ознаки
# (volatile, IRAM_ATTR, коротке тіло) — четверта (важке в loop) як підпис.

def fig_anatomy():
    W, H = 720, 320
    p = []
    # код-блок (темний)
    p.append(rect(110, 70, 500, 120, fill="#0f1115", stroke=INK, sw=1.6, rx=10))
    code = [
        "volatile uint32_t pulses = 0;",
        "void IRAM_ATTR onPulse() {",
        "  pulses++;",
        "}",
    ]
    for i, ln in enumerate(code):
        p.append('<text x="140" y="%d" font-family="Consolas, monospace" '
                 'font-size="15" fill="#e8e8e8" font-weight="bold">%s</text>'
                 % (102 + i * 26, esc(ln)))

    cards = [
        (60, GOLD, "1 · volatile", "спільну змінну\nне «оптимізують»"),
        (270, NEG, "2 · IRAM_ATTR", "обробник у RAM —\nпрацює при зайнятому флеші"),
        (480, FIELD, "3 · коротке тіло", "лише лічильник;\nжодних delay/Serial/malloc"),
    ]
    for x, col, head, body in cards:
        p.append(fitbox(x, 220, 180, 76, head + "\n" + body, size=10, fill=BG, stroke=col, sw=1.6, color=col, bold=True))

    p.append(text(W / 2, 312, "4 · уся важка робота винесена в loop()", size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "isr-anatomy.svg"), W, H, *p,
           title="Анатомія правильного обробника")


# ══ Фігури вставок ════════════════════════════════════════════════════════════

# ── two-halves: верхня (коротка) і нижня (важка) половини обробника ────────────
def fig_two_halves():
    W, H = 720, 280
    p = []
    # верхня половина
    p.append(rect(50, 70, 360, 90, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    p.append(text(230, 94, "Верхня половина (обробник) — коротка", size=11.5, color=FIELD, bold=True))
    for i, s in enumerate(["підтвердити залізо", "схопити критичне (час, байт)", "відмітити «є робота» → вийти"]):
        p.append(text(230, 116 + i * 16, "• " + s, size=9.6, color=INK))
    # стрілка-сигнал
    p.append(arrow(230, 160, 230, 188, color=POS, sw=2.2))
    p.append(text(230, 178, "сигнал: прапорець / черга / задача", size=9, color=POS, bold=True))
    # нижня половина
    p.append(rect(50, 190, 360, 76, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    p.append(text(230, 214, "Нижня половина (loop / задача)", size=11.5, color=NEG, bold=True))
    p.append(text(230, 236, "розбір пакета, екран, запис у Flash, математика —", size=9.4, color=INK))
    p.append(text(230, 252, "на дозвіллі, з увімкненими перериваннями", size=9.4, color=MUTED))
    # пояснення збоку
    p.append(fitbox(440, 90, 240, 150,
                    "Чому так\n\nОбробник блокує все,\nпоки триває. Тож у ньому —\nлиш мінімум, а важке\nвиносимо «вниз», де воно\nнікому не заважає й може\nчекати, рахувати скільки треба.",
                    size=9.6, fill=BG, stroke=MUTED, sw=1.4, color=INK))

    render(os.path.join(OUT, "two-halves.svg"), W, H, *p,
           title="Дві половини обробника: коротка зверху, важка знизу")


# ── three-forms: прапорець → черга → задача RTOS ──────────────────────────────
def fig_three_forms():
    W, H = 720, 260
    p = []
    cards = [
        (40, FIELD, "#eafaf0", "Прапорець", "обробник ставить,\nloop перевіряє", "одна подія"),
        (260, NEG, "#eaf0fd", "Черга подій", "обробник кладе в кільце,\nloop розбирає", "потік подій"),
        (480, GOLD, "#fdf3e0", "Задача (RTOS)", "обробник будить задачу,\nвона робить важке", "структурована робота"),
    ]
    for x, col, fill, head, body, tag in cards:
        p.append(rect(x, 80, 200, 130, fill=fill, stroke=col, sw=2, rx=12))
        p.append(text(x + 100, 108, head, size=13, color=col, bold=True))
        for i, ln in enumerate(body.split("\n")):
            p.append(text(x + 100, 138 + i * 16, ln, size=9.6, color=INK))
        p.append(text(x + 100, 190, tag, size=9.4, color=MUTED, bold=True))
    p.append(arrow(242, 145, 258, 145, color=MUTED, sw=2))
    p.append(arrow(462, 145, 478, 145, color=MUTED, sw=2))
    p.append(text(W / 2, 242, "Що важча робота — то правіше; суть одна: обробник лише сигналить, робота — поза ним",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "three-forms.svg"), W, H, *p,
           title="Три способи відкласти роботу — від простого до потужного")


# ── reentrancy: один стан — два проходи ───────────────────────────────────────
def fig_reentrancy():
    W, H = 720, 300
    p = []
    # дві осі
    p.append(text(60, 78, "loop()", size=12, color=NEG, anchor="start", bold=True))
    p.append(text(60, 178, "обробник", size=12, color=POS, anchor="start", bold=True))
    p.append(line(60, 95, 660, 95, color=NEG, sw=2.2))
    p.append(line(60, 175, 660, 175, color=POS, sw=2.2))
    # виклик у loop
    p.append(rect(120, 81, 200, 28, fill="#eaf0fd", stroke=NEG, sw=2, rx=6))
    p.append(text(220, 100, "strtok / malloc (у loop)", size=11, color=NEG))
    # обробник влітає
    p.append(line(250, 95, 250, 161, color=POS, sw=1.8, dash="5 4"))
    p.append(text(250, 132, "обробник влітає", size=10, color=POS, bold=True))
    p.append(rect(250, 161, 190, 28, fill="#fdecea", stroke=POS, sw=2, rx=6))
    p.append(text(345, 180, "та сама strtok / malloc", size=11, color=POS))
    # спільний стан
    sb = fitbox(330, 110, 130, 56, "Спільний стан:\nстатичний *ptr\n(замок купи)", size=10, fill="#fdf3e0", stroke=GOLD, sw=1.8, color=INK)
    p.append(sb)
    p.append(arrow(250, 109, 360, 124, color=NEG, sw=1.6))
    p.append(arrow(360, 161, 395, 166, color=POS, sw=1.6))
    p.append(text(560, 78, "стан затерто", size=10, color=POS, anchor="middle", bold=True))
    # підсумок
    p.append(rect(150, 230, 420, 30, fill="#fdecea", stroke=POS, sw=1.6, rx=6))
    p.append(text(360, 250, "Зіпсовані дані: не два примірники стану, а ОДИН на двох", size=10.5, color=INK))

    render(os.path.join(OUT, "reentrancy.svg"), W, H, *p,
           title="Нереентерабельність: один стан — два проходи")


# ── unsafe-table: чому виклики небезпечні і чим замінити ───────────────────────
def fig_unsafe_table():
    W, H = 760, 320
    p = []
    cols = [("Функція", INK, 30, 170), ("Чому небезпечна в обробнику", POS, 210, 270), ("Безпечна заміна", FIELD, 490, 250)]
    # шапка
    for head, col, x, w in cols:
        p.append(rect(x, 50, w, 32, fill=FILL, stroke=col, sw=2, rx=5))
        p.append(text(x + w / 2, 71, head, size=11.5, color=col, bold=True))
    rows = [
        ("strtok", "статичний буфер:\nзберігає *ptr між викликами", "парсити в loop();\nабо strtok_r (лише в loop)"),
        ("malloc / new / String", "замок купи:\nна FreeRTOS — збій", "буфер фікс. розміру,\nвиділений у setup()"),
        ("printf / Serial.print", "внутр. буфер + malloc,\nдо того ж повільно", "прапорець/черга в обробнику,\nдрук у loop()"),
        ("gmtime / localtime", "статичний буфер\n(errno, результат)", "localtime_r у loop(),\nне в обробнику"),
    ]
    y = 90
    for fn, why, fix in rows:
        p.append(fitbox(30, y, 170, 50, fn, size=11, fill=FILL, stroke=INK, sw=1, color=INK, bold=True))
        p.append(fitbox(210, y, 270, 50, why, size=10, fill="#fdf6f5", stroke=POS, sw=1, color=INK))
        p.append(fitbox(490, y, 250, 50, fix, size=10, fill="#f3faf4", stroke=FIELD, sw=1, color=INK))
        y += 54
    p.append(text(W / 2, 312, "Дивись не на швидкість, а на середній стовпець: прихований стан між викликами — ось небезпека",
                  size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "unsafe-table.svg"), W, H, *p,
           title="Чому популярні виклики небезпечні в обробнику — і чим їх замінити")


if __name__ == "__main__":
    fig_on_hold()
    fig_short_vs_long()
    fig_dos_donts()
    fig_deferred()
    fig_iram()
    fig_anatomy()
    fig_two_halves()
    fig_three_forms()
    fig_reentrancy()
    fig_unsafe_table()
    print("OK: figures written to", OUT)
