# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Апаратний ланцюг аварійного стопу (Cat 4 / SIL 3) ──────────────
def fig_estop_circuit():
    W, H = 820, 440
    frags = []
    frags.append(text(W / 2, 28, "Двоканальний ланцюг аварійного стопу з імпульсним тестом і EDM",
                      size=15, bold=True))

    # Лівий блок: Контролер безпеки / Виходи тесту
    frags.append(fitbox(20, 60, 170, 340, "Контролер безпеки\n(Safety Controller)\n\n[T1] Тест Канал 1\n\n[T2] Тест Канал 2\n\n[IN1] Вхід К1\n\n[IN2] Вхід К2\n\n[EDM] Зворотний зв'язок\n\n[OUT] Керування K1/K2",
                        size=12, bold=False, fill="#f0f4f8", stroke=NEG, sw=1.8))

    # Центральний блок 1: Кнопка E-Stop (2xNC Positive Opening)
    frags.append(fitbox(240, 60, 200, 160, "Кнопка E-Stop (ISO 13850)\nПримусове розмикання (→)\n\nNC Контакт 1 (Ch 1)\n\nNC Контакт 2 (Ch 2)",
                        size=12, bold=False, fill="#fdf2f0", stroke=POS, sw=1.8))

    # Центральний блок 2: Реле безпеки / Контактори (EDM)
    frags.append(fitbox(240, 250, 200, 150, "Ланцюг зворотного зв'язку\n(EDM Loop)\n\nNC контакт контактора K1\nпослідовно з\nNC контактом контактора K2",
                        size=11, bold=False, fill="#fef9e7", stroke="#d98324", sw=1.6))

    # Правий блок: Силовий розрив і приводи
    frags.append(fitbox(500, 60, 290, 340, "Силовий комутаційний вузол\n(Power Isolation & STO)\n\n+24V / 3~ 400V Живлення двигунів\n\n[ K1 ] Силовий контактор 1 (NO)\n       (Примусово керовані контакти)\n\n[ K2 ] Силовий контактор 2 (NO)\n       (Дубльований розрив)\n\n──────► До сервоприводів (STO)\n──────► До силових котушок двигунів",
                        size=12, bold=False, fill="#f4f6f8", stroke=INK, sw=1.8))

    # З'єднувальні лінії
    # T1 -> E-Stop NC1 -> IN1
    frags.append(arrow(190, 115, 240, 115, color=NEG, sw=1.5))
    frags.append(arrow(440, 115, 470, 115, color=NEG, sw=1.5))
    frags.append(line(470, 115, 470, 175, color=NEG, sw=1.5))
    frags.append(arrow(470, 175, 190, 175, color=NEG, sw=1.5))

    # T2 -> E-Stop NC2 -> IN2
    frags.append(arrow(190, 145, 240, 145, color=POS, sw=1.5))
    frags.append(arrow(440, 145, 485, 145, color=POS, sw=1.5))
    frags.append(line(485, 145, 485, 205, color=POS, sw=1.5))
    frags.append(arrow(485, 205, 190, 205, color=POS, sw=1.5))

    # EDM Loop
    frags.append(arrow(190, 310, 240, 310, color="#d98324", sw=1.5))
    frags.append(arrow(440, 310, 500, 310, color="#d98324", sw=1.5))
    frags.append(line(500, 345, 470, 345, color="#d98324", sw=1.5))
    frags.append(line(470, 345, 470, 275, color="#d98324", sw=1.5))
    frags.append(arrow(470, 275, 190, 275, color="#d98324", sw=1.5))

    # OUT -> K1/K2 coils
    frags.append(arrow(190, 370, 500, 370, color=INK, sw=1.8))

    render(os.path.join(OUT, 'estop-dual-channel-circuit.svg'), W, H, *frags)


