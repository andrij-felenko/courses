# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. four-questions-cycle: Чотири фундаментальні питання моделювання загроз ──
def fig_four_questions_cycle():
    W, H = 820, 360
    p = []

    # Центральний заголовок/хаб
    p.append(circle(410, 180, 52, fill="#f8fafc", stroke=LINE, sw=1.5))
    p.append(text(410, 174, "Цикл", size=13, color=INK, bold=True))
    p.append(text(410, 192, "Шостака", size=12, color=MUTED))

    # Крок 1: Що ми будуємо? (Вгорі)
    p.append(rect(270, 20, 280, 75, fill="#f0f7ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(410, 44, "1. Що ми будуємо?", size=13, color=NEG, bold=True))
    p.append(text(410, 64, "Декомпозиція: DFD, процеси, межі довіри", size=11, color=INK))
    p.append(text(410, 80, "Потоки даних і сховища активів", size=10, color=MUTED))

    # Крок 2: Що може піти не так? (Праворуч)
    p.append(rect(540, 140, 260, 80, fill="#fdf2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(670, 164, "2. Що може піти не так?", size=13, color=POS, bold=True))
    p.append(text(670, 186, "Ідентифікація загроз: STRIDE", size=11, color=INK))
    p.append(text(670, 204, "Дерева атак (Attack Trees)", size=10, color=MUTED))

    # Крок 3: Що ми з цим робимо? (Внизу)
    p.append(rect(270, 265, 280, 75, fill="#f0fbf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(410, 289, "3. Що ми з цим робимо?", size=13, color=FIELD, bold=True))
    p.append(text(410, 310, "Контрзаходи: зменшити, усунути,", size=11, color=INK))
    p.append(text(410, 326, "передати або свідомо прийняти ризик", size=10, color=MUTED))

    # Крок 4: Чи добре ми впоралися? (Ліворуч)
    p.append(rect(20, 140, 260, 80, fill="#fdf8ed", stroke="#d97706", sw=1.8, rx=8))
    p.append(text(150, 164, "4. Чи добре впоралися?", size=13, color="#d97706", bold=True))
    p.append(text(150, 186, "Валідація повноти, QA-тести,", size=11, color=INK))
    p.append(text(150, 204, "ретроспектива та оновлення моделі", size=10, color=MUTED))

    # Стрілки по колу між блоками
    p.append(arrow(550, 60, 640, 135, color=LINE, sw=2.0))
    p.append(arrow(640, 225, 550, 300, color=LINE, sw=2.0))
    p.append(arrow(270, 300, 180, 225, color=LINE, sw=2.0))
    p.append(arrow(180, 135, 270, 60, color=LINE, sw=2.0))

    render(os.path.join(OUT, "four-questions-cycle.svg"), W, H, *p,
           title="Чотири фундаментальні питання моделювання загроз")


# ── 2. dfd-stride-mapping: Елементи DFD та матриця загроз STRIDE ─────────────
def fig_dfd_stride_mapping():
    W, H = 840, 380
    p = []

    # Заголовок
    p.append(text(420, 25, "Відповідність категорій загроз STRIDE типам елементів діаграми потоків даних (DFD)", size=13, color=INK, bold=True))

    # Елемент 1: Зовнішня сутність (External Entity)
    p.append(rect(30, 50, 230, 140, fill="#ffffff", stroke=INK, sw=1.8, rx=4))
    p.append(text(145, 75, "Зовнішня сутність", size=12, color=INK, bold=True))
    p.append(text(145, 93, "(External Entity: користувач, API)", size=10, color=MUTED))
    p.append(line(45, 105, 245, 105, color=MUTED, sw=1.0))
    p.append(text(145, 125, "[S] Spoofing (Підробка)", size=11, color=POS, bold=True))
    p.append(text(145, 145, "[R] Repudiation (Відмова)", size=11, color=POS, bold=True))
    p.append(text(145, 170, "Вхід за межі контролю системи", size=10, color=MUTED, italic=True))

    # Елемент 2: Процес (Process)
    p.append(rect(295, 50, 250, 140, fill="#fdf2f2", stroke=POS, sw=1.8, rx=24))
    p.append(text(420, 75, "Процес (Process)", size=12, color=POS, bold=True))
    p.append(text(420, 93, "(Веб-сервер, сервіс, воркер)", size=10, color=MUTED))
    p.append(line(310, 105, 530, 105, color=MUTED, sw=1.0))
    p.append(text(420, 125, "Всі 6 категорій STRIDE:", size=11, color=INK, bold=True))
    p.append(text(420, 145, "Spoofing · Tampering · Repudiation", size=10, color=POS))
    p.append(text(420, 165, "Info Disclosure · DoS · Elev. Privilege", size=10, color=POS))

    # Елемент 3: Сховище даних (Data Store)
    p.append(rect(580, 50, 230, 140, fill="#ffffff", stroke=INK, sw=1.8, rx=0))
    p.append(line(580, 58, 810, 58, color=INK, sw=1.8))
    p.append(line(580, 182, 810, 182, color=INK, sw=1.8))
    p.append(text(695, 78, "Сховище даних", size=12, color=INK, bold=True))
    p.append(text(695, 95, "(Data Store: БД, файл, S3)", size=10, color=MUTED))
    p.append(line(595, 107, 795, 107, color=MUTED, sw=1.0))
    p.append(text(695, 127, "[T] Tampering (Зміна)", size=11, color=POS, bold=True))
    p.append(text(695, 147, "[I] Info Disclosure (Витік)", size=11, color=POS, bold=True))
    p.append(text(695, 167, "[D] DoS · [R] Repudiation", size=11, color=POS, bold=True))

    # Потік даних між ними
    p.append(arrow(260, 110, 290, 110, color=FIELD, sw=2.2))
    p.append(arrow(545, 110, 575, 110, color=FIELD, sw=2.2))

    # Елемент 4: Потік даних (Data Flow)
    p.append(rect(30, 220, 360, 135, fill="#f0f7ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(210, 245, "Потік даних (Data Flow)", size=12, color=NEG, bold=True))
    p.append(text(210, 265, "HTTP, gRPC, TCP-сокет, IPC-канал", size=10, color=MUTED))
    p.append(line(45, 277, 375, 277, color=MUTED, sw=1.0))
    p.append(text(210, 298, "[T] Tampering (Модифікація пакетів на льоту)", size=10, color=POS))
    p.append(text(210, 318, "[I] Info Disclosure (Перехоплення, sniffing)", size=10, color=POS))
    p.append(text(210, 338, "[D] Denial of Service (Глушіння, флуд)", size=10, color=POS))

    # Елемент 5: Межа довіри (Trust Boundary)
    p.append(rect(450, 220, 360, 135, fill="#fdf8ed", stroke="#d97706", sw=1.8, rx=8))
    p.append(text(630, 245, "Межа довіри (Trust Boundary)", size=12, color="#d97706", bold=True))
    p.append(text(630, 265, "Розділяє зони з різними рівнями прав", size=10, color=MUTED))
    p.append(line(465, 277, 795, 277, color=MUTED, sw=1.0))
    p.append(text(630, 298, "Перетин вимагає суворої автентифікації", size=10, color=INK, bold=True))
    p.append(text(630, 318, "Обов'язкова валідація та санітизація входу", size=10, color=INK))
    p.append(text(630, 338, "Тут концентрується максимальний ризик", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "dfd-stride-mapping.svg"), W, H, *p,
           title="Відповідність категорій STRIDE елементам DFD")


# ── 3. attack-tree-structure: Структура дерева атак (Attack Tree) ───────────
def fig_attack_tree_structure():
    W, H = 840, 420
    p = []

    # Корінь: Головна мета атаки
    p.append(rect(270, 15, 300, 65, fill="#fdf2f2", stroke=POS, sw=2.0, rx=8))
    p.append(text(420, 38, "[OR] Несанкціоноване списання коштів", size=12, color=POS, bold=True))
    p.append(text(420, 60, "Цільова вигода нападника: 1 000 000 грн", size=10, color=MUTED))

    # З'єднання корінь -> проміжні вузли
    p.append(line(420, 80, 420, 110, color=LINE, sw=1.5))
    p.append(line(190, 110, 650, 110, color=LINE, sw=1.5))
    p.append(arrow(190, 110, 190, 135, color=LINE, sw=1.5))
    p.append(arrow(650, 110, 650, 135, color=LINE, sw=1.5))

    # Гілка 1 (Ліворуч): AND-вузол "Компрометація платіжного API"
    p.append(rect(50, 140, 280, 70, fill="#f0f7ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(190, 163, "[AND] Пряма підробка API-запиту", size=12, color=NEG, bold=True))
    p.append(text(190, 183, "Потрібне одночасне виконання гілок", size=10, color=MUTED))
    p.append(text(190, 198, "Вартість: C1 + C2 | Ймовірність: P1 · P2", size=9, color=FIELD, bold=True))

    # Гілка 2 (Праворуч): AND-вузол "Злам бази даних"
    p.append(rect(510, 140, 280, 70, fill="#f0f7ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(650, 163, "[AND] Ін'єкція та обхід WAF", size=12, color=NEG, bold=True))
    p.append(text(650, 183, "Потрібне одночасне виконання гілок", size=10, color=MUTED))
    p.append(text(650, 198, "Вартість: C3 + C4 | Ймовірність: P3 · P4", size=9, color=FIELD, bold=True))

    # З'єднання для лівого AND-вузла
    p.append(line(190, 210, 190, 235, color=LINE, sw=1.5))
    p.append(line(95, 235, 285, 235, color=LINE, sw=1.5))
    p.append(arrow(95, 235, 95, 255, color=LINE, sw=1.5))
    p.append(arrow(285, 235, 285, 255, color=LINE, sw=1.5))

    # Листки лівої гілки
    p.append(rect(15, 260, 160, 95, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(95, 282, "1.1. Викрасти API-ключ", size=10, color=INK, bold=True))
    p.append(text(95, 302, "Фішинг розробника", size=9, color=MUTED))
    p.append(text(95, 322, "Вартість: 20 000 грн", size=9, color=POS))
    p.append(text(95, 340, "Ймовірність: 0.15", size=9, color=FIELD))

    p.append(rect(205, 260, 160, 95, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(285, 282, "1.2. Обійти IP-фільтр", size=10, color=INK, bold=True))
    p.append(text(285, 302, "BGP-spoofing / VPN", size=9, color=MUTED))
    p.append(text(285, 322, "Вартість: 15 000 грн", size=9, color=POS))
    p.append(text(285, 340, "Ймовірність: 0.30", size=9, color=FIELD))

    # З'єднання для правого AND-вузла
    p.append(line(650, 210, 650, 235, color=LINE, sw=1.5))
    p.append(line(555, 235, 745, 235, color=LINE, sw=1.5))
    p.append(arrow(555, 235, 555, 255, color=LINE, sw=1.5))
    p.append(arrow(745, 235, 745, 255, color=LINE, sw=1.5))

    # Листки правої гілки
    p.append(rect(475, 260, 160, 95, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(555, 282, "2.1. Знайти SQLi", size=10, color=INK, bold=True))
    p.append(text(555, 302, "Фаззинг ендпоінтів", size=9, color=MUTED))
    p.append(text(555, 322, "Вартість: 5 000 грн", size=9, color=POS))
    p.append(text(555, 340, "Ймовірність: 0.05", size=9, color=FIELD))

    p.append(rect(665, 260, 160, 95, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(745, 282, "2.2. Обійти WAF-правила", size=10, color=INK, bold=True))
    p.append(text(745, 302, "Обфускація payload", size=9, color=MUTED))
    p.append(text(745, 322, "Вартість: 10 000 грн", size=9, color=POS))
    p.append(text(745, 340, "Ймовірність: 0.20", size=9, color=FIELD))

    # Підсумкова плашка
    p.append(rect(120, 375, 600, 35, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(420, 397, "Агрегація: для OR обирається шлях із найменшою вартістю / найвищою ймовірністю", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "attack-tree-structure.svg"), W, H, *p,
           title="Структура та обчислення дерева атак")


# ── 4. dread-matrix-evaluation: Модель кількісної оцінки ризиків DREAD ──────
def fig_dread_matrix_evaluation():
    W, H = 820, 340
    p = []

    # Заголовок
    p.append(text(410, 25, "Шкала кількісної оцінки ризику DREAD та рівні критичності", size=13, color=INK, bold=True))

    # 5 компонентів DREAD у ряд
    cols = [
        ("D", "Damage", "Збитки", "Повний злам системи", POS),
        ("R", "Reproducibility", "Відтворюваність", "Працює щоразу", POS),
        ("E", "Exploitability", "Легкість зламу", "Досить браузера", POS),
        ("A", "Affected Users", "Уражені особи", "Всі користувачі", POS),
        ("D", "Discoverability", "Легкість пошуку", "Публічний баг", POS),
    ]

    x_start = 30
    w_box = 144
    gap = 10

    for i, (letter, name_en, name_ua, desc, clr) in enumerate(cols):
        bx = x_start + i * (w_box + gap)
        p.append(rect(bx, 50, w_box, 130, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
        p.append(rect(bx, 50, w_box, 32, fill="#f4f6f8", stroke=INK, sw=1.5, rx=6))
        p.append(text(bx + w_box/2, 72, f"{letter} — {name_en}", size=11, color=INK, bold=True))
        p.append(text(bx + w_box/2, 102, name_ua, size=11, color=clr, bold=True))
        p.append(text(bx + w_box/2, 125, desc, size=9, color=MUTED))
        p.append(text(bx + w_box/2, 155, "Бали: 1 .. 10", size=10, color=FIELD, bold=True))

    # Формула агрегації
    p.append(rect(30, 195, 760, 50, fill="#f0f7ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(410, 225, "Підсумковий рейтинг ризику = ( Damage + Reproducibility + Exploitability + Affected + Discoverability ) / 5", size=11, color=NEG, bold=True))

    # Рівні критичності (High / Medium / Low)
    p.append(rect(30, 260, 240, 65, fill="#fdf2f2", stroke=POS, sw=1.8, rx=6))
    p.append(text(150, 285, "Високий (7.0 – 10.0)", size=12, color=POS, bold=True))
    p.append(text(150, 305, "Негайне виправлення (блокер релізу)", size=9, color=INK))

    p.append(rect(290, 260, 240, 65, fill="#fdf8ed", stroke="#d97706", sw=1.8, rx=6))
    p.append(text(410, 285, "Середній (4.0 – 6.9)", size=12, color="#d97706", bold=True))
    p.append(text(410, 305, "Виправлення в плановому спринті", size=9, color=INK))

    p.append(rect(550, 260, 240, 65, fill="#f0fbf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(670, 285, "Низький (1.0 – 3.9)", size=12, color=FIELD, bold=True))
    p.append(text(670, 305, "Моніторинг або свідоме прийняття", size=9, color=INK))

    render(os.path.join(OUT, "dread-matrix-evaluation.svg"), W, H, *p,
           title="Шкала кількісної оцінки ризику DREAD")


if __name__ == "__main__":
    fig_four_questions_cycle()
    fig_dfd_stride_mapping()
    fig_attack_tree_structure()
    fig_dread_matrix_evaluation()
    print("Всі фігури успішно згенеровано.")
