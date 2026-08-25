# -*- coding: utf-8 -*-
"""Фігури до теми «Автодобір елементів: decodebin і вибір за caps»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef4fb"
WARM = "#fdf3e6"
GREY = "#ececec"
GREEN = "#eef6ee"


# ── 1. Опис і граф, який із нього виростає ─────────────────────────────────
def fig_tree():
    W, H = 1200, 710
    f = []

    # ліва панель: те, що написано
    f.append(text(220, 76, "написано в програмі", size=15, bold=True))
    f.append(fitbox(45, 100, 350, 110,
                    "filesrc location=clip.mkv\n! decodebin\n! videoconvert\n! autovideosink",
                    size=13, fill="#ffffff"))
    f.append(mtext(220, 250,
                   ["імені жодного декодера тут немає;",
                    "немає навіть слова про те,",
                    "що всередині файла"],
                   size=13, color=MUTED))
    f.append(arrow(405, 160, 452, 160))

    # права панель: граф під час роботи
    cx = 815
    f.append(text(cx, 76, "побудовано під час запуску", size=15, bold=True))
    f.append(fitbox(cx - 105, 83 + 0, 210, 44, "filesrc", size=14, fill="#ffffff"))

    f.append(rect(470, 160, 680, 480, fill="#fbfbfb"))
    f.append(text(490, 186, "decodebin", size=14, bold=True, anchor="start"))

    f.append(arrow(cx, 129, cx, 201))
    f.append(fitbox(cx - 105, 203, 210, 44, "typefind", size=14, fill=SOFT))
    f.append(arrow(cx, 249, cx, 281))
    f.append(text(cx + 16, 269, "video/x-matroska", size=12, color=MUTED, anchor="start"))

    f.append(fitbox(cx - 105, 283, 210, 44, "matroskademux", size=14, fill=SOFT))
    f.append(arrow(cx, 329, cx, 356))
    f.append(fitbox(cx - 295, 358, 590, 44, "multiqueue", size=14, fill=WARM))

    left, right = 640, 990
    f.append(arrow(left, 404, left, 436))
    f.append(text(left + 16, 424, "video/x-h264", size=12, color=MUTED, anchor="start"))
    f.append(arrow(right, 404, right, 436))
    f.append(text(right + 16, 424, "audio/x-opus", size=12, color=MUTED, anchor="start"))

    f.append(fitbox(left - 105, 438, 210, 44, "h264parse", size=14, fill=SOFT))
    f.append(fitbox(right - 105, 438, 210, 44, "opusparse", size=14, fill=SOFT))
    f.append(arrow(left, 484, left, 511))
    f.append(arrow(right, 484, right, 511))
    f.append(fitbox(left - 105, 513, 210, 44, "avdec_h264", size=14, fill=SOFT))
    f.append(fitbox(right - 105, 513, 210, 44, "opusdec", size=14, fill=SOFT))
    f.append(arrow(left, 559, left, 583))
    f.append(arrow(right, 559, right, 583))
    f.append(fitbox(left - 115, 585, 230, 44, "привидний пад\nvideo/x-raw", size=12, fill=GREEN))
    f.append(fitbox(right - 115, 585, 230, 44, "привидний пад\naudio/x-raw", size=12, fill=GREEN))

    f.append(text(cx, 672, "далі йде те, що написав застосунок", size=13, color=MUTED))

    render(os.path.join(OUT, 'autoplug-tree.svg'), W, H, *f,
           title="Короткий опис конвеєра і граф, який decodebin будує з нього")


# ── 2. Цикл автодобору ─────────────────────────────────────────────────────
def fig_loop():
    W, H = 1140, 780
    f = []
    cx = 520

    f.append(fitbox(cx - 160, 48, 320, 46, "новий пад: caps зафіксовані", size=14, fill="#ffffff"))
    f.append(arrow(cx, 96, cx, 150))

    f.append(fitbox(cx - 130, 152, 260, 46, "caps уже цільові?", size=14, fill=WARM))
    # так → виставити пад
    f.append(text(700, 163, "так", size=13, color=MUTED))
    f.append(arrow(654, 175, 786, 175))
    f.append(fitbox(788, 148, 230, 54, "виставити привидний пад\nі дати pad-added", size=12, fill=GREEN))
    # ні → далі вниз
    f.append(text(cx + 14, 232, "ні", size=13, color=MUTED, anchor="start"))
    f.append(arrow(cx, 200, cx, 262))

    f.append(fitbox(cx - 200, 264, 400, 70,
                    "кандидати з реєстру: шаблонні caps перетинаються,\n"
                    "категорія підходить, порядок — за rank", size=13, fill=SOFT))
    f.append(arrow(cx, 336, cx, 398))

    f.append(fitbox(cx - 175, 400, 350, 62,
                    "створити найкращого, злінкувати,\nперевести в PAUSED", size=13, fill=SOFT))
    f.append(arrow(cx, 464, cx, 520))

    f.append(fitbox(cx - 90, 522, 180, 46, "вийшло?", size=14, fill=WARM))

    # так → нові caps → назад угору
    f.append(text(700, 533, "так", size=13, color=MUTED))
    f.append(arrow(612, 545, 786, 545))
    f.append(fitbox(788, 518, 250, 54, "на src-паді елемента\nз'явилися нові caps", size=12, fill="#ffffff"))
    f.append(line(1038, 545, 1090, 545))
    f.append(line(1090, 545, 1090, 71))
    f.append(arrow(1090, 71, 686, 71))

    # ні, але є ще кандидати → назад до спроби
    f.append(text(330, 533, "ні", size=13, color=MUTED))
    f.append(arrow(428, 545, 258, 545))
    f.append(fitbox(60, 518, 195, 54, "наступний\nкандидат", size=13, fill="#ffffff"))
    f.append(line(157, 518, 157, 431))
    f.append(arrow(157, 431, 341, 431))

    # кандидатів немає
    f.append(text(cx + 14, 604, "кандидатів більше немає", size=13, color=MUTED, anchor="start"))
    f.append(arrow(cx, 570, cx, 646))
    f.append(fitbox(cx - 175, 648, 350, 62,
                    "unknown-type, повідомлення про брак\nплагіна, помилка на шину", size=13, fill="#fdecea"))

    render(os.path.join(OUT, 'autoplug-loop.svg'), W, H, *f,
           title="Крок автодобору: цільові caps, кандидати, спроба, повернення")


# ── 3. Чому пади виставляють пачкою ────────────────────────────────────────
def fig_timing():
    W, H = 1120, 560
    f = []

    f.append(text(430, 66, "чому pad-added приходить пачкою", size=15, bold=True))

    f.append(fitbox(40, 130, 145, 60, "відеогілка", size=13, fill="#ffffff"))
    f.append(fitbox(40, 250, 145, 60, "звукова гілка", size=13, fill="#ffffff"))

    f.append(fitbox(205, 130, 225, 60, "добудова гілки", size=13, fill=SOFT))
    f.append(fitbox(430, 130, 150, 60, "преролл", size=13, fill=GREEN))
    f.append(fitbox(580, 130, 185, 60, "пад заблоковано", size=13, fill=GREY))

    f.append(fitbox(205, 250, 285, 60, "добудова гілки", size=13, fill=SOFT))
    f.append(fitbox(490, 250, 275, 60, "преролл, довший", size=13, fill=GREEN))

    f.append(line(790, 118, 790, 400, color=MUTED, dash="6,5"))

    f.append(fitbox(820, 130, 260, 60, "обидві гілки дійшли\nдо перших даних", size=12, fill="#ffffff"))
    f.append(fitbox(820, 250, 260, 60, "pad-added ×2,\nпотім no-more-pads", size=12, fill=GREEN))

    f.append(arrow(205, 430, 1000, 430))
    f.append(text(205, 458, "перехід у PAUSED", size=12, color=MUTED, anchor="start"))
    f.append(text(790, 458, "момент виставлення", size=12, color=MUTED))

    render(os.path.join(OUT, 'expose-timing.svg'), W, H, *f,
           title="Пади тримають заблокованими, доки не прерольнулися всі гілки")


# ── 4. decodebin і decodebin3 ──────────────────────────────────────────────
def fig_db3():
    W, H = 1140, 620
    f = []
    lx, rx = 285, 855

    f.append(text(lx, 66, "decodebin", size=15, bold=True))
    f.append(text(rx, 66, "decodebin3", size=15, bold=True))
    f.append(line(570, 90, 570, 560, color=MUTED, dash="5,5"))

    # ліва частина
    f.append(fitbox(lx - 235, 96, 470, 50, "демультиплексор і розбирачі", size=13, fill=SOFT))
    f.append(arrow(120, 148, 120, 196))
    f.append(arrow(lx, 148, lx, 196))
    f.append(arrow(450, 148, 450, 196))
    f.append(fitbox(35, 198, 170, 56, "декодер\nвідео", size=13, fill=GREEN))
    f.append(fitbox(200, 198, 170, 56, "декодер\nзвуку 1", size=13, fill=GREEN))
    f.append(fitbox(365, 198, 170, 56, "декодер\nзвуку 2", size=13, fill=GREEN))
    f.append(fitbox(lx - 235, 300, 470, 80,
                    "створено всі, грає один;\nзміна доріжки перебудовує граф", size=13, fill="#fdecea"))

    # права частина
    f.append(fitbox(rx - 235, 96, 470, 50, "parsebin: демультиплексор і розбирачі", size=13, fill=SOFT))
    f.append(arrow(rx, 148, rx, 178))
    f.append(fitbox(rx - 235, 180, 470, 50, "перелік потоків на шину", size=13, fill=WARM))
    f.append(arrow(rx, 232, rx, 262))
    f.append(fitbox(rx - 235, 264, 470, 50, "застосунок обирає: select-streams", size=13, fill=WARM))
    f.append(arrow(rx, 316, rx, 346))
    f.append(fitbox(rx - 130, 348, 260, 56, "декодер\nлише для обраного", size=13, fill=GREEN))
    f.append(fitbox(rx - 235, 430, 470, 80,
                    "зміна доріжки міняє вхід декодера,\nа не будову конвеєра", size=13, fill="#eef6ee"))

    render(os.path.join(OUT, 'decodebin3-split.svg'), W, H, *f,
           title="decodebin декодує все виставлене, decodebin3 — лише обране")


# ── 5. Чотири покоління автодобірників (вставка hist) ──────────────────────
def fig_history():
    W, H = 1220, 760
    f = []

    f.append(text(180, 52, "покоління", size=14, bold=True))
    f.append(text(560, 52, "що воно принесло", size=14, bold=True))
    f.append(text(970, 52, "вада, яка лишалася", size=14, bold=True))

    rows = [
        ("spider\nгілка 0.8, до 2005",
         "один елемент, який ставили\nпосеред конвеєра, і він сам\nдотягував потік до потрібних caps",
         "шукав шлях наосліп, окремим кодом\nпоза загальною моделлю;\nне ріс разом із набором плагінів",
         GREY),
        ("decodebin\nгілка 0.8 → 0.10",
         "спершу тип потоку, далі рекурсія\nза caps і рангами з реєстру;\nмета — «дай сирі кадри»",
         "усі гілки поділяли одну чергу:\nдовгий звук зупиняв відео,\nа перебудова графа була крихкою",
         SOFT),
        ("decodebin2 → decodebin\n0.10.11 (2006), ім'я з 1.0 (2012)",
         "групи потоків, multiqueue між\nгілками, відкат невдалої спроби,\nсигнал autoplug-select",
         "декодував усе, що є в контейнері:\nп'ять звукових доріжок — п'ять\nдекодерів, з них грає один",
         WARM),
        ("decodebin3 + parsebin\n1.10 (2016), стабільно з 1.22 (2023)",
         "розбір окремо від декодування;\nколекція потоків на шину,\nвибір подією select-streams",
         "буферизацію мережі винесено вище,\nа старий сигнальний код\nне переїжджає механічно",
         GREEN),
    ]

    y = 80
    for i, (name, gave, flaw, col) in enumerate(rows):
        f.append(fitbox(40, y, 280, 140, name, size=13, fill=col))
        f.append(fitbox(360, y, 400, 140, gave, size=13, fill="#ffffff"))
        f.append(fitbox(800, y, 380, 140, flaw, size=13, fill="#ffffff"))
        if i < len(rows) - 1:
            f.append(arrow(180, y + 140, 180, y + 165))
        y += 165

    render(os.path.join(OUT, 'autoplug-history.svg'), W, H, *f,
           title="Чотири покоління автодобору в GStreamer і вади, які закривав кожен крок")


# ── 6. Три точки втручання і два потоки (вставка proj) ─────────────────────
def fig_hooks():
    W, H = 1260, 690
    f = []

    # ── верхня смуга: потік даних
    f.append(rect(30, 96, 1200, 172, fill="#fbfbfb"))
    f.append(text(40, 84, "потік, що обробляє дані", size=14, bold=True, anchor="start"))
    f.append(text(1230, 84, "жовтим — те, що виконує наша програма",
                 size=12, color=MUTED, anchor="end"))

    top = [(50, "typefind:\nщо це за байти", GREY),
           (290, "autoplug-select:\nпо разу на кожного\nкандидата", WARM),
           (530, "створення елемента\nі спроба", GREY),
           (770, "pad-added:\nхвіст під ці caps", WARM),
           (1010, "no-more-pads:\nграф повний", WARM)]
    for x, s, col in top:
        f.append(fitbox(x, 120, 210, 110, s, size=13, fill=col))
    for x in (260, 500, 740, 980):
        f.append(arrow(x, 175, x + 28, 175))

    # ── спільний журнал посередині
    f.append(fitbox(300, 330, 600, 76,
                    "журнал кандидатів: GString під GMutex\n"
                    "пишуть потоки даних, читає головний",
                    size=13, fill=SOFT))
    f.append(arrow(395, 232, 395, 328))
    f.append(arrow(875, 232, 875, 328))

    # ── нижня смуга: головний потік
    f.append(rect(30, 470, 1200, 172, fill="#fbfbfb"))
    f.append(text(40, 458, "головний потік: GMainLoop", size=14, bold=True, anchor="start"))
    f.append(fitbox(50, 495, 250, 110,
                    "вартовий шини:\nELEMENT → pbutils,\nERROR, EOS", size=13, fill=GREEN))
    f.append(fitbox(340, 495, 250, 110, "друк журналу\nпісля циклу", size=13, fill=GREEN))
    f.append(fitbox(1010, 495, 210, 110, "g_idle_add:\nдрук топології", size=13, fill=GREEN))
    f.append(arrow(465, 408, 465, 493))
    f.append(arrow(1115, 232, 1115, 493))
    f.append(text(1115, 630, "важку роботу — у головний потік", size=12, color=MUTED))

    render(os.path.join(OUT, 'autoplug-hooks.svg'), W, H, *f,
           title="Три колбеки приходять із потоку даних, а друк і розбір шини живуть у головному")


if __name__ == '__main__':
    fig_tree()
    fig_loop()
    fig_timing()
    fig_db3()
    fig_history()
    fig_hooks()
    print("ok")
