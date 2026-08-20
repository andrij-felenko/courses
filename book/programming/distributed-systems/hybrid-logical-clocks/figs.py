# -*- coding: utf-8 -*-
"""Фігури до теми «Гібридні логічні годинники (HLC)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"    # попередження / похибка / гаряче
COOL = "#eaf0fd"    # заголовки / фізичний час
GOOD = "#e8f6ee"    # логічний лічильник / узгодженість
WARN_BG = "#fff9db" # проміжні стани / тайм-аути
ACCENT = "#9b51e0"  # ідентифікатор вузла / координація


# ── 1. Структура мітки часу HLC ──────────────────────────────────────────────
def hlc_structure():
    W, H = 960, 520
    f = []

    f.append(text(W / 2, 30, "Анатомія та бінарна структура мітки часу HLC", size=16, bold=True))

    # Верхній блок: Концептуальна пара (l, c, node_id)
    f.append(rect(40, 60, W - 80, 180, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, 85, "Складові компоненти гібридної мітки HLC = (l, c, node)", size=13, bold=True))

    # 3 секції вгорі
    box_w = (W - 140) / 3
    # 1. Фізична компонента l
    bx1 = 60
    f.append(rect(bx1, 105, box_w, 115, fill=COOL, stroke=NEG, sw=1.5, rx=6))
    f.append(text(bx1 + box_w / 2, 128, "l : Фізичний час (Physical)", size=12.5, bold=True, color=NEG))
    f.append(text(bx1 + box_w / 2, 150, "Найбільший відомий фізичний час", size=10.5))
    f.append(text(bx1 + box_w / 2, 168, "l = max(l_prev, msg.l, pt_local)", size=10, bold=True))
    f.append(text(bx1 + box_w / 2, 188, "Гарантує |l - pt| <= ε (обмежений дрейф)", size=9.5, color=MUTED))

    # 2. Логічна компонента c
    bx2 = bx1 + box_w + 10
    f.append(rect(bx2, 105, box_w, 115, fill=GOOD, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(bx2 + box_w / 2, 128, "c : Логічний лічильник (Logical)", size=12.5, bold=True, color=FIELD))
    f.append(text(bx2 + box_w / 2, 150, "Впорядкування в межах одного тіку l", size=10.5))
    f.append(text(bx2 + box_w / 2, 168, "c = c + 1 або max(c, msg.c) + 1", size=10, bold=True))
    f.append(text(bx2 + box_w / 2, 188, "Скидається в 0, коли pt наздоганяє l", size=9.5, color=MUTED))

    # 3. Ідентифікатор вузла
    bx3 = bx2 + box_w + 10
    f.append(rect(bx3, 105, box_w, 115, fill=WARN_BG, stroke=LINE, sw=1.5, rx=6))
    f.append(text(bx3 + box_w / 2, 128, "node_id : Вузол (Tie-breaker)", size=12.5, bold=True))
    f.append(text(bx3 + box_w / 2, 150, "Унікальний номер вузла в кластері", size=10.5))
    f.append(text(bx3 + box_w / 2, 168, "Забезпечує строгий повний порядок", size=10, bold=True))
    f.append(text(bx3 + box_w / 2, 188, "Вирішує колізії при однакових (l, c)", size=9.5, color=MUTED))

    # Нижній блок: Бінарне представлення в пам'яті (64-бітний або 96-бітний формат)
    f.append(rect(40, 260, W - 80, 235, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, 285, "Компактне бінарне кодування (фіксований розмір O(1))", size=13, bold=True))

    # Візуалізація бітової смуги
    bit_y = 310
    total_bit_w = W - 160
    l_bit_w = total_bit_w * 0.65
    c_bit_w = total_bit_w * 0.35

    f.append(rect(80, bit_y, l_bit_w, 45, fill=COOL, stroke=NEG, sw=1.8, rx=4))
    f.append(text(80 + l_bit_w / 2, bit_y + 22, "Фізичний час l (48 бітів або 64 біти)", size=11.5, bold=True, color=NEG))
    f.append(text(80 + l_bit_w / 2, bit_y + 37, "Мілісекунди або наносекунди від Unix Epoch", size=9.5, color=MUTED))

    f.append(rect(80 + l_bit_w, bit_y, c_bit_w, 45, fill=GOOD, stroke=FIELD, sw=1.8, rx=4))
    f.append(text(80 + l_bit_w + c_bit_w / 2, bit_y + 22, "Лічильник c (16 або 32 біти)", size=11.5, bold=True, color=FIELD))
    f.append(text(80 + l_bit_w + c_bit_w / 2, bit_y + 37, "Логічний інкремент", size=9.5, color=MUTED))

    # Правило лексикографічного порівняння
    rule_y = 380
    f.append(fitbox(80, rule_y, W - 160, 95,
                    "Правило лексикографічного порівняння:\n"
                    "ts1 < ts2  <=>  (l1 < l2) АБО (l1 == l2 ТА c1 < c2) АБО (l1 == l2 ТА c1 == c2 ТА node1 < node2)\n"
                    "У Big-Endian бінарному форматі звичайне числове або memcmp() порівняння безпосередньо відтворює причинний порядок.",
                    size=10.5, pad=8, fill=FILL, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, "hlc-structure.svg"), W, H, *f)


# ── 2. Потік подій та оновлення HLC між вузлами ─────────────────────────────
def hlc_events_flow():
    W, H = 1000, 600
    f = []

    f.append(text(W / 2, 28, "Потік подій, перехід станів та оновлення HLC між трьома вузлами", size=15.5, bold=True))

    # 3 осі вузлів
    y1, y2, y3 = 110, 260, 420
    x_start, x_end = 160, W - 60

    # Лінії часу
    f.append(line(x_start, y1, x_end, y1, color=LINE, sw=2))
    f.append(line(x_start, y2, x_end, y2, color=LINE, sw=2))
    f.append(line(x_start, y3, x_end, y3, color=LINE, sw=2))

    # Заголовки вузлів з фізичними годинниками (зі скосом/skew)
    f.append(fitbox(20, y1 - 25, 125, 50, "Вузол A\npt_A = t", size=11, bold=True, fill=COOL, stroke=LINE))
    f.append(fitbox(20, y2 - 25, 125, 50, "Вузол B (відстає)\npt_B = t - 8", size=11, bold=True, fill=WARM, stroke=POS))
    f.append(fitbox(20, y3 - 25, 125, 50, "Вузол C (поспішає)\npt_C = t + 5", size=11, bold=True, fill=WARN_BG, stroke=LINE))

    # Подія e1 на вузлі A: Локальна подія при pt = 100
    e1_x = 220
    f.append(circle(e1_x, y1, 6, fill=POS, stroke=LINE, sw=1.5))
    f.append(fitbox(e1_x - 55, y1 - 65, 110, 48, "e1: Локальна подія\npt=100\nHLC = (100, 0)", size=9.5, fill=COOL, stroke=LINE))

    # Подія e2 на вузлі A: Друга подія при тому самому фізичному тіку pt = 100
    e2_x = 360
    f.append(circle(e2_x, y1, 6, fill=POS, stroke=LINE, sw=1.5))
    f.append(fitbox(e2_x - 55, y1 - 65, 110, 48, "e2: Відправка m1\npt=100\nHLC = (100, 1)", size=9.5, fill=COOL, stroke=LINE))

    # Стрілка відправки повідомлення m1 від Вузла A до Вузла B
    f.append(arrow(e2_x, y1 + 6, 480, y2 - 6, color=POS, sw=2))
    f.append(text(400, 180, "Повідомлення m1 з міткою (100, 1)", size=10, bold=True, color=POS))

    # Подія e3 на вузлі B: Отримання повідомлення m1 при pt = 92 (годинник B відстає!)
    e3_x = 480
    f.append(circle(e3_x, y2, 6, fill=FIELD, stroke=LINE, sw=1.5))
    f.append(fitbox(e3_x - 85, y2 + 18, 170, 62, "e3: Прийом m1 (pt=92 < 100)\nl = max(92, 100) = 100\nc = 1 + 1 = 2\nHLC = (100, 2)", size=9, fill=GOOD, stroke=FIELD))

    # Подія e4 на вузлі B: Локальна подія пізніше, коли фізичний годинник B наздогнав (pt = 108)
    e4_x = 680
    f.append(circle(e4_x, y2, 6, fill=POS, stroke=LINE, sw=1.5))
    f.append(fitbox(e4_x - 80, y2 - 65, 160, 50, "e4: Відправка m2 (pt=108)\n108 > 100 -> l=108, c=0\nHLC = (108, 0)", size=9, fill=COOL, stroke=LINE))

    # Стрілка відправки повідомлення m2 від Вузла B до Вузла C
    f.append(arrow(e4_x, y2 + 6, 800, y3 - 6, color=FIELD, sw=2))
    f.append(text(720, 340, "Повідомлення m2 з міткою (108, 0)", size=10, bold=True, color=FIELD))

    # Подія e5 на вузлі C: Отримання повідомлення m2 при pt = 114 (годинник C поспішає)
    e5_x = 800
    f.append(circle(e5_x, y3, 6, fill=FIELD, stroke=LINE, sw=1.5))
    f.append(fitbox(e5_x - 85, y3 + 18, 170, 62, "e5: Прийом m2 (pt=114 > 108)\nl = max(108, 114) = 114\nc = 0 (скидання лічильника)\nHLC = (114, 0)", size=9, fill=GOOD, stroke=FIELD))

    # Нижній висновок
    f.append(fitbox(40, 505, W - 80, 75,
                    "Ключові інваріанти на часовій діаграмі:\n"
                    "1. Причинність зберігається: e1 (100,0) < e2 (100,1) < e3 (100,2) < e4 (108,0) < e5 (114,0).\n"
                    "2. Коли локальний годинник відстає (e3), компонента l «перестрибує» наперед, а лічильник c інкрементується.\n"
                    "3. Щойно фізичний час наздоганяє l (e4, e5), компонента l стає рівною pt, а логічний лічильник c скидається в 0.",
                    size=10, pad=6, fill=FILL, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, "hlc-events-flow.svg"), W, H, *f)


# ── 3. Еволюція та порівняння розподілених годинників ────────────────────────
def clocks_evolution():
    W, H = 1040, 620
    f = []

    f.append(text(W / 2, 28, "Порівняльний спектр підходів до вимірювання часу в розподілених системах", size=15.5, bold=True))

    headers = ["Властивість / Модель", "NTP / Wall Clock", "Годинник Лампорта", "Векторний годинник", "TrueTime (Spanner)", "HLC (Гібридний)"]
    col_w = [180, 160, 160, 170, 170, 170]
    xs = [15]
    for w in col_w[:-1]:
        xs.append(xs[-1] + w)

    # Шапка таблиці
    head_y = 55
    f.append(rect(15, head_y, W - 30, 35, fill=COOL, stroke=LINE, sw=1.5, rx=4))
    for i, h in enumerate(headers):
        f.append(text(xs[i] + col_w[i] / 2, head_y + 22, h, size=11, bold=True))

    # Рядки таблиці
    rows = [
        ("Розмір мітки часу", "8 байтів (O(1))", "8 байтів (O(1))", "O(N) (росте з вузлами)", "16-24 байти (O(1))", "8-12 байтів (O(1))"),
        ("Збереження причинності\n(e -> f => T(e) < T(f))", "НІ\n(через skew порушується)", "ТАК\n(гарантовано)", "ТАК\n(гарантовано)", "ТАК\n(через commit-wait)", "ТАК\n(гарантовано)"),
        ("Виявлення конкурентності\n(e || f)", "НІ", "НІ", "ТАК\n(істинне причинне порівняння)", "НІ\n(лише через порядок)", "НІ\n(дає довільний повний порядок)"),
        ("Прив'язка до фізичного часу", "Пряма (але нестійка)", "ВІДСУТНЯ\n(абстрактне число)", "ВІДСУТНЯ\n(вектор лічильників)", "СТРОГА\n[t.earliest, t.latest]", "ОБМЕЖЕНА\n|l - pt| <= ε"),
        ("Вимоги до заліза / мережі", "Стандартний NTP", "Звичайне залізо", "Звичайне залізо", "GPS + Атомні годинники\nу кожному ДЦ", "Стандартний NTP\n(програмне рішення)"),
        ("Запити знімків стану (MVCC)\nта Time-Travel queries", "Схильні до аномалій\nвтрати оновлень", "Неможливо співставити\nз астрономічним часом", "Високий оверхед\nзберігання векторів", "Ідеально\n(без блокувань читання)", "Ефективно\n(з вікном невизначеності ε)")
    ]

    row_y = 95
    for idx, r in enumerate(rows):
        h_row = 70 if "\n" in r[0] or "\n" in r[1] or "\n" in r[4] else 50
        bg = GOOD if idx % 2 == 0 else "#ffffff"
        # Особливий акцент на колонку HLC
        f.append(rect(15, row_y, W - 30, h_row, fill=bg, stroke=LINE, sw=1))
        f.append(rect(xs[5], row_y, col_w[5], h_row, fill=COOL, stroke=LINE, sw=1))

        for j, val in enumerate(r):
            lines = val.split("\n")
            cy = row_y + h_row / 2 - (len(lines) - 1) * 12 / 2 + 4
            is_bold = (j == 0 or j == 5)
            c_color = NEG if "НІ" in lines[0] or "ВІДСУТНЯ" in lines[0] else (FIELD if "ТАК" in lines[0] or "Ефективно" in lines[0] or "Ідеально" in lines[0] else INK)
            for li, line_text in enumerate(lines):
                cur_color = c_color if li == 0 else MUTED
                f.append(text(xs[j] + col_w[j] / 2, cy + li * 13, line_text, size=9.5, bold=is_bold, color=cur_color))

        row_y += h_row

    # Підсумковий висновок
    f.append(fitbox(15, row_y + 10, W - 30, 65,
                    "Висновок: HLC поєднує компактність і масштабованість годинників Лампорта (O(1)) із прив'язкою до реального часу TrueTime,\n"
                    "не вимагаючи спеціалізованого апаратного обладнання (атомних годинників чи супутникових GPS-приймачів).",
                    size=10.5, pad=6, fill=COOL, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, "clocks-evolution.svg"), W, H, *f)


if __name__ == "__main__":
    hlc_structure()
    hlc_events_flow()
    clocks_evolution()
    print("Усі 3 фігури успішно згенеровано.")
