# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «RPC у вбудованих системах»
(guide/embedded/zvyazok/rpc-embedded).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Ілюзія локального виклику: заглушка ховає мережу ────────────────────────
# Ідея: код на обох боках викликає/реалізує ЗВИЧАЙНУ функцію. Між ними —
# заглушка (пакує аргументи в байти) і диспетчер (розпаковує й кличе справжню).
# Дріт між ними невидимий для прикладного коду — у цьому й суть, і пастка.
def fig_illusion():
    W, H = 880, 430
    f = []
    f.append(text(W / 2, 30, "RPC: виклик функції, що насправді живе на іншому пристрої",
                  16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "прикладний код кличе звичайну функцію — заглушка нишком перетворює виклик на кадр і назад",
                  11.5, MUTED, "middle", italic=True))

    xL, xR = 180, 700           # центри двох колонок
    colw = 250

    # ── ліва сторона: клієнт ──
    f.append(text(xL, 86, "клієнт (наземна станція / задача)", 12.5, INK, "middle", bold=True))
    b1 = textbox(xL, 122, "val = read_sensor(3);", 12.5, fill="#eaf0fd",
                 stroke=NEG, color=NEG, bold=True, min_w=colw)
    f.append(b1[0])
    f.append(text(xL, 150, "звичайний виклик у коді", 10.5, MUTED, "middle", italic=True))
    b2 = textbox(xL, 190, "заглушка (stub)\nпакує №3 у байти", 11.5, fill=FILL,
                 stroke=LINE, min_w=colw)
    f.append(b2[0])
    f.append(arrow(xL, 138, xL, 174, color=NEG, sw=2.0))

    # ── права сторона: сервер ──
    f.append(text(xR, 86, "сервер (давач / периферійний МК)", 12.5, INK, "middle", bold=True))
    b3 = textbox(xR, 122, "int read_sensor(int n){\n  return adc[n];\n}", 11.5,
                 fill="#e9f7ef", stroke=FIELD, color=FIELD, bold=True, min_w=colw)
    f.append(b3[0])
    f.append(text(xR, 162, "справжня реалізація", 10.5, MUTED, "middle", italic=True))
    b4 = textbox(xR, 200, "диспетчер\nрозбирає кадр, кличе функцію", 11.5, fill=FILL,
                 stroke=LINE, min_w=colw)
    f.append(b4[0])
    f.append(arrow(xR, 184, xR, 144, color=FIELD, sw=2.0))

    # ── дріт між заглушкою і диспетчером ──
    f.append(arrow(xL + colw / 2, 184, xR - colw / 2, 194, color=POS, sw=2.2))
    f.append(text(W / 2, 176, "запит: «функція №7, аргумент 3»", 11, POS, "middle", bold=True))
    f.append(arrow(xR - colw / 2, 214, xL + colw / 2, 204, color=POS, sw=2.2))
    f.append(text(W / 2, 230, "відповідь: «результат = 512»", 11, POS, "middle", bold=True))

    # межа «тут — мережа»
    f.append(line(W / 2, 250, W / 2, H - 70, color=MUTED, sw=1.4, dash="4,5"))
    f.append(text(W / 2, H - 56, "↑ невидимий для прикладного коду дріт: UART, радіо, шина ↑",
                  11, MUTED, "middle", italic=True))

    f.append(text(W / 2, H - 30,
                  "Заглушка й диспетчер — це весь RPC: одна перетворює виклик на байти, друга — байти назад на виклик.",
                  11.5, INK, "middle", italic=True))
    f.append(text(W / 2, H - 12,
                  "Ілюзія зручна, але дріт не зникає: він може загубити запит, відповідь або впасти посередині.",
                  11, POS, "middle", italic=True))
    render(os.path.join(IMG, "rpc-illusion.svg"), W, H, *f)


