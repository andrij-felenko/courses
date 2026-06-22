# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── what-is-rtos: крихітне ядро з готовими засобами багатозадачності ───────────
# Ідея: RTOS — не настільна ОС, а маленький набір цеглинок поверх голого чипа.

def fig_what_is_rtos():
    W, H = 760, 360
    p = []
    # рамка-ядро
    bx, by, bw, bh = 70, 70, W - 140, 200
    p.append(rect(bx, by, bw, bh, fill="#eef4ff", stroke=NEG, sw=2, rx=12))
    p.append(text(W / 2, by + 26, "ядро RTOS", size=13, color=NEG, bold=True))

    cells = [
        ("задачі", "кілька програм нараз", FIELD, "#eafaf0"),
        ("планувальник", "хто й коли", POS, "#fdecea"),
        ("час", "тіки, паузи", "#b07d2a", "#fdf6e3"),
        ("обмін", "черги, семафори", "#8a5fb0", "#f2ecf8"),
        ("пам'ять", "стеки задач", "#2aa198", "#e6f6f4"),
    ]
    cw, chh = 188, 60
    gx, gy = 100, 110
    pos = [(gx, gy), (gx + 220, gy), (gx + 440, gy),
           (gx + 110, gy + 86), (gx + 330, gy + 86)]
    for (lab, sub, col, fill), (x, y) in zip(cells, pos):
        p.append(rect(x, y, cw, chh, fill=fill, stroke=col, sw=1.6))
        p.append(text(x + cw / 2, y + 26, lab, size=12, color=col, bold=True))
        p.append(text(x + cw / 2, y + 45, sub, size=10, color=MUTED))

    # підвал: не настільна ОС
    fy = by + bh + 24
    p.append(fitbox(bx, fy, bw, 50,
                    "не велика настільна ОС: ні файлів, ні вікон — крихітний набір,\n"
                    "що перетворює голий чип на багатозадачну систему",
                    size=11, fill="#fff6e0", stroke="#caa24a", sw=1.4, color=INK))

    render(os.path.join(OUT, "what-is-rtos.svg"), W, H, *p,
           title="RTOS — невелике ядро з готовими засобами багатозадачності")


# ── freertos: коротка історія + воно вже в ESP32 ──────────────────────────────
# Ідея: стрічка ~2003 → 2017 і головне — у ESP32 ядро вже працює (loop = задача).

