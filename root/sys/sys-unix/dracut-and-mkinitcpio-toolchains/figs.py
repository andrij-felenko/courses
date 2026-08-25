import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def render():
    out_dir = os.path.dirname(__file__)
    img_dir = os.path.join(out_dir, "img")
    os.makedirs(img_dir, exist_ok=True)

    # 1. Generators Architecture Comparison
    # Show input sources -> Generator Core -> Output Compressed CPIO Archive
    frags1 = []
    
    # Input sources column (left)
    frags1.append(svgkit.rect(30, 60, 160, 220, fill="#f0f4f8", stroke="#4a5568", rx=6))
    frags1.append(svgkit.text(110, 85, "Джерела системи", bold=True, size=14, color="#1a202c"))
    frags1.append(svgkit.line(40, 95, 180, 95, color="#cbd5e1"))
    
    frags1.append(svgkit.rect(45, 110, 130, 32, fill="#ffffff", stroke="#94a3b8", rx=4))
    frags1.append(svgkit.text(110, 131, "Модулі ядра", size=11))
    
    frags1.append(svgkit.rect(45, 150, 130, 32, fill="#ffffff", stroke="#94a3b8", rx=4))
    frags1.append(svgkit.text(110, 171, "Бібліотеки (ELF)", size=11))
    
    frags1.append(svgkit.rect(45, 190, 130, 32, fill="#ffffff", stroke="#94a3b8", rx=4))
    frags1.append(svgkit.text(110, 211, "udev-правила", size=11))
    
    frags1.append(svgkit.rect(45, 230, 130, 32, fill="#ffffff", stroke="#94a3b8", rx=4))
    frags1.append(svgkit.text(110, 251, "Конфігурація", size=11))

    # Arrows to generators
    frags1.append(svgkit.arrow(190, 126, 230, 110, color="#2563eb"))
    frags1.append(svgkit.arrow(190, 170, 230, 170, color="#059669"))
    frags1.append(svgkit.arrow(190, 214, 230, 230, color="#d97706"))

    # Generators column (middle)
    # dracut box
    frags1.append(svgkit.rect(230, 50, 260, 75, fill="#eff6ff", stroke="#2563eb", sw=1.8, rx=6))
    frags1.append(svgkit.text(360, 72, "dracut (systemd-driven)", bold=True, size=13, color="#1e40af"))
    frags1.append(svgkit.text(360, 92, "modules.d/ + systemd units + rd.*", size=10, color="#3b82f6"))

    # mkinitcpio box
    frags1.append(svgkit.rect(230, 135, 260, 75, fill="#ecfdf5", stroke="#059669", sw=1.8, rx=6))
    frags1.append(svgkit.text(360, 157, "mkinitcpio (declarative)", bold=True, size=13, color="#065f46"))
    frags1.append(svgkit.text(360, 177, "install/ + hooks/ + autodetect", size=10, color="#10b981"))

    # initramfs-tools box
    frags1.append(svgkit.rect(230, 220, 260, 75, fill="#fffbeb", stroke="#d97706", sw=1.8, rx=6))
    frags1.append(svgkit.text(360, 242, "initramfs-tools (shell-script)", bold=True, size=13, color="#92400e"))
    frags1.append(svgkit.text(360, 262, "hooks/ + scripts/ (local-top/etc)", size=10, color="#f59e0b"))

    # Arrows to output
    frags1.append(svgkit.arrow(490, 87, 530, 150, color="#2563eb"))
    frags1.append(svgkit.arrow(490, 172, 530, 170, color="#059669"))
    frags1.append(svgkit.arrow(490, 257, 530, 190, color="#d97706"))

    # Output column (right)
    frags1.append(svgkit.rect(530, 80, 180, 180, fill="#f8fafc", stroke="#334155", sw=2, rx=6))
    frags1.append(svgkit.text(620, 110, "Образ initramfs", bold=True, size=14, color="#0f172a"))
    frags1.append(svgkit.line(540, 122, 700, 122, color="#cbd5e1"))
    
    frags1.append(svgkit.rect(545, 135, 150, 30, fill="#e2e8f0", stroke="#64748b", rx=4))
    frags1.append(svgkit.text(620, 155, "Нестиснений мікрокод", size=10))
    
    frags1.append(svgkit.rect(545, 175, 150, 70, fill="#dbeafe", stroke="#3b82f6", rx=4))
    frags1.append(svgkit.text(620, 200, "Основна rootfs", bold=True, size=11, color="#1e3a8a"))
    frags1.append(svgkit.text(620, 220, "cpio archive (zstd/gzip)", size=10, color="#1d4ed8"))
    frags1.append(svgkit.text(620, 235, "З /init або systemd", size=9, color="#475569"))

    svgkit.render(os.path.join(img_dir, "generators-architecture.svg"), 740, 320, *frags1, title="Архітектура та компоненти генераторів initramfs")

    # 2. Hook Execution Phases Sequence
    frags2 = []

    # Timeline header steps
    steps = [
        ("Ядро / cpio", "Розпакування"),
        ("Ранній init", "Параметри cmdline"),
        ("Події / udev", "Виявлення заліза"),
        ("Сховища", "LUKS / LVM / RAID"),
        ("Перехід", "switch_root")
    ]
    
    xs = [40, 180, 320, 460, 600]
    for i, (title_st, sub_st) in enumerate(steps):
        x = xs[i]
        frags2.append(svgkit.rect(x, 45, 110, 42, fill="#f1f5f9", stroke="#475569", rx=4))
        frags2.append(svgkit.text(x + 55, 62, title_st, bold=True, size=11))
        frags2.append(svgkit.text(x + 55, 77, sub_st, size=9, color="#64748b"))
        if i < len(steps) - 1:
            frags2.append(svgkit.arrow(x + 110, 66, xs[i+1], 66, color="#94a3b8"))

    # Toolchain rows
    # dracut row
    frags2.append(svgkit.rect(20, 110, 710, 55, fill="#eff6ff", stroke="#93c5fd", rx=4))
    frags2.append(svgkit.text(45, 130, "dracut", bold=True, size=12, color="#1e40af", anchor="start"))
    frags2.append(svgkit.text(45, 148, "(systemd)", size=9, color="#3b82f6", anchor="start"))

    frags2.append(svgkit.rect(170, 120, 120, 35, fill="#dbeafe", stroke="#2563eb", rx=3))
    frags2.append(svgkit.text(230, 141, "dracut-cmdline", size=10, bold=True, color="#1e40af"))

    frags2.append(svgkit.rect(310, 120, 130, 35, fill="#dbeafe", stroke="#2563eb", rx=3))
    frags2.append(svgkit.text(375, 141, "dracut-initqueue", size=10, bold=True, color="#1e40af"))

    frags2.append(svgkit.rect(450, 120, 130, 35, fill="#dbeafe", stroke="#2563eb", rx=3))
    frags2.append(svgkit.text(515, 141, "dracut-mount", size=10, bold=True, color="#1e40af"))

    frags2.append(svgkit.rect(595, 120, 120, 35, fill="#dbeafe", stroke="#2563eb", rx=3))
    frags2.append(svgkit.text(655, 141, "dracut-pre-pivot", size=10, bold=True, color="#1e40af"))

    # mkinitcpio row
    frags2.append(svgkit.rect(20, 175, 710, 55, fill="#ecfdf5", stroke="#6ee7b7", rx=4))
    frags2.append(svgkit.text(45, 195, "mkinitcpio", bold=True, size=12, color="#065f46", anchor="start"))
    frags2.append(svgkit.text(45, 213, "(hooks)", size=9, color="#10b981", anchor="start"))

    frags2.append(svgkit.rect(170, 185, 120, 35, fill="#d1fae5", stroke="#059669", rx=3))
    frags2.append(svgkit.text(230, 206, "run_earlyhook", size=10, bold=True, color="#065f46"))

    frags2.append(svgkit.rect(310, 185, 130, 35, fill="#d1fae5", stroke="#059669", rx=3))
    frags2.append(svgkit.text(375, 206, "run_hook (udev)", size=10, bold=True, color="#065f46"))

    frags2.append(svgkit.rect(450, 185, 130, 35, fill="#d1fae5", stroke="#059669", rx=3))
    frags2.append(svgkit.text(515, 206, "run_latehook (encrypt)", size=10, bold=True, color="#065f46"))

    frags2.append(svgkit.rect(595, 185, 120, 35, fill="#d1fae5", stroke="#059669", rx=3))
    frags2.append(svgkit.text(655, 206, "run_cleanuphook", size=10, bold=True, color="#065f46"))

    # initramfs-tools row
    frags2.append(svgkit.rect(20, 240, 710, 55, fill="#fffbeb", stroke="#fcd34d", rx=4))
    frags2.append(svgkit.text(45, 260, "initramfs-tools", bold=True, size=12, color="#92400e", anchor="start"))
    frags2.append(svgkit.text(45, 278, "(scripts)", size=9, color="#f59e0b", anchor="start"))

    frags2.append(svgkit.rect(170, 250, 120, 35, fill="#fef3c7", stroke="#d97706", rx=3))
    frags2.append(svgkit.text(230, 271, "scripts/init-top", size=10, bold=True, color="#92400e"))

    frags2.append(svgkit.rect(310, 250, 130, 35, fill="#fef3c7", stroke="#d97706", rx=3))
    frags2.append(svgkit.text(375, 271, "scripts/local-top", size=10, bold=True, color="#92400e"))

    frags2.append(svgkit.rect(450, 250, 130, 35, fill="#fef3c7", stroke="#d97706", rx=3))
    frags2.append(svgkit.text(515, 271, "scripts/local-premount", size=10, bold=True, color="#92400e"))

    frags2.append(svgkit.rect(595, 250, 120, 35, fill="#fef3c7", stroke="#d97706", rx=3))
    frags2.append(svgkit.text(655, 271, "scripts/init-bottom", size=10, bold=True, color="#92400e"))

    svgkit.render(os.path.join(img_dir, "hook-execution-phases.svg"), 750, 310, *frags2, title="Фази виконання хуків та служб у ранньому просторі користувача")

if __name__ == "__main__":
    render()
