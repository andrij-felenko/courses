# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F   = "#e8eefc"
RED_F    = "#fdecea"
GREEN_F  = "#e6f7ee"
PURPLE_F = "#f3e8fa"
YELLOW_F = "#fffde6"

# ── 1. germain-mapping: Відображення простих чисел Софі Жермен у безпечні прості числа ──
def fig_germain_mapping():
    W, H = 1000, 520
    elements = []

    # Заголовок
    elements.append(text(W / 2, 35, "Відображення p ↦ q = 2p + 1 для початкових простих чисел", size=17, color=INK, bold=True))

    # Стовпчик 1: Початкові прості числа p
    elements.append(fitbox(60, 65, 360, 40, "Просте число p", size=15, fill=BLUE_F, stroke=NEG, sw=2, bold=True, color=INK))

    # Стовпчик 2: Результат 2p + 1 та його статус
    elements.append(fitbox(580, 65, 360, 40, "Результат q = 2p + 1 (Безпечне просте чи складене)", size=15, fill=PURPLE_F, stroke="#7e22ce", sw=2, bold=True, color=INK))

    # Параметри рядків
    rows = [
        ("p = 2", "q = 2(2) + 1 = 5\nПРОСТЕ (Жермен ✓)", GREEN_F, FIELD),
        ("p = 3", "q = 2(3) + 1 = 7\nПРОСТЕ (Жермен ✓)", GREEN_F, FIELD),
        ("p = 5", "q = 2(5) + 1 = 11\nПРОСТЕ (Жермен ✓)", GREEN_F, FIELD),
        ("p = 7", "q = 2(7) + 1 = 15 = 3 · 5\nСКЛАДЕНЕ (не Жермен ✗)", RED_F, POS),
        ("p = 11", "q = 2(11) + 1 = 23\nПРОСТЕ (Жермен ✓)", GREEN_F, FIELD),
        ("p = 13", "q = 2(13) + 1 = 27 = 3³\nСКЛАДЕНЕ (не Жермен ✗)", RED_F, POS),
        ("p = 23", "q = 2(23) + 1 = 47\nПРОСТЕ (Жермен ✓)", GREEN_F, FIELD),
    ]

    y_start = 115
    row_h = 42
    spacing = 5

    for i, (p_text, q_text, bg_color, stroke_color) in enumerate(rows):
        y = y_start + i * (row_h + spacing)
        
        # Ліва комірка (p)
        elements.append(fitbox(60, y, 360, row_h, p_text, size=14, fill=FILL, stroke=MUTED, sw=1.5, bold=True, color=INK))
        
        # Стрілка з оператором
        elements.append(arrow(430, y + row_h / 2, 570, y + row_h / 2, color=NEG, sw=2))
        elements.append(text(500, y + row_h / 2 - 8, "2p + 1", size=12, color=NEG, bold=True))

        # Права комірка (q)
        elements.append(fitbox(580, y, 360, row_h, q_text, size=12.5, fill=bg_color, stroke=stroke_color, sw=1.8, bold=True, color=INK))

    # Висновок
    elements.append(fitbox(60, 450, 880, 50, "Операція 2p + 1 відсіює частину простих чисел. Ті, що витримують перевірку, стають криптографічними безпечними простими числами.", size=13, fill=YELLOW_F, stroke=MUTED, sw=1.5, color=INK))

    return render(os.path.join(OUT, "germain-mapping.svg"), W, H, *elements,
                  title="Відображення простих чисел Софі Жермен у безпечні прості числа")


