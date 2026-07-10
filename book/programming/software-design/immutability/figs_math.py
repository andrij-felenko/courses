# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER = '#fbe6c9'
GREENBG = '#eafaf0'
BLUEBG = '#eaf0fd'
REDBG = '#fdecea'


def bucket_loss():
    """Мутація ключа в геш-таблиці: об'єкт лежить у кошику СТАРОГО геша (3),
    а пошук тим самим об'єктом обчислює НОВИЙ геш (7) і йде в порожній кошик —
    запис губиться у власному кошику. Ліворуч — три кроки; праворуч — масив кошиків."""
    W, H = 880, 600
    f = []
    f.append(text(W / 2, 32, 'Мутація ключа: запис губиться у власному кошику', size=17, bold=True))

    # ── масив кошиків праворуч ──
    f.append(text(680, 74, 'кошики геш-таблиці', size=12, color=MUTED))
    bx, bw, bh, top0, rowh = 560, 240, 36, 88, 44
    for i in range(8):
        top = top0 + i * rowh
        cy = top + bh / 2
        if i == 3:
            f.append(fitbox(bx, top, bw, bh,
                            'тепер {«beer»} → геш 7\nа лежить у кошику 3',
                            size=11, fill=AMBER, stroke=POS, sw=2.2, color=POS, bold=True))
        else:
            f.append(rect(bx, top, bw, bh, fill=FILL, stroke=LINE, sw=1.4))
            label = 'порожньо' if i == 7 else '—'
            f.append(text(bx + bw / 2, cy + 4, label, size=12, color=MUTED))
        f.append(text(bx + bw + 20, cy + 4, str(i), size=12, color=MUTED))

    # ── три кроки ліворуч ──
    f.append(fitbox(30, 100, 300, 70,
                    '1. Вставили ключ зі вмістом «cola»\nгеш(«cola») = 3 → кошик 3',
                    size=12, fill=FILL, stroke=LINE))
    f.append(fitbox(30, 244, 300, 70,
                    '2. Змінили поле на місці «cola»→«beer»\nтепер геш(«beer») = 7',
                    size=12, fill=FILL, stroke=LINE))
    f.append(fitbox(30, 388, 300, 70,
                    "3. Шукаємо ТИМ САМИМ об'єктом-ключем\nобчислюємо геш = 7 → кошик 7",
                    size=12, fill=FILL, stroke=LINE))

    # ── короткі стрілки в кошики + підписи над ними ──
    y_b3, y_b7 = top0 + 3 * rowh + bh / 2, top0 + 7 * rowh + bh / 2
    f.append(arrow(470, y_b3, 556, y_b3, color=FIELD, sw=2.2))
    f.append(text(500, y_b3 - 24, "об'єкт лежить тут", size=12, color=FIELD, bold=True))
    f.append(arrow(470, y_b7, 556, y_b7, color=NEG, sw=2.2))
    f.append(text(500, y_b7 - 24, 'пошук веде сюди', size=12, color=NEG, bold=True))

    # ── висновок ──
    f.append(text(W / 2, 548,
                  'Ключ шукають у кошику ПОТОЧНОГО геша (7), а він лежить у кошику старого (3).',
                  size=13, bold=True))
    f.append(text(W / 2, 574,
                  'Запис видно перебором, але ключем не знайти — він загубився у власному кошику.',
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'bucket-loss.svg'), W, H, *f)


def laws_and_time():
    """Угорі: три закони еквівалентності тримаються в заморожений момент —
    рівність розбиває множину на класи. Унизу: зміна на місці переносить той самий
    об'єкт між класами в різні моменти — у часі це вже не одне відношення."""
    W, H = 900, 620
    f = []
    f.append(text(W / 2, 30,
                  'Рівність за вмістом як відношення еквівалентності — і як час її ламає',
                  size=16, bold=True))
    f.append(line(40, 332, 860, 332, color=MUTED, sw=1, dash='5,5'))

    # ── ВЕРХНЯ панель ──
    f.append(text(W / 2, 64, 'Заморожений момент: три закони тримаються', size=14, bold=True))
    f.append(fitbox(40, 88, 260, 78,
                    'РЕФЛЕКСИВНІСТЬ\na = a\nкожне дорівнює собі', size=14, fill=GREENBG, stroke=FIELD))
    f.append(fitbox(320, 88, 260, 78,
                    'СИМЕТРІЯ\na = b ⇒ b = a\nпорядок не важить', size=14, fill=GREENBG, stroke=FIELD))
    f.append(fitbox(600, 88, 260, 78,
                    'ТРАНЗИТИВНІСТЬ\na = b, b = c ⇒ a = c', size=14, fill=GREENBG, stroke=FIELD))

    f.append(text(W / 2, 208,
                  'разом ⇒ рівність чисто розбиває множину на класи (усе в класі взаємозамінне):',
                  size=13))
    f.append(rect(300, 232, 300, 66, fill=FILL, stroke=LINE, sw=1.4))
    for cx, lab, col in [(360, '100₴', FIELD), (450, '50₴', NEG), (540, '3€', POS)]:
        f.append(circle(cx, 265, 24, fill=BG, stroke=col, sw=2.0))
        f.append(text(cx, 270, lab, size=11, color=col, bold=True))
    f.append(text(W / 2, 318, 'класи не перетинаються й покривають усе', size=12, color=MUTED))

    # ── НИЖНЯ панель ──
    f.append(text(W / 2, 362,
                  "Зміна на місці: той самий об'єкт у різних класах у різні моменти",
                  size=14, bold=True))
    f.append(fitbox(70, 400, 300, 120,
                    "МОМЕНТ t₁\nоб'єкт a у класі {«cola»}\nрівний усім іншим «cola»",
                    size=13, fill=GREENBG, stroke=FIELD))
    f.append(fitbox(530, 400, 300, 120,
                    'МОМЕНТ t₂ (після мутації)\nтой самий a у класі {«beer»}\nуже НЕ рівний «cola»',
                    size=13, fill=REDBG, stroke=POS))
    f.append(arrow(370, 460, 530, 460, color=POS, sw=2.4))
    f.append(text(450, 440, 'мутація на місці', size=12, color=POS, bold=True))

    f.append(text(W / 2, 556,
                  'Клас об’єкта a у t₁ і у t₂ — різні; рівність за змінним вмістом у часі не одне',
                  size=12))
    f.append(text(W / 2, 580,
                  'відношення, а щомиті інше. Кожен закон читається у ДВА моменти — і ламається.',
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'laws-and-time.svg'), W, H, *f)


if __name__ == '__main__':
    bucket_loss()
    laws_and_time()
    print('done')
