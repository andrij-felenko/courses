# -*- coding: utf-8 -*-
"""Фігури теми «USB-C аудіоадаптер: резистор Ra і режим аналогового звуку».
Імпортує svgkit зі scripts/. Вивід у ./img/.
Запуск:  python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_adapter_concept():
    """Перепризначення виводів: 3.5 мм роз'єм TRRS переноситься на контакти USB Type-C."""
    W, H = 760, 360
    parts = []

    # Ліва колонка: 3.5 мм TRRS
    lx, ly, lw, lh = 50, 60, 200, 240
    parts.append(rect(lx, ly, lw, lh, fill="#f0f4f8", stroke=NEG, sw=2))
    parts.append(text(lx + lw / 2, ly + 26, "Роз'єм 3.5 мм TRRS", size=13, bold=True, color=NEG))

    trrs_pins = [
        ("Tip (кінчик)", "Лівий канал (Audio L)", "#e3f0fb"),
        ("Ring 1 (кільце 1)", "Правий канал (Audio R)", "#fdf2e0"),
        ("Ring 2 (кільце 2)", "Земля (AGND) / Mic", "#eaf3ea"),
        ("Sleeve (гільза)", "Мікрофон (Mic) / AGND", "#fdecea"),
    ]
    for i, (pin, sig, col) in enumerate(trrs_pins):
        py = ly + 50 + i * 44
        parts.append(rect(lx + 10, py, lw - 20, 36, fill=col, stroke=LINE, sw=1.2))
        parts.append(text(lx + 18, py + 16, pin, size=11, bold=True, anchor="start"))
        parts.append(text(lx + 18, py + 29, sig, size=10, color=MUTED, anchor="start"))

    # Права колонка: USB Type-C
    rx, ry, rw, rh = 510, 60, 200, 240
    parts.append(rect(rx, ry, rw, rh, fill="#fdfbf7", stroke=POS, sw=2))
    parts.append(text(rx + rw / 2, ry + 26, "Виводи USB Type-C", size=13, bold=True, color=POS))

    usbc_pins = [
        ("DP (A6 / B6)", "Лівий канал аудіо", "#e3f0fb"),
        ("DN (A7 / B7)", "Правий канал аудіо", "#fdf2e0"),
        ("SBU1 / SBU2", "Mic / Аналогова земля", "#eaf3ea"),
        ("CC1 + CC2", "Резистори Ra (1 кОм)", "#fdecea"),
    ]
    for i, (pin, sig, col) in enumerate(usbc_pins):
        py = ry + 50 + i * 44
        parts.append(rect(rx + 10, py, rw - 20, 36, fill=col, stroke=LINE, sw=1.2))
        parts.append(text(rx + 18, py + 16, pin, size=11, bold=True, anchor="start"))
        parts.append(text(rx + 18, py + 29, sig, size=10, color=MUTED, anchor="start"))

    # З'єднувальні стрілки по центру
    for i in range(4):
        y_arrow = ly + 68 + i * 44
        parts.append(arrow(lx + lw, y_arrow, rx, y_arrow, color=LINE, sw=1.8))

    box, _, _ = textbox(W / 2, 330,
                        ["Пасивний адаптер комутує аналогові сигнали безпосередньо на виводи Type-C.",
                         "Два резистори Ra сигналізують хосту про перехід у режим аудіоаксесуара."],
                        size=11, fill="#f4f6f8")
    parts.append(box)

    render(os.path.join(IMG, "adapter-concept.svg"), W, H, *parts,
           title="Перепризначення контактів у режимі Audio Adapter Accessory Mode")


