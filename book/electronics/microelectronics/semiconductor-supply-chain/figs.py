# -*- coding: utf-8 -*-
import sys, os
# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

VIOLET = "#6a3d9a"
GOLD   = "#b8860b"
CYAN   = "#0288d1"
AMBER  = "#e67e22"

# ── 1. global-supply-map: Глобальна географічна та функціональна спеціалізація ──
def fig_global_supply_map():
    W, H = 840, 520
    p = []

    # Підзаголовок під головним title (який рендериться на y=26)
    p.append(text(W / 2, 48, "Розподіл ключових технологічних етапів між країнами та провідними компаніями", size=11, color=MUTED))

    # Картки шести ланок (2 стовпчики по 3 картки)
    # Стовпчик 1: x=40..400, Стовпчик 2: x=440..800
    cards = [
        # (x, y, w, h, fill, stroke, title_color, country, role, companies, detail)
        (40, 68, 365, 122, "#eef4fb", NEG, NEG,
         "США & UK", "1. Проєктування, EDA та IP-ядра",
         "Synopsys, Cadence, Arm, Siemens EDA",
         ">75% світового ринку софту EDA та провідні процесорні архітектури"),

        (435, 68, 365, 122, "#eef8f2", FIELD, FIELD,
         "Нідерланди & Німеччина", "2. Літографія та оптика",
         "ASML (EUV/DUV), Carl Zeiss SMT, Trumpf",
         "100% монополія на EUV-сканери (13.5 нм) та відбивну оптику Zeiss"),

        (40, 204, 365, 122, "#fdf6e7", GOLD, GOLD,
         "Японія", "3. Матеріали та підкладки",
         "Shin-Etsu, SUMCO, TOK, JSR, Stella Chemifa",
         ">55% ринку 300-мм кремнію, >85% передових резистів і 11N фтороводень"),

        (435, 204, 365, 122, "#fcf0f0", POS, POS,
         "Тайвань & Південна Корея", "4. Контрактні фаби (Foundry)",
         "TSMC, Samsung Foundry, UMC, Vanguard",
         ">90% світового виготовлення передової логіки (<5 нм) на Тайвані"),

        (40, 340, 365, 122, "#f4eefb", VIOLET, VIOLET,
         "Південна Корея, США, Японія", "5. Пам'ять (DRAM і NAND)",
         "Samsung, SK Hynix, Micron, Kioxia",
         "Олігополія: три компанії тримають понад 90% світового ринку DRAM"),

        (435, 340, 365, 122, "#edf8fa", CYAN, CYAN,
         "Тайвань, Малайзія, Китай", "6. Advanced Packaging & OSAT",
         "ASE Group, Amkor, TSMC (CoWoS), JCET",
         "Корпусування чіпів, 2.5D/3D стекінг (чиплети, HBM) та тестування"),
    ]

    for x, y, w, h, fill, stroke, tcolor, ctry, role, comps, detail in cards:
        p.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8))
        p.append(text(x + 12, y + 22, role, size=12, color=tcolor, bold=True, anchor="start"))
        p.append(text(x + w - 12, y + 22, ctry, size=10.5, color=INK, bold=True, anchor="end"))
        p.append(line(x + 12, y + 32, x + w - 12, y + 32, color=stroke, sw=1, dash="3,3"))
        p.append(text(x + 12, y + 52, "Гравці: " + comps, size=10.5, color=INK, bold=True, anchor="start"))
        p.append(text(x + 12, y + 74, detail, size=9.5, color=MUTED, anchor="start"))

    # Нижня стрічка підсумку
    p.append(rect(40, 478, 760, 28, fill=FILL, stroke=LINE, sw=1.2, rx=4))
    p.append(text(W / 2, 496, "Жодна країна не має замкненого циклу: кристал долає до 70 000 км між континентами", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "global-supply-map.svg"), W, H, *p,
           title="Глобальна спеціалізація виробництва чіпів")


