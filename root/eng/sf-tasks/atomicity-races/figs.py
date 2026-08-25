# -*- coding: utf-8 -*-
"""Фігури до теми «Атомарність і гонки даних».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольори ролей (поверх палітри svgkit)
MAIN = NEG          # основний код / loop()
ISRC = POS          # обробник / переривання
SAFE = FIELD        # захищене / цілісне
WARN = "#caa24a"    # рамка-висновок


def boxlabel(f, x, y, w, h, s, fill=FILL, stroke=LINE, tcol=INK, size=12, sw=1.6):
    """Прямокутник із підписом по центру; багаторядковий через \\n (fitbox масштабує)."""
    if "\n" in s:
        f.append(fitbox(x, y, w, h, s.split("\n"), size=size, fill=fill,
                        stroke=stroke, sw=sw, color=tcol, bold=True, pad=6))
        return
    f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=6))
    fs = fit_font(s, w - 12, size, bold=True)
    f.append(text(x + w / 2, y + h / 2 + fs * 0.35, s, size=fs, color=tcol, bold=True))


def note(f, cx, y, w, lines, fill="#fff6e0", stroke=WARN, size=11):
    """Рамка-висновок знизу фігури."""
    f.append(fitbox(cx - w / 2, y, w, 18 + size * 1.3 * len(lines), lines,
                    size=size, fill=fill, stroke=stroke))


# ════════════════════════════════════════════════════════════════════════════
#  СТАТТЯ
# ════════════════════════════════════════════════════════════════════════════

# ── 1. Гонка даних на лічильнику ────────────────────────────────────────────
def fig_race_condition():
    W, H = 880, 420
    f = [text(W / 2, 30, "Гонка даних: два +1, а лічильник зріс лише на одиницю",
              size=17, bold=True)]
    f.append(text(W / 2, 52, "і loop(), і обробник роблять count++ — через перекриття замість +2 виходить +1",
                  size=11, color=MUTED, italic=True))

    # три стани count угорі
    for x, val, col in [(150, "5", INK), (470, "5", INK), (760, "6", ISRC)]:
        f.append(rect(x, 78, 56, 30, fill="#fbfcff", stroke=col, sw=1.5, rx=5))
        f.append(text(x + 28, 99, val, size=14, color=col, bold=True))
    f.append(text(110, 96, "count:", size=11, color=INK, anchor="end", bold=True))

    # доріжка loop()
    yL = 180
    f.append(text(64, yL - 22, "loop()", size=11, color=MAIN, bold=True))
    f.append(line(110, yL, 850, yL, color="#dfe6f5", sw=2))
    boxlabel(f, 150, yL - 16, 110, 32, "читає 5", fill="#e9eefb", stroke=MAIN, size=11)
    f.append(line(260, yL, 690, yL, color=MAIN, sw=1.4, dash="3,3"))
    f.append(text(475, yL - 6, "...перервано, своє «5» забуто...", size=9, color=MUTED, italic=True))
    boxlabel(f, 690, yL - 16, 160, 32, "пише 5 + 1 = 6", fill="#e9eefb", stroke=MAIN, size=11)

    # точка переривання + доріжка обробника
    yI = 300
    f.append(text(64, yI - 8, "обробник", size=11, color=ISRC, bold=True))
    f.append(circle(330, yL, 4, fill=ISRC, stroke=ISRC, sw=0))
    f.append(text(330, yL - 24, "переривання врізалось", size=9, color=ISRC, bold=True))
    f.append(line(330, yL, 330, yI - 16, color=ISRC, sw=1.4, dash="3,3"))
    boxlabel(f, 330, yI - 16, 300, 32, "читає 5 → +1 → пише 6", fill="#fbecec", stroke=ISRC, size=11, tcol=ISRC)
    f.append(line(630, yI, 630, yL, color=ISRC, sw=1.4, dash="3,3"))

    note(f, W / 2, 350, 700,
         ["Було два «+1», а count став лише 6 замість 7: loop писав, спираючись на застаріле «5».",
          "Результат залежить від того, ХТО коли встиг. Одне оновлення зникло."])
    render(os.path.join(IMG, "race-condition.svg"), W, H, *f)


# ── 2. Що таке атомарність ──────────────────────────────────────────────────
def fig_what_is_atomic():
    W, H = 860, 400
    f = [text(W / 2, 30, "Атомарна дія неподільна; багатокрокову переривання може розрізати",
              size=16, bold=True)]

    # ліворуч: count++ = 3 кроки, розрізані
    f.append(text(230, 70, "count++ — три кроки (подільна)", size=12.5, bold=True, color=ISRC))
    steps = [("прочитати", 95), ("додати", 165), ("записати", 235)]
    for s, y in steps:
        boxlabel(f, 130, y, 200, 44, s, fill="#fbecec", stroke=ISRC, size=12)
    f.append(arrow(230, 139, 230, 163, color=INK))
    f.append(arrow(230, 209, 230, 233, color=INK))
    # стрілка переривання між кроками
    f.append(line(360, 152, 360, 222, color=ISRC, sw=2, dash="4,4"))
    f.append(text(372, 192, "переривання", size=10, color=ISRC, anchor="start", bold=True))
    f.append(text(372, 206, "втручається тут", size=10, color=ISRC, anchor="start"))
    f.append(arrow(360, 187, 332, 187, color=ISRC))

    # вертикальний роздільник
    f.append(line(W / 2, 70, W / 2, 300, color="#dde2ea", sw=1.5, dash="2,4"))

    # праворуч: одне читання/запис слова = атомарне
    f.append(text(640, 70, "читання/запис слова (атомарна)", size=12.5, bold=True, color=SAFE))
    boxlabel(f, 540, 150, 200, 60, "одна неподільна дія", fill="#eef6ef", stroke=SAFE, size=12.5)
    f.append(text(640, 235, "перервати «всередині» ніде", size=11, color=MUTED, italic=True))

    note(f, W / 2, 320, 720,
         ["Захищати треба саме БАГАТОКРОКОВІ дії: count++ з обох боків, читання ширшого за слово.",
          "Одне читання чи запис вирівняного слова на 32-бітному ESP32 атомарне саме собою."])
    render(os.path.join(IMG, "what-is-atomic.svg"), W, H, *f)


# ── 3. Критична секція ──────────────────────────────────────────────────────
def fig_critical_section():
    W, H = 880, 360
    f = [text(W / 2, 30, "Критична секція: noInterrupts() … interrupts() огороджують цілісну дію",
              size=15.5, bold=True)]

    # часова вісь
    yL = 150
    f.append(line(80, yL, 800, yL, color="#cfd6e2", sw=2))
    f.append(text(64, yL + 4, "час", size=10, color=MUTED, anchor="end"))

    # межі секції
    x0, x1 = 300, 560
    f.append(line(x0, 90, x0, 230, color=INK, sw=2))
    f.append(line(x1, 90, x1, 230, color=INK, sw=2))
    f.append(text(x0, 84, "noInterrupts()", size=11, bold=True))
    f.append(text(x1, 84, "interrupts()", size=11, bold=True))

    # захищена ділянка
    f.append(rect(x0, yL - 22, x1 - x0, 44, fill="#eef6ef", stroke=SAFE, sw=1.8, rx=6))
    f.append(text((x0 + x1) / 2, yL + 5, "робота зі спільними даними — цілісно", size=11.5, bold=True, color=SAFE))

    # переривання прийшло всередині — чекає
    xev = 420
    f.append(circle(xev, yL, 4, fill=ISRC, stroke=ISRC, sw=0))
    f.append(text(xev, 248, "подія прийшла тут", size=10, color=ISRC, bold=True))
    f.append(line(xev, yL + 6, xev, 244, color=ISRC, sw=1.3, dash="3,3"))
    # чекання до кінця секції
    f.append(line(xev, 268, x1, 268, color=ISRC, sw=1.6, dash="2,3"))
    f.append(arrow(x1, 268, x1 + 30, 268, color=ISRC))
    boxlabel(f, x1 + 32, 252, 150, 32, "обробник спрацює", fill="#fbecec", stroke=ISRC, size=10.5, tcol=ISRC)
    f.append(text((xev + x1) / 2, 282, "чекає кілька тактів", size=9.5, color=MUTED, italic=True))

    note(f, W / 2, 304, 720,
         ["Подія, що прийшла всередині секції, не губиться — обробник лише ЧЕКАЄ до її кінця.",
          "За неподільність ми платимо крихітною затримкою тих переривань, що зібрались."])
    render(os.path.join(IMG, "critical-section.svg"), W, H, *f)


# ── 4. Патерн «знімок» ──────────────────────────────────────────────────────
def fig_snapshot_pattern():
    W, H = 860, 340
    f = [text(W / 2, 30, "Патерн «знімок»: копіювати під захистом, працювати поза ним",
              size=15.5, bold=True)]

    yL = 150
    f.append(line(80, yL, 800, yL, color="#cfd6e2", sw=2))

    # коротка секція: копіювання
    x0, x1 = 220, 320
    f.append(rect(x0, yL - 20, x1 - x0, 40, fill="#eef6ef", stroke=SAFE, sw=1.8, rx=6))
    f.append(text((x0 + x1) / 2, 96, "секція (мить)", size=10.5, bold=True))
    f.append(text((x0 + x1) / 2, yL + 5, "n = pulses", size=11, bold=True, color=SAFE))
    f.append(line(x0, 104, x0, yL - 20, color=INK, sw=1.5))
    f.append(line(x1, 104, x1, yL - 20, color=INK, sw=1.5))

    # робота поза секцією: довга
    f.append(rect(x1 + 30, yL - 20, 420, 40, fill="#e9eefb", stroke=MAIN, sw=1.6, rx=6))
    f.append(text(x1 + 30 + 210, yL + 5, "Serial.println(n) — з копією, поза секцією", size=11.5, bold=True, color=MAIN))
    f.append(arrow(x1, yL, x1 + 28, yL, color=INK))

    f.append(text((x0 + x1) / 2, 256, "переривання вимкнені — мить", size=10, color=MUTED, italic=True))
    f.append(text(x1 + 30 + 210, 256, "переривання знову ввімкнені — працюй скільки треба", size=10, color=MUTED, italic=True))
    f.append(line(x1, yL + 24, x1, 248, color="#cfd6e2", sw=1, dash="2,3"))

    note(f, W / 2, 286, 720,
         ["Під захистом — лише копіювання спільного в локальне (лічені такти).",
          "Уся «важка» робота — поза секцією, з копією. Секція лишається якнайкоротшою."])
    render(os.path.join(IMG, "snapshot-pattern.svg"), W, H, *f)


# ── 5. Тримати секцію короткою ──────────────────────────────────────────────
def fig_keep_short():
    W, H = 880, 380
    f = [text(W / 2, 30, "Коротка критична секція безпечна; довга сліпить систему",
              size=16, bold=True)]

    def lane(y, x0, x1, lab, good):
        col = SAFE if good else ISRC
        f.append(text(70, y + 4, lab, size=11, bold=True, color=col, anchor="start"))
        f.append(line(210, y, 800, y, color="#cfd6e2", sw=2))
        f.append(rect(x0, y - 16, x1 - x0, 32,
                      fill="#eef6ef" if good else "#fbecec", stroke=col, sw=1.7, rx=5))
        f.append(text((x0 + x1) / 2, y + 5, "секція (переривання вимкнені)", size=9.5, bold=True, color=col))
        return col

    # подія приходить в один і той самий момент в обох доріжках
    xev = 300
    # коротка
    yS = 120
    lane(yS, 250, 360, "коротка", True)
    f.append(circle(xev, yS, 4, fill=ISRC, stroke=ISRC, sw=0))
    f.append(line(xev, yS, 365, yS, color=ISRC, sw=1.5, dash="2,3"))
    f.append(arrow(365, yS, 392, yS, color=ISRC))
    f.append(text(400, yS + 4, "обслуговано майже відразу", size=10, color=SAFE, anchor="start"))

    # довга
    yD = 240
    lane(yD, 250, 660, "довга", False)
    f.append(circle(xev, yD, 4, fill=ISRC, stroke=ISRC, sw=0))
    f.append(line(xev, yD, 665, yD, color=ISRC, sw=1.5, dash="2,3"))
    f.append(arrow(665, yD, 692, yD, color=ISRC))
    f.append(text(450, yD - 26, "подія мусить чекати весь цей час → джитер, втрати", size=10, color=ISRC))

    note(f, W / 2, 300, 720,
         ["Поки переривання вимкнені, сліпне ВСЯ система: час збивається, події набігають.",
          "Захищають лише мінімальну дію — лічені такти, одиниці мікросекунд."])
    render(os.path.join(IMG, "keep-short.svg"), W, H, *f)


# ── 6. Два ядра ESP32: спінлок ──────────────────────────────────────────────
def fig_esp32_spinlock():
    W, H = 900, 400
    f = [text(W / 2, 30, "Два ядра: noInterrupts() діє лише на своє ядро; спінлок захищає обидва",
              size=15, bold=True)]

    # ліворуч: noInterrupts недостатньо
    f.append(text(230, 70, "тільки noInterrupts()", size=12.5, bold=True, color=ISRC))
    boxlabel(f, 80, 95, 150, 46, "ядро 0\nперерив. вимкнені", fill="#eef6ef", stroke=SAFE, size=10.5)
    boxlabel(f, 250, 95, 150, 46, "ядро 1\nпрацює далі", fill="#fbecec", stroke=ISRC, size=10.5)
    # обидва лізуть у спільні дані
    boxlabel(f, 165, 188, 150, 36, "спільні дані", fill="#fbfcff", stroke=INK, size=11)
    f.append(arrow(150, 143, 215, 186, color=SAFE))
    f.append(arrow(310, 143, 255, 186, color=ISRC))
    f.append(text(230, 250, "ядро 1 не спинене → гонка лишилась", size=10, color=ISRC, bold=True))

    # роздільник
    f.append(line(W / 2, 70, W / 2, 270, color="#dde2ea", sw=1.5, dash="2,4"))

    # праворуч: спінлок
    f.append(text(680, 70, "portENTER / EXIT_CRITICAL", size=12, bold=True, color=SAFE))
    boxlabel(f, 520, 95, 150, 46, "ядро 0\nузяв замок", fill="#eef6ef", stroke=SAFE, size=10.5)
    boxlabel(f, 690, 95, 150, 46, "ядро 1\nЧЕКАЄ біля замка", fill="#eef6ef", stroke=SAFE, size=10.5)
    boxlabel(f, 605, 188, 150, 36, "спільні дані", fill="#fbfcff", stroke=INK, size=11)
    f.append(arrow(595, 143, 660, 186, color=SAFE))
    f.append(line(760, 143, 720, 186, color=MUTED, sw=1.4, dash="3,3"))
    f.append(text(765, 168, "✕", size=14, color=ISRC, anchor="start", bold=True))
    f.append(text(680, 250, "друге ядро не пускає замок → цілісно", size=10, color=SAFE, bold=True))

    note(f, W / 2, 290, 760,
         ["noInterrupts() вимикає переривання лише на ТОМУ ядрі, де виконується.",
          "Для справді спільних між ядрами даних беруть спінлок (в обробнику — варіант …_ISR)."])
    render(os.path.join(IMG, "esp32-spinlock.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА hist-therac25
# ════════════════════════════════════════════════════════════════════════════

# ── гонка: швидке редагування розсинхронізувало програму й механіку ─────────
def fig_therac_race():
    W, H = 880, 380
    f = [text(W / 2, 30, "Гонка: швидке редагування розсинхронізувало програму й механіку",
              size=15, bold=True)]

    # доріжка введення
    y1 = 110
    f.append(text(70, y1 + 4, "введення", size=11, bold=True, color=MAIN, anchor="start"))
    f.append(line(210, y1, 800, y1, color="#dfe6f5", sw=2))
    boxlabel(f, 250, y1 - 16, 150, 32, "рентген обрано", fill="#e9eefb", stroke=MAIN, size=10.5)
    boxlabel(f, 470, y1 - 16, 200, 32, "швидка правка → електрони", fill="#e9eefb", stroke=MAIN, size=10)
    f.append(text(550, y1 - 26, "≈ 8 секунд", size=10, color=ISRC, bold=True))

    # доріжка механіки (столик з мішенню)
    y2 = 230
    f.append(text(70, y2 + 4, "механіка", size=11, bold=True, color=ISRC, anchor="start"))
    f.append(line(210, y2, 800, y2, color="#fbe2e0", sw=2))
    boxlabel(f, 250, y2 - 16, 220, 32, "столик ще веде мішень", fill="#fbecec", stroke=ISRC, size=10)
    f.append(text(620, y2 + 5, "мішені ще НЕМАЄ на місці", size=10.5, color=ISRC, bold=True))

    # розсинхрон
    f.append(line(570, y1 + 16, 570, y2 - 16, color=ISRC, sw=1.5, dash="3,3"))
    f.append(text(585, (y1 + y2) / 2, "програма «вважає» пучок слабким,", size=9.5, color=MUTED, anchor="start", italic=True))

    note(f, W / 2, 300, 740,
         ["Дві задачі діяли над спільним станом без черги; за швидкого редагування вони розсинхронізувались.",
          "Потужний промінь спрацьовував напряму, без мішені — багаторазове передозування."],
         fill="#fbecec", stroke=ISRC)
    render(os.path.join(IMG, "therac-race.svg"), W, H, *f)


# ── зниклий запобіжник ──────────────────────────────────────────────────────
def fig_therac_interlock():
    W, H = 880, 360
    f = [text(W / 2, 30, "Зниклий запобіжник: ранні моделі мали апаратне блокування, Therac-25 — лише софт",
              size=14, bold=True)]

    def chain(x0, title, has_hw, good):
        col = SAFE if good else ISRC
        f.append(text(x0 + 150, 80, title, size=12.5, bold=True, color=col))
        boxlabel(f, x0, 105, 300, 38, "програма помилилась", fill="#fbecec", stroke=ISRC, size=11)
        f.append(arrow(x0 + 150, 145, x0 + 150, 170, color=INK))
        if has_hw:
            boxlabel(f, x0, 172, 300, 38, "апаратне блокування — не пускає", fill="#eef6ef", stroke=SAFE, size=10.5)
            f.append(arrow(x0 + 150, 212, x0 + 150, 237, color=INK))
            boxlabel(f, x0 + 60, 238, 180, 36, "промінь безпечний", fill="#eef6ef", stroke=SAFE, size=11, tcol=SAFE)
        else:
            f.append(text(x0 + 150, 192, "(апаратний запобіжник прибрано)", size=10, color=MUTED, italic=True))
            f.append(arrow(x0 + 150, 205, x0 + 150, 237, color=ISRC))
            boxlabel(f, x0 + 50, 238, 200, 36, "передозування", fill="#fbecec", stroke=ISRC, size=11, tcol=ISRC)

    chain(80, "Therac-6 / 20", True, True)
    f.append(line(W / 2, 80, W / 2, 290, color="#dde2ea", sw=1.5, dash="2,4"))
    chain(500, "Therac-25", False, False)

    note(f, W / 2, 308, 760,
         ["Ранні моделі мали незалежний апаратний блокувальник: помилка софту не пускала промінь.",
          "Therac-25 поклався на саму лише програму — і помилка лишилась без останньої сітки."])
    render(os.path.join(IMG, "therac-interlock.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА proj-critical-sections
# ════════════════════════════════════════════════════════════════════════════

# ── хто свариться за дані — той і обирає інструмент ──────────────────────────
def fig_which_tool():
    W, H = 900, 440
    f = [text(W / 2, 30, "Хто свариться за дані — той і обирає інструмент", size=16, bold=True)]

    rows = [
        ("ISR ↔ main (одне ядро)", "вимкнути переривання", "noInterrupts() — швидко, грубо", SAFE),
        ("задача ↔ задача", "м'ютекс", "можна блокуватись; НЕ з ISR", MAIN),
        ("два ядра ESP32", "спінлок", "portENTER_CRITICAL — замок + вимк. перерив.", ISRC),
        ("одне вирівняне слово", "часто без секції", "атомарний доступ / lock-free кільце", MUTED),
    ]
    y = 80
    for who, tool, hint, col in rows:
        boxlabel(f, 70, y, 260, 50, who, fill="#fbfcff", stroke=col, size=12)
        f.append(arrow(335, y + 25, 375, y + 25, color=INK))
        boxlabel(f, 380, y, 220, 50, tool, fill="#eef6ef" if col != MUTED else FILL, stroke=col, size=12.5, tcol=col)
        f.append(text(620, y + 30, hint, size=10.5, color=MUTED, anchor="start"))
        y += 72

    note(f, W / 2, y + 4, 760,
         ["Інструмент диктує контендер: хто з ким змагається за спільні дані.",
          "Одне вирівняне слово часто й секції не потребує — атомарний доступ дешевший."])
    render(os.path.join(IMG, "which-tool.svg"), W, H, *f)


# ── секція вимикає переривання — усі чекають ────────────────────────────────
def fig_cs_keep_short():
    W, H = 860, 330
    f = [text(W / 2, 30, "Секція вимикає переривання — усі чекають; тримай її крихітною",
              size=15.5, bold=True)]

    yL = 150
    f.append(line(80, yL, 790, yL, color="#cfd6e2", sw=2))
    x0, x1 = 320, 520
    f.append(rect(x0, yL - 18, x1 - x0, 36, fill="#fbecec", stroke=ISRC, sw=1.8, rx=6))
    f.append(text((x0 + x1) / 2, yL + 5, "секція: переривання вимкнені", size=10.5, bold=True, color=ISRC))
    f.append(line(x0, 100, x0, yL - 18, color=INK, sw=1.5))
    f.append(line(x1, 100, x1, yL - 18, color=INK, sw=1.5))
    f.append(text(x0, 94, "вхід", size=10, bold=True))
    f.append(text(x1, 94, "вихід", size=10, bold=True))

    xev = 400
    f.append(circle(xev, yL, 4, fill=ISRC, stroke=ISRC, sw=0))
    f.append(text(xev, 238, "обробник хоче спрацювати", size=10, color=ISRC, bold=True))
    f.append(line(xev, yL + 6, xev, 234, color=ISRC, sw=1.3, dash="3,3"))
    f.append(line(xev, 222, x1, 222, color=ISRC, sw=1.6, dash="2,3"))
    f.append(arrow(x1, 222, x1 + 28, 222, color=ISRC))
    f.append(text((xev + x1) / 2 + 10, 214, "чекає до виходу", size=9.5, color=MUTED, italic=True))

    note(f, W / 2, 264, 700,
         ["Секція додає затримку КОЖНОМУ перериванню: усі обробники чекають до виходу.",
          "Усередині — лише пара інструкцій, без Serial, delay чи Flash."],
         fill="#fbecec", stroke=ISRC)
    render(os.path.join(IMG, "cs-keep-short.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА proj-atomics-barriers
# ════════════════════════════════════════════════════════════════════════════

# ── спінлок проти atomic fetch_add ──────────────────────────────────────────
def fig_spinlock_vs_atomic():
    W, H = 900, 400
    f = [text(W / 2, 30, "Спінлок проти atomic fetch_add на двох ядрах (одне слово, +1)",
              size=15, bold=True)]

    # ліворуч: спінлок
    f.append(text(230, 72, "спінлок — повний замок", size=12.5, bold=True, color=ISRC))
    boxlabel(f, 80, 100, 150, 46, "Core 0\nportENTER → ++", fill="#eef6ef", stroke=SAFE, size=10.5)
    boxlabel(f, 250, 100, 150, 46, "Core 1\nкрутиться вхолосту", fill="#fbecec", stroke=ISRC, size=10)
    f.append(text(230, 178, "інше ядро марно палить такти", size=10, color=ISRC, italic=True))

    f.append(line(W / 2, 72, W / 2, 250, color="#dde2ea", sw=1.5, dash="2,4"))

    # праворуч: atomic
    f.append(text(680, 72, "atomic::fetch_add — lock-free", size=12, bold=True, color=SAFE))
    boxlabel(f, 530, 100, 150, 46, "Core 0\nfetch_add(1)", fill="#eef6ef", stroke=SAFE, size=10.5)
    boxlabel(f, 700, 100, 150, 46, "Core 1\nпрацює своє", fill="#eef6ef", stroke=SAFE, size=10.5)
    f.append(text(690, 178, "ніхто нікого не чекає (LL/SC)", size=10, color=SAFE, italic=True))

    # спільне слово знизу
    boxlabel(f, W / 2 - 95, 212, 190, 36, "одне вирівняне слово", fill="#fbfcff", stroke=INK, size=11)
    f.append(arrow(170, 148, W / 2 - 85, 210, color=MUTED))
    f.append(arrow(740, 148, W / 2 + 85, 210, color=MUTED))

    note(f, W / 2, 268, 760,
         ["Для +1 над одним словом спінлок бере повний замок і змушує сусіднє ядро крутитись.",
          "fetch_add робить ту саму RMW однією неподільною інструкцією. Замок — для багатопольних оновлень."])
    render(os.path.join(IMG, "spinlock-vs-atomic.svg"), W, H, *f)


# ── переставлення пам'яті: без бар'єра і з бар'єром ─────────────────────────
def fig_barrier_reorder():
    W, H = 920, 420
    f = [text(W / 2, 30, "Переставлення пам'яті: без бар'єра читач бачить head раніше за дані",
              size=15, bold=True)]

    # без бар'єра
    f.append(text(230, 70, "без бар'єра", size=13, bold=True, color=ISRC))
    boxlabel(f, 90, 95, 280, 36, "writer: data = x;  потім head++", fill="#e9eefb", stroke=MAIN, size=10.5)
    f.append(text(230, 150, "store buffer переставив видимість", size=9.5, color=MUTED, italic=True))
    boxlabel(f, 90, 165, 280, 36, "reader бачить новий head ПЕРШИМ", fill="#fbecec", stroke=ISRC, size=10)
    boxlabel(f, 120, 215, 220, 36, "читає недописаний слот", fill="#fbecec", stroke=ISRC, size=10.5, tcol=ISRC)
    f.append(arrow(230, 131, 230, 163, color=ISRC))
    f.append(arrow(230, 201, 230, 213, color=ISRC))

    f.append(line(W / 2, 70, W / 2, 290, color="#dde2ea", sw=1.5, dash="2,4"))

    # з бар'єром
    f.append(text(690, 70, "з бар'єром (release / acquire)", size=12.5, bold=True, color=SAFE))
    boxlabel(f, 550, 95, 280, 36, "writer: data = x; ▸release▸ head++", fill="#e9eefb", stroke=MAIN, size=10)
    f.append(text(690, 150, "буфер прочищено перед публікацією head", size=9, color=MUTED, italic=True))
    boxlabel(f, 550, 165, 280, 36, "reader: acquire бачить head", fill="#eef6ef", stroke=SAFE, size=10.5)
    boxlabel(f, 580, 215, 220, 36, "дані вже видимі — слот готовий", fill="#eef6ef", stroke=SAFE, size=10, tcol=SAFE)
    f.append(arrow(690, 131, 690, 163, color=SAFE))
    f.append(arrow(690, 201, 690, 213, color=SAFE))

    note(f, W / 2, 300, 800,
         ["Кожне ядро має власний store buffer; інше ядро може побачити записи в іншому порядку.",
          "Пара release/acquire змушує залізо: побачив head — дані перед ним уже видимі. volatile від цього не рятує."])
    render(os.path.join(IMG, "barrier-reorder.svg"), W, H, *f)


if __name__ == "__main__":
    # стаття
    fig_race_condition()
    fig_what_is_atomic()
    fig_critical_section()
    fig_snapshot_pattern()
    fig_keep_short()
    fig_esp32_spinlock()
    # hist-therac25
    fig_therac_race()
    fig_therac_interlock()
    # proj-critical-sections
    fig_which_tool()
    fig_cs_keep_short()
    # proj-atomics-barriers
    fig_spinlock_vs_atomic()
    fig_barrier_reorder()
    print("Готово: 12 SVG у", IMG)
