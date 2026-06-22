# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

FLASH = "#eef4ff"   # світла заливка «Flash»
FLASH_S = "#c9d6f0"
RAM_F = "#eafaf0"   # світла заливка «RAM»
RAM_S = "#bfe6cf"
RO_F  = "#fdf6e3"   # «лише для читання»


# ── why-sections: різнорідний вміст → Flash чи RAM за потребою ─────────────────
# Ідея: три сорти вмісту програми сортуються за однією ознакою «що має пережити
# вимкнення й чи змінюється» — звідси й місце: енергонезалежний Flash чи швидка RAM.

def fig_why_sections():
    W, H = 720, 330
    p = []
    # дві скриньки пам'яті
    fx, fy, fw, fh = 60, 70, 270, 210
    rx, ry, rw, rh = 390, 70, 270, 210
    p.append(rect(fx, fy, fw, fh, fill=FLASH, stroke=FLASH_S, sw=2))
    p.append(rect(rx, ry, rw, rh, fill=RAM_F, stroke=RAM_S, sw=2))
    p.append(text(fx + fw / 2, fy + 24, "Flash", size=15, bold=True, color="#3a5bb8"))
    p.append(text(fx + fw / 2, fy + 42, "переживає вимкнення", size=10, color=MUTED))
    p.append(text(rx + rw / 2, ry + 24, "RAM", size=15, bold=True, color=FIELD))
    p.append(text(rx + rw / 2, ry + 42, "швидка, але летка", size=10, color=MUTED))

    # мешканці Flash
    for i, lab in enumerate(("код (інструкції)", "сталі дані", "початкові значення")):
        p.append(fitbox(fx + 22, fy + 64 + i * 44, fw - 44, 34, lab, size=11,
                        fill="#ffffff", stroke=FLASH_S, sw=1.4, color=INK))
    # мешканці RAM
    for i, lab in enumerate(("змінні (живі)", "стек і купа\n(ростуть на ходу)")):
        p.append(fitbox(rx + 22, ry + 64 + i * 56, rw - 44, 46, lab, size=11,
                        fill="#ffffff", stroke=RAM_S, sw=1.4, color=INK))

    p.append(text(W / 2, H - 16,
                  "сортуємо за ознакою: чи має пережити вимкнення й чи змінюється",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "why-sections.svg"), W, H, *p,
           title="Вміст програми різнорідний: що у Flash, що в RAM")


# ── three-sections: .text / .data / .bss — що це й де живе ─────────────────────
# Ідея: три класичні секції в одному ряду; під кожною — приклад коду, ознака
# «читається/змінюється» і де її початок (Flash чи нуль).

def fig_three_sections():
    W, H = 740, 300
    p = []
    cols = [
        (".text", "int code;\n(машинний код)", "тільки читається", "Flash", FLASH, FLASH_S, "#3a5bb8"),
        (".data", "int x = 5;", "змінюється; початок у Flash", "Flash → RAM", RAM_F, RAM_S, FIELD),
        (".bss",  "int y;  // = 0", "змінюється; початок — нуль", "RAM (нуль)", RAM_F, RAM_S, FIELD),
    ]
    bw, gap = 210, 24
    x0 = (W - (bw * 3 + gap * 2)) / 2
    for i, (name, code, rw_lab, where, fill, stroke, col) in enumerate(cols):
        x = x0 + i * (bw + gap)
        p.append(rect(x, 60, bw, 200, fill=fill, stroke=stroke, sw=2))
        p.append(text(x + bw / 2, 90, name, size=18, bold=True, color=col))
        p.append(fitbox(x + 18, 108, bw - 36, 44, code, size=12, fill="#ffffff",
                        stroke=stroke, sw=1.3, color=INK))
        p.append(text(x + bw / 2, 178, rw_lab, size=11, color=INK))
        p.append(text(x + bw / 2, 230, where, size=12, bold=True, color=col))
    render(os.path.join(OUT, "three-sections.svg"), W, H, *p,
           title="Три класичні секції: код, ненульові й нульові змінні")


