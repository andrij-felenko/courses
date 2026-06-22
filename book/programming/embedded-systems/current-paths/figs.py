# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Куди тече струм».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: карта п'яти споживачів струму ──────────────────────────────────
# Серце статті. Струм від батареї проходить стабілізатор і розгалужується на
# п'ять доменів. Радіо виділено як домінанту в передачі — там і найбільший
# важіль економії. Числа — типові орієнтири для ESP32.
def fig_current_map():
    W, H = 760, 430
    parts = []

    # батарея ліворуч
    bx, by = 70, H / 2 - 28
    parts.append(rect(bx, by, 96, 56, fill="#d6eaf8", stroke=NEG, sw=2.5))
    parts.append(mtext(bx + 48, by + 23, ["Батарея", "3.7 В"], size=13,
                       color=NEG, bold=True))

    # стабілізатор (LDO) посередині
    lx, ly = 210, H / 2 - 26
    parts.append(line(bx + 96, H / 2, lx, H / 2, color=FIELD, sw=3))
    parts.append(rect(lx, ly, 84, 52, fill="#eafaf1", stroke=FIELD, sw=2))
    parts.append(mtext(lx + 42, ly + 21, ["LDO", "стабіл."], size=12,
                       color=FIELD, bold=True))

    # вузол розгалуження
    nx = lx + 84 + 18
    ny = H / 2
    parts.append(circle(nx, ny, 5, fill=INK, stroke=INK, sw=1))

    # п'ять доменів праворуч
    dom = [
        ("Ядра", "20–40 мА у роботі", NEG, "#d6eaf8", 70),
        ("Радіо", "150–250 мА у TX  ← домінанта", POS, "#fdecea", 150),
        ("Периферія", "1–10 мА при тактуванні", FIELD, "#eafaf1", 230),
        ("Витоки", "одиниці мкА, ростуть з T°", "#8e44ad", "#f5eef8", 310),
        ("Стабілізатор Iq", "власний струм спокою", MUTED, "#f1f3f5", 390),
    ]
    bx2 = 430
    bw2 = 270
    bh2 = 46
    for name, note, col, fill, cy in dom:
        # лінія від вузла до домену
        parts.append(line(nx, ny, bx2 - 10, cy + bh2 / 2, color=MUTED, sw=1.4))
        parts.append(rect(bx2, cy, bw2, bh2, fill=fill, stroke=col, sw=2, rx=6))
        parts.append(text(bx2 + 12, cy + 20, name, size=13, color=col,
                          anchor="start", bold=True))
        parts.append(text(bx2 + 12, cy + 37, note, size=11, color=INK,
                          anchor="start"))

    box, bw, bh = textbox(W / 2, H - 22,
                          "Перший важіль економії — зрідити або вимкнути РАДІО: у передачі воно перевершує решту на порядки",
                          size=12.5, pad=10, fill="#fdecea", stroke=POS, sw=1.6, bold=True)
    parts.append(box)

    render("img/current-map.svg", W, H, *parts,
           title="Куди тече струм: п'ять споживачів чипа")


# ── Фігура 2: дві природи струму (динамічний vs статичний) ───────────────────
# Чому сон узагалі працює. Ліворуч — динамічний струм (на перемикання, ∝ f·C·V²),
# зникає зі спиненням такту → це light-sleep. Праворуч — статичний витік, тече
# завжди при наявній напрузі, прибрати можна лише знявши живлення → deep-sleep.
def fig_dynamic_vs_static():
    W, H = 700, 420
    parts = []

    midx = W / 2
    parts.append(line(midx, 50, midx, H - 70, color=MUTED, sw=1, dash="5,4"))

    def column(cx, head, head_col, fill, rows, foot):
        parts.append(rect(cx - 150, 48, 300, 40, fill=fill, stroke=head_col, sw=2.5))
        parts.append(text(cx, 74, head, size=16, color=head_col, bold=True))
        y = 110
        for r in rows:
            box, bw, bh = textbox(cx, y, r, size=12, pad=8, fill=fill,
                                  stroke=head_col, sw=1.0)
            parts.append(box)
            y += 40
        parts.append(line(cx, y - 12, cx, y + 18, color=head_col, sw=2))
        # стрілку малюємо вручну, бо колір не дефолтний
        parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="2" marker-end="url(#arrow)"/>'
                     % (cx, y - 12, cx, y + 18, head_col))
        box2, bw2, bh2 = textbox(cx, y + 44, foot, size=12, pad=9, fill=fill,
                                 stroke=head_col, sw=2, bold=True)
        parts.append(box2)

    column(midx / 2 + 20, "ДИНАМІЧНИЙ", NEG, "#d6eaf8",
           ["P ∝ f · C · V²",
            "тільки на перемикання",
            "гейтинг тактів → ≈ 0"],
           ["вимикає LIGHT-SLEEP", "(такти стоять)"])

    column(midx + midx / 2 - 20, "СТАТИЧНИЙ / витік", POS, "#fdecea",
           ["тече завжди, доки є V",
            "не залежить від такту",
            "росте з температурою"],
           ["вимикає DEEP-SLEEP", "(знімає живлення)"])

    render("img/dynamic-vs-static.svg", W, H, *parts,
           title="Дві природи струму: чому сон працює, а deep — глибше")


