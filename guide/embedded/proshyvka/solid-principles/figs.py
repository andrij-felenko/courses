# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# локальні відтінки під єдину палітру svgkit
AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"


# ── srp-axes: одна причина змінитися ─────────────────────────────────────────
# Ідея: модуль, який тягнуть за різні мотузки різні «замовники змін» (протокол
# давача, формат логу, формат пакета по радіо), має кілька причин змінитися —
# правка для одного ламає інших. SRP: розрізати по осях змін, щоб у кожного
# шматка лишилася рівно одна причина переписувати його.

def fig_srp_axes():
    W, H = 820, 410
    p = []
    # ЛІВОРУЧ — один модуль, три мотузки
    lx, lcw = 60, 300
    p.append(text(lx + lcw / 2, 60, "один модуль — три причини", size=13, color=POS, bold=True))
    mx, my, mw, mh = lx + lcw / 2 - 85, 210, 170, 70
    p.append(rect(mx, my, mw, mh, fill=REDBG, stroke=POS, sw=2, rx=10))
    p.append(text(lx + lcw / 2, my + 30, "sensor_task()", size=12, color=POS, bold=True))
    p.append(text(lx + lcw / 2, my + 50, "читає + логує + шле", size=9.5, color=INK))
    pulls = [
        (lx + 20,  92, "змінився протокол давача"),
        (lx + lcw - 20, 92, "змінився формат логу"),
        (lx + lcw / 2, 110, "змінився пакет по радіо"),
    ]
    anchors = [(mx + 18, my), (mx + mw - 18, my), (mx + mw / 2, my)]
    al = ["start", "end", "middle"]
    for (tx, ty, lbl), (ax, ay), an in zip(pulls, anchors, al):
        p.append(circle(tx, ty, 7, fill=AMBERBG, stroke=AMBER, sw=1.6))
        p.append(text(tx, ty - 12, lbl, size=9, color=MUTED, anchor=an))
        p.append(arrow(tx, ty + 7, ax, ay, color=AMBER, sw=1.8))
    p.append(text(lx + lcw / 2, my + mh + 34, "правка для одного", size=10, color=POS, bold=True))
    p.append(text(lx + lcw / 2, my + mh + 50, "ризикує зламати інших", size=10, color=POS))

    # роздільник
    p.append(line(W / 2, 50, W / 2, H - 50, color="#cccccc", sw=1.2, dash="4 4"))

    # ПРАВОРУЧ — три шматки, по одній причині
    rx0, rcw = W / 2 + 30, 300
    p.append(text(rx0 + rcw / 2, 60, "три шматки — по одній", size=13, color=FIELD, bold=True))
    parts = [
        ("sensor_read()", "протокол давача", BLUEBG, NEG),
        ("log_format()",  "формат логу",     GREENBG, FIELD),
        ("radio_pack()",  "пакет по радіо",  AMBERBG, AMBER),
    ]
    pw, ph = 220, 56
    px = rx0 + rcw / 2 - pw / 2
    for i, (name, why, fill, col) in enumerate(parts):
        py = 96 + i * 78
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(px, py, pw, ph, fill=fill, stroke=col, sw=1.8, rx=9))
        p.append(text(rx0 + rcw / 2, py + 24, name, size=11.5, color=tagcol, bold=True))
        p.append(text(rx0 + rcw / 2, py + 43, "причина: " + why, size=9.5, color=INK))
    p.append(text(rx0 + rcw / 2, 96 + 3 * 78 + 6, "правка не виходить за свій шматок", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, H - 14,
                  "«одна причина змінитися» = один замовник змін на модуль",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "srp-axes.svg"), W, H, *p,
           title="SRP: один модуль — одна причина переписувати його")


# ── dip-inversion: стрілка залежності перевертається ─────────────────────────
# Ідея: наївно високорівнева політика (керування) залежить прямо від конкретного
# драйвера — стрілка вниз, до заліза. DIP: між ними вставляють інтерфейс, і ТЕПЕР
# обидва — і політика, і драйвер — залежать від інтерфейсу (стрілка від драйвера
# йде ВГОРУ). Залежність на конкретику перевернулась на залежність від абстракції.

