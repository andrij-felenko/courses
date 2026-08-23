# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def ir_link():
    """Одна ІЧ-лінія, дві половини: KY-005 (передавач) мигтить несучою 38 кГц,
    повітряний проміжок, KY-022 (приймач) знімає несучу й віддає чисту логіку."""
    W, H = 860, 420
    parts = []

    # ── Лівий бік: передавач KY-005 ─────────────────────────────────────
    tbx, tby, tbw, tbh = 40, 150, 190, 150
    parts.append(rect(tbx, tby, tbw, tbh, fill="#fbfcfd", stroke=INK, sw=1.6, rx=10))
    parts.append(text(tbx + tbw / 2, tby - 14, "KY-005", size=15, color=INK, bold=True))
    parts.append(text(tbx + tbw / 2, tby - 0 + 22, "передавач", size=12, color=MUTED))
    parts.append(text(tbx + tbw / 2, tby + 40, "ІЧ-світлодіод", size=11, color=INK))
    parts.append(text(tbx + tbw / 2, tby + 58, "940 нм", size=11, color=MUTED))
    # маленький символ світлодіода в модулі
    lx, ly = tbx + tbw / 2, tby + 96
    parts.append('<path d="M%.0f,%.0f L%.0f,%.0f L%.0f,%.0f z" fill="#fdecea" stroke="%s" stroke-width="1.8"/>'
                 % (lx - 14, ly - 12, lx - 14, ly + 12, lx + 8, ly, POS))
    parts.append(line(lx + 8, ly - 12, lx + 8, ly + 12, color=POS, sw=2.2))

    # ── Правий бік: приймач KY-022 ──────────────────────────────────────
    rbx, rby, rbw, rbh = 630, 150, 190, 150
    parts.append(rect(rbx, rby, rbw, rbh, fill="#fbfcfd", stroke=INK, sw=1.6, rx=10))
    parts.append(text(rbx + rbw / 2, rby - 14, "KY-022", size=15, color=INK, bold=True))
    parts.append(text(rbx + rbw / 2, rby + 22, "приймач", size=12, color=MUTED))
    parts.append(text(rbx + rbw / 2, rby + 44, "чип 1838", size=11, color=INK))
    parts.append(text(rbx + rbw / 2, rby + 62, "VS1838B", size=11, color=MUTED))
    # чорна крапля-приймач
    parts.append(circle(rbx + rbw / 2, rby + 100, 13, fill="#1a1a1a", stroke=INK, sw=1.4))

    # ── Повітряний проміжок: пачки несучої 38 кГц ───────────────────────
    # осьова лінія польоту
    ay = tby + 96
    x0 = tbx + tbw + 6
    x1 = rbx + rbw / 2 - 16   # ціляться в краплю
    parts.append(text((x0 + x1) / 2, tby - 30, "повітря, пряма видимість  1–8 м",
                      size=11, color=MUTED))

    # три пачки мигтіння (кожна — дрібні риски = несуча 38 кГц), між ними паузи
    def burst(cx, n=6, step=7, amp=16):
        segs = []
        for i in range(n):
            xx = cx + i * step
            segs.append(line(xx, ay - amp, xx, ay + amp, color=POS, sw=2.0))
        return segs, cx + (n - 1) * step

    cx = x0 + 18
    for _ in range(3):
        segs, cx = burst(cx)
        parts.extend(segs)
        cx += 40  # пауза
    # напрямна стрілка польоту (тонка, під пачками, не перетинає риски)
    parts.append(arrow(x0 + 6, ay + 34, x1, ay + 34, color=MUTED, sw=1.4))
    parts.append(text((x0 + x1) / 2, ay + 54, "пачки несучої 38 кГц (мигтіння)",
                      size=11, color=POS))

    # ── Знизу: два сигнали в часі — що на світлодіоді vs що на виході приймача ──
    baseY = 350
    # ліворуч: керувальний сигнал (обвідна на боці передавача)
    parts.append(text(tbx + tbw / 2, baseY - 20, "на вході передавача:", size=11, color=INK))
    # проста обвідна: мітка-пробіл-мітка
    ex = tbx + 10
    def envelope(x, y):
        segs = []
        seq = [(0, 0), (0, 1), (46, 1), (46, 0), (74, 0), (74, 1), (120, 1), (120, 0), (150, 0)]
        px, py = None, None
        for dx, lvl in seq:
            X = x + dx
            Y = y - lvl * 22
            if px is not None:
                segs.append(line(px, py, X, Y, color=INK, sw=1.8))
            px, py = X, Y
        return segs
    parts.extend(envelope(ex, baseY + 30))

    # праворуч: вихід приймача — та сама обвідна, але ПЕРЕВЕРНУТА (active-low)
    parts.append(text(rbx + rbw / 2, baseY - 20, "на виході приймача (S):", size=11, color=INK))
    parts.append(text(rbx + rbw / 2, baseY + 54, "спокій = «1», сигнал = «0»", size=10, color=NEG))
    rex = rbx + 10
    def inv_envelope(x, y):
        # перевернуто: спокій зверху (=1), пачка тисне вниз (=0)
        segs = []
        seq = [(0, 1), (0, 0), (46, 0), (46, 1), (74, 1), (74, 0), (120, 0), (120, 1), (150, 1)]
        px, py = None, None
        for dx, lvl in seq:
            X = x + dx
            Y = y - lvl * 22
            if px is not None:
                segs.append(line(px, py, X, Y, color=NEG, sw=1.8))
            px, py = X, Y
        return segs
    parts.extend(inv_envelope(rex, baseY + 30))

    render(os.path.join(IMG, "ir-link.svg"), W, H, *parts)


