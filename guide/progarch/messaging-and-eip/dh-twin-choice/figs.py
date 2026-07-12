# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір твіна»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREENF = "#eafaf0"   # актор / гарячий шлях — зелене поле
GREYF  = "#eef0f3"   # холодний хвіст / приглушене
BLUEF  = "#eef3fd"   # довговічне джерело правди
AMBERF = "#fdf3e6"   # append-only журнал


def fig_composition():
    """Композиція твіна: актор-шар з'єднань + шардована БД + журнал аудиту."""
    W, H = 1220, 580
    frags = []

    # ── три зони-сховища ───────────────────────────────────────────────────
    # Актор-шар (гарячий, зелений)
    frags.append(fitbox(330, 140, 300, 116,
        "АКТОР-ШАР З'ЄДНАНЬ\nжива сесія під'єднаного дому\nгарячий шлях · read-your-writes\nкеш+координатор над рядком БД",
        size=13, fill=GREENF, stroke=FIELD, bold=False))
    frags.append(text(480, 130, "тільки доми «на зв'язку»", size=11.5, color=MUTED, italic=True))

    # Шардована БД (джерело правди, синій, наголошена товщою рамкою)
    frags.append(fitbox(720, 140, 340, 116,
        "ШАРДОВАНА БД\nрядок твіна на home_id · УСІ доми\nдовговічне джерело правди\nпереживає рестарт вузла",
        size=13, fill=BLUEF, stroke=NEG, sw=2.4))
    frags.append(text(890, 130, "джерело правди", size=11.5, color=NEG, italic=True, bold=True))

    # Журнал аудиту (append-only, бурштиновий)
    frags.append(fitbox(720, 410, 340, 110,
        "ЖУРНАЛ АУДИТУ\nзамки й доступ · append-only\n«хто й коли відмикав»\nвузька скибка, де історія = продукт",
        size=13, fill=AMBERF, stroke=POS))

    # ── входи (ліворуч) ────────────────────────────────────────────────────
    frags.append(fitbox(70, 150, 210, 76,
        "команда «замкни двері»\n+ тепле читання\n«покажи мій дім»", size=12, fill=FILL, stroke=LINE))
    frags.append(fitbox(70, 300, 210, 70,
        "холодне читання\nдім не на зв'язку", size=12, fill=GREYF, stroke=MUTED, color=MUTED))
    frags.append(fitbox(70, 440, 210, 70,
        "«хто відмикав\nо 3:00?» — підтримка", size=12, fill=FILL, stroke=LINE))

    # ── стрілки потоку ─────────────────────────────────────────────────────
    # вхід1 → актор
    frags.append(arrow(280, 188, 330, 188, color=INK))
    # актор → БД (пише рядок)
    frags.append(arrow(630, 176, 720, 176, color=INK))
    frags.append(text(675, 166, "пише рядок", size=11.5, color=MUTED))
    # актор → журнал (дописує подію)
    frags.append(arrow(470, 256, 762, 408, color=POS, sw=1.7))
    frags.append(text(560, 356, "дописує", size=11.5, color=POS))
    frags.append(text(560, 372, "подію замка", size=11.5, color=POS))
    # холодне читання → БД (повз актор, пунктир)
    frags.append(arrow(280, 332, 720, 246, color=MUTED, sw=1.6))
    frags.append(text(430, 276, "по ключу home_id, повз актор", size=11, color=MUTED, italic=True))
    # історія → журнал
    frags.append(arrow(280, 470, 720, 462, color=INK))

    # ── нижнє правило маршрутизації ────────────────────────────────────────
    frags.append(line(70, 542, 1150, 542, color=MUTED, sw=1, dash="3,5"))
    frags.append(text(610, 566,
        "Не «один варіант на все»: гарячий стан — в актора, довговічна правда — у шард БД, "
        "а сама історія «що коли ставалось» — у вузький журнал.",
        size=12.5, color=INK))

    render(os.path.join(IMG, "twin-composition.svg"), W, H, *frags,
           title="Твін — не одне сховище, а три ролі даних")


