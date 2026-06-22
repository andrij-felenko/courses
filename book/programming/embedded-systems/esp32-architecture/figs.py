# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори-акценти поверх палітри svgkit (радіо — теплий, кеш — жовтий)
RADIO = "#b9560f"
RADBG = "#fff1e6"
RADST = "#d2772a"
CACHE = "#8a6a14"
CACBG = "#fff6e0"
CACST = "#caa24a"


def antenna(p, x, y_top):
    """Антена: вертикальна риска вгору від (x, y_top) з двома дугами і підписом."""
    p.append(line(x, y_top, x, y_top - 42, color=RADIO, sw=2.4))
    p.append(circle(x, y_top - 42, 3.0, fill=RADIO, stroke=RADIO, sw=0))
    p.append('<path d="M %.0f,%.0f A 10,10 0 0 1 %.0f,%.0f" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (x + 6, y_top - 40, x + 6, y_top - 20, RADST))
    p.append('<path d="M %.0f,%.0f A 19,19 0 0 1 %.0f,%.0f" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (x + 6, y_top - 49, x + 6, y_top - 11, RADST))
    p.append(text(x, y_top - 50, "антена", size=10, color=RADIO, bold=True))


# ── soc: ESP32 як система-на-чипі ─────────────────────────────────────────────
def fig_soc():
    W, H = 900, 470
    p = []
    # рамка кристала
    p.append(rect(60, 70, 780, 360, fill="#fbfcff", stroke=INK, sw=2.4, rx=14))
    p.append(text(78, 90, "ESP32 (кристал)", size=11, color=MUTED, anchor="start", bold=True))

    # два ядра
    p.append(fitbox(90, 112, 150, 62, "Ядро 0\n240 МГц", size=13, fill="#fbecec", stroke=POS, sw=1.8, bold=True, color=POS))
    p.append(fitbox(256, 112, 150, 62, "Ядро 1\n240 МГц", size=13, fill="#fbecec", stroke=POS, sw=1.8, bold=True, color=POS))
    p.append(fitbox(422, 120, 96, 46, "ULP\nощадний", size=11, fill=BG, stroke=INK, sw=1.8, bold=True))

    # радіоблок
    p.append(rect(560, 104, 280, 92, fill=RADBG, stroke=RADST, sw=2, rx=8))
    p.append(text(700, 130, "Радіо", size=14, color=RADIO, bold=True))
    p.append(text(700, 150, "Wi-Fi 2.4 ГГц + Bluetooth/BLE", size=10, color=INK, bold=True))
    p.append(text(700, 168, "приймач-передавач", size=9, color=MUTED))
    antenna(p, 820, 104)

    # внутрішня шина
    busy = 230
    p.append(line(96, busy, 824, busy, color=FIELD, sw=5))
    p.append(text(820, busy - 9, "внутрішня шина", size=10, color=FIELD, anchor="end", bold=True))
    for cx in (165, 331, 470, 700):
        p.append(line(cx, 174 if cx < 560 else 196, cx, busy, color=FIELD, sw=2))

    # пам'ять
    p.append(fitbox(90, 266, 150, 64, "SRAM\n~520 КБ · дані", size=12, fill="#eef6ef", stroke=FIELD, sw=1.8, bold=True, color=FIELD))
    p.append(fitbox(256, 266, 120, 64, "ROM\nboot-код", size=12, fill=BG, stroke=INK, sw=1.8, bold=True))
    p.append(fitbox(392, 266, 160, 64, "RTC-пам'ять\nживе у сні", size=12, fill=BG, stroke=INK, sw=1.8, bold=True))
    for cx in (165, 316, 472):
        p.append(line(cx, busy, cx, 266, color=FIELD, sw=2))

    # периферія
    p.append(rect(560, 250, 280, 154, fill="#fafafa", stroke=INK, sw=1.8, rx=10))
    p.append(text(700, 272, "Багата периферія", size=12, color=INK, bold=True))
    for i, ln in enumerate(["GPIO ×34 (матриця)", "SPI · I2C · UART · I2S",
                            "ШІМ ×16 · ADC · DAC", "CAN · дотик · Холл",
                            "крипто (AES/SHA/RSA)"]):
        p.append(text(700, 294 + i * 21, ln, size=10.5, color=INK))
    p.append(line(700, busy, 700, 250, color=FIELD, sw=2))

    p.append(text(W / 2, 452, "зовні чипа — лише кварц, флеш-пам'ять і живлення; решта вся всередині",
                  size=12, color=INK, bold=True, italic=True))

    render(os.path.join(OUT, "soc.svg"), W, H, *p,
           title="ESP32 — система-на-чипі: знайома анатомія, подвоєна, плюс радіо")


# ── two-cores: два ядра + ULP ─────────────────────────────────────────────────
def fig_two_cores():
    W, H = 760, 300
    p = []
    busy = 210
    # два великі ядра
    p.append(fitbox(70, 90, 200, 80, "Ядро 0 (PRO)\n32-біт · до 240 МГц", size=12, fill="#fbecec", stroke=POS, sw=2, bold=True, color=POS))
    p.append(fitbox(300, 90, 200, 80, "Ядро 1 (APP)\n32-біт · до 240 МГц", size=12, fill="#fbecec", stroke=POS, sw=2, bold=True, color=POS))
    p.append(text(170, 184, "типово: радіо-стек", size=10, color=MUTED))
    p.append(text(400, 184, "типово: ваша програма", size=10, color=MUTED))

    # ULP окремо
    p.append(fitbox(560, 96, 150, 68, "ULP\nкрихітний,\nжевріє у сні", size=11, fill=BG, stroke=INK, sw=1.8, bold=True))

    # спільна шина + пам'ять/периферія
    p.append(line(120, busy, 640, busy, color=FIELD, sw=5))
    p.append(text(640, busy - 9, "спільні пам'ять і периферія", size=10, color=FIELD, anchor="end", bold=True))
    p.append(line(170, 170, 170, busy, color=FIELD, sw=2))
    p.append(line(400, 170, 400, busy, color=FIELD, sw=2))
    p.append(line(635, 164, 635, busy, color=INK, sw=1.6, dash="4 3"))

    p.append(text(W / 2, 262, "два рівноцінні ядра працюють паралельно — справжня одночасність у залізі",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "two-cores.svg"), W, H, *p,
           title="Обчислювальна частина: два ядра і крихітний ULP")


# ── flash-cache: своя SRAM + зовнішня флеш крізь кеш ──────────────────────────
def fig_flash_cache():
    W, H = 900, 420
    p = []
    p.append(rect(50, 80, 520, 300, fill="#fbfcff", stroke=INK, sw=2.2, rx=12))
    p.append(text(70, 102, "ESP32 (кристал)", size=11, color=MUTED, anchor="start", bold=True))

    p.append(fitbox(80, 130, 150, 70, "Ядро\nвиконує код", size=13, fill="#fbecec", stroke=POS, sw=1.8, bold=True, color=POS))
    p.append(fitbox(300, 130, 240, 70, "Кеш + MMU\nвідображає флеш у пам'ять", size=12, fill=CACBG, stroke=CACST, sw=1.8, bold=True, color=CACHE))
    p.append(arrow(300, 165, 234, 165, color=INK, sw=2.2))

    p.append(fitbox(80, 234, 150, 64, "SRAM ~520 КБ\nдані", size=12, fill="#eef6ef", stroke=FIELD, sw=1.8, bold=True, color=FIELD))
    p.append(fitbox(250, 234, 120, 64, "ROM\nboot", size=12, fill=BG, stroke=INK, sw=1.8, bold=True))
    p.append(fitbox(390, 234, 150, 64, "RTC-пам'ять\nживе у сні", size=12, fill=BG, stroke=INK, sw=1.8, bold=True))

    # зовнішня флеш
    p.append(rect(645, 160, 200, 120, fill="#2b2b2b", stroke="#000000", sw=1.6, rx=8))
    p.append(text(745, 200, "Зовнішня", size=12, color="#ffffff", bold=True))
    p.append(text(745, 222, "флеш 4 МБ", size=13, color="#ffffff", bold=True))
    p.append(text(745, 242, "(програма)", size=10, color="#cfcfcf"))
    p.append(text(745, 300, "окремий корпус на платі", size=10, color=MUTED, italic=True))
    p.append(arrow(645, 200, 544, 168, color=INK, sw=2.4))
    p.append(text(600, 172, "SPI", size=10, color=MUTED, bold=True))

    p.append(text(W / 2, 405, "для коду це непомітно: зовнішня флеш «бачиться» як звичайна пам'ять",
                  size=11.5, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "flash-cache.svg"), W, H, *p,
           title="Пам'ять: своя SRAM на чипі, зовнішня флеш крізь кеш")


# ── radio: радіоблок на чипі ──────────────────────────────────────────────────
def fig_radio():
    W, H = 760, 320
    p = []
    p.append(rect(60, 80, 640, 200, fill="#fbfcff", stroke=INK, sw=2.2, rx=12))
    p.append(text(78, 102, "ESP32 (кристал)", size=11, color=MUTED, anchor="start", bold=True))

    # ядро керує
    p.append(fitbox(90, 150, 150, 70, "Ядра\n(керують через\nрегістри)", size=11, fill="#fbecec", stroke=POS, sw=1.8, bold=True, color=POS))

    # приймач-передавач
    p.append(rect(300, 130, 220, 110, fill=RADBG, stroke=RADST, sw=2, rx=10))
    p.append(text(410, 158, "Приймач-передавач", size=12, color=RADIO, bold=True))
    p.append(text(410, 178, "2.4 ГГц (спільний тракт)", size=10, color=INK))
    p.append(fitbox(312, 192, 96, 36, "Wi-Fi", size=11, fill=BG, stroke=RADST, sw=1.5, bold=True, color=RADIO))
    p.append(fitbox(414, 192, 96, 36, "BT / BLE", size=11, fill=BG, stroke=RADST, sw=1.5, bold=True, color=RADIO))
    p.append(arrow(240, 185, 298, 185, color=INK, sw=1.8))

    antenna(p, 620, 130)
    p.append(line(520, 185, 600, 150, color=RADST, sw=2))

    # призначення праворуч від антени
    p.append(text(640, 175, "до роутера", size=10, color=MUTED, anchor="start"))
    p.append(text(640, 192, "й інтернету", size=10, color=MUTED, anchor="start"))
    p.append(text(640, 214, "до смартфона", size=10, color=MUTED, anchor="start"))

    p.append(text(W / 2, 300, "радіо вмонтоване в кремній; антена — єдина зовнішня деталь",
                  size=11.5, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "radio.svg"), W, H, *p,
           title="Радіоблок: Wi-Fi і Bluetooth зі спільним трактом 2.4 ГГц")


# ── peripherals-matrix: периферія + матриця ніжок ─────────────────────────────
def fig_peripherals_matrix():
    W, H = 860, 380
    p = []
    # ліворуч — список периферії
    p.append(rect(50, 80, 300, 250, fill="#fafafa", stroke=INK, sw=1.8, rx=10))
    p.append(text(200, 104, "Периферія", size=13, color=INK, bold=True))
    items = ["кілька SPI · I2C · UART · I2S", "ШІМ ×16", "ADC ×2 (12-біт) · DAC ×2",
             "дотик · давач Холла · температура", "CAN · карти пам'яті",
             "крипто: AES · SHA · RSA + RNG"]
    for i, ln in enumerate(items):
        p.append(text(70, 132 + i * 30, "• " + ln, size=11, color=INK, anchor="start"))

    # праворуч — матриця-комутатор і ніжки
    p.append(rect(470, 110, 150, 190, fill="#e9eefb", stroke=NEG, sw=2, rx=10))
    p.append(text(545, 150, "Матриця", size=13, color=NEG, bold=True))
    p.append(text(545, 170, "ніжок", size=13, color=NEG, bold=True))
    p.append(text(545, 196, "(комутатор)", size=10, color=MUTED))
    p.append(text(545, 220, "майже будь-який", size=9.5, color=INK))
    p.append(text(545, 235, "сигнал →", size=9.5, color=INK))
    p.append(text(545, 250, "майже будь-яка ніжка", size=9.5, color=INK))

    # стрілка від периферії до матриці
    p.append(arrow(350, 200, 468, 200, color=INK, sw=2))

    # гребінка ніжок праворуч
    px = 700
    for i in range(10):
        py = 120 + i * 17
        p.append(circle(px, py, 4.5, fill="#d8c98a", stroke=CACST, sw=1))
        p.append(line(620, 205, px - 6, py, color=MUTED, sw=0.8))
    p.append(text(px + 18, 205, "~34 GPIO", size=11, color=INK, anchor="start", bold=True))

    p.append(text(W / 2, 360, "мультиплексування виводів, доведене до краю: інтерфейси кладуться на ніжки майже вільно",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "peripherals-matrix.svg"), W, H, *p,
           title="Багата периферія і гнучка матриця ніжок")


# ── deep-sleep-ulp: глибокий сон ──────────────────────────────────────────────
def fig_deep_sleep_ulp():
    W, H = 820, 360
    p = []
    # знеструмлена частина (приглушена)
    p.append(rect(60, 90, 360, 220, fill="#f3f3f3", stroke="#bdbdbd", sw=1.6, rx=12))
    p.append(text(240, 112, "Знеструмлено у глибокому сні", size=12, color=MUTED, bold=True))
    p.append(fitbox(90, 140, 130, 60, "Ядро 0", size=12, fill="#ededed", stroke="#bdbdbd", sw=1.5, bold=True, color=MUTED))
    p.append(fitbox(252, 140, 130, 60, "Ядро 1", size=12, fill="#ededed", stroke="#bdbdbd", sw=1.5, bold=True, color=MUTED))
    p.append(fitbox(90, 222, 292, 56, "Радіо (Wi-Fi + BT)", size=12, fill="#ededed", stroke="#bdbdbd", sw=1.5, bold=True, color=MUTED))
    p.append(text(240, 300, "≈ нуль споживання", size=11, color=MUTED, italic=True))

    # живий RTC-домен
    p.append(rect(470, 90, 290, 220, fill="#eef6ef", stroke=FIELD, sw=2.2, rx=12))
    p.append(text(615, 112, "Живий RTC-домен", size=12, color=FIELD, bold=True))
    p.append(fitbox(495, 140, 240, 50, "ULP-співпроцесор", size=12, fill=BG, stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    p.append(fitbox(495, 200, 240, 44, "RTC-периферія", size=12, fill=BG, stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    p.append(fitbox(495, 252, 240, 44, "RTC-пам'ять", size=12, fill=BG, stroke=FIELD, sw=1.6, bold=True, color=FIELD))

    # ULP будить ядра за потреби
    p.append(arrow(495, 165, 422, 165, color=POS, sw=2))
    p.append(text(458, 156, "будить лише за потреби", size=9.5, color=POS, anchor="middle"))

    p.append(text(W / 2, 342, "ULP сам опитує давач і будить великі ядра лише за потреби — звідси місяці від батарейки",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "deep-sleep-ulp.svg"), W, H, *p,
           title="Глибокий сон: великі ядра й радіо сплять, ULP і RTC живі")


# ── spec: специфікація, розкладена на анатомію ────────────────────────────────
def fig_spec():
    W, H = 900, 400
    p = []
    rows = [
        ("ЯДРО",      POS,   "#fbecec", ["2 × 32-біт (Xtensa LX6)", "до 240 МГц"]),
        ("ПАМ'ЯТЬ",   FIELD, "#eef6ef", ["520 КБ SRAM (своя)", "4 МБ флеш (зовні, крізь кеш)"]),
        ("РАДІО",     RADST, "#f7f4ea", ["Wi-Fi 2.4 ГГц", "Bluetooth / BLE"]),
        ("ПЕРИФЕРІЯ", NEG,   "#e9eefb", ["~34 GPIO (матриця)", "ADC/DAC · SPI/I2C/UART · ШІМ"]),
        ("ЖИВЛЕННЯ",  CACHE, "#f7f4ea", ["кварц 40 МГц + PLL → 240", "глибокий сон + ULP"]),
    ]
    y = 80
    for label, col, fill, cells in rows:
        p.append(text(48, y + 24, label, size=12.5, color=col, anchor="start", bold=True))
        x = 230
        for c in cells:
            w = max(150, text_width(c, 11.5, True) + 24)
            p.append(fitbox(x, y, w, 36, c, size=11.5, fill=fill, stroke=col, sw=2, bold=True, color=col))
            x += w + 16
        y += 58
    p.append(rect(120, y + 4, 660, 30, fill=CACBG, stroke=CACST, sw=1.2, rx=8))
    p.append(text(W / 2, y + 24, "жодної незнайомої графи — лише загальна анатомія МК, застосована до конкретного чипа",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "spec.svg"), W, H, *p,
           title="Специфікація ESP32, розкладена на знайому анатомію")


# ══════════════════════ ВСТАВКА comp-devkit ══════════════════════════════════

def fig_devkit_block():
    W, H = 900, 470
    p = []
    p.append(rect(36, 70, 828, 380, fill="#fcfdff", stroke=INK, sw=2, rx=14))
    p.append(text(54, 92, "Плата DevKit", size=11, color=MUTED, anchor="start", bold=True))

    # USB
    p.append(fitbox(54, 220, 70, 64, "USB", size=12, fill="#eceff4", stroke=INK, sw=1.8, bold=True))
    p.append(text(89, 300, "5 В + дані", size=9, color=MUTED))

    # міст і LDO
    p.append(fitbox(170, 130, 196, 64, "USB-UART міст\nCP210x / CH340-клас", size=12, fill="#e9eefb", stroke=NEG, sw=1.8, bold=True, color=NEG))
    p.append(fitbox(170, 300, 196, 64, "LDO 3.3 В\nAMS1117-клас", size=12, fill="#fbecec", stroke=POS, sw=1.8, bold=True, color=POS))

    # модуль
    p.append(rect(450, 130, 210, 200, fill="#eef3fb", stroke=INK, sw=2.4, rx=10))
    p.append(text(555, 156, "Модуль ESP32", size=13, color=INK, bold=True))
    p.append(text(555, 174, "WROOM-клас", size=10, color=MUTED))
    p.append(text(555, 192, "чип + кварц + Flash + антена", size=9, color=MUTED))
    p.append(line(470, 206, 640, 206, color="#e4e4e4", sw=1.2))
    p.append(text(555, 230, "TX / RX", size=10.5, color=NEG, bold=True))
    p.append(text(555, 256, "VDD 3.3 В", size=10.5, color=POS, bold=True))
    p.append(text(555, 282, "EN · IO0", size=10.5, color=FIELD, bold=True))

    # авто-скидання + кнопки
    p.append(fitbox(150, 378, 220, 52, "схема авто-скидання\nDTR/RTS → 2 транзистори", size=10, fill="#eef6ef", stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    p.append(circle(490, 396, 15, fill="#e8e8e8", stroke=INK, sw=1.8))
    p.append(text(490, 400, "EN", size=9, color=INK, bold=True))
    p.append(circle(560, 396, 16, fill="#e8e8e8", stroke=INK, sw=1.8))
    p.append(text(560, 400, "BOOT", size=9, color=INK, bold=True))

    # гребінки
    for gx in (700, 744):
        p.append(rect(gx, 130, 26, 200, fill="#fbf7e3", stroke=CACST, sw=1.4, rx=4))
        for i in range(8):
            p.append(circle(gx + 13, 150 + i * 22, 4, fill="#d8c98a", stroke=CACST, sw=1))
    p.append(text(735, 350, "гребінки GPIO", size=9.5, color=INK, bold=True))

    # з'єднання
    p.append(arrow(124, 240, 168, 178, color=NEG, sw=2))
    p.append(text(140, 200, "D+/D−", size=9, color=NEG, anchor="start"))
    p.append(arrow(124, 270, 168, 330, color=POS, sw=2))
    p.append(text(140, 310, "5 В", size=9, color=POS, anchor="start"))
    p.append(arrow(366, 162, 448, 206, color=NEG, sw=2))
    p.append(text(410, 176, "TX/RX", size=9, color=NEG))
    p.append(arrow(366, 332, 448, 280, color=POS, sw=2))
    p.append(text(410, 326, "3.3 В", size=9, color=POS))
    p.append(line(370, 392, 470, 290, color=FIELD, sw=1.8, dash="4 3"))
    p.append(arrow(660, 230, 700, 230, color=INK, sw=1.6))
    p.append(text(681, 222, "GPIO", size=9, color=INK))

    render(os.path.join(OUT, "devkit-block.svg"), W, H, *p,
           title="Анатомія DevKit: що додано навколо модуля ESP32")


def fig_flash_flow():
    W, H = 900, 230
    p = []
    y = 110
    bw, bh, step = 140, 60, 152
    x = 36
    steps = [
        ("USB\nутикаєш", "#eceff4", INK),
        ("міст → COM\n(драйвер)", "#e9eefb", NEG),
        ("DTR/RTS:\nу завантажувач", "#eef6ef", FIELD),
        ("esptool пише\nFlash блоками", CACBG, CACHE),
        ("EN відпущено:\nстартує код", "#fbecec", POS),
    ]
    ends = []
    for i, (lab, fill, col) in enumerate(steps):
        p.append(fitbox(x, y - bh / 2, bw, bh, lab, size=10.5, fill=fill, stroke=col, sw=1.6, bold=True, color=col))
        if i > 0:
            p.append(arrow(ends[-1] + 2, y, x - 2, y, color=INK, sw=1.8))
        ends.append(x + bw)
        x += step

    p.append(text(W / 2, y + 70, "ключ — авто-скидання: під час reset чіп дивиться на IO0 (0 = завантажувач, 1 = програма)",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "flash-flow.svg"), W, H, *p,
           title="Потік прошивки на рівні плати: від USB до старту програми")


# ══════════════════════ ВСТАВКА hist-esp ═════════════════════════════════════

def fig_timeline():
    W, H = 900, 640
    p = []
    ax = 250
    p.append(line(ax, 80, ax, 600, color=MUTED, sw=3))
    nodes = [
        ("до 2014", "Дорогий Wi-Fi", "Плата зв'язку $30–40 — дорожча за весь проєкт. Як вивести саморобку в мережу?", MUTED, INK),
        ("2014", "ESP8266 (Espressif · AI-Thinker)", "Дешевий «перехідник на Wi-Fi» за кілька $. Невже лише причіп до Arduino?", MUTED, INK),
        ("2014–15", "Відкриття спільноти", "А всередині — справжній 32-біт комп'ютер! Та документація китайською.", MUTED, INK),
        ("2015", "NodeMCU + ядро Arduino", "Чіп за $3 програмують як Arduino — стіни впали, вибух проєктів.", MUTED, INK),
        ("2016", "ESP32 (Espressif)", "Два ядра, +Bluetooth, готова екосистема з першого дня.", POS, POS),
        ("сьогодні", "Стандарт IoT", "Чому саме ESP підкорив аматорів?", FIELD, FIELD),
    ]
    y = 120
    dy = (590 - 120) / (len(nodes) - 1)
    for i, (when, head, body, mc, hc) in enumerate(nodes):
        cy = y + i * dy
        if i == len(nodes) - 1:
            p.append(rect(ax - 8, cy - 8, 16, 16, fill=BG, stroke=FIELD, sw=2.6, rx=3))
        elif i == len(nodes) - 2:
            p.append(circle(ax, cy, 10, fill=BG, stroke=POS, sw=3))
            p.append(circle(ax, cy, 4.5, fill=POS, stroke=POS, sw=0))
        else:
            p.append(circle(ax, cy, 7, fill=BG, stroke=INK, sw=2.6))
        p.append(text(ax - 22, cy + 5, when, size=12, color=MUTED, anchor="end", bold=True))
        p.append(text(ax + 26, cy - 3, head, size=14.5, color=hc, anchor="start", bold=True))
        p.append(text(ax + 26, cy + 17, body, size=12, color=INK, anchor="start", italic=True))
    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Як ESP підкорив аматорів: ланцюг подій")


def fig_price_shock():
    W, H = 820, 360
    p = []
    # ліворуч — дорога плата
    p.append(rect(70, 110, 300, 170, fill="#fbecec", stroke=POS, sw=2, rx=12))
    p.append(text(220, 140, "Wi-Fi-плата розширення", size=13, color=POS, bold=True))
    p.append(text(220, 162, "до 2014 року", size=10.5, color=MUTED))
    p.append(text(220, 205, "$30–40", size=34, color=POS, bold=True))
    p.append(text(220, 246, "дорожча за решту проєкту", size=11, color=INK))

    # праворуч — дешевий модуль
    p.append(rect(450, 110, 300, 170, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    p.append(text(600, 140, "Модуль ESP8266", size=13, color=FIELD, bold=True))
    p.append(text(600, 162, "2014 року", size=10.5, color=MUTED))
    p.append(text(600, 205, "кілька $", size=34, color=FIELD, bold=True))
    p.append(text(600, 246, "Wi-Fi усередині чипа", size=11, color=INK))

    p.append(arrow(372, 195, 448, 195, color=INK, sw=2.6))
    p.append(text(410, 182, "×10", size=13, color=INK, bold=True))

    p.append(text(W / 2, 320, "десятикратне падіння — не «трохи дешевше», а зміна того, що взагалі можна собі дозволити",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "price-shock.svg"), W, H, *p,
           title="Що сталося з ціною входу в мережу")


def fig_accidental_computer():
    W, H = 820, 350
    p = []
    # очікували
    p.append(rect(60, 100, 320, 180, fill="#f3f3f3", stroke="#bdbdbd", sw=1.8, rx=12))
    p.append(text(220, 128, "Очікували", size=13, color=MUTED, bold=True))
    p.append(text(220, 158, "німий «перехідник»", size=12, color=INK))
    p.append(text(220, 182, "лише з'єднати чужу плату", size=11, color=MUTED))
    p.append(text(220, 200, "з Wi-Fi за AT-командами", size=11, color=MUTED))
    p.append(fitbox(110, 222, 220, 44, "ESP-01: 8 ніжок,\nантена-доріжка", size=11, fill=BG, stroke="#bdbdbd", sw=1.5, color=MUTED))

    # а всередині
    p.append(rect(440, 100, 320, 180, fill="#eef6ef", stroke=FIELD, sw=2.2, rx=12))
    p.append(text(600, 128, "А всередині виявилось", size=13, color=FIELD, bold=True))
    p.append(text(600, 158, "32-бітне ядро (~80 МГц)", size=12, color=INK, bold=True))
    p.append(text(600, 180, "з пам'яттю + той самий Wi-Fi", size=11, color=INK))
    p.append(fitbox(480, 204, 240, 60, "самодостатній комп'ютер —\nжодна головна плата\nне потрібна", size=11, fill=BG, stroke=FIELD, sw=1.6, bold=True, color=FIELD))

    p.append(arrow(382, 190, 438, 190, color=INK, sw=2.4))
    p.append(text(W / 2, 320, "маскування дрібнички під «причіп» і стало головним сюрпризом",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "accidental-computer.svg"), W, H, *p,
           title="ESP-01: «перехідник на Wi-Fi», а всередині — комп'ютер")


def fig_community_unlock():
    W, H = 940, 300
    p = []
    y = 120
    bw, bh, step = 150, 76, 188
    x = 40
    chain = [
        ("Дешевий чіп\nз потенціалом,\nдок. китайською", "#f3f3f3", MUTED),
        ("Спільнота розбирає,\nперекладає,\nдокументує", "#e9eefb", NEG),
        ("NodeMCU (Lua) +\nядро Arduino", "#eef6ef", FIELD),
        ("Комп'ютер з Wi-Fi\nза $3, як Arduino", "#fbecec", POS),
        ("Вибух аматорських\nпроєктів", CACBG, CACHE),
    ]
    ends = []
    for i, (lab, fill, col) in enumerate(chain):
        p.append(fitbox(x, y - bh / 2, bw, bh, lab, size=10.5, fill=fill, stroke=col, sw=1.7, bold=True, color=col))
        if i > 0:
            p.append(arrow(ends[-1] + 2, y, x - 2, y, color=INK, sw=1.8))
        ends.append(x + bw)
        x += step
    p.append(text(W / 2, y + 90, "екосистему збудували самі користувачі — і ця інерція добра живе досі",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "community-unlock.svg"), W, H, *p,
           title="Як спільнота відчинила ESP8266 світові")


def fig_esp8266_vs_esp32():
    W, H = 820, 360
    p = []
    # ESP8266
    p.append(rect(60, 100, 320, 200, fill="#f7f4ea", stroke=CACST, sw=2, rx=12))
    p.append(text(220, 128, "ESP8266 (2014)", size=14, color=CACHE, bold=True))
    for i, ln in enumerate(["одне ядро", "лише Wi-Fi", "мало ніжок", "документація «зроби сам»"]):
        p.append(text(82, 158 + i * 28, "• " + ln, size=11.5, color=INK, anchor="start"))

    # ESP32
    p.append(rect(440, 100, 320, 200, fill="#eef6ef", stroke=FIELD, sw=2.2, rx=12))
    p.append(text(600, 128, "ESP32 (2016)", size=14, color=FIELD, bold=True))
    for i, ln in enumerate(["два ядра", "Wi-Fi + Bluetooth/BLE", "багато периферії й ніжок",
                            "офіційна екосистема з 1-го дня"]):
        p.append(text(462, 158 + i * 28, "• " + ln, size=11.5, color=INK, anchor="start", bold=(i == 3)))

    p.append(arrow(382, 200, 438, 200, color=INK, sw=2.6))
    p.append(text(410, 188, "уроки", size=10, color=INK, bold=True))
    p.append(text(W / 2, 330, "залізо стало кращим, але переможним його зробив готовий світ навколо",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "esp8266-vs-esp32.svg"), W, H, *p,
           title="Від ESP8266 до ESP32: що додалося і чому це стало стандартом")


if __name__ == "__main__":
    # стаття
    fig_soc(); fig_two_cores(); fig_flash_cache(); fig_radio()
    fig_peripherals_matrix(); fig_deep_sleep_ulp(); fig_spec()
    # comp-devkit
    fig_devkit_block(); fig_flash_flow()
    # hist-esp
    fig_timeline(); fig_price_shock(); fig_accidental_computer()
    fig_community_unlock(); fig_esp8266_vs_esp32()
    print("OK: figures written to", OUT)
