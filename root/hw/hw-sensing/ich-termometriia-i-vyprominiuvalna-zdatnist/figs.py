# -*- coding: utf-8 -*-
"""Фігури до теми «ІЧ-термометрія й випромінювальна здатність».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREY = "#8a8a8a"
LIGHT_BLUE = "#eef4fd"
LIGHT_RED = "#fdf2f2"
LIGHT_GREEN = "#f0fdf4"
LIGHT_YELLOW = "#fefce8"
ACCENT_ORANGE = "#d97706"


# ── 1. Спектральні криві Планка та закон зміщення Віна ────────────────────────
def fig_blackbody_planck():
    W, H = 760, 400
    f = []
    
    ox, oy = 80, 330
    top, right = 40, 720
    
    # Виділена зона 8-14 мкм (LWIR оптичне вікно)
    # Масштаб осі X: від 0 до 25 мкм. x = ox + (lambda / 25) * 600
    x_lwir_start = ox + (8.0 / 25.0) * 600.0   # 272.0
    x_lwir_end = ox + (14.0 / 25.0) * 600.0     # 416.0
    
    f.append(rect(x_lwir_start, top + 20, x_lwir_end - x_lwir_start, oy - top - 20,
                  fill=LIGHT_GREEN, stroke=FIELD, sw=1.2, rx=0))
    f.append(line(x_lwir_start, top + 20, x_lwir_start, oy, color=FIELD, sw=1.2, dash="3,3"))
    f.append(line(x_lwir_end, top + 20, x_lwir_end, oy, color=FIELD, sw=1.2, dash="3,3"))
    
    f.append(text((x_lwir_start + x_lwir_end) / 2, top + 38, "Оптичне вікно LWIR (8–14 мкм)",
                  size=11, color=FIELD, bold=True))
    f.append(text((x_lwir_start + x_lwir_end) / 2, top + 54, "смуга фільтра безконтактних пірометрів",
                  size=9.5, color=FIELD, italic=True))
    
    # Осі
    f.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    f.append(arrow(ox, oy, right, oy, color=INK, sw=1.6))
    f.append(text(ox - 10, top + 10, "Спектральна густина випромінювання E_λ", size=11, color=INK, anchor="end", bold=True))
    f.append(text(right - 5, oy + 24, "Довжина хвилі λ (мкм)", size=11, color=INK, anchor="end", bold=True))
    
    # Поділки на осі X (0, 5, 10, 15, 20, 25 мкм)
    for l_val in [5, 10, 15, 20, 25]:
        px = ox + (l_val / 25.0) * 600.0
        f.append(line(px, oy, px, oy + 5, color=INK, sw=1.2))
        f.append(text(px, oy + 18, "%d" % l_val, size=10, color=MUTED))
    f.append(text(ox, oy + 18, "0", size=10, color=MUTED))
    
    def planck_profile(t_k, max_scale):
        pts = []
        c2 = 14388.0
        for step in range(1, 121):
            lam = step * 0.2 + 0.5  # 0.7 .. 24.5 μm
            px = ox + (lam / 25.0) * 600.0
            x_exp = c2 / (lam * t_k)
            if x_exp > 70.0:
                val = 0.0
            else:
                val = (1.0 / (lam ** 5)) / (math.exp(x_exp) - 1.0)
            py = oy - (val * max_scale)
            py = max(top + 10, min(oy, py))
            pts.append((px, py))
        return pts
    
    # 500 K (гарячий об'єкт, ~227 °C)
    pts_500 = planck_profile(500, 1.8e4)
    path_500 = "M " + " ".join("%.1f,%.1f" % (p[0], p[1]) for p in pts_500)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path_500, POS))
    pk_500_x = ox + (5.80 / 25.0) * 600.0
    f.append(circle(pk_500_x, 70, 3.5, fill=POS, stroke=POS))
    f.append(text(pk_500_x + 8, 66, "500 K (227 °C), λ_max = 5.8 μm", size=10, color=POS, anchor="start", bold=True))
    
    # 400 K (127 °C)
    pts_400 = planck_profile(400, 4.8e4)
    path_400 = "M " + " ".join("%.1f,%.1f" % (p[0], p[1]) for p in pts_400)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_400, ACCENT_ORANGE))
    pk_400_x = ox + (7.25 / 25.0) * 600.0
    f.append(circle(pk_400_x, 150, 3.5, fill=ACCENT_ORANGE, stroke=ACCENT_ORANGE))
    f.append(text(pk_400_x + 8, 145, "400 K (127 °C), λ_max = 7.2 μm", size=10, color=ACCENT_ORANGE, anchor="start", bold=True))
    
    # 300 K (кімнатна температура, ~27 °C)
    pts_300 = planck_profile(300, 1.3e5)
    path_300 = "M " + " ".join("%.1f,%.1f" % (p[0], p[1]) for p in pts_300)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_300, NEG))
    pk_300_x = ox + (9.66 / 25.0) * 600.0
    f.append(circle(pk_300_x, 248, 4.0, fill=NEG, stroke=NEG))
    f.append(text(pk_300_x + 10, 235, "300 K (27 °C), λ_max = 9.7 μm", size=10.5, color=NEG, anchor="start", bold=True))
    f.append(text(pk_300_x + 10, 250, "пік точно в зоні LWIR!", size=9.5, color=NEG, italic=True))
    
    # Лінія зміщення Віна через піки
    f.append(line(pk_500_x, 70, pk_300_x + 30, 275, color=GREY, sw=1.2, dash="4,3"))
    f.append(text(pk_400_x - 12, 110, "Закон Віна: λ_max · T = b", size=10, color=MUTED, anchor="end", italic=True))
    
    # Підпис внизу
    f.append(text(W / 2, 380, "Зі зниженням температури пік зміщується вправо, а загальна площа падає пропорційно T⁴",
                  size=11, color=INK, italic=True))
    
    render(os.path.join(IMG, "blackbody-planck-curves.svg"), W, H, *f,
           title="Спектральний розподіл випромінювання Планка та закон зміщення Віна")


# ── 2. Радіаційний баланс і випромінювальна здатність ────────────────────────
def fig_emissivity_reflection():
    W, H = 760, 380
    f = []
    
    # Ліва панель
    f.append(rect(20, 20, 345, 340, fill=FILL, stroke=LINE, sw=1.4, rx=6))
    f.append(text(192, 45, "Матова поверхня / діелектрик (ε = 0.95)", size=12.5, color=INK, bold=True))
    f.append(text(192, 62, "пластик, анодований метал, шкіра, дерево", size=10, color=MUTED))
    
    # Поверхня об'єкта
    f.append(rect(40, 220, 305, 45, fill="#d1d5db", stroke=LINE, sw=1.5, rx=3))
    f.append(text(192, 247, "Об'єкт вимірювання (T_obj = 80 °C)", size=11, bold=True))
    
    # Власне випромінювання (велике)
    f.append(arrow(110, 220, 110, 100, color=POS, sw=3.2))
    f.append(text(110, 85, "Власне: ε · σ · T_obj⁴", size=10.5, color=POS, bold=True))
    f.append(text(110, 160, "95% сигналу", size=10, color=POS, bold=True, anchor="start"))
    
    # Падаюче фонове від оточення
    f.append(arrow(260, 95, 230, 215, color=NEG, sw=1.5))
    f.append(text(265, 90, "Фон: σ · T_amb⁴", size=10, color=NEG, anchor="start"))
    
    # Відбите фонове (мізерне)
    f.append(arrow(230, 215, 200, 100, color=NEG, sw=1.0))
    f.append(text(205, 140, "Відбите: (1−ε) · σ · T_amb⁴", size=9.5, color=NEG, anchor="start"))
    f.append(text(205, 155, "лише 5% сигналу", size=9, color=MUTED, anchor="start"))
    
    # Сенсор
    f.append(rect(100, 290, 185, 55, fill=LIGHT_GREEN, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(192, 312, "Показання пірометра: ~78.5 °C", size=11, color=FIELD, bold=True))
    f.append(text(192, 330, "Похибка мінімальна (ΔT ≈ −1.5 °C)", size=9.5, color=FIELD))
    
    # Права панель
    f.append(rect(395, 20, 345, 340, fill=FILL, stroke=LINE, sw=1.4, rx=6))
    f.append(text(567, 45, "Полірований метал (ε = 0.10, ρ = 0.90)", size=12.5, color=INK, bold=True))
    f.append(text(567, 62, "полірована мідь, алюмінієва шина, сталь", size=10, color=MUTED))
    
    # Поверхня об'єкта (дзеркальна)
    f.append(rect(415, 220, 305, 45, fill="#93c5fd", stroke=LINE, sw=1.5, rx=3))
    f.append(text(567, 247, "Об'єкт вимірювання (T_obj = 80 °C)", size=11, bold=True))
    
    # Власне випромінювання (крихітне)
    f.append(arrow(480, 220, 480, 130, color=POS, sw=1.2))
    f.append(text(480, 115, "Власне: 10%", size=10, color=POS, bold=True))
    
    # Падаюче фонове
    f.append(arrow(645, 95, 605, 215, color=NEG, sw=2.5))
    f.append(text(650, 90, "Фон кімнати (25 °C)", size=10, color=NEG, anchor="start", bold=True))
    
    # Відбите фонове (величезне — дзеркало!)
    f.append(arrow(605, 215, 565, 100, color=NEG, sw=3.0))
    f.append(text(565, 85, "Відбите фонове: 90%", size=10.5, color=NEG, bold=True))
    f.append(text(575, 155, "«Термічне дзеркало»", size=10, color=NEG, italic=True, anchor="start"))
    
    # Сенсор
    f.append(rect(475, 290, 185, 55, fill=LIGHT_RED, stroke=POS, sw=1.5, rx=4))
    f.append(text(567, 312, "Показання пірометра: ~31 °C", size=11, color=POS, bold=True))
    f.append(text(567, 330, "Катастрофічна похибка (ΔT ≈ −49 °C!)", size=9.5, color=POS, bold=True))
    
    render(os.path.join(IMG, "emissivity-and-reflection.svg"), W, H, *f,
           title="Радіаційний баланс і похибка вимірювання на поверхнях з різною випромінювальною здатністю")


# ── 3. Конструкція MEMS-термостовпчика в розрізі TO-корпусу ──────────────────
def fig_thermopile_mems():
    W, H = 760, 410
    f = []
    
    # Вхідне оптичне вікно (фільтр 8-14 мкм)
    f.append(rect(280, 30, 200, 26, fill="#99f6e4", stroke=FIELD, sw=2.0, rx=3))
    f.append(text(380, 47, "ІЧ-фільтр (Ge / Si віконце 8–14 мкм)", size=10.5, color=FIELD, bold=True))
    
    # Металевий корпус TO-39/TO-46
    f.append(rect(130, 60, 500, 300, fill="#f8fafc", stroke=LINE, sw=2.2, rx=10))
    f.append(text(380, 85, "Металевий корпус датчика (TO-39 / TO-46) — ізотермічна опора", size=11.5, color=INK, bold=True))
    
    # Промені ІЧ через вікно
    f.append(arrow(320, 15, 340, 42, color=POS, sw=1.8))
    f.append(arrow(380, 15, 380, 42, color=POS, sw=1.8))
    f.append(arrow(440, 15, 420, 42, color=POS, sw=1.8))
    f.append(text(380, 10, "Падаючий ІЧ-потік від об'єкта", size=10.5, color=POS, bold=True))
    
    # Кремнієва підкладка (Bulk Silicon)
    f.append(rect(180, 140, 400, 150, fill="#e2e8f0", stroke=LINE, sw=1.8, rx=4))
    f.append(text(240, 260, "Кремнієва підкладка", size=11, color=INK, bold=True))
    f.append(text(240, 275, "(холодна опора T_die)", size=9.5, color=MUTED))
    
    # Витравлена порожнина (Etched cavity)
    f.append(rect(290, 140, 180, 100, fill="#ffffff", stroke=LINE, sw=1.4, rx=0))
    f.append(text(380, 215, "Витравлена вакуумна/газова порожнина", size=9.5, color=MUTED, italic=True))
    f.append(text(380, 230, "(високий тепловий опір R_th)", size=9, color=MUTED))
    
    # Тонка діелектрична мембрана (SiO2 / SiN, товщина 1 мкм)
    f.append(line(260, 140, 500, 140, color=LINE, sw=3.0))
    f.append(text(190, 125, "Тонка мембрана (1 мкм SiN/SiO₂)", size=10, color=INK, bold=True, anchor="start"))
    
    # Чорний ІЧ-поглинач у центрі мембрани (лежить зверху на мембрані)
    f.append(rect(330, 126, 100, 12, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=2))
    f.append(text(380, 118, "ІЧ-поглинач (гаряча зона T_hot)", size=10, color=POS, bold=True))
    
    # Мікротермопари (полікремній p/n)
    # Зліва: гарячий спай у центрі (340, 140), холодний на підкладці (280, 140)
    f.append(line(275, 140, 335, 140, color=POS, sw=3.0))
    f.append(circle(335, 140, 3.5, fill=POS, stroke=POS))  # гарячий спай
    f.append(circle(275, 140, 3.5, fill=NEG, stroke=NEG))  # холодний спай
    
    # Справа
    f.append(line(425, 140, 485, 140, color=POS, sw=3.0))
    f.append(circle(425, 140, 3.5, fill=POS, stroke=POS))  # гарячий спай
    f.append(circle(485, 140, 3.5, fill=NEG, stroke=NEG))  # холодний спай
    
    f.append(text(300, 158, "N термопар", size=9.5, color=POS, bold=True))
    f.append(text(460, 158, "N термопар", size=9.5, color=POS, bold=True))
    
    # Вбудований датчик температури кристала PTAT / NTC
    f.append(rect(480, 240, 90, 40, fill=LIGHT_BLUE, stroke=NEG, sw=1.5, rx=3))
    f.append(text(525, 256, "PTAT / NTC", size=10, color=NEG, bold=True))
    f.append(text(525, 272, "міряє T_die", size=9, color=NEG))
    
    # Виводи датчика
    f.append(line(230, 290, 230, 385, color=LINE, sw=3.0))
    f.append(line(350, 290, 350, 385, color=LINE, sw=3.0))
    f.append(line(410, 290, 410, 385, color=LINE, sw=3.0))
    f.append(line(530, 290, 530, 385, color=LINE, sw=3.0))
    
    f.append(text(230, 400, "V_tp+", size=10, bold=True))
    f.append(text(350, 400, "GND", size=10, bold=True))
    f.append(text(410, 400, "V_tp−", size=10, bold=True))
    f.append(text(530, 400, "T_die вихід", size=10, bold=True))
    
    render(os.path.join(IMG, "thermopile-mems-structure.svg"), W, H, *f,
           title="Будова безконтактного сенсора на базі MEMS-термостовпчика в TO-корпусі")


# ── 4. Геометрія поля зору (FOV) та оптичне співвідношення D:S ────────────────
def fig_field_of_view():
    W, H = 760, 360
    f = []
    
    # Верхній сценарій: Правильне вимірювання (пляма менша за об'єкт)
    f.append(rect(20, 20, 720, 150, fill=FILL, stroke=LINE, sw=1.4, rx=6))
    f.append(text(380, 40, "Правильне вимірювання: об'єкт повністю перекриває поле зору (100% Spot Fill)",
                  size=11.5, color=FIELD, bold=True))
    
    # Сенсор зліва
    f.append(rect(45, 65, 70, 70, fill="#ffffff", stroke=LINE, sw=1.6, rx=4))
    f.append(text(80, 100, "ІЧ-давач", size=11, bold=True))
    f.append(text(80, 116, "FOV 35°", size=9.5, color=MUTED))
    
    # Конус огляду
    f.append('<polygon points="115,100 480,60 480,140" fill="%s" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' %
             (LIGHT_GREEN, FIELD))
    f.append(line(115, 100, 480, 100, color=GREY, sw=1.0, dash="2,2"))
    
    # Об'єкт справа (великий прямокутник)
    f.append(rect(480, 50, 40, 100, fill="#fca5a5", stroke=POS, sw=1.8, rx=2))
    f.append(text(540, 95, "Цільовий об'єкт (70 °C)", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(540, 112, "Діаметр плями S < Розмір об'єкта D_obj", size=9.5, color=INK, anchor="start"))
    f.append(text(540, 128, "Результат: точні 70.0 °C", size=10, color=FIELD, bold=True, anchor="start"))
    
    # Розміри: дистанція L і пляма S
    f.append(arrow(115, 150, 480, 150, color=INK, sw=1.2))
    f.append(text(297, 144, "Дистанція вимірювання L", size=9.5, color=INK))
    
    # Нижній сценарій: Похибка недозаповнення поля зору (пляма більша за об'єкт)
    f.append(rect(20, 190, 720, 150, fill=FILL, stroke=LINE, sw=1.4, rx=6))
    f.append(text(380, 210, "Помилка: пляма зору ширша за мішень — фонове випромінювання спотворює вимір",
                  size=11.5, color=POS, bold=True))
    
    # Сенсор зліва
    f.append(rect(45, 235, 70, 70, fill="#ffffff", stroke=LINE, sw=1.6, rx=4))
    f.append(text(80, 270, "ІЧ-давач", size=11, bold=True))
    f.append(text(80, 286, "FOV 35°", size=9.5, color=MUTED))
    
    # Конус огляду
    f.append('<polygon points="115,270 480,225 480,315" fill="%s" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' %
             (LIGHT_RED, POS))
    
    # Фон позаду
    f.append(rect(480, 220, 40, 100, fill="#93c5fd", stroke=NEG, sw=1.5, rx=2))
    # Маленький об'єкт по центру
    f.append(rect(480, 255, 40, 30, fill="#fca5a5", stroke=POS, sw=2.0, rx=1))
    
    f.append(text(540, 260, "Мішень (SMD чіп 70 °C, 30% плями)", size=10, color=POS, bold=True, anchor="start"))
    f.append(text(540, 276, "Холодна PCB (25 °C, 70% плями)", size=10, color=NEG, bold=True, anchor="start"))
    f.append(text(540, 298, "Результат: усереднені ~42 °C (заниження на 28 °C!)", size=10.5, color=POS, bold=True, anchor="start"))
    
    render(os.path.join(IMG, "field-of-view-geometry.svg"), W, H, *f,
           title="Оптичне поле зору (FOV), співвідношення D:S та похибка перекриття плями")


# ── 5. Сигнальний тракт цифрового інфрачервоного термометра ────────────────────
def fig_signal_pipeline():
    W, H = 760, 360
    f = []
    
    # Загальний корпус мікросхеми (ASIC)
    f.append(rect(20, 20, 720, 320, fill=FILL, stroke=LINE, sw=1.8, rx=8))
    f.append(text(380, 45, "Архітектура цифрового ІЧ-термометра (MLX90614 / TMP006)", size=13, color=INK, bold=True))
    
    # Блок 1: MEMS-термостовпчик
    f.append(rect(40, 80, 120, 80, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(100, 105, "MEMS", size=11, bold=True))
    f.append(text(100, 120, "Термостовпчик", size=11, bold=True))
    f.append(text(100, 142, "0 .. ±5 мВ", size=10, color=POS, bold=True))
    
    # Блок 1б: Датчик температури кристала (T_die)
    f.append(rect(40, 190, 120, 70, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(100, 215, "PTAT / NTC", size=11, bold=True))
    f.append(text(100, 232, "Датчик T_die", size=10, color=NEG, bold=True))
    f.append(text(100, 248, "холодні спаї", size=9, color=MUTED))
    
    # Стрілки до підсилювача та мультиплексора
    f.append(arrow(160, 120, 205, 120, color=INK, sw=1.8))
    f.append(arrow(160, 225, 205, 225, color=INK, sw=1.8))
    
    # Блок 2: Чопперний інструментальний підсилювач (PGA)
    f.append(rect(205, 80, 125, 180, fill=LIGHT_BLUE, stroke=NEG, sw=1.5, rx=4))
    f.append(text(267, 115, "Чопперний", size=11, color=NEG, bold=True))
    f.append(text(267, 132, "підсилювач", size=11, color=NEG, bold=True))
    f.append(text(267, 149, "(PGA 100–2000×)", size=10, color=NEG))
    f.append(line(215, 168, 320, 168, color=GREY, sw=1, dash="2,2"))
    f.append(text(267, 190, "Автообнулення", size=9.5, color=INK))
    f.append(text(267, 208, "усунення зсуву", size=9, color=MUTED))
    f.append(text(267, 224, "та шуму 1/f", size=9, color=MUTED))
    
    # Стрілка до АЦП
    f.append(arrow(330, 170, 370, 170, color=INK, sw=1.8))
    
    # Блок 3: Sigma-Delta АЦП 17-біт
    f.append(rect(370, 100, 110, 140, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(425, 135, "17-бітний", size=11, bold=True))
    f.append(text(425, 152, "Sigma-Delta", size=11, bold=True))
    f.append(text(425, 169, "АЦП (ΣΔ)", size=11, bold=True))
    f.append(text(425, 200, "Роздільність", size=9.5, color=MUTED))
    f.append(text(425, 216, "0.02 °C / LSB", size=9.5, color=FIELD, bold=True))
    
    # Стрілка до DSP
    f.append(arrow(480, 170, 520, 170, color=INK, sw=1.8))
    
    # Блок 4: Цифровий сигнальний процесор (DSP)
    f.append(rect(520, 75, 195, 190, fill=LIGHT_GREEN, stroke=FIELD, sw=1.6, rx=5))
    f.append(text(617, 100, "DSP процесор", size=12, color=FIELD, bold=True))
    f.append(text(617, 122, "1. Лінеаризація поліномами", size=9.5, color=INK, anchor="middle"))
    f.append(text(617, 140, "2. Компенсація T_die (Стефан–Больцман)", size=9.0, color=INK, anchor="middle"))
    f.append(text(617, 158, "3. Корекція ε (EEPROM коефіцієнт)", size=9.5, color=INK, anchor="middle"))
    f.append(text(617, 176, "4. IIR / FIR цифровий фільтр", size=9.5, color=INK, anchor="middle"))
    
    f.append(line(535, 195, 700, 195, color=FIELD, sw=1, dash="3,2"))
    f.append(text(617, 215, "Інтерфейс I2C / SMBus", size=11, color=FIELD, bold=True))
    f.append(text(617, 235, "Регістри RAM (T_obj, T_amb) + CRC-8 PEC", size=9.0, color=MUTED))
    
    # Вихідні стрілки з DSP
    f.append(arrow(617, 265, 617, 310, color=INK, sw=2.2))
    f.append(text(617, 325, "До мікроконтролера (SDA, SCL)", size=10.5, color=INK, bold=True))
    
    render(os.path.join(IMG, "signal-conditioning-pipeline.svg"), W, H, *f,
           title="Сигнальний тракт та цифрова архітектура інтегрованого інфрачервоного пірометра")


if __name__ == "__main__":
    fig_blackbody_planck()
    fig_emissivity_reflection()
    fig_thermopile_mems()
    fig_field_of_view()
    fig_signal_pipeline()
    print("All figures generated successfully!")
