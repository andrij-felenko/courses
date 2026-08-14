# -*- coding: utf-8 -*-
import os
import sys

# Path to scripts/ directory from reference/unix-linux/observability/user-events-ftrace-subsystem
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_architecture_svg(out_file):
    frags = []

    # Title
    frags.append(text(410, 30, "Архітектура підсистеми User Events у Linux", size=18, bold=True))

    # Boundary boxes: Userspace and Kernel Space
    frags.append(rect(30, 60, 360, 390, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(210, 85, "Простір користувача (Userspace)", size=15, bold=True, color="#1e293b"))

    frags.append(rect(430, 60, 360, 390, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(610, 85, "Ядро Linux (Kernel space)", size=15, bold=True, color="#14532d"))

    # Userspace components
    frags.append(rect(60, 110, 300, 70, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(mtext(210, 133, ["Прикладний застосунок", "(C / C++ / Rust / Go)"], size=13, color="#0369a1", bold=True))

    frags.append(rect(60, 210, 300, 80, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(mtext(210, 233, ["Zero-Overhead Перевірка (mmap)", "1. Читання байта статусу з RAM", "2. Якщо 0 -> пропуск виклику"], size=12, color="#92400e"))

    frags.append(rect(60, 320, 300, 110, fill="#e0e7ff", stroke="#4f46e5", sw=1.5, rx=6))
    frags.append(mtext(210, 343, ["Формування та відправка події", "• ioctl(DIAG_IOCSREG) - реєстрація", "• writev(fd, iov) - бистрий payload"], size=12, color="#3730a3"))

    # Kernel components
    frags.append(rect(460, 110, 300, 70, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(mtext(610, 133, ["Інтерфейс tracefs / VFS", "/sys/kernel/tracing/user_events_data"], size=13, color="#15803d", bold=True))

    frags.append(rect(460, 210, 300, 70, fill="#fae8ff", stroke="#c026d3", sw=1.5, rx=6))
    frags.append(mtext(610, 233, ["Підсистема tracepoint ядра", "events/user_events/<event_name>"], size=13, color="#86198f", bold=True))

    frags.append(rect(460, 310, 90, 110, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=6))
    frags.append(mtext(505, 345, ["ftrace", "ring", "buffer"], size=12, color="#991b1b", bold=True))

    frags.append(rect(565, 310, 90, 110, fill="#ffedd5", stroke="#ea580c", sw=1.5, rx=6))
    frags.append(mtext(610, 345, ["perf", "events", "system"], size=12, color="#9a3412", bold=True))

    frags.append(rect(670, 310, 90, 110, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=6))
    frags.append(mtext(715, 345, ["eBPF", "probes", "(tp)"], size=12, color="#854d0e", bold=True))

    # Arrows between blocks
    frags.append(arrow(210, 180, 210, 210, color="#0284c7", sw=2))
    frags.append(arrow(210, 290, 210, 320, color="#d97706", sw=2))

    # Across boundary arrows
    frags.append(arrow(360, 375, 460, 145, color="#4f46e5", sw=2))
    frags.append(arrow(460, 145, 360, 250, color="#16a34a", sw=2))

    frags.append(arrow(610, 180, 610, 210, color="#16a34a", sw=2))
    frags.append(arrow(610, 280, 505, 310, color="#c026d3", sw=1.5))
    frags.append(arrow(610, 280, 610, 310, color="#c026d3", sw=1.5))
    frags.append(arrow(610, 280, 715, 310, color="#c026d3", sw=1.5))

    render(out_file, 820, 480, *frags)
    print(f"Saved {out_file}")

def generate_payload_svg(out_file):
    frags = []

    frags.append(text(410, 30, "Бінарна структура пакунка події у writev()", size=18, bold=True))

    # iovec[0] - Header
    frags.append(rect(40, 70, 200, 140, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=6))
    frags.append(mtext(140, 95, ["iovec[0]: Заголовок події", "(4 байти, write_index)"], size=13, color="#1e40af", bold=True))
    frags.append(rect(55, 135, 170, 55, fill="#ffffff", stroke="#3b82f6", sw=1.2, rx=4))
    frags.append(mtext(140, 155, ["u32 write_index", "(ID від ядра)"], size=12, color="#1d4ed8"))

    # iovec[1] - Payload
    frags.append(rect(270, 70, 510, 240, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(525, 95, "iovec[1]: Структуроване тіло події (Payload)", size=14, bold=True, color="#15803d"))

    # Fixed fields
    frags.append(rect(290, 120, 230, 70, fill="#ffffff", stroke="#22c55e", sw=1.2, rx=4))
    frags.append(mtext(405, 142, ["Фіксовані поля", "u32 count / u64 latency"], size=12, color="#166534", bold=True))

    # Dynamic location header
    frags.append(rect(535, 120, 230, 70, fill="#fef9c3", stroke="#eab308", sw=1.2, rx=4))
    frags.append(mtext(650, 142, ["__data_loc дескриптор", "u16 offset | u16 len"], size=12, color="#854d0e", bold=True))

    # Dynamic payload region
    frags.append(rect(290, 215, 475, 75, fill="#fae8ff", stroke="#d946ef", sw=1.2, rx=4))
    frags.append(mtext(527, 242, ["Динамічні дані змінної довжини (char[] / u8[])", "Рядки, масиви байтів або вкладені структури"], size=12, color="#86198f", bold=True))

    # Pointer arrow from __data_loc to dynamic payload
    frags.append(arrow(650, 190, 527, 215, color="#eab308", sw=2))

    render(out_file, 820, 360, *frags)
    print(f"Saved {out_file}")

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    generate_architecture_svg(os.path.join(img_dir, "architecture.svg"))
    generate_payload_svg(os.path.join(img_dir, "payload-structure.svg"))

if __name__ == "__main__":
    main()
