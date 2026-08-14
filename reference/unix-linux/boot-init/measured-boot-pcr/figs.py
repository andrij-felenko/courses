# -*- coding: utf-8 -*-
"""Фігури до теми «Виміряне завантаження: регістри PCR і журнал подій»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREEN_FILL = "#eaf7ef"
RED_FILL = "#fdecea"
BLUE_FILL = "#eaf0fd"
GREY_FILL = "#f4f6f8"
YELLOW_FILL = "#fffde6"

def fig_chain_of_trust():
    # Естафета вимірювання завантаження від CRTM до IMA та відповідні регістри PCR
    W, H = 1200, 480
    f = []

    f.append(text(600, 40, "Естафета вимірювань завантаження та прив'язка до регістрів PCR", size=16, color=INK, bold=True))

    nodes = [
        (40, 100, "CRTM\n(Boot Block / SPI)", "Незмінне коріння\nдовіри (SRTM)", GREY_FILL, MUTED, "PCR 0"),
        (260, 100, "UEFI Firmware\n& NVRam Vars", "Код прошивки та\nналаштування", BLUE_FILL, FIELD, "PCR 0, 1, 7"),
        (480, 100, "Option ROMs\n& Boot Manager", "Код адаптерів та\nUEFI Boot Manager", GREEN_FILL, POS, "PCR 2, 4, 5"),
        (700, 100, "Bootloader / UKI\n(GRUB / systemd-stub)", "Аргументи ядра,\ninitramfs, UKI", YELLOW_FILL, NEG, "PCR 8, 9, 11"),
        (920, 100, "Linux Kernel & IMA\n(Userspace execution)", "Модулі ядра,\nвиконувачі файли", BLUE_FILL, FIELD, "PCR 10"),
    ]

    for x, y, title, desc, fill, stroke, pcr in nodes:
        f.append(fitbox(x, y, 180, 90, title, size=13, fill=fill, stroke=stroke))
        f.append(fitbox(x, y + 105, 180, 60, desc, size=11, fill=BG, stroke=MUTED))
        f.append(fitbox(x, y + 180, 180, 40, pcr, size=12, fill=fill, stroke=stroke))

    # Стрілки естафети
    f.append(arrow(220, 145, 260, 145))
    f.append(arrow(440, 145, 480, 145))
    f.append(arrow(660, 145, 700, 145))
    f.append(arrow(880, 145, 920, 145))

    # Нижній блок: Апаратний модуль TPM
    f.append(fitbox(40, 360, 1060, 80, "Апаратний чип TPM 2.0: Регістри PCR акумулюють хеші й унеможливлюють підробку історії", size=13, fill=GREY_FILL, stroke=INK))

    render(os.path.join(IMG, 'chain-of-trust.svg'), W, H, *f, title="Естафета вимірювань завантаження")

def fig_pcr_extend_log():
    # Операція Extend у TPM 2.0 та відтворення журналу подій TCG Event Log
    W, H = 1100, 460
    f = []

    f.append(text(550, 35, "Операція TPM2_Extend та перевірка Event Log через відтворення", size=16, color=INK, bold=True))

    # Ліва частина: Журнал подій в RAM
    f.append(fitbox(50, 70, 420, 40, "TCG Event Log в RAM (/sys/kernel/security/...)", size=13, fill=BLUE_FILL, stroke=FIELD))

    events = [
        (50, 130, "Запис #1: Event = UEFI Code, Digest = d1"),
        (50, 195, "Запис #2: Event = Boot Loader, Digest = d2"),
        (50, 260, "Запис #3: Event = Kernel Cmdline, Digest = d3"),
    ]
    for x, y, txt in events:
        f.append(fitbox(x, y, 420, 50, txt, size=12, fill=GREY_FILL, stroke=MUTED))

    # Стрілка Replay
    f.append(fitbox(510, 180, 140, 60, "Послідовне\nвідтворення\nReplay", size=12, fill=YELLOW_FILL, stroke=NEG))
    f.append(arrow(470, 220, 510, 220))
    f.append(arrow(650, 220, 690, 220))

    # Права частина: Схема TPM2_Extend
    f.append(fitbox(690, 70, 360, 40, "Апаратний чип TPM 2.0", size=13, fill=GREEN_FILL, stroke=POS))

    f.append(fitbox(690, 130, 360, 110, "PCR[i]_new = HASH( PCR[i]_old || Digest )\n\n[Операція є незворотною та залежною від порядку]", size=12, fill=BG, stroke=INK))

    f.append(fitbox(690, 260, 360, 60, "Апаратне значення PCR у TPM\n(наприклад, SHA256 Digest)", size=12, fill=GREEN_FILL, stroke=POS))

    # Нижня висновок-панель
    f.append(fitbox(50, 350, 1000, 65, "Збіг відтвореного хешу з апаратним PCR доводить цілісність журналу та системи.\nБудь-яка підміна в логу дасть неспівпадаючий хеш.", size=12, fill=GREY_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'pcr-extend-log.svg'), W, H, *f, title="Операція Extend та відтворення журналу")

def fig_key_sealing_luks():
    # Запечатування ключів шифрування диска (LUKS2) під значення PCR
    W, H = 1100, 440
    f = []

    f.append(text(550, 35, "Запечатування та розпечатування ключів (Sealing/Unsealing) у LUKS2 через TPM 2.0", size=16, color=INK, bold=True))

    # Крок 1: Sealing
    f.append(fitbox(50, 80, 450, 140, "1. Запечатування (Sealing)\n\nСтворення політики довіри tpm2_createpolicy.\nКлюч диска Volume Key шифрується у TPM під конкретне значення обраних PCR (наприклад, PCR 0, 7, 11).", size=12, fill=BLUE_FILL, stroke=FIELD))

    # Крок 2: Boot & Unseal check
    f.append(fitbox(600, 80, 450, 140, "2. Завантаження системи\n\nКожен компонент робить Extend в PCR.\nsystemd-cryptsetup запитує TPM: Unseal(VolumeKey).", size=12, fill=YELLOW_FILL, stroke=NEG))

    # Стрілка між 1 та 2
    f.append(arrow(500, 150, 600, 150))

    # Результати розпечатування
    f.append(fitbox(50, 260, 450, 120, "УСПІХ (PCR збігаються):\nTPM видає Volume Key -> Диск розшифровується без введення пароля користувача.", size=12, fill=GREEN_FILL, stroke=POS))

    f.append(fitbox(600, 260, 450, 120, "ВІДМОВА (Зміна в PCR):\nСистему завантажено з флешки чи змінено ядро -> TPM відмовляється видати Volume Key -> Вимога пароля відновлення.", size=12, fill=RED_FILL, stroke=NEG))

    f.append(arrow(275, 220, 275, 260))
    f.append(arrow(825, 220, 825, 260))

    render(os.path.join(IMG, 'key-sealing-luks.svg'), W, H, *f, title="Запечатування та розпечатування ключів")

if __name__ == '__main__':
    fig_chain_of_trust()
    fig_pcr_extend_log()
    fig_key_sealing_luks()
    print("Figures generated successfully.")
