# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# локальні відтінки під єдину палітру svgkit
AMBER   = "#caa24a"   # бурштин — середній шар / моки
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"


# ── pyramid: піраміда тестів прошивки ────────────────────────────────────────
# Ідея: тести складаються в піраміду — широка дешева основа (хост-тести логіки на
# ПК, секунди), вужча середина (підроблене залізо — моки), вузька вершина (повільні
# тести на справжньому чипі). Що нижче — дешевше, швидше, численніше.

def fig_pyramid():
    W, H = 820, 392
    p = []
    cx = W / 2
    apex_y, base_y = 78, 332
    half = 250          # піврозмаху основи
    # три яруси за висотою (зверху вузько → донизу широко)
    y1, y2 = 162, 246   # межі ярусів
    def xs_at(y):       # піврозмах трикутника на висоті y
        return half * (y - apex_y) / (base_y - apex_y)
    # вершина — залізо
    p.append("<polygon points=\"%.1f,%.1f %.1f,%.1f %.1f,%.1f\" fill=\"%s\" stroke=\"%s\" stroke-width=\"2\"/>" % (
        cx, apex_y, cx - xs_at(y1), y1, cx + xs_at(y1), y1, BLUEBG, NEG))
    # середина — моки
    p.append("<polygon points=\"%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f\" fill=\"%s\" stroke=\"%s\" stroke-width=\"2\"/>" % (
        cx - xs_at(y1), y1, cx + xs_at(y1), y1, cx + xs_at(y2), y2, cx - xs_at(y2), y2, AMBERBG, AMBER))
    # основа — хост
    p.append("<polygon points=\"%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f\" fill=\"%s\" stroke=\"%s\" stroke-width=\"2\"/>" % (
        cx - xs_at(y2), y2, cx + xs_at(y2), y2, cx + half, base_y, cx - half, base_y, GREENBG, FIELD))

    p.append(text(cx, 132, "тест на залізі", size=12, color=NEG, bold=True))
    p.append(text(cx, 150, "мало · повільно · найреальніше", size=9, color=INK))
    p.append(text(cx, 206, "симуляція периферії (моки)", size=12.5, color=AMBERTX, bold=True))
    p.append(text(cx, 224, "підроблене залізо · середньо", size=9, color=INK))
    p.append(text(cx, 292, "юніт-тести на хості", size=14, color=FIELD, bold=True))
    p.append(text(cx, 312, "багато · швидко (секунди) · на ПК", size=9.5, color=INK))

    p.append(text(cx, H - 16, "масу перевірок роби внизу — нагору винось лише те, що інакше не перевірити",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "pyramid.svg"), W, H, *p,
           title="Піраміда тестів: багато швидких, мало повільних")


# ── separation: відділити логіку від заліза ──────────────────────────────────
# Ідея: головний прийом — провести межу між чистою логікою (автомати, обчислення,
# рішення) і доступом до заліза. Над межею код тестується на ПК; на самій межі —
# шов (HAL), де залізо підмінюють моком.

def fig_separation():
    W, H = 820, 360
    p = []
    bx, bw = 70, W - 140

    p.append(rect(bx, 70, bw, 104, fill=GREENBG, stroke=FIELD, sw=2, rx=12))
    p.append(text(W / 2, 98, "ЛОГІКА — без заліза", size=13.5, color=FIELD, bold=True))
    p.append(text(W / 2, 122, "скінченні автомати · обчислення · розбір даних · рішення", size=10.5, color=INK))
    p.append(text(W / 2, 156, "✓ компілюється й тестується прямо на ПК", size=11, color=FIELD, bold=True))

    # шов / HAL
    sw_w = 380
    p.append(rect(W / 2 - sw_w / 2, 196, sw_w, 40, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=8))
    p.append(text(W / 2, 221, "інтерфейс / HAL — шов між світами", size=11, color=AMBERTX, bold=True))
    p.append(mtext(W / 2 + sw_w / 2 + 10, 214, "← тут підмінюють\n   залізо на мок",
                   size=9.5, color=AMBER, anchor="start", lh=1.4))

    p.append(rect(bx, 258, bw, 92, fill=BLUEBG, stroke=NEG, sw=2, rx=12))
    p.append(text(W / 2, 286, "ДОСТУП ДО ЗАЛІЗА", size=13.5, color=NEG, bold=True))
    p.append(text(W / 2, 310, "GPIO · регістри · драйвери давачів · шини", size=10.5, color=INK))
    p.append(text(W / 2, 334, "потрібен чіп — або його підробка (мок)", size=11, color=NEG, bold=True))

    p.append(arrow(bx + 60, 196, bx + 60, 258, color=INK, sw=2))
    p.append(arrow(bx + bw - 60, 258, bx + bw - 60, 196, color=INK, sw=2))
    render(os.path.join(OUT, "separation.svg"), W, H, *p,
           title="Головний прийом: відділити логіку від заліза")


