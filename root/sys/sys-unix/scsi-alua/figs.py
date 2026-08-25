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
RED_FILL = "#fdecea"
GREY_FILL = "#eceff1"
WHITE_FILL = "#ffffff"


# ── 1. Архітектура двоконтролерного сховища та асиметрія шляхів ───────────────
def fig_alua_dual_controller_arch():
    W, H = 1680, 960
    p = []

    # Хост зверху
    hx = 840
    srv, sw, sh = textbox(hx, 90, ["Хост-ініціатор (сервер)", "Блоковий рівень: dm-multipath"],
                          size=15, pad=16, fill=GREY_FILL, stroke=LINE, bold=True)
    p.append(srv)

    hba1_x, hba2_x = 420, 1260
    hba1, h1w, h1h = textbox(hba1_x, 210, ["HBA Порт 1 (/dev/sdb, /dev/sdc)"],
                             size=13, pad=14, fill=WHITE_FILL, stroke=LINE)
    hba2, h2w, h2h = textbox(hba2_x, 210, ["HBA Порт 2 (/dev/sdd, /dev/sde)"],
                             size=13, pad=14, fill=WHITE_FILL, stroke=LINE)
    p.append(hba1)
    p.append(hba2)
    p.append(arrow(hx - 140, 90 + sh / 2, hba1_x, 210 - h1h / 2))
    p.append(arrow(hx + 140, 90 + sh / 2, hba2_x, 210 - h2h / 2))

    # Контролери сховища
    c1_x, c2_x = 380, 1300

    # Контролер A (Власник LUN)
    c1_bg = rect(80, 310, 600, 320, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=8)
    p.append(c1_bg)
    p.append(text(c1_x, 345, "Контролер A (Власник LUN 0 · Прямий доступ)", size=14, bold=True, color=FIELD))

    tpg1_box, t1w, t1h = textbox(c1_x, 425,
                                 ["Цільова група портів 1 (TPG 1)",
                                  "Стан: Active/Optimized (AO)",
                                  "Пріоритет: 50 · Прямий шлях до кешу й дисків"],
                                 size=13, pad=14, fill=WHITE_FILL, stroke=LINE)
    p.append(tpg1_box)

    c1_ports, cp1w, cp1h = textbox(c1_x, 565,
                                   ["Порт цілі 1 (sdb)        Порт цілі 2 (sdd)"],
                                   size=12, pad=12, fill=GREY_FILL, stroke=MUTED)
    p.append(c1_ports)
    p.append(arrow(c1_x, 425 + t1h / 2, c1_x, 565 - cp1h / 2))

    # Контролер B (Партнер)
    c2_bg = rect(1000, 310, 600, 320, fill=WARM_FILL, stroke=LINE, sw=1.5, rx=8)
    p.append(c2_bg)
    p.append(text(c2_x, 345, "Контролер B (Партнер · Проксі-доступ)", size=14, bold=True, color=INK))

    tpg2_box, t2w, t2h = textbox(c2_x, 425,
                                 ["Цільова група портів 2 (TPG 2)",
                                  "Стан: Active/Non-Optimized (ANO)",
                                  "Пріоритет: 10 · Проксі через шину NTB/PCIe"],
                                 size=13, pad=14, fill=WHITE_FILL, stroke=LINE)
    p.append(tpg2_box)

    c2_ports, cp2w, cp2h = textbox(c2_x, 565,
                                   ["Порт цілі 3 (sdc)        Порт цілі 4 (sde)"],
                                   size=12, pad=12, fill=GREY_FILL, stroke=MUTED)
    p.append(c2_ports)
    p.append(arrow(c2_x, 425 + t2h / 2, c2_x, 565 - cp2h / 2))

    # Міжконтролерна шина посередині
    p.append(line(680, 480, 1000, 480, color=POS, sw=3, dash="6 4"))
    ntb_box, ntw, nth = textbox(hx, 480, ["Міжконтролерна шина (PCIe NTB / CMI)", "Пересилання проксі-запитів і дзеркалення кешу"],
                                size=12, pad=11, fill=WHITE_FILL, stroke=POS, sw=1.5)
    p.append(ntb_box)

    # Стрілки від HBA до портів
    p.append(arrow(hba1_x, 210 + h1h / 2, c1_x - 70, 310, color=FIELD, sw=2))
    p.append(arrow(hba2_x - 30, 210 + h2h / 2, c1_x + 70, 310, color=FIELD, sw=2))
    p.append(arrow(hba1_x + 30, 210 + h1h / 2, c2_x - 70, 310, color=MUTED, sw=1.5))
    p.append(arrow(hba2_x, 210 + h2h / 2, c2_x + 70, 310, color=MUTED, sw=1.5))

    # Дискова підсистема знизу
    lun_box, lw, lh = textbox(hx, 820,
                              ["Логічний том LUN 0 (SAS Dual-Port дисковий масив)",
                               "Обидва контролери мають фізичний зв'язок із дисками,",
                               "але кешем і блокуваннями володіє Контролер A"],
                              size=14, pad=16, fill=RED_FILL, stroke=LINE, bold=True)
    p.append(lun_box)

    # Прямий зв'язок від A до дисків
    p.append(arrow(c1_x, 630, hx - 160, 820 - lh / 2, color=FIELD, sw=2.5))
    p.append(text(300, 720, "Прямий шлях: локальний кеш → диск (0.8 мс)", size=12, color=FIELD, bold=True))

    # Зв'язок від B (проксі)
    p.append(arrow(c2_x, 630, hx + 160, 820 - lh / 2, color=MUTED, sw=1.5))
    p.append(text(1380, 720, "Проксі-шлях: шина NTB → Контролер A (14 мс)", size=12, color=POS, bold=True))

    render(os.path.join(IMG, 'alua-dual-controller-arch.svg'), W, H, *p,
           title="Архітектура двоконтролерного сховища та асиметрія шляхів ALUA")


