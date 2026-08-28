# -*- coding: utf-8 -*-
"""Генератор фігур для теми polityka-onovlen."""

import os
import sys

# Шлях до svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    BG,
    FIELD,
    FILL,
    FONT,
    INK,
    LINE,
    MUTED,
    NEG,
    POS,
    arrow,
    circle,
    esc,
    fitbox,
    line,
    mtext,
    rect,
    render,
    text,
    textbox,
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_patch_classification():
    """Фігура 1: Класифікація патчів за рівнем терміновості та глибиною валідації."""
    w, h = 860, 420
    frags = []

    # Заголовок зверху
    frags.append(text(430, 30, "Класифікація оновлень прошивки за рівнем ризику та терміновістю", size=16, bold=True))

    # Стовпчик 1: Emergency Security (Zero-Day)
    frags.append(rect(30, 60, 250, 330, fill="#fdf2f2", stroke=POS, sw=2, rx=8))
    frags.append(text(155, 90, "Критична безпека (Zero-Day)", size=14, color=POS, bold=True))
    frags.append(line(45, 105, 265, 105, color=POS, sw=1, dash="4,3"))
    
    frags.append(text(45, 130, "Критерій: CVSS ≥ 9.0, активний експлойт", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(45, 155, "Час випуску: 24–72 години", size=11, color=INK, anchor="start"))
    frags.append(text(45, 180, "Тестування: Smoke-тести + цільовий регрес", size=11, color=INK, anchor="start"))
    frags.append(text(45, 205, "Канал: Екстрений обхід звичайної черги", size=11, color=INK, anchor="start"))
    frags.append(text(45, 230, "Вікно: Примусове переривання роботи", size=11, color=INK, anchor="start"))
    frags.append(text(45, 255, "Вимоги до АКБ: Знижений поріг (> 30%)", size=11, color=INK, anchor="start"))
    frags.append(text(45, 280, "Згода користувача: Автоматично / Overrule", size=11, color=INK, anchor="start"))
    
    frags.append(rect(45, 305, 220, 65, fill="#ffffff", stroke=POS, sw=1, rx=4))
    frags.append(mtext(155, 325, ["Головна мета:", "Запобігти масовій компрометації", "та проникненню в мережу"], size=11, color=POS, bold=True))

    # Стовпчик 2: Maintenance (Планові виправлення)
    frags.append(rect(305, 60, 250, 330, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    frags.append(text(430, 90, "Технічне обслуговування (Bugfix)", size=14, color=NEG, bold=True))
    frags.append(line(320, 105, 540, 105, color=NEG, sw=1, dash="4,3"))
    
    frags.append(text(320, 130, "Критерій: Помилки логіки, витоки, стабільність", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(320, 155, "Час випуску: Плановий спринт (2–4 тижні)", size=11, color=INK, anchor="start"))
    frags.append(text(320, 180, "Тестування: Повний HIL + регресійний набір", size=11, color=INK, anchor="start"))
    frags.append(text(320, 205, "Канал: Стабільний плановий реліз", size=11, color=INK, anchor="start"))
    frags.append(text(320, 230, "Вікно: Суворо у регламентний час простою", size=11, color=INK, anchor="start"))
    frags.append(text(320, 255, "Вимоги до АКБ: Стандартний поріг (> 50%)", size=11, color=INK, anchor="start"))
    frags.append(text(320, 280, "Згода користувача: Відтермінування до 3 разів", size=11, color=INK, anchor="start"))
    
    frags.append(rect(320, 305, 220, 65, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    frags.append(mtext(430, 325, ["Головна мета:", "Підвищення MTBF та усунення", "накопиченого технічного боргу"], size=11, color=NEG, bold=True))

    # Стовпчик 3: Feature Upgrade (Функціональні зміни)
    frags.append(rect(580, 60, 250, 330, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(705, 90, "Функціональний реліз (Feature)", size=14, color=FIELD, bold=True))
    frags.append(line(595, 105, 815, 105, color=FIELD, sw=1, dash="4,3"))
    
    frags.append(text(595, 130, "Критерій: Новий функціонал, зміна протоколів", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(595, 155, "Час випуску: Квартальний / сезонний реліз", size=11, color=INK, anchor="start"))
    frags.append(text(595, 180, "Тестування: HIL + Польові випробування (Beta)", size=11, color=INK, anchor="start"))
    frags.append(text(595, 205, "Канал: Canary Ring -> Staged rollout", size=11, color=INK, anchor="start"))
    frags.append(text(595, 230, "Вікно: Лише за повної зупинки технології", size=11, color=INK, anchor="start"))
    frags.append(text(595, 255, "Вимоги до АКБ: Суворий поріг (> 70% / AC)", size=11, color=INK, anchor="start"))
    frags.append(text(595, 280, "Згода користувача: Обов'язкове підтвердження", size=11, color=INK, anchor="start"))
    
    frags.append(rect(595, 305, 220, 65, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    frags.append(mtext(705, 325, ["Головна мета:", "Розширення можливостей пристрою", "без ризику для поточних бізнес-процесів"], size=11, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "patch-classification.svg"), w, h, *frags)


def fig_release_governance_raci():
    """Фігура 2: Розподіл відповідальності та матриця ухвалення рішень."""
    w, h = 860, 360
    frags = []

    frags.append(text(430, 25, "Матриця відповідальності та контрольні шлюзи ухвалення рішень (Governance)", size=15, bold=True))

    # 4 ролі (колонки)
    roles = [
        ("Безпека (PSIRT)", "Оцінка CVSS, вето на випуск, аудит криптопідпису", POS, 120),
        ("Розробка (FW Lead)", "Стабільність коду, валідація на HIL, міграція NVS", NEG, 330),
        ("Оператор парку (Ops)", "Графік вікон, моніторинг хвиль, контроль трафіку", FIELD, 540),
        ("Агент вузла (Device)", "Локальне вето (АКБ, навантаження, аварійний стан)", INK, 740)
    ]

    for title, desc, col, cx in roles:
        frags.append(rect(cx - 95, 55, 190, 80, fill=FILL, stroke=col, sw=2, rx=6))
        frags.append(text(cx, 80, title, size=13, color=col, bold=True))
        frags.append(fitbox(cx - 85, 95, 170, 32, desc, size=10, pad=2, fill="none", stroke="none", color=MUTED))

    # Етапи ухвалення рішення (рядки)
    stages = [
        ("1. Оцінка інциденту / потреби", "A (Accountable)", "C (Consulted)", "I (Informed)", "—"),
        ("2. Збірка та верифікація бінарника", "C (Consulted)", "A (Accountable)", "I (Informed)", "—"),
        ("3. Формування кампанії та когорт", "C (Consulted)", "R (Responsible)", "A (Accountable)", "—"),
        ("4. Фінальний допуск до виконання", "I (Informed)", "I (Informed)", "R (Responsible)", "A (Final Veto)")
    ]

    y_start = 160
    for i, (stage, r1, r2, r3, r4) in enumerate(stages):
        y = y_start + i * 45
        frags.append(rect(25, y, 810, 38, fill="#ffffff" if i % 2 == 0 else "#f8fafc", stroke=LINE, sw=0.8, rx=4))
        frags.append(text(35, y + 23, stage, size=12, color=INK, anchor="start", bold=True))
        
        frags.append(text(120, y + 23, r1, size=11, color=POS if "A" in r1 else INK, bold="A" in r1))
        frags.append(text(330, y + 23, r2, size=11, color=NEG if "A" in r2 else INK, bold="A" in r2))
        frags.append(text(540, y + 23, r3, size=11, color=FIELD if "A" in r3 else INK, bold="A" in r3))
        frags.append(text(740, y + 23, r4, size=11, color=POS if "Veto" in r4 else INK, bold="Veto" in r4))

    render(os.path.join(IMG_DIR, "release-governance-raci.svg"), w, h, *frags)


def fig_fleet_rollout_rings():
    """Фігура 3: Хвилі розгортання та автоматичні аварійні зупинки (Circuit Breaker)."""
    w, h = 860, 380
    frags = []

    frags.append(text(430, 25, "Канарейкове розгортання прошивки за кільцями довіри з автоматичними гальмами", size=15, bold=True))

    rings = [
        ("Кільце 0: Лабораторія", "Внутрішні стенди (HIL)\nТестові екземпляри\nN = 10..50 пристроїв", 100),
        ("Кільце 1: Канарейка", "Дружні користувачі\nКонтрольоване середовище\nЧастка: 1% (N ≈ 500)", 320),
        ("Кільце 2: Проміжне", "Регіональні сегменти\nРізні ревізії заліза\nЧастка: 10% (N ≈ 5 000)", 540),
        ("Кільце 3: Весь парк", "Масове виробництво\nЗагальний розсип\nЧастка: 100% (N = 50 000)", 750),
    ]

    for title, desc, cx in rings:
        frags.append(rect(cx - 95, 60, 190, 110, fill=FILL, stroke=LINE, sw=1.5, rx=6))
        frags.append(text(cx, 85, title, size=12, bold=True, color=INK))
        frags.append(line(cx - 85, 95, cx + 85, 95, color=MUTED, sw=0.8))
        frags.append(mtext(cx, 115, desc, size=10, color=MUTED, lh=1.3))

    # Стрілки переходу між кільцями
    frags.append(arrow(195, 115, 225, 115, color=LINE, sw=2))
    frags.append(arrow(415, 115, 445, 115, color=LINE, sw=2))
    frags.append(arrow(635, 115, 665, 115, color=LINE, sw=2))

    # Блок витримки (Bake time) та критеріїв зупинки під кожним переходом
    frags.append(rect(30, 200, 800, 150, fill="#fffbf0", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(430, 225, "Автоматичні аварійні бар'єри (Automated Circuit Breakers & Rollback Triggers)", size=13, color="#b45309", bold=True))

    frags.append(rect(50, 245, 230, 90, fill="#ffffff", stroke="#d97706", sw=1, rx=4))
    frags.append(text(165, 265, "Період витримки (Bake)", size=11, bold=True, color=INK))
    frags.append(mtext(165, 285, ["Кільце 1: пауза 48-72 год", "Кільце 2: пауза 7 днів", "Збір метрик стабільності"], size=10, color=MUTED))

    frags.append(rect(315, 245, 230, 90, fill="#ffffff", stroke=POS, sw=1, rx=4))
    frags.append(text(430, 265, "Поріг відкату (Rollback)", size=11, bold=True, color=POS))
    frags.append(mtext(430, 285, ["Помилки OTA > 0.5%", "Watchdog рестарти > +10%", "Втрата зв'язку > 1%"], size=10, color=POS))

    frags.append(rect(580, 245, 230, 90, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    frags.append(text(695, 265, "Дія при порушенні", size=11, bold=True, color=FIELD))
    frags.append(mtext(695, 285, ["1. Миттєва зупинка черги", "2. A/B відкат збійних вузлів", "3. Сповіщення інженера"], size=10, color=FIELD))

    render(os.path.join(IMG_DIR, "fleet-rollout-rings.svg"), w, h, *frags)


def fig_maintenance_window_decision():
    """Фігура 4: Логіка оцінки умов та вікна оновлення на боці кінцевого пристрою."""
    w, h = 860, 400
    frags = []

    frags.append(text(430, 25, "Логічний автомат перевірки умов оновлення на боці вбудованого вузла", size=15, bold=True))

    # Блок 1: Отримання маніфесту
    frags.append(rect(30, 60, 160, 60, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(mtext(110, 85, ["Отримання маніфесту", "оновлення від хмари"], size=11, bold=True))

    frags.append(arrow(190, 90, 230, 90, color=LINE, sw=1.5))

    # Блок 2: Перевірка підпису та сумісності
    frags.append(rect(230, 60, 180, 60, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(mtext(320, 85, ["1. Перевірка Ed25519", "та ревізії плати (HW ID)"], size=11, bold=True))

    frags.append(arrow(410, 90, 450, 90, color=LINE, sw=1.5))

    # Блок 3: Перевірка рівня важливості (Emergency override?)
    frags.append(rect(450, 50, 180, 80, fill="#fdf2f2", stroke=POS, sw=1.8, rx=6))
    frags.append(mtext(540, 80, ["2. Рівень важливості:", "Критичний Zero-Day?"], size=11, color=POS, bold=True))

    # Гілка ТАК (Zero-Day)
    frags.append(arrow(630, 90, 670, 90, color=POS, sw=1.8))
    frags.append(text(650, 80, "ТАК", size=10, color=POS, bold=True))
    frags.append(rect(670, 60, 160, 60, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(mtext(750, 85, ["Екстрене застосування", "негайно (АКБ > 30%)"], size=11, color=POS, bold=True))

    # Гілка НІ (Стандартний патч)
    frags.append(arrow(540, 130, 540, 180, color=LINE, sw=1.5))
    frags.append(text(555, 155, "НІ", size=10, color=LINE, bold=True))

    # Блок 4: Перевірка операційного стану та вікна
    frags.append(rect(430, 180, 220, 80, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(mtext(540, 205, ["3. Оцінка вікна простою:", "• Техпроцес зупинено?", "• Нічний графік (02:00-04:00)?"], size=11, color=NEG, bold=True))

    # Гілка відкладення (Postpone)
    frags.append(arrow(430, 220, 350, 220, color="#d97706", sw=1.5))
    frags.append(text(390, 210, "НІ", size=10, color="#d97706", bold=True))
    frags.append(rect(190, 190, 160, 60, fill="#fffbf0", stroke="#d97706", sw=1.5, rx=6))
    frags.append(mtext(270, 215, ["POSTPONE (BUSY):", "Спроба через 1 год"], size=11, color="#b45309", bold=True))

    # Гілка ТАК (Вікно підходить)
    frags.append(arrow(540, 260, 540, 300, color=FIELD, sw=1.5))
    frags.append(text(555, 280, "ТАК", size=10, color=FIELD, bold=True))

    # Блок 5: Фінальний тест апаратних ресурсів
    frags.append(rect(410, 300, 260, 80, fill="#f0fdf4", stroke=FIELD, sw=2, rx=6))
    frags.append(mtext(540, 325, ["4. Апаратний чек-лист:", "• Заряд АКБ ≥ 50% (або AC)", "• Температура -10..+55 °C", "• Достатньо місця на Flash"], size=11, color=FIELD, bold=True))

    frags.append(arrow(670, 340, 710, 340, color=FIELD, sw=2))
    frags.append(rect(710, 310, 130, 60, fill="#f0fdf4", stroke=FIELD, sw=2, rx=6))
    frags.append(mtext(775, 335, ["Встановлення", "в A/B слот"], size=12, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "maintenance-window-decision.svg"), w, h, *frags)


def main():
    fig_patch_classification()
    fig_release_governance_raci()
    fig_fleet_rollout_rings()
    fig_maintenance_window_decision()
    print("Всі 4 фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
