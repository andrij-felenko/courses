# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "'Consolas', 'DejaVu Sans Mono', 'Courier New', monospace"


# ── допоміжне: квадратний меандр такту (n періодів) ───────────────────────────
def clock(x0, ybase, period, n, amp=22, color=INK, sw=2.0):
    """Меандр від x0; ybase — низький рівень, угору на amp. Повертає polyline."""
    pts = [(x0, ybase)]
    x = x0
    for _ in range(n):
        pts.append((x, ybase - amp)); pts.append((x + period / 2, ybase - amp))
        pts.append((x + period / 2, ybase)); pts.append((x + period, ybase))
        x += period
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (s, color, sw))


def chip_box(x, y, w, h, fill="#23262b", label="DRAM", sub="чіп"):
    out = rect(x, y, w, h, fill=fill, stroke="#0c0e10", sw=1.5, rx=4)
    out += text(x + w / 2, y + h / 2 - 2, label, size=11, color="#e6e6e6", bold=True)
    if sub:
        out += text(x + w / 2, y + h / 2 + 14, sub, size=9.5, color="#a9adb3", italic=True)
    return out


# ════════════════════════════════════════════════════════════════════════════
# СТАТТЯ
# ════════════════════════════════════════════════════════════════════════════

# ── async-vs-sync: асинхронний діалог проти конвеєра на такті ─────────────────
def fig_async_vs_sync():
    W, H = 1000, 470
    p = []

    # верх: асинхронна DRAM — адреса · «?» · дані, двічі
    p.append(text(90, 100, "Асинхронна DRAM — чекаємо невідому затримку",
                  size=14, color=POS, anchor="start", bold=True))
    p.append(rect(90, 118, 820, 70, fill="#fdeef0", stroke=POS, sw=1.6, rx=8))
    seq = [("адреса", INK), ("?", MUTED), ("дані", POS),
           ("адреса", INK), ("?", MUTED), ("дані", POS)]
    bx = 130
    for lab, col in seq:
        p.append(rect(bx, 136, 80, 34, fill=BG, stroke=col, sw=1.4, rx=4))
        p.append(text(bx + 40, 158, lab, size=11.5, color=col, bold=True))
        bx += 110
    p.append(text(280, 184, "«коли?»", size=10, color=MUTED, italic=True))
    p.append(text(800, 152, "повільно й непевно", size=12, color=POS, bold=True))

    # низ: SDRAM — такт + рядок команд + рядок даних
    p.append(text(90, 260, "SDRAM — кожна дія прив'язана до фронту такту (конвеєр)",
                  size=14, color=FIELD, anchor="start", bold=True))
    x0, period, n = 90, 35, 23
    p.append(clock(x0, 290, period, n, amp=22, color=NEG, sw=2.0))
    p.append(text(82, 286, "CLK", size=11, color=NEG, anchor="end", bold=True))

    # рядок команд/даних під тактом — по комірці на період
    cells = ["ACT", "RD", "—", "D0", "D1", "D2", "D3", "RD", "—", "D0", "D1", "D2"]
    cy = 345
    for i, lab in enumerate(cells):
        cx = x0 + i * (period * 2)
        is_data = lab.startswith("D")
        col = FIELD if is_data else (MUTED if lab == "—" else "#6a3fb5")
        fill = "#eef6ef" if is_data else BG
        p.append(rect(cx + 2, cy, period * 2 - 6, 34, fill=fill, stroke=col, sw=1.4, rx=4))
        p.append(text(cx + period, cy + 22, lab, size=11.5, color=col, bold=True))
        p.append(line(cx + period, 290, cx + period, cy, color="#e2e2e2", sw=1.0))
    p.append(text(x0 + period, cy + 60,
                  "пакет (burst): один запит → потік слів підряд, по одному за такт",
                  size=12, color=FIELD, anchor="start", bold=True))

    p.append(text(W / 2, 452,
                  "Прив'язка до такту дає відгук передбачуваним, а звернення можна конвеєризувати: "
                  "поки одне віддає дані, наступне вже готується.",
                  size=12, color=INK))

    render(os.path.join(OUT, "async-vs-sync.svg"), W, H, *p,
           title="Синхронна пам'ять: працюємо в такт, а не «питання — пауза — відповідь»")


