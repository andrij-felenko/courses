import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_zbd_arch():
    frags = []
    
    # Outer frame
    frags.append(rect(20, 20, 760, 360, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(400, 50, "Адресний простір логічних блоків (LBA) зонованого накопичувача", size=16, bold=True, anchor="middle"))

    # Conventional Zone
    frags.append(rect(40, 80, 210, 240, fill="#eef6ff", stroke="#2457d6", sw=1.5, rx=6))
    frags.append(text(145, 110, "Conventional Zone", size=14, bold=True, color="#2457d6", anchor="middle"))
    frags.append(text(145, 132, "(Звичайна зона)", size=12, color=MUTED, anchor="middle"))
    
    # Sectors inside Conventional
    frags.append(rect(60, 160, 170, 70, fill="#ffffff", stroke="#90caf9", sw=1, rx=4))
    frags.append(text(145, 190, "Довільний запис", size=13, color=INK, anchor="middle"))
    frags.append(text(145, 210, "(Random I/O)", size=11, color=MUTED, anchor="middle"))
    
    frags.append(text(145, 260, "Запис у будь-який LBA", size=11, color=INK, anchor="middle"))
    frags.append(text(145, 280, "без обмежень WP", size=11, color=MUTED, anchor="middle"))

    # Sequential Zone (SWR / ZNS)
    frags.append(rect(270, 80, 490, 240, fill="#fff8e7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(515, 110, "Sequential Write Required Zone (SWR / ZNS)", size=14, bold=True, color="#b45309", anchor="middle"))
    frags.append(text(515, 132, "(Зона послідовного запису)", size=12, color=MUTED, anchor="middle"))

    # Written region
    frags.append(rect(290, 160, 160, 70, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=4))
    frags.append(text(370, 195, "Записані дані", size=13, color="#15803d", bold=True, anchor="middle"))
    frags.append(text(370, 215, "start ... WP-1", size=11, color=MUTED, anchor="middle"))

    # Unwritten (Capacity remaining)
    frags.append(rect(450, 160, 170, 70, fill="#ffffff", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(535, 195, "Вільне місце", size=13, color="#b45309", bold=True, anchor="middle"))
    frags.append(text(535, 215, "WP ... Capacity-1", size=11, color=MUTED, anchor="middle"))

    # Unused capacity gap up to Zone Size
    frags.append(rect(620, 160, 120, 70, fill="#f3f4f6", stroke="#9ca3af", sw=1.5, rx=4))
    frags.append(text(680, 195, "Невикористано", size=12, color="#4b5563", anchor="middle"))
    frags.append(text(680, 215, "Capacity ... Size-1", size=11, color=MUTED, anchor="middle"))

    # Write Pointer line & marker
    frags.append(line(450, 145, 450, 245, color="#c0392b", sw=2.5))
    frags.append(textbox(450, 275, "Write Pointer (WP)", size=12, pad=6, fill="#fee2e2", stroke="#c0392b", color="#b91c1c", bold=True)[0])

    # Zone Capacity & Zone Size markers
    frags.append(line(620, 150, 620, 240, color="#d97706", sw=1.5, dash="2,2"))
    frags.append(text(620, 260, "Zone Capacity", size=11, color="#b45309", anchor="middle", bold=True))

    frags.append(line(740, 150, 740, 240, color="#4b5563", sw=1.5, dash="2,2"))
    frags.append(text(740, 260, "Zone Size", size=11, color="#374151", anchor="middle", bold=True))

    # Bottom explanation
    frags.append(text(400, 350, "Послідовний запис суворо на межі WP; після досягнення Zone Capacity зона стає Full.", size=12, italic=True, color=MUTED, anchor="middle"))

    return frags

def render_zone_append_flow():
    frags = []

    # Outer frame
    frags.append(rect(20, 20, 760, 380, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(400, 48, "Порівняння запису WRITE (із блокуванням) та Zone Append (паралельно)", size=15, bold=True, anchor="middle"))

    # Panel Left: WRITE
    frags.append(rect(40, 75, 345, 305, fill="#fcfcfc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(212, 100, "Класичний WRITE (потрібна серіалізація)", size=13, bold=True, color="#c0392b", anchor="middle"))

    frags.append(rect(70, 120, 120, 40, fill="#fee2e2", stroke="#ef4444", rx=4))
    frags.append(text(130, 145, "Thread A (LBA=100)", size=11, anchor="middle"))

    frags.append(rect(235, 120, 120, 40, fill="#fee2e2", stroke="#ef4444", rx=4))
    frags.append(text(295, 145, "Thread B (LBA=100?)", size=11, anchor="middle"))

    # Lock box
    frags.append(rect(120, 180, 185, 45, fill="#fef3c7", stroke="#f59e0b", rx=4))
    frags.append(text(212, 200, "Хостове блокування зони", size=12, bold=True, color="#b45309", anchor="middle"))
    frags.append(text(212, 217, "(Zone Mutex Wait)", size=10, color=MUTED, anchor="middle"))

    frags.append(arrow(130, 160, 180, 180, color="#ef4444"))
    frags.append(arrow(295, 160, 245, 180, color="#ef4444"))

    # Single queue execution
    frags.append(arrow(212, 225, 212, 250, color="#333"))
    frags.append(rect(90, 250, 245, 55, fill="#ffffff", stroke="#94a3b8", rx=4))
    frags.append(text(212, 272, "Послідовна відправка WRITE", size=11, bold=True, anchor="middle"))
    frags.append(text(212, 290, "1. Write(LBA=100) -> wait -> 2. Write(LBA=104)", size=10, color=MUTED, anchor="middle"))

    frags.append(text(212, 355, "Низький паралелізм, затримки очікування блокування", size=11, color="#b91c1c", italic=True, anchor="middle"))

    # Panel Right: Zone Append
    frags.append(rect(415, 75, 345, 305, fill="#fcfcfc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(587, 100, "ZNS Zone Append (апаратна черга)", size=13, bold=True, color="#15803d", anchor="middle"))

    frags.append(rect(445, 120, 120, 40, fill="#dcfce7", stroke="#22c55e", rx=4))
    frags.append(text(505, 145, "Thread A (Zone 10)", size=11, anchor="middle"))

    frags.append(rect(610, 120, 120, 40, fill="#dcfce7", stroke="#22c55e", rx=4))
    frags.append(text(670, 145, "Thread B (Zone 10)", size=11, anchor="middle"))

    # Arrows down to controller queue directly
    frags.append(arrow(505, 160, 545, 195, color="#16a34a"))
    frags.append(arrow(670, 160, 630, 195, color="#16a34a"))

    frags.append(rect(460, 195, 255, 60, fill="#f0fdf4", stroke="#16a34a", rx=4))
    frags.append(text(587, 218, "NVMe Controller HW Serializer", size=12, bold=True, color="#15803d", anchor="middle"))
    frags.append(text(587, 240, "Контролер пристрою сам призначає LBA!", size=10, color=MUTED, anchor="middle"))

    frags.append(arrow(587, 255, 587, 280, color="#16a34a"))
    frags.append(rect(460, 280, 255, 45, fill="#ffffff", stroke="#86efac", rx=4))
    frags.append(text(587, 298, "Completion Queue: повертає LBA A та LBA B", size=11, bold=True, color="#15803d", anchor="middle"))
    frags.append(text(587, 315, "без жодних хостових mutex/locks", size=10, color=MUTED, anchor="middle"))

    frags.append(text(587, 355, "Максимальна пропускна здатність та паралелізм", size=11, color="#15803d", italic=True, anchor="middle"))

    return frags

def main():
    frags1 = render_zbd_arch()
    render(os.path.join(IMG, 'zbd-architecture.svg'), 800, 400, *frags1, title="Архітектура ZBD")

    frags2 = render_zone_append_flow()
    render(os.path.join(IMG, 'zone-append-flow.svg'), 800, 420, *frags2, title="Zone Append паралелізм")

if __name__ == "__main__":
    main()