# ── host-loop: дві петлі зворотного зв'язку ──────────────────────────────────
# Ідея: «залити й молитися» — довгий цикл на хвилини (правка→компіляція→Flash→
# чіп→лог→здогад); хост-тест замикає те саме коло за секунди й автоматично. Швидкий
# зворотний зв'язок ловить помилку в мить, коли її зробили.

def fig_host_loop():
    W, H = 820, 380
    p = []
    colw = 360
    lx, rx = 30, W - 30 - colw
    top, ch = 76, 270

    # ліворуч — залити й молитися
    p.append(rect(lx, top, colw, ch, fill="#fffafa", stroke=POS, sw=2, rx=12))
    p.append(text(lx + colw / 2, top + 28, "«Залити й молитися»", size=13, color=POS, bold=True))
    left = ["правка коду", "компіляція", "заливання у Flash",
            "запуск на чипі", "вдивляння в лог", "здогад, що не так"]
    for i, t in enumerate(left):
        cyl = top + 58 + i * 32
        p.append(circle(lx + 30, cyl - 4, 9, fill=REDBG, stroke=POS, sw=1.4))
        p.append(text(lx + 30, cyl, str(i + 1), size=9, color=POS, bold=True))
        p.append(text(lx + 48, cyl, t, size=10.5, color=INK, anchor="start"))
    p.append(text(lx + colw / 2, top + ch - 14, "цикл — хвилини", size=11, color=POS, bold=True))

    # праворуч — хост-тест
    p.append(rect(rx, top, colw, ch, fill="#fbfdfb", stroke=FIELD, sw=2, rx=12))
    p.append(text(rx + colw / 2, top + 28, "юніт-тест на хості", size=13, color=FIELD, bold=True))
    right = ["правка логіки", "компіляція під ПК", "запуск тестів", "зелено / червоно одразу"]
    for i, t in enumerate(right):
        cyr = top + 64 + i * 40
        p.append(circle(rx + 30, cyr - 4, 9, fill=GREENBG, stroke=FIELD, sw=1.4))
        p.append(text(rx + 30, cyr, str(i + 1), size=9, color=FIELD, bold=True))
        p.append(text(rx + 48, cyr, t, size=11, color=INK, anchor="start"))
    p.append(text(rx + colw / 2, top + ch - 14, "цикл — секунди, ще й автоматично", size=10.5, color=FIELD, bold=True))

    p.append(text(W / 2, H - 12, "швидкий зворотний зв'язок ловить помилку в мить, коли її зробили",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "host-loop.svg"), W, H, *p,
           title="Дві петлі зворотного зв'язку: хвилини проти секунд")


# ── mock: мок підміняє давач сценарними відповідями ──────────────────────────
# Ідея: код під тестом звертається до інтерфейсу; у реальному пристрої за ним
# справжній давач, у тесті — мок зі сценарними відповідями. Код не бачить різниці,
# а дивні випадки наказують мокові, не чекаючи їх у полі.

