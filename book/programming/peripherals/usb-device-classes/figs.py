# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── class-driver-match: код класу в дескрипторі → готовий драйвер ОС ───────────
# Ідея: пристрій кладе один байт-код у дескриптор; хост за цим кодом дістає вже
# вбудований драйвер — без диска, без встановлення. Показано три класи поруч.

def fig_class_driver():
    W, H = 720, 300
    p = []
    # ліворуч — пристрій із дескриптором, праворуч — ОС із полицею драйверів
    dev = fitbox(40, 110, 150, 90, "пристрій\nдескриптор:\nbInterfaceClass", size=12,
                 fill=FILL, stroke=INK, sw=1.6, bold=True)
    p.append(dev)
    os_box = fitbox(530, 90, 150, 130, "ОС\nвбудовані\nдрайвери класів", size=12,
                    fill="#eef4ff", stroke=NEG, sw=1.6, bold=True)
    p.append(os_box)

    rows = [
        ("0x03  HID",  "клавіатура / миша", FIELD),
        ("0x02  CDC",  "віртуальний COM",   NEG),
        ("0x08  MSC",  "знімний диск",      POS),
    ]
    y = 95
    for code, drv, col in rows:
        p.append(text(210, y, code, size=12, color=col, anchor="start", bold=True))
        p.append(arrow(330, y - 4, 522, y - 4, color=col, sw=1.7))
        p.append(text(335, y - 10, drv, size=10, color=MUTED, anchor="start"))
        y += 50

    p.append(text(W / 2, H - 26,
                  "хост читає код під час енумерації → бере готовий драйвер, диск не потрібен",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "class-driver-match.svg"), W, H, *p,
           title="Код класу в дескрипторі обирає вбудований драйвер ОС")


# ── three-classes: CDC / HID / MSC — кінцеві точки, дані, вигляд в ОС ──────────
# Ідея: три стовпці-картки. Кожен клас = свій набір кінцевих точок + свій тип
# трафіку + те, як його бачить ОС. Видно, що клас диктує всю «трубу» цілком.

