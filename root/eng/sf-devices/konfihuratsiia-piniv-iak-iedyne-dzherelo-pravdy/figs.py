# -*- coding: utf-8 -*-
"""Фігури до теми «Конфігурація пінів як єдине джерело правди».
Запуск: python figs.py -> генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_pin_multiplexing_af_matrix():
    """Фігура 1: Матриця мультиплексування альтернативних функцій GPIO."""
    W, H = 860, 530
    f = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H),
        '<defs>',
        '<marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % LINE,
        '</marker>',
        '<marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % NEG,
        '</marker>',
        '<marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % FIELD,
        '</marker>',
        '</defs>',
        rect(0, 0, W, H, fill=BG, stroke="none")
    ]

    # Заголовок
    f.append(text(W / 2, 28, "Внутрішня комутація фізичного виводу (GPIO Pad)", size=16, bold=True))
    f.append(text(W / 2, 48, "Мультиплексування альтернативних функцій AF0..AF15 та конфігураційні каскади", size=12, color=MUTED, italic=True))

    # Ліва колонка: Джерела сигналів (Периферія та GPIO)
    b_uart, _, _ = textbox(110, 105, "USART1_TX\n(Периферія AF7)", size=11, fill="#eef4ff", stroke=NEG)
    b_spi, _, _ = textbox(110, 165, "SPI1_MOSI\n(Периферія AF5)", size=11, fill="#eef4ff", stroke=NEG)
    b_tim, _, _ = textbox(110, 225, "TIM1_CH1 (ШІМ)\n(Периферія AF1)", size=11, fill="#eef4ff", stroke=NEG)
    b_gpio, _, _ = textbox(110, 285, "GPIO_ODR\n(Вихідний регістр)", size=11, fill="#f4f6f8", stroke=LINE)
    b_adc, _, _ = textbox(110, 450, "ADC / DAC\n(Аналоговий тракт)", size=11, fill="#fdf2e9", stroke=POS)
    f.extend([b_uart, b_spi, b_tim, b_gpio, b_adc])

    # Мультиплексор виходів (AF MUX)
    f.append(rect(240, 80, 70, 230, fill="#e8f4fd", stroke=NEG, sw=1.5, rx=4))
    f.append(text(275, 185, "MUX\nВиходу", size=13, color=NEG, bold=True))
    f.append(text(275, 210, "AF0..AF15", size=10, color=MUTED))

    # Лінії від джерел до MUX
    f.append(line(185, 105, 240, 105, color=NEG))
    f.append(line(185, 165, 240, 145, color=NEG))
    f.append(line(185, 225, 240, 185, color=NEG))
    f.append(line(185, 285, 240, 225, color=LINE))

    # Регістр керування мультиплексором AFR
    b_afr, _, _ = textbox(275, 345, "Регістр GPIOx_AFR\n(4 біти: 0b0111 = AF7)", size=11, fill="#e9f7ef", stroke=FIELD)
    f.append(b_afr)
    f.append('<line x1="275" y1="322" x2="275" y2="310" stroke="%s" stroke-width="1.6" marker-end="url(#arrow-green)"/>' % FIELD)

    # Вихідний каскад (Output Driver)
    b_driver, _, _ = textbox(415, 195, "Вихідний драйвер\n(PMOS / NMOS)\nPush-Pull / Open-Drain\nРегістр OTYPER", size=11, fill="#f9f9f9", stroke=LINE)
    f.append(b_driver)
    f.append('<line x1="310" y1="195" x2="340" y2="195" stroke="%s" stroke-width="1.8" marker-end="url(#arrow-blue)"/>' % NEG)

    # Підтяжки (Pull-Up / Pull-Down)
    b_pupd, _, _ = textbox(570, 195, "Підтяжки R ≈ 40 кОм\nPull-Up / Pull-Down\nРегістр PUPDR", size=11, fill="#f9f9f9", stroke=LINE)
    f.append(b_pupd)
    f.append(line(490, 195, 500, 195, color=LINE, sw=1.8))

    # Вхідний каскад: тригер Шмітта
    b_schmitt, _, _ = textbox(510, 390, "Вхідний буфер\nТригер Шмітта\n(Регістр GPIOx_IDR)", size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b_schmitt)

    # Аналоговий перемикач
    b_asw, _, _ = textbox(510, 460, "Аналоговий комутатор\n(Регістр MODER = 0b11)", size=11, fill="#fdf2e9", stroke=POS)
    f.append(b_asw)
    f.append(line(185, 450, 420, 450, color=POS, sw=1.6))
    f.append(line(600, 460, 710, 460, color=POS, sw=1.6))
    f.append(line(710, 460, 710, 290, color=POS, sw=1.6))

    # Фізичний Pad (вивід чіпа)
    f.append(rect(680, 160, 60, 130, fill="#fef9e7", stroke="#d4ac0d", sw=2, rx=6))
    f.append(text(710, 215, "PAD", size=14, color="#7d6608", bold=True))
    f.append(text(710, 235, "Вивід МК", size=11, color="#7d6608"))

    # Зв'язки з PAD
    f.append(line(640, 195, 680, 195, color=LINE, sw=2))
    f.append(line(710, 290, 710, 390, color=LINE, sw=1.6))
    f.append('<line x1="710" y1="390" x2="590" y2="390" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>' % LINE)

    # Вхідна лінія йде вниз нижче блоку AFR
    f.append(line(430, 390, 370, 390, color=LINE, sw=1.4))
    f.append(line(370, 390, 370, 415, color=LINE, sw=1.4))
    f.append(line(370, 415, 60, 415, color=LINE, sw=1.4))
    f.append(line(60, 415, 60, 315, color=LINE, sw=1.4))
    f.append('<line x1="60" y1="315" x2="80" y2="315" stroke="%s" stroke-width="1.4" marker-end="url(#arrow)"/>' % LINE)
    f.append(text(215, 428, "Вхідна лінія: IDR або вхідна функція периферії (RX/MISO)", size=10, color=MUTED))

    # Фізична ніжка назовні
    f.append(line(740, 225, 820, 225, color=LINE, sw=3))
    f.append(circle(825, 225, 5, fill="#d4ac0d", stroke=LINE, sw=1.5))
    f.append(text(825, 205, "Фізичний пін", size=11, bold=True, anchor="middle"))
    f.append(text(825, 248, "PA9 / PB6...", size=10, color=MUTED, anchor="middle"))

    # Попереджувальний блок знизу
    b_warn, _, _ = textbox(W / 2, 505, "Неузгоджена конфігурація (два активні виходи Push-Pull) веде до короткого замикання та перегріву вихідних ключів.", size=10.5, fill="#fadbd8", stroke=POS, color=POS)
    f.append(b_warn)

    f.append('</svg>')
    out_path = os.path.join(IMG, 'pin-multiplexing-af-matrix.svg')
    with open(out_path, 'w', encoding='utf-8') as fp:
        fp.write("\n".join(f))
    print(f"Generated {out_path}")


def fig_devicetree_pin_configuration_pipeline():
    """Фігура 2: Конвеєр обробки та валідації конфігурації пінів у DeviceTree."""
    W, H = 840, 480
    f = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H),
        '<defs>',
        '<marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % LINE,
        '</marker>',
        '<marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % NEG,
        '</marker>',
        '<marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>' % FIELD,
        '</marker>',
        '</defs>',
        rect(0, 0, W, H, fill=BG, stroke="none")
    ]

    # Заголовок
    f.append(text(W / 2, 28, "Конвеєр декларативної конфігурації пінів (DeviceTree / SSOT)", size=16, bold=True))
    f.append(text(W / 2, 48, "Трансформація опису заліза в незмінні статичні структури конфігурації ядра", size=12, color=MUTED, italic=True))

    # Рівень 1: Вхідні декларативні файли
    f.append(rect(30, 80, 220, 310, fill="#f8f9fa", stroke="#bdc3c7", sw=1.5, rx=6))
    f.append(text(140, 105, "1. Декларативні маніфести", size=13, bold=True))
    b_soc, _, _ = textbox(140, 150, "soc.dtsi\n(Можливості кремнію МК)", size=11, fill="#ffffff", stroke=LINE)
    b_board, _, _ = textbox(140, 220, "board.dts\n(Розведення плати / SSOT)", size=11, fill="#e8f4fd", stroke=NEG)
    b_ovl, _, _ = textbox(140, 290, "app.overlay\n(Користувацькі зміни)", size=11, fill="#ffffff", stroke=LINE)
    b_bind, _, _ = textbox(140, 355, "pinctrl-bindings.yaml\n(Схема валідації)", size=10, fill="#fef9e7", stroke="#d4ac0d")
    f.extend([b_soc, b_board, b_ovl, b_bind])

    # Рівень 2: Збірка і Статична Валідація
    f.append(rect(290, 80, 240, 310, fill="#edf7ee", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(410, 105, "2. Компілятор і Валідатор", size=13, color=FIELD, bold=True))
    b_dtc, _, _ = textbox(410, 155, "DTC / Devicetree Preprocessor\n(Об'єднання вузлів дерева)", size=11, fill="#ffffff", stroke=LINE)
    b_val, _, _ = textbox(410, 240, "Статичний аналіз колізій:\n* Перевірка дублювання пінів\n* Контроль сумісності AF\n* Електричні режими (I2C OD)", size=10.5, fill="#ffffff", stroke=POS)
    b_err, _, _ = textbox(410, 345, "Виявлення помилок\nна етапі компіляції (CI/Build)", size=10.5, fill="#fadbd8", stroke=POS, color=POS)
    f.extend([b_dtc, b_val, b_err])

    # Стрілка між 1 і 2
    f.append('<line x1="250" y1="235" x2="285" y2="235" stroke="%s" stroke-width="2" marker-end="url(#arrow-green)"/>' % FIELD)

    # Рівень 3: Згенеровані структури і драйвери
    f.append(rect(570, 80, 240, 310, fill="#f4f6f9", stroke=NEG, sw=1.5, rx=6))
    f.append(text(690, 105, "3. Згенеровані структури", size=13, color=NEG, bold=True))
    b_cstruct, _, _ = textbox(690, 160, "devicetree_generated.h\nСтатичні таблиці в ROM:\n`const pinctrl_soc_pin_t`", size=10.5, fill="#ffffff", stroke=LINE)
    b_pstates, _, _ = textbox(690, 245, "Профілі стану пінів:\n* `pinctrl-0` (default/active)\n* `pinctrl-1` (sleep/low-power)\n* `pinctrl-2` (high-Z/analog)", size=10, fill="#ffffff", stroke=NEG)
    b_drv, _, _ = textbox(690, 345, "Драйвери периферії:\n`pinctrl_apply_state()`\nбез магічних чисел", size=10.5, fill="#eef4ff", stroke=NEG)
    f.extend([b_cstruct, b_pstates, b_drv])

    # Стрілка між 2 і 3
    f.append('<line x1="530" y1="235" x2="565" y2="235" stroke="%s" stroke-width="2" marker-end="url(#arrow-blue)"/>' % NEG)

    # Підсумкова стрічка
    b_foot, _, _ = textbox(W / 2, 440, "Єдине джерело правди усуває розпорошені виклики ініціалізації в драйверах і гарантує цілісність конфігурації заліза.", size=11, fill="#e8f8f5", stroke=FIELD)
    f.append(b_foot)

    f.append('</svg>')
    out_path = os.path.join(IMG, 'devicetree-pin-configuration-pipeline.svg')
    with open(out_path, 'w', encoding='utf-8') as fp:
        fp.write("\n".join(f))
    print(f"Generated {out_path}")


if __name__ == "__main__":
    fig_pin_multiplexing_af_matrix()
    fig_devicetree_pin_configuration_pipeline()
