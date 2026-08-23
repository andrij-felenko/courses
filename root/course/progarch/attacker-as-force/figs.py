# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"


def fig_retrofit_vs_structural():
    """Порівняння ретрофітингу (наклеєної безпеки над неізольованим монолітом)
    та системної архітектурної безпеки (з явними межами довіри й ізоляцією)."""
    W, H = 1000, 520
    f = []

    # --- Верхній блок: Ретрофітинг ---
    f.append(rect(20, 20, 960, 225, fill="#fdfefe", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(fitbox(35, 32, 280, 28, "1. Ретрофітинг (безпека наклеєна «потім»)", size=14, bold=True, fill=BG, stroke=POS, color=POS))

    # Зовнішній WAF / Наліпка
    f.append(fitbox(45, 80, 150, 135, "Зовнішній WAF /\nПатч авторизації\n\n(лише на вході)", size=12, fill=AMBER_T, stroke=AMBER))

    # Внутрішнє спільне черевце (моноліт без меж)
    f.append(rect(240, 80, 715, 135, fill=RED_T, stroke=POS, sw=1.5, rx=6))
    f.append(text(597, 100, "Спільний неізольований контекст (soft belly)", size=13, color=POS, bold=True))

    f.append(fitbox(260, 120, 160, 75, "Блок A\n(БД / Запити)", size=12, fill=BG, stroke=POS))
    f.append(fitbox(445, 120, 160, 75, "Блок B\n(Сенсори / Пристрої)", size=12, fill=BG, stroke=POS))
    f.append(fitbox(630, 120, 160, 75, "Блок C\n(Замок / Права)", size=12, fill=BG, stroke=POS))
    f.append(fitbox(815, 120, 125, 75, "Спільний\nстан у пам'яті", size=12, fill=BG, stroke=POS))

    # Стрілки обходу всередині
    f.append(arrow(195, 147, 260, 147, color=POS, sw=2))
    f.append(arrow(420, 157, 445, 157, color=POS, sw=2))
    f.append(arrow(605, 157, 630, 157, color=POS, sw=2))
    f.append(arrow(790, 157, 815, 157, color=POS, sw=2))
    f.append(text(597, 207, "Обхід периметра → прямий витік між блоками через спільний стан", size=11, color=POS, italic=True))

    # --- Нижній блок: Системна безпека ---
    f.append(rect(20, 265, 960, 235, fill="#fdfefe", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(fitbox(35, 277, 310, 28, "2. Системна безпека (властивість структури)", size=14, bold=True, fill=BG, stroke=FIELD, color=FIELD))

    # Три ізольовані домени із власними межами
    domains = [
        ("Домен датчиків\n(Низька довіра)", 45, GREEN_T),
        ("Шлюз обробки\n(Проміжна довіра)", 360, BLUE_T),
        ("Ядро керування\n(Висока довіра)", 675, GREEN_T)
    ]

    for title, x, bg_col in domains:
        f.append(rect(x, 325, 280, 155, fill=bg_col, stroke="#a0b0c0", sw=1.2, rx=6))
        f.append(text(x + 140, 345, title, size=13, color=INK, bold=True))

    f.append(fitbox(60, 365, 250, 50, "Вхідний фільтр інваріантів\n+ обмеження частоти", size=11, fill=BG, stroke=LINE))
    f.append(fitbox(60, 425, 250, 40, "Ізольований буфер датчика", size=11, fill=BG, stroke=LINE))

    f.append(fitbox(375, 365, 250, 50, "Точка повної медіації\n(Complete Mediation)", size=11, fill=BG, stroke=LINE))
    f.append(fitbox(375, 425, 250, 40, "Валідація токенів / крипто", size=11, fill=BG, stroke=LINE))

    f.append(fitbox(690, 365, 250, 50, "Доменні інваріанти замка\n+ RBAC / ABAC", size=11, fill=BG, stroke=LINE))
    f.append(fitbox(690, 425, 250, 40, "Аудит та захищений стан", size=11, fill=BG, stroke=LINE))

    # Пунктирні межі довіри між доменами
    f.append(line(340, 325, 340, 480, color=POS, sw=2, dash="5 4"))
    f.append(text(340, 317, "Межа довіри 1", size=10, color=POS, anchor="middle"))

    f.append(line(655, 325, 655, 480, color=POS, sw=2, dash="5 4"))
    f.append(text(655, 317, "Межа довіри 2", size=10, color=POS, anchor="middle"))

    # Контрольовані стрілки переходів
    f.append(arrow(310, 390, 375, 390, color=FIELD, sw=2))
    f.append(arrow(625, 390, 690, 390, color=FIELD, sw=2))

    render(os.path.join(OUT, 'retrofit-vs-structural.svg'), W, H, *f,
           title="Ретрофітинг проти системної безпеки")


def fig_attack_economics_asymmetry():
    """Економічна асиметрія атаки та захисту: крива витрат захисника
    проти витрат нападника та цінності активу."""
    W, H = 900, 480
    f = []

    # Осі координат
    f.append(arrow(80, 410, 840, 410, color=LINE, sw=2))  # X
    f.append(arrow(80, 410, 80, 40, color=LINE, sw=2))    # Y

    f.append(text(840, 435, "Складність / захищеність системи →", size=12, color=INK, anchor="end", bold=True))
    f.append(text(75, 30, "Витрати ($) / Ресурси ↑", size=12, color=INK, anchor="start", bold=True))

    # Горизонтальна лінія: Цінність активу (Asset Value)
    f.append(line(80, 220, 820, 220, color=AMBER, sw=2.5, dash="8 5"))
    f.append(text(825, 215, "Цінність активу для нападника (V_asset)", size=12, color=AMBER, anchor="end", bold=True))

    # Парабола / Експонента: Витрати захисника (Defender Cost)
    # y(x) = 410 - (0.0005 * (x - 80)^2 + 20)
    def y_def(x):
        dx = x - 80
        return 410 - (0.00048 * (dx ** 2) + 20)

    points_def = []
    for x in range(80, 801, 20):
        points_def.append((x, y_def(x)))

    path_def_str = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in points_def)
    f.append(f'<path d="{path_def_str}" stroke="{POS}" fill="none" stroke-width="3"/>')
    f.append(text(780, y_def(780) - 12, "Витрати захисника C_def", size=12, color=POS, anchor="end", bold=True))

    # Лінія витрат нападника (Attacker Cost)
    def y_att(x):
        dx = x - 80
        return 410 - (0.35 * dx + 15)

    points_att = []
    for x in range(80, 801, 20):
        points_att.append((x, y_att(x)))

    path_att_str = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in points_att)
    f.append(f'<path d="{path_att_str}" stroke="{NEG}" fill="none" stroke-width="3"/>')
    f.append(text(750, y_att(750) + 22, "Витрати нападника C_attack", size=12, color=NEG, anchor="end", bold=True))

    # Перетин витрат нападника та цінності активу: Точка економічного відлякування (x ≈ 665, y = 220)
    x_intersect = 665
    f.append(line(x_intersect, 410, x_intersect, 60, color=FIELD, sw=1.8, dash="4 4"))
    f.append(circle(x_intersect, 220, 6, fill=FIELD, stroke=INK, sw=1.5))

    # Зона економічної недоцільності атаки
    f.append(rect(x_intersect, 60, 820 - x_intersect, 350, fill=GREEN_T, stroke="none"))
    # Перемальовуємо поверх графіки, які накрила заливка
    f.append(line(x_intersect, 410, x_intersect, 60, color=FIELD, sw=1.8, dash="4 4"))
    f.append(f'<path d="{path_def_str}" stroke="{POS}" fill="none" stroke-width="3"/>')
    f.append(f'<path d="{path_att_str}" stroke="{NEG}" fill="none" stroke-width="3"/>')
    f.append(line(80, 220, 820, 220, color=AMBER, sw=2.5, dash="8 5"))
    f.append(circle(x_intersect, 220, 6, fill=FIELD, stroke=INK, sw=1.5))

    f.append(fitbox(x_intersect + 15, 80, 135, 55, "Зона недоцільності\nC_attack > V_asset\n(ROI < 0)", size=11, bold=True, fill=BG, stroke=FIELD, color=FIELD))

    # Профілі нападників на осі X
    f.append(text(200, 428, "Скрипт-кіді", size=11, color=MUTED))
    f.append(text(420, 428, "Кіберзлочинці", size=11, color=MUTED))
    f.append(text(720, 428, "APT / Спецслужби", size=11, color=MUTED))

    render(os.path.join(OUT, 'attack-economics-asymmetry.svg'), W, H, *f,
           title="Економічна асиметрія атаки та захисту")


def fig_blast_radius_dh():
    """Ізоляція радіусу ураження в Digital Homes: від компрометованого
    вуличного сенсора до захищеного ядра та замка дверей."""
    W, H = 1000, 400
    f = []

    # 1. Вуличний сенсор (Зкомпрометовано)
    f.append(fitbox(30, 140, 180, 110, "Вуличний сенсор\n(Zigbee / Bluetooth)\n\n[ЗКОМПРОМЕТОВАНО]", size=12, bold=True, fill=RED_T, stroke=POS))

    # Межа 1: Edge Boundary
    f.append(line(245, 50, 245, 340, color=POS, sw=2, dash="6 4"))
    f.append(text(245, 35, "Межа довіри Edge", size=11, color=POS, bold=True))

    # 2. Локальний шлюз DH Gateway (Ізольовано)
    f.append(fitbox(280, 110, 220, 170, "DH Gateway (Шлюз)\n\n• Валідація схеми\n• Rate Limiting\n• Розредагування\n• Санбоксінг", size=12, fill=AMBER_T, stroke=AMBER))

    # Межа 2: Core Boundary
    f.append(line(535, 50, 535, 340, color=POS, sw=2, dash="6 4"))
    f.append(text(535, 35, "Межа довіри Core", size=11, color=POS, bold=True))

    # 3. Ядро контролера та Замок (Захищено)
    f.append(fitbox(575, 100, 180, 90, "Сервер контролю\n(DH Core Engine)\n\n[ЗАХИЩЕНО]", size=12, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(790, 100, 180, 90, "Контролер замка\n(Door Lock Node)\n\n[ІЗОЛЬОВАНО]", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    f.append(fitbox(575, 220, 395, 60, "Аудит лог та виявлення аномалій (SIEM)\nАворт сесії при підозрілій активності", size=11, fill=BLUE_T, stroke=NEG))

    # Стрілки
    f.append(arrow(210, 195, 280, 195, color=POS, sw=2))
    f.append(text(245, 180, "Атака / Спам", size=10, color=POS, anchor="middle"))

    f.append(arrow(500, 145, 575, 145, color=FIELD, sw=2))
    f.append(text(537, 130, "Очищені події", size=10, color=FIELD, anchor="middle"))

    f.append(arrow(755, 145, 790, 145, color=FIELD, sw=2))

    # Червоний хрест спроби пробою (малюється нижче)
    f.append(line(520, 295, 550, 325, color=POS, sw=3))
    f.append(line(550, 295, 520, 325, color=POS, sw=3))
    f.append(fitbox(450, 335, 170, 25, "Прямий доступ заблоковано", size=10, bold=True, fill=BG, stroke=POS, color=POS))

    render(os.path.join(OUT, 'blast-radius-dh.svg'), W, H, *f,
           title="Ізоляція радіусу ураження в Digital Homes")


if __name__ == '__main__':
    fig_retrofit_vs_structural()
    fig_attack_economics_asymmetry()
    fig_blast_radius_dh()
    print("Figures generated successfully.")
