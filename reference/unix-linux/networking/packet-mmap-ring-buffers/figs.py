# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"

def fig_packet_mmap_arch():
    W, H = 1000, 520
    p = []

    # Title / Header
    p.append(fitbox(40, 20, 920, 50,
                    "Порівняння традиційного захоплення пакетів (recvfrom) та механізму PACKET_MMAP",
                    size=16, bold=True, fill=BLUE_FILL, stroke=NEG))

    # Left Box: Traditional Architecture
    lx, ly, lw, lh = 40, 90, 440, 390
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(fitbox(lx + 20, ly + 15, 400, 35, "Традиційний SOCK_RAW + recvfrom()", size=14, bold=True, fill=RED_FILL, stroke=POS))

    # Kernel part left
    p.append(fitbox(lx + 30, ly + 65, 380, 55, "NIC Drivers / NAPI Softirq\nОтримання кадру -> Виділення sk_buff", size=12, fill=WARM_FILL))
    p.append(fitbox(lx + 30, ly + 135, 380, 55, "Socket Queue (af_packet)\nКожен пакет чекає у черзі ядра", size=12, fill=WARM_FILL))

    # Boundary line left
    p.append(line(lx + 20, ly + 205, lx + 420, ly + 205, color=POS, sw=1.5, dash="4 3"))
    p.append(text(lx + 220, ly + 200, "Межа ядра та користувача (Syscall boundary)", size=11, color=POS, bold=True))

    # User part left
    p.append(fitbox(lx + 30, ly + 220, 380, 60, "Користувацький процес (tcpdump / Wireshark)\nВиклики recvfrom() у нескінченному циклі", size=12, fill=GREY_FILL))

    # Draw arrows for traditional
    p.append(arrow(lx + 220, ly + 120, lx + 220, ly + 135))
    p.append(arrow(lx + 220, ly + 190, lx + 220, ly + 220, color=POS, sw=2))
    p.append(text(lx + 225, ly + 212, "memcpy() + Перемикання контексту на КОЖЕН пакет", size=11, color=POS, bold=True, anchor="start"))

    # Bottom notes left
    p.append(fitbox(lx + 30, ly + 300, 380, 65, "Вузьке місце:\n- Високий CPU overhead (context switch)\n- Кеш-пам'ять вимивається при memcpy()\n- Втрати пакетів (drops) на 10Gbps+", size=11, fill=RED_FILL))

    # Right Box: PACKET_MMAP Architecture
    rx, ry, rw, rh = 520, 90, 440, 390
    p.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(fitbox(rx + 20, ry + 15, 400, 35, "PACKET_MMAP (TPACKET_V3 Shared Ring)", size=14, bold=True, fill=GREEN_FILL, stroke=FIELD))

    # Kernel part right
    p.append(fitbox(rx + 30, ry + 65, 380, 55, "NIC Drivers / NAPI Softirq\nЗапис пакетів безпосередньо в Ring Buffer", size=12, fill=WARM_FILL))

    # Shared Memory Ring Buffer in center right
    p.append(fitbox(rx + 30, ry + 135, 380, 75, "Спільний кільцевий буфер (mmap shared memory)\nМасив блоків TPACKET_V3 (Kernel <-> User)\nZero-Copy доступ до даних", size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    # User part right
    p.append(fitbox(rx + 30, ry + 230, 380, 55, "Користувацький процес\nПакетна обробка блоків (Block batching)\npoll() лише коли буфер порожній", size=12, fill=BLUE_FILL))

    # Arrows for right
    p.append(arrow(rx + 220, ry + 120, rx + 220, ry + 135, color=FIELD, sw=2))
    p.append(arrow(rx + 220, ry + 210, rx + 220, ry + 230, color=FIELD, sw=2))
    p.append(text(rx + 225, ry + 222, "Прямий читабельний доступ без syscalls!", size=11, color=FIELD, bold=True, anchor="start"))

    # Bottom notes right
    p.append(fitbox(rx + 30, ry + 300, 380, 65, "Переваги:\n- Zero-Copy між ядром та користувачем\n- Відсутність recvfrom() на кожен пакет\n- Ефективна пакетна обробка сотень пакетів/блок", size=11, fill=GREEN_FILL))

    render(os.path.join(IMG, 'packet-mmap-arch.svg'), W, H, *p)


def fig_tpacket_v3_block():
    W, H = 1050, 480
    p = []

    # Title
    p.append(fitbox(30, 20, 990, 45,
                    "Структура блоку та вирівнювання фреймів у TPACKET_V3 Ring Buffer",
                    size=16, bold=True, fill=BLUE_FILL, stroke=NEG))

    # Outer block rectangle representing a 1MB Block
    bx, by, bw, bh = 30, 85, 990, 370
    p.append(rect(bx, by, bw, bh, fill="#fafafa", stroke=MUTED, sw=1.5, rx=8))

    # Block Header box
    p.append(fitbox(45, 105, 230, 335,
                    "Заголовок блоку\nstruct block_desc\n(struct tpacket_hdr_v1)\n\n"
                    "• block_status:\n  TP_STATUS_USER /\n  TP_STATUS_KERNEL\n"
                    "• num_pkts: к-сть пакетів\n"
                    "• offset_to_first_pkt\n"
                    "• blk_len: довжина блоку\n"
                    "• retire_blk_tov",
                    size=12, fill=WARM_FILL, stroke="#d97706", sw=1.4))

    # Frame 1
    p.append(fitbox(290, 105, 210, 140,
                    "Фрейм 1: tpacket3_hdr\n"
                    "• tp_status\n"
                    "• tp_snaplen, tp_len\n"
                    "• tp_next_offset ->\n"
                    "• tp_sec, tp_nsec",
                    size=11, fill=BLUE_FILL, stroke=NEG, sw=1.2))

    p.append(fitbox(290, 250, 210, 190,
                    "Кадр L2 / MAC Payload 1\n"
                    "Ethernet Header\n"
                    "+ IP Packet / TCP Segment\n"
                    "(Дані без копіювання)",
                    size=11, fill=GREEN_FILL, stroke=FIELD, sw=1.2))

    # Arrow next_offset from Frame 1 to Frame 2
    p.append(arrow(505, 175, 525, 175, color=NEG, sw=2))

    # Frame 2
    p.append(fitbox(530, 105, 210, 140,
                    "Фрейм 2: tpacket3_hdr\n"
                    "• tp_status\n"
                    "• tp_snaplen, tp_len\n"
                    "• tp_next_offset ->\n"
                    "• tp_sec, tp_nsec",
                    size=11, fill=BLUE_FILL, stroke=NEG, sw=1.2))

    p.append(fitbox(530, 250, 210, 190,
                    "Кадр L2 / MAC Payload 2\n"
                    "Ethernet Header\n"
                    "+ UDP Datagram\n"
                    "(Змінний розмір)",
                    size=11, fill=GREEN_FILL, stroke=FIELD, sw=1.2))

    # Padding / Gap box
    p.append(fitbox(745, 105, 40, 335, "P\na\nd\nd\ni\nn\ng", size=11, fill=GREY_FILL, stroke=MUTED))

    # Frame N
    p.append(fitbox(790, 105, 215, 140,
                    "Фрейм N: tpacket3_hdr\n"
                    "• tp_status\n"
                    "• tp_next_offset = 0\n"
                    "  (кінець блоку)\n"
                    "• tp_sec, tp_nsec",
                    size=11, fill=BLUE_FILL, stroke=NEG, sw=1.2))

    p.append(fitbox(790, 250, 215, 190,
                    "Кадр L2 / MAC Payload N\n"
                    "Останній пакет у блоці\n"
                    "Блок заповнено або\n"
                    "спрацював retire timer",
                    size=11, fill=GREEN_FILL, stroke=FIELD, sw=1.2))

    # Arrow from Frame 2 to Frame N
    p.append(arrow(745, 175, 785, 175, color=NEG, sw=2))

    render(os.path.join(IMG, 'tpacket-v3-block.svg'), W, H, *p)


if __name__ == '__main__':
    fig_packet_mmap_arch()
    fig_tpacket_v3_block()
    print("ok")
