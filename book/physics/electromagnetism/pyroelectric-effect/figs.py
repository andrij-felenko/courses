# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)

def gen_pyroelectric_mechanism():
    """Фігура 1: Фізичний механізм генерації піроелектричного струму під час нагріву та охолодження."""
    w, h = 820, 380
    frags = []

    # Загальний фон / заголовок
    frags.append(rect(10, 10, 800, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    
    # Стан 1: Рівновага (T = T0, dT/dt = 0)
    frags.append(rect(25, 30, 245, 325, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(147, 52, "1. Рівновага (T = T₀)", size=13, bold=True, anchor="middle", color=INK))
    frags.append(text(147, 70, "dT/dt = 0", size=11, bold=True, anchor="middle", color=MUTED))
    
    # Кристал 1
    frags.append(rect(65, 120, 165, 120, fill="#f1f5f9", stroke="#64748b", sw=2, rx=4))
    # Поляризація Ps
    frags.append(arrow(147, 215, 147, 145, color=POS, sw=2.5))
    frags.append(text(147, 185, "P_s", size=12, bold=True, anchor="middle", color=POS))
    # Зв'язані заряди на поверхні (верх - , низ +)
    for x in [80, 110, 140, 170, 200]:
        frags.append(text(x, 115, "−", size=14, bold=True, anchor="middle", color=NEG))
        frags.append(text(x, 252, "+", size=14, bold=True, anchor="middle", color=POS))
    # Електроди та компенсаційні вільні заряди
    frags.append(rect(60, 95, 175, 8, fill="#94a3b8", stroke="#475569"))
    frags.append(rect(60, 257, 175, 8, fill="#94a3b8", stroke="#475569"))
    for x in [80, 110, 140, 170, 200]:
        frags.append(text(x, 91, "+", size=12, bold=True, anchor="middle", color=POS))
        frags.append(text(x, 276, "−", size=12, bold=True, anchor="middle", color=NEG))
    
    frags.append(text(147, 305, "Повна компенсація", size=11, anchor="middle", color=INK))
    frags.append(text(147, 325, "i_p = 0", size=12, bold=True, anchor="middle", color=MUTED))

    # Стан 2: Нагрів (dT/dt > 0)
    frags.append(rect(285, 30, 245, 325, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(407, 52, "2. Нагрів (T ↑)", size=13, bold=True, anchor="middle", color=NEG))
    frags.append(text(407, 70, "dT/dt > 0", size=11, bold=True, anchor="middle", color=NEG))
    
    # Кристал 2 (розширений)
    frags.append(rect(325, 120, 165, 120, fill="#fef2f2", stroke="#fca5a5", sw=2, rx=4))
    # Менша поляризація Ps
    frags.append(arrow(407, 200, 407, 160, color=POS, sw=2.0))
    frags.append(text(407, 182, "P_s↓", size=12, bold=True, anchor="middle", color=POS))
    # Зв'язані заряди (менше)
    for x in [100, 147, 194]:
        frags.append(text(x + 260, 115, "−", size=14, bold=True, anchor="middle", color=NEG))
        frags.append(text(x + 260, 252, "+", size=14, bold=True, anchor="middle", color=POS))
    # Електроди
    frags.append(rect(320, 95, 175, 8, fill="#94a3b8", stroke="#475569"))
    frags.append(rect(320, 257, 175, 8, fill="#94a3b8", stroke="#475569"))
    # Надлишкові вільні заряди витікають у коло
    frags.append(arrow(320, 99, 295, 99, color=NEG, sw=2))
    frags.append(line(295, 99, 295, 261, color=NEG, sw=2))
    frags.append(arrow(295, 261, 320, 261, color=NEG, sw=2))
    frags.append(text(280, 180, "i_p", size=12, bold=True, anchor="middle", color=NEG))
    
    frags.append(text(407, 305, "Втрата дипольного моменту", size=11, anchor="middle", color=INK))
    frags.append(text(407, 325, "i_p = A · p · (dT/dt)", size=12, bold=True, anchor="middle", color=NEG))

    # Стан 3: Охолодження (dT/dt < 0)
    frags.append(rect(545, 30, 245, 325, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(667, 52, "3. Охолодження (T ↓)", size=13, bold=True, anchor="middle", color=FIELD))
    frags.append(text(667, 70, "dT/dt < 0", size=11, bold=True, anchor="middle", color=FIELD))
    
    # Кристал 3
    frags.append(rect(585, 120, 165, 120, fill="#eff6ff", stroke="#93c5fd", sw=2, rx=4))
    # Більша поляризація Ps
    frags.append(arrow(667, 225, 667, 135, color=POS, sw=3.0))
    frags.append(text(667, 182, "P_s↑", size=12, bold=True, anchor="middle", color=POS))
    # Зв'язані заряди (більше)
    for x in [70, 95, 120, 147, 172, 197, 222]:
        frags.append(text(x + 520, 115, "−", size=12, bold=True, anchor="middle", color=NEG))
        frags.append(text(x + 520, 252, "+", size=12, bold=True, anchor="middle", color=POS))
    # Електроди
    frags.append(rect(580, 95, 175, 8, fill="#94a3b8", stroke="#475569"))
    frags.append(rect(580, 257, 175, 8, fill="#94a3b8", stroke="#475569"))
    # Струм в протилежний бік
    frags.append(arrow(755, 261, 780, 261, color=FIELD, sw=2))
    frags.append(line(780, 261, 780, 99, color=FIELD, sw=2))
    frags.append(arrow(780, 99, 755, 99, color=FIELD, sw=2))
    frags.append(text(795, 180, "i_p", size=12, bold=True, anchor="middle", color=FIELD))
    
    frags.append(text(667, 305, "Зростання дипольного моменту", size=11, anchor="middle", color=INK))
    frags.append(text(667, 325, "Струм протилежної полярності", size=11, bold=True, anchor="middle", color=FIELD))

    render(os.path.join(IMG_DIR, "pyroelectric-mechanism.svg"), w, h, *frags)

def gen_crystal_hierarchy():
    """Фігура 2: Ієрархія кристалографічних класів (Діелектрики, П'єзоелектрики, Піроелектрики, Сегнетоелектрики)."""
    w, h = 740, 420
    frags = []

    # 1. Діелектрики (32 класи)
    frags.append(rect(20, 20, 700, 380, fill="#f8fafc", stroke="#64748b", sw=2, rx=10))
    frags.append(text(40, 48, "Діелектричні кристали (32 точкові групи)", size=13, bold=True, color=INK))
    frags.append(text(690, 48, "Приклад: NaCl, SiO₂ (кварц)", size=11, anchor="end", color=MUTED))

    # 2. П'єзоелектрики (20 нецентросиметричних класів)
    frags.append(rect(45, 70, 650, 315, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=8))
    frags.append(text(65, 95, "П'єзоелектрики (20 нецентросиметричних класів)", size=13, bold=True, color="#1d4ed8"))
    frags.append(text(670, 95, "Прямий/зворотний п'єзоефект (α-кварц 32)", size=11, anchor="end", color=MUTED))

    # 3. Піроелектрики (10 полярних класів)
    frags.append(rect(70, 120, 600, 250, fill="#fef3c7", stroke="#d97706", sw=2, rx=8))
    frags.append(text(90, 145, "Піроелектрики (10 полярних класів з спонтанною поляризацією P_s)", size=13, bold=True, color="#b45309"))
    frags.append(text(650, 145, "Несегнетоелектрики: Турмалін, ZnO, Li₂SO₄·H₂O", size=11, anchor="end", color=MUTED))

    # 4. Сегнетоелектрики (Підмножина полярних класів з обратимою P_s)
    frags.append(rect(95, 170, 550, 185, fill="#fef2f2", stroke="#ef4444", sw=2, rx=8))
    frags.append(text(115, 198, "Сегнетоелектрики (Обратимий вектор P_s під дією поля E)", size=13, bold=True, color="#b91c1c"))
    frags.append(text(115, 225, "Матеріали: LiTaO₃, LiNbO₃, TGS, PZT-кераміка, PVDF-полімер", size=11, color=INK))
    frags.append(text(115, 252, "Особливість: можливість поляризації полікристалів і плівок", size=11, bold=True, color="#b91c1c"))
    frags.append(text(115, 280, "Усі сегнетоелектрики є піроелектриками, але не навпаки!", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, "crystal-hierarchy.svg"), w, h, *frags)

def gen_frequency_response():
    """Фігура 3: Частотна характеристика піроелектричного детектора (Теплова та електрична складові)."""
    w, h = 760, 420
    frags = []

    # Фон
    frags.append(rect(10, 10, 740, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(380, 35, "Частотна характеристика вольтової чутливості R_v(f)", size=14, bold=True, anchor="middle", color=INK))

    # Осі графіку
    ox, oy = 80, 330
    gw, gh = 620, 250
    frags.append(arrow(ox, oy, ox + gw, oy, color=LINE, sw=1.8)) # log f
    frags.append(arrow(ox, oy, ox, oy - gh, color=LINE, sw=1.8)) # R_v

    frags.append(text(ox + gw - 10, oy + 25, "Частота модуляції f (Гц, логарифмічна шкала)", size=12, bold=True, anchor="end", color=INK))
    frags.append(text(ox - 15, oy - gh + 15, "Чутливість R_v (В/Вт)", size=12, bold=True, anchor="start", color=INK))

    # Крива R_v(f) - полосовий фільтр
    path_rv = ("M 90 320 "
               "C 160 310, 220 120, 260 110 "
               "L 460 110 "
               "C 520 120, 580 310, 660 320")
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_rv, FIELD))

    # Вертикальні пунктири критичних частот
    frags.append(line(260, oy, 260, 90, color=NEG, sw=1.5, dash="4,4"))
    frags.append(circle(260, 110, 5, fill=NEG))
    frags.append(text(260, oy + 18, "f_th = 1/(2π·τ_th)", size=11, bold=True, anchor="middle", color=NEG))
    frags.append(text(260, oy + 32, "Тепловий зріз (~0.1–1 Гц)", size=10, anchor="middle", color=MUTED))

    frags.append(line(460, oy, 460, 90, color=POS, sw=1.5, dash="4,4"))
    frags.append(circle(460, 110, 5, fill=POS))
    frags.append(text(460, oy + 18, "f_e = 1/(2π·τ_e)", size=11, bold=True, anchor="middle", color=POS))
    frags.append(text(460, oy + 32, "Електричний зріз (~10–100 Гц)", size=10, anchor="middle", color=MUTED))

    # Пояснення областей
    frags.append(text(160, 230, "Підйом +20 дБ/дек\n(Витік тепла G_th)", size=11, anchor="middle", color=NEG))
    frags.append(text(360, 85, "Максимальна чутливість R_v,max\n(Плоска робоча зона)", size=11, bold=True, anchor="middle", color=FIELD))
    frags.append(text(570, 230, "Спад -20 дБ/дек\n(Шунтування C_in)", size=11, anchor="middle", color=POS))

    frags.append(line(260, 110, 460, 110, color=FIELD, sw=1.5, dash="2,2"))

    render(os.path.join(IMG_DIR, "frequency-response.svg"), w, h, *frags)

def gen_pir_dual_topology():
    """Фігура 4: Диференціальна топологія двоелементного PIR-датчика та первинна схема підсилення."""
    w, h = 800, 400
    frags = []

    frags.append(rect(10, 10, 780, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    
    # Ліва частина: Оптична система та 2 кристали
    frags.append(rect(30, 40, 330, 330, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(195, 65, "Двоелементний сенсор (PZT/LiTaO₃)", size=13, bold=True, anchor="middle", color=INK))

    # Лінза Френеля
    frags.append('<path d="M 40 100 Q 55 200, 40 300" fill="none" stroke="#3b82f6" stroke-width="4"/>')
    frags.append(text(50, 85, "Лінза Френеля", size=10, color="#1d4ed8"))
    
    # Промені ІЧ-випромінювання
    frags.append(line(55, 140, 110, 140, color="#ef4444", sw=2, dash="3,3"))
    frags.append(line(55, 260, 110, 260, color="#ef4444", sw=2, dash="3,3"))
    frags.append(text(80, 130, "ІЧ 10 мкм", size=10, color="#ef4444"))

    # Кристал 1 (+)
    frags.append(rect(120, 110, 80, 60, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=4))
    frags.append(text(160, 135, "Елемент A", size=11, bold=True, anchor="middle", color="#b91c1c"))
    frags.append(text(160, 155, "(Полярність +)", size=10, anchor="middle", color=POS))

    # Кристал 2 (-)
    frags.append(rect(120, 230, 80, 60, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    frags.append(text(160, 255, "Елемент B", size=11, bold=True, anchor="middle", color="#1d4ed8"))
    frags.append(text(160, 275, "(Полярність −)", size=10, anchor="middle", color=NEG))

    # Зустрічно-послідовне з'єднання
    frags.append(line(200, 140, 240, 140, color=LINE, sw=2))
    frags.append(line(240, 140, 240, 260, color=LINE, sw=2))
    frags.append(line(200, 260, 240, 260, color=LINE, sw=2))
    frags.append(circle(240, 200, 4, fill=INK))
    
    frags.append(text(195, 320, "Спільна фонова завада: Δi = 0", size=11, bold=True, anchor="middle", color=POS))
    frags.append(text(195, 345, "Рух об'єкта: послідовні i_p(+) та i_p(-)", size=11, anchor="middle", color=INK))

    # Права частина: Схема узгодження JFET та підсилювач
    frags.append(rect(380, 40, 390, 330, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(575, 65, "Внутрішній JFET-повторювач та каскад", size=13, bold=True, anchor="middle", color=INK))

    # Затвор JFET та сеточний резистор Rg (50 GOm)
    frags.append(line(340, 200, 430, 200, color=LINE, sw=2))
    frags.append(circle(430, 200, 3, fill=INK))

    # JFET Транзистор
    frags.append(rect(450, 160, 50, 80, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=4))
    frags.append(text(475, 205, "JFET", size=11, bold=True, anchor="middle", color=INK))
    
    # Виводи Drain (VDD), Source (OUT), Gate
    frags.append(line(430, 200, 450, 200, color=LINE, sw=2)) # Gate
    frags.append(line(475, 160, 475, 100, color=POS, sw=2)) # Drain
    frags.append(text(475, 90, "VDD (5V)", size=11, bold=True, anchor="middle", color=POS))
    
    frags.append(line(475, 240, 475, 290, color=LINE, sw=2)) # Source
    frags.append(rect(460, 290, 30, 40, fill="#ffffff", stroke=LINE, sw=1.5)) # Rs
    frags.append(text(475, 310, "R_s", size=10, anchor="middle", color=INK))
    frags.append(line(475, 330, 475, 350, color=LINE, sw=2)) # GND
    frags.append(line(460, 350, 490, 350, color=LINE, sw=2))

    # Вихідний сигнал від Source до смугового підсилювача
    frags.append(circle(475, 265, 3, fill=FIELD))
    frags.append(arrow(475, 265, 540, 265, color=FIELD, sw=2))

    # Активний смуговий підсилювач (Op-Amp)
    frags.append(rect(540, 230, 110, 70, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    frags.append(text(595, 258, "Смуговий\nпідсилювач", size=11, bold=True, anchor="middle", color="#1d4ed8"))
    frags.append(text(595, 285, "K_v ≈ 60-80 дБ", size=10, anchor="middle", color=MUTED))

    # Вихід на АЦП
    frags.append(arrow(650, 265, 730, 265, color=POS, sw=2))
    frags.append(text(745, 265, "АЦП / MCU", size=11, bold=True, anchor="start", color=POS))

    # Резистор сітки R_g (50 GOhm) на землю
    frags.append(line(410, 200, 410, 280, color=LINE, sw=1.5))
    frags.append(rect(400, 280, 20, 35, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(410, 300, "R_g", size=10, anchor="middle", color=INK))
    frags.append(line(410, 315, 410, 330, color=LINE, sw=1.5))
    frags.append(text(410, 345, "50 ГОм", size=9, anchor="middle", color=MUTED))

    render(os.path.join(IMG_DIR, "pir-dual-topology.svg"), w, h, *frags)

if __name__ == "__main__":
    gen_pyroelectric_mechanism()
    gen_crystal_hierarchy()
    gen_frequency_response()
    gen_pir_dual_topology()
    print("Всі 4 фігури згенеровано успішно.")
