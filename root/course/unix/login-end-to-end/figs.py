# -*- coding: utf-8 -*-
"""Генератор схем для теми login-end-to-end."""
import os
import sys

# Підключаємо svgkit з кореневої папки scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_pipeline_end_to_end():
    """Повний наскрізний ланцюг входу в систему."""
    w, h = 940, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Наскрізний конвеєр входу в Linux: від термінала до командного рядка", size=16, bold=True))

    # Стовпчики-етапи (6 колонок)
    cols = [
        ("1. Вхідний канал", ["getty / login", "(віртуальна консоль)", "або sshd daemon", "(мережевий сеанс)"], "#eaf0fd", NEG),
        ("2. Стек PAM", ["pam_authenticate()", "pam_acct_mgmt()", "звірка /etc/shadow", "хеш yescrypt/SHA"], "#fdf2e9", "#d35400"),
        ("3. systemd-logind", ["D-Bus CreateSession()", "cgroup v2 scope", "user-1000.slice", "/run/user/1000"], "#f4ecf7", "#8e44ad"),
        ("4. Зниження прав", ["initgroups(user)", "setgid(gid)", "setuid(uid)", "setsid() + TIOCSCTTY"], "#fdecea", POS),
        ("5. Сеанс & Ліміти", ["pam_limits (setrlimit)", "pam_env (оточення)", "pam_motd (/etc/motd)", "chdir($HOME)"], "#e8f8f5", "#16a085"),
        ("6. Login Shell", ["execve('/bin/bash')", "argv[0] = '-bash'", "/etc/profile", "~/.bash_profile → $PS1"], "#eafaf1", FIELD)
    ]

    col_w = 136
    gap = 14
    start_x = (w - (len(cols) * col_w + (len(cols) - 1) * gap)) / 2
    top_y = 65
    box_h = 180

    for i, (head, lines, bg_col, border_col) in enumerate(cols):
        cx = start_x + i * (col_w + gap)
        # Заголовок блоку
        frags.append(rect(cx, top_y, col_w, 32, fill=border_col, stroke=border_col, rx=4))
        frags.append(text(cx + col_w / 2, top_y + 20, head, size=12, color="#ffffff", bold=True))

        # Тіло блоку
        frags.append(rect(cx, top_y + 32, col_w, box_h - 32, fill=bg_col, stroke=border_col, sw=1.2, rx=4))
        content_text = "\n".join(lines)
        frags.append(mtext(cx + col_w / 2, top_y + 60, content_text, size=11, color=INK, lh=1.4))

        # Стрілка до наступного блоку
        if i < len(cols) - 1:
            arr_y = top_y + box_h / 2
            frags.append(arrow(cx + col_w + 1, arr_y, cx + col_w + gap - 1, arr_y, color=LINE, sw=1.5))

    # Нижній пояснювальний блок: Межа привілеїв root та користувача
    bar_y = 275
    frags.append(rect(start_x, bar_y, 440, 60, fill="#feebe8", stroke=POS, sw=1.5, rx=6))
    frags.append(text(start_x + 220, bar_y + 24, "Рівень привілеїв: root (UID 0, CAP_SYS_ADMIN)", size=12, color=POS, bold=True))
    frags.append(text(start_x + 220, bar_y + 46, "Доступ до /etc/shadow, D-Bus system bus, виклики setsid/setuid", size=11, color=INK))

    frags.append(rect(start_x + 460, bar_y, 426, 60, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(start_x + 673, bar_y + 24, "Рівень привілеїв: користувач (UID 1000, unprivileged)", size=12, color=FIELD, bold=True))
    frags.append(text(start_x + 673, bar_y + 46, "Ізольована cgroup, власні файли в $HOME, обмеження setrlimit", size=11, color=INK))

    # Діагностичні маркери відмов знизу
    diag_y = 360
    frags.append(rect(start_x, diag_y, w - 2 * start_x, 95, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(start_x + 15, diag_y + 22, "Типові точки зупинки конвеєра (Failure Modes):", size=12, bold=True, anchor="start"))

    failures = [
        "• Етап 2 (PAM/Shadow): Account locked ('!'), пароль прострочено (sp_expire), PAM auth_err",
        "• Етап 3 (logind): D-Bus timeout, помилка виділення сесії, збій створення /run/user/UID",
        "• Етап 4 (Права): EPERM при setuid, помилка initgroups (зайві або відсутні GID)",
        "• Етап 5-6 (Оболонка): Переповнена квота $HOME (EDQUOT), відсутня оболонка в /etc/shells"
    ]
    frags.append(mtext(start_x + 25, diag_y + 42, "\n".join(failures), size=11, color=INK, anchor="start", lh=1.35))

    render(os.path.join(OUT_DIR, "login-pipeline-end-to-end.svg"), w, h, *frags)


def fig_pam_stack_decision():
    """Дерево прийняття рішень стеку PAM."""
    w, h = 900, 440
    frags = []

    frags.append(text(w / 2, 28, "Логіка обчислення результатів у модульному стеку PAM", size=16, bold=True))

    # 4 блоки прапорців
    flags = [
        ("required", "Обов'язковий", [
            "У разі помилки: позначає стек як невдалий,",
            "але ПРОДОВЖУЄ виконання наступних модулів.",
            "Приховує від зловмисника точку відмови."
        ], "#fdecea", POS),
        ("requisite", "Критичний", [
            "У разі помилки: НЕГАЙНО перериває стек",
            "і повертає помилку застосунку.",
            "Швидкий вихід без зайвих перевірок."
        ], "#fbeee6", "#e67e22"),
        ("sufficient", "Достатній", [
            "У разі успіху: якщо попередні required успішні,",
            "НЕГАЙНО завершує фазу з успіхом.",
            "Дозволяє альтернативні гілки входу."
        ], "#eafaf1", FIELD),
        ("optional", "Опціональний", [
            "Результат враховується ЛИШЕ тоді, коли в фазі",
            "немає інших модулів (required/sufficient).",
            "Використовується для додаткових дій."
        ], "#eaf0fd", NEG)
    ]

    card_w = 410
    card_h = 130
    gx, gy = 30, 60
    spacing_x = 30
    spacing_y = 20

    for idx, (fl_name, fl_title, desc_lines, bg_col, border_col) in enumerate(flags):
        row = idx // 2
        col = idx % 2
        x = gx + col * (card_w + spacing_x)
        y = gy + row * (card_h + spacing_y)

        frags.append(rect(x, y, card_w, card_h, fill=bg_col, stroke=border_col, sw=1.5, rx=6))
        # Шапка картки
        frags.append(text(x + 15, y + 26, f"Прапорець: {fl_name} ({fl_title})", size=13, color=border_col, bold=True, anchor="start"))
        frags.append(line(x + 15, y + 36, x + card_w - 15, y + 36, color=border_col, sw=1))
        # Опис
        frags.append(mtext(x + 15, y + 58, "\n".join(desc_lines), size=11, color=INK, anchor="start", lh=1.35))

    # Нижній блок: Складний синтаксис [success=N ...]
    bot_y = 350
    frags.append(rect(gx, bot_y, w - 2 * gx, 72, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(gx + 15, bot_y + 22, "Розширений синтаксис дій: [success=N new_authtok_reqd=ok default=bad]", size=12, bold=True, anchor="start"))
    frags.append(text(gx + 15, bot_y + 44, "• Дозволяє стрибки через N рядків (jump), скидання накопиченого статусу (reset) та явне ігнорування (ignore).", size=11, color=INK, anchor="start"))
    frags.append(text(gx + 15, bot_y + 60, "• Механізми include та substack забезпечують модульну композицію політик з /etc/pam.d/common-* та system-auth.", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT_DIR, "pam-stack-decision-tree.svg"), w, h, *frags)


def fig_privilege_drop_sequence():
    """Послідовність зміни привілеїв та створення сесії."""
    w, h = 920, 420
    frags = []

    frags.append(text(w / 2, 28, "Критичний порядок скидання привілеїв та ізоляції сесії в ядрі", size=16, bold=True))

    steps = [
        ("Крок 1: initgroups(user, gid)", "Зчитує допоміжні групи з /etc/group через NSS", "Викликає setgroups() поки є привілей root", "#fdecea", POS),
        ("Крок 2: setgid(primary_gid)", "Встановлює real, effective та saved GID процесу", "Процес переходить у первинну групу користувача", "#fbeee6", "#e67e22"),
        ("Крок 3: setuid(user_uid)", "Остаточне скидання UID процесу (real=eff=saved=UID)", "Незворотна втрата привілею root (CAP_SETUID зникає)", "#fef9e7", "#d4ac0d"),
        ("Крок 4: setsid() + TIOCSCTTY", "Створення нової сесії та групи процесів (SID = PID)", "Прив'язка керуючого термінала /dev/pts/N або tty1", "#eaf0fd", NEG),
        ("Крок 5: execve(shell, ['-bash'])", "Заміна образу пам'яті на оболонку користувача", "argv[0]='-bash' вказує оболонці режим Login Shell", "#eafaf1", FIELD)
    ]

    box_w = 840
    box_h = 52
    start_x = (w - box_w) / 2
    start_y = 55
    gap_y = 15

    for i, (title_text, desc1, desc2, bg_col, border_col) in enumerate(steps):
        y = start_y + i * (box_h + gap_y)

        frags.append(rect(start_x, y, box_w, box_h, fill=bg_col, stroke=border_col, sw=1.5, rx=6))
        # Номер і заголовок зліва
        frags.append(text(start_x + 20, y + 31, title_text, size=13, color=border_col, bold=True, anchor="start"))
        # Опис справа
        frags.append(text(start_x + 360, y + 22, desc1, size=11, color=INK, anchor="start"))
        frags.append(text(start_x + 360, y + 40, desc2, size=11, color=MUTED, anchor="start"))

        # Стрілка вниз
        if i < len(steps) - 1:
            arr_x = start_x + 140
            frags.append(arrow(arr_x, y + box_h, arr_x, y + box_h + gap_y, color=LINE, sw=1.5))

    # Попередження про порушення порядку
    warn_y = start_y + len(steps) * (box_h + gap_y) + 5
    frags.append(rect(start_x, warn_y, box_w, 42, fill="#fdedec", stroke=POS, sw=1.5, rx=6))
    frags.append(text(start_x + 15, warn_y + 26, "⚠ Фатальна помилка: якщо викликати setuid() ДО initgroups() чи setgid(), процес втрачає привілей і отримує EPERM!", size=11, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT_DIR, "privilege-drop-and-session.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_pipeline_end_to_end()
    fig_pam_stack_decision()
    fig_privilege_drop_sequence()
    print("Figures generated successfully.")
