# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── spin-wait: одна нитка тримає замок, друга крутиться навколо нього ──────────
# Ідея: показати сам механізм спінлока. Ліва нитка захопила замок і працює з
# ресурсом; права прийшла другою, бачить «зайнято» і крутиться в тісному циклі
# перевірки, спалюючи такти, доки ліва не відпустить.

def fig_spin_wait():
    W, H = 700, 360
    p = []

    # центральний замок-ресурс
    lock_cx, lock_cy = W / 2, 150
    lb, lw, lh = textbox(lock_cx, lock_cy, "СПІЛЬНІ ДАНІ\n(замок)", size=13, bold=True,
                         fill="#f6f4ec", stroke=INK, sw=2, pad=14)
    p.append(lb)

    # ліва нитка — тримає замок, працює
    l1, l1w, l1h = textbox(140, lock_cy, "Нитка A\nтримає замок", size=12, bold=True,
                           color=FIELD, fill="#eafaf0", stroke=FIELD, sw=2, pad=11)
    p.append(l1)
    p.append(arrow(140 + l1w / 2, lock_cy, lock_cx - lw / 2, lock_cy, color=FIELD, sw=2.2))
    p.append(text(140, lock_cy + l1h / 2 + 22, "працює з ресурсом", size=11, color=FIELD))

    # права нитка — крутиться
    r1, r1w, r1h = textbox(W - 140, lock_cy, "Нитка B\nприйшла другою", size=12, bold=True,
                           color=POS, fill="#fdecea", stroke=POS, sw=2, pad=11)
    p.append(r1)
    # стрілка-відмова до замка (пунктир — не пускає)
    p.append(line(W - 140 - r1w / 2, lock_cy, lock_cx + lw / 2, lock_cy,
                  color=POS, sw=1.8, dash="5,4"))
    p.append(text((W - 140 - r1w / 2 + lock_cx + lw / 2) / 2, lock_cy - 12,
                  "зайнято", size=11, color=POS, bold=True))

    # петля «крутиться» біля правої нитки
    spin_cy = lock_cy + 95
    p.append(circle(W - 140, spin_cy, 30, fill=BG, stroke=POS, sw=2.2))
    # стрілка по колу (дуга-натяк двома відрізками зі стрілкою)
    p.append(arrow(W - 140 + 30, spin_cy - 6, W - 140 + 30, spin_cy + 8, color=POS, sw=2.0))
    p.append(mtext(W - 140, spin_cy - 4, "вільно?\nні.", size=10, color=POS, bold=True))
    p.append(text(W - 140, spin_cy + 56, "крутиться, палить такти", size=11, color=POS))

    p.append(text(W / 2, H - 18,
                  "поки A працює, B не засинає — вона марно крутиться, чекаючи звільнення",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "spin-wait.svg"), W, H, *p,
           title="Спінлок: другий чекає, крутячись на місці")


# ── spin-vs-sleep: дві стратегії чекання поряд ────────────────────────────────
# Ідея: ліворуч спінлок — ядро в циклі, час у нікуди, прокинення миттєве.
# Праворуч мʼютекс — ядро віддане планувальнику, працює інша задача, але вхід/
# вихід коштують перемикання контексту.

