# -*- coding: utf-8 -*-
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Зонні діаграми МДН-структури (Плоскі зони, Збіднення, Сильна інверсія)
# ════════════════════════════════════════════════════════════════════════════
def fig_band_bending():
    W, H = 840, 480
    f = []

    # Три панелі з рівною шириною
    w_p = 260
    h_p = 400
    y_top = 50

    x_offsets = [20, 290, 560]
    titles = ["a) Плоскі зони (V_G = V_FB)", "b) Збіднення (V_FB < V_G < V_th)", "c) Сильна інверсія (V_G > V_th)"]
    subtitles = ["Поле відсутнє", "Неосновні носії відштовхнуті", "Утворено n-канал (E_F > E_i)"]

    for i in range(3):
        xo = x_offsets[i]
        
        # Тло панелі
        f.append(rect(xo, y_top, w_p, h_p, fill="#fafafa", stroke="#d5dbdb", sw=1.0))
        
        # Область металу (Gate), діелектрика (SiO2), напівпровідника (p-Si)
        f.append(rect(xo + 5, y_top + 30, 35, h_p - 45, fill="#d5d8dc", stroke="none"))
        f.append(rect(xo + 40, y_top + 30, 45, h_p - 45, fill="#e8f8f5", stroke="none"))
        f.append(rect(xo + 85, y_top + 30, 165, h_p - 45, fill="#ebf5fb", stroke="none"))

        # Межі розділу
        f.append(line(xo + 40, y_top + 30, xo + 40, y_top + h_p - 15, color="#7f8c8d", sw=1.5))
        f.append(line(xo + 85, y_top + 30, xo + 85, y_top + h_p - 15, color="#2980b9", sw=1.8))

        # Заголовки панелей
        f.append(text(xo + w_p // 2, y_top + 18, titles[i], size=11.5, bold=True, color="#1b4f72"))
        f.append(text(xo + w_p // 2, y_top + 32, subtitles[i], size=9.5, color="#566573"))

        # Підписи матеріалів зверху
        if i == 0:
            f.append(text(xo + 22, y_top + 45, "M", size=10, bold=True, color="#2c3e50"))
            f.append(text(xo + 62, y_top + 45, "SiO₂", size=10, bold=True, color="#16a085"))
            f.append(text(xo + 160, y_top + 45, "p-Si (об'єм)", size=10.5, bold=True, color="#1b4f72"))

        # Постійний рівень Фермі E_F
        ef_y = y_top + 230
        f.append(line(xo + 10, ef_y, xo + 245, ef_y, color="#7d3c98", sw=1.5, dash="5 3"))

        # Будуємо зони E_c, E_v, E_i залежно від режиму
        if i == 0:
            # Flatband
            ec_y = y_top + 110
            ev_y = y_top + 330
            ei_y = (ec_y + ev_y) // 2

            f.append(line(xo + 85, ec_y, xo + 245, ec_y, color="#c0392b", sw=2.0))
            f.append(line(xo + 85, ev_y, xo + 245, ev_y, color="#27ae60", sw=2.0))
            f.append(line(xo + 85, ei_y, xo + 245, ei_y, color="#7f8c8d", sw=1.2, dash="3 3"))

            f.append(text(xo + 215, ec_y - 6, "E_c", size=10.5, bold=True, color="#c0392b"))
            f.append(text(xo + 215, ei_y - 6, "E_i", size=10.5, bold=True, color="#7f8c8d"))
            f.append(text(xo + 215, ev_y + 14, "E_v", size=10.5, bold=True, color="#27ae60"))
            f.append(text(xo + 215, ef_y - 6, "E_F", size=10.5, bold=True, color="#7d3c98"))

        elif i == 1:
            # Depletion
            bend = 65
            pts_ec, pts_ev, pts_ei = [], [], []
            for x in range(xo + 85, xo + 246, 2):
                dx = x - (xo + 85)
                if dx < 90:
                    b = bend * ((1.0 - dx / 90.0)**2)
                else:
                    b = 0.0
                pts_ec.append((x, y_top + 110 + b))
                pts_ev.append((x, y_top + 330 + b))
                pts_ei.append((x, y_top + 220 + b))

            f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_ec), stroke="#c0392b", sw=2.0))
            f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_ev), stroke="#27ae60", sw=2.0))
            f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_ei), stroke="#7f8c8d", sw=1.2, dash="3 3"))

            f.append(text(xo + 215, y_top + 104, "E_c", size=10.5, bold=True, color="#c0392b"))
            f.append(text(xo + 215, y_top + 214, "E_i", size=10.5, bold=True, color="#7f8c8d"))
            f.append(text(xo + 215, y_top + 344, "E_v", size=10.5, bold=True, color="#27ae60"))

            # Позначка збідненого шару W_d
            f.append(rect(xo + 85, y_top + 345, 90, 30, fill="#f9ebea", stroke="none"))
            f.append(text(xo + 130, y_top + 363, "Збіднений шар (W_d)", size=9.5, bold=True, color="#c0392b"))

            # Стрілка поверхневого потенціалу psi_s
            f.append(line(xo + 80, y_top + 220, xo + 80, y_top + 220 + bend, color="#d35400", sw=1.2))
            f.append(text(xo + 60, y_top + 220 + bend // 2, "q·ψ_s", size=10, bold=True, color="#d35400"))

        else:
            # Strong Inversion
            bend = 125
            pts_ec, pts_ev, pts_ei = [], [], []
            for x in range(xo + 85, xo + 246, 2):
                dx = x - (xo + 85)
                if dx < 100:
                    b = bend * ((1.0 - dx / 100.0)**2)
                else:
                    b = 0.0
                pts_ec.append((x, y_top + 110 + b))
                pts_ev.append((x, y_top + 330 + b))
                pts_ei.append((x, y_top + 220 + b))

            f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_ec), stroke="#c0392b", sw=2.2))
            f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_ev), stroke="#27ae60", sw=2.2))
            f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_ei), stroke="#7f8c8d", sw=1.2, dash="3 3"))

            # Виділення інверсійного n-каналу (під E_F біля поверхні)
            pts_inv = [(xo + 85, y_top + 110 + bend)]
            for p in pts_ec[:15]:
                pts_inv.append(p)
            pts_inv.append((pts_ec[14][0], ef_y))
            pts_inv.append((xo + 85, ef_y))
            f.append(polygon(pts_inv, fill="#f5b041"))

            f.append(text(xo + 92, ef_y + 15, "Інверсійний n-канал", size=9.5, bold=True, color="#900c3f"))
            f.append(text(xo + 92, ef_y + 27, "(електрони n_s)", size=9.0, color="#900c3f"))

            f.append(text(xo + 215, y_top + 104, "E_c", size=10.5, bold=True, color="#c0392b"))
            f.append(text(xo + 215, y_top + 214, "E_i", size=10.5, bold=True, color="#7f8c8d"))
            f.append(text(xo + 215, y_top + 344, "E_v", size=10.5, bold=True, color="#27ae60"))

            # Перетин E_i та E_F
            f.append(circle(xo + 85 + 42, ef_y, 4, fill="#e74c3c", stroke="none"))
            f.append(text(xo + 135, ef_y - 10, "E_i = E_F", size=9.5, bold=True, color="#e74c3c"))

            # Позначка psi_s >= 2*psi_B
            f.append(line(xo + 77, y_top + 220, xo + 77, y_top + 220 + bend, color="#c0392b", sw=1.5))
            f.append(text(xo + 48, y_top + 220 + bend // 2, "q·ψ_s ≥ 2qψ_B", size=9.5, bold=True, color="#c0392b"))

    render(os.path.join(OUT, "inversion-band-bending.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Залежність поверхневого заряду Q_sc від поверхневого потенціалу ψ_s
# ════════════════════════════════════════════════════════════════════════════
def fig_charge_potential():
    W, H = 820, 440
    f = []

    f.append(text(W // 2, 25, "Розподіл поверхневого заряду |Q_sc| від потенціалу ψ_s", size=14, bold=True, color=DARK))
    f.append(text(W // 2, 43, "Перехід від збіднення (√ψ_s) до сильної інверсії (exp(qψ_s / 2k_BT))", size=11, color="#566573"))

    ox, oy = 90, 360
    w_ax, h_ax = 680, 280

    # Осі координат
    f.append(line(ox, oy, ox + w_ax, oy, color=DARK, sw=1.5))
    f.append(line(ox, oy, ox, oy - h_ax, color=DARK, sw=1.5))
    f.append(polygon([(ox + w_ax, oy - 4), (ox + w_ax + 10, oy), (ox + w_ax, oy + 4)], fill=DARK))
    f.append(polygon([(ox - 4, oy - h_ax), (ox, oy - h_ax - 10), (ox + 4, oy - h_ax)], fill=DARK))

    f.append(text(ox + w_ax - 20, oy + 30, "Поверхневий потенціал ψ_s (В)", size=11.5, bold=True, color=DARK))
    f.append(text(ox - 50, oy - h_ax + 10, "|Q_sc| (Кл/см²)", size=11.5, bold=True, color=DARK))

    # Вертикальні пунктирні лінії важливих точок
    x_fb = ox + 120
    x_mid = ox + 320
    x_th = ox + 490

    f.append(line(x_fb, oy, x_fb, oy - h_ax + 20, color="#7f8c8d", sw=1.2, dash="4 4"))
    f.append(line(x_mid, oy, x_mid, oy - h_ax + 20, color="#7f8c8d", sw=1.2, dash="4 4"))
    f.append(line(x_th, oy, x_th, oy - h_ax + 20, color="#c0392b", sw=1.8, dash="5 3"))

    f.append(text(x_fb, oy + 18, "0 (Flatband)", size=10.5, bold=True, color="#7f8c8d"))
    f.append(text(x_mid, oy + 18, "ψ_B (Початок інверсії)", size=10.5, bold=True, color="#7f8c8d"))
    f.append(text(x_th, oy + 18, "2ψ_B (Поріг інверсії)", size=11, bold=True, color="#c0392b"))

    # Зони режимів
    f.append(rect(ox + 5, oy - h_ax + 30, x_fb - (ox + 5), 230, fill="#fcf3cf", stroke="none"))
    f.append(rect(x_fb, oy - h_ax + 30, x_mid - x_fb, 230, fill="#ebf5fb", stroke="none"))
    f.append(rect(x_mid, oy - h_ax + 30, x_th - x_mid, 230, fill="#f5eeea", stroke="none"))
    f.append(rect(x_th, oy - h_ax + 30, ox + w_ax - x_th - 10, 230, fill="#fadbd8", stroke="none"))

    f.append(text((ox + x_fb) // 2, oy - h_ax + 45, "Накопичення", size=10.5, bold=True, color="#b7950b"))
    f.append(text((x_fb + x_mid) // 2, oy - h_ax + 45, "Збіднення", size=10.5, bold=True, color="#2980b9"))
    f.append(text((x_mid + x_th) // 2, oy - h_ax + 45, "Слабка інверсія", size=10.5, bold=True, color="#d35400"))
    f.append(text((x_th + ox + w_ax) // 2, oy - h_ax + 45, "СИЛЬНА ІНВЕРСІЯ", size=11, bold=True, color="#78281f"))

    # Крива заряду збіднення Q_d ∝ √ψ_s
    pts_qd = []
    for x in range(x_fb, ox + w_ax - 20, 2):
        psi = (x - x_fb) / (x_th - x_fb) * 2.0
        val = 60 * math.sqrt(max(0, psi))
        pts_qd.append((x, oy - val))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_qd), stroke="#2980b9", sw=1.8, dash="4 3"))
    f.append(text(x_th - 70, oy - 95, "Заряд збіднення Q_d ∝ √ψ_s", size=10, bold=True, color="#2980b9"))

    # Загальна крива |Q_sc| з експоненційним підйомом в інверсії
    pts_qsc = []
    # Накопичення (ліворуч від x_fb)
    for x in range(ox + 10, x_fb, 2):
        dx = (x_fb - x) / 30.0
        val = 10 * math.exp(dx)
        pts_qsc.append((x, oy - val))
    # Збіднення та слабка інверсія
    for x in range(x_fb, x_th, 2):
        psi = (x - x_fb) / (x_th - x_fb) * 2.0
        q_d = 60 * math.sqrt(psi)
        q_n = 0.5 * math.exp((psi - 1.0) * 3.2)
        val = q_d + q_n
        pts_qsc.append((x, oy - val))
    # Сильна інверсія (різкий експоненційний підйом)
    for x in range(x_th, ox + w_ax - 40, 2):
        d_psi = (x - x_th) / 50.0
        q_d = 60 * math.sqrt(2.0 + d_psi * 0.2)
        q_n = 25 * math.exp(d_psi * 1.8)
        val = min(h_ax - 20, q_d + q_n)
        pts_qsc.append((x, oy - val))

    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_qsc), stroke="#c0392b", sw=2.8))
    f.append(text(x_th + 60, oy - 210, "Повний заряд |Q_sc| = |Q_d + Q_n|", size=11, bold=True, color="#c0392b"))
    f.append(text(x_th + 60, oy - 192, "Q_n ∝ exp(qψ_s / 2k_BT)", size=10.5, color="#900c3f"))

    render(os.path.join(OUT, "inversion-charge-potential.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Квантова потенціальна яма інверсійного шару (2DEG у MOSFET)
# ════════════════════════════════════════════════════════════════════════════
def fig_quantum_well():
    W, H = 820, 450
    f = []

    f.append(text(W // 2, 25, "Квантування електронів у трикутній ямі інверсійного каналу", size=14, bold=True, color=DARK))
    f.append(text(W // 2, 43, "Поперечний рух обмежений товщиною z_inv ≈ 2–3 нм < λ_dB", size=11, color="#566573"))

    ox, oy = 100, 370
    w_ax, h_ax = 660, 300

    # Оксидна стінка (SiO2) та напівпровідник (Si)
    f.append(rect(20, 60, 80, oy - 60, fill="#e8f8f5", stroke="none"))
    f.append(line(ox, 60, ox, oy, color="#16a085", sw=2.2))
    f.append(text(55, 100, "SiO₂", size=13, bold=True, color="#16a085"))
    f.append(text(55, 120, "(Бар'єр V₀ = 3.1 еВ)", size=9.5, color="#117864"))

    # Осі
    f.append(line(ox, oy, ox + w_ax, oy, color=DARK, sw=1.5))
    f.append(line(ox, oy, ox, 60, color=DARK, sw=1.5))
    f.append(polygon([(ox + w_ax, oy - 4), (ox + w_ax + 10, oy), (ox + w_ax, oy + 4)], fill=DARK))
    f.append(polygon([(ox - 4, 60), (ox, 50), (ox + 4, 60)], fill=DARK))

    f.append(text(ox + w_ax - 30, oy + 25, "Відстань від межі z (нм)", size=11.5, bold=True, color=DARK))
    f.append(text(ox - 45, 55, "Енергія E", size=11.5, bold=True, color=DARK))

    # Дно зони провідності E_c(z) - трикутна потенціальна яма
    pts_ec = []
    for z in range(0, 550, 2):
        dz = z / 50.0
        if dz < 2.5:
            y_val = oy - 260 + 90 * (dz**0.85)
        else:
            y_val = oy - 90 + 20 * (1.0 - math.exp(-(dz - 2.5) / 3.0))
        pts_ec.append((ox + z, y_val))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_ec), stroke="#2980b9", sw=2.5))
    f.append(text(ox + 350, oy - 65, "E_c(z) (Електростатичний потенціал)", size=11, bold=True, color="#2980b9"))

    # Рівень Фермі E_F
    ef_y = oy - 180
    f.append(line(ox, ef_y, ox + 550, ef_y, color="#7d3c98", sw=1.5, dash="5 3"))
    f.append(text(ox + 460, ef_y - 8, "E_F (Рівень Фермі)", size=11, bold=True, color="#7d3c98"))

    # Дискретні підзони E₀ та E₁
    e0_y = oy - 210
    e1_y = oy - 145

    f.append(line(ox, e0_y, ox + 140, e0_y, color="#c0392b", sw=1.8))
    f.append(line(ox, e1_y, ox + 280, e1_y, color="#d35400", sw=1.8))

    f.append(text(ox + 145, e0_y + 4, "E₀ (Перша підзона)", size=10.5, bold=True, color="#c0392b"))
    f.append(text(ox + 285, e1_y + 4, "E₁ (Друга підзона)", size=10.5, bold=True, color="#d35400"))

    # Огидна функція густості електронів |ψ₀(z)|²
    pts_psi0 = []
    for z in range(0, 220, 2):
        dz = z / 25.0
        psi_val = (dz**2) * math.exp(-dz * 1.4) * 110.0
        pts_psi0.append((ox + z, e0_y - psi_val))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts_psi0), stroke="#e74c3c", sw=2.2))
    
    # Заповнення області хвильової функції |ψ₀|²
    pts_fill_psi = [(ox, e0_y)] + pts_psi0 + [(ox + 220, e0_y)]
    f.append(polygon(pts_fill_psi, fill="#fadbd8"))
    f.append(text(ox + 60, e0_y - 45, "|ψ₀(z)|²", size=11, bold=True, color="#c0392b"))

    # Товщина інверсійного каналу z_inv
    f.append(line(ox, oy - 20, ox + 95, oy - 20, color="#27ae60", sw=1.5))
    f.append(line(ox, oy - 15, ox, oy - 25, color="#27ae60", sw=1.5))
    f.append(line(ox + 95, oy - 15, ox + 95, oy - 25, color="#27ae60", sw=1.5))
    f.append(text(ox + 15, oy - 30, "z_inv ≈ 2–3 нм", size=10.5, bold=True, color="#27ae60"))

    # Стрілка поперечного електричного поля F_s
    f.append(line(ox + 20, oy - 240, ox + 180, oy - 240, color="#8e44ad", sw=1.8))
    f.append(polygon([(ox + 20, oy - 240), (ox + 30, oy - 244), (ox + 30, oy - 236)], fill="#8e44ad"))
    f.append(text(ox + 40, oy - 248, "Поперечне поле F_s ~ 10⁶ В/см", size=10.5, bold=True, color="#8e44ad"))

    render(os.path.join(OUT, "inversion-quantum-well.svg"), W, H, *f)

if __name__ == '__main__':
    fig_band_bending()
    fig_charge_potential()
    fig_quantum_well()
    print("All inversion-layer figures generated successfully.")
