# -*- coding: utf-8 -*-
"""Фігури до теми «Мінімальна обв'язка МК: живлення, скидання, boot-піни, кварц».
Запуск: python figs.py  → генерує SVG у ./img/
Стиль і компоненти — зі спільного svgkit."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Шини живлення, розв'язка та фільтрація аналогового домену ────────────
def fig_power_decoupling():
    W, H = 940, 540
    f = []

    # Загальна рамка плати / шини живлення
    f.append(rect(20, 20, W - 40, H - 40, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, 45, "Архітектура живлення МК: декаплінг, фільтрація VDDA та VCAP", size=15, bold=True, color=INK))

    # Джерело живлення 3.3V (LDO або DC-DC)
    b_ldo, lw, lh = textbox(110, 150, "Джерело 3.3 В\n(LDO / DC-DC)", size=11, bold=True, fill="#eef2f6", stroke=INK, pad=8)
    f.append(b_ldo)

    # Головна шина VDD 3.3V
    f.append(line(170, 150, 720, 150, color=POS, sw=2.5))
    f.append(text(340, 138, "Шина VDD (+3.3 В)", size=11, bold=True, color=POS, anchor="start"))

    # Головна земля GND / VSS
    f.append(line(170, 470, 720, 470, color=NEG, sw=2.5))
    f.append(text(340, 492, "Суцільний полігон GND / VSS (0 В)", size=11, bold=True, color=NEG, anchor="start"))

    # 1. Резервуарний конденсатор (Bulk Capacitor) 10 мкФ
    f.append(line(230, 150, 230, 260, color=POS, sw=1.8))
    b_bulk, _, _ = textbox(230, 290, "C_bulk\n10 мкФ\n(тантал / X7R)", size=10, bold=True, fill="#fff7ed", stroke="#ea580c", pad=6)
    f.append(b_bulk)
    f.append(line(230, 320, 230, 470, color=NEG, sw=1.8))
    f.append(text(230, 360, "гасить просадки", size=10, color=MUTED, anchor="middle"))

    # 2. Локальні блокувальні конденсатори VDD/VSS (100 нФ на кожен пін)
    f.append(line(360, 150, 360, 260, color=POS, sw=1.8))
    b_c1, _, _ = textbox(360, 290, "C_dec 1\n100 нФ\n0402 MLCC", size=10, bold=True, fill="#eff6ff", stroke=NEG, pad=6)
    f.append(b_c1)
    f.append(line(360, 320, 360, 470, color=NEG, sw=1.8))

    f.append(line(480, 150, 480, 260, color=POS, sw=1.8))
    b_c2, _, _ = textbox(480, 290, "C_dec 2\n100 нФ\n0402 MLCC", size=10, bold=True, fill="#eff6ff", stroke=NEG, pad=6)
    f.append(b_c2)
    f.append(line(480, 320, 480, 470, color=NEG, sw=1.8))

    f.append(text(420, 420, "впритул до пар VDD/VSS (<2 мм), короткі vias на GND", size=10, color=FIELD, anchor="middle", bold=True))

    # 3. Аналоговий домен VDDA / VSSA (LC фільтрація через Ferrite Bead)
    f.append(line(580, 150, 580, 185, color=POS, sw=1.8))
    b_fb, _, _ = textbox(580, 215, "Ferrite Bead\n120 Ω @ 100 МГц\nR_dc < 0.1 Ω", size=10, bold=True, fill="#fef08a", stroke="#ca8a04", pad=6)
    f.append(b_fb)
    f.append(line(580, 245, 580, 270, color=POS, sw=1.8))

    # VDDA шина після бусини
    f.append(line(580, 270, 720, 270, color="#d97706", sw=2.0))
    f.append(text(600, 260, "Шина VDDA (чистий аналог)", size=10, bold=True, color="#d97706", anchor="start"))

    # Конденсатори VDDA: 1 мкФ + 10 нФ
    f.append(line(630, 270, 630, 315, color="#d97706", sw=1.5))
    b_cva1, _, _ = textbox(630, 345, "1 мкФ\n+ 10 нФ", size=10, bold=True, fill="#fef3c7", stroke="#d97706", pad=6)
    f.append(b_cva1)
    f.append(line(630, 375, 630, 470, color=NEG, sw=1.5))
    f.append(text(630, 400, "VSSA аналог", size=10, color=MUTED, anchor="middle"))

    # Центральний чип МК (праворуч)
    ch_x, ch_y, ch_w, ch_h = 750, 110, 155, 380
    f.append(rect(ch_x, ch_y, ch_w, ch_h, fill="#1e293b", stroke=INK, sw=2, rx=8))
    f.append(text(ch_x + ch_w / 2, ch_y + 30, "Мікроконтролер", size=13, bold=True, color="#ffffff"))
    f.append(text(ch_x + ch_w / 2, ch_y + 50, "(ARM Cortex-M)", size=10.5, color="#94a3b8"))

    # Піни чіпа
    f.append(line(720, 150, ch_x, 150, color=POS, sw=2))
    f.append(text(ch_x + 8, 154, "VDD_1", size=10, color="#fca5a5", anchor="start", bold=True))
    f.append(line(480, 200, ch_x, 200, color=POS, sw=1.8))
    f.append(text(ch_x + 8, 204, "VDD_2", size=10, color="#fca5a5", anchor="start", bold=True))

    f.append(line(720, 270, ch_x, 270, color="#d97706", sw=2))
    f.append(text(ch_x + 8, 274, "VDDA (ADC)", size=10, color="#fde047", anchor="start", bold=True))

    # VCAP (внутрішній регулятор ядра 1.2В)
    f.append(line(ch_x, 340, 715, 340, color="#0284c7", sw=1.8))
    b_vcap, _, _ = textbox(675, 340, "VCAP\n2.2 мкФ\nESR<1Ω", size=9.5, bold=True, fill="#e0f2fe", stroke="#0284c7", pad=5)
    f.append(b_vcap)
    f.append(line(635, 340, 635, 470, color=NEG, sw=1.5))
    f.append(text(ch_x + 8, 344, "VCAP (1.2V LDO)", size=10, color="#7dd3fc", anchor="start", bold=True))

    f.append(line(ch_x, 430, 720, 430, color=NEG, sw=2))
    f.append(text(ch_x + 8, 434, "VSS / VSSA", size=10, color="#93c5fd", anchor="start", bold=True))

    return render(os.path.join(IMG_DIR, "power-and-decoupling.svg"), W, H, *f)


# ── 2. Ланцюг апаратного скидання (NRST) та конфігурація завантаження (BOOT) ───
def fig_reset_boot():
    W, H = 940, 540
    f = []

    f.append(rect(20, 20, W - 40, H - 40, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, 45, "Схеми апаратного скидання (NRST) та вибору режиму старту (BOOT)", size=15, bold=True, color=INK))

    f.append(line(W / 2 - 10, 70, W / 2 - 10, H - 35, color="#cbd5e1", sw=1.5, dash="6,5"))

    # ── Ліва частина: Вузол NRST ──
    f.append(text(230, 80, "Ланцюг скидання NRST (Active-Low)", size=13, bold=True, color=INK))

    f.append(line(80, 110, 390, 110, color=POS, sw=2))
    f.append(text(80, 105, "+3.3 В (VDD)", size=10.5, bold=True, color=POS, anchor="start"))

    f.append(rect(290, 140, 140, 340, fill="#1e293b", stroke=INK, sw=1.8, rx=6))
    f.append(text(360, 165, "МК", size=13, bold=True, color="#ffffff"))
    f.append(text(360, 185, "(Cortex-M)", size=10, color="#94a3b8"))

    # Внутрішній pull-up резистор 40 кОм всередині МК
    f.append(rect(310, 220, 100, 50, fill="#334155", stroke="#64748b", sw=1.2, rx=4))
    f.append(text(360, 240, "R_PU внутр.", size=10, color="#f1f5f9", bold=True))
    f.append(text(360, 256, "≈ 40 кОм", size=9.5, color="#94a3b8"))
    f.append(line(360, 200, 360, 220, color="#fca5a5", sw=1.5))
    f.append(line(360, 200, 390, 200, color=POS, sw=1.8))
    f.append(line(390, 110, 390, 200, color=POS, sw=1.8))

    # Вивід NRST
    f.append(line(360, 270, 360, 310, color=INK, sw=2))
    f.append(line(290, 310, 360, 310, color=INK, sw=2))
    f.append(text(300, 304, "NRST", size=10.5, bold=True, color="#fca5a5", anchor="start"))

    # Внутрішній тригер Шмітта
    b_rst_in, _, _ = textbox(360, 375, "Внутрішній\nPower-on Reset\n/ Тригер Шмітта", size=9.5, fill="#0f172a", stroke="#475569", color="#38bdf8", pad=6)
    f.append(b_rst_in)
    f.append(arrow(360, 310, 360, 345, color="#38bdf8", sw=1.5))

    # Зовнішня лінія NRST
    f.append(line(130, 310, 290, 310, color=INK, sw=2))

    # Зовнішній конденсатор 100 нФ на землю
    f.append(line(220, 310, 220, 355, color=INK, sw=1.6))
    b_cnrst, _, _ = textbox(220, 385, "C_NRST\n100 нФ\n(фільтр)", size=10, bold=True, fill="#eff6ff", stroke=NEG, pad=6)
    f.append(b_cnrst)
    f.append(line(220, 415, 220, 460, color=NEG, sw=1.6))
    f.append(text(220, 475, "GND", size=10, bold=True, color=NEG))

    # Тактова кнопка скидання
    f.append(line(130, 310, 130, 355, color=INK, sw=1.6))
    b_btn, _, _ = textbox(130, 385, "Кнопка\nСкидання\n(Manual)", size=9.5, bold=True, fill="#fef2f2", stroke=POS, pad=6)
    f.append(b_btn)
    f.append(line(130, 415, 130, 460, color=NEG, sw=1.6))
    f.append(text(130, 475, "GND", size=10, bold=True, color=NEG))

    f.append(text(175, 230, "τ = R_PU · C_NRST ≈ 4 мс\n(затримка при старті)", size=10, color=FIELD, bold=True, anchor="middle"))

    f.append(line(130, 310, 50, 310, color="#7c3aed", sw=1.8, dash="4,3"))
    f.append(text(48, 305, "До SWD NRST (Open-Drain)", size=9.5, bold=True, color="#7c3aed", anchor="start"))


    # ── Права частина: Strapping піни BOOT0 / BOOT1 ──
    f.append(text(680, 80, "Конфігурація завантаження (Boot Mode)", size=13, bold=True, color=INK))

    f.append(rect(730, 140, 140, 340, fill="#1e293b", stroke=INK, sw=1.8, rx=6))
    f.append(text(800, 165, "МК", size=13, bold=True, color="#ffffff"))
    f.append(text(800, 185, "(Boot Logic)", size=10, color="#94a3b8"))

    # Пін BOOT0
    f.append(line(550, 200, 730, 200, color=INK, sw=2))
    f.append(text(740, 195, "BOOT0", size=10.5, bold=True, color="#fde047", anchor="start"))

    f.append(line(630, 200, 630, 235, color=INK, sw=1.6))
    b_rboot0, _, _ = textbox(630, 260, "R_PD\n10 кОм", size=9.5, bold=True, fill="#f8fafc", stroke=LINE, pad=5)
    f.append(b_rboot0)
    f.append(line(630, 285, 630, 310, color=NEG, sw=1.6))
    f.append(text(630, 325, "GND (Штатний старт з Flash)", size=9.5, bold=True, color=FIELD))

    b_jmp, _, _ = textbox(510, 200, "Джампер BOOT0\n[ 1-2: 3.3V ]\n[ 2-3: GND ]", size=9.5, bold=True, fill="#fef3c7", stroke="#d97706", pad=5)
    f.append(b_jmp)

    # Пін BOOT1 / PB2
    f.append(line(550, 370, 730, 370, color=INK, sw=2))
    f.append(text(740, 365, "BOOT1 (PB2)", size=10.5, bold=True, color="#fde047", anchor="start"))

    f.append(line(630, 370, 630, 400, color=INK, sw=1.6))
    b_rboot1, _, _ = textbox(630, 425, "R_PD\n10 кОм", size=9.5, bold=True, fill="#f8fafc", stroke=LINE, pad=5)
    f.append(b_rboot1)
    f.append(line(630, 450, 630, 475, color=NEG, sw=1.6))
    f.append(text(630, 490, "GND", size=10, bold=True, color=NEG))

    # Таблиця вибору режимів
    tbl_x, tbl_y = 470, 105
    f.append(rect(tbl_x, tbl_y, 250, 65, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    f.append(text(tbl_x + 125, tbl_y + 16, "Таблиця режимів завантаження:", size=10, bold=True, color=INK))
    f.append(text(tbl_x + 10, tbl_y + 34, "BOOT0=0       → Головна Flash (0x08000000)", size=9.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(tbl_x + 10, tbl_y + 48, "BOOT0=1, B1=0 → System ROM Bootloader (UART/USB)", size=9.5, color="#d97706", anchor="start"))
    f.append(text(tbl_x + 10, tbl_y + 60, "BOOT0=1, B1=1 → Вбудована SRAM (0x20000000)", size=9.5, color=MUTED, anchor="start"))

    return render(os.path.join(IMG_DIR, "reset-and-boot-circuit.svg"), W, H, *f)


# ── 3. Тактові генератори (HSE, LSE) та трасування резонаторів ────────────────
def fig_crystal_oscillators():
    W, H = 940, 540
    f = []

    f.append(rect(20, 20, W - 40, H - 40, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, 45, "Тактування МК: підключення резонаторів HSE/LSE та захисне кільце", size=15, bold=True, color=INK))

    # Ліва частина: Схема генератора П'єрса (HSE 8–25 МГц)
    f.append(text(230, 80, "Схема генератора HSE (8–25 МГц)", size=13, bold=True, color=INK))

    f.append(rect(40, 110, 160, 380, fill="#1e293b", stroke=INK, sw=1.8, rx=6))
    f.append(text(120, 135, "МК (STM32)", size=13, bold=True, color="#ffffff"))

    # Внутрішній інвертор
    f.append(rect(65, 200, 110, 120, fill="#0f172a", stroke="#38bdf8", sw=1.5, rx=4))
    f.append(text(120, 220, "Інвертуючий\nпідсилювач", size=10, bold=True, color="#38bdf8"))
    f.append(text(120, 260, "R_F feedback\n≈ 1 МОм", size=9.5, color="#94a3b8"))

    # Піни OSC_IN та OSC_OUT
    f.append(line(175, 230, 255, 230, color=INK, sw=2))
    f.append(text(170, 225, "OSC_IN", size=10, color="#fca5a5", anchor="end", bold=True))

    f.append(line(175, 290, 215, 290, color=INK, sw=2))
    f.append(text(170, 285, "OSC_OUT", size=10, color="#fca5a5", anchor="end", bold=True))

    # Демпфуючий резистор R_ext на OSC_OUT
    b_rext, _, _ = textbox(235, 290, "R_ext\n220 Ω", size=9.5, bold=True, fill="#fef3c7", stroke="#d97706", pad=5)
    f.append(b_rext)
    f.append(line(255, 290, 295, 290, color=INK, sw=2))

    # Кварц
    f.append(line(255, 230, 295, 230, color=INK, sw=2))
    f.append(line(295, 230, 295, 245, color=INK, sw=2))
    f.append(line(295, 290, 295, 275, color=INK, sw=2))

    b_xtal, _, _ = textbox(295, 260, "Кварц HSE\n8.000 МГц\nC_L = 16 пФ", size=10, bold=True, fill="#e0f2fe", stroke="#0284c7", pad=6)
    f.append(b_xtal)

    # C1 (на OSC_IN)
    f.append(line(255, 230, 255, 345, color=INK, sw=1.6))
    b_c1, _, _ = textbox(255, 375, "C1\n22 пФ\nC0G", size=10, bold=True, fill="#f1f5f9", stroke=NEG, pad=5)
    f.append(b_c1)
    f.append(line(255, 405, 255, 435, color=NEG, sw=1.6))
    f.append(text(255, 450, "GND_OSC", size=10, bold=True, color=NEG))

    # C2 (на OSC_OUT)
    f.append(line(335, 290, 335, 345, color=INK, sw=1.6))
    f.append(line(295, 290, 335, 290, color=INK, sw=2))
    b_c2, _, _ = textbox(335, 375, "C2\n22 пФ\nC0G", size=10, bold=True, fill="#f1f5f9", stroke=NEG, pad=5)
    f.append(b_c2)
    f.append(line(335, 405, 335, 435, color=NEG, sw=1.6))
    f.append(text(335, 450, "GND_OSC", size=10, bold=True, color=NEG))

    f.append(text(230, 485, "C_L = (C1·C2)/(C1+C2) + C_stray  (де C_stray ≈ 3–5 пФ)", size=10, color=FIELD, bold=True, anchor="middle"))


    # Права частина: Топологія Guard Ring
    f.append(text(680, 80, "Топологія розведення: Guard Ring на PCB", size=13, bold=True, color=INK))

    f.append(rect(470, 110, 420, 380, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8))

    f.append(rect(490, 190, 85, 140, fill="#1e293b", stroke=INK, sw=2, rx=4))
    f.append(text(532, 260, "МК\n(MCU)", size=12, bold=True, color="#ffffff"))

    f.append(rect(610, 160, 240, 190, fill="#dcfce7", stroke=FIELD, sw=2.5, rx=12))
    f.append(text(730, 150, "Земляне кільце (Guard Ring)", size=11, bold=True, color=FIELD))

    # Кварц SMD
    f.append(rect(660, 185, 140, 65, fill="#e2e8f0", stroke="#334155", sw=1.8, rx=4))
    f.append(text(730, 218, "XTAL SMD (8 МГц)", size=11, bold=True, color=INK))

    # Конденсатори C1, C2 SMD
    f.append(rect(650, 280, 50, 35, fill="#eff6ff", stroke=NEG, sw=1.5, rx=3))
    f.append(text(675, 302, "C1", size=10.5, bold=True, color=NEG))

    f.append(rect(760, 280, 50, 35, fill="#eff6ff", stroke=NEG, sw=1.5, rx=3))
    f.append(text(785, 302, "C2", size=10.5, bold=True, color=NEG))

    # Доріжки
    f.append(line(575, 210, 660, 210, color=POS, sw=2))
    f.append(line(575, 230, 660, 230, color=POS, sw=2))
    f.append(text(615, 202, "< 10 мм", size=9.5, color=POS, bold=True))

    f.append(line(675, 315, 675, 335, color=FIELD, sw=2))
    f.append(line(785, 315, 785, 335, color=FIELD, sw=2))
    f.append(circle(730, 335, 5, fill=FIELD, stroke=INK, sw=1))
    f.append(text(730, 360, "Єдина точка з'єднання із загальним GND", size=9.5, bold=True, color=FIELD))

    f.append(text(680, 410, "1. Жодних швидких цифрових сигналів під кварцом!", size=10, color=POS, bold=True, anchor="middle"))
    f.append(text(680, 430, "2. Суцільний земляний шар без розрізів під генератором", size=10, color=INK, anchor="middle"))
    f.append(text(680, 450, "3. Симетричні траси OSC_IN / OSC_OUT однакової довжини", size=10, color=INK, anchor="middle"))

    return render(os.path.join(IMG_DIR, "crystal-oscillator-layout.svg"), W, H, *f)


# ── 4. Інтерфейси відладки SWD проти JTAG ─────────────────────────────────────
def fig_swd_jtag():
    W, H = 940, 540
    f = []

    f.append(rect(20, 20, W - 40, H - 40, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, 45, "Інтерфейс відладки SWD (Serial Wire Debug): підключення та розпіновка", size=15, bold=True, color=INK))

    f.append(text(250, 85, "Апаратне з'єднання Програматор ↔ МК (SWD)", size=13, bold=True, color=INK))

    b_stlink, _, _ = textbox(110, 260, "Програматор\n/ Дебагер\n(ST-LINK,\nJ-Link, DAP)", size=10.5, bold=True, fill="#eef2f6", stroke="#475569", pad=8)
    f.append(b_stlink)

    b_mcu, _, _ = textbox(400, 260, "Мікроконтролер\nARM Cortex-M\n(SWD Debug Core)", size=10.5, bold=True, fill="#1e293b", stroke=INK, color="#ffffff", pad=8)
    f.append(b_mcu)

    # Лінії зв'язку:
    f.append(line(170, 170, 335, 170, color=POS, sw=2))
    f.append(text(250, 160, "1. VCC / VDD (3.3 В Опорна напруга)", size=10, bold=True, color=POS))

    f.append(line(170, 215, 335, 215, color="#2563eb", sw=2))
    f.append(text(250, 205, "2. SWDIO (PA13) — Дані", size=10, bold=True, color="#2563eb"))
    b_r_swdio, _, _ = textbox(250, 215, "R 22–47 Ω", size=9.5, bold=True, fill="#eff6ff", stroke="#2563eb", pad=3)
    f.append(b_r_swdio)

    f.append(line(170, 260, 335, 260, color="#d97706", sw=2))
    f.append(text(250, 250, "3. SWCLK (PA14) — Такт", size=10, bold=True, color="#d97706"))
    b_r_swclk, _, _ = textbox(250, 260, "R 22–47 Ω", size=9.5, bold=True, fill="#fef3c7", stroke="#d97706", pad=3)
    f.append(b_r_swclk)

    f.append(line(170, 305, 335, 305, color=NEG, sw=2))
    f.append(text(250, 320, "4. GND — Спільна земля", size=10, bold=True, color=NEG))

    f.append(line(170, 350, 335, 350, color="#7c3aed", sw=1.8, dash="5,4"))
    f.append(text(250, 365, "5. NRST (Скидання при прошивці)", size=9.5, bold=True, color="#7c3aed"))

    f.append(text(250, 420, "Внутрішні стани пінів Cortex-M за замовчуванням:", size=10, bold=True, color=INK))
    f.append(text(250, 440, "• SWDIO: внутрішній Pull-up до VDD (10–40 кОм)", size=9.5, color=MUTED))
    f.append(text(250, 460, "• SWCLK: внутрішній Pull-down до GND (10–40 кОм)", size=9.5, color=MUTED))


    # Права частина: Стандарти рознімів
    f.append(text(710, 85, "Розпіновка рознімів програмування", size=13, bold=True, color=INK))

    f.append(rect(540, 120, 340, 170, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    f.append(text(710, 140, "Arm Standard Cortex Debug (10-pin, 1.27 мм)", size=10.5, bold=True, color=INK))

    pins_arm10 = [
        ("1: VCC (3.3V)", "2: SWDIO / TMS"),
        ("3: GND",        "4: SWCLK / TCK"),
        ("5: GND",        "6: SWO / TDO (ITM trace)"),
        ("7: NC / Key",   "8: NC / TDI"),
        ("9: GNDDetect",  "10: nRESET (NRST)")
    ]
    for row, (p_left, p_right) in enumerate(pins_arm10):
        py = 165 + row * 22
        f.append(circle(560, py, 4, fill=POS if "VCC" in p_left else (NEG if "GND" in p_left else INK), stroke=LINE, sw=1))
        f.append(text(570, py + 3, p_left, size=9.5, color=INK, anchor="start"))
        f.append(circle(740, py, 4, fill="#2563eb" if "SWDIO" in p_right else ("#d97706" if "SWCLK" in p_right else INK), stroke=LINE, sw=1))
        f.append(text(750, py + 3, p_right, size=9.5, color=INK, anchor="start"))

    f.append(rect(540, 310, 340, 170, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    f.append(text(710, 330, "Мінімальний 4-pin рознім (SIL Header, 2.54 мм)", size=10.5, bold=True, color=INK))

    pins_min4 = [
        ("1: 3.3V", "VCC", POS),
        ("2: SWDIO", "PA13", "#2563eb"),
        ("3: SWCLK", "PA14", "#d97706"),
        ("4: GND", "GND", NEG)
    ]
    for i, (p_name, p_sub, col) in enumerate(pins_min4):
        px = 580 + i * 75
        f.append(circle(px, 380, 8, fill="#ffffff", stroke=col, sw=2))
        f.append(circle(px, 380, 3, fill=col, stroke=col, sw=1))
        f.append(text(px, 410, p_name, size=10, bold=True, color=col))
        f.append(text(px, 425, p_sub, size=9.5, color=MUTED))

    f.append(text(710, 460, "Найзручніший формат для власних міні-плат", size=9.5, bold=True, color=FIELD))

    return render(os.path.join(IMG_DIR, "swd-jtag-interface.svg"), W, H, *f)


# ── 5. Повна зведена схема мінімальної обв'язки МК (All-in-One Master Schematic) ──
def fig_minimal_breakout():
    W, H = 960, 640
    f = []

    f.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, 40, "Повна принципова схема мінімального робочого модуля на базі ARM Cortex-M", size=15, bold=True, color=INK))

    # Центральний чіп МК (LQFP48 / LQFP64)
    cx, cy, cw, ch = 390, 100, 180, 450
    f.append(rect(cx, cy, cw, ch, fill="#1e293b", stroke=INK, sw=2.2, rx=8))
    f.append(text(cx + cw / 2, cy + 30, "STM32F4 / Cortex-M", size=13, bold=True, color="#ffffff"))
    f.append(text(cx + cw / 2, cy + 50, "Мінімальний модуль", size=10, color="#94a3b8"))

    # Блок 1: Живлення та розв'язка (ліворуч угорі)
    f.append(rect(30, 70, 320, 175, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=6))
    f.append(text(190, 92, "1. Шини живлення та декаплінг", size=11, bold=True, color="#0284c7"))
    f.append(text(45, 120, "• 3.3V Вхід + 10 мкФ Bulk тантал", size=9.5, color=INK, anchor="start"))
    f.append(text(45, 140, "• 4× 100 нФ MLCC на кожну пару VDD/VSS", size=9.5, color=INK, anchor="start"))
    f.append(text(45, 160, "• VDDA: Ferrite Bead 120Ω + 1 мкФ + 10 нФ", size=9.5, color=INK, anchor="start"))
    f.append(text(45, 180, "• VCAP_1 / VCAP_2: 2.2 мкФ кераміка (LDO)", size=9.5, color=INK, anchor="start"))
    f.append(text(45, 210, "-> Стабільні шини VDD, VDDA, VCAP", size=9.5, bold=True, color=FIELD, anchor="start"))
    f.append(arrow(350, 150, cx, 150, color="#0284c7", sw=2))

    # Блок 2: Ланцюг скидання NRST (ліворуч посередині)
    f.append(rect(30, 260, 320, 145, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    f.append(text(190, 282, "2. Апаратне скидання (NRST)", size=11, bold=True, color=POS))
    f.append(text(45, 310, "• Внутрішній Pull-up 40 кОм до VDD", size=9.5, color=INK, anchor="start"))
    f.append(text(45, 330, "• Зовнішній фільтр: 100 нФ на GND (τ ≈ 4 мс)", size=9.5, color=INK, anchor="start"))
    f.append(text(45, 350, "• Тактова кнопка паралельно C_NRST", size=9.5, color=INK, anchor="start"))
    f.append(text(45, 375, "• Лінія Open-Drain на рознім SWD", size=9.5, bold=True, color=MUTED, anchor="start"))
    f.append(arrow(350, 330, cx, 330, color=POS, sw=2))

    # Блок 3: Конфігурація завантаження BOOT (ліворуч знизу)
    f.append(rect(30, 420, 320, 130, fill="#ffffff", stroke="#ca8a04", sw=1.5, rx=6))
    f.append(text(190, 442, "3. Вибір старту (BOOT0/BOOT1)", size=11, bold=True, color="#ca8a04"))
    f.append(text(45, 470, "• BOOT0: 10 кОм на GND (Штатний Flash)", size=9.5, color=INK, anchor="start"))
    f.append(text(45, 490, "• BOOT1: 10 кОм на GND", size=9.5, color=INK, anchor="start"))
    f.append(text(45, 510, "• 3-pin перемикач на VDD для ROM-прошивки", size=9.5, color=INK, anchor="start"))
    f.append(arrow(350, 480, cx, 480, color="#ca8a04", sw=2))

    # Блок 4: Тактові генератори HSE / LSE (праворуч угорі)
    f.append(rect(610, 70, 320, 225, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(770, 92, "4. Тактування (HSE та LSE)", size=11, bold=True, color=FIELD))
    f.append(text(625, 120, "• HSE: Кварц 8.000 МГц (або 25 МГц)", size=9.5, color=INK, anchor="start"))
    f.append(text(625, 140, "• Конденсатори C1, C2 = 20–22 пФ (NP0)", size=9.5, color=INK, anchor="start"))
    f.append(text(625, 160, "• Демпфер R_ext = 220 Ω на OSC_OUT", size=9.5, color=INK, anchor="start"))
    f.append(text(625, 185, "• LSE: Годинниковий кварц 32.768 кГц (RTC)", size=9.5, color=INK, anchor="start"))
    f.append(text(625, 205, "• Конденсатори LSE: C3, C4 = 10–12 пФ", size=9.5, color=INK, anchor="start"))
    f.append(text(625, 230, "• Топологія: Кільце Guard Ring на PCB", size=9.5, bold=True, color=FIELD, anchor="start"))
    f.append(arrow(cx + cw, 170, 610, 170, color=FIELD, sw=2))

    # Блок 5: Інтерфейс відладки SWD (праворуч знизу)
    f.append(rect(610, 310, 320, 240, fill="#ffffff", stroke="#7c3aed", sw=1.5, rx=6))
    f.append(text(770, 332, "5. Налагодження SWD / JTAG", size=11, bold=True, color="#7c3aed"))
    f.append(text(625, 360, "• Pin 1: VCC (3.3V Опора)", size=9.5, color=POS, anchor="start", bold=True))
    f.append(text(625, 380, "• Pin 2: SWDIO (PA13) + резистор 22–47 Ω", size=9.5, color="#2563eb", anchor="start", bold=True))
    f.append(text(625, 400, "• Pin 3: SWCLK (PA14) + резистор 22–47 Ω", size=9.5, color="#d97706", anchor="start", bold=True))
    f.append(text(625, 420, "• Pin 4: GND (Земля)", size=9.5, color=NEG, anchor="start", bold=True))
    f.append(text(625, 440, "• Pin 5: NRST (Скидання ядра)", size=9.5, color="#7c3aed", anchor="start", bold=True))
    f.append(text(625, 470, "Розніми: Arm 10-pin (1.27 мм) / 4-pin SIL (2.54 мм)", size=9.5, color=MUTED, anchor="start"))
    f.append(arrow(cx + cw, 410, 610, 410, color="#7c3aed", sw=2))

    f.append(text(W / 2, 595, "Мінімальний модуль повністю самодостатній: запускається, тактується, прошивається та відлагоджується", size=11, bold=True, color=FIELD))

    return render(os.path.join(IMG_DIR, "mcu-minimal-breakout-schematic.svg"), W, H, *f)


if __name__ == "__main__":
    fig_power_decoupling()
    fig_reset_boot()
    fig_crystal_oscillators()
    fig_swd_jtag()
    fig_minimal_breakout()
    print("Всі фігури згенеровано успішно у ./img/")
