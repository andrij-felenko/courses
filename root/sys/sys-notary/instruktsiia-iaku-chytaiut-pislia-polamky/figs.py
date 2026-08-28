# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Інструкція, яку читають після поламки, а не до»."""
import sys, os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_warning_label_hierarchy():
    """Фігура 1: Ієрархія попереджувальних маркувань безпеки за стандартами ANSI Z535.4 та ISO 3864-2."""
    w, h = 960, 560
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Ієрархія сигнальних слів і маркування безпеки (ANSI Z535.4 / ISO 3864-2)", size=16, bold=True))

    # Стовпець 1: DANGER
    x1 = 30
    w_card = 210
    h_card = 490
    frags.append(rect(x1, 50, w_card, h_card, fill="#ffffff", stroke="#c0392b", sw=2, rx=6))
    frags.append(rect(x1, 50, w_card, 55, fill="#c0392b", stroke="#c0392b", sw=2, rx=0))
    frags.append(text(x1 + w_card / 2, 75, "▲ DANGER", size=16, color="#ffffff", bold=True))
    frags.append(text(x1 + w_card / 2, 94, "НЕБЕЗПЕКА", size=12, color="#ffffff", bold=True))
    
    frags.append(fitbox(x1 + 10, 115, w_card - 20, 75, "Рівень ризику:\nНЕМАЄ ПРАВА НА ПОМИЛКУ.\nНеминуча загроза життю\nабо найтяжчого каліцтва.", size=10, fill="#fdf2f2", stroke="#c0392b"))
    frags.append(fitbox(x1 + 10, 200, w_card - 20, 100, "Фізична природа:\n• Висока напруга (>600 В)\n• Відкриті обертові вали\n• Летальні отруйні гази\n• Пряме лазерне випромінювання 4 класу", size=10, fill="#ffffff", stroke="#e5e7eb"))
    frags.append(fitbox(x1 + 10, 310, w_card - 20, 95, "Обов'язкова дія:\nНЕГАЙНО ЗНЕСТРУМИТИ.\nВхід дозволено лише після\nповної процедури LOTO\n(Lockout / Tagout).", size=10, fill="#fef2f2", stroke="#c0392b"))
    frags.append(fitbox(x1 + 10, 415, w_card - 20, 110, "Стандарт кольору:\nSafety Red (PANTONE 186 C)\nБілий текст на червоному тлі.\nСимвол ISO 7010-W001\n(знак оклику в трикутнику).", size=9, fill="#f9fafb", stroke="#9ca3af"))

    # Стовпець 2: WARNING
    x2 = 260
    frags.append(rect(x2, 50, w_card, h_card, fill="#ffffff", stroke="#d97706", sw=2, rx=6))
    frags.append(rect(x2, 50, w_card, 55, fill="#ea580c", stroke="#ea580c", sw=2, rx=0))
    frags.append(text(x2 + w_card / 2, 75, "▲ WARNING", size=16, color="#ffffff", bold=True))
    frags.append(text(x2 + w_card / 2, 94, "ПОПЕРЕДЖЕННЯ", size=12, color="#ffffff", bold=True))
    
    frags.append(fitbox(x2 + 10, 115, w_card - 20, 75, "Рівень ризику:\nПОТЕНЦІЙНА СМЕРТЬ.\nЙмовірна важка травма\nза невиконання правил.", size=10, fill="#fff7ed", stroke="#ea580c"))
    frags.append(fitbox(x2 + 10, 200, w_card - 20, 100, "Фізична природа:\n• Ризик вибуху Li-Ion\n• Напруга 110–230 В AC\n• Тиск у пневмосистемі\n• Токсичні випаровування пайки", size=10, fill="#ffffff", stroke="#e5e7eb"))
    frags.append(fitbox(x2 + 10, 310, w_card - 20, 95, "Обов'язкова дія:\nВикористовувати ЗІЗ:\nзахисні окуляри, термоізоляційні рукавички,\nперевірити заземлення.", size=10, fill="#fff7ed", stroke="#ea580c"))
    frags.append(fitbox(x2 + 10, 415, w_card - 20, 110, "Стандарт кольору:\nSafety Orange (PANTONE 151 C)\nЧорний текст на помаранчевому.\nСимвол ISO 7010-W001\n(знак оклику в трикутнику).", size=9, fill="#f9fafb", stroke="#9ca3af"))

    # Стовпець 3: CAUTION
    x3 = 490
    frags.append(rect(x3, 50, w_card, h_card, fill="#ffffff", stroke="#ca8a04", sw=2, rx=6))
    frags.append(rect(x3, 50, w_card, 55, fill="#eab308", stroke="#eab308", sw=2, rx=0))
    frags.append(text(x3 + w_card / 2, 75, "▲ CAUTION", size=16, color="#1e293b", bold=True))
    frags.append(text(x3 + w_card / 2, 94, "ЗАСТЕРЕЖЕННЯ", size=12, color="#1e293b", bold=True))
    
    frags.append(fitbox(x3 + 10, 115, w_card - 20, 75, "Рівень ризику:\nЛЕГКА АБО СЕРЕДНЯ ТРАВМА.\nТимчасова втрата\nпрацездатності.", size=10, fill="#fefce8", stroke="#ca8a04"))
    frags.append(fitbox(x3 + 10, 200, w_card - 20, 100, "Фізична природа:\n• Гарячий радіатор (>65 °C)\n• Гострі кромки шасі\n• Ризик затискання пальців\n• Акустичний шум сигналізатора", size=10, fill="#ffffff", stroke="#e5e7eb"))
    frags.append(fitbox(x3 + 10, 310, w_card - 20, 95, "Обов'язкова дія:\nДати охолонути 15 хв.\nПрацювати в захисних\nрукавицях, уникати контакту\nз оголеним металом.", size=10, fill="#fefce8", stroke="#ca8a04"))
    frags.append(fitbox(x3 + 10, 415, w_card - 20, 110, "Стандарт кольору:\nSafety Yellow (PANTONE 109 C)\nЧорний текст на жовтому тлі.\nСимвол ISO 7010-W001\n(знак оклику в трикутнику).", size=9, fill="#f9fafb", stroke="#9ca3af"))

    # Стовпець 4: NOTICE
    x4 = 720
    frags.append(rect(x4, 50, w_card, h_card, fill="#ffffff", stroke="#2563eb", sw=2, rx=6))
    frags.append(rect(x4, 50, w_card, 55, fill="#2563eb", stroke="#2563eb", sw=2, rx=0))
    frags.append(text(x4 + w_card / 2, 75, "NOTICE", size=16, color="#ffffff", bold=True))
    frags.append(text(x4 + w_card / 2, 94, "ПОВІДОМЛЕННЯ", size=12, color="#ffffff", bold=True))
    
    frags.append(fitbox(x4 + 10, 115, w_card - 20, 75, "Рівень ризику:\nПОШКОДЖЕННЯ МАЙНА.\nБез травм персоналу,\nлише збитки обладнанню.", size=10, fill="#eff6ff", stroke="#2563eb"))
    frags.append(fitbox(x4 + 10, 200, w_card - 20, 100, "Фізична природа:\n• Чутливість до ESD (статичної електрики)\n• Гаряче відключення кабелів\n• Скидання конфігурації\n• Переривання прошивки OTA", size=10, fill="#ffffff", stroke="#e5e7eb"))
    frags.append(fitbox(x4 + 10, 310, w_card - 20, 95, "Обов'язкова дія:\nОдягти антистатичний браслет.\nВимкнути живлення перед\nпідключенням датчиків.\nНе вимикати під час запису.", size=10, fill="#eff6ff", stroke="#2563eb"))
    frags.append(fitbox(x4 + 10, 415, w_card - 20, 110, "Стандарт кольору:\nSafety Blue (PANTONE 2935 C)\nБілий текст на синьому тлі.\nБЕЗ символу трикутника\n(тільки інформація про майно).", size=9, fill="#f9fafb", stroke="#9ca3af"))

    render(os.path.join(IMG_DIR, "warning-label-hierarchy.svg"), w, h, *frags)