# ── 2. Шлях одного виклику + три біди, яких нема в локального ───────────────────
# Ідея: запит із ID летить, відповідь вертається з тим самим ID. Але: запит може
# згинути (таймаут → повтор), відповідь може згинути (повтор → ПОВТОРНЕ виконання!),
# і саме тому потрібні ID + ідемпотентність. Це той самий каркас, що в ARQ.
def fig_lifecycle():
    W, H = 880, 520
    f = []
    f.append(text(W / 2, 30, "Шлях одного виклику — і три біди, яких у локальної функції немає",
                  16.0, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "ID звʼязує запит із відповіддю; таймер ловить втрату; але загублена відповідь → повторне виконання",
                  11.0, MUTED, "middle", italic=True))

    xc, xs = 175, 705
    top, bot = 90, H - 56
    f.append(text(xc, top - 12, "клієнт", 13, INK, "middle", bold=True))
    f.append(text(xs, top - 12, "сервер", 13, INK, "middle", bold=True))
    f.append(line(xc, top, xc, bot, color=MUTED, sw=1.6, dash="3,4"))
    f.append(line(xs, top, xs, bot, color=MUTED, sw=1.6, dash="3,4"))

    def msg(y0, y1, label, col, left=True, ok=True):
        if left:
            x0, x1 = xc + 8, xs - 8
        else:
            x0, x1 = xs - 8, xc + 8
        if ok:
            f.append(arrow(x0, y0, x1, y1, color=col, sw=2.2))
        else:
            xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
            f.append(line(x0, y0, xm, ym, color=col, sw=2.2, dash="5,4"))
            f.append(text(xm + 8, ym - 6, "✕", 17, POS, "middle", bold=True))
        lx = x0 + (24 if left else -24)
        f.append(text(lx, y0 - 6, label, 11.0, col, "start" if left else "end", bold=True))

    # A. норма: запит ID=7 → виконання → відповідь ID=7
    y = top + 14
    msg(y, y + 18, "запит ID=7  read(3)", NEG)
    f.append(text(xs + 10, y + 30, "виконав: adc[3]=512", 10.5, FIELD, "start", italic=True))
    msg(y + 34, y + 52, "відповідь ID=7  →512", FIELD, left=False)
    f.append(text(xc - 10, y + 64, "ID збігся → це МОЯ відповідь", 10.5, NEG, "end", italic=True))
    y += 96

    # B. запит згинув → таймаут → повтор → ок
    msg(y, y + 18, "запит ID=8", NEG, ok=False)
    f.append(text(xc - 10, y + 26, "⏱ таймаут", 10.5, POS, "end", italic=True))
    f.append(line(xc - 4, y + 4, xc - 4, y + 34, color=POS, sw=1.3, dash="2,3"))
    y += 50
    msg(y, y + 18, "повтор ID=8", NEG)
    msg(y + 22, y + 40, "відповідь ID=8", FIELD, left=False)
    y += 78

    # C. ПАСТКА: відповідь згинула → повтор → сервер виконує ВДРУГЕ
    msg(y, y + 18, "запит ID=9  motor+10", NEG)
    f.append(text(xs + 10, y + 28, "виконав (мотор +10)", 10.5, FIELD, "start", italic=True))
    msg(y + 32, y + 50, "відповідь ID=9", FIELD, left=False, ok=False)
    f.append(text(xc - 10, y + 60, "⏱ таймаут", 10.5, POS, "end", italic=True))
    y += 74
    msg(y, y + 18, "повтор ID=9", NEG)
    f.append(text(xs + 10, y + 28, "БЕЗ кешу — виконає +10 ще раз!", 10.5, POS, "start", bold=True))
    f.append(text(xs + 10, y + 42, "із кешем ID=9 — лише повторить стару відповідь", 10.0, FIELD, "start", italic=True))

    f.append(text(W / 2, H - 14,
                  "Локальний виклик не губиться й не виконується двічі. Віддалений — губиться; рятують ID + памʼять про вже виконане.",
                  11.0, INK, "middle", italic=True))
    render(os.path.join(IMG, "rpc-lifecycle.svg"), W, H, *f)


