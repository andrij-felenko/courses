# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"


# ── 1. Зберігання контрольних сум: CSUM Tree та заголовки ─────────────────────
def fig_csum_tree_structure():
    W, H = 1200, 680
    p = []

    # Ліва колонка — Метадані
    cx1 = 300
    p.append(text(cx1, 50, "Вузол метаданих (Metadata Node / Leaf)", size=16, bold=True))

    f_meta, w_m, h_m = textbox(cx1, 190, [
        "struct btrfs_header",
        "csum: 0x8F3A21C0 (CRC32c / xxHash / SHA256)",
        "fsid, bytenr, flags, nritems, level",
        "--- Елементи B-дерева (Items & Keys) ---"
    ], size=13, pad=16, fill=WARM, stroke=LINE)
    p.append(f_meta)

    f_note1, w_n1, h_n1 = textbox(cx1, 440, [
        "Контрольна сума метаданих зберігається",
        "безпосередньо в заголовку кожного вузла.",
        "Перевіряється під час кожного зчитування вузла з диска."
    ], size=12, pad=14, fill=GREY, stroke=MUTED)
    p.append(f_note1)

    # Права колонка — Звичайні дані та CSUM Tree
    cx2 = 900
    p.append(text(cx2, 50, "Файлові дані (Data Extent) та CSUM Tree", size=16, bold=True))

    f_data, w_d, h_d = textbox(cx2, 140, [
        "Data Extent (Блок файлу на диску)",
        "Сектор 0 (4 КіБ) | Сектор 1 (4 КіБ) | Сектор 2 (4 КіБ)"
    ], size=13, pad=15, fill=GREEN, stroke=FIELD)
    p.append(f_data)

    f_csum_tree, w_ct, h_ct = textbox(cx2, 330, [
        "CSUM Tree (BTRFS_CSUM_TREE_OBJECTID)",
        "Key: [EXTENT_CSUM, offset = bytenr]",
        "struct btrfs_csum_item {",
        "  u8 csum[]: [0x12345678, 0x9ABCDEF0, 0x55AA3377]",
        "}"
    ], size=13, pad=16, fill=BLUE, stroke=LINE)
    p.append(f_csum_tree)

    p.append(arrow(cx2, 140 + h_d / 2 + 6, cx2, 330 - h_ct / 2 - 6))

    f_note2, w_n2, h_n2 = textbox(cx2, 530, [
        "Хеші для даних зберігаються окремо в CSUM Tree.",
        "Кожен сектор (4096 байт) має свій 32-бітний запис хешу.",
        "Відокремлення хешів захищає від фантомних записів."
    ], size=12, pad=14, fill=GREY, stroke=MUTED)
    p.append(f_note2)

    # Розділювач
    p.append(line(600, 40, 600, H - 40, color=MUTED, sw=1.2, dash="6 6"))

    render(os.path.join(IMG, 'btrfs-csum-tree-structure.svg'), W, H, *p,
           title="Організація зберігання контрольних сум у Btrfs")


# ── 2. Контроль цілісності та Самоновлення (Self-Healing) ────────────────────
def fig_scrub_repair_flow():
    W, H = 1260, 720
    p = []

    y1 = 90
    cx = 630

    f1, w1, h1 = textbox(cx, y1, [
        "Запит read() або процес btrfs scrub зчитує блок з Дзеркала 1"
    ], size=14, pad=15, fill=BLUE, stroke=LINE)
    p.append(f1)

    y2 = 220
    f2, w2, h2 = textbox(cx, y2, [
        "Обчислення CRC32c зчитаного блоку та порівняння з хешем із CSUM Tree"
    ], size=14, pad=15, fill=WARM, stroke=LINE)
    p.append(f2)
    p.append(arrow(cx, y1 + h1 / 2 + 6, cx, y2 - h2 / 2 - 6))

    # Перевірка збігу хешів
    y3 = 370
    lx, rx = 350, 910

    f_ok, wok, hok = textbox(lx, y3, [
        "Хеші збігаються (OK)",
        "Дані цілісні. Повертаємо блок додаткам"
    ], size=13, pad=14, fill=GREEN, stroke=FIELD)
    p.append(f_ok)

    f_bad, wbad, hbad = textbox(rx, y3, [
        "Помилка хешу (Checksum Mismatch / Bit Rot!)",
        "Дані пошкоджено! Генериться dmesg warning"
    ], size=13, pad=14, fill=RED, stroke=POS, sw=1.5)
    p.append(f_bad)

    p.append(arrow(cx - 100, y2 + h2 / 2 + 6, lx, y3 - hok / 2 - 6))
    p.append(arrow(cx + 100, y2 + h2 / 2 + 6, rx, y3 - hbad / 2 - 6))

    # Кроки відновлення праворуч
    y4 = 520
    f_repair1, wr1, hr1 = textbox(rx, y4, [
        "1. Зчитування резервної копії з Дзеркала 2 (mirror_num + 1)",
        "2. Перевірка хешу резервної копії"
    ], size=13, pad=14, fill=WARM, stroke=LINE)
    p.append(f_repair1)
    p.append(arrow(rx, y3 + hbad / 2 + 6, rx, y4 - hr1 / 2 - 6))

    y5 = 640
    f_repair2, wr2, hr2 = textbox(rx, y5, [
        "3. Повернення валидних даних користувачу",
        "4. Автоматичний перезапис пошкодженого сектора на Дзеркалі 1"
    ], size=13, pad=14, fill=GREEN, stroke=FIELD, bold=True)
    p.append(f_repair2)
    p.append(arrow(rx, y4 + hr1 / 2 + 6, rx, y5 - hr2 / 2 - 6))

    render(os.path.join(IMG, 'btrfs-scrub-repair-flow.svg'), W, H, *p,
           title="Механізм перевірки контрольних сум та самоновлення (Self-Healing)")