# ── data-bss-twist: звідки беруться початкові значення ────────────────────────
# Ідея: показати дві адреси ініціалізованої змінної (склад у Flash → дім у RAM),
# а поряд — .bss, якій склад не потрібен (просто обнулення).

def fig_data_bss_twist():
    W, H = 720, 320
    p = []
    # .data: склад → дім
    p.append(text(180, 56, ".data:  int x = 5", size=13, bold=True, color=FIELD))
    store, sw_, sh_ = textbox(120, 130, "склад (Flash)\nтут лежить «5»", size=11,
                              fill=FLASH, stroke=FLASH_S, sw=1.6, color=INK)
    home, hw_, hh_ = textbox(280, 130, "дім (RAM)\nтут живе x", size=11,
                             fill=RAM_F, stroke=RAM_S, sw=1.6, color=INK)
    p.append(store); p.append(home)
    p.append(arrow(120 + sw_ / 2, 130, 280 - hw_ / 2, 130, color=INK, sw=2))
    p.append(text(200, 112, "копія при старті", size=10, color=MUTED))

    # .bss: лише обнулення
    p.append(text(540, 56, ".bss:  int y", size=13, bold=True, color=FIELD))
    z, zw_, zh_ = textbox(540, 130, "дім (RAM)\nпросто обнулити", size=11,
                          fill=RAM_F, stroke=RAM_S, sw=1.6, color=INK)
    p.append(z)
    p.append(text(540, 184, "складу у Flash нема\n(нуль зберігати ні до чого)",
                  size=10, color=MUTED))

    p.append(line(W / 2, 70, W / 2, 250, color="#dddddd", sw=1, dash="4 4"))
    p.append(text(W / 2, 286,
                  "ініціалізована змінна коштує і Flash, і RAM; нульова — лише RAM",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "data-bss-twist.svg"), W, H, *p,
           title="Парадокс початкових значень: RAM при старті порожня")


# ── startup-copy: стартовий код готує RAM до main() ───────────────────────────
# Ідея: лінійка часу від скидання до main(); між ними — два кроки стартового
# коду: копія .data з Flash і обнулення .bss.

def fig_startup_copy():
    W, H = 740, 240
    p = []
    y = 120
    boxes = [
        ("скидання\n(увімкнення)", FILL, INK),
        ("копіювати .data\nFlash → RAM", FLASH, "#3a5bb8"),
        ("обнулити .bss\n(затерти нулями)", RAM_F, FIELD),
        ("main() /\nsetup()", "#f6f4ec", INK),
    ]
    bw, gap = 150, 40
    x0 = (W - (bw * len(boxes) + gap * (len(boxes) - 1))) / 2
    cx = []
    for i, (lab, fill, col) in enumerate(boxes):
        x = x0 + i * (bw + gap)
        p.append(fitbox(x, y - 34, bw, 68, lab, size=12, fill=fill, stroke=col,
                        sw=1.8, bold=True, color=col))
        cx.append((x, x + bw))
        if i > 0:
            p.append(arrow(cx[i - 1][1] + 4, y, x - 4, y, color=INK, sw=1.8))
    p.append(text(W / 2, H - 22,
                  "аж тепер змінні мають правильний початок — до цього в RAM сміття",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "startup-copy.svg"), W, H, *p,
           title="Що стається до main(): стартовий код готує RAM")


# ── elf-to-bin: ELF → bin, секції/сегменти, точка входу, контрольна сума ───────
# Ідея (НОВА фігура під worked-приклад): зліва товстий ELF з метаданими; objcopy
# зрізає все зайве; справа голий образ — заголовок (магія, точка входу, лічильник
# сегментів), самі сегменти й контрольна сума в хвості.

