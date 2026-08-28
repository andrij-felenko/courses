# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Ємнісний давач вологості».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Імена файлів — slug-only, без номерів (AUTHORING §2/§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(IMG_DIR, exist_ok=True)


# ── cross-section: будова ємнісної сенсорної комірки на кристалі ─────────────
def fig_cross_section():
    W, H = 840, 420
    parts = []

    cx = W / 2
    top = 50

    # Молекули води в повітрі над давачем
    parts.append(text(cx, top + 10, "молекули водяної пари (H₂O) у навколишньому повітрі", size=13, bold=True, color=NEG))
    for dx in (-260, -180, -100, -20, 60, 140, 220, 290):
        parts.append(circle(cx + dx, top + 34, 5, fill="#cfe0f5", stroke=NEG, sw=1.5))
        parts.append(text(cx + dx, top + 37, "w", size=9, bold=True, color=NEG))
        parts.append(arrow(cx + dx, top + 44, cx + dx, top + 74, color=NEG, sw=1.4))

    # Сенсорний стек
    sy = top + 80
    sw = 580
    sx = cx - sw / 2

    # Верхній пористий електрод (золото/платина)
    parts.append(rect(sx, sy, sw, 14, fill="#f9e79f", stroke="#b7950b", sw=1.8, rx=2))
    # Пори / перфорація
    for i in range(15):
        px = sx + 20 + i * ((sw - 40) / 14)
        parts.append(rect(px - 4, sy - 1, 8, 16, fill=BG, stroke="#b7950b", sw=1.2))
    parts.append(text(sx + sw + 12, sy + 11, "верхній пористий електрод (Au/Pt, ~20 нм)", size=11.5, bold=True, color="#7d6608", anchor="start"))

    # Полімерний вологопоглинаючий діелектрик
    py = sy + 14
    ph = 70
    parts.append(rect(sx, py, sw, ph, fill="#e8f8f5", stroke=FIELD, sw=2))
    # Поглинуті молекули води всередині полімеру
    for row in range(3):
        for col in range(12):
            mx = sx + 25 + col * 44 + (row % 2) * 20
            my = py + 15 + row * 20
            parts.append(circle(mx, my, 4.5, fill="#aed6f1", stroke=NEG, sw=1.2))
    parts.append(text(sx + sw + 12, py + 26, "гігроскопічний полімер (поліімід / CAB)", size=12, bold=True, color=FIELD, anchor="start"))
    parts.append(text(sx + sw + 12, py + 44, "товщина d ≈ 1…2 мкм", size=11, italic=True, color=MUTED, anchor="start"))
    parts.append(text(sx + sw + 12, py + 60, "ε сухого ≈ 3…4 → ε зволоженого росте", size=11, bold=True, color=FIELD, anchor="start"))

    # Нижній суцільний електрод
    by = py + ph
    parts.append(rect(sx, by, sw, 16, fill="#d5dbdb", stroke="#7f8c8d", sw=1.8, rx=2))
    parts.append(text(sx + sw + 12, by + 12, "нижній суцільний електрод (Pt/Ti)", size=11.5, bold=True, color=INK, anchor="start"))

    # Ізоляція SiO2
    iy = by + 16
    parts.append(rect(sx, iy, sw, 22, fill="#f2f3f4", stroke="#bdc3c7", sw=1.5))
    parts.append(text(sx + sw + 12, iy + 15, "ізоляція SiO₂", size=11, color=MUTED, anchor="start"))

    # Кремнієва підкладка (Si Substrate)
    suby = iy + 22
    parts.append(rect(sx, suby, sw, 40, fill="#eaeded", stroke="#95a5a6", sw=2, rx=3))
    parts.append(text(cx, suby + 25, "кремнієва підкладка кристала (Si Substrate + вбудований нагрівач і термометр)", size=12, bold=True, color="#515a5a"))

    # Виводи ємності C
    parts.append(line(sx - 30, sy + 7, sx, sy + 7, color=INK, sw=2))
    parts.append(line(sx - 30, by + 8, sx, by + 8, color=INK, sw=2))
    parts.append(line(sx - 30, sy + 7, sx - 30, by + 8, color=INK, sw=2))
    parts.append(circle(sx - 30, (sy + by) / 2 + 7, 4, fill=BG, stroke=INK, sw=2))
    parts.append(text(sx - 42, (sy + by) / 2 + 11, "C(RH)", size=13, bold=True, color=INK, anchor="end"))

    # Підсумковий блок
    box, bw, bh = textbox(W / 2, H - 30,
                          "Пара проникає крізь пори верхнього електрода → поляризує полімер → ємність C росте прямо пропорційно RH",
                          size=12.5, pad=10, fill=FILL, bold=True)
    parts.append(box)

    render(os.path.join(IMG_DIR, "cross-section.svg"), W, H, *parts,
           title="Будова ємнісної сенсорної комірки на кристалі")


