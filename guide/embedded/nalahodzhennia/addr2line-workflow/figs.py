# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── numbers-to-source: голі адреси + .elf → функція/файл/рядок ────────────────
# Ідея статті в одній картинці. Зліва — рядок Backtrace: з UART: самі числа,
# жодного сенсу. По центру — addr2line, що бере той рядок і .elf як словник.
# Справа — той самий слід уже як імена функцій і рядки коду.
def fig_numbers_to_source():
    W, H = 760, 320
    parts = []

    # ── ліворуч: голий backtrace з консолі ──
    lx, lw = 24, 230
    parts.append(fitbox(lx, 70, lw, 200,
                        "", fill="#0f1115", stroke="#0f1115"))
    parts.append(text(lx + lw / 2, 56, "що бачиш у консолі", size=13, color=MUTED, bold=True))
    mono = "'Consolas','DejaVu Sans Mono',monospace"
    raw = ["Backtrace:",
           "0x400f360d:0x3ffb7e00",
           "0x400dbf56:0x3ffb7e20",
           "0x400d8a11:0x3ffb7e40"]
    for i, ln in enumerate(raw):
        col = "#e06c75" if i == 0 else "#98c379"
        parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" '
                     'fill="%s">%s</text>' % (lx + 14, 104 + i * 30, mono, col, esc(ln)))

    # ── центр: addr2line + .elf ──
    cx = 380
    b, bw, bh = textbox(cx, 120, "addr2line", size=16, bold=True,
                        fill="#fff7e6", stroke=POS, sw=2)
    parts.append(b)
    e, ew, eh = textbox(cx, 200, ["firmware.elf", "(DWARF: адреса → рядок)"],
                        size=12, fill="#eaf0fd", stroke=NEG)
    parts.append(e)
    parts.append(arrow(cx, 200 - eh / 2, cx, 120 + bh / 2 + 2, color=NEG))
    parts.append(text(cx + 96, 168, "словник", size=11, color=NEG, italic=True))

    # стрілки зліва→центр і центр→справа
    parts.append(arrow(lx + lw + 4, 150, cx - bw / 2 - 6, 120, color=LINE))
    parts.append(arrow(cx + bw / 2 + 6, 120, 520, 150, color=FIELD, sw=2.2))

    # ── справа: розшифрований слід ──
    rx, rw = 524, 212
    parts.append(text(rx + rw / 2, 56, "що це означає", size=13, color=FIELD, bold=True))
    dec = ["i2c_read", "  sensor.c:88",
           "update_sensors", "  tasks.c:45",
           "sensor_task", "  tasks.c:120"]
    for i, ln in enumerate(dec):
        is_fn = (i % 2 == 0)
        col = INK if is_fn else MUTED
        parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" '
                     'fill="%s"%s>%s</text>' % (
                         rx + 8, 96 + i * 26, mono, col,
                         ' font-weight="700"' if is_fn else '', esc(ln)))

    render(os.path.join(OUT, "numbers-to-source.svg"), W, H, *parts)