def fig_elf_to_bin():
    W, H = 740, 380
    p = []
    # ── ELF ліворуч ──
    ex, ey, ew = 40, 64, 220
    elf_rows = [
        ("заголовок ELF", "#e9e9e9"),
        (".text (код)", FLASH),
        (".rodata (сталі)", RO_F),
        (".data (поч. значення)", RAM_F),
        ("таблиця символів", "#f0e6e6"),
        ("налагодж. дані", "#f0e6e6"),
        ("заголовки секцій", "#f0e6e6"),
    ]
    rh = 36
    p.append(text(ex + ew / 2, ey - 14, "program.elf", size=13, bold=True, color=INK))
    for i, (lab, fill) in enumerate(elf_rows):
        yy = ey + i * rh
        p.append(rect(ex, yy, ew, rh, fill=fill, stroke="#bbbbbb", sw=1.2, rx=0))
        p.append(text(ex + ew / 2, yy + rh / 2 + 4, lab, size=10, color=INK))
    p.append(text(ex + ew / 2, ey + len(elf_rows) * rh + 18,
                  "усе: код + дані + метадані", size=10, color=MUTED, italic=True))

    # ── стрілка objcopy ──
    mx = ex + ew + 30
    p.append(arrow(mx, ey + 70, mx + 90, ey + 70, color=INK, sw=2.2))
    p.append(text(mx + 46, ey + 56, "objcopy", size=12, bold=True, color=POS))
    p.append(text(mx + 46, ey + 90, "--output-target\n=binary", size=9, color=MUTED))
    p.append(text(mx + 46, ey + 128, "зрізає метадані", size=9, color=MUTED, italic=True))

    # ── bin праворуч ──
    bx, by, bw = mx + 120, 64, 230
    bin_rows = [
        ("заголовок: магія 0xE9", "#dfe9ff", "#3a5bb8"),
        ("· лічильник сегментів", "#eef4ff", INK),
        ("· точка входу", "#eef4ff", INK),
        ("сегмент → адреса .text", FLASH, INK),
        ("сегмент → адреса .data", RAM_F, INK),
        ("контрольна сума (1 байт)", "#fdecea", POS),
    ]
    p.append(text(bx + bw / 2, by - 14, "program.bin", size=13, bold=True, color=INK))
    for i, (lab, fill, col) in enumerate(bin_rows):
        yy = by + i * rh
        p.append(rect(bx, yy, bw, rh, fill=fill, stroke="#bbbbbb", sw=1.2, rx=0))
        p.append(text(bx + bw / 2, yy + rh / 2 + 4, lab, size=10, color=col,
                      bold=(i == 0 or i == 5)))
    p.append(text(bx + bw / 2, by + len(bin_rows) * rh + 18,
                  "лише те, що лягає у Flash", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "elf-to-bin.svg"), W, H, *p,
           title="Від .elf до .bin: образ — це тільки те, що летить у Flash")


# ── image-vs-ram: образ у Flash проти вмісту RAM під час роботи ────────────────
# Ідея: дві різні картини того самого — образ (що заливають) і RAM (що в роботі);
# .data — у двох; .bss — лише як розмір в образі, але жива в RAM; стек/купа зверху.

def fig_image_vs_ram():
    W, H = 720, 330
    p = []
    # Образ у Flash
    fx, fy, fw = 70, 70, 250
    p.append(text(fx + fw / 2, fy - 14, "Образ у Flash (що заливають)",
                  size=12, bold=True, color="#3a5bb8"))
    img_rows = [(".text (код)", FLASH, 70), (".data (поч. значення)", RAM_F, 40),
                (".bss → лише розмір", "#f0f0f0", 24)]
    yy = fy
    for lab, fill, hh in img_rows:
        p.append(rect(fx, yy, fw, hh, fill=fill, stroke="#bbbbbb", sw=1.3, rx=0))
        p.append(text(fx + fw / 2, yy + hh / 2 + 4, lab, size=10, color=INK))
        yy += hh
    p.append(text(fx + fw / 2, yy + 18, "нулів .bss в образі нема", size=10,
                  color=MUTED, italic=True))

    # RAM під час роботи
    rx, ry, rw = 400, 70, 250
    p.append(text(rx + rw / 2, ry - 14, "RAM під час роботи",
                  size=12, bold=True, color=FIELD))
    ram_rows = [(".data (скопійована)", RAM_F, 40), (".bss (обнулена)", RAM_F, 60),
                ("стек ↓ … купа ↑", "#eafaf0", 50)]
    yy = ry
    for lab, fill, hh in ram_rows:
        p.append(rect(rx, yy, rw, hh, fill=fill, stroke=RAM_S, sw=1.3, rx=0))
        p.append(text(rx + rw / 2, yy + hh / 2 + 4, lab, size=10, color=INK))
        yy += hh
    p.append(text(rx + rw / 2, yy + 18, "ще й росте на ходу", size=10,
                  color=MUTED, italic=True))

    p.append(text(W / 2, H - 14,
                  "розмір образу й витрата RAM — різні числа",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "image-vs-ram.svg"), W, H, *p,
           title="Дві різні картини: образ у Flash і RAM у роботі")


