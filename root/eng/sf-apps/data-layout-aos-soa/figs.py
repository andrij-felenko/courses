# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# Палітра для полів і розкладок
COLOR_X   = "#fdecea"   # світло-червоний (координата X)
STROKE_X  = "#c0392b"
COLOR_Y   = "#eaf0fd"   # світло-синій (координата Y)
STROKE_Y  = "#2457d6"
COLOR_Z   = "#eafaf1"   # світло-зелений (координата Z)
STROKE_Z  = "#27ae60"
COLOR_VX  = "#fef5e7"   # світло-помаранчевий (швидкість VX)
STROKE_VX = "#d35400"
COLOR_PAD = "#f2f4f4"   # сірий (непотрібні поля: mass, flags, id)
STROKE_PAD= "#7f8c8d"


# ── Фігура 1: Порівняння розташування даних у пам'яті: AoS, SoA та AoSoA ───────
def fig_memory_layouts():
    W, H = 1040, 680
    f = []

    # Загальний заголовок
    f.append(text(W / 2, 38, "Організація пам'яті: AoS, SoA та гібридний AoSoA", size=18, bold=True))
    f.append(text(W / 2, 60, "Використання 64-байтної кеш-лінії під час обробки лише координат X і Y", size=13, color=MUTED))

    # --- 1. AoS (Array of Structures) ---
    y1 = 100
    f.append(text(60, y1 + 18, "1. AoS (Array of Structures)", size=15, bold=True, anchor="start", color=INK))
    f.append(text(60, y1 + 38, "Об'єкти упереміж: x, y, z, mass, flags, id на кожну сутність", size=12, color=MUTED, anchor="start"))

    # Смуга пам'яті AoS
    cw = 48
    ch = 36
    x_start = 60
    cells_aos = [
        ("x0", COLOR_X, STROKE_X, True),
        ("y0", COLOR_Y, STROKE_Y, True),
        ("z0", COLOR_Z, STROKE_Z, False),
        ("m0", COLOR_PAD, STROKE_PAD, False),
        ("id0", COLOR_PAD, STROKE_PAD, False),
        ("fl0", COLOR_PAD, STROKE_PAD, False),
        ("x1", COLOR_X, STROKE_X, True),
        ("y1", COLOR_Y, STROKE_Y, True),
        ("z1", COLOR_Z, STROKE_Z, False),
        ("m1", COLOR_PAD, STROKE_PAD, False),
        ("id1", COLOR_PAD, STROKE_PAD, False),
        ("fl1", COLOR_PAD, STROKE_PAD, False),
        ("x2", COLOR_X, STROKE_X, True),
        ("y2", COLOR_Y, STROKE_Y, True),
        ("z2", COLOR_Z, STROKE_Z, False),
        ("m2", COLOR_PAD, STROKE_PAD, False),
    ]

    for i, (name, fill, stroke, is_hot) in enumerate(cells_aos):
        cx = x_start + i * cw
        f.append(rect(cx, y1 + 52, cw, ch, fill=fill, stroke=stroke, sw=1.4, rx=4))
        f.append(text(cx + cw / 2, y1 + 75, name, size=13, bold=is_hot, color=INK if is_hot else MUTED))

    # Кеш-лінія дужка
    cache_w = 16 * cw
    f.append(line(x_start, y1 + 96, x_start + cache_w, y1 + 96, color=POS, sw=2))
    f.append(line(x_start, y1 + 92, x_start, y1 + 102, color=POS, sw=2))
    f.append(line(x_start + cache_w, y1 + 92, x_start + cache_w, y1 + 102, color=POS, sw=2))
    f.append(text(x_start + cache_w / 2, y1 + 114, "Кеш-лінія L1 (64 байти): лише 24 байти корисні (37% утилізація шини, 63% баласт)", size=12, color=POS, bold=True))

    # --- 2. SoA (Structure of Arrays) ---
    y2 = 250
    f.append(text(60, y2 + 18, "2. SoA (Structure of Arrays)", size=15, bold=True, anchor="start", color=INK))
    f.append(text(60, y2 + 38, "Окремі однорідні масиви: 100% просторова локальність для циклів по полю", size=12, color=MUTED, anchor="start"))

    # Масив X
    f.append(text(40, y2 + 75, "X[]", size=13, bold=True, anchor="end", color=STROKE_X))
    for i in range(16):
        cx = x_start + i * cw
        f.append(rect(cx, y2 + 52, cw, ch, fill=COLOR_X, stroke=STROKE_X, sw=1.4, rx=4))
        f.append(text(cx + cw / 2, y2 + 75, f"x{i}", size=12, bold=True, color=INK))

    f.append(line(x_start, y2 + 96, x_start + cache_w, y2 + 96, color=FIELD, sw=2))
    f.append(line(x_start, y2 + 92, x_start, y2 + 102, color=FIELD, sw=2))
    f.append(line(x_start + cache_w, y2 + 92, x_start + cache_w, y2 + 102, color=FIELD, sw=2))
    f.append(text(x_start + cache_w / 2, y2 + 114, "Кеш-лінія X (64 байти): 16 елементів float32 поспіль — 100% корисних даних ідеально для Prefetcher", size=12, color=FIELD, bold=True))

    # Масив Y нижче
    f.append(text(40, y2 + 155, "Y[]", size=13, bold=True, anchor="end", color=STROKE_Y))
    for i in range(16):
        cx = x_start + i * cw
        f.append(rect(cx, y2 + 132, cw, ch, fill=COLOR_Y, stroke=STROKE_Y, sw=1.4, rx=4))
        f.append(text(cx + cw / 2, y2 + 155, f"y{i}", size=12, bold=True, color=INK))

    # --- 3. AoSoA (Tiled / Blocked SoA, розмір блоку = 8) ---
    y3 = 450
    f.append(text(60, y3 + 18, "3. AoSoA / Tiled SoA (блок = 8 під AVX2 / 256-бітний SIMD)", size=15, bold=True, anchor="start", color=INK))
    f.append(text(60, y3 + 38, "Масив тайлів: усередині кожного тайла поля лежать як SoA для SIMD-вектора", size=12, color=MUTED, anchor="start"))

    tile_w = 8 * cw
    # Тайл 0: X[0..7], Y[0..7]
    f.append(rect(x_start, y3 + 52, tile_w, ch * 2 + 16, fill="#fdfefe", stroke=LINE, sw=1.6, rx=6))
    f.append(text(x_start + tile_w / 2, y3 + 44, "Тайл 0 (частинки 0..7: 64 байти = 2×32B вектори)", size=12, bold=True, color=INK))

    for i in range(8):
        cx = x_start + i * cw + 4
        f.append(rect(cx, y3 + 58, cw - 8, ch - 4, fill=COLOR_X, stroke=STROKE_X, sw=1.3, rx=3))
        f.append(text(cx + (cw - 8) / 2, y3 + 80, f"x{i}", size=11, bold=True, color=INK))

        f.append(rect(cx, y3 + 96, cw - 8, ch - 4, fill=COLOR_Y, stroke=STROKE_Y, sw=1.3, rx=3))
        f.append(text(cx + (cw - 8) / 2, y3 + 118, f"y{i}", size=11, bold=True, color=INK))

    # Тайл 1: X[8..15], Y[8..15]
    x_tile1 = x_start + tile_w + 24
    f.append(rect(x_tile1, y3 + 52, tile_w, ch * 2 + 16, fill="#fdfefe", stroke=LINE, sw=1.6, rx=6))
    f.append(text(x_tile1 + tile_w / 2, y3 + 44, "Тайл 1 (частинки 8..15)", size=12, bold=True, color=INK))

    for i in range(8):
        cx = x_tile1 + i * cw + 4
        f.append(rect(cx, y3 + 58, cw - 8, ch - 4, fill=COLOR_X, stroke=STROKE_X, sw=1.3, rx=3))
        f.append(text(cx + (cw - 8) / 2, y3 + 80, f"x{i+8}", size=11, bold=True, color=INK))

        f.append(rect(cx, y3 + 96, cw - 8, ch - 4, fill=COLOR_Y, stroke=STROKE_Y, sw=1.3, rx=3))
        f.append(text(cx + (cw - 8) / 2, y3 + 118, f"y{i+8}", size=11, bold=True, color=INK))

    f.append(text(W / 2, y3 + 175, "AoSoA поєднує пряме завантаження SIMD без перестановок і локальність полів однієї сутності", size=13, color=INK, bold=True))

    render(os.path.join(IMG, "aos-soa-aosoa-memory.svg"), W, H, *f)


