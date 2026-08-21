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


# ── 1. Архітектура транспортного прошарку SCSI ──────────────────────────────
def fig_transport_layers():
    W, H = 1260, 780
    p = []
    cx = 630

    p.append(text(cx, 45, "Архітектура підсистеми SCSI та транспортні класи ядра",
                  size=18, bold=True))

    # Верхній блок — Блоковий рівень та dm-multipath
    f, w_blk, h_blk = textbox(cx, 115,
                              ["Блоковий рівень ядра та Device Mapper",
                               "dm-multipath: віртуальний диск /dev/mapper/mpathX · перемикання маршрутів · черга bio"],
                              size=14, pad=14, fill=BLUE, stroke=LINE, min_w=980)
    p.append(f)

    p.append(arrow(cx, 115 + h_blk / 2 + 5, cx, 195))

    # Середній рівень — SCSI Middle Layer
    f, w_mid, h_mid = textbox(cx, 245,
                              ["SCSI Middle Layer (scsi_mod)",
                               "Черга команд (request_queue) · scsi_cmnd · таймаут диска (sd rq_timeout)",
                               "Обробник помилок (scsi_eh thread) · прив'язка логічних одиниць (scsi_device)"],
                              size=14, pad=16, fill=WARM, stroke=LINE, min_w=980)
    p.append(f)

    p.append(arrow(cx, 245 + h_mid / 2 + 5, cx, 345))

    # Транспортний рівень — scsi_transport_*
    p.append(text(cx, 335, "SCSI Transport Layer (шаблони транспорту scsi_transport_template)",
                  size=15, bold=True))

    t_boxes = [
        ("scsi_transport_fc", ["Fibre Channel (FC)", "struct fc_rport", "fast_io_fail_tmo", "dev_loss_tmo", "/sys/class/fc_remote_ports/"]),
        ("iscsi_transport", ["iSCSI over TCP/RDMA", "struct iscsi_cls_session", "recovery_tmo", "replacement_timeout", "/sys/class/iscsi_session/"]),
        ("sas_transport", ["Serial Attached SCSI", "struct sas_rphy", "dev_loss_tmo", "phy_identifier", "/sys/class/sas_rphy/"])
    ]
    xs_t = [250, 630, 1010]
    h_t_max = 0
    for x, (mod, lines) in zip(xs_t, t_boxes):
        f, w, h = textbox(x, 430, [mod] + lines, size=12, pad=12,
                          fill=GREEN, stroke=LINE, min_w=340)
        p.append(f)
        h_t_max = max(h_t_max, h)

    # Стрілки до низькорівневих драйверів (LLD)
    for x in xs_t:
        p.append(arrow(x, 430 + h_t_max / 2 + 5, x, 560))

    # Низькорівневі драйвери адаптерів (LLD)
    lld_boxes = [
        ("qla2xxx / lpfc", ["Драйвери FC HBA", "Marvell/QLogic, Broadcom/Emulex", "Link Down / NOS / OLS"]),
        ("iscsi_tcp / be2iscsi", ["Драйвери iSCSI", "Сокетний стек / HW iSCSI Offload", "TCP RST / NOP-In timeout"]),
        ("mpt3sas / pm80xx", ["Драйвери SAS HBA/RAID", "Broadcom/LSI, Microchip", "SAS PHY link loss"])
    ]
    for x, (title, lines) in zip(xs_t, lld_boxes):
        f, w, h = textbox(x, 620, [title] + lines, size=12, pad=12,
                          fill=GREY, stroke=LINE, min_w=340)
        p.append(f)

    # Фізичне середовище / фабрика
    for x in xs_t:
        p.append(arrow(x, 675, x, 725))

    f, w_fab, h_fab = textbox(cx, 745,
                              ["Фізична фабрика зберігання (SAN Fabric / IP Network / SAS Domain)",
                               "Оптичні комутатори SAN, iSCSI маршрутизатори, контролери дискових масивів (Target)"],
                              size=13, pad=10, fill=WARM, stroke=LINE, min_w=1080)
    p.append(f)

    render(os.path.join(IMG, 'scsi-transport-layers.svg'), W, H, *p,
           title="Архітектура підсистеми SCSI та транспортні класи ядра")


