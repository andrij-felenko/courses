import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def reader_cost():
    """Ціна читання: замок жене рядок кеша між ядрами, RCU не чіпає спільного."""
    W, H = 820, 400
    p = []

    p.append(text(W / 2, 28, 'Що коштує ОДНЕ читання', size=17, bold=True))

    # ─── ліва панель: замок ───
    p.append(rect(30, 55, 360, 300, fill=BG, stroke=LINE, sw=1.2))
    p.append(text(210, 80, 'Читач із замком', size=14, bold=True, color=NEG))

    for i, x in enumerate((85, 210, 335)):
        p.append(rect(x - 42, 105, 84, 44))
        p.append(text(x, 132, 'ядро %d' % (i + 1), size=12))
        p.append(arrow(x, 149, x, 196, color=NEG, sw=2))

    p.append(rect(120, 200, 180, 52, fill=FIELD, stroke=NEG, sw=2))
    p.append(text(210, 222, 'спільний лічильник', size=12, bold=True))
    p.append(text(210, 240, 'рядок кеша', size=11, color=MUTED))

    p.append(text(210, 285, 'кожне читання ПИШЕ сюди', size=12, color=NEG))
    p.append(text(210, 305, 'рядок переїжджає між ядрами', size=12, color=NEG))
    p.append(text(210, 330, 'ціна росте з числом ядер', size=12, bold=True, color=NEG))

    # ─── права панель: RCU ───
    p.append(rect(430, 55, 360, 300, fill=BG, stroke=LINE, sw=1.2))
    p.append(text(610, 80, 'Читач RCU', size=14, bold=True, color=POS))

    for i, x in enumerate((485, 610, 735)):
        p.append(rect(x - 42, 105, 84, 44))
        p.append(text(x, 132, 'ядро %d' % (i + 1), size=12))
        p.append(rect(x - 42, 168, 84, 34, fill=FIELD, stroke=POS, sw=1.5))
        p.append(text(x, 190, 'свій лічильник', size=10))

    p.append(text(610, 240, 'нічого спільного не пишеться', size=12, color=POS))
    p.append(text(610, 262, 'рядок кеша лишається на місці', size=12, color=POS))
    p.append(text(610, 300, 'ціна читання НЕ залежить', size=12, bold=True, color=POS))
    p.append(text(610, 320, 'від числа ядер', size=12, bold=True, color=POS))

    p.append(text(W / 2, 380, 'Різниця не в швидкості коду, а в тому, чи торкається читач спільної памʼяті',
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'reader-cost.svg'), W, H, *p,
           title='Ціна читання: замок проти RCU')


def rcu_update():
    """Три фази оновлення: усунення, період відстрочки, звільнення."""
    W, H = 860, 380
    p = []

    p.append(text(W / 2, 28, 'Оновлення в три фази', size=17, bold=True))

    cx = (150, 430, 710)
    names = ('1. Усунення', '2. Період відстрочки', '3. Звільнення')
    desc = (
        ['новий покажчик стає', 'видимим для нових читачів;', 'старий вузол більше', 'ніхто не знайде'],
        ['чекаємо, доки завершаться', 'УСІ читачі, що встигли', 'узяти старий покажчик', 'до усунення'],
        ['жоден читач більше не', 'тримає старий вузол —', 'памʼять можна', 'віддати'],
    )
    colors = (INK, LINE, POS)

    for i in range(3):
        p.append(rect(cx[i] - 120, 60, 240, 200, fill=BG, stroke=colors[i], sw=2))
        p.append(text(cx[i], 88, names[i], size=14, bold=True, color=colors[i]))
        p.append(mtext(cx[i], 122, desc[i], size=12, lh=1.5))
        if i < 2:
            p.append(arrow(cx[i] + 122, 160, cx[i + 1] - 122, 160, sw=2))

    p.append(text(290, 145, 'rcu_assign_pointer()', size=11, color=MUTED))
    p.append(text(570, 145, 'synchronize_rcu()', size=11, color=MUTED))

    p.append(rect(150, 290, 560, 46, fill=FIELD, stroke=LINE, sw=1.2))
    p.append(text(430, 310, 'Старий вузол живий увесь другий крок — саме тому читачеві',
                  size=12))
    p.append(text(430, 328, 'не потрібен ані замок, ані перевірка', size=12, bold=True))

    render(os.path.join(IMG, 'rcu-update.svg'), W, H, *p,
           title='Три фази оновлення RCU')


def grace_period():
    """Часова діаграма: ділянки читання, спокійні стани, межі періоду відстрочки."""
    W, H = 880, 400
    p = []

    p.append(text(W / 2, 28, 'Період відстрочки: коли старе можна звільнити', size=17, bold=True))

    x0, x1 = 140, 800
    rows = (150, 200, 250)

    # межі періоду — підписи ВИЩЕ за смуги, лінії доходять лише до низу останнього рядка
    gs, ge = 260, 680
    p.append(line(gs, 128, gs, 273, color=INK, sw=2, dash='6,4'))
    p.append(line(ge, 128, ge, 273, color=POS, sw=2, dash='6,4'))
    p.append(text(gs, 118, 'усунення', size=12, bold=True))
    p.append(text(ge, 118, 'звільнення', size=12, bold=True, color=POS))
    p.append(text((gs + ge) / 2, 96, 'період відстрочки', size=13, bold=True))
    p.append(arrow(gs + 6, 76, ge - 6, 76, sw=1.5))

    # три ядра. Смуги без написів усередині — інакше межі періоду їх перетинають
    reads = (
        [(170, 340), (400, 520), (600, 730)],
        [(150, 300), (430, 640)],
        [(200, 470), (540, 620), (700, 780)],
    )
    for i, y in enumerate(rows):
        p.append(text(56, y + 4, 'ядро %d' % (i + 1), size=12, anchor='start'))
        p.append(line(x0, y, x1, y, color=MUTED, sw=1))
        for a, b in reads[i]:
            p.append(rect(a, y - 9, b - a, 18, fill=BG, stroke=INK, sw=1.5, rx=4))
            p.append(circle(b + 9, y, 4, fill=POS, stroke=POS))

    # легенда — під діаграмою, поза лініями
    p.append(rect(150, 300, 24, 14, fill=BG, stroke=INK, sw=1.5, rx=3))
    p.append(text(186, 311, 'ділянка читання', size=11, anchor='start'))
    p.append(circle(360, 307, 4, fill=POS, stroke=POS))
    p.append(text(374, 311, 'спокійний стан: ядро вийшло з ділянки', size=11, anchor='start'))

    p.append(text(W / 2, 348, 'Період завершується, коли КОЖНЕ ядро побувало в спокійному стані хоч раз', size=12))
    p.append(text(W / 2, 370, 'після усунення — аж тоді старий вузол нікому не видимий', size=12, color=MUTED))

    render(os.path.join(IMG, 'grace-period.svg'), W, H, *p,
           title='Період відстрочки й спокійні стани')


if __name__ == '__main__':
    reader_cost()
    rcu_update()
    grace_period()
    print('ok: 3 figures')
