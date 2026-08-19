# -*- coding: utf-8 -*-
"""Фігури до теми «Комірчаста архітектура силового MOSFET».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Розріз комірки VDMOS: шари, шлях струму, BJT і JFET ─────────────────
def fig_vdmos_cross_section():
    W, H = 880, 520
    f = [text(W / 2, 28, "Розріз елементарної комірки VDMOS (Vertical DMOS)", size=17, bold=True)]

    # Координати базових блоків комірки
    cx = W / 2
    top_y = 60
    sub_h = 45
    drift_h = 175
    body_h = 95
    gate_w = 200
    gate_h = 32
    cell_w = 560

    # 1. n⁺ Підкладка (Substrate) - внизу
    sub_y = top_y + body_h + drift_h
    f.append(rect(cx - cell_w / 2, sub_y, cell_w, sub_h, fill="#fdedec", stroke=POS, sw=1.8, rx=0))
    f.append(text(cx, sub_y + 28, "n⁺ Підкладка (хвостик стоку) — сильне легування", size=13, color=POS, bold=True))

    # Стоковий металевий контакт (Drain metallization) під підкладкою
    f.append(rect(cx - cell_w / 2, sub_y + sub_h, cell_w, 20, fill="#d5dbdb", stroke="#7f8c8d", sw=1.5, rx=0))
    f.append(text(cx, sub_y + sub_h + 15, "Нижня суцільна металізація стоку (Drain Pad)", size=12, color=INK, bold=True))

    # 2. n⁻ Епітаксійний дрейфовий шар (Drift Region)
    drift_y = top_y + body_h
    f.append(rect(cx - cell_w / 2, drift_y, cell_w, drift_h, fill="#fcf3cf", stroke="#f1c40f", sw=1.8, rx=0))
    f.append(text(cx - cell_w / 2 + 130, drift_y + 100, "n⁻ Епітаксійний дрейфовий шар", size=13, color="#7d6608", bold=True))
    f.append(text(cx - cell_w / 2 + 130, drift_y + 120, "(витримує високу напругу BV_DSS)", size=11, color="#7d6608"))

    # 3. p-Тіло (p-body wells) — ліва і права чаші
    bw = 190
    lx = cx - cell_w / 2
    rx = cx + cell_w / 2 - bw
    f.append(rect(lx, top_y, bw, body_h, fill="#e8f8f5", stroke="#16a085", sw=1.8, rx=0))
    f.append(rect(rx, top_y, bw, body_h, fill="#e8f8f5", stroke="#16a085", sw=1.8, rx=0))
    f.append(text(lx + 70, top_y + 40, "p-Тіло (p-body)", size=13, color="#0e6251", bold=True))
    f.append(text(rx + bw - 70, top_y + 40, "p-Тіло (p-body)", size=13, color="#0e6251", bold=True))

    # 4. p⁺ Контакти тіла (p⁺ body contact) — по краях
    pw = 55
    f.append(rect(lx, top_y, pw, 40, fill="#a3e4d7", stroke="#117864", sw=1.5, rx=0))
    f.append(rect(rx + bw - pw, top_y, pw, 40, fill="#a3e4d7", stroke="#117864", sw=1.5, rx=0))
    f.append(text(lx + pw / 2, top_y + 25, "p⁺", size=13, color="#0b5345", bold=True))
    f.append(text(rx + bw - pw / 2, top_y + 25, "p⁺", size=13, color="#0b5345", bold=True))

    # 5. n⁺ Витокові області (n⁺ source wells)
    sw = 65
    f.append(rect(lx + pw, top_y, sw, 35, fill="#fadbd8", stroke=POS, sw=1.5, rx=0))
    f.append(rect(rx + bw - pw - sw, top_y, sw, 35, fill="#fadbd8", stroke=POS, sw=1.5, rx=0))
    f.append(text(lx + pw + sw / 2, top_y + 22, "n⁺ витік", size=11, color=POS, bold=True))
    f.append(text(rx + bw - pw - sw / 2, top_y + 22, "n⁺ витік", size=11, color=POS, bold=True))

    # 6. Тонкий підзатворний оксид (Gate Oxide) над проміжком між p-чашами
    ox_y = top_y - 8
    f.append(rect(cx - gate_w / 2, ox_y, gate_w, 8, fill="#ebf5fb", stroke="#2980b9", sw=1.2, rx=0))

    # 7. Полікремнієвий затвор (Polysilicon Gate)
    f.append(rect(cx - gate_w / 2, ox_y - gate_h, gate_w, gate_h, fill="#eaeded", stroke="#34495e", sw=1.8, rx=3))
    f.append(text(cx, ox_y - gate_h / 2 + 5, "Полікремнієвий затвор (Gate)", size=12, color="#2c3e50", bold=True))

    # 8. Верхня металізація витоку (Source Metal) з короткозамикачем n⁺ та p⁺
    f.append(rect(lx - 20, top_y - 25, pw + sw + 30, 25, fill="#bdc3c7", stroke="#7f8c8d", sw=1.5, rx=0))
    f.append(rect(rx + bw - pw - sw - 10, top_y - 25, pw + sw + 30, 25, fill="#bdc3c7", stroke="#7f8c8d", sw=1.5, rx=0))
    f.append(text(lx + 45, top_y - 10, "Метал витоку (Source)", size=11, color=INK, bold=True))
    f.append(text(rx + bw - 45, top_y - 10, "Метал витоку (Source)", size=11, color=INK, bold=True))

    # Канали під затвором
    ch_l_x = lx + pw + sw
    ch_l_w = bw - (pw + sw)
    ch_r_x = rx
    ch_r_w = bw - (pw + sw)
    f.append(rect(ch_l_x, top_y, ch_l_w, 10, fill="#d4efdf", stroke=FIELD, sw=1.0, rx=0))
    f.append(rect(ch_r_x, top_y, ch_r_w, 10, fill="#d4efdf", stroke=FIELD, sw=1.0, rx=0))
    f.append(text(cx - 75, top_y + 20, "канал L_ch", size=10, color=FIELD, bold=True))
    f.append(text(cx + 75, top_y + 20, "канал L_ch", size=10, color=FIELD, bold=True))

    # Горловина JFET (між двома p-body чашами)
    jfet_w = rx - (lx + bw)
    jx1, jy1, jx2, jy2 = cx - jfet_w / 2, top_y, cx + jfet_w / 2, top_y + body_h
    f.append(line(jx1, jy1, jx2, jy1, color="#e67e22", sw=1.5, dash="4,3"))
    f.append(line(jx2, jy1, jx2, jy2, color="#e67e22", sw=1.5, dash="4,3"))
    f.append(line(jx2, jy2, jx1, jy2, color="#e67e22", sw=1.5, dash="4,3"))
    f.append(line(jx1, jy2, jx1, jy1, color="#e67e22", sw=1.5, dash="4,3"))
    f.append(text(cx, top_y + 45, "Паразитна JFET", size=11, color="#b95e04", bold=True))
    f.append(text(cx, top_y + 62, "область звуження", size=10, color="#b95e04"))

    # Струмові стрілки (Шлях електронів: витік -> горизонтальний канал -> накопичення -> дрейф униз)
    f.append(arrow(lx + pw + sw / 2, top_y + 35, ch_l_x + 5, top_y + 5, color=FIELD, sw=2.2))
    f.append(arrow(ch_l_x + 5, top_y + 5, cx - 35, top_y + 5, color=FIELD, sw=2.2))
    f.append(arrow(cx - 35, top_y + 5, cx - 20, top_y + body_h + 30, color=FIELD, sw=2.2))
    f.append(arrow(cx - 20, top_y + body_h + 30, cx - 20, sub_y + sub_h, color=FIELD, sw=2.5))

    f.append(arrow(rx + bw - pw - sw / 2, top_y + 35, ch_r_x + ch_r_w - 5, top_y + 5, color=FIELD, sw=2.2))
    f.append(arrow(ch_r_x + ch_r_w - 5, top_y + 5, cx + 35, top_y + 5, color=FIELD, sw=2.2))
    f.append(arrow(cx + 35, top_y + 5, cx + 20, top_y + body_h + 30, color=FIELD, sw=2.2))
    f.append(arrow(cx + 20, top_y + body_h + 30, cx + 20, sub_y + sub_h, color=FIELD, sw=2.5))

    # Виноски збоку: Паразитний BJT і закорочення
    box_bjt, _, _ = textbox(110, 420, "Паразитний n-p-n BJT:\nЕмітер: n⁺ витік\nБаза: p-тіло\nКолектор: n⁻ дрейф",
                            size=11, pad=8, fill="#fdfefe", stroke=POS)
    f.append(box_bjt)

    box_short, _, _ = textbox(770, 420, "Закорочення Source-Body:\nМетал з'єднує n⁺ та p⁺,\nщоб струм витоку не відмикав\nпаразитний біполярник",
                              size=11, pad=8, fill="#eafaf1", stroke=FIELD)
    f.append(box_short)

    f.append(text(W / 2, H - 12,
                  "Струм тече вертикально крізь весь кристал: сток знизу, витік і затвор згори.",
                  size=12.5, color=INK))
    render(os.path.join(IMG, "vdmos-cross-section.svg"), W, H, *f)


# ── 2. Порівняння Trench MOSFET проти Shielded-Gate Trench MOSFET ───────────
def fig_trench_vs_shielded():
    W, H = 880, 500
    f = [text(W / 2, 28, "Еволюція траншейного затвора: U-MOS проти Shielded-Gate Trench", size=17, bold=True)]

    # Ліва панель: Стандартний Trench MOSFET
    lw, lh = 380, 390
    lx, ly = 45, 55
    f.append(rect(lx, ly, lw, lh, fill="#fbfcfc", stroke=MUTED, sw=1.6, rx=8))
    f.append(text(lx + lw / 2, ly + 26, "Стандартний Trench MOSFET (U-MOS)", size=14, bold=True, color="#2c3e50"))

    # Права панель: Shielded-Gate (Split-Gate) MOSFET
    rw, rh = 380, 390
    rx, ry = 455, 55
    f.append(rect(rx, ry, rw, rh, fill="#f4fbf7", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(rx + rw / 2, ry + 26, "Shielded-Gate (Split-Gate) Trench", size=14, bold=True, color="#1e8449"))

    def draw_trench_half(x0, is_shielded=False):
        res = []
        tw = 70
        th = 230 if is_shielded else 170
        tx = x0 + 190 - tw / 2
        ty = ly + 80
        lw = tx - (x0 + 40)   # 115 px
        rw = lw               # 115 px
        rx_pos = tx + tw

        # 1. n⁺ витік (зліва і справа від траншеї)
        res.append(rect(x0 + 40, ty, lw, 35, fill="#fadbd8", stroke=POS, sw=1.2, rx=0))
        res.append(rect(rx_pos, ty, rw, 35, fill="#fadbd8", stroke=POS, sw=1.2, rx=0))
        res.append(text(x0 + 40 + lw / 2, ty + 22, "n⁺ витік", size=11, color=POS, bold=True))
        res.append(text(rx_pos + rw / 2, ty + 22, "n⁺ витік", size=11, color=POS, bold=True))

        # 2. p-тіло (зліва і справа від траншеї)
        res.append(rect(x0 + 40, ty + 35, lw, 75, fill="#e8f8f5", stroke="#16a085", sw=1.2, rx=0))
        res.append(rect(rx_pos, ty + 35, rw, 75, fill="#e8f8f5", stroke="#16a085", sw=1.2, rx=0))
        res.append(text(x0 + 40 + lw / 2, ty + 75, "p-тіло", size=12, color="#0e6251", bold=True))
        res.append(text(rx_pos + rw / 2, ty + 75, "p-тіло", size=12, color="#0e6251", bold=True))

        # 3. n⁻ дрейф (зліва, справа і знизу під траншеєю)
        res.append(rect(x0 + 40, ty + 110, lw, 150, fill="#fcf3cf", stroke="#f1c40f", sw=1.2, rx=0))
        res.append(rect(rx_pos, ty + 110, rw, 150, fill="#fcf3cf", stroke="#f1c40f", sw=1.2, rx=0))
        if ty + th < ty + 260:
            res.append(rect(tx, ty + th, tw, (ty + 260) - (ty + th), fill="#fcf3cf", stroke="#f1c40f", sw=1.2, rx=0))
        res.append(text(x0 + 40 + lw / 2, ty + 180, "n⁻ дрейф", size=11, color="#7d6608", bold=True))
        res.append(text(rx_pos + rw / 2, ty + 180, "n⁻ дрейф", size=11, color="#7d6608", bold=True))

        # 4. Траншея
        res.append(rect(tx, ty, tw, th, fill="#ebf5fb", stroke="#2980b9", sw=1.8, rx=4))

        if not is_shielded:
            # Один суцільний затвор у траншеї
            res.append(rect(tx + 6, ty + 6, tw - 12, th - 12, fill="#eaeded", stroke="#34495e", sw=1.4, rx=2))
            res.append(text(tx + tw / 2, ty + th / 2, "Затвор (G)", size=12, color="#2c3e50", bold=True))
            # Велика ємність на дні C_gd
            res.append(line(tx, ty + th, tx + tw, ty + th, color=POS, sw=3.0))
            res.append(arrow(x0 + 190, ly + lh - 40, x0 + 190, ty + th + 4, color=POS, sw=1.5))
            box_cgd, _, _ = textbox(x0 + 190, ly + lh - 22, "Велика паразитна C_gd на дні!", size=10.5, pad=5, fill="#fdedec", stroke=POS)
            res.append(box_cgd)
        else:
            # Split-Gate: Верхній затвор (Gate)
            gw_h = 100
            res.append(rect(tx + 6, ty + 6, tw - 12, gw_h, fill="#eaeded", stroke="#34495e", sw=1.4, rx=2))
            res.append(text(tx + tw / 2, ty + 55, "Затвор (G)", size=11, color="#2c3e50", bold=True))

            # Товстий оксид ізоляції між електродами
            res.append(rect(tx, ty + gw_h + 6, tw, 18, fill="#d6eaf8", stroke="#2980b9", sw=1.0, rx=0))

            # Нижній екран (Shield Electrode) з'єднаний з витоком
            sh_h = th - gw_h - 30
            res.append(rect(tx + 8, ty + gw_h + 24, tw - 16, sh_h, fill="#d5dbdb", stroke="#7f8c8d", sw=1.4, rx=2))
            res.append(text(tx + tw / 2, ty + gw_h + 24 + sh_h / 2 + 4, "Екран (S)", size=11, color=INK, bold=True))
            res.append(arrow(x0 + 190, ly + lh - 40, x0 + 190, ty + th + 4, color=FIELD, sw=1.5))
            box_sh, _, _ = textbox(x0 + 190, ly + lh - 22, "C_gd знижено у 3–5 разів екраном!", size=10.5, pad=5, fill="#eafaf1", stroke=FIELD)
            res.append(box_sh)

        # Вертикальні канали уздовж стінок траншеї
        res.append(line(tx - 3, ty + 35, tx - 3, ty + 110, color=FIELD, sw=2.5, dash="3,2"))
        res.append(line(tx + tw + 3, ty + 35, tx + tw + 3, ty + 110, color=FIELD, sw=2.5, dash="3,2"))
        res.append(text(tx - 20, ty + 75, "канал", size=10, color=FIELD, bold=True))
        res.append(text(tx + tw + 20, ty + 75, "канал", size=10, color=FIELD, bold=True))

        return res

    f.extend(draw_trench_half(lx, is_shielded=False))
    f.extend(draw_trench_half(rx, is_shielded=True))

    box_note, _, _ = textbox(W / 2, H - 24,
                             "Траншея усуває JFET-звуження й робить канал вертикальним; екрануючий електрод розряджає заряд Міллера Q_gd.",
                             size=12, pad=6, fill="#fdfefe", stroke=MUTED)
    f.append(box_note)

    render(os.path.join(IMG, "trench-vs-shielded.svg"), W, H, *f)


# ── 3. Superjunction: стовпчики компенсації заряду та профіль поля ─────────
def fig_superjunction_field():
    W, H = 880, 480
    f = [text(W / 2, 28, "Superjunction (CoolMOS): компенсація заряду та вирівнювання поля", size=17, bold=True)]

    # Ліва частина: Структура p/n стовпчиків
    lx, ly, lw, lh = 45, 55, 380, 360
    f.append(rect(lx, ly, lw, lh, fill="#fbfcfc", stroke=MUTED, sw=1.6, rx=8))
    f.append(text(lx + lw / 2, ly + 24, "Структура Superjunction (чергування p/n)", size=13.5, bold=True, color="#2c3e50"))

    # Стовпчики
    pw = 36
    px_start = lx + 45
    py_start = ly + 50
    p_h = 240
    num_p = 4

    for i in range(num_p):
        cur_x = px_start + i * pw * 2
        # n-стовпчик (донорний)
        f.append(rect(cur_x, py_start, pw, p_h, fill="#fef9e7", stroke="#f39c12", sw=1.2, rx=0))
        f.append(text(cur_x + pw / 2, py_start + 40, "n", size=12, color="#b7950b", bold=True))
        # p-стовпчик (акцепторний)
        f.append(rect(cur_x + pw, py_start, pw, p_h, fill="#e8f8f5", stroke="#16a085", sw=1.2, rx=0))
        f.append(text(cur_x + pw + pw / 2, py_start + 40, "p", size=12, color="#0e6251", bold=True))

        # Стрілки бічного збіднення (E_x)
        if i < num_p - 1:
            f.append(arrow(cur_x + pw - 2, py_start + 120, cur_x + 2, py_start + 120, color=NEG, sw=1.5))
            f.append(arrow(cur_x + pw + 2, py_start + 120, cur_x + pw * 2 - 2, py_start + 120, color=NEG, sw=1.5))

    f.append(text(lx + lw / 2, py_start + 150, "Поперечне взаємне", size=11, color=NEG, bold=True))
    f.append(text(lx + lw / 2, py_start + 168, "збіднення (E_x)", size=11, color=NEG, bold=True))

    f.append(rect(px_start, py_start + p_h, num_p * pw * 2, 25, fill="#fadbd8", stroke=POS, sw=1.4, rx=0))
    f.append(text(lx + lw / 2, py_start + p_h + 16, "n⁺ Підкладка стоку", size=11, color=POS, bold=True))

    f.append(text(lx + lw / 2, ly + lh - 18, "Баланс зарядів: N_A · W_p = N_D · W_n", size=12, color=FIELD, bold=True))

    # Права частина: Порівняння профілю електричного поля E(y)
    rx, ry, rw, rh = 455, 55, 380, 360
    f.append(rect(rx, ry, rw, rh, fill="#fdfefe", stroke=MUTED, sw=1.6, rx=8))
    f.append(text(rx + rw / 2, ry + 24, "Профіль напруженості поля E(y) при пробої", size=13.5, bold=True, color="#2c3e50"))

    ox, oy = rx + 60, ry + 280
    ax_w, ax_h = 280, 200

    # Осі координат
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.6))
    f.append(text(ox + ax_w, oy + 20, "глибина y", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - ax_h + 10, "E_крит", size=11, color=POS, anchor="end", bold=True))

    # 1. Трикутний профіль для класичного VDMOS (червоний штрих)
    f.append(line(ox, oy - 170, ox + 180, oy, color=POS, sw=2.4, dash="5,4"))
    f.append(text(ox + 80, oy - 110, "Класичний VDMOS", size=11, color=POS, bold=True))
    f.append(text(ox + 80, oy - 94, "Площа = ½ · E_c · W_d", size=10, color=POS))

    # 2. Прямокутний профіль для Superjunction (зелений)
    f.append(line(ox, oy - 170, ox + 180, oy - 170, color=FIELD, sw=2.6))
    f.append(line(ox + 180, oy - 170, ox + 180, oy, color=FIELD, sw=2.6))
    f.append(text(ox + 90, oy - 180, "Superjunction (CoolMOS)", size=11, color=FIELD, bold=True))
    f.append(text(ox + 90, oy - 145, "Площа = E_c · W_epi", size=10.5, color=FIELD, bold=True))
    f.append(text(ox + 90, oy - 130, "(вдвічі більша напруга BV!)", size=10, color=FIELD))

    f.append(text(rx + rw / 2, ry + rh - 18, "Рівномірне поле ламає класичну межу Баліги", size=12, color=INK, bold=True))

    f.append(text(W / 2, H - 12,
                  "Поперечне збіднення дозволяє сильно легувати стовпчики, зберігаючи прямокутний профіль поля.",
                  size=12.5, color=INK))
    render(os.path.join(IMG, "superjunction-field.svg"), W, H, *f)


# ── 4. Бюджет складових опору R_DS(on) для різних класів напруг ─────────────
def fig_rdson_budget():
    W, H = 880, 460
    f = [text(W / 2, 28, "Розподіл складових опору R_DS(on) залежно від класу напруги", size=17, bold=True)]

    # 3 стовпчики: 30V Trench, 600V Planar VDMOS, 600V Superjunction
    col_w = 170
    col_h = 270
    base_y = 360

    cols = [
        ("30 В Trench", 110, [
            ("R_ch (канал)", 0.60, "#2ecc71"),
            ("R_sub (підкладка)", 0.20, "#e74c3c"),
            ("R_cont (контакти/корпус)", 0.12, "#95a5a6"),
            ("R_drift (дрейф)", 0.08, "#f1c40f"),
        ], "Домінує опір каналу:\nпотрібна макс. щільність комірок"),

        ("600 В VDMOS (планар)", 355, [
            ("R_drift (дрейфовий шар)", 0.88, "#f1c40f"),
            ("R_JFET (звуження)", 0.06, "#e67e22"),
            ("R_ch (канал)", 0.04, "#2ecc71"),
            ("R_sub / R_cont", 0.02, "#95a5a6"),
        ], "90% опору в дрейфовому шарі:\nмежа Баліги R ~ BV^2.5"),

        ("600 В Superjunction", 600, [
            ("R_drift (стовпчики)", 0.45, "#f1c40f"),
            ("R_ch (канал)", 0.30, "#2ecc71"),
            ("R_sub (підкладка)", 0.15, "#e74c3c"),
            ("R_cont (контакти)", 0.10, "#95a5a6"),
        ], "R_drift зменшено у 5–8 разів:\nразом R_DS(on) впав у рази"),
    ]

    for title, cx, segments, comment in cols:
        f.append(text(cx + col_w / 2, base_y - col_h - 18, title, size=14, bold=True, color="#2c3e50"))
        cur_y = base_y
        for label, fraction, color in segments:
            seg_h = col_h * fraction
            f.append(rect(cx, cur_y - seg_h, col_w, seg_h, fill=color, stroke="#2c3e50", sw=1.2, rx=0))
            # Текст всередині секції, якщо поміщається
            if seg_h > 24:
                f.append(text(cx + col_w / 2, cur_y - seg_h / 2 + 4, "%s (%d%%)" % (label.split()[0], int(fraction * 100)),
                              size=11, bold=True, color="#1a1a1a"))
            cur_y -= seg_h

        # Підпис знизу
        f.append(mtext(cx + col_w / 2, base_y + 22, comment, size=11, color=MUTED, lh=1.25))

    f.append(text(W / 2, H - 12,
                  "У низьковольтних MOSFET усе вирішує геометрія каналу; у високовольтних — фізика дрейфового шару.",
                  size=12.5, color=INK))
    render(os.path.join(IMG, "rdson-budget.svg"), W, H, *f)


# ── 5. Топологія кристала згори: Gate Pad, Gate Runners, комірчаста матриця ─
def fig_gate_mesh_top_view():
    W, H = 880, 480
    f = [text(W / 2, 28, "Топологія кристала силового MOSFET: затворна сітка (Gate Mesh)", size=17, bold=True)]

    # Корпус / кристал
    dx, dy, dw, dh = 190, 55, 500, 360
    f.append(rect(dx, dy, dw, dh, fill="#eaeded", stroke="#7f8c8d", sw=2.0, rx=8))

    # Витокова металізація (Source Metal Plate) — покриває більшу частину площі
    f.append(rect(dx + 25, dy + 25, dw - 50, dh - 50, fill="#d5dbdb", stroke="#95a5a6", sw=1.5, rx=6))
    f.append(text(dx + dw / 2 + 60, dy + 180, "Потужна металізація витоку (Source)", size=15, bold=True, color="#2c3e50"))
    f.append(text(dx + dw / 2 + 60, dy + 204, "покриває мільйони паралельних комірок", size=12, color=MUTED))

    # Затворний майданчик (Gate Pad) у кутку
    gpx, gpy, gpw, gph = dx + 35, dy + 35, 75, 75
    f.append(rect(gpx, gpy, gpw, gph, fill="#f9e79f", stroke="#d4ac0d", sw=2.0, rx=4))
    f.append(text(gpx + gpw / 2, gpy + gph / 2 + 5, "Gate Pad", size=12, bold=True, color="#7d6608"))

    # Металеві шини затвора (Gate Runners / Gate Fingers)
    gr_color = "#f39c12"
    gr_w = 12
    # Горизонтальна верхня шина
    f.append(rect(gpx + gpw, gpy + 10, dw - 150, gr_w, fill=gr_color, stroke="#b9770e", sw=1.2, rx=2))
    # Вертикальна бічна шина
    f.append(rect(gpx + 10, gpy + gph, gr_w, dh - 160, fill=gr_color, stroke="#b9770e", sw=1.2, rx=2))
    # Центральний палець (Gate Finger)
    f.append(rect(dx + 80, dy + dh / 2 - gr_w / 2, dw - 140, gr_w, fill=gr_color, stroke="#b9770e", sw=1.2, rx=2))

    f.append(text(dx + 270, dy + gpy + 2, "Головна металева шина затвора (Gate Runner)", size=11, color="#7d6608", bold=True))
    f.append(text(dx + 280, dy + dh / 2 + 22, "Розподілений палець затвора (знижує R_g)", size=11, color="#7d6608", bold=True))

    # Виноски зліва і справа
    box_l, _, _ = textbox(100, 230, "Полікремній:\nвисокий питомий\nопір 20 Ом/кв.\nЗатримує сигнал!",
                          size=11, pad=8, fill="#fefde8", stroke="#d4ac0d")
    f.append(box_l)

    box_r, _, _ = textbox(780, 230, "Металеві шини:\nалюміній/мідь\nмиттєво роздають\nзаряд мільйонам\nкомірок одночасно",
                          size=11, pad=8, fill="#eafaf1", stroke=FIELD)
    f.append(box_r)

    f.append(text(W / 2, H - 12,
                  "Металева сітка (Gate Mesh) запобігає асинхронному вмиканню периферійних комірок і паразитній генерації.",
                  size=12.5, color=INK))
    render(os.path.join(IMG, "gate-mesh-top-view.svg"), W, H, *f)


# ── 6. Графік межі Баліги (Silicon Limit vs Superjunction vs WBG) ───────────
def fig_baliga_limit_curve():
    W, H = 880, 500
    f = [text(W / 2, 28, "Кремнієва межа Баліги проти Superjunction та SiC/GaN", size=17, bold=True)]

    ox, oy = 110, 410
    ax_w, ax_h = 680, 340

    # Осі координат
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))

    # Позначки осі X: Напруга BV_DSS (10 В, 100 В, 1000 В)
    f.append(text(ox + ax_w - 20, oy + 25, "Пробивна напруга BV_DSS (В, логарифмічна шкала)", size=12, color=INK, bold=True, anchor="end"))
    x_ticks = [(10, 0), (30, 0.24), (100, 0.50), (300, 0.74), (1000, 1.0)]
    for v, frac in x_ticks:
        tx = ox + frac * (ax_w - 40)
        f.append(line(tx, oy, tx, oy + 6, color=INK, sw=1.5))
        f.append(text(tx, oy + 20, "%d" % v, size=11, color=MUTED))

    # Позначки осі Y: Питомий опір R_sp (0.01, 0.1, 1, 10, 100, 1000 мОм·см²)
    f.append(text(ox - 15, oy - ax_h + 10, "R_DS(on) · A (мОм·см²)", size=12, color=INK, bold=True, anchor="end"))
    y_ticks = [("0.01", 0.05), ("0.1", 0.23), ("1", 0.41), ("10", 0.59), ("100", 0.77), ("1000", 0.95)]
    for v_str, frac in y_ticks:
        ty = oy - frac * (ax_h - 20)
        f.append(line(ox - 6, ty, ox, ty, color=INK, sw=1.5))
        f.append(text(ox - 10, ty + 4, v_str, size=11, color=MUTED, anchor="end"))
        f.append(line(ox, ty, ox + ax_w, ty, color="#eaeded", sw=1.0, dash="3,4"))

    # 1. 1D Класична кремнієва межа Баліги: нахил 2.5 (R ~ BV^2.5) — червона лінія
    f.append(line(ox + 40, oy - 25, ox + ax_w - 100, oy - 310, color=POS, sw=2.8))
    box_b1, _, _ = textbox(ox + 310, oy - 270, "1D Кремнієва межа Баліги: R_sp ∝ BV^2.5",
                           size=11, pad=5, fill="#fdfefe", stroke=POS)
    f.append(box_b1)

    # 2. Superjunction кремній: нахил 1.0 (R ~ BV^1.0) — зелена лінія
    f.append(line(ox + 0.5 * (ax_w - 40), oy - 0.41 * (ax_h - 20), ox + ax_w - 40, oy - 0.65 * (ax_h - 20), color=FIELD, sw=2.8))
    box_sj, _, _ = textbox(ox + 520, oy - 165, "Superjunction (CoolMOS): R_sp ∝ BV^1.0",
                           size=11, pad=5, fill="#eafaf1", stroke=FIELD)
    f.append(box_sj)

    # 3. Карбід кремнію (SiC) та нітрид галію (GaN) — синя лінія
    f.append(line(ox + 40, oy - 5, ox + ax_w - 40, oy - 190, color=NEG, sw=2.4, dash="6,3"))
    box_wbg, _, _ = textbox(ox + 550, oy - 65, "Межа SiC / GaN (у 100–300 разів нижче)",
                            size=11, pad=5, fill="#eaf0fd", stroke=NEG)
    f.append(box_wbg)

    # Стрілка виграшу Superjunction
    mid_x = ox + 0.82 * (ax_w - 40)
    f.append(arrow(mid_x, oy - 275, mid_x, oy - 220, color=FIELD, sw=2.2))
    box_gain, _, _ = textbox(mid_x, oy - 290, "Виграш R_sp у 5–10 разів при 600 В",
                             size=10.5, pad=4, fill="#f4fbf7", stroke=FIELD)
    f.append(box_gain)

    f.append(text(W / 2, H - 12,
                  "Superjunction перетворює степеневу залежність на лінійну завдяки компенсації заряду в дрейфовій зоні.",
                  size=12.5, color=INK))
    render(os.path.join(IMG, "baliga-limit-curve.svg"), W, H, *f)


if __name__ == "__main__":
    fig_vdmos_cross_section()
    fig_trench_vs_shielded()
    fig_superjunction_field()
    fig_rdson_budget()
    fig_gate_mesh_top_view()
    fig_baliga_limit_curve()
    print("Згенеровано 6 фігур у", IMG)
