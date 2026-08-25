# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HEAD_FILL = "#e8edf3"
NULL_FILL = "#fdecea"
COLD_FILL = "#eaf0fd"
WARM_FILL = "#eafaf0"


# ── 1. Анатомія набору: схема + рядки + NULL + два способи доступу ────────────
def fig_anatomy():
    W, H = 1260, 480
    f = [text(W / 2, 32, "Що всередині набору рядків", size=17, bold=True)]

    x0 = 60
    widths = [100, 200, 150, 150]
    xs = [x0]
    for w in widths:
        xs.append(xs[-1] + w)
    x_end = xs[-1]

    head_y, head_h = 95, 50
    row_h = 42

    # ── схема (шапка) ──
    cols = [
        ("id", "int32 · not null"),
        ("customer_id", "text · not null"),
        ("total", "decimal · NULL"),
        ("status", "text · not null"),
    ]
    for i, (name, typ) in enumerate(cols):
        f.append(rect(xs[i], head_y, widths[i], head_h, fill=HEAD_FILL, stroke=LINE, sw=1.4, rx=0))
        f.append(text(xs[i] + widths[i] / 2, head_y + 21, name, size=12.5, bold=True))
        f.append(text(xs[i] + widths[i] / 2, head_y + 39, typ, size=10, color=MUTED))

    # ── рядки значень ──
    rows = [
        ("41", "ACME", "350.00", "paid"),
        ("42", "Borysfen", "1200.00", "paid"),
        ("43", "Cebra", None, "paid"),
        ("44", "Delta", "90.00", "shipped"),
    ]
    for r, vals in enumerate(rows):
        y = head_y + head_h + r * row_h
        for i, v in enumerate(vals):
            is_null = v is None
            f.append(rect(xs[i], y, widths[i], row_h,
                          fill=(NULL_FILL if is_null else BG), stroke=LINE, sw=1.1, rx=0))
            f.append(text(xs[i] + widths[i] / 2, y + row_h / 2 + 4,
                          "NULL" if is_null else v,
                          size=12, color=(POS if is_null else INK), bold=is_null))

    grid_bottom = head_y + head_h + len(rows) * row_h   # 313

    # ── пояснення праворуч, стрілки не заходять у сітку ──
    f.append(fitbox(700, 95, 540, 50,
                    "схема — з метаданих ЗАПИТУ, а не з таблиці:\n"
                    "колонки-вирази не існують у жодній таблиці",
                    size=12.5, fill=COLD_FILL, stroke=NEG))
    f.append(arrow(696, 120, 665, 120, color=NEG, sw=1.6))

    f.append(fitbox(700, 225, 540, 50,
                    "NULL — окремий стан комірки:\n"
                    "не нуль і не порожній рядок",
                    size=12.5, fill=NULL_FILL, stroke=POS))
    f.append(arrow(696, 250, 665, 250, color=POS, sw=1.6))

    # ── доступ до комірки, знизу ──
    f.append(fitbox(90, 370, 540, 76,
                    "до комірки — двома шляхами:\n"
                    "row[\"total\"] — за іменем, стійко до перестановки\n"
                    "row[2] — за номером, прямо в масив",
                    size=12.5, fill=WARM_FILL, stroke=FIELD))
    f.append(arrow(475, 366, 475, grid_bottom + 3, color=FIELD, sw=1.6))

    return render(os.path.join(OUT, "record-set-anatomy.svg"), W, H, *f)


