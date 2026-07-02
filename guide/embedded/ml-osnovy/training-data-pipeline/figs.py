# -*- coding: utf-8 -*-
"""Фігури до теми «Підготовка навчальних даних» (конвеєр даних під бортову модель).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Конвеєр даних: збір → розмітка → поділ → аугментація → навчання ────────
def fig_pipeline():
    """Чотири кроки підготовки даних, що ведуть до навчання: зібрати кадри,
    розмітити (де ціль), поділити на навчання/перевірку/тест, аугментувати —
    і лише тоді модель учиться. Дані тут — головна робота, не сама мережа."""
    W, H = 900, 300
    f = [text(W / 2, 30, "Конвеєр навчальних даних: що відбувається ДО навчання", size=17, bold=True)]

    steps = [("ЗІБРАТИ", "кадри з польотів\n(різні умови)", FIELD),
             ("РОЗМІТИТИ", "де на кадрі ціль\n(рамка + клас)", POS),
             ("ПОДІЛИТИ", "навчання / перевірка\n/ тест — без витоку", NEG),
             ("АУГМЕНТУВАТИ", "штучні варіації\n(яскравість, поворот…)", FIELD)]
    bx, by, bw, bh, gap = 40, 95, 175, 110, 27
    for i, (head, body, col) in enumerate(steps):
        x = bx + i * (bw + gap)
        f.append(rect(x, by, bw, bh, fill=BG, stroke=col, sw=1.8))
        f.append(text(x + bw / 2, by + 26, head, size=14, bold=True, color=col))
        f.append(mtext(x + bw / 2, by + 50, body, size=11, color=INK))
        if i < 3:
            ax = x + bw
            f.append(arrow(ax + 3, by + bh / 2, ax + gap - 3, by + bh / 2))

    # стрілка вниз до навчання
    f.append(text(W / 2, H - 50, "↓", size=22, color=MUTED))
    f.append(fitbox(W / 2 - 150, H - 44, 300, 30,
                    "тільки тепер модель НАВЧАЄТЬСЯ на цих даних",
                    size=12, bold=True, fill=FILL, stroke=LINE))
    return render(os.path.join(IMG, "pipeline.svg"), W, H, *f)


# ── 2. Поділ і витік: чому ділити по кадрах — пастка ──────────────────────────
def fig_split_leak():
    """Сусідні кадри відео майже однакові. Якщо ділити випадково по кадрах,
    майже той самий кадр потрапляє і в навчання, і в тест — оцінка завищена
    (витік). Правильно — ділити цілими польотами/сценами."""
    W, H = 820, 380
    f = [text(W / 2, 30, "Поділ даних: пастка витоку на сусідніх кадрах", size=17, bold=True)]

    # ── ліворуч: НЕПРАВИЛЬНО — поділ по кадрах ──
    f.append(text(205, 66, "✗ поділ випадково по кадрах", size=13, bold=True, color=POS))
    fr_y = 90
    # ряд майже однакових кадрів
    for i in range(6):
        x = 60 + i * 56
        col = NEG if i in (1, 4) else FIELD   # 1 і 4 — у тест, решта — навчання
        f.append(rect(x, fr_y, 46, 46, fill=BG, stroke=col, sw=2))
        f.append(text(x + 23, fr_y + 29, "▦", size=20, color=col))
        tag = "тест" if i in (1, 4) else "навч"
        f.append(text(x + 23, fr_y + 62, tag, size=10, color=col))
    f.append(text(205, fr_y + 92, "кадри 0,1,2,3,4,5 — майже однакові", size=11, color=MUTED))
    f.append(fitbox(60, fr_y + 108, 290, 56,
                    "майже той самий кадр — і в навчанні, і в тесті\n→ тест «упізнає бачене» → бал завищений",
                    size=11, bold=True, fill="#fdecea", stroke=POS))

    # роздільник
    f.append(line(W / 2, 60, W / 2, H - 30, color=LINE, sw=1, dash="5 5"))

    # ── праворуч: ПРАВИЛЬНО — поділ по польотах ──
    f.append(text(615, 66, "✓ поділ цілими польотами", size=13, bold=True, color=FIELD))
    # три блоки-польоти
    flights = [("політ A", NEG, "навчання"), ("політ B", NEG, "навчання"), ("політ C", FIELD, "тест")]
    for i, (lab, col, role) in enumerate(flights):
        x = 470 + i * 100
        f.append(rect(x, 90, 86, 60, fill=BG, stroke=col, sw=1.8))
        f.append(text(x + 43, 112, lab, size=12, bold=True, color=col))
        f.append(text(x + 43, 132, role, size=11, color=col))
    f.append(fitbox(470, 200, 286, 56,
                    "тест — політ, якого модель не бачила ЗОВСІМ\n→ бал чесний, як у реальному вильоті",
                    size=11, bold=True, fill="#eef6ef", stroke=FIELD))

    f.append(text(W / 2, H - 16,
                  "ділити треба так, щоб у тест не просочилося нічого, схожого на навчальне",
                  size=12, color=INK))
    return render(os.path.join(IMG, "split-leak.svg"), W, H, *f)


# ── 3. Розрив доменів: на чому вчили ≠ що бачить у польоті ────────────────────
def fig_domain_gap():
    """Модель упевнена лише на тому, що БАЧИЛА. Якщо навчальні кадри чисті
    (день, один ракурс, різко), а в польоті — присмерк, змаз, дивний кут,
    модель «сліпне». Лік — збирати дані в умовах майбутньої роботи."""
    W, H = 820, 360
    f = [text(W / 2, 30, "Розрив доменів: модель знає лише те, що бачила", size=17, bold=True)]

    # ліворуч: навчальні дані (вузькі умови)
    f.append(fitbox(50, 80, 310, 40, "НА ЧОМУ ВЧИЛИ", size=14, bold=True,
                    fill="#eef6ef", stroke=FIELD))
    train = ["ясний день", "один ракурс згори", "різкий кадр", "ціль у центрі"]
    for i, t in enumerate(train):
        f.append(text(60, 150 + i * 30, "• " + t, size=12, color=FIELD, anchor="start"))

    # стрілка
    f.append(arrow(375, 200, 445, 200))
    f.append(text(410, 188, "політ", size=11, color=MUTED))

    # праворуч: реальність (ширші умови)
    f.append(fitbox(460, 80, 310, 40, "ЩО БАЧИТЬ У ПОЛЬОТІ", size=14, bold=True,
                    fill="#fdecea", stroke=POS))
    real = ["присмерк, контражур", "косі кути, нахил", "змаз від руху й вібрації", "ціль скраю, частково"]
    for i, t in enumerate(real):
        f.append(text(470, 150 + i * 30, "• " + t, size=12, color=POS, anchor="start"))

    f.append(fitbox(W / 2 - 280, H - 50, 560, 34,
                    "усе, чого не було в навчанні, модель бачить уперше — і помиляється",
                    size=12, bold=True, fill=FILL, stroke=LINE))
    return render(os.path.join(IMG, "domain-gap.svg"), W, H, *f)


# ── 4. Перекіс класів: довгий хвіст ──────────────────────────────────────────
def fig_imbalance():
    """Якщо ціль трапляється рідко (95% кадрів — порожнє тло, 5% — ціль),
    модель «вигідно» завжди казати «тло»: 95% точності, нуль користі. Лік —
    балансувати: добирати рідкісні приклади, важити класи."""
    W, H = 800, 340
    f = [text(W / 2, 30, "Перекіс класів: коли ціль трапляється рідко", size=17, bold=True)]

    # стовпчики: тло величезне, ціль крихітна
    base_y = 230
    f.append(line(110, base_y, 690, base_y, color=LINE, sw=1.4))
    # тло
    f.append(rect(170, base_y - 150, 120, 150, fill="#e9edf6", stroke=NEG, sw=1.8))
    f.append(text(230, base_y - 158, "95%", size=15, bold=True, color=NEG))
    f.append(text(230, base_y + 22, "порожнє тло", size=12, color=NEG))
    # ціль
    f.append(rect(470, base_y - 12, 120, 12, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(530, base_y - 20, "5%", size=15, bold=True, color=POS))
    f.append(text(530, base_y + 22, "ціль", size=12, color=POS))

    f.append(fitbox(W / 2 - 300, H - 70, 600, 50,
                    "модель «вигідно» завжди казати «тло»: 95% точності — і нуль користі\n"
                    "лік — балансувати: добрати рідкісні приклади, важити класи",
                    size=12, bold=True, fill=FILL, stroke=LINE))
    return render(os.path.join(IMG, "imbalance.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pipeline()
    fig_split_leak()
    fig_domain_gap()
    fig_imbalance()
    print("OK: 4 фігури у", IMG)