# ── 2. wafer-lead-time: 5-місячний виробничий цикл пластини ───────────────────
def fig_wafer_lead_time():
    W, H = 820, 390
    p = []

    p.append(text(W / 2, 48, "Багаторазові циклічні проходи крізь літографію, травлення, легування та металізацію", size=11, color=MUTED))

    # Схема часової шкали
    blocks = [
        (40, 75, 130, 115, "#eef4fb", NEG, "1. Підкладка", "Тижні 1–2", ["Монокристал Si,", "нарізка 300 мм,", "полірування CMP"]),
        (185, 75, 150, 115, "#fcf0f0", POS, "2. FEOL (Затвори)", "Тижні 3–9", ["Криниці, канали,", "EUV літографія,", "іонне легування"]),
        (350, 75, 160, 115, "#fdf6e7", GOLD, "3. BEOL (Метал)", "Тижні 10–16", ["15–20 шарів Cu,", "Low-k ізоляція,", "мікропереходи via"]),
        (525, 75, 125, 115, "#f4eefb", VIOLET, "4. Wafer Sort", "Тижні 17–18", ["Зондовий тест", "кристалів на платі,", "картування браку"]),
        (665, 75, 115, 115, "#edf8fa", CYAN, "5. OSAT & Тест", "Тижні 19–22", ["Дискова нарізка,", "пакування BGA,", "фінальний тест FT"]),
    ]

    for x, y, w, h, fill, stroke, title_txt, time_txt, lines in blocks:
        p.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8))
        p.append(text(x + w / 2, y + 20, title_txt, size=11.5, color=stroke, bold=True))
        p.append(rect(x + 12, y + 28, w - 24, 18, fill=BG, stroke=stroke, sw=1, rx=3))
        p.append(text(x + w / 2, y + 41, time_txt, size=9.5, color=INK, bold=True))
        
        for i, l in enumerate(lines):
            p.append(text(x + w / 2, y + 62 + i * 16, l, size=9.5, color=MUTED))

    # Стрілки між блоками
    arrows_x = [170, 335, 510, 650]
    for ax in arrows_x:
        p.append(line(ax + 2, 132, ax + 13, 132, color=LINE, sw=2))
        p.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                 % (ax + 13, 132, ax + 8, 128, ax + 8, 136, LINE))

    # Нижній пояснювальний блок
    p.append(rect(40, 210, 740, 160, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(60, 234, "Чому виготовлення займає понад 100 днів: фізика циклу та черги", size=12, color=INK, bold=True, anchor="start"))

    p.append(text(60, 260, "• 1000–1500 операцій: пластина повторно проходить літографію та травлення 60–90 разів.", size=10, color=INK, anchor="start"))
    p.append(text(60, 284, "• Черги до EUV-сканерів: верстати завантажені на >95%, формуючи технологічні буфери.", size=10, color=INK, anchor="start"))
    p.append(text(60, 308, "• Незавершене виробництво (WIP): на GigaFab одночасно обробляються сотні тисяч пластин.", size=10, color=INK, anchor="start"))
    p.append(text(60, 332, "• Величезна інерція: раптовий сплеск попиту фаб може покрити готовою партією лише за 4–6 місяців.", size=10, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "wafer-lead-time.svg"), W, H, *p,
           title="Часовий цикл виготовлення пластини (3.5–5 місяців)")


# ── 3. chokepoint-matrix: Матриця критичних вузьких місць ──────────────────────
def fig_chokepoint_matrix():
    W, H = 820, 420
    p = []

    p.append(text(W / 2, 48, "Сегменти з екстремальною ринковою або географічною концентрацією (>70–100%)", size=11, color=MUTED))

    # Таблична сітка
    ty = 70
    headers = [
        (40, 190, "Технологічний вузол"),
        (230, 200, "Провідні гравці / Країна"),
        (430, 110, "Концентрація"),
        (540, 240, "Головний бар'єр входу / Ризик")
    ]
    p.append(rect(40, ty, 740, 28, fill="#2c3e50", stroke="#2c3e50", sw=1, rx=4))
    for hx, hw, htitle in headers:
        p.append(text(hx + hw / 2, ty + 19, htitle, size=10.5, color=BG, bold=True))

    rows = [
        (102, "EUV-літографія (13.5 нм)", "ASML (Нідерланди) + Zeiss", "100%", "30 років R&D, надскладна оптика Zeiss", "#fcf0f0"),
        (146, "Передова логіка (<5 нм)", "TSMC (Тайвань)", ">90%", "Геополітика Тайваню, $20 млрд/фаб", "#fcf0f0"),
        (190, "EDA-програми проєктування", "Synopsys, Cadence (США)", ">75%", "Математичні патенти, мільйони людино-років", "#fdf6e7"),
        (234, "Хімікати (EUV резисти, HF)", "TOK, JSR, Shin-Etsu (Японія)", ">85%", "Синтез та надчисте очищення 11N", "#fdf6e7"),
        (278, "Кремнієві 300-мм підкладки", "Shin-Etsu, SUMCO (Японія)", ">55%", "Бездислокаційні монокристали", "#eef4fb"),
        (322, "Advanced Packaging (CoWoS)", "TSMC (Тайвань), ASE", ">80%", "Дефіцит ліній 2.5D для AI-процесорів", "#fdf6e7"),
    ]

    for ry, tech, player, share, risk, rbg in rows:
        p.append(rect(40, ry, 740, 38, fill=rbg, stroke=LINE, sw=0.8, rx=2))
        p.append(text(50, ry + 24, tech, size=10.5, color=INK, bold=True, anchor="start"))
        p.append(text(240, ry + 24, player, size=10, color=INK, anchor="start"))
        p.append(text(485, ry + 24, share, size=10.5, color=POS, bold=True, anchor="middle"))
        p.append(text(550, ry + 24, risk, size=9.5, color=MUTED, anchor="start"))

    p.append(rect(40, 372, 740, 28, fill=FILL, stroke=LINE, sw=1, rx=4))
    p.append(text(W / 2, 390, "Блокування будь-якого вузла паралізує світове виробництво чіпів за 2–4 тижні", size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "chokepoint-matrix.svg"), W, H, *p,
           title="Критичні вузькі місця напівпровідникової індустрії")


if __name__ == "__main__":
    fig_global_supply_map()
    fig_wafer_lead_time()
    fig_chokepoint_matrix()
    print("All figures generated successfully.")