# ── 2. Стани цільових портів ALUA ───────────────────────────────────────────
def fig_alua_port_states():
    W, H = 1580, 960
    p = []

    # 5 станів
    # Active/Optimized (AO)
    ao_box, aow, aoh = textbox(380, 160,
                               ["Active/Optimized (00h)",
                                "Прямий оптимальний доступ",
                                "Усі SCSI-команди виконуються негайно",
                                "Пріоритет dm-multipath: 50"],
                               size=13, pad=15, fill=GREEN_FILL, stroke=FIELD, sw=2, bold=True)
    p.append(ao_box)

    # Active/Non-Optimized (ANO)
    ano_box, anow, anoh = textbox(1200, 160,
                                 ["Active/Non-Optimized (01h)",
                                  "Неоптимальний проксі-доступ",
                                  "Усі команди виконуються із затримкою",
                                  "Пріоритет dm-multipath: 10"],
                                 size=13, pad=15, fill=WARM_FILL, stroke=LINE, bold=True)
    p.append(ano_box)

    # Standby (SB)
    sb_box, sbw, sbh = textbox(380, 520,
                               ["Standby (02h)",
                                "Резервний стан контролера",
                                "I/O відхиляється: Sense 02h / 04h / 0Ah",
                                "Дозволені: INQUIRY, RTPG, TUR, STPG"],
                               size=13, pad=15, fill=BLUE_FILL, stroke=LINE, bold=True)
    p.append(sb_box)

    # Transitioning (TO)
    to_box, tow, toh = textbox(790, 340,
                               ["Transitioning (0Fh)",
                                "Тимчасова зміна стану контролера",
                                "Скидання кешу, міграція прав LUN",
                                "Sense: 02h / 04h / 0Ah (Rapid Transition)",
                                "Драйвер ядра чекає й повторює запит"],
                               size=13, pad=15, fill=RED_FILL, stroke=POS, sw=2, bold=True)
    p.append(to_box)

    # Unavailable (UN)
    un_box, unw, unh = textbox(1200, 520,
                               ["Unavailable (03h)",
                                "Порт недоступний для цього LUN",
                                "Аварія бекенду, ізоляція порту",
                                "Sense: 02h / 04h / 0Bh (Target Port Unavailable)",
                                "I/O неможливе, лише INQUIRY/RTPG"],
                               size=13, pad=15, fill=GREY_FILL, stroke=MUTED, sw=1.5, bold=True)
    p.append(un_box)

    # Стрілки переходів
    # AO <-> TO
    p.append(arrow(380 + aow / 2, 160 + 20, 790 - tow / 2, 340 - 20, color=POS, sw=1.5))
    p.append(arrow(790 - tow / 2, 340 - 40, 380 + aow / 2, 160, color=FIELD, sw=1.5))

    # ANO <-> TO
    p.append(arrow(1200 - anow / 2, 160 + 20, 790 + tow / 2, 340 - 20, color=POS, sw=1.5))
    p.append(arrow(790 + tow / 2, 340 - 40, 1200 - anow / 2, 160, color=FIELD, sw=1.5))

    # SB <-> TO
    p.append(arrow(380 + sbw / 2, 520 - 20, 790 - tow / 2, 340 + 20, color=POS, sw=1.5))
    p.append(arrow(790 - tow / 2, 340 + 40, 380 + sbw / 2, 520, color=FIELD, sw=1.5))

    # UN <-> TO
    p.append(arrow(1200 - unw / 2, 520 - 20, 790 + tow / 2, 340 + 20, color=POS, sw=1.5))
    p.append(arrow(790 + tow / 2, 340 + 40, 1200 - unw / 2, 520, color=FIELD, sw=1.5))

    # Прямий перехід між AO і ANO (Implicit ALUA)
    p.append(line(380 + aow / 2, 160 - 30, 1200 - anow / 2, 160 - 30, color=LINE, sw=1.5, dash="6 4"))
    p.append(text(790, 110, "Автономне перемикання сховища (Implicit transition)", size=12, color=MUTED, italic=True))

    # Нижня інформаційна панель
    info_box, infow, infoh = textbox(790, 800,
                                    ["Механізми керування станами портів цілі:",
                                     "• Неявний (Implicit): Сховище змінює стан самостійно; хост дізнається через Sense 06h / 2Ah / 06h",
                                     "• Явний (Explicit): Хост надсилає команду SET TARGET PORT GROUPS (STPG) для активації групи",
                                     "• Змішаний (Both): Сховище підтримує і автономні переходи, і команди примусового перемикання"],
                                    size=13, pad=18, fill=WHITE_FILL, stroke=LINE)
    p.append(info_box)

    render(os.path.join(IMG, 'alua-port-states.svg'), W, H, *p,
           title="Стани цільових портів ALUA та переходи між ними")


