# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE  = "#eef4ff"
GREEN = "#eaf7ef"
AMBER = "#fff6e6"
GREY  = "#f2f2f5"
RED   = "#fdecea"


def box3(cx, cy, w, h, title, l2=None, l3=None, fill=FILL):
    """Рамка з 1–3 центрованими рядками (заголовок + до двох підписів)."""
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill=fill, stroke=INK, sw=1.8, rx=9)
    if l2 is None and l3 is None:
        out += text(cx, cy + 5, title, size=15, bold=True)
    elif l3 is None:
        out += text(cx, cy - 5, title, size=15, bold=True)
        out += text(cx, cy + 16, l2, size=11.5, color=MUTED)
    else:
        out += text(cx, cy - 14, title, size=15, bold=True)
        out += text(cx, cy + 6, l2, size=11.5, color=MUTED)
        out += text(cx, cy + 24, l3, size=11.5, color=MUTED)
    return out


# ── Фігура 1: анатомія MVVM — рушій зв'язування між поданням і моделлю подання ─
def fig_anatomy():
    W, H = 1040, 470
    f = []

    cy = 232
    # Три частини
    f.append(box3(150, cy, 200, 96, "Подання",
                  "розмітка + прив'язки", "нічого не вирішує", fill=GREEN))
    f.append(box3(520, cy, 230, 108, "Модель подання",
                  "властивості + команди", "не знає про подання", fill=BLUE))
    f.append(box3(890, cy, 200, 96, "Модель",
                  "дані + правила", "не знає про екран", fill=AMBER))

    # ── Проміжок Подання ↔ Модель подання: рушій зв'язування (двобічно) ──
    f.append(text(327, 138, "рушій зв'язування", size=13, bold=True, color=FIELD))
    # показ: Модель подання → Подання
    f.append(arrow(403, 208, 254, 208, color=FIELD, sw=2.2))
    f.append(text(327, 197, "показ", size=12, color=FIELD))
    # ввід: Подання → Модель подання
    f.append(arrow(254, 258, 403, 258, color=FIELD, sw=2.2))
    f.append(text(327, 278, "ввід", size=12, color=FIELD))
    f.append(text(327, 322, "двобічно, автоматично", size=12, color=MUTED))

    # ── Проміжок Модель подання ↔ Модель ──
    f.append(arrow(637, 208, 787, 208))
    f.append(text(712, 197, "читає, кличе правила", size=11, color=INK))
    f.append(arrow(787, 258, 637, 258, color=MUTED, sw=1.6))
    f.append(text(712, 278, "сповіщає (спостерігач)", size=11, color=MUTED))

    f.append(text(520, 420,
                  "Стан екрана — звичайний об'єкт: його крутять у тесті без жодного пікселя",
                  size=12.5, color=MUTED))

    render(os.path.join(IMG, 'mvvm-anatomy.svg'), W, H, *f,
           title="Анатомія MVVM: рушій зв'язування тримає екран і модель подання в синхроні")