def fig_spin_vs_sleep():
    W, H = 720, 360
    p = []
    colx = [70, 400]
    colw = 250
    titles = ["Спінлок: крутитися", "Мʼютекс: заснути"]
    tcol = [POS, NEG]

    for c in range(2):
        cx = colx[c] + colw / 2
        p.append(text(cx, 52, titles[c], size=14, bold=True, color=tcol[c]))

        if c == 0:
            # спінлок: ядро зайняте порожнім циклом
            box = fitbox(colx[c], 80, colw, 70,
                         "ЯДРО зайняте\nциклом перевірки", size=12, bold=True,
                         fill="#fdecea", stroke=POS, sw=2)
            p.append(box)
            p.append(text(cx, 178, "↻ вільно? ні. вільно? ні.", size=12, color=POS, bold=True))
            p.append(text(cx, 210, "такти йдуть у нікуди", size=11, color=POS))
            p.append(fitbox(colx[c], 235, colw, 56,
                            "+ прокинення миттєве\n(нема перемикання)", size=11, bold=True,
                            color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.6))
        else:
            # мʼютекс: ядро віддане іншій задачі
            p.append(fitbox(colx[c], 80, colw, 70,
                            "ЯДРО віддане\nпланувальнику", size=12, bold=True,
                            fill="#eaf0fd", stroke=NEG, sw=2))
            p.append(text(cx, 178, "працює ІНША задача", size=12, color=NEG, bold=True))
            p.append(text(cx, 210, "наша спить, такти не горять", size=11, color=NEG))
            p.append(fitbox(colx[c], 235, colw, 56,
                            "− вхід і вихід коштують\nперемикання контексту", size=11, bold=True,
                            color=POS, fill="#fdecea", stroke=POS, sw=1.6))

    p.append(text(W / 2, H - 18,
                  "коротке очікування виграє спінлок; довге — мʼютекс",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "spin-vs-sleep.svg"), W, H, *p,
           title="Що робити, поки замок зайнятий")


# ── cost-ledger: де в кого витрати ────────────────────────────────────────────
# Ідея: чотири смуги. Вхід/вихід: спінлок дешевий, мʼютекс дорогий. Марнування
# процесора під час очікування: спінлок палить тим більше, чим довше; мʼютекс —
# нуль (ядро працює над іншим).

def fig_cost_ledger():
    W, H = 720, 320
    p = []
    bx = 280
    maxw = 360
    rows = [
        ("Спінлок · вхід/вихід", 0.08, FIELD, "лічені такти"),
        ("Мʼютекс · вхід/вихід", 0.55, POS, "перемикання контексту"),
        ("Спінлок · марнування при очікуванні", 0.92, POS, "палить ядро весь час"),
        ("Мʼютекс · марнування при очікуванні", 0.04, FIELD, "нуль — ядро працює над іншим"),
    ]
    y = 66
    rh = 40
    for lab, frac, col, note in rows:
        p.append(text(bx - 12, y + rh / 2 + 4, lab, size=11, color=INK, anchor="end", bold=True))
        p.append(rect(bx, y, maxw, rh, fill="#f3f3f3", stroke="#dddddd", sw=1.0))
        w = max(8, maxw * frac)
        p.append(rect(bx, y, w, rh, fill=col, stroke=col, sw=1.0))
        if w > 165:
            p.append(text(bx + 10, y + rh / 2 + 4, note, size=10, color=BG, anchor="start", bold=True))
        else:
            p.append(text(bx + w + 8, y + rh / 2 + 4, note, size=10, color=col, anchor="start"))
        y += rh + 18

    p.append(text(W / 2, H - 16,
                  "спінлок дешевий на вхід, але палить ядро; мʼютекс дорогий на вхід, та ядро не марнує",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "cost-ledger.svg"), W, H, *p,
           title="Куди подівся кошт: вхід проти очікування")


# ── decision: три питання поспіль ─────────────────────────────────────────────
# Ідея: вертикальна послідовність питань. ISR? → спінлок. Інакше: довга секція? →
# мʼютекс. Коротка → спінлок. Різні пріоритети додатково схиляють до мʼютекса.

