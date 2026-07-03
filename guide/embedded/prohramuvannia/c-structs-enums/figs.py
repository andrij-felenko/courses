# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

TS   = "#8a6a1e"   # бурштин — час
VAL  = NEG         # синій — значення
OKC  = FIELD       # зелений — ознака справності
REC  = "#5b3fa0"   # фіолетовий — цілий запис/структура


# ── why-struct: три паралельні масиви проти масиву структур ────────────────────
# Ідея: паралельні масиви тримають зв'язок лише «в голові» й розповзаються;
# масив структур зшиває поля одного виміру в одну нероздільну комірку.
def fig_why_struct():
    W, H = 860, 470
    p = []
    p.append(line(W/2, 70, W/2, 430, color="#dcdcdc", sw=1.6, dash="5 6"))

    # ── ЛІВОРУЧ: три паралельні масиви ──
    p.append(text(215, 66, "Три паралельні масиви", size=14, color=INK, bold=True))
    p.append(text(215, 86, "зв'язок «один вимір» — лише домовленість", size=10, color=MUTED, italic=True))
    rows = [
        ("ts[]",    TS,  "#fbf3e0", ["100", "140", "…", "205", "…"]),
        ("value[]", VAL, "#eef2fb", ["23.5", "23.9", "…", "24.0", "…"]),
        ("ok[]",    OKC, "#eaf6ee", ["1", "1", "…", "1", "…"]),
    ]
    cx0, cw, ch = 96, 52, 34
    y = 108
    for name, col, fil, cells in rows:
        p.append(text(cx0 - 44, y + ch/2 + 4, name, size=11, color=col, bold=True, anchor="middle"))
        for i, c in enumerate(cells):
            x = cx0 + i*cw
            hot = (i == 3)   # п'ятий елемент — приклад «одного виміру»
            p.append(rect(x, y, cw-4, ch, fill=fil, stroke=col,
                          sw=2.2 if hot else 1.3))
            p.append(text(x + (cw-4)/2, y + ch/2 + 4, c, size=10, color=INK, bold=hot))
        y += ch + 8
    # індекс-підпис під колонкою-виміром
    p.append(text(cx0 + 3*cw + (cw-4)/2, y + 6, "[5]", size=10, color=INK, bold=True))
    p.append(text(215, y + 34, "зсунув один масив — і ts[5] уже", size=10.5, color=POS, bold=True))
    p.append(text(215, y + 50, "не про той вимір, що value[5]", size=10.5, color=POS, bold=True))

    # ── ПРАВОРУЧ: масив структур ──
    p.append(text(645, 66, "Масив структур", size=14, color=INK, bold=True))
    p.append(text(645, 86, "поля виміру зшиті в одну комірку", size=10, color=MUTED, italic=True))
    # ряд комірок; кожна — цілий запис (три поля разом)
    bx0, bw, bh = 470, 66, 96
    labels = ["[3]", "[4]", "[5]", "[6]"]
    yb = 118
    for i, lb in enumerate(labels):
        x = bx0 + i*(bw+6)
        hot = (i == 2)
        p.append(rect(x, yb, bw, bh, fill="#f2eefb" if hot else "#f7f7fb",
                      stroke=REC, sw=2.4 if hot else 1.3))
        p.append(text(x + bw/2, yb + 16, lb, size=10, color=REC, bold=True))
        # три міні-поля всередині комірки
        p.append(rect(x+6, yb+24, bw-12, 20, fill="#fbf3e0", stroke=TS, sw=1))
        p.append(text(x+bw/2, yb+38, "ts", size=8.5, color=TS, bold=True))
        p.append(rect(x+6, yb+48, bw-12, 20, fill="#eef2fb", stroke=VAL, sw=1))
        p.append(text(x+bw/2, yb+62, "value", size=8.5, color=VAL, bold=True))
        p.append(rect(x+6, yb+72, bw-12, 18, fill="#eaf6ee", stroke=OKC, sw=1))
        p.append(text(x+bw/2, yb+85, "ok", size=8.5, color=OKC, bold=True))
    p.append(text(645, yb + bh + 30, "log[5] — нероздільна трійка:", size=10.5, color=REC, bold=True))
    p.append(text(645, yb + bh + 46, "поля лежать разом і рухаються разом", size=10.5, color=REC, bold=True))

    render(os.path.join(OUT, "why-struct.svg"), W, H, *p,
           title="Паралельні масиви розповзаються; масив структур тримає вимір цілим")