def fig_dip_inversion():
    W, H = 820, 400
    p = []
    bw, bh = 230, 64

    # ЛІВОРУЧ — наївно: політика → конкретний драйвер
    lx = 70
    p.append(text(lx + bw / 2, 56, "наївно: залежність вниз", size=13, color=POS, bold=True))
    p.append(rect(lx, 88, bw, bh, fill=GREENBG, stroke=FIELD, sw=2, rx=10))
    p.append(text(lx + bw / 2, 114, "control_loop()", size=12, color=FIELD, bold=True))
    p.append(text(lx + bw / 2, 132, "високорівнева політика", size=9.3, color=MUTED))
    p.append(rect(lx, 250, bw, bh, fill=BLUEBG, stroke=NEG, sw=2, rx=10))
    p.append(text(lx + bw / 2, 276, "bme280_i2c.c", size=12, color=NEG, bold=True))
    p.append(text(lx + bw / 2, 294, "конкретний драйвер", size=9.3, color=MUTED))
    p.append(arrow(lx + bw / 2, 152, lx + bw / 2, 250, color=POS, sw=2.4))
    p.append(text(lx + bw / 2 + 12, 205, "знає тип давача", size=9.5, color=POS, anchor="start"))
    p.append(text(lx + bw / 2, 332, "зміниш давач — переписуй політику", size=9.6, color=POS, bold=True))

    # роздільник
    p.append(line(W / 2, 46, W / 2, H - 44, color="#cccccc", sw=1.2, dash="4 4"))

    # ПРАВОРУЧ — DIP: обидва залежать від інтерфейсу
    rx0 = W / 2 + 50
    p.append(text(rx0 + bw / 2, 56, "DIP: обидва → інтерфейс", size=13, color=FIELD, bold=True))
    p.append(rect(rx0, 88, bw, bh, fill=GREENBG, stroke=FIELD, sw=2, rx=10))
    p.append(text(rx0 + bw / 2, 114, "control_loop()", size=12, color=FIELD, bold=True))
    p.append(text(rx0 + bw / 2, 132, "високорівнева політика", size=9.3, color=MUTED))
    # інтерфейс посередині
    iw = bw + 16
    p.append(rect(rx0 - 8, 178, iw, 44, fill=AMBERBG, stroke=AMBER, sw=2, rx=8))
    p.append(text(rx0 + bw / 2, 200, "interface  baro_t", size=11.5, color=AMBERTX, bold=True))
    p.append(text(rx0 + bw / 2, 216, "read_pressure()", size=9.2, color=INK))
    p.append(rect(rx0, 268, bw, bh, fill=BLUEBG, stroke=NEG, sw=2, rx=10))
    p.append(text(rx0 + bw / 2, 294, "bme280_i2c.c", size=12, color=NEG, bold=True))
    p.append(text(rx0 + bw / 2, 312, "реалізує baro_t", size=9.3, color=MUTED))
    p.append(arrow(rx0 + bw / 2, 152, rx0 + bw / 2, 178, color=FIELD, sw=2.4))   # політика → інтерфейс (вниз)
    p.append(arrow(rx0 + bw / 2, 268, rx0 + bw / 2, 222, color=NEG, sw=2.4))     # драйвер → інтерфейс (ВГОРУ)
    p.append(text(rx0 + bw / 2 + 14, 248, "стрілка перевернулась", size=9.3, color=NEG, anchor="start"))
    p.append(text(rx0 + bw / 2, 350, "зміниш давач — політики не торкаєшся", size=9.6, color=FIELD, bold=True))

    p.append(text(W / 2, H - 12,
                  "обидва спираються на абстракцію — деталь залежить від політики, не навпаки",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "dip-inversion.svg"), W, H, *p,
           title="DIP: інверсія — хто від кого залежить")


# ── solid-map: п'ять літер на мову прошивки ──────────────────────────────────
# Ідея: зібрати всі п'ять принципів в одну карту — літера, гасло, що це означає
# саме у вбудованому C/C++. Не теорія заради теорії, а п'ять різних відповідей на
# одне питання: як стримати зростання зчеплення, щоб правка не їхала по всьому коду.

