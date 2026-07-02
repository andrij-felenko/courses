# -*- coding: utf-8 -*-
# Фігури для ДЕТАЛЬНОЇ статті «Команди MAVLink». Вивід у ./img з префіксом d-.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

HDR = "#eef2fb"   # заголовок кадру
HDR_STK = "#c3cef0"
PAY = "#eafaf1"   # корисне навантаження
PAY_STK = "#bfe6cf"
CRC = "#fdecea"   # контроль
CRC_STK = "#e7b6b0"
SIG = "#fef6e7"   # підпис
SIG_STK = "#e9d8a6"


# ── d-frame: побайтова будова кадру MAVLink v1 та v2 ──────────────────────────
def fig_frame():
    W, H = 860, 430
    p = []
    p.append(text(W/2, 28, "Побайтова будова кадру: v1 і v2 поруч", size=16, bold=True))

    def row(y, title, fields, note):
        p.append(text(30, y - 8, title, size=13, bold=True, anchor="start"))
        x = 30
        for label, wpx, fl, st in fields:
            p.append(rect(x, y, wpx, 46, fill=fl, stroke=st, sw=1.3))
            p.append(fitbox(x, y, wpx, 46, label, size=10.5, fill="none", stroke="none"))
            x += wpx
        p.append(text(30, y + 68, note, size=10.5, color=MUTED, anchor="start"))
        return x

    # v1
    v1 = [
        ("STX\n0xFE", 46, "#f0f0f0", MUTED),
        ("len", 40, HDR, HDR_STK),
        ("seq", 40, HDR, HDR_STK),
        ("sysid", 48, HDR, HDR_STK),
        ("compid", 54, HDR, HDR_STK),
        ("msgid\n1 Б", 50, HDR, HDR_STK),
        ("payload\n0..255 Б", 210, PAY, PAY_STK),
        ("CRC\n2 Б", 56, CRC, CRC_STK),
    ]
    row(78, "MAVLink v1  (заголовок 6 Б, кадр 8..263 Б)", v1,
        "CRC рахують від байта len до кінця payload; STX не входить. Далі — байт CRC_EXTRA (у кадр не пишуть).")

    # v2
    v2 = [
        ("STX\n0xFD", 46, "#f0f0f0", MUTED),
        ("len", 34, HDR, HDR_STK),
        ("incompat", 62, HDR, HDR_STK),
        ("compat", 56, HDR, HDR_STK),
        ("seq", 34, HDR, HDR_STK),
        ("sysid", 44, HDR, HDR_STK),
        ("compid", 50, HDR, HDR_STK),
        ("msgid\n3 Б", 52, HDR, HDR_STK),
        ("payload\n0..255 Б", 176, PAY, PAY_STK),
        ("CRC\n2 Б", 48, CRC, CRC_STK),
        ("signature\n0 або 13 Б", 96, SIG, SIG_STK),
    ]
    row(222, "MAVLink v2  (заголовок 10 Б, кадр 12..280 Б)", v2,
        "msgid — 24 біти (16 млн типів). Підпис є лише коли в incompat_flags виставлено біт 0x01. Хвіст нулів у payload обрізають.")

    # висновок під двома рядами
    concl = ("v2 додає два байти прапорців, розширює msgid з 1 до 3 байтів і дозволяє підпис — "
             "але тіло повідомлення й спосіб рахувати CRC ті самі. Старий парсер відрізняє версії\n"
             "за першим байтом: 0xFE → v1, 0xFD → v2.")
    p.append(mtext(W/2, 350, concl, size=11.5, color=INK))
    render(os.path.join(OUT, "d-frame.svg"), W, H, *p)


# ── d-crc-extra: чому CRC_EXTRA ловить розбіжність визначень ──────────────────
def fig_crc_extra():
    W, H = 820, 360
    p = []
    p.append(text(W/2, 28, "CRC_EXTRA: підпис самого визначення повідомлення", size=16, bold=True))

    # відправник
    sx = 60
    p.append(fitbox(sx, 70, 300, 92,
                    "Відправник (нова прошивка)\nATTITUDE {roll, pitch, yaw,\n rollspeed, pitchspeed, yawspeed}\nCRC_EXTRA = 39",
                    size=11.5, fill=HDR, stroke=HDR_STK))
    # приймач
    rx = 460
    p.append(fitbox(rx, 70, 300, 92,
                    "Приймач (стара прошивка)\nATTITUDE {roll, pitch, yaw}\n\nCRC_EXTRA = 211",
                    size=11.5, fill=CRC, stroke=CRC_STK))

    p.append(arrow(sx + 300, 116, rx, 116, color=INK, sw=1.8))
    p.append(text(W/2, 108, "кадр із CRC, порахованим із 39", size=11, color=MUTED))

    # обчислення
    calc = [
        "приймач бере той самий байтовий CRC кадру,",
        "але додає в кінець СВІЙ CRC_EXTRA = 211,",
        "а не 39 → підсумкові CRC не збігаються →",
        "кадр відкинуто як «чуже» визначення.",
    ]
    p.append(fitbox(210, 200, 400, 96, "\n".join(calc), size=12, fill=CRC, stroke=CRC_STK))

    concl = ("CRC_EXTRA — це хеш назви повідомлення й типів+імен усіх полів, вкарбований у контрольну суму. "
             "Розійшлися визначення на двох кінцях — кадр не пройде CRC, замість того щоб тихо\n"
             "розкластися в сміття. Дешева перевірка сумісності «за вартість одного байта».")
    p.append(mtext(W/2, 322, concl, size=11.5, color=INK))
    render(os.path.join(OUT, "d-crc-extra.svg"), W, H, *p)


