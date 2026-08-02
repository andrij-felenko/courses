# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: народження апарата — каскад умов від серцебиття до new Vehicle ────
# Ідея: апарат ніде не реєструється. Єдина подія, з якої він з'являється, —
# серцебиття з незнайомим номером системи. Порядок перевірок важить: спершу
# відсіюємо не-автопілоти (інакше підвіс став би «апаратом»), потім не-апарати
# за типом, потім заборону складання, і аж наприкінці — «а чи вже знайомий».
def fig_birth():
    W, H = 980, 640
    p = []

    gx, gw = 60, 420
    gates = [
        ("compid = 1 — це автопілот?",
         "ні → підвіс, камера, компаньйон:\nтелеметрію приймемо, апарата не створимо"),
        ("тип не GCS, не компаньйон,\nне підвіс, не ADSB?",
         "ні → це вузол мережі, а не апарат"),
        ("складання дозволяє кілька апаратів?",
         "ні → лишається тільки перший,\nвендорська збірка так вимкнула багатоапаратність"),
        ("sysid ще не знайомий, і він не 0?",
         "ні → апарат уже в списку,\nсерцебиття просто оновлює його стан"),
    ]

    p.append(fitbox(gx, 52, gw, 50, "HEARTBEAT з каналу: sysid = 3, compid = 1",
                    size=15, fill="#eef4ff", stroke=NEG, bold=True))

    y = 132
    prev_bottom = 102
    for title, drop in gates:
        p.append(line(gx + gw / 2, prev_bottom, gx + gw / 2, y - 6, color=LINE, sw=1.4))
        p.append(arrow(gx + gw / 2, y - 18, gx + gw / 2, y - 2))
        p.append(fitbox(gx, y, gw, 66, title, size=14))
        p.append(arrow(gx + gw + 6, y + 33, 556, y + 33, color=MUTED, sw=1.5))
        p.append(fitbox(566, y + 2, 366, 62, drop, size=12, fill="#fdf3f2",
                        stroke=POS, color="#8c2b20"))
        prev_bottom = y + 66
        y += 108

    p.append(line(gx + gw / 2, prev_bottom, gx + gw / 2, y - 6, color=LINE, sw=1.4))
    p.append(arrow(gx + gw / 2, y - 18, gx + gw / 2, y - 2))
    p.append(fitbox(gx, y, gw, 62, "new Vehicle(...) — і одразу серцебиття станції у відповідь",
                    size=14, fill="#eafaf0", stroke=FIELD, bold=True))
    p.append(fitbox(566, y + 2, 366, 58, "перший апарат стає активним,\nдругий і далі — лише повідомленням",
                    size=12, fill="#f7f8fa", stroke=MUTED, color=MUTED))

    render(os.path.join(OUT, "birth.svg"), W, H, *p,
           title="Від серцебиття до об'єкта: чотири умови поспіль")


# ── Фіг. 2: розсилка всім + фільтр на вході кожного апарата ──────────────────
# Ідея: маршрутизації як такої немає. Кожне розібране повідомлення отримують
# УСІ об'єкти Vehicle, і кожен сам порівнює sysid. Ціна — квадрат: N апаратів
# дають N·N доставок, з яких корисна одна на кожне повідомлення.
def fig_fanout():
    W, H = 990, 480
    p = []

    p.append(fitbox(40, 175, 210, 96,
                    "розібраний потік\nMAVLink\n(усі канали разом)",
                    size=14, fill="#eef4ff", stroke=NEG, bold=True))

    rows = [
        ("Vehicle sysid = 1", "1 ≠ 3 → вихід одразу", False),
        ("Vehicle sysid = 2", "2 ≠ 3 → вихід одразу", False),
        ("Vehicle sysid = 3", "3 = 3 → повний розбір", True),
        ("Vehicle sysid = 4", "4 ≠ 3 → вихід одразу", False),
    ]
    bx, bw, bh = 400, 330, 64
    ys = [66, 156, 246, 336]
    for (name, verdict, hit), y in zip(rows, ys):
        col = FIELD if hit else MUTED
        fill = "#eafaf0" if hit else "#f4f6f8"
        p.append(arrow(258, 223, bx - 8, y + bh / 2, color=col, sw=1.5))
        p.append(fitbox(bx, y, bw, bh, name + "\n" + verdict, size=13,
                        fill=fill, stroke=col, bold=hit))

    p.append(fitbox(766, 150, 194, 150,
                    "одне повідомлення —\nN доставок,\nз них N−1 марних;\nусього N·N за такт",
                    size=13, fill="#fffdf0", stroke="#b8860b", color="#7a5b06"))

    p.append(text(W / 2, 442, "простежено одне повідомлення від апарата з номером 3",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "fanout.svg"), W, H, *p,
           title="Розсилка всім, фільтр на вході")


