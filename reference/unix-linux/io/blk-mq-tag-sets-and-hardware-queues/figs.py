import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def blk_mq_arch():
    frags = []
    
    # Outer frame
    frags.append(rect(10, 10, 780, 430, rx=8, fill="#fafafa", stroke="#d0d0d0"))
    b, _, _ = textbox(400, 30, "Дворівнева архітектура черг blk-mq (ctx -> hctx)", size=16, bold=True, fill="#ffffff", stroke="#d0d0d0")
    frags.append(b)
    
    # Software Queues section (ctx)
    frags.append(rect(30, 60, 740, 130, rx=6, fill="#f0f7ff", stroke="#a3c2ec"))
    frags.append(text(50, 80, "Програмні черги per-CPU (blk_mq_ctx)", size=13, bold=True, anchor="start"))
    
    b0, _, _ = textbox(110, 130, "CPU 0\nblk_mq_ctx", size=11, fill="#ffffff", stroke="#3b82f6", rx=4)
    b1, _, _ = textbox(280, 130, "CPU 1\nblk_mq_ctx", size=11, fill="#ffffff", stroke="#3b82f6", rx=4)
    b2, _, _ = textbox(520, 130, "CPU 2\nblk_mq_ctx", size=11, fill="#ffffff", stroke="#3b82f6", rx=4)
    b3, _, _ = textbox(690, 130, "CPU 3\nblk_mq_ctx", size=11, fill="#ffffff", stroke="#3b82f6", rx=4)
    frags.extend([b0, b1, b2, b3])
    
    # Queue Map text label in middle
    frags.append(text(400, 210, "Мапінг через blk_mq_queue_map (N:1 або 1:1)", size=12, bold=True, anchor="middle", color="#475569"))
    
    # Arrows from ctx to hctx
    frags.append(arrow(110, 160, 170, 240, color="#64748b"))
    frags.append(arrow(280, 160, 230, 240, color="#64748b"))
    frags.append(arrow(520, 160, 570, 240, color="#64748b"))
    frags.append(arrow(690, 160, 630, 240, color="#64748b"))
    
    # Hardware Queues section (hctx)
    frags.append(rect(30, 240, 740, 120, rx=6, fill="#f0fdf4", stroke="#86efac"))
    frags.append(text(50, 260, "Апаратні диспетчерські черги (blk_mq_hw_ctx)", size=13, bold=True, anchor="start"))
    
    h0, _, _ = textbox(200, 310, "hctx 0 (Hardware Queue 0)\n[Dispatch List / Scheduler]", size=11, fill="#ffffff", stroke="#22c55e", rx=4)
    h1, _, _ = textbox(600, 310, "hctx 1 (Hardware Queue 1)\n[Dispatch List / Scheduler]", size=11, fill="#ffffff", stroke="#22c55e", rx=4)
    frags.extend([h0, h1])
    
    # Arrows to physical controller
    frags.append(arrow(200, 345, 200, 375, color="#16a34a"))
    frags.append(arrow(600, 345, 600, 375, color="#16a34a"))
    
    # NVMe / Hardware layer
    frags.append(rect(30, 375, 740, 50, rx=6, fill="#fff7ed", stroke="#fdba74"))
    frags.append(text(400, 405, "Фізичний накопичувач (NVMe Submission Queues / PCIe Ring)", size=13, bold=True, anchor="middle"))
    
    return frags

def tag_set_sharing():
    frags = []
    
    frags.append(rect(10, 10, 780, 380, rx=8, fill="#fafafa", stroke="#d0d0d0"))
    b, _, _ = textbox(400, 30, "Структура blk_mq_tag_set та спільні теги пристроїв", size=16, bold=True, fill="#ffffff", stroke="#d0d0d0")
    frags.append(b)
    
    # Tag set box
    frags.append(rect(30, 60, 740, 125, rx=6, fill="#fef3c7", stroke="#f59e0b"))
    frags.append(text(60, 80, "struct blk_mq_tag_set (Host-Wide Tag Pool)", size=13, bold=True, anchor="start"))
    
    t1, _, _ = textbox(150, 125, "queue_depth = 1024\nreserved_tags = 32\nnr_hw_queues = 4", size=10, fill="#ffffff", stroke="#d97706", rx=4)
    t2, _, _ = textbox(400, 125, "sbitmap_queue (Tags bitmap)\n[ 1 1 0 0 1 0 1 1 ... 0 ]", size=10, fill="#ffffff", stroke="#d97706", rx=4)
    t3, _, _ = textbox(640, 125, "ops: queue_rq(), complete()\nmap: CPU -> hctx mapping", size=10, fill="#ffffff", stroke="#d97706", rx=4)
    frags.extend([t1, t2, t3])
    
    # Arrows to devices
    frags.append(arrow(200, 185, 200, 225, color="#d97706"))
    frags.append(arrow(590, 185, 590, 225, color="#d97706"))
    
    # Devices (request_queue)
    frags.append(rect(40, 225, 330, 125, rx=6, fill="#f0f9ff", stroke="#0284c7"))
    frags.append(text(60, 245, "request_queue (/dev/nvme0n1)", size=12, bold=True, anchor="start"))
    d1, _, _ = textbox(205, 295, "Власні ctx та hctx структури\nВикористовує спільний tag_set->tags\nRequest Tag: #42", size=10, fill="#ffffff", stroke="#38bdf8", rx=4)
    
    frags.append(rect(410, 225, 330, 125, rx=6, fill="#f0f9ff", stroke="#0284c7"))
    frags.append(text(430, 245, "request_queue (/dev/nvme0n2)", size=12, bold=True, anchor="start"))
    d2, _, _ = textbox(575, 295, "Власні ctx та hctx структури\nВикористовує спільний tag_set->tags\nRequest Tag: #107", size=10, fill="#ffffff", stroke="#38bdf8", rx=4)
    
    frags.extend([d1, d2])
    return frags