# ── pc-sp-pair: анатомія однієї пари PC:SP у віконному ABI Xtensa ─────────────
# Чому в сліді ДВА числа на кадр. PC — куди (адреса в коді, її й декодує
# addr2line). SP — вузол розкрутки: під ним лежить SP попереднього кадру,
# тому ланцюг можна йти назад. Зіпсуй SP — і слід обірветься.
def fig_pc_sp_pair():
    W, H = 720, 360
    parts = [text(W / 2, 30, "Один кадр сліду = дві ролі", size=17, bold=True)]
    mono = "'Consolas','DejaVu Sans Mono',monospace"

    # сама пара великим моноширинним
    px, py = W / 2, 92
    parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="30" '
                 'fill="%s" text-anchor="middle" font-weight="700">'
                 '<tspan fill="%s">0x400f360d</tspan>'
                 '<tspan fill="%s">:</tspan>'
                 '<tspan fill="%s">0x3ffb7e00</tspan></text>' % (
                     px, py, mono, INK, POS, MUTED, NEG))

    # підписи-виноски під половинами
    parts.append(arrow(px - 110, py + 14, px - 110, py + 44, color=POS))
    parts.append(arrow(px + 95, py + 14, px + 95, py + 44, color=NEG))

    bpc, wpc, hpc = textbox(px - 110, 178,
                            ["PC — куди", "адреса в коді"],
                            size=13, bold=True, fill="#fdecea", stroke=POS, color=POS)
    parts.append(bpc)
    bsp, wsp, hsp = textbox(px + 95, 178,
                            ["SP — звідки далі", "вузол розкрутки"],
                            size=13, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG)
    parts.append(bsp)

    parts.append(text(px - 110, 226, "це й годує addr2line", size=12, color=POS, italic=True))
    parts.append(text(px + 95, 226, "це веде до наступного кадру", size=12, color=NEG, italic=True))

    # маленька діаграма стека: під кожним SP лежить SP попереднього
    sx, sy, sw, sh = 230, 256, 260, 80
    parts.append(rect(sx, sy, sw, sh, fill="#f9fafb"))
    parts.append(text(sx + sw / 2, sy + 18, "у стеку: під SP кадру — SP попереднього",
                     size=11, color=MUTED))
    # три клітинки-кадри
    cw = sw / 3
    for i, name in enumerate(["кадр 0", "кадр 1", "кадр 2"]):
        cxx = sx + i * cw
        parts.append(rect(cxx + 4, sy + 30, cw - 8, 36, fill=FILL, stroke=NEG, sw=1.4))
        parts.append(text(cxx + cw / 2, sy + 52, name, size=11, color=INK))
        if i < 2:
            parts.append(arrow(cxx + cw - 4, sy + 48, cxx + cw + 4, sy + 48, color=NEG, sw=1.6))

    render(os.path.join(OUT, "pc-sp-pair.svg"), W, H, *parts)


# ── elf-is-dictionary: чому потрібен САМЕ той .elf ────────────────────────────
# Одна адреса, три словники. Рідний .elf → правильний рядок. Чужий (інша
# збірка) → правдоподібний, але ХИБНИЙ рядок (адреси з'їхали). Stripped .bin
# (те, що у Flash) → словника нема взагалі: ??:0.
def fig_elf_dictionary():
    W, H = 740, 330
    parts = [text(W / 2, 30, "Та сама адреса, три словники", size=17, bold=True)]
    mono = "'Consolas','DejaVu Sans Mono',monospace"

    parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="15" '
                 'fill="%s" text-anchor="middle">addr2line  0x400f360d  →  ?</text>' % (
                     W / 2, 60, mono, INK))

    col_w = 226
    xs = [22, 22 + col_w + 12, 22 + 2 * (col_w + 12)]
    heads = ["рідний firmware.elf", "чужий .elf (інша збірка)", "stripped .bin із Flash"]
    cols = [FIELD, POS, MUTED]
    results = [
        ["sensor.c:88", "✓ правильно"],
        ["wifi.c:213", "✗ хибний рядок"],
        ["??:0", "немає DWARF"],
    ]
    fills = ["#eafaf0", "#fdecea", "#f3f4f6"]
    strokes = [FIELD, POS, MUTED]
    for i in range(3):
        x = xs[i]
        parts.append(fitbox(x, 84, col_w, 40, heads[i], size=12, bold=True,
                            fill="#ffffff", stroke=strokes[i], color=strokes[i]))
        parts.append(rect(x, 134, col_w, 120, fill=fills[i], stroke=strokes[i], sw=1.6))
        parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="16" '
                     'fill="%s" text-anchor="middle" font-weight="700">%s</text>' % (
                         x + col_w / 2, 184, mono, INK, esc(results[i][0])))
        parts.append(text(x + col_w / 2, 222, results[i][1], size=13, color=cols[i], bold=True))

    parts.append(text(W / 2, 300,
                     "Числа адрес однакові — сенс дає лише точно відповідний .elf із цієї збірки.",
                     size=13, color=INK))
    render(os.path.join(OUT, "elf-dictionary.svg"), W, H, *parts)