# ── size-report: зі секцій постають два числа звіту збірки ─────────────────────
# Ідея: три секції зліва; стрілки зводяться у дві суми — Flash і RAM; .data
# входить в обидві (рахується двічі), .bss — лише в RAM.

def fig_size_report():
    W, H = 720, 320
    p = []
    # секції-джерела
    secs = [(".text  180 КБ", FLASH, 80), (".data    2 КБ", RAM_F, 150),
            (".bss   40 КБ", RAM_F, 220)]
    sx, sw_ = 60, 180
    for lab, fill, yy in secs:
        p.append(fitbox(sx, yy - 22, sw_, 44, lab, size=12, fill=fill,
                        stroke="#bbbbbb", sw=1.3, bold=True, color=INK))
    # дві суми
    fl, flw, flh = textbox(540, 110, "Flash (образ)\n= .text + .data\n= 182 КБ",
                           size=12, fill=FLASH, stroke="#3a5bb8", sw=1.8, color="#3a5bb8", bold=True)
    rm, rmw, rmh = textbox(540, 220, "RAM (у роботі)\n= .data + .bss\n= 42 КБ  (+ стек/купа)",
                           size=12, fill=RAM_F, stroke=FIELD, sw=1.8, color=FIELD, bold=True)
    # стрілки: .text→Flash; .data→обидві; .bss→RAM
    p.append(arrow(sx + sw_ + 4, 80, 540 - flw / 2 - 4, 96, color="#3a5bb8", sw=1.8))
    p.append(arrow(sx + sw_ + 4, 150, 540 - flw / 2 - 4, 122, color=POS, sw=2.0))
    p.append(arrow(sx + sw_ + 4, 152, 540 - rmw / 2 - 4, 206, color=POS, sw=2.0))
    p.append(arrow(sx + sw_ + 4, 220, 540 - rmw / 2 - 4, 226, color=FIELD, sw=1.8))
    p.append(fl); p.append(rm)
    p.append(text(330, 178, ".data — двічі", size=10, color=POS, bold=True))
    p.append(text(W / 2, H - 12,
                  "те саме показує рядок «програмна пам'ять … / динамічна пам'ять …»",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "size-report.svg"), W, H, *p,
           title="Зі секцій — два числа звіту: Flash і RAM")


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури ВСТАВОК (одна figs.py на теку теми, §5)
# ══════════════════════════════════════════════════════════════════════════════

# ── checksum-ladder (math-image-checksums) ────────────────────────────────────
def fig_checksum_ladder():
    W, H = 720, 300
    p = []
    rungs = [
        ("байтова сума (8 біт)", "промах ~ 1/256; дві помилки гасяться", "#fdecea", POS),
        ("CRC (16/32 біт)", "ловить пакетні помилки; промах ~ 1/4 млрд", FLASH, "#3a5bb8"),
        ("криптохеш (128/256 біт)", "будь-яка зміна → інший хеш", RAM_F, FIELD),
    ]
    bw = 560
    x = (W - bw) / 2
    for i, (title, sub, fill, col) in enumerate(rungs):
        yy = 60 + i * 76
        p.append(rect(x, yy, bw, 60, fill=fill, stroke=col, sw=1.8))
        p.append(text(x + 20, yy + 26, title, size=13, bold=True, color=col, anchor="start"))
        p.append(text(x + 20, yy + 46, sub, size=11, color=MUTED, anchor="start"))
        p.append(text(x + bw - 16, yy + 36, "▲ сильніше", size=10, color=col, anchor="end"))
    p.append(text(W / 2, H - 14, "за силу платять часом і пам'яттю — беруть найдешевше, що ловить потрібне",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "checksum-ladder.svg"), W, H, *p,
           title="Драбина сили: байтова сума → CRC → криптохеш")


