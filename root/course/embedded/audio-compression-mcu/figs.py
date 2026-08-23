# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── bitrate: чому сирий PCM важкий, і що дає стиснення ─────────────────────────
# Ідея: одна вісь — біт/с. Показати, як сира ширина потоку росте з частотою й
# розрядністю, а тоді дві сходинки стиснення (ADPCM 4:1 і Opus ~10:1) складають
# той самий звук у крихітну частку. Головне — впіймати масштаб на око.

def fig_bitrate():
    W, H = 720, 340
    p = []
    x0 = 250          # ліва межа стовпчиків
    xmax = 660        # права межа (максимум шкали)
    span = xmax - x0
    ref = 256000.0    # 16 кГц × 16 біт → 256 кбіт/с = повна шкала

    rows = [
        ("сирий PCM  16 кГц·16 біт", 256000, "#fdecea", POS, "256 кбіт/с"),
        ("сирий PCM  8 кГц·16 біт",  128000, "#eef4ff", NEG, "128 кбіт/с"),
        ("ADPCM 4 біт  (≈ 4:1)",      64000, "#eafaf0", FIELD, "64 кбіт/с"),
        ("Opus голос  (≈ 10:1)",      24000, "#f2ecf8", "#8a5fb0", "24 кбіт/с"),
        ("Opus дуже стисло",          12000, "#fff7e6", "#b8860b", "12 кбіт/с"),
    ]
    y = 70
    bh, gap = 34, 18
    for label, br, fill, st, tag in rows:
        w = span * br / ref
        p.append(text(x0 - 12, y + bh * 0.62, label, size=11, color=INK, anchor="end"))
        p.append(rect(x0, y, max(w, 3), bh, fill=fill, stroke=st, sw=1.6))
        p.append(text(x0 + max(w, 3) + 8, y + bh * 0.62, tag, size=10, color=st, bold=True, anchor="start"))
        y += bh + gap

    p.append(text(W / 2, H - 24,
                  "той самий звук: що нижча смуга потоку, то менше даних щосекунди — а отже, менше карти, ефіру й батареї",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "bitrate.svg"), W, H, *p,
           title="Скільки біт за секунду: сирий PCM проти стиснутого")


# ── adpcm: як влаштоване ADPCM — передбачення + адаптивний крок ────────────────
# Ідея: показати замкнене коло кодера. Замість самого відліку кодуємо різницю
# з передбаченням; квантуємо її ГРУБО, але крок квантування САМ підлаштовується
# під гучність. Ключ — декодер усередині кодера (той самий предиктор), тому
# обидва йдуть у ногу й помилка не накопичується.

