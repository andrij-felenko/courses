# -*- coding: utf-8 -*-
"""Фігури до теми «memfd_create: безіменний файл у пам'яті й пломби (seals)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_trust_gap():
    """Довжина відображення й довжина файлу — два незалежні числа."""
    W, H = 900, 430
    b = []

    # Хто кому що дав
    b.append(fitbox(40, 28, 240, 66, "Клієнт\nтримає свій дескриптор", size=13))
    b.append(fitbox(620, 28, 240, 66, "Сервер\nвідобразив і читає", size=13))
    b.append(text(450, 48, "дескриптор кадру", size=12, color=MUTED))
    b.append(arrow(288, 64, 612, 64))

    # Відображення
    b.append(text(450, 142, "Відображення в адресному просторі сервера — 6 220 800 байтів",
                  size=13, bold=True))
    b.append(fitbox(60, 156, 780, 52, "адреси лишаються дійсними після будь-якої зміни файлу",
                    size=13, fill="#eaf0fd", stroke=NEG))

    # Файл після скорочення
    b.append(rect(60, 268, 16, 52, fill="#fdecea", stroke=POS))
    b.append(rect(76, 268, 764, 52, fill="#ffffff", stroke=MUTED, sw=1.2, rx=0))
    b.append(text(458, 300, "у файлі цих сторінок більше немає", size=13, color=MUTED))

    # Куди дивиться доторк
    b.append(arrow(400, 210, 400, 264, color=POS))
    b.append(text(450, 348, "Файл після ftruncate(fd, 0) — 0 байтів", size=13, bold=True))

    note, _, _ = textbox(450, 392,
                         "сторінки за межею файлу нема → ядро шле SIGBUS\n"
                         "типова дія сигналу — убити сервер, а не клієнта",
                         size=12, fill="#fdecea", stroke=POS)
    b.append(note)
    render(os.path.join(OUT, 'trust-gap.svg'), W, H, *b)


def fig_seals():
    """Кожна пломба — проти конкретної операції."""
    W, H = 920, 480
    b = []

    b.append(text(300, 66, "Що хочуть зробити з файлом", size=13, bold=True))
    b.append(text(740, 66, "Пломба, що відмовляє (EPERM)", size=13, bold=True))

    rows = [
        ("ftruncate менший · truncate · open(O_TRUNC)", "F_SEAL_SHRINK", NEG),
        ("запис за кінець файлу · ftruncate більший · fallocate", "F_SEAL_GROW", NEG),
        ("write() · вибивання дірки · нове спільне\nвідображення на запис", "F_SEAL_WRITE", POS),
        ("нове відображення на запис\n(вже наявні лишаються чинними)", "F_SEAL_FUTURE_WRITE", POS),
        ("відображення з PROT_EXEC · зміна бітів виконання", "F_SEAL_EXEC", FIELD),
        ("додати до файлу ще одну пломбу", "F_SEAL_SEAL", INK),
    ]

    y = 88
    for left, right, col in rows:
        b.append(fitbox(40, y, 520, 56, left, size=13))
        b.append(fitbox(580, y, 300, 56, right, size=13, bold=True,
                        fill="#ffffff", stroke=col, color=col))
        y += 62

    b.append(text(460, y + 26,
                  "Пломби ставлять лише на memfd, створеному з MFD_ALLOW_SEALING; зняти пломбу не можна ніколи",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'seals.svg'), W, H, *b)


def fig_handshake():
    """Порядок дій обох сторін і дві пастки порядку."""
    W, H = 980, 580
    b = []

    b.append(text(230, 32, "Виробник", size=14, bold=True))
    b.append(text(750, 32, "Споживач", size=14, bold=True))

    left = [
        (52, "memfd_create(\"frame\",\nMFD_CLOEXEC | MFD_ALLOW_SEALING)", None),
        (116, "ftruncate  →  mmap PROT_WRITE\n→  наповнити кадр", None),
        (180, "munmap — зняти СВОЄ\nзаписувальне відображення", POS),
        (244, "F_ADD_SEALS:\nSHRINK | GROW | WRITE | SEAL", None),
        (308, "sendmsg + SCM_RIGHTS", None),
    ]
    for y, s, col in left:
        kw = dict(fill="#ffffff", stroke=col, color=col) if col else {}
        b.append(fitbox(40, y, 380, 54, s, size=12, **kw))

    right = [
        (308, "recvmsg + SCM_RIGHTS", None),
        (372, "F_GET_SEALS і перевірка маски\n— ПЕРЕД усім іншим", POS),
        (436, "fstat: лише тепер\nst_size — факт", None),
        (500, "mmap(PROT_READ, MAP_SHARED)", None),
    ]
    for y, s, col in right:
        kw = dict(fill="#ffffff", stroke=col, color=col) if col else {}
        b.append(fitbox(560, y, 380, 54, s, size=12, **kw))

    b.append(arrow(428, 335, 552, 335))
    b.append(text(490, 322, "fd", size=12, color=MUTED))

    b.append(fitbox(40, 386, 380, 62,
                    "пропустити munmap  →  F_ADD_SEALS\nз F_SEAL_WRITE поверне EBUSY",
                    size=12, fill="#fdecea", stroke=POS))
    b.append(fitbox(40, 464, 380, 62,
                    "без F_SEAL_SEAL отримувач сам\nзапломбує ваш робочий буфер",
                    size=12, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, 'handshake.svg'), W, H, *b)


if __name__ == '__main__':
    fig_trust_gap()
    fig_seals()
    fig_handshake()
    print('ok')