# ── 3. Мапування чанків та профілі RAID ──────────────────────────────────────
def fig_raid_stripe_chunk_mapping():
    W, H = 1240, 750
    p = []

    cx = 620
    y_log = 90

    f_log, wl, hl = textbox(cx, y_log, [
        "Логічний простір адресації Btrfs (Logical Address Space)",
        "Чанки: Data Chunk (1 ГБ) | Metadata Chunk (256 МБ)"
    ], size=14, pad=16, fill=BLUE, stroke=LINE, bold=True)
    p.append(f_log)

    y_tree = 230
    f_tree, wt, ht = textbox(cx, y_tree, [
        "Chunk Tree (BTRFS_CHUNK_TREE_OBJECTID)",
        "Мапує logical_bytenr -> (devid, physical_offset, profile)"
    ], size=13, pad=15, fill=WARM, stroke=LINE)
    p.append(f_tree)
    p.append(arrow(cx, y_log + hl / 2 + 6, cx, y_tree - ht / 2 - 6))

    # 3 диски нижче
    y_dev = 440
    d1_x, d2_x, d3_x = 240, 620, 1000

    f_d1, wd1, hd1 = textbox(d1_x, y_dev, [
        "Накопичувач /dev/sda",
        "Stripe 0 (Single/RAID1)",
        "Stripe 0 (RAID5 Data)"
    ], size=13, pad=15, fill=GREY, stroke=LINE)

    f_d2, wd2, hd2 = textbox(d2_x, y_dev, [
        "Накопичувач /dev/sdb",
        "Stripe 1 (RAID1 Mirror)",
        "Stripe 1 (RAID5 Data)"
    ], size=13, pad=15, fill=GREY, stroke=LINE)

    f_d3, wd3, hd3 = textbox(d3_x, y_dev, [
        "Накопичувач /dev/sdc",
        "Unallocated / Spare",
        "Stripe 2 (RAID5 Parity)"
    ], size=13, pad=15, fill=GREY, stroke=LINE)

    p.append(f_d1)
    p.append(f_d2)
    p.append(f_d3)

    p.append(arrow(cx - 150, y_tree + ht / 2 + 6, d1_x, y_dev - hd1 / 2 - 6))
    p.append(arrow(cx, y_tree + ht / 2 + 6, d2_x, y_dev - hd2 / 2 - 6))
    p.append(arrow(cx + 150, y_tree + ht / 2 + 6, d3_x, y_dev - hd3 / 2 - 6))

    # Зауваження про Write Hole у RAID5/6
    f_wh, wwh, hwh = textbox(cx, 650, [
        "Попередження RAID5/6: при раптовому збої живлення оновлення Stripe 0/1 та Parity",
        "може виявитися неатомним (Write Hole). Захист гарантується у профілях RAID1 / RAID1c3."
    ], size=12, pad=14, fill=RED, stroke=POS, sw=1.2)
    p.append(f_wh)

    render(os.path.join(IMG, 'btrfs-raid-stripe-chunk-mapping.svg'), W, H, *p,
           title="Мапування логічного простору чанків на фізичні накопичувачі")


if __name__ == '__main__':
    fig_csum_tree_structure()
    fig_scrub_repair_flow()
    fig_raid_stripe_chunk_mapping()
    print("Figures successfully generated!")
