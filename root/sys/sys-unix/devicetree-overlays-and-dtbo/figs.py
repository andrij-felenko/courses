# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"
PURPLE = "#f3e8ff"

# ── 1. Анатомія бінарного блоку DTBO ─────────────────────────────────────────
def fig_dtbo_anatomy():
    W, H = 1240, 680
    p = []

    # Колонка 1: Вихідний синтаксис DTS
    p.append(fitbox(40, 80, 380, 540,
                    "Вихідний текст оверлею (.dts)\n\n"
                    "/dts-v1/;\n"
                    "/plugin/;\n\n"
                    "/ {\n"
                    "    fragment@0 {\n"
                    "        target = <&i2c1>;\n"
                    "        __overlay__ {\n"
                    "            #address-cells = <1>;\n"
                    "            #size-cells = <0>;\n"
                    "            sensor: temp-sensor@48 {\n"
                    "                compatible = \"ti,tmp102\";\n"
                    "                reg = <0x48>;\n"
                    "                interrupt-parent = <&gpio2>;\n"
                    "                interrupts = <12 1>;\n"
                    "            };\n"
                    "        };\n"
                    "    };\n"
                    "};",
                    size=12, pad=14, fill=WARM, stroke=LINE))

    # Стрілка трансляції DTC
    p.append(arrow(430, 350, 510, 350))
    f_dtc, w_dtc, h_dtc = textbox(470, 305, ["компілятор dtc", "з прапором -@"], size=11, pad=6, fill=GREY, stroke=MUTED)
    p.append(f_dtc)

    # Колонка 2: Структура блоку DTBO
    p.append(rect(520, 80, 680, 540, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(540, 110, "Бінарна структура .dtbo в пам'яті (Flattened Tree)", size=14, bold=True, anchor="start"))

    # Секції DTBO
    y_hdr = 135
    p.append(fitbox(540, y_hdr, 640, 50,
                    "Заголовок fdt_header (magic 0xd00dfeed, totalsize, off_dt_struct)",
                    size=12, pad=8, fill=BLUE, stroke=LINE))

    y_frag = 195
    p.append(fitbox(540, y_frag, 640, 120,
                    "Вузол fragment@0 & __overlay__\n"
                    "  • target = <0x00000000> (тимчасовий phandle-заповнювач)\n"
                    "  • sensor: temp-sensor@48 (опис доданого пристрою)\n"
                    "    - interrupt-parent = <0x00000000> (тимчасовий phandle)",
                    size=12, pad=10, fill=GREEN, stroke=LINE))

    y_sym = 325
    p.append(fitbox(540, y_sym, 640, 70,
                    "Вузол __symbols__ (локальні мітки оверлею)\n"
                    "  • sensor = \"/fragment@0/__overlay__/temp-sensor@48\"",
                    size=12, pad=8, fill=PURPLE, stroke=LINE))

    y_fix = 405
    p.append(fitbox(540, y_fix, 640, 100,
                    "Вузол __fixups__ (посилання на мітки базового дерева)\n"
                    "  • i2c1 = \"/fragment@0:target:0\"\n"
                    "  • gpio2 = \"/fragment@0/__overlay__/temp-sensor@48:interrupt-parent:0\"",
                    size=12, pad=8, fill=RED, stroke=LINE))

    y_lfix = 515
    p.append(fitbox(540, y_lfix, 640, 85,
                    "Вузол __local_fixups__ (внутрішні phandle в оверлеї)\n"
                    "  • містить зсуви локальних phandle для перерахунку при завантаженні",
                    size=12, pad=8, fill=WARM, stroke=LINE))

    render(os.path.join(IMG, 'dtbo-structure-anatomy.svg'), W, H, *p,
           title="Анатомія бінарного блоку оверлею (DTBO) та метаданих компілятора dtc")

# ── 2. Процес дозвілу символів та phandle ───────────────────────────────────
def fig_dtbo_resolution():
    W, H = 1300, 720
    p = []

    # Лівий блок: Базове дерево
    p.append(fitbox(40, 80, 360, 580,
                    "Базове Дерево Пристроїв (of_root)\n\n"
                    "/soc/bus@40000000/i2c@40001000\n"
                    "  (phandle = 0x00000001)\n\n"
                    "/soc/bus@40000000/gpio@40002000\n"
                    "  (phandle = 0x00000002)\n\n"
                    "Вузол __symbols__:\n"
                    "  i2c1 = \"/soc/bus@40000000/i2c@40001000\"\n"
                    "  gpio2 = \"/soc/bus@40000000/gpio@40002000\"",
                    size=12, pad=12, fill=BLUE, stroke=LINE))

    # Правий блок: Оверлей з недозволеними посиланнями
    p.append(fitbox(900, 80, 360, 580,
                    "Фрагмент DTBO для накладання\n\n"
                    "Target path / phandle: ???\n"
                    "  (потребує i2c1)\n\n"
                    "Вузол temp-sensor@48\n"
                    "  interrupt-parent: ???\n"
                    "  (потребує gpio2)\n\n"
                    "Метадані __fixups__:\n"
                    "  i2c1 -> target\n"
                    "  gpio2 -> interrupt-parent",
                    size=12, pad=12, fill=RED, stroke=LINE))

    # Центральний блок: Ядро Linux (of_overlay_fdt_apply)
    cx = 650
    p.append(rect(430, 130, 440, 480, fill=GREEN, stroke=LINE, sw=1.8, rx=10))
    p.append(text(450, 160, "Механізм ядра of_overlay_fdt_apply()", size=14, bold=True, anchor="start"))

    step1, w1, h1 = textbox(cx, 220, ["1. Читання __fixups__ з оверлею"], size=12, pad=8, fill=BG, stroke=LINE)
    step2, w2, h2 = textbox(cx, 300, ["2. Пошук міток в __symbols__ базового дерева"], size=12, pad=8, fill=BG, stroke=LINE)
    step3, w3, h3 = textbox(cx, 380, ["3. Підстановка phandle: i2c1->0x1, gpio2->0x2"], size=12, pad=8, fill=BG, stroke=LINE)
    step4, w4, h4 = textbox(cx, 460, ["4. Перерахунок локальних phandle в оверлеї"], size=12, pad=8, fill=BG, stroke=LINE)
    step5, w5, h5 = textbox(cx, 540, ["5. Злиття вузлів у живе дерево of_root"], size=12, pad=8, fill=PURPLE, stroke=LINE)

    p.extend([step1, step2, step3, step4, step5])

    # Стрілки зв'язку
    p.append(arrow(400, 240, 430, 220))
    p.append(arrow(900, 240, 870, 220))
    p.append(arrow(650, 245, 650, 275))
    p.append(arrow(650, 325, 650, 355))
    p.append(arrow(650, 405, 650, 435))
    p.append(arrow(650, 485, 650, 515))

    render(os.path.join(IMG, 'dtbo-resolution-flow.svg'), W, H, *p,
           title="Розв'язання символів і phandle під час накладання DTBO")

# ── 3. Життєвий цикл DTBO через ConfigFS ─────────────────────────────────────
def fig_dtbo_lifecycle():
    W, H = 1300, 760
    p = []

    # Верхній рівень: Userspace
    p.append(rect(60, 70, 1180, 160, fill=WARM, stroke=LINE, sw=1.5, rx=8))
    p.append(text(80, 105, "Простір користувача (Userspace & ConfigFS)", size=14, bold=True, anchor="start"))

    f_u1, w_u1, h_u1 = textbox(250, 160, ["mkdir /sys/kernel/config/", "device-tree/overlays/display"], size=12, pad=10, fill=BG, stroke=LINE)
    f_u2, w_u2, h_u2 = textbox(650, 160, ["cat display.dtbo >", "overlays/display/dtbo"], size=12, pad=10, fill=BG, stroke=LINE)
    f_u3, w_u3, h_u3 = textbox(1050, 160, ["rmdir overlays/display", "(демонтування)"], size=12, pad=10, fill=BG, stroke=LINE)

    p.extend([f_u1, f_u2, f_u3])

    # Середній рівень: Ядро (Overlay Manager & OF Core)
    p.append(rect(60, 280, 1180, 220, fill=BLUE, stroke=LINE, sw=1.5, rx=8))
    p.append(text(80, 315, "Ядро Linux: Менеджер оверлеїв (OF Overlay Core)", size=14, bold=True, anchor="start"))

    f_k1, w_k1, h_k1 = textbox(250, 400, ["Створення запису оверлею", "struct overlay_changeset"], size=12, pad=10, fill=BG, stroke=LINE)
    f_k2, w_k2, h_k2 = textbox(650, 400, ["of_overlay_fdt_apply()", "• розв'язання phandle", "• модифікація of_root", "• сповіщення нотифікаторів"], size=12, pad=10, fill=GREEN, stroke=LINE)
    f_k3, w_k3, h_k3 = textbox(1050, 400, ["of_overlay_remove()", "• OF_OVERLAY_PRE_REMOVE", "• видалення device_node", "• звільнення токена"], size=12, pad=10, fill=RED, stroke=LINE)

    p.extend([f_k1, f_k2, f_k3])

    # Нижній рівень: Драйвери та пристрої
    p.append(rect(60, 540, 1180, 170, fill=PURPLE, stroke=LINE, sw=1.5, rx=8))
    p.append(text(80, 575, "Підсистема пристроїв та драйвери (Platform / I2C / SPI Bus)", size=14, bold=True, anchor="start"))

    f_d1, w_d1, h_d1 = textbox(450, 635, ["Створення struct device", "of_platform_populate()", "-> probe() драйвера"], size=12, pad=10, fill=GREEN, stroke=LINE)
    f_d2, w_d2, h_d2 = textbox(850, 635, ["Звільнення пристрою", "device_unregister()", "-> remove() & devres_release()"], size=12, pad=10, fill=RED, stroke=LINE)

    p.extend([f_d1, f_d2])

    # Послідовні стрілки життєвого циклу
    p.append(arrow(250, 210, 250, 355))
    p.append(arrow(650, 210, 650, 345))
    p.append(arrow(650, 455, 450, 585))
    p.append(arrow(1050, 210, 1050, 355))
    p.append(arrow(1050, 455, 850, 585))

    render(os.path.join(IMG, 'dtbo-configfs-lifecycle.svg'), W, H, *p,
           title="Життєвий цикл оверлею через ConfigFS: від створення до каскадного видалення")

if __name__ == '__main__':
    fig_dtbo_anatomy()
    fig_dtbo_resolution()
    fig_dtbo_lifecycle()
    print("Figures generated successfully.")
