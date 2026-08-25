import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_bpf_lsm_arch():
    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'bpf-lsm-arch.svg')
    
    frags = []
    
    # 1. User Space Block (top)
    frags.append(rect(30, 40, 740, 95, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(50, 60, "User Space (Простір користувача)", size=13, bold=True, color="#334155", anchor="start"))
    
    # User space components
    b1, _, _ = textbox(160, 95, "Завантажувач BPF\n(libbpf / C / C++)", size=11, pad=10, fill="#e2e8f0", stroke="#64748b", sw=1.2)
    b2, _, _ = textbox(370, 95, "Демон аудиту\n(Ring Buffer Consumer)", size=11, pad=10, fill="#e2e8f0", stroke="#64748b", sw=1.2)
    b3, _, _ = textbox(590, 95, "Утиліти / BTF\n(bpftool / vmlinux.h)", size=11, pad=10, fill="#e2e8f0", stroke="#64748b", sw=1.2)
    frags.extend([b1, b2, b3])
    
    # Boundary line (Syscall interface bpf())
    frags.append(line(30, 160, 770, 160, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(text(760, 150, "Межа системних викликів: bpf() / LSM Hooks", size=11, color="#64748b", anchor="end", italic=True))
    
    # 2. Kernel Space Block (bottom)
    frags.append(rect(30, 180, 740, 210, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(50, 202, "Kernel Space (Ядро Linux)", size=13, bold=True, color="#0f172a", anchor="start"))
    
    # Kernel workflow nodes
    k1, _, _ = textbox(115, 255, "Системний виклик\n(execve / openat)", size=11, pad=10, fill="#ffffff", stroke="#475569", sw=1.2)
    k2, _, _ = textbox(270, 255, "LSM Hook\n(security_bprm_check)", size=11, pad=10, fill="#dbeafe", stroke="#2563eb", sw=1.5, bold=True)
    k3, _, _ = textbox(490, 255, "eBPF LSM Program\n(JIT bytecode / CO-RE)", size=11, pad=12, fill="#dcfce7", stroke="#16a34a", sw=1.5, bold=True)
    k4, _, _ = textbox(695, 255, "Рішення BPF\n0 (Allow) / -EPERM", size=11, pad=10, fill="#fef3c7", stroke="#d97706", sw=1.2)
    frags.extend([k1, k2, k3, k4])
    
    # Supporting kernel structures
    k_verifier, _, _ = textbox(340, 345, "BPF Verifier\n(Перевірка безпеки пам'яті)", size=10, pad=8, fill="#ffffff", stroke="#94a3b8")
    k_buf, _, _ = textbox(570, 345, "Ring Buffer / BPF Maps\n(Телеметрія та стан політик)", size=10, pad=8, fill="#ffffff", stroke="#94a3b8")
    frags.extend([k_verifier, k_buf])
    
    # Arrows (clean paths without crossing boxes)
    frags.append(arrow(160, 120, 240, 230, color="#2563eb", sw=1.5)) # Attach program
    frags.append(arrow(165, 255, 205, 255, color="#475569", sw=1.5)) # Syscall -> LSM Hook
    frags.append(arrow(335, 255, 410, 255, color="#2563eb", sw=1.5)) # LSM Hook -> BPF Program
    frags.append(arrow(570, 255, 635, 255, color="#16a34a", sw=1.5)) # BPF Program -> Decision
    frags.append(arrow(490, 285, 340, 325, color="#64748b", sw=1.2)) # Verifier check
    frags.append(arrow(490, 285, 570, 325, color="#16a34a", sw=1.2)) # Ring buffer push
    frags.append(arrow(620, 325, 450, 120, color="#0284c7", sw=1.2)) # Ring buffer consume up right side
    
    render(out_path, 800, 410, *frags, title="Архітектура BPF-LSM та потік виконання політик безпеки")

if __name__ == '__main__':
    build_bpf_lsm_arch()
