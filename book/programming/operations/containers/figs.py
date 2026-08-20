# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Порівняння архітектури віртуальних машин та контейнерів ────────────
def fig_container_vs_vm():
    W, H = 960, 440
    p = []
    
    # Загальна підкладка
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    col_w = 430.0
    col_h = 390.0
    y_start = 25.0
    
    # Ліва колонка: Віртуальні машини (Гіпервізор)
    x_vm = 35.0
    p.append(rect(x_vm, y_start, col_w, col_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(x_vm + col_w / 2, y_start + 28, "Апаратна віртуалізація (Hypervisor VM)", size=14, color="#1e293b", bold=True))
    
    # Нижні шари ВМ
    p.append(rect(x_vm + 20, y_start + 330, col_w - 40, 42, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(x_vm + col_w / 2, y_start + 356, "Фізичне залізо (CPU, RAM, NIC, Disk)", size=12, color="#334155", bold=True))
    
    p.append(rect(x_vm + 20, y_start + 275, col_w - 40, 42, fill="#dbeafe", stroke="#3b82f6", sw=1.2, rx=4))
    p.append(text(x_vm + col_w / 2, y_start + 301, "Хостова ОС та Гіпервізор (KVM / QEMU / ESXi)", size=12, color="#1d4ed8", bold=True))
    
    # Дві віртуальні машини зверху
    vm_box_w = 185.0
    for idx, (vm_x, app_name, mem_note) in enumerate([
        (x_vm + 20, "Застосунок A", "512 МБ пам'яті ядра"),
        (x_vm + 225, "Застосунок B", "512 МБ пам'яті ядра")
    ]):
        # Рамка ВМ
        p.append(rect(vm_x, y_start + 50, vm_box_w, 210, fill="#ffffff", stroke="#93c5fd", sw=1.4, rx=6))
        p.append(text(vm_x + vm_box_w / 2, y_start + 72, "Guest OS (ВМ %d)" % (idx + 1), size=12, color="#1e40af", bold=True))
        
        # App
        p.append(rect(vm_x + 12, y_start + 85, vm_box_w - 24, 38, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=4))
        p.append(text(vm_x + vm_box_w / 2, y_start + 109, app_name, size=12, color="#15803d", bold=True))
        
        # Libs / Userland
        p.append(rect(vm_x + 12, y_start + 130, vm_box_w - 24, 38, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=4))
        p.append(text(vm_x + vm_box_w / 2, y_start + 154, "Бібліотеки / Бінарники", size=11, color="#475569"))
        
        # Guest Kernel
        p.append(rect(vm_x + 12, y_start + 175, vm_box_w - 24, 45, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=4))
        p.append(mtext(vm_x + vm_box_w / 2, y_start + 194, ["Гостьове ядро Linux", mem_note], size=10, color="#991b1b", lh=1.2))

    # Права колонка: Контейнери (Ізоляція рівня ОС)
    x_ct = 495.0
    p.append(rect(x_ct, y_start, col_w, col_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(x_ct + col_w / 2, y_start + 28, "Контейнеризація (OS-Level Isolation)", size=14, color="#1e293b", bold=True))
    
    # Нижні шари контейнерів
    p.append(rect(x_ct + 20, y_start + 330, col_w - 40, 42, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(x_ct + col_w / 2, y_start + 356, "Фізичне залізо (CPU, RAM, NIC, Disk)", size=12, color="#334155", bold=True))
    
    # Єдине спільне ядро
    p.append(rect(x_ct + 20, y_start + 245, col_w - 40, 72, fill="#e0e7ff", stroke="#6366f1", sw=1.5, rx=4))
    p.append(text(x_ct + col_w / 2, y_start + 270, "Єдине спільне ядро хоста (Linux Kernel)", size=13, color="#3730a3", bold=True))
    p.append(text(x_ct + col_w / 2, y_start + 296, "Namespaces • cgroups v2 • Seccomp • LSM • OverlayFS", size=10.5, color="#4338ca"))
    
    # Контейнери зверху (два контейнери)
    for idx, (ct_x, app_name, rootfs_note) in enumerate([
        (x_ct + 20, "Застосунок A", "Ізольований rootfs A"),
        (x_ct + 225, "Застосунок B", "Ізольований rootfs B")
    ]):
        p.append(rect(ct_x, y_start + 50, vm_box_w, 180, fill="#ffffff", stroke="#818cf8", sw=1.4, rx=6))
        p.append(text(ct_x + vm_box_w / 2, y_start + 72, "Контейнер %d (Процес)" % (idx + 1), size=12, color="#3730a3", bold=True))
        
        # App
        p.append(rect(ct_x + 12, y_start + 85, vm_box_w - 24, 42, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=4))
        p.append(text(ct_x + vm_box_w / 2, y_start + 111, app_name, size=12, color="#15803d", bold=True))
        
        # Libs / Rootfs
        p.append(rect(ct_x + 12, y_start + 135, vm_box_w - 24, 45, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=4))
        p.append(mtext(ct_x + vm_box_w / 2, y_start + 154, ["Бібліотеки / Залежності", rootfs_note], size=10.5, color="#475569", lh=1.2))
        
        # Прямий виклик до ядра (стрілка ліворуч, напис праворуч)
        p.append(arrow(ct_x + vm_box_w / 2 - 35, y_start + 188, ct_x + vm_box_w / 2 - 35, y_start + 242, color="#6366f1", sw=1.5))
        p.append(text(ct_x + vm_box_w / 2 - 22, y_start + 215, "syscall (0 оверхеду)", size=9.5, color="#4338ca", anchor="start"))

    render(os.path.join(OUT, 'container-vs-vm-architecture.svg'), W, H, *p)

# ── Фіг. 2: Три стовпи ізоляції контейнера в ядрі Linux ─────────────────────────
def fig_linux_isolation_primitives():
    W, H = 960, 420
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Центральний блок: Контейнеризований процес
    p.append(rect(340, 30, 280, 65, fill="#ecfdf5", stroke="#10b981", sw=2.0, rx=8))
    p.append(text(480, 56, "Контейнеризований процес", size=14, color="#065f46", bold=True))
    p.append(text(480, 78, "Звичайний процес ядра (task_struct)", size=11, color="#047857"))
    
    # Три стовпи знизу
    col_w = 280.0
    col_h = 280.0
    y_col = 120.0
    
    # 1. Namespaces (Видимість)
    p.append(rect(30, y_col, col_w, col_h, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    p.append(text(30 + col_w / 2, y_col + 26, "1. Простори назв (Namespaces)", size=13, color="#1d4ed8", bold=True))
    p.append(text(30 + col_w / 2, y_col + 46, "Ізоляція глобальних таблиць ядра", size=10.5, color="#2563eb"))
    
    ns_items = [
        "PID — власне дерево процесів (PID 1)",
        "NET — свій IP, порти, veth, iptables",
        "MNT — власна таблиця монтувань VFS",
        "IPC — черги POSIX/SysV, семафори",
        "UTS — власні hostname та domainname",
        "USER — мапінг UID/GID (rootless)",
        "CGROUP — корінь дерева cgroups",
        "TIME — зсув монотонного годинника"
    ]
    for i, item in enumerate(ns_items):
        p.append(rect(45, y_col + 60 + i * 26, col_w - 30, 22, fill="#ffffff", stroke="#bfdbfe", sw=1.0, rx=3))
        p.append(text(52, y_col + 76 + i * 26, item, size=9.5, color="#1e3a8a", anchor="start"))
        
    # 2. Cgroups v2 (Ресурси)
    p.append(rect(340, y_col, col_w, col_h, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=6))
    p.append(text(340 + col_w / 2, y_col + 26, "2. Контрольні групи (cgroups v2)", size=13, color="#b45309", bold=True))
    p.append(text(340 + col_w / 2, y_col + 46, "Облік і жорсткі ліміти ресурсів", size=10.5, color="#d97706"))
    
    cg_items = [
        "cpu.max — квота часу CFS / період (тротлінг)",
        "cpu.weight — пропорційна частка (1–10000)",
        "memory.max — стеля RAM (виклик OOM killer)",
        "memory.high — поріг тротлінгу алокацій",
        "io.max — ліміти IOPS та байтів/с для дисків",
        "pids.max — захист від fork-бомб у контейнері",
        "cpu.pressure / memory.pressure — метрики PSI",
        "cgroup.freeze / cgroup.kill — групові операції"
    ]
    for i, item in enumerate(cg_items):
        p.append(rect(355, y_col + 60 + i * 26, col_w - 30, 22, fill="#ffffff", stroke="#fde68a", sw=1.0, rx=3))
        p.append(text(362, y_col + 76 + i * 26, item, size=9.5, color="#78350f", anchor="start"))
        
    # 3. Безпека та пісочниця
    p.append(rect(650, y_col, col_w, col_h, fill="#fdf2f8", stroke="#ec4899", sw=1.5, rx=6))
    p.append(text(650 + col_w / 2, y_col + 26, "3. Межі безпеки (Sandboxing)", size=13, color="#be185d", bold=True))
    p.append(text(650 + col_w / 2, y_col + 46, "Зниження привілеїв і фільтрація", size=10.5, color="#db2777"))
    
    sec_items = [
        "Capabilities — дроп CAP_SYS_ADMIN, RAW_IO",
        "Seccomp-BPF — блокування небезпечних syscalls",
        "no_new_privs — заборона SUID-ескалації",
        "AppArmor / SELinux — обов'язковий контроль (MAC)",
        "Masked Paths — приховування /proc/kcore, /sys/firmware",
        "Read-Only Paths — захист /proc/sys, /proc/sysrq-trigger",
        "pivot_root — відсікання хостового VFS-кореня",
        "User Namespaces — root у контейнері = ніхто на хості"
    ]
    for i, item in enumerate(sec_items):
        p.append(rect(665, y_col + 60 + i * 26, col_w - 30, 22, fill="#ffffff", stroke="#fbcfe8", sw=1.0, rx=3))
        p.append(text(672, y_col + 76 + i * 26, item, size=9.5, color="#831843", anchor="start"))

    # Стрілки від процесу до стовпів
    p.append(arrow(400, 95, 170, 118, color="#3b82f6", sw=1.5))
    p.append(arrow(480, 95, 480, 118, color="#f59e0b", sw=1.5))
    p.append(arrow(560, 95, 790, 118, color="#ec4899", sw=1.5))

    render(os.path.join(OUT, 'linux-isolation-primitives.svg'), W, H, *p)

# ── Фіг. 3: Механізм нашарування файлової системи OverlayFS ────────────────────
def fig_overlayfs_layering():
    W, H = 960, 450
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Ліва частина: Шари на диску
    x_l = 40.0
    w_l = 420.0
    
    p.append(text(x_l + w_l / 2, 36, "Шари образу та контейнера на диску", size=14, color="#1e293b", bold=True))
    
    # 1. Read-Write Upperdir
    p.append(rect(x_l, 60, w_l, 70, fill="#fef2f2", stroke="#ef4444", sw=1.6, rx=6))
    p.append(text(x_l + 16, 84, "Upper Layer (Read-Write Container Layer)", size=12, color="#991b1b", bold=True, anchor="start"))
    p.append(text(x_l + 16, 104, "/var/lib/docker/overlay2/<id>/diff", size=10, color="#b91c1c", anchor="start"))
    p.append(text(x_l + 16, 120, "Змінені файли: /etc/nginx.conf (новий), /app/tmp.log, .wh.old.txt (whiteout)", size=9.5, color="#7f1d1d", anchor="start"))
    
    # 2. Read-Only Lower Layer 3 (App code)
    p.append(rect(x_l, 145, w_l, 60, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=6))
    p.append(text(x_l + 16, 168, "Lower Layer 3: Application Code (Read-Only)", size=11.5, color="#166534", bold=True, anchor="start"))
    p.append(text(x_l + 16, 188, "Файли проєкту: /app/server.js, /app/package.json", size=10, color="#14532d", anchor="start"))
    
    # 3. Read-Only Lower Layer 2 (Runtime)
    p.append(rect(x_l, 220, w_l, 60, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=6))
    p.append(text(x_l + 16, 243, "Lower Layer 2: Runtime Environment (Read-Only)", size=11.5, color="#166534", bold=True, anchor="start"))
    p.append(text(x_l + 16, 263, "Виконуване середовище: /usr/bin/node, системні модулі", size=10, color="#14532d", anchor="start"))
    
    # 4. Read-Only Lower Layer 1 (Base OS)
    p.append(rect(x_l, 295, w_l, 60, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=6))
    p.append(text(x_l + 16, 318, "Lower Layer 1: Base OS Rootfs (Read-Only)", size=11.5, color="#166534", bold=True, anchor="start"))
    p.append(text(x_l + 16, 338, "Базовий образ: /bin/sh, /lib/ld-musl-x86_64.so, /etc/passwd", size=10, color="#14532d", anchor="start"))
    
    # Workdir
    p.append(rect(x_l, 370, w_l, 45, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(x_l + 16, 396, "Workdir: службовий каталог ядра для атомарних CoW та видалень", size=10, color="#64748b", anchor="start"))

    # Центральні стрілки об'єднання (Union Mount)
    p.append(arrow(465, 95, 535, 185, color="#ef4444", sw=1.8))
    p.append(arrow(465, 175, 535, 205, color="#22c55e", sw=1.5))
    p.append(arrow(465, 250, 535, 225, color="#22c55e", sw=1.5))
    p.append(arrow(465, 325, 535, 245, color="#22c55e", sw=1.5))
    p.append(rect(460, 60, 75, 24, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=3))
    p.append(text(497.5, 76, "mount", size=10, color="#334155", bold=True))

    # Права частина: Об'єднаний вид (Merged View у контейнері)
    x_r = 540.0
    w_r = 380.0
    p.append(text(x_r + w_r / 2, 36, "Об'єднане дерево файлів (Merged View)", size=14, color="#1e293b", bold=True))
    
    p.append(rect(x_r, 60, w_r, 355, fill="#f8fafc", stroke="#6366f1", sw=2.0, rx=8))
    p.append(text(x_r + w_r / 2, 88, "Коренева файлова система контейнера (/)", size=13, color="#3730a3", bold=True))
    p.append(text(x_r + w_r / 2, 108, "Те, що бачить процес усередині MNT namespace", size=10.5, color="#4f46e5"))
    
    files_view = [
        ("/etc/nginx.conf", "З Upper Layer (перекриває базовий)", "#fee2e2", "#991b1b"),
        ("/app/tmp.log", "З Upper Layer (новостворений файл)", "#fee2e2", "#991b1b"),
        ("/app/server.js", "З Lower Layer 3 (пряме читання без копії)", "#dcfce7", "#166534"),
        ("/app/package.json", "З Lower Layer 3 (пряме читання)", "#dcfce7", "#166534"),
        ("/usr/bin/node", "З Lower Layer 2 (спільний виконуваний файл)", "#dcfce7", "#166534"),
        ("/bin/sh", "З Lower Layer 1 (базова оболонка)", "#dcfce7", "#166534"),
        ("/lib/ld-musl.so", "З Lower Layer 1 (динамічний лінкер)", "#dcfce7", "#166534"),
        ("/etc/old.txt", "[Видалено] Приховано через whiteout", "#f1f5f9", "#94a3b8")
    ]
    
    for i, (fn, origin, bg_c, tx_c) in enumerate(files_view):
        p.append(rect(x_r + 20, 125 + i * 34, w_r - 40, 28, fill=bg_c, stroke="#cbd5e1", sw=1.0, rx=4))
        p.append(text(x_r + 30, 143 + i * 34, fn, size=10.5, color=tx_c, bold=True, anchor="start"))
        p.append(text(x_r + w_r - 30, 143 + i * 34, origin, size=9.5, color=tx_c, anchor="end"))

    render(os.path.join(OUT, 'overlayfs-layering.svg'), W, H, *p)

# ── Фіг. 4: Життєвий цикл та архітектура стандартів OCI ────────────────────────
def fig_oci_lifecycle():
    W, H = 960, 420
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # 4 етапи конвеєра зліва направо
    steps = [
        ("1. OCI Image Spec", "Реєстр образів\nManifest + Config JSON\nTar-архіви шарів (blobs)", "#f0fdf4", "#16a34a"),
        ("2. High-Level Runtime", "containerd / CRI-O\nЗавантаження tar-шарів\nМонтування rootfs\nГенерація config.json", "#eff6ff", "#2563eb"),
        ("3. Low-Level Runtime", "runc / crun (OCI Runtime)\nСтворення cgroups v2\nВиклик clone() з CLONE_NEW*\npivot_root() + seccomp", "#fffbeb", "#d97706"),
        ("4. Виконання процесу", "Контейнерний процес\nPID 1 у власному NS\nЗнижені Capabilities\nВиклик execve(binary)", "#faf5ff", "#9333ea")
    ]
    
    box_w = 195.0
    box_h = 175.0
    gap = 35.0
    start_x = 32.0
    y_pos = 50.0
    
    for i, (title_text, desc_text, bg_col, stroke_col) in enumerate(steps):
        x = start_x + i * (box_w + gap)
        
        # Рамка етапу
        p.append(rect(x, y_pos, box_w, box_h, fill=bg_col, stroke=stroke_col, sw=1.8, rx=6))
        p.append(text(x + box_w / 2, y_pos + 26, title_text, size=12.5, color=stroke_col, bold=True))
        
        lines = desc_text.split("\n")
        p.append(mtext(x + box_w / 2, y_pos + 56, lines, size=10.5, color=INK, lh=1.35))
        
        # Стрілка переходу
        if i < len(steps) - 1:
            next_x = start_x + (i + 1) * (box_w + gap)
            p.append(arrow(x + box_w + 3, y_pos + box_h / 2, next_x - 3, y_pos + box_h / 2, color=LINE, sw=1.6))
            
    # Нижня панель: Контракти взаємодії
    panel_y = 255.0
    panel_h = 145.0
    p.append(rect(30, panel_y, W - 60, panel_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(W / 2, panel_y + 24, "Стандартизовані контракти Відкритої ініціативи контейнерів (Open Container Initiative)", size=13, color="#1e293b", bold=True))
    
    # Три описи специфікацій
    spec_w = 270.0
    for idx, (spec_title, spec_desc_lines, bg_c, border_c) in enumerate([
        ("OCI Image Format Specification", ["Визначає формат тарболів шарів,", "схему маніфесту (schema2/oci),", "геші SHA256 та дескриптори."], "#ffffff", "#86efac"),
        ("OCI Runtime Specification", ["Визначає структуру OCI Bundle:", "кореневий каталог rootfs та", "декларативний файл config.json."], "#ffffff", "#93c5fd"),
        ("OCI Distribution Specification", ["HTTP API для пушу, пулу,", "перевірки автентичності та", "вивантаження blob-об'єктів."], "#ffffff", "#fde047")
    ]):
        x_spec = 48.0 + idx * (spec_w + 25.0)
        p.append(rect(x_spec, panel_y + 40, spec_w, 90, fill=bg_c, stroke=border_c, sw=1.2, rx=4))
        p.append(text(x_spec + spec_w / 2, panel_y + 58, spec_title, size=11, color="#0f172a", bold=True))
        p.append(mtext(x_spec + spec_w / 2, panel_y + 78, spec_desc_lines, size=9.5, color="#475569", lh=1.3))

    render(os.path.join(OUT, 'oci-lifecycle-and-architecture.svg'), W, H, *p)

if __name__ == "__main__":
    fig_container_vs_vm()
    fig_linux_isolation_primitives()
    fig_overlayfs_layering()
    fig_oci_lifecycle()
    print("Всі фігури згенеровано успішно.")
