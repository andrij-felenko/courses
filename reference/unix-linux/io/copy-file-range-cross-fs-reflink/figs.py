import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def cross_fs_reflink_boundary():
    frags = []
    
    # Outer frame
    frags.append(rect(10, 10, 780, 430, rx=8, fill="#fafafa", stroke="#d0d0d0"))
    b, _, _ = textbox(400, 30, "Межа екземпляра ФС (Superblock Boundary) та виклики Reflink / Cross-FS", size=15, bold=True, fill="#ffffff", stroke="#d0d0d0")
    frags.append(b)
    
    # Left Box: Superblock A (x=25 to x=345, width=320)
    frags.append(rect(25, 60, 320, 350, rx=6, fill="#f0f7ff", stroke="#3b82f6"))
    frags.append(text(185, 85, "Superblock A (struct super_block *sb_in)", size=12, bold=True, anchor="middle", color="#1e40af"))
    frags.append(text(185, 105, "Пристрій /dev/sda1 (Btrfs Pool 1)", size=10, anchor="middle", color="#475569"))
    
    in0, _, _ = textbox(185, 145, "Inode #1042 (файл-джерело)\nРозмір: 10 Гігобайт", size=10, fill="#ffffff", stroke="#60a5fa", rx=4)
    in1, _, _ = textbox(185, 215, "B-Tree екстентів (Extent Tree)\nExtent ID: 0x8F0A -> Block #50010\n[refcount = 1]", size=10, fill="#ffffff", stroke="#60a5fa", rx=4)
    in2, _, _ = textbox(185, 335, "Inode #2088 (локальний клон)\nExtent ID: 0x8F0A -> Block #50010\n[refcount = 2 (CoW клон)]", size=10, fill="#ffffff", stroke="#22c55e", rx=4)
    frags.extend([in0, in1, in2])
    frags.append(arrow(185, 255, 185, 305, color="#16a34a"))
    frags.append(text(195, 280, "FICLONE (0 байт I/O)", size=9, bold=True, anchor="start", color="#15803d"))
    
    # Right Box: Superblock B (x=455 to x=775, width=320)
    frags.append(rect(455, 60, 320, 350, rx=6, fill="#fff7ed", stroke="#f97316"))
    frags.append(text(615, 85, "Superblock B (struct super_block *sb_out)", size=12, bold=True, anchor="middle", color="#9a3412"))
    frags.append(text(615, 105, "Пристрій /dev/sdb1 (XFS / Pool 2)", size=10, anchor="middle", color="#475569"))
    
    out0, _, _ = textbox(615, 145, "Inode #9012 (цільовий файл)\nПорожній / Новий файл", size=10, fill="#ffffff", stroke="#fb923c", rx=4)
    out1, _, _ = textbox(615, 215, "Окремий простір адресації блоків\nAG (Allocation Groups) / Block Map B", size=10, fill="#ffffff", stroke="#fb923c", rx=4)
    out2, _, _ = textbox(615, 335, "Фізичне копіювання даних\nВиділення нових блоків у SB B\nPageCache splice / SSC сервера", size=10, fill="#ffffff", stroke="#ea580c", rx=4)
    frags.extend([out0, out1, out2])
    frags.append(arrow(615, 255, 615, 305, color="#c2410c"))
    
    # Gap between 345 and 455 is 110px.
    # Cross-Superblock Arrow (EXDEV)
    frags.append(arrow(300, 215, 500, 215, color="#dc2626"))
    frags.append(rect(350, 195, 100, 40, rx=4, fill="#fef2f2", stroke="#ef4444"))
    frags.append(text(400, 212, "FICLONE", size=9, bold=True, anchor="middle", color="#b91c1c"))
    frags.append(text(400, 227, "errno = EXDEV", size=9, bold=True, anchor="middle", color="#b91c1c"))
    
    # copy_file_range arrow across superblocks
    frags.append(arrow(300, 335, 500, 335, color="#2563eb"))
    frags.append(rect(350, 315, 100, 40, rx=4, fill="#eff6ff", stroke="#3b82f6"))
    frags.append(text(400, 332, "copy_file_range", size=9, bold=True, anchor="middle", color="#1d4ed8"))
    frags.append(text(400, 347, "Cross-FS Offload", size=9, anchor="middle", color="#1d4ed8"))
    
    return frags