# ── Фігура 2: що прибирає зв'язування — ручний перепис проти однієї декларації ─
def fig_binding_vs_glue():
    W, H = 1040, 500
    f = []

    f.append(line(520, 84, 520, 430, color=MUTED, sw=1.2, dash="4 6"))

    # ── ЛІВОРУЧ: руками, рядок за рядком ──
    f.append(text(265, 66, "Руками: рядок коду на кожен показ і ввід",
                  size=15, bold=True))
    f.append(rect(58, 92, 414, 250, fill=RED, stroke=INK, sw=1.8, rx=10))
    rows = ["лейбл.text = fmt(темп)",
            "темп = parse(поле.text)",
            "кнопка.enabled = можнаЗберегти",
            "× на КОЖНЕ поле, обидва боки"]
    y = 132
    for r in rows:
        f.append(fitbox(84, y, 362, 40, r, size=13, fill=BG, sw=1.3))
        y += 50
    f.append(text(265, 372, "багато однакового коду; забув рядок — екран бреше",
                  size=12, color=POS))

    # ── ПРАВОРУЧ: оголосив пару — рушій тримає ──
    f.append(text(775, 66, "Зв'язуванням: оголосив пару — рушій тримає",
                  size=15, bold=True))
    f.append(rect(568, 92, 414, 250, fill=GREEN, stroke=INK, sw=1.8, rx=10))
    f.append(fitbox(594, 138, 362, 56, "<поле text={Binding Темп}>",
                    size=15, fill=BG, sw=1.4))
    f.append(text(775, 214, "подання: одна прив'язка", size=11.5, color=MUTED))
    f.append(fitbox(594, 240, 362, 56, "Темп — спостережувана властивість",
                    size=14, fill=BG, sw=1.4))
    f.append(text(775, 316, "модель подання: одне поле", size=11.5, color=MUTED))
    f.append(text(775, 372, "рушій сам тримає їх рівними — копіювати не треба",
                  size=12, color=FIELD))

    f.append(text(520, 466,
                  "MVVM прибирає ручний перепис: оголошуєш зв'язок раз — рушій тримає екран і дані рівними",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'binding-vs-glue.svg'), W, H, *f,
           title="Що прибирає зв'язування: перепис поле-за-полем проти однієї декларації")


# ── Фігура 3 (вставка proj): кільце двобічного зв'язування і його точка зупину ─
def fig_binding_cycle():
    W, H = 1060, 560
    f = []

    # Чотири вузли кільця
    f.append(box3(250, 170, 270, 90, "Поле вводу", "текст «23»", fill=GREEN))
    f.append(box3(810, 170, 270, 90, "Перетворювач", "«23» → 23", fill=GREY))
    f.append(box3(810, 390, 270, 90, "Властивість", "нове ≠ старе?", fill=BLUE))
    f.append(box3(250, 390, 270, 90, "Перетворювач", "23 → «23»", fill=GREY))

    # Верх: поле → перетворювач у число
    f.append(arrow(390, 170, 670, 170, color=FIELD, sw=2.2))
    f.append(text(530, 152, "подія input", size=12.5, color=FIELD))
    f.append(text(530, 197, "користувач надрукував", size=11.5, color=MUTED))

    # Право: число → у сетер властивості
    f.append(arrow(810, 220, 810, 340, color=FIELD, sw=2.2))
    f.append(text(828, 268, "число 23", size=12.5, color=FIELD, anchor="start"))
    f.append(text(828, 290, "у сетер", size=11.5, color=MUTED, anchor="start"))

    # Низ: сигнал про зміну → перетворювач у текст
    f.append(arrow(670, 390, 390, 390, color=NEG, sw=2.2))
    f.append(text(530, 371, "сигнал про зміну", size=12.5, color=NEG))
    f.append(text(530, 416, "лише якщо значення справді інше", size=11.5, color=MUTED))

    # Ліво: текст назад у поле
    f.append(arrow(250, 345, 250, 220, color=NEG, sw=2.2))
    f.append(text(232, 268, "«23» у поле", size=12.5, color=NEG, anchor="end"))
    f.append(text(232, 290, "запис із коду", size=11.5, color=MUTED, anchor="end"))

    # Дві причини, чому кільце не крутиться вічно
    f.append(fitbox(40, 462, 420, 66,
                    "запис у поле з коду не породжує\nподії input — обороту не буде",
                    size=13, fill=GREEN, stroke=FIELD, sw=1.8))
    f.append(fitbox(600, 462, 420, 66,
                    "нове = старе → сигналу немає:\nкільце спиняється саме тут",
                    size=13, fill=RED, stroke=POS, sw=1.8))

    render(os.path.join(IMG, 'binding-cycle.svg'), W, H, *f,
           title="Кільце двобічного зв'язування: де воно спиняється")


