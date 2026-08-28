# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Архітектура апаратної інжекції шин давачів (I2C/SPI) ────────────
def fig_sensor_bus_injection():
    W, H = 760, 390
    frags = []

    # Хост-симулятор (ліворуч)
    b_host, _, _ = textbox(130, 150, ["Хост-симулятор", "(ПК / Real-Time ОС)", "Модель фізики середовища", "Оновлення стану: 1 кГц"],
                           size=12, fill="#f4f6f8", stroke=LINE, sw=1.8, pad=12)
    frags.append(b_host)
    frags.append(text(130, 84, "СИМУЛЯТОР", size=11, color=MUTED, bold=True))

    # Емулятор шин (посередині - FPGA / Швидкий МК)
    b_emu, _, _ = textbox(380, 150, ["Емулятор шин (FPGA / МК)", "Двопортова пам'ять регістрів", "Апаратний I2C / SPI Target", "Інжекція збоїв (біт-фліпи, NACK)"],
                          size=12, fill="#eafaf0", stroke=FIELD, sw=2.0, pad=12)
    frags.append(b_emu)
    frags.append(text(380, 84, "МІСТ ІНЖЕКЦІЇ СИГНАЛІВ", size=11, color=FIELD, bold=True))

    # Випробуваний пристрій DUT (праворуч)
    b_dut, _, _ = textbox(630, 150, ["Випробувана плата (DUT)", "Справжній мікроконтролер", "Штатний драйвер давача", "Швидкість SPI: 10 МГц"],
                          size=12, fill="#eaf0fd", stroke=NEG, sw=2.0, pad=12)
    frags.append(b_dut)
    frags.append(text(630, 84, "РЕАЛЬНЕ ЗАЛІЗО (DUT)", size=11, color=NEG, bold=True))

    # Зв'язок Хост -> Емулятор (PCIe / Ethernet / USB-HS)
    frags.append(arrow(225, 135, 275, 135, color=LINE, sw=1.8))
    frags.append(arrow(275, 165, 225, 165, color=MUTED, sw=1.5))
    frags.append(text(250, 122, "Ethernet / USB", size=10, color=MUTED, bold=True))
    frags.append(text(250, 182, "Статус / Тріґери", size=9, color=MUTED))

    # Зв'язок Емулятор <-> DUT (Фізичні лінії SPI / I2C)
    frags.append(arrow(485, 135, 535, 135, color=FIELD, sw=2.0))
    frags.append(arrow(535, 165, 485, 165, color=NEG, sw=2.0))
    frags.append(text(510, 122, "SCK / MOSI / CS", size=10, color=FIELD, bold=True))
    frags.append(text(510, 182, "MISO / SDA / IRQ", size=10, color=NEG, bold=True))

    # Блок пояснення часового обмеження
    frags.append(line(40, 245, 720, 245, color=MUTED, sw=1))
    frags.append(text(380, 275, "Критична вимога: емулятор зобов'язаний виставити перший біт MISO за десятки наносекунд",
                      size=12, color=INK, bold=True))
    frags.append(text(380, 298, "після спаду CS та першого фронту SCK. Звичайний МК у перериванні не встигає — потрібна FPGA або DMA.",
                      size=11, color=MUTED))
    frags.append(text(380, 320, "Штатна прошивка DUT не підозрює про підміну: електричні рівні, таймінги та регістри ідентичні датчику.",
                      size=11, color=MUTED))

    render(os.path.join(IMG, 'sensor-bus-injection.svg'), W, H, *frags,
           title="Архітектура апаратної інжекції цифрових шин давачів")


