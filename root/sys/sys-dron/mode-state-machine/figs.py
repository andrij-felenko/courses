# -*- coding: utf-8 -*-
"""Фігури до статті «Автомат режимів» (sys-dron/mode-state-machine).
Запуск: python figs.py  ->  ./img/*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Ієрархія та переходи між польотними режимами ─────────────────────────
def fig_hierarchy_fsm():
    W, H = 860, 530
    f = []

    # Заголовок
    f.append(text(W / 2, 25, "Ієрархія польотних режимів та безпечна деградація", size=16, bold=True))

    # Рамки супер-станів
    # 1. Ручні режими (ліва колонка)
    f.append(rect(20, 50, 180, 420, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(110, 72, "РУЧНІ РЕЖИМИ", size=12, bold=True, color=INK))
    f.append(text(110, 88, "Вимоги: IMU (гіро/аксель)", size=10, color=MUTED))

    box_man = fitbox(35, 110, 150, 42, "MANUAL\n(прямий PWM/стік)", size=11, fill="#ffffff", stroke=INK, sw=1.5)
    box_acro = fitbox(35, 180, 150, 42, "ACRO / RATE\n(кутова швидкість)", size=11, fill="#ffffff", stroke=INK, sw=1.5)
    box_stab = fitbox(35, 250, 150, 42, "STABILIZE / ANGLE\n(горизонт / кут)", size=11, fill="#ffffff", stroke=FIELD, sw=1.8)
    f.extend([box_man, box_acro, box_stab])

    # 2. Напівавтономні режими (середня колонка)
    f.append(rect(230, 50, 190, 420, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(325, 72, "НАПІВАВТОНОМНІ", size=12, bold=True, color=FIELD))
    f.append(text(325, 88, "Вимоги: Баро / EKF-Z / GNSS", size=10, color=MUTED))

    box_alt = fitbox(245, 140, 160, 46, "ALT_HOLD\n(утримання висоти)", size=11, fill="#ffffff", stroke=FIELD, sw=1.5)
    box_pos = fitbox(245, 250, 160, 46, "POS_HOLD / LOITER\n(утримання точки 3D)", size=11, fill="#ffffff", stroke=FIELD, sw=1.8)
    f.extend([box_alt, box_pos])

    # 3. Повністю автономні (права колонка зверху)
    f.append(rect(450, 50, 195, 420, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    f.append(text(547, 72, "АВТОНОМНІ РЕЖИМИ", size=12, bold=True, color=NEG))
    f.append(text(547, 88, "Вимоги: 3D Fix + Місія/Home", size=10, color=MUTED))

    box_auto = fitbox(465, 110, 165, 42, "AUTO / MISSION\n(політ за точками)", size=11, fill="#ffffff", stroke=NEG, sw=1.5)
    box_guided = fitbox(465, 175, 165, 42, "GUIDED / OFFBOARD\n(команди з бортового ПК)", size=11, fill="#ffffff", stroke=NEG, sw=1.5)
    box_rtl = fitbox(465, 240, 165, 42, "RTL\n(повернення додому)", size=11, fill="#ffffff", stroke=NEG, sw=1.5)
    box_land = fitbox(465, 305, 165, 42, "LAND\n(автономна посадка)", size=11, fill="#ffffff", stroke=NEG, sw=1.5)
    f.extend([box_auto, box_guided, box_rtl, box_land])

    # 4. Аварійні стани (Failsafe) (крайня права колонка)
    f.append(rect(670, 50, 170, 420, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    f.append(text(755, 72, "АВАРІЙНІ (FAILSAFE)", size=12, bold=True, color=POS))
    f.append(text(755, 88, "Тригери: втрата зв'язку / EKF", size=10, color=MUTED))

    box_fs_rtl = fitbox(680, 140, 150, 44, "FAILSAFE RTL\n(обрив RC / GCS)", size=11, fill="#ffffff", stroke=POS, sw=1.8)
    box_fs_land = fitbox(680, 240, 150, 44, "FAILSAFE LAND\n(втрата GNSS / батарея)", size=11, fill="#ffffff", stroke=POS, sw=1.8)
    box_fs_term = fitbox(680, 340, 150, 44, "TERMINATE / DISARM\n(краш / спут)", size=11, fill="#ffffff", stroke=POS, sw=1.8)
    f.extend([box_fs_rtl, box_fs_land, box_fs_term])

    # Стрілки нормальних переходів (сірі/зелені/сині)
    # Ручні вгору-вниз
    f.append(arrow(110, 152, 110, 180, color=MUTED))
    f.append(arrow(110, 222, 110, 250, color=MUTED))
    # STABILIZE -> ALT_HOLD
    f.append(arrow(185, 260, 245, 163, color=FIELD))
    # ALT_HOLD -> POS_HOLD
    f.append(arrow(325, 186, 325, 250, color=FIELD))
    # POS_HOLD -> AUTO
    f.append(arrow(405, 260, 465, 131, color=NEG))

    # Стрілки деградації при відмові сенсорів (червоні)
    # AUTO -> POS_HOLD
    f.append(arrow(465, 140, 405, 265, color=POS, sw=1.5))
    # POS_HOLD -> ALT_HOLD (Втрата EKF-позиції)
    f.append(arrow(295, 250, 295, 186, color=POS, sw=1.5))
    f.append(fitbox(245, 330, 160, 36, "Втрата EKF-позиції ->\nдеградація в ALT_HOLD", size=10, fill="#fff0f0", stroke=POS, color=POS, bold=True))

    # ALT_HOLD -> STABILIZE (Втрата Баро/EKF-Z)
    f.append(arrow(245, 175, 185, 270, color=POS, sw=1.5))
    f.append(fitbox(35, 330, 150, 36, "Відмова барометра ->\nдеградація в STABILIZE", size=10, fill="#fff0f0", stroke=POS, color=POS, bold=True))

    # Аварійні переходи в Failsafe
    f.append(arrow(630, 131, 680, 155, color=POS, sw=1.6))
    f.append(arrow(630, 260, 680, 260, color=POS, sw=1.6))
    f.append(arrow(405, 285, 680, 270, color=POS, sw=1.6))

    # Підписи умов внизу
    f.append(rect(35, 480, 790, 30, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(430, 500, "Зелені стрілки — запити пілота/GCS з guard-перевірками. Червоні — автоматична деградація за EKF/Failsafe.", size=11, color=INK))

    render(os.path.join(IMG, "mode-hierarchy-fsm.svg"), W, H, *f)


# ── 2. Часова діаграма Bumpless Transfer при зміні режиму ─────────────────────
def fig_bumpless_transfer():
    W, H = 800, 440
    f = []

    # Заголовок
    f.append(text(W / 2, 25, "Синхронізація сетопоінтів (Bumpless Transfer) при переході STABILIZE -> ALT_HOLD", size=15, bold=True))

    # Часова вісь
    t_switch = 360
    y_top = 60
    h_block = 150

    # Блок 1: БЕЗ Bumpless Transfer (верхній графік)
    f.append(rect(30, y_top, 740, h_block, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    f.append(text(45, y_top + 20, "БЕЗ синхронізації (Hard Switch): ривок і провал висоти", size=12, bold=True, color=POS, anchor="start"))

    # Осі
    f.append(line(70, y_top + 120, 740, y_top + 120, color=MUTED, sw=1))
    f.append(line(70, y_top + 40, 70, y_top + 130, color=MUTED, sw=1))
    f.append(text(65, y_top + 45, "Z, м", size=10, color=MUTED, anchor="end"))
    f.append(text(740, y_top + 135, "час (t)", size=10, color=MUTED, anchor="end"))

    # Лінія моменту перемикання
    f.append(line(t_switch, y_top + 35, t_switch, y_top + 135, color=POS, sw=1.5, dash="4,4"))
    f.append(text(t_switch, y_top + 145, "t_switch (перемикання)", size=10, color=POS, bold=True))

    # Поточна висота (синя)
    # До перемикання літак на 50 м
    f.append(line(70, y_top + 75, t_switch, y_top + 75, color=NEG, sw=2))
    # Після перемикання - стрибок сетопоінта в 0м спричиняє різке пікірування
    f.append(line(t_switch, y_top + 75, t_switch + 40, y_top + 110, color=NEG, sw=2))
    f.append(line(t_switch + 40, y_top + 110, 720, y_top + 100, color=NEG, sw=2))
    f.append(text(180, y_top + 68, "Фактична висота Z_real = 50 м", size=10, color=NEG, bold=True))

    # Уставка цільової висоти (зелений пунктир)
    # До t_switch уставка неактивна (ручний режим)
    f.append(line(70, y_top + 115, t_switch, y_top + 115, color=FIELD, sw=1.5, dash="3,3"))
    f.append(text(180, y_top + 110, "Стара уставка Z_target = 0 м", size=10, color=FIELD))
    # У момент t_switch без синхронізації регулятор бачить помилку 50м!
    f.append(line(t_switch, y_top + 115, 720, y_top + 115, color=FIELD, sw=1.5, dash="3,3"))

    # Позначка стрибка
    f.append(arrow(t_switch + 15, y_top + 75, t_switch + 15, y_top + 115, color=POS, sw=1.5))
    f.append(text(t_switch + 25, y_top + 95, "Велика помилка e = 50м -> удар газом униз!", size=10, color=POS, anchor="start", bold=True))

    # Блок 2: З Bumpless Transfer (нижній графік)
    y_bot = y_top + h_block + 30
    f.append(rect(30, y_bot, 740, h_block, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(45, y_bot + 20, "З Bumpless Transfer: Z_target := Z_real, інтегратор предзавантажено", size=12, bold=True, color=FIELD, anchor="start"))

    # Осі
    f.append(line(70, y_bot + 120, 740, y_bot + 120, color=MUTED, sw=1))
    f.append(line(70, y_bot + 40, 70, y_bot + 130, color=MUTED, sw=1))
    f.append(text(65, y_bot + 45, "Z, м", size=10, color=MUTED, anchor="end"))
    f.append(text(740, y_bot + 135, "час (t)", size=10, color=MUTED, anchor="end"))

    # Лінія моменту перемикання
    f.append(line(t_switch, y_bot + 35, t_switch, y_bot + 135, color=FIELD, sw=1.5, dash="4,4"))
    f.append(text(t_switch, y_bot + 145, "t_switch", size=10, color=FIELD, bold=True))

    # Поточна висота (синя лінія рівна)
    f.append(line(70, y_bot + 75, 720, y_bot + 75, color=NEG, sw=2))
    f.append(text(180, y_bot + 68, "Фактична висота Z_real = 50 м (без коливань)", size=10, color=NEG, bold=True))

    # Уставка цільової висоти
    # У момент перемикання уставка миттєво стає рівною 50 м
    f.append(line(70, y_bot + 115, t_switch, y_bot + 115, color=FIELD, sw=1.5, dash="3,3"))
    f.append(arrow(t_switch, y_bot + 115, t_switch, y_bot + 77, color=FIELD, sw=1.8))
    f.append(text(t_switch - 10, y_bot + 95, "Z_target := 50 м", size=10, color=FIELD, anchor="end", bold=True))
    f.append(line(t_switch, y_bot + 75, 720, y_bot + 75, color=FIELD, sw=1.5, dash="3,3"))

    f.append(text(t_switch + 40, y_bot + 95, "Помилка e = 0, тяга = T_hover -> плавне зависання", size=10, color=FIELD, anchor="start", bold=True))

    # Підсумок внизу
    f.append(text(W / 2, y_bot + h_block + 20, "Плавний перехід вимагає синхронізації сетопоінтів та ініціалізації внутрішнього стану інтеграторів PID.", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "bumpless-transfer-timing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_hierarchy_fsm()
    fig_bumpless_transfer()
    print("SVG generated successfully.")