def fig_mock():
    W, H = 820, 360
    p = []
    # код під тестом
    p.append(rect(60, 150, 230, 96, fill=GREENBG, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(175, 178, "код під тестом", size=12.5, color=FIELD, bold=True))
    p.append(text(175, 198, "драйвер / логіка", size=9.6, color=MUTED))
    p.append(text(175, 214, "питає «дай вимір»", size=9.6, color=MUTED))
    p.append(text(175, 268, "він не бачить різниці →", size=9.5, color=MUTED, italic=True))

    p.append(arrow(292, 180, 398, 142, color=INK, sw=2))
    p.append(arrow(292, 216, 398, 280, color=INK, sw=2))

    # справжній давач
    p.append(text(515, 96, "у реальному пристрої", size=9, color=MUTED))
    p.append(rect(400, 106, 230, 72, fill=BLUEBG, stroke=NEG, sw=1.8, rx=8))
    p.append(text(515, 134, "справжній давач", size=12.5, color=NEG, bold=True))
    p.append(text(515, 154, "потрібен чіп і залізо", size=9.6, color=MUTED))

    # мок
    p.append(rect(400, 250, 380, 92, fill=AMBERBG, stroke=AMBER, sw=2, rx=10))
    p.append(text(590, 278, "МОК давача (у тесті)", size=12, color=AMBERTX, bold=True))
    p.append(text(590, 300, "сценарій: 25 °C → 0 → −999 (помилка) → таймаут", size=9.6, color=INK))
    p.append(text(590, 320, "повертає що скажеш — і ловить реакцію коду на кожен", size=9.3, color=MUTED))

    p.append(text(W / 2, H - 12, "дивні випадки не чекають у полі — їх наказують мокові в тесті",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "mock.svg"), W, H, *p,
           title="Мок підміняє давач сценарними відповідями")


# ── on-hardware: тест на залізі (hardware-in-the-loop) ───────────────────────
# Ідея: тест-раннер роздає завдання справжньому чипу під тестом (DUT), за потреби —
# із зовнішньою оснасткою. Повільно й небагато, зате ловить тайминг, brownout,
# електрику й реальні примхи периферії, яких мок не вигадає.

def fig_on_hardware():
    W, H = 820, 360
    p = []
    bw, bh, by = 200, 96, 130
    # три бокси в ряд
    p.append(rect(40, by, bw, bh, fill=GREENBG, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(140, by + 26, "тест-раннер", size=12.5, color=FIELD, bold=True))
    p.append(text(140, by + 46, "на ПК або в чипі", size=9.6, color=MUTED))
    p.append(text(140, by + 62, "дає завдання, читає звіт", size=9.6, color=MUTED))

    p.append(rect(310, by, bw, bh, fill=BLUEBG, stroke=NEG, sw=1.8, rx=8))
    p.append(text(410, by + 26, "чіп під тестом", size=12.5, color=NEG, bold=True))
    p.append(text(410, by + 46, "реальне залізо (DUT)", size=9.6, color=MUTED))
    p.append(text(410, by + 62, "тестова прошивка", size=9.6, color=MUTED))

    p.append(rect(580, by, bw, bh, fill=BG, stroke=MUTED, sw=1.8, rx=8))
    p.append(text(680, by + 26, "зовнішня оснастка", size=12.5, color=INK, bold=True))
    p.append(text(680, by + 46, "генератор, вимірювач", size=9.6, color=MUTED))
    p.append(text(680, by + 62, "за потреби", size=9.6, color=MUTED))

    p.append(arrow(240, by + bh / 2, 310, by + bh / 2, color=INK, sw=2.2))
    p.append(arrow(510, by + bh / 2, 580, by + bh / 2, color=INK, sw=2.2))

    # що ловить
    p.append(rect(90, 268, 640, 74, fill=REDBG, stroke=POS, sw=1.6, rx=10))
    p.append(text(410, 292, "ловить саме «залізні» біди:", size=11, color=POS, bold=True))
    p.append(text(410, 314, "тайминг і гонки між перериваннями · просідання живлення (brownout) ·", size=10, color=INK))
    p.append(text(410, 332, "реальні примхи периферії · електричні ефекти", size=10, color=INK))
    render(os.path.join(OUT, "on-hardware.svg"), W, H, *p,
           title="Тест на залізі (hardware-in-the-loop)")


# ── what-catches: який шар яку біду ловить ───────────────────────────────────
# Ідея: кожен шар бачить свій клас багів і сліпий до чужого — логіку ловить хост,
# драйвер/протокол ловлять моки, тайминг/електрику показує лише залізо. Тому
# потрібні всі три.

def fig_what_catches():
    W, H = 820, 360
    p = []
    rows = [
        ("логіка", "автомат, обчислення, розбір даних", "хост-тести", FIELD, GREENBG),
        ("драйвер / протокол", "хибна послідовність, погана реакція на помилку", "моки", AMBER, AMBERBG),
        ("тайминг / електрика", "гонки, brownout, реальні примхи", "залізо", NEG, BLUEBG),
    ]
    top, rh, gap = 84, 66, 16
    lx, rw = 40, 740
    p.append(text(lx + 8, top - 14, "клас бага", size=11, color=INK, anchor="start", bold=True))
    p.append(text(lx + rw - 90, top - 14, "де ловиться", size=11, color=INK, bold=True))
    for i, (name, note, where, col, fill) in enumerate(rows):
        y = top + i * (rh + gap)
        p.append(rect(lx, y, rw, rh, fill=fill, stroke=col, sw=1.7, rx=10))
        p.append(text(lx + 22, y + 28, name, size=12.5, color=col, anchor="start", bold=True))
        p.append(text(lx + 22, y + 48, note, size=10, color=INK, anchor="start"))
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(lx + rw - 180, y + 16, 160, 34, fill=BG, stroke=col, sw=1.6, rx=8))
        p.append(text(lx + rw - 100, y + 38, where, size=11.5, color=tagcol, bold=True))

    p.append(text(W / 2, H - 14, "один шар сліпий до двох третин бід — тому потрібні всі три",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "what-catches.svg"), W, H, *p,
           title="Який шар яку біду ловить")


# ════════════════════════════════════════════════════════════════════════════
# Фігура вставки proj-emulators.md
# ════════════════════════════════════════════════════════════════════════════


# ── emulator-stack: стек емулятора і місце на піраміді ───────────────────────
# Ідея: емулятор складає три яруси (ядро → пам'ять → периферія) і виконує той самий
# .elf, що поїде в чип, перехоплюючи записи в регістри. На осі точність↔швидкість
# він лягає між моками і живим залізом — пропущена сходинка піраміди.

def fig_emulator_stack():
    W, H = 820, 420
    p = []
    # ліва половина — стек
    p.append(text(215, 30, "стек емулятора", size=15, color=INK, bold=True))
    layers = [
        (138, 70, "модель периферії",
         "перехоплює записи в регістри:\nUART / ADC / GPIO"),
        (232, 56, "карта пам'яті",
         "масив = Flash / RAM за адресами"),
        (318, 56, "ядро CPU",
         "виконує машинні інструкції .elf"),
    ]
    for y, h, name, note in layers:
        p.append(rect(80, y, 270, h, fill=BLUEBG, stroke=NEG, sw=2, rx=8))
        lines = note.split("\n")
        p.append(text(215, y + 24, name, size=12.5, color=NEG, bold=True))
        for j, ln in enumerate(lines):
            p.append(text(215, y + 42 + j * 15, ln, size=9.3, color=INK))
    # вхід .elf зверху
    p.append(rect(118, 40, 194, 24, fill=REDBG, stroke=POS, sw=1.8, rx=6))
    p.append(text(215, 56, "той самий .elf, що й у чіп", size=10.5, color=POS, bold=True))
    p.append(arrow(215, 64, 215, 70, color=POS, sw=2.2))
    p.append(arrow(215, 138 + 70 + 2, 215, 232 - 2, color=NEG, sw=2))   # периферія→память
    p.append(arrow(215, 232 + 56 + 2, 215, 318 - 2, color=NEG, sw=2))   # память→ядро
    p.append(text(215, H - 14, "прошивка виконується на підроблених регістрах — рівень нижче за мок-функцію",
                  size=9.6, color=MUTED, italic=True))

    # роздільник
    p.append(line(420, 20, 420, 396, color="#cccccc", sw=1.2, dash="4 4"))

    # права половина — місце на осі тестів (стовпчики висхідної точності)
    p.append(text(622, 30, "місце на осі тестів", size=15, color=INK, bold=True))
    cols = [
        (440, 80, "хост-тести", "x86,\nне .elf", FIELD, GREENBG, 1.8),
        (535, 110, "моки", "хост +\nфункції", AMBER, AMBERBG, 1.8),
        (630, 140, "емулятор", "той .elf,\nфейк-чіп", POS, AMBERBG, 2.6),
        (725, 170, "залізо", "реальний\nчіп", NEG, BLUEBG, 1.8),
    ]
    base = 372
    for x, hh, name, note, col, fill, sw_ in cols:
        y = base - hh
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, y, 82, hh, fill=fill, stroke=col, sw=sw_, rx=6))
        p.append(text(x + 41, y + 22, name, size=10, color=tagcol, bold=True))
        for j, ln in enumerate(note.split("\n")):
            p.append(text(x + 41, y + 40 + j * 12, ln, size=9, color=INK))
    # вісь
    p.append(line(806, base + 8, 438, base + 8, color=MUTED, sw=1.5))
    p.append(line(438, base + 8, 806, base + 8, color=MUTED, sw=1.5, dash=None))
    p.append("<line x1=\"806\" y1=\"%d\" x2=\"438\" y2=\"%d\" stroke=\"%s\" stroke-width=\"1.5\" marker-end=\"url(#arrow)\"/>" % (base + 8, base + 8, MUTED))
    p.append("<line x1=\"438\" y1=\"%d\" x2=\"806\" y2=\"%d\" stroke=\"%s\" stroke-width=\"1.5\" marker-end=\"url(#arrow)\"/>" % (base + 8, base + 8, MUTED))
    p.append(text(440, base + 24, "швидше / масштабованіше →", size=9, color=MUTED, anchor="start"))
    p.append(text(806, base + 24, "← точніше / ближче до заліза", size=9, color=MUTED, anchor="end"))
    p.append(mtext(630 + 41, 372 - 140 - 14, "↕ пропущена\nсходинка", size=9, color=POS, bold=True, lh=1.2))
    render(os.path.join(OUT, "emulator-stack.svg"), W, H, *p,
           title="")