# ── decode-spectrum: три способи розшифрувати, за зростанням сили й мороки ─────
# addr2line у контексті. Авто (idf.py monitor) — нуль зусиль, але лише поки
# дивишся живу консоль. Ручний addr2line — лог із поля + .elf, без чипа.
# Повний GDB над core dump — змінні й кадри, але потрібен записаний дамп.
def fig_decode_spectrum():
    W, H = 760, 300
    parts = [text(W / 2, 30, "Три способи перетворити адреси на рядки", size=17, bold=True)]

    items = [
        ("idf.py monitor", "автоматично, наживо",
         "нуль зусиль; лише поки\nдивишся живу консоль", FIELD, "#eafaf0"),
        ("addr2line вручну", "лог із поля + .elf",
         "слід з будь-якого логу,\nбез чипа; лише рядки", POS, "#fff7e6"),
        ("GDB над core dump", "повна сцена офлайн",
         "змінні, кадри, всі задачі;\nтреба записаний дамп", NEG, "#eaf0fd"),
    ]
    bw, gap = 220, 20
    x0 = (W - (3 * bw + 2 * gap)) / 2
    for i, (title, sub, note, col, fill) in enumerate(items):
        x = x0 + i * (bw + gap)
        parts.append(rect(x, 70, bw, 150, fill=fill, stroke=col, sw=2))
        parts.append(text(x + bw / 2, 98, title, size=15, color=INK, bold=True))
        parts.append(text(x + bw / 2, 120, sub, size=12, color=col, italic=True))
        parts.append(fitbox(x + 12, 138, bw - 24, 66, note, size=12,
                            fill="#ffffff", stroke=col, color=INK))
        if i < 2:
            parts.append(arrow(x + bw + 2, 145, x + bw + gap - 2, 145, color=LINE, sw=2))

    parts.append(text(W / 2, 250, "ліворуч — менше зусиль; праворуч — більше сили й більше підготовки",
                     size=13, color=MUTED))
    parts.append(text(W / 2, 274, "addr2line — золота середина: працює з голого тексту логу",
                     size=13, color=POS, bold=True))
    render(os.path.join(OUT, "decode-spectrum.svg"), W, H, *parts)


# ── split-debug: один .elf → реліз + словник, зшиті .gnu_debuglink (CRC) ──────
# Вставка proj-symbol-server. Три кроки objcopy: only-keep-debug витягує DWARF
# у словник; strip-debug лишає стрункий реліз; add-gnu-debuglink вписує в реліз
# ім'я словника + 4-байтову CRC. Реліз — у поле, словник — в архів; CRC не дає
# підхопити чужий словник.
def fig_split_debug():
    W, H = 760, 340
    parts = [text(W / 2, 30, "Один .elf → стрункий реліз + товстий словник", size=17, bold=True)]

    # вхідний повний .elf
    src, sw_, sh_ = textbox(W / 2, 78, ["firmware.elf", "код + увесь DWARF"],
                            size=13, bold=True, fill="#fff7e6", stroke=POS)
    parts.append(src)

    # дві гілки вниз
    lx, rx = 200, 560
    by = 170
    parts.append(arrow(W / 2 - 20, 78 + sh_ / 2, lx, by - 34, color=NEG))
    parts.append(arrow(W / 2 + 20, 78 + sh_ / 2, rx, by - 34, color=FIELD))
    parts.append(text((W / 2 - 20 + lx) / 2 - 40, 122, "--strip-debug", size=11, color=NEG, italic=True))
    parts.append(text((W / 2 + 20 + rx) / 2 + 44, 122, "--only-keep-debug", size=11, color=FIELD, italic=True))

    # ліворуч: обчищений реліз
    lb, lw, lh = textbox(lx, by, ["firmware-stripped.elf", "код, без DWARF"],
                         size=12, bold=True, fill="#eaf0fd", stroke=NEG)
    parts.append(lb)
    parts.append(text(lx, by + 44, "→ їде в поле", size=12, color=NEG, italic=True))

    # праворуч: словник
    rb, rw, rh = textbox(rx, by, ["firmware.debug", "самий DWARF"],
                         size=12, bold=True, fill="#eafaf0", stroke=FIELD)
    parts.append(rb)
    parts.append(text(rx, by + 44, "→ лягає в архів", size=12, color=FIELD, italic=True))

    # зшивання: .gnu_debuglink (ім'я + CRC) між ними
    linkbox, lkw, lkh = textbox(W / 2, by, [".gnu_debuglink", "ім'я + 4-байт CRC"],
                                size=12, bold=True, fill="#ffffff", stroke=INK)
    parts.append(linkbox)
    parts.append(arrow(lx + lw / 2 + 4, by, W / 2 - lkw / 2 - 4, by, color=INK, sw=1.6))
    parts.append(line(W / 2 + lkw / 2 + 4, by, rx - rw / 2 - 4, by, color=INK, sw=1.6, dash="4 3"))
    parts.append(text(W / 2, by - lkh / 2 - 10, "--add-gnu-debuglink", size=11, color=INK, italic=True))

    parts.append(text(W / 2, 272,
                     "Реліз малий — у поле; словник окремо — в архів.",
                     size=13, color=INK))
    parts.append(text(W / 2, 296,
                     "CRC у debuglink не дає GDB підхопити схожий ЧУЖИЙ словник.",
                     size=13, color=POS, bold=True))
    render(os.path.join(OUT, "split-debug.svg"), W, H, *parts)


