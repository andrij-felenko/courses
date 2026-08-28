# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Фізичний інтерфейс SWD ──────────────────────────────────────────────────
def fig_swd_physical_layer():
    W, H = 960, 540
    p = []

    # Лівий блок: Відлагоджувач
    p.append(rect(30, 50, 270, 450, fill="#f8fafc", stroke=NEG, sw=2, rx=8))
    p.append(text(165, 78, "Апаратний відлагоджувач", size=14, color=NEG, bold=True))
    p.append(text(165, 96, "(J-Link / ST-Link / DAPLink)", size=11, color=MUTED))

    p.append(rect(45, 115, 240, 65, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(165, 138, "Схема вимірювання Vref", size=11.5, color=INK, bold=True))
    p.append(text(165, 158, "АЦП / компаратор напруги", size=10, color=MUTED))

    p.append(rect(45, 190, 240, 175, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(165, 214, "Буфери логічних рівнів", size=11.5, color=INK, bold=True))
    p.append(text(165, 233, "Level Shifter (1.65 В – 5.0 В)", size=10, color=MUTED))
    p.append(text(165, 260, "SWCLK драйвер (вихід)", size=10, color=INK))
    p.append(text(165, 285, "SWDIO трансивер (напівдуплекс)", size=10, color=INK))
    p.append(text(165, 310, "nRESET відкритий колектор", size=10, color=INK))
    p.append(text(165, 335, "Підтяжка SWDIO: 100 кОм до Vref", size=9.5, color=FIELD))

    p.append(rect(45, 375, 240, 95, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(165, 400, "USB-контролер / Фірмвар", size=11.5, color=INK, bold=True))
    p.append(text(165, 422, "CMSIS-DAP / Segger протокол", size=10, color=MUTED))
    p.append(text(165, 444, "Зв'язок з ПК через USB CDC/HID", size=10, color=MUTED))

    # Правий блок: Мікроконтролер на власній платі
    p.append(rect(660, 50, 270, 450, fill="#f8fafc", stroke=POS, sw=2, rx=8))
    p.append(text(795, 78, "Мікроконтролер (Target MCU)", size=14, color=POS, bold=True))
    p.append(text(795, 96, "Власна плата розробника", size=11, color=MUTED))

    p.append(rect(675, 115, 240, 75, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(795, 138, "Шина живлення VDD (3.3 В)", size=11.5, color=INK, bold=True))
    p.append(text(795, 158, "Живить периферію та I/O", size=10, color=MUTED))
    p.append(text(795, 177, "Блокувальні керамічні 100 нФ", size=9.5, color=FIELD))

    p.append(rect(675, 200, 240, 160, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(795, 222, "ARM CoreSight Debug Port", size=11.5, color=INK, bold=True))
    p.append(text(795, 242, "SW-DP / AHB-AP інтерфейс", size=10, color=MUTED))
    p.append(text(795, 268, "Внутрішній pull-down SWCLK", size=9.5, color=MUTED))
    p.append(text(795, 290, "Внутрішній pull-up SWDIO", size=9.5, color=MUTED))
    p.append(text(795, 312, "NRST фільтр (100 нФ на GND)", size=9.5, color=FIELD))
    p.append(text(795, 334, "BOOT0 притягнутий до GND", size=9.5, color=FIELD))

    p.append(rect(675, 370, 240, 100, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(795, 395, "Цифрове ядро (1.2 В) + LDO", size=11.5, color=INK, bold=True))
    p.append(text(795, 417, "Піни VCAP1 / VCAP2", size=10.5, color=POS, bold=True))
    p.append(text(795, 439, "Конденсатори 2.2 мкФ Low-ESR", size=10, color=POS))

    # Лінії зв'язку
    lines_info = [
        (145, "VTref / Vtarget (опора)", POS, "→", "Опорна напруга плати для буферів"),
        (225, "SWCLK (тактування 1–10 МГц)", INK, "→", "Послідовний резистор Rs 22–47 Ом"),
        (290, "SWDIO (двонаправлені дані)", NEG, "↔", "Послідовний резистор Rs 22–47 Ом"),
        (355, "nRESET (апаратне скидання)", FIELD, "→", "Open-drain лінія скидання ядра"),
        (430, "GND (спільна земля)", LINE, "—", "Обов'язковий зворотний шлях струму"),
    ]

    for y, name, col, dir_sym, note in lines_info:
        p.append(line(300, y, 660, y, color=col, sw=2))
        p.append(circle(300, y, 4, fill=col, stroke=col))
        p.append(circle(660, y, 4, fill=col, stroke=col))
        p.append(rect(330, y - 20, 300, 40, fill="#ffffff", stroke=col, sw=1.2, rx=4))
        p.append(text(480, y - 4, name + " " + dir_sym, size=11, color=col, bold=True))
        p.append(text(480, y + 12, note, size=9.5, color=MUTED))

    render(os.path.join(OUT, "swd-physical-layer.svg"), W, H, *p,
           title="Фізичний інтерфейс SWD: з'єднання відлагоджувача з мікроконтролером")


# ── 2. Цілісність сигналу і дзвін ──────────────────────────────────────────────
def fig_signal_integrity_ringing():
    W, H = 940, 480
    p = []

    # Верхній графік: Довгий шлейф без демпфування
    p.append(rect(40, 50, 860, 195, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(60, 75, "A. Довгий шлейф (30 см Dupont) без демпфуючого резистора", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(60, 95, "Крутий фронт драйвера (tr = 1 нс) викликає сильний LC-резонанс та відбиття від входу", size=10.5, color=MUTED, anchor="start"))

    # Осі A
    p.append(line(80, 205, 820, 205, color="#94a3b8", sw=1.2)) # GND
    p.append(line(80, 125, 820, 125, color="#94a3b8", sw=1, dash="4,4")) # 3.3V
    p.append(text(72, 209, "0 В", size=10, color=MUTED, anchor="end"))
    p.append(text(72, 129, "3.3 В", size=10, color=MUTED, anchor="end"))

    # Поріг VIH / VIL
    p.append(line(80, 145, 820, 145, color="#fca5a5", sw=0.8, dash="2,2"))
    p.append(text(825, 149, "Поріг VIH (2.0 В)", size=9.5, color=POS, anchor="start"))
    p.append(line(80, 180, 820, 180, color="#fca5a5", sw=0.8, dash="2,2"))
    p.append(text(825, 184, "Поріг VIL (0.8 В)", size=9.5, color=POS, anchor="start"))

    # Крива з дзвоном
    ring_pts = [
        (80, 205), (140, 205), (148, 110), (160, 100), (175, 190), (190, 115),
        (205, 145), (220, 120), (235, 130), (250, 125), (380, 125),
        (388, 220), (400, 230), (415, 150), (430, 215), (445, 195), (460, 208), (475, 205), (580, 205),
        (588, 110), (600, 100), (615, 190), (630, 115), (645, 145), (660, 125), (780, 125)
    ]
    pts_str = " ".join(f"{x},{y}" for x, y in ring_pts)
    p.append(f'<polyline points="{pts_str}" fill="none" stroke="{POS}" stroke-width="2.2"/>')

    # Підписи дефектів
    p.append(circle(160, 100, 5, fill="#fee2e2", stroke=POS, sw=1.5))
    p.append(text(160, 88, "Overshoot (+1.2 В)", size=9.5, color=POS, bold=True))

    p.append(circle(175, 190, 5, fill="#fee2e2", stroke=POS, sw=1.5))
    p.append(rect(195, 168, 230, 34, fill="#ffffff", stroke=POS, sw=1, rx=3))
    p.append(text(310, 183, "Провал нижче VIH → хибний спад", size=9.5, color=POS, bold=True))
    p.append(text(310, 196, "Подвійне тактування SWCLK!", size=9, color=POS))

    # Нижній графік: Короткий шлейф + демпфуючий резистор
    p.append(rect(40, 260, 860, 195, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(60, 285, "B. Узгоджена лінія (шлейф <15 см + послідовний резистор Rs = 33 Ом)", size=13, color=FIELD, bold=True, anchor="start"))
    p.append(text(60, 305, "Резистор поглинає відбиту хвилю; фронт наростання стає монотонним і плавним", size=10.5, color=MUTED, anchor="start"))

    # Осі B
    p.append(line(80, 415, 820, 415, color="#94a3b8", sw=1.2)) # GND
    p.append(line(80, 335, 820, 335, color="#94a3b8", sw=1, dash="4,4")) # 3.3V
    p.append(text(72, 419, "0 В", size=10, color=MUTED, anchor="end"))
    p.append(text(72, 339, "3.3 В", size=10, color=MUTED, anchor="end"))

    # Поріг VIH / VIL
    p.append(line(80, 355, 820, 355, color="#86efac", sw=0.8, dash="2,2"))
    p.append(text(825, 359, "Поріг VIH (2.0 В)", size=9.5, color=FIELD, anchor="start"))
    p.append(line(80, 390, 820, 390, color="#86efac", sw=0.8, dash="2,2"))
    p.append(text(825, 394, "Поріг VIL (0.8 В)", size=9.5, color=FIELD, anchor="start"))

    # Плавна крива
    clean_pts = [
        (80, 415), (140, 415), (160, 335), (380, 335),
        (400, 415), (580, 415), (600, 335), (780, 335)
    ]
    pts_clean_str = " ".join(f"{x},{y}" for x, y in clean_pts)
    p.append(f'<polyline points="{pts_clean_str}" fill="none" stroke="{FIELD}" stroke-width="2.4"/>')

    p.append(rect(230, 360, 250, 34, fill="#ffffff", stroke=FIELD, sw=1, rx=3))
    p.append(text(355, 375, "Монотонний фронт (tr ≈ 6 нс)", size=10, color=FIELD, bold=True))
    p.append(text(355, 388, "Надійне стробування даних без збоїв", size=9.5, color=MUTED))

    render(os.path.join(OUT, "signal-integrity-ringing.svg"), W, H, *p,
           title="Цілісність сигналу SWD: дзвін на довгому шлейфі проти резисторного демпфування")


# ── 3. Connect under Reset ─────────────────────────────────────────────────────
def fig_connect_under_reset():
    W, H = 940, 500
    p = []

    # Верхній сценарій: Звичайне підключення (Normal Connect)
    p.append(rect(40, 50, 860, 205, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=6))
    p.append(text(60, 75, "Сценарій 1. Звичайне підключення (Normal Connect) — відмова при збійній прошивці", size=13, color="#ea580c", bold=True, anchor="start"))

    # Шкала часу
    p.append(line(80, 160, 840, 160, color="#cbd5e1", sw=2))
    p.append(text(840, 178, "Час t →", size=10, color=MUTED, anchor="end"))

    # Фази
    p.append(rect(80, 105, 140, 45, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(150, 123, "Зняття nRESET", size=10.5, color=INK, bold=True))
    p.append(text(150, 140, "Ядро стартує", size=9.5, color=MUTED))

    p.append(rect(240, 105, 200, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text(340, 123, "Користувацький код (0..5 мкс)", size=10.5, color=POS, bold=True))
    p.append(text(340, 140, "Ремап SWD в GPIO або Deep Sleep", size=9.5, color=POS))

    p.append(rect(460, 105, 230, 45, fill="#ffffff", stroke="#ea580c", sw=1.2, rx=4))
    p.append(text(575, 123, "Відлагоджувач шле DP-IDCODE", size=10.5, color=INK, bold=True))
    p.append(text(575, 140, "Спроба зупинити ядро через DHCSR", size=9.5, color=MUTED))

    p.append(rect(710, 105, 140, 45, fill="#fee2e2", stroke=POS, sw=2, rx=4))
    p.append(text(780, 123, "ПОМИЛКА ЗВ'ЯЗКУ", size=10.5, color=POS, bold=True))
    p.append(text(780, 140, "Target not found", size=9.5, color=POS))

    p.append(text(150, 185, "t = 0", size=9.5, color=MUTED))
    p.append(text(340, 185, "t = 5 мкс (SWD вимкнено!)", size=9.5, color=POS, bold=True))
    p.append(text(575, 185, "t = 2 мс (запізно)", size=9.5, color=MUTED))

    # Нижній сценарій: Connect under Reset
    p.append(rect(40, 275, 860, 205, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(60, 300, "Сценарій 2. Підключення під скиданням (Connect under Reset) — надійне перехоплення", size=13, color=FIELD, bold=True, anchor="start"))

    p.append(line(80, 390, 840, 390, color="#cbd5e1", sw=2))
    p.append(text(840, 408, "Час t →", size=10, color=MUTED, anchor="end"))

    p.append(rect(80, 335, 190, 45, fill="#e0f2fe", stroke=NEG, sw=1.5, rx=4))
    p.append(text(175, 353, "Відлагоджувач тримає nRESET=0", size=10, color=NEG, bold=True))
    p.append(text(175, 370, "Ядро заморожене, CoreSight активний", size=9.5, color=MUTED))

    p.append(rect(290, 335, 230, 45, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(405, 353, "Налаштування Vector Catch", size=10.5, color=FIELD, bold=True))
    p.append(text(405, 370, "DEMCR.VC_CORERESET = 1, C_DEBUGEN", size=9.5, color=INK))

    p.append(rect(540, 335, 160, 45, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(620, 353, "Зняття nRESET (High)", size=10.5, color=INK, bold=True))
    p.append(text(620, 370, "Ядро починає вибірку вектора", size=9.5, color=MUTED))

    p.append(rect(720, 335, 140, 45, fill="#dcfce7", stroke=FIELD, sw=2, rx=4))
    p.append(text(790, 353, "ЗУПИНКА НА ВЕКТОРІ", size=10, color=FIELD, bold=True))
    p.append(text(790, 370, "PC = Reset_Handler", size=9.5, color=FIELD))

    p.append(text(175, 418, "Ядро спить у Reset", size=9.5, color=MUTED))
    p.append(text(405, 418, "Пастка налаштована", size=9.5, color=MUTED))
    p.append(text(620, 418, "Апаратний пуск", size=9.5, color=MUTED))
    p.append(text(790, 418, "Код ще не виконався!", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "connect-under-reset.svg"), W, H, *p,
           title="Connect under Reset: перехоплення керування ядром до виконання прошивки")


# ── 4. Дерево пошуку несправностей ────────────────────────────────────────────
def fig_bringup_troubleshooting_tree():
    W, H = 940, 560
    p = []

    # Головний заголовок блоку
    p.append(rect(310, 40, 320, 40, fill="#fee2e2", stroke=POS, sw=2, rx=6))
    p.append(text(470, 65, "Cannot connect to target / Target not found", size=12, color=POS, bold=True))

    # Стовпчик 1: Живлення
    p.append(arrow(470, 80, 200, 120, color=LINE, sw=1.5))
    p.append(rect(80, 120, 240, 60, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=5))
    p.append(text(200, 142, "1. Напруга VDD та VTref", size=11.5, color=INK, bold=True))
    p.append(text(200, 161, "Вольтметром на пінах чіпа: 3.3 В?", size=10, color=MUTED))

    p.append(arrow(140, 180, 140, 220, color=POS, sw=1.5))
    p.append(rect(45, 220, 190, 50, fill="#fff5f5", stroke=POS, sw=1.2, rx=4))
    p.append(text(140, 239, "Ні (0 В або <3.0 В)", size=10.5, color=POS, bold=True))
    p.append(text(140, 256, "КЗ, LDO вимкнено, обрив", size=9.5, color=MUTED))

    # Стовпчик 2: Ядро і VCAP
    p.append(arrow(470, 80, 470, 120, color=LINE, sw=1.5))
    p.append(rect(350, 120, 240, 60, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=5))
    p.append(text(470, 142, "2. Напруга ядра на VCAP", size=11.5, color=INK, bold=True))
    p.append(text(470, 161, "Вольтметром на VCAP: 1.2 В?", size=10, color=MUTED))

    p.append(arrow(470, 180, 470, 220, color=POS, sw=1.5))
    p.append(rect(370, 220, 200, 50, fill="#fff5f5", stroke=POS, sw=1.2, rx=4))
    p.append(text(470, 239, "Ні (0 В або шум)", size=10.5, color=POS, bold=True))
    p.append(text(470, 256, "Забули 2.2 мкФ VCAP кераміку", size=9.5, color=POS, bold=True))

    # Стовпчик 3: Скидання та BOOT0
    p.append(arrow(470, 80, 740, 120, color=LINE, sw=1.5))
    p.append(rect(620, 120, 240, 60, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=5))
    p.append(text(740, 142, "3. Рівні на NRST та BOOT0", size=11.5, color=INK, bold=True))
    p.append(text(740, 161, "NRST = 3.3 В, BOOT0 = 0 В (GND)?", size=10, color=MUTED))

    p.append(arrow(740, 180, 740, 220, color=POS, sw=1.5))
    p.append(rect(645, 220, 190, 50, fill="#fff5f5", stroke=POS, sw=1.2, rx=4))
    p.append(text(740, 239, "Ні (NRST=0 або BOOT0=1)", size=10.5, color=POS, bold=True))
    p.append(text(740, 256, "Залип reset, висить BOOT0", size=9.5, color=MUTED))

    # Нижній рівень: Програмне лікування
    p.append(line(260, 180, 260, 310, color=FIELD, sw=1.5))
    p.append(line(260, 310, 470, 310, color=FIELD, sw=1.5))
    p.append(line(590, 180, 590, 310, color=FIELD, sw=1.5))
    p.append(line(860, 180, 860, 310, color=FIELD, sw=1.5))
    p.append(line(590, 310, 860, 310, color=FIELD, sw=1.5))
    p.append(arrow(470, 310, 470, 340, color=FIELD, sw=1.5))

    p.append(rect(280, 340, 380, 65, fill="#f0fdf4", stroke=FIELD, sw=2, rx=6))
    p.append(text(470, 363, "Апаратні напруги в нормі! Програмний крок:", size=11.5, color=FIELD, bold=True))
    p.append(text(470, 386, "Увімкнути режим «Connect under Reset»", size=12.5, color=INK, bold=True))

    p.append(arrow(380, 405, 250, 445, color=LINE, sw=1.5))
    p.append(rect(90, 445, 320, 85, fill="#ffffff", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(250, 468, "Успішне підключення!", size=11.5, color=FIELD, bold=True))
    p.append(text(250, 488, "Причина: попередня прошивка спала", size=10, color=INK))
    p.append(text(250, 508, "або ремапила піни SWDIO/SWCLK", size=10, color=MUTED))

    p.append(arrow(560, 405, 690, 445, color=LINE, sw=1.5))
    p.append(rect(530, 445, 320, 85, fill="#ffffff", stroke=POS, sw=1.5, rx=5))
    p.append(text(690, 468, "Помилка читання Flash (MEM-AP error)", size=11.5, color=POS, bold=True))
    p.append(text(690, 488, "Причина: активний захист RDP Level 1", size=10, color=INK))
    p.append(text(690, 508, "Рішення: RDP Unlock / Mass Erase через CLI", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "bringup-troubleshooting-tree.svg"), W, H, *p,
           title="Дерево пошуку несправностей при відмові першого контакту відлагоджувача")


if __name__ == "__main__":
    fig_swd_physical_layer()
    fig_signal_integrity_ringing()
    fig_connect_under_reset()
    fig_bringup_troubleshooting_tree()
    print("All figures generated successfully.")