def ir_map():
    """Мапа ІЧ-членів KY-родини за роллю: пульти (світять кодом / ловлять код)
    проти віддзеркалення (світять поряд і ловлять власне відбиття)."""
    W, H = 820, 430
    parts = []

    parts.append(text(W / 2, 34, "ІЧ-члени KY-родини — за роллю", size=16, color=INK, bold=True))

    # ── Колонка 1: ПУЛЬТИ (лінія зв'язку між приладами) ─────────────────
    c1x, cw = 60, 320
    parts.append(rect(c1x, 60, cw, 320, fill="#f4f8ff", stroke=NEG, sw=1.5, rx=12))
    parts.append(text(c1x + cw / 2, 88, "лінія «пульт → прилад»", size=13, color=NEG, bold=True))
    parts.append(text(c1x + cw / 2, 108, "світло летить від одного до іншого", size=10, color=MUTED))

    # KY-005
    b1 = rect(c1x + 24, 130, cw - 48, 70, fill="#ffffff", stroke=INK, sw=1.4, rx=8)
    parts.append(b1)
    parts.append(text(c1x + 44, 158, "KY-005", size=14, color=INK, bold=True, anchor="start"))
    parts.append(text(c1x + 44, 178, "передавач: одинокий ІЧ-світлодіод,", size=10, color=MUTED, anchor="start"))
    parts.append(text(c1x + 44, 192, "шле код (потрібен резистор)", size=10, color=MUTED, anchor="start"))

    # KY-022
    b2 = rect(c1x + 24, 216, cw - 48, 70, fill="#ffffff", stroke=INK, sw=1.4, rx=8)
    parts.append(b2)
    parts.append(text(c1x + 44, 244, "KY-022", size=14, color=INK, bold=True, anchor="start"))
    parts.append(text(c1x + 44, 264, "приймач: чип 1838 (VS1838B),", size=10, color=MUTED, anchor="start"))
    parts.append(text(c1x + 44, 278, "ловить код, вихід перевернутий", size=10, color=MUTED, anchor="start"))

    # VS1838B (голий приймач)
    b3 = rect(c1x + 24, 302, cw - 48, 60, fill="#fbfcfd", stroke=MUTED, sw=1.3, rx=8)
    parts.append(b3)
    parts.append(text(c1x + 44, 328, "VS1838B", size=13, color=INK, bold=True, anchor="start"))
    parts.append(text(c1x + 44, 348, "той самий приймач без плати", size=10, color=MUTED, anchor="start"))

    # ── Колонка 2: ВІДДЗЕРКАЛЕННЯ (світло вертається до себе) ────────────
    c2x = 440
    parts.append(rect(c2x, 60, cw, 320, fill="#f2fbf5", stroke=FIELD, sw=1.5, rx=12))
    parts.append(text(c2x + cw / 2, 88, "віддзеркалення від поверхні", size=13, color=FIELD, bold=True))
    parts.append(text(c2x + cw / 2, 108, "світять поряд і ловлять власне відбиття", size=10, color=MUTED))

    b4 = rect(c2x + 24, 130, cw - 48, 78, fill="#ffffff", stroke=INK, sw=1.4, rx=8)
    parts.append(b4)
    parts.append(text(c2x + 44, 158, "KY-032", size=14, color=INK, bold=True, anchor="start"))
    parts.append(text(c2x + 44, 178, "давач перешкоди: є відбиток —", size=10, color=MUTED, anchor="start"))
    parts.append(text(c2x + 44, 192, "попереду щось є (поріг гвинтиком)", size=10, color=MUTED, anchor="start"))

    b5 = rect(c2x + 24, 224, cw - 48, 78, fill="#ffffff", stroke=INK, sw=1.4, rx=8)
    parts.append(b5)
    parts.append(text(c2x + 44, 252, "KY-033", size=14, color=INK, bold=True, anchor="start"))
    parts.append(text(c2x + 44, 272, "давач лінії: темне тло не відбиває,", size=10, color=MUTED, anchor="start"))
    parts.append(text(c2x + 44, 286, "світле — відбиває (робот їде по смузі)", size=10, color=MUTED, anchor="start"))

    # примітка внизу зеленої колонки
    note = fitbox(c2x + 24, 318, cw - 48, 44,
                  "інша книга-родина (давачі), не пульти —\nтут лише згадані, щоб не сплутати",
                  size=10, color=MUTED, fill="#eefaf1", stroke=FIELD)
    parts.append(note)

    # спільний низ
    parts.append(text(W / 2, 410, "спільне для всіх: 940 нм · несуча ~38 кГц · трипінова гребінка KY",
                      size=11, color=INK))

    render(os.path.join(IMG, "ir-map.svg"), W, H, *parts)