# ── 2. Курсор проти відірваного набору: час утримання з'єднання ───────────────
def fig_connected_vs_disconnected():
    W, H = 1300, 460
    f = [text(W / 2, 32, "Скільки живе з'єднання: курсор проти відірваного набору",
              size=17, bold=True)]

    xa, xb = 180, 1000
    seg1, seg2 = 260, 860          # межі ділянок
    bar_h = 44

    def row(y, title, fills, labels, summary, summary_color):
        out = []
        out.append(fitbox(30, y - 8, 140, 60, title, size=12, fill=BG, stroke=MUTED))
        bounds = [xa, seg1, seg2, xb]
        for i in range(3):
            out.append(rect(bounds[i], y, bounds[i + 1] - bounds[i], bar_h,
                            fill=fills[i], stroke=LINE, sw=1.3, rx=0))
        # підписи ділянок — під смугою, кожен по центру своєї ділянки
        for i in range(3):
            cx = (bounds[i] + bounds[i + 1]) / 2
            out.append(mtext(cx, y + bar_h + 22, labels[i], size=11.5, color=MUTED))
        out.append(fitbox(1040, y - 12, 230, 68, summary, size=12,
                          fill=BG, stroke=summary_color, color=INK))
        return out

    # верх: курсор тримає з'єднання весь час
    f += row(110, "курсор\nтримає\nз'єднання",
             ["#d7dee7", "#d7dee7", "#d7dee7"],
             ["запит\n15 мс", "людина гортає сторінку: 2.5 с\nз'єднання зайняте", "закриття"],
             "20 з'єднань\nдають\n8 запитів/с", POS)
    f.append(text((xa + xb) / 2, 98, "з'єднання зайняте 2.5 с", size=12.5, color=POS, bold=True))

    # низ: набір відірвано
    f += row(290, "набір\nвідірвано",
             ["#d7dee7", BG, "#d7dee7"],
             ["читання\n15 мс", "робота з набором у пам'яті: бази не видно",
              "запис змін\n20 мс"],
             "20 з'єднань\nдають\n≈1330 запитів/с", FIELD)
    f.append(text((xa + xb) / 2, 278, "з'єднання зайняте 35 мс", size=12.5, color=FIELD, bold=True))

    f.append(text(W / 2, 420,
                  "ширина ділянок умовна: у справжньому масштабі 15 мс поряд із 2.5 с були б непомітні",
                  size=11.5, color=MUTED, italic=True))
    return render(os.path.join(OUT, "connected-vs-disconnected.svg"), W, H, *f)


# ── 3. Стани рядків → згенеровані оператори → перевірка конфлікту ─────────────
def fig_writeback():
    W, H = 1300, 640
    f = [text(W / 2, 32, "Зворотний запис: стан рядка стає оператором", size=17, bold=True)]

    f.append(text(250, 70, "набір після правок", size=13.5, bold=True, color=MUTED))
    f.append(text(920, 70, "що піде в базу", size=13.5, bold=True, color=MUTED))

    lx, lw = 60, 380
    rx, rw = 600, 640

    items = [
        (95, 58, "#f2f4f6", MUTED,
         "рядок 41 · незмінений\nstatus='paid'  total=350.00",
         "нічого не надсилаємо"),
        (170, 100, COLD_FILL, NEG,
         "рядок 42 · змінений\nбуло:  status='paid'  total=1200.00\nстало: status='review'",
         "UPDATE orders SET status = @status\n WHERE id = @id\n   AND status = @orig_status\n"
         "   AND total  = @orig_total"),
        (290, 58, WARM_FILL, FIELD,
         "рядок 45 · доданий\nstatus='new'  total=70.00",
         "INSERT INTO orders (customer_id, total, status)\nVALUES (@customer_id, @total, @status)"),
        (365, 78, NULL_FILL, POS,
         "рядок 43 · вилучений\nбуло: status='paid'  total=90.00",
         "DELETE FROM orders\n WHERE id = @id\n   AND status = @orig_status AND total = @orig_total"),
    ]
    for y, h, fill, stroke, left, right in items:
        f.append(fitbox(lx, y, lw, h, left, size=12, fill=fill, stroke=stroke))
        f.append(fitbox(rx, y, rw, h, right, size=11.5, fill=BG, stroke=stroke))
        f.append(arrow(lx + lw + 8, y + h / 2, rx - 8, y + h / 2, color=stroke, sw=1.6))

    f.append(text(520, 466, "обхід рядків при записі", size=12, color=MUTED, italic=True))

    # розгалуження за кількістю змінених рядків
    f.append(fitbox(160, 500, 460, 66,
                    "база повернула 1 змінений рядок\nпочаткові значення збіглися — успіх",
                    size=12.5, fill=WARM_FILL, stroke=FIELD))
    f.append(fitbox(700, 500, 460, 66,
                    "база повернула 0 змінених рядків\nхтось випередив — конфлікт",
                    size=12.5, fill=NULL_FILL, stroke=POS))
    f.append(text(W / 2, 604, "усі оператори — в одній транзакції",
                  size=12.5, color=MUTED, italic=True))
    return render(os.path.join(OUT, "writeback-states.svg"), W, H, *f)


