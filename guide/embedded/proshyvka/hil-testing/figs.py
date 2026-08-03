# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: анатомія стенда — справжня плата в петлі, модель замикає коло ──
def fig_anatomy():
    W, H = 760, 380
    frags = []

    # DUT — справжня плата (ліворуч)
    b, bw, bh = textbox(180, 150, ["Справжня плата (DUT)", "справжня прошивка", "справжній чіп і тайминг"],
                        size=14, bold=False, fill="#eaf0fd", stroke=NEG, sw=2.2, pad=14)
    frags.append(b)
    frags.append(text(180, 92, "У ПЕТЛІ — СПРАВЖНЄ", size=12, color=NEG, bold=True))

    # Симулятор/модель (праворуч)
    s, sw_, sh = textbox(580, 150, ["ПК: симулятор", "модель фізики польоту", "+ модель давачів"],
                        size=14, fill="#f4f6f8", stroke=LINE, sw=1.8, pad=14)
    frags.append(s)
    frags.append(text(580, 92, "МОДЕЛЬ", size=12, color=MUTED, bold=True))

    # верхня стрілка: модель -> плата (виміри інжектуються)
    frags.append(arrow(500, 128, 262, 128, color=NEG, sw=2.2))
    frags.append(text(381, 116, "виміри → в плату (інжекція)", size=12, color=NEG, bold=True))

    # нижня стрілка: плата -> модель (команди на мотори читаються)
    frags.append(arrow(262, 178, 500, 178, color=POS, sw=2.2))
    frags.append(text(381, 200, "команди на мотори (зчитування)", size=12, color=POS, bold=True))

    # інтерфейсна плата — на стику дротів
    ib = fitbox(330, 232, 100, 46, "інтерфейс\n(дроти, шини, АЦП/ЦАП)", size=11, fill="#eafaf0", stroke=FIELD, sw=1.8)
    frags.append(ib)
    # конектор інтерфейс↔коло: стартує НИЖЧЕ напису «команди на мотори» (bbox ≤ y≈202),
    # щоб пунктир не різав його — веде від y=206 до верху плати (y=232)
    frags.append(line(381, 206, 381, 232, color=FIELD, sw=1.5, dash="4 3"))

    # петля фізики під симулятором
    frags.append(text(580, 214, "→ рахує новий стан апарата →", size=11, color=MUTED, italic=True))
    frags.append(text(580, 232, "нові виміри", size=11, color=MUTED, italic=True))

    # підпис-різниця з SITL
    frags.append(line(40, 300, 720, 300, color=MUTED, sw=1))
    frags.append(text(380, 326, "Різниця з SITL: там у петлі лише КОД (процес на ПК).",
                     size=13, color=INK, bold=True))
    frags.append(text(380, 348, "Тут справжні КОД і ПЛАТА — модель лише навколо. Заліза не прибрано, прибрано тільки світ.",
                     size=12, color=MUTED))

    render(os.path.join(IMG, 'anatomy.svg'), W, H, *frags,
           title="HIL-стенд: справжня плата в петлі, модель замикає коло")


