# -*- coding: utf-8 -*-
"""Фігури до теми «База облікових записів: passwd, group, shadow і шар NSS»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def panel(x, y, w, h, head, record, note):
    """Панель файлу: заголовок, зразок рядка, підпис під ним."""
    out = rect(x, y, w, h, fill="#f7f9fc")
    cx = x + w / 2
    out += text(cx, y + 34, head, size=15, bold=True)
    out += text(cx, y + 78, record, size=12, color=NEG)
    out += mtext(cx, y + 118, note, size=12, color=MUTED)
    return out


def fig_lookup_path():
    """Шлях одного запиту: програма → libc → перемикач → модуль → джерело."""
    W, H = 1180, 640
    f = []

    b, _, _ = textbox(170, 92, "процес\n(ls -l, id, sshd)", size=14)
    f.append(b)
    f.append(arrow(252, 92, 468, 92))

    b, _, _ = textbox(590, 92, "libc: getpwuid_r(1000, …)\nодин контракт на всі джерела", size=14)
    f.append(b)
    f.append(arrow(590, 130, 590, 182))

    b, _, _ = textbox(590, 214, "перемикач NSS", size=15, fill="#eef3fd", stroke=NEG)
    f.append(b)

    b, _, _ = textbox(960, 214, "/etc/nsswitch.conf\npasswd: files systemd sss", size=13, fill="#f7f9fc")
    f.append(b)
    f.append(arrow(852, 214, 672, 214))

    mods = [
        (250, "libnss_files.so.2"),
        (590, "libnss_systemd.so.2"),
        (930, "libnss_sss.so.2"),
    ]
    for mx, name in mods:
        f.append(arrow(590, 246, mx, 330))
        b, _, _ = textbox(mx, 356, name, size=13)
        f.append(b)
        f.append(arrow(mx, 386, mx, 452))

    srcs = [
        (250, "/etc/passwd\n/etc/group"),
        (590, "динамічні записи\nслужб systemd"),
        (930, "кеш SSSD, а за ним\nмережевий каталог"),
    ]
    for sx, txt in srcs:
        f.append(fitbox(sx - 130, 460, 260, 74, txt, size=13, fill="#f4f6f8"))

    f.append(fitbox(140, 562, 900, 56,
                    "ядро в цьому ланцюгу не бере участі: воно порівнює числа\n"
                    "й не відкриває жодного з цих файлів",
                    size=13, fill="#eef7f0", stroke=FIELD))

    render(os.path.join(OUT, 'lookup-path.svg'), W, H, *f,
           title="Як число перетворюється на ім'я: перемикач між джерелами")


def fig_record_split():
    """Один обліковий запис, розрізаний на чотири файли з різними правами."""
    W, H = 1140, 580
    f = []
    f.append(panel(70, 70, 480, 170, "/etc/passwd — rw-r--r--",
                   "andrij:x:1000:1000:Andrij:/home/andrij:/bin/bash",
                   "ім'я · «x» на місці хеша · UID · GID\nGECOS · домашній каталог · оболонка"))
    f.append(panel(590, 70, 480, 170, "/etc/shadow — rw-r----- root:shadow",
                   "andrij:$y$j9T$sIl…:20180:0:99999:7:::",
                   "хеш із сіллю · коли міняли пароль\nмежі старіння · дата вимкнення запису"))
    f.append(panel(70, 300, 480, 170, "/etc/group — rw-r--r--",
                   "dialout:x:20:andrij,marta",
                   "назва · GID · список учасників\nлежить на групі, а не на людині"))
    f.append(panel(590, 300, 480, 170, "/etc/gshadow — rw-r----- root:shadow",
                   "dialout:!::andrij,marta",
                   "пароль групи (майже не вживають)\nі адміністратори групи"))
    f.append(fitbox(120, 500, 900, 56,
                    "поділ проведено за одним критерієм: усе, потрібне для показу імені, лишилось відкритим;\n"
                    "усе, що допомагає підбирати пароль, поїхало у файл, доступний лише root",
                    size=13, fill="#eef3fd", stroke=NEG))
    render(os.path.join(OUT, 'record-split.svg'), W, H, *f,
           title="Один запис, розрізаний за правом на читання")


def fig_status_action():
    """Чотири відповіді модуля й типова дія перемикача на кожну."""
    W, H = 1120, 540
    f = []
    rows = [
        (120, "SUCCESS — знайшов запис", "return — віддати відповідь", FIELD),
        (200, "NOTFOUND — такого нема", "continue — питати наступне джерело", LINE),
        (280, "UNAVAIL — не зміг спитати", "continue — питати наступне джерело", POS),
        (360, "TRYAGAIN — зайнято зараз", "continue — питати наступне джерело", LINE),
    ]
    for y, left, right, color in rows:
        b, _, _ = textbox(260, y, left, size=14, stroke=color)
        f.append(b)
        f.append(arrow(400, y, 620, y))
        b, _, _ = textbox(790, y, right, size=14)
        f.append(b)
    f.append(fitbox(110, 432, 900, 76,
                    "різниця між «такого нема» і «не зміг спитати» — уся безпека конструкції:\n"
                    "звести їх в одну відповідь означає, що зникнення каталогу з мережі\n"
                    "мовчки перетворює всіх його користувачів на неіснуючих",
                    size=13, fill="#fdecea", stroke=POS))
    render(os.path.join(OUT, 'status-action.svg'), W, H, *f,
           title="Що перемикач робить із відповіддю модуля")


def fig_conf_line():
    """Розбір складеного рядка nsswitch.conf: до кого прив'язані дужки."""
    W, H = 1120, 410
    f = []

    tokens = [
        (110, "passwd:"),
        (270, "files"),
        (450, "[SUCCESS=merge]"),
        (620, "sss"),
        (810, "[!UNAVAIL=return]"),
        (1000, "ldap"),
    ]
    for cx, tok in tokens:
        mark = tok.startswith("[")
        b, _, _ = textbox(cx, 80, tok, size=14,
                          fill="#eef3fd" if mark else FILL,
                          stroke=NEG if mark else LINE)
        f.append(b)

    notes = [
        (110, 168, 180, "ім'я бази\nз таблиці нижче"),
        (450, 505, 520, "дужки правлять ПОПЕРЕДНІЙ\nзнайшов у files — не спинятись,\nа злити зі списком із sss"),
        (810, 866, 880, "«!» — усе, крім UNAVAIL:\nsss відповів будь-як, окрім\n«не зміг» — спинитись тут"),
    ]
    for sx, ex, cx, txt in notes:
        f.append(arrow(sx, 100, ex, 172))
        b, _, _ = textbox(cx, 210, txt, size=13)
        f.append(b)

    f.append(fitbox(110, 300, 900, 76,
                    "рядок читається зліва направо; дужки стоять ПІСЛЯ модуля\n"
                    "й міняють дію тільки для нього, а не для всього рядка.\n"
                    "решта модулів лишається з типовим: success=return, три інші статуси=continue",
                    size=13, fill="#eef7f0", stroke=FIELD))

    render(os.path.join(OUT, 'conf-line.svg'), W, H, *f,
           title="Як розбирається складений рядок /etc/nsswitch.conf")