# ════════════════════════════════════════════════════════════════════════════
# Фігури детальної версії firmware-testing-d.md
# ════════════════════════════════════════════════════════════════════════════


# ── doubles: таксономія тест-дублів ──────────────────────────────────────────
# Ідея: «підробка» — не одне, а п'ять різних речей за тим, ЩО вони роблять.
# Dummy лише заповнює параметр; stub віддає готову відповідь; fake — спрощена
# робоча реалізація; spy записує виклики й дає звіт; mock несе очікування й сам
# виносить вердикт. Шкала «пасивний → активний».

def fig_doubles():
    W, H = 820, 470
    p = []
    rows = [
        ("dummy", "пустушка",
         "лише заповнює параметр; його не викликають",
         "пасивний", MUTED, FILL),
        ("stub", "заглушка",
         "віддає готову відповідь: «температура = 25»",
         "віддає вхід", NEG, BLUEBG),
        ("fake", "фейк",
         "спрощена РОБОЧА реалізація: масив у RAM замість Flash",
         "працює спрощено", FIELD, GREENBG),
        ("spy", "шпигун",
         "робить як стаб + ЗАПИСУЄ, як його кликали (для звіту)",
         "записує виклики", AMBER, AMBERBG),
        ("mock", "мок",
         "несе ОЧІКУВАННЯ наперед і сам валить тест, якщо їх порушено",
         "виносить вердикт", POS, REDBG),
    ]
    top, rh, gap = 92, 60, 12
    lx, rw = 40, 740
    p.append(text(W / 2, 40, "п'ять тест-дублів — за тим, ЩО вони роблять", size=15, color=INK, bold=True))
    p.append(text(lx + 70, top - 16, "пасивний", size=10, color=MUTED, bold=True))
    p.append(text(lx + rw - 70, top - 16, "активний →", size=10, color=POS, bold=True))
    for i, (en, ua, note, role, col, fill) in enumerate(rows):
        y = top + i * (rh + gap)
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(lx, y, rw, rh, fill=fill, stroke=col, sw=1.7, rx=10))
        p.append(text(lx + 20, y + 26, en, size=13, color=tagcol, anchor="start", bold=True))
        p.append(text(lx + 20, y + 45, ua, size=9.5, color=MUTED, anchor="start"))
        p.append(text(lx + 150, y + 26, note, size=10.5, color=INK, anchor="start"))
        p.append(rect(lx + rw - 168, y + 14, 150, 32, fill=BG, stroke=col, sw=1.4, rx=8))
        p.append(text(lx + rw - 93, y + 35, role, size=10, color=tagcol, bold=True))
    p.append(text(W / 2, H - 12,
                  "стаб відповідає на питання коду; мок ставить питання коду — і сам судить відповідь",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "doubles.svg"), W, H, *p,
           title="")


