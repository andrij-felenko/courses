# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

REDBG   = "#fbecec"
GRNBG   = "#eef6ef"
BLUEBG  = "#e9eefb"
AMBERBG = "#fff8e7"
AMBER   = "#d97706"

def fig1_joule_integral_concept():
    W, H = 760, 400
    p = []
    
    # Заголовок / фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e5e7eb", sw=1, rx=8))
    
    # Лівий графік: Струм i(t)
    p.append(rect(30, 40, 330, 300, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))
    p.append(text(195, 65, "Миттєвий струм аварії i(t)", size=13, color=INK, bold=True))
    
    # Осі лівого графіка
    p.append(line(70, 290, 330, 290, color=LINE, sw=1.5))  # вісь t
    p.append(line(70, 290, 70, 90, color=LINE, sw=1.5))   # вісь i
    p.append(text(335, 294, "t", size=12, color=INK, anchor="start", italic=True))
    p.append(text(65, 85, "i(t)", size=12, color=INK, anchor="end", italic=True))
    
    # Крива i(t) (імпульс КЗ)
    # Початкова точка (70, 290) -> пік (160, 120) -> спад (280, 290)
    p.append('<path d="M 70 290 C 100 280, 130 120, 160 120 C 190 120, 230 250, 280 290" fill="none" stroke="%s" stroke-width="2.5"/>' % POS)
    p.append(circle(160, 120, 4, fill=POS, stroke=POS))
    p.append(text(160, 110, "Піковий струм I_pk", size=11, color=POS, bold=True))
    p.append(line(160, 120, 160, 290, color=POS, sw=1, dash="3,3"))
    p.append(text(160, 308, "t_кз", size=11, color=MUTED))
    
    # Правий графік: Квадрат струму i²(t) та інтеграл Джоуля
    p.append(rect(390, 40, 340, 300, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))
    p.append(text(560, 65, "Квадрат струму i²(t) і теплова доза", size=13, color=INK, bold=True))
    
    # Осі правого графіка
    p.append(line(430, 290, 690, 290, color=LINE, sw=1.5)) # вісь t
    p.append(line(430, 290, 430, 90, color=LINE, sw=1.5))  # вісь i²
    p.append(text(695, 294, "t", size=12, color=INK, anchor="start", italic=True))
    p.append(text(425, 85, "i²(t)", size=12, color=INK, anchor="end", italic=True))
    
    # Заливка інтеграла (площа під i²(t))
    p.append('<path d="M 430 290 C 470 285, 490 130, 520 130 C 550 130, 580 260, 640 290 Z" fill="%s" opacity="0.35" stroke="none"/>' % REDBG)
    p.append('<path d="M 430 290 C 470 285, 490 130, 520 130 C 550 130, 580 260, 640 290" fill="none" stroke="%s" stroke-width="2.5"/>' % POS)
    
    # Пояснення площі
    p.append(text(545, 205, "Площа = ∫ i² dt (А²·с)", size=12, color=POS, bold=True))
    p.append(text(545, 225, "Питома наскрізна енергія", size=10, color=INK))
    p.append(text(545, 245, "Виділене тепло: Q = R · I²t", size=11, color=FIELD, bold=True))
    
    # Нижній висновок
    p.append(text(380, 365, "Для швидкої аварії (< 10 мс) форма хвилі не важлива — нагрів визначає лише накопичений інтеграл I²t", size=11, color=INK, bold=True))
    
    render(os.path.join(OUT, "fig1-joule-integral-concept.svg"), W, H, *p,
           title="Фізичний зміст інтеграла Джоуля I²t")

