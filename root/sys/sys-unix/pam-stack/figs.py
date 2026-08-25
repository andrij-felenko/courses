# -*- coding: utf-8 -*-
"""Фігури до теми «PAM: стек модулів автентифікації»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_four_stacks():
    """Чотири незалежні списки перевірок і питання кожного."""
    W, H = 1120, 560
    f = []
    rows = [
        (90,  "auth",
              "чи це справді та людина —\nі які додаткові облікові дані їй видати"),
        (195, "account",
              "чи вільно цим записом користуватися\nзараз, звідси й саме цією службою"),
        (300, "password",
              "заміна самого секрету, коли він застарів\nабо коли зміни вимагає політика"),
        (405, "session",
              "що налаштувати навколо на вході\nй розібрати назад на виході"),
    ]
    for y, name, question in rows:
        b, _, _ = textbox(170, y, name, size=15, min_w=200)
        f.append(b)
        f.append(arrow(285, y, 385, y))
        f.append(fitbox(395, y - 40, 620, 80, question, size=13, fill="#f7f9fc"))
    b, _, _ = textbox(560, 505,
                      "не кожна служба зачіпає всі чотири: вхід за відкритим ключем обходить auth,\n"
                      "команда зміни пароля вживає лише password, а задача з cron не має auth узагалі",
                      size=13, fill="#eef3fd", stroke=NEG)
    f.append(b)
    render(os.path.join(OUT, 'four-stacks.svg'), W, H, *f,
           title="Чотири стеки PAM і питання, на яке відповідає кожен")


def fig_conversation():
    """Модуль формулює запит, а показує його програма."""
    W, H = 1120, 640
    f = []
    b, _, _ = textbox(560, 70,
                      "модуль pam_unix.so: «спитай рядок і не показуй набране»",
                      size=14, min_w=640)
    f.append(b)
    f.append(arrow(560, 105, 560, 168))
    f.append(fitbox(340, 178, 440, 74,
                    "повідомлення PAM_PROMPT_ECHO_OFF\nтекст: «Пароль:»",
                    size=13, fill="#eef3fd", stroke=NEG))
    f.append(arrow(560, 258, 560, 315))
    b, _, _ = textbox(560, 345, "розмовник — функція, яку дала сама програма",
                      size=13, fill="#f7f9fc", min_w=520)
    f.append(b)

    f.append(arrow(560, 375, 200, 442, color=MUTED))
    f.append(arrow(560, 375, 560, 442, color=MUTED))
    f.append(arrow(560, 375, 920, 442, color=MUTED))

    b, _, _ = textbox(200, 490, "текстовий login\nрядок у терміналі,\nвідлуння вимкнено",
                      size=12, min_w=260)
    f.append(b)
    b, _, _ = textbox(560, 490, "вітальний екран\nвіконце з полем,\nкрапки замість літер",
                      size=12, min_w=260)
    f.append(b)
    b, _, _ = textbox(920, 490, "sshd\nпакет протоколу\nдо клієнта на тому кінці",
                      size=12, min_w=260)
    f.append(b)

    b, _, _ = textbox(560, 600,
                      "назад приходять самі рядки — модуль не дізнається, звідки вони взялися",
                      size=13, fill="#eef3fd", stroke=NEG)
    f.append(b)
    render(os.path.join(OUT, 'conversation.svg'), W, H, *f,
           title="Розмовник PAM: хто формулює запит і хто його показує")


def fig_login_order():
    """Ідентичність міняється в самому кінці, після всіх стеків."""
    W, H = 1020, 680
    f = []
    steps = [
        (55,  'pam_start("login", …)', LINE, FILL),
        (140, "pam_authenticate()  ·  стек auth", LINE, FILL),
        (225, "pam_acct_mgmt()  ·  стек account", LINE, FILL),
        (310, "pam_setcred()  ·  додаткові облікові дані", LINE, FILL),
        (395, "pam_open_session()  ·  стек session", LINE, FILL),
        (480, "setgid → initgroups → setuid", POS, "#fdecea"),
        (565, "exec оболонки користувача", LINE, FILL),
    ]
    for y, label, stroke, fill in steps:
        b, _, _ = textbox(320, y, label, size=13, min_w=430,
                          stroke=stroke, fill=fill)
        f.append(b)
    for y in (55, 140, 225, 310, 395, 480):
        f.append(arrow(320, y + 21, 320, y + 64))

    b, _, _ = textbox(775, 380,
                      "pam_limits, pam_env,\npam_keyinit, pam_loginuid,\npam_systemd",
                      size=12, fill="#f7f9fc", min_w=260)
    f.append(b)
    f.append(line(545, 395, 640, 380, color=MUTED, sw=1.2))

    b, _, _ = textbox(775, 500,
                      "аж тут процес стає\nкористувачем: усе, що\nпотребувало прав, уже зроблено",
                      size=12, fill="#fdecea", stroke=POS, min_w=260)
    f.append(b)
    f.append(line(545, 480, 640, 500, color=POS, sw=1.2))

    b, _, _ = textbox(500, 640,
                      "на виході — pam_close_session() тим самим списком у зворотний бік",
                      size=13, fill="#eef3fd", stroke=NEG)
    f.append(b)
    render(os.path.join(OUT, 'login-order.svg'), W, H, *f,
           title="Порядок дій програми входу і місце зміни ідентичності")


def fig_pam_lineage():
    """Хронологія: одна пропозиція, три реалізації, нератифікована специфікація."""
    W, H = 1060, 640
    f = []
    spine = 300
    f.append(line(spine, 50, spine, 600, color=MUTED, sw=2, dash="5,5"))

    rows = [
        (78,  "жовтень 1995",
              "SunSoft подає до OSF пропозицію RFC 86.0\n«Unified Login with Pluggable Authentication Modules»",
              FILL, LINE),
        (160, "березень 1996",
              "доповідь про той самий задум на ACM CCS'96 —\nнаукова публікація, а не документ стандарту",
              FILL, MUTED),
        (242, "серпень 1996",
              "Linux-PAM — незалежна реалізація для Linux —\nвиходить у складі Red Hat Linux 3.0.4",
              "#eef3fd", NEG),
        (330, "червень 1997",
              "Open Group видає XSSO (документ P702) —\nі він назавжди лишається ПОПЕРЕДНІМ, а не стандартом",
              "#fff8e1", "#b8860b"),
        (420, "липень 1997",
              "Solaris 2.6 приносить рідну реалізацію Sun;\nтой самий каркас бере собі CDE",
              "#fdecea", POS),
        (520, "березень 2002",
              "OpenPAM заміняє Linux-PAM у FreeBSD;\nзгодом його беруть NetBSD, DragonFly й macOS",
              "#fdecea", POS),
    ]
    for y, when, what, fill, stroke in rows:
        f.append(text(spine - 34, y + 5, when, size=14, anchor="end", color=MUTED))
        f.append(circle(spine, y, 7, fill=BG, stroke=stroke, sw=2.5))
        lines = what.count("\n") + 1
        h = 34 + lines * 22
        f.append(fitbox(spine + 30, y - h / 2, 690, h, what, size=14,
                        fill=fill, stroke=stroke))

    f.append(fitbox(spine + 30, 588, 690, 44,
                    "спільним лишився інтерфейс для програм — розійшлися налаштування й набори модулів",
                    size=14, fill="#f4f6f8", stroke=MUTED))

    render(os.path.join(OUT, 'pam-lineage.svg'), W, H, *f,
           title="Хронологія PAM: пропозиція, три реалізації й специфікація, що не стала стандартом")


def fig_include_vs_substack():
    """Куди повертає sufficient: вклеювання проти окремого підстека."""
    W, H = 1180, 570
    f = []
    cols = (300, 880)

    heads = ("@include common-auth   ·   include", "substack common-auth")
    for cx, head in zip(cols, heads):
        b, _, _ = textbox(cx, 45, head, size=14, min_w=380, fill="#eef3fd", stroke=NEG)
        f.append(b)

    caps = ("рядки стають частиною того самого стека",
            "рядки виконуються як окремий підстек")
    for cx, cap in zip(cols, caps):
        f.append(text(cx, 165, cap, size=12, color=MUTED))

    # рамка підстека — праворуч, ширша за самі рядки
    f.append(rect(665, 185, 430, 115, fill=BG, stroke=MUTED, sw=1.2))

    for cx in cols:
        b, _, _ = textbox(cx, 115, "auth  required    pam_env.so", size=13, min_w=380)
        f.append(b)
        b, _, _ = textbox(cx, 213, "auth  sufficient  pam_sss.so", size=13, min_w=380,
                          stroke=POS, fill="#fdecea")
        f.append(b)
        b, _, _ = textbox(cx, 271, "auth  required    pam_unix.so", size=13, min_w=380)
        f.append(b)
        b, _, _ = textbox(cx, 350, "auth  required    pam_deny.so", size=13, min_w=380)
        f.append(b)

    # ліворуч: керування йде повз решту стека — просто до програми
    f.append(line(105, 213, 55, 213, color=POS, sw=1.8))
    f.append(line(55, 213, 55, 470, color=POS, sw=1.8))
    f.append(arrow(55, 470, 96, 470, color=POS))

    # праворуч: керування виходить із підстека й повертається в батьківський список
    f.append(line(1075, 213, 1125, 213, color=POS, sw=1.8))
    f.append(line(1125, 213, 1125, 350, color=POS, sw=1.8))
    f.append(arrow(1125, 350, 1076, 350, color=POS))

    b, _, _ = textbox(300, 470,
                      "успіх завершує ВЕСЬ стек:\n"
                      "програма одразу дістає PAM_SUCCESS,\n"
                      "рядок pam_deny.so не виконується",
                      size=12, min_w=400, fill="#f7f9fc")
    f.append(b)
    b, _, _ = textbox(880, 470,
                      "успіх завершує лише підстек і йде\n"
                      "в батьківський стек як результат ОДНОГО\n"
                      "модуля — далі виконується pam_deny.so",
                      size=12, min_w=400, fill="#f7f9fc")
    f.append(b)

    render(os.path.join(OUT, 'include-vs-substack.svg'), W, H, *f,
           title="Куди повертає sufficient: include проти substack")


if __name__ == '__main__':
    fig_four_stacks()
    fig_conversation()
    fig_login_order()
    fig_pam_lineage()
    fig_include_vs_substack()
    print("ok")
