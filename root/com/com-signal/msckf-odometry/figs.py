# -*- coding: utf-8 -*-
import sys, os

# 4 levels up to reach scripts/ from book/algorithms/signal-robotics/msckf-odometry
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Порівняння структури стану: EKF-SLAM vs MSCKF ────────────────────────
def fig_state_structure():
    W, H = 840, 420
    frags = []
    frags.append(text(W/2, 28, "Структура вектора стану: класичний EKF-SLAM проти MSCKF", size=16, bold=True))

    colW = 360
    x1 = 40
    x2 = W - 40 - colW
    yTop = 60

    # Ліва колонка: EKF-SLAM
    frags.append(fitbox(x1, yTop, colW, 40, "Класичний EKF-SLAM (стан росте з картою)",
                        size=14, bold=True, fill="#fdecea", stroke=POS))
    
    y = yTop + 50
    frags.append(fitbox(x1, y, colW, 36, "Поточний стан IMU (поза, швидкість, зсуви: 15)",
                        size=12, fill="#f4f6f8", stroke=LINE))
    y += 42
    frags.append(fitbox(x1, y, colW, 36, "3D-орієнтир #1 (X₁, Y₁, Z₁)", size=12, fill="#eaf0fd", stroke=NEG))
    y += 40
    frags.append(fitbox(x1, y, colW, 36, "3D-орієнтир #2 (X₂, Y₂, Z₂)", size=12, fill="#eaf0fd", stroke=NEG))
    y += 40
    frags.append(fitbox(x1, y, colW, 36, "... сотні 3D-орієнтирів (M × 3) ...", size=12, fill="#eaf0fd", stroke=NEG, sw=1.2))
    y += 46
    frags.append(fitbox(x1, y, colW, 46, "Розмір стану: 15 + 3M\nКоваріація P: (15+3M) × (15+3M)  →  O(M³) обчислень",
                        size=11, bold=True, fill="#fdecea", stroke=POS))

    # Права колонка: MSCKF
    frags.append(fitbox(x2, yTop, colW, 40, "MSCKF (стан не залежить від кількості точок)",
                        size=14, bold=True, fill="#eafaf1", stroke=FIELD))
    
    y = yTop + 50
    frags.append(fitbox(x2, y, colW, 36, "Поточний стан IMU (поза, швидкість, зсуви: 15)",
                        size=12, fill="#f4f6f8", stroke=LINE))
    y += 42
    frags.append(fitbox(x2, y, colW, 36, "Клонована поза камери t[k-N+1] (p, q: 6)", size=12, fill="#eafaf1", stroke=FIELD))
    y += 40
    frags.append(fitbox(x2, y, colW, 36, "Клонована поза камери t[k-1] (p, q: 6)", size=12, fill="#eafaf1", stroke=FIELD))
    y += 40
    frags.append(fitbox(x2, y, colW, 36, "Клонована поза камери t[k] (p, q: 6)", size=12, fill="#eafaf1", stroke=FIELD))
    y += 46
    frags.append(fitbox(x2, y, colW, 46, "Розмір стану: 15 + 6N  (сталий, N ~ 10...30)\nОрієнтири усуваються проєкцією  →  O(N³) обчислень",
                        size=11, bold=True, fill="#eafaf1", stroke=FIELD))

    # Підсумковий напис внизу
    frags.append(text(W/2, H - 18,
                      "В EKF-SLAM складність росте від кількості точок світу; в MSCKF — фіксована вікном поз камери.",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "msckf-state-structure.svg"), W, H, *frags)


