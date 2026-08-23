# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір сховища під задачу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_storage_map():
    """Реляційне за замовчуванням у центрі; п'ять НАЗВАНИХ тисків розводять
    до п'яти родин. Спершу дефолт — родину бере лише той тиск, що назвався."""
    W, H = 1200, 560
    frags = []

    spine_x = 452
    rows_y = [118, 214, 310, 406, 502]

    # ── якір: реляційне за замовчуванням ──
    b, _, _ = textbox(196, 310,
                      "Реляційне\nза замовчуванням\n———\nлишайся, поки\nне названо тиск",
                      size=13, fill="#eafaf0", stroke=FIELD, min_w=228, bold=False)
    frags.append(b)
    frags.append(arrow(310, 310, spine_x, 310, color=FIELD, sw=2))

    # вертикальний хребет, з якого розходяться п'ять доріжок
    frags.append(line(spine_x, rows_y[0], spine_x, rows_y[-1], color=MUTED, sw=1.6))

    # ── п'ять рядків: тиск → родина ──
    rows = [
        ("гарячий пошук за ключем,\nточковий, мілісекунди",
         "Ключ-значення"),
        ("завжди береш цілий\nсамодостатній документ;\nсхема гуляє",
         "Документне"),
        ("потік append-only вимірів;\nчитання — діапазони й агрегати",
         "Часові ряди /\nширока колонка"),
        ("питання про зв'язки\nй обходи (друзі друзів)",
         "Графове"),
        ("вільний текст\nіз ранжуванням",
         "Пошуковий індекс"),
    ]
    press_cx, fam_cx = 720, 1058
    for (press, fam), y in zip(rows, rows_y):
        pb, pw, _ = textbox(press_cx, y, press, size=11.5, fill=BG,
                            stroke=MUTED, min_w=300)
        fb, fw, _ = textbox(fam_cx, y, fam, size=13, fill="#eef2fb",
                            stroke=NEG, min_w=176)
        # хребет → тиск
        frags.append(arrow(spine_x, y, press_cx - pw / 2 - 4, y, color=MUTED, sw=1.5))
        # тиск → родина
        frags.append(arrow(press_cx + pw / 2 + 4, y, fam_cx - fw / 2 - 4, y,
                           color=NEG, sw=1.7))
        frags.append(pb)
        frags.append(fb)

    frags.append(text(720, 542, "названий тиск", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "storage-map.svg"), W, H, *frags,
           title="Родину бере той тиск, що назвався; решту тримає дефолт")


