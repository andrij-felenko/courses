# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"
GREY_FILL = "#eeeeee"


# ── 1. Пісковий годинник: фабрики → ядро цілі → backstore ──────────────────
def fig_target_hourglass():
    W = 1660
    LX, CW = 230, 1400
    p = []

    fab = [
        "iSCSI\niscsi_target_mod",
        "Fibre Channel\ntcm_qla2xxx",
        "InfiniBand SRP\nib_srpt",
        "віртмашина\nvhost_scsi",
        "своя ж машина\ntcm_loop",
        "USB-кабель\ntcm_usb_gadget",
    ]
    fw, fgap, fy, fh = 220, 15, 30, 80
    for i, s in enumerate(fab):
        x = LX + i * (fw + fgap)
        p.append(fitbox(x, fy, fw, fh, s, size=15, fill=BLUE_FILL, stroke=NEG))
        p.append(arrow(x + fw / 2, fy + fh, x + fw / 2, 176))

    cy, ch = 180, 110
    p.append(fitbox(LX, cy, CW, ch,
                    "ядро цілі — target_core_mod\n"
                    "який mapped LUN бачить цей сеанс · емуляція INQUIRY, READ CAPACITY, REPORT LUNS\n"
                    "резервації · unit attention · стан ALUA · черга команд",
                    size=17, fill=GREEN_FILL, stroke=FIELD))

    bs = [
        ("iblock\nbio просто в чергу пристрою", "/dev/sdb, том LVM"),
        ("fileio\nчитання й запис у файл", "disk.img на ext4"),
        ("rd_mcp\nсторінки в оперативці", "RAM цієї машини"),
        ("pscsi\nCDB далі як є, без емуляції", "справжній стример"),
        ("user (TCMU)\nдемон у просторі користувача", "Ceph RBD, Gluster"),
    ]
    bw, bstep, by, bh = 267, 283, 360, 86
    ry, rh = 500, 70
    for i, (s, real) in enumerate(bs):
        x = LX + i * bstep
        p.append(arrow(x + bw / 2, cy + ch, x + bw / 2, by - 4))
        p.append(fitbox(x, by, bw, bh, s, size=15, fill=WARM_FILL, stroke=WARM))
        p.append(arrow(x + bw / 2, by + bh, x + bw / 2, ry - 4))
        p.append(fitbox(x, ry, bw, rh, real, size=15, fill=GREY_FILL, stroke=LINE))

    p.append(text(205, fy + fh / 2 + 5, "фабрики", size=16, color=MUTED, anchor="end", bold=True))
    p.append(text(205, cy + ch / 2 + 5, "ядро цілі", size=16, color=MUTED, anchor="end", bold=True))
    p.append(text(205, by + bh / 2 + 5, "backstore", size=16, color=MUTED, anchor="end", bold=True))
    p.append(text(205, ry + rh / 2 + 5, "де насправді байти", size=16, color=MUTED, anchor="end", bold=True))

    render(os.path.join(IMG, 'target-hourglass.svg'), W, ry + rh + 30, *p)


# ── 2. Шлях однієї команди WRITE ───────────────────────────────────────────
def fig_write_path():
    W = 1000
    BX, BW, BH, STEP = 140, 720, 64, 96
    p = []

    FAB = (BLUE_FILL, NEG)
    CORE = (GREEN_FILL, FIELD)
    BACK = (WARM_FILL, WARM)

    steps = [
        (FAB, "iscsi_target_mod розбирає PDU:\nз нього виймається CDB — WRITE(10), LBA, довжина"),
        (CORE, "чий це сеанс і який mapped LUN\nкоманда до LUN, не вписаного в ACL, далі не йде"),
        (CORE, "таблиця емуляції: INQUIRY ядро відповіло б саме,\nа WRITE передає вниз — але спершу потрібні дані"),
        (FAB, "write_pending: фабрика просить дані\nв iSCSI це R2T, за ним — пакети data-out"),
        (BACK, "iblock складає сторінки в bio\nі кладе його в чергу блокового пристрою"),
        (BACK, "bio завершився — колбек будить команду\nі повідомляє, чи все записалось"),
        (CORE, "статус: GOOD або CHECK CONDITION\nіз сенс-кодом, який пояснює, що не так"),
        (FAB, "queue_status: відповідь пакується назад у PDU\nі йде тим самим сокетом"),
    ]

    y = 30
    for i, ((f, st), s) in enumerate(steps):
        p.append(fitbox(BX, y, BW, BH, s, size=15, fill=f, stroke=st))
        if i < len(steps) - 1:
            p.append(arrow(BX + BW / 2, y + BH, BX + BW / 2, y + STEP - 4))
        y += STEP

    ly = y + 20
    for i, ((f, st), nm) in enumerate([(FAB, "фабрика"), (CORE, "ядро цілі"), (BACK, "backstore")]):
        p.append(fitbox(BX + i * 250, ly, 220, 52, nm, size=16, bold=True, fill=f, stroke=st))

    render(os.path.join(IMG, 'write-path.svg'), W, ly + 52 + 30, *p)


