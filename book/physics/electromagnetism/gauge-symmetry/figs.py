# -*- coding: utf-8 -*-
"""Фігури до теми «Калібрувальна симетрія».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def path_tag(d, stroke=LINE, sw=1.5, fill="none", dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"{dash_attr}/>'

# ── Фігура 1: Калібрувальна орбіта потенціалів та інваріантність полів ──────
def fig_gauge_transform():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Калібрувальна орбіта потенціалів та інваріантність спостережуваних полів", size=16, bold=True))

    # Блок простору потенціалів (ліворуч)
    f.append(rect(20, 50, 340, 270, fill="#f8fafc", stroke=LINE, sw=1.5, rx=10))
    f.append(text(190, 74, "Простір електромагнітних потенціалів", size=13, bold=True, color=INK))

    # Крива калібрувальної орбіти
    f.append(path_tag("M 50 260 C 110 120, 270 280, 330 110", stroke="#94a3b8", sw=2, fill="none", dash="5,5"))
    f.append(text(270, 95, "Калібрувальна орбіта", size=11, color=MUTED, italic=True))

    # Точка 1: Початкові потенціали (phi, A)
    f.append(circle(90, 210, 7, fill=POS, stroke=POS, sw=1))
    b1, w1, h1 = textbox(90, 130, "Набір (φ, A)", size=12, bold=True, pad=5, fill="#ffffff", stroke=POS)
    f.append(b1)

    # Точка 2: Трансформовані потенціали (phi', A')
    f.append(circle(260, 170, 7, fill=NEG, stroke=NEG, sw=1))
    b2, w2, h2 = textbox(240, 235, "Набір (φ', A') =\n(φ - ∂λ/∂t, A + ∇λ)", size=11, bold=True, pad=5, fill="#ffffff", stroke=NEG)
    f.append(b2)

    # Стрілка калібрувального перетворення між точками
    f.append(path_tag("M 100 195 Q 175 140 250 165", stroke=FIELD, sw=2, fill="none"))
    f.append(arrow(240, 160, 250, 165, color=FIELD, sw=2))
    f.append(text(175, 135, "Перетворення λ(r, t)", size=12, bold=True, color=FIELD))

    # Блок фізичних полів (праворуч)
    f.append(rect(400, 50, 320, 270, fill="#f1f5f9", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(560, 74, "Фізичний простір спостережень", size=13, bold=True, color=INK))

    # Проєкційні стрілки від обох точок до єдиного фізичного стану
    f.append(line(97, 210, 480, 180, color=POS, sw=1.5, dash="3,3"))
    f.append(line(260, 170, 480, 180, color=NEG, sw=1.5, dash="3,3"))

    # Єдиний фізичний стан полів E та B
    f.append(circle(560, 180, 10, fill=FIELD, stroke=INK, sw=1.5))
    b3, w3, h3 = textbox(560, 125, "Фізичні поля:\nE = -∇φ - ∂A/∂t,  B = ∇×A", size=12, bold=True, pad=8, fill="#ffffff", stroke=FIELD)
    f.append(b3)
    f.append(text(560, 220, "ЄДИНИЙ ФІЗИЧНИЙ СТАН", size=12, bold=True, color=FIELD))
    f.append(text(560, 240, "(Напруженості E та B не змінюються)", size=11, color=MUTED))

    # Нижній висновок
    b_out, w_out, h_out = textbox(W / 2, H - 22, "Нескінченна кількість наборів (φ, A) уздовж орбіти відповідає єдиній фізичній реальності", size=12, pad=6, fill="#eef6ef", stroke=FIELD, sw=1.2, bold=True)
    f.append(b_out)

    return render(os.path.join(IMG, "fig1-gauge-transform.svg"), W, H, *f)


# ── Фігура 2: Калібрувальна фіксація (Lorentz та Coulomb gauges) ────────────
def fig_gauge_fixing():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Геометричний зміст калібрувальної фіксації (Gauge Fixing)", size=16, bold=True))

    # Фонові калібрувальні орбіти (вертикально-хвилясті лінії)
    for x_c in [120, 260, 400, 540, 680]:
        f.append(path_tag(f"M {x_c-20} 60 C {x_c+40} 120, {x_c-40} 180, {x_c+20} 240", stroke="#cbd5e1", sw=1.5, fill="none", dash="4,4"))

    f.append(text(660, 75, "Калібрувальні орбіти", size=11, color=MUTED, italic=True))

    # Гіперповерхня 1: Калібрування Лоренца
    f.append(line(50, 130, 690, 160, color=POS, sw=2.5))
    b_lor, w_lor, h_lor = textbox(370, 95, "Калібрувальна умова Лоренца:  ∇·A + (1/c²) ∂φ/∂t = 0", size=11, bold=True, pad=5, fill="#e0f2fe", stroke=POS)
    f.append(b_lor)

    # Гіперповерхня 2: Кулонівське калібрування
    f.append(line(50, 220, 690, 200, color=NEG, sw=2.5))
    b_coul, w_coul, h_coul = textbox(370, 275, "Поперечне (кулонівське) калібрування:  ∇·A = 0", size=11, bold=True, pad=5, fill="#fef2f2", stroke=NEG)
    f.append(b_coul)

    # Перетинів точки фіксації
    pts_lor = [(128, 133), (273, 140), (395, 146), (547, 153)]
    for px, py in pts_lor:
        f.append(circle(px, py, 6, fill=POS, stroke=INK, sw=1))

    pts_coul = [(110, 218), (275, 213), (403, 209), (530, 205)]
    for px, py in pts_coul:
        f.append(circle(px, py, 6, fill=NEG, stroke=INK, sw=1))

    # Текстові пояснення механізму фіксації
    b_info, w_info, h_info = textbox(W / 2, H - 25, "Умова калібрування вибирає єдиного представника на кожній калібрувальній орбіті", size=12, pad=6, fill="#f8fafc", stroke=LINE, sw=1.2, bold=True)
    f.append(b_info)

    return render(os.path.join(IMG, "fig2-gauge-fixing.svg"), W, H, *f)


# ── Фігура 3: Ефект Ааронова — Бома ──────────────────────────────────────────
def fig_aharonov_bohm():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Ефект Ааронова — Бома: фізична реальність векторного потенціалу", size=16, bold=True))

    # Джерело електронів
    f.append(circle(60, 180, 8, fill=INK, stroke=INK, sw=1))
    f.append(text(60, 205, "Джерело e⁻", size=12, bold=True, color=INK))

    # Екранована соленоїдна область в центрі
    cx, cy, r_sol = 340, 180, 45
    f.append(circle(cx, cy, r_sol + 6, fill="#cbd5e1", stroke="#64748b", sw=1.5)) # Екран
    f.append(circle(cx, cy, r_sol, fill="#fef08a", stroke="#eab308", sw=2))      # Всередині B != 0
    f.append(text(cx, cy - 8, "Магнітний потік", size=11, bold=True, color="#854d0e"))
    f.append(text(cx, cy + 10, "Φ (B ≠ 0)", size=12, bold=True, color="#854d0e"))

    # Текстова позначка: зовні B = 0, A != 0
    b_ext, w_ext, h_ext = textbox(cx, cy + 75, "Зовні соленоїда: B = 0, але A ≠ 0 (∇×A = 0)", size=11, bold=True, pad=5, fill="#ffffff", stroke="#64748b")
    f.append(b_ext)

    # Путь 1 (верхня пучок)
    f.append(path_tag(f"M 60 180 C 160 70, 500 70, 620 180", stroke=POS, sw=2.5, fill="none"))
    f.append(arrow(320, 78, 340, 78, color=POS, sw=2.5))
    f.append(text(340, 60, "Шлях 1 (фаза S₁)", size=12, bold=True, color=POS))

    # Путь 2 (нижня пучок)
    f.append(path_tag(f"M 60 180 C 160 290, 500 290, 620 180", stroke=NEG, sw=2.5, fill="none"))
    f.append(arrow(320, 282, 340, 282, color=NEG, sw=2.5))
    f.append(text(340, 305, "Шлях 2 (фаза S₂)", size=12, bold=True, color=NEG))

    # Детекторний екран праворуч
    f.append(rect(620, 60, 15, 240, fill="#334155", stroke=INK, sw=1.5, rx=3))
    f.append(text(645, 180, "Інтерференційний екран", size=12, bold=True, color=INK, anchor="start"))

    # Нижній висновок
    b_ab, w_ab, h_ab = textbox(W / 2, H - 22, "Різниця фаз ΔS = (q/ℏ) ∮ A · dl = (q/ℏ) Φ зміщує інтерференційну картину навіть при B = 0", size=12, pad=6, fill="#eef6ef", stroke=FIELD, sw=1.2, bold=True)
    f.append(b_ab)

    return render(os.path.join(IMG, "fig3-aharonov-bohm.svg"), W, H, *f)


# ── Фігура 4: Коваріантна похідна та фазова симетрія U(1) ───────────────────
def fig_covariant_derivative():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Локальна фазова симетрія U(1) та компенсаційне калібрувальне поле", size=16, bold=True))

    # Схема комплексної фази хвильової функції ψ(r)
    f.append(rect(20, 50, 340, 270, fill="#fcfdfd", stroke=LINE, sw=1.5, rx=10))
    f.append(text(190, 74, "Локальне обертання фази хвильової функції", size=12, bold=True, color=INK))

    # Коло комплексного числа exp(i θ)
    cx, cy, r_c = 190, 180, 65
    f.append(circle(cx, cy, r_c, fill="none", stroke="#94a3b8", sw=1.5))
    f.append(line(cx - 80, cy, cx + 80, cy, color="#cbd5e1", sw=1))
    f.append(line(cx, cy - 80, cx, cy + 80, color="#cbd5e1", sw=1))

    # Вектор ψ
    f.append(line(cx, cy, cx + 45, cy - 45, color=POS, sw=2.5))
    f.append(arrow(cx, cy, cx + 45, cy - 45, color=POS, sw=2.5))
    f.append(text(cx + 55, cy - 45, "ψ(r)", size=12, bold=True, color=POS))

    # Обертання фази на exp(i q λ(r) / ℏ)
    f.append(path_tag(f"M {cx+45} {cy-45} A {r_c} {r_c} 0 0 0 {cx-20} {cy-62}", stroke=NEG, sw=2, fill="none"))
    f.append(arrow(cx+10, cy-60, cx-20, cy-62, color=NEG, sw=2))
    f.append(text(cx - 10, cy - 75, "ψ'(r) = e^{i q λ/ℏ} ψ(r)", size=11, bold=True, color=NEG))

    # Блок коваріантної похідної (праворуч)
    f.append(rect(365, 50, 355, 270, fill="#f8fafc", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(542, 74, "Компенсація за допомогою поля A_μ", size=12, bold=True, color=INK))

    # Проста похідна лягає через нековаріантний додаток
    b_ord, w_ord, h_ord = textbox(542, 125, "Звичайна похідна: ∂_μ ψ'(r)\nмістить нековаріантний член (q/ℏ)(∂_μ λ)ψ", size=11, bold=False, pad=5, fill="#fef2f2", stroke=NEG)
    f.append(b_ord)

    # Калібрувальне поле компенсує градієнт фази
    b_trans, w_trans, h_trans = textbox(542, 180, "Перетворення поля: A_μ → A_μ + ∂_μ λ", size=11, bold=True, pad=5, fill="#e0f2fe", stroke=POS)
    f.append(b_trans)

    # Повний коваріантний оператор
    b_cov, w_cov, h_cov = textbox(542, 250, "Коваріантна похідна:\nD_μ = ∂_μ - i (q/ℏ) A_μ\n(D_μ ψ)' = e^{i q λ/ℏ} (D_μ ψ)", size=10, bold=True, pad=4, fill="#eef6ef", stroke=FIELD)
    f.append(b_cov)

    # Нижній висновок
    b_fin, w_fin, h_fin = textbox(W / 2, H - 22, "Вимоги локальної калібрувальної симетрії НЕМІНУЧЕ породжують електромагнітне поле A_μ", size=12, pad=6, fill="#f1f5f9", stroke=FIELD, sw=1.2, bold=True)
    f.append(b_fin)

    return render(os.path.join(IMG, "fig4-covariant-derivative.svg"), W, H, *f)


if __name__ == "__main__":
    fig_gauge_transform()
    fig_gauge_fixing()
    fig_aharonov_bohm()
    fig_covariant_derivative()
    print("Всі фігури успішно згенеровані у ./img/")