def fig_freertos():
    W, H = 740, 300
    p = []
    # стрічка часу
    y = 90
    p.append(line(70, y, W - 70, y, color=INK, sw=2))
    marks = [
        (140, "~2003", "Річард Беррі\nстворив FreeRTOS"),
        (370, "2017", "Amazon (AWS)\nстюардство, MIT"),
        (W - 150, "тепер", "у кожному ESP32\nвже вбудовано"),
    ]
    for x, top, sub in marks:
        p.append(circle(x, y, 6, fill=NEG, stroke=NEG, sw=1.5))
        p.append(text(x, y - 16, top, size=12, color=INK, bold=True))
        p.append(mtext(x, y + 24, sub, size=10, color=MUTED))

    # нижня рамка: що це для нас
    bx, by, bw, bh = 90, 180, W - 180, 86
    p.append(rect(bx, by, bw, bh, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(W / 2, by + 26, "головне для нас", size=12, color=FIELD, bold=True))
    p.append(mtext(W / 2, by + 50,
                   "Arduino на ESP32 сам збудований поверх FreeRTOS:\n"
                   "ваш loop() — це задача loopTask, а xTaskCreate і vTaskDelay — її виклики",
                   size=11, color=INK))

    render(os.path.join(OUT, "freertos.svg"), W, H, *p,
           title="FreeRTOS — крихітне вільне ядро, що вже працює у вашому ESP32")


# ── two-cores: два процесорні ядра ESP32 ──────────────────────────────────────
# Ідея: PRO_CPU тягне радіо, APP_CPU — ваш код; обидва під одним ядром FreeRTOS.

def fig_two_cores():
    W, H = 720, 340
    p = []
    cw, chh = 280, 150
    y = 80
    x0, x1 = 70, W - 70 - cw

    # Ядро 0
    p.append(rect(x0, y, cw, chh, fill="#fdecea", stroke=POS, sw=2, rx=12))
    p.append(text(x0 + cw / 2, y + 28, "Ядро 0 — PRO_CPU", size=13, color=POS, bold=True))
    p.append(mtext(x0 + cw / 2, y + 60,
                   "«протокольне»\nза умовчанням: Wi-Fi і Bluetooth\n(усе радіо)",
                   size=11, color=INK))

    # Ядро 1
    p.append(rect(x1, y, cw, chh, fill="#eafaf0", stroke=FIELD, sw=2, rx=12))
    p.append(text(x1 + cw / 2, y + 28, "Ядро 1 — APP_CPU", size=13, color=FIELD, bold=True))
    p.append(mtext(x1 + cw / 2, y + 60,
                   "«застосункове»\nза умовчанням: ваші setup() і loop()\n(код скетчу)",
                   size=11, color=INK))

    # обидва під одним FreeRTOS
    by = y + chh + 22
    p.append(fitbox(x0, by, W - 140, 44, "обидва працюють під одним ядром FreeRTOS",
                    size=12, fill="#eef4ff", stroke=NEG, sw=1.6, color=NEG, bold=True))
    p.append(text(W / 2, by + 76, "не всі ESP32 такі: S2 і C3 — одноядерні",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-cores.svg"), W, H, *p,
           title="ESP32 має два процесорні ядра: PRO_CPU і APP_CPU")


# ── illusion-vs-real: одне ядро (по черзі) проти двох (водночас) ───────────────
# Ідея: ліворуч одне ядро тасує задачі в часі; праворуч два ядра біжать паралельно.

def fig_illusion_vs_real():
    W, H = 740, 320
    p = []
    # ── ліва панель: одне ядро, смужки в часі по черзі
    lx = 60
    p.append(text(lx + 130, 64, "одне ядро: ілюзія по черзі", size=12, color=POS, bold=True, anchor="middle"))
    track_y = 100
    p.append(line(lx, track_y, lx + 260, track_y, color=INK, sw=1.6))
    p.append(text(lx - 8, track_y + 4, "час", size=10, color=MUTED, anchor="end"))
    seg = 260 / 6
    cols = [FIELD, POS, FIELD, POS, FIELD, POS]
    labs = ["A", "B", "A", "B", "A", "B"]
    for i in range(6):
        x = lx + i * seg
        p.append(rect(x, track_y + 8, seg - 3, 30, fill="#eef4ff" if cols[i] == NEG else
                      ("#eafaf0" if cols[i] == FIELD else "#fdecea"),
                      stroke=cols[i], sw=1.4, rx=4))
        p.append(text(x + seg / 2 - 1, track_y + 28, labs[i], size=11, color=cols[i], bold=True))
    p.append(text(lx + 130, track_y + 64, "лише одна задача в кожну мить", size=10, color=MUTED, italic=True, anchor="middle"))

    # ── права панель: два ядра, дві смуги водночас
    rx = 420
    p.append(text(rx + 130, 64, "два ядра: справжня паралельність", size=12, color=FIELD, bold=True, anchor="middle"))
    for k, (lab, col, fill) in enumerate([("Ядро 0: радіо", POS, "#fdecea"),
                                          ("Ядро 1: ваш код", FIELD, "#eafaf0")]):
        ty = 96 + k * 50
        p.append(rect(rx, ty, 260, 36, fill=fill, stroke=col, sw=1.6, rx=6))
        p.append(text(rx + 130, ty + 23, lab, size=11, color=col, bold=True))
    p.append(text(rx + 130, 96 + 2 * 50 + 18, "обидві задачі — в ту саму мить",
                  size=10, color=MUTED, italic=True, anchor="middle"))

    # роздільник
    p.append(line(W / 2 - 8, 56, W / 2 - 8, 240, color="#d0d0d0", sw=1.2, dash="4 4"))
    p.append(text(W / 2, 276, "на кожному ядрі діє той самий пріоритетно-витісняючий планувальник",
                  size=11, color=INK, anchor="middle"))

    render(os.path.join(OUT, "illusion-vs-real.svg"), W, H, *p,
           title="Одне ядро — ілюзія по черзі; два ядра — справжня паралельність")


# ── pinning: прив'язка задачі до ядра ─────────────────────────────────────────
# Ідея: xTaskCreatePinnedToCore = xTaskCreate + номер ядра; типовий поділ праці.

def fig_pinning():
    W, H = 740, 300
    p = []
    # підпис виклику
    p.append(text(W / 2, 64, "xTaskCreatePinnedToCore(  …  , coreID)",
                  size=14, color=INK, bold=True))
    p.append(text(W / 2, 84, "як xTaskCreate, лише з номером ядра наприкінці",
                  size=11, color=MUTED, italic=True))

    # три варіанти номера
    boxes = [
        (160, "0", "радіо й мережа", POS, "#fdecea"),
        (W / 2, "1", "ваша важлива робота", FIELD, "#eafaf0"),
        (W - 160, "tskNO_AFFINITY", "вибір — планувальникові", NEG, "#eef4ff"),
    ]
    y = 150
    for cx, num, sub, col, fill in boxes:
        b, bw, bh = textbox(cx, y, num, size=14, bold=True, color=col, fill=fill, stroke=col, sw=1.8, pad=14, min_w=90)
        p.append(b)
        p.append(text(cx, y + bh / 2 + 22, sub, size=11, color=INK))

    p.append(fitbox(120, 232, W - 240, 46,
                    "типовий поділ: радіо — на Ядрі 0, точне керування — на Ядрі 1,\n"
                    "тож вони не заважають одне одному",
                    size=11, fill="#fff6e0", stroke="#caa24a", sw=1.4, color=INK))

    render(os.path.join(OUT, "pinning.svg"), W, H, *p,
           title="Прив'язування задачі до ядра")


# ── shared-harder: дві задачі на двох ядрах псують спільну змінну ──────────────
# Ідея: на двох ядрах доступ до однієї комірки справді одночасний → гонка.

def fig_shared_harder():
    W, H = 720, 300
    p = []
    # дві задачі
    p.append(rect(70, 90, 220, 54, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    p.append(text(180, 114, "задача на Ядрі 0", size=12, color=POS, bold=True))
    p.append(text(180, 132, "пише x", size=11, color=INK))

    p.append(rect(W - 290, 90, 220, 54, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(W - 180, 114, "задача на Ядрі 1", size=12, color=FIELD, bold=True))
    p.append(text(W - 180, 132, "пише x", size=11, color=INK))

    # спільна комірка
    cx, cy = W / 2, 220
    b, bw, bh = textbox(cx, cy, "x", size=18, bold=True, fill="#f4f6f8", stroke=INK, sw=2, pad=16, min_w=90)
    p.append(b)
    p.append(text(cx, cy + bh / 2 + 20, "спільна змінна", size=11, color=MUTED))

    # стрілки в ту саму мить
    p.append(arrow(180, 144, cx - bw / 2 - 6, cy - bh / 2 - 6, color=POS, sw=2))
    p.append(arrow(W - 180, 144, cx + bw / 2 + 6, cy - bh / 2 - 6, color=FIELD, sw=2))
    p.append(text(cx, 168, "в ту саму мить", size=12, color="#c0392b", bold=True))

    p.append(text(W / 2, H - 18, "значення псується (гонка) — спільні дані конче треба захищати",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "shared-harder.svg"), W, H, *p,
           title="Два ядра можуть зіпсувати спільну змінну одночасно")


# ── core-map: що за умовчанням лежить на кожному ядрі (для comp-вставки) ───────
# Ідея: дві колонки реальних мешканців ядер + дві виноски про тонкощі.

def fig_core_map():
    W, H = 740, 380
    p = []
    cw = 300
    x0, x1 = 60, W - 60 - cw
    y, chh = 70, 184

    # Ядро 0
    p.append(rect(x0, y, cw, chh, fill="#fdecea", stroke=POS, sw=2, rx=12))
    p.append(text(x0 + cw / 2, y + 26, "Ядро 0 — PRO_CPU", size=13, color=POS, bold=True))
    for i, ln in enumerate(["Wi-Fi / BT-стек", "ipc0 (міжядерні виклики)",
                            "esp_timer, Tmr Svc", "обробники драйверів", "IDLE0"]):
        p.append(text(x0 + cw / 2, y + 56 + i * 24, ln, size=11, color=INK))

    # Ядро 1
    p.append(rect(x1, y, cw, chh, fill="#eafaf0", stroke=FIELD, sw=2, rx=12))
    p.append(text(x1 + cw / 2, y + 26, "Ядро 1 — APP_CPU", size=13, color=FIELD, bold=True))
    for i, ln in enumerate(["loopTask: setup() / loop()", "(пріоритет 1)",
                            "ваші незакріплені задачі", "(xTaskCreate без Pinned)", "IDLE1"]):
        p.append(text(x1 + cw / 2, y + 56 + i * 24, ln, size=11, color=INK))

    # дві виноски
    fy = y + chh + 20
    p.append(fitbox(x0, fy, cw, 52,
                    "1) незакріплена xTaskCreate →\nядро творця (зазвичай Ядро 1),\nа не автобаланс",
                    size=10, fill="#fff6e0", stroke="#caa24a", sw=1.3, color=INK))
    p.append(fitbox(x1, fy, cw, 52,
                    "2) переривання драйвера прилипає\nдо ядра, де викликали install\n(Wire.begin, attachInterrupt…)",
                    size=10, fill="#eef4ff", stroke=NEG, sw=1.3, color=INK))

    p.append(text(W / 2, H - 16, "поділ тонший, ніж «системне проти вашого»",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "core-map.svg"), W, H, *p,
           title="За умовчанням: що на Ядрі 0 і що на Ядрі 1")


# ── business-model: одне ядро — три ліцензійні обличчя (для hist-вставки) ──────
# Ідея: спільний код знизу, три юридичні упаковки вгорі.

def fig_business_model():
    W, H = 740, 320
    p = []
    cw, chh = 200, 96
    y = 70
    cols = [
        (60, "FreeRTOS", "$0\nGPL-виняток\n(потім MIT)", FIELD, "#eafaf0"),
        (W / 2 - cw / 2, "OpenRTOS", "комерційна\nліцензія + підтримка\n(WITTENSTEIN)", NEG, "#eef4ff"),
        (W - 60 - cw, "SafeRTOS", "сертифікована\nфункційна безпека\n(IEC/ISO/DO)", POS, "#fdecea"),
    ]
    for x, name, sub, col, fill in cols:
        p.append(rect(x, y, cw, chh, fill=fill, stroke=col, sw=1.8, rx=10))
        p.append(text(x + cw / 2, y + 24, name, size=13, color=col, bold=True))
        p.append(mtext(x + cw / 2, y + 46, sub, size=10, color=INK))

    # спільний код знизу
    by = y + chh + 50
    p.append(rect(60, by, W - 120, 56, fill="#f4f6f8", stroke=INK, sw=1.8, rx=10))
    p.append(text(W / 2, by + 26, "спільна кодова база ядра", size=13, color=INK, bold=True))
    p.append(text(W / 2, by + 46, "те саме ядро — три різні юридичні «упаковки»", size=10, color=MUTED))

    # стрілки від коду до кожної упаковки
    for x, name, sub, col, fill in cols:
        p.append(arrow(x + cw / 2, by, x + cw / 2, y + chh + 4, color=col, sw=1.6))

    render(os.path.join(OUT, "business-model.svg"), W, H, *p,
           title="Бізнес-модель FreeRTOS: одне ядро — три обличчя")


# ── timeline: шлях FreeRTOS від ідеї до вашого ESP32 (для hist-вставки) ────────
# Ідея: п'ять віх однією стрічкою.

def fig_timeline():
    W, H = 760, 300
    p = []
    y = 130
    p.append(line(60, y, W - 60, y, color=INK, sw=2))
    marks = [
        (120, "~2003", "Беррі публікує\nFreeRTOS"),
        (270, "далі", "OpenRTOS / SafeRTOS\n(WITTENSTEIN)"),
        (410, "роки", "хвиля портів\nспільноти"),
        (560, "2017", "Amazon: стюардство\n+ ліцензія MIT"),
        (W - 90, "тепер", "ESP-IDF на двох\nядрах: ваш loopTask"),
    ]
    for i, (x, top, sub) in enumerate(marks):
        col = FIELD if i in (0, 4) else (NEG if i == 3 else INK)
        p.append(circle(x, y, 6, fill=col, stroke=col, sw=1.5))
        p.append(text(x, y - 16, top, size=12, color=col, bold=True))
        # підписи через один — вгору/вниз, щоб не злипались
        if i % 2 == 0:
            p.append(mtext(x, y + 26, sub, size=10, color=MUTED))
        else:
            p.append(mtext(x, y - 56, sub, size=10, color=MUTED))

    p.append(text(W / 2, H - 18,
                  "стрічка продовжує давнішу лінію поділу часу: CTSS → Unix → ядра реального часу",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Шлях FreeRTOS: від роздратування інженера до ядра у вашому ESP32")


if __name__ == "__main__":
    fig_what_is_rtos()
    fig_freertos()
    fig_two_cores()
    fig_illusion_vs_real()
    fig_pinning()
    fig_shared_harder()
    fig_core_map()
    fig_business_model()
    fig_timeline()
    print("OK: figures written to", OUT)
