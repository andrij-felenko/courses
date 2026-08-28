# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра кольорів
AMBER   = "#caa24a"
AMBERBG = "#fff9ec"
AMBERTX = "#7c5c0a"
GREENBG = "#eef8f0"
BLUEBG  = "#eaf2fd"
REDBG   = "#fdeeed"
GRAYBG  = "#f4f6f8"

def fig_pipeline():
    """Діаграма 1: Архітектура конвеєра CI/CD регресійного тестування автопілота в SITL."""
    W, H = 860, 440
    p = []
    
    # 1. Тригер / Репозиторій
    b1_x, b1_y, b1_w, b1_h = 30, 60, 160, 100
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill=BLUEBG, stroke=NEG, sw=2, rx=8))
    p.append(text(b1_x + b1_w/2, b1_y + 26, "КОМІТ / PULL REQUEST", size=11, color=NEG, bold=True))
    p.append(text(b1_x + b1_w/2, b1_y + 48, "зміна коду / тюнінг", size=10, color=INK))
    p.append(text(b1_x + b1_w/2, b1_y + 68, "PID, EKF, навігація", size=9.5, color=MUTED))
    p.append(text(b1_x + b1_w/2, b1_y + 86, "тригер CI/CD runner", size=9.5, color=NEG))
    
    # Стрілка 1 -> 2
    p.append(arrow(b1_x + b1_w, b1_y + b1_h/2, 230, b1_y + b1_h/2, color=LINE, sw=2))
    
    # 2. Матриця симуляцій SITL
    b2_x, b2_y, b2_w, b2_h = 230, 45, 230, 130
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill=GREENBG, stroke=FIELD, sw=2.2, rx=8))
    p.append(text(b2_x + b2_w/2, b2_y + 24, "МАТРИЦЯ СЦЕНАРІЇВ SITL", size=11.5, color=FIELD, bold=True))
    p.append(text(b2_x + b2_w/2, b2_y + 48, "Lockstep-час (dt=4 мс)", size=10, color=INK))
    p.append(text(b2_x + b2_w/2, b2_y + 70, "Прискорення: 20x реального", size=9.5, color=INK))
    p.append(text(b2_x + b2_w/2, b2_y + 92, "Сценарій 1: Штиль (номінал)", size=9.5, color=MUTED))
    p.append(text(b2_x + b2_w/2, b2_y + 110, "Сценарій 2: Вітер + пориви 12 м/с", size=9.5, color=MUTED))
    
    # Стрілка 2 -> 3
    p.append(arrow(b2_x + b2_w, b2_y + b2_h/2, 500, b2_y + b2_h/2, color=LINE, sw=2))
    
    # 3. Витяг і обробка логів
    b3_x, b3_y, b3_w, b3_h = 500, 50, 160, 120
    p.append(rect(b3_x, b3_y, b3_w, b3_h, fill=AMBERBG, stroke=AMBER, sw=2, rx=8))
    p.append(text(b3_x + b3_w/2, b3_y + 24, "ЕКСТРАКТОР ЛОГІВ", size=11, color=AMBERTX, bold=True))
    p.append(text(b3_x + b3_w/2, b3_y + 46, "ULog / DataFlash / CSV", size=10, color=INK))
    p.append(text(b3_x + b3_w/2, b3_y + 68, "vehicle_local_position", size=9.5, color=MUTED))
    p.append(text(b3_x + b3_w/2, b3_y + 88, "battery_status, actuators", size=9.5, color=MUTED))
    p.append(text(b3_x + b3_w/2, b3_y + 106, "інтерполяція кроку dt", size=9.5, color=AMBERTX))
    
    # Стрілка 3 -> 4
    p.append(arrow(b3_x + b3_w, b3_y + b3_h/2, 700, b3_y + b3_h/2, color=LINE, sw=2))
    
    # 4. База еталонів (Golden Baselines)
    b4_x, b4_y, b4_w, b4_h = 700, 60, 135, 100
    p.append(rect(b4_x, b4_y, b4_w, b4_h, fill=GRAYBG, stroke=LINE, sw=1.8, rx=8))
    p.append(text(b4_x + b4_w/2, b4_y + 24, "ЕТАЛОН (GOLDEN)", size=10.5, color=INK, bold=True))
    p.append(text(b4_x + b4_w/2, b4_y + 48, "Базовий маршрут", size=9.5, color=INK))
    p.append(text(b4_x + b4_w/2, b4_y + 70, "Ансамбль 10 прогонів", size=9.5, color=MUTED))
    p.append(text(b4_x + b4_w/2, b4_y + 88, "Довірчий інтервал 3σ", size=9.5, color=MUTED))

    # Стрілки вниз до раннера метрик
    p.append(arrow(b3_x + b3_w/2, b3_y + b3_h, b3_x + b3_w/2, 220, color=AMBER, sw=2))
    p.append(text(b3_x + b3_w/2 - 50, 195, "тестовий трек", size=9.5, color=AMBERTX))
    
    p.append("<path d=\"M %d %d L %d %d L %d %d\" fill=\"none\" stroke=\"%s\" stroke-width=\"2\" marker-end=\"url(#arrow)\"/>" % 
             (b4_x + b4_w/2, b4_y + b4_h, b4_x + b4_w/2, 205, 590, 240, LINE))
    p.append(text(b4_x + b4_w/2, 195, "еталонний трек", size=9.5, color=MUTED))

    # 5. Двигун розрахунку метрик регресії
    b5_x, b5_y, b5_w, b5_h = 160, 220, 430, 145
    p.append(rect(b5_x, b5_y, b5_w, b5_h, fill=FILL, stroke=LINE, sw=2.2, rx=10))
    p.append(text(b5_x + b5_w/2, b5_y + 24, "МОДУЛЬ ПОРІВНЯННЯ ТРАЄКТОРІЙ (REGRESSION RUNNER)", size=12, color=INK, bold=True))
    
    # Підблоки всередині раннера
    p.append(rect(b5_x + 15, b5_y + 38, 125, 92, fill=BG, stroke=FIELD, sw=1.4, rx=6))
    p.append(text(b5_x + 77, b5_y + 56, "Cross-Track (XTE)", size=9.5, color=FIELD, bold=True))
    p.append(text(b5_x + 77, b5_y + 74, "RMS / 95% / Max", size=9.5, color=INK))
    p.append(text(b5_x + 77, b5_y + 94, "Коридор відхилення", size=9.5, color=MUTED))
    p.append(text(b5_x + 77, b5_y + 112, "Зрізання кутів", size=9.5, color=MUTED))

    p.append(rect(b5_x + 152, b5_y + 38, 125, 92, fill=BG, stroke=AMBER, sw=1.4, rx=6))
    p.append(text(b5_x + 214, b5_y + 56, "Фреше та DTW", size=9.5, color=AMBERTX, bold=True))
    p.append(text(b5_x + 214, b5_y + 74, "Відстань повідка δ_dF", size=9.5, color=INK))
    p.append(text(b5_x + 214, b5_y + 94, "Викривлення часу DTW", size=9.5, color=MUTED))
    p.append(text(b5_x + 214, b5_y + 112, "Зсув фази маневру", size=9.5, color=MUTED))

    p.append(rect(b5_x + 289, b5_y + 38, 125, 92, fill=BG, stroke=NEG, sw=1.4, rx=6))
    p.append(text(b5_x + 351, b5_y + 56, "Енергія та час", size=9.5, color=NEG, bold=True))
    p.append(text(b5_x + 351, b5_y + 74, "ΔE = ∫ U·I dt (Дж)", size=9.5, color=INK))
    p.append(text(b5_x + 351, b5_y + 94, "Час між точками Δt", size=9.5, color=MUTED))
    p.append(text(b5_x + 351, b5_y + 112, "Насичення моторів", size=9.5, color=MUTED))

    # Стрілка з раннера до вердикту
    p.append(arrow(b5_x + b5_w, b5_y + b5_h/2, 650, b5_y + b5_h/2, color=LINE, sw=2.2))
    
    # 6. Вердикт та звіт CI
    b6_x, b6_y, b6_w, b6_h = 650, 225, 175, 135
    p.append(rect(b6_x, b6_y, b6_w, b6_h, fill=BG, stroke=LINE, sw=2, rx=8))
    p.append(text(b6_x + b6_w/2, b6_y + 24, "ГЕЙТ ВЕРДИКТУ CI", size=11.5, color=INK, bold=True))
    
    # Зелена плашка PASS
    p.append(rect(b6_x + 12, b6_y + 38, 70, 42, fill=GREENBG, stroke=FIELD, sw=1.5, rx=5))
    p.append(text(b6_x + 47, b6_y + 56, "PASS", size=10.5, color=FIELD, bold=True))
    p.append(text(b6_x + 47, b6_y + 72, "Злиття OK", size=9.5, color=FIELD))
    
    # Червона плашка FAIL
    p.append(rect(b6_x + 92, b6_y + 38, 70, 42, fill=REDBG, stroke=POS, sw=1.5, rx=5))
    p.append(text(b6_x + 127, b6_y + 56, "FAIL", size=10.5, color=POS, bold=True))
    p.append(text(b6_x + 127, b6_y + 72, "Регресія", size=9.5, color=POS))
    
    p.append(text(b6_x + b6_w/2, b6_y + 98, "JUnit XML + JSON звіт", size=9.5, color=INK))
    p.append(text(b6_x + b6_w/2, b6_y + 118, "3D-накладання траєкторій", size=9.5, color=MUTED))

    # Нижній висновок
    p.append(text(W/2, H - 18, "Автоматизований цикл: кожна зміна коду перевіряється на збереження геометрії польоту", size=11, color=MUTED))

    render(os.path.join(OUT, "pipeline.svg"), W, H, *p)

