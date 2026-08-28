# -*- coding: utf-8 -*-
import os
import sys

# Додаємо шлях до спільного модуля svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, rect, line, arrow, text, mtext, textbox, fitbox, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_warranty_decision_tree():
    """Дерево рішень діагностики RMA: розмежування виробничих дефектів та анулювання гарантії."""
    w, h = 960, 580
    frags = []

    # Заголовок
    frags.append(text(w / 2, 26, "Дерево рішень сервісної RMA-діагностики та оцінки гарантійного статусу", size=15, bold=True))

    # Рівень 0: Вхідний пристрій
    frags.append(fitbox(w / 2 - 140, 48, 280, 42, "Повернення RMA: Вхідний екземпляр\n(Фізичний огляд і зчитування EEPROM)", size=12, pad=4, fill="#f4f8fe", stroke=NEG, bold=True))

    # Стрілка вниз до першого вузла
    frags.append(arrow(w / 2, 90, w / 2, 118, color=LINE, sw=1.8))

    # Рівень 1: Перевірка гарантійного терміну
    frags.append(fitbox(w / 2 - 160, 118, 320, 44, "1. Перевірка строку придатності\n(Календарний термін & Лічильник мотогодин)", size=11, pad=4, fill="#f4f6f8", stroke=LINE, bold=True))

    # Гілка 1: Вичерпано термін
    frags.append(arrow(w / 2 + 160, 140, 780, 140, color=POS, sw=1.8))
    frags.append(text(670, 132, "Вичерпано", size=10, color=POS, bold=True))
    frags.append(fitbox(700, 155, 230, 48, "ВІДХИЛЕНО: Вичерпано термін\n(Платне сервісне обслуговування)", size=11, pad=4, fill="#fef6f5", stroke=POS, bold=True))
    frags.append(line(780, 140, 780, 155, color=POS, sw=1.8))

    # Стрілка вниз до Рівня 2
    frags.append(arrow(w / 2, 162, w / 2, 195, color=FIELD, sw=1.8))
    frags.append(text(w / 2 + 35, 182, "Чинний", size=10, color=FIELD, bold=True))

    # Рівень 2: Перевірка несанкціонованого втручання
    frags.append(fitbox(w / 2 - 170, 195, 340, 44, "2. Перевірка цілісності та втручання\n(Апаратний Tamper-loop, зламані пломби, JTAG)", size=11, pad=4, fill="#f4f6f8", stroke=LINE, bold=True))

    # Гілка 2: Виявлено втручання
    frags.append(arrow(w / 2 - 170, 217, 160, 217, color=POS, sw=1.8))
    frags.append(text(270, 209, "Злам / Модифікація", size=10, color=POS, bold=True))
    frags.append(fitbox(45, 232, 230, 48, "АНУЛЬОВАНО: Несанкціоноване втручання\n(Злам захисту / стороння прошивка)", size=11, pad=4, fill="#fef6f5", stroke=POS, bold=True))
    frags.append(line(160, 217, 160, 232, color=POS, sw=1.8))

    # Стрілка вниз до Рівня 3
    frags.append(arrow(w / 2, 239, w / 2, 272, color=FIELD, sw=1.8))
    frags.append(text(w / 2 + 45, 258, "Не порушено", size=10, color=FIELD, bold=True))

    # Рівень 3: Перевірка зовнішніх умов (Волога, Перенапруга, Перегрів, Удар)
    frags.append(fitbox(w / 2 - 180, 272, 360, 44, "3. Аналіз сенсорів експлуатаційного стресу\n(LCI-датчики, перенапруга EOS, T > T_max, Shock > 50g)", size=11, pad=4, fill="#f4f6f8", stroke=LINE, bold=True))

    # Гілка 3: Виявлено порушення умов експлуатації
    frags.append(arrow(w / 2 + 180, 294, 780, 294, color=POS, sw=1.8))
    frags.append(text(670, 286, "Порушення умов", size=10, color=POS, bold=True))
    frags.append(fitbox(700, 310, 230, 52, "АНУЛЬОВАНО: Експлуатаційний стрес\n(Рідина, перенапруга, перегрів, удар)", size=11, pad=4, fill="#fef6f5", stroke=POS, bold=True))
    frags.append(line(780, 294, 780, 310, color=POS, sw=1.8))

    # Стрілка вниз до Рівня 4
    frags.append(arrow(w / 2, 316, w / 2, 350, color=FIELD, sw=1.8))
    frags.append(text(w / 2 + 45, 336, "Нормальний лог", size=10, color=FIELD, bold=True))

    # Рівень 4: Аналіз типу несправності
    frags.append(fitbox(w / 2 - 180, 350, 360, 46, "4. Функціональний та мікроструктурний аналіз\n(Визначення корінної причини відмови: RCA)", size=11, pad=4, fill="#f4f6f8", stroke=LINE, bold=True))

    # Розгалуження внизу: Знос vs Виробничий дефект
    # Ліва стрілка: Нормальний знос
    frags.append(line(w / 2 - 100, 396, w / 2 - 100, 425, color=LINE, sw=1.8))
    frags.append(arrow(w / 2 - 100, 425, 230, 425, color=NEG, sw=1.8))
    frags.append(arrow(230, 425, 230, 448, color=NEG, sw=1.8))
    frags.append(text(300, 417, "Природний знос", size=10, color=NEG, bold=True))
    frags.append(fitbox(115, 448, 230, 56, "ЗНОС: Вичерпання ресурсу\n(Стирання кнопок, деградація АКБ)\nПлатна заміна розхідників", size=11, pad=4, fill="#f4f8fe", stroke=NEG, bold=True))

    # Права стрілка: Виробничий дефект (Conformity / Warranty claim)
    frags.append(line(w / 2 + 100, 396, w / 2 + 100, 425, color=LINE, sw=1.8))
    frags.append(arrow(w / 2 + 100, 425, 730, 425, color=FIELD, sw=1.8))
    frags.append(arrow(730, 425, 730, 448, color=FIELD, sw=1.8))
    frags.append(text(660, 417, "Виробничий дефект", size=10, color=FIELD, bold=True))
    frags.append(fitbox(615, 448, 230, 56, "СХВАЛЕНО: Виробничий брак\n(Холодна пайка, прихований дефект)\nБезоплатний ремонт / Заміна", size=11, pad=4, fill="#f4fbf7", stroke=FIELD, sw=2, rx=8, bold=True))

    # Підсумок внизу
    frags.append(text(w / 2, h - 14, "Схема розмежування відповідальності згідно з нормами Magnuson-Moss Act та Директиви (EU) 2019/771", size=11, color=MUTED, italic=True))

    out_path = os.path.join(OUT_DIR, "warranty-decision-tree.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


def fig_tamper_detection_mechanisms():
    """Архітектура апаратних засобів виявлення порушень та незмінного логування."""
    w, h = 960, 520
    frags = []

    # Заголовок
    frags.append(text(w / 2, 26, "Апаратні сенсори виявлення порушень експлуатації та захищений журнал подій", size=15, bold=True))

    # Лівий блок: Фізичні та електричні датчики
    col_w = 260
    gap = 20
    top_y = 52
    col_h = 425

    # 1. Датчики розкриття та середовища
    x1 = 30
    frags.append(rect(x1, top_y, col_w, col_h, fill="#fefaf6", stroke="#ea580c", sw=2, rx=8))
    frags.append(rect(x1, top_y, col_w, 38, fill="#ffedd5", stroke="#ea580c", sw=1.5, rx=8))
    frags.append(text(x1 + col_w / 2, top_y + 24, "1. Сенсори втручання та середовища", size=12, color="#c2410c", bold=True))

    items1 = [
        ("Tamper Mesh / Switches", "Серпантинні провідні доріжки та\nмікроперемикачі розкриття корпуса"),
        ("LCI & Capacitive Moisture", "Хімічні індикатори контакту з рідиною\nта сенсорні пари виявлення конденсату"),
        ("Shock & Free-Fall Sensor", "3-осьовий акселерометр з апаратним\nфіксатором ударів понад 50g"),
        ("Thermal Monolithic Sensors", "Кремнієві термодатчики з тригерами\nперевищення максимальної T_junction"),
    ]
    cur_y = top_y + 48
    for title, desc in items1:
        frags.append(fitbox(x1 + 10, cur_y, col_w - 20, 68, f"{title}\n{desc}", size=11, pad=4, fill="#ffffff", stroke="#fed7aa", bold=False))
        cur_y += 76

    # 2. Електричні сенсори захисту
    x2 = x1 + col_w + gap
    frags.append(rect(x2, top_y, col_w, col_h, fill="#f4f8fe", stroke=NEG, sw=2, rx=8))
    frags.append(rect(x2, top_y, col_w, 38, fill="#e2edfd", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(x2 + col_w / 2, top_y + 24, "2. Сенсори електроживлення", size=12, color=NEG, bold=True))

    items2 = [
        ("Overvoltage & EOS Detector", "Швидкодіючі компаратори фіксації\nвикидів напруги понад Absolute Max"),
        ("Reverse Polarity Trigger", "Апаратний моніторинг зворотної\nполярності вхідного живлення"),
        ("eFuse Tripping Counter", "Незворотні електронні запобіжники\nзі статусом спрацювання захисту"),
        ("Supply Glitch Monitors", "Детектори короткочасних провалів\nнапруги живлення ядра процесора"),
    ]
    cur_y = top_y + 48
    for title, desc in items2:
        frags.append(fitbox(x2 + 10, cur_y, col_w - 20, 68, f"{title}\n{desc}", size=11, pad=4, fill="#ffffff", stroke="#c8ddfa", bold=False))
        cur_y += 76

    # 3. Захищене сховище та контролер
    x3 = x2 + col_w + gap
    frags.append(rect(x3, top_y, col_w + 90, col_h, fill="#f4fbf7", stroke=FIELD, sw=2, rx=8))
    frags.append(rect(x3, top_y, col_w + 90, 38, fill="#e1f5eb", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(x3 + (col_w + 90) / 2, top_y + 24, "3. Захищений контролер & Black-Box EEPROM", size=12, color=FIELD, bold=True))

    items3 = [
        ("Monotonic Lifetime Timers", "Незворотні апаратні лічильники мотогодин (POH) та циклів"),
        ("Violation Event Ring-Buffer", "Кільцевий буфер запису подій порушення у захищену пам'ять EEPROM"),
        ("Cryptographic Tamper Seals", "Обчислення HMAC-SHA256 для кожного блоку запису з апаратним ключем"),
        ("UDS / Secure Diagnostic API", "Захищений протокол видачі діагностичних даних техніку з RMA-токеном"),
    ]
    cur_y = top_y + 48
    for title, desc in items3:
        frags.append(fitbox(x3 + 10, cur_y, col_w + 70, 68, f"{title}\n{desc}", size=11, pad=4, fill="#ffffff", stroke="#c3e6d5", bold=False))
        cur_y += 76

    # Стрілки передачі подій між групами датчиків та контролером
    frags.append(arrow(x1 + col_w, top_y + 120, x3, top_y + 120, color="#ea580c", sw=1.8))
    frags.append(arrow(x2 + col_w, top_y + 240, x3, top_y + 240, color=NEG, sw=1.8))

    frags.append(text(w / 2, h - 14, "Сенсорна телеметрія формує криптографічно захищений доказовий базис для об'єктивного аудиту гарантійних випадків", size=11, color=MUTED, italic=True))

    out_path = os.path.join(OUT_DIR, "tamper-detection-mechanisms.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    fig_warranty_decision_tree()
    fig_tamper_detection_mechanisms()
