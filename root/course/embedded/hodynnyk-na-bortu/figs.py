# -*- coding: utf-8 -*-
import sys, os

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. quartz-temp-drift: парабола температурного дрейфу 32.768 кГц ──────────
def fig_quartz_temp_drift():
    W, H = 760, 360
    p = []
    
    # Координатна сітка
    x0, y0 = 120, 100
    w_grid, h_grid = 520, 180
    
    # Осі
    p.append(line(x0, y0, x0 + w_grid, y0, color=LINE, sw=1.5))       # Вісь 0 ppm (горизонтальна)
    p.append(line(x0, y0, x0, y0 + h_grid + 20, color=LINE, sw=1.5))  # Вісь від'ємного дрейфу вниз
    p.append(arrow(x0 + w_grid, y0, x0 + w_grid + 30, y0, color=LINE, sw=1.5))
    p.append(arrow(x0, y0 + h_grid + 20, x0, y0 + h_grid + 45, color=LINE, sw=1.5))
    
    p.append(text(x0 + w_grid + 35, y0 - 10, "Температура T (°C)", size=11, color=INK, anchor="end", bold=True))
    p.append(text(x0 - 15, y0 + h_grid + 40, "Дрейф (ppm / с·добу)", size=11, color=INK, anchor="end", bold=True))
    
    # Сітка та мітки температури (T від -30°C до +70°C, пік на +25°C)
    def t_to_x(t):
        return x0 + 40 + (t + 30) * 4.4
    
    def ppm_to_y(ppm):
        return y0 + abs(ppm) * 1.6
    
    temps = [-30, -10, 10, 25, 50, 70]
    for t in temps:
        tx = t_to_x(t)
        p.append(line(tx, y0 - 4, tx, y0 + h_grid, color="#e2e8f0", sw=1.0, dash="3,3"))
        p.append(text(tx, y0 - 12, "%d°" % t, size=10, color=MUTED, anchor="middle"))
        
    ppms = [0, -20, -40, -60, -80, -100]
    for val in ppms:
        py = ppm_to_y(val)
        p.append(line(x0 - 4, py, x0 + w_grid, py, color="#e2e8f0", sw=1.0, dash="3,3"))
        s_day = abs(val) * 0.0864
        p.append(text(x0 - 10, py + 4, "%d ppm (%.1f с)" % (val, s_day), size=9.5, color=MUTED, anchor="end"))
        
    # Парабола дрейфу: df = -0.04 * (T - 25)^2
    points = []
    for t_val in range(-30, 71, 2):
        drift = -0.04 * ((t_val - 25) ** 2)
        px = t_to_x(t_val)
        py = ppm_to_y(drift)
        points.append((px, py))
        
    poly_str = " ".join(["%.1f,%.1f" % pt for pt in points])
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly_str, POS))
    
    # Виділення ключових точок
    x_25 = t_to_x(25)
    y_25 = ppm_to_y(0)
    p.append(circle(x_25, y_25, 4.5, fill=FIELD, stroke=FIELD))
    p.append(text(x_25, y_25 + 18, "T₀ = 25 °C (вершина)", size=10.5, color=FIELD, bold=True))
    
    # Точка -20°C (дрейф -81 ppm ≈ -7.0 с/добу)
    x_m20 = t_to_x(-20)
    y_m20 = ppm_to_y(-81)
    p.append(circle(x_m20, y_m20, 4.5, fill=POS, stroke=POS))
    p.append(text(x_m20 + 8, y_m20 - 8, "-20 °C: -81 ppm (-7.0 с/добу)", size=9.5, color=POS, anchor="start", bold=True))
    
    # Точка +60°C (дрейф -49 ppm ≈ -4.2 с/добу)
    x_p60 = t_to_x(60)
    y_p60 = ppm_to_y(-49)
    p.append(circle(x_p60, y_p60, 4.5, fill=POS, stroke=POS))
    p.append(text(x_p60 + 8, y_p60 - 8, "+60 °C: -49 ppm (-4.2 с/добу)", size=9.5, color=POS, anchor="start", bold=True))
    
    # Формула в прямокутнику
    b, _, _ = textbox(540, 260, "Δf/f₀ = -β · (T - T₀)²\nβ ≈ 0.04 ppm/°C²\nдрейф ЗАВЖДИ в мінус", size=10.5,
                      fill="#fff9db", stroke="#f59f00", pad=8)
    p.append(b)
    
    p.append(text(W / 2, H - 15, "Камертонний кварц 32.768 кГц за будь-якого відхилення від 25 °C відстає",
                  size=11, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "quartz-temp-drift.svg"), W, H, *p,
           title="Температурний дрейф годинникового кварцу 32.768 кГц")


