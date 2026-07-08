# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Анатомія патерну: чотири частини картки ──────────────────────────────
def fig_anatomy():
    W, H = 760, 430
    frags = []
    frags.append(text(W/2, 30, "Патерн — це не код, а картка з чотирьох частин", size=17, bold=True))

    # чотири горизонтальні смуги
    rows = [
        ("НАЗВА", "спільне слово, яким команда називає рішення", "«Стратегія»", FIELD),
        ("ЗАДАЧА + СИЛИ", "яка проблема і які суперечливі вимоги тиснуть", "поведінка мусить мінятися на льоту", MUTED),
        ("РОЗВ'ЯЗОК", "як розставити ролі об'єктів, щоб сили погодити", "винести дію в окремий об'єкт, що підставляється", INK),
        ("НАСЛІДКИ", "що виграв і чим за це заплатив", "гнучкість ↑, але класів більше", POS),
    ]
    x = 60
    w = W - 120
    y = 58
    rh = 78
    gap = 12
    for title, desc, ex, col in rows:
        frags.append(rect(x, y, w, rh, fill="#f4f6f8", stroke=col, sw=2, rx=8))
        frags.append(text(x + 18, y + 26, title, size=14, color=col, anchor="start", bold=True))
        frags.append(text(x + 18, y + 48, desc, size=12.5, color=INK, anchor="start"))
        frags.append(text(x + w - 18, y + 62, ex, size=12, color=MUTED, anchor="end", italic=True))
        y += rh + gap

    render(os.path.join(OUT, 'pattern-anatomy.svg'), W, H, *frags)


# ── 2a. Сили сходяться: дві не пов'язані задачі → одна форма ─────────────────
def fig_forces():
    W, H = 780, 420
    frags = []
    frags.append(text(W/2, 30, "Однакові сили → однакова форма рішення", size=17, bold=True))

    # дві задачі зверху
    tasks = [
        ("Ворог у грі", "манера бою\nмусить мінятися", 60),
        ("Стиснення файлів", "алгоритм стиснення\nмусить мінятися", 470),
    ]
    tw = 250
    ty = 58
    for title, desc, x in tasks:
        frags.append(rect(x, ty, tw, 70, fill="#f4f6f8", stroke=INK, sw=2, rx=8))
        frags.append(text(x + tw/2, ty + 26, title, size=14, color=INK, bold=True))
        dl = desc.split("\n")
        dy = ty + 44
        for ln in dl:
            frags.append(text(x + tw/2, dy, ln, size=12, color=MUTED))
            dy += 15

    # спільні сили посередині
    fx = W/2 - 150
    fy = 175
    frags.append(rect(fx, fy, 300, 92, fill="#eafaf0", stroke=FIELD, sw=2.5, rx=10))
    frags.append(text(W/2, fy + 24, "СПІЛЬНІ СИЛИ", size=13, color=FIELD, bold=True))
    forces = ["поведінка змінна", "не вшивати намертво", "вибір під час роботи"]
    fyy = fy + 46
    for f in forces:
        frags.append(text(W/2, fyy, "• " + f, size=12.5, color=INK))
        fyy += 17

    # стрілки від задач до сил
    frags.append(arrow(60 + tw/2, ty + 70, W/2 - 60, fy + 4, color=MUTED, sw=1.8))
    frags.append(arrow(470 + tw/2, ty + 70, W/2 + 60, fy + 4, color=MUTED, sw=1.8))

    # одна форма знизу
    sx = W/2 - 200
    sy = 315
    frags.append(rect(sx, sy, 400, 66, fill="#f4f6f8", stroke=POS, sw=2.5, rx=10))
    frags.append(text(W/2, sy + 27, "ОДНА ФОРМА: патерн «Стратегія»", size=14, color=POS, bold=True))
    frags.append(text(W/2, sy + 49, "винести змінну поведінку в окремий підставний об'єкт",
                      size=12.5, color=INK))
    frags.append(arrow(W/2, fy + 92, W/2, sy, color=MUTED, sw=1.8))

    render(os.path.join(OUT, 'forces-converge.svg'), W, H, *frags)


