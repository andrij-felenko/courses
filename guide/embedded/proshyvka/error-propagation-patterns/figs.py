# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── pyramid-vs-flat: вкладені if проти ранніх повернень ────────────────────────
# Ідея: та сама логіка двома формами. Ліворуч «піраміда» — кожна перевірка успіху
# додає рівень вкладеності, корисна дія тоне праворуч-униз. Праворуч guard-clause:
# кожна невдача виходить одразу, корисна дія лишається на одному, лівому рівні.

def fig_pyramid_vs_flat():
    W, H = 720, 360
    p = []
    colx = [40, 400]
    titles = ["Піраміда: перевіряємо успіх", "Сторожі: виходимо на невдачі"]
    tcol = [POS, FIELD]
    for c in range(2):
        p.append(text(colx[c] + 150, 52, titles[c], size=13, bold=True, color=tcol[c]))

    # ── ліворуч: вкладеність зростає вправо-вниз ──
    bw, bh, step = 250, 34, 26
    top = 76
    left_rows = ["if open() == OK {", "  if read() == OK {", "    if check() == OK {", "      робота;"]
    for i, t in enumerate(left_rows):
        x = colx[0] + i * 18
        y = top + i * (bh + 8)
        last = (i == len(left_rows) - 1)
        p.append(fitbox(x, y, bw - i * 18, bh, t, size=11,
                        fill=("#eafaf0" if last else "#fdecea"),
                        stroke=(FIELD if last else POS), sw=1.4,
                        bold=last, color=INK))
    p.append(mtext(colx[0] + 6, top + 4 * (bh + 8) + 22,
                   "корисна дія — найглибше праворуч;\nкожна гілка else ще нижче",
                   size=10, color=MUTED, anchor="start"))

    # ── праворуч: усе на одному рівні, ранні return ──
    rb_rows = [
        ("if open()  != OK return err;", POS),
        ("if read()  != OK return err;", POS),
        ("if check() != OK return err;", POS),
        ("робота;  // лишилась тут, зліва", FIELD),
    ]
    for i, (t, col) in enumerate(rb_rows):
        x = colx[1]
        y = top + i * (bh + 8)
        last = (i == len(rb_rows) - 1)
        p.append(fitbox(x, y, bw, bh, t, size=11,
                        fill=("#eafaf0" if last else "#fff6f5"),
                        stroke=col, sw=1.4, bold=last, color=INK))
    p.append(mtext(colx[1] + 6, top + 4 * (bh + 8) + 22,
                   "невдача — і одразу геть;\nщасливий шлях рівний, без сходів",
                   size=10, color=MUTED, anchor="start"))

    p.append(text(W / 2, H - 16,
                  "та сама логіка: ліворуч вкладеність росте з кожною перевіркою, праворуч лишається пласкою",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "pyramid-vs-flat.svg"), W, H, *p,
           title="Піраміда вкладень проти ранніх повернень")


# ── cleanup-ladder: захоплення вниз, звільнення вгору, всі збої в одну точку ────
# Ідея: ресурси беруться по черзі (відкрив порт → виділив буфер → відкрив файл).
# Будь-яка невдача стрибає до ОДНІЄЇ мітки cleanup, що звільняє у ЗВОРОТНОМУ
# порядку — і тільки те, що встигли взяти. Один вихід, нуль дубльованого коду.

def fig_cleanup_ladder():
    W, H = 720, 400
    p = []
    # ліва колонка — захоплення (вниз)
    acq = ["port = open()", "buf = malloc()", "f = fopen()", "// робота з усім"]
    bw, bh, gap = 190, 40, 24
    topy = 80
    ax = 70
    ys = []
    for i, t in enumerate(acq):
        y = topy + i * (bh + gap)
        ys.append(y)
        last = (i == len(acq) - 1)
        p.append(fitbox(ax, y, bw, bh, t, size=11,
                        fill=("#eafaf0" if last else FILL), stroke=(FIELD if last else INK),
                        sw=1.5, bold=last))
        if i < len(acq) - 1:
            p.append(arrow(ax + bw / 2, y + bh, ax + bw / 2, ys[i] + bh + gap, color=MUTED, sw=1.3))
    p.append(text(ax + bw / 2, topy - 14, "захоплення — по черзі", size=11, color=INK, bold=True))

    # права колонка — звільнення (вгору, дзеркально)
    rel = ["fclose(f)", "free(buf)", "close(port)", "return ret;"]
    rx = 460
    rys = []
    for i, t in enumerate(rel):
        # розмістити навпроти відповідного ресурсу, але йдемо знизу-вгору
        y = topy + (len(rel) - 1 - i) * (bh + gap)
        rys.append(y)
        first = (i == len(rel) - 1)
        p.append(fitbox(rx, y, bw, bh, t, size=11,
                        fill=("#fff6f5" if not first else "#f6f4ec"),
                        stroke=(POS if not first else INK), sw=1.5, bold=first))
    p.append(text(rx + bw / 2, topy - 14, "звільнення — у зворотному порядку", size=11, color=POS, bold=True))
    # стрілки звільнення вгору
    for i in range(len(rel) - 1):
        yy = topy + (len(rel) - 1 - i) * (bh + gap)
        p.append(arrow(rx + bw / 2, yy, rx + bw / 2, yy - gap, color=POS, sw=1.6))

    # мітка cleanup між колонками
    midx = (ax + bw + rx) / 2
    cy = topy + 1.5 * (bh + gap) + bh / 2
    cl, clw, clh = textbox(midx, cy, "cleanup:", size=12, bold=True,
                           fill="#f6f4ec", stroke=INK, sw=2, pad=10)
    p.append(cl)
    # збої з кожного захоплення → в одну мітку
    for i in range(3):
        y = ys[i] + bh / 2
        p.append(line(ax + bw, y, midx - clw / 2, cy, color=POS, sw=1.5, dash="4 3"))
    p.append(text(midx, cy - clh / 2 - 8, "будь-яка невдача — сюди", size=10, color=POS, bold=True))
    # від мітки у звільнення
    p.append(arrow(midx + clw / 2, cy, rx, rys[0] + bh / 2, color=INK, sw=1.6))

    p.append(text(W / 2, H - 16,
                  "звільняємо лише те, що встигли взяти, і в зворотному порядку — з одного, спільного виходу",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "cleanup-ladder.svg"), W, H, *p,
           title="Сходи cleanup: один вихід для всіх збоїв")