# ── banks: банки працюють з перекриттям ───────────────────────────────────────
def fig_banks():
    W, H = 1000, 460
    p = []
    cols = [NEG, FIELD, "#caa24a", "#6a3fb5"]

    # ліворуч — стос банків
    by = 105
    for i, c in enumerate(cols):
        y = by + i * 64
        p.append(rect(80, y, 150, 50, fill=BG, stroke=c, sw=2.0, rx=6))
        for k in range(3):
            p.append(line(92, y + 12 + k * 12, 218, y + 12 + k * 12, color="#e6e6e6", sw=0.8))
        p.append(text(155, y + 30, "Bank %d" % i, size=13, color=c, bold=True))

    # спільна шина (вертикаль) зі стрілками від банків
    p.append(line(280, 96, 280, by + 4 * 64 - 12, color=INK, sw=2.4))
    for i, c in enumerate(cols):
        yy = by + i * 64 + 25
        p.append(arrow(230, yy, 280, yy, color=c, sw=1.6))
    p.append(text(286, 92, "спільна шина даних", size=11.5, color=INK, anchor="start", bold=True))

    # праворуч — діаграма часу: ACT (тонкий) + дані (товстий блок) зі зсувом
    tx0, trow = 330, 56
    p.append(arrow(330, 80, 870, 80, color=MUTED, sw=1.6))
    p.append(text(330, 70, "час →", size=12, color=INK, anchor="start", bold=True))
    for i, c in enumerate(cols):
        ry = 108 + i * trow
        ax = 330 + i * 60                    # зсув старту ACT
        p.append(text(326, ry + 10, "Bank %d" % i, size=10.5, color=c, anchor="end", bold=True))
        # ACT
        p.append(rect(ax, ry, 60, 16, fill=BG, stroke=c, sw=1.4, rx=3))
        p.append(text(ax + 30, ry + 12, "ACT", size=9.5, color=c, bold=True))
        # дані
        p.append(rect(ax + 60, ry, 120, 16, fill=c, stroke=c, sw=0, rx=3))
        p.append(text(ax + 120, ry + 12, "дані", size=9.5, color=BG, bold=True))

    # спільна шина зайнята майже без пауз (склейка блоків даних)
    sy = 108 + 4 * trow + 4
    p.append(line(330, sy, 870, sy, color="#e6e6e6", sw=1.0))
    for i, c in enumerate(cols):
        dx = 330 + 60 + i * 60
        p.append(rect(dx, sy + 4, 120, 12, fill=c, stroke=c, sw=0, rx=2))
    p.append(text(595, sy + 40,
                  "шина даних зайнята майже без пауз — банки перекривають затримки одне одного",
                  size=11.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "banks.svg"), W, H, *p,
           title="Банки: поки один віддає дані, інший уже відкриває ряд")


# ── ddr-edges: SDR одне слово за такт проти DDR на обох фронтах ────────────────
def fig_ddr_edges():
    W, H = 1000, 460
    p = []
    period, n, x0 = 50, 11, 90

    # SDR: одне слово на період (висхідний фронт)
    p.append(text(90, 108, "SDR — одне слово за такт", size=14, color=NEG, anchor="start", bold=True))
    p.append(clock(x0, 130, period, n, amp=30, color=INK, sw=2.0))
    p.append(text(82, 116, "CLK", size=10.5, color=INK, anchor="end", bold=True))
    for i in range(6):
        wx = x0 + i * period * 2
        p.append(rect(wx + 4, 160, period * 2 - 8, 26, fill="#eef2fb", stroke=NEG, sw=1.4, rx=3))
        p.append(text(wx + period, 178, "D%d" % i, size=11, color=NEG, bold=True))
        p.append(arrow(wx, 130, wx, 160, color=FIELD, sw=1.2))
    p.append(text(x0 + 12.5 * period, 178, "6 слів", size=12, color=NEG, anchor="start", bold=True))

    # DDR: слово на обох фронтах
    p.append(text(90, 258, "DDR — слово і на висхідному, і на спадному фронті",
                  size=14, color=POS, anchor="start", bold=True))
    p.append(clock(x0, 280, period, n, amp=30, color=INK, sw=2.0))
    p.append(text(82, 266, "CLK", size=10.5, color=INK, anchor="end", bold=True))
    for i in range(12):
        wx = x0 + i * period
        p.append(rect(wx + 3, 310, period - 6, 26, fill="#fdeef0", stroke=POS, sw=1.4, rx=3))
        p.append(text(wx + period / 2, 328, "D%d" % i, size=9.5, color=POS, bold=True))
        p.append(arrow(wx, 280, wx, 310, color=FIELD, sw=1.1))
    p.append(text(x0 + 12.5 * period, 326, "12 слів", size=12, color=POS, anchor="start", bold=True))
    p.append(text(x0 + 12.5 * period, 344, "за той самий час!", size=10.5, color=POS, anchor="start"))

    p.append(text(W / 2, 438,
                  "Частота такту та сама — а слів проходить удвічі більше. "
                  "DDR2/3/4/5 розвивають цю саму ідею з усе вищими частотами.",
                  size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "ddr-edges.svg"), W, H, *p,
           title="DDR: дані на обох фронтах такту — удвічі більше за ту саму частоту")


