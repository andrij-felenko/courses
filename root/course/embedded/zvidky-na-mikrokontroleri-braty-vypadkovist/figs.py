# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Повний конвеєр ентропії: від фізичного шуму до криптографічних ключів ──
def fig_entropy_pipeline():
    W, H = 840, 390
    p = []
    p.append(text(W / 2, 26, "Конвеєр криптографічної випадковості у вбудованих системах", size=15, bold=True))

    # Блок 1: Фізичні джерела шуму
    b1_x, b1_y, b1_w, b1_h = 25, 60, 165, 230
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#fdfaf6", stroke=POS, sw=1.6))
    p.append(text(b1_x + b1_w / 2, b1_y + 22, "1. Джерела ентропії", size=12, color=POS, bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 44, "• Тепловий шум p-n", size=11, color=INK, anchor="middle"))
    p.append(text(b1_x + b1_w / 2, b1_y + 66, "• Фазовий джиттер ROSC", size=11, color=INK, anchor="middle"))
    p.append(text(b1_x + b1_w / 2, b1_y + 88, "• Молодші біти АЦП", size=11, color=INK, anchor="middle"))
    p.append(text(b1_x + b1_w / 2, b1_y + 110, "• Дрейф таймерів RC/HSE", size=11, color=INK, anchor="middle"))
    p.append(text(b1_x + b1_w / 2, b1_y + 132, "• Джиттер радіопакетів", size=11, color=INK, anchor="middle"))
    p.append(line(b1_x + 10, b1_y + 148, b1_x + b1_w - 10, b1_y + 148, color="#e5c8ba", sw=1.0))
    p.append(text(b1_x + b1_w / 2, b1_y + 168, "Сирий шум:", size=10.5, color=POS, bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 188, "Нерівномірний (Bias)", size=10, color=MUTED))
    p.append(text(b1_x + b1_w / 2, b1_y + 208, "Автокорельований", size=10, color=MUTED))

    # Стрілка 1 -> 2
    p.append(arrow(b1_x + b1_w + 3, b1_y + 115, b1_x + b1_w + 22, b1_y + 115, color=LINE, sw=1.8))

    # Блок 2: Онлайн-тести працездатності (Health Tests)
    b2_x, b2_y, b2_w, b2_h = 215, 60, 165, 230
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#fffaf0", stroke="#d97706", sw=1.6))
    p.append(text(b2_x + b2_w / 2, b2_y + 22, "2. Health Monitor", size=12, color="#d97706", bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 40, "(NIST SP 800-90B)", size=10, color=MUTED))
    p.append(text(b2_x + b2_w / 2, b2_y + 68, "Repetition Count Test", size=10.5, color=INK, bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 86, "Виявляє залипання бітів", size=9.5, color=MUTED))
    p.append(line(b2_x + 10, b2_y + 100, b2_x + b2_w - 10, b2_y + 100, color="#fde68a", sw=1.0))
    p.append(text(b2_x + b2_w / 2, b2_y + 120, "Adaptive Proportion", size=10.5, color=INK, bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 138, "Контроль перекосу 0/1", size=9.5, color=MUTED))
    p.append(line(b2_x + 10, b2_y + 152, b2_x + b2_w - 10, b2_y + 152, color="#fde68a", sw=1.0))
    p.append(text(b2_x + b2_w / 2, b2_y + 172, "Детекція деградації:", size=10.5, color="#d97706", bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 192, "Аварійне блокування", size=10, color=POS))
    p.append(text(b2_x + b2_w / 2, b2_y + 210, "при відмові сенсора", size=9.5, color=MUTED))

    # Стрілка 2 -> 3
    p.append(arrow(b2_x + b2_w + 3, b2_y + 115, b2_x + b2_w + 22, b2_y + 115, color=LINE, sw=1.8))

    # Блок 3: Кондиціювання та пул ентропії
    b3_x, b3_y, b3_w, b3_h = 405, 60, 185, 230
    p.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#f0f7ff", stroke=NEG, sw=1.6))
    p.append(text(b3_x + b3_w / 2, b3_y + 22, "3. Пул і кондиціювання", size=12, color=NEG, bold=True))
    p.append(text(b3_x + b3_w / 2, b3_y + 40, "(Entropy Conditioning)", size=10, color=MUTED))
    p.append(text(b3_x + b3_w / 2, b3_y + 68, "Фільтр Фон Неймана", size=10.5, color=INK, bold=True))
    p.append(text(b3_x + b3_w / 2, b3_y + 86, "Знищення асиметрії 0/1", size=9.5, color=MUTED))
    p.append(line(b3_x + 10, b3_y + 100, b3_x + b3_w - 10, b3_y + 100, color="#bfdbfe", sw=1.0))
    p.append(text(b3_x + b3_w / 2, b3_y + 120, "Акумулятор ентропії", size=10.5, color=INK, bold=True))
    p.append(text(b3_x + b3_w / 2, b3_y + 138, "Криптографічний хеш", size=10, color=NEG))
    p.append(text(b3_x + b3_w / 2, b3_y + 154, "(SHA-256 / Blake2s)", size=9.5, color=MUTED))
    p.append(line(b3_x + 10, b3_y + 168, b3_x + b3_w - 10, b3_y + 168, color="#bfdbfe", sw=1.0))
    p.append(text(b3_x + b3_w / 2, b3_y + 188, "Вихід: 256-бітний", size=10, color=INK))
    p.append(text(b3_x + b3_w / 2, b3_y + 208, "ідеальний Seed", size=10.5, color=FIELD, bold=True))

    # Стрілка 3 -> 4
    p.append(arrow(b3_x + b3_w + 3, b3_y + 115, b3_x + b3_w + 22, b3_y + 115, color=LINE, sw=1.8))

    # Блок 4: CSPRNG (Криптографічний генератор)
    b4_x, b4_y, b4_w, b4_h = 615, 60, 195, 230
    p.append(rect(b4_x, b4_y, b4_w, b4_h, fill="#f0faf4", stroke=FIELD, sw=1.6))
    p.append(text(b4_x + b4_w / 2, b4_y + 22, "4. CSPRNG Двигун", size=12, color=FIELD, bold=True))
    p.append(text(b4_x + b4_w / 2, b4_y + 40, "(ChaCha20-DRBG / AES-CTR)", size=10, color=MUTED))
    p.append(text(b4_x + b4_w / 2, b4_y + 68, "Внутрішній стан:", size=10.5, color=INK, bold=True))
    p.append(text(b4_x + b4_w / 2, b4_y + 86, "Key [256] + Nonce [96]", size=9.5, color=MUTED))
    p.append(line(b4_x + 10, b4_y + 100, b4_x + b4_w - 10, b4_y + 100, color="#bbf7d0", sw=1.0))
    p.append(text(b4_x + b4_w / 2, b4_y + 120, "Backtracking Resistance", size=10.5, color=INK, bold=True))
    p.append(text(b4_x + b4_w / 2, b4_y + 138, "Перезапис ключа після виходу", size=9.5, color=MUTED))
    p.append(line(b4_x + 10, b4_y + 152, b4_x + b4_w - 10, b4_y + 152, color="#bbf7d0", sw=1.0))
    p.append(text(b4_x + b4_w / 2, b4_y + 172, "Споживачі:", size=10.5, color=FIELD, bold=True))
    p.append(text(b4_x + b4_w / 2, b4_y + 192, "Ключі сесій TLS / DTLS", size=10, color=INK))
    p.append(text(b4_x + b4_w / 2, b4_y + 210, "ECDSA Nonce, AES-GCM IV", size=10, color=INK))

    # Нижній висновок
    pipeline_msg = (
        "Головний принцип: сирий фізичний шум ніколи не подається в криптографію напряму.\n"
        "Він проходить валідацію здоров'я (Health Tests), декореляцію, хеш-кондиціювання в пулі\n"
        "і слугує виключно для початкового посіву (Seed) криптографічно стійкого генератора CSPRNG."
    )
    p.append(fitbox(25, 305, W - 50, 65, pipeline_msg, size=11, fill="#ffffff", stroke=LINE, sw=1.4))
    return render(os.path.join(OUT, "entropy-pipeline.svg"), W, H, *p)


