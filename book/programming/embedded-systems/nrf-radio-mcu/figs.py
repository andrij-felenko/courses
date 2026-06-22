# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── wifi-vs-ble: заряд на одну сесію = площа під кривою струму ─────────────────
# Ідея: автономність вирішує не середній струм, а ЗАРЯД (струм × час) на одну
# радіо-сесію. Wi-Fi-сплеск — високий і довгий (велика площа); BLE-пакет —
# низький і короткий (мала площа). Та сама вісь часу й струму для обох.

def fig_wifi_vs_ble():
    W, H = 720, 340
    ox, oy = 80, 280
    aw, ah = 600, 220
    p = []

    # осі
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час", size=12, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 12, oy - ah - 2, "струм", size=12, color=INK, bold=True, anchor="end"))

    # рівні струму (орієнтири)
    def ylev(ma, full=250.0):
        return oy - ah * (ma / full)
    for ma in (180, 8):
        ly = ylev(ma)
        p.append(line(ox - 6, ly, ox, ly, color=MUTED, sw=1.0))
        p.append(text(ox - 10, ly + 4, "%d мА" % ma, size=10, color=MUTED, anchor="end"))

    # Wi-Fi-сплеск: високий і довгий прямокутний імпульс (площа = заряд)
    wx0, wx1 = ox + 30, ox + 30 + 150
    wy = ylev(180)
    p.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
             'fill="#d6e4f7" stroke="%s" stroke-width="2.4"/>'
             % (wx0, oy, wx0, wy, wx1, wy, wx1, oy, NEG))
    p.append(text((wx0 + wx1) / 2, wy - 12, "Wi-Fi (ESP32)", size=12, color=NEG, bold=True))
    p.append(text((wx0 + wx1) / 2, wy + (oy - wy) / 2, "≈180 мА × 200 мс", size=11, color=NEG))
    p.append(text((wx0 + wx1) / 2, oy + 18, "велика площа = великий заряд", size=10, color=NEG))

    # BLE-пакет: низький і короткий — у тому ж масштабі ледь видно
    bx0, bx1 = ox + 330, ox + 330 + 18
    by = ylev(8)
    p.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
             'fill="#f6d9d4" stroke="%s" stroke-width="2.4"/>'
             % (bx0, oy, bx0, by, bx1, by, bx1, oy, POS))
    p.append(text(bx1 + 8, by - 6, "BLE (nRF): ≈8 мА × 4 мс", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(bx1 + 8, by + 12, "крихітна площа = крихітний заряд", size=10, color=POS, anchor="start"))

    # лінія сну після BLE-пакета (майже по осі)
    sy = oy - ah * (0.002 / 250.0) - 2
    p.append(line(bx1, sy, ox + aw - 10, sy, color=POS, sw=1.4, dash="5 4"))
    p.append(text(ox + aw - 10, sy - 6, "сон ≈ мікроампери", size=10, color=POS, anchor="end"))

    p.append(text(W / 2, H - 10,
                  "Автономність вирішує заряд на сесію — площа під кривою, не миттєвий струм",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "wifi-vs-ble-current.svg"), W, H, *p,
           title="Чому радіо вирішує бюджет батареї: заряд на сесію = площа під струмом")


# ── three-classes: де nRF серед класів МК ─────────────────────────────────────
# Ідея: два питання-розвилки ведуть до трьох відповідей. Радіо на борту? — ні
# (AVR/STM32/RP2040). Так → що головне: пропускна здатність (ESP32) чи роки
# від монетки (nRF). nRF — єдиний клас, заточений під мікроампери.

def fig_three_classes():
    W, H = 720, 360
    p = []
    cx = W / 2

    # верхній вузол-питання
    q1, q1w, q1h = textbox(cx, 56, "Радіо потрібне\nна борту чипа?",
                           size=12, bold=True, fill="#f4f6f8", stroke=INK, sw=1.8, pad=12)
    p.append(q1)

    # ліва гілка: без радіо
    nx, ny = 150, 200
    nb, nbw, nbh = textbox(nx, ny, "ні → радіо ззовні\nAVR · STM32 · RP2040",
                           size=11, bold=True, color=MUTED, fill="#eef0f2", stroke=MUTED, sw=1.6, pad=11)
    p.append(line(cx - q1w / 2, 56, nx, ny - nbh / 2, color=MUTED, sw=1.6))
    p.append(text((cx - q1w / 2 + nx) / 2 - 6, (56 + ny) / 2 - 6, "ні", size=11, color=MUTED, bold=True))
    p.append(nb)

    # права гілка: так → друге питання
    q2x, q2y = cx + 120, 150
    q2, q2w, q2h = textbox(q2x, q2y, "так → що головне?",
                           size=12, bold=True, fill="#f4f6f8", stroke=INK, sw=1.8, pad=11)
    p.append(line(cx + q1w / 2, 70, q2x - q2w / 2, q2y - 8, color=INK, sw=1.6))
    p.append(text((cx + q1w / 2 + q2x) / 2, (70 + q2y) / 2 - 4, "так", size=11, color=INK, bold=True))
    p.append(q2)

    # дві відповіді другого питання
    ex, ey = cx - 30, 300
    eb, ebw, ebh = textbox(ex, ey, "пропускна здатність,\nWi-Fi-мережа → ESP32",
                           size=11, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.7, pad=11)
    p.append(line(q2x - 10, q2y + q2h / 2, ex, ey - ebh / 2, color=NEG, sw=1.6))
    p.append(eb)

    rx, ry = cx + 215, 300
    rb, rbw, rbh = textbox(rx, ry, "роки від монетки,\nмікроампери → nRF",
                           size=11, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=2.0, pad=11)
    p.append(line(q2x + 10, q2y + q2h / 2, rx, ry - rbh / 2, color=FIELD, sw=1.7))
    p.append(rb)

    render(os.path.join(OUT, "three-classes.svg"), W, H, *p,
           title="Три класи МК: дві розвилки ведуть до nRF")


# ── softdevice-memory: як SoftDevice ділить флеш і RAM із застосунком ──────────
# Ідея: SoftDevice — не бібліотека, яку компонуєш у свій бінарник, а окремий
# прошитий блок «знизу» пам'яті; застосунок живе «над» ним і кличе стек через
# єдиний шлюз (SVC). Чужу зону чіпати не можна.

def fig_softdevice_memory():
    W, H = 720, 330
    p = []

    # дві колонки: FLASH і RAM
    colw = 230
    fx = 110
    rx = 430
    top = 70
    bot = 290
    H_full = bot - top

    def stack(x, label, lo_frac, lo_name, hi_name, lo_col, hi_col):
        out = [text(x + colw / 2, top - 14, label, size=13, color=INK, bold=True)]
        ly = top + H_full * (1 - lo_frac)
        # верх — застосунок
        out.append(rect(x, top, colw, ly - top, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=4))
        out.append(mtext(x + colw / 2, (top + ly) / 2 - 4, hi_name, size=12, color=FIELD, bold=True))
        # низ — SoftDevice (зарезервовано)
        out.append(rect(x, ly, colw, bot - ly, fill="#eef4ff", stroke=NEG, sw=1.8, rx=4))
        out.append(mtext(x + colw / 2, (ly + bot) / 2 - 4, lo_name, size=12, color=NEG, bold=True))
        return out, ly

    f, fy = stack(fx, "FLASH", 0.40, "SoftDevice", "ваш застосунок", NEG, FIELD)
    p += f
    r, ry = stack(rx, "RAM", 0.30, "SoftDevice", "ваш застосунок", NEG, FIELD)
    p += r

    # шлюз SVC між застосунком і стеком
    gx = (fx + colw + rx) / 2
    g, gw, gh = textbox(gx, 175, "виклик стека\nчерез SVC", size=11, bold=True,
                        color="#8a5fb0", fill="#f2ecf8", stroke="#8a5fb0", sw=1.7, pad=9)
    p.append(g)
    p.append(line(fx + colw, (top + fy) / 2, gx - gw / 2, 175, color="#8a5fb0", sw=1.5, dash="4 3"))
    p.append(line(gx + gw / 2, 175, rx, (top + ry) / 2, color="#8a5fb0", sw=1.5, dash="4 3"))

    p.append(text(W / 2, H - 14,
                  "SoftDevice — прошитий «знизу» блок; застосунок лишає його пам'ять недоторканою",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "softdevice-memory.svg"), W, H, *p,
           title="SoftDevice ділить флеш і RAM із застосунком")


# ── module-anatomy: що зібрано під екраном модуля nRF52-класу ──────────────────
# Ідея: модуль = SoC + увесь ВЧ-обв'яз у одній екранованій коробці. Показуємо
# блоки під екраном (SoC із флеш/RAM на кристалі, два резонатори, DC-DC, π-ланка,
# антена) і зону без міді — те, за що насправді платять, купуючи модуль.

def fig_module_anatomy():
    W, H = 760, 430
    p = []

    # екран — велика рамка з підписом усередині згори
    sx, sy, sw, sh = 50, 70, 470, 320
    p.append(rect(sx, sy, sw, sh, fill="#fbfbfd", stroke=INK, sw=2.4))
    p.append(text(sx + sw / 2, sy + 18, "металевий екран (під ним — увесь радіотракт)",
                  size=11, color=MUTED))

    # SoC — серце модуля
    soc = fitbox(90, 150, 180, 150,
                 "радіо-SoC\nCortex-M4 + 2.4 ГГц радіо\nFlash і RAM на кристалі",
                 size=12, fill="#eef4ff", stroke=NEG, sw=2.2, bold=True, color=NEG)
    p.append(soc)

    # два резонатори праворуч від SoC
    p.append(fitbox(310, 140, 150, 50, "кварц 32 МГц\n(такт + опора радіо)",
                    size=10, fill="#fdf6e3", stroke="#b8860b", color=INK))
    p.append(fitbox(310, 210, 150, 50, "кварц 32.768 кГц\n(будить зі сну)",
                    size=10, fill="#eafaf0", stroke=FIELD, color=INK))

    # DC-DC
    p.append(fitbox(310, 290, 150, 56, "DC-DC (дросель+LDO)\nмікроамперний режим",
                    size=10, fill="#f2ecf8", stroke="#8a5fb0", color=INK))

    # π-ланка узгодження під SoC
    p.append(fitbox(90, 300, 180, 46, "π-ланка узгодження → 50 Ом",
                    size=10, fill="#f4f6f8", stroke="#b8860b", color=INK))
    p.append(arrow(180, 300, 180, 280, color="#b8860b", sw=1.6))

    # антена назовні екрана (праворуч), із зоною без міді
    ax, ay, aw_, ah_ = 580, 175, 120, 110
    p.append(rect(ax, ay, aw_, ah_, fill="#eafaf0", stroke=FIELD, sw=2.2))
    p.append(mtext(ax + aw_ / 2, ay + ah_ / 2 - 6, ["PCB-антена", "(або роз'єм U.FL)"],
                   size=11, color=FIELD, bold=True))
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="none" '
             'stroke="%s" stroke-width="1.6" stroke-dasharray="6 4"/>'
             % (ax - 8, ay - 8, aw_ + 16, ah_ + 16, FIELD))
    p.append(text(ax + aw_ / 2, ay + ah_ + 26, "зона без міді навколо", size=10, color=FIELD))
    p.append(arrow(270, 322, ax, ay + ah_ / 2, color="#b8860b", sw=1.6))

    # виводи назовні зліва: SWD, живлення/GPIO
    p.append(fitbox(560, 70, 150, 60, "назовні: VDD, GND,\nSWD (прошивка), GPIO",
                    size=10, fill="#f4f6f8", stroke=INK, color=INK))

    # ярлик-висновок праворуч знизу
    p.append(fitbox(560, 320, 170, 66,
                    "купуєш виміряний тракт\n+ сертифікацію\n(FCC/CE/TELEC)",
                    size=10, fill="#fdf6e3", stroke="#b8860b", bold=True, color=INK))

    render(os.path.join(OUT, "module-anatomy.svg"), W, H, *p,
           title="Анатомія модуля nRF52-класу: що зібрано під екраном")


