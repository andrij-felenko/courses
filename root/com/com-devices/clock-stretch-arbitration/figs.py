# -*- coding: utf-8 -*-
"""Фігури до теми «Розтягування й арбітраж».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

HOLD = "#b08900"   # «притримане», застереження


def _wave(x0, y_hi, y_lo, segs, color, sw=2.6):
    """Цифрова хвиля від x0. segs — список (рівень 0/1, ширина).
    Повертає (фрагменти, x_кінець)."""
    out, x = [], x0
    prev = segs[0][0]
    y_prev = y_lo if prev else y_hi
    for i, (lvl, w) in enumerate(segs):
        y = y_lo if lvl else y_hi
        if i > 0 and lvl != prev:               # вертикальний фронт
            out.append(line(x, y_prev, x, y, color=color, sw=sw))
        out.append(line(x, y, x + w, y, color=color, sw=sw))
        x += w
        prev, y_prev = lvl, y
    return out, x


# ── 1. Розтягування такту: ведений тримає SCL внизу ──────────────────────────
def fig_stretch():
    W, H = 820, 330
    f = [text(W / 2, 30, "Розтягування такту: ведений тримає SCL внизу", size=16, bold=True)]

    y_hi, y_lo = 96, 150
    f.append(text(96, (y_hi + y_lo) / 2 + 4, "SCL", size=12.5, bold=True, color=NEG, anchor="end"))
    # три нормальні такти, довге притримання, ще такт
    segs = [(0, 32), (1, 32), (0, 32), (1, 32), (0, 150), (1, 32), (0, 32)]
    wave, xend = _wave(112, y_hi, y_lo, segs, NEG)
    f += wave

    # зона притримання
    hx0, hx1 = 112 + 32 * 4, 112 + 32 * 4 + 150
    f.append(rect(hx0, y_hi - 8, hx1 - hx0, (y_lo - y_hi) + 16, fill="#fbf3df", stroke=HOLD, sw=1.4, rx=4))
    f.append(text((hx0 + hx1) / 2, y_lo + 26, "ведений тримає SCL внизу", size=11, bold=True, color=HOLD))
    f.append(text((hx0 + hx1) / 2, y_lo + 44, "(ведучий уже відпустив, та лінія не піднялась)",
                  size=9.5, italic=True, color=MUTED))
    f.append(text(120, y_lo + 70, "ведучий чекає, поки SCL підніметься, і лише тоді веде далі",
                  size=11.5, bold=True, anchor="start"))

    f.append(fitbox(60, H - 56, W - 120, 42,
                    ["Розтягування — «гальмо» з боку веденого: єдиний спосіб повільному чіпу сказати «ще не готовий».",
                     "Працює лише тому, що SCL — спільна лінія з монтажним «І»: притримати внизу може будь-хто."],
                    size=11, fill="#eef6ef", stroke=FIELD))
    render(os.path.join(IMG, "stretch.svg"), W, H, *f)


# ── 2. Чому працює й де пастка: правильний vs наївний ведучий ─────────────────
def fig_stretch_why():
    W, H = 840, 360
    f = [text(W / 2, 30, "Чому розтягування працює — і де його ламають", size=16, bold=True)]

    # лівий блок — правильний ведучий
    lx, lw = 60, 360
    f.append(rect(lx, 60, lw, 200, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    f.append(text(lx + lw / 2, 86, "правильний ведучий", size=13, bold=True, color=FIELD))
    f.append(text(lx + lw / 2, 116, "відпустив SCL →", size=11.5, bold=True))
    f.append(text(lx + lw / 2, 138, "читає РЕАЛЬНИЙ рівень лінії", size=11.5))
    f.append(text(lx + lw / 2, 168, "лінія ще внизу?", size=11.5, bold=True))
    f.append(text(lx + lw / 2, 190, "→ чекаю, не цокаю далі", size=11.5, color=FIELD, bold=True))
    f.append(text(lx + lw / 2, 224, "дані завжди свіжі", size=11, italic=True, color=MUTED))

    # правий блок — наївний ведучий
    rx = W - 60 - lw
    f.append(rect(rx, 60, lw, 200, fill="#fbecec", stroke=POS, sw=2, rx=12))
    f.append(text(rx + lw / 2, 86, "наївний ведучий", size=13, bold=True, color=POS))
    f.append(text(rx + lw / 2, 116, "цокає за жорстким таймером", size=11.5, bold=True))
    f.append(text(rx + lw / 2, 138, "на лінію не дивиться", size=11.5))
    f.append(text(rx + lw / 2, 168, "«переїхав» розтягування", size=11.5, bold=True, color=POS))
    f.append(text(rx + lw / 2, 190, "→ зчитав недоготовлені дані", size=11.5, color=POS, bold=True))
    f.append(text(rx + lw / 2, 224, "часто: bit-bang, дешеві контролери", size=10.5, italic=True, color=MUTED))

    f.append(fitbox(60, H - 56, W - 120, 42,
                    "Розтягування поважає лише той ведучий, що читає реальний SCL. Звідси класичне «іноді працює, іноді ні».",
                    size=11.5, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, "stretch-why.svg"), W, H, *f)


# ── 3. Кілька ведучих на одній шині; перевірка вільної шини ───────────────────
def fig_multimaster():
    W, H = 840, 360
    f = [text(W / 2, 30, "Кілька ведучих на спільних лініях", size=16, bold=True)]

    # дві лінії SDA/SCL
    bx, ex = 90, W - 90
    f.append(line(bx, 96, ex, 96, color=POS, sw=3))
    f.append(text(bx - 6, 100, "SDA", size=11, bold=True, color=POS, anchor="end"))
    f.append(line(bx, 124, ex, 124, color=NEG, sw=3))
    f.append(text(bx - 6, 128, "SCL", size=11, bold=True, color=NEG, anchor="end"))

    # два ведучі зверху
    for cx, lab in ((220, "МК-ведучий A"), (440, "МК-ведучий B")):
        f.append(rect(cx - 75, 156, 150, 50, fill="#e9eefb", stroke=NEG, sw=2, rx=8))
        f.append(text(cx, 186, lab, size=11.5, bold=True))
        f.append(line(cx, 96, cx, 156, color=MUTED, sw=1.4))
    # ведені праворуч
    for cx, lab in ((640, "давач"), (740, "давач")):
        f.append(rect(cx - 42, 156, 84, 50, fill=FILL, stroke=MUTED, sw=1.6, rx=8))
        f.append(text(cx, 186, lab, size=11, bold=True))
        f.append(line(cx, 96, cx, 156, color=MUTED, sw=1.4))

    f.append(text(W / 2, 244, "Перш ніж стартувати, ведучий перевіряє: обидві лінії високі → шина ВІЛЬНА",
                  size=12.5, bold=True))
    f.append(text(W / 2, 266, "(хтось щойно дав СТОП). Так двоє не наступають одне одному.",
                  size=11, color=MUTED))

    f.append(fitbox(60, H - 56, W - 120, 42,
                    "Виявлення вільної шини — перший запобіжник. Лишається випадок, коли двоє стартують майже одночасно.",
                    size=11.5, fill="#eef6ef", stroke=FIELD))
    render(os.path.join(IMG, "multimaster.svg"), W, H, *f)


# ── 4. Арбітраж біт за бітом на SDA ──────────────────────────────────────────
def fig_arbitration():
    W, H = 860, 380
    f = [text(W / 2, 30, "Арбітраж: біт за бітом на SDA, перемагає «0»", size=16, bold=True)]

    x0 = 170
    bw = 70
    # A: 1 0 1 ...  B: 1 0 0 ...  розбіжність на 3-му біті
    A = [1, 0, 1]
    B = [1, 0, 0]
    bus = [a & b for a, b in zip(A, B)]

    def row(label, bits, y_hi, color, sw=2.4):
        f.append(text(x0 - 16, (y_hi + y_hi + 34) / 2 + 4, label, size=11, bold=True,
                      color=color, anchor="end"))
        segs = [(b, bw) for b in bits]
        wave, _ = _wave(x0, y_hi, y_hi + 34, segs, color, sw=sw)
        f.extend(wave)

    row("хоче A", A, 78, FIELD)
    row("хоче B", B, 148, HOLD)
    row("лінія SDA", bus, 222, POS, sw=2.9)

    # бітові підписи
    for i in range(3):
        f.append(text(x0 + bw * i + bw / 2, 70, "біт %d" % (i + 1), size=9.5, color=MUTED))

    # маркер розбіжності на 3-му біті
    dx = x0 + bw * 2 + bw / 2
    f.append(line(dx, 64, dx, 262, color=INK, sw=1.2, dash="4,3"))
    f.append(text(dx, 290, "A жене 0, B жене 1 → лінія = 0", size=10.5, bold=True))
    f.append(text(dx, 308, "B бачить 0, хоч хотів 1 → програв", size=10.5, bold=True, color=HOLD))

    f.append(fitbox(60, H - 50, W - 120, 36,
                    "Поки біти однакові — нічого не видно. На першій розбіжності монтажне «І» дає 0; хто жене «0», той виграв.",
                    size=11.5, fill="#eef6ef", stroke=FIELD))
    render(os.path.join(IMG, "arbitration.svg"), W, H, *f)


# ── 5. Як переможений розуміє програш (недеструктивність) ─────────────────────
def fig_loser():
    W, H = 840, 350
    f = [text(W / 2, 30, "Хто жене «1», а читає «0», той тихо відступає", size=16, bold=True)]

    # A — переможець
    f.append(rect(70, 70, 340, 150, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    f.append(text(240, 96, "ведучий A", size=13, bold=True, color=FIELD))
    f.append(text(240, 124, "жене 0  →  читає 0", size=12, bold=True))
    f.append(text(240, 148, "усе, як хотів", size=11.5))
    f.append(text(240, 178, "веде повідомлення ДАЛІ", size=12, bold=True, color=FIELD))
    f.append(text(240, 202, "навіть не помітив суперника", size=10.5, italic=True, color=MUTED))

    # B — переможений
    f.append(rect(W - 410, 70, 340, 150, fill="#fbecec", stroke=POS, sw=2, rx=12))
    f.append(text(W - 240, 96, "ведучий B", size=13, bold=True, color=POS))
    f.append(text(W - 240, 124, "жене 1  →  читає 0", size=12, bold=True))
    f.append(text(W - 240, 148, "розбіжність → «я програв»", size=11.5, color=POS, bold=True))
    f.append(text(W - 240, 178, "негайно замовкає, відступає", size=12, bold=True, color=POS))
    f.append(text(W - 240, 202, "повторить пізніше або стане веденим", size=10, italic=True, color=MUTED))

    f.append(fitbox(60, H - 76, W - 120, 62,
                    ["Недеструктивність: повідомлення переможця проходить ЦІЛИМ, без жодного зіпсованого байта.",
                     "Жодних колізій, повторів чи сміття — один проходить, інший чемно чекає наступної нагоди.",
                     "І все це — лише тому, що «0» на спільній лінії сильніший за «1»."],
                    size=11, fill="#eef6ef", stroke=FIELD))
    render(os.path.join(IMG, "loser.svg"), W, H, *f)


# ── 6. Синхронізація SCL кількох ведучих ─────────────────────────────────────
def fig_sclsync():
    W, H = 840, 360
    f = [text(W / 2, 30, "Спільний SCL — це «І» тактів обох ведучих", size=16, bold=True)]

    x0, bw = 170, 64
    # A швидший, B повільніший — спільна лінія: low найдовший, high найкоротший
    A = [(1, bw), (0, bw), (1, bw), (0, bw), (1, bw)]
    B = [(1, int(bw * 1.4)), (0, int(bw * 1.4)), (1, int(bw * 0.7)), (0, bw)]

    def row(label, segs, y_hi, color):
        f.append(text(x0 - 16, y_hi + 21, label, size=11, bold=True, color=color, anchor="end"))
        wave, _ = _wave(x0, y_hi, y_hi + 34, segs, color)
        f.extend(wave)

    row("такт A", A, 76, NEG)
    row("такт B", B, 142, HOLD)
    # спільна = AND по часу: будуємо вибіркою кожні 8px
    span = 5 * bw
    common = []
    step = 8
    for px in range(0, span, step):
        # рівень A
        def lvl_at(segs, p):
            acc = 0
            for v, w in segs:
                if p < acc + w:
                    return v
                acc += w
            return segs[-1][0]
        common.append((lvl_at(A, px) & lvl_at(B, px), step))
    row("лінія SCL", common, 222, FIELD)

    f.append(text(W / 2, 286, "низький період — «найдовший із низьких», високий — «найкоротший із високих»",
                  size=11, color=MUTED))

    f.append(fitbox(60, H - 50, W - 120, 36,
                    "Такти злипаються в один ритм без узгодження — з фізики монтажного «І». Тому біти SDA порівнюються в ті самі моменти.",
                    size=11, fill="#eef6ef", stroke=FIELD))
    render(os.path.join(IMG, "sclsync.svg"), W, H, *f)


# ── 7. Що з цього треба насправді ────────────────────────────────────────────
def fig_reality():
    W, H = 840, 330
    f = [text(W / 2, 30, "Що з цього треба насправді", size=16, bold=True)]

    # ліворуч — типовий випадок
    f.append(rect(60, 64, 360, 180, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    f.append(text(240, 92, "майже завжди: ОДИН ведучий", size=13, bold=True, color=FIELD))
    f.append(text(240, 120, "один МК керує всіма давачами", size=11.5))
    f.append(text(240, 150, "арбітраж не потрібен зовсім", size=11.5, color=MUTED))
    f.append(text(240, 180, "розтягування такту — ЧАСТО", size=12, bold=True, color=FIELD))
    f.append(text(240, 204, "(ним користуються давачі — підтримай його!)", size=10, italic=True, color=MUTED))

    # праворуч — рідкісний
    f.append(rect(W - 420, 64, 360, 180, fill=FILL, stroke=MUTED, sw=1.8, rx=12))
    f.append(text(W - 240, 92, "рідко: КІЛЬКА ведучих", size=13, bold=True))
    f.append(text(W - 240, 120, "два МК на спільних давачах,", size=11.5))
    f.append(text(W - 240, 142, "хост + співпроцесор", size=11.5))
    f.append(text(W - 240, 172, "тут потрібні арбітраж", size=12, bold=True))
    f.append(text(W - 240, 194, "і виявлення вільної шини", size=12, bold=True))

    f.append(fitbox(60, H - 56, W - 120, 42,
                    "Пріоритет: розтягування стосується тебе майже завжди; арбітраж — лише коли на шині справді кілька ведучих.",
                    size=11.5, fill="#fbecec", stroke=POS))
    render(os.path.join(IMG, "reality.svg"), W, H, *f)


if __name__ == "__main__":
    fig_stretch()
    fig_stretch_why()
    fig_multimaster()
    fig_arbitration()
    fig_loser()
    fig_sclsync()
    fig_reality()
    print("OK: 7 figures ->", IMG)
