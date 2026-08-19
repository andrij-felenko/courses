# -*- coding: utf-8 -*-
"""Фігури до теми «Зонна плавка кремнію (Float Zone)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки
SILICON_POLY = "#7f8c8d"   # полікристалічний вихідний стрижень
SILICON_MELT = "#e67e22"   # розплавлена зона (гарячий кремній)
SILICON_MONO = "#2980b9"   # чистий монокристал
COPPER_COIL  = "#d35400"   # мідний індуктор
ACCENT_BLUE  = "#1f4e79"
ACCENT_GREEN = "#1e8449"
ACCENT_RED   = "#c0392b"


# ── Фігура 1. Будова та принцип безтигельної зонної плавки (FZ) ───────────────
def fig_fz_setup():
    W, H = 820, 520
    f = [
        text(W / 2, 28, "Безтигельна зонна плавка кремнію (Float Zone)", size=17, bold=True),
        text(W / 2, 50, "Вертикальна конфігурація з високочастотним індуктором у захисній атмосфері аргону", size=13, color=MUTED, italic=True),
    ]

    # Робоча камера
    cam_x, cam_y, cam_w, cam_h = 180, 75, 460, 395
    f.append(rect(cam_x, cam_y, cam_w, cam_h, fill="#ffffff", stroke="#7f8c8d", sw=2, rx=8))
    f.append(text(cam_x + 15, cam_y + 24, "Герметична камера (Ar / вакуум)", size=12, color=MUTED, anchor="start", italic=True))

    cx = W / 2  # 410

    # Верхній стрижень (полікремній)
    poly_w, poly_h = 100, 110
    poly_y = 110
    f.append(rect(cx - poly_w / 2, poly_y, poly_w, poly_h, fill="#bdc3c7", stroke=LINE, sw=1.8))
    f.append(text(cx, poly_y + poly_h / 2 - 8, "Полікристалічний", size=13, bold=True))
    f.append(text(cx, poly_y + poly_h / 2 + 10, "живильний стрижень", size=13, bold=True))

    # Стрілка подачі верхнього стрижня
    f.append(arrow(cx + poly_w / 2 + 25, poly_y + 20, cx + poly_w / 2 + 25, poly_y + 80, color=POS, sw=2))
    f.append(text(cx + poly_w / 2 + 35, poly_y + 55, "Подача v_f", size=12, color=POS, anchor="start", bold=True))

    # Обертання верхнього стрижня
    f.append(text(cx - poly_w / 2 - 25, poly_y + 55, "Обертання ω₁", size=12, color=NEG, anchor="end", bold=True))

    # Розплавлена зона (крапля, що тримається натягом)
    melt_y = poly_y + poly_h
    melt_h = 45
    # Звуження та форма розплаву
    melt_path = (f"M {cx - poly_w/2:.1f} {melt_y:.1f} "
                 f"Q {cx - 35:.1f} {melt_y + melt_h/2:.1f} {cx - 45:.1f} {melt_y + melt_h:.1f} "
                 f"L {cx + 45:.1f} {melt_y + melt_h:.1f} "
                 f"Q {cx + 35:.1f} {melt_y + melt_h/2:.1f} {cx + poly_w/2:.1f} {melt_y:.1f} Z")
    f.append(f'<path d="{melt_path}" fill="#f39c12" stroke="#d35400" stroke-width="2"/>')
    f.append(text(cx, melt_y + melt_h / 2 + 4, "Розплавлена зона (Si)", size=12, color="#ffffff", bold=True))

    # ВЧ-індуктор (голкове вушко / needle-eye coil) з двох боків
    coil_y = melt_y + melt_h / 2
    f.append(circle(cx - 65, coil_y, 14, fill="#e74c3c", stroke="#922b21", sw=2))
    f.append(circle(cx - 65, coil_y, 6, fill="#ffffff", stroke="#922b21", sw=1.5))
    f.append(circle(cx + 65, coil_y, 14, fill="#e74c3c", stroke="#922b21", sw=2))
    f.append(circle(cx + 65, coil_y, 6, fill="#ffffff", stroke="#922b21", sw=1.5))

    f.append(text(cx - 88, coil_y + 4, "ВЧ-індуктор (2–3 МГц)", size=12, color=POS, anchor="end", bold=True))
    f.append(text(cx + 88, coil_y + 4, "Водяне охолодження", size=12, color=POS, anchor="start", bold=True))

    # Нижній монокристалічний злиток
    mono_w, mono_h = 90, 115
    mono_y = melt_y + melt_h
    f.append(rect(cx - mono_w / 2, mono_y, mono_w, mono_h, fill="#5dade2", stroke=LINE, sw=1.8))
    f.append(text(cx, mono_y + mono_h / 2 - 8, "Монокристал FZ", size=13, color="#ffffff", bold=True))
    f.append(text(cx, mono_y + mono_h / 2 + 12, "(надчистий кремній)", size=12, color="#ffffff"))

    # Затравка монокристала (seed)
    seed_w, seed_h = 24, 35
    seed_y = mono_y + mono_h
    f.append(rect(cx - seed_w / 2, seed_y, seed_w, seed_h, fill="#2980b9", stroke=LINE, sw=1.5))
    f.append(text(cx, seed_y + seed_h / 2 + 4, "Затравка", size=11, color="#ffffff", bold=True))

    # Рух витягування монокристала
    f.append(arrow(cx + mono_w / 2 + 25, mono_y + 20, cx + mono_w / 2 + 25, mono_y + 80, color=ACCENT_BLUE, sw=2))
    f.append(text(cx + mono_w / 2 + 35, mono_y + 55, "Витягування v_c", size=12, color=ACCENT_BLUE, anchor="start", bold=True))

    # Обертання монокристала (протилежний напрямок)
    f.append(text(cx - mono_w / 2 - 25, mono_y + 55, "Обертання ω₂", size=12, color=NEG, anchor="end", bold=True))

    # Пояснення безтигельності ліворуч та праворуч
    f.append(rect(20, 190, 140, 140, fill="#fdfefe", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(90, 214, "Ключова перевага", size=12.5, color=FIELD, bold=True))
    f.append(text(90, 238, "Жодного контакту", size=11.5, color=INK))
    f.append(text(90, 256, "з кварцовим тиглем!", size=11.5, color=INK))
    f.append(text(90, 276, "[O] < 10¹⁵ см⁻³", size=11.5, color=FIELD, bold=True))
    f.append(text(90, 294, "[C] < 10¹⁵ см⁻³", size=11.5, color=FIELD, bold=True))
    f.append(text(90, 314, "τ > 1000–5000 мкс", size=11, color=MUTED))

    f.append(rect(660, 190, 140, 140, fill="#fdfefe", stroke=POS, sw=1.5, rx=6))
    f.append(text(730, 214, "Фізичний баланс", size=12.5, color=POS, bold=True))
    f.append(text(730, 238, "Краплю утримують:", size=11.5, color=INK))
    f.append(text(730, 258, "• Поверхневий натяг", size=11, color=INK))
    f.append(text(730, 276, "  (γ ≈ 0.72 Н/м)", size=11, color=MUTED))
    f.append(text(730, 296, "• Електромагнітне", size=11, color=INK))
    f.append(text(730, 314, "  стискання (Лоренц)", size=11, color=MUTED))

    f.append(text(W / 2, H - 15, "Розплав тримається власною поверхневою плівкою та електромагнітним полем, не торкаючись стінок.", size=12.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "fz-setup.svg"), W, H, *f)


# ── Фігура 2. Порівняння чистоти й структури: Чохральський (CZ) проти FZ ─────
def fig_cz_vs_fz_purity():
    W, H = 840, 480
    f = [
        text(W / 2, 28, "Порівняння методів вирощування: Чохральський (CZ) та Float Zone (FZ)", size=17, bold=True),
        text(W / 2, 50, "Вплив тигля на чистоту кристалічної ґратки, вміст кисню та час життя носіїв", size=13, color=MUTED, italic=True),
    ]

    col_w, col_h = 380, 360
    y0 = 75

    # Ліва колонка: Чохральський (CZ)
    x_cz = 30
    f.append(rect(x_cz, y0, col_w, col_h, fill="#fbfcfc", stroke=POS, sw=2, rx=8))
    f.append(text(x_cz + col_w / 2, y0 + 28, "Метод Чохральського (CZ)", size=15, color=POS, bold=True))
    f.append(text(x_cz + col_w / 2, y0 + 48, "Стандарт мікроелектроніки (CMOS, пам'ять)", size=12, color=MUTED, italic=True))

    # Схема тигля CZ
    f.append(rect(x_cz + 110, y0 + 65, 160, 70, fill="#f9ebea", stroke="#c0392b", sw=1.5, rx=4))
    f.append(text(x_cz + 190, y0 + 90, "Кварцовий тигель (SiO₂)", size=12, color=POS, bold=True))
    f.append(text(x_cz + 190, y0 + 112, "Розчинення стінок → O, C у розплав", size=11, color="#78281f"))

    cz_metrics = [
        ("Концентрація кисню [O]:", "5·10¹⁷ – 10¹⁸ см⁻³ (висока)", POS),
        ("Концентрація вуглецю [C]:", "10¹⁶ – 10¹⁷ см⁻³ (помітна)", POS),
        ("Питомий опір (ρ):", "1 – 50 Ом·см (обмежений)", INK),
        ("Час життя носіїв (τ):", "10 – 100 мкс (преципітати)", POS),
        ("Максимальний діаметр:", "300 мм (існує 450 мм)", FIELD),
        ("Основне застосування:", "Процесори, пам'ять, CMOS-логіка", INK),
    ]

    for i, (label, val, col) in enumerate(cz_metrics):
        my = y0 + 155 + i * 32
        f.append(text(x_cz + 20, my, label, size=12, color=INK, anchor="start", bold=True))
        f.append(text(x_cz + col_w - 20, my, val, size=12, color=col, anchor="end", bold=True))

    # Права колонка: Float Zone (FZ)
    x_fz = 430
    f.append(rect(x_fz, y0, col_w, col_h, fill="#fbfcfc", stroke=FIELD, sw=2, rx=8))
    f.append(text(x_fz + col_w / 2, y0 + 28, "Зонна плавка (Float Zone, FZ)", size=15, color=FIELD, bold=True))
    f.append(text(x_fz + col_w / 2, y0 + 48, "Силова електроніка та детектори випромінювання", size=12, color=MUTED, italic=True))

    # Схема FZ
    f.append(rect(x_fz + 110, y0 + 65, 160, 70, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=4))
    f.append(text(x_fz + 190, y0 + 90, "Безтигельний розплав", size=12, color=FIELD, bold=True))
    f.append(text(x_fz + 190, y0 + 112, "Вільна поверхня в чистому Ar", size=11, color="#145a32"))

    fz_metrics = [
        ("Концентрація кисню [O]:", "< 10¹⁵ – 10¹⁶ см⁻³ (наднизька)", FIELD),
        ("Концентрація вуглецю [C]:", "< 10¹⁵ см⁻³ (гранично мала)", FIELD),
        ("Питомий опір (ρ):", "1 000 – 100 000 Ом·см (гігантський)", FIELD),
        ("Час життя носіїв (τ):", "1 000 – 10 000 мкс (до 10 мс)", FIELD),
        ("Максимальний діаметр:", "150 – 200 мм (обмежений натягом)", POS),
        ("Основне застосування:", "IGBT, тиристори, детектори, RF", INK),
    ]

    for i, (label, val, col) in enumerate(fz_metrics):
        my = y0 + 155 + i * 32
        f.append(text(x_fz + 20, my, label, size=12, color=INK, anchor="start", bold=True))
        f.append(text(x_fz + col_w - 20, my, val, size=12, color=col, anchor="end", bold=True))

    f.append(text(W / 2, H - 15, "FZ-кремній дає на порядки вищу чистоту й час життя носіїв, але обмежений у діаметрі злитка.", size=12.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "cz-vs-fz-purity.svg"), W, H, *f)


# ── Фігура 3. Профіль сегрегації домішок вздовж злитка ─────────────────────────
def fig_segregation_profile():
    W, H = 800, 460
    f = [
        text(W / 2, 28, "Сегрегація домішок під час проходження зонної плавки", size=17, bold=True),
        text(W / 2, 50, "Розподіл відносної концентрації C(x)/C₀ вздовж злитка для домішок з k₀ < 1", size=13, color=MUTED, italic=True),
    ]

    # Графік
    gx, gy, gw, gh = 90, 85, 620, 270

    # Сітка
    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#bdc3c7", sw=1.5))
    for y_val in [0.25, 0.5, 0.75]:
        yy = gy + gh * (1 - y_val)
        f.append(line(gx, yy, gx + gw, yy, color="#eaeded", sw=1, dash="4,4"))

    for x_val in [0.2, 0.4, 0.6, 0.8]:
        xx = gx + gw * x_val
        f.append(line(xx, gy, xx, gy + gh, color="#eaeded", sw=1, dash="4,4"))

    # Осі
    f.append(arrow(gx, gy + gh, gx + gw + 30, gy + gh, color=INK, sw=2))
    f.append(text(gx + gw + 20, gy + gh + 28, "Відстань вздовж злитка x / L", size=12.5, bold=True))

    f.append(arrow(gx, gy + gh, gx, gy - 25, color=INK, sw=2))
    f.append(text(gx - 15, gy - 15, "C / C₀", size=13, bold=True, anchor="end"))

    # Позначки осі Y
    f.append(text(gx - 10, gy + gh, "0", size=12, anchor="end"))
    f.append(text(gx - 10, gy + gh * 0.75, "k₀", size=12, color=POS, anchor="end", bold=True))
    f.append(text(gx - 10, gy + gh * 0.5, "0.5", size=12, anchor="end"))
    f.append(text(gx - 10, gy + gh * 0.1, "1.0", size=12, anchor="end", bold=True))
    f.append(line(gx - 5, gy + gh * 0.1, gx, gy + gh * 0.1, color=INK, sw=1.5))

    # Позначки осі X
    f.append(text(gx, gy + gh + 18, "0 (початок)", size=11.5, anchor="middle"))
    f.append(text(gx + gw * 0.5, gy + gh + 18, "0.5", size=11.5, anchor="middle"))
    f.append(text(gx + gw, gy + gh + 18, "1.0 (хвіст)", size=11.5, anchor="middle"))

    # Крива 1: Однопрохідна плавка (n = 1, k = 0.1)
    p1 = (f"M {gx:.1f} {gy + gh*0.75:.1f} "
          f"C {gx + gw*0.3:.1f} {gy + gh*0.65:.1f}, {gx + gw*0.6:.1f} {gy + gh*0.25:.1f}, {gx + gw*0.85:.1f} {gy + gh*0.1:.1f} "
          f"Q {gx + gw*0.95:.1f} {gy + gh*0.08:.1f} {gx + gw:.1f} {gy + 10:.1f}")
    f.append(f'<path d="{p1}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    f.append(text(gx + gw * 0.55, gy + gh * 0.35, "1 прохід (n = 1)", size=12.5, color=POS, bold=True))

    # Крива 2: Три проходи (n = 3, k = 0.1)
    p3 = (f"M {gx:.1f} {gy + gh*0.92:.1f} "
          f"C {gx + gw*0.3:.1f} {gy + gh*0.90:.1f}, {gx + gw*0.6:.1f} {gy + gh*0.75:.1f}, {gx + gw*0.82:.1f} {gy + gh*0.2:.1f} "
          f"Q {gx + gw*0.92:.1f} {gy + gh*0.05:.1f} {gx + gw:.1f} {gy + 5:.1f}")
    f.append(f'<path d="{p3}" fill="none" stroke="{ACCENT_BLUE}" stroke-width="2.5" stroke-dasharray="6,3"/>')
    f.append(text(gx + gw * 0.65, gy + gh * 0.65, "3 проходи (n = 3)", size=12.5, color=ACCENT_BLUE, bold=True))

    # Крива 3: Багатопрохідна гранична чистота (n = 10)
    p10 = (f"M {gx:.1f} {gy + gh*0.98:.1f} "
           f"L {gx + gw*0.5:.1f} {gy + gh*0.97:.1f} "
           f"C {gx + gw*0.75:.1f} {gy + gh*0.95:.1f}, {gx + gw*0.85:.1f} {gy + gh*0.6:.1f}, {gx + gw*0.92:.1f} {gy + gh*0.15:.1f} "
           f"L {gx + gw:.1f} {gy:.1f}")
    f.append(f'<path d="{p10}" fill="none" stroke="{ACCENT_GREEN}" stroke-width="2.5"/>')
    f.append(text(gx + gw * 0.35, gy + gh * 0.92, "10 проходів (граничне очищення)", size=12.5, color=ACCENT_GREEN, bold=True))

    # Позначення зон під графіком
    zy = gy + gh + 42
    f.append(rect(gx, zy, gw * 0.75, 30, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(gx + gw * 0.375, zy + 19, "Очищена монокристалічна частина (робочий злиток)", size=12, color=FIELD, bold=True))

    f.append(rect(gx + gw * 0.77, zy, gw * 0.23, 30, fill="#fdedec", stroke=POS, sw=1.5, rx=4))
    f.append(text(gx + gw * 0.885, zy + 19, "Брудний хвіст (відрізається)", size=11, color=POS, bold=True))

    f.append(text(W / 2, H - 12, "Кожен наступний прохід розплавленої зони зсуває домішки з коефіцієнтом k₀ < 1 у хвостову частину.", size=12.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "segregation-profile.svg"), W, H, *f)


# ── Фігура 4. Голковий індуктор (Needle-Eye) та фізика утримання розплаву ─────
def fig_needle_eye_inductor():
    W, H = 840, 480
    f = [
        text(W / 2, 28, "Голковий індуктор (Needle-Eye) та баланс сил у розплаві", size=17, bold=True),
        text(W / 2, 50, "Механізм масштабування діаметра FZ-злитків від 50 мм до 150–200 мм", size=13, color=MUTED, italic=True),
    ]

    # Ліва панель: геометрія голкового індуктора
    lx, ly, lw, lh = 30, 75, 380, 365
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(lx + lw / 2, ly + 25, "Геометрія індуктора «Needle-Eye»", size=14, bold=True))

    lcx = lx + lw / 2  # 220
    # Верхній товстий стрижень
    f.append(rect(lcx - 60, ly + 45, 120, 60, fill="#bdc3c7", stroke=LINE, sw=1.5))
    f.append(text(lcx, ly + 78, "Живильний стрижень (150 мм)", size=11.5, bold=True))

    # Конічний перехід розплаву крізь вузький отвір
    melt_poly = (f"M {lcx - 60:.1f} {ly + 105:.1f} "
                 f"L {lcx - 18:.1f} {ly + 140:.1f} "
                 f"L {lcx - 18:.1f} {ly + 160:.1f} "
                 f"L {lcx - 55:.1f} {ly + 195:.1f} "
                 f"L {lcx + 55:.1f} {ly + 195:.1f} "
                 f"L {lcx + 18:.1f} {ly + 160:.1f} "
                 f"L {lcx + 18:.1f} {ly + 140:.1f} "
                 f"L {lcx + 60:.1f} {ly + 105:.1f} Z")
    f.append(f'<path d="{melt_poly}" fill="#f39c12" stroke="#d35400" stroke-width="2"/>')

    # Індуктор — плоска мідна пластина з малим отвором
    f.append(rect(lcx - 85, ly + 142, 60, 16, fill="#e74c3c", stroke="#922b21", sw=1.5, rx=2))
    f.append(rect(lcx + 25, ly + 142, 60, 16, fill="#e74c3c", stroke="#922b21", sw=1.5, rx=2))
    f.append(text(lcx, ly + 155, "Отвір 30–40 мм", size=10.5, color="#ffffff", bold=True))

    # Нижній монокристал
    f.append(rect(lcx - 55, ly + 195, 110, 75, fill="#5dade2", stroke=LINE, sw=1.5))
    f.append(text(lcx, ly + 235, "Монокристал FZ (150–200 мм)", size=11.5, color="#ffffff", bold=True))

    f.append(text(lcx, ly + 300, "Вузький отвір індуктора локалізує", size=11.5, color=INK))
    f.append(text(lcx, ly + 318, "електромагнітне поле, концентруючи", size=11.5, color=INK))
    f.append(text(lcx, ly + 336, "тепло в тонкому перешийку.", size=11.5, color=INK))

    # Права панель: баланс фізичних сил
    rx_p, ry_p, rw_p, rh_p = 430, 75, 380, 365
    f.append(rect(rx_p, ry_p, rw_p, rh_p, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(rx_p + rw_p / 2, ry_p + 25, "Баланс тисків у рідкій зоні", size=14, bold=True))

    forces = [
        ("1. Гідростатичний гравітаційний тиск:", "P_hyd = ρ · g · h", "Тягне розплав униз, прагне зірвати краплю", POS),
        ("2. Капілярний тиск натягу:", "ΔP_γ = γ · (1/R₁ + 1/R₂)", "Стискає вільну поверхню розплаву (γ ≈ 0.72 Н/м)", FIELD),
        ("3. Електромагнітний тиск (Пінч-ефект):", "P_EM = μ₀ · H² / 2", "Сили Лоренца (J × B) підтримують розплав", ACCENT_BLUE),
    ]

    for i, (title, formula, desc, col) in enumerate(forces):
        fy = ry_p + 55 + i * 82
        f.append(rect(rx_p + 15, fy, rw_p - 30, 72, fill="#fdfefe", stroke=col, sw=1.5, rx=6))
        f.append(text(rx_p + 25, fy + 20, title, size=11.5, color=col, anchor="start", bold=True))
        f.append(text(rx_p + rw_p - 25, fy + 20, formula, size=12, color=INK, anchor="end", bold=True))
        f.append(text(rx_p + 25, fy + 45, desc, size=11, color=MUTED, anchor="start", italic=True))

    f.append(rect(rx_p + 15, ry_p + 305, rw_p - 30, 48, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=6))
    f.append(text(rx_p + rw_p / 2, ry_p + 325, "Критерій стійкості Гейванга (Heywang limit):", size=11.5, color="#7d6608", bold=True))
    f.append(text(rx_p + rw_p / 2, ry_p + 342, "Максимальна висота зони h_max ≈ 2.8 · √(γ / (ρ·g)) ≈ 15 мм", size=11.5, color=INK, bold=True))

    f.append(text(W / 2, H - 15, "Конструкція Needle-Eye компенсує обмеження поверхневого натягу за рахунок електромагнітної левітації.", size=12.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "needle-eye-inductor.svg"), W, H, *f)


# ── Фігура 5. Нейтронно-трансмутаційне легування (NTD) ────────────────────────
def fig_ntd_process():
    W, H = 840, 470
    f = [
        text(W / 2, 28, "Нейтронно-трансмутаційне легування кремнію (NTD)", size=17, bold=True),
        text(W / 2, 50, "Ядерна реакція перетворення ³⁰Si → ³¹P для забезпечення ідеальної радіальної однорідності", size=13, color=MUTED, italic=True),
    ]

    # Верхня частина: ланцюг ядерної реакції
    f.append(rect(30, 75, 780, 115, fill="#f4f6f7", stroke=ACCENT_BLUE, sw=1.8, rx=8))
    f.append(text(W / 2, 98, "Ядерна реакція опромінення тепловими нейтронами в реакторі", size=13.5, color=ACCENT_BLUE, bold=True))

    rx_steps = [
        ("Ізотоп ³⁰Si", "3.1% у природному Si", "#5dade2"),
        ("+ Тепловий нейтрон n_th", "Захоплення нейтрона", "#f39c12"),
        ("Нестабільний ³¹Si", "T₁/₂ = 2.62 години", "#e74c3c"),
        ("β⁻ розпад (електрон + нейтрино)", "Перетворення ядра", "#9b59b6"),
        ("Донорний атом ³¹P", "Фосфор n-типу в ґратці", "#27ae60"),
    ]

    sw_box, sh_box = 135, 54
    start_x = 45
    for i, (head, sub, col) in enumerate(rx_steps):
        bx = start_x + i * 152
        f.append(rect(bx, 120, sw_box, sh_box, fill="#ffffff", stroke=col, sw=1.8, rx=6))
        f.append(text(bx + sw_box / 2, 140, head, size=11.5, color=col, bold=True))
        f.append(text(bx + sw_box / 2, 158, sub, size=10, color=MUTED))
        if i < 4:
            f.append(arrow(bx + sw_box + 2, 147, bx + sw_box + 14, 147, color=INK, sw=1.8))

    # Нижня частина: порівняння профілів питомого опору
    ly = 205
    lw, lh = 380, 220

    # Лівий графік: традиційне газове легування (смуги Marangoni)
    f.append(rect(30, ly, lw, lh, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    f.append(text(30 + lw / 2, ly + 24, "Газове легування FZ (фосфін PH₃)", size=13, color=POS, bold=True))
    f.append(text(30 + lw / 2, ly + 42, "Конвекція Марангоні створює радіальні смуги", size=11.5, color=MUTED, italic=True))

    # Графік флуктуацій опору
    gx1, gy1, gw1, gh1 = 60, ly + 65, 320, 100
    f.append(rect(gx1, gy1, gw1, gh1, fill="#fdfefe", stroke="#bdc3c7", sw=1))
    f.append(line(gx1, gy1 + gh1 / 2, gx1 + gw1, gy1 + gh1 / 2, color="#95a5a6", sw=1, dash="4,4"))

    # Хвиляста лінія коливань
    p_gas = (f"M {gx1:.1f} {gy1 + gh1/2:.1f} "
             f"Q {gx1 + 30:.1f} {gy1 + 20:.1f} {gx1 + 60:.1f} {gy1 + gh1/2:.1f} "
             f"Q {gx1 + 90:.1f} {gy1 + 80:.1f} {gx1 + 120:.1f} {gy1 + gh1/2:.1f} "
             f"Q {gx1 + 150:.1f} {gy1 + 15:.1f} {gx1 + 180:.1f} {gy1 + gh1/2:.1f} "
             f"Q {gx1 + 210:.1f} {gy1 + 85:.1f} {gx1 + 240:.1f} {gy1 + gh1/2:.1f} "
             f"Q {gx1 + 270:.1f} {gy1 + 25:.1f} {gx1 + 300:.1f} {gy1 + gh1/2:.1f} "
             f"L {gx1 + gw1:.1f} {gy1 + gh1/2:.1f}")
    f.append(f'<path d="{p_gas}" fill="none" stroke="{POS}" stroke-width="2"/>')
    f.append(text(30 + lw / 2, ly + 182, "Радіальний розкид опору: ±15% … ±30%", size=12, color=POS, bold=True))
    f.append(text(30 + lw / 2, ly + 200, "Локальні пробої у високовольтних приладах", size=11, color=MUTED))

    # Правий графік: трансмутаційне легування NTD
    f.append(rect(430, ly, lw, lh, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(430 + lw / 2, ly + 24, "Нейтронне легування (NTD)", size=13, color=FIELD, bold=True))
    f.append(text(430 + lw / 2, ly + 42, "Ізотоп ³⁰Si розподілений абсолютно рівномірно", size=11.5, color=MUTED, italic=True))

    gx2, gy2, gw2, gh2 = 460, ly + 65, 320, 100
    f.append(rect(gx2, gy2, gw2, gh2, fill="#fdfefe", stroke="#bdc3c7", sw=1))
    f.append(line(gx2, gy2 + gh2 / 2, gx2 + gw2, gy2 + gh2 / 2, color="#95a5a6", sw=1, dash="4,4"))

    # Ідеально пряма лінія
    f.append(line(gx2, gy2 + gh2 / 2, gx2 + gw2, gy2 + gh2 / 2, color=FIELD, sw=2.5))
    f.append(text(430 + lw / 2, ly + 182, "Радіальний розкид опору: < 1% … 2%", size=12, color=FIELD, bold=True))
    f.append(text(430 + lw / 2, ly + 200, "Ідеально рівномірне поле пробою по всій площі", size=11, color=MUTED))

    f.append(text(W / 2, H - 12, "NTD перетворює природний кремній на фосфор із точністю атомного масштабу по всьому об'єму пластини.", size=12.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "ntd-process.svg"), W, H, *f)


# ── Фігура 6. Застосування FZ-кремнію у високовольтних приладах ───────────────
def fig_power_applications():
    W, H = 840, 480
    f = [
        text(W / 2, 28, "Застосування надчистого FZ-кремнію в силовій електроніці", size=17, bold=True),
        text(W / 2, 50, "Чому високовольтні IGBT та тиристори вимагають товстої високоомної n⁻-бази", size=13, color=MUTED, italic=True),
    ]

    # Ліва частина: переріз високовольтного IGBT
    lx, ly, lw, lh = 30, 75, 430, 365
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke=ACCENT_BLUE, sw=1.8, rx=8))
    f.append(text(lx + lw / 2, ly + 24, "Структура високовольтного IGBT (3.3–6.5 кВ)", size=13.5, color=ACCENT_BLUE, bold=True))

    # Шари IGBT
    cx = lx + lw / 2
    y_top = ly + 48

    # Емітер / Затвор (поверхня)
    f.append(rect(cx - 170, y_top, 340, 32, fill="#aed6f1", stroke=LINE, sw=1.5))
    f.append(text(cx, y_top + 20, "MOS-затвори та p-емітерні комірки", size=11.5, bold=True))

    # Товста n- дрейфова база (FZ Silicon)
    drift_h = 160
    drift_y = y_top + 32
    f.append(rect(cx - 170, drift_y, 340, drift_h, fill="#e8f8f5", stroke=FIELD, sw=2))
    f.append(text(cx, drift_y + 40, "Товста n⁻ дрейфова база з FZ-кремнію", size=13, color=FIELD, bold=True))
    f.append(text(cx, drift_y + 65, "Товщина W_d: 350 – 700 мкм", size=12, color=INK))
    f.append(text(cx, drift_y + 88, "Питомий опір ρ: 100 – 600 Ом·см", size=12, color=INK))
    f.append(text(cx, drift_y + 110, "Час життя τ > 1000 мкс (глибока модуляція провідності)", size=11.5, color=MUTED, italic=True))
    f.append(text(cx, drift_y + 132, "Утримує напругу до 6500 В у закритому стані", size=11.5, color=POS, bold=True))

    # Буферний шар та колектор
    y_bot = drift_y + drift_h
    f.append(rect(cx - 170, y_bot, 340, 25, fill="#f9e79f", stroke=LINE, sw=1.2))
    f.append(text(cx, y_bot + 17, "n⁺ польовий стоп-шар (Field Stop)", size=11, bold=True))

    f.append(rect(cx - 170, y_bot + 25, 340, 30, fill="#f5b7b1", stroke=LINE, sw=1.5))
    f.append(text(cx, y_bot + 45, "p⁺ колекторний шар + металізація анода", size=11.5, bold=True))

    # Права частина: галузі застосування
    rx, ry, rw, rh = 480, 75, 330, 365
    f.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(rx + rw / 2, ry + 24, "Ключові ринкові ніші FZ-кремнію", size=13.5, bold=True))

    apps = [
        ("Електротранспорт та тяга:", "Інвертори електропоїздів, EV,", "приводи 100 кВт – 5 МВт.", ACCENT_BLUE),
        ("Енергетика HVDC:", "Високовольтні лінії передачі,", "тиристорні вентилі до 800 кВ.", POS),
        ("Детектори ядерної фізики:", "Кремнієві трекові детектори (CERN),", "PIN-діоди повного збіднення.", ACCENT_GREEN),
        ("Високочастотні RF-прилади:", "Підкладки для радарів і терагерців", "з нульовими діелектричними втратами.", "#8e44ad"),
    ]

    for i, (head, l1, l2, col) in enumerate(apps):
        ay = ry + 48 + i * 76
        f.append(rect(rx + 12, ay, rw - 24, 68, fill="#fcfcfc", stroke=col, sw=1.5, rx=6))
        f.append(text(rx + 22, ay + 18, head, size=11.5, color=col, anchor="start", bold=True))
        f.append(text(rx + 22, ay + 36, l1, size=10.5, color=INK, anchor="start"))
        f.append(text(rx + 22, ay + 52, l2, size=10.5, color=INK, anchor="start"))

    f.append(text(W / 2, H - 15, "Чим вища блокувальна напруга приладу, тим товстішою має бути база і тим вищі вимоги до FZ-кремнію.", size=12.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "power-applications.svg"), W, H, *f)


# ── Запуск генерації всіх фігур ──────────────────────────────────────────────
if __name__ == "__main__":
    fig_fz_setup()
    fig_cz_vs_fz_purity()
    fig_segregation_profile()
    fig_needle_eye_inductor()
    fig_ntd_process()
    fig_power_applications()
    print("Всі 6 фігур згенеровано успішно в ./img/")
