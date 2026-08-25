# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори зон (стійкі між фігурами): службове — сіре, app/код — червоне,
# дані — синє, файли — зелене, таблиця-карта — бурштин.
BOOT = ("#eef0f5", "#9aa0aa")     # завантажувач, службове
MAP  = ("#fff6e0", "#caa24a")     # таблиця розділів
DATA = ("#e9eefb", NEG)           # data (NVS, otadata, phy)
APP  = ("#fbecec", POS)           # app (factory, ota_*)
FS   = ("#eef6ef", FIELD)         # файлова система


# ── why-partition: Flash — не моноліт, а низка названих ділянок ────────────────
# Ідея: показати РІЗНОРІДНІСТЬ мешканців одного чипа й те, що порядок їм
# задає маленька таблиця на початку Flash.

def fig_why_partition():
    W, H = 760, 300
    p = []
    y, h = 120, 84
    x = 50
    # ширини пропорційні «вазі» зони
    zones = [
        ("заван-\nтажувач", 88, BOOT),
        ("таб-\nлиця", 56, MAP),
        ("NVS", 70, DATA),
        ("ваш\nдодаток", 180, APP),
        ("OTA-\nслот", 150, APP),
        ("файлова\nсистема", 130, FS),
    ]
    p.append(text(x, y - 12, "0x0", size=10, color=MUTED, anchor="start"))
    p.append(text(W - 40, y - 12, "кінець Flash", size=10, color=MUTED, anchor="end"))
    for lab, w, (fill, stroke) in zones:
        p.append(fitbox(x, y, w, h, lab, size=12, fill=fill, stroke=stroke, sw=1.6, bold=True, color=stroke))
        x += w

    # підпис-висновок під смугою
    bx, by, bw, bh = 120, 210, 520, 64
    p.append(rect(bx, by, bw, bh, fill=MAP[0], stroke=MAP[1], sw=1.4))
    p.append(mtext(bx + bw / 2, by + 24,
                   ["Хто де лежить, каже маленька ТАБЛИЦЯ РОЗДІЛІВ на початку Flash:",
                    "«ось тут завантажувач, тут додаток, тут NVS, тут файли».",
                    "Без неї чіп не знав би навіть, звідки запускати програму."],
                   size=11, color=INK, lh=1.4))

    render(os.path.join(OUT, "why-partition.svg"), W, H, *p,
           title="Flash — не один моноліт, а низка названих ділянок")


# ── table: рядок на ділянку — ім'я, тип, зсув, розмір ──────────────────────────
# Ідея: показати, що таблиця — це короткий список, де рядок описує зону
# чотирма числами, і що завантажувач читає її першою.

def fig_table():
    W, H = 720, 300
    p = []
    cols = ["ім'я", "тип", "зсув", "розмір"]
    rows = [
        ("nvs",     "data", "0x9000",  "0x6000"),
        ("factory", "app",  "0x10000", "0x100000"),
        ("storage", "data", "0x110000","0x80000"),
    ]
    x0, y0 = 120, 90
    cw = [110, 90, 130, 130]
    rh = 38
    # заголовок
    x = x0
    for i, c in enumerate(cols):
        p.append(rect(x, y0, cw[i], rh, fill="#eceff4", stroke=LINE, sw=1.3, rx=0))
        p.append(text(x + cw[i] / 2, y0 + rh / 2 + 5, c, size=12, color=INK, bold=True))
        x += cw[i]
    # рядки
    for r, row in enumerate(rows):
        x = x0
        y = y0 + (r + 1) * rh
        for i, cell in enumerate(row):
            fill = APP[0] if (i == 1 and cell == "app") else (DATA[0] if i == 1 else BG)
            p.append(rect(x, y, cw[i], rh, fill=fill, stroke=LINE, sw=1.0, rx=0))
            p.append(text(x + cw[i] / 2, y + rh / 2 + 5, cell, size=11, color=INK))
            x += cw[i]

    p.append(text(W / 2, y0 + 4 * rh + 36,
                  "Чотири числа на рядок — і це вся «магія».", size=12, color=MUTED, italic=True))
    p.append(text(W / 2, y0 + 4 * rh + 58,
                  "Завантажувач читає цей список першим, щоб знайти ваш додаток.",
                  size=11, color=INK))

    render(os.path.join(OUT, "table.svg"), W, H, *p,
           title="Таблиця розділів — короткий список: рядок на ділянку")


