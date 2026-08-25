import os
import sys
from pathlib import Path

# Add scripts directory to path for svgkit
sys.path.append(str(Path(__file__).resolve().parents[4] / "scripts"))
import svgkit

IMG_DIR = Path(__file__).resolve().parent / "img"

def draw_ptrace_flow():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    elements = []
    
    # Tracer Box
    elements.append(svgkit.rect(30, 40, 160, 320, fill="#e3f2fd", stroke="#1565c0", sw=2, rx=8))
    elements.append(svgkit.text(110, 70, "Трасувальник (Tracer)", bold=True, size=13, color="#0d47a1"))
    elements.append(svgkit.text(110, 95, "strace / gdb", size=11, color="#1565c0"))
    
    elements.append(svgkit.rect(45, 140, 130, 40, fill="#ffffff", stroke="#1565c0", rx=5))
    elements.append(svgkit.text(110, 165, "waitpid() чекає", size=11))

    elements.append(svgkit.rect(45, 260, 130, 50, fill="#ffffff", stroke="#1565c0", rx=5))
    elements.append(svgkit.mtext(110, 280, "PTRACE_PEEKDATA\nPTRACE_SYSCALL", size=10))

    # Kernel Box
    elements.append(svgkit.rect(230, 40, 200, 320, fill="#fff3e0", stroke="#e65100", sw=2, rx=8))
    elements.append(svgkit.text(330, 70, "Ядро Linux", bold=True, size=13, color="#bf360c"))
    elements.append(svgkit.text(330, 95, "do_syscall_64()", size=11, color="#e65100"))

    elements.append(svgkit.rect(245, 130, 170, 50, fill="#ffe0b2", stroke="#e65100", rx=5))
    elements.append(svgkit.mtext(330, 150, "Точка sys_enter\n_TIF_SYSCALL_TRACE", size=10))

    elements.append(svgkit.rect(245, 210, 170, 40, fill="#ffe0b2", stroke="#e65100", rx=5))
    elements.append(svgkit.text(330, 235, "Виконання виклику", size=10))

    elements.append(svgkit.rect(245, 280, 170, 50, fill="#ffe0b2", stroke="#e65100", rx=5))
    elements.append(svgkit.mtext(330, 300, "Точка sys_exit\nПеревірка коду повернення", size=10))

    # Tracee Box
    elements.append(svgkit.rect(470, 40, 160, 320, fill="#f3e5f5", stroke="#7b1fa2", sw=2, rx=8))
    elements.append(svgkit.text(550, 70, "Трасований (Tracee)", bold=True, size=13, color="#4a148c"))
    elements.append(svgkit.text(550, 95, "Робочий процес", size=11, color="#7b1fa2"))

    elements.append(svgkit.rect(485, 135, 130, 40, fill="#ffffff", stroke="#7b1fa2", rx=5))
    elements.append(svgkit.text(550, 160, "syscall (write)", size=11))

    elements.append(svgkit.rect(485, 285, 130, 40, fill="#ffffff", stroke="#7b1fa2", rx=5))
    elements.append(svgkit.text(550, 310, "Повернення в Ring 3", size=11))

    # Arrows & Labels
    elements.append(svgkit.arrow(485, 155, 415, 155, color="#7b1fa2", sw=2))
    
    elements.append(svgkit.arrow(245, 155, 175, 155, color="#d32f2f", sw=2))
    elements.append(svgkit.text(210, 145, "SIGTRAP (enter)", size=10, color="#d32f2f"))

    elements.append(svgkit.arrow(175, 285, 245, 285, color="#1565c0", sw=2))
    elements.append(svgkit.text(210, 275, "PTRACE_SYSCALL", size=10, color="#1565c0"))

    elements.append(svgkit.arrow(245, 305, 175, 305, color="#d32f2f", sw=2))
    elements.append(svgkit.text(210, 320, "SIGTRAP (exit)", size=10, color="#d32f2f"))

    elements.append(svgkit.arrow(415, 305, 485, 305, color="#388e3c", sw=2))

    svgkit.render(str(IMG_DIR / "ptrace-flow.svg"), 660, 390, *elements)

