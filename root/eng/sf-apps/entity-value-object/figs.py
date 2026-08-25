# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_identity_vs_value():
    """Дві колонки: об'єкт-значення (однакові = взаємозамінні) проти сутності
    (однакові на вигляд, але дві різні через окрему тотожність)."""
    W, H = 720, 430
    frags = []
    frags.append(text(W / 2, 30, "Два питання про однаковість", size=18, bold=True))

    # ── ліва колонка: об'єкт-значення ──
    lx = 185
    frags.append(text(lx, 66, "Об'єкт-значення", size=15, bold=True, color=FIELD))
    frags.append(text(lx, 88, "«що це» — важать лише атрибути", size=12, color=MUTED))

    b, bw, bh = textbox(lx - 70, 150, "100 грн\nсерія AB\n№ 774521", size=13, fill="#eafaf1", stroke=FIELD)
    frags.append(b)
    b, bw, bh = textbox(lx + 70, 150, "100 грн\nсерія AB\n№ 774521", size=13, fill="#eafaf1", stroke=FIELD)
    frags.append(b)
    frags.append(text(lx, 218, "= рівні", size=15, bold=True, color=FIELD))
    frags.append(text(lx, 244, "взаємозамінні: будь-яка", size=12, color=INK))
    frags.append(text(lx, 262, "згодиться замість іншої", size=12, color=INK))

    b, bw, bh = textbox(lx, 320, "заміни на новий об'єкт —\nнічого не зміниться", size=12,
                        fill="#f4f6f8", stroke=FIELD)
    frags.append(b)

    # роздільник
    frags.append(line(W / 2, 58, W / 2, H - 30, color="#c9ced6", sw=1.5, dash="5,5"))

    # ── права колонка: сутність ──
    rx = 535
    frags.append(text(rx, 66, "Сутність", size=15, bold=True, color=POS))
    frags.append(text(rx, 88, "«хто це» — важить тотожність", size=12, color=MUTED))

    b, bw, bh = textbox(rx - 70, 150, ["Іван Коваль", "id 4471", "борг 0 грн"], size=13,
                        fill="#fdeeec", stroke=POS)
    frags.append(b)
    b, bw, bh = textbox(rx + 70, 150, ["Іван Коваль", "id 9038", "борг 250 грн"], size=13,
                        fill="#fdeeec", stroke=POS)
    frags.append(b)
    frags.append(text(rx, 218, "≠ різні", size=15, bold=True, color=POS))
    frags.append(text(rx, 244, "однакове ім'я — та це", size=12, color=INK))
    frags.append(text(rx, 262, "дві окремі людини (id)", size=12, color=INK))

    b, bw, bh = textbox(rx, 320, "заміниш одного іншим —\nборг спишеться не тому", size=12,
                        fill="#f4f6f8", stroke=POS)
    frags.append(b)

    render(os.path.join(IMG, 'identity-vs-value.svg'), W, H, *frags)


def fig_equality():
    """Як рахується рівність: сутність — за id (поля можуть бути різні),
    об'єкт-значення — за всіма полями (id не існує)."""
    W, H = 720, 360
    frags = []
    frags.append(text(W / 2, 30, "Що означає «дорівнює» для кожного роду", size=18, bold=True))

    # ── сутність ──
    ey = 95
    frags.append(text(120, ey, "Сутність", size=15, bold=True, color=POS))
    b, w1, h1 = textbox(300, ey + 55, ["Замовлення", "id = 42", "сума 300 грн", "статус: новий"],
                        size=12, fill="#fdeeec", stroke=POS)
    frags.append(b)
    b, w2, h2 = textbox(300 + 220, ey + 55, ["Замовлення", "id = 42", "сума 320 грн", "статус: оплач."],
                        size=12, fill="#fdeeec", stroke=POS)
    frags.append(b)
    # знак рівності між ними
    frags.append(text(300 + 110, ey + 55, "=", size=22, bold=True, color=POS))
    frags.append(text(300 + 110, ey + 120, "той самий id → та сама річ,", size=12, color=INK))
    frags.append(text(300 + 110, ey + 138, "хоч поля й змінилися в часі", size=12, color=INK))

    frags.append(line(60, 250, W - 60, 250, color="#c9ced6", sw=1.5, dash="5,5"))

    # ── об'єкт-значення ──
    vy = 278
    frags.append(text(120, vy, "Значення", size=15, bold=True, color=FIELD))
    b, w3, h3 = textbox(300, vy + 30, ["Гроші", "300 грн"], size=12, fill="#eafaf1", stroke=FIELD)
    frags.append(b)
    b, w4, h4 = textbox(300 + 220, vy + 30, ["Гроші", "320 грн"], size=12, fill="#eafaf1", stroke=FIELD)
    frags.append(b)
    frags.append(text(300 + 110, vy + 30, "≠", size=22, bold=True, color=FIELD))
    frags.append(text(300 + 110, vy + 66, "id немає; відрізнилося поле — уже інше значення", size=12, color=INK))

    render(os.path.join(IMG, 'equality-rules.svg'), W, H, *frags)


