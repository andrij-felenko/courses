# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори ролей
PUB, PUBF = "#1a5276", "#d6eaf8"    # видавець / дані
NODEC, NODEF = "#7d3c98", "#f0e6fa"  # вузол теми
SUBC, SUBF = "#1e8449", "#eafaf0"    # передплатник
WARN, WARNF = "#c0392b", "#fdecea"   # втрата / заборона
AMB, AMBF = "#b9770e", "#fdf3d6"     # черга робіт / повільна гілка


# ── uorb-node: вузол теми, лічильник поколінь і три читачі ───────────────────
# Ідея: спільної черги на читача немає. Є один буфер і одне число (покоління)
# у вузла; кожен читач тримає власне число. Різниця = скільки нового або
# скільки безповоротно проґавлено.

def fig_uorb_node():
    W, H = 1010, 526
    p = []

    # ── видавець ──
    p.append(rect(40, 150, 190, 80, fill=PUBF, stroke=PUB, sw=2.0))
    p.append(mtext(135, 182, ["драйвер або оцінювач", "єдиний видавець"], size=11.5, color=PUB, bold=True))

    # стрілка публікації
    p.append(arrow(232, 190, 346, 190, color=PUB, sw=1.8))
    p.append(text(289, 176, "публікація", size=10.5, color=PUB))

    # ── вузол теми ──
    nx, ny, nw, nh = 350, 86, 330, 250
    p.append(rect(nx, ny, nw, nh, fill="#ffffff", stroke=NODEC, sw=2.2))
    p.append(text(nx + nw / 2, ny + 26, "вузол теми  vehicle_attitude", size=12.5, color=NODEC, bold=True))
    p.append(fitbox(nx + 22, ny + 46, nw - 44, 58,
                    "буфер сталого розміру\nодне останнє повідомлення",
                    size=11, fill=PUBF, stroke=PUB, sw=1.4))
    p.append(fitbox(nx + 22, ny + 120, nw - 44, 50,
                    "_generation = 1042",
                    size=13, bold=True, fill=NODEF, stroke=NODEC, sw=1.4))
    p.append(fitbox(nx + 22, ny + 186, nw - 44, 46,
                    "список зворотних викликів",
                    size=11, fill="#f4f6f8", stroke=MUTED, sw=1.2))

    # ── три передплатники ──
    sx, sw_ = 730, 250
    readers = [
        (128, SUBC, SUBF, "регулятор  ·  своє = 1041", "різниця 1 — одне нове повідомлення"),
        (204, WARN, WARNF, "логер  ·  своє = 1037", "різниця 5 при глибині 1 — чотири втрачено"),
        (280, MUTED, "#f4f6f8", "телеметрія  ·  своє = 1042", "різниця 0 — нового немає"),
    ]
    for cy, col, fill, l1, l2 in readers:
        p.append(arrow(nx + nw, cy, sx - 8, cy, color=col, sw=1.6))
        p.append(rect(sx, cy - 32, sw_, 64, fill=fill, stroke=col, sw=1.8))
        p.append(text(sx + sw_ / 2, cy - 6, l1, size=11.5, color=col, bold=True))
        p.append(text(sx + sw_ / 2, cy + 16, l2, size=10, color=INK))

    # ── правило внизу ──
    p.append(rect(40, 372, W - 80, 96, fill="#fbfcfd", stroke=NODEC, sw=1.8))
    p.append(text(W / 2, 400, "різниця  =  _generation вузла  −  власне покоління читача",
                  size=13, color=NODEC, bold=True))
    p.append(text(W / 2, 428, "читання не блокує видавця й не має підтверджень: замість гарантії доставки читач дістає точне число пропущеного",
                  size=11, color=INK))
    p.append(text(W / 2, 452, "різниця більша за глибину черги  →  найстаріші повідомлення вже перезаписано",
                  size=11, color=WARN))

    p.append(text(W / 2, H - 14,
                  "Вартість публікації не залежить від кількості читачів — тому її можна робити навіть із переривання",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "uorb-node.svg"), W, H, *p,
           title="Вузол теми uORB: один буфер, одне число, різні читачі")