# ── Фігура 3: п'ять порядків між TX і hibernation ────────────────────────────
# Найважливіше число статті: динамічний діапазон 10⁵ між Wi-Fi TX і сном.
# Логарифмічна шкала; кожен стан — горизонтальна позначка з підписом.
def fig_orders_of_magnitude():
    import math
    W, H = 720, 430
    parts = []

    axx = 175
    top, bot = 60, H - 80
    parts.append(line(axx, bot, axx, top - 6, color=LINE, sw=1.6))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.6" marker-end="url(#arrow)"/>'
                 % (axx, bot, axx, top - 6, LINE))
    parts.append(text(axx, top - 18, "струм, лог. шкала", size=12, color=MUTED))

    # десяткові орієнтири мкА → лог; від 1 мкА (низ) до 1e6 мкА = 1 А (верх)
    lo_log, hi_log = 0.0, 6.0  # log10(мкА)

    def y_of(ua):
        f = (math.log10(ua) - lo_log) / (hi_log - lo_log)
        return bot - f * (bot - top)

    states = [
        ("Wi-Fi TX пік", "≈ 250 мА", 250000.0, POS, "#fdecea"),
        ("Активне ядро", "≈ 35 мА", 35000.0, "#e67e22", "#fdf2e9"),
        ("Light-sleep", "≈ 0.8 мА", 800.0, FIELD, "#eafaf1"),
        ("Deep-sleep", "≈ 8 мкА", 8.0, NEG, "#d6eaf8"),
        ("Hibernation", "≈ 2.5 мкА", 2.5, "#8e44ad", "#f5eef8"),
    ]
    for name, val, ua, col, fill in states:
        y = y_of(ua)
        parts.append(line(axx - 8, y, axx, y, color=col, sw=2))
        parts.append(line(axx, y, axx + 360, y, color=MUTED, sw=0.5, dash="3,5"))
        parts.append(circle(axx, y, 5, fill=col, stroke=col, sw=0))
        parts.append(rect(axx + 200, y - 20, 175, 40, fill=fill, stroke=col, sw=1.8))
        parts.append(text(axx + 212, y - 2, name, size=12.5, color=col,
                          anchor="start", bold=True))
        parts.append(text(axx + 212, y + 15, val, size=12, color=INK,
                          anchor="start"))

    # дужка «5 порядків» між TX і hibernation
    ytx = y_of(250000.0)
    yhib = y_of(2.5)
    brx = axx + 150
    parts.append(line(brx, ytx, brx, yhib, color=FIELD, sw=2.5))
    parts.append(line(brx - 8, ytx, brx + 8, ytx, color=FIELD, sw=2))
    parts.append(line(brx - 8, yhib, brx + 8, yhib, color=FIELD, sw=2))
    parts.append(mtext(brx - 14, (ytx + yhib) / 2, ["5", "порядків", "10⁵"],
                       size=12, color=FIELD, anchor="end", bold=True))

    box, bw, bh = textbox(W / 2, H - 34,
                          ["Діапазон 10⁵ — і причина величезного виграшу від сну,",
                           "і причина, чому виміряти струм одним приладом важко"],
                          size=12, pad=9, fill="#f1f3f5", stroke=MUTED, sw=1.2)
    parts.append(box)

    render("img/orders-of-magnitude.svg", W, H, *parts,
           title="ESP32: п'ять порядків між передачею і сном")


# ═════════════════════════════════════════════════════════════════════════════
#  Фігури вставки comp-sensor-standby (🔌)
# ═════════════════════════════════════════════════════════════════════════════