# ── seams: три шви для підміни заліза в C ─────────────────────────────────────
# Ідея: відірвати логіку від драйвера в C можна трьома швами. Вказівники на
# функції — шов у РАНТАЙМІ (структура-інтерфейс, мок підставляється під час
# виконання). Підміна на лінкуванні — шов у ЗБІРЦІ (той самий .h, два .c: бойовий
# і тестовий). Препроцесор (#ifdef) — шов у ВИХІДНИКУ, найгірший: тест ганяє
# ІНШИЙ код, ніж їде в чіп.

def fig_seams():
    W, H = 820, 430
    p = []
    p.append(text(W / 2, 38, "три шви, щоб підмінити залізо в C", size=15, color=INK, bold=True))
    cols = [
        (40, "вказівники на функції", "шов у РАНТАЙМІ", FIELD, GREENBG,
         ["структура з полями-функціями",
          "(vtable вручну): код кличе",
          "drv->read(); у тесті в поле",
          "кладуть мок під час виконання"],
         "✓ той самий бінар; гнучко",
         "− трохи зайвого коду й непрямий виклик"),
        (290, "підміна на лінкуванні", "шов у ЗБІРЦІ", NEG, BLUEBG,
         ["один .h, два .c: hw.c для",
          "заліза, fake.c для тесту;",
          "лінкер бере потрібний.",
          "Так і робить Ceedling"],
         "✓ нуль зайвого в бойовому коді",
         "− підміна цілим файлом, не точково"),
        (540, "препроцесор (#ifdef)", "шов у ВИХІДНИКУ", POS, REDBG,
         ["#ifdef TEST → один код,",
          "#else → інший. Гілки",
          "обирає компілятор ще до",
          "складання бінаря"],
         "✗ тест ганяє ІНШИЙ код,",
         "ніж їде в чіп — найгірший шов"),
    ]
    cw = 240
    for x, name, seam, col, fill, body, plusln, minusln in cols:
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, 60, cw, 300, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(x + cw / 2, 86, name, size=12, color=tagcol, bold=True))
        p.append(rect(x + 30, 98, cw - 60, 24, fill=BG, stroke=col, sw=1.2, rx=6))
        p.append(text(x + cw / 2, 115, seam, size=10.5, color=tagcol, bold=True))
        for j, ln in enumerate(body):
            p.append(text(x + 18, 150 + j * 19, ln, size=9.6, color=INK, anchor="start"))
        p.append(line(x + 16, 250, x + cw - 16, 250, color=col, sw=1))
        p.append(text(x + 18, 290, plusln, size=9.6, color=tagcol, anchor="start", bold=True))
        p.append(text(x + 18, 332, minusln, size=9.6, color=INK, anchor="start"))
    p.append(text(W / 2, H - 12,
                  "що пізніше обирається підміна (рантайм → збірка → вихідник), то ближче тест до бойового коду",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "seams.svg"), W, H, *p,
           title="")


