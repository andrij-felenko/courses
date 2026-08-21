# -*- coding: utf-8 -*-
"""Фігури до теми «GEM: об'єкти пам'яті графічного чипа»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_gem_object_architecture():
    """Архітектура GEM: локальні числові дескриптори процесів, ядровий drm_gem_object та бекенди пам'яті."""
    W, H = 1080, 560
    f = []

    # ── Простір користувача ───────────────────────────────────────────────
    f.append(rect(40, 40, 310, 480, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(195, 70, "Простір користувача", size=15, bold=True, color=INK))

    # Процес А
    f.append(rect(60, 95, 270, 185, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(195, 120, "Процес A (3D рушій)", size=13, bold=True, color=INK))
    f.append(text(195, 142, "Відкритий /dev/dri/renderD128", size=11, color=MUTED))
    f.append(fitbox(80, 160, 230, 48, "Хендл #1 (Текстура)\nлокальний id: 1", size=12, fill="#eef2ff", stroke=NEG))
    f.append(fitbox(80, 218, 230, 48, "Хендл #2 (Ціль рендеру)\nлокальний id: 2", size=12, fill="#eaf7ee", stroke=FIELD))

    # Процес Б
    f.append(rect(60, 310, 270, 185, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(195, 335, "Процес B (Композитор Wayland)", size=13, bold=True, color=INK))
    f.append(text(195, 357, "Відкритий /dev/dri/card0", size=11, color=MUTED))
    f.append(fitbox(80, 375, 230, 48, "Хендл #1 (Фреймбуфер екрана)\nлокальний id: 1", size=12, fill="#fdf3e7", stroke=POS))
    f.append(fitbox(80, 433, 230, 48, "Хендл #7 (Імпортований буфер)\nлокальний id: 7", size=12, fill="#eaf7ee", stroke=FIELD))

    # ── Простір ядра: таблиці та drm_gem_object ───────────────────────────
    f.append(rect(380, 40, 340, 480, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(550, 70, "Ядро DRM: struct drm_gem_object", size=15, bold=True, color=INK))

    # Об'єкт 1 (Текстура)
    f.append(rect(400, 95, 300, 110, fill="#eef2ff", stroke=NEG, sw=1.2, rx=6))
    f.append(text(550, 118, "GEM Object A (Текстура)", size=12, bold=True, color=NEG))
    f.append(text(550, 140, "kref = 1 · size = 16 MiB", size=11, color=INK))
    f.append(text(550, 160, "dma_resv · vma_node (fake offset)", size=11, color=MUTED))
    f.append(text(550, 180, "funcs -> drm_gem_shmem_funcs", size=11, color=MUTED))

    # Об'єкт 2 (Спільний буфер кадру)
    f.append(rect(400, 230, 300, 135, fill="#eaf7ee", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(550, 255, "GEM Object B (Спільний буфер кадру)", size=12, bold=True, color=FIELD))
    f.append(text(550, 280, "kref = 2 (Хендл #2 у Процесі A + #7 у B)", size=11, bold=True, color=INK))
    f.append(text(550, 302, "dma_resv (огорожі рендеру й показу)", size=11, color=MUTED))
    f.append(text(550, 324, "dma_buf прив'язка для PRIME", size=11, color=MUTED))
    f.append(text(550, 346, "funcs -> amdgpu_gem_object_funcs", size=11, color=MUTED))

    # Об'єкт 3 (Фреймбуфер екрана)
    f.append(rect(400, 390, 300, 105, fill="#fdf3e7", stroke=POS, sw=1.2, rx=6))
    f.append(text(550, 415, "GEM Object C (Курсор/Екран)", size=12, bold=True, color=POS))
    f.append(text(550, 438, "kref = 1 · size = 32 KiB", size=11, color=INK))
    f.append(text(550, 458, "dumb_buffer / scanout plane", size=11, color=MUTED))
    f.append(text(550, 478, "funcs -> drm_gem_dma_funcs", size=11, color=MUTED))

    # Зв'язки між хендлами та об'єктами
    f.append(arrow(310, 184, 400, 150, color=NEG))
    f.append(arrow(310, 242, 400, 280, color=FIELD))
    f.append(arrow(310, 399, 400, 435, color=POS))
    f.append(arrow(310, 457, 400, 310, color=FIELD))

    # ── Фізична пам'ять і бекенди ─────────────────────────────────────────
    f.append(rect(750, 40, 290, 480, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(895, 70, "Бекенди пам'яті", size=15, bold=True, color=INK))

    f.append(rect(770, 95, 250, 110, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(895, 122, "shmem (Системна RAM)", size=12, bold=True, color=INK))
    f.append(text(895, 148, "Анонімні сторінки ядра", size=11, color=MUTED))
    f.append(text(895, 172, "swapcache · sg_table", size=11, color=MUTED))

    f.append(rect(770, 230, 250, 135, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(895, 257, "TTM (Пам'ять дискретної GPU)", size=12, bold=True, color=INK))
    f.append(text(895, 283, "TTM_PL_VRAM (GDDR/HBM)", size=11, bold=True, color=FIELD))
    f.append(text(895, 307, "TTM_PL_TT (GTT / IOMMU)", size=11, color=MUTED))
    f.append(text(895, 331, "Витіснення та міграція", size=11, color=MUTED))

    f.append(rect(770, 390, 250, 105, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(895, 417, "CMA / DMA Coherent", size=12, bold=True, color=INK))
    f.append(text(895, 443, "Неперервний блок RAM", size=11, color=MUTED))
    f.append(text(895, 467, "Для простих дисплеїв SoC", size=11, color=MUTED))

    # Стрілки до бекендів
    f.append(arrow(700, 150, 770, 150, color=NEG))
    f.append(arrow(700, 297, 770, 297, color=FIELD))
    f.append(arrow(700, 442, 770, 442, color=POS))

    render(os.path.join(IMG, 'gem-object-architecture.svg'), W, H, *f)


def fig_fake_offset_mmap():
    """Механізм DRM fake offset: адресація сотень незалежних буферів через один дескриптор пристрою."""
    W, H = 1080, 520
    f = []

    # 1. Запит у просторі користувача
    f.append(fitbox(40, 80, 260, 90,
                    "1. Запит зміщення:\nioctl(fd, DRM_IOCTL_MODE_MAP_DUMB)\nповертає fake_offset = 0x10000000",
                    size=12, fill="#eef2ff", stroke=NEG))

    f.append(fitbox(40, 230, 260, 90,
                    "2. Відображення пам'яті:\nmmap(NULL, size, PROT_READ|WRITE,\nMAP_SHARED, fd, 0x10000000)\nповертає ptr_cpu",
                    size=12, fill="#eef2ff", stroke=NEG))

    f.append(fitbox(40, 380, 260, 90,
                    "3. Звернення до пам'яті:\nptr_cpu[0] = 0xFFFFFFFF\nгенерує Page Fault (якщо не завантажено)",
                    size=12, fill="#fdecea", stroke=POS))

    # 2. Менеджер фальшивих зміщень ядра
    f.append(rect(350, 40, 360, 440, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(530, 70, "drm_vma_offset_manager (Дерево RB)", size=14, bold=True, color=INK))

    f.append(fitbox(370, 95, 320, 75,
                    "Вузол Буфера 1: [0x00000000 .. 0x00FFFFFF]\nGEM Object #1 (Текстура 16 MiB)",
                    size=11, fill=FILL, stroke=LINE))

    f.append(fitbox(370, 195, 320, 85,
                    "Вузол Буфера 2: [0x10000000 .. 0x107FFFFF]\nGEM Object #2 (Фреймбуфер 8 MiB)\n-> Відповідає зміщенню 0x10000000!",
                    size=11, fill="#eaf7ee", stroke=FIELD))

    f.append(fitbox(370, 305, 320, 75,
                    "Вузол Буфера 3: [0x20000000 .. 0x20007FFF]\nGEM Object #3 (Курсор 32 KiB)",
                    size=11, fill=FILL, stroke=LINE))

    f.append(text(530, 420, "Єдиний простір зміщень для /dev/dri/card0", size=12, color=MUTED))
    f.append(text(530, 445, "Ключ пошуку — номер початкової сторінки vma->vm_pgoff", size=11, color=MUTED))

    # 3. Обробник VFS та сторінковий збій
    f.append(rect(760, 40, 280, 440, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(900, 70, "Обробник сторінкових збоїв", size=14, bold=True, color=INK))

    f.append(fitbox(780, 110, 240, 90,
                    "vma->vm_ops = &drm_gem_vm_ops\nДиспетчер перехоплює mmap\nчерез drm_vma_offset_lookup_locked()",
                    size=11, fill=FILL, stroke=LINE))

    f.append(fitbox(780, 240, 240, 110,
                    "vm_ops->fault() (наприклад,\ndrm_gem_shmem_fault):\n1. Читає сторінку з shmem\n2. Отримує struct page\n3. Встановлює запис PTE процесу",
                    size=11, fill="#eaf7ee", stroke=FIELD))

    f.append(fitbox(780, 385, 240, 75,
                    "Пам'ять доступна процесору:\nПрямий запис у кеш процесора\n(Write-Combine або Uncached)",
                    size=11, fill="#fdecea", stroke=POS))

    # Зв'язки
    f.append(arrow(300, 125, 370, 220, color=NEG))
    f.append(arrow(300, 275, 370, 240, color=NEG))
    f.append(arrow(300, 425, 780, 295, color=POS))
    f.append(arrow(690, 237, 780, 155, color=FIELD))
    f.append(arrow(900, 350, 900, 385, color=FIELD))

    render(os.path.join(IMG, 'fake-offset-mmap.svg'), W, H, *f)


def fig_prime_sharing_flow():
    """Спільне використання буферів через PRIME та dma-buf між процесами або відеокартами."""
    W, H = 1120, 520
    f = []

    # Процес 1: Рендерер
    f.append(rect(40, 40, 320, 440, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(200, 70, "Процес-виробник (3D гра)", size=14, bold=True, color=INK))
    f.append(fitbox(60, 100, 280, 70, "1. Створення буфера кадру\nХендл H1 = 4 у /dev/dri/renderD128\nGEM Object (Розмір 1920x1080 RGBA)", size=12, fill="#eef2ff", stroke=NEG))
    f.append(fitbox(60, 195, 280, 80, "2. Експорт у dma-buf\nioctl(PRIME_HANDLE_TO_FD, H1)\n-> Створює struct dma_buf у ядрі\n-> Повертає анонімний fd = 12", size=12, fill="#eef2ff", stroke=NEG))
    f.append(fitbox(60, 305, 280, 80, "3. Передача дескриптора\nsendmsg(unix_socket, SCM_RIGHTS, fd=12)\nПередає володіння дескриптором\nчерез сокет Wayland IPC", size=12, fill=FILL, stroke=LINE))
    f.append(text(200, 430, "GPU рендерить кадр у буфер", size=12, bold=True, color=FIELD))

    # Центральна частина: Ядро Linux і dma-buf
    f.append(rect(400, 40, 320, 440, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(560, 70, "Ядро Linux: dma-buf & PRIME", size=14, bold=True, color=INK))
    f.append(fitbox(420, 110, 280, 110, "struct dma_buf\n- file->f_count (лічильник посилань)\n- ops -> drm_gem_prime_dmabuf_ops\n- resv -> спільний dma_resv\n- priv -> вказівник на GEM Object", size=11, fill="#eaf7ee", stroke=FIELD))
    f.append(fitbox(420, 250, 280, 100, "Фізичні сторінки пам'яті\n(sg_table / TTM VRAM)\nЄдиний масив пікселів у пам'яті!\nКопіювання байтів ВІДСУТНЄ (Zero-Copy)", size=11, fill="#fdf3e7", stroke=POS))
    f.append(fitbox(420, 375, 280, 85, "Апаратна синхронізація\ndma_fence в об'єкті dma_resv\nзахищає буфер від одночасного\nзапису та читання", size=11, fill=FILL, stroke=LINE))

    # Процес 2: Споживач
    f.append(rect(760, 40, 320, 440, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(920, 70, "Процес-споживач (Wayland / KMS)", size=14, bold=True, color=INK))
    f.append(fitbox(780, 100, 280, 75, "4. Прийом дескриптора\nrecvmsg(unix_socket, &prime_fd)\nОтримує локальний fd = 8", size=12, fill=FILL, stroke=LINE))
    f.append(fitbox(780, 195, 280, 85, "5. Імпорт у GEM драйвера\nioctl(PRIME_FD_TO_HANDLE, fd=8)\n-> Отримує локальний Хендл H2 = 9\nу своєму /dev/dri/card0", size=12, fill="#eef2ff", stroke=NEG))
    f.append(fitbox(780, 305, 280, 80, "6. Виведення на дисплей\ndrmModeAddFB2() з хендлом H2\n-> Атомарний коміт у KMS площину\n(Direct Scanout без копіювання)", size=12, fill="#eaf7ee", stroke=FIELD))
    f.append(text(920, 430, "Контролер дисплея читає пікселі", size=12, bold=True, color=POS))

    # Зв'язки стрілками
    f.append(arrow(340, 235, 420, 165, color=NEG))
    f.append(arrow(340, 345, 780, 137, color=LINE))
    f.append(arrow(780, 237, 700, 165, color=NEG))
    f.append(arrow(560, 220, 560, 250, color=FIELD))
    f.append(arrow(560, 350, 560, 375, color=FIELD))
    f.append(arrow(700, 300, 780, 345, color=POS))

    render(os.path.join(IMG, 'prime-sharing-flow.svg'), W, H, *f)


def fig_dma_resv_fencing():
    """Синхронізація доступу до буфера через dma_resv: читачі, письменники та часова лінія огорож."""
    W, H = 1080, 480
    f = []

    # Об'єкт dma_resv
    f.append(rect(40, 40, 400, 400, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(240, 70, "struct dma_resv (у GEM-об'єкті)", size=15, bold=True, color=INK))

    f.append(fitbox(60, 95, 360, 65,
                    "Блокування: ww_mutex (Wound-Wait)\nЗапобігає взаємному блокуванню (Deadlock)\nпри захопленні багатьох буферів одночасно",
                    size=11, fill=FILL, stroke=LINE))

    f.append(fitbox(60, 175, 360, 110,
                    "Слот запису (DMA_RESV_USAGE_WRITE):\ndma_fence_write (Огородження GPU-рендерингу)\n- Стан: Очікує завершення шейдерів кадру N\n- Гарантує: Буфер не читатиметься до готовності",
                    size=11, fill="#fdecea", stroke=POS))

    f.append(fitbox(60, 300, 360, 120,
                    "Слоти читання (DMA_RESV_USAGE_READ):\n1. dma_fence_scanout (Контролер дисплея KMS)\n2. dma_fence_video (Апаратний енкодер NVENC)\n- Дозволяє паралельне читання багатьма клієнтами\n- Блокує новий запис до завершення читання",
                    size=11, fill="#eaf7ee", stroke=FIELD))

    # Часова лінія виконання операцій
    f.append(rect(480, 40, 560, 400, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(760, 70, "Часова лінія асинхронного виконання", size=15, bold=True, color=INK))

    # Вісь часу
    f.append(arrow(510, 400, 1010, 400, color=LINE, sw=2))
    f.append(text(980, 425, "Час (t)", size=12, bold=True, color=INK))

    # Етап 1: GPU рендерить
    f.append(rect(520, 110, 200, 60, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    f.append(text(620, 135, "GPU Рендеринг", size=12, bold=True, color=POS))
    f.append(text(620, 155, "Запис у буфер", size=11, color=MUTED))

    f.append(line(720, 110, 720, 395, color=POS, sw=1.2, dash="4,4"))
    f.append(text(720, 95, "Огорожа сигналізує: Готово!", size=11, bold=True, color=POS))

    # Етап 2: Паралельне читання дисплеєм та енкодером
    f.append(rect(730, 185, 230, 50, fill="#eaf7ee", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(845, 205, "KMS Display Scanout (Читання)", size=11, bold=True, color=FIELD))
    f.append(text(845, 223, "Виведення на панель екрана", size=10, color=MUTED))

    f.append(rect(730, 245, 230, 50, fill="#eaf7ee", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(845, 265, "Video Encoder (Читання)", size=11, bold=True, color=FIELD))
    f.append(text(845, 283, "Кодування стріму H.264/AV1", size=10, color=MUTED))

    f.append(line(960, 185, 960, 395, color=FIELD, sw=1.2, dash="4,4"))
    f.append(text(960, 170, "Читачі завершили", size=11, bold=True, color=FIELD))

    # Етап 3: Наступний запис кадру N+1
    f.append(rect(970, 110, 50, 60, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    f.append(text(995, 145, "N+1", size=11, bold=True, color=POS))

    # Пояснювальний текст
    f.append(text(760, 335, "CPU подає роботу без затримок (Non-blocking submit)", size=12, color=INK))
    f.append(text(760, 360, "Апаратні черги GPU/KMS самі чекають на сигнали огорож", size=11, color=MUTED))

    # Стрілки зв'язку
    f.append(arrow(420, 230, 520, 140, color=POS))
    f.append(arrow(420, 360, 730, 210, color=FIELD))

    render(os.path.join(IMG, 'dma-resv-fencing.svg'), W, H, *f)


if __name__ == '__main__':
    fig_gem_object_architecture()
    fig_fake_offset_mmap()
    fig_prime_sharing_flow()
    fig_dma_resv_fencing()
    print("All figures generated successfully.")
