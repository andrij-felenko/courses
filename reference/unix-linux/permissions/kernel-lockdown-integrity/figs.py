# -*- coding: utf-8 -*-
"""Фігури до теми «Режим мажоритарного захисту ядра: Kernel Lockdown Mode»."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_lockdown_modes():
    """Ієрархія та обмеження трьох режимів Kernel Lockdown."""
    W, H = 1040, 520
    f = []

    # Три рівні
    # None
    f.append(fitbox(40, 90, 300, 330,
                    "Режим None (Вимкнено)\n\n"
                    "• Повний доступ UID 0 до ядра\n"
                    "• Запис/читання через /dev/mem\n"
                    "• Завантаження будь-яких модулів\n"
                    "• Вільне використання kprobes/eBPF\n"
                    "• Прямий доступ до портів I/O\n\n"
                    "Ризик: руткіт у просторі ядра",
                    size=13, fill="#fdfefe", stroke=LINE))

    # Integrity
    f.append(fitbox(370, 90, 300, 330,
                    "Режим Integrity (Цілісність)\n\n"
                    "• Заборона запису в пам'ять ядра\n"
                    "• Блокування /dev/mem та /dev/kmem (W)\n"
                    "• Вимога підпису для модулів і kexec\n"
                    "• Обмеження MSR та модифікації ACPI\n"
                    "• Заборона iopl() та ioperm()\n\n"
                    "Мета: збереження коду ядра",
                    size=13, fill="#fef9e7", stroke="#f39c12"))

    # Confidentiality
    f.append(fitbox(700, 90, 300, 330,
                    "Режим Confidentiality (Конфіденційність)\n\n"
                    "• Усі обмеження режиму Integrity\n"
                    "• Заборона читання пам'яті ядра\n"
                    "• Блокування /proc/kcore та /dev/mem (R)\n"
                    "• Блокування kprobes та ftrace\n"
                    "• Обмеження eBPF на читання секретів\n\n"
                    "Мета: захист секретів ядра",
                    size=13, fill="#fdedec", stroke=POS))

    # Стрілка одностороннього переходу
    f.append(arrow(345, 255, 365, 255, color=LINE, sw=2))
    f.append(arrow(675, 255, 695, 255, color=LINE, sw=2))

    # Пояснення знизу
    b, _, _ = textbox(520, 460,
                      "Односторонній динамічний перехід: рівень блокування у /sys/kernel/security/lockdown\n"
                      "можна лише підвищувати (None → Integrity → Confidentiality); зниження вимагає перезавантаження",
                      size=13, fill="#f7f9fc")
    f.append(b)

    render(os.path.join(OUT, 'lockdown-modes.svg'), W, H, *f,
           title="Три рівні захисту Kernel Lockdown Mode та напрямок одностороннього переходу")


def fig_lockdown_lsm_architecture():
    """Внутрішньоядерна перевірка запиту користувача через LSM-хук security_locked_down()."""
    W, H = 1060, 520
    f = []

    # User Space Process
    f.append(fitbox(40, 100, 240, 120,
                    "User Space Process (root)\n\n"
                    "Системний виклик:\n"
                    "open(\"/dev/mem\", O_RDWR)\n"
                    "чи init_module()",
                    size=13, fill="#eef3fd", stroke=NEG))

    # VFS / Subsystem
    f.append(fitbox(330, 100, 240, 120,
                    "Підсистема ядра (VFS/Driver)\n\n"
                    "Виклик перевірки LSM:\n"
                    "security_locked_down(\n  LOCKDOWN_DEV_MEM)",
                    size=13, fill=FILL, stroke=LINE))

    # Lockdown LSM module
    f.append(fitbox(620, 100, 400, 120,
                    "Модуль Lockdown LSM\n\n"
                    "Порівняння рівня:\n"
                    "reason_level (Integrity) <= active_level?\n"
                    "lockdown_is_locked_down(reason)",
                    size=13, fill="#fef9e7", stroke="#f39c12"))

    f.append(arrow(285, 160, 325, 160, color=LINE, sw=2))
    f.append(arrow(575, 160, 615, 160, color=LINE, sw=2))

    # Decision branches
    f.append(fitbox(470, 300, 240, 100,
                    "Дозволено (0)\n\n"
                    "Виконання системного виклику\n"
                    "продовжується",
                    size=13, fill="#e8f8f5", stroke=FIELD))

    f.append(fitbox(770, 300, 240, 100,
                    "Заборонено (-EPERM)\n\n"
                    "Помилка Operation not permitted\n"
                    "+ запис аудіту в dmesg",
                    size=13, fill="#fdedec", stroke=POS))

    # Arrows for decision
    f.append(arrow(720, 225, 590, 295, color=FIELD, sw=2))
    f.append(arrow(820, 225, 890, 295, color=POS, sw=2))
    f.append(text(620, 250, "активний < причини", size=12, color=FIELD, bold=True))
    f.append(text(890, 250, "активний >= причини", size=12, color=POS, bold=True))

    b, _, _ = textbox(530, 465,
                      "Кожна чутлива операція ядра звертається до security_locked_down() з відповідним кодом причини.\n"
                      "Якщо поточний рівень Lockdown досяг або перевищив вимогу причини, ядро повертає -EPERM.",
                      size=13, fill="#f7f9fc")
    f.append(b)

    render(os.path.join(OUT, 'lockdown-lsm-architecture.svg'), W, H, *f,
           title="Перехоплення чутливих операцій у ядрі через LSM-хук security_locked_down()")


def fig_secureboot_chain_of_trust():
    """Ланцюжок довіри від UEFI Secure Boot до виконання Lockdown в ядрі."""
    W, H = 1100, 520
    f = []

    steps = [
        ("1. Прошивка UEFI", "Перевірка підпису\nзавантажувача\n(Secure Boot DB)", "#eef3fd", NEG),
        ("2. Shim / GRUB", "Перевірка підпису\nобразу ядра Linux\n(vmlinuz)", "#eef3fd", NEG),
        ("3. Ядро Linux", "Перевірка прапорця\nEFI_SECURE_BOOT\nпід час старту", "#fef9e7", "#f39c12"),
        ("4. Lockdown LSM", "Автоматична активація\nрежиму Integrity\nв пам'яті", "#fdedec", POS),
        ("5. Захищене ядро", "Заборона прямого\nзапису в пам'ять та\nнепідписаного коду", "#e8f8f5", FIELD)
    ]

    for i, (title_text, desc, fill_c, stroke_c) in enumerate(steps):
        cx = 110 + i * 215
        f.append(fitbox(cx - 95, 100, 190, 240,
                        f"{title_text}\n\n{desc}",
                        size=13, fill=fill_c, stroke=stroke_c))
        if i < 4:
            f.append(arrow(cx + 100, 220, cx + 115, 220, color=LINE, sw=2))

    b, _, _ = textbox(550, 420,
                      "UEFI Secure Boot перевіряє цілісність лише ДО завантаження ядра в оперативну пам'ять.\n"
                      "Kernel Lockdown Mode продовжує цей захист у середовищі виконання (runtime),\n"
                      "закриваючи користувачеві root можливість модифікувати завантажене ядро.",
                      size=13, fill="#f7f9fc")
    f.append(b)

    render(os.path.join(OUT, 'secureboot-chain-of-trust.svg'), W, H, *f,
           title="Безперервний ланцюжок довіри: від перевірки прошивки UEFI до захисту Lockdown у runtime")


if __name__ == "__main__":
    fig_lockdown_modes()
    fig_lockdown_lsm_architecture()
    fig_secureboot_chain_of_trust()
