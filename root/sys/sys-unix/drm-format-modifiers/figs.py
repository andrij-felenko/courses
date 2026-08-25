# -*- coding: utf-8 -*-
"""Фігури до теми «Формати й модифікатори буфера: fourcc і розкладка пам'яті»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_linear_vs_tiling():
    """Лінійне розташування пікселів проти 2D-тайлінгу в пам'яті."""
    W, H = 1000, 520
    f = []

    # Заголовок / фон
    f.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Ліва колонка: Лінійна розкладка (Linear / Pitch)
    f.append(fitbox(40, 30, 430, 40, "Лінійна розкладка (Linear / Pitch-linear)", size=14, bold=True))
    f.append(text(255, 90, "Пікселі зберігаються суцільними рядками", size=12, color=MUTED))

    # Сітка 4x4 пікселі ліворуч
    gx, gy = 70, 120
    cw, ch = 80, 50
    colors_lin = ["#e8f4f8", "#d1e8f2", "#b9ddec", "#a2d1e6",
                  "#fceae8", "#f9d5d2", "#f6bfbb", "#f3aaa5",
                  "#eaf7ee", "#d4efdd", "#bee7cc", "#a8dfbb",
                  "#fef8e7", "#fdf0cf", "#fce9b7", "#fae29f"]
    
    for row in range(4):
        for col in range(4):
            idx = row * 4 + col
            px = gx + col * cw
            py = gy + row * ch
            f.append(rect(px, py, cw, ch, fill=colors_lin[idx], stroke=LINE, sw=1.2))
            f.append(text(px + cw / 2, py + ch / 2 + 5, f"({col},{row})", size=12, bold=True))

    # Стрілки звернення для лінійного: 2D фільтрація 2x2 зразка
    f.append(rect(gx + cw - 4, gy + ch - 4, cw * 2 + 8, ch * 2 + 8, fill="none", stroke=POS, sw=2.5, rx=4))
    f.append(text(255, 350, "Вибірка 2×2 пікселів (текстурування/фільтрація):", size=12, bold=True, color=POS))
    f.append(text(255, 375, "Рядок 0: адреса 0x0000 + x·4", size=12, color=INK))
    f.append(text(255, 395, "Рядок 1: адреса 0x0000 + pitch (стрибок на 15 КБ!)", size=12, color=POS))
    f.append(text(255, 420, "Наслідок: 2 різні кеш-лінії й сторінки DRAM", size=12, color=MUTED))
    f.append(text(255, 440, "Промах кеша L1/L2 GPU та падіння пропускної здатності", size=12, color=POS))

    # Розділювач
    f.append(line(500, 30, 500, 480, color="#d0d5dd", sw=1.5, dash="6,6"))

    # Права колонка: Тайлова розкладка (Tiled / Block-linear)
    f.append(fitbox(530, 30, 430, 40, "Тайлова розкладка (2D Tiled / Block-linear)", size=14, bold=True))
    f.append(text(745, 90, "Пікселі згруповані у 2D-блоки (4×4, 16×16, 4 КБ)", size=12, color=MUTED))

    # 4 тайли 2x2
    tx, ty = 560, 120
    for trow in range(2):
        for tcol in range(2):
            tile_num = trow * 2 + tcol
            tile_bx = tx + tcol * (cw * 2 + 16)
            tile_by = ty + trow * (ch * 2 + 16)
            # Фон тайла
            f.append(rect(tile_bx - 4, tile_by - 4, cw * 2 + 8, ch * 2 + 8, fill="#f4f6f8", stroke=FIELD, sw=1.8, rx=6))
            f.append(text(tile_bx + cw, tile_by - 10, f"Тайл #{tile_num} (суцільний блок пам'яті)", size=11, color=FIELD, bold=True))
            for r in range(2):
                for c in range(2):
                    orig_col = tcol * 2 + c
                    orig_row = trow * 2 + r
                    idx = orig_row * 4 + orig_col
                    px = tile_bx + c * cw
                    py = tile_by + r * ch
                    f.append(rect(px, py, cw, ch, fill=colors_lin[idx], stroke=LINE, sw=1.2))
                    f.append(text(px + cw / 2, py + ch / 2 + 5, f"({orig_col},{orig_row})", size=12, bold=True))

    # Стрілки звернення для тайлового
    f.append(rect(tx - 2, ty - 2, cw * 2 + 4, ch * 2 + 4, fill="none", stroke=FIELD, sw=2.5, rx=4))
    f.append(text(745, 350, "Вибірка 2×2 пікселів у межах тайла:", size=12, bold=True, color=FIELD))
    f.append(text(745, 375, "Усі 4 сусідні пікселі лежать в одній кеш-лінії 64 Б", size=12, color=INK))
    f.append(text(745, 395, "Збереження 2D просторової локальності (spatial locality)", size=12, color=FIELD))
    f.append(text(745, 420, "100% попадання в кеш L1 текстурного семплера GPU", size=12, color=MUTED))
    f.append(text(745, 440, "Економія 30–50% енергії та пропускної здатності VRAM", size=12, color=FIELD))

    render(os.path.join(IMG, 'linear-vs-tiling.svg'), W, H, *f)