# ── module-execution: задача проти робочого елемента ─────────────────────────
# Ідея: два способи оживити модуль розрізняються рівно однією річчю — власним
# стеком. Він дає право блокуватися і коштує пам'ять; його відсутність дає
# дешевизну і забороняє блокуватися.

def fig_module_execution():
    W, H = 960, 486
    p = []
    py, ph = 60, 258
    cols = [
        (36, 420, PUB, PUBF, "Задача (task)", "власний потік · власний стек · власний пріоритет",
         "while (!should_exit) {\n    px4_poll(fds, 1, 1000);  // чекає на теми\n    ...\n}",
         [("✓", "може спати, чекати, писати у файл", "#186a3b"),
          ("₽", "коштує кілька кілобайтів RAM під стек", "#7a5200"),
          ("→", "navigator · logger · mavlink", MUTED)]),
        (504, 420, AMB, AMBF, "Робочий елемент (work item)", "спільний потік черги · спільний стек · пріоритет черги",
         "void Run() override {\n    // registerCallback() або\n    // ScheduleOnInterval(2500_us)\n}",
         [("✗", "блокуватися не можна — стануть усі сусіди", WARN),
          ("₽", "коштує майже нічого понад свої дані", "#186a3b"),
          ("→", "mc_rate_control · control_allocator · драйвери", MUTED)]),
    ]
    for x, w, col, fill, head, sub, code, bullets in cols:
        p.append(rect(x, py, w, ph, fill="#ffffff", stroke=col, sw=2.2))
        p.append(text(x + w / 2, py + 30, head, size=14, color=col, bold=True))
        p.append(text(x + w / 2, py + 52, sub, size=10.5, color=MUTED))
        p.append(fitbox(x + 22, py + 68, w - 44, 76, code, size=10, pad=10,
                        fill=fill, stroke=col, sw=1.4))
        yy = py + 172
        for mark, txt, mcol in bullets:
            p.append(text(x + 26, yy, mark, size=13, color=mcol, anchor="start", bold=True))
            p.append(text(x + 50, yy, txt, size=11, color=INK, anchor="start"))
            yy += 30

    p.append(rect(36, 348, W - 72, 66, fill="#f7f9fb", stroke=MUTED, sw=1.6))
    p.append(text(W / 2, 374, "Черг робіт багато, і кожна — окремий потік зі своїм пріоритетом:",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 398, "wq:SPI0…SPI6  ·  wq:I2C0…I2C4  ·  wq:rate_ctrl  ·  wq:nav_and_controllers  ·  wq:hp_default  ·  wq:lp_default",
                  size=11, color=AMB))

    p.append(text(W / 2, H - 14,
                  "Вибір черги — це і є призначення пріоритету: він вирішує, хто кого витіснить",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "module-execution.svg"), W, H, *p,
           title="Два способи виконання модуля")


# ── control-chain: шлях від гіроскопа до мотора, ведений даними ──────────────
# Ідея: жоден крок не має власного таймера — кожен будить публікація
# попереднього. Тому частота контуру дорівнює частоті вибірки гіроскопа.

