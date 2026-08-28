# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми plutanyna-rezhymiv (Плутанина режимів)."""

import os
import sys

# Підключаємо svgkit з кореневої папки scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_mental_model_desync():
    """Фігура 1: Розсинхронізація ментальної моделі оператора та реального стану автопілота."""
    w, h = 900, 400
    frags = []

    # Заголовок блоків
    frags.append(rect(20, 20, 400, 360, fill="#f8fafc", stroke=NEG, sw=2, rx=8))
    frags.append(text(220, 48, "МЕНТАЛЬНА МОДЕЛЬ ОПЕРАТОРА", size=14, color=NEG, bold=True))
    frags.append(text(220, 68, "(Що людина думає про стан апарата)", size=12, color=MUTED, italic=True))

    frags.append(rect(480, 20, 400, 360, fill="#fdfbf7", stroke=POS, sw=2, rx=8))
    frags.append(text(680, 48, "РЕАЛЬНИЙ СТАН АВТОПІЛОТА", size=14, color=POS, bold=True))
    frags.append(text(680, 68, "(Фактичний режим прошивки борту)", size=12, color=MUTED, italic=True))

    # Стан оператора
    tb1, _, _ = textbox(220, 115, "Режим: PosHold (GPS)\n«Відпускаю стік — апарат сам загальмує»", size=12, pad=8, fill="#eaf0fd", stroke=NEG)
    frags.append(tb1)

    tb2, _, _ = textbox(220, 200, "Вхід оператора:\nСтік Roll/Pitch у центрі (0, 0)\nОчікування: нульова швидкість", size=12, pad=8, fill="#ffffff", stroke=LINE)
    frags.append(tb2)

    tb3, _, _ = textbox(220, 305, "Automation Surprise:\n«Чому він летить у дерево?!\nВін не слухається!»", size=12, pad=8, fill="#fdecea", stroke=POS, bold=True)
    frags.append(tb3)

    # Реальний стан автопілота
    tb4, _, _ = textbox(680, 115, "Режим: AltHold (Втрата GPS)\n«Стік у центрі = тримати кут 0°\n(горизонтальний дрейф за вітром)»", size=12, pad=8, fill="#fef3c7", stroke="#d97706")
    frags.append(tb4)

    tb5, _, _ = textbox(680, 200, "Фактична дія регулятора:\nPID крену тримає 0°, але швидкість 12 м/с\nАпарат несе інерція та порив вітру", size=12, pad=8, fill="#ffffff", stroke=LINE)
    frags.append(tb5)

    tb6, _, _ = textbox(680, 305, "Фізичний наслідок:\nЗіткнення з перешкодою\nчерез хибні дії оператора", size=12, pad=8, fill="#fee2e2", stroke=POS, bold=True)
    frags.append(tb6)

    # Прихована подія посередині
    frags.append(line(420, 115, 480, 115, color=POS, sw=2, dash="4,4"))
    frags.append(text(450, 100, "GPS Lost", size=11, color=POS, bold=True))
    frags.append(text(450, 135, "Silent Fallback", size=10, color=MUTED))

    # Стрілки взаємодії
    frags.append(arrow(220, 150, 220, 170, color=LINE, sw=1.5))
    frags.append(arrow(680, 150, 680, 170, color=LINE, sw=1.5))
    frags.append(arrow(220, 245, 220, 270, color=POS, sw=1.8))
    frags.append(arrow(680, 245, 680, 270, color=POS, sw=1.8))

    # Розрив між ментальним очікуванням і реальністю
    frags.append(line(360, 305, 540, 305, color=POS, sw=2.5, dash="6,4"))
    frags.append(text(450, 295, "РОЗСИНХРОН", size=12, color=POS, bold=True))

    out_path = os.path.join(IMG_DIR, "mental-model-desync.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)


def fig_mode_annunciation_hierarchy():
    """Фігура 2: Багаторівнева ієрархія зворотної анонсації (Feedback Annunciation)."""
    w, h = 820, 360
    frags = []

    # Заголовок
    frags.append(text(410, 25, "СИСТЕМА БАГАТОКАНАЛЬНОЇ АНОНСАЦІЇ РЕЖИМІВ (FEEDBACK ANNUNCIATION)", size=14, bold=True))

    # 4 канали: OSD/HUD, Voice/Audio, Haptic, FMA Callout
    cols = [
        ("1. ВІЗУАЛЬНИЙ (HUD / OSD)", ["Великий банер зміни режиму", "Колірний індикатор стану:", "Зелений — Повний GPS/PosHold", "Жовтий — Деградація/AltHold", "Червоний — Ручний/Аварійний", "Мерехтіння 2.5 с при переході"], 110, "#eff6ff", NEG),
        ("2. АКУСТИЧНИЙ (АУДІО)", ["Голосовий синтез події:", "«Warning: Alt-Hold Mode»", "Характерний тональний звук", "Різні патерни для деградації", "та аварійного повернення", "Пріоритет над телеметрією"], 310, "#f0fdf4", FIELD),
        ("3. ТАКТИЛЬНИЙ (HAPTIC)", ["Вібрація корпусу пульта", "Подвійний імпульс: відкат", "Безперервний зумер: аварія", "Миттєве відчуття в руках", "Працює при втраті зорового", "контакту з екраном"], 510, "#fefce8", "#ca8a04"),
        ("4. ПРОЦЕДУРНИЙ (FMA)", ["Обов'язкове підтвердження", "Голосовий виголос пілота:", "«Mode Changed to AltHold»", "Дисципліна двох операторів", "Зняття когнітивного", "тунелювання"], 710, "#faf5ff", "#9333ea")
    ]

    for title, items, cx, bg_col, border_col in cols:
        frags.append(rect(cx - 90, 50, 180, 290, fill=bg_col, stroke=border_col, sw=1.8, rx=6))
        frags.append(text(cx, 75, title, size=11, color=border_col, bold=True))
        frags.append(line(cx - 80, 88, cx + 80, 88, color=border_col, sw=1))
        
        y_cursor = 110
        for it in items:
            bold = ("«" in it or "Зелений" in it or "Жовтий" in it or "Червоний" in it)
            col = POS if "Червоний" in it else FIELD if "Зелений" in it else ("#b45309" if "Жовтий" in it else INK)
            frags.append(text(cx, y_cursor, it, size=10, color=col, bold=bold))
            y_cursor += 26

    out_path = os.path.join(IMG_DIR, "mode-annunciation-hierarchy.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)


def fig_mode_consistency_monitor():
    """Фігура 3: Архітектура програмного монітора узгодженості дій оператора та стану."""
    w, h = 840, 360
    frags = []

    frags.append(text(420, 25, "АРХІТЕКТУРА МОНІТОРА УЗГОДЖЕНОСТІ (MODE CONSISTENCY MONITOR)", size=14, bold=True))

    # Лівий блок: Джерела даних (Входи)
    frags.append(rect(20, 55, 210, 280, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(125, 80, "ВХІДНІ СИГНАЛИ", size=12, color=INK, bold=True))
    frags.append(line(35, 92, 215, 92, color=MUTED, sw=1))

    tb_in1, _, _ = textbox(125, 125, "RC Стіки пілота\n(Roll, Pitch, Yaw, Throttle)", size=11, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_in1)

    tb_in2, _, _ = textbox(125, 195, "Активний режим польоту\n(PosHold, AltHold, RTH, Auto)", size=11, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_in2)

    tb_in3, _, _ = textbox(125, 275, "Вектор руху та сенсори\n(Швидкість EKF, Вітер, GPS)", size=11, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_in3)

    # Центральний блок: Алгоритм виявлення аномалій
    frags.append(rect(270, 55, 300, 280, fill="#eff6ff", stroke=NEG, sw=2, rx=6))
    frags.append(text(420, 80, "ЯДРО МОНІТОРА (DISCREPANCY DETECTOR)", size=12, color=NEG, bold=True))
    frags.append(line(285, 92, 555, 92, color=NEG, sw=1))

    tb_core1, _, _ = textbox(420, 130, "1. Боротьба з автопілотом (Stick Fighting):\nСтік тисне проти траєкторії RTH > T_hold", size=10, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_core1)

    tb_core2, _, _ = textbox(420, 205, "2. Суперечливий газ (Throttle Inversion):\nНульовий газ при спробі знизитись в RTH", size=10, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_core2)

    tb_core3, _, _ = textbox(420, 280, "3. Панічне сіпання (Panic Stick Stirring):\nХаотичні знакозмінні рухи високої частоти", size=10, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_core3)

    # Правий блок: Ескалація дій
    frags.append(rect(610, 55, 210, 280, fill="#fef2f2", stroke=POS, sw=2, rx=6))
    frags.append(text(715, 80, "ЕСКАЛАЦІЯ ЗАХИСТУ", size=12, color=POS, bold=True))
    frags.append(line(625, 92, 805, 92, color=POS, sw=1))

    tb_act1, _, _ = textbox(715, 125, "Рівень 1: Попередження\nГолосове «Mode Mismatch»,\nвібрація на пульті", size=10, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_act1)

    tb_act2, _, _ = textbox(715, 200, "Рівень 2: Stick Override\nПримусове повернення\nкерування людині (Breakout)", size=10, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_act2)

    tb_act3, _, _ = textbox(715, 275, "Рівень 3: Failsafe Stop\nЗависання на місці (Brake)\nдо стабілізації дій", size=10, pad=6, fill="#fee2e2", stroke=POS, bold=True)
    frags.append(tb_act3)

    # Зв'язки стрілками
    frags.append(arrow(230, 125, 270, 130, color=LINE, sw=1.5))
    frags.append(arrow(230, 195, 270, 205, color=LINE, sw=1.5))
    frags.append(arrow(230, 275, 270, 280, color=LINE, sw=1.5))

    frags.append(arrow(570, 130, 610, 125, color=POS, sw=1.8))
    frags.append(arrow(570, 205, 610, 200, color=POS, sw=1.8))
    frags.append(arrow(570, 280, 610, 275, color=POS, sw=1.8))

    out_path = os.path.join(IMG_DIR, "mode-consistency-monitor.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)


if __name__ == "__main__":
    fig_mental_model_desync()
    fig_mode_annunciation_hierarchy()
    fig_mode_consistency_monitor()
