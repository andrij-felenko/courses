import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_io_uring_arch():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'io-uring-arch.svg')

    w, h = 900, 440
    frags = []

    # Title
    frags.append(text(w / 2, 26, "Архітектура io_uring: Спільна пам'ять та асинхронні черги", size=17, bold=True))

    # 1. User Space Panel
    frags.append(rect(20, 50, 240, 370, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(140, 75, "User Space", size=15, bold=True, color="#1e293b"))
    frags.append(textbox(140, 150, "Додаток користувача\n(liburing / Application)", size=13, pad=10, fill="#e2e8f0", stroke="#475569", bold=True)[0])
    frags.append(textbox(140, 300, "Обробники подій\n(Event Handlers)", size=12, pad=8, fill="#f1f5f9", stroke="#64748b")[0])

    # 2. Shared Memory Panel (Middle)
    frags.append(rect(280, 50, 320, 370, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(440, 75, "Спільна пам'ять (mmap)", size=15, bold=True, color=FIELD))

    # Submission Queue inside Shared Memory
    frags.append(rect(300, 95, 280, 140, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(text(440, 118, "Submission Queue (SQ)", size=13, bold=True, color="#0369a1"))
    frags.append(text(440, 142, "[ SQE 0 ]  [ SQE 1 ]  [ SQE 2 ]", size=11, color="#334155"))
    frags.append(text(440, 170, "Tail (User Write) → Head (Kernel Read)", size=11, italic=True, color="#0284c7"))
    frags.append(text(440, 200, "Запити I/O: op, fd, addr, len, user_data (64 B)", size=10, color=MUTED))

    # Completion Queue inside Shared Memory
    frags.append(rect(300, 255, 280, 140, fill="#ffffff", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(440, 278, "Completion Queue (CQ)", size=13, bold=True, color="#15803d"))
    frags.append(text(440, 302, "[ CQE 0 ]  [ CQE 1 ]  [ CQE 2 ]", size=11, color="#334155"))
    frags.append(text(440, 330, "Head (User Read) ← Tail (Kernel Write)", size=11, italic=True, color="#16a34a"))
    frags.append(text(440, 360, "Результати: user_data, res, flags (16 B)", size=10, color=MUTED))

    # 3. Kernel Space Panel
    frags.append(rect(620, 50, 260, 370, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=8))
    frags.append(text(750, 75, "Kernel Space", size=15, bold=True, color="#0f172a"))

    frags.append(textbox(750, 130, "SQPOLL Thread\n(io_uring-sq)", size=12, pad=8, fill="#fef3c7", stroke="#d97706", bold=True)[0])
    frags.append(textbox(750, 230, "Пул потоків io-wq\n(Async Offload)", size=12, pad=8, fill="#fee2e2", stroke=POS, bold=True)[0])
    frags.append(textbox(750, 330, "VFS / Block Layer / Driver\n(NVMe / SSD / Sockets)", size=12, pad=8, fill="#e0f2fe", stroke=NEG, bold=True)[0])

    # Connectors (horizontal lines between panels)
    # User App -> SQ
    frags.append(arrow(220, 145, 295, 145, color="#0284c7", sw=1.8))
    
    # CQ -> User Handlers
    frags.append(arrow(295, 320, 220, 320, color="#16a34a", sw=1.8))

    # SQ -> Kernel SQPOLL
    frags.append(arrow(585, 145, 680, 130, color="#d97706", sw=1.8))

    # Kernel -> CQ
    frags.append(arrow(680, 330, 585, 330, color="#16a34a", sw=1.8))

    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_io_uring_arch()