# ── Фігура 2: Діагностика імпульсним тестом (Pulse Testing) ──────────────────
def fig_pulse_testing():
    W, H = 800, 420
    frags = []
    frags.append(text(W / 2, 26, "Динамічний імпульсний тест: розпізнавання замикань за зсувом фаз",
                      size=15, bold=True))

    # Часова шкала
    t_start, t_end = 180, 750
    y_t1, y_t2 = 70, 130
    y_in1_norm, y_in2_norm = 190, 240
    y_fault1, y_fault2 = 310, 360

    # Підписи зліва
    frags.append(text(160, y_t1 + 6, "Тест T1 (вихід)", size=12, color=NEG, bold=True, anchor="end"))
    frags.append(text(160, y_t2 + 6, "Тест T2 (вихід)", size=12, color=POS, bold=True, anchor="end"))
    frags.append(text(160, y_in1_norm + 6, "Норма IN1 (вхід)", size=12, color=INK, bold=True, anchor="end"))
    frags.append(text(160, y_in2_norm + 6, "Норма IN2 (вхід)", size=12, color=INK, bold=True, anchor="end"))
    frags.append(text(160, y_fault1 + 6, "IN1 при КЗ на +24V", size=12, color=POS, bold=True, anchor="end"))
    frags.append(text(160, y_fault2 + 6, "IN2 при КЗ між T1 і T2", size=12, color="#d98324", bold=True, anchor="end"))

    # Базові лінії
    def draw_sig(y, pulses, color=LINE):
        frags.append(line(t_start, y, t_end, y, color="#e0e0e0", sw=1.0))
        pts = [(t_start, y - 8)]
        cur_x = t_start
        for px1, px2 in pulses:
            pts.append((px1, y - 8))
            pts.append((px1, y + 8))
            pts.append((px2, y + 8))
            pts.append((px2, y - 8))
            cur_x = px2
        pts.append((t_end, y - 8))
        for i in range(len(pts) - 1):
            frags.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=color, sw=2.0))

    # T1 drops at 240..270 and 520..550
    draw_sig(y_t1, [(240, 270), (520, 550)], color=NEG)
    # T2 drops at 380..410 and 660..690 (phase shifted!)
    draw_sig(y_t2, [(380, 410), (660, 690)], color=POS)

    # Normals mirror T1 and T2
    draw_sig(y_in1_norm, [(240, 270), (520, 550)], color=NEG)
    draw_sig(y_in2_norm, [(380, 410), (660, 690)], color=POS)

    # Short to +24V: always HIGH (no pulse observed -> FAULT!)
    draw_sig(y_fault1, [], color=POS)
    frags.append(rect(230, y_fault1 - 18, 90, 36, fill="#feebe8", stroke=POS, sw=1.4))
    frags.append(text(275, y_fault1 + 4, "Немає провалу!", size=10, color=POS, bold=True))

    # Cross short: IN2 sees dips from BOTH T1 and T2!
    draw_sig(y_fault2, [(240, 270), (380, 410), (520, 550), (660, 690)], color="#d98324")
    frags.append(rect(510, y_fault2 - 18, 100, 36, fill="#fef5e7", stroke="#d98324", sw=1.4))
    frags.append(text(560, y_fault2 + 4, "Чужий імпульс T1!", size=10, color="#d98324", bold=True))

    # Роздільні лінії секцій
    frags.append(line(40, 160, 770, 160, color=MUTED, sw=1.0, dash="4,4"))
    frags.append(line(40, 275, 770, 275, color=MUTED, sw=1.0, dash="4,4"))

    # Пояснення імпульсу
    frags.append(text(255, y_t1 - 16, "t_pulse ≈ 200 µs", size=10, color=NEG, bold=True))

    render(os.path.join(OUT, 'pulse-testing-timing.svg'), W, H, *frags)


