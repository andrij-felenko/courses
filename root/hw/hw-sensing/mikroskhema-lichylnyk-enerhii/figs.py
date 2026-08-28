# -*- coding: utf-8 -*-
"""Фігури до теми «Мікросхема-лічильник енергії».
Запуск: python figs.py  → генерує SVG у ./img/
"""
import sys
import os

# Додаємо шлях до svgkit у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Архітектура метрологічного AFE ──────────────────────────────────────────
def fig_afe_architecture():
    W, H = 1000, 620
    frags = []

    # Головний заголовок
    frags.append(text(W / 2, 28, "Внутрішня архітектура метрологічного AFE (ADE7953 / ATM90E32)", size=16, bold=True))

    # Зовнішній контур мікросхеми
    ic_x, ic_y, ic_w, ic_h = 160, 55, 680, 520
    frags.append(rect(ic_x, ic_y, ic_w, ic_h, fill="#fafbfc", stroke=LINE, sw=2, rx=12))
    frags.append(text(ic_x + 150, ic_y + 24, "Метрологічна IC (Energy Metering AFE)", size=13, bold=True, color=MUTED))

    # --- Аналогові входи (зліва за межами IC) ---
    # Канал струму фази IA
    frags.append(textbox(80, 110, "Шунт фази\n(±30 мВ)", size=11, fill="#fff", stroke=LINE)[0])
    frags.append(arrow(130, 110, 190, 110, color=POS, sw=1.8))
    frags.append(text(160, 100, "IA±", size=11, bold=True, color=POS))

    # Канал струму нейтралі IB
    frags.append(textbox(80, 240, "Трансформатор\nнейтралі IB", size=11, fill="#fff", stroke=LINE)[0])
    frags.append(arrow(130, 240, 190, 240, color=NEG, sw=1.8))
    frags.append(text(160, 230, "IB±", size=11, bold=True, color=NEG))

    # Канал напруги VP-VN
    frags.append(textbox(80, 410, "Дільник 230 В\n(±500 мВ)", size=11, fill="#fff", stroke=LINE)[0])
    frags.append(arrow(130, 410, 190, 410, color=FIELD, sw=1.8))
    frags.append(text(160, 400, "VP-VN", size=11, bold=True, color=FIELD))

    # --- Вхідні PGA підсилювачі ---
    frags.append(textbox(220, 110, "PGA\n1×..22×", size=11, fill="#f4f6f8", stroke=LINE)[0])
    frags.append(textbox(220, 240, "PGA\n1×..22×", size=11, fill="#f4f6f8", stroke=LINE)[0])
    frags.append(textbox(220, 410, "PGA\n1×", size=11, fill="#f4f6f8", stroke=LINE)[0])

    frags.append(arrow(250, 110, 280, 110))
    frags.append(arrow(250, 240, 280, 240))
    frags.append(arrow(250, 410, 280, 410))

    # --- Sigma-Delta АЦП (24 біти) ---
    frags.append(textbox(335, 110, "24-bit ΣΔ АЦП\n1.23 МГц / Sinc³", size=11, fill="#e8f4fd", stroke=NEG)[0])
    frags.append(textbox(335, 240, "24-bit ΣΔ АЦП\n1.23 МГц / Sinc³", size=11, fill="#e8f4fd", stroke=NEG)[0])
    frags.append(textbox(335, 410, "24-bit ΣΔ АЦП\n1.23 МГц / Sinc³", size=11, fill="#e8f4fd", stroke=NEG)[0])

    frags.append(arrow(395, 110, 435, 110))
    frags.append(arrow(395, 240, 435, 240))
    frags.append(arrow(395, 410, 435, 410))

    # --- Блок DSP та цифрової фільтрації (HPF, Інтегратор, PHCAL) ---
    dsp_box = rect(435, 80, 175, 460, fill="#fdfbf7", stroke="#d97706", sw=1.5, rx=8)
    frags.append(dsp_box)
    frags.append(text(522, 100, "DSP ЯДРО МЕТРОЛОГІЇ", size=11, bold=True, color="#b45309"))

    # Фільтри в DSP
    frags.append(textbox(522, 135, "HPF (зріз DC) +\nІнтегратор Роговського", size=10, fill="#fff", stroke=LINE)[0])
    frags.append(textbox(522, 205, "PHCAL: калібрування\nфазового зсуву кута φ", size=10, fill="#fff", stroke=POS)[0])
    frags.append(textbox(522, 285, "Множники p(t) = v·i\nта обчислювач True RMS", size=10, fill="#fff", stroke=LINE)[0])
    frags.append(textbox(522, 365, "Калібрувальні регістри\n(Gain, Offset, Phase)", size=10, fill="#fff", stroke=FIELD)[0])
    frags.append(textbox(522, 450, "Блок Anti-Tamper:\nпорівняння |IA - IB|", size=10, fill="#fff", stroke=POS)[0])

    frags.append(arrow(610, 200, 650, 200))
    frags.append(arrow(610, 290, 650, 290))
    frags.append(arrow(610, 450, 650, 450))

    # --- Накопичувачі та вихідні блоки ---
    frags.append(textbox(725, 190, "Акумулятори енергії\nAENERGY / RENERGY\n(кВт·год / вар·год)", size=11, fill="#edf7ed", stroke=FIELD)[0])
    frags.append(textbox(725, 290, "Регістри RMS & PF\nVRMS, IRMS, P, Q, S", size=11, fill="#f4f6f8", stroke=LINE)[0])
    frags.append(textbox(725, 440, "Генератор імпульсів CF\nCF1 (P), CF2 (Q/I)", size=11, fill="#fef2f2", stroke=POS)[0])

    # Виходи з IC праворуч
    frags.append(arrow(805, 200, 875, 200, color=LINE, sw=1.8))
    frags.append(textbox(925, 200, "SPI / I2C шина\nдо MCU", size=11, bold=True, fill="#fff", stroke=LINE)[0])

    frags.append(arrow(805, 440, 875, 440, color=POS, sw=1.8))
    frags.append(textbox(925, 440, "Імпульсні виходи\nCF1, CF2 (LED)", size=11, bold=True, fill="#fff", stroke=POS)[0])

    render(os.path.join(IMG, "energy-meter-afe-architecture.svg"), W, H, *frags)