# ── 4. Рядковий проти колонкового розкладу в пам'яті ──────────────────────────
def fig_layout():
    W, H = 1300, 470
    f = [text(W / 2, 32, "Той самий набір, два розклади в пам'яті", size=17, bold=True)]

    x0, x1 = 80, 1180
    n = 12
    cw = (x1 - x0) / n

    # ── рядковий ──
    f.append(text(x0, 88, "рядковий розклад", size=13.5, bold=True, anchor="start"))
    y = 110
    names = ["id", "cust", "total", "status"]
    for i in range(n):
        col = i % 4
        hot = (col == 2)
        f.append(rect(x0 + i * cw, y, cw, 44,
                      fill=(WARM_FILL if hot else BG), stroke=LINE, sw=1.1, rx=0))
        f.append(text(x0 + i * cw + cw / 2, y + 28, names[col],
                      size=11, color=(FIELD if hot else MUTED), bold=hot))
    for g in range(3):
        gx = x0 + g * 4 * cw
        f.append(text(gx + 2 * cw, y - 10, "рядок %d" % (41 + g), size=11.5, color=INK))
        f.append(rect(gx, y, 4 * cw, 44, fill="none", stroke=INK, sw=2.2, rx=0))
    f.append(text(W / 2, 200,
                  "сума колонки total читає кожну четверту комірку — решта лінії кеша марна",
                  size=12, color=MUTED))

    # ── колонковий ──
    f.append(text(x0, 268, "колонковий розклад", size=13.5, bold=True, anchor="start"))
    y = 290
    for g, name in enumerate(names):
        hot = (g == 2)
        gx = x0 + g * 3 * cw
        for k in range(3):
            f.append(rect(gx + k * cw, y, cw, 44,
                          fill=(WARM_FILL if hot else BG), stroke=LINE, sw=1.1, rx=0))
            f.append(text(gx + k * cw + cw / 2, y + 28, name,
                          size=11, color=(FIELD if hot else MUTED), bold=hot))
        f.append(text(gx + 1.5 * cw, y - 10, "колонка %s" % name, size=11.5, color=INK))
        f.append(rect(gx, y, 3 * cw, 44, fill="none", stroke=INK, sw=2.2, rx=0))
    f.append(text(W / 2, 380,
                  "сума колонки total читає суцільний масив чисел — уся лінія кеша корисна",
                  size=12, color=MUTED))

    f.append(fitbox(120, 402, 480, 48,
                    "рядковому дешево додати й вилучити рядок",
                    size=12.5, fill=BG, stroke=MUTED))
    f.append(fitbox(700, 402, 480, 48,
                    "колонковому дешево пройти колонку й легше важити",
                    size=12.5, fill=BG, stroke=MUTED))
    return render(os.path.join(OUT, "row-vs-column-layout.svg"), W, H, *f)


