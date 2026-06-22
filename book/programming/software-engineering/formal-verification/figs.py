# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PROOF = "#1f8a8a"   # бірюзовий «доказ»
PROOFBG = "#e6f4f4"
TESTBG = "#fff6e0"
TESTCL = "#caa24a"


# ════════════════════════════════════════════════════════════════════════════
# Базова версія (formal-verification.md)
# ════════════════════════════════════════════════════════════════════════════


# ── test-vs-proof: тест показує наявність, доказ — відсутність ─────────────────
# Ідея (Дейкстра): тест проходить ПОодинці точки простору входів і може лише
# СПІЙМАТИ баг; доказ накриває ВЕСЬ простір і стверджує його відсутність.

def fig_test_vs_proof():
    W, H = 820, 380
    p = []

    # ліва панель — тестування: кілька проб у великому полі входів
    lx, lw, top, ph = 30, 360, 78, 250
    p.append(rect(lx, top, lw, ph, fill=TESTBG, stroke=TESTCL, sw=2, rx=12))
    p.append(text(lx + lw / 2, top + 28, "тест — проби простору входів", size=13, color="#8a6d1a", bold=True))
    # поле всіх входів
    fx, fy, fw, fh = lx + 28, top + 48, lw - 56, 132
    p.append(rect(fx, fy, fw, fh, fill=BG, stroke=MUTED, sw=1.3, rx=8))
    p.append(text(fx + fw / 2, fy + 16, "усі можливі входи", size=9.5, color=MUTED, italic=True))
    # кілька «перевірених» точок (зелені) і прихований баг (червоний) між ними
    import math
    pts = [(0.18, 0.45), (0.34, 0.72), (0.52, 0.34), (0.7, 0.66), (0.85, 0.5), (0.46, 0.84)]
    for u, v in pts:
        cx, cy = fx + 14 + u * (fw - 28), fy + 26 + v * (fh - 40)
        p.append(circle(cx, cy, 5, fill=PROOFBG, stroke=PROOF, sw=1.6))
    # прихований баг — у непокритій зоні
    bx, by = fx + 14 + 0.62 * (fw - 28), fy + 26 + 0.2 * (fh - 40)
    p.append(circle(bx, by, 6.5, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(bx, by - 12, "✗ баг", size=9.5, color=POS, bold=True))
    p.append(text(lx + lw / 2, top + ph - 30, "пройшов тест ≠ нема бага", size=11, color=POS, bold=True))
    p.append(text(lx + lw / 2, top + ph - 12, "проби накрили не весь простір", size=9.5, color=MUTED, italic=True))

    # права панель — доказ: усе поле зафарбоване
    rx = W - 30 - lw
    p.append(rect(rx, top, lw, ph, fill=PROOFBG, stroke=PROOF, sw=2, rx=12))
    p.append(text(rx + lw / 2, top + 28, "доказ — увесь простір одразу", size=13, color=PROOF, bold=True))
    gx, gy, gw, gh = rx + 28, top + 48, lw - 56, 132
    p.append(rect(gx, gy, gw, gh, fill="#d4ece9", stroke=PROOF, sw=1.6, rx=8))
    # суцільне штрихування — «усе накрито»
    for i in range(1, 9):
        xx = gx + i * gw / 9
        p.append(line(xx, gy + 6, xx, gy + gh - 6, color=PROOF, sw=0.8, dash="2 4"))
    p.append(text(gx + gw / 2, gy + gh / 2 + 4, "властивість тримається\nдля КОЖНОГО входу", size=10, color=PROOF, bold=True))
    # перетворимо на mtext
    p[-1] = mtext(gx + gw / 2, gy + gh / 2 - 2, "властивість тримається\nдля КОЖНОГО входу", size=10, color=PROOF, bold=True)
    p.append(text(rx + lw / 2, top + ph - 30, "доведено → бага цього класу нема", size=11, color=PROOF, bold=True))
    p.append(text(rx + lw / 2, top + ph - 12, "не проба, а твердження про все", size=9.5, color=MUTED, italic=True))

    p.append(text(W / 2, H - 16,
                  "тест показує ПРИСУТНІСТЬ багів, але ніколи — їхню відсутність (Дейкстра)",
                  size=11.5, color=INK, italic=True))

    render(os.path.join(OUT, "test-vs-proof.svg"), W, H, *p,
           title="Тест проти доказу: проба простору проти твердження про весь простір")


# ── ladder: три родини формальних методів за силою й ціною ─────────────────────
# Ідея: model checking (автомат) → SMT/дедуктивна (контракти+розв'язувач) →
# теорема-пруфери (Coq, ручний доказ). Що нижче — то сильніше, дорожче, ручніше.

def fig_methods_ladder():
    W, H = 840, 380
    p = []
    rows = [
        ("Перевірка моделей (model checking)",
         "автоматичний перебір УСІХ станів скінченної моделі",
         "TLA+ / TLC · SPIN", "автоматично, але модель мусить бути скінченна",
         FIELD, "#eef6ef"),
        ("Дедуктивна верифікація + SMT",
         "контракти {P}C{Q} → умови коректності → розв'язувач",
         "Frama-C / ACSL · Z3", "напівавтоматично: анотації пишеш ти, доводить машина",
         PROOF, PROOFBG),
        ("Інтерактивні теорема-пруфери",
         "доказ будуєш кроками, машина перевіряє кожен крок",
         "Coq · Isabelle", "найсильніше й найдорожче: доказ пишеться руками",
         NEG, "#e9eefb"),
    ]
    bx, bw = 80, 680
    top, rh, gap = 66, 88, 16
    for i, (name, how, tools, cost, col, fill) in enumerate(rows):
        y = top + i * (rh + gap)
        p.append(rect(bx, y, bw, rh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(bx + 18, y + 24, name, size=13, color=col, bold=True, anchor="start"))
        p.append(text(bx + 18, y + 44, how, size=10, color=INK, anchor="start"))
        p.append(text(bx + 18, y + 64, "приклади: " + tools, size=9.5, color=MUTED, anchor="start", italic=True))
        p.append(text(bx + bw - 16, y + 64, cost, size=9, color=col, anchor="end", italic=True))

    # шкала «сила / ручна праця» зліва
    p.append(arrow(bx - 28, top + 6, bx - 28, top + 3 * (rh + gap) - gap, color=MUTED, sw=1.8))
    p.append(mtext(bx - 40, top + 30, "сила\nавтомат.", size=9, color=FIELD, anchor="end", lh=1.2, bold=True))
    p.append(mtext(bx - 40, top + 2 * (rh + gap) + 30, "сила\nручна", size=9, color=NEG, anchor="end", lh=1.2, bold=True))

    p.append(text(W / 2, H - 14,
                  "що нижче — то ширший клас властивостей доводиться, але дорожче й менш автоматично",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "methods-ladder.svg"), W, H, *p,
           title="Три родини формальних методів: від автоматичної до ручної")


# ── proof-vs-spec-limit: доказ певний щодо специфікації, але специфікація може бути хибна
# Ідея: ланцюг «реальна вимога → специфікація → код → доказ». Доказ замикає лише
# ланку код↔специфікація. Якщо специфікація не відбиває реальну вимогу — доведено
# правильно НЕ ТЕ. Це головна межа методу.

def fig_spec_limit():
    W, H = 820, 320
    p = []
    nodes = [
        ("реальна\nвимога", "що насправді\nтреба", MUTED, "#f1f1f1"),
        ("специфікація", "формальний\nзапис вимоги", PROOF, PROOFBG),
        ("код", "реалізація", INK, FILL),
    ]
    bw, bh = 180, 96
    gap = (W - 60 - 3 * bw) / 2
    y = 92
    xs = []
    for i, (name, note, col, fill) in enumerate(nodes):
        x = 30 + i * (bw + gap)
        xs.append((x, x + bw))
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(mtext(x + bw / 2, y + 34, name, size=13, color=col, bold=True, lh=1.15))
        p.append(mtext(x + bw / 2, y + 66, note, size=9.5, color=MUTED, lh=1.2))

    # стрілка код↔специфікація — це й є доказ (зелена, певна)
    p.append(arrow(xs[2][0] - 4, y + bh / 2, xs[1][1] + 4, y + bh / 2, color=PROOF, sw=2.6))
    p.append(arrow(xs[1][1] + 4, y + bh / 2 + 18, xs[2][0] - 4, y + bh / 2 + 18, color=PROOF, sw=2.6))
    p.append(text((xs[1][1] + xs[2][0]) / 2, y - 10, "ДОКАЗ", size=12, color=PROOF, bold=True))
    p.append(text((xs[1][1] + xs[2][0]) / 2, y + bh + 26, "машина гарантує:\nкод = специфікація", size=9.5, color=PROOF, italic=True))
    p[-1] = mtext((xs[1][1] + xs[2][0]) / 2, y + bh + 26, "машина гарантує:\nкод = специфікація", size=9.5, color=PROOF, lh=1.2)

    # ланка вимога↔специфікація — НЕ доведена, людська, крихка (червона, пунктир)
    p.append(line(xs[0][1] + 4, y + bh / 2, xs[1][0] - 4, y + bh / 2, color=POS, sw=2.4, dash="6 4"))
    p.append(text((xs[0][1] + xs[1][0]) / 2, y - 10, "?", size=18, color=POS, bold=True))
    p.append(mtext((xs[0][1] + xs[1][0]) / 2, y + bh + 26, "НЕ доведено:\nлюдина пише руками", size=9.5, color=POS, lh=1.2))

    p.append(text(W / 2, H - 30,
                  "доказ замикає лише ланку «код ↔ специфікація»",
                  size=11.5, color=INK))
    p.append(text(W / 2, H - 12,
                  "хибна специфікація → бездоганно доведено НЕ ТЕ; це головна межа методу",
                  size=10.5, color=POS, italic=True))

    render(os.path.join(OUT, "spec-limit.svg"), W, H, *p,
           title="Межа доказу: певність лише щодо специфікації, яку пише людина")


# ════════════════════════════════════════════════════════════════════════════
# Детальна версія (formal-verification-d.md)
# ════════════════════════════════════════════════════════════════════════════


# ── state-explosion: вибух простору станів і як його приборкують абстракцією ───
# Ідея: реальний простір станів зростає вибухово (добуток змінних), повний перебір
# неможливий; абстракція склеює нерозрізненні стани в класи — і модель стає скінченною.

def fig_state_explosion():
    W, H = 820, 380
    p = []

    # ліва — конкретний простір: щільна сітка точок (вибух)
    lx, lw, top, ph = 30, 360, 80, 250
    p.append(rect(lx, top, lw, ph, fill="#fbecec", stroke=POS, sw=2, rx=12))
    p.append(text(lx + lw / 2, top + 26, "конкретні стани", size=13, color=POS, bold=True))
    gx, gy, gw, gh = lx + 26, top + 44, lw - 52, 150
    p.append(rect(gx, gy, gw, gh, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    cols, rowsn = 16, 9
    for r in range(rowsn):
        for c in range(cols):
            cx = gx + 8 + c * (gw - 16) / (cols - 1)
            cy = gy + 8 + r * (gh - 16) / (rowsn - 1)
            p.append(circle(cx, cy, 2.2, fill=POS, stroke="none", sw=0))
    p.append(mtext(lx + lw / 2, top + ph - 34, "n змінних → добуток діапазонів", size=10, color=INK))
    p.append(text(lx + lw / 2, top + ph - 14, "перебрати все — неможливо (вибух станів)", size=9.5, color=POS, italic=True))

    # стрілка «абстракція»
    midx = lx + lw + (W - 2 * (lx + lw)) / 2
    p.append(arrow(lx + lw + 6, top + ph / 2, W - lw - 30 - 6, top + ph / 2, color=PROOF, sw=2.6))
    p.append(text(midx, top + ph / 2 - 12, "абстракція", size=11, color=PROOF, bold=True))
    p.append(mtext(midx, top + ph / 2 + 12, "склеїти\nнерозрізненні", size=9, color=MUTED, lh=1.15))

    # права — абстрактний простір: кілька великих класів
    rx = W - 30 - lw
    p.append(rect(rx, top, lw, ph, fill=PROOFBG, stroke=PROOF, sw=2, rx=12))
    p.append(text(rx + lw / 2, top + 26, "абстрактні класи станів", size=13, color=PROOF, bold=True))
    ax, ay, aw, ah = rx + 26, top + 44, lw - 52, 150
    p.append(rect(ax, ay, aw, ah, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    classes = [("< 0", 0.2, 0.32), ("= 0", 0.5, 0.32), ("> 0", 0.8, 0.32),
               ("порожньо", 0.3, 0.72), ("повно", 0.7, 0.72)]
    for name, u, v in classes:
        cx, cy = ax + u * aw, ay + v * ah
        p.append(circle(cx, cy, 24, fill=PROOFBG, stroke=PROOF, sw=2))
        p.append(text(cx, cy + 4, name, size=9, color=PROOF, bold=True))
    p.append(text(rx + lw / 2, top + ph - 34, "скінченно мало класів", size=10, color=INK))
    p.append(text(rx + lw / 2, top + ph - 14, "тепер перебір ЗАВЕРШУЄТЬСЯ", size=9.5, color=PROOF, italic=True))

    p.append(text(W / 2, H - 14,
                  "абстракція робить нескінченний (чи величезний) простір скінченним — ціною огрублення",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "state-explosion.svg"), W, H, *p,
           title="Вибух станів і абстракція: від добутку змінних до класів")


# ── hoare-triple: трійка Гоара {P} C {Q} і слабша передумова ──────────────────
# Ідея: {P} C {Q} читається «якщо до C справджується P, то після C — Q». Доказ
# методом слабшої передумови йде НАЗАД: від Q крізь C обчислюємо, що треба на вході.

def fig_hoare_triple():
    W, H = 800, 320
    p = []

    # центральна стрічка: P — C — Q
    y = 110
    bh = 92
    # P
    px, pw = 60, 200
    p.append(rect(px, y, pw, bh, fill=PROOFBG, stroke=PROOF, sw=2, rx=10))
    p.append(text(px + pw / 2, y + 30, "{ P }", size=18, color=PROOF, bold=True))
    p.append(mtext(px + pw / 2, y + 56, "передумова:\nстан ДО виконання", size=9.5, color=INK, lh=1.2))
    # C
    cx, cw = px + pw + 50, 180
    p.append(rect(cx, y, cw, bh, fill=FILL, stroke=INK, sw=2, rx=10))
    p.append(text(cx + cw / 2, y + 30, "C", size=18, color=INK, bold=True))
    p.append(mtext(cx + cw / 2, y + 56, "програма\n(інструкції)", size=9.5, color=MUTED, lh=1.2))
    # Q
    qx, qw = cx + cw + 50, 200
    p.append(rect(qx, y, qw, bh, fill=PROOFBG, stroke=PROOF, sw=2, rx=10))
    p.append(text(qx + qw / 2, y + 30, "{ Q }", size=18, color=PROOF, bold=True))
    p.append(mtext(qx + qw / 2, y + 56, "постумова:\nстан ПІСЛЯ", size=9.5, color=INK, lh=1.2))

    # стрілки виконання вперед
    p.append(arrow(px + pw + 6, y + bh / 2, cx - 6, y + bh / 2, color=INK, sw=2))
    p.append(arrow(cx + cw + 6, y + bh / 2, qx - 6, y + bh / 2, color=INK, sw=2))
    p.append(text((px + pw + cx) / 2, y + bh / 2 - 10, "виконання", size=9, color=MUTED, italic=True))

    # читання трійки зверху
    p.append(text(W / 2, y - 22, "«якщо до C справджується P, то після C справдиться Q»",
                  size=12, color=INK, italic=True))

    # доказ іде НАЗАД (слабша передумова) — червона стрілка під стрічкою
    p.append(arrow(qx + qw / 2, y + bh + 30, px + pw / 2, y + bh + 30, color=POS, sw=2.4))
    p.append(text(W / 2, y + bh + 22, "доказ рухається НАЗАД: від Q крізь C — яка P достатня",
                  size=10.5, color=POS, bold=True))
    p.append(text(W / 2, y + bh + 50, "(числення слабшої передумови — основа дедуктивної верифікації)",
                  size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "hoare-triple.svg"), W, H, *p,
           title="Трійка Гоара {P} C {Q}: уперед виконання, назад доказ")


# ── verification-chain: від контракту до доведеного коду (Frama-C/ACSL/SMT) ────
# Ідея: конвеєр дедуктивної верифікації — анотований код → генератор умов (WP) →
# умови коректності → SMT-розв'язувач → «доведено» або «не зміг» (контрприклад).

def fig_verification_chain():
    W, H = 820, 330
    p = []
    steps = [
        ("код + ACSL-анотації", "/*@ requires …\n   ensures … */", PROOF, PROOFBG),
        ("генератор умов (WP)", "слабша передумова →\nумови коректності", FIELD, "#eef6ef"),
        ("SMT-розв'язувач (Z3)", "довести логічні\nтвердження", NEG, "#e9eefb"),
    ]
    bw, bh = 210, 100
    gap = (W - 60 - 3 * bw) / 2
    y = 80
    xs = []
    for i, (name, note, col, fill) in enumerate(steps):
        x = 30 + i * (bw + gap)
        xs.append((x, x + bw))
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(x + bw / 2, y + 26, name, size=12, color=col, bold=True))
        p.append(mtext(x + bw / 2, y + 52, note, size=9.5, color=INK, lh=1.25))
        if i > 0:
            p.append(arrow(xs[i - 1][1] + 6, y + bh / 2, x - 6, y + bh / 2, color=INK, sw=2))

    # дві розв'язки з SMT — дві коробки, центровані під усією фігурою
    smt_cx = xs[2][0] + bw / 2    # центр третього кроку (звідки виходить стрілка)
    sx = W / 2                    # центр розгалуження
    yy = y + bh + 34
    ow, og = 250, 18             # ширина коробки й проміжок
    lxo = sx - ow - og / 2       # ліва коробка
    rxo = sx + og / 2            # права коробка
    p.append(rect(lxo, yy, ow, 50, fill=PROOFBG, stroke=PROOF, sw=2, rx=8))
    p.append(text(lxo + ow / 2, yy + 22, "✓ довів", size=12, color=PROOF, bold=True))
    p.append(text(lxo + ow / 2, yy + 40, "контракт тримається", size=9, color=MUTED, italic=True))
    p.append(rect(rxo, yy, ow, 50, fill="#fbecec", stroke=POS, sw=2, rx=8))
    p.append(text(rxo + ow / 2, yy + 22, "✗ не зміг / контрприклад", size=10.5, color=POS, bold=True))
    p.append(text(rxo + ow / 2, yy + 40, "слабка анотація або баг", size=9, color=MUTED, italic=True))

    # стрілка від SMT-кроку донизу, тоді розгалуження до двох коробок
    p.append(arrow(smt_cx, y + bh + 6, smt_cx, yy - 14, color=INK, sw=2))
    p.append(line(lxo + ow / 2, yy - 14, rxo + ow / 2, yy - 14, color=INK, sw=1.6))
    p.append(line(smt_cx, yy - 14, smt_cx, yy - 14, color=INK, sw=1.6))
    p.append(arrow(lxo + ow / 2, yy - 14, lxo + ow / 2, yy - 4, color=PROOF, sw=2))
    p.append(arrow(rxo + ow / 2, yy - 14, rxo + ow / 2, yy - 4, color=POS, sw=2))

    p.append(text(W / 2, H - 12,
                  "анотації пише людина; умови й доказ — машина; «не зміг» означає слабку анотацію або справжній баг",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "verification-chain.svg"), W, H, *p,
           title="Конвеєр дедуктивної верифікації: від контракту до вироку SMT")


# ── trusted-base: що доказ ГАРАНТУЄ і у що все одно мусиш вірити ───────────────
# Ідея: навіть доведений код спирається на «довірену базу» — специфікація,
# пруфер, компілятор, залізо. Доказ переносить довіру, а не скасовує її.

def fig_trusted_base():
    W, H = 760, 360
    p = []
    # доведений код — у центрі вгорі
    cx = W / 2
    p.append(rect(cx - 150, 60, 300, 56, fill=PROOFBG, stroke=PROOF, sw=2.4, rx=10))
    p.append(text(cx, 84, "ДОВЕДЕНИЙ КОД", size=14, color=PROOF, bold=True))
    p.append(text(cx, 104, "властивість математично гарантована", size=9.5, color=MUTED, italic=True))

    # стовпи довіри, на яких він стоїть
    base = [
        ("специфікація", "відбиває справжню\nвимогу?", POS),
        ("пруфер", "сам доказувач\nбез вади?", WARN if False else "#caa24a"),
        ("компілятор", "переклав без\nспотворення?", NEG),
        ("залізо", "виконує так,\nяк припускали?", MUTED),
    ]
    n = len(base)
    bw = 150
    gap = (W - 60 - n * bw) / (n - 1)
    y = 200
    for i, (name, q, col) in enumerate(base):
        x = 30 + i * (bw + gap)
        p.append(rect(x, y, bw, 90, fill=BG, stroke=col, sw=2, rx=10))
        p.append(text(x + bw / 2, y + 26, name, size=12, color=col, bold=True))
        p.append(mtext(x + bw / 2, y + 48, q, size=9, color=INK, lh=1.2))
        # підпора під код
        p.append(line(x + bw / 2, y - 4, cx, 120, color=col, sw=1.4, dash="4 3"))

    p.append(text(W / 2, y - 14, "довірена база (їй віримо без доказу)", size=11, color=INK, bold=True))

    p.append(text(W / 2, H - 28,
                  "доказ ПЕРЕНОСИТЬ довіру на цю базу, а не скасовує її",
                  size=11.5, color=INK))
    p.append(text(W / 2, H - 10,
                  "seL4 і CompCert тому й цінні: вони звужують базу — менше того, у що треба просто вірити",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "trusted-base.svg"), W, H, *p,
           title="Довірена база: що доказ гарантує і у що все одно віриш")


if __name__ == "__main__":
    fig_test_vs_proof()
    fig_methods_ladder()
    fig_spec_limit()
    fig_state_explosion()
    fig_hoare_triple()
    fig_verification_chain()
    fig_trusted_base()
    print("OK: figures written to", OUT)
