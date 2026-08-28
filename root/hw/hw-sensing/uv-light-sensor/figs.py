# -*- coding: utf-8 -*-
"""Фігури до теми «УФ-індекс та УФ-давачі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Спектральні діапазони УФ та атмосфера ─────────────────────────────────
def fig_uv_spectral_bands():
    W, H = 820, 400
    f = [text(W / 2, 26, "Спектральні діапазони ультрафіолету та проникнення крізь атмосферу", size=15, bold=True)]

    # Секції діапазонів
    bands = [
        ("UV-C", "100–280 нм", "4.43–12.4 еВ", POS, "#fdf2f0",
         "Повністю поглинається\nкиснем O₂ та озоном O₃\nу стратосфері.",
         "0% доходить до поверхні\n(джерела: бактерицидні лампи)"),
        ("UV-B", "280–315 нм", "3.94–4.43 еВ", "#e67e22", "#fdf7f0",
         "На 90–95% поглинається\nозоновим шаром (смуги Хаггінса).\nВисока фотохімічна енергія.",
         "5–10% на поверхні Землі\nГоловна причина опіків і ДНК-мутацій"),
        ("UV-A", "315–400 нм", "3.10–3.94 еВ", "#2980b9", "#f0f6fc",
         "Майже не поглинається\nозоном і вільно доходить\nдо рівня моря.",
         ">90–95% усього сонячного УФ\nСпричиняє старіння шкіри та засмагу"),
        ("Видиме світло", "400–700 нм", "1.77–3.10 еВ", FIELD, "#f2f9f4",
         "Повна прозорість атмосфери.\nСприймається оком людини\nяк кольори веселки.",
         "Оптичний потік у 100–1000 разів\nперевищує потік УФ-B"),
    ]

    cw = 182
    gap = 14
    start_x = (W - (4 * cw + 3 * gap)) / 2
    top = 52

    for i, (title, wave, energy, stroke_col, bg_col, desc, ground) in enumerate(bands):
        x = start_x + i * (cw + gap)
        # Карточка
        f.append(rect(x, top, cw, 296, fill=bg_col, stroke=stroke_col, sw=1.8, rx=8))
        
        # Заголовок та діапазон
        f.append(text(x + cw / 2, top + 24, title, size=14, bold=True, color=stroke_col))
        f.append(text(x + cw / 2, top + 42, wave, size=11.5, bold=True, color=INK))
        f.append(text(x + cw / 2, top + 58, f"Енергія: {energy}", size=10.5, color=MUTED))
        f.append(line(x + 10, top + 68, x + cw - 10, top + 68, color=stroke_col, sw=1.0))

        # Опис атмосфери
        f.append(text(x + cw / 2, top + 86, "Атмосферний бар'єр:", size=11, bold=True, color=INK))
        f.append(mtext(x + cw / 2, top + 106, desc, size=10.5, color=INK, lh=1.25))

        f.append(line(x + 15, top + 172, x + cw - 15, top + 172, color=stroke_col, sw=0.8, dash="3,3"))

        # Досягнення поверхні
        f.append(text(x + cw / 2, top + 192, "На рівні землі:", size=11, bold=True, color=INK))
        f.append(mtext(x + cw / 2, top + 212, ground, size=10.5, color=INK, lh=1.25))

    f.append(text(W / 2, top + 322,
                  "Озоновий шар відтинає весь UV-C і левову частку UV-B; проте саме залишкові фотони UV-B несуть найбільшу біологічну загрозу",
                  size=11.5, color=INK, italic=True))

    render(os.path.join(IMG, "uv-spectral-bands-atmosphere.svg"), W, H, *f)


# ── 2. Еритемна спектральна дія та парадокс УФ-B ──────────────────────────────
def fig_erythemal_action():
    W, H = 820, 440
    f = [text(W / 2, 24, "Еритемна крива дії Мак-Кінлі — Діффі та ефективний спектр сонячного опіку", size=15, bold=True)]

    # Вісь координат графіка
    gx, gy = 80, 60
    gw, gh = 420, 310

    f.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke=LINE, sw=1.2, rx=4))

    # Горизонтальні лінії сітки (логарифмічний масштаб s_er: 1.0, 0.1, 0.01, 0.001, 0.0001)
    grid_y = [
        (gy + 20, "1.0  (10⁰)", "10⁰"),
        (gy + 85, "0.1  (10⁻¹)", "10⁻¹"),
        (gy + 150, "0.01 (10⁻²)", "10⁻²"),
        (gy + 215, "10⁻³", "10⁻³"),
        (gy + 280, "10⁻⁴", "10⁻⁴"),
    ]
    for y_pos, label, _ in grid_y:
        f.append(line(gx, y_pos, gx + gw, y_pos, color="#e2e6eb", sw=1.0, dash="4,4"))
        f.append(text(gx - 8, y_pos + 4, label, size=10, color=MUTED, anchor="end"))

    # Вертикальні лінії довжин хвиль: 280, 298, 315, 328, 360, 400 нм
    def w_to_x(lam):
        return gx + (lam - 280) / (400 - 280) * gw

    wavelengths = [
        (280, "280 (UV-B)"),
        (298, "298"),
        (315, "315 (UV-A)"),
        (328, "328"),
        (360, "360"),
        (400, "400 (VIS)"),
    ]
    for lam, label in wavelengths:
        x_pos = w_to_x(lam)
        f.append(line(x_pos, gy, x_pos, gy + gh, color="#e2e6eb", sw=1.0, dash="3,3"))
        f.append(text(x_pos, gy + gh + 16, label, size=9.5, color=MUTED, anchor="middle"))

    # Позначення осі X
    f.append(text(gx + gw / 2, gy + gh + 34, "Довжина хвилі λ (нм)", size=11, bold=True, color=INK))
    # Позначення осі Y
    f.append(text(gx - 46, gy + gh / 2, "Еритемна чутливість s_er(λ)  [лог. шкала]", size=11, bold=True, color=POS, anchor="middle"))

    # Крива s_er(λ): 280..298 -> y=gy+20; 298..328 -> y падає до gy+215; 328..400 -> y падає до gy+280
    x280 = w_to_x(280)
    x298 = w_to_x(298)
    x328 = w_to_x(328)
    x400 = w_to_x(400)
    y1 = gy + 20
    y2 = gy + 215
    y3 = gy + 280
    f.append(line(x280, y1, x298, y1, color=POS, sw=3.0))
    f.append(line(x298, y1, x328, y2, color=POS, sw=3.0))
    f.append(line(x328, y2, x400, y3, color=POS, sw=3.0))

    # Точки перегину
    f.append(circle(x298, y1, 4, fill=POS, stroke=BG, sw=1.5))
    f.append(circle(x328, y2, 4, fill=POS, stroke=BG, sw=1.5))
    f.append(circle(x400, y3, 4, fill=POS, stroke=BG, sw=1.5))

    # Крива сонячного спектра E(λ) на поверхні (умовна форма, пунктир)
    sun_pts = [
        (w_to_x(280), gy + 295),
        (w_to_x(295), gy + 295),
        (w_to_x(305), gy + 260),
        (w_to_x(315), gy + 190),
        (w_to_x(330), gy + 110),
        (w_to_x(360), gy + 60),
        (w_to_x(400), gy + 35),
    ]
    for k in range(len(sun_pts) - 1):
        f.append(line(sun_pts[k][0], sun_pts[k][1], sun_pts[k+1][0], sun_pts[k+1][1], color="#e67e22", sw=2.0, dash="5,3"))

    # Крива ефективної еритеми E_eff(λ) = E(λ) * s_er(λ) (утворює пік на 305–315 нм)
    eff_pts = [
        (w_to_x(280), gy + 295),
        (w_to_x(295), gy + 295),
        (w_to_x(300), gy + 240),
        (w_to_x(308), gy + 150),  # Пік
        (w_to_x(315), gy + 180),
        (w_to_x(325), gy + 240),
        (w_to_x(340), gy + 270),
        (w_to_x(380), gy + 285),
        (w_to_x(400), gy + 290),
    ]
    for k in range(len(eff_pts) - 1):
        f.append(line(eff_pts[k][0], eff_pts[k][1], eff_pts[k+1][0], eff_pts[k+1][1], color=NEG, sw=2.5))

    # Права інформаційна панель
    panel_x = 525
    panel_w = 275

    b1, _, _ = textbox(panel_x + panel_w / 2, gy + 50,
                       "Еритемна дія s_er(λ) (червона)\n"
                       "Чутливість шкіри на 298 нм у ~1000 разів\n"
                       "вища, ніж на 360 нм, і в ~8200 разів\n"
                       "вища, ніж на 400 нм!",
                       size=11, fill="#fdf2f0", stroke=POS, bold=False, pad=8)
    f.append(b1)

    b2, _, _ = textbox(panel_x + panel_w / 2, gy + 145,
                       "Сонячний потік E(λ) (помаранчева)\n"
                       "Потік біля 295 нм майже нульовий;\n"
                       "у діапазоні UV-A (360 нм) він у сотні\n"
                       "разів потужніший, ніж у UV-B.",
                       size=11, fill="#fdf7f0", stroke="#e67e22", bold=False, pad=8)
    f.append(b2)

    b3, _, _ = textbox(panel_x + panel_w / 2, gy + 245,
                       "Пік дії: E(λ) · s_er(λ) (синя)\n"
                       "Добуток формує гострий пік\n"
                       "у вузькому вікні 305–315 нм (UV-B).\n"
                       "Саме воно визначає 85–90% УФ-індексу!",
                       size=11, fill="#eef2f8", stroke=NEG, bold=False, pad=8)
    f.append(b3)

    f.append(text(W / 2, H - 12,
                  "Парадокс УФ: потік енергії домінує в UV-A, але опік шкіри майже повністю спричиняє вузька смуга UV-B біля 308 нм",
                  size=11.5, color=INK, italic=True))

    render(os.path.join(IMG, "erythemal-action-spectrum.svg"), W, H, *f)


# ── 3. Кремнієві сенсори проти широкозонних (SiC / GaN) ──────────────────────
def fig_silicon_vs_widegap():
    W, H = 820, 390
    f = [text(W / 2, 24, "Два шляхи детектування УФ: фільтрований кремній проти широкозонних напівпровідників", size=15, bold=True)]

    card_w = 370
    card_h = 300
    top = 50

    # Ліва колонка: Кремнієвий сенсор з фільтром
    x_left = 30
    f.append(rect(x_left, top, card_w, card_h, fill="#fffaf5", stroke="#d35400", sw=1.8, rx=8))
    f.append(text(x_left + card_w / 2, top + 24, "Кремнієвий фотодіод + фільтри (VEML/Si11xx)", size=13, bold=True, color="#d35400"))
    f.append(line(x_left + 15, top + 34, x_left + card_w - 15, top + 34, color="#d35400", sw=1.0))

    # Схема шарів кремнієвого сенсора
    layer_y = top + 52
    f.append(rect(x_left + 35, layer_y, card_w - 70, 24, fill="#dfe6e9", stroke="#636e72", sw=1.2))
    f.append(text(x_left + card_w / 2, layer_y + 16, "Інтерференційний діелектричний фільтр", size=10.5, color=INK))

    layer_y2 = layer_y + 28
    f.append(rect(x_left + 35, layer_y2, card_w - 70, 34, fill="#b2bec3", stroke="#2d3436", sw=1.2))
    f.append(text(x_left + card_w / 2, layer_y2 + 16, "Кремнієвий p-n перехід (Eg = 1.12 еВ)", size=11, bold=True, color=INK))
    f.append(text(x_left + card_w / 2, layer_y2 + 28, "Природна чутливість: 190–1100 нм (УФ + ВИД + ІЧ)", size=9.5, color=MUTED))

    # Опис проблеми та рішення
    f.append(text(x_left + 25, layer_y2 + 56, "Фізичні виклики та обмеження:", size=11, bold=True, color=POS))
    f.append(mtext(x_left + 25, layer_y2 + 74,
                   "• Фільтр має витік 0.1–1% у видимій та ІЧ області.\n"
                   "• Потужне сонце (>800 Вт/м²) створює паразитний ІЧ-струм,\n"
                   "  що перекриває слабкий сигнал УФ у рази.\n"
                   "• Потребує 4 канали (UVA, UVB, VIS, IR) і матричну\n"
                   "  компенсацію перехресного засвічення в DSP.",
                   size=10.5, color=INK, anchor="start", lh=1.25))

    # Права колонка: Широкозонний напівпровідник (SiC / GaN)
    x_right = 420
    f.append(rect(x_right, top, card_w, card_h, fill="#f4faf6", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(x_right + card_w / 2, top + 24, "Широкозонний фотодіод (SiC / GaN / AlGaN)", size=13, bold=True, color=FIELD))
    f.append(line(x_right + 15, top + 34, x_right + card_w - 15, top + 34, color=FIELD, sw=1.0))

    # Схема шарів широкозонного сенсора
    layer_ry = top + 52
    f.append(rect(x_right + 35, layer_ry, card_w - 70, 24, fill="#e8f8f5", stroke=FIELD, sw=1.2))
    f.append(text(x_right + card_w / 2, layer_ry + 16, "Кварцове вікно / прямий контакт із світлом", size=10.5, color=FIELD))

    layer_ry2 = layer_ry + 28
    f.append(rect(x_right + 35, layer_ry2, card_w - 70, 34, fill="#a3e4d7", stroke="#117864", sw=1.2))
    f.append(text(x_right + card_w / 2, layer_ry2 + 16, "Кристал 4H-SiC (Eg = 3.26 еВ) / AlGaN", size=11, bold=True, color=INK))
    f.append(text(x_right + card_w / 2, layer_ry2 + 28, "Сліпий до видимого: фотони >380 нм не породжують пар!", size=9.5, color=FIELD))

    # Опис переваг
    f.append(text(x_right + 25, layer_ry2 + 56, "Фізичні переваги:", size=11, bold=True, color=FIELD))
    f.append(mtext(x_right + 25, layer_ry2 + 74,
                   "• Природна «сонцесліпість» (visible/solar-blind).\n"
                   "• Придушення видимого та ІЧ > 10⁴–10⁶ БЕЗ фільтрів.\n"
                   "• Темновий струм < 10 фА (у 1000 разів менший за кремній).\n"
                   "• Стійкість до жорсткого УФ і деградації кристала.\n"
                   "• Висока ціна; вимагає прецизійного TIA (пА-струми).",
                   size=10.5, color=INK, anchor="start", lh=1.25))

    f.append(text(W / 2, H - 12,
                  "Широкозонний напівпровідник вирішує проблему оптичної селективності на рівні квантової забороненої зони речовини",
                  size=11.5, color=INK, italic=True))

    render(os.path.join(IMG, "silicon-vs-widegap-physics.svg"), W, H, *f)


# ── 4. Матрична компенсація та обчислення UVI ─────────────────────────────────
def fig_matrix_compensation():
    W, H = 820, 370
    f = [text(W / 2, 24, "Архітектура матричної компенсації перехресного оптичного засвічення", size=15, bold=True)]

    # 4 блоки вхідних фотодіодів
    top_y = 65
    ch_w, ch_h = 160, 48
    ch_gap = 14
    ch_start_x = 40

    channels = [
        ("Raw UVA", "Канал UV-A + паразитне ІЧ", POS, "#fdf2f0"),
        ("Raw UVB", "Канал UV-B + паразитне ІЧ", "#e67e22", "#fdf7f0"),
        ("Raw VIS", "Канал видимого світла", FIELD, "#f2f9f4"),
        ("Raw IR", "Канал ближнього ІЧ", "#8e44ad", "#fbf5fc"),
    ]

    for i, (title, sub, col, bg_col) in enumerate(channels):
        y = top_y + i * (ch_h + ch_gap)
        f.append(rect(ch_start_x, y, ch_w, ch_h, fill=bg_col, stroke=col, sw=1.5, rx=6))
        f.append(text(ch_start_x + ch_w / 2, y + 20, title, size=12, bold=True, color=col))
        f.append(text(ch_start_x + ch_w / 2, y + 36, sub, size=9.5, color=MUTED))
        f.append(arrow(ch_start_x + ch_w, y + ch_h / 2, ch_start_x + ch_w + 35, y + ch_h / 2, color=col, sw=1.5))

    # Центральний блок DSP компенсації
    dsp_x = ch_start_x + ch_w + 40
    dsp_y = top_y
    dsp_w = 320
    dsp_h = 4 * ch_h + 3 * ch_gap

    f.append(rect(dsp_x, dsp_y, dsp_w, dsp_h, fill="#f8fafc", stroke=NEG, sw=1.8, rx=8))
    f.append(text(dsp_x + dsp_w / 2, dsp_y + 26, "Матричний процесор компенсації (DSP)", size=13, bold=True, color=NEG))
    f.append(line(dsp_x + 20, dsp_y + 38, dsp_x + dsp_w - 20, dsp_y + 38, color=NEG, sw=1.0))

    # Формули компенсації всередині блоку
    f.append(text(dsp_x + 20, dsp_y + 64, "Віднімання паразитних засвіток:", size=11, bold=True, color=INK, anchor="start"))
    
    b_uva, _, _ = textbox(dsp_x + dsp_w / 2, dsp_y + 98,
                          "UVA_comp = Raw_UVA − a·VIS − b·IR − Offset_A",
                          size=10.5, fill=BG, stroke=POS, bold=True, pad=6)
    f.append(b_uva)

    b_uvb, _, _ = textbox(dsp_x + dsp_w / 2, dsp_y + 148,
                          "UVB_comp = Raw_UVB − c·VIS − d·IR − Offset_B",
                          size=10.5, fill=BG, stroke="#e67e22", bold=True, pad=6)
    f.append(b_uvb)

    f.append(text(dsp_x + dsp_w / 2, dsp_y + 194, "де a, b, c, d — калібрувальні коефіцієнти матриці", size=10, italic=True, color=MUTED))

    # Стрілки на вихід
    out_y1 = dsp_y + 98
    out_y2 = dsp_y + 148
    f.append(arrow(dsp_x + dsp_w, out_y1, dsp_x + dsp_w + 40, out_y1, color=POS, sw=1.8))
    f.append(arrow(dsp_x + dsp_w, out_y2, dsp_x + dsp_w + 40, out_y2, color="#e67e22", sw=1.8))

    # Правий вихідний блок обчислення UVI
    out_x = dsp_x + dsp_w + 45
    out_w = 200
    out_y = top_y + 30
    out_h = 175

    f.append(rect(out_x, out_y, out_w, out_h, fill="#fdfaf3", stroke="#d4ac0d", sw=1.8, rx=8))
    f.append(text(out_x + out_w / 2, out_y + 24, "Обчислення UVI", size=13, bold=True, color="#b7950b"))
    f.append(line(out_x + 15, out_y + 34, out_x + out_w - 15, out_y + 34, color="#d4ac0d", sw=1.0))

    f.append(mtext(out_x + out_w / 2, out_y + 58,
                   "UVI = kA·UVA + kB·UVB\n\n"
                   "Масштабування:\n"
                   "1 UVI = 25 мВт/м²\n"
                   "еритемної опроміненості",
                   size=11, color=INK, lh=1.25, bold=False))

    f.append(rect(out_x + 20, out_y + 128, out_w - 40, 32, fill="#e74c3c", stroke=BG, sw=1, rx=4))
    f.append(text(out_x + out_w / 2, out_y + 148, "UVI: 0 .. 11+ (WHO)", size=11.5, bold=True, color=BG))

    f.append(text(W / 2, H - 14,
                  "Паразитний відгук на сонячне видиме та ІЧ випромінювання компенсується лінійною матрицею коефіцієнтів у реальному часі",
                  size=11.5, color=INK, italic=True))

    render(os.path.join(IMG, "optical-crosstalk-matrix.svg"), W, H, *f)


if __name__ == "__main__":
    fig_uv_spectral_bands()
    fig_erythemal_action()
    fig_silicon_vs_widegap()
    fig_matrix_compensation()
    print("All figures generated successfully.")