# ── layout: типова розкладка ESP32 з адресами, службове на дні ────────────────
# Ідея: вертикальна карта від низьких адрес угору; службове внизу на фіксованих
# адресах, код у середині, дані ростуть угору.

def fig_layout():
    W, H = 700, 400
    p = []
    bx, bw = 200, 420
    rows = [
        ("завантажувач",          "0x1000",  BOOT),
        ("таблиця розділів",      "0x8000",  MAP),
        ("NVS — налаштування",    "0x9000",  DATA),
        ("otadata — активний слот","0xF000",  DATA),
        ("ваш додаток (factory)", "0x10000", APP),
        ("файлова система",       "…",       FS),
    ]
    rh = 46
    y = 70
    for lab, addr, (fill, stroke) in rows:
        p.append(rect(bx, y, bw, rh, fill=fill, stroke=stroke, sw=1.6))
        p.append(text(bx + 14, y + rh / 2 + 5, lab, size=12, color=stroke, anchor="start", bold=True))
        p.append(text(bx - 12, y + rh / 2 + 5, addr, size=11, color=MUTED, anchor="end"))
        y += rh

    # вісь адрес угору
    p.append(arrow(bx - 100, y - 8, bx - 100, 78, color=MUTED, sw=1.6))
    p.append(text(bx - 100, y + 14, "0x0", size=10, color=MUTED))
    p.append(text(bx - 116, (78 + y) / 2, "адреси", size=10, color=MUTED, anchor="middle"))

    p.append(text(W / 2, y + 30,
                  "Службове — на дні (фіксовані адреси); код — вище; дані ростуть угору.",
                  size=11, color=INK))

    render(os.path.join(OUT, "layout.svg"), W, H, *p,
           title="Типова розкладка Flash на ESP32")


# ── types: два роди розділів — app (код) і data (дані) ─────────────────────────
# Ідея: дві колонки; ліворуч те, що завантажувач ЗАПУСКАЄ; праворуч те, що він
# лише надає програмі.

def fig_types():
    W, H = 720, 340
    p = []
    colw = 280
    lx, rx = 70, W - 70 - colw
    top, ih = 110, 40
    gap = 8

    def column(x, head, headcol, items):
        out = [rect(x, 70, colw, 30, fill=headcol[0], stroke=headcol[1], sw=1.6)]
        out.append(text(x + colw / 2, 90, head, size=13, color=headcol[1], bold=True))
        yy = top
        for name, note in items:
            out.append(rect(x, yy, colw, ih, fill=headcol[0], stroke=headcol[1], sw=1.2))
            out.append(text(x + 12, yy + ih / 2 + 4, name, size=12, color=INK, anchor="start", bold=True))
            out.append(text(x + colw - 12, yy + ih / 2 + 4, note, size=10, color=MUTED, anchor="end"))
            yy += ih + gap
        return out

    p += column(lx, "app — КОД, який запускають", APP, [
        ("factory", "основна прошивка"),
        ("ota_0", "слот оновлення"),
        ("ota_1", "слот оновлення"),
    ])
    p += column(rx, "data — ДАНІ для програми", DATA, [
        ("nvs", "ключ–значення"),
        ("spiffs / littlefs", "файлова система"),
        ("otadata", "який слот активний"),
        ("phy", "калібрування радіо"),
    ])

    p.append(text(W / 2, H - 26,
                  "Завантажувач вибирає, який app пускати; data лише надає програмі.",
                  size=11, color=INK))

    render(os.path.join(OUT, "types.svg"), W, H, *p,
           title="Два роди розділів: app і data")


# ── alignment: межі клацають на сектори, бо стирання — секторне ────────────────
# Ідея: показати, чому межа розділу мусить лягти на межу сектора: інакше стирання
# одного розділу зачепить сусіда, що ділить із ним сектор.