# ── dipole-polarization: механізм поляризації диполів води ──────────────────
def fig_dipole_polarization():
    W, H = 840, 380
    parts = []

    half_w = 370
    top = 45
    h_box = 245

    # Ліва половина: Сухий полімер
    lx = 35
    parts.append(rect(lx, top, half_w, h_box, fill="#fdfefe", stroke=MUTED, sw=1.8, rx=6))
    parts.append(text(lx + half_w / 2, top + 26, "Сухий полімер (RH ≈ 0 %)", size=14, bold=True, color=INK))
    parts.append(text(lx + half_w / 2, top + 48, "ε_polymer ≈ 3.0…3.8", size=12, bold=True, color=FIELD))

    # Ланцюги полімеру з малою поляризацією
    for r in range(4):
        yy = top + 80 + r * 34
        parts.append(line(lx + 40, yy, lx + half_w - 40, yy, color="#a2d9ce", sw=3))
        for c in range(5):
            xx = lx + 65 + c * 60 + (r % 2) * 20
            parts.append(circle(xx, yy, 6, fill="#76d7c4", stroke=FIELD, sw=1.2))

    parts.append(text(lx + half_w / 2, top + 215, "Лише слабка електронна поляризація", size=11.5, color=MUTED))
    parts.append(text(lx + half_w / 2, top + 232, "Ємність базова: C₀ ≈ 10…20 пФ", size=12, bold=True, color=INK))

    # Права половина: Зволожений полімер
    rx = W - half_w - 35
    parts.append(rect(rx, top, half_w, h_box, fill="#ebf5fb", stroke=NEG, sw=2, rx=6))
    parts.append(text(rx + half_w / 2, top + 26, "Зволожений полімер (RH ≈ 80 %)", size=14, bold=True, color=NEG))
    parts.append(text(rx + half_w / 2, top + 48, "ε_water ≈ 80 (дипольний стрибок)", size=12, bold=True, color=NEG))

    # Полімерні ланцюги + орієнтовані диполі води
    for r in range(4):
        yy = top + 80 + r * 34
        parts.append(line(rx + 40, yy, rx + half_w - 40, yy, color="#aed6f1", sw=2.5))
        for c in range(5):
            xx = rx + 65 + c * 60 + (r % 2) * 20
            # Диполь H2O: червоний (+) та синій (-)
            parts.append(line(xx - 10, yy - 5, xx + 10, yy + 5, color=INK, sw=1.5))
            parts.append(circle(xx - 10, yy - 5, 5, fill=POS, stroke=POS, sw=1))
            parts.append(circle(xx + 10, yy + 5, 5, fill=NEG, stroke=NEG, sw=1))

    parts.append(text(rx + half_w / 2, top + 215, "Орієнтаційна поляризація диполів H₂O", size=11.5, bold=True, color=NEG))
    parts.append(text(rx + half_w / 2, top + 232, "Ємність зростає: C = C₀ · (1 + α · RH)", size=12, bold=True, color=NEG))

    # Підсумок унизу
    box, bw, bh = textbox(W / 2, H - 28,
                          "Дипольний момент води (1.85 D) у 20 разів перевищує діелектричну проникність полімеру — звідси висока чутливість",
                          size=12, pad=10, fill=FILL)
    parts.append(box)

    render(os.path.join(IMG_DIR, "dipole-polarization.svg"), W, H, *parts,
           title="Орієнтаційна поляризація диполів води в полімерній матриці")


