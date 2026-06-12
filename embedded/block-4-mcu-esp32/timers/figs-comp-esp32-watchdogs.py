# -*- coding: utf-8 -*-
"""
Фігури для вставки ch24-s7-c-esp32-watchdogs.md
«Три watchdog-и ESP32: TWDT, RTC WDT, зовнішній супервізор»

Рис. 4.6.7c.1 — ешелон сторожів: TWDT/IWDT у CPU-домені, RWDT у RTC-домені,
                зовнішній чип над усіма доменами.
Рис. 4.6.7c.2 — віконний зовнішній супервізор (часова вісь).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Палітра (розширення стандартної svgkit) ──────────────────────────────────
ORANGE  = "#e67e22"
LORANGE = "#fdf2e9"
PURPLE  = "#7d3c98"
LPURPLE = "#f5eef8"
TEAL    = "#1a7a73"
LTEAL   = "#e8f8f7"
LGREEN  = "#eafaf1"
LRED    = "#fdedec"
LBLUE   = "#eaf3fb"
DGREY   = "#555555"
LGREY   = "#f0f0f0"
SHADOW  = "#cccccc"


# ════════════════════════════════════════════════════════════════════════════════
# Рис. 4.6.7c.1 — ешелон сторожів ESP32
# ════════════════════════════════════════════════════════════════════════════════
def fig1_watchdog_echelon():
    W, H = 820, 480
    frags = []

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W // 2, 28, "Ешелон watchdog-ів ESP32", size=17, bold=True))

    # ────────────────────────────────────────────────────────────────────────
    # 1. CPU-домен (велика рамка зліва)
    # ────────────────────────────────────────────────────────────────────────
    cpu_x, cpu_y, cpu_w, cpu_h = 30, 52, 490, 260
    frags.append(rect(cpu_x, cpu_y, cpu_w, cpu_h,
                      fill=LBLUE, stroke=NEG, sw=2.5, rx=10))
    frags.append(text(cpu_x + cpu_w // 2, cpu_y + 22,
                      "CPU-домен  (ядра + пам'ять + периферія)", size=13,
                      color=NEG, bold=True))

    # ── TWDT всередині CPU-домену ─────────────────────────────────────────
    twdt_x, twdt_y, twdt_w, twdt_h = 48, 88, 215, 198
    frags.append(rect(twdt_x, twdt_y, twdt_w, twdt_h,
                      fill="#dce9fb", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(twdt_x + twdt_w // 2, twdt_y + 20,
                      "TWDT", size=14, color=NEG, bold=True))

    # idle-задачі всередині TWDT
    frags.append(fitbox(twdt_x + 12, twdt_y + 38, twdt_w - 24, 38,
                        "idle0 (ядро 0)", size=12, fill="#c6d9f8", stroke=NEG, sw=1.2))
    frags.append(fitbox(twdt_x + 12, twdt_y + 85, twdt_w - 24, 38,
                        "idle1 (ядро 1)", size=12, fill="#c6d9f8", stroke=NEG, sw=1.2))
    frags.append(text(twdt_x + twdt_w // 2, twdt_y + 143,
                      "+ ваші задачі", size=11, color=MUTED, italic=True))
    frags.append(text(twdt_x + twdt_w // 2, twdt_y + 162,
                      "(esp_task_wdt_add)", size=10, color=MUTED, italic=True))
    frags.append(text(twdt_x + twdt_w // 2, twdt_y + 182,
                      "Ловить: задача-ненажера", size=10, color=NEG))

    # ── IWDT всередині CPU-домену ─────────────────────────────────────────
    iwdt_x, iwdt_y, iwdt_w, iwdt_h = 278, 88, 215, 198
    frags.append(rect(iwdt_x, iwdt_y, iwdt_w, iwdt_h,
                      fill="#dce9fb", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(iwdt_x + iwdt_w // 2, iwdt_y + 20,
                      "IWDT", size=14, color=NEG, bold=True))
    frags.append(fitbox(iwdt_x + 12, iwdt_y + 38, iwdt_w - 24, 50,
                        "Вимкнені переривання\nнадто довго", size=11,
                        fill="#c6d9f8", stroke=NEG, sw=1.2))
    frags.append(fitbox(iwdt_x + 12, iwdt_y + 100, iwdt_w - 24, 38,
                        "Завислий ISR", size=11,
                        fill="#c6d9f8", stroke=NEG, sw=1.2))
    frags.append(text(iwdt_x + iwdt_w // 2, iwdt_y + 162,
                      "Завжди → panic + reset", size=10, color=NEG))
    frags.append(text(iwdt_x + iwdt_w // 2, iwdt_y + 182,
                      "Планувальник теж стоїть", size=10, color=MUTED, italic=True))

    # ── Стрілки TWDT/IWDT → «RESET» (спільна мітка для CPU) ──────────────
    frags.append(arrow(twdt_x + twdt_w // 2, twdt_y + twdt_h,
                       twdt_x + twdt_w // 2, cpu_y + cpu_h - 8, color=NEG))
    frags.append(arrow(iwdt_x + iwdt_w // 2, iwdt_y + iwdt_h,
                       iwdt_x + iwdt_w // 2, cpu_y + cpu_h - 8, color=NEG))

    reset_cpu_x = cpu_x + cpu_w // 2
    frags.append(text(reset_cpu_x, cpu_y + cpu_h - 10,
                      "→ reset/panic", size=11, color=NEG, bold=True))

    # ────────────────────────────────────────────────────────────────────────
    # 2. RTC-домен (права рамка, менша)
    # ────────────────────────────────────────────────────────────────────────
    rtc_x, rtc_y, rtc_w, rtc_h = 540, 52, 220, 260
    frags.append(rect(rtc_x, rtc_y, rtc_w, rtc_h,
                      fill=LGREEN, stroke=FIELD, sw=2.5, rx=10))
    frags.append(text(rtc_x + rtc_w // 2, rtc_y + 22,
                      "RTC-домен", size=13, color=FIELD, bold=True))
    frags.append(text(rtc_x + rtc_w // 2, rtc_y + 38,
                      "(найживучіший)", size=11, color=MUTED, italic=True))

    # RWDT всередині RTC-домену
    rwdt_x, rwdt_y, rwdt_w, rwdt_h = rtc_x + 12, rtc_y + 55, rtc_w - 24, 140
    frags.append(rect(rwdt_x, rwdt_y, rwdt_w, rwdt_h,
                      fill="#c9ecd4", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(rwdt_x + rwdt_w // 2, rwdt_y + 22,
                      "RTC WDT (RWDT)", size=13, color=FIELD, bold=True))
    frags.append(fitbox(rwdt_x + 8, rwdt_y + 36, rwdt_w - 16, 36,
                        "bootloader → старт", size=11,
                        fill="#a8dcb8", stroke=FIELD, sw=1.2))
    frags.append(text(rwdt_x + rwdt_w // 2, rwdt_y + 92,
                      "Від RTC-генератора", size=10, color=FIELD))
    frags.append(text(rwdt_x + rwdt_w // 2, rwdt_y + 110,
                      "Причина: RTCWDT_*", size=10, color=FIELD))
    frags.append(arrow(rwdt_x + rwdt_w // 2, rwdt_y + rwdt_h,
                       rwdt_x + rwdt_w // 2, rtc_y + rtc_h - 8, color=FIELD))
    frags.append(text(rwdt_x + rwdt_w // 2, rtc_y + rtc_h - 10,
                      "→ reset", size=11, color=FIELD, bold=True))

    # ────────────────────────────────────────────────────────────────────────
    # 3. SoC-межа (пунктирна рамка навколо обох доменів)
    # ────────────────────────────────────────────────────────────────────────
    soc_x, soc_y, soc_w, soc_h = 16, 38, 762, 290
    frags.append(
        '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="14" '
        'fill="none" stroke="%s" stroke-width="2" stroke-dasharray="8,5"/>'
        % (soc_x, soc_y, soc_w, soc_h, DGREY)
    )
    frags.append(text(soc_x + 8, soc_y + 14, "ESP32  SoC", size=11,
                      color=DGREY, anchor="start"))

    # ────────────────────────────────────────────────────────────────────────
    # 4. Зовнішній супервізор (над/під SoC — нижня частина)
    # ────────────────────────────────────────────────────────────────────────
    ext_x, ext_y, ext_w, ext_h = 60, 355, 700, 100
    frags.append(rect(ext_x, ext_y, ext_w, ext_h,
                      fill=LORANGE, stroke=ORANGE, sw=2.5, rx=10))
    frags.append(text(ext_x + ext_w // 2, ext_y + 22,
                      "Зовнішній чип-супервізор (TPLxxxx / MAXxxxx-клас)",
                      size=13, color=ORANGE, bold=True))

    # «розпіновка» зовнішнього
    pin_texts = [
        ("WDI ←", "GPIO ESP32 смикає імпульсом (годівля)", NEG),
        ("RESET →", "EN/RST ESP32 — скидає весь SoC", POS),
        ("window", "апаратне вікно: не зарано й не запізно", ORANGE),
    ]
    px = ext_x + 28
    for i, (pin, desc, col) in enumerate(pin_texts):
        py = ext_y + 44 + i * 20
        frags.append(text(px, py, pin, size=11, color=col, bold=True, anchor="start"))
        frags.append(text(px + 90, py, desc, size=11, color=INK, anchor="start"))

    # ── Стрілки: SoC → зовнішній (WDI) і зовнішній → SoC (RESET) ────────
    # WDI: праворуч від SoC-рамки вниз
    frags.append(arrow(650, soc_y + soc_h, 650, ext_y, color=NEG))
    frags.append(text(662, soc_y + soc_h + 14, "WDI", size=10,
                      color=NEG, anchor="start"))

    # RESET: зліва від зовнішнього вгору до SoC EN
    frags.append(arrow(180, ext_y, 180, soc_y + soc_h, color=POS))
    frags.append(text(140, soc_y + soc_h + 12, "EN/RST", size=10,
                      color=POS, anchor="start"))

    # ── Коментар «ззовні всіх доменів» ───────────────────────────────────
    frags.append(text(ext_x + ext_w // 2, ext_y + ext_h + 22,
                      "Ззовні всіх доменів SoC — рятує навіть за глибокого збою кремнію",
                      size=11, color=ORANGE))

    path = os.path.join(OUT, "fig-24-7c-1-watchdog-echelon.svg")
    render(path, W, H, *frags,
           title=None)
    print("  OK", path)


# ════════════════════════════════════════════════════════════════════════════════
# Рис. 4.6.7c.2 — віконний зовнішній супервізор (часова вісь)
# ════════════════════════════════════════════════════════════════════════════════
def fig2_windowed_supervisor():
    W, H = 740, 300
    frags = []

    frags.append(text(W // 2, 28, "Віконний зовнішній супервізор: вікно годівлі",
                      size=17, bold=True))

    # ── Часова вісь ──────────────────────────────────────────────────────────
    ax_y = 160
    ax_x0, ax_x1 = 50, 690
    frags.append(arrow(ax_x0, ax_y, ax_x1, ax_y, color=INK))
    frags.append(text(ax_x1 + 10, ax_y + 4, "час", size=12, color=INK, anchor="start"))

    # ── Зони ─────────────────────────────────────────────────────────────────
    zone_h = 52
    zone_y = ax_y - zone_h // 2

    # «зарано» (0 → w_start)
    w_start = 200
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="%s" opacity="0.55" stroke="none"/>'
                 % (ax_x0, zone_y, w_start - ax_x0, zone_h, LRED))
    frags.append(text((ax_x0 + w_start) // 2, ax_y - zone_h // 2 - 10,
                      "ЗАРАНО", size=12, color=POS, bold=True))
    frags.append(text((ax_x0 + w_start) // 2, ax_y - zone_h // 2 - 26,
                      "→ reset", size=11, color=POS))

    # «вікно» (w_start → w_end)
    w_end = 520
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="%s" opacity="0.6" stroke="none"/>'
                 % (w_start, zone_y, w_end - w_start, zone_h, LGREEN))
    frags.append(text((w_start + w_end) // 2, ax_y,
                      "ВІКНО — годуй тут", size=13, color=FIELD, bold=True))

    # «запізно» (w_end → ax_x1)
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="%s" opacity="0.55" stroke="none"/>'
                 % (w_end, zone_y, ax_x1 - w_end, zone_h, LRED))
    frags.append(text((w_end + ax_x1) // 2, ax_y - zone_h // 2 - 10,
                      "ЗАПІЗНО", size=12, color=POS, bold=True))
    frags.append(text((w_end + ax_x1) // 2, ax_y - zone_h // 2 - 26,
                      "→ reset", size=11, color=POS))

    # ── Межі вікна (вертикальні лінії) ───────────────────────────────────────
    for xv, lbl in [(w_start, "t_min"), (w_end, "t_max")]:
        frags.append(line(xv, zone_y - 8, xv, zone_y + zone_h + 8,
                          color=DGREY, sw=1.5, dash="5,3"))
        frags.append(text(xv, zone_y + zone_h + 22, lbl, size=11,
                          color=DGREY))

    # ── Стрілки-приклади годівлі ─────────────────────────────────────────────
    # Здорова (у вікні)
    good_x = (w_start + w_end) // 2
    frags.append(arrow(good_x, ax_y + zone_h // 2 + 38, good_x, ax_y + zone_h // 2 + 4,
                       color=FIELD))
    frags.append(text(good_x, ax_y + zone_h // 2 + 54,
                      "здорова годівля", size=11, color=FIELD, bold=True))

    # Зарано (у лівій зоні)
    early_x = (ax_x0 + w_start) // 2
    frags.append(arrow(early_x, ax_y + zone_h // 2 + 38, early_x, ax_y + zone_h // 2 + 4,
                       color=POS))
    frags.append(text(early_x, ax_y + zone_h // 2 + 54,
                      "'оскаженілий' код", size=11, color=POS, bold=True))

    # Запізно (у правій зоні) — хрестик
    late_x = (w_end + ax_x1) // 2
    frags.append(text(late_x, ax_y + zone_h // 2 + 20,
                      "×  мовчить", size=13, color=POS, bold=True))
    frags.append(text(late_x, ax_y + zone_h // 2 + 38,
                      "(завис)", size=11, color=MUTED, italic=True))

    # ── Контраст із TWDT (примітка внизу) ────────────────────────────────────
    note = "TWDT ловить лише «запізно»; вікно (зовнішній супервізор) ловить і «зарано»."
    frags.append(text(W // 2, H - 18, note, size=11, color=MUTED, italic=True))

    path = os.path.join(OUT, "fig-24-7c-2-windowed-supervisor.svg")
    render(path, W, H, *frags, title=None)
    print("  OK", path)


# ── Запуск ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating figures for ch24-s7-c-esp32-watchdogs ...")
    fig1_watchdog_echelon()
    fig2_windowed_supervisor()
    print("Done.")