# ── 2. Часова шкала обриву та таймерів ───────────────────────────────────────
def fig_timeline_timeouts():
    W, H = 1320, 680
    p = []

    p.append(text(660, 45, "Часова шкала збою лінку: реакція черги, fast_io_fail_tmo та dev_loss_tmo",
                  size=17, bold=True))

    # Горизонтальна вісь часу
    y_axis = 170
    p.append(line(80, y_axis, 1240, y_axis, sw=3, color=LINE))
    p.append(arrow(1230, y_axis, 1270, y_axis, sw=3, color=LINE))
    p.append(text(1285, y_axis + 5, "Час (t)", size=14, bold=True, anchor="start"))

    # Маркери подій на осі
    events = [
        (140, "t = 0 c", "Link Down\n(обрив сигналу)"),
        (380, "0 < t < 5 c", "Вікно короткого збою\n(flapping / re-login)"),
        (660, "t = 5 c", "fast_io_fail_tmo\n(швидке відхилення I/O)"),
        (1040, "t = 30 c (або dev_loss_tmo)", "dev_loss_tmo\n(видалення пристрою rport)")
    ]

    for x, t_label, desc in events:
        p.append(line(x, y_axis - 15, x, y_axis + 15, sw=2.5, color=POS if "t =" in t_label else NEG))
        p.append(text(x, y_axis - 25, t_label, size=13, bold=True, color=POS if "t =" in t_label else NEG))
        lines = desc.split("\n")
        p.append(mtext(x, y_axis + 35, lines, size=12, color=INK, bold=False))

    # Зони станів
    # Зона 1: Блокування (0..5с)
    p.append(rect(140, 260, 520, 150, fill=WARM, stroke=LINE, sw=1.5))
    p.append(text(400, 285, "Стан порту: Blocked (Queue Holding)", size=14, bold=True, color=INK))
    p.append(mtext(400, 312, [
        "• LLD викликає fc_remote_port_delete() / iscsi_session_failure()",
        "• scsi_target_block(): черга блокується, нові I/O стають на паузу",
        "• Якщо лінк підніметься тут — розблокування без жодної помилки I/O"
    ], size=12, anchor="middle", lh=1.35))

    # Зона 2: Fast Fail (5..30с)
    p.append(rect(660, 260, 380, 150, fill=RED, stroke=LINE, sw=1.5))
    p.append(text(850, 285, "Стан порту: Fast Failover", size=14, bold=True, color=POS))
    p.append(mtext(850, 312, [
        "• Спливає fast_io_fail_tmo (напр. 5 с)",
        "• Чергу розблоковано, I/O скидаються",
        "  зі статусом DID_TRANSPORT_FAILFAST",
        "• dm-multipath робить миттєвий failover"
    ], size=12, anchor="middle", lh=1.35))

    # Зона 3: Видалення пристрою (>30с)
    p.append(rect(1040, 260, 220, 150, fill=GREY, stroke=LINE, sw=1.5))
    p.append(text(1150, 285, "Видалення rport", size=14, bold=True, color=INK))
    p.append(mtext(1150, 312, [
        "• Спливає dev_loss_tmo",
        "• scsi_remove_target()",
        "• Видалення /dev/sdX",
        "• Знищення об'єкта"
    ], size=12, anchor="middle", lh=1.35))

    # Нижня пояснювальна картка
    f_bot, w_b, h_b = textbox(660, 520, [
        "Ключова архітектурна різниця двох таймерів:",
        "• fast_io_fail_tmo керує ДОЛЕЮ ЗАПИТІВ (I/O) — змушує ядро швидко відмовити в очікуванні, звільняючи multipath;",
        "• dev_loss_tmo керує ЖИТТЄВИМ ЦИКЛОМ ПРИСТРОЮ (структур ядра) — не дає видалити /dev/sdX завчасно.",
        "Правило коректності: fast_io_fail_tmo < dev_loss_tmo (наприклад, 5 с проти 30 с або 300 с у SAN)."
    ], size=13, pad=16, fill=GREEN, stroke=LINE, min_w=1180)
    p.append(f_bot)

    render(os.path.join(IMG, 'timeline-timeouts.svg'), W, H, *p,
           title="Часова шкала реакції на обрив лінку Fibre Channel / iSCSI")


