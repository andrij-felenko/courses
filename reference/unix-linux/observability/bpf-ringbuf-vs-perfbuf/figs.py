import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_figs():
    # -------------------------------------------------------------------------
    # 1. Perf Event Array (per-CPU buffers)
    # -------------------------------------------------------------------------
    w1, h1 = 780, 440
    frags1 = []

    # Title box
    tbox1, _, _ = textbox(390, 25, "Perf Event Array: Розділені per-CPU буфери пам'яті", size=16, bold=True, fill="#eef2f7", stroke="#2c3e50")
    frags1.append(tbox1)

    # CPU cores and their local buffers
    cpus_data = [
        ("CPU 0 (95% load)", "#e74c3c", "Переповнено! Drop", "#fadbd8"),
        ("CPU 1 (40% load)", "#3498db", "Нормальний потік", "#ebf5fb"),
        ("CPU 2 (10% load)", "#2ecc71", "Мало подій", "#e8f8f5"),
        ("CPU 3 (1% load)",  "#95a5a6", "Простій: марнотратство", "#f2f4f4")
    ]

    for i, (cpu_name, cpu_col, status, buf_fill) in enumerate(cpus_data):
        cx = 105 + i * 190
        # CPU box
        frags1.append(rect(cx - 75, 60, 150, 45, fill=buf_fill, stroke=cpu_col, sw=2, rx=6))
        frags1.append(mtext(cx, 87, cpu_name, size=13, bold=True, color=INK))

        # Arrow down to per-CPU buffer
        frags1.append(arrow(cx, 105, cx, 135, color=cpu_col, sw=2))

        # Per-CPU Ring Buffer
        frags1.append(rect(cx - 80, 140, 160, 130, fill="#ffffff", stroke="#34495e", sw=1.5, rx=6))
        frags1.append(mtext(cx, 160, f"Буфер CPU {i}", size=12, bold=True, color="#2c3e50"))
        
        # Buffer slots
        if i == 0:
            # Overflown slots
            for s in range(3):
                frags1.append(rect(cx - 70, 175 + s * 22, 140, 18, fill="#e74c3c", stroke="#c0392b", rx=3))
                frags1.append(text(cx, 189 + s * 22, f"Подія {s+1} (BUSY)", size=10, color="#ffffff", bold=True))
            frags1.append(text(cx, 255, "DROP ПОДІЙ!", size=11, color="#c0392b", bold=True))
        elif i == 1:
            frags1.append(rect(cx - 70, 175, 140, 18, fill="#3498db", stroke="#2980b9", rx=3))
            frags1.append(text(cx, 189, "Подія A (t=102ms)", size=10, color="#ffffff"))
            frags1.append(rect(cx - 70, 199, 140, 18, fill="#3498db", stroke="#2980b9", rx=3))
            frags1.append(text(cx, 213, "Подія B (t=115ms)", size=10, color="#ffffff"))
            frags1.append(text(cx, 250, "Вільна пам'ять 60%", size=10, color=MUTED))
        else:
            frags1.append(text(cx, 210, "Порожній буфер", size=11, color=MUTED, italic=True))
            frags1.append(text(cx, 250, "Пам'ять зарезервована", size=10, color=MUTED))

        # Status badge below buffer
        frags1.append(rect(cx - 75, 280, 150, 24, fill=buf_fill, stroke=cpu_col, rx=4))
        frags1.append(text(cx, 296, status, size=10, color=INK, bold=True))

        # Arrow down to User Space consumer
        frags1.append(arrow(cx, 304, cx, 345, color="#7f8c8d", sw=1.5))

    # User Space Reader Box
    frags1.append(rect(25, 350, 730, 70, fill="#f8f9fa", stroke="#2c3e50", sw=2, rx=8))
    frags1.append(mtext(390, 375, "User-Space Reader (epoll_wait по N файлових дескрипторах)", size=14, bold=True, color="#2c3e50"))
    frags1.append(mtext(390, 398, "Недолік: Події зчитуються почергово з CPU-буферів. Необхідне сортування в User Space для хронології!", size=11, color="#c0392b"))

    render(os.path.join(IMG, 'perfbuf-arch.svg'), w1, h1, *frags1, title="Perf Event Array Architecture")

    # -------------------------------------------------------------------------
    # 2. BPF Ring Buffer (shared lockless buffer + double mmap)
    # -------------------------------------------------------------------------
    w2, h2 = 780, 470
    frags2 = []

    # Title box
    tbox2, _, _ = textbox(390, 25, "BPF Ring Buffer: Єдиний розділювальний буфер з Zero-Copy mmap", size=16, bold=True, fill="#eef2f7", stroke="#2c3e50")
    frags2.append(tbox2)

    # Top CPUs producers
    for i in range(4):
        cx = 110 + i * 185
        frags2.append(rect(cx - 65, 60, 130, 40, fill="#eaf2f8", stroke="#2980b9", sw=1.5, rx=5))
        frags2.append(text(cx, 85, f"CPU {i} Probe", size=12, bold=True, color="#1b4f72"))
        frags2.append(arrow(cx, 100, 390 + (i-1.5)*60, 140, color="#2980b9", sw=1.8))

    # Single Shared Ring Buffer Container
    frags2.append(rect(50, 145, 680, 115, fill="#eaafaf10", stroke="#27ae60", sw=2, rx=8))
    frags2.append(text(390, 168, "Глобальний безблокувальний кільцевий буфер (Shared Ring Buffer)", size=14, bold=True, color="#1e8449"))

    # Ordered Events Queue inside shared buffer
    events_in_ring = [
        ("E1 (t=100ms)", "#27ae60", "CPU 0"),
        ("E2 (t=102ms)", "#27ae60", "CPU 1"),
        ("E3 (t=105ms)", "#27ae60", "CPU 0"),
        ("E4 (t=110ms)", "#27ae60", "CPU 2"),
        ("E5 (t=115ms)", "#f39c12", "Reserve..."),
    ]
    for idx, (ev_text, ev_col, cpu_src) in enumerate(events_in_ring):
        ex = 75 + idx * 132
        frags2.append(rect(ex, 185, 122, 45, fill="#e8f8f5", stroke=ev_col, sw=1.5, rx=4))
        frags2.append(text(ex + 61, 203, ev_text, size=11, bold=True, color="#145a32"))
        frags2.append(text(ex + 61, 221, cpu_src, size=10, color=MUTED))

    # Virtual Memory Double Mapping Diagram
    frags2.append(rect(50, 275, 680, 80, fill="#fcf3cf", stroke="#f39c12", sw=1.5, rx=6))
    frags2.append(text(390, 295, "Структура віртуальної пам'яті (Double mmap Mapping)", size=12, bold=True, color="#b9770e"))
    
    # Page layout boxes
    frags2.append(rect(65, 308, 120, 35, fill="#fadbd8", stroke="#e74c3c", rx=3))
    frags2.append(mtext(125, 330, "Header Page\n(prod/cons pos)", size=10, bold=True, color="#78281f"))

    frags2.append(rect(195, 308, 240, 35, fill="#d5f5e3", stroke="#27ae60", rx=3))
    frags2.append(mtext(315, 330, "Data Pages (Основний буфер N сторінок)", size=10, bold=True, color="#145a32"))

    frags2.append(rect(445, 308, 270, 35, fill="#d4efdf", stroke="#27ae60", sw=1, rx=3))
    frags2.append(mtext(580, 330, "Data Pages Mirror (Повторне mmap відображення)", size=10, bold=True, color="#1e8449"))

    # Arrow down to User Space consumer
    frags2.append(arrow(390, 355, 390, 385, color="#27ae60", sw=2))

    # User Space Reader Box
    frags2.append(rect(50, 390, 680, 65, fill="#e8f8f5", stroke="#27ae60", sw=2, rx=8))
    frags2.append(mtext(390, 413, "User-Space Consumer (ring_buffer__poll / zero-copy reserve-submit)", size=14, bold=True, color="#145a32"))
    frags2.append(text(390, 438, "Переваги: Повний хронологічний порядок (Total Order) + Економія пам'яті до 90%", size=11, color="#196f3d", bold=True))

    render(os.path.join(IMG, 'ringbuf-arch.svg'), w2, h2, *frags2, title="BPF Ring Buffer Architecture")

if __name__ == "__main__":
    render_figs()
