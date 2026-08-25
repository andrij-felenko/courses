import sys
import os

# '..' four levels up from reference/unix-linux/files/statx-extended-stat-api to root scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_handshake_diagram(img_dir):
    w, h = 840, 430
    body = []
    
    # Background
    body.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # 3 Main Actors
    box_w, box_h = 220, 48
    
    # Header Boxes
    body.append(fitbox(50, 20, box_w, box_h, "Простір користувача\n(User Space Application)", size=12, bold=True, fill="#e8f4f8", stroke="#2980b9"))
    body.append(fitbox(310, 20, box_w, box_h, "Ядро / VFS\n(Virtual Filesystem Switch)", size=12, bold=True, fill="#fef9e7", stroke="#f39c12"))
    body.append(fitbox(570, 20, box_w, box_h, "Драйвер ФС / Носій\n(ext4, btrfs, NFS, NVMe)", size=12, bold=True, fill="#eaafaf", stroke="#c0392b"))
    
    # Vertical lifelines - segmented so they don't cross text boxes
    body.append(line(160, 70, 160, 350, color=MUTED, sw=1.5, dash="4,4"))
    body.append(line(420, 70, 420, 350, color=MUTED, sw=1.5, dash="4,4"))
    body.append(line(680, 70, 680, 350, color=MUTED, sw=1.5, dash="4,4"))
    
    # Step 1: User calls statx with mask_req
    body.append(arrow(160, 110, 410, 110, color="#2980b9", sw=2))
    body.append(fitbox(175, 82, 220, 24, "statx(fd, path, flags, mask_req, &stx)", size=10, bold=True, fill="#ffffff", stroke="#2980b9"))
    body.append(fitbox(180, 118, 210, 32, "Запит: STATX_BASIC_STATS |\nSTATX_BTIME | STATX_DIOALIGN", size=9, bold=False, fill="#ffffff", stroke=MUTED))

    # Step 2: VFS checks cache & delegates to FS
    body.append(arrow(420, 170, 670, 170, color="#f39c12", sw=2))
    body.append(fitbox(440, 142, 210, 24, "vfs_statx() -> getattr()", size=10, bold=True, fill="#ffffff", stroke="#f39c12"))
    body.append(fitbox(450, 178, 190, 32, "Перевірка підтримки полів\nта синхронізація кешу", size=9, bold=False, fill="#ffffff", stroke=MUTED))

    # Step 3: FS returns populated fields
    body.append(arrow(670, 240, 430, 240, color="#c0392b", sw=2))
    body.append(fitbox(445, 212, 210, 24, "Заповнення полів inode", size=10, bold=True, fill="#ffffff", stroke="#c0392b"))
    body.append(fitbox(450, 248, 200, 32, "Заповнено: BASIC_STATS, BTIME\nНе підтримано: DIOALIGN", size=9, bold=False, fill="#ffffff", stroke=MUTED))

    # Step 4: Kernel sets stx_mask and returns to user
    body.append(arrow(410, 310, 170, 310, color="#27ae60", sw=2))
    body.append(fitbox(180, 282, 210, 24, "Повернення struct statx", size=10, bold=True, fill="#ffffff", stroke="#27ae60"))
    body.append(fitbox(185, 318, 200, 32, "stx_mask = STATX_BASIC_STATS |\nSTATX_BTIME", size=9, bold=False, fill="#ffffff", stroke="#27ae60"))

    # Step 5: User space mask check (placed at bottom, lifeline ends at 350)
    body.append(fitbox(50, 365, 220, 40, "Перевірка простору користувача:\nif (stx.stx_mask & STATX_BTIME)", size=9, bold=True, fill="#e8f8f5", stroke="#27ae60"))

    out_path = os.path.join(img_dir, "statx-mask-handshake.svg")
    write_svg(out_path, "".join(body), w, h)