# ── Фігура 2: дві «двері» інжекції — електрична проти програмної ──
def fig_two_doors():
    W, H = 760, 420
    frags = []
    frags.append(text(380, 52, "Куди підсунути виміри справжній платі — дві двері", size=15, bold=True))

    # ── ліва колонка: електрична двері ──
    frags.append(fitbox(60, 80, 300, 34, "Електрична двері", size=15, fill="#fdecea", stroke=POS, sw=2, bold=True))
    frags.append(fitbox(60, 124, 300, 40, "модель → сигнал на РЕАЛЬНІ ніжки й шини\n(SPI/I²C/АЦП), як зі справжнього давача",
                        size=11, fill=BG, stroke=MUTED, sw=1))
    frags.append(fitbox(60, 172, 140, 60, "весь стек\nдрайверів\nпрацює", size=12, fill="#eafaf0", stroke=FIELD, sw=1.6))
    frags.append(fitbox(220, 172, 140, 60, "потрібна\nінтерфейсна\nплата, важко", size=12, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(text(210, 258, "+ найчесніше: чіп нічого не підозрює", size=11, color=FIELD, bold=True))
    frags.append(text(210, 276, "− найдорожче: залізо, що вдає давачі", size=11, color=POS))

    # ── права колонка: програмна двері ──
    frags.append(fitbox(400, 80, 300, 34, "Програмна двері (HIL-повідомлення)", size=13, fill="#eaf0fd", stroke=NEG, sw=2, bold=True))
    frags.append(fitbox(400, 124, 300, 40, "модель → HIL-повідомлення по USB/UART;\nу коді шов бере вимір звідти, не з драйвера",
                        size=11, fill=BG, stroke=MUTED, sw=1))
    frags.append(fitbox(400, 172, 140, 60, "просто:\nлише дріт\nданих", size=12, fill="#eafaf0", stroke=FIELD, sw=1.6))
    frags.append(fitbox(560, 172, 140, 60, "драйвери\nдавачів\nобійдено", size=12, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(text(550, 258, "+ дешево, лиш кабель даних", size=11, color=FIELD, bold=True))
    frags.append(text(550, 276, "− не перевіряє сам стек драйверів", size=11, color=POS))

    # спільний висновок
    frags.append(line(40, 306, 720, 306, color=MUTED, sw=1))
    frags.append(text(380, 332, "Та сама межа «логіка / залізо» (шов HAL), що й у піраміді тестів —",
                     size=12, color=INK))
    frags.append(text(380, 352, "лише тепер по один бік шва СПРАВЖНІЙ чіп, а не процес на ПК.",
                     size=12, color=INK))
    frags.append(text(380, 384, "Чим правіше ставиш двері (ближче до ніжок) — тим реалістичніше й дорожче.",
                     size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'two-doors.svg'), W, H, *frags)


# ── Фігура 3: реальний час не спиниш — латентність лінка вбиває петлю ──
def fig_realtime():
    W, H = 800, 360
    frags = []
    frags.append(text(380, 46, "Чіп біжить по СПРАВЖНЬОМУ годиннику — його не поставиш на паузу", size=14, bold=True))

    # вісь часу
    y0 = 120
    frags.append(line(70, y0, 690, y0, color=INK, sw=2))
    frags.append(arrow(680, y0, 700, y0, color=INK, sw=2))
    frags.append(text(700, y0 + 4, "t", size=14, bold=True, anchor="start"))

    # такти керування на платі — фіксований крок
    xs = [120, 230, 340, 450, 560]
    for x in xs:
        frags.append(line(x, y0 - 8, x, y0 + 8, color=NEG, sw=2))
    frags.append(text(120, y0 + 28, "крок", size=11, color=NEG))
    frags.append(text(340, y0 - 22, "плата вимагає новий вимір КОЖНІ 2.5 мс — і не чекатиме",
                     size=12, color=NEG, bold=True))

    # бюджет: інжекція має встигнути в проміжок
    frags.append(line(230, y0 + 40, 340, y0 + 40, color=FIELD, sw=2))
    frags.append(line(230, y0 + 34, 230, y0 + 46, color=FIELD, sw=2))
    frags.append(line(340, y0 + 34, 340, y0 + 46, color=FIELD, sw=2))
    frags.append(text(285, y0 + 62, "модель + лінк мусять встигнути ТУТ", size=11, color=FIELD, bold=True))

    # запізнілий вимір — приходить після такту -> шкода
    lx = 490
    frags.append(circle(lx, y0 + 40, 7, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(lx, y0 + 44, "!", size=12, color=POS, bold=True))
    frags.append(text(lx + 14, y0 + 44, "вимір спізнився — плата вже зробила крок на старому", size=11, color=POS, anchor="start"))

    # два виходи
    frags.append(line(40, 250, 720, 250, color=MUTED, sw=1))
    frags.append(fitbox(60, 264, 300, 74,
                        "Лінк має бути ШВИДКИЙ і СТАБІЛЬНИЙ\nUSB/UART чи дротовий Ethernet, не Wi-Fi.\nВелика затримка/тремтіння — петля розпадається\n(так і вмерла класична HIL ArduPilot).",
                        size=11, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(fitbox(400, 264, 300, 74,
                        "Або крок-у-крок (lockstep) НА ЗАЛІЗІ:\nмодель і прошивка ходять по черзі за\nмодельним годинником — так робить PX4.\nАле чіп мусить уміти чекати на модель.",
                        size=11, fill="#eafaf0", stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'realtime.svg'), W, H, *frags)


# ── Фігура (вставка hist): пів століття HIL однією смугою ──
def fig_hist_timeline():
    W, H = 820, 470
    frags = []
    frags.append(text(W / 2, 34, "Пів століття HIL: як несправжній світ дійшов до справжнього заліза й повернувся в чип",
                     size=15, bold=True))

    # головна вісь часу
    y = 120
    frags.append(line(60, y, 760, y, color=INK, sw=2.5))
    frags.append(arrow(752, y, 780, y, color=INK, sw=2.5))
    frags.append(text(778, y + 5, "час", size=12, bold=True, anchor="start"))

    # віхи: (x, рік, підпис зверху коротко, колір вузла)
    nodes = [
        (120, "1929",  NEG),
        (300, "1940–70-ті", NEG),
        (470, "1989",  FIELD),
        (600, "1992 →", POS),
        (720, "нині",  INK),
    ]
    for x, yr, col in nodes:
        frags.append(circle(x, y, 7, fill=BG, stroke=col, sw=2.5))
        frags.append(text(x, y - 16, yr, size=12, color=col, bold=True))

    # картки-пояснення попід віхами (fitbox — текст гарантовано влазить)
    frags.append(fitbox(60, y + 26, 130, 90,
                        "Тренажер Лінка:\nмодельований світ —\nЛЮДИНІ (пілоту).\nЩе не залізо в петлі.",
                        size=10, fill="#eaf0fd", stroke=NEG, sw=1.6))
    frags.append(fitbox(210, y + 26, 170, 90,
                        "Аналогові стійки й столи\nруху: модельований світ —\nСПРАВЖНЬОМУ залізу\n(ракети, літаки, HiMAT).",
                        size=10, fill="#eaf0fd", stroke=NEG, sw=1.6))
    frags.append(fitbox(398, y + 26, 150, 90,
                        "dSPACE: перший\nHIL-симулятор в АВТО.\nРеальний час стає\nтоваром із дедлайном.",
                        size=10, fill="#eafaf0", stroke=FIELD, sw=1.6))
    frags.append(fitbox(556, y + 26, 130, 90,
                        "DO-178 (авіа),\nISO 26262 (авто):\nстенд стає ЗАКОНОМ,\nа не зручністю.",
                        size=10, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(fitbox(694, y + 26, 118, 90,
                        "У дронах зовнішній\nHIL відступає:\nlockstep (PX4),\nсимуляція на залізі\n(ArduPilot).",
                        size=10, fill=BG, stroke=INK, sw=1.6))

    # нижній рядок-мораль: коло історії
    frags.append(line(40, 350, 780, 350, color=MUTED, sw=1))
    frags.append(text(W / 2, 378,
                     "Колесо оберталося умовою «чи тягне цільове залізо модель САМО»:",
                     size=12, color=INK, bold=True))
    frags.append(text(W / 2, 400,
                     "спершу НІ → модель виносили назовні (стійка, потім ПК);",
                     size=12, color=MUTED))
    frags.append(text(W / 2, 420,
                     "тепер малий чип тягне модель сам → у дронах вона вертається ВСЕРЕДИНУ чипа.",
                     size=12, color=MUTED))
    frags.append(text(W / 2, 448,
                     "У великій техніці модель усе ще надто важка — там повний електричний HIL непорушний і обов'язковий.",
                     size=11, color=INK, italic=True))

    render(os.path.join(IMG, 'hist-timeline.svg'), W, H, *frags)


# ── Фігура (detailed): джитер — вбиває хвіст, не середнє ──
def fig_jitter():
    W, H = 812, 430
    frags = []
    frags.append(text(W / 2, 30, "Керує стендом хвіст затримки, а не середнє", size=16, bold=True))

    # осі: x — затримка, y — частота
    x0, y0 = 80, 300          # початок координат
    xmax = 700
    frags.append(arrow(x0, y0, xmax + 20, y0, color=INK, sw=2))
    frags.append(text(xmax + 24, y0 + 5, "затримка кола", size=11, anchor="start", color=MUTED))
    frags.append(arrow(x0, y0, x0, 70, color=INK, sw=2))
    frags.append(text(x0 - 8, 66, "частота", size=11, anchor="end", color=MUTED))

    # дедлайн (спільна вертикаль)
    xd = 560
    frags.append(line(xd, y0, xd, 80, color=INK, sw=2, dash="6 4"))
    frags.append(text(xd, 74, "ДЕДЛАЙН 2500 мкс", size=12, color=INK, bold=True))

    import math
    # вузький розподіл (дротовий) — центр 300, вузький; увесь ліворуч дедлайну
    def bump(cx, spread, amp, base_x):
        pts = []
        for i in range(0, 121):
            xx = base_x + i * 5
            v = amp * math.exp(-((xx - cx) ** 2) / (2 * spread ** 2))
            pts.append((xx, y0 - v))
        return pts

    def poly(pts, color, sw=2.5):
        d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)

    narrow = bump(240, 26, 190, x0)      # дротовий: центр ~240 (лівіше), вузький
    wide = bump(300, 95, 95, x0)         # Wi-Fi: те саме-менше середнє, широкий, довгий хвіст

    frags.append(poly(narrow, NEG, 3))
    frags.append(poly(wide, POS, 2.5))

    # підписи кривих
    frags.append(text(210, 118, "дротовий (USB/UART)", size=12, color=NEG, bold=True, anchor="middle"))
    frags.append(text(210, 136, "вузький — увесь до дедлайну", size=10, color=NEG, anchor="middle"))
    frags.append(text(470, 176, "Wi-Fi", size=12, color=POS, bold=True))
    frags.append(text(470, 194, "те саме середнє, довгий хвіст", size=10, color=POS))

    # заштрихована зона хвоста за дедлайном
    frags.append(text(628, 250, "хвіст за", size=10, color=POS, anchor="middle"))
    frags.append(text(628, 264, "дедлайном =", size=10, color=POS, anchor="middle"))
    frags.append(text(628, 278, "зриви петлі", size=10, color=POS, bold=True, anchor="middle"))
    frags.append(arrow(600, 250, 585, 292, color=POS, sw=1.6))

    # нижній висновок
    frags.append(line(40, 340, 740, 340, color=MUTED, sw=1))
    frags.append(text(W / 2, 366, "Один спізнілий такт із тисячі × 240 000 тактів за політ = сотні зривів.",
                     size=12, color=INK, bold=True))
    frags.append(text(W / 2, 388, "Тому лінк оцінюють по НАЙГІРШІЙ затримці, не по середній —",
                     size=11, color=MUTED))
    frags.append(text(W / 2, 408, "і Wi-Fi заборонений за хвіст, а не за швидкість.",
                     size=11, color=MUTED))

    render(os.path.join(IMG, 'jitter.svg'), W, H, *frags)


# ── Фігура (detailed): вільний хід проти lockstep ──
def fig_lockstep():
    W, H = 800, 470
    frags = []
    frags.append(text(W / 2, 30, "Дві конструкції HIL: хто дає команду «крок»", size=16, bold=True))

    # ── ВЕРХ: вільний хід ──
    frags.append(fitbox(40, 56, 200, 30, "ВІЛЬНИЙ ХІД", size=14, fill="#fdecea", stroke=POS, sw=2, bold=True))
    # часова вісь плати
    yA = 130
    frags.append(line(60, yA, 620, yA, color=INK, sw=2))
    frags.append(text(60, yA - 30, "годинник ПЛАТИ (власний кварц) веде час:", size=11, color=POS, anchor="start"))
    for x in [120, 240, 360, 480, 600]:
        frags.append(line(x, yA - 7, x, yA + 7, color=POS, sw=2))
    frags.append(text(120, yA + 22, "крок кожні 2500 мкс — байдуже, чи є свіжий вимір", size=11, color=POS, anchor="start"))
    # спізнілий вимір
    frags.append(circle(430, yA - 26, 7, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(430, yA - 22, "!", size=11, color=POS, bold=True))
    frags.append(text(444, yA - 22, "вимір спізнивсь → крок на СТАРОМУ; кварц дрейфує", size=10, color=POS, anchor="start"))
    frags.append(text(660, yA + 4, "лінк і дрейф", size=10, color=POS, anchor="start"))
    frags.append(text(660, yA + 18, "ПСУЮТЬ правильність", size=10, color=POS, bold=True, anchor="start"))

    # роздільник
    frags.append(line(40, 200, 760, 200, color=MUTED, sw=1, dash="4 3"))

    # ── НИЗ: lockstep ──
    frags.append(fitbox(40, 216, 200, 30, "LOCKSTEP", size=14, fill="#eafaf0", stroke=FIELD, sw=2, bold=True))
    yB = 300
    frags.append(text(60, yB - 46, "годинник МОДЕЛІ (мітка T) веде час; плата його позичає:", size=11, color=FIELD, anchor="start"))
    # чотири блоки циклу
    b1 = fitbox(70, yB - 26, 150, 52, "модель:\nстан на час T\n+ вимір {…, t=T}", size=10, fill="#eafaf0", stroke=FIELD, sw=1.6)
    frags.append(b1)
    frags.append(arrow(224, yB, 264, yB, color=INK, sw=2))
    frags.append(text(244, yB - 8, "вимір", size=9, color=MUTED))
    b2 = fitbox(268, yB - 26, 150, 52, "плата: бере T\nза «зараз»,\nОДИН крок", size=10, fill="#eaf0fd", stroke=NEG, sw=1.6)
    frags.append(b2)
    frags.append(arrow(422, yB, 462, yB, color=INK, sw=2))
    frags.append(text(442, yB - 8, "тяга", size=9, color=MUTED))
    b3 = fitbox(466, yB - 26, 160, 52, "модель: інтегрує\nфізику T → T+Δt", size=10, fill="#eafaf0", stroke=FIELD, sw=1.6)
    frags.append(b3)
    # стрілка назад (T += Δt)
    frags.append(line(546, yB + 26, 546, yB + 44, color=INK, sw=1.6))
    frags.append(line(546, yB + 44, 145, yB + 44, color=INK, sw=1.6))
    frags.append(arrow(145, yB + 44, 145, yB + 28, color=INK, sw=1.6))
    frags.append(text(345, yB + 58, "T ← T + Δt   (модельний час стоїть, поки котрась сторона чекає)", size=10, color=MUTED, anchor="middle"))
    frags.append(text(650, yB - 8, "лінк і дрейф", size=10, color=FIELD, anchor="start"))
    frags.append(text(650, yB + 6, "НЕ впливають", size=10, color=FIELD, bold=True, anchor="start"))
    frags.append(text(650, yB + 20, "на правильність", size=10, color=FIELD, anchor="start"))

    # нижній висновок
    frags.append(line(40, 392, 760, 392, color=MUTED, sw=1))
    frags.append(text(W / 2, 418, "Вільний хід зберігає СПРАВЖНІЙ тайминг (ловить гонки), та чутливий до лінка й дрейфу.",
                     size=11, color=INK))
    frags.append(text(W / 2, 440, "Lockstep імунний до лінка й дрейфу (один годинник), але РОЗМИВАЄ реальний тайминг і йде повільніше.",
                     size=11, color=INK))

    render(os.path.join(IMG, 'lockstep.svg'), W, H, *frags)


# ── Фігура (detailed): чотири способи електричної інжекції ──
def fig_electrical_injection():
    W, H = 820, 440
    frags = []
    frags.append(text(W / 2, 30, "Електрична інжекція — чотири прийоми за типом давача", size=16, bold=True))
    frags.append(text(W / 2, 52, "інтерфейсна плата завжди АКТИВНА: точніша й швидша за той пристрій, який удає", size=11, color=MUTED, italic=True))

    # чотири колонки-картки
    cols = [
        (30, "SPI / I²C\n(давач ведений)", "інтерфейс = SLAVE:\nловить такт майстра-DUT,\nвчасно віддає байти\n(мікросекундний дедлайн)", "найскладніше:\nсвій МК/FPGA", NEG),
        (230, "Аналог через АЦП", "інтерфейс = ЦАП:\nвиставляє напругу на вхід.\nКрок ЦАП мусить бути\nДРІБНІШИЙ за молодший\nбіт АЦП DUT", "13-біт ЦАП\nдля 12-біт АЦП", FIELD),
        (430, "UART-GPS\n(давач сам шле)", "інтерфейс генерує кадри\n(NMEA/двійкові) з модельними\nкоординатами за розкладом\nсправжнього приймача", "найлегше:\nтакт ловити не треба", NEG),
        (630, "Керована периферія\n(DUT сам веде)", "інтерфейс = приймач:\nловить команди DUT як\nвиконавчий пристрій\nі рапортує моделі", "дзеркало\nactuator readback", POS),
    ]
    for x, title_, body, tag, col in cols:
        frags.append(fitbox(x, 80, 170, 44, title_, size=12, fill=BG, stroke=col, sw=2, bold=True))
        frags.append(fitbox(x, 134, 170, 120, body, size=10, fill="#f4f6f8", stroke=MUTED, sw=1))
        frags.append(fitbox(x, 264, 170, 40, tag, size=10, fill="#fdf4e6" if col == FIELD else BG, stroke=col, sw=1.4, bold=True))

    # спільний висновок
    frags.append(line(40, 336, 780, 336, color=MUTED, sw=1))
    frags.append(text(W / 2, 362, "Ось чому електрична двері дорога: інтерфейсна плата — це НАБІР емуляторів давачів,",
                     size=12, color=INK, bold=True))
    frags.append(text(W / 2, 384, "кожен зі своїм контролером, кожен точніший і швидший за оригінал, кожен під конкретну модель.",
                     size=11, color=MUTED))
    frags.append(text(W / 2, 412, "Правило спільне з ЦАП і зі зчитувачем ШІМ: хто дурить пристрій — мусить бути точнішим за нього.",
                     size=11, color=INK, italic=True))

    render(os.path.join(IMG, 'electrical-injection.svg'), W, H, *frags)


# ── Фігура (proj): байтова розкладка двох кадрів lockstep ──
def fig_frame_layout():
    W, H = 860, 470
    frags = []
    frags.append(text(W / 2, 30, "Два кадри lockstep-обміну: що саме летить дротом", size=16, bold=True))

    # спільна легенда полів
    def field_cells(x0, y0, cells, col):
        """cells: список (ширина_px, верхній_підпис, нижній_підпис_байти)."""
        out = []
        x = x0
        for w, top, bot in cells:
            out.append(rect(x, y0, w, 56, fill=col, stroke=INK, sw=1.4, rx=4))
            out.append(text(x + w / 2, y0 + 24, top, size=11, color=INK, bold=True))
            out.append(text(x + w / 2, y0 + 42, bot, size=10, color=MUTED))
            x += w
        return out, x

    # ── Кадр 1: давачі (модель → плата) ──
    frags.append(fitbox(40, 66, 260, 30, "Кадр ДАВАЧІВ  (модель → плата)", size=13,
                        fill="#eaf0fd", stroke=NEG, sw=2, bold=True))
    c1 = [
        (70,  "SYNC", "2 Б: 0xB5 0x62"),
        (60,  "seq",  "2 Б: лічильник"),
        (90,  "t_us", "4 Б: модельн. час"),
        (150, "imu (roll…az)", "24 Б: 6×float"),
        (90,  "GPS lat/lon", "8 Б"),
        (74,  "CRC-16", "2 Б"),
    ]
    cells1, xend1 = field_cells(40, 104, c1, "#eaf6ff")
    frags.extend(cells1)
    frags.append(text(40, 178, "усього 42 байти — фіксована довжина, тому приймач точно знає межу кадру",
                     size=11, color=NEG, anchor="start"))

    # ── Кадр 2: актуатори (плата → модель) ──
    frags.append(fitbox(40, 210, 260, 30, "Кадр АКТУАТОРІВ  (плата → модель)", size=13,
                        fill="#eafaf0", stroke=FIELD, sw=2, bold=True))
    c2 = [
        (70,  "SYNC", "2 Б: 0xB5 0x62"),
        (60,  "seq",  "2 Б: ЕХО seq"),
        (90,  "t_us", "4 Б: ехо часу"),
        (150, "thr[0..3]", "16 Б: 4×float"),
        (74,  "CRC-16", "2 Б"),
    ]
    cells2, xend2 = field_cells(40, 248, c2, "#eafcf3")
    frags.extend(cells2)
    frags.append(text(40, 322, "усього 26 байтів — seq і t_us вертаються ЕХОМ: модель бачить, на який саме вимір це відповідь",
                     size=11, color=FIELD, anchor="start"))

    # висновок про роль кожного поля
    frags.append(line(40, 350, 820, 350, color=MUTED, sw=1))
    frags.append(text(W / 2, 376, "Кожне поле має роботу, і без жодного протокол ламається:",
                     size=12, color=INK, bold=True))
    frags.append(text(W / 2, 398, "SYNC — знайти початок у потоці байтів · seq — зловити втрату/дубль · t_us — вести модельний час",
                     size=11, color=MUTED))
    frags.append(text(W / 2, 418, "CRC-16 — відкинути спотворений кадр раніше, ніж він зіб'є оцінку положення.",
                     size=11, color=MUTED))
    frags.append(text(W / 2, 446, "Фіксована довжина + SYNC + CRC = кадр або приймається цілим і правильним, або відкидається — третього нема.",
                     size=11, color=INK, italic=True))

    render(os.path.join(IMG, 'frame-layout.svg'), W, H, *frags)


# ── Фігура (proj): seq ловить втрату, дубль і розсинхрон ──
def fig_seq_recovery():
    W, H = 840, 440
    frags = []
    frags.append(text(W / 2, 30, "Один лічильник seq ловить три біди лінка", size=16, bold=True))

    # вісь прибуття кадрів
    y = 130
    frags.append(line(60, y, 740, y, color=INK, sw=2))
    frags.append(arrow(732, y, 760, y, color=INK, sw=2))
    frags.append(text(758, y + 5, "кадри, що ПРИЙШЛИ", size=10, anchor="start", color=MUTED))

    # прийняті seq у порядку прибуття (з дефектами)
    seqs = [
        (120, "7",  NEG,   "норма"),
        (210, "8",  NEG,   "норма"),
        (300, "10", POS,   "СТРИБОК: 9 загубивсь"),
        (420, "10", POS,   "ПОВТОР: дубль 10"),
        (540, "11", NEG,   "норма"),
        (630, "12", NEG,   "норма"),
    ]
    for x, s, col, _ in seqs:
        frags.append(circle(x, y, 15, fill=BG, stroke=col, sw=2.4))
        frags.append(text(x, y + 5, s, size=13, color=col, bold=True))

    # анотації над дефектами (рознесені, щоб не накладались)
    frags.append(text(300, y - 34, "очікували 9, прийшло 10", size=10, color=POS, anchor="middle"))
    frags.append(text(300, y - 20, "→ втрата кадру 9", size=10, color=POS, bold=True, anchor="middle"))
    frags.append(text(420, y - 34, "seq не зріс (10 = 10)", size=10, color=POS, anchor="middle"))
    frags.append(text(420, y - 20, "→ дубль, ВІДКИНУТИ", size=10, color=POS, bold=True, anchor="middle"))

    # три правила-реакції
    frags.append(line(40, 210, 800, 210, color=MUTED, sw=1))
    frags.append(fitbox(50, 226, 240, 96,
                        "ВТРАТА (seq перескочив)\nу lockstep НЕ буває:\nмодель шле наступний кадр\nлише отримавши ЕХО.\nБуває лиш на СТАРТІ й після\nскидання — тоді ре-синхрон.",
                        size=10, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(fitbox(300, 226, 240, 96,
                        "ДУБЛЬ (seq не зріс):\nмовчки ВІДКИНУТИ кадр —\nне робити другий крок на\nтому самому t_us, бо це\nдвічі проінтегрує фізику й\nзаб'є оцінку положення.",
                        size=10, fill="#fdf4e6", stroke=FIELD, sw=1.6))
    frags.append(fitbox(550, 226, 240, 96,
                        "РОЗСИНХРОН (t_us стрибнув\nназад або зник вперед):\nмітка часу не монотонна —\nВІДКИНУТИ кадр і чекати\nмонотонного. Так захищаємо\nΔt фільтра від від'ємного.",
                        size=10, fill="#eaf0fd", stroke=NEG, sw=1.6))

    # нижня мораль
    frags.append(line(40, 344, 800, 344, color=MUTED, sw=1))
    frags.append(text(W / 2, 370, "Правило одне на всі три: приймай кадр, ЛИШЕ якщо seq зріс рівно на 1 І t_us строго більший.",
                     size=12, color=INK, bold=True))
    frags.append(text(W / 2, 392, "Інакше — тихо відкинь і лишись на старому стані: краще пропустити крок, ніж зробити хибний.",
                     size=11, color=MUTED))
    frags.append(text(W / 2, 418, "У lockstep це майже ніколи не спрацьовує (черга з одного кадру), але коштує кілька рядків — і рятує від зависань.",
                     size=11, color=INK, italic=True))

    render(os.path.join(IMG, 'seq-recovery.svg'), W, H, *frags)


# ── Фігура (math-вставка): пропускна проти латентності — два канали ──
def fig_throughput_latency():
    W, H = 780, 400
    frags = []
    frags.append(text(W / 2, 30, "Пропускна й латентність — різні величини", size=16, bold=True))

    frags.append(text(W / 2, 54, "одне й те саме маленьке HIL-повідомлення (~100 байтів) крізь два канали", size=12, color=MUTED))

    # ── ЛІВОРУЧ: тонкий потоковий канал (UART) ──
    lx = 60
    frags.append(fitbox(lx, 84, 300, 30, "ТОНКИЙ ПОТОКОВИЙ КАНАЛ (UART)", size=12, fill="#eaf0fd", stroke=NEG, sw=2, bold=True))
    yb = 150
    frags.append(text(lx, yb - 10, "латентність ≈ 0, тече одразу", size=11, color=NEG, anchor="start"))
    frags.append(rect(lx, yb, 6, 34, fill=NEG, stroke=NEG, sw=1))
    frags.append(rect(lx + 6, yb, 300, 34, fill="#eaf0fd", stroke=NEG, sw=1.6))
    frags.append(text(lx + 156, yb + 22, "СЕРІАЛІЗАЦІЯ (довга)", size=11, color=NEG, bold=True))
    frags.append(text(lx + 8, yb + 58, "затримка = майже цілком серіалізація", size=11, color=INK, anchor="start"))
    frags.append(text(lx + 8, yb + 76, "обсяг × 10 / швидкість_бод", size=11, color=MUTED, anchor="start"))

    # ── ПРАВОРУЧ: товстий кадровий канал (USB) ──
    rx = 420
    frags.append(fitbox(rx, 84, 300, 30, "ТОВСТИЙ КАДРОВИЙ КАНАЛ (USB)", size=12, fill="#eafaf0", stroke=FIELD, sw=2, bold=True))
    frags.append(text(rx, yb - 10, "чекає до кадру опитування — латентність", size=11, color=FIELD, anchor="start"))
    frags.append(rect(rx, yb, 250, 34, fill="#eafaf0", stroke=FIELD, sw=1.6))
    frags.append(text(rx + 125, yb + 22, "ЛАТЕНТНІСТЬ КАДРУ (довга)", size=11, color=FIELD, bold=True))
    frags.append(rect(rx + 250, yb, 16, 34, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(text(rx + 258, yb + 58, "серіал.", size=10, color=FIELD, anchor="middle"))
    frags.append(text(rx + 8, yb + 76, "серіалізація миттєва, зате чекання кадру", size=11, color=MUTED, anchor="start"))

    frags.append(line(40, 300, 740, 300, color=MUTED, sw=1))
    frags.append(text(W / 2, 326, "Пропускна задає ДОВЖИНУ серіалізації; латентність — сталий наклад до старту.",
                     size=12, color=INK, bold=True))
    frags.append(text(W / 2, 348, "Для маленького повідомлення вирішує СУМА обох —", size=11, color=MUTED))
    frags.append(text(W / 2, 368, "тому канал із більшою пропускною не конче має меншу повну затримку.", size=11, color=INK, italic=True))

    render(os.path.join(IMG, 'throughput-latency.svg'), W, H, *frags)


# ── Фігура (math-вставка): повна затримка туди-назад по трьох каналах ──
def fig_link_comparison():
    W, H = 780, 448
    frags = []
    frags.append(text(W / 2, 30, "Повна затримка ланки (100 байтів): серіалізація + латентність", size=16, bold=True))

    x0, y0 = 220, 322
    top = 70
    frags.append(arrow(x0, y0, x0, top, color=INK, sw=2))
    frags.append(text(x0 - 8, top - 4, "затримка, мкс", size=11, anchor="end", color=MUTED))
    frags.append(line(x0, y0, 740, y0, color=INK, sw=2))

    scale = 240.0 / 1100.0

    def bar(cx, serial_us, lat_us, label, sub):
        bw = 90
        x = cx - bw / 2
        hs = serial_us * scale
        hl = lat_us * scale
        frags.append(rect(x, y0 - hs, bw, hs, fill="#dfe6f5", stroke=NEG, sw=1.6))
        if hl > 0:
            frags.append(rect(x, y0 - hs - hl, bw, hl, fill="#fdecea", stroke=POS, sw=1.6))
        frags.append(text(cx, y0 + 22, label, size=12, color=INK, bold=True))
        frags.append(text(cx, y0 + 40, sub, size=10, color=MUTED))
        frags.append(text(cx, y0 - hs - hl - 8, "≈ %d" % int(serial_us + lat_us), size=11, color=INK, bold=True))

    # легенда — у порожньому лівому верхньому куті (лівіше осі)
    frags.append(rect(40, top + 6, 14, 14, fill="#dfe6f5", stroke=NEG, sw=1.4))
    frags.append(text(58, top + 18, "серіалізація", size=11, color=NEG, anchor="start", bold=True))
    frags.append(text(58, top + 33, "обсяг / пропускна", size=10, color=MUTED, anchor="start"))
    frags.append(rect(40, top + 48, 14, 14, fill="#fdecea", stroke=POS, sw=1.4))
    frags.append(text(58, top + 60, "латентність", size=11, color=POS, anchor="start", bold=True))
    frags.append(text(58, top + 75, "наклад кадру", size=10, color=MUTED, anchor="start"))

    bar(340, 1085, 5, "UART 921600", "серіал. 1085")
    bar(490, 67, 1000, "USB Full-Speed", "серіал. 67")
    bar(640, 67, 125, "USB High-Speed", "серіал. 67")

    frags.append(line(40, 388, 740, 388, color=MUTED, sw=1))
    frags.append(text(W / 2, 412, "USB виграє пропускну (серіалізація мізерна), але кадр FS зрівнює його повну затримку з UART.",
                     size=11, color=INK, bold=True))
    frags.append(text(W / 2, 434, "High-Speed кращий для HIL не пропускною, а увосьмеро меншим кадром (125 мкс проти 1000).",
                     size=11, color=MUTED))

    render(os.path.join(IMG, 'link-comparison.svg'), W, H, *frags)


# ── Фігура (math-вставка): p — площа хвоста; середнє мовчить, керує процентиль ──
def fig_tail_probability():
    import math
    W, H = 825, 430
    frags = []
    frags.append(text(W / 2, 30, "Імовірність зриву p — це площа ХВОСТА за дедлайном", size=16, bold=True))

    x0, y0 = 70, 300
    xmax = 720
    frags.append(arrow(x0, y0, xmax + 10, y0, color=INK, sw=2))
    frags.append(text(xmax + 12, y0 + 5, "затримка такту", size=11, anchor="start", color=MUTED))
    frags.append(arrow(x0, y0, x0, 70, color=INK, sw=2))
    frags.append(text(x0 - 8, 66, "частота", size=11, anchor="end", color=MUTED))

    cx, spread, amp = 300, 70, 200
    def curve_y(xx):
        return y0 - amp * math.exp(-((xx - cx) ** 2) / (2 * spread ** 2))
    pts = [(x0 + i * 6, curve_y(x0 + i * 6)) for i in range(0, 109)]
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, NEG))

    xd = 560
    frags.append(line(xd, y0, xd, 90, color=INK, sw=2, dash="6 4"))
    frags.append(text(xd + 4, 96, "ДЕДЛАЙН", size=12, color=INK, bold=True, anchor="start"))

    tail = [(xd, y0)] + [(x, y) for (x, y) in pts if x >= xd] + [(pts[-1][0], y0)]
    dt = "M " + " L ".join("%.1f %.1f" % p for p in tail) + " Z"
    frags.append('<path d="%s" fill="#fdecea" stroke="%s" stroke-width="1.5"/>' % (dt, POS))
    frags.append(text(632, 250, "площа = p", size=12, color=POS, bold=True, anchor="middle"))
    frags.append(text(632, 268, "(зриви)", size=10, color=POS, anchor="middle"))
    frags.append(arrow(614, 256, 585, 288, color=POS, sw=1.5))

    frags.append(line(cx, y0, cx, curve_y(cx) - 6, color=MUTED, sw=1.6, dash="3 3"))
    frags.append(text(cx, y0 + 20, "середнє", size=11, color=MUTED, bold=True))
    frags.append(text(cx, y0 + 36, "про хвіст мовчить", size=10, color=MUTED))

    xp = 512
    frags.append(line(xp, y0, xp, curve_y(xp) - 6, color=FIELD, sw=1.8, dash="3 3"))
    frags.append(text(xp - 4, 150, "99.9-й", size=11, color=FIELD, bold=True, anchor="end"))
    frags.append(text(xp - 4, 166, "процентиль", size=10, color=FIELD, anchor="end"))
    frags.append(text(xp - 4, 182, "керує", size=10, color=FIELD, bold=True, anchor="end"))

    frags.append(line(40, 340, 740, 340, color=MUTED, sw=1))
    frags.append(text(W / 2, 366, "Кожен такт — випробування Бернуллі; за політ E[зривів] = N · p.",
                     size=12, color=INK, bold=True))
    frags.append(text(W / 2, 388, "N = 240 000 тактів, p = 0.001  →  240 зривів за політ — попри «прекрасне середнє».",
                     size=11, color=MUTED))
    frags.append(text(W / 2, 410, "Тому метрика лінка — 99.9-й процентиль (обмежує p), а не середнє.",
                     size=11, color=INK, italic=True))

    render(os.path.join(IMG, 'tail-probability.svg'), W, H, *frags)


# ── Фігура (math-вставка): накопичений дрейф двох годинників ──
def fig_clock_drift():
    W, H = 780, 420
    frags = []
    frags.append(text(W / 2, 30, "Зсув двох годинників росте лінійно з часом місії", size=16, bold=True))

    x0, y0 = 90, 320
    xmax = 700
    ytop = 78
    frags.append(arrow(x0, y0, xmax + 10, y0, color=INK, sw=2))
    frags.append(text(xmax + 12, y0 + 5, "час місії, с", size=11, anchor="start", color=MUTED))
    frags.append(arrow(x0, y0, x0, ytop, color=INK, sw=2))
    frags.append(text(x0 - 8, ytop - 6, "накопичений зсув", size=11, anchor="end", color=MUTED))

    def X(t): return x0 + (t / 600.0) * (xmax - x0)
    def Y(ms): return y0 - (ms / 60.0) * (y0 - ytop)

    # головна пряма: нахил 100 ppm => 60 мс за 600 с
    frags.append(line(X(0), Y(0), X(600), Y(60), color=POS, sw=3))
    frags.append(text(X(360), Y(43), "нахил = |ε_відн| = 100 ppm", size=12, color=POS, bold=True, anchor="middle"))
    frags.append(text(X(360), Y(43) + 16, "(±50 ppm плата + ±50 ppm ПК)", size=10, color=POS, anchor="middle"))

    # рівень «один такт» = 2.5 мс
    yt = Y(2.5)
    frags.append(line(x0, yt, xmax, yt, color=MUTED, sw=1.4, dash="5 4"))
    frags.append(text(xmax, yt - 6, "один такт = 2500 мкс", size=10, color=MUTED, anchor="end"))
    frags.append(circle(X(25), yt, 5, fill=BG, stroke=INK, sw=1.8))
    frags.append(line(X(25), y0, X(25), yt, color=INK, sw=1, dash="2 3"))
    frags.append(text(X(25) + 8, yt - 8, "25 с → 1 такт", size=10, color=INK, anchor="start"))

    frags.append(circle(X(600), Y(60), 5, fill=BG, stroke=POS, sw=1.8))
    frags.append(text(X(600) - 6, Y(60) - 12, "600 с → 24 такти (60 мс)", size=10, color=POS, anchor="end"))

    # пунктирна пилка — ресинхронізація тримає зсув під тактом
    saw = []
    period = 20.0
    t = 0.0
    while t <= 600:
        saw.append((X(t), Y(0)))
        saw.append((X(min(t + period, 600)), Y(1.6)))
        t += period
    ds = "M " + " L ".join("%.1f %.1f" % p for p in saw)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 3"/>' % (ds, FIELD))
    frags.append(text(X(300), Y(9), "ресинхронізація: пилкоподібне скидання тримає зсув під тактом", size=10, color=FIELD, anchor="middle"))

    frags.append(line(40, 358, 740, 358, color=MUTED, sw=1))
    frags.append(text(W / 2, 382, "Два незалежні кварци розходяться зі швидкістю |ε_плати| + |ε_ПК| — вдвічі за найгірший поодинокий.",
                     size=11, color=INK, bold=True))
    frags.append(text(W / 2, 404, "Прибрати розбіжність повністю вільний хід не може — доки годинників два (це й робить lockstep).",
                     size=11, color=MUTED))

    render(os.path.join(IMG, 'clock-drift.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_anatomy()
    fig_two_doors()
    fig_realtime()
    fig_hist_timeline()
    fig_jitter()
    fig_lockstep()
    fig_electrical_injection()
    fig_frame_layout()
    fig_seq_recovery()
    fig_throughput_latency()
    fig_link_comparison()
    fig_tail_probability()
    fig_clock_drift()
    print("figures written to", IMG)
