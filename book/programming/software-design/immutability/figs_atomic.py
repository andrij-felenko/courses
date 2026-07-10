# -*- coding: utf-8 -*-
# Фігури для вставки proj-atomic-snapshot.md
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GREEN_FILL = '#eafaf0'
RED_FILL = '#fdecea'


def cas_cycle():
    """Дві панелі: ЧИТАННЯ (без замка) і ЗАПИС (копіюй-і-CAS з повтором).
    Ліворуч — читач бере миттєвий незмінний знімок; праворуч — цикл писаря
    з петлею-повтором при збігу CAS. Панелі розділені порожнечею (без лінії)."""
    W, H = 980, 560
    f = []

    # ── ЛІВА панель: ЧИТАННЯ ──
    f.append(fitbox(40, 34, 410, 34, 'ЧИТАННЯ — без замка', size=15, bold=True,
                    fill='#eef1f4', stroke=LINE))
    la, lw, lh = textbox(255, 130, 'ЧИТАЧ', size=14, bold=True, min_w=150)
    lb, bw, bh = textbox(255, 275, ['КОМІРКА', 'посилання → vN'], size=13,
                         fill='#f0f4ff', stroke=NEG, min_w=200)
    lc, cw, ch = textbox(255, 430, ['знімок vN незмінний:', 'читай поля без замка'],
                         size=13, fill=GREEN_FILL, stroke=FIELD, min_w=220)
    f += [la, lb, lc]
    f.append(arrow(255, 130 + lh / 2, 255, 275 - bh / 2, sw=2))
    f.append(arrow(255, 275 + bh / 2, 255, 430 - ch / 2, sw=2))
    f.append(text(285, 197, 'get(): 1 атомарний load', size=12, color=MUTED, anchor='start'))
    f.append(text(285, 353, 'далі — без синхронізації', size=12, color=MUTED, anchor='start'))

    # ── ПРАВА панель: ЗАПИС ──
    f.append(fitbox(530, 34, 410, 34, 'ЗАПИС — копіюй-і-CAS, повтори при збігу',
                    size=15, bold=True, fill='#eef1f4', stroke=LINE))
    s1, w1, h1 = textbox(745, 120, '1.  prev ← load(комірка)', size=13, min_w=250)
    s2, w2, h2 = textbox(745, 245, ['2.  next ← копія(prev) + зміна',
                                    'нова НЕЗМІННА версія'], size=13, min_w=250)
    s3, w3, h3 = textbox(745, 370, '3.  CAS(prev → next)', size=13, min_w=250)
    ok, wok, hok = textbox(745, 495, 'опубліковано vN+1', size=13, bold=True,
                           fill=GREEN_FILL, stroke=FIELD, min_w=200)
    f += [s1, s2, s3, ok]
    f.append(arrow(745, 120 + h1 / 2, 745, 245 - h2 / 2, sw=2))
    f.append(arrow(745, 245 + h2 / 2, 745, 370 - h3 / 2, sw=2))
    f.append(arrow(745, 370 + h3 / 2, 745, 495 - hok / 2, color=FIELD, sw=2.2))
    f.append(text(765, 448, 'успіх ✓', size=12, color=FIELD, anchor='start', bold=True))

    # петля-повтор: S3 → ліворуч → вгору → S1 (елбоу), підпис у порожнечі ліворуч
    ex = 560
    f.append(line(745 - w3 / 2, 370, ex, 370, color=POS, sw=2))
    f.append(line(ex, 370, ex, 120, color=POS, sw=2))
    f.append(arrow(ex, 120, 745 - w1 / 2, 120, color=POS, sw=2))
    f.append(mtext(548, 238, ['збіг — хтось', 'устиг: повтор'], size=12,
                   color=POS, anchor='end', bold=True))

    render(os.path.join(OUT, 'cas-cycle.svg'), W, H, *f)