def fig_adpcm():
    W, H = 720, 330
    p = []
    cy = 150

    # вхідний відлік
    p.append(fitbox(40, cy - 26, 92, 52, "відлік\nx[n]", size=12, bold=True,
                    fill=FILL, stroke=INK, sw=1.7))
    # суматор різниці
    sx = 190
    p.append(circle(sx, cy, 20, fill="#fdecea", stroke=POS, sw=1.9))
    p.append(text(sx, cy + 5, "−", size=20, color=POS, bold=True))
    p.append(arrow(132, cy, sx - 20, cy, color=INK, sw=1.8))
    # квантувач із адаптивним кроком
    qx = 300
    p.append(fitbox(qx, cy - 30, 116, 60, "квантувач\n4 біти\nкрок Δ", size=11, bold=True,
                    fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(arrow(sx + 20, cy, qx - 2, cy, color=INK, sw=1.8))
    p.append(text((sx + qx) / 2 + 4, cy - 12, "різниця d", size=9, color=MUTED))
    # вихід — 4-бітний код
    ox = 470
    p.append(fitbox(ox, cy - 24, 104, 48, "код c[n]\n4 біти", size=11, bold=True,
                    fill="#f2ecf8", stroke="#8a5fb0", sw=1.8))
    p.append(arrow(qx + 116, cy, ox - 2, cy, color=INK, sw=1.8))

    # зворотний контур: декодер усередині кодера будує передбачення
    py = cy + 95
    p.append(fitbox(qx - 6, py - 24, 128, 48, "предиктор\n(як у декодері)", size=10, bold=True,
                    fill="#eef4ff", stroke=NEG, sw=1.7))
    # від коду вниз у предиктор (стрілка вістрям у рамку)
    p.append(arrow(qx + 58, cy + 30, qx + 58, py - 24, color=NEG, sw=1.5))
    # від предиктора назад у суматор (передбачення)
    p.append(line(qx - 6, py, sx, py, color=NEG, sw=1.5))
    p.append(arrow(sx, py, sx, cy + 20, color=NEG, sw=1.5))
    p.append(text((sx + qx) / 2, py + 16, "передбачення x̂[n]", size=9, color=NEG))

    # адаптація кроку
    p.append(line(qx + 58, cy - 30, qx + 58, cy - 52, color=FIELD, sw=1.3, dash="4 3"))
    p.append(text(qx + 58, cy - 60, "гучно → крок ↑    тихо → крок ↓", size=9, color=FIELD, italic=True))

    p.append(text(W / 2, H - 18,
                  "кодуємо не сам відлік, а різницю з передбаченням; крок квантування сам стежить за гучністю",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "adpcm.svg"), W, H, *p,
           title="ADPCM: передбачення різниці плюс адаптивний крок")


# ── choose: коли ADPCM, а коли Opus — дві осі рішення ──────────────────────────
# Ідея: чесна карта вибору. Вісь X — скільки коштує процесору (ліворуч дешево),
# вісь Y — якість при однаковій смузі (вище краще). ADPCM — дешевий кут із
# помірною якістю; Opus — дорогий кут із чудовою якістю на ту саму смугу.
# Показати, що вибір — це не "краще/гірше", а що ти готовий віддати.

def fig_choose():
    W, H = 720, 360
    p = []
    ox, oy = 120, 300     # початок осей
    ax, ay = 660, 70      # кінці осей
    # осі
    p.append(arrow(ox, oy, ax, oy, color=INK, sw=1.8))          # X: вартість CPU
    p.append(arrow(ox, oy, ox, ay, color=INK, sw=1.8))          # Y: якість/біт
    p.append(text((ox + ax) / 2, oy + 34, "скільки коштує процесору  →", size=11, color=INK, bold=True))
    p.append(text(ox - 12, oy + 22, "дешево", size=9, color=MUTED, anchor="start"))
    p.append(text(ax - 8, oy + 22, "дорого", size=9, color=MUTED, anchor="end"))
    # Y-підпис вертикально
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">'
             'якість на ту саму смугу  →</text>' % (ox - 40, (oy + ay) / 2, FONT, INK, ox - 40, (oy + ay) / 2))

    # ADPCM — дешево, помірна якість
    p.append(circle(ox + 90, oy - 70, 12, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(fitbox(ox + 40, oy - 158, 190, 74,
                    "ADPCM (IMA)\nкілька зсувів на відлік\nвлазить у будь-який МК\nякість — «телефонна»",
                    size=10, bold=False, fill="#eafaf0", stroke=FIELD, sw=1.5))
    p.append(line(ox + 90, oy - 82, ox + 100, oy - 118, color=FIELD, sw=1.2, dash="3 3"))

    # Opus — дорого, чудова якість
    p.append(circle(ax - 90, ay + 60, 12, fill="#f2ecf8", stroke="#8a5fb0", sw=2))
    p.append(fitbox(ax - 250, ay + 90, 210, 74,
                    "Opus\nповноцінний кодек, RAM/такт\nбагатий: голос і музика\nчудова якість на низькій смузі",
                    size=10, bold=False, fill="#f2ecf8", stroke="#8a5fb0", sw=1.5))
    p.append(line(ax - 90, ay + 72, ax - 100, ay + 90, color="#8a5fb0", sw=1.2, dash="3 3"))

    p.append(text(W / 2, H - 12,
                  "вибір не «краще/гірше», а що ти готовий віддати: такти й пам'ять — за якість на тій самій смузі",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "choose.svg"), W, H, *p,
           title="ADPCM чи Opus: дешевизна проти якості на ту саму смугу")


# ── nibble: як два 4-бітні коди складаються в один байт ────────────────────────
# Ідея (для проєкту-кодека): показати ПОРЯДОК пакування. Стандарт IMA кладе
# ПЕРШИЙ відлік у молодший півбайт, ДРУГИЙ — у старший. Це головна пастка при
# ручному пакуванні: переплутаєш порядок — декодер із чужого плеєра дасть тріск.

def fig_nibble():
    W, H = 720, 300
    p = []
    # два коди на вході
    cy = 78
    p.append(fitbox(70, cy - 22, 150, 44, "код n₀\n(перший відлік)", size=11, bold=True,
                    fill="#eef4ff", stroke=NEG, sw=1.7))
    p.append(fitbox(500, cy - 22, 150, 44, "код n₁\n(другий відлік)", size=11, bold=True,
                    fill="#eafaf0", stroke=FIELD, sw=1.7))

    # байт: 8 клітинок, старший півбайт ліворуч (біти 7..4), молодший праворуч (3..0)
    bx, by, cw, ch = 250, 175, 27, 40
    labels = ["b7", "b6", "b5", "b4", "b3", "b2", "b1", "b0"]
    for i in range(8):
        x = bx + i * cw
        hi = i < 4                      # ліві 4 — старший півбайт
        fill = "#eafaf0" if hi else "#eef4ff"
        stroke = FIELD if hi else NEG
        p.append(rect(x, by, cw, ch, fill=fill, stroke=stroke, sw=1.6, rx=3))
        p.append(text(x + cw / 2, by + ch * 0.62, labels[i], size=10, color=INK))
    # дужки-підписи півбайтів
    p.append(text(bx + 2 * cw, by - 12, "старший півбайт = n₁", size=10, color=FIELD, bold=True))
    p.append(text(bx + 6 * cw, by - 12, "молодший півбайт = n₀", size=10, color=NEG, bold=True))
    p.append(text(bx + 4 * cw, by + ch + 22, "один байт = два відліки", size=11, color=MUTED, italic=True))

    # стрілки: n0 → молодший (праворуч), n1 → старший (ліворуч)
    p.append(arrow(145, cy + 22, bx + 6 * cw, by - 4, color=NEG, sw=1.6))
    p.append(arrow(575, cy + 22, bx + 2 * cw, by - 4, color=FIELD, sw=1.6))

    p.append(text(W / 2, H - 16,
                  "порядок IMA: перший код — у молодші біти, другий — у старші (byte = (n₁ << 4) | n₀)",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "nibble.svg"), W, H, *p,
           title="Пакування ADPCM: два 4-бітні коди в один байт, молодший перший")


# ── hist-timeline: родовід стиснення звуку від DPCM до Opus ───────────────────
# Ідея (для вставки-історії): одна горизонтальна вісь часу, чотири віхи —
# DPCM (ідея-патент 1950/52) → ADPCM (адаптивний крок) → IMA/DVI4 (стандарт 1992)
# → Opus (2012). Головне, що словами передати важко: Opus не продовжує ту саму
# лінію, а ЗЛИВАЄ дві окремі — мовний SILK і музичний CELT. Показуємо це двома
# доріжками, що сходяться в одну точку.

def fig_hist_timeline():
    W, H = 780, 384
    p = []
    y = 150                      # вісь часу
    cw, chh = 176, 108           # картка: ширина / висота
    xs = [100, 288, 476, 686]    # центри чотирьох віх (рівні проміжки, з полями під картку)

    # одна картка-віха: коло на осі, рік над ним, пунктир до картки, картка з
    # кольоровою жирною назвою (перший рядок) і описом під нею.
    def milestone(x, yr, name, desc, fill, col, merge=False):
        f = []
        r = 8 if merge else 7
        f.append(circle(x, y, r, fill=fill if merge else col, stroke=col, sw=2.4 if merge else 2))
        f.append(text(x, y - 14, yr, size=11, color=INK, bold=True))
        f.append(line(x, y + r, x, y + 34, color=col, sw=1.2, dash="3 3"))
        # картка: рамка + опис, зсунутий униз, щоб над ним стала кольорова назва
        f.append(fitbox(x - cw / 2, y + 34, cw, chh, "\n\n" + desc,
                        size=10, fill=fill, stroke=col, sw=1.5))
        f.append(text(x, y + 52, name, size=12, color=col, bold=True))
        return f

    # вісь часу
    p.append(arrow(xs[0] - 40, y, xs[3] + 42, y, color=INK, sw=1.8))
    p.append(text(xs[3] + 48, y + 4, "час", size=11, color=MUTED, anchor="start"))

    p += milestone(xs[0], "1950 → 1952", "DPCM",
                   "Чапін Катлер, Bell Labs\nпатент US 2 605 361:\nпередбач відлік,\nшли лише похибку", "#eef4ff", NEG)
    p += milestone(xs[1], "1970-ті", "ADPCM",
                   "крок квантування\nсам дихає з гучністю:\nдрібний у тиші,\nкрупний на гучному", "#eafaf0", FIELD)
    p += milestone(xs[2], "1992", "IMA / DVI4",
                   "код Intel DVI ухвалює\nInteractive Multimedia\nAssociation — спільний\nстандарт, без множень", "#fff7e6", "#b8860b")

    # ── дві окремі лінії, що зливаються в Opus ────────────────────────────────
    xo = xs[3]
    p.append(fitbox(xo - 210, y - 74, 150, 22, "мовний SILK  ·  Skype",
                    size=10, fill="#f2ecf8", stroke="#8a5fb0", sw=1.3, color="#6a4a8c"))
    p.append(fitbox(xo - 210, y - 48, 150, 22, "музичний CELT  ·  Xiph.Org",
                    size=10, fill="#f2ecf8", stroke="#8a5fb0", sw=1.3, color="#6a4a8c"))
    p.append(arrow(xo - 58, y - 63, xo - 6, y - 12, color="#8a5fb0", sw=1.6))
    p.append(arrow(xo - 58, y - 37, xo - 6, y - 12, color="#8a5fb0", sw=1.6))
    p += milestone(xo, "2012", "Opus",
                   "RFC 6716, відкритий\nпроцес IETF: одна\nбібліотека — і голос,\nі музика, будь-яка смуга", "#f2ecf8", "#8a5fb0", merge=True)

    p.append(text(W / 2, H - 12,
                  "одна лінія передбачення (DPCM → ADPCM → IMA) і окреме злиття двох кодеків в Opus — кроки різні за духом",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Родовід стиснення звуку: від похибки передбачення до Opus")


# ── quant-snr: звідки береться шум квантування й правило 6 дБ на біт ──────────
# Ідея (для детальної): показати, ЧОМУ кожен біт додає ~6 дБ. Ліворуч — сходинка
# квантування й пилкоподібна похибка (сигнал − сходинка), яка гуляє в межах
# ±½ кроку. Праворуч — пряма SNR = 6.02·N + 1.76 дБ: скидаємо біти (ADPCM 4,
# телефон 8, CD 16) на ту саму пряму. Головне — зв'язати картину похибки з
# формулою, чого текст словами дає важко.

def fig_quant_snr():
    W, H = 760, 360
    p = []

    # ── лівий блок: сходинка + пилкоподібна похибка ──────────────────────────
    lx, lw = 60, 300
    top, bot = 60, 210
    mid = (top + bot) / 2
    # плавний сигнал (пряма з нахилом) і його квантована сходинка
    import math
    # вісь
    p.append(line(lx, bot, lx + lw, bot, color=INK, sw=1.4))
    p.append(text(lx + lw / 2, bot + 44, "сигнал повз сходинки квантування", size=10, color=MUTED, italic=True))
    # плавна пряма
    x1, y1, x2, y2 = lx + 10, bot - 12, lx + lw - 10, top + 12
    p.append(line(x1, y1, x2, y2, color=NEG, sw=1.8))
    p.append(text(lx + lw - 8, top + 8, "справжній сигнал", size=9, color=NEG, anchor="end"))
    # сходинки: 6 рівнів
    steps = 6
    q = (y1 - y2) / steps          # висота кроку в px (за напрямком угору)
    seg = (x2 - x1) / steps
    poly = []
    for i in range(steps):
        yq = y1 - q * (i + 0.5)     # рівень сходинки (центр)
        xa = x1 + seg * i
        xb = x1 + seg * (i + 1)
        poly.append((xa, yq)); poly.append((xb, yq))
        # пунктир межі рівня
        p.append(line(lx, yq, lx + 6, yq, color=MUTED, sw=0.8))
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in poly)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (pts, FIELD))
    p.append(text(x1 + 4, y1 - q * 0.5 - 6, "сходинка q", size=9, color=FIELD, anchor="start"))
    # похибка = різниця; підпис ±q/2
    p.append(line(lx + lw + 6, top + 12, lx + lw + 6, bot - 12, color=POS, sw=1.0, dash="3 2"))
    p.append(text(lx + lw + 12, mid, "похибка", size=9, color=POS, anchor="start"))
    p.append(text(lx + lw + 12, mid + 14, "гуляє ±q/2", size=9, color=POS, anchor="start"))

    # ── правий блок: пряма SNR = 6.02N + 1.76 ────────────────────────────────
    gx, gy0, gw, gh = 470, 300, 250, 220     # початок осей, розміри
    p.append(arrow(gx, gy0, gx + gw, gy0, color=INK, sw=1.6))       # X: біти
    p.append(arrow(gx, gy0, gx, gy0 - gh, color=INK, sw=1.6))       # Y: SNR дБ
    p.append(text(gx + gw / 2, gy0 + 30, "біт на відлік  N →", size=10, color=INK, bold=True))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="10" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">'
             'SNR, дБ →</text>' % (gx - 30, gy0 - gh / 2, FONT, INK, gx - 30, gy0 - gh / 2))
    # пряма: N від 2 до 16, SNR від ~13.8 до ~98 дБ → у координати
    nmin, nmax = 0, 16
    smax = 100.0
    def X(n): return gx + gw * (n - nmin) / (nmax - nmin)
    def Y(s): return gy0 - gh * s / smax
    a, b = X(nmin), Y(6.02 * nmin + 1.76)
    c, d = X(nmax), Y(6.02 * nmax + 1.76)
    p.append(line(a, b, c, d, color="#8a5fb0", sw=2))
    p.append(text(X(9), Y(6.02 * 9 + 1.76) - 12, "6.02·N + 1.76 дБ", size=10, color="#8a5fb0", bold=True))
    # точки-орієнтири
    for n, tag, col in [(4, "ADPCM 4 біт", FIELD), (8, "телефон 8", "#b8860b"), (16, "CD 16 біт", NEG)]:
        s = 6.02 * n + 1.76
        p.append(circle(X(n), Y(s), 4, fill=col, stroke=col, sw=1))
        p.append(text(X(n) + 6, Y(s) + 4, tag, size=9, color=col, anchor="start"))

    p.append(text(W / 2, H - 12,
                  "кожен біт додає ~6 дБ: груба 4-бітна сходинка ADPCM шумніша за 16-бітний CD рівно на цю різницю",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "quant-snr.svg"), W, H, *p,
           title="Шум квантування й правило 6 дБ на біт")


# ── opus-arch: дві половини Opus і спільний ентропійний кодер ─────────────────
# Ідея (для детальної): показати, ЧОМУ Opus дорожчий і розумніший за ADPCM. Вхід
# розходиться на дві доріжки — мовну SILK (лінійне передбачення, як спадок ADPCM)
# і музичну CELT (MDCT — розклад на частоти + психоакустика), — а обидві зводяться
# в один діапазонний (range) кодер, що ентропійно пакує результат у біти. Гібридний
# режим зшиває обидві. Це та внутрішня складність, яку словами передати важко.

def fig_opus_arch():
    W, H = 780, 400
    p = []
    # вхід
    p.append(fitbox(40, 175, 92, 50, "звук\nз буфера", size=11, bold=True,
                    fill=FILL, stroke=INK, sw=1.7))
    # розгалуження
    bx = 132
    p.append(arrow(bx, 200, 190, 110, color=NEG, sw=1.6))
    p.append(arrow(bx, 200, 190, 290, color="#8a5fb0", sw=1.6))

    # верхня доріжка: SILK (LPC)
    p.append(fitbox(190, 78, 250, 64,
                    "SILK — мовна половина\nлінійне передбачення (LPC 16)\n+ передбачення тону (pitch)",
                    size=10, bold=False, fill="#eef4ff", stroke=NEG, sw=1.6))
    p.append(text(315, 60, "голос, вузька смуга", size=9, color=NEG, italic=True))

    # нижня доріжка: CELT (MDCT + психоакустика)
    p.append(fitbox(190, 258, 250, 64,
                    "CELT — музична половина\nMDCT: розклад на частоти\n+ психоакустика (маскування)",
                    size=10, bold=False, fill="#f2ecf8", stroke="#8a5fb0", sw=1.6))
    p.append(text(315, 340, "музика, широка смуга, мала затримка", size=9, color="#8a5fb0", italic=True))

    # гібрид-місток між доріжками
    p.append(line(315, 142, 315, 258, color=MUTED, sw=1.0, dash="4 3"))
    p.append(text(322, 200, "гібрид:", size=9, color=MUTED, anchor="start"))
    p.append(text(322, 213, "обидві разом", size=9, color=MUTED, anchor="start"))

    # злиття у range-кодер
    rx = 500
    p.append(arrow(440, 110, rx, 185, color=NEG, sw=1.6))
    p.append(arrow(440, 290, rx, 215, color="#8a5fb0", sw=1.6))
    p.append(fitbox(rx, 168, 150, 64,
                    "діапазонний\n(range) кодер\nентропійне пакування",
                    size=10, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.7))
    # вихід — кадри
    ox = 675
    p.append(arrow(rx + 150, 200, ox, 200, color=INK, sw=1.6))
    p.append(fitbox(ox, 175, 92, 50, "кадри\nOpus", size=11, bold=True,
                    fill=FILL, stroke=INK, sw=1.7))

    p.append(text(W / 2, H - 14,
                  "дві половини — передбачення для голосу й частоти для музики — зводяться в один ентропійний кодер",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "opus-arch.svg"), W, H, *p,
           title="Дві половини Opus: SILK-передбачення й CELT-частоти в спільному кодері")


# ── companding-curve: криві компресора μ-law та A-law проти лінії ─────────────
# Ідея (для вставки-math): показати, ЧОМУ логарифмічний закон дає малим сигналам
# більше кодів. Діагональ — лінійне кодування (рівні коди на весь діапазон).
# Крива μ-law круто йде вгору при малому вході: тиха ділянка входу [0..0.1]
# розтягується мало не на пів-виходу — туди й лягає більшість із 256 кодів.
# A-law поруч, лише з прямою ланкою біля нуля. Головне на око: де крива крута,
# там густо кодів; де полога — там рідко.

def fig_companding_curve():
    import math
    W, H = 720, 430
    p = []
    # квадрат осей (вхід x у [0..1] по горизонталі, вихід y у [0..1] вгору)
    ox, oy = 110, 360         # початок координат (лівий низ)
    sq = 300                  # сторона квадрата
    p.append(rect(ox, oy - sq, sq, sq, fill="#fbfcfd", stroke=MUTED, sw=1.0))
    p.append(arrow(ox, oy, ox + sq + 26, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - sq - 26, color=INK, sw=1.6))
    p.append(text(ox + sq / 2, oy + 34, "вхід  |x|  (частка від повної шкали)  →", size=11, color=INK, bold=True))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">'
             'вихід  y  (номер коду)  →</text>' % (ox - 40, oy - sq / 2, FONT, INK, ox - 40, oy - sq / 2))

    def PX(x): return ox + sq * x
    def PY(y): return oy - sq * y

    # діагональ — лінійне кодування
    p.append(line(PX(0), PY(0), PX(1), PY(1), color=MUTED, sw=1.4, dash="5 4"))
    p.append(text(PX(0.82), PY(0.82) + 16, "лінійне", size=10, color=MUTED, italic=True, anchor="start"))

    # крива μ-law: y = ln(1+μx)/ln(1+μ)
    mu = 255.0
    pts = []
    n = 120
    for i in range(n + 1):
        x = i / n
        y = math.log(1 + mu * x) / math.log(1 + mu)
        pts.append("%.1f,%.1f" % (PX(x), PY(y)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), POS))
    p.append(text(PX(0.42), PY(0.90), "μ-law  (μ = 255)", size=11, color=POS, bold=True, anchor="middle"))

    # крива A-law: A|x|/(1+lnA) при x<1/A; (1+ln(Ax))/(1+lnA) далі
    A = 87.6
    lnA = math.log(A)
    pts = []
    for i in range(n + 1):
        x = i / n
        if x < 1.0 / A:
            y = A * x / (1 + lnA)
        else:
            y = (1 + math.log(A * x)) / (1 + lnA)
        pts.append("%.1f,%.1f" % (PX(x), PY(y)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="2 3"/>' % (" ".join(pts), NEG))
    p.append(text(PX(0.55), PY(0.66), "A-law  (A = 87.6)", size=11, color=NEG, bold=True, anchor="middle"))

    # виділити: тиха ділянка входу [0..0.1] → великий шмат виходу
    xq = 0.1
    yq = math.log(1 + mu * xq) / math.log(1 + mu)
    p.append(line(PX(xq), oy, PX(xq), PY(yq), color=FIELD, sw=1.2, dash="3 3"))
    p.append(line(ox, PY(yq), PX(xq), PY(yq), color=FIELD, sw=1.2, dash="3 3"))
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10"/>'
             % (PX(0), PY(yq), PX(xq) - PX(0), oy - PY(yq), FIELD))
    p.append(text(PX(xq) + 8, PY(yq) - 6, "тихі 10 % входу…", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(PX(xq) + 8, PY(yq) + 10, "…займають ≈ " + str(round(yq * 100)) + " % кодів", size=10, color=FIELD, anchor="start"))

    p.append(text(W / 2, H - 14,
                  "де крива крута (тихий вхід) — туди лягає більшість кодів; де полога (гучний вхід) — кодів мало",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "companding-curve.svg"), W, H, *p,
           title="Крива компресора: μ-law та A-law проти лінійного кодування")


# ── companding-segments: 8 хорд μ-law і геометричні сходинки квантування ──────
# Ідея (для вставки-math): реальний кодек не бере ln у залізі, а наближає криву
# ВІСЬМА прямими хордами (сегментами) на кожну полярність. Кожен наступний
# сегмент удвічі ширший за попередній по входу, але несе ту саму кількість кодів
# (16) — тож крок квантування подвоюється щосегмента. Це та сама геометрична
# драбина, що й таблиця кроків ADPCM. Показуємо ширини сегментів стовпчиками,
# що подвоюються, і крок квантування, що росте вдвічі.

def fig_companding_segments():
    import math
    W, H = 740, 400
    p = []
    ox, oy = 90, 300          # початок осей
    axw = 560                 # ширина осі входу
    # 8 сегментів: ширини по входу 1,1,2,4,8,16,32,64 (перші два рівні — біля нуля)
    widths = [1, 1, 2, 4, 8, 16, 32, 64]
    total = float(sum(widths))    # = 128 (14-бітна півшкала μ-law: 2^13 = 8192, тут у «щаблях»)
    p.append(arrow(ox, oy, ox + axw + 24, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - 250, color=INK, sw=1.6))
    p.append(text(ox + axw / 2, oy + 52, "вхід (лінійна амплітуда) — межі 8 сегментів →", size=11, color=INK, bold=True))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">'
             'крок квантування Δ (лог-шкала) →</text>' % (ox - 42, oy - 120, FONT, INK, ox - 42, oy - 120))

    # кольори від тихого (зелений) до гучного (червоний)
    cols = ["#1f8f4d", "#3f9a3a", "#7a9e2a", "#a8912a", "#c07f2a", "#c56a26", "#c34f24", "#b83320"]
    x = ox
    step_h0 = 22              # висота стовпчика кроку для сегмента 0
    for i, w in enumerate(widths):
        seg_w = axw * w / total
        # висота ∝ log2(крок): крок подвоюється щосегмента → лінійний приріст висоти
        bh = step_h0 * (i + 1) * 0.9
        p.append(rect(x, oy - bh, seg_w, bh, fill=cols[i], stroke=INK, sw=1.0, rx=2))
        # номер сегмента всередині/над стовпчиком
        lbl_y = oy - bh - 8 if seg_w < 40 else oy - bh + 16
        lbl_col = INK if seg_w < 40 else "#ffffff"
        p.append(text(x + seg_w / 2, oy - bh - 8, "S%d" % i, size=10, color=INK, bold=True))
        # ширина сегмента під віссю
        p.append(line(x, oy, x, oy + 6, color=MUTED, sw=1.0))
        x += seg_w
    p.append(line(x, oy, x, oy + 6, color=MUTED, sw=1.0))

    # підписи-виноски: кожен сегмент = 16 кодів, крок ×2
    p.append(fitbox(ox + 8, oy - 244, 214, 46,
                    "кожен сегмент = 16 рівних кодів\nширина сегмента ×2 щоразу\n⇒ крок квантування Δ ×2",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.4))
    p.append(text(ox + axw * 0.06, oy + 26, "тихо: дрібний крок, густо кодів", size=10, color="#1f8f4d", anchor="start"))
    p.append(text(ox + axw * 0.62, oy + 26, "гучно: крупний крок, рідко кодів", size=10, color="#b83320", anchor="start"))

    p.append(text(W / 2, H - 14,
                  "та сама геометрична драбина, що й таблиця кроків ADPCM: рівні кроки на слух — це подвоєння на шкалі",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "companding-segments.svg"), W, H, *p,
           title="Вісім хорд μ-law: геометричні сходинки квантування")


if __name__ == "__main__":
    fig_bitrate()
    fig_adpcm()
    fig_choose()
    fig_nibble()
    fig_hist_timeline()
    fig_quant_snr()
    fig_opus_arch()
    fig_companding_curve()
    fig_companding_segments()
    print("OK: figures written to", OUT)