def fig_modifier_64bit_structure():
    """Структура 64-бітного модифікатора формату DRM."""
    W, H = 1000, 480
    f = []

    f.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    f.append(fitbox(40, 24, 920, 44, "Анатомія 64-бітного модифікатора формату DRM (uint64_t modifier)", size=15, bold=True))

    # 64-бітне поле: верхні 8 бітів та нижні 56 бітів
    y_bar = 90
    # Vendor ID (bits 63..56)
    f.append(rect(50, y_bar, 220, 54, fill="#fdecea", stroke=POS, sw=2, rx=4))
    f.append(text(160, y_bar + 24, "Vendor ID (8 бітів)", size=13, bold=True, color=POS))
    f.append(text(160, y_bar + 44, "біти [63 .. 56]", size=11, color=MUTED))

    # Layout / Mod code (bits 55..0)
    f.append(rect(280, y_bar, 670, 54, fill="#eaf7ee", stroke=FIELD, sw=2, rx=4))
    f.append(text(615, y_bar + 24, "Специфічний для виробника код розкладки пам'яті (56 бітів)", size=13, bold=True, color=FIELD))
    f.append(text(615, y_bar + 44, "біти [55 .. 0]: тайлінг, геометрія блоків, стиснення, aux-площини", size=11, color=MUTED))

    # Макрос fourcc_mod_code
    f.append(fitbox(50, 160, 900, 36, "Формування: #define fourcc_mod_code(vendor, val) ((((uint64_t)DRM_FORMAT_MOD_VENDOR_##vendor) << 56) | ((val) & 0x00ffffffffffffffULL))", size=12))

    # Приклади значень вендорів
    y_v = 220
    f.append(text(50, y_v + 14, "Ідентифікатори виробників (Vendor ID):", size=13, bold=True, anchor="start"))
    
    vendors = [
        ("NONE (0x00)", "DRM_FORMAT_MOD_LINEAR (суцільний растровий порядок)", "#333333"),
        ("INTEL (0x01)", "I915_FORMAT_MOD_X_TILED, Y_TILED, 4_TILED, 4_TILED_DG2_RC_CCS", "#0066cc"),
        ("AMD (0x02)", "AMD_FMT_MOD_TILE_GFX9_64K_S, AMD_FMT_MOD_DCC, DCC_RETILE", "#cc0000"),
        ("NVIDIA (0x03)", "DRM_FORMAT_MOD_NVIDIA_BLOCK_LINEAR_2D(h, kind, gen)", "#76b900"),
        ("ARM (0x08)", "AFBC_FORMAT_MOD_BLOCK_SIZE_16x16, AFBC_FORMAT_MOD_SPARSE", "#009999"),
        ("BROADCOM (0x07)", "DRM_FORMAT_MOD_BROADCOM_VC4_T_TILED, SAND128", "#d97706"),
    ]

    vy = y_v + 30
    for v_name, v_desc, v_col in vendors:
        f.append(rect(50, vy, 180, 28, fill="#f4f6f8", stroke=v_col, sw=1.5, rx=3))
        f.append(text(140, vy + 19, v_name, size=11, bold=True, color=v_col))
        f.append(text(245, vy + 19, v_desc, size=11, color=INK, anchor="start"))
        vy += 34

    render(os.path.join(IMG, 'modifier-64bit-structure.svg'), W, H, *f)


