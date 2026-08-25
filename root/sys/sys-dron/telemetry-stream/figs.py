# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Телеметрія: двосторонній потік».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Імена файлів — slug-only, без номерів (AUTHORING §2, §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


def antenna(x, y, col=NEG, h=22):
    """Маленька антена-щогла з пташкою згори."""
    return (line(x, y, x, y - h, color=MUTED, sw=3) +
            line(x - 6, y - h, x + 6, y - h - 4, color=MUTED, sw=2.4))


def radio_board(cx, cy, col, label):
    """Платка модема: прямокутник + антена + підпис."""
    w, h = 60, 38
    out = rect(cx - w / 2, cy - h / 2, w, h, fill="#fbfbfb", stroke=col, sw=1.8)
    out += antenna(cx, cy - h / 2, col=col)
    out += text(cx, cy + 5, label, size=12, color=col, bold=True)
    return out


# ── Фігура 1: пара модулів — air на борту, ground на землі ───────────────────
# Ідея: ДВА однакові модулі по краях, між ними радіолінк в обидва боки; разом —
# один невидимий «провід». Підкреслює парність і діапазони.
def fig_air_ground():
    W, H = 900, 340
    P = [text(W / 2, 30, "Телеметрія — це ПАРА модулів (air + ground)", size=17, bold=True)]

    # борт ліворуч
    P.append(radio_board(150, 150, NEG, "air"))
    fr, w, h = textbox(150, 232, "на борту:\nу телеметрійний\nUART контролера",
                       size=11.5, fill="#eef2f7", stroke=INK)
    P.append(fr)

    # земля праворуч
    P.append(radio_board(W - 150, 150, FIELD, "ground"))
    fr, w, h = textbox(W - 150, 232, "на землі:\nу USB ноутбука\n/ станції",
                       size=11.5, fill="#eef2f7", stroke=INK)
    P.append(fr)

    # радіолінк в обидва боки
    P.append(line(200, 135, W - 200, 135, color=POS, sw=2.2, dash="5,4"))
    P.append(line(W - 200, 165, 200, 165, color=POS, sw=2.2, dash="5,4"))
    P.append(text(W / 2, 118, "радіолінк 433 / 868 / 915 МГц", size=12.5, color=POS, bold=True))
    P.append(text(W / 2, 158, "(обидва боки)", size=11, color=MUTED))

    P.append(fitbox(120, 288, W - 240, 36,
                    "Разом пара працює як один прозорий «бездротовий провід»",
                    size=12.5, fill="#e9f7ef", stroke=FIELD, bold=True))
    render("img/air-ground.svg", W, H, *P)


# ── Фігура 2: прозорий серійний міст ────────────────────────────────────────
# Ідея: байт, що ввійшов з одного UART, виходить з іншого; сторони «думають»,
# що це дріт. Показуємо наскрізний потік байтів і думку-хмарку «це кабель».
def fig_serial_bridge():
    W, H = 940, 320
    P = [text(W / 2, 30, "Прозорий серійний міст: наче бездротовий UART-кабель", size=17, bold=True)]

    y = 150
    # контролер
    fr, w, h = textbox(110, y, "польотний\nконтролер", size=12, bold=True,
                       fill="#eef2f7", stroke=INK, min_w=130)
    P.append(fr)
    # модеми
    P.append(radio_board(330, y, NEG, "air"))
    P.append(radio_board(610, y, FIELD, "ground"))
    # станція
    fr, w, h = textbox(W - 110, y, "наземна\nстанція", size=12, bold=True,
                       fill="#eef2f7", stroke=INK, min_w=130)
    P.append(fr)

    # наскрізний потік байтів зліва направо
    P.append(arrow(178, y - 12, 300, y - 12, color=INK))
    P.append(text(239, y - 20, "UART", size=10.5, color=MUTED))
    P.append(arrow(360, y - 12, 580, y - 12, color=POS))
    P.append(text(470, y - 20, "радіо", size=10.5, color=POS))
    P.append(arrow(640, y - 12, W - 178, y - 12, color=INK))
    P.append(text(W - 290, y - 20, "USB", size=10.5, color=MUTED))

    # «байти» як кружечки на лінії
    for bx in (240, 470, W - 290):
        P.append(circle(bx, y - 12, 4, fill=INK, stroke=INK))

    # думка-хмарка
    P.append(fitbox(280, 232, 380, 34,
                    "обидві сторони «думають», що з'єднані ДРОТОМ",
                    size=12, fill="#fdecea", stroke=POS, color=POS, bold=True))

    P.append(text(W / 2, 296, "що ввійшло з одного кінця — виходить з іншого; MAVLink тече наскрізь",
                  size=12, color=MUTED))
    render("img/serial-bridge.svg", W, H, *P)


