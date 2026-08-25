# -*- coding: utf-8 -*-
"""Фігури до теми «Чиплети та advanced packaging» (chiplets) та її вставок.
Запуск: python figs.py  → генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Палітра для чиплетних компонентів
C_COMPUTE = "#eaf0fd"   # синій для обчислювальних ядер
C_COMPUTE_K = "#2457d6"
C_IOD     = "#fdf3e7"   # помаранчевий для I/O кристала
C_IOD_K   = "#d97706"
C_HBM     = "#e8f7ec"   # зелений для пам'яті HBM
C_HBM_K   = "#1e7e34"
C_SUBST   = "#ede9fe"   # фіолетовий для підкладки / інтерпозера
C_SUBST_K = "#6d28d9"
C_DEFECT  = "#fce8e6"   # червонуватий для дефектів / браку
C_DEFECT_K= "#c0392b"
C_WARN    = "#c0392b"
C_OK      = "#1e7e34"


# ── Фігура 1: Монолітний кристал проти модульної системи на чиплетах ────────
def fig_monolith_vs_chiplet():
    W, H = 840, 490
    f = [text(W / 2, 28, "Монолітний кристал проти модульної чиплетної архітектури",
              size=15, bold=True)]

    # Ліва панель: Монолітний кристал
    f.append(rect(25, 50, 380, 415, fill="#ffffff", stroke=LINE, sw=1.6, rx=8))
    f.append(text(215, 76, "Монолітний кристал (Monolithic Die)", size=13, bold=True))
    f.append(text(215, 95, "Єдиний великий кристал на дорогому вузлі 3 нм", size=11, color=MUTED))

    # Контур моноліту
    f.append(rect(45, 115, 340, 240, fill="#f8fafc", stroke=LINE, sw=1.8, rx=6))
    f.append(text(215, 136, "Площа кристала ~800 мм² (межа фотошаблона)", size=11, bold=True))

    # Внутрішні блоки моноліту
    f.append(rect(60, 150, 145, 80, fill=C_COMPUTE, stroke=C_COMPUTE_K, sw=1.2, rx=4))
    f.append(text(132, 185, "CPU / GPU Ядра", size=11, bold=True, color=C_COMPUTE_K))
    f.append(text(132, 204, "(логіка 3 нм)", size=10, color=C_COMPUTE_K))

    f.append(rect(225, 150, 145, 80, fill=C_COMPUTE, stroke=C_COMPUTE_K, sw=1.2, rx=4))
    f.append(text(297, 185, "NPU / Тензори", size=11, bold=True, color=C_COMPUTE_K))
    f.append(text(297, 204, "(логіка 3 нм)", size=10, color=C_COMPUTE_K))

    f.append(rect(60, 240, 310, 100, fill=C_IOD, stroke=C_IOD_K, sw=1.2, rx=4))
    f.append(text(215, 268, "I/O контролери, SerDes PHY, контролери пам'яті", size=10.5, bold=True, color=C_IOD_K))
    f.append(text(215, 288, "Аналогові блоки не масштабуються, займають площу 3 нм", size=9.5, color=MUTED))
    f.append(text(215, 308, "Площа I/O ~40% кристала за ціною передового вузла", size=9.5, color=C_WARN, bold=True))

    # Точки дефектів
    f.append(circle(115, 175, 7, fill=C_DEFECT, stroke=C_DEFECT_K, sw=1.5))
    f.append(text(115, 179, "×", size=14, color=C_DEFECT_K, bold=True))
    f.append(circle(275, 275, 7, fill=C_DEFECT, stroke=C_DEFECT_K, sw=1.5))
    f.append(text(275, 279, "×", size=14, color=C_DEFECT_K, bold=True))

    # Підсумок моноліту
    f.append(rect(45, 370, 340, 80, fill="#fff1f0", stroke=C_WARN, sw=1.2, rx=6))
    f.append(text(215, 390, "Критичні недоліки моноліту:", size=11, bold=True, color=C_WARN))
    f.append(text(215, 410, "• 1 точковий дефект вбиває весь кристал 800 мм²", size=10, color=INK))
    f.append(text(215, 428, "• Вихід придатних (Yield) низький: 30–45%", size=10, color=INK))
    f.append(text(215, 444, "• Неможливо перевищити ліміт ретикули (858 мм²)", size=9.5, color=MUTED))

    # Права панель: Чиплетна система
    f.append(rect(435, 50, 380, 415, fill="#ffffff", stroke=LINE, sw=1.6, rx=8))
    f.append(text(625, 76, "Модульна чиплетна збірка (Chiplets)", size=13, bold=True))
    f.append(text(625, 95, "Гетерогенна інтеграція на спільній підкладці", size=11, color=MUTED))

    # Органічний субстрат / Інтерпозер
    f.append(rect(455, 115, 340, 240, fill=C_SUBST, stroke=C_SUBST_K, sw=1.8, rx=6))
    f.append(text(625, 134, "Кремнієвий інтерпозер / Пакувальний субстрат", size=11, bold=True, color=C_SUBST_K))

    # Окремі чиплети
    # Compute 1 & 2
    f.append(rect(470, 150, 95, 75, fill=C_COMPUTE, stroke=C_COMPUTE_K, sw=1.4, rx=4))
    f.append(text(517, 178, "Compute 1", size=10.5, bold=True, color=C_COMPUTE_K))
    f.append(text(517, 195, "3 нм (75 мм²)", size=9.5, color=INK))
    f.append(text(517, 212, "Yield > 88%", size=9.5, color=C_OK, bold=True))

    f.append(rect(575, 150, 95, 75, fill=C_COMPUTE, stroke=C_COMPUTE_K, sw=1.4, rx=4))
    f.append(text(622, 178, "Compute 2", size=10.5, bold=True, color=C_COMPUTE_K))
    f.append(text(622, 195, "3 нм (75 мм²)", size=9.5, color=INK))
    f.append(text(622, 212, "Yield > 88%", size=9.5, color=C_OK, bold=True))

    # HBM Stack
    f.append(rect(680, 150, 100, 75, fill=C_HBM, stroke=C_HBM_K, sw=1.4, rx=4))
    f.append(text(730, 178, "HBM3 Стек", size=10.5, bold=True, color=C_HBM_K))
    f.append(text(730, 195, "3D Пам'ять", size=9.5, color=INK))
    f.append(text(730, 212, "819 ГБ/с", size=9.5, color=C_HBM_K, bold=True))

    # Central I/O Die
    f.append(rect(470, 240, 310, 100, fill=C_IOD, stroke=C_IOD_K, sw=1.4, rx=4))
    f.append(text(625, 264, "Центральний I/O кристал (cIOD)", size=11.5, bold=True, color=C_IOD_K))
    f.append(text(625, 282, "Виготовлений на дешевому зрілому вузлі 12 нм або 28 нм", size=10, color=INK))
    f.append(text(625, 300, "PCIe 5.0/6.0, контролери DDR5/CXL, аналоговий SerDes PHY", size=9.5, color=MUTED))
    f.append(text(625, 318, "Собівартість кремнію у 4–6 разів нижча, ніж на 3 нм", size=9.5, color=C_OK, bold=True))

    # Зв'язки між чиплетами (D2D Interconnect)
    f.append(line(517, 225, 517, 240, color=C_SUBST_K, sw=2.5, dash="3,2"))
    f.append(line(622, 225, 622, 240, color=C_SUBST_K, sw=2.5, dash="3,2"))
    f.append(line(730, 225, 730, 240, color=C_SUBST_K, sw=2.5, dash="3,2"))

    # Підсумок чиплетів
    f.append(rect(455, 370, 340, 80, fill="#f6ffed", stroke=C_OK, sw=1.2, rx=6))
    f.append(text(625, 390, "Переваги модульної архітектури:", size=11, bold=True, color=C_OK))
    f.append(text(625, 410, "• Тестування до збірки (KGD): дефектні чиплети відсіюються", size=10, color=INK))
    f.append(text(625, 428, "• Сумарна площа системи може сягати 2000–4000+ мм²", size=10, color=INK))
    f.append(text(625, 444, "• Оптимальний техпроцес для кожного функціонального блоку", size=9.5, color=MUTED))

    render(os.path.join(IMG, "monolith-vs-chiplet.svg"), W, H, *f)


# ── Фігура 2: Технології корпусування: 2D, 2.5D, 3D ──────────────────────────
def fig_packaging_technologies_25d_3d():
    W, H = 870, 520
    f = [text(W / 2, 26, "Еволюція технологій монтажу: 2D (органіка), 2.5D (інтерпозер) та 3D (SoIC)",
              size=15, bold=True)]

    # 1. Секція 2D: Традиційний субстрат
    f.append(rect(20, 50, 260, 445, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(150, 74, "2D: Органічний субстрат", size=12.5, bold=True))
    f.append(text(150, 92, "Standard Multi-Chip Module", size=10.5, color=MUTED))

    # Чиплети
    f.append(rect(40, 115, 100, 50, fill=C_COMPUTE, stroke=C_COMPUTE_K, sw=1.2, rx=3))
    f.append(text(90, 144, "Чиплет A", size=10.5, bold=True, color=C_COMPUTE_K))
    f.append(rect(160, 115, 100, 50, fill=C_IOD, stroke=C_IOD_K, sw=1.2, rx=3))
    f.append(text(210, 144, "Чиплет B", size=10.5, bold=True, color=C_IOD_K))

    # C4 Bumps
    for bx in [55, 75, 95, 115, 135, 165, 185, 205, 225, 245]:
        f.append(circle(bx, 175, 5, fill="#94a3b8", stroke="#475569", sw=1.0))
    f.append(text(150, 198, "C4 бампи (крок 100–150 мкм)", size=9.5, color=MUTED))

    # Organic substrate
    f.append(rect(30, 210, 240, 55, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=4))
    f.append(text(150, 233, "Органічна друкована підкладка", size=10.5, bold=True))
    f.append(text(150, 251, "Мідні траси (ширина ліній 10–20 мкм)", size=9.5, color=MUTED))

    # BGA balls
    for bx in [60, 105, 150, 195, 240]:
        f.append(circle(bx, 280, 9, fill="#cbd5e1", stroke="#475569", sw=1.2))
    f.append(text(150, 308, "BGA виводи до плати", size=9.5, color=MUTED))

    # Характеристики 2D
    f.append(rect(30, 325, 240, 155, fill="#f8fafc", stroke=LINE, sw=1.0, rx=4))
    f.append(text(150, 347, "Параметри з'єднання 2D:", size=11, bold=True))
    f.append(text(40, 372, "• Щільність: <20 ліній / мм краю", size=9.5, anchor="start"))
    f.append(text(40, 394, "• Крок виводів: 100–150 мкм", size=9.5, anchor="start"))
    f.append(text(40, 416, "• Паразитна ємність: 1–5 пФ", size=9.5, anchor="start"))
    f.append(text(40, 438, "• Енергія: 5–10 пДж / біт", size=10, color=C_WARN, bold=True, anchor="start"))
    f.append(text(40, 460, "• Затримка зв'язку: 5–15 нс", size=9.5, anchor="start"))

    # 2. Секція 2.5D: Кремнієвий інтерпозер (CoWoS / EMIB)
    f.append(rect(305, 50, 260, 445, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(435, 74, "2.5D: Кремнієвий інтерпозер", size=12.5, bold=True))
    f.append(text(435, 92, "TSMC CoWoS / Intel EMIB", size=10.5, color=MUTED))

    # Чиплети
    f.append(rect(320, 115, 105, 45, fill=C_COMPUTE, stroke=C_COMPUTE_K, sw=1.2, rx=3))
    f.append(text(372, 142, "Логічний чип", size=10.5, bold=True, color=C_COMPUTE_K))
    f.append(rect(445, 115, 105, 45, fill=C_HBM, stroke=C_HBM_K, sw=1.2, rx=3))
    f.append(text(497, 142, "HBM Пам'ять", size=10.5, bold=True, color=C_HBM_K))

    # Microbumps
    for bx in range(326, 545, 16):
        f.append(circle(bx, 168, 2.5, fill="#94a3b8", stroke="#334155", sw=0.8))
    f.append(text(435, 185, "Мікростовпчики (μbumps, крок 25–45 мкм)", size=9.5, color=MUTED))

    # Silicon Interposer + TSVs
    f.append(rect(315, 195, 240, 52, fill=C_SUBST, stroke=C_SUBST_K, sw=1.5, rx=3))
    f.append(text(435, 212, "Кремнієвий інтерпозер (Interposer)", size=10, bold=True, color=C_SUBST_K))
    f.append(text(435, 227, "Тонкі металеві шари BEOL (0.4–1 мкм)", size=9, color=INK))
    # TSV vertical lines
    for tx in [345, 385, 485, 525]:
        f.append(line(tx, 230, tx, 247, color=C_SUBST_K, sw=2.5))
    f.append(text(435, 243, "TSV", size=9, color=C_SUBST_K, bold=True))

    # C4 Bumps to package substrate
    for bx in [345, 390, 435, 480, 525]:
        f.append(circle(bx, 258, 5, fill="#94a3b8", stroke="#475569", sw=1.0))
    f.append(rect(315, 268, 240, 35, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=3))
    f.append(text(435, 289, "Органічний пакувальний субстрат", size=9.5, color=MUTED))

    # Характеристики 2.5D
    f.append(rect(315, 325, 240, 155, fill="#f8fafc", stroke=LINE, sw=1.0, rx=4))
    f.append(text(435, 347, "Параметри з'єднання 2.5D:", size=11, bold=True))
    f.append(text(325, 372, "• Щільність: 200–800 ліній / мм краю", size=9.5, anchor="start"))
    f.append(text(325, 394, "• Крок виводів: 25–45 мкм", size=9.5, anchor="start"))
    f.append(text(325, 416, "• Паразитна ємність: 50–200 фФ", size=9.5, anchor="start"))
    f.append(text(325, 438, "• Енергія: 0.5–1.0 пДж / біт", size=10, color=C_OK, bold=True, anchor="start"))
    f.append(text(325, 460, "• Затримка зв'язку: <2 нс", size=9.5, anchor="start"))

    # 3. Секція 3D: Пряме гібридне зрощування (TSMC SoIC / Direct Cu-Cu)
    f.append(rect(590, 50, 260, 445, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(720, 74, "3D: Гібридне зрощування Cu-Cu", size=12.5, bold=True))
    f.append(text(720, 92, "TSMC SoIC / Foveros Direct", size=10.5, color=MUTED))

    # Верхній кристал (Top Die)
    f.append(rect(610, 115, 220, 45, fill=C_COMPUTE, stroke=C_COMPUTE_K, sw=1.4, rx=3))
    f.append(text(720, 138, "Верхній чип (напр. 3D V-Cache)", size=10.5, bold=True, color=C_COMPUTE_K))
    f.append(text(720, 153, "Кристал стоншений до ~20 мкм", size=9, color=MUTED))

    # Поверхня Direct Cu-Cu Bonding (без припою!)
    f.append(rect(610, 160, 220, 16, fill="#fef08a", stroke="#ca8a04", sw=1.2, rx=1))
    f.append(text(720, 172, "Прямий шов Cu-Cu + SiO2 (крок 0.5–9 мкм)", size=9, bold=True, color="#854d0e"))

    # Нижній базовий кристал (Base Die / Active Substrate)
    f.append(rect(610, 176, 220, 65, fill=C_IOD, stroke=C_IOD_K, sw=1.4, rx=3))
    f.append(text(720, 198, "Базовий кристал (Base Compute Die)", size=10.5, bold=True, color=C_IOD_K))
    f.append(text(720, 213, "Крізні кремнієві отвори TSV", size=9, color=MUTED))
    # TSVs through base die
    for tx in [645, 685, 735, 775]:
        f.append(line(tx, 218, tx, 241, color=C_IOD_K, sw=2.5))
    f.append(text(720, 235, "TSV", size=9, color=C_IOD_K, bold=True))

    # Microbumps to package
    for bx in [635, 675, 720, 765, 805]:
        f.append(circle(bx, 252, 4, fill="#94a3b8", stroke="#475569", sw=0.8))
    f.append(rect(605, 262, 230, 35, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=3))
    f.append(text(720, 283, "Органічний субстрат корпусу", size=9.5, color=MUTED))

    # Характеристики 3D
    f.append(rect(600, 325, 240, 155, fill="#f8fafc", stroke=LINE, sw=1.0, rx=4))
    f.append(text(720, 347, "Параметри з'єднання 3D SoIC:", size=11, bold=True))
    f.append(text(610, 372, "• Щільність: >10 000–1 000 000 / мм²", size=9.5, anchor="start"))
    f.append(text(610, 394, "• Крок виводів: 0.5–9 мкм", size=9.5, anchor="start"))
    f.append(text(610, 416, "• Паразитна ємність: <1 фФ (0.001 пФ)", size=9.5, anchor="start"))
    f.append(text(610, 438, "• Енергія: <0.05 пДж / біт", size=10, color=C_OK, bold=True, anchor="start"))
    f.append(text(610, 460, "• Затримка: <0.1 нс (внутрішньокристальна)", size=9.5, anchor="start"))

    render(os.path.join(IMG, "packaging-technologies-25d-3d.svg"), W, H, *f)


# ── Фігура 3: Техпроцесний розрив масштабування компонентів ──────────────────
def fig_heterogeneous_die_scaling():
    W, H = 820, 440
    f = [text(W / 2, 26, "Техпроцесний розрив: чому аналогові та I/O блоки не масштабуються",
              size=15, bold=True)]

    # Лівий блок: Масштабування площі різних функціональних блоків
    f.append(rect(25, 50, 370, 365, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(210, 75, "Відносна площа при переході 16 нм → 3 нм", size=12, bold=True))

    # Стовпчик 1: Цифрова логіка
    f.append(text(45, 115, "Цифрова логіка (ALU/FPU/Tensor)", size=10.5, bold=True, anchor="start"))
    f.append(rect(45, 125, 220, 22, fill="#e2e8f0", stroke="#94a3b8", sw=1.0, rx=3))
    f.append(text(155, 140, "16 нм: 100% (база)", size=9.5, color=MUTED))
    f.append(rect(45, 150, 35, 22, fill=C_COMPUTE, stroke=C_COMPUTE_K, sw=1.2, rx=3))
    f.append(text(62, 165, "15%", size=9.5, bold=True, color=C_COMPUTE_K))
    f.append(text(130, 165, "Зменшення площі у ~6.5 разів!", size=9.5, color=C_OK, bold=True, anchor="start"))

    # Стовпчик 2: Пам'ять SRAM
    f.append(text(45, 195, "Кеш-пам'ять SRAM (Bitcell)", size=10.5, bold=True, anchor="start"))
    f.append(rect(45, 205, 220, 22, fill="#e2e8f0", stroke="#94a3b8", sw=1.0, rx=3))
    f.append(text(155, 220, "16 нм: 100% (база)", size=9.5, color=MUTED))
    f.append(rect(45, 230, 120, 22, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=3))
    f.append(text(105, 245, "55%", size=9.5, bold=True, color="#b45309"))
    f.append(text(175, 245, "Масштабування гальмує", size=9.5, color=MUTED, anchor="start"))

    # Стовпчик 3: Аналогові блоки та SerDes PHY
    f.append(text(45, 275, "Аналогові блоки, SerDes PHY, I/O контакти", size=10.5, bold=True, anchor="start"))
    f.append(rect(45, 285, 220, 22, fill="#e2e8f0", stroke="#94a3b8", sw=1.0, rx=3))
    f.append(text(155, 300, "16 нм: 100% (база)", size=9.5, color=MUTED))
    f.append(rect(45, 310, 195, 22, fill=C_DEFECT, stroke=C_DEFECT_K, sw=1.2, rx=3))
    f.append(text(142, 325, "88% (майже не зменшується!)", size=9.5, bold=True, color=C_DEFECT_K))
    f.append(text(45, 355, "Причина: вимоги до напруги, резисторів, індуктивностей", size=9.5, color=MUTED, anchor="start"))
    f.append(text(45, 372, "та ESD-захисту, які не залежать від довжини затвора.", size=9.5, color=MUTED, anchor="start"))

    # Правий блок: Порівняння вартості кремнію на пластині
    f.append(rect(425, 50, 370, 365, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(610, 75, "Економіка гетерогенного розщеплення", size=12, bold=True))

    # Вартість пластин
    f.append(rect(445, 100, 330, 48, fill="#f8fafc", stroke=LINE, sw=1.0, rx=4))
    f.append(text(460, 120, "Вартість 300-мм пластини 3 нм:", size=10, anchor="start"))
    f.append(text(760, 120, "~$20 000+", size=10.5, bold=True, color=C_WARN, anchor="end"))
    f.append(text(460, 139, "Вартість 300-мм пластини 12/28 нм:", size=10, anchor="start"))
    f.append(text(760, 139, "~$3 000–$4 500", size=10.5, bold=True, color=C_OK, anchor="end"))

    # Схема розподілу
    f.append(rect(445, 160, 330, 140, fill=C_SUBST, stroke=C_SUBST_K, sw=1.4, rx=6))
    f.append(text(610, 182, "Гетерогенна система за призначенням", size=11, bold=True, color=C_SUBST_K))

    # Малий чиплет логіки
    f.append(rect(460, 198, 140, 48, fill=C_COMPUTE, stroke=C_COMPUTE_K, sw=1.2, rx=3))
    f.append(text(530, 218, "Compute Die (3 нм)", size=10, bold=True, color=C_COMPUTE_K))
    f.append(text(530, 234, "Максимальна щільність", size=9, color=MUTED))

    # Великий I/O кристал
    f.append(rect(615, 198, 145, 48, fill=C_IOD, stroke=C_IOD_K, sw=1.2, rx=3))
    f.append(text(687, 218, "I/O Die (12/28 нм)", size=10, bold=True, color=C_IOD_K))
    f.append(text(687, 234, "Дешева площа під SerDes", size=9, color=MUTED))

    f.append(text(610, 266, "Зв'язок через високощільний D2D інтерконект", size=9.5, bold=True, color=C_SUBST_K))
    f.append(text(610, 283, "Економія сумарної собівартості системи: 40–60%", size=10, bold=True, color=C_OK))

    # Пояснення внизу правої панелі
    f.append(text(445, 325, "Висновок: перенесення I/O та аналогових схем", size=10, bold=True, anchor="start"))
    f.append(text(445, 344, "з дорогого техпроцесу 3 нм на зрілий вузол 12 нм", size=9.5, anchor="start"))
    f.append(text(445, 363, "вивільняє коштовний кремній під обчислювальні", size=9.5, anchor="start"))
    f.append(text(445, 382, "ядра без втрати загальної швидкодії системи.", size=9.5, anchor="start"))

    render(os.path.join(IMG, "heterogeneous-die-scaling.svg"), W, H, *f)


# ── Фігура 4: Рівнева архітектура стандарту UCIe ─────────────────────────────
def fig_ucie_stack_architecture():
    W, H = 840, 480
    f = [text(W / 2, 26, "Рівнева архітектура відкритого стандарту чиплетів UCIe",
              size=15, bold=True)]

    # Лівий чиплет (Die 0)
    f.append(rect(35, 55, 350, 335, fill="#ffffff", stroke=LINE, sw=1.6, rx=8))
    f.append(text(210, 78, "Чиплет 0 (Die 0: напр. CPU Core)", size=12.5, bold=True, color=C_COMPUTE_K))

    # Рівень 1: Protocol Layer
    f.append(rect(50, 95, 320, 65, fill="#e0f2fe", stroke="#0284c7", sw=1.4, rx=4))
    f.append(text(210, 116, "Рівень протоколів (Protocol Layer)", size=11.5, bold=True, color="#0369a1"))
    f.append(text(210, 134, "PCIe 6.0 Flit Mode  |  CXL 2.0 / 3.0 (io/cache/mem)", size=9.5, color=INK))
    f.append(text(210, 149, "Streaming Protocol (прямий користувацький інтерфейс)", size=9, color=MUTED))

    # FDI інтерфейс
    f.append(line(210, 160, 210, 180, color="#0284c7", sw=2.0))
    f.append(text(210, 173, "FDI (Flit-to-Die Interface)", size=9, bold=True, color="#0369a1"))

    # Рівень 2: Die-to-Die Adapter
    f.append(rect(50, 180, 320, 75, fill="#fef3c7", stroke="#d97706", sw=1.4, rx=4))
    f.append(text(210, 202, "D2D Адаптер (Die-to-Die Adapter)", size=11.5, bold=True, color="#b45309"))
    f.append(text(210, 220, "Арбітраж протоколів та мультиплексування флітів", size=9.5, color=INK))
    f.append(text(210, 235, "CRC-16 / CRC-32 + буфер повторної передачі (ARQ Retry)", size=9, color=INK))
    f.append(text(210, 248, "Керування живленням зв'язку: L0 (Active), L1, L2", size=9, color=MUTED))

    # RDI інтерфейс
    f.append(line(210, 255, 210, 275, color="#d97706", sw=2.0))
    f.append(text(210, 268, "RDI (Raw Die Interface)", size=9, bold=True, color="#b45309"))

    # Рівень 3: Physical Layer (PHY)
    f.append(rect(50, 275, 320, 100, fill="#ede9fe", stroke="#7c3aed", sw=1.4, rx=4))
    f.append(text(210, 297, "Фізичний рівень (Physical Layer / PHY)", size=11.5, bold=True, color="#6d28d9"))
    f.append(text(210, 316, "Standard Package (16/32 ліній) або Advanced (64 лінії)", size=9.5, color=INK))
    f.append(text(210, 332, "Однополярні сигнали (Single-Ended, 0.4–0.9 В), 4–32 Гбіт/с", size=9.5, color=INK))
    f.append(text(210, 348, "Вирівнювання фази, калібрування затримок та ремонт ліній", size=9, color=MUTED))
    f.append(text(210, 364, "Тактування: Forwarded Clock (окремий тактовий сигнал)", size=9.5, color="#6d28d9", bold=True))

    # Правий чиплет (Die 1)
    f.append(rect(455, 55, 350, 335, fill="#ffffff", stroke=LINE, sw=1.6, rx=8))
    f.append(text(630, 78, "Чиплет 1 (Die 1: напр. I/O Die / Accelerator)", size=12.5, bold=True, color=C_IOD_K))

    # Рівень 1: Protocol Layer
    f.append(rect(470, 95, 320, 65, fill="#e0f2fe", stroke="#0284c7", sw=1.4, rx=4))
    f.append(text(630, 116, "Рівень протоколів (Protocol Layer)", size=11.5, bold=True, color="#0369a1"))
    f.append(text(630, 134, "PCIe 6.0 Flit Mode  |  CXL 2.0 / 3.0 (io/cache/mem)", size=9.5, color=INK))
    f.append(text(630, 149, "Streaming Protocol (прямий користувацький інтерфейс)", size=9, color=MUTED))

    # FDI інтерфейс
    f.append(line(630, 160, 630, 180, color="#0284c7", sw=2.0))
    f.append(text(630, 173, "FDI (Flit-to-Die Interface)", size=9, bold=True, color="#0369a1"))

    # Рівень 2: Die-to-Die Adapter
    f.append(rect(470, 180, 320, 75, fill="#fef3c7", stroke="#d97706", sw=1.4, rx=4))
    f.append(text(630, 202, "D2D Адаптер (Die-to-Die Adapter)", size=11.5, bold=True, color="#b45309"))
    f.append(text(630, 220, "Арбітраж протоколів та мультиплексування флітів", size=9.5, color=INK))
    f.append(text(630, 235, "CRC-16 / CRC-32 + буфер повторної передачі (ARQ Retry)", size=9, color=INK))
    f.append(text(630, 248, "Керування живленням зв'язку: L0 (Active), L1, L2", size=9, color=MUTED))

    # RDI інтерфейс
    f.append(line(630, 255, 630, 275, color="#d97706", sw=2.0))
    f.append(text(630, 268, "RDI (Raw Die Interface)", size=9, bold=True, color="#b45309"))

    # Рівень 3: Physical Layer (PHY)
    f.append(rect(470, 275, 320, 100, fill="#ede9fe", stroke="#7c3aed", sw=1.4, rx=4))
    f.append(text(630, 297, "Фізичний рівень (Physical Layer / PHY)", size=11.5, bold=True, color="#6d28d9"))
    f.append(text(630, 316, "Standard Package (16/32 ліній) або Advanced (64 лінії)", size=9.5, color=INK))
    f.append(text(630, 332, "Однополярні сигнали (Single-Ended, 0.4–0.9 В), 4–32 Гбіт/с", size=9.5, color=INK))
    f.append(text(630, 348, "Вирівнювання фази, калібрування затримок та ремонт ліній", size=9, color=MUTED))
    f.append(text(630, 364, "Тактування: Forwarded Clock (окремий тактовий сигнал)", size=9.5, color="#6d28d9", bold=True))

    # Лінії фізичного зв'язку між PHY (канал зв'язку)
    f.append(rect(100, 405, 640, 55, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    f.append(text(420, 427, "Фізичне середовище з'єднання (Channel): Кремнієвий інтерпозер / Субстрат", size=11.5, bold=True))
    f.append(text(420, 445, "Паралельні доріжки D2D (довжина <2–25 мм, паразитна ємність <100 фФ, енергія <0.5 пДж/біт)", size=9.5, color=MUTED))

    # Стрілки з'єднання від PHY до середовища
    f.append(arrow(210, 375, 210, 405, color="#7c3aed", sw=2.0))
    f.append(arrow(630, 375, 630, 405, color="#7c3aed", sw=2.0))

    render(os.path.join(IMG, "ucie-stack-architecture.svg"), W, H, *f)


# ── Головний блок генерації ──────────────────────────────────────────────────
if __name__ == '__main__':
    fig_monolith_vs_chiplet()
    fig_packaging_technologies_25d_3d()
    fig_heterogeneous_die_scaling()
    fig_ucie_stack_architecture()
    print("OK: 4 SVG згенеровано у", IMG)