# ── 3. Бінарний формат дескрипторів команди RTPG ─────────────────────────────
def fig_alua_rtpg_descriptor_format():
    W, H = 1580, 880
    p = []

    # Заголовок відповіді RTPG (4 байти)
    p.append(text(790, 60, "Структура даних параметра команди REPORT TARGET PORT GROUPS (SPC-4)", size=15, bold=True))

    hdr_box, hw, hh = textbox(790, 140,
                              ["Заголовок даних параметра (Header, 4 байти)",
                               "Байти 0..3: Довжина даних списку дескрипторів (Data Length, uint32 big-endian)"],
                              size=13, pad=14, fill=GREY_FILL, stroke=LINE, bold=True)
    p.append(hdr_box)

    # Дескриптор цільової групи портів (Target Port Group Descriptor)
    tpg_bg = rect(140, 240, 1300, 380, fill=WHITE_FILL, stroke=LINE, sw=1.5, rx=8)
    p.append(tpg_bg)
    p.append(text(790, 275, "Дескриптор цільової групи портів (Target Port Group Descriptor)", size=14, bold=True, color=FIELD))

    rows = [
        ("Байт 0", "Бит 7: PREF (Preferred)", "Бити 3..0: Асиметричний стан доступу (0h=AO, 1h=ANO, 2h=SB, 3h=UN, Fh=TO)", GREEN_FILL),
        ("Байт 1", "Маска підтримуваних станів (AO_SUP, ANO_SUP, SB_SUP, UN_SUP, TO_SUP)", "Бітова маска можливостей сховища", WARM_FILL),
        ("Байти 2..3", "Ідентифікатор цільової групи портів (Target Port Group ID, uint16)", "Унікальний номер групи (TPG ID 0x0001..0xFFFF)", BLUE_FILL),
        ("Байт 4", "Код статусу групи (Status Code: 0h=Normal, 1h=Altered by STPG, 2h=Implicit change)", "Причина останньої зміни стану", GREY_FILL),
        ("Байт 5", "Зарезервовано", "Вендор-специфічні біти", WHITE_FILL),
        ("Байт 6..7", "Кількість портів у цій групі (Target Port Count: k, uint16)", "Визначає кількість дескрипторів портів далі", GREEN_FILL),
    ]

    ry = 320
    for b_off, b_main, b_desc, fill in rows:
        b1, w1, h1 = textbox(240, ry, [b_off], size=12, pad=10, fill=GREY_FILL, stroke=LINE)
        b2, w2, h2 = textbox(570, ry, [b_main], size=12, pad=10, fill=fill, stroke=LINE)
        b3, w3, h3 = textbox(1100, ry, [b_desc], size=12, pad=10, fill=WHITE_FILL, stroke=MUTED)
        p.append(b1)
        p.append(b2)
        p.append(b3)
        ry += 46

    # Список дескрипторів портів
    ports_bg = rect(140, 650, 1300, 170, fill=BLUE_FILL, stroke=LINE, sw=1.5, rx=8)
    p.append(ports_bg)
    p.append(text(790, 685, "Список дескрипторів цільових портів (Target Port Descriptors, k × 4 байти)", size=14, bold=True))

    p_rows = [
        ("Порт 0 (Байти 8..11)", "Байти 8..9: Зарезервовано  |  Байти 10..11: Відносний ID порту цілі (Relative Target Port ID)", WHITE_FILL),
        ("Порт 1 (Байти 12..15)", "Байти 12..13: Зарезервовано  |  Байти 14..15: Відносний ID порту цілі (Relative Target Port ID)", WHITE_FILL),
    ]

    pry = 730
    for p_off, p_desc, fill in p_rows:
        pb1, pw1, ph1 = textbox(280, pry, [p_off], size=12, pad=9, fill=GREY_FILL, stroke=LINE)
        pb2, pw2, ph2 = textbox(910, pry, [p_desc], size=12, pad=9, fill=fill, stroke=LINE)
        p.append(pb1)
        p.append(pb2)
        pry += 42

    p.append(arrow(790, 140 + hh / 2, 790, 240))
    p.append(arrow(790, 240 + 380, 790, 650))

    render(os.path.join(IMG, 'alua-rtpg-descriptor-format.svg'), W, H, *p,
           title="Формат бінарних дескрипторів відповіді REPORT TARGET PORT GROUPS")


