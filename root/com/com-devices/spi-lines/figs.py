# -*- coding: utf-8 -*-
"""Фігури до теми «Лінії SPI» та її вставки comp-tri-state-buffer.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b08900"   # CS
PURP = "#7a2bd6"   # двонапрямлена лінія SDIO


# ── спільний помічник: цифровий меандр як ламана ─────────────────────────────
def wave(x0, y_hi, y_lo, bits, unit, color=INK, sw=2.4):
    out = []
    x = x0
    prev = None
    for b in bits:
        y = y_lo if b else y_hi
        if prev is not None and prev != y:
            out.append(line(x, prev, x, y, color=color, sw=sw))
        out.append(line(x, y, x + unit, y, color=color, sw=sw))
        prev = y
        x += unit
    return out


def caption(f, W, y, s, color=MUTED, size=12.5):
    f.append(text(W / 2, y, s, size=size, color=color, italic=True))


# ════════════════════════════════════════════════════════════════════════════
#  СТАТТЯ
# ════════════════════════════════════════════════════════════════════════════

# ── 1. Хто жене кожну лінію й коли (таблиця) ─────────────────────────────────
def fig_who_drives():
    W, H = 900, 372
    f = [text(W / 2, 34, "Чотири лінії SPI: хто жене кожну й коли", size=19, bold=True)]
    caption(f, W, 56, "три лінії завжди жене ведучий, а MISO оживає лише в обраного веденого")

    cols = [(96, "лінія"), (230, "напрям"), (400, "хто жене"), (600, "коли")]
    # шапка
    f.append(rect(80, 96, 740, 34, fill="#f0f0f0", stroke=MUTED, sw=1.3))
    for x, t in cols:
        f.append(text(x, 118, t, size=11.5, color=INK, anchor="start", bold=True))

    rows = [
        ("SCK",  NEG,  "ведучий → ведений", "ведучий", "завжди (це він тактує)", MUTED, False),
        ("MOSI", POS,  "ведучий → ведений", "ведучий", "завжди",                 MUTED, False),
        ("MISO", FIELD,"ведений → ведучий", "ведений", "ЛИШЕ коли його CS = 0",  FIELD, True),
        ("CS",   GOLD, "ведучий → ведений", "ведучий", "опускає, щоб обрати",    MUTED, False),
    ]
    y = 130
    for name, ncol, direction, who, when, wcol, wbold in rows:
        f.append(rect(80, y, 740, 44, fill=BG, stroke=MUTED, sw=1, rx=0))
        f.append(text(96, y + 28, name, size=13, color=ncol, anchor="start", bold=True))
        f.append(text(230, y + 28, direction, size=11, color=INK, anchor="start"))
        f.append(text(400, y + 28, who, size=11, color=INK, anchor="start"))
        f.append(text(600, y + 28, when, size=11, color=wcol, anchor="start", bold=wbold))
        y += 44

    f.append(fitbox(60, 320, 780, 44,
                    "Ключ до спільної шини: необраний ведений ВІДПУСКАЄ MISO (високий імпеданс), щоб не заважати.",
                    size=12, fill="#eef6ef", stroke=FIELD, bold=True))
    render(os.path.join(IMG, "who-drives.svg"), W, H, *f)


# ── 2. Спільний MISO без конфлікту: високий імпеданс ─────────────────────────
def fig_miso_tristate():
    W, H = 900, 400
    f = [text(W / 2, 34, "Спільний MISO без конфлікту: необрані ведені відключаються", size=18, bold=True)]
    caption(f, W, 56, "лише обраний (CS = 0) жене MISO; решта тримають вихід у високому імпедансі (Z)")

    # спільна шина MISO
    f.append(line(120, 160, 820, 160, color=FIELD, sw=3))
    f.append(text(70, 164, "MISO", size=11.5, color=FIELD, anchor="end", bold=True))
    f.append(text(845, 164, "→ ведучий", size=10.5, color=MUTED, anchor="start"))

    # ведений A — обраний, жене лінію
    f.append(rect(175, 220, 150, 100, fill="#eef6ef", stroke=FIELD, sw=2, rx=10))
    f.append(text(250, 248, "ведений A", size=12, color=FIELD, bold=True))
    f.append(text(250, 272, "CS = 0 (обраний)", size=10.5, color=FIELD, bold=True))
    f.append(text(250, 294, "жене MISO", size=11, color=FIELD, bold=True))
    f.append(line(250, 220, 250, 160, color=FIELD, sw=2.4))
    f.append(circle(250, 160, 4, fill=FIELD, stroke=FIELD, sw=0))

    # ведені B, C — у Z
    for cx, name in [(470, "ведений B"), (690, "ведений C")]:
        f.append(rect(cx - 75, 220, 150, 100, fill="#f4f4f4", stroke=MUTED, sw=2, rx=10))
        f.append(text(cx, 248, name, size=12, color=MUTED, bold=True))
        f.append(text(cx, 272, "CS = 1", size=10.5, color=MUTED, bold=True))
        f.append(text(cx, 294, "вихід = Z (відпущено)", size=10.5, color=MUTED, bold=True))
        f.append(line(cx, 232, cx, 220, color=MUTED, sw=2, dash="3,3"))
        f.append(text(cx, 210, "Z", size=11, color=POS, bold=True))

    f.append(fitbox(60, 340, 780, 44,
                    "Високий імпеданс дає багатьом веденим ділити один MISO: у кожну мить говорить рівно один.",
                    size=12, fill="#eef6ef", stroke=FIELD, bold=True))
    render(os.path.join(IMG, "miso-tristate.svg"), W, H, *f)


# ── 3. CS обрамляє обмін ─────────────────────────────────────────────────────
def fig_cs_framing():
    W, H = 900, 360
    f = [text(W / 2, 34, "CS обрамляє обмін: опустив — почав, підняв — завершив", size=19, bold=True)]
    caption(f, W, 56, "роль, схожа на старт і стоп у I2C, але це фізична лінія, а не сигнал на даних")

    x0, xe = 166, 658
    # CS: високий, провал, високий
    f.append(text(114, 130, "CS", size=12, color=GOLD, anchor="end", bold=True))
    f.append(line(130, 112, x0, 112, color=GOLD, sw=2.6))
    f.append(line(x0, 112, x0, 150, color=GOLD, sw=2.6))
    f.append(line(x0, 150, xe, 150, color=GOLD, sw=2.6))
    f.append(line(xe, 112, xe, 150, color=GOLD, sw=2.6))
    f.append(line(xe, 112, 694, 112, color=GOLD, sw=2.6))

    # SCK — пакет тактів поки CS=0
    f.append(text(114, 210, "SCK", size=12, color=NEG, anchor="end", bold=True))
    f.append(line(130, 230, x0, 230, color=NEG, sw=2.4))
    clk = []
    for _ in range(16):
        clk += [1, 0]
    f.extend(wave(x0, 192, 230, clk, unit=15.0, color=NEG))
    f.append(line(646, 230, 682, 230, color=NEG, sw=2.4))

    # маркери фронтів CS
    f.append(line(x0, 100, x0, 240, color=FIELD, sw=1.2, dash="3,3"))
    f.append(line(xe, 100, xe, 240, color=FIELD, sw=1.2, dash="3,3"))
    f.append(text(x0, 92, "CS↓ старт", size=10.5, color=FIELD, bold=True))
    f.append(text(xe, 92, "CS↑ кінець", size=10.5, color=FIELD, bold=True))
    f.append(text(412, 268, "поки CS = 0 — ведений активний, тактуються байти", size=11.5, bold=True))

    f.append(fitbox(60, 300, 780, 44,
                    "Тримати CS на весь обмін чи смикати на кожне слово — залежить від чіпа.",
                    size=12, fill="#eef6ef", stroke=FIELD, bold=True))
    render(os.path.join(IMG, "cs-framing.svg"), W, H, *f)


# ── 4. Повна картина в часі: обмін байтом ────────────────────────────────────
def fig_waveform():
    W, H = 920, 440
    f = [text(W / 2, 34, "Повна картина в часі: CS, SCK, MOSI, MISO за один байт", size=19, bold=True)]
    caption(f, W, 56, "ведучий жене MOSI, ведений — MISO, обидва біти знімають по фронту SCK — і так 8 разів", size=12)

    x0 = 181.2
    unit = 78.0          # один такт = 2 півперіоди SCK
    half = unit / 2
    xe = x0 + 8 * unit

    # CS — опущений на весь байт
    f.append(text(134, 110, "CS", size=11.5, color=GOLD, anchor="end", bold=True))
    f.append(line(150, 96, x0, 96, color=GOLD, sw=2.2))
    f.append(line(x0, 96, x0, 124, color=GOLD, sw=2.2))
    f.append(line(x0, 124, xe, 124, color=GOLD, sw=2.2))
    f.append(line(xe, 96, xe, 124, color=GOLD, sw=2.2))
    f.append(line(xe, 96, xe + 31, 96, color=GOLD, sw=2.2))

    # SCK — 8 тактів
    f.append(text(134, 185, "SCK", size=11.5, color=NEG, anchor="end", bold=True))
    f.append(line(150, 200, x0, 200, color=NEG, sw=2.2))
    clk = []
    for _ in range(8):
        clk += [1, 0]
    f.extend(wave(x0, 168, 200, clk, unit=half, color=NEG, sw=2.2))

    # MOSI/MISO — біти по тактах, оновлення на межі такту
    mosi_bits = [1, 0, 1, 0, 0, 1, 1, 0]
    miso_bits = [0, 0, 1, 1, 1, 1, 0, 0]

    def databits(label, col, y_hi, y_lo, bits):
        f.append(text(134, (y_hi + y_lo) / 2 + 4, label, size=11.5, color=col, anchor="end", bold=True))
        x = x0
        prev = None
        for b in bits:
            y = y_lo if b else y_hi
            if prev is not None and prev != y:
                f.append(line(x, prev, x, y, color=col, sw=2.4))
            f.append(line(x, y, x + unit, y, color=col, sw=2.4))
            prev = y
            x += unit

    databits("MOSI", POS, 240, 272, mosi_bits)
    databits("MISO", FIELD, 312, 344, miso_bits)

    # пунктир — моменти вибірки (середина такту)
    for i in range(8):
        xs = x0 + i * unit + half
        f.append(line(xs, 168, xs, 344, color=MUTED, sw=0.8, dash="2,3"))
    f.append(text(x0 + 4 * unit, 372,
                  "пунктир — моменти вибірки (тут по фронту SCK; який саме фронт — задає режим CPOL/CPHA)",
                  size=11, color=MUTED, italic=True))

    f.append(fitbox(60, 392, 800, 36,
                    "Усі чотири лінії разом і дають один обмін: вибрав (CS), протактував 8 біт у кожен бік.",
                    size=11.5, fill="#eef6ef", stroke=FIELD, bold=True))
    render(os.path.join(IMG, "waveform.svg"), W, H, *f)


# ── 5. Зоопарк назв (таблиця) ────────────────────────────────────────────────
def fig_naming():
    W, H = 900, 360
    f = [text(W / 2, 34, "Зоопарк назв: ті самі лінії — різні позначення в даташитах", size=19, bold=True)]
    caption(f, W, 56, "дивися на роль (хто жене, у який бік ідуть дані), а не лише на букви")

    cols = [(106, "роль"), (320, "класично"), (490, "інклюзивно"), (650, "на чіпі-веденому")]
    f.append(rect(90, 96, 720, 34, fill="#f0f0f0", stroke=MUTED, sw=1.3))
    for x, t in cols:
        f.append(text(x, 118, t, size=11, color=INK, anchor="start", bold=True))

    rows = [
        ("дані до веденого",  "MOSI",      POS,   "COPI / SDO",  "SDI / DIN"),
        ("дані від веденого", "MISO",      FIELD, "CIPO / SDI",  "SDO / DOUT"),
        ("такт",              "SCK / SCLK",NEG,   "SCK",         "SCK / CLK"),
        ("вибір",             "CS / SS",   GOLD,  "CS",          "CS / nCS / SS"),
    ]
    y = 130
    for role, classic, col, inclusive, onslave in rows:
        f.append(rect(90, y, 720, 44, fill=BG, stroke=MUTED, sw=1, rx=0))
        f.append(text(106, y + 27, role, size=11, color=INK, anchor="start"))
        f.append(text(320, y + 27, classic, size=12, color=col, anchor="start", bold=True))
        f.append(text(490, y + 27, inclusive, size=11.5, color=col, anchor="start"))
        f.append(text(650, y + 27, onslave, size=11.5, color=MUTED, anchor="start"))
        y += 44

    f.append(fitbox(60, 320, 780, 36,
                    "Пастка: на веденому чіпі SDO — це його ВИХІД, тобто MISO; SDI — його вхід, тобто MOSI.",
                    size=11.5, fill="#fbecec", stroke=POS, bold=True))
    render(os.path.join(IMG, "naming.svg"), W, H, *f)


# ── 6. CS робить більше, ніж вибір ───────────────────────────────────────────
def fig_cs_more():
    W, H = 900, 360
    f = [text(W / 2, 34, "CS — не лише «вибір»: він ще й обрамляє команду", size=19, bold=True)]
    caption(f, W, 56, "багато чіпів за фронтом CS скидають внутрішній стан або засувають результат")

    cards = [
        (60,  NEG,   "кадр команди",     ["CS↓ — початок нової команди;", "команда має вкластися, поки CS = 0"]),
        (340, GOLD,  "скидання стану",   ["CS↑ між словами скидає", "внутрішній лічильник або автомат чіпа"]),
        (620, FIELD, "CS на кожне слово",["деякі АЦП хочуть CS-імпульс", "на КОЖЕН вимір (засувка результату)"]),
    ]
    for x, col, title, lines in cards:
        f.append(rect(x, 96, 260, 150, fill="#fbfbfb", stroke=col, sw=2, rx=12))
        f.append(text(x + 130, 124, title, size=12.5, color=col, bold=True))
        f.append(text(x + 130, 156, lines[0], size=10.5, color=INK))
        f.append(text(x + 130, 176, lines[1], size=10.5, color=INK))

    f.append(rect(60, 266, 780, 80, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=10))
    f.append(text(W / 2, 292, "Тому CS не можна тримати завжди опущеним «про запас»: для багатьох чіпів важать саме його ФРОНТИ.",
                  size=11.5, bold=True))
    f.append(text(W / 2, 314, "Звіряйся з даташитом: тримати CS на весь обмін чи смикати на кожне слово.",
                  size=11.5, color=MUTED, italic=True))
    f.append(text(W / 2, 334, "Неправильна робота з CS — другий за частотою глюк SPI (після неправильного режиму CPOL/CPHA).",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "cs-more.svg"), W, H, *f)


# ── 7. Економний варіант: 3-дротовий SPI ─────────────────────────────────────
def fig_3wire():
    W, H = 900, 340
    f = [text(W / 2, 34, "Економний варіант: 3-дротовий SPI (одна лінія даних)", size=19, bold=True)]
    caption(f, W, 56, "MOSI і MISO зливають в одну двонапрямлену лінію — менше дротів, але напівдуплекс")

    # 4-дротовий
    f.append(rect(70, 100, 360, 140, fill="none", stroke="#e4e4e4", sw=2, rx=12))
    f.append(text(250, 124, "4-дротовий (звичайний)", size=12.5, bold=True))
    for yy, col, lab in [(150, NEG, "SCK"), (174, POS, "MOSI"), (198, FIELD, "MISO"), (222, GOLD, "CS")]:
        f.append(line(110, yy, 390, yy, color=col, sw=2))
        f.append(text(100, yy + 4, lab, size=9, color=col, anchor="end", bold=True))
    f.append(text(250, 236, "повний дуплекс, 4 лінії", size=10.5, color=MUTED))

    # 3-дротовий
    f.append(rect(470, 100, 360, 140, fill="none", stroke="#e4e4e4", sw=2, rx=12))
    f.append(text(650, 124, "3-дротовий", size=12.5, bold=True))
    for yy, col, lab in [(156, NEG, "SCK"), (186, PURP, "SDIO"), (216, GOLD, "CS")]:
        f.append(line(510, yy, 790, yy, color=col, sw=2))
        f.append(text(500, yy + 4, lab, size=9, color=col, anchor="end", bold=True))
    f.append(text(650, 200, "дані в обидва боки по черзі", size=9.5, color=PURP, bold=True))
    f.append(text(650, 236, "напівдуплекс, 3 лінії", size=10.5, color=MUTED))

    f.append(rect(60, 262, 780, 56, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=10))
    f.append(text(W / 2, 286, "3-дротовий SPI економить ніжку там, де дані й так ідуть по черзі (багато дисплеїв, дрібні чіпи).",
                  size=11.5, bold=True))
    f.append(text(W / 2, 306, "Той самий компроміс «менше дротів за менше одночасності», що й між I2C та SPI.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "3wire.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА comp-tri-state-buffer
# ════════════════════════════════════════════════════════════════════════════

# ── c1. Три стани виходу й роль OE ───────────────────────────────────────────
def fig_tristate_states():
    W, H = 900, 400
    f = [text(W / 2, 34, "Три стани виходу: «0», «1» і відключено (Z)", size=19, bold=True)]
    caption(f, W, 56, "вхід OE (вмикання виходу) вирішує: тягнути лінію чи відпустити її в Z")

    # три буфери: OE=1 жене 1, OE=1 жене 0, OE=0 → Z
    states = [
        (190, "OE = 1, вхід = 1", "жене «1»", POS,   "1", "#fdecea", POS),
        (450, "OE = 1, вхід = 0", "жене «0»", NEG,   "0", "#eaf0fd", NEG),
        (710, "OE = 0",           "вихід у Z","#8a8a8a", "Z", "#f4f4f4", MUTED),
    ]
    for cx, top, mid, col, sym, fill, scol in states:
        # трикутник-буфер
        f.append('<path d="M%d,%d L%d,%d L%d,%d Z" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (cx - 34, 150, cx - 34, 214, cx + 38, 182, fill, scol))
        f.append(text(cx, 130, top, size=11, color=INK, bold=True))
        f.append(text(cx - 10, 188, sym, size=18, color=col, bold=True))
        # лінія від буфера праворуч
        dash = ' stroke-dasharray="4,4"' if sym == "Z" else ''
        f.append('<line x1="%d" y1="182" x2="%d" y2="182" stroke="%s" stroke-width="2.4"%s/>'
                 % (cx + 38, cx + 78, col, dash))
        f.append(text(cx + 2, 246, mid, size=11.5, color=scol, bold=True))
        # позначка OE знизу
        f.append(text(cx, 150 - 28, "OE", size=10, color=MUTED))
        f.append(line(cx, 150 - 24, cx, 150, color=MUTED, sw=1.2, dash="2,2"))

    f.append(fitbox(60, 300, 780, 64,
                    ["Звичайний двотактний вихід уміє лише «0» і «1» — він завжди тягне лінію. Третій стан додає",
                     "вибір «нічого»: за OE = 0 транзистори замкнені обидва, вихід має дуже високий опір (Z) і для",
                     "лінії наче зник. Це й дозволяє кільком виходам ділити один провід — за умови, що активний лише один."],
                    size=12, fill=FILL))
    render(os.path.join(IMG, "tristate-states.svg"), W, H, *f)


if __name__ == "__main__":
    # стаття
    fig_who_drives()
    fig_miso_tristate()
    fig_cs_framing()
    fig_waveform()
    fig_naming()
    fig_cs_more()
    fig_3wire()
    # вставка
    fig_tristate_states()
    print("OK: figures written to", IMG)