# ── 2. rtc-power-domains: розділення доменів живлення VDD та VBAT ────────────
def fig_rtc_power_domains():
    W, H = 760, 340
    p = []
    
    # Головний домен (VDD 3.3V)
    p.append(rect(40, 60, 240, 230, fill="#f8fafc", stroke=NEG, sw=1.8, rx=8))
    p.append(text(160, 84, "ГОЛОВНИЙ ДОМЕН (VDD)", size=12, color=NEG, bold=True))
    
    b_cpu = fitbox(60, 105, 200, 36, "Ядро процесора (CPU)\n240 МГц / 160 МГц", size=10, fill="#ffffff", stroke=MUTED)
    b_ram = fitbox(60, 150, 200, 36, "SRAM та Flash-пам'ять\nСкидається при знеструмленні", size=10, fill="#ffffff", stroke=MUTED)
    b_per = fitbox(60, 195, 200, 36, "Високошвидкісна периферія\nШини APB / AHB, DMA", size=10, fill="#ffffff", stroke=MUTED)
    p.extend([b_cpu, b_ram, b_per])
    p.append(text(160, 265, "Струм споживання: 20–150 мА", size=10, color=MUTED, italic=True))
    
    # Автоматичний перемикач живлення (Power Switch MUX)
    p.append(rect(320, 115, 120, 120, fill="#eef3ff", stroke=NEG, sw=1.8, rx=8))
    p.append(mtext(380, 145, "Автоматичний\nперемикач\n(Power Switch)", size=10.5, color=INK, bold=True))
    p.append(text(380, 215, "VDD > 2.0V → VDD\nVDD < 2.0V → VBAT", size=9.5, color=MUTED))
    
    # Домен резервного живлення (AON / Backup Domain)
    p.append(rect(480, 60, 240, 230, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(600, 84, "РЕЗЕРВНИЙ ДОМЕН (AON / VBAT)", size=12, color=FIELD, bold=True))
    
    b_rtc = fitbox(500, 105, 200, 36, "Апаратний RTC-лічильник\nСекунди, субсекунди, дата", size=10, fill="#ffffff", stroke=MUTED)
    b_lse = fitbox(500, 150, 200, 36, "Генератор LSE 32.768 кГц\nКамертонний кварц", size=10, fill="#ffffff", stroke=MUTED)
    b_bkp = fitbox(500, 195, 200, 36, "Backup SRAM (калібрування)\nРегістри збереження стану", size=10, fill="#ffffff", stroke=MUTED)
    p.extend([b_rtc, b_lse, b_bkp])
    p.append(text(600, 265, "Струм споживання: 300–800 нА", size=10, color=FIELD, bold=True))
    
    # Зв'язки ліній живлення
    # VDD -> Switch
    p.append(arrow(280, 150, 320, 150, color=NEG, sw=2))
    p.append(text(300, 140, "VDD", size=9.5, color=NEG, bold=True))
    
    # VBAT (зовнішня батарея) -> Switch
    p.append(arrow(380, 280, 380, 235, color=FIELD, sw=2))
    p.append(circle(380, 298, 14, fill="#fdecea", stroke=POS, sw=1.5))
    p.append(text(380, 302, "BAT", size=10, color=POS, bold=True))
    p.append(text(380, 324, "CR2032 / Іоністор", size=9.5, color=INK))
    
    # Switch -> AON Domain
    p.append(arrow(440, 175, 480, 175, color=FIELD, sw=2))
    p.append(text(460, 165, "V_RTC", size=9.5, color=FIELD, bold=True))
    
    render(os.path.join(OUT, "rtc-power-domains.svg"), W, H, *p,
           title="Розділення доменів живлення мікроконтролера та живлення RTC")


# ── 3. monotonic-vs-wall-step: стрибок настінного часу проти монотонного ────
def fig_monotonic_vs_wall_step():
    W, H = 760, 330
    p = []
    
    # Верхній трек: Настінний час (Wall clock) зі стрибком назад
    y_wall = 90
    p.append(text(60, y_wall - 18, "Настінний час (Wall Clock / gettimeofday)", size=12, color=POS, anchor="start", bold=True))
    p.append(line(60, y_wall + 30, 680, y_wall + 30, color="#cbd5e1", sw=1.5))
    
    # Часові позначки на верхній шкалі
    p.append(line(100, y_wall + 25, 340, y_wall - 20, color=POS, sw=2.5))
    # Стрибок вниз
    p.append(line(340, y_wall - 20, 340, y_wall + 10, color=POS, sw=2, dash="4,3"))
    p.append(arrow(340, y_wall - 20, 340, y_wall + 5, color=POS, sw=2))
    p.append(text(348, y_wall - 5, "NTP Step (-10 с)", size=10, color=POS, anchor="start", bold=True))
    # Продовження після стрибка
    p.append(line(340, y_wall + 10, 600, y_wall - 40, color=POS, sw=2.5))
    
    # Зона катастрофи для таймера інтервалу
    p.append(rect(280, y_wall + 38, 180, 24, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    p.append(text(370, y_wall + 54, "Δt = t_end - t_start = -4 с (< 0 !)", size=9.5, color=POS, bold=True))
    
    # Нижній трек: Монотонний час (CLOCK_MONOTONIC)
    y_mono = 220
    p.append(text(60, y_mono - 18, "Монотонний годинник (CLOCK_MONOTONIC / steady_clock)", size=12, color=FIELD, anchor="start", bold=True))
    p.append(line(60, y_mono + 30, 680, y_mono + 30, color="#cbd5e1", sw=1.5))
    
    # Безперервна лінія
    p.append(line(100, y_mono + 25, 600, y_mono - 45, color=FIELD, sw=2.5))
    
    # Позначення відрізка вимірювання
    p.append(line(280, y_mono + 30, 280, y_mono + 2, color=LINE, sw=1.5, dash="2,2"))
    p.append(line(460, y_mono + 30, 460, y_mono - 25, color=LINE, sw=1.5, dash="2,2"))
    p.append(circle(280, y_mono + 2, 4, fill=FIELD, stroke=FIELD))
    p.append(circle(460, y_mono - 25, 4, fill=FIELD, stroke=FIELD))
    
    p.append(arrow(280, y_mono + 45, 460, y_mono + 45, color=FIELD, sw=1.8))
    p.append(text(370, y_mono + 60, "Δt = +6.0 с (гарантовано строго > 0)", size=10, color=FIELD, bold=True))
    
    p.append(text(W / 2, H - 12, "Стрибок настінного часу ламає таймери й дельти; монотонний час завжди неперервний",
                  size=11, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "monotonic-vs-wall-step.svg"), W, H, *p,
           title="Стрибок настінного часу проти неперервності монотонного")


# ── 4. time-slew-vs-step: миттєвий крок проти плавного підтягування (Slew) ───
def fig_time_slew_vs_step():
    W, H = 760, 320
    p = []
    
    # Лівий блок: Миттєвий крок (Step Adjustment)
    cx1 = 200
    p.append(rect(40, 60, 320, 220, fill="#fef2f2", stroke=POS, sw=1.6, rx=8))
    p.append(text(cx1, 85, "МИTTЄВИЙ КРОК (STEP)", size=13, color=POS, bold=True))
    
    # Графік кроку
    p.append(line(70, 220, 330, 220, color=MUTED, sw=1.2))
    p.append(line(70, 220, 70, 110, color=MUTED, sw=1.2))
    
    p.append(line(70, 200, 180, 150, color=POS, sw=2.2))
    p.append(line(180, 150, 180, 180, color=POS, sw=2, dash="4,3"))
    p.append(arrow(180, 150, 180, 178, color=POS, sw=2))
    p.append(line(180, 180, 320, 130, color=POS, sw=2.2))
    
    p.append(text(cx1, 245, "Стрибок стрілок назад на Δt = -2 с", size=10, color=POS, bold=True))
    p.append(text(cx1, 265, "Розрив неперервності, гонитви, дублі логів", size=9.5, color=MUTED))
    
    # Правий блок: Плавне підтягування (Time Slew)
    cx2 = 560
    p.append(rect(400, 60, 320, 220, fill="#f0fdf4", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(cx2, 85, "ПЛАВНЕ ПІДТЯГУВАННЯ (SLEW)", size=13, color=FIELD, bold=True))
    
    # Графік slew
    p.append(line(430, 220, 690, 220, color=MUTED, sw=1.2))
    p.append(line(430, 220, 430, 110, color=MUTED, sw=1.2))
    
    # Опорний еталон (пунктир)
    p.append(line(430, 200, 680, 120, color=MUTED, sw=1.5, dash="4,4"))
    p.append(text(680, 115, "Еталон", size=9.5, color=MUTED, anchor="end"))
    
    # Локальний годинник що плавно наздоганяє без стрибка
    p.append('<path d="M 430 185 Q 540 160 670 123" fill="none" stroke="%s" stroke-width="2.5"/>' % FIELD)
    
    p.append(text(cx2, 245, "Зміна темпу ходу на ±500 ppm (±0.05%)", size=10, color=FIELD, bold=True))
    p.append(text(cx2, 265, "Час завжди монотонний, нуль стрибків", size=9.5, color=FIELD))
    
    p.append(text(W / 2, H - 15, "Slew поступово вибирає похибку фази за рахунок мікрозміни частоти генератора",
                  size=11, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "time-slew-vs-step.svg"), W, H, *p,
           title="Корекція часу: миттєвий крок проти плавного підтягування (Slew)")


# ── 5. rtc-driver-architecture: архітектура драйвера бортового часу ──────────
def fig_rtc_driver_architecture():
    W, H = 760, 360
    p = []
    
    # Апаратний шар (Hardware)
    p.append(rect(40, 60, 200, 240, fill="#f8fafc", stroke=MUTED, sw=1.6, rx=8))
    p.append(text(140, 85, "АПАРАТНИЙ ШАР", size=12, color=MUTED, bold=True))
    
    b_hw1 = fitbox(55, 110, 170, 42, "32-бітний таймер\n(SysTick / TIMx 1 МГц)", size=10, fill="#ffffff", stroke=MUTED)
    b_hw2 = fitbox(55, 170, 170, 42, "Кварц LSE 32.768 кГц\n(Апаратний RTC)", size=10, fill="#ffffff", stroke=MUTED)
    b_hw3 = fitbox(55, 230, 170, 42, "Регістр калібрування\n(RTC_CALR / fractional)", size=10, fill="#ffffff", stroke=MUTED)
    p.extend([b_hw1, b_hw2, b_hw3])
    
    # Ядро драйвера часу (Time Engine Core)
    p.append(rect(280, 60, 240, 240, fill="#eef3ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(400, 85, "ЯДРО ДРАЙВЕРА ЧАСУ", size=12, color=NEG, bold=True))
    
    b_core1 = fitbox(295, 105, 210, 40, "64-бітний акумулятор тіків\n(Розширення без переповнення)", size=9.5, fill="#ffffff", stroke=NEG)
    b_core2 = fitbox(295, 155, 210, 40, "Фільтр корекції Slew (PI-PLL)\nЧастотна підгонка ppm", size=9.5, fill="#ffffff", stroke=NEG)
    b_core3 = fitbox(295, 205, 210, 40, "Зсув епохи (Epoch Base UTC)\nЗбереження в Backup SRAM", size=9.5, fill="#ffffff", stroke=NEG)
    b_core4 = fitbox(295, 255, 210, 32, "Атомарний захист (Seqlock / Mutex)", size=9.5, fill="#ffffff", stroke=MUTED)
    p.extend([b_core1, b_core2, b_core3, b_core4])
    
    # Прикладні інтерфейси (Application APIs)
    p.append(rect(560, 60, 160, 240, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(640, 85, "ПРИКЛАДНИЙ API", size=12, color=FIELD, bold=True))
    
    b_api1 = fitbox(570, 110, 140, 45, "monotonic_now_us()\nТаймаути, дельти,\nPID-регулятори", size=9.5, fill="#ffffff", stroke=FIELD)
    b_api2 = fitbox(570, 175, 140, 45, "wall_clock_get_utc()\nЛоги, TLS-сертифікати,\nРозклад", size=9.5, fill="#ffffff", stroke=FIELD)
    b_api3 = fitbox(570, 240, 140, 45, "time_sync_slew()\nПлавне вирівнювання\nвід NTP / GNSS", size=9.5, fill="#ffffff", stroke=FIELD)
    p.extend([b_api1, b_api2, b_api3])
    
    # Стрілки взаємодії
    p.append(arrow(225, 131, 280, 131, color=LINE, sw=1.6))
    p.append(arrow(225, 191, 280, 191, color=LINE, sw=1.6))
    p.append(arrow(280, 251, 225, 251, color=LINE, sw=1.6))
    
    p.append(arrow(520, 131, 560, 131, color=FIELD, sw=1.6))
    p.append(arrow(520, 195, 560, 195, color=FIELD, sw=1.6))
    p.append(arrow(560, 260, 520, 260, color=NEG, sw=1.6))
    
    render(os.path.join(OUT, "rtc-driver-architecture.svg"), W, H, *p,
           title="Архітектура бортового драйвера монотонного й настінного часу")


if __name__ == "__main__":
    fig_quartz_temp_drift()
    fig_rtc_power_domains()
    fig_monotonic_vs_wall_step()
    fig_time_slew_vs_step()
    fig_rtc_driver_architecture()
    print("OK: all 5 figures generated successfully in", OUT)