def fig_solid_map():
    W, H = 820, 430
    p = []
    rows = [
        ("S", "одна причина змінитися",
         "модуль робить одне; читання давача, лог і пакет — нарізно", FIELD, GREENBG),
        ("O", "відкрите на розширення",
         "новий давач = новий .c під інтерфейс, старий код не чіпаєш", NEG, BLUEBG),
        ("L", "підтип чесно заміняє предка",
         "будь-яка реалізація драйвера працює там, де чекають інтерфейс", AMBER, AMBERBG),
        ("I", "вузькі інтерфейси",
         "клієнт залежить лише від методів, які справді кличе", POS, REDBG),
        ("D", "залежність від абстракції",
         "політика й драйвер дивляться на інтерфейс, не один на одного", NEG, BLUEBG),
    ]
    top, rh, gap = 78, 62, 10
    lx, rw = 40, 740
    for i, (letter, motto, what, col, fill) in enumerate(rows):
        y = top + i * (rh + gap)
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(lx, y, rw, rh, fill=fill, stroke=col, sw=1.7, rx=10))
        # велика літера в кружку
        p.append(circle(lx + 38, y + rh / 2, 22, fill=BG, stroke=col, sw=2.2))
        p.append(text(lx + 38, y + rh / 2 + 9, letter, size=24, color=tagcol, bold=True))
        p.append(text(lx + 78, y + 26, motto, size=12.5, color=tagcol, anchor="start", bold=True))
        p.append(text(lx + 78, y + 46, what, size=10, color=INK, anchor="start"))

    p.append(text(W / 2, H - 14,
                  "п'ять відповідей на одне питання: як стримати зчеплення, щоб правка не їхала по всьому коду",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "solid-map.svg"), W, H, *p,
           title="SOLID мовою прошивки")


# ── vtable-layout: рукотворна таблиця методів за непрозорим вказівником ───────
# Ідея (вставка proj-c-interfaces): політика бачить ЛИШЕ baro_t + таблицю методів
# (read/close). Виклик baro->vt->read(...) потрапляє в ту реалізацію, чий рядок
# таблиці підставлено: I2C-драйвер, SPI-драйвер чи мок. Прихований стан кожної
# (дескриптор шини, адреса, сценарій тесту) живе у власному .c і політиці недоступний.

def fig_vtable_layout():
    W, H = 820, 470
    p = []

    # ВЕРХ — політика, бачить лише абстракцію
    polw, polh = 300, 58
    polx = W / 2 - polw / 2
    p.append(rect(polx, 54, polw, polh, fill=GREENBG, stroke=FIELD, sw=2, rx=10))
    p.append(text(W / 2, 78, "політика  altitude_step()", size=13, color=FIELD, bold=True))
    p.append(text(W / 2, 96, "кличе baro->vt->read(...) — не знає, чий", size=9.3, color=INK))

    # СЕРЕДИНА — baro_t + таблиця методів (абстракція)
    vtx, vty, vtw, vth = W / 2 - 130, 150, 260, 70
    p.append(rect(vtx, vty, vtw, vth, fill=AMBERBG, stroke=AMBER, sw=2, rx=9))
    p.append(text(W / 2, vty + 22, "baro_t  →  vtable", size=12, color=AMBERTX, bold=True))
    p.append(text(W / 2, vty + 41, "read(self, *out_pa)", size=9.5, color=INK))
    p.append(text(W / 2, vty + 57, "close(self)", size=9.5, color=INK))
    p.append(arrow(W / 2, 112, W / 2, vty, color=FIELD, sw=2.2))   # політика → абстракція

    # НИЗ — три реалізації, кожна кладе у таблицю свої функції; стрілки ВГОРУ
    impls = [
        ("bme280_i2c.c", "addr 0x76", "i2c_read", BLUEBG, NEG),
        ("bme280_spi.c", "cs_pin 17", "spi_read", BLUEBG, NEG),
        ("baro_mock.c",  "сценарій",  "mock_read", REDBG, POS),
    ]
    iw, ih = 218, 74
    gap = (W - 3 * iw) / 4
    ytop = 330
    for i, (name, state, fn, fill, col) in enumerate(impls):
        x = gap + i * (iw + gap)
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, ytop, iw, ih, fill=fill, stroke=col, sw=1.8, rx=9))
        p.append(text(x + iw / 2, ytop + 22, name, size=11.5, color=tagcol, bold=True))
        p.append(text(x + iw / 2, ytop + 41, "vt.read = " + fn, size=9.3, color=INK))
        p.append(text(x + iw / 2, ytop + 59, "прихований стан: " + state, size=8.8, color=MUTED))
        # стрілка ВГОРУ — реалізація заповнює абстракцію (DIP: деталь → абстракція)
        p.append(arrow(x + iw / 2, ytop, W / 2 + (i - 1) * 70, vty + vth, color=col, sw=2.0))

    p.append(text(W / 2, H - 14,
                  "одна таблиця методів, три реалізації — політика бачить лише абстракцію",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "vtable-layout.svg"), W, H, *p,
           title="vtable за непрозорим вказівником: хто що бачить")


