# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"


# ── 1. Заголовок = службові поля + три вказівники ──────────────────────────
def fig_envelope():
    W, H = 1200, 700
    p = []

    p.append(text(300, 42, "заголовок sg_io_hdr_t", size=17, bold=True))
    p.append(text(300, 68, "ці поля ядро читає й розуміє", size=13, color=MUTED))
    p.append(text(930, 42, "пам'ять процесу", size=17, bold=True))
    p.append(text(930, 68, "ці байти ядро лише переносить", size=13, color=MUTED))

    fields = [
        "interface_id = 'S'",
        "dxfer_direction = FROM_DEV",
        "cmd_len = 6",
        "dxfer_len = 96",
        "mx_sb_len = 32",
        "timeout = 5000 мс",
    ]
    y = 100
    for s in fields:
        p.append(fitbox(90, y, 420, 42, s, size=14, fill=GREY))
        y += 52

    ptrs = [
        ("cmdp →", "команда пристрою (CDB)", "12 00 00 00 60 00", WARM),
        ("dxferp →", "буфер даних", "96 байтів відповіді", GREEN),
        ("sbp →", "звіт пристрою", "сенс-дані, до 32 байтів", BLUE),
    ]
    ys = [440, 520, 600]
    for (name, what, inside, col), yy in zip(ptrs, ys):
        p.append(fitbox(90, yy, 420, 56, name, size=15, bold=True, fill=GREY))
        p.append(fitbox(720, yy - 10, 420, 76, what + "\n" + inside, size=14, fill=col))
        p.append(arrow(520, yy + 28, 710, yy + 28))

    return render(os.path.join(IMG, 'envelope.svg'), W, H, *p)


# ── 2. Дві дороги через блоковий шар ───────────────────────────────────────
def fig_two_paths():
    W, H = 1260, 850
    p = []
    xl, xr = 300, 820

    p.append(fitbox(100, 40, 400, 64,
                    "звичайне читання\nread(fd, …)", size=16, bold=True, fill=GREEN))
    p.append(fitbox(620, 40, 400, 64,
                    "наскрізна команда\nioctl(fd, SG_IO, …)", size=16, bold=True, fill=WARM))

    stages = ["кеш сторінок",
              "зсув розділу",
              "злиття сусідніх запитів",
              "планувальник і облік cgroup"]
    y = 150
    for label in stages:
        p.append(arrow(xl, y - 34, xl, y - 6))
        p.append(fitbox(100, y, 400, 58, label, size=15, fill=GREY))
        y += 92

    p.append(fitbox(620, 150, 400, 334,
                    "жоден із цих шарів\nне бачить команди:\nвміст конверта невідомий",
                    size=15, fill="#ffffff", color=MUTED, stroke=MUTED))

    y_common = 560
    p.append(arrow(xl, 484, xl, y_common - 6))
    p.append(arrow(xr, 110, xr, 146))
    p.append(arrow(xr, 488, xr, y_common - 6))

    p.append(fitbox(100, y_common, 920, 68,
                    "запит у черзі пристрою: тег, сторінки процесу, драйвер",
                    size=15, bold=True, fill=BLUE))

    p.append(text(xl, 672, "REQ_OP_READ", size=15, bold=True, color=FIELD))
    p.append(text(xr, 672, "REQ_OP_DRV_IN", size=15, bold=True, color=POS))
    p.append(text(560, 706, "тип операції — єдина різниця, яку бачить драйвер",
                  size=13, color=MUTED))

    p.append(arrow(560, 722, 560, 754))
    p.append(fitbox(380, 758, 360, 58, "пристрій", size=16, bold=True, fill=WARM))

    return render(os.path.join(IMG, 'two-paths.svg'), W, H, *p)