def aba_two_faces():
    """Дві панелі: значеннєва ABA (знята незмінністю) проти адресної (НЕ знята).
    Ліворуч — те саме посилання = той самий зміст, CAS має рацію.
    Праворуч — аллокатор віддає стару адресу під новий об'єкт, CAS обманюється."""
    W, H = 980, 560
    f = []

    def step(cx, cy, s, fill=FILL, stroke=LINE, w=390):
        return fitbox(cx - w / 2, cy - 26, w, 52, s, size=13, fill=fill, stroke=stroke)

    # ── ЛІВА: значеннєва ABA ──
    f.append(fitbox(40, 34, 410, 34, 'ЗНАЧЕННЄВА ABA — знята незмінністю',
                    size=14, bold=True, fill=GREEN_FILL, stroke=FIELD))
    lx = 245
    ys = [120, 210, 300]
    f.append(step(lx, ys[0], 'комірка → v1   (незмінний)', fill='#f0f4ff', stroke=NEG))
    f.append(step(lx, ys[1], 'хтось: v1 → v2 → v1  (назад ТОЙ САМИЙ v1)'))
    f.append(step(lx, ys[2], 'писар: prev = v1 → CAS(v1 → v3) успіх', fill=GREEN_FILL, stroke=FIELD))
    for a, b in ((ys[0], ys[1]), (ys[1], ys[2])):
        f.append(arrow(lx, a + 26, lx, b - 26, sw=1.8))
    f.append(fitbox(50, 372, 390, 66,
                    ['те саме посилання ⇒ той самий зміст.',
                     'незмінний об’єкт не міг збрехати —', 'CAS має рацію'],
                    size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, color=FIELD))

    # ── ПРАВА: адресна ABA ──
    f.append(fitbox(530, 34, 410, 34, 'АДРЕСНА ABA — НЕ знята незмінністю',
                    size=14, bold=True, fill=RED_FILL, stroke=POS))
    rx = 735
    yr = [115, 190, 265, 340]
    f.append(step(rx, yr[0], 'сира комірка → &A   (0xA1 = v1)', fill='#f0f4ff', stroke=NEG))
    f.append(step(rx, yr[1], 'v1 звільнено — 0xA1 вільна'))
    f.append(step(rx, yr[2], 'аллокатор віддає 0xA1 під НОВИЙ v3', fill=RED_FILL, stroke=POS))
    f.append(step(rx, yr[3], 'комірка → &A знову, та за 0xA1 вже v3', fill=RED_FILL, stroke=POS))
    for a, b in ((yr[0], yr[1]), (yr[1], yr[2]), (yr[2], yr[3])):
        f.append(arrow(rx, a + 26, rx, b - 26, sw=1.8))
    f.append(fitbox(540, 408, 390, 66,
                    ['CAS(&A → …) збігся за АДРЕСОЮ, об’єкт інший →',
                     'тихе псування. незмінність', 'не керує аллокатором'],
                    size=13, bold=True, fill=RED_FILL, stroke=POS, color=POS))

    render(os.path.join(OUT, 'aba-two-faces.svg'), W, H, *f)


