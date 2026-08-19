# -*- coding: utf-8 -*-
"""Фігури для статті «Timsort» та її вставок.
Генерує чотири SVG у ./img:
1. run-decomposition.svg — виділення природних серій (неспадні, строго спадні з розвертанням, подовження до minrun)
2. merge-stack-invariants.svg — стек серій та інваріанти злиття
3. galloping-mode.svg — механіка режиму галопу (експоненційні стрибки + двійковий пошук)
4. merge-lo-hi.svg — оптимізація буфера пам'яті через merge_lo та merge_hi
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
BG_ASC    = "#eef6fc"   # Неспадна серія (світло-блакитний)
BORDER_ASC = "#2980b9"
BG_DESC   = "#fdecea"   # Спадна серія (світло-червоний)
BORDER_DESC = "#c0392b"
BG_EXT    = "#eafaf1"   # Подовження вставками (світло-зелений)
BORDER_EXT = "#27ae60"
BG_WARN   = "#fef9e7"   # Порушення інваріанта (світло-жовтий)
BORDER_WARN = "#d4ac0d"
BG_BUF    = "#f4f6f8"   # Тимчасовий буфер (сірий)
BORDER_BUF = "#7f8c8d"

def cell(x, y, w, h, val, fill=FILL, stroke=LINE, sw=1.5, tc=INK, bold=True, sub=""):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4)
    if sub:
        out += text(x + w / 2, y + h / 2 - 2, val, size=14, color=tc, bold=bold)
        out += text(x + w / 2, y + h - 5, sub, size=10, color=MUTED)
    else:
        out += text(x + w / 2, y + h / 2 + 5, val, size=14, color=tc, bold=bold)
    return out

# ── Фігура 1: Виділення та подовження серій ──────────────────────────────────
def fig_runs():
    W, H = 820, 360
    cw, ch = 44, 38
    f = []

    # Заголовок блоку 1: Природна неспадна серія
    f.append(text(40, 30, "1. Природна неспадна серія (залишається як є)", size=13, color=BORDER_ASC, anchor="start", bold=True))
    vals1 = [12, 25, 33, 48, 55]
    x1 = 40
    for i, v in enumerate(vals1):
        f.append(cell(x1 + i * cw, 42, cw, ch, str(v), fill=BG_ASC, stroke=BORDER_ASC))
    f.append(text(x1 + len(vals1) * cw + 20, 65, "len = 5 ≥ minrun  →  серія готова", size=12, color=INK, anchor="start"))

    # Заголовок блоку 2: Строго спадна серія -> розвертання
    f.append(text(40, 115, "2. Строго спадна серія (інвертується на місці двома вказівниками)", size=13, color=BORDER_DESC, anchor="start", bold=True))
    vals2 = [89, 64, 41, 18]
    x2 = 40
    for i, v in enumerate(vals2):
        f.append(cell(x2 + i * cw, 127, cw, ch, str(v), fill=BG_DESC, stroke=BORDER_DESC))
    
    f.append(arrow(x2 + len(vals2) * cw + 15, 146, x2 + len(vals2) * cw + 55, 146, color=BORDER_DESC, sw=2))
    f.append(text(x2 + len(vals2) * cw + 35, 138, "reverse", size=10, color=BORDER_DESC, bold=True))

    vals2_rev = [18, 41, 64, 89]
    x2_rev = x2 + len(vals2) * cw + 70
    for i, v in enumerate(vals2_rev):
        f.append(cell(x2_rev + i * cw, 127, cw, ch, str(v), fill=BG_ASC, stroke=BORDER_ASC))
    f.append(text(x2_rev + len(vals2_rev) * cw + 20, 150, "стабільність збережено", size=12, color=INK, anchor="start"))

    # Заголовок блоку 3: Коротка серія + подовження до minrun
    f.append(text(40, 205, "3. Коротка серія (подовження через Binary Insertion Sort до minrun = 6)", size=13, color=BORDER_EXT, anchor="start", bold=True))
    
    # Вихідний стан
    f.append(text(40, 230, "Вихідний масив:", size=12, color=MUTED, anchor="start"))
    x3 = 40
    vals3_init = [10, 20, 15, 5, 42, 8]
    for i, v in enumerate(vals3_init):
        if i < 2:
            f.append(cell(x3 + i * cw, 240, cw, ch, str(v), fill=BG_ASC, stroke=BORDER_ASC))
        else:
            f.append(cell(x3 + i * cw, 240, cw, ch, str(v), fill=FILL, stroke=LINE))
    
    f.append(text(x3 + cw, 292, "природна серія (len=2)", size=10, color=BORDER_ASC, bold=True))
    f.append(text(x3 + 4 * cw, 292, "наступні елементи масиву для поглинання", size=10, color=MUTED))

    # Стрілка вниз
    f.append(arrow(170, 298, 170, 318, color=BORDER_EXT, sw=2))

    # Після подовження
    f.append(text(370, 230, "Після бінарних вставок:", size=12, color=BORDER_EXT, anchor="start", bold=True))
    x3_res = 370
    vals3_res = [5, 8, 10, 15, 20, 42]
    for i, v in enumerate(vals3_res):
        f.append(cell(x3_res + i * cw, 240, cw, ch, str(v), fill=BG_EXT, stroke=BORDER_EXT))
    f.append(text(x3_res + len(vals3_res) * cw + 15, 263, "len = 6 = minrun", size=12, color=BORDER_EXT, anchor="start", bold=True))

    render(os.path.join(IMG, "run-decomposition.svg"), W, H, *f)

# ── Фігура 2: Стек серій та інваріанти ───────────────────────────────────────
def fig_stack():
    W, H = 840, 340
    f = []

    # Ліва частина: Стек серій
    f.append(text(150, 35, "Стек активних серій", size=14, bold=True))
    
    sx, sy = 50, 60
    sw_box = 200
    sh_box = 45

    # Run C (bottom of top-3)
    f.append(rect(sx, sy, sw_box, sh_box, fill=BG_ASC, stroke=BORDER_ASC, sw=1.5))
    f.append(text(sx + sw_box / 2, sy + 20, "Серія C (stack[top-2])", size=12, color=BORDER_ASC, bold=True))
    f.append(text(sx + sw_box / 2, sy + 36, "довжина = len(C) = 120", size=11, color=INK))

    # Run B (mid)
    f.append(rect(sx, sy + 55, sw_box, sh_box, fill=BG_WARN, stroke=BORDER_WARN, sw=1.8))
    f.append(text(sx + sw_box / 2, sy + 75, "Серія B (stack[top-1])", size=12, color=BORDER_WARN, bold=True))
    f.append(text(sx + sw_box / 2, sy + 91, "довжина = len(B) = 80", size=11, color=INK))

    # Run A (top)
    f.append(rect(sx, sy + 110, sw_box, sh_box, fill=BG_DESC, stroke=BORDER_DESC, sw=1.5))
    f.append(text(sx + sw_box / 2, sy + 130, "Серія A (stack[top])", size=12, color=BORDER_DESC, bold=True))
    f.append(text(sx + sw_box / 2, sy + 146, "довжина = len(A) = 50", size=11, color=INK))

    # Права частина: Перевірка інваріантів
    f.append(text(540, 35, "Інваріанти збалансованого злиття", size=14, bold=True))

    ix, iy = 310, 65
    f.append(rect(ix, iy, 480, 70, fill="#ffffff", stroke=BORDER_ASC, sw=1.5, rx=5))
    f.append(text(ix + 15, iy + 25, "1. len(C) > len(B) + len(A)", size=13, color=BORDER_ASC, anchor="start", bold=True))
    f.append(text(ix + 15, iy + 48, "Поточний стан: 120 ≤ (80 + 50 = 130)  →  ПОРУШЕНО!", size=12, color=POS, anchor="start", bold=True))

    f.append(rect(ix, iy + 85, 480, 70, fill="#ffffff", stroke=BORDER_ASC, sw=1.5, rx=5))
    f.append(text(ix + 15, iy + 110, "2. len(B) > len(A)", size=13, color=BORDER_ASC, anchor="start", bold=True))
    f.append(text(ix + 15, iy + 133, "Поточний стан: 80 > 50  →  ВИКОНАНО", size=12, color=FIELD, anchor="start", bold=True))

    # Злиття для відновлення інваріанта
    f.append(rect(ix, iy + 170, 480, 65, fill=BG_EXT, stroke=BORDER_EXT, sw=1.5, rx=5))
    f.append(text(ix + 15, iy + 193, "Дія алгоритму: злити B з меншою із (A, C)", size=13, color=BORDER_EXT, anchor="start", bold=True))
    f.append(text(ix + 15, iy + 216, "Оскільки len(A) < len(C) (50 < 120), зливаємо B та A у нову серію довжиною 130.", size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, "merge-stack-invariants.svg"), W, H, *f)

# ── Фігура 3: Режим галопу (Galloping mode) ──────────────────────────────────
def fig_gallop():
    W, H = 860, 430
    cw, ch = 52, 40
    f = []

    f.append(text(40, 25, "Пошук позиції ключа x = 45 у серії B за допомогою галопу", size=14, color=INK, anchor="start", bold=True))
    f.append(text(40, 50, "Елементи серії B (впорядкований масив із 12 елементів):", size=12, color=MUTED, anchor="start"))

    # Масив елементів серії B
    vals_b = [10, 14, 19, 23, 28, 35, 41, 52, 60, 73, 85, 94]
    xb, yb = 50, 85
    for i, v in enumerate(vals_b):
        f.append(cell(xb + i * cw, yb, cw, ch, str(v), fill=BG_ASC, stroke=BORDER_ASC, sub=f"[{i}]"))

    # Виділення знайденого діапазону
    f.append(rect(xb + 3 * cw - 2, yb - 2, 5 * cw + 4, ch + 4, fill="none", stroke=POS, sw=2.2, rx=4))
    f.append(text(xb + 5 * cw + 26, yb - 12, "Локалізований інтервал [B[3] .. B[7]]", size=11, color=POS, bold=True))

    # Фаза 1: Картки стрибків
    f.append(text(40, 155, "Фаза 1: Експоненційні стрибки зі зсувом 2^k - 1", size=13, color=BORDER_DESC, anchor="start", bold=True))

    jumps = [
        ("k=0 (зсув 0)", "B[0] = 10", "10 < 45", "продовжуємо"),
        ("k=1 (зсув 1)", "B[1] = 14", "14 < 45", "продовжуємо"),
        ("k=2 (зсув 3)", "B[3] = 23", "23 < 45", "продовжуємо"),
        ("k=3 (зсув 7)", "B[7] = 52", "52 > 45", "СТОП! Межу знайдено"),
    ]

    card_w = 175
    card_h = 100
    card_y = 170
    for idx, (title_j, val_j, cmp_j, act_j) in enumerate(jumps):
        cx = 45 + idx * (card_w + 20)
        is_last = (idx == 3)
        b_color = POS if is_last else BORDER_DESC
        bg_color = "#fdecea" if is_last else BG_BUF
        
        f.append(rect(cx, card_y, card_w, card_h, fill=bg_color, stroke=b_color, sw=1.5, rx=5))
        f.append(text(cx + card_w / 2, card_y + 25, title_j, size=11, color=b_color, bold=True))
        f.append(text(cx + card_w / 2, card_y + 48, val_j, size=13, color=INK, bold=True))
        f.append(text(cx + card_w / 2, card_y + 70, cmp_j, size=11, color=MUTED))
        f.append(text(cx + card_w / 2, card_y + 90, act_j, size=10, color=b_color, bold=True))

    # Фаза 2: Підсумок двійкового пошуку
    f.append(rect(40, 290, 780, 115, fill=BG_EXT, stroke=BORDER_EXT, sw=1.5, rx=6))
    f.append(text(55, 318, "Фаза 2: Двійковий пошук у локалізованому діапазоні [індекс 3 .. індекс 7]", size=13, color=BORDER_EXT, anchor="start", bold=True))
    f.append(text(55, 342, "Замість лінійного сканування всіх елементів двійковий пошук виконує лише ⌈log₂(5)⌉ = 3 порівняння.", size=11, color=INK, anchor="start"))
    f.append(text(55, 365, "Точний індекс знайдено: B[6] = 41 < 45 < B[7] = 52. Всі 7 елементів B[0..6] копіюються за 1 виклик memmove.", size=11, color=INK, anchor="start"))
    f.append(text(55, 388, "Економія: 4 порівняння на стрибках + 3 порівняння у бінарному пошуку = 7 порівнянь замість лінійного перебору.", size=11, color=BORDER_EXT, anchor="start", bold=True))

    render(os.path.join(IMG, "galloping-mode.svg"), W, H, *f)

# ── Фігура 4: Оптимізація буфера пам'яті (merge_lo та merge_hi) ──────────────
def fig_merge():
    W, H = 840, 350
    cw, ch = 42, 36
    f = []

    # Верхній блок: merge_lo
    f.append(text(40, 30, "Варіант 1: merge_lo (довжина лівої серії A ≤ довжини правої серії B)", size=13, color=BORDER_ASC, anchor="start", bold=True))
    
    # Вихідні серії A та B в основному масиві
    f.append(text(40, 58, "Основний масив:", size=11, color=MUTED, anchor="start"))
    vals_a = [3, 9, 15]
    vals_b = [4, 8, 12, 20, 25]
    x_m = 160
    for i, v in enumerate(vals_a):
        f.append(cell(x_m + i * cw, 42, cw, ch, str(v), fill=BG_ASC, stroke=BORDER_ASC, sub="A"))
    for i, v in enumerate(vals_b):
        f.append(cell(x_m + (len(vals_a) + i) * cw, 42, cw, ch, str(v), fill=BG_DESC, stroke=BORDER_DESC, sub="B"))

    # Тимчасовий буфер для серії A
    f.append(text(540, 58, "Тимчасовий буфер (лише len(A) = 3):", size=11, color=BORDER_ASC, anchor="start", bold=True))
    x_buf = 540
    for i, v in enumerate(vals_a):
        f.append(cell(x_buf + i * cw, 70, cw, ch, str(v), fill=BG_BUF, stroke=BORDER_BUF, sub="temp"))

    # Стрілка злиття
    f.append(text(40, 115, "Злиття зліва направо прямо в пам'ять масиву A..B:", size=11, color=INK, anchor="start"))
    f.append(arrow(x_buf + 60, 115, x_m + 60, 90, color=BORDER_ASC, sw=1.5))

    # Нижній блок: merge_hi
    f.append(text(40, 185, "Варіант 2: merge_hi (довжина правої серії B < довжини лівої серії A)", size=13, color=BORDER_DESC, anchor="start", bold=True))
    
    f.append(text(40, 213, "Основний масив:", size=11, color=MUTED, anchor="start"))
    vals_a2 = [2, 7, 14, 22, 30]
    vals_b2 = [5, 18, 28]
    for i, v in enumerate(vals_a2):
        f.append(cell(x_m + i * cw, 197, cw, ch, str(v), fill=BG_ASC, stroke=BORDER_ASC, sub="A"))
    for i, v in enumerate(vals_b2):
        f.append(cell(x_m + (len(vals_a2) + i) * cw, 197, cw, ch, str(v), fill=BG_DESC, stroke=BORDER_DESC, sub="B"))

    # Тимчасовий буфер для серії B
    f.append(text(540, 213, "Тимчасовий буфер (лише len(B) = 3):", size=11, color=BORDER_DESC, anchor="start", bold=True))
    for i, v in enumerate(vals_b2):
        f.append(cell(x_buf + i * cw, 225, cw, ch, str(v), fill=BG_BUF, stroke=BORDER_BUF, sub="temp"))

    # Стрілка злиття
    f.append(text(40, 270, "Злиття справа наліво прямо в пам'ять масиву A..B:", size=11, color=INK, anchor="start"))
    f.append(arrow(x_buf + 60, 270, x_m + 6 * cw, 245, color=BORDER_DESC, sw=1.5))

    # Нижній висновок
    f.append(rect(40, 295, 760, 42, fill=BG_EXT, stroke=BORDER_EXT, sw=1.2, rx=4))
    f.append(text(55, 320, "Висновок: обсяг виділеної пам'яті обмежений min(len(A), len(B)) ≤ N / 2 замість повного виділення N.", size=12, color=BORDER_EXT, anchor="start", bold=True))

    render(os.path.join(IMG, "merge-lo-hi.svg"), W, H, *f)

if __name__ == '__main__':
    fig_runs()
    fig_stack()
    fig_gallop()
    fig_merge()
    print("Всі фігури згенеровано успішно.")