# ── Фігура 2: Тракт генерації радіосигналу GNSS та захист приймача ────────────
def fig_gnss_rf_chain():
    W, H = 760, 390
    frags = []

    # 1. Генератор сценарію
    b_scen, _, _ = textbox(110, 140, ["ПК / Генератор", "Траєкторія руху", "Ефемериди супутників", "Доплер + псевдовідстані"],
                           size=11, fill="#f4f6f8", stroke=LINE, sw=1.6, pad=10)
    frags.append(b_scen)
    frags.append(text(110, 78, "1. СЦЕНАРІЙ", size=11, color=MUTED, bold=True))

    # 2. SDR (Програмне радіо)
    b_sdr, _, _ = textbox(280, 140, ["SDR (ПЛІС + ЦАП)", "Синтез L1/L2/E1", "I/Q потоки 2.6 Мвиб/с", "Вихідна потужність: 0 дБм"],
                          size=11, fill="#eafaf0", stroke=FIELD, sw=1.8, pad=10)
    frags.append(b_sdr)
    frags.append(text(280, 78, "2. СИНТЕЗ RF", size=11, color=FIELD, bold=True))

    # 3. Каскад атенюаторів
    b_att, _, _ = textbox(460, 140, ["Каскад атенюаторів", "Постійний: −60 дБ", "Керований: 0..31.5 дБ", "Рівень: −130..−160 дБм"],
                          size=11, fill="#fef9e7", stroke=POS, sw=2.0, pad=10)
    frags.append(b_att)
    frags.append(text(460, 78, "3. ПОСЛАБЛЕННЯ", size=11, color=POS, bold=True))

    # 4. Безвідлункова / екранована камера з DUT
    b_box, _, _ = textbox(645, 140, ["Екран-бокс (Faraday)", "DUT: GNSS-модуль", "Чутливий МШУ (LNA)", "Ізоляція від ефіру >80 дБ"],
                          size=11, fill="#eaf0fd", stroke=NEG, sw=2.0, pad=10)
    frags.append(b_box)
    frags.append(text(645, 78, "4. ЗАХИЩЕНИЙ DUT", size=11, color=NEG, bold=True))

    # Стрілки тракту
    frags.append(arrow(185, 140, 205, 140, color=LINE, sw=1.8))
    frags.append(arrow(355, 140, 380, 140, color=FIELD, sw=2.0))
    frags.append(arrow(540, 140, 565, 140, color=POS, sw=2.0))

    frags.append(text(368, 126, "RF 0 дБм", size=9, color=FIELD, bold=True))
    frags.append(text(553, 126, "RF −130 дБм", size=9, color=POS, bold=True))

    # Пояснення захисту
    frags.append(line(40, 240, 720, 240, color=MUTED, sw=1))
    frags.append(text(380, 270, "Чому не можна з'єднувати SDR напряму: сигнал 0 дБм (1 мВт) миттєво спалить вхідний LNA приймача,",
                      size=12, color=POS, bold=True))
    frags.append(text(380, 292, "розрахований на нанопіковати (−130 дБм = 0.1 пВт). Каскад атенюаторів зрізає 13 порядків потужності.",
                      size=11, color=MUTED))
    frags.append(text(380, 314, "Екранована скриня унеможливлює витік штучного сигналу назовні (захист від нелегального супутникового спуфінгу).",
                      size=11, color=MUTED))

    render(os.path.join(IMG, 'gnss-rf-chain.svg'), W, H, *frags,
           title="Тракт генерації радіосигналу GNSS та каскад захисту")


# ── Фігура 3: Імітація радіоефіру та динамічного затухання сигналу ────────────
def fig_rf_channel_attenuation():
    W, H = 760, 390
    frags = []

    # Бортовий радіомодем DUT (ліворуч)
    b_tx, _, _ = textbox(120, 150, ["Бортовий трансивер", "Потужність: +20 дБм", "Діапазон: 868 / 2400 МГц", "Телеметрія / Керування"],
                         size=11, fill="#eaf0fd", stroke=NEG, sw=2.0, pad=10)
    frags.append(b_tx)
    frags.append(text(120, 85, "DUT (ТРАНСИВЕР АПАРАТА)", size=11, color=NEG, bold=True))

    # Блок емуляції каналу (посередині)
    b_ch, _, _ = textbox(380, 150, ["Керований RF-емулятор каналу", "Програмований атенюатор (0..95 дБ)", "Генератор релеївського завмирання", "Інжектор шуму та завад (AWGN)"],
                         size=11, fill="#fef9e7", stroke=POS, sw=2.0, pad=12)
    frags.append(b_ch)
    frags.append(text(380, 85, "МАТРИЦЯ ЗАТУХАННЯ ТА ЗАВАД", size=11, color=POS, bold=True))

    # Наземна станція керування (праворуч)
    b_rx, _, _ = textbox(640, 150, ["Наземний модем / Пульт", "Чутливість: −115 дБм", "Вимірювання RSSI та SNR", "Оцінка втрат пакетів (PER)"],
                         size=11, fill="#eafaf0", stroke=FIELD, sw=2.0, pad=10)
    frags.append(b_rx)
    frags.append(text(640, 85, "НАЗЕМНА СТАНЦІЯ (GCS)", size=11, color=FIELD, bold=True))

    # З'єднання коаксіальними кабелями
    frags.append(arrow(210, 138, 255, 138, color=NEG, sw=2.0))
    frags.append(arrow(255, 162, 210, 162, color=LINE, sw=1.8))
    frags.append(text(232, 124, "Коаксіал RF", size=9, color=NEG, bold=True))

    frags.append(arrow(505, 138, 550, 138, color=LINE, sw=1.8))
    frags.append(arrow(550, 162, 505, 162, color=FIELD, sw=2.0))
    frags.append(text(528, 124, "Коаксіал RF", size=9, color=FIELD, bold=True))

    # Пояснення моделі Фрііса
    frags.append(line(40, 245, 720, 245, color=MUTED, sw=1))
    frags.append(text(380, 275, "Модель зв'язку: втрати на відстані (формула Фрііса) + орієнтація антени (провали діаграми) + завмирання",
                      size=12, color=INK, bold=True))
    frags.append(text(380, 298, "Замість прогулянок у полі на 5 км стенд змінює атенюацію від 40 дБ (100 м) до 95 дБ (край зв'язку) за мілісекунди.",
                      size=11, color=MUTED))
    frags.append(text(380, 320, "Перевірка переходу на аварійний протокол, зміна потужності передавача та адаптація бітрейту під завадами.",
                      size=11, color=MUTED))

    render(os.path.join(IMG, 'rf-channel-attenuation.svg'), W, H, *frags,
           title="Імітація радіоефіру та динамічного затухання сигналу")


