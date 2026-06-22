# -*- coding: utf-8 -*-
"""Фігури до теми «Асинхронна передача» та її історичної вставки.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

ORANGE = "#e67e22"


# ── допоміжне: цифровий меандр як ламана ─────────────────────────────────────
def wave(x0, y_hi, y_lo, bits, unit, color=INK, sw=2.4):
    """Ламана-сигнал: bits — список 0/1; повертає список фрагментів."""
    out = []
    x = x0
    prev_y = None
    for b in bits:
        y = y_lo if b else y_hi
        if prev_y is not None and prev_y != y:
            out.append(line(x, prev_y, x, y, color=color, sw=sw))
        out.append(line(x, y, x + unit, y, color=color, sw=sw))
        prev_y = y
        x += unit
    return out


# ════════════════════════════════════════════════════════════════════════════
#  СТАТТЯ
# ════════════════════════════════════════════════════════════════════════════

# ── 1. Паралельно проти послідовно ──────────────────────────────────────────
def fig_parallel_serial():
    W, H = 760, 430
    f = [text(W / 2, 26, "Той самий байт: вісім дротів за такт — чи один дріт за вісім тактів",
              size=15, bold=True)]

    # розділювач
    f.append(line(380, 60, 380, 360, color="#d0d4d8", sw=1.2, dash="4,4"))

    # --- ліворуч: паралельно ---
    f.append(text(195, 60, "Паралельно", size=14, bold=True, color=NEG))
    for i in range(8):
        y = 95 + i * 26
        f.append(line(80, y, 300, y, color=INK, sw=2.0))
        f.append(text(72, y + 4, "D%d" % i, size=10, color=MUTED, anchor="end"))
    # момент знімання t0
    f.append(line(300, 88, 300, 290, color=POS, sw=1.6, dash="3,3"))
    f.append(text(300, 308, "усе в мить t₀", size=11, color=POS))
    f.append(text(195, 338, "8 ліній даних + земля — швидко,", size=11.5, anchor="middle"))
    f.append(text(195, 354, "та дорого за дротами", size=11.5, anchor="middle", color=NEG))

    # --- праворуч: послідовно ---
    f.append(text(575, 60, "Послідовно", size=14, bold=True, color=FIELD))
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    f.extend(wave(450, 110, 160, bits, unit=30, color=FIELD))
    for i in range(8):
        f.append(text(450 + 30 * i + 15, 182, "b%d" % i, size=9.5, color=MUTED))
    f.append(text(575, 210, "одна лінія, біти по черзі в часі", size=11.5, anchor="middle"))
    f.append(text(575, 338, "1 лінія даних — дешево за дротами,", size=11.5, anchor="middle"))
    f.append(text(575, 354, "ціна — час (8 інтервалів на байт)", size=11.5, anchor="middle", color=FIELD))

    render(os.path.join(IMG, "parallel-serial.svg"), W, H, *f)


# ── 2. Перекіс (skew) ───────────────────────────────────────────────────────
def fig_skew():
    W, H = 760, 470
    f = [text(W / 2, 26, "Лінії стартують разом — а приходять урізнобій (перекіс)",
              size=15, bold=True)]

    unit = 70
    x0 = 110
    # на передавачі — усі міняються одночасно (зелена опорна лінія)
    f.append(text(60, 70, "Передавач", size=13, bold=True, color=MUTED, anchor="start"))
    f.append(line(x0, 95, x0, 250, color=FIELD, sw=1.6, dash="4,3"))
    f.append(text(x0, 86, "усі міняються разом", size=10.5, color=FIELD))

    rows = [("D0", 0), ("D1", 10), ("D2", 26), ("D3", 40)]
    base = 110
    for name, delay in rows:
        y_hi = base
        y_lo = base + 24
        # фронт спізнюється на delay
        f.append(line(x0, y_hi, x0 + delay, y_hi, color=INK, sw=2.2))
        f.append(line(x0 + delay, y_hi, x0 + delay, y_lo, color=INK, sw=2.2))
        f.append(line(x0 + delay, y_lo, x0 + 3 * unit, y_lo, color=INK, sw=2.2))
        f.append(text(x0 - 8, base + 14, name, size=10.5, color=MUTED, anchor="end"))
        base += 46

    # момент вибірки на приймачі
    sx = x0 + 28
    f.append(line(sx, 95, sx, 300, color=POS, sw=1.8, dash="3,3"))
    f.append(text(sx + 6, 92, "мить вибірки", size=11, color=POS, anchor="start"))
    f.append(text(sx + 6, 312, "D0,D1 уже нові, D2,D3 ще старі → читається суміш",
                  size=11, color=POS, anchor="start"))

    box = fitbox(70, 350, 620, 96, [
                 "Вісім дротів ніколи не однакові: різна довжина, ємність, опір — тож фронт по",
                 "кожному біжить із трохи різною затримкою. Поки інтервал на біт довгий, це",
                 "дрібниця. Та що вищий темп — то коротший біт, і коли він стає сумірний із",
                 "розкидом затримок, біти одного стовпчика прибувають врізнобій, і приймач",
                 "знімає суміш старого й нового байта. Одна послідовна лінія цієї біди не має."],
                 size=12, fill="#fdecea", stroke=POS)
    f.append(box)
    render(os.path.join(IMG, "skew.svg"), W, H, *f)


# ── 3. Синхронно: окремий дріт такту ────────────────────────────────────────
def fig_sync():
    W, H = 760, 380
    f = [text(W / 2, 26, "Синхронно: окремий дріт такту вказує мить кожного біта",
              size=15, bold=True)]

    unit = 64
    x0 = 110
    nbits = 8
    # лінія ТАКТ (меандр повних періодів)
    f.append(text(x0 - 12, 86, "ТАКТ", size=12, bold=True, color=NEG, anchor="end"))
    clk = []
    for i in range(nbits):
        clk += [1, 0]
    f.extend(wave(x0, 70, 100, clk, unit=unit / 2.0, color=NEG))

    # лінія ДАНІ
    f.append(text(x0 - 12, 170, "ДАНІ", size=12, bold=True, color=INK, anchor="end"))
    data = [1, 0, 0, 1, 1, 0, 1, 0]
    f.extend(wave(x0, 150, 185, data, unit=unit, color=INK))

    # стрілки вибірки по фронту такту
    for i in range(nbits):
        xx = x0 + i * unit
        f.append(arrow(xx, 110, xx, 148, color=FIELD))
    f.append(text(x0 + nbits * unit / 2, 230, "приймач бере відлік по кожному фронту такту",
                  size=11.5, anchor="middle", color=FIELD))

    box = fitbox(80, 262, 600, 96, [
                 "Передавач не лише виставляє біт на лінії даних, а й цокає тактом: ось фронт —",
                 "дивись зараз. Мить кожного біта задана явно, дротом, тож приймачеві не",
                 "потрібен власний точний годинник, і лінію можна навіть спинити посеред",
                 "передачі. Ціна — зайвий дріт такту (дані + такт + земля), а на відстані",
                 "повертається перекіс, але вже між даними й тактом."],
                 size=12, fill="#eaf0fd", stroke=NEG)
    f.append(box)
    render(os.path.join(IMG, "sync.svg"), W, H, *f)


# ── 4. Асинхронно (UART): старт-біт і власний годинник ──────────────────────
def fig_async():
    W, H = 760, 380
    f = [text(W / 2, 26, "Асинхронно (UART): дроту такту немає — є старт-біт і домовлений baud",
              size=15, bold=True)]

    unit = 52
    x0 = 90
    y_hi, y_lo = 90, 130
    # спокій(1) старт(0) дані... стоп(1)
    seq = [("спокій", 1), ("старт", 0), ("D0", 1), ("D1", 0), ("D2", 0),
           ("D3", 1), ("D4", 1), ("D5", 0), ("D6", 1), ("D7", 0), ("стоп", 1)]
    bits = [b for _, b in seq]
    f.extend(wave(x0, y_hi, y_lo, bits, unit=unit, color=INK))
    # підписи клітин
    for i, (name, b) in enumerate(seq):
        col = POS if name == "старт" else (NEG if name == "стоп" else MUTED)
        f.append(text(x0 + i * unit + unit / 2, 152, name, size=9.5, color=col,
                      bold=(name in ("старт", "стоп"))))
    # старт-біт виділити
    f.append(rect(x0 + unit, y_hi - 6, unit, (y_lo - y_hi) + 30, fill="none",
                  stroke=POS, sw=1.6, rx=3))
    f.append(text(x0 + unit + unit / 2, 78, "перепад 1→0", size=10, color=POS))

    # власний годинник приймача
    f.append(text(x0, 205, "власний генератор приймача f_rx ≈ baud", size=12,
                  color=FIELD, anchor="start", bold=True))
    f.append(text(x0, 224, "старт-біт лише ЗАПУСКАЄ відлік; далі час веде свій годинник",
                  size=11, color=MUTED, anchor="start"))

    box = fitbox(80, 252, 600, 96, [
                 "Лінія в спокої тримається у «1». Щоб надіслати знак, передавач кидає її в «0»",
                 "на один біт — це старт-біт, постріл стартового пістолета. Упіймавши цей",
                 "перепад, приймач запускає власний відлік і сам, за своїм годинником, знімає",
                 "кожен наступний біт через домовлений інтервал; завершує знак стоп-біт.",
                 "І так — наново перед кожним знаком. Та сама ідея старт-стоп із телетайпа."],
                 size=12, fill="#eef7f0", stroke=FIELD)
    f.append(box)
    render(os.path.join(IMG, "async.svg"), W, H, *f)


# ── 5. Передискретизація 16× ────────────────────────────────────────────────
def fig_oversample():
    W, H = 900, 420
    f = [text(W / 2, 26, "Передискретизація: зловити спад старту, брати відлік посеред біта",
              size=15, bold=True)]

    unit = 150          # ширина одного біта
    x0 = 70
    y_hi, y_lo = 90, 140
    # спокій | старт(0) | D0(1) | D1(0) | D2(1)
    seq = [(1, "спокій"), (0, "старт"), (1, "D0"), (0, "D1"), (1, "D2")]
    bits = [b for b, _ in seq]
    f.extend(wave(x0, y_hi, y_lo, bits, unit=unit, color=INK))
    for i, (b, name) in enumerate(seq):
        f.append(text(x0 + i * unit + unit / 2, 162, name, size=10, color=MUTED))

    # тики 16× під лінією — дрібні риски
    tick_y = 178
    n_cells = len(seq)
    sub = 16
    step = unit / sub
    for c in range(n_cells):
        for k in range(sub):
            xx = x0 + c * unit + k * step
            big = (k == 0)
            f.append(line(xx, tick_y, xx, tick_y + (10 if big else 5),
                          color=MUTED, sw=1.0))
    f.append(text(x0 + unit * n_cells + 6, tick_y + 8, "16× baud", size=10,
                  color=MUTED, anchor="start"))

    # середина старту: ≈8 тиків
    mid_start = x0 + 1 * unit + unit / 2
    f.append(arrow(x0 + unit, 198, mid_start, 198, color=POS))
    f.append(text((x0 + unit + mid_start) / 2, 214, "≈8 тиків", size=10, color=POS, anchor="middle"))
    f.append(line(mid_start, y_hi - 6, mid_start, 200, color=POS, sw=1.4, dash="3,2"))
    f.append(text(mid_start, 78, "перевірка: тут і досі «0»?", size=10, color=POS))

    # відліки посеред кожного даного біта — зелені стрілки
    for i in (2, 3, 4):
        xx = x0 + i * unit + unit / 2
        f.append(line(xx, y_hi - 6, xx, 200, color=FIELD, sw=1.4, dash="3,2"))
        f.append(arrow(xx, 230, xx, 200, color=FIELD))
    f.append(text(x0 + 3 * unit + unit / 2, 246, "відлік посеред кожного біта (кожні 16 тиків)",
                  size=11, color=FIELD, anchor="middle"))

    box = fitbox(70, 270, 760, 96, [
                 "Внутрішній годинник приймача біжить ≈16× швидше за baud. Зловивши спад,",
                 "він відлічує ≈8 тиків до середини старту й перевіряє, що там і досі «0» — так",
                 "відсіюються короткі завади. Далі бере відлік кожні 16 тиків, тобто посеред",
                 "кожного біта: середина найдалі від країв-переходів, де сигнал ще хитається.",
                 "Цей запас і дає терпіти невеликий розсинхрон годинників."],
                 size=12, fill="#eef7f0", stroke=FIELD)
    f.append(box)
    render(os.path.join(IMG, "oversample.svg"), W, H, *f)


# ── 6. З'єднання: TX↔RX навхрест + земля ────────────────────────────────────
def fig_wiring():
    W, H = 720, 360
    f = [text(W / 2, 26, "Двопровідне з'єднання: TX↔RX навхрест і спільна земля",
              size=15, bold=True)]

    # дві коробки-пристрої
    bxA = rect(70, 90, 150, 150, fill="#eef2f7", stroke=INK, sw=1.8)
    bxB = rect(500, 90, 150, 150, fill="#eef2f7", stroke=INK, sw=1.8)
    f += [bxA, bxB]
    f.append(text(145, 80, "Пристрій A", size=13, bold=True))
    f.append(text(575, 80, "Пристрій B", size=13, bold=True))

    # піни A
    f.append(text(216, 122, "TX", size=12, bold=True, anchor="end", color=POS))
    f.append(text(216, 165, "RX", size=12, bold=True, anchor="end", color=NEG))
    f.append(text(216, 215, "GND", size=12, bold=True, anchor="end", color=MUTED))
    # піни B
    f.append(text(504, 122, "RX", size=12, bold=True, anchor="start", color=NEG))
    f.append(text(504, 165, "TX", size=12, bold=True, anchor="start", color=POS))
    f.append(text(504, 215, "GND", size=12, bold=True, anchor="start", color=MUTED))

    # навхрест: A.TX(118) → B.RX(118) ; A.RX(160) ← B.TX(160) — зобразимо перехрест
    f.append('<path d="M220,118 C330,118 390,160 500,160" fill="none" stroke="%s" stroke-width="2.2"/>' % POS)
    f.append('<path d="M220,160 C330,160 390,118 500,118" fill="none" stroke="%s" stroke-width="2.2"/>' % NEG)
    f.append(text(360, 128, "A.TX → B.RX", size=10.5, color=POS, anchor="middle"))
    f.append(text(360, 178, "B.TX → A.RX", size=10.5, color=NEG, anchor="middle"))
    # земля
    f.append(line(220, 210, 500, 210, color=MUTED, sw=2.2))
    f.append(text(360, 228, "спільна земля (GND)", size=11, color=MUTED, anchor="middle"))

    box = fitbox(70, 262, 580, 78, [
                 "Вихід одного йде на вхід іншого: A.TX → B.RX і B.TX → A.RX (навхрест).",
                 "Окремі лінії на кожен напрям дають повний дуплекс — обидва боки говорять",
                 "одночасно. Третій обов'язковий дріт — спільна земля: «0» і «1» це напруги,",
                 "а напругу нема як виміряти без спільної опорної точки."],
                 size=12, fill=FILL)
    f.append(box)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 7. Карта: послідовно/паралельно × синхронно/асинхронно ──────────────────
def fig_map():
    W, H = 720, 470
    f = [text(W / 2, 26, "Дві осі рішень — і де на них сидить UART",
              size=15, bold=True)]

    # сітка 2×2
    gx, gy = 230, 90
    cw, ch = 230, 150
    for c in range(2):
        for r in range(2):
            x = gx + c * cw
            y = gy + r * ch
            f.append(rect(x, y, cw, ch, fill="#fbfbfc", stroke="#c8ccd0", sw=1.4))

    # підписи осей
    f.append(text(gx + cw, gy - 14, "одна лінія даних → →  багато ліній", size=11.5,
                  anchor="middle", color=MUTED))
    # вертикальний підпис осі
    f.append('<text x="%.0f" y="%.0f" font-family="%s" font-size="11.5" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.0f %.0f)">є дріт такту ↑   немає такту ↓</text>'
             % (gx - 18, gy + ch, FONT, MUTED, gx - 18, gy + ch))

    def cell(c, r, title, sub, color, fill):
        x = gx + c * cw + cw / 2
        y = gy + r * ch
        f.append(rect(gx + c * cw + 6, gy + r * ch + 6, cw - 12, ch - 12,
                      fill=fill, stroke=color, sw=1.8))
        f.append(text(x, y + 40, title, size=13.5, bold=True, color=color))
        for i, ln in enumerate(sub):
            f.append(text(x, y + 66 + i * 18, ln, size=10.5, color=MUTED))

    # верхній ряд — є такт; нижній — нема такту. лівий стовпець — послідовно; правий — паралельно
    cell(0, 0, "Синхронна послідовна", ["SPI, I²C", "дані + такт"], NEG, "#eaf0fd")
    cell(1, 0, "Паралельна з тактом", ["шини пам'яті", "коротко, швидко"], MUTED, "#f2f3f5")
    cell(0, 1, "Асинхронна послідовна", ["UART ←", "старт-стоп, без такту"], FIELD, "#eef7f0")
    cell(1, 1, "Асинхронна паралельна", ["майже не вживають:", "перекіс ліній"], POS, "#fdecea")

    box = fitbox(70, 410, 580, 50, [
                 "UART — у клітині «асинхронна послідовна»: одна лінія на напрям, без дроту",
                 "такту, синхронізація старт-стопом. Сусіди — синхронні шини з дротом такту."],
                 size=12, fill=FILL)
    f.append(box)
    render(os.path.join(IMG, "map.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ІСТОРИЧНА ВСТАВКА (hist-baudot)
# ════════════════════════════════════════════════════════════════════════════

# ── h1. Часова лінія: від Морзе до кадру UART ───────────────────────────────
def fig_timeline():
    W, H = 820, 300
    f = [text(W / 2, 26, "Дорога завдовжки у 80 років: від коду Морзе до кадру UART",
              size=15, bold=True)]

    y = 120
    f.append(line(60, y, 760, y, color=MUTED, sw=2.0))
    stops = [
        ("1840-і", "Морзе", "швидкість —\nале рукою оператора", INK),
        ("1870-і", "Бодо", "5 однакових одиниць:\nчитає машина", FIELD),
        ("1870-і", "розподільник", "один дріт —\nкільком (TDM)", NEG),
        ("1900-і", "Маррей / телетайп", "клавіатура\nі перфострічка", INK),
        ("1910-і", "старт-стоп", "кадр сам себе\nсинхронізує", POS),
        ("нині", "UART", "той самий кадр\nу кремнії", FIELD),
    ]
    n = len(stops)
    for i, (date, name, note, col) in enumerate(stops):
        x = 90 + i * (640 / (n - 1))
        f.append(circle(x, y, 7, fill="#ffffff", stroke=col, sw=2.4))
        f.append(text(x, y - 30, name, size=12, bold=True, color=col))
        f.append(text(x, y - 14, date, size=10, color=MUTED))
        f.append(mtext(x, y + 26, note, size=10, color=MUTED, lh=1.25))

    box = fitbox(70, 240, 680, 44, [
                 "Кожен крок прибирав щось зайве: спершу майстерність руки, потім спільний",
                 "годинник — аж лишився мінімальний самосинхронний кадр, що дожив до UART."],
                 size=12, fill=FILL)
    f.append(box)
    render(os.path.join(IMG, "timeline.svg"), W, H, *f)


# ── h2. Морзе (змінна довжина) проти Бодо (5 рівних одиниць) ─────────────────
def fig_morse_baudot():
    W, H = 780, 420
    f = [text(W / 2, 26, "Корінь проблеми: змінна довжина Морзе проти 5 рівних клітин Бодо",
              size=15, bold=True)]

    f.append(line(390, 60, 390, 350, color="#d0d4d8", sw=1.2, dash="4,4"))

    # --- ліворуч: Морзе ---
    f.append(text(195, 60, "Код Морзе — змінна довжина", size=13.5, bold=True, color=NEG))
    u = 16
    # «E» = крапка
    yE = 110
    f.append(text(60, yE + 4, "E", size=13, bold=True, anchor="end"))
    f.append(rect(80, yE - 8, u, 16, fill=NEG, stroke="none"))
    f.append(text(80 + u + 8, yE + 4, "1 одиниця", size=10.5, color=MUTED, anchor="start"))
    # «O» = три тире (по 3u, з проміжками 1u)
    yO = 160
    f.append(text(60, yO + 4, "O", size=13, bold=True, anchor="end"))
    x = 80
    for _ in range(3):
        f.append(rect(x, yO - 8, 3 * u, 16, fill=NEG, stroke="none"))
        x += 3 * u + u
    f.append(text(80, yO + 30, "9 одиниць — удев'ятеро довше", size=10.5, color=POS, anchor="start"))
    f.append(text(195, 250, "щоб відрізнити крапки від тире,", size=11, anchor="middle"))
    f.append(text(195, 268, "треба точно міряти паузи —", size=11, anchor="middle"))
    f.append(text(195, 286, "робота для тренованого вуха", size=11, anchor="middle", color=POS))

    # --- праворуч: Бодо ---
    f.append(text(580, 60, "Код Бодо — 5 рівних клітин", size=13.5, bold=True, color=FIELD))
    cell = 36
    bx = 470
    for row, (ch, bitstr) in enumerate([("A", "11000"), ("E", "10000")]):
        yy = 110 + row * 60
        f.append(text(bx - 14, yy + 18, ch, size=13, bold=True, anchor="end"))
        for k, ch2 in enumerate(bitstr):
            on = ch2 == "1"
            f.append(rect(bx + k * cell, yy, cell - 4, 30,
                          fill=FIELD if on else "#ffffff",
                          stroke=FIELD, sw=1.6))
            f.append(text(bx + k * cell + (cell - 4) / 2, yy + 20, ch2, size=11,
                          color="#ffffff" if on else MUTED))
    f.append(text(580, 250, "кожен знак — рівно 5 однакових тактів", size=11, anchor="middle"))
    f.append(text(580, 268, "машині не треба впізнавати візерунок:", size=11, anchor="middle", color=FIELD))
    f.append(text(580, 286, "вона просто лічить п'ять клітин", size=11, anchor="middle", color=FIELD))

    box = fitbox(70, 320, 640, 56, [
                 "Морзе економний (часта «E» — найкоротша), але змінна довжина важко",
                 "автоматизується. Бодо платить рівною довжиною — і тим відкриває машинне",
                 "декодування: фіксований кадр дозволяє приймачу просто відлічувати такти."],
                 size=11.5, fill=FILL)
    f.append(box)
    render(os.path.join(IMG, "morse-baudot.svg"), W, H, *f)


# ── h3. Клавіатура Бодо на 5 клавіш і каданс ────────────────────────────────
def fig_keyboard():
    W, H = 740, 400
    f = [text(W / 2, 26, "Машина Бодо вперше нав'язала людині свій темп",
              size=15, bold=True)]

    # каданс зверху — ритмічні імпульси
    f.append(text(70, 70, "Каданс (ритм апарата):", size=12, bold=True, anchor="start", color=NEG))
    cu = 40
    cx = 290
    cad = [1, 0, 1, 0, 1, 0, 1, 0]
    f.extend(wave(cx, 58, 78, cad, unit=cu / 2.0, color=NEG))
    f.append(text(cx + cu * 2, 98, "натисни й відпусти строго в такт", size=10.5, color=MUTED, anchor="start"))

    # клавіатура: 2 + 3 клавіші, акорд «A» = 11000
    f.append(text(W / 2, 140, "Акорд літери «A» = 11000  (натиснуто 2 ліві)", size=12.5, bold=True))
    keys = [("L1", True), ("L2", True), (None, None), ("R1", False), ("R2", False), ("R3", False)]
    kx = 230
    kw = 54
    for i, (name, pressed) in enumerate(keys):
        if name is None:
            kx += 24
            continue
        x = kx
        col = FIELD if pressed else "#ffffff"
        f.append(rect(x, 170, kw, 60, fill=col, stroke=INK, sw=1.8, rx=6))
        f.append(text(x + kw / 2, 205, name, size=12, bold=True,
                      color="#ffffff" if pressed else INK))
        kx += kw + 10
    f.append(text(257, 252, "ліві (під ліву руку)", size=10.5, color=MUTED, anchor="middle"))
    f.append(text(490, 252, "праві (під праву руку)", size=10.5, color=MUTED, anchor="middle"))

    box = fitbox(70, 286, 600, 96, [
                 "Літеру набирали не послідовно, а акордом — натискали одночасно ту",
                 "комбінацію з п'яти клавіш (дві ліворуч, три праворуч), що відповідала п'яти",
                 "бітам знака. І робити це треба було строго у відведену апаратом мить:",
                 "оператор підлаштовувався під машину, а не навпаки. Уперше ритм лінії задавало",
                 "не людське чуття, а механічний такт — щоб на тому кінці декодувала машина."],
                 size=12, fill="#eaf0fd", stroke=NEG)
    f.append(box)
    render(os.path.join(IMG, "keyboard.svg"), W, H, *f)


# ── h4. Розподільник = поділ часу (TDM) ─────────────────────────────────────
def fig_tdm():
    W, H = 760, 430
    f = [text(W / 2, 26, "Розподільник Бодо: один дріт обслуговує кількох — по черзі (TDM)",
              size=15, bold=True)]

    # ліве колесо
    cxL, cyL, r = 150, 150, 70
    f.append(circle(cxL, cyL, r, fill="#fbfbfc", stroke=INK, sw=1.8))
    ops = ["A", "B", "C", "D"]
    cols = [POS, NEG, FIELD, ORANGE]
    for i, (op, col) in enumerate(zip(ops, cols)):
        ang = -90 + i * 90
        ax = cxL + (r + 18) * math.cos(math.radians(ang))
        ay = cyL + (r + 18) * math.sin(math.radians(ang)) + 4
        f.append(text(ax, ay, op, size=12, bold=True, color=col))
        # сектор-риска
        sx = cxL + r * math.cos(math.radians(ang))
        sy = cyL + r * math.sin(math.radians(ang))
        f.append(line(cxL, cyL, sx, sy, color="#c8ccd0", sw=1.2))
    # щітка
    f.append(line(cxL, cyL, cxL + r * math.cos(math.radians(-90)),
                  cyL + r * math.sin(math.radians(-90)), color=INK, sw=3.0))
    f.append(text(cxL, cyL + r + 34, "щітка обертається", size=10.5, color=MUTED))
    f.append(text(cxL, 70, "передавач", size=12, bold=True))

    # спільна лінія посередині
    f.append(line(cxL + r + 20, 150, cxR_anchor := 760 - 150 - 70 - 20, 150, color=INK, sw=2.4))
    f.append(text(380, 138, "спільний дріт", size=11, color=INK, anchor="middle"))
    # підписи слотів на лінії
    slot_x = [255, 320, 385, 450]
    for sx2, op, col in zip(slot_x, ops, cols):
        f.append(rect(sx2, 156, 50, 22, fill="none", stroke=col, sw=1.6, rx=3))
        f.append(text(sx2 + 25, 172, op, size=10.5, color=col))

    # праве колесо (синхронне)
    cxR, cyR = 610, 150
    f.append(circle(cxR, cyR, r, fill="#fbfbfc", stroke=INK, sw=1.8))
    for i, (op, col) in enumerate(zip(ops, cols)):
        ang = -90 + i * 90
        ax = cxR + (r + 18) * math.cos(math.radians(ang))
        ay = cyR + (r + 18) * math.sin(math.radians(ang)) + 4
        f.append(text(ax, ay, op + "′", size=12, bold=True, color=col))
        sx = cxR + r * math.cos(math.radians(ang))
        sy = cyR + r * math.sin(math.radians(ang))
        f.append(line(cxR, cyR, sx, sy, color="#c8ccd0", sw=1.2))
    f.append(line(cxR, cyR, cxR + r * math.cos(math.radians(-90)),
                  cyR + r * math.sin(math.radians(-90)), color=INK, sw=3.0))
    f.append(text(cxR, 70, "приймач (синхронно)", size=12, bold=True))

    box = fitbox(70, 250, 620, 130, [
                 "Лінію ділять на кілька каналів — скажімо, чотири, по одному на оператора.",
                 "Обертова щітка по черзі під'єднує до спільного дроту то A, то B, то C, то D:",
                 "кожному дістається свій короткий інтервал, у який його п'ять елементів летять",
                 "лінією. На тому кінці таке саме колесо, що крутиться синхронно, роздає прийняте",
                 "по принтерах. Це поділ часу (TDM) — живе й досі, від мобільного зв'язку до шин",
                 "у процесорі. Ахіллесова п'ята: обидва колеса мусять крутитися в один такт,",
                 "інакше дані A потраплять у принтер B′."],
                 size=12, fill="#eef7f0", stroke=FIELD)
    f.append(box)
    render(os.path.join(IMG, "tdm.svg"), W, H, *f)


# ── h5. Старт-стоп-кадр телетайпа = кадр UART ───────────────────────────────
def fig_startstop():
    W, H = 800, 430
    f = [text(W / 2, 26, "Та сама конструкція через століття: кадр телетайпа й кадр UART",
              size=15, bold=True)]

    def frame(y0, label, data_bits, with_parity, color):
        unit = 52
        x0 = 120
        y_hi, y_lo = y0, y0 + 38
        cells = [("спокій", 1), ("СТАРТ", 0)]
        for i, b in enumerate(data_bits):
            cells.append(("D%d" % i, b))
        if with_parity:
            cells.append(("P", 1))
        cells.append(("СТОП", 1))
        bits = [b for _, b in cells]
        f.extend(wave(x0, y_hi, y_lo, bits, unit=unit, color=color))
        for i, (nm, b) in enumerate(cells):
            c = POS if nm == "СТАРТ" else (NEG if nm == "СТОП" else MUTED)
            f.append(text(x0 + i * unit + unit / 2, y_lo + 18, nm, size=9,
                          color=c, bold=(nm in ("СТАРТ", "СТОП"))))
        f.append(text(x0 - 12, y0 + 18, label, size=11.5, bold=True, anchor="end", color=color))
        # стрілки відліку посеред кожного даного біта
        for i, (nm, b) in enumerate(cells):
            if nm.startswith("D"):
                xx = x0 + i * unit + unit / 2
                f.append(line(xx, y_hi - 5, xx, y_lo + 6, color=FIELD, sw=1.0, dash="2,2"))

    frame(80, "Телетайп (ITA-2)", [1, 0, 0, 1, 1], False, INK)
    f.append(text(400, 162, "старт + 5 даних + стоп (≥1.5)", size=10.5, color=MUTED, anchor="middle"))

    frame(230, "UART", [1, 0, 1, 1, 0, 0, 1, 0], True, INK)
    f.append(text(430, 312, "старт + 8 даних + парність + стоп", size=10.5, color=MUTED, anchor="middle"))

    box = fitbox(80, 340, 640, 78, [
                 "Приймач не має дроту такту: він ловить спад СТАРТ, запускає власний лічильник",
                 "і бере відлік посеред кожного біта (пунктир). Перед наступним знаком усе",
                 "синхронізується знову. Дорогу й крихку вічну синхронність розподільника",
                 "замінили на дешеву разову — перед кожним знаком. Це й є асинхронність."],
                 size=12, fill="#eef7f0", stroke=FIELD)
    f.append(box)
    render(os.path.join(IMG, "startstop.svg"), W, H, *f)


# ── h6. Що таке baud: одиниць за секунду ────────────────────────────────────
def fig_baud():
    W, H = 760, 400
    f = [text(W / 2, 26, "Що таке baud: сигнальних одиниць за секунду",
              size=15, bold=True)]

    # розклад одного знака ITA-2: старт(1) + 5 даних + стоп(1.5) = 7.5
    unit = 70
    x0 = 90
    y_hi, y_lo = 90, 128
    cells = [("старт", 0, 1.0), ("D0", 1, 1.0), ("D1", 0, 1.0), ("D2", 1, 1.0),
             ("D3", 1, 1.0), ("D4", 0, 1.0), ("стоп", 1, 1.5)]
    x = x0
    prev = None
    for nm, b, w in cells:
        y = y_lo if b else y_hi
        ww = unit * w
        if prev is not None and prev != y:
            f.append(line(x, prev, x, y, color=INK, sw=2.4))
        f.append(line(x, y, x + ww, y, color=INK, sw=2.4))
        c = POS if nm == "старт" else (NEG if nm == "стоп" else MUTED)
        f.append(text(x + ww / 2, y_lo + 22, nm, size=9.5, color=c,
                      bold=(nm in ("старт", "стоп"))))
        f.append(text(x + ww / 2, y_lo + 36, ("%.1f" % w), size=9, color=MUTED))
        prev = y
        x += ww
    f.append(text(x0, 78, "1 + 5 + 1.5 = 7.5 одиниць на знак", size=11.5, anchor="start", bold=True))

    box = fitbox(80, 200, 600, 130, [
                 "1 бод = одна сигнальна одиниця (символ) за секунду. Класичний телетайп —",
                 "45.45 бода, тож одна одиниця триває 1 / 45.45 ≈ 22 мс, а знак (7.5 одиниць) —",
                 "≈165 мс: близько 6 знаків за секунду, тобто ≈60 слів за хвилину. З 7.5 одиниць",
                 "корисні лише 5 — третина «ефіру» йде на старт і стоп: це плата за те, щоб",
                 "обійтися без дроту такту. Чому бод ≠ біт/с? Бо бод лічить символи на лінії.",
                 "Поки символ має два рівні (мітка/пропуск), він несе 1 біт — і бод = біт/с;",
                 "щойно рівнів більше двох, один символ несе кілька біт, і вони розходяться."],
                 size=12, fill=FILL)
    f.append(box)
    render(os.path.join(IMG, "baud.svg"), W, H, *f)


if __name__ == "__main__":
    # стаття
    fig_parallel_serial()
    fig_skew()
    fig_sync()
    fig_async()
    fig_oversample()
    fig_wiring()
    fig_map()
    # історична вставка
    fig_timeline()
    fig_morse_baudot()
    fig_keyboard()
    fig_tdm()
    fig_startstop()
    fig_baud()
    print("OK: figures written to", IMG)