def fig_access_profile():
    """Профіль доступу: малий гарячий набір на зв'язку проти великого холодного хвоста."""
    W, H = 1120, 470
    frags = []

    # верхня примітка — асиметрія доступу
    frags.append(fitbox(60, 66, 1000, 46,
        "профіль доступу: читань «покажи мій дім» — десятки тисяч/с ≫ записів; "
        "ключ усюди — home_id (природний шард)",
        size=13, fill=FILL, stroke=LINE))

    # смуга «усі ~пів мільйона домів», поділена на гарячий і холодний сегменти
    BX, BY, BW, BH = 90, 190, 940, 74
    hot_w = 200
    # гарячий сегмент (малий, зелений)
    frags.append(rect(BX, BY, hot_w, BH, fill=GREENF, stroke=FIELD, sw=2, rx=0))
    frags.append(mtext(BX + hot_w / 2, BY + BH / 2 - 4,
        ["на зв'язку зараз", "десятки тисяч"], size=12.5, color=INK, lh=1.25))
    # холодний сегмент (великий, сірий)
    frags.append(rect(BX + hot_w, BY, BW - hot_w, BH, fill=GREYF, stroke=MUTED, sw=2, rx=0))
    frags.append(mtext(BX + hot_w + (BW - hot_w) / 2, BY + BH / 2 - 4,
        ["офлайн / сплять", "сотні тисяч — довгий холодний хвіст"], size=12.5, color=MUTED, lh=1.25))
    # підпис смуги
    frags.append(text(BX + BW / 2, BY - 14, "усі доми платформи", size=12, color=MUTED, italic=True))

    # куди веде кожен сегмент
    frags.append(arrow(BX + hot_w / 2, BY + BH + 6, BX + hot_w / 2, BY + BH + 44, color=FIELD))
    frags.append(fitbox(BX + hot_w / 2 - 150, BY + BH + 50, 300, 66,
        "→ АКТОР-ШАР\nжива сесія, real-time, read-your-writes",
        size=12.5, fill=GREENF, stroke=FIELD))

    frags.append(arrow(BX + hot_w + (BW - hot_w) / 2, BY + BH + 6,
                       BX + hot_w + (BW - hot_w) / 2, BY + BH + 44, color=NEG))
    frags.append(fitbox(BX + hot_w + (BW - hot_w) / 2 - 175, BY + BH + 50, 350, 66,
        "→ ШАРДОВАНА БД\nдешеве читання по ключу home_id, без гарячої машинерії",
        size=12.5, fill=BLUEF, stroke=NEG))

    # окрема нижня примітка про аудит
    frags.append(text(W / 2, 448,
        "А «що коли ставалось» (замки, доступ) не лягає ні туди, ні туди — це вузька скибка в журнал аудиту.",
        size=12.5, color=POS))

    render(os.path.join(IMG, "access-profile.svg"), W, H, *frags,
           title="Чому композиція: гарячий набір малий, холодний хвіст величезний")