# ── build-id-flow: відбиток замикає коло образ-у-полі ↔ словник-у-архіві ──────
# Вставка proj-symbol-server. Компонувальник рахує хеш над вмістом → .note.gnu
# .build-id. Та сама секція у Flash, тож прошивка друкує свій Build-ID у лог
# поряд із версією. На сервері той самий хеш — ключ до .elf у сховищі.
def fig_build_id_flow():
    W, H = 780, 300
    parts = [text(W / 2, 28, "Build-ID: один відбиток зшиває образ із його словником", size=16, bold=True)]
    mono = "'Consolas','DejaVu Sans Mono',monospace"

    # чотири щаблі в ряд
    boxes = [
        ("компонувальник", "хеш над вмістом\n--build-id", FIELD, "#eafaf0"),
        (".note.gnu.build-id", "секція в образі\n(їде у Flash)", NEG, "#eaf0fd"),
        ("прошивка в полі", "друкує свій\nBuild-ID у лог", POS, "#fff7e6"),
        ("сховище символів", "хеш — ключ\nдо .elf", INK, "#f3f4f6"),
    ]
    bw, gap = 168, 24
    x0 = (W - (4 * bw + 3 * gap)) / 2
    cy = 96
    for i, (title, sub, col, fill) in enumerate(boxes):
        x = x0 + i * (bw + gap)
        parts.append(rect(x, cy, bw, 78, fill=fill, stroke=col, sw=2))
        parts.append(text(x + bw / 2, cy + 24, title, size=13, color=INK, bold=True))
        parts.append(mtext(x + bw / 2, cy + 44, sub, size=11, color=col))
        if i < 3:
            parts.append(arrow(x + bw + 2, cy + 39, x + bw + gap - 2, cy + 39, color=LINE, sw=2))

    # сам хеш великим моноширинним під ланцюгом
    parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="15" '
                 'fill="%s" text-anchor="middle" font-weight="700">'
                 'Build ID: 4e9f2a1c8b3d5e7f…1a3c5e7f9b1d</text>' % (
                     W / 2, 218, mono, INK))
    parts.append(text(W / 2, 252,
                     "Той самий 40-значний хеш — у логу з поля Й іменем файла в архіві.",
                     size=13, color=INK))
    parts.append(text(W / 2, 276,
                     "Машина рахує його з коду — переплутати збірки руками неможливо.",
                     size=13, color=FIELD, bold=True))
    render(os.path.join(OUT, "build-id-flow.svg"), W, H, *parts)


# ── binutils-layers (вставка hist-binutils-addr2line): що під addr2line ───────
# Сам інструмент не розбирає формати файлів — він кличе BFD, а та ховає всі
# відмінності форматів (ELF/COFF/a.out/PE) за одним інтерфейсом. Усередині .elf
# лежить DWARF — мапа «адреса → рядок». Тому той самий код обслуговує і ESP32,
# і чужу архітектуру: різницю проковтнула бібліотека (кросовість від Cygnus).
def fig_binutils_layers():
    W, H = 720, 360
    parts = [text(W / 2, 30, "Що під addr2line", size=17, bold=True)]
    mono = "'Consolas','DejaVu Sans Mono',monospace"

    bt, wt, ht = textbox(W / 2, 70, "addr2line", size=16, bold=True,
                         fill="#fff7e6", stroke=POS, sw=2)
    parts.append(bt)

    parts.append(arrow(W / 2, 70 + ht / 2, W / 2, 116, color=LINE))
    parts.append(text(W / 2 + 150, 100, "«дай символи й рядки»", size=11,
                      color=MUTED, italic=True))

    bx, by, bw, bh = 150, 122, W - 300, 52
    parts.append(rect(bx, by, bw, bh, fill="#eafaf0", stroke=FIELD, sw=2))
    parts.append(text(W / 2, by + 22, "BFD — бібліотека-абстракція форматів",
                      size=14, color=INK, bold=True))
    parts.append(text(W / 2, by + 40, "єдиний інтерфейс понад усіма форматами",
                      size=11, color=FIELD, italic=True))

    fmts = ["ELF", "COFF", "a.out", "PE"]
    fw, gap = 120, 18
    x0 = (W - (4 * fw + 3 * gap)) / 2
    fy = 214
    for i, fm in enumerate(fmts):
        x = x0 + i * (fw + gap)
        parts.append(arrow(W / 2, by + bh, x + fw / 2, fy, color=FIELD, sw=1.4))
        hot = (fm == "ELF")
        parts.append(rect(x, fy, fw, 46,
                          fill="#fdecea" if hot else FILL,
                          stroke=POS if hot else NEG, sw=1.8 if hot else 1.4))
        parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="15" '
                     'fill="%s" text-anchor="middle" font-weight="700">%s</text>' % (
                         x + fw / 2, fy + 22, mono, INK, esc(fm)))
        sub = "у ньому DWARF" if hot else "інший формат"
        parts.append(text(x + fw / 2, fy + 38, sub, size=10,
                          color=POS if hot else MUTED))

    parts.append(text(W / 2, 300,
                      "addr2line не читає формати сам — за нього це робить BFD; усередині ELF лежить DWARF.",
                      size=12, color=INK))
    parts.append(text(W / 2, 322,
                      "Тому той самий код обслуговує і ESP32, і чужу архітектуру — різницю проковтнула бібліотека.",
                      size=12, color=MUTED))
    render(os.path.join(OUT, "binutils-layers.svg"), W, H, *parts)


