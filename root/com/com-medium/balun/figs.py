# -*- coding: utf-8 -*-
import sys
import os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору з book/communications/radio-engineering/balun)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def render(w, h, elements):
    """Скласти підсумковий SVG-документ з оголошенням стрілок."""
    defs = '''<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/>
    </marker>
  </defs>''' % INK
    body = "\n  ".join(elements)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '  %s\n  %s\n</svg>' % (w, h, w, h, defs, body))

def save_svg(filename, content):
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Збережено: %s" % path)


# ── Фігура 1: Струми спільної моди та дія балуна ──────────────────────────────
def fig_common_mode_current():
    W, H = 780, 380
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    # Секція Ліва: Живлення без балуна
    p.append(rect(15, 15, 365, 350, fill="#fff5f5", stroke=POS, sw=1.2, rx=8))
    p.append(text(197, 38, "Пряме живлення (Без Балуна)", size=13, color=POS, bold=True))

    # Коаксіал ліворуч
    p.append(rect(35, 180, 90, 24, fill="#e8ecef", stroke=INK, sw=1.5, rx=3))
    p.append(line(35, 192, 125, 192, color=POS, sw=2.0)) # Центральна жила
    p.append(text(75, 168, "Кабель 50 Ом", size=10, color=MUTED))

    # Диполь
    p.append(line(125, 115, 125, 192, color=POS, sw=3.0)) # Верхнє плече
    p.append(line(125, 192, 125, 245, color=NEG, sw=3.0)) # Нижнє плече
    p.append(text(125, 95, "+ Плече 1", size=10, color=POS, bold=True))
    p.append(text(125, 258, "− Плече 2", size=10, color=NEG, bold=True))

    # Струми
    p.append(arrow(40, 188, 105, 188, color=POS, sw=1.5))
    p.append(text(75, 152, "I_1 (жила)", size=9, color=POS, bold=True))

    p.append(arrow(105, 196, 40, 196, color=NEG, sw=1.5))
    p.append(text(75, 212, "I_2 (оплітка вхід)", size=9, color=NEG))

    # Струм затікання I_3 (на зовнішній оболонці)
    p.append(arrow(125, 225, 45, 225, color=POS, sw=2.2))
    p.append(textbox(85, 310, "Паразитний струм I_3\n(зовнішня оплітка)", size=9, color=POS, fill="#ffffff", stroke=POS, min_w=125)[0])

    # Спотворення ДН
    p.append(textbox(275, 185, "Наслідки затікання:\n1. Спотворення ДН (кос)\n2. ВЧ-наведення (TVI/RFI)\n3. Прийом завад опліткою", size=10, color=POS, fill="#ffffff", stroke=POS, min_w=150)[0])


    # Секція Права: Живлення із струмовим балуном (Гуанелла)
    p.append(rect(400, 15, 365, 350, fill="#f2fdf5", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(582, 38, "Зворотне живлення (Із Струмовим Балуном)", size=13, color=FIELD, bold=True))

    # Коаксіал праворуч
    p.append(rect(415, 180, 50, 24, fill="#e8ecef", stroke=INK, sw=1.5, rx=3))
    p.append(line(415, 192, 465, 192, color=POS, sw=2.0))

    # Балун (Феритовий дросель)
    p.append(rect(465, 168, 60, 48, fill="#d5dbdb", stroke=INK, sw=2.0, rx=4))
    p.append(text(495, 192, "Осердя\nZ_cm>>Z_0", size=9, color=INK, bold=True))

    p.append(rect(525, 180, 25, 24, fill="#e8ecef", stroke=INK, sw=1.5, rx=3))
    p.append(line(525, 192, 550, 192, color=POS, sw=2.0))

    # Диполь
    p.append(line(550, 115, 550, 192, color=POS, sw=3.0)) # Верхнє плече
    p.append(line(550, 192, 550, 245, color=NEG, sw=3.0)) # Нижнє плече
    p.append(text(550, 95, "+ Плече 1", size=10, color=POS, bold=True))
    p.append(text(550, 258, "− Плече 2", size=10, color=NEG, bold=True))

    # Струми
    p.append(arrow(420, 188, 455, 188, color=POS, sw=1.5))
    p.append(arrow(528, 188, 545, 188, color=POS, sw=1.5))
    p.append(text(495, 130, "I_1 = −I_2", size=10, color=FIELD, bold=True))

    # Блокування I_3
    p.append(line(465, 225, 420, 225, color=MUTED, sw=1.5, dash="3,3"))
    p.append(textbox(445, 310, "I_3 = 0\n(Заблоковано)", size=9, color=FIELD, fill="#ffffff", stroke=FIELD, min_w=90)[0])

    # Переваги
    p.append(textbox(665, 185, "Результат:\n1. Симетричні струми I_1 = −I_2\n2. Чітка симетрична ДН\n3. Немає ВЧ-наведень на кабель", size=10, color=FIELD, fill="#ffffff", stroke=FIELD, min_w=150)[0])

    save_svg("common-mode-current.svg", render(W, H, p))


# ── Фігура 2: Вольтний проти Струмового балуна ────────────────────────────────
def fig_voltage_vs_current_balun():
    W, H = 780, 380
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    # Ліва секція: Вольтний Балун (Voltage Balun)
    p.append(rect(15, 15, 365, 350, fill="#f9f9fb", stroke=NEG, sw=1.2, rx=8))
    p.append(text(197, 38, "Вольтний Балун (Voltage Balun)", size=13, color=NEG, bold=True))

    # Схема вольтного балуна (Автотрансформатор з відводом від землі)
    p.append(line(35, 190, 85, 190, color=INK, sw=1.5)) # Вхід
    p.append(circle(85, 190, 4, fill=INK, stroke=INK))
    p.append(textbox(60, 165, "Вхід 50 Ом", size=9, min_w=65)[0])

    # Котушки (Автотрансформатор)
    p.append(rect(115, 110, 30, 160, fill="#eaecee", stroke=INK, sw=1.5, rx=4))
    p.append(text(130, 190, "Ферит", size=9, color=MUTED))

    # Обмотки Ліві (Вхід і Земля)
    p.append(line(85, 190, 115, 130, color=POS, sw=2.0))
    p.append(line(85, 190, 115, 250, color=NEG, sw=2.0))

    # Земля в центрі
    p.append(line(85, 190, 85, 230, color=INK, sw=1.5))
    p.append(line(75, 230, 95, 230, color=INK, sw=2.0))
    p.append(line(80, 235, 90, 235, color=INK, sw=1.5))

    # Виходи
    p.append(line(145, 130, 195, 130, color=POS, sw=2.0))
    p.append(line(145, 250, 195, 250, color=NEG, sw=2.0))

    p.append(text(215, 125, "V_1 = +V_in / 2", size=9, color=POS, bold=True))
    p.append(text(215, 255, "V_2 = −V_in / 2", size=9, color=NEG, bold=True))

    # Навантаження з асиметрією
    p.append(rect(245, 110, 50, 160, fill="#ffffff", stroke=INK, sw=1.5, rx=3))
    p.append(text(270, 190, "Антена\n(Навант.)", size=9, color=INK))

    # Пояснення проблем
    p.append(textbox(197, 310, "Принцип: Фіксує напруги V_1 = −V_2\nПроблема: Якщо опір плечей до землі нерівний\n(C_1 ≠ C_2), струми I_1 ≠ I_2! Струм затікає!", size=10, color=NEG, fill="#ffffff", stroke=NEG, min_w=320)[0])


    # Права секція: Струмовий Балун (Current Balun / Guanella)
    p.append(rect(400, 15, 365, 350, fill="#f2fdf5", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(582, 38, "Струмовий Балун (Current Balun / Guanella)", size=13, color=FIELD, bold=True))

    # Схема струмового балуна (Двопровідна лінія на осерді)
    p.append(line(420, 140, 470, 140, color=POS, sw=2.0))
    p.append(line(420, 240, 470, 240, color=NEG, sw=2.0))
    p.append(textbox(445, 115, "Вхід 50 Ом", size=9, min_w=65)[0])

    # Феритове осердя
    p.append(rect(470, 120, 60, 140, fill="#d5dbdb", stroke=INK, sw=2.0, rx=4))
    p.append(text(500, 190, "Дросель\nZ_cm", size=10, color=INK, bold=True))

    # Виходи
    p.append(line(530, 140, 580, 140, color=POS, sw=2.0))
    p.append(line(530, 240, 580, 240, color=NEG, sw=2.0))

    # Струми
    p.append(arrow(535, 132, 570, 132, color=POS, sw=1.8))
    p.append(text(552, 122, "I_1", size=10, color=POS, bold=True))

    p.append(arrow(570, 248, 535, 248, color=NEG, sw=1.8))
    p.append(text(552, 262, "I_2", size=10, color=NEG, bold=True))

    # Навантаження
    p.append(rect(590, 120, 50, 140, fill="#ffffff", stroke=INK, sw=1.5, rx=3))
    p.append(text(615, 190, "Антена\n(Навант.)", size=9, color=INK))

    # Переваги
    p.append(textbox(582, 310, "Принцип: Високий опір Z_cm примушує I_1 = −I_2\nПеревага: При будь-якій асиметрії антени\nструм затікання пригнічено на 30–50 дБ!", size=10, color=FIELD, fill="#ffffff", stroke=FIELD, min_w=320)[0])

    save_svg("voltage-vs-current-balun.svg", render(W, H, p))


# ── Фігура 3: Топології 4:1 Рутрофа та Гуанелла ───────────────────────────────
def fig_guanella_ruthroff_4to1():
    W, H = 780, 380
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    # Секція 1: Автотрансформатор Рутрофа 4:1 (Вольтний)
    p.append(rect(15, 15, 365, 350, fill="#f9f9fb", stroke=INK, sw=1.2, rx=8))
    p.append(text(197, 38, "Вольтний Балун Рутрофа 4:1", size=13, color=INK, bold=True))

    p.append(textbox(197, 75, "Трансформація 50 Ом → 200 Ом\n(Паралельний вхід / Послідовний вихід)", size=10, min_w=240)[0])

    # Топологічна схема Рутрофа
    p.append(line(35, 160, 85, 160, color=POS, sw=2.0))
    p.append(text(60, 145, "50 Ом In", size=9, color=POS, bold=True))

    # Осердя з обмоткою
    p.append(rect(85, 130, 80, 100, fill="#eaecee", stroke=INK, sw=1.5, rx=4))
    p.append(text(125, 180, "Ферит 1:1\nАвтотр-р", size=9, color=MUTED))

    # Вихід
    p.append(line(165, 150, 235, 150, color=POS, sw=2.0))
    p.append(line(165, 210, 235, 210, color=NEG, sw=2.0))

    p.append(textbox(280, 180, "Вихід\n200 Ом\n(Balanced)", size=9, color=POS, fill="#ffffff", stroke=POS, min_w=75)[0])

    p.append(textbox(197, 295, "Особливості Рутрофа 4:1:\n• Один феритовий тороїд\n• Чутливий до асиметрії навантаження\n• Обмежена смуга частот зверху", size=10, color=INK, fill="#ffffff", stroke=INK, min_w=310)[0])


    # Секція 2: Струмовий Балун Гуанелла 4:1 (ШПТЛ)
    p.append(rect(400, 15, 365, 350, fill="#f2fdf5", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(582, 38, "Струмовий Балун Гуанелла 4:1", size=13, color=FIELD, bold=True))

    p.append(textbox(582, 75, "Дві лінії 100 Ом: Паралельно на вході (50 Ом),\nПослідовно на виході (200 Ом)", size=10, color=FIELD, min_w=280)[0])

    # Дві лінії Гуанелла
    p.append(rect(470, 120, 70, 45, fill="#d5dbdb", stroke=INK, sw=1.5, rx=3))
    p.append(text(505, 142, "Лінія 1 (100 Ом)", size=9, color=INK, bold=True))

    p.append(rect(470, 185, 70, 45, fill="#d5dbdb", stroke=INK, sw=1.5, rx=3))
    p.append(text(505, 207, "Лінія 2 (100 Ом)", size=9, color=INK, bold=True))

    # З'єднання вхід паралельно (50 Ом)
    p.append(line(435, 142, 470, 142, color=POS, sw=2.0))
    p.append(line(435, 207, 470, 207, color=POS, sw=2.0))
    p.append(line(435, 142, 435, 207, color=POS, sw=2.0))
    p.append(line(410, 175, 435, 175, color=POS, sw=2.0))
    p.append(text(420, 160, "50 Ом In", size=9, color=POS, bold=True))

    # З'єднання вихід послідовно (200 Ом)
    p.append(line(540, 130, 615, 130, color=POS, sw=2.0)) # Вихід 1
    p.append(line(540, 155, 565, 155, color=MUTED, sw=1.5)) # Середина
    p.append(line(565, 155, 565, 195, color=MUTED, sw=1.5))
    p.append(line(565, 195, 540, 195, color=MUTED, sw=1.5))
    p.append(line(540, 220, 615, 220, color=NEG, sw=2.0)) # Вихід 2

    p.append(textbox(660, 175, "Вихід\n200 Ом\n(Balanced)", size=9, color=FIELD, fill="#ffffff", stroke=FIELD, min_w=75)[0])

    p.append(textbox(582, 295, "Переваги Гуанелла 4:1:\n• Ідеальне симетрування струмів (Current Balun)\n• Наднадширока смуга (1–500 МГц)\n• Високий ККД (> 98%), низькі втрати у фериті", size=10, color=FIELD, fill="#ffffff", stroke=FIELD, min_w=310)[0])

    save_svg("guanella-ruthroff-4to1.svg", render(W, H, p))


# ── Фігура 4: Розподілені балуни: Базука та Маршан ────────────────────────────
def fig_marchand_sleeve_topologies():
    W, H = 780, 360
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    # Ліва секція: Рукавний Балун "Базука" (Sleeve Balun λ/4)
    p.append(rect(15, 15, 365, 330, fill="#fdfefe", stroke=INK, sw=1.2, rx=8))
    p.append(text(197, 38, "Рукавний Балун Базука (Sleeve λ/4)", size=13, color=INK, bold=True))

    # Схема Базуки
    p.append(line(35, 180, 220, 180, color=POS, sw=2.0)) # Центральна жила
    p.append(rect(35, 168, 185, 24, fill="#e8ecef", stroke=INK, sw=1.5, rx=2)) # Оплітка кабелю

    # Металевий рукав λ/4 поверх кабелю
    p.append(rect(95, 155, 125, 50, fill="none", stroke=POS, sw=2.5, rx=3))
    p.append(text(157, 140, "Металевий рукав L = λ/4", size=10, color=POS, bold=True))

    # Коротке замикання знизу
    p.append(line(95, 155, 95, 205, color=POS, sw=3.0))
    p.append(text(95, 220, "КЗ з опліткою", size=9, color=MUTED, anchor="middle"))

    # Вихід на диполь
    p.append(line(220, 120, 220, 180, color=POS, sw=3.0))
    p.append(line(220, 180, 220, 240, color=NEG, sw=3.0))

    p.append(textbox(197, 290, "Принцип: Короткозамкнений шлейф λ/4 дає Z_cm → ∞\nЗастосування: УВЧ/ВЧ, вузькосмугові системи", size=10, color=INK, fill="#ffffff", stroke=INK, min_w=310)[0])


    # Права секція: Планарний Балун Маршана (Marchand Balun на PCB/LTCC)
    p.append(rect(400, 15, 365, 330, fill="#f5f8ff", stroke=NEG, sw=1.5, rx=8))
    p.append(text(582, 38, "Планарний Балун Маршана (Marchand)", size=13, color=NEG, bold=True))

    # Вхід
    p.append(line(415, 180, 460, 180, color=POS, sw=2.0))
    p.append(text(435, 165, "In 50 Ом", size=9, color=POS, bold=True))

    # Зв'язані лінії λ/4 (Смужкові доріжки)
    p.append(rect(460, 140, 85, 20, fill="#d4efdf", stroke=FIELD, sw=1.5, rx=2))
    p.append(text(502, 153, "Смужкова лінія 1", size=9, color=FIELD, bold=True))

    p.append(rect(460, 200, 85, 20, fill="#d4efdf", stroke=FIELD, sw=1.5, rx=2))
    p.append(text(502, 213, "Смужкова лінія 2", size=9, color=FIELD, bold=True))

    # Зв'язані вторинні лінії
    p.append(rect(560, 140, 85, 20, fill="#d6eaf8", stroke=NEG, sw=1.5, rx=2))
    p.append(text(602, 153, "Вторинна λ/4", size=9, color=NEG, bold=True))

    p.append(rect(560, 200, 85, 20, fill="#d6eaf8", stroke=NEG, sw=1.5, rx=2))
    p.append(text(602, 213, "Вторинна λ/4", size=9, color=NEG, bold=True))

    # Виходи
    p.append(line(645, 150, 680, 150, color=POS, sw=2.0))
    p.append(line(645, 210, 680, 210, color=NEG, sw=2.0))

    p.append(text(715, 145, "Out + (0°)", size=9, color=POS, bold=True))
    p.append(text(715, 215, "Out − (180°)", size=9, color=NEG, bold=True))

    p.append(textbox(582, 290, "Принцип: Зв'язані смужкові лінії λ/4 на PCB\nЗастосування: Смартфони, Wi-Fi, мікросхеми RFIC/MMIC\nСмуга: Широка (від десятків % до октави)", size=10, color=NEG, fill="#ffffff", stroke=NEG, min_w=310)[0])

    save_svg("marchand-sleeve-topologies.svg", render(W, H, p))


if __name__ == "__main__":
    fig_common_mode_current()
    fig_voltage_vs_current_balun()
    fig_guanella_ruthroff_4to1()
    fig_marchand_sleeve_topologies()
    print("Усі фігури згенеровано успішно.")
