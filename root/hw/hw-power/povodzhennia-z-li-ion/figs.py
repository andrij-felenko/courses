# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ORANGE = "#d35400"
GOLD   = "#b8860b"
PURPLE = "#8e44ad"

# ── 1. jeita-profile: Температурні зони та ліміти JEITA ──────────────────────
def fig_jeita_profile():
    W, H = 760, 360
    p = []

    # Заголовок осі
    p.append(text(W / 2, 28, "Температурний профіль заряду JEITA", size=14, bold=True, color=INK))
    
    # 5 зон
    zones = [
        ("< 0 °C", "Холод", "Заряд заборонено\nI = 0 мА\n(ризик плакування)", NEG, "#eef4ff", 40, 160),
        ("0..10 °C", "Прохолодно", "Знижений струм\nI ≤ 0.2C..0.5C\nV = 4.20 В", "#2980b9", "#f0f8ff", 160, 290),
        ("10..45 °C", "Стандарт", "Повний заряд\nI = 1.0C\nV = 4.20 В (CC/CV)", FIELD, "#eef8ef", 290, 520),
        ("45..60 °C", "Тепло", "Знижена напруга\nI ≤ 0.5C\nV ≤ 4.10 В", ORANGE, "#fdf6e8", 520, 640),
        ("> 60 °C", "Спека", "Заряд заборонено\nI = 0 мА\n(ризик розгону)", POS, "#fdf0ed", 640, 720),
    ]

    y_top = 55
    y_bot = 260

    # Малюємо смуги зон
    for t_range, z_name, z_desc, stroke_col, fill_col, x1, x2 in zones:
        zw = x2 - x1
        p.append(rect(x1, y_top, zw, y_bot - y_top, fill=fill_col, stroke=stroke_col, sw=1.5, rx=4))
        p.append(text(x1 + zw / 2, y_top + 22, z_name, size=12, bold=True, color=stroke_col))
        p.append(text(x1 + zw / 2, y_top + 40, t_range, size=11, bold=True, color=INK))
        
        lines = z_desc.split("\n")
        for idx, line_txt in enumerate(lines):
            p.append(text(x1 + zw / 2, y_top + 75 + idx * 18, line_txt, size=10, color=INK))

    # Вісь температури внизу
    p.append(line(30, y_bot + 25, 730, y_bot + 25, color=LINE, sw=1.8))
    p.append(arrow(700, y_bot + 25, 740, y_bot + 25, color=LINE, sw=1.8))
    p.append(text(745, y_bot + 29, "T, °C", size=11, bold=True, color=INK, anchor="start"))

    ticks = [(160, "0 °C"), (290, "10 °C"), (520, "45 °C"), (640, "60 °C")]
    for tx, tlbl in ticks:
        p.append(line(tx, y_bot + 18, tx, y_bot + 32, color=LINE, sw=1.5))
        p.append(text(tx, y_bot + 46, tlbl, size=10, bold=True, color=INK))

    # Пояснення внизу
    b, bw, bh = textbox(W / 2, H - 25, "Гістерезис ~2 °C на межах запобігає перемиканню режимів від шуму АЦП",
                        size=11, color=MUTED, fill=BG, stroke=MUTED, sw=1.0, min_w=580)
    p.append(b)

    render(os.path.join(OUT, "jeita-profile.svg"), W, H, *p,
           title="Профіль заряду JEITA за температурними зонами")


# ── 2. thermal-runaway-stages: Каскад теплового розгону ───────────────────────
def fig_thermal_runaway_stages():
    W, H = 760, 380
    p = []

    p.append(text(W / 2, 26, "П'ять стадій ланцюгової реакції теплового розгону (Thermal Runaway)",
                  size=13, bold=True, color=INK))

    stages = [
        ("80–120 °C", "Розпад пасиваційного SEI-шару", "Анод втрачає захисну плівку; початок екзотермічного саморозігріву", NEG, 55),
        ("120–140 °C", "Реакція літію в графіті з електролітом", "Пряма хімічна взаємодія розчинника з Li; виділення горючих вуглеводневих газів", "#d35400", 115),
        ("130–170 °C", "Плавлення полімерного сепаратора", "Поліетилен/поліпропілен плавляться; пряме внутрішнє коротке замикання (ISC)", POS, 175),
        ("180–240 °C", "Термічний розпад оксидного катода", "Вивільнення атомарного й молекулярного кисню (O₂) прямо всередину комірки", POS, 235),
        ("> 250–800 °C+", "Самопідтримуване вибухове горіння", "Кисень миттєво окиснює пари розчинника; викид полум'я, розрив корпусу, тиск >30 атм", "#780000", 295),
    ]

    for t_range, title_st, desc_st, col, y_pos in stages:
        # Температурна плашка
        tb, tbw, tbh = textbox(90, y_pos + 15, t_range, size=11, bold=True, color=BG, fill=col, stroke=col, min_w=120)
        p.append(tb)
        
        # Опис стадії
        p.append(rect(170, y_pos - 3, 560, 36, fill=FILL, stroke=col, sw=1.2, rx=4))
        p.append(text(180, y_pos + 13, title_st, size=11, bold=True, color=col, anchor="start"))
        p.append(text(180, y_pos + 26, desc_st, size=9.5, color=INK, anchor="start"))
        
        # Стрілка вниз між блоками
        if y_pos < 290:
            p.append(arrow(90, y_pos + 32, 90, y_pos + 46, color=col, sw=1.5))

    render(os.path.join(OUT, "thermal-runaway-stages.svg"), W, H, *p,
           title="Каскад температурних стадій теплового розгону")


