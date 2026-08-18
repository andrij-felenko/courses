# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#f4f6f8"


# ── 1. Ілюзія контейнера проти реальності ядра ──────────────────────────────
def fig_container_architecture():
    W, H = 1240, 680
    p = []

    # Ліва половина: користувацьке уявлення
    lx, ly, lw, lh = 40, 50, 530, 590
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(lx + lw / 2, ly + 36, "Уявлення користувача («віртуальна машина»)", size=17, bold=True, color=INK))

    p.append(fitbox(lx + 30, ly + 65, 470, 70,
                    "Ілюзія окремої ОС:\nвласна файлова система, ізольована мережа, свій PID 1",
                    size=13, fill=WARM_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(lx + 45, ly + 160, 440, 75,
                    "Процес застосунку (PID 1 усередині)\nВиконує код, слухає локальний порт 8080",
                    size=14, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    p.append(fitbox(lx + 45, ly + 255, 440, 65,
                    "Приватний кореневий каталог (/)\n/bin, /lib, /etc/nginx/nginx.conf",
                    size=13, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(lx + 45, ly + 338, 440, 65,
                    "Віртуальний мережевий інтерфейс\neth0: 10.0.2.15/24, власна таблиця маршрутів",
                    size=13, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(lx + 45, ly + 420, 440, 70,
                    "Приватні псевдофайлові системи\n/proc (видно лише PID 1), /sys, /dev/null",
                    size=13, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(lx + 45, ly + 510, 440, 65,
                    "Обмеження пам'яті та CPU (уявний гіпервізор)\n«Виділено 512 MB RAM і 1 ядро vCPU»",
                    size=13, fill=WARM_FILL, stroke=MUTED, sw=1.2))

    # Права половина: реальність ядра Linux
    rx, ry, rw, rh = 630, 50, 570, 590
    p.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(rx + rw / 2, ly + 36, "Реальність у ядрі Linux (спільне монолітне ядро)", size=17, bold=True, color=INK))

    p.append(fitbox(rx + 30, ry + 65, 510, 70,
                    "Жодного гіпервізора та окремого ядра немає:\nзвичайний процес task_struct із набором обмежувальних вказівників",
                    size=13, fill=GREY_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(rx + 45, ry + 155, 500, 75,
                    "task_struct (справжній PID 4192 на хості)\nВиконує нативні інструкції на спільному процесорі",
                    size=14, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    p.append(fitbox(rx + 45, ry + 248, 500, 72,
                    "struct nsproxy *nsproxy\nВказівники на структури mnt_ns, pid_ns, net_ns, uts_ns, ipc_ns",
                    size=13, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(rx + 45, ry + 338, 500, 72,
                    "struct cgroup *cgroups (cgroup v2)\nОблік: memory.max (512M), cpu.max (100000 100000), pids.max (64)",
                    size=13, fill=WARM_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(rx + 45, ry + 428, 500, 68,
                    "struct seccomp_filter (BPF-фільтр викликів)\nПерехоплює заборонені системні виклики (reboot, kexec, init_module)",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.2))

    p.append(fitbox(rx + 45, ry + 512, 500, 68,
                    "Спільні апаратні ресурси ядра\nЄдиний планувальник CFS/EEVDF, драйвери заліза, кеш сторінок VFS",
                    size=13, fill=GREY_FILL, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'container-architecture.svg'), W, H, *p)


# ── 2. Послідовність pivot_root ─────────────────────────────────────────────
def fig_pivot_root_sequence():
    W, H = 1260, 660
    p = []

    p.append(text(W / 2, 40, "Послідовність надійної зміни кореневої файлової системи (pivot_root)", size=18, bold=True))

    steps = [
        ("Крок 1: Розрив розповсюдження монтувань",
         "mount(NULL, \"/\", NULL, MS_REC | MS_PRIVATE, NULL)\n\n"
         "За замовчуванням монтування на системі мають прапорець MS_SHARED. Будь-яка зміна точок усередині простору\n"
         "передавалася б у дерево хоста. Прапорець MS_PRIVATE ізолює піддерево простору від хостової VFS.",
         BLUE_FILL),
        ("Крок 2: Перетворення new_root на точку монтування",
         "mount(new_root, new_root, NULL, MS_BIND | MS_REC, NULL)\n\n"
         "Системний виклик pivot_root вимагає, щоб новий корінь був окремою точкою монтування VFS, а не просто текою.\n"
         "Зворотне монтування прив'язки (bind mount) створює необхідний вузол struct vfsmount у ядрі.",
         WARM_FILL),
        ("Крок 3: Атомарний обмін старого та нового кореня",
         "mkdir(new_root + \"/.old_root\")\n"
         "pivot_root(new_root, new_root + \"/.old_root\")\n\n"
         "Ядро переставляє новий корінь на позицію /, а старе хостове дерево файлів розміщує у вказаній підтеці .old_root.\n"
         "На відміну від chroot, старий корінь не зникає з пам'яті, а стає дочірнім піддеревом нового кореня.",
         GREEN_FILL),
        ("Крок 4: Відмонтування старого кореня та зачистка",
         "chdir(\"/\")\n"
         "umount2(\"/.old_root\", MNT_DETACH)\n"
         "rmdir(\"/.old_root\")\n\n"
         "Процес переходить у новий корінь і відмонтовує .old_root з прапорцем MNT_DETACH (ліниве відмонтування).\n"
         "Після цього процес повністю позбавлений доступу до хостової файлової системи: виходу назад не існує.",
         GREY_FILL),
    ]

    y = 75
    card_h = 125
    gap = 18

    for i, (title, desc, fill) in enumerate(steps):
        p.append(fitbox(40, y, 320, card_h, title, size=15, bold=True, fill=fill, stroke=LINE, sw=1.5))
        p.append(fitbox(380, y, 840, card_h, desc, size=12.5, fill="#ffffff", stroke=MUTED, sw=1.2))
        y += card_h + gap

    render(os.path.join(IMG, 'pivot-root-sequence.svg'), W, H, *p)


# ── 3. Матриця 8 просторів імен ─────────────────────────────────────────────
def fig_namespaces_matrix():
    W, H = 1280, 720
    p = []

    p.append(text(W / 2, 40, "Вісім просторів імен Linux: прапорці clone та ізольовані ресурси", size=18, bold=True))

    headers = [
        ("Простір імен", 40, 180),
        ("Прапорець clone/unshare", 235, 230),
        ("Що саме ізолює в ядрі", 480, 540),
        ("Вузол у /proc/[pid]/ns", 1035, 205),
    ]

    for title, x, w in headers:
        p.append(fitbox(x, 70, w, 40, title, size=14, bold=True, fill=WARM_FILL, stroke=LINE, sw=1.2))

    rows = [
        ("Mount (mnt)", "CLONE_NEWNS", "Дерево точок монтування, таблиця VFS, прапорці прив'язок", "mnt", BLUE_FILL),
        ("PID (pid)", "CLONE_NEWPID", "Ієрархія номерів процесів, віртуальний PID 1, доставка сигналів", "pid", GREEN_FILL),
        ("Network (net)", "CLONE_NEWNET", "Мережеві інтерфейси, IP-адреси, таблиці маршрутизації, правила сокетів", "net", BLUE_FILL),
        ("IPC (ipc)", "CLONE_NEWIPC", "Черги повідомлень POSIX/SysV, спільна пам'ять (shm), семафори", "ipc", GREY_FILL),
        ("UTS (uts)", "CLONE_NEWUTS", "Ім'я комп'ютера (nodename) та доменне ім'я системи (domainname)", "uts", GREY_FILL),
        ("User (user)", "CLONE_NEWUSER", "Відображення UID/GID (uid_map), власні привілеї (capabilities)", "user", WARM_FILL),
        ("Cgroup (cgroup)", "CLONE_NEWCGROUP", "Відображення власного вузла cgroup у /proc/self/cgroup як /", "cgroup", GREY_FILL),
        ("Time (time)", "CLONE_NEWTIME", "Зсуви годинників CLOCK_MONOTONIC та CLOCK_BOOTTIME", "time", RED_FILL),
    ]

    y = 122
    rh = 58
    gap = 12

    for name, flag, what, node, fill in rows:
        p.append(fitbox(40, y, 180, rh, name, size=13.5, bold=True, fill=fill, stroke=LINE, sw=1.2))
        p.append(fitbox(235, y, 230, rh, flag, size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
        p.append(fitbox(480, y, 540, rh, what, size=12.5, fill="#ffffff", stroke=MUTED, sw=1.2))
        p.append(fitbox(1035, y, 205, rh, node, size=13, fill=GREY_FILL, stroke=MUTED, sw=1.2))
        y += rh + gap

    render(os.path.join(IMG, 'namespaces-matrix.svg'), W, H, *p)


# ── 4. Дворівневий бар'єр: cgroups v2 та seccomp-BPF ────────────────────────
def fig_cgroups_seccomp_control():
    W, H = 1260, 680
    p = []

    p.append(text(W / 2, 40, "Дворівневий захист вузла: квотування ресурсів та фільтрація викликів", size=18, bold=True))

    # Ліва колонка: cgroups v2
    lx, ly, lw, lh = 40, 70, 570, 570
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(lx + lw / 2, ly + 36, "1. cgroups v2: Квотування ресурсів (скільки)", size=16, bold=True, color=INK))

    p.append(fitbox(lx + 25, ly + 65, 520, 65,
                    "Підсистема ядра для обліку та обмеження споживання фізичних ресурсів.\nЗапобігає виснаженню пам'яті (OOM) та блокуванню процесора хоста.",
                    size=12.5, fill=WARM_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(lx + 25, ly + 145, 520, 85,
                    "Контролер пам'яті (memory.max, memory.high)\n"
                    "memory.max = 536870912 (512 MB hard limit). Перевищення викликає OOM Killer усередині групи.\n"
                    "memory.high = 419430400 (400 MB soft limit). Примусове витіснення сторінок у фоні.",
                    size=12, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(lx + 25, ly + 245, 520, 85,
                    "Контролер процесора (cpu.max, cpu.weight)\n"
                    "cpu.max = 20000 100000 (квота 20 мс на кожні 100 мс періоду = 20% від 1 ядра).\n"
                    "cpu.weight = 100 (пропорційна вага процесу при конкуренції з іншими групами).",
                    size=12, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(lx + 25, ly + 345, 520, 80,
                    "Контролер процесів (pids.max)\n"
                    "pids.max = 64 (максимальна кількість задач у групі).\n"
                    "Повний захист від атак типу fork-bomb, які вичерпують таблицю процесів ядра.",
                    size=12, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(lx + 25, ly + 440, 520, 80,
                    "Контролер вводу-виводу (io.max, io.weight)\n"
                    "io.max = 8:0 rbps=10485760 wbps=10485760 (ліміт швидкості читання/запису 10 MB/s).\n"
                    "Захист від блокування спільних дисків хоста інтенсивними операціями вводу-виводу.",
                    size=12, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    # Права колонка: seccomp-BPF
    rx, ry, rw, rh = 650, 70, 570, 570
    p.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(rx + rw / 2, ry + 36, "2. seccomp-BPF: Фільтрація викликів (що дозволено)", size=16, bold=True, color=INK))

    p.append(fitbox(rx + 25, ry + 65, 520, 65,
                    "Інтерцептор системних викликів на вході в ядро.\nПеревіряє номер виклику та аргументи через BPF-інструкції до виконання коду ядра.",
                    size=12.5, fill=RED_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(rx + 25, ry + 145, 520, 85,
                    "prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)\n"
                    "Обов'язковий прапорець перед завантаженням BPF-фільтра без root.\n"
                    "Забороняє дочірнім процесам підвищувати привілеї через біти setuid/setgid на файлах.",
                    size=12, fill=WARM_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(rx + 25, ry + 245, 520, 85,
                    "Дозволені системні виклики (SECCOMP_RET_ALLOW)\n"
                    "Безпечні операції: read, write, openat, close, epoll_wait, nanosleep, futex, mmap, brk.\n"
                    "Формують білий список, достатній для звичайної роботи серверних програм.",
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.2))

    p.append(fitbox(rx + 25, ry + 345, 520, 85,
                    "Заборонені системні виклики (SECCOMP_RET_ERRNO(EPERM))\n"
                    "Небезпечні для хоста: reboot, kexec_load, init_module, finit_module, sysfs, swapon.\n"
                    "Ядро повертає помилку Operation not permitted без виконання коду драйвера.",
                    size=12, fill=RED_FILL, stroke=POS, sw=1.2))

    p.append(fitbox(rx + 25, ry + 440, 520, 75,
                    "Критичні порушення (SECCOMP_RET_KILL_PROCESS)\n"
                    "Спроби втручання в інші процеси (ptrace, process_vm_writev) або атаки на ядро.\n"
                    "Ядро негайно завершує контейнер сигналом SIGSYS.",
                    size=12, fill=GREY_FILL, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'cgroups-seccomp-control.svg'), W, H, *p)


if __name__ == '__main__':
    fig_container_architecture()
    fig_pivot_root_sequence()
    fig_namespaces_matrix()
    fig_cgroups_seccomp_control()
    print("Figures generated successfully in img/")