# ── Фігура 4: Симуляція батареї з внутрішнім опором та динамічне навантаження ─
def fig_dynamic_load_power_tree():
    W, H = 760, 400
    frags = []

    # 1. Симулятор батареї (ліворуч)
    b_bat, _, _ = textbox(130, 155, ["Симулятор батареї", "Джерело ЕРС E(SoC)", "+ Програмний опір R_int", "Просідання при стрибках струму"],
                          size=11, fill="#fef9e7", stroke=POS, sw=2.0, pad=10)
    frags.append(b_bat)
    frags.append(text(130, 88, "1. ДЖЕРЕЛО ЖИВЛЕННЯ", size=11, color=POS, bold=True))

    # 2. Плата DUT з регуляторами (посередині)
    b_dut, _, _ = textbox(380, 155, ["Плата пристрою (DUT)", "DC-DC перетворювач (Buck)", "LDO для мікроконтролера", "BMS та датчик струму (Shunt)"],
                          size=11, fill="#eaf0fd", stroke=NEG, sw=2.0, pad=12)
    frags.append(b_dut)
    frags.append(text(380, 88, "2. ПЛАТА ТА ЖИВИЛЬНЕ ДЕРЕВО", size=11, color=NEG, bold=True))

    # 3. Динамічне навантаження (праворуч)
    b_load, _, _ = textbox(630, 155, ["Електронне навантаження", "Режими: CC / CV / CR / CP", "Імітація моторів: 0 -> 25 А", "Швидкість наростання: 5 А/мкс"],
                           size=11, fill="#eafaf0", stroke=FIELD, sw=2.0, pad=10)
    frags.append(b_load)
    frags.append(text(630, 88, "3. ДИНАМІЧНИЙ СПОЖИВАЧ", size=11, color=FIELD, bold=True))

    # Силові лінії
    frags.append(arrow(220, 142, 275, 142, color=POS, sw=2.5))
    frags.append(line(275, 168, 220, 168, color=LINE, sw=2.0))
    frags.append(text(248, 128, "V_bat (з просіданням)", size=9, color=POS, bold=True))
    frags.append(text(248, 185, "GND (Силовий)", size=9, color=MUTED))

    frags.append(arrow(485, 142, 540, 142, color=FIELD, sw=2.5))
    frags.append(line(540, 168, 485, 168, color=LINE, sw=2.0))
    frags.append(text(512, 128, "Силові шини (ESC)", size=9, color=FIELD, bold=True))
    frags.append(text(512, 185, "GND (Силовий)", size=9, color=MUTED))

    # Пояснення фізики перехідного процесу
    frags.append(line(40, 255, 720, 255, color=MUTED, sw=1))
    frags.append(text(380, 285, "Фізика ефекту: стрибок струму навантаження I_нав викликає миттєве падіння напруги на внутрішньому опорі:",
                      size=12, color=INK, bold=True))
    frags.append(text(380, 310, "V_вих = E_акб − I_нав · R_внутр. Якщо напруга просяде нижче порогу LDO, МК перезавантажиться (Brownout reset).",
                      size=11, color=POS))
    frags.append(text(380, 332, "Лабораторний блок без моделі R_int маскує цю вразливість, а електронне навантаження знаходить її до першого вильоту.",
                      size=11, color=MUTED))

    render(os.path.join(IMG, 'dynamic-load-power-tree.svg'), W, H, *frags,
           title="Симуляція батареї з внутрішнім опором та динамічне навантаження")


