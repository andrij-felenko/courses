# -*- coding: utf-8 -*-
"""Фігури до теми «Сокети в Linux: від дескриптора до з'єднання»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_socket_structures():
    """Внутрішньоядерний зв'язок від дескриптора до протокольної структури tcp_sock."""
    W, H = 980, 480
    g = []

    # Заголовок шарів
    g.append(text(240, 36, "Простір користувача & VFS (BSD Socket Layer)", size=14, bold=True, color="#1e293b"))
    g.append(text(740, 36, "Мережевий стек ядра (Protocol Engine)", size=14, bold=True, color="#1e293b"))

    # Пунктирна лінія розділення VFS та Network Stack
    g.append(line(490, 50, 490, 410, color="#94a3b8", sw=1.5, dash="6,4"))

    # Ланцюжок VFS (ліворуч)
    g.append(fitbox(40, 70, 200, 54, "Таблиця FD процесу\nfd = 3", size=13, fill="#e2e8f0"))
    g.append(arrow(240, 97, 280, 97, sw=1.6))

    g.append(fitbox(280, 70, 180, 54, "struct file\nf_op = socket_file_ops\nprivate_data", size=12, fill="#dbeafe"))
    g.append(arrow(370, 124, 370, 160, sw=1.6))

    g.append(fitbox(280, 160, 180, 64, "struct socket\nstate = SS_CONNECTED\nops = inet_stream_ops\nsk ────────────┐", size=12, fill="#bfdbfe"))

    # Стрілка переходу від struct socket до struct sock (через межу)
    g.append(arrow(460, 192, 520, 192, sw=1.8, color="#1d4ed8"))

    # Ієрархія struct sock (праворуч)
    g.append(fitbox(520, 70, 420, 54, "struct sock (загальний сокет)\nsk_family = AF_INET · sk_type = SOCK_STREAM\nsk_receive_queue · sk_write_queue · sk_wq", size=12, fill="#fef3c7"))
    g.append(arrow(730, 124, 730, 160, sw=1.6))

    g.append(fitbox(520, 160, 420, 54, "struct inet_sock (IP-рівень)\ninet_saddr (локальний IP) · inet_daddr (віддалений IP)\ninet_sport (локальний порт) · inet_dport (віддалений порт)", size=12, fill="#fde68a"))
    g.append(arrow(730, 214, 730, 250, sw=1.6))

    g.append(fitbox(520, 250, 420, 54, "struct inet_connection_sock (з'єднувальний сокет)\nicsk_accept_queue (Accept queue) · icsk_rto (таймаути)\nicsk_af_ops (IPv4/IPv6 конкретні операції)", size=12, fill="#fcd34d"))
    g.append(arrow(730, 304, 730, 340, sw=1.6))

    g.append(fitbox(520, 340, 420, 64, "struct tcp_sock (специфікація TCP)\nsnd_una · snd_nxt · rcv_nxt (номери послідовностей)\nsnd_wnd · rcv_wnd (вікна) · srtt_us (RTT) · mss_cache", size=12, fill="#f59e0b"))

    # Нижня підсумкова картка
    g.append(fitbox(40, 424, 900, 46, "VFS бачить сокет як звичайний дескриптор через struct socket, "
                                    "а мережевий стек розгортає його до struct tcp_sock", size=12, fill="#f1f5f9", stroke="#cbd5e1"))

    render(os.path.join(IMG, 'socket-structures.svg'), W, H, *g,
           title="Структури сокета у ядрі Linux")


