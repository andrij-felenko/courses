# -*- coding: utf-8 -*-
"""Генератор схем для теми 'Ім'я — не файл: наслідки для щоденної роботи'."""

import sys, os

# 4 рівні вгору до кореня, де лежить scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_unlink_lifecycle():
    """Схема двофазного звільнення ресурсів: unlink() прибирає ім'я, close() звільняє блоки."""
    w, h = 980, 560
    frags = []

    # Заголовок / Опис рівнів
    frags.append(rect(30, 20, 920, 520, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(490, 46, "ДВОФАЗНИЙ ЖИТТЄВИЙ ЦИКЛ ФАЙЛУ: РОЗРИВ ІМЕНІ ТА ДИСКОВИХ БЛОКІВ", size=14, color="#0f172a", bold=True))

    # Стовпчик 1: Початковий стан (Файл відкритий, ім'я в каталозі)
    frags.append(rect(50, 75, 275, 445, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(187, 100, "1. ЗВИЧАЙНИЙ СТАН", size=12, color="#1e293b", bold=True))
    
    frags.append(fitbox(65, 120, 245, 55, "Каталог: /var/log/\napp.log ──> Inode #4211", size=11, pad=5, fill="#eff6ff", stroke="#3b82f6"))
    frags.append(arrow(187, 175, 187, 205, color="#3b82f6", sw=1.6))
    
    frags.append(fitbox(65, 205, 245, 80, "Inode #4211 (Ext4)\ni_nlink = 1  (одне ім'я)\ni_count = 1  (відкрито)\nРозмір: 4.2 ГБ", size=11, pad=5, fill="#f0fdf4", stroke="#22c55e"))
    frags.append(arrow(187, 285, 187, 315, color="#22c55e", sw=1.6))

    frags.append(fitbox(65, 315, 245, 75, "Процес PID 1042 (Daemon)\nFD 3 ──> struct file\nf_count = 1 | f_pos = 4.2 ГБ", size=11, pad=5, fill="#faf5ff", stroke="#a855f7"))
    frags.append(arrow(187, 390, 187, 420, color="#64748b", sw=1.6))

    frags.append(fitbox(65, 420, 245, 85, "Дисковий простір\nБлоки: 1 048 576 шт. (ЗАЙНЯТІ)\nУтиліта df: бачить 4.2 ГБ\nУтиліта du: бачить 4.2 ГБ", size=10.5, pad=5, fill="#f1f5f9", stroke="#64748b"))

    # Стовпчик 2: Фаза 1 — виклик unlink() при відкритому файлі (фантомний файл)
    frags.append(rect(352, 75, 275, 445, fill="#ffffff", stroke="#f59e0b", sw=1.8, rx=6))
    frags.append(text(489, 100, "2. ПІСЛЯ unlink(\"app.log\")", size=12, color="#b45309", bold=True))

    frags.append(fitbox(367, 120, 245, 55, "Каталог: /var/log/\n[ЗАПИС ВИДАЛЕНО]", size=11, pad=5, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True))
    frags.append(line(489, 175, 489, 205, color="#ef4444", sw=1.6, dash="4,3"))

    frags.append(fitbox(367, 205, 245, 80, "Inode #4211 (Ext4)\ni_nlink = 0  (БЕЗ ІМЕНІ!)\ni_count = 1  (ТРИМАЄ FD)\nРозмір: 4.8 ГБ (росте!)", size=11, pad=5, fill="#fefce8", stroke="#eab308", bold=True))
    frags.append(arrow(489, 285, 489, 315, color="#22c55e", sw=1.6))

    frags.append(fitbox(367, 315, 245, 75, "Процес PID 1042\nFD 3 ──> пише далі!\n/proc/1042/fd/3 (deleted)", size=11, pad=5, fill="#faf5ff", stroke="#a855f7"))
    frags.append(arrow(489, 390, 489, 420, color="#d97706", sw=1.6))

    frags.append(fitbox(367, 420, 245, 85, "Парадокс пам'яті:\nБлоки ЗАЙНЯТІ (не звільнено)\ndf: 100% (місце зайняте)\ndu /var/log: 0 байтів (не бачить)", size=10.5, pad=5, fill="#fffbeb", stroke="#f59e0b", color="#92400e"))

    # Стовпчик 3: Фаза 2 — закриття останнього дескриптора close()
    frags.append(rect(655, 75, 275, 445, fill="#ffffff", stroke="#10b981", sw=1.5, rx=6))
    frags.append(text(792, 100, "3. ПІСЛЯ close(3) АБО KILL", size=12, color="#065f46", bold=True))

    frags.append(fitbox(670, 120, 245, 55, "Каталог: /var/log/\n[Запис відсутній]", size=11, pad=5, fill="#f8fafc", stroke="#cbd5e1", color="#64748b"))

    frags.append(fitbox(670, 205, 245, 80, "Inode #4211\ni_nlink = 0\ni_count = 0  ──> ext4_evict_inode\n[ІНОД ОЧИЩЕНО]", size=11, pad=5, fill="#fef2f2", stroke="#dc2626", color="#991b1b"))
    frags.append(arrow(792, 285, 792, 315, color="#dc2626", sw=1.6))

    frags.append(fitbox(670, 315, 245, 75, "Процес PID 1042\nДескриптор закритий\n[struct file знищено]", size=11, pad=5, fill="#f8fafc", stroke="#cbd5e1", color="#64748b"))
    frags.append(arrow(792, 390, 792, 420, color="#10b981", sw=1.6))

    frags.append(fitbox(670, 420, 245, 85, "Повне звільнення:\nБлоки повернуто в бітову карту\ndf: МІСЦЕ ЗВІЛЬНЕНО\ndu: 0 байтів (узгоджено)", size=10.5, pad=5, fill="#f0fdf4", stroke="#10b981", color="#065f46", bold=True))

    # Стрілки між колонками (переходи)
    frags.append(arrow(325, 245, 352, 245, color="#d97706", sw=2.2))
    frags.append(arrow(627, 245, 655, 245, color="#10b981", sw=2.2))

    render(os.path.join(OUT_DIR, "unlink-vs-close-lifecycle.svg"), w, h, *frags)


def fig_atomic_rename():
    """Схема атомарної заміни файлу через rename() проти небезпечного прямого запису O_TRUNC."""
    w, h = 980, 520
    frags = []

    frags.append(rect(30, 20, 920, 480, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(490, 46, "АТОМАРНА ПІДМІНА (RENAME) ПРОТИ ПРЯМОГО ПЕРЕЗАПИСУ (TRUNCATE)", size=14, color="#0f172a", bold=True))

    # Ліва половина: Небезпечний прямий перезапис (O_TRUNC)
    frags.append(rect(50, 75, 420, 405, fill="#ffffff", stroke="#fca5a5", sw=1.5, rx=6))
    frags.append(text(260, 100, "НЕБЕЗПЕЧНО: open(O_WRONLY | O_TRUNC)", size=12.5, color="#991b1b", bold=True))

    frags.append(fitbox(70, 120, 380, 60, "1. Файл config.json (Inode #501)\nОбнуляється розмір (length = 0)\nДані старого файлу стерто з блоків", size=11, pad=5, fill="#fef2f2", stroke="#ef4444"))
    frags.append(arrow(260, 180, 260, 210, color="#ef4444", sw=1.6))

    frags.append(fitbox(70, 210, 380, 70, "2. Процес починає повільний запис...\nПаралельний читач читає ПОВРЕЖДЕНІ / НАПІВПУСТІ ДАНІ!\nЗбій живлення / SIGKILL ──> файл знищено назавжди!", size=10.5, pad=5, fill="#fff1f2", stroke="#f43f5e", color="#9f1239", bold=True))
    frags.append(arrow(260, 280, 260, 310, color="#ef4444", sw=1.6))

    frags.append(fitbox(70, 310, 380, 60, "3. Виконуваний бінарник (/usr/bin/app)\nЯдро повертає помилку ETXTBSY або\nпадіння через сторінковий збій mmap!", size=10.5, pad=5, fill="#fef2f2", stroke="#ef4444"))
    frags.append(arrow(260, 370, 260, 400, color="#ef4444", sw=1.6))

    frags.append(fitbox(70, 400, 380, 65, "Підсумок: стан гонитви (race condition),\nризик повної втрати конфігурації,\nнеможливість гарячого оновлення.", size=11, pad=5, fill="#fee2e2", stroke="#dc2626", color="#7f1d1d", bold=True))

    # Права половина: Безпечна заміна через rename()
    frags.append(rect(510, 75, 420, 405, fill="#ffffff", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(720, 100, "ПАТЕРН НАДІЙНОСТІ: Safe Save (rename)", size=12.5, color="#166534", bold=True))

    frags.append(fitbox(530, 120, 380, 60, "1. Запис у тимчасовий файл поруч:\nconfig.json.tmp.1042 (новий Inode #599)\nfsync(fd) ──> гарантія скидання на диск", size=11, pad=5, fill="#f0fdf4", stroke="#22c55e"))
    frags.append(arrow(720, 180, 720, 210, color="#16a34a", sw=1.6))

    frags.append(fitbox(530, 210, 380, 70, "2. rename(\"config.json.tmp.1042\", \"config.json\")\nАтомарна зміна покажчика в каталозі!\nЧитачі бачать АБО стару версію, АБО нову", size=10.5, pad=5, fill="#ecfdf5", stroke="#10b981", color="#065f46", bold=True))
    frags.append(arrow(720, 280, 720, 310, color="#16a34a", sw=1.6))

    frags.append(fitbox(530, 310, 380, 60, "3. Старий Inode #501 відв'язується (unlink):\nПрацюючий процес читає стару версію до кінця;\nНовий процес відкриває вже новий Inode #599", size=10.5, pad=5, fill="#f0fdf4", stroke="#22c55e"))
    frags.append(arrow(720, 370, 720, 400, color="#16a34a", sw=1.6))

    frags.append(fitbox(530, 400, 380, 65, "Підсумок: нульовий час простою,\nнеможливість прочитати напів-записаний файл,\nнадійне оновлення працюючих служб.", size=11, pad=5, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True))

    render(os.path.join(OUT_DIR, "atomic-rename-swap.svg"), w, h, *frags)


def fig_links_structure():
    """Схема структури жорстких та символьних посилань у VFS."""
    w, h = 980, 520
    frags = []

    frags.append(rect(30, 20, 920, 480, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(490, 46, "ВНУТРІШНЯ СТРУКТУРА ЖОРСТКИХ І СИМВОЛЬНИХ ПОСИЛАНЬ", size=14, color="#0f172a", bold=True))

    # Ліва половина: Жорсткі посилання (Hard Links)
    frags.append(rect(50, 75, 420, 405, fill="#ffffff", stroke="#93c5fd", sw=1.5, rx=6))
    frags.append(text(260, 100, "ЖОРСТКІ ПОСИЛАННЯ (Hard Links)", size=12.5, color="#1e40af", bold=True))

    frags.append(fitbox(70, 120, 380, 75, "Каталог (таблиця імен):\n• file_a.txt  ──> Inode #3312\n• file_b.txt  ──> Inode #3312\nДва рівноправні записи в каталозі", size=11, pad=5, fill="#eff6ff", stroke="#3b82f6"))
    frags.append(arrow(260, 195, 260, 230, color="#2563eb", sw=1.8))

    frags.append(fitbox(70, 230, 380, 80, "ЄДИНИЙ Inode #3312 (Ext4)\ni_nlink = 2  (лічильник посилань)\nПрава: 0644 | Власник: 1000\nАдреси блоків даних: [B102, B103]", size=11, pad=5, fill="#dbeafe", stroke="#1d4ed8", bold=True))
    frags.append(arrow(260, 310, 260, 345, color="#2563eb", sw=1.8))

    frags.append(fitbox(70, 345, 380, 120, "Властивості та обмеження:\n✓ Зміна вмісту через одне ім'я миттєво видно в іншому\n✓ Немає різниці між «оригіналом» і «посиланням»\n✗ НЕ МОЖНА крізь межу файлових систем (EXDEV)\n✗ ЗАБОРОНЕНО для каталогів (запобігання циклам)", size=10.5, pad=5, fill="#f8fafc", stroke="#64748b"))

    # Права половина: Символьні посилання (Symbolic Links)
    frags.append(rect(510, 75, 420, 405, fill="#ffffff", stroke="#c084fc", sw=1.5, rx=6))
    frags.append(text(720, 100, "СИМВОЛЬНІ ПОСИЛАННЯ (Symlinks)", size=12.5, color="#6b21a8", bold=True))

    frags.append(fitbox(530, 120, 380, 75, "Каталог (таблиця імен):\n• link.txt ──> Inode #7784 (тип S_IFLNK)\nОкремий запис на власний унікальний інод", size=11, pad=5, fill="#faf5ff", stroke="#a855f7"))
    frags.append(arrow(720, 195, 720, 230, color="#9333ea", sw=1.8))

    frags.append(fitbox(530, 230, 380, 80, "Окремий Inode #7784 (S_IFLNK)\nВміст інода або окремого блоку:\nТекстовий рядок: \"/data/target.txt\"\n(або відносний: \"../target.txt\")", size=11, pad=5, fill="#f3e8ff", stroke="#7e22ce", bold=True))
    frags.append(arrow(720, 310, 720, 345, color="#9333ea", sw=1.8))

    frags.append(fitbox(530, 345, 380, 120, "Властивості та обмеження:\n✓ ПРАЦЮЄ крізь різні розділи й накопичувачі\n✓ МОЖЕ вказувати на каталоги\n✓ Може бути висячим (dangling), якщо ціль видалено\n✗ Потребує додаткового розбору шляху (overhead)", size=10.5, pad=5, fill="#f8fafc", stroke="#64748b"))

    render(os.path.join(OUT_DIR, "hardlink-vs-symlink-structure.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_unlink_lifecycle()
    fig_atomic_rename()
    fig_links_structure()
    print("OK: generated figures for name-is-not-the-file")