def fig_three_classes():
    W, H = 740, 340
    p = []
    cols = [
        ("HID", FIELD, "interrupt-IN\n(+ опц. OUT)",
         "короткі звіти\nкожні N мс", "клавіатура,\nмиша, геймпад"),
        ("CDC", NEG, "bulk-IN + bulk-OUT\n+ interrupt-IN",
         "потік байтів\nдовільної довжини", "COM-порт\n/dev/ttyACM"),
        ("MSC", POS, "bulk-IN + bulk-OUT",
         "блоки по 512 Б\n(команди SCSI)", "знімний диск\nз файловою ФС"),
    ]
    cw, gap = 210, 24
    x0 = (W - (cw * 3 + gap * 2)) / 2
    top = 56
    for i, (name, col, eps, data, view) in enumerate(cols):
        x = x0 + i * (cw + gap)
        p.append(rect(x, top, cw, 250, fill="#ffffff", stroke=col, sw=2.0, rx=10))
        p.append(text(x + cw / 2, top + 30, name, size=18, color=col, bold=True))
        p.append(line(x + 16, top + 44, x + cw - 16, top + 44, color=col, sw=1.2))
        # три рядки-характеристики
        labels = [("кінцеві точки", eps), ("трафік", data), ("в ОС видно як", view)]
        yy = top + 72
        for cap, val in labels:
            p.append(text(x + cw / 2, yy, cap, size=10, color=MUTED))
            p.append(mtext(x + cw / 2, yy + 18, val, size=11, color=INK, bold=True))
            yy += 62
    p.append(text(W / 2, H - 16,
                  "клас задає всю трубу: набір кінцевих точок, формат трафіку й вигляд у системі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "three-classes.svg"), W, H, *p,
           title="Три класи для мікроконтролера: CDC, HID, MSC")


# ── composite: один роз'єм → кілька інтерфейсів через IAD ──────────────────────
# Ідея: один фізичний кабель/роз'єм несе кілька логічних інтерфейсів; ОС вантажить
# окремий драйвер на кожен. IAD «склеює» інтерфейси CDC у одну функцію.

def fig_composite():
    W, H = 720, 340
    p = []
    # роз'єм ліворуч
    p.append(fitbox(40, 150, 92, 56, "один\nроз'єм", size=12, fill=FILL, stroke=INK, sw=1.8, bold=True))
    # «коробка» пристрою
    p.append(rect(170, 60, 230, 240, fill="#fbfbfd", stroke=INK, sw=1.6, rx=10))
    p.append(text(285, 84, "композитний пристрій", size=12, color=MUTED, bold=True))

    # IAD-група CDC (інтерфейси 0+1)
    p.append(rect(186, 100, 198, 96, fill="#eef4ff", stroke=NEG, sw=1.6, rx=8))
    p.append(text(285, 118, "IAD: функція CDC", size=11, color=NEG, bold=True))
    p.append(fitbox(196, 128, 86, 54, "Interface 0\nCDC Control", size=10, fill="#ffffff", stroke=NEG, sw=1.2, bold=False))
    p.append(fitbox(290, 128, 86, 54, "Interface 1\nCDC Data", size=10, fill="#ffffff", stroke=NEG, sw=1.2, bold=False))

    # HID-інтерфейс 2
    p.append(fitbox(196, 214, 180, 54, "Interface 2 — HID\n(макро-пад)", size=11, fill="#eafaf0", stroke=FIELD, sw=1.6, bold=True))

    # кабель від роз'єму до коробки
    p.append(arrow(132, 178, 168, 150, color=INK, sw=1.7))

    # ОС праворуч: два драйвери
    p.append(rect(470, 90, 210, 180, fill="#ffffff", stroke=INK, sw=1.6, rx=10))
    p.append(text(575, 114, "ОС вантажить два драйвери", size=11, color=MUTED, bold=True))
    p.append(arrow(404, 148, 466, 138, color=NEG, sw=1.7))
    p.append(fitbox(486, 130, 178, 44, "драйвер CDC → COM-порт", size=11, fill="#eef4ff", stroke=NEG, sw=1.4, bold=True))
    p.append(arrow(384, 241, 466, 212, color=FIELD, sw=1.7))
    p.append(fitbox(486, 196, 178, 44, "драйвер HID → клавіатура", size=11, fill="#eafaf0", stroke=FIELD, sw=1.4, bold=True))

    p.append(text(W / 2, H - 14,
                  "один кабель — кілька функцій; IAD каже ОС, які інтерфейси склеїти в одну",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "composite.svg"), W, H, *p,
           title="Композитний пристрій: CDC + HID в одному роз'ємі")


# ── class-code-location: де саме лежить код класу ─────────────────────────────
# Ідея: дерево дескрипторів; код класу або на рівні Device (рідко, одна функція),
# або на рівні кожного Interface (звично, і завжди для композита).

def fig_class_location():
    W, H = 700, 320
    p = []
    # Device descriptor зверху
    dd, dw, dh = textbox(W / 2, 64, "Device Descriptor\nbDeviceClass = 0x00 (або 0xEF для композита)",
                         size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(dd)
    p.append(text(W / 2, 64 + dh / 2 + 16, "клас тут — лише коли весь пристрій = одна функція", size=10, color=MUTED))

    # Configuration
    cfg, cw, ch = textbox(W / 2, 150, "Configuration Descriptor", size=11, bold=True,
                          fill="#ffffff", stroke=MUTED, sw=1.4, pad=10)
    p.append(cfg)
    p.append(line(W / 2, 64 + dh / 2, W / 2, 150 - ch / 2, color=INK, sw=1.4))

    # три інтерфейси з кодом класу
    ix = [180, 350, 520]
    labels = ["Interface 0\nbInterfaceClass\n= 0x02 CDC",
              "Interface 1\nbInterfaceClass\n= 0x0A CDC-Data",
              "Interface 2\nbInterfaceClass\n= 0x03 HID"]
    cols = [NEG, NEG, FIELD]
    for x, lab, col in zip(ix, labels, cols):
        p.append(line(W / 2, 150 + ch / 2, x, 232, color=col, sw=1.4))
        p.append(fitbox(x - 80, 232, 160, 64, lab, size=11, fill="#ffffff", stroke=col, sw=1.6, bold=True))
    p.append(text(W / 2, H - 12, "звично код класу живе на кожному інтерфейсі; для композита — завжди там",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "class-code-location.svg"), W, H, *p,
           title="Де оголошений клас: Device чи кожен Interface")


# ── report-layout: 8 байтів boot keyboard report (proj-вставка) ────────────────

def fig_report_layout():
    W, H = 720, 250
    p = []
    bx, by = 50, 110
    cellw, cellh = 76, 60
    cells = [
        ("byte 0", "modifier\n(біт-маска)", "#eafaf0"),
        ("byte 1", "reserved\n0x00", "#efefef"),
        ("byte 2", "key[0]", "#eef4ff"),
        ("byte 3", "key[1]", "#eef4ff"),
        ("byte 4", "key[2]", "#eef4ff"),
        ("byte 5", "key[3]", "#eef4ff"),
        ("byte 6", "key[4]", "#eef4ff"),
        ("byte 7", "key[5]", "#eef4ff"),
    ]
    x = bx
    for idx, body, fill in cells:
        p.append(rect(x, by, cellw, cellh, fill=fill, stroke=INK, sw=1.5, rx=4))
        p.append(text(x + cellw / 2, by - 8, idx, size=10, color=MUTED))
        p.append(mtext(x + cellw / 2, by + cellh / 2 - 4, body, size=10, color=INK, bold=True))
        x += cellw

    # фігурна дужка під шістьма слотами
    p.append(text(bx + cellw * 2 + cellw * 3, by + cellh + 26,
                  "до 6 одночасних usage ID (page 0x07)", size=11, color=NEG))
    p.append(line(bx + cellw * 2, by + cellh + 8, x, by + cellh + 8, color=NEG, sw=1.4))

    # приклад Win+R
    p.append(text(W / 2, by + cellh + 64,
                  "Win+R = {modifier 0x08 (LGUI), key[0]=0x15 'R', решта 0}, слідом — вісім нулів",
                  size=11, color=INK))
    p.append(text(W / 2, H - 16, "натиск = заповнені поля; відпускання = весь звіт у нулях",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "report-layout.svg"), W, H, *p,
           title="8 байтів boot keyboard report")


# ── press-flow: один натиск у часі по interrupt-IN (proj-вставка) ──────────────

def fig_press_flow():
    W, H = 720, 250
    p = []
    ox, oy = 70, 170
    aw = 580
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час", size=12, color=INK, italic=True))

    # такти опитування хоста (interrupt-IN, кожні bInterval)
    n = 9
    dt = aw / (n + 1)
    for i in range(n):
        x = ox + (i + 1) * dt
        p.append(line(x, oy - 6, x, oy + 6, color=MUTED, sw=1.2))
    p.append(text(ox + dt * 1.5, oy + 34, "опитування хоста кожні bInterval (напр. 1 мс)",
                  size=10, color=MUTED, anchor="start"))

    # два звіти: стан і порожній
    x1 = ox + dt * 3
    x2 = ox + dt * 5
    p.append(rect(x1 - 34, oy - 80, 68, 44, fill="#eef4ff", stroke=NEG, sw=1.6, rx=6))
    p.append(mtext(x1, oy - 80 + 26, "звіт-стан\nkey=0x15", size=10, color=NEG, bold=True))
    p.append(arrow(x1, oy - 34, x1, oy - 4, color=NEG, sw=1.6))

    p.append(rect(x2 - 34, oy - 80, 68, 44, fill="#efefef", stroke=INK, sw=1.6, rx=6))
    p.append(mtext(x2, oy - 80 + 26, "порожній\n0x00×8", size=10, color=INK, bold=True))
    p.append(arrow(x2, oy - 34, x2, oy - 4, color=INK, sw=1.6))

    p.append(text(W / 2, H - 14, "темп задає опитування хоста, а не код пристрою; без порожнього звіту — авторепіт",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "press-flow.svg"), W, H, *p,
           title="Один натиск у часі: стан і порожній звіт по interrupt-IN")


# ── ducky-chain: ланцюг атаки Rubber Ducky (hist-вставка) ──────────────────────

def fig_ducky_chain():
    W, H = 740, 220
    p = []
    y = 100
    bw, bh = 150, 64
    step = 178
    x = 24
    boxes = [
        ("вигляд флешки\n(USB-A корпус)", FILL, INK),
        ("енумерація:\nкаже «я HID»", "#fdecea", POS),
        ("потік натискань\nза сценарієм", "#eef4ff", NEG),
        ("виконана\nкоманда", "#eafaf0", FIELD),
    ]
    centers = []
    for i, (lab, fill, col) in enumerate(boxes):
        p.append(fitbox(x, y - bh / 2, bw, bh, lab, size=11, fill=fill, stroke=col, sw=1.8, bold=True, color=col))
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1], y, x - 2, y, color=INK, sw=1.8))
        x += step
    p.append(text(W / 2, H - 18,
                  "хост не відрізняє цей потік від живих пальців — менше двох секунд до консолі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "ducky-chain.svg"), W, H, *p,
           title="Ланцюг атаки Rubber Ducky")


# ── badusb-layers: двошаровий розріз флешки (hist-вставка) ─────────────────────

def fig_badusb_layers():
    W, H = 700, 300
    p = []
    cx = W / 2
    # верхній шар — видимий MSC-диск
    p.append(rect(120, 60, 460, 80, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(cx, 92, "видимий шар: MSC-диск", size=13, color=FIELD, bold=True))
    p.append(text(cx, 116, "антивірус сканує · форматування стирає файлову систему", size=10, color=MUTED))

    # нижній шар — прихований контролер
    p.append(rect(120, 170, 460, 90, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    p.append(text(cx, 200, "прихований шар: прошивка контролера", size=13, color=POS, bold=True))
    p.append(mtext(cx, 222, ["перепрошита → оголошує ДОДАТКОВИЙ HID-інтерфейс",
                             "форматування не чіпає · антивірус не бачить"], size=10, color=MUTED))

    p.append(text(cx, H - 12,
                  "вада в архітектурі USB: пристрій сам каже, хто він, і це нічим не перевіряється",
                  size=11, color=INK, italic=True))
    render(os.path.join(OUT, "badusb-layers.svg"), W, H, *p,
           title="Чому BadUSB страшніший за вірус-файл")


if __name__ == "__main__":
    fig_class_driver()
    fig_three_classes()
    fig_composite()
    fig_class_location()
    fig_report_layout()
    fig_press_flow()
    fig_ducky_chain()
    fig_badusb_layers()
    print("OK: figures written to", OUT)
