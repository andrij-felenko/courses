import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit

def draw_tmpfiles_hierarchy_and_flow():
    out = []
    
    # Config Locations Box (Left side)
    out.append(svgkit.rect(30, 40, 240, 240, fill="#f8f9fa", stroke="#bdc3c7", sw=1.5, rx=8))
    out.append(svgkit.text(150, 65, "Ієрархія tmpfiles.d", size=15, bold=True, color="#2c3e50"))
    
    # Priority Layers
    out.append(svgkit.rect(45, 85, 210, 45, fill="#fadbd8", stroke="#e74c3c", sw=1.5, rx=5))
    out.append(svgkit.text(150, 103, "/etc/tmpfiles.d/*.conf", size=12, bold=True, color="#922b21"))
    out.append(svgkit.text(150, 120, "1. Адміністратор (найвищий)", size=11, color="#78281f"))
    
    out.append(svgkit.rect(45, 140, 210, 45, fill="#fdebd0", stroke="#e67e22", sw=1.5, rx=5))
    out.append(svgkit.text(150, 158, "/run/tmpfiles.d/*.conf", size=12, bold=True, color="#a04000"))
    out.append(svgkit.text(150, 175, "2. Динамічні (рантайм)", size=11, color="#7e5109"))

    out.append(svgkit.rect(45, 195, 210, 45, fill="#d6eaf8", stroke="#3498db", sw=1.5, rx=5))
    out.append(svgkit.text(150, 213, "/usr/lib/tmpfiles.d/*.conf", size=12, bold=True, color="#1b4f72"))
    out.append(svgkit.text(150, 230, "3. Пакети дистрибутива", size=11, color="#154360"))
    
    # Parser Core Engine (Middle)
    out.append(svgkit.rect(330, 100, 180, 120, fill="#34495e", stroke="#2c3e50", sw=2, rx=10))
    out.append(svgkit.text(420, 140, "systemd-tmpfiles", size=15, bold=True, color="#ffffff"))
    out.append(svgkit.text(420, 165, "Декларативний парсер", size=12, color="#bdc3c7"))
    out.append(svgkit.text(420, 185, "&amp; Перевірка специфікацій", size=11, color="#ecf0f1"))
    
    # Arrow from Configs to Engine
    out.append(svgkit.arrow(270, 160, 330, 160, color="#2c3e50", sw=2))
    
    # Execution Modes (Right side)
    modes = [
        ("--create", "boot / setup.service", "Створення ФС-об'єктів, UID/GID, ACL, xattr", 50, "#27ae60", "#d4efdf"),
        ("--clean", "timer / clean.service", "Очищення за віком (Age: mtime, atime)", 135, "#2980b9", "#d4e6f1"),
        ("--remove", "shutdown / manual", "Видалення позначених шляхів (r/R)", 220, "#c0392b", "#fadbd8")
    ]
    
    for flag, trigger, desc, y_pos, stroke_c, fill_c in modes:
        out.append(svgkit.rect(570, y_pos, 220, 70, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        out.append(svgkit.text(680, y_pos + 22, flag, size=13, bold=True, color=stroke_c))
        out.append(svgkit.text(680, y_pos + 40, trigger, size=11, bold=True, color="#34495e"))
        out.append(svgkit.text(680, y_pos + 57, desc, size=10, color="#566573"))
        
        # Arrow from engine to modes
        out.append(svgkit.arrow(510, 160, 570, y_pos + 35, color=stroke_c, sw=1.5))
        
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "tmpfiles-hierarchy-and-flow.svg")
    svgkit.render(out_path, 820, 310, *out)

def draw_volatile_storage_architecture():
    out = []
    
    # Storage targets (3 Columns)
    targets = [
        ("/run", "tmpfs (ОЗП)", "Нестійке (до reboot)", "Сокети, PID, рантайм-стан", "Age: без автоочищення", 50, "#e74c3c", "#fadbd8"),
        ("/tmp", "tmpfs / disk", "Швидкі тимчасові файли", "Короткоживучий кєш / буфери", "Age: 10d (за замовчуванням)", 300, "#f39c12", "#fdebd0"),
        ("/var/tmp", "Диск (Persistent)", "Переживає перезавантаження", "Великі дампи, довгі обробки", "Age: 30d (за замовчуванням)", 550, "#27ae60", "#d4efdf")
    ]
    
    for path, fstype, life, usage, age_rule, x, stroke_c, fill_c in targets:
        out.append(svgkit.rect(x, 40, 220, 170, fill=fill_c, stroke=stroke_c, sw=2, rx=8))
        out.append(svgkit.text(x + 110, 68, path, size=16, bold=True, color=stroke_c))
        out.append(svgkit.text(x + 110, 92, fstype, size=12, bold=True, color="#2c3e50"))
        out.append(svgkit.text(x + 110, 115, life, size=11, color="#34495e"))
        out.append(svgkit.text(x + 110, 138, usage, size=11, color="#566573"))
        out.append(svgkit.text(x + 110, 168, age_rule, size=11, bold=True, color=stroke_c))
        
    # Safety Layer Box at the bottom
    out.append(svgkit.rect(50, 235, 720, 85, fill="#eaeded", stroke="#7f8c8d", sw=1.5, rx=8))
    out.append(svgkit.text(410, 258, "Механізми безпеки systemd-tmpfiles", size=14, bold=True, color="#2c3e50"))
    
    guards = [
        ("openat() + O_NOFOLLOW", 170),
        ("Захист від symlink-атак (TOCTOU)", 410),
        ("statx() аналіз btime / mtime / ctime", 650)
    ]
    for label, x_pos in guards:
        out.append(svgkit.rect(x_pos - 100, 275, 200, 32, fill="#ffffff", stroke="#95a5a6", sw=1, rx=4))
        out.append(svgkit.text(x_pos, 296, label, size=11, bold=True, color="#2c3e50"))

    # Connectors from targets to safety layer
    out.append(svgkit.line(160, 210, 160, 235, color="#7f8c8d", sw=1.5, dash="4,4"))
    out.append(svgkit.line(410, 210, 410, 235, color="#7f8c8d", sw=1.5, dash="4,4"))
    out.append(svgkit.line(660, 210, 660, 235, color="#7f8c8d", sw=1.5, dash="4,4"))

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "volatile-storage-architecture.svg")
    svgkit.render(out_path, 820, 340, *out)

if __name__ == "__main__":
    draw_tmpfiles_hierarchy_and_flow()
    draw_volatile_storage_architecture()
