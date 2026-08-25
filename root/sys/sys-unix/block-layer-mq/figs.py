import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

def fig_two_tier_pipeline():
    frags = []
    
    # Layer 1: User Space / CPU cores
    frags.append(rect(20, 50, 760, 75, fill="#f8f9fa", stroke="#d0d7de", rx=8))
    frags.append(text(400, 72, "Прикладний рівень та логічні ядра CPU", bold=True, size=15))
    
    frags.append(rect(40, 85, 210, 32, fill="#e3f2fd", stroke="#1976d2"))
    frags.append(text(145, 106, "Потік A (CPU 0)", size=13))
    
    frags.append(rect(295, 85, 210, 32, fill="#e3f2fd", stroke="#1976d2"))
    frags.append(text(400, 106, "Потік B (CPU 1)", size=13))
    
    frags.append(rect(550, 85, 210, 32, fill="#e3f2fd", stroke="#1976d2"))
    frags.append(text(655, 106, "Потік N (CPU N)", size=13))
    
    # Arrows to Software Queues
    frags.append(arrow(145, 117, 145, 155, color="#555"))
    frags.append(arrow(400, 117, 400, 155, color="#555"))
    frags.append(arrow(655, 117, 655, 155, color="#555"))
    
    # Layer 2: Software Staging Queues (ctx)
    frags.append(rect(20, 155, 760, 95, fill="#fff8e1", stroke="#ffa000", rx=8))
    frags.append(text(400, 175, "Рівень 1: Програмні черги per-CPU (struct blk_mq_ctx)", bold=True, size=14, color="#b78103"))
    
    frags.append(rect(40, 190, 210, 48, fill="#ffffff", stroke="#ffb300"))
    frags.append(text(145, 210, "Software Queue 0", size=12, bold=True))
    frags.append(text(145, 226, "Планувальник / None", size=11, color=MUTED))
    
    frags.append(rect(295, 190, 210, 48, fill="#ffffff", stroke="#ffb300"))
    frags.append(text(400, 210, "Software Queue 1", size=12, bold=True))
    frags.append(text(400, 226, "Планувальник / None", size=11, color=MUTED))
    
    frags.append(rect(550, 190, 210, 48, fill="#ffffff", stroke="#ffb300"))
    frags.append(text(655, 210, "Software Queue N", size=12, bold=True))
    frags.append(text(655, 226, "Планувальник / None", size=11, color=MUTED))
    
    # Mapping lines
    frags.append(line(145, 238, 250, 280, color="#777", dash="4,4"))
    frags.append(line(400, 238, 250, 280, color="#777", dash="4,4"))
    frags.append(line(655, 238, 550, 280, color="#777", dash="4,4"))
    
    # Layer 3: Hardware Dispatch Queues (hctx)
    frags.append(rect(20, 280, 760, 85, fill="#e8f5e9", stroke="#388e3c", rx=8))
    frags.append(text(400, 300, "Рівень 2: Апаратні черги диспетчеризації (struct blk_mq_hw_ctx)", bold=True, size=14, color="#2e7d32"))
    
    frags.append(rect(80, 312, 340, 42, fill="#ffffff", stroke="#4caf50"))
    frags.append(text(250, 330, "Hardware Queue 0 (hctx 0)", size=12, bold=True))
    frags.append(text(250, 345, "sbitmap теги & dispatch list", size=11, color=MUTED))
    
    frags.append(rect(380, 312, 340, 42, fill="#ffffff", stroke="#4caf50"))
    frags.append(text(550, 330, "Hardware Queue M (hctx M)", size=12, bold=True))
    frags.append(text(550, 345, "sbitmap теги & dispatch list", size=11, color=MUTED))
    
    # Arrows to Controller
    frags.append(arrow(250, 354, 250, 395, color="#388e3c", sw=2))
    frags.append(arrow(550, 354, 550, 395, color="#388e3c", sw=2))
    
    # Layer 4: NVMe/SCSI Controller
    frags.append(rect(20, 395, 760, 65, fill="#f3e5f5", stroke="#8e24aa", rx=8))
    frags.append(text(400, 417, "Контролер пристрою зберігання (NVMe / SCSI Host / SATA)", bold=True, size=14, color="#6a1b9a"))
    frags.append(text(400, 440, "Апаратні черги подачі команд (Submission Queues) та завершення (Completion Queues)", size=12, color=MUTED))
    
    return render(os.path.join(IMG, "blk-mq-two-tier-pipeline.svg"), 800, 480, *frags, title="Дворівнева архітектура підсистеми blk-mq")