# ── 3. Диспетчер на МК: одна таблиця замість дерева if ─────────────────────────
# Ідея: прийшов кадр → дістали ID функції → таблиця функцій дає вказівник →
# викликали обробник. Додати команду = дописати рядок у таблицю, а не гілку if.
def fig_dispatch():
    W, H = 860, 410
    f = []
    f.append(text(W / 2, 30, "Диспетчер на мікроконтролері: номер функції → таблиця → обробник",
                  16.0, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "кадр несе НОМЕР функції; таблиця вказівників веде до потрібного обробника — без дерева if",
                  11.0, MUTED, "middle", italic=True))

    # вхідний кадр
    fx, fy = 60, 110
    parts = [("ID=9", NEG), ("func=2", POS), ("arg=10", FIELD), ("CRC", MUTED)]
    x = fx
    for lbl, col in parts:
        w = 86
        f.append(rect(x, fy, w, 34, fill="#ffffff", stroke=col, sw=1.8, rx=4))
        f.append(text(x + w / 2, fy + 22, lbl, 12, col, "middle", bold=True))
        x += w + 4
    f.append(text(fx, fy - 10, "вхідний кадр запиту", 11, INK, "start", bold=True))
    f.append(text(x + 6, fy + 22, "→", 18, INK, "start", bold=True))

    # таблиця функцій
    tx, ty = 470, 96
    tw, rh = 330, 40
    rows = [("0", "ping()", "→ pong", MUTED),
            ("1", "read_sensor(n)", "→ значення АЦП", FIELD),
            ("2", "set_motor(d)", "→ статус", POS),
            ("3", "reboot()", "→ (без відповіді)", MUTED)]
    f.append(text(tx, ty - 12, "таблиця функцій (масив вказівників)", 11.5, INK, "start", bold=True))
    for i, (n, sig, ret, col) in enumerate(rows):
        y = ty + i * rh
        hl = (n == "2")
        f.append(rect(tx, y, tw, rh - 4,
                      fill=("#fdecea" if hl else "#f4f6f8"),
                      stroke=(POS if hl else LINE), sw=(2.2 if hl else 1.4), rx=4))
        f.append(text(tx + 18, y + 25, "[" + n + "]", 12, (POS if hl else MUTED), "middle", bold=True))
        f.append(text(tx + 46, y + 25, sig, 12, (POS if hl else INK), "start",
                      bold=hl))
        f.append(text(tx + tw - 8, y + 25, ret, 10.5, (POS if hl else MUTED), "end", italic=True))

    # стрілка func=2 → рядок [2]
    f.append(arrow(fx + 90 + 43, fy + 34, tx - 6, ty + 2 * rh + (rh - 4) / 2, color=POS, sw=2.2))
    f.append(text((fx + 90 + 43 + tx) / 2, fy + 88, "func=2 індексує таблицю",
                  10.5, POS, "middle", italic=True))

    # підсумок
    f.append(text(W / 2, H - 40,
                  "table[func](arg) — один рядок коду диспетчеризує будь-яку команду; нова команда = новий рядок таблиці.",
                  11.5, INK, "middle", italic=True))
    f.append(text(W / 2, H - 18,
                  "CRC відсіває побиті кадри до виклику; reboot() може не слати відповіді — клієнт це мусить знати.",
                  11.0, MUTED, "middle", italic=True))
    render(os.path.join(IMG, "rpc-dispatch.svg"), W, H, *f)


