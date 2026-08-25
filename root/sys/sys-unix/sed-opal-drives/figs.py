# -*- coding: utf-8 -*-
"""Фігури до теми «Самошифрувальний носій: TCG Opal і підтримка sed-opal у ядрі»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def box(cx, cy, s, **kw):
    """textbox + межі рамки: (фрагмент, left, right, top, bottom)."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Ієрархія ключів: MEK не виходить, PIN лише відчиняє ворота ───────────
def fig_key_gate():
    W, H = 1120, 470
    f = []

    # межа носія
    f.append(line(250, 62, 250, 400, color=MUTED, sw=1.4, dash="6 5"))
    f.append(text(250, 54, "межа носія", size=12, color=MUTED))

    pin, pl, pr, pt, pb = box(130, 125, "PIN\nвід хоста", size=14, bold=True)
    kek, kl, kr, kt, kb = box(440, 125, "KEK\nвиводиться з PIN", size=14)
    mek, ml, mr, mt, mb = box(790, 125, "MEK — ключ носія\nназовні не виходить", size=14, bold=True)
    f += [pin, kek, mek]
    f.append(arrow(pr + 8, 125, kl - 8, 125))
    f.append(arrow(kr + 8, 125, ml - 8, 125))

    sec, sl, sr, st, sb2 = box(130, 335, "сектор\nвід хоста", size=14)
    enc, el, er, et, eb = box(790, 335, "шифратор AES-XTS\nу тракті даних", size=14)
    nand, nl, nr, nt, nb = box(1010, 335, "NAND:\nшифротекст", size=14)
    f += [sec, enc, nand]
    f.append(arrow(sr + 8, 335, el - 8, 335))
    f.append(arrow(er + 8, 335, nl - 8, 335))
    f.append(arrow(790, mb + 8, 790, et - 8))
    f.append(text(700, 240, "ключ подається лише тоді,", size=12, color=MUTED, anchor="end"))
    f.append(text(700, 258, "коли діапазон відімкнено", size=12, color=MUTED, anchor="end"))

    f.append(text(560, 438,
                  "GenKey → новий MEK: старий шифротекст лишається на місці, але прочитати його вже нічим",
                  size=13, color=POS))

    render(os.path.join(OUT, 'key-gate.svg'), W, H, *f,
           title="Ключ носія не виходить назовні: PIN лише відчиняє ворота")


# ── 2. Канал: від ioctl до модуля безпеки носія ────────────────────────────
def fig_channel():
    W, H = 1000, 620
    f = []

    b1, _, _, _, b1b = box(500, 82, "програма: ioctl(fd, IOC_OPAL_LOCK_UNLOCK, …)", size=13)
    b2, _, _, b2t, b2b = box(500, 168, "блоковий шар: sed_ioctl(), потрібен CAP_SYS_ADMIN", size=13)
    b3, _, _, b3t, b3b = box(500, 254, "block/sed-opal.c — сеанси, таблиці, потік токенів TCG", size=13, bold=True)
    b4, _, _, b4t, b4b = box(500, 340, "зворотний виклик send_recv(spsp = ComID, secp = 0x01)", size=13)
    f += [b1, b2, b3, b4]
    f.append(arrow(500, b1b + 6, 500, b2t - 6))
    f.append(arrow(500, b2b + 6, 500, b3t - 6))
    f.append(arrow(500, b3b + 6, 500, b4t - 6))

    t1, _, _, t1t, t1b = box(160, 452, "nvme_sec_submit\nSecurity Send / Receive", size=13)
    t2, _, _, t2t, t2b = box(500, 452, "sd_sec_submit\nSECURITY PROTOCOL OUT / IN", size=13)
    t3, _, _, t3t, t3b = box(840, 452, "libata → ATA\nTRUSTED SEND / RECEIVE", size=13)
    f += [t1, t2, t3]
    f.append(arrow(470, b4b + 6, 200, t1t - 6))
    f.append(arrow(500, b4b + 6, 500, t2t - 6))
    f.append(arrow(530, b4b + 6, 800, t3t - 6))

    f.append(fitbox(120, 545, 760, 54,
                    "модуль безпеки носія (TPer): таблиці, ключі, діапазони", size=14, bold=True))
    for x in (160, 500, 840):
        f.append(arrow(x, t1b + 6, x, 543))

    render(os.path.join(OUT, 'opal-channel.svg'), W, H, *f,
           title="Одна реалізація протоколу, три набори команд під нею")


