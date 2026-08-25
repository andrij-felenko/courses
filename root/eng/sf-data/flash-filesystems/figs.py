# -*- coding: utf-8 -*-
"""Фігури до теми «Файлові системи Flash» (і до вставки hist-fat).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── tree: файлова система як дерево іменованих файлів у теках ────────────────
# Ідея: знайомий образ — корінь, теки-гілки, файли-листя; над файлами звичні дії.
def fig_tree():
    W, H = 660, 380
    p = []
    x = 70
    rows = [
        (0, "/",            "корінь",              INK,   True),
        (1, "log.txt",      "журнал, що росте",    FIELD, False),
        (1, "config.json",  "налаштування",        FIELD, False),
        (1, "photo.jpg",    "40 КБ",               FIELD, False),
        (1, "web/",         "тека",                NEG,   True),
        (2, "index.html",   "сторінка",            FIELD, False),
        (2, "style.css",    "стилі",               FIELD, False),
    ]
    y = 70
    step = 38
    for depth, name, note, col, bold in rows:
        tx = x + depth * 34
        bullet = "" if depth == 0 else "├─ "
        p.append(text(tx, y, bullet + name, size=14, color=col, anchor="start", bold=bold))
        p.append(text(x + 360, y, note, size=11, color=MUTED, anchor="start"))
        y += step
    # тонкі вертикалі-зв'язки дерева
    p.append(line(x + 40, 60, x + 40, 70 + 3 * step + 4, color="#dcdcdc", sw=1.4))
    p.append(line(x + 74, 70 + 4 * step + 6, x + 74, 70 + 5 * step + 4, color="#dcdcdc", sw=1.4))

    p.append(text(W / 2, H - 22,
                  "над файлами: створити · відкрити · читати · дописати · стерти",
                  size=11, color=INK, italic=True))

    render(os.path.join(IMG, "tree.svg"), W, H, *p,
           title="Файлова система: іменовані файли в теках")


# ── namemap: ФС тримає карту «ім'я → блоки» і список вільного місця ──────────
# Ідея: ти бачиш ім'я; ФС знає, з яких розкиданих блоків зібрати файл.
def fig_namemap():
    W, H = 720, 360
    p = []

    # зліва — погляд програми: просто ім'я
    nb, nw, nh = textbox(120, 130, "log.txt", size=15, bold=True,
                         fill="#eef2f7", stroke=INK, sw=1.8, pad=16)
    p.append(nb)
    p.append(text(120, 185, "що бачить ваша програма", size=10.5, color=MUTED))

    # праворуч — фізичні блоки Flash, файл розкиданий по 1,2,5
    bx, by, bw, bh, gap = 360, 90, 56, 44, 8
    owners = ["log", "log", "·", "·", "log", "·", "·"]
    for i, who in enumerate(owners):
        cx = bx + i % 4 * (bw + gap)
        cy = by + (i // 4) * (bh + 26)
        mine = who == "log"
        p.append(rect(cx, cy, bw, bh,
                      fill="#eafaf0" if mine else "#fafafa",
                      stroke=FIELD if mine else "#cccccc",
                      sw=1.8 if mine else 1.2, rx=4))
        p.append(text(cx + bw / 2, cy + bh / 2 + 4,
                      "log" if mine else "вільн.",
                      size=11, color=INK if mine else MUTED,
                      bold=mine))
        p.append(text(cx + bw / 2, cy - 6, "блок %d" % i, size=9, color=MUTED))

    # стрілка від імені до карти
    p.append(arrow(120 + nw / 2, 130, bx - 8, 112, color=INK, sw=1.8))
    p.append(text((120 + nw / 2 + bx) / 2, 104, "карта", size=11, color=INK, bold=True))

    p.append(text(W / 2, H - 20,
                  "ФС пам'ятає порядок 1→2→5 і збирає файл; вільні блоки — про запас",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "namemap.svg"), W, H, *p,
           title="Файлова система: карта «ім'я → блоки» + вільне місце")


# ── flash-aware: ПК-ФС зношує один сектор, Flash-свідома розмазує ────────────
# Ідея: переписування службової таблиці НА МІСЦІ б'є один сектор; copy-on-write
# розкидає записи по чипу.
def fig_flash_aware():
    W, H = 720, 380
    p = []
    cols = 6
    cw, ch, gap = 86, 50, 10
    x0 = (W - (cols * cw + (cols - 1) * gap)) / 2

    def strip(y, hits, label, col):
        p.append(text(x0, y - 12, label, size=12, color=INK, anchor="start", bold=True))
        for i in range(cols):
            cx = x0 + i * (cw + gap)
            n = hits[i]
            hot = n >= 5
            fill = "#fdecea" if hot else ("#eafaf0" if n else "#fafafa")
            stroke = POS if hot else ("#cccccc")
            p.append(rect(cx, y, cw, ch, fill=fill, stroke=stroke,
                          sw=2 if hot else 1.2, rx=4))
            tag = "×%d" % n if n else "—"
            p.append(text(cx + cw / 2, y + ch / 2 + 4, tag,
                          size=12, color=POS if hot else MUTED, bold=hot))

    # ПК-стиль: уся правка в один сектор
    strip(80, [0, 0, 9, 0, 0, 0], "ПК-стиль (FAT): таблиця завжди на тому ж місці", POS)
    p.append(text(W / 2, 150, "один сектор лупиться раз у раз → зноситься першим",
                  size=11, color=POS, italic=True))

    # Flash-свідома: записи розходяться по чипу
    strip(220, [2, 1, 2, 2, 1, 2], "Flash-свідома (LittleFS): копія в чисте місце", FIELD)
    p.append(text(W / 2, 290, "записи розмазані по чипу → знос рівний, збій не псує старого",
                  size=11, color=FIELD, italic=True))

    p.append(text(W / 2, H - 18, "число = скільки разів стерто цей сектор",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "flash-aware.svg"), W, H, *p,
           title="Чому ПК-ФС зношує Flash, а Flash-свідома — ні")


# ── one-step-switch: «спершу нове поряд, тоді один крок-перемикач» ───────────
# Ідея: copy-on-write — старе ціле, нове пишеться поряд, останній атомарний крок
# перемикає вказівник; збій до/після лишає цілий файл, «півфайлу» не буває.
def fig_switch():
    W, H = 720, 360
    p = []
    yA, yB, h, w = 110, 230, 56, 150
    ax, bx = 120, 360

    # старий вміст (цілий)
    p.append(rect(ax, yA, w, h, fill="#eef2f7", stroke=NEG, sw=1.8, rx=6))
    p.append(text(ax + w / 2, yA + h / 2 + 4, "старий\n(цілий)".split("\n")[0],
                  size=12, color=INK, bold=True))
    p.append(text(ax + w / 2, yA + h / 2 + 18, "цілий", size=10, color=MUTED))

    # новий вміст поряд (теж цілий, у чистому місці)
    p.append(rect(ax, yB, w, h, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(ax + w / 2, yB + h / 2 - 2, "новий", size=12, color=INK, bold=True))
    p.append(text(ax + w / 2, yB + h / 2 + 14, "у чистому місці", size=10, color=MUTED))

    # вказівник «дійсний зараз» + один крок-перемикач
    pb, pw, ph = bx, 170, 56
    p.append(rect(pb, yA, pw, ph, fill="#fff8e1", stroke="#b8860b", sw=1.8, rx=6))
    p.append(text(pb + pw / 2, yA + ph / 2 + 4, "вказівник:\nдійсний зараз".split("\n")[0],
                  size=12, color=INK, bold=True))
    p.append(text(pb + pw / 2, yA + ph / 2 + 18, "дійсний зараз", size=10, color=MUTED))

    p.append(arrow(ax + w, yA + h / 2, pb - 6, yA + ph / 2, color=NEG, sw=1.8))
    # пунктир — куди перемкнеться одним кроком
    p.append(line(pb + pw / 2, yA + ph, pb + pw / 2, yB + h / 2, color="#b8860b", sw=1.6, dash="5,4"))
    p.append(arrow(pb + pw / 2, yB + h / 2, ax + w + 4, yB + h / 2, color="#b8860b", sw=1.8))
    p.append(text(pb + pw / 2 + 10, (yA + ph + yB) / 2, "один крок-перемикач",
                  size=10.5, color="#b8860b", anchor="start", bold=True))

    p.append(text(W / 2, H - 20,
                  "гасне струм до кроку — лишається старий; після — новий; «півфайлу» немає",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "one-step-switch.svg"), W, H, *p,
           title="Copy-on-write: нове поряд, тоді один крок-перемикач")


# ── compare: SPIFFS проти LittleFS — чому новим проєктам LittleFS ────────────
# Ідея: рядок-за-рядком зіставлення чотирьох властивостей, що вирішують вибір.
def fig_compare():
    W, H = 720, 340
    p = []
    x0 = 40
    cols = [("властивість", 230), ("SPIFFS (старіша)", 220), ("LittleFS (сучасна)", 220)]
    rowh = 40
    y = 64

    # шапка
    x = x0
    heads = [INK, POS, FIELD]
    for (name, w), col in zip(cols, heads):
        p.append(rect(x, y, w, rowh, fill="#eef2f7", stroke=INK, sw=1.3, rx=0))
        p.append(text(x + w / 2, y + rowh / 2 + 4, name, size=11, color=col, bold=True))
        x += w
    y += rowh

    rows = [
        ("теки", "плоска (імітація)", "справжні теки"),
        ("втрата живлення", "може пошкодити", "стійка (copy-on-write)"),
        ("під заповнення", "помітно гальмує", "тримає швидкість"),
        ("статус", "виходить з ужитку", "рекомендована"),
    ]
    for prop, sp, lf in rows:
        x = x0
        for (name, w), v, col in zip(cols, (prop, sp, lf), (INK, POS, FIELD)):
            first = name == "властивість"
            fill = "#f6f7f9" if first else ("#fdf0ee" if col == POS else "#f0faf3")
            p.append(rect(x, y, w, rowh, fill=fill, stroke="#d0d5db", sw=1.0, rx=0))
            p.append(text(x + w / 2, y + rowh / 2 + 4, v, size=11,
                          color=INK if first else col, bold=first))
            x += w
        y += rowh

    p.append(text(W / 2, y + 26, "для нового пристрою — LittleFS; SPIFFS лишився в старих проєктах",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "compare.svg"), W, H, *p,
           title="SPIFFS проти LittleFS")


# ── decision: що куди класти — NVS / LittleFS / SD ──────────────────────────
# Ідея: вибір сховища читається за двома питаннями — розмір і знімність.
def fig_decision():
    W, H = 720, 380
    p = []
    cx = W / 2

    q1, w1, h1 = textbox(cx, 70, "наскільки воно велике?", size=13, bold=True,
                         fill="#fff8e1", stroke="#b8860b", sw=1.8, pad=12)
    p.append(q1)

    # три цілі
    def dest(x, title, sub, col, fill):
        bw, bh = 190, 86
        p.append(rect(x - bw / 2, 220, bw, bh, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(x, 248, title, size=14, color=INK, bold=True))
        p.append(text(x, 270, sub.split("\n")[0], size=10.5, color=MUTED))
        p.append(text(x, 286, sub.split("\n")[1], size=10.5, color=MUTED))
        return x

    xN, xL, xS = 150, cx, 570
    dest(xN, "NVS", "дрібне й іменоване\nгучність, ключі", NEG, "#eef2f7")
    dest(xL, "LittleFS", "файлоподібне, внутрішнє\nжурнал, веб, звук", FIELD, "#eafaf0")
    dest(xS, "SD-картка (FAT)", "велике або знімне\nвідео, гігабайти", POS, "#fdecea")

    # ребра рішення з підписами
    p.append(arrow(cx - 40, 70 + h1 / 2, xN, 214, color=INK, sw=1.6))
    p.append(text((cx - 40 + xN) / 2 - 6, 150, "маленьке", size=10, color=MUTED, anchor="end"))
    p.append(arrow(cx, 70 + h1 / 2, xL, 214, color=INK, sw=1.6))
    p.append(text(cx + 8, 150, "середнє,\nфайл", size=10, color=MUTED, anchor="start"))
    p.append(arrow(cx + 40, 70 + h1 / 2, xS, 214, color=INK, sw=1.6))
    p.append(text((cx + 40 + xS) / 2 + 6, 150, "велике /\nзнімне", size=10, color=MUTED, anchor="start"))

    p.append(text(W / 2, H - 18, "друге питання: чи треба його виймати? → так схиляє до SD",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "decision.svg"), W, H, *p,
           title="Що куди класти: NVS · LittleFS · SD-картка")


# ════════════════ фігури вставки hist-fat ════════════════════════════════════

# ── chain: ланцюг кластерів — таблиця зчіплює клапті файлу ───────────────────
def fig_chain():
    W, H = 720, 320
    p = []
    # диск як ряд кластерів 0..7; файл — 2 → 3 → 7
    cn = 8
    cw, gap = 70, 8
    x0 = (W - (cn * cw + (cn - 1) * gap)) / 2
    y = 90
    ch = 56
    chain = {2: 3, 3: 7, 7: None}
    for i in range(cn):
        cx = x0 + i * (cw + gap)
        mine = i in chain
        p.append(rect(cx, y, cw, ch,
                      fill="#eafaf0" if mine else "#fafafa",
                      stroke=FIELD if mine else "#cccccc",
                      sw=1.8 if mine else 1.2, rx=4))
        p.append(text(cx + cw / 2, y - 8, str(i), size=10, color=MUTED))
        p.append(text(cx + cw / 2, y + ch / 2 + 4,
                      "лист" if mine else "·", size=11,
                      color=INK if mine else MUTED, bold=mine))

    # дуги ланцюга 2→3→7 (через таблицю)
    def cxof(i):
        return x0 + i * (cw + gap) + cw / 2
    for a, b in [(2, 3), (3, 7)]:
        p.append(arrow(cxof(a), y + ch + 6, cxof(b), y + ch + 6, color=POS, sw=2))
    p.append(text(cxof(7) + cw / 2 + 6, y + ch + 10, "кінець",
                  size=10, color=POS, anchor="start", bold=True))

    # таблиця-підпис «наступний»
    p.append(text(W / 2, y + ch + 70,
                  "таблиця FAT: кластер 2 → 3,  3 → 7,  7 → кінець",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, y + ch + 96,
                  "ланцюг зчіплює розкидані клапті в один файл — звідси й назва",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "chain.svg"), W, H, *p,
           title="Ланцюг кластерів: таблиця зчіплює клапті файлу")


# ── timeline: шлях FAT у часі 1977 → 1980 → 1984 → 1996 → нині ───────────────
def fig_timeline():
    W, H = 760, 300
    p = []
    y = 140
    p.append(line(60, y, W - 60, y, color=INK, sw=2))
    p.append(arrow(W - 70, y, W - 56, y, color=INK, sw=2))

    marks = [
        (110, "1977–78", "перша FAT\nМ. Макдональд", NEG),
        (270, "1980", "FAT12, шлях у 86-DOS\nТ. Патерсон", FIELD),
        (420, "1984+", "FAT16\nжорсткі диски", MUTED),
        (560, "1996", "FAT32\nWindows 95", MUTED),
        (690, "нині", "знімні носії\nдонині", POS),
    ]
    for x, yr, lab, col in marks:
        p.append(circle(x, y, 7, fill=col, stroke=col, sw=1.5))
        p.append(text(x, y - 18, yr, size=12, color=INK, bold=True))
        a, b = lab.split("\n")
        p.append(text(x, y + 30, a, size=10, color=MUTED))
        p.append(text(x, y + 45, b, size=10, color=MUTED))

    p.append(text(W / 2, H - 18,
                  "ідея й перша таблиця — Макдональд; дорога в DOS і FAT12 — Патерсон",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "timeline.svg"), W, H, *p,
           title="Шлях FAT у часі")


# ── everywhere: FAT усюди — дискета, USB, SD, картка фотоапарата ─────────────
def fig_everywhere():
    W, H = 720, 320
    p = []
    cx = W / 2
    hub, hw, hh = textbox(cx, 160, "FAT\nчитають усі", size=14, bold=True,
                          fill="#fff8e1", stroke="#b8860b", sw=2, pad=16)
    p.append(hub)

    nodes = [
        (140, 90,  "дискета", NEG),
        (140, 240, "USB-флешка", FIELD),
        (580, 90,  "SD-картка", POS),
        (580, 240, "картка фото", MUTED),
    ]
    for x, y, lab, col in nodes:
        b, bw, bh = textbox(x, y, lab, size=12, bold=True,
                            fill=BG, stroke=col, sw=1.6, pad=12)
        p.append(b)
        p.append(arrow(x + (bw / 2 if x < cx else -bw / 2), y,
                       cx + (-hw / 2 if x < cx else hw / 2),
                       160 + (-20 if y < 160 else 20), color=col, sw=1.6))

    p.append(text(W / 2, H - 18,
                  "знімне мусить читатися скрізь → спільна мова → FAT (SD-стандарт її приписує)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "everywhere.svg"), W, H, *p,
           title="FAT усюди: знімні носії всіх епох")


if __name__ == "__main__":
    fig_tree()
    fig_namemap()
    fig_flash_aware()
    fig_switch()
    fig_compare()
    fig_decision()
    fig_chain()
    fig_timeline()
    fig_everywhere()
    print("OK: figures written to", IMG)