# ════════════════════════════════════════════════════════════════════════════
# ВСТАВКА comp-ddr-labels
# ════════════════════════════════════════════════════════════════════════════

# ── label-decode: рядок маркування розкладений на три поля ────────────────────
def fig_label_decode():
    W, H = 880, 470
    p = []
    # рядок-маркування
    p.append(rect(70, 78, 740, 52, fill="#f3f7f3", stroke="#1f6b3a", sw=2, rx=8))
    p.append('<text x="440.0" y="112.0" font-family="%s" font-size="22" fill="%s" '
             'text-anchor="middle" font-weight="700">PC4-25600   DDR4-3200   CL22-22-22</text>'
             % (MONO, INK))

    fields = [
        (176, FIELD, "PC4-25600", "= пік ГБ/с × 1000",
         ["клас модуля (PC4 = DDR4)", "25600 МБ/с = 3200 × 8 байтів"]),
        (440, NEG, "DDR4-3200", "тип і швидкість",
         ["DDR4 — покоління", "3200 — передач за секунду,", "у мільйонах (МТ/с)"]),
        (704, POS, "CL22", "затримка, у тактах",
         ["CAS latency — пауза від", "запиту до першого слова;", "22 такти, не наносекунди!"]),
    ]
    src_x = [218, 468, 700]
    for (cx, col, head, ital, rows), sx in zip(fields, src_x):
        p.append(line(sx, 132, sx, 152, color=col, sw=2))
        p.append(arrow(sx, 152, cx, 244, color=col, sw=2.0))
        bx = cx - 116
        p.append(rect(bx, 250, 232, 150, fill=BG, stroke=col, sw=2.2, rx=10))
        p.append(rect(bx, 250, 232, 30, fill=col, stroke=col, sw=0, rx=0))
        p.append('<text x="%.1f" y="271.0" font-family="%s" font-size="15" fill="%s" '
                 'text-anchor="middle" font-weight="700">%s</text>' % (cx, MONO, BG, esc(head)))
        p.append(text(cx, 299, ital, size=12, color=INK, italic=True))
        for k, r in enumerate(rows):
            p.append(text(bx + 12, 322 + k * 19, r, size=12, color=INK, anchor="start"))

    p.append(rect(60, 418, 760, 38, fill="#fff7ef", stroke="#e08030", sw=1.8, rx=8))
    p.append(text(440, 442,
                  "Швидкість (3200) і затримка (CL22) — різні числа: одне про потік, "
                  "друге про паузу перед першим словом.",
                  size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, "label-decode.svg"), W, H, *p,
           title="Маркування модуля: що в ньому зашифровано")


