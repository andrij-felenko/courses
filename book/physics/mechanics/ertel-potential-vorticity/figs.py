# -*- coding: utf-8 -*-
"""Фігури до теми «Потенціальна вихореність Ертеля».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def head_at(x, y, dx, dy, color=INK, size=10):
    """Наконечник стрілки у точці (x,y), напрям (dx,dy)."""
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    bx, by = x - ux * size, y - uy * size
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.4, head=11):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


# ── Фігура 1: Розтягнення та стискання стовпчика між поверхнями θ ─────────────
def fig_column_stretching():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Збереження вихореності Ертеля: розтягнення збільшує вихор, стискання — зменшує",
                  size=15, bold=True))

    # ── ЛІВА СТОРОНА: Розтягнутий високий стовпчик (h1 велике -> ∇θ малий -> ωa велика) ──
    xL = 170
    yTop1 = 90
    yBot1 = 310
    h1 = yBot1 - yTop1 # 220
    r1 = 34

    # Поверхня θ2 (верхня)
    f.append(polyline([(xL - 100, yTop1 - 10), (xL + 100, yTop1 + 10)], color=FIELD, sw=2, dash="6 4"))
    f.append(text(xL + 106, yTop1 + 14, "θ₂ = θ + Δθ", size=12, bold=True, color=FIELD, anchor="start"))

    # Поверхня θ1 (нижня)
    f.append(polyline([(xL - 100, yBot1 - 10), (xL + 100, yBot1 + 10)], color=FIELD, sw=2, dash="6 4"))
    f.append(text(xL + 106, yBot1 - 6, "θ₁ = θ", size=12, bold=True, color=FIELD, anchor="start"))

    # Стовпчик (циліндр)
    f.append(rect(xL - r1, yTop1, 2 * r1, h1, fill="#eef3fa", stroke=MUTED, sw=1.6, rx=4))

    # Стрілка вихореності ω_a1 (висока)
    f.append(varrow(xL, yBot1 - 15, xL, yTop1 - 35, color=POS, sw=3.5, head=12))
    f.append(text(xL + 12, yTop1 - 25, "ω_a (велика)", size=13, bold=True, color=POS, anchor="start"))

    # Виноска висоти h1
    f.append(line(xL - r1 - 20, yTop1, xL - r1 - 20, yBot1, color=INK, sw=1.4))
    f.append(line(xL - r1 - 26, yTop1, xL - r1 - 14, yTop1, color=INK, sw=1.4))
    f.append(line(xL - r1 - 26, yBot1, xL - r1 - 14, yBot1, color=INK, sw=1.4))
    f.append(text(xL - r1 - 30, (yTop1 + yBot1) / 2 + 4, "h₁", size=14, bold=True, anchor="end"))

    # Підпис лівого стану
    f.append(fitbox(xL - 90, 335, 180, 52, "Розтягнення:\n∇θ мали́й (широкий шар)\n→ ω_a зростає",
                    size=12, pad=7, fill="#eef6ef", stroke=POS, sw=1.3, bold=True))

    # ── ПРАВА СТОРОНА: Стиснутий низький стовпчик (h2 мале -> ∇θ великий -> ωa мала) ──
    xR = 560
    yTop2 = 160
    yBot2 = 250
    h2 = yBot2 - yTop2 # 90
    r2 = 54 # ширший за радіусом за збереженням маси

    # Поверхня θ2 (верхня)
    f.append(polyline([(xR - 120, yTop2 - 10), (xR + 120, yTop2 + 10)], color=FIELD, sw=2, dash="6 4"))
    f.append(text(xR + 126, yTop2 + 14, "θ₂ = θ + Δθ", size=12, bold=True, color=FIELD, anchor="start"))

    # Поверхня θ1 (нижня)
    f.append(polyline([(xR - 120, yBot2 - 10), (xR + 120, yBot2 + 10)], color=FIELD, sw=2, dash="6 4"))
    f.append(text(xR + 126, yBot2 - 6, "θ₁ = θ", size=12, bold=True, color=FIELD, anchor="start"))

    # Стовпчик (циліндр)
    f.append(rect(xR - r2, yTop2, 2 * r2, h2, fill="#fdf4f2", stroke=MUTED, sw=1.6, rx=4))

    # Стрілка вихореності ω_a2 (коротка)
    f.append(varrow(xR, yBot2 - 10, xR, yTop2 - 15, color=NEG, sw=2.8, head=10))
    f.append(text(xR + 12, yTop2 - 10, "ω_a (мала)", size=13, bold=True, color=NEG, anchor="start"))

    # Виноска висоти h2
    f.append(line(xR - r2 - 20, yTop2, xR - r2 - 20, yBot2, color=INK, sw=1.4))
    f.append(line(xR - r2 - 26, yTop2, xR - r2 - 14, yTop2, color=INK, sw=1.4))
    f.append(line(xR - r2 - 26, yBot2, xR - r2 - 14, yBot2, color=INK, sw=1.4))
    f.append(text(xR - r2 - 30, (yTop2 + yBot2) / 2 + 4, "h₂", size=14, bold=True, anchor="end"))

    # Підпис правого стану
    f.append(fitbox(xR - 90, 335, 180, 52, "Стискання:\n∇θ вели́кий (вузький шар)\n→ ω_a зменшується",
                    size=12, pad=7, fill="#fdecea", stroke=NEG, sw=1.3, bold=True))

    # Стрілка переходу посередині
    f.append(varrow(xL + 110, 200, xR - 130, 200, color=LINE, sw=2.5, head=11))
    f.append(text((xL + xR) / 2 - 10, 186, "стискання", size=12, bold=True, color=MUTED))

    # Нижній загальний підсумок
    b, w, h = textbox(W / 2, 400, "q = (ω_a · ∇θ) / ρ = const   —   абсолютний інваріант адіабатичного плину",
                      size=13, pad=8, fill=FILL, stroke=INK, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "ertel-column-stretching.svg"), W, H, *f)


# ── Фігура 2: Нахил вихореності у бароклінній зоні ───────────────────────────
def fig_vortex_tilting():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Векторний добуток: проєкція вихореності на нахилені ізоентропійні поверхні",
                  size=15, bold=True))

    cx, cy = 340, 220

    # Нахилені поверхні потенціальної температури θ
    angle_deg = 25
    ang = math.radians(angle_deg)
    cos_a, sin_a = math.cos(ang), math.sin(ang)

    for offset in (-70, 0, 70):
        # Перпендикулярний зсув
        ox, oy = -offset * sin_a, -offset * cos_a
        x1, y1 = cx + ox - 240 * cos_a, cy + oy + 240 * sin_a
        x2, y2 = cx + ox + 240 * cos_a, cy + oy - 240 * sin_a
        f.append(line(x1, y1, x2, y2, color=FIELD, sw=2, dash="6 4"))

    f.append(text(cx + 170 * cos_a - 70 * sin_a + 10, cy - 170 * sin_a - 70 * cos_a, "θ + Δθ", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(text(cx + 170 * cos_a + 10, cy - 170 * sin_a, "θ", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(text(cx + 170 * cos_a + 70 * sin_a + 10, cy - 170 * sin_a + 70 * cos_a, "θ − Δθ", size=12, bold=True, color=FIELD, anchor="start"))

    # Напрямок ∇θ (ортогональний до поверхонь θ, вгору-ліворуч)
    grad_len = 110
    gx, gy = -grad_len * sin_a, -grad_len * cos_a
    f.append(varrow(cx, cy, cx + gx, cy + gy, color=POS, sw=3, head=12))
    f.append(text(cx + gx - 14, cy + gy - 8, "∇θ (градієнт стратифікації)", size=13, bold=True, color=POS, anchor="end"))

    # Вектор абсолютної вихореності ω_a (вертикальний чи трохи нахилений)
    w_len = 130
    wx, wy = 25, -w_len # злегка відхилений від строгої вертикалі
    f.append(varrow(cx, cy, cx + wx, cy + wy, color=NEG, sw=3.2, head=12))
    f.append(text(cx + wx + 12, cy + wy + 4, "ω_a (абсолютна вихореність)", size=13, bold=True, color=NEG, anchor="start"))

    # Проєкція ω_a на ∇θ (скалярний добуток)
    proj_val = (wx * gx + wy * gy) / grad_len
    px, py = -proj_val * sin_a, -proj_val * cos_a
    f.append(line(cx + wx, cy + wy, cx + px, cy + py, color=MUTED, sw=1.4, dash="4 3"))
    f.append(line(cx, cy, cx + px, cy + py, color=INK, sw=4))
    f.append(text(cx + px / 2 - 20, cy + py / 2, "ω_a · n̂", size=12, bold=True, color=INK, anchor="end"))

    # Правий пояснювальний блок
    f.append(fitbox(540, 110, 215, 75, "Бароклінний шар:\nповерхні θ нахилені\nчерез горизонтальний\nградієнт температури",
                    size=12, pad=8, fill="#eef1fb", stroke=FIELD, sw=1.3, bold=True))

    f.append(fitbox(540, 205, 215, 80, "Скалярний добуток:\nq = (ω_a · ∇θ) / ρ\nвраховує лише складову,\nперпендикулярну до θ",
                    size=12, pad=8, fill="#eef6ef", stroke=POS, sw=1.3, bold=True))

    b, w, h = textbox(W / 2, 400, "Нахил поверхонь θ пов'язує горизонтальний зсув вітру із потенціальною вихореністю",
                      size=12, pad=8, fill=FILL, stroke=INK, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "vortex-tilting-baroclinic.svg"), W, H, *f)


# ── Фігура 3: Вторгнення стратосферного повітря (Tropopause Fold) ────────────
def fig_tropopause_fold():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Атмосферна складка тропопаузи: аномалія PV понад 2 PVU діє як рушій циклогенезу",
                  size=15, bold=True))

    # Схема меридіонального розрізу (Широта по х, Висота по у)
    fold_pts = [
        (60, 100), (220, 110), (320, 140),
        (380, 270), (410, 290), (430, 240), # Язик вторгнення
        (460, 160), (600, 130), (720, 120)
    ]

    # Фон стратосфери (верх)
    strat_poly = [(60, 50)] + fold_pts + [(720, 50)]
    p_str = " ".join("%.1f,%.1f" % (x, y) for (x, y) in strat_poly)
    f.append('<polygon points="%s" fill="#e8edf8" stroke="none"/>' % p_str)

    # Фон тропосфери (низ)
    trop_poly = [(60, 350)] + fold_pts + [(720, 350)]
    p_trp = " ".join("%.1f,%.1f" % (x, y) for (x, y) in trop_poly)
    f.append('<polygon points="%s" fill="#fcf6ed" stroke="none"/>' % p_trp)

    # Лінія тропопаузи
    f.append(polyline(fold_pts, color=NEG, sw=3))
    f.append(text(200, 95, "Тропопауза (2 PVU)", size=12, bold=True, color=NEG))

    # Написи регіонів
    f.append(text(200, 70, "Стратосфера (висока PV: q > 2–8 PVU)", size=13, bold=True, color=FIELD))
    f.append(text(180, 240, "Тропосфера (низька PV: q < 1 PVU)", size=13, bold=True, color=POS))

    # Стрілка вторгнення сухої стратосферної аномалії
    f.append(varrow(340, 130, 395, 260, color=NEG, sw=3, head=11))
    f.append(text(435, 270, "Стратосферне язик-вторгнення\n(High PV anomaly)", size=12, bold=True, color=NEG, anchor="start"))

    # Наслідок на поверхні Землі: циклонічний вихор (низький тиск L)
    f.append(line(60, 350, 720, 350, color=INK, sw=2)) # Поверхня Землі
    f.append(text(390, 370, "Поверхня Землі", size=12, color=MUTED))

    # Низький тиск L під аномалією
    f.append(circle(400, 330, 16, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(400, 335, "L", size=16, bold=True, color=POS))
    f.append(text(480, 335, "Приземний циклон (індукований вихор)", size=12, bold=True, color=POS, anchor="start"))

    # Циклонічні стрілки циркуляції на поверхні
    f.append(varrow(340, 345, 370, 345, color=POS, sw=2, head=8))
    f.append(varrow(460, 320, 430, 320, color=POS, sw=2, head=8))

    b, w, h = textbox(W / 2, 400, "1 PVU = 10⁻⁶ м²·с⁻¹·К·кг⁻¹   —   стандартна одиниця потенціальної вихореності",
                      size=12, pad=8, fill=FILL, stroke=INK, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "tropopause-fold-pv.svg"), W, H, *f)


# ── Фігура 4: Схема принципу оберненості (PV Invertibility Loop) ───────────────
def fig_invertibility_loop():
    W, H = 780, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Принцип оберненості: від поля PV до повної динаміки атмосфери",
                  size=15, bold=True))

    # Блоки циклу
    bx1, by1 = 80, 130
    f.append(fitbox(bx1, by1, 170, 80, "1. Поле PV q(x,y,z)\n+ граничні умови θ\n(динамічне ДНК)",
                    size=12, pad=8, fill="#eef1fb", stroke=FIELD, sw=1.6, bold=True))

    bx2, by2 = 305, 130
    f.append(fitbox(bx2, by2, 170, 80, "2. Обернення (PDE):\n∇²ψ + (f²/N²)ψ_zz = q′\n(геострофічний баланс)",
                    size=12, pad=8, fill="#eef6ef", stroke=POS, sw=1.6, bold=True))

    bx3, by3 = 530, 130
    f.append(fitbox(bx3, by3, 170, 80, "3. Функція току ψ(x,y,z)\nта геопотенціал Φ",
                    size=12, pad=8, fill="#fdf4f2", stroke=NEG, sw=1.6, bold=True))

    # Нижній блок діагностики
    bx4, by4 = 230, 270
    f.append(fitbox(bx4, by4, 320, 75, "4. Відновлені поля:\n• Вітер: u = −∂ψ/∂y,  v = ∂ψ/∂x\n• Температура: T ∝ ∂ψ/∂z\n• Поле тиску: p = ρ₀ f ψ",
                    size=12, pad=9, fill=FILL, stroke=INK, sw=1.6, bold=True))

    # Стрілки між блоками
    f.append(varrow(bx1 + 170, by1 + 40, bx2, by2 + 40, color=LINE, sw=2.5, head=10))
    f.append(varrow(bx2 + 170, by2 + 40, bx3, by3 + 40, color=LINE, sw=2.5, head=10))
    f.append(varrow(bx3 + 85, by3 + 80, bx4 + 240, by4, color=LINE, sw=2.5, head=10))

    # Стрілка переносу адвекції назад до кроку 1
    f.append(polyline([(bx4, by4 + 37), (165, by4 + 37), (165, by1 + 80)], color=MUTED, sw=2, dash="5 4"))
    f.append(head_at(165, by1 + 80, 0, -1, MUTED, 9))
    f.append(text(150, by4 + 20, "Адвекція PV: Dq/Dt = 0", size=11, bold=True, color=MUTED, anchor="end"))

    b, w, h = textbox(W / 2, 385, "Знаючи q(x,y,z), можна повністю реконструювати поле вітру, тиску та температури",
                      size=12, pad=8, fill=FILL, stroke=INK, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "pv-invertibility-diagram.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [
        fig_column_stretching(),
        fig_vortex_tilting(),
        fig_tropopause_fold(),
        fig_invertibility_loop()
    ]
    print("written:")
    for p in ps:
        print("  ", p)
