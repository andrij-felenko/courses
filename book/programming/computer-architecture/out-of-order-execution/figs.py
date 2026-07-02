# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

C_WAIT = "#eef1f4"; S_WAIT = MUTED          # простій / очікування
C_WORK = "#eaf6ef"; S_WORK = FIELD          # корисна робота
C_LOAD = "#eaf0fd"; S_LOAD = NEG            # довге завантаження з пам'яті
C_BLOCK= "#fdecea"; S_BLOCK= POS            # затор / та сама команда, що застрягла


def cell(cx, cy, label, fill, stroke, w, h=30):
    x, y = cx - w / 2, cy - h / 2
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.4, rx=5)
            + text(cx, cy + 4, label, size=11, color=stroke, bold=True))


# ── 1. Головна ідея: черга проти вікна ───────────────────────────────────────
def fig_in_order_vs_ooo():
    W, H = 780, 400
    p = [text(W / 2, 28, "Довге завантаження: черга стоїть, вікно працює", size=16, bold=True)]
    x0, cw = 210, 52
    n = 8
    # шкала тактів (спільна для двох панелей)
    for i in range(n):
        p.append(text(x0 + i * cw + cw / 2, 62, "т%d" % (i + 1), size=10, color=MUTED, bold=True))

    # ── панель А: строго по черзі ──
    yA = 100
    p.append(text(x0 - 12, yA - 22, "Строго по черзі", size=12, color=INK, bold=True, anchor="end"))
    # LOAD займає т1..т4 (промах кешу — 4 такти)
    p.append(cell(x0 + 0 * cw + 2 * cw, yA, "LOAD R1  (промах кешу, 4 такти)", C_LOAD, S_LOAD, w=4 * cw - 6))
    # ADD R2 залежить від R1 — чекає, тоді т5
    yA2 = yA + 40
    for i in range(4):
        p.append(cell(x0 + i * cw + cw / 2, yA2, "стоїть", C_WAIT, S_WAIT, w=cw - 6))
    p.append(cell(x0 + 4 * cw + cw / 2, yA2, "ADD R2", C_WORK, S_WORK, w=cw - 6))
    # MUL R4 — незалежна, але за порядком мусить чекати
    yA3 = yA2 + 40
    for i in range(5):
        p.append(cell(x0 + i * cw + cw / 2, yA3, "стоїть", C_WAIT, S_WAIT, w=cw - 6))
    p.append(cell(x0 + 5 * cw + cw / 2, yA3, "MUL R4", C_WORK, S_WORK, w=cw - 6))
    p.append(text(x0 - 12, yA2 + 4, "ADD R2←R1", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 - 12, yA3 + 4, "MUL R4←R5", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 + 6 * cw, yA3 + 4, "готово аж на т6", size=10, color=POS, anchor="start"))

    # ── панель Б: позачергово ──
    yB = 250
    p.append(text(x0 - 12, yB - 22, "Позачергово", size=12, color=INK, bold=True, anchor="end"))
    p.append(cell(x0 + 2 * cw, yB, "LOAD R1  (промах кешу, 4 такти)", C_LOAD, S_LOAD, w=4 * cw - 6))
    yB2 = yB + 40
    # MUL R4 незалежна — виконується поки LOAD у польоті (т1)
    p.append(cell(x0 + 0 * cw + cw / 2, yB2, "MUL R4", C_WORK, S_WORK, w=cw - 6))
    p.append(text(x0 + 1 * cw + 6, yB2 + 4, "не чекала — пішла першою", size=10, color=FIELD, anchor="start"))
    yB3 = yB2 + 40
    # ADD R2 мусить чекати R1 — виконується щойно LOAD завершився (т5)
    for i in range(4):
        p.append(cell(x0 + i * cw + cw / 2, yB3, "чекає R1", C_WAIT, S_WAIT, w=cw - 6))
    p.append(cell(x0 + 4 * cw + cw / 2, yB3, "ADD R2", C_WORK, S_WORK, w=cw - 6))
    p.append(text(x0 - 12, yB2 + 4, "MUL R4←R5", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 - 12, yB3 + 4, "ADD R2←R1", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 + 5 * cw + 6, yB3 + 4, "усе готово на т5", size=10, color=FIELD, anchor="start"))
    return render(os.path.join(OUT, "in-order-vs-ooo.svg"), W, H, *p)