def fig_convergence_map():
    """Три індустрії × три ролі даних — усі зійшлися на тій самій трійці."""
    W, H = 1320, 610
    frags = []

    LX, LW = 40, 224           # колонка ярликів-індустрій
    CW, GAP = 320, 16
    AX = LX + LW + GAP         # 280 — довговічне сховище (синє)
    BX = AX + CW + GAP         # 616 — гарячий актор (зелене)
    CX = BX + CW + GAP         # 952 — історія/аудит (бурштин)
    HY, HH = 58, 60
    R1, R2, R3, RH = 140, 258, 376, 108

    # ── заголовки ролей ─────────────────────────────────────────────────
    frags.append(fitbox(AX, HY, CW, HH, "ДОВГОВІЧНЕ СХОВИЩЕ\n= джерело правди",
        size=13.5, fill=BLUEF, stroke=NEG, sw=2.2, bold=True))
    frags.append(fitbox(BX, HY, CW, HH, "ГАРЯЧИЙ АКТОР-ШАР\nнад сховищем — не правда",
        size=13.5, fill=GREENF, stroke=FIELD, sw=2.2, bold=True))
    frags.append(fitbox(CX, HY, CW, HH, "ІСТОРІЯ / АУДИТ\nокремим потоком",
        size=13.5, fill=AMBERF, stroke=POS, sw=2.2, bold=True))

    # ── ярлики-індустрії ────────────────────────────────────────────────
    for ry, name in ((R1, "Хмарний IoT\n(AWS · Azure)"),
                     (R2, "Ігровий бекенд\n(Orleans · Halo)"),
                     (R3, "Чат реального часу\n(Discord)")):
        frags.append(fitbox(LX, ry, LW, RH, name, size=13, fill=FILL, stroke=LINE, bold=True))

    def cell(x, y, s, fill, stroke):
        frags.append(fitbox(x, y, CW, RH, s, size=12, fill=fill, stroke=stroke))

    # рядок 1 — хмарний IoT
    cell(AX, R1, "device shadow (AWS)\ndevice twin (Azure)\nJSON, читаний і офлайн", BLUEF, NEG)
    cell(BX, R1, "тонка, керована службою\n(сесія пристрою — MQTT)", GREENF, FIELD)
    cell(CX, R1, "телеметрія → окремий потік\n(Timestream · Event Hubs)", AMBERF, POS)
    # рядок 2 — Orleans / Halo
    cell(AX, R2, "storage provider → БД\nстан грейна персиститься", BLUEF, NEG)
    cell(BX, R2, "grain: одна активація на ключ\nгідрується з БД, правди не тримає", GREENF, FIELD)
    cell(CX, R2, "журнал подій — окрема опція,\nне основа (Halo: стан у сховищі)", AMBERF, POS)
    # рядок 3 — Discord
    cell(AX, R3, "ScyllaDB · розділ (channel_id, bucket)\nSnowflake — хронологія", BLUEF, NEG)
    cell(BX, R3, "GenServer: сесія-на-з'єднання\n+ процес гільдії (жива, в пам'яті)", GREENF, FIELD)
    cell(CX, R3, "audit log сервера окремо\n+ Rust-шар проти гарячих розділів", AMBERF, POS)

    # ── наскрізне правило ───────────────────────────────────────────────
    frags.append(line(LX, 512, CX + CW, 512, color=MUTED, sw=1, dash="3,5"))
    frags.append(text((LX + CX + CW) / 2, 540,
        "Жодна не веде весь стан журналом подій. Жодна не тримає весь стан лише в акторах.",
        size=13, color=INK, bold=True))
    frags.append(text((LX + CX + CW) / 2, 562,
        "Правда — у сховищі; актор — лише гарячий шлях; історія — окремим логом.",
        size=12.5, color=MUTED))

    render(os.path.join(IMG, "convergence-map.svg"), W, H, *frags,
           title="Три індустрії, один кістяк: та сама трійця ролей даних")


