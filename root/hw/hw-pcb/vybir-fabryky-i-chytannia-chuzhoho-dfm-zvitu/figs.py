# -*- coding: utf-8 -*-
"""Фігури до теми «Вибір фабрики й читання чужого DFM-звіту»
(root/hw/hw-pcb/vybir-fabryky-i-chytannia-chuzhoho-dfm-zvitu).

Дві фігури:
  1. dfm-defects-catalog.svg — Каталог типових DFM-дефектів (пастки кислоти, містки маски, поясок отвору, зазор до краю).
  2. cam-eq-flowchart.svg     — Блок-схема проходження та прийняття рішень щодо CAM Engineering Questions (EQ).

Запуск: python figs.py -> пише SVG у ./img/
"""
import sys
import os

# 4 рівні вгору до кореня репозиторію -> scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. dfm-defects-catalog.svg — Каталог типових топологічних DFM-дефектів
# ════════════════════════════════════════════════════════════════════════════
def fig_dfm_defects_catalog():
    W, H = 860, 480
    f = []

    # Загальний фон
    f.append(rect(0, 0, W, H, fill=BG, stroke=LINE, sw=1, rx=0))

    # Заголовок зверху
    f.append(text(W / 2, 28, "Типові топологічні дефекти у звітах DFM та їхній механізм", size=16, bold=True, color=INK))

    # 4 колонки/картки для 4 головних дефектів
    card_w = 195
    card_h = 410
    card_y = 50
    spacing = 15
    start_x = 18

    defects = [
        {
            "num": "1",
            "title": "Пастка кислоти",
            "subtitle": "Acid Trap (< 90°)",
            "color": POS,
            "desc": ["Гострий кут затримує", "травильний розчин.", "Результат: локальне", "перетравлення доріжки", "і ризик розриву кола."],
            "good_note": "Норма: зріз 45° / скруглення"
        },
        {
            "num": "2",
            "title": "Слизька маска",
            "subtitle": "Mask Sliver (< 3.5 mil)",
            "color": POS,
            "desc": ["Занадто вузька смужка", "маски між падами QFP.", "Результат: лущення маски,", "перемички припою", "і короткі замикання."],
            "good_note": "Норма: місток ≥ 0.1 мм"
        },
        {
            "num": "3",
            "title": "Зрив пояска",
            "subtitle": "Annular Breakout",
            "color": POS,
            "desc": ["Зсув отвору відносно", "контактного майданчика.", "Результат: розрив міді,", "погана металізація", "і втрата контакту шарів."],
            "good_note": "Норма: Teardrop / ширший пад"
        },
        {
            "num": "4",
            "title": "Мідь біля краю",
            "subtitle": "Copper-to-Edge (< 0.3mm)",
            "color": POS,
            "desc": ["Провідники близько до", "фрезерування чи V-Score.", "Результат: оголена мідь,", "задирки, замикання на", "корпус і розшарування."],
            "good_note": "Норма: зазор ≥ 0.3..0.5 мм"
        }
    ]

    for idx, d in enumerate(defects):
        cx = start_x + idx * (card_w + spacing)

        # Рамка дефекту
        f.append(rect(cx, card_y, card_w, card_h, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))

        # Розділювальна лінія заголовка
        f.append(line(cx, card_y + 46, cx + card_w, card_y + 46, color="#d0d7de", sw=1.0))

        # Номер і назва
        f.append(circle(cx + 20, card_y + 22, 12, fill=d["color"], stroke="none"))
        f.append(text(cx + 20, card_y + 26, d["num"], size=12, bold=True, color="#ffffff"))
        f.append(text(cx + 38, card_y + 20, d["title"], size=13, bold=True, color=INK, anchor="start"))
        f.append(text(cx + 38, card_y + 36, d["subtitle"], size=10, bold=False, color=MUTED, anchor="start"))

        # Зона графічної ілюстрації
        draw_y = card_y + 54
        draw_h = 160
        f.append(rect(cx + 8, draw_y, card_w - 16, draw_h, fill="#ffffff", stroke="#d0d7de", sw=1, rx=4))

        mid_x = cx + card_w / 2
        mid_y = draw_y + draw_h / 2

        if idx == 0:
            # Acid Trap ілюстрація
            # Провідник під гострим кутом
            f.append(line(mid_x - 65, mid_y + 50, mid_x + 10, mid_y - 20, color="#b87333", sw=14))
            f.append(line(mid_x - 65, mid_y - 45, mid_x + 10, mid_y - 20, color="#b87333", sw=14))
            # Гострий клин з кислотою
            f.append(circle(mid_x - 15, mid_y - 10, 10, fill="#e74c3c", stroke="none"))
            f.append(text(mid_x - 15, mid_y - 7, "!", size=10, bold=True, color="#ffffff"))
            # Напис
            f.append(text(mid_x + 40, mid_y + 25, "Кут < 90°", size=11, bold=True, color=POS))
            f.append(text(mid_x + 40, mid_y + 40, "(застій кислоти)", size=9, color=MUTED))

        elif idx == 1:
            # Mask sliver ілюстрація
            # Два SMD контактні майданчики
            f.append(rect(mid_x - 65, mid_y - 50, 45, 100, fill="#b87333", stroke=LINE, sw=1.2, rx=2))
            f.append(rect(mid_x + 20, mid_y - 50, 45, 100, fill="#b87333", stroke=LINE, sw=1.2, rx=2))
            # Зелена маска навколо
            f.append(rect(mid_x - 15, mid_y - 55, 30, 110, fill="#27ae60", stroke=LINE, sw=1, rx=0))
            # Стрілка мікрощілини
            f.append(line(mid_x - 15, mid_y, mid_x + 15, mid_y, color=POS, sw=2))
            f.append(text(mid_x, mid_y - 12, "< 3.5 mil", size=10, bold=True, color=POS))
            f.append(text(mid_x, mid_y + 20, "Слизький", size=10, bold=True, color="#ffffff"))
            f.append(text(mid_x, mid_y + 32, "місток", size=10, bold=True, color="#ffffff"))

        elif idx == 2:
            # Annular ring breakout ілюстрація
            # Мідний пад
            f.append(circle(mid_x, mid_y, 48, fill="#b87333", stroke=LINE, sw=1.5))
            # Зсунутий отвір свердління (breakout)
            f.append(circle(mid_x + 24, mid_y, 25, fill="#ffffff", stroke=POS, sw=2.5))
            # Зона прориву
            f.append(text(mid_x + 52, mid_y + 4, "Прорив", size=10, bold=True, color=POS, anchor="start"))
            f.append(text(mid_x - 18, mid_y + 4, "Мідний", size=10, bold=True, color="#ffffff"))
            f.append(text(mid_x - 18, mid_y + 16, "поясок", size=10, bold=True, color="#ffffff"))

        elif idx == 3:
            # Copper-to-edge ілюстрація
            # Контур плати (пунктир)
            f.append(line(mid_x + 50, mid_y - 65, mid_x + 50, mid_y + 65, color=LINE, sw=2.5, dash="6,4"))
            # Текстоліт
            f.append(rect(mid_x - 70, mid_y - 60, 115, 120, fill="#e8f5e9", stroke="#a5d6a7", sw=1, rx=0))
            # Мідний полігон/доріжка надто близько до краю
            f.append(rect(mid_x - 60, mid_y - 45, 98, 90, fill="#b87333", stroke=LINE, sw=1.2, rx=2))
            # Розмір зазору
            f.append(line(mid_x + 38, mid_y - 10, mid_x + 50, mid_y - 10, color=POS, sw=2))
            f.append(text(mid_x + 20, mid_y - 20, "< 0.2 mm", size=10, bold=True, color=POS))
            f.append(text(mid_x + 58, mid_y + 25, "Край", size=10, bold=True, color=INK, anchor="start"))
            f.append(text(mid_x + 58, mid_y + 38, "плати", size=10, bold=True, color=INK, anchor="start"))

        # Опис наслідків
        desc_y = draw_y + draw_h + 18
        for l_idx, line_text in enumerate(d["desc"]):
            f.append(text(cx + card_w / 2, desc_y + l_idx * 16, line_text, size=11, color=INK))

        # Нижня плашка з нормою
        norm_y = card_y + card_h - 32
        f.append(rect(cx + 8, norm_y, card_w - 16, 24, fill="#eef8f1", stroke=FIELD, sw=1, rx=4))
        f.append(text(cx + card_w / 2, norm_y + 16, d["good_note"], size=10, bold=True, color=FIELD))

    # Збереження
    out_path = os.path.join(IMG, 'dfm-defects-catalog.svg')
    with open(out_path, 'w', encoding='utf-8') as fp:
        fp.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fp.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (W, H, W, H))
        fp.write('<defs>\n')
        fp.write('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n')
        fp.write('    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>\n' % LINE)
        fp.write('  </marker>\n')
        fp.write('</defs>\n')
        fp.write("\n".join(f))
        fp.write('\n</svg>\n')
    print("Generated:", out_path)