def fig_lineage_timeline():
    """Родовід поняття: Whole Value (Каннінгем, 1994/95) → Value Object як патерн
    (Фаулер, P of EAA, 2002) → класифікація Entity/Value/Service (Еванс, DDD, 2003)."""
    W, H = 860, 360
    frags = []
    frags.append(text(W / 2, 32, "Родовід поділу на два роди", size=18, bold=True))

    # горизонтальна вісь часу
    axis_y = 150
    x0, x1 = 70, W - 60
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2))
    frags.append(arrow(x1 - 30, axis_y, x1, axis_y, color=INK, sw=2))
    frags.append(text(x1, axis_y - 12, "час", size=12, color=MUTED, anchor="end"))

    # чотири віхи; кожна — крапка на осі + рамка над/під
    marks = [
        (150, "1994–95", "«Whole Value»\nВорд Каннінгем\n(CHECKS, PLoP)",
         "маленький свій тип\nна число з сенсом:\nгроші, період", FIELD, "up"),
        (350, "2002", "«Value Object»\nМартін Фаулер\n(P of EAA, гл. 18)",
         "названо патерном:\nрівність не за\nтотожністю", NEG, "down"),
        (560, "2003", "Entity / Value /\nService\nЕрік Еванс (DDD)",
         "піднято до повної\nкласифікації родів\nу моделі", POS, "up"),
        (760, "згодом", "«Evans\nClassification»",
         "так Фаулер назвав\nтрійку Еванса", MUTED, "down"),
    ]
    for cx, year, top, bot, col, side in marks:
        frags.append(circle(cx, axis_y, 7, fill=col, stroke=INK, sw=1.5))
        if side == "up":
            b, w, h = textbox(cx, axis_y - 78, top, size=12, bold=True,
                              fill="#f4f6f8", stroke=col, color=INK)
            frags.append(b)
            frags.append(line(cx, axis_y - 8, cx, axis_y - 78 + h / 2, color=col, sw=1.2))
            frags.append(text(cx, axis_y + 26, year, size=13, bold=True, color=col))
            b, w, h = textbox(cx, axis_y + 78, bot, size=11, fill="#ffffff",
                              stroke="#c9ced6", color=MUTED)
            frags.append(b)
        else:
            b, w, h = textbox(cx, axis_y + 78, top, size=12, bold=True,
                              fill="#f4f6f8", stroke=col, color=INK)
            frags.append(b)
            frags.append(line(cx, axis_y + 8, cx, axis_y + 78 - h / 2, color=col, sw=1.2))
            frags.append(text(cx, axis_y - 22, year, size=13, bold=True, color=col))
            b, w, h = textbox(cx, axis_y - 78, bot, size=11, fill="#ffffff",
                              stroke="#c9ced6", color=MUTED)
            frags.append(b)

    render(os.path.join(IMG, 'lineage-timeline.svg'), W, H, *frags)


def fig_naming_clash():
    """Плутанина назв: одне слово «value object» тягли у два різні боки —
    маленьке незмінне значення (Фаулер/Еванс) vs пакунок даних для передачі (J2EE)."""
    W, H = 760, 330
    frags = []
    frags.append(text(W / 2, 32, "Одне слово — два різні значення", size=18, bold=True))

    # спільне слово посередині зверху
    b, w, h = textbox(W / 2, 78, "«value object»", size=15, bold=True,
                      fill="#fff7e6", stroke="#d9a441", color=INK)
    frags.append(b)

    # дві стрілки вниз, у різні боки
    lx, rx, ty = 190, 570, 150
    frags.append(arrow(W / 2 - 40, 96, lx, ty - 18, color=FIELD, sw=1.8))
    frags.append(arrow(W / 2 + 40, 96, rx, ty - 18, color=POS, sw=1.8))

    # ліворуч: значення домену
    frags.append(text(lx, ty, "спільнота патернів", size=13, bold=True, color=FIELD))
    b, w, h = textbox(lx, ty + 70,
                      "маленьке незмінне\nзначення домену:\nгроші, дата, колір\n\nрівність — за вмістом",
                      size=12, fill="#eafaf1", stroke=FIELD, color=INK)
    frags.append(b)

    # роздільник
    frags.append(line(W / 2, 130, W / 2, H - 28, color="#c9ced6", sw=1.5, dash="5,5"))

    # праворуч: пакунок для передачі
    frags.append(text(rx, ty, "рання J2EE-література", size=13, bold=True, color=POS))
    b, w, h = textbox(rx, ty + 70,
                      "пакунок полів, щоб\nодним махом переслати\nдані між рівнями\n\n(тепер — Transfer Object)",
                      size=12, fill="#fdeeec", stroke=POS, color=INK)
    frags.append(b)

    render(os.path.join(IMG, 'naming-clash.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_identity_vs_value()
    fig_equality()
    fig_lineage_timeline()
    fig_naming_clash()
    print("figs done")