def fig_convergence_timeline():
    """Незалежні, рознесені в часі доріжки трьох індустрій до тієї самої форми."""
    W, H = 1320, 540
    frags = []
    AMBER = "#b9770e"

    X0, X1, Y0, Y1 = 235, 1262, 2011, 2023
    def X(y):
        return X0 + (y - Y0) * (X1 - X0) / (Y1 - Y0)

    L1, L2, L3 = 105, 250, 400

    for ly, tag, col, fillc in ((L1, "ІГРИ\nOrleans", FIELD, GREENF),
                                (L2, "ХМАРНИЙ IoT\nAWS · Azure", NEG, BLUEF),
                                (L3, "ЧАТ\nDiscord", AMBER, AMBERF)):
        frags.append(line(X0 - 8, ly, X1 + 8, ly, color=MUTED, sw=1.1, dash="2,5"))
        frags.append(fitbox(24, ly - 30, 152, 60, tag, size=12, fill=fillc, stroke=col, bold=True))

    def dot(y, ly, col, lines, up=True):
        x = X(y)
        frags.append(circle(x, ly, 7, fill=col, stroke=col))
        if up:
            ty = ly - 20 - (len(lines) - 1) * 11 * 1.25
        else:
            ty = ly + 24
        frags.append(mtext(x, ty, lines, size=11, color=INK, lh=1.25))

    # доріжка 1 — ігри / Orleans
    dot(2011, L1, FIELD, ["2011", "Orleans у проді", "під Halo"], up=True)
    dot(2012, L1, FIELD, ["2012", "Halo 4 — увесь", "бекенд на Orleans"], up=False)
    dot(2014, L1, FIELD, ["2014", "стаття MSR-TR-2014-41"], up=True)
    dot(2015, L1, FIELD, ["2015 (січ.)", "відкритий код"], up=False)
    # доріжка 2 — хмарний IoT
    dot(2015, L2, NEG, ["2015 (жовт.)", "AWS IoT · Device Shadow", "(re:Invent)"], up=True)
    dot(2016, L2, NEG, ["2016", "Azure IoT Hub GA", "device twin"], up=False)
    # доріжка 3 — Discord
    dot(2017, L3, AMBER, ["2017", "Elixir · GenServer", "5 млн онлайн"], up=True)
    dot(2022, L3, AMBER, ["2022–23", "→ ScyllaDB (трильйони)", "+ Rust-шар злиття"], up=True)

    # ── вісь часу ───────────────────────────────────────────────────────
    AY = 490
    frags.append(arrow(X0 - 10, AY, X1 + 20, AY, color=INK))
    for yr in (2011, 2014, 2017, 2020, 2023):
        frags.append(line(X(yr), AY - 5, X(yr), AY + 5, color=INK, sw=1.2))
        frags.append(text(X(yr), AY + 20, str(yr), size=11, color=MUTED))
    frags.append(text(X1 + 4, AY - 10, "час", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "convergence-timeline.svg"), W, H, *frags,
           title="Незалежно й нарізно — до тієї самої форми")


def fig_command_writethrough():
    """Командний шлях «замкни двері»: актор-координатор пише наскрізь у шард і аудит."""
    W, H = 1280, 580
    frags = []

    # ── caller ───────────────────────────────────────────────────────────────
    frags.append(fitbox(60, 205, 200, 96,
        "сесія А (власник)\n«замкни двері»\nзамок entrance",
        size=13, fill=FILL, stroke=LINE))

    # ── актор-координатор (центр, зелений) ────────────────────────────────────
    frags.append(fitbox(350, 175, 340, 150,
        "ЖИВА СЕСІЯ ДОМУ · актор\nкеш-координатор, НЕ джерело правди\n"
        "стан у пам'яті: version 6 → 7\nпошта серіалізує команди",
        size=13, fill=GREENF, stroke=FIELD))
    frags.append(text(520, 162, "дім home42 на зв'язку", size=11.5, color=MUTED, italic=True))

    # ── шард (джерело правди, синій, товща рамка) ─────────────────────────────
    frags.append(fitbox(780, 95, 440, 130,
        "ШАРДОВАНА БД · ДЖЕРЕЛО ПРАВДИ\nрядок на home_id · переживає рестарт\n"
        "put_cas(expected=6) → version=7",
        size=13, fill=BLUEF, stroke=NEG, sw=2.4))
    frags.append(text(1000, 82, "тут правда", size=11.5, color=NEG, italic=True, bold=True))

    # ── журнал аудиту (append-only, бурштиновий) ──────────────────────────────
    frags.append(fitbox(780, 375, 440, 120,
        "ЖУРНАЛ АУДИТУ · append-only\nappend «Locked entrance · by A»\n"
        "вузька скибка: замки й доступ",
        size=13, fill=AMBERF, stroke=POS))

    # ── стрілки потоку (нумеровані) ───────────────────────────────────────────
    # ① команда
    frags.append(arrow(260, 240, 350, 240, color=INK))
    frags.append(text(305, 230, "① команда", size=11.5, color=INK))
    # ② пише рядок у шард
    frags.append(arrow(690, 220, 780, 165, color=NEG, sw=2.2))
    frags.append(text(730, 146, "② пише у шард", size=12, color=NEG, bold=True))
    # ③ дописує подію в аудит (підпис ліворуч від діагоналі, щоб стрілка не перетинала)
    frags.append(arrow(690, 285, 780, 400, color=POS, sw=1.9))
    frags.append(text(612, 352, "③ дописує подію", size=11.5, color=POS, bold=True))
    # ④ ack назад (аж тепер)
    frags.append(arrow(350, 285, 260, 285, color=FIELD, sw=1.8))
    frags.append(text(305, 306, "④ ack (аж тепер)", size=11.5, color=FIELD))

    # ── нижнє правило ─────────────────────────────────────────────────────────
    frags.append(line(60, 520, 1220, 520, color=MUTED, sw=1, dash="3,5"))
    frags.append(mtext(640, 542,
        ["Актор веде кеш, але правду кладе В ШАРД (крок ②) ще ДО ack. Тому read-your-writes:",
         "щойно ④ повернувся — довговічний рядок уже несе version 7; і тепле, і холодне читання це побачать."],
        size=12.5, color=INK, lh=1.35))

    render(os.path.join(IMG, "command-writethrough.svg"), W, H, *frags,
           title="Командний шлях: координатор пише наскрізь у джерело правди")