# ── 3. copper-shunting: Механізм розчинення міді при перерозряді ───────────────
def fig_copper_shunting():
    W, H = 760, 340
    p = []

    p.append(text(W / 2, 25, "Механізм руйнування комірки при перерозряді нижче 2.0 В",
                  size=13, bold=True, color=INK))

    steps = [
        ("1. Нормальний розряд", "Напруга > 3.0 В\nПотенціал анода низький\nМідна фольга пасивна", FIELD, 105),
        ("2. Перерозряд (<2.0 В)", "Потенціал анода > 3.6 В\nОкиснення міді:\nCu → Cu²⁺ + 2e⁻", POS, 280),
        ("3. Міграція іонів", "Іони Cu²⁺ дифундують\nкрізь електроліт\nта пори сепаратора", ORANGE, 455),
        ("4. Наступний заряд", "Відновлення Cu²⁺ → Cu⁰\nРіст мідних дендритів\nВнутрішній коротун!", "#780000", 630),
    ]

    for title_s, desc_s, col, cx in steps:
        b, bw, bh = textbox(cx, 130, title_s + "\n\n" + desc_s, size=10.5, bold=False,
                            color=INK, fill=FILL, stroke=col, sw=1.6, min_w=155)
        p.append(b)
        # заголовок блоку окремим кольором
        p.append(text(cx, 85, title_s, size=11, bold=True, color=col))

    # Стрілки між кроками
    p.append(arrow(185, 130, 200, 130, color=LINE, sw=1.8))
    p.append(arrow(360, 130, 375, 130, color=LINE, sw=1.8))
    p.append(arrow(535, 130, 550, 130, color=LINE, sw=1.8))

    # Нижній висновок
    p.append(rect(40, 235, 680, 75, fill="#fdf0ed", stroke=POS, sw=1.5, rx=6))
    p.append(text(W / 2, 260, "ГОЛОВНЕ ПРАВИЛО БЕЗПЕКИ", size=11, bold=True, color=POS))
    p.append(text(W / 2, 280, "Комірку, що просіла нижче 1.5–2.0 В, ЗАБОРОНЕНО заряджати стандартним струмом.", size=10.5, bold=True, color=INK))
    p.append(text(W / 2, 296, "Мідні містки вже проросли крізь сепаратор: спроба заряду спричиняє лавинний внутрішній нагрів.", size=10, color=MUTED))

    render(os.path.join(OUT, "copper-shunting.svg"), W, H, *p,
           title="Розчинення мідного струмознімача та утворення мідних містків")


# ── 4. storage-degradation: Матриця умов зберігання ───────────────────────────
def fig_storage_degradation():
    W, H = 760, 350
    p = []

    p.append(text(W / 2, 26, "Вплив рівня заряду (SOC) і температури на деградацію при зберіганні",
                  size=13, bold=True, color=INK))

    cards = [
        ("100% SOC (4.20 В) @ 45 °C", "Втрата: ~35% ємності / рік\nПрискорене роздуття газом\nОкиснення електроліту на катоді", POS, "#fdf0ed", 140, 95),
        ("100% SOC (4.20 В) @ 25 °C", "Втрата: ~20% ємності / рік\nВисокий хімічний стрес\nРіст опору SEI-шару", ORANGE, "#fdf6e8", 430, 95),
        ("50% SOC (3.85 В) @ 25 °C", "Втрата: ~4% ємності / рік\nПомірне старіння\nНорма для побутових приладів", FIELD, "#eef8ef", 140, 220),
        ("50% SOC (3.85 В) @ 10–15 °C", "Втрата: ~1.5–2% ємності / рік\nІДЕАЛЬНИЙ РЕЖИМ\nМінімальний стрес і саморозряд", FIELD, "#eef8ef", 430, 220),
        ("0% SOC (<2.50 В) будь-де", "НЕБЕЗПЕКА!\nСаморозряд нижче 2.0 В\nРозчинення міді та смерть комірки", "#780000", "#f9eaea", 630, 157),
    ]

    for title_c, desc_c, col, fill_bg, cx, cy in cards:
        if cx == 630:
            # Окрема висока картка для 0% SOC
            b, bw, bh = textbox(cx, cy, title_c + "\n\n" + desc_c, size=10, bold=False,
                                color=INK, fill=fill_bg, stroke=col, sw=1.5, min_w=170)
            p.append(b)
            p.append(text(cx, cy - 40, title_c, size=10.5, bold=True, color=col))
        else:
            b, bw, bh = textbox(cx, cy, title_c + "\n\n" + desc_c, size=10, bold=False,
                                color=INK, fill=fill_bg, stroke=col, sw=1.5, min_w=240)
            p.append(b)
            p.append(text(cx, cy - 25, title_c, size=10.5, bold=True, color=col))

    # Підпис внизу
    p.append(text(W / 2, H - 18, "Оптимальна напруга тривалого консервування — 3.80–3.85 В (Storage Voltage)",
                  size=11, bold=True, color=INK, italic=True))

    render(os.path.join(OUT, "storage-degradation.svg"), W, H, *p,
           title="Деградація ємності Li-ion залежно від умов зберігання")


if __name__ == "__main__":
    fig_jeita_profile()
    fig_thermal_runaway_stages()
    fig_copper_shunting()
    fig_storage_degradation()
    print("All figures generated successfully.")