def fig_trajectory_metrics():
    """Діаграма 2: Геометричне зіставлення траєкторій: Cross-Track Error, відстань Фреше та DTW."""
    W, H = 860, 450
    p = []

    # Ліва колонка: Геометрія у просторі (Плановий сегмент, Еталон Q, Тестовий трек P)
    p.append(rect(30, 40, 380, 350, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(220, 65, "ПРОСТОРОВЕ ЗІСТАВЛЕННЯ ТРАЄКТОРІЙ", size=12, color=INK, bold=True))

    # Точки маршруту Waypoints
    wp1_x, wp1_y = 70, 320
    wp2_x, wp2_y = 190, 140
    wp3_x, wp3_y = 360, 110

    # Плановий маршрут (пунктир)
    p.append("<polyline points=\"%d,%d %d,%d %d,%d\" fill=\"none\" stroke=\"%s\" stroke-width=\"1.8\" stroke-dasharray=\"6 4\"/>" %
             (wp1_x, wp1_y, wp2_x, wp2_y, wp3_x, wp3_y, MUTED))
    p.append(circle(wp1_x, wp1_y, 4, fill=MUTED, stroke=LINE, sw=1.5))
    p.append(circle(wp2_x, wp2_y, 4, fill=MUTED, stroke=LINE, sw=1.5))
    p.append(circle(wp3_x, wp3_y, 4, fill=MUTED, stroke=LINE, sw=1.5))
    p.append(text(wp1_x - 10, wp1_y + 16, "WP1", size=10, color=MUTED, bold=True))
    p.append(text(wp2_x, wp2_y - 12, "WP2 (Поворот)", size=10, color=MUTED, bold=True))
    p.append(text(wp3_x + 10, wp3_y + 16, "WP3", size=10, color=MUTED, bold=True))

    # Еталонна траєкторія Q (Синя плавна лінія)
    p.append("<path d=\"M 70 320 Q 170 180 210 145 T 360 110\" fill=\"none\" stroke=\"%s\" stroke-width=\"3\"/>" % NEG)
    p.append(text(105, 190, "Еталон Q (Golden)", size=10, color=NEG, bold=True))

    # Тестова траєкторія P з регресією (Червона лінія з перельотом і коливанням)
    p.append("<path d=\"M 70 320 Q 185 140 240 100 T 290 135 T 360 110\" fill=\"none\" stroke=\"%s\" stroke-width=\"2.5\"/>" % POS)
    p.append(text(285, 85, "Тест P (Регресія)", size=10, color=POS, bold=True))

    # Cross-Track Error (ортогональ до сегмента)
    p.append(line(130, 230, 152, 245, color=FIELD, sw=2, dash="3 3"))
    p.append(circle(152, 245, 3, fill=FIELD, stroke=LINE, sw=1))
    p.append(text(165, 265, "XTE (e_ct)", size=10, color=FIELD, bold=True))

    # Відстань Фреше (максимальний повідок)
    frechet_p_x, frechet_p_y = 238, 102
    frechet_q_x, frechet_q_y = 205, 147
    p.append(line(frechet_p_x, frechet_p_y, frechet_q_x, frechet_q_y, color=POS, sw=2.2))
    p.append(circle(frechet_p_x, frechet_p_y, 4, fill=POS, stroke=LINE, sw=1.5))
    p.append(circle(frechet_q_x, frechet_q_y, 4, fill=NEG, stroke=LINE, sw=1.5))
    p.append(text(300, 118, "Повідок Фреше δ_dF", size=9.5, color=POS, bold=True))
    p.append(text(300, 134, "(найгірший розрив)", size=9.5, color=MUTED))

    # Дзвін після повороту
    p.append(line(290, 135, 275, 120, color=AMBER, sw=1.8, dash="2 2"))
    p.append(text(320, 160, "Дзвін (Ringing)", size=9.5, color=AMBERTX, bold=True))

    # Легенда зліва внизу
    p.append(rect(45, 335, 350, 42, fill=BG, stroke=LINE, sw=1, rx=5))
    p.append(line(55, 356, 80, 356, color=NEG, sw=2.5))
    p.append(text(125, 360, "Еталонний політ", size=9.5, color=INK))
    p.append(line(175, 356, 200, 356, color=POS, sw=2.5))
    p.append(text(250, 360, "Політ після зміни коду", size=9.5, color=INK))

    # Права колонка: Матриця нелінійного зіставлення часу DTW
    dtw_x, dtw_y, dtw_w, dtw_h = 440, 40, 390, 350
    p.append(rect(dtw_x, dtw_y, dtw_w, dtw_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    p.append(text(dtw_x + dtw_w/2, dtw_y + 25, "ДИНАМІЧНЕ ВИКРИВЛЕННЯ ЧАСУ (DTW)", size=12, color=INK, bold=True))

    # Сітка матриці накопиченої вартості (Cost Matrix)
    grid_ox, grid_oy = dtw_x + 55, dtw_y + 60
    gw, gh = 230, 200
    p.append(rect(grid_ox, grid_oy, gw, gh, fill=FILL, stroke=LINE, sw=1.2, rx=4))

    # Лінії сітки
    for i in range(1, 6):
        gx = grid_ox + i * (gw / 6)
        gy = grid_oy + i * (gh / 6)
        p.append(line(gx, grid_oy, gx, grid_oy + gh, color="#e0e4e8", sw=1))
        p.append(line(grid_ox, gy, grid_ox + gw, gy, color="#e0e4e8", sw=1))

    # Смуга Сакое-Чіба (Sakoe-Chiba band)
    p.append("<polygon points=\"%d,%d %d,%d %d,%d %d,%d\" fill=\"#eaf4ff\" opacity=\"0.6\"/>" %
             (grid_ox, grid_oy + gh, grid_ox, grid_oy + gh - 60, grid_ox + gw - 60, grid_oy, grid_ox + gw, grid_oy))
    p.append(text(grid_ox + 120, grid_oy + 40, "Коридор Сакое-Чіба |i-j| ≤ R", size=9.5, color=NEG))

    # Оптимальний шлях викривлення
    path_pts = [
        (grid_ox + 5, grid_oy + gh - 5),
        (grid_ox + 35, grid_oy + gh - 30),
        (grid_ox + 55, grid_oy + gh - 60),
        (grid_ox + 90, grid_oy + gh - 75),
        (grid_ox + 130, grid_oy + gh - 120),
        (grid_ox + 175, grid_oy + gh - 150),
        (grid_ox + 225, grid_oy + 5)
    ]
    path_str = " ".join("%d,%d" % (x, y) for x, y in path_pts)
    p.append("<polyline points=\"%s\" fill=\"none\" stroke=\"%s\" stroke-width=\"3\"/>" % (path_str, POS))

    for x, y in path_pts:
        p.append(circle(x, y, 3.5, fill=POS, stroke=LINE, sw=1))

    # Підписи осей матриці
    p.append(text(grid_ox + gw/2, grid_oy + gh + 22, "Часовий індекс тестового треку P [i]", size=10, color=INK, bold=True))
    p.append(text(grid_ox - 22, grid_oy + gh/2, "Еталон Q [j]", size=10, color=INK, bold=True))

    # Пояснення праворуч від матриці / внизу
    p.append(rect(dtw_x + 20, dtw_y + 280, 350, 50, fill=AMBERBG, stroke=AMBER, sw=1.2, rx=6))
    p.append(text(dtw_x + 195, dtw_y + 298, "Горизонтальні ділянки шляху:", size=9.5, color=AMBERTX, bold=True))
    p.append(text(dtw_x + 195, dtw_y + 316, "Дрон гальмує або витрачає більше часу на проходження кута", size=9.5, color=INK))

    # Загальний підпис
    p.append(text(W/2, H - 18, "Геометричний та часовий аналіз: Фреше ловить розрив форми, DTW — неузгодженість темпу руху", size=10.5, color=MUTED))

    render(os.path.join(OUT, "trajectory-metrics.svg"), W, H, *p)

if __name__ == "__main__":
    fig_pipeline()
    fig_trajectory_metrics()
    print("All figures generated successfully.")
