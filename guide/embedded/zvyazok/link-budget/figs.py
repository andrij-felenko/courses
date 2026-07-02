# -*- coding: utf-8 -*-
"""Фігури до детальної теми «Бюджет лінії» (link-budget-d.md).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b9770e"


# ── 1. З чого складається чутливість: −174 → +смуга → +NF → +SNR ─────────────
def fig_sensitivity_stack():
    W, H = 960, 500
    f = [text(W / 2, 30, "Звідки береться поріг чутливості: чотири доданки", size=18, bold=True),
         text(W / 2, 52, "S_rx = −174 + 10·log₁₀(B) + NF + SNR_min  — той самий рецепт для будь-якого радіо",
              size=11.5, color=MUTED, italic=True)]

    # три стовпчики: BLE, Wi-Fi 256-QAM, LoRa SF12
    # (значення в дБм/дБ; малюємо як накопичувальні відрізки вниз від −174)
    cols = [
        ("BLE (GFSK)",   1_000_000, 8,  17,  FIELD),   # B=1 МГц, NF≈8, SNRmin≈17 → ≈ −95
        ("Wi-Fi 256-QAM", 20_000_000, 5, 31, POS),      # B=20 МГц, NF≈5, SNRmin≈31 → ≈ −65
        ("LoRa SF12",    125_000,    6,  -20, NEG),      # B=125 кГц, NF≈6, SNRmin≈−20 → ≈ −137
    ]

    # вісь: 0 dBm зверху, −150 dBm знизу
    top, bot = 110, 430
    dbm_top, dbm_bot = -50.0, -150.0

    def yy(dbm):
        t = (dbm - dbm_top) / (dbm_bot - dbm_top)
        return top + t * (bot - top)

    # сітка рівнів
    for lvl in range(-50, -151, -20):
        f.append(line(120, yy(lvl), W - 40, yy(lvl), color="#e5e7eb", sw=1))
        f.append(text(112, yy(lvl) + 4, "%d" % lvl, size=10, color=MUTED, anchor="end"))
    f.append(text(60, (top + bot) / 2, "дБм", size=11, color=MUTED))

    bw = 150
    x0 = 170
    for i, (name, B, NF, snr, col) in enumerate(cols):
        cx = x0 + i * 250
        floor = -174.0 + 10.0 * math.log10(B)     # kTB для цієї смуги
        after_nf = floor + NF
        srx = after_nf + snr
        # відрізок «тепловий поріг у цій смузі»
        f.append(rect(cx - bw / 2, yy(-50), bw, yy(floor) - yy(-50),
                      fill="#f6f7f9", stroke="#cbd5e1", sw=1.2, rx=3))
        f.append(text(cx, yy(-50) + 16, "−174 + 10·logB", size=9.5, color=MUTED))
        f.append(text(cx, yy(floor) - 6, "kTB = %d дБм" % round(floor), size=10, color=INK, bold=True))
        # NF
        f.append(rect(cx - bw / 2, yy(floor), bw, yy(after_nf) - yy(floor),
                      fill="#fff4e6", stroke=GOLD, sw=1.4, rx=3))
        f.append(text(cx, (yy(floor) + yy(after_nf)) / 2 + 4, "+NF %d" % NF, size=10, color=GOLD, bold=True))
        # SNR_min (може бути від'ємний — тоді відрізок іде ВГОРУ)
        if snr >= 0:
            f.append(rect(cx - bw / 2, yy(after_nf), bw, yy(srx) - yy(after_nf),
                          fill=col + "22", stroke=col, sw=1.6, rx=3))
            f.append(text(cx, (yy(after_nf) + yy(srx)) / 2 + 4, "+SNR %d" % snr, size=10, color=col, bold=True))
        else:
            f.append(rect(cx - bw / 2, yy(srx), bw, yy(after_nf) - yy(srx),
                          fill=col + "22", stroke=col, sw=1.6, rx=3))
            f.append(text(cx, (yy(after_nf) + yy(srx)) / 2 + 4, "SNR %d" % snr, size=10, color=col, bold=True))
            f.append(text(cx, yy(after_nf) + 14, "нижче шуму!", size=9, color=col, italic=True))
        # підсумок S_rx
        f.append(line(cx - bw / 2 - 6, yy(srx), cx + bw / 2 + 6, yy(srx), color=col, sw=2.4))
        f.append(text(cx, yy(srx) + (18 if snr >= 0 else -10), "S_rx ≈ %d дБм" % round(srx),
                      size=11.5, color=col, bold=True))
        f.append(text(cx, bot + 24, name, size=12, color=col, bold=True))
        f.append(text(cx, bot + 42, "B=%s" % (("%d МГц" % (B // 1_000_000)) if B >= 1_000_000 else ("%d кГц" % (B // 1000))),
                      size=9.5, color=MUTED))

    f.append(text(W / 2, H - 12,
                  "Вузька смуга + низький потрібний SNR ⇒ глибший поріг ⇒ більша дальність. LoRa чує НИЖЧЕ теплового шуму.",
                  size=10.5, color=INK, italic=True))
    return render(os.path.join(IMG, 'sensitivity-stack.svg'), W, H, *f)


# ── 2. Чому модуляції рівняють за Eb/N0, а не за SNR ──────────────────────────
def fig_ebn0():
    W, H = 920, 400
    f = [text(W / 2, 30, "Порівнюй модуляції за Eb/N₀, а не за «сирим» SNR", size=18, bold=True),
         text(W / 2, 52, "SNR ділить потужність на всю смугу; Eb/N₀ — енергію ОДНОГО біта на щільність шуму",
              size=11.5, color=MUTED, italic=True)]

    # ліворуч: SNR = C/N — залежить від смуги
    f.append(rect(44, 84, 400, 286, fill="#fbfdfb", stroke=FIELD, sw=2, rx=12))
    f.append(text(244, 112, "SNR = C / N", size=14, color=FIELD, bold=True))
    f.append(text(244, 132, "потужність сигналу / шум у всій смузі", size=10, color=MUTED, italic=True))
    f.append(line(90, 300, 398, 300, color=INK, sw=1.8))
    f.append(line(90, 300, 90, 160, color=INK, sw=1.8))
    # широка смуга — низький, розмазаний рівень
    f.append(rect(120, 250, 240, 50, fill=FIELD + "22", stroke=FIELD, sw=1.6, rx=3))
    f.append(text(240, 320, "широка смуга: та сама енергія", size=10, color=INK))
    f.append(text(240, 336, "розмазана → SNR виглядає гірше", size=10, color=INK))
    f.append(text(244, 358, "SNR залежить від смуги — нечесно", size=10.5, color=POS, bold=True))

    # праворуч: Eb/N0 — нормовано на біт
    f.append(rect(476, 84, 400, 286, fill="#fefafa", stroke=NEG, sw=2, rx=12))
    f.append(text(676, 112, "Eb / N₀", size=14, color=NEG, bold=True))
    f.append(text(676, 132, "енергія на біт / щільність шуму", size=10, color=MUTED, italic=True))
    # формула-місток
    f.append(fitbox(516, 160, 320, 46, "SNR = (Eb/N₀) · (Rb / B)",
                    size=14, fill="#eef2ff", stroke=NEG, bold=True))
    f.append(text(676, 236, "Rb — бітова швидкість, B — смуга", size=10, color=MUTED, italic=True))
    f.append(text(676, 262, "менша швидкість Rb → нижчий потрібний SNR", size=10.5, color=INK))
    f.append(text(676, 282, "за тим самим Eb/N₀ на біт", size=10.5, color=INK))
    f.append(text(676, 316, "Eb/N₀ від смуги НЕ залежить —", size=10.5, color=FIELD, bold=True))
    f.append(text(676, 334, "чесна міра якості модуляції", size=10.5, color=FIELD, bold=True))
    f.append(text(676, 356, "саме тому «повільніше = далі»", size=10, color=INK, italic=True))

    return render(os.path.join(IMG, 'ebn0.svg'), W, H, *f)


# ── 3. Запас на завмирання ⇄ доступність лінії ───────────────────────────────
def fig_fade_availability():
    W, H = 940, 440
    f = [text(W / 2, 30, "Запас на завмирання — це плата за доступність лінії", size=18, bold=True),
         text(W / 2, 52, "реальний сигнал «дихає»; поки він над порогом — зв'язок є, провал під поріг — розрив",
              size=11.5, color=MUTED, italic=True)]

    left, right = 70, 620
    top, bot = 90, 360
    # осі
    f.append(line(left, bot, right, bot, color=INK, sw=1.8))
    f.append(line(left, top, left, bot, color=INK, sw=1.8))
    f.append(text((left + right) / 2, bot + 30, "час", size=11, color=MUTED))
    f.append(text(left - 40, (top + bot) / 2, "P_rx", size=11, color=MUTED))

    # рівень порогу чутливості
    thr = bot - 40
    f.append(line(left, thr, right, thr, color=POS, sw=2, dash="7,5"))
    f.append(text(right + 6, thr + 4, "поріг S_rx", size=10.5, color=POS, anchor="start", bold=True))
    # середній рівень сигналу
    mean = top + 70
    f.append(line(left, mean, right, mean, color=NEG, sw=1.6, dash="3,4"))
    f.append(text(right + 6, mean + 4, "середній P_rx", size=10.5, color=NEG, anchor="start"))
    # стрілка запасу
    f.append(line((left + right) / 2 - 260, mean, (left + right) / 2 - 260, thr, color=FIELD, sw=2))
    f.append('<path d="M %.0f,%.0f l -4,7 h 8 z" fill="%s"/>' % ((left + right) / 2 - 260, thr, FIELD))
    f.append('<path d="M %.0f,%.0f l -4,-7 h 8 z" fill="%s"/>' % ((left + right) / 2 - 260, mean, FIELD))
    f.append(text((left + right) / 2 - 250, (mean + thr) / 2, "запас (fade margin)", size=10.5, color=FIELD, anchor="start", bold=True))

    # «дихаючий» сигнал — синусоїда з шумом, місцями пірнає під поріг
    import random
    random.seed(7)
    pts = []
    n = 220
    for i in range(n + 1):
        x = left + (right - left) * i / n
        base = mean + 26 * math.sin(i * 0.11) + 16 * math.sin(i * 0.37 + 1)
        base += random.uniform(-10, 10)
        pts.append((x, base))
    d = "M %.1f,%.1f " % pts[0] + " ".join("L %.1f,%.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, INK))
    # позначити провали під поріг
    for (x, y) in pts:
        if y > thr:
            f.append(circle(x, y, 2.2, fill=POS, stroke=POS, sw=0))
    f.append(text((left + right) / 2, top - 4, "провали під поріг = втрачені пакети", size=10, color=POS, italic=True))

    # праворуч: таблиця запас → доступність
    tx = 700
    f.append(rect(tx, 96, 210, 266, fill="#fcfcfc", stroke=MUTED, sw=1.6, rx=10))
    f.append(text(tx + 105, 122, "запас → доступність", size=12, color=INK, bold=True))
    f.append(text(tx + 105, 140, "(релеївський канал, груба оцінка)", size=8.6, color=MUTED, italic=True))
    rows = [("0 дБ", "≈ 50 %", POS), ("10 дБ", "≈ 90 %", GOLD),
            ("20 дБ", "≈ 99 %", FIELD), ("30 дБ", "≈ 99.9 %", FIELD)]
    ry = 172
    for m, a, c in rows:
        f.append(text(tx + 24, ry, m, size=12, color=c, anchor="start", bold=True))
        f.append(text(tx + 190, ry, a, size=12, color=c, anchor="end"))
        ry += 40
    f.append(text(tx + 105, ry + 6, "кожні +10 дБ ≈ ×10", size=9.5, color=INK, italic=True))
    f.append(text(tx + 105, ry + 22, "менше часу «в провалі»", size=9.5, color=INK, italic=True))

    return render(os.path.join(IMG, 'fade-availability.svg'), W, H, *f)


# ── 4. Зона Френеля: «видно» ще не означає «чути» ────────────────────────────
def fig_fresnel():
    W, H = 940, 430
    f = [text(W / 2, 30, "Пряма видимість — це не все: зона Френеля", size=18, bold=True),
         text(W / 2, 52, "хвиля йде не ниткою, а «сигарою» навколо прямої; перекрий її — і сигнал просяде",
              size=11.5, color=MUTED, italic=True)]

    ax, bx = 120, 820
    midy = 200
    # щогли
    f.append(line(ax, midy, ax, midy + 120, color=INK, sw=3))
    f.append(line(bx, midy, bx, midy + 120, color=INK, sw=3))
    f.append(circle(ax, midy, 5, fill=NEG, stroke=NEG, sw=0))
    f.append(circle(bx, midy, 5, fill=NEG, stroke=NEG, sw=0))
    f.append(text(ax, midy + 140, "передавач", size=11, color=INK))
    f.append(text(bx, midy + 140, "приймач", size=11, color=INK))

    # еліпс першої зони Френеля
    cx = (ax + bx) / 2
    rx = (bx - ax) / 2
    ry = 70
    f.append('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" fill="%s22" stroke="%s" stroke-width="1.8"/>'
             % (cx, midy, rx, ry, FIELD, FIELD))
    # 60%-еліпс
    f.append('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="5,4"/>'
             % (cx, midy, rx, ry * 0.6, GOLD))
    # пряма видимості
    f.append(line(ax, midy, bx, midy, color=INK, sw=1.6, dash="2,5"))
    f.append(text(cx, midy - ry - 10, "1-ша зона Френеля (важлива «сигара»)", size=10.5, color=FIELD, italic=True))
    f.append(text(cx, midy - ry * 0.6 + 16, "60 % — критичний мінімум", size=9.5, color=GOLD))

    # перешкода, що ріже низ зони, хоча пряму НЕ перекриває
    ox = cx + 120
    f.append(rect(ox - 22, midy + 8, 44, 80, fill="#d9d9de", stroke=MUTED, sw=1.6, rx=2))
    f.append(text(ox, midy + 104, "дах / дерево", size=9.5, color=INK))
    f.append(text(ox + 40, midy + 30, "пряму видно,", size=9.5, color=POS, anchor="start", bold=True))
    f.append(text(ox + 40, midy + 46, "але зону ріже →", size=9.5, color=POS, anchor="start", bold=True))
    f.append(text(ox + 40, midy + 62, "втрати дифракції", size=9.5, color=POS, anchor="start"))

    # формула радіуса
    f.append(fitbox(120, midy + 150, 320, 44, "r₁ ≈ 8.66·√(d/f)   (r,м · d,км · f,ГГц)",
                    size=12.5, fill="#f6f7f9", stroke=MUTED))
    f.append(text(660, midy + 172, "нижча частота ⇒ товща «сигара» ⇒ потрібно вище підняти антени",
                  size=10.5, color=INK, italic=True))

    return render(os.path.join(IMG, 'fresnel.svg'), W, H, *f)


# ── 5. (вставка math-noise-floor) Чому доступний шум = kTB і R скорочується ──
def fig_ktb_matched():
    W, H = 900, 440
    f = [text(W / 2, 30, "Доступна шумова потужність: чому R скорочується", size=18, bold=True),
         text(W / 2, 52, "джерело шуму з внутрішнім R віддає максимум у РІВНЕ навантаження R — і R зникає",
              size=11.5, color=MUTED, italic=True)]

    # ── ліворуч: схема узгодженого дільника ──
    bx, by = 120, 110
    f.append(rect(60, by - 10, 360, 300, fill="#fbfcfe", stroke="#cbd5e1", sw=1.5, rx=12))

    # джерело ЕРС (кружок з ~)
    scx, scy = 150, 200
    f.append(circle(scx, scy, 26, fill="#eef2ff", stroke=NEG, sw=2))
    f.append(text(scx, scy - 4, "U", size=15, color=NEG, bold=True, italic=True))
    f.append(text(scx, scy + 14, "шум", size=9, color=NEG))
    # внутрішній опір R (резистор-джерело)
    f.append(rect(scx - 16, scy - 100, 32, 46, fill="#fff4e6", stroke=GOLD, sw=1.8, rx=3))
    f.append(text(scx, scy - 72, "R", size=14, color=GOLD, bold=True))
    f.append(text(scx - 44, scy - 74, "внутр.", size=9, color=MUTED, anchor="middle"))
    # навантаження R (рівне!)
    lcx = 320
    f.append(rect(lcx - 16, scy - 100, 32, 46, fill="#eafbf0", stroke=FIELD, sw=1.8, rx=3))
    f.append(text(lcx, scy - 72, "R", size=14, color=FIELD, bold=True))
    f.append(text(lcx + 52, scy - 74, "наван-", size=9, color=MUTED))
    f.append(text(lcx + 52, scy - 62, "таження", size=9, color=MUTED))
    # провідники
    f.append(line(scx, scy - 26, scx, scy - 54, color=INK, sw=1.8))          # джерело↑ до R
    f.append(line(scx, scy - 100, lcx, scy - 100, color=INK, sw=1.8))        # верх
    f.append(line(lcx, scy - 100, lcx, scy - 100, color=INK, sw=1.8))
    f.append(line(scx, scy + 26, scx, scy + 60, color=INK, sw=1.8))          # низ джерела
    f.append(line(scx, scy + 60, lcx, scy + 60, color=INK, sw=1.8))          # низ
    f.append(line(lcx, scy - 54, lcx, scy + 60, color=INK, sw=1.8))          # права гілка

    # ── праворуч: два записи однієї потужності ──
    rx = 560
    f.append(text(rx, 120, "одну потужність — двома мовами", size=13, color=INK, bold=True))
    f.append(fitbox(470, 140, 360, 46, "закон Ома:  P_наван = ⟨U²⟩ / (4R)",
                    size=13.5, fill="#fff9f0", stroke=GOLD, bold=True))
    f.append(text(rx, 205, "«4» = два опори послідовно, у квадраті", size=10, color=MUTED, italic=True))
    f.append(fitbox(470, 222, 360, 46, "термодинаміка:  P_наван = k·T·B",
                    size=13.5, fill="#eef2ff", stroke=NEG, bold=True))
    f.append(text(rx, 288, "рівновага двох рівних резисторів", size=10, color=MUTED, italic=True))

    # знак рівності між ними
    f.append(text(rx, 330, "⟨U²⟩ / (4R)  =  k·T·B", size=15, color=INK, bold=True))
    f.append(text(rx, 356, "⇓  домножити на 4R", size=11, color=MUTED))
    f.append(fitbox(470, 372, 360, 46, "⟨U²⟩ = 4·k·T·R·B     N_дост = k·T·B",
                    size=13, fill="#eafbf0", stroke=FIELD, bold=True))

    f.append(text(W / 2, H - 10,
                  "Витягуєш максимум потужності — і R зникає: доступний шум залежить лише від T і смуги B.",
                  size=10.5, color=INK, italic=True))
    return render(os.path.join(IMG, 'ktb-matched.svg'), W, H, *f)


# ── 6. (вставка math-noise-floor) Драбина SNR_min: від LoRa до 256-QAM ───────
def fig_snr_ladder():
    W, H = 940, 520
    f = [text(W / 2, 30, "Скільки сигналу над шумом просить модуляція (SNR_min)", size=18, bold=True),
         text(W / 2, 52, "той самий поріг у смузі приймача: чим щільніше сузір'я, тим гучніший потрібен сигнал",
              size=11.5, color=MUTED, italic=True)]

    # (назва, SNR_min дБ, колір, короткий підпис)
    rows = [
        ("LoRa SF12 (CSS)",   -20, NEG,   "чирп читається З-ПІД шуму"),
        ("LoRa SF7 (CSS)",     -7.5, NEG, "менший обробний виграш"),
        ("BPSK",                6.8, FIELD,"1 біт/символ, найтвердіша"),
        ("QPSK",                9.8, FIELD,"2 біти/символ"),
        ("FSK (некогер.)",     10.9, GOLD, "без фази — простий приймач"),
        ("16-QAM",             16.5, GOLD, "4 біти/символ"),
        ("64-QAM",             22.5, POS,  "6 біт/символ"),
        ("256-QAM",            28.4, POS,  "8 біт/символ, найкрихкіша"),
    ]

    # горизонтальна вісь SNR: від -24 до +32 дБ
    left, right = 210, 900
    lo, hi = -24.0, 32.0

    def xx(snr):
        return left + (snr - lo) / (hi - lo) * (right - left)

    # нульова лінія «сигнал = шум»
    top, bot = 92, 470
    f.append(line(xx(0), top - 6, xx(0), bot + 6, color=INK, sw=1.6, dash="4,4"))
    f.append(text(xx(0), top - 12, "SNR = 0 (сигнал = шум)", size=10, color=INK, italic=True))

    # сітка
    for s in range(-24, 33, 8):
        f.append(line(xx(s), top, xx(s), bot, color="#eef1f4", sw=1))
        f.append(text(xx(s), bot + 20, "%d" % s, size=10, color=MUTED))
    f.append(text((left + right) / 2, bot + 40, "потрібний SNR, дБ", size=11, color=MUTED, italic=True))

    rh = (bot - top) / len(rows)
    for i, (name, snr, col, note) in enumerate(rows):
        cy = top + i * rh + rh / 2
        # смуга від 0 до значення (ліворуч для від'ємних)
        x0 = xx(0)
        x1 = xx(snr)
        xa, xb = (min(x0, x1), max(x0, x1))
        f.append(rect(xa, cy - 11, xb - xa, 22, fill=col + "22", stroke=col, sw=1.6, rx=4))
        f.append(circle(x1, cy, 5, fill=col, stroke=col, sw=1))
        # підпис модуляції ліворуч
        f.append(text(200, cy + 4, name, size=11.5, color=col, bold=True, anchor="end"))
        # число + нота
        lblx = x1 + (10 if snr >= -2 else -10)
        anch = "start" if snr >= -2 else "end"
        f.append(text(lblx, cy - 3, "%+.1f дБ" % snr, size=10.5, color=INK, bold=True, anchor=anch))
        f.append(text(lblx, cy + 12, note, size=9, color=MUTED, anchor=anch, italic=True))

    f.append(text(W / 2, H - 12,
                  "Ліворуч від нуля — читається з-під шуму (обробний виграш). Праворуч — треба сигнал, гучніший за шум.",
                  size=10.5, color=INK, italic=True))
    return render(os.path.join(IMG, 'snr-ladder.svg'), W, H, *f)


if __name__ == '__main__':
    fig_sensitivity_stack()
    fig_ebn0()
    fig_fade_availability()
    fig_fresnel()
    fig_ktb_matched()
    fig_snr_ladder()
    print('OK: sensitivity-stack.svg, ebn0.svg, fade-availability.svg, fresnel.svg, ktb-matched.svg, snr-ladder.svg')
