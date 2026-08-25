# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN = "#caa24a"   # жовтий «попередження»
WARNBG = "#fff6e0"


# ── error-vs-warning: та сама стадія, різний наслідок ─────────────────────────
# Ідея: і error, і warning народжує компілятор на стадії розбору, але error спиняє
# збірку (баг не доходить до чипа), а warning пропускає прошивку з прихованим багом.

def fig_error_vs_warning():
    W, H = 760, 340
    p = []

    # спільне джерело — стадія розбору
    src, sw_, sh = textbox(W / 2, 96, "Компілятор — стадія розбору\n(граматика й типи)",
                           size=11, bold=True, color="#8a6d1a", fill=WARNBG, stroke=WARN, sw=2, pad=12)
    p.append(src)

    # ліва колонка — ERROR (стоп)
    ex, ew = 40, 320
    p.append(rect(ex, 150, ew, 150, fill="#fbecec", stroke=POS, sw=2.2, rx=12))
    cx = ex + ew / 2
    p.append(text(cx, 178, "ERROR — стоп-знак", size=14, color=POS, bold=True))
    p.append(text(cx, 202, "«не можу перекласти цей рядок»", size=10.5, color=INK))
    p.append(text(cx, 226, "збірку спинено", size=12, color=POS, bold=True))
    p.append(text(cx, 248, "прошивки немає", size=10, color=INK))
    p.append(text(cx, 282, "баг не доходить до чипа", size=10, color=POS))

    # права колонка — WARNING (пропуск)
    wx = 400
    p.append(rect(wx, 150, ew, 150, fill=WARNBG, stroke=WARN, sw=2.2, rx=12))
    wcx = wx + ew / 2
    p.append(text(wcx, 178, "WARNING — жовтий знак", size=14, color=WARN, bold=True))
    p.append(text(wcx, 202, "«переклав, але підозріло»", size=10.5, color=INK))
    p.append(text(wcx, 226, "збірка триває", size=12, color=FIELD, bold=True))
    p.append(text(wcx, 248, "прошивка є — з прихованим багом", size=10, color=INK))
    p.append(text(wcx, 282, "баг мовчки усередині чипа", size=10, color=POS))

    # стрілки від джерела до обох наслідків
    p.append(line(W / 2 - sw_ / 2, 110, cx + 30, 150, color=POS, sw=2.2))
    p.append(line(W / 2 + sw_ / 2, 110, wcx - 30, 150, color=WARN, sw=2.2))

    p.append(text(W / 2, 326, "ігнорований ворнінг небезпечніший за помилку: ніщо не кричить",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "error-vs-warning.svg"), W, H, *p,
           title="Error і warning: та сама стадія, різний наслідок")


# ── sharp-corners: галерея «гострих кутів» C ──────────────────────────────────
# Ідея: чотири легальні, але майже завжди помилкові конструкції; кожна —
# код-фрагмент + наслідок. Усі їх компілятор з -Wall відзначає до запуску.