def fig_control_chain():
    W, H = 980, 700
    p = []
    bx, bw, bh, pitch = 268, 420, 66, 96
    top = 92

    steps = [
        ("драйвер інерціального блока", "публікує  sensor_gyro_fifo", "wq:SPI1", "вичитує FIFO ~1 кГц", PUB, PUBF),
        ("VehicleAngularVelocity", "публікує  vehicle_angular_velocity", "wq:rate_ctrl", "калібрування й фільтри", NODEC, NODEF),
        ("mc_rate_control", "публікує  vehicle_torque_setpoint", "wq:rate_ctrl", "ПІД по трьох осях", NODEC, NODEF),
        ("control_allocator", "публікує  actuator_motors", "wq:rate_ctrl", "матриця ефективності рами", NODEC, NODEF),
        ("драйвер виходів PWM / DShot", "імпульси на регулятори обертів", "—", "PWM_MAIN_FUNCx", SUBC, SUBF),
    ]
    for i, (name, topic, wq, note, col, fill) in enumerate(steps):
        y = top + i * pitch
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=col, sw=2.0))
        p.append(text(bx + bw / 2, y + 27, name, size=12.5, color=col, bold=True))
        p.append(text(bx + bw / 2, y + 48, topic, size=10.5, color=INK))
        # ліва колонка — черга робіт
        p.append(text(bx - 30, y + 32, wq, size=11.5, color=AMB, anchor="end", bold=True))
        # права колонка — що робить
        p.append(text(bx + bw + 30, y + 32, note, size=10.5, color=MUTED, anchor="start"))
        if i < len(steps) - 1:
            p.append(arrow(bx + bw / 2, y + bh + 4, bx + bw / 2, y + pitch - 4, color=col, sw=1.8))

    p.append(text(bx + bw / 2 + 118, top + bh + 22, "публікація будить наступного",
                  size=10, color=MUTED, anchor="start"))

    yb = top + len(steps) * pitch - (pitch - bh) + 22
    p.append(rect(120, yb, W - 240, 86, fill="#fbfcfd", stroke=NODEC, sw=1.8))
    p.append(text(W / 2, yb + 28, "Жоден крок не запускається за власним таймером",
                  size=13, color=NODEC, bold=True))
    p.append(text(W / 2, yb + 52, "такт задає вибірка гіроскопа — тому дві незалежні частоти не «б'ються»",
                  size=11, color=INK))
    p.append(text(W / 2, yb + 74, "і вік даних на вході регулятора не гуляє від нуля до цілого періоду",
                  size=11, color=INK))

    p.append(text(W / 2, H - 14,
                  "Повільна гілка — оцінювач, регулятор положення, навігатор — живиться тими самими темами, лише рідше",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "control-chain.svg"), W, H, *p,
           title="Від гіроскопа до мотора: ланцюг, який ведуть дані")


# ── mode-wiring: три режими як три джерела уставки для одного каскаду ────────
# Ідея: код регуляторів у трьох режимах той самий. Різниця лише в тому, які
# прапорці підняті у vehicle_control_mode і хто публікує уставку.

def fig_mode_wiring():
    W, H = 1000, 590
    p = []
    cw = 280
    xs = [40, 360, 680]
    modes = [
        ("Стабілізований", PUB, PUBF,
         "manual_control_setpoint",
         "нахил стика  =  нахил апарата",
         ["rates ✓", "attitude ✓", "position ✗"]),
        ("Позиційний", SUBC, SUBF,
         "mc_pos_control",
         "стик  =  бажана швидкість",
         ["rates ✓", "attitude ✓", "position ✓"]),
        ("Місія", AMB, AMBF,
         "navigator → mc_pos_control",
         "position_setpoint_triplet",
         ["rates ✓", "attitude ✓", "position ✓"]),
    ]
    for x, (name, col, fill, src, note, flags) in zip(xs, modes):
        p.append(fitbox(x, 60, cw, 44, name, size=14, bold=True, color=col, fill=fill, stroke=col, sw=2.0))
        p.append(rect(x, 122, cw, 76, fill="#ffffff", stroke=col, sw=1.8))
        p.append(text(x + cw / 2, 150, "джерело уставки", size=10, color=MUTED))
        p.append(text(x + cw / 2, 172, src, size=11.5, color=col, bold=True))
        p.append(text(x + cw / 2, 190, note, size=10, color=INK))
        yy = 232
        for f in flags:
            fc = WARN if f.endswith("✗") else "#186a3b"
            p.append(text(x + cw / 2, yy, "vehicle_control_mode:  " + f, size=11, color=fc))
            yy += 24
        p.append(arrow(x + cw / 2, 312, x + cw / 2, 356, color=col, sw=1.8))

    p.append(rect(40, 360, W - 80, 92, fill=NODEF, stroke=NODEC, sw=2.2))
    p.append(text(W / 2, 390, "Спільний каскад — той самий код у всіх трьох режимах",
                  size=13, color=NODEC, bold=True))
    p.append(text(W / 2, 416, "mc_att_control  →  mc_rate_control  →  control_allocator  →  драйвер виходів",
                  size=12, color=INK))
    p.append(text(W / 2, 438, "кожен регулятор сам дивиться на свій прапорець і мовчить, коли його знято",
                  size=10.5, color=MUTED))

    p.append(rect(140, 478, W - 280, 62, fill="#fbfcfd", stroke=MUTED, sw=1.6))
    p.append(text(W / 2, 502, "Перемикання режиму — це зміна одного числа в темі vehicle_status",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 526, "ані коду переходу, ані розмотування стека: перехід триває один період найшвидшого контуру",
                  size=10.5, color=MUTED))

    p.append(text(W / 2, H - 14,
                  "Failsafe користується тим самим механізмом: командер просто вибирає режим замість пілота",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "mode-wiring.svg"), W, H, *p,
           title="Режим — це розкладка тем, а не окремий клас")


