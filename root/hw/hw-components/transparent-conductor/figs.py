# -*- coding: utf-8 -*-
"""Фігури теми «Прозорі провідники». svgkit імпортуємо зі scripts/, не переписуємо."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра теми:
OPT_UV  = "#8e44ad"   # УФ поглинання
OPT_VIS = "#27ae60"   # видиме вікно
OPT_IR  = "#d35400"   # ІЧ відбиття
ITO_COL = "#2980b9"   # оксид індію-олова
AG_COL  = "#7f8c8d"   # срібні нанодроти
POLY_COL= "#e67e22"   # полімери (PEDOT)


# ── fig 1: оптичне вікно прозорості TCO ─────────────────────────────────────────
# Спектр пропускання та відбиття від УФ до ІЧ: між міжзонним поглинанням та плазмовим відбиттям
def fig_optical_window():
    W, H = 840, 420
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 34, "Оптичне вікно прозорості плівки TCO (ITO товщиною ~150 нм)",
                  size=15, color=INK, bold=True))

    # Рамка графіка
    gx, gy, gw, gh = 90, 70, 680, 260
    p.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke=LINE, sw=1.5, rx=0))

    # Зони спектра (фонові смуги)
    # Шкала: 200 нм -> x=90; 380 нм -> x=200; 780 нм -> x=450; 2500 нм -> x=770
    x_uv_end = gx + int(gw * (380 - 200) / (2500 - 200) * 1.5)      # ~180 px
    x_vis_end = gx + int(gw * (780 - 200) / (2500 - 200) * 1.5)     # ~440 px
    
    # Розрахуємо нелінійну/гарну розкладку по довжині хвилі
    # 200-380 нм (УФ): 90..210 (w=120)
    # 380-780 нм (Видиме): 210..470 (w=260)
    # 780-2500 нм (Ближній ІЧ): 470..770 (w=300)
    x0, x1, x2, x3 = gx, gx + 120, gx + 380, gx + gw

    p.append(rect(x0, gy, x1 - x0, gh, fill="#f5eef8", stroke="none", rx=0))
    p.append(rect(x1, gy, x2 - x1, gh, fill="#eafaf1", stroke="none", rx=0))
    p.append(rect(x2, gy, x3 - x2, gh, fill="#fef5e7", stroke="none", rx=0))

    # Вертикальні розділювачі зон
    p.append(line(x1, gy, x1, gy + gh, color="#a569bd", sw=1.5, dash="4 4"))
    p.append(line(x2, gy, x2, gy + gh, color="#e67e22", sw=1.5, dash="4 4"))

    # Підписи зон спектра зверху графіка
    p.append(text((x0 + x1) / 2, gy + 22, "Ультрафіолет (UV)", size=12, color="#7d3c98", bold=True))
    p.append(text((x1 + x2) / 2, gy + 22, "Видиме світло (380–780 нм)", size=13, color="#1e8449", bold=True))
    p.append(text((x2 + x3) / 2, gy + 22, "Ближній інфрачервоний діапазон (NIR)", size=12, color="#b9770e", bold=True))

    # Горизонтальна сітка 0%, 50%, 100%
    for pct, y_val in ((0, gy + gh), (50, gy + gh / 2), (100, gy)):
        p.append(line(gx, y_val, gx + gw, y_val, color="#e5e7eb", sw=1))
        p.append(text(gx - 10, y_val + 4, "%d%%" % pct, size=11, color=MUTED, anchor="end"))

    # Крива пропускання T(λ) — зелена
    # UV: 0% -> крутий підйом біля 350-380 нм -> 88-92% у видимому -> спад до 10% в ІЧ після 1200-1500 нм
    t_pts = [
        (x0, gy + gh - 4), (x0 + 60, gy + gh - 4),
        (x0 + 95, gy + gh - 20), (x1, gy + gh - 190), (x1 + 30, gy + gh - 230),
        (x1 + 100, gy + gh - 234), (x1 + 180, gy + gh - 230), (x2, gy + gh - 220),
        (x2 + 50, gy + gh - 185), (x2 + 110, gy + gh - 110), (x2 + 180, gy + gh - 40),
        (x3, gy + gh - 10)
    ]
    t_str = " ".join("%.1f,%.1f" % pt for pt in t_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (t_str, FIELD))

    # Крива відбиття R(λ) — помаранчева/червона
    # UV: ~15% -> спад у видимому до ~10% -> різкий підйом на плазмовій довжині λ_p -> 85-90% в ІЧ
    r_pts = [
        (x0, gy + gh - 40), (x0 + 60, gy + gh - 35), (x1, gy + gh - 25),
        (x1 + 80, gy + gh - 20), (x1 + 180, gy + gh - 22), (x2, gy + gh - 35),
        (x2 + 50, gy + gh - 70), (x2 + 110, gy + gh - 150), (x2 + 180, gy + gh - 215),
        (x3, gy + gh - 232)
    ]
    r_str = " ".join("%.1f,%.1f" % pt for pt in r_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6 3"/>' % (r_str, OPT_IR))

    # Маркери та виноски ключових фізичних меж
    # 1. Міжзонне поглинання
    p.append(circle(x1 - 10, gy + gh - 100, 4, fill="#8e44ad", stroke=INK, sw=1.5))
    p.append(arrow(x1 - 50, gy + gh - 140, x1 - 14, gy + gh - 104, color="#8e44ad", sw=1.8))
    p.append(text(x1 - 55, gy + gh - 146, "Міжзонне поглинання", size=11, color="#7d3c98", anchor="end", bold=True))
    p.append(text(x1 - 55, gy + gh - 132, "ħω > Eg (електрони валентної зони)", size=10, color=MUTED, anchor="end"))

    # 2. Висока прозорість у видимому
    p.append(text((x1 + x2) / 2, gy + gh - 246, "Пропускання T > 85–90%", size=12, color=FIELD, bold=True))

    # 3. Плазмова частота / довжина хвилі
    p.append(circle(x2 + 110, gy + gh - 130, 4, fill=OPT_IR, stroke=INK, sw=1.5))
    p.append(arrow(x2 + 170, gy + gh - 80, x2 + 116, gy + gh - 124, color=OPT_IR, sw=1.8))
    p.append(text(x2 + 176, gy + gh - 84, "Плазмова довжина хвилі λp", size=11.5, color=OPT_IR, anchor="start", bold=True))
    p.append(text(x2 + 176, gy + gh - 70, "ω < ωp: плазмове відбиття R > 85%", size=10.5, color=MUTED, anchor="start"))

    # Осі та підписи довжин хвиль знизу
    p.append(line(gx, gy + gh, gx + gw, gy + gh, color=INK, sw=1.8))
    wavelengths = [(x0, "200"), (x1, "380"), (x1 + 130, "550"), (x2, "780"), (x2 + 110, "1300"), (x3, "2500 нм")]
    for wx, wlbl in wavelengths:
        p.append(line(wx, gy + gh, wx, gy + gh + 6, color=INK, sw=1.5))
        p.append(text(wx, gy + gh + 20, wlbl, size=11, color=INK))
    p.append(text(gx + gw / 2, gy + gh + 42, "Довжина хвилі світла λ (нм)", size=12, color=INK, bold=True))

    # Легенда
    lx, ly = gx + gw - 220, gy + 45
    p.append(rect(lx, ly, 210, 52, fill=BG, stroke=MUTED, sw=1, rx=4))
    p.append(line(lx + 10, ly + 16, lx + 40, ly + 16, color=FIELD, sw=3))
    p.append(text(lx + 48, ly + 20, "Пропускання T(λ)", size=11, color=INK, anchor="start", bold=True))
    p.append(line(lx + 10, ly + 36, lx + 40, ly + 36, color=OPT_IR, sw=2.5, dash="5 3"))
    p.append(text(lx + 48, ly + 40, "Відбиття R(λ)", size=11, color=INK, anchor="start", bold=True))

    render(os.path.join(OUT, "optical-window.svg"), W, H, *p,
           title="Оптичне вікно прозорості прозорих оксидних провідників")


# ── fig 2: ефект Бурштейна — Мосса ─────────────────────────────────────────────
# Зонна діаграма E(k): фундаментальна зона vs вироджене заповнення зони провідності
def fig_burstein_moss():
    W, H = 840, 390
    p = []

    p.append(text(W / 2, 30, "Ефект Бурштейна — Мосса: оптичне розширення забороненої зони",
                  size=15, color=INK, bold=True))

    def draw_band_diagram(cx, is_doped, title_text, sub_text):
        c = []
        c.append(text(cx, 64, title_text, size=13.5, color=INK, bold=True))
        c.append(text(cx, 80, sub_text, size=11, color=MUTED))

        # Межі діаграми
        bx, by, bw, bh = cx - 160, 94, 320, 250
        c.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke="#d1d5db", sw=1.2, rx=6))

        # Вісь k (горизонтальна) і вісь E (вертикальна)
        c.append(line(cx - 130, by + 130, cx + 130, by + 130, color="#bdc3c7", sw=1, dash="3 3"))
        c.append(arrow(cx, by + bh - 15, cx, by + 15, color=INK, sw=1.5))
        c.append(text(cx + 8, by + 24, "E", size=12, color=INK, bold=True))
        c.append(text(cx + 135, by + 134, "k", size=12, color=INK, bold=True))

        # Парабола валентної зони (спрямована вниз, вершина на E_v)
        # E_v при y = 260
        ev_y = by + 190
        pts_vb = []
        for i in range(-12, 13):
            k_val = i * 10
            y_val = ev_y + 0.005 * (k_val ** 2)
            pts_vb.append("%.1f,%.1f" % (cx + k_val, y_val))
        c.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_vb), NEG))
        c.append(text(cx - 100, ev_y + 35, "Валентна зона (VB)", size=11, color=NEG, bold=True))

        # Парабола зони провідності (спрямована вгору, дно на E_c)
        ec_y = by + 90
        pts_cb = []
        for i in range(-12, 13):
            k_val = i * 10
            y_val = ec_y - 0.005 * (k_val ** 2)
            pts_cb.append("%.1f,%.1f" % (cx + k_val, y_val))
        c.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_cb), POS))
        c.append(text(cx - 100, ec_y - 30, "Зона провідності (CB)", size=11, color=POS, bold=True))

        if not is_doped:
            # Рівень Фермі в забороненій зоні
            ef_y = by + 140
            c.append(line(cx - 110, ef_y, cx + 110, ef_y, color="#7f8c8d", sw=1.5, dash="4 4"))
            c.append(text(cx + 114, ef_y + 4, "EF", size=11.5, color="#7f8c8d", anchor="start", bold=True))

            # Стрілка оптичного переходу Eg0 (від VB до дна CB)
            c.append(arrow(cx, ev_y - 2, cx, ec_y + 2, color=OPT_UV, sw=2.2))
            c.append(text(cx + 14, (ev_y + ec_y) / 2 + 4, "Eg⁰", size=13, color=OPT_UV, bold=True))
            c.append(text(cx, by + bh - 12, "Фундаментальний перехід: ħω ≥ Eg⁰", size=11, color=INK))
        else:
            # Вироджений рівень Фермі всередині зони провідності
            ef_y = ec_y - 32
            c.append(line(cx - 110, ef_y, cx + 110, ef_y, color=OPT_IR, sw=2, dash="5 3"))
            c.append(text(cx + 114, ef_y + 4, "EF (виродження)", size=11, color=OPT_IR, anchor="start", bold=True))

            # Заповнені електрони нижче EF (сині точки / штрихування)
            for i in range(-8, 9):
                k_val = i * 9
                cb_bot = ec_y - 0.005 * (k_val ** 2)
                if cb_bot > ef_y:
                    c.append(line(cx + k_val, cb_bot, cx + k_val, ef_y, color="#cbd5e1", sw=4))

            # Заборонені переходи через принцип Паулі
            c.append(line(cx, ev_y - 2, cx, ec_y + 2, color="#94a3b8", sw=1.6, dash="3 3"))
            c.append(text(cx - 16, (ev_y + ec_y) / 2 + 4, "Eg⁰", size=11, color="#94a3b8"))
            c.append(circle(cx, (ev_y + ec_y) / 2, 8, fill="none", stroke=POS, sw=1.5))
            c.append(line(cx - 6, (ev_y + ec_y) / 2 - 6, cx + 6, (ev_y + ec_y) / 2 + 6, color=POS, sw=1.5))

            # Дозволений прямий оптичний перехід до незаповнених станів вище EF
            kf = 80
            kf_y_vb = ev_y + 0.005 * (kf ** 2)
            c.append(arrow(cx + kf, kf_y_vb - 2, cx + kf, ef_y + 2, color=FIELD, sw=2.4))
            c.append(text(cx + kf + 12, (kf_y_vb + ef_y) / 2 + 4, "Egᵒᵖᵗ = Eg⁰ + ΔEᵍ_BM",
                          size=11.5, color=FIELD, anchor="start", bold=True))
            c.append(text(cx, by + bh - 12, "Заборона Паулі блокує переходи до дна CB", size=11, color=INK))

        return c

    p += draw_band_diagram(210, False, "Нелегований оксид (діелектрик)", "Рівень Фермі EF посередині забороненої зони")
    p += draw_band_diagram(630, True, "Сильнолегований TCO (n > 10²⁰ см⁻³)", "EF заходить у зону провідності (вироджений електронний газ)")

    # Розділювач
    p.append(line(420, 70, 420, 350, color="#e5e7eb", sw=1.5, dash="4 4"))

    render(os.path.join(OUT, "burstein-moss.svg"), W, H, *p,
           title="Ефект Бурштейна — Мосса та блокування Паулі")


# ── fig 3: кристалічна структура та легування ITO і AZO ────────────────────────
# Схема кристалічної ґратки In2O3:Sn та механізм заміщення іонів
def fig_tco_lattice_doping():
    W, H = 840, 370
    p = []

    p.append(text(W / 2, 30, "Механізми генерації вільних носіїв у TCO: легування заміщенням та вакансії",
                  size=14.5, color=INK, bold=True))

    def panel_ito(x0, y0):
        c = []
        c.append(text(x0 + 170, y0 + 15, "Оксид індію-олова (ITO: In₂O₃:Sn)", size=13.5, color=ITO_COL, bold=True))
        c.append(text(x0 + 170, y0 + 32, "Sn⁴⁺ заміщує In³⁺ у вузлах ґратки біксбіїту", size=11, color=MUTED))

        # Грати атомів (спрощена 2D сітка)
        grid_x, grid_y = x0 + 30, y0 + 50
        nodes = [
            (0, 0, "In³⁺", ITO_COL), (1, 0, "O²⁻", "#e74c3c"), (2, 0, "In³⁺", ITO_COL), (3, 0, "O²⁻", "#e74c3c"),
            (0, 1, "O²⁻", "#e74c3c"), (1, 1, "Sn⁴⁺", "#8e44ad"), (2, 1, "O²⁻", "#e74c3c"), (3, 1, "In³⁺", ITO_COL),
            (0, 2, "In³⁺", ITO_COL), (1, 2, "O²⁻", "#e74c3c"), (2, 2, "Vo••", "#f39c12"), (3, 2, "O²⁻", "#e74c3c"),
            (0, 3, "O²⁻", "#e74c3c"), (1, 3, "In³⁺", ITO_COL), (2, 3, "O²⁻", "#e74c3c"), (3, 3, "In³⁺", ITO_COL)
        ]
        step = 62
        # Зв'язки
        for row in range(4):
            for col in range(4):
                if col < 3:
                    c.append(line(grid_x + col * step, grid_y + row * step, grid_x + (col + 1) * step, grid_y + row * step, color="#cbd5e1", sw=1.5))
                if row < 3:
                    c.append(line(grid_x + col * step, grid_y + row * step, grid_x + col * step, grid_y + (row + 1) * step, color="#cbd5e1", sw=1.5))

        # Атоми
        for col, row, label, colr in nodes:
            nx, ny = grid_x + col * step, grid_y + row * step
            if label == "Vo••":
                c.append(circle(nx, ny, 16, fill="#fef9e7", stroke=colr, sw=2))
                c.append(text(nx, ny + 4, "Vo••", size=10, color=colr, bold=True))
            elif label == "Sn⁴⁺":
                c.append(circle(nx, ny, 18, fill="#f4ecf7", stroke=colr, sw=2.5))
                c.append(text(nx, ny + 4, label, size=11, color=colr, bold=True))
                # Вибитий вільний електрон
                c.append(arrow(nx + 14, ny - 14, nx + 32, ny - 28, color=POS, sw=1.8))
                c.append(circle(nx + 36, ny - 32, 6, fill="#fee2e2", stroke=POS, sw=1.5))
                c.append(text(nx + 36, ny - 29, "e⁻", size=9, color=POS, bold=True))
            else:
                c.append(circle(nx, ny, 14 if "O" in label else 16, fill=BG, stroke=colr, sw=1.8))
                c.append(text(nx, ny + 4, label, size=10 if "O" in label else 10.5, color=colr, bold=True))

        c.append(text(x0 + 170, y0 + 265, "Sn⁴⁺ постачає 1 e⁻; киснева вакансія Vo•• постачає 2 e⁻", size=10.5, color=INK))
        return c

    def panel_azo(x0, y0):
        c = []
        c.append(text(x0 + 170, y0 + 15, "Оксид цинку з алюмінієм (AZO: ZnO:Al)", size=13.5, color=FIELD, bold=True))
        c.append(text(x0 + 170, y0 + 32, "Al³⁺ заміщує Zn²⁺ у вюрцитній ґратці", size=11, color=MUTED))

        grid_x, grid_y = x0 + 30, y0 + 50
        nodes = [
            (0, 0, "Zn²⁺", FIELD), (1, 0, "O²⁻", "#e74c3c"), (2, 0, "Zn²⁺", FIELD), (3, 0, "O²⁻", "#e74c3c"),
            (0, 1, "O²⁻", "#e74c3c"), (1, 1, "Al³⁺", "#d35400"), (2, 1, "O²⁻", "#e74c3c"), (3, 1, "Zn²⁺", FIELD),
            (0, 2, "Zn²⁺", FIELD), (1, 2, "O²⁻", "#e74c3c"), (2, 2, "Zn²⁺", FIELD), (3, 2, "O²⁻", "#e74c3c"),
            (0, 3, "O²⁻", "#e74c3c"), (1, 3, "Zn²⁺", FIELD), (2, 3, "O²⁻", "#e74c3c"), (3, 3, "Zn²⁺", FIELD)
        ]
        step = 62
        for row in range(4):
            for col in range(4):
                if col < 3:
                    c.append(line(grid_x + col * step, grid_y + row * step, grid_x + (col + 1) * step, grid_y + row * step, color="#cbd5e1", sw=1.5))
                if row < 3:
                    c.append(line(grid_x + col * step, grid_y + row * step, grid_x + col * step, grid_y + (row + 1) * step, color="#cbd5e1", sw=1.5))

        for col, row, label, colr in nodes:
            nx, ny = grid_x + col * step, grid_y + row * step
            if label == "Al³⁺":
                c.append(circle(nx, ny, 18, fill="#fdf2e9", stroke=colr, sw=2.5))
                c.append(text(nx, ny + 4, label, size=11, color=colr, bold=True))
                c.append(arrow(nx + 14, ny - 14, nx + 32, ny - 28, color=POS, sw=1.8))
                c.append(circle(nx + 36, ny - 32, 6, fill="#fee2e2", stroke=POS, sw=1.5))
                c.append(text(nx + 36, ny - 29, "e⁻", size=9, color=POS, bold=True))
            else:
                c.append(circle(nx, ny, 14 if "O" in label else 16, fill=BG, stroke=colr, sw=1.8))
                c.append(text(nx, ny + 4, label, size=10 if "O" in label else 10.5, color=colr, bold=True))

        c.append(text(x0 + 170, y0 + 265, "Al³⁺ заміщує Zn²⁺, вивільняючи 1 електрон провідності", size=10.5, color=INK))
        return c

    p += panel_ito(40, 50)
    p += panel_azo(460, 50)
    p.append(line(420, 60, 420, 330, color="#e5e7eb", sw=1.5, dash="4 4"))

    render(os.path.join(OUT, "tco-lattice-doping.svg"), W, H, *p,
           title="Кристалічна ґратка та легування оксидів ITO та AZO")


# ── fig 4: компроміс пропускання vs поверхневий опір ────────────────────────────
# Діаграма T vs R_sq для різних технологій та криві фактора якості Хааке (Haacke FOM)
def fig_sheet_resistance_tradeoff():
    W, H = 840, 430
    p = []

    p.append(text(W / 2, 30, "Оптико-електричний компроміс: пропускання (T) проти опору (R_sq)",
                  size=15, color=INK, bold=True))

    gx, gy, gw, gh = 90, 65, 700, 290
    p.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke=LINE, sw=1.5, rx=0))

    # Вісь Y: Пропускання T (%) від 60% до 100%
    # y = gy + gh - (T - 60) / 40 * gh
    # Вісь X: log10(R_sq) від 1 Ом/кв до 1000 Ом/кв (3 декади: 1, 10, 100, 1000)
    # x = gx + (log10(R) - 0) / 3 * gw

    # Горизонтальні лінії T
    for t_val in (60, 70, 80, 85, 90, 95, 100):
        y_pos = gy + gh - (t_val - 60) / 40.0 * gh
        p.append(line(gx, y_pos, gx + gw, y_pos, color="#e5e7eb", sw=1))
        p.append(text(gx - 8, y_pos + 4, "%d%%" % t_val, size=11, color=MUTED, anchor="end"))

    # Вертикальні лінії R_sq
    for exp_val, r_lbl in ((0, "1"), (1, "10"), (2, "100"), (3, "1000")):
        x_pos = gx + exp_val / 3.0 * gw
        p.append(line(x_pos, gy, x_pos, gy + gh, color="#e5e7eb", sw=1))
        p.append(text(x_pos, gy + gh + 18, r_lbl, size=11, color=INK))

    p.append(text(gx + gw / 2, gy + gh + 38, "Питомий поверхневий опір R_sq (Ом/кв, логарифмічна шкала)", size=12, color=INK, bold=True))
    p.append(text(gx - 45, gy + gh / 2, "Пропускання T на 550 нм (%)", size=12, color=INK, bold=True, anchor="middle"))

    # Цільова індустріальна зона (Touch / OLED: T > 88%, R_sq < 30 Ом/кв)
    # R_sq від 5 до 30 -> log10(5)=0.7, log10(30)=1.47 -> x від gx + 0.7/3*gw до gx + 1.47/3*gw
    x_targ_0 = gx + 0.699 / 3.0 * gw
    x_targ_1 = gx + 1.477 / 3.0 * gw
    y_targ_top = gy + gh - (100 - 60) / 40.0 * gh
    y_targ_bot = gy + gh - (88 - 60) / 40.0 * gh
    p.append(rect(x_targ_0, y_targ_top, x_targ_1 - x_targ_0, y_targ_bot - y_targ_top,
                  fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    p.append(text((x_targ_0 + x_targ_1) / 2, y_targ_top + 20, "Дисплеї та тачскріни", size=11, color=FIELD, bold=True))
    p.append(text((x_targ_0 + x_targ_1) / 2, y_targ_top + 34, "(T > 88%, R_sq < 30 Ω/sq)", size=9.5, color=FIELD))

    # Області матеріалів (еліпси або прямокутники з заокругленням)
    # 1. ITO (In2O3:Sn): R_sq = 10..50 Ω/sq, T = 88..93%
    # log10(10)=1.0, log10(50)=1.7 -> x_c = gx + 1.35/3*gw = gx + 315; y_c = gy + gh - (91-60)/40*gh = gy + 65
    ito_x = gx + 1.25 / 3.0 * gw
    ito_y = gy + gh - (91.0 - 60) / 40.0 * gh
    p.append('<ellipse cx="%.1f" cy="%.1f" rx="45" ry="18" fill="#ebf5fb" stroke="%s" stroke-width="2"/>' % (ito_x, ito_y, ITO_COL))
    p.append(text(ito_x, ito_y + 4, "ITO (еталон)", size=11.5, color=ITO_COL, bold=True))

    # 2. FTO (SnO2:F): R_sq = 8..20 Ω/sq, T = 80..86%
    fto_x = gx + 1.1 / 3.0 * gw
    fto_y = gy + gh - (83.0 - 60) / 40.0 * gh
    p.append('<ellipse cx="%.1f" cy="%.1f" rx="38" ry="16" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/>' % (fto_x, fto_y))
    p.append(text(fto_x, fto_y + 4, "FTO", size=11, color="#b7950b", bold=True))

    # 3. AZO (ZnO:Al): R_sq = 20..100 Ω/sq, T = 84..89%
    azo_x = gx + 1.65 / 3.0 * gw
    azo_y = gy + gh - (86.5 - 60) / 40.0 * gh
    p.append('<ellipse cx="%.1f" cy="%.1f" rx="42" ry="16" fill="#eafaf1" stroke=FIELD stroke-width="2"/>' % (azo_x, azo_y))
    p.append(text(azo_x, azo_y + 4, "AZO", size=11, color=FIELD, bold=True))

    # 4. AgNW (Срібні нанодроти): R_sq = 10..50 Ω/sq, T = 88..92% (гнучкий)
    agnw_x = gx + 1.3 / 3.0 * gw
    agnw_y = gy + gh - (89.5 - 60) / 40.0 * gh
    p.append('<ellipse cx="%.1f" cy="%.1f" rx="50" ry="20" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4 3"/>' % (agnw_x, agnw_y, AG_COL))
    p.append(text(agnw_x + 65, agnw_y - 12, "AgNW (нанодроти, гнучкі)", size=10.5, color=AG_COL, anchor="start", bold=True))

    # 5. Графен (1-4 шари з легуванням): R_sq = 30..300 Ω/sq, T = 88..97%
    grap_x = gx + 2.0 / 3.0 * gw
    grap_y = gy + gh - (93.0 - 60) / 40.0 * gh
    p.append('<ellipse cx="%.1f" cy="%.1f" rx="55" ry="18" fill="#f4f6f7" stroke="#34495e" stroke-width="1.8"/>' % (grap_x, grap_y))
    p.append(text(grap_x, grap_y + 4, "Графен / CNT", size=10.5, color="#34495e", bold=True))

    # 6. PEDOT:PSS (провідний полімер): R_sq = 60..500 Ω/sq, T = 80..88%
    ped_x = gx + 2.25 / 3.0 * gw
    ped_y = gy + gh - (84.0 - 60) / 40.0 * gh
    p.append('<ellipse cx="%.1f" cy="%.1f" rx="50" ry="18" fill="#fef5e7" stroke="%s" stroke-width="1.8"/>' % (ped_x, ped_y, POLY_COL))
    p.append(text(ped_x, ped_y + 4, "PEDOT:PSS", size=10.5, color=POLY_COL, bold=True))

    # Лінії Haacke Figure of Merit (FOM = T^10 / R_sq)
    # Наприклад, FOM = 10^-2 (10000 мкСм) і FOM = 10^-3
    # Для FOM = 10^-2: R_sq = T^10 / 10^-2 -> при T=0.9 -> R_sq = 0.3486 / 0.01 = 34.8 Ω/sq
    # при T=0.85 -> R_sq = 0.1968 / 0.01 = 19.7 Ω/sq; при T=0.95 -> R_sq = 0.5987 / 0.01 = 59.9 Ω/sq
    fom_pts = []
    for t_pct in range(70, 99, 2):
        t_dec = t_pct / 100.0
        r_fom = (t_dec ** 10) / 0.01
        if 1 <= r_fom <= 1000:
            import math
            fx = gx + math.log10(r_fom) / 3.0 * gw
            fy = gy + gh - (t_pct - 60) / 40.0 * gh
            fom_pts.append("%.1f,%.1f" % (fx, fy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5 4"/>' % (" ".join(fom_pts), "#8e44ad"))
    p.append(text(gx + 1.8 / 3.0 * gw, gy + 45, "Крива Хааке FOM = T¹⁰ / R_sq = 10⁻² Ω⁻¹", size=10.5, color="#8e44ad", italic=True))

    render(os.path.join(OUT, "sheet-resistance-tradeoff.svg"), W, H, *p,
           title="Порівняння прозорих провідників за фактором якості Хааке")


# ── fig 5: інтеграція в сенсорні дисплеї та OLED ───────────────────────────────
# Ліворуч: ємнісний тачскрін (ромбоподібна ITO сітка Tx/Rx); Праворуч: стек OLED/Сонячного елемента
def fig_touchscreen_oled_stack():
    W, H = 860, 420
    p = []

    p.append(text(W / 2, 28, "Застосування TCO: сенсорні матриці (Touch) та оптоелектронні стеки (OLED)",
                  size=15, color=INK, bold=True))

    # ── Ліва панель: Touchscreen Diamond Pattern ──
    def draw_touch(x0, y0):
        c = []
        c.append(text(x0 + 170, y0 + 15, "Проєкційно-ємнісний тачскрін (PCAP)", size=13.5, color=INK, bold=True))
        c.append(text(x0 + 170, y0 + 32, "Ромбовидна ITO-сітка рядків (Tx) та стовпчиків (Rx)", size=11, color=MUTED))

        bx, by, bw, bh = x0 + 15, y0 + 45, 310, 280
        c.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))

        # Намалюємо ромби Tx (водії, синій) і Rx (сенсори, зелений)
        # Горизонтальні лінії Tx (з'єднані горизонтально)
        # Вертикальні лінії Rx (з'єднані вертикально через діелектричні містки)
        cx0, cy0 = bx + 65, by + 65
        d_step = 60
        # Ромби Tx (рядки)
        for r in range(4):
            for c_idx in range(4):
                rx = cx0 + c_idx * d_step
                ry = cy0 + r * d_step
                # Ромб Tx
                pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
                    rx, ry - 18, rx + 18, ry, rx, ry + 18, rx - 18, ry
                )
                c.append('<polygon points="%s" fill="#ebf5fb" stroke="%s" stroke-width="1.6"/>' % (pts, ITO_COL))
                # Горизонтальний перемикач
                if c_idx < 3:
                    c.append(line(rx + 18, ry, rx + d_step - 18, ry, color=ITO_COL, sw=3))

        # Перемикачі Rx між ромбами (ізольовані містками)
        for r in range(3):
            for c_idx in range(4):
                rx = cx0 + c_idx * d_step
                ry = cy0 + r * d_step + d_step / 2
                # Вертикальний місток
                c.append(rect(rx - 5, ry - 7, 10, 14, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=2))
                c.append(line(rx, ry - 14, rx, ry + 14, color=FIELD, sw=2.5))

        # Палець над сенсором (зміна взаємної ємності ΔC_m)
        c.append(circle(cx0 + 90, cy0 + 60, 22, fill="#fed7aa", stroke="#ea580c", sw=2))
        c.append(text(cx0 + 90, cy0 + 64, "Палець", size=10, color="#9a3412", bold=True))
        # Лінії поля
        c.append(line(cx0 + 75, cy0 + 82, cx0 + 65, cy0 + 105, color="#ea580c", sw=1.4, dash="3 3"))
        c.append(line(cx0 + 105, cy0 + 82, cx0 + 115, cy0 + 105, color="#ea580c", sw=1.4, dash="3 3"))
        c.append(text(cx0 + 90, cy0 + 100, "ΔCm", size=10, color="#ea580c", bold=True))

        c.append(text(x0 + 170, y0 + 305, "ITO прозорий: оком сітка не помітна на дисплеї", size=10.5, color=INK))
        return c

    # ── Права панель: Стек OLED / Сонячного елемента ──
    def draw_oled_stack(x0, y0):
        c = []
        c.append(text(x0 + 190, y0 + 15, "Стек випромінювача OLED (Bottom Emission)", size=13.5, color=INK, bold=True))
        c.append(text(x0 + 190, y0 + 32, "ITO анод пропускає світло крізь скляну підкладку", size=11, color=MUTED))

        bx, by, bw, bh = x0 + 15, y0 + 45, 360, 280
        c.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))

        # Шари стека (зверху вниз)
        layers = [
            ("Металевий катод (Al / Mg:Ag)", 28, "#94a3b8", "#e2e8f0", False),
            ("Електронно-транспортний шар (ETL)", 22, "#3b82f6", "#eff6ff", False),
            ("Емісійний шар (EML — випромінює світло)", 32, "#eab308", "#fef9c3", True),
            ("Дірковий транспортний шар (HTL)", 22, "#f97316", "#fff7ed", False),
            ("Прозорий анод ITO (~120–150 нм)", 26, ITO_COL, "#dbeafe", False),
            ("Скляна підкладка (Glass Substrate)", 46, "#0284c7", "#f0f9ff", False)
        ]

        curr_y = by + 20
        lx = bx + 25
        lw = 310
        for name, lh, border_col, fill_col, is_eml in layers:
            c.append(rect(lx, curr_y, lw, lh, fill=fill_col, stroke=border_col, sw=1.8, rx=3))
            c.append(text(lx + lw / 2, curr_y + lh / 2 + 4, name, size=11, color=border_col, bold=True))

            # Стрілки фотонів світла з EML донизу крізь ITO та скло
            if is_eml:
                eml_mid = curr_y + lh / 2
                for px in (lx + 60, lx + 155, lx + 250):
                    c.append(circle(px, eml_mid, 4, fill="#ca8a04", stroke="#854d0e", sw=1))

            curr_y += lh + 4

        # Промені світла крізь скло назовні (донизу)
        for px in (lx + 60, lx + 155, lx + 250):
            c.append(arrow(px, curr_y - 20, px, curr_y + 16, color="#ca8a04", sw=2.4))
        c.append(text(lx + lw / 2, curr_y + 28, "Вихід видимого світла до глядача (T > 90%)", size=11.5, color="#854d0e", bold=True))

        return c

    p += draw_touch(30, 45)
    p += draw_oled_stack(430, 45)
    p.append(line(415, 60, 415, 380, color="#e5e7eb", sw=1.5, dash="4 4"))

    render(os.path.join(OUT, "touchscreen-oled-stack.svg"), W, H, *p,
           title="Застосування TCO в сенсорних екранах та світлодіодних дисплеях OLED")


if __name__ == "__main__":
    fig_optical_window()
    fig_burstein_moss()
    fig_tco_lattice_doping()
    fig_sheet_resistance_tradeoff()
    fig_touchscreen_oled_stack()
    print("ok: optical-window, burstein-moss, tco-lattice-doping, sheet-resistance-tradeoff, touchscreen-oled-stack")