# ── Фігура 5: Єдина архітектура синхронізації та оркестрації стенда ───────────
def fig_integrated_rig_architecture():
    W, H = 760, 420
    frags = []

    # Головний оркестратор (зверху)
    b_orch, _, _ = textbox(380, 75, ["Головний оркестратор стенда (Test Runner)", "Спільна шкала часу (PTP / Hardware Trigger)", "Керування приладами через SCPI / PyVISA / LXI"],
                           size=12, fill="#f4f6f8", stroke=LINE, sw=2.0, pad=12)
    frags.append(b_orch)
    frags.append(text(380, 28, "ЦЕНТРАЛЬНА ОРКЕСТРАЦІЯ", size=11, color=MUTED, bold=True))

    # Чотири домени імітації (середній ряд)
    b_sens, _, _ = textbox(110, 200, ["Емулятор шин", "I2C / SPI / ADC", "IMU + Барометр"],
                           size=10, fill="#eafaf0", stroke=FIELD, sw=1.6, pad=8)
    frags.append(b_sens)

    b_gnss, _, _ = textbox(280, 200, ["GNSS SDR", "L1 / L2 сигнали", "Ефемериди + завади"],
                           size=10, fill="#eafaf0", stroke=FIELD, sw=1.6, pad=8)
    frags.append(b_gnss)

    b_rf, _, _ = textbox(470, 200, ["RF Атенюатор", "Керовані втрати", "Завмирання сигналу"],
                         size=10, fill="#eafaf0", stroke=FIELD, sw=1.6, pad=8)
    frags.append(b_rf)

    b_pwr, _, _ = textbox(645, 200, ["Джерело + Навантаження", "Модель батареї R_int", "Стрибки струму 0..30 А"],
                         size=10, fill="#eafaf0", stroke=FIELD, sw=1.6, pad=8)
    frags.append(b_pwr)

    # Стрілки оркестрації до приладів
    frags.append(arrow(310, 115, 150, 168, color=LINE, sw=1.5))
    frags.append(arrow(350, 115, 280, 168, color=LINE, sw=1.5))
    frags.append(arrow(410, 115, 470, 168, color=LINE, sw=1.5))
    frags.append(arrow(450, 115, 610, 168, color=LINE, sw=1.5))

    # Випробуваний пристрій DUT (знизу)
    b_dut, _, _ = textbox(380, 335, ["ВИПРОБУВАНИЙ ПРИСТРІЙ (DUT)", "Плата апарата + штатна прошивка без правок під стенд", "Оцінка орієнтації, регулятори моторів, модем зв'язку, моніторинг живлення"],
                          size=12, fill="#eaf0fd", stroke=NEG, sw=2.2, pad=14)
    frags.append(b_dut)

    # Стрілки фізичного впливу на DUT
    frags.append(arrow(110, 235, 260, 305, color=FIELD, sw=1.8))
    frags.append(arrow(280, 235, 330, 305, color=FIELD, sw=1.8))
    frags.append(arrow(470, 235, 430, 305, color=FIELD, sw=1.8))
    frags.append(arrow(645, 235, 500, 305, color=FIELD, sw=1.8))

    # Підписи типів зв'язку
    frags.append(text(175, 275, "Шини I2C/SPI", size=9, color=FIELD, bold=True))
    frags.append(text(295, 275, "RF GNSS", size=9, color=FIELD, bold=True))
    frags.append(text(460, 275, "RF Радіо", size=9, color=FIELD, bold=True))
    frags.append(text(585, 275, "V_bat / Сила", size=9, color=FIELD, bold=True))

    render(os.path.join(IMG, 'integrated-rig-architecture.svg'), W, H, *frags,
           title="Єдина архітектура синхронізації та оркестрації апаратного стенда")


if __name__ == "__main__":
    fig_sensor_bus_injection()
    fig_gnss_rf_chain()
    fig_rf_channel_attenuation()
    fig_dynamic_load_power_tree()
    fig_integrated_rig_architecture()
    print("All figures generated successfully.")