# ── Фігура 3: потік MAVLink — різні типи, різні частоти ──────────────────────
# Ідея: кожен тип повідомлення тече зі своєю частотою потоку; критичне/швидке —
# густо, фонове — зрідка. Щільність крапок = частота.
def fig_mavlink_stream():
    W, H = 940, 380
    P = [text(W / 2, 30, "Потік телеметрії: кожен тип — на своїй частоті", size=17, bold=True)]

    rows = [
        ("ATTITUDE — кути нахилу", "~10–50 Гц", FIELD, 14),
        ("VFR_HUD — швидкість, висота", "~10 Гц", INK, 8),
        ("GLOBAL_POSITION_INT — координати", "~5 Гц", INK, 5),
        ("SYS_STATUS — заряд, давачі", "~2 Гц", MUTED, 3),
        ("HEARTBEAT — я живий + режим", "~1 Гц", POS, 2),
    ]
    lane_x0, lane_x1 = 90, W - 150
    y0 = 90
    for i, (name, rate, col, n) in enumerate(rows):
        y = y0 + i * 52
        P.append(line(lane_x0, y, lane_x1, y, color="#d0d5dd", sw=1.2))
        P.append(text(lane_x0 - 8, y + 4, "▶", size=11, color=col, anchor="end"))
        for k in range(n):
            px = lane_x0 + 14 + k * (lane_x1 - lane_x0 - 28) / max(1, n - 1) if n > 1 else (lane_x0 + lane_x1) / 2
            P.append(circle(px, y, 4.5, fill=col, stroke=col))
        P.append(text(lane_x0 + 8, y - 13, name, size=11.5, color=INK, anchor="start"))
        P.append(text(lane_x1 + 8, y + 4, rate, size=11.5, color=col, bold=True, anchor="start"))

    P.append(text(W / 2, H - 18,
                  "густо = часто (критичне); зрідка = рідко (фонове) → вузький канал не тоне",
                  size=12, color=MUTED))
    render("img/mavlink-stream.svg", W, H, *P)


# ── Фігура 4: розмова, а не мовлення — потік у два боки ──────────────────────
# Ідея: вниз тече стан, угору команди/запити, ОДНІЄЮ лінією; це діалог.
def fig_two_way():
    W, H = 940, 320
    P = [text(W / 2, 30, "Це РОЗМОВА, а не мовлення: потік у два боки", size=17, bold=True)]

    P.append(radio_board(140, 165, NEG, "борт"))
    fr, w, h = textbox(W - 130, 165, "наземна\nстанція (GCS)", size=12, bold=True,
                       fill="#eef2f7", stroke=INK, min_w=150)
    P.append(fr)

    # вниз: телеметрія
    P.append(arrow(W - 230, 120, 200, 120, color=POS))
    P.append(text(W / 2, 108, "ВНИЗ: стан — висота, GPS, заряд, кути, режим",
                  size=12, color=POS, bold=True))
    # вгору: команди
    P.append(arrow(200, 215, W - 230, 215, color=NEG))
    P.append(text(W / 2, 233, "ВГОРУ: команди, читання/запис параметрів, місія, RC-override",
                  size=12, color=NEG, bold=True))

    P.append(fitbox(110, 270, W - 220, 36,
                    "Та сама лінія несе обидва напрями — тому це дім для MAVLink (мови запитів і відповідей)",
                    size=12, fill="#fbf3df", stroke="#b08900", bold=True))
    render("img/two-way.svg", W, H, *P)


# ── Фігура 5: SiK-радіо — дві однакові платки ───────────────────────────────
# Ідея: впізнаваний клас заліза; дві ОДНАКОВІ платки, відкрита прошивка, FHSS,
# дві швидкості (серійна на UART vs повітряна в ефірі).
def fig_sik_radio():
    W, H = 920, 360
    P = [text(W / 2, 30, "Класика заліза: SiK-радіо (дві однакові платки)", size=17, bold=True)]

    P.append(radio_board(220, 130, NEG, "SiK air"))
    P.append(radio_board(W - 220, 130, FIELD, "SiK ground"))
    P.append(line(270, 118, W - 270, 118, color=POS, sw=2, dash="5,4"))
    P.append(text(W / 2, 106, "FHSS — стрибки частоти, щоб не глушитися", size=12, color=POS, bold=True))

    facts = [
        "відкрита прошивка SiK · чипи Silicon Labs",
        "433 / 868 / 915 МГц · ~100 мВт (20 дБм)",
        "серійна швидкість на UART: ~57600 бод",
        "повітряна швидкість в ефірі: ~64 кбіт/с",
        "дальність — кілометри (RFD900: десятки км)",
    ]
    y = 198
    for i, f in enumerate(facts):
        P.append(circle(120, y + i * 28 - 4, 3.5, fill=INK, stroke=INK))
        P.append(text(136, y + i * 28, f, size=12.5, color=INK, anchor="start"))

    P.append(fitbox(560, 188, 320, 56,
                    "дві швидкості —\nНЕЗАЛЕЖНІ:\nдріт ≠ ефір",
                    size=13, fill="#fdecea", stroke=POS, color=POS, bold=True))
    render("img/sik-radio.svg", W, H, *P)


