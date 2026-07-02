# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори п'яти класичних стадій (узгоджено з палітрою svgkit).
C_IF = "#fdecea"; S_IF = POS          # Вибірка   (fetch)
C_ID = "#eef1f4"; S_ID = MUTED        # Декодування (decode)
C_EX = "#eaf6ef"; S_EX = FIELD        # Виконання (execute)
C_ME = "#eaf0fd"; S_ME = NEG          # Пам'ять   (memory)
C_WB = "#f3eefb"; S_WB = "#6b3fa0"    # Запис     (write-back)
DEAD = "#fbe9e7"                       # викинута робота

FIVE = [("Виб", C_IF, S_IF), ("Дек", C_ID, S_ID), ("Вик", C_EX, S_EX),
        ("Пам", C_ME, S_ME), ("Зап", C_WB, S_WB)]


def cell(cx, cy, label, fill, stroke, w=76, h=32):
    x, y = cx - w / 2, cy - h / 2
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.5, rx=5)
            + text(cx, cy + 5, label, size=12, color=stroke, bold=True))


def crossed(cx, cy, w=76, h=32):
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill=DEAD, stroke=POS, sw=1.3, rx=5)
    out += line(x + 6, y + 6, x + w - 6, y + h - 6, color=POS, sw=1.5)
    out += line(x + w - 6, y + 6, x + 6, y + h - 6, color=POS, sw=1.5)
    return out


# ── 1. stages5: п'ять стадій, кожна — свій блок, розріз на засувках ───────────
def fig_stages5():
    W, H = 860, 380
    p = []
    p.append(text(W / 2, 30, "П'ять класичних стадій — і що робить кожна", size=17, bold=True))
    x0, bw, gap = 40, 138, 22
    top, bh = 70, 62
    jobs = [
        ("ВИБІРКА", S_IF, C_IF, ["взяти команду з", "пам'яті за PC", "у регістр IR; PC+="]),
        ("ДЕКОД.", S_ID, C_ID, ["розібрати число-", "команду; прочитати", "потрібні регістри"]),
        ("ВИКОН.", S_EX, C_EX, ["АЛП рахує:", "арифметика або", "адреса для пам'яті"]),
        ("ПАМ'ЯТЬ", S_ME, C_ME, ["доступ до даних:", "завантажити або", "зберегти число"]),
        ("ЗАПИС", S_WB, C_WB, ["покласти результат", "назад у регістр", "(register write-back)"]),
    ]
    cxs = []
    for i, (name, sc, fc, lines) in enumerate(jobs):
        x = x0 + i * (bw + gap)
        cx = x + bw / 2
        cxs.append(cx)
        p.append(rect(x, top, bw, bh, fill=fc, stroke=sc, sw=2, rx=8))
        p.append(text(cx, top + 20, name, size=13, color=sc, bold=True))
        p.append(mtext(cx, top + 84, lines, size=10.5, color=INK, lh=1.28))
    # засувки (pipeline registers) між стадіями — вузькі стовпчики
    for i in range(len(jobs) - 1):
        lx = x0 + i * (bw + gap) + bw + gap / 2
        p.append(rect(lx - 5, top - 6, 10, bh + 118, fill="#fff8e1", stroke="#b8860b", sw=1.4, rx=3))
    p.append(text(x0 + bw + gap / 2, top + bh + 150, "між кожною парою стадій — засувка (pipeline register):",
                  size=11, color="#8a6508", bold=True, anchor="start"))
    p.append(text(x0 + bw + gap / 2, top + bh + 168, "щотакту вона замикає готовий результат стадії й передає його далі",
                  size=10.5, color=MUTED, italic=True, anchor="start"))
    # хід зверху вниз
    p.append(text(W / 2, 336, "Кожна стадія — окреме залізо; робота ділиться так, щоб усі шматки були приблизно рівні за часом.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 358, "PC — лічильник команд, IR — регістр команди, АЛП — арифметико-логічний пристрій.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "stages5.svg"), W, H, *p)