# ── Фігура 4 (вставка proj): таблиця підписок і час життя зв'язку ──────────────
def fig_binding_subscriptions():
    W, H = 1060, 520
    f = []

    # Джерело сигналу
    f.append(box3(160, 200, 240, 100, "Модель подання",
                  "temperature = 23", "error = «»", fill=BLUE))
    f.append(arrow(285, 200, 370, 200, color=FIELD, sw=2.2))
    f.append(text(327, 184, "сигнал", size=12, color=FIELD))

    # Серце рушія — звичайний словник
    f.append(rect(380, 118, 300, 262, fill=FILL, stroke=INK, sw=1.8, rx=10))
    f.append(text(530, 148, "Таблиця підписок", size=14, bold=True))
    f.append(fitbox(400, 168, 260, 64, "«temperature» →\nслухач A, слухач B",
                    size=12.5, fill=BG, sw=1.3))
    f.append(fitbox(400, 244, 260, 64, "«error» →\nслухач C",
                    size=12.5, fill=BG, sw=1.3))
    f.append(text(530, 352, "ключ — ім'я властивості рядком", size=11.5, color=MUTED))

    # Віджети на тому кінці підписок
    f.append(fitbox(760, 140, 240, 58, "поле вводу", size=13, fill=GREEN, sw=1.6))
    f.append(fitbox(760, 218, 240, 58, "велика цифра", size=13, fill=GREEN, sw=1.6))
    f.append(fitbox(760, 296, 240, 74, "напис про помилку\nзнятий з екрана",
                    size=12.5, fill=RED, stroke=POS, sw=1.8))

    f.append(arrow(690, 192, 750, 169))
    f.append(arrow(690, 210, 750, 247))
    f.append(arrow(690, 288, 750, 330, color=POS, sw=2))

    f.append(fitbox(120, 418, 820, 76,
                    "Поки підписка в таблиці — живий і слухач, і віджет за ним.\n"
                    "Тому bind віддає відписку, а рушії тримають слухачів слабко.",
                    size=13.5, fill=AMBER, stroke=INK, sw=1.4))

    render(os.path.join(IMG, 'binding-subscriptions.svg'), W, H, *f,
           title="Серце рушія — словник «ім'я властивості → слухачі»")


# ── Фігура 5 (вставка hist): вісь часу — до імені, народження імені, розселення ─
def fig_mvvm_timeline():
    W, H = 1020, 668
    f = []

    AX = 312            # вісь
    X_DATE, X_EVT = 294, 332

    f.append(text(510, 44, "Ім'я MVVM: що було до нього, коли воно з'явилося й куди розійшлося",
                  size=14.5, bold=True))
    f.append(line(AX, 76, AX, 626, color=MUTED, sw=2))

    rows = [
        ("початок 1990-х", "ParcPlace VisualWorks: клас ApplicationModel —", "модель екрана вже є, імені ще немає", False),
        ("жовтень 2003", "Cocoa Bindings у Mac OS X 10.3 —", "декларативне зв'язування працює на іншій платформі", False),
        ("19 липня 2004", "Мартін Фаулер друкує «презентаційну модель» —", "синхронізацію з екраном пишуть руками", False),
        ("8 жовтня 2005", "Джон Ґоссман у блозі називає Model/View/ViewModel", "", True),
        ("21 листопада 2006", "WPF виходить у складі .NET Framework 3.0 —", "рушій зв'язування нарешті в коробці", False),
        ("лютий 2009", "стаття Джоша Сміта в MSDN Magazine —", "назва «ViewModel» перемагає «презентаційну модель»", False),
        ("5 липня 2010", "Knockout переносить ім'я і патерн у JavaScript", "", False),
        ("лютий 2014", "Vue виходить із гаслом «JavaScript MVVM made simple»", "", False),
        ("листопад 2017", "Android дає слово ViewModel зовсім іншій речі", "", False),
    ]

    y = 108
    for when, what, note, key in rows:
        f.append(text(X_DATE, y + 5, when, size=13, anchor="end",
                      bold=key, color=INK if key else MUTED))
        f.append(circle(AX, y, 8 if key else 6,
                        fill=FIELD if key else BG, stroke=INK, sw=2))
        f.append(text(X_EVT, y + (-3 if note else 5), what,
                      size=13.5 if key else 13, anchor="start", bold=key))
        if note:
            f.append(text(X_EVT, y + 17, note, size=12, anchor="start", color=MUTED))
        y += 62

    f.append(text(510, 652,
                  "Ідея старша за ім'я, ім'я старше за платформу, а платформа не пережила імені",
                  size=12.5, color=MUTED))

    render(os.path.join(IMG, 'mvvm-timeline.svg'), W, H, *f,
           title="Вісь часу: ApplicationModel, презентаційна модель, народження назви MVVM і її мандри")


