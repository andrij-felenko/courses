# -*- coding: utf-8 -*-
"""Фігури до теми «sshd: конфігурація й загартування»."""
import sys, os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_architecture_privsep():
    """Архітектура OpenSSH Privilege Separation."""
    W, H = 1080, 620
    f = []

    # Заголовок / фон для батьківського процесу
    f.append(rect(40, 40, 1000, 540, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(540, 70, "Архітектура розділення привілеїв OpenSSH (Privilege Separation)", size=16, bold=True))

    # 1. Привілейований монітор
    f.append(rect(70, 110, 420, 210, fill="#fdecea", stroke=POS, sw=2, rx=6))
    f.append(text(280, 140, "Головний монітор (sshd: [priv])", size=14, color=POS, bold=True))
    f.append(mtext(280, 175,
                   "UID 0 (root) · Повний доступ до системи\n"
                   "Читає /etc/ssh/ssh_host_*_key\n"
                   "Керує PAM, виділяє PTY, робить chroot\n"
                   "Створює сесійний процес і робить setuid()",
                   size=12, color=INK, anchor="middle", lh=1.4))

    # 2. Непривілейований мережевий процес
    f.append(rect(590, 110, 420, 210, fill="#eef3fd", stroke=NEG, sw=2, rx=6))
    f.append(text(800, 140, "Мережевий процес (sshd: [net])", size=14, color=NEG, bold=True))
    f.append(mtext(800, 175,
                   "UID sshd (непривілейований) · Без прав\n"
                   "chroot у порожній /var/empty\n"
                   "Обмежений Seccomp-фільтром BPF\n"
                   "Веде TCP-діалог, KEX, парсить пакети клієнта",
                   size=12, color=INK, anchor="middle", lh=1.4))

    # Канал зв'язку (IPC socketpair)
    f.append(arrow(490, 190, 590, 190, color=LINE, sw=2))
    f.append(arrow(590, 230, 490, 230, color=LINE, sw=2))
    b_ipc, _, _ = textbox(540, 210, "IPC socketpair\n(суворий RPC)", size=11, pad=6, fill="#ffffff", stroke=MUTED)
    f.append(b_ipc)

    # Клієнт ззовні
    f.append(rect(670, 360, 260, 70, fill="#ffffff", stroke=MUTED, sw=1.5, rx=6))
    f.append(text(800, 390, "SSH-клієнт з мережі", size=13, bold=True))
    f.append(text(800, 412, "TCP port 22 / неперевірені дані", size=11, color=MUTED))
    f.append(arrow(800, 360, 800, 320, color=NEG, sw=2))

    # 3. Сесійний процес користувача
    f.append(rect(70, 370, 420, 170, fill="#eafaf1", stroke=FIELD, sw=2, rx=6))
    f.append(text(280, 400, "Сесійний процес (sshd: username)", size=14, color=FIELD, bold=True))
    f.append(mtext(280, 435,
                   "UID/GID користувача (після успішної автентифікації)\n"
                   "Відкрито PTY або підсистему sftp-server\n"
                   "Викликано pam_open_session() і initgroups()\n"
                   "Запуск оболонки: execve(/bin/bash)",
                   size=12, color=INK, anchor="middle", lh=1.4))

    f.append(arrow(280, 320, 280, 370, color=FIELD, sw=2))
    f.append(text(340, 348, "fork() + drop privileges", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, 'sshd-architecture-privsep.svg'), W, H, *f,
           title="Архітектура OpenSSH Privilege Separation")


def fig_hardening_layers():
    """Багатошарова модель захисту SSH-сервера."""
    W, H = 1080, 580
    f = []

    f.append(text(540, 45, "Багатошаровий периметр загартування OpenSSH", size=16, bold=True))

    layers = [
        (100, "1. Мережевий рівень (nftables / firewall)",
         "Фільтрація джерел IP · Обмеження з'єднань meter/rate-limit · Захист від сканування",
         "#eef3fd", NEG),
        (205, "2. Рівень демона (sshd: захист ресурсів)",
         "MaxStartups 10:30:100 · LoginGraceTime 30 · MaxAuthTries 3 · Port 2222",
         "#fef9e7", "#d35400"),
        (310, "3. Криптографічний шар (KEX, Ciphers, MACs)",
         "curve25519, sntrup761 · chacha20-poly1305, aes-gcm · EtM MACs · Заборона CBC/SHA-1",
         "#f4ecf7", "#8e44ad"),
        (415, "4. Рівень доступу й автентифікації (Identity)",
         "PasswordAuthentication no · PermitRootLogin no · AllowGroups · MFA / FIDO2",
         "#fdecea", POS),
        (520, "5. Рівень ізоляції середовища (Chroot / Sandbox)",
         "ChrootDirectory %h · ForceCommand internal-sftp · Seccomp sandbox · Без shell",
         "#eafaf1", FIELD),
    ]

    for y, title, desc, fill_c, stroke_c in layers:
        f.append(rect(140, y - 25, 800, 75, fill=fill_c, stroke=stroke_c, sw=1.8, rx=6))
        f.append(text(540, y + 2, title, size=14, color=stroke_c, bold=True))
        f.append(text(540, y + 28, desc, size=12, color=INK))
        if y < 520:
            f.append(arrow(540, y + 50, 540, y + 78, color=MUTED, sw=1.5))

    render(os.path.join(OUT, 'sshd-hardening-layers.svg'), W, H, *f,
           title="Багатошарова модель загартування OpenSSH")


def fig_match_evaluation():
    """Порядок оцінки конфігурації sshd_config та блоків Match."""
    W, H = 1080, 560
    f = []

    f.append(text(540, 45, "Послідовність обробки директив і блоків Match у sshd_config", size=16, bold=True))

    steps = [
        (100, "1. Глобальна секція (Global Configuration)",
         "Базові налаштування (Port, ListenAddress, Ciphers, KexAlgorithms).\n"
         "Діє правило «first match wins»: перше значення фіксує параметр.",
         "#f4f6f8", LINE),
        (220, "2. Включення Drop-in файлів (Include /etc/ssh/sshd_config.d/*.conf)",
         "Файли читаються за алфавітом. Значення з 01-hardening.conf мають вищий\n"
         "пріоритет за значення, визначені пізніше в основному файлі.",
         "#eef3fd", NEG),
        (340, "3. Умовні блоки (Match User / Group / Address / Host)",
         "Обчислюються після глобальних директив під час кожного підключення.\n"
         "Усі директиви після Match належать цьому блоку до наступного Match.",
         "#fef9e7", "#d35400"),
        (460, "4. Ефективний результуючий профіль (Effective Configuration)",
         "Формується специфічний набір правил для конкретного з'єднання.\n"
         "Перевіряється утилітою: sshd -T -C \"user=...,host=...,addr=...\"",
         "#eafaf1", FIELD),
    ]

    for y, title, desc, fill_c, stroke_c in steps:
        f.append(rect(100, y - 30, 880, 85, fill=fill_c, stroke=stroke_c, sw=1.8, rx=6))
        f.append(text(540, y - 5, title, size=14, color=stroke_c, bold=True))
        f.append(mtext(540, y + 20, desc, size=12, color=INK, lh=1.35))
        if y < 460:
            f.append(arrow(540, y + 55, 540, y + 88, color=LINE, sw=1.8))

    render(os.path.join(OUT, 'sshd-match-evaluation.svg'), W, H, *f,
           title="Порядок оцінки конфігурації sshd_config та блоків Match")


if __name__ == '__main__':
    fig_architecture_privsep()
    fig_hardening_layers()
    fig_match_evaluation()
    print("All figures generated successfully.")
