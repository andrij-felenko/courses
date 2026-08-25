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
PURPLE_FILL = "#f3e8ff"

BLUE_STROKE = "#2b579a"
GREEN_STROKE = "#1e7e34"
RED_STROKE = "#bd2130"
WARM_STROKE = "#b8860b"
PURPLE_STROKE = "#6f42c1"


# ── 1. VFS -> Procfs Kernel Call Path ───────────────────────────────────────
def fig_vfs_architecture():
    W, H = 1100, 480
    p = []

    # Шар користувача (Userspace)
    p.append(rect(40, 30, 1020, 90, fill="#f8f9fa", stroke="#d6d8db", rx=8))
    p.append(text(120, 52, "Простір користувача (Userspace)", size=14, bold=True, color="#495057"))
    p.append(fitbox(70, 65, 340, 42, ["Утиліта (ps, top, gdb)", "read(\"/proc/1234/status\", buf, len)"], size=13, fill=BLUE_FILL, stroke=BLUE_STROKE))
    p.append(arrow(415, 86, 685, 86))
    p.append(fitbox(690, 65, 340, 42, ["Буфер користувача", "ASCII текст (State, VmSize, Uid...)"], size=13, fill=GREEN_FILL, stroke=GREEN_STROKE))

    # Межа системного виклику
    p.append(text(550, 142, "Системний виклик read() / sys_read()", size=13, bold=True, color=MUTED))
    p.append(arrow(240, 108, 240, 165))
    p.append(arrow(860, 165, 860, 108))

    # Шар ядра (Kernel Space)
    p.append(rect(40, 165, 1020, 285, fill="#f4f6f9", stroke="#ced4da", rx=8))
    p.append(text(120, 188, "Ядро Linux (Kernel Space)", size=14, bold=True, color="#212529"))

    # VFS і Procfs
    p.append(fitbox(70, 205, 290, 52, ["VFS (vfs_read)", "Пошук dentry / inode в procfs"], size=13, fill=WARM_FILL, stroke=WARM_STROKE))
    p.append(arrow(365, 231, 415, 231))

    p.append(fitbox(420, 205, 300, 52, ["Обробник procfs (seq_file)", "proc_pid_status() / single_open()"], size=13, fill=PURPLE_FILL, stroke=PURPLE_STROKE))
    p.append(arrow(570, 260, 570, 310))

    # Внутрішні структури ядра
    p.append(rect(60, 315, 980, 120, fill="#ffffff", stroke="#adb5bd", rx=6))
    p.append(text(150, 335, "Структури даних процесу в пам'яті ядра", size=13, bold=True, color="#343a40"))

    p.append(fitbox(80, 350, 270, 70, ["struct task_struct", "pid, tgid, state, comm", "real_cred, saved_cred"], size=12.5, fill=RED_FILL, stroke=RED_STROKE))
    p.append(fitbox(410, 350, 280, 70, ["struct mm_struct", "total_vm, locked_vm", "vma list (mmap)"], size=12.5, fill=BLUE_FILL, stroke=BLUE_STROKE))
    p.append(fitbox(740, 350, 280, 70, ["struct files_struct", "fd_array[], fdt", "struct file *, struct inode *"], size=12.5, fill=GREEN_FILL, stroke=GREEN_STROKE))

    p.append(arrow(570, 310, 215, 345))
    p.append(arrow(570, 310, 550, 345))
    p.append(arrow(570, 310, 880, 345))

    render(os.path.join(IMG, 'procfs-vfs-architecture.svg'), W, H, *p)