def fig2_melting_vs_arcing():
    W, H = 760, 420
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e5e7eb", sw=1, rx=8))
    
    # Верхня панель: хвиля струму і фази
    p.append(rect(30, 35, 700, 220, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))
    p.append(text(380, 55, "Динаміка струму та напруги запобіжника під час відключення КЗ", size=13, color=INK, bold=True))
    
    # Осі
    p.append(line(80, 210, 690, 210, color=LINE, sw=1.5)) # вісь часу
    p.append(line(80, 210, 80, 70, color=LINE, sw=1.5))   # вісь струму/напруги
    p.append(text(695, 214, "t", size=12, color=INK, anchor="start", italic=True))
    
    # Фази по часу
    # t0 = 100, t_melt = 300, t_clear = 580
    p.append(line(100, 210, 100, 70, color=MUTED, sw=1, dash="3,3"))
    p.append(line(300, 210, 300, 70, color=MUTED, sw=1, dash="3,3"))
    p.append(line(580, 210, 580, 70, color=MUTED, sw=1, dash="3,3"))
    
    p.append(text(100, 226, "t_0 (початок КЗ)", size=10, color=MUTED))
    p.append(text(300, 226, "t_melt (розплавлення)", size=10, color=POS, bold=True))
    p.append(text(580, 226, "t_clear (згасання дуги)", size=10, color=FIELD, bold=True))
    
    # Фазові зони кольором
    p.append(rect(100, 75, 200, 130, fill=AMBERBG, stroke="none", rx=0))
    p.append(rect(300, 75, 280, 130, fill=REDBG, stroke="none", rx=0))
    
    # Крива струму i(t)
    # Наростання від (100, 210) до піку плавлення (300, 90), потім спад під дією дуги до (580, 210)
    p.append('<path d="M 100 210 C 160 190, 230 100, 300 90 C 370 85, 470 140, 580 210" fill="none" stroke="%s" stroke-width="3"/>' % POS)
    p.append(text(250, 120, "Струм КЗ i(t)", size=12, color=POS, bold=True))
    
    # Крива напруги дуги u_fuse(t)
    # Від (100, 205) до (300, 205), стрибок вгору (300, 80) -> спад до напруги мережі (580, 150) -> (680, 150)
    p.append('<path d="M 100 205 L 300 205 L 310 80 C 360 85, 480 120, 580 150 L 680 150" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,2"/>' % NEG)
    p.append(text(460, 95, "Напруга дуги U_arc > U_мережі", size=11, color=NEG, bold=True))
    
    # Нижня панель: смуги енергії
    p.append(rect(30, 265, 700, 130, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))
    
    # Смуга Pre-arcing
    p.append(rect(80, 290, 220, 45, fill=AMBERBG, stroke=AMBER, sw=1.5, rx=4))
    p.append(text(190, 310, "Melting I²t (Pre-arcing)", size=11, color=AMBER, bold=True))
    p.append(text(190, 326, "Нагрів до плавлення і випаровування", size=9, color=INK))
    
    # Смуга Arcing
    p.append(rect(305, 290, 300, 45, fill=REDBG, stroke=POS, sw=1.5, rx=4))
    p.append(text(455, 310, "Arcing I²t (Горіння дуги)", size=11, color=POS, bold=True))
    p.append(text(455, 326, "Енергія дуги в кварцовому піску до повного розриву", size=9, color=INK))
    
    # Сумарна дужка / стрілка
    p.append(line(80, 355, 605, 355, color=FIELD, sw=2))
    p.append(circle(80, 355, 3, fill=FIELD, stroke=FIELD))
    p.append(circle(605, 355, 3, fill=FIELD, stroke=FIELD))
    p.append(text(342, 375, "Clearing I²t (Total) = Melting I²t + Arcing I²t (Повна пропущена енергія)", size=11, color=FIELD, bold=True))
    
    render(os.path.join(OUT, "fig2-melting-vs-arcing.svg"), W, H, *p,
           title="Етапи відключення: плавлення (Melting) і горіння дуги (Arcing)")