def vfs_copy_cascade_hierarchy():
    frags = []
    
    frags.append(rect(10, 10, 780, 440, rx=8, fill="#fafafa", stroke="#d0d0d0"))
    b, _, _ = textbox(400, 30, "Каскадна ієрархія виконання copy_file_range() у ядрі Linux", size=15, bold=True, fill="#ffffff", stroke="#d0d0d0")
    frags.append(b)
    
    # Top Node: Syscall entry
    n0, _, _ = textbox(400, 70, "Системний виклик copy_file_range(fd_in, off_in, fd_out, off_out, len, 0)\nVFS: sys_copy_file_range() -> vfs_copy_file_range()", size=10, fill="#f0f7ff", stroke="#3b82f6", rx=4)
    frags.append(n0)
    frags.append(arrow(400, 95, 400, 120, color="#64748b"))
    
    # Level 1: Same SB Reflink
    n1, _, _ = textbox(400, 140, "Рівень 1: Reflink / Extent Cloning (sb_in == sb_out)\nВказівник file_in->f_op->remap_file_range (CoW на рівні метаданих ФС)", size=10, fill="#f0fdf4", stroke="#22c55e", rx=4)
    frags.append(n1)
    frags.append(arrow(400, 165, 400, 190, color="#64748b"))
    frags.append(text(415, 180, "Якщо rfr не підтримується або sb_in != sb_out (Cross-FS)", size=9, color="#64748b", anchor="start"))
    
    # Level 2: File System Specific / SSC
    n2, _, _ = textbox(400, 210, "Рівень 2: Хук ФС file_in->f_op->copy_file_range\nServer-Side Copy (NFS v4.2 SSC, SMB3 CopyChunk) / Cross-Mount Offload", size=10, fill="#fff7ed", stroke="#f97316", rx=4)
    frags.append(n2)
    frags.append(arrow(400, 235, 400, 260, color="#64748b"))
    frags.append(text(415, 250, "Якщо f_op->copy_file_range = NULL", size=9, color="#64748b", anchor="start"))
    
    # Level 3: Block Layer Offload
    n3, _, _ = textbox(400, 280, "Рівень 3 (у майнлайн НЕ прийнято): offload блочного шару\nПатчі blkdev_issue_copy: NVMe Copy TP 4065 / SCSI XCOPY", size=10, fill="#fef3c7", stroke="#f59e0b", rx=4)
    frags.append(n3)
    frags.append(arrow(400, 305, 400, 330, color="#64748b"))
    frags.append(text(415, 320, "Якщо апаратний offload не підтримується", size=9, color="#64748b", anchor="start"))
    
    # Level 4: Generic Splice Fallback
    n4, _, _ = textbox(400, 360, "Рівень 4: Універсальний фолбек ядра (generic_copy_file_range)\nПередача байтів через Kernel Page Cache за допомогою splice_direct_to_actor()", size=10, fill="#fef2f2", stroke="#ef4444", rx=4)
    frags.append(n4)
    
    # Success/Return arrows on right
    frags.append(text(670, 140, "-> Повернення (0 байт I/O)", size=9, bold=True, color="#15803d", anchor="start"))
    frags.append(text(670, 210, "-> Повернення (Offload без CPU)", size=9, bold=True, color="#c2410c", anchor="start"))
    frags.append(text(670, 280, "-> Немає у ванільному ядрі", size=9, bold=True, color="#b45309", anchor="start"))
    frags.append(text(670, 360, "-> Повернення (DRAM / PageCache)", size=9, bold=True, color="#b91c1c", anchor="start"))
    
    return frags