def fig_decision():
    W, H = 720, 380
    p = []
    cx = W / 2

    q1, q1w, q1h = textbox(cx, 64, "Дані чіпає переривання (ISR)?",
                           size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=12)
    p.append(q1)

    # ТАК → спінлок (мʼютекс заборонений в ISR)
    sx = 168
    sp, spw, sph = textbox(sx, 175, "ТАК → СПІНЛОК\n(мʼютекс в ISR\nзаборонений)",
                           size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.8, pad=10)
    p.append(line(cx - q1w * 0.28, 64 + q1h / 2, sx, 175 - sph / 2, color=POS, sw=1.7))
    p.append(text((cx - q1w * 0.28 + sx) / 2 - 14, (64 + q1h / 2 + 175 - sph / 2) / 2,
                  "так", size=11, color=POS, bold=True, anchor="end"))
    p.append(sp)

    # НІ → друге питання
    q2, q2w, q2h = textbox(cx + 30, 175, "Секція довга/блокувальна?",
                           size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=11)
    p.append(line(cx + q1w * 0.22, 64 + q1h / 2, cx + 30 - q2w * 0.30, 175 - q2h / 2, color=INK, sw=1.5))
    p.append(text((cx + q1w * 0.22 + cx + 30 - q2w * 0.30) / 2 + 12,
                  (64 + q1h / 2 + 175 - q2h / 2) / 2, "ні", size=11, color=INK, bold=True, anchor="start"))
    p.append(q2)

    # друге питання → коротка=спінлок, довга=мʼютекс
    short_x = cx - 40
    sh, shw, shh = textbox(short_x, 288, "коротка →\nСПІНЛОК",
                           size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.8, pad=9)
    p.append(line(cx + 30 - q2w * 0.18, 175 + q2h / 2, short_x, 288 - shh / 2, color=POS, sw=1.6))
    p.append(sh)

    long_x = cx + 130
    lo, low, loh = textbox(long_x, 288, "довга →\nМʼЮТЕКС",
                           size=11, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.8, pad=9)
    p.append(line(cx + 30 + q2w * 0.18, 175 + q2h / 2, long_x, 288 - loh / 2, color=NEG, sw=1.6))
    p.append(lo)

    p.append(text(W / 2, H - 40,
                  "різні пріоритети задач додатково схиляють до мʼютекса (успадкування пріоритету)",
                  size=11, color=NEG))
    p.append(text(W / 2, H - 16,
                  "корінь усього — час, який доведеться тримати замок",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "decision.svg"), W, H, *p,
           title="Спінлок чи мʼютекс: три питання")


# ── dekker-to-hw: від програмного розвʼязку Деккера до апаратної інструкції ────
# Ідея для вставки hist: показати дві епохи однієї обіцянки «рівно один».
# Ліворуч — суто програмний розвʼязок Деккера (два прапорці + спільна черга,
# без заліза). Праворуч — нинішній шлях: одна неподільна інструкція процесора
# «перевір і встанови», на якій тримається спінлок.

