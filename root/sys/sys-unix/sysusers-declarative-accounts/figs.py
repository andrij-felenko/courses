import sys
import os

# Insert path to scripts directory (4 levels up from topic dir)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def render_sysusers_flow():
    # Width 850, Height 420
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 420" width="100%" height="100%">')
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#333333"/></marker></defs>')
    out.append(rect(0, 0, 850, 420, fill="#ffffff", stroke="none"))
    
    # Title / Top banner
    out.append(text(425, 25, "Конвеєр декларативного опрацювання системних акаунтів", size=16, bold=True))
    
    # Column 1: Config Sources (Left)
    out.append(rect(20, 50, 230, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    out.append(text(135, 75, "Джерела конфігурації", size=14, bold=True, color="#1e293b"))
    
    b1, _, _ = textbox(135, 120, "/etc/sysusers.d/*.conf\n(Пріоритет 1: Адмін)", size=12, pad=8, fill="#eff6ff", stroke="#3b82f6")
    b2, _, _ = textbox(135, 200, "/run/sysusers.d/*.conf\n(Пріоритет 2: Runtime)", size=12, pad=8, fill="#f0fdf4", stroke="#22c55e")
    b3, _, _ = textbox(135, 280, "/usr/lib/sysusers.d/*.conf\n(Пріоритет 3: Пакет)", size=12, pad=8, fill="#fef3c7", stroke="#f59e0b")
    
    out.append(b1)
    out.append(b2)
    out.append(b3)
    out.append(text(135, 360, "Перекриття та маскування", size=11, italic=True, color="#64748b"))
    
    # Arrows from Sources to Processing Engine
    out.append(arrow(250, 120, 310, 190, color="#3b82f6", sw=2))
    out.append(arrow(250, 200, 310, 200, color="#22c55e", sw=2))
    out.append(arrow(250, 280, 310, 210, color="#f59e0b", sw=2))
    
    # Column 2: systemd-sysusers Engine (Middle)
    out.append(rect(310, 50, 240, 340, fill="#f1f5f9", stroke="#64748b", sw=2, rx=8))
    out.append(text(430, 75, "systemd-sysusers", size=15, bold=True, color="#0f172a"))
    
    e1, _, _ = textbox(430, 125, "1. Злиття та вирішення\nконфліктів файлів", size=12, pad=8, fill="#ffffff", stroke="#94a3b8")
    e2, _, _ = textbox(430, 195, "2. Блокування бази\n(lckpwdf)", size=12, pad=8, fill="#fee2e2", stroke="#ef4444")
    e3, _, _ = textbox(430, 265, "3. Розподіл вільних\nUID / GID (1..999)", size=12, pad=8, fill="#ffffff", stroke="#94a3b8")
    e4, _, _ = textbox(430, 340, "4. Запис у *.tmp та\nатомарний rename()", size=12, pad=8, fill="#dcfce7", stroke="#16a34a")
    
    out.append(e1)
    out.append(arrow(430, 150, 430, 170, color="#64748b", sw=1.5))
    out.append(e2)
    out.append(arrow(430, 220, 430, 240, color="#64748b", sw=1.5))
    out.append(e3)
    out.append(arrow(430, 290, 430, 315, color="#64748b", sw=1.5))
    out.append(e4)
    
    # Arrows from Engine to Output Databases
    out.append(arrow(550, 340, 600, 110, color="#16a34a", sw=2))
    out.append(arrow(550, 340, 600, 190, color="#16a34a", sw=2))
    out.append(arrow(550, 340, 600, 270, color="#16a34a", sw=2))
    out.append(arrow(550, 340, 600, 350, color="#16a34a", sw=2))
    
    # Column 3: System Target Files (Right)
    out.append(rect(600, 50, 230, 340, fill="#fafafa", stroke="#d4d4d8", sw=1.5, rx=8))
    out.append(text(715, 75, "Системні бази даних", size=14, bold=True, color="#18181b"))
    
    f1, _, _ = textbox(715, 110, "/etc/passwd\n(Записи користувачів)", size=12, pad=6, fill="#ffffff", stroke="#a1a1aa")
    f2, _, _ = textbox(715, 190, "/etc/group\n(Записи та члени груп)", size=12, pad=6, fill="#ffffff", stroke="#a1a1aa")
    f3, _, _ = textbox(715, 270, "/etc/shadow\n(Заблоковані паролі '!')", size=12, pad=6, fill="#fef2f2", stroke="#f87171")
    f4, _, _ = textbox(715, 350, "/etc/gshadow\n(Тіньові записи груп)", size=12, pad=6, fill="#fef2f2", stroke="#f87171")
    
    out.append(f1)
    out.append(f2)
    out.append(f3)
    out.append(f4)
    
    out.append('</svg>')
    
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    with open(os.path.join(img_dir, "sysusers-flow.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))

def render_sysusers_precedence():
    # Width 800, Height 280
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 280" width="100%" height="100%">')
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#333333"/></marker></defs>')
    out.append(rect(0, 0, 800, 280, fill="#ffffff", stroke="none"))
    
    out.append(text(400, 25, "Ієрархія пріоритетів та маскування конфігурацій sysusers.d", size=15, bold=True))
    
    # Box 1: /etc
    b1, _, _ = textbox(150, 110, "/etc/sysusers.d/foo.conf\n\nАдміністраторський файл\n(Найвищий пріоритет)", size=13, pad=12, fill="#eff6ff", stroke="#2563eb", min_w=220)
    out.append(b1)
    
    # Box 2: /run
    b2, _, _ = textbox(400, 110, "/run/sysusers.d/foo.conf\n\nТимчасові правила\n(Середній пріоритет)", size=13, pad=12, fill="#f0fdf4", stroke="#16a34a", min_w=220)
    out.append(b2)
    
    # Box 3: /usr/lib
    b3, _, _ = textbox(650, 110, "/usr/lib/sysusers.d/foo.conf\n\nПакетний дефолт\n(Низький пріоритет)", size=13, pad=12, fill="#fef3c7", stroke="#d97706", min_w=220)
    out.append(b3)
    
    # Overriding arrows: /etc overrides /run and /usr/lib
    out.append(arrow(265, 110, 285, 110, color="#2563eb", sw=2))
    out.append(arrow(515, 110, 535, 110, color="#16a34a", sw=2))
    
    # Bottom note on /dev/null symlink
    note, _, _ = textbox(400, 220, "Маскування: створення симлінку /etc/sysusers.d/foo.conf -> /dev/null\nповністю вимикає правило з /usr/lib/sysusers.d/foo.conf", size=12, pad=10, fill="#fef2f2", stroke="#dc2626", min_w=600)
    out.append(note)
    
    out.append('</svg>')
    
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    with open(os.path.join(img_dir, "sysusers-precedence.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    render_sysusers_flow()
    render_sysusers_precedence()
    print("SVG figures rendered successfully.")
