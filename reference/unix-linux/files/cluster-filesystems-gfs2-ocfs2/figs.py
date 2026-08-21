import os
import sys

# Import svgkit from scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

try:
    import svgkit
except ImportError:
    svgkit = None

def generate_shared_disk_architecture():
    if not svgkit:
        return
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    frags = []

    # Title / Header
    frags.append(svgkit.text(450, 25, "Архітектура Кластерних ФС: Shared-Disk проти Клієнт-Серверних", size=14, bold=True, anchor="middle", color="#1a252f"))

    # Left Container: Shared-Disk Cluster Filesystem (GFS2 / OCFS2)
    frags.append(svgkit.rect(20, 45, 420, 315, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(svgkit.text(230, 68, "Shared-Disk (GFS2 / OCFS2)", size=12, bold=True, anchor="middle", color="#0f172a"))
    frags.append(svgkit.text(230, 84, "Симетричний прямий блоковий доступ усіх вузлів", size=9.5, anchor="middle", color="#64748b"))

    # Left Nodes
    tb_n1, _, _ = svgkit.textbox(90, 128, "Вузол 1 (Node A)\nVFS + GFS2/OCFS2\nPage Cache (RAM)", size=9, fill="#e0f2fe", stroke="#0284c7")
    tb_n2, _, _ = svgkit.textbox(230, 128, "Вузол 2 (Node B)\nVFS + GFS2/OCFS2\nPage Cache (RAM)", size=9, fill="#e0f2fe", stroke="#0284c7")
    tb_n3, _, _ = svgkit.textbox(370, 128, "Вузол 3 (Node C)\nVFS + GFS2/OCFS2\nPage Cache (RAM)", size=9, fill="#e0f2fe", stroke="#0284c7")
    frags.extend([tb_n1, tb_n2, tb_n3])

    # Interconnect DLM
    tb_dlm, _, _ = svgkit.textbox(230, 205, "Розподілений менеджер блокувань (DLM)\nМережа координації: Corosync / Totem (BAST, CAST)", size=9, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(tb_dlm)

    # Connections between nodes and DLM
    frags.append(svgkit.line(90, 155, 120, 185, color="#d97706", sw=1.5, dash="2,2"))
    frags.append(svgkit.line(230, 155, 230, 185, color="#d97706", sw=1.5, dash="2,2"))
    frags.append(svgkit.line(370, 155, 340, 185, color="#d97706", sw=1.5, dash="2,2"))

    # Shared SAN Storage box
    tb_san, _, _ = svgkit.textbox(230, 305, "Спільне блокове сховище (SAN / iSCSI / FC LUN)\nОкремі журнали (Per-Node) | Спільні метадані й блоки", size=9.5, fill="#dcfce7", stroke="#16a34a", bold=True)
    frags.append(tb_san)

    # Direct block I/O lines from nodes to SAN (routed around DLM box)
    # Node 1 -> SAN (left bypass)
    frags.append(svgkit.line(50, 155, 50, 260, color="#16a34a", sw=1.5))
    frags.append(svgkit.arrow(50, 260, 90, 285, color="#16a34a", sw=1.5))

    # Node 2 -> SAN (direct down between textboxes)
    frags.append(svgkit.arrow(230, 225, 230, 285, color="#16a34a", sw=1.5))

    # Node 3 -> SAN (right bypass)
    frags.append(svgkit.line(410, 155, 410, 260, color="#16a34a", sw=1.5))
    frags.append(svgkit.arrow(410, 260, 370, 285, color="#16a34a", sw=1.5))

    # Right Container: Client-Server / Distributed FS (NFS / Ceph)
    frags.append(svgkit.rect(460, 45, 420, 315, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(svgkit.text(670, 68, "Клієнт-Серверні / Об'єктні ФС (NFS / Ceph)", size=12, bold=True, anchor="middle", color="#0f172a"))
    frags.append(svgkit.text(670, 84, "Доступ через виділені сервери метаданих і шлюзи", size=9.5, anchor="middle", color="#64748b"))

    # Right Client Nodes
    tb_c1, _, _ = svgkit.textbox(530, 128, "Клієнт 1\nДрайвер VFS\n(NFS/CephFS)", size=9, fill="#f1f5f9", stroke="#64748b")
    tb_c2, _, _ = svgkit.textbox(670, 128, "Клієнт 2\nДрайвер VFS\n(NFS/CephFS)", size=9, fill="#f1f5f9", stroke="#64748b")
    tb_c3, _, _ = svgkit.textbox(810, 128, "Клієнт 3\nДрайвер VFS\n(NFS/CephFS)", size=9, fill="#f1f5f9", stroke="#64748b")
    frags.extend([tb_c1, tb_c2, tb_c3])

    # Metadata & Storage Servers
    tb_mds, _, _ = svgkit.textbox(575, 215, "Сервер метаданих (MDS)\nКерування простором імен", size=9, fill="#fee2e2", stroke="#dc2626")
    tb_osd, _, _ = svgkit.textbox(765, 215, "Вузли зберігання (OSD)\nОбслуговування блоків", size=9, fill="#fee2e2", stroke="#dc2626")
    frags.extend([tb_mds, tb_osd])

    # Network client connections
    frags.append(svgkit.arrow(530, 155, 565, 195, color="#dc2626", sw=1.5))
    frags.append(svgkit.arrow(650, 155, 595, 195, color="#dc2626", sw=1.5))
    frags.append(svgkit.arrow(690, 155, 745, 195, color="#dc2626", sw=1.5))
    frags.append(svgkit.arrow(810, 155, 775, 195, color="#dc2626", sw=1.5))

    # Backend Disks
    tb_disks, _, _ = svgkit.textbox(670, 305, "Локальні диски серверів зберігання\nПрямий доступ клієнтів до блоків ВІДСУТНІЙ", size=9.5, fill="#f1f5f9", stroke="#64748b", bold=True)
    frags.append(tb_disks)

    frags.append(svgkit.arrow(575, 235, 630, 285, color="#64748b", sw=1.5))
    frags.append(svgkit.arrow(765, 235, 710, 285, color="#64748b", sw=1.5))

    out_path = os.path.join(img_dir, "shared-disk-vs-distributed-fs.svg")
    svgkit.render(out_path, 900, 375, *frags)

def generate_dlm_invalidation_flow():
    if not svgkit:
        return
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    frags = []

    # Title
    frags.append(svgkit.text(450, 25, "Когерентність Розподіленого Кешу: Протокол BAST/CAST та Інвалідація", size=14, bold=True, anchor="middle", color="#1a252f"))

    # Four Columns: Node A, DLM (Lockspace), Node B, Shared LUN
    tb_col_a, _, _ = svgkit.textbox(120, 60, "Вузол A (Утримує EX-блокування)", size=10.5, fill="#dbeafe", stroke="#2563eb", bold=True)
    tb_col_dlm, _, _ = svgkit.textbox(370, 60, "DLM (Distributed Lock Manager)", size=10.5, fill="#fef3c7", stroke="#d97706", bold=True)
    tb_col_b, _, _ = svgkit.textbox(620, 60, "Вузол B (Запитує читання SH)", size=10.5, fill="#dbeafe", stroke="#2563eb", bold=True)
    tb_col_disk, _, _ = svgkit.textbox(820, 60, "Спільний LUN (Диск)", size=10.5, fill="#dcfce7", stroke="#16a34a", bold=True)
    frags.extend([tb_col_a, tb_col_dlm, tb_col_b, tb_col_disk])

    # Vertical lifelines - segmented to avoid passing through boxes
    # Node A lifeline: 75 -> 180, and 230 -> 440
    frags.append(svgkit.line(120, 75, 120, 180, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(svgkit.line(120, 230, 120, 440, color="#94a3b8", sw=1.5, dash="4,4"))

    # DLM lifeline: 75 -> 440
    frags.append(svgkit.line(370, 75, 370, 440, color="#94a3b8", sw=1.5, dash="4,4"))

    # Node B lifeline: 75 -> 350, and 400 -> 440
    frags.append(svgkit.line(620, 75, 620, 350, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(svgkit.line(620, 400, 620, 440, color="#94a3b8", sw=1.5, dash="4,4"))

    # Disk lifeline: 75 -> 440
    frags.append(svgkit.line(820, 75, 820, 440, color="#94a3b8", sw=1.5, dash="4,4"))

    # Step 1: Node B requests SH lock
    frags.append(svgkit.arrow(620, 110, 370, 110, color="#2563eb", sw=1.8))
    frags.append(svgkit.text(495, 102, "1. Запит блокування: lock(inode_42, mode=SH)", size=9.5, anchor="middle", color="#1e40af"))

    # Step 2: DLM detects conflict and sends BAST to Node A
    frags.append(svgkit.arrow(370, 150, 120, 150, color="#d97706", sw=1.8))
    frags.append(svgkit.text(245, 142, "2. BAST: Потрібно понизити EX → SH", size=9.5, anchor="middle", color="#b45309", bold=True))

    # Step 3: Node A flushes dirty pages to Disk
    tb_flush, _, _ = svgkit.textbox(120, 205, "Скидання кешу:\nfilemap_write_and_wait()\n(Dirty Pages → Disk)", size=9, fill="#fee2e2", stroke="#dc2626")
    frags.append(tb_flush)

    frags.append(svgkit.arrow(120, 240, 820, 240, color="#dc2626", sw=1.8))
    frags.append(svgkit.text(470, 232, "3. Запис брудних сторінок та оновлення метаданих на диск", size=9.5, anchor="middle", color="#991b1b"))

    # Step 4: Node A acknowledges demote to DLM
    frags.append(svgkit.arrow(120, 280, 370, 280, color="#16a34a", sw=1.8))
    frags.append(svgkit.text(245, 272, "4. Підтвердження пониження (EX → SH)", size=9.5, anchor="middle", color="#15803d"))

    # Step 5: DLM sends CAST to Node B
    frags.append(svgkit.arrow(370, 320, 620, 320, color="#16a34a", sw=1.8))
    frags.append(svgkit.text(495, 312, "5. CAST: Блокування SH успішно надано", size=9.5, anchor="middle", color="#15803d", bold=True))

    # Step 6: Node B invalidates old page cache & reads from Disk
    tb_inv, _, _ = svgkit.textbox(620, 375, "Інвалідація локального кешу:\ninvalidate_inode_pages2()\n(Очищення старих сторінок у RAM)", size=9, fill="#fef3c7", stroke="#d97706")
    frags.append(tb_inv)

    frags.append(svgkit.arrow(620, 415, 820, 415, color="#2563eb", sw=1.8))
    frags.append(svgkit.text(720, 407, "6. Читання свіжих блоків із LUN", size=9.5, anchor="middle", color="#1e40af"))

    out_path = os.path.join(img_dir, "dlm-ast-invalidation-flow.svg")
    svgkit.render(out_path, 900, 460, *frags)

def generate_per_node_journal_recovery():
    if not svgkit:
        return
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    frags = []

    # Title
    frags.append(svgkit.text(450, 25, "Розподілене Журналювання та Відновлення Після Збою (Per-Node Journal Replay)", size=14, bold=True, anchor="middle", color="#1a252f"))

    # LUN Layout Structure (top section)
    frags.append(svgkit.rect(40, 50, 820, 110, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(svgkit.text(450, 70, "Структура Розділів на Спільному Блоковому Диску (LUN)", size=11, bold=True, anchor="middle", color="#0f172a"))

    # Blocks in LUN
    tb_sb, _, _ = svgkit.textbox(105, 115, "Суперблок\n(Superblock)", size=9.5, fill="#e2e8f0", stroke="#64748b")
    tb_j0, _, _ = svgkit.textbox(235, 115, "Журнал Вузла 1\n(Journal 0 - Node 1)", size=9.5, fill="#dcfce7", stroke="#16a34a")
    tb_j1, _, _ = svgkit.textbox(375, 115, "Журнал Вузла 2\n(Journal 1 - Node 2)\n[АВАРІЙНИЙ СТАН]", size=9, fill="#fee2e2", stroke="#dc2626", bold=True)
    tb_rg, _, _ = svgkit.textbox(535, 115, "Resource Groups\nБітові карти виділення", size=9.5, fill="#fef3c7", stroke="#d97706")
    tb_data, _, _ = svgkit.textbox(730, 115, "Таблиці Inodes та Блоки Даних\n(Файли та каталоги)", size=9.5, fill="#e0f2fe", stroke="#0284c7")
    frags.extend([tb_sb, tb_j0, tb_j1, tb_rg, tb_data])

    # Steps of Recovery (bottom section)
    frags.append(svgkit.rect(40, 180, 820, 190, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(svgkit.text(450, 202, "Алгоритм Відновлення Метаданих Мертвого Вузла (Journal Replay Flow)", size=12, bold=True, anchor="middle", color="#0f172a"))

    # Step 1 box
    tb_s1, _, _ = svgkit.textbox(130, 260, "1. Збій Вузла 2\nВтрата зв'язку / паніка.\nCorosync фіксує вибуття.", size=9, fill="#fee2e2", stroke="#dc2626")
    # Step 2 box
    tb_s2, _, _ = svgkit.textbox(305, 260, "2. STONITH / Fencing\nАпаратне відсікання\nВузол 2 знеструмлено.", size=9, fill="#fee2e2", stroke="#dc2626", bold=True)
    # Step 3 box
    tb_s3, _, _ = svgkit.textbox(480, 260, "3. Захоплення Journal 1\nВузол 1 бере EX-блок\nна glock журналу 1.", size=9, fill="#fef3c7", stroke="#d97706")
    # Step 4 box
    tb_s4, _, _ = svgkit.textbox(655, 260, "4. Replay Транзакцій\nВузол 1 накочує redo-лог\nу спільні Inodes / RG.", size=9, fill="#dcfce7", stroke="#16a34a", bold=True)
    # Step 5 box
    tb_s5, _, _ = svgkit.textbox(795, 260, "5. Фініш\nЖурнал чистий.\nБлокування знято.", size=9, fill="#dcfce7", stroke="#16a34a")

    frags.extend([tb_s1, tb_s2, tb_s3, tb_s4, tb_s5])

    # Connecting arrows between recovery steps
    frags.append(svgkit.arrow(190, 260, 235, 260, color="#dc2626", sw=1.8))
    frags.append(svgkit.arrow(375, 260, 410, 260, color="#d97706", sw=1.8))
    frags.append(svgkit.arrow(550, 260, 580, 260, color="#16a34a", sw=1.8))
    frags.append(svgkit.arrow(730, 260, 755, 260, color="#16a34a", sw=1.8))

    # Summary note below
    frags.append(svgkit.text(450, 345, "Інваріант: Replay не починається до отримання підтвердження STONITH (захист від паралельного запису).", size=9.5, italic=True, anchor="middle", color="#475569"))

    out_path = os.path.join(img_dir, "per-node-journal-recovery.svg")
    svgkit.render(out_path, 900, 390, *frags)

def generate_split_brain_and_fencing():
    if not svgkit:
        return
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    frags = []

    # Title
    frags.append(svgkit.text(450, 25, "Розрив Мережі (Split-Brain), Кворум та Апаратна Ізоляція STONITH", size=14, bold=True, anchor="middle", color="#1a252f"))

    # Left: Quorum Side (Nodes 1 and 2)
    frags.append(svgkit.rect(30, 50, 380, 280, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(svgkit.text(220, 75, "Сегмент A: Є КВОРУМ (2 з 3 вузлів)", size=11.5, bold=True, anchor="middle", color="#15803d"))
    frags.append(svgkit.text(220, 92, "Кворум = floor(3/2) + 1 = 2 (Більшість збережена)", size=9.5, anchor="middle", color="#166534"))

    tb_na1, _, _ = svgkit.textbox(130, 140, "Вузол 1 (Node 1)\nСтан: Active", size=9.5, fill="#dcfce7", stroke="#16a34a")
    tb_na2, _, _ = svgkit.textbox(310, 140, "Вузол 2 (Node 2)\nСтан: Active", size=9.5, fill="#dcfce7", stroke="#16a34a")
    frags.extend([tb_na1, tb_na2])

    tb_fence_action, _, _ = svgkit.textbox(220, 230, "Дія Сегменту A:\n1. Зафіксовано втрату Вузла 3\n2. Виклик STONITH через IPMI/iLO\n3. Блокування доступу до SAN", size=9, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(tb_fence_action)

    # Middle: Broken Network Interconnect
    frags.append(svgkit.rect(425, 110, 50, 80, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    frags.append(svgkit.text(450, 140, "РОЗРИВ", size=9, bold=True, anchor="middle", color="#dc2626"))
    frags.append(svgkit.text(450, 155, "МЕРЕЖІ", size=9, bold=True, anchor="middle", color="#dc2626"))
    frags.append(svgkit.line(430, 115, 470, 185, color="#dc2626", sw=2))

    # Right: Non-Quorum Side (Node 3)
    frags.append(svgkit.rect(490, 50, 380, 280, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=6))
    frags.append(svgkit.text(680, 75, "Сегмент B: НЕМАЄ КВОРУМУ (1 з 3)", size=11.5, bold=True, anchor="middle", color="#991b1b"))
    frags.append(svgkit.text(680, 92, "1 < 2 → Вузол втрачає право на запис", size=9.5, anchor="middle", color="#991b1b"))

    tb_nb3, _, _ = svgkit.textbox(680, 140, "Вузол 3 (Node 3)\n[ІЗОЛЬОВАНИЙ ВУЗОЛ]", size=9.5, fill="#fee2e2", stroke="#dc2626", bold=True)
    frags.append(tb_nb3)

    tb_fence_target, _, _ = svgkit.textbox(680, 230, "Примусове Знеструмлення:\nSTONITH вимикає живлення\nабо SCSI-3 PR скидає реєстрацію.\nЗапис унеможливлено!", size=9, fill="#fee2e2", stroke="#dc2626")
    frags.append(tb_fence_target)

    # Fencing arrow from segment A to segment B
    frags.append(svgkit.arrow(320, 230, 580, 230, color="#dc2626", sw=2))
    frags.append(svgkit.text(450, 218, "IPMI Power OFF", size=9, bold=True, anchor="middle", color="#dc2626"))

    # Bottom SAN Storage Access Box
    tb_bot_san, _, _ = svgkit.textbox(450, 380, "Спільний Блоковий LUN (SAN Fabric)\nСегмент A: Доступ ДОЗВОЛЕНО | Вузол 3: Доступ ЗАБЛОКОВАНО", size=10, fill="#dcfce7", stroke="#16a34a", bold=True)
    frags.append(tb_bot_san)

    frags.append(svgkit.arrow(220, 290, 320, 355, color="#16a34a", sw=1.8))
    frags.append(svgkit.line(680, 290, 580, 355, color="#dc2626", sw=1.8, dash="3,3"))

    out_path = os.path.join(img_dir, "split-brain-and-fencing.svg")
    svgkit.render(out_path, 900, 420, *frags)

if __name__ == "__main__":
    generate_shared_disk_architecture()
    generate_dlm_invalidation_flow()
    generate_per_node_journal_recovery()
    generate_split_brain_and_fencing()
    print("All figures generated successfully.")