def rcu_grace_period():
    """Часова вісь RCU: писар публікує нову версію, стару звільняють лише коли
    її вже не тримає жоден ДОЧАСНИЙ читач. Новий читач бачить нову версію й до
    старої стосунку не має. Період відкладення = grace period."""
    W, H = 980, 520
    f = []
    f.append(text(W / 2, 34, 'RCU: відкладене вивільнення старої версії', size=16, bold=True))

    axis_y = 430
    x_pub = 430
    x_free = 660

    # смуги життя читачів (rect, не line)
    def reader(x1, x2, y, label, fill='#f0f4ff', stroke=NEG):
        f.append(rect(x1, y - 11, x2 - x1, 22, fill=fill, stroke=stroke, sw=1.6, rx=8))
        f.append(text(x1 - 12, y + 5, label, size=12, anchor='end', color=INK))

    reader(150, 520, 150, 'r1', )
    reader(195, 630, 200, 'r2', )
    # r3 стартує ПІСЛЯ публікації — підпис над смугою, щоб пунктир не різав напис
    f.append(rect(475, 239, 305, 22, fill=GREEN_FILL, stroke=FIELD, sw=1.6, rx=8))
    f.append(text(627, 234, 'r3 — новий читач', size=12, color=FIELD, bold=True))

    # вертикаль публікації (пунктир) — від осі вгору, не крізь написи
    f.append(line(x_pub, 130, x_pub, axis_y, color=POS, sw=1.8, dash='6,5'))
    f.append(text(x_pub + 12, 120, 'публікація vN+1', size=12, color=POS, anchor='start', bold=True))

    # позначка вивільнення
    f.append(line(x_free, 300, x_free, axis_y, color=FIELD, sw=1.8, dash='6,5'))
    f.append(text(x_free + 12, 300, 'звільнити стару vN — безпечно', size=12,
                  color=FIELD, anchor='start', bold=True))

    # смуга grace period
    f.append(rect(x_pub, 330, x_free - x_pub, 26, fill=GREEN_FILL, stroke=FIELD, sw=1.4, rx=6))
    f.append(text((x_pub + x_free) / 2, 347, 'період відкладення (grace period)',
                  size=12, color=FIELD, bold=True))

    # вісь часу
    f.append(arrow(120, axis_y, 900, axis_y, sw=1.8))
    f.append(text(895, axis_y + 22, 'час', size=12, color=MUTED, anchor='end'))

    f.append(mtext(W / 2, 474,
                   ['стару версію звільняють лише коли її вже не тримає жоден ДОЧАСНИЙ читач;',
                    'новий читач r3 бачить одразу нову версію. GC чи лічильник роблять це відкладення за нас.'],
                   size=12, color=MUTED))

    render(os.path.join(OUT, 'rcu-grace-period.svg'), W, H, *f)


def cost_table():
    """Вартість читання проти запису в патерні єдиної мінливої комірки."""
    W, H = 940, 520
    f = []
    f.append(text(W / 2, 36, 'Вартість: читач проти писаря', size=17, bold=True))

    x0 = 30
    cols = [300, 300, 280]           # аспект · читач · писар
    cx = [x0, x0 + cols[0], x0 + cols[0] + cols[1]]
    header_y = 74
    row_h = 66

    # шапка
    hd = ['аспект', 'ЧИТАЧ', 'ПИСАР']
    hfill = ['#eef1f4', '#f0f4ff', RED_FILL]
    for i, h in enumerate(hd):
        f.append(fitbox(cx[i], header_y, cols[i], 44, h, size=14, bold=True,
                        fill=hfill[i], stroke=LINE))

    rows = [
        ('синхронізація', 'без замка: 1 атомарний load', '1 CAS (+ повтори при збігу)'),
        ('час', 'O(1), wait-free', 'O(n) копія + CAS'),
        ('пам’ять', '0 — лише читання', 'O(n) новий знімок; старий → сміття'),
        ('масштабування', 'лінійно з ядрами', 'писарі серіалізуються'),
        ('кого блокує', 'нікого', 'не блокує читачів; писарі конкурують'),
    ]
    y = header_y + 44 + 6
    for r, (a, rd, wr) in enumerate(rows):
        yy = y + r * row_h
        f.append(fitbox(cx[0], yy, cols[0], row_h - 6, a, size=13, bold=True,
                        fill='#f7f9fb', stroke=MUTED))
        f.append(fitbox(cx[1], yy, cols[1], row_h - 6, rd, size=13,
                        fill=GREEN_FILL, stroke=FIELD))
        f.append(fitbox(cx[2], yy, cols[2], row_h - 6, wr, size=13,
                        fill=FILL, stroke=MUTED))

    f.append(mtext(W / 2, y + len(rows) * row_h + 22,
                   ['патерн сяє при «багато читань, зрідка запис» — профіль RCU.',
                    'велику «копію» здешевлює структурний поділ до O(log n).'],
                   size=12, color=MUTED))

    render(os.path.join(OUT, 'cost-read-vs-write.svg'), W, H, *f)


if __name__ == '__main__':
    cas_cycle()
    aba_two_faces()
    rcu_grace_period()
    cost_table()
    print('done')
