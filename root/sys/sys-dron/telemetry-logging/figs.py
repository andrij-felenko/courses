# -*- coding: utf-8 -*-
"""Фігури до теми «Запис телеметрії й відтворення логів» довідника QGroundControl."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

BAND = "#eef2f6"
SOFT = "#ffffff"
WARM = "#fdf3e7"
COLD = "#eaf0fd"
GOOD = "#eaf7ef"
GREY = "#c8d2dc"


# ───────────────── 1. Будова запису в лозі ─────────────────
def fig_record_layout():
    W, H = 1280, 780
    f = []

    f.append(text(W / 2, 36, "Лог телеметрії: ланцюг записів «мітка часу + кадр»", size=18, bold=True))

    # ── верхня смуга: чотири записи поспіль ──
    y0 = 84
    f.append(text(60, y0 - 12, "файл від початку", size=13, color=MUTED, anchor="start"))

    recs = [(60, 70, 210, "ATTITUDE"),
            (350, 70, 130, "HEARTBEAT"),
            (560, 70, 310, "PARAM_VALUE"),
            (950, 70, 160, "SYS_STATUS")]
    for x, tw, fw, name in recs:
        f.append(rect(x, y0, tw, 66, fill=COLD, stroke=NEG, sw=1.6, rx=8))
        f.append(text(x + tw / 2, y0 + 42, "8 Б", size=14, color=NEG, bold=True))
        f.append(rect(x + tw, y0, fw, 66, fill=GOOD, stroke=LINE, sw=1.6, rx=8))
        f.append(text(x + tw + fw / 2, y0 + 42, name, size=13))

    f.append(text(60, y0 + 92, "синє — час у мікросекундах · зелене — кадр MAVLink як прийшов",
                  size=13, color=MUTED, anchor="start"))

    # ── зум одного запису ──
    f.append(arrow(200, y0 + 108, 200, y0 + 152))

    yz = 250
    f.append(text(140, yz - 16, "один запис зблизька", size=13, color=MUTED, anchor="start"))

    f.append(rect(140, yz, 250, 96, fill=COLD, stroke=NEG, sw=1.8, rx=8))
    f.append(mtext(265, yz + 36, ["мітка часу", "старший байт першим"], size=14, color=NEG, bold=True))

    parts = [(390, 210, "заголовок\n10 Б"),
             (600, 400, "навантаження\n0…255 Б"),
             (1000, 140, "сума\n2 Б")]
    for x, w, label in parts:
        f.append(fitbox(x, yz, w, 96, label, size=14, fill=GOOD))

    f.append(text(140, yz + 130, "0", size=13, color=MUTED, anchor="start"))
    f.append(text(390, yz + 130, "8", size=13, color=MUTED))
    f.append(text(1140, yz + 130, "до 275", size=13, color=MUTED, anchor="end"))
    f.append(line(140, yz + 112, 1140, yz + 112, color=GREY, sw=1.2))

    # ── два наслідки ──
    f.append(fitbox(70, 440, 560, 150,
                    "ПОЛЯ ДОВЖИНИ В ЗАПИСІ НЕМАЄ\n"
                    "Скільки байтів займає кадр, знає тільки\n"
                    "сам кадр. Отже, дійти до наступного запису\n"
                    "можна лише розібравши поточний.",
                    size=15, fill=WARM))

    f.append(fitbox(650, 440, 560, 150,
                    "НАЙДОВШИЙ ЗАПИС\n"
                    "10 + 255 + 2 = 267 Б  (кадр v2 без підпису)\n"
                    "267 + 8 = 275 Б  (весь запис)\n"
                    "Підпис на 13 Б знімають перед записуванням.",
                    size=15, fill=COLD))

    # ── наслідок для доступу ──
    f.append(fitbox(70, 620, 1140, 120,
                    "ЗВІДСИ ВСЯ МЕХАНІКА ВІДТВОРЕННЯ: файл — не масив, а ланцюг.\n"
                    "Тривалість логу коштує повного проходу файлом; перемотування бере позицію\n"
                    "пропорційно до РОЗМІРУ В БАЙТАХ і далі шукає найближчу межу кадру заново.",
                    size=15, fill=BAND))

    render(os.path.join(OUT, 'record-layout.svg'), W, H, *f)


# ───────────────── 2. Життя файлу телеметрії ─────────────────
def fig_log_lifecycle():
    W, H = 1300, 860
    f = []

    f.append(text(W / 2, 36, "Життя файлу телеметрії: тимчасовий із першої ж миті", size=18, bold=True))

    LX = 340   # центр лівої (нормальної) колонки
    RX = 980   # центр правої (аварійної) колонки

    # ── спільний початок ──
    f.append(fitbox(LX - 300, 80, 600, 70,
                    "перший HEARTBEAT або HIGH_LATENCY у каналі", size=15, fill=GOOD, bold=True))
    f.append(arrow(LX, 150, LX, 194))

    f.append(fitbox(LX - 300, 196, 600, 88,
                    "відкрито тимчасовий файл у системній теці tmp:\nFlightDataXXXXXX.mavlink",
                    size=15, fill=COLD))
    f.append(arrow(LX, 284, LX, 328))

    f.append(fitbox(LX - 300, 330, 600, 88,
                    "кожен цілий кадр — обох напрямків — лягає на диск\nодразу, до кінця сеансу",
                    size=15, fill=BAND))

    # ── розгалуження вниз (нормально) і вправо (падіння) ──
    f.append(arrow(LX, 418, LX, 462))

    f.append(fitbox(LX - 300, 464, 600, 70,
                    "останній апарат зник із переліку → _stopLogging()", size=15, fill=SOFT))
    f.append(arrow(LX, 534, LX, 578))

    f.append(fitbox(LX - 300, 580, 600, 88,
                    "апарат був зброєний  АБО  ввімкнено telemetrySaveNotArmed ?",
                    size=15, fill=SOFT))

    f.append(arrow(LX - 160, 668, LX - 160, 714))
    f.append(text(LX - 232, 696, "так", size=13, color=MUTED))
    f.append(fitbox(LX - 320, 716, 320, 96,
                    "Telemetry/\n2026-08-02 14-31-07.tlog\n(атомарна заміна)",
                    size=14, fill=GOOD))

    f.append(arrow(LX + 160, 668, LX + 160, 714))
    f.append(text(LX + 232, 696, "ні", size=13, color=MUTED))
    f.append(fitbox(LX + 20, 716, 300, 96, "файл прибрано", size=14, fill=WARM))

    # ── аварійна гілка ──
    f.append(arrow(LX + 300, 374, RX - 300, 374))
    f.append(text((LX + 300 + RX - 300) / 2, 312, "застосунок упав", size=13, color=POS, bold=True))

    f.append(fitbox(RX - 300, 330, 600, 88,
                    "ніхто не викликав _stopLogging(),\nале файл уже лежить на диску цілий",
                    size=15, fill=WARM))
    f.append(arrow(RX, 418, RX, 462))

    f.append(fitbox(RX - 300, 464, 600, 70,
                    "наступний запуск: обхід tmp за маскою *.mavlink", size=15, fill=SOFT))
    f.append(arrow(RX, 534, RX, 578))

    f.append(fitbox(RX - 300, 580, 600, 88,
                    "порожні прибрано, решту збережено як звичайні логи",
                    size=15, fill=GOOD))
    f.append(arrow(RX, 668, RX, 714))

    f.append(fitbox(RX - 300, 716, 600, 96,
                    "ФІЛЬТР ЗБРОЄНОСТИ ТУТ НЕ ДІЄ:\nпрапорець зник разом із застосунком,\n"
                    "тож рятують усі непорожні файли підряд",
                    size=14, fill=WARM))

    render(os.path.join(OUT, 'log-lifecycle.svg'), W, H, *f)


# ───────────────── 3. Відтворення як канал ─────────────────
def fig_replay_as_link():
    W, H = 1300, 800
    f = []

    f.append(text(W / 2, 36, "Відтворення підмінює лише джерело байтів", size=18, bold=True))

    # ── два джерела ──
    f.append(fitbox(70, 80, 480, 110,
                    "живий канал\nсерійний порт · UDP · TCP · Bluetooth",
                    size=15, fill=GOOD, bold=True))
    f.append(fitbox(750, 80, 480, 110,
                    "LogReplayLink : LinkInterface\nбайти читаються з файлу .tlog",
                    size=15, fill=COLD, bold=True))

    f.append(arrow(310, 190, 560, 246))
    f.append(arrow(990, 190, 740, 246))

    # ── спільний тракт ──
    f.append(rect(260, 248, 780, 350, fill=BAND, stroke=GREY, sw=1.4, rx=12))
    f.append(text(650, 280, "далі — той самий тракт, який не знає про підміну", size=14, color=MUTED))

    stages = [("розбір MAVLink   ·   кадр із потоку байтів", 300),
              ("маршрутизація   ·   за sysid і compid", 372),
              ("Vehicle і факти   ·   модель стану апарата", 444),
              ("карта, прилади, журнал повідомлень", 516)]
    for label, y in stages:
        f.append(fitbox(340, y, 620, 60, label, size=15, fill=SOFT))
        if y < 516:
            f.append(arrow(650, y + 60, 650, y + 70))

    # ── зворотний напрямок: обидві анотації ПОЗА рамкою тракту ──
    f.append(text(1165, 306, "команди застосунку", size=12, color=MUTED))
    f.append(line(1165, 320, 1165, 452, color=POS, sw=1.6, dash="6 5"))
    f.append(arrow(1165, 452, 1165, 466, color=POS))
    f.append(fitbox(1060, 470, 210, 96, "у живому каналі\nбайти йдуть\nв ефір", size=13, fill=GOOD))

    f.append(text(135, 306, "команди застосунку", size=12, color=MUTED))
    f.append(line(135, 320, 135, 452, color=POS, sw=1.6, dash="6 5"))
    f.append(arrow(135, 452, 135, 466, color=POS))
    f.append(fitbox(30, 470, 210, 96, "при відтворенні\n_writeBytes порожній\nкоманди зникають", size=13, fill=WARM))

    # ── три наслідки ──
    notes = [(70, "ПАУЗА = ТИША\nдля станції канал без\nсерцебиття — це «Communication Lost»"),
             (480, "ІНШІ З'ЄДНАННЯ ЗАБОРОНЕНО\nживий апарат із тим самим sysid\nзлився б із записаним в один об'єкт"),
             (890, "ЗАПИС ПРИЗУПИНЕНО\nбез цього кожен перегляд логу\nпороджував би новий лог")]
    for x, s in notes:
        f.append(fitbox(x, 630, 340, 130, s, size=14, fill=WARM))

    render(os.path.join(OUT, 'replay-as-link.svg'), W, H, *f)


# ───────────────── 4. Розклад відтворення ─────────────────
def fig_replay_timing():
    W, H = 1300, 860
    f = []

    f.append(text(W / 2, 36, "Кожен запис планують від нерухомої опори, а не від попереднього кроку",
                  size=18, bold=True))

    X0, X1 = 200, 1180
    TMAX = 20.0          # секунд у лозі

    def sx(t):
        return X0 + (X1 - X0) * t / TMAX

    # події в лозі (секунди): щільна пачка й розріджена ділянка
    events = [1.2, 2.4, 2.402, 2.404, 5.8, 7.8, 11.3, 11.302, 13.6, 17.5, 18.9]
    # пунктирні прив'язки ведемо лише для трьох подій — щоб лінії не йшли крізь підписи осей
    tied = [1.2, 7.8, 17.5]

    # ── вісь «час у лозі» ──
    y1 = 150
    f.append(text(70, y1 - 40, "час у лозі", size=15, bold=True, anchor="start"))
    f.append(line(X0, y1, X1 + 20, y1, color=LINE, sw=1.8))
    for t in (0, 5, 10, 15, 20):
        f.append(line(sx(t), y1 - 8, sx(t), y1 + 8, color=LINE, sw=1.4))
        f.append(text(sx(t), y1 + 32, "%d с" % t, size=13, color=MUTED))
    for t in events:
        f.append(circle(sx(t), y1, 6, fill=GOOD, stroke=FIELD, sw=1.8))

    # ── вісь «настінний час, 1×» ──
    y2 = 330
    f.append(text(70, y2 - 40, "настінний час, 1×", size=15, bold=True, anchor="start"))
    f.append(line(X0, y2, X1 + 20, y2, color=LINE, sw=1.8))
    for t in (0, 5, 10, 15, 20):
        f.append(line(sx(t), y2 - 8, sx(t), y2 + 8, color=LINE, sw=1.4))
        f.append(text(sx(t), y2 + 32, "%d с" % t, size=13, color=MUTED))
    for t in events:
        f.append(circle(sx(t), y2, 6, fill=COLD, stroke=NEG, sw=1.8))
    for t in tied:
        f.append(line(sx(t), y1 + 12, sx(t), y2 - 12, color=GREY, sw=1.0, dash="4 4"))

    # ── вісь «настінний час, 2×» ──
    y3 = 500
    f.append(text(70, y3 - 40, "настінний час, 2×", size=15, bold=True, anchor="start"))
    f.append(line(X0, y3, sx(10.0) + 20, y3, color=LINE, sw=1.8))
    for t in (0, 5, 10):
        f.append(line(sx(t / 2.0), y3 - 8, sx(t / 2.0), y3 + 8, color=LINE, sw=1.4))
        f.append(text(sx(t / 2.0), y3 + 32, "%d с" % t, size=13, color=MUTED))
    for t in events:
        f.append(circle(sx(t / 2.0), y3, 6, fill=COLD, stroke=NEG, sw=1.8))
    for t in tied:
        f.append(line(sx(t), y2 + 12, sx(t / 2.0), y3 - 12, color=GREY, sw=1.0, dash="4 4"))

    f.append(text(sx(11.0), y3 + 4, "вдвічі коротший настінний проміжок при тих самих подіях",
                  size=14, color=MUTED, anchor="start"))

    # ── вікно в 3 мс ──
    f.append(circle(sx(2.4), y1, 13, fill="none", stroke=POS, sw=2.2))
    f.append(arrow(sx(2.4) + 18, y1 - 16, 436, 86, color=POS))
    f.append(fitbox(440, 52, 680, 48,
                    "три кадри в межах 3 мс — один крок таймера, пачка", size=15, fill=WARM))

    # ── дві стратегії ──
    f.append(fitbox(70, 600, 560, 190,
                    "ВІД ПОПЕРЕДНЬОГО КРОКУ\n"
                    "спати (tᵢ − tᵢ₋₁) / швидкість\n"
                    "кожне спрацювання таймера запізнюється\n"
                    "на ε > 0, і ці ε додаються:\n"
                    "N кроків → відставання N · ε",
                    size=15, fill=WARM))

    f.append(fitbox(670, 600, 560, 190,
                    "ВІД ОПОРИ НА ПОЧАТКУ\n"
                    "бажаний = опора + (t − t₀) / швидкість\n"
                    "чекати = бажаний − зараз\n"
                    "запізнення попереднього кроку просто\n"
                    "вкорочує наступне чекання; ε не росте",
                    size=15, fill=GOOD))

    f.append(fitbox(70, 812, 1160, 40,
                    "чекати вийшло від'ємним — програвач відстав і читає без пауз, поки не наздожене графік",
                    size=14, fill=COLD))

    render(os.path.join(OUT, 'replay-timing.svg'), W, H, *f)


# ───────────────── 5. Перемотування: ресинк проти індексу ─────────────────
def fig_seek_and_resync():
    W, H = 1340, 920
    f = []

    f.append(text(W / 2, 36, "Два способи потрапити в потрібну мить логу", size=18, bold=True))

    # ══ ПАНЕЛЬ А ══
    f.append(text(80, 78, "А. Зсув пропорційно до розміру файлу", size=15, bold=True, anchor="start"))
    f.append(text(760, 78, "просимо 50 % часу — беремо 50 % байтів", size=14, color=POS))

    ys, hh = 110, 56
    widths = [90, 45, 150, 70, 110, 52, 190, 80, 42]
    x = 90
    for w in widths:
        f.append(rect(x, ys, 26, hh, fill=COLD, stroke=NEG, sw=1.4, rx=4))
        f.append(rect(x + 26, ys, w, hh, fill=GOOD, stroke=LINE, sw=1.4, rx=4))
        x += 26 + w + 4

    f.append(arrow(690, 92, 690, 106, color=POS))
    f.append(line(690, 108, 690, 170, color=POS, sw=2.4))

    f.append(text(637, 192, "запис = 8 Б часу + кадр; ширина запису різна, бо різна довжина кадру",
                  size=13, color=MUTED))

    f.append(text(180, 232, "що бачить автомат, почавши з цієї позиції",
                  size=14, bold=True, anchor="start"))

    f.append(fitbox(180, 248, 300, 64, "хвіст чужого кадру\nдля автомата — сміття", size=14, fill=BAND))
    f.append(fitbox(486, 248, 340, 64, "0xFD усередині даних\nкадр зібрано, сума не зійшлася",
                    size=14, fill=WARM))
    f.append(fitbox(832, 248, 308, 64, "0xFD справжній\nсума зійшлася — межа", size=14, fill=GOOD))

    f.append(text(180, 336,
                  "хибний старт коштує щонайбільше одного кадру: байти, які автомат забрав, назад не вертаються",
                  size=13, color=MUTED, anchor="start"))

    f.append(fitbox(180, 358, 960, 86,
                    "ДЕ ПОЧИНАЄТЬСЯ ЗНАЙДЕНИЙ ЗАПИС\n"
                    "позиція після кадру − mavlink_msg_get_send_buffer_length(&msg) = початок кадру\n"
                    "початок кадру − 8 = початок запису, тобто його мітка часу",
                    size=15, fill=COLD))

    # ══ ПАНЕЛЬ Б ══
    f.append(text(80, 490, "Б. Індекс «час → зсув», зібраний під час відкриття",
                  size=15, bold=True, anchor="start"))

    f.append(rect(140, 516, 240, 38, fill=BAND, stroke=LINE, sw=1.4))
    f.append(text(260, 541, "час у лозі", size=14, bold=True))
    f.append(rect(380, 516, 240, 38, fill=BAND, stroke=LINE, sw=1.4))
    f.append(text(500, 541, "зсув запису, Б", size=14, bold=True))

    rows = [("+0 с", "0"), ("+1 с", "6 208"), ("+2 с", "12 736"),
            ("+3 с", "19 010"), ("+4 с", "25 344")]
    for i, (t, off) in enumerate(rows):
        y = 554 + i * 40
        fill = WARM if i == 2 else SOFT
        f.append(rect(140, y, 240, 40, fill=fill, stroke=GREY, sw=1.2, rx=0))
        f.append(rect(380, y, 240, 40, fill=fill, stroke=GREY, sw=1.2, rx=0))
        f.append(text(260, y + 26, t, size=14))
        f.append(text(500, y + 26, off, size=14))

    f.append(arrow(700, 654, 628, 654, color=POS))

    f.append(fitbox(720, 546, 520, 84,
                    "ЦІЛЬ +2.4 с\nupper_bound по часу дає останній запис,\nне пізніший за ціль",
                    size=14, fill=COLD))
    f.append(fitbox(720, 642, 520, 84,
                    "зсув із таблиці — СПРАВЖНЯ межа запису:\nресинхронізувати нема чого,\n"
                    "далі просто читаємо вперед до цілі",
                    size=14, fill=GOOD))

    f.append(fitbox(90, 782, 560, 110,
                    "БЕЗ ІНДЕКСУ\nпозиція за часткою байтів — влучання приблизне:\n"
                    "щільна ділянка займає більше байтів за секунду,\nі повзунок над нею повзе повільніше",
                    size=14, fill=WARM))
    f.append(fitbox(690, 782, 560, 110,
                    "З ІНДЕКСОМ\nпошук O(log m), влучання точне\n"
                    "крок 1 с → 57 КБ на годину логу\nдочитування — не більше як 6.4 КБ",
                    size=14, fill=GOOD))

    render(os.path.join(OUT, 'proj-seek-and-resync.svg'), W, H, *f)


fig_record_layout()
fig_log_lifecycle()
fig_replay_as_link()
fig_replay_timing()
fig_seek_and_resync()
print("ok")
