# -*- coding: utf-8 -*-
"""Фігури до теми «Кільця ключів ядра: add_key, keyctl і довірені сертифікати»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_keyring_scopes():
    """Кільця в облікових даних процесу й порядок пошуку по них."""
    W, H = 1120, 610
    f = [text(560, 34, "Де ядро шукає ключ від імені процесу", size=17, bold=True)]

    f.append(mtext(70, 58, ["порядок", "пошуку"], size=12, color=MUTED))

    rows = [
        (110, "1", "кільце нитки",
         "своє в кожної нитки; заводиться на першу вимогу\nй зникає разом із ниткою"),
        (210, "2", "кільце процесу",
         "спільне для всіх ниток одного процесу"),
        (310, "3", "кільце сеансу",
         "успадковується дітьми при fork і переживає exec —\nодне на весь вхід у систему"),
    ]
    for y, n, name, note in rows:
        f.append(circle(70, y, 16))
        f.append(text(70, y + 5, n, size=14, bold=True))
        b, _, _ = textbox(250, y, name, size=15, min_w=250)
        f.append(b)
        f.append(fitbox(410, y - 34, 660, 68, note, size=13, fill="#f7f9fc"))

    f.append(arrow(250, 129, 250, 189))
    f.append(arrow(250, 229, 250, 289))

    f.append(line(250, 330, 250, 400, dash="5 4"))
    f.append(arrow(250, 400, 250, 410))
    f.append(text(268, 366, "посилання", size=12, color=MUTED, anchor="start"))

    b, _, _ = textbox(250, 430, "кільце користувача", size=15, min_w=250)
    f.append(b)
    f.append(fitbox(410, 396, 660, 68,
                    "одне на UID; посилання на нього кладе в сеанс\nмодуль pam_keyinit під час входу в систему",
                    size=13, fill="#f7f9fc"))

    f.append(line(40, 505, 1080, 505, color=MUTED, dash="6 5"))

    b, _, _ = textbox(250, 555, "стале кільце користувача", size=15, min_w=250)
    f.append(b)
    f.append(fitbox(410, 521, 660, 68,
                    "поза будь-яким процесом і поза пошуком;\nберуть окремо — keyctl get_persistent",
                    size=13, fill="#f7f9fc"))

    render(os.path.join(OUT, 'keyring-scopes.svg'), W, H, *f)


def fig_request_key_upcall():
    """Що робить ядро, коли потрібного ключа немає на кільцях."""
    W, H = 1200, 560
    f = [text(600, 34, "Виклик назовні: ядру бракує ключа", size=17, bold=True)]

    steps = [
        (200, 130, "Ядро потребує ключ\nі не знаходить його\nна кільцях того, хто просить"),
        (600, 130, "Створює ключ у стані\n«ще не наповнений»\nі чіпляє його на кільце"),
        (1000, 130, "Разом із ним — ключ-повноваження\nрівно на цей один ключ"),
        (1000, 340, "Запускає /sbin/request-key;\nтой за /etc/request-key.conf\nобирає обробник"),
        (600, 340, "Обробник у просторі користувача\nдобуває матеріал: Kerberos, DNS,\nвідображення ідентифікаторів"),
        (200, 340, "keyctl instantiate — ключ наповнено,\nтой, хто чекав, прокидається"),
    ]
    for cx, cy, s in steps:
        f.append(fitbox(cx - 160, cy - 46, 320, 92, s, size=13))

    f.append(arrow(360, 130, 440, 130))
    f.append(arrow(760, 130, 840, 130))
    f.append(arrow(1000, 176, 1000, 294))
    f.append(arrow(840, 340, 760, 340))
    f.append(arrow(440, 340, 360, 340))

    f.append(arrow(600, 386, 600, 434))
    f.append(fitbox(370, 440, 460, 76,
                    "не вийшло → від'ємне наповнення:\nпомилка кешується, і наступні запити\nне плодять нових процесів",
                    size=13, fill="#fdecea"))

    render(os.path.join(OUT, 'request-key-upcall.svg'), W, H, *f)


def fig_trusted_keyrings():
    """Кільця довіри, які тримає саме ядро, і хто до них звертається."""
    W, H = 1220, 630
    f = [text(610, 36, "Кільця довіри самого ядра", size=17, bold=True)]

    f.append(fitbox(30, 76, 340, 88,
                    ".builtin_trusted_keys\nвбудовані в образ ядра;\nна ходу не додати нічого", size=13))
    f.append(fitbox(420, 76, 340, 88,
                    ".machine\nключі власника машини,\nвнесені через MOK (з ядра 5.18)", size=13))
    f.append(fitbox(840, 76, 340, 88,
                    ".platform\nключі з бази UEFI та MOK;\nлише для образу при kexec", size=13))

    f.append(fitbox(190, 256, 420, 88,
                    ".secondary_trusted_keys\nросте на ходу — але приймає лише те,\nщо підписане вже довіреним ключем",
                    size=13))

    f.append(arrow(200, 168, 320, 250))
    f.append(arrow(590, 168, 480, 250))

    f.append(fitbox(650, 258, 420, 84,
                    "обмеження висить на самому кільці,\nа не на тому, хто просить:\nпитання не про права процесу,\nа про ланцюг підпису",
                    size=12, fill="#f7f9fc"))

    f.append(fitbox(230, 422, 340, 76, "перевірка підпису\nмодуля ядра", size=14))
    f.append(fitbox(840, 422, 340, 76, "перевірка образу\nдля kexec", size=14))

    f.append(arrow(400, 348, 400, 418))
    f.append(arrow(1130, 168, 1130, 418))

    f.append(line(40, 540, 1180, 540, color=MUTED, dash="6 5"))
    f.append(fitbox(210, 556, 800, 56,
                    ".blacklist — хеші й сертифікати, які відхиляють завжди,\nнавіть коли ланцюг підпису математично сходиться",
                    size=13, fill="#fdecea"))

    render(os.path.join(OUT, 'trusted-keyrings.svg'), W, H, *f)


fig_keyring_scopes()
fig_request_key_upcall()
fig_trusted_keyrings()
print("ok")