def fig3_coordination_selectivity():
    W, H = 760, 420
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e5e7eb", sw=1, rx=8))
    
    # Ліва частина: Схема кола
    p.append(rect(30, 35, 310, 355, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))
    p.append(text(185, 60, "Схема селективного захисту", size=13, color=INK, bold=True))
    
    # Джерело живлення
    p.append(circle(185, 95, 18, fill=BLUEBG, stroke=NEG, sw=1.8))
    p.append(text(185, 99, "U_вх", size=11, color=NEG, bold=True))
    p.append(line(185, 113, 185, 135, color=LINE, sw=1.8))
    
    # Запобіжник F1 (Головний)
    p.append(rect(145, 135, 80, 35, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=4))
    p.append(line(140, 152, 230, 152, color=LINE, sw=1.5))
    p.append(text(185, 148, "F1 (Ввідний)", size=10, color=AMBER, bold=True))
    p.append(text(185, 163, "наприклад, 63 А", size=9, color=MUTED))
    
    p.append(line(185, 170, 185, 205, color=LINE, sw=1.8))
    
    # Розгалуження на дві гілки
    p.append(line(110, 205, 260, 205, color=LINE, sw=1.8))
    p.append(line(110, 205, 110, 230, color=LINE, sw=1.8))
    p.append(line(260, 205, 260, 230, color=LINE, sw=1.8))
    
    # Гілка 1: Здорова
    p.append(rect(75, 230, 70, 30, fill=FILL, stroke=LINE, sw=1.4, rx=4))
    p.append(text(110, 248, "F3 (20 А)", size=9, color=INK))
    p.append(line(110, 260, 110, 280, color=LINE, sw=1.8))
    p.append(rect(80, 280, 60, 35, fill=GRNBG, stroke=FIELD, sw=1.4, rx=4))
    p.append(text(110, 302, "Навантаж. 1", size=9, color=FIELD))
    
    # Гілка 2: Аварійна (F2)
    p.append(rect(225, 230, 70, 30, fill=REDBG, stroke=POS, sw=1.6, rx=4))
    p.append(text(260, 248, "F2 (20 А)", size=9, color=POS, bold=True))
    p.append(line(260, 260, 260, 280, color=LINE, sw=1.8))
    p.append(rect(230, 280, 60, 35, fill=REDBG, stroke=POS, sw=1.4, rx=4))
    p.append(text(260, 297, "КЗ!", size=10, color=POS, bold=True))
    p.append(text(260, 310, "Аварія", size=9, color=POS))
    
    p.append(text(185, 355, "Вимога: вимикається тільки F2,", size=10, color=FIELD, bold=True))
    p.append(text(185, 372, "а ввідний F1 залишається неушкодженим", size=9, color=INK))
    
    # Права частина: Енергетична умова селективності
    p.append(rect(360, 35, 370, 355, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))
    p.append(text(545, 60, "Енергетична умова координації (I²t)", size=13, color=INK, bold=True))
    
    # Смуги порівняння енергії
    # Верхня: F2 Clearing I²t
    p.append(text(380, 100, "Нижній апарат F2 (Clearing I²t):", size=11, color=POS, anchor="start", bold=True))
    p.append(rect(380, 112, 170, 34, fill=REDBG, stroke=POS, sw=1.5, rx=4))
    p.append(text(465, 133, "Total I²t (F2) = 1 200 А²·с", size=10, color=POS, bold=True))
    
    # Нижня: F1 Melting I²t
    p.append(text(380, 175, "Верхній апарат F1 (Melting I²t):", size=11, color=AMBER, anchor="start", bold=True))
    p.append(rect(380, 187, 280, 34, fill=AMBERBG, stroke=AMBER, sw=1.5, rx=4))
    p.append(text(520, 208, "Melting I²t (F1) = 3 500 А²·с", size=10, color=AMBER, bold=True))
    
    # Запас селективності (стрілка різниці)
    p.append(line(550, 112, 550, 187, color=FIELD, sw=1.5, dash="3,3"))
    p.append(rect(560, 135, 150, 36, fill=GRNBG, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(635, 150, "Запас селективності", size=9, color=FIELD, bold=True))
    p.append(text(635, 163, "F1 навіть не розплавився", size=9, color=INK))
    
    # Формула в рамці
    p.append(rect(380, 245, 330, 60, fill=GRNBG, stroke=FIELD, sw=1.8, rx=6))
    p.append(text(545, 268, "Критерій повної селективності:", size=11, color=INK))
    p.append(text(545, 290, "Total I²t (нижній F2) < Melting I²t (верхній F1)", size=11, color=FIELD, bold=True))
    
    p.append(text(545, 335, "Якщо умова не виконується — плавкий елемент F1", size=10, color=POS))
    p.append(text(545, 350, "розігріється до розриву або втратить ресурс (хибне відключення)", size=9, color=MUTED))
    
    render(os.path.join(OUT, "fig3-coordination-selectivity.svg"), W, H, *p,
           title="Селективність та координація захисту за енергією I²t")

def fig4_semiconductor_vs_gg():
    W, H = 760, 400
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e5e7eb", sw=1, rx=8))
    
    # Заголовок
    p.append(text(380, 38, "Захист напівпровідників: стандартний gG проти надшвидкого aR", size=13, color=INK, bold=True))
    
    # 3 стовпчики порівняння енергії
    # Лівий: Стійкість кристала
    p.append(rect(40, 65, 205, 300, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))
    p.append(text(142, 90, "Кристал IGBT / Діод", size=12, color=INK, bold=True))
    p.append(text(142, 106, "Межа виживання кристала", size=9, color=MUTED))
    
    p.append(rect(65, 170, 155, 140, fill=BLUEBG, stroke=NEG, sw=2, rx=4))
    p.append(text(142, 230, "I²t Withstand", size=12, color=NEG, bold=True))
    p.append(text(142, 250, "Стійкість кристала", size=10, color=INK))
    p.append(text(142, 275, "наприклад, 800 А²·с", size=10, color=NEG, bold=True))
    
    # Центральний: Стандартний gG (Знищення)
    p.append(rect(275, 65, 210, 300, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(text(380, 90, "Стандартний gG (лінійний)", size=12, color=POS, bold=True))
    p.append(text(380, 106, "Для кабелів і трансформаторів", size=9, color=MUTED))
    
    p.append(rect(300, 120, 160, 190, fill=REDBG, stroke=POS, sw=2, rx=4))
    p.append(text(380, 180, "Total I²t (gG)", size=12, color=POS, bold=True))
    p.append(text(380, 205, "3 500 А²·с", size=13, color=POS, bold=True))
    p.append(text(380, 240, "Повільне плавлення,", size=10, color=INK))
    p.append(text(380, 256, "велика енергія дуги", size=10, color=INK))
    
    p.append(rect(290, 320, 180, 34, fill=REDBG, stroke=POS, sw=1.2, rx=4))
    p.append(text(380, 342, "КРИСТАЛ ЗНИЩЕНО!", size=10, color=POS, bold=True))
    
    # Правий: Надшвидкий aR (Порятунок)
    p.append(rect(515, 65, 205, 300, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(617, 90, "Надшвидкий aR / gR", size=12, color=FIELD, bold=True))
    p.append(text(617, 106, "Срібна смужка зі звуженнями", size=9, color=MUTED))
    
    p.append(rect(540, 230, 155, 80, fill=GRNBG, stroke=FIELD, sw=2, rx=4))
    p.append(text(617, 260, "Total I²t (aR)", size=12, color=FIELD, bold=True))
    p.append(text(617, 280, "450 А²·с", size=13, color=FIELD, bold=True))
    
    p.append(rect(530, 320, 175, 34, fill=GRNBG, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(617, 342, "КРИСТАЛ ВРЯТОВАНО", size=10, color=FIELD, bold=True))
    
    # Риска стійкості через весь графік
    p.append(line(50, 170, 710, 170, color=NEG, sw=1.5, dash="4,4"))
    p.append(text(490, 163, "Межа стійкості I²t_withstand", size=9, color=NEG, bold=True))
    
    p.append(text(380, 385, "Умова захисту напівпровідника: Total I²t (запобіжника) < Withstand I²t (кристала)", size=10, color=FIELD, bold=True))
    
    render(os.path.join(OUT, "fig4-semiconductor-vs-gg.svg"), W, H, *p,
           title="Порівняння енергії відключення gG та aR для захисту силових кристалів")

def fig5_inrush_derating_curve():
    W, H = 760, 400
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e5e7eb", sw=1, rx=8))
    p.append(text(380, 38, "Крива термомеханічної втоми (Pulse Derating Factor)", size=13, color=INK, bold=True))
    
    # Графік
    p.append(rect(40, 55, 680, 285, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6))
    
    # Осі (X: логарифмічна кількість циклів 1..100 000; Y: % від I²t плавлення 0..100%)
    p.append(line(90, 290, 680, 290, color=LINE, sw=1.5))
    p.append(line(90, 290, 90, 80, color=LINE, sw=1.5))
    
    p.append(text(685, 294, "Кількість циклів (N)", size=11, color=INK, anchor="start"))
    p.append(text(85, 75, "I²t_імпульсу / I²t_плавлення (%)", size=10, color=INK, anchor="end"))
    
    # Сітка та мітки X (1, 10, 100, 1 000, 10 000, 100 000)
    x_ticks = [(90, "1"), (200, "10"), (310, "100"), (420, "1 000"), (530, "10 000"), (640, "100 000")]
    for x_pos, label in x_ticks:
        p.append(line(x_pos, 290, x_pos, 85, color="#f3f4f6", sw=1))
        p.append(line(x_pos, 290, x_pos, 295, color=LINE, sw=1.2))
        p.append(text(x_pos, 310, label, size=10, color=INK))
        
    # Сітка та мітки Y (0%, 20%, 40%, 60%, 80%, 100%)
    y_ticks = [(290, "0%"), (250, "20%"), (210, "40%"), (170, "60%"), (130, "80%"), (90, "100%")]
    for y_pos, label in y_ticks:
        p.append(line(90, y_pos, 660, y_pos, color="#f3f4f6", sw=1))
        p.append(line(85, y_pos, 90, y_pos, color=LINE, sw=1.2))
        p.append(text(80, y_pos + 4, label, size=10, color=INK, anchor="end"))
        
    # Заливка безпечної зони під кривою
    p.append('<path d="M 90 90 L 200 150 L 310 190 L 420 214 L 530 232 L 640 246 L 640 290 L 90 290 Z" fill="%s" opacity="0.4"/>' % GRNBG)
    # Заливка небезпечної зони над кривою
    p.append('<path d="M 90 90 L 200 150 L 310 190 L 420 214 L 530 232 L 640 246 L 640 85 L 90 85 Z" fill="%s" opacity="0.3"/>' % REDBG)
    
    # Сама крива
    p.append('<path d="M 90 90 L 200 150 L 310 190 L 420 214 L 530 232 L 640 246" fill="none" stroke="%s" stroke-width="3"/>' % POS)
    
    # Точки на кривій
    pts = [(90, 90, "100%"), (200, 150, "70%"), (310, 190, "50%"), (420, 214, "38%"), (530, 232, "29%"), (640, 246, "22%")]
    for x, y, val in pts:
        p.append(circle(x, y, 4, fill=POS, stroke=BG, sw=1.5))
        
    p.append(text(250, 115, "ЗОНА ДЕГРАДАЦІЇ ТА ХИБНОГО ЗГОРАННЯ", size=10, color=POS, bold=True))
    p.append(text(270, 260, "БЕЗПЕЧНА ЗОНА ТРИВАЛОЇ ЕКСПЛУАТАЦІЇ", size=10, color=FIELD, bold=True))
    
    # Виноска на 10 000 циклів
    p.append(line(530, 232, 530, 130, color=AMBER, sw=1.2, dash="3,3"))
    p.append(rect(430, 105, 200, 30, fill=AMBERBG, stroke=AMBER, sw=1.2, rx=4))
    p.append(text(530, 124, "10 000 пусків: запас I²t ≥ 3.5× (29%)", size=9, color=AMBER, bold=True))
    
    # Підпис внизу
    p.append(text(380, 370, "Через повторний циклічний нагрів запобіжник витримує лише ~20–30% номінального I²t", size=11, color=INK, bold=True))
    
    render(os.path.join(OUT, "fig5-inrush-derating-curve.svg"), W, H, *p,
           title="Крива зниження допустимої енергії I²t залежно від кількості пускових імпульсів")

def main():
    fig1_joule_integral_concept()
    fig2_melting_vs_arcing()
    fig3_coordination_selectivity()
    fig4_semiconductor_vs_gg()
    fig5_inrush_derating_curve()
    print("Всі фігури успішно згенеровано.")

if __name__ == "__main__":
    main()