# ════════════════════════════════════════════════════════════════════════════
# 2. cam-eq-flowchart.svg — Блок-схема обробки CAM Engineering Questions (EQ)
# ════════════════════════════════════════════════════════════════════════════
def fig_cam_eq_flowchart():
    W, H = 840, 470
    f = []

    # Загальний фон
    f.append(rect(0, 0, W, H, fill=BG, stroke=LINE, sw=1, rx=0))

    # Заголовок
    f.append(text(W / 2, 28, "Конвеєр обробки інженерних запитів CAM (Engineering Questions / EQ)", size=16, bold=True, color=INK))

    # Блок 1: Вихідний пакет герберів
    b1_x, b1_y, b1_w, b1_h = 40, 60, 200, 55
    f.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#f0f4f8", stroke=LINE, sw=1.5, rx=6))
    f.append(text(b1_x + b1_w / 2, b1_y + 22, "Вихідний пакет файлів", size=13, bold=True, color=INK))
    f.append(text(b1_x + b1_w / 2, b1_y + 42, "Gerber X2 / ODB++, Drill, BOM", size=11, color=MUTED))

    # Стрілка 1 -> 2
    f.append(arrow(b1_x + b1_w, b1_y + b1_h / 2, b1_x + b1_w + 50, b1_y + b1_h / 2, color=LINE, sw=1.8))

    # Блок 2: CAM аудит фабрики
    b2_x, b2_y, b2_w, b2_h = 290, 60, 220, 55
    f.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#f0f4f8", stroke=LINE, sw=1.5, rx=6))
    f.append(text(b2_x + b2_w / 2, b2_y + 22, "CAM-аудит фабрики", size=13, bold=True, color=INK))
    f.append(text(b2_x + b2_w / 2, b2_y + 42, "Автоматизований DFM-аналіз", size=11, color=MUTED))

    # Стрілка 2 -> вниз до ромба розгалуження
    f.append(arrow(b2_x + b2_w / 2, b2_y + b2_h, b2_x + b2_w / 2, 160, color=LINE, sw=1.8))

    # Ромб рішень: Чи виявлено зауваження?
    rx, ry, rw, rh = 400, 195, 170, 70
    points = "%d,%d %d,%d %d,%d %d,%d" % (rx, ry - rh / 2, rx + rw / 2, ry, rx, ry + rh / 2, rx - rw / 2, ry)
    f.append('<polygon points="%s" fill="#fff8e1" stroke="%s" stroke-width="1.8"/>' % (points, LINE))
    f.append(text(rx, ry - 6, "Чи виявлено", size=12, bold=True, color=INK))
    f.append(text(rx, ry + 12, "порушення норм?", size=12, bold=True, color=INK))

    # Гілка "НІ" (Праворуч -> Запуск у виробництво)
    f.append(arrow(rx + rw / 2, ry, 680, ry, color=FIELD, sw=2.0))
    f.append(text(rx + rw / 2 + 50, ry - 10, "Ні (0 EQ)", size=11, bold=True, color=FIELD))

    # Блок: Запуск у виробництво
    prod_x, prod_y, prod_w, prod_h = 680, 165, 130, 60
    f.append(rect(prod_x, prod_y, prod_w, prod_h, fill="#e8f5e9", stroke=FIELD, sw=2.0, rx=8))
    f.append(text(prod_x + prod_w / 2, prod_y + 26, "Запуск у", size=13, bold=True, color=FIELD))
    f.append(text(prod_x + prod_w / 2, prod_y + 46, "виробництво", size=13, bold=True, color=FIELD))

    # Гілка "ТАК" (Вниз -> Формування звіту EQ)
    f.append(arrow(rx, ry + rh / 2, rx, 290, color=POS, sw=2.0))
    f.append(text(rx + 35, ry + rh / 2 + 20, "Так (EQ)", size=11, bold=True, color=POS))

    # Блок 3: Звіт CAM EQ
    b3_x, b3_y, b3_w, b3_h = 280, 290, 240, 55
    f.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#fde8e8", stroke=POS, sw=1.8, rx=6))
    f.append(text(b3_x + b3_w / 2, b3_y + 22, "Звіт CAM EQ інженеру", size=13, bold=True, color=POS))
    f.append(text(b3_x + b3_w / 2, b3_y + 42, "Знімки шарів + пропозиції правок", size=11, color=MUTED))

    # Розгалуження на 3 варіанти дій інженера
    f.append(line(b3_x + b3_w / 2, b3_y + b3_h, b3_x + b3_w / 2, 375, color=LINE, sw=1.5))
    f.append(line(130, 375, 680, 375, color=LINE, sw=1.5))

    # 3 варіанти рішень:
    # Варіант А: Схвалити правку CAM (Auto-clip, Teardrop)
    act1_x, act1_y, act1_w, act1_h = 40, 395, 180, 60
    f.append(arrow(130, 375, 130, act1_y, color=LINE, sw=1.5))
    f.append(rect(act1_x, act1_y, act1_w, act1_h, fill="#edf7ed", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(act1_x + act1_w / 2, act1_y + 22, "1. Схвалити правку CAM", size=12, bold=True, color=FIELD))
    f.append(text(act1_x + act1_w / 2, act1_y + 42, "Обрізка маски, teardrop", size=10, color=MUTED))

    # Варіант Б: Відхилити і перегенерувати CAD (критична геометрія)
    act2_x, act2_y, act2_w, act2_h = 290, 395, 220, 60
    f.append(arrow(400, 375, 400, act2_y, color=LINE, sw=1.5))
    f.append(rect(act2_x, act2_y, act2_w, act2_h, fill="#fff3e0", stroke="#e67e22", sw=1.5, rx=6))
    f.append(text(act2_x + act2_w / 2, act2_y + 22, "2. Перерозвести в CAD", size=12, bold=True, color="#d35400"))
    f.append(text(act2_x + act2_w / 2, act2_y + 42, "Зміна трасування / зазорів", size=10, color=MUTED))

    # Варіант В: Відхилити під власну відповідальність (Wave disclaimer)
    act3_x, act3_y, act3_w, act3_h = 580, 395, 200, 60
    f.append(arrow(680, 375, 680, act3_y, color=LINE, sw=1.5))
    f.append(rect(act3_x, act3_y, act3_w, act3_h, fill="#fbe9e7", stroke=POS, sw=1.5, rx=6))
    f.append(text(act3_x + act3_w / 2, act3_y + 22, "3. Ігнорувати (Hold Waive)", size=12, bold=True, color=POS))
    f.append(text(act3_x + act3_w / 2, act3_y + 42, "Ризик браку бере замовник", size=10, color=MUTED))

    # Збереження
    out_path = os.path.join(IMG, 'cam-eq-flowchart.svg')
    with open(out_path, 'w', encoding='utf-8') as fp:
        fp.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fp.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (W, H, W, H))
        fp.write('<defs>\n')
        fp.write('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n')
        fp.write('    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>\n' % LINE)
        fp.write('  </marker>\n')
        fp.write('</defs>\n')
        fp.write("\n".join(f))
        fp.write('\n</svg>\n')
    print("Generated:", out_path)


if __name__ == "__main__":
    fig_dfm_defects_catalog()
    fig_cam_eq_flowchart()