def fig_sharp_corners():
    W, H = 880, 380
    p = []
    cards = [
        ("= замість ==", "if (f = read())", "присвоєння,\nне порівняння", "завжди «істина»", POS, "#fbecec"),
        ("неініціалізована", "int v;\nuse(v);", "читання сміття\nзі стека", "поведінка\nнепередбачувана", WARN, WARNBG),
        ("звуження типу", "uint8_t m =\n  1 << 9;", "512 не влазить\nу 8 біт", "маска = 0,\nбіт не встав", NEG, "#e9eefb"),
        ("висячий покажчик", "p = local();\n*p = 1;", "адреса кадру\nпісля return", "стек затерто,\nсміття/аварія", POS, "#fbecec"),
    ]
    n = len(cards)
    margin, gap = 30, 18
    cw = (W - 2 * margin - (n - 1) * gap) / n
    cy0 = 78
    chh = 280
    for i, (title, code, danger, result, col, fill) in enumerate(cards):
        x = margin + i * (cw + gap)
        p.append(rect(x, cy0, cw, chh, fill=fill, stroke=col, sw=1.8, rx=10))
        p.append(mtext(x + cw / 2, cy0 + 26, title, size=11.5, color=col, bold=True))
        # код-плашка (темна)
        codeh = 64
        p.append(rect(x + 10, cy0 + 44, cw - 20, codeh, fill="#1e1e2e", stroke="#333344", sw=1, rx=6))
        p.append(mtext(x + 18, cy0 + 64, code, size=10, color="#7fb8a0", anchor="start", lh=1.35))
        # небезпека
        p.append(text(x + cw / 2, cy0 + 138, "небезпека", size=9.5, color=MUTED, bold=True))
        p.append(mtext(x + cw / 2, cy0 + 156, danger, size=9.5, color=col, lh=1.3))
        # наслідок
        p.append(text(x + cw / 2, cy0 + 212, "наслідок", size=9.5, color=MUTED, bold=True))
        p.append(mtext(x + cw / 2, cy0 + 230, result, size=9.5, color=INK, lh=1.3))

    p.append(text(W / 2, H - 16, "усе це легальний C — компілятор із -Wall відзначає кожен рядок ще до запуску",
                  size=11, color=FIELD, italic=True))

    render(os.path.join(OUT, "sharp-corners.svg"), W, H, *p,
           title="Гострі кути C: легальні конструкції, що майже завжди помилкові")


# ── static-vs-dynamic: дві осі перевірки ──────────────────────────────────────
# Ідея: статика бачить весь код, але не знає даних; динаміка бачить реальні дані,
# але лише пройдені шляхи. Тому вони доповнюють одна одну.