def fig_read_routing():
    """Три читання — три різні шляхи; розвилку робить реєстр сесій."""
    W, H = 1320, 560
    frags = []

    # ── входи ліворуч ─────────────────────────────────────────────────────────
    frags.append(fitbox(50, 95, 260, 80,
        "ТЕПЛЕ\n«покажи мій дім»\nдім на зв'язку", size=12.5, fill=FILL, stroke=LINE))
    frags.append(fitbox(50, 220, 260, 80,
        "ХОЛОДНЕ\n«покажи мій дім»\nдім спить (офлайн)",
        size=12.5, fill=GREYF, stroke=MUTED, color=MUTED))
    frags.append(fitbox(50, 400, 260, 80,
        "ІСТОРІЯ\n«хто відмикав о 3:00?»", size=12.5, fill=FILL, stroke=LINE))

    # ── реєстр сесій (розвилка для теплого й холодного) ───────────────────────
    frags.append(fitbox(430, 145, 300, 100,
        "РЕЄСТР СЕСІЙ\nдім на зв'язку?\n(жива сесія існує?)",
        size=12.5, fill=FILL, stroke=INK))

    # ── призначення праворуч ──────────────────────────────────────────────────
    frags.append(fitbox(870, 80, 400, 96,
        "АКТОР · жива сесія\nsnapshot із пам'яті → version 7\nread-your-writes",
        size=12.5, fill=GREENF, stroke=FIELD))
    frags.append(fitbox(870, 235, 400, 96,
        "ШАРДОВАНА БД\nget(home_id) — точково по ключу\nповз актор, дешеве читання",
        size=12.5, fill=BLUEF, stroke=NEG))
    frags.append(fitbox(870, 400, 400, 96,
        "ЖУРНАЛ АУДИТУ\nread(home_id, 02:00–04:00)\nстрічка подій, не поточний стан",
        size=12.5, fill=AMBERF, stroke=POS))

    # ── стрілки ───────────────────────────────────────────────────────────────
    frags.append(arrow(310, 135, 430, 175, color=INK))      # тепле → реєстр
    frags.append(arrow(310, 260, 430, 215, color=INK))      # холодне → реєстр
    frags.append(arrow(730, 175, 870, 128, color=FIELD, sw=2.1))   # реєстр → актор
    frags.append(arrow(730, 215, 870, 283, color=NEG, sw=2.1))     # реєстр → шард
    # підписи розвилки — у клині МІЖ двома стрілками, жодної не перетинають
    frags.append(text(800, 188, "жива сесія → актор", size=11, color=FIELD))
    frags.append(text(800, 212, "нема сесії → шард", size=11, color=NEG))
    frags.append(arrow(310, 440, 870, 448, color=POS))      # історія → журнал
    frags.append(text(585, 428, "прямо в журнал — повз актор і повз поточний стан",
                      size=11, color=MUTED, italic=True))

    # ── нижнє правило ─────────────────────────────────────────────────────────
    frags.append(line(60, 516, 1260, 516, color=MUTED, sw=1, dash="3,5"))
    frags.append(mtext(660, 538,
        ["Одне слово «читання» — три шляхи. Гаряче → в актор (read-your-writes); холодне → прямо в шард по ключу;",
         "історія → у журнал. Розвилку теплого й холодного робить реєстр сесій: дім на зв'язку чи спить."],
        size=12, color=INK, lh=1.3))

    render(os.path.join(IMG, "read-routing.svg"), W, H, *frags,
           title="Три читання твіна — три різні шляхи")