# ── Фігура 2: Завантаження даних у векторний регістр: Contiguous Load проти Gather ──
def fig_simd_contiguous_vs_gather():
    W, H = 980, 520
    f = []

    f.append(text(W / 2, 36, "Векторне завантаження у SIMD-регістр YMM (256 біт / 8 × float32)", size=17, bold=True))
    f.append(text(W / 2, 58, "Пряма інструкція vmovups у SoA проти розрізненого читання vgatherdps у AoS", size=13, color=MUTED))

    # --- Лівий бік: SoA / AoSoA (Contiguous Load) ---
    xl = 50
    wl = 420
    f.append(rect(xl, 85, wl, 400, fill="#fafffb", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(xl + wl / 2, 114, "SoA / AoSoA: Неперервне завантаження", size=15, bold=True, color=FIELD))
    f.append(text(xl + wl / 2, 134, "Інструкція vmovups / _mm256_loadu_ps", size=12, color=MUTED))

    # Пам'ять L1D
    f.append(text(xl + 30, 175, "Пам'ять (L1D Cache):", size=13, bold=True, anchor="start"))
    cw = 42
    for i in range(8):
        f.append(rect(xl + 30 + i * cw, 190, cw, 34, fill=COLOR_X, stroke=STROKE_X, sw=1.3, rx=3))
        f.append(text(xl + 30 + i * cw + cw / 2, 212, f"x{i}", size=11, bold=True))

    # Стрілка вниз
    f.append(arrow(xl + wl / 2, 240, xl + wl / 2, 290, color=FIELD, sw=2.5))
    f.append(text(xl + wl / 2 + 15, 270, "1 такт (1 звертання до L1)", size=11, color=FIELD, bold=True, anchor="start"))

    # Регістр YMM
    f.append(text(xl + 30, 315, "Регістр YMM (256 біт):", size=13, bold=True, anchor="start"))
    for i in range(8):
        f.append(rect(xl + 30 + i * cw, 330, cw, 38, fill=COLOR_X, stroke=STROKE_X, sw=1.5, rx=4))
        f.append(text(xl + 30 + i * cw + cw / 2, 354, f"x{i}", size=12, bold=True))

    f.append(text(xl + wl / 2, 410, "Темп: 2 завантаження за такт на порт", size=12, bold=True, color=FIELD))
    f.append(text(xl + wl / 2, 432, "Затримка: 4–5 тактів · Конвеєр заповнений", size=11, color=MUTED))
    f.append(text(xl + wl / 2, 454, "Prefetcher передбачає лінійний доступ", size=11, color=MUTED))

    # --- Правий бік: AoS (Gather або Transpose) ---
    xr = 510
    wr = 420
    f.append(rect(xr, 85, wr, 400, fill="#fdf7f7", stroke=POS, sw=1.5, rx=8))
    f.append(text(xr + wr / 2, 114, "AoS: Збирання розкиданих даних (Gather)", size=15, bold=True, color=POS))
    f.append(text(xr + wr / 2, 134, "Інструкція vgatherdps / _mm256_i32gather_ps", size=12, color=MUTED))

    # Пам'ять AoS
    f.append(text(xr + 20, 175, "Пам'ять (AoS зі кроком 32–64 байти):", size=13, bold=True, anchor="start"))
    step_w = 46
    for i in range(8):
        bx = xr + 20 + i * step_w
        f.append(rect(bx, 190, 20, 34, fill=COLOR_X, stroke=STROKE_X, sw=1.2, rx=2))
        f.append(text(bx + 10, 212, f"x{i}", size=10, bold=True))
        f.append(rect(bx + 22, 190, 22, 34, fill=COLOR_PAD, stroke=STROKE_PAD, sw=1.0, rx=2))
        f.append(text(bx + 33, 212, "...", size=9, color=MUTED))

    # Стрілки збирання
    for i in range(8):
        bx = xr + 20 + i * step_w + 10
        dest_x = xr + 30 + i * cw + cw / 2
        f.append(line(bx, 240, dest_x, 325, color=POS, sw=1.2, dash="3 3"))

    # Пояснення розміщуємо вище ліній
    f.append(text(xr + wr / 2, 234, "8 окремих скалярних запитів до пам'яті", size=11, color=POS, bold=True))

    # Регістр YMM
    f.append(text(xr + 30, 315, "Регістр YMM (256 біт):", size=13, bold=True, anchor="start"))
    for i in range(8):
        f.append(rect(xr + 30 + i * cw, 330, cw, 38, fill=COLOR_X, stroke=STROKE_X, sw=1.5, rx=4))
        f.append(text(xr + 30 + i * cw + cw / 2, 354, f"x{i}", size=12, bold=True))

    f.append(text(xr + wr / 2, 410, "Затримка: 15–35 тактів на інструкцію", size=12, bold=True, color=POS))
    f.append(text(xr + wr / 2, 432, "Блокує порти завантаження та MSHR буфери", size=11, color=MUTED))
    f.append(text(xr + wr / 2, 454, "Часті промахи кешу через великий крок", size=11, color=MUTED))

    render(os.path.join(IMG, "simd-contiguous-vs-gather.svg"), W, H, *f)


# ── Фігура 3: Data-Oriented Design: Таблиці архетипів у ECS та СУБД ───────────
def fig_ecs_columnar_storage():
    W, H = 1000, 540
    f = []

    f.append(text(W / 2, 36, "Data-Oriented Design: Таблиці архетипів в ECS та стовпчикові СУБД", size=17, bold=True))
    f.append(text(W / 2, 58, "Групування сутностей за складом компонентів у щільні масиви SoA-стовпчиків", size=13, color=MUTED))

    # Архетип А: [Position, Velocity] (наприклад, кулі)
    xa = 50
    wa = 420
    f.append(rect(xa, 85, wa, 410, fill="#fcfdfd", stroke=LINE, sw=1.5, rx=8))
    f.append(text(xa + wa / 2, 114, "Архетип A: {Position, Velocity}", size=15, bold=True, color=INK))
    f.append(text(xa + wa / 2, 134, "Чанк пам'яті 16 КБ (щільні стовпчики SoA без пропусків)", size=12, color=MUTED))

    # Стовпчик Entity ID
    f.append(rect(xa + 20, 155, 60, 26, fill=FILL, stroke=LINE, sw=1.2))
    f.append(text(xa + 50, 172, "EntityID", size=11, bold=True))
    # Стовпчик Position (X, Y)
    f.append(rect(xa + 85, 155, 140, 26, fill=COLOR_X, stroke=STROKE_X, sw=1.2))
    f.append(text(xa + 155, 172, "Position (float x, y)", size=11, bold=True))
    # Стовпчик Velocity (VX, VY)
    f.append(rect(xa + 230, 155, 160, 26, fill=COLOR_VX, stroke=STROKE_VX, sw=1.2))
    f.append(text(xa + 310, 172, "Velocity (float vx, vy)", size=11, bold=True))

    rows_a = [
        ("E#101", "(10.5, 20.0)", "(1.0, 0.0)"),
        ("E#102", "(12.0, 24.5)", "(0.5, 1.2)"),
        ("E#103", "(15.2, 18.1)", "(2.0, -0.5)"),
        ("E#104", "(19.8, 30.4)", "(1.5, 0.8)"),
        ("E#...", "(..., ...)", "(..., ...)"),
    ]
    for idx, (eid, pos, vel) in enumerate(rows_a):
        ry = 186 + idx * 30
        f.append(rect(xa + 20, ry, 60, 26, fill=FILL, stroke=MUTED, sw=0.8))
        f.append(text(xa + 50, ry + 17, eid, size=11, color=MUTED))

        f.append(rect(xa + 85, ry, 140, 26, fill=COLOR_X, stroke=STROKE_X, sw=0.8))
        f.append(text(xa + 155, ry + 17, pos, size=11))

        f.append(rect(xa + 230, ry, 160, 26, fill=COLOR_VX, stroke=STROKE_VX, sw=0.8))
        f.append(text(xa + 310, ry + 17, vel, size=11))

    # Системний прохід MovementSystem
    f.append(rect(xa + 20, 360, wa - 40, 110, fill="#f4faf6", stroke=FIELD, sw=1.3, rx=6))
    f.append(text(xa + wa / 2, 385, "Рушій: MovementSystem(dt)", size=13, bold=True, color=FIELD))
    f.append(text(xa + wa / 2, 408, "Ітерує лінійно по масивах Position і Velocity", size=11, color=INK))
    f.append(text(xa + wa / 2, 428, "0 віртуальних викликів · Авто-векторизація SIMD", size=11, color=MUTED))
    f.append(text(xa + wa / 2, 448, "100% потрапляння в кеш L1 · Без промахів гілок", size=11, color=MUTED))

    # Архетип Б: [Position, Velocity, Health, Mesh] (гравці/вороги)
    xb = 510
    wb = 440
    f.append(rect(xb, 85, wb, 410, fill="#fcfdfd", stroke=LINE, sw=1.5, rx=8))
    f.append(text(xb + wb / 2, 114, "Архетип B: {Position, Velocity, Health, Mesh}", size=15, bold=True, color=INK))
    f.append(text(xb + wb / 2, 134, "Інший склад компонентів — окрема таблиця зі своїми чанками", size=12, color=MUTED))

    # Стовпчики
    f.append(rect(xb + 15, 155, 55, 26, fill=FILL, stroke=LINE, sw=1.2))
    f.append(text(xb + 42, 172, "Entity", size=11, bold=True))

    f.append(rect(xb + 75, 155, 95, 26, fill=COLOR_X, stroke=STROKE_X, sw=1.2))
    f.append(text(xb + 122, 172, "Position", size=11, bold=True))

    f.append(rect(xb + 175, 155, 95, 26, fill=COLOR_VX, stroke=STROKE_VX, sw=1.2))
    f.append(text(xb + 222, 172, "Velocity", size=11, bold=True))

    f.append(rect(xb + 275, 155, 75, 26, fill=COLOR_Y, stroke=STROKE_Y, sw=1.2))
    f.append(text(xb + 312, 172, "Health", size=11, bold=True))

    f.append(rect(xb + 355, 155, 70, 26, fill=COLOR_PAD, stroke=STROKE_PAD, sw=1.2))
    f.append(text(xb + 390, 172, "MeshID", size=11, bold=True))

    rows_b = [
        ("E#501", "(0.0, 1.0)", "(0.1, 0.0)", "100 HP", "M#4"),
        ("E#502", "(5.4, 3.2)", "(0.0, 0.0)", "85 HP", "M#12"),
        ("E#503", "(8.1, 9.0)", "(-0.4, 0.2)", "10 HP", "M#4"),
        ("E#...", "(..., ...)", "(..., ...)", "... HP", "M#..."),
    ]
    for idx, (eid, pos, vel, hp, mesh) in enumerate(rows_b):
        ry = 186 + idx * 30
        f.append(rect(xb + 15, ry, 55, 26, fill=FILL, stroke=MUTED, sw=0.8))
        f.append(text(xb + 42, ry + 17, eid, size=11, color=MUTED))

        f.append(rect(xb + 75, ry, 95, 26, fill=COLOR_X, stroke=STROKE_X, sw=0.8))
        f.append(text(xb + 122, ry + 17, pos, size=11))

        f.append(rect(xb + 175, ry, 95, 26, fill=COLOR_VX, stroke=STROKE_VX, sw=0.8))
        f.append(text(xb + 222, ry + 17, vel, size=11))

        f.append(rect(xb + 275, ry, 75, 26, fill=COLOR_Y, stroke=STROKE_Y, sw=0.8))
        f.append(text(xb + 312, ry + 17, hp, size=11))

        f.append(rect(xb + 355, ry, 70, 26, fill=COLOR_PAD, stroke=STROKE_PAD, sw=0.8))
        f.append(text(xb + 390, ry + 17, mesh, size=11))

    # СУБД аналогія
    f.append(rect(xb + 15, 360, wb - 30, 110, fill="#fdfbf5", stroke=STROKE_VX, sw=1.3, rx=6))
    f.append(text(xb + wb / 2, 385, "Аналогія: Стовпчикові СУБД (ClickHouse, Parquet)", size=13, bold=True, color=STROKE_VX))
    f.append(text(xb + wb / 2, 408, "Запит 'SELECT AVG(Health)' читає ЛИШЕ стовпчик Health", size=11, color=INK))
    f.append(text(xb + wb / 2, 428, "Position, Velocity та MeshID взагалі не підтягуються з RAM", size=11, color=MUTED))
    f.append(text(xb + wb / 2, 448, "Економія пам'яті до 80–90% та SIMD фільтрація", size=11, color=MUTED))

    render(os.path.join(IMG, "ecs-columnar-storage.svg"), W, H, *f)


if __name__ == '__main__':
    fig_memory_layouts()
    fig_simd_contiguous_vs_gather()
    fig_ecs_columnar_storage()
    print("All figures generated successfully.")