# ── 5. Родовід форми: що кожен крок дописав до набору ─────────────────────────
def fig_lineage():
    rows = [
        ("1980", "dBASE II · формат DBF",
         "файлова база на одному робочому місці: сервера немає, відривати нема від чого",
         "у заголовку файлу — опис полів: ім'я, тип, довжина. Таблиця описує себе сама"),
        ("1991—1995", "DataWindow · VB3 · Delphi 1",
         "сітку на екрані не напишеш під кожну таблицю — вона мусить спитати дані про колонки",
         "схема живе в самому результаті; рух по рядках в обидва боки, а не лише вперед"),
        ("1996—1998", "ADC/RDS · ADO Recordset",
         "багатоланковий застосунок і браузер: у клієнта з'єднання немає взагалі",
         "від'єднаність як РЕЖИМ курсора: CursorLocation = adUseClient, потім ActiveConnection = Nothing"),
        ("1998", "пакетні правки в ADO",
         "набір відірвано — негайний UPDATE слати нікуди, а рядок тим часом могли змінити",
         "стан рядка (незмінений / змінений / доданий / вилучений) і початкові значення полів"),
        ("1997—2004", "JDBC ResultSet → CachedRowSet",
         "та сама біда в Java, але перша відповідь інша — збагатити курсор, а не відривати його",
         "прокрутка й правка в курсорі (1998); від'єднаний RowSet — окремим інтерфейсом, реалізації аж 2004"),
        ("2002", "ADO.NET DataSet",
         "режим вимагав питати про об'єкт «а ти ще тримаєш з'єднання?» під час виконання",
         "від'єднаність стала ТИПОМ: кілька таблиць, зв'язки між ними, запис себе в XML"),
        ("2002", "каталог PoEAA",
         "у чотирьох платформ — чотири назви для однієї речі",
         "спільне ім'я: набір рядків — подання табличних даних у пам'яті"),
    ]

    W = 1240
    top, step, box_h = 96, 96, 74
    H = top + len(rows) * step + 40
    f = [text(W / 2, 34, "Родовід набору рядків: що кожен крок дописав до форми",
              size=17, bold=True)]

    axis_x = 300
    y_first = top + box_h / 2
    y_last = top + (len(rows) - 1) * step + box_h / 2
    f.append(line(axis_x, y_first - 34, axis_x, y_last + 34, color=MUTED, sw=2))

    for i, (when, what, why, added) in enumerate(rows):
        y = top + i * step
        f.append(fitbox(40, y, 226, box_h, when + "\n" + what,
                        size=12.5, fill=HEAD_FILL, stroke=LINE))
        f.append(circle(axis_x, y + box_h / 2, 7, fill=BG, stroke=MUTED, sw=2))
        f.append(fitbox(334, y, 866, box_h,
                        "змусило: " + why + "\nдодалося: " + added,
                        size=12, fill=BG, stroke=(FIELD if i % 2 else NEG)))

    return render(os.path.join(OUT, "record-set-lineage.svg"), W, H, *f)


