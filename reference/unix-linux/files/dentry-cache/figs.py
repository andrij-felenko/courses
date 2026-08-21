# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#f1f3f5"
WARM = "#b8860b"


# ── 1. Анатомія struct dentry ──────────────────────────────────────────────
def fig_dentry_structure():
    W, H = 1240, 860
    p = []

    # Заголовок блоку
    p.append(rect(40, 20, 1160, 820, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10))
    p.append(fitbox(60, 35, 1120, 40, ["struct dentry — об'єкт зв'язку імені та ієрархії у пам'яті VFS"],
                    size=16, bold=True, fill=WARM_FILL, stroke=WARM, sw=1.8, color=INK))

    # Секція 1: Керування та синхронізація (зліва)
    p.append(rect(60, 90, 350, 340, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=8))
    p.append(text(235, 115, "Керування та синхронізація", size=14, bold=True, color=NEG))
    p.append(line(60, 128, 410, 128, color=NEG, sw=1.2))

    fields_left = [
        ("unsigned int d_flags", "прапорці стану та типу (DCACHE_*)"),
        ("seqcount_spinlock_t d_seq", "лічильник версій seqlock (RCU-walk)"),
        ("struct lockref d_lockref", "об'єднані d_lock (spinlock) + d_count"),
        ("const struct dentry_operations *d_op", "таблиця операцій файлової системи"),
        ("struct super_block *d_sb", "вказівник на суперблок файлової системи"),
        ("unsigned long d_time", "часова мітка чинності (для NFS/CIFS)"),
    ]
    y_cursor = 140
    for fname, fdesc in fields_left:
        p.append(fitbox(70, y_cursor, 330, 42, [fname, fdesc], size=11, pad=4, fill="#ffffff", stroke=MUTED, sw=1.0, color=INK))
        y_cursor += 47

    # Секція 2: Ім'я та швидкий пошук (посередині)
    p.append(rect(430, 90, 370, 340, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(615, 115, "Ім'я та хеш-пошук", size=14, bold=True, color=FIELD))
    p.append(line(430, 128, 800, 128, color=FIELD, sw=1.2))

    fields_mid = [
        ("struct qstr d_name", "ім'я: hashlen (довжина + хеш) + *name"),
        ("unsigned char d_iname[32]", "вбудований буфер для коротких імен"),
        ("struct hlist_bl_node d_hash", "вузол у глобальній dentry_hashtable"),
        ("struct inode *d_inode", "вказівник на inode (NULL = негативний dentry)"),
    ]
    y_cursor = 140
    for fname, fdesc in fields_mid:
        p.append(fitbox(440, y_cursor, 350, 46, [fname, fdesc], size=11, pad=4, fill="#ffffff", stroke=MUTED, sw=1.0, color=INK))
        y_cursor += 52

    # Секція 3: Топологія дерева та пам'ять (справа)
    p.append(rect(820, 90, 360, 340, fill=RED_FILL, stroke=POS, sw=1.8, rx=8))
    p.append(text(1000, 115, "Ієрархія та керування пам'яттю", size=14, bold=True, color=POS))
    p.append(line(820, 128, 1180, 128, color=POS, sw=1.2))

    fields_right = [
        ("struct dentry *d_parent", "вказівник на батьківський каталог"),
        ("struct list_head d_subdirs", "голова списку дочірніх dentry"),
        ("struct list_head d_child", "вузол у списку d_subdirs батька"),
        ("struct list_head d_lru", "вузол у списку невикористовуваних (LRU)"),
        ("union { d_rcu, d_alias } d_u", "звільнення через RCU або список аліасів"),
    ]
    y_cursor = 140
    for fname, fdesc in fields_right:
        p.append(fitbox(830, y_cursor, 340, 44, [fname, fdesc], size=11, pad=4, fill="#ffffff", stroke=MUTED, sw=1.0, color=INK))
        y_cursor += 49

    # Нижній пояснювальний блок: зв'язки з зовнішніми структурами
    p.append(rect(60, 450, 1120, 370, fill=GREY_FILL, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(620, 475, "Зовнішні зв'язки структури dentry у підсистемі VFS", size=15, bold=True, color=INK))
    p.append(line(60, 490, 1180, 490, color=MUTED, sw=1.0))

    # 4 блоки зовнішніх структур
    p.append(fitbox(80, 510, 240, 130,
                    ["struct inode", "метадані файлу на диску", "(права, розмір, блоки)",
                     "d_inode == NULL →", "негативний dentry"],
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.5, color=INK))

    p.append(fitbox(350, 510, 240, 130,
                    ["dentry_hashtable", "глобальний хеш VFS", "ключ: (d_parent, d_name)",
                     "bit-locked ланцюжки", "hlist_bl_head"],
                    size=12, fill=BLUE_FILL, stroke=NEG, sw=1.5, color=INK))

    p.append(fitbox(620, 510, 240, 130,
                    ["Батьківський dentry", "d_parent вказує вгору", "у списку d_subdirs батька",
                     "знаходиться d_child", "поточного dentry"],
                    size=12, fill=RED_FILL, stroke=POS, sw=1.5, color=INK))

    p.append(fitbox(890, 510, 270, 130,
                    ["Черги list_lru", "списки витіснення LRU", "активні при d_count == 0",
                     "prune_dcache_sb()", "сканує при нестачі RAM"],
                    size=12, fill=WARM_FILL, stroke=WARM, sw=1.5, color=INK))

    # Стрілки від dentry до зовнішніх об'єктів
    p.append(arrow(200, 650, 200, 700, color=FIELD, sw=1.8))
    p.append(arrow(470, 650, 470, 700, color=NEG, sw=1.8))
    p.append(arrow(740, 650, 740, 700, color=POS, sw=1.8))
    p.append(arrow(1020, 650, 1020, 700, color=WARM, sw=1.8))

    p.append(fitbox(80, 710, 240, 85,
                    ["Один inode може мати", "кілька dentry", "(жорсткі посилання, links)"],
                    size=12, fill="#ffffff", stroke=FIELD, sw=1.2, color=FIELD))

    p.append(fitbox(350, 710, 240, 85,
                    ["O(1) швидкий пошук", "без читання диска та", "блокувань у RCU-режимі"],
                    size=12, fill="#ffffff", stroke=NEG, sw=1.2, color=NEG))

    p.append(fitbox(620, 710, 240, 85,
                    ["Відновлення повного шляху", "d_path() та getcwd()", "проходом знизу до кореня"],
                    size=12, fill="#ffffff", stroke=POS, sw=1.2, color=POS))

    p.append(fitbox(890, 710, 270, 85,
                    ["Пам'ять повертається в slab", "через call_rcu() після", "періоду благодаті"],
                    size=12, fill="#ffffff", stroke=WARM, sw=1.2, color=WARM))

    render(os.path.join(IMG, 'dentry-structure.svg'), W, H, *p)


# ── 2. Дворівнева організація: хеш-таблиця та дерево ───────────────────────
def fig_dcache_hashtable_and_tree():
    W, H = 1260, 780
    p = []

    # Ліва колонка: Глобальна хеш-таблиця
    p.append(rect(30, 30, 560, 720, fill="#ffffff", stroke=NEG, sw=1.8, rx=10))
    p.append(fitbox(50, 45, 520, 45, ["1. Глобальна хеш-таблиця dentry_hashtable"],
                    size=16, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.5, color=NEG))

    p.append(fitbox(50, 100, 520, 60,
                    ["Масив кошиків hlist_bl_head (bit-spinlocks у молодшому біті вказівника)",
                     "Ключ хешування: hash(d_parent, d_name) → O(1) пошук за ім'ям"],
                    size=12, fill=GREY_FILL, stroke=MUTED, sw=1.0, color=INK))

    # Слот 0, Слот 1, ... Слот k
    buckets = [
        (175, "Bucket #1024", ["dentry(\"/usr\", parent=/)"]),
        (255, "Bucket #2048", ["dentry(\"bin\", parent=/usr)", "→ dentry(\"lib\", parent=/usr)"]),
        (355, "Bucket #4096", ["dentry(\"libc.so\", parent=/usr/lib)", "→ dentry(\"missing.so\", parent=/usr/lib, NULL)"]),
        (475, "Bucket #8192", ["dentry(\"bash\", parent=/usr/bin)"]),
    ]

    for y, bname, entries in buckets:
        p.append(fitbox(50, y, 140, 50, [bname, "hlist_bl_head"], size=12, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.2, color=NEG))
        p.append(arrow(195, y + 25, 225, y + 25, color=NEG, sw=1.5))
        p.append(fitbox(230, y, 340, 50 + (len(entries)-1)*20, entries, size=11, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))

    p.append(fitbox(50, 580, 520, 150,
                    ["Як працює lookup_fast():",
                     "1. Обчислюється hashlen = hash(parent, name).",
                     "2. Знаходиться bucket у dentry_hashtable.",
                     "3. У критичній секції RCU сканується ланцюжок без взяття блокувань.",
                     "4. Звіряються d_parent, довжина, хеш та ім'я рядка.",
                     "5. Чинність перевіряється через seqlock d_seq."],
                    size=12, pad=6, fill=WARM_FILL, stroke=WARM, sw=1.4, color=INK))

    # Права колонка: Ієрархічне дерево в пам'яті
    p.append(rect(610, 30, 620, 720, fill="#ffffff", stroke=FIELD, sw=1.8, rx=10))
    p.append(fitbox(630, 45, 580, 45, ["2. Ієрархічне дерево в пам'яті (d_parent / d_subdirs)"],
                    size=16, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.5, color=FIELD))

    p.append(fitbox(630, 100, 580, 60,
                    ["Деревоподібний граф з коренем sb->s_root (/) у пам'яті",
                     "Зв'язки d_parent (вгору) та d_subdirs / d_child (вниз і вшир)"],
                    size=12, fill=GREY_FILL, stroke=MUTED, sw=1.0, color=INK))

    # Вузли дерева
    # Root /
    p.append(fitbox(850, 175, 140, 45, ["dentry: / (корінь)", "inode: #2"], size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.5, color=FIELD))

    # /usr
    p.append(arrow(920, 225, 920, 265, color=FIELD, sw=1.5))
    p.append(fitbox(850, 270, 140, 45, ["dentry: usr", "inode: #1420"], size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.5, color=FIELD))

    # /usr/bin та /usr/lib
    p.append(arrow(880, 320, 750, 370, color=FIELD, sw=1.5))
    p.append(arrow(960, 320, 1080, 370, color=FIELD, sw=1.5))

    p.append(fitbox(680, 375, 140, 45, ["dentry: bin", "inode: #1421"], size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.2, color=INK))
    p.append(fitbox(1010, 375, 140, 45, ["dentry: lib", "inode: #1422"], size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.2, color=INK))

    # Листки
    p.append(arrow(750, 425, 710, 475, color=FIELD, sw=1.5))
    p.append(arrow(1050, 425, 890, 475, color=FIELD, sw=1.5))
    p.append(arrow(1110, 425, 1110, 475, color=POS, sw=1.5))

    p.append(fitbox(635, 480, 150, 45, ["dentry: bash", "inode: #9801"], size=11, fill="#ffffff", stroke=FIELD, sw=1.2, color=INK))
    p.append(fitbox(805, 480, 175, 45, ["dentry: libc.so", "inode: #9802"], size=11, fill="#ffffff", stroke=FIELD, sw=1.2, color=INK))
    p.append(fitbox(1000, 480, 200, 45, ["dentry: missing.so", "inode: NULL (негативний)"], size=11, fill=RED_FILL, stroke=POS, sw=1.5, color=POS))

    p.append(fitbox(630, 580, 580, 150,
                    ["Навіщо потрібні обидві структури одночасно:",
                     "• Хеш-таблиця знаходить елемент за O(1) під час спуску вниз.",
                     "• Вказівники d_parent дозволяють миттєво піднятися до кореня (d_path),",
                     "  відтворюючи рядок поточного робочого каталогу (getcwd).",
                     "• d_subdirs дозволяє рекурсивно скидати або перейменовувати піддерева."],
                    size=12, pad=6, fill=WARM_FILL, stroke=WARM, sw=1.4, color=INK))

    render(os.path.join(IMG, 'dcache-hashtable-and-tree.svg'), W, H, *p)


# ── 3. Життєвий цикл і стани dentry ─────────────────────────────────────────
def fig_dentry_lifecycle_states():
    W, H = 1240, 760
    p = []

    p.append(fitbox(60, 30, 1120, 50, ["Стани запису каталогу (dentry lifecycle) та переходи між ними"],
                    size=16, bold=True, fill=WARM_FILL, stroke=WARM, sw=1.8, color=INK))

    # Стан 1: Створення / Виділення
    p.append(fitbox(60, 130, 280, 90,
                    ["Виділення пам'яті: d_alloc()", "slab кеш: dentry_cache", "d_count = 1, d_inode = NULL"],
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.5, color=INK))

    # Стан 2: Active (In-Use)
    p.append(fitbox(460, 110, 340, 130,
                    ["СТАН: Active (Використовуваний)",
                     "• d_count > 0, d_inode != NULL",
                     "• Відкритий процесом, cwd або предок",
                     "• НЕ перебуває в чергах LRU",
                     "• Захищений від вивільнення пам'яті"],
                    size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2.0, color=FIELD))

    # Стан 3: Negative Dentry
    p.append(fitbox(880, 110, 300, 130,
                    ["СТАН: Negative (Негативний)",
                     "• d_inode == NULL (файл відсутній)",
                     "• Кешує факт помилки ENOENT",
                     "• Може бути Active або Unused (в LRU)",
                     "• Запобігає дисковим перевіркам"],
                    size=13, bold=True, fill=RED_FILL, stroke=POS, sw=2.0, color=POS))

    # Стан 4: Unused (В черзі LRU)
    p.append(fitbox(460, 380, 340, 140,
                    ["СТАН: Unused (Невикористовуваний)",
                     "• d_count == 0, d_inode != NULL",
                     "• Знаходиться у списку super_block->s_dentry_lru",
                     "• Залишається в dentry_hashtable (швидкий хіт)",
                     "• Кандидат на вивільнення при брак пам'яті"],
                    size=13, bold=True, fill=BLUE_FILL, stroke=NEG, sw=2.0, color=NEG))

    # Стан 5: Звільнення / Знищення
    p.append(fitbox(460, 620, 340, 100,
                    ["Звільнення: dentry_kill()",
                     "• Видалення з хешу d_drop() та з LRU",
                     "• iput(d_inode) декрементує inode",
                     "• call_rcu() → kmem_cache_free()"],
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.5, color=INK))

    # Стрілки переходів
    # d_alloc -> Active (ініціалізація успішним inode)
    p.append(arrow(345, 175, 455, 175, color=FIELD, sw=2.0))
    p.append(text(400, 160, "d_instantiate()", size=11, bold=True, color=FIELD))

    # d_alloc -> Negative (файлу не знайдено на диску)
    p.append(arrow(200, 125, 875, 125, color=POS, sw=1.8))
    p.append(text(540, 95, "i_op->lookup() повернув NULL → d_add(dentry, NULL)", size=11, color=POS))

    # Active -> Unused (останній close/dput)
    p.append(arrow(580, 245, 580, 375, color=NEG, sw=2.0))
    p.append(text(640, 310, "dput() (d_count == 0)", size=12, bold=True, color=NEG))

    # Unused -> Active (повторне звернення)
    p.append(arrow(680, 375, 680, 245, color=FIELD, sw=2.0))
    p.append(text(740, 310, "dget() (кеш-хіт)", size=12, bold=True, color=FIELD))

    # Active -> Negative (unlink / видалення файлу)
    p.append(arrow(805, 175, 875, 175, color=POS, sw=1.8))
    p.append(text(840, 160, "d_delete()", size=11, color=POS))

    # Negative -> Active (створення файлу: open O_CREAT / mknod)
    p.append(arrow(875, 210, 805, 210, color=FIELD, sw=1.8))
    p.append(text(840, 230, "d_instantiate()", size=11, color=FIELD))

    # Unused -> Знищення (prune_dcache_sb під час memory pressure)
    p.append(arrow(630, 525, 630, 615, color=MUTED, sw=2.0))
    p.append(text(730, 570, "dcache shrinker (пам'ятний тиск)", size=12, bold=True, color=POS))

    # Negative (unused) -> Знищення
    p.append(arrow(1030, 245, 680, 620, color=MUTED, sw=1.5))
    p.append(text(910, 430, "витіснення з LRU", size=11, color=MUTED))

    render(os.path.join(IMG, 'dentry-lifecycle-states.svg'), W, H, *p)


# ── 4. RCU-walk проти Ref-walk ──────────────────────────────────────────────
def fig_rcu_walk_vs_ref_walk():
    W, H = 1260, 840
    p = []

    p.append(fitbox(50, 20, 1160, 45, ["Механізм розбору шляхів у Linux: паралельний RCU-walk проти блокувального Ref-walk"],
                    size=16, bold=True, fill=WARM_FILL, stroke=WARM, sw=1.8, color=INK))

    # Ліва колонка: RCU-walk (Швидкий шлях)
    p.append(rect(50, 80, 560, 540, fill="#ffffff", stroke=FIELD, sw=2.0, rx=10))
    p.append(fitbox(70, 90, 520, 40, ["RCU-walk (LOOKUP_RCU) — Швидкий шлях"],
                    size=15, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.5, color=FIELD))

    rcu_steps = [
        (140, "1. Вхід у критичну секцію RCU", ["rcu_read_lock() — забороняє вивільнення пам'яті об'єктів.", "Жодних блокувань і змін d_count (0 atomic операцій!)."]),
        (230, "2. Отримання послідовності seqlock", ["seq = read_seqcount_begin(&dentry->d_seq);", "Фіксує версію стану dentry перед читанням полів."]),
        (320, "3. Читання полів та хеш-пошук", ["Звірка d_parent, hashlen та рядка d_name.", "Отримання вказівника d_inode без взяття spinlock."]),
        (410, "4. Перевірка цілісності (Seqlock Validation)", ["if (read_seqcount_retry(&dentry->d_seq, seq)) → FAIL", "Якщо під час читання dentry змінився, перевірка провалюється."]),
        (510, "5. Успішний перехід до нащадка", ["Поточний dentry стає новим parent.", "Продовжуємо RCU-walk для наступного компонента шляху."]),
    ]
    for y, title, desc in rcu_steps:
        p.append(fitbox(70, y, 520, 75, [title] + desc, size=11, fill=GREEN_FILL, stroke=FIELD, sw=1.0, color=INK))
        if y < 510:
            p.append(arrow(330, y + 77, 330, y + 88, color=FIELD, sw=1.5))

    # Права колонка: Ref-walk (Повільний шлях)
    p.append(rect(650, 80, 560, 540, fill="#ffffff", stroke=POS, sw=2.0, rx=10))
    p.append(fitbox(670, 90, 520, 40, ["Ref-walk (LOOKUP_REPARSE) — Повільний шлях"],
                    size=15, bold=True, fill=RED_FILL, stroke=POS, sw=1.5, color=POS))

    ref_steps = [
        (140, "1. Блокування та посилання", ["dget(dentry) — атомарний інкремент лічильника посилань.", "Спричиняє cacheline contention на багатоядерних CPU."]),
        (230, "2. Обробка промахів (lookup_slow)", ["dir->i_op->lookup() — файлова система читає диск.", "Процес може засинати в очікуванні блокового I/O."]),
        (320, "3. Обробка складних переходів", ["Читання символьних посилань (symlinks, vfs_readlink).", "Перетин точок монтування із взяттям mount_lock."]),
        (410, "4. Кастомна валідація d_revalidate()", ["Виклик d_op->d_revalidate() у мережевих ФС (NFS, CIFS)", "із можливістю відправки RPC-запитів по мережі."]),
        (510, "5. Завершення обходу", ["Повернення знайденого struct path (dentry + vfsmount).", "Звільнення проміжних посилань через dput()."]),
    ]
    for y, title, desc in ref_steps:
        p.append(fitbox(670, y, 520, 75, [title] + desc, size=11, fill=RED_FILL, stroke=POS, sw=1.0, color=INK))
        if y < 510:
            p.append(arrow(930, y + 77, 930, y + 88, color=POS, sw=1.5))

    # Окремий нижній блок: unlazy_walk / legitimize_path
    p.append(rect(50, 650, 1160, 160, fill=WARM_FILL, stroke=WARM, sw=2.0, rx=8))
    p.append(fitbox(70, 660, 1120, 30, ["Точка відкату: unlazy_walk() та legitimize_path()"],
                    size=14, bold=True, fill="#ffffff", stroke=WARM, sw=1.2, color=WARM))

    p.append(fitbox(70, 700, 1120, 95,
                    ["Коли RCU-walk не може продовжити роботу (symlink, монтування, промах у dcache, збій seqlock):",
                     "1. Викликається legitimize_path() — спроба атомарно взяти dget() на поточному dentry через lockref_get_not_dead().",
                     "2. У разі успіху — обхід безпечно переходить у Ref-walk для решти шляху без повернення на старт.",
                     "3. У разі невдачі — повний перезапуск обходу від самого кореня у режимі Ref-walk з блокуваннями."],
                    size=12, pad=4, fill="#ffffff", stroke=MUTED, sw=1.0, color=INK))

    # Стрілка від лівої колонки вниз до unlazy_walk (збоку)
    p.append(arrow(330, 622, 330, 648, color=WARM, sw=2.0))
    p.append(text(390, 638, "Fallback", size=11, bold=True, color=WARM))

    # Стрілка від unlazy_walk вгору до правої колонки
    p.append(arrow(930, 648, 930, 622, color=WARM, sw=2.0))
    p.append(text(990, 638, "Перехід", size=11, bold=True, color=WARM))

    render(os.path.join(IMG, 'rcu-walk-vs-ref-walk.svg'), W, H, *p)


# ── 5. Скидання пам'яті dcache та vfs_cache_pressure ────────────────────────
def fig_dcache_shrinker_pressure():
    W, H = 1240, 780
    p = []

    p.append(fitbox(60, 25, 1120, 45, ["Механізм вивільнення пам'яті dcache під керуванням ядра (Memory Pressure)"],
                    size=16, bold=True, fill=WARM_FILL, stroke=WARM, sw=1.8, color=INK))

    # Блок 1: Системний стан нестачі RAM
    p.append(fitbox(60, 90, 340, 110,
                    ["1. Нестача вільної пам'яті (RAM)",
                     "• Аллокатор сторінок досяг нижньої межі (low watermark)",
                     "• Пробудження фонового демона kswapd",
                     "• Або пряме витіснення (direct reclaim)"],
                    size=12, fill=RED_FILL, stroke=POS, sw=1.5, color=INK))

    # Блок 2: Інтерфейс Shrinker ядра
    p.append(fitbox(450, 90, 340, 110,
                    ["2. Ядерний інтерфейс struct shrinker",
                     "• Реєстрація зворотних викликів підсистем VFS",
                     "• Метод count_objects() оцінює розмір Unused dentry",
                     "• Метод scan_objects() ініціює вивільнення"],
                    size=12, fill=BLUE_FILL, stroke=NEG, sw=1.5, color=INK))

    # Блок 3: Сканування LRU списків
    p.append(fitbox(840, 90, 340, 110,
                    ["3. Функція prune_dcache_sb()",
                     "• Обхід per-NUMA / per-memcg списків list_lru",
                     "• Вилучення найстаріших dentry (d_count == 0)",
                     "• Виклик dentry_kill() та iput(inode)"],
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.5, color=INK))

    # Стрілки між 1 -> 2 -> 3
    p.append(arrow(405, 145, 445, 145, color=INK, sw=1.8))
    p.append(arrow(795, 145, 835, 145, color=INK, sw=1.8))

    # Великий блок регулювання vfs_cache_pressure
    p.append(rect(60, 230, 1120, 380, fill="#ffffff", stroke=MUTED, sw=1.8, rx=10))
    p.append(fitbox(80, 245, 1080, 40,
                    ["Регулювання балансу витіснення через /proc/sys/vm/vfs_cache_pressure"],
                    size=15, bold=True, fill=WARM_FILL, stroke=WARM, sw=1.5, color=WARM))

    # 3 стовпчики: <100, =100, >100
    p.append(fitbox(80, 305, 340, 200,
                    ["vfs_cache_pressure = 50 (< 100)",
                     "Пріоритет збереження метаданих",
                     "───────────────────────────",
                     "• Ядро менш охоче скидає dcache та icache.",
                     "• Агресивніше витісняються сторінки даних (page cache).",
                     "• Вигідно для компіляторів, Git, веб-серверів із мільйонами дрібних файлів.",
                     "• Ризик: вищий тиск на пам'ять при великих файлах."],
                    size=12, pad=6, fill=GREEN_FILL, stroke=FIELD, sw=1.5, color=INK))

    p.append(fitbox(450, 305, 340, 200,
                    ["vfs_cache_pressure = 100 (Default)",
                     "Збалансоване витіснення",
                     "───────────────────────────",
                     "• Справедливий паритет 1:1 між page cache та dentry/inode cache.",
                     "• Кількість записів dcache, що скидаються, пропорційна загальному скануванню сторінок.",
                     "• Оптимально для більшості стандартних робочих навантажень."],
                    size=12, pad=6, fill=BLUE_FILL, stroke=NEG, sw=1.5, color=INK))

    p.append(fitbox(820, 305, 340, 200,
                    ["vfs_cache_pressure = 500 (> 100)",
                     "Агресивне очищення метаданих",
                     "───────────────────────────",
                     "• Ядро скидає dentry та inode кеші у 5 разів агресивніше за page cache.",
                     "• Звільняє slab-пам'ять при перших ознаках браку RAM.",
                     "• Вигідно для streaming баз даних, транскодування відео (де важливі сторінки даних)."],
                    size=12, pad=6, fill=RED_FILL, stroke=POS, sw=1.5, color=INK))

    p.append(fitbox(80, 520, 1080, 75,
                    ["Формула розрахунку сканування dcache:",
                     "objects_to_scan = (unused_dentries * scan_pages * vfs_cache_pressure) / (total_reclaimable_pages * 100)"],
                    size=12, bold=True, fill=GREY_FILL, stroke=MUTED, sw=1.2, color=INK))

    # Нижній блок: Ручне скидання
    p.append(fitbox(60, 630, 1120, 120,
                    ["Ручне скидання кешів простору ядра (Drop Caches):",
                     "• sync && echo 2 > /proc/sys/vm/drop_caches  → скидає всі Unused dentry та неактивні inode.",
                     "• sync && echo 3 > /proc/sys/vm/drop_caches  → скидає pagecache + dentry + inodes.",
                     "Active dentry (d_count > 0) залишаються в пам'яті та захищені від скидання."],
                    size=12, pad=6, fill=WARM_FILL, stroke=WARM, sw=1.5, color=INK))

    render(os.path.join(IMG, 'dcache-shrinker-pressure.svg'), W, H, *p)


if __name__ == '__main__':
    fig_dentry_structure()
    fig_dcache_hashtable_and_tree()
    fig_dentry_lifecycle_states()
    fig_rcu_walk_vs_ref_walk()
    fig_dcache_shrinker_pressure()
    print("All 5 dcache figures generated successfully.")