# ── 3. Ескалація SCSI Error Handling та відсікання ──────────────────────────
def fig_scsi_eh_escalation():
    W, H = 1280, 720
    p = []

    p.append(text(640, 45, "Ескалація SCSI Error Handling (scsi_eh) та транспортне відсікання",
                  size=17, bold=True))

    steps = [
        ("Сходинка 1: eh_abort_handler", ["Спроба скасування конкретної завислої команди", "SCSI Task Management: ABORT TASK", "Діє лише на одну команду CDB"]),
        ("Сходинка 2: eh_device_reset_handler", ["Скидання конкретної логічної одиниці (LUN)", "Task Management: LOGICAL UNIT RESET", "Очищає стан черги LUN, скидає резервації"]),
        ("Сходинка 3: eh_target_reset_handler", ["Скидання всього цільового порту/вузла", "TARGET RESET / I_T Nexus Reset", "Скидає всі LUN на даному цільовому контролері"]),
        ("Сходинка 4: eh_host_reset_handler", ["Повне апаратне скидання HBA-адаптера", "Host Adapter Hardware Reset", "Найважча операція: зупиняє трафік усіх портів HBA"])
    ]

    y_start = 130
    step_h = 110

    for i, (title, lines) in enumerate(steps):
        y = y_start + i * step_h
        # Ліва колонка — класична ескалація EH
        f, w, h = textbox(360, y, [title] + lines, size=12, pad=10,
                          fill=WARM if i < 3 else RED, stroke=LINE, min_w=520)
        p.append(f)

        if i < len(steps) - 1:
            p.append(arrow(360, y + h / 2 + 3, 360, y + step_h - h / 2 - 3))
            p.append(text(390, y + step_h / 2 + 3, "якщо не допомогло", size=11, color=MUTED, anchor="start"))

    # Права панель — Транспортне відсікання (Transport Short-Circuit)
    f_sc, w_sc, h_sc = textbox(950, 300, [
        "Транспортне відсікання (Short-Circuit)",
        "",
        "Якщо віддалений порт у стані Blocked",
        "або fast_io_fail_tmo вже сплив:",
        "",
        "1. scsi_eh перевіряє стан транспорту",
        "2. Спроби посилати ABORT/RESET у мертвий",
        "   кабель блокуються",
        "3. eh_abort_handler повертає FAST_IO_FAIL",
        "4. Ескалація НЕ витрачає 4 × 30 секунд",
        "5. Команда негайно завершується з помилкою",
        "   DID_TRANSPORT_FAILFAST"
    ], size=13, pad=16, fill=GREEN, stroke=LINE, min_w=440)
    p.append(f_sc)

    # Стрілки перехоплення від сходів до правої панелі
    for i in range(3):
        y = y_start + i * step_h
        p.append(arrow(625, y, 725, 260 + i * 40, color=FIELD, sw=2))

    # Нижній висновок
    f_inf, w_i, h_i = textbox(640, 630, [
        "Без транспортних класів: scsi_eh витрачає до 120–180 секунд на марні спроби скидання мертвої фабрики.",
        "З fast_io_fail_tmo: транспорт відсікає ескалацію scsi_eh за лічені мілісекунди після спливу таймера."
    ], size=13, pad=12, fill=BLUE, stroke=LINE, min_w=1160)
    p.append(f_inf)

    render(os.path.join(IMG, 'scsi-eh-escalation.svg'), W, H, *p,
           title="Ескалація SCSI Error Handling та транспортне відсікання")