# ── 6. Що саме лежить у пам'яті колонкового набору ───────────────────────────
def fig_in_memory():
    W = 1300
    x0, cw, n = 300, 72, 8
    xr = x0 + cw * n                 # 876
    ax, aw = 910, 360

    top = 96
    val_h, bit_h, gap = 40, 22, 14
    block = val_h + bit_h + gap      # 76

    cols = [
        ("id\nint64", ["41", "42", "43", "44", "45", "46", "47", "48"], [1] * 8),
        ("customer_id\ntext",
         ["ACME", "Borysfen", "Cebra", "Delta", "Erid", "Fenix", "Grot", "Hvylia"],
         [1] * 8),
        ("total_cents\nint64",
         ["35000", "118000", "?", "9000", "7000", "15500", "2000", "41000"],
         [1, 1, 0, 1, 1, 1, 1, 1]),
        ("status\ntext",
         ["paid", "review", "paid", "shipped", "new", "paid", "paid", "paid"],
         [1] * 8),
    ]

    f = [text(W / 2, 34, "Колонковий набір у пам'яті: масиви, маска, стани, тіні",
              size=17, bold=True)]

    # лінійка номерів рядків
    f.append(text(290, 82, "рядок №", size=11, color=MUTED, anchor="end"))
    for j in range(n):
        f.append(text(x0 + j * cw + cw / 2, 82, str(j), size=11, color=MUTED))

    for i, (name, vals, bits) in enumerate(cols):
        vy = top + i * block
        by = vy + val_h
        f.append(fitbox(30, vy, 260, val_h + bit_h, name, size=12.5,
                        fill=HEAD_FILL, stroke=LINE))
        for j in range(n):
            null = (bits[j] == 0)
            f.append(rect(x0 + j * cw, vy, cw, val_h,
                          fill=(NULL_FILL if null else BG), stroke=LINE, sw=1.1, rx=0))
            f.append(text(x0 + j * cw + cw / 2, vy + val_h / 2 + 4, vals[j],
                          size=10.5, color=(POS if null else INK)))
            f.append(rect(x0 + j * cw, by, cw, bit_h,
                          fill=(NULL_FILL if null else "#f2f6ff"), stroke=LINE, sw=1.0, rx=0))
            f.append(text(x0 + j * cw + cw / 2, by + bit_h / 2 + 4, str(bits[j]),
                          size=11, color=(POS if null else NEG), bold=True))

    # стани рядків
    sy = top + 4 * block + 8
    f.append(fitbox(30, sy, 260, val_h, "стан рядка", size=12.5,
                    fill=HEAD_FILL, stroke=LINE))
    states = [("незм.", BG), ("змін.", COLD_FILL), ("незм.", BG), ("незм.", BG),
              ("незм.", BG), ("вил.", NULL_FILL), ("незм.", BG), ("дод.", WARM_FILL)]
    for j, (s, fill) in enumerate(states):
        f.append(rect(x0 + j * cw, sy, cw, val_h, fill=fill, stroke=LINE, sw=1.1, rx=0))
        f.append(text(x0 + j * cw + cw / 2, sy + val_h / 2 + 4, s, size=10.5))

    # примітки праворуч
    f.append(fitbox(ax, 100, aw, 54,
                    "рядок — це спільний індекс:\n"
                    "рядок 3 стоїть третьою коміркою\nв КОЖНОМУ масиві",
                    size=11.5, fill=BG, stroke=NEG))
    f.append(arrow(ax - 6, 127, xr + 4, 127, color=NEG, sw=1.5))

    f.append(fitbox(ax, 262, aw, 54,
                    "біт 0 — комірка NULL.\n"
                    "У масиві на цьому місці сміття,\nчитати його не можна",
                    size=11.5, fill=NULL_FILL, stroke=POS))
    f.append(arrow(ax - 6, 289, xr + 4, 289, color=POS, sw=1.5))

    f.append(fitbox(ax, sy - 8, aw, 56,
                    "вилучений рядок лишається\nна місці надгробком — інакше\n"
                    "в базі не буде чого видаляти",
                    size=11.5, fill=BG, stroke=MUTED))
    f.append(arrow(ax - 6, sy + 20, xr + 4, sy + 20, color=MUTED, sw=1.5))

    # два нижні блоки
    by2 = sy + val_h + 34
    f.append(fitbox(30, by2, 610, 108,
                    "схема як дані — відображення «ім'я → номер», будується раз:\n"
                    "id→0   customer_id→1   total_cents→2   status→3\n"
                    "col(\"total_cents\") — один пошук у хеші,\n"
                    "далі прямий доступ у масив за номером",
                    size=12, fill=WARM_FILL, stroke=FIELD))
    f.append(fitbox(670, by2, 600, 108,
                    "початкові значення — розріджено, лише правлені комірки:\n"
                    "(рядок 1, total_cents) → 118000     (рядок 1, status) → 'paid'\n"
                    "тінь на ВЕСЬ набір подвоїла б пам'ять;\n"
                    "у доданого рядка 7 початкових значень немає взагалі",
                    size=12, fill=COLD_FILL, stroke=NEG))

    H = by2 + 108 + 46
    f.append(text(W / 2, H - 20,
                  "маска валідності — 64-бітні слова: на вісім рядків вистачає одного слова на колонку",
                  size=11.5, color=MUTED, italic=True))
    return render(os.path.join(OUT, "record-set-in-memory.svg"), W, H, *f)


