import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

import svgkit

def generate_arch_fig(img_dir):
    """Фігура 1: Порівняння класичного копіювання та io_uring SendZC/RecvZC."""
    w, h = 820, 420
    frags = []
    
    # Ліва панель (Класичний ввід-вивід)
    frags.append(svgkit.rect(20, 50, 380, 340, fill="#fdfefe", stroke="#b0bec5", sw=1.5, rx=8))
    frags.append(svgkit.text(210, 75, "Класичний ввід-вивід (send/recv)", size=15, bold=True, color="#2c3e50"))
    
    frags.append(svgkit.fitbox(40, 100, 340, 45, "Userspace Buffer (Пам'ять програми)", fill="#e3f2fd", stroke="#1e88e5", bold=True))
    frags.append(svgkit.arrow(140, 145, 140, 180, color="#d32f2f", sw=2))
    frags.append(svgkit.text(150, 165, "memcpy() CPU", size=11, color="#d32f2f", anchor="left", bold=True))
    
    frags.append(svgkit.fitbox(40, 180, 340, 45, "Kernel Space Socket Buffer (sk_buff)", fill="#fff3e0", stroke="#fb8c00", bold=True))
    frags.append(svgkit.arrow(140, 225, 140, 260, color="#2e7d32", sw=2))
    frags.append(svgkit.text(150, 245, "DMA передача", size=11, color="#2e7d32", anchor="left"))
    
    frags.append(svgkit.fitbox(40, 260, 340, 45, "Мережевий контролер (NIC TX Ring)", fill="#e8f5e9", stroke="#43a047", bold=True))
    frags.append(svgkit.fitbox(40, 330, 340, 40, "Недолік: CPU забруднює L1/L3 кеш копіюванням", fill="#ffebee", stroke="#e53935", size=11, color="#c62828"))

    # Права панель (io_uring SendZC)
    frags.append(svgkit.rect(420, 50, 380, 340, fill="#fdfefe", stroke="#b0bec5", sw=1.5, rx=8))
    frags.append(svgkit.text(610, 75, "io_uring SendZC / RecvZC", size=15, bold=True, color="#2c3e50"))
    
    frags.append(svgkit.fitbox(440, 100, 340, 45, "Зареєстрований буфер (Fixed Buffer)", fill="#e3f2fd", stroke="#1e88e5", bold=True))
    frags.append(svgkit.arrow(520, 145, 520, 260, color="#2e7d32", sw=2.2))
    frags.append(svgkit.text(535, 195, "Прямий DMA (Zero-Copy)", size=12, color="#2e7d32", anchor="left", bold=True))
    frags.append(svgkit.text(535, 215, "без memcpy у ядро", size=11, color="#555555", anchor="left"))
    
    frags.append(svgkit.fitbox(440, 180, 340, 45, "sk_buff (лише вказівники pfn/page)", fill="#fff8e1", stroke="#ffa000", bold=True))
    frags.append(svgkit.fitbox(440, 260, 340, 45, "Мережевий контролер (NIC TX Ring)", fill="#e8f5e9", stroke="#43a047", bold=True))
    frags.append(svgkit.fitbox(440, 330, 340, 40, "Перевага: 0 копіювань, сповіщення через CQE", fill="#e8f5e9", stroke="#2e7d32", size=11, color="#1b5e20"))

    path = os.path.join(img_dir, "io-uring-zc-arch.svg")
    svgkit.render(path, w, h, *frags, title="Архітектура мережевого вводу-виводу: memcpy проти SendZC")

def generate_twophase_fig(img_dir):
    """Фігура 2: Двофазне завершення SendZC (Two-Phase Completion)."""
    w, h = 800, 380
    frags = []

    # Вертикальні лінії часової шкали
    frags.append(svgkit.line(160, 80, 160, 330, color="#1976d2", sw=2))
    frags.append(svgkit.text(160, 65, "Застосунок (Userspace)", size=13, bold=True, color="#1976d2"))

    frags.append(svgkit.line(400, 80, 400, 330, color="#f57c00", sw=2))
    frags.append(svgkit.text(400, 65, "Підсистема io_uring", size=13, bold=True, color="#f57c00"))

    frags.append(svgkit.line(640, 80, 640, 330, color="#388e3c", sw=2))
    frags.append(svgkit.text(640, 65, "Драйвер & NIC DMA", size=13, bold=True, color="#388e3c"))

    # Крок 1: SQE submit
    frags.append(svgkit.arrow(160, 110, 400, 110, color="#1976d2", sw=1.8))
    frags.append(svgkit.text(280, 100, "SQE: IORING_OP_SEND_ZC", size=11, bold=True))

    # Крок 2: Kernel queues skb
    frags.append(svgkit.arrow(400, 135, 640, 135, color="#f57c00", sw=1.8))
    frags.append(svgkit.text(520, 125, "skb -> NIC TX Ring", size=11))

    # Крок 3: Перший CQE (completion)
    frags.append(svgkit.arrow(400, 175, 160, 175, color="#f57c00", sw=1.8))
    frags.append(svgkit.text(280, 165, "1st CQE: bytes sent (IORING_CQE_F_MORE)", size=10, color="#c62828", bold=True))
    frags.append(svgkit.fitbox(10, 195, 140, 42, "Буфер ЗАБЛОКОВАНО!\nНе перезаписувати", size=9, fill="#fffde7", stroke="#fbc02d"))

    # Крок 4: NIC sends packet
    frags.append(svgkit.arrow(640, 255, 400, 255, color="#388e3c", sw=1.8))
    frags.append(svgkit.text(520, 245, "TX IRQ: Packet Sent / ACKed", size=11))

    # Крок 5: Notification CQE
    frags.append(svgkit.arrow(400, 295, 160, 295, color="#2e7d32", sw=2))
    frags.append(svgkit.text(280, 285, "2nd CQE: Notification (IORING_CQE_F_NOTIF)", size=10, color="#2e7d32", bold=True))
    frags.append(svgkit.fitbox(10, 305, 140, 42, "Буфер ЗВІЛЬНЕНО\nможна перевикористати", size=9, fill="#e8f5e9", stroke="#388e3c"))

    path = os.path.join(img_dir, "io-uring-sendzc-two-phase.svg")
    svgkit.render(path, w, h, *frags, title="Життєвий цикл двофазного завершення SendZC")