def fig_restart_rehydrate():
    """Той самий крах — дві ціни: знімок+перегравання проти одного store.get."""
    W, H = 1200, 480
    frags = []

    # ── верхня доріжка: чистий актор (правда в пам'яті) ───────────────────────
    frags.append(text(40, 92, "чистий актор — правда в пам'яті (складне відновлення):",
                      size=12.5, color=POS, anchor="start", bold=True))
    frags.append(fitbox(60, 108, 180, 72, "актор у RAM\nversion 7",
                        size=12.5, fill=GREENF, stroke=FIELD))
    frags.append(fitbox(288, 108, 132, 72, "⚡ крах\nRAM зникла",
                        size=12, fill="#fdecea", stroke=POS, color=POS))
    frags.append(fitbox(468, 108, 200, 72, "знімок v5 на диску",
                        size=12.5, fill=FILL, stroke=LINE))
    frags.append(fitbox(716, 108, 240, 72, "+ переграти хвіст\nподій e6, e7",
                        size=12.5, fill=FILL, stroke=LINE))
    frags.append(fitbox(1004, 108, 150, 72, "version 7",
                        size=12.5, fill=GREENF, stroke=FIELD))
    frags.append(arrow(240, 144, 288, 144, color=INK))
    frags.append(arrow(420, 144, 468, 144, color=INK))
    frags.append(arrow(668, 144, 716, 144, color=INK))
    frags.append(arrow(956, 144, 1004, 144, color=INK))
    frags.append(text(607, 202, "вікно втрати між знімками", size=11, color=POS, italic=True))

    # ── нижня доріжка: композиція (правда у шарді) ────────────────────────────
    frags.append(text(40, 292, "композиція — актор-координатор, правда у шарді (відновлення = один store.get):",
                      size=12.5, color=FIELD, anchor="start", bold=True))
    frags.append(fitbox(60, 308, 180, 72, "актор-кеш\n(будь-який стан)",
                        size=12.5, fill=GREENF, stroke=FIELD))
    frags.append(fitbox(288, 308, 132, 72, "⚡ крах\nсесія зникла",
                        size=12, fill="#fdecea", stroke=POS, color=POS))
    frags.append(fitbox(468, 308, 260, 72, "store.get(home_id)\nодин рух",
                        size=12.5, fill=BLUEF, stroke=NEG))
    frags.append(fitbox(776, 308, 260, 72, "свіжий актор\nversion 7",
                        size=12.5, fill=GREENF, stroke=FIELD))
    frags.append(arrow(240, 344, 288, 344, color=INK))
    frags.append(arrow(420, 344, 468, 344, color=INK))
    frags.append(arrow(728, 344, 776, 344, color=INK))

    # ── підпис ────────────────────────────────────────────────────────────────
    frags.append(line(40, 410, 1160, 410, color=MUTED, sw=1, dash="3,5"))
    frags.append(mtext(600, 434,
        ["Той самий крах — дві ціни. Актор як джерело правди воскресає зі знімка плюс перегравання (і має вікно втрати).",
         "Актор-координатор просто перечитує рядок: стан ніколи не був у ньому, тож «відновлювати» нема чого."],
        size=12.5, color=INK, lh=1.3))

    render(os.path.join(IMG, "restart-rehydrate.svg"), W, H, *frags,
           title="Рестарт: складне відновлення проти регідратації")


if __name__ == "__main__":
    fig_composition()
    fig_access_profile()
    fig_convergence_map()
    fig_convergence_timeline()
    fig_command_writethrough()
    fig_read_routing()
    fig_restart_rehydrate()
    print("OK: twin-composition.svg, access-profile.svg, convergence-map.svg, convergence-timeline.svg, "
          "command-writethrough.svg, read-routing.svg, restart-rehydrate.svg")
