# -*- coding: utf-8 -*-
"""Фігури до теми «FSK і PSK» (fsk-psk).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

AMB = "#b08900"   # бурштиновий — для QAM/третього стану (поза палітрою +/−/поле)


def wave(x0, y, x1, step, amp, cycles_per_step, color, sw=1.9):
    """Синусоїда від x0 до x1 уздовж низки тактів завширшки step кожен.
    cycles_per_step — список: скільки періодів вкладається в кожен такт
    (так кодуємо ASK амплітудою, FSK/PSK — частотою/фазою). Повертає <path>."""
    pts = []
    x = x0
    seg = 0
    while x < x1 - 1e-9:
        c = cycles_per_step[seg] if seg < len(cycles_per_step) else cycles_per_step[-1]
        a = amp[seg] if isinstance(amp, list) else amp
        ph = 0.0
        # фазовий злам PSK задається від'ємними «періодами» — обробляє caller
        n = 24
        for i in range(n + 1):
            t = i / n
            xx = x + t * step
            yy = y - a * math.sin(2 * math.pi * c * t)
            pts.append("%.1f,%.1f" % (xx, yy))
        x += step
        seg += 1
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (" ".join(pts), color, sw))


def psk_wave(x0, y, step, bits, amp, cyc, color, sw=1.9):
    """PSK: стала амплітуда й частота, але на кожній зміні біта фаза +180°."""
    pts = []
    x = x0
    phase = 0.0
    prev = None
    n = 24
    for b in bits:
        if prev is not None and b != prev:
            phase += math.pi          # розворот фази на межі біта
        for i in range(n + 1):
            t = i / n
            xx = x + t * step
            yy = y - amp * math.sin(2 * math.pi * cyc * t + phase)
            pts.append("%.1f,%.1f" % (xx, yy))
        x += step
        prev = b
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (" ".join(pts), color, sw))


# ── 1. Три ручки стають дискретними: ASK / FSK / PSK на однім потоці бітів ─────
# Ідея, яку важко сказати словами: один і той самий потік нулів/одиниць
# по-різному «лягає» на несучу — амплітудою, частотою або фазою.
def fig_keyings():
    W, H = 900, 470
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    x0, step = 70, 96
    f = []

    # сітка тактів + підписи бітів
    f.append(text(40, 92, "біти:", 11, INK, "start", bold=True))
    for i, b in enumerate(bits):
        cx = x0 + i * step + step / 2
        f.append(text(cx, 92, str(b), 13, INK, "middle", bold=True))
        f.append(line(x0 + i * step, 100, x0 + i * step, 430, color="#e4e4e4", sw=1, dash="3 3"))
    f.append(line(x0 + len(bits) * step, 100, x0 + len(bits) * step, 430, color="#e4e4e4", sw=1, dash="3 3"))

    x1 = x0 + len(bits) * step

    # ASK: амплітуда 1 → повна, 0 → майже нуль; частота стала
    yA = 158
    f.append(text(40, yA - 8, "ASK", 12, POS, "start", bold=True))
    f.append(text(40, yA + 8, "(амплітуда)", 9, MUTED, "start"))
    ampA = [30 if b else 3 for b in bits]
    f.append(wave(x0, yA, x1, step, ampA, [4] * len(bits), POS))

    # FSK: 1 → густіша (більше періодів), 0 → рідша; амплітуда стала
    yF = 266
    f.append(text(40, yF - 8, "FSK", 12, FIELD, "start", bold=True))
    f.append(text(40, yF + 8, "(частота)", 9, MUTED, "start"))
    cycF = [6 if b else 3 for b in bits]
    f.append(wave(x0, yF, x1, step, 30, cycF, FIELD))

    # PSK: стала амплітуда й частота, розворот фази на межі біта
    yP = 374
    f.append(text(40, yP - 8, "PSK", 12, NEG, "start", bold=True))
    f.append(text(40, yP + 8, "(фаза)", 9, MUTED, "start"))
    f.append(psk_wave(x0, yP, step, bits, 30, 4, NEG))
    # позначка розвороту на першій зміні біта (між 1-м і 2-м тактом)
    fx = x0 + 1 * step
    f.append(line(fx, yP - 40, fx, yP + 40, color=NEG, sw=1, dash="4 3"))
    f.append(text(fx + 6, yP + 56, "↑ розворот фази на межі біта", 10, NEG, "start", bold=True))

    render(os.path.join(IMG, "keyings.svg"), W, H, *f,
           title="Цифрова модуляція: ті самі три ручки, але дискретно")


# ── 2. Символ і біт: один стан несе log₂M бітів ───────────────────────────────
# Ідея: подвоїти кількість станів символу = додати рівно один біт на символ.
def fig_symbols():
    W, H = 900, 384
    rows = [
        ("BPSK",   2,   1, NEG),
        ("QPSK",   4,   2, FIELD),
        ("8-PSK",  8,   3, AMB),
        ("16-QAM", 16,  4, POS),
        ("256-QAM", 256, 8, INK),
    ]
    f = []
    # шапка таблиці
    cols = [185, 420, 660]
    head = ["схема", "станів M", "біт на символ = log₂M"]
    for cx, h in zip(cols, head):
        f.append(text(cx, 84, h, 12, MUTED, "middle", bold=True))
    f.append(line(70, 94, 830, 94, color="#d8dde3", sw=1.3))

    y = 118
    for name, M, b, col in rows:
        f.append(text(cols[0], y + 6, name, 13.5, col, "middle", bold=True))
        f.append(text(cols[1], y + 6, str(M), 13, INK, "middle"))
        # стовпчик «вантажності»: b клітинок
        bx = cols[2] - 90
        for k in range(b):
            f.append(rect(bx + k * 21, y - 8, 17, 17, fill="#eef6ef", stroke=col, sw=1.6, rx=3))
        f.append(text(cols[2] + 96, y + 6, "%d біт" % b, 12, col, "middle", bold=True))
        y += 44

    f.append(rect(70, y + 2, 760, 30, fill="#eef6ef", stroke=FIELD, sw=1.3, rx=8))
    f.append(text(450, y + 22, "Подвоїти кількість станів — це додати рівно один біт на символ.",
                  12, INK, "middle", bold=True))

    render(os.path.join(IMG, "symbols.svg"), W, H, *f,
           title="Символ і біт: один стан несучої може нести кілька бітів")


# ── 3. Сузір'я: карта станів несучої на площині I/Q ───────────────────────────
# Ідея: точка на площині I/Q = амплітуда (відстань від центру) + фаза (кут).
def fig_constellation():
    W, H = 900, 360
    f = []

    def axes(cx, cy, r):
        f.append(line(cx - r - 14, cy, cx + r + 14, cy, color=MUTED, sw=1.4))
        f.append(line(cx, cy + r + 14, cx, cy - r - 14, color=MUTED, sw=1.4))
        f.append(text(cx + r + 22, cy + 4, "I", 11, MUTED, "middle"))
        f.append(text(cx + 8, cy - r - 16, "Q", 11, MUTED, "middle"))

    def dot(cx, cy, col, r=5):
        f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, col))

    # BPSK: дві точки на осі I
    cx, cy, r = 165, 195, 60
    axes(cx, cy, r)
    dot(cx - 0.7 * r, cy, NEG); dot(cx + 0.7 * r, cy, NEG)
    f.append(text(cx, 295, "BPSK — 2 точки", 12.5, NEG, "middle", bold=True))
    f.append(text(cx, 314, "1 біт/символ", 10.5, MUTED, "middle"))

    # QPSK: чотири точки квадратом
    cx, cy, r = 450, 195, 60
    axes(cx, cy, r)
    for sx in (-1, 1):
        for sy in (-1, 1):
            dot(cx + sx * 0.62 * r, cy - sy * 0.62 * r, FIELD)
    f.append(text(cx, 295, "QPSK — 4 точки", 12.5, FIELD, "middle", bold=True))
    f.append(text(cx, 314, "2 біти/символ", 10.5, MUTED, "middle"))

    # 16-QAM: сітка 4×4 (фаза + амплітуда)
    cx, cy, r = 735, 195, 60
    axes(cx, cy, r)
    grid = [-0.78, -0.26, 0.26, 0.78]
    for gi in grid:
        for gj in grid:
            dot(cx + gi * r, cy - gj * r, AMB, r=4)
    f.append(text(cx, 295, "16-QAM — 16 точок", 12.5, AMB, "middle", bold=True))
    f.append(text(cx, 314, "4 біти/символ", 10.5, MUTED, "middle"))

    render(os.path.join(IMG, "constellation.svg"), W, H, *f,
           title="Сузір'я: карта станів несучої на площині I/Q")


# ── 4. Чому не ущільнювати нескінченно: шум розмиває точки в «хмарки» ──────────
def fig_noise():
    W, H = 900, 380
    f = []

    def dot_cloud(cx, cy, col, cloud, r=4):
        f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.1"/>'
                 % (cx, cy, cloud, col))
        f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, col))

    # QPSK ліворуч — хмарки далеко, не торкаються
    cx, cy, r = 230, 200, 70
    f.append(line(cx - r - 10, cy, cx + r + 10, cy, color=MUTED, sw=1.2))
    f.append(line(cx, cy + r + 10, cx, cy - r - 10, color=MUTED, sw=1.2))
    for sx in (-1, 1):
        for sy in (-1, 1):
            dot_cloud(cx + sx * 0.62 * r, cy - sy * 0.62 * r, FIELD, 26)
    f.append(text(cx, 322, "QPSK: хмарки далеко", 12.5, FIELD, "middle", bold=True))
    f.append(text(cx, 340, "→ помилок мало", 10.5, FIELD, "middle"))

    # 16-QAM праворуч — хмарки тісні, перекриваються
    cx, cy, r = 670, 200, 105
    f.append(line(cx - r - 10, cy, cx + r + 10, cy, color=MUTED, sw=1.2))
    f.append(line(cx, cy + r + 10, cx, cy - r - 10, color=MUTED, sw=1.2))
    grid = [-0.78, -0.26, 0.26, 0.78]
    for gi in grid:
        for gj in grid:
            dot_cloud(cx + gi * r, cy - gj * r, POS, 15, r=3)
    f.append(text(cx, 332, "16-QAM: хмарки тісні", 12.5, POS, "middle", bold=True))
    f.append(text(cx, 350, "→ треба чистіший сигнал (вищий SNR)", 10, POS, "middle"))

    render(os.path.join(IMG, "noise.svg"), W, H, *f,
           title="Чому не можна нескінченно ущільнювати: шум розмиває точки")


# ── 5. Бод проти біт/с: вантажність символу множить швидкість ──────────────────
def fig_baud():
    W, H = 900, 340
    f = []
    f.append(text(450, 86, "бітова швидкість = символьна швидкість (бод) × log₂M",
                  14, INK, "middle", bold=True))
    f.append(text(450, 110, "приклад: символьна швидкість 1 Мбод", 11, MUTED, "middle"))

    rows = [("BPSK", 1, 120, NEG, "#e9eefb"),
            ("QPSK", 2, 240, FIELD, "#eef6ef"),
            ("16-QAM", 4, 480, AMB, "#fbf3df")]
    y = 150
    for name, mult, w, col, fill in rows:
        f.append(text(135, y + 17, name, 12, col, "start", bold=True))
        f.append(rect(245, y, w, 34, fill=fill, stroke=col, sw=1.8, rx=5))
        f.append(text(255, y + 22, "1 Мбод × %d = %d Мбіт/с" % (mult, mult),
                      11.5, INK, "start", bold=True))
        y += 50

    f.append(rect(60, y + 6, 780, 30, fill="#eef6ef", stroke=FIELD, sw=1.3, rx=8))
    f.append(text(450, y + 26, "Та сама символьна швидкість — а біт/с різні: ось як вантажніший символ прискорює лінію.",
                  11, INK, "middle", bold=True))

    render(os.path.join(IMG, "baud.svg"), W, H, *f,
           title="Бод проти біт/с: чому це не одне й те саме")


# ── 6. Головний компроміс: надійність ↔ швидкість ─────────────────────────────
def fig_tradeoff():
    W, H = 900, 330
    f = []
    f.append(line(80, 250, 840, 250, color=INK, sw=2))
    f.append(arrow(820, 250, 845, 250, color=INK, sw=2))
    f.append(text(80, 276, "надійно / повільно", 11, FIELD, "start", bold=True))
    f.append(text(840, 276, "швидко / крихко", 11, POS, "end", bold=True))

    pts = [(130, "FSK\nBPSK", FIELD, 90),
           (320, "QPSK", FIELD, 110),
           (510, "16-QAM", AMB, 140),
           (690, "64-QAM", AMB, 165),
           (810, "256-QAM", POS, 190)]
    for x, lab, col, h in pts:
        f.append(line(x, 250, x, 250 - h, color=col, sw=3))
        f.append('<circle cx="%.1f" cy="%.1f" r="6" fill="%s"/>' % (x, 250 - h, col))
        lines = lab.split("\n")
        ty = 250 - h - 12 - (len(lines) - 1) * 14
        for ln in lines:
            f.append(text(x, ty, ln, 11, col, "middle", bold=True))
            ty += 14

    f.append(rect(170, 286, 560, 30, fill="#fbfbfb", stroke="#d8dde3", sw=1.2, rx=8))
    f.append(text(450, 306, "Сучасні системи міняють модуляцію на льоту — за якістю каналу.",
                  11.5, INK, "middle", bold=True))

    render(os.path.join(IMG, "tradeoff.svg"), W, H, *f,
           title="Головний компроміс: надійність ↔ швидкість")


# ── 7. Що насправді вживають знайомі радіо ────────────────────────────────────
def fig_radios():
    W, H = 900, 330
    cards = [
        ("Bluetooth / BLE", "GFSK", "згладжена FSK —\nпроста й ощадна", NEG),
        ("Wi-Fi", "OFDM:\nBPSK→256-QAM", "багато піднесучих +\nадаптивне сузір'я", FIELD),
        ("LoRa", "CSS (чирп)", "розширений спектр\nзаради дальності", AMB),
        ("RC / телеметрія", "FSK / GFSK", "надійність важливіша\nза швидкість", POS),
    ]
    f = []
    cw, gap, x = 200, 13, 44
    for title_, mod, note, col in cards:
        f.append(rect(x, 86, cw, 204, fill="#fbfbfb", stroke=col, sw=2, rx=12))
        f.append(text(x + cw / 2, 118, title_, 13, INK, "middle", bold=True))
        my = 150
        for ln in mod.split("\n"):
            f.append(text(x + cw / 2, my, ln, 13.5, col, "middle", bold=True))
            my += 19
        ny = my + 14
        for ln in note.split("\n"):
            f.append(text(x + cw / 2, ny, ln, 9.8, MUTED, "middle"))
            ny += 15
        x += cw + gap

    render(os.path.join(IMG, "radios.svg"), W, H, *f,
           title="Що насправді вживають знайомі радіо")


if __name__ == "__main__":
    fig_keyings()
    fig_symbols()
    fig_constellation()
    fig_noise()
    fig_baud()
    fig_tradeoff()
    fig_radios()
    print("OK: figures written to", IMG)
