# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Родина Arduino».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Дві речі під назвою «Arduino»: залізо (плати) vs фреймворк (софт) ───────
def fig_two_meanings():
    W, H = 940, 560
    f = [text(W / 2, 30, "Одне слово «Arduino» — два різні шари", size=16, bold=True)]

    # Верхній пояс: ФРЕЙМВОРК (спільна мова коду) — тягнеться на всю ширину
    fw_x, fw_y, fw_w, fw_h = 90, 70, 760, 96
    f.append(rect(fw_x, fw_y, fw_w, fw_h, fill="#eef2f8", stroke=NEG, sw=2.0, rx=12))
    f.append(text(fw_x + fw_w / 2, fw_y + 26, "ФРЕЙМВОРК Arduino  (софт)",
                  size=14, bold=True, color=NEG))
    f.append(text(fw_x + fw_w / 2, fw_y + 50,
                  "мова = C++ · середовище (IDE) · бібліотеки: digitalWrite(), analogRead(), Serial",
                  size=10.5, color=INK))
    f.append(text(fw_x + fw_w / 2, fw_y + 72,
                  "модель setup() / loop() — той самий скетч для будь-якого сумісного заліза",
                  size=10.5, color=MUTED))

    # Дві колонки заліза внизу; спільна мова спускається в обидві
    col_y = 250
    col_h = 210

    # ЛІВА колонка — власні плати Arduino (AVR)
    lx, lw = 110, 320
    f.append(rect(lx, col_y, lw, col_h, fill="#eef6ef", stroke=FIELD, sw=2.0, rx=12))
    f.append(text(lx + lw / 2, col_y + 26, "Власні плати Arduino  (залізо)",
                  size=13, bold=True, color=FIELD))
    f.append(text(lx + lw / 2, col_y + 48, "чипи AVR від Atmel / Microchip",
                  size=10.5, color=MUTED))
    for i, (name, chip) in enumerate([("UNO · Nano", "ATmega328P"),
                                      ("Mega", "ATmega2560"),
                                      ("Leonardo", "ATmega32U4")]):
        yy = col_y + 78 + i * 40
        f.append(rect(lx + 24, yy, lw - 48, 30, fill=BG, stroke=FIELD, sw=1.4, rx=7))
        f.append(text(lx + 42, yy + 20, name, size=10.5, bold=True, color=INK, anchor="start"))
        f.append(text(lx + lw - 42, yy + 20, chip, size=10, color=MUTED, anchor="end"))

    # ПРАВА колонка — чуже залізо, сумісне через ядро-перекладач
    rx, rw = 510, 320
    f.append(rect(rx, col_y, rw, col_h, fill="#fdf4ea", stroke=POS, sw=2.0, rx=12))
    f.append(text(rx + rw / 2, col_y + 26, "Чуже залізо «сумісне з Arduino»",
                  size=13, bold=True, color=POS))
    f.append(text(rx + rw / 2, col_y + 48, "плати ESP32 / ESP8266 від Espressif",
                  size=10.5, color=MUTED))
    for i, (name, chip) in enumerate([("ESP32-CAM · S3", "Xtensa / RISC-V"),
                                      ("ESP-01 (ESP8266)", "Tensilica L106"),
                                      ("…тисячі інших", "не-AVR ядро")]):
        yy = col_y + 78 + i * 40
        f.append(rect(rx + 24, yy, rw - 48, 30, fill=BG, stroke=POS, sw=1.4, rx=7))
        f.append(text(rx + 42, yy + 20, name, size=10.5, bold=True, color=INK, anchor="start"))
        f.append(text(rx + rw - 42, yy + 20, chip, size=10, color=MUTED, anchor="end"))

    # мова спускається з фреймворку в обидві колонки; стрілки — збоку від колонки,
    # підписи — з іншого боку від стрілки, щоб лінія НЕ перетинала напис
    lcx = lx + lw / 2
    rcx = rx + rw / 2
    mid_y = (fw_y + fw_h + col_y) / 2
    la_x = lx + 60          # стрілка лівої колонки — ближче до лівого краю
    ra_x = rx + 60          # стрілка правої колонки — ближче до лівого краю
    f.append(arrow(la_x, fw_y + fw_h, la_x, col_y, color=NEG, sw=2.0))
    f.append(arrow(ra_x, fw_y + fw_h, ra_x, col_y, color=NEG, sw=2.0))
    # ліворуч: короткий підпис праворуч від стрілки
    f.append(text(la_x + 14, mid_y + 4, "рідне ядро", size=9.5, color=NEG,
                  bold=True, anchor="start"))
    # праворуч: рамка-підпис праворуч від стрілки (у своїй рамці — це норма)
    b, bw, _ = textbox(ra_x + 150, mid_y,
                       "ядро-перекладач\n(Arduino core для ESP)",
                       size=9.5, fill="#eef2f8", stroke=NEG)
    f.append(b)

    # нижня рамка-висновок
    b2, _, _ = textbox(W / 2, 528,
                       "«плата Arduino» = залізо від Arduino;  «сумісна з Arduino» = чуже залізо + той самий фреймворк",
                       size=11, fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "two-meanings.svg"), W, H, *f)