# ── psychrometric-curve: тиск насиченої пари та проєкція точки роси ──────────
def fig_psychrometric_curve():
    W, H = 840, 420
    parts = []

    ox, oy = 110, 320
    pw, ph = 640, 240

    # Осі
    parts.append(arrow(ox, oy, ox + pw + 25, oy, color=INK, sw=2))
    parts.append(arrow(ox, oy, ox, oy - ph - 20, color=INK, sw=2))
    parts.append(text(ox + pw + 20, oy + 28, "Температура повітря T (°C)", size=12, bold=True, anchor="end"))
    parts.append(text(ox - 15, oy - ph - 15, "Парціальний тиск водяної пари e (гПа)", size=12, bold=True, anchor="start"))

    # Позначки шкали
    # T: -10, 0, 10, 20, 30, 40
    t_coords = [
        (-10, ox + 40),
        (0,   ox + 130),
        (10,  ox + 230),
        (20,  ox + 350),
        (30,  ox + 490),
        (40,  ox + 630)
    ]
    for val, xpos in t_coords:
        parts.append(line(xpos, oy, xpos, oy + 6, color=INK, sw=1.5))
        parts.append(text(xpos, oy + 20, "%d°" % val, size=11, color=MUTED))

    # Крива насиченої пари e_sat(T)
    # y(T) = oy - ph * (e(T) / e(40))
    # приблизні точки експоненти e_sat: -10->2.8, 0->6.1, 10->12.3, 20->23.4, 30->42.4, 40->73.8
    curve_pts = [
        (ox + 40,  oy - 10),
        (ox + 130, oy - 20),
        (ox + 230, oy - 42),
        (ox + 350, oy - 80),
        (ox + 490, oy - 142),
        (ox + 630, oy - 245)
    ]
    d_path = "M " + " L ".join(["%.1f %.1f" % pt for pt in curve_pts])
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.5"/>' % (d_path, POS))
    parts.append(text(ox + 520, oy - 175, "e_sat(T) — лінія насичення (100 % RH)", size=12.5, bold=True, color=POS, anchor="start"))

    # Робоча точка А: T = 30 °C, RH = 40 % -> e = 0.4 * 42.4 = 17.0 гПа
    pt_ax = ox + 490
    pt_ay = oy - 58  # 17 гПа
    parts.append(circle(pt_ax, pt_ay, 6, fill=NEG, stroke=INK, sw=1.8))
    parts.append(text(pt_ax + 12, pt_ay - 6, "Стан повітря A (30 °C, 40 % RH)", size=12, bold=True, color=NEG, anchor="start"))

    # Вертикаль до насичення e_sat(30)
    parts.append(line(pt_ax, oy, pt_ax, oy - 142, color=MUTED, sw=1.4, dash="4,4"))
    parts.append(circle(pt_ax, oy - 142, 5, fill=POS, stroke=INK, sw=1.5))
    parts.append(text(pt_ax + 12, oy - 138, "e_sat(30 °C) = 42.4 гПа", size=11, color=POS, anchor="start"))

    # Стрілка охолодження вліво до лінії роси (e = const)
    pt_dew_x = ox + 290  # ~15 °C
    parts.append(arrow(pt_ax, pt_ay, pt_dew_x + 4, pt_ay, color=FIELD, sw=2.2))
    parts.append(text((pt_ax + pt_dew_x) / 2, pt_ay - 12, "охолодження при сталому e", size=11, italic=True, color=FIELD))

    # Точка роси B
    parts.append(circle(pt_dew_x, pt_ay, 6, fill=FIELD, stroke=INK, sw=1.8))
    parts.append(text(pt_dew_x - 12, pt_ay - 12, "Точка роси B (T_dew ≈ 14.9 °C)", size=12, bold=True, color=FIELD, anchor="end"))

    # Проєкція точки роси на вісь T
    parts.append(line(pt_dew_x, pt_ay, pt_dew_x, oy, color=FIELD, sw=1.5, dash="4,4"))
    parts.append(text(pt_dew_x, oy + 20, "T_dew", size=12, bold=True, color=FIELD))

    # Підсумковий блок
    box, bw, bh = textbox(W / 2, H - 24,
                          "RH = e / e_sat(T). Охолодження повітря до T_dew призводить до 100 % RH і випадання конденсату",
                          size=12, pad=10, fill=FILL)
    parts.append(box)

    render(os.path.join(IMG_DIR, "psychrometric-curve.svg"), W, H, *parts,
           title="Крива тиску насиченої пари та визначення точки роси")


