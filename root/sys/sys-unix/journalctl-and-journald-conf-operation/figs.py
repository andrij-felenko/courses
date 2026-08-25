# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"
RED_FILL = "#fdeae8"


# ── 1. Архітектура підсистеми systemd-journald ──────────────────────────────
def fig_journald_architecture():
    W, H = 1200, 540
    p = []

    p.append(text(600, 36, "Архітектурний потік даних підсистеми systemd-journald", size=17, bold=True))

    # Джерела входу
    p.append(rect(40, 70, 310, 430, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(195, 96, "Джерела логів", size=15, bold=True))

    p.append(fitbox(60, 120, 270, 56, "Процеси служб\nstdout / stderr (fd 1, 2)", size=13, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(60, 196, 270, 56, "Рідний сокет journald\n/run/systemd/journal/socket", size=13, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(60, 272, 270, 56, "Сумісність із syslog\n/dev/log (syslog() API)", size=13, fill=WARM_FILL, stroke=MUTED))
    p.append(fitbox(60, 348, 270, 56, "Буфер ядра Linux\n/dev/kmsg (printk)", size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(60, 424, 270, 56, "Події аудиту й безпеки\nNetlink audit socket", size=13, fill=GREEN_FILL, stroke=FIELD))

    # Ядро / Демон
    p.append(fitbox(430, 215, 230, 140, "systemd-journald\n\n- Валідація SO_PASSCRED\n- Дочитання з /proc\n- Буферизація в пам'яті", size=14, bold=True, fill=WARM_FILL, stroke=MUTED))

    # Стрелки от источников к демону
    p.append(arrow(330, 148, 430, 240))
    p.append(arrow(330, 224, 430, 260))
    p.append(arrow(330, 300, 430, 285))
    p.append(arrow(330, 376, 430, 310))
    p.append(arrow(330, 452, 430, 330))

    # Сховище
    p.append(rect(730, 70, 430, 210, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(945, 96, "Дискове сховище (.journal)", size=15, bold=True))
    p.append(fitbox(750, 120, 390, 60, "Оперативне (Volatile)\n/run/log/journal/ (tmpfs)", size=13, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(750, 200, 390, 60, "Постійне (Persistent)\n/var/log/journal/ (ext4/xfs/btrfs)", size=13, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(660, 285, 730, 175))

    # Споживачі
    p.append(rect(730, 310, 430, 190, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(945, 336, "Споживачі та клієнти", size=15, bold=True))
    p.append(fitbox(750, 360, 185, 120, "Утиліта journalctl\n(інтерактивний\nперегляд, JSON,\nфільтрація)", size=13, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(955, 360, 185, 120, "Syslog / Forwarding\nrsyslogd, fluentd,\nlogstash, vector", size=13, fill=GREY_FILL, stroke=MUTED))

    p.append(arrow(945, 280, 945, 310))

    render(os.path.join(IMG, 'journald-architecture.svg'), W, H, *p,
           title="Архітектура підсистеми systemd-journald")


# ── 2. Формування довірених полів через SO_PASSCRED ────────────────────────
def fig_trusted_fields_flow():
    W, H = 1200, 520
    p = []

    p.append(text(600, 36, "Механізм формування довірених полів запису в journald", size=17, bold=True))

    # Процес
    p.append(fitbox(50, 80, 300, 110, "Клієнтський процес (PID 2410)\n\nНадсилає датаграму:\nMESSAGE=Database query failed\nPRIORITY=3\nERRNO=111", size=13, fill=BLUE_FILL, stroke=NEG))

    # Сокет ядра
    p.append(fitbox(430, 80, 340, 110, "Ядро Linux (AF_UNIX socket)\n\nДодає SCM_CREDENTIALS:\nstruct ucred { pid=2410, uid=1000, gid=1000 }", size=13, fill=GREEN_FILL, stroke=FIELD))

    # Демон
    p.append(fitbox(850, 80, 300, 110, "systemd-journald\n\nОтримує датаграму та ucred,\nпотім читає /proc/2410/", size=13, fill=WARM_FILL, stroke=MUTED))

    p.append(arrow(350, 135, 430, 135))
    p.append(arrow(770, 135, 850, 135))

    # Файли /proc
    p.append(fitbox(430, 240, 340, 90, "Віртуальна файлова система /proc/2410/\n\n/proc/2410/cgroup → system.slice/db.service\n/proc/2410/exe    → /usr/bin/postgres\n/proc/2410/cmdline → postgres: worker", size=13, fill=GREY_FILL, stroke=MUTED))

    p.append(arrow(850, 165, 770, 270))

    # Підсумковий запис
    p.append(rect(50, 360, 1100, 130, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(600, 382, "Збірне підсумкове повідомлення журналу", size=14, bold=True))

    p.append(fitbox(70, 398, 510, 78, "Поля відправника (невірифіковані):\nMESSAGE=Database query failed\nPRIORITY=3\nERRNO=111", size=12, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(600, 398, 530, 78, "Довірені метаполя ядра та /proc (захищені від підробки):\n_PID=2410  _UID=1000  _GID=1000\n_SYSTEMD_UNIT=db.service  _EXE=/usr/bin/postgres  _TRANSPORT=journal", size=12, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(1000, 190, 1000, 360))

    render(os.path.join(IMG, 'trusted-fields-flow.svg'), W, H, *p,
           title="Формування довірених полів через SO_PASSCRED")


# ── 3. Індексація та об'єктна структура файлу .journal ──────────────────────
def fig_journal_file_indexing():
    W, H = 1200, 540
    p = []

    p.append(text(600, 36, "Об'єктна структура та індексація бінарного файлу .journal", size=17, bold=True))

    # Header
    p.append(fitbox(50, 80, 240, 130, "Header (Заголовок)\n\nMagic: LPKSHHRH\nBoot ID: 4f2a89c...\nFile Sequence No\nPointer to Hash Table", size=13, fill=WARM_FILL, stroke=MUTED))

    # Hash Table
    p.append(fitbox(340, 80, 240, 130, "OBJECT_HASH_TABLE\n\n[Hash 0x8a] ──┐\n[Hash 0x3f] ──┼─► Pointer\n[Hash 0xc1] ──┘", size=13, fill=GREY_FILL, stroke=MUTED))

    # Data Objects (De-duplicated)
    p.append(rect(630, 70, 520, 200, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(890, 95, "Об'єкти даних (OBJECT_DATA) — дедупліковані", size=14, bold=True))

    p.append(fitbox(650, 115, 480, 42, "DATA 1: _SYSTEMD_UNIT=nginx.service (Hash 0x3f)", size=12, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(650, 165, 480, 42, "DATA 2: PRIORITY=3 (Hash 0x8a)", size=12, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(650, 215, 480, 42, "DATA 3: MESSAGE=Connection timeout (Hash 0xc1)", size=12, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(290, 145, 340, 145))
    p.append(arrow(580, 145, 650, 136))

    # Entry Objects & Entry Arrays
    p.append(rect(50, 310, 1100, 200, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(80, 332, "Записи подій (OBJECT_ENTRY) та списки зв'язків (OBJECT_ENTRY_ARRAY)", size=14, bold=True, anchor="start"))

    p.append(fitbox(80, 360, 320, 125, "OBJECT_ENTRY #501\n\nRealtime: 1723593600000\nMonotonic: 4891204\nSequence: 501\nArray of pointers to DATA 1, 2, 3", size=12, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(440, 360, 320, 125, "OBJECT_ENTRY #502\n\nRealtime: 1723593601500\nMonotonic: 4892704\nSequence: 502\nArray of pointers to DATA 1, 3", size=12, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(800, 360, 320, 125, "OBJECT_ENTRY_ARRAY\n\nДвозв'язний масив для\nшвидкого пошуку та\nітерації назад/вперед", size=12, fill=WARM_FILL, stroke=MUTED))

    p.append(arrow(890, 260, 240, 360))
    p.append(arrow(890, 260, 600, 360))
    p.append(arrow(400, 422, 440, 422))
    p.append(arrow(760, 422, 800, 422))

    render(os.path.join(IMG, 'journal-file-indexing.svg'), W, H, *p,
           title="Об'єктна структура бінарного файлу .journal")


# ── 4. Захист цілісності FSS (Forward Secure Sealing) ───────────────────────
def fig_fss_tree_sealing():
    W, H = 1200, 500
    p = []

    p.append(text(600, 36, "Математична схема запечатування журналів FSS (Forward Secure Sealing)", size=17, bold=True))

    # Offline Master Key
    p.append(fitbox(50, 90, 260, 90, "Майстер-ключ K_master\n(Offline / Безпечне сховище)\n\nСгенеровано при setup-keys", size=13, fill=WARM_FILL, stroke=MUTED))

    # Epoches
    p.append(fitbox(370, 90, 240, 110, "Епоха t = 0 (0-15 хв)\n\nКлюч підпису K_0\nПідпис подій епохи t0\nHASH(K_0) записано", size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(660, 90, 240, 110, "Епоха t = 1 (15-30 хв)\n\nK_1 = HMAC(K_0, 'SEAL')\nK_0 знищено з пам'яті!\nПідпис подій епохи t1", size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(950, 90, 200, 110, "Епоха t = 2 (30-45 хв)\n\nK_2 = HMAC(K_1, 'SEAL')\nK_1 знищено!\nПідпис подій t2", size=13, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(310, 135, 370, 135))
    p.append(arrow(610, 145, 660, 145))
    p.append(arrow(900, 145, 950, 145))

    # Threat scenario
    p.append(rect(50, 250, 1100, 210, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(600, 275, "Сценарій зламу системи в епоху t = 2", size=15, bold=True, color="#c0392b"))

    p.append(fitbox(80, 305, 480, 130, "Зловмисник отримує root у t = 2:\n\n- Бачить поточний ключ K_2 в ОЗП\n- МАТЕМАТИЧНО НЕ МОЖЕ обчислити K_1 або K_0,\n  бо HMAC-SHA256 є однонаправленою функцією!", size=13, fill=RED_FILL, stroke="#c0392b"))

    p.append(fitbox(610, 305, 510, 130, "Результат верифікації journalctl --verify:\n\n- Спроба підробити записи епох t0 або t1 буде викрита!\n- Офлайн K_master дозволяє перевірити цілісність\n  усього ланцюжка від початку створення.", size=13, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'fss-tree-sealing.svg'), W, H, *p,
           title="Схема запечатування журналів FSS")


# ── 5. Пайплайн фільтрації та форматування journalctl ────────────────────────
def fig_journalctl_filter_pipeline():
    W, H = 1200, 480
    p = []

    p.append(text(600, 36, "Пайплайн вибірки, фільтрації та форматування утилітою journalctl", size=17, bold=True))

    # Inputs
    p.append(fitbox(50, 90, 220, 160, "Файли сховища\n\n/var/log/journal/*\n/run/log/journal/*\n\nсистемний + юзерські\nбінарні журналі", size=13, fill=GREY_FILL, stroke=MUTED))

    # Filtering Engine
    p.append(rect(320, 80, 520, 360, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(580, 105, "Механізм фільтрації (Journal Match Engine)", size=15, bold=True))

    p.append(fitbox(340, 125, 480, 45, "Фільтр за джерелом / юнітом: -u nginx.service", size=12, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(340, 180, 480, 45, "Фільтр за часом: --since '1 hour ago' --until 'now'", size=12, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(340, 235, 480, 45, "Фільтр за пріоритетом: -p err..emerg (PRIORITY <= 3)", size=12, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(340, 290, 480, 45, "Сесія / завантаження: -b -1 (попередній boot)", size=12, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(340, 345, 480, 75, "Довільні точні співпадіння по полях:\n_PID=1234  _TRANSPORT=kernel  _COMM=sshd", size=12, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(270, 170, 320, 170))

    # Formatter Output
    p.append(rect(890, 80, 260, 360, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(1020, 105, "Рендерер виводу (-o)", size=15, bold=True))

    p.append(fitbox(910, 130, 220, 50, "-o short-precise\n(стандартний людський)", size=12, fill=WARM_FILL, stroke=MUTED))
    p.append(fitbox(910, 190, 220, 50, "-o json-pretty\n(для аналізу та парсингу)", size=12, fill=WARM_FILL, stroke=MUTED))
    p.append(fitbox(910, 250, 220, 50, "-o verbose\n(усі поля запису)", size=12, fill=WARM_FILL, stroke=MUTED))
    p.append(fitbox(910, 310, 220, 50, "-o cat\n(чистий текст MESSAGE)", size=12, fill=WARM_FILL, stroke=MUTED))
    p.append(fitbox(910, 370, 220, 50, "-o export\n(бінарний потік)", size=12, fill=WARM_FILL, stroke=MUTED))

    p.append(arrow(840, 260, 890, 260))

    render(os.path.join(IMG, 'journalctl-filter-pipeline.svg'), W, H, *p,
           title="Пайплайн вибірки та фільтрації journalctl")


def main():
    fig_journald_architecture()
    fig_trusted_fields_flow()
    fig_journal_file_indexing()
    fig_fss_tree_sealing()
    fig_journalctl_filter_pipeline()
    print("All figures generated successfully.")

if __name__ == '__main__':
    main()
