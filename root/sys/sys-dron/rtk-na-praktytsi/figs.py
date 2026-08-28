# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «RTK на практиці: база, ровер, канал корекцій, PPK»."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теми: root/sys/sys-dron/rtk-na-praktytsi)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    FONT, BG, INK, LINE, MUTED, POS, NEG, FIELD, FILL,
    text, mtext, rect, line, arrow, circle, textbox, fitbox, render
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_carrier_vs_code_phase():
    """Фігура 1: Порівняння кодового виміру (C/A) та фази несучої (L1)."""
    w, h = 880, 390
    frags = []

    # Верхня панель: Кодовий вимір C/A (Pseudorange)
    frags.append(rect(30, 20, 820, 155, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(250, 44, "Кодовий вимір C/A (модуляція PRN, чип 293 м)", size=14, bold=True, color="#1e40af", anchor="start"))

    # Схематичні чипи коду
    frags.append(rect(60, 65, 380, 45, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=4))
    for i in range(1, 6):
        frags.append(line(60 + i * 63, 65, 60 + i * 63, 110, color="#475569", sw=1.2, dash="3,3"))
        frags.append(text(60 + i * 63 - 31, 92, f"Чип {i}", size=11, color=MUTED))
    frags.append(text(250, 130, "Довжина чипа C/A коду: 293.05 м (τ = 977.5 нс)", size=12, bold=True, color=INK))

    # Характеристики праворуч
    frags.append(rect(480, 58, 350, 98, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=6))
    frags.append(text(500, 80, "• Роздільна здатність DLL: 0.5–2.0 м", size=12, bold=True, color="#1e40af", anchor="start"))
    frags.append(text(500, 104, "• Однозначний вимір часу польоту ToF", size=12, color=INK, anchor="start"))
    frags.append(text(500, 128, "• Стандартна точність автономного GNSS: 1.5–3.0 м", size=12, color=MUTED, anchor="start"))

    # Нижня панель: Фазовий вимір несучої L1 (Carrier Phase)
    frags.append(rect(30, 195, 820, 175, fill="#fdf8f6", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(250, 220, "Фазовий вимір несучої L1 (f = 1575.42 МГц, λ = 19.03 см)", size=14, bold=True, color="#b91c1c", anchor="start"))

    # Хвиля несучої
    wave_path = []
    for cycle_idx in range(6):
        bx = 60 + cycle_idx * 63
        wave_path.append(f"M {bx} 265 Q {bx+15} 245 {bx+31} 265 Q {bx+47} 285 {bx+63} 265")
    frags.append(f'<path d="{" ".join(wave_path)}" fill="none" stroke="#dc2626" stroke-width="2"/>')
    frags.append(line(60, 265, 438, 265, color="#94a3b8", sw=1, dash="2,2"))

    # Позначення довжини хвилі та невизначеності N
    frags.append(line(60, 300, 123, 300, color="#b91c1c", sw=1.5))
    frags.append(line(60, 295, 60, 305, color="#b91c1c", sw=1.5))
    frags.append(line(123, 295, 123, 305, color="#b91c1c", sw=1.5))
    frags.append(text(91, 318, "λ = 19.03 см", size=11, bold=True, color="#b91c1c"))

    frags.append(text(250, 345, "Відстань = N · λ + дробова фаза φ (N — невідоме ціле число хвиль)", size=12, bold=True, color=INK))

    # Характеристики праворуч
    frags.append(rect(480, 235, 350, 115, fill="#fef2f2", stroke="#ef4444", sw=1.2, rx=6))
    frags.append(text(500, 258, "• Точність фазового дискримінатора PLL: 1–2 мм (1% λ)", size=12, bold=True, color="#b91c1c", anchor="start"))
    frags.append(text(500, 282, "• Проблема цілочисельної неоднозначності N", size=12, color=INK, anchor="start"))
    frags.append(text(500, 306, "• Фіксація N (RTK Fix) відкриває точність 1–2 см!", size=12, bold=True, color="#15803d", anchor="start"))
    frags.append(text(500, 330, "• Зрив циклу (Cycle Slip) скидає відоме значення N", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT_DIR, "carrier-vs-code-phase.svg"), w, h, *frags)


def fig_double_differences_geometry():
    """Фігура 2: Геометрія подвійних різниць (Double Differences)."""
    w, h = 880, 420
    frags = []

    # Верхній блок: Супутники
    frags.append(rect(40, 20, 800, 95, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(440, 42, "Супутники на орбіті (висота ~20 200 км)", size=14, bold=True, color=INK))

    # Супутник j
    frags.append(circle(220, 75, 16, fill="#2563eb", stroke=LINE, sw=1.5))
    frags.append(text(220, 80, "Sat j", size=11, bold=True, color="#ffffff"))
    frags.append(text(220, 103, "Супутник j", size=11, color=MUTED))

    # Супутник k (опорний / зенітний)
    frags.append(circle(640, 75, 16, fill="#16a34a", stroke=LINE, sw=1.5))
    frags.append(text(640, 80, "Sat k", size=11, bold=True, color="#ffffff"))
    frags.append(text(640, 103, "Опорний супутник k (найвищий кут місця)", size=11, bold=True, color="#15803d"))

    # Промені від супутників до Бази та Ровера
    # До Бази B (200, 290)
    frags.append(line(220, 91, 200, 270, color="#2563eb", sw=1.5))
    frags.append(text(175, 180, "Φ_B^j", size=11, bold=True, color="#2563eb"))

    frags.append(line(640, 91, 200, 270, color="#16a34a", sw=1.5))
    frags.append(text(380, 170, "Φ_B^k", size=11, bold=True, color="#16a34a"))

    # До Ровера R (660, 290)
    frags.append(line(220, 91, 660, 270, color="#2563eb", sw=1.5))
    frags.append(text(470, 195, "Φ_R^j", size=11, bold=True, color="#2563eb"))

    frags.append(line(640, 91, 660, 270, color="#16a34a", sw=1.5))
    frags.append(text(690, 180, "Φ_R^k", size=11, bold=True, color="#16a34a"))

    # Нижній блок: База і Ровер
    # База B
    frags.append(rect(70, 270, 260, 65, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(circle(200, 285, 7, fill="#3b82f6", stroke=LINE, sw=1.2))
    frags.append(text(200, 305, "Базова станція B (ARP)", size=12, bold=True, color="#1e40af"))
    frags.append(text(200, 322, "Координати r_B відомі з мм-точністю", size=10, color=MUTED))

    # Ровер R
    frags.append(rect(530, 270, 260, 65, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(circle(660, 285, 7, fill="#dc2626", stroke=LINE, sw=1.2))
    frags.append(text(660, 305, "Ровер R (дрон у польоті)", size=12, bold=True, color="#b91c1c"))
    frags.append(text(660, 322, "Шуканий базисний вектор b = r_R − r_B", size=10, color=MUTED))

    # Вектор базисної лінії b між Базою і Ровером
    frags.append(arrow(330, 302, 530, 302, color="#d97706", sw=2.5))
    frags.append(text(430, 292, "Базисна лінія b (< 15–20 км)", size=11, bold=True, color="#b45309"))

    # Підсумок знищення похибок
    frags.append(rect(40, 350, 800, 55, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(440, 370, "1. Одинарна різниця ΔΦ_BR^j: повністю скасовує похибку супутникового годинника δt^j та атмосферу", size=11, bold=True, color="#1e40af"))
    frags.append(text(440, 390, "2. Подвійна різниця ∇ΔΦ_BR^jk: повністю скасовує похибки годинників обох приймачів (δt_R та δt_B)", size=11, bold=True, color="#15803d"))

    render(os.path.join(OUT_DIR, "double-differences-geometry.svg"), w, h, *frags)


def fig_rtk_system_architecture_ntrip_mavlink():
    """Фігура 3: Архітектура передачі поправок RTK (NTRIP, Radio, MAVLink)."""
    w, h = 880, 410
    frags = []

    # Колонка 1: Базова станція
    frags.append(rect(30, 25, 230, 240, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(145, 50, "Базова станція (Base)", size=13, bold=True, color="#1e40af"))
    frags.append(rect(50, 70, 190, 70, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=6))
    frags.append(text(145, 92, "GNSS антена + приймач", size=11, bold=True, color=INK))
    frags.append(text(145, 110, "Survey-In / Фіксована точка", size=10, color=MUTED))
    frags.append(text(145, 126, "Генерація RTCM 3.x", size=10, bold=True, color="#1e40af"))

    frags.append(rect(50, 155, 190, 95, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(145, 175, "Кадри RTCM 3.x:", size=11, bold=True, color=INK))
    frags.append(text(145, 195, "• 1005 / 1006 (Антена ARP)", size=10, color=MUTED))
    frags.append(text(145, 215, "• MSM4 / MSM7 (1074, 1084...)", size=10, color=MUTED))
    frags.append(text(145, 235, "• 1029 (Unicode текст)", size=10, color=MUTED))

    # Канали передачі: LoRa радіо або NTRIP
    # Варіант А: Прямий радіолінк (LoRa 433/868/915 МГц)
    frags.append(arrow(260, 100, 600, 100, color="#d97706", sw=2))
    frags.append(text(430, 90, "Прямий радіомодем (LoRa / 433 / 868 / 915 МГц)", size=11, bold=True, color="#b45309"))
    frags.append(text(430, 115, "Точка-точка (Point-to-Point, 9600–115200 бод)", size=10, color=MUTED))

    # Варіант Б: NTRIP Caster + GCS + MAVLink
    frags.append(arrow(260, 190, 330, 190, color="#2563eb", sw=1.5))
    frags.append(rect(330, 155, 200, 80, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=6))
    frags.append(text(430, 178, "NTRIP Caster (Інтернет / 4G)", size=11, bold=True, color="#15803d"))
    frags.append(text(430, 198, "Mountpoint, аутентифікація", size=10, color=MUTED))
    frags.append(text(430, 218, "GCS (QGC / Mission Planner)", size=10, color=INK))

    frags.append(arrow(530, 190, 600, 190, color="#2563eb", sw=1.5))
    frags.append(text(565, 178, "MAVLink", size=10, bold=True, color="#2563eb"))
    frags.append(text(565, 205, "GPS_RTCM_DATA", size=9, color=MUTED))

    # Колонка 3: Борт дрона (Ровер)
    frags.append(rect(600, 25, 250, 240, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(725, 50, "Борт дрона (Ровер)", size=13, bold=True, color="#b91c1c"))

    frags.append(rect(620, 70, 210, 50, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=6))
    frags.append(text(725, 90, "Польотний контролер (FC)", size=11, bold=True, color=INK))
    frags.append(text(725, 106, "ArduPilot / PX4 розпаковує RTCM", size=10, color=MUTED))

    frags.append(arrow(725, 120, 725, 150, color=LINE, sw=1.5))
    frags.append(text(760, 138, "UART", size=10, color=MUTED))

    frags.append(rect(620, 150, 210, 100, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=6))
    frags.append(text(725, 172, "RTK GNSS (u-blox ZED-F9P)", size=11, bold=True, color="#1e40af"))
    frags.append(text(725, 192, "Фазовий розв'язувач + LAMBDA", size=10, color=INK))
    frags.append(text(725, 212, "Синхронізація міток затвора", size=10, color=MUTED))
    frags.append(text(725, 232, "Вивід: 3D Fix → Float → Fix", size=10, bold=True, color="#15803d"))

    # Нижня панель статусів фіксу
    frags.append(rect(30, 280, 820, 115, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(440, 302, "Статуси позиціонування GNSS приймача на дроні:", size=12, bold=True, color=INK))

    frags.append(rect(50, 315, 235, 65, fill="#f1f5f9", stroke="#64748b", sw=1, rx=4))
    frags.append(text(167, 335, "1. 3D Fix (Автономний)", size=11, bold=True, color="#475569"))
    frags.append(text(167, 353, "Поправки відсутні, код C/A", size=10, color=MUTED))
    frags.append(text(167, 369, "Точність: 1.5 – 3.0 м", size=10, bold=True, color="#b91c1c"))

    frags.append(rect(320, 315, 240, 65, fill="#fffbeb", stroke="#f59e0b", sw=1, rx=4))
    frags.append(text(440, 335, "2. RTK Float (Плавучий)", size=11, bold=True, color="#b45309"))
    frags.append(text(440, 353, "Поправки є, N — дійсні числа", size=10, color=MUTED))
    frags.append(text(440, 369, "Точність: 0.15 – 0.50 м", size=10, bold=True, color="#d97706"))

    frags.append(rect(595, 315, 235, 65, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=4))
    frags.append(text(712, 335, "3. RTK Fix (Фіксований)", size=11, bold=True, color="#15803d"))
    frags.append(text(712, 353, "N зафіксовано в цілих числах", size=10, color=MUTED))
    frags.append(text(712, 369, "Точність: 0.01 – 0.02 м (1–2 см)!", size=10, bold=True, color="#15803d"))

    render(os.path.join(OUT_DIR, "rtk-system-architecture-ntrip-mavlink.svg"), w, h, *frags)


def fig_lambda_decorrelation_search():
    """Фігура 4: Декореляція фазових неоднозначностей алгоритмом LAMBDA."""
    w, h = 880, 370
    frags = []

    # Ліва панель: До декореляції (Float-розв'язок)
    frags.append(rect(30, 20, 390, 330, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(225, 46, "До декореляції: сильна кореляція", size=13, bold=True, color="#b91c1c"))

    # Сітка цілих чисел Z^2
    for gx in range(90, 370, 35):
        for gy in range(80, 240, 35):
            frags.append(circle(gx, gy, 2, fill="#94a3b8", stroke="none"))

    # Довгастий еліпсоїд розсіювання коваріацій
    frags.append('<ellipse cx="230" cy="155" rx="130" ry="18" fill="#fee2e2" stroke="#ef4444" stroke-width="1.8" transform="rotate(-35 230 155)"/>')

    # Оцінка з плаваючою комою (Float)
    frags.append(circle(230, 155, 4, fill="#2563eb", stroke=LINE, sw=1))
    frags.append(text(230, 175, "Float оцінка â", size=11, bold=True, color="#2563eb"))

    frags.append(text(225, 260, "Видовжений еліпсоїд коваріацій Q_â", size=12, bold=True, color="#b91c1c"))
    frags.append(text(225, 282, "Звичайне округлення обирає хибний вузол", size=11, color=INK))
    frags.append(text(225, 302, "Прямий перебір охоплює тисячі точок решітки", size=11, color=MUTED))
    frags.append(text(225, 322, "Кореляція між неоднозначностями > 0.99", size=10, color=MUTED))

    # Стрілка Z-перетворення між панелями
    frags.append(arrow(430, 170, 470, 170, color="#2563eb", sw=2.5))
    frags.append(text(450, 150, "Zᵀ · Q_â · Z", size=11, bold=True, color="#2563eb"))
    frags.append(text(450, 195, "det(Z) = ±1", size=10, color=MUTED))

    # Права панель: Після декореляції LAMBDA
    frags.append(rect(480, 20, 370, 330, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(665, 46, "Після LAMBDA: майже сферичний простір", size=13, bold=True, color="#15803d"))

    # Декорельована сітка Z^2
    for gx in range(530, 810, 35):
        for gy in range(80, 240, 35):
            frags.append(circle(gx, gy, 2, fill="#94a3b8", stroke="none"))

    # Сферичний еліпсоїд коваріацій
    frags.append(circle(670, 155, 48, fill="#dcfce7", stroke="#22c55e", sw=2))

    # Трансформована оцінка ẑ
    frags.append(circle(670, 155, 4, fill="#2563eb", stroke=LINE, sw=1))
    frags.append(text(670, 175, "Трансформована ẑ", size=11, bold=True, color="#2563eb"))

    # Фіксований вузол ž (найближчий цілочисельний кандидат)
    frags.append(circle(670, 150, 5, fill="#16a34a", stroke=LINE, sw=1.5))
    frags.append(text(710, 145, "Фіксований ž", size=11, bold=True, color="#15803d"))

    frags.append(text(665, 260, "Матриця Q_ẑ майже діагональна (сфера)", size=12, bold=True, color="#15803d"))
    frags.append(text(665, 282, "Деревоподібний пошук знаходить мінімум за мкс", size=11, color=INK))
    frags.append(text(665, 302, "Зворотне перетворення: ǎ = Z⁻ᵀ · ž", size=11, bold=True, color="#15803d"))
    frags.append(text(665, 322, "Валідація: Ratio Test Ω(ǎ₂)/Ω(ǎ₁) ≥ 2.5–3.0", size=10, color=MUTED))

    render(os.path.join(OUT_DIR, "lambda-decorrelation-search.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_carrier_vs_code_phase()
    fig_double_differences_geometry()
    fig_rtk_system_architecture_ntrip_mavlink()
    fig_lambda_decorrelation_search()
    print("Всі 4 фігури успішно згенеровано у", OUT_DIR)
