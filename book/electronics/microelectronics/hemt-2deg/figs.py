# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми HEMT і двовимірний електронний газ (2DEG)."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від book/electronics/microelectronics/hemt-2deg)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_modulation_doping():
    """Фігура 1: Порівняння класичного гомогенного каналу та просторового розділення носіїв (Modulation Doping)."""
    w, h = 880, 480
    frags = []

    # Заголовок блоків
    frags.append(text(220, 30, "Класичний гомогенний напівпровідник", size=15, bold=True, color=LINE))
    frags.append(text(660, 30, "Гетероструктура з модуляційним легуванням", size=15, bold=True, color=LINE))

    # --- Ліва панель: Гомогенний легований кристал ---
    frags.append(rect(30, 48, 380, 360, fill="#fcf8f7", stroke="#e0b4b4", sw=1.5, rx=8))
    frags.append(text(220, 72, "Кремній або GaAs (об'ємне легування)", size=13, bold=True, color=POS))

    # Кристалічний об'єм з іонами донорів і електронами
    frags.append(rect(50, 88, 340, 205, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))

    # Сітка розсіювання: іонізовані донори (+) та електрони (-)
    donors = [
        (90, 125), (170, 115), (250, 130), (330, 120),
        (110, 180), (190, 195), (270, 175), (345, 200),
        (85, 245), (155, 255), (235, 240), (320, 250)
    ]
    for dx, dy in donors:
        frags.append(plus(dx, dy, r=9))
        frags.append(text(dx, dy - 13, "N_d⁺", size=10, color=POS, bold=True))

    # Траєкторія електрона з хаотичним кулонівським розсіюванням
    frags.append(line(60, 145, 85, 133, color=NEG, sw=2))
    frags.append(line(85, 133, 115, 170, color=NEG, sw=2))
    frags.append(line(115, 170, 165, 123, color=NEG, sw=2))
    frags.append(line(165, 123, 195, 185, color=NEG, sw=2))
    frags.append(line(195, 185, 225, 233, color=NEG, sw=2))
    frags.append(line(225, 233, 265, 183, color=NEG, sw=2))
    frags.append(arrow(265, 183, 365, 145, color=NEG, sw=2.2))

    # Електрон, що летить крізь перешкоди
    frags.append(minus(140, 150, r=8))
    frags.append(text(140, 134, "e⁻ (дрейф)", size=11, color=NEG, bold=True))

    # Пояснювальний блок знизу зліва (всередині лівої панелі)
    frags.append(textbox(220, 345, "Електрони продираються крізь іони донорів:\nсильне кулонівське розсіювання (μ < 1400 см²/(В·с))",
                         size=11, color=POS, fill="#fff0ed", stroke=POS, sw=1.2)[0])

    # --- Права панель: Гетероструктура з модуляційним легуванням ---
    frags.append(rect(470, 48, 380, 360, fill="#f4fbf7", stroke="#a3d9b8", sw=1.5, rx=8))

    # Шар 1: Легований бар'єр AlGaAs (лише іони, електрони пішли)
    frags.append(rect(490, 68, 340, 65, fill="#fef0ed", stroke="#f5c2b8", sw=1.2, rx=4))
    frags.append(text(660, 85, "n-AlGaAs (легований бар'єр)", size=12, bold=True, color=POS))
    for dx in [520, 575, 630, 685, 740, 795]:
        frags.append(plus(dx, 108, r=7))
        frags.append(text(dx, 124, "донори", size=9, color=POS))

    # Шар 2: Нелегований спейсер i-AlGaAs
    frags.append(rect(490, 140, 340, 28, fill="#fffde7", stroke="#ffe082", sw=1.2, rx=4))
    frags.append(text(660, 158, "i-AlGaAs спейсер (чистий бар'єр, 2–5 нм)", size=11, bold=True, color="#8d6e63"))

    # Межа гетеропереходу
    frags.append(line(490, 173, 830, 173, color=FIELD, sw=2, dash="4,3"))

    # Шар 3: Нелегований i-GaAs з каналом 2DEG
    frags.append(rect(490, 178, 340, 105, fill="#e8f5e9", stroke="#a5d6a7", sw=1.2, rx=4))
    frags.append(text(660, 258, "i-GaAs канал (нелегований монокристал)", size=12, bold=True, color="#2e7d32"))

    # 2DEG шар у каналі прямо під гетеропереходом
    frags.append(rect(498, 183, 324, 28, fill="#d0e1fd", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(535, 201, "2DEG:", size=11, bold=True, color=NEG))
    for ex in [575, 620, 665, 710, 755, 795]:
        frags.append(minus(ex, 197, r=7))

    # Стрілка вільного безперешкодного руху електронів у 2DEG
    frags.append(arrow(505, 197, 815, 197, color=NEG, sw=2.5))
    frags.append(text(750, 222, "вільний політ", size=10, color=NEG, bold=True))

    # Пояснювальний блок знизу справа
    frags.append(textbox(660, 345, "Просторове розділення: електрони у чистому i-GaAs,\nдонори відсунуті спейсером (μ > 2·10⁶ см²/(В·с) при 4 К)",
                         size=11, color="#1b5e20", fill="#e8f5e9", stroke=FIELD, sw=1.2)[0])

    # Загальний підсумок знизу
    frags.append(fitbox(140, 422, 600, 42,
                        "Головний принцип: електрони скочуються в потенціальну яму іншого матеріалу й позбуваються кулонівського тертя",
                        size=13, bold=True, fill="#ffffff", stroke=LINE, color=INK))

    render(os.path.join(IMG_DIR, "modulation-doping-concept.svg"), w, h, *frags)


def fig_hemt_band_diagram():
    """Фігура 2: Зонна діаграма гетеропереходу AlGaAs/GaAs з трикутною квантовою ямою та 2DEG."""
    w, h = 880, 480
    frags = []

    # Рамка фону
    frags.append(rect(20, 20, 840, 440, fill="#fafbfc", stroke="#d0d5dd", sw=1.5, rx=8))

    # Вертикальна лінія межі розділу (гетероперехід)
    frags.append(line(420, 60, 420, 390, color="#78909c", sw=1.8, dash="5,4"))
    frags.append(text(420, 48, "Межа гетеропереходу (z = 0)", size=12, bold=True, color="#455a64"))

    # Підписи напівпровідників
    frags.append(text(230, 75, "Широкозонний n-AlGaAs (E_g1 ≈ 1.8 еВ)", size=14, bold=True, color=POS))
    frags.append(text(620, 75, "Вузькозонний i-GaAs (E_g2 ≈ 1.42 еВ)", size=14, bold=True, color="#2e7d32"))

    # Рівень Фермі E_F (горизонтальна штрихова лінія)
    frags.append(line(60, 240, 800, 240, color="#d32f2f", sw=1.8, dash="6,4"))
    frags.append(text(810, 244, "E_F", size=13, bold=True, color="#d32f2f", anchor="start"))
    frags.append(text(120, 230, "Рівень Фермі E_F", size=11, color="#d32f2f", bold=True))

    # Зона провідності E_c
    ec_path = (
        "M 60,130 "
        "C 180,140 320,180 420,205 "        # AlGaAs зона провідності йде до 205 px
        "L 420,310 "                         # Розрив ΔE_c: стрибок униз з 205 до 310 px
        "C 440,310 460,305 480,270 "        # Дно трикутної ями (нижче E_F=240)
        "C 520,220 620,185 800,180"         # Плавний вихід вище E_F
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (ec_path, NEG))
    frags.append(text(90, 120, "E_c (зона провідності)", size=13, bold=True, color=NEG))

    # Стрибок зони провідності ΔE_c
    frags.append(line(415, 205, 415, 310, color=POS, sw=2))
    frags.append(arrow(395, 205, 395, 310, color=POS, sw=1.5))
    frags.append(arrow(395, 310, 395, 205, color=POS, sw=1.5))
    frags.append(text(370, 260, "ΔE_c", size=13, bold=True, color=POS))

    # Штриховка області 2DEG (трикутна потенціальна яма нижче рівня Фермі)
    tri_well_path = "M 420,240 L 420,310 C 440,310 460,305 480,270 C 500,245 510,240 520,240 Z"
    frags.append('<path d="%s" fill="#bbdefb" fill-opacity="0.7" stroke="none"/>' % tri_well_path)

    # Квантовані енергетичні рівні підзон (E0, E1) всередині ями
    frags.append(line(422, 285, 465, 285, color="#1565c0", sw=2))
    frags.append(text(475, 289, "E₀ (основна підзона)", size=11, bold=True, color="#1565c0", anchor="start"))

    frags.append(line(422, 258, 492, 258, color="#1976d2", sw=1.8))
    frags.append(text(500, 262, "E₁ (перша підзона)", size=11, bold=True, color="#1976d2", anchor="start"))

    # Напис 2DEG всередині ями
    frags.append(textbox(455, 345, "2DEG у трикутній ямі\n(z < 5–10 нм)", size=11, color="#0d47a1",
                         fill="#e3f2fd", stroke="#1565c0", sw=1.2)[0])

    # Зона валентності E_v
    ev_path = (
        "M 60,380 "
        "C 180,385 320,410 420,425 "
        "L 420,445 "
        "C 450,445 550,410 800,390"
    )
    frags.append('<path d="%s" fill="none" stroke="#7b1fa2" stroke-width="2" stroke-dasharray="4,3"/>' % ev_path)
    frags.append(text(120, 395, "E_v (валентна зона)", size=12, color="#7b1fa2"))
    frags.append(text(390, 438, "ΔE_v", size=11, color="#7b1fa2"))

    # Пояснювальні виноски з боків
    frags.append(textbox(210, 310, "Збіднений шар AlGaAs:\nдонори іонізовані,\nзона вигнута вгору",
                         size=11, color=POS, fill="#fff5f5", stroke="#ef9a9a")[0])

    frags.append(textbox(670, 335, "Чистий об'єм GaAs:\nзона провідності вище E_F,\nвільних об'ємних носіїв немає",
                         size=11, color="#2e7d32", fill="#f1f8e9", stroke="#a5d6a7")[0])

    # Стрілка переходу електронів
    frags.append(arrow(310, 175, 440, 275, color=NEG, sw=2))
    frags.append(text(340, 160, "Електрони скочуються в яму", size=11, bold=True, color=NEG))

    render(os.path.join(IMG_DIR, "hemt-band-diagram.svg"), w, h, *frags)


def fig_gan_polarization_2deg():
    """Фігура 3: Механізм утворення 2DEG в AlGaN/GaN завдяки спонтанній та п'єзоелектричній поляризації."""
    w, h = 880, 460
    frags = []

    # Рамка фону
    frags.append(rect(20, 20, 840, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок фігури
    frags.append(text(440, 45, "Формування 2DEG в AlGaN/GaN під дією поляризаційних полів", size=16, bold=True, color=LINE))

    # Ліва частина: Шари гетероструктури з векторами поляризації
    # Шар поверхні / пасивації
    frags.append(rect(60, 75, 340, 30, fill="#eceff1", stroke="#b0bec5", sw=1.2, rx=4))
    frags.append(text(230, 95, "Поверхня (донорні пастки / затвор)", size=11, bold=True, color="#455a64"))

    # Шар AlGaN (псевдоморфно розтягнутий)
    frags.append(rect(60, 115, 340, 110, fill="#e1f5fe", stroke="#81d4fa", sw=1.5, rx=4))
    frags.append(text(130, 138, "Бар'єр AlGaN (20–25 нм)", size=12, bold=True, color="#0277bd"))
    frags.append(text(130, 155, "(розтягнутий, a_AlGaN < a_GaN)", size=10, color="#546e7a"))

    # Вектори поляризації в AlGaN
    # Спонтанна поляризація P_sp
    frags.append(arrow(260, 130, 260, 175, color="#c2185b", sw=2.5))
    frags.append(text(285, 155, "P_sp (AlGaN)", size=11, bold=True, color="#c2185b", anchor="start"))

    # П'єзоелектрична поляризація P_pe
    frags.append(arrow(260, 175, 260, 215, color="#7b1fa2", sw=2.5))
    frags.append(text(285, 200, "P_pe (AlGaN)", size=11, bold=True, color="#7b1fa2", anchor="start"))

    # Гетероперехід: шар позитивного поляризаційного заряду +σ_pol
    frags.append(line(55, 230, 405, 230, color=POS, sw=2))
    for px in [90, 140, 190, 240, 290, 340, 380]:
        frags.append(plus(px, 230, r=7))
    frags.append(text(230, 248, "Позитивний поляризаційний заряд +σ_pol = +q · 10¹³ см⁻²", size=11, bold=True, color=POS))

    # Шар 2DEG прямо під гетеропереходом
    frags.append(rect(60, 255, 340, 25, fill="#d0e1fd", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(110, 272, "2DEG канал:", size=11, bold=True, color=NEG))
    for ex in [180, 220, 260, 300, 340, 375]:
        frags.append(minus(ex, 267, r=6))

    # Шар GaN (буфер / підкладка)
    frags.append(rect(60, 285, 340, 100, fill="#e8f5e9", stroke="#a5d6a7", sw=1.5, rx=4))
    frags.append(text(130, 310, "Буфер GaN (недеформований)", size=12, bold=True, color="#2e7d32"))

    # Вектор спонтанної поляризації в GaN
    frags.append(arrow(260, 310, 260, 355, color="#c2185b", sw=2.5))
    frags.append(text(285, 335, "P_sp (GaN)", size=11, bold=True, color="#c2185b", anchor="start"))
    frags.append(text(230, 375, "P_pe (GaN) = 0 (буфер без напружень)", size=10, color="#689f38"))

    # Права частина: Електростатичний механізм виникнення 2DEG
    frags.append(rect(450, 75, 390, 310, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(645, 105, "Електростатичний баланс поля", size=14, bold=True, color=LINE))

    # Кроки механізму
    steps = [
        "1. Кристал вюрциту GaN/AlGaN позбавлений центра інверсії:",
        "   вектор P_sp спрямований до підкладки [0001].",
        "2. Розтяг AlGaN додає п'єзополяризацію P_pe в тому ж напрямку.",
        "3. На межі розділу виникає розрив поляризації:",
        "   σ_pol = (P_sp + P_pe)_AlGaN - (P_sp)_GaN > 0.",
        "4. Величезний заряд +σ_pol створює сильне електричне поле,",
        "   яке опускає зону провідності GaN нижче рівня Фермі E_F.",
        "5. Електрони з поверхні притягуються полем до межі:",
        "   формується 2DEG з рекордною n_s ≈ 10¹³ см⁻² без легування!"
    ]
    frags.append(mtext(470, 135, steps, size=11, color="#263238", anchor="start", lh=1.35))

    # Підсумок знизу
    frags.append(fitbox(60, 400, 780, 32,
                        "У GaN HEMT надвисока провідність каналу досягається силою вбудованих полів поляризації кристалічної ґратки",
                        size=12, bold=True, fill="#e8f5e9", stroke=FIELD, color="#1b5e20"))

    render(os.path.join(IMG_DIR, "gan-polarization-2deg.svg"), w, h, *frags)


def fig_hemt_transistor_structure():
    """Фігура 4: Поперечний розріз та топологія транзистора HEMT (AlGaAs/GaAs або GaN)."""
    w, h = 880, 500
    frags = []

    # Рамка фону
    frags.append(rect(20, 20, 840, 460, fill="#fafbfc", stroke="#d0d5dd", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(440, 45, "Архітектура та контакти транзистора HEMT", size=16, bold=True, color=LINE))

    # Електроди зверху
    # Витік (Source) - омічний контакт
    frags.append(rect(70, 65, 150, 45, fill="#ffd54f", stroke="#f57f17", sw=1.8, rx=4))
    frags.append(text(145, 87, "ВИТІК (Source)", size=13, bold=True, color="#bf360c"))
    frags.append(text(145, 102, "Омічний контакт (Ti/Al/Ni/Au)", size=9, color="#e65100"))

    # Затвор (Gate) - бар'єр Шотткі (Т-подібний затвор / mushroom gate для НВЧ)
    # Ніжка затвора (коротка довжина L_g)
    frags.append(rect(420, 95, 40, 45, fill="#90a4ae", stroke="#37474f", sw=1.5, rx=2))
    # Верхня розширена «капелюшок» Т-затвора (низький опір металізації)
    frags.append(rect(380, 65, 120, 30, fill="#b0bec5", stroke="#37474f", sw=1.8, rx=4))
    frags.append(text(440, 85, "ЗАТВОР (Gate)", size=12, bold=True, color="#263238"))
    frags.append(text(440, 120, "L_g", size=10, bold=True, color="#d32f2f"))

    # Стік (Drain) - омічний контакт
    frags.append(rect(660, 65, 150, 45, fill="#ffd54f", stroke="#f57f17", sw=1.8, rx=4))
    frags.append(text(735, 87, "СТІК (Drain)", size=13, bold=True, color="#bf360c"))
    frags.append(text(735, 102, "Омічний контакт (Ti/Al/Ni/Au)", size=9, color="#e65100"))

    # Пасивація SiN
    frags.append(rect(225, 115, 190, 25, fill="#e0f2f1", stroke="#80cbc4", sw=1, rx=2))
    frags.append(text(320, 131, "Пасивація SiN", size=10, color="#00695c"))
    frags.append(rect(465, 115, 190, 25, fill="#e0f2f1", stroke="#80cbc4", sw=1, rx=2))
    frags.append(text(560, 131, "Пасивація SiN", size=10, color="#00695c"))

    # Шар бар'єра (AlGaN або n-AlGaAs) — секціями між контактами або суцільний шар
    # Бар'єр між витоком і затвором
    frags.append(rect(225, 140, 190, 50, fill="#e1f5fe", stroke="#81d4fa", sw=1.5, rx=2))
    # Бар'єр між затвором і стоком
    frags.append(rect(465, 140, 190, 50, fill="#e1f5fe", stroke="#81d4fa", sw=1.5, rx=2))
    frags.append(text(320, 170, "Бар'єр AlGaN / AlGaAs", size=11, bold=True, color="#0277bd"))
    frags.append(text(560, 170, "Дрейфова зона (25 нм)", size=11, bold=True, color="#0277bd"))

    # Сплавні омічні контакти, що пронизують бар'єр до каналу 2DEG
    frags.append(rect(70, 110, 150, 80, fill="#ffe082", stroke="#ffb300", sw=1.5, rx=2))
    frags.append(text(145, 150, "Сплавний омічний контакт", size=10, bold=True, color="#e65100"))
    frags.append(text(145, 168, "пряме з'єднання з 2DEG", size=9, color="#bf360c"))

    frags.append(rect(660, 110, 150, 80, fill="#ffe082", stroke="#ffb300", sw=1.5, rx=2))
    frags.append(text(735, 150, "Сплавний омічний контакт", size=10, bold=True, color="#e65100"))
    frags.append(text(735, 168, "пряме з'єднання з 2DEG", size=9, color="#bf360c"))

    # Межа гетеропереходу та 2DEG канал
    frags.append(line(50, 190, 830, 190, color=FIELD, sw=2, dash="4,3"))
    frags.append(rect(60, 192, 760, 20, fill="#bbdefb", stroke=NEG, sw=1.5, rx=3))
    frags.append(text(440, 206, "Двовимірний електронний газ (2DEG) — струмопровідний канал", size=11, bold=True, color="#0d47a1"))

    # Буферний шар каналу (GaN або GaAs)
    frags.append(rect(50, 212, 780, 80, fill="#e8f5e9", stroke="#a5d6a7", sw=1.5, rx=4))
    frags.append(text(440, 245, "Нелегований буферний шар (GaN / GaAs, 1–2 мкм)", size=13, bold=True, color="#2e7d32"))
    frags.append(text(440, 265, "Високоомний монокристал: відсутність паразитних витоків у товщу підкладки", size=10, color="#558b2f"))

    # Перехідний шар / підкладка (Si, SiC або сапфір)
    frags.append(rect(50, 292, 780, 60, fill="#efebe9", stroke="#bcaaa4", sw=1.5, rx=4))
    frags.append(text(440, 320, "Підкладка (SiC — для високої потужності, Si — для масового виробництва, Сапфір / GaAs)", size=12, bold=True, color="#4e342e"))

    # Нижня панель: ключові переваги архітектури
    frags.append(textbox(230, 410, "НВЧ-властивості:\nТ-подібний затвор мінімізує опір R_g,\nL_g < 100 нм забезпечує f_T > 100 ГГц",
                         size=11, color="#0277bd", fill="#e1f5fe", stroke="#81d4fa")[0])

    frags.append(textbox(650, 410, "Силові переваги:\nДрейфовий проміжок затвор-стік\nвитримує напругу V_ds > 650–1200 В",
                         size=11, color="#bf360c", fill="#fff3e0", stroke="#ffb74d")[0])

    render(os.path.join(IMG_DIR, "hemt-transistor-structure.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_modulation_doping()
    fig_hemt_band_diagram()
    fig_gan_polarization_2deg()
    fig_hemt_transistor_structure()
    print("All figures generated successfully.")
