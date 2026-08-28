# -*- coding: utf-8 -*-
"""Фігури для теми moisture-sensitivity-levels:
1. img/popcorn-delamination-cross-section.svg — анатомія розшарування та ефекту попкорну в корпусі ІМС.
2. img/msl-baking-recovery-curves.svg — кінетика десорбції вологи при сушінні (125°C, 90°C, 40°C) та правило відновлення 5x."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова гама
MOLD_BODY     = "#334155"  # Епоксидний компаунд (EMC)
SILICON_DIE   = "#64748b"  # Кремнієвий кристал
COPPER_LEAD   = "#d97706"  # Мідна рамка виводів / Die paddle
GOLD_WIRE     = "#eab308"  # Золоті розварювальні дротики
DELAM_RED     = "#ef4444"  # Зона розшарування / тиск пари
PCB_SUBSTRATE = "#059669"  # Плата FR-4
SOLDER_BALL   = "#94a3b8"  # Паяні виводи / кульки BGA
TEXT_DARK     = "#0f172a"
TEXT_MUTED    = "#475569"


def fig_popcorn_cross_section():
    W, H = 840, 420
    frags = []

    # Тло блоку та рамка
    frags.append(rect(15, 15, 810, 390, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))

    # Заголовок фігури
    frags.append(text(420, 38, "Фізика ефекту попкорну: розшарування корпусу ІМС при 260 °C", size=14, color=TEXT_DARK, bold=True))

    # Корпус компаунда (Epoxy Molding Compound) - x: 80..500
    frags.append(rect(80, 95, 420, 190, fill="#f1f5f9", stroke=MOLD_BODY, sw=2, rx=4))
    frags.append(text(175, 115, "Епоксидний компаунд (EMC)", size=11, color=TEXT_MUTED, bold=True))

    # Зовнішні виводи рамки (Leadframe fingers) зліва (x: 20..80) та справа (x: 500..560)
    frags.append(rect(20, 180, 60, 14, fill="#fed7aa", stroke=COPPER_LEAD, sw=1.5, rx=2))
    frags.append(rect(500, 180, 60, 14, fill="#fed7aa", stroke=COPPER_LEAD, sw=1.5, rx=2))
    frags.append(text(50, 172, "Вивід", size=10, color=TEXT_MUTED))
    frags.append(text(530, 172, "Вивід", size=10, color=TEXT_MUTED))

    # Внутрішні контактні площадки виводів всередині компаунда
    frags.append(rect(90, 180, 30, 14, fill="#fed7aa", stroke=COPPER_LEAD, sw=1.5, rx=2))
    frags.append(rect(460, 180, 30, 14, fill="#fed7aa", stroke=COPPER_LEAD, sw=1.5, rx=2))

    # Мідна основа кристала (Die Paddle / Flag)
    frags.append(rect(150, 220, 280, 16, fill="#fed7aa", stroke=COPPER_LEAD, sw=1.5, rx=2))
    frags.append(text(290, 232, "Мідна підкладка кристала (Die Paddle)", size=10, color="#7c2d12", bold=True))

    # Клейовий шар (Die Attach)
    frags.append(rect(180, 212, 220, 8, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=1))

    # Кремнієвий кристал (Silicon Die)
    frags.append(rect(180, 155, 220, 57, fill="#cbd5e1", stroke=SILICON_DIE, sw=1.5, rx=2))
    frags.append(text(290, 185, "Кремнієвий кристал (Silicon Die)", size=11, color=TEXT_DARK, bold=True))

    # Дротяні розварки (Bond wires) - золоті дуги
    # Ліва розварка: від кристала (200, 155) до внутрішнього контакту (105, 180)
    frags.append('<path d="M 200 155 Q 140 120 105 180" fill="none" stroke="%s" stroke-width="2.5" />' % GOLD_WIRE)
    # Права розварка (зірвана через розрив): від кристала (380, 155) розрив
    frags.append('<path d="M 380 155 Q 425 125 455 145" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="3,3" />' % GOLD_WIRE)
    frags.append(text(450, 135, "Зрив зварки!", size=10, color=POS, bold=True))

    # Зона вибухового розшарування (Delamination cavity / Steam bubble) під die paddle
    frags.append(rect(160, 236, 260, 22, fill="#fee2e2", stroke=DELAM_RED, sw=2, rx=6))
    frags.append(text(290, 251, "Тиск пари P > 4.7 МПа (47 атм) при 260 °C", size=10, color=POS, bold=True))

    # Тріщина в компаунді (Crack venting to surface)
    frags.append('<path d="M 420 245 L 460 260 L 495 280" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % POS)
    frags.append(text(505, 295, "Тріщина компаунда", size=10, color=POS, bold=True, anchor="start"))
    frags.append(text(505, 308, "(вихід пари назовні)", size=9, color=POS, anchor="start"))

    # Тріщина кристала (Die crack)
    frags.append('<path d="M 330 212 L 350 180 L 340 155" fill="none" stroke="%s" stroke-width="2" />' % POS)
    frags.append(text(340, 145, "Тріщина кристала", size=9, color=POS, bold=True))

    # Пояснювальний блок праворуч: стадії процесу
    frags.append(rect(575, 75, 235, 315, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(692, 98, "Послідовність руйнування", size=12, color=TEXT_DARK, bold=True))

    steps = [
        ("1. Дифузія вологи:", True),
        ("Поглинання H2O компаундом", False),
        ("під час зберігання у цеху.", False),
        ("", False),
        ("2. Нагрів у печі (до 260 °C):", True),
        ("Волога миттєво закипає,", False),
        ("P_sat зростає до 4.7+ МПа.", False),
        ("", False),
        ("3. Відшарування (Delam):", True),
        ("Пара відриває компаунд від", False),
        ("мідного флага кристала.", False),
        ("", False),
        ("4. Вибух (Popcorn):", True),
        ("Купол розриває компаунд,", False),
        ("рве розварки та кремній.", False)
    ]
    for idx, (st, is_h) in enumerate(steps):
        if not st:
            continue
        col = POS if is_h else TEXT_MUTED
        sz = 10 if is_h else 9
        frags.append(text(585, 120 + idx * 16, st, size=sz, color=col, anchor="start", bold=is_h))

    # Нижній блок підписів для шарів
    b1, _, _ = textbox(190, 345, ["Волога накопичується на гідрофільних", "межах метал-полімер і Si-полімер"], size=9, pad=6, fill="#ffffff", stroke="#cbd5e1")
    frags.append(b1)
    frags.append(arrow(190, 320, 230, 260, color=TEXT_MUTED, sw=1.2))

    b2, _, _ = textbox(410, 355, ["Критичне зниження адгезії", "при T > Tg компаунда (150 °C)"], size=9, pad=6, fill="#ffffff", stroke="#cbd5e1")
    frags.append(b2)
    frags.append(arrow(410, 332, 360, 260, color=TEXT_MUTED, sw=1.2))

    render(os.path.join(OUT, "popcorn-delamination-cross-section.svg"), W, H, *frags)


def fig_msl_baking_recovery():
    W, H = 840, 420
    frags = []

    frags.append(rect(15, 15, 810, 390, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(420, 38, "Кінетика сушіння (Baking) та правило відновлення Floor Life", size=14, color=TEXT_DARK, bold=True))

    # Лівий графік: Криві десорбції вологи C(t) при різних температурах
    frags.append(rect(30, 65, 380, 325, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6))
    frags.append(text(220, 88, "Десорбція вологи з корпусу (t = 1.4 мм)", size=11, color=TEXT_DARK, bold=True))

    # Осі лівого графіка
    ox, oy = 75, 330
    gw, gh = 310, 210
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))
    frags.append(text(ox + gw - 15, oy + 22, "Час сушіння", size=9, color=TEXT_MUTED, bold=True))
    frags.append(text(ox - 8, oy - gh + 10, "C(H2O), %", size=9, color=TEXT_MUTED, bold=True, anchor="end"))

    # Позначки осі Y
    frags.append(text(ox - 6, oy - 180, "0.4%", size=9, color=TEXT_MUTED, anchor="end"))
    frags.append(text(ox - 6, oy - 90, "0.2%", size=9, color=TEXT_MUTED, anchor="end"))
    frags.append(text(ox - 6, oy - 45, "0.1%", size=9, color=POS, anchor="end", bold=True))
    frags.append(line(ox, oy - 45, ox + gw, oy - 45, color="#fca5a5", sw=1, dash="4,4"))
    frags.append(text(ox + gw - 10, oy - 50, "C_crit (безпечний поріг)", size=9, color=POS, anchor="end", bold=True))

    # Крива 125 °C (швидка експонента: 8-24 год)
    frags.append('<path d="M 75 150 Q 105 270 140 285 T 200 290" fill="none" stroke="#dc2626" stroke-width="2.5"/>')
    frags.append(text(145, 260, "125 °C (8–24 год)", size=9, color="#dc2626", bold=True))

    # Крива 90 °C (середня: 24–72 год)
    frags.append('<path d="M 75 150 Q 135 230 220 285 T 320 290" fill="none" stroke="#d97706" stroke-width="2.2"/>')
    frags.append(text(230, 240, "90 °C (2–3 доби)", size=9, color="#d97706", bold=True))

    # Крива 40 °C (низькотемпературна у стрічці: 8–15 діб)
    frags.append('<path d="M 75 150 Q 175 190 280 240 T 375 285" fill="none" stroke="#2563eb" stroke-width="2.2"/>')
    frags.append(text(315, 215, "40 °C (8–15 діб)", size=9, color="#2563eb", bold=True))

    frags.append(text(220, 370, "125 °C — для термостійких лотків (JEDEC Tray)", size=9, color=TEXT_MUTED))

    # Правий блок: Суха шафа (<5% RH) та правило відновлення 5x
    frags.append(rect(425, 65, 385, 325, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6))
    frags.append(text(615, 88, "Зберігання у сухій шафі та правило 5x", size=11, color=TEXT_DARK, bold=True))

    # Діаграма станів / часова шкала
    # Блок 1: Експозиція на лінії
    frags.append(rect(440, 115, 150, 50, fill="#fee2e2", stroke="#f87171", sw=1.2, rx=4))
    frags.append(text(515, 135, "Експозиція в цеху", size=10, color=POS, bold=True))
    frags.append(text(515, 152, "t_exp ≤ 12 год", size=9, color=TEXT_MUTED))

    # Стрілка переходу
    frags.append(arrow(595, 140, 635, 140, color=TEXT_DARK, sw=1.5))

    # Блок 2: Суха шафа
    frags.append(rect(640, 115, 155, 50, fill="#eff6ff", stroke="#60a5fa", sw=1.2, rx=4))
    frags.append(text(717, 135, "Суха шафа RH < 5%", size=10, color="#1d4ed8", bold=True))
    frags.append(text(717, 152, "t_dry = 5 × t_exp", size=9, color=TEXT_MUTED))

    # Результат: Повне відновлення Floor Life
    frags.append(rect(440, 185, 355, 45, fill="#f0fdf4", stroke="#4ade80", sw=1.2, rx=4))
    frags.append(text(617, 205, "Повний скид лічильника: Floor Life = 100%", size=10, color="#15803d", bold=True))
    frags.append(text(617, 220, "без теплового навантаження та окиснення виводів", size=9, color="#166534"))

    # Порівняльна таблиця обмежень
    frags.append(rect(440, 245, 355, 130, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(617, 265, "Технологічні обмеження сушіння", size=10, color=TEXT_DARK, bold=True))

    rules = [
        ("• Стрічка на котушці (Tape & Reel):", "лише 40 °C (пластик плавиться при >55 °C)"),
        ("• Сумарне сушіння при 125 °C:", "макс. 96 год (ріст інтерметалідів)"),
        ("• Суха шафа RH < 10%:", "зупиняє лічильник, але НЕ скидає (пауза)"),
        ("• Суха шафа RH < 5%:", "скидає лічильник за правилом 5x часу")
    ]
    for i, (r_title, r_desc) in enumerate(rules):
        frags.append(text(448, 288 + i * 20, r_title, size=9, color=TEXT_DARK, anchor="start", bold=True))
        frags.append(text(618, 288 + i * 20, r_desc, size=9, color=TEXT_MUTED, anchor="start"))

    render(os.path.join(OUT, "msl-baking-recovery-curves.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_popcorn_cross_section()
    fig_msl_baking_recovery()
    print("OK: generated figures for moisture-sensitivity-levels")
