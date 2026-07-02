# -*- coding: utf-8 -*-
"""Фігури до теми «Сімейство ESP32».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Колір ядра: Xtensa — холодне (фірмове), RISC-V — зелене (відкрите)
XT_F, XT_S = "#eaf0fd", NEG     # заливка/обводка для Xtensa-чипів
RV_F, RV_S = "#eafaf1", FIELD   # заливка/обводка для RISC-V-чипів


# ── Родина одним поглядом: корінь і відгалуження ─────────────────────────────
def fig_family():
    W, H = 940, 430
    title = "Не один чіп, а ціла родина ESP32"
    f = [text(W / 2, 26, title, size=18, bold=True),
         text(W / 2, 48, "варіанти під різні потреби — фірмове Xtensa та новіші відкриті RISC-V",
              size=12, color=MUTED, italic=True)]

    # корінь
    box, bw, bh = textbox(W / 2, 116, "ESP32 (2016)\nоригінал · 2× Xtensa",
                          size=12, fill=XT_F, stroke=XT_S, sw=2, color=XT_S, bold=True, min_w=200)
    f.append(box)
    root_y = 116 + bh / 2

    # листя
    leaves = [
        (150, "ESP32-S2", "1× Xtensa", "Wi-Fi, USB, без BT", XT_F, XT_S),
        (370, "ESP32-S3", "2× Xtensa", "Wi-Fi+BLE, AI",      XT_F, XT_S),
        (590, "ESP32-C3", "1× RISC-V", "дешевий Wi-Fi+BLE",  RV_F, RV_S),
        (810, "ESP32-C6", "1× RISC-V", "Wi-Fi 6 + Thread",   RV_F, RV_S),
    ]
    ly = 300
    for cx, name, core, conn, fill, stroke in leaves:
        f.append(line(W / 2, root_y, cx, ly - 43, color=MUTED, sw=1.4))
    for cx, name, core, conn, fill, stroke in leaves:
        f.append(rect(cx - 92, ly - 43, 184, 86, fill=fill, stroke=stroke, sw=2))
        f.append(text(cx, ly - 18, name, size=13, color=stroke, bold=True))
        f.append(text(cx, ly + 3, core, size=11, color=INK, bold=True))
        f.append(text(cx, ly + 24, conn, size=10, color=MUTED))

    # легенда ядер
    f.append(rect(300, 388, 18, 14, fill=XT_F, stroke=XT_S, sw=1.4, rx=2))
    f.append(text(326, 400, "Xtensa (фірмове ядро)", size=11, color=XT_S, anchor="start", bold=True))
    f.append(rect(560, 388, 18, 14, fill=RV_F, stroke=RV_S, sw=1.4, rx=2))
    f.append(text(586, 400, "RISC-V (відкрите ядро)", size=11, color=RV_S, anchor="start", bold=True))
    render(os.path.join(IMG, "family.svg"), W, H, *f)


# ── Осі відмінностей: на що взагалі дивитися ─────────────────────────────────
def fig_axes():
    W, H = 900, 430
    title = "По яких осях різняться члени родини"
    f = [text(W / 2, 26, title, size=18, bold=True),
         text(W / 2, 48, "насправді їх лише кілька — є на що дивитися",
              size=12, color=MUTED, italic=True)]

    rows = [
        ("Архітектура ядра", "Xtensa  ↔  RISC-V"),
        ("Кількість ядер",   "одне  ↔  два"),
        ("Покоління Wi-Fi",  "Wi-Fi 4  ↔  Wi-Fi 6"),
        ("Bluetooth",        "немає  /  BLE  /  + класичний"),
        ("Вбудований USB",   "немає  ↔  є"),
        ("Особливі здатності", "AI-прискорення (S3) · Thread/Matter (C6)"),
    ]
    top, rh = 88, 48
    for i, (label, val) in enumerate(rows):
        y = top + i * rh
        f.append(text(60, y + 22, label, size=12.5, color=INK, anchor="start", bold=True))
        f.append(fitbox(320, y, 540, 36, val, size=12, bold=True, fill="#fbfbfb", stroke="#e4e4e4", sw=1.4))

    f.append(fitbox(120, 392, 660, 30, "Решта — пам'ять, число ніжок — другорядні відмінності.",
                    size=12, bold=True, fill=RV_F, stroke=RV_S, sw=1.4))
    render(os.path.join(IMG, "axes.svg"), W, H, *f)


# ── Зсув Xtensa → RISC-V: дві школи ядер ─────────────────────────────────────
def fig_xtensa_riscv():
    W, H = 900, 410
    title = "Великий зсув: від фірмового Xtensa до відкритого RISC-V"
    f = [text(W / 2, 26, title, size=18, bold=True),
         text(W / 2, 48, "новіші, дешевші члени родини йдуть відкритим шляхом",
              size=12, color=MUTED, italic=True)]

    # ліва панель — Xtensa
    f.append(rect(60, 100, 320, 220, fill=XT_F, stroke=XT_S, sw=2, rx=12))
    f.append(text(220, 128, "Xtensa", size=15, color=XT_S, bold=True))
    f.append(text(220, 150, "ESP32 · S2 · S3", size=12, color=INK, bold=True))
    for i, ln in enumerate(["фірмове, ліцензоване ядро", "перевірене, потужне", "оригінал і серія S"]):
        f.append(text(220, 184 + i * 28, "• " + ln, size=11, color=INK))

    # стрілка
    f.append(line(395, 210, 505, 210, color=INK, sw=4))
    f.append(arrow(395, 210, 505, 210, color=INK, sw=4))
    f.append(mtext(450, 196, "новіші,\nдешевші", size=10.5, color=MUTED, bold=True))

    # права панель — RISC-V
    f.append(rect(520, 100, 320, 220, fill=RV_F, stroke=RV_S, sw=2, rx=12))
    f.append(text(680, 128, "RISC-V", size=15, color=RV_S, bold=True))
    f.append(text(680, 150, "C3 · C6 · …", size=12, color=INK, bold=True))
    for i, ln in enumerate(["відкритий стандарт — без ліцензій", "дешевше, сучасно, вільно", "майбутнє лінійки"]):
        f.append(text(680, 184 + i * 28, "• " + ln, size=11, color=INK))

    f.append(fitbox(120, 360, 660, 34, "У коді різниця майже невидима — Arduino та ESP-IDF ховають ядро.",
                    size=12, bold=True, fill="#fff6e0", stroke="#caa24a", sw=1.4))
    render(os.path.join(IMG, "xtensa-riscv.svg"), W, H, *f)


# ── Зв'язок по членах родини: таблиця-матриця ───────────────────────────────
def fig_connectivity():
    W, H = 920, 440
    title = "Хто що вміє по бездротовому зв'язку"
    f = [text(W / 2, 26, title, size=18, bold=True),
         text(W / 2, 48, "найважливіша вісь вибору — який саме зв'язок потрібен",
              size=12, color=MUTED, italic=True)]

    cols = [("чіп", 120), ("Wi-Fi", 430), ("BT класич.", 560), ("BLE", 680), ("802.15.4", 812)]
    hy = 102
    for label, cx in cols:
        f.append(text(cx, hy, label, size=11, color=INK, bold=True))
    f.append(text(812, hy + 16, "Thread/Matter", size=9, color=MUTED, italic=True))
    f.append(line(60, hy + 24, 884, hy + 24, color="#e4e4e4", sw=1.4))

    # рядки: чіп, Wi-Fi, BT-класичний?, BLE?, 802.15.4?
    rows = [
        ("ESP32",    "Wi-Fi 4", True,  True,  False),
        ("ESP32-S2", "Wi-Fi 4", False, False, False),
        ("ESP32-S3", "Wi-Fi 4", False, True,  False),
        ("ESP32-C3", "Wi-Fi 4", False, True,  False),
        ("ESP32-C6", "Wi-Fi 6", False, True,  True),
    ]
    ry, rh = hy + 30, 50
    for i, (chip, wifi, bt, ble, ieee) in enumerate(rows):
        y = ry + i * rh
        f.append(rect(60, y, 824, 44, fill=("#fcfcfc" if i % 2 == 0 else "#f4f7fb"),
                      stroke="#e4e4e4", sw=1))
        cy = y + 28
        f.append(text(120, cy, chip, size=11.5, color=INK, bold=True))
        f.append(text(430, cy, wifi, size=11, color=(FIELD if wifi.endswith("6") else INK), bold=True))
        for cx, ok in ((560, bt), (680, ble), (812, ieee)):
            f.append(text(cx, cy, "✓" if ok else "—", size=13,
                          color=(FIELD if ok else MUTED), bold=True))
    render(os.path.join(IMG, "connectivity.svg"), W, H, *f)


# ── Порадник вибору: потреба → чіп ──────────────────────────────────────────
def fig_chooser():
    W, H = 900, 470
    title = "Що обирати: короткий порадник"
    f = [text(W / 2, 26, title, size=18, bold=True),
         text(W / 2, 48, "щойно чесно сформулюєш потребу — вибір майже очевидний",
              size=12, color=MUTED, italic=True)]

    rows = [
        ("найдешевший простий Wi-Fi + BLE",        "ESP32-C3",        RV_F, RV_S),
        ("потужність + камера / звук / ML",        "ESP32-S3",        XT_F, XT_S),
        ("USB + Wi-Fi, без Bluetooth, дешево",     "ESP32-S2",        XT_F, XT_S),
        ("Matter / Thread / Zigbee (розумний дім)", "ESP32-C6",       RV_F, RV_S),
        ("загальне навчання, максимум прикладів",  "ESP32 (оригінал)", XT_F, XT_S),
    ]
    top, rh = 100, 66
    for i, (need, chip, fill, stroke) in enumerate(rows):
        y = top + i * rh
        f.append(rect(46, y, 520, 50, fill="#fbfbfb", stroke="#e4e4e4", sw=1.4))
        f.append(fitbox(56, y + 9, 500, 32, need, size=12, color=INK, anchor="start", fill="#fbfbfb", stroke="#fbfbfb", sw=0))
        f.append(line(576, y + 25, 640, y + 25, color=INK, sw=2.6))
        f.append(arrow(576, y + 25, 640, y + 25, color=INK, sw=2.6))
        f.append(fitbox(650, y, 204, 50, chip, size=13, color=stroke, bold=True, fill=fill, stroke=stroke, sw=2))
    render(os.path.join(IMG, "chooser.svg"), W, H, *f)


# ── Добір під проєкт: три приклади ──────────────────────────────────────────
def fig_picks():
    W, H = 920, 420
    title = "Добір під проєкт: три приклади"
    f = [text(W / 2, 26, title, size=18, bold=True),
         text(W / 2, 48, "кожен вибір диктує одна-дві ключові вимоги, а не «загальна крутість»",
              size=12, color=MUTED, italic=True)]

    cards = [
        (175, "Розумна розетка", "масовий тираж · простий Wi-Fi", "ESP32-C3", "найдешевший · RISC-V", RV_F, RV_S),
        (462, "Камера з розпізнаванням", "RAM · два ядра · прискорення", "ESP32-S3", "AI-інструкції · багато RAM", XT_F, XT_S),
        (749, "Давач розумного дому", "Matter / Thread", "ESP32-C6", "802.15.4 + Wi-Fi 6", RV_F, RV_S),
    ]
    for cx, task, why, chip, note, fill, stroke in cards:
        f.append(rect(cx - 135, 88, 270, 286, fill=BG, stroke="#e4e4e4", sw=2, rx=12))
        f.append(text(cx, 116, task, size=12.5, color=INK, bold=True))
        f.append(text(cx, 140, why, size=9.8, color=MUTED))
        f.append(line(cx, 158, cx, 196, color=INK, sw=2.6))
        f.append(arrow(cx, 158, cx, 196, color=INK, sw=2.6))
        f.append(rect(cx - 100, 202, 200, 62, fill=fill, stroke=stroke, sw=2, rx=10))
        f.append(text(cx, 230, chip, size=14.5, color=stroke, bold=True))
        f.append(text(cx, 251, "✓ підходить", size=9.5, color=stroke, bold=True))
        f.append(text(cx, 300, note, size=10.5, color=INK, bold=True))
        f.append(text(cx, 322, "ключова вимога вирішила", size=9, color=MUTED, italic=True))
    render(os.path.join(IMG, "picks.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури до вставки hist-riscv.md (префікс riscv- — щоб не плутати з темою)
# ════════════════════════════════════════════════════════════════════════════

WARN = "#caa24a"  # осторога/«!»

def _pmn(cx, cy, kind):
    """Маленький значок +/−/! на позиції (cx,cy)."""
    if kind == "+":
        return plus(cx, cy, r=11)
    if kind == "-":
        return minus(cx, cy, r=11)
    return (circle(cx, cy, 11, fill="#f3eede", stroke=WARN, sw=1.6) +
            text(cx, cy + 4.5, "!", size=14, color=WARN, bold=True))


# ── Три способи дістати ядро: своє / ліцензоване / відкрите ──────────────────
def fig_riscv_three_ways():
    W, H = 940, 430
    f = [text(W / 2, 26, "Три способи дістати ядро для свого чипа", size=18, bold=True),
         text(W / 2, 48, "кожен виробник МК щось із цього обирає — і дедалі частіше це RISC-V",
              size=11.5, color=MUTED, italic=True)]

    panels = [
        (40,  POS,   "Спроєктувати СВОЄ", [("+", "повний контроль"),
                                           ("-", "роки роботи, ризик"),
                                           ("!", "майже ніхто з нуля")]),
        (332, NEG,   "Ліцензувати",       [("+", "готове (ARM, Xtensa)"),
                                           ("-", "ліцензія + роялті/чип"),
                                           ("!", "залежність від власника")]),
        (624, FIELD, "Взяти ВІДКРИТЕ",    [("+", "безкоштовно (RISC-V)"),
                                           ("+", "вільно кроїти ISA"),
                                           ("!", "молодша екосистема")]),
    ]
    for px, col, head, items in panels:
        f.append(rect(px, 90, 276, 300, fill="#fcfcfc", stroke=col, sw=2, rx=12))
        f.append(text(px + 138, 120, head, size=13.5, color=col, bold=True))
        f.append(line(px + 24, 136, px + 252, 136, color=col, sw=1.4))
        for i, (kind, label) in enumerate(items):
            cy = 178 + i * 60
            f.append(_pmn(px + 40, cy, kind))
            f.append(text(px + 62, cy + 4, label, size=10.6, color=INK, anchor="start"))
    render(os.path.join(IMG, "riscv-three-ways.svg"), W, H, *f)


# ── Розкол родини: старші на Xtensa, нові на RISC-V ─────────────────────────
def fig_riscv_espressif_split():
    W, H = 920, 420
    f = [text(W / 2, 26, "Родина ESP32 переходить на RISC-V", size=18, bold=True),
         text(W / 2, 48, "старші чипи — на ліцензованому Xtensa; усі нові — на відкритому RISC-V",
              size=11.5, color=MUTED, italic=True)]

    # ліва група — Xtensa
    f.append(rect(60, 90, 380, 150, fill=XT_F, stroke=NEG, sw=2, rx=12))
    f.append(text(250, 116, "Xtensa (ліцензоване ядро)", size=12, color=NEG, bold=True))
    for i, name in enumerate(["ESP32", "ESP32-S2", "ESP32-S3"]):
        x = 108 + i * 110
        f.append(rect(x, 140, 96, 40, fill=BG, stroke=NEG, sw=1.6, rx=8))
        f.append(text(x + 48, 165, name, size=10, color=NEG, bold=True))
    f.append(text(250, 214, "S3 — останній великий на Xtensa", size=9.5, color=MUTED, italic=True))

    # права група — RISC-V
    f.append(rect(480, 90, 380, 150, fill=RV_F, stroke=FIELD, sw=2, rx=12))
    f.append(text(670, 116, "RISC-V (відкрита ISA)", size=12, color=FIELD, bold=True))
    for i, name in enumerate(["ESP32-C3", "ESP32-C6", "ESP32-H2", "ESP32-P4"]):
        x = 508 + i * 88
        f.append(rect(x, 140, 76, 40, fill=BG, stroke=FIELD, sw=1.6, rx=8))
        f.append(text(x + 38, 165, name, size=9.5, color=FIELD, bold=True))
    f.append(text(670, 214, "усі нові сімейства", size=9.5, color=MUTED, italic=True))

    # стрілка переходу
    f.append(line(250, 272, 660, 272, color=INK, sw=3))
    f.append(arrow(250, 272, 660, 272, color=INK, sw=3))
    f.append(text(460, 262, "з ~2019 — курс на RISC-V", size=11, color=INK, bold=True))

    f.append(fitbox(150, 318, 620, 66,
                    "Для коду різниця майже непомітна: IDF і GCC компілюють під обидві.\nЗмінюється ISA всередині — не спосіб, у який ви пишете програму.",
                    size=10.5, bold=True, fill="#fff6e0", stroke=WARN, sw=1.4))
    render(os.path.join(IMG, "riscv-espressif-split.svg"), W, H, *f)


# ── Чотири сили міграції на RISC-V і одна осторога ──────────────────────────
def fig_riscv_why_migrate():
    W, H = 920, 420
    f = [text(W / 2, 26, "Що жене виробників до RISC-V", size=18, bold=True),
         text(W / 2, 48, "чотири сили тягнуть в один бік — і одна осторога",
              size=11.5, color=MUTED, italic=True)]

    forces = [
        ("Ціна",        "нуль роялті × мільярди штук",      RV_F, FIELD),
        ("Контроль",    "кроїти й розширювати ISA під себе", XT_F, NEG),
        ("Незалежність", "не залежати від одного власника",  "#f3eede", WARN),
        ("Імпульс",     "багато нових чипів, росте екосистема", RV_F, FIELD),
    ]
    for i, (head, sub, fill, col) in enumerate(forces):
        y = 80 + i * 82
        f.append(rect(70, y, 540, 70, fill=fill, stroke=col, sw=1.8, rx=10))
        f.append(text(98, y + 30, head, size=13, color=col, anchor="start", bold=True))
        f.append(text(98, y + 52, sub, size=10.5, color=INK, anchor="start"))
        f.append(line(610, y + 35, 730, 200, color=col, sw=2))
        f.append(arrow(610, y + 35, 730, 200, color=col, sw=2))

    # центр тяжіння
    f.append(circle(800, 200, 64, fill=RV_F, stroke=FIELD, sw=2.6))
    f.append(text(800, 196, "RISC-V", size=14, color=FIELD, bold=True))
    f.append(text(800, 215, "відкрита ISA", size=9.5, color=INK))
    f.append(mtext(800, 300, "екосистема молодша\nза ARM — поки що", size=9.5, color=POS, bold=True))
    render(os.path.join(IMG, "riscv-why-migrate.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури до ДЕТАЛЬНОЇ статті esp32-family-d.md (префікс d-)
# ════════════════════════════════════════════════════════════════════════════

WARN2 = "#caa24a"

# ── Два ядра й SMP: хто на якому ядрі ────────────────────────────────────────
def fig_d_cores():
    W, H = 920, 430
    f = [text(W / 2, 26, "Два ядра, спільна пам'ять і хто де сидить", size=18, bold=True),
         text(W / 2, 48, "радіо тримає одне ядро — тому «два» не завжди означає «удвічі вільніше»",
              size=11.5, color=MUTED, italic=True)]

    # PRO CPU (core 0)
    f.append(rect(70, 92, 340, 150, fill=XT_F, stroke=NEG, sw=2, rx=12))
    f.append(text(240, 118, "Ядро 0 (PRO_CPU)", size=13, color=NEG, bold=True))
    for i, ln in enumerate(["стек Wi-Fi / Bluetooth", "службові задачі IDF", "переривання радіо"]):
        f.append(text(240, 148 + i * 26, "• " + ln, size=10.6, color=INK))
    f.append(text(240, 232, "радіо «з'їдає» помітну частку", size=9.5, color=POS, italic=True))

    # APP CPU (core 1)
    f.append(rect(510, 92, 340, 150, fill=RV_F, stroke=FIELD, sw=2, rx=12))
    f.append(text(680, 118, "Ядро 1 (APP_CPU)", size=13, color=FIELD, bold=True))
    for i, ln in enumerate(["ваш app_main і задачі", "важкі обчислення", "вільніше під навантаження"]):
        f.append(text(680, 148 + i * 26, "• " + ln, size=10.6, color=INK))
    f.append(text(680, 232, "сюди «пінимо» гарячий код", size=9.5, color=FIELD, italic=True))

    # спільна шина/RAM
    f.append(rect(70, 286, 780, 56, fill="#fbfbfb", stroke="#d8d8d8", sw=1.8, rx=10))
    f.append(text(460, 309, "спільна внутрішня SRAM · спільна шина · спільні периферія й регістри",
                  size=11.5, color=INK, bold=True))
    f.append(text(460, 328, "обидва ядра бачать ту саму пам'ять — тому потрібні м'ютекси й критичні секції",
                  size=9.5, color=MUTED, italic=True))
    f.append(line(240, 242, 240, 286, color=NEG, sw=2))
    f.append(line(680, 242, 680, 286, color=FIELD, sw=2))

    f.append(fitbox(150, 366, 620, 46,
                    "Одноядерні C3/C6 роблять те саме — але по черзі: радіо й ваш код\n"
                    "ділять ОДИН конвеєр, тож планувальник перемикає їх у часі.",
                    size=10.5, bold=True, fill="#fff6e0", stroke=WARN2, sw=1.4))
    render(os.path.join(IMG, "d-cores.svg"), W, H, *f)


# ── Мапа пам'яті: внутрішня SRAM, кеш, зовнішні flash і PSRAM ────────────────
def fig_d_memory():
    W, H = 940, 470
    f = [text(W / 2, 26, "Мапа пам'яті — справжня «особистість» чипа", size=18, bold=True),
         text(W / 2, 48, "той самий байт видно з різних шин; зовнішнє — крізь кеш",
              size=11.5, color=MUTED, italic=True)]

    # ядро
    f.append(rect(60, 96, 150, 300, fill="#eef1f6", stroke=INK, sw=2, rx=12))
    f.append(text(135, 128, "Ядро", size=13, color=INK, bold=True))
    f.append(text(135, 168, "шина", size=10, color=MUTED))
    f.append(text(135, 184, "команд", size=10, color=NEG, bold=True))
    f.append(text(135, 300, "шина", size=10, color=MUTED))
    f.append(text(135, 316, "даних", size=10, color=FIELD, bold=True))

    # внутрішня SRAM
    f.append(rect(250, 96, 300, 300, fill="#fbfbfb", stroke="#cfcfcf", sw=2, rx=12))
    f.append(text(400, 122, "внутрішня SRAM (на кристалі)", size=11.5, color=INK, bold=True))
    f.append(rect(272, 140, 256, 70, fill=XT_F, stroke=NEG, sw=1.8, rx=8))
    f.append(text(400, 166, "IRAM — код у RAM", size=11, color=NEG, bold=True))
    f.append(text(400, 190, "гарячі функції, ISR (.iram_attr)", size=9.3, color=INK))
    f.append(rect(272, 224, 256, 70, fill=RV_F, stroke=FIELD, sw=1.8, rx=8))
    f.append(text(400, 250, "DRAM — дані в RAM", size=11, color=FIELD, bold=True))
    f.append(text(400, 274, ".data / .bss / купа / стеки", size=9.3, color=INK))
    f.append(rect(272, 308, 256, 70, fill="#f3eede", stroke=WARN2, sw=1.8, rx=8))
    f.append(text(400, 334, "кеш (частина SRAM)", size=11, color="#8a6d1e", bold=True))
    f.append(text(400, 358, "вікно у зовнішні flash і PSRAM", size=9.3, color=INK))

    # зовнішні
    f.append(rect(600, 96, 300, 300, fill="#fcfcfc", stroke="#cfcfcf", sw=2, rx=12))
    f.append(text(750, 122, "зовнішні мікросхеми (по SPI)", size=11.5, color=INK, bold=True))
    f.append(rect(622, 150, 256, 96, fill="#eef1f6", stroke=NEG, sw=1.8, rx=8))
    f.append(text(750, 178, "flash: IROM + DROM", size=11, color=NEG, bold=True))
    f.append(text(750, 202, "основний код і константи", size=9.3, color=INK))
    f.append(text(750, 222, "виконується «на місці» крізь кеш", size=9, color=MUTED, italic=True))
    f.append(rect(622, 262, 256, 96, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(750, 290, "PSRAM (опційно)", size=11, color=FIELD, bold=True))
    f.append(text(750, 314, "великі буфери: кадри, звук, ML", size=9.3, color=INK))
    f.append(text(750, 334, "теж крізь кеш — повільніше за SRAM", size=9, color=MUTED, italic=True))

    # шини
    f.append(line(210, 184, 272, 175, color=NEG, sw=2.4)); f.append(arrow(210, 184, 272, 175, color=NEG, sw=2.4))
    f.append(line(210, 316, 272, 259, color=FIELD, sw=2.4)); f.append(arrow(210, 316, 272, 259, color=FIELD, sw=2.4))
    f.append(line(528, 343, 622, 200, color="#8a6d1e", sw=2.2)); f.append(arrow(528, 343, 622, 200, color="#8a6d1e", sw=2.2))
    f.append(line(528, 343, 622, 300, color="#8a6d1e", sw=2.2)); f.append(arrow(528, 343, 622, 300, color="#8a6d1e", sw=2.2))

    f.append(fitbox(150, 418, 640, 42,
                    "Внутрішня SRAM — швидка й мала (сотні КБ). Зовнішнє — велике й дешеве,\n"
                    "але кожен промах кешу коштує тактів. Звідси весь тюнінг: що тримати всередині.",
                    size=10.3, bold=True, fill="#f4f7fb", stroke="#cfd6e2", sw=1.4))
    render(os.path.join(IMG, "d-memory.svg"), W, H, *f)


# ── Домени живлення: що засинає, а що лишається живим ────────────────────────
def fig_d_power():
    W, H = 920, 440
    f = [text(W / 2, 26, "Домени живлення: що вимикається уві сні", size=18, bold=True),
         text(W / 2, 48, "глибокий сон гасить майже все — струм падає з міліампер до мікроампер",
              size=11.5, color=MUTED, italic=True)]

    # активна зона (гасне)
    f.append(rect(60, 92, 500, 210, fill="#fdecea", stroke=POS, sw=2, rx=12))
    f.append(text(310, 118, "«Цифровий» домен — ГАСНЕ у глибокому сні", size=12, color=POS, bold=True))
    items = ["ядра (Xtensa / RISC-V)", "більшість SRAM",
             "радіо Wi-Fi / BT", "швидка периферія (APB)"]
    for i, lbl in enumerate(items):
        col = 60 + (0 if i < 2 else 260)
        yy = 150 + (i % 2) * 44
        f.append(rect(col + 20, yy, 220, 34, fill=BG, stroke=POS, sw=1.4, rx=6))
        f.append(text(col + 130, yy + 22, lbl, size=10, color=INK))
    f.append(text(310, 288, "усе це знеструмлюється → десятки мкА зникають", size=9.5, color=POS, italic=True))

    # RTC домен (живий)
    f.append(rect(600, 92, 260, 210, fill="#eafaf1", stroke=FIELD, sw=2, rx=12))
    f.append(text(730, 118, "RTC-домен — ЖИВИЙ", size=12, color=FIELD, bold=True))
    for i, ln in enumerate(["RTC-контролер + таймер", "маленька RTC-пам'ять", "співпроцесор (ULP / LP)", "кілька RTC-ніжок"]):
        f.append(text(730, 150 + i * 30, "• " + ln, size=10, color=INK))
    f.append(text(730, 288, "лишається на мікроамперах", size=9.5, color=FIELD, italic=True))

    # вісь струму
    f.append(line(80, 356, 840, 356, color=INK, sw=2))
    f.append(arrow(80, 356, 840, 356, color=INK, sw=2))
    for x, lab in [(120, "глибокий сон\n~7 мкА (RTC on)"), (360, "легкий сон\n~240 мкА"),
                   (620, "активно, радіо тихо\nдесятки мА"), (800, "передавання\n>100 мА")]:
        f.append(circle(x, 356, 6, fill=BG, stroke=INK, sw=2))
        f.append(mtext(x, 378, lab, size=9.3, color=INK, bold=True))
    f.append(text(460, 420, "числа — для голого чипа з даташита; плата з регулятором і USB-мостом додасть своє",
                  size=9.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "d-power.svg"), W, H, *f)


# ── Співпроцесорний «звіринець»: FSM · RISC-V ULP · LP-ядро ──────────────────
def fig_d_coproc():
    W, H = 940, 400
    f = [text(W / 2, 26, "Три обличчя «малого мозку, що не спить»", size=18, bold=True),
         text(W / 2, 48, "той самий задум — стерегти давачі уві сні — у трьох поколіннях",
              size=11.5, color=MUTED, italic=True)]

    cards = [
        (185, "ULP FSM", "ESP32 · S2 · S3",
         ["крихітний автомат", "асемблер / C-макроси", "4 × 16-біт регістри", "I²C — лише бітбенгом"], XT_F, NEG),
        (470, "ULP RISC-V", "S2 · S3",
         ["справжнє RISC-V ядро", "звичайний C + GCC", "RV32IMC, множення/ділення", "є апаратний I²C"], RV_F, FIELD),
        (755, "LP-ядро", "C6 · H2 · P4",
         ["окреме RISC-V до ~20 МГц", "звичайний C", "власні переривання й шина", "стеки живлення нового рівня"], RV_F, FIELD),
    ]
    for cx, head, chips, items, fill, col in cards:
        f.append(rect(cx - 135, 88, 270, 268, fill=fill, stroke=col, sw=2, rx=12))
        f.append(text(cx, 116, head, size=14, color=col, bold=True))
        f.append(text(cx, 138, chips, size=10, color=INK, bold=True))
        f.append(line(cx - 105, 150, cx + 105, 150, color=col, sw=1.2))
        for i, ln in enumerate(items):
            f.append(text(cx, 178 + i * 30, "• " + ln, size=10, color=INK))
    # стрілка «дозрівання»
    f.append(line(320, 372, 620, 372, color=MUTED, sw=2, dash="4,4"))
    f.append(arrow(320, 372, 620, 372, color=MUTED, sw=2))
    f.append(text(470, 366, "від примітивного автомата — до повноцінного ядра", size=9.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "d-coproc.svg"), W, H, *f)


if __name__ == "__main__":
    # тема
    fig_family()
    fig_axes()
    fig_xtensa_riscv()
    fig_connectivity()
    fig_chooser()
    fig_picks()
    # вставка hist-riscv.md
    fig_riscv_three_ways()
    fig_riscv_espressif_split()
    fig_riscv_why_migrate()
    # детальна esp32-family-d.md
    fig_d_cores()
    fig_d_memory()
    fig_d_power()
    fig_d_coproc()
    print("OK: family, axes, xtensa-riscv, connectivity, chooser, picks, "
          "riscv-three-ways, riscv-espressif-split, riscv-why-migrate, "
          "d-cores, d-memory, d-power, d-coproc")