def fig_bio_request_merge():
    frags = []
    
    # Memory Pages (Top)
    frags.append(rect(30, 50, 740, 65, fill="#f1f8e9", stroke="#7cb342", rx=6))
    frags.append(text(400, 68, "Фізичні сторінки пам'яті (struct page)", bold=True, size=13))
    
    frags.append(rect(50, 78, 150, 28, fill="#ffffff", stroke="#8bc34a"))
    frags.append(text(125, 96, "Page 0 (Sector 100..107)", size=11))
    
    frags.append(rect(220, 78, 150, 28, fill="#ffffff", stroke="#8bc34a"))
    frags.append(text(295, 96, "Page 1 (Sector 108..115)", size=11))
    
    frags.append(rect(430, 78, 150, 28, fill="#ffffff", stroke="#8bc34a"))
    frags.append(text(505, 96, "Page 2 (Sector 116..123)", size=11))
    
    frags.append(rect(600, 78, 150, 28, fill="#ffffff", stroke="#8bc34a"))
    frags.append(text(675, 96, "Page 3 (Sector 124..131)", size=11))
    
    # Arrows to bio
    frags.append(arrow(125, 106, 175, 145, color="#555"))
    frags.append(arrow(295, 106, 215, 145, color="#555"))
    frags.append(arrow(505, 106, 555, 145, color="#555"))
    frags.append(arrow(675, 106, 595, 145, color="#555"))
    
    # Bio layer (Middle)
    frags.append(rect(30, 145, 340, 95, fill="#e3f2fd", stroke="#1e88e5", rx=6))
    frags.append(text(200, 165, "struct bio A", bold=True, size=13, color="#1565c0"))
    frags.append(text(200, 183, "Sector: 100, Size: 16 sectors (8KB)", size=11))
    frags.append(text(200, 201, "bio_vec[0]: Page 0 | bio_vec[1]: Page 1", size=11, color=MUTED))
    frags.append(text(200, 222, "Операція: REQ_OP_WRITE", size=11, bold=True, color="#c0392b"))
    
    frags.append(rect(430, 145, 340, 95, fill="#e3f2fd", stroke="#1e88e5", rx=6))
    frags.append(text(600, 165, "struct bio B (Back Merge)", bold=True, size=13, color="#1565c0"))
    frags.append(text(600, 183, "Sector: 116, Size: 16 sectors (8KB)", size=11))
    frags.append(text(600, 201, "bio_vec[0]: Page 2 | bio_vec[1]: Page 3", size=11, color=MUTED))
    frags.append(text(600, 222, "Суміжний сектор з кінцем bio A", size=11, bold=True, color="#27ae60"))
    
    # Merge action arrow
    frags.append(arrow(200, 240, 320, 270, color="#1e88e5", sw=2))
    frags.append(arrow(600, 240, 480, 270, color="#1e88e5", sw=2))
    
    # Request layer (Bottom)
    frags.append(rect(30, 270, 740, 115, fill="#fff3e0", stroke="#f57c00", rx=6))
    frags.append(text(400, 292, "Контейнер запиту в ядрі (struct request)", bold=True, size=14, color="#e65100"))
    frags.append(text(400, 312, "Сектор: 100..131 (Загальний розмір: 32 сектори / 16KB) | HW Tag: #42", size=12, bold=True))
    
    frags.append(rect(60, 325, 320, 45, fill="#ffffff", stroke="#ff9800"))
    frags.append(text(220, 344, "Голова: struct bio A", size=12, bold=True))
    frags.append(text(220, 360, "bi_next -> bio B", size=11, color=MUTED))
    
    frags.append(arrow(380, 347, 420, 347, color="#f57c00", sw=2))
    
    frags.append(rect(420, 325, 320, 45, fill="#ffffff", stroke="#ff9800"))
    frags.append(text(580, 344, "Хвіст: struct bio B", size=12, bold=True))
    frags.append(text(580, 360, "Об'єднано через I/O Back Merge", size=11, color="#27ae60"))
    
    return render(os.path.join(IMG, "bio-request-merge.svg"), 800, 410, *frags, title="Анатомія bio, bio_vec та механізм злиття I/O (Back Merge)")

