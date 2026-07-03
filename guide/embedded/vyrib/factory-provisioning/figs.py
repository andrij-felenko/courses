# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

BROWN = "#b07a35"
BROWN_FILL = "#fff8e6"


# ── Фігура 1: партія однакових, але порожніх плат → станція наливає три речі ──
def fig_empty_boards():
    W, H = 780, 372
    frags = []
    frags.append(text(W / 2, 30, "Плата зі складання — жива, але порожня й безлика",
                      size=15, bold=True))

    # три однакові порожні плати ліворуч
    bw, bh = 90, 66
    bx0, by0 = 56, 84
    for i in range(3):
        by = by0 + i * (bh + 12)
        frags.append(rect(bx0, by, bw, bh, fill="#eaf4ec", stroke=FIELD, sw=1.6))
        frags.append(text(bx0 + bw / 2, by + bh / 2 - 5, "плата", size=11, color=FIELD))
        frags.append(text(bx0 + bw / 2, by + bh / 2 + 13, "#?", size=13, color=MUTED, bold=True))
    frags.append(text(bx0 + bw / 2, by0 + 3 * (bh + 12) + 4,
                      "усі однакові —", size=10, color=MUTED))
    frags.append(text(bx0 + bw / 2, by0 + 3 * (bh + 12) + 18,
                      "жодна себе не знає", size=10, color=MUTED))

    # станція провізіонування посередині
    sx, sy, sw_, sh = 292, 150, 150, 116
    frags.append(rect(sx, sy, sw_, sh, fill="#eef2f7", stroke=INK, sw=2))
    frags.append(text(sx + sw_ / 2, sy + 26, "СТАНЦІЯ", size=13, bold=True))
    frags.append(text(sx + sw_ / 2, sy + 44, "провізіонування", size=11, color=INK))
    frags.append(text(sx + sw_ / 2, sy + 74, "прошити +", size=10, color=MUTED))
    frags.append(text(sx + sw_ / 2, sy + 90, "записати + звірити", size=10, color=MUTED))
    frags.append(arrow(bx0 + bw + 6, sy + sh / 2, sx - 6, sy + sh / 2, color=INK, sw=2))

    # три речі, які станція наливає в кожну плату (праворуч)
    items = [
        ("прошивка", "спільний образ — на всю партію", POS),
        ("особистість", "серійник, ключі, MAC — унікальні", NEG),
        ("калібрування", "поправки саме цього примірника", FIELD),
    ]
    ix = sx + sw_ + 34
    iw = 262
    for i, (name, sub, col) in enumerate(items):
        iy = 92 + i * 80
        frags.append(rect(ix, iy, iw, 62, fill="#fbfbfb", stroke=col, sw=1.6))
        frags.append(text(ix + 14, iy + 25, name, size=13, color=col, bold=True, anchor="start"))
        frags.append(text(ix + 14, iy + 45, sub, size=10, color=MUTED, anchor="start"))
        frags.append(arrow(sx + sw_ + 4, sy + sh / 2, ix - 6, iy + 31, color=col, sw=1.4))
    render(os.path.join(OUT, 'empty-boards.svg'), W, H, *frags)