def generate_layout_diagram(img_dir):
    w, h = 840, 500
    body = []
    
    # Background
    body.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Title / Header Banner
    body.append(fitbox(20, 15, 800, 35, "Структура struct statx у пам'яті (фіксований розмір 256 байтів)", size=13, bold=True, fill="#ebf5fb", stroke="#2980b9"))
    
    # Layout blocks representation (Grid of 64-bit / 32-bit fields)
    # Row 1: stx_mask (32b) | stx_blksize (32b) | stx_attributes (64b)
    body.append(fitbox(20, 60, 190, 48, "stx_mask (4B)\nМаска заповнених полів", size=9, bold=True, fill="#fadbd8", stroke="#e74c3c"))
    body.append(fitbox(220, 60, 190, 48, "stx_blksize (4B)\nОптимальний блок вводу/виводу", size=9, bold=False, fill=FILL, stroke=LINE))
    body.append(fitbox(420, 60, 400, 48, "stx_attributes (8B)\nРозширені прапорці файлу (compressed, immutable, dax, verity)", size=9, bold=True, fill="#d5f5e3", stroke="#27ae60"))

    # Row 2: stx_nlink (32b) | stx_uid (32b) | stx_gid (32b) | stx_mode (16b) | __spare0 (16b)
    body.append(fitbox(20, 118, 150, 48, "stx_nlink (4B)\nЖорсткі посилання", size=9, bold=False, fill=FILL, stroke=LINE))
    body.append(fitbox(180, 118, 150, 48, "stx_uid (4B)\nВласник (UID)", size=9, bold=False, fill=FILL, stroke=LINE))
    body.append(fitbox(340, 118, 150, 48, "stx_gid (4B)\nГрупа (GID)", size=9, bold=False, fill=FILL, stroke=LINE))
    body.append(fitbox(500, 118, 160, 48, "stx_mode (2B)\nТип і права доступу", size=9, bold=True, fill="#fdebd0", stroke="#e67e22"))
    body.append(fitbox(670, 118, 150, 48, "__spare0 (2B)\nВирівнювання", size=9, bold=False, fill="#eaeded", stroke=MUTED))

    # Row 3: stx_ino (64b) | stx_size (64b) | stx_blocks (64b) | stx_attributes_mask (64b)
    body.append(fitbox(20, 176, 190, 48, "stx_ino (8B)\nНомер inode (64 біти)", size=9, bold=True, fill=FILL, stroke=LINE))
    body.append(fitbox(220, 176, 190, 48, "stx_size (8B)\nРозмір файлу в байтах", size=9, bold=True, fill=FILL, stroke=LINE))
    body.append(fitbox(420, 176, 190, 48, "stx_blocks (8B)\nБлоки по 512 байтів", size=9, bold=False, fill=FILL, stroke=LINE))
    body.append(fitbox(620, 176, 200, 48, "stx_attributes_mask (8B)\nМаска підтримуваних атрибутів", size=9, bold=True, fill="#d5f5e3", stroke="#27ae60"))

    # Row 4: Timestamps (4 x 16B = 64B total)
    body.append(fitbox(20, 234, 190, 52, "stx_atime (16B)\nЧас останнього доступу\n(tv_sec 64b + tv_nsec 32b)", size=9, bold=False, fill="#e8f8f5", stroke="#16a085"))
    body.append(fitbox(220, 234, 190, 52, "stx_btime (16B)\nЧас створення (birth time)\n(tv_sec 64b + tv_nsec 32b)", size=9, bold=True, fill="#d4efdf", stroke="#27ae60"))
    body.append(fitbox(420, 234, 190, 52, "stx_ctime (16B)\nЧас зміни статусу inode\n(tv_sec 64b + tv_nsec 32b)", size=9, bold=False, fill="#e8f8f5", stroke="#16a085"))
    body.append(fitbox(620, 234, 200, 52, "stx_mtime (16B)\nЧас зміни вмісту файлу\n(tv_sec 64b + tv_nsec 32b)", size=9, bold=False, fill="#e8f8f5", stroke="#16a085"))

    # Row 5: Device IDs & Mount ID
    body.append(fitbox(20, 296, 190, 48, "stx_rdev_* (8B)\nMajor/Minor пристрою", size=9, bold=False, fill=FILL, stroke=LINE))
    body.append(fitbox(220, 296, 190, 48, "stx_dev_* (8B)\nMajor/Minor файлової системи", size=9, bold=False, fill=FILL, stroke=LINE))
    body.append(fitbox(420, 296, 400, 48, "stx_mnt_id (8B)\nІдентифікатор точки монтування (Linux 5.8 / 6.8 unique)", size=9, bold=True, fill="#fef9e7", stroke="#f39c12"))

    # Row 6: DIO Alignments & Atomic Writes
    body.append(fitbox(20, 354, 390, 48, "stx_dio_mem_align & stx_dio_offset_align (8B)\nВимоги до вирівнювання буфера та зсуву для O_DIRECT (Linux 6.1)", size=9, bold=True, fill="#eaf2f8", stroke="#2980b9"))
    body.append(fitbox(420, 354, 400, 48, "stx_atomic_write_* (16B)\nАтомарні межі запису min/max/segments (Linux 6.11)", size=9, bold=True, fill="#f39c12", color="#ffffff", stroke="#b9770e"))

    # Row 7: Padding reserve for future ABI
    body.append(fitbox(20, 412, 800, 42, "__spare2 / Padding reserve (~80B)\nРезервні байти для збереження ABI-сумісності при розширенні ядра у майбутньому", size=9, bold=False, fill="#f2f4f4", stroke=MUTED))

    out_path = os.path.join(img_dir, "statx-struct-layout.svg")
    write_svg(out_path, "".join(body), w, h)

def write_svg(filepath, content_str, w, h):
    svg_str = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n'
               '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>\n'
               '%s\n</svg>' % (w, h, w, h, LINE, content_str))
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_str)
    print(f"Generated {filepath}")

def render():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    # Remove old statx-evolution.svg if present
    old_file = os.path.join(img_dir, "statx-evolution.svg")
    if os.path.exists(old_file):
        try: os.remove(old_file)
        except OSError: pass
    generate_handshake_diagram(img_dir)
    generate_layout_diagram(img_dir)

if __name__ == "__main__":
    render()
