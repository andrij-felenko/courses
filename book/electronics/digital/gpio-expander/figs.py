# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── concept: віддав 2 ніжки шини — дістав цілий банк GPIO ──────────────────────
# Ідея: дві лінії I²C коштують МК дві ніжки, а взамін дають 8 (PCF8574) або 16
# (MCP23017) нових виводів; адресні ніжки A0–A2 множать це на вісім чипів.

def fig_concept():
    W, H = 720, 300
    p = []
    ymid = 150

    # МК ліворуч
    p.append(rect(50, 108, 130, 96, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    p.append(text(115, 140, "мікроконтролер", size=12, color=NEG, bold=True))
    p.append(text(115, 162, "SDA · SCL", size=11, color=INK, bold=True))
    p.append(text(115, 182, "(лише 2 ніжки)", size=10, color=MUTED))

    # дві лінії шини
    p.append(arrow(180, ymid, 300, ymid, color=INK, sw=2.2))
    p.append(text(240, 138, "I²C", size=12, color=INK, bold=True))

    # чип-розширювач
    p.append(rect(300, 96, 180, 120, fill="#f4f6f8", stroke="#caa24a", sw=2, rx=12))
    p.append(text(390, 124, "розширювач", size=12, color="#8a6d1a", bold=True))
    p.append(text(390, 144, "PCF8574-клас", size=10, color=MUTED))
    # «ніжки» банку
    for i in range(8):
        yy = 158 + i * 6.5
        p.append(line(480, yy, 506, yy, color="#9a9aa0", sw=2))

    # вихід — банк GPIO
    p.append(text(590, 144, "8 нових GPIO", size=12, color=FIELD, bold=True))
    p.append(text(590, 164, "(P0…P7)", size=11, color=FIELD, bold=True))
    p.append(text(590, 188, "16 у MCP23017", size=10, color=MUTED))
    p.append(arrow(506, ymid, 530, ymid, color=FIELD, sw=2.0))

    # нижня смуга — адреса множить кількість
    box = fitbox(120, 248, 480, 36,
                 "A0–A2 задають адресу: 2 ніжки → до 8 чипів на шині → десятки виводів",
                 size=11, fill="#fbfbfb", stroke=MUTED, sw=1.4)
    p.append(box)

    render(os.path.join(OUT, "concept.svg"), W, H, *p,
           title="Розширювач: віддав 2 ніжки шини — дістав цілий банк GPIO")


# ── wiring: спільна шина, адресні ніжки, INT економить опитування ─────────────
# Ідея: SDA/SCL з підтяжками спільні з рештою пристроїв; A0–A2 на землю задають
# адресу; вивід INT дає чипу смикнути МК замість постійного опитування.

def fig_wiring():
    W, H = 720, 320
    p = []

    # МК і чип
    p.append(rect(50, 110, 130, 130, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    p.append(text(115, 150, "мікроконтролер", size=11, color=NEG, bold=True))
    p.append(rect(500, 100, 160, 150, fill="#f4f6f8", stroke="#caa24a", sw=2, rx=12))
    p.append(text(580, 126, "розширювач", size=11, color="#8a6d1a", bold=True))

    # шина живлення вгорі
    p.append(line(220, 86, 470, 86, color=POS, sw=2))
    p.append(text(220, 80, "VCC", size=10, color=POS, bold=True, anchor="start"))

    # SDA, SCL з підтяжками
    p.append(line(180, 150, 500, 150, color=NEG, sw=1.8))
    p.append(text(340, 144, "SDA", size=10, color=NEG, bold=True))
    p.append(line(290, 96, 290, 150, color=INK, sw=1.4))
    p.append(rect(282, 100, 16, 26, fill=BG, stroke=INK, sw=1.4, rx=3))

    p.append(line(180, 176, 500, 176, color=NEG, sw=1.8))
    p.append(text(340, 170, "SCL", size=10, color=NEG, bold=True))
    p.append(line(330, 96, 330, 176, color=INK, sw=1.4))
    p.append(rect(322, 100, 16, 26, fill=BG, stroke=INK, sw=1.4, rx=3))
    p.append(text(310, 96, "підтяжки", size=9, color=MUTED))

    # GND
    p.append(line(180, 200, 500, 200, color=FIELD, sw=1.6))
    p.append(text(340, 194, "GND", size=10, color=FIELD, bold=True))

    # адресні ніжки
    p.append(text(580, 200, "A0–A2 → GND", size=10, color=MUTED))
    p.append(text(580, 216, "(задає адресу)", size=9, color=MUTED))

    # навантаження на виходах
    p.append(line(660, 130, 695, 130, color="#9a9aa0", sw=2))
    p.append(circle(705, 130, 8, fill="#eef6ef", stroke=FIELD, sw=1.6))
    p.append(text(660, 124, "світлодіод", size=9, color=FIELD, anchor="start"))
    p.append(line(660, 168, 695, 168, color="#9a9aa0", sw=2))
    p.append(rect(695, 160, 20, 15, fill=BG, stroke=INK, sw=1.4, rx=3))
    p.append(text(660, 162, "кнопка", size=9, color=INK, anchor="start"))

    # INT назад до МК
    p.append(arrow(500, 226, 180, 226, color=POS, sw=1.8))
    p.append(text(340, 240, "INT → МК: «на вході щось змінилось»", size=10, color=POS, bold=True))

    box = fitbox(120, 280, 480, 32,
                 "Шина спільна з рештою пристроїв; INT дає чекати сигналу замість опитування",
                 size=10, fill="#fbfbfb", stroke=MUTED, sw=1.4)
    p.append(box)

    render(os.path.join(OUT, "wiring.svg"), W, H, *p,
           title="Підключення розширювача по I²C")


# ── pin-electric: чому PCF8574 тягне вниз сильно, а вгору ледь ─────────────────
# Ідея: поряд три виходи. Open-drain PCF8574 = сильний нижній транзистор +
# кволий струмок 100 мкА вгору; push-pull MCP23017 = обидва плеча сильні.
# Звідси правило монтажу: навантаження PCF8574 — на землю.

def fig_pin_electric():
    W, H = 720, 330
    p = []
    p.append(text(W / 2, 50, "Чому навантаження PCF8574 вішають на землю, а не на плюс",
                  size=12, color=MUTED, italic=True))

    # ── ліва панель: PCF8574, квазі-двонапрямний ──
    lx = 170
    p.append(rect(60, 78, 280, 222, fill="#fdf6ee", stroke="#caa24a", sw=1.6, rx=10))
    p.append(text(lx, 102, "PCF8574: квазі-двонапрямний", size=12, color="#8a6d1a", bold=True))

    # верх: слабкий струмок до VCC
    p.append(line(lx, 120, lx, 150, color=POS, sw=1.6, dash="4 3"))
    p.append(text(lx, 132, "VCC", size=9, color=POS, anchor="end"))
    p.append(circle(lx, 160, 11, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text(lx, 164, "≈", size=12, color=POS, bold=True))
    p.append(text(lx + 70, 162, "≈100 мкА", size=10, color=POS))
    p.append(text(lx + 70, 176, "(ледь тягне вгору)", size=9, color=MUTED))

    # вузол-ніжка
    p.append(circle(lx, 200, 4, fill=INK, stroke=INK, sw=1))
    p.append(text(lx + 36, 204, "ніжка P", size=9, color=INK, anchor="start"))

    # низ: сильний транзистор до GND
    p.append(line(lx, 204, lx, 232, color=NEG, sw=3.2))
    p.append(rect(lx - 16, 232, 32, 22, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    p.append(text(lx, 247, "↧", size=13, color=NEG, bold=True))
    p.append(line(lx, 254, lx, 276, color=NEG, sw=3.2))
    p.append(text(lx, 290, "GND", size=9, color=NEG))
    p.append(text(lx + 78, 246, "до ~25 мА", size=10, color=NEG))
    p.append(text(lx + 78, 260, "(сильно тягне вниз)", size=9, color=MUTED))

    # ── права панель: MCP23017, push-pull ──
    rx0 = 540
    p.append(rect(380, 78, 280, 222, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(rx0, 102, "MCP23017: двотактний (push-pull)", size=12, color="#1f7a3b", bold=True))

    p.append(line(rx0, 120, rx0, 150, color=POS, sw=1.6))
    p.append(text(rx0, 132, "VCC", size=9, color=POS, anchor="end"))
    p.append(rect(rx0 - 16, 150, 32, 22, fill="#fdecea", stroke=POS, sw=2.2, rx=3))
    p.append(text(rx0, 165, "↥", size=13, color=POS, bold=True))
    p.append(line(rx0, 172, rx0, 200, color=POS, sw=3.0))
    p.append(text(rx0 + 70, 164, "сильно вгору", size=10, color=POS))

    p.append(circle(rx0, 200, 4, fill=INK, stroke=INK, sw=1))
    p.append(text(rx0 + 36, 204, "ніжка", size=9, color=INK, anchor="start"))

    p.append(line(rx0, 204, rx0, 232, color=NEG, sw=3.0))
    p.append(rect(rx0 - 16, 232, 32, 22, fill="#eaf0fd", stroke=NEG, sw=2.2, rx=3))
    p.append(text(rx0, 247, "↧", size=13, color=NEG, bold=True))
    p.append(line(rx0, 254, rx0, 276, color=NEG, sw=3.0))
    p.append(text(rx0, 290, "GND", size=9, color=NEG))
    p.append(text(rx0 + 70, 246, "сильно вниз", size=10, color=NEG))

    render(os.path.join(OUT, "pin-electric.svg"), W, H, *p,
           title="Електрика виходу: open-drain проти push-pull")


if __name__ == "__main__":
    fig_concept()
    fig_wiring()
    fig_pin_electric()
    print("OK: figures written to", OUT)