# ── 2b. Три родини GoF ──────────────────────────────────────────────────────
def fig_families():
    W, H = 820, 400
    frags = []
    frags.append(text(W/2, 30, "23 патерни GoF — за питанням, на яке вони відповідають", size=17, bold=True))

    cols = [
        ("ПОРОДЖУВАЛЬНІ", "як СТВОРИТИ об'єкт,\nне прибиваючи цвяхами\nконкретний клас",
         ["Фабричний метод", "Будівельник", "Сінглтон", "Пул об'єктів"], FIELD, 60),
        ("СТРУКТУРНІ", "як СКЛАСТИ об'єкти\nв більшу форму,\nне зрощуючи їх намертво",
         ["Адаптер", "Декоратор", "Фасад", "Проксі"], NEG, 300),
        ("ПОВЕДІНКОВІ", "як РОЗПОДІЛИТИ обов'язки\nй хід дій\nміж об'єктами",
         ["Стратегія", "Спостерігач", "Команда", "Стан"], POS, 540),
    ]
    cw = 220
    top = 56
    for title, q, members, col, x in cols:
        # заголовок родини
        frags.append(rect(x, top, cw, 40, fill="#f4f6f8", stroke=col, sw=2.5, rx=8))
        frags.append(text(x + cw/2, top + 26, title, size=14, color=col, bold=True))
        # питання
        qlines = q.split("\n")
        qy = top + 66
        for ln in qlines:
            frags.append(text(x + cw/2, qy, ln, size=12, color=MUTED))
            qy += 17
        # члени
        my = qy + 12
        for m in members:
            frags.append(rect(x + 14, my, cw - 28, 30, fill=BG, stroke=col, sw=1.3, rx=6))
            frags.append(text(x + cw/2, my + 20, m, size=12.5, color=INK))
            my += 38

    render(os.path.join(OUT, 'gof-families.svg'), W, H, *frags)


# ── 3. Патерн ↔ антипатерн як дзеркало ──────────────────────────────────────
def fig_mirror():
    W, H = 780, 360
    frags = []
    frags.append(text(W/2, 30, "Патерн і антипатерн описують ту саму ситуацію", size=17, bold=True))

    # ліворуч — патерн
    lx = 50
    lw = 300
    frags.append(rect(lx, 64, lw, 250, fill="#eafaf0", stroke=FIELD, sw=2.5, rx=10))
    frags.append(text(lx + lw/2, 92, "ПАТЕРН", size=15, color=FIELD, bold=True))
    frags.append(text(lx + lw/2, 112, "перевірене хороше рішення", size=12, color=MUTED, italic=True))
    good = [
        "задача повторювана →",
        "рішення веде до цілі →",
        "наслідки названо чесно →",
        "далі стає легше міняти",
    ]
    gy = 150
    for g in good:
        frags.append(text(lx + lw/2, gy, g, size=13, color=INK))
        gy += 40

    # праворуч — антипатерн
    rx = W - 50 - lw
    frags.append(rect(rx, 64, lw, 250, fill="#fdecea", stroke=POS, sw=2.5, rx=10))
    frags.append(text(rx + lw/2, 92, "АНТИПАТЕРН", size=15, color=POS, bold=True))
    frags.append(text(rx + lw/2, 112, "теж повторюване, але шкодить", size=12, color=MUTED, italic=True))
    bad = [
        "задача повторювана →",
        "рішення на вигляд рятує →",
        "справжню ціну сховано →",
        "далі стає лише гірше",
    ]
    by = 150
    for b in bad:
        frags.append(text(rx + lw/2, by, b, size=13, color=INK))
        by += 40

    # дзеркальна вісь
    frags.append(line(W/2, 70, W/2, 308, color=MUTED, sw=1.2, dash="5 5"))
    frags.append(text(W/2, 335, "різниця не в частоті, а в тому, куди рішення веде систему з часом",
                      size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'pattern-antipattern.svg'), W, H, *frags)