def fig_backbone_vs_sprawl():
    """Ліворуч — дисципліна: хребет + один супутник + кеш за швами.
    Праворуч — розсип: сховище на кожну задачу = стільки ж операційних поверхонь."""
    W, H = 1200, 600
    frags = []

    # розділювач панелей
    frags.append(line(600, 60, 600, 566, color=MUTED, sw=1, dash="4,5"))
    frags.append(text(300, 70, "Дисципліна: хребет + супутник", size=15, bold=True))
    frags.append(text(900, 70, "Розсип: сховище на кожну задачу", size=15, bold=True))

    # ── ЛІВА панель ──
    b, _, _ = textbox(300, 118, "застосунок DH", size=12.5, fill="#eef2fb",
                      stroke=NEG, min_w=200)
    frags.append(b)
    # шов
    frags.append(rect(96, 150, 408, 34, fill="#f4f6f8", stroke=LINE, sw=1.4))
    frags.append(text(300, 172, "репозиторії — один шов на кожне сховище",
                      size=12, color=MUTED))
    frags.append(arrow(300, 138, 300, 150, color=MUTED, sw=1.5))

    # хребет
    b, _, _ = textbox(230, 288,
                      "Реляційний ХРЕБЕТ\n———\nреєстр · аудит\nтвін-таблиця · пошук (FTS)",
                      size=12.5, fill="#eafaf0", stroke=FIELD, min_w=232)
    frags.append(b)
    # супутник
    b, _, _ = textbox(430, 260, "Часові ряди\n(телеметрія)", size=12,
                      fill="#eef2fb", stroke=NEG, min_w=150)
    frags.append(b)
    # кеш
    b, _, _ = textbox(430, 348, "Кеш\n(гарячий твін)", size=12,
                      fill="#fdf4e8", stroke="#b8791f", min_w=150)
    frags.append(b)
    frags.append(arrow(300, 190, 250, 250, color=LINE, sw=1.5))
    frags.append(arrow(360, 190, 425, 232, color=LINE, sw=1.5))

    b, _, _ = textbox(300, 470,
                      "2 сховища + кеш\nстільки ж бекапів, моніторингу,\nтреба лагодити консистентність",
                      size=12, fill=BG, stroke=FIELD, min_w=320)
    frags.append(b)

    # ── ПРАВА панель ──
    b, _, _ = textbox(900, 118, "застосунок DH", size=12.5, fill="#eef2fb",
                      stroke=NEG, min_w=200)
    frags.append(b)
    frags.append(rect(690, 150, 420, 34, fill="#f4f6f8", stroke=LINE, sw=1.4))
    frags.append(text(900, 172, "шість швів — по одному на сховище",
                      size=12, color=MUTED))
    frags.append(arrow(900, 138, 900, 150, color=MUTED, sw=1.5))

    stores = ["реєстр:\nSQL", "телеметрія:\nTSDB", "твін:\nKV",
              "аудит:\nжурнал", "пошук:\nіндекс", "правила:\nдокумент"]
    gx = [772, 900, 1028]
    gy = [252, 344]
    for i, name in enumerate(stores):
        cx = gx[i % 3]
        cy = gy[i // 3]
        b, _, _ = textbox(cx, cy, name, size=11.5, fill="#fbeef0",
                          stroke=POS, min_w=112)
        frags.append(b)
        if cx == 900 and cy == gy[1]:
            # середня колонка другого ряду: пряма від вершини йшла б крізь
            # напис середньої колонки першого ряду — обходимо його праворуч
            frags.append(line(900, 190, 950, 233, color=MUTED, sw=1, dash="3,4"))
            frags.append(line(950, 233, 950, 300, color=MUTED, sw=1, dash="3,4"))
            frags.append(line(950, 300, cx, cy - 26, color=MUTED, sw=1, dash="3,4"))
        else:
            frags.append(line(900, 190, cx, cy - 26, color=MUTED, sw=1, dash="3,4"))

    b, _, _ = textbox(900, 470,
                      "6 сховищ = 6× операційна поверхня\n———\nшість бекапів, шість дашбордів,\nп'ятнадцять пар «між чим і чим»",
                      size=12, fill=BG, stroke=POS, min_w=344)
    frags.append(b)

    render(os.path.join(IMG, "backbone-vs-sprawl.svg"), W, H, *frags,
           title="Та сама задача: хребет із супутником проти розсипу сховищ")


def fig_nosql_pendulum():
    """Дуга маятника в часі: наскільки настрій індустрії відходив від
    реляційного дефолту. Хибний старт 1998 → тиск папери 2006–07 → гештег 2009
    → пік «реляційне померло» 2011–12 → Postgres ковтає JSONB 2014 → boring
    technology 2015 → рівновага «нудний дефолт + супутник за тиском». Осідає
    ВИЩЕ наївного дому — полиглот лишають там, де тиск справжній."""
    W, H = 1220, 600
    frags = []

    base_y = 500          # «дім»: реляційний дефолт
    x0, x1 = 120, 1100

    # ── вісь-дім і підпис ──
    frags.append(line(x0, base_y, x1, base_y, color=FIELD, sw=2))
    frags.append(text(x0 + 6, base_y + 24, "реляційний дефолт («дім»)",
                      size=12.5, color=FIELD, anchor="start", italic=True))
    # напрям осі «далі від дому»
    frags.append(arrow(x0, base_y, x0, 96, color=MUTED, sw=1.4))
    frags.append(text(x0 - 6, 92, "далі від реляційного дефолту", size=11.5,
                      color=MUTED, anchor="start", italic=True))

    # ── віхи: (x, y_кривої, колір_точки, підпис, (lx, ly)) ──
    stops = [
        (130, 476, FIELD, "1998\nStrozzi вжив назву",        (172, 430)),
        (355, 402, MUTED, "2006–07\nпапери BigTable / Dynamo", (355, 344)),
        (505, 300, POS,   "2009\nгештег #nosql",             (470, 244)),
        (655, 168, POS,   "2011–12\n«реляційне померло»",     (655, 112)),
        (805, 262, NEG,   "2014\nPostgres ковтає JSONB",      (860, 205)),
        (900, 336, NEG,   "2015\n«boring technology»",        (955, 300)),
        (1065, 414, FIELD, "2020-і\nдефолт + супутник\nза тиском", (998, 446)),
    ]

    # крива — ламана через точки (траєкторія маятника)
    for a, b in zip(stops, stops[1:]):
        frags.append(line(a[0], a[1], b[0], b[1], color=INK, sw=2.4))

    # точки + підписи з тонким лідером
    for x, y, col, lab, (lx, ly) in stops:
        frags.append(line(x, y, lx, ly + 9, color=MUTED, sw=0.9, dash="2,4"))
        frags.append(circle(x, y, 7, fill=col, stroke=BG, sw=2))
        frags.append(mtext(lx, ly, lab, size=12, color=INK))

    # позначка піку й рівноваги (осторонь від лідера підпису «2011-12», що йде вертикально по x=655)
    frags.append(text(600, 150, "пік", size=11.5, color=POS, italic=True))
    frags.append(line(1065, 414, 1065, base_y, color=NEG, sw=1, dash="3,4"))
    frags.append(mtext(1088, 434, "осідає вище\nнаївного дому", size=10.5,
                       color=NEG, anchor="start"))

    render(os.path.join(IMG, "nosql-pendulum.svg"), W, H, *frags,
           title="Маятник NoSQL: відхід від реляційного дефолту і повернення")


def fig_twin_vs_raw():
    """Та сама відповідь «поточний стан», дві форми доступу.
    Червона крива — DISTINCT ON по сирій телеметрії: робота росте з історією.
    Зелена лінія — GET матеріалізованого твіна за ключем: пласка, байдужа до історії."""
    W, H = 1000, 540
    frags = []

    ox, oy = 150, 450          # початок координат
    x_end, y_top = 920, 100

    # осі
    frags.append(arrow(ox, oy, x_end, oy, color=MUTED, sw=1.8))
    frags.append(arrow(ox, oy, ox, y_top, color=MUTED, sw=1.8))
    frags.append(text(540, 492, "розмір історії телеметрії  →", size=13, color=MUTED))
    frags.append(text(150, 78, "робота на один запит поточного стану", size=13, color=MUTED))

    # зелена лінія: матеріалізований твін — GET за ключем, майже пласко
    frags.append(line(ox, 432, 910, 426, color=FIELD, sw=3))
    frags.append(circle(910, 426, 6, fill="#eafaf0", stroke=FIELD, sw=2))

    # червона крива: реконструкція з сирої (DISTINCT ON) — росте з історією
    pts = [(150, 432), (250, 416), (360, 388), (480, 348),
           (610, 296), (760, 220), (910, 116)]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        frags.append(line(x1, y1, x2, y2, color=POS, sw=3))
    frags.append(circle(910, 116, 6, fill="#fdecea", stroke=POS, sw=2))

    # підписи (у порожніх зонах, повз лінії)
    b, _, _ = textbox(350, 152,
                      "реконструкція з сирої:\nDISTINCT ON —\nробота росте з історією",
                      size=12, fill=BG, stroke=POS, min_w=300)
    frags.append(b)
    b, _, _ = textbox(712, 392,
                      "матеріалізований твін:\nGET за ключем — пласко",
                      size=12, fill=BG, stroke=FIELD, min_w=300)
    frags.append(b)

    render(os.path.join(IMG, "twin-vs-raw.svg"), W, H, *frags,
           title="Та сама відповідь, дві ціни: копати з-під історії проти GET за ключем")


if __name__ == "__main__":
    fig_storage_map()
    fig_backbone_vs_sprawl()
    fig_nosql_pendulum()
    fig_twin_vs_raw()
    print("OK: storage-map.svg, backbone-vs-sprawl.svg, nosql-pendulum.svg, twin-vs-raw.svg")
