# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── swallowed-error: причина і симптом рознесені в часі/просторі ───────────────
# Ідея: проковтнутий збій I2C летить ланцюгом викликів і виринає «за кілометр»
# безглуздим значенням; перевірка прив'язує симптом назад до причини.

def fig_swallowed():
    W, H = 820, 360
    p = []

    # верхній ряд — проковтнуто
    p.append(text(30, 72, "ПРОКОВТНУТО", size=11, color=POS, anchor="start", bold=True))
    row1 = [
        (60,  "i2c_read()\nпровалився", "#fdecea", POS),
        (210, "err == ESP_FAIL\n(ігнорується)", "#fdecea", POS),
        (360, "buf — сміття\n0xFF 0xFF …", "#fdecea", POS),
        (510, "use(buf)\nобчислює", FILL, MUTED),
        (660, "−1000 °C ?!\n«звідки?»", "#fdecea", POS),
    ]
    cx_prev = None
    for cx, lab, fill, col in row1:
        b, bw, bh = textbox(cx, 100, lab, size=11, fill=fill, stroke=col, sw=2.0, pad=8)
        if cx_prev is not None:
            p.append(arrow(cx_prev + 1, 100, cx - bw / 2 - 2, 100, color=MUTED, sw=1.5))
        p.append(b)
        cx_prev = cx + bw / 2

    p.append(text(60, 152, "↑ причина тут", size=10, color=POS))
    p.append(text(660, 152, "↑ симптом тут", size=10, color=POS, bold=True))
    p.append(line(60, 135, 660, 135, color=POS, sw=1.2, dash="6 4"))
    p.append(text(360, 130, "рознесено в часі й просторі", size=10, color=POS, italic=True))

    # нижній ряд — перевірено
    p.append(text(30, 222, "ПЕРЕВІРЕНО", size=11, color=FIELD, anchor="start", bold=True))
    row2 = [
        (60,  "i2c_read()\nпровалився", "#fdecea", POS),
        (210, "if (err != OK)\nспіймав!", "#e8f5e9", FIELD),
        (360, "лог + safe\nтут-таки", "#e8f5e9", FIELD),
    ]
    cx_prev = None
    for cx, lab, fill, col in row2:
        b, bw, bh = textbox(cx, 250, lab, size=11, fill=fill, stroke=col, sw=2.0, pad=8)
        if cx_prev is not None:
            p.append(arrow(cx_prev + 1, 250, cx - bw / 2 - 2, 250, color=MUTED, sw=1.5))
        p.append(b)
        cx_prev = cx + bw / 2

    p.append(text(360, 302, "↑ причина й реакція — поряд", size=10, color=FIELD, bold=True))

    band, bw, bh = textbox(410, 332, "Перевірка прив'язує симптом до причини. Тиша — рознімає їх.",
                           size=12, bold=True, fill="#e8f5e9", stroke=FIELD, sw=2.0, pad=8)
    p.append(band)

    render(os.path.join(OUT, "swallowed-error.svg"), W, H, *p,
           title="Проковтнута помилка: симптом виринає далеко від причини")


# ── error-ladder: п'ять щаблів гучності сигналу про помилку ────────────────────
# Ідея: від найтихішого (код повернення) до найгучнішого (паніка/reset);
# тихіше=локальніше, гучніше=глобальніше.