# ── module-anatomy: планка = ряд чіпів + контакти + SPD ───────────────────────
def fig_module_anatomy():
    W, H = 880, 430
    p = []
    # текстоліт планки
    p.append(rect(70, 95, 740, 150, fill="#1f6b3a", stroke="#0f3a1f", sw=2, rx=6))
    p.append(text(440, 116, "8 однакових чіпів × по 8 біт → разом 64-бітне слово",
                  size=13, color="#eafff0", bold=True))
    for i in range(8):
        cx = 95 + i * 88
        p.append(chip_box(cx, 125, 74, 56, label="DRAM", sub="die"))

    # SPD
    p.append(rect(86, 199, 58, 30, fill="#3a2a55", stroke="#000", sw=1.5, rx=3))
    p.append(text(115, 219, "SPD", size=11, color=BG, bold=True))
    p.append(text(156, 221, "← крихітна EEPROM: тут лежить «паспорт» планки",
                  size=12, color="#eafff0", anchor="start"))

    # ряд контактів
    for i in range(28):
        cx = 88 + i * 25.4
        if 380 < cx < 410:
            continue
        p.append(rect(cx, 245, 6, 12, fill="#c9a227", stroke="#c9a227", sw=0, rx=1))
    p.append(text(440, 275, "сотні золочених контактів: дані, адреси, команди, такт, живлення",
                  size=12, color=MUTED, italic=True))

    # пояснення «першого байта»
    p.append(rect(70, 330, 740, 78, fill="#f3f7f3", stroke="#1f6b3a", sw=2, rx=8))
    p.append(text(90, 354, "«Перший байт» тут — не з пам'яті, а з SPD:",
                  size=14, color=INK, anchor="start", bold=True))
    p.append(text(90, 376, "контролер по простій шині I²C читає з SPD-EEPROM тип, обсяг, "
                  "рядки таймінгу (CL, частоту)", size=12.5, color=INK, anchor="start"))
    p.append(text(90, 395, "і лише потім, налаштувавшись за цим «паспортом», починає "
                  "звертатися до самих чіпів DRAM.", size=12.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "module-anatomy.svg"), W, H, *p,
           title="Клас «модуль DRAM»: плата, а не один чіп")


# ════════════════════════════════════════════════════════════════════════════
# ВСТАВКА math-bandwidth
# ════════════════════════════════════════════════════════════════════════════

# ── formula: три множники + фізичний сенс «×2» на фронтах ─────────────────────
def fig_formula():
    W, H = 880, 470
    p = []
    # формула трьома плитками
    tiles = [("частота\nтакту f", NEG), ("×", None), ("ширина\nшини W", FIELD),
             ("×", None), ("множник\n1 (SDR) / 2 (DDR)", POS)]
    x = 70
    for lab, col in tiles:
        if lab == "×":
            p.append(text(x + 18, 118, "×", size=24, color=INK, bold=True))
            x += 46
            continue
        body, w, h = textbox(0, 0, lab, size=13, pad=12, stroke=col, fill="#fbfdff",
                             color=INK, bold=True, min_w=150)
        bx, by = x, 92
        p.append(rect(bx, by, w, h, fill="#fbfdff", stroke=col, sw=2.0, rx=8))
        lines = lab.split("\n")
        ty = by + h / 2 - (len(lines) - 1) * 13 * 0.65 + 13 * 0.35
        p.append(mtext(bx + w / 2, ty, lines, size=13, color=INK, bold=True))
        x += w + 16
    p.append(text(70, 162, "= пропускна здатність (байтів за секунду)",
                  size=13, color=MUTED, anchor="start", italic=True))

    # фізичний сенс «×2»: два такти, SDR ловить висхідні, DDR обидва
    p.append(line(70, 200, 810, 200, color="#e6e6e6", sw=1.0))
    period, n, x0 = 90, 4, 120
    # SDR
    p.append(text(70, 250, "SDR", size=13, color=NEG, anchor="start", bold=True))
    p.append(clock(x0, 270, period, n, amp=26, color=INK, sw=2.0))
    for i in range(4):
        wx = x0 + i * period
        p.append(circle(wx, 244, 5, fill=NEG, stroke=NEG, sw=1))
    p.append(text(x0 + 4 * period + 16, 250, "4 слова за 4 такти",
                  size=12, color=NEG, anchor="start"))
    # DDR
    p.append(text(70, 360, "DDR", size=13, color=POS, anchor="start", bold=True))
    p.append(clock(x0, 380, period, n, amp=26, color=INK, sw=2.0))
    for i in range(8):
        wx = x0 + i * (period / 2)
        p.append(circle(wx, 354, 5, fill=POS, stroke=POS, sw=1))
    p.append(text(x0 + 4 * period + 16, 360, "8 слів за ті самі 4 такти",
                  size=12, color=POS, anchor="start"))

    p.append(text(W / 2, 440,
                  "Подвоюється не частота, а кількість слів на період: DDR ловить і спадний фронт.",
                  size=12.5, color=INK))

    render(os.path.join(OUT, "formula.svg"), W, H, *p,
           title="Пропускна здатність = такт × ширина × множник передач")


