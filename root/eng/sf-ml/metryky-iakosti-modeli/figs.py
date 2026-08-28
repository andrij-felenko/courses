# -*- coding: utf-8 -*-
"""Генератор SVG-діаграм для теми «Метрики якості моделі»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1 — Матриця плутанини та похідні метрики
# ─────────────────────────────────────────────────────────────────────────────
def fig_confusion_matrix():
    W, H = 940, 560
    p = []
    
    # Заголовок зверху
    p.append(text(W / 2, 28, "Матриця плутанини 2×2 та похідні інженерні коефіцієнти", size=16, color=INK, bold=True))
    
    # Координати сітки 2x2
    grid_x0, grid_y0 = 180, 110
    cw, ch = 170, 110
    
    # Підписи стовпців (передбачення)
    bx_p1 = fitbox(grid_x0, grid_y0 - 55, cw, 42, "Передбачено: POS (+)\nPredicted Positive (PP)", size=12, pad=4, fill="#f8fafc", stroke=LINE, bold=True)
    bx_p0 = fitbox(grid_x0 + cw + 10, grid_y0 - 55, cw, 42, "Передбачено: NEG (−)\nPredicted Negative (PN)", size=12, pad=4, fill="#f8fafc", stroke=LINE, bold=True)
    p.append(bx_p1)
    p.append(bx_p0)
    
    # Підписи рядків (дійсна істина)
    bx_a1 = fitbox(grid_x0 - 155, grid_y0, 145, ch, "Дійсно: POS (+)\nActual Positive\nP = TP + FN", size=12, pad=6, fill="#f8fafc", stroke=LINE, bold=True)
    bx_a0 = fitbox(grid_x0 - 155, grid_y0 + ch + 10, 145, ch, "Дійсно: NEG (−)\nActual Negative\nN = FP + TN", size=12, pad=6, fill="#f8fafc", stroke=LINE, bold=True)
    p.append(bx_a1)
    p.append(bx_a0)
    
    # 4 комірки матриці
    # 1. TP (True Positive)
    c_tp = fitbox(grid_x0, grid_y0, cw, ch,
                  "TP (True Positive)\nІстинно позитивні\n\nВлучання в ціль\n(передбачено +, дійсно +)",
                  size=12, pad=6, fill="#eafaf0", stroke=FIELD, sw=2, bold=True, color=FIELD)
    p.append(c_tp)
    
    # 2. FN (False Negative)
    c_fn = fitbox(grid_x0 + cw + 10, grid_y0, cw, ch,
                  "FN (False Negative)\nПомилка II роду (β)\n\nПропуск цілі\n(передбачено −, дійсно +)",
                  size=12, pad=6, fill="#fdecea", stroke=POS, sw=2, bold=True, color=POS)
    p.append(c_fn)
    
    # 3. FP (False Positive)
    c_fp = fitbox(grid_x0, grid_y0 + ch + 10, cw, ch,
                  "FP (False Positive)\nПомилка I роду (α)\n\nФальшива тривога\n(передбачено +, дійсно −)",
                  size=12, pad=6, fill="#fff7ed", stroke="#ea580c", sw=2, bold=True, color="#ea580c")
    p.append(c_fp)
    
    # 4. TN (True Negative)
    c_tn = fitbox(grid_x0 + cw + 10, grid_y0 + ch + 10, cw, ch,
                  "TN (True Negative)\nІстинно негативні\n\nКоректний спокій\n(передбачено −, дійсно −)",
                  size=12, pad=6, fill="#eef6ff", stroke=NEG, sw=2, bold=True, color=NEG)
    p.append(c_tn)
    
    # Маргінальні похідні праворуч (по рядках: відносно істини)
    rx0 = grid_x0 + 2 * cw + 25
    
    bx_row1 = fitbox(rx0, grid_y0, 380, ch,
                     "Метрики щодо істинних позитивних (P):\n"
                     "• Recall / Sensitivity (TPR) = TP / (TP + FN)\n"
                     "  (частка виявлених цілей серед усіх реальних)\n"
                     "• Miss Rate / FNR = FN / P = 1 − TPR\n"
                     "  (частка критично пропущених дефектів)",
                     size=11, pad=8, fill="#f9fafb", stroke="#9ca3af", color=INK)
    p.append(bx_row1)
    
    bx_row2 = fitbox(rx0, grid_y0 + ch + 10, 380, ch,
                     "Метрики щодо істинних негативних (N):\n"
                     "• Specificity / Selectivity (TNR) = TN / (FP + TN)\n"
                     "  (здатність не давати тривогу на норму)\n"
                     "• Fall-out / FPR = FP / N = 1 − TNR\n"
                     "  (рівень фальшивих спрацювань на шумі)",
                     size=11, pad=8, fill="#f9fafb", stroke="#9ca3af", color=INK)
    p.append(bx_row2)
    
    # Маргінальні похідні знизу (по стовпцях: відносно прогнозу)
    by0 = grid_y0 + 2 * ch + 25
    
    bx_col1 = fitbox(grid_x0, by0, cw, 105,
                     "Точність (PPV):\n"
                     "Precision = TP/(TP+FP)\n\n"
                     "FDR = FP/(TP+FP)\n"
                     "= 1 − Precision",
                     size=11, pad=6, fill="#f9fafb", stroke="#9ca3af", color=INK)
    p.append(bx_col1)
    
    bx_col2 = fitbox(grid_x0 + cw + 10, by0, cw, 105,
                     "Надійність (NPV):\n"
                     "NPV = TN/(TN+FN)\n\n"
                     "FOR = FN/(TN+FN)\n"
                     "= 1 − NPV",
                     size=11, pad=6, fill="#f9fafb", stroke="#9ca3af", color=INK)
    p.append(bx_col2)
    
    # Інтегральні агреговані метрики у правому нижньому куті
    bx_global = fitbox(rx0, by0, 380, 105,
                       "Інтегральні коефіцієнти балансу:\n"
                       "• F₁ = 2·(Prec·Rec)/(Prec+Rec) = 2·TP / (2·TP + FP + FN)\n"
                       "• F_β = (1+β²)·(Prec·Rec)/(β²·Prec + Rec)  [β>1: акцент на Recall]\n"
                       "• MCC = (TP·TN − FP·FN) / √((TP+FP)(TP+FN)(TN+FP)(TN+FN))\n"
                       "• Accuracy = (TP+TN)/(P+N),  Balanced Acc = (TPR + TNR)/2",
                       size=11, pad=8, fill="#eff6ff", stroke=NEG, color=INK, bold=False)
    p.append(bx_global)
    
    # Захисний рендер
    render(os.path.join(OUT, "confusion-matrix-derivatives.svg"), W, H, *p)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2 — Порівняння ROC-кривої та Precision-Recall кривої
# ─────────────────────────────────────────────────────────────────────────────
def fig_roc_vs_pr():
    W, H = 940, 480
    p = []
    
    p.append(text(W / 2, 28, "Порівняння кривих оцінки: ROC-крива проти Precision-Recall (PR)", size=16, color=INK, bold=True))
    
    # Дві панелі графіків: ліва (ROC) і права (PR)
    pw, ph = 340, 260
    lx0, ly0 = 90, 80
    rx0, ry0 = 530, 80
    
    # ── Лівий графік: ROC-крива ──
    # Фон і сітка
    p.append(rect(lx0, ly0, pw, ph, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))
    
    # Горизонтальні та вертикальні лінії сітки (0.25, 0.5, 0.75)
    for frac in [0.25, 0.5, 0.75]:
        gx = lx0 + frac * pw
        gy = ly0 + (1.0 - frac) * ph
        p.append(line(gx, ly0, gx, ly0 + ph, color="#f3f4f6", sw=1.0))
        p.append(line(lx0, gy, lx0 + pw, gy, color="#f3f4f6", sw=1.0))
    
    # Діагональ випадкового класифікатора (AUC = 0.50)
    p.append(line(lx0, ly0 + ph, lx0 + pw, ly0, color="#9ca3af", sw=1.5, dash="5,5"))
    p.append(text(lx0 + pw * 0.58, ly0 + ph * 0.46, "Випадковий (AUC = 0.50)", size=10, color=MUTED, italic=True))
    
    # Крива якісної моделі (AUC = 0.93)
    roc_pts = [
        (0.0, 0.0), (0.04, 0.50), (0.08, 0.72), (0.15, 0.84),
        (0.28, 0.92), (0.45, 0.96), (0.70, 0.98), (1.0, 1.0)
    ]
    poly_roc = []
    for fx, fy in roc_pts:
        sx = lx0 + fx * pw
        sy = ly0 + (1.0 - fy) * ph
        poly_roc.append((sx, sy))
    
    for i in range(len(poly_roc) - 1):
        x1, y1 = poly_roc[i]
        x2, y2 = poly_roc[i+1]
        p.append(line(x1, y1, x2, y2, color=POS, sw=2.5))
    
    # Операційні точки на ROC
    op_pts_roc = [
        (poly_roc[2][0], poly_roc[2][1], "pth=0.8 (суворий)"),
        (poly_roc[4][0], poly_roc[4][1], "pth=0.5 (баланс)"),
        (poly_roc[5][0], poly_roc[5][1], "pth=0.2 (м'який)")
    ]
    for ox, oy, lbl in op_pts_roc:
        p.append(circle(ox, oy, 4.5, fill="#ffffff", stroke=POS, sw=2))
        p.append(text(ox + 8, oy - 6, lbl, size=10, color=POS, bold=True, anchor="start"))
    
    # Підписи осей ROC
    p.append(text(lx0 + pw / 2, ly0 + ph + 34, "FPR (1 − Specificity)  →", size=12, color=INK, bold=True))
    p.append(text(lx0 - 45, ly0 + ph / 2, "TPR (Recall)  ↑", size=12, color=INK, bold=True))
    p.append(text(lx0 - 15, ly0 + ph, "0.0", size=10, color=MUTED))
    p.append(text(lx0 - 15, ly0, "1.0", size=10, color=MUTED))
    p.append(text(lx0, ly0 + ph + 16, "0.0", size=10, color=MUTED))
    p.append(text(lx0 + pw, ly0 + ph + 16, "1.0", size=10, color=MUTED))
    
    p.append(text(lx0 + pw / 2, ly0 - 12, "ROC-простір (ROC-AUC = 0.93)", size=13, color=INK, bold=True))
    
    # ── Правий графік: PR-крива ──
    p.append(rect(rx0, ry0, pw, ph, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))
    
    for frac in [0.25, 0.5, 0.75]:
        gx = rx0 + frac * pw
        gy = ry0 + (1.0 - frac) * ph
        p.append(line(gx, ry0, gx, ry0 + ph, color="#f3f4f6", sw=1.0))
        p.append(line(rx0, gy, rx0 + pw, gy, color="#f3f4f6", sw=1.0))
    
    # Базові лінії випадкового вибору (Prevalence)
    # Збалансована: P/(P+N) = 0.50
    p.append(line(rx0, ry0 + 0.5 * ph, rx0 + pw, ry0 + 0.5 * ph, color="#9ca3af", sw=1.2, dash="4,4"))
    p.append(text(rx0 + pw - 8, ry0 + 0.5 * ph - 5, "База (баланс 1:1, P=0.5)", size=9.5, color=MUTED, anchor="end"))
    
    # Незбалансована: P/(P+N) = 0.05
    p.append(line(rx0, ry0 + 0.95 * ph, rx0 + pw, ry0 + 0.95 * ph, color="#dc2626", sw=1.2, dash="3,3"))
    p.append(text(rx0 + pw - 8, ry0 + 0.95 * ph - 5, "База (дисбаланс 1:20, P=0.05)", size=9.5, color="#dc2626", anchor="end"))
    
    # PR-крива для збалансованого датасету
    pr_pts_bal = [
        (0.0, 0.98), (0.20, 0.95), (0.45, 0.92), (0.70, 0.85),
        (0.85, 0.74), (0.94, 0.58), (1.0, 0.50)
    ]
    poly_pr_bal = []
    for fx, fy in pr_pts_bal:
        sx = rx0 + fx * pw
        sy = ry0 + (1.0 - fy) * ph
        poly_pr_bal.append((sx, sy))
    
    for i in range(len(poly_pr_bal) - 1):
        x1, y1 = poly_pr_bal[i]
        x2, y2 = poly_pr_bal[i+1]
        p.append(line(x1, y1, x2, y2, color=FIELD, sw=2.2))
        
    # PR-крива тієї самої моделі при сильному дисбалансі (1:20)
    pr_pts_imb = [
        (0.0, 0.92), (0.15, 0.82), (0.35, 0.65), (0.55, 0.42),
        (0.75, 0.22), (0.90, 0.11), (1.0, 0.05)
    ]
    poly_pr_imb = []
    for fx, fy in pr_pts_imb:
        sx = rx0 + fx * pw
        sy = ry0 + (1.0 - fy) * ph
        poly_pr_imb.append((sx, sy))
    
    for i in range(len(poly_pr_imb) - 1):
        x1, y1 = poly_pr_imb[i]
        x2, y2 = poly_pr_imb[i+1]
        p.append(line(x1, y1, x2, y2, color=NEG, sw=2.5))
        
    p.append(text(rx0 + pw * 0.42, ry0 + ph * 0.16, "PR-крива (баланс 1:1, PR-AUC=0.88)", size=10, color=FIELD, bold=True))
    p.append(text(rx0 + pw * 0.42, ry0 + ph * 0.58, "PR-крива (дисбаланс 1:20, PR-AUC=0.41)", size=10, color=NEG, bold=True))
    
    # Підписи осей PR
    p.append(text(rx0 + pw / 2, ry0 + ph + 34, "Recall (TPR)  →", size=12, color=INK, bold=True))
    p.append(text(rx0 - 45, ry0 + ph / 2, "Precision (PPV)  ↑", size=12, color=INK, bold=True))
    p.append(text(rx0 - 15, ry0 + ph, "0.0", size=10, color=MUTED))
    p.append(text(rx0 - 15, ly0, "1.0", size=10, color=MUTED))
    p.append(text(rx0, ry0 + ph + 16, "0.0", size=10, color=MUTED))
    p.append(text(rx0 + pw, ry0 + ph + 16, "1.0", size=10, color=MUTED))
    
    p.append(text(rx0 + pw / 2, ry0 - 12, "PR-простір (Precision-Recall)", size=13, color=INK, bold=True))
    
    # Пояснювальні картки знизу
    bx_note1 = fitbox(lx0, ly0 + ph + 50, pw, 75,
                      "Інваріантність ROC до балансу класів:\n"
                      "TPR і FPR рахуються суто у своїх класах (по рядках).\n"
                      "Крива ROC не змінюється при додаванні TN,\n"
                      "що може маскувати падіння точності при 1:100.",
                      size=10.5, pad=6, fill="#f9fafb", stroke="#d1d5db", color=INK)
    p.append(bx_note1)
    
    bx_note2 = fitbox(rx0, ly0 + ph + 50, pw, 75,
                      "Чутливість PR до рідкісних подій:\n"
                      "Precision ділить TP на (TP + FP). Якщо N ≫ P,\n"
                      "навіть крихітний FPR створює лавину FP,\n"
                      "і Precision катастрофічно обвалюється.",
                      size=10.5, pad=6, fill="#f9fafb", stroke="#d1d5db", color=INK)
    p.append(bx_note2)
    
    render(os.path.join(OUT, "roc-vs-pr-curves.svg"), W, H, *p)

if __name__ == "__main__":
    fig_confusion_matrix()
    fig_roc_vs_pr()
    print("Figures generated successfully in", OUT)
