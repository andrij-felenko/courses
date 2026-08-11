import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[4] / "scripts"))
import svgkit

def draw_ptrace_flow():
    elements = []
    
    # Tracer
    elements.append(svgkit.rect(50, 50, 150, 300, fill="#e1f5fe", stroke="#0288d1", rx=10))
    elements.append(svgkit.text(125, 80, "Tracer", bold=True))
    
    # Tracee
    elements.append(svgkit.rect(400, 50, 150, 300, fill="#f3e5f5", stroke="#7b1fa2", rx=10))
    elements.append(svgkit.text(475, 80, "Tracee", bold=True))
    
    # Kernel
    elements.append(svgkit.rect(250, 100, 100, 200, fill="#fff3e0", stroke="#e65100", rx=10))
    elements.append(svgkit.mtext(300, 130, "Kernel\n(syscall)", bold=True))

    # Flow lines
    elements.append(svgkit.arrow(475, 100, 350, 150))
    elements.append(svgkit.text(400, 115, "sys_enter", size=12))
    
    elements.append(svgkit.arrow(250, 150, 200, 150))
    elements.append(svgkit.text(225, 140, "SIGTRAP", size=12))
    
    elements.append(svgkit.arrow(200, 200, 250, 200))
    elements.append(svgkit.text(225, 190, "PTRACE_SYSCALL", size=12))

    elements.append(svgkit.arrow(300, 200, 300, 250))
    
    elements.append(svgkit.arrow(350, 250, 475, 300))
    elements.append(svgkit.text(400, 290, "sys_exit", size=12))

    elements.append(svgkit.arrow(250, 250, 200, 250))
    elements.append(svgkit.text(225, 240, "SIGTRAP", size=12))

    svgkit.render(os.path.join(IMG, 'ptrace-flow.svg'), 600, 400, *elements)

def draw_seccomp_notif():
    elements = []
    
    # Supervisor
    elements.append(svgkit.rect(50, 50, 150, 300, fill="#e8f5e9", stroke="#388e3c", rx=10))
    elements.append(svgkit.text(125, 80, "Supervisor", bold=True))
    
    # Process
    elements.append(svgkit.rect(400, 50, 150, 300, fill="#ffebee", stroke="#d32f2f", rx=10))
    elements.append(svgkit.mtext(475, 80, "Target\nProcess", bold=True))
    
    # Kernel / Seccomp
    elements.append(svgkit.rect(225, 150, 150, 100, fill="#eceff1", stroke="#455a64", rx=10))
    elements.append(svgkit.mtext(300, 180, "Kernel\n(seccomp BPF)", bold=True))

    elements.append(svgkit.arrow(400, 180, 375, 180))
    elements.append(svgkit.text(387, 170, "syscall", size=12))

    elements.append(svgkit.arrow(225, 180, 200, 180))
    elements.append(svgkit.mtext(212, 170, "FD\n(req)", size=12))

    elements.append(svgkit.arrow(200, 220, 225, 220))
    elements.append(svgkit.mtext(212, 210, "FD\n(resp)", size=12))
    
    elements.append(svgkit.arrow(375, 220, 400, 220))
    elements.append(svgkit.text(387, 210, "return", size=12))

    svgkit.render(os.path.join(IMG, 'seccomp-notif.svg'), 600, 400, *elements)

def render():
    draw_ptrace_flow()
    draw_seccomp_notif()

if __name__ == "__main__":
    render()