# ── d-coord-scaling: чому координата в float втрачає точність ─────────────────
def fig_coord_scaling():
    W, H = 820, 340
    p = []
    p.append(text(W/2, 28, "Координата: float проти масштабованого int32", size=16, bold=True))

    # float гілка
    p.append(fitbox(50, 70, 340, 150,
                    "COMMAND_LONG · float32\n\n"
                    "50.4501° → зберігається як float\n"
                    "мантиса 24 біти ≈ 7 знач. цифр\n"
                    "крок біля 50° ≈ 0.0000038°\n"
                    "≈ 0.4 м похибки квантування\n"
                    "…а після арифметики — гірше",
                    size=12, fill=CRC, stroke=CRC_STK))
    # int гілка
    p.append(fitbox(430, 70, 340, 150,
                    "COMMAND_INT · int32 × 10⁷\n\n"
                    "50.4501° × 10⁷ = 504501000\n"
                    "ціле, влазить у int32 (±214°)\n"
                    "крок = 10⁻⁷° ≈ 1.1 см\n"
                    "точно й однаково скрізь на Землі\n"
                    "жодного дрейфу від float-арифметики",
                    size=12, fill=PAY, stroke=PAY_STK))

    concl = ("float має сталу кількість значущих цифр, тож біля великих градусів абсолютний крок стає метрами. "
             "Масштабоване ціле фіксує крок у 10⁻⁷° по всій планеті — тому координатні команди й точки місій\n"
             "шлють через *_INT, а не через float.")
    p.append(mtext(W/2, 300, concl, size=11.5, color=INK))
    render(os.path.join(OUT, "d-coord-scaling.svg"), W, H, *p)


# ── d-ack-fsm: автомат «команда → ACK» з усіма гілками ───────────────────────
def fig_ack_fsm():
    W, H = 860, 430
    p = []
    p.append(text(W/2, 28, "Автомат відправника: команда → ACK", size=16, bold=True))

    # стани
    send = fitbox(60, 70, 200, 54, "Надіслати кадр\n(confirmation = № спроби)", size=11.5, fill=HDR, stroke=HDR_STK)
    wait = fitbox(60, 170, 200, 54, "Чекати ACK\n(таймер + читати потік)", size=11.5, fill=FILL, stroke=LINE)
    p.append(send); p.append(wait)
    p.append(arrow(160, 124, 160, 170, color=INK))

    # гілка: прийшов ACK з потрібним command
    p.append(arrow(260, 197, 380, 197, color=FIELD, sw=1.8))
    p.append(text(320, 189, "ACK, command збігся", size=10.5, color=FIELD))
    dec = fitbox(380, 170, 180, 54, "Який result?", size=12, fill=PAY, stroke=PAY_STK)
    p.append(dec)

    # результати
    res = [
        ("ACCEPTED / DENIED /\nUNSUPPORTED / FAILED", "остаточно — вихід, віддати код", PAY, PAY_STK, 70),
        ("IN_PROGRESS", "відсунути дедлайн, чекати далі", SIG, SIG_STK, 170),
        ("TEMPORARILY_REJECTED", "зайнятий — коротка пауза, повтор", SIG, SIG_STK, 270),
    ]
    for label, act, fl, st, y in res:
        p.append(fitbox(620, y, 210, 54, label + "\n" + act, size=10.5, fill=fl, stroke=st))
    p.append(arrow(560, 190, 620, 100, color=INK, sw=1.4))
    p.append(arrow(560, 197, 620, 197, color=INK, sw=1.4))
    p.append(arrow(560, 204, 620, 290, color=INK, sw=1.4))

    # гілка таймауту
    p.append(arrow(120, 224, 120, 300, color=POS, sw=1.8))
    p.append(text(126, 268, "таймаут", size=10.5, color=POS, anchor="start"))
    tmo = fitbox(60, 300, 200, 54, "Спроб < max_tries?", size=12, fill=CRC, stroke=CRC_STK)
    p.append(tmo)
    # так → назад до Надіслати (confirmation+1)
    p.append(arrow(60, 314, 30, 314, color=INK, sw=1.4))
    p.append(line(30, 314, 30, 97, color=INK, sw=1.4))
    p.append(arrow(30, 97, 60, 97, color=INK, sw=1.4))
    p.append(text(24, 210, "так: confirmation+1", size=10, color=MUTED, anchor="middle"))
    # ні → здатися
    p.append(arrow(260, 327, 380, 327, color=POS, sw=1.8))
    p.append(text(320, 319, "ні", size=10.5, color=POS))
    p.append(fitbox(380, 300, 180, 54, "Здатися: −1 нагору\n(лінк мертвий)", size=11, fill=CRC, stroke=CRC_STK))

    concl = ("Дві опори коректності: ACK беруть лише той, у якого поле command збіглося з надісланим "
             "(інакше чужий ACK видасть себе за свій), і саму дію тримають ідемпотентною, щоб зайвий\n"
             "повтор після загубленого ACK не виконав її вдруге.")
    p.append(mtext(W/2, 400, concl, size=11, color=INK))
    render(os.path.join(OUT, "d-ack-fsm.svg"), W, H, *p)


