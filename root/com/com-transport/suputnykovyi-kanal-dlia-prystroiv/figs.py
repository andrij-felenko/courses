# -*- coding: utf-8 -*-
"""Фігури для теми «Супутниковий канал для пристроїв» (com-transport).
Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Порівняння орбітальних угруповань GEO та LEO ────────────────────
def fig_constellations():
    W, H = 820, 460
    parts = []

    # Фон та заголовок
    parts.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=10))

    # Ліва колонка: Геостаціонарна орбіта (GEO)
    parts.append(rect(30, 35, 365, 400, fill="#ffffff", stroke=NEG, sw=1.6, rx=8))
    parts.append(text(212, 60, "Геостаціонарна орбіта (GEO)", 14, NEG, "middle", bold=True))
    parts.append(text(212, 78, "Inmarsat, Thuraya, Viasat", 11, MUTED, "middle"))

    parts.append(fitbox(45, 95, 335, 62,
                        "Висота орбіти: 35 786 км над екватором\n"
                        "Період обертання: 23 год 56 хв (синхронно із Землею)\n"
                        "Видимість: постійна фіксована точка на небосхилі",
                        size=11, fill="#f0f4fd", stroke=NEG, sw=1.0, color=INK))

    parts.append(fitbox(45, 170, 335, 110,
                        "Властивості радіоканалу:\n"
                        "• Велика затримка: RTT = 500…600 мс\n"
                        "• Величезні втрати простору: FSPL ≈ 190…200 дБ (L-діапазон)\n"
                        "• Доплерівський зсув: Δf ≈ 0 Гц (відносна швидкість нульова)\n"
                        "• Сліпа зона: полярні широти (>75° пн./пд. ш.) поза зоною зв'язку",
                        size=10.5, fill="#ffffff", stroke="#d0d7de", sw=1.0, color=INK))

    parts.append(fitbox(45, 292, 335, 130,
                        "Вимоги до абонентського термінала:\n"
                        "• Спрямована антена або громіздкий тарілчастий опромінювач\n"
                        "• Висока випромінювана потужність (EIRP > 15…25 дБВт)\n"
                        "• Високе енергоспоживання (складно живити від батарейок)\n"
                        "• Стаціонарне або морське використання (буї, судна, вишки)",
                        size=10.5, fill="#fff8e1", stroke="#f0b429", sw=1.0, color=INK))

    # Права колонка: Низька навколоземна орбіта (LEO)
    parts.append(rect(425, 35, 365, 400, fill="#ffffff", stroke=FIELD, sw=1.6, rx=8))
    parts.append(text(607, 60, "Низька орбіта (LEO / IoT Nanosats)", 14, FIELD, "middle", bold=True))
    parts.append(text(607, 78, "Iridium, Swarm (SpaceX), Globalstar, Astrocast", 11, MUTED, "middle"))

    parts.append(fitbox(440, 95, 335, 62,
                        "Висота орбіти: 500…1400 км\n"
                        "Швидкість руху: v ≈ 7.5 км/с (період ~90…100 хв)\n"
                        "Видимість супутника: динамічне вікно 5…12 хвилин",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.0, color=INK))

    parts.append(fitbox(440, 170, 335, 110,
                        "Властивості радіоканалу:\n"
                        "• Низька затримка: RTT = 10…40 мс (міжвузловий час)\n"
                        "• Помірні втрати простору: FSPL ≈ 155…165 дБ (L-діапазон)\n"
                        "• Значний доплерівський зсув: Δf до ±38 кГц на 1.6 ГГц\n"
                        "• Повне покриття: полярні орбіти охоплюють 100% поверхні Землі",
                        size=10.5, fill="#ffffff", stroke="#d0d7de", sw=1.0, color=INK))

    parts.append(fitbox(440, 292, 335, 130,
                        "Вимоги до абонентського термінала:\n"
                        "• Компактна всеспрямована керамічна патч-антена (RHCP)\n"
                        "• Передавач 1…2 Вт у коротких імпульсах (Short Burst Data)\n"
                        "• Можливість автономного живлення від первинних літієвих батарей\n"
                        "• Оптимально для трекерів, сенсорів, датчиків дикої природи",
                        size=10.5, fill="#eaf0fd", stroke=NEG, sw=1.0, color=INK))

    render(os.path.join(IMG, "satellite-constellations-leo-geo.svg"), W, H, *parts,
           title="Порівняння супутникових угруповань GEO та LEO для IoT")


# ── Фігура 2: Бюджет радіолінії супутникового зв'язку (Link Budget) ────────────
def fig_link_budget():
    W, H = 820, 420
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=10))
    parts.append(text(W / 2, 36, "Каскадний баланс рівнів сигналу супутникової радіолінії (Uplink LEO 1.6 ГГц)", 13, INK, "middle", bold=True))

    # Стадії водоспаду бюджету потужності
    stages = [
        ("Потужність передавача\n(Tx Power, 1.6 Вт)", "+32.0 дБм", POS, 60, 70, 180, 50),
        ("Підсилення антени IoT\n(Patch Antenna Gain)", "+2.5 дБі", POS, 260, 70, 180, 50),
        ("Еквівалентна потужність\n(EIRP = P_tx + G_tx)", "+34.5 дБм", POS, 460, 70, 180, 50),
        ("Втрати вільного простору\n(FSPL на d = 1000 км)", "-156.6 дБ", NEG, 660, 70, 180, 50),

        ("Втрати в атмосфері та листі\n(L_atm + L_foliage)", "-3.5 дБ", NEG, 660, 190, 180, 50),
        ("Поляризаційні втрати\n(Polarization Mismatch)", "-1.5 дБ", NEG, 460, 190, 180, 50),
        ("Підсилення антени супутника\n(Satellite Rx Gain)", "+6.0 дБі", FIELD, 260, 190, 180, 50),
        ("Рівень сигналу на вході Rx\n(Received Power P_rx)", "-121.1 дБм", FIELD, 60, 190, 180, 50),
    ]

    for title, val, col, x, y, bw, bh in stages:
        parts.append(rect(x - bw / 2, y, bw, bh, fill="#f8fafc", stroke=col, sw=1.4, rx=6))
        parts.append(mtext(x, y + 16, title, size=10, color=INK, bold=False, lh=1.2))
        parts.append(text(x, y + 42, val, 11.5, col, "middle", bold=True))

    # Стрілки переходу між блоками
    parts.append(arrow(150, 95, 170, 95, color=LINE, sw=1.5))
    parts.append(arrow(350, 95, 370, 95, color=LINE, sw=1.5))
    parts.append(arrow(550, 95, 570, 95, color=LINE, sw=1.5))

    # Перехід між рядами
    parts.append(line(660, 120, 660, 155, color=NEG, sw=1.5))
    parts.append(line(660, 155, 660, 190, color=NEG, sw=1.5))
    parts.append(arrow(570, 215, 550, 215, color=LINE, sw=1.5))
    parts.append(arrow(370, 215, 350, 215, color=LINE, sw=1.5))
    parts.append(arrow(170, 215, 150, 215, color=LINE, sw=1.5))

    # Підсумковий блок чутливості та запасу
    parts.append(rect(40, 275, 740, 115, fill="#f0f7ff", stroke=NEG, sw=1.4, rx=8))
    parts.append(text(410, 298, "Аналіз енергетичного запасу радіолінії (Link Margin):", 12, NEG, "middle", bold=True))

    parts.append(fitbox(60, 312, 330, 66,
                        "Тепловий шум приймача (B = 25 кГц, NF = 3 дБ):\n"
                        "P_noise = k · T · B + NF ≈ -127.0 дБм\n"
                        "Поріг демодуляції QPSK (Eb/N0 = 6 дБ): -134.0 дБм",
                        size=10, fill="#ffffff", stroke="#d0d7de", sw=1.0, color=INK))

    parts.append(fitbox(410, 312, 350, 66,
                        "Підсумковий запас каналу (Link Margin):\n"
                        "Margin = P_rx - P_threshold = -121.1 - (-134.0) = +12.9 дБ\n"
                        "Запас гарантує стійкий зв'язок під час дощу та низьких кутів місця (>15°)",
                        size=10, fill="#eafaf1", stroke=FIELD, sw=1.2, color=INK))

    render(os.path.join(IMG, "link-budget-breakdown.svg"), W, H, *parts,
           title="Бюджет радіолінії супутникового каналу зв'язку")


# ── Фігура 3: Послідовність сесії Iridium Short Burst Data (SBD) ───────────────
def fig_sbd_flow():
    W, H = 820, 460
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=10))
    parts.append(text(W / 2, 34, "Послідовність сесії обміну даними Iridium Short Burst Data (SBD)", 13, INK, "middle", bold=True))

    # Лінії учасників (Lifelines)
    lifelines = [
        ("Мікроконтролер\n(MCU / DTE)", 100),
        ("Супутниковий модем\n(Iridium 9603N / DCE)", 290),
        ("Супутник LEO\n(Iridium NEXT)", 490),
        ("Шлюз мережі\n(Iridium Gateway / NOC)", 700),
    ]

    y_top = 80
    y_bot = 420

    for name, x in lifelines:
        parts.append(rect(x - 70, y_top - 30, 140, 38, fill="#eef2f7", stroke=INK, sw=1.3, rx=5))
        parts.append(mtext(x, y_top - 20, name, size=10, color=INK, bold=True, lh=1.2))
        parts.append(line(x, y_top + 8, x, y_bot, color="#cbd5e1", sw=1.4, dash="4,4"))

    # Повідомлення
    steps = [
        (100, 290, 110, "AT+SBDWB=42 (запис 42 байтів)", POS),
        (290, 100, 135, "READY\\r\\n", MUTED),
        (100, 290, 160, "[2 байти довжини] + [42 байти даних] + [2 байти CRC]", POS),
        (290, 100, 185, "0\\r\\n (OK: буфер завантажено)", FIELD),

        (100, 290, 220, "AT+SBDIX (ініціація сесії в ефір)", NEG),
        (290, 490, 250, "Burst Handshake & SBD Message (L-band TDMA)", NEG),
        (490, 700, 280, "Inter-Satellite Link (Ka-band) → Downlink до шлюзу", NEG),

        (700, 490, 315, "Gateway ACK + Вхідний MT-пакет (якщо є)", FIELD),
        (490, 290, 345, "Супутник повертає підтвердження модему", FIELD),
        (290, 100, 375, "+SBDIX: 0, 321, 1, 14, 28, 0 (MO успіх, MT прийнято)", FIELD),

        (100, 290, 400, "AT+SBDRB (вичитування 28 байтів MT з буфера)", POS),
    ]

    for x1, x2, y, msg, col in steps:
        parts.append(arrow(x1, y, x2, y, color=col, sw=1.6))
        mx = (x1 + x2) / 2
        parts.append(text(mx, y - 5, msg, 9.5, col, "middle", bold=True))

    render(os.path.join(IMG, "iridium-sbd-session-flow.svg"), W, H, *parts,
           title="Діаграма послідовності сесії Iridium SBD")


# ── Фігура 4: Антена RHCP та схема буферизації живлення трансивера ─────────────
def fig_antenna_power():
    W, H = 820, 430
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=10))

    # Ліва половина: Патч-антена кругової поляризації
    parts.append(rect(25, 30, 370, 380, fill="#fafbfc", stroke="#cbd5e1", sw=1.2, rx=8))
    parts.append(text(210, 52, "Керамічна патч-антена RHCP (1621 МГц)", 12.5, INK, "middle", bold=True))

    # Рисунок патча
    parts.append(rect(80, 75, 260, 150, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    parts.append(text(210, 92, "Плата заземлення (Ground Plane ≥ 50 × 50 мм)", 10, MUTED, "middle"))

    # Керамічний елемент
    parts.append(rect(130, 105, 160, 100, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=3))
    parts.append(text(210, 140, "Кераміка ε_r ≈ 36", 11, "#b45309", "middle", bold=True))
    parts.append(text(210, 158, "25 × 25 × 4 мм", 10, "#b45309", "middle"))

    # Точка живлення (Offset Feed Pin)
    parts.append(circle(185, 175, 5, fill=POS, stroke=INK, sw=1.2))
    parts.append(line(185, 175, 150, 195, color=POS, sw=1.2))
    parts.append(text(145, 208, "Зміщена точка запитки (RHCP)", 9.5, POS, "middle", bold=True))

    # Зрізані кути для кругової поляризації
    parts.append(line(130, 118, 143, 105, color="#d97706", sw=2.0))
    parts.append(line(277, 205, 290, 192, color="#d97706", sw=2.0))
    parts.append(text(275, 120, "зрізи кутів\n(зсув фази 90°)", 9.5, MUTED, "middle"))

    parts.append(fitbox(40, 240, 340, 155,
                        "Вимоги до антени супутникового вузла:\n"
                        "• Права кругова поляризація (RHCP, Axial Ratio < 3 дБ)\n"
                        "• Екранує втрати від обертання площини Фарадея в іоносфері\n"
                        "• Чистий горизонт (Sky View) без металевих перешкод\n"
                        "• Розмір екранної площини задає резонансну частоту та КСХ",
                        size=10, fill="#ffffff", stroke="#d0d7de", sw=1.0, color=INK))

    # Права половина: Схема живлення з буферизацією суперконденсатором
    parts.append(rect(425, 30, 370, 380, fill="#fafbfc", stroke="#cbd5e1", sw=1.2, rx=8))
    parts.append(text(610, 52, "Буферизація імпульсного струму (до 2 А)", 12.5, INK, "middle", bold=True))

    # Батарея
    parts.append(rect(440, 80, 80, 50, fill="#ffffff", stroke=INK, sw=1.4, rx=4))
    parts.append(text(480, 100, "Батарея", 10, INK, "middle", bold=True))
    parts.append(text(480, 118, "Li-SOCl2 (3.6В)", 9.5, MUTED, "middle"))

    # Обмежувач струму / Soft-start
    parts.append(rect(540, 80, 95, 50, fill="#fff8e1", stroke="#f0b429", sw=1.4, rx=4))
    parts.append(text(587, 100, "Soft-Start / LDO", 9.5, INK, "middle", bold=True))
    parts.append(text(587, 118, "I_max ≤ 150 мА", 9.5, POS, "middle"))

    # Суперконденсатор
    parts.append(rect(655, 80, 125, 50, fill="#eafaf1", stroke=FIELD, sw=1.4, rx=4))
    parts.append(text(717, 100, "Суперконденсатор", 9.5, FIELD, "middle", bold=True))
    parts.append(text(717, 118, "0.22…0.5 Ф (ESR < 50 мОм)", 9.5, INK, "middle"))

    # З'єднувальні стрілки живлення
    parts.append(arrow(520, 105, 540, 105, color=LINE, sw=1.5))
    parts.append(arrow(635, 105, 655, 105, color=LINE, sw=1.5))

    # Імпульсна шина до трансивера
    parts.append(line(717, 130, 717, 165, color=POS, sw=2.0))
    parts.append(arrow(717, 165, 717, 185, color=POS, sw=2.0))
    parts.append(text(745, 160, "Піковий імпульс\n1.5…2.0 А (8.3 мс)", 9.5, POS, "start", bold=True))

    # Супутниковий модуль
    parts.append(rect(480, 185, 270, 45, fill="#fee2e2", stroke=POS, sw=1.6, rx=6))
    parts.append(text(615, 205, "Підсилювач потужності (PA Transceiver)", 11, POS, "middle", bold=True))
    parts.append(text(615, 220, "Iridium 9603N / Swarm M138", 9.5, INK, "middle"))

    parts.append(fitbox(440, 245, 340, 150,
                        "Фізична проблема просідання напруги (Brownout):\n"
                        "• Первинні батареї мають високий внутрішній опір (ESR > 5…15 Ом)\n"
                        "• Стрибок струму 2 А викликає падіння ΔU = I · R_esr > 10 В (колапс!)\n"
                        "• Суперконденсатор накопичує енергію E = 0.5 · C · (U1² - U2²)\n"
                        "• Soft-start обмежує струм заряду, запобігаючи скиданню мікроконтролера",
                        size=10, fill="#ffffff", stroke="#d0d7de", sw=1.0, color=INK))

    render(os.path.join(IMG, "satellite-patch-antenna-matching.svg"), W, H, *parts,
           title="Конструкція антени RHCP та схема буферизації живлення")


fig_constellations()
fig_link_budget()
fig_sbd_flow()
fig_antenna_power()
print("Done. SVG in", IMG)
