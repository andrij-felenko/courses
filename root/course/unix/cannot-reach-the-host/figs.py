# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми «Не достукатися: ім'я, маршрут, порт, ключ».

Фігури:
1. four-step-triage-chain.svg — Чотириланковий діагностичний ланцюг: Name -> Route -> Port -> Auth.
2. tcp-rst-vs-drop.svg — Порівняння поведінки TCP: активне скидання RST проти мовчазного DROP.
3. ssh-auth-failure-matrix.svg — Матриця перевірок безпеки OpenSSH: права файлів, StrictModes та MaxAuthTries.
"""

import os
import sys

# Підключаємо спільний модуль svgkit (4 рівні вгору до scripts/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"
YELLOW = "#fef9e7"
PURPLE = "#f4ecf7"


def fig_triage_chain():
    W, H = 1000, 520
    p = []

    # Заголовок
    p.append(fitbox(200, 14, 600, 36, "Чотириланковий ланцюг мережевої діагностики (4-Step Triage Chain)",
                    size=15, fill=PALE, stroke=INK, sw=1.8, color=INK, bold=True))
    p.append(text(W / 2, 66, "Послідовне звуження простору відмови: від доменного імені до криптографічного ключа",
                  size=12, color=MUTED, italic=True))

    stages = [
        ("1. Ім'я (Name Resolution)",
         "Розпізнавання імені в IP:\n• /etc/nsswitch.conf, /etc/hosts\n• systemd-resolved (127.0.0.53)\n• getent ahosts, resolvectl, dig\n\nТипові збої: NXDOMAIN, SERVFAIL, DNS таймаут",
         COOL, "#2457d6"),
        ("2. Маршрут (Kernel Route & L2)",
         "Шлях у ядрі та сусіди:\n• FIB таблиця: ip route get <IP>\n• Default gateway & metrics\n• ARP/NDP стан: ip neigh (REACHABLE/FAILED)\n\nТипові збої: Network unreachable, No route to host",
         GREENF, "#27ae60"),
        ("3. Порт (L4 Transport & Firewall)",
         "Транспортна зв'язність TCP:\n• Тристороннє рукостискання SYN/ACK\n• Стан сокетів на сервері: ss -tlpn\n• Зондування: nc -zv, curl telnet://\n\nТипові збої: Connection refused (RST) / timed out (DROP)",
         YELLOW, "#d4ac0d"),
        ("4. Ключ (SSH Auth & Protocol)",
         "Прикладна автентифікація:\n• Трасування клієнта: ssh -vvv\n• Права: ~/.ssh (0700), authorized_keys (0600)\n• Конфлікт known_hosts, перебір MaxAuthTries\n\nТипові збої: Host key mismatch, Permission denied",
         WARM, "#c0392b")
    ]

    bx = 35
    bw = 215
    bh = 380
    gap = 25
    start_y = 90

    for i, (title, desc, fill_c, stroke_c) in enumerate(stages):
        cur_x = bx + i * (bw + gap)
        
        # Заголовок кроку
        p.append(fitbox(cur_x, start_y, bw, 40, f"Крок {i+1}", size=14, fill=stroke_c, stroke=stroke_c, color="#ffffff", bold=True))
        # Тіло картки
        p.append(fitbox(cur_x, start_y + 44, bw, bh - 44, f"{title}\n\n{desc}", size=11, fill=fill_c, stroke=stroke_c, sw=1.5))
        
        # Стрілка переходу
        if i < len(stages) - 1:
            arr_x1 = cur_x + bw + 4
            arr_x2 = cur_x + bw + gap - 4
            arr_y = start_y + bh / 2
            p.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color=MUTED, sw=2.0))

    return render(os.path.join(OUT, "four-step-triage-chain.svg"), W, H, *p)


def fig_tcp_rst_vs_drop():
    W, H = 1000, 520
    p = []

    p.append(fitbox(180, 14, 640, 36, "Анатомія відмови TCP: Активне скидання (RST) проти мовчазного поглинання (DROP)",
                    size=14, fill=PALE, stroke=INK, sw=1.8, color=INK, bold=True))
    p.append(text(W / 2, 66, "Фундаментальна різниця між Connection refused та Connection timed out на транспортному рівні",
                  size=12, color=MUTED, italic=True))

    # Ліва колонка: Connection refused (TCP RST)
    col1_x = 40
    col_w = 440
    p.append(fitbox(col1_x, 90, col_w, 40, "Сценарій А: Connection refused (Прийшов TCP RST)",
                    size=13, fill=WARM, stroke=POS, color=POS, bold=True))
    
    flow_a = [
        "1. Клієнт надсилає сегмент [SYN] на порт 22 сервера",
        "2. Пакет успішно доходить до ядра цільового сервера",
        "3. Ядро шукає сокет у таблиці inet_lookup_listener",
        "4. Слухач відсутній (демон впав або слухає лише 127.0.0.1)\n   АБО правило фаєрволу nftables робить reject with tcp reset",
        "5. Ядро сервера негайно повертає клієнту сегмент [RST, ACK]",
        "6. Системний виклик connect() миттєво завершується з ECONNREFUSED"
    ]
    p.append(fitbox(col1_x, 138, col_w, 240, "\n".join(flow_a), size=11, fill="#ffffff", stroke=POS, sw=1.4))
    
    diag_a = "Діагностичний висновок:\n• Мережевий маршрут справний і L3 зв'язок є\n• Проблема на кінцевому вузлі (sshd не запущено або iptables REJECT)"
    p.append(fitbox(col1_x, 388, col_w, 100, diag_a, size=11, fill=WARM, stroke=POS, sw=1.4))

    # Права колонка: Connection timed out (Silent DROP)
    col2_x = 520
    p.append(fitbox(col2_x, 90, col_w, 40, "Сценарій Б: Connection timed out (Мовчазний DROP)",
                    size=13, fill=COOL, stroke=NEG, color=NEG, bold=True))
    
    flow_b = [
        "1. Клієнт надсилає перший сегмент [SYN] на порт 22 сервера",
        "2. Фаєрвол (nftables, AWS Security Group, ISP) скидає пакет (DROP)",
        "3. Жодного відповідного пакета (ні ACK, ні RST, ні ICMP) не надходить",
        "4. Стек TCP клієнта очікує і виконує ретрансміти SYN через бекофф:\n   1с -> 2с -> 4с -> 8с -> 16с -> 32с (залежно від tcp_syn_retries)",
        "5. Після вичерпання ліміту часу (типово 60-130с) таймер розриває сокет",
        "6. Системний виклик connect() завершується з помилкою ETIMEDOUT"
    ]
    p.append(fitbox(col2_x, 138, col_w, 240, "\n".join(flow_b), size=11, fill="#ffffff", stroke=NEG, sw=1.4))
    
    diag_b = "Діагностичний висновок:\n• Пакет поглинається на шляху або на вході\n• Причина: nftables DROP, Cloud Security Group, асиметричний маршрут"
    p.append(fitbox(col2_x, 388, col_w, 100, diag_b, size=11, fill=COOL, stroke=NEG, sw=1.4))

    return render(os.path.join(OUT, "tcp-rst-vs-drop.svg"), W, H, *p)


def fig_ssh_auth_matrix():
    W, H = 1000, 520
    p = []

    p.append(fitbox(200, 14, 600, 36, "Матриця перевірок автентифікації OpenSSH та вузькі місця",
                    size=14, fill=PALE, stroke=INK, sw=1.8, color=INK, bold=True))
    p.append(text(W / 2, 66, "Внутрішні перевірки демона sshd, конфлікти ключів та ліміти сеансу",
                  size=12, color=MUTED, italic=True))

    checks = [
        ("1. Перевірка відбитка хоста (known_hosts)",
         "Клієнт звіряє відкритий ключ сервера зі своїм кешем ~/.ssh/known_hosts\n\n"
         "Помилка: Host key verification failed / Remote host identification has changed\n"
         "Причина: Сервер перевстановлено, IP-адресу перевиділено або атака перехоплення (MITM)\n"
         "Виправлення: ssh-keygen -R <hostname_or_ip>",
         WARM, POS),
        
        ("2. Права доступу файлової системи (StrictModes)",
         "Демон sshd перевіряє права на шляху до ключа:\n"
         "• ~/.ssh має бути 0700 (drwx------)\n"
         "• ~/.ssh/authorized_keys має бути 0600 (-rw-------)\n"
         "• /home/user НЕ повинен мати права запису для групи/інших (не 0777/0775, а 0755/0750)\n\n"
         "Помилка: Permission denied (publickey) при повністю правильному ключі в файлі",
         YELLOW, "#d4ac0d"),
        
        ("3. Вичерпання спроб автентифікації (MaxAuthTries)",
         "Клієнтський ssh-agent послідовно пропонує серверу всі завантажені ключі.\n"
         "Якщо на клієнті 8 ключів, а на сервері встановлено MaxAuthTries 6:\n\n"
         "Помилка: Received disconnect: 2: Too many authentication failures\n"
         "Виправлення: ssh -o IdentitiesOnly=yes -i ~/.ssh/id_target user@host",
         COOL, NEG),
        
        ("4. Узгодження криптографічних алгоритмів",
         "Узгодження алгоритмів підпису публічного ключа (KexAlgorithms, PubkeyAcceptedKeyTypes)\n\n"
         "Помилка: no mutual signature algorithm (відхилення застарілих ключів ssh-rsa SHA-1)\n"
         "Виправлення: Перехід на ключі Ed25519 (ssh-keygen -t ed25519)",
         PURPLE, "#8e44ad")
    ]

    bx = 40
    bw = 440
    bh = 185
    gap_x = 40
    gap_y = 20
    start_y = 95

    coords = [
        (bx, start_y),
        (bx + bw + gap_x, start_y),
        (bx, start_y + bh + gap_y),
        (bx + bw + gap_x, start_y + bh + gap_y)
    ]

    for i, (title, desc, fill_c, stroke_c) in enumerate(checks):
        x, y = coords[i]
        p.append(fitbox(x, y, bw, bh, f"{title}\n\n{desc}", size=11, fill=fill_c, stroke=stroke_c, sw=1.5))

    return render(os.path.join(OUT, "ssh-auth-failure-matrix.svg"), W, H, *p)


def main():
    print("Генерація SVG-ілюстрацій для cannot-reach-the-host...")
    fig_triage_chain()
    print("  + four-step-triage-chain.svg")
    fig_tcp_rst_vs_drop()
    print("  + tcp-rst-vs-drop.svg")
    fig_ssh_auth_matrix()
    print("  + ssh-auth-failure-matrix.svg")
    print("Готово.")


if __name__ == "__main__":
    main()