def why38():
    """ЧОМУ ~38 кГц: несуча відсіює рівне ІЧ-тло сонця/ламп; а конкретне число
    38 — побічний наслідок дільника ÷12 і повсюдного резонатора 455 кГц."""
    W, H = 900, 470
    parts = []

    parts.append(text(W / 2, 34, "Чому пульт мигтить, і чому саме на ~38 кГц", size=16, color=INK, bold=True))

    # ── Верхній ряд: боротьба з фоном (несуча як фільтр) ─────────────────
    topY = 60
    parts.append(text(W / 2, topY + 4, "1 · несуча відрізає рівне ІЧ-тло від пачки пульта", size=12, color=NEG))

    # ліва панель: широкий рівний фон (сонце/лампа)
    lx, lw = 60, 350
    ly, lh = topY + 24, 120
    parts.append(rect(lx, ly, lw, lh, fill="#fffaf0", stroke=MUTED, sw=1.3, rx=8))
    parts.append(text(lx + lw / 2, ly + 22, "що приходить на фотодіод", size=11, color=INK))
    # рівна лінія фону
    baseY = ly + 74
    parts.append(line(lx + 20, baseY, lx + lw - 20, baseY, color=POS, sw=2.2))
    parts.append(text(lx + lw / 2, baseY + 22, "сонце й лампи: сильне, але РІВНЕ ІЧ", size=10, color=POS))
    # дрібні пачки пульта поверх
    def tiny_burst(cx, n, ay, step=4, amp=9):
        segs = []
        for i in range(n):
            xx = cx + i * step
            segs.append(line(xx, ay - amp, xx, ay + amp, color=NEG, sw=1.6))
        return segs
    parts.extend(tiny_burst(lx + 70, 7, ly + 40))
    parts.extend(tiny_burst(lx + 200, 7, ly + 40))
    parts.append(text(lx + lw / 2, ly + 16, "кволі пачки 38 кГц від пульта", size=10, color=NEG, anchor="middle"))

    # стрілка «фільтр» → права панель: лишилась тільки пачка
    midX = lx + lw + 40
    parts.append(arrow(lx + lw + 6, ly + lh / 2, midX + 28, ly + lh / 2, color=INK, sw=1.8))
    parts.append(text(midX + 14, ly + lh / 2 - 12, "смуговий", size=10, color=INK))
    parts.append(text(midX + 14, ly + lh / 2 + 24, "фільтр 38 кГц", size=10, color=INK))

    rx2 = midX + 60
    rw2 = W - rx2 - 40
    parts.append(rect(rx2, ly, rw2, lh, fill="#f4f8ff", stroke=NEG, sw=1.3, rx=8))
    parts.append(text(rx2 + rw2 / 2, ly + 22, "що бачить демодулятор", size=11, color=INK))
    parts.extend(tiny_burst(rx2 + 40, 8, ly + 74, step=5, amp=14))
    parts.extend(tiny_burst(rx2 + 130, 8, ly + 74, step=5, amp=14))
    parts.append(text(rx2 + rw2 / 2, ly + lh - 14, "рівний фон викинуто, лишилась пачка", size=10, color=NEG))

    # ── Нижній ряд: звідки взялося число 38 ─────────────────────────────
    botY = 300
    parts.append(text(W / 2, botY, "2 · а звідки саме 38, а не 36 чи 40 — з дільника й резонатора", size=12, color=FIELD))

    # два ланцюжки-обчислення поруч, з великим просвітом
    def chain(cx, top_label, res, note, col):
        segs = []
        bw = 300
        bx = cx - bw / 2
        segs.append(text(cx, botY + 30, top_label, size=11, color=col, bold=True))
        # рядок обчислення в код-стилі
        segs.append(rect(bx, botY + 44, bw, 92, fill="#fbfcfd", stroke=col, sw=1.3, rx=8))
        segs.append(text(cx, botY + 70, res, size=13, color=INK))
        segs.append(text(cx, botY + 96, note[0], size=10, color=MUTED))
        segs.append(text(cx, botY + 116, note[1], size=10, color=MUTED))
        return segs

    parts.extend(chain(255, "«за книжкою» (RC-5, Philips)",
                       "432 кГц ÷ 12 = 36.0 кГц",
                       ("резонатор 432 кГц — рідкісний,", "мало хто його ставив"), NEG))
    parts.extend(chain(645, "«як вийшло насправді»",
                       "455 кГц ÷ 12 = 37.92 ≈ 38 кГц",
                       ("455 кГц — копійчаний резонатор ПЧ", "з кожного АМ-приймача"), FIELD))

    parts.append(arrow(415, botY + 90, 485, botY + 90, color=INK, sw=1.8))

    parts.append(text(W / 2, botY + 158, "тому «38 кГц» — не закон фізики, а звичка масового виробництва",
                      size=11, color=INK, bold=True))

    render(os.path.join(IMG, "why-38khz.svg"), W, H, *parts)


