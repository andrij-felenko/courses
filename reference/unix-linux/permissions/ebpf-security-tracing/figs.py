import sys
import os

# Four levels up to scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import rect, text, arrow, render, line, mtext, fitbox, textbox, INK, FILL, MUTED, POS, NEG, FIELD

def draw_ringbuf_tracing():
    frags = []
    
    # Background panel for Userspace
    frags.append(rect(20, 20, 760, 100, fill="#f8f9fa", stroke="#ced4da", rx=8))
    frags.append(text(35, 45, "Простір користувача (Userspace)", size=13, bold=True, color="#495057", anchor="start"))
    
    # Userspace daemon box
    frags.append(rect(460, 40, 290, 65, fill="#e8f4f8", stroke="#2b6cb0", rx=6))
    frags.append(text(605, 65, "Аналітичний демон аудиту", size=13, bold=True, color="#1a365d"))
    frags.append(text(605, 87, "epoll_wait() → ring_buffer__poll()", size=11, color="#2b6cb0"))

    # Shared Memory Ring Buffer
    frags.append(rect(140, 140, 520, 70, fill="#e6fffa", stroke="#319795", rx=6))
    frags.append(text(400, 165, "Спільна пам'ять: BPF Ring Buffer (mmap)", size=13, bold=True, color="#234e52"))
    frags.append(text(400, 190, "bpf_ringbuf_reserve() → bpf_ringbuf_submit()", size=11, color="#2c7a7b"))

    # Background panel for Kernel Space
    frags.append(rect(20, 230, 760, 150, fill="#fff5f5", stroke="#feb2b2", rx=8))
    frags.append(text(35, 255, "Ядро Linux (Kernel Space)", size=13, bold=True, color="#9b2c2c", anchor="start"))
    
    # Event triggers / Probes
    frags.append(rect(40, 275, 210, 85, fill="#ffffff", stroke="#e53e3e", rx=6))
    frags.append(text(145, 298, "Джерела подій безпеки", size=12, bold=True, color="#9b2c2c"))
    frags.append(text(145, 320, "kprobes / tracepoints / fentry", size=11, color="#742a2a"))
    frags.append(text(145, 340, "sys_enter_execve, commit_creds", size=10, color=MUTED))

    # BPF Program Execution
    frags.append(rect(300, 275, 220, 85, fill="#ffffff", stroke="#dd6b20", rx=6))
    frags.append(text(410, 298, "BPF Program (JIT)", size=12, bold=True, color="#9c4221"))
    frags.append(text(410, 320, "Збір контексту (PID, UID, comm)", size=11, color="#7b341e"))
    frags.append(text(410, 340, "bpf_probe_read_user_str()", size=10, color=MUTED))

    # Kernel Hook / Event origin
    frags.append(rect(560, 275, 200, 85, fill="#ffffff", stroke="#3182ce", rx=6))
    frags.append(text(660, 298, "Подія ядра / Syscall", size=12, bold=True, color="#2b6cb0"))
    frags.append(text(660, 320, "Виконання процесу /", size=11, color="#2c5282"))
    frags.append(text(660, 340, "Зміна привілеїв", size=11, color="#2c5282"))

    # Arrows
    # Trigger to BPF program
    frags.append(arrow(560, 317, 520, 317))
    frags.append(arrow(250, 317, 300, 317))
    # BPF program to Ring Buffer
    frags.append(arrow(410, 275, 410, 210))
    # Ring Buffer to Userspace daemon
    frags.append(arrow(605, 140, 605, 105))

    return frags

def draw_falco_vs_tetragon():
    frags = []
    
    # Left Box: Falco (Async Detection)
    frags.append(rect(20, 20, 360, 350, fill="#f7fafc", stroke="#cbd5e0", rx=8))
    frags.append(text(200, 50, "Falco: Асинхронний аудит", size=14, bold=True, color="#2d3748"))
    
    frags.append(rect(50, 80, 300, 55, fill="#ffffff", stroke="#4a5568", rx=5))
    frags.append(text(200, 102, "Системний виклик (Syscall)", size=12, bold=True))
    frags.append(text(200, 122, "Виконання в ядрі без затримок", size=10, color=MUTED))
    
    frags.append(rect(50, 160, 300, 55, fill="#edf2f7", stroke="#4a5568", rx=5))
    frags.append(text(200, 182, "Tracepoint / raw_tracepoint", size=12, bold=True))
    frags.append(text(200, 202, "Запис події у Ring Buffer", size=10, color=MUTED))
    
    frags.append(rect(50, 240, 300, 55, fill="#ebf8ff", stroke="#3182ce", rx=5))
    frags.append(text(200, 262, "Falco Engine (Userspace)", size=12, bold=True, color="#2b6cb0"))
    frags.append(text(200, 282, "Аналіз правил та сповіщення (Alert)", size=10, color="#2c5282"))
    
    frags.append(text(200, 335, "Режим: Детекція після події", size=11, bold=True, color="#c53030"))

    # Right Box: Tetragon (Sync Enforcement)
    frags.append(rect(420, 20, 360, 350, fill="#f7fafc", stroke="#cbd5e0", rx=8))
    frags.append(text(600, 50, "Tetragon: Синхронний контроль", size=14, bold=True, color="#2d3748"))
    
    frags.append(rect(450, 80, 300, 55, fill="#ffffff", stroke="#4a5568", rx=5))
    frags.append(text(600, 102, "Системний виклик / Операція VFS", size=12, bold=True))
    frags.append(text(600, 122, "Запит на виконання дії", size=10, color=MUTED))
    
    frags.append(rect(450, 160, 300, 55, fill="#feebc8", stroke="#dd6b20", rx=5))
    frags.append(text(600, 182, "BPF LSM Hook / fentry", size=12, bold=True, color="#9c4221"))
    frags.append(text(600, 202, "Перевірка політики прямо в ядрі", size=10, color="#7b341e"))
    
    frags.append(rect(450, 240, 300, 55, fill="#fff5f5", stroke="#e53e3e", rx=5))
    frags.append(text(600, 262, "Синхронна дія (In-kernel Action)", size=12, bold=True, color="#9b2c2c"))
    frags.append(text(600, 282, "Блокування -EPERM / SIGKILL", size=10, color="#742a2a"))
    
    frags.append(text(600, 335, "Режим: Блокування у реальному часі", size=11, bold=True, color="#22543d"))

    # Arrows Left
    frags.append(arrow(200, 135, 200, 160))
    frags.append(arrow(200, 215, 200, 240))

    # Arrows Right
    frags.append(arrow(600, 135, 600, 160))
    frags.append(arrow(600, 215, 600, 240))

    return frags

def main():
    topic_dir = os.path.dirname(__file__)
    img_dir = os.path.join(topic_dir, 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    frags1 = draw_ringbuf_tracing()
    render(os.path.join(img_dir, 'ebpf-ringbuf-tracing.svg'), 800, 400, *frags1)
    
    frags2 = draw_falco_vs_tetragon()
    render(os.path.join(img_dir, 'ebpf-security-tools-comparison.svg'), 800, 390, *frags2)
    print("Figures generated successfully.")

if __name__ == '__main__':
    main()
