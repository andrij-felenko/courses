# -*- coding: utf-8 -*-
"""Фігури до кроку «CQS: команда діє, запит відповідає» (guide/progarch)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")


def fig_model():
    """Дві доріжки: команда пише в стан і мовчить; запит читає й відповідає."""
    W, H = 820, 360
    parts = []

    # центральний стан
    sx, sy, sw_, sh = 330, 108, 160, 96
    parts.append(rect(sx, sy, sw_, sh, fill="#fbfbfb", stroke=INK, sw=2, rx=10))
    parts.append(mtext(sx + sw_ / 2, sy + sh / 2 - 6, ["СТАН", "об'єкта"],
                       size=15, color=INK, bold=True))
    scx = sx + sw_ / 2

    # ── ліва доріжка: КОМАНДА ──
    cb, cw, ch = 60, 200, 84
    cy = 126
    parts.append(rect(cb, cy, cw, ch, fill="#eafaf0", stroke=FIELD, sw=1.9, rx=9))
    parts.append(text(cb + cw / 2, cy + 30, "КОМАНДА", size=15, color=FIELD, bold=True))
    parts.append(text(cb + cw / 2, cy + 54, "append(reading)", size=13, color=INK))
    # стрілка команда → стан (пише, гаряча)
    parts.append(arrow(cb + cw + 4, cy + ch / 2, sx - 6, sy + sh * 0.45, color=FIELD, sw=2.2))
    parts.append(text((cb + cw + sx) / 2, cy + ch / 2 - 12, "пише", size=12, color=FIELD, bold=True))
    # повертає порожнечу — під командою
    b, w, h = textbox(cb + cw / 2, cy + ch + 34, "повертає ∅ (void)",
                      size=12, color=FIELD, stroke=FIELD, fill="#eafaf0", pad=8)
    parts.append(b)

    # ── права доріжка: ЗАПИТ ──
    qb = 560
    qy = 126
    parts.append(rect(qb, qy, cw, ch, fill="#eef2fb", stroke=NEG, sw=1.9, rx=9))
    parts.append(text(qb + cw / 2, qy + 30, "ЗАПИТ", size=15, color=NEG, bold=True))
    parts.append(text(qb + cw / 2, qy + 54, "average()", size=13, color=INK))
    # стрілка стан → запит (лише читає, пунктир)
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="2" stroke-dasharray="6 4" marker-end="url(#arrow)"/>'
                 % (sx + sw_ + 6, sy + sh * 0.45, qb - 4, qy + ch / 2, NEG))
    parts.append(text((sx + sw_ + qb) / 2, qy + ch / 2 - 12, "лише читає", size=12, color=NEG, bold=True))
    # повертає значення — під запитом
    b, w, h = textbox(qb + cw / 2, qy + ch + 34, "повертає значення",
                      size=12, color=NEG, stroke=NEG, fill="#eef2fb", pad=8)
    parts.append(b)

    # нижній присуд
    parts.append(text(W / 2, 322,
                      "чіпає стан лише команда (ліворуч) — тому запит (праворуч) завжди каже правду",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "model.svg"), W, H, *parts,
           title="Один метод — або міняє стан, або відповідає, не обоє")


def fig_leverage():
    """Матриця дозволів: що можна робити із запитом, чого — з командою."""
    W, H = 860, 420
    parts = []

    xlab = 300              # правий край підписів операції
    col_q = 470            # центр стовпця «запит»
    col_c = 690            # центр стовпця «команда»
    cellw = 150

    # заголовки стовпців
    b, w, h = textbox(col_q, 66, "ЗАПИТ\n(безпечний)", size=13, color=NEG,
                      stroke=NEG, fill="#eef2fb", pad=9, bold=True, min_w=cellw)
    parts.append(b)
    b, w, h = textbox(col_c, 66, "КОМАНДА\n(з наслідком)", size=13, color=FIELD,
                      stroke=FIELD, fill="#eafaf0", pad=9, bold=True, min_w=cellw)
    parts.append(b)

    rows = [
        ("викликати ще раз",        "✓ те саме", "✗ ще один ефект"),
        ("переставити місцями",     "✓ вільно",  "✗ порядок важить"),
        ("закешувати відповідь",    "✓ можна",   "— нема чого"),
        ("не викликати, як не треба", "✓ дарма",  "✗ дія пропаде"),
        ("протестувати",            "✓ виклич і\nпорівняй", "⚠ перевіряй\nзміну стану"),
    ]
    y0, dy, rh = 108, 54, 44
    for i, (lab, q, c) in enumerate(rows):
        cy = y0 + i * dy + rh / 2
        parts.append(text(xlab, cy + 5, lab, size=13, color=INK, anchor="end"))
        # клітина запиту (зелене «так»)
        parts.append(fitbox(col_q - cellw / 2, y0 + i * dy, cellw, rh, q,
                            size=12, fill="#eafaf0", stroke=FIELD, sw=1.5, color="#15703b"))
        # клітина команди (червоне «ні»/жовте «обережно»)
        warn = c.startswith("⚠") or c.startswith("—")
        parts.append(fitbox(col_c - cellw / 2, y0 + i * dy, cellw, rh, c,
                            size=12, fill=("#fef7e6" if warn else "#fdecea"),
                            stroke=("#b8860b" if warn else POS), sw=1.5,
                            color=("#8a6d0b" if warn else POS)))

    parts.append(text(W / 2, y0 + len(rows) * dy + 20,
                      "усі «так» лівого стовпця — з однієї причини: запит не лишає слідів",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "leverage.svg"), W, H, *parts,
           title="Що дозволено із запитом, а що — з командою")


def fig_family():
    """Родина принципів Меєра з одного кореня — надійності; CQS підпирає однаковий доступ.
    (Фігура для вставки hist-meyer-cqs.md.)"""
    W, H = 940, 440
    parts = []

    # ── корінь: надійність ──
    b, w, h = textbox(470, 72, "НАДІЙНІСТЬ\nміркувати про код, не запускаючи його",
                      size=13, bold=True, min_w=430, stroke=INK, fill="#f4f6f8")
    parts.append(b)

    # ── посудина: мова Eiffel ──
    b, w, h = textbox(470, 150, "втілена в мові Eiffel (1986)\nродина принципів Бертрана Меєра",
                      size=12, min_w=430, stroke=MUTED, fill="#ffffff", color=MUTED)
    parts.append(b)
    parts.append(line(470, 97, 470, 126, color=INK, sw=1.6))

    # ── чотири гілки ──
    cy = 266
    xs = [120, 353, 586, 819]
    labels = ["Проєктування\nза контрактом",
              "Відкритість–\nзакритість",
              "Однаковий\nдоступ",
              "CQS\nкоманда / запит"]
    for i, (x, lab) in enumerate(zip(xs, labels)):
        parts.append(line(470, 174, x, 236, color=MUTED, sw=1.4))
        if i == 3:  # CQS — герой вставки, синій акцент
            b, w, h = textbox(x, cy, lab, size=13, bold=True, min_w=200,
                              stroke=NEG, fill="#eef2fb", color=NEG)
        else:
            b, w, h = textbox(x, cy, lab, size=13, min_w=200,
                              stroke=MUTED, fill="#fbfbfb", color=INK)
        parts.append(b)

    # ── CQS підпирає однаковий доступ (пунктир CQS → UAP) ──
    parts.append(text(688, 312, "робить безпечним", size=11, color=NEG, bold=True))
    parts.append('<line x1="755" y1="322" x2="622" y2="322" stroke="%s" '
                 'stroke-width="1.8" stroke-dasharray="6 4" marker-end="url(#arrow)"/>' % NEG)

    parts.append(text(470, 408,
                      "усі чотири виросли з одного кореня — коду, якому можна довіряти, не запустивши його",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "family.svg"), W, H, *parts,
           title="Родина принципів Меєра: спільний корінь — надійність")


def fig_race_window():
    """Виняток «дістати-й-вилучити»: чому роздільні peek+removeFirst відкривають вікно."""
    W, H = 940, 360
    parts = []

    # вікно (позаду боксів): від A.peek до A.removeFirst — тут стан не змінюється
    parts.append(rect(195, 72, 477, 186, fill="#fdecea", stroke=POS, sw=1.8, rx=12))

    # мітки доріжок
    parts.append(text(100, 116, "Воркер A", size=14, color=INK, anchor="end", bold=True))
    parts.append(text(100, 236, "Воркер B", size=14, color=INK, anchor="end", bold=True))

    # доріжка A
    b, _, _ = textbox(250, 110, ["① peek()", "→ бачить #7"], size=13,
                      fill="#eef2fb", stroke=NEG, color=INK)
    parts.append(b)
    b, _, _ = textbox(600, 110, "③ removeFirst()", size=13,
                      fill="#eafaf0", stroke=FIELD, color=INK)
    parts.append(b)

    # доріжка B — вклинюється всередині вікна
    b, _, _ = textbox(430, 230, ["② peek()", "→ бачить #7"], size=13,
                      fill="#eef2fb", stroke=NEG, color=INK)
    parts.append(b)
    b, _, _ = textbox(740, 230, "④ removeFirst()", size=13,
                      fill="#eafaf0", stroke=FIELD, color=INK)
    parts.append(b)

    # присуд праворуч, у проміжку між доріжками
    b, _, _ = textbox(852, 170, ["#7 оброблено", "ДВІЧІ"], size=14,
                      fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(b)

    # підпис вікна — під ним, у чистому місці
    parts.append(text(400, 300,
                      "вікно: між peek і removeFirst стан той самий — B хапає той самий #7",
                      size=12, color=POS))

    render(os.path.join(IMG, "race-window.svg"), W, H, *parts,
           title="Розділив «дістати» і «вилучити» — і відкрив вікно")


def fig_honest_return():
    """Таксономія трьох винятків за причиною злиття + що чесно повертає команда."""
    W, H = 900, 380
    parts = []

    # дві панелі (позаду)
    parts.append(rect(30, 60, 430, 250, fill="#fbfbfb", stroke=MUTED, sw=1.6, rx=12))
    parts.append(rect(480, 60, 390, 250, fill="#fbfbfb", stroke=MUTED, sw=1.6, rx=12))

    # заголовки панелей
    parts.append(fitbox(45, 74, 400, 42, "Розділити МОЖНА — але відкриється вікно",
                        size=14, fill="#fef7e6", stroke="#b8860b", color="#8a6d0b", bold=True))
    parts.append(fitbox(492, 74, 366, 42, "Розділити НЕМОЖЛИВО — значення створює сама дія",
                        size=14, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # ліві картки: два «вікно»-винятки
    parts.append(rect(48, 128, 394, 70, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=8))
    parts.append(text(245, 154, "«дістати-й-вилучити» — dequeue()", size=13, color=INK, bold=True))
    parts.append(text(245, 180, "повертає: вилучений елемент", size=13, color=FIELD, bold=True))
    parts.append(rect(48, 214, 394, 70, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=8))
    parts.append(text(245, 240, "«атомарний лічильник» — allocate()", size=13, color=INK, bold=True))
    parts.append(text(245, 266, "повертає: унікальний номер", size=13, color=FIELD, bold=True))

    # права картка: «неможливо»-виняток
    parts.append(rect(498, 150, 354, 96, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=8))
    parts.append(text(675, 180, "«створити-й-повернути id»", size=13, color=INK, bold=True))
    parts.append(text(675, 206, "createDevice() → свіжий id", size=13, color=FIELD, bold=True))
    parts.append(text(675, 232, "до вставки id не існує", size=12, color=MUTED, italic=True))

    # спільний присуд знизу
    b, _, _ = textbox(450, 344,
                      "спільне: повернене — прямий продукт дії, а не побічний звіт",
                      size=13, fill="#eef7ef", stroke=FIELD, color=INK)
    parts.append(b)

    render(os.path.join(IMG, "honest-return.svg"), W, H, *parts,
           title="Чесне повернене: прямий продукт дії")


if __name__ == "__main__":
    fig_model()
    fig_leverage()
    fig_family()
    fig_race_window()
    fig_honest_return()
    print("ok")
