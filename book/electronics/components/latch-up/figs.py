# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-ілюстрацій для теми «Latch-up у CMOS».
Запуск: python figs.py
Вивід: ./img/*.svg
"""

import sys
import os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від book/electronics/components/latch-up)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_cross_section():
    """Фігура 1: Фізичний поперечний зріз CMOS-пари з паразитними PNP і NPN транзисторами."""
    w, h = 860, 480
    frags = []

    # 1. Загальна підкладка P-Substrate
    frags.append(rect(40, 70, 780, 360, fill="#edf2f7", stroke="#4a5568", sw=2, rx=8))
    frags.append(text(160, 400, "Кремнієва p-підкладка (P-Substrate, p-Si)", size=13, color="#4a5568", bold=True))

    # 2. N-кишеня (N-Well) зліва
    frags.append(rect(60, 110, 360, 240, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    frags.append(text(240, 330, "Дифузійна n-кишеня (N-Well)", size=13, color="#b45309", bold=True))

    # 3. Дифузійні області в N-Well (зліва направо: VDD Tap (n+), Source PMOS (p+), Drain PMOS (p+))
    # n+ Tap
    frags.append(rect(80, 110, 60, 45, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=3))
    frags.append(text(110, 138, "n⁺ Tap", size=11, color="#9a3412", bold=True))
    # p+ PMOS Source
    frags.append(rect(170, 110, 75, 45, fill="#fecaca", stroke="#dc2626", sw=1.5, rx=3))
    frags.append(text(207, 138, "p⁺ Витік", size=11, color="#991b1b", bold=True))
    # p+ PMOS Drain
    frags.append(rect(280, 110, 75, 45, fill="#fecaca", stroke="#dc2626", sw=1.5, rx=3))
    frags.append(text(317, 138, "p⁺ Стік", size=11, color="#991b1b", bold=True))

    # Затвор PMOS між витоком і стоком
    frags.append(rect(247, 95, 31, 15, fill="#cbd5e1", stroke="#475569", sw=1.2, rx=2))
    frags.append(text(262, 90, "Затвор", size=10, color="#334155"))

    # 4. Дифузійні області в P-Substrate (справа від N-Well: Drain NMOS (n+), Source NMOS (n+), GND Tap (p+))
    # n+ NMOS Drain
    frags.append(rect(480, 110, 75, 45, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=3))
    frags.append(text(517, 138, "n⁺ Стік", size=11, color="#9a3412", bold=True))
    # n+ NMOS Source
    frags.append(rect(590, 110, 75, 45, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=3))
    frags.append(text(627, 138, "n⁺ Витік", size=11, color="#9a3412", bold=True))
    # p+ Substrate Tap
    frags.append(rect(700, 110, 60, 45, fill="#fecaca", stroke="#dc2626", sw=1.5, rx=3))
    frags.append(text(730, 138, "p⁺ Tap", size=11, color="#991b1b", bold=True))

    # Затвор NMOS між витоком і стоком
    frags.append(rect(557, 95, 31, 15, fill="#cbd5e1", stroke="#475569", sw=1.2, rx=2))
    frags.append(text(572, 90, "Затвор", size=10, color="#334155"))

    # 5. Металеві контакти та шини зверху
    # VDD підключення
    frags.append(line(110, 110, 110, 50, color=POS, sw=2))
    frags.append(line(207, 110, 207, 50, color=POS, sw=2))
    frags.append(line(110, 50, 207, 50, color=POS, sw=2.5))
    tb_vdd, _, _ = textbox(158, 35, "Шина живлення VDD", size=12, pad=6, fill="#fee2e2", stroke=POS, bold=True)
    frags.append(tb_vdd)

    # Вихід I/O (з'єднання стоків PMOS і NMOS)
    frags.append(line(317, 110, 317, 65, color="#0284c7", sw=2))
    frags.append(line(517, 110, 517, 65, color="#0284c7", sw=2))
    frags.append(line(317, 65, 517, 65, color="#0284c7", sw=2))
    frags.append(line(417, 65, 417, 35, color="#0284c7", sw=2))
    tb_out, _, _ = textbox(417, 22, "Вивід виходу (I/O)", size=12, pad=6, fill="#e0f2fe", stroke="#0284c7", bold=True)
    frags.append(tb_out)

    # GND підключення
    frags.append(line(627, 110, 627, 50, color=NEG, sw=2))
    frags.append(line(730, 110, 730, 50, color=NEG, sw=2))
    frags.append(line(627, 50, 730, 50, color=NEG, sw=2.5))
    tb_gnd, _, _ = textbox(678, 35, "Шина землі (GND / VSS)", size=12, pad=6, fill="#dbeafe", stroke=NEG, bold=True)
    frags.append(tb_gnd)

    # 6. Паразитні компоненти (схематично всередині зрізу)
    # Паразитний PNP транзистор
    frags.append(circle(207, 230, 18, fill="#ffffff", stroke="#b91c1c", sw=2))
    frags.append(text(207, 235, "Q_pnp", size=11, color="#b91c1c", bold=True))
    frags.append(line(207, 155, 207, 212, color="#b91c1c", sw=1.8))  # Emitter
    frags.append(text(192, 180, "E", size=10, color="#b91c1c", bold=True))

    # Опір R_well (горизонтальний резистор від n+ tap до бази PNP)
    frags.append(rect(100, 222, 60, 16, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=3))
    frags.append(text(130, 234, "R_well", size=10, color="#854d0e", bold=True))
    frags.append(line(110, 155, 110, 230, color="#ca8a04", sw=1.5))
    frags.append(line(110, 230, 100, 230, color="#ca8a04", sw=1.5))
    frags.append(line(160, 230, 189, 230, color="#ca8a04", sw=1.5))

    # Паразитний NPN транзистор
    frags.append(circle(530, 250, 18, fill="#ffffff", stroke="#1d4ed8", sw=2))
    frags.append(text(530, 255, "Q_npn", size=11, color="#1d4ed8", bold=True))
    frags.append(line(627, 155, 627, 250, color="#1d4ed8", sw=1.8))
    frags.append(line(627, 250, 548, 250, color="#1d4ed8", sw=1.8))  # Emitter
    frags.append(text(612, 240, "E", size=10, color="#1d4ed8", bold=True))

    # Опір R_sub (від p+ substrate tap до бази NPN)
    frags.append(rect(660, 242, 60, 16, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=3))
    frags.append(text(690, 254, "R_sub", size=10, color="#854d0e", bold=True))
    frags.append(line(730, 155, 730, 250, color="#ca8a04", sw=1.5))
    frags.append(line(730, 250, 720, 250, color="#ca8a04", sw=1.5))
    frags.append(line(660, 250, 548, 250, color="#ca8a04", sw=1.5))

    # Зв'язки між PNP та NPN (петля зворотного зв'язку)
    frags.append(line(207, 248, 207, 280, color="#b91c1c", sw=1.8))
    frags.append(line(207, 280, 530, 280, color="#b91c1c", sw=1.8))
    frags.append(arrow(530, 280, 530, 268, color="#b91c1c", sw=1.8))
    frags.append(text(350, 296, "I_C(PNP) тече в базу NPN та крізь R_sub", size=10, color="#b91c1c"))

    frags.append(line(512, 250, 420, 250, color="#1d4ed8", sw=1.8))
    frags.append(line(420, 250, 420, 205, color="#1d4ed8", sw=1.8))
    frags.append(line(420, 205, 207, 205, color="#1d4ed8", sw=1.8))
    frags.append(arrow(207, 205, 207, 212, color="#1d4ed8", sw=1.8))
    frags.append(text(330, 198, "I_C(NPN) тягне струм із бази PNP та крізь R_well", size=10, color="#1d4ed8"))

    # Пояснювальний блок знизу
    tb_expl, _, _ = textbox(430, 445, "Чотиришарова p-n-p-n структура (тиристор) між VDD і GND утворює ланцюг самопідтримного короткого замикання",
                            size=12, pad=8, fill="#ffffff", stroke="#64748b", bold=False)
    frags.append(tb_expl)

    return render(os.path.join(IMG_DIR, "latchup-cross-section.svg"), w, h, *frags)


def fig_scr_equivalent():
    """Фігура 2: Еквівалентна схемотехнічна модель пари біполярних транзисторів і тригерних шляхів."""
    w, h = 860, 460
    frags = []

    # Верхня шина VDD і нижня шина GND
    frags.append(line(80, 50, 780, 50, color=POS, sw=3))
    frags.append(text(130, 38, "VDD (Шина живлення)", size=13, color=POS, bold=True))

    frags.append(line(80, 410, 780, 410, color=NEG, sw=3))
    frags.append(text(130, 430, "GND / VSS (Земля)", size=13, color=NEG, bold=True))

    # Схемний символ Q1 (PNP)
    frags.append(line(280, 50, 280, 120, color=LINE, sw=2))
    frags.append(circle(280, 150, 28, fill="#ffffff", stroke="#b91c1c", sw=2))
    frags.append(text(280, 155, "Q1 (PNP)", size=12, color="#b91c1c", bold=True))
    frags.append(text(260, 105, "E", size=11, color="#b91c1c", bold=True))

    # Схемний символ Q2 (NPN)
    frags.append(line(560, 410, 560, 310, color=LINE, sw=2))
    frags.append(circle(560, 280, 28, fill="#ffffff", stroke="#1d4ed8", sw=2))
    frags.append(text(560, 285, "Q2 (NPN)", size=12, color="#1d4ed8", bold=True))
    frags.append(text(580, 335, "E", size=11, color="#1d4ed8", bold=True))

    # Опір кишені R_well
    frags.append(line(160, 50, 160, 100, color=LINE, sw=1.8))
    frags.append(rect(142, 100, 36, 30, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=3))
    frags.append(text(160, 119, "R_well", size=10, color="#854d0e", bold=True))
    frags.append(line(160, 130, 160, 150, color=LINE, sw=1.8))
    frags.append(line(160, 150, 252, 150, color=LINE, sw=1.8))
    frags.append(text(240, 142, "B", size=11, color="#b91c1c", bold=True))

    # Опір підкладки R_sub
    frags.append(line(680, 410, 680, 360, color=LINE, sw=1.8))
    frags.append(rect(662, 330, 36, 30, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=3))
    frags.append(text(680, 349, "R_sub", size=10, color="#854d0e", bold=True))
    frags.append(line(680, 330, 680, 280, color=LINE, sw=1.8))
    frags.append(line(680, 280, 588, 280, color=LINE, sw=1.8))
    frags.append(text(600, 272, "B", size=11, color="#1d4ed8", bold=True))

    # Перехресні зв'язки:
    # 1. База Q1 з'єднана з колектором Q2
    frags.append(line(252, 150, 420, 150, color="#1d4ed8", sw=2))
    frags.append(line(420, 150, 420, 210, color="#1d4ed8", sw=2))
    frags.append(line(420, 210, 560, 210, color="#1d4ed8", sw=2))
    frags.append(arrow(560, 210, 560, 252, color="#1d4ed8", sw=2))
    frags.append(text(545, 235, "C", size=11, color="#1d4ed8", bold=True))
    frags.append(text(340, 140, "I_C2 = β_npn · I_B2", size=11, color="#1d4ed8"))

    # 2. Колектор Q1 з'єднаний з базою Q2
    frags.append(line(280, 178, 280, 280, color="#b91c1c", sw=2))
    frags.append(arrow(280, 280, 532, 280, color="#b91c1c", sw=2))
    frags.append(text(295, 195, "C", size=11, color="#b91c1c", bold=True))
    frags.append(text(380, 295, "I_C1 = β_pnp · I_B1", size=11, color="#b91c1c"))

    # Спускові тригери
    frags.append(arrow(770, 240, 680, 280, color="#d97706", sw=2))
    tb_trig1, _, _ = textbox(770, 215, "Тригерний струм I_trig+\n(Вхід V_in > VDD + 0.5V)", size=11, pad=6, fill="#fffbeb", stroke="#d97706", bold=True)
    frags.append(tb_trig1)

    frags.append(arrow(90, 190, 160, 150, color="#d97706", sw=2))
    tb_trig2, _, _ = textbox(90, 225, "Тригерний струм I_trig−\n(Вхід V_in < GND − 0.5V)", size=11, pad=6, fill="#fffbeb", stroke="#d97706", bold=True)
    frags.append(tb_trig2)

    # Тригер dV/dt
    frags.append(rect(460, 80, 80, 35, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(500, 95, "C_well", size=11, color="#334155", bold=True))
    frags.append(text(500, 108, "dV/dt", size=9, color="#64748b"))
    frags.append(line(500, 50, 500, 80, color="#64748b", sw=1.5))
    frags.append(arrow(500, 115, 500, 150, color="#64748b", sw=1.5))

    # Центральний блок: умова спрацьовування
    tb_crit, _, _ = textbox(420, 370, "Умова регенеративної защіпки: β_pnp · β_npn ≥ 1 та I_trig · R_sub ≥ V_BE(on)\nПісля відкриття струм обмежений лише опором ліній та потужністю джерела",
                            size=11, pad=8, fill="#ffffff", stroke="#b91c1c", sw=1.8, bold=True)
    frags.append(tb_crit)

    return render(os.path.join(IMG_DIR, "scr-equivalent-circuit.svg"), w, h, *frags)


def fig_iv_curve():
    """Фігура 3: Вольт-амперна характеристика защіпання (S-подібна крива Snapback/тиристора)."""
    w, h = 860, 480
    frags = []

    # Осі координат
    frags.append(arrow(100, 400, 780, 400, color=LINE, sw=2))
    frags.append(text(760, 425, "Напруга V (VDD − GND)", size=12, color=INK, bold=True))

    frags.append(arrow(100, 400, 100, 50, color=LINE, sw=2))
    frags.append(text(95, 40, "Струм I_DD", size=12, color=INK, bold=True))

    # 1. Робоча напруга V_DD_nom
    frags.append(line(360, 400, 360, 70, color="#94a3b8", sw=1.2, dash="4,4"))
    frags.append(text(360, 420, "V_nom (3.3 В)", size=11, color="#64748b", bold=True))

    # 2. Крива I-V (Стан 1: вимкнений)
    frags.append(line(100, 395, 560, 390, color="#16a34a", sw=2.5))
    frags.append(text(240, 375, "Нормальний стан (I_витоку < 1 мкА)", size=11, color="#16a34a", bold=True))

    # Точка спрацьовування
    frags.append(circle(560, 388, 6, fill="#ea580c", stroke="#ffffff", sw=1.5))
    frags.append(line(560, 400, 560, 388, color="#ea580c", sw=1.2, dash="3,3"))
    frags.append(text(560, 420, "V_trig (поріг спрацьовування)", size=11, color="#ea580c", bold=True))
    frags.append(text(590, 380, "I_trig", size=11, color="#ea580c", bold=True))

    # 3. Область негативного диференційного опору
    frags.append(line(560, 388, 200, 260, color="#dc2626", sw=2.5, dash="6,4"))
    frags.append(text(410, 310, "Зрив у защіпку (від'ємний опір dV/dI < 0)", size=11, color="#dc2626", italic=True))

    # 4. Точка утримання
    frags.append(circle(200, 260, 6, fill="#b91c1c", stroke="#ffffff", sw=1.5))
    frags.append(line(200, 400, 200, 260, color="#b91c1c", sw=1.2, dash="3,3"))
    frags.append(text(200, 420, "V_hold (0.8–1.5 В)", size=11, color="#b91c1c", bold=True))
    frags.append(line(100, 260, 200, 260, color="#b91c1c", sw=1.2, dash="3,3"))
    frags.append(text(65, 263, "I_hold", size=11, color="#b91c1c", bold=True))

    # 5. Стан короткого замикання
    frags.append(line(200, 260, 250, 70, color="#b91c1c", sw=3))
    frags.append(text(285, 120, "Замкнений тиристор (Latch-up)", size=12, color="#b91c1c", bold=True))
    frags.append(text(285, 140, "Струм сотні мА – Ампери (R_on < 2 Ом)", size=11, color="#b91c1c"))

    # 6. Навантажувальна пряма джерела живлення
    frags.append(line(360, 400, 210, 80, color="#2563eb", sw=1.8, dash="5,3"))
    frags.append(text(340, 200, "Навантажувальна пряма джерела", size=11, color="#2563eb", bold=True))

    # Стабільна робоча точка у стані защіпки
    frags.append(circle(234, 131, 6, fill="#2563eb", stroke="#ffffff", sw=1.5))
    frags.append(text(150, 125, "Стабільна точка защіпки", size=11, color="#2563eb", bold=True))
    frags.append(text(150, 140, "(V_op ≈ 1.2 В, I_op >> I_hold)", size=10, color="#2563eb"))

    # Пояснювальний висновок
    tb_res, _, _ = textbox(560, 160, "Оскільки V_nom > V_hold, схема залишається\nу замкненому аварійному стані нескінченно довго.\nЄдиний спосіб виходу — повне зняття живлення\nабо зниження напруги нижче V_hold.",
                           size=11, pad=8, fill="#fef2f2", stroke="#ef4444", bold=False)
    frags.append(tb_res)

    return render(os.path.join(IMG_DIR, "latchup-iv-curve.svg"), w, h, *frags)


def fig_guard_rings():
    """Фігура 4: Конструкція захисних охоронних кілець (Guard Rings) та tap-контактів."""
    w, h = 860, 460
    frags = []

    # Топологія зверху (Top-down view)
    frags.append(rect(40, 60, 780, 360, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=8))
    frags.append(text(430, 40, "Топологічний захист: подвійні охоронні кільця та Tap-комірки", size=14, color=INK, bold=True))

    # Лівий блок: PMOS в N-Well
    frags.append(rect(70, 90, 340, 300, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(240, 115, "N-Well (PMOS область)", size=12, color="#b45309", bold=True))

    # Зовнішнє кільце n+ (VDD Guard Ring)
    frags.append(rect(90, 135, 300, 235, fill="#ffedd5", stroke="#ea580c", sw=1.8, rx=4))
    frags.append(text(240, 155, "n⁺ Охоронне кільце (підключено до VDD)", size=11, color="#9a3412", bold=True))

    # Внутрішня зона PMOS
    frags.append(rect(130, 180, 220, 170, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=4))
    frags.append(text(240, 205, "Дифузія витоків/стоків p⁺ (PMOS)", size=11, color="#991b1b", bold=True))
    frags.append(rect(160, 230, 70, 100, fill="#fca5a5", stroke="#dc2626", sw=1.2, rx=3))
    frags.append(text(195, 280, "p⁺ Витік", size=11, color="#7f1d1d", bold=True))
    frags.append(rect(250, 230, 70, 100, fill="#fca5a5", stroke="#dc2626", sw=1.2, rx=3))
    frags.append(text(285, 280, "p⁺ Стік", size=11, color="#7f1d1d", bold=True))

    # Правий блок: NMOS у P-Substrate
    frags.append(rect(450, 90, 340, 300, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=6))
    frags.append(text(620, 115, "P-Substrate (NMOS область)", size=12, color="#334155", bold=True))

    # Зовнішнє кільце p+ (GND Guard Ring)
    frags.append(rect(470, 135, 300, 235, fill="#fee2e2", stroke="#dc2626", sw=1.8, rx=4))
    frags.append(text(620, 155, "p⁺ Охоронне кільце (підключено до GND)", size=11, color="#991b1b", bold=True))

    # Внутрішня зона NMOS
    frags.append(rect(510, 180, 220, 170, fill="#ffedd5", stroke="#f97316", sw=1.5, rx=4))
    frags.append(text(620, 205, "Дифузія витоків/стоків n⁺ (NMOS)", size=11, color="#9a3412", bold=True))
    frags.append(rect(540, 230, 70, 100, fill="#fed7aa", stroke="#ea580c", sw=1.2, rx=3))
    frags.append(text(575, 280, "n⁺ Стік", size=11, color="#7c2d12", bold=True))
    frags.append(rect(630, 230, 70, 100, fill="#fed7aa", stroke="#ea580c", sw=1.2, rx=3))
    frags.append(text(665, 280, "n⁺ Витік", size=11, color="#7c2d12", bold=True))

    # Стрілки збору носіїв заряду
    frags.append(arrow(390, 280, 470, 280, color="#dc2626", sw=2))
    frags.append(text(430, 265, "Дірки", size=10, color="#dc2626", bold=True))
    frags.append(text(430, 300, "перехоплюються\nкільцем GND", size=9, color="#dc2626"))

    # Пояснювальний блок знизу
    tb_guard, _, _ = textbox(430, 435, "Охоронні кільця збирають інжектовані носії заряду та знижують опори R_well і R_sub у 10–50 разів",
                             size=11, pad=6, fill="#ffffff", stroke="#059669", bold=True)
    frags.append(tb_guard)

    return render(os.path.join(IMG_DIR, "guard-ring-topology.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_cross_section()
    fig_scr_equivalent()
    fig_iv_curve()
    fig_guard_rings()
    print("Всі SVG-фігури згенеровано успішно.")