# ── px4-timeline: від студентського змагання до апстріму NuttX ───────────────
# Ідея вставки-історії: PX4 виріс не з проєкту «зробимо автопілот», а з потреби
# пролетіти приміщення на машинному зорі — і з чотирьох переписувань поспіль.

def fig_px4_timeline():
    W, H = 960, 700
    p = []
    spine = 262
    rows = [
        ("2008", PUB, "ETH Zurich: дослідницький проєкт PIXHAWK",
         "Лоренц Маєр збирає 14 студентів під європейське змагання мікроапаратів"),
        ("2009", PUB, "EMAV: перше місце в категорії внутрішньої автономії",
         "перші, хто обійшов перешкоди машинним зором на борту, а не з наземного комп'ютера"),
        ("2011", WARN, "архітектуру визнано безнадійною — переписування з нуля",
         "три попередні покоління політного ПЗ відкинуто; четверте й дало PX4"),
        ("2012", NODEC, "код відкрито: перший публічний реліз PX4",
         "репозиторій на GitHub створено 4 серпня 2012; uORB уже всередині"),
        ("2013", SUBC, "FMUv2 під іменем Pixhawk, серійне виробництво в 3D Robotics",
         "плата стає доступною поза лабораторією — звідси й пізніші стандарти Pixhawk"),
        ("2014", SUBC, "Dronecode: фонд під Linux Foundation",
         "торгові марки й врядування виходять з-під однієї компанії; ліцензія коду — BSD 3-clause"),
        ("2015", NODEC, "ICRA 2015, с. 6235–6240: модель опубліковано як наукову роботу",
         "Meier, Honegger, Pollefeys — вимірювання затримок і опис брокера"),
        ("2022", AMB, "uORB з'являється в апстрімі Apache NuttX",
         "apps/system/uorb — C-інтерфейси з прямим посиланням на документацію PX4"),
    ]
    p.append(line(spine, 62, spine, 62 + (len(rows) - 1) * 74 + 20, color=MUTED, sw=2.0))
    for i, (year, col, head, note) in enumerate(rows):
        y = 82 + i * 74
        p.append(text(spine - 34, y + 5, year, size=15, color=col, anchor="end", bold=True))
        p.append(circle(spine, y, 7, fill="#ffffff", stroke=col, sw=2.4))
        p.append(rect(spine + 22, y - 28, 660, 58, fill="#ffffff", stroke=col, sw=1.6))
        p.append(text(spine + 40, y - 5, head, size=11.5, color=col, anchor="start", bold=True))
        p.append(text(spine + 40, y + 16, note, size=10, color=INK, anchor="start"))

    p.append(text(W / 2, H - 44,
                  "Жоден рядок тут не є заслугою однієї людини: ім'я в копірайті коду — «PX4 Development Team»",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, H - 20,
                  "Дати 2008–2015 — за власною розповіддю учасників; 2012 і 2022 звірено з історією репозиторіїв",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "px4-timeline.svg"), W, H,
           *p, title="Як PX4 дійшов від студентського змагання до апстріму NuttX")


# ── orb-lineage: звідки в назві uORB узялися три літери ORB ──────────────────
# Ідея: успадковано саме СЛОВО й одну думку (іменований посередник між
# незнайомими сторонами), а майже вся машинерія CORBA свідомо викинута.