# ── time-injection: інжекція джерела часу робить таймаут детермінованим ───────
# Ідея: код, що дивиться на справжній годинник (now()), у тесті треба ЧЕКАТИ
# реальну секунду й результат хисткий. Винесемо джерело часу за шов: у бою —
# справжній лічильник, у тесті — змінна, якій тест САМ підкручує час. Тоді
# «минуло 5 с» настає миттєво й однаково щоразу.

def fig_time_injection():
    W, H = 820, 400
    p = []
    p.append(text(W / 2, 38, "інжекція часу: таймаут без реального чекання", size=15, color=INK, bold=True))

    # ліворуч — час зашитий усередині (погано)
    lx, cw = 40, 350
    p.append(rect(lx, 64, cw, 280, fill=REDBG, stroke=POS, sw=2, rx=12))
    p.append(text(lx + cw / 2, 90, "час зашитий усередині", size=12.5, color=POS, bold=True))
    p.append(rect(lx + 40, 110, cw - 80, 56, fill=BG, stroke=POS, sw=1.4, rx=8))
    p.append(text(lx + cw / 2, 132, "if (millis() - t0 > 5000)", size=10.5, color=INK))
    p.append(text(lx + cw / 2, 152, "код сам читає залізний годинник", size=9.6, color=MUTED))
    p.append(arrow(lx + cw / 2, 168, lx + cw / 2, 196, color=POS, sw=2))
    p.append(rect(lx + 30, 200, cw - 60, 84, fill="#fff", stroke=POS, sw=1.4, rx=8))
    p.append(text(lx + cw / 2, 224, "у тесті: щоб настав таймаут,", size=10, color=INK))
    p.append(text(lx + cw / 2, 242, "треба ЧЕКАТИ справжні 5 секунд", size=10, color=POS, bold=True))
    p.append(text(lx + cw / 2, 264, "повільно · хистко · недетерміновано", size=9.4, color=MUTED, italic=True))
    p.append(text(lx + cw / 2, 322, "✗ годинник — невидима залежність", size=10.5, color=POS, bold=True))

    # праворуч — час інжектований (добре)
    rx = W - 40 - cw
    p.append(rect(rx, 64, cw, 280, fill=GREENBG, stroke=FIELD, sw=2, rx=12))
    p.append(text(rx + cw / 2, 90, "джерело часу за швом", size=12.5, color=FIELD, bold=True))
    p.append(rect(rx + 40, 110, cw - 80, 56, fill=BG, stroke=FIELD, sw=1.4, rx=8))
    p.append(text(rx + cw / 2, 132, "if (now() - t0 > 5000)", size=10.5, color=INK))
    p.append(text(rx + cw / 2, 152, "now() подають ззовні", size=9.6, color=MUTED))
    p.append(arrow(rx + cw / 2, 168, rx + cw / 2, 196, color=FIELD, sw=2))
    p.append(rect(rx + 30, 200, cw - 60, 84, fill="#fff", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(rx + cw / 2, 224, "у тесті: now = 0; крок; now = 6000;", size=9.8, color=INK))
    p.append(text(rx + cw / 2, 242, "«минуло 6 с» настає МИТТЄВО", size=10, color=FIELD, bold=True))
    p.append(text(rx + cw / 2, 264, "швидко · стабільно · повторювано", size=9.4, color=MUTED, italic=True))
    p.append(text(rx + cw / 2, 322, "✓ час керований — ловить межі точно", size=10.5, color=FIELD, bold=True))

    p.append(text(W / 2, H - 10,
                  "винеси годинник за шов — і час у тесті стає кермом, а не секундоміром",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "time-injection.svg"), W, H, *p,
           title="")


if __name__ == "__main__":
    fig_pyramid()
    fig_separation()
    fig_host_loop()
    fig_mock()
    fig_on_hardware()
    fig_what_catches()
    fig_emulator_stack()
    fig_doubles()
    fig_seams()
    fig_time_injection()
    print("OK: figures written to", OUT)