# ── standby-map: лог-шкала струмів давачів проти сплячого МК ──────────────────
# Головна думка вставки: один забутий у normal давач (185 µA) перевершує весь
# сплячий ESP32 (одиниці µA). Горизонтальні смужки на лог-шкалі.
def fig_sensor_standby_map():
    import math
    W, H = 760, 430
    parts = []

    axx = 250
    top, bot = 60, H - 90
    # лог-шкала від 0.1 до 200 µA
    lo, hi = -1.0, math.log10(200.0)

    def x_of(ua):
        f = (math.log10(ua) - lo) / (hi - lo)
        return axx + f * (W - axx - 60)

    for tick in (0.1, 1, 10, 100, 200):
        x = x_of(tick)
        parts.append(line(x, top, x, bot, color="#d1d5db", sw=0.8, dash="3,3"))
        lab = ("%g" % tick)
        parts.append(text(x, bot + 16, lab, size=10, color=MUTED))
    parts.append(text((axx + W - 60) / 2, bot + 34,
                      "середній струм, µA (лог. шкала)", size=11, color=MUTED))

    rows = [
        ("ESP32 deep-sleep", "(МК спить)", 5.0, NEG),
        ("BME280 sleep", "≈0.1 µA", 0.1, FIELD),
        ("LIS3DH power-down", "≈0.5 µA", 0.5, FIELD),
        ("LIS3DH low-power 10 Hz", "≈2 µA", 2.0, FIELD),
        ("BME280 forced", "≈2.8 µA сер.", 2.8, "#e67e22"),
        ("BME280 normal", "≈3.6 µA", 3.6, POS),
        ("LIS3DH normal / HR", "≈185 µA", 185.0, POS),
    ]
    y = top + 8
    bh = (bot - top - 20) / len(rows)
    for name, val, ua, col in rows:
        cy = y + bh / 2
        fill = "#fdecea" if col == POS else ("#fdf2e9" if col == "#e67e22" else "#eafaf1")
        x = x_of(ua)
        parts.append(rect(axx, cy - 11, max(2.0, x - axx), 22, fill=fill, stroke=col, sw=1.5, rx=3))
        parts.append(text(x + 6, cy + 4, val, size=10, color=col, anchor="start", bold=True))
        parts.append(text(axx - 10, cy + 4, name, size=11, color=INK, anchor="end"))
        y += bh

    box, bw2, bh2 = textbox((axx + W) / 2 - 30, top + 4,
                            "Один давач у normal > весь сплячий МК",
                            size=11, pad=7, fill="#fff3cd", stroke="#e67e22", sw=1.5, bold=True)
    parts.append(box)

    render("img/sensor-standby-map.svg", W, H, *parts,
           title="Карта струму: МК спить — давачі можуть ні")


# ── mode-states: автомат режимів давача й струм у кожному ────────────────────
# Три стани (sleep / forced / normal) і переходи; петля forced→sleep — фундамент
# скважності. Підписи стрілок — що пишемо в регістр.
def fig_sensor_mode_states():
    W, H = 720, 420
    parts = []

    sleep = (140, H / 2)
    forced = (400, 110)
    normal = (400, H - 110)

    def node(cx, cy, title, l1, l2, col, fill):
        w, h = 190, 74
        parts.append(rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=col, sw=2, rx=10))
        parts.append(text(cx, cy - 14, title, size=12, color=col, bold=True))
        parts.append(text(cx, cy + 5, l1, size=12, color=col))
        parts.append(text(cx, cy + 22, l2, size=12, color=col))

    node(*sleep, "sleep / power-down", "BME ≈0.1 µA", "LIS ≈0.5 µA", FIELD, "#eafaf1")
    node(*forced, "forced / one-shot", "(один вимір)", "≈ кілька µA сер.", "#e67e22", "#fdf2e9")
    node(*normal, "normal / continuous", "BME ≈3.6 µA", "LIS ≈185 µA", POS, "#fdecea")

    def edge(a, b, col, label):
        parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="1.8" marker-end="url(#arrow)"/>'
                     % (a[0] + 60, a[1] - 18, b[0] - 95, b[1] + 10, col))

    # sleep ↔ forced
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.8" marker-end="url(#arrow)"/>'
                 % (sleep[0] + 70, sleep[1] - 24, forced[0] - 96, forced[1] + 20, "#e67e22"))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.8" marker-end="url(#arrow)"/>'
                 % (forced[0] - 96, forced[1] + 34, sleep[0] + 70, sleep[1] - 38, FIELD))
    b, bw, bh = textbox(258, 150, ["forced: 0xF4←0x01", "сам у sleep"], size=10,
                        pad=6, fill="#fdf2e9", stroke="#e67e22", sw=1.0)
    parts.append(b)

    # sleep ↔ normal
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.8" marker-end="url(#arrow)"/>'
                 % (sleep[0] + 70, sleep[1] + 24, normal[0] - 96, normal[1] - 20, POS))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.8" marker-end="url(#arrow)"/>'
                 % (normal[0] - 96, normal[1] - 34, sleep[0] + 70, sleep[1] + 38, FIELD))
    b2, bw2, bh2 = textbox(258, H - 150, ["normal: 0xF4←0xB7", "sleep: ←0x00"], size=10,
                           pad=6, fill="#eafaf1", stroke=FIELD, sw=1.0)
    parts.append(b2)

    # петля forced→sleep підкреслена
    b3, bw3, bh3 = textbox(560, 110, ["петля forced → sleep:", "основа скважності"],
                           size=11, pad=8, fill="#fff3cd", stroke="#e67e22", sw=1.5, bold=True)
    parts.append(b3)

    render("img/sensor-mode-states.svg", W, H, *parts,
           title="Режими давача: один байт у регістрі — різниця на порядки")


