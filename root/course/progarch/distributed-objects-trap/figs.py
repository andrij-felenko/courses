# -*- coding: utf-8 -*-
"""Фігури до кроку «Чому "distributed objects"».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ───────── Фіг. 1: реальна затримка (лог-шкала) і людський масштаб ─────────
def fig_latency_human():
    W, H = 900, 430
    f = []

    x0, axisW = 280, 540          # старт смуг і ширина 9 декад (1 нс … 1 с)
    DECADES = 9.0

    def X(lg):                    # позиція за десятковим логарифмом наносекунд
        return x0 + lg / DECADES * axisW

    rows = [
        # назва,               реальна,     людський масштаб,   ns,          колір
        ("виклик у пам'яті",   "≈ 1 нс",    "= 1 секунда",      1,           FIELD),
        ("оперативна пам'ять", "≈ 100 нс",  "≈ 1.7 хвилини",    100,         FIELD),
        ("межа в дата-центрі", "≈ 0.5 мс",  "≈ 5.8 дня",        500000,      POS),
        ("пакет через океан",  "≈ 150 мс",  "≈ 4.7 року",       150000000,   POS),
    ]
    ys = [110, 180, 250, 320]
    bh = 30

    # ── «провалля» пам'ять → мережа: смуга між 100 нс і 0.5 мс (× ~5000) ──
    bx1, bx2 = X(2.0), X(math.log10(500000))
    f.append(rect(bx1, 92, bx2 - bx1, 260, fill="#fbeeec", stroke="#f0d9d5", sw=1, rx=4))
    f.append(text((bx1 + bx2) / 2, 84, "провалля × ~5000", size=12, color=POS, bold=True))

    # ── вісь із декадними позначками (під смугами) ──
    ay = 368
    f.append(line(x0, ay, x0 + axisW, ay, color="#c8ced6", sw=1.6))
    for d, lab in [(0, "1 нс"), (3, "1 мкс"), (6, "1 мс"), (9, "1 с")]:
        x = X(d)
        f.append(line(x, ay - 5, x, ay + 5, color=MUTED, sw=1.2))
        f.append(text(x, ay + 22, lab, size=11, color=MUTED))

    # ── смуги + підписи ──
    for (name, real, human, ns, col), yc in zip(rows, ys):
        xe = X(math.log10(ns))
        w = max(10, xe - x0)                       # 1 нс → коротка позначка
        # ліворуч: назва операції + реальна затримка
        f.append(text(x0 - 24, yc - 4, name, size=13, bold=True, color=INK, anchor="end"))
        f.append(text(x0 - 24, yc + 13, real, size=11, color=MUTED, anchor="end"))
        # сама смуга
        f.append(rect(x0, yc - bh / 2, w, bh, fill=col, stroke=col, sw=1, rx=5))
        # праворуч: людський масштаб
        f.append(text(x0 + w + 12, yc + 5, human, size=14, bold=True, color=col, anchor="start"))

    render(os.path.join(IMG, "latency-human.svg"), W, H, *f,
           title="Одна операція, дві шкали: реальна затримка (лог) і людський масштаб")


# ───────── Фіг. 2: балакучий інтерфейс проти грубого ─────────
def fig_chatty_vs_coarse():
    W, H = 980, 600
    f = []
    WALL = 490

    # спільний підпис межі — у просвіті між панелями
    f.append(line(60, 305, 920, 305, color="#e5e7eb", sw=1))
    f.append(text(WALL, 300, "вертикальна пунктирна лінія = межа процесу / машини",
                  size=11, color=MUTED))

    # ── Панель А: балакучий ──
    f.append(text(300, 78, "БАЛАКУЧИЙ — багато дрібних викликів",
                  size=15, bold=True, color=POS))
    f.append(line(WALL, 95, WALL, 244, color=MUTED, sw=1.4, dash="5,6"))
    b, _, _ = textbox(210, 165, "Клієнт-дашборд\n(хмара)", size=13)
    f.append(b)
    b, _, _ = textbox(770, 165, "Реєстр\n30 × Device", size=13, fill="#eef2f6")
    f.append(b)
    # багато дрібних стрілок туди-назад крізь стіну
    ax_l, ax_r = 285, 695
    for i, yc in enumerate([105, 129, 153, 177, 201, 225]):
        if i % 2 == 0:
            f.append(arrow(ax_l, yc, ax_r, yc, color=POS, sw=1.3))
        else:
            f.append(arrow(ax_r, yc, ax_l, yc, color=POS, sw=1.3))
    f.append(text(WALL, 272, "150 переходів через межу", size=16, bold=True, color=POS))

    # ── Панель Б: грубий ──
    f.append(text(300, 350, "ГРУБИЙ — один виклик пакунком",
                  size=15, bold=True, color=FIELD))
    f.append(line(WALL, 366, WALL, 486, color=MUTED, sw=1.4, dash="5,6"))
    b, _, _ = textbox(210, 430, "Клієнт-дашборд\n(хмара)", size=13)
    f.append(b)
    b, _, _ = textbox(770, 430, "Реєстр\n30 × Device", size=13, fill="#eef2f6")
    f.append(b)
    # один похід туди, один назад із пакунком
    f.append(arrow(285, 408, 695, 408, color=FIELD, sw=2.6))
    f.append(text(372, 398, "getSnapshot()", size=12, bold=True, color=FIELD))
    f.append(arrow(695, 456, 285, 456, color=FIELD, sw=2.6))
    b, _, _ = textbox(630, 482, "30 × DeviceDTO", size=12, fill="#eafaf0", stroke=FIELD)
    f.append(b)
    f.append(text(300, 482, "1 перехід через межу", size=15, bold=True, color=FIELD))

    render(os.path.join(IMG, "chatty-vs-coarse.svg"), W, H, *f,
           title="Той самий дашборд через ту саму межу")


# ───────── Фіг. 3: розв'язка «чи є межа процесу» ─────────
def fig_dont_distribute_rule():
    W, H = 840, 540
    f = []

    # верхній вузол
    b, _, _ = textbox(420, 68, "Два об'єкти\nговорять", size=14, bold=True)
    f.append(b)
    f.append(arrow(420, 100, 420, 130, color=LINE, sw=1.8))

    # питання
    f.append(fitbox(300, 134, 240, 52, "Вони в одному процесі?",
                    size=15, fill="#fff8e8", stroke="#c9a93b", color=INK, bold=True))

    # гілки
    f.append(arrow(392, 188, 235, 298, color=FIELD, sw=2.2))
    f.append(text(300, 230, "Так", size=14, bold=True, color=FIELD))
    f.append(arrow(448, 188, 620, 298, color=POS, sw=2.2))
    f.append(text(528, 226, "Ні — світ поставив межу",
                  size=12, bold=True, color=POS, anchor="start"))

    # листки
    f.append(fitbox(110, 300, 250, 84,
                    "Лишай дрібнозернистим —\nвиклики дарові, межі нема",
                    size=13, fill="#eafaf0", stroke=FIELD, color=INK, bold=True))
    f.append(fitbox(490, 300, 260, 84,
                    "Перетинай рідко і грубо —\nодин виклик, пакунок-DTO",
                    size=13, fill="#fdecea", stroke=POS, color=INK, bold=True))

    # девіз-підсумок
    f.append(fitbox(240, 432, 360, 52, "За замовчуванням — не розподіляй",
                    size=16, fill="#f4f6f8", stroke=INK, color=INK, bold=True, sw=2.2))

    render(os.path.join(IMG, "dont-distribute-rule.svg"), W, H, *f,
           title="Розв'язка: чи є між об'єктами межа процесу")


# ───────── Фіг. 4 (для hist-вставки): злет і відступ, 1989–2006 ─────────
def fig_rise_fall_timeline():
    W, H = 1060, 470
    f = []

    # ── дві епохи як фонові зони ──
    f.append(rect(30, 92, 672, 330, fill="#f2f9f4", stroke="#e2efe7", sw=1, rx=10))
    f.append(rect(702, 92, 328, 330, fill="#fdf2f0", stroke="#f2ddd8", sw=1, rx=10))
    f.append(text(366, 118, "МРІЯ РОСТЕ — «зроби раз, розкидай усюди»",
                  size=14, bold=True, color=FIELD))
    f.append(text(866, 118, "ВІДСТУП — назад до грубих меж",
                  size=14, bold=True, color=POS))

    # ── вісь часу ──
    axisY = 262
    f.append(line(50, axisY, 1010, axisY, color=INK, sw=2.4))

    # ── межа епох: припливна хвиля обертається одразу після піку ──
    f.append(line(702, 132, 702, 398, color=MUTED, sw=1.4, dash="4,6"))
    f.append(text(702, 414, "тут приплив повертає назад",
                  size=11, color=MUTED, italic=True))
    f.append(text(645, 238, "пік мрії", size=11, bold=True, color=FIELD))

    events = [
        # i,  рік,    підпис,                    колір фази, заливка
        (0, "1989", "OMG-консорціум",        FIELD, "#eafaf0"),
        (1, "1991", "CORBA 1.0 · IDL",       FIELD, "#eafaf0"),
        (2, "1994", "«A Note…» + 7 хиб",     POS,   "#fdecea"),
        (3, "1996", "DCOM · CORBA 2.0",      FIELD, "#eafaf0"),
        (4, "1997", "Java RMI · 8-ма хиба",  FIELD, "#eafaf0"),
        (5, "1998", "EJB 1.0 · entity beans", FIELD, "#eafaf0"),
        (6, "2001", "EJB 2.0: локальні",     NEG,   "#eaf0fd"),
        (7, "2002", "1-й закон Фаулера",      NEG,   "#eaf0fd"),
        (8, "2006", "EJB 3.0 → JPA",          NEG,   "#eaf0fd"),
    ]
    for i, year, lab, col, fill in events:
        xi = 70 + 115 * i
        above = (i % 2 == 0)
        yc = 178 if above else 348
        # конектор від осі до рамки
        if above:
            f.append(line(xi, axisY - 8, xi, 205, color=col, sw=1.4))
        else:
            f.append(line(xi, axisY + 8, xi, 320, color=col, sw=1.4))
        # крапка на осі (пік 1998 — трохи більший)
        r = 8 if year == "1998" else 6
        f.append(circle(xi, axisY, r, fill=fill, stroke=col, sw=2.4))
        # рамка події
        b, _, _ = textbox(xi, yc, year + "\n" + lab, size=12,
                          color=col, fill=fill, stroke=col, bold=True, pad=9)
        f.append(b)

    render(os.path.join(IMG, "rise-fall-timeline.svg"), W, H, *f,
           title="Розподілені об'єкти: злет і відступ, 1989–2006")


# ───────── Фіг. 5 (proj-вставка): конвеєр «дрібно → грубо → дрібно» ─────────
def fig_wire_pipeline():
    W, H = 1040, 430
    f = []

    # дві стіни-межі (стартують нижче підписів-стрілок)
    for wx in (340, 690):
        f.append(line(wx, 100, wx, 338, color=MUTED, sw=1.4, dash="5,6"))
    f.append(text(340, 354, "межа", size=11, color=MUTED))
    f.append(text(690, 354, "межа", size=11, color=MUTED))

    # ── ХАБ (зелений берег) ──
    f.append(rect(40, 100, 250, 150, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(165, 128, "ХАБ", size=15, bold=True, color=INK))
    f.append(mtext(165, 160, ["Device — об'єкт", "з поведінкою", "геттери дарові"],
                   size=12, color=INK))

    # ── ДРІТ: один пакунок ──
    f.append(rect(410, 150, 210, 80, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(515, 182, "30 × DeviceDTO", size=13, bold=True, color=INK))
    f.append(text(515, 206, "1 перехід через межу", size=11, color=POS))

    # ── ХМАРА (зелений берег) ──
    f.append(rect(760, 100, 250, 150, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(885, 128, "ХМАРА", size=15, bold=True, color=INK))
    f.append(mtext(885, 160, ["CloudDevice — об'єкт", "зі своєю поведінкою",
                              "геттери знову дарові"], size=12, color=INK))

    # ── стрілки збірки й відновлення (підписи над стінами, щоб не лягали на них) ──
    f.append(arrow(290, 175, 405, 175, color=FIELD, sw=2.2))
    f.append(text(347, 90, "збірка → DTO[]", size=11, bold=True, color=FIELD))
    f.append(arrow(620, 175, 755, 175, color=FIELD, sw=2.2))
    f.append(text(688, 90, "DTO → відновлення", size=11, bold=True, color=FIELD))

    # ── девіз ──
    f.append(fitbox(370, 372, 300, 42, "DTO живе лише на дроті",
                    size=15, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))

    render(os.path.join(IMG, "wire-pipeline.svg"), W, H, *f,
           title="Дрібно на берегах, грубо на переправі")


# ───────── Фіг. 6 (proj-вставка): N+1, що переїхав за другу межу ─────────
def fig_hidden_n1():
    W, H = 940, 460
    f = []

    # межа 1 — між хмарою і хабом (звичайна); межа 2 — схована, гаряча
    f.append(line(285, 108, 285, 350, color=MUTED, sw=1.4, dash="5,6"))
    f.append(line(630, 108, 630, 350, color=POS, sw=1.6, dash="5,6"))
    f.append(text(285, 96, "межа 1", size=11, color=MUTED))
    f.append(text(630, 96, "межа 2 — схована!", size=11, bold=True, color=POS))

    # ── ХМАРА ──
    f.append(rect(40, 165, 180, 78, fill=FILL, stroke=LINE, sw=1.6))
    f.append(text(130, 198, "ХМАРА", size=13, bold=True, color=INK))
    f.append(text(130, 220, "дашборд", size=11, color=MUTED))

    # ── ХАБ ──
    f.append(rect(330, 150, 240, 110, fill=FILL, stroke=LINE, sw=1.6))
    f.append(text(450, 182, "ХАБ", size=14, bold=True, color=INK))
    f.append(text(450, 206, "snapshot()", size=13, color=INK))
    f.append(text(450, 230, "грубий назовні", size=11, color=MUTED))

    # ── ЗАЛІЗО ──
    f.append(rect(730, 130, 170, 150, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(815, 158, "фізичні пристрої", size=12, bold=True, color=INK))
    for cx in (770, 800, 830, 860):
        f.append(circle(cx, 200, 7, fill="#ffffff", stroke=POS, sw=1.4))
    f.append(text(815, 232, "× 30", size=13, bold=True, color=POS))
    f.append(text(815, 258, "читання = перехід", size=10, color=MUTED))

    # ── один грубий перехід хмара→хаб ──
    f.append(arrow(220, 203, 330, 203, color=FIELD, sw=2.4))
    f.append(text(252, 190, "1 перехід", size=11, bold=True, color=FIELD))

    # ── віяло прихованих радіо-переходів хаб→залізо ──
    for yy in (150, 178, 205, 232, 260):
        f.append(arrow(570, 205, 728, yy, color=POS, sw=1.5))
    f.append(text(675, 138, "× 30", size=12, bold=True, color=POS))

    # ── два лічильники: назовні грубо, всередині балакуче ──
    f.append(fitbox(120, 378, 250, 46, "cloud.crossings = 1",
                    size=14, fill="#eafaf0", stroke=FIELD, color=INK, bold=True, sw=2))
    f.append(fitbox(470, 378, 350, 46, "radio.reads = 30 — прихований N+1",
                    size=14, fill="#fdecea", stroke=POS, color=INK, bold=True, sw=2))

    render(os.path.join(IMG, "hidden-n1.svg"), W, H, *f,
           title="Грубий фасад, балакуче нутро: лічи кожну межу")


if __name__ == "__main__":
    fig_latency_human()
    fig_chatty_vs_coarse()
    fig_dont_distribute_rule()
    fig_rise_fall_timeline()
    fig_wire_pipeline()
    fig_hidden_n1()
    print("OK: latency-human.svg, chatty-vs-coarse.svg, dont-distribute-rule.svg, "
          "rise-fall-timeline.svg, wire-pipeline.svg, hidden-n1.svg")