# ── 4. Народження RPC: лінія часу від ідеї до сучасних каркасів ───────────────
# Ідея (для вставки hist-rpc-birth): показати, що RPC не «винайшов одну мить
# одна людина», а виростав етапами — ідея поділу ресурсів (White, RFC 707),
# термін і теза (Nelson, 1981), перша робоча система (Courier, 1981),
# знакова стаття-доказ (Birrell & Nelson, 1984), масовий ужиток (Sun ONC),
# сучасний каркас (gRPC, 2015). Кожна віха — окремий тип внеску.
def fig_birth_timeline():
    W, H = 900, 500
    f = []
    f.append(text(W / 2, 30, "Народження RPC: не одна мить, а ланцюг внесків",
                  16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "ідея → термін → перша робоча система → стаття-доказ → масовий ужиток → сучасний каркас",
                  11.5, MUTED, "middle", italic=True))

    # вісь часу
    ax = 70
    bx = W - 40
    ay = 160
    f.append(line(ax, ay, bx, ay, color=INK, sw=2.0))
    f.append(arrow(bx - 24, ay, bx, ay, color=INK, sw=2.0))
    f.append(text(bx, ay - 12, "час", 11, MUTED, "end", italic=True))

    # віхи: (рік, x-частка, заголовок, хто, що це за внесок, колір, вгору?)
    miles = [
        ("1975-76", 0.05, "RFC 707", "Дж. Е. Вайт", "ідея: ділити ресурси\nмережі як виклик функцій", NEG, True),
        ("1981", 0.27, "теза «Remote\nProcedure Call»", "Брюс Дж. Нельсон", "уведено сам ТЕРМІН\n(Карнегі-Меллон)", POS, False),
        ("1981", 0.45, "Courier", "Xerox XNS", "перша робоча RPC,\nщо пішла в продукт", FIELD, True),
        ("1984", 0.62, "«Implementing RPC»", "Бірелл і Нельсон", "стаття-ДОКАЗ, що це\nпрактично (премія ACM)", POS, False),
        ("~1985", 0.78, "ONC / Sun RPC", "Sun, під NFS", "RPC у кожному Unix —\nмасовий ужиток", FIELD, True),
        ("2015", 0.95, "gRPC", "Google, відкрито", "сучасний каркас:\nHTTP/2 + Protocol Buffers", NEG, False),
    ]
    for yr, fx, head, who, what, col, up in miles:
        x = ax + (bx - ax) * fx
        f.append(circle(x, ay, 6, fill="#ffffff", stroke=col, sw=2.4))
        f.append(text(x, ay + (-18 if up else 22), yr, 12, col, "middle", bold=True))
        # картка
        bw, bh = 158, 70
        cy = ay - 120 if up else ay + 84
        bx0 = min(max(x - bw / 2, 4), W - bw - 4)
        f.append(rect(bx0, cy, bw, bh, fill="#f7f9fb", stroke=col, sw=1.6, rx=6))
        f.append(text(bx0 + bw / 2, cy + 17, head.split("\n")[0], 11.5, INK, "middle", bold=True))
        hd2 = head.split("\n")
        yoff = 0
        if len(hd2) > 1:
            f.append(text(bx0 + bw / 2, cy + 30, hd2[1], 11.5, INK, "middle", bold=True))
            yoff = 12
        f.append(text(bx0 + bw / 2, cy + 30 + yoff, who, 10, col, "middle", italic=True))
        wl = what.split("\n")
        for i, ln in enumerate(wl):
            f.append(text(bx0 + bw / 2, cy + 45 + yoff + i * 12, ln, 9.5, MUTED, "middle"))
        # вивідна риска від картки до точки
        ty = cy + bh if up else cy
        f.append(line(x, ay + (-12 if up else 12), x, ty, color=col, sw=1.1, dash="2,3"))

    f.append(text(W / 2, H - 16,
                  "Ідея, термін, перша реалізація, доказ практичності й масовий ужиток — РІЗНІ внески РІЗНИХ людей. RPC ніхто не «винайшов» сам.",
                  11.0, INK, "middle", italic=True))
    render(os.path.join(IMG, "rpc-birth-timeline.svg"), W, H, *f)