# ── 2. Фазовий зсув і похибка вимірювання ─────────────────────────────────────
def fig_phase_error():
    W, H = 880, 460
    frags = []

    frags.append(text(W / 2, 28, "Вплив фазової похибки датчика струму на вимірювання потужності", size=16, bold=True))

    # Векторна діаграма ліворуч
    diag_cx, diag_cy = 200, 240
    frags.append(circle(diag_cx, diag_cy, 130, fill="#fafbfc", stroke=LINE, sw=1))
    frags.append(line(diag_cx - 140, diag_cy, diag_cx + 140, diag_cy, color=MUTED, sw=1))
    frags.append(line(diag_cx, diag_cy - 140, diag_cx, diag_cy + 140, color=MUTED, sw=1))

    # Вектор напруги V (по осі X)
    frags.append(arrow(diag_cx, diag_cy, diag_cx + 120, diag_cy, color=FIELD, sw=2.5))
    frags.append(text(diag_cx + 130, diag_cy - 8, "Вектор напруги V", size=12, bold=True, color=FIELD, anchor="start"))

    # Справжній вектор струму I (під кутом phi = 60 град, cos phi = 0.5)
    ix = diag_cx + 55
    iy = diag_cy + 95
    frags.append(arrow(diag_cx, diag_cy, ix, iy, color=NEG, sw=2.2))
    frags.append(text(ix + 10, iy + 14, "Справжній струм I (φ = 60°)", size=11, bold=True, color=NEG, anchor="start"))

    # Спотворений вектор струму I' через затримку CT (зсув на кут theta = +2°)
    i_err_x = diag_cx + 38
    i_err_y = diag_cy + 105
    frags.append(line(diag_cx, diag_cy, i_err_x, i_err_y, color=POS, sw=2, dash="3,3"))
    frags.append(text(i_err_x - 10, i_err_y + 22, "Виміряний I' (φ + θ_err)", size=11, bold=True, color=POS, anchor="end"))

    # Дуга кута зсуву
    frags.append(text(diag_cx + 45, diag_cy + 40, "φ (кут навантаження)", size=11, color=MUTED))
    frags.append(text(diag_cx + 70, diag_cy + 120, "θ_err (похибка CT/RC)", size=11, color=POS))

    # Права частина — кількісний аналіз похибки
    rx = 440
    frags.append(textbox(rx + 200, 100, "Формула активної потужності:\nP_дійсна = V · I · cos(φ)\nP_виміряна = V · I · cos(φ + θ_err)", size=12, fill="#fdfbf7", stroke="#d97706")[0])

    # Порівняння для двох випадків
    frags.append(textbox(rx + 200, 210, "Випадок 1: Чисто активне навантаження (cos φ = 1.0, φ = 0°)\n  θ_err = 0.5°  →  cos(0.5°) = 0.99996\n  Відносна похибка потужності = лише -0.004%  (непомітна)", size=11, fill="#edf7ed", stroke=FIELD)[0])

    frags.append(textbox(rx + 200, 320, "Випадок 2: Індуктивне навантаження (cos φ = 0.5, φ = 60°)\n  θ_err = 0.5°  →  cos(60.5°) = 0.4924\n  Відносна похибка потужності = (0.4924 - 0.5)/0.5 = -1.52%!\n  (Помилка зростає у ~380 разів через множник tan φ)", size=11, fill="#fef2f2", stroke=POS)[0])

    # Нижній висновок
    frags.append(text(rx + 200, 410, "Регістр PHCAL усуває θ_err субмікросекундною цифровою затримкою", size=12, bold=True, color=INK))

    render(os.path.join(IMG, "phase-calibration-error.svg"), W, H, *frags)


