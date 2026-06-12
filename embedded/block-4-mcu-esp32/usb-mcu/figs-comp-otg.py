# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки 4.12.8.c — «OTG-кабель і host-модулі».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Фігури:
  fig-r12-8c-1-id-pin.svg    — два micro-USB штекери; ID висить (device) vs ID на GND (host)
  fig-r12-8c-2-vbus-power.svg — три джерела VBUS 5 В для МК-host
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: ID-пін — що перемикає роль ────────────────────────────────────

def fig1_id_pin():
    W, H = 860, 460
    frags = []

    # ─── заголовок ──────────────────────────────────────────────────────────
    tb, _, _ = textbox(W // 2, 28, "П'ятий контакт ID вирішує роль: пристрій чи host",
                       size=14, bold=True, fill=FILL, stroke=MUTED, pad=8)
    frags.append(tb)

    # ─── розділова лінія між лівою і правою частинами ───────────────────────
    frags.append(line(W // 2, 50, W // 2, H - 50, color=MUTED, sw=1.2, dash="6,4"))

    # ─── ліва частина: micro-B (звичайний кабель) ───────────────────────────
    # Заголовок лівого стовпця
    tb_l, _, _ = textbox(215, 70, "micro-B (звичайний кабель)", size=13,
                         bold=True, fill="#fdecea", stroke=POS, pad=8)
    frags.append(tb_l)

    # 5 контактів штекера micro-B — таблиця зліва
    pins_left = [
        ("VBUS", "+5 В", "#fdecea", POS),
        ("D−",   "D−",   "#eaf0fd", NEG),
        ("D+",   "D+",   "#eaf0fd", NEG),
        ("ID",   "floating\n(не підключений)", "#fef9e7", "#e67e22"),
        ("GND",  "GND",  "#f4f6f8", MUTED),
    ]
    pin_x_name, pin_x_desc = 110, 270
    py_start = 120
    py_step = 58

    for i, (pname, pdesc, pfill, pstroke) in enumerate(pins_left):
        py = py_start + i * py_step
        tb_n, _, _ = textbox(pin_x_name, py, pname, size=13, bold=True,
                             fill=pfill, stroke=pstroke, pad=7, min_w=60)
        frags.append(tb_n)
        tb_d, _, _ = textbox(pin_x_desc, py, pdesc, size=12,
                             fill=pfill, stroke=pstroke, pad=7, min_w=120)
        frags.append(tb_d)
        # сполучна лінія між назвою і описом
        frags.append(line(pin_x_name + 35, py, pin_x_desc - 75, py,
                          color=pstroke, sw=1.2))

    # Плашка ролі
    tb_role_l, _, _ = textbox(215, py_start + 5 * py_step - 10,
                              "роль: ПРИСТРІЙ (device)",
                              size=13, bold=True, fill="#fdecea", stroke=POS, pad=10)
    frags.append(tb_role_l)

    # ─── права частина: micro-A (тільки в OTG-кабелі) ───────────────────────
    tb_r, _, _ = textbox(645, 70, "micro-A (тільки в OTG-кабелі)", size=13,
                         bold=True, fill="#edf7ed", stroke=FIELD, pad=8)
    frags.append(tb_r)

    pins_right = [
        ("VBUS", "+5 В", "#fdecea", POS),
        ("D−",   "D−",   "#eaf0fd", NEG),
        ("D+",   "D+",   "#eaf0fd", NEG),
        ("ID",   "→ GND\n(замкнутий!)", "#edf7ed", FIELD),
        ("GND",  "GND",  "#f4f6f8", MUTED),
    ]
    pin_x_name_r, pin_x_desc_r = 520, 680

    for i, (pname, pdesc, pfill, pstroke) in enumerate(pins_right):
        py = py_start + i * py_step
        tb_n, _, _ = textbox(pin_x_name_r, py, pname, size=13, bold=True,
                             fill=pfill, stroke=pstroke, pad=7, min_w=60)
        frags.append(tb_n)
        tb_d, _, _ = textbox(pin_x_desc_r, py, pdesc, size=12,
                             fill=pfill, stroke=pstroke, pad=7, min_w=120)
        frags.append(tb_d)
        frags.append(line(pin_x_name_r + 35, py, pin_x_desc_r - 75, py,
                          color=pstroke, sw=1.2))

    # Плашка ролі
    tb_role_r, _, _ = textbox(645, py_start + 5 * py_step - 10,
                              "роль: HOST",
                              size=13, bold=True, fill="#edf7ed", stroke=FIELD, pad=10)
    frags.append(tb_role_r)

    # ─── стрілка від ID-рядка правої колонки до блоку «контролер» ──────────
    ctrl_y = 390
    # лінія ID (права) → блок контролера
    frags.append(arrow(pin_x_desc_r + 78, py_start + 3 * py_step,
                       W // 2 + 10, ctrl_y - 18,
                       color=FIELD, sw=2))

    # блок «dual-role контролер»
    ctrl_text = "dual-role контролер\nчитає ID → обирає режим\nі вмикає VBUS"
    tb_ctrl, _, _ = textbox(W // 2 + 130, ctrl_y, ctrl_text, size=12,
                            fill="#edf7ed", stroke=FIELD, pad=10)
    frags.append(tb_ctrl)

    # ─── підпис-висновок ────────────────────────────────────────────────────
    note = "Господарем робить не кабель, а замкнутий на GND п'ятий контакт ID"
    tb_note, _, _ = textbox(W // 2, H - 22, note, size=12, fill="#f8f8f8",
                            stroke=MUTED, pad=8, color=MUTED)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r12-8c-1-id-pin.svg"), W, H, *frags,
           title="ID-пін micro-USB: device (floating) vs host (GND)")


# ── Фігура 2: звідки береться VBUS 5 В ──────────────────────────────────────

def fig2_vbus_power():
    W, H = 900, 480
    frags = []

    # ─── заголовок ──────────────────────────────────────────────────────────
    tb, _, _ = textbox(W // 2, 28,
                       "МК-host мусить сам подати 5 В на VBUS — чип їх не видає",
                       size=14, bold=True, fill=FILL, stroke=MUTED, pad=8)
    frags.append(tb)

    # ─── центральний блок: МК + Type-A гніздо ───────────────────────────────
    mcu_x, mcu_y = 450, 200
    tb_mcu, _, _ = textbox(mcu_x, mcu_y,
                           "МК-host\n(ESP32-S2/S3)\nUSB-OTG контролер",
                           size=13, bold=True, fill="#e8f4fd", stroke=NEG, pad=12)
    frags.append(tb_mcu)

    # Type-A гніздо праворуч від МК
    socket_x = 700
    tb_sock, _, _ = textbox(socket_x, mcu_y, "Type-A\nгніздо",
                            size=12, fill="#f4f6f8", stroke=LINE, pad=10)
    frags.append(tb_sock)

    # шина VBUS (від джерела до гнізда) — горизонтальна лінія
    frags.append(line(socket_x - 48, mcu_y - 30, socket_x + 48, mcu_y - 30,
                      color=POS, sw=2.5))
    frags.append(line(mcu_x + 60, mcu_y - 30, socket_x - 48, mcu_y - 30,
                      color=POS, sw=2.5))

    # підпис «чип сам 5 В не дає»
    tb_warn, _, _ = textbox(mcu_x, mcu_y - 55,
                            "чип сам 5 В не дає!",
                            size=11, fill="#fdecea", stroke=POS, pad=7, color=POS)
    frags.append(tb_warn)

    # лінії D+/D−/GND (від МК до гнізда)
    for i, (label, clr) in enumerate([("D+", NEG), ("D−", NEG), ("GND", MUTED)]):
        ly = mcu_y - 5 + i * 18
        frags.append(line(mcu_x + 60, ly, socket_x - 48, ly, color=clr, sw=1.5))

    # підпис VBUS на лінії
    tb_vbus_label, _, _ = textbox(590, mcu_y - 44, "VBUS +5 В",
                                  size=11, bold=True, fill="#fdecea", stroke=POS, pad=5, color=POS)
    frags.append(tb_vbus_label)

    # периферія (флешка/клавіатура) від гнізда
    peri_x = 820
    tb_peri, _, _ = textbox(peri_x, mcu_y, "флешка /\nклавіатура\n(периферія)",
                            size=11, fill="#f4f6f8", stroke=MUTED, pad=8)
    frags.append(tb_peri)
    frags.append(arrow(socket_x + 50, mcu_y, peri_x - 52, mcu_y,
                       color=LINE, sw=1.5))

    # бюджет струму
    tb_budget, _, _ = textbox(peri_x, mcu_y + 80, "5 В, до ~500 мА",
                              size=11, fill="#fef9e7", stroke="#e67e22", pad=8)
    frags.append(tb_budget)

    # ─── три джерела VBUS (зліва, знизу, нижче ліворуч) ────────────────────
    src_y_top = 340

    # (а) Ключ живлення на платі (load switch + GPIO)
    tb_a, _, _ = textbox(150, src_y_top,
                         "(а) load switch на платі\nGPIO enable → +5 В\n(host-модуль)",
                         size=12, fill="#edf7ed", stroke=FIELD, pad=10)
    frags.append(tb_a)
    frags.append(arrow(150, src_y_top - 42, mcu_x - 62, mcu_y - 30,
                       color=FIELD, sw=2))

    # (б) Зовнішні 5 В
    tb_b, _, _ = textbox(450, src_y_top,
                         "(б) зовнішні 5 В збоку\n(повербанк / окреме\nджерело)",
                         size=12, fill="#fef9e7", stroke="#e67e22", pad=10)
    frags.append(tb_b)
    frags.append(arrow(450, src_y_top - 42, 520, mcu_y - 30,
                       color="#e67e22", sw=2))

    # (в) Живлений USB-хаб
    tb_c, _, _ = textbox(750, src_y_top,
                         "(в) живлений USB-хаб\n(хаб сам живить\nпристрої)",
                         size=12, fill="#f4f6f8", stroke=MUTED, pad=10)
    frags.append(tb_c)
    frags.append(arrow(750, src_y_top - 42, socket_x + 10, mcu_y + 30,
                       color=MUTED, sw=2))

    # ─── підпис-висновок ────────────────────────────────────────────────────
    note = ("OTG-кабель дає дозвіл на роль host;  "
            "5 В для периферії треба взяти окремо — чип їх не генерує")
    tb_note, _, _ = textbox(W // 2, H - 22, note, size=12, fill="#f8f8f8",
                            stroke=MUTED, pad=8, color=MUTED)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r12-8c-2-vbus-power.svg"), W, H, *frags,
           title="VBUS 5 В для МК-host: три джерела і бюджет струму")


# ── Запуск ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    p1 = fig1_id_pin()
    p2 = fig2_vbus_power()
    print("Готово:")
    print("  ", os.path.join(OUT, "fig-r12-8c-1-id-pin.svg"))
    print("  ", os.path.join(OUT, "fig-r12-8c-2-vbus-power.svg"))