def fig_alignment():
    W, H = 720, 320
    p = []
    x0, sw_sec = 90, 60          # ширина одного сектора
    n = 9
    ytop, hh = 110, 56

    # сектори
    for i in range(n):
        x = x0 + i * sw_sec
        p.append(rect(x, ytop, sw_sec, hh, fill="#fafafa", stroke="#cfcfcf", sw=1.0, rx=0))
        p.append(text(x + sw_sec / 2, ytop + hh / 2 + 4, "4 КБ", size=9, color="#bcbcbc") if i == 0 else "")
    p.append(text(x0 + n * sw_sec / 2, ytop - 26, "Flash поділений на сектори по 4 КБ (стирання — цілим сектором)",
                  size=11, color=MUTED, italic=True))

    # ПРАВИЛЬНО: розділи лягають рівно на межі секторів
    gy = ytop + hh + 34
    p.append(text(x0, gy - 10, "Правильно: межі збігаються з межами секторів", size=11, color=FIELD, anchor="start", bold=True))
    p.append(rect(x0, gy, 4 * sw_sec, 30, fill=APP[0], stroke=APP[1], sw=1.6))
    p.append(text(x0 + 2 * sw_sec, gy + 20, "розділ A", size=11, color=APP[1]))
    p.append(rect(x0 + 4 * sw_sec, gy, 5 * sw_sec, 30, fill=DATA[0], stroke=DATA[1], sw=1.6))
    p.append(text(x0 + 4 * sw_sec + 2.5 * sw_sec, gy + 20, "розділ B", size=11, color=DATA[1]))

    # НЕПРАВИЛЬНО: межа посеред сектора — спільний сектор
    by = gy + 70
    p.append(text(x0, by - 10, "Неправильно: межа посеред сектора → A і B ділять один сектор", size=11, color=POS, anchor="start", bold=True))
    cut = 4 * sw_sec + sw_sec * 0.5
    p.append(rect(x0, by, cut, 30, fill=APP[0], stroke=APP[1], sw=1.6))
    p.append(rect(x0 + cut, by, 5 * sw_sec - sw_sec * 0.5, 30, fill=DATA[0], stroke=DATA[1], sw=1.6))
    # підсвітити спільний сектор
    shared_x = x0 + 4 * sw_sec
    p.append(rect(shared_x, by - 3, sw_sec, 36, fill="none", stroke=POS, sw=2.2))
    p.append(text(shared_x + sw_sec / 2, by + 50, "стерти A — зіпсувати B", size=10, color=POS))

    render(os.path.join(OUT, "alignment.svg"), W, H, *p,
           title="Межі розділів «клацають» на сектори")


# ── custom: своя таблиця — з CSV у двійкову карту Flash ────────────────────────
# Ідея: людина пише читабельний CSV, збірка перетворює його на двійкову таблицю,
# яку кладуть на 0x8000 і читає завантажувач.

def fig_custom():
    W, H = 740, 300
    p = []
    y = 150
    # CSV
    cw, ch = 230, 120
    cx = 60
    p.append(rect(cx, y - ch / 2, cw, ch, fill=FILL, stroke=LINE, sw=1.5))
    p.append(text(cx + cw / 2, y - ch / 2 - 12, "CSV (текст, який пишете ви)", size=11, color=INK, bold=True))
    csv_lines = ["nvs,     data, nvs,  0x9000,  0x6000",
                 "factory, app,  ,     0x10000, 1M",
                 "storage, data, ,     ,        1M"]
    for i, ln in enumerate(csv_lines):
        p.append(text(cx + 12, y - 22 + i * 22, ln, size=10, color=MUTED, anchor="start"))

    # збірка
    bx = cx + cw + 60
    bw2 = 120
    p.append(fitbox(bx, y - 26, bw2, 52, "збірка\n(idf.py)", size=12, fill=MAP[0], stroke=MAP[1], sw=1.6, bold=True, color=MAP[1]))
    p.append(arrow(cx + cw + 6, y, bx - 4, y, color=INK, sw=1.8))

    # двійкова таблиця у Flash
    fx = bx + bw2 + 60
    fw = 150
    p.append(arrow(bx + bw2 + 4, y, fx - 4, y, color=INK, sw=1.8))
    p.append(fitbox(fx, y - 36, fw, 72, "двійкова таблиця\nу Flash @ 0x8000", size=12, fill=DATA[0], stroke=DATA[1], sw=1.6, bold=True, color=DATA[1]))
    p.append(text(fx + fw / 2, y + 64, "її читає завантажувач", size=10, color=MUTED))

    p.append(text(W / 2, H - 22,
                  "Людина працює з читабельним текстом, машина — з двійковим форматом.",
                  size=11, color=INK))

    render(os.path.join(OUT, "custom.svg"), W, H, *p,
           title="Своя таблиця: з CSV у двійкову карту Flash")