# ── 2. Мапа родини плат: класична 8-біт AVR vs сучасна 32-біт ARM ─────────────
def fig_family_map():
    W, H = 940, 560
    f = [text(W / 2, 30, "Дерево родини Arduino: дві гілки за розрядністю й логікою",
              size=16, bold=True)]

    # корінь
    f.append(rect(W / 2 - 95, 56, 190, 40, fill=FILL, stroke=INK, sw=2.0, rx=10))
    f.append(text(W / 2, 81, "Родина Arduino", size=13, bold=True))

    # дві гілки
    def branch(cx, title, sub, accent, fill, boards):
        bx, bw = cx - 190, 380
        by, bh = 150, 340
        f.append(rect(bx, by, bw, bh, fill=fill, stroke=accent, sw=2.0, rx=12))
        f.append(text(cx, by + 28, title, size=13.5, bold=True, color=accent))
        f.append(text(cx, by + 50, sub, size=10.5, color=MUTED))
        # лінія від кореня до гілки
        f.append(line(W / 2, 96, cx, by, color=accent, sw=2.0))
        for i, (name, chip, note) in enumerate(boards):
            yy = by + 74 + i * 62
            f.append(rect(bx + 22, yy, bw - 44, 50, fill=BG, stroke=accent, sw=1.5, rx=8))
            f.append(text(bx + 40, yy + 21, name, size=11.5, bold=True, color=INK, anchor="start"))
            f.append(text(bx + bw - 40, yy + 21, chip, size=10.5, color=accent,
                          anchor="end", bold=True))
            f.append(text(bx + 40, yy + 39, note, size=9.5, color=MUTED, anchor="start"))

    branch(285, "Класична гілка", "8-бітна · AVR · логіка 5 В", FIELD, "#eef6ef", [
        ("UNO / Nano", "ATmega328P", "32 КБ флеш · 16 МГц · старт сюди"),
        ("Mega", "ATmega2560", "багато виводів · 256 КБ флеш"),
        ("Leonardo / Micro", "ATmega32U4", "чип сам уміє USB (HID)"),
    ])
    branch(655, "Сучасна гілка", "32-бітна · ARM · логіка 3.3 В", NEG, "#eef2f8", [
        ("Due", "SAM3X8E", "Cortex-M3 · 84 МГц · швидша"),
        ("MKR-серія", "SAMD Cortex-M0+", "компактна · часто з радіо"),
        ("Nano 33", "M0+ / nRF", "Wi-Fi / BLE на борту"),
    ])

    # застереження про вольти між гілками
    b, _, _ = textbox(W / 2, 525,
                      "ПАСТКА переходу: класична — 5 В, сучасна — 3.3 В; подати 5 В на піни 3.3-вольтової плати = псуєш її",
                      size=11, fill="#fdecea", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "family-map.svg"), W, H, *f)


