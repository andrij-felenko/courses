# -*- coding: utf-8 -*-
"""Фігури до теми «Платформа авторизації PAM»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

def fig_pam_arch():
    """Трирівнева архітектура PAM: Застосунки -> libpam -> Модулі."""
    W, H = 1100, 520
    f = []

    # Рівень 1: Застосунки
    b1, _, _ = textbox(200, 110, "Застосунки\n(sshd, sudo, login, su)", size=14, min_w=240, fill="#f7f9fc", stroke=INK, bold=True)
    f.append(b1)

    # Рівень 2: libpam.so + /etc/pam.d/
    b2, _, _ = textbox(550, 110, "Бібліотека libpam.so\n(PAM API & SPI Двигун)", size=14, min_w=260, fill="#eef3fd", stroke=NEG, bold=True)
    f.append(b2)

    b2c, _, _ = textbox(550, 240, "Конфігурація /etc/pam.d/\n(правила стеків та прапорці)", size=13, min_w=260, fill="#ffffff", stroke=MUTED)
    f.append(b2c)

    # Рівень 3: Модулі PAM
    b3a, _, _ = textbox(900, 80, "pam_unix.so\n(shadow/passwd)", size=13, min_w=200, fill="#eef7ee", stroke=FIELD)
    b3b, _, _ = textbox(900, 160, "pam_faillock.so\n(блокування)", size=13, min_w=200, fill="#eef7ee", stroke=FIELD)
    b3c, _, _ = textbox(900, 240, "pam_limits.so\n(обмеження rlimit)", size=13, min_w=200, fill="#eef7ee", stroke=FIELD)
    b3d, _, _ = textbox(900, 320, "pam_systemd.so\n(cgroups/cgroupsv2)", size=13, min_w=200, fill="#eef7ee", stroke=FIELD)
    f.extend([b3a, b3b, b3c, b3d])

    # Зв'язки
    f.append(arrow(320, 110, 420, 110, color=LINE, sw=2))
    f.append(arrow(550, 160, 550, 205, color=MUTED, sw=1.5))

    f.append(arrow(680, 110, 800, 80, color=LINE, sw=1.5))
    f.append(arrow(680, 110, 800, 160, color=LINE, sw=1.5))
    f.append(arrow(680, 110, 800, 240, color=LINE, sw=1.5))
    f.append(arrow(680, 110, 800, 320, color=LINE, sw=1.5))

    # Пояснення внизу
    b_foot, _, _ = textbox(550, 440,
                           "Застосунок викликає стандартизований API (pam_authenticate), libpam зчитує стеки з /etc/pam.d/\n"
                           "та динамічно завантажує необхідні .so модулі через dlopen()",
                           size=13, fill="#f7f9fc", stroke=MUTED)
    f.append(b_foot)

    render(os.path.join(OUT, 'pam-arch.svg'), W, H, *f,
           title="Трирівнева архітектура Pluggable Authentication Modules")


def fig_pam_phase_flow():
    """Чотири фази управління та обчислення контрольних прапорців."""
    W, H = 1180, 540
    f = []

    # 4 фази
    phases = [
        ("1. auth", "Перевірка токена та\nвстановлення облікових даних"),
        ("2. account", "Перевірка терміну дії,\nдоступу за часом та блокування"),
        ("3. session", "Монтування home, rlimit,\nkeyring, systemd scope"),
        ("4. password", "Зміна пароля та перевірка\nскладності (pwquality)"),
    ]

    for i, (title, desc) in enumerate(phases):
        x = 160 + i * 280
        b, _, _ = textbox(x, 90, "%s\n\n%s" % (title, desc), size=13, min_w=240, fill="#eef3fd", stroke=NEG, bold=True)
        f.append(b)

    # Секція прапорців нижче
    f.append(text(590, 230, "Поведінка контрольних прапорців у стеку", size=14, bold=True, color=INK))

    flags = [
        ("required", "Невдача фіксується, але стек виконується далі — так приховано, який саме модуль відхилив запит.", "#fdecea", POS),
        ("requisite", "Невдача негайно перериває виконання стеку з помилкою — решта модулів не виконується.", "#fdecea", POS),
        ("sufficient", "Успіх негайно завершує стек із PAM_SUCCESS (якщо не було попередніх помилок required).", "#eef7ee", FIELD),
        ("optional", "Результат враховується лише якщо це єдиний модуль у стеку або решта повернули PAM_IGNORE.", "#f7f9fc", MUTED),
    ]

    for j, (flag, expl, fill_c, stroke_c) in enumerate(flags):
        y = 290 + j * 54
        f.append(fitbox(60, y, 160, 44, flag, size=13, fill=fill_c, stroke=stroke_c, bold=True))
        f.append(fitbox(240, y, 880, 44, expl, size=12, fill="#ffffff", stroke=MUTED))

    render(os.path.join(OUT, 'pam-phase-flow.svg'), W, H, *f,
           title="Фази управління PAM та логіка контрольних прапорців")


def fig_pam_conv_handshake():
    """Послідовність викликів між програмою, libpam та callback-функцією розмови."""
    W, H = 1080, 520
    f = []

    # Лінії учасників
    cols = [
        (180, "Застосунок\n(напр. sshd)"),
        (540, "Бібліотека\nlibpam.so"),
        (900, "PAM Модуль\n(напр. pam_unix.so)")
    ]

    for cx, label in cols:
        b, _, _ = textbox(cx, 60, label, size=13, min_w=200, fill="#eef3fd", stroke=NEG, bold=True)
        f.append(b)
        f.append(line(cx, 100, cx, 430, color=MUTED, dash="4,4"))

    # Виклики
    # 1. pam_start
    f.append(arrow(180, 130, 540, 130, color=LINE, sw=1.5))
    f.append(fitbox(220, 108, 280, 24, "1. pam_start(service, user, &conv)", size=11, fill="#ffffff", stroke=LINE))

    # 2. pam_authenticate
    f.append(arrow(180, 170, 540, 170, color=LINE, sw=1.5))
    f.append(fitbox(220, 148, 280, 24, "2. pam_authenticate(pamh, 0)", size=11, fill="#ffffff", stroke=LINE))

    # 3. libpam calls module
    f.append(arrow(540, 210, 900, 210, color=LINE, sw=1.5))
    f.append(fitbox(580, 188, 280, 24, "3. pam_sm_authenticate()", size=11, fill="#ffffff", stroke=LINE))

    # 4. module requests password via conv
    f.append(arrow(900, 260, 180, 260, color=POS, sw=1.5))
    f.append(fitbox(340, 238, 400, 24, "4. conv(PAM_PROMPT_ECHO_OFF, 'Password: ')", size=11, fill="#fdecea", stroke=POS))

    # 5. user enters secret, app returns struct pam_response
    f.append(arrow(180, 310, 900, 310, color=FIELD, sw=1.5))
    f.append(fitbox(340, 288, 400, 24, "5. response: struct pam_response { resp = 'secret' }", size=11, fill="#eef7ee", stroke=FIELD))

    # 6. module evaluates password against /etc/shadow
    f.append(arrow(900, 360, 540, 360, color=LINE, sw=1.5))
    f.append(fitbox(580, 338, 280, 24, "6. повертає PAM_SUCCESS", size=11, fill="#ffffff", stroke=LINE))

    # 7. pam_authenticate returns status
    f.append(arrow(540, 400, 180, 400, color=NEG, sw=1.5))
    f.append(fitbox(220, 378, 280, 24, "7. PAM_SUCCESS", size=11, fill="#eef3fd", stroke=NEG))

    render(os.path.join(OUT, 'pam-conv-handshake.svg'), W, H, *f,
           title="Протокол розмови (conversation handshake) у стеку PAM")


if __name__ == '__main__':
    fig_pam_arch()
    fig_pam_phase_flow()
    fig_pam_conv_handshake()
    print("ok")
