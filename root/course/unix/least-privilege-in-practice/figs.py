# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL  = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL   = "#fdecea"
WARM_FILL  = "#fff6e5"
GREY_FILL  = "#f4f6f8"


# ── 1. Ешелонована оборона найменших привілеїв ──────────────────────────────
def fig_defense_layers():
    W, H = 1240, 700
    p = []

    p.append(text(W / 2, 40, "Ешелонована оборона (Defense in Depth) привілеїв у Linux", size=18, bold=True))

    layers = [
        ("Рівень 1: Дискреційний контроль (DAC) та скидання ідентичності",
         "UID / GID / Groups (setresuid, setresgid, setgroups)\n"
         "Процес відмовляється від всемогутнього UID 0. Створюється виділений системний користувач (наприклад, _nginx, nobody).\n"
         "Помилка в коді не дає автоматичного доступу до чужих файлів у VFS за межами прав непривілейованого користувача.",
         BLUE_FILL, FIELD),
        ("Рівень 2: Декомпозиція прав суперкористувача (Linux Capabilities)",
         "POSIX 1003.1e / Linux Capabilities (CAP_NET_BIND_SERVICE, CAP_SYS_TIME, CAP_CHOWN...)\n"
         "Замість монолітного root процес утримує лише атомарні бітові дозволи. Скидання Bounding Set та Ambient-маски\n"
         "гарантує, що процес не зможе завантажувати модулі ядра (CAP_SYS_MODULE) чи обходити DAC (CAP_DAC_OVERRIDE).",
         GREEN_FILL, NEG),
        ("Рівень 3: Звуження інтерфейсу ядра (Seccomp-BPF)",
         "Фільтрація системних викликів (PR_SET_NO_NEW_PRIVS + seccomp-bpf)\n"
         "Блокування доступу до небезпечних системних викликів (ptrace, bpf, io_uring_setup, unshare, mount).\n"
         "Навіть якщо зловмисник захопив потік виконання (ROP/shellcode), він не може експлуатувати 0-day вразливості ядра.",
         WARM_FILL, POS),
        ("Рівень 4: Мандатний контроль доступу (MAC: AppArmor / SELinux)",
         "Політики безпеки на рівні ОС (Type Enforcement, Path confinement)\n"
         "Примусове обмеження операцій над ресурсами навіть для привілейованих процесів. Якщо демон скомпрометовано,\n"
         "політика забороняє читання /etc/shadow, зміну бінарників та запуск командних оболонок (/bin/sh).",
         RED_FILL, POS),
        ("Рівень 5: Просторова ізоляція та Landlock (Namespaces & Sandboxing)",
         "Простори імен (Mount, PID, Net) та обмеження VFS у просторі користувача (Landlock LSM)\n"
         "Повна невидимість чужих процесів, ізольований мережевий стек, приватне дерево /tmp та доступ лише до дозволених папок.",
         GREY_FILL, LINE),
    ]

    y = 75
    card_h = 108
    for i, (title_text, desc_text, fill_col, border_col) in enumerate(layers):
        p.append(rect(60, y, W - 120, card_h, fill=fill_col, stroke=border_col, sw=1.8, rx=8))
        p.append(text(85, y + 28, title_text, size=15, bold=True, anchor="start", color=INK))
        p.append(fitbox(85, y + 38, W - 170, 62, desc_text, size=12, fill=fill_col, stroke="none", color=INK))
        y += card_h + 14

    render(os.path.join(IMG, 'privilege-defense-layers.svg'), W, H, *p)


