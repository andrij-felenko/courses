# -*- coding: utf-8 -*-
"""Фігури до теми «Планарний процес».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── локальна палітра шарів ──────────────────────────────────────────────────
SUB_N   = "#cdd9ec"   # кремній n-типу (підкладка / колектор)
P_BASE  = "#dcd0ea"   # кремній p-типу (база)
N_EMIT  = "#f6c4c0"   # кремній n⁺-типу (емітер)
OXID    = "#cfe0a8"   # діоксид кремнію SiO₂ (зеленавий діелектрик)
OXID_DK = "#9ab66a"   # темний контур оксиду
METAL   = "#d89c38"   # метал (алюміній/золото)
METED   = "#8a5810"   # обведення металу
RES_P   = "#dcd0ea"   # дифузійний резистор (p-область)


def srect(x, y, w, h, fill, stroke=INK, sw=1.5):
    """Прямокутник із прямими кутами для шарів у розрізі."""
    return rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=0)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — mesa-vs-planar: Меза проти планарного транзистора
# ════════════════════════════════════════════════════════════════════════════
def fig_mesa_vs_planar():
    W, H = 760, 360
    s = [text(W / 2, 25, "Меза-транзистор проти планарного транзистора (розріз)", size=16, bold=True)]

    # ── Ліва частина: Меза-транзистор ─────────────────────────────────────────
    s.append(rect(30, 48, 335, 292, fill="#fdfbf9", stroke="#d0c8be", sw=1.2, rx=6))
    s.append(text(197, 72, "Меза-транзистор (1954–1958)", size=13, bold=True, color=POS))

    # Підкладка колектора
    s.append(srect(60, 185, 275, 75, SUB_N, stroke="#7088a8"))
    s.append(text(197, 235, "Колектор n-Si (підкладка)", size=11, color="#3a5070"))

    # Витравлений меза-пагорб
    # База p-Si
    s.append(srect(105, 145, 185, 40, P_BASE, stroke="#6c5088"))
    s.append(text(145, 168, "База p-Si", size=10, color="#5a4070"))

    # Емітер n⁺-Si
    s.append(srect(190, 125, 80, 20, N_EMIT, stroke=POS))
    s.append(text(230, 139, "Емітер n⁺", size=10, color=POS, bold=True))

    # Витравлені урвища навколо мези
    s.append(line(60, 185, 105, 185, color="#7088a8", sw=1.5))
    s.append(line(290, 185, 335, 185, color="#7088a8", sw=1.5))

    # Навісні дротики
    s.append(line(135, 145, 115, 98, color=METED, sw=2))
    s.append(circle(135, 145, 3.5, fill=METAL, stroke=METED, sw=1.2))
    s.append(text(115, 92, "золотий дріт бази", size=9, color=METED))

    s.append(line(230, 125, 250, 98, color=METED, sw=2))
    s.append(circle(230, 125, 3.5, fill=METAL, stroke=METED, sw=1.2))
    s.append(text(250, 92, "золотий дріт емітера", size=9, color=METED))

    # Вказівники на відкриті переходи
    s.append(line(80, 145, 105, 145, color=POS, sw=1.4, dash="3,2"))
    s.append(arrow(80, 145, 103, 145, color=POS, sw=1.4))
    s.append(text(75, 140, "відкритий перехід", size=9, color=POS, anchor="end"))
    s.append(text(75, 151, "на стінці урвища", size=9, color=POS, anchor="end"))

    s.append(line(315, 145, 290, 145, color=POS, sw=1.4, dash="3,2"))
    s.append(arrow(315, 145, 292, 145, color=POS, sw=1.4))
    s.append(text(320, 140, "бруд, волога, струм", size=9, color=POS, anchor="start"))
    s.append(text(320, 151, "витоку I_CBO ~ 1-10 мкА", size=9, color=POS, anchor="start"))

    s.append(text(197, 280, "Поверхня тривимірна, з урвищами.", size=10, color=MUTED))
    s.append(text(197, 295, "Переходи виходять на голе повітря.", size=10, color=MUTED))
    s.append(text(197, 310, "З'єднання — лише ручні навісні дроти.", size=10, color=MUTED))

    # ── Права частина: Планарний транзистор ────────────────────────────────────
    s.append(rect(395, 48, 335, 292, fill="#f9fbf9", stroke="#bed0be", sw=1.2, rx=6))
    s.append(text(562, 72, "Планарний транзистор (Жан Ерні, 1959)", size=13, bold=True, color=FIELD))

    # Підкладка колектора
    s.append(srect(425, 145, 275, 115, SUB_N, stroke="#7088a8"))
    s.append(text(562, 235, "Колектор n-Si (підкладка)", size=11, color="#3a5070"))

    # Дифузійна база p-Si (заглиблена в підкладку)
    s.append(srect(465, 145, 195, 45, P_BASE, stroke="#6c5088"))
    s.append(text(500, 178, "База p-Si", size=10, color="#5a4070"))

    # Дифузійний емітер n⁺-Si (заглиблений у базу)
    s.append(srect(550, 145, 80, 22, N_EMIT, stroke=POS))
    s.append(text(590, 160, "Емітер n⁺", size=10, color=POS, bold=True))

    # Захисний шар діоксиду кремнію SiO₂ з вікнами
    # лівий оксид
    s.append(srect(425, 133, 50, 12, OXID, stroke=OXID_DK, sw=1.2))
    # між контактом бази й емітера
    s.append(srect(500, 133, 40, 12, OXID, stroke=OXID_DK, sw=1.2))
    # правий оксид
    s.append(srect(620, 133, 80, 12, OXID, stroke=OXID_DK, sw=1.2))

    # Алюмінієва металізація (плівкові доріжки поверх оксиду)
    # контакт бази
    s.append(srect(465, 130, 45, 15, METAL, stroke=METED, sw=1.2))
    s.append(text(487, 120, "Al (база)", size=9, color=METED, bold=True))

    # контакт емітера
    s.append(srect(530, 130, 100, 15, METAL, stroke=METED, sw=1.2))
    s.append(text(580, 120, "Al (емітер)", size=9, color=METED, bold=True))

    # Вказівники на захищені переходи
    s.append(line(450, 195, 465, 145, color=FIELD, sw=1.4))
    s.append(circle(465, 145, 3.5, fill=FIELD, stroke="#1e7040", sw=1.2))
    s.append(text(445, 208, "перехід герметично", size=9, color=FIELD, anchor="middle"))
    s.append(text(445, 219, "запечатаний оксидом", size=9, color=FIELD, anchor="middle"))

    s.append(line(670, 195, 630, 145, color=FIELD, sw=1.4))
    s.append(circle(630, 145, 3.5, fill=FIELD, stroke="#1e7040", sw=1.2))
    s.append(text(670, 208, "витік I_CBO < 0.1 нА", size=9, color=FIELD, anchor="middle"))
    s.append(text(670, 219, "стабільність роками", size=9, color=FIELD, anchor="middle"))

    s.append(text(562, 280, "Поверхня ідеально пласка.", size=10, color=MUTED))
    s.append(text(562, 295, "Переходи сховані під оксидом SiO₂.", size=10, color=MUTED))
    s.append(text(562, 310, "З'єднання — плоскі тонкі плівки металу.", size=10, color=MUTED))

    render(os.path.join(IMG, "mesa-vs-planar.svg"), W, H, *s)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — planar-steps: 6 головних кроків планарного процесу
# ════════════════════════════════════════════════════════════════════════════
def fig_planar_steps():
    W, H = 800, 480
    s = [text(W / 2, 24, "Виготовлення планарного BJT: шість ключових кроків", size=16, bold=True)]

    # 6 панелей у сітці 3 стовпчики x 2 рядки
    coords = [
        (40, 50),   (290, 50),  (540, 50),
        (40, 260),  (290, 260), (540, 260)
    ]
    titles = [
        "1. Термічне окиснення",
        "2. Вікно під базу",
        "3. Дифузія бази (бор)",
        "4. Вікно й дифузія емітера",
        "5. Контактні вікна",
        "6. Металізація алюмінієм"
    ]
    subtitles = [
        "Ріст суцільного SiO₂ (~500 нм)",
        "Фотолітографія + травлення BHF",
        "p-область + повторний оксид",
        "n⁺-область (фосфор) + оксид",
        "Травлення оксиду під виводи",
        "Напилення Al і малюнок доріжок"
    ]

    for i in range(6):
        x, y = coords[i]
        pw, ph = 220, 190
        s.append(rect(x, y, pw, ph, fill="#ffffff", stroke="#d0d6dc", sw=1.0, rx=4))
        s.append(text(x + pw / 2, y + 20, titles[i], size=11, bold=True, color=INK))
        s.append(text(x + pw / 2, y + 34, subtitles[i], size=9, color=MUTED))

        # Основа підкладки для всіх панелей
        bx, by, bw, bh = x + 20, y + 90, 180, 75
        s.append(srect(bx, by, bw, bh, SUB_N, stroke="#7088a8", sw=1.2))
        s.append(text(bx + bw / 2, by + bh - 10, "n-колектор", size=9, color="#405878"))

        if i == 0:
            # Крок 1: суцільний оксид
            s.append(srect(bx, by - 12, bw, 12, OXID, stroke=OXID_DK, sw=1.2))
            s.append(text(bx + bw / 2, by - 18, "оксид SiO₂", size=9, color="#4a6a1a"))

        elif i == 1:
            # Крок 2: вікно в оксиді
            s.append(srect(bx, by - 12, 45, 12, OXID, stroke=OXID_DK, sw=1.2))
            s.append(srect(bx + 135, by - 12, 45, 12, OXID, stroke=OXID_DK, sw=1.2))
            s.append(line(bx + 45, by, bx + 135, by, color="#7088a8", sw=1.2))
            s.append(text(bx + bw / 2, by - 18, "відкрите вікно", size=9, color=POS))

        elif i == 2:
            # Крок 3: дифузія бази p-Si + повторне окиснення
            s.append(srect(bx + 35, by, 110, 32, P_BASE, stroke="#6c5088", sw=1.2))
            s.append(text(bx + bw / 2, by + 18, "p-база", size=9, color="#5a4070", bold=True))
            # суцільний відновлений оксид згори
            s.append(srect(bx, by - 12, bw, 12, OXID, stroke=OXID_DK, sw=1.2))

        elif i == 3:
            # Крок 4: дифузія емітера n⁺
            s.append(srect(bx + 35, by, 110, 38, P_BASE, stroke="#6c5088", sw=1.2))
            s.append(srect(bx + 85, by, 45, 18, N_EMIT, stroke=POS, sw=1.2))
            s.append(text(bx + 107, by + 12, "n⁺", size=9, color=POS, bold=True))
            # оксид зверху
            s.append(srect(bx, by - 12, bw, 12, OXID, stroke=OXID_DK, sw=1.2))

        elif i == 4:
            # Крок 5: контактні вікна
            s.append(srect(bx + 35, by, 110, 38, P_BASE, stroke="#6c5088", sw=1.2))
            s.append(srect(bx + 85, by, 45, 18, N_EMIT, stroke=POS, sw=1.2))
            # оксид розбитий на острівці (вікна під B та E)
            s.append(srect(bx, by - 12, 35, 12, OXID, stroke=OXID_DK, sw=1.0))
            s.append(srect(bx + 64, by - 12, 20, 12, OXID, stroke=OXID_DK, sw=1.0))
            s.append(srect(bx + 122, by - 12, 58, 12, OXID, stroke=OXID_DK, sw=1.0))
            s.append(text(bx + 50, by - 16, "B", size=9, color=INK, bold=True))
            s.append(text(bx + 103, by - 16, "E", size=9, color=INK, bold=True))

        elif i == 5:
            # Крок 6: металізація алюмінієм
            s.append(srect(bx + 35, by, 110, 38, P_BASE, stroke="#6c5088", sw=1.2))
            s.append(srect(bx + 85, by, 45, 18, N_EMIT, stroke=POS, sw=1.2))
            # оксид (рознесені без колізій із металом)
            s.append(srect(bx, by - 12, 35, 12, OXID, stroke=OXID_DK, sw=1.0))
            s.append(srect(bx + 64, by - 12, 20, 12, OXID, stroke=OXID_DK, sw=1.0))
            s.append(srect(bx + 122, by - 12, 58, 12, OXID, stroke=OXID_DK, sw=1.0))
            # алюмінієві контакти
            s.append(srect(bx + 37, by - 15, 25, 15, METAL, stroke=METED, sw=1.2))
            s.append(srect(bx + 86, by - 15, 34, 15, METAL, stroke=METED, sw=1.2))
            s.append(text(bx + 49, by - 19, "Al-база", size=9, color=METED, bold=True))
            s.append(text(bx + 103, by - 19, "Al-емітер", size=9, color=METED, bold=True))

    render(os.path.join(IMG, "planar-steps.svg"), W, H, *s)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — junction-passivation: Механізм пасивації переходу під оксидом
# ════════════════════════════════════════════════════════════════════════════
def fig_junction_passivation():
    W, H = 760, 340
    s = [text(W / 2, 25, "Мікроструктура пасивації: бічна дифузія під оксидну маску", size=16, bold=True)]

    # Фонова кремнієва підкладка n-Si
    s.append(srect(60, 120, 640, 160, SUB_N, stroke="#7088a8", sw=1.5))
    s.append(text(130, 260, "Підкладка n-Si (колектор)", size=12, color="#3a5070", bold=True))

    # Дифузійна область p-бази із закругленими краями під оксидом
    # Головне тіло p-бази
    s.append(srect(220, 120, 320, 80, P_BASE, stroke="#6c5088", sw=1.5))
    # Ліве й праве бічне розширення під оксид
    s.append('<path d="M 220 120 C 180 120 170 150 170 170 C 170 190 190 200 220 200 Z" fill="%s" stroke="#6c5088" stroke-width="1.5"/>' % P_BASE)
    s.append('<path d="M 540 120 C 580 120 590 150 590 170 C 590 190 570 200 540 200 Z" fill="%s" stroke="#6c5088" stroke-width="1.5"/>' % P_BASE)
    s.append(text(380, 165, "Дифузійна область p-Si (база)", size=12, color="#5a4070", bold=True))

    # Маска діоксиду кремнію SiO₂ з вікном посередині
    # Лівий блок оксиду (перекриває край переходу!)
    s.append(srect(60, 96, 210, 24, OXID, stroke=OXID_DK, sw=1.5))
    s.append(text(150, 85, "Захисний шар SiO₂ (~500 нм)", size=10, color="#4a6a1a", bold=True))

    # Правий блок оксиду
    s.append(srect(490, 96, 210, 24, OXID, stroke=OXID_DK, sw=1.5))
    s.append(text(610, 85, "Захисний шар SiO₂", size=10, color="#4a6a1a", bold=True))

    # Відкрите вікно в масці
    s.append(line(270, 60, 270, 115, color=POS, sw=1.2, dash="3,3"))
    s.append(line(490, 60, 490, 115, color=POS, sw=1.2, dash="3,3"))
    s.append(arrow(340, 70, 275, 70, color=POS, sw=1.2))
    s.append(arrow(420, 70, 485, 70, color=POS, sw=1.2))
    s.append(text(380, 73, "вікно в оксиді", size=10, color=POS, bold=True))

    # Потік домішки
    for dx in range(295, 470, 25):
        s.append(arrow(dx, 82, dx, 112, color="#7a5090", sw=1.4))
    s.append(text(380, 102, "потік атомів бору (B)", size=10, color="#7a5090"))

    # Вихід p-n переходу строго під оксид
    s.append(circle(175, 120, 4.5, fill=FIELD, stroke="#1e7040", sw=1.4))
    s.append(line(175, 120, 130, 160, color=FIELD, sw=1.4))
    s.append(text(130, 175, "p-n перехід виходить", size=9, color=FIELD, bold=True))
    s.append(text(130, 187, "під нативний оксид!", size=9, color=FIELD, bold=True))

    s.append(circle(585, 120, 4.5, fill=FIELD, stroke="#1e7040", sw=1.4))
    s.append(line(585, 120, 630, 160, color=FIELD, sw=1.4))
    s.append(text(630, 175, "герметична ізоляція", size=9, color=FIELD, bold=True))
    s.append(text(630, 187, "від зовнішнього середовища", size=9, color=FIELD, bold=True))

    # Розміри: глибина xj та бічна дифузія x_lat
    s.append(line(270, 120, 270, 200, color=MUTED, sw=1.0, dash="2,2"))
    s.append(line(265, 200, 275, 200, color=MUTED, sw=1.0))
    s.append(line(210, 205, 270, 205, color=MUTED, sw=1.0))
    s.append(text(240, 218, "x_j (глибина)", size=9, color=MUTED))

    s.append(line(175, 115, 175, 60, color=MUTED, sw=1.0, dash="2,2"))
    s.append(line(270, 115, 270, 60, color=MUTED, sw=1.0, dash="2,2"))
    s.append(line(175, 65, 270, 65, color=MUTED, sw=1.0))
    s.append(text(222, 58, "x_lat ≈ 0.75-0.8 x_j", size=9, color=MUTED))

    s.append(text(W / 2, 305, "Атоми домішки дифундують углиб і вбік під край оксиду.", size=11, color=INK, italic=True))
    s.append(text(W / 2, 322, "Металургійна межа p-n переходу ніколи в житті не контактує з повітрям чи брудом.", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "junction-passivation.svg"), W, H, *s)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — monolithic-interconnect: Доріжки металу на оксиді (Нойс)
# ════════════════════════════════════════════════════════════════════════════
def fig_monolithic_interconnect():
    W, H = 760, 320
    s = [text(W / 2, 25, "Монолітна інтеграція Роберта Нойса: надруковані з'єднання", size=16, bold=True)]

    # Спільна підкладка p-типу (ізоляція підкладкою)
    s.append(srect(40, 130, 680, 130, "#e4dcf0", stroke="#786098", sw=1.4))
    s.append(text(80, 245, "Підкладка p-Si", size=11, color="#5a4070", bold=True))

    # Кишеня 1: NPN транзистор у n-острівці
    s.append(srect(140, 130, 240, 95, SUB_N, stroke="#7088a8", sw=1.2))
    s.append(text(185, 215, "n-кишеня (колектор)", size=9, color="#3a5070"))
    # База p-Si
    s.append(srect(170, 130, 130, 50, P_BASE, stroke="#6c5088", sw=1.2))
    s.append(text(210, 172, "p-база", size=9, color="#5a4070"))
    # Емітер n⁺
    s.append(srect(230, 130, 50, 22, N_EMIT, stroke=POS, sw=1.2))
    s.append(text(255, 145, "n⁺", size=9, color=POS, bold=True))
    # Колекторний контакт n⁺
    s.append(srect(330, 130, 35, 22, N_EMIT, stroke="#7088a8", sw=1.2))
    s.append(text(347, 145, "n⁺", size=9, color="#3a5070"))

    # Кишеня 2: Дифузійний резистор у n-острівці
    s.append(srect(440, 130, 220, 95, SUB_N, stroke="#7088a8", sw=1.2))
    s.append(text(550, 215, "n-кишеня (ізоляція резистора)", size=9, color="#3a5070"))
    # Тіло резистора (смужка p-Si)
    s.append(srect(480, 130, 140, 40, RES_P, stroke="#6c5088", sw=1.2))
    s.append(text(550, 162, "p-дифузійний резистор R", size=9, color="#5a4070", bold=True))

    # Ізолюючий суцільний оксид SiO₂ з вікнами
    s.append(srect(40, 116, 145, 14, OXID, stroke=OXID_DK, sw=1.0))
    s.append(srect(205, 116, 20, 14, OXID, stroke=OXID_DK, sw=1.0))
    s.append(srect(285, 116, 40, 14, OXID, stroke=OXID_DK, sw=1.0))
    s.append(srect(370, 116, 105, 14, OXID, stroke=OXID_DK, sw=1.0))
    s.append(srect(500, 116, 100, 14, OXID, stroke=OXID_DK, sw=1.0))
    s.append(srect(625, 116, 95, 14, OXID, stroke=OXID_DK, sw=1.0))

    # Алюмінієві доріжки (металізація Нойса):
    # Доріжка 1: вивід бази
    s.append(srect(170, 100, 35, 18, METAL, stroke=METED, sw=1.2))
    s.append(text(187, 92, "База (B)", size=9, color=METED, bold=True))

    # Доріжка 2: вивід емітера
    s.append(srect(225, 100, 60, 18, METAL, stroke=METED, sw=1.2))
    s.append(text(255, 92, "Емітер (E)", size=9, color=METED, bold=True))

    # Доріжка 3: Монолітне з'єднання Колектор транзистора → Резистор!
    # Біжить просто по поверхні оксиду між транзистором і резистором!
    s.append(srect(325, 100, 180, 18, METAL, stroke=METED, sw=1.5))
    s.append(text(415, 88, "Надрукований дріт Al: Колектор C → Резистор R", size=9, color=METED, bold=True))

    # Доріжка 4: другий вивід резистора
    s.append(srect(595, 100, 35, 18, METAL, stroke=METED, sw=1.2))
    s.append(text(612, 92, "Живлення Vcc", size=9, color=METED, bold=True))

    s.append(text(W / 2, 280, "Алюміній напилюється суцільною плівкою, а маска фотолітографії витравлює доріжки.", size=11, color=INK, italic=True))
    s.append(text(W / 2, 298, "Доріжка спирається на ізолюючий оксид: жодного навісного дроту чи ручного паяння.", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "monolithic-interconnect.svg"), W, H, *s)


if __name__ == "__main__":
    fig_mesa_vs_planar()
    fig_planar_steps()
    fig_junction_passivation()
    fig_monolithic_interconnect()
    print("OK: mesa-vs-planar.svg, planar-steps.svg, junction-passivation.svg, monolithic-interconnect.svg -> ./img/")