# ── 3. Конверт у конверті: ATA під SCSI ────────────────────────────────────
def fig_nested():
    W, H = 1220, 720
    p = []

    p.append(text(610, 42, "туди: кожен шар розпечатує рівно один конверт",
                  size=16, bold=True))

    p.append(rect(120, 76, 980, 202, fill="#ffffff"))
    p.append(text(160, 106, "заголовок sg_io_hdr_t", size=14, bold=True, anchor="start"))
    p.append(rect(210, 122, 800, 138, fill=WARM))
    p.append(text(250, 152, "CDB: 85h ATA PASS-THROUGH (16)", size=14, bold=True, anchor="start"))
    p.append(fitbox(280, 170, 690, 72,
                    "регістри ATA: SECTOR_COUNT=1, COMMAND=ECh (IDENTIFY DEVICE)",
                    size=14, fill=GREEN))

    rows = [
        (330, "ядро", "дивиться лише на перший байт CDB"),
        (420, "libata — шар трансляції SAT", "розбирає CDB і виставляє регістри на дріт"),
        (510, "диск SATA", "бачить самі регістри, про SCSI не знає"),
    ]
    for y, who, what in rows:
        p.append(fitbox(120, y, 360, 62, who, size=15, bold=True, fill=GREY))
        p.append(fitbox(520, y, 580, 62, what, size=14, fill="#ffffff"))
    p.append(arrow(300, 282, 300, 324))
    p.append(arrow(300, 394, 300, 414))
    p.append(arrow(300, 484, 300, 504))

    p.append(text(610, 622, "назад: регістри повертаються під виглядом відмови",
                  size=16, bold=True))
    p.append(fitbox(120, 642, 440, 54, "у CDB виставлено CK_COND = 1",
                    size=15, bold=True, fill=BLUE))
    p.append(arrow(572, 669, 616, 669))
    p.append(fitbox(628, 642, 472, 54,
                    "CHECK CONDITION, регістри — у сенс-даних", size=14, fill=RED))

    return render(os.path.join(IMG, 'nested.svg'), W, H, *p)


# ── 4. Чий це вирок: канал, дорога чи пристрій ─────────────────────────────
def fig_verdict():
    W, H = 1240, 700
    p = []

    p.append(text(620, 40, "одна невдача — чотири різні винуватці", size=17, bold=True))

    rows = [
        ("ioctl(...) < 0",
         "КАНАЛ: команда навіть не поїхала\nENOTTY, EINVAL, EFAULT — дивись errno", RED),
        ("host_status ≠ 0",
         "ДОРОГА: строк вийшов, шлях зник,\nконтролер скинув пристрій", WARM),
        ("status = 02h, sb_len_wr > 0",
         "ПРИСТРІЙ: він відповів, і відповідь —\nвідмова; причина в сенс-даних", BLUE),
        ("ASC/ASCQ = 00h / 1Dh",
         "ЦЕ НЕ ВІДМОВА: так повертаються\nрегістри ATA, коли виставлено CK_COND", GREEN),
    ]
    y = 90
    for cond, verdict, col in rows:
        p.append(fitbox(70, y, 420, 96, cond, size=15, bold=True, fill=GREY))
        p.append(arrow(500, y + 48, 596, y + 48))
        p.append(fitbox(610, y, 560, 96, verdict, size=14, fill=col))
        y += 130

    p.append(text(620, 640, "driver_status у сучасних ядрах несе лише DRIVER_SENSE —",
                  size=13, color=MUTED))
    p.append(text(620, 664, "як вирок про дорогу його читати не можна",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, 'verdict.svg'), W, H, *p)


# ── 5. Де в сенс-даних лежать регістри ATA ─────────────────────────────────
def fig_sense_map():
    W, H = 1300, 620
    p = []

    p.append(text(650, 40, "буфер сенс-даних після SMART RETURN STATUS із CK_COND",
                  size=17, bold=True))

    p.append(text(330, 84, "заголовок, байти 0–7", size=15, bold=True))
    head = [
        "0 : 72h — описовий формат",
        "1 : ключ 01h — RECOVERED ERROR",
        "2 : ASC  00h",
        "3 : ASCQ 1Dh — «є дані ATA»",
        "7 : довжина решти буфера",
    ]
    y = 108
    for s in head:
        p.append(fitbox(70, y, 520, 52, s, size=14, fill=GREY))
        y += 62

    p.append(arrow(600, 380, 690, 380))

    p.append(text(985, 84, "описовий блок, байти 8–21", size=15, bold=True))
    desc = [
        ("8  : 09h — ATA Status Return", GREY),
        ("9  : 0Ch — довжина решти блока", GREY),
        ("11 : регістр ERROR", GREY),
        ("13 : регістр SECTOR_COUNT", GREY),
        ("15 : регістр LBA_LOW", GREY),
        ("17 : регістр LBA_MID   → 4Fh або F4h", RED),
        ("19 : регістр LBA_HIGH  → C2h або 2Ch", RED),
        ("21 : регістр STATUS", GREEN),
    ]
    y = 108
    for s, col in desc:
        p.append(fitbox(700, y, 530, 52, s, size=14, fill=col))
        y += 62

    return render(os.path.join(IMG, 'sense-map.svg'), W, H, *p)


if __name__ == '__main__':
    fig_envelope()
    fig_two_paths()
    fig_nested()
    fig_verdict()
    fig_sense_map()
    print("ok")
