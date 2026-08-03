# -*- coding: utf-8 -*-
"""Фігури до теми «Як чипи розмовляють: навіщо шини».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

BUS = "#2c7a4b"      # спільна шина — зелене (порятунок)
WIRE = "#c0392b"     # окремий дріт на кожну пару — червоне (вибух)


# ── 1. Окремі дроти проти спільної шини ──────────────────────────────────────
def fig_wire_explosion():
    W, H = 760, 380
    f = [text(W / 2, 26, "Окремий дріт на кожну пару — проти спільної шини", size=16, bold=True)]
    f.append(text(W / 2, 46, "п'ять чипів; ліворуч — по дроту між кожними двома, праворуч — усі на одній шині",
                  size=11, color=MUTED, italic=True))

    import math

    # ── ліва панель: повний граф зв'язків (кожен з кожним) ──
    cxL, cyL, rL = 190, 196, 88
    nodesL = []
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        nodesL.append((cxL + rL * math.cos(a), cyL + rL * math.sin(a)))
    # усі ребра
    for i in range(5):
        for j in range(i + 1, 5):
            f.append(line(nodesL[i][0], nodesL[i][1], nodesL[j][0], nodesL[j][1],
                          color=WIRE, sw=1.4))
    for i, (x, y) in enumerate(nodesL):
        f.append(circle(x, y, 17, fill=BG, stroke=WIRE, sw=2))
        f.append(text(x, y + 4, chr(ord('A') + i), size=12, color=WIRE, bold=True))
    f.append(text(cxL, cyL + rL + 30, "окремі дроти: 10 ліній на 5 чипів",
                  size=11.5, color=WIRE, bold=True))
    f.append(text(cxL, cyL + rL + 47, "N·(N−1)/2 — росте як квадрат",
                  size=10, color=MUTED, italic=True))

    # ── права панель: спільна шина (одна магістраль, відводи) ──
    bx0, bx1, by = 470, 720, 180
    f.append(line(bx0, by, bx1, by, color=BUS, sw=3))          # магістраль
    f.append(line(bx0, by + 12, bx1, by + 12, color=BUS, sw=3))
    xs = [500, 555, 610, 665, 705]
    for i, x in enumerate(xs):
        f.append(line(x, by + 12, x, by + 60, color=BUS, sw=1.6))   # відвід
        f.append(rect(x - 20, by + 60, 40, 30, fill=BG, stroke=BUS, sw=1.8))
        f.append(text(x, by + 80, chr(ord('A') + i), size=11, color=BUS, bold=True))
    f.append(text(595, by - 16, "спільна шина: 1 магістраль на всіх",
                  size=11.5, color=BUS, bold=True))
    f.append(text(595, by + 118, "новий чип — просто ще один відвід",
                  size=10, color=MUTED, italic=True))

    f.append(fitbox(30, 344, 700, 28,
                    "Шина міняє «дріт на кожну пару» на спільну магістраль плюс правила, хто коли говорить.",
                    size=10.5, color=INK, fill=FILL, stroke="#e0e0e0", sw=1))
    render(os.path.join(IMG, "wire-explosion.svg"), W, H, *f)


# ── 2. Паралельно проти послідовно ───────────────────────────────────────────
def fig_parallel_vs_serial():
    W, H = 760, 400
    f = [text(W / 2, 26, "Паралельно проти послідовно: чому виграє вузьке", size=16, bold=True)]
    f.append(text(W / 2, 46, "той самий байт 1011 0010 — ліворуч усі біти воднораз, праворуч один за одним",
                  size=11, color=MUTED, italic=True))

    bits = [1, 0, 1, 1, 0, 0, 1, 0]

    # ── ліва панель: 8 паралельних ліній, перекіс фронтів ──
    lx0, lx1 = 60, 300
    ytop = 92
    dy = 24
    for i, b in enumerate(bits):
        y = ytop + i * dy
        f.append(line(lx0, y, lx1, y, color="#c8c8c8", sw=1))
        # фронт кожної лінії приходить у трохи різний момент → перекіс
        skew = (i % 3) * 10 + (i // 4) * 8
        col = WIRE if b else NEG
        f.append(line(lx0 + 60 + skew, y - 7, lx0 + 60 + skew, y + 3, color=col, sw=2.4))
        f.append(text(lx0 - 10, y + 4, "D%d" % i, size=9, color=MUTED, anchor="end"))
        f.append(text(lx1 + 8, y + 4, str(b), size=10, color=col, anchor="start", bold=True))
    # зона невизначеності від перекосу
    f.append(rect(lx0 + 60, ytop - 12, 42, 8 * dy - 6, fill="#f7dede", stroke="none", sw=0, rx=3))
    f.append(text((lx0 + lx1) / 2, ytop + 8 * dy + 8, "8 ліній: 8 біт воднораз",
                  size=11, color=INK, bold=True, anchor="middle"))
    f.append(text((lx0 + lx1) / 2, ytop + 8 * dy + 26,
                  "але фронти приходять НЕ разом → перекіс (skew)",
                  size=9.5, color=POS, italic=True, anchor="middle"))

    # ── права панель: 1 лінія, біти по черзі, під такт ──
    rx0, rx1 = 430, 720
    ydat = 150
    ytk = 250
    span = rx1 - rx0
    bw = span / 8.0
    # такт: 8 імпульсів
    tk = ["M %.1f %.1f" % (rx0, ytk)]
    for i in range(8):
        x = rx0 + i * bw
        tk.append("L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f"
                  % (x, ytk, x, ytk - 20, x + bw / 2, ytk - 20, x + bw / 2, ytk))
        tk.append("L %.1f %.1f" % (x + bw, ytk))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(tk), NEG))
    f.append(text(rx0 - 8, ytk - 8, "такт", size=10, color=NEG, anchor="end", bold=True))
    # дані: рівень тримається бітом
    dp = ["M %.1f %.1f" % (rx0, ydat - bits[0] * 30)]
    for i, b in enumerate(bits):
        x0 = rx0 + i * bw
        y = ydat - b * 30
        dp.append("L %.1f %.1f" % (x0, y))
        dp.append("L %.1f %.1f" % (x0 + bw, y))
        f.append(text(x0 + bw / 2, ydat - 40, str(b), size=11, color=BUS, bold=True))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(dp), BUS))
    f.append(text(rx0 - 8, ydat - 14, "дані", size=10, color=BUS, anchor="end", bold=True))
    f.append(text((rx0 + rx1) / 2, ytk + 34, "1 лінія + такт: біти по черзі",
                  size=11, color=INK, bold=True, anchor="middle"))
    f.append(text((rx0 + rx1) / 2, ytk + 52,
                  "нема перекосу — приймач ловить біт на кожен фронт такту",
                  size=9.5, color=BUS, italic=True, anchor="middle"))

    f.append(fitbox(30, 344, 700, 40,
                    ["Широка паралельна шина здається швидшою (8 біт за раз), але на високій частоті фронти",
                     "розповзаються — перекіс і наведення ставлять стелю. Вузька послідовна лінія її обходить."],
                    size=10.5, color=INK, fill=FILL, stroke="#e0e0e0", sw=1))
    render(os.path.join(IMG, "parallel-vs-serial.svg"), W, H, *f)


# ── 3. Три угоди, які фіксує будь-яка шина ────────────────────────────────────
def fig_three_agreements():
    W, H = 760, 340
    f = [text(W / 2, 26, "Три угоди, без яких шина не працює", size=16, bold=True)]
    f.append(text(W / 2, 46, "кожна дротова шина плати — це власна відповідь на ці самі три питання",
                  size=11, color=MUTED, italic=True))

    def card(x, q, sub, ans):
        f.append(rect(x, 66, 224, 176, fill=FILL, stroke=INK, sw=1.8))
        f.append(text(x + 112, 92, q, size=13.5, bold=True))
        f.append(fitbox(x + 12, 102, 200, 42, sub, size=10, color=MUTED, italic=True,
                        fill=FILL, stroke="none", sw=0))
        f.append(line(x + 18, 152, x + 206, 152, color="#dddddd", sw=1))
        yy = 172
        for name, col, how in ans:
            f.append(text(x + 22, yy, name, size=11, color=col, anchor="start", bold=True))
            f.append(text(x + 74, yy, how, size=9.5, anchor="start"))
            yy += 22

    UART = NEG
    I2C = "#b9770e"
    SPI = FIELD
    card(24, "1 · Де межа біта?",
         "коли рівень — це «1»,\nа коли просто тиша",
         [("UART", UART, "домовлена швидкість"),
          ("I2C", I2C, "спільний такт SCL"),
          ("SPI", SPI, "спільний такт SCLK")])
    card(268, "2 · Хто веде?",
         "хто саме штовхає лінію,\nщоб не штовхали двоє",
         [("UART", UART, "кожен свій дріт"),
          ("I2C", I2C, "ведучий + арбітраж"),
          ("SPI", SPI, "ведучий смикає CS")])
    card(512, "3 · До кого мова?",
         "як із багатьох відгукнувся\nсаме потрібний",
         [("UART", UART, "нема — точка-точка"),
          ("I2C", I2C, "адреса в кадрі"),
          ("SPI", SPI, "окрема лінія CS")])

    f.append(text(W / 2, 300,
                  "усі шини курсу відповідають на ці три однаково за суттю, різно за виконанням",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "three-agreements.svg"), W, H, *f)


# ── 4. Родовід слова «шина»: omnibus → busbar → bus (для вставки hist) ────────
def fig_bus_word_lineage():
    W, H = 780, 300
    f = [text(W / 2, 26, "Родовід слова «шина»: одна думка — «для всіх» — крізь двісті років",
              size=15.5, bold=True)]
    f.append(text(W / 2, 46, "від латинського відмінка до мідного бруса й далі до магістралі чипів",
                  size=11, color=MUTED, italic=True))

    y = 120                      # вісь родоводу
    x0, x1 = 60, 720
    f.append(line(x0, y, x1, y, color=FIELD, sw=3))   # наскрізна нитка «для всіх»
    f.append(text(x1 + 4, y + 4, "→", size=16, color=FIELD, bold=True, anchor="start"))

    # п'ять станцій ланцюга: (x, підпис-слово, рік/примітка, значення)
    stations = [
        (110, "omnibus", "лат.", "«для всіх»"),
        (270, "voiture", "1828", "повіз для всіх"),
        (430, "busbar", "~1900", "мідний брус"),
        (590, "bus", "1960-ті", "шина чипів"),
    ]
    for x, word, yr, mean in stations:
        f.append(circle(x, y, 8, fill=BG, stroke=FIELD, sw=2.4))
        f.append(text(x, y - 30, word, size=13, color=INK, bold=True))
        f.append(text(x, y - 14, yr, size=9.5, color=MUTED, italic=True))
        f.append(text(x, y + 30, mean, size=10, color=FIELD))

    # розвилка внизу: поворот до серійних шин (2003–2004) — від краю станції, повз меанінг-підпис
    f.append(line(612, y + 4, 612, y + 66, color=MUTED, sw=1.4, dash="4,3"))
    box = textbox(612, y + 96, ["поворот до серійних:",
                                "SATA 2003 · PCIe 2004"],
                  size=10, color=INK, fill=FILL, stroke=POS, sw=1.4)
    f.append(box[0])

    f.append(fitbox(30, 248, 720, 40,
                    ["Слово несе свою суть незмінно: лінія, СПІЛЬНА для всіх, хто до неї під'єднаний —",
                     "спершу пасажирів, потім кіл живлення, нарешті мікросхем на платі."],
                    size=10.5, color=INK, fill=FILL, stroke="#e0e0e0", sw=1))
    render(os.path.join(IMG, "bus-word-lineage.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
# Фігури для ДЕТАЛЬНОЇ версії (why-buses-d.md) — глибша механіка, не дублюють базові
# ══════════════════════════════════════════════════════════════════════════════

DRV = "#c0392b"     # активний драйвер (штовхає рівень)
HIZ = "#6b7280"     # відпущений вихід (Hi-Z)
PUP = "#2c7a4b"     # підтяжка / порятунок


# ── 5. Три режими виходу на спільній лінії ───────────────────────────────────
def fig_output_stages():
    """Push-pull (конфлікт!) · open-drain+підтяжка (wired-AND) · три-стан (шина даних)."""
    W, H = 800, 440
    f = [text(W / 2, 26, "Три способи ділити одну лінію — і що стається при зіткненні", size=15.5, bold=True)]
    f.append(text(W / 2, 46, "чому push-pull двох ведучих небезпечний, а open-drain і три-стан — ні",
                  size=11, color=MUTED, italic=True))

    PW = 246          # ширина панелі
    rail_y = 236      # спільна лінія в кожній панелі

    # ── панель A: push-pull, двоє штовхають протилежне → коротке ──
    ax = 20
    f.append(rect(ax, 70, PW, 236, fill=BG, stroke="#dddddd", sw=1.2))
    f.append(text(ax + PW / 2, 92, "push-pull: двоє ведучих", size=12, color=DRV, bold=True))
    f.append(line(ax + 30, rail_y, ax + PW - 30, rail_y, color=INK, sw=2.6))
    # драйвер 1 тягне ВГОРУ (+3.3): підпис — ЗЛІВА від лінії, не на ній
    f.append(rect(ax + 40, 128, 46, 40, fill="#fdecea", stroke=DRV, sw=1.8))
    f.append(text(ax + 63, 120, "A → 1", size=10, color=DRV, bold=True))
    f.append(line(ax + 63, 168, ax + 63, rail_y, color=DRV, sw=2.2))
    f.append(text(ax + 34, 196, "+3.3", size=9, color=DRV, anchor="end"))
    # драйвер 2 тягне ВНИЗ (0): підпис — СПРАВА від лінії
    f.append(rect(ax + PW - 86, 128, 46, 40, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(ax + PW - 63, 120, "B → 0", size=10, color=NEG, bold=True))
    f.append(line(ax + PW - 63, 168, ax + PW - 63, rail_y, color=NEG, sw=2.2))
    f.append(text(ax + PW - 34, 196, "0 В", size=9, color=NEG, anchor="start"))
    # струм наскрізь по лінії (підпис під рейкою, не на дроп-лініях)
    f.append(text(ax + PW / 2, rail_y + 22, "I = 3.3 / 2R_on  ⇒  коротке", size=10, color=DRV, bold=True))

    # ── панель B: open-drain + підтяжка, wired-AND ──
    bx = 20 + PW + 21
    f.append(rect(bx, 70, PW, 236, fill=BG, stroke="#dddddd", sw=1.2))
    f.append(text(bx + PW / 2, 92, "open-drain + підтяжка", size=12, color=PUP, bold=True))
    # підтяжка до Vcc (з краю панелі, щоб лінія такту не різала написів)
    pux = bx + PW - 40
    f.append(text(pux, 116, "Vcc", size=9.5, color=PUP, bold=True, anchor="middle"))
    f.append(line(pux, 122, pux, 138, color=PUP, sw=1.6))
    f.append(rect(pux - 13, 138, 26, 15, fill=BG, stroke=PUP, sw=1.6))
    f.append(text(pux + 20, 149, "R", size=9.5, color=PUP, anchor="start"))
    f.append(line(pux, 153, pux, rail_y, color=PUP, sw=1.6))
    f.append(line(bx + 30, rail_y, pux, rail_y, color=INK, sw=2.6))
    # ведений 1 тягне вниз (підпис над блоком)
    f.append(rect(bx + 44, 150, 46, 38, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(bx + 67, 142, "тягне 0", size=9, color=NEG, bold=True))
    f.append(line(bx + 67, 188, bx + 67, rail_y, color=NEG, sw=2))
    # ведений 2 відпущено (підпис над блоком)
    f.append(rect(bx + 130, 150, 46, 38, fill=BG, stroke=HIZ, sw=1.4))
    f.append(text(bx + 153, 142, "відпущ.", size=9, color=HIZ))
    f.append(line(bx + 153, 188, bx + 153, rail_y, color=HIZ, sw=1.4, dash="3,3"))
    f.append(text(bx + PW / 2, rail_y + 22, "хтось тягне 0 ⇒ лінія 0", size=9.5, color=INK, bold=True))

    # ── панель C: три-стан ──
    cx = 20 + 2 * (PW + 21)
    f.append(rect(cx, 70, PW, 236, fill=BG, stroke="#dddddd", sw=1.2))
    f.append(text(cx + PW / 2, 92, "три-стан (шина даних)", size=12, color=INK, bold=True))
    f.append(line(cx + 30, rail_y, cx + PW - 30, rail_y, color=INK, sw=2.6))
    # один активний, решта Hi-Z; підписи над блоками
    f.append(rect(cx + 40, 150, 46, 38, fill="#fdecea", stroke=DRV, sw=1.8))
    f.append(text(cx + 63, 142, "OE=1", size=9, color=DRV, bold=True))
    f.append(line(cx + 63, 188, cx + 63, rail_y, color=DRV, sw=2.2))
    for dx in (120, 172):
        f.append(rect(cx + dx, 150, 42, 38, fill=BG, stroke=HIZ, sw=1.4))
        f.append(text(cx + dx + 21, 142, "OE=0", size=9, color=HIZ))
        f.append(line(cx + dx + 21, 188, cx + dx + 21, rail_y, color=HIZ, sw=1.4, dash="3,3"))
    f.append(text(cx + PW / 2, rail_y + 22, "лише один OE=1; решта Hi-Z", size=9.5, color=INK, bold=True))

    # три однорядкові підсумки під панелями (короткі — шрифт не стискається)
    f.append(fitbox(ax, 320, PW, 28, "штовхачі б'ються — каскад згорає",
                    size=9.5, color=INK, fill="#fdecea", stroke=DRV, sw=1.2))
    f.append(fitbox(bx, 320, PW, 28, "зіткнення немає за побудовою",
                    size=9.5, color=INK, fill="#eafaf1", stroke=PUP, sw=1.2))
    f.append(fitbox(cx, 320, PW, 28, "веде рівно один за чергою",
                    size=9.5, color=INK, fill=FILL, stroke=INK, sw=1.1))

    f.append(fitbox(20, 356, W - 40, 30,
                    "Спільна лінія жива, лише коли її ставить хтось один: або жорстка черга (три-стан), "
                    "або конструкція, де зіткнення неможливе за побудовою (open-drain — усі тягнуть тільки вниз).",
                    size=10, color=INK, fill=FILL, stroke="#e0e0e0", sw=1))
    render(os.path.join(IMG, "output-stages.svg"), W, H, *f)


# ── 6. RC-заряд підтягнутої лінії: ємність ставить стелю частоти ──────────────
def fig_rc_risetime():
    """Відкритий стік тягне вниз швидко, а вгору лінію піднімає підтяжка через R — повільно (τ=R·C)."""
    W, H = 760, 400
    f = [text(W / 2, 26, "Чому ємність шини ставить стелю частоти", size=15.5, bold=True)]
    f.append(text(W / 2, 46, "вниз лінію «кидає» транзистор, а вгору повільно піднімає підтяжка крізь R·C",
                  size=11, color=MUTED, italic=True))

    # осі
    ox, oy = 90, 300           # початок координат (лівий-низ графіка)
    axw, axh = 560, 200
    f.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.6))          # час →
    f.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.6))          # напруга ↑
    f.append(text(ox + axw, oy + 18, "час", size=10, color=MUTED, anchor="end", italic=True))
    f.append(text(ox - 14, oy - axh + 6, "V", size=11, color=MUTED, anchor="end", bold=True))
    yV = oy - axh + 20         # рівень Vcc
    y0 = oy                    # рівень 0
    f.append(line(ox, yV, ox + axw, yV, color=PUP, sw=1, dash="4,3"))
    f.append(text(ox - 8, yV + 4, "Vcc", size=9.5, color=PUP, anchor="end", bold=True))
    # поріг «1»
    yTh = oy - axh * 0.7
    f.append(line(ox, yTh, ox + axw, yTh, color=MUTED, sw=1, dash="2,3"))
    f.append(text(ox + axw + 4, yTh + 4, "поріг «1»", size=9, color=MUTED, anchor="start"))

    import math
    # ── швидкий спад (транзистор тягне вниз): майже вертикаль ──
    xt0 = ox + 40
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (xt0 - 40, yV, xt0, yV, xt0 + 6, y0, NEG))
    f.append(text(xt0 + 4, y0 + 18, "спад: транзистор", size=9.5, color=NEG, anchor="start", bold=True))
    f.append(text(xt0 + 4, y0 + 32, "«кидає» вниз — швидко", size=9, color=NEG, anchor="start"))

    # ── повільний підйом (RC) від xt1 ──
    xt1 = ox + 250
    tau = 70.0                 # пікселів на τ
    pts = []
    for i in range(0, 260):
        x = xt1 + i
        v = 1 - math.exp(-(x - xt1) / tau)      # 0→1
        y = y0 - (y0 - yV) * v
        pts.append("%.1f %.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), PUP))
    f.append(text(xt1 + 150, oy - axh * 0.30, "підйом: підтяжка крізь R", size=9.5, color=PUP, anchor="middle", bold=True))
    f.append(text(xt1 + 150, oy - axh * 0.30 + 14, "заряджає C — повільно, τ = R·C", size=9, color=PUP, anchor="middle"))
    # позначка τ
    f.append(line(xt1, oy + 6, xt1, oy + 22, color=MUTED, sw=1))
    f.append(line(xt1 + tau, oy + 6, xt1 + tau, oy + 22, color=MUTED, sw=1))
    f.append(text(xt1 + tau / 2, oy + 34, "τ", size=11, color=INK, anchor="middle", bold=True, italic=True))
    # точка перетину порога
    xcross = xt1 + tau * math.log(1 / 0.3)      # v=0.7
    f.append(circle(xcross, yTh, 3.5, fill=PUP, stroke=PUP, sw=1))
    f.append(line(xcross, yTh, xcross, oy, color=MUTED, sw=0.9, dash="2,2"))
    f.append(text(xcross, oy + 34, "тут читається «1»", size=9, color=MUTED, anchor="middle"))

    f.append(fitbox(30, 352, 700, 40,
                    ["Спад майже миттєвий, а підйом лінія «повзе» за законом заряду конденсатора: більша ємність C",
                     "(довші дроти, більше пристроїв) → більший час підйому → нижча стеля частоти шини."],
                    size=10, color=INK, fill=FILL, stroke="#e0e0e0", sw=1))
    render(os.path.join(IMG, "rc-risetime.svg"), W, H, *f)


# ── 7. Синхронно проти асинхронно: як приймач ловить момент біта ─────────────
def fig_sync_vs_async():
    W, H = 780, 420
    f = [text(W / 2, 26, "Де межа біта: тактом проти домовленої швидкості", size=15.5, bold=True)]
    f.append(text(W / 2, 46, "синхронно — фронт такту каже «лови»; асинхронно — приймач сам лічить свій час",
                  size=11, color=MUTED, italic=True))

    bits = [1, 0, 1, 1, 0, 1]
    span = 560
    x0 = 110
    bw = span / len(bits)

    # ── верх: СИНХРОННО (дані + такт), стрілки семплів на фронтах ──
    yd = 110
    ytk = 175
    dp = ["M %.1f %.1f" % (x0, yd - bits[0] * 26)]
    for i, b in enumerate(bits):
        xa = x0 + i * bw
        y = yd - b * 26
        dp.append("L %.1f %.1f" % (xa, y)); dp.append("L %.1f %.1f" % (xa + bw, y))
        f.append(text(xa + bw / 2, yd - 34, str(b), size=10, color=INK, bold=True))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(dp), INK))
    f.append(text(x0 - 10, yd - 12, "дані", size=10, color=INK, anchor="end", bold=True))
    # такт
    tk = ["M %.1f %.1f" % (x0, ytk)]
    for i in range(len(bits)):
        xa = x0 + i * bw
        tk.append("L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f"
                  % (xa, ytk, xa, ytk - 20, xa + bw / 2, ytk - 20, xa + bw / 2, ytk))
        tk.append("L %.1f %.1f" % (xa + bw, ytk))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(tk), NEG))
    f.append(text(x0 - 10, ytk - 8, "такт", size=10, color=NEG, anchor="end", bold=True))
    # семпли на висхідних фронтах: лінія від рівня даних до такту (не заходить у рядок підписів)
    for i in range(len(bits)):
        xa = x0 + i * bw
        f.append(line(xa, yd - 22, xa, ytk - 20, color=PUP, sw=1, dash="3,2"))
        f.append('<path d="M %.1f %.1f l -4 8 l 8 0 z" fill="%s"/>' % (xa, ytk - 20, PUP))
    f.append(text(x0 + span + 8, yd + 4, "фронт такту", size=9, color=PUP, anchor="start", bold=True))
    f.append(text(x0 + span + 8, yd + 18, "= «лови біт»", size=9, color=PUP, anchor="start"))
    f.append(text(x0 + span / 2, ytk + 24, "СИНХРОННО: межу біта задає окремий дріт такту",
                  size=10.5, color=INK, anchor="middle", bold=True))

    # ── низ: АСИНХРОННО (лише дані), приймач семплить у СЕРЕДИНІ за своїм часом ──
    yd2 = 300
    f.append(line(x0 - 40, yd2, x0, yd2, color="#c8c8c8", sw=1))     # idle=1
    dp2 = ["M %.1f %.1f" % (x0 - 40, yd2 - 26)]
    seq = [0] + bits + [1]        # старт-біт (0), дані, стоп (1)
    bw2 = span / len(seq)
    labels = ["старт"] + [str(b) for b in bits] + ["стоп"]
    for i, b in enumerate(seq):
        xa = x0 + i * bw2
        y = yd2 - b * 26
        dp2.append("L %.1f %.1f" % (xa, y)); dp2.append("L %.1f %.1f" % (xa + bw2, y))
        col = POS if i == 0 else (PUP if i == len(seq) - 1 else MUTED)
        f.append(text(xa + bw2 / 2, yd2 - 36, labels[i], size=9, color=col, bold=(i == 0)))
        # семпл у середині кожного біта — за ВЛАСНИМ годинником приймача (нижче рядка підписів)
        f.append(line(xa + bw2 / 2, yd2 - 18, xa + bw2 / 2, yd2 + 14, color=FIELD, sw=1, dash="3,2"))
        f.append(circle(xa + bw2 / 2, yd2 + 14, 3, fill=FIELD, stroke=FIELD, sw=1))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(dp2), INK))
    f.append(text(x0 - 50, yd2 - 12, "дані", size=10, color=INK, anchor="end", bold=True))
    f.append(text(x0 + span / 2, yd2 + 40, "АСИНХРОННО: старт-біт запускає лічбу; приймач семплить у СЕРЕДИНІ біта",
                  size=10.5, color=INK, anchor="middle", bold=True))
    f.append(text(x0 + span / 2, yd2 + 56, "за наперед домовленою швидкістю — доки його час не «сповз» від чужого",
                  size=9.5, color=FIELD, anchor="middle", italic=True))

    render(os.path.join(IMG, "sync-vs-async.svg"), W, H, *f)


if __name__ == "__main__":
    fig_wire_explosion()
    fig_parallel_vs_serial()
    fig_three_agreements()
    fig_bus_word_lineage()
    fig_output_stages()
    fig_rc_risetime()
    fig_sync_vs_async()
    print("OK: 7 figures ->", IMG)