# ── 4. Перемикання шляху в dm-multipath ──────────────────────────────────────
def fig_multipath_failover_flow():
    W, H = 1320, 720
    p = []

    p.append(text(660, 45, "Схема взаємодії ядра, dm-multipath та таймерів при перемиканні шляху",
                  size=17, bold=True))

    # Блок застосунку
    f_app, w_a, h_a = textbox(660, 110,
                              ["Застосунок / СУБД (PostgreSQL, Oracle, QEMU)",
                               "Виконує write()/read() у віртуальний блоковий пристрій /dev/mapper/mpatha"],
                              size=13, pad=12, fill=BLUE, stroke=LINE, min_w=800)
    p.append(f_app)

    p.append(arrow(660, 110 + h_a / 2 + 5, 660, 185))

    # Блок dm-multipath
    f_dm, w_dm, h_dm = textbox(660, 235,
                               ["dm-multipath (Device Mapper Multipath Target)",
                                "Поточний активний шлях: Шлях 1 (/dev/sda) · Резервний шлях: Шлях 2 (/dev/sdb)",
                                "Черга біо утримується в dm_mq_queue · Політика вибору: service-time / round-robin"],
                               size=13, pad=14, fill=WARM, stroke=LINE, min_w=950)
    p.append(f_dm)

    # Розгалуження на два шляхи
    p.append(arrow(500, 235 + h_dm / 2 + 5, 340, 365))
    p.append(arrow(820, 235 + h_dm / 2 + 5, 980, 365))

    # Шлях 1 (Збійний)
    f_p1, w_p1, h_p1 = textbox(340, 440,
                               ["Шлях 1: HBA 0 → Порт 1 (/dev/sda)",
                                "[ЗБІЙ ЛІНКУ: кабель висмикнуто]",
                                "1. rport переходить у Blocked",
                                "2. fast_io_fail_tmo (5 c) спливає",
                                "3. Драйвер повертає DID_TRANSPORT_FAILFAST",
                                "4. dm позначає шлях як 'faulty'"],
                               size=12, pad=14, fill=RED, stroke=POS, min_w=460)
    p.append(f_p1)

    # Шлях 2 (Живий)
    f_p2, w_p2, h_p2 = textbox(980, 440,
                               ["Шлях 2: HBA 1 → Порт 2 (/dev/sdb)",
                                "[АКТИВНИЙ РЕЗЕРВНИЙ ШЛЯХ]",
                                "1. dm перенаправляє (requeue) запити",
                                "2. Відправка CDB через живий FC/iSCSI порт",
                                "3. Контролер масиву повертає GOOD статус",
                                "4. Застосунок отримує дані без I/O помилки"],
                               size=12, pad=14, fill=GREEN, stroke=FIELD, min_w=460)
    p.append(f_p2)

    # Стрілка перенаправлення від збійного шляху до dm і до живого
    p.append(arrow(340, 525, 660, 580, color=POS, sw=2))
    p.append(arrow(660, 580, 980, 525, color=FIELD, sw=2))

    p.append(text(660, 570, "Швидкий failover: повернення bio в dm (requeue) і відправка на Шлях 2 (< 5.1 с)",
                  size=13, bold=True, color=POS))

    # Нижній блок — Контролер сховища
    f_tgt, w_t, h_t = textbox(660, 665,
                              ["Дисковий масив / Сховище SAN (Dual Controller Storage Array)",
                               "LUN 0 доступний через обидва контролери (ALUA Active/Optimized або Active/Non-Optimized)"],
                              size=13, pad=10, fill=GREY, stroke=LINE, min_w=1080)
    p.append(f_tgt)

    p.append(arrow(980, 525 + h_p2 / 2 + 5, 980, 630, color=FIELD, sw=2))

    render(os.path.join(IMG, 'multipath-failover-flow.svg'), W, H, *p,
           title="Перемикання шляху в dm-multipath при спрацюванні fast_io_fail_tmo")


if __name__ == '__main__':
    fig_transport_layers()
    fig_timeline_timeouts()
    fig_scsi_eh_escalation()
    fig_multipath_failover_flow()
    print("All figures generated successfully.")