# ── record-state: структура-запис із полем-переліченням = машина станів ────────
# Ідея: один запис Sensor тримає все про давач; поле-enum робить стан читабельним,
# а switch по цьому полю переводить давача між станами.
def fig_record_state():
    W, H = 860, 430
    p = []
    # ── ліворуч: сам запис Sensor ──
    p.append(text(200, 62, "Один запис — усе про давач", size=13.5, color=INK, bold=True))
    rec_x, rec_y, rec_w = 70, 84, 260
    p.append(rect(rec_x, rec_y, rec_w, 150, fill="#f2eefb", stroke=REC, sw=2))
    p.append(text(rec_x + rec_w/2, rec_y + 22, "Sensor", size=13, color=REC, bold=True))
    fields = [
        ("id", "1", TS, "#fbf3e0", "номер на шині"),
        ("last", "23.5", VAL, "#eef2fb", "останнє °C"),
        ("mode", "S_IDLE", OKC, "#eaf6ee", "стан (перелічення)"),
    ]
    fy = rec_y + 34
    for nm, vv, col, fil, note in fields:
        p.append(rect(rec_x + 12, fy, rec_w - 24, 34, fill=fil, stroke=col, sw=1.4))
        p.append(text(rec_x + 30, fy + 21, nm, size=11, color=col, bold=True, anchor="start"))
        p.append(text(rec_x + rec_w - 24, fy + 14, vv, size=10.5, color=INK, bold=True, anchor="end"))
        p.append(text(rec_x + rec_w - 24, fy + 28, note, size=8, color=MUTED, italic=True, anchor="end"))
        fy += 38
    p.append(text(200, rec_y + 168, "поле mode — не число, а названий стан", size=10, color=MUTED, italic=True))

    # ── праворуч: машина станів по полю mode ──
    p.append(text(620, 62, "switch (s->mode) веде давача", size=13.5, color=INK, bold=True))
    # три стани колом
    st = [
        (560, 150, "S_IDLE", "чекає", OKC, "#eaf6ee"),
        (760, 150, "S_READING", "міряє", VAL, "#eef2fb"),
        (660, 300, "S_FAULT", "несправність", POS, "#fff0ef"),
    ]
    pos = {}
    for x, y, nm, note, col, fil in st:
        b, w, h = textbox(x, y, nm, size=11.5, color=col, stroke=col, fill=fil, bold=True, min_w=118)
        p.append(b)
        p.append(text(x, y + 28, note, size=9, color=MUTED, italic=True))
        pos[nm] = (x, y)
    # переходи
    p.append(arrow(pos["S_IDLE"][0]+62, pos["S_IDLE"][1]-6,
                   pos["S_READING"][0]-62, pos["S_READING"][1]-6, color=INK, sw=2))
    p.append(text(660, 128, "крок", size=9, color=INK, bold=True))
    p.append(arrow(pos["S_READING"][0]-62, pos["S_READING"][1]+6,
                   pos["S_IDLE"][0]+62, pos["S_IDLE"][1]+6, color=OKC, sw=2))
    p.append(text(660, 176, "вимір ок", size=9, color=OKC, bold=True))
    p.append(arrow(pos["S_READING"][0]-24, pos["S_READING"][1]+26,
                   pos["S_FAULT"][0]+40, pos["S_FAULT"][1]-24, color=POS, sw=2))
    p.append(text(748, 238, "безглузде число", size=9, color=POS, bold=True))
    p.append(text(W/2, 400, "Структура тримає все про давач; поле-перелічення робить стан читабельним, "
                  "а switch по ньому — це машина станів.", size=11, color=INK, bold=True))
    render(os.path.join(OUT, "record-state.svg"), W, H, *p,
           title="Структура + перелічення = кістяк машини станів")