# ── 2. Несправжня залежність і перейменування регістрів ──────────────────────
def fig_renaming():
    W, H = 780, 340
    p = [text(W / 2, 28, "Несправжня залежність: імена стикаються, дані — ні", size=16, bold=True)]

    # ліворуч: до перейменування
    lx = 40
    p.append(text(lx, 70, "Як написано (обидві пишуть у R3):", size=12, color=INK, bold=True, anchor="start"))
    b1, w1, h1 = textbox(lx + 150, 110, "A:  R3 ← R1 + R2", size=13, fill=C_WORK, stroke=S_WORK, bold=True, min_w=250)
    p.append(b1)
    b2, w2, h2 = textbox(lx + 150, 160, "B:  R3 ← R5 · R6", size=13, fill=C_WORK, stroke=S_WORK, bold=True, min_w=250)
    p.append(b2)
    # хибна стрілка «B чекає A»
    p.append(arrow(lx + 150, 178, lx + 150, 132, color=POS))
    p.append(text(lx + 165, 152, "B нібито мусить", size=10, color=POS, anchor="start"))
    p.append(text(lx + 165, 166, "чекати A —", size=10, color=POS, anchor="start"))
    p.append(text(lx + 165, 180, "хоч даних не бере", size=10, color=POS, anchor="start"))
    p.append(text(lx + 150, 225, "Клас у клас — те саме ім'я R3.", size=11, color=MUTED))
    p.append(text(lx + 150, 243, "Це не потік даних, а тіснота імен.", size=11, color=MUTED))

    # стрілка переходу
    p.append(arrow(400, 150, 460, 150, color=INK, sw=2.2))
    p.append(text(430, 138, "переймен.", size=10, color=INK))

    # праворуч: після перейменування
    rx = 480
    p.append(text(rx, 70, "Апаратура дає різні фізичні комірки:", size=12, color=INK, bold=True, anchor="start"))
    b3, w3, h3 = textbox(rx + 130, 110, "A:  p37 ← R1 + R2", size=13, fill=C_WORK, stroke=S_WORK, bold=True, min_w=230)
    p.append(b3)
    b4, w4, h4 = textbox(rx + 130, 160, "B:  p52 ← R5 · R6", size=13, fill=C_WORK, stroke=S_WORK, bold=True, min_w=230)
    p.append(b4)
    p.append(text(rx + 130, 210, "p37 і p52 — різні регістри.", size=11, color=FIELD))
    p.append(text(rx + 130, 228, "Залежності нема — обидві", size=11, color=FIELD))
    p.append(text(rx + 130, 246, "йдуть одночасно.", size=11, color=FIELD))
    return render(os.path.join(OUT, "renaming.svg"), W, H, *p)


# ── 3. Три ділянки: вхід по черзі · вікно позачергово · вихід по черзі ────────
def fig_ooo_pipeline():
    W, H = 800, 300
    p = [text(W / 2, 28, "По черзі → позачергово → знову по черзі", size=16, bold=True)]
    cy = 150
    # три зони
    zx = [30, 300, 570]; zw = [230, 240, 200]
    labels = ["ВХІД — по черзі", "ВІКНО — позачергово", "ВИХІД — по черзі"]
    subs = [
        "вибірка · декодування ·\nперейменування · видача\nв чергу",
        "станції очікування:\nкоманда стартує, ЩОЙНО\nготові її дані —\nбудь-яка, будь-коли",
        "буфер упорядкування (ROB):\nрезультати «оприлюднюють»\nстрого за програмою",
    ]
    cols = [(C_WAIT, S_WAIT), (C_WORK, S_WORK), (C_LOAD, S_LOAD)]
    for i in range(3):
        fc, sc = cols[i]
        p.append(rect(zx[i], cy - 62, zw[i], 124, fill=fc, stroke=sc, sw=1.6, rx=8))
        p.append(text(zx[i] + zw[i] / 2, cy - 40, labels[i], size=12, color=sc, bold=True))
        p.append(mtext(zx[i] + zw[i] / 2, cy - 12, subs[i], size=10, color=INK, lh=1.25))
    # стрілки між зонами
    p.append(arrow(zx[0] + zw[0], cy, zx[1], cy, color=INK, sw=2))
    p.append(arrow(zx[1] + zw[1], cy, zx[2], cy, color=INK, sw=2))
    # підпис знизу
    p.append(text(W / 2, cy + 90, "Ззовні порядок збережено; всередині — воля. Це і є весь фокус.",
                  size=12, color=MUTED, italic=True))
    return render(os.path.join(OUT, "ooo-pipeline.svg"), W, H, *p)


