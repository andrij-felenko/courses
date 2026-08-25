# -*- coding: utf-8 -*-
"""
Фігури до статті «Відстань Левенштейна».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_wagner_fisher_matrix():
    W, H = 860, 520
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 28, "Матриця Вагнера—Фішера: покрокове обчислення відстані між KITTEN та SITTING", size=15, bold=True))

    ox, oy = 60, 75
    cw, ch = 48, 44

    s1 = ["ε", "K", "I", "T", "T", "E", "N"]
    s2 = ["ε", "S", "I", "T", "T", "I", "N", "G"]
    
    matrix = [
        [0, 1, 2, 3, 4, 5, 6, 7],
        [1, 1, 2, 3, 4, 5, 6, 7],
        [2, 2, 1, 2, 3, 4, 5, 6],
        [3, 3, 2, 1, 2, 3, 4, 5],
        [4, 4, 3, 2, 1, 2, 3, 4],
        [5, 5, 4, 3, 2, 2, 3, 4],
        [6, 6, 5, 4, 3, 3, 2, 3]
    ]

    opt_path = {(0,0), (1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (6,7)}

    for j, ch_s2 in enumerate(s2):
        x = ox + (j + 1) * cw
        y = oy
        parts.append(rect(x, y, cw, ch, fill="#f0f4f8", stroke="#b0c4de", sw=1))
        parts.append(text(x + cw / 2, y + 27, ch_s2, size=14, bold=True, color=NEG))
        parts.append(text(x + cw / 2, y + 12, "j=%d" % j, size=9, color=MUTED))

    for i, ch_s1 in enumerate(s1):
        x = ox
        y = oy + (i + 1) * ch
        parts.append(rect(x, y, cw, ch, fill="#f0f4f8", stroke="#b0c4de", sw=1))
        parts.append(text(x + cw / 2, y + 27, ch_s1, size=14, bold=True, color=POS))
        parts.append(text(x + cw / 2, y + 12, "i=%d" % i, size=9, color=MUTED))

    parts.append(rect(ox, oy, cw, ch, fill="#e8edf2", stroke="#b0c4de", sw=1))
    parts.append(text(ox + cw / 2, oy + 26, "D[i,j]", size=11, bold=True, color=MUTED))

    for i in range(7):
        for j in range(8):
            x = ox + (j + 1) * cw
            y = oy + (i + 1) * ch
            val = matrix[i][j]
            is_path = (i, j) in opt_path

            if is_path:
                if i == 6 and j == 7:
                    cell_fill = "#d4edda"
                    cell_stroke = FIELD
                    sw_val = 2
                else:
                    cell_fill = "#fff3cd"
                    cell_stroke = "#e0a800"
                    sw_val = 1.8
            else:
                cell_fill = "#ffffff"
                cell_stroke = "#d0d7de"
                sw_val = 1

            parts.append(rect(x, y, cw, ch, fill=cell_fill, stroke=cell_stroke, sw=sw_val))
            parts.append(text(x + cw / 2, y + 28, str(val), size=14, bold=is_path, color=INK if not is_path else "#856404"))

    p1 = (ox + 8 * cw + cw / 2, oy + 7 * ch + ch / 2)
    p2 = (ox + 7 * cw + cw / 2, oy + 7 * ch + ch / 2)
    parts.append(arrow(p1[0] - 12, p1[1], p2[0] + 12, p2[1], color=FIELD, sw=2))

    for step_i, step_j in [(6,6), (5,5), (4,4), (3,3), (2,2), (1,1)]:
        pt_from = (ox + (step_j + 1) * cw + cw / 2, oy + (step_i + 1) * ch + ch / 2)
        pt_to = (ox + step_j * cw + cw / 2, oy + step_i * ch + ch / 2)
        parts.append(arrow(pt_from[0] - 8, pt_from[1] - 8, pt_to[0] + 8, pt_to[1] + 8, color=FIELD, sw=2))

    rx, ry, rw, rh = 515, 75, 320, 410
    parts.append(rect(rx, ry, rw, rh, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=6))
    parts.append(text(rx + rw / 2, ry + 24, "Рекурентне правило переходу", size=13, bold=True, color=INK))

    cx, cy = rx + 65, ry + 80
    parts.append(rect(cx - 30, cy - 30, 36, 32, fill="#e8f0fe", stroke="#1a73e8", sw=1.2))
    parts.append(text(cx - 12, cy - 10, "↖ D[i-1,j-1]", size=9, bold=True, color=INK))
    parts.append(text(cx + 40, cy - 10, "Заміна/Збіг (+0 або +1)", size=11, color=INK, anchor="start"))

    parts.append(rect(cx + 30, cy - 30, 36, 32, fill="#fce8e6", stroke=POS, sw=1.2))
    parts.append(text(cx + 48, cy - 10, "↑ D[i-1,j]", size=9, bold=True, color=INK))
    parts.append(text(cx + 40, cy + 20, "Видалення (+1)", size=11, color=INK, anchor="start"))

    parts.append(rect(cx - 30, cy + 30, 36, 32, fill="#e6f4ea", stroke=FIELD, sw=1.2))
    parts.append(text(cx - 12, cy + 50, "← D[i,j-1]", size=9, bold=True, color=INK))
    parts.append(text(cx + 40, cy + 50, "Вставка (+1)", size=11, color=INK, anchor="start"))

    parts.append(rect(cx + 30, cy + 30, 36, 32, fill="#fff3cd", stroke="#e0a800", sw=1.5))
    parts.append(text(cx + 48, cy + 50, "D[i,j]", size=11, bold=True, color="#856404"))

    parts.append(rect(rx + 15, ry + 165, rw - 30, 85, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=4))
    parts.append(text(rx + rw / 2, ry + 185, "D[i,j] = min(", size=12, bold=True))
    parts.append(text(rx + rw / 2, ry + 205, "D[i-1, j] + 1,       // видалення", size=11, color=POS))
    parts.append(text(rx + rw / 2, ry + 223, "D[i, j-1] + 1,       // вставка", size=11, color=FIELD))
    parts.append(text(rx + rw / 2, ry + 241, "D[i-1, j-1] + cost   // заміна/збіг", size=11, color=NEG))

    parts.append(rect(rx + 15, ry + 265, rw - 30, 130, fill="#f6f8fa", stroke="#d0d7de", sw=1, rx=4))
    parts.append(text(rx + rw / 2, ry + 285, "Відновлений скрипт вирівнювання: KITTEN -> SITTING", size=11, bold=True))
    parts.append(text(rx + rw / 2, ry + 307, "K  I  T  T  E  N  _", size=12, bold=True, color=POS))
    parts.append(text(rx + rw / 2, ry + 325, "S  I  T  T  I  N  G", size=12, bold=True, color=NEG))
    parts.append(text(rx + rw / 2, ry + 345, "S  M  M  M  S  M  I", size=11, bold=True, color=MUTED))
    parts.append(text(rx + rw / 2, ry + 372, "Разом: 2 заміни + 1 вставка = 3", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "wagner-fisher-matrix.svg"), W, H, *parts)


def fig_space_optimization():
    W, H = 840, 420
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 28, "Просторова оптимізація матриці DP: від O(N·M) до O(min(N, M)) пам'яті", size=15, bold=True))

    lx, ly, lw, lh = 30, 60, 370, 330
    parts.append(rect(lx, ly, lw, lh, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=6))
    parts.append(text(lx + lw / 2, ly + 25, "Варіант А: Два вектори (попередній та поточний)", size=13, bold=True, color=INK))

    py1 = ly + 70
    parts.append(text(lx + 45, py1 + 20, "prev:", size=12, bold=True, color=MUTED))
    for j in range(5):
        jx = lx + 80 + j * 50
        parts.append(rect(jx, py1, 46, 36, fill="#e8f0fe", stroke="#1a73e8", sw=1.2))
        parts.append(text(jx + 23, py1 + 23, "D[i-1,%d]" % j, size=9, bold=True, color=INK))

    py2 = ly + 150
    parts.append(text(lx + 45, py2 + 20, "curr:", size=12, bold=True, color=MUTED))
    for j in range(5):
        jx = lx + 80 + j * 50
        if j < 3:
            fill_c, strk_c = "#d4edda", FIELD
            lbl = "обчисл."
        elif j == 3:
            fill_c, strk_c = "#fff3cd", "#e0a800"
            lbl = "D[i,j]"
        else:
            fill_c, strk_c = "#ffffff", "#d0d7de"
            lbl = "ще ні"
        parts.append(rect(jx, py2, 46, 36, fill=fill_c, stroke=strk_c, sw=1.2 if j != 3 else 2))
        parts.append(text(jx + 23, py2 + 23, lbl, size=9, bold=(j == 3), color=INK))

    parts.append(arrow(lx + 80 + 2 * 50 + 23, py1 + 36, lx + 80 + 3 * 50 + 15, py2, color=NEG, sw=1.8))
    parts.append(arrow(lx + 80 + 3 * 50 + 23, py1 + 36, lx + 80 + 3 * 50 + 23, py2, color=POS, sw=1.8))
    parts.append(arrow(lx + 80 + 2 * 50 + 46, py2 + 18, lx + 80 + 3 * 50, py2 + 18, color=FIELD, sw=1.8))

    parts.append(rect(lx + 20, ly + 215, lw - 40, 95, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=4))
    parts.append(text(lx + lw / 2, ly + 235, "Пам'ять: 2 · (M + 1) чисел", size=12, bold=True, color=INK))
    parts.append(text(lx + lw / 2, ly + 260, "Після завершення рядка: swap(prev, curr)", size=11, color=MUTED))
    parts.append(text(lx + lw / 2, ly + 285, "Складність пам'яті: O(min(N, M))", size=12, bold=True, color=FIELD))

    rx, ry, rw, rh = 440, 60, 370, 330
    parts.append(rect(rx, ry, rw, rh, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=6))
    parts.append(text(rx + rw / 2, ry + 25, "Варіант Б: Один вектор dp[0..M] + регістр diag", size=13, bold=True, color=INK))

    ry1 = ry + 80
    parts.append(text(rx + 35, ry1 + 20, "dp[]:", size=12, bold=True, color=MUTED))
    for j in range(5):
        jx = rx + 75 + j * 54
        if j < 3:
            fill_c, strk_c = "#d4edda", FIELD
            lbl = "нові"
        elif j == 3:
            fill_c, strk_c = "#fff3cd", "#e0a800"
            lbl = "поточ."
        else:
            fill_c, strk_c = "#e8f0fe", "#1a73e8"
            lbl = "старі"
        parts.append(rect(jx, ry1, 50, 36, fill=fill_c, stroke=strk_c, sw=1.2 if j == 3 else 1))
        parts.append(text(jx + 25, ry1 + 23, lbl, size=10, bold=(j == 3), color=INK))

    rx_diag, ry_diag = rx + rw / 2 - 60, ry + 150
    parts.append(rect(rx_diag, ry_diag, 120, 34, fill="#fce8e6", stroke=POS, sw=1.5, rx=4))
    parts.append(text(rx_diag + 60, ry_diag + 22, "diag = D[i-1, j-1]", size=10, bold=True, color=POS))

    parts.append(arrow(rx_diag + 60, ry_diag, rx + 75 + 3 * 54 + 25, ry1 + 36, color=POS, sw=1.8))

    parts.append(rect(rx + 20, ry + 205, rw - 40, 105, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=4))
    parts.append(text(rx + rw / 2, ry + 225, "Збереження діагоналі перед перезаписом:", size=11, bold=True))
    parts.append(text(rx + rw / 2, ry + 248, "temp = dp[j];", size=11, color=MUTED))
    parts.append(text(rx + rw / 2, ry + 268, "dp[j] = min(dp[j]+1, dp[j-1]+1, diag+cost);", size=10, bold=True, color=INK))
    parts.append(text(rx + rw / 2, ry + 290, "diag = temp;  // стає діагоналлю для j+1", size=10, color=POS))

    render(os.path.join(IMG, "space-optimization.svg"), W, H, *parts)


def fig_damerau_transposition():
    W, H = 840, 400
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 28, "Відстань Дамерау—Левенштейна: обробка транспозиції двох сусідніх символів", size=15, bold=True))

    lx, ly, lw, lh = 30, 60, 360, 310
    parts.append(rect(lx, ly, lw, lh, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=6))
    parts.append(text(lx + lw / 2, ly + 25, "Порівняння оцінки перестановки літер", size=13, bold=True, color=INK))

    parts.append(rect(lx + 15, ly + 50, lw - 30, 110, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=4))
    parts.append(text(lx + 25, ly + 72, "Класичний Левенштейн:", size=12, bold=True, color=POS, anchor="start"))
    parts.append(text(lx + 25, ly + 95, "Слово «TEHS» -> «THES» (перестановка E та H)", size=10, color=MUTED, anchor="start"))
    parts.append(text(lx + 25, ly + 118, "Операції: Заміна E->H + Заміна H->E", size=10, color=INK, anchor="start"))
    parts.append(text(lx + 25, ly + 142, "Вартість = 2 операції (або Видалення + Вставка)", size=11, bold=True, color=POS, anchor="start"))

    parts.append(rect(lx + 15, ly + 175, lw - 30, 115, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(lx + 25, ly + 197, "Дамерау—Левенштейн (з транспозицією):", size=12, bold=True, color=FIELD, anchor="start"))
    parts.append(text(lx + 25, ly + 220, "Слово «TEHS» -> «THES»", size=10, color=MUTED, anchor="start"))
    parts.append(text(lx + 25, ly + 243, "Операція: Транспозиція (обмін місцями) EH <-> HE", size=10, color=INK, anchor="start"))
    parts.append(text(lx + 25, ly + 268, "Вартість = 1 операція (природна друкарська помилка)", size=11, bold=True, color=FIELD, anchor="start"))

    rx, ry, rw, rh = 420, 60, 390, 310
    parts.append(rect(rx, ry, rw, rh, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=6))
    parts.append(text(rx + rw / 2, ry + 25, "Четвертий перехід у комірці D[i, j]", size=13, bold=True, color=INK))

    mx, my = rx + 30, ry + 55
    cw, ch = 56, 46

    for row in range(3):
        for col in range(3):
            cx = mx + col * cw
            cy = my + row * ch
            if row == 0 and col == 0:
                fill_c, strk_c = "#e8f0fe", "#1a73e8"
                lbl = "D[i-2,j-2]"
            elif row == 2 and col == 2:
                fill_c, strk_c = "#fff3cd", "#e0a800"
                lbl = "D[i,j]"
            else:
                fill_c, strk_c = "#ffffff", "#d0d7de"
                lbl = ""
            parts.append(rect(cx, cy, cw, ch, fill=fill_c, stroke=strk_c, sw=1.5 if (row==2 and col==2) or (row==0 and col==0) else 1))
            if lbl:
                parts.append(text(cx + cw / 2, cy + ch / 2 + 5, lbl, size=10, bold=True, color=INK))

    parts.append(arrow(mx + cw + 10, my + 15, mx + 2 * cw + 10, my + 2 * ch + 15, color=POS, sw=2.2))
    parts.append(text(mx + 2 * cw + 30, my + ch + 15, "Транспозиція (+1)", size=11, bold=True, color=POS, anchor="start"))

    parts.append(rect(rx + 15, ry + 205, rw - 30, 85, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=4))
    parts.append(text(rx + rw / 2, ry + 225, "Умова застосування транспозиції:", size=11, bold=True, color=INK))
    parts.append(text(rx + rw / 2, ry + 248, "s1[i - 1] == s2[j - 2]  та  s1[i - 2] == s2[j - 1]", size=11, color=NEG))
    parts.append(text(rx + rw / 2, ry + 272, "D[i,j] = min(D[i,j], D[i-2, j-2] + 1)", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG, "damerau-transposition.svg"), W, H, *parts)


def fig_ukkonen_band():
    W, H = 840, 420
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 28, "Алгоритм Укконена: динамічне програмування у діагональній смузі ширини 2k + 1", size=15, bold=True))

    ox, oy = 70, 70
    N, M = 8, 8
    cw, ch = 38, 36
    k = 2

    for i in range(N):
        for j in range(M):
            x = ox + j * cw
            y = oy + i * ch
            diag_dist = abs(i - j)

            if diag_dist <= k:
                if diag_dist == 0:
                    fill_c = "#d4edda"
                    strk_c = FIELD
                else:
                    fill_c = "#ffffff"
                    strk_c = "#a0c4de"
                active = True
            else:
                fill_c = "#f0f2f5"
                strk_c = "#e1e4e8"
                active = False

            parts.append(rect(x, y, cw, ch, fill=fill_c, stroke=strk_c, sw=1.2 if active else 0.8))

            if not active:
                parts.append(text(x + cw / 2, y + ch / 2 + 4, "×", size=11, color="#b0b8c4"))
            elif diag_dist == 0:
                parts.append(text(x + cw / 2, y + ch / 2 + 4, "0", size=10, bold=True, color=FIELD))

    parts.append(text(ox + M * cw / 2, oy + N * ch + 25, "Діагональна смуга обчислень: |i - j| ≤ k (k = 2)", size=12, bold=True, color=INK))

    rx, ry, rw, rh = 430, 70, 380, 310
    parts.append(rect(rx, ry, rw, rh, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=6))
    parts.append(text(rx + rw / 2, ry + 25, "Переваги смугового відсікання", size=13, bold=True, color=INK))

    parts.append(rect(rx + 15, ry + 50, rw - 30, 75, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=4))
    parts.append(text(rx + 25, ry + 72, "Повний алгоритм Вагнера—Фішера:", size=11, bold=True, color=POS, anchor="start"))
    parts.append(text(rx + 25, ry + 94, "Кількість клітинок: N · M", size=11, color=INK, anchor="start"))
    parts.append(text(rx + 25, ry + 112, "Часова складність: O(N · M)", size=11, bold=True, color=POS, anchor="start"))

    parts.append(rect(rx + 15, ry + 135, rw - 30, 85, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(rx + 25, ry + 157, "Смуговий алгоритм Укконена:", size=11, bold=True, color=FIELD, anchor="start"))
    parts.append(text(rx + 25, ry + 179, "Кількість клітинок: (2k + 1) · min(N, M)", size=11, color=INK, anchor="start"))
    parts.append(text(rx + 25, ry + 201, "Часова складність: O(k · min(N, M))", size=12, bold=True, color=FIELD, anchor="start"))

    parts.append(rect(rx + 15, ry + 230, rw - 30, 65, fill="#e8f0fe", stroke="#1a73e8", sw=1, rx=4))
    parts.append(text(rx + rw / 2, ry + 252, "При N = M = 1000 та k = 2:", size=11, bold=True, color=INK))
    parts.append(text(rx + rw / 2, ry + 275, "1 000 000 клітинок -> 5 000 клітинок (прискорення ×200)", size=11, bold=True, color="#1a73e8"))

    render(os.path.join(IMG, "ukkonen-band.svg"), W, H, *parts)


def fig_levenshtein_trie():
    W, H = 860, 440
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 28, "Пошук з помилками у префіксному дереві (Trie) за допомогою векторів DP", size=15, bold=True))

    root_x, root_y = 220, 75
    parts.append(rect(root_x - 30, root_y - 18, 60, 36, fill="#f0f4f8", stroke="#1a73e8", sw=1.5, rx=6))
    parts.append(text(root_x, root_y + 5, "ROOT", size=11, bold=True, color=INK))
    parts.append(text(root_x + 40, root_y + 5, "[0, 1, 2, 3]", size=10, bold=True, color=MUTED, anchor="start"))

    c_x, c_y = 220, 155
    parts.append(arrow(root_x, root_y + 18, c_x, c_y - 18, color=LINE, sw=1.5))
    parts.append(text(root_x + 10, root_y + 50, "'c'", size=12, bold=True, color=POS, anchor="start"))
    parts.append(rect(c_x - 25, c_y - 18, 50, 36, fill="#ffffff", stroke="#b0c4de", sw=1.2, rx=6))
    parts.append(text(c_x, c_y + 5, "'c'", size=12, bold=True, color=INK))
    parts.append(text(c_x + 35, c_y + 5, "[1, 0, 1, 2]", size=10, bold=True, color=FIELD, anchor="start"))

    a_x, a_y = 220, 235
    parts.append(arrow(c_x, c_y + 18, a_x, a_y - 18, color=LINE, sw=1.5))
    parts.append(text(c_x + 10, c_y + 50, "'a'", size=12, bold=True, color=POS, anchor="start"))
    parts.append(rect(a_x - 25, a_y - 18, 50, 36, fill="#ffffff", stroke="#b0c4de", sw=1.2, rx=6))
    parts.append(text(a_x, a_y + 5, "'a'", size=12, bold=True, color=INK))
    parts.append(text(a_x + 35, a_y + 5, "[2, 1, 0, 1]", size=10, bold=True, color=FIELD, anchor="start"))

    t1_x, t1_y = 110, 335
    parts.append(arrow(a_x - 15, a_y + 18, t1_x + 15, t1_y - 18, color=LINE, sw=1.5))
    parts.append(text((a_x + t1_x) / 2 - 20, (a_y + t1_y) / 2, "'t'", size=12, bold=True, color=POS))
    parts.append(rect(t1_x - 30, t1_y - 18, 60, 36, fill="#d4edda", stroke=FIELD, sw=2, rx=6))
    parts.append(text(t1_x, t1_y + 5, "★ 't'", size=11, bold=True, color=FIELD))
    parts.append(text(t1_x + 40, t1_y + 5, "[3, 2, 1, 0] -> d=0", size=10, bold=True, color=FIELD, anchor="start"))

    r_x, r_y = 330, 335
    parts.append(arrow(a_x + 15, a_y + 18, r_x - 15, r_y - 18, color=LINE, sw=1.5))
    parts.append(text((a_x + r_x) / 2 + 20, (a_y + r_y) / 2, "'r'", size=12, bold=True, color=POS))
    parts.append(rect(r_x - 25, r_y - 18, 50, 36, fill="#ffffff", stroke="#b0c4de", sw=1.2, rx=6))
    parts.append(text(r_x, r_y + 5, "'r'", size=12, bold=True, color=INK))
    parts.append(text(r_x + 35, r_y + 5, "[3, 2, 1, 1]", size=10, bold=True, color=MUTED, anchor="start"))

    s_x, s_y = 330, 400
    parts.append(arrow(r_x, r_y + 18, s_x, s_y - 16, color=LINE, sw=1.2))
    parts.append(rect(s_x - 30, s_y - 16, 60, 30, fill="#d4edda", stroke=FIELD, sw=1.8, rx=6))
    parts.append(text(s_x, s_y + 4, "★ 's'", size=10, bold=True, color=FIELD))
    parts.append(text(s_x + 40, s_y + 4, "[4, 3, 2, 2] -> d=2", size=9, bold=True, color=MUTED, anchor="start"))

    px, py, pw, ph = 470, 75, 360, 340
    parts.append(rect(px, py, pw, ph, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=6))
    parts.append(text(px + pw / 2, py + 25, "Механізм векторного пошуку в Trie", size=13, bold=True, color=INK))

    parts.append(rect(px + 15, py + 50, pw - 30, 80, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=4))
    parts.append(text(px + 25, py + 70, "1. Запит: «cat» (довжина 3)", size=11, bold=True, color=POS, anchor="start"))
    parts.append(text(px + 25, py + 90, "Вектор у ROOT: [0, 1, 2, 3]  (базовий рядок DP)", size=10, color=MUTED, anchor="start"))
    parts.append(text(px + 25, py + 110, "Максимальна дистанція: k = 1", size=10, bold=True, color=INK, anchor="start"))

    parts.append(rect(px + 15, py + 140, pw - 30, 95, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=4))
    parts.append(text(px + 25, py + 160, "2. Перехід до дочірнього вузла:", size=11, bold=True, color=NEG, anchor="start"))
    parts.append(text(px + 25, py + 180, "Обчислюється ОДИН новий рядок DP", size=10, color=INK, anchor="start"))
    parts.append(text(px + 25, py + 200, "Спільний префікс «ca» обчислюється 1 раз", size=10, bold=True, color=FIELD, anchor="start"))
    parts.append(text(px + 25, py + 220, "для всіх тисяч слів зі спільним початком!", size=10, color=MUTED, anchor="start"))

    parts.append(rect(px + 15, py + 245, pw - 30, 80, fill="#fff3cd", stroke="#e0a800", sw=1.2, rx=4))
    parts.append(text(px + 25, py + 265, "3. Раннє відсікання піддерев (Pruning):", size=11, bold=True, color="#856404", anchor="start"))
    parts.append(text(px + 25, py + 288, "Якщо min(dp_vector) > k :", size=10, bold=True, color=POS, anchor="start"))
    parts.append(text(px + 25, py + 308, "Усе піддерево відкидається без перебору!", size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "levenshtein-trie.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_wagner_fisher_matrix()
    fig_space_optimization()
    fig_damerau_transposition()
    fig_ukkonen_band()
    fig_levenshtein_trie()
    print("All figures generated successfully.")