# ═════════════════════════════════════════════════════════════════════════════
#  Фігури вставки hist-voyager (📜)
# ═════════════════════════════════════════════════════════════════════════════

# ── rtg: як гаряча грудка ²³⁸Pu робить струм (і де дві майбутні втрати) ───────
def fig_rtg():
    W, H = 820, 440
    parts = []

    # грудка пального ліворуч
    fx, fy = 150, 230
    parts.append(circle(fx, fy, 50, fill="#fef3e2", stroke="#8B4513", sw=3))
    parts.append(circle(fx, fy, 28, fill="#f9a825", stroke="#8B4513", sw=1.5))
    parts.append(mtext(fx, fy - 2, ["²³⁸Pu", "пальне"], size=12, color="#8B4513", bold=True))
    parts.append(mtext(fx, fy + 78, ["радіоактивний розпад", "→ постійне тепло"],
                       size=10, color=MUTED))

    # тепловий потік
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="2.5" marker-end="url(#arrow)"/>' % (fx + 52, fy, 250, fy, POS))
    parts.append(text(225, fy - 12, "Q (тепло)", size=10, color=POS))

    # гарячий бік
    parts.append(rect(255, 165, 42, 130, fill="#fdecea", stroke=POS, sw=2.5))
    parts.append(mtext(276, 222, ["гарячий", "бік T_h"], size=11, color=POS, bold=True))

    # термопари SiGe (центр)
    parts.append(rect(300, 165, 150, 130, fill="#f0fdf4", stroke=FIELD, sw=2))
    parts.append(mtext(375, 215, ["SiGe", "термопари", "(ефект Зеебека)"], size=11,
                       color=FIELD, bold=True))

    # холодний бік + радіатор
    parts.append(rect(453, 165, 42, 130, fill="#eaf0fd", stroke=NEG, sw=2.5))
    parts.append(mtext(474, 222, ["холодн.", "бік T_c"], size=11, color=NEG, bold=True))
    parts.append(rect(498, 165, 70, 130, fill="#e8eaf6", stroke=NEG, sw=1.5))
    parts.append(text(533, 222, "радіатор", size=11, color=NEG))
    parts.append(text(533, 240, "→ космос", size=10, color=MUTED))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="2" marker-end="url(#arrow)"/>' % (570, fy, 605, fy, NEG))

    # клеми напруги
    parts.append(plus(375, 135, 9))
    parts.append(minus(375, 325, 9))
    parts.append(line(375, 156, 375, 146, color=INK, sw=1.5))
    parts.append(line(375, 304, 375, 314, color=INK, sw=1.5))

    # дві втрати (рамки)
    b1, bw1, bh1 = textbox(150, 90, ["Втрата 1: ²³⁸Pu розпадається",
                                     "−0.79 %/рік теплової потужності"],
                           size=10, pad=7, fill="#fff8e1", stroke="#e67e22", sw=1.5)
    parts.append(b1)
    parts.append(line(150, 110, 150, 178, color="#e67e22", sw=1.2, dash="4,3"))

    b2, bw2, bh2 = textbox(390, 360, ["Втрата 2: термопари старіють",
                                      "(ефективність спадає — БІЛЬША!)"],
                           size=10, pad=7, fill="#fff8e1", stroke="#e67e22", sw=1.5)
    parts.append(b2)
    parts.append(line(390, 340, 390, 300, color="#e67e22", sw=1.2, dash="4,3"))

    box, bw, bh = textbox(W / 2, H - 24,
                          "Напруга народжується з різниці T_h − T_c; обидва майбутні джерела згасання — тут",
                          size=11, pad=9, fill="#fafafa", stroke=MUTED, sw=1.2)
    parts.append(box)

    render("img/rtg.svg", W, H, *parts,
           title="RTG: як гаряча грудка плутонію-238 робить струм")


