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
RED_FILL = "#fdecea"
GREY_FILL = "#eceff1"


# ── 1. Архітектура virtio-mem та sub-block unplug ────────────────────────────
def fig_virtio_mem_arch():
    W, H = 1480, 920
    p = []
    cx = 740

    p.append(text(cx, 45, "АРХІТЕКТУРА VIRTIO-MEM: SUB-BLOCK MEMORY HOTPLUG", size=16, bold=True))
    p.append(text(cx, 70, "Господар керує requested_size; гість динамічно онлайнить і офлайнить блоки по 2-4 МБ",
                  size=12.5, color=MUTED))

    # Господар / QEMU
    qemu_box, _, _ = textbox(cx, 145, [
        "ГОСПОДАР (QEMU / KVM)",
        "Задає requested_size у регістрі конфігурації | Отримує сповіщення через virtqueue"
    ], size=13, pad=15, fill=WARM_FILL, stroke=LINE, sw=1.6, min_w=900)
    p.append(qemu_box)

    p.append(arrow(cx, 185, cx, 245))

    # Драйвер у ядрі гостя
    drv_box, _, _ = textbox(cx, 280, [
        "ДРАЙВЕР ГОСТЯ (virtio_mem.ko)",
        "Обробляє переривання конфігурації · Керує станом блоків · Взаємодіє з Buddy Allocator"
    ], size=13, pad=15, fill=BLUE_FILL, stroke=LINE, sw=1.6, min_w=900)
    p.append(drv_box)

    p.append(arrow(cx, 320, cx, 380))

    p.append(text(cx, 400, "НЕПЕРЕРВНЕ ВІКНО АДРЕС ГОСТЯ (GPA WINDOW — наприклад 128 ГБ)", size=13.5, bold=True))

    # Схема блоків у пам'яті
    blocks = [
        ("Блок #0 (4 МБ)", "PLUGGED / ONLINE\n(ZONE_NORMAL)", GREEN_FILL),
        ("Блок #1 (4 МБ)", "PLUGGED / UNMOVABLE\n(пропущено при unplug)", RED_FILL),
        ("Блок #2 (4 МБ)", "PLUGGED / ONLINE\n(ZONE_MOVABLE)", GREEN_FILL),
        ("Блок #3 (4 МБ)", "UNPLUGGED / OFFLINE\n(повернуто господарю)", GREY_FILL),
    ]

    bx_positions = [240, 570, 900, 1230]
    for b_x, (b_title, b_status, fill) in zip(bx_positions, blocks):
        lines = [b_title] + b_status.split('\n')
        box, _, _ = textbox(b_x, 485, lines, size=12, pad=12, fill=fill, stroke=LINE, sw=1.4, min_w=280)
        p.append(box)

    # Пояснення до повернення пам'яті
    info_box, _, _ = textbox(cx, 630, [
        "Гнучкість sub-block unplug:",
        "Якщо Блок #1 містить непереміщувані дані ядра (unmovable pages), virtio-mem пропускає його,",
        "але успішно повертає господарю Блок #3. На відміну від ACPI DIMM, система не блокується повністю."
    ], size=12.5, pad=14, fill=GREEN_FILL, stroke=FIELD, sw=1.3, min_w=960)
    p.append(info_box)

    # Підсистема allocator у ядрі
    buddy_box, _, _ = textbox(cx, 780, [
        "ПІДСИСТЕМА ПАМ'ЯТІ LINUX (buddy allocator / zone_movable)",
        "add_memory_driver_managed() · offline_pages() · alloc_contig_range()"
    ], size=12.5, pad=14, fill=BLUE_FILL, stroke=MUTED, sw=1.2, min_w=960)
    p.append(buddy_box)

    p.append(arrow(cx, 690, cx, 735))

    render(os.path.join(IMG, 'virtio-mem-architecture.svg'), W, H, *p,
           title="Архітектура virtio-mem та механізм sub-block memory hotplug")