# ── Фігура 6: інші «труби» доставки MAVLink ─────────────────────────────────
# Ідея: труба і мова розділені → одну й ту саму мову (MAVLink) везуть різні
# транспорти. Чотири варіанти + особливий випадок.
def fig_transports():
    W, H = 960, 380
    P = [text(W / 2, 30, "Одна мова (MAVLink) — різні «труби»", size=17, bold=True)]

    pipes = [
        ("телеметрійне\nрадіо (SiK/RFD900)", "кілометри", FIELD),
        ("USB-кабель", "стіл / стенд", INK),
        ("Wi-Fi / Bluetooth\n(ESP32-міст)", "TCP/UDP, телефон", NEG),
        ("спільно з RC\n(CRSF / ELRS)", "один лінк на все", POS),
    ]
    n = len(pipes)
    bw = 200
    gap = (W - n * bw) / (n + 1)
    for i, (name, note, col) in enumerate(pipes):
        x = gap + i * (bw + gap)
        P.append(fitbox(x, 80, bw, 70, name, size=13, fill="#fbfbfb", stroke=col, color=col, bold=True))
        P.append(text(x + bw / 2, 172, note, size=11.5, color=MUTED))
        # стрілка вниз до спільної шини «MAVLink»
        P.append(arrow(x + bw / 2, 190, x + bw / 2, 232, color=col))

    # спільна шина
    P.append(rect(gap, 236, W - 2 * gap, 40, fill="#eef2f7", stroke=INK, sw=1.6))
    P.append(text(W / 2, 261, "той самий потік MAVLink — мова не змінюється", size=13, bold=True))

    P.append(text(W / 2, 320, "особливий випадок: бортовий комп'ютер ПОРЯД із контролером, короткий UART без радіо",
                  size=12, color=MUTED, italic=True))
    render("img/transports.svg", W, H, *P)


# ── Фігура 7: наземна станція — людський кінець ─────────────────────────────
# Ідея: GCS розкладає потік MAVLink у панель приладів і шле команди назад;
# перекладач між мовою машини й очима людини.
def fig_gcs():
    W, H = 940, 360
    P = [text(W / 2, 30, "Людський кінець лінії: наземна станція (GCS)", size=17, bold=True)]

    # зліва: потік MAVLink
    fr, w, h = textbox(120, 170, "потік\nMAVLink", size=12.5, bold=True,
                       fill="#eef2f7", stroke=INK, min_w=120)
    P.append(fr)

    # центр: GCS
    P.append(rect(330, 90, 280, 180, fill="#fbfbfb", stroke=FIELD, sw=2))
    P.append(text(470, 78, "QGroundControl / Mission Planner", size=12.5, bold=True, color=FIELD))
    panel = ["карта + маршрут", "висота · швидкість", "заряд · режим", "супутники GPS · попередження"]
    for i, p in enumerate(panel):
        P.append(text(470, 130 + i * 32, p, size=12, color=INK))

    # праворуч: людина
    fr, w, h = textbox(W - 110, 170, "очі та руки\nоператора", size=12.5, bold=True,
                       fill="#eef2f7", stroke=INK, min_w=130)
    P.append(fr)

    # стрілки: потік → GCS → людина (читання) і людина → GCS → команди (запис)
    P.append(arrow(184, 150, 326, 150, color=POS))
    P.append(text(255, 140, "читає", size=10.5, color=POS))
    P.append(arrow(614, 150, W - 178, 150, color=POS))
    P.append(arrow(W - 178, 200, 614, 200, color=NEG))
    P.append(text(W - 250, 220, "команди", size=10.5, color=NEG))
    P.append(arrow(326, 200, 184, 200, color=NEG))

    P.append(text(W / 2, 320, "GCS — перекладач між мовою машини (MAVLink) і очима людини",
                  size=12.5, color=MUTED))
    render("img/gcs.svg", W, H, *P)


if __name__ == "__main__":
    fig_air_ground()
    fig_serial_bridge()
    fig_mavlink_stream()
    fig_two_way()
    fig_sik_radio()
    fig_transports()
    fig_gcs()
    print("OK: 7 figures -> img/")
