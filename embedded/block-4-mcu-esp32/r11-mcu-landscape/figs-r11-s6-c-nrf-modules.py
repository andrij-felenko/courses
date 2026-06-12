# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки r11-s6-c-nrf-modules.md
(🔌 Компонент: модулі nRF52-класу — радіо із сертифікованою антеною «з коробки»)

Фігури:
  fig-r11-6c-1-module-anatomy.svg  — що під металевим екраном модуля nRF52-класу
  fig-r11-6c-2-wiring-flash.svg    — підключення на власній платі + два шляхи прошивки

Вивід → ./img/
Стиль (AUTHORING §9): svgkit — спільні примітиви; текст лише через textbox()/fitbox().
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# Додаткові кольори для радіо-тематики
RF_GOLD   = "#c8900a"   # ВЧ/антена
RF_FILL   = "#2a1a0a"   # фон ВЧ-блоків
XTAL_CLR  = "#aaaa22"   # кварц
DCDC_CLR  = "#22aa88"   # DC-DC / зелено-блакитний
SHIELD    = "#4a4a4a"   # метал екрану
SHIELD_FG = "#cccccc"   # текст на екрані
GPIO_CLR  = "#3a5c8a"   # GPIO / SWD

# ────────────────────────────────────────────────────────────────────────────
# Рис. 4.11.6c.1 — Анатомія модуля nRF52-класу
# ────────────────────────────────────────────────────────────────────────────
def fig_module_anatomy():
    W, H = 820, 480
    frags = []

    # ── Металевий екран (зовнішня рамка модуля) ──────────────────────────────
    frags.append('<rect x="60" y="60" width="520" height="360" rx="10" '
                 'fill="#3a3a3a" stroke="#888" stroke-width="3"/>')
    tb, _, _ = textbox(320, 88, "Металевий екран (EMC shield)", size=12,
                       fill="#3a3a3a", stroke="#888", color=SHIELD_FG, bold=False)
    frags.append(tb)

    # ── Радіо-SoC (центр) ─────────────────────────────────────────────────────
    frags.append('<rect x="140" y="140" width="200" height="160" rx="8" '
                 'fill="#1a1a2a" stroke="#5566cc" stroke-width="2.5"/>')
    tb, _, _ = textbox(240, 220, "Радіо-SoC\nCortex-M4\n2.4 ГГц радіо\nFlash + RAM\n(на кристалі)",
                       size=12, fill="#1a1a2a", stroke="#5566cc", color="#aabbff", bold=True)
    frags.append(tb)

    # ── ВЧ-кристал 32 МГц ────────────────────────────────────────────────────
    frags.append('<rect x="370" y="120" width="130" height="52" rx="5" '
                 'fill="#2a2a10" stroke="#aaaa33" stroke-width="1.5"/>')
    frags.append(fitbox(370, 120, 130, 52, "Кварц\n32 МГц", size=12,
                        fill="#2a2a10", stroke="#aaaa33", color="#eeee88"))

    # ── Годинниковий кристал 32.768 кГц ─────────────────────────────────────
    frags.append('<rect x="370" y="190" width="130" height="52" rx="5" '
                 'fill="#1a2a2a" stroke="#33aaaa" stroke-width="1.5"/>')
    frags.append(fitbox(370, 190, 130, 52, "Кварц\n32.768 кГц\n(RTC/сон)", size=10,
                        fill="#1a2a2a", stroke="#33aaaa", color="#88eeee"))

    # Лінії від SoC до кристалів
    frags.append(line(340, 160, 370, 146, color="#aaaa33", sw=1.5, dash="4,3"))
    frags.append(line(340, 200, 370, 216, color="#33aaaa", sw=1.5, dash="4,3"))

    # ── DC-DC (дросель + LDO) ────────────────────────────────────────────────
    frags.append('<rect x="370" y="270" width="130" height="60" rx="5" '
                 'fill="#0a2a1a" stroke="#22aa88" stroke-width="1.5"/>')
    frags.append(fitbox(370, 270, 130, 60, "DC-DC\n(дросель + LDO)\nмікроамперний режим",
                        size=10, fill="#0a2a1a", stroke="#22aa88", color="#66eebb"))

    # ── π-ланка узгодження (matching) ────────────────────────────────────────
    frags.append('<rect x="140" y="330" width="130" height="50" rx="5" '
                 'fill="%s" stroke="%s" stroke-width="1.5"/>' % (RF_FILL, RF_GOLD))
    frags.append(fitbox(140, 330, 130, 50, "π-ланка\nузгодження (matching)",
                        size=10, fill=RF_FILL, stroke=RF_GOLD, color="#ffdd88"))

    # Лінія від SoC до matching
    frags.append(arrow(240, 300, 240, 330, color=RF_GOLD, sw=2))

    # ── Антена (за краєм екрану) ─────────────────────────────────────────────
    # Антена — PCB-доріжка на правому боці за межами екрану
    frags.append('<rect x="580" y="185" width="110" height="110" rx="6" '
                 'fill="#1a2a1a" stroke="%s" stroke-width="2"/>' % FIELD)
    frags.append(fitbox(580, 185, 110, 110, "PCB-антена\n(або U.FL)", size=11,
                        fill="#1a2a1a", stroke=FIELD, color="#88ffaa"))

    # Лінія від matching до антени
    frags.append(arrow(270, 355, 580, 240, color=RF_GOLD, sw=2))
    frags.append(text(430, 330, "RF-тракт", size=10, color=RF_GOLD, anchor="middle", italic=True))

    # ── Зона "no copper" під антеною (штрихова) ──────────────────────────────
    frags.append('<rect x="578" y="183" width="114" height="114" rx="8" '
                 'fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="6,4"/>' % FIELD)
    frags.append(text(635, 318, "↓ зона без міді", size=9, color=FIELD,
                      anchor="middle", italic=True))

    # ── SWD-стрілка назовні ──────────────────────────────────────────────────
    frags.append('<rect x="70" y="200" width="60" height="40" rx="5" '
                 'fill="#0a1a2a" stroke="#4488cc" stroke-width="1.5"/>')
    frags.append(fitbox(70, 200, 60, 40, "SWD\n(назовні)", size=9,
                        fill="#0a1a2a", stroke="#4488cc", color="#88ccff"))
    frags.append(arrow(130, 220, 140, 220, color="#4488cc", sw=2))
    frags.append(text(95, 252, "прошивка /\nналагодження", size=8, color="#4488cc", anchor="middle"))

    # ── Піни GPIO/VDD назовні ────────────────────────────────────────────────
    frags.append(text(70, 290, "GPIO\nVDD\nGND", size=9, color=SHIELD_FG,
                      anchor="middle", bold=False))
    for yy in [285, 302, 319]:
        frags.append(line(60, yy, 75, yy, color=MUTED, sw=1.2))

    # ── Легенда ──────────────────────────────────────────────────────────────
    frags.append(fitbox(590, 60, 210, 100,
                        "Flash і RAM —\nна кристалі SoC\n(не окремий чип,\nяк у RP2040/Pico)",
                        size=10, fill="#fffbe6", stroke="#ccaa00", color=INK))

    # ── Підпис головного висновку ─────────────────────────────────────────────
    frags.append(fitbox(590, 360, 210, 80,
                        "Антена + узгодження +\nвиміряний тракт =\nсертифікація включена",
                        size=10, fill="#eef8ee", stroke=FIELD, color=INK))

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(400, 34, "Анатомія модуля nRF52-класу: що під екраном", size=15,
                      bold=True, color=INK))

    render(os.path.join(OUT, "fig-r11-6c-1-module-anatomy.svg"), W, H, *frags,
           title=None)
    print("  fig-r11-6c-1-module-anatomy.svg — OK")