# ── 4. Стек інтеграції ALUA в Linux (dm-multipath + scsi_dh_alua) ────────────
def fig_linux_alua_stack():
    W, H = 1580, 940
    p = []

    # Рівні архітектури
    # Простір користувача ліворуч
    usr_bg = rect(100, 80, 640, 280, fill=WHITE_FILL, stroke=LINE, sw=1.5, rx=8)
    p.append(usr_bg)
    p.append(text(420, 115, "Простір користувача (User Space)", size=14, bold=True, color=INK))

    mpd_box, mw, mh = textbox(420, 180,
                              ["multipathd (Демон багатошляховості)",
                               "• prio alua (визначає пріоритет через RTPG/sysfs)",
                               "• path_grouping_policy group_by_prio",
                               "• path_checker tur (періодичний огляд здоров'я)"],
                              size=12, pad=14, fill=WARM_FILL, stroke=LINE)
    p.append(mpd_box)

    mconf_box, mcw, mch = textbox(420, 295,
                                  ["/etc/multipath.conf", "hardware_handler \"1 alua\" · prio \"alua\""],
                                  size=12, pad=10, fill=GREY_FILL, stroke=MUTED)
    p.append(mconf_box)

    # Device Mapper праворуч
    dm_bg = rect(840, 80, 640, 280, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=8)
    p.append(dm_bg)
    p.append(text(1160, 115, "Ядро: Device Mapper (dm-multipath)", size=14, bold=True, color=FIELD))

    dm_box, dmw, dmh = textbox(1160, 210,
                               ["Віртуальний блоковий пристрій /dev/mapper/mpatha",
                                "• Група 1 (Active/Optimized)  → prio 50 [sdb, sdd] (АКТИВНА)",
                                "• Група 2 (Active/Non-Optimized) → prio 10 [sdc, sde] (РЕЗЕРВ)",
                                "Перемикання групи: коли всі шляхи Групи 1 впали"],
                               size=12, pad=14, fill=WHITE_FILL, stroke=LINE)
    p.append(dm_box)

    # Зв'язок між multipathd і dm-multipath
    p.append(arrow(420 + mw / 2, 180, 840, 210, color=LINE, sw=1.5))
    p.append(text(790, 185, "ioctl DM_TABLE_LOAD", size=12, color=MUTED))

    # Обробник пристроїв SCSI (scsi_dh_alua)
    dh_bg = rect(100, 410, 1380, 260, fill=BLUE_FILL, stroke=LINE, sw=2, rx=8)
    p.append(dh_bg)
    p.append(text(790, 445, "Ядро: Обробник пристроїв SCSI (scsi_dh_alua)", size=14, bold=True, color=NEG))

    dh1, dh1w, dh1h = textbox(340, 540,
                              ["Ініціалізація та опитування",
                               "• Зчитування INQUIRY TPGS",
                               "• Періодичний виклик RTPG",
                               "• Заповнення sysfs alua_*"],
                              size=12, pad=13, fill=WHITE_FILL, stroke=LINE)
    p.append(dh1)

    dh2, dh2w, dh2h = textbox(790, 540,
                              ["Перехоплення помилок і Sense-кодів",
                               "• 06h / 2Ah / 06h → Асинхронний RTPG",
                               "• 02h / 04h / 0Ah → Затримка (Transitioning)",
                               "• 02h / 04h / 0Bh → Шлях непридатний"],
                              size=12, pad=13, fill=WHITE_FILL, stroke=LINE)
    p.append(dh2)

    dh3, dh3w, dh3h = textbox(1240, 540,
                              ["Активація та керування (STPG)",
                               "• Надсилання SET TARGET PORT GROUPS",
                               "• Переведення TPG у стан Active",
                               "• Синхронізація з dm-multipath"],
                              size=12, pad=13, fill=WHITE_FILL, stroke=LINE)
    p.append(dh3)

    # SCSI Mid-layer та драйвери HBA
    scsi_bg = rect(100, 720, 1380, 170, fill=GREY_FILL, stroke=LINE, sw=1.5, rx=8)
    p.append(scsi_bg)
    p.append(text(790, 755, "SCSI Mid-layer, sysfs (/sys/class/scsi_disk/.../alua_access_state) та HBA Драйвери", size=14, bold=True))

    sdevs = [
        (260, "/dev/sdb (Шлях 1 · AO)"),
        (610, "/dev/sdd (Шлях 2 · AO)"),
        (970, "/dev/sdc (Шлях 3 · ANO)"),
        (1320, "/dev/sde (Шлях 4 · ANO)"),
    ]
    for sx, slbl in sdevs:
        s_fr, sw_, sh_ = textbox(sx, 820, [slbl], size=12, pad=10, fill=WHITE_FILL, stroke=LINE)
        p.append(s_fr)

    # Стрілки між рівнями
    p.append(arrow(1160, 210 + dmh / 2, 1160, 410))
    p.append(arrow(340, 540 + dh1h / 2, 340, 720))
    p.append(arrow(790, 540 + dh2h / 2, 790, 720))
    p.append(arrow(1240, 540 + dh3h / 2, 1240, 720))

    render(os.path.join(IMG, 'linux-alua-stack.svg'), W, H, *p,
           title="Стек взаємодії dm-multipath, scsi_dh_alua та драйверів у Linux")