# ── gdb-vs-addr2line (вставка hist-binutils-addr2line): навіщо окремий ────────
# при наявному GDB. GDB — важкий інтерактивний відлагоджувач: жива сесія,
# потрібен процес/чип. addr2line — крихітний пакетний фільтр: .elf + числа →
# рядки, легко в конвеєр, живого процесу не треба. Лаутер 1997 виокремив цю
# дрібну операцію, бо ганяти GDB заради перекладу адрес — як танком цвях.
def fig_gdb_vs_addr2line():
    W, H = 760, 320
    parts = [text(W / 2, 30, "Одна адреса — два шляхи", size=17, bold=True)]
    mono = "'Consolas','DejaVu Sans Mono',monospace"

    colw, gap = 350, 40
    x0 = (W - (2 * colw + gap)) / 2

    gx = x0
    parts.append(rect(gx, 60, colw, 210, fill="#eaf0fd", stroke=NEG, sw=2))
    parts.append(text(gx + colw / 2, 88, "GDB", size=18, color=INK, bold=True))
    parts.append(text(gx + colw / 2, 110, "повний відлагоджувач", size=12,
                      color=NEG, italic=True))
    gl = ["жива інтерактивна сесія",
          "потрібен запущений процес / чип",
          "зупинки, кроки, змінні",
          "могутньо — та важко для дрібниці"]
    for i, ln in enumerate(gl):
        parts.append(minus(gx + 26, 140 + i * 28, r=7))
        parts.append(text(gx + 42, 145 + i * 28, ln, size=12, color=INK, anchor="start"))

    ax = x0 + colw + gap
    parts.append(rect(ax, 60, colw, 210, fill="#fff7e6", stroke=POS, sw=2))
    parts.append(text(ax + colw / 2, 88, "addr2line", size=18, color=INK, bold=True))
    parts.append(text(ax + colw / 2, 110, "крихітний пакетний фільтр", size=12,
                      color=POS, italic=True))
    al = [".elf + числа → рядки коду",
          "живого процесу не треба",
          "легко в конвеєр і скрипт",
          "одна річ — зроблена добре"]
    for i, ln in enumerate(al):
        parts.append(plus(ax + 26, 140 + i * 28, r=7))
        parts.append(text(ax + 42, 145 + i * 28, ln, size=12, color=INK, anchor="start"))

    parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" '
                 'fill="%s" text-anchor="middle">cat log | addr2line -e fw.elf</text>' % (
                     ax + colw / 2, 258, mono, MUTED))

    parts.append(text(W / 2, 296,
                      "Лаутер 1997-го виокремив саме цю операцію: ганяти GDB заради перекладу адрес — як танком забивати цвях.",
                      size=12, color=INK))
    render(os.path.join(OUT, "gdb-vs-addr2line.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_numbers_to_source()
    fig_pc_sp_pair()
    fig_elf_dictionary()
    fig_decode_spectrum()
    fig_split_debug()
    fig_build_id_flow()
    fig_binutils_layers()
    fig_gdb_vs_addr2line()
    print("ok")