# ── checksum-verify (math-image-checksums) ────────────────────────────────────
def fig_checksum_verify():
    W, H = 700, 280
    p = []
    a, aw, ah = textbox(160, 110, "образ на ПК\n(надіслали)", size=12, fill=FILL, stroke=INK, sw=1.6)
    b, bw, bh = textbox(540, 110, "образ у Flash\n(прийняли)", size=12, fill=FLASH, stroke="#3a5bb8", sw=1.6)
    p.append(a); p.append(b)
    p.append(arrow(160 + aw / 2, 110, 540 - bw / 2, 110, color=INK, sw=2))
    p.append(text(350, 92, "залили по дроту", size=10, color=MUTED))
    # суми
    p.append(text(160, 180, "сума A", size=12, bold=True, color=INK))
    p.append(text(540, 180, "сума B", size=12, bold=True, color="#3a5bb8"))
    p.append(line(160, 188, 540, 188, color=MUTED, sw=1.4, dash="6 4"))
    eq, ew, eh = textbox(350, 188, "A = B ?", size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8)
    p.append(eq)
    p.append(text(350, 236, "збіглося — цілий · різні — зіпсовано (перезалити)",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, H - 12, "для хешу — лавина: зміна одного біта дає геть інший хеш",
                  size=11, color=POS))
    render(os.path.join(OUT, "checksum-verify.svg"), W, H, *p,
           title="Перевірка: сума надісланого = сумі в чипі?")


# ── version-inject (proj-firmware-version) ────────────────────────────────────
def fig_version_inject():
    W, H = 780, 200
    p = []
    y = 96
    boxes = [
        ("git describe\n--dirty", "#f0e6e6", INK),
        ("configure_file\n→ app_version.h", FILL, INK),
        ("компілятор\n→ .rodata", FLASH, "#3a5bb8"),
        ("лінкер\n→ Flash", RAM_F, FIELD),
        ("старт:\nлог гіт-хеш", "#f6f4ec", INK),
    ]
    bw, gap = 134, 18
    x0 = (W - (bw * len(boxes) + gap * (len(boxes) - 1))) / 2
    cx = []
    for i, (lab, fill, col) in enumerate(boxes):
        x = x0 + i * (bw + gap)
        p.append(fitbox(x, y - 32, bw, 64, lab, size=11, fill=fill, stroke=col, sw=1.6, bold=True, color=col))
        cx.append((x, x + bw))
        if i > 0:
            p.append(arrow(cx[i - 1][1] + 2, y, x - 2, y, color=INK, sw=1.7))
    p.append(text(W / 2, H - 20, "ідентичність ставить інструмент, не людина — забути неможливо",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "version-inject.svg"), W, H, *p,
           title="Шлях git-хешу в образ прошивки")