# ── lineage: родовід і дозрівання struct/enum (для hist-вставки) ───────────────
# Ідея: горизонтальна стрічка мов-предків CPL→BCPL→B→C, а під C — три віхи,
# коли структура з кволої дозріла: народження (Embryonic C), union/typedef (V6),
# «майже першокласна» + enum після K&R.
def fig_lineage():
    W, H = 880, 470
    p = []
    # ── верхня стрічка: родовід мов ──
    p.append(text(W/2, 60, "Родовід: від CPL до C", size=14, color=INK, bold=True))
    chain = [
        (110, "CPL",  "Кембридж\n1963–67", MUTED, "#f2f2f4"),
        (300, "BCPL", "М. Річардс\n1967", NEG,   "#eef2fb"),
        (490, "B",    "К. Томпсон\n1969–70", "#8a6a1e", "#fbf3e0"),
        (700, "C",    "Д. Рітчі\n1971–73", REC,   "#f2eefb"),
    ]
    cy = 108
    boxes = {}
    for x, nm, sub, col, fil in chain:
        b, w, h = textbox(x, cy, nm, size=15, color=col, stroke=col, fill=fil,
                          bold=True, min_w=88, pad=12)
        p.append(b)
        boxes[nm] = (x, w)
        for i, ln in enumerate(sub.split("\n")):
            p.append(text(x, cy + 34 + i*13, ln, size=8.5, color=MUTED, italic=True))
    order = ["CPL", "BCPL", "B", "C"]
    for a, bb in zip(order, order[1:]):
        xa, wa = boxes[a]; xb, wb = boxes[bb]
        p.append(arrow(xa + wa/2, cy, xb - wb/2, cy, color=INK, sw=2))
    p.append(text(205, cy - 30, "спрощення", size=8.5, color=MUTED, italic=True))
    p.append(text(395, cy - 30, "стиснення", size=8.5, color=MUTED, italic=True))
    p.append(text(600, cy - 30, "+ типи", size=8.5, color=POS, bold=True))
    p.append(text(W/2, cy + 62, "кожна ланка коштувала можливостей: типи були в CPL, "
                  "їх викинули заради простоти — і Рітчі вернув їх у C",
                  size=9.5, color=MUTED, italic=True))

    # ── нижня стрічка: дозрівання структури ──
    axis_y = 300
    p.append(text(W/2, 208, "Як структура дозрівала", size=14, color=INK, bold=True))
    p.append(line(80, axis_y, 800, axis_y, color="#cfcfcf", sw=2))
    milestones = [
        (150, "«Ембріональна» C\n~1972", "структури ще нема;\nтип-запис — головна\nтруднота Рітчі", POS, "#fff0ef"),
        (400, "V6 · 1975", "додано union,\ntypedef, unsigned", NEG, "#eef2fb"),
        (650, "після K&R · 1978", "присвоєння, передача\nу функцію; enum;\nполя тверде за типом", FIELD, "#eaf6ee"),
    ]
    for x, head, body, col, fil in milestones:
        p.append(circle(x, axis_y, 6, fill=col, stroke=col, sw=2))
        p.append(line(x, axis_y, x, axis_y - 42, color=col, sw=1.4, dash="3 4"))
        for i, ln in enumerate(head.split("\n")):
            p.append(text(x, axis_y - 60 + i*15, ln, size=11, color=col, bold=True))
        b = fitbox(x - 92, axis_y + 22, 184, 72, body, size=10, color=INK,
                   stroke=col, fill=fil, sw=1.4)
        p.append(b)
    p.append(text(W/2, axis_y + 128, "Книга K&R (1978) описала майбутнє структур; "
                  "мова догнала опис лише після виходу книги.",
                  size=10, color=INK, bold=True))
    render(os.path.join(OUT, "lineage.svg"), W, H, *p,
           title="Родовід C і повільне дозрівання структури")


