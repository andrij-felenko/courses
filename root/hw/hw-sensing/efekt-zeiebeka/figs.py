# -*- coding: utf-8 -*-
"""Фігури до теми «Ефект Зеєбека».
Запуск: python figs.py  → генерує SVG у ./img/
Стиль і допоміжні функції — з svgkit (scripts/svgkit.py).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WARM = "#e08a3c"   # колір тепла / гарячого боку
COLD = "#2457d6"   # колір холоду / холодного боку
ACCENT = "#8e44ad" # акцентний фіолетовий


# ── 1. Дифузія носіїв заряду в градієнті температур ─────────────────────────
def fig_carrier_diffusion():
    W, H = 840, 480
    f = [text(W / 2, 28, "Фізичний механізм ефекту Зеєбека: термодифузія носіїв заряду", size=16, bold=True)]

    # ── Верхня панель: n-тип (електрони) ──
    y_n = 55
    f.append(rect(20, y_n, 800, 190, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(40, y_n + 26, "Провідник n-типу (або метал з переважанням електронної провідності)", size=13.5, bold=True, color=INK, anchor="start"))
    
    # Тіло провідника з градієнтом температури (від x=180 до x=630)
    f.append(rect(180, y_n + 40, 450, 70, fill="#fcf3ed", stroke=LINE, sw=1.6, rx=4))
    f.append(rect(405, y_n + 40, 225, 70, fill="#edf2fa", stroke="none", rx=0))
    
    # Позначення зон обабіч бруска
    b_hot, _, _ = textbox(95, y_n + 75, "Гарячий кінець\nT_hot (швидкі e⁻)", size=11, fill="#fbeee6", stroke=POS, bold=True)
    b_cold, _, _ = textbox(735, y_n + 75, "Холодний кінець\nT_cold (повільні e⁻)", size=11, fill="#eef2f8", stroke=NEG, bold=True)
    f.append(b_hot)
    f.append(b_cold)

    # Носії: зліва багато розсіяних векторів швидкості, справа скупчення зарядів
    f.append(circle(220, y_n + 60, 6, fill="#eaf0fd", stroke=NEG, sw=1.2))
    f.append(text(220, y_n + 63, "−", size=10, bold=True, color=NEG))
    f.append(arrow(226, y_n + 60, 270, y_n + 60, color=NEG, sw=1.8))

    f.append(circle(280, y_n + 85, 6, fill="#eaf0fd", stroke=NEG, sw=1.2))
    f.append(text(280, y_n + 88, "−", size=10, bold=True, color=NEG))
    f.append(arrow(286, y_n + 85, 335, y_n + 85, color=NEG, sw=1.8))

    f.append(circle(345, y_n + 55, 6, fill="#eaf0fd", stroke=NEG, sw=1.2))
    f.append(text(345, y_n + 58, "−", size=10, bold=True, color=NEG))
    f.append(arrow(351, y_n + 55, 395, y_n + 55, color=NEG, sw=1.8))

    # Накопичення негативного заряду на холодному кінці
    f.append(circle(560, y_n + 58, 6, fill="#eaf0fd", stroke=NEG, sw=1.2))
    f.append(text(560, y_n + 61, "−", size=10, bold=True, color=NEG))
    f.append(circle(590, y_n + 82, 6, fill="#eaf0fd", stroke=NEG, sw=1.2))
    f.append(text(590, y_n + 85, "−", size=10, bold=True, color=NEG))
    f.append(circle(615, y_n + 60, 6, fill="#eaf0fd", stroke=NEG, sw=1.2))
    f.append(text(615, y_n + 63, "−", size=10, bold=True, color=NEG))
    f.append(circle(610, y_n + 92, 6, fill="#eaf0fd", stroke=NEG, sw=1.2))
    f.append(text(610, y_n + 95, "−", size=10, bold=True, color=NEG))

    # Нескомпенсований позитивний остов іонів на гарячому кінці
    f.append(circle(195, y_n + 60, 5, fill="#fdecea", stroke=POS, sw=1.2))
    f.append(text(195, y_n + 63, "+", size=9, bold=True, color=POS))
    f.append(circle(200, y_n + 90, 5, fill="#fdecea", stroke=POS, sw=1.2))
    f.append(text(200, y_n + 93, "+", size=9, bold=True, color=POS))

    # Стрілка термодифузійного потоку і стрілка поля
    f.append(arrow(280, y_n + 130, 480, y_n + 130, color=WARM, sw=2.2))
    f.append(text(380, y_n + 122, "Дифузійний потік гарячих електронів  →", size=11, bold=True, color=WARM))

    f.append(arrow(530, y_n + 155, 280, y_n + 155, color=FIELD, sw=2.2))
    f.append(text(405, y_n + 170, "Внутрішнє термоелектричне поле E_th  (зупиняє струм) ←", size=11, bold=True, color=FIELD))

    # Підсумок n-типу
    b_res_n, _, _ = textbox(405, y_n + 215, "Потенціал холодного кінця: V_cold < V_hot  →  коефіцієнт Зеєбека S < 0", size=11.5, fill="#edf2fa", stroke=NEG, bold=True)
    f.append(b_res_n)

    # ── Нижня панель: p-тип (дірки) ──
    y_p = 285
    f.append(rect(20, y_p, 800, 180, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(40, y_p + 26, "Напівпровідник p-типу (носії заряду — квазічастинки-дірки)", size=13.5, bold=True, color=INK, anchor="start"))

    f.append(rect(180, y_p + 40, 450, 65, fill="#fcf3ed", stroke=LINE, sw=1.6, rx=4))
    f.append(rect(405, y_p + 40, 225, 65, fill="#edf2fa", stroke="none", rx=0))

    b_hot_p, _, _ = textbox(95, y_p + 72, "Гарячий кінець\nT_hot (швидкі h⁺)", size=11, fill="#fbeee6", stroke=POS, bold=True)
    b_cold_p, _, _ = textbox(735, y_p + 72, "Холодний кінець\nT_cold (повільні h⁺)", size=11, fill="#eef2f8", stroke=NEG, bold=True)
    f.append(b_hot_p)
    f.append(b_cold_p)

    # Дірки дифундують на холодний кінець
    f.append(circle(230, y_p + 60, 6, fill="#fdecea", stroke=POS, sw=1.2))
    f.append(text(230, y_p + 63, "+", size=10, bold=True, color=POS))
    f.append(arrow(236, y_p + 60, 285, y_p + 60, color=POS, sw=1.8))

    f.append(circle(330, y_p + 80, 6, fill="#fdecea", stroke=POS, sw=1.2))
    f.append(text(330, y_p + 83, "+", size=10, bold=True, color=POS))
    f.append(arrow(336, y_p + 80, 385, y_p + 80, color=POS, sw=1.8))

    # Накопичення плюса на холодному кінці
    f.append(circle(570, y_p + 58, 6, fill="#fdecea", stroke=POS, sw=1.2))
    f.append(text(570, y_p + 61, "+", size=10, bold=True, color=POS))
    f.append(circle(600, y_p + 80, 6, fill="#fdecea", stroke=POS, sw=1.2))
    f.append(text(600, y_p + 83, "+", size=10, bold=True, color=POS))
    f.append(circle(620, y_p + 58, 6, fill="#fdecea", stroke=POS, sw=1.2))
    f.append(text(620, y_p + 61, "+", size=10, bold=True, color=POS))

    # Негативні іонізовані акцептори зліва
    f.append(circle(195, y_p + 65, 5, fill="#eaf0fd", stroke=NEG, sw=1.2))
    f.append(text(195, y_p + 68, "−", size=9, bold=True, color=NEG))
    f.append(circle(200, y_p + 88, 5, fill="#eaf0fd", stroke=NEG, sw=1.2))
    f.append(text(200, y_p + 91, "−", size=9, bold=True, color=NEG))

    # Поле дірок напрямлене вправо
    f.append(arrow(300, y_p + 125, 510, y_p + 125, color=FIELD, sw=2.2))
    f.append(text(405, y_p + 116, "Внутрішнє термоелектричне поле E_th →", size=11, bold=True, color=FIELD))

    b_res_p, _, _ = textbox(405, y_p + 158, "Потенціал холодного кінця: V_cold > V_hot  →  коефіцієнт Зеєбека S > 0", size=11.5, fill="#fdecea", stroke=POS, bold=True)
    f.append(b_res_p)

    render(os.path.join(IMG, "seebeck-carrier-diffusion.svg"), W, H, *f)


# ── 2. Диференціальна термо-ЕРС у колі двох різнорідних провідників ──────────
def fig_thermocouple_circuit():
    W, H = 820, 420
    f = [text(W / 2, 28, "Диференціальна термо-ЕРС у замкненому контурі двох матеріалів A і B", size=16, bold=True)]

    # Гарячий спай (T_h)
    f.append(circle(120, 200, 36, fill="#fbeee6", stroke=POS, sw=2.4))
    f.append(text(120, 194, "Спай 1", size=12.5, bold=True, color=POS))
    f.append(text(120, 212, "T_гарячий", size=12, bold=True, color=POS))

    # Провідник A (верхня гілка)
    f.append(line(120, 200, 600, 150, color="#b9770e", sw=5.0))
    b_mat_a, _, _ = textbox(360, 136, "Провідник A  (коефіцієнт Зеєбека S_A(T))", size=11.5, fill="#fef9e7", stroke="#b9770e", bold=True)
    f.append(b_mat_a)

    # Провідник B (нижня гілка)
    f.append(line(120, 200, 600, 250, color="#2980b9", sw=5.0))
    b_mat_b, _, _ = textbox(360, 264, "Провідник B  (коефіцієнт Зеєбека S_B(T))", size=11.5, fill="#ebf5fb", stroke="#2980b9", bold=True)
    f.append(b_mat_b)

    # Стрілки градієнта вздовж дротів
    f.append(arrow(180, 185, 260, 170, color=MUTED, sw=1.6))
    f.append(text(220, 160, "grad T", size=10, italic=True, color=MUTED))

    # Холодні спаї / виводи (T_c)
    f.append(rect(560, 85, 80, 230, fill="#edf2fa", stroke=NEG, sw=1.6, rx=6))
    f.append(text(600, 106, "Холодна зона", size=11, bold=True, color=NEG))
    f.append(text(600, 122, "T_холодний", size=11, bold=True, color=NEG))

    f.append(circle(600, 150, 7, fill=BG, stroke=LINE, sw=1.8))
    f.append(text(600, 153, "C₁", size=10, bold=True, color=INK))

    f.append(circle(600, 250, 7, fill=BG, stroke=LINE, sw=1.8))
    f.append(text(600, 253, "C₂", size=10, bold=True, color=INK))

    # Мідні дроти від холодного спаю до вимірювача (Cu, ізотермічні)
    f.append(line(600, 150, 700, 150, color=LINE, sw=2.0))
    f.append(line(700, 150, 700, 175, color=LINE, sw=2.0))

    f.append(line(600, 250, 700, 250, color=LINE, sw=2.0))
    f.append(line(700, 250, 700, 225, color=LINE, sw=2.0))

    # Вольтметр
    f.append(circle(700, 200, 24, fill="#f4f6f8", stroke=LINE, sw=2.0))
    f.append(text(700, 206, "V", size=18, bold=True, color=INK))

    # Формула внизу
    b_eq, _, _ = textbox(W / 2, 365, "V_AB = ∫ [T_c .. T_h] ( S_A(T) − S_B(T) ) dT\nТермо-ЕРС виникає об'ємно в тілі обох провідників вздовж градієнта, а не в точці контакту", size=12.5, fill=FILL, stroke=FIELD, bold=True)
    f.append(b_eq)

    render(os.path.join(IMG, "thermocouple-circuit-integral.svg"), W, H, *f)


# ── 3. Термоелектричний трикутник Зеєбека-Пельтьє-Томсона ──────────────────
def fig_thermoelectric_triangle():
    W, H = 820, 440
    f = [text(W / 2, 28, "Фундаментальний термоелектричний трикутник і співвідношення Кельвіна", size=16, bold=True)]

    # З'єднувальні лінії
    f.append(line(410, 100, 170, 310, color=LINE, sw=2.2))
    f.append(line(410, 100, 650, 310, color=LINE, sw=2.2))
    f.append(line(170, 310, 650, 310, color=LINE, sw=2.2))

    # Блок 1: Ефект Зеєбека (вгорі)
    b_seebeck = (
        rect(280, 50, 260, 86, fill="#fef9e7", stroke="#b9770e", sw=2.0, rx=8) +
        text(410, 76, "Ефект Зеєбека (S)", size=14, bold=True, color="#b9770e") +
        mtext(410, 96, ["Генерація ЕРС від градієнта T", "E_th = S · ∇T", "S = перенос ентропії зарядом"], size=11, color=INK)
    )
    f.append(b_seebeck)

    # Блок 2: Ефект Пельтьє (ліворуч внизу)
    b_peltier = (
        rect(40, 270, 260, 86, fill="#fbeee6", stroke=POS, sw=2.0, rx=8) +
        text(170, 296, "Ефект Пельтьє (Π)", size=14, bold=True, color=POS) +
        mtext(170, 316, ["Виділення/поглинання тепла на спаї", "Q_P = Π · I", "стрибок ентропії на межі"], size=11, color=INK)
    )
    f.append(b_peltier)

    # Блок 3: Ефект Томсона (праворуч внизу)
    b_thomson = (
        rect(520, 270, 260, 86, fill="#edf2fa", stroke=NEG, sw=2.0, rx=8) +
        text(650, 296, "Ефект Томсона (τ)", size=14, bold=True, color=NEG) +
        mtext(650, 316, ["Об'ємне тепло струму в grad T", "dQ_Th/dx = τ · I · (dT/dx)", "зміна теплоємності носіїв"], size=11, color=INK)
    )
    f.append(b_thomson)

    # Співвідношення Кельвіна вздовж ребер
    b_k1, _, _ = textbox(245, 185, "1-е співвідношення Кельвіна\nΠ = S · T", size=12, fill="#fdfefe", stroke=FIELD, bold=True)
    f.append(b_k1)

    b_k2, _, _ = textbox(575, 185, "2-е співвідношення Кельвіна\nτ = T · (dS / dT)", size=12, fill="#fdfefe", stroke=FIELD, bold=True)
    f.append(b_k2)

    b_k3, _, _ = textbox(410, 310, "dΠ/dT − (S_A − S_B) = τ_A − τ_B", size=11.5, fill="#fdfefe", stroke=MUTED, bold=True)
    f.append(b_k3)

    # Підпис внизу про Онзагера
    b_ons, _, _ = textbox(W / 2, 400, "Термодинамічне обґрунтування базується на симетрії кінетичних коефіцієнтів Онзагера (L_12 = L_21)", size=11.5, fill=FILL, stroke=LINE)
    f.append(b_ons)

    render(os.path.join(IMG, "thermoelectric-triangle.svg"), W, H, *f)


# ── 4. Термоелектрична добротність ZT і компроміс носіїв ───────────────────
def fig_figure_of_merit():
    W, H = 820, 440
    f = [text(W / 2, 28, "Термоелектрична добротність ZT: компроміс між S, σ та теплопровідністю κ", size=16, bold=True)]

    ox, oy = 90, 340
    ax_w, ax_h = 660, 240

    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))

    f.append(text(ox + ax_w / 2, oy + 42, "Концентрація носіїв заряду n (см⁻³)", size=12.5, bold=True, color=INK))
    f.append(mtext(ox - 54, oy - ax_h / 2, ["Властивості", "матеріалу"], size=11.5, color=INK))

    # Зони матеріалів
    f.append(rect(ox + 10, oy - ax_h + 10, 180, ax_h - 15, fill="#fdfefe", stroke="none"))
    f.append(text(ox + 100, oy - ax_h + 26, "Діелектрики / Легколеговані", size=10.5, color=MUTED))

    f.append(rect(ox + 220, oy - ax_h + 10, 220, ax_h - 15, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(ox + 330, oy - ax_h + 26, "Оптимум ZT (10¹⁹ – 10²⁰ см⁻³)", size=11, bold=True, color=FIELD))
    f.append(text(ox + 330, oy - ax_h + 44, "Bi₂Te₃, PbTe, SiGe", size=10.5, color=FIELD))

    f.append(rect(ox + 470, oy - ax_h + 10, 180, ax_h - 15, fill="#fdfefe", stroke="none"))
    f.append(text(ox + 560, oy - ax_h + 26, "Метали (n ~ 10²² – 10²³)", size=10.5, color=MUTED))

    # Криві:
    # 1. Seebeck S
    pts_s = []
    for x_rel in range(0, ax_w, 10):
        val = 220 - 180 * (x_rel / ax_w)**0.5
        pts_s.append("%.1f,%.1f" % (ox + x_rel, oy - val))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="6,4"/>' % (" ".join(pts_s), "#b9770e"))
    f.append(text(ox + 110, oy - 200, "Зеєбек |S| (падає)", size=11, bold=True, color="#b9770e"))

    # 2. Провідність sigma
    pts_sigma = []
    for x_rel in range(0, ax_w, 10):
        val = 15 + 210 * (x_rel / ax_w)**1.4
        pts_sigma.append("%.1f,%.1f" % (ox + x_rel, oy - val))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="4,3"/>' % (" ".join(pts_sigma), NEG))
    f.append(text(ox + 580, oy - 180, "Електропровідність σ (росте)", size=11, bold=True, color=NEG))

    # 3. Фактор потужності S^2 * sigma
    pts_pf = []
    for x_rel in range(0, ax_w, 10):
        t = x_rel / ax_w
        val = 200 * math.exp(-((t - 0.52)**2) / 0.04)
        pts_pf.append("%.1f,%.1f" % (ox + x_rel, oy - val))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="2,2"/>' % (" ".join(pts_pf), ACCENT))
    f.append(text(ox + 330, oy - 165, "Фактор потужності S²·σ", size=11, bold=True, color=ACCENT))

    # 4. Добротність ZT = S^2 sigma T / kappa
    pts_zt = []
    for x_rel in range(0, ax_w, 10):
        t = x_rel / ax_w
        val = 180 * math.exp(-((t - 0.48)**2) / 0.035)
        pts_zt.append("%.1f,%.1f" % (ox + x_rel, oy - val))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (" ".join(pts_zt), FIELD))
    f.append(text(ox + 330, oy - 210, "Добротність ZT (пік)", size=13, bold=True, color=FIELD))

    # Формула ZT внизу
    b_form, _, _ = textbox(W / 2, 405, "ZT = ( S² · σ · T ) / ( κ_електронна + κ_ґраткова )   —   метали мають малий S, ізолятори мають мізерну σ", size=12, fill=FILL, stroke=LINE, bold=True)
    f.append(b_form)

    render(os.path.join(IMG, "figure-of-merit-zt.svg"), W, H, *f)


# ── 5. Енергетичний баланс та елемент термоелектричного генератора (TEG) ─────
def fig_teg_energy_balance():
    W, H = 820, 460
    f = [text(W / 2, 28, "Енергетичний баланс термопари в режимі генератора енергії (TEG)", size=16, bold=True)]

    # Гарячий теплообмінник зверху (T_h)
    f.append(rect(140, 55, 540, 45, fill="#fbeee6", stroke=POS, sw=2.0, rx=6))
    f.append(text(410, 78, "Гарячий радіатор (Джерело тепла T_h)", size=13.5, bold=True, color=POS))
    f.append(arrow(410, 100, 410, 130, color=POS, sw=2.4))
    f.append(text(440, 118, "Тепловий потік Q_h", size=11, bold=True, color=POS))

    # Верхня сполучна мідна пластина (спай)
    f.append(rect(220, 130, 380, 20, fill="#d4ac0d", stroke=LINE, sw=1.6, rx=3))
    f.append(text(410, 144, "Гарячий контактний спай (мідна шина)", size=11, bold=True, color=INK))

    # Термоелемент p-типу (зліва)
    f.append(rect(240, 150, 120, 140, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    f.append(text(300, 180, "p-тип", size=15, bold=True, color=POS))
    f.append(text(300, 202, "S_p > 0", size=12, bold=True, color=POS))
    f.append(mtext(300, 230, ["струм дірок", "зверху вниз ↓"], size=10.5, color=INK))
    f.append(arrow(300, 245, 300, 275, color=POS, sw=2.2))

    # Термоелемент n-типу (справа)
    f.append(rect(460, 150, 120, 140, fill="#edf2fa", stroke=NEG, sw=1.8, rx=4))
    f.append(text(520, 180, "n-тип", size=15, bold=True, color=NEG))
    f.append(text(520, 202, "S_n < 0", size=12, bold=True, color=NEG))
    f.append(mtext(520, 230, ["струм e⁻ вгору", "струм I вниз ↓"], size=10.5, color=INK))
    f.append(arrow(520, 245, 520, 275, color=NEG, sw=2.2))

    # Внутрішні теплові процеси в ніжках
    b_proc, _, _ = textbox(410, 215, "Втрати в ніжках:\n• Теплопровідність K·ΔT\n• Джоулеве тепло I²·R_int\n• Тепло Томсона", size=10.5, fill=BG, stroke=MUTED)
    f.append(b_proc)

    # Нижні контактні пластини
    f.append(rect(220, 290, 140, 20, fill="#d4ac0d", stroke=LINE, sw=1.6, rx=3))
    f.append(rect(460, 290, 140, 20, fill="#d4ac0d", stroke=LINE, sw=1.6, rx=3))

    # Холодний теплообмінник знизу (T_c)
    f.append(rect(140, 310, 540, 45, fill="#edf2fa", stroke=NEG, sw=2.0, rx=6))
    f.append(text(410, 334, "Холодний радіатор (Стік тепла T_c)", size=13.5, bold=True, color=NEG))
    f.append(arrow(410, 355, 410, 385, color=NEG, sw=2.4))
    f.append(text(440, 372, "Скинуте тепло Q_c", size=11, bold=True, color=NEG))

    # Зовнішнє коло з навантаженням
    f.append(line(240, 300, 100, 300, color=LINE, sw=2.0))
    f.append(line(100, 300, 100, 395, color=LINE, sw=2.0))

    f.append(line(580, 300, 720, 300, color=LINE, sw=2.0))
    f.append(line(720, 300, 720, 395, color=LINE, sw=2.0))

    f.append(line(100, 395, 340, 395, color=LINE, sw=2.0))
    f.append(line(480, 395, 720, 395, color=LINE, sw=2.0))

    # Навантаження R_load
    f.append(rect(340, 375, 140, 40, fill="#e8f8f5", stroke=FIELD, sw=2.0, rx=6))
    f.append(text(410, 395, "Навантаження R_L", size=12, bold=True, color=FIELD))
    f.append(text(410, 410, "P_max при R_L = R_int", size=10, bold=True, color=FIELD))

    # Стрілка струму в колі
    f.append(arrow(200, 395, 160, 395, color=FIELD, sw=2.2))
    f.append(text(180, 414, "Струм I", size=10.5, bold=True, color=FIELD))

    # Підсумковий баланс
    b_bal, _, _ = textbox(W / 2, 435, "Корисна електрична потужність: P_el = Q_h − Q_c = I²·R_L = V_oc² / (4·R_int)  [при узгодженні]", size=11.5, fill=FILL, stroke=LINE)
    f.append(b_bal)

    render(os.path.join(IMG, "teg-energy-balance.svg"), W, H, *f)


if __name__ == "__main__":
    fig_carrier_diffusion()
    fig_thermocouple_circuit()
    fig_thermoelectric_triangle()
    fig_figure_of_merit()
    fig_teg_energy_balance()
    print("OK: 5 SVG figures generated ->", IMG)
