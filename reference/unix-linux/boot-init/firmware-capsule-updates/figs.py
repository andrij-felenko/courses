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

def tb(cx, cy, lines, **kw):
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2

def fig_capsule_flow():
    W, H = 1000, 480
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#cccccc"))

    p.append(text(W / 2, 35, "Шлях оновлення прошивки: від LVFS до прошивання SPI Flash", size=20, bold=True))

    # Zone 1: Userspace
    p.append(rect(30, 60, 290, 380, fill=BLUE_FILL, stroke="#1565c0", sw=1.5, rx=8))
    p.append(text(175, 85, "Простір користувача (Userspace)", size=16, bold=True, color="#1565c0"))

    frag1, _, _, _, _ = tb(175, 140, "LVFS (fwupd.org)\nСервер метаданих та .cab", size=13, fill="#ffffff", stroke="#1565c0", rx=5)
    p.append(frag1)

    p.append(arrow(175, 175, 175, 210, color="#1565c0"))

    frag2, _, _, _, _ = tb(175, 245, "fwupd.service + plugins\n(uefi_capsule, nvme)", size=13, fill="#ffffff", stroke="#1565c0", rx=5)
    p.append(frag2)

    p.append(arrow(175, 280, 175, 315, color="#1565c0"))

    frag3, _, _, _, _ = tb(175, 350, "fwupdmgr CLI / D-Bus\nІнтерфейс управління", size=13, fill="#ffffff", stroke="#1565c0", rx=5)
    p.append(frag3)

    # Transition Arrow 1 -> 2
    p.append(arrow(320, 245, 370, 245, color="#333333", sw=2))
    p.append(text(345, 235, "/dev/efi_capsule_loader", size=11, bold=True))

    # Zone 2: Kernel
    p.append(rect(370, 60, 260, 380, fill=WARM_FILL, stroke="#e65100", sw=1.5, rx=8))
    p.append(text(500, 85, "Ядро Linux (Kernel)", size=16, bold=True, color="#e65100"))

    frag4, _, _, _, _ = tb(500, 150, "drivers/firmware/efi/\ncapsule-loader.c", size=13, fill="#ffffff", stroke="#e65100", rx=5)
    p.append(frag4)

    p.append(arrow(500, 185, 500, 220, color="#e65100"))

    frag5, _, _, _, _ = tb(500, 255, "Побудова Scatter-Gather\nсписків сторінок RAM", size=13, fill="#ffffff", stroke="#e65100", rx=5)
    p.append(frag5)

    p.append(arrow(500, 290, 500, 325, color="#e65100"))

    frag6, _, _, _, _ = tb(500, 360, "Виклик UpdateCapsule()\n+ прапор OsIndications", size=13, fill="#ffffff", stroke="#e65100", rx=5)
    p.append(frag6)

    # Transition Arrow 2 -> 3
    p.append(arrow(630, 360, 680, 360, color="#333333", sw=2))
    p.append(text(655, 350, "Warm Reset", size=11, bold=True))

    # Zone 3: Firmware & HW
    p.append(rect(680, 60, 290, 380, fill=GREEN_FILL, stroke="#2e7d32", sw=1.5, rx=8))
    p.append(text(825, 85, "UEFI Firmware & Обладнання", size=16, bold=True, color="#2e7d32"))

    frag7, _, _, _, _ = tb(825, 140, "PEI / DXE фази завантаження\nВиявлення капсули в RAM", size=13, fill="#ffffff", stroke="#2e7d32", rx=5)
    p.append(frag7)

    p.append(arrow(825, 175, 825, 210, color="#2e7d32"))

    frag8, _, _, _, _ = tb(825, 245, "Автентифікація підпису\nПеревірка ключа виробника", size=13, fill="#ffffff", stroke="#2e7d32", rx=5)
    p.append(frag8)

    p.append(arrow(825, 280, 825, 315, color="#2e7d32"))

    frag9, _, _, _, _ = tb(825, 350, "Прошивання SPI Flash\nОновлення запису в ESRT", size=13, fill="#ffffff", stroke="#2e7d32", rx=5)
    p.append(frag9)

    render(os.path.join(IMG, 'capsule-flow.svg'), W, H, *p)

def fig_esrt_structure():
    W, H = 960, 440
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#cccccc"))

    p.append(text(W / 2, 30, "Структура таблиці ESRT та її представлення у sysfs", size=18, bold=True))

    # Left box: Physical Memory ESRT
    p.append(rect(30, 60, 420, 350, fill=WARM_FILL, stroke="#e65100", sw=1.5, rx=8))
    p.append(text(240, 85, "Структура в пам'яті (UEFI ESRT Table)", size=15, bold=True, color="#e65100"))

    frag1, _, _, _, _ = tb(240, 135, "EFI_SYSTEM_RESOURCE_TABLE\nFwResourceCount: 1..N\nFwResourceVersion: 1", size=13, fill="#ffffff", stroke="#e65100", rx=5)
    p.append(frag1)

    p.append(arrow(240, 175, 240, 205, color="#e65100"))

    frag2, _, _, _, _ = tb(240, 275, "EFI_SYSTEM_RESOURCE_ENTRY\n• FwClassId (GUID пристрою)\n• FwType (1 = System Firmware)\n• FwVersion (поточна версія)\n• LowestSupportedFwVersion\n• CapsuleFlags\n• LastAttemptVersion / Status", size=12, fill="#ffffff", stroke="#e65100", rx=5)
    p.append(frag2)

    # Center arrow
    p.append(arrow(450, 240, 510, 240, color="#333333", sw=2))
    p.append(text(480, 225, "drivers/firmware/efi/esrt.c", size=11, bold=True))

    # Right box: sysfs representation
    p.append(rect(510, 60, 420, 350, fill=BLUE_FILL, stroke="#1565c0", sw=1.5, rx=8))
    p.append(text(720, 85, "Представлення у VFS (/sys/firmware/efi/esrt/)", size=15, bold=True, color="#1565c0"))

    frag3, _, _, _, _ = tb(720, 135, "/sys/firmware/efi/esrt/entries/\n├── entry0/\n└── entry1/", size=13, fill="#ffffff", stroke="#1565c0", rx=5)
    p.append(frag3)

    p.append(arrow(720, 175, 720, 205, color="#1565c0"))

    frag4, _, _, _, _ = tb(720, 275, "/sys/firmware/efi/esrt/entries/entry0/\n├── fw_class (GUID)\n├── fw_type\n├── fw_version\n├── lowest_supported_fw_version\n├── capsule_flags\n└── last_attempt_status", size=12, fill="#ffffff", stroke="#1565c0", rx=5)
    p.append(frag4)

    render(os.path.join(IMG, 'esrt-structure.svg'), W, H, *p)

if __name__ == '__main__':
    fig_capsule_flow()
    fig_esrt_structure()
    print("Figures rendered successfully!")
