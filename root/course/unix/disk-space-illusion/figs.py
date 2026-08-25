# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми 'Місце скінчилося: df проти du, inode і видалений відкритий файл'."""

import sys, os

# 4 рівні вгору до кореня репо, де лежить scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_df_vs_du():
    """Схема 1: Анатомія розбіжності між df (statvfs) та du (stat/readdir)."""
    w, h = 980, 560
    frags = []

    # Головна підкладка
    frags.append(rect(20, 20, 940, 520, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(490, 48, "ДВА ШЛЯХИ ОБЛІКУ ДИСКОВОГО ПРОСТОРУ: СУПЕРБЛОК ПРОТИ ДЕРЕВА КАТАЛОГІВ", size=14, color="#0f172a", bold=True))

    # Ліва колонка: Утиліта df
    frags.append(rect(40, 75, 430, 445, fill="#ffffff", stroke="#3b82f6", sw=1.6, rx=6))
    frags.append(text(255, 102, "УТИЛІТА df (Disk Free)", size=13, color="#1d4ed8", bold=True))
    frags.append(text(255, 120, "Системний виклик statvfs() / statfs()", size=11, color="#64748b", italic=True))

    frags.append(fitbox(55, 138, 400, 60, "Запит до ядра VFS:\nvfs_statfs() ──> sb->s_op->statfs()\nМиттєве опитування структури суперблока", size=11, pad=6, fill="#eff6ff", stroke="#93c5fd"))
    frags.append(arrow(255, 198, 255, 222, color="#3b82f6", sw=1.6))

    frags.append(fitbox(55, 222, 400, 80, "Суперблок файлової системи (struct super_block)\n• Глобальна бітова карта виділення блоків\n• Лічильники: s_free_blocks_count, s_free_inodes_count\n• Облік резерву суперкористувача (s_r_blocks_count)", size=10.5, pad=6, fill="#dbeafe", stroke="#3b82f6", bold=False))
    frags.append(arrow(255, 302, 255, 326, color="#3b82f6", sw=1.6))

    frags.append(fitbox(55, 326, 400, 85, "Що бачить df:\n[+] Усі зайняті блоки носія (100% заповнення)\n[+] Відкриті видалені файли ((deleted) втримують блоки)\n[+] Приховані дані під точками монтування\n[+] Резерв 5% root (f_bavail < f_bfree)", size=10.5, pad=6, fill="#f0fdf4", stroke="#22c55e", color="#166534"))

    frags.append(fitbox(55, 420, 400, 85, "Швидкість та межі:\n• Час виконання: O(1) (миттєво для будь-якого терабайтного диска)\n• Сліпа зона: не знає, які саме файли чи каталоги зайняли місце", size=10.5, pad=6, fill="#f8fafc", stroke="#94a3b8", color="#334155"))

    # Права колонка: Утиліта du
    frags.append(rect(510, 75, 430, 445, fill="#ffffff", stroke="#f59e0b", sw=1.6, rx=6))
    frags.append(text(725, 102, "УТИЛІТА du (Disk Usage)", size=13, color="#b45309", bold=True))
    frags.append(text(725, 120, "Системні виклики readdir() + fstatat() / stat()", size=11, color="#64748b", italic=True))

    frags.append(fitbox(525, 138, 400, 60, "Рекурсивний обхід дерева каталогів:\nopenat() ──> getdents64() ──> newfstatat()\nПослідовне сканування кожного видимого запису dirent", size=11, pad=6, fill="#fffbeb", stroke="#fcd34d"))
    frags.append(arrow(725, 198, 725, 222, color="#f59e0b", sw=1.6))

    frags.append(fitbox(525, 222, 400, 80, "Атрибути кожного знайденого файлу (struct stat)\n• st_blocks: кількість виділених секторів по 512 байтів\n• Хеш-таблиця перевірки inode/dev (щоб не дублювати hardlinks)\n• Підсумовування: загальний розмір = ∑ (st_blocks × 512)", size=10.5, pad=6, fill="#fef3c7", stroke="#f59e0b"))
    frags.append(arrow(725, 302, 725, 326, color="#f59e0b", sw=1.6))

    frags.append(fitbox(525, 326, 400, 85, "Що бачить du:\n[−] Сліпа до видалених відкритих файлів (немає запису в каталозі)\n[−] Сліпа до даних, закритих поверх іншим монтуванням\n[−] Не знає про резервні блоки root\n[=] Показує лише 12 ГБ із 200 ГБ зайнятого простору!", size=10.5, pad=6, fill="#fef2f2", stroke="#ef4444", color="#991b1b"))

    frags.append(fitbox(525, 420, 400, 85, "Швидкість та межі:\n• Час виконання: O(N) (залежить від мільйонів файлів та I/O навантаження)\n• Перевага: показує точні шляхи до видимих великих файлів", size=10.5, pad=6, fill="#f8fafc", stroke="#94a3b8", color="#334155"))

    render(os.path.join(OUT_DIR, "df-vs-du-divergence.svg"), w, h, *frags)


def fig_deleted_open_file():
    """Схема 2: Механізм утримання дискових блоків відкритим видаленим файлом."""
    w, h = 980, 520
    frags = []

    frags.append(rect(20, 20, 940, 480, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(490, 48, "АНАТОМІЯ ФАНТОМНОГО ФАЙЛУ: РОЗРИВ МІЖ КАТАЛОГОМ, ДЕСКРИПТОРОМ ТА БЛОКАМИ", size=14, color="#0f172a", bold=True))

    # Секція 1: Простір користувача / Процес
    frags.append(rect(40, 75, 270, 405, fill="#ffffff", stroke="#9333ea", sw=1.6, rx=6))
    frags.append(text(175, 102, "ПРОЦЕС (User Space)", size=12, color="#7e22ce", bold=True))
    frags.append(fitbox(55, 120, 240, 70, "Процес-демон (PID: 28411)\n• Виконує активний запис у лог\n• Відкрив файл через open()\n• Таблиця FD процесу", size=10.5, pad=5, fill="#faf5ff", stroke="#c084fc"))

    frags.append(arrow(175, 190, 175, 215, color="#9333ea", sw=1.6))
    frags.append(fitbox(55, 215, 240, 80, "Файловий дескриптор:\nFD = 3 (в пам'яті процесу)\nПосилання у псевдо-ФС:\n/proc/28411/fd/3 ──>\n'/var/log/app.log (deleted)'", size=10, pad=5, fill="#f3e8ff", stroke="#9333ea", bold=True))

    frags.append(arrow(175, 295, 175, 320, color="#9333ea", sw=1.6))
    frags.append(fitbox(55, 320, 240, 145, "Діагностика через lsof:\n$ lsof +L1\nCOMMAND: java\nPID: 28411\nFD: 3w\nNLINK: 0 (немає імен!)\nSIZE: 180 ГБ\nNAME: /var/log/app.log (deleted)", size=9.5, pad=5, fill="#f8fafc", stroke="#a855f7"))

    # Секція 2: Простір ядра / VFS
    frags.append(rect(345, 75, 290, 405, fill="#ffffff", stroke="#2563eb", sw=1.6, rx=6))
    frags.append(text(490, 102, "ЯДРО: VFS ТА ІНОД", size=12, color="#1d4ed8", bold=True))

    frags.append(fitbox(360, 120, 260, 70, "Каталог /var/log/\nПісля виклику unlink('app.log'):\nЗапис (dirent) ПОВНІСТЮ ВИДАЛЕНО\ndu більше не знаходить файл!", size=10, pad=5, fill="#fef2f2", stroke="#ef4444", color="#991b1b"))

    frags.append(arrow(490, 190, 490, 215, color="#2563eb", sw=1.6))
    frags.append(fitbox(360, 215, 260, 80, "struct file (в RAM ядра)\n• f_count = 1 (утримується PID 28411)\n• f_pos = 193 273 528 320\n• Вказує на struct inode #88219", size=10.5, pad=5, fill="#eff6ff", stroke="#3b82f6"))

    frags.append(arrow(490, 295, 490, 320, color="#2563eb", sw=1.6))
    frags.append(fitbox(360, 320, 260, 145, "struct inode #88219 (Ext4)\n• i_nlink = 0  (видалено з каталогу!)\n• i_count = 1  (тримає struct file)\n• Розмір: 180 ГБ\n• Дерево екстентів: активне!\n\nУМОВА ОЧИЩЕННЯ:\n(i_nlink == 0) && (i_count == 0)\nПоки i_count > 0, блоки блоковані!", size=10, pad=5, fill="#fefce8", stroke="#eab308", bold=True))

    # Секція 3: Фізичний диск / Блоки
    frags.append(rect(670, 75, 270, 405, fill="#ffffff", stroke="#059669", sw=1.6, rx=6))
    frags.append(text(805, 102, "ДИСК ТА СУПЕРБЛОК", size=12, color="#047857", bold=True))

    frags.append(fitbox(685, 120, 240, 70, "Бітова карта блоків (Ext4)\nБлоки #40102 .. #47219030\nПозначені бітами '1' (ЗАЙНЯТІ)\nЯдро не має права їх віддати!", size=10, pad=5, fill="#ecfdf5", stroke="#10b981"))

    frags.append(arrow(805, 190, 805, 215, color="#059669", sw=1.6))
    frags.append(fitbox(685, 215, 240, 110, "Показники df:\n• Загалом: 200 ГБ\n• Зайнято: 198 ГБ (100%)\n• Вільних блоків: 0\n• Помилка запису: ENOSPC\n(No space left on device)", size=10.5, pad=5, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))

    frags.append(arrow(805, 325, 805, 345, color="#059669", sw=1.6))
    frags.append(fitbox(685, 345, 240, 120, "Хірургічне лікування:\n$ : > /proc/28411/fd/3\n(виклик ftruncate(3, 0))\nБлоки звільняються МИТТЄВО,\nпроцес продовжує працювати без аварійного перезапуску!", size=10, pad=5, fill="#f0fdf4", stroke="#16a34a", color="#15803d", bold=True))

    # Зв'язки між секціями
    frags.append(arrow(295, 255, 360, 255, color="#2563eb", sw=1.8))
    frags.append(arrow(620, 390, 685, 155, color="#059669", sw=1.8))

    render(os.path.join(OUT_DIR, "deleted-file-fd-reference.svg"), w, h, *frags)


def fig_mount_occlusion():
    """Схема 3: Приховування файлів під точкою монтування (Over-mounting)."""
    w, h = 980, 500
    frags = []

    frags.append(rect(20, 20, 940, 460, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(490, 48, "ПРИХОВУВАННЯ ДАНИХ ПІД ТОЧКОЮ МОНТУВАННЯ (OVER-MOUNTING)", size=14, color="#0f172a", bold=True))

    # Лівий блок: Стан ДО монтування
    frags.append(rect(40, 75, 430, 385, fill="#ffffff", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(255, 102, "1. СТАН ДО МОНТУВАННЯ ДИСКА", size=12, color="#334155", bold=True))

    frags.append(fitbox(55, 120, 400, 80, "Коренева файлова система /dev/nvme0n1p2 (/)\nКаталог: /mnt/storage/\nУ каталог записано великий архів: backup.tar (60 ГБ)\nІнод #521902 належить кореневій ФС", size=10.5, pad=6, fill="#f1f5f9", stroke="#94a3b8"))

    frags.append(fitbox(55, 215, 400, 105, "Показники утиліт до монтування:\n• df -h / ──> Зайнято: 90 ГБ (включно з 60 ГБ backup.tar)\n• du -sh /mnt/storage ──> 60 ГБ\n\nУсе узгоджено: du та df показують однакові числа!", size=10.5, pad=6, fill="#f0fdf4", stroke="#22c55e", color="#166534"))

    frags.append(fitbox(55, 335, 400, 105, "Фізичний стан блоків:\nБлоки файлу backup.tar фізично записані у секторах /dev/nvme0n1p2.\nКаталоговий запис існує в dentry кореневої системи.", size=10, pad=6, fill="#ffffff", stroke="#cbd5e1"))

    # Правий блок: Стан ПІСЛЯ монтування поверх
    frags.append(rect(510, 75, 430, 385, fill="#ffffff", stroke="#dc2626", sw=1.6, rx=6))
    frags.append(text(725, 102, "2. ПІСЛЯ mount /dev/sdb1 /mnt/storage", size=12, color="#b91c1c", bold=True))

    frags.append(fitbox(525, 120, 400, 80, "Нова файлова система /dev/sdb1 змонтована поверх!\nVFS перенаправляє шлях /mnt/storage на корінь нового диска.\nПопередній вміст каталогу /mnt/storage/ СТАЄ НЕВИДИМИМ!", size=10.5, pad=6, fill="#fef2f2", stroke="#ef4444", color="#991b1b", bold=True))

    frags.append(fitbox(525, 215, 400, 105, "Ілюзія зникнення 60 Гігабайтів:\n• df -h / ──> Зайнято: 90 ГБ (60 ГБ НЕ звільнилися з кореня!)\n• du -sh /mnt/storage ──> 2 МБ (бачить лише новий порожній диск /dev/sdb1)\n• du -sh /* ──> 30 ГБ (не знаходить 60 ГБ прихованих даних!)", size=10.5, pad=6, fill="#fffbeb", stroke="#f59e0b", color="#92400e"))

    frags.append(fitbox(525, 335, 400, 105, "Як побачити й очистити приховане:\n1. Тимчасовий bind-mount кореня:\n   # mount --bind / /mnt/inspect_root\n2. Сканування без перекриття: du -sh /mnt/inspect_root/mnt/storage\n3. Видалення прихованого файлу через /mnt/inspect_root/...", size=9.8, pad=6, fill="#f0fdf4", stroke="#16a34a", color="#15803d", bold=True))

    render(os.path.join(OUT_DIR, "mount-point-occlusion.svg"), w, h, *frags)


def fig_reserved_and_inodes():
    """Схема 4: Вичерпання інодів (df -i) та резерв блоків root (5%)."""
    w, h = 980, 500
    frags = []

    frags.append(rect(20, 20, 940, 460, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(490, 48, "ВИЧЕРПАННЯ ІНОДІВ ТА ПАСТКА РЕЗЕРВНИХ БЛОКІВ EXT4", size=14, color="#0f172a", bold=True))

    # Ліва колонка: Вичерпання інодів (df -i)
    frags.append(rect(40, 75, 430, 385, fill="#ffffff", stroke="#ea580c", sw=1.6, rx=6))
    frags.append(text(255, 102, "ВИЧЕРПАННЯ ІНОДІВ (df -i)", size=12, color="#c2410c", bold=True))

    frags.append(fitbox(55, 120, 400, 75, "Фіксована таблиця інодів (Ext4):\nПід час форматування mkfs.ext4 виділяється фіксована кількість інодів (наприклад, 1 інод на 16 КБ диска). Всього: 6 553 600 шт.", size=10.5, pad=5, fill="#fff7ed", stroke="#fdba74"))

    frags.append(fitbox(55, 205, 400, 115, "Сценарій катастрофи: мільйони дрібних файлів\n• 6.5 млн сесій PHP (/var/lib/php/sessions)\n• Поштова черга postfix або кеш дрібних іконок по 100 байтів\n• Використано дискового простору: лише 4 ГБ із 100 ГБ (4%!)\n• Використано інодів: 6 553 600 / 6 553 600 (100%)", size=10, pad=5, fill="#fef2f2", stroke="#ef4444", color="#991b1b", bold=True))

    frags.append(fitbox(55, 330, 400, 115, "Наслідок та розв'язання:\n$ touch test.txt ──> touch: cannot touch: No space left on device\ndf -h: 96 ГБ ВІЛЬНО! | df -i: IUse% = 100% (ВІЛЬНИХ ІНОДІВ 0)\nПошук винуватця:\n$ find / -xdev -printf '%h\\n' | sort | uniq -c | sort -nr | head -n 10", size=9.5, pad=5, fill="#f8fafc", stroke="#94a3b8"))

    # Права колонка: Резервні блоки root (5%)
    frags.append(rect(510, 75, 430, 385, fill="#ffffff", stroke="#0284c7", sw=1.6, rx=6))
    frags.append(text(725, 102, "РЕЗЕРВНІ БЛОКИ ROOT (tune2fs -m)", size=12, color="#0369a1", bold=True))

    frags.append(fitbox(525, 120, 400, 75, "Структура дискового простору Ext4:\n┌────────────────────────────┬──────────────┐\n│ Доступно користувачам (95%)│ Резерв root (5%)│\n└────────────────────────────┴──────────────┘", size=10.5, pad=5, fill="#f0f9ff", stroke="#7dd3fc"))

    frags.append(fitbox(525, 205, 400, 115, "Чому 95% = 100% для звичайного процесу:\n• f_bfree (фізично вільні блоки): 5 ГБ (5%)\n• f_bavail (доступно не-root користувачам): 0 ГБ (0%)\n• Процес застосунку падає з ENOSPC при 95% заповнення диска!\n• root може увійти через sshd і відредагувати конфіги.", size=10, pad=5, fill="#fffbeb", stroke="#f59e0b", color="#92400e", bold=True))

    frags.append(fitbox(525, 330, 400, 115, "Оптимізація для терабайтних накопичувачів:\nНа диску 16 ТБ резерв 5% марнує 800 Гігабайтів!\nЗменшення резерву до 1% або 0% для розділів даних:\n# tune2fs -m 1 /dev/sdb1    (1% замість 5%)\n# tune2fs -m 0 /dev/sdc1    (для чистого data-диска)", size=10, pad=5, fill="#f0fdf4", stroke="#16a34a", color="#15803d", bold=True))

    render(os.path.join(OUT_DIR, "ext4-reserved-blocks-and-inodes.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_df_vs_du()
    fig_deleted_open_file()
    fig_mount_occlusion()
    fig_reserved_and_inodes()
    print("All 4 figures generated successfully in img/")