# ── Фігура 2: спільний образ на всіх + окремий пер-юніт запис на кожній ───────
def fig_common_vs_perunit():
    W, H = 780, 360
    frags = []
    frags.append(text(W / 2, 30, "Що однакове на всій партії, а що — своє в кожної плати",
                      size=15, bold=True))

    # три плати, у кожної — однаковий блок «образ» і різний блок «запис»
    bw = 200
    x0 = 56
    gap = 24
    ytop = 74
    firm_h = 108
    data_h = 70
    records = ["SN 000041\nMAC …:A3:F2\nключ ▓▓▓▓", "SN 000042\nMAC …:A3:F3\nключ ▒▒▒▒", "SN 000043\nMAC …:A3:F4\nключ ░░░░"]
    for i in range(3):
        x = x0 + i * (bw + gap)
        # спільний образ прошивки — однаковий колір/текст усюди
        frags.append(rect(x, ytop, bw, firm_h, fill="#fdecea", stroke=POS, sw=1.6))
        frags.append(text(x + bw / 2, ytop + 26, "ОБРАЗ ПРОШИВКИ", size=12, color=POS, bold=True))
        frags.append(text(x + bw / 2, ytop + 50, "той самий байт-у-байт", size=10, color=MUTED))
        frags.append(text(x + bw / 2, ytop + 68, "на кожній платі партії", size=10, color=MUTED))
        frags.append(text(x + bw / 2, ytop + 92, "(один .bin на всіх)", size=10, color=POS))
        # пер-юніт запис — різний у кожної
        dy = ytop + firm_h + 16
        frags.append(rect(x, dy, bw, data_h, fill="#eaf0fd", stroke=NEG, sw=1.6))
        frags.append(mtext(x + bw / 2, dy + 22, records[i], size=11, color=NEG))

    # підписи-дужки збоку
    frags.append(text(x0 - 6, ytop + firm_h / 2, "спільне", size=11, color=POS,
                      anchor="end", bold=True))
    frags.append(text(x0 - 6, ytop + firm_h + 16 + data_h / 2, "своє", size=11, color=NEG,
                      anchor="end", bold=True))
    frags.append(fitbox(x0, H - 46, 3 * bw + 2 * gap, 34,
                        "Прошивка однакова; особистість — ні. Тому їх наливають окремо: образ — гуртом, запис — по одному.",
                        size=12, fill="#f4f6f8", stroke=INK, sw=1.4))
    render(os.path.join(OUT, 'common-vs-perunit.svg'), W, H, *frags)


# ── Фігура 3: конвеєр станції — прошити → записати → пропалити → звірити → лог ─
def fig_station_pipeline():
    W, H = 820, 330
    frags = []
    frags.append(text(W / 2, 30, "Станція провізіонування — теж сліпий конвеєр із п'яти кроків",
                      size=15, bold=True))

    stages = [
        ("Прошити", "образ у Flash", POS),
        ("Записати", "серійник, ключі,\nMAC, калібр.", NEG),
        ("Пропалити", "eFuse — назавжди\n(ключ, захист)", BROWN),
        ("Звірити", "прочитати назад,\nсамотест", FIELD),
        ("Записати в базу", "серійник ↔ партія,\nдата, тест", INK),
    ]
    n = len(stages)
    bw, gap = 138, 14
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    ytop = 92
    bh = 58
    # стрічка-конвеєр одразу під блоками; підписи-правила — НИЖЧЕ неї
    belt_y = ytop + bh + 18
    sub_top = belt_y + 22
    frags.append(line(x0 - 8, belt_y, x0 + total + 8, belt_y, color=MUTED, sw=3))
    for i, (name, sub, col) in enumerate(stages):
        x = x0 + i * (bw + gap)
        frags.append(fitbox(x, ytop, bw, bh, name, size=14, bold=True,
                            fill="#eef2f7", stroke=INK, sw=1.6))
        if i < n - 1:
            frags.append(arrow(x + bw + 2, ytop + bh / 2, x + bw + gap - 2, ytop + bh / 2,
                               color=INK, sw=2))
        frags.append(line(x + bw / 2, belt_y + 2, x + bw / 2, sub_top - 2, color=col, sw=1.4, dash="4,4"))
        frags.append(fitbox(x + 3, sub_top, bw - 6, 62, sub, size=10, color=col,
                            fill="#fbfbfb", stroke=col, sw=1.3))
    frags.append(text(W / 2, H - 16,
                      "Проходить усі п'ять — плата готова до відвантаження; спіткнулась на будь-якому — у брак.",
                      size=11, color=MUTED))
    render(os.path.join(OUT, 'station-pipeline.svg'), W, H, *frags)