# ── 2. Шлях даних та флаш-запити virtio-pmem ─────────────────────────────────
def fig_virtio_pmem_dax_flush():
    W, H = 1480, 880
    p = []
    lx, rx = 400, 1080

    p.append(text(740, 45, "КАНАЛИ ДАНИХ ТА ГАРАНТІЯ НАДІЙНОСТІ VIRTIO-PMEM", size=16, bold=True))
    p.append(text(740, 70, "Прямий доступ (DAX) оминає кеш гостя, а флаш-запити через virtqueue гарантують скидання на диски хоста",
                  size=12.5, color=MUTED))

    # Лівий канал: DAX read/write
    p.append(text(lx, 120, "1. ШЛЯХ ЧИТАННЯ ТА ЗАПИСУ (DAX / mmap)", size=14, bold=True))
    dax_app, _, _ = textbox(lx, 180, ["Додаток у гості (mmap)"], size=13, pad=13, fill=GREEN_FILL, stroke=LINE, sw=1.4, min_w=460)
    p.append(dax_app)
    p.append(arrow(lx, 215, lx, 275))

    dax_fs, _, _ = textbox(lx, 310, ["Файлова система гостя (ext4 / XFS -o dax)"], size=13, pad=13, fill=GREEN_FILL, stroke=LINE, sw=1.4, min_w=460)
    p.append(dax_fs)
    p.append(arrow(lx, 345, lx, 405))

    dax_bar, _, _ = textbox(lx, 440, ["Прямий доступ до BAR пам'яті хоста\n(Без копіювання в page cache гостя)"], size=12.5, pad=13, fill=BLUE_FILL, stroke=LINE, sw=1.4, min_w=460)
    p.append(dax_bar)

    # Правий канал: Durability / Virtqueue Flush
    p.append(text(rx, 120, "2. ШЛЯХ ФЛАШУ ВІРТУАЛЬНОЇ ПЕРЗИСТЕНТНОСТІ", size=14, bold=True))
    flush_req, _, _ = textbox(rx, 180, ["Запит на надійний скид: fsync() / msync()"], size=13, pad=13, fill=WARM_FILL, stroke=LINE, sw=1.4, min_w=460)
    p.append(flush_req)
    p.append(arrow(rx, 215, rx, 275))

    virtio_drv, _, _ = textbox(rx, 310, ["virtio_pmem.ko (виправка VIRTIO_PMEM_REQ_TYPE_FLUSH)"], size=13, pad=13, fill=WARM_FILL, stroke=LINE, sw=1.4, min_w=460)
    p.append(virtio_drv)
    p.append(arrow(rx, 345, rx, 405))

    host_qemu, _, _ = textbox(rx, 440, ["Обробник QEMU у хості: виконання fsync() / msync()\nна бекенд-файлі або NVDIMM host"], size=12.5, pad=13, fill=RED_FILL, stroke=LINE, sw=1.4, min_w=460)
    p.append(host_qemu)

    p.append(line(740, 110, 740, 520, color=MUTED, sw=1.2, dash="7 6"))

    # Нижній синтез
    syn_box, _, _ = textbox(740, 660, [
        "Чому звичайні CPU-інструкції (clwb/clflush) не гарантують збереження в VM:",
        "Інструкція clwb гостя виштовхує дані з кешу CPU у кеш сторінок хоста або контролер RAID хоста.",
        "При аварійному вимкненні хоста ці дані втрачаються. Лише virtio_pmem flush через virtqueue",
        "примушує ядро хоста записати дані на фізичний енергонезалежний носій."
    ], size=12.5, pad=16, fill=WARM_FILL, stroke=FIELD, sw=1.4, min_w=1280)
    p.append(syn_box)

    render(os.path.join(IMG, 'virtio-pmem-dax-flush.svg'), W, H, *p,
           title="Канали даних DAX та механізм флаш-запитів у virtio-pmem")


if __name__ == '__main__':
    fig_virtio_mem_arch()
    fig_virtio_pmem_dax_flush()
    print("ok")