# ── wiring-flash: мінімальний обв'яз модуля + два шляхи прошивки ───────────────
# Ідея: ліворуч — що треба розвести навколо модуля (живлення, GND, SWD, RESET,
# антена назовні); праворуч — два способи залити firmware: SWD перший раз,
# далі DFU/OTA без програматора.

def fig_wiring_flash():
    W, H = 820, 340
    p = []
    p.append(line(W / 2, 50, W / 2, H - 24, color=MUTED, sw=1.0, dash="6 4"))
    p.append(text(W / 4, 30, "Обв'яз на власній платі", size=13, color=INK, bold=True))
    p.append(text(3 * W / 4, 30, "Два шляхи залити firmware", size=13, color=INK, bold=True))

    # ── ліворуч: модуль із виводами ──
    mx, my, mw, mh = 230, 70, 150, 230
    p.append(rect(mx, my, mw, mh, fill="#eef4ff", stroke=NEG, sw=2.2))
    p.append(text(mx + mw / 2, my + 20, "модуль nRF52", size=11, color=NEG, bold=True))

    pins = [("VDD", POS, "#fdecea"), ("GND", MUTED, "#eef0f2"),
            ("SWDIO", NEG, "#eef4ff"), ("SWCLK", NEG, "#eef4ff"),
            ("RESET", MUTED, "#eef0f2"), ("P0/P1", FIELD, "#eafaf0")]
    py = my + 44
    for lab, col, fill in pins:
        p.append(fitbox(mx + mw - 8, py, 86, 22, lab, size=10, fill=fill, stroke=col, color=INK))
        py += 30

    # обв'яз ліворуч від модуля
    p.append(fitbox(70, 96, 96, 40, "C 100 нФ\nбіля VDD", size=9, fill="#fdecea", stroke=POS, color=INK))
    p.append(fitbox(70, 156, 96, 40, "GND-полігон\nсуцільний", size=9, fill="#eef0f2", stroke=MUTED, color=INK))
    p.append(fitbox(70, 216, 96, 40, "RESET → 10 кΩ\nна VDD", size=9, fill="#fdf6e3", stroke="#b8860b", color=INK))
    p.append(fitbox(70, 270, 96, 40, "антена назовні\nплати, без міді", size=9, fill="#eafaf0", stroke=FIELD, color=INK))

    # ── праворуч: два шляхи прошивки ──
    rx = W / 2 + 40
    p.append(fitbox(rx, 80, 180, 56, "SWD-програматор\n(перший bring-up)",
                    size=11, fill="#eef4ff", stroke=NEG, bold=True, color=NEG))
    p.append(fitbox(rx, 170, 180, 56, "DFU / OTA\n(оновлення в полі)",
                    size=11, fill="#eafaf0", stroke=FIELD, bold=True, color=FIELD))
    p.append(fitbox(rx + 210, 125, 110, 60, "firmware\nу Flash SoC",
                    size=11, fill="#f4f6f8", stroke=INK, bold=True, color=INK))
    p.append(arrow(rx + 180, 108, rx + 210, 150, color=NEG, sw=2.0))
    p.append(arrow(rx + 180, 198, rx + 210, 160, color=FIELD, sw=2.0))
    p.append(fitbox(rx, 252, 320, 40,
                    "SWD активує чип уперше; далі — USB (nRF52840) або BLE OTA",
                    size=10, fill="#fdf6e3", stroke="#b8860b", color=INK))

    render(os.path.join(OUT, "wiring-flash.svg"), W, H, *p,
           title="Підключення модуля й два шляхи прошивки")


if __name__ == "__main__":
    fig_wifi_vs_ble()
    fig_three_classes()
    fig_softdevice_memory()
    fig_module_anatomy()
    fig_wiring_flash()
    print("OK: figures written to", OUT)