def fig_plug_unplug_batching():
    frags = []
    
    # Phase 1: Thread Plug
    frags.append(rect(20, 50, 230, 300, fill="#f5f5f5", stroke="#bdbdbd", rx=8))
    frags.append(text(135, 75, "1. Створення Plug", bold=True, size=14))
    frags.append(text(135, 95, "blk_start_plug(&plug)", size=11, color=MUTED))
    
    frags.append(rect(35, 115, 200, 160, fill="#e8eaf6", stroke="#3f51b5", rx=6))
    frags.append(text(135, 135, "Стек struct blk_plug", bold=True, size=12, color="#1a237e"))
    frags.append(rect(45, 148, 180, 28, fill="#ffffff", stroke="#7986cb"))
    frags.append(text(135, 166, "Request 1 (Sector 0..7)", size=11))
    frags.append(rect(45, 182, 180, 28, fill="#ffffff", stroke="#7986cb"))
    frags.append(text(135, 200, "Request 2 (Sector 8..23)", size=11))
    frags.append(rect(45, 216, 180, 28, fill="#ffffff", stroke="#7986cb"))
    frags.append(text(135, 234, "Request 3 (Sector 24..31)", size=11))
    frags.append(text(135, 262, "Злиття локально (No locks)", size=11, bold=True, color="#27ae60"))
    
    # Arrow 1 -> 2
    frags.append(arrow(250, 200, 285, 200, color="#1a237e", sw=2))
    
    # Phase 2: Batch Unplug
    frags.append(rect(285, 50, 230, 300, fill="#fff8e1", stroke="#ffe082", rx=8))
    frags.append(text(400, 75, "2. Виштовхування Unplug", bold=True, size=14))
    frags.append(text(400, 95, "blk_finish_plug(&plug)", size=11, color=MUTED))
    
    frags.append(rect(300, 125, 200, 140, fill="#ffffff", stroke="#ffb300", rx=6))
    frags.append(text(400, 150, "Пакетна передача", bold=True, size=13, color="#f57f17"))
    frags.append(text(400, 175, "Всі 3 запити передаються", size=11))
    frags.append(text(400, 192, "одним викликом", size=11))
    frags.append(text(400, 220, "Захист від spinlock storm", size=11, bold=True, color="#c0392b"))
    
    # Arrow 2 -> 3
    frags.append(arrow(515, 200, 550, 200, color="#f57f17", sw=2))
    
    # Phase 3: Software Queue (ctx)
    frags.append(rect(550, 50, 230, 300, fill="#e8f5e9", stroke="#a5d6a7", rx=8))
    frags.append(text(665, 75, "3. blk-mq Queues", bold=True, size=14))
    frags.append(text(665, 95, "Software Queue per-CPU", size=11, color=MUTED))
    
    frags.append(rect(565, 125, 200, 140, fill="#ffffff", stroke="#4caf50", rx=6))
    frags.append(text(665, 150, "blk_mq_ctx (CPU 0)", bold=True, size=13, color="#2e7d32"))
    frags.append(text(665, 175, "Вставка в планирувальник", size=11))
    frags.append(text(665, 192, "або пряма відправка v hctx", size=11))
    frags.append(text(665, 220, "Швидкий flush батчу", size=11, bold=True, color="#27ae60"))
    
    return render(os.path.join(IMG, "plug-unplug-batching.svg"), 800, 370, *frags, title="Механізм накопичення й пакетної відправки (Plugging / Unplugging)")

def main():
    fig_two_tier_pipeline()
    fig_bio_request_merge()
    fig_plug_unplug_batching()
    print("Figures generated successfully.")

if __name__ == "__main__":
    main()