def fig_cc_detection_state():
    """Схема детектування режиму Audio Adapter за двома резисторами Ra на лініях CC1 і CC2."""
    W, H = 760, 370
    parts = []

    # Хост (телефон / контролер порту)
    hx, hy, hw, hh = 40, 60, 300, 240
    parts.append(rect(hx, hy, hw, hh, fill="#fbf3f3", stroke=POS, sw=2))
    parts.append(text(hx + hw / 2, hy + 24, "Хост (порт Type-C)", size=13, bold=True, color=POS))

    # Аксесуар (аудіоадаптер)
    ax, ay, aw, ah = 480, 60, 240, 240
    parts.append(rect(ax, ay, aw, ah, fill="#f0f7f0", stroke=FIELD, sw=2))
    parts.append(text(ax + aw / 2, ay + 24, "Пасивний адаптер", size=13, bold=True, color=FIELD))

    # Лінії CC1 і CC2 між ними
    y_cc1 = 120
    y_cc2 = 220
    parts.append(line(hx + hw, y_cc1, ax, y_cc1, color=INK, sw=2.0))
    parts.append(line(hx + hw, y_cc2, ax, y_cc2, color=INK, sw=2.0))
    parts.append(text((hx + hw + ax) / 2, y_cc1 - 10, "CC1", size=12, bold=True))
    parts.append(text((hx + hw + ax) / 2, y_cc2 - 10, "CC2", size=12, bold=True))

    # Підтяжки Rp всередині хоста
    # CC1 підтяжка
    b1, _, _ = textbox(hx + 75, y_cc1 - 32, "Rp / 80 мкА", size=10, fill="#fdecea", stroke=POS)
    parts.append(b1)
    parts.append(line(hx + 75, y_cc1 - 15, hx + 75, y_cc1, color=POS, sw=1.5))
    parts.append(line(hx + 75, y_cc1, hx + hw, y_cc1, color=INK, sw=1.5))

    # CC2 підтяжка
    b2, _, _ = textbox(hx + 75, y_cc2 - 32, "Rp / 80 мкА", size=10, fill="#fdecea", stroke=POS)
    parts.append(b2)
    parts.append(line(hx + 75, y_cc2 - 15, hx + 75, y_cc2, color=POS, sw=1.5))
    parts.append(line(hx + 75, y_cc2, hx + hw, y_cc2, color=INK, sw=1.5))

    # Компаратори всередині хоста
    b_cmp1, _, _ = textbox(hx + 210, y_cc1 + 35, "Компаратор:\nV(CC1) ≤ vRa", size=10, fill="#ffffff", stroke=LINE)
    parts.append(b_cmp1)
    parts.append(line(hx + 210, y_cc1, hx + 210, y_cc1 + 18, color=INK, sw=1.5))

    b_cmp2, _, _ = textbox(hx + 210, y_cc2 + 35, "Компаратор:\nV(CC2) ≤ vRa", size=10, fill="#ffffff", stroke=LINE)
    parts.append(b_cmp2)
    parts.append(line(hx + 210, y_cc2, hx + 210, y_cc2 + 18, color=INK, sw=1.5))

    # Резистори Ra всередині адаптера
    b_ra1, _, _ = textbox(ax + 110, y_cc1 + 32, "Ra1 = 1 кОм\n(800–1200 Ом)", size=10, fill="#eaf3ea", stroke=FIELD)
    parts.append(b_ra1)
    parts.append(line(ax, y_cc1, ax + 110, y_cc1, color=INK, sw=1.5))
    parts.append(line(ax + 110, y_cc1, ax + 110, y_cc1 + 12, color=FIELD, sw=1.5))
    parts.append(line(ax + 110, y_cc1 + 52, ax + 110, y_cc1 + 64, color=FIELD, sw=1.5))
    parts.append(text(ax + 110, y_cc1 + 76, "GND", size=9.5, color=MUTED))

    b_ra2, _, _ = textbox(ax + 110, y_cc2 + 32, "Ra2 = 1 кОм\n(800–1200 Ом)", size=10, fill="#eaf3ea", stroke=FIELD)
    parts.append(b_ra2)
    parts.append(line(ax, y_cc2, ax + 110, y_cc2, color=INK, sw=1.5))
    parts.append(line(ax + 110, y_cc2, ax + 110, y_cc2 + 12, color=FIELD, sw=1.5))
    parts.append(line(ax + 110, y_cc2 + 52, ax + 110, y_cc2 + 64, color=FIELD, sw=1.5))
    parts.append(text(ax + 110, y_cc2 + 76, "GND", size=9.5, color=MUTED))

    box, _, _ = textbox(W / 2, 335,
                        ["Обидва виводи CC одночасно підтягнуті резисторами Ra до землі.",
                         "Напруга V(CC) < 0.2 В на обох лініях переводить порт у стан AudioAccessory."],
                        size=11, fill="#f4f6f8")
    parts.append(box)

    render(os.path.join(IMG, "cc-detection-state.svg"), W, H, *parts,
           title="Детектування аналогового аудіоадаптера за двома резисторами Ra")