# ── ocp-two-versions: дві історичні версії OCP ───────────────────────────────
# Ідея (вставка hist-solid-origin): та сама назва Open-Closed несе два різні
# механізми. Меєр (1988) — розширення через УСПАДКУВАННЯ готового класу (нащадок
# бере код предка). Мартін (1996) — через АБСТРАКТНИЙ ІНТЕРФЕЙС і нові реалізації
# збоку. Назва перейшла, серцевина за вісім років змінилася.

def fig_ocp_two_versions():
    W, H = 840, 430
    p = []
    bw, bh = 210, 56

    # ЛІВОРУЧ — Меєр 1988: успадкування реалізації
    lx = 60
    p.append(text(lx + bw / 2, 58, "Меєр, 1988", size=14, color=NEG, bold=True))
    p.append(text(lx + bw / 2, 76, "через успадкування", size=10, color=MUTED))
    p.append(rect(lx, 100, bw, bh, fill=GREENBG, stroke=FIELD, sw=2, rx=10))
    p.append(text(lx + bw / 2, 124, "старий клас", size=11.5, color=FIELD, bold=True))
    p.append(text(lx + bw / 2, 142, "закритий, готовий", size=9.3, color=MUTED))
    p.append(rect(lx, 268, bw, bh, fill=BLUEBG, stroke=NEG, sw=2, rx=10))
    p.append(text(lx + bw / 2, 292, "нащадок", size=11.5, color=NEG, bold=True))
    p.append(text(lx + bw / 2, 310, "успадковує код предка", size=9.3, color=MUTED))
    p.append(arrow(lx + bw / 2, 268, lx + bw / 2, 158, color=NEG, sw=2.2))   # нащадок → предок (вгору)
    p.append(text(lx + bw / 2 + 12, 215, "бере реалізацію", size=9.3, color=INK, anchor="start"))
    p.append(text(lx + bw / 2, 348, "розширюєш, успадковуючи", size=9.6, color=NEG, bold=True))
    p.append(text(lx + bw / 2, 364, "готовий клас", size=9.6, color=NEG, bold=True))

    # роздільник
    p.append(line(W / 2, 50, W / 2, H - 44, color="#cccccc", sw=1.2, dash="4 4"))

    # ПРАВОРУЧ — Мартін 1996: абстрактний інтерфейс + реалізації збоку
    rx0 = W / 2 + 50
    p.append(text(rx0 + bw / 2, 58, "Мартін, 1996", size=14, color=FIELD, bold=True))
    p.append(text(rx0 + bw / 2, 76, "через абстракцію", size=10, color=MUTED))
    iw = bw + 10
    p.append(rect(rx0 - 5, 100, iw, bh, fill=AMBERBG, stroke=AMBER, sw=2, rx=10))
    p.append(text(rx0 + bw / 2, 124, "інтерфейс", size=11.5, color=AMBERTX, bold=True))
    p.append(text(rx0 + bw / 2, 142, "закритий на зміну", size=9.3, color=MUTED))
    rw2 = 96
    p.append(rect(rx0 - 5, 268, rw2, bh, fill=BLUEBG, stroke=NEG, sw=1.8, rx=9))
    p.append(text(rx0 - 5 + rw2 / 2, 292, "реал. A", size=10.5, color=NEG, bold=True))
    p.append(text(rx0 - 5 + rw2 / 2, 309, "старий .c", size=8.8, color=MUTED))
    p.append(rect(rx0 + bw - rw2 + 5, 268, rw2, bh, fill=REDBG, stroke=POS, sw=1.8, rx=9))
    p.append(text(rx0 + bw - rw2 / 2 + 5, 292, "реал. B", size=10.5, color=POS, bold=True))
    p.append(text(rx0 + bw - rw2 / 2 + 5, 309, "новий .c", size=8.8, color=MUTED))
    p.append(arrow(rx0 - 5 + rw2 / 2, 268, rx0 + bw / 2 - 28, 158, color=NEG, sw=2.0))
    p.append(arrow(rx0 + bw - rw2 / 2 + 5, 268, rx0 + bw / 2 + 28, 158, color=POS, sw=2.0))
    p.append(text(rx0 + bw / 2, 348, "розширюєш, додаючи", size=9.6, color=FIELD, bold=True))
    p.append(text(rx0 + bw / 2, 364, "нову реалізацію збоку", size=9.6, color=FIELD, bold=True))

    p.append(text(W / 2, H - 12,
                  "одна назва «open-closed» — два механізми: успадкування проти поліморфізму",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "ocp-two-versions.svg"), W, H, *p,
           title="«O»: від успадкування Меєра до абстракцій Мартіна")


