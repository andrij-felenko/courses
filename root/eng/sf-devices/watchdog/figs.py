# -*- coding: utf-8 -*-
"""Фігури до теми «Watchdog».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b9770e"   # тепле виділення (підсумкова рамка-нотатка)


# ── 1. Зависання, до якого не дотягнутися ────────────────────────────────────
def fig_hang_problem():
    W, H = 760, 380
    f = []
    # ліворуч: завислий процесор
    pf = textbox(190, 150, "процесор\nзавис", size=15, bold=True,
                 fill="#fdecea", stroke=POS, sw=2, min_w=180)
    f.append(pf[0])
    f.append(text(190, 215, "вічний цикл або очікування", size=11, color=MUTED, italic=True))
    f.append(text(190, 233, "не реагує ні на що", size=11, color=MUTED, italic=True))
    # перекреслена кнопка reset (нікому натиснути)
    f.append(circle(190, 300, 30, fill=FILL, stroke=MUTED, sw=2))
    f.append(text(190, 305, "RESET", size=11, color=MUTED, bold=True))
    f.append(line(166, 324, 214, 276, color=POS, sw=2.6))
    f.append(text(190, 352, "натиснути нікому", size=11, color=POS, bold=True))

    # стрілка-міст
    f.append(arrow(300, 150, 400, 150, color=INK, sw=2))
    f.append(text(350, 138, "лікує лише", size=10, color=MUTED, italic=True))
    f.append(text(350, 173, "скид живлення", size=10, color=MUTED, italic=True))

    # праворуч: недосяжні пристрої
    f.append(text(560, 96, "а пристрій — недосяжний", size=13, bold=True))
    for i, (lbl) in enumerate(["давач на горі", "контролер у стіні", "апарат у космосі"]):
        y = 130 + i * 56
        b = fitbox(430, y, 260, 42, lbl, size=12.5, fill=FILL, stroke=FIELD, sw=1.6)
        f.append(b)
    return render(os.path.join(IMG, "hang-problem.svg"), W, H, *f,
                  title="Завислий пристрій мертвий, а дотягнутися нікому")


# ── 2. Сама ідея watchdog: годуєш — живеш; перестав — скид ────────────────────
def _countdown(x0, ylab, feeds, color, n=5, step=70, top=150, base=210):
    """Лічильник, що падає вниз і скидається при кожній годівлі."""
    g = [line(x0, base, x0 + step * n, base, color=INK, sw=1.6)]  # вісь часу
    for i in range(n):
        x = x0 + i * step
        # «зуб»: лічильник упав і скинувся вгору
        if i in feeds:
            g.append("<polyline points=\"%.1f,%.1f %.1f,%.1f %.1f,%.1f\" fill=\"none\" "
                     "stroke=\"%s\" stroke-width=\"2.4\" stroke-linejoin=\"round\" "
                     "stroke-linecap=\"round\"/>" % (x, base, x, top, x + step * 0.5, base, color))
            g.append(text(x + 4, top - 6, "годуй", size=9, color=color, bold=True, anchor="start"))
    return g


def fig_watchdog_concept():
    W, H = 820, 400
    f = []
    # ── живий ──
    g = textbox(210, 96, "Живий: годуємо вчасно", size=12.5, bold=True,
                fill="#f3faf4", stroke=FIELD, sw=1.8, min_w=300)
    f.append(g[0])
    f.extend(_countdown(70, 150, feeds={0, 1, 2, 3, 4}, color=FIELD, n=5, step=58,
                        top=150, base=220))
    f.append(text(210, 250, "лічильник не доходить до 0 → усе гаразд", size=10, color=INK))

    # ── завис ──
    g = textbox(610, 96, "Завис: годувати нікому", size=12.5, bold=True,
                fill="#fdecea", stroke=POS, sw=1.8, min_w=300)
    f.append(g[0])
    base, top = 220, 150
    f.append(line(440, base, 760, base, color=INK, sw=1.6))
    # одна годівля, потім вільне падіння до нуля
    f.append("<polyline points=\"450,220 450,150 480,220\" fill=\"none\" stroke=\"%s\" "
             "stroke-width=\"2.4\" stroke-linejoin=\"round\" stroke-linecap=\"round\"/>" % FIELD)
    f.append(text(454, 144, "годуй", size=9, color=FIELD, bold=True, anchor="start"))
    f.append("<polyline points=\"480,150 720,220\" fill=\"none\" stroke=\"%s\" "
             "stroke-width=\"2.6\" stroke-linecap=\"round\"/>" % POS)
    f.append(text(600, 168, "не годують…", size=10, color=POS, bold=True))
    f.append(circle(722, 220, 5, fill=POS, stroke=POS))
    f.append(text(722, 240, "0 → СКИД", size=10, color=POS, bold=True))

    # нотатка внизу
    nb = fitbox(110, 300, 600, 64,
                "«Погодувати» (англ. feed, kick, pet) = скинути лічильник watchdog до старту.\n"
                "Поки програма крутиться — вона годує; зависла — годувати нікому, чип рятує себе сам.",
                size=11, fill="#fff8ec", stroke=GOLD, sw=1.4)
    f.append(nb)
    return render(os.path.join(IMG, "watchdog-concept.svg"), W, H, *f,
                  title="Watchdog відлічує вниз; годуй вчасно — живеш, перестав — скид")


# ── 3. Аналогія: запобіжник пильності машиніста ──────────────────────────────
def fig_deadmans_switch():
    W, H = 760, 360
    f = []
    # ліворуч: педаль натиснута → їде
    g = textbox(200, 100, "натискає педаль", size=13, bold=True,
                fill="#f3faf4", stroke=FIELD, sw=1.8, min_w=260)
    f.append(g[0])
    f.append(circle(200, 175, 34, fill="#eaf7ee", stroke=FIELD, sw=2.4))
    f.append(text(200, 170, "педаль", size=11, color=FIELD, bold=True))
    f.append(text(200, 188, "↓", size=16, color=FIELD, bold=True))
    f.append(arrow(150, 250, 250, 250, color=FIELD, sw=2.2))
    f.append(text(200, 280, "поїзд їде", size=13, color=FIELD, bold=True))

    # праворуч: педаль відпущена → стає
    g = textbox(560, 100, "знепритомнів, педаль відпущено", size=13, bold=True,
                fill="#fdecea", stroke=POS, sw=1.8, min_w=300)
    f.append(g[0])
    f.append(circle(560, 175, 34, fill="#fdecea", stroke=POS, sw=2.4))
    f.append(text(560, 180, "✕", size=22, color=POS, bold=True))
    f.append(line(534, 282, 586, 282, color=POS, sw=3))  # «стоп»-смуга
    f.append(text(560, 305, "поїзд сам зупиняється", size=12.5, color=POS, bold=True))

    nb = fitbox(110, 322, 540, 28,
                "Watchdog — це той самий «запобіжник пильності» для прошивки.",
                size=11.5, bold=True, fill="#fff8ec", stroke=GOLD, sw=1.4)
    f.append(nb)
    return render(os.path.join(IMG, "deadmans-switch.svg"), W, H, *f,
                  title="Запобіжник пильності: натискаєш — їдеш, відпустив — стає")


# ── 4. Де годувати: доказ поступу проти сліпого цокання ───────────────────────
def fig_feed_correctly():
    W, H = 820, 380
    f = []
    code = ('Segoe UI, monospace')
    # ── правильно ──
    f.append(rect(40, 70, 360, 240, fill="#f3faf4", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(220, 96, "ПРАВИЛЬНО", size=13, color=FIELD, bold=True))
    f.append(text(60, 124, "годувати в кінці loop():", size=11, color=INK, anchor="start"))
    f.append(text(60, 142, "доказ, що цикл пройшов здоровим", size=10, color=MUTED,
                  anchor="start", italic=True))
    f.append(text(60, 184, "void loop() {", size=11, color=INK, anchor="start"))
    f.append(text(80, 206, "doWork();", size=11, color=MUTED, anchor="start"))
    f.append(text(80, 228, "feedWatchdog();", size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(60, 250, "}", size=11, color=INK, anchor="start"))
    f.append(text(220, 290, "завис усередині → не нагодує → скид ✓", size=9.5, color=INK))

    # ── неправильно ──
    f.append(rect(420, 70, 360, 240, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    f.append(text(600, 96, "НЕПРАВИЛЬНО", size=13, color=POS, bold=True))
    f.append(text(440, 124, "годувати в окремому перериванні,", size=11, color=INK, anchor="start"))
    f.append(text(440, 142, "що тікає завжди", size=10, color=MUTED, anchor="start", italic=True))
    f.append(text(440, 184, "void onTimerISR() {", size=11, color=INK, anchor="start"))
    f.append(text(460, 206, "feedWatchdog();", size=11, color=POS, anchor="start", bold=True))
    f.append(text(460, 228, "// байдуже до loop()!", size=10, color=POS, anchor="start"))
    f.append(text(440, 250, "}", size=11, color=INK, anchor="start"))
    f.append(text(600, 290, "loop завис, а годівля йде → скиду НЕ буде ✗", size=9.5, color=INK))

    nb = fitbox(140, 328, 540, 28,
                "Годівля має бути ознакою життя програми, а не цоканням збоку.",
                size=11.5, bold=True, fill="#fff8ec", stroke=GOLD, sw=1.4)
    f.append(nb)
    return render(os.path.join(IMG, "feed-correctly.svg"), W, H, *f,
                  title="Годуй тільки там, де це доводить поступ")


# ── 5. Спершу попередження-переривання, потім скид ───────────────────────────
def fig_interrupt_then_reset():
    W, H = 760, 320
    f = []
    base, top = 210, 110
    x0, x1 = 70, 690
    f.append(line(x0, base, x1, base, color=INK, sw=1.6))
    # лічильник вниз
    f.append("<polyline points=\"%d,%d %d,%d\" fill=\"none\" stroke=\"%s\" "
             "stroke-width=\"2.6\" stroke-linecap=\"round\"/>" % (x0 + 10, top, 430, base - 10, POS))
    f.append(text(220, 150, "лічильник падає (годівлі нема)", size=11, color=POS, italic=True))

    # крок 1: переривання-попередження
    f.append(line(440, base, 440, 100, color=GOLD, sw=2, dash="5,4"))
    b = fitbox(360, 70, 160, 30, "переривання-\nпопередження", size=10, bold=True,
               fill="#fff8ec", stroke=GOLD, sw=1.6)
    f.append(b)
    f.append(text(440, 232, "зберегти стан,", size=9.5, color=GOLD))
    f.append(text(440, 248, "записати причину", size=9.5, color=GOLD))

    # крок 2: скид
    f.append(line(600, base, 600, 100, color=POS, sw=2.4))
    f.append(circle(600, base, 5, fill=POS, stroke=POS))
    b = fitbox(540, 70, 120, 30, "СКИД чипа", size=11, bold=True,
               fill="#fdecea", stroke=POS, sw=1.8, color=POS)
    f.append(b)
    f.append(text(600, 232, "чистий старт", size=9.5, color=POS))

    nb = fitbox(120, 276, 520, 30,
                "«Передсмертна записка» веде до справжнього баґа — watchdog ще й слідчий.",
                size=11, bold=True, fill="#f3faf4", stroke=FIELD, sw=1.4)
    f.append(nb)
    return render(os.path.join(IMG, "interrupt-then-reset.svg"), W, H, *f,
                  title="Двокроковий watchdog: спершу попередження, потім скид")


# ── 6. Три watchdog ESP32 за доменами ────────────────────────────────────────
def fig_esp32_watchdog():
    W, H = 800, 360
    f = []
    rows = [
        ("Task WDT (TWDT)", "стежить, чи всі задачі (і loop) дістають час на ядрі;\n"
                            "задача-ненажера захопила CPU → тривога", FIELD),
        ("Interrupt WDT (IWDT)", "ловить «німі» зависання: переривання вимкнені\n"
                                 "задовго (довга критична секція, завислий ISR)", NEG),
        ("RTC WDT (RWDT)", "найживучіший, від RTC-домену; стереже навіть\n"
                          "завантаження — застрягання ще до старту коду", GOLD),
    ]
    y = 70
    for name, desc, col in rows:
        f.append(rect(40, y, 720, 78, fill=FILL, stroke=col, sw=1.8, rx=8))
        f.append(text(60, y + 30, name, size=13, color=col, bold=True, anchor="start"))
        for i, ln in enumerate(desc.split("\n")):
            f.append(text(60, y + 50 + i * 17, ln, size=10.5, color=INK, anchor="start"))
        y += 92

    return render(os.path.join(IMG, "esp32-watchdog.svg"), W, H, *f,
                  title="ESP32: три сторожі за доменами живлення й такту")


# ── proj-вставка 1: сліпий feed() проти чекпойнтів ───────────────────────────
def fig_blind_vs_checkpoint():
    W, H = 820, 320
    f = []
    # сліпо
    f.append(rect(40, 70, 360, 200, fill="#fdecea", stroke=POS, sw=2, rx=10))
    f.append(text(220, 96, "Сліпо: feed() щоразу на початку loop()", size=10.5, color=POS, bold=True))
    f.append(text(220, 128, "годуємо БЕЗУМОВНО,", size=10.5, color=INK))
    f.append(text(220, 148, "навіть коли справжня робота стала", size=10.5, color=INK))
    f.append(text(220, 184, "пес мовчить, хоча пристрій зламано", size=10.5, color=POS, bold=True))
    f.append(text(220, 210, "✗ марна сторожа", size=12, color=POS, bold=True))
    f.append(text(220, 242, "feed нічого не доводить про поступ", size=9.5, color=MUTED, italic=True))
    # чекпойнти
    f.append(rect(420, 70, 360, 200, fill="#f3faf4", stroke=FIELD, sw=2, rx=10))
    f.append(text(600, 96, "Чекпойнти: feed лише коли всі живі", size=10.5, color=FIELD, bold=True))
    f.append(text(600, 128, "годуємо, ЛИШЕ коли всі задачі", size=10.5, color=INK))
    f.append(text(600, 148, "відмітились «я жива» нещодавно", size=10.5, color=INK))
    f.append(text(600, 184, "зависла задача → не годуємо → скид", size=10.5, color=FIELD, bold=True))
    f.append(text(600, 210, "✓ чесна сторожа", size=12, color=FIELD, bold=True))
    f.append(text(600, 242, "feed доводить поступ КОЖНОЇ задачі", size=9.5, color=MUTED, italic=True))

    nb = fitbox(110, 286, 600, 26,
                "Годувати — означає підтвердити, що робота рухається, а не просто крутиться loop().",
                size=10.5, bold=True, fill="#fff8ec", stroke=GOLD, sw=1.4)
    f.append(nb)
    return render(os.path.join(IMG, "blind-vs-checkpoint.svg"), W, H, *f,
                  title="Як годувати watchdog: сліпо проти чекпойнтів")


# ── proj-вставка 2: схема чекпойнтів ─────────────────────────────────────────
def fig_checkpoints():
    W, H = 820, 300
    f = []
    tasks = [("задача A", "✓ свіжа", FIELD), ("задача B", "✓ свіжа", FIELD),
             ("задача C", "✗ зависла", POS)]
    for i, (name, st, col) in enumerate(tasks):
        x = 70 + i * 175
        f.append(rect(x, 78, 155, 64, fill=(("#f3faf4") if col == FIELD else "#fdecea"),
                      stroke=col, sw=1.8, rx=10))
        f.append(text(x + 77, 104, name, size=11.5, color=INK, bold=True))
        f.append(text(x + 77, 126, st, size=10.5, color=col, bold=True))
    # збирач
    f.append(rect(600, 78, 150, 64, fill=FILL, stroke=INK, sw=1.6, rx=10))
    f.append(text(675, 104, "збирач:", size=11, color=INK, bold=True))
    f.append(text(675, 124, "усі свіжі?", size=10.5, color=INK))
    # стрілки до рішення
    for i in range(3):
        x = 70 + i * 175 + 77
        f.append(line(x, 144, 410, 184, color=MUTED, sw=1.5))
    f.append(line(675, 144, 410, 184, color=MUTED, sw=1.5))
    # рішення
    f.append(rect(260, 186, 300, 58, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    f.append(text(410, 210, "одна стара → НЕ годувати", size=11.5, color=POS, bold=True))
    f.append(text(410, 230, "→ watchdog скидає пристрій", size=10.5, color=INK))

    nb = fitbox(110, 262, 600, 26,
                "Сторожа стереже, що поступ робить КОЖНА задача, а не лише що крутиться цикл.",
                size=10.5, bold=True, fill="#fff8ec", stroke=GOLD, sw=1.4)
    f.append(nb)
    return render(os.path.join(IMG, "checkpoints.svg"), W, H, *f,
                  title="Чекпойнти: годуй, лише коли ВСІ живі")


# ── comp-вставка 1: ешелон watchdog ESP32 + зовнішній чип ────────────────────
def fig_watchdog_echelon():
    W, H = 820, 470
    f = []
    # рамка SoC
    f.append(rect(20, 44, 780, 286, fill="none", stroke=MUTED, sw=2, rx=14))
    f.append(text(30, 60, "ESP32  SoC", size=11, color=MUTED, anchor="start"))

    # CPU-домен
    f.append(rect(36, 70, 480, 250, fill="#eaf3fb", stroke=NEG, sw=2.4, rx=10))
    f.append(text(276, 92, "CPU-домен (ядра + пам'ять + периферія)", size=12.5, color=NEG, bold=True))
    # TWDT
    f.append(rect(52, 104, 215, 200, fill="#dce9fb", stroke=NEG, sw=1.8, rx=8))
    f.append(text(159, 126, "TWDT", size=14, color=NEG, bold=True))
    f.append(fitbox(64, 138, 191, 34, "idle0 (ядро 0)", size=11, fill="#c6d9f8", stroke=NEG, sw=1.2))
    f.append(fitbox(64, 178, 191, 34, "idle1 (ядро 1)", size=11, fill="#c6d9f8", stroke=NEG, sw=1.2))
    f.append(text(159, 232, "+ ваші задачі (esp_task_wdt_add)", size=9.5, color=MUTED, italic=True))
    f.append(text(159, 262, "ловить: задача-ненажера", size=10, color=NEG))
    f.append(text(159, 286, "→ reset / panic", size=10.5, color=NEG, bold=True))
    # IWDT
    f.append(rect(282, 104, 218, 200, fill="#dce9fb", stroke=NEG, sw=1.8, rx=8))
    f.append(text(391, 126, "IWDT", size=14, color=NEG, bold=True))
    f.append(fitbox(294, 138, 194, 46, "вимкнені переривання\nнадто довго", size=10.5,
                    fill="#c6d9f8", stroke=NEG, sw=1.2))
    f.append(fitbox(294, 192, 194, 34, "завислий ISR", size=10.5, fill="#c6d9f8", stroke=NEG, sw=1.2))
    f.append(text(391, 254, "завжди → panic + reset", size=10, color=NEG))
    f.append(text(391, 276, "планувальник теж стоїть", size=9.5, color=MUTED, italic=True))
    f.append(text(391, 298, "→ reset / panic", size=10.5, color=NEG, bold=True))

    # RTC-домен
    f.append(rect(534, 70, 252, 250, fill="#eafaf1", stroke=FIELD, sw=2.4, rx=10))
    f.append(text(660, 92, "RTC-домен (найживучіший)", size=12, color=FIELD, bold=True))
    f.append(rect(548, 110, 224, 150, fill="#c9ecd4", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(660, 134, "RTC WDT (RWDT)", size=13, color=FIELD, bold=True))
    f.append(fitbox(560, 148, 200, 36, "bootloader → старт", size=11, fill="#a8dcb8",
                    stroke=FIELD, sw=1.2))
    f.append(text(660, 206, "від RTC-генератора", size=10, color=FIELD))
    f.append(text(660, 226, "причина: RTCWDT_*", size=10, color=FIELD))
    f.append(text(660, 290, "→ reset", size=10.5, color=FIELD, bold=True))

    # зовнішній чип
    f.append(rect(60, 350, 700, 104, fill="#fdf2e9", stroke="#e67e22", sw=2.4, rx=10))
    f.append(text(410, 374, "Зовнішній чип-супервізор (клас TPLxxxx / MAXxxxx)", size=12.5,
                  color="#e67e22", bold=True))
    f.append(text(90, 398, "WDI ←", size=11, color=NEG, bold=True, anchor="start"))
    f.append(text(170, 398, "GPIO ESP32 смикає імпульсом (годівля)", size=11, color=INK, anchor="start"))
    f.append(text(90, 420, "RESET →", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(170, 420, "EN/RST ESP32 — скидає весь SoC", size=11, color=INK, anchor="start"))
    f.append(text(90, 442, "window", size=11, color="#e67e22", bold=True, anchor="start"))
    f.append(text(170, 442, "апаратне вікно: не зарано й не запізно", size=11, color=INK, anchor="start"))
    f.append(line(660, 330, 660, 350, color=NEG, sw=1.8))
    f.append(line(180, 350, 180, 330, color=POS, sw=1.8))
    return render(os.path.join(IMG, "watchdog-echelon.svg"), W, H, *f,
                  title="Ешелон watchdog ESP32 і зовнішній чип над доменами SoC")


# ── comp-вставка 2: віконний супервізор ──────────────────────────────────────
def fig_windowed_supervisor():
    W, H = 740, 300
    f = []
    base = 160
    f.append(line(50, base, 690, base, color=INK, sw=1.8))
    f.append(text(700, base + 4, "час", size=12, color=INK, anchor="start"))
    # зони
    f.append("<rect x=\"50\" y=\"134\" width=\"150\" height=\"52\" fill=\"#fdecea\" opacity=\"0.55\"/>")
    f.append(text(125, 124, "ЗАРАНО", size=12, color=POS, bold=True))
    f.append(text(125, 108, "→ reset", size=11, color=POS))
    f.append("<rect x=\"200\" y=\"134\" width=\"320\" height=\"52\" fill=\"#eafaf1\" opacity=\"0.6\"/>")
    f.append(text(360, 160, "ВІКНО — годуй тут", size=13, color=FIELD, bold=True))
    f.append("<rect x=\"520\" y=\"134\" width=\"170\" height=\"52\" fill=\"#fdecea\" opacity=\"0.55\"/>")
    f.append(text(605, 124, "ЗАПІЗНО", size=12, color=POS, bold=True))
    f.append(text(605, 108, "→ reset", size=11, color=POS))
    # межі вікна
    f.append(line(200, 126, 200, 194, color=MUTED, sw=1.5, dash="5,3"))
    f.append(text(200, 208, "t_min", size=11, color=MUTED))
    f.append(line(520, 126, 520, 194, color=MUTED, sw=1.5, dash="5,3"))
    f.append(text(520, 208, "t_max", size=11, color=MUTED))
    # годівлі
    f.append(line(360, 224, 360, 190, color=FIELD, sw=1.8))
    f.append(text(360, 240, "здорова годівля", size=11, color=FIELD, bold=True))
    f.append(line(125, 224, 125, 190, color=POS, sw=1.8))
    f.append(text(125, 240, "«оскаженілий» код", size=11, color=POS, bold=True))
    f.append(text(605, 206, "✗ мовчить (завис)", size=11.5, color=POS, bold=True))

    nb = fitbox(90, 264, 560, 26,
                "TWDT ловить лише «запізно»; вікно (зовнішній супервізор) ловить і «зарано».",
                size=10.5, italic=False, fill=FILL, stroke=MUTED, sw=1.2)
    f.append(nb)
    return render(os.path.join(IMG, "windowed-supervisor.svg"), W, H, *f,
                  title="Віконний зовнішній супервізор: вікно годівлі між t_min і t_max")


if __name__ == "__main__":
    fig_hang_problem()
    fig_watchdog_concept()
    fig_deadmans_switch()
    fig_feed_correctly()
    fig_interrupt_then_reset()
    fig_esp32_watchdog()
    fig_blind_vs_checkpoint()
    fig_checkpoints()
    fig_watchdog_echelon()
    fig_windowed_supervisor()
    print("Готово: 10 фігур у", IMG)
