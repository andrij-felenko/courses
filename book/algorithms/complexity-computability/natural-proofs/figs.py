# -*- coding: utf-8 -*-
"""Фігури для теми «Природні доведення» (book/algorithms/complexity-computability/natural-proofs)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
COLOR_BG_BOX = "#f8fafc"
COLOR_GRID_BORDER = "#cbd5e1"
COLOR_HEADER_BG = "#e2e8f0"
COLOR_ACCENT = "#2563eb"
COLOR_ACCENT_BG = "#dbeafe"
COLOR_SUCCESS = "#059669"
COLOR_SUCCESS_BG = "#d1fae5"
COLOR_WARNING = "#d97706"
COLOR_WARNING_BG = "#fef3c7"
COLOR_DANGER = "#dc2626"
COLOR_DANGER_BG = "#fee2e2"
COLOR_MUTED = "#64748b"


def fig_natural_property_structure():
    """Фігура 1: Три складові Натуральної властивості булевих функцій."""
    W, H = 960, 420
    frags = []

    # Головна рамка
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    # 3 блоки складових
    box_w, box_h = 280, 260
    y_pos = 70

    # Блок 1: Конструктивність
    x1 = 40
    b1_bg = rect(x1, y_pos, box_w, box_h, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=2, rx=8)
    frags.append(b1_bg)
    frags.append(text(x1 + box_w / 2, y_pos + 30, "1. Конструктивність", size=15, bold=True, color=COLOR_ACCENT))
    frags.append(text(x1 + box_w / 2, y_pos + 52, "(Constructiveness)", size=12, color=COLOR_MUTED))
    frags.append(line(x1 + 15, y_pos + 68, x1 + box_w - 15, y_pos + 68, color=COLOR_ACCENT, sw=1))

    tb1 = fitbox(x1 + 15, y_pos + 80, box_w - 30, 160, [
        "Перевірка належності f ∈ Cₙ",
        "виконується ефективно:",
        "алгоритм з урахуванням",
        "таблиці істинності 2ⁿ біт",
        "працює за поліноміальний",
        "час poly(2ⁿ) = 2⁰⁽ⁿ⁾."
    ], size=13, color=INK, lh=22)
    frags.append(tb1)

    # Блок 2: Великість
    x2 = 340
    b2_bg = rect(x2, y_pos, box_w, box_h, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=2, rx=8)
    frags.append(b2_bg)
    frags.append(text(x2 + box_w / 2, y_pos + 30, "2. Великість", size=15, bold=True, color=COLOR_SUCCESS))
    frags.append(text(x2 + box_w / 2, y_pos + 52, "(Largeness)", size=12, color=COLOR_MUTED))
    frags.append(line(x2 + 15, y_pos + 68, x2 + box_w - 15, y_pos + 68, color=COLOR_SUCCESS, sw=1))

    tb2 = fitbox(x2 + 15, y_pos + 80, box_w - 30, 160, [
        "Властивість Cₙ притаманна",
        "великій частці функцій:",
        "випадкова функція R ∈ Fₙ",
        "задовольняє Cₙ з ймовірністю",
        "Pr[R ∈ Cₙ] ≥ 1 / poly(n)",
        "(або ≥ 2⁻ᶜⁿ)."
    ], size=13, color=INK, lh=22)
    frags.append(tb2)

    # Блок 3: Корисність
    x3 = 640
    b3_bg = rect(x3, y_pos, box_w, box_h, fill=COLOR_WARNING_BG, stroke=COLOR_WARNING, sw=2, rx=8)
    frags.append(b3_bg)
    frags.append(text(x3 + box_w / 2, y_pos + 30, "3. Корисність", size=15, bold=True, color=COLOR_WARNING))
    frags.append(text(x3 + box_w / 2, y_pos + 52, "(Usefulness)", size=12, color=COLOR_MUTED))
    frags.append(line(x3 + 15, y_pos + 68, x3 + box_w - 15, y_pos + 68, color=COLOR_WARNING, sw=1))

    tb3 = fitbox(x3 + 15, y_pos + 80, box_w - 30, 160, [
        "Кожна функція f ∈ Cₙ",
        "вимагає великої складності:",
        "CircuitSize(f) > S(n).",
        "Якщо f ∈ Cₙ, її не можна",
        "обчислити схемою розміру",
        "меншого за S(n)."
    ], size=13, color=INK, lh=22)
    frags.append(tb3)

    # Нижній висновок
    bot_box, _, _ = textbox(W / 2, 365,
                             "Висновок: Натуральне доведення будує критерій Cₙ для доведення складності > S(n)",
                             size=13, bold=True, fill="#f1f5f9", stroke="#cbd5e1", pad=8)
    frags.append(bot_box)

    render(os.path.join(IMG, "natural-property-structure.svg"), W, H, *frags,
           title="Три складові натуральної властивості Cₙ ⊆ Fₙ проти схем S(n)")


def fig_prg_distinguisher_attack():
    """Фігура 2: Як натуральна властивість перетворюється на криптографічний розрізнювач."""
    W, H = 960, 480
    frags = []

    # Головна рамка
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    # Ліве джерело: PRG генератор
    prg_box = rect(40, 80, 260, 170, fill=COLOR_DANGER_BG, stroke=COLOR_DANGER, sw=2, rx=8)
    frags.append(prg_box)
    frags.append(text(170, 110, "Псевдовипадковий генератор G", size=13, bold=True, color=COLOR_DANGER))
    frags.append(text(170, 130, "Коротке зерно s (nᵉ біт)", size=12, color=COLOR_MUTED))
    frags.append(line(55, 145, 285, 145, color=COLOR_DANGER, sw=1))

    tb_prg = fitbox(55, 155, 230, 85, [
        "Генерує псевдовипадкову",
        "функцію f_G з коротким кодом.",
        "Складність f_G < S(n).",
        "Отже: f_G ∉ Cₙ (за корисністю)!"
    ], size=12, color=INK, lh=19)
    frags.append(tb_prg)

    # Праве джерело: Справжній хаос
    rnd_box = rect(660, 80, 260, 170, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=2, rx=8)
    frags.append(rnd_box)
    frags.append(text(790, 110, "Справжній хаос R ∈ Fₙ", size=14, bold=True, color=COLOR_SUCCESS))
    frags.append(text(790, 130, "Випадкова таблиця 2ⁿ біт", size=12, color=COLOR_MUTED))
    frags.append(line(675, 145, 905, 145, color=COLOR_SUCCESS, sw=1))

    tb_rnd = fitbox(675, 155, 230, 85, [
        "Справді випадкова функція R",
        "має високу складність.",
        "За умовою великості:",
        "Pr[ R ∈ Cₙ ] ≥ 1 / poly(n)."
    ], size=12, color=INK, lh=19)
    frags.append(tb_rnd)

    # Центральний вузол: Розрізнювач на основі C_n
    dist_box = rect(330, 280, 300, 150, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=2, rx=8)
    frags.append(dist_box)
    frags.append(text(480, 308, "Розрізнювач D(f) на базі Cₙ", size=14, bold=True, color=COLOR_ACCENT))
    frags.append(text(480, 328, "Час роботи poly(2ⁿ) — Конструктивність", size=11, color=COLOR_MUTED))
    frags.append(line(345, 338, 615, 338, color=COLOR_ACCENT, sw=1))

    tb_dist = fitbox(345, 345, 270, 75, [
        "D(f) = 1, якщо f ∈ Cₙ",
        "D(f) = 0, якщо f ∉ Cₙ",
        "• D(f_G) = 0 завжди!",
        "• D(R) = 1 з ймовірністю ≥ 1/poly(n)"
    ], size=12, color=INK, lh=18)
    frags.append(tb_dist)

    # Стрілки від джерел до розрізнювача
    frags.append(arrow(170, 250, 370, 280, color=COLOR_DANGER, sw=2))
    frags.append(text(250, 255, "f_G", size=13, bold=True, color=COLOR_DANGER))

    frags.append(arrow(790, 250, 590, 280, color=COLOR_SUCCESS, sw=2))
    frags.append(text(710, 255, "R", size=13, bold=True, color=COLOR_SUCCESS))

    render(os.path.join(IMG, "prg-distinguisher-attack.svg"), W, H, *frags,
           title="Конфлікт Разборова–Рудіча: Натуральна властивість ламає PRG")


def fig_barriers_timeline_comparison():
    """Фігура 3: Порівняння трьох фундаментальних бар'єрів теорії складності."""
    W, H = 980, 460
    frags = []

    # Головна рамка
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    col_w = 290
    col_h = 320
    y_top = 70

    # Бар'єр 1: BGS (1975)
    x1 = 30
    frags.append(rect(x1, y_top, col_w, col_h, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    frags.append(text(x1 + col_w / 2, y_top + 28, "Релятивізація (BGS, 1975)", size=14, bold=True, color="#1d4ed8"))
    frags.append(line(x1 + 15, y_top + 42, x1 + col_w - 15, y_top + 42, color="#93c5fd", sw=1))

    tb_bgs = fitbox(x1 + 15, y_top + 55, col_w - 30, 240, [
        "• Ідея: Діагоналізація та",
        "  симуляція машин Тюринга.",
        "• Суть бар'єру: Існують",
        "  оракули A та B такі, що",
        "  Pᴬ = NPᴬ, але P🅱 ≠ NP🅱.",
        "• Що блокує: Будь-які докази,",
        "  що зберігають чинність для",
        "  чорних скриньок-оракулів.",
        "• Обхід: Арифметизація,",
        "  використання структури."
    ], size=12, color=INK, lh=22)
    frags.append(tb_bgs)

    # Бар'єр 2: RR (1997)
    x2 = 345
    frags.append(rect(x2, y_top, col_w, col_h, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=8))
    frags.append(text(x2 + col_w / 2, y_top + 28, "Натуральні доведення (1997)", size=14, bold=True, color="#b91c1c"))
    frags.append(line(x2 + 15, y_top + 42, x2 + col_w - 15, y_top + 42, color="#fca5a5", sw=1))

    tb_rr = fitbox(x2 + 15, y_top + 55, col_w - 30, 240, [
        "• Ідея: Пошук конструктивних",
        "  та великих властивостей Cₙ.",
        "• Суть бар'єру: Натуральні",
        "  властивості стають розрізнювачами",
        "  для криптографічних PRG.",
        "• Що блокує: Комбінаторні",
        "  нижні оцінки схем P/poly.",
        "• Обхід: Рідкісні властивості",
        "  (GCT), програма Вільямса."
    ], size=12, color=INK, lh=22)
    frags.append(tb_rr)

    # Бар'єр 3: AW (2008)
    x3 = 660
    frags.append(rect(x3, y_top, col_w, col_h, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=8))
    frags.append(text(x3 + col_w / 2, y_top + 28, "Алгебраїзація (AW, 2008)", size=14, bold=True, color="#15803d"))
    frags.append(line(x3 + 15, y_top + 42, x3 + col_w - 15, y_top + 42, color="#86efac", sw=1))

    tb_aw = fitbox(x3 + 15, y_top + 55, col_w - 30, 240, [
        "• Ідея: Арифметизація та",
        "  поліноміальні розширення.",
        "• Суть бар'єру: Існують",
        "  алгебраїчні оракули з",
        "  колапсом та розділенням.",
        "• Що блокує: Методи IP=PSPACE",
        "  і PCP для розділення P/NP.",
        "• Обхід: Не-алгебраїчні",
        "  геометричні симетрії (GCT)."
    ], size=12, color=INK, lh=22)
    frags.append(tb_aw)

    # Нижній висновок
    bot_box, _, _ = textbox(W / 2, 415,
                             "GCT та програма Вільямса оминають усі три бар'єри завдяки не-натуральності й не-релятивізованості",
                             size=12, bold=True, fill="#f1f5f9", stroke="#cbd5e1", pad=6)
    frags.append(bot_box)

    render(os.path.join(IMG, "barriers-timeline-comparison.svg"), W, H, *frags,
           title="Три мета-бар'єри доведення P ≠ NP та шляхи їх обходу")


def fig_circuit_classes_hierarchy():
    """Фігура 4: Ієрархія схемних класів та криптографічний поріг."""
    W, H = 960, 440
    frags = []

    # Головна рамка
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    # Вкладені класи складності (концентричні прямокутники)
    # 1. P/poly
    frags.append(rect(50, 70, 860, 330, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    frags.append(text(480, 95, "P/poly (Схеми поліноміального розміру) — Мета: довести NP ⊈ P/poly", size=13, bold=True, color="#334155"))

    # 2. NC1 / TC0
    frags.append(rect(80, 115, 800, 265, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(480, 140, "NC¹ / TC⁰ (Схеми логарифмічної глибини / порогові вентилі)", size=13, bold=True, color="#1e293b"))

    # Червона пунктирна лінія — КРИПТОГРАФІЧНИЙ ПОРІГ
    frags.append(line(90, 195, 290, 195, color=COLOR_DANGER, sw=2.5, dash="6 4"))
    frags.append(line(670, 195, 870, 195, color=COLOR_DANGER, sw=2.5, dash="6 4"))

    frags.append(rect(300, 180, 360, 30, fill=COLOR_DANGER_BG, stroke=COLOR_DANGER, sw=1.5, rx=4))
    frags.append(text(480, 200, "КРИПТОГРАФІЧНИЙ ПОРІГ: Тут виникають PRG!", size=13, bold=True, color=COLOR_DANGER))

    # 3. AC0[p]
    frags.append(rect(110, 225, 740, 135, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=1.5, rx=6))
    frags.append(text(480, 248, "AC⁰[p] (Схеми сталої глибини з вентилями mod p) — Нижні оцінки доведені (Смоленський, 1987)", size=12, bold=True, color=COLOR_SUCCESS))

    # 4. AC0
    frags.append(rect(140, 265, 680, 80, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    frags.append(text(480, 288, "AC⁰ (Схеми сталої глибини AND, OR, NOT) — Доведено нижні оцінки (Гостад, 1987)", size=12, bold=True, color=COLOR_ACCENT))

    # Пояснювальний текст знизу в AC0
    frags.append(text(480, 325, "Натуральні доведення ПРАЦЮЮТЬ тут, бо AC⁰ та AC⁰[p] не здатні обчислити PRG!", size=12, bold=True, color="#1e40af"))

    render(os.path.join(IMG, "circuit-classes-hierarchy.svg"), W, H, *frags,
           title="Ієрархія схемних класів та лінія криптографічного бар'єру")


if __name__ == "__main__":
    fig_natural_property_structure()
    fig_prg_distinguisher_attack()
    fig_barriers_timeline_comparison()
    fig_circuit_classes_hierarchy()
    print("Всі фігури успішно згенеровано у теку img/")
