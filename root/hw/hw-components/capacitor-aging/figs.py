# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. mlcc-aging-log-domains: доменна релаксація BaTiO3 та логарифмічний спад ──
def fig_mlcc_aging():
    W, H = 760, 440
    p = []

    # Ліва панель: Доменна динаміка та де-ейджинг
    p.append(rect(15, 15, 345, 410, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(187, 38, "Сегнетоелектричні домени BaTiO₃", size=13, color=INK, bold=True))
    p.append(text(187, 54, "Орієнтація доменних стінок та пінінг дефектами", size=10, color=MUTED))

    # Стан 1: Одразу після охолодження (t = 0+)
    p.append(rect(25, 72, 155, 120, fill="#edf2f7", stroke="#4a5568", sw=1.2, rx=4))
    p.append(text(102, 90, "Свіжий (після пайки)", size=10.5, color=POS, bold=True))
    p.append(text(102, 105, "t = 1 год (нестійкий)", size=9.5, color=MUTED))
    # Домени з вільними стінками
    p.append(line(32, 140, 172, 140, color="#cbd5e0", sw=1, dash="3,3"))
    p.append(line(102, 115, 102, 170, color="#cbd5e0", sw=1, dash="3,3"))
    p.append(arrow(45, 130, 75, 130, color=POS, sw=1.5))
    p.append(arrow(85, 155, 55, 155, color=NEG, sw=1.5))
    p.append(arrow(115, 130, 155, 130, color=POS, sw=1.5))
    p.append(arrow(155, 155, 115, 155, color=NEG, sw=1.5))
    p.append(text(102, 182, "Рухливі стінки → C_max", size=9, color=INK))

    # Стан 2: Зістарений стан (t = 10 000+ год)
    p.append(rect(190, 72, 160, 120, fill="#edf2f7", stroke="#4a5568", sw=1.2, rx=4))
    p.append(text(270, 90, "Зістарений (впорядкований)", size=10.5, color="#2b6cb0", bold=True))
    p.append(text(270, 105, "t = 10 000 год (релаксація)", size=9.5, color=MUTED))
    p.append(line(198, 140, 342, 140, color="#718096", sw=1.5))
    p.append(line(270, 115, 270, 170, color="#718096", sw=1.5))
    # Заблоковані домени + кисневі вакансії V_O
    p.append(arrow(210, 130, 255, 130, color="#718096", sw=1.2))
    p.append(arrow(330, 155, 285, 155, color="#718096", sw=1.2))
    p.append(circle(270, 140, 4, fill=POS, stroke=LINE, sw=1))
    p.append(circle(235, 140, 3, fill=POS, stroke=LINE, sw=0.8))
    p.append(text(270, 182, "Пінінг вакансіями V_O¨ → спад C", size=9, color=INK))

    # Де-ейджинг стрілка
    p.append(arrow(260, 204, 115, 204, color=FIELD, sw=2))
    p.append(text(187, 222, "Де-ейджинг: Нагрів T > 150 °C (1 год)", size=10, color=FIELD, bold=True))
    p.append(text(187, 238, "Перехід у параелектричну кубічну фазу скидає годинник", size=9, color=MUTED))

    # Формула старіння
    p.append(rect(25, 255, 325, 160, fill="#ffffff", stroke="#cbd5e0", sw=1, rx=6))
    p.append(text(187, 276, "Логарифмічний закон старіння MLCC", size=11, color=INK, bold=True))
    p.append(text(187, 302, "C(t) = C₀ · ( 1 − k · log₁₀(t / t₀) )", size=12, color=POS, bold=True))
    p.append(text(187, 328, "k — швидкість старіння (% на декаду часу)", size=9.5, color=INK))
    p.append(text(187, 350, "C0G / NP0: k = 0 %/декаду (без старіння)", size=9.5, color=FIELD, bold=True))
    p.append(text(187, 372, "X7R / X5R: k = 1.0 ... 2.5 %/декаду", size=9.5, color="#d69e2e", bold=True))
    p.append(text(187, 394, "Y5V / Z5U: k = 4.0 ... 7.0 %/декаду", size=9.5, color=POS, bold=True))

    # Права панель: Графік старіння по декадах часу
    p.append(rect(375, 15, 370, 410, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(560, 38, "Дрейф ємності за логарифмічною шкалою", size=13, color=INK, bold=True))
    p.append(text(560, 54, "Відлік від 1000 годин (базовий стан EIA-198 = 0 %)", size=10, color=MUTED))

    # Сітка графіка
    gx0, gy0, gw, gh = 425, 80, 300, 275
    p.append(rect(gx0, gy0, gw, gh, fill="#ffffff", stroke="#a0aec0", sw=1.2, rx=4))

    # Горизонтальні лінії (ΔC %)
    y_p10 = gy0 + int(gh * 0.15)
    y_0   = gy0 + int(gh * 0.40)
    y_m10 = gy0 + int(gh * 0.65)
    y_m20 = gy0 + int(gh * 0.90)

    for y, label in [(y_p10, "+10%"), (y_0, "  0%"), (y_m10, "−10%"), (y_m20, "−20%")]:
        p.append(line(gx0, y, gx0 + gw, y, color="#e2e8f0", sw=1))
        p.append(text(gx0 - 15, y + 4, label, size=9.5, color=MUTED, anchor="end"))

    # Базова лінія 0%
    p.append(line(gx0, y_0, gx0 + gw, y_0, color="#a0aec0", sw=1.2, dash="4,4"))

    # Вертикальні декади (1h, 10h, 100h, 1000h, 10k h, 100k h)
    decades = [
        (gx0 + int(gw * 0.05), "1 год", "t₀"),
        (gx0 + int(gw * 0.23), "10 год", "дек. 1"),
        (gx0 + int(gw * 0.41), "100 год", "дек. 2"),
        (gx0 + int(gw * 0.59), "1 тис", "ref"),
        (gx0 + int(gw * 0.77), "10 тис", "1.1 р."),
        (gx0 + int(gw * 0.95), "100 тис", "11.4 р.")
    ]
    for x, top_lbl, bot_lbl in decades:
        p.append(line(x, gy0, x, gy0 + gh, color="#edf2f7", sw=1))
        p.append(text(x, gy0 + gh + 15, top_lbl, size=9, color=INK))
        p.append(text(x, gy0 + gh + 28, bot_lbl, size=9, color=MUTED))

    # Крива C0G / NP0 (горизонтальна пряма на 0%)
    p.append(line(gx0 + int(gw*0.05), y_0, gx0 + int(gw*0.95), y_0, color=FIELD, sw=2.5))
    p.append(text(gx0 + int(gw*0.75), y_0 - 8, "C0G (k=0)", size=9.5, color=FIELD, bold=True))

    # Крива X7R (k ≈ 2 %/декаду, перетин 0% на 1000 год)
    x_coords = [gx0 + int(gw*0.05), gx0 + int(gw*0.23), gx0 + int(gw*0.41), gx0 + int(gw*0.59), gx0 + int(gw*0.77), gx0 + int(gw*0.95)]
    y_x7r = [y_0 - 25, y_0 - 17, y_0 - 8, y_0, y_0 + 8, y_0 + 17]
    for i in range(len(x_coords)-1):
        p.append(line(x_coords[i], y_x7r[i], x_coords[i+1], y_x7r[i+1], color="#d69e2e", sw=2.2))
    p.append(text(gx0 + int(gw*0.75), y_x7r[-1] + 14, "X7R (k=2%)", size=9.5, color="#d69e2e", bold=True))

    # Крива Y5V (k ≈ 6 %/декаду, перетин 0% на 1000 год)
    y_y5v = [y_0 - 72, y_0 - 48, y_0 - 24, y_0, y_0 + 24, y_0 + 48]
    for i in range(len(x_coords)-1):
        p.append(line(x_coords[i], y_y5v[i], x_coords[i+1], y_y5v[i+1], color=POS, sw=2.2))
    p.append(text(gx0 + int(gw*0.75), y_y5v[-1] + 16, "Y5V (k=6%)", size=9.5, color=POS, bold=True))

    # Підпис осі часу
    p.append(text(560, gy0 + gh + 46, "Час після останнього термічного циклу (де-ейджингу / пайки)", size=9.5, color=INK, bold=True))

    render(os.path.join(OUT, "mlcc-aging-log-domains.svg"), W, H, *p, title="Логарифмічне старіння MLCC та доменна релаксація")

# ── 2. electrolytic-dryout-arrhenius: випаровування рідкого електроліту ─────
def fig_electrolytic_aging():
    W, H = 760, 400
    p = []

    # Ліва панель: Анатомія випаровування крізь герметик
    p.append(rect(15, 15, 345, 370, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(187, 38, "Дифузія розчинника електроліту", size=13, color=INK, bold=True))
    p.append(text(187, 54, "Випаровування молекул GBL/EG крізь гумову пробку", size=10, color=MUTED))

    # Корпус електроліта
    cx, cy = 187, 190
    p.append(rect(cx - 60, cy - 100, 120, 160, fill="#edf2f7", stroke="#2d3748", sw=2, rx=6))
    p.append(text(cx, cy - 80, "Алюмінієвий стакан", size=9.5, color=MUTED))

    # Рулон фольги всередині
    p.append(rect(cx - 45, cy - 60, 90, 90, fill="#e2e8f0", stroke="#4a5568", sw=1.2, rx=3))
    p.append(text(cx, cy - 30, "Травлені фольги", size=9.5, color=INK, bold=True))
    p.append(text(cx, cy - 14, "+ папір сепаратора", size=9, color=MUTED))
    p.append(text(cx, cy + 6, "Рідкий електроліт", size=9.5, color="#2b6cb0", bold=True))

    # Гумова пробка ущільнювача (End seal)
    p.append(rect(cx - 55, cy + 35, 110, 22, fill="#4a5568", stroke="#1a202c", sw=1.5, rx=3))
    p.append(text(cx, cy + 50, "Гумова пробка (EPDM/бутил)", size=9, color="#ffffff", bold=True))

    # Виводи
    p.append(line(cx - 25, cy + 57, cx - 25, cy + 95, color="#a0aec0", sw=3))
    p.append(line(cx + 25, cy + 57, cx + 25, cy + 95, color="#a0aec0", sw=3))
    p.append(text(cx - 25, cy + 108, "Анод (+)", size=9, color=POS, bold=True))
    p.append(text(cx + 25, cy + 108, "Катод (−)", size=9, color=NEG, bold=True))

    # Стрілки дифузії розчинника крізь гуму
    for dx in [-40, -15, 15, 40]:
        p.append(arrow(cx + dx, cy + 55, cx + dx, cy + 80, color=POS, sw=1.5))
    p.append(text(cx + 85, cy + 65, "Пермеація", size=9.5, color=POS, bold=True))
    p.append(text(cx + 85, cy + 80, "розчинника", size=9, color=MUTED))

    # Пояснення знизу
    p.append(text(187, 345, "Втрата маси розчинника ∝ exp(−Ea / k_B T)", size=9.5, color=INK, bold=True))
    p.append(text(187, 365, "Зменшення об'єму → ріст ESR у 2–5 разів", size=9.5, color=POS, bold=True))

    # Права панель: Тепловий розгін старіння (Feedback loop)
    p.append(rect(375, 15, 370, 370, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(560, 38, "Тепловий розгін старіння електроліта", size=13, color=INK, bold=True))
    p.append(text(560, 54, "Закон Арреніуса та правило 10 градусів", size=10, color=MUTED))

    # Блоки зворотного зв'язку
    bx, bw = 560, 260
    # Блок 1: Струм пульсацій
    b1_body, _, _ = textbox(bx, 90, "1. Струм пульсацій I_rms у схемі", size=10, fill="#ffffff", stroke="#4a5568", min_w=bw)
    p.append(b1_body)
    p.append(arrow(bx, 110, bx, 130, color=LINE, sw=1.5))

    # Блок 2: Джоулів нагрів серцевини
    b2_body, _, _ = textbox(bx, 150, "2. Нагрів серцевини: P_loss = I_rms² · ESR", size=10, fill="#fed7d7", stroke=POS, min_w=bw, color=POS, bold=True)
    p.append(b2_body)
    p.append(arrow(bx, 170, bx, 190, color=POS, sw=1.5))

    # Блок 3: Прискорене випаровування (+10 °C → ×2)
    b3_body, _, _ = textbox(bx, 210, "3. Арреніус: кожні +10 °C подвоюють випаровування", size=9.5, fill="#fffaf0", stroke="#dd6b20", min_w=bw, color="#c05621", bold=True)
    p.append(b3_body)
    p.append(arrow(bx, 230, bx, 250, color="#dd6b20", sw=1.5))

    # Блок 4: Висихання та стрибок ESR
    b4_body, _, _ = textbox(bx, 270, "4. Висихання розчину → Стрибок ESR вгору", size=10, fill="#feebc8", stroke="#d69e2e", min_w=bw, color="#744210", bold=True)
    p.append(b4_body)

    # Зворотна петля (від блоку 4 назад до блоку 2)
    p.append(line(bx + bw/2, 270, bx + bw/2 + 20, 270, color=POS, sw=2))
    p.append(line(bx + bw/2 + 20, 270, bx + bw/2 + 20, 150, color=POS, sw=2))
    p.append(arrow(bx + bw/2 + 20, 150, bx + bw/2, 150, color=POS, sw=2))
    p.append(text(bx + bw/2 + 25, 210, "+ΔP", size=10, color=POS, bold=True, anchor="start"))

    # Формула ресурсу знизу
    p.append(rect(390, 310, 340, 60, fill="#ffffff", stroke="#cbd5e0", sw=1, rx=4))
    p.append(text(560, 330, "L = L₀ · 2^((T_max − T_core) / 10)", size=12, color=POS, bold=True))
    p.append(text(560, 352, "Ресурс скорочується вдвічі на кожні 10 °C перегріву серцевини", size=9, color=MUTED))

    render(os.path.join(OUT, "electrolytic-dryout-arrhenius.svg"), W, H, *p, title="Випаровування електроліту та термодинаміка Арреніуса")

# ── 3. film-self-healing-corona: самозаліковування та корона в плівкових ────
def fig_film_aging():
    W, H = 760, 420
    p = []

    # Ліва панель: Механізм самозаліковування (Clearing)
    p.append(rect(15, 15, 345, 390, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(187, 38, "Самозаліковування металізованої плівки", size=13, color=INK, bold=True))
    p.append(text(187, 54, "Випаровування шару Al/Zn (20–50 нм) довкола пробою", size=10, color=MUTED))

    # Схема шарів плівкового конденсатора
    cx, cy = 187, 130
    # Верхня металізація (Al)
    p.append(rect(cx - 130, cy - 40, 260, 8, fill="#a0aec0", stroke="#4a5568", sw=1, rx=1))
    p.append(text(cx + 80, cy - 48, "Металізація Al (30 нм)", size=9, color="#4a5568"))

    # Полімерний діелектрик (PP / PET)
    p.append(rect(cx - 130, cy - 32, 260, 35, fill="#edf2f7", stroke="#718096", sw=1.2, rx=2))
    p.append(text(cx - 50, cy - 14, "Поліпропіленова плівка (PP)", size=9.5, color=INK, bold=True))

    # Нижня металізація (Al)
    p.append(rect(cx - 130, cy + 3, 260, 8, fill="#a0aec0", stroke="#4a5568", sw=1, rx=1))

    # Зона мікропробою та випаровування
    p.append(circle(cx, cy - 14, 18, fill="#fff5f5", stroke=POS, sw=1.5))
    p.append(line(cx, cy - 32, cx, cy + 3, color=POS, sw=2))
    # Випарувана зона металізації
    p.append(rect(cx - 18, cy - 41, 36, 10, fill="#ffffff", stroke=POS, sw=1.2))
    p.append(text(cx, cy - 14, "⚡ Пробій", size=9, color=POS, bold=True))
    p.append(text(cx, cy - 48, "Очищена зона", size=9, color=POS, bold=True))

    # Наслідок самозаліковування
    p.append(rect(25, 205, 325, 185, fill="#ffffff", stroke="#cbd5e0", sw=1, rx=6))
    p.append(text(187, 226, "Ціна надійності: Спад активної площі", size=10.5, color=INK, bold=True))
    p.append(text(187, 248, "• Кожен мікропробій випаровує ~0.01–0.1 мм² металізації", size=9, color=MUTED))
    p.append(text(187, 270, "• Коротке замикання ліквідується за < 10 мкс", size=9, color=FIELD, bold=True))
    p.append(text(187, 292, "• Сумарна площа обкладинок безперервно спадає", size=9, color=POS))
    p.append(text(187, 314, "• Ємність C(t) монотонно падає (до −2%...−5% за EoL)", size=9, color=INK, bold=True))
    p.append(text(187, 336, "• Окиснення Al вологою (Al + H₂O → Al(OH)₃) руйнує краї", size=9, color="#c53030"))
    p.append(text(187, 358, "• Руйнування торцевого контакту (schoopage) веде до росту ESR", size=9, color=MUTED))

    # Права панель: Часткові розряди та коронний розряд
    p.append(rect(375, 15, 370, 390, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(560, 38, "Часткові розряди та корона (AC напруга)", size=13, color=INK, bold=True))
    p.append(text(560, 54, "Іонізація мікропустот між витками за високої напруги", size=10, color=MUTED))

    # Схема мікропустоти
    px, py = 560, 130
    p.append(rect(px - 130, py - 40, 260, 18, fill="#e2e8f0", stroke="#4a5568", sw=1.2, rx=2))
    p.append(text(px, py - 28, "Шар полімеру 1", size=9, color=INK))

    # Повітряний мікропроміжок (Void)
    p.append(rect(px - 130, py - 22, 260, 30, fill="#fffaf0", stroke="#dd6b20", sw=1.2))
    p.append(text(px - 50, py - 6, "Мікропустота (каверна)", size=9.5, color="#c05621", bold=True))
    # Іскри коронного розряду праворуч від тексту
    for ix in [px + 45, px + 75, px + 105]:
        p.append(line(ix, py - 20, ix, py + 6, color="#dd6b20", sw=1.5, dash="2,2"))
        p.append(text(ix, py - 6, "⚡", size=9, color="#dd6b20"))

    p.append(rect(px - 130, py + 8, 260, 18, fill="#e2e8f0", stroke="#4a5568", sw=1.2, rx=2))
    p.append(text(px, py + 20, "Шар полімеру 2", size=9, color=INK))

    # Хімічна руйнація газами
    p.append(rect(385, 205, 350, 185, fill="#ffffff", stroke="#cbd5e0", sw=1, rx=6))
    p.append(text(560, 226, "Хімічна деградація полімерних ланцюгів", size=10.5, color=INK, bold=True))
    p.append(text(560, 248, "1. Напруженість E у повітрі: E_void = ε_r · E_diel", size=9, color=INK))
    p.append(text(560, 270, "2. Іонізація повітря перевищує поріг закону Пашена", size=9, color=MUTED))
    p.append(text(560, 292, "3. Генерація озону O₃ та оксидів азоту NO_x", size=9, color=POS, bold=True))
    p.append(text(560, 314, "4. Окиснення поліпропілену → розрив C-C зв'язків", size=9, color=POS))
    p.append(text(560, 336, "5. Карбонізація діелектрика → локальний пробій плівки", size=9, color="#9b2c2c", bold=True))
    p.append(text(560, 358, "Критично для мережевих X/Y конденсаторів та DC-link", size=9, color=MUTED))

    render(os.path.join(OUT, "film-self-healing-corona.svg"), W, H, *p, title="Самозаліковування та коронні розряди у плівкових конденсаторах")

# ── 4. tantalum-field-crystallization: польова кристалізація Ta2O5 ──────────
def fig_tantalum_aging():
    W, H = 760, 400
    p = []

    # Ліва панель: Польова кристалізація аморфного Ta2O5
    p.append(rect(15, 15, 345, 370, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(187, 38, "Польова кристалізація аморфного Ta₂O₅", size=12.5, color=INK, bold=True))
    p.append(text(187, 54, "Ріст кристалітів під напругою та підвищеною температурою", size=9.5, color=MUTED))

    # Схема шарів аморфного та кристалічного діелектрика
    cx, cy = 187, 140
    # Метал танталу (анод)
    p.append(rect(cx - 130, cy - 50, 260, 20, fill="#a0aec0", stroke="#4a5568", sw=1.2, rx=2))
    p.append(text(cx, cy - 37, "Металевий тантал Ta (анодне тіло)", size=9.5, color=INK, bold=True))

    # Шар оксиду Ta2O5
    p.append(rect(cx - 130, cy - 30, 260, 45, fill="#ebf8ff", stroke="#3182ce", sw=1.2, rx=2))
    p.append(text(cx - 55, cy - 10, "Аморфний Ta₂O₅ (ізолятор)", size=9, color="#2b6cb0"))

    # Кристалічний вузол Ta2O5 (дефект росту)
    p.append(rect(cx + 25, cy - 30, 45, 45, fill="#fed7d7", stroke=POS, sw=1.5, rx=2))
    p.append(text(cx + 47, cy - 15, "Кристаліт", size=9, color=POS, bold=True))
    p.append(text(cx + 47, cy - 3, "Ta₂O₅", size=9, color=POS))
    # Провідний канал витоку вздовж межі зерен
    p.append(line(cx + 25, cy - 30, cx + 25, cy + 15, color="#c53030", sw=2, dash="2,2"))
    p.append(line(cx + 70, cy - 30, cx + 70, cy + 15, color="#c53030", sw=2, dash="2,2"))

    # Катодний шар
    p.append(rect(cx - 130, cy + 15, 260, 20, fill="#718096", stroke="#2d3748", sw=1.2, rx=2))
    p.append(text(cx, cy + 28, "Катодний шар (MnO₂ або Полімер)", size=9.5, color="#ffffff", bold=True))

    # Пояснення фізики
    p.append(rect(25, 215, 325, 155, fill="#ffffff", stroke="#cbd5e0", sw=1, rx=6))
    p.append(text(187, 235, "Механізм росту струму витоку (DCL)", size=10.5, color=INK, bold=True))
    p.append(text(187, 256, "• Аморфний Ta₂O₅ термодинамічно метастабільний", size=9, color=MUTED))
    p.append(text(187, 276, "• Поле E > 2 МВ/см викликає міграцію іонів кисню", size=9, color=INK))
    p.append(text(187, 296, "• Кристалічна фаза має вищу густину → мікротріщини", size=9, color=POS))
    p.append(text(187, 316, "• Струм витоку DCL стрімко зростає у 10–100 разів", size=9, color=POS, bold=True))
    p.append(text(187, 338, "• Потребує напругового дератингу до 50% від V_nom", size=9, color=FIELD, bold=True))

    # Права панель: Порівняння відмов MnO2 проти Полімеру
    p.append(rect(375, 15, 370, 370, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(560, 38, "Режими відмови: MnO₂ проти Полімеру", size=13, color=INK, bold=True))
    p.append(text(560, 54, "Самозаліковування та ризик теплового загоряння", size=10, color=MUTED))

    # Блок MnO2
    p.append(rect(385, 75, 350, 135, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    p.append(text(560, 95, "Твердотільний тантал з катодом MnO₂", size=10.5, color=POS, bold=True))
    p.append(text(560, 115, "1. Мікропробій нагріває MnO₂: 2MnO₂ → Mn₂O₃ + O₂", size=9, color=INK))
    p.append(text(560, 134, "2. Mn₂O₃ ізолятор (самозаліковування за малого струму)", size=9, color=FIELD))
    p.append(text(560, 153, "3. За високого струму: вивільнений O₂ окиснює Ta", size=9, color="#9b2c2c", bold=True))
    p.append(text(560, 172, "4. Екзотермічна реакція горіння Ta + O₂ → Пожежа", size=9, color=POS, bold=True))
    p.append(text(560, 191, "Вимога: послідовний опір 1–3 Ом/В або дератинг 50%", size=9, color=MUTED))

    # Блок Полімер
    p.append(rect(385, 220, 350, 150, fill="#f0fff4", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(560, 240, "Полімерний тантал (PEDOT:PSS)", size=10.5, color=FIELD, bold=True))
    p.append(text(560, 260, "1. Провідний полімер не містить зв'язаного кисню", size=9, color=INK))
    p.append(text(560, 279, "2. Нагрів викликає карбонізацію та ізоляцію полімеру", size=9, color=FIELD, bold=True))
    p.append(text(560, 298, "3. Відсутність кисню виключає екзотермічне горіння Ta", size=9, color=INK))
    p.append(text(560, 317, "4. «Доброякісна відмова» (Benign failure): високоомний стан", size=9, color=FIELD, bold=True))
    p.append(text(560, 338, "Допускає дератинг напруги 10–20% (робота на 80–90% V_nom)", size=9, color=MUTED))

    render(os.path.join(OUT, "tantalum-field-crystallization.svg"), W, H, *p, title="Польова кристалізація та надійність танталових конденсаторів")

# ── 5. capacitor-eol-criteria-comparison: підсумкове порівняння EoL ─────────
def fig_eol_comparison():
    W, H = 760, 420
    p = []

    p.append(rect(15, 15, 730, 390, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(380, 40, "Порівняльна матриця механізмів старіння та критеріїв EoL (AEC-Q200)", size=13.5, color=INK, bold=True))
    p.append(text(380, 58, "Фізика деградації, фактори прискорення та граничні параметри бракування", size=10, color=MUTED))

    # Таблиця
    tx0, ty0, tw, th = 25, 75, 710, 315
    p.append(rect(tx0, ty0, tw, th, fill="#ffffff", stroke="#a0aec0", sw=1.2, rx=4))

    # Заголовок таблиці
    p.append(rect(tx0, ty0, tw, 32, fill="#edf2f7", stroke="#a0aec0", sw=1, rx=2))
    cols = [
        (tx0 + 65, "Тип діелектрика"),
        (tx0 + 205, "Головний механізм старіння"),
        (tx0 + 355, "Фактори прискорення"),
        (tx0 + 495, "Критерій відмови (EoL)"),
        (tx0 + 635, "Метод компенсації")
    ]
    for cx, title in cols:
        p.append(text(cx, ty0 + 20, title, size=9.5, color=INK, bold=True))

    # Розділювальні вертикальні лінії
    v_lines = [tx0 + 130, tx0 + 280, tx0 + 425, tx0 + 565]
    for vx in v_lines:
        p.append(line(vx, ty0, vx, ty0 + th, color="#e2e8f0", sw=1))

    # Рядки таблиці
    rows = [
        # Рядок 1: MLCC II/III
        (ty0 + 32, 68, "#ffffff", [
            ("MLCC Клас II/III\n(BaTiO₃: X7R, Y5V)", 9.5, INK, True),
            ("Релаксація доменів,\nпінінг вакансіями V_O¨", 9, INK, False),
            ("Логарифмічний час,\nDC-bias напруга", 9, MUTED, False),
            ("ΔC > −10%...−20%\n(понад допуск схеми)", 9, POS, True),
            ("Де-ейджинг (>150 °C),\nвибір класу C0G/NP0", 9, FIELD, False)
        ]),
        # Рядок 2: Алюмінієві електролітичні
        (ty0 + 100, 72, "#f8fafc", [
            ("Алюмінієві рідкі\n(GBL / EG розчинник)", 9.5, INK, True),
            ("Випаровування розчинника\nкрізь ущільнювач, сушка", 9, INK, False),
            ("T_core (Арреніус: +10°→×2),\nструм пульсацій I_rms", 9, POS, False),
            ("ΔC < −20%...−30%,\nESR > 2×...3× початкового", 9, POS, True),
            ("Зниження T_core,\nзапас за пульсаціями", 9, FIELD, False)
        ]),
        # Рядок 3: Плівкові
        (ty0 + 172, 68, "#ffffff", [
            ("Плівкові металізовані\n(PP, PET, PPS)", 9.5, INK, True),
            ("Самозаліковування пробоїв,\nкорона, корозія Al вологою", 9, INK, False),
            ("AC напруга (корона),\nвологість 85°C / 85% RH", 9, MUTED, False),
            ("ΔC < −5%...−10%,\nріст tan δ у 2–3 рази", 9, POS, True),
            ("Герметичні корпуси,\nдератинг AC напруги", 9, FIELD, False)
        ]),
        # Рядок 4: Танталові
        (ty0 + 240, 75, "#f8fafc", [
            ("Танталові твердотільні\n(Ta₂O₅: MnO₂ / Полімер)", 9.5, INK, True),
            ("Польова кристалізація\nаморфного оксиду Ta₂O₅", 9, INK, False),
            ("Електричне поле E,\nтемпература T", 9, MUTED, False),
            ("Ріст струму витоку DCL\nу 5–10 разів, пробій", 9, POS, True),
            ("Дератинг напруги 50% (MnO₂)\nабо перехід на полімер", 9, FIELD, False)
        ])
    ]

    for ry, r_h, bg_col, cell_data in rows:
        p.append(rect(tx0, ry, tw, r_h, fill=bg_col, stroke="#e2e8f0", sw=1))
        # Малюємо комірки
        col_centers = [tx0 + 65, tx0 + 205, tx0 + 355, tx0 + 495, tx0 + 635]
        for i, (text_content, fsize, fcol, fbold) in enumerate(cell_data):
            cx = col_centers[i]
            lines = text_content.split("\n")
            start_y = ry + r_h / 2 - (len(lines) - 1) * fsize * 0.65 + fsize * 0.35
            for j, ln in enumerate(lines):
                p.append(text(cx, start_y + j * fsize * 1.3, ln, size=fsize, color=fcol, bold=fbold))

    render(os.path.join(OUT, "capacitor-eol-criteria-comparison.svg"), W, H, *p, title="Порівняння критеріїв старіння та EoL конденсаторів")

if __name__ == "__main__":
    fig_mlcc_aging()
    fig_electrolytic_aging()
    fig_film_aging()
    fig_tantalum_aging()
    fig_eol_comparison()
    print("Всі 5 фігур успішно згенеровано.")
