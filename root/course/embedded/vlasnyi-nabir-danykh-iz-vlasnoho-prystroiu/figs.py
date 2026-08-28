# -*- coding: utf-8 -*-
"""Фігури до теми «Власний набір даних із власного пристрою: запис, розмітка, баланс».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Архітектура безперервного логування сенсорних даних ────────────────────
def fig_sensor_logging_pipeline():
    """Архітектура збору даних на мікроконтролері: апаратні сенсори через DMA,
    апаратна мітка часу, подвійний буфер у RAM, бінарний фрейм і фоновий запис
    на SD-карту із захистом від затримок Flash GC."""
    W, H = 880, 440
    f = [text(W / 2, 28, "Архітектура безперервного логування сенсорних даних на МК", size=16, bold=True)]

    # Рівень 1: Апаратні джерела
    f.append(text(W / 2, 60, "1. Апаратні джерела потоків (DMA без переривання процесора)", size=12, color=MUTED, bold=True))
    sources = [
        ("Акселерометр / IMU", "SPI DMA @ 1.6 кГц\n(вібрація, кути)", NEG),
        ("Струмовий шунт", "ADC DMA @ 10 кГц\n(струм, напруга)", FIELD),
        ("Мікрофон", "I2S DMA @ 16 кГц\n(акустичний шуми)", POS),
        ("Апаратний таймер", "TIM 32-bit @ 1 МГц\n(мікросекунди us)", INK),
    ]
    sw, sh, s_gap, sx0 = 180, 52, 24, 46
    for i, (title_s, sub_s, col) in enumerate(sources):
        x = sx0 + i * (sw + s_gap)
        f.append(rect(x, 75, sw, sh, fill=BG, stroke=col, sw=1.6, rx=5))
        f.append(text(x + sw / 2, 92, title_s, size=11, bold=True, color=col))
        f.append(mtext(x + sw / 2, 107, sub_s, size=9.5, color=INK))
        # стрілки вниз
        f.append(arrow(x + sw / 2, 127, x + sw / 2, 155))

    # Рівень 2: Двобуферна система в RAM (Ping-Pong)
    f.append(text(W / 2, 170, "2. Подвійний буфер у RAM (Ping-Pong) та пакування фреймів", size=12, color=MUTED, bold=True))
    
    # Блок Буфер А
    f.append(rect(60, 185, 340, 65, fill="#f0f7ff", stroke=NEG, sw=1.6, rx=6))
    f.append(text(230, 205, "Буфер A (наповнюється від DMA)", size=12, bold=True, color=NEG))
    f.append(text(230, 225, "Сенсори пишуть сюди в реальному часі", size=10.5, color=INK))
    f.append(text(230, 240, "Апаратний таймстемп + лічильник seq_num", size=9.5, color=MUTED))

    # Перемикач
    f.append(rect(430, 195, 30, 45, fill=BG, stroke=LINE, sw=1.2, rx=4))
    f.append(text(445, 222, "⇄", size=18, color=POS, bold=True))

    # Блок Буфер Б
    f.append(rect(480, 185, 340, 65, fill="#f2faf5", stroke=FIELD, sw=1.6, rx=6))
    f.append(text(650, 205, "Буфер B (скидається на накопичувач)", size=12, bold=True, color=FIELD))
    f.append(text(650, 225, "Готовий блок передається у фонову задачу", size=10.5, color=INK))
    f.append(text(650, 240, "Розмір кратний сектору Flash (512 / 4096 байт)", size=9.5, color=MUTED))

    # Рівень 3: Структура бінарного фрейму
    f.append(arrow(W / 2, 252, W / 2, 275))
    f.append(text(W / 2, 290, "3. Структура бінарного фрейму (без текстового оверхеду)", size=12, color=MUTED, bold=True))
    
    fields = [
        ("Magic (2B)", "0xAA55"),
        ("Stream ID (1B)", "0x01 = IMU"),
        ("Seq Num (4B)", "0..4294967295"),
        ("Timestamp (8B)", "Час у мкс"),
        ("Payload (N байт)", "Сирі відліки LSB"),
        ("CRC32 (4B)", "Контроль цілісності"),
    ]
    fx, fy, fw, fh = 46, 302, 126, 42
    for i, (fn, fd) in enumerate(fields):
        bx = fx + i * (fw + 5)
        f.append(rect(bx, fy, fw, fh, fill="#fafbfc", stroke=LINE, sw=1.2, rx=4))
        f.append(text(bx + fw / 2, fy + 16, fn, size=10, bold=True, color=INK))
        f.append(text(bx + fw / 2, fy + 32, fd, size=9, color=MUTED))

    # Рівень 4: Накопичувач і захист від затримок
    f.append(arrow(W / 2, 346, W / 2, 368))
    f.append(rect(100, 370, 680, 52, fill=BG, stroke=POS, sw=1.8, rx=6))
    f.append(text(440, 390, "4. Накопичувач (SD-карта / eMMC) та черга запису", size=12, bold=True, color=POS))
    f.append(text(440, 408, "Фоновий потік поглинає затримки Flash GC (до 250 мс) за рахунок RAM-черги без втрати пакетів", size=10, color=INK))

    return render(os.path.join(IMG, "sensor-logging-pipeline.svg"), W, H, *f)


# ── 2. Проблема дисбалансу класів та One-Class підхід ─────────────────────────
def fig_class_imbalance_solutions():
    """Порівняння дисбалансу класів (парадокс точності 99.9%) та рішень:
    активний збір дефектів на стендах, One-Class SVM і автоенкодери норми."""
    W, H = 880, 410
    f = [text(W / 2, 28, "Дисбаланс класів: парадокс точності та методи вирішення", size=16, bold=True)]

    # Ліва колонка: Проблема дисбалансу та парадокс точності
    f.append(rect(40, 55, 370, 335, fill="#fff9f8", stroke=POS, sw=1.5, rx=7))
    f.append(text(225, 80, "Проблема: 99.9% норми проти 0.1% поломок", size=12.5, bold=True, color=POS))
    
    # Стрічка часу даних
    f.append(rect(55, 98, 340, 32, fill="#eaf7ed", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(195, 118, "Штатна робота (годинами / днями)", size=10.5, bold=True, color=FIELD))
    f.append(rect(365, 98, 30, 32, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    f.append(text(380, 118, "💥", size=14))

    f.append(text(225, 150, "Парадокс точності (Accuracy Paradox):", size=11, bold=True, color=INK))
    f.append(rect(55, 162, 340, 58, fill=BG, stroke=LINE, sw=1, rx=5))
    f.append(text(225, 180, "Наївний класифікатор вивчив одне правило:", size=10, color=MUTED))
    f.append(text(225, 196, "«Завжди відповідай: ШТАТНО»", size=11, bold=True, color=POS))
    f.append(text(225, 212, "Формальна точність: 99.9% | Виявлено аварій: 0%", size=9.5, bold=True, color=POS))

    f.append(text(225, 240, "Наслідки для пристрою:", size=11, bold=True, color=INK))
    points_left = [
        "• Класифікатор сліпий до рідкісних катастроф",
        "• Метрика Accuracy втрачає будь-який сенс",
        "• Необхідні Precision/Recall, F1 та PR-AUC",
    ]
    f.append(mtext(65, 260, points_left, size=10, color=INK, anchor="start", lh=1.4))

    f.append(fitbox(55, 325, 340, 48,
                    "Висновок: звичайний багатокласовий класифікатор\nне працює на сирих потоках телеметрії",
                    size=10, bold=True, fill="#fef0ee", stroke=POS))

    # Права колонка: Інженерні рішення
    f.append(rect(450, 55, 390, 335, fill="#f4f8fb", stroke=NEG, sw=1.5, rx=7))
    f.append(text(645, 80, "Три інженерні стратегії подолання", size=12.5, bold=True, color=NEG))

    solutions = [
        ("1. Активний збір крайових випадків",
         "• Випробувальні стенди, перевантаження\n• Штучні дефекти: надпил підшипника, дисбаланс",
         FIELD),
        ("2. Однокласове моделювання (One-Class)",
         "• One-Class SVM / Isolation Forest\n• Описують межу нормальної поведінки",
         NEG),
        ("3. Автоенкодер реконструкції сигналу",
         "• Вчиться тільки на 100% здоровій роботі\n• Аномалія = висока похибка відновлення MSE(x, x̂)",
         POS),
    ]

    for i, (st, sd, sc) in enumerate(solutions):
        sy = 100 + i * 85
        f.append(rect(465, sy, 360, 72, fill=BG, stroke=sc, sw=1.4, rx=5))
        f.append(text(645, sy + 18, st, size=11, bold=True, color=sc))
        f.append(mtext(475, sy + 38, sd, size=9.5, color=INK, anchor="start", lh=1.35))

    f.append(fitbox(465, 358, 360, 24, "Головний підхід в Edge AI: навчатися на нормі, ловити відхилення",
                    size=10, bold=True, fill=BG, stroke=LINE))

    return render(os.path.join(IMG, "class-imbalance-solutions.svg"), W, H, *f)


# ── 3. Розбіжність розподілів (Data Drift) та аугментація ─────────────────────
def fig_sensor_data_drift():
    """Чому лабораторна модель ламається в полі (температурний дрейф нуля,
    вібрації, люфти) та як аугментація сенсорних рядів відновлює надійність."""
    W, H = 880, 420
    f = [text(W / 2, 28, "Розбіжність розподілів (Data Drift) та аугментація сенсорів", size=16, bold=True)]

    # Лівий блок: Дрейф розподілів
    f.append(rect(40, 55, 380, 345, fill="#fffaf5", stroke="#e67e22", sw=1.5, rx=7))
    f.append(text(230, 80, "Чому лабораторна модель відмовляє в полі", size=12, bold=True, color="#d35400"))

    # Схема розподілів (кола або еліпси)
    f.append(circle(150, 160, 48, fill="#e8f4fc", stroke=NEG, sw=1.6))
    f.append(text(150, 154, "Лабораторія", size=11, bold=True, color=NEG))
    f.append(text(150, 172, "+22°C, новий стенд", size=9.5, color=MUTED))

    f.append(arrow(202, 160, 252, 160, color="#d35400", sw=2))
    f.append(text(227, 148, "Дрейф", size=10.5, bold=True, color="#d35400"))

    f.append(circle(310, 160, 54, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(310, 154, "Реальне поле", size=11, bold=True, color=POS))
    f.append(text(310, 172, "-15°C..+55°C, знос", size=9.5, color=MUTED))

    drift_reasons = [
        "1. Температурний дрейф: зміщення нуля (offset)",
        "   та чутливості кремнієвих MEMS / АЦП",
        "2. Механічний знос: люфти валу, ослаблення",
        "   кріплень, зміна резонансних частот",
        "3. Електричні завади: ШІМ моторів, просадка АКБ",
    ]
    f.append(mtext(55, 235, drift_reasons, size=10, color=INK, anchor="start", lh=1.35))

    f.append(fitbox(55, 340, 350, 45,
                    "Наслідок: вхідний вектор виходить за межі\nнавченого простору → хибні спрацювання",
                    size=10, bold=True, fill="#fef5ee", stroke="#e67e22"))

    # Правий блок: Сенсорна аугментація
    f.append(rect(450, 55, 390, 345, fill="#f2faf5", stroke=FIELD, sw=1.5, rx=7))
    f.append(text(645, 80, "Аугментація часових рядів сенсорів", size=12, bold=True, color=FIELD))

    aug_methods = [
        ("Дрожання (Jittering)", "Додавання гаусового шуму та поодиноких сплесків", NEG),
        ("Масштабування (Scaling)", "Множення амплітуди на випадковий фактор [0.85 .. 1.15]", FIELD),
        ("Часовий зсув (Warping)", "Локальне розтягування/стискання за шкалою часу", POS),
        ("Дрейф зміщення (Offset Drift)", "Штучне лінійне зміщення нуля датчика за температурою", "#8e44ad"),
    ]

    for i, (at, ad, ac) in enumerate(aug_methods):
        ay = 100 + i * 58
        f.append(rect(465, ay, 360, 48, fill=BG, stroke=ac, sw=1.3, rx=5))
        f.append(text(475, ay + 18, at, size=10.5, bold=True, color=ac, anchor="start"))
        f.append(text(475, ay + 36, ad, size=9.5, color=INK, anchor="start"))

    f.append(rect(465, 340, 360, 45, fill=BG, stroke=FIELD, sw=1.5, rx=5))
    f.append(text(645, 358, "Результат: розширена область генералізації", size=10.5, bold=True, color=FIELD))
    f.append(text(645, 374, "Модель покриває весь діапазон польових температур і вібрацій", size=9.5, color=MUTED))

    return render(os.path.join(IMG, "sensor-data-drift.svg"), W, H, *f)


if __name__ == "__main__":
    fig_sensor_logging_pipeline()
    fig_class_imbalance_solutions()
    fig_sensor_data_drift()
    print("All figures generated successfully.")
