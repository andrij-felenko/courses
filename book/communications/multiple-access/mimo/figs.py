# -*- coding: utf-8 -*-
"""Фігури до теми «MIMO (Multiple-Input Multiple-Output)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори для MIMO
ANT_TX = "#2457d6"    # передавальні антени
ANT_RX = "#c0392b"    # приймальні антени
CHANNEL = "#8e44ad"   # матриця каналу та промені
DATA_A = "#27ae60"    # потік даних 1
DATA_B = "#e67e22"    # потік даних 2
BORDER = INK

# ── 1. Матрична модель радіоканалу y = Hx + n ───────────────────────────────
def fig_mimo_channel_matrix():
    W, H = 780, 380
    f = [text(W / 2, 26, "Матрична модель MIMO-радіоканалу: y = H·x + n", size=15, bold=True)]

    # Ліва частина: Вектор передавача x (N_t антен)
    f.append(rect(25, 60, 160, 240, fill="#f4f6f8", stroke=BORDER, sw=1.5, rx=6))
    f.append(text(105, 85, "Передавач (Tx)", size=13, bold=True, color=ANT_TX))
    f.append(text(105, 105, "N_t антен", size=11, color=MUTED))

    # Антени передавача
    tx_y = [140, 190, 260]
    for i, y in enumerate(tx_y):
        lbl = "x_%d" % (i + 1) if i < 2 else "x_{N_t}"
        f.append(rect(40, y - 16, 50, 32, fill="#ffffff", stroke=ANT_TX, sw=1.5, rx=4))
        f.append(text(65, y + 5, lbl, size=12, bold=True, color=ANT_TX))
        # Символ антени
        f.append(line(90, y, 120, y, color=ANT_TX, sw=2))
        f.append(line(120, y - 12, 120, y + 12, color=ANT_TX, sw=2))
        f.append(line(120, y, 135, y - 10, color=ANT_TX, sw=1.5))
        f.append(line(120, y, 135, y + 10, color=ANT_TX, sw=1.5))

    f.append(text(105, 230, "⋮", size=16, bold=True, color=MUTED))

    # Центральна частина: Матриця каналу H (розсіювання у просторі)
    f.append(rect(230, 60, 310, 240, fill="#fdfefe", stroke=CHANNEL, sw=1.5, rx=8))
    f.append(text(385, 85, "Багатопроменеве середовище H", size=13, bold=True, color=CHANNEL))
    f.append(text(385, 105, "Розмірність: N_r × N_t", size=11, color=MUTED))

    # Промені розсіювання між антенами
    rx_y = [140, 190, 260]
    f.append(line(140, 140, 600, 140, color="#3498db", sw=1.8, dash="4,2"))
    f.append(line(140, 140, 600, 190, color=CHANNEL, sw=1.5, dash="3,3"))
    f.append(line(140, 190, 600, 140, color=CHANNEL, sw=1.5, dash="3,3"))
    f.append(line(140, 190, 600, 190, color="#e74c3c", sw=1.8, dash="4,2"))

    # Текстові підписи коефіцієнтів каналу всередині матриці
    f.append(rect(280, 130, 210, 120, fill="#f9f9fb", stroke=MUTED, sw=1, rx=4))
    f.append(text(385, 155, "H = [ h₁₁  h₁₂  …  h₁_Nt ]", size=11, bold=True, color=CHANNEL))
    f.append(text(385, 178, "    [ h₂₁  h₂₂  …  h₂_Nt ]", size=11, bold=True, color=CHANNEL))
    f.append(text(385, 200, "    [  ⋮    ⋮   ⋱    ⋮   ]", size=11, bold=True, color=MUTED))
    f.append(text(385, 225, "    [ h_Nr1 …   …  h_NrNt]", size=11, bold=True, color=CHANNEL))

    # Права частина: Приймач y (N_r антен)
    f.append(rect(585, 60, 170, 240, fill="#f4f6f8", stroke=BORDER, sw=1.5, rx=6))
    f.append(text(670, 85, "Приймач (Rx)", size=13, bold=True, color=ANT_RX))
    f.append(text(670, 105, "N_r антен + шум n", size=11, color=MUTED))

    # Антени приймача
    for i, y in enumerate(rx_y):
        lbl = "y_%d" % (i + 1) if i < 2 else "y_{N_r}"
        # Символ антени
        f.append(line(600, y - 12, 600, y + 12, color=ANT_RX, sw=2))
        f.append(line(600, y, 615, y, color=ANT_RX, sw=2))
        f.append(line(600, y - 10, 585, y, color=ANT_RX, sw=1.5))
        f.append(line(600, y + 10, 585, y, color=ANT_RX, sw=1.5))

        f.append(rect(625, y - 16, 50, 32, fill="#ffffff", stroke=ANT_RX, sw=1.5, rx=4))
        f.append(text(650, y + 5, lbl, size=12, bold=True, color=ANT_RX))
        f.append(text(710, y + 5, "+ n_%d" % (i + 1) if i < 2 else "+ n_{N_r}", size=11, color=MUTED))

    f.append(text(650, 230, "⋮", size=16, bold=True, color=MUTED))

    # Інформаційна панель унизу
    f.append(fitbox(25, 312, 730, 55,
                    "Рівняння сигналу: y = H·x + n, де кожне h_ij — комплексний коефіцієнт передачі з Tx_j на Rx_i.\n"
                    "Багатопроменеве розсіювання створює незалежні коефіцієнти h_ij, забезпечуючи високий ранг матриці rank(H).",
                    size=11, fill="#ffffff", stroke=BORDER))

    render(os.path.join(IMG, "mimo-channel-matrix.svg"), W, H, *f)


# ── 2. Просторове мультиплексування проти просторового рознесення ───────────
def fig_spatial_multiplexing_vs_diversity():
    W, H = 780, 380
    f = [text(W / 2, 26, "Просторове мультиплексування (Швидкість) проти Рознесення (Надійність)", size=15, bold=True)]

    # Ліва панель: Просторово-часове рознесення (Diversity)
    f.append(rect(20, 50, 360, 250, fill="#fcfcfd", stroke=BORDER, sw=1.5, rx=8))
    f.append(text(200, 75, "Просторове рознесення (Diversity)", size=13, bold=True, color=POS))
    f.append(text(200, 95, "Ціль: боротьба із завмираннями, стійкість", size=11, color=MUTED))

    # Схема передачі однакового потоку s1
    f.append(rect(40, 130, 70, 40, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    f.append(text(75, 155, "Символ s₁", size=11, bold=True, color=POS))

    f.append(arrow(110, 140, 160, 120, color=POS, sw=1.5))
    f.append(arrow(110, 160, 160, 180, color=POS, sw=1.5))

    f.append(rect(160, 105, 55, 30, fill="#ffffff", stroke=ANT_TX, sw=1.5, rx=4))
    f.append(text(187, 125, "Tx₁: s₁", size=11, bold=True, color=ANT_TX))

    f.append(rect(160, 165, 55, 30, fill="#ffffff", stroke=ANT_TX, sw=1.5, rx=4))
    f.append(text(187, 185, "Tx₂: s₁*", size=11, bold=True, color=ANT_TX))

    f.append(arrow(215, 120, 280, 140, color=CHANNEL, sw=1.5))
    f.append(arrow(215, 180, 280, 160, color=CHANNEL, sw=1.5))

    f.append(rect(280, 130, 80, 40, fill="#ffffff", stroke=ANT_RX, sw=1.5, rx=4))
    f.append(text(320, 150, "Комбайнер", size=11, bold=True, color=ANT_RX))
    f.append(text(320, 165, "MRC / STBC", size=9.5, color=MUTED))

    f.append(fitbox(30, 215, 340, 75,
                    "• Один потік даних дублюється у просторі/часі.\n"
                    "• Швидкість передачі R = 1 символ/такт (не зростає).\n"
                    "• Порядок рознесення d = N_t · N_r: ймовірність глибокого завмирання падає як SNR^(−d).",
                    size=10.5, fill="#fdecea", stroke=POS))

    # Права панель: Просторове мультиплексування (Spatial Multiplexing)
    f.append(rect(400, 50, 360, 250, fill="#fcfcfd", stroke=BORDER, sw=1.5, rx=8))
    f.append(text(580, 75, "Просторове мультиплексування (Spatial Multiplexing)", size=13, bold=True, color=DATA_A))
    f.append(text(580, 95, "Ціль: кратна пропускна здатність на одній частоті", size=11, color=MUTED))

    # Схема передачі двох незалежних потоків s1 та s2
    f.append(rect(420, 110, 60, 30, fill="#e8f8f5", stroke=DATA_A, sw=1.5, rx=4))
    f.append(text(450, 130, "Потік s₁", size=11, bold=True, color=DATA_A))

    f.append(rect(420, 160, 60, 30, fill="#fef5e7", stroke=DATA_B, sw=1.5, rx=4))
    f.append(text(450, 180, "Потік s₂", size=11, bold=True, color=DATA_B))

    f.append(arrow(480, 125, 520, 125, color=DATA_A, sw=1.8))
    f.append(arrow(480, 175, 520, 175, color=DATA_B, sw=1.8))

    f.append(rect(520, 110, 55, 30, fill="#ffffff", stroke=ANT_TX, sw=1.5, rx=4))
    f.append(text(547, 130, "Tx₁: s₁", size=11, bold=True, color=DATA_A))

    f.append(rect(520, 160, 55, 30, fill="#ffffff", stroke=ANT_TX, sw=1.5, rx=4))
    f.append(text(547, 180, "Tx₂: s₂", size=11, bold=True, color=DATA_B))

    # Перехресні стрілки в ефірі
    f.append(arrow(575, 125, 640, 125, color=DATA_A, sw=1.5))
    f.append(arrow(575, 125, 640, 175, color=DATA_A, sw=1.2))
    f.append(arrow(575, 175, 640, 125, color=DATA_B, sw=1.2))
    f.append(arrow(575, 175, 640, 175, color=DATA_B, sw=1.5))

    f.append(rect(640, 110, 105, 80, fill="#ffffff", stroke=ANT_RX, sw=1.5, rx=4))
    f.append(text(692, 135, "MIMO Детектор", size=11, bold=True, color=ANT_RX))
    f.append(text(692, 155, "ZF / MMSE / ML", size=10, bold=True, color=CHANNEL))
    f.append(text(692, 175, "→ ŝ₁, ŝ₂", size=11, bold=True, color=INK))

    f.append(fitbox(410, 215, 340, 75,
                    "• Незалежні потоки передаються паралельно на тій самій смузі.\n"
                    "• Швидкість передачі R = min(N_t, N_r) символів/такт.\n"
                    "• Вимагає високого SNR та некорельованого каналу rank(H) = min(N_t, N_r).",
                    size=10.5, fill="#e8f8f5", stroke=DATA_A))

    # Узагальнення внизу
    f.append(fitbox(20, 310, 740, 58,
                    "Компроміс Чженя-Це (Zheng-Tse Diversity-Multiplexing Tradeoff):\n"
                    "Неможливо одночасно досягти максимального рознесення d_max = N_t · N_r та максимального мультиплексування r_max = min(N_t, N_r).\n"
                    "Адаптивні системи перемикають режим: на межі стільника (низький SNR) — рознесення, біля станції (високий SNR) — мультиплексування.",
                    size=10.5, fill="#ffffff", stroke=BORDER))

    render(os.path.join(IMG, "spatial-multiplexing-vs-diversity.svg"), W, H, *f)


# ── 3. Схема Аламоуті 2x1 та 2x2: Просторове кодування ─────────────────────
def fig_alamouti_scheme():
    W, H = 780, 380
    f = [text(W / 2, 26, "Просторово-часовий блоковий код Аламоуті (STBC 2×1 та 2×2)", size=15, bold=True)]

    # Ліва частина: Матриця передачі у часі
    f.append(rect(20, 50, 260, 245, fill="#fcfcfd", stroke=BORDER, sw=1.5, rx=8))
    f.append(text(150, 75, "Передавач Аламоуті (2 Tx)", size=13, bold=True, color=ANT_TX))

    # Таблиця передачі
    f.append(rect(35, 100, 230, 110, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    f.append(line(35, 135, 265, 135, color=MUTED, sw=1))
    f.append(line(35, 175, 265, 175, color=MUTED, sw=1))
    f.append(line(115, 100, 115, 210, color=MUTED, sw=1))
    f.append(line(190, 100, 190, 210, color=MUTED, sw=1))

    f.append(text(75, 122, "Час", size=11, bold=True, color=MUTED))
    f.append(text(152, 122, "Антена Tx₁", size=11, bold=True, color=ANT_TX))
    f.append(text(227, 122, "Антена Tx₂", size=11, bold=True, color=ANT_TX))

    f.append(text(75, 158, "Такт t₁", size=11, bold=True, color=INK))
    f.append(text(152, 158, "s₁", size=13, bold=True, color=DATA_A))
    f.append(text(227, 158, "s₂", size=13, bold=True, color=DATA_B))

    f.append(text(75, 195, "Такт t₂", size=11, bold=True, color=INK))
    f.append(text(152, 195, "−s₂*", size=13, bold=True, color=DATA_B))
    f.append(text(227, 195, "s₁*", size=13, bold=True, color=DATA_A))

    f.append(fitbox(30, 220, 240, 65,
                    "Властивість матриці S:\n"
                    "Рядки і стовпці взаємно ортогональні: S · Sᴴ = (|s₁|² + |s₂|²) · I₂\n"
                    "Повна швидкість R = 1 (2 символи за 2 такти).",
                    size=10, fill="#ffffff", stroke=ANT_TX))

    # Центральна частина: Ефір із коефіцієнтами h1, h2
    f.append(rect(295, 50, 170, 245, fill="#fdfefe", stroke=CHANNEL, sw=1.5, rx=8))
    f.append(text(380, 75, "Канал 2×1", size=13, bold=True, color=CHANNEL))

    f.append(circle(330, 125, 14, fill="#ffffff", stroke=ANT_TX, sw=1.5))
    f.append(text(330, 130, "Tx₁", size=10.5, bold=True, color=ANT_TX))

    f.append(circle(330, 185, 14, fill="#ffffff", stroke=ANT_TX, sw=1.5))
    f.append(text(330, 190, "Tx₂", size=10.5, bold=True, color=ANT_TX))

    f.append(circle(430, 155, 14, fill="#ffffff", stroke=ANT_RX, sw=1.5))
    f.append(text(430, 160, "Rx₁", size=10.5, bold=True, color=ANT_RX))

    f.append(arrow(345, 125, 415, 150, color=CHANNEL, sw=1.8))
    f.append(text(375, 130, "h₁", size=12, bold=True, color=CHANNEL))

    f.append(arrow(345, 185, 415, 160, color=CHANNEL, sw=1.8))
    f.append(text(375, 182, "h₂", size=12, bold=True, color=CHANNEL))

    f.append(fitbox(305, 215, 150, 70,
                    "Прийняті сигнали:\n"
                    "y₁ = h₁s₁ + h₂s₂ + n₁\n"
                    "y₂ = −h₁s₂* + h₂s₁* + n₂",
                    size=10.5, fill="#ffffff", stroke=CHANNEL))

    # Права частина: Ортогональне лінійне детектування
    f.append(rect(480, 50, 280, 245, fill="#fcfcfd", stroke=BORDER, sw=1.5, rx=8))
    f.append(text(620, 75, "Лінійний декодер Аламоуті", size=13, bold=True, color=ANT_RX))

    f.append(fitbox(490, 100, 260, 105,
                    "Матричне перемноження на H_effᴴ:\n\n"
                    "ŝ₁ = h₁*·y₁ + h₂·y₂* = (|h₁|² + |h₂|²)·s₁ + ñ₁\n"
                    "ŝ₂ = h₂*·y₁ − h₁·y₂* = (|h₁|² + |h₂|²)·s₂ + ñ₂\n\n"
                    "Перехресна інтерференція повністю зникає!",
                    size=10.5, fill="#f4f6f8", stroke=BORDER))

    f.append(fitbox(490, 215, 260, 70,
                    "Головний результат:\n"
                    "• Не потрібен зворотний зв'язок (CSI на передавачі не вимагається).\n"
                    "• Повний порядок рознесення d = 2 без матричного обернення.",
                    size=10.5, fill="#eafaf1", stroke=FIELD))

    # Підсумок унизу
    f.append(fitbox(20, 308, 740, 60,
                    "Схема Аламоуті (IEEE 802.11n, LTE, WCDMA) — єдиний ортогональний просторово-часовий код для комплексних сигналів зі швидкістю R = 1.\n"
                    "Для систем 2×2 з двома антена приймача рознесення зростає до d = 4, а результуючий SNR масштабується як (|h₁₁|² + |h₁₂|² + |h₂₁|² + |h₂₂|²).",
                    size=10.5, fill="#ffffff", stroke=BORDER))

    render(os.path.join(IMG, "alamouti-scheme.svg"), W, H, *f)


# ── 4. SVD-декомпозиція та розподіл потужності Water-filling ────────────────
def fig_svd_eigenmode_waterfilling():
    W, H = 780, 380
    f = [text(W / 2, 26, "SVD-декомпозиція каналу та розподіл потужності Water-filling", size=15, bold=True)]

    # Ліва частина: SVD факторизація H = U · Σ · Vᴴ
    f.append(rect(20, 50, 360, 245, fill="#fcfcfd", stroke=BORDER, sw=1.5, rx=8))
    f.append(text(200, 75, "SVD-факторизація: H = U · Σ · Vᴴ", size=13, bold=True, color=CHANNEL))

    # Схема прекодера, каналу та посткодера
    f.append(rect(35, 105, 75, 45, fill="#ebf5fb", stroke=ANT_TX, sw=1.5, rx=4))
    f.append(text(72, 125, "Прекодер V", size=11, bold=True, color=ANT_TX))
    f.append(text(72, 140, "x = V · s", size=10, color=MUTED))

    f.append(arrow(110, 127, 150, 127, color=INK, sw=1.5))

    f.append(rect(150, 105, 80, 45, fill="#f5eef8", stroke=CHANNEL, sw=1.5, rx=4))
    f.append(text(190, 125, "Канал H", size=11, bold=True, color=CHANNEL))
    f.append(text(190, 140, "y = Hx + n", size=10, color=MUTED))

    f.append(arrow(230, 127, 270, 127, color=INK, sw=1.5))

    f.append(rect(270, 105, 95, 45, fill="#fbeee6", stroke=ANT_RX, sw=1.5, rx=4))
    f.append(text(317, 125, "Посткодер Uᴴ", size=11, bold=True, color=ANT_RX))
    f.append(text(317, 140, "ỹ = Uᴴ · y", size=10, color=MUTED))

    f.append(fitbox(35, 165, 330, 115,
                    "Розв'язка на r незалежних SISO-підканалів:\n"
                    "ỹ = Uᴴ(H·V·s + n) = Uᴴ(U·Σ·Vᴴ·V·s + n) = Σ·s + ñ\n\n"
                    "де матриця Σ = diag(σ₁, σ₂, …, σ_r) містить сингулярні числа каналу.\n"
                    "Кожен потік s_i передається без перехресних завад: ỹ_i = σ_i · s_i + ñ_i.",
                    size=10.5, fill="#ffffff", stroke=CHANNEL))

    # Права частина: Water-filling (Заповнення водою)
    f.append(rect(400, 50, 360, 245, fill="#fcfcfd", stroke=BORDER, sw=1.5, rx=8))
    f.append(text(580, 75, "Розподіл потужності Water-filling", size=13, bold=True, color=POS))

    # Діаграма судин Water-filling
    # Рівень води (му)
    f.append(line(420, 120, 740, 120, color="#2980b9", sw=2, dash="4,2"))
    f.append(text(710, 112, "Рівень μ", size=11, bold=True, color="#2980b9"))

    # Стовпчики 1, 2, 3, 4
    # Підканал 1 (сильний, висока сигма1, низький рівень шуму N0/sigma1^2)
    f.append(rect(435, 170, 65, 70, fill="#d5dbdb", stroke=BORDER, sw=1.2)) # Дно
    f.append(rect(435, 120, 65, 50, fill="#aed6f1", stroke="#2980b9", sw=1.2)) # Вода (P1)
    f.append(text(467, 145, "P₁", size=12, bold=True, color="#1b4f72"))
    f.append(text(467, 205, "N₀/σ₁²", size=10, bold=True, color=INK))
    f.append(text(467, 255, "Мода 1", size=10.5, bold=True, color=FIELD))

    # Підканал 2 (середній)
    f.append(rect(515, 145, 65, 95, fill="#d5dbdb", stroke=BORDER, sw=1.2))
    f.append(rect(515, 120, 65, 25, fill="#aed6f1", stroke="#2980b9", sw=1.2))
    f.append(text(547, 133, "P₂", size=11, bold=True, color="#1b4f72"))
    f.append(text(547, 190, "N₀/σ₂²", size=10, bold=True, color=INK))
    f.append(text(547, 255, "Мода 2", size=10.5, bold=True, color=FIELD))

    # Підканал 3 (слабкий, на межі)
    f.append(rect(595, 195, 65, 45, fill="#d5dbdb", stroke=BORDER, sw=1.2))
    f.append(text(627, 220, "N₀/σ₃²", size=10, bold=True, color=INK))
    f.append(text(627, 255, "Мода 3", size=10.5, bold=True, color=MUTED))

    # Підканал 4 (дуже слабкий, N0/sigma4^2 > mu -> P4 = 0 вимкнено)
    f.append(rect(675, 95, 65, 145, fill="#fadbd8", stroke=POS, sw=1.2))
    f.append(text(707, 160, "N₀/σ₄² > μ", size=9.5, bold=True, color=POS))
    f.append(text(707, 180, "P₄ = 0", size=11, bold=True, color=POS))
    f.append(text(707, 255, "Вимкнено", size=10.5, bold=True, color=POS))

    # Пояснення правила water-filling внизу
    f.append(fitbox(20, 308, 740, 60,
                    "Правило Water-filling оптимізує ємність Шеннона C = ∑ log₂(1 + P_i · σ_i² / N₀) за умови ∑ P_i ≤ P_total.\n"
                    "Більше потужності виділяється у власні моди з високим підсиленням σ_i². Слабкі моди з великим рівнем шуму (N₀/σ_i² ≥ μ) не живляться взагалі.",
                    size=10.5, fill="#ffffff", stroke=BORDER))

    render(os.path.join(IMG, "svd-eigenmode-waterfilling.svg"), W, H, *f)


# ── 5. Формування променя (Beamforming) та Massive MIMO ─────────────────────
def fig_beamforming_and_massive_mimo():
    W, H = 780, 410
    f = [text(W / 2, 26, "Формування променя (Beamforming), MU-MIMO та концепція Massive MIMO", size=15, bold=True)]

    # Ліва панель: Цифровий та аналоговий Beamforming
    f.append(rect(20, 50, 360, 265, fill="#fcfcfd", stroke=BORDER, sw=1.5, rx=8))
    f.append(text(200, 72, "Формування діаграми спрямованості", size=13, bold=True, color=ANT_TX))
    f.append(text(200, 88, "Когерентне додавання фаз антенної решітки", size=10.5, color=MUTED))

    # Масив антен Tx
    for i in range(4):
        ay = 110 + i * 28
        f.append(rect(30, ay - 9, 36, 18, fill="#ebf5fb", stroke=ANT_TX, sw=1.2, rx=3))
        f.append(text(48, ay + 4, "w_%d" % (i + 1), size=9.5, bold=True, color=ANT_TX))
        f.append(line(66, ay, 84, ay, color=ANT_TX, sw=1.5))
        f.append(line(84, ay - 7, 84, ay + 7, color=ANT_TX, sw=1.5))

    # Сфокусований промінь на абонента
    f.append('<path d="M 90 150 Q 200 105 310 120 Q 200 195 90 150 Z" fill="#d5f5e3" stroke="#27ae60" stroke-width="1.5"/>')
    f.append(text(200, 145, "Головний промінь (Beam)", size=10.5, bold=True, color=FIELD))
    f.append(text(200, 160, "Підсилення ~ N антен", size=9.5, color=FIELD))

    # Нуль у бік завади
    f.append(line(90, 150, 230, 200, color=POS, sw=1.5, dash="3,2"))
    f.append(text(275, 205, "Просторовий нуль (Null)", size=10, bold=True, color=POS))

    f.append(circle(325, 120, 12, fill="#ffffff", stroke=FIELD, sw=2))
    f.append(text(325, 124, "UE", size=10, bold=True, color=FIELD))

    f.append(fitbox(30, 222, 340, 85,
                    "Керування вектором ваг w = [e^(jθ₁), e^(jθ₂), …]:\n"
                    "• Конструктивна інтерференція у напрямку корисного сигналу (+10·log₁₀(N) дБ).\n"
                    "• Деструктивна інтерференція (нули) у напрямку інтерферентів.",
                    size=10, fill="#ffffff", stroke=ANT_TX))

    # Права панель: Massive MIMO у 5G NR
    f.append(rect(400, 50, 360, 265, fill="#fcfcfd", stroke=BORDER, sw=1.5, rx=8))
    f.append(text(580, 72, "Massive MIMO (64T64R / 128T128R)", size=13, bold=True, color=CHANNEL))
    f.append(text(580, 88, "Багатокористувацький режим (MU-MIMO) у 5G NR", size=10.5, color=MUTED))

    # Велика антена решітка БС (Massive Array)
    f.append(rect(415, 105, 55, 80, fill="#5d6d7e", stroke=BORDER, sw=1.5, rx=4))
    for r in range(4):
        for c in range(3):
            f.append(circle(426 + c * 16, 116 + r * 18, 3.5, fill="#ffffff", stroke=ANT_TX, sw=1))
    f.append(text(442, 200, "64T64R", size=10, bold=True, color=INK))

    # Промені до декількох абонентів (MU-MIMO)
    # Промінь 1 до UE1
    f.append('<path d="M 475 130 Q 560 100 670 110 Q 560 145 475 130 Z" fill="#ebf5fb" stroke="#2980b9" stroke-width="1.2"/>')
    f.append(circle(685, 110, 9, fill="#ffffff", stroke="#2980b9", sw=1.5))
    f.append(text(685, 113, "UE₁", size=9, bold=True, color="#2980b9"))

    # Промінь 2 до UE2
    f.append('<path d="M 475 145 Q 560 150 670 155 Q 560 180 475 145 Z" fill="#fef5e7" stroke="#e67e22" stroke-width="1.2"/>')
    f.append(circle(685, 155, 9, fill="#ffffff", stroke="#e67e22", sw=1.5))
    f.append(text(685, 158, "UE₂", size=9, bold=True, color="#e67e22"))

    # Промінь 3 до UE3
    f.append('<path d="M 475 160 Q 550 190 650 200 Q 550 215 475 160 Z" fill="#e8f8f5" stroke="#27ae60" stroke-width="1.2"/>')
    f.append(circle(665, 200, 9, fill="#ffffff", stroke="#27ae60", sw=1.5))
    f.append(text(665, 203, "UE₃", size=9, bold=True, color="#27ae60"))

    f.append(fitbox(410, 222, 340, 85,
                    "Ефекти Massive MIMO:\n"
                    "1. Асимптотична ортогональність каналів: (Hᴴ·H)/M → I при M → ∞.\n"
                    "2. Затвердіння каналу (Channel Hardening): швидкі завмирання зникають.\n"
                    "3. Простий лінійний прекодинг (ZF/MRT) досягає оптимуму.",
                    size=10, fill="#ffffff", stroke=CHANNEL))

    # Загальний підсумок унизу
    f.append(fitbox(20, 325, 740, 72,
                    "Massive MIMO усуває внутрішньостільникову інтерференцію виключно просторовою фільтрацією в цифровій базовій смузі.\n"
                    "Стандарти Wi-Fi 6/7 (802.11ax/be) та 5G NR використовують явний та неявний зворотний зв'язок (SRS reciprocity в TDD) для побудови прекодерів.",
                    size=10.5, fill="#ffffff", stroke=BORDER))

    render(os.path.join(IMG, "beamforming-and-massive-mimo.svg"), W, H, *f)


if __name__ == "__main__":
    fig_mimo_channel_matrix()
    fig_spatial_multiplexing_vs_diversity()
    fig_alamouti_scheme()
    fig_svd_eigenmode_waterfilling()
    fig_beamforming_and_massive_mimo()
    print("OK: 5 figures created ->", IMG)
