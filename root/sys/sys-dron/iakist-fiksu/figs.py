# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Якість фіксу: DOP, холодний старт, міський каньйон»."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    FONT, BG, INK, LINE, MUTED, POS, NEG, FIELD, FILL,
    text, mtext, rect, line, arrow, circle, textbox, fitbox, render
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_dop_geometry():
    """Фігура 1: Геометричне погіршення точності (DOP) — оптимальне та вироджене сузір'я."""
    w, h = 860, 420
    frags = []

    # Ліва панель: Оптимальна геометрія (Низький DOP)
    frags.append(rect(30, 20, 385, 380, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(222, 48, "Оптимальна геометрія: Низький DOP (≈ 1.5)", size=14, bold=True, color="#15803d"))

    # Небесна півсфера (ліворуч)
    frags.append(circle(222, 160, 90, fill="#ffffff", stroke="#94a3b8", sw=1.2))
    frags.append(line(132, 160, 312, 160, color="#94a3b8", sw=1, dash="2,2"))
    frags.append(line(222, 70, 222, 160, color="#94a3b8", sw=1, dash="2,2"))
    frags.append(text(222, 175, "Дрон (приймач)", size=11, bold=True, color=INK))
    frags.append(circle(222, 160, 4, fill=INK, stroke=LINE, sw=1))

    # Супутники: рознесені
    # Sat 1 (Zenith)
    frags.append(circle(222, 80, 7, fill="#2563eb", stroke=LINE, sw=1))
    frags.append(text(222, 68, "Sat 1 (зеніт)", size=10, bold=True, color="#2563eb"))
    frags.append(line(222, 87, 222, 156, color="#2563eb", sw=1.2))

    # Sat 2 (West low)
    frags.append(circle(150, 140, 7, fill="#2563eb", stroke=LINE, sw=1))
    frags.append(text(130, 132, "Sat 2", size=10, bold=True, color="#2563eb"))
    frags.append(line(156, 142, 218, 158, color="#2563eb", sw=1.2))

    # Sat 3 (East low)
    frags.append(circle(294, 140, 7, fill="#2563eb", stroke=LINE, sw=1))
    frags.append(text(314, 132, "Sat 3", size=10, bold=True, color="#2563eb"))
    frags.append(line(288, 142, 226, 158, color="#2563eb", sw=1.2))

    # Sat 4 (South-East)
    frags.append(circle(255, 120, 7, fill="#2563eb", stroke=LINE, sw=1))
    frags.append(text(278, 112, "Sat 4", size=10, bold=True, color="#2563eb"))
    frags.append(line(251, 124, 224, 157, color="#2563eb", sw=1.2))

    # Еліпс помилки (маленький, круглий)
    frags.append(circle(222, 225, 20, fill="#dcfce7", stroke="#16a34a", sw=1.8))
    frags.append(text(222, 229, "σ_pos", size=11, bold=True, color="#15803d"))
    frags.append(text(222, 258, "Компактна сфера невизначеності", size=11, bold=True, color="#15803d"))

    # Опис властивостей ліворуч
    frags.append(rect(45, 280, 355, 105, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(55, 302, "• Широкий об'єм тетраедра ліній візування", size=11, color=INK, anchor="start"))
    frags.append(text(55, 322, "• Рядки матриці G майже ортогональні", size=11, color=INK, anchor="start"))
    frags.append(text(55, 342, "• det(GᵀG) максимальний, (GᵀG)⁻¹ мінімальна", size=11, color=INK, anchor="start"))
    frags.append(text(55, 364, "• Похибка дальності σ₀ множиться лише на 1.5", size=11, bold=True, color="#15803d", anchor="start"))

    # Права панель: Погана геометрія (Високий DOP)
    frags.append(rect(445, 20, 385, 380, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(637, 48, "Погана геометрія: Високий DOP (> 6.0)", size=14, bold=True, color="#b91c1c"))

    # Небесна півсфера (праворуч)
    frags.append(circle(637, 160, 90, fill="#ffffff", stroke="#94a3b8", sw=1.2))
    frags.append(line(547, 160, 727, 160, color="#94a3b8", sw=1, dash="2,2"))
    frags.append(line(637, 70, 637, 160, color="#94a3b8", sw=1, dash="2,2"))
    frags.append(text(637, 175, "Дрон (приймач)", size=11, bold=True, color=INK))
    frags.append(circle(637, 160, 4, fill=INK, stroke=LINE, sw=1))

    # Супутники: скупчені в одному кутку
    frags.append(circle(675, 85, 7, fill="#ef4444", stroke=LINE, sw=1))
    frags.append(circle(695, 95, 7, fill="#ef4444", stroke=LINE, sw=1))
    frags.append(circle(660, 105, 7, fill="#ef4444", stroke=LINE, sw=1))
    frags.append(circle(685, 115, 7, fill="#ef4444", stroke=LINE, sw=1))
    frags.append(text(730, 85, "Sat 1..4", size=11, bold=True, color="#b91c1c"))

    frags.append(line(675, 92, 639, 156, color="#ef4444", sw=1.2))
    frags.append(line(695, 102, 641, 156, color="#ef4444", sw=1.2))
    frags.append(line(660, 112, 638, 156, color="#ef4444", sw=1.2))
    frags.append(line(685, 122, 640, 156, color="#ef4444", sw=1.2))

    # Еліпс помилки (витягнутий, велетенський)
    frags.append(rect(580, 218, 115, 18, fill="#fee2e2", stroke="#ef4444", sw=1.8, rx=9))
    frags.append(text(637, 231, "σ_pos (витягнута)", size=11, bold=True, color="#b91c1c"))
    frags.append(text(637, 258, "Еліпсоїд помилок роздутий у рази", size=11, bold=True, color="#b91c1c"))

    # Опис властивостей праворуч
    frags.append(rect(460, 280, 355, 105, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(470, 302, "• Супутники згруповані в одному квадранті", size=11, color=INK, anchor="start"))
    frags.append(text(470, 322, "• Вектори візування майже лінійно залежні", size=11, color=INK, anchor="start"))
    frags.append(text(470, 342, "• det(GᵀG) → 0, обернена матриця прямує до ∞", size=11, color=INK, anchor="start"))
    frags.append(text(470, 364, "• Похибка дальності роздувається до десятків метрів", size=11, bold=True, color="#b91c1c", anchor="start"))

    render(os.path.join(OUT_DIR, "dop-geometry-comparison.svg"), w, h, *frags)


def fig_ttff_starts():
    """Фігура 2: Режими стартів GNSS-приймача та тривалість TTFF."""
    w, h = 860, 430
    frags = []

    # Загальний заголовок
    frags.append(text(430, 30, "Анатомія часу до першого визначення координат (TTFF)", size=16, bold=True, color=INK))

    modes = [
        ("Холодний старт (Cold Start): 30–60 с", "#b91c1c", "#fef2f2", [
            ("Пошук сітки: частота Доплера ±10 кГц, фаза PRN", 0, 180, "#fca5a5"),
            ("Захоплення несучої та кадрова синхронізація", 185, 330, "#f87171"),
            ("Вичитування ефемерид (субкадри 1–3: 18–30 с)", 335, 600, "#ef4444"),
            ("Обчислення 3D Fix", 605, 760, "#dc2626"),
        ], "Немає альманаху, ефемерид, часу й координат. Повний перебір супутників."),

        ("Теплий старт (Warm Start): 15–30 с", "#d97706", "#fffbeb", [
            ("Цільовий пошук відомих супутників (альманах у NVRAM)", 0, 240, "#fde68a"),
            ("Завантаження свіжих ефемерид із субкадрів 1–3", 245, 600, "#f59e0b"),
            ("3D Fix", 605, 760, "#d97706"),
        ], "Є альманах і приблизний час RTC. Потрібно завантажити свіжі ефемериди."),

        ("Гарячий старт (Hot Start): 1–3 с", "#15803d", "#f0fdf4", [
            ("Миттєве захоплення частот і кодів", 0, 360, "#86efac"),
            ("3D Fix", 365, 760, "#22c55e"),
        ], "Є все: валідні ефемериди (<2 год), точний RTC-час та координати."),

        ("A-GNSS (Assisted GNSS через IP/LTE/MAVLink): 1–2 с", "#2563eb", "#eff6ff", [
            ("Ін'єкція ефемерид та часу через інтернет/радіоканал", 0, 480, "#93c5fd"),
            ("Миттєвий 3D Fix", 485, 760, "#3b82f6"),
        ], "Ефемериди передаються через стільниковий зв'язок або наземну станцію QGC."),
    ]

    y = 60
    for title, col, bg_col, segments, desc in modes:
        frags.append(rect(40, y, 780, 80, fill=bg_col, stroke=col, sw=1.2, rx=6))
        frags.append(text(55, y + 20, title, size=13, bold=True, color=col, anchor="start"))
        frags.append(text(55, y + 36, desc, size=11, color=MUTED, anchor="start"))

        # Смуга таймлайну
        bar_y = y + 46
        bar_h = 24
        base_x = 55
        for seg_text, x_start, x_end, seg_col in segments:
            sw = x_end - x_start
            frags.append(rect(base_x + x_start, bar_y, sw, bar_h, fill=seg_col, stroke="#ffffff", sw=1, rx=3))
            frags.append(text(base_x + x_start + sw / 2, bar_y + 16, seg_text, size=10, bold=True, color="#ffffff" if col != "#d97706" else INK))

        y += 90

    render(os.path.join(OUT_DIR, "ttff-start-modes.svg"), w, h, *frags)


def fig_multipath_urban():
    """Фігура 3: Багатопроменевість (Multipath) у міському каньйоні та спотворення кореляційного піка."""
    w, h = 860, 430
    frags = []

    # Ліва частина: Геометрія міського каньйону
    frags.append(rect(30, 20, 400, 390, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(230, 48, "Поширення сигналу в міському каньйоні", size=13, bold=True, color=INK))

    # Будівлі
    frags.append(rect(45, 120, 110, 240, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=2))
    frags.append(text(100, 220, "Будинок А", size=12, bold=True, color="#334155"))
    frags.append(text(100, 240, "(Скло/Бетон)", size=10, color="#475569"))

    frags.append(rect(305, 160, 110, 200, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=2))
    frags.append(text(360, 240, "Будинок Б", size=12, bold=True, color="#334155"))
    frags.append(text(360, 260, "(Фасад)", size=10, color="#475569"))

    # Земля / асфальт
    frags.append(rect(45, 360, 370, 30, fill="#94a3b8", stroke="#475569", sw=1.2))
    frags.append(text(230, 380, "Дорожнє покриття (відбиття)", size=10, color="#ffffff"))

    # Дрон
    frags.append(rect(205, 290, 50, 25, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=4))
    frags.append(circle(230, 285, 4, fill="#38bdf8", stroke=LINE, sw=1))
    frags.append(text(230, 328, "Антена дрона", size=10, bold=True, color=INK))

    # Супутник 1: Пряма видимість (LOS)
    frags.append(circle(210, 75, 9, fill="#16a34a", stroke=LINE, sw=1))
    frags.append(text(210, 62, "Супутник (LOS)", size=10, bold=True, color="#15803d"))
    # Прямий промінь
    frags.append(line(212, 85, 228, 281, color="#16a34a", sw=2))
    frags.append(text(202, 175, "Прямий промінь", size=10, bold=True, color="#15803d"))

    # Супутник 2: Відбитий сигнал (NLOS)
    frags.append(circle(70, 65, 9, fill="#ef4444", stroke=LINE, sw=1))
    frags.append(text(70, 52, "Супутник (NLOS)", size=10, bold=True, color="#b91c1c"))
    # Промінь до фасаду
    frags.append(line(76, 72, 305, 195, color="#ef4444", sw=1.5, dash="4,3"))
    # Відбиття до дрона
    frags.append(line(305, 195, 234, 282, color="#ef4444", sw=1.8))
    frags.append(circle(305, 195, 4, fill="#ef4444", stroke=LINE, sw=1))
    frags.append(text(340, 190, "Точка відбиття", size=9, bold=True, color="#b91c1c"))
    frags.append(text(295, 235, "Відбитий (+ΔL)", size=10, bold=True, color="#b91c1c"))

    # Права частина: Спотворення кореляційного піка
    frags.append(rect(445, 20, 385, 390, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(637, 48, "Спотворення кореляційного піка в DLL", size=13, bold=True, color=INK))

    # Графік корелятора
    # Осі
    frags.append(line(480, 240, 800, 240, color=LINE, sw=1.5))  # Вісь часового зсуву tau
    frags.append(line(480, 240, 480, 90, color=LINE, sw=1.5))   # Вісь R(tau)
    frags.append(text(800, 255, "Зсув коду τ", size=11, color=MUTED, anchor="end"))
    frags.append(text(485, 85, "Кореляція R(τ)", size=11, color=MUTED, anchor="start"))

    # Ідеальний кореляційний пік (зелений трикутник)
    frags.append(line(520, 240, 620, 110, color="#16a34a", sw=2))
    frags.append(line(620, 110, 720, 240, color="#16a34a", sw=2))
    frags.append(line(620, 110, 620, 240, color="#16a34a", sw=1, dash="2,2"))
    frags.append(text(620, 255, "τ₀ (істинний)", size=10, bold=True, color="#15803d"))

    # Спотворений пік із multipath (червона лінія)
    frags.append(line(520, 240, 610, 125, color="#ef4444", sw=2, dash="5,2"))
    frags.append(line(610, 125, 655, 118, color="#ef4444", sw=2.5))
    frags.append(line(655, 118, 765, 240, color="#ef4444", sw=2, dash="5,2"))
    frags.append(line(655, 118, 655, 240, color="#ef4444", sw=1, dash="2,2"))
    frags.append(text(665, 255, "τ_err", size=10, bold=True, color="#b91c1c"))

    # Зсув похибки
    frags.append(rect(605, 275, 75, 22, fill="#fee2e2", stroke="#ef4444", sw=1, rx=3))
    frags.append(text(642, 290, "Δτ = τ_err − τ₀", size=10, bold=True, color="#b91c1c"))

    # Пояснення внизу
    frags.append(rect(460, 310, 355, 85, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(470, 330, "• Відбитий сигнал приходить із затримкою ΔL/c", size=11, color=INK, anchor="start"))
    frags.append(text(470, 350, "• Складання копій зміщує вершину трикутника", size=11, color=INK, anchor="start"))
    frags.append(text(470, 372, "• Похибка псевдодальності Δρ = c·Δτ сягає 5–50 м!", size=11, bold=True, color="#b91c1c", anchor="start"))

    render(os.path.join(OUT_DIR, "multipath-urban-canyon.svg"), w, h, *frags)


def fig_signal_and_fix():
    """Фігура 4: Індикатори якості сигналу C/N0 та ієрархія статусів фіксу."""
    w, h = 860, 420
    frags = []

    # Верхня частина: Рівні сигналу C/N0
    frags.append(rect(30, 20, 800, 150, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(430, 42, "Співвідношення сигнал/шум несучої C/N₀ (дБ-Гц)", size=14, bold=True, color=INK))

    cno_bands = [
        ("> 42 дБ-Гц: Відмінний", "Пряма видимість у відкритому небі, високий кут місця", "#15803d", "#dcfce7", 45, 175),
        ("35–42 дБ-Гц: Номінальний", "Стабільне кодове та фазове стеження", "#1e40af", "#dbeafe", 230, 175),
        ("28–35 дБ-Гц: Граничний", "Затінення, дерева, ризик зриву фази", "#d97706", "#fef3c7", 415, 175),
        ("< 28 дБ-Гц: Непридатний", "Глибоке згасання або радіоелектронне глушіння", "#b91c1c", "#fee2e2", 600, 175),
    ]

    for title, desc, col, bg_col, bx, bw in cno_bands:
        frags.append(rect(bx, 60, bw, 95, fill=bg_col, stroke=col, sw=1.2, rx=6))
        frags.append(text(bx + bw / 2, 85, title, size=11, bold=True, color=col))
        frags.append(rect(bx + 10, 100, bw - 20, 45, fill="#ffffff", stroke="#cbd5e1", sw=0.8, rx=4))
        frags.append(fitbox(bx + 12, 103, bw - 24, 38, desc, size=10, color=INK))

    # Нижня частина: Ієрархія статусів розв'язку (Fix Types)
    frags.append(rect(30, 185, 800, 215, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(430, 208, "Ієрархія статусів супутникового фіксу та горизонтальна точність", size=14, bold=True, color=INK))

    fixes = [
        ("No Fix (0/1)", "Немає розв'язку", "∞", "#64748b", "#f1f5f9"),
        ("2D Fix (2)", "3 супутники", "5–15 м", "#d97706", "#fef3c7"),
        ("3D Fix (3)", "≥ 4 супутники", "1.5–3.0 м", "#2563eb", "#dbeafe"),
        ("DGPS / SBAS (4)", "Кодові поправки", "0.6–1.2 м", "#0284c7", "#e0f2fe"),
        ("RTK Float (5)", "Фаза без фіксації", "0.1–0.5 м", "#059669", "#d1fae5"),
        ("RTK Fixed (6)", "Цілочисельна фаза", "0.01–0.02 м", "#15803d", "#dcfce7"),
    ]

    fx = 45
    fw = 118
    gap = 14
    for name, cond, acc, col, bg_col in fixes:
        frags.append(rect(fx, 225, fw, 160, fill=bg_col, stroke=col, sw=1.5, rx=6))
        frags.append(text(fx + fw / 2, 248, name, size=11, bold=True, color=col))
        frags.append(text(fx + fw / 2, 270, cond, size=10, color=MUTED))

        frags.append(rect(fx + 10, 290, fw - 20, 40, fill="#ffffff", stroke=col, sw=1, rx=4))
        frags.append(text(fx + fw / 2, 305, "Точність (1σ):", size=9, color=MUTED))
        frags.append(text(fx + fw / 2, 322, acc, size=11, bold=True, color=col))

        if name != "RTK Fixed (6)":
            frags.append(arrow(fx + fw + 2, 305, fx + fw + gap - 2, 305, color=MUTED, sw=1.2))

        fx += fw + gap

    render(os.path.join(OUT_DIR, "signal-indicators-fix-hierarchy.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_dop_geometry()
    fig_ttff_starts()
    fig_multipath_urban()
    fig_signal_and_fix()
    print("Всі 4 фігури для iakist-fiksu успішно згенеровано.")
