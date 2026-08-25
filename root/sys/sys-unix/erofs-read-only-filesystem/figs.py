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
WARM = "#b8860b"

def fig_erofs_architecture():
    W, H = 1180, 680
    p = []

    p.append(fitbox(40, 60, 240, 60, "Блок 0 (4 КБ)\nСуперблок на зсуві 1024 Б", size=14,
                    fill=BLUE_FILL, stroke=NEG, bold=True))
    
    p.append(fitbox(310, 60, 380, 60, "Таблиці індексних вузлів (Inodes)\nCompact (32B) або Extended (64B)", size=14,
                    fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(fitbox(720, 60, 420, 60, "Фізичні блоки даних (4 КБ)\nСтиснені / Нестиснені екстенти", size=14,
                    fill=WARM_FILL, stroke=WARM, bold=True))

    p.append(arrow(280, 90, 306, 90))
    p.append(arrow(690, 90, 716, 90))

    # Inode layout details
    p.append(fitbox(40, 180, 520, 200,
                    "Структура Inode та Inline-дані (Tail-packing):\n\n"
                    "• i_format: FLAT_PLAIN, FLAT_INLINE, COMPRESSED_FULL, CHUNK_BASED\n"
                    "• Метадані: UID/GID, mode, size, nlink, xattr_icount\n"
                    "• Tail-packing: якщо хвіст файла < 4 КБ, він зберігається\n"
                    "  безпосередньо в тому ж блоці метаданих одразу за inode!\n"
                    "• Виграш: 0 марнованого місця на фрагментацію останнього блоку",
                    size=13, fill=FILL, stroke=LINE))

    # Compressed Extent mapping details
    p.append(fitbox(600, 180, 540, 200,
                    "Картування екстентів (Compressed Block Map):\n\n"
                    "• Логічні блоки групи (наприклад, 12 КБ = 3 × 4 КБ)\n"
                    "• Упаковка у фіксований фізичний блок (4 КБ на диску)\n"
                    "• Head-запис (початок pcluster) + Non-head (продовження)\n"
                    "• Послідовне розташування на диску полегшує блокове I/O",
                    size=13, fill=FILL, stroke=LINE))

    p.append(line(40, 410, 1140, 410, color=MUTED, dash="6 6"))

    # Bottom summary box
    p.append(fitbox(140, 450, 900, 180,
                    "Ключовий принцип дискового розташування EROFS:\n\n"
                    "1. Фізичне вирівнювання: усі фізичні блоки строго вирівняні по 4 КБ (розмір сторінки RAM).\n"
                    "2. Нульові витрати на нестиснені файли: зсув перераховується арифметично, без таблиць екстентів.\n"
                    "3. Дедуплікація метаданих: спільна таблиця xattr для SELinux-контекстів багатьох файлів.",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'erofs-architecture.svg'), W, H, *p,
           title="Дискова структура та вирівнювання блоків EROFS")

def fig_fixed_input_vs_fixed_output():
    W, H = 1180, 720
    p = []

    # Top: SquashFS
    p.append(fitbox(40, 60, 1100, 50, "SquashFS: Fixed-Input Compression (фіксований вхід)", size=16,
                    fill=RED_FILL, stroke=POS, bold=True))

    p.append(fitbox(60, 130, 260, 70, "Вхідний блок даних\n(128 КБ нестиснено)", size=13, fill=FILL, stroke=LINE))
    p.append(arrow(320, 165, 360, 165))
    p.append(fitbox(360, 130, 240, 70, "Алгоритм zlib/XZ\nстискає 128 КБ в один блок", size=13, fill=RED_FILL, stroke=POS))
    p.append(arrow(600, 165, 640, 165))
    p.append(fitbox(640, 130, 220, 70, "Стиснений блок на диску\n(невирівняний розмір, напр. 37 КБ)", size=13, fill=FILL, stroke=LINE))
    p.append(arrow(860, 165, 900, 165))
    p.append(fitbox(900, 130, 220, 70, "Читання 4 КБ потребує\nрозпакування всього 128 КБ!", size=13, fill=RED_FILL, stroke=POS, bold=True))

    p.append(line(40, 235, 1140, 235, color=MUTED, dash="6 6"))

    # Bottom: EROFS
    p.append(fitbox(40, 260, 1100, 50, "EROFS: Fixed-Output Compression (фіксований вихід)", size=16,
                    fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(fitbox(60, 330, 260, 70, "Змінний логічний обсяг\n(наприклад, 12 КБ = 3 сторінки)", size=13, fill=FILL, stroke=LINE))
    p.append(arrow(320, 365, 360, 365))
    p.append(fitbox(360, 330, 240, 70, "Упаковка LZ4/Zstd у фіксований\nфізичний блок диска", size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(600, 365, 640, 365))
    p.append(fitbox(640, 330, 220, 70, "Фізичний блок на диску\n(строго 4 КБ / PAGE_SIZE)", size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))
    p.append(arrow(860, 365, 900, 365))
    p.append(fitbox(900, 330, 220, 70, "In-place декомпресія\nпрямо в сторінки Page Cache!", size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(fitbox(100, 440, 980, 240,
                    "Порівняльний підсумок ефективності:\n\n"
                    "• Read Amplification (підвищення обсягу зчитування):\n"
                    "  SquashFS: розпаковує до 32× більше даних, ніж потрібно для однієї 4 КБ сторінки.\n"
                    "  EROFS: зчитує точно один або мінімальну кількість 4 КБ блоків (1x-2x amplification).\n\n"
                    "• Тимчасові буфери оперативної пам'яті:\n"
                    "  SquashFS: вимагає проміжного буфера декомпресії в RAM.\n"
                    "  EROFS: декомпресія за місцем (In-place decompression) без додаткових виділень пам'яті.",
                    size=13, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'fixed-input-vs-fixed-output.svg'), W, H, *p,
           title="Порівняння підходів стиснення: Fixed-Input (SquashFS) проти Fixed-Output (EROFS)")

def fig_inplace_decompression_pipeline():
    W, H = 1180, 660
    p = []

    steps = [
        ("1. Читання сторінки", "Запит VFS page read fault\nдля логічної 4 КБ сторінки", BLUE_FILL, NEG),
        ("2. Пошук у Bmap", "Перетворення логічного зсуву\nу фізичний кластер диска", FILL, LINE),
        ("3. Драйвер пристрою", "Пряме читання 4 КБ блоку\nіз диска (Block I/O)", FILL, LINE),
        ("4. Decompressor", "LZ4 / Zstd у ковзному\nрежимі in-place", GREEN_FILL, FIELD),
        ("5. Заповнення Cache", "Дані записані прямо у цільові\nсторінки Page Cache RAM", GREEN_FILL, FIELD),
    ]

    x0 = 40
    w_box = 200
    gap = 30
    for i, (title, desc, fill, stroke) in enumerate(steps):
        x = x0 + i * (w_box + gap)
        p.append(fitbox(x, 70, w_box, 110, f"{title}\n\n{desc}", size=13, fill=fill, stroke=stroke, bold=True))
        if i < len(steps) - 1:
            p.append(arrow(x + w_box + 4, 125, x + w_box + gap - 4, 125))

    p.append(line(40, 220, 1140, 220, color=MUTED, dash="6 6"))

    p.append(fitbox(60, 250, 510, 360,
                    "Звичайна декомпресія (Bounce Buffer):\n\n"
                    "1. Зчитування стисненого блоку з диска у буфер A.\n"
                    "2. Виділення тимчасового буфера B під розпаковані дані.\n"
                    "3. Декомпресія з A в B через CPU.\n"
                    "4. Копіювання з B у цільові сторінки Page Cache.\n"
                    "5. Звільнення буферів A та B.\n\n"
                    "❌ Результат: подвійне копіювання, навантаження на kmalloc,\n"
                    "  сплески затримок та фрагментація RAM.",
                    size=13, fill=RED_FILL, stroke=POS))

    p.append(fitbox(610, 250, 510, 360,
                    "In-Place декомпресія в EROFS:\n\n"
                    "1. Зчитування стисненого блоку у хвіст цільового масиву сторінок.\n"
                    "2. Декомпресія виконується безпосередньо у тому ж масиві\n"
                    "   фізичних сторінок (Rolling Decompression).\n"
                    "3. Жодного проміжного виділення пам'яті (0 extra allocations).\n"
                    "4. Жодного зайвого копіювання байтів (Zero CPU memcpy).\n\n"
                    "✅ Результат: затримка читання нижча в рази, передбачуваний\n"
                    "  час відгуку для системних процесів Android/microVM.",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'inplace-decompression-pipeline.svg'), W, H, *p,
           title="Конвеєр In-place декомпресії в ядрах Linux")

def fig_erofs_container_stack():
    W, H = 1180, 680
    p = []

    p.append(fitbox(40, 60, 1100, 50, "Простір користувача / Контейнери (nerdctl, containerd, Podman, Nydus)", size=15,
                    fill=BLUE_FILL, stroke=NEG, bold=True))

    p.append(arrow(590, 110, 590, 145))

    p.append(fitbox(40, 150, 520, 110,
                    "Класичний підхід (OverlayFS layer stack):\n"
                    "• Десятки шарів tgz розпаковуються в каталоги\n"
                    "• Мільйони окремих inodes/dentries у пам'яті\n"
                    "• Тиск на dentry cache та повільний старт",
                    size=13, fill=RED_FILL, stroke=POS))

    p.append(fitbox(620, 150, 520, 110,
                    "Сучасний підхід (EROFS + Composefs / Nydus):\n"
                    "• Контейнерний образ як єдиний blob EROFS\n"
                    "• Дедуплікація однакового вмісту між образами\n"
                    "• Миттєвий mount за мілісекунди без un-tar",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(880, 260, 880, 295))

    p.append(fitbox(400, 300, 560, 100,
                    "Шар ядра Linux: EROFS + FS-Cache (erofs over fscache)\n"
                    "• Ощадне онлайн-завантаження блоків (On-demand pulling)\n"
                    "• Запитуються лише ті 4 КБ блоки, які дійсно читаються під час старту\n"
                    "• Прямий доступ через VFS без розпакованих шарів OverlayFS",
                    size=13, fill=WARM_FILL, stroke=WARM, bold=True))

    p.append(arrow(680, 400, 680, 435))

    p.append(fitbox(200, 440, 960, 180,
                    "Практичні переваги EROFS для хмарних навантажень та прошивок:\n\n"
                    "1. Незмінність: образ лише для читання не дає підмінити системний код.\n"
                    "2. Старт контейнера не чекає на розпакування образу: читаються лише потрібні блоки.\n"
                    "3. Економія пам'яті вузла: відсутність дублювання dentries та підтримка shared page cache.",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'erofs-container-stack.svg'), W, H, *p,
           title="Архітектурний стек EROFS у контейнерах та хмарній інфраструктурі")

if __name__ == '__main__':
    fig_erofs_architecture()
    fig_fixed_input_vs_fixed_output()
    fig_inplace_decompression_pipeline()
    fig_erofs_container_stack()
    print("ok")