# ── Фігура 3: Трипозиційний перемикач мертвої руки (3-Position Enabling) ──────
def fig_deadman_switch():
    W, H = 820, 380
    frags = []
    frags.append(text(W / 2, 26, "3-позиційна кнопка мертвої руки: кінематика та безпечні стани",
                      size=15, bold=True))

    cols = [
        ("Позиція 1: Відпущено", "OFF (Небезпечний стан)", "Рука знята або оператор знепритомнів", "#eef2f7", MUTED),
        ("Позиція 2: Середня (Робота)", "ENABLE (Дозвіл руху)", "Свідоме легке утримання пружини", "#eafaf1", FIELD),
        ("Позиція 3: Панічне стискання", "OFF (Аварійний стоп)", "Судома, переляк, падіння на пульт", "#fdecea", POS),
    ]

    bw = 230
    gap = 25
    x0 = (W - (3 * bw + 2 * gap)) / 2
    y0 = 65
    bh = 170

    for i, (title, state, desc, bg_col, border_col) in enumerate(cols):
        x = x0 + i * (bw + gap)
        frags.append(rect(x, y0, bw, bh, fill=bg_col, stroke=border_col, sw=2.0))
        frags.append(text(x + bw / 2, y0 + 30, title, size=13, bold=True, color=INK))
        frags.append(fitbox(x + 15, y0 + 55, bw - 30, 36, state, size=12, bold=True,
                            fill="#ffffff", stroke=border_col, sw=1.5))
        frags.append(fitbox(x + 15, y0 + 105, bw - 30, 50, desc, size=11, bold=False,
                            fill="none", stroke="none"))

    # Стрілки переходів
    y_arr = y0 + bh + 30
    frags.append(arrow(x0 + bw - 20, y_arr, x0 + bw + gap + 20, y_arr, color=FIELD, sw=2))
    frags.append(text(x0 + bw + gap / 2, y_arr - 10, "Натискання", size=11, color=FIELD, bold=True))

    frags.append(arrow(x0 + 2 * bw + gap - 20, y_arr, x0 + 2 * bw + 2 * gap + 20, y_arr, color=POS, sw=2))
    frags.append(text(x0 + 2 * bw + 1.5 * gap, y_arr - 10, "Стискання", size=11, color=POS, bold=True))

    # Нижній банер про захист від повернення
    frags.append(fitbox(x0, H - 75, 3 * bw + 2 * gap, 55,
                        "Ключова вимога IEC 60947-5-8: При відпусканні з Позиції 3 контакти НЕ замикаються\nв Позиції 2! Система лишається вимкненою, доки кнопку не відпустять повністю в Позицію 1.",
                        size=11, bold=False, fill="#fff9db", stroke="#d98324", sw=1.6))

    render(os.path.join(OUT, 'deadman-three-position.svg'), W, H, *frags)


# ── Фігура 4: Примусово керовані контакти реле безпеки (EN 50205) ─────────────
def fig_forcibly_guided():
    W, H = 800, 390
    frags = []
    frags.append(text(W / 2, 26, "Примусово керовані контакти (Forcibly Guided): неможливість подвійної брехні",
                      size=15, bold=True))

    # Ліва половина: Звичайне реле
    frags.append(rect(30, 60, 350, 300, fill="#fdf2f0", stroke=POS, sw=1.8))
    frags.append(text(205, 85, "Звичайне реле (Небезпечно)", size=14, bold=True, color=POS))
    frags.append(fitbox(45, 105, 320, 75,
                        "Контакти з'єднані гнучкими пружинами.\nЯкщо силовий NO контакт приварився (зварився дугою),\nпружина NC контакту все одно замикає NC коло!",
                        size=11, fill="#ffffff", stroke=POS, sw=1.2))
    frags.append(fitbox(45, 200, 320, 140,
                        "Наслідок відмови:\n• Силовий двигун K1 увімкнений (NO зварений!)\n• Моніторинг EDM бачить NC замкненим\n• Контролер вважає, що контактор вимкнено!\n• Небезпечний прихований дефект (λ_DU).",
                        size=11, fill="#feebe8", stroke=POS, sw=1.4))

    # Права половина: Реле з примусовим веденням (EN 50205 / Type A)
    frags.append(rect(420, 60, 350, 300, fill="#eafaf1", stroke=FIELD, sw=1.8))
    frags.append(text(595, 85, "Реле безпеки (EN 50205 / Type A)", size=14, bold=True, color=FIELD))
    frags.append(fitbox(435, 105, 320, 75,
                        "Жорсткий механічний шток ( гребінка ).\nРухомі контакти NO та NC механічно заблоковані:\nвони НЕ можуть бути замкнені одночасно!",
                        size=11, fill="#ffffff", stroke=FIELD, sw=1.2))
    frags.append(fitbox(435, 200, 320, 140,
                        "Поведінка при зварюванні:\n• Силовий NO контакт зварився у замкненому стані\n• Шток блокує NC контакт у розімкненому стані (зазор ≥ 0.5 мм)\n• Коло EDM розірване -> Контролер блокує пуск!\n• 100% діагностичне покриття дефекту.",
                        size=11, fill="#e8f8f0", stroke=FIELD, sw=1.4))

    render(os.path.join(OUT, 'forcibly-guided-contacts.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_estop_circuit()
    fig_pulse_testing()
    fig_deadman_switch()
    fig_forcibly_guided()
    print("All figures generated successfully.")