# ── waterfall: від пікового числа реальність відбирає частку за часткою ────────
def fig_waterfall():
    W, H = 880, 430
    p = []
    base_y, top_y = 360, 90
    full_h = base_y - top_y
    x0, bw, gap = 80, 116, 24

    steps = [
        ("піковий\n25.6 ГБ/с", 1.00, NEG),
        ("− регенерація", 0.92, MUTED),
        ("− відкриття\nрядка", 0.78, MUTED),
        ("− латентність\nвипадкового\nдоступу", 0.60, MUTED),
        ("− команди й\nрозвороти шини", 0.50, POS),
    ]
    prev_top = None
    for i, (lab, frac, col) in enumerate(steps):
        h = full_h * frac
        bx = x0 + i * (bw + gap)
        by = base_y - h
        fill = "#fdeef0" if i == 0 else ("#eef6ef" if i == len(steps) - 1 else "#f1f3f6")
        p.append(rect(bx, by, bw, h, fill=fill, stroke=col, sw=1.8, rx=4))
        lines = lab.split("\n")
        ty = by - 6 - (len(lines) - 1) * 12
        p.append(mtext(bx + bw / 2, ty, lines, size=11, color=col, bold=(i == 0 or i == len(steps) - 1)))
        if prev_top is not None:
            p.append(line(prev_top[0], prev_top[1], bx, by, color="#c8ccd2", sw=1.2, dash="4 3"))
        prev_top = (bx + bw, by)

    p.append(line(x0 - 20, base_y, x0 + 5 * (bw + gap) - gap + 20, base_y, color=INK, sw=1.6))
    p.append(text(W / 2, base_y + 26,
                  "до корисного потоку доходить — грубо — близько половини піку",
                  size=12.5, color=FIELD, bold=True))
    p.append(text(W / 2, base_y + 48,
                  "вузьке горло — затримки й випадковий доступ, а не такт чи ширина",
                  size=12, color=INK))

    render(os.path.join(OUT, "waterfall.svg"), W, H, *p,
           title="Чому реальний потік нижчий за піковий: каскад втрат")


# ── scale: той самий закон, інший масштаб (лог-вісь) ──────────────────────────
def fig_scale():
    import math as _m
    W, H = 880, 400
    p = []
    ax, ay, aw = 120, 300, 680     # вісь X (лог МБ/с)
    lo, hi = 1.0, 30000.0          # 1 МБ/с .. 30 ГБ/с
    def X(v):
        return ax + aw * (_m.log10(v) - _m.log10(lo)) / (_m.log10(hi) - _m.log10(lo))

    # вісь і поділки
    p.append(line(ax, ay, ax + aw, ay, color=INK, sw=1.6))
    for v, lab in [(1, "1"), (10, "10"), (100, "100"), (1000, "1 ГБ/с"),
                   (10000, "10"), (30000, "30")]:
        xx = X(v)
        p.append(line(xx, ay, xx, ay + 6, color=INK, sw=1.2))
        p.append(text(xx, ay + 22, lab, size=10, color=MUTED))
    p.append(text(ax + aw, ay + 22, "МБ/с (лог)", size=10.5, color=INK, anchor="end", italic=True))

    bars = [
        ("quad-SPI пам'ять МК", 40, NEG, "≈40 МБ/с"),
        ("octal-SPI / паралельна", 320, FIELD, "≈0.3 ГБ/с"),
        ("ПК-модуль DDR4", 25600, POS, "25.6 ГБ/с"),
    ]
    by = 110
    for lab, v, col, tag in bars:
        yy = by
        p.append(line(ax, yy, X(v), yy, color=col, sw=10))
        p.append(circle(X(v), yy, 6, fill=col, stroke=col, sw=1))
        p.append(text(ax - 8, yy + 4, lab, size=11, color=INK, anchor="end", bold=True))
        p.append(text(X(v) + 12, yy + 4, tag, size=11, color=col, anchor="start", bold=True))
        by += 56

    p.append(text(W / 2, 360,
                  "Той самий закон, інші множники: ×16 за шириною, ×20 за тактом, ще ×2 за DDR.",
                  size=12, color=INK))
    p.append(text(W / 2, 382,
                  "Практичний наслідок: кадр невеликого дисплея впирається в шину, а не в розрахунок.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "scale.svg"), W, H, *p,
           title="Той самий закон, інший масштаб: ПК-модуль проти пам'яті МК")


if __name__ == "__main__":
    fig_async_vs_sync()
    fig_banks()
    fig_ddr_edges()
    fig_label_decode()
    fig_module_anatomy()
    fig_formula()
    fig_waterfall()
    fig_scale()
    print("OK: figures written to", OUT)
