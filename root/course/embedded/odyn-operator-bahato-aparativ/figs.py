# -*- coding: utf-8 -*-
"""Фігури для статті odyn-operator-bahato-aparativ («Один оператор, багато апаратів: межа уваги»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. human-attention-capacity: Завантаження уваги W vs кількість БПЛА N ─────
def fig_human_attention_capacity():
    W, H = 820, 480
    ox, oy = 80, 410           # початок координат
    gw, gh = 680, 340          # ширина і висота сітки графіку
    p = []

    # Сітка та осі
    p.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#e1e4e8", sw=1.0, rx=0))
    p.append(arrow(ox, oy, ox + gw + 25, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - gh - 25, color=INK, sw=1.8))
    p.append(text(ox + gw + 20, oy + 28, "Кількість апаратів N", size=13, color=INK, bold=True, anchor="end"))
    p.append(text(ox - 10, oy - gh - 15, "Завантаження уваги W (%)", size=13, color=INK, bold=True, anchor="start"))

    # Позначки осі X (N = 0, 5, 10, 15, 20, 25, 30)
    for n in range(0, 31, 5):
        gx = ox + (n / 30.0) * gw
        p.append(line(gx, oy, gx, oy + 6, color=INK, sw=1.2))
        p.append(text(gx, oy + 20, str(n), size=12, color=INK, anchor="middle"))
        if n > 0:
            p.append(line(gx, oy - gh, gx, oy, color="#edf0f2", sw=1.0, dash="3 3"))

    # Позначки осі Y (W = 0, 50, 70, 100, 150, 200)
    y_levels = [(0, 0), (50, 50), (70, 70), (100, 100), (150, 150), (200, 200)]
    max_w_val = 220.0
    for w_val, label_val in y_levels:
        gy = oy - (w_val / max_w_val) * gh
        p.append(line(ox - 6, gy, ox, gy, color=INK, sw=1.2))
        p.append(text(ox - 10, gy + 4, str(label_val) + "%", size=11, color=INK, anchor="end"))

    # Червона зона та порогові лінії
    y70 = oy - (70.0 / max_w_val) * gh
    y100 = oy - (100.0 / max_w_val) * gh

    p.append(rect(ox, oy - gh, gw, y70 - (oy - gh), fill="#fff5f5", stroke="none", rx=0))
    p.append(line(ox, y70, ox + gw, y70, color="#d97706", sw=1.5, dash="6 4"))
    p.append(text(ox + gw - 8, y70 - 7, "Порогове навантаження (70%): деградація уваги", size=11, color="#d97706", anchor="end", bold=True))

    p.append(line(ox, y100, ox + gw, y100, color=POS, sw=1.8, dash="8 4"))
    p.append(text(ox + gw - 8, y100 - 7, "Критична межа (100%): неминучий зрив черги подій", size=11, color=POS, anchor="end", bold=True))

    # Крива 1: Ручне пілотування W = N * 180% (швидкий зліт)
    pts1 = []
    for i in range(0, 15):
        n_val = i * 0.1
        w_val = n_val * 180.0
        if w_val > max_w_val:
            break
        gx = ox + (n_val / 30.0) * gw
        gy = oy - (w_val / max_w_val) * gh
        pts1.append("%.1f,%.1f" % (gx, gy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" stroke-linecap="round"/>' % (" ".join(pts1), POS))

    # Крива 2: Нагляд за траєкторією (Supervisory control) W = N * 22% + 5%
    pts2 = []
    for i in range(0, 110):
        n_val = i * 0.1
        w_val = n_val * 22.0 + 5.0
        if w_val > max_w_val:
            break
        gx = ox + (n_val / 30.0) * gw
        gy = oy - (w_val / max_w_val) * gh
        pts2.append("%.1f,%.1f" % (gx, gy))
    p.append('<polyline points="%s" fill="none" stroke="#2563eb" stroke-width="2.8" stroke-linecap="round"/>' % (" ".join(pts2),))

    # Крива 3: Керування за винятком (Management by Exception) W = 8% + N * 1.5% + N^0.7 * 2.5%
    pts3 = []
    for i in range(0, 301):
        n_val = i * 0.1
        w_val = 8.0 + n_val * 1.5 + (n_val ** 0.7) * 2.5
        gx = ox + (n_val / 30.0) * gw
        gy = oy - (w_val / max_w_val) * gh
        pts3.append("%.1f,%.1f" % (gx, gy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0" stroke-linecap="round"/>' % (" ".join(pts3), FIELD))

    # Пояснювальні плашки збоку
    b1, _, _ = textbox(ox + 105, oy - 290, "Ручне пілотування\nN_max = 1 (жорсткий бар'єр)", size=11, color=POS, bold=True, fill="#fdf2f2", stroke=POS, sw=1.2)
    p.append(b1)

    b2, _, _ = textbox(ox + 230, oy - 190, "Нагляд за маршрутом\nN = 3..4 (межа реакції)", size=11, color="#1d4ed8", bold=True, fill="#eff6ff", stroke="#3b82f6", sw=1.2)
    p.append(b2)

    b3, _, _ = textbox(ox + 480, oy - 70, "Керування за винятком (MbE)\nРойова автономія: N = 20..50+", size=11, color="#15803d", bold=True, fill="#f0fdf4", stroke=FIELD, sw=1.4)
    p.append(b3)

    render(os.path.join(OUT, "human-attention-capacity.svg"), W, H, *p)


# ── 2. mission-hierarchy: Трирівнева ієрархія керування флотом ────────────────
def fig_mission_hierarchy():
    W, H = 840, 440
    p = []

    # 3 великі блоки рівнів (Зверху вниз)
    box_w = 780
    box_h = 100
    bx = 30

    # Рівень 1: Стратегічний (Людина над контуром)
    y1 = 30
    p.append(rect(bx, y1, box_w, box_h, fill="#eff6ff", stroke="#3b82f6", sw=1.8, rx=8))
    p.append(text(bx + 20, y1 + 28, "Рівень 3: Людина над контуром (Human-above-the-loop)", size=14, color="#1d4ed8", bold=True, anchor="start"))
    p.append(text(bx + 20, y1 + 52, "• Масштаб часу: хвилини — години", size=12, color=INK, anchor="start"))
    p.append(text(bx + 20, y1 + 74, "• Задачі: вибір полігонів пошуку, коридори безпеки, затвердження дій (ROE), пріоритети", size=12, color=INK, anchor="start"))
    b1, _, _ = textbox(bx + box_w - 90, y1 + 50, "Оператор\n(HMI / Карта)", size=12, color="#1d4ed8", bold=True, fill="#dbeafe", stroke="#3b82f6", sw=1.2)
    p.append(b1)

    # Стрілка зверху вниз (Наміри / Завдання) та знизу вгору (Винятки / Агрегований статус)
    p.append(arrow(bx + 220, y1 + box_h, bx + 220, y1 + box_h + 38, color="#1d4ed8", sw=2.0))
    p.append(text(bx + 230, y1 + box_h + 22, "Групові цілі, зони, обмеження", size=11, color="#1d4ed8", bold=True, anchor="start"))

    p.append(arrow(bx + 560, y1 + box_h + 38, bx + 560, y1 + box_h, color="#d97706", sw=2.0))
    p.append(text(bx + 570, y1 + box_h + 22, "Критичні винятки, виявлені цілі", size=11, color="#d97706", bold=True, anchor="start"))

    # Рівень 2: Тактичний ройовий координатор (Людина на контурі)
    y2 = 170
    p.append(rect(bx, y2, box_w, box_h, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(bx + 20, y2 + 28, "Рівень 2: Ройовий планувальник і координатор (Swarm Coordinator)", size=14, color="#15803d", bold=True, anchor="start"))
    p.append(text(bx + 20, y2 + 52, "• Масштаб часу: 1 — 10 секунд (децентралізований / наземний диспетчер)", size=12, color=INK, anchor="start"))
    p.append(text(bx + 20, y2 + 74, "• Задачі: розподіл цілей (аукціони CBBA), розбиття площі (Вороний), динамічні маршрути", size=12, color=INK, anchor="start"))
    b2, _, _ = textbox(bx + box_w - 90, y2 + 50, "Ройовий\nпланувальник", size=12, color="#15803d", bold=True, fill="#dcfce7", stroke=FIELD, sw=1.2)
    p.append(b2)

    # Стрілка між рівнем 2 і 3
    p.append(arrow(bx + 220, y2 + box_h, bx + 220, y2 + box_h + 38, color=FIELD, sw=2.0))
    p.append(text(bx + 230, y2 + box_h + 22, "Індивідуальні польотні завдання (Waypoints)", size=11, color=FIELD, bold=True, anchor="start"))

    p.append(arrow(bx + 560, y2 + box_h + 38, bx + 560, y2 + box_h, color="#4b5563", sw=2.0))
    p.append(text(bx + 570, y2 + box_h + 22, "Локальні позиції, стан батарей, зв'язок", size=11, color="#4b5563", bold=True, anchor="start"))

    # Рівень 3: Виконавчий бортовий автопілот (Людина поза прямим контуром)
    y3 = 310
    p.append(rect(bx, y3, box_w, box_h, fill="#faf5ff", stroke="#9333ea", sw=1.8, rx=8))
    p.append(text(bx + 20, y3 + 28, "Рівень 1: Бортовий автопілот (Flight Controller on-board)", size=14, color="#7e22ce", bold=True, anchor="start"))
    p.append(text(bx + 20, y3 + 52, "• Масштаб часу: 1 — 10 мілісекунд (100 — 400 Гц контур стабілізації)", size=12, color=INK, anchor="start"))
    p.append(text(bx + 20, y3 + 74, "• Задачі: PID кутів/швидкостей, утримання висоти, локальний обхід перешкод (ORCA / APF)", size=12, color=INK, anchor="start"))
    b3, _, _ = textbox(bx + box_w - 90, y3 + 50, "Бортовий\nконтролер", size=12, color="#7e22ce", bold=True, fill="#f3e8ff", stroke="#9333ea", sw=1.2)
    p.append(b3)

    render(os.path.join(OUT, "mission-hierarchy.svg"), W, H, *p)


# ── 3. fleet-overview-clustering: Екранний шум vs Семантична кластеризація ────
def fig_fleet_overview_clustering():
    W, H = 840, 420
    p = []

    # Ліва половина: Неструктурований UI (Шум)
    px = 25
    pw = 380
    ph = 370
    py = 25

    p.append(rect(px, py, pw, ph, fill="#fafafa", stroke="#e5e7eb", sw=1.5, rx=6))
    p.append(rect(px, py, pw, 36, fill="#fee2e2", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(px + pw / 2, py + 22, "1. Без кластеризації: 18 маркерів (Шум)", size=13, color=POS, bold=True))

    # Карта з хаотичними точками, що перекриваються
    import random
    rng = random.Random(42)

    # 3 групи точок на лівій карті
    centers = [(px + 100, py + 130), (px + 270, py + 160), (px + 180, py + 280)]
    for cidx, (cx, cy) in enumerate(centers):
        for k in range(6):
            dx = rng.uniform(-35, 35)
            dy = rng.uniform(-35, 35)
            uav_x = cx + dx
            uav_y = cy + dy
            # маркер дрона
            p.append(circle(uav_x, uav_y, 8, fill="#ffffff", stroke="#4b5563", sw=1.5))
            p.append(text(uav_x, uav_y + 3, str(cidx * 6 + k + 1), size=9, color=INK, bold=True))
            # дрібний текст телеметрії поруч (нашаровується)
            p.append(text(uav_x + 12, uav_y + 3, "98%", size=9, color="#6b7280", anchor="start"))

    # Один червоний апарат захований під купою
    p.append(circle(px + 280, py + 155, 8, fill="#ef4444", stroke="#991b1b", sw=2.0))
    p.append(text(px + 280, py + 158, "!", size=10, color="#ffffff", bold=True))

    b_err, _, _ = textbox(px + pw / 2, py + ph - 25, "Тривога маскується серед нагромадження іконок", size=11, color=POS, bold=True, fill="#fff5f5", stroke=POS, sw=1.0)
    p.append(b_err)

    # Права половина: Семантична кластеризація (MbE UI)
    rx = px + pw + 30
    p.append(rect(rx, py, pw, ph, fill="#f8fafc", stroke="#e2e8f0", sw=1.5, rx=6))
    p.append(rect(rx, py, pw, 36, fill="#dcfce7", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(rx + pw / 2, py + 22, "2. Агрегований UI: 3 кластери (Чисто)", size=13, color="#15803d", bold=True))

    # Кластер 1: Зелений (Штатно)
    rc1_x, rc1_y = rx + 100, py + 130
    p.append(circle(rc1_x, rc1_y, 28, fill="#dcfce7", stroke=FIELD, sw=2.5))
    p.append(text(rc1_x, rc1_y - 2, "6", size=16, color="#15803d", bold=True))
    p.append(text(rc1_x, rc1_y + 13, "БПЛА", size=9, color="#15803d", bold=True))
    p.append(text(rc1_x, rc1_y + 44, "Група «Північ» (100% OK)", size=10, color="#15803d", bold=True))

    # Кластер 2: Червоний (Аномалія: один борт має відмову)
    rc2_x, rc2_y = rx + 270, py + 160
    p.append(circle(rc2_x, rc2_y, 32, fill="#fee2e2", stroke=POS, sw=3.0))
    p.append(text(rc2_x, rc2_y - 3, "6", size=18, color=POS, bold=True))
    p.append(text(rc2_x, rc2_y + 13, "УВАГА!", size=9, color=POS, bold=True))
    p.append(text(rc2_x, rc2_y + 48, "Група «Схід» (1 борт: GPS Jam)", size=10, color=POS, bold=True))

    # Кластер 3: Зелений (Штатно)
    rc3_x, rc3_y = rx + 180, py + 280
    p.append(circle(rc3_x, rc3_y, 28, fill="#dcfce7", stroke=FIELD, sw=2.5))
    p.append(text(rc3_x, rc3_y - 2, "6", size=16, color="#15803d", bold=True))
    p.append(text(rc3_x, rc3_y + 13, "БПЛА", size=9, color="#15803d", bold=True))
    p.append(text(rc3_x, rc3_y + 44, "Група «Резерв» (100% OK)", size=10, color="#15803d", bold=True))

    # Зв'язки Mesh між кластерами
    p.append(line(rc1_x + 25, rc1_y + 10, rc2_x - 28, rc2_y - 10, color="#94a3b8", sw=1.8, dash="4 4"))
    p.append(line(rc1_x + 15, rc1_y + 25, rc3_x - 15, rc3_y - 22, color="#94a3b8", sw=1.8, dash="4 4"))
    p.append(line(rc2_x - 18, rc2_y + 25, rc3_x + 22, rc3_y - 15, color="#94a3b8", sw=1.8, dash="4 4"))

    b_ok, _, _ = textbox(rx + pw / 2, py + ph - 25, "Принцип найгіршого стану: тривога видно миттєво", size=11, color="#15803d", bold=True, fill="#f0fdf4", stroke=FIELD, sw=1.0)
    p.append(b_ok)

    render(os.path.join(OUT, "fleet-overview-clustering.svg"), W, H, *p)


# ── 4. management-by-exception-flow: Алгоритм керування за винятком ───────────
def fig_management_by_exception_flow():
    W, H = 840, 460
    p = []

    # 1. Вхідний потік
    x0, y0 = 40, 70
    b0, bw0, bh0 = textbox(x0 + 75, y0, "Телеметрія флоту\n(N апаратів, 10 Гц)", size=12, color=INK, bold=True, fill="#f1f5f9", stroke="#64748b", sw=1.5)
    p.append(b0)

    # Стрілка до детектора аномалій
    p.append(arrow(x0 + 150, y0, x0 + 200, y0, color=INK, sw=1.6))

    # 2. Блок детекції відхилень
    x1, y1 = x0 + 280, y0
    b1, bw1, bh1 = textbox(x1, y1, "Перевірка допусків:\n• Відхилення від планового треку > Δd\n• Заряд батареї < T_crit\n• Втрата лінка / GPS HDOP > 2.5", size=11, color=INK, bold=False, fill="#ffffff", stroke="#475569", sw=1.5)
    p.append(b1)

    # Розгалуження: Штатно (вниз) чи Аномалія (вправо)
    # Гілка 1: Штатно -> Тихий режим
    p.append(arrow(x1, y1 + bh1 / 2, x1, y1 + bh1 / 2 + 50, color=FIELD, sw=2.0))
    p.append(text(x1 + 10, y1 + bh1 / 2 + 25, "Штатно (99% часу)", size=11, color=FIELD, bold=True, anchor="start"))

    b_norm, _, _ = textbox(x1, y1 + bh1 / 2 + 85, "Тихий режим (Dark Cockpit):\nФоновий запис у журнал,\nнуль звуків і спливаючих вікон", size=11, color="#15803d", bold=True, fill="#f0fdf4", stroke=FIELD, sw=1.4)
    p.append(b_norm)

    # Гілка 2: Аномалія -> Класифікація і тротлінг
    p.append(arrow(x1 + bw1 / 2, y1, x1 + bw1 / 2 + 55, y1, color=POS, sw=2.0))
    p.append(text(x1 + bw1 / 2 + 25, y1 - 10, "Аномалія", size=11, color=POS, bold=True, anchor="middle"))

    x2, y2 = x1 + bw1 / 2 + 150, y0
    b2, bw2, bh2 = textbox(x2, y2, "Фільтрація та тротлінг:\n• Придушення шторму дублів\n• Визначення пріоритету (P0 / P1)", size=11, color=INK, bold=True, fill="#fffbeb", stroke="#d97706", sw=1.5)
    p.append(b2)

    # Стрілка вниз до ескалації оператору
    p.append(arrow(x2, y2 + bh2 / 2, x2, y2 + bh2 / 2 + 50, color="#d97706", sw=2.0))

    x3, y3 = x2, y2 + bh2 / 2 + 95
    b3, bw3, bh3 = textbox(x3, y3, "Ескалація операторові:\nКартка винятку з контекстом\nта вибором дії в 1 клік", size=12, color=POS, bold=True, fill="#fef2f2", stroke=POS, sw=1.8)
    p.append(b3)

    # Розгалуження після сповіщення: Відповідь за тайм-аутом?
    p.append(arrow(x3, y3 + bh3 / 2, x3, y3 + bh3 / 2 + 45, color=INK, sw=1.6))

    x4, y4 = x3, y3 + bh3 / 2 + 85
    b4, bw4, bh4 = textbox(x4, y4, "Оператор зреагував за T_timeout?", size=11, color=INK, bold=True, fill="#f8fafc", stroke="#64748b", sw=1.4)
    p.append(b4)

    # Відповідь: ТАК -> Виконання команди
    p.append(arrow(x4 - bw4 / 2, y4, x4 - bw4 / 2 - 50, y4, color=FIELD, sw=2.0))
    p.append(text(x4 - bw4 / 2 - 25, y4 - 10, "ТАК", size=11, color=FIELD, bold=True, anchor="middle"))

    b_act, _, _ = textbox(x4 - bw4 / 2 - 130, y4, "Виконання рішення:\nБорт приймає новий план", size=11, color="#15803d", bold=True, fill="#f0fdf4", stroke=FIELD, sw=1.2)
    p.append(b_act)

    # Відповідь: НІ -> Автономний Failsafe
    p.append(arrow(x4 + bw4 / 2, y4, x4 + bw4 / 2 + 50, y4, color=POS, sw=2.0))
    p.append(text(x4 + bw4 / 2 + 25, y4 - 10, "НІ", size=11, color=POS, bold=True, anchor="middle"))

    b_fail, _, _ = textbox(x4 + bw4 / 2 + 130, y4, "Автономний Failsafe:\nОрбіта очікування / RTL\nбез шкоди для рою", size=11, color=POS, bold=True, fill="#fff1f2", stroke=POS, sw=1.4)
    p.append(b_fail)

    render(os.path.join(OUT, "management-by-exception-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_human_attention_capacity()
    fig_mission_hierarchy()
    fig_fleet_overview_clustering()
    fig_management_by_exception_flow()
    print("Всі фігури згенеровано успішно.")
