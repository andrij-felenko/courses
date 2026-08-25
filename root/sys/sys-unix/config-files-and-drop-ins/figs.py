import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit

def draw_three_tier_config_hierarchy():
    out = []
    
    # Left: Three Tiers Box
    out.append(svgkit.rect(20, 20, 290, 310, fill="#f8f9fa", stroke="#bdc3c7", sw=1.5, rx=8))
    out.append(svgkit.text(165, 42, "Трирівнева ієрархія каталогів", size=13, bold=True, color="#2c3e50"))
    
    # Tier 3 (/etc) - Admin overrides
    out.append(svgkit.rect(35, 55, 260, 75, fill="#fadbd8", stroke="#e74c3c", sw=1.5, rx=6))
    out.append(svgkit.text(165, 73, "/etc/sysctl.d/*.conf", size=12, bold=True, color="#922b21"))
    out.append(svgkit.text(165, 90, "1. Адміністратор (RW, пріоритет 1)", size=10, bold=True, color="#78281f"))
    out.append(svgkit.text(165, 107, "50-net.conf | 80-disable-ipv6.conf -> /dev/null", size=9, color="#922b21"))
    
    # Tier 2 (/run) - Transient runtime
    out.append(svgkit.rect(35, 140, 260, 75, fill="#fdebd0", stroke="#e67e22", sw=1.5, rx=6))
    out.append(svgkit.text(165, 158, "/run/sysctl.d/*.conf", size=12, bold=True, color="#a04000"))
    out.append(svgkit.text(165, 175, "2. Рантайм (tmpfs, пріоритет 2)", size=10, bold=True, color="#7e5109"))
    out.append(svgkit.text(165, 192, "20-cloud-init.conf (ефемерні правила)", size=9, color="#a04000"))

    # Tier 1 (/usr/lib) - Vendor defaults
    out.append(svgkit.rect(35, 225, 260, 90, fill="#d6eaf8", stroke="#3498db", sw=1.5, rx=6))
    out.append(svgkit.text(165, 243, "/usr/lib/sysctl.d/*.conf", size=12, bold=True, color="#1b4f72"))
    out.append(svgkit.text(165, 260, "3. Дистрибутив (RO, пріоритет 3)", size=10, bold=True, color="#154360"))
    out.append(svgkit.text(165, 277, "10-default.conf | 50-net.conf (затінено)", size=9, color="#1b4f72"))
    out.append(svgkit.text(165, 294, "80-disable-ipv6.conf (замасковано)", size=9, color="#7f8c8d"))

    # Middle Engine Box: Resolver and Sorter
    out.append(svgkit.rect(345, 95, 175, 160, fill="#2c3e50", stroke="#1a252f", sw=2, rx=8))
    out.append(svgkit.text(432, 125, "Резолвер конфігурації", size=12, bold=True, color="#ffffff"))
    out.append(svgkit.text(432, 148, "1. Скан /etc, /run, /usr/lib", size=10, color="#ecf0f1"))
    out.append(svgkit.text(432, 168, "2. Затінення за ім'ям", size=10, color="#f39c12"))
    out.append(svgkit.text(432, 188, "3. Відкидання /dev/null", size=10, color="#e74c3c"))
    out.append(svgkit.text(432, 208, "4. Сортування ASCII", size=10, color="#2ecc71"))
    out.append(svgkit.text(432, 230, "00- → 50- → 99-", size=10, bold=True, color="#3498db"))

    # Arrows from Tiers to Resolver
    out.append(svgkit.arrow(295, 92, 345, 140, color="#e74c3c", sw=1.8))
    out.append(svgkit.arrow(295, 175, 345, 175, color="#e67e22", sw=1.8))
    out.append(svgkit.arrow(295, 265, 345, 210, color="#3498db", sw=1.8))

    # Right: Effective Merged Config Output
    out.append(svgkit.rect(555, 20, 265, 310, fill="#eafaf1", stroke="#27ae60", sw=1.8, rx=8))
    out.append(svgkit.text(687, 42, "Результуючий потік параметрів", size=12, bold=True, color="#1e8449"))

    items = [
        ("1. 10-default.conf", "Джерело: /usr/lib (дефолти ОС)", "#2980b9", "#ebf5fb", 55),
        ("2. 20-cloud-init.conf", "Джерело: /run (налаштування хмари)", "#d35400", "#fef5e7", 120),
        ("3. 50-net.conf", "Джерело: /etc (перекрило /usr/lib)", "#c0392b", "#fdedec", 185),
        ("— 80-disable-ipv6.conf", "СТАН: ЗАМАСКОВАНО (/dev/null)", "#7f8c8d", "#f2f3f4", 250),
    ]

    for title, src, stroke_c, fill_c, y_pos in items:
        out.append(svgkit.rect(570, y_pos, 235, 55, fill=fill_c, stroke=stroke_c, sw=1.2, rx=5))
        out.append(svgkit.text(687, y_pos + 20, title, size=11, bold=True, color=stroke_c))
        out.append(svgkit.text(687, y_pos + 38, src, size=9.5, color="#2c3e50"))

    # Arrow from Resolver to Effective Output
    out.append(svgkit.arrow(520, 175, 555, 175, color="#27ae60", sw=2))

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    svgkit.render(os.path.join(img_dir, "three-tier-config-hierarchy.svg"), 840, 350, *out)