# ── 2. Послідовність безпечного скидання прав ───────────────────────────────
def fig_drop_lifecycle():
    W, H = 1260, 720
    p = []

    p.append(text(W / 2, 38, "Послідовність безпечного скидання прав мережевого демона", size=18, bold=True))

    steps = [
        ("1. Старт із UID 0",
         "Процес запускається під root:\nчитає конф /etc, відкриває сокет на порту 80/443,\nстворює дескриптори логів.",
         WARM_FILL),
        ("2. Налаштування Caps",
         "prctl(PR_SET_KEEPCAPS, 1)\nВмикає прапорець збереження\nPermitted capabilities при скиданні UID.",
         BLUE_FILL),
        ("3. Очищення груп",
         "setgroups(0, NULL)\ninitgroups(user, gid)\nСкидає додаткові групи root;\nОБОВ'ЯЗКОВО до скидання UID!",
         RED_FILL),
        ("4. Скидання GID та UID",
         "setresgid(gid, gid, gid)\nsetresuid(uid, uid, uid)\nАтомарно встановлює Real, Effective\nта Saved ID у непривілейовані.",
         RED_FILL),
        ("5. Фіксація Caps",
         "cap_set_proc(desired_caps)\nСкидає непотрібні права (CAP_SYS_ADMIN);\nзалишає лише CAP_NET_BIND_SERVICE.",
         GREEN_FILL),
        ("6. Seccomp-BPF",
         "prctl(PR_SET_NO_NEW_PRIVS, 1)\nseccomp(SECCOMP_SET_MODE_FILTER)\nЗабороняє повернення прав і обмежує syscalls.",
         GREY_FILL),
    ]

    col_w = 180
    gap = 20
    total_w = len(steps) * col_w + (len(steps) - 1) * gap
    start_x = (W - total_w) / 2

    y_top = 75
    box_h = 230

    for i, (stitle, sdesc, fill_c) in enumerate(steps):
        x = start_x + i * (col_w + gap)
        p.append(rect(x, y_top, col_w, box_h, fill=fill_c, stroke=LINE, sw=1.5, rx=8))
        p.append(text(x + col_w / 2, y_top + 28, stitle, size=13, bold=True, color=INK))
        p.append(fitbox(x + 10, y_top + 42, col_w - 20, box_h - 52, sdesc, size=11.5, fill=fill_c, stroke="none", color=INK))

        if i < len(steps) - 1:
            arr_x1 = x + col_w + 3
            arr_x2 = x + col_w + gap - 3
            arr_y = y_top + box_h / 2
            p.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color=POS, sw=2.0))

    # Нижня пояснювальна зона
    p.append(rect(50, 330, W - 100, 360, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(W / 2, 360, "Критичні пастки та інваріанти скидання привілеїв", size=15, bold=True, color=POS))

    traps = [
        ("Порушення порядку викликів",
         "Якщо викликати setresuid() до setgroups(), процес втрачає привілей CAP_SETGID і не може скинути групи суперкористувача. Зловмисник отримує доступ до файлів з GID 0 (root/wheel)."),
        ("Використання застарілого setuid()",
         "Класичний setuid() у разі помилки або в setuid-бінарниках може змінити лише Effective UID, залишаючи Saved UID = 0. Це дозволяє повернути root через повторний виклик seteuid(0)."),
        ("Очищення Capabilities ядром",
         "При переході UID 0 -> non-zero ядро Linux за замовчуванням обнуляє всі маски Capabilities. Без prctl(PR_SET_KEEPCAPS, 1) процес втрачає право прив'язки до привілейованих портів."),
        ("Відсутність PR_SET_NO_NEW_PRIVS",
         "Без встановлення цього прапорця непривілейований процес не може завантажити Seccomp-BPF фільтр, або залишається вразливим до виконання setuid-програм із підвищенням прав."),
    ]

    ty = 385
    for title_t, desc_t in traps:
        p.append(rect(70, ty, W - 140, 64, fill=WARM_FILL, stroke=LINE, sw=1.0, rx=6))
        p.append(text(90, ty + 22, "• " + title_t + ":", size=12.5, bold=True, anchor="start", color=POS))
        p.append(fitbox(90, ty + 28, W - 180, 32, desc_t, size=11, fill=WARM_FILL, stroke="none", color=INK))
        ty += 74

    render(os.path.join(IMG, 'privilege-drop-lifecycle.svg'), W, H, *p)


# ── 3. Архітектура розподілу привілеїв (Privilege Separation) ────────────────
def fig_privilege_separation():
    W, H = 1260, 640
    p = []

    p.append(text(W / 2, 38, "Архітектурний патерн розподілу привілеїв (Privilege Separation)", size=18, bold=True))

    # Лівий блок: Привілейований Майстер (Master / Monitor)
    lx, ly, lw, lh = 50, 75, 480, 525
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10))
    p.append(rect(lx, ly, lw, 48, fill=WARM_FILL, stroke=MUTED, sw=1.5, rx=10))
    p.append(text(lx + lw / 2, ly + 30, "Привілейований процес (Master / Monitor)", size=15, bold=True, color=POS))

    master_items = [
        "Запускається від root (UID 0) або з вузьким набором Capabilities",
        "НЕ читає дані з неперевіреної мережі напряму",
        "Виконує критичні привілейовані операції за запитом воркера:\n  • Відкриття файлів сертифікатів SSL/TLS (/etc/ssl/private)\n  • Прив'язка до нових мережевих портів (bind < 1024)\n  • Перезавантаження конфігурації (SIGHUP)\n  • Аутентифікація користувачів (PAM, /etc/shadow)",
        "Мінімальна поверхня коду: проста логіка валідації команд",
        "Контролює життєвий цикл воркерів (fork, waitpid, restart при збої)",
    ]

    my = ly + 65
    for it in master_items:
        h_it = 76 if "\n" in it else 54
        p.append(fitbox(lx + 15, my, lw - 30, h_it, it, size=11.5, fill=GREY_FILL, stroke=LINE, sw=1.0))
        my += h_it + 10

    # Правий блок: Непривілейований Воркер (Worker / Sandbox)
    rx, ry, rw, rh = 730, 75, 480, 525
    p.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10))
    p.append(rect(rx, ry, rw, 48, fill=GREEN_FILL, stroke=MUTED, sw=1.5, rx=10))
    p.append(text(rx + rw / 2, ry + 30, "Непривілейований процес (Worker / Engine)", size=15, bold=True, color=FIELD))

    worker_items = [
        "Працює від непривілейованого користувача (UID 65534 / nobody)",
        "Обробляє небезпечний вхідний мережевий потік (HTTP, DNS, SSH)",
        "Повна пісочниця (Multi-layer Sandbox):\n  • Caps: 0 (усі capabilities скинуто)\n  • Seccomp-BPF: дозволено лише read, write, epoll_wait, futex\n  • Namespaces / chroot: пустий каталог /var/empty\n  • PR_SET_NO_NEW_PRIVS: блокування підвищення прав",
        "При збої / ROP-атаці зловмисник не має системних прав",
        "Спілкується з Master виключно через локальний socketpair",
    ]

    wy = ry + 65
    for it in worker_items:
        h_it = 82 if "\n" in it else 54
        p.append(fitbox(rx + 15, wy, rw - 30, h_it, it, size=11.5, fill=GREY_FILL, stroke=LINE, sw=1.0))
        wy += h_it + 10

    # Міжпроцесний зв'язок посередині
    mid_x = (lx + lw + rx) / 2
    p.append(arrow(lx + lw + 10, 220, rx - 10, 220, color=NEG, sw=2.2))
    p.append(arrow(rx - 10, 420, lx + lw + 10, 420, color=POS, sw=2.2))

    tb1, _, _ = textbox(mid_x, 180, "Unix Domain Socket\n(socketpair / SCM_RIGHTS)\nПередача дескрипторів FD", size=11, bold=True, fill="#ffffff", stroke=LINE)
    tb2, _, _ = textbox(mid_x, 460, "Запити на відкриття ресурсів\nта валідовані команди", size=11, bold=True, fill="#ffffff", stroke=LINE)
    p.append(tb1)
    p.append(tb2)

    render(os.path.join(IMG, 'privilege-separation-arch.svg'), W, H, *p)


if __name__ == '__main__':
    fig_defense_layers()
    fig_drop_lifecycle()
    fig_privilege_separation()
    print("All figures generated successfully.")
