# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра для креслень та схем
ACCENT = "#2563eb"
ACCENT_BG = "#eff6ff"
BORDER = "#94a3b8"
TEXT_DARK = "#0f172a"
SUCCESS = "#16a34a"
SUCCESS_BG = "#f0fdf4"
DANGER = "#dc2626"
DANGER_BG = "#fef2f2"
WARN = "#d97706"
WARN_BG = "#fffbeb"
PURPLE = "#7c3aed"
PURPLE_BG = "#f5f3ff"


# ── 1. rev-a-to-rev-b-lifecycle.svg ──────────────────────────────────────────
def fig_lifecycle():
    W, H = 860, 360
    p = []
    p.append(text(W/2, 26, "Інженерний цикл переходу від прототипу Rev A до ревізії Rev B", size=14, bold=True))

    steps = [
        ("1. Дослідна експлуатація Rev A", [
            "• Оживлення плати (Bringup)",
            "• Верифікація за ТЗ і Worst-case",
            "• Випробування на вібрацію і кліматику",
            "• Монтаж тимчасових дротів (bodge)"
        ], "#3b82f6", "#eff6ff"),
        ("2. Журнал дефектів (Errata)", [
            "• Реєстрація всіх перерізів доріжок",
            "• Документування невідповідності пінів",
            "• Звіт технолога SMT про брак пайки",
            "• Аналіз ланцюга постачання (EOL)"
        ], "#d97706", "#fffbeb"),
        ("3. Тріаж та інженерний фільтр", [
            "• ЖОРСТКИЙ ЗАХИСТ: стабільні вузли",
            "• Заборона випадкових змін чіпів",
            "• Уніфікація пасивних номіналів",
            "• Перевірка збереження контуру"
        ], "#dc2626", "#fef2f2"),
        ("4. Випуск і регресія Rev B", [
            "• Розведення виправлень у міді",
            "• Додавання Board ID для прошивки",
            "• Виробництво серійної партії",
            "• Регресійне тестування"
        ], "#16a34a", "#f0fdf4")
    ]

    card_w = 190
    card_h = 240
    gap = 22
    x0 = (W - (4 * card_w + 3 * gap)) / 2
    y0 = 65

    for i, (title, lines, col, bg) in enumerate(steps):
        cx = x0 + i * (card_w + gap)
        p.append(rect(cx, y0, card_w, card_h, fill=bg, stroke=col, sw=1.5, rx=6))
        
        # Заголовок картки
        p.append(rect(cx, y0, card_w, 36, fill=col, stroke=col, sw=1.0, rx=6))
        p.append(text(cx + card_w/2, y0 + 22, title, size=10, bold=True, color="#ffffff"))

        ly = y0 + 60
        for ln in lines:
            p.append(text(cx + 10, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
            ly += 26

        # Стрілка між етапами
        if i < 3:
            ax = cx + card_w + 2
            ay = y0 + card_h / 2
            p.append(arrow(ax, ay, ax + gap - 4, ay, color="#64748b", sw=1.8))

    p.append(line(40, 328, 820, 328, color="#cbd5e1", sw=1.0))
    p.append(text(W/2, 346, "Головний принцип: Rev B виправляє зареєстровані дефекти, а не створює нову схемотехніку з нуля", size=10.5, bold=True, color=TEXT_DARK))

    render(os.path.join(OUT, "rev-a-to-rev-b-lifecycle.svg"), W, H, *p)


# ── 2. bodge-wire-to-copper.svg ──────────────────────────────────────────────
def fig_bodge_vs_copper():
    W, H = 860, 380
    p = []
    p.append(text(W/2, 26, "Перехід від синіх дротів (Rev A) до цілісної топології міді (Rev B)", size=14, bold=True))

    half_w = 390
    h_box = 280
    y0 = 55

    # Ліва колонка: Rev A з bodge wire
    p.append(rect(25, y0, half_w, h_box, fill="#fff5f5", stroke="#dc2626", sw=1.5, rx=8))
    p.append(rect(25, y0, half_w, 34, fill="#dc2626", stroke="#dc2626", sw=1.0, rx=8))
    p.append(text(25 + half_w/2, y0 + 22, "Rev A: Тимчасовий ремонт (Bodge Wire)", size=11, bold=True, color="#ffffff"))

    # Спрощена схема джгута-дроту
    p.append(rect(45, y0 + 50, 70, 45, fill="#ffffff", stroke="#64748b", sw=1.2, rx=4))
    p.append(text(80, y0 + 76, "U1 (MCU)", size=9.5, bold=True, color=TEXT_DARK))

    p.append(rect(325, y0 + 50, 70, 45, fill="#ffffff", stroke="#64748b", sw=1.2, rx=4))
    p.append(text(360, y0 + 76, "U2 (Sensor)", size=9.5, bold=True, color=TEXT_DARK))

    # Синій дріт дугою в повітрі
    p.append(line(115, y0 + 72, 160, y0 + 52, color="#2563eb", sw=2.2))
    p.append(line(160, y0 + 52, 280, y0 + 52, color="#2563eb", sw=2.2))
    p.append(line(280, y0 + 52, 325, y0 + 72, color="#2563eb", sw=2.2))
    p.append(text(220, y0 + 44, "AWG 30 дріт у повітрі", size=9.5, bold=True, color="#2563eb"))

    # Перерізана доріжка під ним
    p.append(line(115, y0 + 110, 195, y0 + 110, color="#94a3b8", sw=1.8))
    p.append(line(205, y0 + 102, 215, y0 + 118, color="#dc2626", sw=2.5))
    p.append(line(205, y0 + 118, 215, y0 + 102, color="#dc2626", sw=2.5))
    p.append(line(225, y0 + 110, 325, y0 + 110, color="#94a3b8", sw=1.8))
    p.append(text(210, y0 + 128, "Переріз скальпелем", size=9.5, color="#dc2626"))

    flaws = [
        "• Паразитна індуктивність контуру: L ~ 1.2 нГн/мм",
        "• Розірваний зворотний шлях струму на шарі GND",
        "• Антена для наведених ЕМ-завад і перехресних наводок",
        "• Ризик відриву пайки при вібрації та термоциклі",
        "• Непридатність для серійного складання автоматом"
    ]
    ly = y0 + 155
    for fl in flaws:
        p.append(text(40, ly, fl, size=9.5, color="#991b1b", anchor="start"))
        ly += 22

    # Права колонка: Rev B з нормальною трасою
    p.append(rect(445, y0, half_w, h_box, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    p.append(rect(445, y0, half_w, 34, fill="#16a34a", stroke="#16a34a", sw=1.0, rx=8))
    p.append(text(445 + half_w/2, y0 + 22, "Rev B: Трасування у міді на друкованій платі", size=11, bold=True, color="#ffffff"))

    # Спрощена схема мікрополоска
    p.append(rect(465, y0 + 50, 70, 45, fill="#ffffff", stroke="#64748b", sw=1.2, rx=4))
    p.append(text(500, y0 + 76, "U1 (MCU)", size=9.5, bold=True, color=TEXT_DARK))

    p.append(rect(745, y0 + 50, 70, 45, fill="#ffffff", stroke="#64748b", sw=1.2, rx=4))
    p.append(text(780, y0 + 76, "U2 (Sensor)", size=9.5, bold=True, color=TEXT_DARK))

    # Мідна доріжка на внутрішньому або зовнішньому шарі
    p.append(line(535, y0 + 72, 745, y0 + 72, color="#16a34a", sw=3.0))
    p.append(text(640, y0 + 62, "Шина 50 Ом з суцільним екраном", size=9.5, bold=True, color="#15803d"))

    # Опорна земля знизу
    p.append(rect(535, y0 + 95, 210, 14, fill="#bbf7d0", stroke="#16a34a", sw=1.0))
    p.append(text(640, y0 + 106, "Шар суцільної землі GND (L2)", size=9.5, color="#14532d"))

    advantages = [
        "• Контрольований хвильовий опір і мінімальна площа петлі",
        "• Неперервний шар зворотного струму безпосередньо під трасою",
        "• Повна відповідність стандартам вібростійкості та надійності",
        "• Захист паяльною маскою від корозії та КЗ",
        "• Нульові додаткові трудовитрати при монтажі SMT"
    ]
    ly = y0 + 155
    for adv in advantages:
        p.append(text(460, ly, adv, size=9.5, color="#166534", anchor="start"))
        ly += 22

    p.append(line(40, 350, 820, 350, color="#cbd5e1", sw=1.0))
    p.append(text(W/2, 368, "Будь-який синій дріт у Rev A має стати перевіреним трасуванням у схемі та топології Rev B", size=10, bold=True, color=TEXT_DARK))

    render(os.path.join(OUT, "bodge-wire-to-copper.svg"), W, H, *p)


# ── 3. forbidden-vs-allowed-zones.svg ────────────────────────────────────────
def fig_zones():
    W, H = 860, 400
    p = []
    p.append(text(W/2, 26, "Карта втручання в Rev B: заборонені та дозволені зони змін", size=14, bold=True))

    col_w = 390
    h_box = 305
    y0 = 55

    # Ліва колонка: ЗАБОРОНЕНО ЗМІНЮВАТИ
    p.append(rect(25, y0, col_w, h_box, fill="#fff5f5", stroke="#dc2626", sw=1.5, rx=8))
    p.append(rect(25, y0, col_w, 36, fill="#dc2626", stroke="#dc2626", sw=1.0, rx=8))
    p.append(text(25 + col_w/2, y0 + 23, "⛔ СУВОРО ЗАБОРОНЕНО РУХАТИ (Locked)", size=11, bold=True, color="#ffffff"))

    locked_items = [
        ("ВЧ/НВЧ тракт і антени (RF 2.4/5.8 ГГц):", [
            "• Узгоджувальні кола (П-фільтри), мікрополоски 50 Ом",
            "• Keep-out зони навколо чіп-антен або PCB-пачів"
        ]),
        ("Силові імпульсні контури (DC-DC Switches):", [
            "• Гаряча петля Cin → MOSFET → Діод → GND",
            "• Вузол комутації SW (мінімальна площа міді для EMI)"
        ]),
        ("Швидкісні диференційні пари та шини:", [
            "• USB High-Speed, Ethernet MII, MIPI, DDR пам'ять",
            "• Кварцовий резонатор і його обв'язка (навантажувальні C)"
        ]),
        ("Механічний конверт і база чіпів:", [
            "• Координати кріпильних отворів і контур плати",
            "• Заміна базового МК на іншу родину без гострої потреби"
        ])
    ]

    ly = y0 + 56
    for title, lines in locked_items:
        p.append(text(40, ly, title, size=10, bold=True, color="#991b1b", anchor="start"))
        ly += 16
        for ln in lines:
            p.append(text(46, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
            ly += 15
        ly += 5

    # Права колонка: ДОЗВОЛЕНО ТА НЕОБХІДНО ВНОСИТИ
    p.append(rect(445, y0, col_w, h_box, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    p.append(rect(445, y0, col_w, 36, fill="#16a34a", stroke="#16a34a", sw=1.0, rx=8))
    p.append(text(445 + col_w/2, y0 + 23, "✅ ОБОВ'ЯЗКОВО ТА ДОЗВОЛЕНО (Allowed/Required)", size=11, bold=True, color="#ffffff"))

    allowed_items = [
        ("Виправлення дефектів з Errata:", [
            "• Інвертовані виводи RX/TX, переплутані піни RESET/BOOT",
            "• Додавання відсутніх підтяжок I2C, захисних діодів TVS"
        ]),
        ("Оптимізація футпрінтів під монтаж (DFM):", [
            "• Подовження контактних майданчиків QFN для паяльника",
            "• Термобар'єри (Thermal Relief) для рівномірного прогріву",
            "• Збільшення зазорів під паяльну маску між виводами 0.5 мм"
        ]),
        ("Уніфікація BOM та оптимізація фідерів:", [
            "• Зведення номіналів резисторів (4.7к + 5.1к → 10к)",
            "• Заміна компонентів з довгим строком доставки на AVL"
        ]),
        ("Контрольні точки та ідентифікація:", [
            "• Додавання тестових майданчиків (TP) під голчастий адаптер",
            "• Апаратний дільник або strapping-піни Board ID"
        ])
    ]

    ly = y0 + 56
    for title, lines in allowed_items:
        p.append(text(460, ly, title, size=10, bold=True, color="#166534", anchor="start"))
        ly += 16
        for ln in lines:
            p.append(text(466, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
            ly += 15
        ly += 5

    p.append(line(40, 375, 820, 375, color="#cbd5e1", sw=1.0))
    p.append(text(W/2, 392, "Якщо перевірений вузол працює без завад у Rev A — будь-яке його перетрасування в Rev B є ризиком", size=10, bold=True, color=TEXT_DARK))

    render(os.path.join(OUT, "forbidden-vs-allowed-zones.svg"), W, H, *p)


# ── 4. bom-consolidation-feeders.svg ─────────────────────────────────────────
def fig_bom_consolidation():
    W, H = 860, 370
    p = []
    p.append(text(W/2, 26, "Оптимізація BOM у Rev B: уніфікація номіналів та скорочення фідерів", size=14, bold=True))

    box_w = 380
    box_h = 270
    y0 = 60

    # Ліва колонка: Rev A — хаотичний вибір номіналів
    p.append(rect(35, y0, box_w, box_h, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=8))
    p.append(rect(35, y0, box_w, 36, fill="#d97706", stroke="#d97706", sw=1.0, rx=8))
    p.append(text(35 + box_w/2, y0 + 23, "Rev A: 38 унікальних позицій (BOM Lines)", size=11, bold=True, color="#ffffff"))

    r_a = [
        "• Резистори 0603: 1k, 1.2k, 2.2k, 4.7k, 5.1k, 10k, 12k, 47k, 100k",
        "• Конденсатори: 10pF, 22pF, 100nF 16V, 100nF 50V, 1uF 10V, 4.7uF",
        "• 40 фідерів задіяно на Pick & Place автоматі",
        "• Вартість переналаштування лінії: 38 позицій × $15 = $570",
        "• Висока ймовірність помилки заправки стрічки оператором",
        "• Залишки на складі: 20 недовикористаних котушок"
    ]
    ly = y0 + 58
    for ln in r_a:
        p.append(text(48, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
        ly += 32

    # Права колонка: Rev B — уніфікований BOM
    p.append(rect(445, y0, box_w, box_h, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    p.append(rect(445, y0, box_w, 36, fill="#16a34a", stroke="#16a34a", sw=1.0, rx=8))
    p.append(text(445 + box_w/2, y0 + 23, "Rev B: 16 уніфікованих позицій (BOM Lines)", size=11, bold=True, color="#ffffff"))

    r_b = [
        "• Стандартні резистори 0603 1%: 100R, 1k, 10k, 100k (E6 база)",
        "• Конденсатори 0603 X7R: 22pF (кварц), 100nF 50V, 10uF 25V",
        "• Лише 18 фідерів на автоматі (швидкий монтаж за один прохід)",
        "• Вартість переналаштування лінії: $240 (економія 58%)",
        "• Оптова закупівля котушок по 5000/10000 шт (знижка до 40%)",
        "• Мінімальний складський запас, захист від зупинки лінії"
    ]
    ly = y0 + 58
    for ln in r_b:
        p.append(text(458, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
        ly += 32

    p.append(line(40, 345, 820, 345, color="#cbd5e1", sw=1.0))
    p.append(text(W/2, 362, "Уніфікація номіналів без погіршення режимів роботи скорочує вартість і час монтажу серії", size=10, bold=True, color=TEXT_DARK))

    render(os.path.join(OUT, "bom-consolidation-feeders.svg"), W, H, *p)


# ── 5. hardware-revision-id-circuits.svg ─────────────────────────────────────
def fig_revision_id():
    W, H = 860, 380
    p = []
    p.append(text(W/2, 26, "Апаратна ідентифікація ревізії плати (Board Revision ID) для прошивки", size=14, bold=True))

    col_w = 385
    h_box = 280
    y0 = 60

    # Варіант 1: Цифровий Strapping (GPIO Pins)
    p.append(rect(30, y0, col_w, h_box, fill="#f8fafc", stroke="#3b82f6", sw=1.5, rx=8))
    p.append(rect(30, y0, col_w, 36, fill="#3b82f6", stroke="#3b82f6", sw=1.0, rx=8))
    p.append(text(30 + col_w/2, y0 + 23, "Варіант А: Двійковий Strapping (2-3 GPIO)", size=11, bold=True, color="#ffffff"))

    # Схема підтяжок
    p.append(rect(50, y0 + 50, 100, 75, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=4))
    p.append(text(100, y0 + 72, "REV_BIT0", size=9.5, bold=True, color="#1e40af"))
    p.append(text(100, y0 + 90, "Pull-up 10k", size=9.5, color=TEXT_DARK))
    p.append(text(100, y0 + 108, "або Pull-down", size=9.5, color=MUTED))

    p.append(rect(165, y0 + 50, 100, 75, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=4))
    p.append(text(215, y0 + 72, "REV_BIT1", size=9.5, bold=True, color="#1e40af"))
    p.append(text(215, y0 + 90, "Pull-up 10k", size=9.5, color=TEXT_DARK))
    p.append(text(215, y0 + 108, "або Pull-down", size=9.5, color=MUTED))

    p.append(arrow(270, y0 + 87, 305, y0 + 87, color="#2563eb", sw=1.5))
    p.append(rect(310, y0 + 65, 90, 45, fill="#ffffff", stroke="#64748b", sw=1.2, rx=4))
    p.append(text(355, y0 + 85, "MCU GPIO", size=9.5, bold=True, color=TEXT_DARK))
    p.append(text(355, y0 + 99, "(Читання)", size=9.5, color=MUTED))

    desc_a = [
        "• Rev A: `00` (обидва резистори на GND)",
        "• Rev B: `01` (BIT0 на 3.3V, BIT1 на GND)",
        "• Rev C: `10` (BIT0 на GND, BIT1 на 3.3V)",
        "• Плюси: миттєве читання без ініціалізації АЦП",
        "• Мінуси: витрачає 2-3 виводи мікроконтролера"
    ]
    ly = y0 + 145
    for ln in desc_a:
        p.append(text(45, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
        ly += 23

    # Варіант 2: Резистивний дільник на один канал АЦП
    p.append(rect(445, y0, col_w, h_box, fill="#f8fafc", stroke="#7c3aed", sw=1.5, rx=8))
    p.append(rect(445, y0, col_w, 36, fill="#7c3aed", stroke="#7c3aed", sw=1.0, rx=8))
    p.append(text(445 + col_w/2, y0 + 23, "Варіант Б: Резистивний дільник (1 пін АЦП)", size=11, bold=True, color="#ffffff"))

    # Схема дільника
    p.append(rect(470, y0 + 50, 160, 75, fill="#f5f3ff", stroke="#7c3aed", sw=1.2, rx=4))
    p.append(text(550, y0 + 72, "Дільник R1 / R2 (1%)", size=9.5, bold=True, color="#5b21b6"))
    p.append(text(550, y0 + 90, "+ фільтр C = 100 нФ", size=9.5, color=TEXT_DARK))
    p.append(text(550, y0 + 108, "Напруга 0..3.3 В", size=9.5, color=MUTED))

    p.append(arrow(635, y0 + 87, 675, y0 + 87, color="#7c3aed", sw=1.5))
    p.append(rect(680, y0 + 65, 120, 45, fill="#ffffff", stroke="#64748b", sw=1.2, rx=4))
    p.append(text(740, y0 + 85, "MCU ADC_IN", size=9.5, bold=True, color=TEXT_DARK))
    p.append(text(740, y0 + 99, "(1 канал виміру)", size=9.5, color=MUTED))

    desc_b = [
        "• Rev A: 0.00 В (GND, R1 DNP, R2 10k)",
        "• Rev B: 0.82 В (R1 30k, R2 10k, Vref=3.3V)",
        "• Rev C: 1.65 В (R1 10k, R2 10k)",
        "• Плюси: економить піни (потрібен лише 1 пін АЦП)",
        "• Захист: допуски вікна напруги ±150 мВ проти шуму"
    ]
    ly = y0 + 145
    for ln in desc_b:
        p.append(text(460, ly, ln, size=9.5, color=TEXT_DARK, anchor="start"))
        ly += 23

    p.append(line(40, 352, 820, 352, color="#cbd5e1", sw=1.0))
    p.append(text(W/2, 369, "Ідентифікатор ревізії дозволяє одній прошивці автоматично конфігурувати периферію під будь-яку плату", size=10, bold=True, color=TEXT_DARK))

    render(os.path.join(OUT, "hardware-revision-id-circuits.svg"), W, H, *p)


if __name__ == "__main__":
    fig_lifecycle()
    fig_bodge_vs_copper()
    fig_zones()
    fig_bom_consolidation()
    fig_revision_id()
    print("All 5 figures generated successfully in", OUT)