# ── two-leaks: дві діри бюджету RTG і їхній аналог на карті чипа ──────────────
def fig_two_leaks():
    W, H = 860, 430
    parts = []

    # ── ліворуч: RTG ──
    parts.append(text(150, 56, "RTG «Вояджера»", size=13, bold=True))
    parts.append(rect(60, 78, 175, 210, fill="#fef9ec", stroke=POS, sw=2.5))
    parts.append(mtext(147, 110, ["теплова", "потужність", "(RTG)"], size=12, color=POS, bold=True))
    parts.append(text(147, 175, "Q_rtg", size=20, color="#e67e22", bold=True))
    # дві текучі діри (стовпчики)
    parts.append(rect(82, 200, 20, 64, fill="#fdecea", stroke=POS, sw=2, rx=3))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.5" marker-end="url(#arrow)"/>' % (92, 264, 92, 286, POS))
    parts.append(mtext(92, 300, ["розпад", "пального"], size=9, color=POS))
    parts.append(rect(140, 196, 36, 68, fill="#fff3e0", stroke="#e67e22", sw=2.5, rx=3))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="2" marker-end="url(#arrow)"/>' % (158, 264, 158, 290, "#e67e22"))
    parts.append(mtext(158, 304, ["термопари", "(більша!)"], size=9, color="#e67e22"))

    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="3" marker-end="url(#arrow)"/>' % (237, 150, 280, 150, FIELD))
    b, bw, bh = textbox(330, 165, ["вихідна електрика", "~470 Вт (1977)", "→ ~232 Вт (2025)"],
                        size=11, pad=8, fill="#f0fdf4", stroke=FIELD, sw=1.5, bold=True)
    parts.append(b)

    # ── роздільник «аналог» ──
    parts.append(line(450, 60, 450, 360, color=MUTED, sw=1.2, dash="6,5"))
    parts.append(text(450, 48, "аналог", size=12, color=MUTED, italic=True))

    # ── праворуч: карта чипа ──
    parts.append(text(660, 56, "Карта споживання чипа", size=13, bold=True))
    parts.append(rect(560, 78, 195, 175, fill="#f8f9fa", stroke=INK, sw=2))
    parts.append(text(657, 100, "ESP32 чип", size=12, bold=True))
    parts.append(rect(572, 112, 82, 46, fill="#eafaf1", stroke=NEG, sw=1.5))
    parts.append(mtext(613, 132, ["ядро", "+ радіо"], size=11, color=NEG))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.8" marker-end="url(#arrow)"/>' % (613, 158, 613, 180, NEG))
    parts.append(mtext(613, 196, ["корисне", "(«замовлене»)"], size=9, color=NEG))
    parts.append(rect(662, 112, 82, 46, fill="#f5eef8", stroke="#8e44ad", sw=1.5))
    parts.append(mtext(703, 132, ["витоки", "+ Iq LDO"], size=11, color="#8e44ad"))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="2" marker-end="url(#arrow)"/>' % (703, 158, 703, 180, "#8e44ad"))
    parts.append(mtext(703, 196, ["тіньове", "(«незамовлене»)"], size=9, color="#8e44ad"))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="2" marker-end="url(#arrow)"/>' % (657, 253, 657, 285, INK))
    parts.append(text(657, 301, "I_total", size=11, bold=True))

    box, bw2, bh2 = textbox(W / 2, H - 24,
                            "Головна втрата — не там, де «витрачають», а де «втрачають»: термопари ↔ витоки транзисторів",
                            size=11, pad=9, fill="#f9fafb", stroke=MUTED, sw=1.2)
    parts.append(box)

    render("img/two-leaks.svg", W, H, *parts,
           title="Дві діри бюджету RTG та їхній аналог на карті чипа")


# ── budget-timeline: плавне згасання RTG проти дискретних вимикань ────────────
def fig_budget_timeline():
    W, H = 880, 460
    parts = []

    ox, oy = 90, 340      # початок осей
    rt = 800              # права межа
    tp = 50               # верх

    # осі
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.5" marker-end="url(#arrow)"/>' % (ox, oy, rt, oy, MUTED))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.5" marker-end="url(#arrow)"/>' % (ox, oy + 5, ox, tp, MUTED))
    parts.append(text(460, 372, "рік", size=11, color=MUTED))
    parts.append(text(46, 195, "Вт", size=11, color=MUTED))

    # шкала років 1977..2025
    yr0, yr1 = 1977, 2025
    def x_of(yr):
        return ox + (yr - yr0) / (yr1 - yr0) * (rt - 30 - ox)
    for yr in (1977, 1985, 1995, 2005, 2015, 2025):
        x = x_of(yr)
        parts.append(line(x, oy, x, oy + 5, color=MUTED, sw=1))
        parts.append(text(x, oy + 18, str(yr), size=10, color=MUTED))

    # шкала ват 0..470
    def y_of(w):
        return oy - w / 470.0 * (oy - tp - 10)
    for w in (0, 100, 200, 300, 400):
        y = y_of(w)
        parts.append(line(ox - 5, y, ox, y, color=MUTED, sw=1))
        parts.append(text(ox - 16, y + 4, str(w), size=10, color=MUTED, anchor="end"))

    # «дно»: передавач + критичний обігрів
    yfloor = y_of(140)
    parts.append(line(ox, yfloor, rt - 30, yfloor, color=NEG, sw=1.5, dash="8,5"))
    b, bw, bh = textbox(230, yfloor - 13, "«дно»: передавач + критичний обігрів",
                        size=10, pad=6, fill="#eaf0fd", stroke=NEG, sw=1.5)
    parts.append(b)

    # спадна крива (лінійна 470 → 232 за 48 років)
    import math
    pts = []
    for yr in range(1977, 2026):
        w = 470 - 4 * (yr - 1977)
        pts.append((x_of(yr), y_of(w)))
    for i in range(len(pts) - 1):
        parts.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=POS, sw=2.5))
    parts.append(circle(x_of(1977), y_of(470), 5, fill=POS, stroke=POS, sw=1.5))
    b1, bw1, bh1 = textbox(140, y_of(470) - 22, "1977: старт ~470 Вт",
                           size=10, pad=6, fill="#fdecea", stroke=POS, sw=1.5)
    parts.append(b1)
    parts.append(circle(x_of(2025), y_of(278), 5, fill=POS, stroke=POS, sw=1.5))
    b2, bw2, bh2 = textbox(720, y_of(278) - 26, "~232 Вт (2025)",
                           size=10, pad=6, fill="#fdecea", stroke=POS, sw=1.5)
    parts.append(b2)

    # дискретні вимикання (виноски під кривою)
    events = [
        (1990, "вимкнено нагрівачі", "(прилади нижче −79 °C)", 250),
        (2025, "−CRS", "2025-02-25", 300),
        (2025, "−LECP", "2025-03-24", 360),
    ]
    for yr, l1, l2, ylab in events:
        x = x_of(yr)
        w = 470 - 4 * (yr - 1977)
        parts.append(circle(x, y_of(w), 5, fill=FIELD, stroke=FIELD, sw=1.5))
        bx = min(max(x, 150), 720)
        bb, bbw, bbh = textbox(bx, ylab, [l1, l2], size=9, pad=6,
                               fill="#f0fdf4", stroke=FIELD, sw=1.2)
        parts.append(bb)
        parts.append(line(x, y_of(w), bx, ylab - 14, color=FIELD, sw=1.0, dash="3,3"))

    box, bw3, bh3 = textbox(W / 2, H - 22,
                            "Крива тане безперервно; сходинки — навмисні скидання споживачів: інженери женуться за лінією, що падає",
                            size=11, pad=9, fill="#f9fafb", stroke=MUTED, sw=1.2)
    parts.append(box)

    render("img/budget-timeline.svg", W, H, *parts,
           title="Бюджет «Вояджерів»: згасання й дискретні вимикання")


if __name__ == "__main__":
    fig_current_map()
    fig_dynamic_vs_static()
    fig_orders_of_magnitude()
    fig_sensor_standby_map()
    fig_sensor_mode_states()
    fig_rtg()
    fig_two_leaks()
    fig_budget_timeline()
    print("OK: current-map, dynamic-vs-static, orders-of-magnitude, "
          "sensor-standby-map, sensor-mode-states, rtg, two-leaks, budget-timeline")
