# -*- coding: utf-8 -*-
"""Фігури до теми «Можливості (capabilities) замість всесильного root»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_one_bit_vs_names():
    """Один ключ до всіх дверей проти окремого ключа на кожні."""
    W, H = 1010, 640
    f = []

    f.append(text(225, 78, "дія, яку ядро колись пускало лише root", size=13, color=MUTED))
    f.append(text(530, 78, "ключ до неї", size=13, color=MUTED))
    f.append(text(805, 78, "іменована можливість", size=13, color=MUTED))

    rows = [
        ("відкрити сирий сокет (ICMP, ARP)",   "CAP_NET_RAW"),
        ("прив'язатися до порту нижче 1024",   "CAP_NET_BIND_SERVICE"),
        ("завантажити модуль ядра",            "CAP_SYS_MODULE"),
        ("обійти дев'ять бітів прав файлу",    "CAP_DAC_OVERRIDE"),
        ("змонтувати файлову систему",         "CAP_SYS_ADMIN"),
        ("поставити собі будь-який UID",       "CAP_SETUID"),
    ]
    for i, (action, cap) in enumerate(rows):
        y = 110 + i * 76
        f.append(fitbox(60, y, 330, 62, action, size=13))
        f.append(fitbox(440, y, 180, 62, "uid == 0", size=14, fill="#fdecea", stroke=POS))
        f.append(fitbox(660, y, 290, 62, cap, size=13, fill="#eef3fd", stroke=NEG))

    b, _, _ = textbox(505, 600,
                      "той самий ключ у середньому стовпці — це й є вся проблема:\n"
                      "хто дістав його заради одного рядка, відчинив геть усе",
                      size=13, fill="#f7f9fc")
    f.append(b)
    render(os.path.join(OUT, 'one-bit-vs-names.svg'), W, H, *f,
           title="Одна перевірка uid == 0 проти окремої назви на кожну дію")


def fig_exec_channels():
    """Три канали, якими можливість потрапляє в новий образ програми."""
    W, H = 1370, 580
    f = []

    # канал 1 — домовленість процесу й файлу
    b, _, _ = textbox(150, 110, "P(успадковувані)", size=14, min_w=240)
    f.append(b)
    f.append(text(305, 117, "∩", size=22, color=MUTED))
    b, _, _ = textbox(470, 110, "F(успадковувані)", size=14, min_w=240)
    f.append(b)
    f.append(text(310, 166, "обидві сторони мусять погодитись", size=12, color=MUTED))

    # канал 2 — файл дає сам, стеля обмежує
    b, _, _ = textbox(150, 250, "F(дозволені)", size=14, min_w=240)
    f.append(b)
    f.append(text(305, 257, "∩", size=22, color=MUTED))
    b, _, _ = textbox(470, 250, "P(гранична стеля)", size=14, min_w=240)
    f.append(b)
    f.append(text(310, 306, "файл дає, стеля не пускає вище", size=12, color=MUTED))

    # канал 3 — навколишні
    b, _, _ = textbox(150, 390, "P′(навколишні)", size=14, min_w=240, stroke=NEG)
    f.append(b)
    b, _, _ = textbox(470, 390, "нікого не питає", size=13, min_w=240, fill="#f7f9fc")
    f.append(b)
    f.append(text(310, 446, "з ядра 4.3: проходить без позначок на файлі", size=12, color=MUTED))

    # злиття
    f.append(arrow(595, 110, 700, 228))
    f.append(arrow(595, 250, 700, 250))
    f.append(arrow(595, 390, 700, 272))

    f.append(fitbox(715, 190, 280, 120,
                    "P′(дозволені)\n\nщо новий образ\nмає право вмикати",
                    size=14, fill="#eef3fd", stroke=NEG))

    f.append(arrow(1000, 250, 1085, 250))
    f.append(fitbox(1100, 190, 250, 120,
                    "P′(діючі)\n\nщо ядро справді\nпитає на перевірці",
                    size=14, fill="#f7f9fc"))

    b, _, _ = textbox(685, 530,
                      "у діючі лягає все дозволене, якщо на файлі стоїть біт «діючий»;\n"
                      "інакше — лише навколишні, і програма вмикає решту сама",
                      size=13, fill="#f7f9fc")
    f.append(b)
    render(os.path.join(OUT, 'exec-channels.svg'), W, H, *f,
           title="Три канали, якими можливість переживає exec")


def fig_ping_eras():
    """Скільки влади коштувала одна дія: три покоління однієї програми."""
    W, H = 1210, 450
    f = []

    cols = [
        (200, "setuid root\n(до 2008)",
              "біт s на файлі: exec підіймає\nдіючий UID до нуля",
              "помилка в ping —\nуся машина", POS),
        (600, "файлова можливість\n(з ядра 2.6.24)",
              "xattr security.capability:\ncap_net_raw+ep",
              "помилка в ping —\nсирі пакети, і все", MUTED),
        (1000, "сокет ICMP\n(з ядра 3.0)",
              "net.ipv4.ping_group_range:\nядро саме пускає echo",
              "привілею немає\nвзагалі", NEG),
    ]
    for cx, title, mech, cost, color in cols:
        b, _, _ = textbox(cx, 78, title, size=14, min_w=300, bold=True)
        f.append(b)
        f.append(fitbox(cx - 150, 132, 300, 76, mech, size=13, fill="#f7f9fc"))
        b, _, _ = textbox(cx, 300, cost, size=13, min_w=300, stroke=color)
        f.append(b)

    f.append(arrow(365, 170, 435, 170, color=MUTED))
    f.append(arrow(765, 170, 835, 170, color=MUTED))

    b, _, _ = textbox(600, 400,
                      "найдешевша можливість — та, якої програмі більше не треба",
                      size=13, fill="#eef3fd", stroke=NEG)
    f.append(b)
    render(os.path.join(OUT, 'ping-eras.svg'), W, H, *f,
           title="Три покоління ping і ціна одного привілею")


def fig_keepcaps_order():
    """Що стається з наборами на кожному кроці зниження UID — з прапорцем і без."""
    W, H = 1250, 700
    f = []

    f.append(fitbox(40, 56, 300, 44, "крок служби", size=13, fill="#f7f9fc"))
    f.append(fitbox(370, 56, 380, 44, "без PR_SET_KEEPCAPS",
                    size=14, fill="#fdecea", stroke=POS))
    f.append(fitbox(790, 56, 380, 44, "з PR_SET_KEEPCAPS",
                    size=14, fill="#eef3fd", stroke=NEG))

    rows = [
        ("старт від root",
         "Prm: усі 41\nEff: усі 41", "#f7f9fc",
         "Prm: усі 41\nEff: усі 41", "#f7f9fc"),
        ("prctl(PR_SET_KEEPCAPS, 1)",
         "рядка немає", "#fdecea",
         "прапорець піднято,\nнабори ще не змінились", "#eef3fd"),
        ("setgroups → setresgid → setresuid",
         "Prm: {}   Eff: {}\nправило 1 стерло все", "#fdecea",
         "Prm: усі 41   Eff: {}\nправило 2 гасить лише діючі", "#eef3fd"),
        ("capset(prm = eff = NET_BIND_SERVICE)",
         "EPERM: нові дозволені мусять\nбути підмножиною старих", "#fdecea",
         "Prm: NET_BIND_SERVICE\nEff: NET_BIND_SERVICE", "#eef3fd"),
        ("bind(:443) після переналаштування",
         "EACCES", "#fdecea",
         "порт наш", "#eef3fd"),
    ]
    for i, (step, a_txt, a_fill, b_txt, b_fill) in enumerate(rows):
        y = 120 + i * 96
        f.append(fitbox(40, y, 300, 80, step, size=13))
        f.append(fitbox(370, y, 380, 80, a_txt, size=13, fill=a_fill))
        f.append(fitbox(790, y, 380, 80, b_txt, size=13, fill=b_fill))

    b, _, _ = textbox(625, 655,
                      "прапорець рятує лише дозволені: діючі гасить окреме правило,\n"
                      "і підняти їх назад мусить сама програма",
                      size=13, fill="#f7f9fc")
    f.append(b)
    render(os.path.join(OUT, 'keepcaps-order.svg'), W, H, *f,
           title="Що лишається в наборах на кожному кроці зниження UID")


def fig_hex_mask():
    """Як прочитати шістнадцяткову маску з /proc/PID/status. Вставка api-."""
    W, H = 1040, 530
    f = []

    digits = "0000000000003000"
    x0, bw, by, bh = 150, 46, 120, 48
    hot = 12                       # позиція цифри «3» у рядку зліва

    f.append(text(138, by + bh / 2 + 5, "CapPrm:", size=14, anchor="end", bold=True))
    for i, d in enumerate(digits):
        is_hot = (i == hot)
        f.append(fitbox(x0 + i * bw, by, bw, bh, d, size=17,
                        fill="#eef3fd" if is_hot else BG,
                        stroke=NEG if is_hot else MUTED))

    f.append(text(x0 + bw / 2, by + bh + 24, "цифра 15", size=11, color=MUTED))
    f.append(text(x0 + 15 * bw + bw / 2, by + bh + 24, "цифра 0", size=11, color=MUTED))

    cx = x0 + hot * bw + bw / 2
    f.append(arrow(cx, by + bh + 40, cx, 234, color=NEG))

    for j, (bit, val) in enumerate(((15, "0"), (14, "0"), (13, "1"), (12, "1"))):
        f.append(fitbox(cx - 156 + j * 78, 244, 78, 62,
                        "біт %d\n%s" % (bit, val), size=13,
                        fill="#eef3fd" if val == "1" else BG,
                        stroke=NEG if val == "1" else MUTED))

    f.append(text(cx, 334, "0x3 = 0011₂", size=13, color=MUTED))

    b, _, _ = textbox(cx, 378,
                      "підняті біти 12 і 13:\n"
                      "CAP_NET_ADMIN (12) і CAP_NET_RAW (13)",
                      size=13, fill="#eef3fd", stroke=NEG)
    f.append(b)

    b, _, _ = textbox(500, 478,
                      "цифра номер n справа (з нуля) несе біти 4n…4n+3;\n"
                      "шістнадцять цифр — це 64 біти, з яких вжито поки 41",
                      size=13, fill="#f7f9fc")
    f.append(b)
    render(os.path.join(OUT, 'hex-mask.svg'), W, H, *f,
           title="Як прочитати шістнадцяткову маску можливостей")


def fig_xattr_layout():
    """Байтова розкладка security.capability у трьох ревізіях. Вставка api-."""
    W, H = 1180, 490
    f = []

    x0, fw, fh = 280, 140, 58
    MAGIC = ("#f7f9fc", MUTED)
    PERM = ("#eef3fd", NEG)
    INH = ("#fdecea", POS)
    ROOT = ("#eef7ee", FIELD)

    f.append(text(x0 + 3 * fw, 70, "зсув у байтах", size=11, color=MUTED))
    for i in range(7):
        f.append(text(x0 + i * fw, 94, str(i * 4), size=11, color=MUTED))

    rows = [
        (112, "VFS_CAP_REVISION_1\n0x01000000 · 12 Б",
         [("magic_etc", MAGIC), ("permitted[0]", PERM), ("inheritable[0]", INH)]),
        (202, "VFS_CAP_REVISION_2\n0x02000000 · 20 Б",
         [("magic_etc", MAGIC), ("permitted[0]", PERM), ("inheritable[0]", INH),
          ("permitted[1]", PERM), ("inheritable[1]", INH)]),
        (292, "VFS_CAP_REVISION_3\n0x03000000 · 24 Б",
         [("magic_etc", MAGIC), ("permitted[0]", PERM), ("inheritable[0]", INH),
          ("permitted[1]", PERM), ("inheritable[1]", INH), ("rootid", ROOT)]),
    ]
    for y, label, fields in rows:
        f.append(fitbox(40, y, 215, fh, label, size=12, fill=BG, stroke=MUTED))
        for i, (name, (fill, stroke)) in enumerate(fields):
            f.append(fitbox(x0 + i * fw, y, fw, fh, name, size=12,
                            fill=fill, stroke=stroke))

    b, _, _ = textbox(590, 428,
                      "кожне поле — 32-бітне ціле в порядку від молодшого байта;\n"
                      "magic_etc = номер ревізії, і ще 0x000001, коли піднято біт «діючий»",
                      size=13, fill="#f7f9fc")
    f.append(b)
    render(os.path.join(OUT, 'xattr-layout.svg'), W, H, *f,
           title="Розкладка розширеного атрибута security.capability")


if __name__ == '__main__':
    fig_one_bit_vs_names()
    fig_exec_channels()
    fig_ping_eras()
    fig_keepcaps_order()
    fig_hex_mask()
    fig_xattr_layout()
    print("ok")