def fig_static_vs_dynamic():
    W, H = 820, 360
    p = []
    colw = 360
    lx, rx = 30, W - 30 - colw
    top, ch = 80, 210

    # ліва — статична
    p.append(rect(lx, top, colw, ch, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    p.append(text(lx + colw / 2, top + 28, "статична (без запуску)", size=13.5, color=FIELD, bold=True))
    p.append(text(lx + colw / 2, top + 50, "ворнінги · статичний аналіз", size=10, color=INK))
    p.append(line(lx + 20, top + 62, lx + colw - 20, top + 62, color=FIELD, sw=1, dash="4 3"))
    for i, t in enumerate(["+ бачить весь код, усі шляхи",
                           "+ не потребує виконання",
                           "+ дешево і швидко",
                           "− не знає реальних даних",
                           "− можливі хибні тривоги"]):
        col = POS if t.startswith("−") else FIELD
        p.append(text(lx + 24, top + 86 + i * 25, t, size=10.5, color=col, anchor="start"))

    # права — динамічна
    p.append(rect(rx, top, colw, ch, fill="#e9eefb", stroke=NEG, sw=2, rx=12))
    p.append(text(rx + colw / 2, top + 28, "динамічна (із запуском)", size=13.5, color=NEG, bold=True))
    p.append(text(rx + colw / 2, top + 50, "тести · відлагоджувач · санітайзери", size=10, color=INK))
    p.append(line(rx + 20, top + 62, rx + colw - 20, top + 62, color=NEG, sw=1, dash="4 3"))
    for i, t in enumerate(["+ бачить реальні значення",
                           "+ ловить рантайм-баги",
                           "+ перевіряє фізичну поведінку",
                           "− лише пройдені шляхи",
                           "− потрібне залізо або симулятор"]):
        col = POS if t.startswith("−") else FIELD
        p.append(text(rx + 24, top + 86 + i * 25, t, size=10.5, color=col, anchor="start"))

    # середина — «доповнюють»
    p.append(circle(W / 2, top + ch / 2, 24, fill=BG, stroke=MUTED, sw=2))
    p.append(text(W / 2, top + ch / 2 + 5, "+", size=22, color=MUTED, bold=True))

    p.append(text(W / 2, H - 36, "статика ловить структурні вади; динаміка — поведінкові з реальними даними",
                  size=10.5, color=INK))
    p.append(text(W / 2, H - 16, "разом — повна сітка; порізно — сліпа пляма",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "static-vs-dynamic.svg"), W, H, *p,
           title="Дві осі перевірки: статична й динамічна")


# ── quality-nets: чотири фільтри вартості ─────────────────────────────────────
# Ідея: баг падає крізь рівні; що вище зловити — то дешевше. Ворнінги — найвищий
# і безкоштовний рівень, живий чіп — найнижчий і найдорожчий.

def fig_quality_nets():
    W, H = 820, 360
    p = []
    bx, bw = 130, 560
    rows = [
        ("ворнінги", "при кожній збірці — безкоштовно", FIELD, "#eef6ef"),
        ("статичний аналіз", "рідше, автоматично, на ПК", "#1f8a8a", "#e6f4f4"),
        ("хост-тести", "хвилини на ПК, автоматично", WARN, WARNBG),
        ("живий чіп", "повільно, потрібне залізо", NEG, "#e9eefb"),
    ]
    top, rh, gap = 70, 54, 14
    for i, (name, note, col, fill) in enumerate(rows):
        y = top + i * (rh + gap)
        p.append(rect(bx, y, bw, rh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(bx + bw / 2, y + 23, name, size=13, color=col, bold=True))
        p.append(text(bx + bw / 2, y + 42, note, size=9.5, color=MUTED, italic=True))
        # стрілка «баг падає» між рівнями
        if i < len(rows) - 1:
            ay = y + rh
            p.append(arrow(bx + bw + 24, ay + 2, bx + bw + 24, ay + gap - 2, color=MUTED, sw=1.8))

    # «баг» входить зверху
    p.append(arrow(bx + bw + 24, top - 18, bx + bw + 24, top - 2, color=INK, sw=2.4))
    p.append(text(bx + bw + 38, top - 8, "баг", size=11, color=INK, bold=True, anchor="start"))

    # шкала вартості зліва
    p.append(text(bx - 18, top + 30, "дешево", size=10, color=FIELD, bold=True, anchor="end"))
    p.append(text(bx - 18, top + 3 * (rh + gap) + 30, "найдорожче", size=10, color=NEG, bold=True, anchor="end"))
    p.append(arrow(bx - 70, top + 8, bx - 70, top + 3 * (rh + gap) + 40, color=MUTED, sw=1.6))

    p.append(text(W / 2, H - 16, "кожен клас багів дешевше зловити на своєму рівні, а не на вершині піраміди",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "quality-nets.svg"), W, H, *p,
           title="Чотири сітки якості: що раніше зловиш — то дешевше")


# ════════════════════════════════════════════════════════════════════════════
# Фігури детальної версії (static-analysis-d.md)
# ════════════════════════════════════════════════════════════════════════════


# ── dataflow: аналіз потоку даних веде стан змінної крізь граф ─────────────────
# Ідея: аналізатор тримає для покажчика «решітку» станів (unknown→allocated→
# freed→use) і перехід у «use після freed» = дефект. Це суть data-flow аналізу.

def fig_dataflow():
    W, H = 760, 320
    p = []
    states = [
        ("unknown", "ще нічого\nне відомо", MUTED, "#f1f1f1"),
        ("allocated", "malloc повернув\nживу пам'ять", FIELD, "#eef6ef"),
        ("freed", "free() —\nпам'ять мертва", WARN, WARNBG),
        ("use", "розіменування\nмертвого = дефект", POS, "#fbecec"),
    ]
    n = len(states)
    bw, bh = 150, 92
    gap = (W - 60 - n * bw) / (n - 1)
    y = 110
    centers = []
    for i, (name, note, col, fill) in enumerate(states):
        x = 30 + i * (bw + gap)
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(x + bw / 2, y + 26, name, size=13, color=col, bold=True))
        p.append(mtext(x + bw / 2, y + 48, note, size=9.5, color=INK, lh=1.3))
        centers.append((x, x + bw))
        if i > 0:
            lab = ["malloc", "free", "*ptr"][i - 1]
            ax = centers[i - 1][1]
            p.append(arrow(ax + 4, y + bh / 2, x - 4, y + bh / 2, color=INK, sw=1.7))
            p.append(text((ax + x) / 2, y - 8, lab, size=10, color=INK, bold=True))

    p.append(text(W / 2, y + bh + 44,
                  "аналізатор веде стан покажчика крізь усі шляхи; перехід у «use» після «freed» — дефект",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, y + bh + 70,
                  "те саме для NULL (може-NULL → розіменовано) і для меж (індекс поза розміром)",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "dataflow.svg"), W, H, *p,
           title="Аналіз потоку даних: стан змінної як решітка")


# ── false-positive: чотири підсумки аналізу (матриця помилок) ─────────────────
# Ідея: справжній стан коду × вердикт аналізатора = 2×2; хибна тривога й
# пропуск — дві різні ціни, і їх балансують агресивністю аналізу.

def fig_false_positive():
    W, H = 720, 360
    p = []
    gx, gy = 230, 90      # лівий-верхній кут сітки
    cw, chh = 220, 96
    # заголовки стовпців (вердикт аналізатора)
    p.append(text(gx + cw / 2, gy - 16, "аналізатор мовчить", size=11, color=INK, bold=True))
    p.append(text(gx + cw + cw / 2, gy - 16, "аналізатор кричить", size=11, color=INK, bold=True))
    # заголовки рядків (істина)
    p.append(mtext(gx - 16, gy + chh / 2 - 6, "код\nсправний", size=11, color=INK, anchor="end", lh=1.2, bold=True))
    p.append(mtext(gx - 16, gy + chh + chh / 2 - 6, "код\nдефектний", size=11, color=INK, anchor="end", lh=1.2, bold=True))

    cells = [
        (0, 0, "правильно тихо", "усе гаразд — і тиша", FIELD, "#eef6ef"),
        (1, 0, "ХИБНА ТРИВОГА", "галас на чистому коді\n(false positive)", WARN, WARNBG),
        (0, 1, "ПРОПУСК", "дефект проліз повз\n(false negative)", POS, "#fbecec"),
        (1, 1, "правильна знахідка", "дефект і спіймано", FIELD, "#eef6ef"),
    ]
    for col, row, title, note, c, fill in cells:
        x = gx + col * cw
        y = gy + row * chh
        p.append(rect(x, y, cw, chh, fill=fill, stroke=c, sw=2, rx=8))
        p.append(text(x + cw / 2, y + 30, title, size=11.5, color=c, bold=True))
        p.append(mtext(x + cw / 2, y + 52, note, size=9.5, color=INK, lh=1.3))

    p.append(text(W / 2, H - 30,
                  "агресивніший аналіз ловить більше дефектів, але дає більше хибних тривог",
                  size=10.5, color=INK))
    p.append(text(W / 2, H - 12,
                  "налаштування = вибір точки балансу між пропуском і галасом",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "false-positive.svg"), W, H, *p,
           title="Чотири підсумки аналізу: тривога правдива чи хибна")


# ── misra-pyramid: рівні зобов'язань MISRA ────────────────────────────────────
# Ідея: правила MISRA поділені за силою — mandatory (не порушувати ніколи),
# required (порушення лише з обґрунтованим відхиленням), advisory (бажано).

def fig_misra_levels():
    W, H = 720, 360
    p = []
    rows = [
        ("mandatory", "порушувати НІКОЛИ — без винятків", POS, "#fbecec"),
        ("required", "порушення лише з письмовим відхиленням (deviation)", WARN, WARNBG),
        ("advisory", "бажано дотримуватися; відхилення без формальностей", FIELD, "#eef6ef"),
    ]
    bx, bw = 90, 540
    top, rh, gap = 80, 64, 18
    for i, (name, note, col, fill) in enumerate(rows):
        y = top + i * (rh + gap)
        p.append(rect(bx, y, bw, rh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(bx + bw / 2, y + 26, name, size=14, color=col, bold=True))
        p.append(text(bx + bw / 2, y + 47, note, size=10, color=INK))

    p.append(text(W / 2, top + 3 * (rh + gap) + 22,
                  "усе відхилення — задокументоване: правило, причина, чому безпечно",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "misra-levels.svg"), W, H, *p,
           title="MISRA-C: три рівні сили правил")


if __name__ == "__main__":
    fig_error_vs_warning()
    fig_sharp_corners()
    fig_static_vs_dynamic()
    fig_quality_nets()
    fig_dataflow()
    fig_false_positive()
    fig_misra_levels()
    print("OK: figures written to", OUT)