# ── 7. Порядок операторів і межа підтвердження ────────────────────────────────
def fig_apply_order():
    W, H = 1300, 616
    f = [text(W / 2, 34, "Запис назад: у якому порядку і де межа підтвердження",
              size=17, bold=True)]

    f.append(text(320, 70, "порядок операторів", size=13.5, bold=True, color=MUTED))
    f.append(text(970, 70, "межа транзакції", size=13.5, bold=True, color=MUTED))

    lx, lw = 40, 560
    rx, rw = 680, 580

    f.append(fitbox(lx, 90, lw, 88,
                    "1 · INSERT — батьки раніше за дітей\n"
                    "customers → orders → order_lines\n"
                    "згенерований ключ батька повертає RETURNING —\n"
                    "і його вписують дітям перед їхньою вставкою",
                    size=12, fill=WARM_FILL, stroke=FIELD))
    f.append(fitbox(lx, 196, lw, 56,
                    "2 · UPDATE — усередині одного рівня\nпорядок довільний",
                    size=12, fill=COLD_FILL, stroke=NEG))
    f.append(fitbox(lx, 270, lw, 74,
                    "3 · DELETE — діти раніше за батьків\n"
                    "order_lines → orders → customers\n"
                    "інакше зовнішній ключ не дасть прибрати батька",
                    size=12, fill=NULL_FILL, stroke=POS))
    f.append(fitbox(lx, 366, lw, 74,
                    "набір, що просто йде рядками згори вниз,\n"
                    "розіб'ється об обмеження цілісності на пів дорозі:\n"
                    "порядок задає граф зв'язків, а не номер рядка",
                    size=12, fill=BG, stroke=MUTED))

    steps = [
        (90, 42, "BEGIN", FIELD, BG),
        (152, 96, "кожен оператор: виконати й спитати,\n"
                  "скільки рядків він змінив\n"
                  "1 → далі     0 → нас випередили", NEG, BG),
        (268, 42, "COMMIT", FIELD, WARM_FILL),
        (330, 74, "accept(): стани → незмінений,\n"
                  "початкові значення стерти, надгробки прибрати", MUTED, BG),
    ]
    for y, h, s, stroke, fill in steps:
        f.append(fitbox(rx, y, rw, h, s, size=12.5, fill=fill, stroke=stroke))
    for y0, y1 in ((132, 148), (248, 264), (310, 326)):
        f.append(arrow(rx + rw / 2, y0, rx + rw / 2, y1, color=MUTED, sw=1.6))

    f.append(fitbox(rx, 418, rw, 44, "0 змінених рядків → ROLLBACK і конфлікт",
                    size=12.5, fill=NULL_FILL, stroke=POS))
    f.append(arrow(rx - 8, 200, rx - 8, 440, color=POS, sw=1.4))

    f.append(fitbox(120, 490, 1060, 84,
                    "Поміняти місцями два останні кроки — і набір збреше сам собі:\n"
                    "після відкату стани вже «незмінений», початкові значення стерті,\n"
                    "правки користувача зникли без сліду, а в базі їх ніколи не було.\n"
                    "Приймати зміни можна ЛИШЕ після того, як COMMIT повернувся успіхом.",
                    size=12.5, fill=NULL_FILL, stroke=POS))
    return render(os.path.join(OUT, "record-set-apply-order.svg"), W, H, *f)


if __name__ == "__main__":
    for fn in (fig_anatomy, fig_connected_vs_disconnected, fig_writeback,
               fig_layout, fig_lineage, fig_in_memory, fig_apply_order):
        print(fn())