def offload_mechanisms_comparison():
    frags = []
    
    frags.append(rect(10, 10, 780, 420, rx=8, fill="#fafafa", stroke="#d0d0d0"))
    b, _, _ = textbox(400, 30, "Шляхи руху даних: Reflink vs NVMe Copy vs Server-Side Copy vs PageCache", size=15, bold=True, fill="#ffffff", stroke="#d0d0d0")
    frags.append(b)
    
    # 4 columns for 4 mechanisms
    # Col 1: Reflink (CoW)
    frags.append(rect(25, 60, 175, 340, rx=6, fill="#f0fdf4", stroke="#86efac"))
    frags.append(text(112, 85, "1. Reflink (CoW)", size=12, bold=True, anchor="middle", color="#166534"))
    c1_1, _, _ = textbox(112, 130, "Метадані ФС\n(Superblock A)", size=9, fill="#ffffff", stroke="#4ade80", rx=4)
    c1_2, _, _ = textbox(112, 210, "Нуль I/O операцій\nлише інкремент\nrefcount в B-Tree", size=9, fill="#ffffff", stroke="#4ade80", rx=4)
    c1_3, _, _ = textbox(112, 300, "Швидкість: < 1 мс\nCPU: 0%\nDRAM: 0 байт", size=9, fill="#ffffff", stroke="#15803d", rx=4)
    frags.extend([c1_1, c1_2, c1_3])
    frags.append(arrow(112, 155, 112, 185, color="#16a34a"))
    frags.append(arrow(112, 235, 112, 275, color="#16a34a"))
    
    # Col 2: NVMe Copy (Controller)
    frags.append(rect(215, 60, 175, 340, rx=6, fill="#fef3c7", stroke="#fde047"))
    frags.append(text(302, 85, "2. NVMe Copy", size=12, bold=True, anchor="middle", color="#854d0e"))
    c2_1, _, _ = textbox(302, 130, "Команда NVMe\nSimple Copy (TP 4065)", size=9, fill="#ffffff", stroke="#facc15", rx=4)
    c2_2, _, _ = textbox(302, 210, "Копіювання у SRAM\nконтролера SSD\nбез шини PCIe", size=9, fill="#ffffff", stroke="#facc15", rx=4)
    c2_3, _, _ = textbox(302, 300, "Поза майнлайном:\nлише патчі offload\nCPU: ~0, DRAM: 0 байт", size=9, fill="#ffffff", stroke="#a16207", rx=4)
    frags.extend([c2_1, c2_2, c2_3])
    frags.append(arrow(302, 155, 302, 185, color="#ca8a04"))
    frags.append(arrow(302, 235, 302, 275, color="#ca8a04"))
    
    # Col 3: Server-Side Copy (NFS/SMB)
    frags.append(rect(405, 60, 175, 340, rx=6, fill="#fff7ed", stroke="#ffbb78"))
    frags.append(text(492, 85, "3. Server-Side Copy", size=12, bold=True, anchor="middle", color="#9a3412"))
    c3_1, _, _ = textbox(492, 130, "RPC NFSv4.2 COPY /\nSMB3 CopyChunk", size=9, fill="#ffffff", stroke="#fb923c", rx=4)
    c3_2, _, _ = textbox(492, 210, "Локальне копіювання\nна сервері сховища\nбез мережі", size=9, fill="#ffffff", stroke="#fb923c", rx=4)
    c3_3, _, _ = textbox(492, 300, "Швидкість: Диск серв.\nМережа трафік: 0 B\nКлієнт CPU: 0%", size=9, fill="#ffffff", stroke="#c2410c", rx=4)
    frags.extend([c3_1, c3_2, c3_3])
    frags.append(arrow(492, 155, 492, 185, color="#ea580c"))
    frags.append(arrow(492, 235, 492, 275, color="#ea580c"))
    
    # Col 4: PageCache Fallback
    frags.append(rect(595, 60, 175, 340, rx=6, fill="#fef2f2", stroke="#fca5a5"))
    frags.append(text(682, 85, "4. Generic Splice", size=12, bold=True, anchor="middle", color="#991b1b"))
    c4_1, _, _ = textbox(682, 130, "generic_copy_file_range\n(kernel splice)", size=9, fill="#ffffff", stroke="#f87171", rx=4)
    c4_2, _, _ = textbox(682, 210, "Зчитування в DRAM\nPage Cache ядра ->\nЗапис на ціль", size=9, fill="#ffffff", stroke="#f87171", rx=4)
    c4_3, _, _ = textbox(682, 300, "Швидкість: DRAM/Bus\nCPU: високе навантаж.\nPage Cache: вимивання", size=9, fill="#ffffff", stroke="#b91c1c", rx=4)
    frags.extend([c4_1, c4_2, c4_3])
    frags.append(arrow(682, 155, 682, 185, color="#dc2626"))
    frags.append(arrow(682, 235, 682, 275, color="#dc2626"))
    
    return frags

def main():
    f1 = cross_fs_reflink_boundary()
    render(os.path.join(IMG, 'cross-fs-reflink-boundary.svg'), 800, 450, *f1, title="Межа екземпляра ФС та Reflink")
    
    f2 = vfs_copy_cascade_hierarchy()
    render(os.path.join(IMG, 'vfs-copy-cascade-hierarchy.svg'), 800, 450, *f2, title="Каскадна ієрархія copy_file_range")
    
    f3 = offload_mechanisms_comparison()
    render(os.path.join(IMG, 'offload-mechanisms-comparison.svg'), 800, 430, *f3, title="Порівняння механізмів копіювання")

if __name__ == "__main__":
    main()
