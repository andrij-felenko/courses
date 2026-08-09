# -*- coding: utf-8 -*-
"""Фігури до теми «Каталог LDAP як мережеве джерело облікових записів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_entry_and_tree():
    """Дерево імен каталогу і той самий обліковий запис, розгорнутий у атрибути."""
    W, H = 1240, 700
    f = []

    f.append(text(280, 34, "імена складаються зі шляху", size=14, color=MUTED))

    b, _, _ = textbox(280, 78, "dc=firma,dc=ua", size=14, fill="#eef3fd", stroke=NEG)
    f.append(b)

    b, _, _ = textbox(150, 198, "ou=people", size=14)
    f.append(b)
    b, _, _ = textbox(420, 198, "ou=groups", size=14)
    f.append(b)
    f.append(arrow(280, 96, 152, 180))
    f.append(arrow(280, 96, 418, 180))

    b, _, _ = textbox(110, 318, "uid=andrij", size=14, fill="#eef7f0", stroke=FIELD)
    f.append(b)
    b, _, _ = textbox(272, 318, "uid=marta", size=14)
    f.append(b)
    b, _, _ = textbox(432, 318, "cn=dialout", size=14)
    f.append(b)
    f.append(arrow(150, 216, 112, 300))
    f.append(arrow(150, 216, 270, 300))
    f.append(arrow(420, 216, 432, 300))

    f.append(fitbox(50, 388, 460, 96,
                    "остання ланка — RDN, «uid=andrij»;\n"
                    "разом з усім, що вище, вона дає DN —\n"
                    "повне й єдине ім'я запису в каталозі",
                    size=13, fill="#f7f9fc"))

    # ── праворуч: сам запис ──
    f.append(text(880, 34, "той самий запис зсередини", size=14, color=MUTED))
    f.append(rect(560, 56, 640, 300, fill="#fbfcfe"))
    lines = [
        "dn: uid=andrij,ou=people,dc=firma,dc=ua",
        "objectClass: posixAccount",
        "objectClass: shadowAccount",
        "uid: andrij",
        "cn: Andrij Felenko",
        "uidNumber: 1000",
        "gidNumber: 1000",
        "homeDirectory: /home/andrij",
        "loginShell: /bin/bash",
        "userPassword: {CRYPT}$y$j9T$sIl…",
    ]
    f.append(mtext(586, 90, lines, size=13, anchor="start", lh=1.45))

    f.append(fitbox(560, 388, 640, 96,
                    "objectClass вирішує, які атрибути тут дозволені й обов'язкові:\n"
                    "сервер відмовить у записі, що не відповідає схемі.\n"
                    "«uid» — це логін, число живе окремо, в «uidNumber»",
                    size=13, fill="#eef3fd", stroke=NEG))

    f.append(fitbox(120, 552, 1000, 100,
                    "жоден із цих атрибутів не є для LDAP природним: каталог нічого не знає про Unix.\n"
                    "posixAccount, shadowAccount і posixGroup — це схема, дописана поверх загальної моделі,\n"
                    "щоб рядок /etc/passwd мав куди лягти",
                    size=13, fill="#eef7f0", stroke=FIELD))

    render(os.path.join(OUT, 'entry-and-tree.svg'), W, H, *f,
           title="Дерево імен каталогу і запис облікового рахунку")


def fig_search_then_bind():
    """Два різні питання до каталогу: пошук про особу і bind про секрет."""
    W, H = 1240, 640
    f = []

    b, _, _ = textbox(320, 66, "хто такий «andrij»?", size=15, bold=True,
                      fill="#eef3fd", stroke=NEG)
    f.append(b)
    b, _, _ = textbox(920, 66, "чи знає він пароль?", size=15, bold=True,
                      fill="#fdecea", stroke=POS)
    f.append(b)

    b, _, _ = textbox(320, 190,
                      "SEARCH\nbase: ou=people,dc=firma,dc=ua\nfilter: (uid=andrij)",
                      size=13)
    f.append(b)
    b, _, _ = textbox(920, 190,
                      "BIND\ndn: uid=andrij,ou=people,dc=firma,dc=ua\npassword: те, що ввела людина",
                      size=13)
    f.append(b)

    b, _, _ = textbox(620, 336, "сервер каталогу", size=15, fill="#f7f9fc")
    f.append(b)
    f.append(arrow(320, 236, 528, 318))
    f.append(arrow(920, 236, 712, 318))

    b, _, _ = textbox(320, 458,
                      "запис: uidNumber, gidNumber,\nhomeDirectory, loginShell",
                      size=13, fill="#eef7f0", stroke=FIELD)
    f.append(b)
    b, _, _ = textbox(920, 458,
                      "success або invalidCredentials —\nі жодного хеша назад",
                      size=13, fill="#eef7f0", stroke=FIELD)
    f.append(b)
    f.append(arrow(528, 356, 340, 428))
    f.append(arrow(712, 356, 900, 428))

    f.append(fitbox(120, 540, 1000, 80,
                    "клієнт не забирає хеш і не звіряє його сам: він просить сервер спробувати ним увійти.\n"
                    "тому userPassword звичайно закритий для читання — а часом його там і немає зовсім",
                    size=13, fill="#eef3fd", stroke=NEG))

    render(os.path.join(OUT, 'search-then-bind.svg'), W, H, *f,
           title="Пошук відповідає про особу, bind — про секрет")


def fig_client_shapes():
    """Бібліотека в кожному процесі проти одного демона з кешем."""
    W, H = 1240, 640
    f = []

    f.append(text(320, 36, "бібліотека в кожному процесі", size=14, bold=True, color=MUTED))
    f.append(text(920, 36, "один демон з кешем", size=14, bold=True, color=MUTED))
    f.append(line(620, 20, 620, 612, color="#cbd5e1", dash="6,6"))

    # ── ліворуч ──
    for cx, name in ((140, "ls -l"), (320, "sshd"), (500, "cron")):
        b, _, _ = textbox(cx, 92, name, size=13)
        f.append(b)
        f.append(arrow(cx, 110, cx, 182))
        b, _, _ = textbox(cx, 206, "nss_ldap", size=12, fill="#fdecea", stroke=POS)
        f.append(b)

    b, _, _ = textbox(320, 458, "сервер каталогу", size=14, fill="#f7f9fc")
    f.append(b)
    f.append(arrow(140, 226, 268, 436))
    f.append(arrow(320, 226, 320, 436))
    f.append(arrow(500, 226, 372, 436))

    f.append(fitbox(60, 524, 520, 88,
                    "три рукостискання TLS, три пошуки, спільного кешу немає;\n"
                    "каталог замовк — не заходить ніхто,\n"
                    "і навіть «ls -l» завмирає посеред виводу",
                    size=13, fill="#fdecea", stroke=POS))

    # ── праворуч ──
    for cx, name in ((740, "ls -l"), (920, "sshd"), (1100, "login")):
        b, _, _ = textbox(cx, 92, name, size=13)
        f.append(b)

    b, _, _ = textbox(920, 206, "nss_sss · pam_sss → локальний сокет", size=13,
                      fill="#eef3fd", stroke=NEG)
    f.append(b)
    f.append(arrow(740, 110, 830, 186))
    f.append(arrow(920, 110, 920, 186))
    f.append(arrow(1100, 110, 1010, 186))

    b, _, _ = textbox(920, 330, "демон sssd:\nодне з'єднання й кеш на диску", size=13,
                      fill="#eef7f0", stroke=FIELD)
    f.append(b)
    f.append(arrow(920, 226, 920, 300))

    b, _, _ = textbox(920, 458, "сервер каталогу", size=14, fill="#f7f9fc")
    f.append(b)
    f.append(arrow(920, 362, 920, 436))

    f.append(fitbox(660, 524, 520, 88,
                    "одне рукостискання на машину, а не на процес;\n"
                    "кеш переживає обрив мережі, тож вхід і «ls -l»\n"
                    "працюють, доки записи в ньому вважаються чинними",
                    size=13, fill="#eef7f0", stroke=FIELD))

    render(os.path.join(OUT, 'client-shapes.svg'), W, H, *f,
           title="Дві форми клієнта каталогу")


def fig_stack_shedding():
    """Як каталог скидав стос: DAP на OSI → шлюз ldapd → самостійний slapd."""
    W, H = 1300, 540
    f = []

    cols = [50, 500, 950]
    PW = 300

    f.append(text(cols[0] + PW / 2, 32, "1988 — X.500 і DAP", size=15, bold=True))
    f.append(text(cols[1] + PW / 2, 32, "1991–93 — шлюз", size=15, bold=True))
    f.append(text(cols[2] + PW / 2, 32, "1995–96 — власний сервер", size=15, bold=True))

    # ── 1988: усе на стосі OSI
    x = cols[0]
    f.append(fitbox(x, 60, PW, 44, "клієнт DUA", size=14, fill="#eef3fd", stroke=NEG))
    f.append(arrow(x + PW / 2, 104, x + PW / 2, 128))
    f.append(fitbox(x, 128, PW, 150,
                    "DAP\n"
                    "прикладний рівень (ACSE, ROSE)\n"
                    "рівень представлення (BER)\n"
                    "сеансовий рівень\n"
                    "транспорт і мережа OSI",
                    size=13, fill="#fdecea", stroke=POS))
    f.append(arrow(x + PW / 2, 278, x + PW / 2, 306))
    f.append(fitbox(x, 306, PW, 44, "сервер DSA", size=14, fill="#f7f9fc"))
    f.append(fitbox(x, 388, PW, 110,
                    "щоб спитати одне ім'я,\n"
                    "машина мусить нести\n"
                    "весь стос — і купити\n"
                    "його разом із системою",
                    size=13, fill="#fdecea", stroke=POS))

    # ── 1991–93: легкий протокол спереду, важкий позаду
    x = cols[1]
    f.append(fitbox(x, 60, PW, 44, "клієнт LDAP", size=14, fill="#eef3fd", stroke=NEG))
    f.append(arrow(x + PW / 2, 104, x + PW / 2, 128))
    f.append(fitbox(x, 128, PW, 44, "TCP, порт 389", size=14, fill="#eef7f0", stroke=FIELD))
    f.append(arrow(x + PW / 2, 172, x + PW / 2, 196))
    f.append(fitbox(x, 196, PW, 44, "шлюз ldapd", size=14))
    f.append(arrow(x + PW / 2, 240, x + PW / 2, 262))
    f.append(fitbox(x, 262, PW, 44, "DAP на стосі OSI", size=14, fill="#fdecea", stroke=POS))
    f.append(arrow(x + PW / 2, 306, x + PW / 2, 328))
    f.append(fitbox(x, 328, PW, 44, "сервер QUIPU", size=14, fill="#f7f9fc"))
    f.append(fitbox(x, 388, PW, 110,
                    "клієнт полегшав,\n"
                    "але OSI нікуди не зник —\n"
                    "він просто переїхав\n"
                    "за спину шлюзові",
                    size=13, fill="#f7f9fc"))

    # ── 1995–96: OSI немає з жодного боку
    x = cols[2]
    f.append(fitbox(x, 60, PW, 44, "клієнт LDAP", size=14, fill="#eef3fd", stroke=NEG))
    f.append(arrow(x + PW / 2, 104, x + PW / 2, 128))
    f.append(fitbox(x, 128, PW, 44, "TCP, порт 389", size=14, fill="#eef7f0", stroke=FIELD))
    f.append(arrow(x + PW / 2, 172, x + PW / 2, 306))
    f.append(fitbox(x, 306, PW, 44, "slapd із власною базою", size=14, fill="#eef7f0", stroke=FIELD))
    f.append(fitbox(x, 388, PW, 110,
                    "модель даних лишилася\n"
                    "від X.500, стос OSI\n"
                    "зник з обох кінців —\n"
                    "разом із потребою в DSA",
                    size=13, fill="#eef7f0", stroke=FIELD))

    render(os.path.join(OUT, 'stack-shedding.svg'), W, H, *f,
           title="Три покоління доступу до каталогу")


def fig_search_scope():
    """Три значення поля scope на одному й тому самому дереві."""
    W, H = 1240, 560
    f = []

    ON = dict(fill="#eef7f0", stroke=FIELD, sw=2)
    OFF = dict(fill="#ffffff", stroke="#c8ccd2", sw=1.2, color=MUTED)

    panels = [
        (200, "scope = base (0)", (True, False, False, False),
         "сам запис бази — і більше нічого;\n"
         "так перевіряють атрибути\n"
         "вже відомого DN"),
        (620, "scope = one (1)", (False, True, True, False),
         "лише прямі нащадки бази;\n"
         "сама база у відповідь\n"
         "не входить"),
        (1040, "scope = sub (2)", (True, True, True, True),
         "база й усе піддерево під нею —\n"
         "це те, чим шукають\n"
         "конкретну людину"),
    ]

    for cx, title, flags, note in panels:
        f.append(text(cx, 42, title, size=15, bold=True))

        st = [ON if fl else OFF for fl in flags]

        b, _, _ = textbox(cx, 110, "ou=people", size=13, **st[0])
        f.append(b)
        b, _, _ = textbox(cx - 100, 220, "uid=andrij", size=13, **st[1])
        f.append(b)
        b, _, _ = textbox(cx + 100, 220, "ou=temp", size=13, **st[2])
        f.append(b)
        b, _, _ = textbox(cx + 100, 330, "uid=olena", size=13, **st[3])
        f.append(b)

        f.append(line(cx, 128, cx - 100, 202, color="#9aa1ab", sw=1.2))
        f.append(line(cx, 128, cx + 100, 202, color="#9aa1ab", sw=1.2))
        f.append(line(cx + 100, 238, cx + 100, 312, color="#9aa1ab", sw=1.2))

        f.append(fitbox(cx - 165, 384, 330, 80, note, size=13, fill="#f7f9fc"))

    f.append(line(410, 62, 410, 470, color="#dfe3e8", sw=1))
    f.append(line(830, 62, 830, 470, color="#dfe3e8", sw=1))

    f.append(fitbox(130, 492, 980, 62,
                    "база каже, ДЕ шукати, а не ЩО: чим вужча база, тим менше сервер перебирає.\n"
                    "«sub» від кореня каталогу змушує його дивитися все дерево на кожен вхід",
                    size=13, fill="#eef3fd", stroke=NEG))

    render(os.path.join(OUT, 'search-scope.svg'), W, H, *f,
           title="Три області пошуку: base, one, sub")


if __name__ == '__main__':
    fig_entry_and_tree()
    fig_search_then_bind()
    fig_client_shapes()
    fig_stack_shedding()
    fig_search_scope()
    print("ok")