# ── 3. Життя діапазону через вимкнення живлення ────────────────────────────
def fig_range_lifecycle():
    W, H = 1140, 420
    f = []

    f.append(text(50, 130, "стан діапазону", size=13, color=MUTED, anchor="start"))
    f.append(text(50, 272, "що віддає LBA 0", size=13, color=MUTED, anchor="start"))

    a1, a1l, a1r, _, a1b = box(360, 130, "замкнено", size=14, bold=True)
    a2, a2l, a2r, _, a2b = box(690, 130, "відімкнено", size=14, bold=True)
    a3, a3l, a3r, _, a3b = box(1000, 130, "замкнено", size=14, bold=True)
    f += [a1, a2, a3]

    f.append(arrow(a1r + 10, 130, a2l - 10, 130))
    f.append(text((a1r + a2l) / 2, 100, "Unlock з PIN, далі MBRDone", size=12, color=FIELD))
    f.append(arrow(a2r + 10, 130, a3l - 10, 130))
    f.append(text((a2r + a3l) / 2, 100, "втрата живлення", size=12, color=POS))

    c1, _, _, c1t, _ = box(360, 272, "тіньовий MBR\n(образ PBA)", size=13)
    c2, _, _, c2t, _ = box(690, 272, "справжні дані\nрозділу", size=13)
    c3, _, _, c3t, _ = box(1000, 272, "тіньовий MBR\n(образ PBA)", size=13)
    f += [c1, c2, c3]
    for x, top in ((360, c1t), (690, c2t), (1000, c3t)):
        f.append(line(x, a1b + 8, x, top - 8, color=MUTED, sw=1.2, dash="5 4"))

    f.append(text(570, 370,
                  "шифротекст на носії весь час той самий — замок керує доступом, а не вмістом",
                  size=13, color=MUTED))

    render(os.path.join(OUT, 'range-lifecycle.svg'), W, H, *f,
           title="Діапазон замикається сам: LockOnReset і тіньовий MBR")


# ── 4. Вкладення структур: усе виростає з opal_key ─────────────────────────
def fig_struct_nesting():
    W, H = 1300, 660
    f = []

    a, al, ar, at, ab = box(200, 300,
                            "struct opal_key\nlr · key_len · key_type\nkey[256]",
                            size=14, bold=True)
    b, bl, br, bt, bb = box(660, 130,
                            "struct opal_session_info\nwho: ADMIN1 / USER1…USER9\nsum · opal_key",
                            size=14)
    c, cl, cr, ct, cb = box(1080, 130,
                            "аргументи, що беруть session:\nopal_lock_unlock · opal_lr_status\nopal_user_lr_setup\nopal_new_pw (двічі)",
                            size=13)
    d, dl, dr, dt, db = box(760, 420,
                            "аргументи, що беруть ключ напряму:\nopal_lr_act · opal_lr_react · opal_sum_ranges\nopal_revert_lsp · opal_mbr_data · opal_mbr_done\nopal_shadow_mbr · opal_read_write_table",
                            size=13)
    f += [a, b, c, d]

    f.append(arrow(ar + 10, 250, bl - 10, 165))
    f.append(arrow(br + 10, 130, cl - 10, 130))
    f.append(arrow(ar + 10, 350, dl - 10, 400))

    f.append(fitbox(300, 560, 760, 56,
                    "без ключа взагалі: opal_status · opal_geometry · opal_discovery",
                    size=14))

    render(os.path.join(OUT, 'opal-structs.svg'), W, H, *f,
           title="Структури-аргументи sed-opal: два рівні вкладення над opal_key")