# ── Фігура 4: карта Flash — чому пер-юніт запис переживає оновлення прошивки ──
def fig_partition_survival():
    W, H = 760, 360
    frags = []
    frags.append(text(W / 2, 30, "Чому особистість кладуть в ОКРЕМИЙ розділ Flash",
                      size=15, bold=True))

    # два стани карти пам'яті: до і після оновлення прошивки
    col_w = 150
    xL, xR = 150, 470
    ytop = 78
    parts = [
        ("завантажувач", "#e8e8e8", INK, 34),
        ("прошивка (додаток)", "#fdecea", POS, 96),
        ("розділ даних\n(SN, ключі, калібр.)", "#eaf0fd", NEG, 70),
    ]
    def draw_map(x, title, app_overwritten):
        out = [text(x + col_w / 2, ytop - 12, title, size=12, bold=True)]
        y = ytop
        for name, fill, stroke, h in parts:
            f = fill
            s = stroke
            if name.startswith("прошивка") and app_overwritten:
                f = "#fff3d6"
                s = BROWN
            out.append(rect(x, y, col_w, h, fill=f, stroke=s, sw=1.7))
            lbl = name
            if name.startswith("прошивка"):
                lbl = ("НОВА прошивка\n(перезаписано)" if app_overwritten else "прошивка\n(додаток)")
            out.append(mtext(x + col_w / 2, y + h / 2 - 4, lbl, size=10,
                             color=(BROWN if (name.startswith("прошивка") and app_overwritten) else stroke)))
            y += h + 6
        return out
    frags += draw_map(xL, "спочатку", False)
    frags += draw_map(xR, "після OTA-оновлення", True)

    # стрілка «оновлення» між картами
    frags.append(arrow(xL + col_w + 18, ytop + 130, xR - 18, ytop + 130, color=INK, sw=2))
    frags.append(text((xL + col_w + xR) / 2, ytop + 118, "оновлення", size=11, color=INK))

    # виноска: що змінилось, а що ні
    frags.append(fitbox(xL, H - 58, col_w * 2 + (xR - xL - col_w), 40,
                        "Оновлення перезаписує лише розділ додатка. Розділ даних воно не чіпає — серійник, ключі й калібрування лишаються на місці.",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.5))
    render(os.path.join(OUT, 'partition-survival.svg'), W, H, *frags)


# ── Фігура 5: побайтова розкладка запису провізіонування в розділі Flash ──────
def fig_record_layout():
    W, H = 880, 388
    f = [text(W / 2, 30, "Запис провізіонування в розділі Flash — поле за полем",
              size=15, bold=True)]

    # поля запису: (назва, розмір-байтів, ширина-в-px, колір)
    fields = [
        ("magic", "4 Б", 96, POS),
        ("version", "2 Б", 74, NEG),
        ("serial", "8 Б", 118, FIELD),
        ("MAC", "6 Б", 104, FIELD),
        ("калібр-\nпоправки", "N Б", 150, "#8e44ad"),
        ("CRC-32", "4 Б", 96, BROWN),
    ]
    x0, ytop, bh = 40, 92, 66
    x = x0
    xs = []
    for name, sz, w, col in fields:
        f.append(rect(x, ytop, w, bh, fill="#fbfbfb", stroke=col, sw=1.8))
        f.append(mtext(x + w / 2, ytop + (24 if "\n" not in name else 20), name,
                       size=12, color=col, bold=True))
        f.append(text(x + w / 2, ytop + bh - 10, sz, size=10, color=MUTED))
        xs.append((x, w))
        x += w
    total = x - x0

    # дужка «CRC накриває все, що ліворуч від неї»
    crc_x = xs[-1][0]
    by = ytop + bh + 26
    f.append(line(x0, by, crc_x, by, color=BROWN, sw=1.6))
    f.append(line(x0, by - 6, x0, by, color=BROWN, sw=1.6))
    f.append(line(crc_x, by - 6, crc_x, by, color=BROWN, sw=1.6))
    f.append(arrow(crc_x, by, crc_x + 44, by, color=BROWN, sw=1.6))
    f.append(text((x0 + crc_x) / 2, by + 16,
                  "CRC-32 рахується з УСІХ цих байтів — і кладеться в кінець",
                  size=11, color=BROWN, bold=True))

    # два «вартові» — magic спереду, CRC ззаду — і що кожен ловить
    gy = by + 44
    f.append(fitbox(x0, gy, total / 2 - 8, 54,
                    "magic ПОПЕРЕДУ ловить\nстерту (0xFF…) чи чужу\nобласть — цих 4 байтів у ній нема",
                    size=10.5, color=POS, fill="#fdecea", stroke=POS, sw=1.3))
    f.append(fitbox(x0 + total / 2 + 8, gy, total / 2 - 8, 54,
                    "CRC ПОЗАДУ ловить\nнапівзаписаний запис —\nсума не збіжиться",
                    size=10.5, color=BROWN, fill="#fff3d6", stroke=BROWN, sw=1.3))
    render(os.path.join(OUT, 'record-layout.svg'), W, H, *f)


