# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Принцип оптичного гетеродинного детектування
# ═══════════════════════════════════════════════════════════════════════════
def fig_heterodyne_principle():
    W, H = 720, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Схема та принцип оптичного гетеродинного детектування', 16, INK, 'middle', bold=True))

    # Джерело слабкого сигналу (сигнальний лазер)
    f.append(rect(40, 60, 140, 55, fill='#eff6ff', stroke=POS, sw=1.8, rx=6))
    f.append(text(110, 84, 'Сигнальний лазер', 11, POS, 'middle', bold=True))
    f.append(text(110, 101, 'E⛛(t), частота f⛛', 10, INK, 'middle'))

    # Джерело гетеродина (Local Oscillator)
    f.append(rect(230, 175, 140, 55, fill='#fef2f2', stroke=NEG, sw=1.8, rx=6))
    f.append(text(300, 199, 'Гетеродин (LO)', 11, NEG, 'middle', bold=True))
    f.append(text(300, 216, 'Eₗ(t), частота fₗ', 10, INK, 'middle'))

    # Світлодільник (Beam Splitter 50:50)
    bs_cx, bs_cy = 300, 875 // 10  # 87.5
    f.append(rect(bs_cx - 25, bs_cy - 25, 50, 50, fill='#f1f5f9', stroke=INK, sw=1.5, rx=2))
    f.append(line(bs_cx - 25, bs_cy + 25, bs_cx + 25, bs_cy - 25, color=FIELD, sw=2, dash='4,3'))
    f.append(text(bs_cx, bs_cy - 30, 'Світлодільник (50:50)', 10, INK, 'middle', bold=True))

    # Промені
    # Сигнальний промінь входить зліва
    f.append(arrow(180, bs_cy, bs_cx - 25, bs_cy, color=POS, sw=2.2))
    f.append(text(215, bs_cy - 8, 'P⛛ (слабкий)', 9, POS, 'middle', bold=True))

    # Гетеродинний промінь входить знизу
    f.append(arrow(300, 175, 300, bs_cy + 25, color=NEG, sw=2.2))
    f.append(text(342, 145, 'Pₗ (потужний)', 9, NEG, 'start', bold=True))

    # Змішаний промінь прямує вправо до фотодетектора
    f.append(arrow(bs_cx + 25, bs_cy, 460, bs_cy, color=FIELD, sw=2.5))
    f.append(text(392, bs_cy - 8, 'E⛛(t) + Eₗ(t)', 10, FIELD, 'middle', bold=True))

    # Фотодетектор (Квадратичний змішувач)
    f.append(rect(460, bs_cy - 27, 95, 55, fill='#ecfdf5', stroke=FIELD, sw=1.8, rx=6))
    f.append(text(507, bs_cy - 5, 'Фотодіод', 11, FIELD, 'middle', bold=True))
    f.append(text(507, bs_cy + 12, 'i(t) ∝ |E⛛ + Eₗ|²', 9, INK, 'middle'))

    # Електричний сигнал та смуговий фільтр
    f.append(arrow(555, bs_cy, 605, bs_cy, color=INK, sw=2))
    f.append(rect(605, bs_cy - 27, 95, 55, fill='#fffbeb', stroke='#d97706', sw=1.8, rx=6))
    f.append(text(652, bs_cy - 5, 'Смуговий фільтр', 10, '#b45309', 'middle', bold=True))
    f.append(text(652, bs_cy + 12, 'f_IF = |f⛛ - fₗ|', 10, '#b45309', 'middle', bold=True))

    # Вихідний сигнал проміжної частоти
    f.append(arrow(652, bs_cy + 28, 652, 230, color='#b45309', sw=2))
    f.append(text(652, 245, 'Сигнал f_IF', 10, '#b45309', 'middle', bold=True))

    # Інформаційна панель знизу
    f.append(fitbox(40, 260, 640, 140,
                    'Фізика виникнення биття:\n'
                    '1. Фотострум пропорційний квадрату сумарної амплітуди: i(t) ∝ P⛛ + Pₗ + 2√(P⛛Pₗ)·cos(2π·f_IF·t + Δφ)\n'
                    '2. Оптичні частоти 2f⛛, 2fₗ (~400 THz) усереднюються інерцією фотодетектора.\n'
                    '3. Проміжна частота f_IF = |f⛛ - fₗ| (MHz...GHz) виділяється радіоелектронним фільтром.\n'
                    '4. Гетеродинне підсилення: амплітуда струму биття пропорційна √(Pₗ), що піднімає сигнал над шумами.',
                    size=10, color=INK, fill='#f8fafc', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'heterodyne-principle.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Спектральне перетворення: оптичний vs радіочастотний спектр
# ═══════════════════════════════════════════════════════════════════════════
def fig_spectral_mixing():
    W, H = 700, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Оптичний та радіочастотний спектри при гетеродинуванні', 16, INK, 'middle', bold=True))

    # Графік 1: Оптичний діапазон (зліва)
    ox1, oy1 = 60, 160
    gw1, gh1 = 260, 100
    f.append(rect(ox1, oy1 - gh1, gw1, gh1, fill='#fafbfc', stroke=MUTED, sw=1))
    f.append(text(ox1 + gw1 / 2, oy1 - gh1 - 10, 'Оптичний спектр (~193 THz)', 12, INK, 'middle', bold=True))

    # Вісь X та Y
    f.append(arrow(ox1, oy1, ox1 + gw1 + 15, oy1, color=INK, sw=1.2))
    f.append(arrow(ox1, oy1, ox1, oy1 - gh1 - 15, color=INK, sw=1.2))
    f.append(text(ox1 + gw1 + 10, oy1 + 16, 'f (THz)', 10, INK, 'middle'))

    # Оптичні піки: f_L та f_s
    xl = ox1 + 100
    xs = ox1 + 180
    f.append(line(xl, oy1, xl, oy1 - 85, color=NEG, sw=2.5))
    f.append(text(xl, oy1 - 92, 'fₗ (LO)', 11, NEG, 'middle', bold=True))

    f.append(line(xs, oy1, xs, oy1 - 35, color=POS, sw=2.5))
    f.append(text(xs, oy1 - 42, 'f⛛ (сигнал)', 11, POS, 'middle', bold=True))

    # Стрілка різниці частот f_IF
    f.append(arrow(xl, oy1 - 50, xs, oy1 - 50, color=FIELD, sw=1.5))
    f.append(text((xl + xs) / 2, oy1 - 58, 'f_IF', 10, FIELD, 'middle', bold=True))

    # Графік 2: Радіочастотний спектр після фотодіода (праворуч)
    ox2, oy2 = 400, 160
    gw2, gh2 = 260, 100
    f.append(rect(ox2, oy2 - gh2, gw2, gh2, fill='#fafbfc', stroke=MUTED, sw=1))
    f.append(text(ox2 + gw2 / 2, oy2 - gh2 - 10, 'Електричний спектр радіочастот', 12, INK, 'middle', bold=True))

    f.append(arrow(ox2, oy2, ox2 + gw2 + 15, oy2, color=INK, sw=1.2))
    f.append(arrow(ox2, oy2, ox2, oy2 - gh2 - 15, color=INK, sw=1.2))
    f.append(text(ox2 + gw2 + 10, oy2 + 16, 'f (GHz)', 10, INK, 'middle'))

    # Постійна складова (DC)
    f.append(line(ox2, oy2, ox2, oy2 - 90, color=MUTED, sw=3))
    f.append(text(ox2 + 15, oy2 - 80, 'DC (Pₗ)', 10, MUTED, 'start'))

    # Пік проміжної частоти f_IF
    x_if = ox2 + 120
    f.append(line(x_if, oy2, x_if, oy2 - 70, color='#b45309', sw=2.8))
    f.append(text(x_if, oy2 - 78, 'f_IF = |f⛛ - fₗ|', 11, '#b45309', 'middle', bold=True))

    # Лінія дробового шуму гетеродина
    f.append(line(ox2, oy2 - 20, ox2 + gw2, oy2 - 20, color=NEG, sw=1.5, dash='4,3'))
    f.append(text(ox2 + gw2 - 10, oy2 - 28, 'Шум гетеродина (Shot noise)', 9, NEG, 'end'))

    # Лінія теплового шуму (значно нижче)
    f.append(line(ox2, oy2 - 6, ox2 + gw2, oy2 - 6, color=MUTED, sw=1, dash='2,2'))
    f.append(text(ox2 + gw2 - 10, oy2 - 12, 'Тепловий шум', 9, MUTED, 'end'))

    # Нижня пояснювальна картка
    f.append(fitbox(60, 200, 600, 130,
                    'Перенесення спектра (Downconversion):\n'
                    '1. Квадратичне детектування оптичних хвиль переносить оптичний сигнал із частотою ~200 THz у радіочастотний діапазон f_IF.\n'
                    '2. Частотна селективність визначається вузькосмуговим радіочастотним фільтром (Δf_IF ~ 1...100 MHz).\n'
                    '3. Оптична роздільна здатність становить Δλ ~ 10⁻⁵...10⁻⁷ nm, що недосяжно для звичайних оптичних спектрометрів.',
                    size=10, color=INK, fill='#f4f6f8', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'spectral-mixing.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Схема балансного гетеродинного детектування (Balanced Detector)
# ═══════════════════════════════════════════════════════════════════════════
def fig_balanced_heterodyne_detection():
    W, H = 720, 370
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Балансне оптичне гетеродинне детектування', 16, INK, 'middle', bold=True))

    # Сигнальне та гетеродинне джерела
    f.append(text(40, 75, 'Сигнал E⛛', 11, POS, 'start', bold=True))
    f.append(arrow(110, 75, 230, 75, color=POS, sw=2))

    f.append(text(40, 160, 'Гетеродин Eₗ', 11, NEG, 'start', bold=True))
    f.append(arrow(110, 160, 230, 160, color=NEG, sw=2))

    # Воконний / волоконний змішувач 2x2 (Coupler / Beam Splitter)
    f.append(rect(230, 55, 100, 120, fill='#f1f5f9', stroke=INK, sw=1.8, rx=6))
    f.append(text(280, 105, 'Куплер 2×2\n(50:50)', 11, INK, 'middle', bold=True))

    # Виходи з куплера до двох фотодіодів
    # Верхній плече (Порт 1)
    f.append(arrow(330, 80, 440, 80, color=FIELD, sw=2))
    f.append(text(385, 68, '1/√2 (E⛛ + Eₗ)', 10, FIELD, 'middle'))

    # Нижнє плече (Порт 2 — фазовий зсув π для гетеродина!)
    f.append(arrow(330, 150, 440, 150, color=FIELD, sw=2))
    f.append(text(385, 165, '1/√2 (E⛛ - Eₗ)', 10, FIELD, 'middle'))

    # Фотодіод 1 (PD1)
    f.append(rect(440, 60, 70, 40, fill='#ecfdf5', stroke=FIELD, sw=1.5, rx=4))
    f.append(text(475, 84, 'PD1', 11, FIELD, 'middle', bold=True))

    # Фотодіод 2 (PD2)
    f.append(rect(440, 130, 70, 40, fill='#ecfdf5', stroke=FIELD, sw=1.5, rx=4))
    f.append(text(475, 154, 'PD2', 11, FIELD, 'middle', bold=True))

    # Струми з фотодіодів до вузла віднімання
    f.append(arrow(510, 80, 570, 80, color=INK, sw=1.8))
    f.append(text(535, 68, 'I₁', 11, INK, 'middle', bold=True))

    f.append(arrow(510, 150, 570, 150, color=INK, sw=1.8))
    f.append(text(535, 165, 'I₂', 11, INK, 'middle', bold=True))

    # Вузол віднімання (Диференціальний підсилювач / балансна схема)
    f.append(circle(590, 115, 20, fill='#eff6ff', stroke=POS, sw=1.8))
    f.append(text(590, 119, '−', 18, POS, 'middle', bold=True))
    f.append(line(570, 80, 590, 95, color=INK, sw=1.8))
    f.append(line(570, 150, 590, 135, color=INK, sw=1.8))

    # Результуючий балансний струм
    f.append(arrow(610, 115, 690, 115, color=POS, sw=2.5))
    f.append(text(650, 98, 'I_bal = I₁ - I₂', 11, POS, 'middle', bold=True))

    # Картка переваг балансного детектування
    f.append(fitbox(40, 210, 650, 135,
                    'Переваги балансної схеми:\n'
                    '• Повне пригнічення постійної складової гетеродина (DC offset cancelation).\n'
                    '• Пригнічення шуму інтенсивності гетеродина (RIN — Relative Intensity Noise) на 20...40 dB.\n'
                    '• Подвоєння корисної амплітуди сигналу проміжної частоти: I_bal(t) = 2·R·√(P⛛Pₗ)·cos(2π·f_IF·t + Δφ).\n'
                    '• Запобігання насиченню підсилювача постійним фотострумом гетеродина.',
                    size=10, color=INK, fill='#fdfbf7', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'balanced-heterodyne-detection.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Просторова когерентність та Antenna Theorem Зігмана
# ═══════════════════════════════════════════════════════════════════════════
def fig_spatial_wavefront_matching():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Умова просторового узгодження та антенна теорема Зігмана', 16, INK, 'middle', bold=True))

    # Варіант А: Ідеальне узгодження (ліворуч)
    f.append(rect(40, 60, 300, 150, fill='#fafbfc', stroke=MUTED, sw=1))
    f.append(text(190, 78, 'А) Ідеальне узгодження (θ = 0)', 11, POS, 'middle', bold=True))

    # Паралельні фронти
    for y in [100, 115, 130]:
        f.append(line(60, y, 220, y, color=POS, sw=2))
    f.append(text(140, 90, 'Хвильовий фронт E⛛ ∥ Eₗ', 10, POS, 'middle'))

    # Фотодіод
    f.append(line(240, 90, 240, 180, color=INK, sw=4))
    f.append(text(250, 135, 'Площа А', 10, INK, 'start'))

    f.append(text(190, 190, 'Синфазні коливання по всій площі А\nСигнал биття максимальний!', 10, INK, 'middle'))

    # Варіант Б: Кутовий розсинхрон (разом із смугами інтерференції) (праворуч)
    f.append(rect(380, 60, 300, 150, fill='#fafbfc', stroke=MUTED, sw=1))
    f.append(text(530, 78, 'Б) Кутовий нахил (θ > λ / D)', 11, NEG, 'middle', bold=True))

    # Нахилений фронт
    for y in [100, 115, 130]:
        f.append(line(400, y - 12, 540, y + 12, color=NEG, sw=2))
    f.append(text(470, 90, 'Нахил фронту на кут θ', 10, NEG, 'middle'))

    # Фотодіод
    f.append(line(580, 90, 580, 180, color=INK, sw=4))

    # Інтерференційні смуги на поверхні фотодіода
    for y in range(95, 180, 16):
        f.append(rect(576, y, 8, 8, fill=NEG if (y//16)%2==0 else POS, stroke='none'))

    f.append(text(530, 190, 'Утворюються смуги періодом Λ = λ/θ\nСинхронне інтегрування → Сигнал = 0!', 10, INK, 'middle'))

    # Пояснювальний блок знизу: Антенна теорема Зігмана
    f.append(fitbox(40, 225, 640, 115,
                    'Антенна теорема Зігмана (Siegman Antenna Theorem):\n'
                    '• Ефективне гетеродинне детектування вимагає узгодження фазових фронтів сигнальної хвилі та гетеродина.\n'
                    '• Граничний кутовий допуск: θ_max ≈ λ / D (для D = 1 mm, λ = 1550 nm допуск θ < 1.5 mrad ≈ 0.08°).\n'
                    '• Теорема Зігмана: A_det · Ω_fov ≈ λ² (добуток площі детектора на тілесний кут поля зору дорівнює λ²).\n'
                    '• Поляризаційне узгодження: вектори E⛛ та Eₗ повинні мати однакову поляризацію (ортогональні → Сигнал = 0).',
                    size=10, color=INK, fill='#eff6ff', stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'spatial-wavefront-matching.svg'), W, H, *f)

if __name__ == '__main__':
    fig_heterodyne_principle()
    fig_spectral_mixing()
    fig_balanced_heterodyne_detection()
    fig_spatial_wavefront_matching()
    print("All heterodyne figures generated successfully!")