def fig_passive_vs_active():
    """Порівняння пасивного аналогового адаптера та активного цифрового ЦАП."""
    W, H = 760, 360
    parts = []

    # Верхній блок: Пасивний адаптер
    y1 = 60
    parts.append(rect(40, y1, 680, 120, fill="#f8fafc", stroke=NEG, sw=1.5))
    parts.append(text(60, y1 + 22, "Пасивний адаптер (Analog Audio Accessory Mode)", size=12, bold=True, color=NEG, anchor="start"))

    # Блоки всередині пасивного
    b_phone1, _, _ = textbox(140, y1 + 70, "Смартфон:\nЦАП + Кодек + Ключ", size=10.5, fill="#fbf3f3", stroke=POS)
    b_dongle1, _, _ = textbox(380, y1 + 70, "Адаптер:\n2× Ra + Прямі дроти", size=10.5, fill="#eaf3ea", stroke=FIELD)
    b_out1, _, _ = textbox(620, y1 + 70, "Навушники:\nАналоговий звук", size=10.5, fill="#e3f0fb", stroke=NEG)
    parts.extend([b_phone1, b_dongle1, b_out1])

    parts.append(arrow(215, y1 + 70, 300, y1 + 70, color=LINE, sw=1.5))
    parts.append(text(257, y1 + 58, "Аналог L/R", size=9.5, color=MUTED))
    parts.append(arrow(460, y1 + 70, 555, y1 + 70, color=LINE, sw=1.5))
    parts.append(text(507, y1 + 58, "3.5 мм дріт", size=9.5, color=MUTED))

    # Нижній блок: Активний цифровий ЦАП
    y2 = 200
    parts.append(rect(40, y2, 680, 120, fill="#fdfbf7", stroke=POS, sw=1.5))
    parts.append(text(60, y2 + 22, "Активний адаптер (USB Audio Class 2.0 / Цифровий ЦАП)", size=12, bold=True, color=POS, anchor="start"))

    # Блоки всередині активного
    b_phone2, _, _ = textbox(140, y2 + 70, "Смартфон:\nЦифровий USB Host", size=10.5, fill="#fbf3f3", stroke=POS)
    b_dongle2, _, _ = textbox(380, y2 + 70, "Адаптер з мікросхемою:\nUSB контролер + ЦАП/АЦП", size=10.5, fill="#fdf2e0", stroke=POS)
    b_out2, _, _ = textbox(620, y2 + 70, "Навушники:\nАналоговий звук", size=10.5, fill="#e3f0fb", stroke=NEG)
    parts.extend([b_phone2, b_dongle2, b_out2])

    parts.append(arrow(215, y2 + 70, 275, y2 + 70, color=LINE, sw=1.5))
    parts.append(text(245, y2 + 58, "USB PCM дані", size=9.5, color=MUTED))
    parts.append(arrow(485, y2 + 70, 555, y2 + 70, color=LINE, sw=1.5))
    parts.append(text(520, y2 + 58, "Аналог 3.5 мм", size=9.5, color=MUTED))

    box, _, _ = textbox(W / 2, 335,
                        ["Пасивний адаптер вимагає аналогового кодека всередині смартфона.",
                         "Активний адаптер містить власний ЦАП і працює з будь-яким USB-хостом."],
                        size=11, fill="#f4f6f8")
    parts.append(box)

    render(os.path.join(IMG, "passive-vs-active.svg"), W, H, *parts,
           title="Архітектурна різниця: пасивний перехідник проти цифрового ЦАП")


def fig_analog_switch_mux():
    """Внутрішня комутація смартфона: аналоговий мультиплексор, захист OVP і від'ємний розмах."""
    W, H = 760, 360
    parts = []

    # Роз'єм Type-C зліва
    parts.append(rect(40, 70, 130, 210, fill="#f0f4f8", stroke=NEG, sw=1.5))
    parts.append(text(105, 95, "Роз'єм Type-C", size=12, bold=True, color=NEG))
    parts.append(text(105, 140, "DP (A6/B6)", size=10.5))
    parts.append(text(105, 175, "DN (A7/B7)", size=10.5))
    parts.append(text(105, 210, "SBU1 (A8)", size=10.5))
    parts.append(text(105, 245, "SBU2 (B8)", size=10.5))

    # Аналоговий комутатор / мультиплексор по центру
    parts.append(rect(230, 60, 270, 230, fill="#fdf2e0", stroke=POS, sw=2))
    parts.append(text(365, 84, "Аналоговий комутатор (FSA4480 / SGM7227)", size=11.5, bold=True, color=POS))

    # Складові всередині комутатора
    b_ovp, _, _ = textbox(365, 120, "Захист від перенапруги OVP (до 24 В)", size=10, fill="#fdecea", stroke=POS)
    b_pump, _, _ = textbox(365, 160, "Заряд-помпа від'ємної напруги (-3 В)", size=10, fill="#ffffff", stroke=LINE)
    b_cross, _, _ = textbox(365, 200, "Крос-комутатор Mic / AGND (OMTP ⇄ CTIA)", size=10, fill="#eaf3ea", stroke=FIELD)
    b_i2c, _, _ = textbox(365, 245, "I2C інтерфейс керування від TCPC", size=9.5, fill="#f0f7f0", stroke=MUTED)
    parts.extend([b_ovp, b_pump, b_cross, b_i2c])

    # Внутрішні блоки смартфона справа
    b_usb_phy, _, _ = textbox(635, 100, "USB 2.0 PHY\n(Контролер даних)", size=10, fill="#f4f6f8", stroke=LINE)
    b_audio_dac, _, _ = textbox(635, 170, "Аудіокодек\n(ЦАП L / R)", size=10, fill="#e3f0fb", stroke=NEG)
    b_mic_adc, _, _ = textbox(635, 240, "MICBIAS + АЦП\n/ Аудіоземля", size=10, fill="#eaf3ea", stroke=FIELD)
    parts.extend([b_usb_phy, b_audio_dac, b_mic_adc])

    # З'єднувальні лінії
    parts.append(line(170, 140, 230, 140, color=INK, sw=1.5))
    parts.append(line(170, 175, 230, 175, color=INK, sw=1.5))
    parts.append(line(170, 210, 230, 210, color=INK, sw=1.5))
    parts.append(line(170, 245, 230, 245, color=INK, sw=1.5))

    parts.append(line(500, 100, 565, 100, color=INK, sw=1.5))
    parts.append(line(500, 170, 565, 170, color=INK, sw=1.5))
    parts.append(line(500, 240, 565, 240, color=INK, sw=1.5))

    box, _, _ = textbox(W / 2, 330,
                        ["Комутатор ізолює чутливий аудіотракт від USB PHY, захищає від перенапруги на VBUS",
                         "і забезпечує розмах аудіосигналу нижче нуля вольтів завдяки вбудованій заряд-помпі."],
                        size=10.5, fill="#f4f6f8")
    parts.append(box)

    render(os.path.join(IMG, "analog-switch-mux.svg"), W, H, *parts,
           title="Структура аналогового комутатора аудіосигналів усередині смартфона")


