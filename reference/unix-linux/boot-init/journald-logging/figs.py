# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"


# ── 1. Анатомія запису: хто яке поле заповнив ───────────────────────────────
def fig_entry_anatomy():
    W, H = 1320, 620
    p = []

    p.append(text(660, 40, "одне повідомлення — два джерела полів", size=17, bold=True))

    # джерела
    p.append(fitbox(50, 96, 330, 96,
                    "процес\nрядки FIELD=значення,\nяких він хоче",
                    size=15, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(50, 256, 330, 96,
                    "ядро разом із датаграмою\nдодає pid, uid, gid\nвідправника",
                    size=15, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(50, 416, 330, 96,
                    "/proc за цим pid:\ncomm, exe, cmdline,\nконтрольна група",
                    size=15, fill=GREEN_FILL, stroke=FIELD))

    # демон
    p.append(fitbox(444, 244, 190, 120, "systemd-\njournald", size=17, bold=True,
                    fill=WARM_FILL, stroke=MUTED))

    p.append(arrow(384, 144, 440, 268))
    p.append(arrow(384, 304, 440, 304))
    p.append(arrow(384, 464, 440, 340))
    p.append(arrow(638, 304, 700, 304))

    # запис
    p.append(rect(706, 66, 570, 500, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(991, 100, "запис у журналі", size=16, bold=True))

    p.append(text(991, 130, "написав відправник — може бути яким завгодно", size=13, color=MUTED))
    own = ["MESSAGE=Accepted publickey for deploy",
           "PRIORITY=6",
           "MESSAGE_ID=8daee1d3b9a04f8e…",
           "SYSLOG_IDENTIFIER=sshd"]
    y = 142
    for s in own:
        p.append(fitbox(730, y, 522, 32, s, size=13, fill=BLUE_FILL, stroke=NEG, sw=1.0))
        y += 36

    p.append(text(991, 316, "додав демон — відправник не міг це підмінити", size=13, color=MUTED))
    got = ["_PID=1187",
           "_UID=0",
           "_COMM=sshd",
           "_EXE=/usr/sbin/sshd",
           "_SYSTEMD_UNIT=sshd.service",
           "_BOOT_ID=4f2a…",
           "_TRANSPORT=journal"]
    y = 328
    for s in got:
        p.append(fitbox(730, y, 522, 32, s, size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.0))
        y += 33

    render(os.path.join(IMG, 'entry-anatomy.svg'), W, H, *p,
           title="Анатомія запису журналу")


# ── 2. Об'єкти у файлі журналу й шлях запиту ────────────────────────────────
def fig_journal_objects():
    W, H = 1320, 730
    p = []

    p.append(rect(40, 56, 1240, 306, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(660, 90, "запис не тримає тексту — лише зміщення на спільні об'єкти",
                  size=16, bold=True))

    p.append(fitbox(150, 116, 300, 68, "ENTRY\n03:14:07 · seq 5012",
                    size=14, fill=WARM_FILL, stroke=MUTED))
    p.append(fitbox(830, 116, 300, 68, "ENTRY\n03:14:09 · seq 5013",
                    size=14, fill=WARM_FILL, stroke=MUTED))

    p.append(fitbox(60, 258, 260, 76, "DATA\nMESSAGE=Accepted…",
                    size=13, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(370, 258, 300, 76, "DATA\n_SYSTEMD_UNIT=sshd.service",
                    size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(720, 258, 210, 76, "DATA\nPRIORITY=6",
                    size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(980, 258, 260, 76, "DATA\nMESSAGE=Disconnected…",
                    size=13, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(300, 184, 200, 252))
    p.append(arrow(300, 184, 510, 252))
    p.append(arrow(300, 184, 815, 252))
    p.append(arrow(980, 184, 1105, 252))
    p.append(arrow(980, 184, 530, 252))
    p.append(arrow(980, 184, 835, 252))

    p.append(rect(40, 402, 1240, 288, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(660, 436, "запит «усе від цієї служби» — жодного перегляду тексту",
                  size=16, bold=True))

    p.append(fitbox(70, 486, 250, 92, "хеш-таблиця даних\nхеш значення → об'єкт",
                    size=14, fill=GREY_FILL, stroke=MUTED))
    p.append(arrow(324, 532, 384, 532))
    p.append(fitbox(390, 486, 300, 92, "DATA\n_SYSTEMD_UNIT=sshd.service",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(694, 532, 754, 532))
    p.append(fitbox(760, 470, 470, 124,
                    "ланцюг масивів записів\nвпорядковані зміщення записів\nмасиви ростуть удвічі — звідси двійковий пошук",
                    size=14, fill=WARM_FILL, stroke=MUTED))

    p.append(text(660, 646, "друга умова — другий такий самий ланцюг, ідуть обома в ногу",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'journal-objects.svg'), W, H, *p,
           title="Об'єкти у файлі журналу")


# ── 3. Де журнал живе від вмикання до сталої роботи ─────────────────────────
def fig_journal_storage():
    W, H = 1300, 430
    p = []

    p.append(text(650, 44, "де лежать записи від вмикання живлення й далі", size=17, bold=True))

    boxes = [
        (40, "кільцевий буфер ядра\n\nповідомлення ядра\nчекають, поки демон\nвзагалі запуститься"),
        (350, "/run/log/journal\n\nце tmpfs, тобто пам'ять:\n/var ще не змонтовано,\nа писати треба вже"),
        (660, "/var/log/journal\n\nз'явився /var — служба\nперенесення переливає\nнакопичене й лишає там"),
        (970, "ротація й прибирання\n\nзапис не редагують,\nтому звільняють місце\nлише цілими файлами"),
    ]
    fills = [GREY_FILL, WARM_FILL, GREEN_FILL, BLUE_FILL]
    strokes = [MUTED, MUTED, FIELD, NEG]
    for (x, s), f, st in zip(boxes, fills, strokes):
        p.append(fitbox(x, 96, 290, 230, s, size=14, fill=f, stroke=st))

    p.append(arrow(334, 211, 344, 211))
    p.append(arrow(644, 211, 654, 211))
    p.append(arrow(954, 211, 964, 211))

    p.append(text(650, 380,
                  "перезавантаження переживе лише те, що встигли перенести в /var",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'journal-storage.svg'), W, H, *p,
           title="Де живе журнал")


# ── 4. Рідний протокол: байти однієї датаграми ─────────────────────────────
def fig_native_wire():
    W, H = 1360, 610
    p = []

    p.append(text(680, 40, "рідний протокол: що саме летить у сокет", size=17, bold=True))

    # ── ліворуч: звичайна датаграма
    p.append(rect(40, 70, 700, 508, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(390, 106, "датаграма з даними — це і є запис", size=15, bold=True))

    y = 130
    for s in ("MESSAGE=не вдалося відкрити сокет\\n",
              "PRIORITY=3\\n",
              "ORDER_ID=8841\\n"):
        p.append(fitbox(70, y, 640, 40, s, size=14, fill=BLUE_FILL, stroke=NEG, sw=1.0))
        y += 46

    p.append(text(390, y + 20, "значення з переносом рядка — лише другою формою:",
                  size=13, color=MUTED))
    y += 38
    x = 70
    for s, w in (("TRACE\\n", 140),
                 ("довжина значення:\n8 байтів, молодший перший", 262),
                 ("байти значення,\nяк вони є", 178),
                 ("\\n", 50)):
        p.append(fitbox(x, y, w, 66, s, size=13, fill=WARM_FILL, stroke=MUTED, sw=1.0))
        x += w + 10
    y += 82

    p.append(fitbox(70, y, 640, 42, "\\n     порожній рядок — тут запис скінчився",
                    size=14, fill=GREY_FILL, stroke=MUTED, sw=1.0))
    y += 62
    p.append(text(390, y, "поле з підкресленням, надіслане клієнтом, демон відкидає",
                  size=13, color=MUTED))

    # ── праворуч: запис не вліз
    p.append(rect(780, 70, 540, 508, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(1050, 106, "запис не вліз у датаграму", size=15, bold=True))

    p.append(fitbox(810, 132, 480, 58, "send() → EMSGSIZE",
                    size=14, fill=GREY_FILL, stroke=MUTED))
    p.append(arrow(1050, 194, 1050, 224))
    p.append(fitbox(810, 230, 480, 76, "друга спроба: датаграма\nз порожніми даними",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(1050, 310, 1050, 340))
    p.append(fitbox(810, 346, 480, 76, "SCM_RIGHTS: рівно один\nдескриптор і жодного більше",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(1050, 426, 1050, 456))
    p.append(fitbox(810, 462, 480, 88, "memfd, запечатаний від змін:\nусередині ті самі байти\nтією самою розкладкою",
                    size=14, fill=WARM_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'native-wire.svg'), W, H, *p,
           title="Байтова розкладка рідного протоколу journald")


# ── 5. Де стоїть покажчик читання ──────────────────────────────────────────
def fig_read_pointer():
    W, H = 1320, 430
    p = []

    p.append(text(660, 40, "seek лише наводить, next робить запис поточним",
                  size=17, bold=True))
    p.append(text(660, 70, "після будь-якого seek поточного запису ще немає — покажчик стоїть у проміжку",
                  size=13, color=MUTED))

    xs = [150, 360, 570, 780, 990]
    BW, BH, BY = 170, 88, 186
    labels = ["запис 1", "запис 2",
              "запис 3\nсаме на нього вказує\nзбережений курсор",
              "запис 4", "запис 5"]
    for x, s in zip(xs, labels):
        cursor_box = s.startswith("запис 3")
        p.append(fitbox(x, BY, BW, BH, s, size=14,
                        fill=GREEN_FILL if cursor_box else BLUE_FILL,
                        stroke=FIELD if cursor_box else NEG))

    gaps = [130, 340, 550, 760, 970, 1180]
    for g in gaps:
        p.append(line(g, 162, g, 296, color=MUTED, sw=1.4, dash="5 5"))

    # куди веде кожен seek
    for lx, gx, s in ((150, 130, "seek_head()"),
                      (550, 550, "seek_cursor(c)"),
                      (1180, 1180, "seek_tail()")):
        p.append(text(lx, 118, s, size=14, bold=True))
        p.append(arrow(lx, 128, gx, 158))

    p.append(arrow(132, 336, 226, 336))
    p.append(text(248, 341, "sd_journal_next() — запис 1 стає поточним",
                  size=13, anchor="start"))

    p.append(arrow(1180, 386, 880, 386))
    p.append(text(858, 391, "sd_journal_previous_skip(2) від хвоста — запис 4",
                  size=13, anchor="end"))

    render(os.path.join(IMG, 'read-pointer.svg'), W, H, *p,
           title="Покажчик читання й функції переміщення")


# ── 6. Перезапуск читача: три випадки після seek_cursor ────────────────────
def fig_restart_cursor():
    W, H = 1300, 520
    p = []

    p.append(text(650, 40, "перезапуск читача: три випадки після збереженого курсора",
                  size=17, bold=True))

    p.append(fitbox(390, 74, 520, 62,
                    "sd_journal_seek_cursor(збережений)\n+ sd_journal_next()",
                    size=15, bold=True, fill=WARM_FILL, stroke=MUTED))

    cols = [
        (40, GREY_FILL, MUTED,
         "next() повернув 0\n\nставати нема на що:\nжурнал порожній або\nобрізаний до курсора\n→ просто чекаємо"),
        (460, GREEN_FILL, FIELD,
         "test_cursor() > 0\n\nце той самий запис,\nвін уже оброблений\n→ нічого не робимо,\nнаступний next() дасть новий"),
        (880, BLUE_FILL, NEG,
         "test_cursor() == 0\n\nзапис прибрано ротацією;\nстоїмо на найближчому за часом\n→ обробляємо його\nі кажемо про пропуск уголос"),
    ]
    for x, fill, stroke, s in cols:
        p.append(fitbox(x, 210, 380, 156, s, size=14, fill=fill, stroke=stroke))

    p.append(arrow(600, 142, 232, 204))
    p.append(arrow(650, 142, 650, 204))
    p.append(arrow(700, 142, 1068, 204))

    p.append(fitbox(40, 412, 1220, 68,
                    "ні дубліката, ні тихого пропуску — тому курсор зберігають ПІСЛЯ обробки запису",
                    size=15, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, 'restart-cursor.svg'), W, H, *p,
           title="Відновлення позиції читача за курсором")


if __name__ == "__main__":
    fig_entry_anatomy()
    fig_journal_objects()
    fig_journal_storage()
    fig_native_wire()
    fig_read_pointer()
    fig_restart_cursor()
    print("ok")