# ────────────────────────────────────────────────────────────────────────────
# Рис. 4.11.6c.2 — Підключення на власній платі + два шляхи прошивки
# ────────────────────────────────────────────────────────────────────────────
def fig_wiring_flash():
    W, H = 860, 340
    frags = []

    # ── Роздільник між панелями ────────────────────────────────────────────────
    frags.append(line(450, 30, 450, 310, color=MUTED, sw=1, dash="6,4"))
    frags.append(text(225, 22, "Підключення на власній платі", size=13,
                      bold=True, color=INK, anchor="middle"))
    frags.append(text(655, 22, "Два шляхи заливки firmware", size=13,
                      bold=True, color=INK, anchor="middle"))

    # ═══ ЛІВА ПАНЕЛЬ: підключення ═══════════════════════════════════════════

    # Модуль nRF52 (центр лівої панелі)
    frags.append('<rect x="130" y="80" width="180" height="210" rx="8" '
                 'fill="#2a2a3a" stroke="#5566cc" stroke-width="2.5"/>')
    frags.append(fitbox(130, 80, 180, 30, "Модуль nRF52", size=12,
                        fill="#1a1a2a", stroke="#5566cc", color="#aabbff", bold=True))

    # Піни модуля (права сторона блоку)
    pins_left = [
        ("VDD",      120, POS,   "#ffeaea"),
        ("GND",      158, MUTED, "#cccccc"),
        ("SWDIO",    196, "#4488cc", "#ddeeff"),
        ("SWCLK",    234, "#4488cc", "#ddeeff"),
        ("RESET",    272, MUTED, "#cccccc"),
        ("P0.xx",    310, FIELD, "#ddfff0"),
    ]
    for label, yy, clr, bg in pins_left:
        frags.append(fitbox(230, yy - 12, 78, 24, label, size=10,
                            fill=bg, stroke=clr, color=INK))

    # Антена (зліва від модуля, за краєм)
    frags.append('<rect x="50" y="145" width="72" height="64" rx="5" '
                 'fill="#1a2a1a" stroke="%s" stroke-width="1.5"/>' % FIELD)
    frags.append(fitbox(50, 145, 72, 64, "Антена\n(без\nміді\nпід нею)", size=9,
                        fill="#1a2a1a", stroke=FIELD, color="#88ffaa"))
    frags.append(line(50, 177, 130, 177, color=RF_GOLD, sw=1.5, dash="5,3"))
    frags.append(text(90, 170, "RF", size=9, color=RF_GOLD, anchor="middle", italic=True))

    # Конденсатор біля VDD
    frags.append(fitbox(50, 108, 65, 24, "C 100 нФ\n(VDD bypass)", size=8,
                        fill="#3a1a1a", stroke=POS, color="#ffaaaa"))
    frags.append(arrow(115, 120, 130, 120, color=POS, sw=1.5))
    # Лінія VDD→конденсатор
    frags.append(line(50, 120, 80, 120, color=POS, sw=1.5))

    # GND-полігон підпис
    frags.append(fitbox(50, 270, 65, 22, "GND\nполігон", size=9,
                        fill="#222222", stroke=MUTED, color="#cccccc"))
    frags.append(line(115, 281, 130, 281, color=MUTED, sw=1.5))

    # Підтяжка RESET
    frags.append(fitbox(50, 240, 65, 22, "10 кΩ\n→ VDD", size=9,
                        fill="#3a3a1a", stroke=MUTED, color="#ddddaa"))
    frags.append(line(115, 251, 130, 258, color=MUTED, sw=1.2, dash="3,2"))

    # SWD-роз'єм
    frags.append('<rect x="340" y="185" width="90" height="46" rx="5" '
                 'fill="#0a1a2a" stroke="#4488cc" stroke-width="1.5"/>')
    frags.append(fitbox(340, 185, 90, 46, "SWD\n(тест-площадки)", size=9,
                        fill="#0a1a2a", stroke="#4488cc", color="#88ccff"))
    frags.append(arrow(308, 205, 340, 205, color="#4488cc", sw=1.8))
    frags.append(arrow(308, 225, 340, 225, color="#4488cc", sw=1.8))

    # Підпис P0/P1 → периферія
    frags.append(text(375, 252, "P0/P1 → I2C/SPI/\nUART/ADC…", size=9,
                      color=FIELD, anchor="middle", italic=True))

    # ═══ ПРАВА ПАНЕЛЬ: два шляхи ══════════════════════════════════════════

    # Flash у модулі (ціль прошивки)
    frags.append('<rect x="690" y="120" width="150" height="100" rx="8" '
                 'fill="#1a2a1a" stroke="%s" stroke-width="2.5"/>' % FIELD)
    frags.append(fitbox(690, 120, 150, 100, "Firmware\nу Flash\n(всередині\nSoC)", size=12,
                        fill="#1a2a1a", stroke=FIELD, color="#88ffaa", bold=True))

    # Шлях 1: SWD-програматор
    frags.append('<rect x="470" y="80" width="160" height="60" rx="6" '
                 'fill="#0a1a2a" stroke="#4488cc" stroke-width="1.5"/>')
    frags.append(fitbox(470, 80, 160, 60, "SWD-програматор\n(перший bring-up,\nbare-metal)", size=10,
                        fill="#0a1a2a", stroke="#4488cc", color="#88ccff"))
    frags.append(arrow(630, 110, 690, 155, color="#4488cc", sw=2.2))
    frags.append(text(662, 130, "SWDIO/\nSWCLK", size=9, color="#4488cc",
                      anchor="middle", italic=True))

    # Шлях 2: DFU / OTA
    frags.append('<rect x="470" y="200" width="160" height="60" rx="6" '
                 'fill="#0a2a0a" stroke="%s" stroke-width="1.5"/>' % FIELD)
    frags.append(fitbox(470, 200, 160, 60, "DFU / OTA\n(USB — nRF52840;\nBLE OTA — будь-який)", size=10,
                        fill="#0a2a0a", stroke=FIELD, color="#88ffaa"))
    frags.append(arrow(630, 230, 690, 200, color=FIELD, sw=2.2))
    frags.append(text(662, 220, "USB /\nBLE", size=9, color=FIELD,
                      anchor="middle", italic=True))

    # Підпис виводу
    frags.append(fitbox(465, 278, 375, 28,
                        "SWD — перший раз; DFU/OTA — оновлення в полі без програматора",
                        size=9, fill="#fffbe6", stroke="#ccaa00", color=INK))

    render(os.path.join(OUT, "fig-r11-6c-2-wiring-flash.svg"), W, H, *frags,
           title=None)
    print("  fig-r11-6c-2-wiring-flash.svg — OK")


# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Генерую SVG для r11-s6-c-nrf-modules …")
    fig_module_anatomy()
    fig_wiring_flash()
    print("Готово.")