def fig_aux_planes_and_compression():
    """Багатоплощинна структура буфера зі стисненням метаданих."""
    W, H = 1000, 500
    f = []

    f.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    f.append(fitbox(40, 20, 920, 44, "Багатоплощинна структура буфера: основні пікселі та площини метаданих стиснення", size=14, bold=True))

    # Логічний буфер кадру зверху
    f.append(fitbox(250, 80, 500, 46, "Логічний Framebuffer (3840×2160, DRM_FORMAT_ARGB8888, Modifier: Tile4 + CCS)", size=13, bold=True, fill="#dceffe", stroke=NEG))

    # Стрілки розгалуження на площини
    f.append(arrow(380, 126, 200, 180, color=NEG))
    f.append(arrow(500, 126, 500, 180, color=FIELD))
    f.append(arrow(620, 126, 800, 180, color=POS))

    # Площина 0: Основні пікселі
    f.append(rect(50, 180, 300, 170, fill="#f4f8fc", stroke=NEG, sw=1.8, rx=6))
    f.append(text(200, 206, "Площина 0 (Plane 0): Колір", size=13, bold=True, color=NEG))
    f.append(text(200, 230, "dma-buf FD: handles[0]", size=11, color=MUTED))
    f.append(text(200, 252, "Розкладка: Tile4 (4 КБ тайли)", size=11, color=INK))
    f.append(text(200, 274, "Pitch: pitches[0] = 15360 байтів", size=11, color=INK))
    f.append(text(200, 296, "Offset: offsets[0] = 0", size=11, color=INK))
    f.append(text(200, 324, "Розмір: ~33.17 МБ стиснених пікселів", size=11, color=NEG, bold=True))

    # Площина 1: CCS / DCC метадані
    f.append(rect(360, 180, 300, 170, fill="#f4fbf6", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(510, 206, "Площина 1 (Plane 1): Метадані CCS", size=13, bold=True, color=FIELD))
    f.append(text(510, 230, "dma-buf FD: handles[1] (або той самий)", size=11, color=MUTED))
    f.append(text(510, 252, "Призначення: теги стиснення блоків", size=11, color=INK))
    f.append(text(510, 274, "Співвідношення: 1 байт на 256 Б даних", size=11, color=INK))
    f.append(text(510, 296, "Offset: offsets[1] = +33.17 МБ", size=11, color=INK))
    f.append(text(510, 324, "Розмір: ~130 КБ бітових масок RLE", size=11, color=FIELD, bold=True))

    # Площина 2: Clear Color (швидке очищення)
    f.append(rect(670, 180, 280, 170, fill="#fef6f5", stroke=POS, sw=1.8, rx=6))
    f.append(text(810, 206, "Площина 2 (Plane 2): Clear Color", size=13, bold=True, color=POS))
    f.append(text(810, 230, "dma-buf FD: handles[2]", size=11, color=MUTED))
    f.append(text(810, 252, "Призначення: колір фону (RGBA)", size=11, color=INK))
    f.append(text(810, 274, "Дозволяє glClear() без запису", size=11, color=INK))
    f.append(text(810, 296, "всього 33 МБ буфера у VRAM", size=11, color=INK))
    f.append(text(810, 324, "Розмір: 64 байти (1 кеш-лінія)", size=11, color=POS, bold=True))

    # Нижня рамка ioctl DRM_IOCTL_MODE_ADDFB2
    f.append(rect(50, 380, 900, 95, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    f.append(text(500, 404, "Системний виклик: ioctl(drm_fd, DRM_IOCTL_MODE_ADDFB2, &cmd2)", size=13, bold=True))
    f.append(text(500, 428, "cmd2.flags = DRM_MODE_FB_MODIFIERS;  cmd2.modifier[0..2] = I915_FORMAT_MOD_4_TILED_DG2_RC_CCS;", size=11, color=NEG))
    f.append(text(500, 452, "Контролер дисплея KMS апаратно розпаковує потік пікселів «на льоту» під час сканування рядків", size=11, color=MUTED))

    render(os.path.join(IMG, 'aux-planes-and-compression.svg'), W, H, *f)


def fig_dmabuf_modifier_negotiation():
    """Узгодження модифікаторів між Wayland-клієнтом, композитором і KMS."""
    W, H = 1020, 540
    f = []

    f.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    f.append(fitbox(40, 16, 940, 42, "Узгодження модифікаторів через wp_linux_dmabuf_feedback_v1 і Zero-Copy Scanout", size=14, bold=True))

    C_CLI, C_SRV, C_KMS = 160, 510, 860

    f.append(fitbox(C_CLI - 120, 70, 240, 40, "Клієнт (Vulkan / EGL / GBM)", size=13, bold=True))
    f.append(fitbox(C_SRV - 130, 70, 260, 40, "Wayland Compositor (Weston/Sway)", size=13, bold=True))
    f.append(fitbox(C_KMS - 120, 70, 240, 40, "Драйвер KMS / Дисплейний блок", size=13, bold=True))

    # Лінії життя
    f.append(line(C_CLI, 110, C_CLI, 490, color=MUTED, sw=1.2, dash="5,5"))
    f.append(line(C_SRV, 110, C_SRV, 490, color=MUTED, sw=1.2, dash="5,5"))
    f.append(line(C_KMS, 110, C_KMS, 490, color=MUTED, sw=1.2, dash="5,5"))

    def step(y, x1, x2, label, color=LINE, dash=False):
        f.append(arrow(x1, y, x2, y, color=color))
        if dash:
            f.append(line(x1, y, x2, y, color=BG, sw=3))
            f.append(line(x1, y, x2, y, color=color, sw=1.5, dash="6,4"))
            f.append(arrow(x2 - 12 if x2 > x1 else x2 + 12, y, x2, y, color=color))
        f.append(text((x1 + x2) / 2, y - 10, label, size=11, color=color))

    step(150, C_KMS, C_SRV, "1. IN_FORMATS blob: площина підтримує [Tile4, Y-Tile, Linear]", color=MUTED, dash=True)
    step(200, C_SRV, C_CLI, "2. feedback.tranche: Scanout tranche = {ARGB8888: Tile4, Linear}", color=FIELD)
    step(250, C_CLI, C_CLI + 1, "3. gbm_bo_create_with_modifiers(ARGB8888, [Tile4, Linear]) → обирає Tile4", color=NEG)
    step(300, C_CLI, C_SRV, "4. wl_surface.attach(dma-buf FD, modifier=Tile4)", color=NEG)
    step(360, C_SRV, C_KMS, "5. Атомарний тест: drmModeAtomicCommit(TEST_ONLY, FB(Tile4)) → УСПІХ", color=FIELD)
    step(420, C_SRV, C_KMS, "6. Direct Scanout: FB виводиться напряму на дисплейну площину без копій!", color=POS)

    # Примітка внизу
    f.append(rect(50, 460, 920, 60, fill="#eaf7ee", stroke=FIELD, sw=1.5, rx=5))
    f.append(text(510, 485, "Zero-Copy Direct Scanout: 0% навантаження на GPU композитора, мінімальна затримка кадру (input lag),", size=12, bold=True, color=FIELD))
    f.append(text(510, 505, "якщо клієнт обрав модифікатор, з яким апаратно сумісний контролер сканування дисплея KMS.", size=11, color=MUTED))

    render(os.path.join(IMG, 'dmabuf-modifier-negotiation.svg'), W, H, *f)


if __name__ == '__main__':
    fig_linear_vs_tiling()
    fig_modifier_64bit_structure()
    fig_aux_planes_and_compression()
    fig_dmabuf_modifier_negotiation()
    print("ok")