# ── csv-anatomy (вставка): анатомія рядка CSV ─────────────────────────────────
# Ідея: розкласти один рядок CSV на п'ять підписаних полів.

def fig_csv_anatomy():
    W, H = 740, 240
    p = []
    fields = [
        ("factory", "ім'я", "як ви її звете"),
        ("app",     "тип",  "app / data"),
        ("factory", "підтип", "уточнення роду"),
        ("0x10000", "зсув",  "звідки починається"),
        ("1M",      "розмір","скільки байтів"),
    ]
    x = 40
    fw = 132
    y = 110
    centers = []
    for val, name, note in fields:
        p.append(rect(x, y, fw, 44, fill=FILL, stroke=LINE, sw=1.5))
        p.append(text(x + fw / 2, y + 28, val, size=13, color=INK, bold=True))
        p.append(text(x + fw / 2, y - 10, name, size=12, color=NEG, bold=True))
        p.append(text(x + fw / 2, y + 64, note, size=9, color=MUTED))
        centers.append(x + fw / 2)
        x += fw + 6
    # кома-роздільники
    for i in range(len(fields) - 1):
        cxk = (centers[i] + centers[i + 1]) / 2
        p.append(text(cxk, y + 28, ",", size=16, color=POS, bold=True))

    p.append(text(W / 2, H - 26,
                  "Збірка перетворює цей рядок на запис двійкової таблиці у Flash @ 0x8000.",
                  size=11, color=INK))

    render(os.path.join(OUT, "csv-anatomy.svg"), W, H, *p,
           title="Анатомія рядка CSV: п'ять полів")


# ── offsets (вставка): зсуви складаються в ланцюжок ───────────────────────────
# Ідея: зсув кожного = зсув + розмір попереднього; межі кратні 4 КБ / 64 КБ;
# поле offset можна лишити порожнім.

def fig_offsets():
    W, H = 720, 300
    p = []
    rows = [
        ("nvs",     "0x9000",  "0x6000",  DATA),
        ("factory", "0xF000",  "0x100000",APP),
        ("storage", "0x10F000","0x80000", DATA),
    ]
    # навмисна помилка в прикладі? Ні — порахуймо чесний ланцюжок:
    rows = [
        ("nvs",     0x9000,  0x6000,  DATA),
        ("factory", 0x10000, 0x100000,APP),
        ("storage", 0x110000,0x80000, DATA),
    ]
    x0, y0 = 80, 100
    bw, rh = 200, 46
    for i, (name, off, size, (fill, stroke)) in enumerate(rows):
        y = y0 + i * (rh + 22)
        p.append(rect(x0, y, bw, rh, fill=fill, stroke=stroke, sw=1.6))
        p.append(text(x0 + bw / 2, y + rh / 2 + 5, name, size=12, color=stroke, bold=True))
        p.append(text(x0 + bw + 14, y + 14, "зсув  0x%X" % off, size=11, color=INK, anchor="start"))
        p.append(text(x0 + bw + 14, y + 34, "розмір 0x%X" % size, size=11, color=MUTED, anchor="start"))
        # стрілка «+ розмір» до наступного зсуву
        if i < len(rows) - 1:
            p.append(arrow(x0 + bw / 2, y + rh, x0 + bw / 2, y + rh + 22, color=stroke, sw=1.6))
            p.append(text(x0 + bw / 2 + 90, y + rh + 16, "+ розмір → наступний зсув", size=10, color=MUTED))

    p.append(text(W / 2, H - 40, "зсув кожного = зсув попереднього + його розмір; межі кратні 4 КБ (app — 64 КБ)",
                  size=11, color=INK))
    p.append(text(W / 2, H - 20, "поле offset можна лишити порожнім — збірка покладе розділ одразу за попереднім",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "offsets.svg"), W, H, *p,
           title="Зсуви складаються в ланцюжок")


if __name__ == "__main__":
    fig_why_partition()
    fig_table()
    fig_layout()
    fig_types()
    fig_alignment()
    fig_custom()
    fig_csv_anatomy()
    fig_offsets()
    print("OK: figures written to", OUT)
