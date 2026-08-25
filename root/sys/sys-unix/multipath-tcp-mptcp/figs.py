# -*- coding: utf-8 -*-
import os
import sys

# 4 levels up to reach scripts/ in repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

try:
    from svgkit import *
except ImportError:
    svgkit = None

def render():
    if "textbox" not in globals():
        return

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    # -------------------------------------------------------------------------
    # 1. mptcp-arch.svg: Socket layering and sequence space
    # -------------------------------------------------------------------------
    f1 = []
    f1.append(rect(10, 10, 780, 480, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    f1.append(text(400, 35, "Архітектура MPTCP та розмежування просторів послідовностей", size=16, bold=True, color="#1f2328"))

    b_app, _, _ = textbox(400, 80, "Прикладний додаток (Browser / Client / Server)\nсокет: socket(AF_INET, SOCK_STREAM, IPPROTO_MPTCP)", size=13, pad=10, fill="#eef6ff", stroke="#0969da", bold=True)
    f1.append(b_app)

    f1.append(arrow(400, 108, 400, 138, color="#0969da", sw=2))

    f1.append(rect(40, 140, 720, 150, fill="#f6f8fa", stroke="#6e7781", sw=1.5, rx=6))
    f1.append(text(400, 162, "Шар мета-сокета MPTCP (struct mptcp_sock)", size=14, bold=True, color="#1f2328"))
    f1.append(text(400, 182, "Глобальний простір послідовностей: 64-бітний DSN (Data Sequence Number)", size=12, color="#57606a"))

    b_sched = fitbox(60, 200, 310, 70, "Планувальник пакетів (Scheduler)\n- minRTT (за замовчуванням)\n- round-robin / redundant", size=12, fill="#ffffff", stroke="#8c959f")
    b_pm = fitbox(430, 200, 310, 70, "Менеджер шляхів (Path Manager)\n- in-kernel PM / userspace PM\n- сигналізація ADD_ADDR / MP_JOIN", size=12, fill="#ffffff", stroke="#8c959f")
    f1.append(b_sched)
    f1.append(b_pm)

    f1.append(arrow(215, 290, 215, 328, color="#1f2328", sw=1.8))
    f1.append(arrow(585, 290, 585, 328, color="#1f2328", sw=1.8))

    f1.append(rect(40, 330, 350, 95, fill="#dafbe1", stroke="#1a7f37", sw=1.5, rx=6))
    f1.append(text(215, 350, "Підпотік 1: struct tcp_sock", size=13, bold=True, color="#1a7f37"))
    f1.append(text(215, 370, "Локальний SSN (32-біт Sequence Number)", size=11, color="#1a7f37"))
    f1.append(text(215, 390, "Інтерфейс: eth0 (192.168.1.50:42100)", size=11, color="#1f2328"))

    f1.append(rect(410, 330, 350, 95, fill="#fff8c5", stroke="#9a6700", sw=1.5, rx=6))
    f1.append(text(585, 350, "Підпотік 2: struct tcp_sock", size=13, bold=True, color="#9a6700"))
    f1.append(text(585, 370, "Локальний SSN (32-біт Sequence Number)", size=11, color="#9a6700"))
    f1.append(text(585, 390, "Інтерфейс: wlan0 (10.0.2.15:42100)", size=11, color="#1f2328"))

    f1.append(arrow(215, 425, 215, 458, color="#1a7f37", sw=2))
    f1.append(arrow(585, 425, 585, 458, color="#9a6700", sw=2))

    f1.append(text(215, 473, "Канал Ethernet (WAN 1)", size=12, bold=True, color="#1a7f37"))
    f1.append(text(585, 473, "Бездротовий канал Wi-Fi / LTE (WAN 2)", size=12, bold=True, color="#9a6700"))

    render_out1 = os.path.join(img_dir, "mptcp-arch.svg")
    svgkit_render(render_out1, 800, 500, *f1)

    # -------------------------------------------------------------------------
    # 2. mptcp-handshake.svg: MP_CAPABLE and MP_JOIN establishing sequence
    # -------------------------------------------------------------------------
    f2 = []
    f2.append(rect(10, 10, 840, 540, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    f2.append(text(430, 35, "Встановлення MPTCP-з'єднання (MP_CAPABLE) та приєднання підпотоку (MP_JOIN)", size=16, bold=True, color="#1f2328"))

    # Lifelines
    f2.append(line(210, 70, 210, 500, color="#d0d7de", sw=2, dash="4,4"))
    f2.append(line(650, 70, 650, 500, color="#d0d7de", sw=2, dash="4,4"))

    f2.append(fitbox(120, 65, 180, 40, "Клієнт (Host A)\neth0, wlan0", size=12, fill="#eef6ff", stroke="#0969da", bold=True))
    f2.append(fitbox(560, 65, 180, 40, "Сервер (Host B)\neth0 (Server IP)", size=12, fill="#f6f8fa", stroke="#1f2328", bold=True))

    # Phase 1: MP_CAPABLE
    f2.append(rect(40, 120, 780, 165, fill="#f6f8fa", stroke="#8c959f", sw=1, rx=4))
    f2.append(text(210, 138, "Фаза 1: Первинний підпотік (MP_CAPABLE)", size=12, bold=True, color="#0969da", anchor="start"))

    # SYN MP_CAPABLE
    f2.append(text(430, 155, "1. SYN [MP_CAPABLE, KeyA]", size=11, bold=True, color="#0969da"))
    f2.append(arrow(210, 168, 650, 168, color="#0969da", sw=2))

    # SYN/ACK MP_CAPABLE
    f2.append(text(430, 195, "2. SYN/ACK [MP_CAPABLE, KeyB]", size=11, bold=True, color="#1a7f37"))
    f2.append(arrow(650, 208, 210, 208, color="#1a7f37", sw=2))

    # ACK MP_CAPABLE
    f2.append(text(430, 235, "3. ACK [MP_CAPABLE, KeyA, KeyB]", size=11, bold=True, color="#0969da"))
    f2.append(arrow(210, 248, 650, 248, color="#0969da", sw=2))

    f2.append(text(430, 273, "Обчислено TokenA=H(KeyA), TokenB=H(KeyB), IDSNA, IDSNB", size=11, italic=True, color="#57606a"))

    # Phase 2: MP_JOIN
    f2.append(rect(40, 300, 780, 180, fill="#fff8c5", stroke="#d4a72c", sw=1, rx=4))
    f2.append(text(210, 318, "Фаза 2: Додатковий підпотік через другий інтерфейс (MP_JOIN)", size=12, bold=True, color="#9a6700", anchor="start"))

    # SYN MP_JOIN
    f2.append(text(430, 335, "4. SYN [MP_JOIN, TokenB, NonceA, AddressID=2]", size=11, bold=True, color="#9a6700"))
    f2.append(arrow(210, 348, 650, 348, color="#9a6700", sw=2))

    # SYN/ACK MP_JOIN
    f2.append(text(430, 375, "5. SYN/ACK [MP_JOIN, NonceB, HMAC-B, AddressID=1]", size=11, bold=True, color="#1a7f37"))
    f2.append(arrow(650, 388, 210, 388, color="#1a7f37", sw=2))

    # ACK MP_JOIN
    f2.append(text(430, 415, "6. ACK [MP_JOIN, HMAC-A]", size=11, bold=True, color="#9a6700"))
    f2.append(arrow(210, 428, 650, 428, color="#9a6700", sw=2))

    f2.append(text(430, 465, "Другий підпотік успішно приєднано до мета-сокета!", size=12, bold=True, color="#1a7f37"))

    render_out2 = os.path.join(img_dir, "mptcp-handshake.svg")
    svgkit_render(render_out2, 860, 540, *f2)

    # -------------------------------------------------------------------------
    # 3. mptcp-dss-header.svg: Data Sequence Signal header structure
    # -------------------------------------------------------------------------
    f3 = []
    f3.append(rect(10, 10, 780, 420, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    f3.append(text(400, 35, "Структура TCP-опції Data Sequence Signal (DSS, Kind=30, Subtype=2)", size=15, bold=True, color="#1f2328"))

    # Bit width ruler
    f3.append(rect(50, 60, 700, 25, fill="#f6f8fa", stroke="#d0d7de", sw=1))
    f3.append(text(137, 77, "0..7 біт (Kind)", size=11, bold=True))
    f3.append(text(312, 77, "8..15 біт (Length)", size=11, bold=True))
    f3.append(text(487, 77, "16..19 біт (Subtype)", size=11, bold=True))
    f3.append(text(637, 77, "20..23 біт (Прапори)", size=11, bold=True))

    # Row 1: Kind, Length, Subtype, Flags
    f3.append(fitbox(50, 95, 175, 45, "Kind = 30\n(0x1E - MPTCP)", size=12, fill="#eef6ff", stroke="#0969da"))
    f3.append(fitbox(225, 95, 175, 45, "Довжина (Length)\nв байтах (змінна)", size=12, fill="#f6f8fa", stroke="#6e7781"))
    f3.append(fitbox(400, 95, 175, 45, "Subtype = 2\n(DSS)", size=12, fill="#dafbe1", stroke="#1a7f37", bold=True))
    f3.append(fitbox(575, 95, 175, 45, "Прапори: F m M a A\nF=FIN, M/m=DSN, A/a=ACK", size=11, fill="#fff8c5", stroke="#9a6700"))

    # Row 2: Data ACK
    f3.append(fitbox(50, 150, 700, 45, "Data ACK (32-біт або 64-біт)\nКумулятивне підтвердження даних у глобальному просторі DSN", size=12, fill="#ddf4ff", stroke="#0969da"))

    # Row 3: DSN
    f3.append(fitbox(50, 205, 700, 45, "Data Sequence Number (DSN, 32-біт або 64-біт)\nГлобальний порядковий номер першого байта даного фрагмента", size=12, fill="#dafbe1", stroke="#1a7f37"))

    # Row 4: SSN & Data Length
    f3.append(fitbox(50, 260, 345, 45, "Subflow Sequence Number (SSN, 32-біт)\nПочатковий SSN для даного DSN-маппінгу", size=12, fill="#fff8c5", stroke="#9a6700"))
    f3.append(fitbox(405, 260, 170, 45, "Data Length (16-біт)\nДовжина блоку даних", size=12, fill="#f6f8fa", stroke="#6e7781"))
    f3.append(fitbox(580, 260, 170, 45, "Checksum (16-біт)\nКонтрольна сума DSS", size=12, fill="#f6f8fa", stroke="#6e7781"))

    # Note
    f3.append(rect(50, 320, 700, 80, fill="#f6f8fa", stroke="#d0d7de", sw=1, rx=4))
    f3.append(text(400, 345, "Ключове призначення DSS:", size=12, bold=True, color="#1f2328"))
    f3.append(text(400, 365, "Мапування локальних послідовностей підпотоку (SSN) у глобальну послідовність (DSN).", size=11, color="#57606a"))
    f3.append(text(400, 385, "Це дозволяє приймачу збирати пакети з різних підпотоків у єдиний впорядкований потік.", size=11, color="#57606a"))

    render_out3 = os.path.join(img_dir, "mptcp-dss-header.svg")
    svgkit_render(render_out3, 800, 420, *f3)

    # -------------------------------------------------------------------------
    # 4. mptcp-path-manager.svg: Path manager & netlink architecture
    # -------------------------------------------------------------------------
    f4 = []
    f4.append(rect(10, 10, 780, 460, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    f4.append(text(400, 35, "Архітектура підсистеми Path Manager та управління сокетами", size=15, bold=True, color="#1f2328"))

    # User space box
    f4.append(rect(40, 55, 720, 115, fill="#f6f8fa", stroke="#0969da", sw=1.5, rx=6))
    f4.append(fitbox(50, 62, 220, 24, "Простір користувача", size=12, fill="#eef6ff", stroke="#0969da", bold=True))

    f4.append(fitbox(90, 95, 270, 60, "Команда ip mptcp\n(iproute2 CLI)", size=12, fill="#ffffff", stroke="#8c959f"))
    f4.append(fitbox(420, 95, 290, 60, "Демон управління mptcpd\n(Userspace Path Manager)", size=12, fill="#ffffff", stroke="#8c959f"))

    # Netlink
    f4.append(arrow(225, 170, 225, 208, color="#0969da", sw=2))
    f4.append(arrow(565, 170, 565, 208, color="#0969da", sw=2))

    f4.append(rect(140, 210, 520, 40, fill="#ddf4ff", stroke="#54aadf", sw=1, rx=4))
    f4.append(text(400, 235, "Інтерфейс Generic Netlink (Сімейство \"mptcp\", IPPROTO_MPTCP)", size=12, bold=True, color="#0969da"))

    f4.append(arrow(225, 250, 225, 288, color="#0969da", sw=2))
    f4.append(arrow(565, 250, 565, 288, color="#0969da", sw=2))

    # Kernel space box
    f4.append(rect(40, 290, 720, 155, fill="#dafbe1", stroke="#1a7f37", sw=1.5, rx=6))
    f4.append(fitbox(50, 297, 180, 24, "Простір ядра Linux", size=12, fill="#e6ffed", stroke="#1a7f37", bold=True))

    f4.append(fitbox(70, 330, 300, 100, "Ядерний Path Manager (in-kernel PM)\n- Автоматичний розшук ендпоінтів\n- Команди ADD_ADDR / RM_ADDR\n- Таблиця MPTCP Endpoints", size=11, fill="#ffffff", stroke="#1a7f37"))
    f4.append(fitbox(410, 330, 320, 100, "Підсистема сокетів MPTCP (mptcp_sock)\n- Створення subflows (MP_JOIN)\n- Моніторинг стану (sysctl net.mptcp.*)\n- Трасування розривів та фолбеків", size=11, fill="#ffffff", stroke="#1a7f37"))

    render_out4 = os.path.join(img_dir, "mptcp-path-manager.svg")
    svgkit_render(render_out4, 780, 460, *f4)

def svgkit_render(path, w, h, *frags):
    from svgkit import render as sk_render
    sk_render(path, w, h, *frags)

if __name__ == '__main__':
    render()