# ── reproducible-build (proj-firmware-version) ────────────────────────────────
def fig_reproducible_build():
    W, H = 740, 340
    p = []
    src, sw_, sh_ = textbox(W / 2, 70, "git commit abc123  (той самий код)", size=12,
                            bold=True, fill="#f6f4ec", stroke=INK, sw=1.8)
    p.append(src)
    p.append(arrow(W / 2, 70 + sh_ / 2, W / 2, 104, color=INK, sw=1.6))
    p.append(line(180, 104, 560, 104, color=INK, sw=1.6))
    p.append(arrow(180, 104, 180, 124, color=INK, sw=1.7))
    p.append(arrow(560, 104, 560, 124, color=INK, sw=1.7))
    # наївно
    p.append(text(180, 150, "наївно", size=13, bold=True, color=POS))
    bad, bw_, bh_ = textbox(180, 200, "__DATE__/__TIME__\nC:\\Users\\…  (абс. шлях)", size=11,
                            fill="#fdecea", stroke=POS, sw=1.8, color=INK)
    p.append(bad)
    p.append(arrow(180, 200 + bh_ / 2, 180, 252, color=POS, sw=1.7))
    res1, r1w, r1h = textbox(180, 285, "build #1: MD5 3f8a…\nbuild #2: MD5 c91e…\nРІЗНІ .bin", size=11,
                             bold=True, fill="#fdecea", stroke=POS, sw=1.8, color=POS)
    p.append(res1)
    # детерміновано
    p.append(text(560, 150, "детерміновано", size=13, bold=True, color=FIELD))
    good, gw_, gh_ = textbox(560, 200, "SOURCE_DATE_EPOCH\n-ffile-prefix-map", size=11,
                             fill=RAM_F, stroke=FIELD, sw=1.8, color=INK)
    p.append(good)
    p.append(arrow(560, 200 + gh_ / 2, 560, 252, color=FIELD, sw=1.7))
    res2, r2w, r2h = textbox(560, 285, "build #1: MD5 7b4d…\nbuild #2: MD5 7b4d…\nОДНАКОВІ .bin", size=11,
                             bold=True, fill=RAM_F, stroke=FIELD, sw=1.8, color=FIELD)
    p.append(res2)
    p.append(line(W / 2, 130, W / 2, 320, color="#dddddd", sw=1, dash="6 4"))
    render(os.path.join(OUT, "reproducible-build.svg"), W, H, *p,
           title="Однаковий хеш — лише коли збірка детермінована")


# ── map-anatomy (proj-map-file) ───────────────────────────────────────────────
def fig_map_anatomy():
    W, H = 720, 300
    p = []
    # частина 1
    a, aw_, ah_ = textbox(200, 130, "ЗВЕДЕННЯ РОЗМІРІВ\n.text/.data/.bss\n→ Flash чи RAM", size=12,
                          bold=True, fill=FLASH, stroke="#3a5bb8", sw=1.8, color=INK)
    p.append(a)
    p.append(text(200, 200, "чого саме бракує:\nкоду (Flash) чи даних (RAM)", size=10, color=MUTED))
    # частина 2
    b, bw_, bh_ = textbox(520, 130, "ПЕРЕЛІК СИМВОЛІВ\nкожен символ:\nрозмір + звідки", size=12,
                          bold=True, fill=RAM_F, stroke=FIELD, sw=1.8, color=INK)
    p.append(b)
    p.append(text(520, 200, "відсортуй за розміром ↓\n— винний нагорі", size=10, color=MUTED))
    p.append(text(W / 2, H - 14, "лінкер знає про кожен байт усе — за прапорцем -Map виписує це у файл",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "map-anatomy.svg"), W, H, *p,
           title="Дві частини map-файлу: бюджет і винний")


# ── map-budget (proj-map-file) ────────────────────────────────────────────────
def fig_map_budget():
    W, H = 720, 300
    p = []
    # дві скриньки
    p.append(rect(60, 70, 260, 150, fill=FLASH, stroke="#3a5bb8", sw=2))
    p.append(text(190, 96, "Flash = .text + .data", size=13, bold=True, color="#3a5bb8"))
    p.append(text(190, 116, "код + початкові значення", size=10, color=MUTED))
    p.append(rect(400, 70, 260, 150, fill=RAM_F, stroke=FIELD, sw=2))
    p.append(text(530, 96, "RAM = .data + .bss", size=13, bold=True, color=FIELD))
    p.append(text(530, 116, "змінні (з нулями й без)", size=10, color=MUTED))
    # типові ненажери
    flash_eat = ["велика const-таблиця", "жирна бібліотека", "printf із %f"]
    ram_eat = [".data / .bss буфери", "великий глобальний буфер"]
    for i, lab in enumerate(flash_eat):
        p.append(fitbox(80, 138 + i * 26, 220, 22, lab, size=10, fill="#ffffff", stroke="#c9d6f0", sw=1.1))
    for i, lab in enumerate(ram_eat):
        p.append(fitbox(420, 144 + i * 30, 220, 24, lab, size=10, fill="#ffffff", stroke=RAM_S, sw=1.1))
    p.append(text(W / 2, H - 14, "переповнився Flash → шукай у .text; бракує RAM → у .bss і .data",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "map-budget.svg"), W, H, *p,
           title="Дві скриньки пам'яті й хто їх переповнює")