def fig_dekker_to_hw():
    W, H = 720, 350
    p = []

    # ── ліва панель: Деккер, суто програмно ──
    lx = 40
    lw = 290
    p.append(rect(lx, 64, lw, 210, fill="#f6f4ec", stroke=INK, sw=1.6, rx=8))
    p.append(text(lx + lw / 2, 50, "Деккер · ~1959 · суто програмно",
                  size=12.5, bold=True, color=INK))

    p.append(fitbox(lx + 20, 86, 120, 46, "прапорець\n«хочу» A",
                    size=11, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(fitbox(lx + lw - 140, 86, 120, 46, "прапорець\n«хочу» B",
                    size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(fitbox(lx + 55, 150, lw - 110, 44, "спільна змінна\n«чия черга»",
                    size=11, bold=True, fill="#eef0f4", stroke=INK, sw=1.6))
    p.append(text(lx + lw / 2, 232, "лише читання/записи памʼяті",
                  size=11, color=MUTED, italic=True))
    p.append(text(lx + lw / 2, 256, "коректно, але крихко й на 2 процеси",
                  size=11, color=POS))

    # ── стрілка переходу ──
    p.append(arrow(lx + lw + 8, 169, lx + lw + 58, 169, color=INK, sw=2.4))
    p.append(text(lx + lw + 33, 150, "залізо", size=10, color=MUTED, bold=True))

    # ── права панель: апаратна неподільна інструкція ──
    rx = lx + lw + 66
    rw = W - rx - 40
    p.append(rect(rx, 64, rw, 210, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(rx + rw / 2, 50, "Прошивка сьогодні · апаратно",
                  size=12.5, bold=True, color=FIELD))

    p.append(fitbox(rx + 24, 96, rw - 48, 60,
                    "одна неподільна\nінструкція процесора", size=12, bold=True,
                    fill=BG, stroke=FIELD, sw=1.8))
    p.append(text(rx + rw / 2, 182, "«перевір і встанови»", size=12, bold=True, color=FIELD))
    p.append(text(rx + rw / 2, 206, "(test-and-set)", size=10.5, color=MUTED))
    p.append(text(rx + rw / 2, 240, "на ній тримається спінлок —", size=11, color=INK))
    p.append(text(rx + rw / 2, 258, "дешево й надійно", size=11, color=INK))

    p.append(text(W / 2, H - 16,
                  "Деккер довів, що впорядкувати МОЖНА; апаратура зробила це дешевим",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "dekker-to-hw.svg"), W, H, *p,
           title="Від програмного розвʼязку Деккера до апаратної інструкції")


# ── timeline: ідея й слово розведені в часі ──────────────────────────────────
# Ідея для вставки hist: одна горизонтальна вісь часу з п’ятьма віхами. Видно
# головне — між абстракцією (Дейкстра/Деккер, ~1959–65) і звичним словом
# «mutex» (POSIX, 1995) лежить близько тридцяти років.

def fig_timeline():
    W, H = 720, 320
    p = []

    x0, x1 = 70, W - 50
    y = 150
    t0, t1 = 1958, 1997  # межі шкали

    def X(year):
        return x0 + (x1 - x0) * (year - t0) / (t1 - t0)

    # вісь
    p.append(arrow(x0 - 10, y, x1 + 18, y, color=INK, sw=2.0))
    p.append(text(x1 + 14, y + 20, "рік", size=11, color=MUTED, italic=True))

    # дрібні поділки-десятиліття
    for yr in (1960, 1970, 1980, 1990):
        xx = X(yr)
        p.append(line(xx, y - 5, xx, y + 5, color=MUTED, sw=1.2))
        p.append(text(xx, y + 22, str(yr), size=10, color=MUTED))

    # віхи: (рік, підпис, угору?, колір)
    marks = [
        (1959, "Деккер:\nперший програмний\nрозвʼязок", True, FIELD),
        (1962, "EWD35:\nсемафор, P/V,\nвзаємне виключення", False, NEG),
        (1965, "EWD123:\nусталює мову\n(друком — 1968)", True, NEG),
        (1995, "POSIX-потоки:\nслово «mutex»\n(1003.1c)", False, POS),
    ]
    for yr, lab, up, col in marks:
        xx = X(yr)
        p.append(circle(xx, y, 6, fill=col, stroke=col, sw=1.0))
        if up:
            p.append(line(xx, y - 6, xx, y - 30, color=col, sw=1.4))
            p.append(textbox(xx, y - 58, lab, size=10, bold=True, color=col,
                             fill=BG, stroke=col, sw=1.4, pad=7)[0])
        else:
            p.append(line(xx, y + 6, xx, y + 38, color=col, sw=1.4))
            p.append(textbox(xx, y + 66, lab, size=10, bold=True, color=col,
                             fill=BG, stroke=col, sw=1.4, pad=7)[0])

    # дужка «≈30 років» між ідеєю та назвою
    ax0, ax1 = X(1962), X(1995)
    by = 38
    p.append(line(ax0, by, ax1, by, color=MUTED, sw=1.2, dash="4,4"))
    p.append(line(ax0, by, ax0, by + 8, color=MUTED, sw=1.2))
    p.append(line(ax1, by, ax1, by + 8, color=MUTED, sw=1.2))
    p.append(text((ax0 + ax1) / 2, by - 8, "≈ 30 років: ідея → звичне ім’я",
                  size=11, color=MUTED, bold=True))

    p.append(text(W / 2, H - 14,
                  "ідея — Дейкстра й Деккер (Амстердам); коротке слово «mutex» — на тридцять років молодше",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Семафор і «mutex»: ідея та назва в різні десятиліття")


if __name__ == "__main__":
    fig_spin_wait()
    fig_spin_vs_sleep()
    fig_cost_ledger()
    fig_decision()
    fig_dekker_to_hw()
    fig_timeline()
    print("OK: figures written to", OUT)