def fig_orb_lineage():
    W, H = 1060, 560
    p = []
    boxes = [
        (30, PUB, PUBF, "CORBA · OMG, від 1991",
         "«брокер об'єктних запитів»:\nклієнт кличе метод об'єкта,\nне знаючи, де той живе"),
        (290, NODEC, NODEF, "ORB як загальне слово",
         "у робототехніці ним описують\nі легкі шини — наприклад LCM\n(Huang, Olson, Moore, 2010)"),
        (550, NODEC, NODEF, "mORB · проза статті 2015",
         "«micro object request broker»:\nтой самий задум, урізаний\nдо мікроконтролера"),
        (810, SUBC, SUBF, "uORB · код і фігури",
         "у заголовку файлу —\n«lightweight object broker»;\nсаме ця назва й прижилася"),
    ]
    for x, col, fill, head, body in boxes:
        p.append(rect(x, 56, 220, 150, fill="#ffffff", stroke=col, sw=2.0))
        p.append(fitbox(x + 12, 66, 196, 36, head, size=11.5, bold=True, color=col, fill=fill, stroke=col, sw=1.2))
        p.append(mtext(x + 110, 128, body, size=10.5, color=INK, lh=1.45))
    for x in (250, 510, 770):
        p.append(arrow(x, 131, x + 40, 131, color=MUTED, sw=1.6))

    p.append(rect(30, 244, 500, 240, fill="#ffffff", stroke=SUBC, sw=2.0))
    p.append(text(280, 274, "Що з тієї лінії взяли", size=13, color=SUBC, bold=True))
    keep = ["іменований посередник між сторонами,", "які не знають одна одну на ім'я",
            "тема як семантичний канал: «attitude», «position»", "єдиний невеликий API замість чужих заголовків",
            "видавець оголошує тему, читачі підписуються"]
    for i, s in enumerate(keep):
        p.append(text(52, 306 + i * 32, "· " + s, size=11, color=INK, anchor="start"))

    p.append(rect(560, 244, 470, 240, fill="#ffffff", stroke=WARN, sw=2.0))
    p.append(text(795, 274, "Що викинули без жалю", size=13, color=WARN, bold=True))
    drop = ["мережеву прозорість і заглушки з IDL", "динамічний пошук служби за іменем у мережі",
            "синхронний виклик методу з відповіддю", "будь-які гарантії доставки й порядку",
            "динамічну пам'ять у роботі шини"]
    for i, s in enumerate(drop):
        p.append(text(582, 306 + i * 32, "· " + s, size=11, color=INK, anchor="start"))

    p.append(text(W / 2, H - 22,
                  "Від CORBA лишилася думка, а не машинерія: буфер на тему, лічильник публікацій — і жодного посередника в мережі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "orb-lineage.svg"), W, H, *p,
           title="Родовід назви uORB: від брокера об'єктних запитів до буфера на тему")


# ── api-wrapper-choice: яку C++-обгортку взяти ───────────────────────────────
# Ідея: вибір обгортки — не питання смаку. Ліворуч його вирішує кількість
# екземплярів теми, праворуч — те, ЩО саме будить модуль. Усі шість класів
# однаково тонкі: дескриптор плюс власне покоління.

def fig_api_wrapper_choice():
    W, H = 1180, 668
    p = []

    CW, KW = 228, 246          # ширина рамки-умови та рамки-класу
    LX, RX = 50, 620           # ліва межа кожної колонки

    # ── шапки колонок ──
    p.append(fitbox(LX, 56, 510, 46,
                    "ПУБЛІКУЮ  —  вирішує кількість екземплярів теми",
                    size=13, bold=True, color=PUB, fill=PUBF, stroke=PUB, sw=2.0))
    p.append(fitbox(RX, 56, 510, 46,
                    "ЧИТАЮ  —  вирішує те, що будить мій модуль",
                    size=13, bold=True, color=SUBC, fill=SUBF, stroke=SUBC, sw=2.0))

    def row(x0, y, cond, cls, api, col, fill):
        p.append(fitbox(x0, y, CW, 84, cond, size=11.5, color=INK, fill="#ffffff",
                        stroke=col, sw=1.6))
        p.append(arrow(x0 + CW + 4, y + 42, x0 + CW + 32, y + 42, color=col, sw=1.7))
        p.append(fitbox(x0 + CW + 36, y, KW, 84, cls + "\n" + api,
                        size=11.5, bold=False, color=col, fill=fill, stroke=col, sw=1.8))

    # ── ліва колонка: публікація ──
    row(LX, 126,
        "тема одна на всю систему\n(регулятор, оцінювач, командер)",
        "Publication<T>", "publish(data)", PUB, PUBF)
    row(LX, 236,
        "по екземпляру на пристрій\nчи на примірник фільтра",
        "PublicationMulti<T>", "publish(data) · get_instance()", PUB, PUBF)

    # підказка під лівою колонкою
    p.append(fitbox(LX, 346, 510, 84,
                    "Обидві оголошують тему ліниво — при першій публікації.\n"
                    "Номер екземпляра видає сама шина, задати його наперед не можна.",
                    size=11.5, color=INK, fill="#fbfcfd", stroke=MUTED, sw=1.4))

    # ── права колонка: читання ──
    row(RX, 126,
        "модуль має прокидатися\nсаме від цієї теми",
        "SubscriptionCallbackWorkItem", "будить чергу робіт на публікації", SUBC, SUBF)
    row(RX, 236,
        "тема часта, а мені досить\nраз на N мілісекунд",
        "SubscriptionInterval", "updated() бреше до кінця інтервалу", SUBC, SUBF)
    row(RX, 346,
        "треба обійти всі екземпляри\n(усі гіроскопи, усі баро)",
        "SubscriptionMultiArray<T>", "цикл range-for по масиву", SUBC, SUBF)
    row(RX, 456,
        "просто дочитати найсвіжіше\nу власному такті",
        "Subscription", "updated() · copy() · update()", SUBC, SUBF)

    # ── нижня смуга ──
    p.append(rect(LX, 566, W - 2 * LX, 62, fill="#ffffff", stroke=NODEC, sw=1.8))
    p.append(text(W / 2, 592,
                  "усі шість — тонкі обгортки над тим самим C-API: дескриптор плюс власне покоління",
                  size=12.5, color=NODEC, bold=True))
    p.append(text(W / 2, 614,
                  "жодна не додає буфера й не змінює семантики втрат — вибір впливає лише на те, коли ти прокидаєшся",
                  size=11, color=INK))

    p.append(text(W / 2, H - 12,
                  "Помилковий вибір не дає ні помилки компіляції, ні попередження — лише гірші числа в польоті",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "api-wrapper-choice.svg"), W, H, *p,
           title="Вибір C++-обгортки uORB: ліворуч вирішують екземпляри, праворуч — джерело пробудження")


# ── loop-watch-clocks: що саме міряє сторож швидкого контуру ─────────────────
# Ідея: три величини, які видно лише з місця споживача — інтервал між власними
# пробудженнями, вік даних у мить обчислення і розрив поколінь, коли два
# пробудження злилися в одне.

def fig_loop_watch_clocks():
    W, H = 1140, 710
    p = []

    PUB_Y, RUN_Y = 150, 332

    # ── лівий жолоб: підписи доріжок ──
    p.append(fitbox(60, 118, 170, 64, "публікації\nvehicle_angular_velocity",
                    size=11, fill=PUBF, stroke=PUB, sw=1.6, color=PUB, bold=True))
    p.append(fitbox(60, 300, 170, 64, "Run() сторожа\nна черзі wq:rate_ctrl",
                    size=11, fill=SUBF, stroke=SUBC, sw=1.6, color=SUBC, bold=True))

    # ── осі часу ──
    p.append(line(250, PUB_Y, 1100, PUB_Y, color=MUTED, sw=1.2))
    p.append(line(250, RUN_Y, 1100, RUN_Y, color=MUTED, sw=1.2))

    # ── публікації ──
    pubs = [(300, "1041", False), (470, "1042", False), (640, "1043", True),
            (810, "1044", False), (980, "1045", False)]
    for px, gen, lost in pubs:
        col, fil = (WARN, WARNF) if lost else (PUB, PUBF)
        p.append(circle(px, PUB_Y, 8, fill=fil, stroke=col, sw=2.0))
        p.append(text(px, 126, "покоління " + gen, size=10.5, color=col, bold=lost))

    # ── позначка вибірки гіроскопа для другого циклу ──
    SAMP_X = 405
    p.append(line(SAMP_X, PUB_Y, SAMP_X, 520, color=NODEC, sw=1.2, dash="4 5"))
    p.append(circle(SAMP_X, PUB_Y, 5, fill="#ffffff", stroke=NODEC, sw=1.8))
    p.append(text(SAMP_X, 548, "timestamp_sample", size=10, color=NODEC))

    # ── пробудження ──
    runs = [(340, "1041", False), (510, "1042", False),
            (850, "1044", True), (1020, "1045", False)]
    for rx, gen, bad in runs:
        col, fil = (WARN, WARNF) if bad else (SUBC, SUBF)
        p.append(rect(rx - 34, RUN_Y - 16, 68, 32, fill=fil, stroke=col, sw=1.8))
        p.append(text(rx, RUN_Y + 5, "Run()", size=11, color=col, bold=True))
        p.append(text(rx, 372, "прочитано " + gen, size=10.5, color=col, bold=bad))

    # ── стрілки «публікація розбудила Run» ──
    for px, rx in ((300, 340), (470, 510), (810, 850), (980, 1020)):
        p.append(arrow(px, PUB_Y + 12, rx - 12, RUN_Y - 20, color=SUBC, sw=1.5))

    # ── втрачене покоління ──
    p.append(arrow(640, PUB_Y + 12, 640, 201, color=WARN, sw=1.6))
    p.append(fitbox(530, 205, 260, 70,
                    "потік черги зайнятий сусідом:\nдві публікації дали одне пробудження,\n1043 перезаписано в буфері глибиною 1",
                    size=10, fill=WARNF, stroke=WARN, sw=1.6, color=WARN))

    # ── три виміряні проміжки ──
    p.append(line(340, 430, 510, 430, color=SUBC, sw=2.4))
    p.append(line(340, 422, 340, 438, color=SUBC, sw=2.0))
    p.append(line(510, 422, 510, 438, color=SUBC, sw=2.0))
    p.append(text(470, 418, "А · 1000 мкс", size=10.5, color=SUBC, bold=True))

    p.append(line(510, 475, 850, 475, color=AMB, sw=2.4))
    p.append(line(510, 467, 510, 483, color=AMB, sw=2.0))
    p.append(line(850, 467, 850, 483, color=AMB, sw=2.0))
    p.append(text(680, 463, "Б · 2000 мкс", size=10.5, color=AMB, bold=True))

    p.append(line(SAMP_X, 520, 510, 520, color=NODEC, sw=2.4))
    p.append(line(SAMP_X, 512, SAMP_X, 528, color=NODEC, sw=2.0))
    p.append(line(510, 512, 510, 528, color=NODEC, sw=2.0))
    p.append(text(450, 508, "В · ≈380 мкс", size=10.5, color=NODEC, bold=True))

    # ── легенда ──
    p.append(rect(60, 570, 1020, 120, fill="#fbfcfd", stroke=MUTED, sw=1.4))
    rows = [
        (SUBC, "А — інтервал між власними пробудженнями: now − _last_run; у нормі дорівнює періоду публікації."),
        (AMB,  "Б — той самий інтервал, коли два пробудження злилися в одне: 2000 мкс замість 1000."),
        (NODEC, "В — вік даних у мить обчислення: now − av.timestamp_sample, а не «дані щойно прийшли»."),
        (WARN, "✕ — розрив поколінь: get_last_generation() − _last_generation = 2, одне повідомлення втрачено назавжди."),
    ]
    for i, (col, s) in enumerate(rows):
        y = 598 + i * 24
        p.append(rect(72, y - 10, 12, 12, fill=col, stroke=col, sw=1.0, rx=2))
        p.append(text(96, y, s, size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "loop-watch-clocks.svg"), W, H, *p,
           title="Три величини, які сторож міряє в одному пробудженні")


if __name__ == "__main__":
    fig_uorb_node()
    fig_module_execution()
    fig_control_chain()
    fig_mode_wiring()
    fig_px4_timeline()
    fig_orb_lineage()
    fig_api_wrapper_choice()
    fig_loop_watch_clocks()
    print("OK: figures written to", OUT)
