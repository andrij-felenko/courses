# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def polygon(points, fill=FILL, stroke=LINE, sw=1.5):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

def path_builder(points, stroke=INK, sw=2, fill="none", dash=None):
    d_str = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in points)
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Схема розсіювання та дрейфу електронів у моделі Друде
# ════════════════════════════════════════════════════════════════════════════
def fig_scattering():
    W, H = 840, 420
    f = []

    # Розділювальна лінія між панелями
    f.append(line(420, 20, 420, 400, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: E = 0 ──
    f.append(text(210, 40, "Без електричного поля (E = 0)", size=16, bold=True, color=INK))
    f.append(text(210, 62, "Хаотичний термічний рух: середня швидкість dV/dt = 0", size=12, color=MUTED))

    # Рамка для лівої панелі
    f.append(rect(30, 80, 360, 280, fill="#fcfcfc", stroke=LINE, sw=1.2, rx=8))

    # Іони ґратки (3x3 grid)
    ions_left = [(90, 130), (210, 130), (330, 130),
                 (90, 220), (210, 220), (330, 220),
                 (90, 310), (210, 310), (330, 310)]
    for ix, iy in ions_left:
        f.append(circle(ix, iy, 16, fill="#fadbd8", stroke=POS, sw=2))
        f.append(text(ix, iy + 5, "+", size=16, bold=True, color=POS))

    # Замкнена/хаотична траєкторія електрона (без поля)
    traj_left = [(60, 290), (90, 130), (210, 130), (210, 310), (330, 220), (210, 220), (65, 285)]
    f.append(path_builder(traj_left, stroke=NEG, sw=2.2, dash="3 3"))
    f.append(circle(60, 290, 6, fill=NEG, stroke=INK, sw=1.5))
    f.append(text(50, 315, "Старт/Фініш", size=11, color=NEG, bold=True))

    # Пояснення внизу лівої панелі
    f.append(text(210, 385, "Зсув за час tau дорівнює нулю: J = 0", size=13, bold=True, color=INK))

    # ── Права панель: E > 0 ──
    f.append(text(630, 40, "Ззовні прикладено поле E > 0", size=16, bold=True, color=INK))
    f.append(text(630, 62, "Напрямлений дрейф проти поля з часом релаксації tau", size=12, color=MUTED))

    # Рамка для правої панелі
    f.append(rect(450, 80, 360, 280, fill="#fcfcfc", stroke=LINE, sw=1.2, rx=8))

    # Вектор електричного поля E (вліво)
    f.append(arrow(750, 105, 510, 105, color=POS, sw=2.5))
    f.append(text(630, 100, "Електричне поле E", size=13, bold=True, color=POS))

    # Іони ґратки правого боку
    ions_right = [(510, 150), (630, 150), (750, 150),
                  (510, 240), (630, 240), (750, 240),
                  (510, 330), (630, 330), (750, 330)]
    for ix, iy in ions_right:
        f.append(circle(ix, iy, 16, fill="#fadbd8", stroke=POS, sw=2))
        f.append(text(ix, iy + 5, "+", size=16, bold=True, color=POS))

    # Траєкторія зі зсувом під дією поля E
    traj_right = [(480, 310), (510, 150), (645, 155), (655, 335), (770, 245)]
    f.append(path_builder(traj_right, stroke=NEG, sw=2.2, dash="3 3"))
    f.append(circle(480, 310, 6, fill=MUTED, stroke=INK, sw=1.5)) # старт
    f.append(circle(770, 245, 7, fill=NEG, stroke=INK, sw=1.5)) # фініш

    # Стрілка дрейфу
    f.append(arrow(480, 345, 770, 345, color=FIELD, sw=2.5))
    f.append(text(625, 338, "Дрейф v_d = -e E tau / m", size=12, bold=True, color=FIELD))

    f.append(text(630, 385, "Результуючий струм J = n e² tau E / m", size=13, bold=True, color=INK))

    render(os.path.join(OUT, "drude-gas-scattering.svg"), W, H, "\n".join(f))

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Ефект Голла у моделі Друде
# ════════════════════════════════════════════════════════════════════════════
def fig_hall_effect():
    W, H = 840, 420
    f = []

    f.append(text(420, 35, "Геометрія ефекту Голла в металевому провіднику", size=16, bold=True, color=INK))
    f.append(text(420, 58, "Рівновага сили Лоренца та поперечного поля Голла у стаціонарному стані", size=12, color=MUTED))

    # Задні лінії
    f.append(line(250, 120, 650, 120, color=MUTED, sw=1.2, dash="3 3"))
    f.append(line(250, 120, 250, 260, color=MUTED, sw=1.2, dash="3 3"))
    f.append(line(250, 120, 150, 180, color=MUTED, sw=1.2, dash="3 3"))

    # Основний об'єм (полігон верхньої та бічної граней)
    # Верхня грань
    f.append(polygon([(150, 180), (250, 120), (650, 120), (550, 180)], fill="#e8f4f8", stroke=LINE, sw=1.5))
    # Права бічна грань
    f.append(polygon([(550, 180), (650, 120), (650, 260), (550, 320)], fill="#d4e6f1", stroke=LINE, sw=1.5))
    # Передня грань
    f.append(polygon([(150, 180), (550, 180), (550, 320), (150, 320)], fill="#ebf5fb", stroke=LINE, sw=2.0))

    # Магнітне поле B (вгору по осі Z)
    f.append(arrow(350, 370, 350, 65, color=FIELD, sw=3.0))
    f.append(text(350, 52, "Магнітне поле B_z", size=14, bold=True, color=FIELD))

    # Густина струму J_x (вправо вздовж осі X)
    f.append(arrow(80, 250, 220, 250, color=POS, sw=3.0))
    f.append(text(120, 238, "Струм J_x", size=13, bold=True, color=POS))

    # Дрейф електронів v_x (вліво, бо електрон негативний)
    f.append(arrow(480, 250, 360, 250, color=NEG, sw=2.5))
    f.append(circle(480, 250, 6, fill=NEG, stroke=INK, sw=1.5))
    f.append(text(440, 238, "v_x (електрони)", size=12, bold=True, color=NEG))

    # Накопичення негативних зарядів на верхній/передній грані
    charges_neg = [(200, 172), (300, 172), (400, 172), (500, 172)]
    for cx, cy in charges_neg:
        f.append(circle(cx, cy, 7, fill="#d4e6f1", stroke=NEG, sw=1.2))
        f.append(text(cx, cy + 4, "−", size=12, bold=True, color=NEG))

    # Накопичення позитивних зарядів на нижній грані
    charges_pos = [(200, 328), (300, 328), (400, 328), (500, 328)]
    for cx, cy in charges_pos:
        f.append(circle(cx, cy, 7, fill="#fadbd8", stroke=POS, sw=1.2))
        f.append(text(cx, cy + 4, "+", size=12, bold=True, color=POS))

    # Поперечне поле Голла E_y (напрямлене від + до -)
    f.append(arrow(280, 315, 280, 188, color=POS, sw=2.0))
    f.append(text(245, 255, "Поле E_y", size=12, bold=True, color=POS))

    # Сила Лоренца F_L (напрямлена доверх)
    f.append(arrow(480, 250, 480, 190, color="#8e44ad", sw=2.0))
    f.append(text(525, 215, "Сила Лоренца F_L", size=12, bold=True, color="#8e44ad"))

    # Прямокутник результату у правій частині
    tb, tw, th = textbox(690, 250, "Коефіцієнт Голла:\n\nR_H = E_y / (J_x · B_z)\nR_H = -1 / (n · e)",
                         size=13, pad=12, fill="#ffffff", stroke=LINE, sw=1.8, color=INK, bold=True)
    f.append(tb)

    f.append(text(420, 395, "Значення R_H залежить ЛИШЕ від концентрації електронів n та їхнього заряду", size=12, bold=True, color=INK))

    render(os.path.join(OUT, "hall-effect-drude.svg"), W, H, "\n".join(f))

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Подвійна помилка Друде в законі Відемана — Франца
# ════════════════════════════════════════════════════════════════════════════
def fig_wiedemann_franz():
    W, H = 840, 420
    f = []

    f.append(text(420, 35, "Випадковий успіх: подвійна компенсація помилок Друде", size=16, bold=True, color=INK))
    f.append(text(420, 58, "Чому класична модель Друде збіглася з експериментом у законі Відемана — Франца", size=12, color=MUTED))

    # Картка 1: Завищення теплоємності
    c1, w1, h1 = textbox(210, 140, "Помилка №1: Теплоємність c_v\n\nКласичний газ (Максвелл-Больцман):\nc_v = (3/2) · n · k_B\n\nЗАВИЩЕНО у ~100 разів!",
                         size=12, pad=12, fill="#fadbd8", stroke=POS, sw=1.8, color=INK, bold=False)
    f.append(c1)

    # Картка 2: Заниження квадрата швидкості
    c2, w2, h2 = textbox(630, 140, "Помилка №2: Квадрат швидкості v²\n\nКласична теплова швидкість:\nv_th² = 3 · k_B · T / m\n\nЗАНИЖЕНО у ~100 разів!",
                         size=12, pad=12, fill="#d4e6f1", stroke=NEG, sw=1.8, color=INK, bold=False)
    f.append(c2)

    # Стрілки компенсації до центру
    f.append(arrow(340, 140, 410, 140, color=POS, sw=2.5))
    f.append(arrow(500, 140, 430, 140, color=NEG, sw=2.5))

    # Центральний вузол перемноження
    c3, w3, h3 = textbox(420, 245, "Теплопровідність kappa = (1/3) · c_v · v² · tau\n\nДобуток: (100) × (1/100) = 1 (Повна компенсація!)",
                         size=13, pad=14, fill="#e8f8f5", stroke=FIELD, sw=2.0, color=INK, bold=True)
    f.append(c3)

    # Нижній порівняльний блок
    c4, w4, h4 = textbox(420, 355, "Число Лоренца L = kappa / (sigma · T):\n• Модель Друде: L = (3/2) · (k_B / e)² ≈ 2.23 × 10⁻⁸ Вт·Ом/К²\n• Квантова модель Зоммерфельда: L = (pi²/3) · (k_B / e)² ≈ 2.44 × 10⁻⁸ Вт·Ом/К²",
                         size=12, pad=12, fill="#ffffff", stroke=LINE, sw=1.5, color=INK, bold=False)
    f.append(c4)

    render(os.path.join(OUT, "wiedemann-franz-cancellation.svg"), W, H, "\n".join(f))

# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Оптичні властивості та плазмовий резонанс
# ════════════════════════════════════════════════════════════════════════════
def fig_reflectivity():
    W, H = 840, 420
    f = []

    f.append(text(420, 35, "Оптичний спектр та відбивання металу за моделлю Друде", size=16, bold=True, color=INK))
    f.append(text(420, 58, "Залежність діелектричної проникності epsilon_1 та коефіцієнта відбивання R від частоти omega", size=12, color=MUTED))

    # Графічні осі
    f.append(line(100, 330, 750, 330, color=LINE, sw=2.0)) # X axis
    f.append(line(100, 330, 100, 90, color=POS, sw=2.0)) # Y left axis (R)
    f.append(line(750, 330, 750, 90, color=NEG, sw=2.0)) # Y right axis (eps)

    # Пунктирна лінія нульового рівня для діелектричної проникності epsilon_1 = 0
    f.append(line(100, 238, 750, 238, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(785, 238, "eps = 0", size=11, color=MUTED))

    # Пунктирна вертикальна лінія плазмової частоти w = w_p (x = 450)
    f.append(line(450, 90, 450, 345, color=FIELD, sw=1.8, dash="4 4"))
    f.append(text(450, 365, "omega = omega_p (Плазмова частота)", size=12, bold=True, color=FIELD))

    # Підписи осей
    f.append(text(420, 395, "Частота падаючої хвилі omega / omega_p", size=13, bold=True, color=INK))
    f.append(text(80, 80, "Відбивання R (%)", size=12, bold=True, color=POS))
    f.append(text(760, 80, "Проникність epsilon_1", size=12, bold=True, color=NEG))

    # Крива відбивання R(w): R = 100% до w_p (x=450), далі різке падіння до 0
    pts_R = [(100, 100), (430, 100), (450, 110), (470, 280), (520, 320), (750, 328)]
    f.append(path_builder(pts_R, stroke=POS, sw=3.0, fill="none"))

    # Крива діелектричної проникності epsilon_1(w) = 1 - (w_p/w)²
    pts_eps = [(120, 325), (200, 315), (300, 290), (400, 255), (450, 238), (550, 180), (650, 145), (750, 130)]
    f.append(path_builder(pts_eps, stroke=NEG, sw=2.5, fill="none"))

    # Пояснювальні області
    f.append(rect(150, 140, 240, 50, fill="#fdf2e9", stroke=POS, sw=1.2, rx=6))
    f.append(text(270, 160, "omega < omega_p: Дзеркальне відбивання", size=11, bold=True, color=POS))
    f.append(text(270, 177, "Метал непрозорий (блиск)", size=11, color=INK))

    f.append(rect(490, 140, 230, 50, fill="#eaf2f8", stroke=NEG, sw=1.2, rx=6))
    f.append(text(605, 160, "omega > omega_p: Прозорість", size=11, bold=True, color=NEG))
    f.append(text(605, 177, "Хвиля проходить крізь метал", size=11, color=INK))

    render(os.path.join(OUT, "drude-reflectivity.svg"), W, H, "\n".join(f))

if __name__ == "__main__":
    fig_scattering()
    fig_hall_effect()
    fig_wiedemann_franz()
    fig_reflectivity()
    print("Figures generated successfully in img/")