# ── 4. Meltdown: слід у кеші переживає скасовану команду ──────────────────────
def fig_cache_trace():
    W, H = 800, 430
    p = [text(W / 2, 28, "Викинута робота стерта — а слід у кеші лишився", size=16, bold=True)]

    # ── ліва колонка: що робить процесор у транзитному вікні ──
    lx = 40
    p.append(text(lx, 66, "У транзитному вікні (до перевірки прав):", size=12, color=INK, bold=True, anchor="start"))
    steps = [
        ("1", "читає байт із забороненої адреси → таємне значення  s", C_LOAD, S_LOAD),
        ("2", "звертається до probe[s · 256] — підтягує цей рядок у кеш", C_LOAD, S_LOAD),
        ("3", "апаратура помічає: доступу не було права → ВИНЯТОК", C_BLOCK, S_BLOCK),
    ]
    sy = 92
    for i, (nn, txt, fc, sc) in enumerate(steps):
        y = sy + i * 46
        p.append(circle(lx + 14, y + 14, 13, fill=fc, stroke=sc, sw=1.8))
        p.append(text(lx + 14, y + 18, nn, size=13, color=sc, bold=True))
        b, w, h = textbox(lx + 40 + 355, y + 14, txt, size=11, fill=fc, stroke=sc, min_w=710 - 40, sw=1.3)
        p.append(b)

    # результат скасування
    yr = sy + 3 * 46 + 12
    p.append(text(lx, yr + 4, "Виняток → усе транзитне ВИКИНУТО: регістри, результати — як не було.",
                  size=12, color=POS, bold=True, anchor="start"))
    p.append(text(lx, yr + 24, "Архітектурно машина чиста. Але крок 2 уже змінив КЕШ — і його не відкотили.",
                  size=12, color=INK, anchor="start"))

    # ── проба кешу: один рядок «теплий», решта «холодні» ──
    py = yr + 58
    p.append(text(lx, py - 6, "Тепер зловмисник міряє час доступу до кожного рядка probe[k · 256]:",
                  size=12, color=INK, bold=True, anchor="start"))
    cx0, cw, n = lx + 6, 88, 8
    hot = 5  # припустимо s = 5
    for k in range(n):
        x = cx0 + k * cw
        warm = (k == hot)
        fc, sc = (C_WORK, S_WORK) if warm else (C_WAIT, S_WAIT)
        p.append(rect(x, py + 8, cw - 10, 40, fill=fc, stroke=sc, sw=1.5, rx=5))
        p.append(text(x + (cw - 10) / 2, py + 26, "k=%d" % k, size=10, color=sc, bold=True))
        p.append(text(x + (cw - 10) / 2, py + 42,
                      "швидко" if warm else "повільно", size=9,
                      color=sc, bold=warm))
    p.append(text(cx0 + hot * cw + (cw - 10) / 2, py + 66, "↑ цей — у кеші", size=10, color=FIELD, bold=True))
    p.append(text(cx0 + hot * cw + (cw - 10) / 2, py + 82, "отже s = 5", size=11, color=FIELD, bold=True))
    return render(os.path.join(OUT, "cache-trace.svg"), W, H, *p)


# ── 5. Meltdown vs Spectre: два різні обмани того самого двигуна ───────────────
def fig_meltdown_vs_spectre():
    W, H = 800, 340
    p = [text(W / 2, 28, "Одна апаратура — два різні обмани", size=16, bold=True)]

    # ліва панель: Meltdown
    lx, lw = 40, 350
    p.append(rect(lx, 56, lw, 250, fill=C_LOAD, stroke=S_LOAD, sw=1.6, rx=10))
    p.append(text(lx + lw / 2, 82, "MELTDOWN", size=15, color=S_LOAD, bold=True))
    p.append(text(lx + lw / 2, 100, "проламує МЕЖУ ПРИВІЛЕЇВ", size=11, color=INK, bold=True))
    p.append(mtext(lx + 18, 130, (
        "Своя ж команда читає чужу\n"
        "(ядрову) пам'ять. Заборона є,\n"
        "але перевірка прав спізнюється —\n"
        "виконання встигає скористатися\n"
        "забороненим байтом наперед."), size=11, color=INK, anchor="start", lh=1.32))
    p.append(text(lx + 18, 250, "Обман: гонка «прочитав ⟷ заборонили».", size=10, color=MUTED, anchor="start"))
    p.append(text(lx + 18, 268, "Лік: розвести адреси ядра й програми", size=10, color=FIELD, anchor="start"))
    p.append(text(lx + 18, 284, "(KPTI) — читати нема чого.", size=10, color=FIELD, anchor="start"))

    # права панель: Spectre
    rx, rw = 410, 350
    p.append(rect(rx, 56, rw, 250, fill=C_BLOCK, stroke=S_BLOCK, sw=1.6, rx=10))
    p.append(text(rx + rw / 2, 82, "SPECTRE", size=15, color=S_BLOCK, bold=True))
    p.append(text(rx + rw / 2, 100, "обманює ПЕРЕДБАЧЕННЯ ПЕРЕХОДІВ", size=11, color=INK, bold=True))
    p.append(mtext(rx + 18, 130, (
        "Жертву намовляють саму\n"
        "стрибнути «не туди»: наперед\n"
        "натреновують передбачувач,\n"
        "щоб вона спекулятивно прочитала\n"
        "власну ж пам'ять поза межами."), size=11, color=INK, anchor="start", lh=1.32))
    p.append(text(rx + 18, 250, "Обман: отруєний передбачувач переходу.", size=10, color=MUTED, anchor="start"))
    p.append(text(rx + 18, 268, "Лік: точкові бар'єри в коді (lfence,", size=10, color=FIELD, anchor="start"))
    p.append(text(rx + 18, 284, "retpoline) — важче, дорожче.", size=10, color=FIELD, anchor="start"))

    # спільний низ
    p.append(text(W / 2, 326, "Спільне серце обох — слід у кеші від роботи, якої «не було».",
                  size=11, color=INK, italic=True))
    return render(os.path.join(OUT, "meltdown-vs-spectre.svg"), W, H, *p)


if __name__ == "__main__":
    fig_in_order_vs_ooo()
    fig_renaming()
    fig_ooo_pipeline()
    fig_cache_trace()
    fig_meltdown_vs_spectre()
    print("figures written to", OUT)