def ir_lineage():
    """Родовід побутового ІЧ-пульта: від першого цифрового пульта до
    'приймач в одному корпусі' (Telefunken/Vishay TSOP) і NEC як де-факто."""
    W, H = 900, 430
    parts = []

    parts.append(text(W / 2, 34, "Родовід побутового ІЧ-пульта", size=16, color=INK, bold=True))

    # горизонтальна вісь часу
    axY = 210
    parts.append(line(60, axY, W - 60, axY, color=MUTED, sw=1.6))
    parts.append(text(W - 56, axY + 4, "час", size=11, color=MUTED, anchor="start"))

    # віхи: (x, рік, заголовок, підпис-рядки, зверху/знизу, колір)
    milestones = [
        (130, "1970", "RCA: цифровий пульт",
         ["перший повністю", "електронний, память", "на MOSFET"], "up", INK),
        (300, "1973→78", "поштовх — телетекст",
         ["Ceefax від BBC зажадав", "багатокнопкового пульта;", "ІЧ-прототипи ~1977–78"], "down", MUTED),
        (470, "поч. 1980-х", "RC-5 (Philips)",
         ["перший добре описаний", "протокол; несуча 36 кГц", "проти смуг розгортки ТБ"], "up", NEG),
        (640, "1980-ті", "NEC (Nippon Electric)",
         ["де-факто пультів побуту;", "несуча 38 кГц; поряд —", "Sony SIRC 40, ITT"], "down", FIELD),
        (810, "1990-ті", "TSOP: приймач у корпусі",
         ["Telefunken→Vishay: фотодіод", "+ підсилювач + фільтр +", "епокси-ІЧ-скло як один чип"], "up", POS),
    ]

    for x, yr, head, sub, side, col in milestones:
        # точка на осі
        parts.append(circle(x, axY, 6, fill=col, stroke=INK, sw=1.2))
        parts.append(text(x, axY + (26 if side == "up" else -14), yr, size=12, color=col, bold=True))
        # картка
        cw, ch = 150, 92
        cx = x
        if side == "up":
            cy = axY - 40 - ch
        else:
            cy = axY + 44
        bx = cx - cw / 2
        # тримаємо картки в межах полотна
        bx = max(20, min(bx, W - 20 - cw))
        parts.append(rect(bx, cy, cw, ch, fill="#fbfcfd", stroke=col, sw=1.3, rx=8))
        parts.append(text(bx + cw / 2, cy + 20, head, size=11, color=INK, bold=True))
        for i, ln in enumerate(sub):
            parts.append(text(bx + cw / 2, cy + 40 + i * 15, ln, size=9, color=MUTED))
        # тонка ніжка від картки до осі
        legY0 = cy + ch if side == "up" else cy
        parts.append(line(x, legY0, x, axY, color=col, sw=1.0, dash="3,3"))

    parts.append(text(W / 2, H - 14,
                      "спільне для всіх ІЧ-членів KY: 940 нм · несуча ~38 кГц · «слухавка» вже зібрана в чипі",
                      size=11, color=INK))

    render(os.path.join(IMG, "ir-lineage.svg"), W, H, *parts)


ir_link()
ir_map()
why38()
ir_lineage()
print("figs done")
