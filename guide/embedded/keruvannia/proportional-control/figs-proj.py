# -*- coding: utf-8 -*-
# Фігури вставки proj-p-controller-firmware. Окремий файл, щоб не чіпати
# наявні figs.py / figs-d.py цієї теми.
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорові наконечники (svgkit дає лише нейтральний #arrow).
COL_MARKERS = (
    '<defs>'
    '<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '</defs>' % (NEG, FIELD, POS)
)


def carrow(x1, y1, x2, y2, color, mid, sw=2.0):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arr%s)" stroke-linecap="round"/>'
            % (x1, y1, x2, y2, color, sw, mid))


# ── p-struct: дані одного контуру (налаштування + діагностика) ────────────────
def fig_p_struct():
    W, H = 720, 470
    p = [COL_MARKERS]
    p.append(text(W / 2, 50, "усе, що визначає один P-контур, — в одній структурі",
                  size=13, color=MUTED))
    # рамка налаштувань
    p.append(rect(90, 76, 540, 232, fill="#eef6ff", stroke=NEG, sw=1.9, rx=12))
    p.append(text(112, 100, "НАЛАШТУВАННЯ — задати один раз", size=13.5, color=NEG, anchor="start", bold=True))
    cfg = [
        ("kp", "коефіцієнт [одиниць виходу / одиницю помилки]"),
        ("beta", "вага завдання: 1 = P-на-помилці · 0 = P-на-вимірі"),
        ("u_min · u_max", "реальні межі виконавчого органу"),
        ("u_bias", "відома наперед поправка (живлення наперед)"),
    ]
    yy = 132
    for name, desc in cfg:
        p.append(rect(108, yy, 504, 38, fill=BG, stroke="#a9c2f2", sw=1.2, rx=8))
        p.append(text(124, yy + 24, name, size=12.5, color=INK, anchor="start", bold=True))
        p.append(text(300, yy + 24, desc, size=11, color=MUTED, anchor="start"))
        yy += 44
    # вузьке вікно діагностики
    p.append(rect(90, 322, 540, 84, fill="#f4f4f5", stroke=INK, sw=1.7, rx=12))
    p.append(text(112, 346, "ДІАГНОСТИКА — модуль оновлює щотакту", size=12.5, color=INK, anchor="start", bold=True))
    p.append(rect(108, 358, 244, 36, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(124, 381, "last_u", size=12, color=INK, anchor="start", bold=True))
    p.append(text(210, 381, "сирий вплив", size=10.5, color=MUTED, anchor="start"))
    p.append(rect(368, 358, 244, 36, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(384, 381, "saturated", size=12, color=POS, anchor="start", bold=True))
    p.append(text(486, 381, "уперся в межу?", size=10.5, color=MUTED, anchor="start"))
    p.append(carrow(360, 314, 360, 320, MUTED, "B", sw=1.6))
    p.append(text(W / 2, 448,
                  "Стан окремо від логіки: налаштування незмінні, діагностику видно в телеметрії — і скільки завгодно незалежних осей на одному коді.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "p-struct.svg"), W, H, *p,
           title="Один P-контур як структура: налаштування + діагностика")


# ── p-step-flow: потік даних одного виклику p_step ────────────────────────────
def fig_p_step_flow():
    W, H = 980, 380
    p = [COL_MARKERS]
    p.append(text(W / 2, 50, "один такт: зважити завдання → помножити на Kp → додати bias → ОБМЕЖИТИ останнім",
                  size=13, color=MUTED))
    ymid = 176
    h = 70
    # входи
    p.append(rect(30, ymid - 46, 118, 40, fill="#eef6ff", stroke=NEG, sw=1.6, rx=9))
    p.append(text(89, ymid - 21, "завдання r", size=11.5, color=NEG, bold=True))
    p.append(rect(30, ymid + 6, 118, 40, fill="#eef6ff", stroke=NEG, sw=1.6, rx=9))
    p.append(text(89, ymid + 31, "вимір y", size=11.5, color=NEG, bold=True))

    # блоки конвеєра
    blocks = [
        (176, "β·r − y", "зважена\nпомилка", "#f4f4f5", INK),
        (356, "× Kp", "пропорційна\nдія", "#eafaef", FIELD),
        (520, "+ u_bias", "живлення\nнаперед", "#fff5e6", "#d98a00"),
        (690, "clamp\nu_min..u_max", "ОБМЕЖИТИ", "#fdecea", POS),
    ]
    cx = []
    for x, big, sub, fill, col in blocks:
        w = 128
        p.append(rect(x, ymid - h / 2, w, h, fill=fill, stroke=col, sw=1.8, rx=11))
        p.append(mtext(x + w / 2, ymid - 6, big.split("\n"), size=13, color=col, bold=True))
        p.append(mtext(x + w / 2, ymid + 20, sub.split("\n"), size=9.5, color=MUTED))
        cx.append((x, x + w))
    # стрілки між блоками
    p.append(arrow(148, ymid - 26, 174, ymid - 8, color=INK, sw=1.8))
    p.append(arrow(148, ymid + 26, 174, ymid + 8, color=INK, sw=1.8))
    for i in range(len(blocks) - 1):
        p.append(arrow(cx[i][1], ymid, cx[i + 1][0] - 2, ymid, color=INK, sw=2.0))
    # вихід
    p.append(carrow(cx[-1][1], ymid, cx[-1][1] + 44, ymid, FIELD, "G", sw=2.4))
    p.append(rect(cx[-1][1] + 46, ymid - 20, 108, 40, fill="#eafaef", stroke=FIELD, sw=1.7, rx=9))
    p.append(text(cx[-1][1] + 100, ymid + 5, "→ драйвер", size=11.5, color=FIELD, bold=True))
    # відгалуження діагностики (до обмеження)
    dx = (cx[2][1] + cx[3][0]) / 2
    p.append(line(dx, ymid, dx, ymid + 74, color=MUTED, sw=1.4, dash="4 3"))
    p.append(rect(dx - 118, ymid + 74, 236, 40, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(dx, ymid + 92, "last_u (сирий) · saturated", size=11, color=MUTED))
    p.append(text(dx, ymid + 108, "діагностика — знімається ДО обмеження", size=9.5, color=MUTED))
    p.append(text(W / 2, 362,
                  "Обмеження бачить ВЕСЬ вплив разом із bias і стоїть останнім; β всередині множення перемикає P-на-помилці ↔ P-на-вимірі без жодної гілки.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "p-step-flow.svg"), W, H, *p,
           title="Один виклик p_step: конвеєр від виміру до обмеженого впливу")


# ── fixed-overflow: 32-бітне множення загортається, 64-бітне — ні ─────────────
def fig_fixed_overflow():
    W, H = 940, 470
    p = [COL_MARKERS]
    p.append(text(W / 2, 50,
                  "kp_q · e за великої помилки перестрибує межу 32-біт і обертає вплив на протилежний",
                  size=13, color=MUTED))
    x0, x1 = 80.0, 860.0
    # ── верхня вісь: 32-бітне знакове ─────────────────────────────────────────
    ay = 150.0
    p.append(line(x0, ay, x1, ay, color=INK, sw=2.0))
    p.append(text(x0, ay - 40, "32-бітний знаковий проміжок", size=12.5, color=INK, anchor="start", bold=True))
    # позначки меж
    xmax = x0 + (x1 - x0) * 0.72       # +2.147 млрд
    p.append(line(xmax, ay - 10, xmax, ay + 10, color=POS, sw=2.0))
    p.append(text(xmax, ay - 16, "+2.147 млрд (межа)", size=10.5, color=POS))
    p.append(text(x0, ay + 24, "0", size=10.5, color=MUTED, anchor="start"))
    # зона переповнення
    p.append(rect(xmax, ay - 6, x1 - xmax, 12, fill="#fbe3df", stroke="none", sw=0))
    p.append(text((xmax + x1) / 2, ay + 26, "тут результат ЗАГОРТАЄТЬСЯ", size=10.5, color=POS))
    # справжній добуток «хоче» сюди — за межу
    xwant = x0 + (x1 - x0) * 0.90
    p.append(carrow(x0 + 40, ay - 62, xwant, ay - 12, NEG, "B", sw=2.2))
    p.append(text(x0 + 40, ay - 68, "kp_q·e росте з помилкою →", size=11, color=NEG, anchor="start"))
    p.append(circle(xwant, ay, 6, fill=NEG, stroke=INK, sw=1.3))
    p.append(text(xwant, ay + 40, "хоче сюди", size=10, color=NEG))
    # куди насправді падає (загорнуте у від'ємне)
    xland = x0 + (x1 - x0) * 0.16
    p.append(circle(xland, ay, 7, fill=POS, stroke=INK, sw=1.4))
    p.append(line(xwant, ay + 8, xland, ay + 8, color=POS, sw=1.2, dash="4 3"))
    p.append(carrow((xwant + xland) / 2, ay + 8, xland + 4, ay + 4, POS, "R", sw=1.6))
    p.append(text(xland, ay - 16, "падає СЮДИ (від'ємне!)", size=10.5, color=POS))
    p.append(text(xland - 40, ay + 40, "вплив уперед → різкий ривок назад", size=10, color=POS, anchor="start"))

    # ── нижня вісь: 64-бітний проміжок ────────────────────────────────────────
    by = 320.0
    p.append(line(x0, by, x1, by, color=INK, sw=2.0))
    p.append(text(x0, by - 24, "64-бітний проміжок (int64_t)", size=12.5, color=FIELD, anchor="start", bold=True))
    p.append(rect(x0, by - 6, x1 - x0, 12, fill="#e5f6ec", stroke="none", sw=0))
    xok = x0 + (x1 - x0) * 0.30       # той самий добуток — легко вміщається
    p.append(circle(xok, by, 7, fill=FIELD, stroke=INK, sw=1.4))
    p.append(text(xok, by - 14, "той самий добуток — вміщається", size=10.5, color=FIELD))
    p.append(carrow(xok, by + 8, xok - 150, by + 40, FIELD, "G", sw=1.8))
    p.append(text(xok - 156, by + 56, ">> QBITS після ділення на масштаб → мале число → назад у 32 біти",
                  size=10.5, color=FIELD, anchor="start"))
    p.append(text(x1, by + 24, "величезний запас", size=10.5, color=MUTED, anchor="end"))

    p.append(text(W / 2, 452,
                  "Ліки: приведення (int64_t) на ОПЕРАНДАХ до множення, не на результаті; +пів масштабу для округлення, тоді зсув назад.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "fixed-overflow.svg"), W, H, *p,
           title="Пастка фіксованої коми: множення переповнює 32 біти")


if __name__ == "__main__":
    fig_p_struct()
    fig_p_step_flow()
    fig_fixed_overflow()
    print("OK: proj figures written to", OUT)