# ── 3. Що дозволяє відкрита ліцензія: копіювати схему — так, бренд — ні ────────
def fig_license_line():
    W, H = 940, 380
    f = [text(W / 2, 32, "Відкрите залізо: де межа дозволеного", size=16, bold=True)]

    # ЛІВА половина — ВІЛЬНО (схема, файли, код під відкритою ліцензією)
    lx, lw, ty, th = 70, 400, 74, 250
    f.append(rect(lx, ty, lw, th, fill="#eef6ef", stroke=FIELD, sw=2.0, rx=12))
    f.append(text(lx + lw / 2, ty + 30, "ВІЛЬНО — під ліцензією", size=14, bold=True, color=FIELD))
    for i, s in enumerate([
        "узяти схему й розводку плати (файли Eagle)",
        "виготовити свою плату 1-в-1",
        "продавати її, змінювати, вбудовувати",
        "узяти код IDE та бібліотек, форкнути"]):
        yy = ty + 66 + i * 42
        f.append(circle(lx + 34, yy - 4, 9, fill=BG, stroke=FIELD, sw=2))
        f.append(text(lx + 34, yy + 1, "✓", size=12, color=FIELD, bold=True))
        f.append(text(lx + 56, yy, s, size=11, color=INK, anchor="start"))

    # ПРАВА половина — НЕ МОЖНА (бренд, логотип, назва)
    rx, rw = 490, 380
    f.append(rect(rx, ty, rw, th, fill="#fdecea", stroke=POS, sw=2.0, rx=12))
    f.append(text(rx + rw / 2, ty + 30, "НЕ МОЖНА — це торгова марка", size=14, bold=True, color=POS))
    for i, s in enumerate([
        "назвати свою плату «Arduino»",
        "ставити на неї логотип-нескінченність (∞)",
        "видавати клон за офіційний виріб",
        "торгувати під чужим брендом"]):
        yy = ty + 66 + i * 42
        f.append(circle(rx + 34, yy - 4, 9, fill=BG, stroke=POS, sw=2))
        f.append(text(rx + 34, yy + 1, "✕", size=12, color=POS, bold=True))
        f.append(text(rx + 56, yy, s, size=11, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, 356,
                      "тому клони звуться «Arduino-compatible / для Arduino», а не просто «Arduino»",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "license-line.svg"), W, H, *f)


# ── 4. Хроніка суперечки за марку: одне ім'я → дві компанії → знову одна ───────
def fig_split_timeline():
    W, H = 960, 620
    f = [text(W / 2, 32, "Роздвоєння й повернення бренду Arduino", size=16, bold=True)]

    ax = 150               # вісь часу (вертикальна)
    top, bot = 74, 556
    f.append(line(ax, top, ax, bot, color=INK, sw=2.5))

    def node(y, year, txt, accent, side="right", lines=None):
        f.append(circle(ax, y, 7, fill=accent, stroke=BG, sw=2))
        f.append(text(ax - 20, y + 5, year, size=12, bold=True, color=accent, anchor="end"))
        body = txt if lines is None else txt
        b, bw, bh = textbox(ax + 24 + 250, y, body, size=10.5, fill="#f7f9fb",
                            stroke=accent, min_w=470)
        f.append(b)

    node(96,  "2005", "IDII, Іврея: пʼятеро роблять Arduino;\nсхеми й код одразу відкриті", FIELD)
    node(168, "2008", "Arduino LLC (США) тримає марку · Smart Projects\nМартіно тихо реєструє «Arduino» в Італії", NEG)
    node(240, "2014", "жовтень: Smart Projects → «Arduino SRL»,\nсайт arduino.org; заявка в USPTO скасувати марку LLC", POS)
    node(312, "2015", "січень: Arduino LLC судиться з Arduino SRL ·\nпоза США LLC торгує під іменем «Genuino»", POS)
    node(384, "2016", "Maker Faire (жовтень): мир — злиття\nдвох фірм у єдину Arduino AG", NEG)
    node(456, "2017", "липень: BCMI (Банці, Куартьєльєс,\nМелліс, Іго) викуповує 100% Arduino AG", FIELD)
    node(528, "нині", "одна компанія, один бренд;\nвідкриті ліцензії лишились — клони живуть", INK)

    render(os.path.join(IMG, "split-timeline.svg"), W, H, *f)