# ── solid-origin: дві осі однієї збірки ──────────────────────────────────────
# Ідея (вставка hist-solid-origin): SOLID — збірка, а не монолит. Угорі — хто що
# зробив (Меєр, Лісков-Вінг, Мартін). Унизу — внесок Фезерса: він переставив
# наявні принципи так, щоб початкові літери склали слово SOLID (мнемоніка, не логіка).

def fig_solid_origin():
    W, H = 840, 470
    p = []

    p.append(text(W / 2, 56, "хто що зробив", size=14, color=INK, bold=True))
    origins = [
        ("O", "Меєр 1988 → переосмислив Мартін 1996", AMBER, AMBERBG),
        ("L", "Лісков 1987 + Вінг 1994 → інтегрував Мартін", NEG, BLUEBG),
        ("SID", "формулювання Мартіна (1996, зведення 2000)", FIELD, GREENBG),
    ]
    top, rh, gap = 76, 50, 12
    lx, rw = 70, W - 140
    for i, (who, what, col, fill) in enumerate(origins):
        y = top + i * (rh + gap)
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(lx, y, rw, rh, fill=fill, stroke=col, sw=1.7, rx=10))
        p.append(circle(lx + 52, y + rh / 2, 21, fill=BG, stroke=col, sw=2.2))
        lab = "S·I·D" if who == "SID" else who
        p.append(text(lx + 52, y + rh / 2 + (5 if who == "SID" else 7),
                      lab, size=14 if who == "SID" else 22, color=tagcol, bold=True))
        p.append(text(lx + 92, y + rh / 2 + 5, what, size=11, color=INK, anchor="start"))

    midy = top + 3 * (rh + gap) + 8
    p.append(text(W / 2, midy + 14, "Фезерс (≈2004): переставив літери в слово", size=12,
                  color=POS, bold=True))
    p.append(arrow(W / 2, midy + 22, W / 2, midy + 44, color=POS, sw=2.2))

    by = midy + 64
    letters = [("S", FIELD), ("O", AMBER), ("L", NEG), ("I", FIELD), ("D", NEG)]
    cw = 86
    startx = W / 2 - (len(letters) * cw) / 2 + cw / 2
    full = {"S": "Single", "O": "Open-closed", "L": "Liskov", "I": "Interface", "D": "Dependency"}
    for i, (ch, col) in enumerate(letters):
        cx = startx + i * cw
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(cx - 36, by, 72, 72, fill=BG, stroke=col, sw=2.2, rx=10))
        p.append(text(cx, by + 46, ch, size=34, color=tagcol, bold=True))
        p.append(text(cx, by + 92, full[ch], size=9, color=MUTED))
    p.append(text(W / 2, by + 116, "порядок мнемонічний, а не логічний",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "solid-origin.svg"), W, H, *p,
           title="SOLID — збірка: походження й акронім")


if __name__ == "__main__":
    fig_srp_axes()
    fig_dip_inversion()
    fig_solid_map()
    fig_vtable_layout()
    fig_ocp_two_versions()
    fig_solid_origin()
    print("OK: figures written to", OUT)
