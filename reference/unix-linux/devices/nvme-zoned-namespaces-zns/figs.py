import sys
import os

# Add scripts directory to sys.path (4 levels up from topic directory)
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from svgkit import (
    rect, text, mtext, line, arrow, circle, textbox, fitbox, render,
    FILL, LINE, INK, MUTED, POS, NEG, FIELD, BG
)

def make_zns_vs_ftl_svg(out_path):
    """
    Figure 1: Comparison of Conventional SSD FTL vs NVMe ZNS architecture.
    """
    w, h = 900, 520
    frags = []

    # Column 1: Conventional SSD Architecture
    frags.append(rect(20, 20, 410, 480, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(225, 48, "Традиційний NVMe SSD (Block Device)", size=16, bold=True, color=INK))

    # Host layer
    b_host1 = fitbox(40, 75, 370, 50, "ОС / Застосунок\nДовільний запис LBA (0..N)", size=13, fill="#e8f4f8", stroke="#2980b9")
    frags.append(b_host1)

    frags.append(arrow(225, 125, 225, 160, color=LINE, sw=2))

    # FTL layer
    b_ftl = fitbox(40, 160, 370, 190, 
                   "Складний шар FTL у пристрої\n"
                   "• LBA-to-PBA відображення (посторінкове)\n"
                   "• Garbage Collection (Збірка сміття)\n"
                   "• Write Amplification (WAF > 3.0)\n"
                   "• Потреба в DRAM (1 ГБ / 1 ТБ)\n"
                   "• Over-provisioning (~28% ємності)\n"
                   "• Непередбачувана затримка (Tail Latency)",
                   size=12, fill="#fdedec", stroke=POS)
    frags.append(b_ftl)

    frags.append(arrow(225, 350, 225, 385, color=LINE, sw=2))

    # NAND layer
    b_nand1 = fitbox(40, 385, 370, 95, 
                     "Фізична флеш-пам'ять NAND\n"
                     "Хаотичне мішування активних і застарілих сторінок\n"
                     "Постійне внутрішнє перезаписання блоків",
                     size=12, fill="#f4f6f8", stroke=MUTED)
    frags.append(b_nand1)


    # Column 2: NVMe ZNS SSD Architecture
    frags.append(rect(470, 20, 410, 480, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(675, 48, "Зонований NVMe ZNS SSD", size=16, bold=True, color=INK))

    # Host layer with ZBD awareness
    b_host2 = fitbox(490, 75, 370, 50, "ОС / Zone-Aware ФС / База даних\nПослідовний запис у зони (SWR / Append)", size=13, fill="#eafaf1", stroke=FIELD)
    frags.append(b_host2)

    frags.append(arrow(675, 125, 675, 160, color=LINE, sw=2))

    # Lightweight ZNS Layer
    b_zns = fitbox(490, 160, 370, 190, 
                   "Тонкий контролер ZNS\n"
                   "• Лінійне відображення зон на блоки\n"
                   "• Відсутня збірка сміття (WAF ≈ 1.0)\n"
                   "• Робота без DRAM (DRAM-less ZNS)\n"
                   "• Zero Over-provisioning (100% ємності)\n"
                   "• Лінійний вказівник запису (Write Pointer)\n"
                   "• Детермінована затримка (Predictable Latency)",
                   size=12, fill="#eafaf1", stroke=FIELD)
    frags.append(b_zns)

    frags.append(arrow(675, 350, 675, 385, color=LINE, sw=2))

    # NAND layer in ZNS
    b_nand2 = fitbox(490, 385, 370, 95, 
                     "Фізичні Erase Blocks NAND\n"
                     "Пряма відповідність зон і блоків стирання\n"
                     "Zone Reset = стирання фізичного блоку",
                     size=12, fill="#f4f6f8", stroke=MUTED)
    frags.append(b_nand2)

    render(out_path, w, h, *frags)

def make_zone_state_machine_svg(out_path):
    """
    Figure 2: Zone State Machine diagram for NVMe ZNS.
    """
    w, h = 920, 540
    frags = []

    frags.append(text(460, 30, "Кінцевий автомат станів зони ZNS (Zone State Machine)", size=17, bold=True, color=INK))

    # States positions
    # Empty: top center
    b_empty = fitbox(360, 70, 200, 50, "Empty (Порожня)\nWP = ZSLBA", size=13, fill="#e8f4f8", stroke="#2980b9", bold=True)
    frags.append(b_empty)

    # Open states
    b_imp = fitbox(120, 190, 200, 55, "Implicit Open\n(Неявно відкрита)\nАвто-відкриття записом", size=12, fill="#eafaf1", stroke=FIELD)
    frags.append(b_imp)

    b_exp = fitbox(600, 190, 200, 55, "Explicit Open\n(Явно відкрита)\nКоманда Zone Open", size=12, fill="#eafaf1", stroke=FIELD)
    frags.append(b_exp)

    # Closed state
    b_closed = fitbox(360, 310, 200, 50, "Closed (Закрита)\nРесурси вивільнені", size=13, fill="#fef9e7", stroke="#f39c12", bold=True)
    frags.append(b_closed)

    # Full state
    b_full = fitbox(360, 430, 200, 50, "Full (Заповнена)\nWP = End of Zone", size=13, fill="#ebdef0", stroke="#8e44ad", bold=True)
    frags.append(b_full)

    # Error states (side)
    b_ro = fitbox(690, 430, 180, 50, "Read Only\nЗбій запису", size=12, fill="#fdedec", stroke=POS)
    frags.append(b_ro)

    b_off = fitbox(50, 430, 180, 50, "Offline\nАпаратний збій", size=12, fill="#fdedec", stroke=POS)
    frags.append(b_off)

    # Transitions (Arrows)
    # Empty -> Implicit Open (Write)
    frags.append(arrow(380, 120, 220, 190, color=LINE, sw=1.5))
    frags.append(text(285, 142, "WRITE", size=11, bold=True, color=INK))

    # Empty -> Explicit Open (Zone Open)
    frags.append(arrow(540, 120, 700, 190, color=LINE, sw=1.5))
    frags.append(text(645, 142, "Zone Open", size=11, bold=True, color=INK))

    # Implicit Open <-> Closed
    frags.append(arrow(190, 245, 360, 320, color=LINE, sw=1.5))
    frags.append(text(245, 290, "Zone Close", size=11, color=MUTED))

    frags.append(arrow(370, 310, 240, 245, color=LINE, sw=1.5))
    frags.append(text(320, 265, "WRITE", size=11, color=INK))

    # Explicit Open <-> Closed
    frags.append(arrow(710, 245, 560, 320, color=LINE, sw=1.5))
    frags.append(text(665, 290, "Zone Close", size=11, color=MUTED))

    frags.append(arrow(550, 310, 680, 245, color=LINE, sw=1.5))
    frags.append(text(600, 265, "Zone Open", size=11, color=INK))

    # Implicit / Explicit Open -> Full
    frags.append(arrow(220, 245, 410, 430, color=LINE, sw=1.5))
    frags.append(text(270, 370, "Zone Finish / Full Write", size=11, color=INK))

    frags.append(arrow(700, 245, 510, 430, color=LINE, sw=1.5))
    frags.append(text(640, 370, "Zone Finish / Full Write", size=11, color=INK))

    # Closed -> Full (Finish)
    frags.append(arrow(460, 360, 460, 430, color=LINE, sw=1.5))
    frags.append(text(495, 395, "Zone Finish", size=11, color=INK))

    # Reset: Full / Closed / Open -> Empty
    frags.append(line(360, 455, 20, 455, color=POS, sw=1.8, dash="4,4"))
    frags.append(line(20, 455, 20, 95, color=POS, sw=1.8, dash="4,4"))
    frags.append(arrow(20, 95, 360, 95, color=POS, sw=1.8))
    frags.append(text(120, 80, "Zone Reset (Повернення в Empty)", size=12, bold=True, color=POS))

    render(out_path, w, h, *frags)

def make_zone_append_svg(out_path):
    """
    Figure 3: Standard Write (Locking bottleneck) vs Zone Append (Lockfree parallel submission).
    """
    w, h = 900, 480
    frags = []

    frags.append(text(450, 30, "Паралелізм NVMe: Стандартний Write vs Zone Append", size=17, bold=True, color=INK))

    # Left: Standard Write with Locks
    frags.append(rect(20, 55, 410, 400, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(225, 80, "Стандартний NVMe WRITE (Потрібні локи)", size=14, bold=True, color=POS))

    b_threads1 = fitbox(40, 105, 370, 45, "Потоки CPU 0..N (Багаточерговість blk-mq)", size=12, fill="#e8f4f8", stroke="#2980b9")
    frags.append(b_threads1)

    frags.append(arrow(225, 150, 225, 185, color=LINE, sw=2))

    b_lock = fitbox(60, 185, 330, 55, 
                    "Глобальний Mutex / Spinlock зони\n"
                    "Хост мусить послідовно вибирати LBA\n"
                    "Серіалізація викликів у ПЗ", size=12, fill="#fdedec", stroke=POS)
    frags.append(b_lock)

    frags.append(arrow(225, 240, 225, 275, color=LINE, sw=2))

    b_cmd1 = fitbox(40, 275, 370, 55, 
                    "NVMe Command: WRITE (LBA = X)\n"
                    "Якщо раптом гонка адресації ->\n"
                    "Помилка Unaligned Write (0x0288)", size=12, fill="#fef9e7", stroke="#f39c12")
    frags.append(b_cmd1)

    frags.append(arrow(225, 330, 225, 365, color=LINE, sw=2))

    b_ssd1 = fitbox(40, 365, 370, 70, 
                    "Контролер SSD ZNS\n"
                    "Перевіряє: LBA == Write Pointer?\n"
                    "Приймає лише ідеально впорядковані I/O", size=12, fill="#f4f6f8", stroke=MUTED)
    frags.append(b_ssd1)


    # Right: Zone Append
    frags.append(rect(470, 55, 410, 400, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(675, 80, "Атомарна команда ZONE APPEND (Lock-free)", size=14, bold=True, color=FIELD))

    b_threads2 = fitbox(490, 105, 370, 45, "Потоки CPU 0..N (Асинхронний io_uring)", size=12, fill="#eafaf1", stroke=FIELD)
    frags.append(b_threads2)

    frags.append(arrow(675, 150, 675, 185, color=FIELD, sw=2))

    b_nolock = fitbox(510, 185, 330, 55, 
                      "БЕЗ БЛОКУВАНЬ (Lock-free)\n"
                      "Хост передає лише ZSLBA (Початок зони)\n"
                      "Паралельне заповнення Submission Queues", size=12, fill="#eafaf1", stroke=FIELD)
    frags.append(b_nolock)

    frags.append(arrow(675, 240, 675, 275, color=FIELD, sw=2))

    b_cmd2 = fitbox(490, 275, 370, 55, 
                    "NVMe Command: ZONE APPEND (ZSLBA = ZoneStart)\n"
                    "Ніде немає явного вказання LBA", size=12, fill="#eafaf1", stroke=FIELD)
    frags.append(b_cmd2)

    frags.append(arrow(675, 330, 675, 365, color=FIELD, sw=2))

    b_ssd2 = fitbox(490, 365, 370, 70, 
                    "Апаратна обробка в SSD ZNS\n"
                    "1. Атомарне виділення LBA = Write Pointer\n"
                    "2. Інкремент Write Pointer на розмір запису\n"
                    "3. Повернення виділеного LBA у CQE", size=12, fill="#e8f4f8", stroke="#2980b9")
    frags.append(b_ssd2)

    render(out_path, w, h, *frags)

def render_all():
    img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
    os.makedirs(img_dir, exist_ok=True)

    make_zns_vs_ftl_svg(os.path.join(img_dir, 'zns-vs-conventional-ftl.svg'))
    make_zone_state_machine_svg(os.path.join(img_dir, 'zone-state-machine.svg'))
    make_zone_append_svg(os.path.join(img_dir, 'zone-append-locking.svg'))
    print("Rendered 3 SVG diagrams successfully.")

if __name__ == '__main__':
    render_all()