# ── 2. Structural Hierarchy of /proc/[pid]/ ────────────────────────────────
def fig_process_tree():
    W, H = 1150, 540
    p = []

    # Кореневий вузол
    p.append(fitbox(460, 20, 230, 48, ["/proc/[pid]/", "Директорія процесу"], size=14, fill=BLUE_FILL, stroke=BLUE_STROKE, sw=2))

    # Лінії розгалуження
    p.append(arrow(575, 70, 140, 120))
    p.append(arrow(575, 70, 390, 120))
    p.append(arrow(575, 70, 640, 120))
    p.append(arrow(575, 70, 880, 120))
    p.append(arrow(575, 70, 1030, 120))

    # Категорія 1: Метадані та стан
    p.append(fitbox(40, 125, 200, 45, ["Метадані та стан", "Текстові файли"], size=13, fill=GREEN_FILL, stroke=GREEN_STROKE, sw=1.8))
    p.append(arrow(140, 172, 140, 205))
    p.append(fitbox(30, 210, 220, 140, [
        "status  (зведення для людини)",
        "stat    (поля для парсингу)",
        "cmdline (аргументи argv)",
        "environ (змінні оточення)",
        "wchan   (назва блокування)"
    ], size=12, fill="#ffffff", stroke=GREEN_STROKE))

    # Категорія 2: Віртуальна пам'ять
    p.append(fitbox(290, 125, 200, 45, ["Віртуальна пам'ять", "Адресний простір"], size=13, fill=PURPLE_FILL, stroke=PURPLE_STROKE, sw=1.8))
    p.append(arrow(390, 172, 390, 205))
    p.append(fitbox(280, 210, 220, 140, [
        "maps     (регіони VMA)",
        "smaps    (детальний PSS/RSS)",
        "statm    (сторінки пам'яті)",
        "pagemap  (мапінг у PFN)",
        "mem      (прямий доступ RAM)"
    ], size=12, fill="#ffffff", stroke=PURPLE_STROKE))

    # Категорія 3: Дескриптори та шляхи
    p.append(fitbox(540, 125, 200, 45, ["Дескриптори та шляхи", "Магічні посилання"], size=13, fill=WARM_FILL, stroke=WARM_STROKE, sw=1.8))
    p.append(arrow(640, 172, 640, 205))
    p.append(fitbox(530, 210, 220, 140, [
        "fd/     (0, 1, 2... -> inode)",
        "fdinfo/ (позиція, прапорці)",
        "cwd     (поточна директорія)",
        "exe     (шлях до бінарника)",
        "root    (корінь chroot)"
    ], size=12, fill="#ffffff", stroke=WARM_STROKE))

    # Категорія 4: Потоки виконання
    p.append(fitbox(780, 125, 200, 45, ["Потоки (Threads)", "Ієрархія task/"], size=13, fill=RED_FILL, stroke=RED_STROKE, sw=1.8))
    p.append(arrow(880, 172, 880, 205))
    p.append(fitbox(770, 210, 220, 140, [
        "task/[tid]/status",
        "task/[tid]/stat",
        "task/[tid]/comm",
        "task/[tid]/children",
        "(власні файли потоку)"
    ], size=12, fill="#ffffff", stroke=RED_STROKE))

    # Категорія 5: Ізоляція та cgroups
    p.append(fitbox(980, 125, 140, 45, ["Ізоляція", "ns/ та cgroup"], size=13, fill=BLUE_FILL, stroke=BLUE_STROKE, sw=1.8))
    p.append(arrow(1050, 172, 1050, 205))
    p.append(fitbox(970, 210, 160, 140, [
        "ns/net  (net_ns)",
        "ns/mnt  (mount_ns)",
        "ns/pid  (pid_ns)",
        "cgroup  (групи)",
        "oom_score"
    ], size=12, fill="#ffffff", stroke=BLUE_STROKE))

    # Пояснювальний шар внизу через fitbox
    p.append(fitbox(30, 380, 1090, 130, [
        "Особливості доступу та генерації вмісту ядра:",
        "• st_size = 0 для більшості файлів: вміст генерується 'on-the-fly' під час системного виклику read().",
        "• fd/ та ns/ є 'магічними' посиланнями: вони посилаються безпосередньо на inode ядра, а не на шляхи у VFS.",
        "• Налаштування hidepid регулює видимість чужих директорій /proc/[pid] для користувачів без привілеїв."
    ], size=12, fill="#f8f9fa", stroke="#dee2e6", rx=6))

    render(os.path.join(IMG, 'procfs-process-tree.svg'), W, H, *p)


if __name__ == '__main__':
    fig_vfs_architecture()
    fig_process_tree()
    print("SVG figures generated successfully.")
