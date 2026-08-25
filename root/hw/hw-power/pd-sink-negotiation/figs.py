# -*- coding: utf-8 -*-
"""Фігури до теми «PD-переговори стіка: алгоритм вибору профілю».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (імпорт із scripts/)."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Послідовність переговорів PD: джерело ↔ стік ──────────────────────────
def fig_negotiation_flow():
    W, H = 880, 530
    frags = [
        text(W / 2, 26, "Часова послідовність переговорів Power Delivery (Source ↔ Sink)", size=16, bold=True),
    ]

    # Вертикальні лінії життя (жили зв'язку)
    x_src = 250
    x_snk = 630
    y_start = 55
    y_end = 480

    # Шапки сутностей
    b_src, _, _ = textbox(x_src, y_start + 15, "Джерело живлення\n(Source / DFP)", size=12, pad=6, fill="#eaf0fd", stroke=NEG, bold=True)
    b_snk, _, _ = textbox(x_snk, y_start + 15, "Приймач живлення\n(Sink / UFP)", size=12, pad=6, fill="#fdecea", stroke=POS, bold=True)
    frags.extend([b_src, b_snk])

    # Пунктирні вертикальні лінії (не проходять крізь шапки)
    frags.append(line(x_src, y_start + 36, x_src, y_end, color=NEG, sw=1.5, dash="4,4"))
    frags.append(line(x_snk, y_start + 36, x_snk, y_end, color=POS, sw=1.5, dash="4,4"))

    # Подія 1: Підключення
    y1 = 115
    b_conn, _, _ = textbox(W / 2, y1 - 8, "1. З'єднання Type-C (Rd виявлено на CC) → VBUS = 5 В (vSafe5V)", size=11, fill="#ffffff", stroke="#9ca3af", pad=5)
    frags.append(b_conn)

    # Подія 2: Source_Capabilities
    y2 = 160
    frags.append(arrow(x_src + 5, y2, x_snk - 5, y2, color=NEG, sw=2.0))
    frags.append(text(W / 2, y2 - 8, "Source_Capabilities [PDO1: 5V@3A, PDO2: 9V@3A, PDO3: 20V@3.25A...]", size=11, color=NEG, bold=True))

    # Подія 3: Аналіз та Request
    y3 = 225
    b_eval, _, _ = textbox(x_snk + 120, y3 - 10, "Аналіз списку PDO:\nвибір найкращого\nпрофілю (ККД, I²R)", size=10, fill="#fef3c7", stroke="#d97706", pad=5, min_w=100)
    frags.append(b_eval)
    frags.append(arrow(x_snk - 5, y3, x_src + 5, y3, color=POS, sw=2.0))
    frags.append(text(W / 2, y3 - 8, "Request [Pos=3 (20V), OperI=3.0A, MaxI=3.25A, GiveBack=0]", size=11, color=POS, bold=True))

    # Подія 4: Відповідь Accept
    y4 = 285
    frags.append(arrow(x_src + 5, y4, x_snk - 5, y4, color=FIELD, sw=2.0))
    frags.append(text(W / 2, y4 - 8, "Accept (запит на 20 В схвалено джерелом)", size=11, color=FIELD, bold=True))

    # Подія 5: Перехід VBUS (Slew Rate)
    y5 = 345
    b_trans, _, _ = textbox(x_src - 120, y5, "Плавне підняття VBUS\n(30–150 мВ/мкс):\n5 В → 20 В", size=10, fill="#f3f4f6", stroke=LINE, pad=5)
    b_snk_wait, _, _ = textbox(x_snk + 120, y5, "Ключ VBUS розімкнено\n(навантаження відсічене,\nструм < 2.5 Вт)", size=10, fill="#fef2f2", stroke=POS, pad=5)
    frags.extend([b_trans, b_snk_wait])

    # Подія 6: PS_RDY
    y6 = 405
    frags.append(arrow(x_src + 5, y6, x_snk - 5, y6, color=FIELD, sw=2.0))
    frags.append(text(W / 2, y6 - 8, "PS_RDY (Power Supply Ready: 20 В стабілізовано)", size=11, color=FIELD, bold=True))

    # Подія 7: Замикання ключа навантаження
    y7 = 465
    b_ready, _, _ = textbox(x_snk + 120, y7 - 5, "Замикання ключа VBUS\n(живлення схеми 20 В)", size=11, fill="#ecfdf5", stroke=FIELD, pad=6, bold=True)
    frags.append(b_ready)

    # Альтернативні відповіді (Reject / Wait) окремим поясненням зліва внизу
    b_alt, _, _ = textbox(x_src - 120, y7 - 5, "Альтернативні відповіді:\n• Reject (профіль зайнятий)\n• Wait (джерело балансує)", size=10, fill="#fee2e2", stroke=POS, pad=5)
    frags.append(b_alt)

    render(os.path.join(IMG, 'pd-negotiation-flow.svg'), W, H, *frags)


# ── 2. Дерево евристичної оцінки PDO ─────────────────────────────────────────
def fig_pdo_eval_tree():
    W, H = 880, 520
    frags = [
        text(W / 2, 26, "Ієрархія та критерії алгоритму вибору профілю живлення", size=16, bold=True),
    ]

    # Вхідний блок: Масив Source Capabilities
    y0 = 65
    b_in, _, _ = textbox(W / 2, y0, "Вхід: масив Source_Capabilities (1..7 об'єктів PDO від джерела)", size=13, pad=8, fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(b_in)
    frags.append(arrow(W / 2, y0 + 18, W / 2, y0 + 44, color=LINE))

    # Етап 1: Фільтрація за безпекою та граничними умовами
    y1 = 135
    b_f1, _, _ = textbox(W / 2, y1, "Етап 1. Жорсткий фільтр безпеки: відкидання профілів\nз напругою вище V_max (стеля схеми) або струмом нижче I_min (мінімум для старту)", size=12, pad=8, fill="#fef2f2", stroke=POS, bold=False)
    frags.append(b_f1)

    # Розгалуження на 3 стратегії застосування
    y2_top = 210
    frags.append(arrow(220, y1 + 25, 180, y2_top, color=LINE))
    frags.append(arrow(W / 2, y1 + 25, W / 2, y2_top, color=LINE))
    frags.append(arrow(660, y1 + 25, 700, y2_top, color=LINE))

    # Стратегія А: Прямий заряд акумулятора (PPS / AVS)
    b_pps, _, _ = textbox(180, y2_top + 45, "Стратегія A: Прямий заряд Li-ion\n(режим PPS / AVS)\n\n• Вибір APDO (3.3–21 В)\n• Крок напруги 20 мВ\n• Крок струму 50 мА\n• Тепло розсіюється в адаптері,\n  а не в корпусі пристрою", size=11, pad=8, fill="#fef3c7", stroke="#d97706", min_w=220)

    # Стратегія Б: Точний збіг напруги (DC-DC Bypass)
    b_byp, _, _ = textbox(W / 2, y2_top + 45, "Стратегія B: Обхід DC-DC\n(пряме живлення шини)\n\n• Пошук Fixed PDO з V == V_bus\n  (наприклад, рівно 12 В або 19 В)\n• Пряме живлення через ключ\n• Економія ККД перетворювача\n  (мінус 3–5 Вт втрат на платі)", size=11, pad=8, fill="#ecfdf5", stroke=FIELD, min_w=220)

    # Стратегія В: Максимальна потужність + мінімум I²R втрат
    b_maxp, _, _ = textbox(700, y2_top + 45, "Стратегія C: Максимальна потужність\n(швидкий заряд / важке навантаження)\n\n• Максимізація P = V · I\n• Мінімізація I²·R втрат у кабелі:\n  перевага 20 В @ 2.25 А\n  над 15 В @ 3 А (менший нагрів дроту)", size=11, pad=8, fill="#eaf0fd", stroke=NEG, min_w=220)

    frags.extend([b_pps, b_byp, b_maxp])

    # Зведення в єдиний скоринг
    y3 = 385
    frags.append(arrow(180, y2_top + 115, 300, y3 - 15, color=LINE))
    frags.append(arrow(W / 2, y2_top + 115, W / 2, y3 - 15, color=LINE))
    frags.append(arrow(700, y2_top + 115, 580, y3 - 15, color=LINE))

    b_score, _, _ = textbox(W / 2, y3, "Етап 2. Обчислення рангу профілю (Fitness Score) & вибір найкращого PDO:\nScore = w_v·Match(V) + w_p·Power(P) - w_loss·(I²·R_cable)", size=12, pad=8, fill="#f4f6f8", stroke=LINE, bold=True)
    frags.append(b_score)

    # Формування RDO
    y4 = 465
    frags.append(arrow(W / 2, y3 + 20, W / 2, y4 - 20, color=LINE))
    b_out, _, _ = textbox(W / 2, y4, "Вихід: формування 32-бітного пакета Request (RDO)\n[Object Position | Operating Current | Max Current | Capability Mismatch | GiveBack]", size=12, pad=8, fill="#ecfdf5", stroke=FIELD, bold=True)
    frags.append(b_out)

    render(os.path.join(IMG, 'pdo-eval-tree.svg'), W, H, *frags)


# ── 3. Скінченний автомат (FSM) стіка ────────────────────────────────────────
def fig_sink_fsm_states():
    W, H = 900, 520
    frags = [
        text(W / 2, 26, "Машина станів протокольного рівня стіка (Sink Policy Engine FSM)", size=16, bold=True),
    ]

    # Координати станів
    x1, y1 = 150, 95
    x2, y2 = 450, 95
    x3, y3 = 750, 95

    x4, y4 = 750, 265
    x5, y5 = 450, 265
    x6, y6 = 150, 265

    x7, y7 = 450, 430
    x8, y8 = 150, 430

    # 1. PE_SNK_Discovery
    b1, _, _ = textbox(x1, y1, "PE_SNK_Discovery\n(CC Rd виявлено,\nVBUS = 5 В)", size=11, pad=6, fill="#f4f6f8", stroke=LINE)
    # 2. PE_SNK_Wait_For_Cap
    b2, _, _ = textbox(x2, y1, "PE_SNK_Wait_For_Cap\n(Очікування Source_Cap,\nтаймаут tSinkWaitCap)", size=11, pad=6, fill="#eaf0fd", stroke=NEG)
    # 3. PE_SNK_Evaluate_Cap
    b3, _, _ = textbox(x3, y1, "PE_SNK_Evaluate_Cap\n(Аналіз PDO, вибір\nпрофілю за критеріями)", size=11, pad=6, fill="#fef3c7", stroke="#d97706")

    # 4. PE_SNK_Select_Cap
    b4, _, _ = textbox(x3, y4, "PE_SNK_Select_Cap\n(Надсилання Request,\nочікування відповіді)", size=11, pad=6, fill="#fef2f2", stroke=POS)
    # 5. PE_SNK_Transition_Sink
    b5, _, _ = textbox(x5, y4, "PE_SNK_Transition_Sink\n(Отримано Accept,\nочікування PS_RDY)", size=11, pad=6, fill="#fef3c7", stroke="#d97706")
    # 6. PE_SNK_Ready
    b6, _, _ = textbox(x6, y4, "PE_SNK_Ready\n(Отримано PS_RDY,\nсиловий ключ УВІМКНЕНО)", size=11, pad=6, fill="#ecfdf5", stroke=FIELD, bold=True)

    # 7. PE_SNK_GiveBack
    b7, _, _ = textbox(x7, y7, "PE_SNK_GiveBack\n(Отримано GotoMin: зниження\nспоживання до MinCurrent)", size=11, pad=6, fill="#f3f4f6", stroke=LINE)

    # 8. PE_SNK_Hard_Reset
    b8, _, _ = textbox(x8, y8, "PE_SNK_Hard_Reset\n(Аварійне скидання шини,\nVBUS скидається до 0 В)", size=11, pad=6, fill="#fee2e2", stroke=POS, bold=True)

    frags.extend([b1, b2, b3, b4, b5, b6, b7, b8])

    # Стрілки переходів
    # 1 -> 2 (Attach)
    frags.append(arrow(x1 + 65, y1, x2 - 85, y1, color=LINE))
    frags.append(text((x1 + x2) / 2 - 10, y1 - 10, "vSafe5V є", size=10, color=MUTED))

    # 2 -> 3 (Rx Source_Caps)
    frags.append(arrow(x2 + 85, y1, x3 - 85, y1, color=NEG))
    frags.append(text((x2 + x3) / 2, y1 - 10, "Rx Source_Cap", size=10, color=NEG, bold=True))

    # 3 -> 4 (Евристика обрала PDO)
    frags.append(arrow(x3, y1 + 25, x3, y4 - 25, color=LINE))
    frags.append(text(x3 + 55, (y1 + y4) / 2, "Tx Request", size=10, color=POS, bold=True))

    # 4 -> 5 (Rx Accept)
    frags.append(arrow(x3 - 85, y4, x5 + 85, y4, color=FIELD))
    frags.append(text((x3 + x5) / 2, y4 - 10, "Rx Accept", size=10, color=FIELD, bold=True))

    # 4 -> 2 (Rx Reject або Wait)
    frags.append(arrow(x3 - 50, y4 - 25, x2 + 50, y1 + 25, color=POS, sw=1.2))
    frags.append(text((x3 + x2) / 2 + 10, (y4 + y1) / 2 - 15, "Rx Reject / Wait", size=10, color=POS))

    # 5 -> 6 (Rx PS_RDY)
    frags.append(arrow(x5 - 85, y4, x6 + 85, y4, color=FIELD, sw=2.0))
    frags.append(text((x5 + x6) / 2, y4 - 10, "Rx PS_RDY (ключ ON)", size=10, color=FIELD, bold=True))

    # 6 -> 7 (Rx GotoMin)
    frags.append(arrow(x6 + 50, y4 + 25, x7 - 85, y7 - 10, color=LINE))
    frags.append(text((x6 + x7) / 2 - 40, (y4 + y7) / 2, "Rx GotoMin", size=10, color=MUTED))

    # 7 -> 6 (Відновлення струму)
    frags.append(arrow(x7 - 85, y7 + 10, x6 + 30, y4 + 30, color=LINE, sw=1.2))

    # 6 -> 3 (Rx нові Source_Caps під час роботи)
    frags.append(arrow(x6 + 20, y4 - 30, x3 - 40, y1 + 30, color=NEG, sw=1.2))
    frags.append(text(W / 2, y4 - 75, "Rx нові Source_Cap (переузгодження)", size=10, color=NEG))

    # Переходи в Hard_Reset при помилці
    frags.append(arrow(x6, y4 + 25, x8, y8 - 25, color=POS, sw=1.5))
    frags.append(text(x8 + 65, (y4 + y8) / 2, "Помилка / Таймаут", size=10, color=POS))

    # Hard_Reset -> Discovery
    frags.append(arrow(x8 - 60, y8 - 25, x1 - 60, y1 + 25, color=POS, sw=1.5))
    frags.append(text(x1 - 95, (y1 + y8) / 2, "Скидання до 0 В", size=10, color=POS))

    render(os.path.join(IMG, 'sink-fsm-states.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_negotiation_flow()
    fig_pdo_eval_tree()
    fig_sink_fsm_states()
    print("Фігури успішно згенеровано у ./img/")