# ── frame-choice: що зробити з помилкою в ЦІЙ рамці ────────────────────────────
# Ідея: коли помилка дійшла до функції, є рівно три чесні відповіді — провести
# далі, обробити тут, або свідомо проковтнути. Кожна має своє «коли доречно».

def fig_frame_choice():
    W, H = 720, 320
    p = []
    # центральний вузол — помилка прийшла
    cx = W / 2
    root, rw, rh = textbox(cx, 64, "Помилка прийшла в цю функцію",
                           size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=12)
    p.append(root)

    cols = [
        (150, "ПРОВЕСТИ", FIELD,
         "return err;\nмені тут не зарадити —\nнехай вирішує вищий рівень",
         "типовий вибір"),
        (cx, "ОБРОБИТИ", NEG,
         "тут є запасний план:\nретрай, значення за\nзамовчуванням, інша гілка",
         "де є чим зарадити"),
        (W - 150, "ПРОКОВТНУТИ", POS,
         "ігнорую свідомо й\nз коментарем — лише на\nшляху прибирання тощо",
         "рідко й обережно"),
    ]
    by = 150
    for x, head, col, body, note in cols:
        hb, hbw, hbh = textbox(x, by, head, size=12, bold=True, color=col,
                               fill=BG, stroke=col, sw=1.8, pad=8, min_w=120)
        p.append(line(cx, 64 + rh / 2, x, by - hbh / 2, color=col, sw=1.5))
        p.append(hb)
        p.append(mtext(x, by + 36, body, size=10, color=INK))
        p.append(text(x, by + 92, note, size=10, color=col, bold=True, italic=True))

    p.append(text(W / 2, H - 14,
                  "три чесні відповіді на одну помилку; проковтнути — лише свідомо й із приміткою, ніколи мовчки",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "frame-choice.svg"), W, H, *p,
           title="Три відповіді на помилку в цій рамці")


# ── macro-expand: ESP_GOTO_ON_ERROR розгортається в do{}while(0) ───────────────
# Ідея: один рядок-виклик макроса ховає всередині сторожа + лог + запис ret +
# стрибок на мітку, загорнуті в do{}while(0). Показуємо ліворуч компактний
# виклик, праворуч — у що його розгортає препроцесор, рядок у рядок.

def fig_macro_expand():
    W, H = 760, 430
    p = []
    p.append(text(190, 54, "Що ти пишеш", size=13, bold=True, color=FIELD))
    p.append(text(545, 54, "У що це розгортає препроцесор", size=13, bold=True, color=POS))

    # ліворуч — компактний виклик
    call = "ESP_GOTO_ON_ERROR(\n  port_read(p, buf, n),\n  cleanup, TAG, \"read\");"
    p.append(fitbox(40, 80, 300, 92, call, size=12,
                    fill="#eafaf0", stroke=FIELD, sw=1.6, color=INK))
    p.append(mtext(190, 200,
                   "один рядок на крок:\nкод, мітка, тег, підпис",
                   size=10, color=MUTED))

    # стрілка «розгортається в»
    p.append(arrow(348, 126, 392, 126, color=INK, sw=1.8))

    # праворуч — тіло do{}while(0), по рядках з підсвіткою ролей
    rows = [
        ("do {", MUTED, BG),
        ("  esp_err_t err_rc_ = (x);", INK, FILL),          # локальний ret
        ("  if (unlikely(err_rc_ != ESP_OK)) {", POS, "#fff6f5"),  # сторож
        ("    ESP_LOGE(TAG, \"%s(%d): \"...,", NEG, "#eef3ff"),    # слід: функція+рядок
        ("              __FUNCTION__, __LINE__);", NEG, "#eef3ff"),
        ("    ret = err_rc_;", INK, "#f6f4ec"),              # у локальний ret
        ("    goto cleanup;", POS, "#fff6f5"),               # стрибок на мітку
        ("  }", MUTED, BG),
        ("} while (0)", MUTED, BG),
    ]
    rx, ry, rw, rh = 392, 80, 330, 34
    for i, (t, col, fill) in enumerate(rows):
        y = ry + i * (rh + 3)
        p.append(fitbox(rx, y, rw, rh, t, size=11, fill=fill, stroke=col, sw=1.3,
                        color=INK))

    # підписи-ролі праворуч від відповідних рядків
    notes = [
        (1, "локальний ret —\nмакрос вимагає його", INK),
        (2, "сторож: невдача?", POS),
        (3, "слід: функція + рядок\n(тег замість файла)", NEG),
        (6, "стрибок на ТВОЮ мітку", POS),
    ]
    for idx, note, col in notes:
        y = ry + idx * (rh + 3) + rh / 2
        p.append(mtext(rx + rw + 8, y - (note.count("\n")) * 6 + 3, note,
                       size=9, color=col, anchor="start"))

    render(os.path.join(OUT, "macro-expand.svg"), W, H, *p,
           title="ESP_GOTO_ON_ERROR під мікроскопом")