def fig_charge_through_audio():
    """Схема адаптера з одночасним прослуховуванням аудіо та заряджанням (Charge-Through)."""
    W, H = 760, 360
    parts = []

    # Телефон зліва
    parts.append(rect(40, 70, 150, 220, fill="#fbf3f3", stroke=POS, sw=2))
    parts.append(text(115, 95, "Смартфон", size=12, bold=True, color=POS))
    parts.append(text(115, 115, "(Dual-Role / Sink)", size=10, color=MUTED))
    parts.append(text(115, 150, "Аудіотракт L/R", size=10.5))
    parts.append(text(115, 190, "CC контролер", size=10.5))
    parts.append(text(115, 230, "Вхід VBUS (5 В)", size=10.5, color=POS))

    # Адаптер з розгалуженням по центру
    parts.append(rect(240, 60, 280, 240, fill="#f0f7f0", stroke=FIELD, sw=2))
    parts.append(text(380, 85, "Адаптер Charge-Through", size=12, bold=True, color=FIELD))

    b_audio_br, _, _ = textbox(380, 130, "Розгалужувач аудіо L/R/Mic\n(прямий зв'язок з 3.5 мм)", size=10, fill="#e3f0fb", stroke=NEG)
    b_pwr_mgmt, _, _ = textbox(380, 190, "Комутація CC: Ra на аудіо,\nRd / PD на зарядний порт", size=10, fill="#ffffff", stroke=LINE)
    b_pwr_path, _, _ = textbox(380, 250, "Силовий ключ VBUS (5 В / 500 мА)\nіз захистом від зворотного струму", size=9.5, fill="#fdecea", stroke=POS)
    parts.extend([b_audio_br, b_pwr_mgmt, b_pwr_path])

    # Зовнішні підключення справа
    b_jack, _, _ = textbox(635, 130, "Роз'єм 3.5 мм\n(Навушники)", size=11, fill="#e3f0fb", stroke=NEG)
    b_charger, _, _ = textbox(635, 230, "Вхід Type-C\n(Зарядний пристрій)", size=11, fill="#fbf3f3", stroke=POS)
    parts.extend([b_jack, b_charger])

    # Зв'язки
    parts.append(arrow(240, 150, 190, 150, color=LINE, sw=1.5))
    parts.append(arrow(460, 130, 565, 130, color=LINE, sw=1.5))

    parts.append(arrow(565, 230, 480, 230, color=POS, sw=1.8))
    parts.append(arrow(240, 230, 190, 230, color=POS, sw=1.8))

    box, _, _ = textbox(W / 2, 330,
                        ["Режим Charge-Through дозволяє одночасно передавати аналогове аудіо",
                         "та живити пристрій струмом 500 мА (або більше за наявності PD контролера)."],
                        size=10.5, fill="#f4f6f8")
    parts.append(box)

    render(os.path.join(IMG, "charge-through-audio.svg"), W, H, *parts,
           title="Адаптер одночасного прослуховування аудіо та заряджання (Charge-Through)")


def main():
    fig_adapter_concept()
    fig_cc_detection_state()
    fig_passive_vs_active()
    fig_analog_switch_mux()
    fig_charge_through_audio()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