# ── 5. Дуга правління Ардуїна Іврейського: злет 1002 → крах 1004 → зречення 1014
def fig_arduin_timeline():
    W, H = 940, 470
    f = [text(W / 2, 30, "Ардуїн Іврейський: дуга короля-невдахи (1002–1015)",
              size=16, bold=True)]

    # горизонтальна вісь часу
    ax0, ax1 = 90, 850
    axis_y = 250
    yr0, yr1 = 1000, 1016  # діапазон років на осі

    def X(year):
        return ax0 + (year - yr0) / (yr1 - yr0) * (ax1 - ax0)

    f.append(line(ax0, axis_y, ax1, axis_y, color=INK, sw=2.0))
    f.append(arrow(ax1 - 2, axis_y, ax1 + 10, axis_y, color=INK, sw=2.0))
    # позначки років на осі (роки-віхи — під віссю, з запасом)
    for yr in (1002, 1004, 1014, 1015):
        f.append(line(X(yr), axis_y - 5, X(yr), axis_y + 5, color=INK, sw=1.6))
    f.append(text(X(1002), axis_y + 24, "1002", size=11, bold=True, color=MUTED))
    # 1004 має повідець-пунктир униз (до нижньої рамки) рівно на своєму x,
    # тож рік підписуємо ЗБОКУ від тієї лінії, щоб вона не перетинала напис.
    f.append(text(X(1004) + 20, axis_y + 24, "1004", size=11, bold=True,
                  color=MUTED, anchor="start"))
    f.append(text(X(1014), axis_y + 24, "1014", size=11, bold=True, color=MUTED))

    # смуга «фактичного тримання влади» 1002–1014 — десятиліття чіпляння за край.
    # Кладемо ПІД роками-підписами (нижче ~274), щоб вісь і написи її НЕ перетинали.
    band_y = 296
    f.append(rect(X(1002), band_y, X(1014) - X(1002), 22,
                  fill="#eef6ef", stroke=FIELD, sw=1.4, rx=6))
    f.append(text((X(1002) + X(1014)) / 2, band_y + 15,
                  "фактично тримає північ Італії ~12 років",
                  size=9.5, color=FIELD, bold=True))

    # ── подія-віха: рамку малюю сам (accent-заголовок + INK-підпис), повідець
    #    зупиняється РІВНО біля зовнішнього краю рамки — крізь текст не проходить ──
    def beat(year, title, sub, accent, box_top, above):
        x = X(year)
        fs = 9.5
        bw = max(text_width(title, fs, True), text_width(sub, fs)) + 20
        bh = 2 * fs * 1.3 + 14
        bx, by = x - bw / 2, box_top
        # повідець від осі до краю рамки (по вертикалі), не заходить у рамку
        if above:      # рамка над віссю → лінія від осі вгору до низу рамки
            f.append(line(x, axis_y - 11, x, by + bh, color=accent, sw=1.4, dash="3,3"))
        else:          # рамка під віссю → лінія від осі вниз до верху рамки
            f.append(line(x, axis_y + 11, x, by, color=accent, sw=1.4, dash="3,3"))
        f.append(rect(bx, by, bw, bh, fill=BG, stroke=accent, sw=1.5, rx=6))
        f.append(text(x, by + 16, title, size=fs, bold=True, color=accent))
        f.append(text(x, by + 16 + fs * 1.3, sub, size=fs, color=INK))
        f.append(circle(x, axis_y, 6, fill=accent, stroke=BG, sw=2))

    # верхній ряд: злет (ліворуч) і зречення (праворуч) — не перетнуться
    beat(1002, "Коронація в Павії", "1002 · король Італії", FIELD, box_top=96, above=True)
    beat(1014, "Зречення 1014", "іде в монастир", MUTED, box_top=96, above=True)
    # нижній ряд: крах — посередині, окремим поясом під віссю
    beat(1004, "Приходить Генріх II", "палить Павію, король сам", POS, box_top=360, above=False)

    # смерть — маленька позначка праворуч, без рамки (щоб не тіснити 1014)
    f.append(circle(X(1015), axis_y, 5, fill=INK, stroke=BG, sw=1.6))
    f.append(text(X(1015) + 6, axis_y - 12, "†1015", size=9.5, color=INK,
                  bold=True, anchor="start"))

    # нижня рамка-мораль
    b2, _, _ = textbox(W / 2, 448,
                       "виграв битву проти намісника, та програв корону самому імператору — "
                       "«гідний невдаха», якого Іврея памʼятає тисячу років",
                       size=11, fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "arduin-timeline.svg"), W, H, *f)


