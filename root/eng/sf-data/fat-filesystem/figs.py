# -*- coding: utf-8 -*-
"""Фігури до теми «Файлова система FAT».
Генерує векторні схеми SVG у теці ./img/:
1. fat-volume-layout.svg — анатомія тома FAT12/16 проти FAT32 (регіони та розміщення)
2. fat-cluster-chain.svg — зв'язування розрізнених кластерів через таблицю FAT (індексований список)
3. fat-directory-entry.svg — структура 32-байтного запису каталогу (SFN 8.3) та стек записів LFN
4. fat-cluster-lookup.svg — трансляція логічного зміщення файлу у фізичний сектор LBA
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Анатомія тома FAT12/16 та FAT32
# ─────────────────────────────────────────────────────────────────────────────
def fig_volume_layout():
    W, H = 840, 420
    parts = []
    
    parts.append(rect(15, 15, 810, 390, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 42, "Структура тома файлової системи FAT на блочному носії", size=16, color=INK, bold=True))
    parts.append(text(420, 64, "Поділ простору LBA на зарезервовану область, таблиці FAT, кореневий каталог та купу кластерів", size=12, color=MUTED))
    
    # ── FAT12 / FAT16 ──
    parts.append(text(40, 100, "FAT12 / FAT16:", size=13, color=INK, bold=True, anchor="start"))
    
    y1 = 115
    h1 = 70
    
    # Block 1: Reserved
    parts.append(rect(40, y1, 130, h1, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=4))
    parts.append(text(105, y1 + 25, "Зарезервована", size=12, color="#991b1b", bold=True))
    parts.append(text(105, y1 + 43, "Boot Sector / BPB", size=11, color="#7f1d1d"))
    parts.append(text(105, y1 + 58, "(Сектор 0)", size=10, color=MUTED))
    
    # Block 2: FATs
    parts.append(rect(180, y1, 160, h1, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=4))
    parts.append(text(260, y1 + 25, "Таблиці FAT", size=12, color="#1e40af", bold=True))
    parts.append(text(260, y1 + 43, "FAT1 (основна)", size=11, color="#1e3a8a"))
    parts.append(text(260, y1 + 58, "FAT2 (резервна)", size=11, color="#1e3a8a"))
    
    # Block 3: Root Dir (Fixed)
    parts.append(rect(350, y1, 150, h1, fill="#fef3c7", stroke="#f59e0b", sw=1.5, rx=4))
    parts.append(text(425, y1 + 25, "Кореневий каталог", size=12, color="#92400e", bold=True))
    parts.append(text(425, y1 + 43, "Фіксований розмір", size=11, color="#78350f"))
    parts.append(text(425, y1 + 58, "512 записів (32 сектори)", size=10, color=MUTED))
    
    # Block 4: Data Region
    parts.append(rect(510, y1, 290, h1, fill="#dcfce7", stroke="#22c55e", sw=1.5, rx=4))
    parts.append(text(655, y1 + 25, "Область даних (Data Region)", size=12, color="#166534", bold=True))
    parts.append(text(655, y1 + 43, "Купа кластерів: Кластери #2, #3, #4, ... #N", size=11, color="#14532d"))
    parts.append(text(655, y1 + 58, "Файли та вкладені підкаталоги", size=10, color=MUTED))

    # ── FAT32 ──
    parts.append(text(40, 225, "FAT32:", size=13, color=INK, bold=True, anchor="start"))
    
    y2 = 240
    h2 = 80
    
    # Block 1: Reserved (Bigger)
    parts.append(rect(40, y2, 170, h2, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=4))
    parts.append(text(125, y2 + 22, "Зарезервована область", size=12, color="#991b1b", bold=True))
    parts.append(text(125, y2 + 40, "Сектор 0: VBR + BPB", size=11, color="#7f1d1d"))
    parts.append(text(125, y2 + 56, "Сектор 1: FSInfo", size=11, color="#7f1d1d"))
    parts.append(text(125, y2 + 71, "Сектор 6: Backup VBR", size=10, color=MUTED))
    
    # Block 2: FATs (Much larger, 32-bit entries)
    parts.append(rect(220, y2, 190, h2, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=4))
    parts.append(text(315, y2 + 22, "Таблиці FAT (32-бітні)", size=12, color="#1e40af", bold=True))
    parts.append(text(315, y2 + 40, "FAT1 (основна таблиця)", size=11, color="#1e3a8a"))
    parts.append(text(315, y2 + 56, "FAT2 (резервна копія)", size=11, color="#1e3a8a"))
    parts.append(text(315, y2 + 71, "4 байти на кожен кластер", size=10, color=MUTED))
    
    # Block 3: Data Region with dynamic root cluster
    parts.append(rect(420, y2, 380, h2, fill="#dcfce7", stroke="#22c55e", sw=1.5, rx=4))
    parts.append(text(610, y2 + 22, "Область даних (Data Region / Cluster Heap)", size=12, color="#166534", bold=True))
    parts.append(text(610, y2 + 40, "Кластер #2: Кореневий каталог (BPB_RootClus) — динамічний ланцюжок", size=11, color="#14532d", bold=True))
    parts.append(text(610, y2 + 56, "Кластери #3, #4, ... #N: Звичайні файли та підкаталоги", size=11, color="#14532d"))
    parts.append(text(610, y2 + 71, "Кореневий каталог може нескінченно рости, як звичайний файл", size=10, color=MUTED))

    # Bottom notes
    parts.append(text(420, 355, "Ключова відмінність FAT32: відсутність окремої фіксованої області для Root Directory.", size=12, color=INK, bold=True))
    parts.append(text(420, 375, "Кореневий каталог у FAT32 розміщується безпосередньо в купі даних як динамічний ланцюжок кластерів.", size=11, color=MUTED))

    render(os.path.join(OUT, "fat-volume-layout.svg"), W, H, *parts)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Зв'язування розрізнених кластерів через таблицю FAT
# ─────────────────────────────────────────────────────────────────────────────
def fig_cluster_chain():
    W, H = 840, 460
    parts = []
    
    parts.append(rect(15, 15, 810, 430, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 40, "Механізм зв'язування файлу: Directory Entry → Таблиця FAT → Кластери даних", size=15, color=INK, bold=True))
    parts.append(text(420, 60, "Таблиця FAT слугує зовнішнім індексованим однозв'язним списком для фізичних кластерів", size=12, color=MUTED))
    
    # ── 1. Directory Entry box ──
    parts.append(rect(40, 95, 220, 115, fill="#fef3c7", stroke="#f59e0b", sw=1.5, rx=4))
    parts.append(text(150, 118, "Запис каталогу (Dir Entry)", size=12, color="#92400e", bold=True))
    parts.append(line(40, 128, 260, 128, color="#f59e0b", sw=1))
    parts.append(text(50, 148, "Ім'я файлу:  REPORT.TXT", size=11, color="#78350f", anchor="start"))
    parts.append(text(50, 168, "Розмір:      11 400 байтів", size=11, color="#78350f", anchor="start"))
    parts.append(text(50, 192, "Перший кластер = 3", size=12, color="#b45309", bold=True, anchor="start"))

    # ── 2. FAT Table box ──
    parts.append(rect(300, 95, 200, 315, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=4))
    parts.append(text(400, 118, "Таблиця FAT", size=13, color="#1e40af", bold=True))
    parts.append(line(300, 128, 500, 128, color="#3b82f6", sw=1))
    
    # Table header
    parts.append(text(340, 145, "Індекс", size=11, color="#1e3a8a", bold=True))
    parts.append(text(435, 145, "Значення (Next)", size=11, color="#1e3a8a", bold=True))
    parts.append(line(300, 153, 500, 153, color="#93c5fd", sw=1))

    # FAT rows
    entries = [
        (0, "0x0FFFFFF8", "Службовий (Media ID)", False, False),
        (1, "0x0FFFFFFF", "Службовий (EOC)", False, False),
        (2, "0x0FFFFFFF", "EOC (Root Dir)", False, False),
        (3, "0x00000005", "Вказівник на #5", True, True),
        (4, "0x00000000", "0 (Вільний кластер)", False, False),
        (5, "0x00000007", "Вказівник на #7", True, True),
        (6, "0x00000000", "0 (Вільний кластер)", False, False),
        (7, "0x0FFFFFFF", "EOC (Кінець файлу)", True, True)
    ]
    
    y_row = 172
    for idx, val, desc, is_file, is_highlight in entries:
        if is_highlight:
            parts.append(rect(305, y_row - 14, 190, 22, fill="#fed7aa" if idx == 3 else ("#fef08a" if idx == 5 else "#bbf7d0"), stroke="#f97316" if idx == 3 else ("#eab308" if idx == 5 else "#22c55e"), sw=1, rx=2))
        
        parts.append(text(340, y_row + 1, f"[{idx}]", size=11, color="#0f172a" if not is_file else "#1e3a8a", bold=is_file))
        parts.append(text(435, y_row + 1, val, size=11, color="#0f172a" if not is_file else "#1e3a8a", bold=is_file))
        y_row += 27

    # ── 3. Data Clusters ──
    parts.append(rect(540, 95, 265, 315, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=4))
    parts.append(text(672, 118, "Купа кластерів (Data Clusters)", size=13, color="#166534", bold=True))
    parts.append(line(540, 128, 805, 128, color="#22c55e", sw=1))
    
    clusters = [
        (2, "Кластер #2", "Вміст Root Directory", "#e2e8f0", "#64748b"),
        (3, "Кластер #3", "Файл REPORT.TXT (0 – 4095 B)", "#fed7aa", "#c2410c"),
        (4, "Кластер #4", "[Порожній / Вільний простір]", "#ffffff", "#94a3b8"),
        (5, "Кластер #5", "Файл REPORT.TXT (4096 – 8191 B)", "#fef08a", "#a16207"),
        (6, "Кластер #6", "[Порожній / Вільний простір]", "#ffffff", "#94a3b8"),
        (7, "Кластер #7", "Файл REPORT.TXT (8192 – 11399 B)", "#bbf7d0", "#15803d")
    ]
    
    y_c = 145
    for c_id, title, subtitle, bg_col, border_col in clusters:
        parts.append(rect(555, y_c, 235, 35, fill=bg_col, stroke=border_col, sw=1.5, rx=3))
        parts.append(text(672, y_c + 15, title, size=11, color=INK, bold=True))
        parts.append(text(672, y_c + 29, subtitle, size=10, color=MUTED))
        y_c += 43

    # ── Connectors and arrows ──
    parts.append(arrow(260, 192, 305, 253, color="#ea580c", sw=2))
    parts.append(line(495, 253, 555, 205, color="#ea580c", sw=2, dash="3,3"))
    
    parts.append(arrow(495, 260, 495, 295, color="#d97706", sw=2))
    parts.append(line(495, 307, 555, 292, color="#d97706", sw=2, dash="3,3"))

    parts.append(arrow(495, 315, 495, 350, color="#16a34a", sw=2))
    parts.append(line(495, 361, 555, 378, color="#16a34a", sw=2, dash="3,3"))

    # Bottom summary
    parts.append(text(420, 427, "Ланцюжок кластерів файлу REPORT.TXT: Кластер 3 → Кластер 5 → Кластер 7 (EOC)", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "fat-cluster-chain.svg"), W, H, *parts)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Структура 32-байтного запису каталогу (SFN) та довгі імена (LFN)
# ─────────────────────────────────────────────────────────────────────────────
def fig_directory_entry():
    W, H = 840, 450
    parts = []
    
    parts.append(rect(15, 15, 810, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 40, "Анатомія 32-байтного запису каталогу та механізм VFAT LFN", size=15, color=INK, bold=True))
    parts.append(text(420, 60, "Короткий запис 8.3 (SFN) та стек псевдозаписів довгих імен файлів (LFN)", size=12, color=MUTED))
    
    # ── Top block: 8.3 SFN Byte Layout ──
    parts.append(text(40, 90, "Структура класичного 32-байтного запису каталогу (SFN):", size=13, color=INK, bold=True, anchor="start"))
    
    fields = [
        (0, 8, "DIR_Name", "8 байтів\nІм'я (ASCII)", "#dbeafe", "#3b82f6"),
        (8, 3, "DIR_Ext", "3 байти\nТип (Ext)", "#e0e7ff", "#6366f1"),
        (11, 1, "Attr", "1 байт\nПрапорці", "#fef3c7", "#f59e0b"),
        (12, 1, "NTRes", "1 байт\nРегістр", "#f1f5f9", "#94a3b8"),
        (13, 1, "CrtTimeTenth", "1 байт\n10 мс", "#f1f5f9", "#94a3b8"),
        (14, 2, "CrtTime", "2 байти\nСтворення", "#f1f5f9", "#94a3b8"),
        (16, 2, "CrtDate", "2 байти\nСтворення", "#f1f5f9", "#94a3b8"),
        (18, 2, "LstAccDate", "2 байти\nДоступ", "#f1f5f9", "#94a3b8"),
        (20, 2, "FstClusHI", "2 байти\nКластер [31:16]", "#fee2e2", "#ef4444"),
        (22, 2, "WrtTime", "2 байти\nЗміна", "#f1f5f9", "#94a3b8"),
        (24, 2, "WrtDate", "2 байти\nЗміна", "#f1f5f9", "#94a3b8"),
        (26, 2, "FstClusLO", "2 байти\nКластер [15:0]", "#fee2e2", "#ef4444"),
        (28, 4, "FileSize", "4 байти\nРозмір (B)", "#dcfce7", "#22c55e")
    ]
    
    # Render SFN byte ribbon
    x_pos = 40
    y_ribbon = 105
    h_ribbon = 60
    
    widths = [75, 45, 45, 40, 42, 55, 55, 50, 78, 55, 55, 78, 77]
    
    for i, (offset, size_b, name, desc, bg_col, b_col) in enumerate(fields):
        w = widths[i]
        parts.append(rect(x_pos, y_ribbon, w, h_ribbon, fill=bg_col, stroke=b_col, sw=1.5, rx=3))
        parts.append(text(x_pos + w/2, y_ribbon + 15, name, size=10, color=INK, bold=True))
        
        # Split desc into 2 lines
        d_lines = desc.split("\n")
        parts.append(text(x_pos + w/2, y_ribbon + 33, d_lines[0], size=9, color=MUTED))
        parts.append(text(x_pos + w/2, y_ribbon + 48, d_lines[1], size=9, color="#0f172a", bold=True if "Кластер" in d_lines[1] or "Розмір" in d_lines[1] else False))
        
        # Byte offset marker below
        parts.append(text(x_pos, y_ribbon + 72, f"+{offset}", size=9, color=MUTED, anchor="start"))
        x_pos += w
    parts.append(text(x_pos, y_ribbon + 72, "+32", size=9, color=MUTED, anchor="end"))

    # ── Bottom block: VFAT LFN Stack Mechanism ──
    parts.append(text(40, 205, "Стек записів VFAT для довгого імені «Фінансовий_звіт_2026.docx»:", size=13, color=INK, bold=True, anchor="start"))
    
    y_lfn = 225
    lfn_h = 42
    
    # Entry 1: LFN #2 (0x42)
    parts.append(rect(40, y_lfn, 760, lfn_h, fill="#fdf4ff", stroke="#c084fc", sw=1.5, rx=4))
    parts.append(text(80, y_lfn + 25, "LFN #2 (0x42)", size=11, color="#7e22ce", bold=True))
    parts.append(text(190, y_lfn + 25, "Прапорець LAST_ENTRY | Порядок 2", size=10, color=MUTED))
    parts.append(text(460, y_lfn + 25, "Символи UTF-16LE: «_2026.docx\\0»", size=11, color="#581c87", bold=True))
    parts.append(text(690, y_lfn + 25, "Attr: 0x0F | Checksum: 0x8B", size=10, color="#7e22ce"))
    
    # Entry 2: LFN #1 (0x01)
    y_lfn += 48
    parts.append(rect(40, y_lfn, 760, lfn_h, fill="#fdf4ff", stroke="#c084fc", sw=1.5, rx=4))
    parts.append(text(80, y_lfn + 25, "LFN #1 (0x01)", size=11, color="#7e22ce", bold=True))
    parts.append(text(190, y_lfn + 25, "Порядковий номер 1", size=10, color=MUTED))
    parts.append(text(460, y_lfn + 25, "Символи UTF-16LE: «Фінансовий_звіт»", size=11, color="#581c87", bold=True))
    parts.append(text(690, y_lfn + 25, "Attr: 0x0F | Checksum: 0x8B", size=10, color="#7e22ce"))

    # Entry 3: Alias SFN
    y_lfn += 48
    parts.append(rect(40, y_lfn, 760, lfn_h, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=4))
    parts.append(text(80, y_lfn + 25, "SFN (8.3 Alias)", size=11, color="#1e40af", bold=True))
    parts.append(text(190, y_lfn + 25, "Короткий аліас: «ФІНАНС~1.DOC»", size=11, color="#1e3a8a", bold=True))
    parts.append(text(460, y_lfn + 25, "Реальні метадані: Кластер #142, Розмір 48 512 B, Час/Дата", size=10, color="#1e3a8a"))
    parts.append(text(690, y_lfn + 25, "Attr: 0x20 | Обчислено Checksum: 0x8B", size=10, color="#1e40af"))

    # Explanation lines
    parts.append(text(420, 395, "Записи LFN розміщуються безпосередньо перед коротким записом у зворотному порядку.", size=12, color=INK, bold=True))
    parts.append(text(420, 415, "Атрибут 0x0F захищає LFN від модифікації старими драйверами DOS, а контрольна сума гарантує зв'язок.", size=11, color=MUTED))

    render(os.path.join(OUT, "fat-directory-entry.svg"), W, H, *parts)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4: Трансляція логічного зміщення файлу у фізичний сектор LBA
# ─────────────────────────────────────────────────────────────────────────────
def fig_cluster_lookup():
    W, H = 840, 420
    parts = []
    
    parts.append(rect(15, 15, 810, 390, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 40, "Покрокова трансляція зміщення у файлі у фізичний сектор носія (LBA)", size=15, color=INK, bold=True))
    parts.append(text(420, 60, "Від логічного байта до секторів таблиці FAT та кінцевого сектора на диску", size=12, color=MUTED))
    
    y_step = 95
    step_w = 175
    step_h = 135
    
    # Step 1: Logical Offset
    parts.append(rect(40, y_step, step_w, step_h, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=4))
    parts.append(text(127, y_step + 22, "1. Логічне зміщення", size=12, color="#991b1b", bold=True))
    parts.append(line(40, y_step + 32, 40 + step_w, y_step + 32, color="#ef4444", sw=1))
    parts.append(text(127, y_step + 55, "Зсув у файлі: 10 500 B", size=11, color=INK, bold=True))
    parts.append(text(127, y_step + 75, "Кластер = 4096 B", size=10, color=MUTED))
    parts.append(text(127, y_step + 95, "Номер кроку = 10500 ÷ 4096", size=9, color="#7f1d1d"))
    parts.append(text(127, y_step + 115, "= 2-й кластер файлу", size=11, color="#991b1b", bold=True))

    # Arrow 1 -> 2
    parts.append(arrow(215, y_step + 67, 240, y_step + 67, color=INK, sw=2))

    # Step 2: Traverse FAT Chain
    parts.append(rect(240, y_step, step_w, step_h, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=4))
    parts.append(text(327, y_step + 22, "2. Прохід ланцюжка", size=12, color="#1e40af", bold=True))
    parts.append(line(240, y_step + 32, 240 + step_w, y_step + 32, color="#3b82f6", sw=1))
    parts.append(text(327, y_step + 55, "DirEntry: FirstClus = 8", size=10, color=INK))
    parts.append(text(327, y_step + 75, "FAT[8] → 15 (крок 1)", size=10, color=INK))
    parts.append(text(327, y_step + 95, "FAT[15] → 23 (крок 2)", size=10, color=INK))
    parts.append(text(327, y_step + 115, "Шуканий кластер = 23", size=11, color="#1e40af", bold=True))

    # Arrow 2 -> 3
    parts.append(arrow(415, y_step + 67, 440, y_step + 67, color=INK, sw=2))

    # Step 3: FAT Sector Math
    parts.append(rect(440, y_step, step_w, step_h, fill="#fef3c7", stroke="#f59e0b", sw=1.5, rx=4))
    parts.append(text(527, y_step + 22, "3. Читання самої FAT", size=12, color="#92400e", bold=True))
    parts.append(line(440, y_step + 32, 440 + step_w, y_step + 32, color="#f59e0b", sw=1))
    parts.append(text(527, y_step + 55, "Зміщення = 23 · 4 = 92 B", size=10, color=INK))
    parts.append(text(527, y_step + 75, "Сектор FAT = Rsvd + (92÷512)", size=9, color=MUTED))
    parts.append(text(527, y_step + 95, "Зміщення в секторі = 92", size=10, color=INK))
    parts.append(text(527, y_step + 115, "Кеш блоків FAT (L1)", size=11, color="#b45309", bold=True))

    # Arrow 3 -> 4
    parts.append(arrow(615, y_step + 67, 640, y_step + 67, color=INK, sw=2))

    # Step 4: Final LBA Sector
    parts.append(rect(640, y_step, step_w, step_h, fill="#dcfce7", stroke="#22c55e", sw=1.5, rx=4))
    parts.append(text(727, y_step + 22, "4. Фізичний сектор", size=12, color="#166534", bold=True))
    parts.append(line(640, y_step + 32, 640 + step_w, y_step + 32, color="#22c55e", sw=1))
    parts.append(text(727, y_step + 55, "LBA = FirstDataSector +", size=10, color=INK))
    parts.append(text(727, y_step + 75, "(23 - 2) · SecPerClus", size=10, color=INK))
    parts.append(text(727, y_step + 95, "+ Зсув у кластері (4 B)", size=10, color=MUTED))
    parts.append(text(727, y_step + 115, "LBA #2048 (read/write)", size=11, color="#166534", bold=True))

    # Bottom detailed formulas
    parts.append(rect(40, 255, 760, 120, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=4))
    parts.append(text(420, 275, "Формули обчислення адрес для драйвера файлової системи:", size=12, color=INK, bold=True))
    parts.append(text(60, 300, "• Сектор FAT для кластера N:   FAT_Sector = BPB_RsvdSecCnt + ((N · FAT_Entry_Size) ÷ BPB_BytsPerSec)", size=11, color="#1e3a8a", anchor="start"))
    parts.append(text(60, 322, "• Зміщення запису в секторі:   FAT_Offset = (N · FAT_Entry_Size) % BPB_BytsPerSec", size=11, color="#1e3a8a", anchor="start"))
    parts.append(text(60, 344, "• Перший сектор кластера N:    Cluster_LBA = FirstDataSector + ((N - 2) · BPB_SecPerClus)", size=11, color="#15803d", anchor="start"))
    parts.append(text(60, 364, "• Зсув сектора всередині купи: Sector_In_Cluster = (File_Offset % Cluster_Bytes) ÷ BPB_BytsPerSec", size=11, color="#15803d", anchor="start"))

    render(os.path.join(OUT, "fat-cluster-lookup.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_volume_layout()
    fig_cluster_chain()
    fig_directory_entry()
    fig_cluster_lookup()
    print("Усі 4 фігури успішно згенеровано у ./img/")