def generate_pbuf_fig(img_dir):
    """Фігура 3: Provided Buffer Ring та Multishot Receive."""
    w, h = 820, 360
    frags = []

    # App Ring
    frags.append(svgkit.rect(30, 60, 240, 260, fill="#f4f6f8", stroke="#1565c0", sw=1.5, rx=8))
    frags.append(svgkit.text(150, 85, "Застосунок", size=14, bold=True, color="#1565c0"))
    frags.append(svgkit.fitbox(45, 110, 210, 40, "PBUF Ring Allocator", fill="#e3f2fd", stroke="#1e88e5"))
    frags.append(svgkit.fitbox(45, 165, 210, 40, "Pool of Buffers (buf_id 0..N)", fill="#bbdefb", stroke="#1565c0"))
    frags.append(svgkit.fitbox(45, 230, 210, 60, "Обробка CQE даних\nбез копіювання заголовка", fill="#ffffff", stroke="#90caf9", size=11))

    # Shared Memory Ring
    frags.append(svgkit.rect(290, 60, 240, 260, fill="#fffde7", stroke="#f57f17", sw=1.5, rx=8))
    frags.append(svgkit.text(410, 85, "PBUF Ring (Shared Memory)", size=13, bold=True, color="#f57f17"))
    frags.append(svgkit.fitbox(305, 110, 210, 35, "io_uring_buf [id=0, addr, len]", fill="#fff9c4", stroke="#fbc02d", size=10))
    frags.append(svgkit.fitbox(305, 155, 210, 35, "io_uring_buf [id=1, addr, len]", fill="#fff9c4", stroke="#fbc02d", size=10))
    frags.append(svgkit.fitbox(305, 200, 210, 35, "io_uring_buf [id=2, addr, len]", fill="#fff9c4", stroke="#fbc02d", size=10))
    frags.append(svgkit.text(410, 260, "Tail updated by User", size=11, color="#e65100"))
    frags.append(svgkit.text(410, 285, "Head updated by Kernel", size=11, color="#e65100"))

    # Kernel Recv
    frags.append(svgkit.rect(550, 60, 240, 260, fill="#f1f8e9", stroke="#2e7d32", sw=1.5, rx=8))
    frags.append(svgkit.text(670, 85, "Ядро Linux (Multishot Recv)", size=13, bold=True, color="#2e7d32"))
    frags.append(svgkit.fitbox(565, 110, 210, 45, "1 SQE: RECV_MULTISHOT", fill="#c8e6c9", stroke="#43a047", bold=True))
    frags.append(svgkit.arrow(670, 160, 670, 190, color="#2e7d32", sw=1.8))
    frags.append(svgkit.fitbox(565, 190, 210, 45, "Пакет з мережі -> Бере buf_id", fill="#a5d6a7", stroke="#2e7d32"))
    frags.append(svgkit.arrow(565, 212, 515, 212, color="#2e7d32", sw=1.8))
    frags.append(svgkit.fitbox(565, 255, 210, 45, "Генерує CQE з flags=buf_id", fill="#dcedc8", stroke="#558b2f", size=11))

    # Cross arrows
    frags.append(svgkit.arrow(255, 130, 290, 130, color="#1565c0", sw=1.5))
    frags.append(svgkit.arrow(550, 277, 270, 277, color="#2e7d32", sw=1.8))

    path = os.path.join(img_dir, "io-uring-recvzc-pbuf.svg")
    svgkit.render(path, w, h, *frags, title="Механізм Provided Buffers та Multishot Receive в io_uring")

def main():
    img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "img"))
    os.makedirs(img_dir, exist_ok=True)
    generate_arch_fig(img_dir)
    generate_twophase_fig(img_dir)
    generate_pbuf_fig(img_dir)
    print("Figures generated successfully in", img_dir)

if __name__ == "__main__":
    main()