# ── 5. Дві сторони ілюзії: геніальна й небезпечна — і вісім хибних припущень ───
# Ідея: та сама обгортка «локального виклику» одночасно ховає рутину (добре)
# і ховає ненадійність мережі (зле). Праворуч — список хибних припущень, які
# ця обгортка непомітно нав'язує. Це стрижень усієї вставки.
def fig_two_faces():
    W, H = 900, 470
    f = []
    f.append(text(W / 2, 30, "Чому та сама ілюзія — і геніальна, і небезпечна",
                  16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "виклик `set_heater(60)` виглядає локальним — обгортка ховає і рутину (добре), і дріт (зле)",
                  11.0, MUTED, "middle", italic=True))

    # центр — сам «локальний» виклик
    f.append(textbox(W / 2, 96, "val = read_sensor(3);", 13, fill="#eef2fb",
                     stroke=INK, color=INK, bold=True, min_w=240)[0])
    f.append(text(W / 2, 124, "виглядає як звичайний локальний виклик", 10.5, MUTED, "middle", italic=True))

    # ліва колонка — геніально
    lx, lw = 40, 360
    f.append(rect(lx, 150, lw, 150, fill="#e9f7ef", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(lx + lw / 2, 174, "ГЕНІАЛЬНО: ховає рутину", 13.5, FIELD, "middle", bold=True))
    good = ["• не вигадуєш формат пакета щоразу",
            "• не пишеш розбір байтів руками",
            "• код обох боків — просто функції",
            "• нову команду додав одним рядком"]
    for i, g in enumerate(good):
        f.append(text(lx + 16, 198 + i * 24, g, 11.5, INK, "start"))

    # права колонка — небезпечно
    rx0 = W - 40 - lw
    f.append(rect(rx0, 150, lw, 150, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    f.append(text(rx0 + lw / 2, 174, "НЕБЕЗПЕЧНО: ховає дріт", 13.5, POS, "middle", bold=True))
    bad = ["• запит може не дійти",
           "• відповідь може згинути → подвійна дія",
           "• сервер може впасти посеред виклику",
           "• затримка, втрати, обрив — не видно в коді"]
    for i, b in enumerate(bad):
        f.append(text(rx0 + 16, 198 + i * 24, b, 11.5, INK, "start"))

    # стрілки від центру вниз
    f.append(arrow(W / 2 - 60, 116, lx + lw / 2, 150, color=FIELD, sw=2.0))
    f.append(arrow(W / 2 + 60, 116, rx0 + lw / 2, 150, color=POS, sw=2.0))

    # знизу — вісім хибних припущень розподілених систем
    by = 322
    f.append(text(W / 2, by, "Вісім хибних припущень, які ця ілюзія непомітно нав'язує",
                  13, INK, "middle", bold=True))
    fall = ["мережа надійна", "затримка нульова", "смуга безмежна", "мережа безпечна",
            "топологія стала", "адміністратор один", "передача безплатна", "мережа однорідна"]
    cols = 4
    cw = (W - 80) / cols
    for i, fl in enumerate(fall):
        r, c = divmod(i, cols)
        x = 40 + c * cw + cw / 2
        y = by + 22 + r * 40
        f.append(rect(40 + c * cw + 6, y - 16, cw - 12, 30, fill="#fff7ed", stroke=POS, sw=1.3, rx=5))
        f.append(text(x, y + 4, str(i + 1) + ". " + fl, 11, POS, "middle", bold=True))

    f.append(text(W / 2, H - 12,
                  "Кожне «припущення» — те, що локальний виклик дає задарма, а мережевий — НІ. RPC ховає саме цей розрив.",
                  11.0, INK, "middle", italic=True))
    render(os.path.join(IMG, "rpc-two-faces.svg"), W, H, *f)


# ── 6. Фрагментація купи: динамічне виділення vs сталі буфери ─────────────────
# Ідея (для proj-rpc-dispatch): malloc/free під кадри лишають дірки → купа
# фрагментується → великий запит вертає NULL саме після довгої роботи. Сталі
# буфери лежать раз і назавжди, вільне суцільне. Тому весь код RPC — без malloc.
def fig_fragmentation():
    W, H = 880, 410
    f = []
    f.append(text(W / 2, 30, "Чому вбудований RPC не виділяє памʼять динамічно",
                  16.0, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "malloc/free під кадри фрагментують купу; сталі буфери — ні",
                  11.0, MUTED, "middle", italic=True))

    bar_w, bar_h = 360, 46
    xL, xR = 60, 460
    ytop = 120

    f.append(text(xL + bar_w / 2, ytop - 40, "динамічне виділення (malloc/free)",
                  12.5, POS, "middle", bold=True))
    f.append(text(xR + bar_w / 2, ytop - 40, "сталі буфери фіксованого розміру",
                  12.5, FIELD, "middle", bold=True))

    def heap_frame(x):
        return rect(x, ytop, bar_w, bar_h, fill="#ffffff", stroke=LINE, sw=1.6, rx=4)

    # ліва купа: чергування зайнятих блоків і дірок (фрагментація)
    f.append(heap_frame(xL))
    left_segs = [(0.12, True), (0.07, False), (0.10, True), (0.06, False),
                 (0.14, True), (0.08, False), (0.11, True), (0.05, False),
                 (0.13, True), (0.14, False)]
    cx = xL
    for frac, used in left_segs:
        w = bar_w * frac
        if used:
            f.append(rect(cx, ytop, w, bar_h, fill="#fdecea", stroke=POS, sw=1.2, rx=2))
        cx += w
    f.append(text(xL + bar_w / 2, ytop + bar_h + 22,
                  "дрібні дірки між блоками: вільного багато, суцільного — нема",
                  10.5, INK, "middle", italic=True))
    f.append(rect(xL, ytop + bar_h + 40, bar_w, 30, fill="#fff4f0", stroke=POS, sw=1.8, rx=4))
    f.append(text(xL + bar_w / 2, ytop + bar_h + 60,
                  "malloc(кадр) → NULL  (після днів роботи)", 11.0, POS, "middle", bold=True))

    # права купа: статичні буфери раз і назавжди, далі суцільне вільне
    f.append(heap_frame(xR))
    right_segs = [(0.18, True), (0.18, True), (0.16, True), (0.48, False)]
    cx = xR
    for frac, used in right_segs:
        w = bar_w * frac
        if used:
            f.append(rect(cx, ytop, w, bar_h, fill="#e9f7ef", stroke=FIELD, sw=1.4, rx=2))
            f.append(text(cx + w / 2, ytop + bar_h / 2 + 4, "буфер", 9.5, FIELD, "middle", bold=True))
        cx += w
    f.append(text(xR + bar_w / 2, ytop + bar_h + 22,
                  "виділено на старті, не рухаються — вільне суцільне",
                  10.5, INK, "middle", italic=True))
    f.append(rect(xR, ytop + bar_h + 40, bar_w, 30, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(xR + bar_w / 2, ytop + bar_h + 60,
                  "кадр завжди має куди лягти", 11.0, FIELD, "middle", bold=True))

    f.append(text(W / 2, H - 16,
                  "Та сама причина, чому весь код RPC тримає буфери статичними: на МК без віртуальної памʼяті дірки не зникають.",
                  11.0, INK, "middle", italic=True))
    render(os.path.join(IMG, "rpc-fragmentation.svg"), W, H, *f)


# ── 7. Повний шлях виклику крізь усі шари (клієнт → дріт → сервер) ─────────────
# Ідея (для proj-rpc-dispatch): як шість шарів змикаються в один обмін і який
# шар яку біду закриває. CRC — спотворення, межа — побитий номер, кеш — повтор,
# таймаут — мовчання. Це підсумкова мапа всього коду вставки.
def fig_stack():
    W, H = 900, 540
    f = []
    f.append(text(W / 2, 30, "Повний шлях виклику крізь усі шари RPC",
                  16.0, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "кожен шар закриває свою біду: CRC — спотворення, межа — побитий номер, кеш — повтор, таймаут — мовчання",
                  10.5, MUTED, "middle", italic=True))

    colw = 300
    xL, xR = 60, 540
    f.append(text(xL + colw / 2, 84, "КЛІЄНТ", 13, NEG, "middle", bold=True))
    f.append(text(xR + colw / 2, 84, "СЕРВЕР", 13, FIELD, "middle", bold=True))

    bh, gap = 44, 16
    y0 = 100

    def box(x, yy, label, col, fill, note):
        out = [rect(x, yy, colw, bh, fill=fill, stroke=col, sw=1.7, rx=5)]
        out.append(text(x + colw / 2, yy + 18, label, 11.0, INK, "middle", bold=True))
        out.append(text(x + colw / 2, yy + 33, note, 9.5, col, "middle", italic=True))
        return out

    steps_L = [
        ("прикладний код: val = read_sensor(3)", NEG, "#eaf0fd", "звичайний виклик"),
        ("заглушка: маршалінг у packed-структуру", NEG, "#f4f6f8", "присвоєння полів"),
        ("CRC-16 над {id, func, arg}", NEG, "#f4f6f8", "доказ цілості"),
        ("неблокувальний автомат: кадр + таймер", NEG, "#eaf0fd", "не морозить систему"),
    ]
    for i, (lbl, col, fl, note) in enumerate(steps_L):
        yy = y0 + i * (bh + gap)
        f += box(xL, yy, lbl, col, fl, note)
        if i < len(steps_L) - 1:
            f.append(arrow(xL + colw / 2, yy + bh, xL + colw / 2, yy + bh + gap, color=NEG, sw=1.8))

    steps_R = [
        ("приймач-автомат: збирає кадр із потоку", FIELD, "#e9f7ef", "байт за байтом"),
        ("звірка CRC", FIELD, "#f4f6f8", "битий → мовчки геть"),
        ("кеш за ID", POS, "#fff4f0", "повтор → стара відповідь"),
        ("диспетчер: межа таблиці → обробник", FIELD, "#e9f7ef", "func ≥ N → помилка"),
    ]
    for i, (lbl, col, fl, note) in enumerate(steps_R):
        yy = y0 + i * (bh + gap)
        f += box(xR, yy, lbl, col, fl, note)
        if i < len(steps_R) - 1:
            f.append(arrow(xR + colw / 2, yy + bh, xR + colw / 2, yy + bh + gap, color=FIELD, sw=1.8))

    # дріт UART: запит уперед (від верхнього блоку клієнта до верхнього сервера)
    f.append(arrow(xL + colw, y0 + bh / 2, xR, y0 + bh / 2, color=POS, sw=2.2))
    f.append(text((xL + colw + xR) / 2, y0 + bh / 2 - 8, "кадр запиту", 10.5, POS, "middle", bold=True))

    # відповідь назад (від нижнього блоку сервера до нижнього клієнта)
    yb = y0 + 3 * (bh + gap)
    f.append(arrow(xR, yb + bh / 2, xL + colw, yb + bh / 2, color=FIELD, sw=2.2))
    f.append(text((xL + colw + xR) / 2, yb + bh / 2 + 16, "кадр відповіді (той самий ID)",
                  10.5, FIELD, "middle", bold=True))

    f.append(text(W / 2, H - 16,
                  "Шість шарів — один обмін. Виклик розтягнутий у часі, але система не зупиняється; кожна біда дроту має свій лік.",
                  11.0, INK, "middle", italic=True))
    render(os.path.join(IMG, "rpc-stack.svg"), W, H, *f)


if __name__ == "__main__":
    fig_illusion()
    fig_lifecycle()
    fig_dispatch()
    fig_birth_timeline()
    fig_two_faces()
    fig_fragmentation()
    fig_stack()
    print("OK: figures written to", IMG)
