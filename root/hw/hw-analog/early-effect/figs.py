# -*- coding: utf-8 -*-
"""Фігури до теми «Ефект Ерлі».
Три фігури:
  basewidth.svg — фізика: зона збіднення з'їдає базу, коли росте Vce (W → W')
  output.svg    — вихідні характеристики Ic(Vce): віяло прямих, що сходяться в −Va
  ro.svg        — наслідок: похила пряма = скінченний вихідний опір ro = Va/Ic
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: фізика — звуження бази при зростанні Vce ──────────────────────
def fig_basewidth():
    W, H = 720, 360
    P = []
    # дві однакові «плити» транзистора: ліворуч мала напруга, праворуч велика
    def stack(x0, y0, wtot, h, depl, title, vlabel):
        # три шари: емітер | база (нейтральна) | колектор; між базою й колектором — зона збіднення
        we = wtot * 0.26          # емітер
        wc = wtot * 0.30          # колектор (фіксований початок)
        # ширина зони збіднення в базу залежить від depl (0..1)
        wd = (wtot - we - wc) * (0.18 + 0.55 * depl)   # скільки з'їдено
        wb = wtot - we - wc - wd                        # нейтральна база, що лишилась
        out = []
        cx = x0
        # емітер
        out.append(rect(cx, y0, we, h, fill="#eef3ff", stroke=INK, sw=1.4, rx=2))
        out.append(text(cx + we / 2, y0 + h + 18, "емітер", size=12, color=NEG))
        cx += we
        # нейтральна база (зелена) — те, що реально працює
        out.append(rect(cx, y0, wb, h, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=2))
        out.append(text(cx + wb / 2, y0 + h / 2 + 4, "база", size=12, color=FIELD, bold=True))
        bx_right = cx + wb
        cx += wb
        # зона збіднення (заштрихована-світла) — «з'їдена» частина бази
        out.append(rect(cx, y0, wd, h, fill="#fdecea", stroke=POS, sw=1.4, rx=2))
        cx += wd
        # колектор
        out.append(rect(cx, y0, wc, h, fill="#f4f6f8", stroke=INK, sw=1.4, rx=2))
        out.append(text(cx + wc / 2, y0 + h + 18, "колектор", size=12, color=MUTED))
        # розмір нейтральної бази — стрілка під базою
        ay = y0 + h + 40
        out.append(arrow(x0 + we, ay, bx_right, ay, color=FIELD, sw=1.6))
        out.append(arrow(bx_right, ay, x0 + we, ay, color=FIELD, sw=1.6))
        out.append(text((x0 + we + bx_right) / 2, ay + 18, vlabel, size=13, color=FIELD, bold=True))
        # підпис зверху
        out.append(text(x0 + wtot / 2, y0 - 14, title, size=13, color=INK, bold=True))
        return "".join(out), bx_right

    y0, h = 90, 110
    left, _ = stack(60, y0, 250, h, depl=0.0, title="мала Vce", vlabel="W")
    right, _ = stack(410, y0, 250, h, depl=1.0, title="велика Vce", vlabel="W′ < W")
    P.append(left)
    P.append(right)
    # стрілка-перехід між картинами
    P.append(arrow(322, y0 + h / 2, 398, y0 + h / 2, color=INK, sw=2.2))
    P.append(text(360, y0 + h / 2 - 12, "Vce ↑", size=13, color=POS, bold=True))
    # підпис зони збіднення — внизу, на матеріалі правої картини
    tb = fitbox(250, 300, 220, 44,
                "рожеве — зона збіднення:\nросте в базу зі зростанням Vce",
                size=11, color=POS, stroke=POS, fill="#fdecea")
    P.append(tb)
    render(os.path.join(IMG, "basewidth.svg"), W, H, *P,
           title="Колекторна напруга з'їдає базу зсередини")


# ── Фігура 2: вихідні характеристики — віяло, що сходиться в −Va ─────────────
def fig_output():
    W, H = 720, 450
    P = []
    ox, oy = 250, 380          # початок осей (нуль) — зсунутий праворуч, щоб лишити місце для −Va
    aw, ah = 420, 300          # довжина осей праворуч/угору
    negx = 175                 # скільки осі тягнемо ліворуч від нуля (для −Va)
    # осі
    P.append(arrow(ox - negx, oy, ox + aw, oy, color=INK, sw=1.8))
    P.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    P.append(text(ox + aw - 4, oy + 26, "Vce", size=13, color=INK, anchor="end", italic=True))
    P.append(text(ox + 8, oy - ah + 8, "Ic", size=13, color=INK, anchor="start", italic=True))
    P.append(text(ox, oy + 22, "0", size=12, color=MUTED))
    # точка −Va на осі (ліворуч від нуля)
    vax = ox - negx + 18
    P.append(circle(vax, oy, 4, fill=INK, stroke=INK))
    P.append(text(vax, oy + 24, "−Va", size=13, color=POS, bold=True))
    P.append(text(vax, oy - 16, "точка сходу", size=11, color=MUTED))
    # три характеристики для різних Ib: усі прямі, з ПОМІРНИМ спільним нахилом,
    # продовжені пунктиром вліво — вони сходяться в околі −Va (зумисне обмежений нахил,
    # щоб лінії не вилазили за полотно: справжня −Va далеко лівіше за край малюнка).
    knee = ox + aw * 0.10       # коліно — кінець насичення, початок активного режиму
    x_end = ox + aw - 6
    levels = [0.30, 0.48, 0.66]   # струм у коліні (частка ah)
    labels = ["Ib мала", "Ib середня", "Ib велика"]
    rise_frac = 0.16              # на скільки (частка ah) лінія підніметься за активний пробіг
    for lv, lab in zip(levels, labels):
        y_knee = oy - lv * ah
        # спільний помірний нахил угору-праворуч
        slope = -(rise_frac * ah) / (x_end - knee)
        y_end = y_knee + slope * (x_end - knee)
        # суцільна частина (активний режим) від коліна праворуч
        P.append(line(knee, y_knee, x_end, y_end, color=INK, sw=2.2))
        # пунктир-продовження вліво до осі — перетин природно лягає в околі −Va
        x_axis = knee + (oy - y_knee) / slope     # де лінія перетне Ic=0 (вісь Vce)
        x_axis = max(x_axis, vax - 30)            # тримати в межах полотна
        P.append(line(knee, y_knee, x_axis, oy, color=MUTED, sw=1.2, dash="6 5"))
        # ділянка насичення — круте підняття від 0 до коліна
        P.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (ox, oy, ox + (knee - ox) * 0.35, y_knee, knee, y_knee, INK))
        # підпис струму бази праворуч
        P.append(text(x_end + 4, y_end + 4, lab, size=11, color=MUTED, anchor="start"))
    # вертикаль коліна
    P.append(line(knee, oy, knee, oy - ah + 20, color=MUTED, sw=1.0, dash="3 4"))
    P.append(text(knee, oy - ah + 14, "насичення | активний режим", size=11, color=MUTED))
    # ідеал: горизонтальна пунктирна для порівняння (як «мало б бути»)
    y_ideal = oy - 0.43 * ah
    P.append(line(knee, y_ideal, ox + aw - 6, y_ideal, color=NEG, sw=1.4, dash="2 5"))
    P.append(text(ox + aw - 6, y_ideal - 8, "ідеал: горизонталь", size=11, color=NEG, anchor="end"))
    # підпис нахилу
    tb = fitbox(ox + 40, oy - ah + 30, 230, 40,
                "реальність: лінії трохи піднімаються\n— це й є ефект Ерлі",
                size=11, color=INK, stroke=INK, fill=FILL)
    P.append(tb)
    render(os.path.join(IMG, "output.svg"), W, H, *P,
           title="Вихідні характеристики сходяться в одну точку −Va")


# ── Фігура 3: наслідок — скінченний вихідний опір ro ────────────────────────
def fig_ro():
    W, H = 680, 360
    P = []
    # ліворуч: ідеальне джерело струму (горизонталь) → ro = ∞
    # праворуч: реальне (похила лінія) → ro скінченне
    def axes(ox, oy, aw, ah, lab):
        out = [arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6),
               arrow(ox, oy, ox, oy - ah, color=INK, sw=1.6),
               text(ox + aw - 4, oy + 20, "Vce", size=12, color=INK, anchor="end", italic=True),
               text(ox + 6, oy - ah + 6, "Ic", size=12, color=INK, anchor="start", italic=True),
               text(ox + aw / 2, oy + 40, lab, size=12, color=INK, bold=True, anchor="middle")]
        return "".join(out)

    # ліва панель
    ox, oy, aw, ah = 70, 250, 220, 180
    P.append(axes(ox, oy, aw, ah, "ідеал: ro = ∞"))
    yflat = oy - ah * 0.6
    P.append(line(ox + aw * 0.12, yflat, ox + aw - 6, yflat, color=NEG, sw=2.4))
    P.append(text(ox + aw * 0.55, yflat - 10, "струм не залежить від Vce", size=10,
                  color=NEG, anchor="middle"))

    # права панель
    ox2 = 400
    P.append(axes(ox2, oy, aw, ah, "реальність: ro = Va / Ic"))
    x1, y1 = ox2 + aw * 0.12, oy - ah * 0.50
    x2 = ox2 + aw - 6
    slope = -0.30 * ah / aw
    y2 = y1 + slope * (x2 - x1)
    P.append(line(x1, y1, x2, y2, color=POS, sw=2.4))
    # трикутник нахилу: ΔVce / ΔIc
    P.append(line(x1 + 50, y1 + slope * 50, x1 + 50, y1, color=MUTED, sw=1.2, dash="3 3"))
    P.append(line(x1, y1, x1 + 50, y1, color=MUTED, sw=1.2, dash="3 3"))
    P.append(text(x1 + 25, y1 - 6, "ΔVce", size=10, color=MUTED))
    P.append(text(x1 + 58, y1 + slope * 25, "ΔIc", size=10, color=MUTED, anchor="start"))
    # рамка з формулою опору як 1/нахил
    tb = fitbox(ox2 + 20, oy - ah - 4, 200, 38,
                "нахил ≠ 0 → скінченний опір\nro = ΔVce / ΔIc = Va / Ic",
                size=11, color=POS, stroke=POS, fill="#fdecea")
    P.append(tb)
    render(os.path.join(IMG, "ro.svg"), W, H, *P,
           title="Нахил кривої — це вихідний опір транзистора")


if __name__ == "__main__":
    fig_basewidth()
    fig_output()
    fig_ro()
    print("OK: 3 figures ->", IMG)