# ── 3. Ідентичність LUN: коли злиття правильне і коли згубне ───────────────
def fig_lun_identity():
    W = 1500
    PW = 690
    PA, PB = 30, 780
    p = []

    def panel(px, title, tfill, tstroke, rows):
        p.append(fitbox(px, 25, PW, 46, title, size=17, bold=True, fill=tfill, stroke=tstroke))
        for r in rows:
            p.append(r)

    half_w, half_l, half_r = 290, 30, 370

    def two(px, y, h, s1, s2, f, st):
        return [fitbox(px + half_l, y, half_w, h, s1, size=15, fill=f, stroke=st),
                fitbox(px + half_r, y, half_w, h, s2, size=15, fill=f, stroke=st)]

    def wide(px, y, h, s, f, st):
        return fitbox(px + 30, y, PW - 60, h, s, size=16, fill=f, stroke=st)

    # ── панель А: один LUN, два шляхи
    rows = [wide(PA, 100, 56, "на цілі один backstore — disk1", GREY_FILL, LINE)]
    rows += two(PA, 190, 52, "портал на eth0", "портал на eth1", BLUE_FILL, NEG)
    rows += two(PA, 280, 52, "/dev/sdb", "/dev/sdc", GREY_FILL, LINE)
    rows += [wide(PA, 370, 56, "designator у VPD 0x83 однаковий", GREEN_FILL, FIELD),
             wide(PA, 460, 56, "dm-0: один диск, два шляхи", GREEN_FILL, FIELD)]
    rows += [arrow(PA + 345, 156, PA + half_l + half_w / 2, 186),
             arrow(PA + 345, 156, PA + half_r + half_w / 2, 186),
             arrow(PA + half_l + half_w / 2, 242, PA + half_l + half_w / 2, 276),
             arrow(PA + half_r + half_w / 2, 242, PA + half_r + half_w / 2, 276),
             arrow(PA + half_l + half_w / 2, 332, PA + 250, 366),
             arrow(PA + half_r + half_w / 2, 332, PA + 440, 366),
             arrow(PA + 345, 426, PA + 345, 456)]
    panel(PA, "як має бути", GREEN_FILL, FIELD, rows)

    # ── панель Б: два різні LUN з тим самим серійником
    rows = two(PB, 100, 56, "сервер A: disk1", "сервер B: disk2", GREY_FILL, LINE)
    rows += [wide(PB, 190, 52, "конфіг склоновано — той самий vpd_unit_serial", RED_FILL, POS)]
    rows += two(PB, 280, 52, "/dev/sdb", "/dev/sdc", GREY_FILL, LINE)
    rows += [wide(PB, 370, 56, "multipath зливає їх в один dm-0", RED_FILL, POS),
             wide(PB, 460, 56, "записи розлітаються — биті обидва", RED_FILL, POS)]
    rows += [arrow(PB + half_l + half_w / 2, 156, PB + 250, 186),
             arrow(PB + half_r + half_w / 2, 156, PB + 440, 186),
             arrow(PB + 250, 242, PB + half_l + half_w / 2, 276),
             arrow(PB + 440, 242, PB + half_r + half_w / 2, 276),
             arrow(PB + half_l + half_w / 2, 332, PB + 250, 366),
             arrow(PB + half_r + half_w / 2, 332, PB + 440, 366),
             arrow(PB + 345, 426, PB + 345, 456)]
    panel(PB, "та сама помилка в конфігу", RED_FILL, POS, rows)

    render(os.path.join(IMG, 'lun-identity.svg'), W, 546, *p)


# ── 4. Вікна, у яких атрибути ще можна міняти ──────────────────────────────
def fig_attr_windows():
    W = 1560
    E = [400, 700, 1000, 1300]      # межі подій
    X0, X1 = 270, 1480              # ліва й права межі доріжок
    p = []

    ev = [
        "mkdir core/fileio_0/disk1\nобʼєкт у ядрі є, ще не налаштований",
        "echo 1 > enable\nblock_size ← hw_block_size",
        "ln -s … lun/lun_0/store\nexport_count = 1",
        "iscsiadm --login\nсеанс живий, є /dev/sdX",
    ]
    ey, eh, ew = 25, 74, 268
    for x, s in zip(E, ev):
        p.append(fitbox(x - ew / 2, ey, ew, eh, s, size=14, fill=BLUE_FILL, stroke=NEG))

    LY, LH, LSTEP = 140, 58, 88
    bottom = LY + 2 * LSTEP + LH
    for x in E:
        p.append(line(x, ey + eh, x, bottom + 12, color=MUTED, sw=1.2, dash="5,5"))

    GREEN, GREY, RED = (GREEN_FILL, FIELD), (GREY_FILL, LINE), (RED_FILL, POS)

    lanes = [
        ("attrib/block_size", [
            (X0, E[1], "ще нема сенсу", GREY),
            (E[1], E[2], "тут і тільки тут", GREEN),
            (E[2], X1, "EINVAL: export_count", RED),
        ]),
        ("wwn/vpd_unit_serial", [
            (X0, E[2], "власний серійник — поки не експортовано", GREEN),
            (E[2], X1, "EINVAL: export_count", RED),
        ]),
        ("attrib/emulate_write_cache", [
            (X0, X1, "будь-коли; хост побачить після rescan", GREEN),
        ]),
    ]
    for i, (nm, segs) in enumerate(lanes):
        y = LY + i * LSTEP
        p.append(text(X0 - 26, y - 12, nm, size=15, color=MUTED, anchor="end", bold=True))
        for a, b, s, (f, st) in segs:
            p.append(fitbox(a + 4, y, b - a - 8, LH, s, size=14, fill=f, stroke=st))

    ly = bottom + 34
    for i, (s, (f, st)) in enumerate([
        ("міняти можна", GREEN), ("міняти можна, але марно", GREY), ("ядро відмовить", RED)
    ]):
        p.append(fitbox(X0 + i * 300, ly, 280, 46, s, size=14, fill=f, stroke=st))

    render(os.path.join(IMG, 'attr-windows.svg'), W, ly + 46 + 26, *p)


fig_target_hourglass()
fig_write_path()
fig_lun_identity()
fig_attr_windows()
print("ok")