def fig_ladder():
    W, H = 560, 400
    p = []
    rungs = [
        ("код повернення / статус",          FILL,      INK,  False),
        ("виняткове значення (errno-стиль)",  FILL,      INK,  False),
        ("запис у лог",                       "#eaf0fd", NEG,  False),
        ("assert (зупинка з файлом і рядком)", "#fff3cd", "#c07000", True),
        ("паніка / reset",                    "#fdecea", POS,  True),
    ]
    y = 70
    step = 60
    cx = 280
    for i, (lab, fill, col, bold) in enumerate(rungs):
        w = 360 - i * 6
        b = fitbox(cx - w / 2, y, w, 46, lab, size=13, fill=fill, stroke=col, sw=2.0, bold=bold)
        p.append(b)
        if i < len(rungs) - 1:
            p.append(arrow(cx, y + 46, cx, y + step, color=MUTED, sw=1.5))
        y += step

    # права вісь — гучніше/глобальніше
    p.append(arrow(470, y - step + 30, 470, 100, color=POS, sw=2.0))
    p.append(mtext(486, (100 + y - step) / 2, "гучніше\nглобальніше", size=11, color=POS, anchor="start"))
    # ліва вісь — тихіше/локальніше
    p.append(arrow(90, 100, 90, y - step + 30, color=NEG, sw=2.0))
    p.append(mtext(74, (100 + y - step) / 2, "тихіше\nлокальніше", size=11, color=NEG, anchor="end"))

    render(os.path.join(OUT, "error-ladder.svg"), W, H, *p,
           title="Як помилка може заявити про себе: щаблі гучності")


# ── sri-obc-chain: уявна надлишковість Ariane 5 (вставка hist-ariane5) ─────────
# Ідея: два SRI з ІДЕНТИЧНИМ кодом подають на шину, OBC жене команди соплам;
# спільна вада валить обидва водночас — надлишковість лише на вигляд.

def fig_sri_chain():
    W, H = 820, 400
    p = []
    p.append(text(410, 32, "Ланцюг навігації та керування — Ariane 5", size=15, bold=True))
    p.append(text(410, 52, "Два SRI крутять ІДЕНТИЧНИЙ код — одна вада валить обох водночас",
                  size=11, color=MUTED))

    # два SRI
    p.append(rect(70, 126, 120, 67, fill="#fdecea", stroke=POS, sw=2.5))
    p.append(mtext(130, 148, ["SRI", "(активний)", "флайт-код v2.6"], size=12))
    p.append(text(130, 207, "▲ той самий код", size=10, color=POS))
    p.append(rect(63, 256, 134, 67, fill="#fdecea", stroke=POS, sw=2.5))
    p.append(mtext(130, 278, ["SRI", "(гарячий резерв)", "флайт-код v2.6"], size=12))
    p.append(text(130, 337, "▲ той самий код", size=10, color=POS))

    # дужка common-mode
    p.append(line(202, 130, 214, 130, color=POS, sw=1.5))
    p.append(line(214, 130, 214, 320, color=POS, sw=1.5))
    p.append(line(202, 320, 214, 320, color=POS, sw=1.5))
    p.append(line(214, 225, 228, 225, color=POS, sw=1.5))
    p.append(rect(232, 200, 128, 50, fill="#fdecea", stroke=POS, sw=1.5))
    p.append(mtext(296, 215, ["Спільна вада", "(common-mode fault):", "падають обидва"], size=10))

    # шина
    p.append(rect(370, 130, 70, 190, fill="#e8edf5", stroke=NEG, sw=2.0, rx=4))
    p.append(mtext(405, 224, ["Шина", "даних"], size=12, color=NEG, bold=True))
    p.append(arrow(190, 160, 370, 160, color=INK, sw=1.8))
    p.append(arrow(197, 290, 370, 290, color=INK, sw=1.8))

    # OBC
    p.append(rect(525, 188, 109, 75, fill="#eaf0fd", stroke=NEG, sw=2.5))
    p.append(mtext(580, 212, ["OBC", "(бортовий", "комп'ютер)"], size=13, bold=True))
    p.append(arrow(440, 225, 525, 225, color=NEG, sw=2.0))

    # приводи
    p.append(rect(689, 135, 102, 60, fill="#e8f5e9", stroke=FIELD, sw=2.0))
    p.append(mtext(740, 154, ["гідроприводи", "бустери (SRB)", "сопла"], size=11))
    p.append(rect(680, 255, 120, 60, fill="#e8f5e9", stroke=FIELD, sw=2.0))
    p.append(mtext(740, 274, ["гідроприводи", "маршовий", "двигун (Vulcain)"], size=11))
    p.append(arrow(634, 205, 689, 165, color=FIELD, sw=1.8))
    p.append(arrow(634, 245, 680, 285, color=FIELD, sw=1.8))

    p.append(rect(38, 344, 743, 27, fill="#fff8dc", stroke=POS, sw=1.5))
    p.append(text(410, 362,
                  "Обидва SRI відмовили з однієї причини (overflow BH). OBC прийняв "
                  "діагностичний код за дані → різке відхилення сопел.", size=11))

    render(os.path.join(OUT, "sri-obc-chain.svg"), W, H, *p, title=None)


