# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── layers: три шари з швом diskio ────────────────────────────────────────────
# Ідея: застосунок (мова файлів) → FatFs (знає лише формат FAT) → diskio (ваш код,
# мова секторів) → залізо. Шов diskio підписаний явно — саме він міняється під чип.

def fig_layers():
    W, H = 720, 380
    p = []
    cx = W / 2
    bw = 460
    x = cx - bw / 2

    rows = [
        ("Ваш застосунок", "f_open · f_write · f_read · f_close", "#eafaf0", FIELD, "мова файлів"),
        ("FatFs — модуль FAT", "знає лише формат FAT; про залізо — нічого", "#f6f4ec", INK, "мова секторів"),
        ("Ваш diskio (шов)", "disk_read · disk_write · disk_ioctl · get_fattime", "#eef4ff", NEG, "переклад: сектор → команда носія"),
        ("Залізо: SD по SPI / NOR-Flash / SDIO", "фізичні блоки на носії", FILL, INK, ""),
    ]
    bh = 58
    gap = 26
    y = 64
    ys = []
    for title, sub, fill, col, _ in rows:
        ys.append(y)
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=2.0))
        p.append(text(cx, y + 23, title, size=13, color=col, bold=True))
        p.append(text(cx, y + 42, sub, size=10.5, color=MUTED))
        y += bh + gap

    # стрілки вниз «кличе» зліва, вгору «дані/код помилки» справа
    for i in range(len(rows) - 1):
        xx_d = x + 70
        p.append(arrow(xx_d, ys[i] + bh, xx_d, ys[i + 1], color=INK, sw=2.0))
        xx_u = x + bw - 70
        p.append(arrow(xx_u, ys[i + 1], xx_u, ys[i] + bh, color=MUTED, sw=1.6))

    p.append(text(x + 58, ys[0] + bh + gap / 2 + 4, "кличе вниз", size=9.5, color=INK, anchor="end"))
    p.append(text(x + bw - 58, ys[0] + bh + gap / 2 + 4, "дані / код", size=9.5, color=MUTED, anchor="start"))

    # виноска до шва
    p.append(text(cx, ys[2] + bh + 17, "↑ замінюєте лише цей шар — і той самий FatFs пише на будь-який носій",
                  size=10.5, color=NEG, bold=True))

    render(os.path.join(OUT, "layers.svg"), W, H, *p,
           title="FatFs: три шари й шов diskio")


# ── sync-risk: де насправді ваші дані ─────────────────────────────────────────
# Ідея: горизонтальний шлях даних. f_write кладе байти лише в кеш ОЗП (вразливо).
# f_sync / f_close скидають кеш на носій і оновлюють каталог+таблицю (надійно).

def fig_sync_risk():
    W, H = 720, 330
    p = []

    # три блоки: застосунок → кеш ОЗП → носій
    by = 90
    bh = 70
    app = (60, 150)
    cache = (300, 150)
    media = (540, 150)

    def block(xy, title, sub, fill, col):
        x, w = xy
        p.append(rect(x, by, w, bh, fill=fill, stroke=col, sw=2.0))
        p.append(text(x + w / 2, by + 28, title, size=12.5, color=col, bold=True))
        p.append(text(x + w / 2, by + 48, sub, size=10, color=MUTED))

    block(app, "застосунок", "ваш код", FILL, INK)
    block(cache, "кеш у ОЗП", "вразливо при збої", "#fdecea", POS)
    block(media, "носій", "надійно", "#eafaf0", FIELD)

    # f_write: застосунок → кеш
    ax = app[0] + app[1]
    p.append(arrow(ax, by + bh / 2, cache[0], by + bh / 2, color=INK, sw=2.2))
    p.append(text((ax + cache[0]) / 2, by - 12, "f_write", size=12, color=INK, bold=True))
    p.append(text((ax + cache[0]) / 2, by + bh + 20, "швидко", size=9.5, color=MUTED))

    # f_sync / f_close: кеш → носій
    bx = cache[0] + cache[1]
    p.append(arrow(bx, by + bh / 2, media[0], by + bh / 2, color=FIELD, sw=2.6))
    p.append(text((bx + media[0]) / 2, by - 12, "f_sync /\nf_close" if False else "f_sync / f_close", size=11.5, color=FIELD, bold=True))
    p.append(mtext((bx + media[0]) / 2, by + bh + 20, "скидає кеш,\nоновлює каталог\n+ таблицю FAT",
                   size=9, color=FIELD))

    # блискавка-загроза над кешем
    p.append(text(cache[0] + cache[1] / 2, by - 40, "⚡ зникло живлення → незбережене зникає",
                  size=11, color=POS, bold=True))

    p.append(text(W / 2, H - 20,
                  "різниця f_sync і f_close одна: f_sync лишає файл відкритим, f_close — ні",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "sync-risk.svg"), W, H, *p,
           title="f_write кладе в кеш; надійним робить f_sync / f_close")


# ── media-choice: один FatFs, два носії ───────────────────────────────────────
# Ідея: під FatFs дві дороги. Ліворуч SD — власний контролер, простий diskio.
# Праворуч сира Flash — потрібен шар вирівнювання зносу, інакше таблиця FAT
# швидко вб'є свій блок.

def fig_media_choice():
    W, H = 720, 360
    p = []
    cx = W / 2

    # спільна вершина — FatFs
    top, tw, th = textbox(cx, 60, "FatFs (формат FAT)", size=13, bold=True,
                          fill="#f6f4ec", stroke=INK, sw=2, pad=12)
    p.append(top)

    lx = 185
    rx = W - 185
    # розгалуження
    p.append(arrow(cx - tw * 0.18, 60 + th / 2, lx, 150, color=INK, sw=1.8))
    p.append(arrow(cx + tw * 0.18, 60 + th / 2, rx, 150, color=INK, sw=1.8))

    # ── ліва дорога: SD-картка ──
    def stack(x, items, headcol):
        y = 150
        bw, bh, gap = 250, 46, 16
        ys = []
        for i, (t, s, fill, col) in enumerate(items):
            ys.append(y)
            p.append(rect(x - bw / 2, y, bw, bh, fill=fill, stroke=col, sw=1.8))
            p.append(text(x, y + 19, t, size=11.5, color=col, bold=True))
            if s:
                p.append(text(x, y + 36, s, size=9.5, color=MUTED))
            y += bh + gap
        for i in range(len(ys) - 1):
            p.append(arrow(x, ys[i] + bh, x, ys[i + 1], color=headcol, sw=1.6))
        return ys

    stack(lx, [
        ("ваш diskio", "простий: читай / пиши блок", "#eef4ff", NEG),
        ("SD-картка", "власний контролер ховає знос", "#eafaf0", FIELD),
    ], INK)
    p.append(text(lx, 134, "просто, але дешеві картки", size=10, color=FIELD, bold=True))

    ys = stack(rx, [
        ("ваш diskio", None, "#eef4ff", NEG),
        ("шар вирівнювання зносу", "тасує блоки рівномірно", "#fff7e6", POS),
        ("сира Flash", "стирати блоками, ресурс комірок", FILL, INK),
    ], INK)
    p.append(text(rx, 134, "складніше, але дешево й надійно", size=10, color=POS, bold=True))

    p.append(text(W / 2, H - 16,
                  "вибір носія міняє не застосунок, а лише нижній шар під FatFs",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "media-choice.svg"), W, H, *p,
           title="Один FatFs — дві дороги до носія")


if __name__ == "__main__":
    fig_layers()
    fig_sync_risk()
    fig_media_choice()
    print("OK: figures written to", OUT)
