# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Версія протоколу: сумісність вперед і назад, зміна полів»
(root/course/embedded/versiia-protokolu).
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Матриця сумісності: пряма і зворотна ──────────────────────────────────
def fig_compatibility_matrix():
    W, H = 880, 480
    f = []

    f.append(text(W / 2, 28, "Матриця сумісності: взаємодія вузлів різних поколінь",
                  17, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "як старі й нові прошивки інтерпретують повідомлення одна одної в розподіленій мережі",
                  12, MUTED, "middle", italic=True))

    # Стовпці і рядки матриці
    ox, oy = 140, 85
    col_w, row_h = 340, 165

    # Заголовки стовпців (Приймач)
    f.append(text(ox + col_w / 2, oy - 12, "Приймач v1 (Старий вузол)", 13, INK, "middle", bold=True))
    f.append(text(ox + col_w * 1.5, oy - 12, "Приймач v2 (Оновлений вузол)", 13, INK, "middle", bold=True))

    # Заголовки рядків (Відправник)
    f.append(text(ox - 15, oy + row_h / 2 - 8, "Відправник v1", 13, INK, "end", bold=True))
    f.append(text(ox - 15, oy + row_h / 2 + 10, "(Старий вузол)", 11, MUTED, "end"))

    f.append(text(ox - 15, oy + row_h * 1.5 - 8, "Відправник v2", 13, INK, "end", bold=True))
    f.append(text(ox - 15, oy + row_h * 1.5 + 10, "(Оновлений)", 11, MUTED, "end"))

    # Квадрант 1: v1 -> v1 (Базовий зв'язок)
    x1, y1 = ox, oy
    f.append(rect(x1 + 6, y1 + 6, col_w - 12, row_h - 12, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(x1 + col_w / 2, y1 + 32, "Базова сумісність v1 ↔ v1", 13, INK, "middle", bold=True))
    f.append(text(x1 + col_w / 2, y1 + 58, "• Однаковий набір полів і розмірів", 11.5, INK, "middle"))
    f.append(text(x1 + col_w / 2, y1 + 78, "• Прямий розбір без трансформацій", 11.5, MUTED, "middle"))
    f.append(text(x1 + col_w / 2, y1 + 104, "Стан системи в момент першого релізу", 11, FIELD, "middle", bold=True))

    # Квадрант 2: v1 -> v2 (Зворотна сумісність / Backward Compatibility)
    x2, y2 = ox + col_w, oy
    f.append(rect(x2 + 6, y2 + 6, col_w - 12, row_h - 12, fill="#eefaf2", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(x2 + col_w / 2, y2 + 32, "Зворотна сумісність (Backward)", 13, FIELD, "middle", bold=True))
    f.append(text(x2 + col_w / 2, y2 + 58, "• Новий приймач читає старий пакет v1", 11.5, INK, "middle"))
    f.append(text(x2 + col_w / 2, y2 + 78, "• Відсутні поля v2 заповнюються дефолтами", 11.5, INK, "middle"))
    f.append(text(x2 + col_w / 2, y2 + 100, "• Новий сервер приймає телеметрію старих плат", 11, MUTED, "middle"))
    f.append(text(x2 + col_w / 2, y2 + 124, "✔ Безпечно: сервер знає правила минулих версій", 11, FIELD, "middle", bold=True))

    # Квадрант 3: v2 -> v1 (Пряма сумісність / Forward Compatibility)
    x3, y3 = ox, oy + row_h
    f.append(rect(x3 + 6, y3 + 6, col_w - 12, row_h - 12, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    f.append(text(x3 + col_w / 2, y3 + 32, "Пряма сумісність (Forward)", 13, NEG, "middle", bold=True))
    f.append(text(x3 + col_w / 2, y3 + 58, "• Старий приймач читає новий пакет v2", 11.5, INK, "middle"))
    f.append(text(x3 + col_w / 2, y3 + 78, "• Невідомі нові поля ігноруються / пропускаються", 11.5, INK, "middle"))
    f.append(text(x3 + col_w / 2, y3 + 100, "• Старий прилад не падає від розширених кадрів", 11, MUTED, "middle"))
    f.append(text(x3 + col_w / 2, y3 + 124, "✔ Вимагає TLV або фіксації зміщень базових полів", 11, NEG, "middle", bold=True))

    # Квадрант 4: v2 -> v2 (Повна функціональність)
    x4, y4 = ox + col_w, oy + row_h
    f.append(rect(x4 + 6, y4 + 6, col_w - 12, row_h - 12, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(x4 + col_w / 2, y4 + 32, "Сумісність v2 ↔ v2 (Повний функціонал)", 13, INK, "middle", bold=True))
    f.append(text(x4 + col_w / 2, y4 + 58, "• Передаються всі нові поля і прапорці", 11.5, INK, "middle"))
    f.append(text(x4 + col_w / 2, y4 + 78, "• Максимальна інформативність каналу", 11.5, INK, "middle"))
    f.append(text(x4 + col_w / 2, y4 + 104, "Стан мережі після 100% оновлення парку", 11, FIELD, "middle", bold=True))

    # Нижній висновок
    f.append(line(40, H - 42, W - 40, H - 42, color=MUTED, sw=1, dash="4,4"))
    f.append(text(W / 2, H - 18,
                  "Порушення прямої сумісності ламає старі пристрої в полі; порушення зворотної — блокує оновлення сервера.",
                  11.5, POS, "middle", bold=True))

    render(os.path.join(IMG, "evolution-compatibility-matrix.svg"), W, H, *f)


# ── 2. Еволюція позиційної структури: додавання полів у хвіст ──────────────────
def fig_fixed_struct_extension():
    W, H = 880, 430
    f = []

    f.append(text(W / 2, 28, "Еволюція фіксованої структури: розширення в хвіст і відсікання",
                  17, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "збереження позицій полів v1.0 та ініціалізація нових полів значеннями за замовчуванням",
                  12, MUTED, "middle", italic=True))

    # Схема пакету v1.0
    y_v1 = 90
    f.append(text(75, y_v1 + 18, "Пакет v1.0", 12, INK, "end", bold=True))
    f.append(text(75, y_v1 + 34, "(8 байтів)", 10.5, MUTED, "end"))

    # Блоки v1.0
    bx = 90
    # Header: Type, Len
    f.append(rect(bx, y_v1, 100, 50, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    f.append(text(bx + 50, y_v1 + 22, "Header [2B]", 11, INK, "middle", bold=True))
    f.append(text(bx + 50, y_v1 + 38, "Type=1, Len=8", 9.5, MUTED, "middle"))
    bx += 105

    # Field A: Voltage (2B)
    f.append(rect(bx, y_v1, 140, 50, fill="#e0f2fe", stroke=NEG, sw=1.5, rx=4))
    f.append(text(bx + 70, y_v1 + 22, "voltage_mv [2B]", 11, NEG, "middle", bold=True))
    f.append(text(bx + 70, y_v1 + 38, "Offset: 2..3", 9.5, MUTED, "middle"))
    bx += 145

    # Field B: Current (4B)
    f.append(rect(bx, y_v1, 180, 50, fill="#e0f2fe", stroke=NEG, sw=1.5, rx=4))
    f.append(text(bx + 90, y_v1 + 22, "current_ma [4B]", 11, NEG, "middle", bold=True))
    f.append(text(bx + 90, y_v1 + 38, "Offset: 4..7", 9.5, MUTED, "middle"))
    bx += 185

    # Схема пакету v1.1
    y_v2 = 190
    f.append(text(75, y_v2 + 18, "Пакет v1.1", 12, INK, "end", bold=True))
    f.append(text(75, y_v2 + 34, "(14 байтів)", 10.5, MUTED, "end"))

    bx2 = 90
    # Header: Type, Len
    f.append(rect(bx2, y_v2, 100, 50, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    f.append(text(bx2 + 50, y_v2 + 22, "Header [2B]", 11, INK, "middle", bold=True))
    f.append(text(bx2 + 50, y_v2 + 38, "Type=1, Len=14", 9.5, MUTED, "middle"))
    bx2 += 105

    # Field A: Voltage (2B) - незмінне
    f.append(rect(bx2, y_v2, 140, 50, fill="#e0f2fe", stroke=NEG, sw=1.5, rx=4))
    f.append(text(bx2 + 70, y_v2 + 22, "voltage_mv [2B]", 11, NEG, "middle", bold=True))
    f.append(text(bx2 + 70, y_v2 + 38, "Offset: 2..3 (Стале)", 9.5, MUTED, "middle"))
    bx2 += 145

    # Field B: Current (4B) - незмінне
    f.append(rect(bx2, y_v2, 180, 50, fill="#e0f2fe", stroke=NEG, sw=1.5, rx=4))
    f.append(text(bx2 + 90, y_v2 + 22, "current_ma [4B]", 11, NEG, "middle", bold=True))
    f.append(text(bx2 + 90, y_v2 + 38, "Offset: 4..7 (Стале)", 9.5, MUTED, "middle"))
    bx2 += 185

    # Field C: Temperature (2B) - нове поле
    f.append(rect(bx2, y_v2, 140, 50, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(bx2 + 70, y_v2 + 22, "+ temp_c [2B]", 11, FIELD, "middle", bold=True))
    f.append(text(bx2 + 70, y_v2 + 38, "Offset: 8..9 (Нове)", 9.5, MUTED, "middle"))
    bx2 += 145

    # Field D: State Flags (4B) - нове поле
    f.append(rect(bx2, y_v2, 160, 50, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(bx2 + 80, y_v2 + 22, "+ flags [4B]", 11, FIELD, "middle", bold=True))
    f.append(text(bx2 + 80, y_v2 + 38, "Offset: 10..13 (Нове)", 9.5, MUTED, "middle"))

    # Пояснювальні зв'язки (стрілки / правила)
    f.append(arrow(435, 145, 435, 185, color=FIELD, sw=1.8))
    f.append(text(445, 168, "базові зміщення не порушено", 10.5, FIELD, "start", bold=True))

    # Панель правил парсингу
    py = 275
    f.append(rect(80, py, 750, 105, fill="#fffbeb", stroke="#d97706", sw=1.4, rx=6))
    f.append(text(100, py + 22, "Алгоритм безпечного розбору змінної довжини у фіксованих структурах:", 12, "#92400e", "start", bold=True))
    f.append(text(100, py + 44, "1. Старий парсер читає v1.1: бере перші 8 байтів (розмір struct v1.0), а хвіст (байти 8..13) відкидає.", 11, INK, "start"))
    f.append(text(100, py + 64, "2. Новий парсер читає v1.0: бачить Len=8 < 14, копіює 8 байтів, а temp_c та flags ініціалізує дефолтами.", 11, INK, "start"))
    f.append(text(100, py + 86, "3. ЗАБОРОНЕНО змінювати зміщення або типи полів Offset 2..7 — це миттєво ламає старих клієнтів!", 11, POS, "start", bold=True))

    f.append(text(W / 2, H - 15,
                  "Правило: поля додаються виключно в кінець структури; парсер перевіряє фактичну довжину кадру.",
                  11.5, MUTED, "middle", italic=True))

    render(os.path.join(IMG, "fixed-struct-extension.svg"), W, H, *f)


# ── 3. Потік записів TLV: пропуск невідомих типів ─────────────────────────────
def fig_tlv_wire_stream():
    W, H = 880, 430
    f = []

    f.append(text(W / 2, 28, "Формат TLV: безпечний стрибок через невідомі поля",
                  17, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "самоописний потік пар «Тип-Довжина-Значення» дозволяє пропускати будь-які нові розширення",
                  12, MUTED, "middle", italic=True))

    # Схема TLV елементів
    y_tlv = 95
    cur_x = 45

    # Елемент 1: Відомий тег 0x01 (Температура)
    # T
    f.append(rect(cur_x, y_tlv, 45, 60, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=4))
    f.append(text(cur_x + 22.5, y_tlv + 25, "Tag", 10, "#9a3412", "middle", bold=True))
    f.append(text(cur_x + 22.5, y_tlv + 45, "0x01", 11, INK, "middle", bold=True))
    cur_x += 48
    # L
    f.append(rect(cur_x, y_tlv, 45, 60, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=4))
    f.append(text(cur_x + 22.5, y_tlv + 25, "Len", 10, "#9a3412", "middle", bold=True))
    f.append(text(cur_x + 22.5, y_tlv + 45, "2", 11, INK, "middle", bold=True))
    cur_x += 48
    # V
    f.append(rect(cur_x, y_tlv, 95, 60, fill="#ffedd5", stroke="#ea580c", sw=1.5, rx=4))
    f.append(text(cur_x + 47.5, y_tlv + 25, "Val: Temp", 11, "#9a3412", "middle", bold=True))
    f.append(text(cur_x + 47.5, y_tlv + 45, "23.48 °C", 9.5, INK, "middle"))
    cur_x += 105

    # Розділювач
    f.append(line(cur_x, y_tlv + 10, cur_x, y_tlv + 50, color=MUTED, sw=1.2, dash="3,3"))
    cur_x += 15

    # Елемент 2: НЕВІДОМИЙ тег 0x85 (Новий сенсор)
    x_unk_start = cur_x
    # T
    f.append(rect(cur_x, y_tlv, 45, 60, fill="#fecaca", stroke=POS, sw=1.8, rx=4))
    f.append(text(cur_x + 22.5, y_tlv + 25, "Tag", 10, POS, "middle", bold=True))
    f.append(text(cur_x + 22.5, y_tlv + 45, "0x85", 11, POS, "middle", bold=True))
    cur_x += 48
    # L
    f.append(rect(cur_x, y_tlv, 45, 60, fill="#fecaca", stroke=POS, sw=1.8, rx=4))
    f.append(text(cur_x + 22.5, y_tlv + 25, "Len", 10, POS, "middle", bold=True))
    f.append(text(cur_x + 22.5, y_tlv + 45, "6", 11, POS, "middle", bold=True))
    cur_x += 48
    # V
    f.append(rect(cur_x, y_tlv, 180, 60, fill="#fee2e2", stroke=POS, sw=1.8, rx=4))
    f.append(text(cur_x + 90, y_tlv + 25, "Val: Невідомий сенсор [6B]", 11, POS, "middle", bold=True))
    f.append(text(cur_x + 90, y_tlv + 45, "0xAA 0xBB 0xCC 0xDD 0xEE 0xFF", 9.5, MUTED, "middle"))
    cur_x += 190

    # Розділювач
    f.append(line(cur_x, y_tlv + 10, cur_x, y_tlv + 50, color=MUTED, sw=1.2, dash="3,3"))
    cur_x += 15

    # Елемент 3: Відомий тег 0x02 (Батарея)
    # T
    f.append(rect(cur_x, y_tlv, 45, 60, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=4))
    f.append(text(cur_x + 22.5, y_tlv + 25, "Tag", 10, "#9a3412", "middle", bold=True))
    f.append(text(cur_x + 22.5, y_tlv + 45, "0x02", 11, INK, "middle", bold=True))
    cur_x += 48
    # L
    f.append(rect(cur_x, y_tlv, 45, 60, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=4))
    f.append(text(cur_x + 22.5, y_tlv + 25, "Len", 10, "#9a3412", "middle", bold=True))
    f.append(text(cur_x + 22.5, y_tlv + 45, "1", 11, INK, "middle", bold=True))
    cur_x += 48
    # V
    f.append(rect(cur_x, y_tlv, 85, 60, fill="#ffedd5", stroke="#ea580c", sw=1.5, rx=4))
    f.append(text(cur_x + 42.5, y_tlv + 25, "Val: Batt", 11, "#9a3412", "middle", bold=True))
    f.append(text(cur_x + 42.5, y_tlv + 45, "94 %", 9.5, INK, "middle"))

    # Дуга стрибка парсера
    jump_x0 = x_unk_start + 45
    jump_x1 = cur_x - 90
    f.append(arrow(jump_x0, y_tlv - 10, jump_x1, y_tlv - 10, color=POS, sw=2.2))
    f.append(text((jump_x0 + jump_x1) / 2, y_tlv - 22,
                  "Стрибок: ptr += sizeof(Tag) + sizeof(Len) + Len (пропуск 8 байтів)",
                  11.5, POS, "middle", bold=True))

    # Статуси розбору знизу
    f.append(text(140, y_tlv + 80, "✔ 0x01: Розпізнано -> Temp=23.48°C", 11, FIELD, "middle", bold=True))
    f.append(text(410, y_tlv + 80, "⚠ 0x85: Невідомий тег -> Пропущено без збою", 11, POS, "middle", bold=True))
    f.append(text(725, y_tlv + 80, "✔ 0x02: Розпізнано -> Batt=94%", 11, FIELD, "middle", bold=True))

    # Нижній опис
    py = 220
    f.append(rect(45, py, 790, 150, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(65, py + 24, "Переваги та компроміси TLV у вбудованих системах:", 12.5, INK, "start", bold=True))
    f.append(text(65, py + 48, "1. Абсолютна пряма сумісність: приймач не потребує знання про майбутні сенсори; Len задає зміщення.", 11, INK, "start"))
    f.append(text(65, py + 70, "2. Відсутність динамічної пам'яті: цикл розбору ітерується вхідним буфером без жодного malloc().", 11, INK, "start"))
    f.append(text(65, py + 92, "3. Накладні витрати: кожен елемент вимагає 2 додаткові байти (Tag + Len). Для 1B даних це +200% оверхеду.", 11, MUTED, "start"))
    f.append(text(65, py + 114, "4. Вкладеність (Nested TLV): значенням тегу може бути інший потік TLV-записів (для складних об'єктів).", 11, INK, "start"))
    f.append(text(65, py + 136, "5. Валідація меж: перед переходом парсер перевіряє offset + tag_len <= buffer_size для захисту від атаки.", 11, POS, "start", bold=True))

    render(os.path.join(IMG, "tlv-wire-stream.svg"), W, H, *f)


# ── 4. Заголовок із контролем сумісності: мажорні версії та прапорці ──────────
def fig_version_header_schemes():
    W, H = 880, 470
    f = []

    f.append(text(W / 2, 28, "Заголовок кадру: мажорні версії та прапорці сумісності",
                  17, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "розподіл відповідальності між мажорною версією (ламана зміна) та прапорцями розширення",
                  12, MUTED, "middle", italic=True))

    # Розкладка байтів заголовка
    y_hdr = 85
    hx = 50

    # Magic [2B]
    f.append(rect(hx, y_hdr, 80, 50, fill="#e2e8f0", stroke=LINE, sw=1.4, rx=4))
    f.append(text(hx + 40, y_hdr + 22, "Magic [2B]", 11, INK, "middle", bold=True))
    f.append(text(hx + 40, y_hdr + 38, "0xAA55", 9.5, MUTED, "middle"))
    hx += 85

    # Ver Major [1B]
    f.append(rect(hx, y_hdr, 100, 50, fill="#fee2e2", stroke=POS, sw=1.8, rx=4))
    f.append(text(hx + 50, y_hdr + 22, "Ver Major [1B]", 11, POS, "middle", bold=True))
    f.append(text(hx + 50, y_hdr + 38, "Ламані зміни", 9.5, POS, "middle"))
    hx += 105

    # Ver Minor [1B]
    f.append(rect(hx, y_hdr, 100, 50, fill="#dbeafe", stroke=NEG, sw=1.5, rx=4))
    f.append(text(hx + 50, y_hdr + 22, "Ver Minor [1B]", 11, NEG, "middle", bold=True))
    f.append(text(hx + 50, y_hdr + 38, "Сумісні зміни", 9.5, NEG, "middle"))
    hx += 105

    # Incompat Flags [1B]
    f.append(rect(hx, y_hdr, 140, 50, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=4))
    f.append(text(hx + 70, y_hdr + 22, "Incompat Flags [1B]", 11, "#b45309", "middle", bold=True))
    f.append(text(hx + 70, y_hdr + 38, "Обов'язкові розширення", 9.5, "#b45309", "middle"))
    hx += 145

    # Compat Flags [1B]
    f.append(rect(hx, y_hdr, 130, 50, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(hx + 65, y_hdr + 22, "Compat Flags [1B]", 11, FIELD, "middle", bold=True))
    f.append(text(hx + 65, y_hdr + 38, "Опційні фічі", 9.5, FIELD, "middle"))
    hx += 135

    # Msg ID [2B]
    f.append(rect(hx, y_hdr, 90, 50, fill="#e2e8f0", stroke=LINE, sw=1.4, rx=4))
    f.append(text(hx + 45, y_hdr + 22, "Msg ID [2B]", 11, INK, "middle", bold=True))
    f.append(text(hx + 45, y_hdr + 38, "Тип пакета", 9.5, MUTED, "middle"))
    hx += 95

    # Payload Length [2B]
    f.append(rect(hx, y_hdr, 110, 50, fill="#e2e8f0", stroke=LINE, sw=1.4, rx=4))
    f.append(text(hx + 55, y_hdr + 22, "Length [2B]", 11, INK, "middle", bold=True))
    f.append(text(hx + 55, y_hdr + 38, "Розмір тіла", 9.5, MUTED, "middle"))

    # Блок-схема логіки валідації на приймачі
    y_flow = 160
    f.append(text(W / 2, y_flow + 15, "Диспетчеризація та перевірка сумісності під час прийому кадру:", 13, INK, "middle", bold=True))

    # Крок 1: Перевірка Ver Major
    bx1 = 60
    by1 = y_flow + 40
    f.append(rect(bx1, by1, 230, 80, fill="#fff1f2", stroke=POS, sw=1.5, rx=6))
    f.append(text(bx1 + 115, by1 + 24, "1. Перевірка Ver Major", 12, POS, "middle", bold=True))
    f.append(text(bx1 + 115, by1 + 45, "if (hdr.major != MY_MAJOR)", 11, INK, "middle"))
    f.append(text(bx1 + 115, by1 + 65, "-> Відкинути кадр (Drop)", 11, POS, "middle", bold=True))

    # Стрілка 1 -> 2
    f.append(arrow(bx1 + 230, by1 + 40, bx1 + 280, by1 + 40, color=FIELD, sw=2))
    f.append(text(bx1 + 255, by1 + 32, "OK", 10, FIELD, "middle", bold=True))

    # Крок 2: Перевірка Incompat Flags
    bx2 = 320
    by2 = by1
    f.append(rect(bx2, by2, 250, 80, fill="#fefce8", stroke="#d97706", sw=1.5, rx=6))
    f.append(text(bx2 + 125, by2 + 24, "2. Incompat Flags Mask", 12, "#b45309", "middle", bold=True))
    f.append(text(bx2 + 125, by2 + 45, "if (hdr.incompat & ~SUPPORTED)", 11, INK, "middle"))
    f.append(text(bx2 + 125, by2 + 65, "-> Відкинути (невідома вимога)", 11, POS, "middle", bold=True))

    # Стрілка 2 -> 3
    f.append(arrow(bx2 + 250, by2 + 40, bx2 + 300, by2 + 40, color=FIELD, sw=2))
    f.append(text(bx2 + 275, by2 + 32, "OK", 10, FIELD, "middle", bold=True))

    # Крок 3: Перевірка Compat Flags
    bx3 = 600
    by3 = by1
    f.append(rect(bx3, by3, 230, 80, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(bx3 + 115, by3 + 24, "3. Compat Flags Mask", 12, FIELD, "middle", bold=True))
    f.append(text(bx3 + 115, by3 + 45, "ignore = hdr.compat & ~SUPPORTED", 11, INK, "middle"))
    f.append(text(bx3 + 115, by3 + 65, "-> Прийняти і розібрати тіло", 11, FIELD, "middle", bold=True))

    # Пояснення внизу
    py = 310
    f.append(rect(50, py, 780, 130, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(70, py + 22, "Семантика прапорців розширення (модель MAVLink v2 / QUIC):", 12, INK, "start", bold=True))
    f.append(text(70, py + 44, "• Incompat Flags: встановлюється, якщо розширення обов'язкове (наприклад, шифрування/підпис).", 11, INK, "start"))
    f.append(text(70, py + 62, "  Якщо приймач не знає цього біта — він зобов'язаний скинути пакет.", 11, MUTED, "start"))
    f.append(text(70, py + 82, "• Compat Flags: опційні розширення (діагностичний таймстемп, додаткова мітка пріоритету).", 11, INK, "start"))
    f.append(text(70, py + 100, "  Приймач, який не знає цього біта, спокійно обробляє корисні дані й ігнорує опцію.", 11, MUTED, "start"))
    f.append(text(70, py + 120, "• Мажорна версія (Major) змінюється лише при фундаментальній несумісності фреймінгу.", 10.5, POS, "start", bold=True))

    render(os.path.join(IMG, "version-header-schemes.svg"), W, H, *f)


def main():
    fig_compatibility_matrix()
    fig_fixed_struct_extension()
    fig_tlv_wire_stream()
    fig_version_header_schemes()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