# ── 3. Топологія Anti-Tamper ──────────────────────────────────────────────────
def fig_anti_tamper():
    W, H = 920, 520
    frags = []

    frags.append(text(W / 2, 28, "Апаратний захист від крадіжки електроенергії (Anti-Tamper)", size=16, bold=True))

    # Мережеві дроти зліва
    frags.append(text(60, 100, "Фаза L (Вхід)", size=12, bold=True, color=POS))
    frags.append(text(60, 340, "Нейтраль N (Вхід)", size=12, bold=True, color=NEG))

    # Лінії живлення крізь лічильник
    # Фазний провід
    frags.append(line(120, 110, 240, 110, color=POS, sw=3))
    # Шунт на фазі
    frags.append(rect(240, 95, 60, 30, fill="#fff", stroke=POS, sw=2))
    frags.append(text(270, 115, "Шунт Rш", size=11, bold=True, color=POS))
    frags.append(line(300, 110, 680, 110, color=POS, sw=3))

    # Нейтральний провід
    frags.append(line(120, 350, 440, 350, color=NEG, sw=3))
    # Трансформатор струму на нейтралі
    frags.append(circle(470, 350, 25, fill="#fff", stroke=NEG, sw=2))
    frags.append(text(470, 355, "CT", size=12, bold=True, color=NEG))
    frags.append(line(500, 350, 680, 350, color=NEG, sw=3))

    # Навантаження праворуч
    frags.append(rect(680, 80, 90, 300, fill="#f4f6f8", stroke=LINE, sw=2, rx=8))
    frags.append(text(725, 230, "Навантаження\nспоживача\n(Квартира / Дім)", size=12, bold=True, color=INK))

    # Лічильник — внутрішній блок AFE
    afe_x, afe_y, afe_w, afe_h = 200, 160, 420, 160
    frags.append(rect(afe_x, afe_y, afe_w, afe_h, fill="#fdfbf7", stroke="#d97706", sw=1.8, rx=10))
    frags.append(text(afe_x + afe_w / 2, afe_y + 24, "Метрологічна мікросхема (Anti-Tamper Logic)", size=12, bold=True, color="#b45309"))

    # Сенсорні зв'язки від шунта і CT до IC
    frags.append(line(255, 125, 255, 200, color=POS, sw=1.5, dash="3,3"))
    frags.append(line(285, 125, 285, 200, color=POS, sw=1.5, dash="3,3"))
    frags.append(arrow(270, 200, 270, 215, color=POS, sw=1.5))
    frags.append(text(270, 230, "Канал IA\n(Фаза)", size=10, bold=True, color=POS))

    frags.append(line(470, 325, 470, 255, color=NEG, sw=1.5, dash="3,3"))
    frags.append(arrow(470, 255, 470, 240, color=NEG, sw=1.5))
    frags.append(text(470, 230, "Канал IB\n(Нейтраль)", size=10, bold=True, color=NEG))

    # Логіка вибору каналу
    frags.append(textbox(afe_x + 210, afe_y + 110, "Порівняння |IA - IB| > 6.25%:\n• Якщо рівні → облік за IA\n• Якщо нерівні → тривога TAMPER та облік за max(IA, IB)", size=10.5, fill="#fff", stroke=POS)[0])

    # Шлях витоку / шунтування (крадіжка)
    frags.append(line(160, 110, 160, 50, color="#dc2626", sw=1.8, dash="4,4"))
    frags.append(line(160, 50, 650, 50, color="#dc2626", sw=1.8, dash="4,4"))
    frags.append(arrow(650, 50, 650, 110, color="#dc2626", sw=1.8))
    frags.append(textbox(400, 45, "Спроба байпасу фази в обхід шунта лічильника (шунтування дротом)", size=10.5, fill="#fef2f2", stroke="#dc2626")[0])

    # Пояснення результату
    frags.append(textbox(W / 2, 470, "Результат захисту: струм нейтралі IB лишається повним (100%), IC детектує дисбаланс,\nвмикає прапорець несанкціонованого втручання та нараховує енергію за каналом IB.", size=11, bold=True, fill="#edf7ed", stroke=FIELD)[0])

    render(os.path.join(IMG, "anti-tamper-topology.svg"), W, H, *frags)