# ── Фіг. 3: один апарат — кілька каналів; сходинка вибору головного ──────────
# Ідея: тотожність апарата — це номер, а не дріт. Той самий sysid, почутий на
# трьох каналах, лишається ОДНИМ об'єктом із трьома каналами; кожен канал має
# власний таймер тиші, а команди йдуть лише в один — головний.
def fig_links():
    W, H = 980, 560
    p = []

    links = [
        ("USB напряму", "тиша 0.2 с — живий", FIELD, "#eafaf0"),
        ("Радіо 433 МГц", "тиша 6 с — «зв'язок утрачено»", POS, "#fdf3f2"),
        ("Супутниковий канал", "висока затримка — тишу не рахують", MUTED, "#f4f6f8"),
    ]
    lx, lw, lh = 50, 320, 74
    ys = [66, 166, 266]
    for (name, note, col, fill), y in zip(links, ys):
        p.append(fitbox(lx, y, lw, lh, name + "\n" + note, size=13, stroke=col, fill=fill))
        p.append(arrow(lx + lw + 6, y + lh / 2, 592, 200, color=col, sw=1.5))

    p.append(fitbox(600, 140, 330, 120,
                    "Vehicle sysid = 3\nодин об'єкт, три канали\nголовний: USB",
                    size=14, fill="#eef4ff", stroke=NEG, bold=True))

    p.append(text(W / 2, 396, "Кого беруть за головний — у такому порядку",
                  size=15, color=INK, bold=True))
    ladder = ["USB напряму", "звичайний канал", "канал із високою затримкою"]
    sx, sw_, sh = 60, 258, 60
    for i, s in enumerate(ladder):
        x = sx + i * 296
        p.append(fitbox(x, 424, sw_, sh, s, size=13))
        if i < 2:
            p.append(arrow(x + sw_ + 6, 454, x + sw_ + 30, 454, color=MUTED, sw=1.6))

    p.append(text(W / 2, 518, "канали, на яких тиша, з розгляду випадають",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "links.svg"), W, H, *p,
           title="Один апарат, кілька каналів")


