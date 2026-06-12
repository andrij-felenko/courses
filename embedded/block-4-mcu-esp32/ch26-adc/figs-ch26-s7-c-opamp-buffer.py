# -*- coding: utf-8 -*-
"""
Фігури для вставки §4.8.7c «Повторювач на ОП перед АЦП: розв'язуємо імпеданс джерела».
Дві фігури:
  fig-26-7c-1-buffer-schematic-esp32.svg  — конкретна схема ввімкнення
  fig-26-7c-2-raw-vs-buffered-undershoot.svg — виміряний результат «до/після»

Запуск: python figs-ch26-s7-c-opamp-buffer.py
Вивід: ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# FIG 1 — конкретна схема ввімкнення повторювача перед ADC1 ESP32
# ─────────────────────────────────────────────────────────────────────────────
def fig_buffer_schematic():
    W, H = 780, 480
    frags = []

    # ── Заголовок ────────────────────────────────────────────────────────────
    frags.append(text(W/2, 30, "Повторювач ОП перед ADC1 ESP32 — схема ввімкнення",
                      size=15, bold=True))

    # ── Резистивний подільник (ліва частина) ─────────────────────────────────
    # Rtop: від 3.3 В до вузла (середина)
    # Rbot: від вузла до GND
    div_x = 120          # x-координата вертикалі подільника
    v33_y  = 80          # верх (3.3 В)
    node_y = 220         # вузол (IN+ ОП)
    gnd_y  = 380         # низ (GND)

    # Лінія Rtop
    frags.append(line(div_x, v33_y + 16, div_x, node_y - 30, color=INK, sw=2))
    # Символ Rtop (зигзаг-резистор схематично — прямокутник)
    frags.append(rect(div_x - 14, v33_y + 16, 28, 50, fill=FILL, stroke=LINE, sw=1.5, rx=3))
    frags.append(text(div_x, v33_y + 41, "Rtop", size=11, color=MUTED))
    frags.append(text(div_x, v33_y + 55, "(100 кОм+)", size=9, color=MUTED))

    # 3.3 В підпис зверху
    frags.append(line(div_x, v33_y - 18, div_x, v33_y + 16, color=POS, sw=2))
    frags.append(text(div_x, v33_y - 22, "3.3 В", size=12, color=POS, bold=True))
    # Маленька лінія вгорі (шина)
    frags.append(line(div_x - 18, v33_y - 18, div_x + 18, v33_y - 18, color=POS, sw=2.5))

    # Лінія між Rtop і Rbot
    frags.append(line(div_x, node_y - 30, div_x, node_y - 14, color=INK, sw=2))
    # Символ Rbot
    frags.append(rect(div_x - 14, node_y - 14, 28, 50, fill=FILL, stroke=LINE, sw=1.5, rx=3))
    frags.append(text(div_x, node_y + 11, "Rbot", size=11, color=MUTED))
    frags.append(text(div_x, node_y + 25, "(100 кОм+)", size=9, color=MUTED))

    # GND від Rbot до низу
    frags.append(line(div_x, node_y + 36, div_x, gnd_y, color=INK, sw=2))
    # GND символ
    frags.append(line(div_x - 18, gnd_y, div_x + 18, gnd_y, color=NEG, sw=2.5))
    frags.append(line(div_x - 12, gnd_y + 6, div_x + 12, gnd_y + 6, color=NEG, sw=2))
    frags.append(line(div_x - 6, gnd_y + 12, div_x + 6, gnd_y + 12, color=NEG, sw=1.5))
    frags.append(text(div_x, gnd_y + 28, "GND", size=11, color=NEG))

    # ── Вузол (точка середини подільника) ────────────────────────────────────
    frags.append(circle(div_x, node_y, 5, fill=INK, stroke=INK, sw=1))
    tb, tw, th = textbox(div_x, node_y - 52, "вузол подільника\n(висока імпедансія)", size=10,
                          fill="#fff9e0", stroke="#caa24a", sw=1.2, pad=6)
    frags.append(tb)
    frags.append(line(div_x, node_y - 44, div_x, node_y - 5, color=MUTED, sw=1, dash="3,3"))

    # ── Горизонтальна лінія від вузла до IN+ ОП ──────────────────────────────
    op_cx = 400          # центр ОП по x
    op_cy = node_y       # вертикаль ОП = вертикаль вузла
    inp_x = op_cx - 70   # x де IN+ входить у трикутник ОП

    frags.append(line(div_x, node_y, inp_x, node_y, color=FIELD, sw=2.5))
    frags.append(text((div_x + inp_x) // 2, node_y - 10, "IN+ (сигнал)", size=10, color=FIELD))

    # ── Символ ОП (трикутник) ────────────────────────────────────────────────
    # Трикутник: вершина вправо
    op_h = 90   # висота трикутника
    op_w = 80   # ширина (глибина)
    pts = (f"{op_cx - op_w//2},{op_cy - op_h//2} "
           f"{op_cx - op_w//2},{op_cy + op_h//2} "
           f"{op_cx + op_w//2},{op_cy}")
    frags.append(f'<polygon points="{pts}" fill="#eef4ff" stroke="{LINE}" stroke-width="2"/>')

    # IN+ і IN− всередині трикутника
    frags.append(plus(op_cx - op_w//2 + 14, op_cy - 18, r=8))
    frags.append(minus(op_cx - op_w//2 + 14, op_cy + 18, r=8))
    frags.append(text(op_cx - 4, op_cy + 5, "ОП", size=13, bold=True, color=INK))

    # Пін IN+ (лінія з вершини до IN+ маркера)
    frags.append(line(op_cx - op_w//2, op_cy - 18, op_cx - op_w//2 + 6, op_cy - 18, color=INK, sw=1.5))
    # Пін IN− (лінія)
    frags.append(line(op_cx - op_w//2, op_cy + 18, op_cx - op_w//2 + 6, op_cy + 18, color=NEG, sw=1.5))

    # OUT (вершина трикутника)
    out_x = op_cx + op_w//2
    out_y = op_cy

    # ── Петля ×1: OUT → IN− ───────────────────────────────────────────────────
    fb_x1 = out_x + 20
    fb_y1 = out_y
    fb_y2 = op_cy + 18
    fb_x2 = op_cx - op_w//2

    # Лінія петлі (L-подібна: вправо від OUT, вниз, вліво до IN−)
    frags.append(line(out_x, out_y, fb_x1, fb_y1, color=NEG, sw=2))
    frags.append(line(fb_x1, fb_y1, fb_x1, fb_y2, color=NEG, sw=2))
    frags.append(line(fb_x1, fb_y2, fb_x2, fb_y2, color=NEG, sw=2))
    # Підпис петлі
    frags.append(text(fb_x1 + 30, (fb_y1 + fb_y2) // 2, "петля ×1\n(OUT→IN−)", size=10,
                      color=NEG, anchor="start"))

    # ── Лінія від IN+ у трикутник ────────────────────────────────────────────
    # Вже є горизонталь до inp_x; від inp_x до ліво-боку трикутника
    frags.append(line(inp_x, op_cy - 18, op_cx - op_w//2, op_cy - 18, color=FIELD, sw=2.5))

    # ── Живлення ОП ──────────────────────────────────────────────────────────
    vplus_x = op_cx
    vplus_y = op_cy - op_h//2 - 10

    # V+ від вершини трикутника вгору
    frags.append(line(vplus_x, op_cy - op_h//2, vplus_x, vplus_y - 22, color=POS, sw=2))
    frags.append(line(vplus_x - 14, vplus_y - 22, vplus_x + 14, vplus_y - 22, color=POS, sw=2.5))
    frags.append(text(vplus_x, vplus_y - 32, "V+ = 3.3 В", size=11, color=POS, bold=True))

    # Декаплінг 0.1 мкФ поряд із V+
    dc_x = vplus_x + 48
    dc_y = vplus_y - 22
    frags.append(line(dc_x, dc_y, dc_x, dc_y + 12, color=INK, sw=1.5))
    # Конденсатор (дві паралельні лінії)
    frags.append(line(dc_x - 10, dc_y + 12, dc_x + 10, dc_y + 12, color=INK, sw=2.5))
    frags.append(line(dc_x - 10, dc_y + 18, dc_x + 10, dc_y + 18, color=INK, sw=2.5))
    frags.append(line(dc_x, dc_y + 18, dc_x, dc_y + 30, color=INK, sw=1.5))
    frags.append(line(dc_x - 10, dc_y + 30, dc_x + 10, dc_y + 30, color=NEG, sw=2.5))  # GND
    frags.append(line(dc_x - 6, dc_y + 36, dc_x + 6, dc_y + 36, color=NEG, sw=2))
    frags.append(line(dc_x - 3, dc_y + 42, dc_x + 3, dc_y + 42, color=NEG, sw=1.5))
    frags.append(text(dc_x + 14, dc_y + 16, "0.1 мкФ\n(декаплінг)", size=10,
                      color=MUTED, anchor="start"))

    # Горизонтальна шина від V+ ОП до декаплінгу
    frags.append(line(vplus_x, dc_y, dc_x, dc_y, color=POS, sw=1.5, dash="4,3"))

    # V− (GND) від низу трикутника
    vminus_x = op_cx
    vminus_y = op_cy + op_h//2 + 10
    frags.append(line(vminus_x, op_cy + op_h//2, vminus_x, vminus_y + 16, color=NEG, sw=2))
    frags.append(line(vminus_x - 14, vminus_y + 16, vminus_x + 14, vminus_y + 16, color=NEG, sw=2.5))
    frags.append(line(vminus_x - 9, vminus_y + 22, vminus_x + 9, vminus_y + 22, color=NEG, sw=2))
    frags.append(line(vminus_x - 4, vminus_y + 28, vminus_x + 4, vminus_y + 28, color=NEG, sw=1.5))
    frags.append(text(vminus_x, vminus_y + 44, "V− = GND", size=11, color=NEG, bold=True))

    # ── Лінія з OUT до ADC1-ніжки ────────────────────────────────────────────
    adc_x = 650
    adc_y = out_y

    frags.append(line(out_x, out_y, adc_x - 60, adc_y, color=FIELD, sw=3))
    # Кружечок вузла на OUT
    frags.append(circle(out_x, out_y, 5, fill=INK, stroke=INK, sw=1))

    # Блок ESP32 ADC1
    tb2, tw2, th2 = textbox(adc_x + 30, adc_y, "ESP32\nADC1\n(GPIO32–39)", size=11,
                             fill="#e8f5e9", stroke=FIELD, sw=2, pad=10, bold=True)
    frags.append(tb2)
    # Стрілка до ADC-блоку
    frags.append(arrow(adc_x - 60, adc_y, adc_x, adc_y, color=FIELD, sw=2.5))
    frags.append(text((out_x + adc_x - 60) // 2, adc_y - 12,
                      "OUT → ADC1 (коротка доріжка)", size=10, color=FIELD))

    # ── Легенда (нижній правий кут) ─────────────────────────────────────────
    leg_x, leg_y = 50, 430
    frags.append(text(leg_x, leg_y, "Single-supply RRIO ОП (напр. MCP6001)", size=10,
                      color=MUTED, anchor="start"))
    frags.append(text(leg_x, leg_y + 15, "V+ = 3.3 В; V− = GND; підсилення = 1 (×1)", size=10,
                      color=MUTED, anchor="start"))

    render(os.path.join(OUT, "fig-26-7c-1-buffer-schematic-esp32.svg"), W, H, *frags,
           title=None)
    print("  fig-26-7c-1-buffer-schematic-esp32.svg OK")


# ─────────────────────────────────────────────────────────────────────────────
# FIG 2 — виміряний результат «до/після»: raw vs buffered
# ─────────────────────────────────────────────────────────────────────────────
def fig_raw_vs_buffered():
    W, H = 700, 440
    frags = []

    frags.append(text(W/2, 28, "Той самий МОм-подільник: пряме читання vs через буфер",
                      size=14, bold=True))

    # ── Підписи під стовпцями ────────────────────────────────────────────────
    col1_x = 200   # центр лівого стовпця
    col2_x = 490   # центр правого стовпця
    bar_w   = 110
    base_y  = 370  # нижня лінія стовпців (GND)

    # Максимальна висота (100% = істинна напруга)
    max_h = 260
    raw_h = int(max_h * 0.55)   # 55% — занижений (~945 mV з 1720 mV)
    buf_h = int(max_h * 0.97)   # 97% — майже істина (невелике IR на виходному R)

    # Вісь Y (шкала)
    axis_x = 80
    frags.append(line(axis_x, base_y - max_h - 20, axis_x, base_y + 5, color=MUTED, sw=1.5))
    for pct, label in [(0, "0 мВ"), (50, "~860 мВ"), (100, "~1720 мВ (Vtrue)")]:
        yy = base_y - int(max_h * pct / 100)
        frags.append(line(axis_x - 5, yy, axis_x + 5, yy, color=MUTED, sw=1.5))
        frags.append(text(axis_x - 8, yy + 4, label, size=10, color=MUTED, anchor="end"))
        if pct == 100:
            # Горизонтальна пунктирна лінія «істинна напруга»
            frags.append(line(axis_x, yy, W - 60, yy, color=FIELD, sw=1, dash="5,4"))
            frags.append(text(W - 56, yy + 4, "Vtrue", size=10, color=FIELD, anchor="start"))

    # Назва осі Y
    frags.append(text(axis_x - 40, base_y - max_h // 2, "Показ АЦП (мВ)", size=11,
                      color=MUTED))

    # Стовпець 1 — RAW (занижений)
    raw_y = base_y - raw_h
    frags.append(rect(col1_x - bar_w//2, raw_y, bar_w, raw_h,
                      fill="#fdecea", stroke=POS, sw=2, rx=4))
    frags.append(text(col1_x, raw_y - 10, "~945 мВ", size=13, color=POS, bold=True))
    frags.append(text(col1_x, raw_y - 24, "(-45%!)", size=11, color=POS))

    # Стрілка «недобір»
    frags.append(line(col1_x + bar_w//2 + 6, raw_y, col1_x + bar_w//2 + 6,
                      base_y - max_h, color=POS, sw=1.5, dash="3,3"))
    frags.append(arrow(col1_x + bar_w//2 + 6, raw_y,
                       col1_x + bar_w//2 + 6, base_y - max_h - 12, color=POS, sw=1.5))
    frags.append(text(col1_x + bar_w//2 + 40, (raw_y + base_y - max_h) // 2,
                      "недобір\n775 мВ", size=10, color=POS, anchor="start"))

    # Стовпець 2 — BUFFERED (≈ істина)
    buf_y = base_y - buf_h
    frags.append(rect(col2_x - bar_w//2, buf_y, bar_w, buf_h,
                      fill="#e8f5e9", stroke=FIELD, sw=2, rx=4))
    frags.append(text(col2_x, buf_y - 10, "~1670 мВ", size=13, color=FIELD, bold=True))
    frags.append(text(col2_x, buf_y - 24, "(≈ Vtrue)", size=11, color=FIELD))

    # ── Підписи під стовпцями ────────────────────────────────────────────────
    frags.append(text(col1_x, base_y + 20, "Пряме читання", size=12, bold=True, color=POS))
    frags.append(text(col1_x, base_y + 36, "(PIN_RAW — МОм напряму)", size=10, color=MUTED))
    frags.append(text(col2_x, base_y + 20, "Через повторювач", size=12, bold=True, color=FIELD))
    frags.append(text(col2_x, base_y + 36, "(PIN_BUF — буфер+ADC1)", size=10, color=MUTED))

    # ── Базова лінія (0 В) ───────────────────────────────────────────────────
    frags.append(line(axis_x, base_y, W - 40, base_y, color=NEG, sw=1.5))
    frags.append(text(W - 36, base_y + 4, "0 В", size=10, color=NEG, anchor="start"))

    # ── Виноска: очікуваний Serial.printf ───────────────────────────────────
    tb3, tw3, th3 = textbox(W//2, base_y + 90,
                             "Serial: raw=945 mV  buf=1670 mV  dif=+725 mV",
                             size=11, fill="#f5f5f5", stroke=MUTED, sw=1.5, pad=10,
                             color=INK)
    frags.append(tb3)
    frags.append(text(W//2, base_y + 90 + th3//2 + 14,
                      "Додатна різниця (dif) → підтверджено: АЦП недобирав через опір джерела",
                      size=10, color=MUTED))

    render(os.path.join(OUT, "fig-26-7c-2-raw-vs-buffered-undershoot.svg"), W, H, *frags,
           title=None)
    print("  fig-26-7c-2-raw-vs-buffered-undershoot.svg OK")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Генерація фігур §4.8.7c…")
    fig_buffer_schematic()
    fig_raw_vs_buffered()
    print("Готово.")