# ── int16-overflow: BH вискочив за межу int16 (вставка hist-ariane5) ───────────
# Ідея: вісь діапазону int16; BH Ariane 4 у нормі, BH Ariane 5 — далеко за 32767,
# незахищене звуження кидає Operand Error і зупиняє SRI.

def fig_int16_overflow():
    W, H = 820, 360
    p = []
    p.append(text(410, 32, "Переповнення, що знищило ракету: float64 → int16", size=15, bold=True))
    p.append(text(410, 52, "Горизонтальний зсув BH вискочив за межу 16-бітного цілого → "
                  "Operand Error → зупинка SRI", size=11, color=MUTED))

    # вісь
    p.append(line(60, 195, 700, 195, color=INK, sw=2.0))
    p.append(arrow(698, 195, 730, 195, color=INK, sw=2.0))
    p.append(rect(87, 165, 537, 60, fill="#e8f5e9", stroke=FIELD, sw=2.0, rx=4))
    p.append(text(355, 199, "безпечний діапазон int16", size=11, color=FIELD, bold=True))
    p.append(line(87, 185, 87, 205, color=INK, sw=1.8))
    p.append(text(87, 221, "−32768", size=11))
    p.append(line(624, 185, 624, 205, color=INK, sw=1.8))
    p.append(text(624, 221, "32767", size=11))
    p.append(line(355, 189, 355, 201, color=MUTED, sw=1.2))
    p.append(text(355, 215, "0", size=10, color=MUTED))

    # BH Ariane 4 — у нормі
    p.append(circle(413, 195, 7, fill=FIELD, stroke=FIELD, sw=2.0))
    p.append(text(413, 175, "BH Ariane 4", size=11, color=FIELD))
    p.append(text(413, 159, "≈ 7 000", size=10, color=FIELD))

    # хрест-розрив на межі
    p.append(line(624, 173, 642, 187, color=POS, sw=2.5))
    p.append(line(642, 187, 624, 203, color=POS, sw=2.5))
    p.append(line(624, 203, 642, 217, color=POS, sw=2.5))

    # BH Ariane 5 — за межею
    p.append(circle(667, 195, 7, fill=POS, stroke=POS, sw=2.0))
    p.append(text(667, 175, "BH Ariane 5", size=11, color=POS, bold=True))
    p.append(text(667, 159, "≈ 38 000", size=11, color=POS, bold=True))
    p.append(arrow(628, 139, 658, 187, color=POS, sw=1.8))
    p.append(rect(623, 97, 102, 39, fill="#fdecea", stroke=POS, sw=2.0))
    p.append(mtext(674, 113, ["Operand Error!", "SRI зупинено"], size=11))

    p.append(arrow(667, 265, 648, 265, color=POS, sw=2.0))
    p.append(rect(519, 274, 277, 25, fill="#fdecea", stroke=POS, sw=1.5))
    p.append(text(657, 290, "float64 → int16: вийшло за [−32768; 32767]", size=11))

    p.append(rect(13, 304, 793, 27, fill=FILL, stroke=MUTED, sw=1.5))
    p.append(text(410, 321,
                  "Ariane 4 — повільніший старт, BH у нормі. Ariane 5 — потужніший, "
                  "горизонтальна швидкість у кілька разів більша → BH виходить за 32767.", size=11))

    render(os.path.join(OUT, "int16-overflow.svg"), W, H, *p, title=None)


if __name__ == "__main__":
    fig_swallowed()
    fig_ladder()
    fig_sri_chain()
    fig_int16_overflow()
    print("OK: figures written to", OUT)