# ── d-routing: адресація й ретрансляція в системі MAVLink ─────────────────────
def fig_routing():
    W, H = 820, 340
    p = []
    p.append(text(W/2, 28, "Адресація: system / component і ретрансляція", size=16, bold=True))

    # GCS
    p.append(fitbox(40, 90, 150, 70, "Наземна станція\nsys 255", size=12, fill=HDR, stroke=HDR_STK))
    # борт (система дрона з кількома компонентами)
    p.append(rect(360, 70, 300, 200, fill="#f7f9ff", stroke=HDR_STK, sw=1.5))
    p.append(text(510, 92, "Апарат — система sys 1", size=12.5, bold=True))
    p.append(fitbox(380, 110, 120, 48, "автопілот\ncomp 1", size=11, fill=PAY, stroke=PAY_STK))
    p.append(fitbox(520, 110, 120, 48, "камера\ncomp 100", size=11, fill=FILL, stroke=LINE))
    p.append(fitbox(380, 175, 120, 48, "бортовий ПК\ncomp 191", size=11, fill=FILL, stroke=LINE))
    p.append(fitbox(520, 175, 120, 48, "давач\ncomp 158", size=11, fill=FILL, stroke=LINE))

    p.append(arrow(190, 118, 360, 130, color=POS, sw=2.0))
    p.append(text(275, 108, "target sys=1, comp=1", size=10.5, color=POS))
    p.append(arrow(360, 150, 190, 138, color=FIELD, sw=1.6))
    p.append(text(275, 168, "HEARTBEAT від кожного comp", size=10, color=FIELD))

    concl = ("Кожне повідомлення має адресу відправника (sysid/compid у заголовку) і — для команд — адресу "
             "отримувача (target_system/target_component у тілі). target=0 означає «всім». Маршрутизатор на\n"
             "борту роздає кадр потрібному компонентові; тому команду камері й команду автопілоту не сплутати.")
    p.append(mtext(W/2, 305, concl, size=11, color=INK))
    render(os.path.join(OUT, "d-routing.svg"), W, H, *p)


# ── d-param-sync: проблема синхронізації при читанні всіх параметрів ──────────
def fig_param_sync():
    W, H = 820, 330
    p = []
    p.append(text(W/2, 28, "Читання всіх параметрів: як ловлять пропуск", size=16, bold=True))

    p.append(fitbox(40, 70, 180, 50, "PARAM_REQUEST_LIST", size=11.5, fill=HDR, stroke=HDR_STK))
    p.append(arrow(220, 95, 300, 95, color=POS, sw=1.6))

    # стрічка PARAM_VALUE з пропуском
    labels = ["idx 0\ncount 812", "idx 1", "idx 2", "×\nвтрачено", "idx 4", "…", "idx 811"]
    x = 300
    for i, lab in enumerate(labels):
        fl, st = (CRC, CRC_STK) if "×" in lab else (PAY, PAY_STK)
        p.append(fitbox(x, 72, 66, 48, lab, size=9.5, fill=fl, stroke=st))
        x += 70
    p.append(text(510, 140, "кожен PARAM_VALUE несе param_count = 812 і свій param_index", size=11, color=MUTED))

    calc = ("Приймач заводить масив на count позицій. Прийшло 811 із 812 → у позиції 3 діра. "
            "Замість повторювати ВЕСЬ список, він шле точковий PARAM_REQUEST_READ (index = 3) —\n"
            "і добирає лише пропущене. Так довгий список сходиться навіть на ненадійному лінку.")
    p.append(mtext(W/2, 195, calc, size=11.5, color=INK))

    p.append(fitbox(300, 245, 220, 48, "PARAM_REQUEST_READ\nparam_index = 3", size=11, fill=SIG, stroke=SIG_STK))
    p.append(arrow(520, 269, 600, 269, color=POS, sw=1.6))
    p.append(fitbox(600, 245, 150, 48, "PARAM_VALUE\nidx 3", size=11, fill=PAY, stroke=PAY_STK))
    render(os.path.join(OUT, "d-param-sync.svg"), W, H, *p)


if __name__ == "__main__":
    fig_frame()
    fig_crc_extra()
    fig_coord_scaling()
    fig_ack_fsm()
    fig_routing()
    fig_param_sync()
    print("OK d-figs ->", OUT)
