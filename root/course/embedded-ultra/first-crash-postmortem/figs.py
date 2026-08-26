# -*- coding: utf-8 -*-
"""Фігури до теми «Розбір першого падіння» (first-crash-postmortem).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Часова шкала тріажу аварії (postmortem-timeline-triage) ───────────────
def fig_timeline_triage():
    W, H = 1100, 460
    f = [text(W / 2, 30, "Часова шкала тріажу аварії: розмотування подій від точки удару до тригера відмови",
              size=15, bold=True)]

    # Загальна вісь часу
    ox, oy, ow = 80, 240, 940
    f.append(line(ox, oy, ox + ow, oy, color=INK, sw=2.5))
    f.append(arrow(ox + ow - 10, oy, ox + ow + 20, oy, color=INK, sw=2.5))
    f.append(text(ox + ow + 20, oy + 26, "Час (TimeUS)", size=11, bold=True, anchor="end"))

    # Фази польоту
    # Фаза 1: Нормальний політ (t0 -> t_trig)
    t_trig_x = 420
    f.append(rect(ox, 80, t_trig_x - ox, 140, fill="#f2f8f2", stroke=FIELD, sw=1.5, rx=6))
    f.append(text((ox + t_trig_x) / 2, 105, "1. Стабільний керований політ", size=12, bold=True, color=FIELD))
    f.append(text((ox + t_trig_x) / 2, 130, "Помилка e(t) < 3°", size=10.5, color=INK))
    f.append(text((ox + t_trig_x) / 2, 150, "Мотори: 30–60% тяги", size=10, color=MUTED))
    f.append(text((ox + t_trig_x) / 2, 170, "Живлення: стабільне V_bat", size=10, color=MUTED))
    f.append(text((ox + t_trig_x) / 2, 195, "Базовий рівень (baseline)", size=10.5, bold=True, color=FIELD))

    # Фаза 2: Розвиток аномалії (t_trig -> t_sat)
    t_sat_x = 640
    f.append(rect(t_trig_x, 80, t_sat_x - t_trig_x, 140, fill="#fff7e6", stroke=POS, sw=1.5, rx=6))
    f.append(text((t_trig_x + t_sat_x) / 2, 105, "2. Тригер відмови (T_trigger)", size=12, bold=True, color=POS))
    f.append(text((t_trig_x + t_sat_x) / 2, 130, "Десинхрон / зрив гвинта / збій", size=10.5, bold=True, color=POS))
    f.append(text((t_trig_x + t_sat_x) / 2, 150, "Кутова похибка стрімко зростає", size=10, color=INK))
    f.append(text((t_trig_x + t_sat_x) / 2, 170, "P-терм і I-терм зашкалюють", size=10, color=MUTED))
    f.append(text((t_trig_x + t_sat_x) / 2, 195, "Тривалість: 10–50 мс", size=10, color=MUTED))

    # Фаза 3: Втрата керування та падіння (t_sat -> t_crash)
    t_crash_x = 880
    f.append(rect(t_sat_x, 80, t_crash_x - t_sat_x, 140, fill="#fdecea", stroke=POS, sw=2, rx=6))
    f.append(text((t_sat_x + t_crash_x) / 2, 105, "3. Сатурація та падіння", size=12, bold=True, color=POS))
    f.append(text((t_sat_x + t_crash_x) / 2, 130, "Мікшер: мотори на 100% / 0%", size=10.5, bold=True, color=POS))
    f.append(text((t_sat_x + t_crash_x) / 2, 150, "Некерований штопор (death roll)", size=10, color=INK))
    f.append(text((t_sat_x + t_crash_x) / 2, 170, "Гіроскоп: > 1000 °/с", size=10, color=MUTED))
    f.append(text((t_sat_x + t_crash_x) / 2, 195, "Апарат летить у землю", size=10, color=POS))

    # Фаза 4: Удар і Disarm (t_crash -> кінець)
    f.append(rect(t_crash_x, 80, ox + ow - t_crash_x, 140, fill="#1a1a1a", stroke=INK, sw=2, rx=6))
    f.append(text((t_crash_x + ox + ow) / 2, 105, "4. Удар (T_crash)", size=12, bold=True, color=BG))
    f.append(text((t_crash_x + ox + ow) / 2, 130, "G-удар акселерометра", size=10.5, color="#fca5a5"))
    f.append(text((t_crash_x + ox + ow) / 2, 150, "Піковий стрибок струму", size=10, color="#fca5a5"))
    f.append(text((t_crash_x + ox + ow) / 2, 170, "Аварійний Disarm / обрив", size=10, color=BG))
    f.append(text((t_crash_x + ox + ow) / 2, 195, "Зупинка логу", size=10, color="#9ca3af"))

    # Маркери подій на осі
    for (px, label, col) in [(t_trig_x, "T_trigger", POS), (t_sat_x, "T_saturation", POS), (t_crash_x, "T_crash", INK)]:
        f.append(circle(px, oy, 6, fill=col, stroke=BG, sw=2))
        f.append(line(px, oy - 20, px, oy + 40, color=col, sw=1.8, dash="3,3"))
        f.append(text(px, oy + 56, label, size=11, bold=True, color=col))

    # Стрілка напрямку розслідування (назад від T_crash)
    f.append(rect(180, 320, 740, 90, fill="#eef3fb", stroke=NEG, sw=1.8, rx=8))
    f.append(text(550, 345, "МЕТОДИКА РОЗСЛІДУВАННЯ: РУХ НАЗАД У ЧАСІ (ТВОРЧИЙ ТРІАЖ)", size=12.5, bold=True, color=NEG))
    f.append(arrow(850, 375, 220, 375, color=NEG, sw=2.5))
    f.append(text(550, 395, "Крок 1 (T_crash: фіксація удару) ──► Крок 2 (T_sat: перевірка мікшера) ──► Крок 3 (T_trigger: першопричина)",
                  size=11, bold=True, color=INK))

    return W, H, f


# ── 2. Відбиток десинхронізації мотора в лозі (motor-desync-signature) ───────
def fig_motor_desync():
    W, H = 1100, 560
    f = [text(W / 2, 28, "Сигнатура десинхронізації мотора: 100% тяги при зворотній кутовій швидкості",
              size=15, bold=True)]

    ox = 110
    aw = 920
    ah = 95

    # Три графіки:
    # 1. Задана кутова швидкість (Setpoint) проти фактичної (Gyro Rate)
    # 2. ПІД-складові (P, I, D) та I-term Windup
    # 3. Виходи моторів (Motor 1..4)
    oy1, oy2, oy3 = 135, 275, 435

    # ── Графік 1: Кути та кутова швидкість
    f.append(arrow(ox, oy1, ox + aw, oy1))
    f.append(arrow(ox, oy1, ox, oy1 - ah))
    f.append(text(ox - 14, oy1 - ah + 15, "Roll Rate (°/с)", size=11, bold=True, anchor="end"))
    f.append(line(ox, oy1 - ah / 2, ox + aw - 30, oy1 - ah / 2, color="#e5e7eb", sw=1, dash="4,4"))
    f.append(text(ox - 10, oy1 - ah / 2 + 4, "0 °/с", size=10, color=MUTED, anchor="end"))

    # Часова мітка тригера
    t_ev = ox + 360
    f.append(line(t_ev, 50, t_ev, 500, color=POS, sw=1.8, dash="4,3"))
    f.append(text(t_ev, 46, "Зрив синхронізації мотора M4 (T_desync)", size=11, bold=True, color=POS))

    # Криві графіку 1
    # Setpoint (синій)
    pts_sp = [(ox, oy1 - ah / 2)]
    for px in range(0, 360):
        pts_sp.append((ox + px, oy1 - ah / 2))
    for px in range(360, 500):
        pts_sp.append((ox + px, oy1 - ah / 2 - 25))
    for px in range(500, 860):
        pts_sp.append((ox + px, oy1 - ah / 2))
    p_sp = "M %.1f %.1f " % pts_sp[0] + " ".join("L %.1f %.1f" % p for p in pts_sp[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5,3"/>' % (p_sp, NEG))
    f.append(text(ox + 160, oy1 - ah / 2 - 12, "Задане (Setpoint Roll)", size=10.5, bold=True, color=NEG))

    # Gyro Rate (червоний) - після t_ev зривається в протилежний бік!
    pts_gy = [(ox, oy1 - ah / 2)]
    for px in range(0, 360):
        noise = math.sin(px * 0.2) * 2.0
        pts_gy.append((ox + px, oy1 - ah / 2 + noise))
    for px in range(360, 860):
        t = (px - 360) / 120.0
        val = (oy1 - ah / 2) + min(ah * 0.45, t * 45.0 + math.sin(px * 0.3) * 6.0)
        pts_gy.append((ox + px, val))
    p_gy = "M %.1f %.1f " % pts_gy[0] + " ".join("L %.1f %.1f" % p for p in pts_gy[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p_gy, POS))
    f.append(text(ox + 560, oy1 + 32, "Фактичний гіроскоп (Gyro Roll) падає у штопор!", size=11, bold=True, color=POS))

    # ── Графік 2: ПІД-регулятор
    f.append(arrow(ox, oy2, ox + aw, oy2))
    f.append(arrow(ox, oy2, ox, oy2 - ah))
    f.append(text(ox - 14, oy2 - ah + 15, "PID Sum / I-term", size=11, bold=True, anchor="end"))
    f.append(line(ox, oy2 - ah / 2, ox + aw - 30, oy2 - ah / 2, color="#e5e7eb", sw=1, dash="4,4"))

    # I-term накопичення (віндап)
    pts_it = [(ox, oy2 - ah / 2)]
    for px in range(0, 360):
        pts_it.append((ox + px, oy2 - ah / 2))
    for px in range(360, 860):
        t = (px - 360) / 150.0
        val = (oy2 - ah / 2) - min(ah * 0.44, t * 38.0)
        pts_it.append((ox + px, val))
    p_it = "M %.1f %.1f " % pts_it[0] + " ".join("L %.1f %.1f" % p for p in pts_it[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p_it, "#8e44ad"))
    f.append(text(ox + 500, oy2 - ah / 2 - 34, "I-term Windup: інтегратор роздувається до 100% ліміту", size=10.5, bold=True, color="#8e44ad"))

    # ── Графік 3: Виходи моторів
    f.append(arrow(ox, oy3, ox + aw, oy3))
    f.append(arrow(ox, oy3, ox, oy3 - ah))
    f.append(text(ox - 14, oy3 - ah + 15, "Тяга моторів (%)", size=11, bold=True, anchor="end"))
    f.append(text(ox + aw, oy3 + 24, "Час t (мс)", size=11, bold=True, anchor="end"))

    # 100% лінія стелі
    f.append(line(ox, oy3 - ah + 10, ox + aw - 30, oy3 - ah + 10, color=POS, sw=1.2, dash="3,3"))
    f.append(text(ox - 10, oy3 - ah + 14, "100% (max)", size=10, bold=True, color=POS, anchor="end"))
    f.append(text(ox - 10, oy3 - 4, "0% (min)", size=10, color=MUTED, anchor="end"))

    # Мотор 4 (зависає на 100%)
    pts_m4 = [(ox, oy3 - 45)]
    for px in range(0, 360):
        pts_m4.append((ox + px, oy3 - 45 + math.sin(px * 0.1) * 5))
    for px in range(360, 390):
        t = (px - 360) / 30.0
        val = (oy3 - 45) - t * (ah - 55)
        pts_m4.append((ox + px, val))
    for px in range(390, 860):
        pts_m4.append((ox + px, oy3 - ah + 10))
    p_m4 = "M %.1f %.1f " % pts_m4[0] + " ".join("L %.1f %.1f" % p for p in pts_m4[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (p_m4, POS))

    # Мотор 1, 2, 3 (падають до 0% для балансування)
    pts_moth = [(ox, oy3 - 45)]
    for px in range(0, 360):
        pts_moth.append((ox + px, oy3 - 45 - math.sin(px * 0.1) * 5))
    for px in range(360, 390):
        t = (px - 360) / 30.0
        val = (oy3 - 45) + t * 40
        pts_moth.append((ox + px, val))
    for px in range(390, 860):
        pts_moth.append((ox + px, oy3 - 5))
    p_moth = "M %.1f %.1f " % pts_moth[0] + " ".join("L %.1f %.1f" % p for p in pts_moth[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,3"/>' % (p_moth, MUTED))

    # Пояснювальний блок
    f.append(rect(ox + 420, oy3 - 80, 480, 60, fill="#fdecea", stroke=POS, sw=1.6, rx=6))
    f.append(text(ox + 660, oy3 - 60, "КЛЮЧОВА ОЗНАКА DESYNC: Мотор M4 вимагає 100% тяги,", size=11, bold=True, color=POS))
    f.append(text(ox + 660, oy3 - 38, "але апарат обертається у протилежний бік без кутового прискорення!", size=10.5, color=POS))

    f.append(text(W / 2, H - 12,
                  "Повна сатурація мікшера: коли один мотор зависає на 100%, а інші на 0%, зв'язок регулювання розірвано",
                  size=11.5, color=MUTED))
    return W, H, f


# ── 3. Просідання батареї та Brownout Reset (battery-sag-and-brownout) ──────
def fig_battery_sag():
    W, H = 1080, 500
    f = [text(W / 2, 28, "Просідання напруги батареї: безпечний робочий спад проти фатального Brownout Reset",
              size=15, bold=True)]

    ox = 110
    aw = 880
    ah = 150

    oy1 = 200
    oy2 = 420

    # Верхній графік: Струм I_bat (А)
    f.append(arrow(ox, oy1, ox + aw, oy1))
    f.append(arrow(ox, oy1, ox, oy1 - ah))
    f.append(text(ox - 14, oy1 - ah + 15, "Струм I_bat (А)", size=11, bold=True, anchor="end"))
    f.append(text(ox - 10, oy1 - 10, "0 А", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy1 - 120, "120 А (пік)", size=10.5, bold=True, color=POS, anchor="end"))

    # Сплеск струму при різкому газі (punchout)
    pts_i = [(ox, oy1 - 15)]
    for px in range(0, 200):
        pts_i.append((ox + px, oy1 - 15))
    for px in range(200, 240):
        t = (px - 200) / 40.0
        val = 15 + t * 105
        pts_i.append((ox + px, oy1 - val))
    for px in range(240, 500):
        pts_i.append((ox + px, oy1 - 120))
    for px in range(500, 800):
        pts_i.append((ox + px, oy1 - 15))
    p_i = "M %.1f %.1f " % pts_i[0] + " ".join("L %.1f %.1f" % p for p in pts_i[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p_i, POS))
    f.append(text(ox + 350, oy1 - 132, "Різкий маневр / повний газ (Punch-out)", size=11, bold=True, color=POS))

    # Нижній графік: Напруга батареї V_bat (В)
    f.append(arrow(ox, oy2, ox + aw, oy2))
    f.append(arrow(ox, oy2, ox, oy2 - ah))
    f.append(text(ox - 14, oy2 - ah + 15, "Напруга батареї (В)", size=11, bold=True, anchor="end"))
    f.append(text(ox + aw, oy2 + 24, "Час t (мс)", size=11, bold=True, anchor="end"))

    # Номінал 6S (25.2 В / 22.2 В)
    y_nom = oy2 - 130
    f.append(line(ox, y_nom, ox + aw - 30, y_nom, color=FIELD, sw=1.2, dash="4,4"))
    f.append(text(ox - 10, y_nom + 4, "22.2 В (6S номінал)", size=10, bold=True, color=FIELD, anchor="end"))

    # Поріг відсічки BEC 5V (еквівалент напруги батареї ~6.5 В або провал регулятора)
    y_bod = oy2 - 25
    f.append(line(ox, y_bod, ox + aw - 30, y_bod, color=POS, sw=1.8, dash="5,3"))
    f.append(text(ox - 10, y_bod + 4, "Поріг BOD MCU (2.7 В / 5 В BEC)", size=10, bold=True, color=POS, anchor="end"))

    # Крива 1: Здорова батарея (нормальний ESR ~15 мОм) -> просідання до 20 В
    pts_u_ok = [(ox, y_nom)]
    for px in range(0, 200):
        pts_u_ok.append((ox + px, y_nom))
    for px in range(200, 240):
        t = (px - 200) / 40.0
        val = y_nom + t * 30
        pts_u_ok.append((ox + px, val))
    for px in range(240, 500):
        pts_u_ok.append((ox + px, y_nom + 30))
    for px in range(500, 540):
        t = (px - 500) / 40.0
        val = (y_nom + 30) - t * 30
        pts_u_ok.append((ox + px, val))
    for px in range(540, 800):
        pts_u_ok.append((ox + px, y_nom))
    p_u_ok = "M %.1f %.1f " % pts_u_ok[0] + " ".join("L %.1f %.1f" % p for p in pts_u_ok[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (p_u_ok, FIELD))
    f.append(text(ox + 580, y_nom + 18, "Здорова батарея: ΔV = I · ESR (~2.0 В просідання)", size=10.5, color=FIELD))

    # Крива 2: Деградована банка / високий опір (ESR ~120 мОм) -> колапс у Brownout!
    pts_u_bad = [(ox, y_nom)]
    for px in range(0, 200):
        pts_u_bad.append((ox + px, y_nom))
    for px in range(200, 260):
        t = (px - 200) / 60.0
        val = y_nom + t * (y_bod - y_nom + 15)
        pts_u_bad.append((ox + px, val))
    # Обрив логу в точці BOD!
    p_u_bad = "M %.1f %.1f " % pts_u_bad[0] + " ".join("L %.1f %.1f" % p for p in pts_u_bad[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (p_u_bad, POS))

    # Точка обриву
    bod_x = ox + 260
    f.append(circle(bod_x, y_bod + 15, 6, fill=POS, stroke=BG, sw=2))
    f.append(rect(bod_x + 15, y_bod - 60, 380, 65, fill="#fdecea", stroke=POS, sw=1.6, rx=6))
    f.append(text(bod_x + 205, y_bod - 40, "ФАТАЛЬНИЙ BROWNOUT RESET (BOD):", size=11, bold=True, color=POS))
    f.append(text(bod_x + 205, y_bod - 20, "МК перезавантажується mid-air, лог обривається без Disarm", size=10, color=POS))

    return W, H, f


# ── 4. FFT-спектрограма вібрацій (gyro-fft-spectrogram-harmonics) ─────────────
def fig_gyro_fft():
    W, H = 1080, 500
    f = [text(W / 2, 28, "FFT-спектрограма вібрацій: моторні гармоніки, структурний резонанс та дія режекторних фільтрів",
              size=15, bold=True)]

    ox = 100
    aw = 880
    ah = 340
    oy = 420

    f.append(arrow(ox, oy, ox + aw, oy))
    f.append(arrow(ox, oy, ox, oy - ah))
    f.append(text(ox + aw, oy + 24, "Частота f (Гц)", size=11.5, bold=True, anchor="end"))
    f.append(text(ox - 14, oy - ah + 15, "Амплітуда шуму гіроскопа (дБ)", size=11.5, bold=True, anchor="end"))

    # Позначки частот (0, 100, 200, 300, 400, 500, 600, 800 Гц)
    freqs = [
        (100, "100"),
        (200, "200"),
        (300, "300"),
        (450, "450 (f_motor)"),
        (600, "600"),
        (750, "750 (Резонанс)")
    ]
    for (fq, lbl) in freqs:
        fx = ox + fq * (aw - 60) / 800.0
        f.append(line(fx, oy, fx, oy - 6, color=INK, sw=1.5))
        f.append(text(fx, oy + 18, lbl, size=10, color=MUTED))

    # Спектральний фон шуму (сирий сигнал до фільтрів - червоний штрих)
    pts_raw = [(ox, oy - 30)]
    for px in range(0, int(aw - 60)):
        fq = px * 800.0 / (aw - 60)
        # базовий шум
        amp = 25.0 + math.sin(fq * 0.05) * 4.0
        # Пік 1: Моторна гармоніка f_motor ~ 220 Гц
        amp += 90.0 * math.exp(-((fq - 220) ** 2) / (2 * 18 ** 2))
        # Пік 2: Лопатева гармоніка (3 лопаті) ~ 450 Гц
        amp += 140.0 * math.exp(-((fq - 450) ** 2) / (2 * 22 ** 2))
        # Пік 3: Структурний резонанс рами (незалежний від газу!) ~ 720 Гц
        amp += 180.0 * math.exp(-((fq - 720) ** 2) / (2 * 15 ** 2))
        pts_raw.append((ox + px, oy - amp))
    p_raw = "M %.1f %.1f " % pts_raw[0] + " ".join("L %.1f %.1f" % p for p in pts_raw[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>' % (p_raw, POS))
    f.append(text(ox + 680, oy - 270, "Сирий шум гіроскопа (Raw Gyro)", size=11, bold=True, color=POS))

    # Спектральний фон після динамічного режекторного фільтра (Dynamic Notch + Lowpass - зелений)
    pts_flt = [(ox, oy - 28)]
    for px in range(0, int(aw - 60)):
        fq = px * 800.0 / (aw - 60)
        amp = 20.0 * math.exp(-fq / 150.0) + 4.0
        # Подавлені моторні піки
        amp += 15.0 * math.exp(-((fq - 220) ** 2) / (2 * 18 ** 2))
        amp += 18.0 * math.exp(-((fq - 450) ** 2) / (2 * 22 ** 2))
        # Незафільтрований резонанс пробиває фільтр!
        amp += 120.0 * math.exp(-((fq - 720) ** 2) / (2 * 15 ** 2))
        pts_flt.append((ox + px, oy - amp))
    p_flt = "M %.1f %.1f " % pts_flt[0] + " ".join("L %.1f %.1f" % p for p in pts_flt[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p_flt, FIELD))
    f.append(text(ox + 260, oy - 70, "Відфільтрований сигнал (Filtered Gyro)", size=11, bold=True, color=FIELD))

    # Рамка аналізу небезпечного резонансу
    res_x = ox + 720 * (aw - 60) / 800.0
    f.append(rect(res_x - 170, 70, 320, 95, fill="#fdecea", stroke=POS, sw=1.6, rx=6))
    f.append(text(res_x - 10, 92, "СТРУКТУРНИЙ РЕЗОНАНС РАМИ:", size=11.5, bold=True, color=POS))
    f.append(text(res_x - 10, 112, "Вузький пік ~720 Гц не рухається з газом", size=10.5, color=INK))
    f.append(text(res_x - 10, 130, "→ D-терм підсилює шум: d(noise)/dt = ω·Noise", size=10, bold=True, color=POS))
    f.append(text(res_x - 10, 148, "→ Мотори гріються й входять у flyaway!", size=10, color=POS))

    return W, H, f


# ── 5. Дерево рішень посмертного розбору (crash-decision-tree) ───────────────
def fig_decision_tree():
    W, H = 1100, 520
    f = [text(W / 2, 28, "Дерево рішень постмортему: покрокова локалізація причини аварії за Blackbox",
              size=15, bold=True)]

    # Корінь: Аналіз початку та кінця логу
    rx, ry = 550, 75
    b_root, rw, rh = textbox(rx, ry, "1. Чи завершився лог коректно?\n(Перевірка прапорця Disarm та напруги)",
                             size=11.5, pad=10, fill="#eef3fb", stroke=INK, bold=True)
    f.append(b_root)

    # Гілка НІ (ліворуч) -> Brownout
    bx_l, by_l = 220, 190
    f.append(arrow(rx - rw / 3, ry + rh / 2, bx_l, by_l - 30, color=POS, sw=2))
    f.append(text((rx - rw / 3 + bx_l) / 2 - 10, (ry + rh / 2 + by_l - 30) / 2, "НІ (обрив)", size=10.5, bold=True, color=POS))
    b_l, _, _ = textbox(bx_l, by_l, "ЖИВЛЕННЯ: BROWNOUT RESET\nЛог обірвано mid-air без Disarm.\nПричина: просідання Vbat, дефект BEC\nабо коротке замикання силової шини.",
                        size=10.5, pad=10, fill="#fdecea", stroke=POS, bold=False)
    f.append(b_l)

    # Гілка ТАК (праворуч) -> Крок 2
    bx_r, by_r = 750, 190
    f.append(arrow(rx + rw / 3, ry + rh / 2, bx_r, by_r - 30, color=FIELD, sw=2))
    f.append(text((rx + rw / 3 + bx_r) / 2 + 10, (ry + rh / 2 + by_r - 30) / 2, "ТАК (є Disarm)", size=10.5, bold=True, color=FIELD))
    b_r, r2_w, r2_h = textbox(bx_r, by_r, "2. Чи є розбіжність між бажаним і кутом?\n(Помилка стеження e(t) > 30° триває > 50 мс)",
                              size=11, pad=10, fill="#fdfbf7", stroke=FIELD, bold=True)
    f.append(b_r)

    # Від кроку 2:
    # Гілка НІ (помилки кута не було до зіткнення) -> Пілот / Failsafe / Перешкода
    p_x, p_y = 950, 320
    f.append(arrow(bx_r + r2_w / 3, by_r + r2_h / 2, p_x, p_y - 30, color=MUTED, sw=1.8))
    f.append(text(p_x - 40, by_r + 35, "НІ (e ≈ 0)", size=10, bold=True, color=MUTED))
    b_p, _, _ = textbox(p_x, p_y, "ПЕРЕШКОДА / ПІЛОТ / FAILSAFE\nАпарат ідеально виконував команди\nдо фізичного контакту із землею.\nПеревірити: радіолінк та Failsafe.",
                        size=10, pad=8, fill="#f4f6f8", stroke=MUTED, bold=False)
    f.append(b_p)

    # Гілка ТАК (була велика розбіжність) -> Крок 3 (Перевірка моторів)
    k3_x, k3_y = 550, 320
    f.append(arrow(bx_r - r2_w / 4, by_r + r2_h / 2, k3_x, k3_y - 30, color=POS, sw=2))
    f.append(text((bx_r - r2_w / 4 + k3_x) / 2 + 15, by_r + 35, "ТАК (зрив)", size=10, bold=True, color=POS))
    b_k3, k3_w, k3_h = textbox(k3_x, k3_y, "3. Чи завис один із моторів на 100%?\n(Сатурація мікшера: M_x = 100%, M_opp = 0%)",
                               size=11, pad=10, fill="#fdfbf7", stroke=POS, bold=True)
    f.append(b_k3)

    # Від кроку 3:
    # Гілка А: 100% тяги без реакції кута -> ДЕСИНХРОН / ЗРИВ ГВИНТА
    d_x, d_y = 380, 445
    f.append(arrow(k3_x - k3_w / 4, k3_y + k3_h / 2, d_x, d_y - 30, color=POS, sw=2))
    f.append(text(d_x + 30, k3_y + 35, "ТАК (1 мотор 100%)", size=9.5, bold=True, color=POS))
    b_d, _, _ = textbox(d_x, d_y, "ДЕСИНХРОН ESC / ВТРАТА ГВИНТА\nМотор на 100%, але кутове прискорення нульове.\nРозрізнення: струм зріс → десинхрон;\nструм впав → відкрутився пропелер.",
                        size=9.5, pad=8, fill="#fdecea", stroke=POS, bold=False)
    f.append(b_d)

    # Гілка Б: Усі мотори коливаються / розгін вібрацій -> ПІД / ФІЛЬТРИ / РЕЗОНАНС
    o_x, o_y = 720, 445
    f.append(arrow(k3_x + k3_w / 4, k3_y + k3_h / 2, o_x, o_y - 30, color="#8e44ad", sw=2))
    f.append(text(o_x - 30, k3_y + 35, "НІ (дикий дзвін усіх)", size=9.5, bold=True, color="#8e44ad"))
    b_o, _, _ = textbox(o_x, o_y, "РЕЗОНАНС РАМИ / ПЕРЕРЕГУЛЮВАННЯ D\nМотори синхронно пиляють на високій частоті.\nПричина: розхитаний промінь, шум гіроскопа,\nзавеликий D-терм або пізні фільтри.",
                        size=9.5, pad=8, fill="#fff2e6", stroke="#8e44ad", bold=False)
    f.append(b_o)

    return W, H, f


for name, fn in [("postmortem-timeline-triage", fig_timeline_triage),
                 ("motor-desync-signature", fig_motor_desync),
                 ("battery-sag-and-brownout", fig_battery_sag),
                 ("gyro-fft-spectrogram-harmonics", fig_gyro_fft),
                 ("crash-decision-tree", fig_decision_tree)]:
    W, H, frags = fn()
    render(os.path.join(IMG, name + ".svg"), W, H, *frags)
    print("wrote", name + ".svg")