# ── sensor-architecture: блок-схема мікросхеми цифрового сенсора ─────────────
def fig_sensor_architecture():
    W, H = 860, 420
    parts = []

    # Загальний корпус IC
    ix, iy, iw, ih = 50, 45, 760, 315
    parts.append(rect(ix, iy, iw, ih, fill="#f8f9f9", stroke=INK, sw=2.2, rx=10))
    parts.append(text(ix + 24, iy + 26, "Кристал цифрового сенсора (SHT4x / HDC1080)", size=14, bold=True, color=INK, anchor="start"))

    # Лівий блок: Фізичні чутливі елементи
    bx, by, bw, bh = 75, 90, 200, 245
    parts.append(rect(bx, by, bw, bh, fill="#e8f8f5", stroke=FIELD, sw=1.8, rx=6))
    parts.append(text(bx + bw / 2, by + 24, "Сенсорний блок", size=13, bold=True, color=FIELD))

    # Ємнісна комірка
    parts.append(fitbox(bx + 15, by + 42, 170, 52, "Ємність вологості\nC(RH) ~ 10…25 пФ", size=11.5, fill="#d4efdf", stroke=FIELD, sw=1.2, bold=True))
    # Термометр PTAT / Bandgap
    parts.append(fitbox(bx + 15, by + 104, 170, 52, "Термометр PTAT\n(точний кристальний)", size=11.5, fill="#d4efdf", stroke=FIELD, sw=1.2, bold=True))
    # Вбудований нагрівач
    parts.append(fitbox(bx + 15, by + 166, 170, 62, "Вбудований нагрівач\n(Joule Heater)\nдля десорбції роси", size=11, fill="#fadbd8", stroke=POS, sw=1.2, bold=True))

    # Центральний блок: Аналоговий тракт CDC + ADC
    cx, cy, cw, ch = 315, 90, 200, 245
    parts.append(rect(cx, cy, cw, ch, fill="#ebf5fb", stroke=NEG, sw=1.8, rx=6))
    parts.append(text(cx + cw / 2, cy + 24, "Перетворювач сигналу", size=13, bold=True, color=NEG))

    parts.append(fitbox(cx + 15, cy + 42, 170, 52, "CDC: перемикані\nємності (ΔΣ Switched-Cap)", size=11, fill="#d4e6f1", stroke=NEG, sw=1.2, bold=True))
    parts.append(fitbox(cx + 15, cy + 104, 170, 52, "Прецизійний 16-біт\nАЦП температури", size=11, fill="#d4e6f1", stroke=NEG, sw=1.2, bold=True))
    parts.append(fitbox(cx + 15, cy + 166, 170, 62, "Драйвер нагрівача\n(ШІМ / таймер імпульсу)", size=11, fill="#fadbd8", stroke=POS, sw=1.2))

    # Стрілки сенсор -> CDC
    parts.append(arrow(bx + bw, by + 68, cx, cy + 68, color=INK, sw=1.8))
    parts.append(arrow(bx + bw, by + 130, cx, cy + 130, color=INK, sw=1.8))
    parts.append(arrow(cx, cy + 197, bx + bw, cy + 197, color=POS, sw=1.8))

    # Правий блок: Цифровий контролер + пам'ять + I2C
    dx, dy, dw, dh = 555, 90, 230, 245
    parts.append(rect(dx, dy, dw, dh, fill="#fef9e7", stroke="#d4ac0d", sw=1.8, rx=6))
    parts.append(text(dx + dw / 2, dy + 24, "Цифровий рушій & Інтерфейс", size=13, bold=True, color="#7d6608"))

    parts.append(fitbox(dx + 15, dy + 42, 200, 52, "OTP / EEPROM\nзаводські калібрувальні сталі", size=11, fill="#fcf3cf", stroke="#d4ac0d", sw=1.2))
    parts.append(fitbox(dx + 15, dy + 104, 200, 52, "DSP: лінеаризація +\nтемпературна компенсація", size=11, fill="#fcf3cf", stroke="#d4ac0d", sw=1.2, bold=True))
    parts.append(fitbox(dx + 15, dy + 166, 200, 62, "Контролер I²C / SPI\nз апаратним CRC-8", size=11.5, fill="#fcf3cf", stroke="#d4ac0d", sw=1.2, bold=True))

    # Стрілки аналог -> DSP
    parts.append(arrow(cx + cw, cy + 130, dx, dy + 130, color=INK, sw=2))

    # Виводи назовні (I2C)
    parts.append(arrow(dx + dw, dy + 185, dx + dw + 55, dy + 185, color=INK, sw=2.2))
    parts.append(text(dx + dw + 60, dy + 189, "SDA (Дані)", size=11.5, bold=True, color=INK, anchor="start"))
    parts.append(arrow(dx + dw + 55, dy + 210, dx + dw, dy + 210, color=INK, sw=2.2))
    parts.append(text(dx + dw + 60, dy + 214, "SCL (Тактування)", size=11.5, bold=True, color=INK, anchor="start"))

    # Підсумок унизу
    box, bw, bh = textbox(W / 2, H - 24,
                          "Інтегрований чип виконує температурну компенсацію ємності «на льоту» і віддає готові відкалібровані % RH та °C",
                          size=12, pad=10, fill=FILL)
    parts.append(box)

    render(os.path.join(IMG_DIR, "sensor-architecture.svg"), W, H, *parts,
           title="Внутрішня архітектура цифрового сенсора вологості")


if __name__ == "__main__":
    fig_cross_section()
    fig_dipole_polarization()
    fig_psychrometric_curve()
    fig_sensor_architecture()
    print("OK: cross-section, dipole-polarization, psychrometric-curve, sensor-architecture")