def draw_seccomp_notif():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    elements = []

    # Target Process Box
    elements.append(svgkit.rect(30, 40, 160, 300, fill="#ffebee", stroke="#c62828", sw=2, rx=8))
    elements.append(svgkit.text(110, 70, "Цільовий процес", bold=True, size=13, color="#b71c1c"))
    elements.append(svgkit.text(110, 95, "(Контейнер)", size=11, color="#c62828"))

    elements.append(svgkit.rect(45, 140, 130, 50, fill="#ffffff", stroke="#c62828", rx=5))
    elements.append(svgkit.mtext(110, 160, "Заблокований на\nmkdirat()", size=10))

    # Kernel Seccomp BPF Box
    elements.append(svgkit.rect(230, 40, 200, 300, fill="#eceff1", stroke="#37474f", sw=2, rx=8))
    elements.append(svgkit.text(330, 70, "Ядро: Seccomp BPF", bold=True, size=13, color="#263238"))

    elements.append(svgkit.rect(245, 120, 170, 50, fill="#cfd8dc", stroke="#37474f", rx=5))
    elements.append(svgkit.mtext(330, 140, "Фільтр повертає\nSECCOMP_RET_USER_NOTIF", size=10))

    elements.append(svgkit.rect(245, 210, 170, 50, fill="#cfd8dc", stroke="#37474f", rx=5))
    elements.append(svgkit.mtext(330, 230, "Черга сповіщень\nlistener_fd", size=10))

    # Supervisor Box
    elements.append(svgkit.rect(470, 40, 160, 300, fill="#e8f5e9", stroke="#2e7d32", sw=2, rx=8))
    elements.append(svgkit.text(550, 70, "Супервізор", bold=True, size=13, color="#1b5e20"))
    elements.append(svgkit.text(550, 95, "gVisor / systemd", size=11, color="#2e7d32"))

    elements.append(svgkit.rect(485, 120, 130, 60, fill="#ffffff", stroke="#2e7d32", rx=5))
    elements.append(svgkit.mtext(550, 140, "NOTIF_RECV\nioctl()", size=10))

    elements.append(svgkit.rect(485, 210, 130, 60, fill="#ffffff", stroke="#2e7d32", rx=5))
    elements.append(svgkit.mtext(550, 230, "NOTIF_SEND\n(val / error)", size=10))

    # Arrows
    elements.append(svgkit.arrow(175, 145, 245, 145, color="#c62828", sw=2))

    elements.append(svgkit.arrow(415, 145, 485, 145, color="#2e7d32", sw=2))
    elements.append(svgkit.text(450, 135, "Запит", size=10, color="#2e7d32"))

    elements.append(svgkit.arrow(485, 235, 415, 235, color="#1565c0", sw=2))
    elements.append(svgkit.text(450, 225, "Відповідь", size=10, color="#1565c0"))

    elements.append(svgkit.arrow(245, 235, 175, 235, color="#2e7d32", sw=2))
    elements.append(svgkit.text(210, 225, "Результат", size=10, color="#2e7d32"))

    svgkit.render(str(IMG_DIR / "seccomp-notif.svg"), 660, 360, *elements)

def draw_ptrace_vs_seccomp_perf():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    elements = []

    # Container 1: ptrace Overhead
    elements.append(svgkit.rect(30, 40, 180, 280, fill="#fff8e1", stroke="#ffa000", sw=2, rx=8))
    elements.append(svgkit.text(120, 70, "ptrace", bold=True, size=15, color="#ff8f00"))
    elements.append(svgkit.text(120, 95, "4 switches / syscall", size=11))
    elements.append(svgkit.text(120, 115, "Високі накладні витрати", size=10, color="#d84315"))

    elements.append(svgkit.rect(45, 140, 150, 40, fill="#ffe0b2", stroke="#ff8f00", rx=4))
    elements.append(svgkit.text(120, 165, "sys_enter: 2 switches", size=9))

    elements.append(svgkit.rect(45, 190, 150, 40, fill="#ffe0b2", stroke="#ff8f00", rx=4))
    elements.append(svgkit.text(120, 215, "Контекстний зупин", size=9))

    elements.append(svgkit.rect(45, 240, 150, 40, fill="#ffcc80", stroke="#ff8f00", rx=4))
    elements.append(svgkit.text(120, 265, "sys_exit: 2 switches", size=9))

    # Container 2: Seccomp User Notif
    elements.append(svgkit.rect(240, 40, 180, 280, fill="#e8f5e9", stroke="#43a047", sw=2, rx=8))
    elements.append(svgkit.text(330, 70, "seccomp notif", bold=True, size=15, color="#2e7d32"))
    elements.append(svgkit.text(330, 95, "Селективне трасування", size=11))
    elements.append(svgkit.text(330, 115, "BPF-фільтрація в ядрі", size=10, color="#1b5e20"))

    elements.append(svgkit.rect(255, 140, 150, 40, fill="#c8e6c9", stroke="#43a047", rx=4))
    elements.append(svgkit.text(330, 165, "Дозволені: 0 overhead", size=9))

    elements.append(svgkit.rect(255, 190, 150, 90, fill="#a5d6a7", stroke="#43a047", rx=4))
    elements.append(svgkit.mtext(330, 220, "Перехоплені:\nАсинхронний fd\nЗахист від TOCTOU\nчерез pidfd", size=9))

    # Container 3: eBPF Tracepoints
    elements.append(svgkit.rect(450, 40, 180, 280, fill="#e0f2f1", stroke="#00897b", sw=2, rx=8))
    elements.append(svgkit.text(540, 70, "eBPF tracepoints", bold=True, size=15, color="#00695c"))
    elements.append(svgkit.text(540, 95, "Пасивне спостереження", size=11))
    elements.append(svgkit.text(540, 115, "Без зупинки процесів", size=10, color="#004d40"))

    elements.append(svgkit.rect(465, 140, 150, 40, fill="#b2dfdb", stroke="#00897b", rx=4))
    elements.append(svgkit.text(540, 165, "raw_syscalls/sys_enter", size=9))

    elements.append(svgkit.rect(465, 190, 150, 90, fill="#80cbc4", stroke="#00897b", rx=4))
    elements.append(svgkit.mtext(540, 220, "Виконання в ядрі\nЗапис у Ring Buffer\n0 switches", size=9))

    svgkit.render(str(IMG_DIR / "ptrace-vs-seccomp-perf.svg"), 660, 340, *elements)

def render():
    draw_ptrace_flow()
    draw_seccomp_notif()
    draw_ptrace_vs_seccomp_perf()

if __name__ == "__main__":
    render()
