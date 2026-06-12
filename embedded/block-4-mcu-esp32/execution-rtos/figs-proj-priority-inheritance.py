# -*- coding: utf-8 -*-
"""
Фігури для вставки ch27-s6-a-priority-inheritance.md
«Успадкування пріоритету: що насправді робить м'ютекс проти інверсії пріоритетів»

  fig-4-10-6a-1-inversion-timeline.svg   — інверсія БЕЗ успадкування (бінарний семафор)
  fig-4-10-6a-2-inheritance-timeline.svg — виправлення З успадкуванням (м'ютекс)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Локальні кольори ─────────────────────────────────────────────────────────
HIGH_COL   = "#c0392b"   # Висока В — POS (червоний)
MID_COL    = "#e08b00"   # Середня С — жовто-жовтогаряча
LOW_COL    = "#2457d6"   # Низька Н  — NEG (синій)
LOCK_COL   = "#27ae60"   # Замок / ресурс — FIELD (зелений)
INH_COL    = "#9b59b6"   # Успадкований пріоритет — фіолетовий
BLOCKED_BG = "#fdecea"   # Фон «заблоковано»
RUN_ALPHA  = 0.92        # opacity (не потрібно — просто для нотаток)
LRED   = "#fdecea"
LYEL   = "#fff8e1"
LBLUE  = "#e8eef9"
LPURP  = "#f3eefa"
LGRE   = "#edf7ef"

# ── Спільна геометрія часової діаграми ───────────────────────────────────────
W, H = 960, 320
TRACK_H   = 52        # висота доріжки
TRACK_GAP = 12        # зазор між доріжками
LABEL_W   = 90        # ширина підпису зліва
AXIS_Y    = H - 40    # вісь часу (нижній підпис)
T0        = LABEL_W + 10          # початок часової осі
T_END     = W - 20                # кінець
TW        = T_END - T0            # загальна ширина
TRACK_TOP = 28                    # де починається перша доріжка


def track_y(i):
    """Y-координата верхньої межі i-ї доріжки (0=В, 1=С, 2=Н)."""
    return TRACK_TOP + i * (TRACK_H + TRACK_GAP)


# ── допоміжні функції ─────────────────────────────────────────────────────────
def run_block(tx, tw, row, fill, stroke, label=None, label_color=INK, size=11):
    """Прямокутник «задача виконується» у хронолінії."""
    y = track_y(row) + 8
    h = TRACK_H - 16
    out = rect(tx, y, tw, h, fill=fill, stroke=stroke, sw=1.6, rx=4)
    if label:
        cx = tx + tw / 2
        cy = y + h / 2 + size * 0.35
        out += text(cx, cy, label, size=size, color=label_color, anchor="middle", bold=True)
    return out


def wait_block(tx, tw, row, label="чекає замок"):
    """Смуга 'заблоковано / чекає' — штриховані краї, інший колір."""
    y = track_y(row) + 14
    h = TRACK_H - 28
    out = rect(tx, y, tw, h, fill=LRED, stroke=HIGH_COL, sw=1.2, rx=3)
    cx = tx + tw / 2
    cy = y + h / 2 + 10 * 0.35
    out += text(cx, cy, label, size=10, color=HIGH_COL, anchor="middle", italic=True)
    return out


def idle_line(tx, tw, row, color=MUTED):
    """Тонка горизонтальна лінія «задача неактивна»."""
    my = track_y(row) + TRACK_H // 2
    return line(tx, my, tx + tw, my, color=color, sw=1.2, dash="4 4")


def time_mark(tx, label, color=MUTED):
    """Вертикальна позначка на осі часу."""
    return (line(tx, TRACK_TOP, tx, AXIS_Y - 6, color=color, sw=1.0, dash="2 4") +
            text(tx, AXIS_Y + 12, label, size=10, color=color, anchor="middle"))


def lock_icon(tx, row, color=LOCK_COL, size=11):
    """Невеликий значок «🔒» — замок, що бере/дає задача."""
    cy = track_y(row) + 6
    return text(tx, cy + size, "🔒", size=size, color=color, anchor="middle")


# ── Фігура 1: Інверсія БЕЗ успадкування ─────────────────────────────────────
def fig1_inversion():
    parts = []

    # Заголовок
    parts.append(text(W / 2, 18, "Інверсія пріоритетів: бінарний семафор (без успадкування)",
                      size=15, bold=True, color=INK))

    # ── Підписи доріжок ─────────────────────────────────────────────────────
    labels = [
        ("Висока В", HIGH_COL),
        ("Середня С", MID_COL),
        ("Низька Н",  LOW_COL),
    ]
    for i, (lbl, col) in enumerate(labels):
        y = track_y(i) + TRACK_H // 2 + 5
        tb, tbw, tbh = textbox(LABEL_W / 2, track_y(i) + TRACK_H / 2,
                               lbl, size=12, fill="#f4f6f8", stroke=col, sw=1.5,
                               color=col, bold=True, min_w=78, pad=6)
        parts.append(tb)

    # ── Координати ключових подій (у відносних одиницях 0..1 від TW) ───────
    # t0=0: H починає роботу + бере замок
    # t1: H у крит. секції, В прокидається
    # t2: В блокується на замку
    # t3: С прокидається і витісняє Н (С > Н)
    # t4: С завершує (тут умовно) — Н повертається
    # t5: Н завершує крит. секцію, дає замок → В нарешті біжить
    # t6: В виконується

    def tx(frac):
        return T0 + frac * TW

    t = [tx(f) for f in [0.0, 0.12, 0.18, 0.30, 0.70, 0.76, 1.0]]
    # t[0] = старт, t[1] = H бере замок (початок крит. сек.), t[2] = В блокується
    # t[3] = С витісняє Н, t[4] = С закінчує, t[5] = Н завершує + Give, t[6] = кінець

    # ── ROW 2: Низька Н ─────────────────────────────────────────────────────
    # 0→t1: Н готується (перед критичною секцією)
    parts.append(run_block(t[0], t[1]-t[0], 2, LBLUE, LOW_COL, "Н: робота до замка", LOW_COL, 10))
    # t1→t3: Н у критичній секції (тримає замок)
    parts.append(run_block(t[1], t[3]-t[1], 2, "#c5d9f8", LOW_COL, "Н: крит. секція 🔒", LOW_COL, 10))
    # t3→t4: Н ЗУПИНЕНА — витіснена С
    parts.append(rect(t[3], track_y(2)+8, t[4]-t[3], TRACK_H-16,
                      fill="#e0e0e0", stroke="#999", sw=1.2, rx=4))
    parts.append(text((t[3]+t[4])/2, track_y(2)+TRACK_H//2+4, "Н: витіснена С", size=10, color="#555", anchor="middle"))
    # t4→t5: Н відновлюється, закінчує крит. секцію
    parts.append(run_block(t[4], t[5]-t[4], 2, "#c5d9f8", LOW_COL, "Н: дає замок 🔓", LOW_COL, 10))
    # t5→end: Н продовжує (малий залишок)
    parts.append(run_block(t[5], t[6]-t[5], 2, LBLUE, LOW_COL, "Н: далі", LOW_COL, 10))

    # ── ROW 1: Середня С ─────────────────────────────────────────────────────
    # 0→t3: С спить / не прокидалась
    parts.append(idle_line(t[0], t[3]-t[0], 1, MID_COL))
    # t3→t4: С БІГАЄ (витісняє Н)
    parts.append(run_block(t[3], t[4]-t[3], 1, LYEL, MID_COL, "С: виконується (без замка!)", MID_COL, 10))
    # t4→end: С спить
    parts.append(idle_line(t[4], t[6]-t[4], 1, MID_COL))

    # ── ROW 0: Висока В ──────────────────────────────────────────────────────
    # 0→t2: В спить
    parts.append(idle_line(t[0], t[2]-t[0], 0, HIGH_COL))
    # t2→t5: В ЗАБЛОКОВАНА чекає замку (поки тримає Н, яку витіснила С)
    parts.append(wait_block(t[2], t[5]-t[2], 0, "В: чекає замку..."))
    # t5→end: В нарешті виконується
    parts.append(run_block(t[5], t[6]-t[5], 0, LRED, HIGH_COL, "В: виконується", HIGH_COL, 10))

    # ── Позначки на осі часу ─────────────────────────────────────────────────
    marks = [
        (t[1], "Н бере\nзамок"),
        (t[2], "В проки-\nдається"),
        (t[3], "С вит-\nісняє Н"),
        (t[4], "С завер-\nшила"),
        (t[5], "Н дає\nзамок→В"),
    ]
    for tx_pos, lbl in marks:
        my = AXIS_Y - 6
        parts.append(line(tx_pos, TRACK_TOP, tx_pos, my, color=MUTED, sw=1.0, dash="3 4"))
        parts.append(mtext(tx_pos, AXIS_Y + 4, lbl.split("\n"), size=9, color=MUTED, anchor="middle"))

    # Вісь часу
    parts.append(arrow(T0, AXIS_Y, T_END, AXIS_Y, color=MUTED, sw=1.4))
    parts.append(text(T_END - 16, AXIS_Y - 8, "час", size=11, color=MUTED, anchor="end"))

    # ── Підпис аномалії: В чекає довше за С ─────────────────────────────────
    ann_cx = (t[3] + t[5]) / 2
    ann_cy = track_y(0) + TRACK_H - 4
    tb, tbw, tbh = textbox(ann_cx, ann_cy + 10,
        "В чекає стільки, скільки бігла С\n(необмежено: залежить від С, не від Н)",
        size=11, fill="#fef0f0", stroke=HIGH_COL, sw=1.8, color=HIGH_COL, pad=7, rx=6)
    # стрілка від В-блоку вниз до підпису
    parts.append(tb)
    parts.append(arrow(ann_cx, track_y(0) + TRACK_H + 2, ann_cx, ann_cy + 2, color=HIGH_COL, sw=1.4))

    path = os.path.join(OUT, "fig-4-10-6a-1-inversion-timeline.svg")
    render(path, W, H, *parts)
    print("wrote fig-4-10-6a-1-inversion-timeline.svg")


# ── Фігура 2: Виправлення З успадкуванням (м'ютекс) ─────────────────────────
def fig2_inheritance():
    parts = []

    parts.append(text(W / 2, 18, "Успадкування пріоритету: м'ютекс (інверсії немає)",
                      size=15, bold=True, color=INK))

    # Підписи доріжок
    for i, (lbl, col) in enumerate([("Висока В", HIGH_COL), ("Середня С", MID_COL), ("Низька Н", LOW_COL)]):
        tb, tbw, tbh = textbox(LABEL_W / 2, track_y(i) + TRACK_H / 2,
                               lbl, size=12, fill="#f4f6f8", stroke=col, sw=1.5,
                               color=col, bold=True, min_w=78, pad=6)
        parts.append(tb)

    def tx(frac):
        return T0 + frac * TW

    # Тепер: Н не встигає бути витіснена — бо її пріоритет піднято до В
    # t0: старт
    # t1: H бере замок м'ютекс
    # t2: В прокидається, блокується → ядро піднімає Н до рівня В
    # t3: Н ШВИДКО завершує крит. секцію (С не встигла витіснити)
    #     На Give: Н повертає пріоритет, В отримує замок
    # t4: В виконується
    # t5: Н продовжує (вже з низьким пріоритетом)
    # t6: кінець (С не отримувала керування в цей критичний відрізок)

    t = [tx(f) for f in [0.0, 0.12, 0.22, 0.42, 0.44, 1.0]]

    # ── ROW 2: Низька Н ─────────────────────────────────────────────────────
    # 0→t1: Н до замка
    parts.append(run_block(t[0], t[1]-t[0], 2, LBLUE, LOW_COL, "Н: робота до замка", LOW_COL, 10))
    # t1→t2: Н у крит. секції (пріоритет ще низький)
    parts.append(run_block(t[1], t[2]-t[1], 2, "#c5d9f8", LOW_COL, "Н: крит. сек. 🔒", LOW_COL, 10))
    # t2→t3: Н у крит. секції з ПІДВИЩЕНИМ пріоритетом (успадкування)
    parts.append(run_block(t[2], t[3]-t[2], 2, LPURP, INH_COL,
                           "Н: крит. сек. 🔒 (prio↑ = В)", INH_COL, 10))
    # t3→t4: Н дає замок (Give) — одразу переходить замок до В
    parts.append(run_block(t[3], t[4]-t[3], 2, "#e0fce4", LOCK_COL, "Н дає 🔓→В", LOCK_COL, 9))
    # t4→end: Н продовжує з низьким пріоритетом
    parts.append(run_block(t[4], t[5]-t[4], 2, LBLUE, LOW_COL, "Н: далі (prio↓ = Н)", LOW_COL, 10))

    # ── ROW 1: Середня С ─────────────────────────────────────────────────────
    # 0→t2: С спить
    parts.append(idle_line(t[0], t[2]-t[0], 1, MID_COL))
    # t2→t4: С ХОТІЛА б витіснити Н, але Н тепер «висока» → С чекає
    parts.append(rect(t[2], track_y(1)+14, t[4]-t[2], TRACK_H-28,
                      fill=LYEL, stroke=MID_COL, sw=1.1, rx=3))
    parts.append(text((t[2]+t[4])/2, track_y(1)+TRACK_H//2+4,
                      "С: не може витіснити Н (prio Н = В)", size=10, color=MID_COL,
                      anchor="middle", italic=True))
    # t4→end: С виконується
    parts.append(run_block(t[4], t[5]-t[4], 1, LYEL, MID_COL, "С: виконується", MID_COL, 10))

    # ── ROW 0: Висока В ──────────────────────────────────────────────────────
    # 0→t2: В спить
    parts.append(idle_line(t[0], t[2]-t[0], 0, HIGH_COL))
    # t2→t3: В ЧЕКАЄ — але лише доки Н в крит. секції (коротко!)
    parts.append(wait_block(t[2], t[3]-t[2], 0, "В: чекає (тільки крит. секцію Н)"))
    # t3→end: В виконується одразу після Give
    parts.append(run_block(t[3], t[5]-t[3], 0, LRED, HIGH_COL, "В: виконується", HIGH_COL, 10))

    # ── Стрілка підйому пріоритету Н ─────────────────────────────────────────
    arrow_x = t[2] + 14
    arrow_y_from = track_y(2) + TRACK_H - 4
    arrow_y_to   = track_y(2) + 10
    parts.append(arrow(arrow_x, arrow_y_from, arrow_x, arrow_y_to, color=INH_COL, sw=2.2))
    tb2, tw2, th2 = textbox(arrow_x + 70, track_y(2) + 20,
        "prio Н ↑ до В\n(успадкування)", size=10, fill=LPURP, stroke=INH_COL,
        sw=1.5, color=INH_COL, pad=5, rx=5)
    parts.append(tb2)

    # ── Позначки ─────────────────────────────────────────────────────────────
    marks = [
        (t[1], "Н бере\nм'ютекс"),
        (t[2], "В проки-\nдається\n→ prio Н↑"),
        (t[3], "Н дає замок\n→ В отримує\nprio Н↓"),
        (t[4], "В+Н"),
    ]
    for tx_pos, lbl in marks:
        my = AXIS_Y - 6
        parts.append(line(tx_pos, TRACK_TOP, tx_pos, my, color=MUTED, sw=1.0, dash="3 4"))
        parts.append(mtext(tx_pos, AXIS_Y + 3, lbl.split("\n"), size=9, color=MUTED, anchor="middle"))

    # Вісь часу
    parts.append(arrow(T0, AXIS_Y, T_END, AXIS_Y, color=MUTED, sw=1.4))
    parts.append(text(T_END - 16, AXIS_Y - 8, "час", size=11, color=MUTED, anchor="end"))

    # ── Підпис успіху ────────────────────────────────────────────────────────
    ann_cx = (t[2] + t[3]) / 2
    ann_cy = track_y(0) + TRACK_H - 2
    tb3, tbw3, tbh3 = textbox(ann_cx, ann_cy + 14,
        "В чекала лише тривалість крит. секції Н\n(обмежено та коротко — інверсії немає!)",
        size=11, fill="#edf7ef", stroke=LOCK_COL, sw=1.8, color=LOCK_COL, pad=7, rx=6)
    parts.append(tb3)
    parts.append(arrow(ann_cx, track_y(0) + TRACK_H + 2, ann_cx, ann_cy + 2, color=LOCK_COL, sw=1.4))

    path = os.path.join(OUT, "fig-4-10-6a-2-inheritance-timeline.svg")
    render(path, W, H, *parts)
    print("wrote fig-4-10-6a-2-inheritance-timeline.svg")


if __name__ == "__main__":
    fig1_inversion()
    fig2_inheritance()
