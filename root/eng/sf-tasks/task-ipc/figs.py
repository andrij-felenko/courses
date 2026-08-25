# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── problem: дві потреби задач — передати дані й поділити ресурс ───────────────
# Ідея: показати, що «гола» спільна змінна між задачами небезпечна обома боками:
# і коли через неї передають дані (A→B), і коли через неї ділять один ресурс.

def fig_problem():
    W, H = 700, 330
    p = []
    # дві задачі зверху
    a, _, _ = textbox(165, 70, "Задача A", size=13, bold=True, fill="#eef4ff", stroke=NEG, sw=1.8)
    b, _, _ = textbox(535, 70, "Задача B", size=13, bold=True, fill="#eef4ff", stroke=NEG, sw=1.8)
    p += [a, b]

    # ліворуч: передавання даних через голу змінну
    var, vw, vh = textbox(165, 200, "глобальна\nзмінна", size=12, bold=True,
                          fill="#fdecea", stroke=POS, sw=1.8)
    p.append(line(165, 92, 165, 200 - vh / 2, color=INK, sw=1.6))
    p.append(arrow(165, 200 - vh / 2 - 36, 165, 200 - vh / 2 - 2, color=POS, sw=1.8))
    p.append(text(165, 150, "пише", size=10, color=POS, anchor="start"))
    p.append(var)
    p.append(arrow(195, 205, 480, 130, color=POS, sw=1.8))
    p.append(text(330, 150, "читає напівоновлене", size=10, color=POS))
    p.append(text(165, 252, "передати дані", size=11, color=MUTED, italic=True))

    # праворуч: спільний ресурс, до якого тягнуться обидві
    res, rw, rh = textbox(535, 210, "спільна\nшина / ресурс", size=12, bold=True,
                          fill="#fdf6e3", stroke=POS, sw=1.8)
    p.append(arrow(500, 92, 520, 210 - rh / 2 - 2, color=POS, sw=1.8))
    p.append(arrow(165 + 70, 92, 535 - rw / 2 - 2, 210 - rh / 2 + 6, color=POS, sw=1.8))
    p.append(res)
    p.append(text(535, 262, "поділити ресурс", size=11, color=MUTED, italic=True))

    # підсумок-плашка: одночасний доступ = гонка
    warn = fitbox(W / 2 - 175, 296, 350, 26,
                  "одночасний доступ через «голе» спільне → гонка даних",
                  size=11, fill="#fdecea", stroke=POS, sw=1.6, bold=True, color=POS)
    p.append(warn)

    render(os.path.join(OUT, "problem.svg"), W, H, *p,
           title="Дві потреби задач: передати дані й поділити ресурс")


# ── queue: безпечна FIFO-труба, виробник→споживач, дані копіюються ─────────────
# Ідея: черга — труба з комірками; виробник кладе з одного кінця, споживач бере
# з іншого; обидва блокуються на крайніх станах (порожньо / повно).

def fig_queue():
    W, H = 720, 280
    p = []
    # виробник і споживач
    prod, pw, ph = textbox(95, 130, "виробник", size=13, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8)
    cons, cw, ch = textbox(625, 130, "споживач", size=13, bold=True, fill="#eef4ff", stroke=NEG, sw=1.8)

    # труба з комірок
    cells = 5
    cwid = 56
    gap = 6
    total = cells * cwid + (cells - 1) * gap
    x0 = W / 2 - total / 2
    y0 = 108
    fills = ["#dff0df", "#dff0df", "#dff0df", BG, BG]   # три зайняті, дві вільні
    for i in range(cells):
        cx = x0 + i * (cwid + gap)
        p.append(rect(cx, y0, cwid, 44, fill=fills[i], stroke=INK, sw=1.5, rx=4))
    p.append(text(W / 2, y0 - 12, "черга (FIFO)", size=11, color=INK, bold=True))
    p.append(text(x0 + cwid * 1.5, y0 + 70, "перший прийшов — перший пішов", size=10, color=MUTED))

    # стрілки кладе / бере
    p.append(arrow(95 + pw / 2, 130, x0 - 4, 130, color=FIELD, sw=2.0))
    p.append(text(95 + pw / 2 + 36, 118, "xQueueSend", size=10, color=FIELD, anchor="start"))
    p.append(arrow(x0 + total + 4, 130, 625 - cw / 2 - 2, 130, color=NEG, sw=2.0))
    p.append(text(x0 + total + 8, 118, "xQueueReceive", size=10, color=NEG, anchor="start"))
    p += [prod, cons]

    # блокування на краях
    p.append(text(95, 200, "повна → виробник чекає місця", size=10, color=POS))
    p.append(text(625, 200, "порожня → споживач чекає даних", size=10, color=POS, anchor="end"))
    p.append(text(W / 2, 250, "дані копіюються всередину — спільної змінної немає, гонок немає",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "queue.svg"), W, H, *p,
           title="Черга: безпечна труба між задачами")