def fig_tcp_handshake_queues():
    """3-Way Handshake, системні виклики та двочергова модель (SYN Backlog і Accept Queue)."""
    W, H = 980, 520
    g = []

    # Лінії часу Клієнта і Сервера
    g.append(text(120, 40, "Клієнт (connect)", size=14, bold=True, color="#1e293b"))
    g.append(text(500, 40, "Сервер у ядрі (SYN Backlog & Accept Queue)", size=14, bold=True, color="#1e293b"))
    g.append(text(860, 40, "Процес сервера", size=14, bold=True, color="#1e293b"))

    # Вертикальні осі часу
    g.append(line(120, 60, 120, 450, color="#64748b", sw=2))
    g.append(line(440, 60, 440, 450, color="#64748b", sw=2))
    g.append(line(860, 60, 860, 450, color="#64748b", sw=2))

    # Крок 1: socket() + bind() + listen() на сервері
    g.append(fitbox(770, 70, 180, 44, "listen(listen_fd, backlog)\n(стан: TCP_LISTEN)", size=11, fill="#e2e8f0"))

    # Дві черги на сервері
    g.append(rect(340, 120, 200, 100, fill="#fef3c7", stroke="#d97706", sw=1.5))
    g.append(text(440, 140, "SYN Backlog", size=12, bold=True, color="#92400e"))
    g.append(text(440, 160, "request_sock (SYN_RECV)", size=11, color="#b45309"))
    g.append(text(440, 180, "ліміт: tcp_max_syn_backlog", size=10, color="#78350f"))

    g.append(rect(340, 260, 200, 110, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    g.append(text(440, 280, "Accept Queue", size=12, bold=True, color="#14532d"))
    g.append(text(440, 300, "struct tcp_sock (ESTABLISHED)", size=11, color="#15803d"))
    g.append(text(440, 320, "ліміт: min(backlog, somaxconn)", size=10, color="#166534"))

    # Крок 2: connect() надсилає SYN
    g.append(fitbox(20, 110, 180, 40, "connect(cli_fd, addr)\n(стан: SYN_SENT)", size=11, fill="#dbeafe"))
    g.append(arrow(120, 140, 340, 160, sw=1.8, color="#2563eb"))
    g.append(text(220, 140, "1. SYN (ISN_c)", size=11, bold=True, color="#1d4ed8"))

    # Крок 3: Сервер додає request_sock в SYN Backlog і надсилає SYN-ACK
    g.append(arrow(340, 180, 120, 210, sw=1.8, color="#d97706"))
    g.append(text(220, 185, "2. SYN-ACK (ISN_s, ACK_c)", size=11, bold=True, color="#b45309"))

    # Крок 4: Клієнт отримує SYN-ACK, переходить у ESTABLISHED, надсилає ACK
    g.append(fitbox(20, 220, 180, 36, "connect() повертає 0\n(стан: ESTABLISHED)", size=11, fill="#bbf7d0"))
    g.append(arrow(120, 240, 340, 270, sw=1.8, color="#16a34a"))
    g.append(text(220, 245, "3. ACK (ACK_s)", size=11, bold=True, color="#15803d"))

    # Крок 5: Переміщення з SYN Backlog в Accept Queue
    g.append(arrow(440, 220, 440, 260, sw=2, color="#16a34a"))
    g.append(text(490, 240, "просування", size=10, color="#16a34a"))

    # Крок 6: accept() витягає з Accept Queue
    g.append(fitbox(770, 340, 180, 48, "accept(listen_fd, ...)\nблокується, якщо порожньо", size=11, fill="#fed7aa"))
    g.append(arrow(540, 350, 770, 350, sw=1.8, color="#ea580c"))
    g.append(text(655, 340, "витягування з'єднання", size=11, bold=True, color="#c2410c"))

    g.append(fitbox(770, 405, 180, 44, "повертає новий conn_fd\n(слухаючий FD вільний)", size=11, fill="#bbf7d0"))

    # Нижня підсказка
    g.append(fitbox(40, 470, 900, 40, "accept() НЕ бере участі у 3-Way Handshake — ядро виконує його повністю асинхронно у фоні", size=12, fill="#f1f5f9", stroke="#cbd5e1"))

    render(os.path.join(IMG, 'tcp-handshake-queues.svg'), W, H, *g,
           title="Послідовність системних викликів та двочергова модель TCP")


def fig_socket_lifecycle():
    """Повний життєвий цикл сокета: створення, з'єднання, передача даних, закриття та TIME_WAIT."""
    W, H = 980, 440
    g = []

    # Блоки Сервера
    g.append(text(180, 30, "Серверний сокет (Passive)", size=13, bold=True))
    g.append(fitbox(60, 50, 240, 36, "socket(AF_INET, SOCK_STREAM, 0)", size=11, fill="#e2e8f0"))
    g.append(arrow(180, 86, 180, 106, sw=1.5))
    g.append(fitbox(60, 106, 240, 36, "bind(fd, local_addr, len)", size=11, fill="#e2e8f0"))
    g.append(arrow(180, 142, 180, 162, sw=1.5))
    g.append(fitbox(60, 162, 240, 36, "listen(fd, backlog) → TCP_LISTEN", size=11, fill="#fef3c7"))
    g.append(arrow(180, 198, 180, 218, sw=1.5))
    g.append(fitbox(60, 218, 240, 36, "accept(fd, ...) → новий conn_fd", size=11, fill="#dcfce7"))

    # Блоки Клієнта
    g.append(text(780, 30, "Клієнтський сокет (Active)", size=13, bold=True))
    g.append(fitbox(660, 50, 240, 36, "socket(AF_INET, SOCK_STREAM, 0)", size=11, fill="#e2e8f0"))
    g.append(arrow(780, 86, 780, 162, sw=1.5))
    g.append(fitbox(660, 162, 240, 36, "connect(fd, server_addr, len)", size=11, fill="#dbeafe"))

    # Зв'язок connect -> accept (Handshake)
    g.append(arrow(660, 180, 300, 236, sw=1.8, color="#2563eb"))
    g.append(text(460, 195, "3-Way Handshake", size=11, color="#1d4ed8", bold=True))

    # Обмін даними
    g.append(rect(340, 260, 300, 60, fill="#f8fafc", stroke="#94a3b8", sw=1.5))
    g.append(text(490, 280, "Двосторонній обмін даними", size=12, bold=True))
    g.append(text(490, 300, "read() / write() · recv() / send()", size=11, color="#475569"))

    g.append(arrow(180, 254, 340, 275, sw=1.5))
    g.append(arrow(780, 198, 640, 275, sw=1.5))

    # Закриття з'єднання (4-Way Teardown)
    g.append(arrow(490, 320, 490, 350, sw=1.5))
    g.append(fitbox(340, 350, 300, 44, "close(fd) або shutdown(fd, how)\n4-Way Teardown (FIN → ACK → FIN → ACK)", size=11, fill="#fee2e2", stroke="#ef4444"))

    g.append(fitbox(660, 350, 240, 44, "Стан TIME_WAIT у ядрі\n(тривалість: 2 · MSL = 60 сек)", size=11, fill="#fecaca"))
    g.append(arrow(640, 372, 660, 372, sw=1.5, color="#dc2626"))

    # Нижня примітка
    g.append(fitbox(40, 404, 900, 30, "close() закриває дескриптор, але з'єднання в ядрі живе у TIME_WAIT до завершення таймера", size=11, fill="#f1f5f9", stroke="#cbd5e1"))

    render(os.path.join(IMG, 'socket-lifecycle.svg'), W, H, *g,
           title="Повний життєвий цикл сокета та дескриптора")


if __name__ == '__main__':
    fig_socket_structures()
    fig_tcp_handshake_queues()
    fig_socket_lifecycle()
    print("ok")