def draw_dropin_merging_and_override():
    out = []

    # Left Top: Main Vendor Unit
    out.append(svgkit.rect(20, 20, 370, 135, fill="#ebf5fb", stroke="#3498db", sw=1.5, rx=8))
    out.append(svgkit.text(205, 40, "Головний unit постачальника (/usr/lib/...)", size=12, bold=True, color="#1b4f72"))
    out.append(svgkit.text(205, 58, "/usr/lib/systemd/system/app.service", size=10, color="#566573"))
    
    code_vendor = [
        "[Service]",
        "ExecStart=/usr/bin/app --worker",
        "Restart=on-failure",
        "MemoryMax=1G"
    ]
    for i, line in enumerate(code_vendor):
        out.append(svgkit.text(40, 80 + i * 16, line, size=10, anchor="start", color="#1a252f"))

    # Left Bottom: Drop-in Directory
    out.append(svgkit.rect(20, 170, 370, 155, fill="#fdedec", stroke="#e74c3c", sw=1.5, rx=8))
    out.append(svgkit.text(205, 190, "Каталог drop-in адміністратора (/etc/...)", size=12, bold=True, color="#922b21"))
    out.append(svgkit.text(205, 208, "/etc/systemd/system/app.service.d/*.conf", size=10, color="#566573"))
    
    out.append(svgkit.rect(35, 220, 165, 90, fill="#ffffff", stroke="#e74c3c", sw=1, rx=4))
    out.append(svgkit.text(117, 236, "10-resources.conf", size=9.5, bold=True, color="#922b21"))
    out.append(svgkit.text(42, 256, "[Service]", size=9, anchor="start", color="#2c3e50"))
    out.append(svgkit.text(42, 272, "MemoryMax=4G", size=9, bold=True, anchor="start", color="#c0392b"))
    out.append(svgkit.text(42, 288, "CPUQuota=200%", size=9, bold=True, anchor="start", color="#27ae60"))

    out.append(svgkit.rect(210, 220, 165, 90, fill="#ffffff", stroke="#e74c3c", sw=1, rx=4))
    out.append(svgkit.text(292, 236, "20-exec.conf", size=9.5, bold=True, color="#922b21"))
    out.append(svgkit.text(217, 256, "[Service]", size=9, anchor="start", color="#2c3e50"))
    out.append(svgkit.text(217, 272, "ExecStart=", size=9, bold=True, anchor="start", color="#e67e22"))
    out.append(svgkit.text(217, 288, "ExecStart=/opt/app", size=9, bold=True, anchor="start", color="#2980b9"))

    # Middle Arrow Connection
    out.append(svgkit.arrow(390, 85, 450, 140, color="#3498db", sw=2))
    out.append(svgkit.arrow(390, 245, 450, 190, color="#e74c3c", sw=2))

    # Right: Effective Merged In-Memory Representation
    out.append(svgkit.rect(450, 20, 370, 305, fill="#fcf3cf", stroke="#f1c40f", sw=2, rx=8))
    out.append(svgkit.text(635, 45, "Ефективний стан юніта в пам'яті (PID 1)", size=12, bold=True, color="#7d6608"))
    out.append(svgkit.text(635, 65, "Результат конкатенації та перевизначень", size=10, color="#7d6608"))

    effective_lines = [
        ("[Unit] / [Service]", "#7f8c8d", False),
        ("ExecStart=/opt/app", "#2980b9", True),
        ("  ↳ ExecStart= очистив /usr/bin/app", "#7f8c8d", False),
        ("Restart=on-failure", "#1b4f72", False),
        ("  ↳ Успадковано без змін від постачальника", "#7f8c8d", False),
        ("MemoryMax=4G", "#c0392b", True),
        ("  ↳ Скаляр замінив значення 1G", "#7f8c8d", False),
        ("CPUQuota=200%", "#27ae60", True),
        ("  ↳ Додано нову директиву обмеження", "#7f8c8d", False),
    ]

    y_cur = 95
    for text_val, col, is_b in effective_lines:
        out.append(svgkit.text(475, y_cur, text_val, size=10, anchor="start", color=col, bold=is_b))
        y_cur += 22

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    svgkit.render(os.path.join(img_dir, "dropin-merging-and-override.svg"), 840, 345, *out)