def sbitmap_alloc():
    frags = []
    
    frags.append(rect(10, 10, 780, 410, rx=8, fill="#fafafa", stroke="#d0d0d0"))
    b, _, _ = textbox(400, 30, "Будова sbitmap та sbitmap_queue для аллокації тегів", size=16, bold=True, fill="#ffffff", stroke="#d0d0d0")
    frags.append(b)
    
    # Per-CPU hints
    frags.append(rect(30, 60, 740, 80, rx=6, fill="#f5f3ff", stroke="#8b5cf6"))
    frags.append(text(60, 78, "Per-CPU hints (alloc_hint)", size=12, bold=True, anchor="start"))
    
    c0, _, _ = textbox(110, 105, "CPU 0 Hint:\nWord 0, Bit 4", size=10, fill="#ffffff", stroke="#a78bfa", rx=3)
    c1, _, _ = textbox(300, 105, "CPU 1 Hint:\nWord 0, Bit 19", size=10, fill="#ffffff", stroke="#a78bfa", rx=3)
    c2, _, _ = textbox(490, 105, "CPU 2 Hint:\nWord 1, Bit 2", size=10, fill="#ffffff", stroke="#a78bfa", rx=3)
    c3, _, _ = textbox(670, 105, "CPU 3 Hint:\nWord 1, Bit 30", size=10, fill="#ffffff", stroke="#a78bfa", rx=3)
    frags.extend([c0, c1, c2, c3])
    
    # Arrow to words
    frags.append(arrow(400, 140, 400, 165, color="#7c3aed"))
    
    # Bitmap Words array
    frags.append(rect(30, 165, 740, 110, rx=6, fill="#fef2f2", stroke="#ef4444"))
    frags.append(text(60, 183, "sbitmap_word Array (Розподілена бітова карта)", size=12, bold=True, anchor="start"))
    
    w0, _, _ = textbox(210, 230, "sbitmap_word [0]\ndepth = 64 | word = 0xFF00FFFE\nAtomic Test-and-Set", size=10, fill="#ffffff", stroke="#fca5a5", rx=4)
    w1, _, _ = textbox(580, 230, "sbitmap_word [1]\ndepth = 64 | word = 0x0000000F\nAtomic Test-and-Set", size=10, fill="#ffffff", stroke="#fca5a5", rx=4)
    frags.extend([w0, w1])
    
    # Arrow to waitqueues
    frags.append(arrow(400, 275, 400, 300, color="#dc2626"))
    
    # Wait Queues (sbq_wait)
    frags.append(rect(30, 300, 740, 100, rx=6, fill="#ecfdf5", stroke="#10b981"))
    frags.append(text(60, 318, "sbitmap_queue Wait Queues (sbq_wait_state)", size=12, bold=True, anchor="start"))
    
    q0, _, _ = textbox(150, 360, "Wait Queue 0\n[Thread A sleeping]", size=10, fill="#ffffff", stroke="#6ee7b7", rx=4)
    q1, _, _ = textbox(400, 360, "Wait Queue 1\n[Empty]", size=10, fill="#ffffff", stroke="#6ee7b7", rx=4)
    q2, _, _ = textbox(650, 360, "Wait Queue 2\n[Thread B sleeping]", size=10, fill="#ffffff", stroke="#6ee7b7", rx=4)
    frags.extend([q0, q1, q2])
    
    return frags

def main():
    f1 = blk_mq_arch()
    render(os.path.join(IMG, 'blk-mq-arch.svg'), 800, 450, *f1, title="Архітектура blk-mq")
    
    f2 = tag_set_sharing()
    render(os.path.join(IMG, 'tag-set-sharing.svg'), 800, 400, *f2, title="Спільний blk_mq_tag_set")
    
    f3 = sbitmap_alloc()
    render(os.path.join(IMG, 'sbitmap-alloc.svg'), 800, 430, *f3, title="Будова sbitmap")

if __name__ == "__main__":
    main()