# ── semaphore: дзвоник події — одна сторона дає, інша чекає ────────────────────
# Ідея: ISR лише «дає» семафор і миттю виходить; задача-обробник, що спала на
# ньому, прокидається і робить важку роботу — відкладене опрацювання.

def fig_semaphore():
    W, H = 720, 270
    p = []
    # ISR — короткий блок ліворуч
    isr, iw, ih = textbox(120, 90, "ISR\n(коротка)", size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.8)
    # семафор — дзвоник у центрі
    sem, sw_, sh = textbox(W / 2, 110, "семафор", size=13, bold=True, fill="#fdf6e3", stroke="#b8860b", sw=2)
    # задача-обробник праворуч
    task, tw, th = textbox(600, 90, "задача-\nобробник", size=12, bold=True, fill="#eef4ff", stroke=NEG, sw=1.8)
    p += [isr, sem, task]

    # дає / чекає
    p.append(arrow(120 + iw / 2, 100, W / 2 - sw_ / 2 - 2, 105, color=POS, sw=2.0))
    p.append(text((120 + iw / 2 + W / 2 - sw_ / 2) / 2, 88, "дає («сталося!»)", size=10, color=POS))
    p.append(arrow(W / 2 + sw_ / 2 + 2, 105, 600 - tw / 2 - 2, 100, color=NEG, sw=2.0))
    p.append(text((W / 2 + sw_ / 2 + 600 - tw / 2) / 2, 88, "будить", size=10, color=NEG))
    p.append(mtext(600, 150, ["спала на ньому →", "прокинулась і працює"], size=10, color=MUTED))

    # внизу: бінарний vs лічильний
    p.append(line(60, 200, W - 60, 200, color="#dddddd", sw=1.2))
    p.append(text(W / 2, 226, "бінарний — є/нема сигналу · лічильний — рахує вільні одиниці ресурсу",
                  size=11, color=INK))
    p.append(text(W / 2, 250, "семафор передає СИГНАЛ, не дані", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "semaphore.svg"), W, H, *p,
           title="Семафор: дзвоник події (виносить роботу з ISR)")


# ── mutex: один за раз до спільного ресурсу ───────────────────────────────────
# Ідея: замок пускає до ресурсу лише одну задачу; друга поступливо чекає, доки
# перша не віддасть — жодних двох одночасно, отже жодної гонки.