# ── 4. Список проти мови: головний здогад Александера ───────────────────────
def fig_list_vs_language():
    W, H = 860, 470
    frags = []
    frags.append(text(W/2, 30, "Здогад Александера: не список порад, а мова", size=17, bold=True))

    # ── ЛІВОРУЧ: мертвий список — три однакові непов'язані картки ──
    lcx = 205
    frags.append(text(lcx, 66, "СПИСОК", size=14, color=MUTED, bold=True))
    frags.append(text(lcx, 86, "окремі поради, знати кожну", size=11.5, color=MUTED, italic=True))
    cards = ["порада про світло", "порада про вхід", "порада про стелю"]
    cy = 116
    for c in cards:
        frags.append(rect(lcx - 130, cy, 260, 46, fill=FILL, stroke=MUTED, sw=1.6, rx=8))
        frags.append(text(lcx, cy + 28, c, size=12.5, color=INK))
        cy += 66
    # немає стрілок — у тому й суть

    # роздільна вісь
    frags.append(line(W/2, 60, W/2, 430, color=MUTED, sw=1.2, dash="5 5"))

    # ── ПРАВОРУЧ: мова — дерево масштабів, з'єднане стрілками ──
    rcx = 640
    frags.append(text(rcx, 66, "МОВА", size=14, color=FIELD, bold=True))
    frags.append(text(rcx, 86, "менші складаються у більші", size=11.5, color=MUTED, italic=True))
    # вузли зверху вниз: місто → район → будинок → кімната → вікно
    nodes = [
        ("місто", 116),
        ("район", 178),
        ("будинок", 240),
        ("кімната", 302),
        ("вікно", 364),
    ]
    nw = 176
    for label, ny in nodes:
        frags.append(rect(rcx - nw/2, ny, nw, 40, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
        frags.append(text(rcx, ny + 25, label, size=13, color=INK, bold=True))
    # стрілки згори вниз між сусідніми вузлами (більше «розкладається на» менше)
    for i in range(len(nodes) - 1):
        y1 = nodes[i][1] + 40
        y2 = nodes[i + 1][1]
        frags.append(arrow(rcx, y1, rcx, y2, color=FIELD, sw=1.8))
    frags.append(text(rcx + nw/2 + 20, 240, "кожен масштаб —", size=11, color=MUTED, anchor="start"))
    frags.append(text(rcx + nw/2 + 20, 256, "патерн, що входить", size=11, color=MUTED, anchor="start"))
    frags.append(text(rcx + nw/2 + 20, 272, "у більший", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'list-vs-language.svg'), W, H, *frags)


# ── 5. Перенос форми: той самий кістяк для будинку й коду ────────────────────
def fig_alexander_to_gof():
    W, H = 900, 430
    frags = []
    frags.append(text(W/2, 30, "Перенесли не поради — форму запису патерну", size=17, bold=True))

    lx = 40          # ліва картка (архітектура)
    rx = W - 40 - 300  # права картка (код)
    cw = 300
    top = 58
    frags.append(rect(lx, top, cw, 36, fill="#f4f6f8", stroke=NEG, sw=2.2, rx=8))
    frags.append(text(lx + cw/2, top + 24, "Александер · «Світло з двох боків»", size=12.5, color=NEG, bold=True))
    frags.append(rect(rx, top, cw, 36, fill="#f4f6f8", stroke=POS, sw=2.2, rx=8))
    frags.append(text(rx + cw/2, top + 24, "Банда чотирьох · «Стратегія»", size=12.5, color=POS, bold=True))

    # три рядки-відповідники з містком посередині
    rows = [
        ("КОНТЕКСТ", "кімната в будинку", "об'єкт зі змінною поведінкою"),
        ("СИЛИ", "м'яке світло з кількох боків,\nале вікна коштують", "мінятися, не переписуючи\nвласника, під час роботи"),
        ("РОЗВ'ЯЗОК", "вікна у дві зовнішні стіни", "винести поведінку\nв підставний об'єкт"),
    ]
    ry = 112
    rh = 92
    gap = 8
    midw = 118
    for tag, left, right in rows:
        # ліва клітина
        frags.append(fitbox(lx, ry, cw, rh, left, size=12.5, pad=10,
                            fill=BG, stroke=NEG, sw=1.4, rx=8, color=INK))
        # права клітина
        frags.append(fitbox(rx, ry, cw, rh, right, size=12.5, pad=10,
                            fill=BG, stroke=POS, sw=1.4, rx=8, color=INK))
        # містковий ярлик посередині
        mx = W/2 - midw/2
        frags.append(rect(mx, ry + rh/2 - 17, midw, 34, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=17))
        frags.append(text(W/2, ry + rh/2 + 5, tag, size=12, color=MUTED, bold=True))
        # двобічні стрілки від картки до ярлика
        frags.append(arrow(lx + cw, ry + rh/2, mx, ry + rh/2, color=MUTED, sw=1.5))
        frags.append(arrow(rx, ry + rh/2, mx + midw, ry + rh/2, color=MUTED, sw=1.5))
        ry += rh + gap

    frags.append(text(W/2, ry + 16, "та сама кістка — змінилися лише іменники",
                      size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'alexander-to-gof.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_anatomy()
    fig_forces()
    fig_families()
    fig_mirror()
    fig_list_vs_language()
    fig_alexander_to_gof()
    print("figures written to", OUT)