# ── Фігура 6: перевірка запису на старті прошивки (магія → CRC → вирок) ────────
def fig_boot_check():
    W, H = 800, 476
    f = [text(W / 2, 30, "Що прошивка робить із записом на старті — щоразу ПЕРЕВІРЯЄ, не вірить",
              size=15, bold=True)]

    bw, bh = 240, 46
    cx = W / 2
    y = 62

    def box(cy, s, col=INK, fill="#eef2f7"):
        f.append(fitbox(cx - bw / 2, cy, bw, bh, s, size=12, bold=True,
                        fill=fill, stroke=col, sw=1.6))

    def down(y1, y2, label=None, col=INK):
        f.append(arrow(cx, y1, cx, y2, color=col, sw=1.8))
        if label:
            f.append(text(cx + 10, (y1 + y2) / 2 + 4, label, size=10,
                          color=col, anchor="start", bold=True))

    # ланцюг перевірок згори вниз
    box(y, "прочитати розділ у RAM"); b1 = y + bh
    y2 = b1 + 34; box(y2, "magic == 0x50524F56 ?", NEG); b2 = y2 + bh
    y3 = b2 + 34; box(y3, "version підтримується ?", NEG); b3 = y3 + bh
    y4 = b3 + 34; box(y4, "CRC-32 збігається ?", BROWN); b4 = y4 + bh
    y5 = b4 + 40; box(y5, "ПРОВІЗІОНОВАНА ✓\nсерійник, MAC, калібр — свої", FIELD, "#eafaf1")

    down(b1, y2)
    down(b2, y3, "так", FIELD)
    down(b3, y4, "так", FIELD)
    down(b4, y5, "так", FIELD)

    # права гілка «ні» → стоп або дефолти
    rx = cx + bw / 2 + 70
    ry = (y2 + b4) / 2
    f.append(fitbox(rx - 78, ry - 30, 156, 60,
                    "будь-яке «ні» →\nЗАПИС НЕДІЙСНИЙ",
                    size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.6))
    for yy in (y2 + bh / 2, y3 + bh / 2, y4 + bh / 2):
        f.append(line(cx + bw / 2, yy, rx - 78, ry, color=POS, sw=1.2, dash="4,3"))
    f.append(text(cx + bw / 2 + 16, y2 + bh / 2 - 6, "ні", size=10, color=POS, bold=True))

    # з «недійсно» — дві можливі політики
    py = ry + 60
    f.append(arrow(rx, ry + 30, rx, py, color=POS, sw=1.6))
    f.append(fitbox(rx - 150, py, 140, 48,
                    "СТОП + сигнал:\n«не провізіонована»",
                    size=10.5, bold=True, color=INK, fill="#f4f6f8", stroke=INK, sw=1.4))
    f.append(fitbox(rx + 14, py, 140, 48,
                    "або безпечні\nДЕФОЛТИ (де можна)",
                    size=10.5, bold=True, color=MUTED, fill="#fbfbfb", stroke=MUTED, sw=1.4))
    f.append(line(rx, py, rx - 80, py, color=POS, sw=1.4))
    f.append(line(rx, py, rx + 84, py, color=POS, sw=1.4))

    render(os.path.join(OUT, 'boot-check.svg'), W, H, *f)


if __name__ == '__main__':
    fig_empty_boards()
    fig_common_vs_perunit()
    fig_station_pipeline()
    fig_partition_survival()
    fig_record_layout()
    fig_boot_check()
    print("ok")
