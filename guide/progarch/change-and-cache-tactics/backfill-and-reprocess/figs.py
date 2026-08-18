# -*- coding: utf-8 -*-
"""Фігури до теми «Backfill і reprocessing»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_keyset_vs_offset():
    """Порівняння пагінації за OFFSET та курсором (Keyset Pagination) під час бекфілу."""
    W, H = 960, 440
    frags = []

    # ── Лівий блок: Наївна пагінація за OFFSET ──
    frags.append(rect(30, 40, 435, 360, fill="#fdf2f2", stroke=POS, sw=2.0, rx=10))
    frags.append(text(247, 75, "OFFSET Пагінація: O(N²) сканування", size=14, bold=True, color=POS))
    frags.append(text(247, 98, "SELECT * FROM events ORDER BY id LIMIT 1000 OFFSET 1000000", size=10, color=INK))

    # Схема зчитування файлу/індексу
    frags.append(rect(55, 125, 385, 45, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(247, 145, "Прочитати та ВІДКИНУТИ 1 000 000 рядків", size=11, bold=True, color=POS))
    frags.append(text(247, 160, "Високий IOPS, виснаження Buffer Pool", size=10, color=MUTED))

    frags.append(arrow(247, 170, 247, 195, color=POS, sw=2.0))

    frags.append(rect(55, 195, 385, 45, fill="#fde8e8", stroke=POS, sw=1.5, rx=6))
    frags.append(text(247, 215, "Повернути лише 1 000 рядків", size=11, bold=True, color=INK))
    frags.append(text(247, 230, "Час запиту зростає з кожною наступною сторінкою", size=10, color=MUTED))

    # Ризики
    frags.append(rect(55, 260, 385, 120, fill="#ffffff", stroke=POS, sw=1.0, rx=6))
    frags.append(text(75, 285, "• Тривалі Read-locks на сторінках індексу", size=11, color=INK, anchor="start"))
    frags.append(text(75, 305, "• Пропущені або дубльовані записи при паралельному INSERT", size=11, color=INK, anchor="start"))
    frags.append(text(75, 325, "• Деградація продуктивності бази для живих OLTP запитів", size=11, color=INK, anchor="start"))
    frags.append(text(75, 345, "• Ризик падаючого OOM або таймауту з'єднання", size=11, bold=True, color=POS, anchor="start"))

    # ── Правий блок: Курсорна пагінація (Keyset Pagination) ──
    frags.append(rect(495, 40, 435, 360, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=10))
    frags.append(text(712, 75, "Keyset Пагінація: O(1) B-Tree точковий пошук", size=14, bold=True, color=FIELD))
    frags.append(text(712, 98, "WHERE id > 1000000 ORDER BY id ASC LIMIT 1000", size=10, color=INK))

    # Схема точкового пошуку
    frags.append(rect(520, 125, 385, 45, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(712, 145, "Прямий стрибок за індексом B-Tree до id = 1000001", size=11, bold=True, color=FIELD))
    frags.append(text(712, 160, "Нульове сканування застарілих даних", size=10, color=MUTED))

    frags.append(arrow(712, 170, 712, 195, color=FIELD, sw=2.0))

    frags.append(rect(520, 195, 385, 45, fill="#d4edda", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(712, 215, "Миттєва вибірка 1 000 рядків", size=11, bold=True, color=INK))
    frags.append(text(712, 230, "Постійний час відповіді незалежно від глибини історії", size=10, color=MUTED))

    # Переваги
    frags.append(rect(520, 260, 385, 120, fill="#ffffff", stroke=FIELD, sw=1.0, rx=6))
    frags.append(text(540, 285, "• Стабільне короткочасне блокування чанку", size=11, color=INK, anchor="start"))
    frags.append(text(540, 305, "• Стійкість до паралельного додавання нових рядків", size=11, color=INK, anchor="start"))
    frags.append(text(540, 325, "• Просте створення чекпоінтів (last_processed_id)", size=11, color=INK, anchor="start"))
    frags.append(text(540, 345, "• Передбачуване навантаження на I/O СУБД", size=11, bold=True, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "keyset-vs-offset.svg"), W, H, *frags,
           title="Порівняння OFFSET та Keyset (Cursor) пагінації під час бекфілу")


def fig_dual_write_backfill_timeline():
    """Хронологія фаз Dual-Write Backfill та вирішення конфліктів."""
    W, H = 960, 440
    frags = []

    phases = [
        ("1. Expand & Dual-Write", "Живий трафік пише у v1 і v2", "Нові записи отримують обидві версії", "#eef2f7", INK),
        ("2. Backfill (Історія)", "Фоновий worker заповнює v2", "Тільки для WHERE v2 IS NULL", "#fff3cd", POS),
        ("3. Shadow Validation", "Порівняння v1 та v2 в фоні", "Темне читання (Diff Engine)", "#e8f4f8", "#1b6ec2"),
        ("4. Contract & Cleanup", "Перемикання читання на v2", "Видалення v1 та Dual-Write", "#eafaf0", FIELD),
    ]

    x_start = 25
    box_w = 215
    gap = 18
    y_top = 40

    for i, (title_str, main_str, note_str, fill_col, border_col) in enumerate(phases):
        x = x_start + i * (box_w + gap)
        frags.append(rect(x, y_top, box_w, 130, fill=fill_col, stroke=border_col, sw=1.8, rx=8))
        frags.append(text(x + box_w / 2, y_top + 30, title_str, size=12, bold=True, color=border_col))
        frags.append(text(x + box_w / 2, y_top + 60, main_str, size=11, bold=True, color=INK))
        frags.append(line(x + 10, y_top + 80, x + box_w - 10, y_top + 80, color=MUTED, sw=1, dash="4,4"))
        frags.append(text(x + box_w / 2, y_top + 105, note_str, size=10, color=MUTED))

        if i < len(phases) - 1:
            frags.append(arrow(x + box_w, y_top + 65, x + box_w + gap, y_top + 65, color=border_col, sw=2.0))

    # ── Нижній детальній блок розв'язання гонок ──
    frags.append(rect(25, 200, 910, 210, fill="#fafafa", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(480, 225, "Механіка запобігання перезапису живого трафіку фоновим бекфілом", size=13, bold=True, color=INK))

    # Ліва колонка: Живий трафік
    frags.append(rect(55, 245, 410, 145, fill="#ffffff", stroke="#1b6ec2", sw=1.2, rx=6))
    frags.append(text(260, 268, "Потік 1: Активний OLTP трафік (Dual-Write)", size=12, bold=True, color="#1b6ec2"))
    frags.append(text(75, 295, "1. Користувач створює/оновлює запис", size=11, color=INK, anchor="start"))
    frags.append(text(75, 315, "2. Код пише `v1_val` та обчислений `v2_val`", size=11, color=INK, anchor="start"))
    frags.append(text(75, 335, "3. Встановлює `updated_at = NOW()` та `v2_status = 'READY'`", size=11, color=INK, anchor="start"))
    frags.append(text(75, 360, "Вищий пріоритет: свіжі дані не перекриваються бекфілом", size=10, bold=True, color=FIELD, anchor="start"))

    # Права колонка: Фоновий бекфіл
    frags.append(rect(495, 245, 410, 145, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    frags.append(text(700, 268, "Потік 2: Фоновий Backfill Worker", size=12, bold=True, color=POS))
    frags.append(text(515, 295, "1. Вибирає історичний чанк `WHERE v2_val IS NULL`", size=11, color=INK, anchor="start"))
    frags.append(text(515, 315, "2. Обчислює `v2_val` для давнього запису", size=11, color=INK, anchor="start"))
    frags.append(text(515, 335, "3. UPDATE `... WHERE id = X AND v2_val IS NULL`", size=11, color=INK, anchor="start"))
    frags.append(text(515, 360, "Атомарна умова `IS NULL` відкидає конфліктний перезапис", size=10, bold=True, color=POS, anchor="start"))

    render(os.path.join(IMG, "dual-write-backfill-timeline.svg"), W, H, *frags,
           title="Фази Dual-Write Backfill та вирішення конфліктів із живим трафіком")


def fig_stream_reprocess_shadow():
    """Схема повторної обробки подій у Kafka через Shadow Consumer Group."""
    W, H = 960, 440
    frags = []

    # ── Event Stream (Kafka Topic) ──
    frags.append(rect(40, 180, 200, 100, fill="#fdf6e3", stroke=POS, sw=2.0, rx=8))
    frags.append(text(140, 210, "Event Stream", size=14, bold=True, color=POS))
    frags.append(text(140, 230, "Topic: telemetry-events", size=11, color=INK))
    frags.append(text(140, 255, "Незимовний журнал (Retention)", size=10, color=MUTED))

    # ── Гілка 1: Live Consumer (v1) ──
    frags.append(arrow(240, 210, 340, 120, color="#1b6ec2", sw=2.0))
    frags.append(text(285, 150, "Live Offset", size=11, bold=True, color="#1b6ec2"))

    frags.append(rect(340, 60, 240, 110, fill="#e8f4f8", stroke="#1b6ec2", sw=1.8, rx=8))
    frags.append(text(460, 85, "Live Worker Group (v1)", size=13, bold=True, color="#1b6ec2"))
    frags.append(text(460, 108, "Обробка поточних подій", size=11, color=INK))
    frags.append(text(460, 130, "Зовнішні side-effects: УВІМКНЕНО", size=10, bold=True, color=POS))

    frags.append(arrow(580, 115, 680, 115, color="#1b6ec2", sw=1.8))
    frags.append(rect(680, 85, 230, 60, fill="#ffffff", stroke="#1b6ec2", sw=1.2, rx=6))
    frags.append(text(795, 110, "Основна БД / Read Model v1", size=12, bold=True, color=INK))
    frags.append(text(795, 128, "Обслуговує користувачів", size=10, color=MUTED))

    # ── Гілка 2: Shadow Consumer (Reprocessing v2) ──
    frags.append(arrow(240, 250, 340, 320, color=FIELD, sw=2.0))
    frags.append(text(285, 300, "Reset Offset=0", size=11, bold=True, color=FIELD))

    frags.append(rect(340, 270, 240, 120, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(460, 295, "Shadow Worker Group (v2)", size=13, bold=True, color=FIELD))
    frags.append(text(460, 318, "Replay всієї історії з початку", size=11, color=INK))
    frags.append(line(355, 335, 565, 335, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(460, 355, "Side-Effect Suppressor (No-Op)", size=11, bold=True, color=POS))
    frags.append(text(460, 372, "Email / Webhooks ЗАБЛОКОВАНО", size=10, color=POS))

    frags.append(arrow(580, 330, 680, 330, color=FIELD, sw=1.8))
    frags.append(rect(680, 300, 230, 60, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(795, 325, "Shadow БД / Read Model v2", size=12, bold=True, color=INK))
    frags.append(text(795, 343, "Новий формат / Новий алгоритм", size=10, color=MUTED))

    # Звірка та підключення
    frags.append(arrow(795, 300, 795, 145, color=FIELD, sw=1.5))
    frags.append(text(795, 225, "Switchover після наздоганяння (Catch-up)", size=10, bold=True, color=FIELD))

    render(os.path.join(IMG, "stream-reprocess-shadow.svg"), W, H, *frags,
           title="Повторна обробка подій через Shadow Consumer Group та придушення side-effects")


if __name__ == "__main__":
    fig_keyset_vs_offset()
    fig_dual_write_backfill_timeline()
    fig_stream_reprocess_shadow()
    print("Figures generated successfully.")