# ── 2. Геометрія обмеження: багато поз спостерігають одну точку ───────────────
def fig_multi_camera_constraint():
    W, H = 800, 380
    frags = []
    frags.append(text(W/2, 28, "Геометричне обмеження між позами камери через спільний орієнтир", size=16, bold=True))

    # 3D орієнтир угорі
    fx, fy = W/2, 90
    frags.append(circle(fx, fy, 8, fill="#c0392b", stroke=POS, sw=2))
    frags.append(text(fx, fy - 16, "Нерухомий 3D-орієнтир f", size=13, color=POS, bold=True))

    # 3 пози камери внизу
    c_poses = [
        (160, 270, "Поза C₁ (t₁)"),
        (400, 290, "Поза C₂ (t₂)"),
        (640, 260, "Поза C₃ (t₃)")
    ]

    # Траєкторія руху
    frags.append(line(160, 270, 400, 290, color=MUTED, sw=2, dash="4 4"))
    frags.append(line(400, 290, 640, 260, color=MUTED, sw=2, dash="4 4"))
    frags.append(text(280, 295, "траєкторія руху", size=11, color=MUTED, italic=True))

    # Промені спостереження
    for cx, cy, label in c_poses:
        # Камера як прямокутник
        frags.append(rect(cx - 35, cy - 20, 70, 40, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
        frags.append(text(cx, cy + 5, label, size=12, color=NEG, bold=True))
        # Промінь до точки
        frags.append(line(cx, cy - 20, fx, fy + 8, color=LINE, sw=1.5))
        # Вектор спостереження z_i
        mid_x = (cx + fx) / 2
        mid_y = (cy - 20 + fy + 8) / 2
        frags.append(circle(mid_x, mid_y, 3, fill=INK, stroke=INK))

    frags.append(text(240, 160, "промінь z₁", size=11, color=INK))
    frags.append(text(430, 175, "промінь z₂", size=11, color=INK))
    frags.append(text(550, 155, "промінь z₃", size=11, color=INK))

    # Пояснення знизу
    frags.append(textbox(W/2, H - 35,
                         "Всі 3 промені зобов'язані перетнутися в одній точці. "
                         "Це створює жорсткий зв'язок між C₁, C₂ та C₃ без збереження f у фільтрі.",
                         size=12, fill="#f4f6f8", stroke=LINE)[0])

    render(os.path.join(IMG, "msckf-multi-camera-constraint.svg"), W, H, *frags)


# ── 3. Проєкція в нуль-простір (Null-Space Projection) ────────────────────────
def fig_nullspace_projection():
    W, H = 840, 400
    frags = []
    frags.append(text(W/2, 28, "Усунення невідомої 3D-точки проєкцією на лівий нуль-простір", size=16, bold=True))

    # Блок вихідного рівняння
    y1 = 65
    frags.append(fitbox(60, y1, 720, 55,
                        "Вихідна лінеаризована нев'язка спостережень:\n"
                        "r_j = H_X · x̃ + H_f · f̃ + v   (де f̃ — похибка координат 3D-точки, що заважає)",
                        size=13, bold=False, fill="#fdecea", stroke=POS))

    # Стрілка вниз
    frags.append(arrow(W/2, y1 + 55, W/2, y1 + 95, color=LINE, sw=2))
    frags.append(text(W/2 + 15, y1 + 78, "Множення зліва на базисну матрицю Aᵀ (Aᵀ · H_f = 0)",
                      size=12, color=INK, anchor="start", bold=True))

    # Блок QR розкладу
    y2 = y1 + 95
    frags.append(fitbox(60, y2, 720, 65,
                        "QR-розклад матриці чутливості до орієнтира:\n"
                        "H_f = [Q₁  Q₂] · [ R ;  0 ]   →   Обираємо матрицю A = Q₂  (лівий нуль-простір)\n"
                        "Властивість: Q₂ᵀ · H_f = 0  (стовпці Q₂ ортогональні стовпцям H_f)",
                        size=12, fill="#eaf0fd", stroke=NEG))

    # Стрілка вниз
    frags.append(arrow(W/2, y2 + 65, W/2, y2 + 105, color=LINE, sw=2))
    frags.append(text(W/2 + 15, y2 + 88, "Проєкція: r_o = Aᵀ · r_j", size=12, color=INK, anchor="start", bold=True))

    # Блок результуючого рівняння
    y3 = y2 + 105
    frags.append(fitbox(60, y3, 720, 55,
                        "Спроєктована нев'язка для кроку корекції фільтра Калмана:\n"
                        "r_o = Aᵀ · H_X · x̃ + Aᵀ · v = H_o · x̃ + v_o   (доданок з f̃ зник абсолютно точно!)",
                        size=13, bold=True, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG, "msckf-nullspace-projection.svg"), W, H, *frags)


# ── 4. Загальний конвеєр роботи MSCKF ────────────────────────────────────────
def fig_pipeline_flow():
    W, H = 840, 430
    frags = []
    frags.append(text(W/2, 26, "Повний робочий конвеєр алгоритму MSCKF", size=16, bold=True))

    boxW = 165
    boxH = 75
    yTop = 65

    # Етап 1: IMU Інтегрування
    x1 = 30
    frags.append(fitbox(x1, yTop, boxW, boxH,
                        "1. Швидке IMU (~500 Гц)\nІнтегрування показів,\nпророкування стану,\nнакопичення коваріації",
                        size=11, fill="#fdecea", stroke=POS))

    # Стрілка
    frags.append(arrow(x1 + boxW, yTop + boxH/2, x1 + boxW + 25, yTop + boxH/2, color=LINE, sw=1.5))

    # Етап 2: Прихід кадру / Клонування
    x2 = x1 + boxW + 25
    frags.append(fitbox(x2, yTop, boxW, boxH,
                        "2. Новий кадр (~30 Гц)\nКлонування стану поз:\nдодавання поточної пози\nкамери до ковзного вікна",
                        size=11, fill="#eaf0fd", stroke=NEG))

    # Стрілка
    frags.append(arrow(x2 + boxW, yTop + boxH/2, x2 + boxW + 25, yTop + boxH/2, color=LINE, sw=1.5))

    # Етап 3: Трекінг та Тріангуляція
    x3 = x2 + boxW + 25
    frags.append(fitbox(x3, yTop, boxW, boxH,
                        "3. Оптичний потік\nВідстеження точок.\nДля втрачених треків:\n3D-тріангуляція орієнтира",
                        size=11, fill="#f4f6f8", stroke=LINE))

    # Стрілка
    frags.append(arrow(x3 + boxW, yTop + boxH/2, x3 + boxW + 25, yTop + boxH/2, color=LINE, sw=1.5))

    # Етап 4: Нуль-простір
    x4 = x3 + boxW + 25
    frags.append(fitbox(x4, yTop, boxW, boxH,
                        "4. Проєкція усунення\nОбчислення H_X, H_f.\nQR-розклад H_f.\nПроєкція r_o = Q₂ᵀ · r",
                        size=11, fill="#eafaf1", stroke=FIELD))

    # Стрілка вниз від 4 до 5
    yBot = yTop + boxH + 60
    frags.append(line(x4 + boxW/2, yTop + boxH, x4 + boxW/2, yBot - 20, color=LINE, sw=1.5))
    frags.append(arrow(x4 + boxW/2, yBot - 20, x3 + boxW/2, yBot - 20, color=LINE, sw=1.5))

    # Етап 5: EKF Корекція
    x5 = (W - 460) / 2
    frags.append(fitbox(x5, yBot - 45, 215, 80,
                        "5. Корекція фільтра Калмана\nРозрахунок підсилення K,\nоновлення похибок поз та IMU,\nкорекція зсувів гіро/аксель",
                        size=11, bold=True, fill="#eafaf1", stroke=FIELD))

    # Стрілка від 5 до 6
    x6 = x5 + 245
    frags.append(arrow(x5 + 215, yBot - 5, x6, yBot - 5, color=LINE, sw=1.5))

    # Етап 6: Маргіналізація
    frags.append(fitbox(x6, yBot - 45, 215, 80,
                        "6. Маргіналізація вікна\nВидалення найстарішої\nабо надлишкової пози\nз вектора стану і матриці P",
                        size=11, fill="#fdecea", stroke=POS))

    # Петля повернення до кроку 1
    frags.append(line(x6 + 107, yBot + 35, x6 + 107, H - 35, color=MUTED, sw=1.5, dash="4 3"))
    frags.append(line(x6 + 107, H - 35, x1 + boxW/2, H - 35, color=MUTED, sw=1.5, dash="4 3"))
    frags.append(arrow(x1 + boxW/2, H - 35, x1 + boxW/2, yTop + boxH, color=MUTED, sw=1.5))
    frags.append(text(W/2, H - 42, "Оновлений стан повертається для наступних кроків інтегрування IMU",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "msckf-pipeline-flow.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_state_structure()
    fig_multi_camera_constraint()
    fig_nullspace_projection()
    fig_pipeline_flow()
    print("MSCKF figures generated successfully.")