# ── 2. diffie-hellman-safe-prime: Порівняння структур порядку групи для Diffie-Hellman ──
def fig_diffie_hellman_safe_prime():
    W, H = 1000, 460
    elements = []

    elements.append(text(W / 2, 35, "Вплив будови порядку групи (Z/qZ)* на стійкість до алгоритму Поліга — Геллмана", size=16, color=INK, bold=True))

    # Панель А: Звичайне просте число (Гладкий порядок q - 1)
    elements.append(fitbox(50, 65, 420, 340, "", fill=RED_F, stroke=POS, sw=2, rx=8))
    elements.append(text(260, 95, "Вразливий модуль: Звичайне просте q", size=15, color=POS, bold=True))
    elements.append(text(260, 125, "Порядок групи: q − 1 = 2ᵃ · 3ᵇ · 5ᶜ · 7ᵈ ...", size=13.5, color=INK))
    elements.append(text(260, 150, "(багато малих простих множників)", size=13, color=MUTED, bold=True))

    # Ілюстрація розщеплення Поліга-Геллмана
    elements.append(fitbox(75, 180, 370, 110, "Алгоритм Поліга — Геллмана:\n1. Розв'язання ДЛП у малих підгрупах Z₃, Z₅, Z₇\n2. Обчислення остач x mod pᵢ\n3. Відновлення x через Китайську теорему про остачі\nСкладність: O(∑ eᵢ √pᵢ) — ШВИДКИЙ ЗЛАМ!", size=12.5, fill=FILL, stroke=POS, sw=1.5, color=POS))
    elements.append(fitbox(75, 305, 370, 85, "РЕЗУЛЬТАТ: Дискретне логорифмування обчислюється за кілька секунд на звичайному ПК.", size=13, fill=RED_F, stroke=POS, sw=1.5, bold=True, color=POS))

    # Панель Б: Безпечне просте число q = 2p + 1
    elements.append(fitbox(530, 65, 420, 340, "", fill=GREEN_F, stroke=FIELD, sw=2, rx=8))
    elements.append(text(740, 95, "Захищений модуль: Безпечне просте q = 2p + 1", size=15, color=FIELD, bold=True))
    elements.append(text(740, 125, "Порядок групи: q − 1 = 2 · p", size=13.5, color=INK))
    elements.append(text(740, 150, "(лиш один гігантський простий множник p)", size=13, color=FIELD, bold=True))

    # Захист
    elements.append(fitbox(555, 180, 370, 110, "Стійкість до Поліга — Геллмана:\n1. Єдиний великий підгруповий порядок p\n2. Відсутність малих дільників для розщеплення\n3. Зведення складності до загального ДЛП у підгрупі\nСкладність: O(√p) — НЕПРОНИКНИЙ БАР'ЄР!", size=12.5, fill=FILL, stroke=FIELD, sw=1.5, color=FIELD))
    elements.append(fitbox(555, 305, 370, 85, "РЕЗУЛЬТАТ: Криптографічна стійкість відповідає повній довжині ключа.", size=13, fill=GREEN_F, stroke=FIELD, sw=1.8, bold=True, color=FIELD))

    # Нижня рамка
    elements.append(fitbox(50, 415, 900, 35, "Використання безпечних простих чисел q = 2p + 1 блокує факторизацію порядку групи q − 1 та забезпечує максимальну стійкість протоколу Діффі — Геллмана.", size=13, fill=YELLOW_F, stroke=MUTED, sw=1.5, color=INK))

    return render(os.path.join(OUT, "diffie-hellman-safe-prime.svg"), W, H, *elements,
                  title="Порівняння структур порядку групи для Diffie-Hellman")


# ── 3. cunningham-chain: Ланцюжки Каннінгема першого роду ──
def fig_cunningham_chain():
    W, H = 1000, 440
    elements = []

    elements.append(text(W / 2, 35, "Ланцюжок Каннінгема першого роду завдовжки 5 (початок p₁ = 2)", size=17, color=INK, bold=True))

    # Елементи ланцюжка
    chain_nodes = [
        ("p₁ = 2", "Просте (Жермен 1)", GREEN_F, FIELD),
        ("p₂ = 5", "2(2)+1 = 5\nПросте (Жермен 2)", GREEN_F, FIELD),
        ("p₃ = 11", "2(5)+1 = 11\nПросте (Жермен 3)", GREEN_F, FIELD),
        ("p₄ = 23", "2(11)+1 = 23\nПросте (Жермен 4)", GREEN_F, FIELD),
        ("p₅ = 47", "2(23)+1 = 47\nПросте (Жермен 5)", GREEN_F, FIELD),
        ("p₆ = 95", "2(47)+1 = 95\n5 · 19 (Складене!)", RED_F, POS),
    ]

    x_start = 40
    box_w = 135
    box_h = 75
    gap_x = 22

    y_pos = 120

    for i, (title_str, desc_str, bg_c, stroke_c) in enumerate(chain_nodes):
        x = x_start + i * (box_w + gap_x)
        
        # Блок вузла
        content = f"{title_str}\n{desc_str}"
        elements.append(fitbox(x, y_pos, box_w, box_h, content, size=12.5, fill=bg_c, stroke=stroke_c, sw=2, bold=True, color=INK))

        # Стрілка між вузлами
        if i < len(chain_nodes) - 1:
            arrow_x1 = x + box_w
            arrow_x2 = arrow_x1 + gap_x
            elements.append(arrow(arrow_x1, y_pos + box_h / 2, arrow_x2, y_pos + box_h / 2, color=NEG, sw=2))

    # Маркування обриву ланцюжка
    elements.append(fitbox(700, y_pos + box_h + 30, 260, 50, "ОБРИВ ЛАНЦЮЖКА:\np₆ = 95 не є простим!", size=13, fill=RED_F, stroke=POS, sw=2, bold=True, color=POS))
    elements.append(arrow(850, y_pos + box_h + 5, 850, y_pos + box_h + 28, color=POS, sw=2))

    # Нижній опис
    elements.append(fitbox(40, 340, 920, 75, "Ланцюжок Каннінгема першого роду — це послідовність простих чисел (p₁, p₂, ..., pₖ), де pᵢ₊₁ = 2pᵢ + 1.\nКожен елемент ланцюжка (крім останнього) є простим числом Софі Жермен, а кожен елемент (крім першого) — безпечним простим числом.", size=13.5, fill=BLUE_F, stroke=NEG, sw=1.8, color=INK))

    return render(os.path.join(OUT, "cunningham-chain.svg"), W, H, *elements,
                  title="Ланцюжок Каннінгема першого роду")


if __name__ == "__main__":
    fig_germain_mapping()
    fig_diffie_hellman_safe_prime()
    fig_cunningham_chain()
    print("Усі фігури успішно згенеровано у teці img/")