PAD = "#c9ccd4"   # набивка (padding) — сірий


# ── layout-offsets (detailed): байтова лінійка розкладки з offsetof і дірками ───
# Ідея: показати РЕАЛЬНІ зсуви полів на лінійці байтів — де сидить кожне поле,
# де компілятор устромив набивку, і що дає offsetof; поряд — той самий набір
# полів, перевпорядкований від більших до менших, стиснений без хвостової дірки.
def fig_layout_offsets():
    W, H = 880, 470
    p = []
    bw = 40   # ширина одного байта на лінійці
    x0 = 70

    def ruler(y, cells, label):
        # cells: список (span, kind, name) — kind: 'f' поле, 'p' набивка
        frags = []
        x = x0
        idx = 0
        for span, kind, name in cells:
            w = span * bw
            if kind == "p":
                # набивку читаємо кольором (сірий) — без штрихування, щоб напис лишався чистим
                frags.append(rect(x, y, w, 34, fill="#e9eaee", stroke=PAD, sw=1.4, rx=3))
                frags.append(text(x + w/2, y + 21, "pad", size=9, color=MUTED, italic=True))
            else:
                col, fil = name[1], name[2]
                frags.append(rect(x, y, w, 34, fill=fil, stroke=col, sw=1.8, rx=3))
                frags.append(text(x + w/2, y + 15, name[0], size=10.5, color=col, bold=True))
                frags.append(text(x + w/2, y + 28, name[3], size=8, color=MUTED))
            # адреси-риски знизу
            for b in range(span):
                bx = x + b*bw
                frags.append(text(bx + bw/2, y + 48, str(idx), size=8.5, color=MUTED))
                idx += 1
            x += w
        frags.append(text(x0 - 12, y + 21, label, size=11, color=INK, bold=True, anchor="end"))
        return frags, x

    # ── верхня лінійка: «незручний» порядок → дірки ──
    p.append(text(W/2, 62, "Той самий набір полів, дві розкладки", size=14, color=INK, bold=True))
    tsF   = ("flag",  POS,  "#fdecea", "1 Б")
    valF  = ("value", NEG,  "#eaf0fd", "4 Б")
    cntF  = ("count", FIELD,"#eafaf0", "2 Б")
    top, xend = ruler(96, [
        (1, "f", tsF), (3, "p", None), (4, "f", valF), (2, "f", cntF), (2, "p", None),
    ], "Bad")
    p += top
    p.append(text(x0, 168, "sizeof(Bad) = 12  — 5 байтів «повітря»: 3 перед value + 2 у хвості",
                  size=10.5, color=POS, bold=True, anchor="start"))
    # offsetof-виноски
    p.append(text(x0 + 0*bw + bw/2, 84, "offsetof=0", size=8, color=MUTED))
    p.append(text(x0 + 4*bw + 2*bw, 84, "offsetof(value)=4", size=8, color=MUTED))

    # ── нижня лінійка: від більших до менших → щільно ──
    bot, xend2 = ruler(230, [
        (4, "f", valF), (2, "f", cntF), (1, "f", tsF), (1, "p", None),
    ], "Good")
    p += bot
    p.append(text(x0, 302, "sizeof(Good) = 8  — та сама інформація, лише 1 байт хвоста",
                  size=10.5, color=FIELD, bold=True, anchor="start"))

    # висновок
    p.append(line(x0, 336, W-70, 336, color="#e2e2e6", sw=1))
    p.append(text(W/2, 366, "Розмір структури — не сума полів: компілятор вирівнює кожне поле й додає набивку.",
                  size=11, color=INK, bold=True))
    p.append(text(W/2, 388, "offsetof дає точний зсув кожного поля; порядок «від більших до менших» стискає дірки.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "layout-offsets.svg"), W, H, *p,
           title="Розкладка структури: зсуви, набивка, offsetof")


# ── bitfield-pack (detailed): бітові поля пакують прапорці в одне слово ─────────
# Ідея: три прапорці й лічильник — окремими uint8_t це 4+ байти; бітовими полями
# все лягає в одне 8-бітне слово. Показуємо самі біти й хто який зайняв.
def fig_bitfield_pack():
    W, H = 880, 440
    p = []
    p.append(text(W/2, 60, "Прапорці: окремі байти проти бітових полів", size=14, color=INK, bold=True))

    # ── ліворуч: наївно — кожен прапорець окремий байт ──
    p.append(text(215, 96, "Кожне поле — свій байт", size=12, color=INK, bold=True))
    naive = [("ready", POS, "#fdecea"), ("error", NEG, "#eaf0fd"),
             ("armed", FIELD, "#eafaf0"), ("count:5", MUTED, "#f0f0f3")]
    bx, by, bs = 90, 120, 46
    for i, (nm, col, fil) in enumerate(naive):
        y = by + i*(bs+8)
        p.append(rect(bx, y, 240, bs, fill=fil, stroke=col, sw=1.6))
        p.append(text(bx + 14, y + bs/2 + 4, nm, size=11, color=col, bold=True, anchor="start"))
        p.append(text(bx + 240 - 14, y + bs/2 + 4, "1 байт", size=9.5, color=MUTED, anchor="end"))
    p.append(text(215, by + 4*(bs+8) + 14, "разом ≈ 4 байти на 4 біти сенсу",
                  size=10.5, color=POS, bold=True))

    # ── праворуч: бітові поля в одному 8-бітному слові ──
    p.append(text(645, 96, "Бітові поля — одне слово", size=12, color=INK, bold=True))
    # 8 клітинок-бітів
    cell = 44
    ox, oy = 470, 132
    # розмітка: біти 7..0 (старший ліворуч); ready=b0, error=b1, armed=b2, count=b3..b7
    bits = [
        ("count", FIELD, "#eafaf0"), ("count", FIELD, "#eafaf0"),
        ("count", FIELD, "#eafaf0"), ("count", FIELD, "#eafaf0"),
        ("count", FIELD, "#eafaf0"),
        ("armed", "#8a6a1e", "#fbf3e0"), ("error", NEG, "#eaf0fd"),
        ("ready", POS, "#fdecea"),
    ]
    for i, (nm, col, fil) in enumerate(bits):
        x = ox + i*cell
        p.append(rect(x, oy, cell-3, cell, fill=fil, stroke=col, sw=1.5, rx=3))
        p.append(text(x + (cell-3)/2, oy + cell + 14, str(7-i), size=9, color=MUTED))
    # дужки-підписи полів під групами
    def brace_label(i0, i1, name, col):
        xa = ox + i0*cell
        xb = ox + i1*cell + (cell-3)
        yb = oy + cell + 22
        p.append(line(xa, yb, xb, yb, color=col, sw=2))
        p.append(line(xa, yb, xa, yb-5, color=col, sw=2))
        p.append(line(xb, yb, xb, yb-5, color=col, sw=2))
        p.append(text((xa+xb)/2, yb + 16, name, size=9.5, color=col, bold=True))
    brace_label(0, 4, "count : 5", FIELD)
    brace_label(5, 5, "armed", "#8a6a1e")
    brace_label(6, 6, "error", NEG)
    brace_label(7, 7, "ready", POS)
    p.append(text(645, oy + cell + 66, "усе в 1 байті — те, що раніше займало 4",
                  size=10.5, color=FIELD, bold=True))
    p.append(text(645, oy + cell + 84, "порядок бітів у слові — на розсуд компілятора",
                  size=9.5, color=MUTED, italic=True))

    p.append(text(W/2, 408, "Бітове поле «: n» просить у поля рівно n бітів; компілятор пакує їх в одне слово.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "bitfield-pack.svg"), W, H, *p,
           title="Бітові поля: багато прапорців в одному слові")


# ── union-overlay (detailed): члени об'єднання ділять ті самі байти ─────────────
# Ідея: union кладе всі члени на ОДНУ пам'ять; float і чотири uint8 — це той самий
# шматок, поглянутий двома очима. Класичний прийом розбору байтів пакета.
def fig_union_overlay():
    W, H = 860, 420
    p = []
    p.append(text(W/2, 60, "Об'єднання: одні байти — два погляди", size=14, color=INK, bold=True))

    # спільні 4 байти посередині
    cw, cx0, cy = 96, 300, 210
    p.append(text(W/2, cy - 40, "одна й та сама пам'ять — 4 байти", size=11, color=REC, bold=True))
    for i in range(4):
        x = cx0 + i*cw
        p.append(rect(x, cy, cw-6, 54, fill="#f2eefb", stroke=REC, sw=2))
        p.append(text(x + (cw-6)/2, cy + 22, "байт", size=9.5, color=REC))
        p.append(text(x + (cw-6)/2, cy + 40, str(i), size=11, color=INK, bold=True))

    # погляд 1: як float (зверху) — суцільна смуга над байтами = одне 4-байтне число
    p.append(text(cx0 - 10, cy - 8, "як float f:", size=11, color=NEG, bold=True, anchor="end"))
    p.append(rect(cx0, cy - 8, 4*cw - 6, 6, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=2))
    p.append(text(cx0 + (4*cw-6)/2, cy - 20, "одне 4-байтне число", size=9, color=NEG, italic=True))

    # погляд 2: як чотири uint8 (знизу)
    p.append(text(cx0 - 10, cy + 78, "як bytes[4]:", size=11, color="#8a6a1e", bold=True, anchor="end"))
    for i in range(4):
        x = cx0 + i*cw
        p.append(rect(x, cy + 66, cw-6, 22, fill="#fbf3e0", stroke="#8a6a1e", sw=1.5, rx=3))
        p.append(text(x + (cw-6)/2, cy + 81, "b[%d]" % i, size=9.5, color="#8a6a1e", bold=True))

    p.append(text(W/2, cy + 118, "Пишеш f — читаєш b[0..3]: ті самі біти, розібрані на байти.",
                  size=11, color=INK, bold=True))
    p.append(text(W/2, cy + 140, "struct кладе поля ПОРЯД (сума розмірів); union кладе їх НА ОДНЕ МІСЦЕ (розмір найбільшого).",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "union-overlay.svg"), W, H, *p,
           title="union: члени лежать на одній пам'яті")


# ── reg-two-views (proj): один 32-бітний регістр статусу, два способи прочитати ──
# Ідея: реальний UART_STATUS_REG ESP32 — datasheet кладе поля за ФІКСОВАНИМИ
# бітами (RXFIFO_CNT [7:0], TXFIFO_CNT [23:16]…). Явні маски/зсуви над volatile-
# словом читають рівно ці біти — надійно. Наївна bit-field-структура припускає
# СВІЙ порядок пакування, який компілятор не зобов'язаний узгодити з datasheet.
def fig_reg_two_views():
    W, H = 880, 500
    p = []
    p.append(text(W/2, 60, "UART_STATUS_REG ESP32: один регістр, два прочитання", size=14, color=INK, bold=True))

    # ── 32-бітне слово: показуємо групи бітів за datasheet ──
    # групи (старший біт ліворуч): [31]TXD [30]RTSN [29]DTRN [28]· [27:24]UTX
    #  [23:16]TXFIFO_CNT [15]RXD [14]CTSN [13]DSRN [12]· [11:8]URX [7:0]RXFIFO_CNT
    x0, y0, totw, bh = 70, 100, 740, 40
    groups = [
        (4, "лінії TX", "31–28", MUTED, "#f0f0f3"),
        (4, "UTX",  "27–24", "#8a6a1e", "#fbf3e0"),
        (8, "TXFIFO_CNT", "23–16", NEG, "#eaf0fd"),
        (4, "лінії RX", "15–12", MUTED, "#f0f0f3"),
        (4, "URX",  "11–8",  "#8a6a1e", "#fbf3e0"),
        (8, "RXFIFO_CNT", "7–0", FIELD, "#eafaf0"),
    ]
    total_bits = sum(g[0] for g in groups)
    x = x0
    for span, nm, rng, col, fil in groups:
        w = totw * span / total_bits
        p.append(rect(x, y0, w-2, bh, fill=fil, stroke=col, sw=1.8, rx=3))
        fs = fit_font(nm, w-8, 10.5, True)
        p.append(text(x + w/2, y0 + 17, nm, size=fs, color=col, bold=True))
        p.append(text(x + w/2, y0 + 31, "["+rng+"]", size=8, color=MUTED))
        x += w
    p.append(text(x0, y0 - 10, "біт 31 (старший)", size=8.5, color=MUTED, anchor="start"))
    p.append(text(x0+totw, y0 - 10, "біт 0 (молодший)", size=8.5, color=MUTED, anchor="end"))
    p.append(text(W/2, y0 + bh + 22, "розкладку бітів диктує datasheet — вона фіксована й однакова для всіх",
                  size=10, color=INK, bold=True))

    # ── два способи прочитати RXFIFO_CNT ──
    cy = 250
    # ЛІВОРУЧ: маски/зсуви над volatile-словом (надійно)
    lx = 70
    p.append(rect(lx, cy, 360, 150, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    p.append(text(lx + 180, cy + 26, "Явні маски й зсуви", size=12.5, color=FIELD, bold=True))
    p.append(text(lx + 180, cy + 46, "над volatile-словом", size=10, color=MUTED, italic=True))
    p.append(text(lx + 20, cy + 74, "w = UART0->status;", size=10.5, color=INK, anchor="start"))
    p.append(text(lx + 20, cy + 94, "rx = (w >> 0) & 0xFF;", size=10.5, color=INK, anchor="start"))
    p.append(text(lx + 20, cy + 114, "tx = (w >> 16) & 0xFF;", size=10.5, color=INK, anchor="start"))
    p.append(text(lx + 180, cy + 138, "читає рівно ті біти, що в datasheet", size=9, color=FIELD, bold=True))

    # ПРАВОРУЧ: наївна bit-field-структура (крихко)
    rx = 470
    p.append(rect(rx, cy, 360, 150, fill="#fdecea", stroke=POS, sw=2, rx=8))
    p.append(text(rx + 180, cy + 26, "Наївні бітові поля", size=12.5, color=POS, bold=True))
    p.append(text(rx + 180, cy + 46, "накладені на регістр", size=10, color=MUTED, italic=True))
    p.append(text(rx + 20, cy + 74, "struct { uint32_t rx:8;", size=10.5, color=INK, anchor="start"))
    p.append(text(rx + 40, cy + 94, "... tx:8; } *S;", size=10.5, color=INK, anchor="start"))
    p.append(text(rx + 20, cy + 114, "S->rx;  // де насправді?", size=10.5, color=INK, anchor="start"))
    p.append(text(rx + 180, cy + 138, "порядок бітів — на розсуд компілятора", size=9, color=POS, bold=True))

    p.append(text(W/2, 448, "Маски над словом і datasheet говорять про біти однаково.",
                  size=11, color=INK, bold=True))
    p.append(text(W/2, 470, "Бітове поле «rx:8» може лягти в старші біти, а не в [7:0] — і код тихо читає не те.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "reg-two-views.svg"), W, H, *p,
           title=None)


# ── overlay-map (proj): структура-слова накладена на базову адресу периферії ────
# Ідея: карту регістрів описують структурою з volatile uint32_t полів; покажчик
# на неї = базова адреса блоку. Кожне поле лягає на СВІЙ регістр за зсувом, а
# static_assert(offsetof(...)==datasheet) звіряє розкладку ще на компіляції.
def fig_overlay_map():
    W, H = 860, 470
    p = []
    p.append(text(W/2, 60, "Структура-накладка на карту регістрів периферії", size=14, color=INK, bold=True))

    # ── ЛІВОРУЧ: структура полів ──
    sx, sy, sw_, rh = 70, 100, 300, 44
    p.append(text(sx + sw_/2, sy - 14, "struct UartRegs (у пам'яті програми)", size=10.5, color=REC, bold=True))
    regs = [
        ("fifo",   "+0x00", "0x00"),
        ("(проміжні)", "…", None),
        ("status", "+0x1C", "0x1C"),
        ("conf0",  "+0x20", "0x20"),
    ]
    p.append(rect(sx, sy, sw_, len(regs)*rh + 12, fill="#f2eefb", stroke=REC, sw=2))
    fy = sy + 12
    ycent = {}
    for nm, off, hexoff in regs:
        col = MUTED if hexoff is None else REC
        fil = "#f0f0f3" if hexoff is None else "#f7f4fc"
        p.append(rect(sx + 12, fy, sw_ - 24, rh - 8, fill=fil, stroke=col, sw=1.4))
        p.append(text(sx + 30, fy + (rh-8)/2 + 4, "volatile uint32_t " + nm if hexoff else nm,
                      size=10 if hexoff else 9.5, color=col, bold=bool(hexoff), anchor="start"))
        p.append(text(sx + sw_ - 24, fy + (rh-8)/2 + 4, off, size=9.5, color=MUTED, anchor="end"))
        ycent[nm] = fy + (rh-8)/2
        fy += rh

    # ── ПРАВОРУЧ: реальні регістри за адресами ──
    ax, ay = 560, 100
    p.append(text(ax + 120, ay - 14, "залізо на APB-шині", size=10.5, color=INK, bold=True))
    addrs = [
        ("0x3FF40000", "FIFO",   "fifo",   NEG,  "#eaf0fd"),
        ("0x3FF4001C", "STATUS", "status", FIELD,"#eafaf0"),
        ("0x3FF40020", "CONF0",  "conf0",  "#8a6a1e", "#fbf3e0"),
    ]
    ry = ay + 12
    for addr, nm, src, col, fil in addrs:
        b, bw2, bh2 = textbox(ax + 120, ry + 18, nm, size=11, color=col, stroke=col,
                              fill=fil, bold=True, min_w=110)
        p.append(b)
        p.append(text(ax + 120, ry + 42, addr, size=9, color=MUTED))
        # стрілка від поля структури до його регістра
        if src in ycent:
            p.append(arrow(sx + sw_ + 4, ycent[src], ax + 120 - bw2/2 - 6, ry + 18,
                           color=col, sw=1.8))
        ry += 66

    p.append(text(sx, 360, "UartRegs *U = (UartRegs*)0x3FF40000;", size=10.5, color=INK, bold=True, anchor="start"))
    p.append(text(sx, 384, "U->status;  →  читає слово за адресою 0x3FF4001C", size=10, color=FIELD, anchor="start"))
    p.append(text(sx, 408, "_Static_assert(offsetof(UartRegs,status)==0x1C, \"зсув!\");",
                  size=10, color=POS, anchor="start"))
    p.append(text(W/2, 446, "Поле структури = регістр за своїм зсувом; static_assert звіряє розкладку ще на компіляції.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "overlay-map.svg"), W, H, *p, title=None)


if __name__ == "__main__":
    fig_why_struct()
    fig_record_state()
    fig_lineage()
    fig_layout_offsets()
    fig_bitfield_pack()
    fig_union_overlay()
    fig_reg_two_views()
    fig_overlay_map()
    print("OK: figs written to", OUT)