def fig_nss_buffer():
    """Куди модуль складає відповідь: пакування рядків у чужий буфер."""
    W, H = 1240, 620
    f = []

    # ── поля структури, які є вказівниками ──
    ptr_fields = [
        (175, "pw_name"),
        (325, "pw_passwd"),
        (510, "pw_dir"),
        (735, "pw_shell"),
    ]
    for cx, name in ptr_fields:
        b, _, _ = textbox(cx, 110, name, size=14, stroke=NEG, fill="#eef3fd")
        f.append(b)
        f.append(arrow(cx, 132, cx, 236))

    b, _, _ = textbox(1030, 110,
                      "pw_uid = 6001\npw_gid = 6001\nчисла лежать у самій\nструктурі — місця в буфері\nне просять",
                      size=13, stroke=FIELD, fill="#eef7f0")
    f.append(b)

    f.append(text(860, 222, "буфер викликача: buffer, buflen", size=13,
                  color=MUTED, anchor="start"))

    # ── сам буфер: рядки, покладені один за одним ──
    f.append(rect(80, 240, 1090, 84, fill=BG))
    cells = [
        (90, 170, "andrij\\0"),
        (270, 110, "*\\0"),
        (390, 240, "/srv/proj/andrij\\0"),
        (640, 190, "/usr/sbin/nologin\\0"),
        (840, 320, "вільний хвіст"),
    ]
    for x, w, txt in cells:
        f.append(fitbox(x, 252, w, 60, txt, size=13,
                        fill="#f4f6f8" if "хвіст" not in txt else BG))

    # ── той самий буфер для групи: вирівнювання під масив вказівників ──
    f.append(text(80, 382, "той самий буфер для struct group", size=13,
                  color=MUTED, anchor="start"))
    f.append(text(690, 382, "масив gr_mem мусить лягти на межу sizeof(char*)",
                  size=13, color=POS, anchor="start"))

    f.append(rect(80, 400, 1090, 84, fill=BG))
    gcells = [
        (90, 150, "dialout\\0", "#f4f6f8"),
        (250, 80, "x\\0", "#f4f6f8"),
        (340, 150, "andrij\\0", "#f4f6f8"),
        (500, 140, "marta\\0", "#f4f6f8"),
        (650, 150, "вирівнювання", "#fdecea"),
        (810, 110, "&andrij", "#eef3fd"),
        (930, 110, "&marta", "#eef3fd"),
        (1050, 110, "NULL", "#eef3fd"),
    ]
    for x, w, txt, fill in gcells:
        f.append(fitbox(x, 412, w, 60, txt, size=13, fill=fill))

    f.append(fitbox(80, 512, 1090, 84,
                    "не влізло — це НЕ «такого користувача нема»:\n"
                    "модуль кладе *errnop = ERANGE і повертає NSS_STATUS_TRYAGAIN,\n"
                    "після чого libc бере буфер удвічі більший і питає те саме ще раз",
                    size=13, fill="#eef3fd", stroke=NEG))

    render(os.path.join(OUT, 'nss-buffer.svg'), W, H, *f,
           title="Що модуль кладе в буфер викликача")


if __name__ == '__main__':
    fig_lookup_path()
    fig_record_split()
    fig_status_action()
    fig_conf_line()
    fig_nss_buffer()
    print("ok")
