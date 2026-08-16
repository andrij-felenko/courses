# -*- coding: utf-8 -*-
"""Фігури до теми «Принцип детального балансу».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Мікроскопічна оборотність у фазовому просторі ─────────────────
def fig_microscopic_reversibility():
    W, H = 780, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 26, "Мікроскопічна оборотність у фазовому просторі", size=16, bold=True))
    f.append(text(W / 2, 46, "Закон руху симетричний відносно інверсії часу t → -t та імпульсу p → -p", size=12, color=MUTED))

    pw = 350
    ph = 265
    py = 68

    # Панель А: Пряма траєкторія
    px1 = 25
    f.append(rect(px1, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(px1 + pw / 2, py + 22, "А. Прямий процес (час t)", size=13, bold=True, color=INK))

    # Стан i
    cx_i, cy_i = px1 + 65, py + 180
    f.append(circle(cx_i, cy_i, 22, fill="#e8f0fe", stroke="#1a73e8", sw=2.0))
    f.append(text(cx_i, cy_i + 4, "i", size=14, bold=True, color="#1557b0"))
    f.append(text(cx_i, cy_i - 30, "(q, p)", size=12, color=MUTED))

    # Стан j
    cx_j, cy_j = px1 + 285, py + 90
    f.append(circle(cx_j, cy_j, 22, fill="#e6f4ea", stroke="#137333", sw=2.0))
    f.append(text(cx_j, cy_j + 4, "j", size=14, bold=True, color="#137333"))
    f.append(text(cx_j, cy_j - 30, "(q', p')", size=12, color=MUTED))

    # Траєкторія від i до j
    path_a = ("M %d %d C %d %d, %d %d, %d %d" %
              (cx_i + 20, cy_i - 10, px1 + 140, py + 220, px1 + 210, py + 120, cx_j - 20, cy_j + 10))
    f.append('<path d="%s" stroke="#1a73e8" stroke-width="2.5" fill="none" marker-end="url(#arrow)"/>' % path_a)

    # Підпис імовірності переходу W(i → j)
    body_a, _, _ = textbox(px1 + 175, py + 200, "W(i → j)", size=12, bold=True, color="#1557b0", fill="#e8f0fe", stroke="#aecbfa", pad=4)
    f.append(body_a)

    # Вектор імпульсу p
    f.append(arrow(cx_i, cy_i, cx_i + 35, cy_i - 20, color=POS, sw=2.0))
    f.append(text(cx_i + 42, cy_i - 22, "p", size=12, bold=True, color=POS))


    # Панель Б: Обернена траєкторія
    px2 = 405
    f.append(rect(px2, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(px2 + pw / 2, py + 22, "Б. Часово-обернений процес (-t)", size=13, bold=True, color=INK))

    # Стан j* (звернений j)
    cx_j_star, cy_j_star = px2 + 285, py + 90
    f.append(circle(cx_j_star, cy_j_star, 22, fill="#fce8e6", stroke="#d93025", sw=2.0))
    f.append(text(cx_j_star, cy_j_star + 4, "j*", size=14, bold=True, color="#b31412"))
    f.append(text(cx_j_star, cy_j_star - 30, "(q', -p')", size=12, color=MUTED))

    # Стан i* (звернений i)
    cx_i_star, cy_i_star = px2 + 65, py + 180
    f.append(circle(cx_i_star, cy_i_star, 22, fill="#fef7e0", stroke="#b06000", sw=2.0))
    f.append(text(cx_i_star, cy_i_star + 4, "i*", size=14, bold=True, color="#b06000"))
    f.append(text(cx_i_star, cy_i_star - 30, "(q, -p)", size=12, color=MUTED))

    # Траєкторія від j* до i*
    path_b = ("M %d %d C %d %d, %d %d, %d %d" %
              (cx_j_star - 20, cy_j_star + 10, px2 + 210, py + 120, px2 + 140, py + 220, cx_i_star + 20, cy_i_star - 10))
    f.append('<path d="%s" stroke="#d93025" stroke-width="2.5" fill="none" marker-end="url(#arrow)"/>' % path_b)

    # Підпис імовірності переходу W(j* → i*)
    body_b, _, _ = textbox(px2 + 175, py + 200, "W(j* → i*)", size=12, bold=True, color="#b31412", fill="#fce8e6", stroke="#f5c2c7", pad=4)
    f.append(body_b)

    # Вектор імпульсу -p
    f.append(arrow(cx_j_star, cy_j_star, cx_j_star - 35, cy_j_star + 20, color=NEG, sw=2.0))
    f.append(text(cx_j_star - 45, cy_j_star + 26, "-p'", size=12, bold=True, color=NEG))

    return render(os.path.join(IMG, "microscopic-reversibility.svg"), W, H, *f)


# ── Фігура 2: Глобальний баланс проти детального балансу ────────────────────
def fig_detailed_vs_global_balance():
    W, H = 780, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Глобальний баланс проти детального балансу", size=16, bold=True))
    f.append(text(W / 2, 46, "Стаціонарність дозволяє циркуляцію (ліворуч); рівновага її повністю забороняє (праворуч)", size=12, color=MUTED))

    pw = 350
    ph = 285
    py = 68

    # Панель А: Глобальний баланс (Неривноважний стаціонарний стан NESS)
    px1 = 25
    f.append(rect(px1, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(px1 + pw / 2, py + 22, "А. Глобальний баланс (з замкненим потоком)", size=13, bold=True, color=INK))

    # Три вузли у трикутнику
    n1_x, n1_y = px1 + 175, py + 65
    n2_x, n2_y = px1 + 80, py + 220
    n3_x, n3_y = px1 + 270, py + 220

    f.append(circle(n1_x, n1_y, 22, fill="#e8f0fe", stroke="#1a73e8", sw=2.0))
    f.append(text(n1_x, n1_y + 5, "1", size=14, bold=True, color="#1557b0"))

    f.append(circle(n2_x, n2_y, 22, fill="#e8f0fe", stroke="#1a73e8", sw=2.0))
    f.append(text(n2_x, n2_y + 5, "2", size=14, bold=True, color="#1557b0"))

    f.append(circle(n3_x, n3_y, 22, fill="#e8f0fe", stroke="#1a73e8", sw=2.0))
    f.append(text(n3_x, n3_y + 5, "3", size=14, bold=True, color="#1557b0"))

    # Циклічні сильні потоки (1 -> 2 -> 3 -> 1)
    f.append(arrow(n1_x - 14, n1_y + 16, n2_x + 14, n2_y - 16, color="#d93025", sw=2.8))
    f.append(text(px1 + 110, py + 130, "J = 10", size=11, bold=True, color="#d93025"))

    f.append(arrow(n2_x + 22, n2_y, n3_x - 22, n3_y, color="#d93025", sw=2.8))
    f.append(text(px1 + 175, py + 242, "J = 10", size=11, bold=True, color="#d93025"))

    f.append(arrow(n3_x - 14, n3_y - 16, n1_x + 14, n1_y + 16, color="#d93025", sw=2.8))
    f.append(text(px1 + 240, py + 130, "J = 10", size=11, bold=True, color="#d93025"))

    # Слабкі зворотні потоки (2 -> 1, 3 -> 2, 1 -> 3)
    f.append(arrow(n2_x + 5, n2_y - 22, n1_x - 22, n1_y + 5, color=MUTED, sw=1.2))
    f.append(arrow(n3_x - 22, n3_y - 12, n2_x + 22, n2_y - 12, color=MUTED, sw=1.2))
    f.append(arrow(n1_x + 22, n1_y + 5, n3_x - 5, n3_y - 22, color=MUTED, sw=1.2))

    body_g, _, _ = textbox(px1 + 175, py + 270, "Вхід = Вихід у кожному вузлі\nАле є коловий потік J_коло ≠ 0", size=11, bold=False, fill="#fce8e6", stroke="#f5c2c7", color="#b31412", pad=3)
    f.append(body_g)


    # Панель Б: Детальний баланс (Термодинамічна рівновага)
    px2 = 405
    f.append(rect(px2, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(px2 + pw / 2, py + 22, "Б. Детальний баланс (термодинамічна рівновага)", size=13, bold=True, color=INK))

    mb1_x, mb1_y = px2 + 175, py + 65
    mb2_x, mb2_y = px2 + 80, py + 220
    mb3_x, mb3_y = px2 + 270, py + 220

    f.append(circle(mb1_x, mb1_y, 22, fill="#e6f4ea", stroke="#137333", sw=2.0))
    f.append(text(mb1_x, mb1_y + 5, "1", size=14, bold=True, color="#137333"))

    f.append(circle(mb2_x, mb2_y, 22, fill="#e6f4ea", stroke="#137333", sw=2.0))
    f.append(text(mb2_x, mb2_y + 5, "2", size=14, bold=True, color="#137333"))

    f.append(circle(mb3_x, mb3_y, 22, fill="#e6f4ea", stroke="#137333", sw=2.0))
    f.append(text(mb3_x, mb3_y + 5, "3", size=14, bold=True, color="#137333"))

    # Попарно рівні взаємні стрілки (1 <-> 2, 2 <-> 3, 3 <-> 1)
    f.append(arrow(mb1_x - 18, mb1_y + 12, mb2_x + 10, mb2_y - 20, color="#137333", sw=2.0))
    f.append(arrow(mb2_x + 20, mb2_y - 10, mb1_x - 8, mb1_y + 22, color="#137333", sw=2.0))

    f.append(arrow(mb2_x + 22, mb2_y - 8, mb3_x - 22, mb3_y - 8, color="#137333", sw=2.0))
    f.append(arrow(mb3_x - 22, mb3_y + 8, mb2_x + 22, mb2_y + 8, color="#137333", sw=2.0))

    f.append(arrow(mb3_x - 10, mb3_y - 20, mb1_x + 18, mb1_y + 12, color="#137333", sw=2.0))
    f.append(arrow(mb1_x + 8, mb1_y + 22, mb3_x - 20, mb3_y - 10, color="#137333", sw=2.0))

    body_d, _, _ = textbox(px2 + 175, py + 270, "P(i)·W(i → j) = P(j)·W(j → i)\nЧистий потік J_ij = 0 для кожної пари", size=11, bold=True, fill="#e6f4ea", stroke="#a8dab5", color="#137333", pad=3)
    f.append(body_d)

    return render(os.path.join(IMG, "detailed-vs-global-balance.svg"), W, H, *f)


# ── Фігура 3: Радіаційні переходи Ейнштейна та детальний баланс ─────────────
def fig_einstein_transitions():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Радіаційні переходи Ейнштейна (1917)", size=16, bold=True))
    f.append(text(W / 2, 46, "Рівновага між поглинанням, спонтанним і вимушеним випромінюванням світла", size=12, color=MUTED))

    px = 35
    py = 70
    pw = 690
    ph = 285

    f.append(rect(px, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))

    # Лінії енергетичних рівнів E2 та E1
    y_e2 = py + 55
    y_e1 = py + 215

    f.append(line(px + 40, y_e2, px + pw - 40, y_e2, color="#d93025", sw=3.0))
    f.append(text(px + 50, y_e2 - 12, "Верхній рівень E₂ (заселеність N₂)", size=13, bold=True, color="#b31412", anchor="left"))

    f.append(line(px + 40, y_e1, px + pw - 40, y_e1, color="#1a73e8", sw=3.0))
    f.append(text(px + 50, y_e1 + 22, "Нижній рівень E₁ (заселеність N₁)", size=13, bold=True, color="#1557b0", anchor="left"))

    # Перехід 1: Поглинання (Стрілка ліворуч від блоку)
    x_abs_arrow = px + 100
    x_abs_box   = px + 180
    f.append(arrow(x_abs_arrow, y_e1 - 5, x_abs_arrow, y_e2 + 10, color="#f9ab00", sw=2.8))
    body_abs, _, _ = textbox(x_abs_box, py + 135, "Поглинання\nB₁₂ · ρ(ν)", size=12, bold=True, fill="#fef7e0", stroke="#fce8b2", color="#b06000", pad=4)
    f.append(body_abs)

    # Перехід 2: Спонтанне випромінювання
    x_spont_arrow = px + 280
    x_spont_box   = px + 360
    f.append(arrow(x_spont_arrow, y_e2 + 5, x_spont_arrow, y_e1 - 10, color="#137333", sw=2.8))
    body_spont, _, _ = textbox(x_spont_box, py + 135, "Спонтанне\nвипромінювання\nA₂₁", size=12, bold=True, fill="#e6f4ea", stroke="#a8dab5", color="#137333", pad=4)
    f.append(body_spont)

    # Перехід 3: Вимушене випромінювання
    x_stim_arrow = px + 470
    x_stim_box   = px + 570
    f.append(arrow(x_stim_arrow, y_e2 + 5, x_stim_arrow, y_e1 - 10, color="#d93025", sw=2.8))
    body_stim, _, _ = textbox(x_stim_box, py + 135, "Вимушене\nвипромінювання\nB₂₁ · ρ(ν)", size=12, bold=True, fill="#fce8e6", stroke="#f5c2c7", color="#b31412", pad=4)
    f.append(body_stim)

    # Нижній прямокутник з умовою детального балансу
    body_eq, _, _ = textbox(px + pw / 2, py + 250, "Умова детального балансу:   N₁ · B₁₂ · ρ(ν) = N₂ · [ A₂₁ + B₂₁ · ρ(ν) ]", size=13, bold=True, fill="#f4f6f8", stroke=LINE, color=INK, pad=6)
    f.append(body_eq)

    return render(os.path.join(IMG, "einstein-transitions.svg"), W, H, *f)


# ── Фігура 4: Механізм прийняття Метрополіса-Гастінгса ──────────────────────
def fig_mcmc_metropolis_chain():
    W, H = 780, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Алгоритм Метрополіса-Гастінгса та детальний баланс", size=16, bold=True))
    f.append(text(W / 2, 46, "Розбиття переходу на пропозицію q(i → j) та прийняття α(i → j)", size=12, color=MUTED))

    pw = 730
    ph = 285
    px = 25
    py = 68

    f.append(rect(px, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))

    # Стан i (поточний)
    cx_i, cy_i = px + 90, py + 120
    f.append(circle(cx_i, cy_i, 28, fill="#e8f0fe", stroke="#1a73e8", sw=2.2))
    f.append(text(cx_i, cy_i + 5, "стан i", size=13, bold=True, color="#1557b0"))
    f.append(text(cx_i, cy_i + 45, "Енергія E_i", size=12, color=MUTED))

    # Пропозиція q(i -> j)
    f.append(arrow(cx_i + 30, cy_i, px + 215, cy_i, color="#1a73e8", sw=2.5))
    body_prop, _, _ = textbox(px + 160, cy_i - 22, "Пропозиція\nq(i → j)", size=11, bold=True, fill="#e8f0fe", stroke="#aecbfa", color="#1557b0", pad=3)
    f.append(body_prop)

    # Кандидат j
    cx_cand, cy_cand = px + 250, py + 120
    f.append(circle(cx_cand, cy_cand, 28, fill="#fef7e0", stroke="#b06000", sw=2.2))
    f.append(text(cx_cand, cy_cand + 5, "стан j", size=13, bold=True, color="#b06000"))
    f.append(text(cx_cand, cy_cand + 45, "Енергія E_j", size=12, color=MUTED))

    # Перевірка ΔE = E_j - E_i
    cx_check, cy_check = px + 440, py + 120
    body_check, _, _ = textbox(cx_check, cy_check, "Розрахунок ΔE = E_j - E_i\nα = min(1, exp(-ΔE / kT))", size=12, bold=True, fill="#f4f6f8", stroke=LINE, pad=6)
    f.append(body_check)
    f.append(arrow(cx_cand + 30, cy_cand, cx_check - 90, cy_check, color=LINE, sw=2.0))

    # Два виходи: Прийнято / Відхилено
    cx_acc, cy_acc = px + 630, py + 65
    f.append(arrow(cx_check + 85, cy_check - 15, cx_acc - 45, cy_acc + 10, color="#137333", sw=2.2))
    body_acc, _, _ = textbox(cx_acc, cy_acc, "ПРИЙНЯТО\nx_{n+1} = j", size=12, bold=True, fill="#e6f4ea", stroke="#a8dab5", color="#137333", pad=4)
    f.append(body_acc)

    cx_rej, cy_rej = px + 630, py + 175
    f.append(arrow(cx_check + 85, cy_check + 15, cx_rej - 45, cy_rej - 10, color="#d93025", sw=2.2))
    body_rej, _, _ = textbox(cx_rej, cy_rej, "ВІДХИЛЕНО\nx_{n+1} = i", size=12, bold=True, fill="#fce8e6", stroke="#f5c2c7", color="#b31412", pad=4)
    f.append(body_rej)

    # Нижній підпис про гарантію детального балансу
    body_foot, _, _ = textbox(px + pw / 2, py + 250, "Результат: P(i) · W(i → j) = P(j) · W(j → i)   ⇒   ланцюг сходиться до больцманівського розподілу", size=12, bold=True, fill="#e8f0fe", stroke="#aecbfa", color="#1557b0", pad=5)
    f.append(body_foot)

    return render(os.path.join(IMG, "mcmc-metropolis-chain.svg"), W, H, *f)


if __name__ == "__main__":
    fig_microscopic_reversibility()
    fig_detailed_vs_global_balance()
    fig_einstein_transitions()
    fig_mcmc_metropolis_chain()
    print("Figures generated successfully in ./img/")