# ── 5. Родовід: специфікації TCG угорі, Linux і практика внизу ──────────────
def fig_lineage():
    W, H = 1700, 440
    f = []

    axis_y = 230
    f.append(line(60, axis_y, W - 90, axis_y, color=MUTED, sw=2))
    f.append(arrow(W - 95, axis_y, W - 55, axis_y, color=MUTED, sw=2))

    f.append(text(60, 58, "специфікації TCG", size=13, color=MUTED,
                  anchor="start", bold=True))
    f.append(text(60, 406, "Linux і практика", size=13, color=MUTED,
                  anchor="start", bold=True))

    up = [
        (0, "2009\nCore Spec 2.00\nOpal SSC 1.0"),
        (1, "2012\nOpal 2.00"),
        (2, "2015\nOpal 2.01\nOpalite · Pyrite"),
        (5, "2020\nRuby"),
        (6, "2022\nOpal 2.02"),
        (8, "2025\nOpal 2.30"),
    ]
    down = [
        (3, "2016–17\nядро 4.11\nsed-opal.c"),
        (4, "2018\nрозбір прошивок\nADV180028"),
        (7, "2024\ncryptsetup 2.7\n--hw-opal"),
    ]

    def col(i):
        return 110 + i * 185

    for i, s in up:
        x = col(i)
        body, l, r, t, b = box(x, 120, s, size=13)
        f.append(body)
        f.append(line(x, b + 6, x, axis_y - 8, color=MUTED, sw=1.2))
        f.append(circle(x, axis_y, 6, fill=FILL, stroke=INK))

    for i, s in down:
        x = col(i)
        body, l, r, t, b = box(x, 340, s, size=13)
        f.append(body)
        f.append(line(x, axis_y + 8, x, t - 6, color=MUTED, sw=1.2))
        f.append(circle(x, axis_y, 6, fill=INK, stroke=INK))

    render(os.path.join(OUT, 'opal-lineage.svg'), W, H, *f,
           title="Родовід специфікацій TCG Storage і підтримки Opal у Linux")


# ── 6. Розкладка буфера Level 0 Discovery ──────────────────────────────────
def fig_discovery_layout():
    W, H = 1340, 560
    f = []
    X0, WID = 95, 1150

    def strip(y, widths, labels, colors=None):
        x = X0
        for i, (w, s) in enumerate(zip(widths, labels)):
            col = colors[i] if colors else INK
            f.append(fitbox(x, y, w, 66, s, size=13, color=col))
            x += w

    f.append(text(X0, 66, "буфер цілком — стільки байтів, скільки повернув ioctl",
                  size=13, color=MUTED, anchor="start", bold=True))
    strip(84,
          [235, 190, 210, 215, 220, 80],
          ["заголовок\n48 байтів",
           "TPer\n0x0001",
           "Locking\n0x0002",
           "Geometry\n0x0003",
           "Opal SSC v2.00\n0x0203",
           "…"])

    f.append(text(X0, 232, "будь-який дескриптор: чотири байти шапки, далі дані",
                  size=13, color=MUTED, anchor="start", bold=True))
    strip(250, [235, 220, 180, 515],
          ["код можливості\nBE16",
           "версія у старшій\nпівбайті · 1 байт",
           "довжина len\n1 байт",
           "дані дескриптора — рівно len байтів"])
    f.append(text(X0 + WID, 348, "крок циклу: off += 4 + len",
                  size=13, color=FIELD, anchor="end"))

    f.append(text(X0, 400, "дані дескриптора Opal SSC v2.00 — зміщення від початку даних",
                  size=13, color=MUTED, anchor="start", bold=True))
    strip(418,
          [205, 195, 195, 200, 185, 170],
          ["+0 · 2 байти\nбазовий ComID",
           "+2 · 2 байти\nскільки ComID",
           "+4 · 1 байт\nперетин діапазонів",
           "+5 · 2 байти\nадмінів Locking SP",
           "+7 · 2 байти\nкористувачів",
           "+9, +10\nповодження PIN"],
          [INK, INK, INK, POS, POS, INK])

    f.append(text(X0, 524,
                  "два шістнадцятибітні поля лежать на непарних зміщеннях — накласти на буфер "
                  "структуру мовою C не вийде, читаємо побайтово",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'discovery-layout.svg'), W, H, *f,
           title="Level 0 Discovery: заголовок і ланцюг дескрипторів можливостей")


if __name__ == '__main__':
    fig_key_gate()
    fig_channel()
    fig_range_lifecycle()
    fig_struct_nesting()
    fig_lineage()
    fig_discovery_layout()
    print("ok")
