import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..", "scripts")))
from svgkit import render, rect, fitbox, arrow, text, BG, INK, POS, NEG, FIELD, LINE

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def make_bpf_iter_arch():
    frags = []
    
    # Background Canvas Box
    frags.append(rect(0, 0, 800, 360, fill=BG, stroke="none"))
    
    # Userspace Region
    frags.append(rect(30, 30, 240, 300, fill="#f8fafc", stroke="#cbd5e1", sw=2, rx=8))
    frags.append(text(150, 60, "Userspace", size=16, color=INK, bold=True))
    frags.append(fitbox(50, 90, 200, 50, "Утиліта читання\nopen() + read()", fill="#e2e8f0", stroke="#94a3b8"))
    frags.append(fitbox(50, 160, 200, 50, "Файловий дескриптор\nfd = open('/sys/fs/bpf/tasks')", fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(50, 230, 200, 70, "Потік виводу\n(JSON / ASCII / Binary)\nбез парсингу в ядрі", fill="#e0f2fe", stroke="#0284c7"))

    # Kernel Space Region
    frags.append(rect(310, 30, 460, 300, fill="#f1f5f9", stroke="#94a3b8", sw=2, rx=8))
    frags.append(text(540, 60, "Kernel Space (eBPF & VFS)", size=16, color=INK, bold=True))

    # Kernel Subsystems inside Kernel Space
    frags.append(fitbox(330, 90, 200, 60, "Файлова система bpffs\n(/sys/fs/bpf/tasks)", fill="#ffffff", stroke="#64748b"))
    frags.append(fitbox(550, 90, 200, 60, "Підсистема seq_file\n(буфер запису)", fill="#fef3c7", stroke="#d97706"))

    frags.append(fitbox(330, 180, 420, 60, "Програма BPF (bpf_iter/task)\nIn-kernel Filtering & bpf_seq_printf()", fill="#dcfce7", stroke="#16a34a"))
    frags.append(fitbox(330, 260, 420, 50, "Структури даних ядра (Lockless RCU Traversal)\ntask_struct -> task_struct -> task_struct", fill="#fee2e2", stroke="#dc2626"))

    # Arrows
    frags.append(arrow(150, 140, 150, 160, color=LINE))
    frags.append(arrow(250, 185, 330, 120, color=NEG))
    frags.append(arrow(430, 150, 430, 180, color=LINE))
    frags.append(arrow(540, 260, 540, 240, color=FIELD))
    frags.append(arrow(650, 180, 650, 150, color=LINE))
    frags.append(arrow(550, 120, 250, 260, color=POS))

    render(os.path.join(IMG, 'bpf-iter-arch.svg'), 800, 360, *frags)

def make_user_ringbuf():
    frags = []
    
    # Background
    frags.append(rect(0, 0, 800, 360, fill=BG, stroke="none"))
    
    # Userspace Producer
    frags.append(rect(30, 30, 230, 300, fill="#f8fafc", stroke="#cbd5e1", sw=2, rx=8))
    frags.append(text(145, 60, "Userspace Producer", size=16, color=INK, bold=True))
    frags.append(fitbox(45, 90, 200, 50, "Генератор подій / політик\n(App / Daemon)", fill="#e0e7ff", stroke="#4f46e5"))
    frags.append(fitbox(45, 160, 200, 60, "libbpf helper API\nreserve() -> write -> submit()", fill="#dcfce7", stroke="#16a34a"))
    frags.append(fitbox(45, 240, 200, 60, "Zero-Syscall Write!\nПрямий запис у mmap", fill="#fef3c7", stroke="#d97706"))

    # Shared Memory Region (Ring Buffer)
    frags.append(rect(280, 30, 240, 300, fill="#fefce8", stroke="#eab308", sw=2, rx=8))
    frags.append(text(400, 60, "BPF User Ring Buffer", size=16, color=INK, bold=True))
    frags.append(fitbox(295, 90, 210, 45, "Consumer Page (Kernel Head)", fill="#ffffff", stroke="#ca8a04"))
    frags.append(fitbox(295, 145, 210, 45, "Producer Page (User Tail)", fill="#ffffff", stroke="#ca8a04"))
    frags.append(fitbox(295, 200, 210, 115, "Ring Data Pages\n[ S2 (Commit) ][ S1 (Commit) ]\n[ S3 (Alloc)  ][ Free Space  ]", fill="#fef08a", stroke="#ca8a04"))

    # Kernel Consumer
    frags.append(rect(540, 30, 230, 300, fill="#f1f5f9", stroke="#94a3b8", sw=2, rx=8))
    frags.append(text(655, 60, "Kernel eBPF Consumer", size=16, color=INK, bold=True))
    frags.append(fitbox(555, 90, 200, 60, "bpf_user_ringbuf_drain()\nPolling / Event Callback", fill="#dbeafe", stroke="#2563eb"))
    frags.append(fitbox(555, 170, 200, 60, "bpf_dynptr Engine\nБезпечна розпаковка", fill="#e0e7ff", stroke="#4338ca"))
    frags.append(fitbox(555, 250, 200, 60, "Двигун фільтрації / XDP\nОновлення таблиць в ядрі", fill="#dcfce7", stroke="#15803d"))

    # Connections
    frags.append(arrow(245, 270, 295, 250, color=POS))
    frags.append(arrow(505, 250, 555, 120, color=NEG))
    frags.append(arrow(655, 150, 655, 170, color=LINE))
    frags.append(arrow(655, 230, 655, 250, color=LINE))

    render(os.path.join(IMG, 'bpf-user-ringbuf.svg'), 800, 360, *frags)

if __name__ == "__main__":
    make_bpf_iter_arch()
    make_user_ringbuf()
    print("Generated SVGs successfully")
