# -*- coding: utf-8 -*-
"""Фігури до кроку «Fallback і деградація виклику».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER   = "#b8860b"   # бурштиновий — «прийнятно, але з допуском»
AMBERBG = "#fff8e8"
AMBERST = "#c9a93b"
REDBG   = "#fdecea"
GREENBG = "#eafaf0"
GREY    = "#e5e7eb"


# ───────── Фіг. 1: драбина відповідей fallback ─────────
def fig_fallback_ladder():
    W, H = 1080, 476
    f = []

    # ліва вісь «краще ↑ / гірше ↓»
    f.append(line(94, 92, 94, 448, color=MUTED, sw=1.2))
    f.append(text(64, 80, "↑ більше користі, менша брехня", size=12,
                  color=FIELD, bold=True, anchor="start"))
    f.append(text(64, 468, "↓ ближче до повної відмови", size=12,
                  color=POS, bold=True, anchor="start"))

    # cx-name  назва щабля                          приклад праворуч          fill,     stroke,  колір
    rungs = [
        ("① Свіжа справжня відповідь",       "залежність жива — деградації не треба",     GREENBG, FIELD,   FIELD),
        ("② Кешований останній добрий стан", "твін показує температуру, яку бачив 2 хв тому", GREENBG, FIELD, FIELD),
        ("③ Розумний дефолт",                "рекомендації мовчать → загальні хіти",       AMBERBG, AMBERST, INK),
        ("④ Функція вимкнена, сервіс живий", "кнопку сіро, віджет сховано — решта працює", AMBERBG, AMBERST, INK),
        ("⑤ Чесна вузька помилка",           "падає лише зламаний блок, не вся сторінка",  REDBG,   POS,     INK),
        ("⑥ Уся сторінка вмирає",            "катастрофа, якої уникаємо",                  REDBG,   POS,     POS),
    ]
    y, step = 90, 60
    for name, ex, fill, stroke, col in rungs:
        f.append(fitbox(110, y, 440, 52, name, size=15,
                        fill=fill, stroke=stroke, color=col, bold=True, sw=1.8))
        f.append(text(580, y + 31, ex, size=13, color=MUTED, anchor="start"))
        y += step

    render(os.path.join(IMG, "fallback-ladder.svg"), W, H, *f,
           title="Драбина відповідей: що віддати, коли залежність замовкла")


# ───────── Фіг. 2: та сама тиша — протилежний fallback ─────────
def fig_lie_safety():
    W, H = 1040, 432
    f = []

    # верхня подія
    f.append(fitbox(380, 52, 280, 52, "Хмара мовчить\n(таймаут / запобіжник розімкнено)",
                    size=13, fill=AMBERBG, stroke=AMBERST, color=INK, bold=True, sw=1.8))

    # роздільник колонок
    f.append(line(520, 132, 520, 322, color=GREY, sw=1))

    # дві гілки
    f.append(arrow(468, 106, 300, 148, color=FIELD, sw=2))
    f.append(arrow(572, 106, 740, 148, color=POS, sw=2))

    # ── ЛІВА колонка: читання (безпечно) ──
    f.append(fitbox(90, 150, 320, 50, "Читання: показати температуру", size=13,
                    fill=BG, stroke=FIELD, color=FIELD, bold=True, sw=1.8))
    f.append(text(250, 228, "допуск: застаріле на 2 хв — байдуже", size=12, color=MUTED))
    f.append(fitbox(90, 246, 320, 64, "Fallback: кеш останнього стану\n— безпечно", size=13,
                    fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=1.8))

    # ── ПРАВА колонка: дія (небезпечно) ──
    f.append(fitbox(630, 150, 320, 50, "Дія: відчинити замок", size=13,
                    fill=BG, stroke=POS, color=POS, bold=True, sw=1.8))
    f.append(text(790, 228, "допуск: застаріле «дозволено» — небезпечно", size=12, color=MUTED))
    f.append(fitbox(630, 246, 320, 64, "Наосліп кеш НЕ можна →\nfail-closed або LAN-режим", size=13,
                    fill=REDBG, stroke=POS, color=POS, bold=True, sw=1.8))

    # нижній банер
    f.append(fitbox(70, 344, 900, 52,
                    "Та сама тиша. Що віддати — вирішує не збій, а що робить із відповіддю той, хто питає.",
                    size=14, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))

    render(os.path.join(IMG, "lie-safety.svg"), W, H, *f,
           title="Один збій, два виклики — протилежний fallback")


# ───────── Фіг. 3: brownout проти blackout ─────────
def fig_brownout():
    W, H = 1040, 432
    f = []

    f.append(line(520, 58, 520, 404, color=GREY, sw=1))

    def panel(cx, x0, heading, hcol, chips, banner, bcol, bfill, bstroke):
        g = [text(cx, 66, heading, size=14, bold=True, color=hcol)]
        g.append(fitbox(cx - 120, 82, 240, 34, "навантаження ↑ пік", size=12,
                        fill=AMBERBG, stroke=AMBERST, color=INK, bold=True))
        yy = 132
        for lab, col, fill, stroke in chips:
            g.append(fitbox(x0, yy, 360, 34, lab, size=12,
                            fill=fill, stroke=stroke, color=col, bold=True, sw=1.6))
            yy += 44
        g.append(fitbox(x0, 358, 360, 44, banner, size=14,
                        fill=bfill, stroke=bstroke, color=bcol, bold=True, sw=2))
        return g

    left = [
        ("відео-перекодування · повільно", POS, REDBG, POS),
        ("схожі доми · повільно",          POS, REDBG, POS),
        ("presence · повільно",            POS, REDBG, POS),
        ("команда: відчинити двері · повільно", POS, REDBG, POS),
        ("камера · повільно",              POS, REDBG, POS),
    ]
    right = [
        ("відео-перекодування ✕ вимкнено", MUTED, FILL,    MUTED),
        ("схожі доми ✕ вимкнено",          MUTED, FILL,    MUTED),
        ("presence · швидко",              FIELD, GREENBG, FIELD),
        ("команда: відчинити двері · швидко", FIELD, GREENBG, FIELD),
        ("камера · швидко",                FIELD, GREENBG, FIELD),
    ]
    f += panel(270, 90, "Без плану: усе рівноцінне під піком", POS, left,
               "усе конкурує → каскад → лягло", POS, REDBG, POS)
    f += panel(770, 590, "Brownout: гасимо зайве навмисно", FIELD, right,
               "ядро живе й швидке", FIELD, GREENBG, FIELD)

    render(os.path.join(IMG, "brownout.svg"), W, H, *f,
           title="Свідома деградація: погасити зайве, щоб ядро жило")


# ───────── Фіг. 4: потік обгортки withFallback (для вставки proj) ─────────
def fig_withfallback_flow():
    W, H = 1160, 556
    f = []

    # вхідна рамка
    f.append(fitbox(110, 56, 640, 40, "будь-який виклик → withFallback(key, policy, primary())",
                    size=14, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))

    # чотири щаблі: умова ліворуч → кольоровий бейдж-результат праворуч
    rows = [
        ("primary() — жива відповідь\n(таймаут/запобіжник усередині)",
         "① primary() успіх\nrung=live", GREENBG, FIELD, FIELD),
        ("залежність мовчить?\nкеш свіжіший за staleBudget?",
         "② кеш ≤ staleBudget\nrung=cache · stale", GREENBG, FIELD, FIELD),
        ("кеш не дав?\nє розумний дефолт?",
         "③ smartDefault\nrung=default", AMBERBG, AMBERST, INK),
        ("дефолту нема?\nчесно зізнатись «недоступно»",
         "④ throw Unavailable\nrung=unavailable", REDBG, POS, POS),
    ]
    descend = ["↓ dependency down (не баг!)",
               "↓ кешу нема / прострочений",
               "↓ дефолту не передбачено"]
    y, step, ch = 116, 102, 58
    for i, (cond, badge, bg, st, col) in enumerate(rows):
        f.append(fitbox(110, y, 360, ch, cond, size=14,
                        fill=BG, stroke=MUTED, color=INK, sw=1.4))
        f.append(arrow(474, y + ch / 2, 496, y + ch / 2, color=MUTED, sw=1.8))
        f.append(fitbox(500, y, 250, ch, badge, size=14,
                        fill=bg, stroke=st, color=col, bold=True, sw=1.8))
        if i < len(rows) - 1:                          # спуск між щаблями
            f.append(arrow(140, y + ch, 140, y + step, color=MUTED, sw=1.8))
            f.append(text(320, y + ch + 28, descend[i], size=12, color=MUTED))
        y += step

    # виноска про політику — праворуч на всю висоту
    f.append(rect(790, 116, 340, 364, fill=BG, stroke=MUTED, sw=1.4))
    f.append(text(960, 150, "policy вмикає щаблі", size=14, bold=True, color=INK))
    f.append(line(812, 162, 1108, 162, color=GREY, sw=1))
    f.append(mtext(812, 192, [
        "read:",
        "   cache + чесна відмова",
        "   (дефолту нема)",
        "",
        "ґейт (так / ні):",
        "   без кешу,",
        "   дефолт = fail-closed",
        "",
        "той самий механізм —",
        "різні дані.",
    ], size=13, color=FIELD, anchor="start", lh=1.4))

    # нижній банер
    f.append(fitbox(110, 500, 640, 40,
                    "recordRung на КОЖНОМУ виході — навіть live: без знаменника деградацію не побачиш",
                    size=13, fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=2))

    render(os.path.join(IMG, "withfallback-flow.svg"), W, H, *f,
           title="withFallback: драбина в даних, метрика на кожному виході")


# ───────── Фіг. 5: тест, що навмисне вимикає залежність (для вставки proj) ─────────
def fig_outage_test_matrix():
    W, H = 1160, 388
    f = []

    cols = [(30, 300), (335, 195), (535, 250), (790, 340)]
    heads = ["Сценарій", "Впорснутий збій", "Очікуваний щабель", "Що НЕ сталося"]

    # шапка
    hy, hh = 46, 42
    for (x, w), htext in zip(cols, heads):
        f.append(fitbox(x, hy, w, hh, htext, size=14,
                        fill=FILL, stroke=INK, color=INK, bold=True, sw=1.6))

    # рядки: c1, c2, c3(colored), c4 ; (bg3, st3, col3) — колір щабля
    rows = [
        ("readState ·\nкеш свіжий (≤ бюджет)", "залежність\ndown",
         "rung=cache\nstale=true", "не впав;\nне віддав прострочене", GREENBG, FIELD, FIELD),
        ("readState ·\nкеш прострочений (> бюджет)", "залежність\ndown",
         "throw Unavailable\nrung=unavailable", "НЕ збрехав\nстарим кешем", REDBG, POS, POS),
        ("canCommand:unlock ·\nfail-closed · без кешу", "залежність\ndown",
         "allowed=false\nrung=default", "НЕ fail-open;\nкеш не чіпав", AMBERBG, AMBERST, INK),
        ("readState ·\nзалежність ЖИВА (контроль)", "—",
         "rung=live\nкеш прогрітий", "видно live у метриці\n(знаменник)", GREENBG, FIELD, FIELD),
    ]
    y, rh, step = 96, 64, 70
    for c1, c2, c3, c4, bg3, st3, col3 in rows:
        (x1, w1), (x2, w2), (x3, w3), (x4, w4) = cols
        f.append(fitbox(x1, y, w1, rh, c1, size=13, fill=BG, stroke=MUTED, color=INK, sw=1.2))
        f.append(fitbox(x2, y, w2, rh, c2, size=13, fill=BG, stroke=MUTED, color=MUTED, sw=1.2))
        f.append(fitbox(x3, y, w3, rh, c3, size=13, fill=bg3, stroke=st3, color=col3, bold=True, sw=1.6))
        f.append(fitbox(x4, y, w4, rh, c4, size=13, fill=BG, stroke=MUTED, color=INK, sw=1.2))
        y += step

    render(os.path.join(IMG, "outage-test-matrix.svg"), W, H, *f,
           title="Тест навмисного збою: перевіряємо ЩАБЕЛЬ, не лише «встояло»")


# ───────── Фіг. 6 (вставка hist): родовід деградації — стрілка перевертається ─────────
def fig_hist_lineage():
    W, H = 1120, 566
    f = []

    # ── часова вісь із реперами ──
    ax_y = 96
    f.append(line(80, ax_y, 1040, ax_y, color=MUTED, sw=1.4))
    reps = [
        (120, "1956", "фон Нейман"),
        (250, "1967", "«fault-tolerant»"),
        (352, "1971", "FTCS-1"),
        (600, "2003", "prog. enhancement"),
        (820, "2012", "Hystrix"),
        (985, "2018", "адаптивні ліміти"),
    ]
    for x, yr, tag in reps:
        f.append(line(x, ax_y - 6, x, ax_y + 6, color=MUTED, sw=1.4))
        f.append(text(x, ax_y - 14, tag, size=10.5, color=MUTED))
        f.append(text(x, ax_y + 26, yr, size=13, color=INK, bold=True))

    # ── роздільники панелей ──
    f.append(line(424, 150, 424, 470, color=GREY, sw=1))
    f.append(line(700, 150, 700, 470, color=GREY, sw=1))

    def era(x0, x1, head, arrow_dir, arrow_col, mid, note, mid_fill):
        """Панель-епоха: заголовок, велика стрілка напряму деградації, підпис, нота."""
        g = []
        g.append(fitbox(x0, 156, x1 - x0, 46, head, size=13,
                        fill=FILL, stroke=INK, color=INK, bold=True, sw=1.6))
        ax = x0 + 46                      # вісь стрілки — ліворуч у панелі
        if arrow_dir == "down":
            g.append(arrow(ax, 222, ax, 372, color=arrow_col, sw=4))
        else:
            g.append(arrow(ax, 372, ax, 222, color=arrow_col, sw=4))
        g.append(fitbox(x0 + 84, 250, x1 - x0 - 96, 64, mid, size=12.5,
                        fill=mid_fill, stroke=arrow_col, color=INK, bold=True, sw=1.8))
        g.append(fitbox(x0, 392, x1 - x0, 62, note, size=12,
                        fill=BG, stroke=MUTED, color=MUTED, sw=1.2))
        return g

    f += era(84, 420, "Відмовостійкі обчислення\nкосмос · авіоніка", "down", POS,
             "падаєш із ПОВНОГО\nfail-soft · graceful degradation", REDBG,
             "почни цілим → втрать вузол →\nпрацюй меншим  (драбина вниз)")
    f += era(430, 694, "Вебдизайн\nбраузери", "up", FIELD,
             "лізеш із МІНІМУМУ\nprogressive enhancement", GREENBG,
             "почни базовим → додавай,\nде браузер тягне  (вгору)")
    f += era(706, 1038, "Розподілені сервіси\nHystrix → адаптивні", "down", POS,
             "знову падаєш із ПОВНОГО\nfallback · getFallback()", REDBG,
             "справжня відповідь щойно була →\nвіддай кеш / дефолт  (драбина вниз)")

    # ── нижній банер-теза ──
    f.append(fitbox(84, 486, 954, 54,
                    "Та сама форма — «служи корисним, утративши частину». "
                    "Напрям деградації перевертається у вебі й вертається на сервері.",
                    size=14, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))

    render(os.path.join(IMG, "degradation-lineage.svg"), W, H, *f,
           title="Родовід деградації: напрям стрілки перевертається — і вертається")


if __name__ == "__main__":
    fig_fallback_ladder()
    fig_lie_safety()
    fig_brownout()
    fig_withfallback_flow()
    fig_outage_test_matrix()
    fig_hist_lineage()
    print("OK: fallback-ladder.svg, lie-safety.svg, brownout.svg, "
          "withfallback-flow.svg, outage-test-matrix.svg, degradation-lineage.svg")
