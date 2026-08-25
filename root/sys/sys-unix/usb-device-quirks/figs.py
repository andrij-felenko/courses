# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE   = "#eaf0fd"
GREEN  = "#eaf6ef"
WARM   = "#fff6e5"
RED    = "#fdecea"
GREY   = "#eceff1"
PURPLE = "#f3e8ff"

def fig_quirks_detection_and_flow():
    W, H = 1100, 720
    p = []

    # Title
    f_hdr, _, _ = textbox(W / 2, 35, ["Архітектура підсистеми quirks: виявлення та модифікація поведінки USB Core"], size=15, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # 1. Hardware plug & initial descriptor fetch
    x_enum = 200
    f_hw, _, _ = textbox(x_enum, 110, ["Під'єднання пристрою USB", "hub_port_init(): скидання порту", "Зчитування дескриптора (VID:PID)"], size=13, bold=True, fill=BLUE, stroke=LINE)
    p.append(f_hw)

    # 2. Quirks detection engine
    y_detect = 250
    f_det, _, _ = textbox(x_enum, y_detect, ["usb_detect_quirks(struct usb_device *udev)", "Пошук збігів за VID, PID та класом"], size=13, bold=True, fill=PURPLE, stroke=LINE)
    p.append(f_det)

    # Sources of quirks (Static vs Dynamic)
    x_src = 620
    f_stat, _, _ = textbox(x_src, 200, ["Статична таблиця ядра: usb_quirk_list[]", "drivers/usb/core/quirks.c", "Вбудована база дефектного заліза"], size=12, fill=FILL, stroke=LINE)
    p.append(f_stat)

    f_dyn, _, _ = textbox(x_src, 300, ["Динамічні прапорці відхилень", "Параметр usbcore.quirks=VID:PID:flags", "/sys/module/usbcore/parameters/quirks"], size=12, fill=FILL, stroke=LINE)
    p.append(f_dyn)

    # Bitmask accumulation
    y_mask = 390
    f_mask, _, _ = textbox(x_enum, y_mask, ["Формування бітової маски", "udev->quirks |= static_quirks | dynamic_quirks", "Збереження маски в структурі пристрою"], size=13, bold=True, fill=GREEN, stroke=LINE)
    p.append(f_mask)

    # Core branches affected by quirks
    y_branch = 560
    f_b1, _, _ = textbox(160, y_branch, ["USB_QUIRK_NO_SET_INTF", "usb_set_interface()", "Пропуск SET_INTERFACE", "запобігання зависанню контролера"], size=11, fill=RED, stroke=LINE)
    p.append(f_b1)

    f_b2, _, _ = textbox(440, y_branch, ["USB_QUIRK_RESET_RESUME", "usb_resume_both()", "Примусове скидання шини", "замість resume signaling"], size=11, fill=WARM, stroke=LINE)
    p.append(f_b2)

    f_b3, _, _ = textbox(720, y_branch, ["USB_QUIRK_NO_AUTOSUSPEND", "usb_autosuspend_device()", "Блокування runtime PM", "заборона переходу в стан сну"], size=11, fill=RED, stroke=LINE)
    p.append(f_b3)

    f_b4, _, _ = textbox(970, y_branch, ["USB_QUIRK_DELAY_INIT", "hub_port_init()", "Пауза після скидання", "стабілізація повільної FW"], size=11, fill=FILL, stroke=LINE)
    p.append(f_b4)

    # Flow arrows
    p.append(arrow(x_enum, 145, x_enum, y_detect - 25))
    p.append(arrow(x_src - 150, 200, x_enum + 150, y_detect - 15))
    p.append(arrow(x_src - 150, 300, x_enum + 150, y_detect + 15))
    p.append(arrow(x_enum, y_detect + 25, x_enum, y_mask - 25))

    # Split arrows from mask to quirk handlers
    p.append(arrow(x_enum - 60, y_mask + 25, 160, y_branch - 35))
    p.append(arrow(x_enum + 20, y_mask + 25, 440, y_branch - 35))
    p.append(arrow(x_enum + 100, y_mask + 25, 720, y_branch - 35))
    p.append(arrow(x_enum + 140, y_mask + 25, 970, y_branch - 35))

    # Binding step at the bottom
    f_bind, _, _ = textbox(W / 2, 675, ["Прив'язка драйвера пристрою (driver_probe)", "Робота драйвера з урахуванням накладених обмежень стека"], size=12, bold=True, fill=GREEN, stroke=LINE)
    p.append(f_bind)

    out_path = os.path.join(IMG, 'quirks-detection-and-flow.svg')
    render(out_path, W, H, *p)
    print(f"Generated {out_path}")

def fig_uas_vs_bot_quirk_arbitration():
    W, H = 1050, 680
    p = []

    # Title
    f_hdr, _, _ = textbox(W / 2, 35, ["Арбітраж USB-накопичувачів: UAS проти Bulk-Only Transport (BOT)"], size=15, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Initial probe
    x_mid = 525
    f_dev, _, _ = textbox(x_mid, 100, ["Під'єднано USB 3.0 / SATA міст (наприклад, JMS567 / ASM1051)", "Дескриптор інтерфейсу заявляє протокол UAS (USB Attached SCSI)"], size=13, bold=True, fill=BLUE, stroke=LINE)
    p.append(f_dev)

    # Driver probe step
    f_probe, _, _ = textbox(x_mid, 210, ["Спроба прив'язки високопродуктивного драйвера uas.ko", "Перевірка чорного списку unusual_uas.h та uas.quirks"], size=13, fill=PURPLE, stroke=LINE)
    p.append(f_probe)

    # Branch left: UAS compatible
    x_uas = 260
    f_uas_ok, _, _ = textbox(x_uas, 340, ["Чип підтримує UAS без критичних багів", "Прапорець US_FL_IGNORE_UAS відсутній"], size=12, bold=True, fill=GREEN, stroke=LINE)
    p.append(f_uas_ok)

    f_uas_work, _, _ = textbox(x_uas, 480, ["Робота через драйвер uas.ko", "SCSI Command Queuing (NCQ / SAM-4)", "Паралельні потоки USB 3.0 Streams", "Мінімальні затримки введення-виведення"], size=12, fill=GREEN, stroke=LINE)
    p.append(f_uas_work)

    # Branch right: Defective UAS chip
    x_bot = 790
    f_uas_bad, _, _ = textbox(x_bot, 340, ["Виявлено дефектний чип або зависання черги", "Встановлено прапорець US_FL_IGNORE_UAS", "uas_probe() повертає -ENODEV"], size=12, bold=True, fill=RED, stroke=LINE)
    p.append(f_uas_bad)

    f_bot_work, _, _ = textbox(x_bot, 480, ["Відкат до драйвера usb-storage.ko", "Класичний Bulk-Only Transport (BOT)", "Суворо послідовна передача (одна команда)", "Накладання прапорців US_FL_* з unusual_devs.h"], size=12, fill=WARM, stroke=LINE)
    p.append(f_bot_work)

    # Summary box
    f_res, _, _ = textbox(W / 2, 620, ["Результат: пристрій не зависає на операціях запису й коректно функціонує в системі"], size=13, bold=True, fill=BLUE, stroke=LINE)
    p.append(f_res)

    # Arrows
    p.append(arrow(x_mid, 130, x_mid, 185))
    p.append(arrow(x_mid - 80, 235, x_uas, 315))
    p.append(arrow(x_mid + 80, 235, x_bot, 315))
    p.append(arrow(x_uas, 365, x_uas, 440))
    p.append(arrow(x_bot, 365, x_bot, 440))
    p.append(arrow(x_uas, 530, x_mid - 60, 595))
    p.append(arrow(x_bot, 530, x_mid + 60, 595))

    out_path = os.path.join(IMG, 'uas-vs-bot-quirk-arbitration.svg')
    render(out_path, W, H, *p)
    print(f"Generated {out_path}")

def fig_usb_error_recovery_and_reset():
    W, H = 1000, 700
    p = []

    # Title
    f_hdr, _, _ = textbox(W / 2, 35, ["Ескалація відновлення після збоїв та таймаутів USB"], size=15, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Escalation level 1
    x_c = 500
    f_l1, _, _ = textbox(x_c, 110, ["Рівень 1: Стан зупинки кінцевої точки (Endpoint STALL)", "Апаратний прапорець Halt на кінцевій точці передачі даних", "usb_clear_halt(udev, pipe) -> відправка CLEAR_FEATURE(ENDPOINT_HALT)"], size=12, fill=GREEN, stroke=LINE)
    p.append(f_l1)

    # Escalation level 2
    f_l2, _, _ = textbox(x_c, 240, ["Рівень 2: Таймаут URB або відсутність відповіді контролера", "Скасування незавершених запитів (usb_unlink_urb)", "Драйвер ініціює скидання пристрою через usb_queue_reset_device()"], size=12, fill=WARM, stroke=LINE)
    p.append(f_l2)

    # Escalation level 3
    f_l3, _, _ = textbox(x_c, 380, ["Рівень 3: Скидання порту концентратора (usb_reset_device)", "hub_port_reset(): фізичний імпульс SE0 тривалістю >= 50 мс", "Повторне зчитування дескрипторів та верифікація конфігурації", "Відновлення альтернативних налаштувань інтерфейсів"], size=12, fill=RED, stroke=LINE)
    p.append(f_l3)

    # Escalation level 4
    f_l4, _, _ = textbox(x_c, 530, ["Рівень 4: Морфінг або критичний збій дескрипторів", "Дескриптори змінилися (USB_QUIRK_RESET_MORPHS) або пристрій не відповідає", "Ядро фіксує логічне від'єднання (disconnect) та видаляє старий вузол", "Повна повторна нумерація як нового фізичного пристрою"], size=12, fill=PURPLE, stroke=LINE)
    p.append(f_l4)

    # Success outcome
    f_ok, _, _ = textbox(x_c, 645, ["Шина відновлена: стек продовжує передачу пакетів або створює новий екземпляр пристрою"], size=12, bold=True, fill=BLUE, stroke=LINE)
    p.append(f_ok)

    # Escalation arrows
    p.append(arrow(x_c, 145, x_c, 210))
    p.append(arrow(x_c, 275, x_c, 345))
    p.append(arrow(x_c, 425, x_c, 490))
    p.append(arrow(x_c, 570, x_c, 620))

    out_path = os.path.join(IMG, 'usb-error-recovery-and-reset.svg')
    render(out_path, W, H, *p)
    print(f"Generated {out_path}")

if __name__ == '__main__':
    fig_quirks_detection_and_flow()
    fig_uas_vs_bot_quirk_arbitration()
    fig_usb_error_recovery_and_reset()
