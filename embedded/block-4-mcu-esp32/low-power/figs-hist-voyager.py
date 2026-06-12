# -*- coding: utf-8 -*-
"""
Фігури для 📜 r13-s2-history-voyager.md
  fig-r13-2i-1-rtg            — Рис. 4.13.2i.1 (схема RTG)
  fig-r13-2i-2-two-leaks      — Рис. 4.13.2i.2 (дві діри + аналог чипа)
  fig-r13-2i-3-budget-timeline — Рис. 4.13.2i.3 (таймлайн бюджету)

Запуск: python figs-r13-s2-history-voyager.py
Вивід → ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.13.2i.1 — Схема RTG: як гаряча грудка плутонію робить струм
# ─────────────────────────────────────────────────────────────────────────────
def fig1_rtg():
    W, H = 820, 440
    frags = []

    C_HOT    = "#c0392b"   # гарячий бік
    C_COLD   = "#2457d6"   # холодний бік / радіатор
    C_THERMO = "#27ae60"   # термопари
    C_FUEL   = "#8B4513"   # пальне / плутоній
    C_ARROW  = "#555555"   # потік тепла
    C_LOSS   = "#e67e22"   # джерела втрат

    CX = W // 2  # центр горизонтальний

    # ── Заголовок ──
    frags.append(text(CX, 28, "RTG: як гаряча грудка плутонію-238 робить струм", size=16, bold=True))

    # ── Ядро: грудка плутонію (кола) ──
    FUEL_CX = 160
    FUEL_CY = 220
    FUEL_R  = 52
    frags.append(circle(FUEL_CX, FUEL_CY, FUEL_R, fill="#fef3e2", stroke=C_FUEL, sw=3))
    frags.append(circle(FUEL_CX, FUEL_CY, FUEL_R * 0.55, fill="#f9a825", stroke=C_FUEL, sw=1.5))
    tb, _, _ = textbox(FUEL_CX, FUEL_CY,
                       "²³⁸Pu\n(пальне)", size=12, fill="#fef3e2", stroke=C_FUEL,
                       pad=5, color=C_FUEL, bold=True, min_w=60)
    frags.append(tb)
    frags.append(text(FUEL_CX, FUEL_CY + FUEL_R + 16, "радіоактивний розпад\n→ постійне тепло",
                      size=10, color=MUTED, anchor="middle"))

    # ── Стрілка тепла з плутонію → гарячий бік ──
    HOT_X = 250
    frags.append(arrow(FUEL_CX + FUEL_R + 4, FUEL_CY, HOT_X - 4, FUEL_CY, color=C_HOT, sw=2.5))
    frags.append(text((FUEL_CX + FUEL_R + HOT_X) // 2, FUEL_CY - 12,
                      "Q (тепловий потік)", size=10, color=C_HOT, anchor="middle"))

    # ── Гарячий бік ──
    HOT_W = 40
    HOT_H = 150
    HOT_Y = FUEL_CY - HOT_H // 2
    frags.append(rect(HOT_X, HOT_Y, HOT_W, HOT_H, fill="#fdecea", stroke=C_HOT, sw=2.5, rx=4))
    tb, _, _ = textbox(HOT_X + HOT_W // 2, FUEL_CY,
                       "гарячий\nбік\nT_h", size=11, fill="#fdecea", stroke=C_HOT,
                       pad=4, color=C_HOT, bold=True, min_w=52)
    frags.append(tb)

    # ── Стовпчик термопар ──
    THERMO_X = HOT_X + HOT_W
    THERMO_W = 140
    THERMO_H = HOT_H
    THERMO_Y = HOT_Y
    # Фон стовпчика
    frags.append(rect(THERMO_X, THERMO_Y, THERMO_W, THERMO_H,
                      fill="#f0fdf4", stroke=C_THERMO, sw=2, rx=3))
    # Символічні «зубці» термопар
    N_TEETH = 6
    step_h = THERMO_H / N_TEETH
    for i in range(N_TEETH):
        ty = THERMO_Y + i * step_h
        # чергуємо напрямок зубця
        if i % 2 == 0:
            frags.append(line(THERMO_X + 10, ty + step_h * 0.1,
                              THERMO_X + THERMO_W - 10, ty + step_h * 0.5,
                              color=C_THERMO, sw=1.5))
        else:
            frags.append(line(THERMO_X + THERMO_W - 10, ty + step_h * 0.1,
                              THERMO_X + 10, ty + step_h * 0.5,
                              color=C_THERMO, sw=1.5))
    tb, _, _ = textbox(THERMO_X + THERMO_W // 2, FUEL_CY,
                       "SiGe\nтермопари\n(ефект\nЗеебека)", size=11,
                       fill="#f0fdf4", stroke=C_THERMO, pad=5,
                       color=C_THERMO, bold=True, min_w=80)
    frags.append(tb)

    # ── Холодний бік ──
    COLD_X = THERMO_X + THERMO_W
    COLD_W = 40
    COLD_H = HOT_H
    COLD_Y = HOT_Y
    frags.append(rect(COLD_X, COLD_Y, COLD_W, COLD_H, fill="#eaf0fd", stroke=C_COLD, sw=2.5, rx=4))
    tb, _, _ = textbox(COLD_X + COLD_W // 2, FUEL_CY,
                       "холодний\nбік\nT_c", size=11, fill="#eaf0fd", stroke=C_COLD,
                       pad=4, color=C_COLD, bold=True, min_w=52)
    frags.append(tb)

    # ── Радіатор → космос ──
    RAD_X = COLD_X + COLD_W
    RAD_W = 80
    RAD_H = HOT_H
    RAD_Y = HOT_Y
    # Хвилясті «ребра» радіатора
    frags.append(rect(RAD_X, RAD_Y, RAD_W, RAD_H, fill="#e8eaf6", stroke=C_COLD, sw=1.5, rx=3))
    N_FINS = 5
    fin_step = RAD_H / N_FINS
    for i in range(N_FINS):
        fy = RAD_Y + i * fin_step
        frags.append(line(RAD_X + 6, fy + 4, RAD_X + RAD_W - 6, fy + 4, color=C_COLD, sw=1.2))
    frags.append(text(RAD_X + RAD_W // 2, FUEL_CY - 8, "радіатор", size=11, color=C_COLD, anchor="middle"))
    frags.append(text(RAD_X + RAD_W // 2, FUEL_CY + 10, "→ космос", size=10, color=MUTED, anchor="middle"))

    # ── Стрілка тепла від холодного боку у космос ──
    frags.append(arrow(RAD_X + RAD_W, FUEL_CY, RAD_X + RAD_W + 35, FUEL_CY, color=C_COLD, sw=2))
    frags.append(text(RAD_X + RAD_W + 20, FUEL_CY - 14, "Q_cold", size=10, color=C_COLD, anchor="middle"))

    # ── Клеми +/− ──
    TERM_X = THERMO_X + THERMO_W // 2
    frags.append(plus(TERM_X, THERMO_Y - 26))
    frags.append(minus(TERM_X, THERMO_Y + THERMO_H + 26))
    # Дроти до клем
    frags.append(line(TERM_X, THERMO_Y - 5, TERM_X, THERMO_Y - 17, color=INK, sw=1.5))
    frags.append(line(TERM_X, THERMO_Y + THERMO_H + 5, TERM_X, THERMO_Y + THERMO_H + 17, color=INK, sw=1.5))

    # ── Напруга U ──
    U_X = TERM_X + 55
    frags.append(line(U_X, THERMO_Y - 26, U_X, THERMO_Y + THERMO_H + 26, color=INK, sw=1.2, dash="5,4"))
    tb, _, _ = textbox(U_X + 28, FUEL_CY, "U\n(напруга\nЗеебека)", size=11,
                       fill=FILL, stroke=LINE, pad=5, color=INK, min_w=68)
    frags.append(tb)

    # ── Два джерела майбутніх втрат (помічені знаком ⚠) ──
    # 1) Менше тепла від розпаду
    LOSS1_X = FUEL_CX
    LOSS1_Y = HOT_Y - 58
    tb, _, _ = textbox(LOSS1_X, LOSS1_Y,
                       "⚠ Втрата 1:\n²³⁸Pu розпадається\n(−0.79%/рік теплової потужності)",
                       size=10, fill="#fff8e1", stroke=C_LOSS, pad=6, color=C_LOSS, min_w=200)
    frags.append(tb)
    frags.append(line(FUEL_CX, HOT_Y - 30, FUEL_CX, FUEL_CY - FUEL_R - 2, color=C_LOSS, sw=1.2, dash="4,3"))

    # 2) Деградація термопар
    LOSS2_X = THERMO_X + THERMO_W // 2
    LOSS2_Y = THERMO_Y + THERMO_H + 68
    tb, _, _ = textbox(LOSS2_X, LOSS2_Y,
                       "⚠ Втрата 2:\nтермопари старіють\n(ефективність спадає)",
                       size=10, fill="#fff8e1", stroke=C_LOSS, pad=6, color=C_LOSS, min_w=190)
    frags.append(tb)
    frags.append(line(LOSS2_X, LOSS2_Y - 24, LOSS2_X, THERMO_Y + THERMO_H + 2,
                      color=C_LOSS, sw=1.2, dash="4,3"))

    # ── Підпис знизу ──
    note = "Напруга з'являється з різниці T_h − T_c. Обидва майбутні джерела згасання — тут."
    tb, _, _ = textbox(CX, H - 20, note, size=11, fill="#fafafa", stroke=MUTED, pad=7, min_w=520)
    frags.append(tb)

    render(os.path.join(OUT, "fig-r13-2i-1-rtg.svg"), W, H, *frags, title=None)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.13.2i.2 — Дві діри в бюджеті та аналог на карті споживання чипа
# ─────────────────────────────────────────────────────────────────────────────
def fig2_two_leaks():
    W, H = 860, 440
    frags = []

    C_FUEL  = "#c0392b"   # розпад пального
    C_THERMO = "#e67e22"  # деградація термопар
    C_ELEC  = "#27ae60"   # вихідна електрика
    C_CHIP  = "#2457d6"   # корисне споживання чипа
    C_LEAK  = "#8e44ad"   # витоки / тіньове споживання

    # ── Ліва частина: бак із двома кранами ──
    # Бак
    BK_X, BK_Y, BK_W, BK_H = 60, 80, 160, 220
    frags.append(rect(BK_X, BK_Y, BK_W, BK_H, fill="#fef9ec", stroke="#c0392b", sw=2.5, rx=8))
    tb, _, _ = textbox(BK_X + BK_W // 2, BK_Y + 42,
                       "теплова\nпотужність\n(RTG)", size=12,
                       fill="#fef9ec", stroke=C_FUEL, pad=5, color=C_FUEL, bold=True, min_w=110)
    frags.append(tb)

    # Рівень рідини (заливка)
    LEVEL_H = int(BK_H * 0.7)
    LEVEL_Y = BK_Y + BK_H - LEVEL_H
    frags.append(rect(BK_X + 3, LEVEL_Y, BK_W - 6, LEVEL_H,
                      fill="#fcf3cf", stroke="none", sw=0, rx=4))
    frags.append(text(BK_X + BK_W // 2, LEVEL_Y + LEVEL_H // 2 + 5,
                      "Q_rtg", size=20, color="#e67e22", anchor="middle", bold=True))

    # ── Кран 1: розпад пального (вузький, ліворуч) ──
    CR1_X = BK_X + 25
    CR1_Y_TOP = BK_Y + BK_H
    CR1_W = 18
    CR1_H = 60
    frags.append(rect(CR1_X, CR1_Y_TOP, CR1_W, CR1_H, fill="#fdecea", stroke=C_FUEL, sw=2, rx=3))
    frags.append(text(CR1_X + CR1_W // 2, CR1_Y_TOP + CR1_H + 16,
                      "розпад ²³⁸Pu\n−0.79%/рік", size=9, color=C_FUEL, anchor="middle"))
    frags.append(arrow(CR1_X + CR1_W // 2, CR1_Y_TOP + CR1_H + 4,
                       CR1_X + CR1_W // 2, CR1_Y_TOP + CR1_H + 38,
                       color=C_FUEL, sw=1.5))

    # ── Кран 2: деградація термопар (ширший, правіше) ──
    CR2_X = BK_X + 80
    CR2_Y_TOP = BK_Y + BK_H
    CR2_W = 36
    CR2_H = 60
    frags.append(rect(CR2_X, CR2_Y_TOP, CR2_W, CR2_H, fill="#fff3e0", stroke=C_THERMO, sw=2.5, rx=3))
    frags.append(text(CR2_X + CR2_W // 2, CR2_Y_TOP + CR2_H + 16,
                      "деградація\nтермопар\n(БІЛЬША втрата!)", size=9, color=C_THERMO, anchor="middle"))
    frags.append(arrow(CR2_X + CR2_W // 2, CR2_Y_TOP + CR2_H + 4,
                       CR2_X + CR2_W // 2, CR2_Y_TOP + CR2_H + 46,
                       color=C_THERMO, sw=2))

    # ── Стрілка вихідної електрики вправо ──
    OUT_Y = BK_Y + 100
    frags.append(arrow(BK_X + BK_W + 4, OUT_Y, BK_X + BK_W + 60, OUT_Y, color=C_ELEC, sw=3))
    tb, _, _ = textbox(BK_X + BK_W + 90, OUT_Y,
                       "вихідна\nелектрика\n~470 Вт (1977)\n→ ~225 Вт (2025)",
                       size=11, fill="#f0fdf4", stroke=C_ELEC, pad=6, color=C_ELEC,
                       bold=True, min_w=130)
    frags.append(tb)

    # ── Вертикальний роздільник ──
    DIV_X = W // 2 + 10
    frags.append(line(DIV_X, 50, DIV_X, H - 50, color=MUTED, sw=1.2, dash="6,5"))
    frags.append(text(DIV_X, 40, "аналог", size=12, color=MUTED, anchor="middle", italic=True))

    # ── Права частина: міні-карта споживання чипа ──
    CHIP_CX = DIV_X + (W - DIV_X) // 2
    CHIP_TOP = 75

    # Корпус чипа
    CHIP_W, CHIP_H = 190, 170
    CHIP_X = CHIP_CX - CHIP_W // 2
    CHIP_Y = CHIP_TOP
    frags.append(rect(CHIP_X, CHIP_Y, CHIP_W, CHIP_H, fill="#f8f9fa", stroke=INK, sw=2, rx=6))
    frags.append(text(CHIP_CX, CHIP_Y + 18, "ESP32 чип", size=12, bold=True, anchor="middle"))

    # Ядро + радіо (корисне)
    frags.append(fitbox(CHIP_X + 10, CHIP_Y + 30, 80, 44,
                        "ядро\n+радіо",
                        size=11, fill="#e8f5e9", stroke=C_CHIP, sw=1.5, color=C_CHIP))
    frags.append(arrow(CHIP_X + 50, CHIP_Y + 74, CHIP_X + 50, CHIP_Y + 96, color=C_CHIP, sw=1.8))
    frags.append(text(CHIP_X + 50, CHIP_Y + 110,
                      "корисне\n(«замовлене»)", size=9, color=C_CHIP, anchor="middle"))

    # Витоки + Iq (тіньове)
    frags.append(fitbox(CHIP_X + 100, CHIP_Y + 30, 80, 44,
                        "витоки\n+ Iq LDO",
                        size=11, fill="#f3e5f5", stroke=C_LEAK, sw=1.5, color=C_LEAK))
    frags.append(arrow(CHIP_X + 140, CHIP_Y + 74, CHIP_X + 140, CHIP_Y + 96, color=C_LEAK, sw=2))
    frags.append(text(CHIP_X + 140, CHIP_Y + 110,
                      "тіньове\n(«незамовлене»)", size=9, color=C_LEAK, anchor="middle"))

    # Стрілки струму з чипа
    CURR_Y = CHIP_Y + CHIP_H
    frags.append(arrow(CHIP_CX, CURR_Y, CHIP_CX, CURR_Y + 36, color=INK, sw=2))
    frags.append(text(CHIP_CX, CURR_Y + 52, "I_total", size=11, bold=True, anchor="middle"))

    # ── Ярлики для стрілки відповідності ──
    tb, _, _ = textbox(DIV_X - 4, 200,
                       "розпад ←→ очевидне\nтермопари ←→ витоки",
                       size=10, fill="#fffde7", stroke="#f9a825", pad=6, color="#7d6608", min_w=190)
    frags.append(tb)

    # ── Висновок ──
    note = "Головна втрата — не там, де «витрачають», а де «втрачають»: термопари ↔ витоки транзисторів"
    tb, _, _ = textbox(W // 2, H - 22, note, size=11, fill="#f9fafb", stroke=MUTED, pad=7, min_w=540)
    frags.append(tb)

    # ── Заголовки частин ──
    frags.append(text(BK_X + BK_W // 2, 58, "RTG: бюджет «Вояджера»", size=13, bold=True, anchor="middle"))
    frags.append(text(CHIP_CX, 58, "Карта споживання чипа", size=13, bold=True, anchor="middle"))

    render(os.path.join(OUT, "fig-r13-2i-2-two-leaks.svg"), W, H, *frags, title=None)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.13.2i.3 — Таймлайн бюджету: спадна крива + сходинки вимикань
# ─────────────────────────────────────────────────────────────────────────────
def fig3_budget_timeline():
    W, H = 880, 460
    frags = []

    C_CURVE  = "#c0392b"   # крива потужності
    C_FLOOR  = "#2457d6"   # пунктир «дна»
    C_EVENT  = "#27ae60"   # сходинки-події
    C_AXIS   = "#6b7280"   # осі

    # ── Область графіка ──
    GX0, GX1 = 90, 830    # x-діапазон
    GY0, GY1 = 50, 340    # y-діапазон (y0=верх=більше ват)
    GW = GX1 - GX0
    GH = GY1 - GY0

    YEAR_MIN, YEAR_MAX = 1977, 2030
    WATT_MIN, WATT_MAX = 0, 490

    def gx(year):
        return GX0 + (year - YEAR_MIN) / (YEAR_MAX - YEAR_MIN) * GW

    def gy(watt):
        return GY1 - (watt - WATT_MIN) / (WATT_MAX - WATT_MIN) * GH

    # ── Вісь X ──
    frags.append(arrow(GX0, GY1, GX1 + 10, GY1, color=C_AXIS, sw=1.5))
    for yr in [1977, 1985, 1995, 2005, 2015, 2025]:
        x = gx(yr)
        frags.append(line(x, GY1 - 5, x, GY1 + 5, color=C_AXIS, sw=1))
        frags.append(text(x, GY1 + 18, str(yr), size=10, color=C_AXIS))
    frags.append(text((GX0 + GX1) // 2, GY1 + 34, "рік", size=11, color=C_AXIS))

    # ── Вісь Y ──
    frags.append(arrow(GX0, GY1 + 5, GX0, GY0 - 15, color=C_AXIS, sw=1.5))
    for watt in [0, 100, 200, 300, 400]:
        y = gy(watt)
        frags.append(line(GX0 - 5, y, GX0 + 5, y, color=C_AXIS, sw=1))
        frags.append(text(GX0 - 22, y + 4, str(watt), size=10, color=C_AXIS, anchor="middle"))
    frags.append(text(GX0 - 52, (GY0 + GY1) // 2, "Вт", size=11, color=C_AXIS, anchor="middle"))

    # ── Пунктир «дна»: передавач + мінімум обігріву ──
    FLOOR_WATT = 50
    FY = gy(FLOOR_WATT)
    frags.append(line(GX0, FY, GX1, FY, color=C_FLOOR, sw=1.5, dash="8,5"))
    tb, _, _ = textbox(GX0 + 130, FY - 18,
                       "«дно»: передавач + критичний обігрів",
                       size=10, fill="#eaf0fd", stroke=C_FLOOR, pad=5, color=C_FLOOR, min_w=220)
    frags.append(tb)

    # ── Спадна крива (ламана лінія через ключові точки) ──
    # Точки (рік, вати) за оцінками (~470 Вт 1977, ~4 Вт/рік, нелінійна деградація)
    curve_pts = [
        (1977, 470), (1982, 447), (1990, 415), (1995, 393),
        (2000, 368), (2005, 342), (2010, 315), (2015, 286),
        (2020, 258), (2025, 232), (2026, 228)
    ]
    for i in range(len(curve_pts) - 1):
        x1, y1 = gx(curve_pts[i][0]), gy(curve_pts[i][1])
        x2, y2 = gx(curve_pts[i + 1][0]), gy(curve_pts[i + 1][1])
        frags.append(line(x1, y1, x2, y2, color=C_CURVE, sw=2.5))

    # ── Позначка старту ──
    frags.append(circle(gx(1977), gy(470), 5, fill=C_CURVE, stroke=C_CURVE))
    tb, _, _ = textbox(gx(1977) + 40, gy(470) - 16,
                       "1977: старт ~470 Вт", size=10,
                       fill="#fdecea", stroke=C_CURVE, pad=4, color=C_CURVE, min_w=140)
    frags.append(tb)

    # ── Позначка 2025 ──
    frags.append(circle(gx(2025), gy(232), 5, fill=C_CURVE, stroke=C_CURVE))
    tb, _, _ = textbox(gx(2025) - 10, gy(232) - 22,
                       "~232 Вт (2025)", size=10,
                       fill="#fdecea", stroke=C_CURVE, pad=4, color=C_CURVE, min_w=120)
    frags.append(tb)

    # ── Сходинки-події (дискретні вимикання) ──
    events = [
        (1997, 280, "вимкнено нагрівачі\n(прилади – нижче −79 °C)"),
        (2025.2, 242, "−CRS\n2025-02-25"),
        (2025.4, 238, "−LECP\n2025-03-24"),
        (2026.3, 228, "−прилад\n2026-04-17"),
    ]

    LABEL_DIR = [1, -1, 1, -1]  # напрямок підпису (1=вправо/вниз, -1=вліво/вгору)
    for idx, (yr, wt, label) in enumerate(events):
        ex, ey = gx(yr), gy(wt)
        frags.append(circle(ex, ey, 6, fill=C_EVENT, stroke=C_EVENT))
        lx = ex + (50 if LABEL_DIR[idx] > 0 else -50)
        ly = ey + (40 if LABEL_DIR[idx] > 0 else -40)
        tb, tw, th = textbox(lx, ly, label, size=9,
                             fill="#f0fdf4", stroke=C_EVENT, pad=5, color=C_EVENT, min_w=90)
        frags.append(tb)
        frags.append(line(ex, ey, lx, ly - th // 2 if LABEL_DIR[idx] < 0 else ly - th // 2,
                          color=C_EVENT, sw=1, dash="3,3"))

    # ── Заголовок ──
    frags.append(text(W // 2, 28, "Бюджет «Вояджерів»: плавне згасання та дискретні вимикання",
                      size=15, bold=True))

    # ── Підпис знизу ──
    note = "Крива тане безперервно; сходинки — навмисні скидання споживачів. Так інженери женуться за лінією, що падає."
    tb, _, _ = textbox(W // 2, H - 24, note, size=11, fill="#f9fafb", stroke=MUTED, pad=7, min_w=580)
    frags.append(tb)

    render(os.path.join(OUT, "fig-r13-2i-3-budget-timeline.svg"), W, H, *frags, title=None)


if __name__ == "__main__":
    fig1_rtg()
    print("  fig-r13-2i-1-rtg.svg — OK")
    fig2_two_leaks()
    print("  fig-r13-2i-2-two-leaks.svg — OK")
    fig3_budget_timeline()
    print("  fig-r13-2i-3-budget-timeline.svg — OK")
    print("Усі 3 фігури записано в", OUT)