# ── 2. pipe-fill: п'ять команд у польоті, стовпчик — усі 5 стадій зайняті ─────
def fig_pipe_fill():
    W, H = 860, 400
    p = []
    p.append(text(W / 2, 30, "Наповнений конвеєр: у кожен такт у польоті п'ять різних команд", size=15.5, bold=True))
    x0, cw = 150, 74
    for i in range(9):
        p.append(text(x0 + i * cw, 70, "т%d" % (i + 1), size=10, color=MUTED, bold=True))
    rows = [96, 132, 168, 204, 240]
    for r, ry in enumerate(rows):
        p.append(text(x0 - 14, ry + 4, "ком.%d" % (r + 1), size=10.5, color=INK, bold=True, anchor="end"))
        for s, (lab, fc, sc) in enumerate(FIVE):
            cx = x0 + (r + s) * cw            # діагональ: зсув на 1 такт
            p.append(cell(cx, ry, lab, fc, sc, w=cw - 8, h=30))
    # стовпчик такту 5: усі п'ять стадій зайняті різними командами
    col = 4
    p.append(rect(x0 + col * cw - cw / 2, 80, cw, 180, fill="none", stroke=INK, sw=2.2, rx=6))
    p.append(text(x0 + col * cw, 280, "такт 5: усі 5 стадій зайняті", size=11, color=INK, bold=True))
    p.append(text(x0 + col * cw, 298, "(Зап·Пам·Вик·Дек·Виб — п'ять команд)", size=10, color=INK))
    p.append(text(W / 2, 340, "Одна команда все одно триває 5 тактів (затримка), але з лінії сходить нова щотакту.",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 362, "Розгін: перші 4 такти конвеєр наповнюється; далі — усталений темп, команда за такт.",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, 384, "Це і є перекриття фаз; чому воно множить пропускну здатність — окрема тема про конвеєр.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "pipe-fill.svg"), W, H, *p)


# ── 3. skip-stages: не кожна команда проходить усі стадії, але слот лишається ─
def fig_skip():
    W, H = 820, 360
    p = []
    p.append(text(W / 2, 30, "Не кожна команда справді працює в усіх стадіях", size=16, bold=True))
    x0, cw = 210, 108
    heads = ["ВИБ", "ДЕК", "ВИК", "ПАМ", "ЗАП"]
    for s, hlab in enumerate(heads):
        p.append(text(x0 + s * cw, 70, hlab, size=11, color=INK, bold=True))
    kinds = [
        ("ДОДАЙ R3←R1+R2", [1, 1, 1, 0, 1], "арифметика: пам'ять не потрібна"),
        ("ЗАВАНТАЖ R5←[R6]", [1, 1, 1, 1, 1], "читання з пам'яті — усі п'ять"),
        ("ЗБЕРЕЖИ [R6]←R5", [1, 1, 1, 1, 0], "запис у пам'ять: у регістр нема чого писати"),
        ("СТРИБОК", [1, 1, 1, 0, 0], "лише міняє PC"),
    ]
    rows = [96, 140, 184, 228]
    for k, (name, mask, note) in enumerate(kinds):
        ry = rows[k]
        p.append(text(x0 - cw + 4, ry + 4, name, size=10.5, color=INK, bold=True, anchor="end"))
        for s, on in enumerate(mask):
            cx = x0 + s * cw
            lab, fc, sc = FIVE[s]
            if on:
                p.append(cell(cx, ry, lab[:3], fc, sc, w=cw - 20, h=28))
            else:
                x, y, w, h = cx - (cw - 20) / 2, ry - 14, cw - 20, 28
                p.append(rect(x, y, w, h, fill="#fafafa", stroke="#d0d0d0", sw=1.2, rx=5))
                p.append(text(cx, ry + 4, "—", size=13, color=MUTED))
        p.append(text(x0 + 5 * cw - 4, ry + 4, note, size=9.5, color=MUTED, italic=True, anchor="start"))
    p.append(text(W / 2, 288, "Порожня стадія не зникає — команда однаково «займає її слот» такт, лише нічого не робить.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 312, "Так усі команди йдуть конвеєром у ногу: п'ять тактів кожна, ряд у ряд, без плутанини порядку.",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, 336, "[R6] — «те, що лежить у пам'яті за адресою в регістрі R6».",
                  size=9.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "skip-stages.svg"), W, H, *p)


# ── 4. stage-count: скільки стадій у реальних процесорах і компроміс ──────────
def fig_stage_count():
    W, H = 820, 460
    p = []
    p.append(text(W / 2, 30, "Скільки стадій — це вибір інженера, не закон природи", size=16, bold=True))
    x0 = 60
    rows = [
        ("Cortex-M0+", 2, ["Виб+Пред", "Дек+Вик"], "найощадніший: короткий конвеєр — менше звернень до Flash"),
        ("Cortex-M0 / M3 / M4", 3, ["Виб", "Дек", "Вик"], "класичні дрібні MCU: дешевий стрибок, простий"),
        ("класичний MIPS", 5, ["Виб", "Дек", "Вик", "Пам", "Зап"], "канон навчання: рівні стадії, чіткий load/store"),
        ("настільний ПК", 14, None, "стадій багато — заради високої частоти, ціна — дорогі промахи гілок"),
    ]
    y0, dy = 76, 74
    cw = 58
    for i, (name, n, labs, note) in enumerate(rows):
        ry = y0 + i * dy
        p.append(text(x0, ry + 2, name, size=12, color=INK, bold=True, anchor="start"))
        bx = x0 + 190
        if labs:
            for s in range(n):
                lab, fc, sc = FIVE[s]
                p.append(cell(bx + s * (cw + 4) + cw / 2, ry, labs[s], fc, sc, w=cw, h=26))
        else:
            # багато стадій — схематично 14 вузьких комірок
            nw = 32
            for s in range(n):
                fc = [C_IF, C_ID, C_EX, C_ME, C_WB][s % 5]
                sc = [S_IF, S_ID, S_EX, S_ME, S_WB][s % 5]
                x = bx + s * (nw + 2)
                p.append(rect(x, ry - 13, nw, 26, fill=fc, stroke=sc, sw=1.2, rx=3))
            p.append(text(bx + n * (nw + 2) + 6, ry + 4, "…14 стадій…", size=10, color=MUTED, italic=True, anchor="start"))
        p.append(text(x0, ry + 24, note, size=9.5, color=MUTED, italic=True, anchor="start"))
    # вісь компромісу
    ay = y0 + 4 * dy + 6
    p.append(line(x0 + 40, ay, W - 60, ay, color=INK, sw=1.8, dash=None))
    p.append(text(x0 + 40, ay - 10, "◄ мало стадій", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(W - 60, ay - 10, "багато стадій ►", size=11, color=POS, bold=True, anchor="end"))
    p.append(text(x0 + 40, ay + 20, "простіше, ощадніше,", size=10, color=NEG, anchor="start"))
    p.append(text(x0 + 40, ay + 34, "дешеві стрибки", size=10, color=NEG, anchor="start"))
    p.append(text(W - 60, ay + 20, "вища частота,", size=10, color=POS, anchor="end"))
    p.append(text(W - 60, ay + 34, "але дорогі промахи гілок", size=10, color=POS, anchor="end"))
    p.append(text(W / 2, H - 22, "Довший конвеєр дрібнить роботу на менші такти → вищу частоту; та кожен промах гілки коштує більше тактів.",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "stage-count.svg"), W, H, *p)


# ── 5. latch-shift: ЧОМУ засувки копіюємо з хвоста в голову (порядок зсуву) ───
def fig_latch_shift():
    W, H = 860, 470
    p = []
    p.append(text(W / 2, 28, "Порядок зсуву засувок: чому з хвоста в голову", size=16, bold=True))
    names = ["IF/ID", "ID/EX", "EX/MEM", "MEM/WB"]
    cols = [S_ID, S_EX, S_ME, S_WB]
    fills = [C_ID, C_EX, C_ME, C_WB]

    def row_of_latches(y, contents, title, tcol):
        pp = [text(60, y - 34, title, size=12, color=tcol, bold=True, anchor="start")]
        x0, bw, gap = 175, 128, 30
        for i in range(4):
            x = x0 + i * (bw + gap)
            cx = x + bw / 2
            pp.append(rect(x, y - 22, bw, 44, fill=fills[i], stroke=cols[i], sw=1.8, rx=7))
            pp.append(text(cx, y - 4, names[i], size=11, color=cols[i], bold=True))
            pp.append(text(cx, y + 14, contents[i], size=10.5, color=INK))
            if i < 3:
                ax = x + bw + gap / 2
                pp.append(arrow(x + bw + 3, y, x + bw + gap - 3, y, color=MUTED, sw=1.6))
        return pp

    # правильно: копіюємо праву засувку першою, тоді ліву → команди зсуваються рівно на 1
    p.append(text(60, 62, "ПРАВИЛЬНО — копіюємо з хвоста (WB) до голови (IF):",
                  size=12.5, color=FIELD, bold=True, anchor="start"))
    p += row_of_latches(116, ["к.5", "к.4", "к.3", "к.2"], "було на початку такту", MUTED)
    p += row_of_latches(186, ["к.6", "к.5", "к.4", "к.3"], "стало після зсуву — кожна на 1 крок", FIELD)
    p.append(text(W / 2, 222, "MEM/WB ← EX/MEM ← ID/EX ← IF/ID  (спершу спорожнили праву, тоді туди зайшла ліва)",
                  size=10.5, color=MUTED, italic=True))

    # неправильно: копіюємо ліву першою → одне значення "протікає" крізь усі стадії за такт
    p.append(text(60, 266, "НЕПРАВИЛЬНО — копіюємо з голови (IF) до хвоста (WB):",
                  size=12.5, color=POS, bold=True, anchor="start"))
    p += row_of_latches(320, ["к.5", "к.4", "к.3", "к.2"], "було на початку такту", MUTED)
    p += row_of_latches(390, ["к.6", "к.6", "к.6", "к.6"], "стало — к.6 «протекла» крізь усі 4 за такт!", POS)
    p.append(text(W / 2, 426, "IF/ID→ID/EX затерло к.4 значенням к.6, потім к.6 поповзла далі тим самим тактом — 4 стадії за 1 такт.",
                  size=10.5, color=POS, italic=True))
    p.append(text(W / 2, 458, "Засувки — це паралельні тригери: усі захоплюють НОВЕ від фронту такту, читаючи СТАРЕ. У коді старе бережемо, ідучи з хвоста.",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "latch-shift.svg"), W, H, *p)


# ── 6. inflight-snapshot: масив 5 засувок у русі — розгін, 5 у польоті, дренаж ─
def fig_inflight():
    W, H = 900, 430
    p = []
    p.append(text(W / 2, 28, "Масив із п'яти засувок у русі: розгін → 5 у польоті → дренаж", size=15.5, bold=True))
    stage_names = ["IF", "ID", "EX", "MEM", "WB"]
    scols = [S_IF, S_ID, S_EX, S_ME, S_WB]
    sfills = [C_IF, C_ID, C_EX, C_ME, C_WB]
    # стан на кожному такті: у якій стадії яка команда (0 = порожньо/бульбашка)
    # такти 1..9, команди 1..5 вводяться на тактах 1..5
    ticks = list(range(1, 10))
    # snapshot[t][s] = номер команди в стадії s на початку такту t (після зсуву)
    x0, cw = 210, 74
    top, rh = 92, 52
    # заголовки тактів
    for j, t in enumerate(ticks):
        p.append(text(x0 + j * cw + cw / 2, top - 12, "такт %d" % t, size=10, color=MUTED, bold=True))
    for s in range(5):
        ry = top + s * rh
        p.append(text(x0 - 14, ry + rh / 2 + 4, stage_names[s], size=12, color=scols[s], bold=True, anchor="end"))
        for j, t in enumerate(ticks):
            # команда у стадії s на такті t: k = t - s (якщо 1..5)
            k = t - s
            x = x0 + j * cw
            if 1 <= k <= 5:
                p.append(rect(x + 4, ry + 4, cw - 8, rh - 8, fill=sfills[s], stroke=scols[s], sw=1.6, rx=6))
                p.append(text(x + cw / 2, ry + rh / 2 + 4, "к.%d" % k, size=11.5, color=scols[s], bold=True))
            else:
                p.append(rect(x + 4, ry + 4, cw - 8, rh - 8, fill="#fafafa", stroke="#dcdcdc", sw=1.1, rx=6))
                p.append(text(x + cw / 2, ry + rh / 2 + 4, "·", size=13, color="#c0c0c0"))
    # рамка: такт 5 — усі 5 стадій зайняті
    col5 = 4
    p.append(rect(x0 + col5 * cw + 1, top + 1, cw - 2, 5 * rh - 2, fill="none", stroke=INK, sw=2.4, rx=5))
    p.append(text(x0 + col5 * cw + cw / 2, top + 5 * rh + 16, "усі 5", size=10, color=INK, bold=True))
    p.append(text(x0 + col5 * cw + cw / 2, top + 5 * rh + 30, "у польоті", size=10, color=INK, bold=True))
    # позначки розгін / усталений / дренаж
    ay = top + 5 * rh + 4
    p.append(line(x0, ay, x0 + 4 * cw, ay, color=NEG, sw=2))
    p.append(text(x0 + 2 * cw, ay + 16, "розгін (наповнення)", size=10, color=NEG, bold=True))
    p.append(line(x0 + 5 * cw, ay, x0 + 6 * cw, ay, color=FIELD, sw=2))
    p.append(line(x0 + 5 * cw, ay, x0 + 9 * cw, ay, color=POS, sw=2, dash="4 3"))
    p.append(text(x0 + 7 * cw, ay + 16, "дренаж (спорожнення)", size=10, color=POS, bold=True))
    p.append(text(W / 2, H - 40, "Команда 1 вибрана на такті 1, а завершує (WB) аж на такті 5 — рівно 5 тактів по вибірці.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, H - 20, "На спаді нові команди не входять — «бульбашки» (·) повзуть конвеєром, доки остання не допрацює.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "inflight-snapshot.svg"), W, H, *p)


# ── 7. risc-birth: звідки взялися п'ять стадій — лінія народження RISC ─────────
def fig_risc_birth():
    W, H = 900, 440
    p = []
    p.append(text(W / 2, 30, "Звідки взялися п'ять стадій: лінія народження RISC", size=16, bold=True))

    ax0, ax1, ay = 66, W - 40, 308
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    p.append(text(ax1, ay + 24, "час", size=10, color=MUTED, italic=True, anchor="end"))

    y_lo, y_hi = 1974, 1991
    def xof(yr):
        return ax0 + (ax1 - ax0 - 24) * (yr - y_lo) / (y_hi - y_lo)

    for yr in (1975, 1980, 1985, 1990):
        x = xof(yr)
        p.append(line(x, ay - 5, x, ay + 5, color=MUTED, sw=1.4))
        p.append(text(x, ay + 20, str(yr), size=10, color=MUTED, bold=True))

    # (рік, зверху?, колір-рамки, колір-заливки, заголовок, рядки)
    ev = [
        (1975, True,  S_IF, C_IF, "IBM 801 (Джон Кок)",
         ["перша RISC-машина;", "мало простих команд", "під компілятор"]),
        (1980, False, S_EX, C_EX, "Берклі: RISC (Паттерсон)",
         ["термін «RISC»;", "RISC-I — 31 команда,", "одна за такт"]),
        (1981, True,  S_ME, C_ME, "Стенфорд: MIPS (Геннессі)",
         ["без апаратних блокувань", "стадій — затори лагодить", "компілятор"]),
        (1985, False, S_WB, C_WB, "MIPS R2000",
         ["перша комерційна", "реалізація —", "5 стадій конвеєра"]),
        (1990, True,  "#6b3fa0", C_ID, "Підручник + DLX",
         ["слово «затор» (hazard)", "й навчальна модель —", "канон на весь світ"]),
    ]
    bw, bh = 168, 68
    for yr, up, sc, fc, title, lines in ev:
        x = xof(yr)
        p.append(circle(x, ay, 6, fill=sc, stroke="#ffffff", sw=1.6))
        by = ay - 44 - bh if up else ay + 44
        bx = x - bw / 2
        bx = max(6, min(bx, W - bw - 6))
        conn_y = by + bh if up else by
        p.append(line(x, ay + (-7 if up else 7), x, conn_y, color=sc, sw=1.4, dash="3,3"))
        p.append(rect(bx, by, bw, bh, fill=fc, stroke=sc, sw=1.6, rx=7))
        p.append(text(bx + bw / 2, by + 17, title, size=10.5, color=sc, bold=True))
        p.append(mtext(bx + bw / 2, by + 34, lines, size=9, color=INK, lh=1.3))

    p.append(text(W / 2, H - 30, "Ідея → термін → без-блокувань → комерційна реалізація → канон: п'ять різних кроків, не один.",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, H - 12, "«Перший» тут — не одне ім'я: 801 дав ідею, Берклі й Стенфорд — робочі RISC, R2000 — продукт.",
                  size=9.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "risc-birth.svg"), W, H, *p)


if __name__ == "__main__":
    fig_stages5()
    fig_pipe_fill()
    fig_skip()
    fig_stage_count()
    fig_latch_shift()
    fig_inflight()
    fig_risc_birth()
    print("OK: figs written to", OUT)
