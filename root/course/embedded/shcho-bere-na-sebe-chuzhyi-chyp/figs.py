# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. monolithic-vs-companion-architecture: Порівняння монолітного та делегованого підходів ───
def fig_monolithic_vs_companion():
    W, H = 960, 480
    p = []

    # Ліва половина — Перевантажений монолітний мікроконтролер
    p.append(rect(20, 35, 450, 395, fill="#fdf4f4", stroke=POS, sw=1.5, rx=8))
    p.append(text(245, 60, "Монолітна архітектура (All-in-One)", size=13, color=POS, bold=True))
    p.append(text(245, 78, "Одне ядро виконує абсолютно всі задачі програмно", size=10, color=MUTED))

    # Ядро Host MCU
    p.append(rect(35, 95, 420, 185, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(245, 118, "Головний мікроконтролер (Host MCU)", size=12, color=POS, bold=True))
    p.append(text(245, 136, "Cortex-M4 @ 168 МГц · Навантаження 94%", size=10, color=INK))

    # Задачі всередині ядра
    p.append(rect(45, 150, 90, 50, fill="#fbebeb", stroke=POS, sw=1, rx=4))
    p.append(text(90, 170, "FOC ШІМ", size=10, color=POS, bold=True))
    p.append(text(90, 187, "20 кГц ISR", size=9, color=MUTED))

    p.append(rect(148, 150, 95, 50, fill="#fbebeb", stroke=POS, sw=1, rx=4))
    p.append(text(195, 170, "Тач-матриця", size=10, color=POS, bold=True))
    p.append(text(195, 187, "Опитування", size=9, color=MUTED))

    p.append(rect(255, 150, 90, 50, fill="#fbebeb", stroke=POS, sw=1, rx=4))
    p.append(text(300, 170, "ECC / TLS", size=10, color=POS, bold=True))
    p.append(text(300, 187, "Мільйони тактів", size=9, color=MUTED))

    p.append(rect(355, 150, 90, 50, fill="#fbebeb", stroke=POS, sw=1, rx=4))
    p.append(text(400, 170, "Кулони АКБ", size=10, color=POS, bold=True))
    p.append(text(400, 187, "Інтегрування", size=9, color=MUTED))

    p.append(rect(45, 215, 400, 50, fill="#fff0f0", stroke=POS, sw=1, rx=4))
    p.append(text(245, 235, "Конфлікти пріоритетів переривань (IRQ Jitter)", size=10, color=POS, bold=True))
    p.append(text(245, 252, "Пропуск кроків двигуна під час обчислення криптографії", size=9, color=MUTED))

    # Наслідки моноліту
    b_left, _, _ = textbox(245, 345,
                           "• Висока тактова частота ядра → споживання до 80 мА\n"
                           "• Жорсткий Real-Time ламається при накладанні подій\n"
                           "• Flash/RAM забиті кодом криптографії, DSP та жестів\n"
                           "• Неможливість спати: ядро мусить постійно опитувати піни",
                           size=10, fill="#ffffff", stroke=POS, min_w=420)
    p.append(b_left)

    # Права половина — Гетерогенна система з супутніми чипами
    p.append(rect(490, 35, 450, 395, fill="#edf8f1", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(715, 60, "Делегована архітектура (Host + Companion ICs)", size=13, color=FIELD, bold=True))
    p.append(text(715, 78, "Кожна критична функція має власний кремнієвий співпроцесор", size=10, color=MUTED))

    # Host MCU розвантажений
    p.append(rect(505, 95, 175, 120, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(592, 118, "Host MCU (Базовий)", size=12, color=FIELD, bold=True))
    p.append(text(592, 136, "Cortex-M0+ @ 32 МГц", size=10, color=INK))
    p.append(text(592, 154, "Навантаження: 6%", size=10, color=FIELD, bold=True))
    p.append(text(592, 172, "Чиста бізнес-логіка", size=10, color=MUTED))
    p.append(text(592, 190, "Спить 95% часу", size=10, color=FIELD))

    # Супутні спеціалізовані чипи
    chips = [
        ("TMC2209", "FOC Вектор", 735, 95),
        ("FT6236", "Сенсорний екран", 835, 95),
        ("ATECC608", "Крипточип", 735, 160),
        ("BQ27441", "Fuel Gauge АКБ", 835, 160)
    ]
    for name, desc, cx, cy in chips:
        p.append(rect(cx, cy, 90, 55, fill="#ffffff", stroke=FIELD, sw=1.1, rx=4))
        p.append(text(cx + 45, cy + 22, name, size=10, color=FIELD, bold=True))
        p.append(text(cx + 45, cy + 40, desc, size=9, color=INK))

    # Шина взаємодії
    p.append(arrow(680, 130, 735, 130, color=FIELD, sw=1.5))
    p.append(arrow(735, 185, 680, 185, color=FIELD, sw=1.5))
    p.append(text(707, 122, "SPI", size=9, color=FIELD, bold=True))
    p.append(text(707, 197, "I²C/INT", size=9, color=FIELD, bold=True))

    # Наслідки делегування
    b_right, _, _ = textbox(715, 345,
                            "• Низька частота ядра → споживання в рази менше (Host < 3 мА)\n"
                            "• Нуль джиттеру: FOC та обробка дотиків працюють апаратно\n"
                            "• Економія Flash/RAM: прошивка без важких математичних бібліотек\n"
                            "• Глибокий сон: Host спить, супутні чипи будять його лінією INT",
                            size=10, fill="#ffffff", stroke=FIELD, min_w=420)
    p.append(b_right)

    # Підсумок знизу
    b_bot, _, _ = textbox(W / 2, 452,
                          "Делегування перетворює перевантажений моноліт на надійну систему: апаратні чипи знімають жорсткий Real-Time, зберігаючи енергію та стабільність.",
                          size=10, stroke=MUTED, fill="#ffffff", min_w=920)
    p.append(b_bot)

    render(os.path.join(OUT, "monolithic-vs-companion-architecture.svg"), W, H, *p,
           title="Архітектурне порівняння: перевантажений монолітний процесор проти гетерогенної системи")


# ── 2. companion-chips-spectrum: Спектр супутніх мікросхем та їхній кремнієвий контракт ───
def fig_companion_chips_spectrum():
    W, H = 960, 470
    p = []

    # 5 блоків по вертикалі / горизонталі
    cols = [
        {
            "x": 20, "w": 175, "title": "Secure Element", "chip": "ATECC608 / TPM",
            "color": "#7a2e1d", "bg": "#fcf3f0",
            "inside": ["Захищена пам'ять", "EEPROM з екраном", "TRNG шум переходу", "Акселератор ECC/SHA", "Захист від DPA/глітчу"],
            "contract": ["I²C запит: Hash", "I²C відповідь: (r, s)", "Ключ не покидає чип"]
        },
        {
            "x": 205, "w": 175, "title": "Audio DSP Codec", "chip": "WM8960 / PCM5102",
            "color": "#1b4d3e", "bg": "#eef8f3",
            "inside": ["Параметричний EQ", "АРП / Dynamic Range", "Sigma-Delta ЦАП/АЦП", "Апаратне змішування", "Вбудований драйвер"],
            "contract": ["I²S потік через DMA", "I²C: гучність, EQ", "Нуль тактів CPU на FIR"]
        },
        {
            "x": 390, "w": 175, "title": "Touch Controller", "chip": "FT6236 / GT911",
            "color": "#0d47a1", "bg": "#eef4fd",
            "inside": ["Сканування матриці", "ΔC ємнісні виміри", "Фільтр мережних завад", "Трекінг до 5 точок", "Детекція жестів"],
            "contract": ["Лінія INT при дотику", "I²C: координати X, Y", "Host не сканує сітку"]
        },
        {
            "x": 575, "w": 175, "title": "Motor FOC Driver", "chip": "TMC2209 / TMC5160",
            "color": "#5c2d91", "bg": "#f7f0fc",
            "inside": ["Векторний FOC 20 кГц", "Мікрокрок до 1/256", "StealthChop (тиша)", "StallGuard детекція", "Апаратний профіль Ramp"],
            "contract": ["Імпульси STEP/DIR", "SPI: цільова позиція", "Чип сам крутить синус"]
        },
        {
            "x": 760, "w": 180, "title": "Battery Fuel Gauge", "chip": "BQ27441 / MAX17055",
            "color": "#b26a00", "bg": "#fdf7eb",
            "inside": ["16-бітний кулонометр", "Impedance Track", "Модель хімії АКБ", "Компенсація T° та Rint", "Порогові компаратори"],
            "contract": ["I²C: регістр SOC (%)", "INT при розряді < 15%", "Host спокійно спить"]
        }
    ]

    for c in cols:
        x, w = c["x"], c["w"]
        # Загальний контейнер
        p.append(rect(x, 50, w, 360, fill=c["bg"], stroke=c["color"], sw=1.3, rx=6))
        p.append(text(x + w / 2, 75, c["title"], size=11, color=c["color"], bold=True))
        p.append(text(x + w / 2, 93, c["chip"], size=10, color=MUTED))

        # Блок "Що робить кремній"
        p.append(rect(x + 8, 108, w - 16, 140, fill="#ffffff", stroke=c["color"], sw=0.8, rx=4))
        p.append(text(x + w / 2, 126, "Кремнієвий двигун:", size=9, color=c["color"], bold=True))
        for i, line in enumerate(c["inside"]):
            p.append(text(x + 14, 147 + i * 20, f"• {line}", size=9, color=INK, anchor="start"))

        # Блок "Контракт з Host MCU"
        p.append(rect(x + 8, 258, w - 16, 140, fill="#ffffff", stroke=MUTED, sw=0.8, rx=4))
        p.append(text(x + w / 2, 276, "Контракт з Host MCU:", size=9, color=INK, bold=True))
        
        # Текст контракту
        for j, cl in enumerate(c["contract"]):
            p.append(text(x + 14, 302 + j * 24, cl, size=9, color=c["color"] if j == 0 else INK, anchor="start"))

    # Підсумковий рядок знизу
    b_bot, _, _ = textbox(W / 2, 440,
                          "Супутній чип інкапсулює предметну складність: аналогову фізику, математичні моделі та мікросекундні цикли, надаючи Host лише високорівневі дані.",
                          size=10, stroke=MUTED, fill="#ffffff", min_w=920)
    p.append(b_bot)

    render(os.path.join(OUT, "companion-chips-spectrum.svg"), W, H, *p,
           title="Спектр супутніх мікросхем: кремнієві двигуни та цифровий контракт взаємодії")


# ── 3. decision-flowchart-integrate-vs-offload: Дерево рішень «Робити в ядрі чи ставити окремий чип» ───
def fig_decision_flowchart():
    W, H = 960, 480
    p = []

    # Крок 1: Жорсткий Real-Time
    p.append(rect(60, 50, 230, 75, fill="#edf4fc", stroke=NEG, sw=1.3, rx=6))
    p.append(text(175, 73, "1. Чи є жорсткий дедлайн?", size=11, color=NEG, bold=True))
    p.append(text(175, 90, "FOC ШІМ < 10 мкс, точний аудіо DSP,", size=9, color=INK))
    p.append(text(175, 107, "кулонометрія без пропусків", size=9, color=INK))

    p.append(arrow(290, 87, 380, 87, color=LINE, sw=1.5))
    p.append(text(335, 77, "НІ", size=10, color=MUTED, bold=True))

    # Відгалуження ТАК 1
    p.append(arrow(175, 125, 175, 185, color=POS, sw=1.5))
    p.append(text(190, 155, "ТАК", size=10, color=POS, bold=True))

    # Крок 2: Завантаження CPU
    p.append(rect(380, 50, 230, 75, fill="#edf4fc", stroke=NEG, sw=1.3, rx=6))
    p.append(text(495, 73, "2. Завантаження CPU > 30%?", size=11, color=NEG, bold=True))
    p.append(text(495, 90, "Криптографія, сканування тачу,", size=9, color=INK))
    p.append(text(495, 107, "важка цифрова фільтрація", size=9, color=INK))

    p.append(arrow(610, 87, 700, 87, color=LINE, sw=1.5))
    p.append(text(655, 77, "НІ", size=10, color=MUTED, bold=True))

    # Відгалуження ТАК 2
    p.append(arrow(495, 125, 495, 185, color=POS, sw=1.5))
    p.append(text(510, 155, "ТАК", size=10, color=POS, bold=True))

    # Крок 3: Вимоги до сну та безпеки
    p.append(rect(700, 50, 230, 75, fill="#edf4fc", stroke=NEG, sw=1.3, rx=6))
    p.append(text(815, 73, "3. Автономний сон / Безпека?", size=11, color=NEG, bold=True))
    p.append(text(815, 90, "Струм < 15 мкА у сні або апаратне", size=9, color=INK))
    p.append(text(815, 107, "зберігання ключів без витоку", size=9, color=INK))

    # Відгалуження ТАК 3
    p.append(arrow(815, 125, 815, 185, color=POS, sw=1.5))
    p.append(text(830, 155, "ТАК", size=10, color=POS, bold=True))

    # Відгалуження НІ 3 -> Робити програмно
    p.append(arrow(815, 50, 815, 38, color=FIELD, sw=1.5))
    p.append(line(815, 38, 935, 38, color=FIELD, sw=1.5))
    p.append(arrow(935, 38, 935, 340, color=FIELD, sw=1.5))
    p.append(arrow(935, 340, 730, 340, color=FIELD, sw=1.5))
    p.append(text(870, 30, "НІ на всі три", size=9, color=FIELD, bold=True))

    # Проміжний блок: Оцінка BOM та ланцюжка постачання
    p.append(rect(140, 185, 710, 80, fill="#fdfbf0", stroke="#b26a00", sw=1.3, rx=6))
    p.append(text(495, 208, "Економічна та виробнича перевірка (BOM Cost & Supply Chain Check)", size=11, color="#b26a00", bold=True))
    p.append(text(495, 228, "Чи виправдовує додавання чипу ($0.5–$2.5) зниження вимог до Host MCU та спрощення прошивки?", size=10, color=INK))
    p.append(text(495, 246, "Чи є альтернативні постачальники (Second Source), або ризик вендор-локу прийнятний?", size=10, color=MUTED))

    # Стрілки з проміжного блоку до фінальних рішень
    p.append(arrow(320, 265, 320, 310, color=POS, sw=2))
    p.append(text(335, 288, "ТАК (Вигідно)", size=10, color=POS, bold=True))

    p.append(arrow(670, 265, 670, 310, color=FIELD, sw=2))
    p.append(text(685, 288, "НІ (Задорого)", size=10, color=FIELD, bold=True))

    # Рішення А: Виносити на окремий чип
    p.append(rect(60, 310, 420, 115, fill="#fdf4f4", stroke=POS, sw=1.5, rx=6))
    p.append(text(270, 335, "РІШЕННЯ: Спеціалізований чип (Offload)", size=12, color=POS, bold=True))
    p.append(text(270, 357, "• Ставимо TMC2209 / ATECC608 / BQ27441 / FT6236", size=10, color=INK))
    p.append(text(270, 375, "• Host MCU залишається дешевим (Cortex-M0+/M3, мала пам'ять)", size=10, color=INK))
    p.append(text(270, 395, "• Гарантована надійність, нуль джиттеру, мінімальний струм сну", size=10, color=POS, bold=True))

    # Рішення Б: Робити все всередині MCU
    p.append(rect(510, 310, 420, 115, fill="#eefaf1", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(720, 335, "РІШЕННЯ: Інтеграція в MCU (Monolithic)", size=12, color=FIELD, bold=True))
    p.append(text(720, 357, "• Беремо потужніший MCU (Cortex-M4/M7, FPU, більше Flash/RAM)", size=10, color=INK))
    p.append(text(720, 375, "• Менше компонентів на платі, простіше трасування, менший BOM", size=10, color=INK))
    p.append(text(720, 395, "• Програмна реалізація алгоритмів з ретельним RTOS-профілюванням", size=10, color=FIELD, bold=True))

    # Підсумок знизу
    b_bot, _, _ = textbox(W / 2, 452,
                          "Супутній чип обирають не заради зручності, а коли фізика задачі (час, безпека, автономність) робить програмну реалізацію в одному ядрі ненадійною.",
                          size=10, stroke=MUTED, fill="#ffffff", min_w=920)
    p.append(b_bot)

    render(os.path.join(OUT, "decision-flowchart-integrate-vs-offload.svg"), W, H, *p,
           title="Інженерний алгоритм вибору між супутнім чипом та монолітним мікроконтролером")


if __name__ == "__main__":
    fig_monolithic_vs_companion()
    fig_companion_chips_spectrum()
    fig_decision_flowchart()
    print("All figures generated successfully.")