# ── 4. Формування імпульсів CF ────────────────────────────────────────────────
def fig_pulse_accumulator():
    W, H = 900, 480
    frags = []

    frags.append(text(W / 2, 28, "Апаратний акумулятор енергії та формування повірочних імпульсів CF", size=16, bold=True))

    # Блок 1: Миттєва потужність p(t)
    frags.append(textbox(120, 110, "Миттєва потужність\np(t) = v(t) · i(t)\n(частота 8 кГц)", size=11, fill="#f4f6f8", stroke=LINE)[0])
    frags.append(arrow(195, 110, 245, 110))

    # Блок 2: Фільтр LPF / Активна потужність P
    frags.append(textbox(315, 110, "Фільтр LPF / Усереднення\nАктивна потужність P\n(регістр AWATT / BWATT)", size=11, fill="#e8f4fd", stroke=NEG)[0])
    frags.append(arrow(390, 110, 440, 110))

    # Блок 3: Внутрішній накопичувач енергії високої роздільності
    frags.append(textbox(545, 110, "Внутрішній накопичувач\nAcc = Acc + P · Δt\n(48-бітний акумулятор)", size=11, fill="#edf7ed", stroke=FIELD)[0])
    frags.append(arrow(650, 110, 700, 110))

    # Блок 4: Компаратор порогу кванта енергії (CFxDEN)
    frags.append(textbox(790, 110, "Компаратор порогу\nAcc ≥ CF_DEN\n(поріг кванта енергії)", size=11, fill="#fdfbf7", stroke="#d97706")[0])

    # Зворотний зв'язок від компаратора (скидання / віднімання порогу)
    frags.append(line(790, 155, 790, 210, color="#d97706", sw=1.5, dash="3,3"))
    frags.append(line(790, 210, 545, 210, color="#d97706", sw=1.5, dash="3,3"))
    frags.append(arrow(545, 210, 545, 155, color="#d97706", sw=1.5))
    frags.append(text(670, 225, "Acc = Acc - CF_DEN (збереження залишку)", size=10, color="#b45309"))

    # Вихід компаратора вниз до формувача імпульсу
    frags.append(arrow(790, 155, 790, 270, color=POS, sw=2))
    frags.append(text(805, 240, "Переповнення", size=10, bold=True, color=POS))

    # Блок 5: Формувач каліброваного імпульсу CF
    frags.append(textbox(790, 310, "Формувач імпульсу\nТривалість 80 мс\n(відкритий колектор / Push-Pull)", size=11, fill="#fef2f2", stroke=POS)[0])
    frags.append(arrow(790, 360, 790, 400, color=POS, sw=2))

    # Вихід на світлодіод лічильника та оптичну повірочну головку
    frags.append(textbox(790, 435, "Вихідний пін CF1 / CF2\n(Світлодіод: напр. 3200 імп/кВт·год)", size=11, bold=True, fill="#fff", stroke=POS)[0])

    # Ліва нижня частина: графік накопичення та імпульсів
    gx, gy, gw, gh = 80, 230, 560, 200
    frags.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(gx + 160, gy + 22, "Графік накопичення енергії та імпульсів", size=11, bold=True, color=MUTED))

    # Вісь часу та накопичення
    frags.append(line(gx + 40, gy + 110, gx + 520, gy + 110, color=LINE, sw=1.2))
    frags.append(line(gx + 40, gy + 175, gx + 520, gy + 175, color=LINE, sw=1.2))

    frags.append(text(gx + 30, gy + 50, "Acc", size=10, bold=True, color=FIELD))
    frags.append(text(gx + 30, gy + 150, "CF", size=10, bold=True, color=POS))

    # Лінія порогу CF_DEN
    frags.append(line(gx + 40, gy + 55, gx + 520, gy + 55, color="#d97706", sw=1, dash="4,4"))
    frags.append(text(gx + 480, gy + 48, "Поріг CF_DEN", size=9.5, color="#d97706"))

    # Пилоподібний графік накопичення (3 цикли)
    # Цикл 1
    frags.append(line(gx + 60, gy + 110, gx + 180, gy + 55, color=FIELD, sw=2))
    frags.append(line(gx + 180, gy + 55, gx + 180, gy + 110, color=FIELD, sw=1.2, dash="2,2"))
    # Цикл 2
    frags.append(line(gx + 180, gy + 110, gx + 300, gy + 55, color=FIELD, sw=2))
    frags.append(line(gx + 300, gy + 55, gx + 300, gy + 110, color=FIELD, sw=1.2, dash="2,2"))
    # Цикл 3
    frags.append(line(gx + 300, gy + 110, gx + 420, gy + 55, color=FIELD, sw=2))
    frags.append(line(gx + 420, gy + 55, gx + 420, gy + 110, color=FIELD, sw=1.2, dash="2,2"))

    # Імпульси CF (низький рівень 80 мс при переповненні)
    frags.append(line(gx + 60, gy + 140, gx + 180, gy + 140, color=POS, sw=2))
    frags.append(line(gx + 180, gy + 140, gx + 180, gy + 170, color=POS, sw=2))
    frags.append(line(gx + 180, gy + 170, gx + 210, gy + 170, color=POS, sw=2))
    frags.append(line(gx + 210, gy + 170, gx + 210, gy + 140, color=POS, sw=2))
    frags.append(line(gx + 210, gy + 140, gx + 300, gy + 140, color=POS, sw=2))
    frags.append(line(gx + 300, gy + 140, gx + 300, gy + 170, color=POS, sw=2))
    frags.append(line(gx + 300, gy + 170, gx + 330, gy + 170, color=POS, sw=2))
    frags.append(line(gx + 330, gy + 170, gx + 330, gy + 140, color=POS, sw=2))
    frags.append(line(gx + 330, gy + 140, gx + 420, gy + 140, color=POS, sw=2))
    frags.append(line(gx + 420, gy + 140, gx + 420, gy + 170, color=POS, sw=2))
    frags.append(line(gx + 420, gy + 170, gx + 450, gy + 170, color=POS, sw=2))
    frags.append(line(gx + 450, gy + 170, gx + 450, gy + 140, color=POS, sw=2))
    frags.append(line(gx + 450, gy + 140, gx + 500, gy + 140, color=POS, sw=2))

    frags.append(text(gx + 250, gy + 190, "t_pulse = 80 мс (1 імпульс = 1 квант енергії)", size=10, color=POS))

    render(os.path.join(IMG, "pulse-accumulator-cf.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_afe_architecture()
    fig_phase_error()
    fig_anti_tamper()
    fig_pulse_accumulator()
    print("All figures generated successfully.")