# ── size-levers (proj-size-opt) ───────────────────────────────────────────────
def fig_size_levers():
    W, H = 740, 280
    p = []
    levers = [
        ("-Os", "компілятор обирає\nкомпактний код", "жме .text", FLASH, "#3a5bb8"),
        ("gc-sections", "лінкер викидає\nсекції без посилань", "вирізає невжите", RAM_F, FIELD),
        ("LTO", "оптимізація крізь\nмежі файлів", "чистить наскрізь", RO_F, POS),
    ]
    bw, gap = 210, 24
    x0 = (W - (bw * 3 + gap * 2)) / 2
    for i, (name, what, eff, fill, col) in enumerate(levers):
        x = x0 + i * (bw + gap)
        p.append(rect(x, 60, bw, 180, fill=fill, stroke=col, sw=2))
        p.append(text(x + bw / 2, 92, name, size=16, bold=True, color=col))
        p.append(mtext(x + bw / 2, 124, what, size=12, color=INK))
        p.append(text(x + bw / 2, 200, eff, size=11, bold=True, color=col))
    p.append(text(W / 2, H - 12, "три незалежні механізми; вмикати можна разом, розуміти — окремо",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "size-levers.svg"), W, H, *p,
           title="Три важелі стиснення образу: -Os, gc-sections, LTO")


# ── size-measure-verify (proj-size-opt) ───────────────────────────────────────
def fig_size_measure_verify():
    W, H = 720, 300
    cx, cy, r = W / 2, 150, 96
    p = []
    nodes = [
        (cx, cy - r, "увімкни ОДИН\nважіль", FLASH, "#3a5bb8"),
        (cx + r, cy, "глянь size/map\n(скільки й де)", RAM_F, FIELD),
        (cx, cy + r, "залий і перевір:\nробить те саме?", RO_F, POS),
        (cx - r, cy, "лише тоді\nнаступний", FILL, INK),
    ]
    pts = []
    for nx, ny, lab, fill, col in nodes:
        b, bw_, bh_ = textbox(nx, ny, lab, size=11, bold=True, fill=fill, stroke=col, sw=1.7, color=col)
        pts.append((nx, ny))
        p.append(b)
    # стрілки по колу
    order = [(0, 1), (1, 2), (2, 3), (3, 0)]
    for a, b in order:
        x1, y1 = pts[a]; x2, y2 = pts[b]
        dx, dy = x2 - x1, y2 - y1
        import math as _m
        d = _m.hypot(dx, dy)
        ox, oy = dx / d, dy / d
        p.insert(0, arrow(x1 + ox * 54, y1 + oy * 30, x2 - ox * 60, y2 - oy * 30, color=MUTED, sw=1.6))
    p.append(text(cx, cy + 4, "петля, не\nодин постріл", size=11, color=MUTED, italic=True))
    p.append(text(W / 2, H - 12, "мета — найменший образ, що ДОСІ ПРАЦЮЄ",
                  size=12, bold=True, color=POS))
    render(os.path.join(OUT, "size-measure-verify.svg"), W, H, *p,
           title="Дисципліна стиснення: важіль → міра → перевірка")


if __name__ == "__main__":
    # фігури статті
    fig_why_sections()
    fig_three_sections()
    fig_data_bss_twist()
    fig_startup_copy()
    fig_elf_to_bin()
    fig_image_vs_ram()
    fig_size_report()
    # фігури вставок
    fig_checksum_ladder()
    fig_checksum_verify()
    fig_version_inject()
    fig_reproducible_build()
    fig_map_anatomy()
    fig_map_budget()
    fig_size_levers()
    fig_size_measure_verify()
    print("OK: figures written to", OUT)