def fig_mutex():
    W, H = 700, 280
    p = []
    res, rw, rh = textbox(W / 2, 200, "спільний ресурс\n(шина I2C)", size=12, bold=True,
                          fill="#fdf6e3", stroke="#b8860b", sw=2)
    # замок над ресурсом
    lock, lw, lh = textbox(W / 2, 120, "м'ютекс\n(замок)", size=12, bold=True,
                           fill="#f4f6f8", stroke=INK, sw=2)
    p += [lock, res]
    p.append(line(W / 2, 120 + lh / 2, W / 2, 200 - rh / 2, color=INK, sw=1.6))

    # задача A — тримає
    a, aw, ah = textbox(150, 90, "задача A", size=12, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(a)
    p.append(arrow(150 + aw / 2, 95, W / 2 - lw / 2 - 2, 112, color=FIELD, sw=2.0))
    p.append(text(295, 80, "взяла → працює", size=10, color=FIELD))

    # задача B — чекає
    b, bw, bh = textbox(550, 90, "задача B", size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(b)
    p.append(line(550 - bw / 2, 100, W / 2 + lw / 2 + 2, 116, color=POS, sw=1.8, dash="6 4"))
    p.append(text(420, 80, "поступливо чекає", size=10, color=POS, anchor="start"))

    p.append(text(W / 2, 252, "поки A тримає замок — B не дістанеться: жодних двох одночасно",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "mutex.svg"), W, H, *p,
           title="М'ютекс: один за раз до спільного ресурсу")


# ── mutex-vs-sem: дві відмінності м'ютекса — власник і успадкування пріоритету ─
# Ідея: дві колонки. (1) власник: замок віддає лише та, що взяла. (2) успадкування:
# поки низька тримає замок потрібний високій, її пріоритет тимчасово піднімають.

def fig_mutex_vs_sem():
    W, H = 720, 320
    p = []
    midx = W / 2
    p.append(line(midx, 50, midx, H - 30, color="#dddddd", sw=1.2))

    # ── ліва колонка: власник ──
    p.append(text(midx / 2, 70, "1. Власник", size=13, color=INK, bold=True))
    own, ow, oh = textbox(midx / 2, 130, "м'ютекс:\nвіддає лише та,\nщо ВЗЯЛА", size=11, bold=True,
                          fill="#eafaf0", stroke=FIELD, sw=1.8)
    sem2, s2w, s2h = textbox(midx / 2, 230, "семафор:\nдати може\nБУДЬ-ХТО", size=11, bold=True,
                             fill="#eef4ff", stroke=NEG, sw=1.8)
    p += [own, sem2]

    # ── права колонка: успадкування пріоритету ──
    cx = midx + (W - midx) / 2
    p.append(text(cx, 70, "2. Успадкування пріоритету", size=13, color=INK, bold=True))
    # три смужки пріоритету
    lab = [("низька тримає замок", FIELD, 110),
           ("середня НЕ витісняє", "#b8860b", 170),
           ("висока чекає замок", POS, 230)]
    for t, c, yy in lab:
        p.append(fitbox(cx - 130, yy - 16, 260, 30, t, size=10, fill="#f7f7f7", stroke=c, sw=1.5, color=c, bold=True))
    p.append(arrow(cx, 126, cx, 156, color=INK, sw=1.6))
    p.append(mtext(cx, 280, ["низькій тимчасово піднімають пріоритет —", "рятує від інверсії пріоритетів"], size=10, color=MUTED))

    render(os.path.join(OUT, "mutex-vs-sem.svg"), W, H, *p,
           title="Дві відмінності м'ютекса від семафора")


# ── decision: чотири потреби — чотири засоби ──────────────────────────────────
# Ідея: проста мапа «потреба → засіб», щоб не плутати чергу, два семафори й м'ютекс.

def fig_decision():
    W, H = 720, 300
    p = []
    rows = [
        ("передати ДАНІ між задачами", "черга", FIELD, "#eafaf0"),
        ("сигнал про ПОДІЮ («сталося!»)", "бінарний семафор", NEG, "#eef4ff"),
        ("порахувати вільні ОДИНИЦІ ресурсу", "лічильний семафор", "#b8860b", "#fdf6e3"),
        ("захистити СПІЛЬНИЙ РЕСУРС (один за раз)", "м'ютекс", POS, "#fdecea"),
    ]
    y = 70
    lh = 54
    for need, tool, col, fill in rows:
        p.append(fitbox(50, y, 360, 40, need, size=12, fill="#f7f7f7", stroke=MUTED, sw=1.4, color=INK))
        p.append(arrow(414, y + 20, 470, y + 20, color=col, sw=2.0))
        p.append(fitbox(475, y, 195, 40, tool, size=13, fill=fill, stroke=col, sw=1.8, bold=True, color=col))
        y += lh

    p.append(text(W / 2, H - 18, "дані — черга · подія — семафор · ресурс — м'ютекс",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "decision.svg"), W, H, *p,
           title="Чотири потреби — чотири засоби")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставок (hist-pathfinder, proj-deadlock, proj-priority-inheritance,
#  proj-queue-pattern) — slug-нейминг, той самий стиль.
# ════════════════════════════════════════════════════════════════════════════

# ── information-bus (hist-pathfinder): шина під замком і три задачі ────────────
# Ідея: спільна структура в пам'яті під одним м'ютексом; навколо три задачі
# різних пріоритетів — дизайн виглядає правильним, пастка у взаємодії.

def fig_information_bus():
    W, H = 720, 320
    p = []
    # інформаційна шина під замком — у центрі
    bus, bw, bh = textbox(W / 2, 175, "інформаційна шина\n(спільна пам'ять)", size=12, bold=True,
                          fill="#fdf6e3", stroke="#b8860b", sw=2)
    lock, lw, lh = textbox(W / 2, 110, "м'ютекс", size=11, bold=True, fill="#f4f6f8", stroke=INK, sw=1.8)
    p += [lock, bus]
    p.append(line(W / 2, 110 + lh / 2, W / 2, 175 - bh / 2, color=INK, sw=1.6))

    # три задачі
    hi, hw, hh = textbox(140, 90, "керування шиною\nВИСОКА", size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.8)
    lo, low, loh = textbox(140, 250, "метео\nНИЗЬКА", size=11, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8)
    md, mw, mh = textbox(590, 175, "зв'язок\nСЕРЕДНЯ", size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.8)
    p += [hi, lo, md]

    # висока і низька беруть замок
    p.append(arrow(140 + hw / 2, 95, W / 2 - lw / 2 - 2, 104, color=POS, sw=1.8))
    p.append(arrow(140 + low / 2, 245, W / 2 - bw / 2 - 2, 185, color=FIELD, sw=1.8))
    p.append(text(300, 96, "бере часто, коротко", size=9, color=POS, anchor="start"))
    p.append(text(300, 240, "бере рідко, тримає довго", size=9, color=FIELD, anchor="start"))

    # середня тисне процесор, замка не торкається
    p.append(mtext(590, 230, ["тисне процесор,", "замка НЕ торкається"], size=9, color=NEG))

    p.append(text(W / 2, H - 16, "дизайн виглядає бездоганно — пастка у взаємодії пріоритетів",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "information-bus.svg"), W, H, *p,
           title="Pathfinder: шина під замком і три задачі")


# ── priority-inversion (hist-pathfinder): інверсія по кроках + watchdog ────────
# Ідея: три доріжки часу. Низька з замком віддає процесор середній; висока спить
# на замку → висока чекає на середню; дедлайн зривається, watchdog скидає.

def fig_priority_inversion():
    W, H = 720, 320
    p = []
    lanes = [("ВИСОКА", POS, 80), ("СЕРЕДНЯ", NEG, 150), ("НИЗЬКА", FIELD, 220)]
    x0, x1 = 150, 640
    for name, c, y in lanes:
        p.append(line(x0, y, x1, y, color="#cccccc", sw=1.2))
        p.append(text(x0 - 8, y + 4, name, size=11, color=c, anchor="end", bold=True))

    def bar(lane_y, xa, xb, c, fill):
        return rect(xa, lane_y - 13, xb - xa, 26, fill=fill, stroke=c, sw=1.6, rx=4)

    # низька тримає замок (1) потім витіснена
    p.append(bar(220, 170, 250, FIELD, "#dff0df"))
    p.append(text(180, 200, "взяла замок", size=9, color=FIELD, anchor="start"))
    # висока прокидається, блокується на замку
    p.append(bar(80, 250, 270, POS, "#fdecea"))
    p.append(text(255, 60, "чекає замок (Blocked)", size=9, color=POS, anchor="start"))
    # середня витісняє низьку і довго рахує
    p.append(bar(150, 270, 520, NEG, "#eef4ff"))
    p.append(text(360, 132, "довго рахує (замка не треба)", size=9, color=NEG))
    # низька заморожена з замком
    p.append(rect(250, 220 - 13, 270, 26, fill="#f0f0f0", stroke="#bbbbbb", sw=1.3, rx=4))
    p.append(text(360, 244, "заморожена з замком", size=9, color=MUTED))

    # стрілка залежності: висока → чекає на середню
    p.append(line(360, 93, 360, 137, color=INK, sw=1.4, dash="4 3"))
    p.append(text(368, 116, "висока фактично чекає на середню", size=9, color=INK, anchor="start"))

    # watchdog reset
    p.append(line(520, 60, 520, 250, color=POS, sw=1.6, dash="5 4"))
    p.append(text(520, 278, "дедлайн зірвано →", size=10, color=POS, bold=True))
    p.append(text(520, 296, "watchdog: повне скидання", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "priority-inversion.svg"), W, H, *p,
           title="Пріоритетна інверсія по кроках")


# ── deadlock-cycle (proj-deadlock): кільце очікування ─────────────────────────
# Ідея: A тримає SPI й чекає SD; B тримає SD й чекає SPI; стрілки «чекає»
# замикаються в коло — ні A, ні B не зрушать.

def fig_deadlock_cycle():
    W, H = 640, 340
    p = []
    # дві задачі по боках
    a, aw, ah = textbox(165, 110, "задача A", size=13, bold=True, fill="#eef4ff", stroke=NEG, sw=1.8)
    b, bw, bh = textbox(475, 110, "задача B", size=13, bold=True, fill="#fdecea", stroke=POS, sw=1.8)
    # два замки знизу
    spi, sw1, sh1 = textbox(165, 250, "spiMtx\n(SPI)", size=12, bold=True, fill="#fdf6e3", stroke="#b8860b", sw=1.8)
    sd, sw2, sh2 = textbox(475, 250, "sdMtx\n(SD)", size=12, bold=True, fill="#fdf6e3", stroke="#b8860b", sw=1.8)
    p += [a, b, spi, sd]

    # A тримає SPI (суцільна), чекає SD (пунктир)
    p.append(arrow(165, 110 + ah / 2, 165, 250 - sh1 / 2 - 2, color=NEG, sw=2.0))
    p.append(text(150, 185, "тримає", size=10, color=NEG, anchor="end"))
    p.append(line(190, 120, 460, 235, color=NEG, sw=1.8, dash="6 4"))
    p.append(arrow(440, 226, 460, 235, color=NEG, sw=1.8))
    p.append(text(330, 150, "чекає SD", size=10, color=NEG))

    # B тримає SD (суцільна), чекає SPI (пунктир)
    p.append(arrow(475, 110 + bh / 2, 475, 250 - sh2 / 2 - 2, color=POS, sw=2.0))
    p.append(text(490, 185, "тримає", size=10, color=POS, anchor="start"))
    p.append(line(450, 120, 180, 235, color=POS, sw=1.8, dash="6 4"))
    p.append(arrow(200, 226, 180, 235, color=POS, sw=1.8))
    p.append(text(330, 205, "чекає SPI", size=10, color=POS))

    p.append(text(W / 2, H - 20, "кільце «чекає» замкнулося → обидві застигли назавжди",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "deadlock-cycle.svg"), W, H, *p,
           title="Взаємне блокування як кільце очікування")


# ── order-discipline (proj-deadlock): єдиний порядок розриває кільце ───────────
# Ідея: ліворуч — протилежні порядки → коло (дедлок); праворуч — усі беруть
# замки в одному порядку (spi → sd) → кільце неможливе.

def fig_order_discipline():
    W, H = 740, 320
    p = []
    midx = W / 2
    p.append(line(midx, 50, midx, H - 30, color="#dddddd", sw=1.2))

    # ліворуч: протилежні порядки
    p.append(text(midx / 2, 72, "Протилежні порядки → дедлок", size=12, color=POS, bold=True))
    p.append(fitbox(40, 100, 150, 56, "A:\nspi → sd", size=11, fill="#eef4ff", stroke=NEG, sw=1.6, bold=True, color=NEG))
    p.append(fitbox(midx - 190, 100, 150, 56, "B:\nsd → spi", size=11, fill="#fdecea", stroke=POS, sw=1.6, bold=True, color=POS))
    # кільце між ними
    p.append(arrow(190, 120, midx - 190, 120, color=POS, sw=1.7))
    p.append(arrow(midx - 190, 145, 190, 145, color=POS, sw=1.7))
    p.append(mtext(midx / 2, 210, ["кожен дивиться у свій бік →", "очікування замикається в коло"], size=10, color=POS))

    # праворуч: єдиний порядок
    cx = midx + (W - midx) / 2
    p.append(text(cx, 72, "Єдиний порядок → безпечно", size=12, color=FIELD, bold=True))
    p.append(fitbox(midx + 50, 100, 150, 56, "A:\nspi → sd", size=11, fill="#eafaf0", stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    p.append(fitbox(W - 200, 100, 150, 56, "B:\nspi → sd", size=11, fill="#eafaf0", stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    p.append(text(cx, 185, "1) завжди spi", size=11, color=INK))
    p.append(text(cx, 207, "2) потім sd", size=11, color=INK))
    p.append(mtext(cx, 245, ["усі беруть в ОДНОМУ порядку →", "кругове очікування неможливе"], size=10, color=FIELD))

    p.append(text(W / 2, H - 14, "і то задарма — самою домовленістю, без нового механізму",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "order-discipline.svg"), W, H, *p,
           title="Дисципліна порядку розриває кільце")


# ── inversion-timeline (proj-priority-inheritance): інверсія на семафорі ───────
# Ідея: часова шкала; Н тримає замок, В чекає, С витісняє Н — затримка В
# розтягується на весь час С (необмежена).

def fig_inversion_timeline():
    W, H = 720, 300
    p = []
    lanes = [("В (3)", POS, 90), ("С (2)", NEG, 150), ("Н (1)", FIELD, 210)]
    x0, x1 = 130, 650
    for name, c, y in lanes:
        p.append(line(x0, y, x1, y, color="#cccccc", sw=1.2))
        p.append(text(x0 - 8, y + 4, name, size=11, color=c, anchor="end", bold=True))

    def bar(y, xa, xb, c, fill):
        return rect(xa, y - 13, xb - xa, 26, fill=fill, stroke=c, sw=1.6, rx=4)

    # Н бере замок
    p.append(bar(210, 150, 210, FIELD, "#dff0df"))
    p.append(text(160, 240, "взяла замок", size=9, color=FIELD, anchor="start"))
    # В чекає замок — довгий блок
    p.append(bar(90, 210, 560, POS, "#fdecea"))
    p.append(text(360, 78, "чекає замок — увесь час С (необмежено)", size=9, color=POS))
    # С витісняє Н і молотить
    p.append(bar(150, 230, 560, NEG, "#eef4ff"))
    p.append(text(380, 138, "молотить CPU (замок не треба)", size=9, color=NEG))
    # Н заморожена
    p.append(rect(210, 210 - 13, 350, 26, fill="#f0f0f0", stroke="#bbbbbb", sw=1.3, rx=4))
    p.append(text(380, 234, "заморожена з замком", size=9, color=MUTED))
    # В дістає замок аж після С
    p.append(bar(90, 560, 650, POS, "#dff0df"))
    p.append(text(605, 78, "нарешті", size=9, color=POS))

    p.append(text(W / 2, H - 16, "порядок виконання В < С — хоча В має вищий пріоритет: інверсія",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "inversion-timeline.svg"), W, H, *p,
           title="Інверсія пріоритетів на бінарному семафорі")


# ── inheritance-timeline (proj-priority-inheritance): успадкування лікує ───────
# Ідея: те саме, але поки Н тримає замок потрібний В, її пріоритет піднято до В,
# тож С не витісняє; В чекає лише тривалість короткої критичної секції.

def fig_inheritance_timeline():
    W, H = 720, 300
    p = []
    lanes = [("В (3)", POS, 90), ("С (2)", NEG, 150), ("Н (1→3)", FIELD, 210)]
    x0, x1 = 140, 650
    for name, c, y in lanes:
        p.append(line(x0, y, x1, y, color="#cccccc", sw=1.2))
        p.append(text(x0 - 8, y + 4, name, size=11, color=c, anchor="end", bold=True))

    def bar(y, xa, xb, c, fill):
        return rect(xa, y - 13, xb - xa, 26, fill=fill, stroke=c, sw=1.6, rx=4)

    # Н бере замок, успадковує пріоритет В — коротка секція
    p.append(bar(210, 230, 330, FIELD, "#dff0df"))
    p.append(text(240, 240, "коротка критична секція", size=9, color=FIELD, anchor="start"))
    p.append(text(280, 195, "пріоритет піднято до В", size=9, color="#b8860b"))
    # В чекає лише цю коротку секцію
    p.append(bar(90, 230, 330, POS, "#fdecea"))
    p.append(text(250, 78, "чекає лише секцію Н — коротко й відомо", size=9, color=POS))
    # С чекає у Ready — не витісняє
    p.append(bar(150, 330, 560, NEG, "#eef4ff"))
    p.append(text(400, 138, "С у Ready: НЕ витісняє Н", size=9, color=NEG))
    # В виконується після віддачі замка
    p.append(bar(90, 330, 470, POS, "#dff0df"))
    p.append(text(400, 84, "В працює", size=9, color=POS))

    p.append(text(W / 2, H - 16, "необмежена інверсія стала обмеженою тривалістю секції Н",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "inheritance-timeline.svg"), W, H, *p,
           title="Успадкування пріоритету (м'ютекс)")


# ── everything-through-queue (proj-queue-pattern): спільні змінні vs черги ─────
# Ідея: ліворуч — задачі сходяться на спільних глобальних (двонапрямлені
# перегони); праворуч — задачі-вузли з'єднані лише чергами-ребрами.

def fig_everything_through_queue():
    W, H = 760, 360
    p = []
    midx = W / 2
    p.append(line(midx, 50, midx, H - 30, color="#dddddd", sw=1.2))

    # ── ліворуч: спільні змінні ──
    p.append(text(midx / 2, 70, "Наївно: спільні глобальні", size=12, color=POS, bold=True))
    # три задачі навколо спільної змінної
    g, gw, gh = textbox(midx / 2, 200, "глобальні:\nflag · cmd · mode", size=11, bold=True,
                        fill="#fdecea", stroke=POS, sw=1.8)
    t1, _, _ = textbox(midx / 2 - 110, 110, "T1", size=11, bold=True, fill="#f4f6f8", stroke=INK, sw=1.5)
    t2, _, _ = textbox(midx / 2 + 110, 110, "T2", size=11, bold=True, fill="#f4f6f8", stroke=INK, sw=1.5)
    t3, _, _ = textbox(midx / 2, 300, "T3", size=11, bold=True, fill="#f4f6f8", stroke=INK, sw=1.5)
    p += [g, t1, t2, t3]
    for tx, ty in [(midx / 2 - 110, 128), (midx / 2 + 110, 128), (midx / 2, 282)]:
        p.append(line(tx, ty, midx / 2, 200, color=POS, sw=1.6, dash="5 4"))
    p.append(text(midx / 2, 250, "кожна стрілка — перегін", size=9, color=POS))

    # ── праворуч: усе через чергу ──
    cx = midx + (W - midx) / 2
    p.append(text(cx, 70, "Усе через чергу", size=12, color=FIELD, bold=True))
    s, sw_, sh = textbox(cx - 120, 120, "Sensor", size=10, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.5)
    bt, btw, bth = textbox(cx - 120, 210, "Button", size=10, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.5)
    ct, ctw, cth = textbox(cx + 20, 165, "Control", size=10, bold=True, fill="#eef4ff", stroke=NEG, sw=1.5)
    ac, acw, ach = textbox(cx + 130, 260, "Actuator", size=10, bold=True, fill="#eef4ff", stroke=NEG, sw=1.5)
    p += [s, bt, ct, ac]
    # черги-ребра (стрілки)
    p.append(arrow(cx - 120 + sw_ / 2, 125, cx + 20 - ctw / 2 - 2, 158, color=FIELD, sw=1.8))
    p.append(arrow(cx - 120 + btw / 2, 205, cx + 20 - ctw / 2 - 2, 175, color=FIELD, sw=1.8))
    p.append(text(cx - 55, 130, "qEvents", size=9, color=FIELD, anchor="start"))
    p.append(arrow(cx + 20 + 6, 165 + cth / 2, cx + 130 - acw / 2 - 2, 260 - ach / 2 - 2, color=NEG, sw=1.8))
    p.append(text(cx + 60, 230, "qActuator", size=9, color=NEG, anchor="start"))
    p.append(text(cx, 320, "вузли — задачі, ребра — черги; спільних змінних нема",
                  size=9, color=FIELD))

    render(os.path.join(OUT, "everything-through-queue.svg"), W, H, *p,
           title="Спільні змінні проти «усе через чергу»")


# ── ownership-transfer (proj-queue-pattern): передавання володіння буфером ─────
# Ідея: виробник наповнив буфер, поклав у чергу лише вказівник; від миті send
# буфера не торкається — володіння «переїхало» до споживача.

def fig_ownership_transfer():
    W, H = 740, 300
    p = []
    # виробник
    prod, pw, ph = textbox(110, 130, "виробник", size=12, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8)
    # буфер
    buf, bw, bh = textbox(W / 2, 130, "буфер 256 Б", size=12, bold=True, fill="#fdf6e3", stroke="#b8860b", sw=1.8)
    # споживач
    cons, cw, ch = textbox(630, 130, "споживач", size=12, bold=True, fill="#eef4ff", stroke=NEG, sw=1.8)
    p += [prod, buf, cons]

    # виробник наповнив (стрілка), потім зона заборони
    p.append(arrow(110 + pw / 2, 130, W / 2 - bw / 2 - 2, 130, color=FIELD, sw=2.0))
    p.append(text(230, 116, "наповнив", size=10, color=FIELD))
    # у чергу — лише вказівник
    p.append(arrow(W / 2 + bw / 2 + 2, 130, 630 - cw / 2 - 2, 130, color=NEG, sw=2.0))
    p.append(text(W / 2 + 90, 116, "send(вказівник)", size=10, color=NEG, anchor="start"))

    # зона заборони для виробника після send
    p.append(rect(60, 180, 230, 50, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    p.append(mtext(175, 200, ["від миті send виробник", "буфера НЕ торкається"], size=10, color=POS))

    # споживач вживає й повертає в пул
    p.append(rect(450, 180, 230, 50, fill="#eef4ff", stroke=NEG, sw=1.5, rx=6))
    p.append(mtext(565, 200, ["споживач вживає", "й повертає в пул"], size=10, color=NEG))

    p.append(text(W / 2, H - 16, "копіювання 256 Б нема; ціна — дисципліна «передав — забув»",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "ownership-transfer.svg"), W, H, *p,
           title="Передавання володіння буфером через чергу")


if __name__ == "__main__":
    # стаття
    fig_problem()
    fig_queue()
    fig_semaphore()
    fig_mutex()
    fig_mutex_vs_sem()
    fig_decision()
    # вставки
    fig_information_bus()
    fig_priority_inversion()
    fig_deadlock_cycle()
    fig_order_discipline()
    fig_inversion_timeline()
    fig_inheritance_timeline()
    fig_everything_through_queue()
    fig_ownership_transfer()
    print("OK: figures written to", OUT)