def draw_stateless_system_factory_reset():
    out = []

    # 4 Steps Horizontal Pipeline
    steps = [
        (20, "1. Заводський образ", "Незмінний /usr", ["• /usr/bin, /usr/lib", "• Дефолтні конфіги", "• Монтування Read-Only"], "#2980b9", "#ebf5fb"),
        (225, "2. Чистий старт", "Порожній /etc та /var", ["• /etc = 0 байтів", "• /var не ініціалізовано", "• Детекція першого старту"], "#e67e22", "#fef5e7"),
        (430, "3. Авто-синтез", "Ініціалізація стану", ["• systemd-sysusers", "• systemd-tmpfiles", "• systemd-firstboot"], "#8e44ad", "#f4ecf7"),
        (635, "4. Робочий вузол", "Повний функціонал", ["• Локальна дельта в /etc", "• systemd-delta аудит", "• Скидання: rm -rf /etc/*"], "#27ae60", "#eafaf1")
    ]

    for x, title, subtitle, bullets, stroke_c, fill_c in steps:
        out.append(svgkit.rect(x, 25, 185, 200, fill=fill_c, stroke=stroke_c, sw=1.8, rx=8))
        out.append(svgkit.text(x + 92, 50, title, size=12, bold=True, color=stroke_c))
        out.append(svgkit.text(x + 92, 68, subtitle, size=10, bold=True, color="#2c3e50"))
        out.append(svgkit.line(x + 15, 78, x + 170, 78, color=stroke_c, sw=1))
        
        for i, b in enumerate(bullets):
            out.append(svgkit.text(x + 15, 105 + i * 26, b, size=9.5, anchor="start", color="#2c3e50"))

    # Arrows between steps
    out.append(svgkit.arrow(205, 125, 225, 125, color="#2c3e50", sw=2))
    out.append(svgkit.arrow(410, 125, 430, 125, color="#2c3e50", sw=2))
    out.append(svgkit.arrow(615, 125, 635, 125, color="#2c3e50", sw=2))

    # Bottom Reset Loop Arrow (Factory Reset)
    out.append(svgkit.rect(120, 250, 600, 60, fill="#fadbd8", stroke="#c0392b", sw=1.5, rx=6))
    out.append(svgkit.text(420, 272, "Factory Reset (Скидання до заводського стану)", size=12, bold=True, color="#922b21"))
    out.append(svgkit.text(420, 292, "Видалення /etc та /var повертає систему на Крок 2 без перевстановлення образу ОС", size=10, color="#78281f"))

    out.append(svgkit.arrow(725, 225, 725, 280, color="#c0392b", sw=1.8))
    out.append(svgkit.arrow(120, 280, 120, 225, color="#c0392b", sw=1.8))

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    svgkit.render(os.path.join(img_dir, "stateless-system-factory-reset.svg"), 840, 330, *out)

if __name__ == "__main__":
    draw_three_tier_config_hierarchy()
    draw_dropin_merging_and_override()
    draw_stateless_system_factory_reset()