def fig_troubleshooting_flowchart_design():
    """Фігура 2: Структура графа діагностики та пошуку несправностей."""
    w, h = 960, 520
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Граф локалізації несправностей: від симптому до відновлення (Troubleshooting Graph)", size=16, bold=True))

    # Рівень 1: Симптом (Початок)
    frags.append(rect(340, 55, 280, 55, fill="#fef2f2", stroke="#c0392b", sw=2, rx=8))
    frags.append(text(480, 78, "СИМПТОМ (Спостереження)", size=13, color="#c0392b", bold=True))
    frags.append(text(480, 97, "Червоний світлодіод STATUS блимає кожні 2 с", size=11, color="#1e293b"))

    frags.append(arrow(480, 110, 480, 145, color="#334155"))

    # Рівень 2: Перевірка 1 (Діагностичний тест)
    frags.append(rect(340, 145, 280, 65, fill="#eff6ff", stroke="#2563eb", sw=2, rx=8))
    frags.append(text(480, 168, "ПЕРЕВІРКА 1: Напруга живлення", size=13, color="#2563eb", bold=True))
    frags.append(text(480, 188, "Чи напруга на клемах V+ та GND у межах 18–30 В DC?", size=10, color="#1e293b"))

    # Гілка НІ (Ліворуч) від Перевірки 1
    frags.append(arrow(340, 177, 180, 177, color="#c0392b"))
    frags.append(text(260, 170, "НІ (V < 18 В)", size=11, color="#c0392b", bold=True))

    frags.append(fitbox(50, 140, 130, 75, "ДІЯ 1:\nПеревірити блок живлення,\nзапобіжник лінії 24 В та\nпадіння напруги в кабелі", size=10, fill="#f0fdf4", stroke="#16a34a"))

    # Гілка ТАК (Вниз) від Перевірки 1
    frags.append(arrow(480, 210, 480, 245, color="#16a34a"))
    frags.append(text(515, 228, "ТАК", size=11, color="#16a34a", bold=True))

    # Рівень 3: Перевірка 2 (Шина зв'язку)
    frags.append(rect(340, 245, 280, 65, fill="#eff6ff", stroke="#2563eb", sw=2, rx=8))
    frags.append(text(480, 268, "ПЕРЕВІРКА 2: Термінація RS-485", size=13, color="#2563eb", bold=True))
    frags.append(text(480, 288, "Опір між лініями A та B знеструмленої шини ~60 Ом?", size=10, color="#1e293b"))

    # Гілка НІ (Праворуч) від Перевірки 2
    frags.append(arrow(620, 277, 770, 277, color="#c0392b"))
    frags.append(text(695, 270, "НІ (R != 60 Ом)", size=11, color="#c0392b", bold=True))

    frags.append(fitbox(770, 240, 140, 75, "ДІЯ 2:\nУвімкнути термінатор 120 Ом\nна обох кінцевих пристроях\nі вимкнути на проміжних", size=10, fill="#f0fdf4", stroke="#16a34a"))

    # Гілка ТАК (Вниз) від Перевірки 2
    frags.append(arrow(480, 310, 480, 345, color="#16a34a"))
    frags.append(text(515, 328, "ТАК", size=11, color="#16a34a", bold=True))

    # Рівень 4: Перевірка 3 (Логіка та адреса)
    frags.append(rect(340, 345, 280, 65, fill="#eff6ff", stroke="#2563eb", sw=2, rx=8))
    frags.append(text(480, 368, "ПЕРЕВІРКА 3: Конфлікт Modbus ID", size=13, color="#2563eb", bold=True))
    frags.append(text(480, 388, "Чи блимає світлодіод RX під час запиту майстра?", size=10, color="#1e293b"))

    # Гілка НІ (Ліворуч) від Перевірки 3
    frags.append(arrow(340, 377, 180, 377, color="#c0392b"))
    frags.append(text(260, 370, "НІ (Немає RX)", size=11, color="#c0392b", bold=True))

    frags.append(fitbox(50, 340, 130, 75, "ДІЯ 3:\nПоміняти місцями дроти\nліній A та B (інверсія полярності\nдиференціальної пари)", size=10, fill="#f0fdf4", stroke="#16a34a"))

    # Гілка ТАК (Вниз) від Перевірки 3
    frags.append(arrow(480, 410, 480, 440, color="#16a34a"))
    frags.append(text(515, 425, "ТАК", size=11, color="#16a34a", bold=True))

    # Фінальна дія 4 (Внизу)
    frags.append(fitbox(310, 440, 340, 65, "ДІЯ 4: Перевірити Modbus Address і Baudrate\nЗвірити швидкість шини з майстром (9600/115200)\nта усунути дублювання адрес у мережі", size=10, fill="#f0fdf4", stroke="#16a34a"))

    render(os.path.join(IMG_DIR, "troubleshooting-flowchart-design.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_warning_label_hierarchy()
    fig_troubleshooting_flowchart_design()
    print("All figures successfully generated in img/")