# ── Фігура 6 (вставка hist): шов синхронізації — хто пише цей код ──────────────
def fig_sync_seam():
    W, H = 1120, 424
    f = []

    f.append(line(560, 40, 560, 396, color=MUTED, sw=1.2, dash="4 6"))

    # ── Ліворуч: 2004, синхронізацію пише програміст ──
    f.append(text(290, 60, "Липень 2004: презентаційна модель", size=15, bold=True))
    f.append(fitbox(60, 110, 180, 80, "Подання", size=15, fill=GREEN, sw=1.8))
    f.append(fitbox(330, 110, 200, 80, "Презентаційна\nмодель", size=15, fill=BLUE, sw=1.8))
    f.append(text(285, 100, "синхронізація", size=12, color=POS))
    f.append(arrow(245, 136, 325, 136, color=POS, sw=2))
    f.append(arrow(325, 168, 245, 168, color=POS, sw=2))
    f.append(fitbox(60, 214, 470, 58, "у поданні — тести моделі її не бачать",
                    size=13, fill=RED, stroke=POS, sw=1.6))
    f.append(fitbox(60, 286, 470, 58, "у моделі — вона знову залежить від подання",
                    size=13, fill=RED, stroke=POS, sw=1.6))
    f.append(text(290, 380, "цей код хтось мусить написати — обидва місця погані",
                  size=12.5, color=MUTED))

    # ── Праворуч: 2005, синхронізацію бере рушій ──
    f.append(text(830, 60, "Жовтень 2005: модель подання", size=15, bold=True))
    f.append(fitbox(600, 110, 180, 80, "Подання", size=15, fill=GREEN, sw=1.8))
    f.append(fitbox(870, 110, 200, 80, "Модель\nподання", size=15, fill=BLUE, sw=1.8))
    f.append(text(825, 100, "рушій", size=12, color=FIELD))
    f.append(arrow(785, 136, 865, 136, color=FIELD, sw=2))
    f.append(arrow(865, 168, 785, 168, color=FIELD, sw=2))
    f.append(fitbox(600, 214, 470, 58, "рушій сам тримає обидва кінці рівними",
                    size=13, fill=GREEN, stroke=FIELD, sw=1.6))
    f.append(fitbox(600, 286, 470, 58, "коду синхронізації не пише ніхто — його немає",
                    size=13, fill=GREEN, stroke=FIELD, sw=1.6))
    f.append(text(830, 380, "той самий рисунок — інший власник шва",
                  size=12.5, color=MUTED))

    render(os.path.join(IMG, 'sync-seam.svg'), W, H, *f,
           title="Шов синхронізації: у презентаційній моделі його пише програміст, у MVVM — рушій")


if __name__ == "__main__":
    fig_anatomy()
    fig_binding_vs_glue()
    fig_binding_cycle()
    fig_binding_subscriptions()
    fig_mvvm_timeline()
    fig_sync_seam()
    print("OK: mvvm-anatomy.svg, binding-vs-glue.svg, "
          "binding-cycle.svg, binding-subscriptions.svg, "
          "mvvm-timeline.svg, sync-seam.svg")