# ── goto-discipline: дозволений стрибок (вперед-униз до однієї мітки) проти ─────
# заборонених (назад, убік, до різних міток). Ідея: «goto considered harmful»
# стосується довільних стрибків — спагеті; cleanup-goto завжди вперед і вниз,
# тільки до ОДНІЄЇ мітки в кінці, тож лишається структурованим.

def fig_goto_discipline():
    W, H = 740, 400
    p = []
    # дві колонки рядків коду — імітація тіла функції
    def column(x0, title, tcol):
        out = [text(x0 + 95, 56, title, size=13, bold=True, color=tcol)]
        steps = ["крок 1", "крок 2", "крок 3", "крок 4", "мітка:"]
        ys = []
        bw, bh, gap = 190, 32, 16
        for i, s in enumerate(steps):
            y = 80 + i * (bh + gap)
            ys.append(y)
            last = (i == len(steps) - 1)
            out.append(fitbox(x0, y, bw, bh, s, size=11,
                              fill=("#f6f4ec" if last else FILL),
                              stroke=(INK if last else MUTED), sw=1.4, bold=last))
        return out, ys, bw, bh

    # ліворуч — дисциплінований cleanup-goto: усі стрибки вперед-униз в одну мітку
    lx = 60
    lc, lys, bw, bh = column(lx, "Дисципліна cleanup", FIELD)
    p += lc
    label_y = lys[-1] + bh / 2
    for i in (0, 1, 2, 3):
        y = lys[i] + bh / 2
        p.append(line(lx + bw, y, lx + bw + 46, label_y, color=FIELD, sw=1.6, dash="4 3"))
    p.append(arrow(lx + bw + 46, label_y, lx + bw, label_y, color=FIELD, sw=1.6))
    p.append(mtext(lx + 95, lys[-1] + bh + 26,
                   "тільки ВПЕРЕД і ВНИЗ,\nдо ОДНІЄЇ мітки — структуровано",
                   size=10, color=FIELD))

    # праворуч — спагеті: стрибки назад, убік, у різні точки
    rx = 460
    rc, rys, bw2, bh2 = column(rx, "Спагеті-goto", POS)
    # перевизначимо праву колонку без «мітка:» — там кілька довільних цілей
    rc = [text(rx + 95, 56, "Спагеті-goto", size=13, bold=True, color=POS)]
    rsteps = ["крок 1", "крок 2", "крок 3", "крок 4", "крок 5"]
    rys = []
    for i, s in enumerate(rsteps):
        y = 80 + i * (bh + 16)
        rys.append(y)
        rc.append(fitbox(rx, y, bw, bh, s, size=11, fill=FILL, stroke=MUTED, sw=1.4))
    p += rc
    # назад (3→1), убік-уперед (1→4), назад (4→2) — заборонені
    def jump(a, b, col):
        ya = rys[a] + bh / 2
        yb = rys[b] + bh / 2
        side = rx - 12
        p.append(line(rx, ya, side, ya, color=col, sw=1.5))
        p.append(line(side, ya, side, yb, color=col, sw=1.5))
        p.append(arrow(side, yb, rx, yb, color=col, sw=1.5))
    jump(2, 0, POS)   # назад
    jump(0, 3, NEG)   # перестриб уперед через крок
    jump(3, 1, POS)   # знову назад
    p.append(mtext(rx + 95, rys[-1] + bh + 26,
                   "назад, убік, у різні точки —\nнитку не простежити",
                   size=10, color=POS))

    p.append(text(W / 2, H - 14,
                  "«goto considered harmful» — про праве; cleanup-goto — завжди ліве: вперед, униз, в одну мітку",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "goto-discipline.svg"), W, H, *p,
           title="Який goto шкідливий, а який ні")


if __name__ == "__main__":
    fig_pyramid_vs_flat()
    fig_cleanup_ladder()
    fig_frame_choice()
    fig_macro_expand()
    fig_goto_discipline()
    print("OK: figures written to", OUT)