# ── Фіг. 4: дві різні «поточності» — активний (один) і вибрані (кілька) ──────
# Ідея: у застосунку живуть ДВА вказівники на «зараз». Керування прив'язане до
# єдиного активного апарата, географія — до всього списку, а групові дії — до
# окремого списку вибраних. Плутати їх — типова помилка правки QGC.
def fig_active_vs_selected():
    W, H = 990, 520
    p = []

    px, pw = 40, 440
    p.append(rect(px, 52, pw, 400, fill="#fbfdff", stroke=NEG, sw=1.6, rx=10))
    p.append(text(px + pw / 2, 84, "прив'язано до АКТИВНОГО — один", size=15,
                  color=NEG, bold=True))
    left = ["прилади й індикатори польоту", "план у режимі планування",
            "джойстик і ручне керування", "панель параметрів",
            "зліт, посадка, повернення додому"]
    for i, s in enumerate(left):
        p.append(fitbox(px + 20, 104 + i * 66, pw - 40, 52, s, size=13,
                        fill="#eef4ff", stroke=NEG))

    qx = 510
    p.append(rect(qx, 52, pw, 400, fill="#fbfdff", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(qx + pw / 2, 84, "прив'язано до ВСІХ або ВИБРАНИХ", size=15,
                  color=FIELD, bold=True))
    right = ["значок кожного апарата на карті", "місія кожного апарата на карті",
             "показ датчиків відстані", "групове зброєння й розброєння",
             "груповий старт місії й пауза"]
    for i, s in enumerate(right):
        p.append(fitbox(qx + 20, 104 + i * 66, pw - 40, 52, s, size=13,
                        fill="#eafaf0", stroke=FIELD))

    p.append(text(W / 2, 490,
                  "активний апарат — один і завжди є; вибраних може бути нуль, один чи всі",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "active-vs-selected.svg"), W, H, *p,
           title="Два різні «зараз»")


# ── Фіг. 5 (вставка proj): доставка через таблицю й три її пробоїни ─────────
# Ідея: таблиця «номер системи → об'єкт» відповідає лише на питання «кому»,
# і відповідає неповно: широкомовний нуль і доповідь модема своїм номером
# у таблиці комірок не мають. А фільтр за номером вузла живе рівнем нижче
# й лишається однаковим у обох схемах — його таблиця не замінює.
def fig_lookup_dispatch():
    W, H = 1020, 620
    p = []

    lx, lw = 60, 420
    rx, rw = 560, 420
    p.append(fitbox(lx, 44, lw, 48, "розібране повідомлення: sysid · compid · msgid",
                    size=14, fill="#eef4ff", stroke=NEG, bold=True))

    rows = [
        ("sysid == 0 ?\nджерело не назвало себе",
         "віддати ВСІМ об'єктам:\nкомірки [0] у таблиці немає,\nнаївний пошук губить пакет"),
        ("msgid == RADIO_STATUS ?\nі канал у списку цього апарата",
         "модем доповідає СВОЇМ номером\n(у SiK це sysid 51, compid 68):\nшукати за каналом, не за номером"),
        ("bySysid[sysid]\nодна індексація масиву на 256 комірок",
         "рівно один об'єкт апарата;\nпорожня комірка — відкинути"),
    ]

    y, rh = 110, 90
    for i, (cond, res) in enumerate(rows):
        fill = "#fdf3f2" if i < 2 else "#eafaf0"
        stroke = POS if i < 2 else FIELD
        p.append(fitbox(lx, y, lw, rh, cond, size=13))
        p.append(arrow(lx + lw + 8, y + rh / 2, rx - 8, y + rh / 2, color=MUTED, sw=1.6))
        p.append(text((lx + lw + rx) / 2, y + rh / 2 - 16, "так", size=12, color=MUTED))
        p.append(fitbox(rx, y, rw, rh, res, size=13, fill=fill, stroke=stroke))
        if i < 2:
            p.append(arrow(lx + lw / 2, y + rh + 6, lx + lw / 2, y + 138))
            p.append(text(lx + lw / 2 + 16, y + rh + 34, "ні", size=12,
                          color=MUTED, anchor="start"))
        y += 140

    p.append(fitbox(60, 500, 920, 84,
                    "другий рівень фільтра лишається В ОБОХ схемах:\n"
                    "усередині апарата compid != _defaultComponentId → вихід",
                    size=14, fill="#f7f7f9", stroke=INK))

    render(os.path.join(OUT, "lookup-dispatch.svg"), W, H, *p,
           title="Доставка через таблицю: три шляхи замість одного")


# ── Фіг. 6 (вставка proj): де розсилка переганяє за ціною сам розбір ────────
# Ідея: розбір пакетів росте як N (джерел стало більше), а розсилка — як N²
# (кожне з N·r повідомлень заходить у кожен із N об'єктів). Дві прямі різного
# порядку неминуче перетинаються, і точка перетину — це відношення двох
# вимірюваних сталих, а не «відчуття, що стало повільно».
def fig_lookup_crossover():
    W, H = 980, 580
    p = []

    X0, X1 = 120.0, 920.0      # N = 0 … 40
    YB, YT = 500.0, 90.0       # 0 … 7000 мкс/с
    kx = (X1 - X0) / 40.0
    ky = (YB - YT) / 7000.0

    def px(n): return X0 + n * kx
    def py(v): return YB - v * ky

    p.append(line(X0, YB, 934, YB, color=INK, sw=1.6))
    p.append(line(X0, YB, X0, 82, color=INK, sw=1.6))

    for v in (0, 2000, 4000, 6000):
        p.append(line(X0 - 8, py(v), X0, py(v), color=INK, sw=1.4))
        p.append(text(X0 - 14, py(v) + 4, str(v), size=12, color=MUTED, anchor="end"))
    for n in (0, 10, 20, 30, 40):
        p.append(line(px(n), YB, px(n), YB + 8, color=INK, sw=1.4))
        p.append(text(px(n), YB + 26, str(n), size=12, color=MUTED))

    p.append(text(X0, 70, "мікросекунд процесора на секунду роботи",
                  size=13, color=MUTED, anchor="start"))
    p.append(text(930, YB + 52, "апаратів N", size=13, color=MUTED, anchor="end"))

    steps = 80
    for i in range(steps):
        a = 40.0 * i / steps
        b = 40.0 * (i + 1) / steps
        p.append(line(px(a), py(a * 60.0), px(b), py(b * 60.0), color=NEG, sw=2.4))
        p.append(line(px(a), py(a * a * 4.0), px(b), py(b * b * 4.0), color=POS, sw=2.4))

    p.append(rect(150, 112, 360, 100, fill=BG, stroke=MUTED, sw=1.2))
    p.append(line(172, 146, 208, 146, color=POS, sw=2.6))
    p.append(text(220, 151, "розсилка всім — як N²", size=13, anchor="start"))
    p.append(line(172, 186, 208, 186, color=NEG, sw=2.6))
    p.append(text(220, 191, "розбір пакетів — як N", size=13, anchor="start"))

    p.append(line(px(15), YB, px(15), py(900) + 14, color=MUTED, sw=1.2, dash="4 4"))
    p.append(circle(px(15), py(900), 6, fill=BG, stroke=INK, sw=2))
    p.append(text(px(15), py(900) - 22, "N ≈ 15", size=14, color=INK, bold=True))

    p.append(text(W / 2, 556,
                  "числа взято за c_розбір = 600 нс, c_доставка = 40 нс, r = 100 повідомлень/с",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "lookup-crossover.svg"), W, H, *p,
           title="Дві сталі й одна точка перетину")


# ── Фіг. 7 (вставка api): порядок сигналів і вікно у 20 мс ──────────────────
# Ідея: контракт менеджера — не лише перелік сигналів, а ПОРЯДОК, у якому вони
# приходять. Обидві дії (перемикання активного, видалення апарата) розірвані
# таймером надвоє, і між половинками є такт, у якому властивості неузгоджені.
def fig_signal_order():
    W, H = 1020, 650
    p = []

    c1x, cw = 50, 385
    bx, bw = 455, 110
    c2x = 585

    p.append(text(c1x + cw / 2, 54, "ФАЗА 1 — того самого такту", size=13,
                  color=MUTED, bold=True))
    p.append(text(c2x + cw / 2, 54, "ФАЗА 2 — за 20 мс, окремим тактом", size=13,
                  color=MUTED, bold=True))

    def band(y, h, cy):
        p.append(rect(bx, y, bw, h, fill="#f7f8fa", stroke=MUTED, sw=1.2, rx=10))
        p.append(mtext(bx + bw / 2, cy - 10, ["+20 мс", "оберт", "циклу подій"],
                       size=12, color=MUTED, bold=True))
        p.append(arrow(c1x + cw + 6, cy + 46, bx - 4, cy + 46, color=MUTED, sw=1.6))
        p.append(arrow(bx + bw + 4, cy + 46, c2x - 6, cy + 46, color=MUTED, sw=1.6))

    SIG = dict(size=12, fill="#eef4ff", stroke=NEG)
    TRAP = dict(size=12, fill="#fdf3f2", stroke=POS, color="#8c2b20")

    # ── лава 1: перемикання активного апарата ────────────────────────────────
    p.append(text(c1x, 86, "① Перемикання активного апарата: A → B", size=14,
                  color=NEG, anchor="start", bold=True))
    band(96, 190, 191)

    p.append(fitbox(c1x, 100, cw, 52, "1 · activeVehicleAvailableChanged(false)", **SIG))
    p.append(fitbox(c1x, 160, cw, 52, "2 · parameterReadyVehicleAvailableChanged(false)", **SIG))
    p.append(fitbox(c1x, 220, cw, 56,
                    "activeVehicle досі вказує на A —\nсама властивість ще не змінилася", **TRAP))

    p.append(fitbox(c2x, 100, cw, 52, "3 · activeVehicleChanged(B)", **SIG))
    p.append(fitbox(c2x, 160, cw, 52, "4 · activeVehicleAvailableChanged(true)", **SIG))
    p.append(fitbox(c2x, 220, cw, 56,
                    "5 · parameterReadyVehicleAvailableChanged(true)\nлише якщо параметри B уже завантажені", **SIG))

    # ── лава 2: видалення апарата ────────────────────────────────────────────
    p.append(text(c1x, 324, "② Видалення апарата V (за сигналом allLinksRemoved)",
                  size=14, color=NEG, anchor="start", bold=True))
    band(334, 248, 458)

    p.append(fitbox(c1x, 338, cw, 52, "1 · V зникає зі списку vehicles", **SIG))
    p.append(fitbox(c1x, 398, cw, 52, "2 · V зникає зі списку selectedVehicles", **SIG))
    p.append(fitbox(c1x, 458, cw, 60,
                    "3 · activeVehicleAvailableChanged(false)\nparameterReadyVehicleAvailableChanged(false)", **SIG))
    p.append(fitbox(c1x, 526, cw, 52, "4 · vehicleRemoved(V) — V ще живий", **SIG))

    p.append(fitbox(c2x, 338, cw, 52, "5 · activeVehicleChanged(vehicles[0] або nullptr)", **SIG))
    p.append(fitbox(c2x, 398, cw, 52, "6 · availability знову true, якщо активний є", **SIG))
    p.append(fitbox(c2x, 458, cw, 52, "7 · V->deleteLater()", **SIG))
    p.append(fitbox(c2x, 518, cw, 60,
                    "від цієї миті кожен збережений Vehicle*\nна V стає висячим", **TRAP))

    p.append(text(W / 2, 616,
                  "прапорці доступності падають у фазі 1 незалежно від того, "
                  "чи зникає саме активний апарат",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "signal-order.svg"), W, H, *p,
           title="Дві фази, розірвані таймером")


fig_birth()
fig_fanout()
fig_links()
fig_active_vs_selected()
fig_lookup_dispatch()
fig_lookup_crossover()
fig_signal_order()
print("ok")
