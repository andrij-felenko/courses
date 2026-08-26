# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. flash-power-loss-corruption: Фізика пошкодження Flash при обриві живлення ──
def fig_flash_power_loss_corruption():
    W, H = 920, 520
    p = []

    # Загальний заголовок
    p.append(rect(15, 15, 890, 490, fill="#ffffff", stroke=LINE, sw=1.5, rx=10))
    p.append(text(460, 42, "Фізика пошкодження Flash-комірки при раптовому обриві живлення", size=15, color=INK, bold=True))

    # Ліва колонка: Нормальне програмування vs Обрив живлення
    p.append(rect(35, 70, 410, 390, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(240, 98, "Механізм інжекції заряду (Помпа 12–18 В)", size=13, color=INK, bold=True))

    # Схема комірки з плаваючим затвором
    # Control Gate
    p.append(rect(90, 125, 300, 32, fill="#e2e8f0", stroke=INK, sw=1.5, rx=4))
    p.append(text(240, 146, "Керівний затвор (Control Gate) [V_gate = 12–18 В]", size=11, color=INK, bold=True))

    # Оксид 1
    p.append(rect(110, 162, 260, 12, fill="#fef3c7", stroke="#d97706", sw=1))
    p.append(text(240, 171, "Міжзатворний діелектрик (ONO)", size=9, color="#92400e"))

    # Floating Gate
    p.append(rect(90, 178, 300, 32, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    p.append(text(240, 199, "Плавучий затвор (Floating Gate) / Пастка заряду", size=11, color="#1e40af", bold=True))

    # Тунельний оксид
    p.append(rect(110, 215, 260, 14, fill="#fee2e2", stroke=POS, sw=1))
    p.append(text(240, 226, "Тунельний оксид SiO2 (товщина 8–10 нм)", size=9, color=POS))

    # Підкладка / Канал
    p.append(rect(90, 234, 300, 45, fill="#f1f5f9", stroke=INK, sw=1.5, rx=4))
    p.append(text(135, 260, "Витік (S)", size=10.5, color=INK, bold=True))
    p.append(text(240, 260, "Провідний канал кремнію (p-Si)", size=10.5, color=MUTED))
    p.append(text(345, 260, "Стік (D)", size=10.5, color=INK, bold=True))

    # Стрілка колапсу помпи заряду
    p.append(arrow(240, 290, 240, 325, color=POS, sw=2))
    p.append(text(240, 340, "⚡ Раптове знеструмлення під час циклу t_prog (0.2–3 мс)", size=10.5, color=POS, bold=True))
    p.append(text(240, 358, "Помпа заряду миттєво втрачає напругу 15 В → 0 В", size=10, color=INK))
    p.append(text(240, 375, "Тільки частина електронів подолала потенційний бар'єр", size=10, color=INK))
    p.append(text(240, 395, "Заряд на затворі: Q_real << Q_target", size=10.5, color=POS, bold=True))
    p.append(text(240, 415, "Порушення (Disturb) на сусідніх лініях слів через спад напруги", size=9.5, color=MUTED))
    p.append(text(240, 435, "Результат: пошкодження всього 4 КБ сектора/сторінки", size=10, color=POS, bold=True))

    # Права колонка: Розподіл порогової напруги V_th та маргінальний стан
    p.append(rect(470, 70, 415, 390, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(677, 98, "Розподіл порогової напруги V_th комірок", size=13, color=INK, bold=True))

    # Осі графіка
    p.append(line(500, 320, 860, 320, color=INK, sw=1.5))
    p.append(line(500, 320, 500, 140, color=INK, sw=1.5))
    p.append(text(860, 335, "V_th (В)", size=10.5, color=INK, bold=True))
    p.append(text(490, 135, "N (кількість комірок)", size=10, color=INK, bold=True))

    # Дзвін 1: Стертий стан '1'
    p.append('<path d="M 515 320 Q 560 160 605 320" fill="#dcfce7" stroke="#15803d" stroke-width="2"/>')
    p.append(text(560, 220, "Стертий стан '1'", size=11, color="#15803d", bold=True))
    p.append(text(560, 238, "Низький V_th", size=9.5, color="#166534"))

    # Дзвін 2: Записаний стан '0'
    p.append('<path d="M 735 320 Q 780 160 825 320" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>')
    p.append(text(780, 220, "Записаний стан '0'", size=11, color="#1e40af", bold=True))
    p.append(text(780, 238, "Високий V_th", size=9.5, color="#1d4ed8"))

    # Дзвін 3: Маргінальний / Пошкоджений стан через обрив
    p.append('<path d="M 620 320 Q 670 200 720 320" fill="#fee2e2" stroke="#c0392b" stroke-width="2" stroke-dasharray="4 2"/>')
    p.append(text(670, 245, "Маргінальний стан", size=10.5, color=POS, bold=True))
    p.append(text(670, 262, "(Сміття / Floating V_th)", size=9.5, color=POS))

    # Лінія напруги зчитування V_read
    p.append(line(670, 320, 670, 145, color=POS, sw=1.5, dash="3 3"))
    p.append(text(670, 140, "Поріг зчитування V_read", size=10, color=POS, bold=True))

    # Пояснення наслідків під графіком
    p.append(rect(485, 345, 385, 100, fill="#ffffff", stroke=MUTED, sw=1, rx=6))
    p.append(text(677, 365, "Наслідки маргінального заряду на кристалі:", size=10.5, color=INK, bold=True))
    p.append(text(677, 383, "1. Зчитування повертає випадкові 0 або 1 залежно від T° та шуму", size=9.5, color=INK))
    p.append(text(677, 401, "2. Вбудований апаратний ECC фіксує невиправну помилку (UECC)", size=9.5, color=POS, bold=True))
    p.append(text(677, 419, "3. Напівстертий блок блокує майбутні операції запису без Erase", size=9.5, color=INK))
    p.append(text(677, 437, "4. Пристрій перезапускається з пошкодженими метаданими", size=9.5, color=POS, bold=True))

    # Нижній висновок
    b, _, _ = textbox(460, 485, "Обрив живлення в процесі програмування Flash залишає комірки з неповним зарядом: порогова напруга потрапляє в зону невизначеності, перетворюючи сектор на випадкове сміття.",
                      size=10.5, fill="#f8fafc", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "flash-power-loss-corruption.svg"), W, H, *p)

# ── 2. atomic-ab-pingpong: Подвійна буферизація A/B Ping-Pong ──
def fig_atomic_ab_pingpong():
    W, H = 920, 480
    p = []

    p.append(rect(15, 15, 890, 450, fill="#ffffff", stroke=LINE, sw=1.5, rx=10))
    p.append(text(460, 40, "Архітектура транзакційного оновлення A/B Ping-Pong (Double Buffering)", size=15, color=INK, bold=True))

    # Слот A
    p.append(rect(45, 75, 380, 315, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(235, 102, "СЕКТОР A (Фізичний блок 0)", size=13, color="#166534", bold=True))
    p.append(text(235, 120, "Стан: АКТИВНИЙ / ВАЛІДНИЙ (Committed)", size=10.5, color=FIELD, bold=True))

    # Поля структури сектора A
    fields_a = [
        ("Magic: 0x54534F4C ('LOST')", "#ffffff", INK),
        ("Sequence / Generation: 42", "#dcfce7", "#166534"),
        ("State Flag: COMMITTED (0x00)", "#ffffff", INK),
        ("Payload: Key-Value Data (256 B)", "#ffffff", INK),
        ("Payload CRC32: 0x8F4A21C3 (OK)", "#dcfce7", "#166534"),
        ("Commit Marker: 0xA55A1234 (Valid)", "#dcfce7", "#166534"),
    ]
    y = 135
    for ftext, fbg, fcol in fields_a:
        p.append(rect(65, y, 340, 26, fill=fbg, stroke=MUTED, sw=1, rx=4))
        p.append(text(235, y + 17, ftext, size=10.5, color=fcol, bold=True))
        y += 31

    p.append(rect(65, 325, 340, 50, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    p.append(text(235, 345, "✓ Читач використовує дані зі слота A", size=10.5, color="#166534", bold=True))
    p.append(text(235, 363, "Generation = 42 є найновішим валідним", size=9.5, color=MUTED))

    # Слот B
    p.append(rect(495, 75, 380, 315, fill="#fef2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(685, 102, "СЕКТОР B (Фізичний блок 1)", size=13, color=POS, bold=True))
    p.append(text(685, 120, "Стан: ПОШКОДЖЕНО ОБРИВОМ (Corrupted)", size=10.5, color=POS, bold=True))

    # Поля структури сектора B
    fields_b = [
        ("Magic: 0x54534F4C ('LOST')", "#ffffff", INK),
        ("Sequence / Generation: 43", "#fee2e2", POS),
        ("State Flag: ALLOCATED (0x01)", "#ffffff", INK),
        ("Payload: [Частковий запис... сміття]", "#fee2e2", POS),
        ("Payload CRC32: 0xFFFFFFFF (Mismatch!)", "#fee2e2", POS),
        ("Commit Marker: 0xFFFFFFFF (Не записано)", "#ffffff", MUTED),
    ]
    y = 135
    for ftext, fbg, fcol in fields_b:
        p.append(rect(515, y, 340, 26, fill=fbg, stroke=MUTED, sw=1, rx=4))
        p.append(text(685, y + 17, ftext, size=10.5, color=fcol, bold=True))
        y += 31

    p.append(rect(515, 325, 340, 50, fill="#ffffff", stroke=POS, sw=1, rx=4))
    p.append(text(685, 345, "⚡ Обрив живлення під час запису слота B", size=10.5, color=POS, bold=True))
    p.append(text(685, 363, "CRC32 не збігається → Слот B відкидається", size=9.5, color=POS))

    # Центральна стрілка перемикання транзакцій
    p.append(arrow(430, 225, 490, 225, color=POS, sw=2))
    p.append(text(460, 212, "Write", size=10, color=POS, bold=True))
    p.append(text(460, 245, "Gen 43", size=9.5, color=MUTED))

    # Нижній блок відновлення (Recovery State)
    p.append(rect(45, 405, 830, 48, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=6))
    p.append(text(460, 424, "Алгоритм відновлення при старті: Скануємо обидва слоти → Перевіряємо CRC32 та Commit Marker", size=11, color="#1e40af", bold=True))
    p.append(text(460, 442, "Слот B визнано невалідним → Безпечний відкат до слота A (Gen 42). Нуль втрачених метаданих.", size=10, color=INK))

    render(os.path.join(OUT, "atomic-ab-pingpong.svg"), W, H, *p)

# ── 3. littlefs-cow-tree: Copy-on-Write дерево у LittleFS vs FAT ──
def fig_littlefs_cow_tree():
    W, H = 920, 500
    p = []

    p.append(rect(15, 15, 890, 470, fill="#ffffff", stroke=LINE, sw=1.5, rx=10))
    p.append(text(460, 40, "Архітектурне порівняння стійкості: FAT (In-Place) проти LittleFS (Copy-on-Write)", size=15, color=INK, bold=True))

    # Лівий блок: FAT Катастрофа при обриві живлення
    p.append(rect(35, 70, 410, 365, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(240, 95, "Традиційна FAT (In-Place оновлення)", size=13, color=POS, bold=True))
    p.append(text(240, 115, "Фіксовані сектори таблиці розміщення", size=10, color=MUTED))

    # Вузли FAT
    p.append(rect(55, 135, 370, 50, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(text(240, 155, "Каталог: DirEntry (Фіксований сектор 2)", size=11, color=INK, bold=True))
    p.append(text(240, 172, "Вказівник на перший кластер = 10", size=9.5, color=MUTED))

    p.append(rect(55, 205, 370, 55, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text(240, 225, "Таблиця FAT (Сектор 1): 10 → 11 → [ОБРИВ!]", size=11, color=POS, bold=True))
    p.append(text(240, 245, "⚡ Кластер 12 не додано в ланцюг через знеструмлення", size=9.5, color=POS))

    p.append(rect(55, 280, 370, 50, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(text(240, 300, "Кластери даних на диску: [10] [11] [12 - Orphan]", size=11, color=INK, bold=True))
    p.append(text(240, 318, "Кластер 12 записаний, але таблиця FAT пошкоджена", size=9.5, color=MUTED))

    p.append(rect(55, 345, 370, 75, fill="#ffffff", stroke=POS, sw=1, rx=4))
    p.append(text(240, 365, "Наслідки для файлової системи FAT:", size=10.5, color=POS, bold=True))
    p.append(text(240, 383, "• Висячі кластери (Lost clusters) та пошкоджене дерево", size=9.5, color=INK))
    p.append(text(240, 401, "• Перехресні посилання між файлами (Cross-linked files)", size=9.5, color=INK))
    p.append(text(240, 415, "• Необхідність тривалого сканування fsck / chkdsk при старті", size=9, color=MUTED))

    # Правий блок: LittleFS Copy-on-Write та Metadata Pairs
    p.append(rect(475, 70, 410, 365, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(680, 95, "LittleFS (Copy-on-Write + Metadata Pairs)", size=13, color="#166534", bold=True))
    p.append(text(680, 115, "Атомарні пари блоків каталогу та Append-Only теги", size=10, color=MUTED))

    # Вузли LittleFS
    p.append(rect(495, 135, 370, 60, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(680, 155, "Metadata Pair каталогу (Блоки 0 та 1)", size=11, color="#166534", bold=True))
    p.append(text(680, 172, "Блок 0: Версія N (Стара, але 100% ціла)", size=9.5, color=INK))
    p.append(text(680, 187, "Блок 1: Версія N+1 (Нова, у процесі запису)", size=9.5, color="#15803d", bold=True))

    p.append(rect(495, 210, 370, 55, fill="#dcfce7", stroke=FIELD, sw=1, rx=4))
    p.append(text(680, 230, "Дерево блоків файлу (CTZ Skip-List):", size=11, color="#166534", bold=True))
    p.append(text(680, 248, "Новий блок даних 12 виділено в новому секторі Flash", size=9.5, color=INK))

    p.append(rect(495, 280, 370, 50, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    p.append(text(680, 300, "Атомарний комміт через інверсію біта ревізії:", size=11, color=INK, bold=True))
    p.append(text(680, 318, "Зміна вказівника на Блок 1 відбувається одним записом тегу", size=9.5, color="#166534", bold=True))

    p.append(rect(495, 345, 370, 75, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    p.append(text(680, 365, "Переваги LittleFS при раптовому обриві живлення:", size=10.5, color="#166534", bold=True))
    p.append(text(680, 383, "• Старий стан (Блок 0) залишається неушкодженим", size=9.5, color=INK))
    p.append(text(680, 401, "• Нульовий час монтування: відкат без прогону сканування", size=9.5, color=INK))
    p.append(text(680, 415, "• Вбудоване вирівнювання зносу та ізоляція битих блоків", size=9, color=MUTED))

    # Нижній висновок
    b, _, _ = textbox(460, 455, "LittleFS ніколи не перезаписує існуючі метадані на місці. Якщо живлення зникає під час дописування файлу, система миттєво повертається до попереднього узгодженого стану пари блоків.",
                      size=10.5, fill="#f8fafc", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "littlefs-cow-tree.svg"), W, H, *p)

# ── 4. pvd-brownout-timeline: Часова шкала PVD, BOR та енергетичний бюджет ──
def fig_pvd_brownout_timeline():
    W, H = 920, 500
    p = []

    p.append(rect(15, 15, 890, 470, fill="#ffffff", stroke=LINE, sw=1.5, rx=10))
    p.append(text(460, 38, "Апаратний захист від обриву живлення: пороги PVD, BOR та аварійне вікно", size=15, color=INK, bold=True))

    # Вісь напруги та часу
    p.append(line(70, 380, 850, 380, color=INK, sw=1.8))
    p.append(line(70, 380, 70, 70, color=INK, sw=1.8))
    p.append(text(850, 400, "Час t (мілісекунди)", size=11, color=INK, bold=True))
    p.append(text(60, 65, "V_DD (В)", size=11, color=INK, bold=True))

    # Горизонтальні рівні напруги
    # 3.3 В (Номінал)
    p.append(line(70, 100, 840, 100, color=FIELD, sw=1.2, dash="4 3"))
    p.append(text(120, 92, "3.3 В — Робоча напруга V_nom", size=10, color="#15803d", bold=True))

    # 2.9 В (Поріг PVD)
    p.append(line(70, 160, 840, 160, color="#d97706", sw=1.5, dash="4 3"))
    p.append(text(135, 152, "2.9 В — Поріг переривання PVD (Level 5)", size=10.5, color="#b45309", bold=True))

    # 2.5 В (Поріг BOR)
    p.append(line(70, 250, 840, 250, color=POS, sw=1.5, dash="4 3"))
    p.append(text(130, 242, "2.5 В — Апаратне скидання Brownout (BOR Level 2)", size=10.5, color=POS, bold=True))

    # 1.8 В (Мінімум логіки)
    p.append(line(70, 340, 840, 340, color=MUTED, sw=1, dash="2 2"))
    p.append(text(125, 332, "1.8 В — Межа працездатності логічних вентилів", size=9.5, color=MUTED))

    # Крива розряду конденсатора
    curve_pts = "M 70 100 L 200 100 Q 280 110 340 160 Q 440 220 540 250 Q 640 310 740 370"
    p.append('<path d="%s" fill="none" stroke="#2563eb" stroke-width="3"/>' % curve_pts)

    # Точка 1: Обрив живлення
    p.append(circle(200, 100, 5, fill=POS, stroke="#ffffff", sw=1.5))
    p.append(text(200, 82, "⚡ Обрив джерела", size=10, color=POS, bold=True))

    # Точка 2: Спрацьовування PVD
    p.append(circle(340, 160, 5, fill="#d97706", stroke="#ffffff", sw=1.5))
    p.append(text(340, 142, "🚨 Спрацював PVD ISR", size=10, color="#b45309", bold=True))

    # Точка 3: Спрацьовування BOR
    p.append(circle(540, 250, 5, fill=POS, stroke="#ffffff", sw=1.5))
    p.append(text(540, 235, "🛑 BOR Reset", size=10, color=POS, bold=True))

    # Аварійне вікно скидання (Текстовий блок без рамки, що перекривається)
    p.append(text(440, 280, "АВАРІЙНЕ ВІКНО Δt_hold (1–5 мс)", size=11, color="#92400e", bold=True))
    p.append(text(440, 298, "Живлення від C_holdup", size=9.5, color=INK))

    # Послідовність дій у перериванні PVD (у правому вільному кутку)
    actions = [
        "1. Заборона нових тривалих транзакцій",
        "2. Очікування фінішу поточної сторінки",
        "3. Запис CRC32 та комміт-маркера",
        "4. Переведення Flash у Deep Power Down",
    ]
    p.append(rect(570, 70, 305, 92, fill="#fffbeb", stroke="#d97706", sw=1.2, rx=6))
    p.append(text(722, 90, "Дії в обробнику PVD_IRQHandler():", size=10.5, color="#b45309", bold=True))
    ay = 108
    for act in actions:
        p.append(text(585, ay, act, size=9.5, color=INK, anchor="start"))
        ay += 16

    # Нижній висновок
    b, _, _ = textbox(460, 445, "Конденсатор C_holdup підтримує напругу вище порогу BOR протягом часу Δt_hold = C·(V_PVD - V_BOR)/I_load. Це дає ядру змогу коректно завершити активну сторінку Flash до апаратного скидання.",
                      size=10.5, fill="#f8fafc", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "pvd-brownout-timeline.svg"), W, H, *p)

def main():
    fig_flash_power_loss_corruption()
    fig_atomic_ab_pingpong()
    fig_littlefs_cow_tree()
    fig_pvd_brownout_timeline()
    print("All figures generated successfully.")

if __name__ == "__main__":
    main()