# ── 2. Джиттер кільцевого генератора (ROSC) та фазове семплювання ─────────────
def fig_rosc_jitter():
    W, H = 820, 370
    p = []
    p.append(text(W / 2, 26, "Апаратний TRNG: нагромадження фазового джиттера в кільцевому генераторі", size=15, bold=True))

    # Схема ROSC (непарна кількість інверторів)
    inv_box_w, inv_box_h = 500, 110
    inv_x, inv_y = 35, 60
    p.append(rect(inv_x, inv_y, inv_box_w, inv_box_h, fill="#fafbfc", stroke=LINE, sw=1.5))
    p.append(text(inv_x + 15, inv_y + 22, "Кільцевий генератор (ROSC, N=3 непарні інвертори)", size=11, bold=True, anchor="start"))

    # Інвертори
    for idx, (ix, iy) in enumerate([(110, 115), (220, 115), (330, 115)]):
        p.append(textbox(ix, iy, f"NOT {idx+1}", size=11, pad=8, fill="#eff6ff", stroke=NEG, sw=1.5)[0])
        if idx < 2:
            p.append(arrow(ix + 32, iy, ix + 78, iy, color=LINE, sw=1.5))

    # Зворотний зв'язок ROSC
    p.append(line(362, 115, 470, 115, color=LINE, sw=1.5))
    p.append(line(470, 115, 470, 150, color=LINE, sw=1.5))
    p.append(line(470, 150, 60, 150, color=LINE, sw=1.5))
    p.append(line(60, 150, 60, 115, color=LINE, sw=1.5))
    p.append(arrow(60, 115, 78, 115, color=LINE, sw=1.5))

    # Вихід ROSC до D-тригера
    p.append(arrow(470, 115, 570, 115, color=POS, sw=1.8))
    p.append(text(520, 105, "Швидкий сигнал D", size=10, color=POS, bold=True))

    # D-тригер семплювання
    d_x, d_y, d_w, d_h = 575, 75, 100, 80
    p.append(rect(d_x, d_y, d_w, d_h, fill="#fdf4ff", stroke="#9333ea", sw=1.6))
    p.append(text(d_x + d_w / 2, d_y + 20, "D-тригер", size=11, color="#9333ea", bold=True))
    p.append(text(d_x + 15, d_y + 42, "D", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(d_x + 15, d_y + 65, "CLK", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(d_x + d_w - 15, d_y + 42, "Q", size=11, color=INK, bold=True, anchor="end"))

    # Тактовий сигнал семплювання CLK
    p.append(arrow(625, 200, 625, 158, color=FIELD, sw=1.8))
    p.append(text(625, 218, "Опорний CLK", size=10.5, color=FIELD, bold=True))
    p.append(text(625, 234, "(Повільний кварц)", size=9.5, color=MUTED))

    # Вихід Q (випадковий біт)
    p.append(arrow(d_x + d_w + 3, d_y + 38, 770, d_y + 38, color=INK, sw=2.0))
    p.append(text(725, d_y + 28, "Випадковий біт", size=10.5, color=INK, bold=True))

    # Нижній блок: Графік джиттеру
    g_x, g_y, g_w, g_h = 35, 190, 500, 155
    p.append(rect(g_x, g_y, g_w, g_h, fill="#ffffff", stroke=LINE, sw=1.4))
    p.append(text(g_x + 15, g_y + 20, "Нагромадження фазового джиттеру в часі", size=11, bold=True, anchor="start"))

    # Осі
    p.append(arrow(g_x + 40, g_y + 125, g_x + g_w - 20, g_y + 125, color=LINE, sw=1.4))
    p.append(text(g_x + g_w - 15, g_y + 140, "Час t", size=10, color=MUTED))

    # Імпульси з розмитими фронтами (джиттер)
    # Ідеальний фронт (пунктир)
    p.append(line(g_x + 120, g_y + 125, g_x + 120, g_y + 45, color=MUTED, sw=1.2, dash="3,3"))
    p.append(line(g_x + 220, g_y + 125, g_x + 220, g_y + 45, color=MUTED, sw=1.2, dash="3,3"))
    p.append(line(g_x + 340, g_y + 125, g_x + 340, g_y + 45, color=MUTED, sw=1.2, dash="3,3"))

    # Зона невизначеності (розмиття фронтів червоним)
    p.append(rect(g_x + 116, g_y + 45, 8, 80, fill="#fee2e2", stroke="none"))
    p.append(rect(g_x + 213, g_y + 45, 14, 80, fill="#fee2e2", stroke="none"))
    p.append(rect(g_x + 328, g_y + 45, 24, 80, fill="#fee2e2", stroke="none"))

    # Траєкторії сигналу
    p.append(line(g_x + 50, g_y + 125, g_x + 118, g_y + 125, color=POS, sw=1.8))
    p.append(line(g_x + 118, g_y + 125, g_x + 122, g_y + 45, color=POS, sw=1.8))
    p.append(line(g_x + 122, g_y + 45, g_x + 217, g_y + 45, color=POS, sw=1.8))
    p.append(line(g_x + 217, g_y + 45, g_x + 223, g_y + 125, color=POS, sw=1.8))
    p.append(line(g_x + 223, g_y + 125, g_x + 335, g_y + 125, color=POS, sw=1.8))
    p.append(line(g_x + 335, g_y + 125, g_x + 345, g_y + 45, color=POS, sw=1.8))

    p.append(text(g_x + 120, g_y + 38, "Δt₁", size=9.5, color=POS, bold=True))
    p.append(text(g_x + 220, g_y + 38, "Δt₂", size=9.5, color=POS, bold=True))
    p.append(text(g_x + 340, g_y + 38, "Δtₖ ≈ σ√k", size=10, color=POS, bold=True))

    # Пояснення праворуч
    rosc_msg = (
        "Тепловий шум у каналах CMOS-транзисторів\n"
        "флуктує час затримки інвертора t_pd.\n"
        "З кожним періодом невизначеність фази σ_jitter зростає\n"
        "як квадратний корінь із кількості циклів."
    )
    p.append(fitbox(550, 255, 245, 90, rosc_msg, size=10.5, fill="#fffaf0", stroke="#d97706", sw=1.4))
    return render(os.path.join(OUT, "rosc-jitter.svg"), W, H, *p)


# ── 3. Декорелятор Джона фон Неймана (Von Neumann Decorrelator) ────────────────
def fig_von_neumann_extractor():
    W, H = 820, 350
    p = []
    p.append(text(W / 2, 26, "Алгоритм відбілювання Джона фон Неймана (Von Neumann Decorrelator)", size=15, bold=True))

    # Таблиця станів та виходу
    tbl_x, tbl_y, tbl_w, tbl_h = 35, 60, 410, 205
    p.append(rect(tbl_x, tbl_y, tbl_w, tbl_h, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(tbl_x + 15, tbl_y + 22, "Правило обробки некорельованих бітових пар", size=11.5, bold=True, anchor="start"))

    # Заголовок таблиці
    p.append(rect(tbl_x + 15, tbl_y + 35, 380, 26, fill="#f3f4f6", stroke=LINE, sw=1.0))
    p.append(text(tbl_x + 60, tbl_y + 52, "Пара (2k, 2k+1)", size=10.5, bold=True))
    p.append(text(tbl_x + 180, tbl_y + 52, "Ймовірність", size=10.5, bold=True))
    p.append(text(tbl_x + 310, tbl_y + 52, "Дія / Вихід", size=10.5, bold=True))

    rows = [
        ("0  0", "(1 - p)²", "Відкинути (немає виходу)", MUTED, "#ffffff"),
        ("0  1", "(1 - p) · p", "Видати біт 0", FIELD, "#f0fdf4"),
        ("1  0", "p · (1 - p)", "Видати біт 1", FIELD, "#f0fdf4"),
        ("1  1", "p²", "Відкинути (немає виходу)", MUTED, "#ffffff"),
    ]

    for i, (pair, prob, act, col, bg_col) in enumerate(rows):
        ry = tbl_y + 61 + i * 26
        p.append(rect(tbl_x + 15, ry, 380, 26, fill=bg_col, stroke=LINE, sw=0.8))
        p.append(text(tbl_x + 60, ry + 17, pair, size=11, color=INK, bold=True))
        p.append(text(tbl_x + 180, ry + 17, prob, size=10.5, color=INK))
        p.append(text(tbl_x + 310, ry + 17, act, size=10.5, color=col, bold=True))

    p.append(text(tbl_x + 15, tbl_y + 188, "Математичний доказ строгої рівності:", size=10.5, bold=True, anchor="start"))
    p.append(text(tbl_x + 15, tbl_y + 200, "P(01) = (1-p)·p = p·(1-p) = P(10) ⇒ P(Вихід=0) = P(Вихід=1) = 0.5", size=10.5, color=FIELD, bold=True, anchor="start"))

    # Схема потоку праворуч
    flow_x, flow_y, flow_w, flow_h = 470, 60, 315, 205
    p.append(rect(flow_x, flow_y, flow_w, flow_h, fill="#fafbfc", stroke=LINE, sw=1.5))
    p.append(text(flow_x + flow_w / 2, flow_y + 22, "Перетворення бітового потоку", size=11.5, bold=True))

    p.append(textbox(flow_x + flow_w / 2, flow_y + 55, "Зсунутий вхідний потік (p = 0.65)\n1 1  0 1  0 0  1 0  1 1  0 1", size=10, pad=6, fill="#fef2f2", stroke=POS, sw=1.2)[0])
    p.append(arrow(flow_x + flow_w / 2, flow_y + 80, flow_x + flow_w / 2, flow_y + 105, color=LINE, sw=1.6))
    p.append(text(flow_x + flow_w / 2 + 75, flow_y + 95, "Фільтр пар", size=9.5, color=MUTED))

    p.append(textbox(flow_x + flow_w / 2, flow_y + 125, "Розпізнані пари:\n[11:✕] [01:→0] [00:✕] [10:→1] [11:✕] [01:→0]", size=10, pad=6, fill="#fffbeb", stroke="#d97706", sw=1.2)[0])
    p.append(arrow(flow_x + flow_w / 2, flow_y + 150, flow_x + flow_w / 2, flow_y + 172, color=LINE, sw=1.6))

    p.append(textbox(flow_x + flow_w / 2, flow_y + 188, "Ідеально збалансований потік:  0  1  0", size=10.5, pad=6, fill="#f0fdf4", stroke=FIELD, sw=1.4, bold=True)[0])

    # Нижній висновок
    vn_msg = (
        "Ціна декорелятора Фон Неймана: вихідна швидкість падає у 4–8 разів (пропускна здатність E ≤ 0.25).\n"
        "Алгоритм ефективно знищує постійний зсув частоти 0/1 (Bias), проте не рятує від наявності\n"
        "міжбітової автокореляції — для її усунення обов'язкове криптографічне хеш-кондиціювання."
    )
    p.append(fitbox(35, 275, W - 70, 65, vn_msg, size=11, fill="#ffffff", stroke=LINE, sw=1.4))
    return render(os.path.join(OUT, "von-neumann-extractor.svg"), W, H, *p)


# ── 4. Захоплення джиттеру несинхронізованих таймерів (Dual-Timer Jitter) ──────
def fig_dual_timer_jitter():
    W, H = 820, 360
    p = []
    p.append(text(W / 2, 26, "Екстракція ентропії з дрейфу незалежних генераторів (HSE кварц vs LSI RC)", size=15, bold=True))

    # Ліва колонка: Швидкий таймер (Кварц HSE)
    t1_x, t1_y, t1_w, t1_h = 35, 60, 340, 110
    p.append(rect(t1_x, t1_y, t1_w, t1_h, fill="#eff6ff", stroke=NEG, sw=1.5))
    p.append(text(t1_x + 15, t1_y + 22, "Швидкий таймер (Timer 1)", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(t1_x + 15, t1_y + 44, "• Джерело: Кварцовий резонатор (HSE)", size=10.5, color=INK, anchor="start"))
    p.append(text(t1_x + 15, t1_y + 64, "• Частота: f_fast = 168 МГц (стабільність 10 ppm)", size=10.5, color=INK, anchor="start"))
    p.append(text(t1_x + 15, t1_y + 86, "• Лічильник: 32-бітний регістр CNT зростає що 5.95 нс", size=10, color=MUTED, anchor="start"))

    # Права колонка: Повільний генератор (Внутрішній RC LSI)
    t2_x, t2_y, t2_w, t2_h = 445, 60, 340, 110
    p.append(rect(t2_x, t2_y, t2_w, t2_h, fill="#fef2f2", stroke=POS, sw=1.5))
    p.append(text(t2_x + 15, t2_y + 22, "Повільний релаксатор (LSI / Watchdog)", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(t2_x + 15, t2_y + 44, "• Джерело: Внутрішній RC-генератор (LSI)", size=10.5, color=INK, anchor="start"))
    p.append(text(t2_x + 15, t2_y + 64, "• Частота: f_slow ≈ 32 кГц (термодрейф ~2–5%)", size=10.5, color=INK, anchor="start"))
    p.append(text(t2_x + 15, t2_y + 86, "• Подія: генерує імпульс Input Capture / переривання", size=10, color=MUTED, anchor="start"))

    # Центральний блок: Регістр захоплення CCR
    ccr_x, ccr_y, ccr_w, ccr_h = 240, 195, 340, 65
    p.append(rect(ccr_x, ccr_y, ccr_w, ccr_h, fill="#f0fdf4", stroke=FIELD, sw=1.6))
    p.append(text(ccr_x + ccr_w / 2, ccr_y + 20, "Регістр захоплення (Input Capture CCR)", size=11.5, color=FIELD, bold=True))
    p.append(text(ccr_x + ccr_w / 2, ccr_y + 40, "Запис поточного значення швидкого лічильника CNT", size=10, color=INK))
    p.append(text(ccr_x + ccr_w / 2, ccr_y + 54, "за кожним переднім фронтом повільного RC", size=9.5, color=MUTED))

    # З'єднувальні стрілки
    p.append(arrow(t1_x + t1_w / 2, t1_y + t1_h + 3, ccr_x + 60, ccr_y - 4, color=NEG, sw=1.8))
    p.append(arrow(t2_x + t2_w / 2, t2_y + t2_h + 3, ccr_x + ccr_w - 60, ccr_y - 4, color=POS, sw=1.8))
    p.append(text(140, 185, "Потік лічби CNT", size=10, color=NEG, bold=True))
    p.append(text(620, 185, "Фронт захоплення", size=10, color=POS, bold=True))

    # Стрілка вниз до бітової маски
    p.append(arrow(ccr_x + ccr_w / 2, ccr_y + ccr_h + 3, ccr_x + ccr_w / 2, 280, color=LINE, sw=1.8))

    # Розбивка 32-бітного слова
    w_x, w_y, w_w, w_h = 160, 285, 500, 60
    p.append(rect(w_x, w_y, w_w, w_h, fill="#ffffff", stroke=LINE, sw=1.4))
    # Старші біти (детерміновані)
    p.append(rect(w_x + 10, w_y + 10, 360, 40, fill="#f3f4f6", stroke=MUTED, sw=1.0))
    p.append(text(w_x + 190, w_y + 26, "Старші розряди [31..2]: детермінована база", size=10, color=MUTED, bold=True))
    p.append(text(w_x + 190, w_y + 42, "Визначаються середнім відношенням f_fast / f_slow", size=9.5, color=MUTED))

    # Молодші біти (ентропія)
    p.append(rect(w_x + 380, w_y + 10, 110, 40, fill="#fee2e2", stroke=POS, sw=1.5))
    p.append(text(w_x + 435, w_y + 26, "Біти [1..0] LSB", size=10.5, color=POS, bold=True))
    p.append(text(w_x + 435, w_y + 42, "Фазовий джиттер!", size=9.5, color=POS, bold=True))

    return render(os.path.join(OUT, "dual-timer-jitter.svg"), W, H, *p)


if __name__ == "__main__":
    fig_entropy_pipeline()
    fig_rosc_jitter()
    fig_von_neumann_extractor()
    fig_dual_timer_jitter()
    print("All figures generated successfully.")
