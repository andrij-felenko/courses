# -*- coding: utf-8 -*-
"""Фігури до теми «SSSD: демон, що тримає з'єднання з каталогом і кеш облікових записів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_anatomy():
    """Клієнти, сокети, респондери, спільний кеш і бекенд домену."""
    W, H = 1320, 800
    f = []

    CX = [505, 825, 1145]     # центри трьох колонок
    X = [380, 700, 1020]
    CW = 250

    # ── клієнтські процеси ──
    f.append(text(825, 30, "з боку машини", size=14, bold=True, color=MUTED))
    f.append(fitbox(X[0], 44, CW, 66, "будь-яка програма\n(nss_sss)", size=13,
                    fill="#eef3fd", stroke=NEG))
    f.append(fitbox(X[1], 44, CW, 66, "login, sshd\n(pam_sss)", size=13,
                    fill="#eef3fd", stroke=NEG))
    f.append(fitbox(X[2], 44, CW, 66, "sudo, ssh, autofs\n(власні клієнти)", size=13,
                    fill="#eef3fd", stroke=NEG))

    for cx in CX:
        f.append(arrow(cx, 112, cx, 146))

    # ── сокети ──
    f.append(fitbox(X[0], 150, CW, 66, "сокет імен\nчитає будь-хто", size=13))
    f.append(fitbox(X[1], 150, CW, 66, "сокет автентифікації\nлише привілейовані", size=13))
    f.append(fitbox(X[2], 150, CW, 66, "сокети правил\nі ключів", size=13))

    for cx in CX:
        f.append(arrow(cx, 218, cx, 258))

    # ── респондери ──
    f.append(fitbox(X[0], 262, CW, 56, "sssd_nss", size=14, fill="#eef7f0", stroke=FIELD))
    f.append(fitbox(X[1], 262, CW, 56, "sssd_pam", size=14, fill="#eef7f0", stroke=FIELD))
    f.append(fitbox(X[2], 262, CW, 56, "sssd_sudo, sssd_ssh", size=14, fill="#eef7f0", stroke=FIELD))

    for cx in CX:
        f.append(arrow(cx, 320, cx, 368))

    # ── кеш ──
    f.append(fitbox(380, 372, 890, 70,
                    "кеш на диску: /var/lib/sss/db/cache_<домен>.ldb\n"
                    "респондери тільки читають, пише лише бекенд",
                    size=13, fill="#fdf6e3", stroke="#b7791f"))

    f.append(arrow(825, 444, 825, 482))

    # ── бекенд ──
    f.append(fitbox(560, 486, 530, 70,
                    "sssd_be — процес домену\nпровайдери: id · auth · access · sudo",
                    size=13, fill="#eef7f0", stroke=FIELD))

    f.append(arrow(825, 558, 825, 596))

    # ── сервер ──
    f.append(text(825, 720, "з боку мережі", size=14, bold=True, color=MUTED))
    f.append(fitbox(640, 600, 370, 56, "каталог: LDAP, IPA, Active Directory",
                    size=13, fill="#f7f9fc"))

    # ── монітор ──
    f.append(fitbox(60, 262, 270, 76, "sssd — монітор\nзапускає й піднімає",
                    size=13, fill="#fdecea", stroke=POS))
    f.append(line(330, 290, 372, 290, color="#9aa1ab", sw=1.2, dash="5,5"))
    f.append(line(195, 340, 195, 520, color="#9aa1ab", sw=1.2, dash="5,5"))
    f.append(line(195, 520, 552, 520, color="#9aa1ab", sw=1.2, dash="5,5"))

    f.append(fitbox(60, 690, 1200, 90,
                    "розріз проходить по кешу: спереду відповідають негайно і тільки з нього,\n"
                    "ззаду ходять у мережу й тримають його свіжим.\n"
                    "зникнення сервера скасовує другу роботу й не чіпає першої",
                    size=13, fill="#eef3fd", stroke=NEG))

    render(os.path.join(OUT, 'anatomy.svg'), W, H, *f,
           title="Будова SSSD: респондери, кеш, бекенд")


def fig_lookup_levels():
    """Три рівні кеша і чим закінчується запит на кожному."""
    W, H = 1300, 640
    f = []

    f.append(fitbox(60, 40, 1180, 54,
                    "програма питає ім'я: getpwnam(\"andrij\")",
                    size=15, fill="#eef3fd", stroke=NEG))

    rows = [
        (150,
         "1 · кеш у пам'яті, /var/lib/sss/mc\n"
         "клієнтська бібліотека відображає файл у себе\n"
         "й читає прямо з пам'яті процесу",
         "влучили — відповідь без сокета\n"
         "й без перемикання контексту;\n"
         "демон навіть не дізнався про запит",
         "#eef7f0", FIELD),
        (272,
         "2 · респондер sssd_nss через локальний сокет\n"
         "дивиться кеш на диску та його терміни,\n"
         "а також пам'ять про те, кого нема",
         "запис чинний — віддає його;\n"
         "у негативному кеші — відразу\n"
         "чесне «такого користувача нема»",
         "#eef7f0", FIELD),
        (394,
         "3 · бекенд sssd_be питає каталог,\n"
         "кладе відповідь у кеш\n"
         "і повертає її респондерові",
         "каталог мовчить — домен іде в офлайн,\n"
         "і відповідь усе одно беруть із кеша,\n"
         "хай навіть застарілого",
         "#fdecea", POS),
    ]

    for y, left, right, fill, stroke in rows:
        f.append(fitbox(60, y, 560, 100, left, size=13))
        f.append(fitbox(680, y, 560, 100, right, size=13, fill=fill, stroke=stroke))
        f.append(arrow(624, y + 50, 676, y + 50))

    f.append(arrow(340, 252, 340, 268))
    f.append(arrow(340, 374, 340, 390))
    f.append(arrow(340, 96, 340, 146))

    f.append(fitbox(60, 524, 1180, 90,
                    "кожен наступний рівень дорожчий приблизно на порядок: пам'ять, локальний сокет, мережа.\n"
                    "перелічити всіх найдешевшим рівнем не можна за задумом — такий запит завжди йде до респондера,\n"
                    "тому «покажи всіх користувачів» коштує дорого навіть з теплим кешем",
                    size=13, fill="#eef3fd", stroke=NEG))

    render(os.path.join(OUT, 'lookup-levels.svg'), W, H, *f,
           title="Три рівні кеша SSSD")


def fig_online_offline():
    """Стан домену: онлайн і офлайн, і що бачить клієнт у кожному."""
    W, H = 1260, 580
    f = []

    f.append(text(330, 62, "домен онлайн", size=15, bold=True))
    f.append(text(910, 62, "домен офлайн", size=15, bold=True))

    f.append(fitbox(120, 84, 420, 150,
                    "запити йдуть у каталог,\n"
                    "кеш поповнюється,\n"
                    "терміни записів продовжуються",
                    size=13, fill="#eef7f0", stroke=FIELD))
    f.append(fitbox(700, 84, 420, 150,
                    "у мережу не ходимо взагалі,\n"
                    "відповіді лише з кеша,\n"
                    "вхід — за збереженою перевіркою",
                    size=13, fill="#eef3fd", stroke=NEG))

    f.append(mtext(620, 108, ["кілька операцій", "зірвалося поспіль"], size=12, lh=1.35))
    f.append(arrow(545, 152, 695, 152))

    f.append(arrow(695, 196, 545, 196))
    f.append(mtext(620, 222, ["чергова спроба", "врешті вдалася"], size=12, lh=1.35))

    f.append(fitbox(120, 288, 420, 96,
                    "клієнт чекає стільки,\n"
                    "скільки триває запит у каталог",
                    size=13, fill="#f7f9fc"))
    f.append(fitbox(700, 288, 420, 96,
                    "клієнт не чекає нічого:\n"
                    "таймаутів TCP уже ніхто не починає",
                    size=13, fill="#f7f9fc"))

    f.append(fitbox(120, 430, 1000, 110,
                    "стан домену береться не з окремої перевірки зв'язку, а з долі власних операцій бекенда.\n"
                    "тому «сервер не відповів» ніколи не перетворюється на «такого користувача нема» —\n"
                    "перше змінює стан демона, друге є відповіддю каталогу",
                    size=13, fill="#fdf6e3", stroke="#b7791f"))

    render(os.path.join(OUT, 'online-offline.svg'), W, H, *f,
           title="Онлайн і офлайн як стан домену")


if __name__ == '__main__':
    fig_anatomy()
    fig_lookup_levels()
    fig_online_offline()
    print("ok")
