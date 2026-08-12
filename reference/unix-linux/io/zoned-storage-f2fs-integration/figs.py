import sys
import os

# Import svgkit from scripts/ (4 levels up)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import (
    render, textbox, fitbox, rect, line, arrow, text, mtext,
    FILL, LINE, INK, MUTED, POS, NEG, FIELD, BG
)

def build_fig1(img_dir):
    path = os.path.join(img_dir, "conventional-vs-zns.svg")
    w, h = 760, 360

    frags = []
    # Section backgrounds
    frags.append(rect(10, 40, 365, 305, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(rect(385, 40, 365, 305, fill="#f0fdf4", stroke="#bbf7d0", sw=1.5, rx=8))

    # Titles for left & right halves
    frags.append(text(192, 65, "Традиційний SSD (FTL в прошивці)", size=14, color=INK, bold=True))
    frags.append(text(567, 65, "Зонований SSD (NVMe ZNS + F2FS)", size=14, color=POS, bold=True))

    # Left path (Conventional)
    tb1, _, _ = textbox(192, 105, "Прикладна програма (VFS / Write)", size=12, pad=6, fill="#ffffff", stroke="#94a3b8")
    tb2, _, _ = textbox(192, 160, "Файлова система (Перезапис на місці)", size=12, pad=6, fill="#ffffff", stroke="#94a3b8")
    tb3, _, _ = textbox(192, 225, "Контролер SSD (Прихований FTL)\nGarbage Collection + Wear Leveling", size=12, pad=8, fill="#fee2e2", stroke=POS, color=POS, bold=True)
    tb4, _, _ = textbox(192, 295, "NAND Flash (Випадковий запис)", size=12, pad=6, fill="#ffffff", stroke="#94a3b8")

    frags.extend([tb1, tb2, tb3, tb4])
    frags.append(arrow(192, 120, 192, 145))
    frags.append(arrow(192, 175, 192, 205))
    frags.append(arrow(192, 245, 192, 280))

    # Left note
    frags.append(text(192, 335, "Високий WAF, неочікувані затримки GC", size=11, color=POS, italic=True))

    # Right path (ZNS)
    tb5, _, _ = textbox(567, 105, "Прикладна програма (VFS / Write)", size=12, pad=6, fill="#ffffff", stroke="#86efac")
    tb6, _, _ = textbox(567, 165, "f2fs у LFS-режимі\n(Хостовий GC + Zone Management)", size=12, pad=8, fill="#dcfce7", stroke=FIELD, color=INK, bold=True)
    tb7, _, _ = textbox(567, 230, "Блочний шар (Zone Append / Reset)", size=12, pad=6, fill="#ffffff", stroke="#86efac")
    tb8, _, _ = textbox(567, 295, "NVMe ZNS накопичувач (Послідовні зони)", size=12, pad=6, fill="#dbeafe", stroke=NEG, color=NEG, bold=True)

    frags.extend([tb5, tb6, tb7, tb8])
    frags.append(arrow(567, 120, 567, 145))
    frags.append(arrow(567, 185, 567, 215))
    frags.append(arrow(567, 245, 567, 280))

    # Right note
    frags.append(text(567, 335, "Хостовий контроль GC, WAF ≈ 1.0, стабільний IOPS", size=11, color=FIELD, italic=True))

    render(path, w, h, *frags, title="Порівняння традиційного SSD та ZNS з F2FS")

def build_fig2(img_dir):
    path = os.path.join(img_dir, "zone-append-mechanics.svg")
    w, h = 760, 320

    frags = []
    # Background boxes
    frags.append(rect(10, 45, 740, 120, fill="#fff1f2", stroke="#fecdd3", sw=1.5, rx=8))
    frags.append(rect(10, 180, 740, 125, fill="#f0fdf4", stroke="#bbf7d0", sw=1.5, rx=8))

    # Top Section: Standard Write Conflict
    frags.append(text(380, 68, "1. Ззвичайний запис (NVMe Write): Конфлікт покажчика запису (Write Pointer Race)", size=13, color=POS, bold=True))

    tb_th1, _, _ = textbox(130, 110, "Потік A: Write(LBA=100)", size=11, pad=6, fill="#ffffff", stroke=POS)
    tb_th2, _, _ = textbox(130, 142, "Потік B: Write(LBA=100)", size=11, pad=6, fill="#ffffff", stroke=POS)
    frags.extend([tb_th1, tb_th2])

    frags.append(arrow(215, 110, 310, 120))
    frags.append(arrow(215, 142, 310, 126))

    tb_zp1, _, _ = textbox(440, 123, "Контролер ZNS:\nWP вже просунувся! Помилка запису", size=11, pad=8, fill="#fee2e2", stroke=POS, color=POS, bold=True)
    frags.append(tb_zp1)

    frags.append(arrow(545, 123, 620, 123))
    tb_res1, _, _ = textbox(675, 123, "NVME_SC_INVALID_WP\n(Вимога блокування)", size=10, pad=6, fill="#ffffff", stroke=POS)
    frags.append(tb_res1)

    # Bottom Section: Zone Append
    frags.append(text(380, 203, "2. Команда Zone Append: Атомарне чергування контролером ZNS", size=13, color=FIELD, bold=True))

    tb_th3, _, _ = textbox(130, 242, "Потік A: Zone_Append(ZoneStart)\nПотік B: Zone_Append(ZoneStart)", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(tb_th3)

    frags.append(arrow(235, 242, 310, 242))

    tb_zp2, _, _ = textbox(440, 242, "Контролер ZNS (Атомарно в апаратурі):\nЗапис A на LBA 100 → Запис B на LBA 101", size=11, pad=8, fill="#dcfce7", stroke=FIELD, color=INK, bold=True)
    frags.append(tb_zp2)

    frags.append(arrow(560, 242, 615, 242))
    tb_res2, _, _ = textbox(675, 242, "Повернення CQE:\nLBA 100 та LBA 101\n(без локів хоста)", size=10, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(tb_res2)

    render(path, w, h, *frags, title="Механізм Zone Append проти звичайного запису")

def build_fig3(img_dir):
    path = os.path.join(img_dir, "f2fs-gc-zone-reset.svg")
    w, h = 820, 280

    frags = []

    # 4 Steps left to right with wide spacing
    steps = [
        ("1. Зона-жертва", "Зона містить застарілі\nта дійсні блоки", "#fff7ed", "#fdba74"),
        ("2. Міграція GC", "Дійсні блоки читаються\nй пишуться в відкриту зону", "#eff6ff", "#93c5fd"),
        ("3. BLKRESETZONE", "f2fs надсилає команду\nZone Reset в ZNS", "#fef2f2", "#fca5a5"),
        ("4. Чиста зона", "Write Pointer = 0\nЗона готова до запису", "#f0fdf4", "#86efac"),
    ]

    x_positions = [105, 305, 505, 705]

    for i, (title, desc, fill_col, stroke_col) in enumerate(steps):
        cx = x_positions[i]
        # Step card (outer box)
        card = rect(cx - 70, 55, 140, 180, fill=fill_col, stroke=stroke_col, sw=1.5, rx=8)
        frags.append(card)
        frags.append(text(cx, 90, title, size=12, color=INK, bold=True))
        # Plain text without inner rect
        frags.append(mtext(cx, 145, desc, size=11, color=INK, anchor="middle", lh=1.3))

        # Arrow to next step
        if i < 3:
            frags.append(arrow(cx + 72, 145, x_positions[i+1] - 72, 145, sw=1.8))

    frags.append(text(410, 255, "Цикл вивільнення зони хостом позбавляє накопичувач фонового FTL GC", size=11, color=MUTED, italic=True))

    render(path, w, h, *frags, title="Життєвий цикл прибирання сміття (GC) та Zone Reset у f2fs")

def render_all():
    img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "img"))
    os.makedirs(img_dir, exist_ok=True)
    print("Generating SVGs for zoned-storage-f2fs-integration...")
    build_fig1(img_dir)
    build_fig2(img_dir)
    build_fig3(img_dir)
    print("SVGs generated successfully.")

if __name__ == '__main__':
    render_all()