# ── 6. Ланцюг збірки: .ino → препроцесор → avr-gcc → linker → .hex → avrdude ──
def fig_build_chain():
    W, H = 940, 640
    f = [text(W / 2, 30, "Ланцюг збірки: від тексту скетчу до байтів у флеші чипа",
              size=16, bold=True)]

    cx = W / 2
    bw = 600
    bx = cx - bw / 2

    # П'ять сходинок на ПК
    steps = [
        ("твій скетч  .ino", "звичайний C++ у дірах setup() / loop()", "#eef2f8", NEG),
        ("препроцесор скетчів",
         "склеїти .ino · вставити #include <Arduino.h> · дописати прототипи → .cpp",
         "#eef2f8", NEG),
        ("компілятор  avr-gcc  (крос-компілятор)",
         "GCC на твоєму ПК → машинний код під набір інструкцій AVR",
         "#eef6ef", FIELD),
        ("компонувальник  (linker)",
         "склеїти твій код + ядро Arduino + бібліотеки → адреси стрибків",
         "#eef6ef", FIELD),
        ("образ  .hex",
         "точні байти для флешу: адреси плюс контрольні суми",
         "#fdf4ea", POS),
    ]
    y0 = 62
    step_h = 62
    gap = 28
    ys = []
    for i, (title, sub, fill, accent) in enumerate(steps):
        yy = y0 + i * (step_h + gap)
        ys.append(yy)
        f.append(rect(bx, yy, bw, step_h, fill=fill, stroke=accent, sw=2.0, rx=10))
        f.append(text(cx, yy + 25, title, size=12.5, bold=True, color=accent))
        f.append(text(cx, yy + 46, sub, size=9.8, color=INK))
        if i > 0:
            f.append(arrow(cx, ys[i - 1] + step_h, cx, yy, color=INK, sw=2.0))

    # Пунктирна межа «ПК ↔ плата»; підписи — ліворуч від стовпчика, повз лінії
    boundary_y = ys[-1] + step_h + gap / 2
    f.append(line(bx - 30, boundary_y, bx + bw + 30, boundary_y,
                  color=MUTED, sw=1.4, dash="6 5"))
    f.append(text(bx - 36, boundary_y - 6, "на твоєму ПК", size=9.5, color=MUTED,
                  anchor="end", italic=True))
    f.append(text(bx - 36, boundary_y + 15, "у платі (по USB)", size=9.5, color=MUTED,
                  anchor="end", italic=True))

    # Остання сходинка — avrdude на платі
    ay = ys[-1] + step_h + gap
    f.append(arrow(cx, ys[-1] + step_h, cx, ay, color=INK, sw=2.0))
    f.append(rect(bx, ay, bw, step_h, fill=FILL, stroke=INK, sw=2.0, rx=10))
    f.append(text(cx, ay + 25, "avrdude  —  заливач по USB", size=12.5, bold=True, color=INK))
    f.append(text(cx, ay + 46,
                  "шле байти в послідовний порт → їх ловить завантажувач, зашитий у чипі",
                  size=9.8, color=INK))

    render(os.path.join(IMG, "build-chain.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_meanings()
    fig_family_map()
    fig_license_line()
    fig_split_timeline()
    fig_arduin_timeline()
    fig_build_chain()
    print("OK: 6 figures ->", IMG)