# ── 5. Часова послідовність автоматичного Failover при аварії контролера ──────
def fig_alua_failover_sequence():
    W, H = 1580, 960
    p = []

    # 4 вертикальні лінії сутностей
    cols = [
        (220, "Хост: Застосунок / FS"),
        (580, "Хост: dm-multipath / scsi_dh_alua"),
        (1000, "Контролер A (TPG 1)"),
        (1380, "Контролер B (TPG 2)"),
    ]

    for cx, clbl in cols:
        p.append(line(cx, 110, cx, 880, color=MUTED, sw=1.2, dash="5 5"))
        b, bw, bh = textbox(cx, 80, [clbl], size=13, pad=12, fill=GREY_FILL, stroke=LINE, bold=True)
        p.append(b)

    # Кроки послідовності
    # 1. Нормальний ввід-вивід
    p.append(arrow(220, 160, 580, 160, color=FIELD, sw=2))
    p.append(text(400, 145, "Запис блоку даних (I/O)", size=12, color=FIELD))

    p.append(arrow(580, 180, 1000, 180, color=FIELD, sw=2))
    p.append(text(790, 165, "SCSI WRITE (Шлях sdb · AO)", size=12, color=FIELD))

    p.append(arrow(1000, 210, 580, 210, color=FIELD, sw=2))
    p.append(text(790, 195, "STATUS: GOOD", size=12, color=FIELD))

    p.append(arrow(580, 230, 220, 230, color=FIELD, sw=2))
    p.append(text(400, 215, "I/O Успішний", size=12, color=FIELD))

    # 2. Аварія контролера A
    fail_box, fw, fh = textbox(1000, 290, ["АВАРІЯ Контролера A", "Втрата лінку / Паніка вузла"],
                               size=12, pad=10, fill=RED_FILL, stroke=POS, sw=2, bold=True)
    p.append(fail_box)

    # 3. Наступний I/O зависає / тайм-аут
    p.append(arrow(220, 350, 580, 350, color=LINE, sw=1.5))
    p.append(text(400, 335, "Наступний I/O", size=12))

    p.append(arrow(580, 370, 1000, 370, color=POS, sw=1.5))
    p.append(text(790, 355, "SCSI WRITE (sdb) → ТАЙМ-АУТ / FAIL", size=12, color=POS))

    # dm-multipath відкидає групу 1
    dm_drop, ddw, ddh = textbox(580, 440,
                                ["dm-multipath: Шляхи sdb, sdd мертві",
                                 "Група 1 переходить у стан FAILED",
                                 "Запити ставляться в чергу (queue_if_no_path)"],
                                size=12, pad=12, fill=WARM_FILL, stroke=LINE)
    p.append(dm_drop)

    # 4. Активація Групи 2 (Контролер B)
    p.append(arrow(580, 530, 1380, 530, color=POS, sw=2))
    p.append(text(980, 515, "SET TARGET PORT GROUPS (STPG) або перший I/O", size=12, color=POS, bold=True))

    # Відповідь Transitioning
    p.append(line(1380, 590, 580, 590, color=POS, sw=1.5, dash="6 4"))
    p.append(text(980, 575, "CHECK CONDITION: Sense 02h/04h/0Ah (Transitioning)", size=12, color=POS))

    # Пауза scsi_dh_alua
    dh_wait, dwh, dww = textbox(580, 660,
                                ["scsi_dh_alua: перехоплює 02/04/0A,",
                                 "затримує запит на 200 мс і повторює опитування"],
                                size=12, pad=10, fill=BLUE_FILL, stroke=LINE)
    p.append(dh_wait)

    # Контролер B стає AO
    cb_ao, cbw, cbh = textbox(1380, 720,
                              ["Контролер B: імпорт блокувань LUN,",
                               "TPG 2 переходить у стан Active/Optimized"],
                              size=12, pad=10, fill=GREEN_FILL, stroke=FIELD, bold=True)
    p.append(cb_ao)

    # 5. Успішний повтор I/O через Контролер B
    p.append(arrow(580, 780, 1380, 780, color=FIELD, sw=2))
    p.append(text(980, 765, "Повторний SCSI WRITE (Шлях sdc · тепер AO)", size=12, color=FIELD, bold=True))

    p.append(arrow(1380, 830, 580, 830, color=FIELD, sw=2))
    p.append(text(980, 815, "STATUS: GOOD (LUN активовано на вузлі B)", size=12, color=FIELD))

    p.append(arrow(580, 860, 220, 860, color=FIELD, sw=2))
    p.append(text(400, 845, "I/O Завершено без втрати даних", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, 'alua-failover-sequence.svg'), W, H, *p,
           title="Послідовність повідомлень під час аварійного перемикання (Failover) в ALUA")


if __name__ == '__main__':
    fig_alua_dual_controller_arch()
    fig_alua_port_states()
    fig_alua_rtpg_descriptor_format()
    fig_linux_alua_stack()
    fig_alua_failover_sequence()
    print("all figures generated successfully")
