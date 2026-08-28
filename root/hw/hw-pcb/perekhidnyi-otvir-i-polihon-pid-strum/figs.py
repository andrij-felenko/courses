# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# ── 1. Тепловий баланс провідника: джоулів нагрів, конвекція, випромінювання та провідність ─
def fig_trace_heat_dissipation():
    W, H = 840, 440
    f = []

    # Заголовок
    f.append(text(W / 2, 24, "Тепловий баланс силового провідника на друкованій платі", size=16, bold=True))

    # Ліва частина: Поперечний розріз плати
    px, py = 40, 56
    pw, ph = 450, 360
    f.append(rect(px, py, pw, ph, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(px + pw / 2, py + 22, "Розріз 4-шарової плати: шляхи розсіювання тепла", size=13, bold=True, color=INK))

    # Повітря зверху
    f.append(rect(px + 15, py + 38, pw - 30, 50, fill="#f0f7ff", stroke="#d0e2ff", sw=1, rx=4))
    f.append(text(px + 28, py + 56, "Навколишнє повітря (Tamb = 25 °C)", size=11, color=NEG, anchor="start", bold=True))

    # Конвекція та випромінювання (стрілки та підписи поруч)
    f.append(arrow(px + 80, py + 120, px + 80, py + 68, color=POS, sw=2))
    f.append(text(px + 90, py + 82, "q_conv (конвекція)", size=10.5, color=POS, bold=True, anchor="start"))

    f.append(arrow(px + 230, py + 120, px + 230, py + 68, color="#e67e22", sw=2))
    f.append(text(px + 240, py + 82, "q_rad (випромінювання)", size=10.5, color="#e67e22", bold=True, anchor="start"))

    # Паяльна маска верхня (ліва та права ділянки навколо доріжки)
    f.append(rect(px + 15, py + 138, 40, 8, fill="#27ae60", stroke="#1e8449", sw=0.8, rx=1))
    f.append(rect(px + 225, py + 138, pw - 240, 8, fill="#27ae60", stroke="#1e8449", sw=0.8, rx=1))
    f.append(text(px + 330, py + 130, "Паяльна маска (ε ≈ 0.9)", size=10, color="#1e8449", anchor="start"))

    # Зовнішній силовий провідник (Top Layer)
    f.append(rect(px + 55, py + 126, 170, 20, fill="#d35400", stroke="#a04000", sw=1.5, rx=2))
    f.append(text(px + 140, py + 140, "Силова доріжка (I²·R)", size=11.5, color="#ffffff", bold=True))

    # Діелектрик FR-4 шар 1-2
    f.append(rect(px + 15, py + 146, pw - 30, 48, fill="#fdfefe", stroke="#cbd5e1", sw=1, rx=1))
    f.append(text(px + pw - 25, py + 172, "FR-4 (k ≈ 0.25 Вт/(м·К))", size=9.5, color=MUTED, anchor="end"))

    # Внутрішній силовий провідник (Inner Layer 2)
    f.append(rect(px + 55, py + 194, 170, 16, fill="#b9770e", stroke="#7e5109", sw=1.2, rx=2))
    f.append(text(px + 140, py + 206, "Внутрішній шар (затиснений)", size=10.5, color="#ffffff", bold=True))

    # Діелектрик FR-4 шар 2-3 (Core)
    f.append(rect(px + 15, py + 210, pw - 30, 42, fill="#fdfefe", stroke="#cbd5e1", sw=1, rx=1))

    # Внутрішній суцільний шар GND (Inner Layer 3)
    f.append(rect(px + 25, py + 252, pw - 50, 12, fill="#2980b9", stroke="#1f618d", sw=1, rx=1))
    f.append(text(px + 35, py + 261, "Шар GND (тепловий розподільник)", size=10, color="#ffffff", anchor="start", bold=True))

    # Діелектрик FR-4 шар 3-4
    f.append(rect(px + 15, py + 264, pw - 30, 40, fill="#fdfefe", stroke="#cbd5e1", sw=1, rx=1))

    # Нижній шар (Bottom Layer)
    f.append(rect(px + 55, py + 304, 210, 18, fill="#d35400", stroke="#a04000", sw=1.2, rx=2))
    f.append(text(px + 160, py + 317, "Нижній полігон міді", size=11, color="#ffffff", bold=True))
    f.append(rect(px + 15, py + 322, 40, 6, fill="#27ae60", stroke="#1e8449", sw=0.8, rx=1))
    f.append(rect(px + 265, py + 322, pw - 280, 6, fill="#27ae60", stroke="#1e8449", sw=0.8, rx=1))

    # Стрілки теплопровідності
    f.append(arrow(px + 140, py + 148, px + 140, py + 190, color=POS, sw=1.8))
    f.append(arrow(px + 140, py + 212, px + 140, py + 248, color=POS, sw=1.8))
    f.append(arrow(px + 240, py + 266, px + 240, py + 300, color=POS, sw=1.8))
    f.append(text(px + 245, py + 285, "q_cond", size=10, color=POS, bold=True, anchor="start"))

    # Стрілки конвекції знизу
    f.append(arrow(px + 160, py + 326, px + 160, py + 372, color=POS, sw=1.8))
    f.append(text(px + 172, py + 360, "Нижня конвекція", size=10, color=POS, anchor="start"))

    # Права частина: Порівняльна таблиця та ключові залежності
    tx, ty = 510, 56
    tw, th = 290, 360
    f.append(rect(tx, ty, tw, th, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(tx + tw / 2, ty + 24, "Фізичні параметри розсіювання", size=13, bold=True, color=INK))

    rows = [
        ("Джерело тепла:", "P = I² · R(T)  [Дж/с]"),
        ("Опір міді росте:", "R(T) = R₀·(1 + α·ΔT)"),
        ("Темп. коеф. α:", "+0.00393  (1/°C)"),
        ("Конвекція повітря:", "h ≈ 10–15 Вт/(м²·К)"),
        ("Теплопровідність FR-4:", "k ≈ 0.25 Вт/(м·К)"),
        ("Теплопровідність Cu:", "k ≈ 385 Вт/(м·К)"),
    ]
    for i, (k_txt, v_txt) in enumerate(rows):
        yy = ty + 56 + i * 30
        f.append(text(tx + 14, yy, k_txt, size=11, color=MUTED, anchor="start"))
        f.append(text(tx + tw - 14, yy, v_txt, size=11, color=INK, anchor="end", bold=True))

    # Інформаційна плашка внизу правої колонки
    f.append(rect(tx + 12, ty + 245, tw - 24, 96, fill="#eef6ff", stroke=NEG, sw=1.2, rx=4))
    f.append(text(tx + tw / 2, ty + 266, "Зовнішній vs Внутрішній шар:", size=11, color=NEG, bold=True))
    f.append(text(tx + tw / 2, ty + 286, "Зовнішній шар охолоджується повітрям.", size=10, color=INK))
    f.append(text(tx + tw / 2, ty + 306, "Внутрішній затиснений у теплоізоляторі FR-4.", size=10, color=INK))
    f.append(text(tx + tw / 2, ty + 326, "Без площин поруч: струм ×0.5 (IPC-2152)!", size=10, color=POS, bold=True))

    return render(os.path.join(IMG, "trace-heat-dissipation.svg"), W, H, *f)


# ── 2. Геометрія перехідного отвору (Via) та матриця stitching vias ───────────
def fig_via_geometry_and_array():
    W, H = 840, 420
    f = []

    f.append(text(W / 2, 24, "Будова перехідного отвору та силова матриця (Stitching Vias)", size=16, bold=True))

    # Ліва колонка: Геометрія циліндричної гільзи перехідного отвору
    vx, vy = 40, 56
    vw, vh = 360, 345
    f.append(rect(vx, vy, vw, vh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(vx + vw / 2, vy + 24, "Геометрія циліндричної гільзи via", size=13, bold=True, color=INK))

    # Верхня площадка (Annular ring)
    f.append(rect(vx + 45, vy + 55, 270, 16, fill="#d35400", stroke="#a04000", sw=1.5, rx=3))
    f.append(text(vx + 35, vy + 67, "Top Pad", size=10.5, color=MUTED, anchor="end"))

    # Тіло плати (FR-4): малюємо лівий і правий блоки діелектрика, щоб не накладатись на гільзу
    f.append(rect(vx + 45, vy + 71, 75, 140, fill="#fdfefe", stroke="#cbd5e1", sw=1, rx=0))
    f.append(rect(vx + 230, vy + 71, 85, 140, fill="#fdfefe", stroke="#cbd5e1", sw=1, rx=0))
    f.append(text(vx + 272, vy + 145, "FR-4 h=1.6 мм", size=10, color=MUTED))

    # Мідна металізація гільзи (ліва та права стінки циліндра)
    f.append(rect(vx + 120, vy + 55, 22, 172, fill="#e67e22", stroke="#b9770e", sw=1.2, rx=0))
    f.append(rect(vx + 208, vy + 55, 22, 172, fill="#e67e22", stroke="#b9770e", sw=1.2, rx=0))

    # Порожнистий отвір усередині
    f.append(rect(vx + 142, vy + 55, 66, 172, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=0))
    f.append(text(vx + 175, vy + 145, "Порожнина", size=10, color=MUTED))

    # Нижня площадка
    f.append(rect(vx + 45, vy + 211, 270, 16, fill="#d35400", stroke="#a04000", sw=1.5, rx=3))
    f.append(text(vx + 35, vy + 223, "Bottom Pad", size=10.5, color=MUTED, anchor="end"))

    # Розмірні стрілки та виноски
    # Діаметр отвору
    f.append(line(vx + 120, vy + 45, vx + 230, vy + 45, color=INK, sw=1.2))
    f.append(text(vx + 175, vy + 38, "d_drill = 0.3–0.5 мм", size=10.5, color=INK, bold=True))

    # Товщина стінки металізації
    f.append(arrow(vx + 75, vy + 105, vx + 118, vy + 105, color=POS, sw=1.5))
    f.append(text(vx + 70, vy + 100, "t_wall ≈ 20–25 мкм", size=9.5, color=POS, bold=True, anchor="end"))

    # Параметри опору та формули
    f.append(rect(vx + 14, vy + 245, vw - 28, 86, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    f.append(text(vx + vw / 2, vy + 265, "Площа перерізу стінки: A ≈ π · d_hole · t_wall", size=11, color=INK, bold=True))
    f.append(text(vx + vw / 2, vy + 287, "Опір 1 via (d=0.3 мм, h=1.6 мм): R ≈ 1.2–1.5 мОм", size=10.5, color=POS, bold=True))
    f.append(text(vx + vw / 2, vy + 309, "Допустимий струм (ΔT=20°C): I_max ≈ 1.5–2.0 А", size=10.5, color=NEG, bold=True))

    # Права колонка: Силова матриця перехідних отворів (Stitching Vias Array)
    ax, ay = 420, 56
    aw, ah = 380, 345
    f.append(rect(ax, ay, aw, ah, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(ax + aw / 2, ay + 24, "Матриця перехідних отворів під струм 15–20 А", size=13, bold=True, color=INK))

    # Верхній полігон Top Layer
    f.append(rect(ax + 25, ay + 48, aw - 50, 92, fill="#fdebd0", stroke="#e67e22", sw=1.4, rx=4))
    f.append(text(ax + 35, ay + 66, "Шина живлення (Top Copper Pour)", size=10.5, color="#b9770e", anchor="start", bold=True))

    # Сітка перехідних отворів 4x2
    for r in range(2):
        for c in range(4):
            cx = ax + 95 + c * 60
            cy = ay + 92 + r * 32
            # Зовнішнє кільце
            f.append(circle(cx, cy, 11, fill="#d35400", stroke="#a04000", sw=1.2))
            # Осаджена мідь
            f.append(circle(cx, cy, 7, fill="#fdfefe", stroke="#b9770e", sw=1))
            # Центр отвору
            f.append(circle(cx, cy, 3.5, fill="#1a1a1a", stroke="#1a1a1a", sw=0.5))

    # Стрілка струму до матриці
    f.append(arrow(ax + 35, ay + 105, ax + 72, ay + 105, color=POS, sw=2.5))
    f.append(text(ax + 35, ay + 126, "I = 16 A", size=11.5, color=POS, bold=True, anchor="start"))

    # Розподіл струму по отворах
    f.append(text(ax + aw / 2, ay + 162, "Струм ділиться порівну: I_via = I_total / N = 16 А / 8 = 2 А", size=11, color=INK, bold=True))

    # Крок сітки (pitch)
    f.append(line(ax + 95, ay + 138, ax + 155, ay + 138, color=MUTED, sw=1.2))
    f.append(text(ax + 125, ay + 150, "pitch p ≥ 2–3·d", size=9.5, color=MUTED))

    # Переваги та правила розрахунку матриці
    f.append(rect(ax + 16, ay + 180, aw - 32, 148, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    f.append(text(ax + 28, ay + 202, "Правила силової матриці (Array Rules):", size=11, color=INK, bold=True, anchor="start"))
    f.append(text(ax + 28, ay + 224, "1. Паралельний опір: R_eq = R_via / N (8 via → 0.18 мОм)", size=10.5, color=INK, anchor="start"))
    f.append(text(ax + 28, ay + 246, "2. Паразитна індуктивність падає в N разів (L_eq = L / N)", size=10.5, color=INK, anchor="start"))
    f.append(text(ax + 28, ay + 268, "3. Теплове взаємопроникнення: крок ≥ 1.0–1.5 мм", size=10.5, color=POS, anchor="start", bold=True))
    f.append(text(ax + 28, ay + 290, "4. Розміщувати впритул до виводів конденсаторів/ключів", size=10, color=MUTED, anchor="start"))
    f.append(text(ax + 28, ay + 312, "5. Струмовий запас: розраховувати на N - 1 отвір", size=10, color=POS, anchor="start"))

    return render(os.path.join(IMG, "via-geometry-and-array.svg"), W, H, *f)


# ── 3. Термобар'єр (Thermal Relief) проти суцільного підключення (Direct Connect)
def fig_thermal_relief_vs_direct():
    W, H = 840, 430
    f = []

    f.append(text(W / 2, 24, "Термобар'єр (Thermal Relief) проти суцільного підключення (Direct Connect)", size=15.5, bold=True))

    # Ліва колонка: Термобар'єр (Thermal Relief)
    lx, ly = 40, 56
    lw, lh = 360, 355
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(lx + lw / 2, ly + 24, "Термобар'єр (Thermal Relief)", size=13.5, bold=True, color=INK))

    # Мідний полігон навколо
    f.append(rect(lx + 25, ly + 46, lw - 50, 150, fill="#fdebd0", stroke="#e67e22", sw=1.4, rx=4))

    # Ізоляційний зазор навколо площадки (Thermal Relief cutout)
    f.append(circle(lx + lw / 2, ly + 121, 54, fill="#ffffff", stroke="#cbd5e1", sw=1.2))

    # 4 спиці (Spokes)
    # Горизонтальна спиця
    f.append(rect(lx + lw / 2 - 54, ly + 121 - 7, 108, 14, fill="#fdebd0", stroke="#e67e22", sw=1, rx=0))
    # Вертикальна спиця
    f.append(rect(lx + lw / 2 - 7, ly + 121 - 54, 14, 108, fill="#fdebd0", stroke="#e67e22", sw=1, rx=0))

    # Центральна контактна площадка (Pad)
    f.append(circle(lx + lw / 2, ly + 121, 28, fill="#d35400", stroke="#a04000", sw=1.5))
    f.append(circle(lx + lw / 2, ly + 121, 12, fill="#1a1a1a", stroke="#1a1a1a", sw=0.5))

    # Позначення спиць
    f.append(text(lx + lw / 2, ly + 54, "4 тонкі спиці (0.3–0.5 мм)", size=10.5, color=POS, bold=True))

    # Стрілки струму (вузькі місця)
    f.append(arrow(lx + 40, ly + 121, lx + 105, ly + 121, color=POS, sw=2))
    f.append(arrow(lx + lw - 40, ly + 121, lx + lw - 105, ly + 121, color=POS, sw=2))

    # Опис властивостей ліворуч
    f.append(rect(lx + 14, ly + 210, lw - 28, 130, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    f.append(text(lx + 24, ly + 232, "Плюси:", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(lx + 68, ly + 232, "Легка пайка ручним паяльником та в печі", size=10.5, color=INK, anchor="start"))
    f.append(text(lx + 24, ly + 252, "Захист:", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(lx + 68, ly + 252, "Усуває дефект «надгробка» (tombstoning)", size=10.5, color=INK, anchor="start"))
    f.append(text(lx + 24, ly + 276, "Мінуси під великим струмом:", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(lx + 24, ly + 296, "• Вузьке горло: 4 спиці × 0.3 мм = 1.2 мм перерізу", size=10.5, color=POS, anchor="start"))
    f.append(text(lx + 24, ly + 318, "• Локальний перегрів спиць при струмі > 5–8 А!", size=10.5, color=POS, bold=True, anchor="start"))

    # Права колонка: Суцільне підключення (Direct Connect)
    rx, ry = 420, 56
    rw, rh = 380, 355
    f.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(rx + rw / 2, ry + 24, "Суцільне підключення (Direct Connect)", size=13.5, bold=True, color=INK))

    # Суцільний мідний полігон
    f.append(rect(rx + 25, ry + 46, rw - 50, 150, fill="#fdebd0", stroke="#e67e22", sw=1.4, rx=4))

    # Суцільна контактна площадка, злита з полігоном
    f.append(circle(rx + rw / 2, ry + 121, 38, fill="#d35400", stroke="#a04000", sw=2))
    f.append(circle(rx + rw / 2, ry + 121, 12, fill="#1a1a1a", stroke="#1a1a1a", sw=0.5))
    f.append(text(rx + rw / 2, ry + 72, "Повний контакт 360°", size=11, color="#a04000", bold=True))

    # Широкі стрілки струму з усіх боків
    f.append(arrow(rx + 50, ry + 121, rx + 120, ry + 121, color=NEG, sw=3))
    f.append(arrow(rx + rw - 50, ry + 121, rx + rw - 120, ry + 121, color=NEG, sw=3))
    f.append(arrow(rx + rw / 2, ry + 50, rx + rw / 2, ry + 78, color=NEG, sw=3))
    f.append(arrow(rx + rw / 2, ry + 190, rx + rw / 2, ry + 162, color=NEG, sw=3))

    # Опис властивостей праворуч
    f.append(rect(rx + 14, ry + 210, rw - 28, 130, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    f.append(text(rx + 24, ly + 232, "Плюси для сили:", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(rx + 24, ly + 252, "• Нульовий додатковий опір шини (R ≈ 0)", size=10.5, color=INK, anchor="start"))
    f.append(text(rx + 24, ly + 272, "• Максимальний струм 20–50+ А без перегріву", size=10.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(rx + 24, ly + 296, "Вимоги до монтажу:", size=11, color=NEG, bold=True, anchor="start"))
    f.append(text(rx + 24, ly + 318, "• Потрібен нижній підігрів (Preheater) або потужне жало", size=10, color=INK, anchor="start"))

    return render(os.path.join(IMG, "thermal-relief-vs-direct.svg"), W, H, *f)


if __name__ == "__main__":
    fig_trace_heat_dissipation()
    fig_via_geometry_and_array()
    fig_thermal_relief_vs_direct()
    print("All figures generated successfully.")
