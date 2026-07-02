# -*- coding: utf-8 -*-
# Фігури для ДЕТАЛЬНОЇ статті «Налаштування ПІД» (pid-tuning-cascade-d.md).
# Базові фігури — у figs.py; тут лише додаткові, глибші.
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


# ── 1. Насичення привода й розкручування інтеграла ────────────────────────────

def fig_windup():
    W, H = 720, 380
    p = []
    ox = 70
    Ax = 590

    # ── верхня панель: вихід і завдання
    oy1 = 130
    top1 = 55
    target1 = 80
    p.append(arrow(ox, oy1, ox, top1, color=INK, sw=1.4))
    p.append(arrow(ox, oy1, ox + Ax, oy1, color=INK, sw=1.4))
    p.append(line(ox, target1, ox + Ax, target1, color=MUTED, sw=1.4, dash="6 4"))
    p.append(text(ox + Ax + 2, target1 + 4, "завдання", size=9.5, color=MUTED, anchor="end"))

    base1 = oy1
    N = 300
    # без анти-віндапу: великий переліт, повільне повернення
    pts_wind = []
    pts_anti = []
    for i in range(N + 1):
        t = i / N * 10.0
        # проста модель: розгін до перельоту, потім осідання
        if t < 0.4:
            yw = base1
            ya = base1
        else:
            tt = t - 0.4
            # без анти-віндапу — велике перехльостування (інтеграл розкрутився)
            envw = math.exp(-0.5 * tt)
            yw = target1 - (target1 - base1) * envw * (1 + 1.15 * math.exp(-0.35 * tt) * math.cos(1.1 * tt - 0.2))
            yw = min(yw, base1)
            # з анти-віндапом — чисте наростання майже без перельоту
            enva = math.exp(-0.95 * tt)
            ya = target1 - (target1 - base1) * enva
        pts_wind.append((ox + (t / 10.0) * Ax, yw))
        pts_anti.append((ox + (t / 10.0) * Ax, ya))
    p.append(polyline(pts_wind, color=NEG, sw=2.6))
    p.append(polyline(pts_anti, color=FIELD, sw=2.6))
    p.append(text(ox + Ax * 0.30, top1 + 6, "без анти-віндапу: великий переліт", size=10, color=NEG, anchor="start", bold=True))
    p.append(text(ox + Ax * 0.55, target1 - 10, "з анти-віндапом", size=10, color=FIELD, anchor="start", bold=True))

    # ── нижня панель: керувальний сигнал і межа насичення
    oy2 = 320
    top2 = 210
    umax = 235
    p.append(arrow(ox, oy2, ox, top2, color=INK, sw=1.4))
    p.append(arrow(ox, oy2, ox + Ax, oy2, color=INK, sw=1.4))
    p.append(text(ox + Ax + 18, oy2 + 4, "час", size=11, color=INK, anchor="end"))
    p.append(line(ox, umax, ox + Ax, umax, color=POS, sw=1.6, dash="5 4"))
    p.append(text(ox + 6, umax - 6, "межа привода u_max (насичення)", size=9.5, color=POS, anchor="start", bold=True))

    # інтеграл, що заходить далеко ЗА межу (розкручений), і обрізаний вихід
    pts_int = []      # «внутрішній» інтеграл — злітає високо над межею
    pts_out = []      # реальний вихід — обрізаний межею
    for i in range(N + 1):
        t = i / N * 10.0
        if t < 0.4:
            raw = oy2
        else:
            tt = t - 0.4
            raw = oy2 - (oy2 - (umax - 55)) * (1 - math.exp(-0.9 * tt)) - 70 * math.exp(-0.25 * tt) * max(0, 1 - 0.25 * tt)
        pts_int.append((ox + (t / 10.0) * Ax, raw))
        pts_out.append((ox + (t / 10.0) * Ax, max(raw, umax)))
    p.append(polyline(pts_int, color=MUTED, sw=2.0, dash="4 3"))
    p.append(polyline(pts_out, color=INK, sw=2.6))
    p.append(text(ox + Ax * 0.5, top2 + 4, "інтеграл розкрутився (внутрішнє u)", size=9.5, color=MUTED, anchor="start"))
    p.append(text(ox + Ax * 0.62, umax + 18, "реальний вихід уперся в межу", size=9.5, color=INK, anchor="start", bold=True))

    render(os.path.join(OUT, "integral-windup.svg"), W, H, *p,
           title="Розкручування інтеграла: привід у насиченні, а інтеграл усе накопичує")


# ── 2. Похідний стрибок і похідна від виміру ──────────────────────────────────

def fig_derivative_kick():
    W, H = 720, 340
    p = []
    ox = 70
    Ax = 590

    # ── верх: завдання-сходинка й гладкий вихід
    oy1 = 120
    top1 = 55
    lo1 = 105
    hi1 = 70
    p.append(arrow(ox, oy1, ox, top1, color=INK, sw=1.4))
    p.append(arrow(ox, oy1, ox + Ax, oy1, color=INK, sw=1.4))
    xj = ox + 0.28 * Ax
    # сходинка завдання
    p.append(polyline([(ox, lo1), (xj, lo1), (xj, hi1), (ox + Ax, hi1)], color=MUTED, sw=2.2, dash="6 4"))
    p.append(text(xj + 6, hi1 - 6, "завдання (стрибок)", size=9.5, color=MUTED, anchor="start"))
    # плавний вихід — виміряна величина
    pts_pv = []
    N = 300
    for i in range(N + 1):
        t = i / N
        x = ox + t * Ax
        if x < xj:
            y = lo1
        else:
            tt = (x - xj) / (Ax) * 6.0
            y = hi1 + (lo1 - hi1) * math.exp(-1.1 * tt)
        pts_pv.append((x, y))
    p.append(polyline(pts_pv, color=INK, sw=2.6))
    p.append(text(ox + Ax * 0.55, lo1 - 6, "вихід (вимір) — плавний", size=9.5, color=INK, anchor="start", bold=True))

    # ── низ: похідна складова у двох варіантах
    oy2 = 285
    top2 = 175
    mid2 = 245
    p.append(arrow(ox, mid2, ox, top2, color=INK, sw=1.4))
    p.append(arrow(ox, mid2, ox + Ax, mid2, color=INK, sw=1.4))
    p.append(line(ox, mid2, ox + Ax, mid2, color=MUTED, sw=1.0))
    p.append(text(ox + Ax + 18, mid2 + 4, "час", size=11, color=INK, anchor="end"))

    # похідна від помилки — велетенський піковий стрибок на сходинці (кік)
    spike_x = xj
    p.append(line(spike_x, mid2, spike_x, top2 + 6, color=POS, sw=3.0))
    p.append(arrow(spike_x, top2 + 12, spike_x, top2 + 4, color=POS, sw=3.0))
    p.append(text(spike_x + 8, top2 + 16, "похідна від ПОМИЛКИ: різкий кік", size=10, color=POS, anchor="start", bold=True))

    # похідна від виміру — гладка від'ємна хвиля (гальмо, реакція лише на рух виміру)
    pts_dm2 = []
    for i in range(N + 1):
        t = i / N
        x = ox + t * Ax
        if x < xj:
            y = mid2
        else:
            tt = (x - xj) / Ax * 6.0
            y = mid2 + 40 * math.exp(-1.1 * tt)
        pts_dm2.append((x, y))
    p.append(polyline(pts_dm2, color=FIELD, sw=2.6))
    p.append(text(ox + Ax * 0.5, mid2 + 56, "похідна від ВИМІРУ: гладке гальмо, без піка", size=10, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "derivative-kick.svg"), W, H, *p,
           title="Похідний стрибок: похідну беруть від виміру, а не від помилки")


# ── 3. Каскад: розділення смуг пропускання (внутрішній ×5 швидший) ─────────────

def fig_bandwidth_separation():
    W, H = 720, 320
    p = []
    ox, oy = 70, 235
    Ax = 600
    Ay = 150

    # осі (лог-частота вздовж X, підсилення вздовж Y — схематично)
    p.append(arrow(ox, oy, ox, oy - Ay - 10, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.4))
    p.append(text(ox + Ax + 16, oy + 4, "частота", size=11, color=INK, anchor="end"))
    p.append(text(ox - 6, oy - Ay - 4, "смуга контуру", size=10, color=INK, anchor="end"))

    # дві криві-«дзвони» смуг: зовнішній (лівий, вужчий) і внутрішній (правий, ширший)
    def bell(cx, w, h):
        pts = []
        for i in range(121):
            t = i / 120
            x = ox + t * Ax
            y = oy - h * math.exp(-((x - cx) ** 2) / (2 * w * w))
            pts.append((x, y))
        return pts

    cx_out = ox + 0.28 * Ax
    cx_in = ox + 0.66 * Ax
    p.append(polyline(bell(cx_out, 0.10 * Ax, Ay * 0.8), color=NEG, sw=2.8))
    p.append(polyline(bell(cx_in, 0.14 * Ax, Ay), color=FIELD, sw=2.8))

    # вертикалі частот зрізу
    p.append(line(cx_out, oy, cx_out, oy - Ay * 0.8, color=NEG, sw=1.2, dash="3 3"))
    p.append(line(cx_in, oy, cx_in, oy - Ay, color=FIELD, sw=1.2, dash="3 3"))
    p.append(text(cx_out, oy + 20, "ω зовн.", size=11, color=NEG, bold=True))
    p.append(text(cx_in, oy + 20, "ω внутр.", size=11, color=FIELD, bold=True))

    # стрілка розриву ×5
    ymid = oy - Ay * 0.55
    p.append(line(cx_out, ymid, cx_in, ymid, color=INK, sw=1.4))
    p.append(arrow(cx_out, ymid, cx_out - 2, ymid, color=INK, sw=1.4))
    p.append(arrow(cx_in, ymid, cx_in + 2, ymid, color=INK, sw=1.4))
    p.append(text((cx_out + cx_in) / 2, ymid - 8, "розрив ≈ ×5", size=12, color=INK, bold=True))

    p.append(text(cx_out, oy - Ay * 0.8 - 8, "зовнішній (кут)", size=10, color=NEG, bold=True))
    p.append(text(cx_in, oy - Ay - 8, "внутрішній (швидкість)", size=10, color=FIELD, bold=True))
    p.append(text(W / 2, oy + 46, "розрив смуг ділить контури: для зовнішнього внутрішній виглядає майже миттєвим",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "bandwidth-separation.svg"), W, H, *p,
           title="Каскад працює лише коли смуги розведені: внутрішній ×5 швидший")


# ── 4. Дискретний ПІД: крок дискретизації й що рахує кожна складова ────────────

def fig_discrete_pid():
    W, H = 720, 320
    p = []
    ox, oy = 70, 235
    Ax = 600
    Ay = 150

    # неперервна помилка (гладка спадна крива)
    def e_cont(t):  # t у [0,1]
        return 1.0 - math.exp(-2.4 * t) * math.cos(3.2 * t)

    # осі
    p.append(arrow(ox, oy, ox, oy - Ay - 10, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.4))
    p.append(text(ox + Ax + 16, oy + 4, "час", size=11, color=INK, anchor="end"))
    p.append(text(ox - 6, oy - Ay - 2, "помилка e", size=10, color=INK, anchor="end"))

    base = oy
    top = oy - Ay
    def Y(v):  # v у [0..~1.4] → координата
        return base - (base - top) * (v / 1.4)

    # гладка неперервна крива
    pts = []
    N = 240
    for i in range(N + 1):
        t = i / N
        pts.append((ox + t * Ax, Y(e_cont(t))))
    p.append(polyline(pts, color=MUTED, sw=2.0, dash="5 4"))
    p.append(text(ox + Ax * 0.55, Y(e_cont(0.55)) - 12, "справжня e(t)", size=9.5, color=MUTED, anchor="start"))

    # дискретні відліки: точки + прямокутники Рімана (інтеграл) + хорда (похідна)
    M = 9
    xs = []
    ys = []
    for k in range(M + 1):
        t = k / M
        x = ox + t * Ax
        v = e_cont(t)
        xs.append(x); ys.append(Y(v))
    dt_px = (xs[1] - xs[0])
    # прямокутники інтеграла (сума e·Δt) — легка заливка
    for k in range(M):
        h = base - ys[k]
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eef7ee" stroke="#cfe6cf" stroke-width="1"/>'
                 % (xs[k], ys[k], dt_px, h))
    # точки відліків
    for k in range(M + 1):
        p.append(circle(xs[k], ys[k], 3.4, fill=NEG, stroke=NEG))
    # ступінчаста ламана (те, що «бачить» МК)
    step_pts = []
    for k in range(M):
        step_pts.append((xs[k], ys[k]))
        step_pts.append((xs[k + 1], ys[k]))
    p.append(polyline(step_pts, color=NEG, sw=1.8))

    # хорда похідної між двома сусідніми відліками (нахил ≈ Δe/Δt)
    ka = 2
    p.append(line(xs[ka], ys[ka], xs[ka + 1], ys[ka + 1], color=POS, sw=3.0))
    p.append(text(xs[ka] - 4, ys[ka] - 10, "нахил = Δe/Δt (D)", size=9.5, color=POS, anchor="start", bold=True))

    # підпис прямокутника
    p.append(text(xs[5] + dt_px / 2, base - 12, "e·Δt (I)", size=9, color=FIELD, bold=True))
    p.append(text(xs[7], oy + 18, "Δt — крок циклу керування", size=10, color=INK, anchor="middle"))

    render(os.path.join(OUT, "discrete-pid.svg"), W, H, *p,
           title="Дискретний ПІД: інтеграл = сума e·Δt, похідна = нахил між відліками")


# ── 5. Дві мети якості: чвертьамплітудне проти без-перельоту ───────────────────

def fig_two_targets():
    W, H = 720, 300
    p = []
    ox, oy = 70, 220
    Ax = 600
    top = 55
    target = 95
    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.4))
    p.append(line(ox, target, ox + Ax, target, color=MUTED, sw=1.4, dash="6 4"))
    p.append(text(ox + Ax + 2, target - 6, "завдання", size=9.5, color=MUTED, anchor="end"))
    p.append(text(ox + Ax + 16, oy + 4, "час", size=11, color=INK, anchor="end"))

    base = oy
    amp = base - target
    N = 300
    # чвертьамплітудне (ζ≈0.21): помітний переліт, кілька гойдань
    def qad(t):
        if t < 0.3:
            return base
        tt = t - 0.3
        z = 0.21
        wn = 1.7
        wd = wn * math.sqrt(1 - z * z)
        env = math.exp(-z * wn * tt)
        return target - amp * env * math.cos(wd * tt)
    # без перельоту (ζ≈1): повільний плавний вихід
    def noos(t):
        if t < 0.3:
            return base
        tt = t - 0.3
        return target + amp * math.exp(-1.15 * tt) * (1 + 1.15 * tt)

    pts1 = [(ox + (i / N) * Ax, qad(i / N * 9.0)) for i in range(N + 1)]
    pts2 = [(ox + (i / N) * Ax, noos(i / N * 9.0)) for i in range(N + 1)]
    p.append(polyline(pts1, color=NEG, sw=2.6))
    p.append(polyline(pts2, color=FIELD, sw=2.6))

    p.append(text(ox + Ax * 0.22, top + 10, "чвертьамплітудне (ζ≈0.21): швидко, з перельотом ~50 %",
                  size=10, color=NEG, anchor="start", bold=True))
    p.append(text(ox + Ax * 0.40, target + 34, "без перельоту (ζ≈1): повільно, зате без стрибка",
                  size=10, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "two-targets.svg"), W, H, *p,
           title="Під що налаштовуємо: швидкість із перельотом чи спокій без нього")


# ── 6. Каскад двох структур pid_t (для вставки proj-anti-windup) ───────────────

def fig_cascade_pid_struct():
    W, H = 760, 340
    p = []

    oy = 92          # верх ряду блоків
    bh = 66          # висота блоків

    # блоки-регулятори та проміжні вузли, зліва направо
    # (x, w, дворядковий підпис, заливка)
    angle_x, angle_w = 150, 132
    clamp_x, clamp_w = 316, 96
    rate_x,  rate_w  = 452, 132
    mot_x,   mot_w   = 626, 104

    # вхід: бажаний кут
    p.append(text(70, oy + bh / 2 - 6, "бажаний", size=11, color=MUTED))
    p.append(text(70, oy + bh / 2 + 9, "кут", size=11, color=MUTED))
    p.append(arrow(104, oy + bh / 2, angle_x, oy + bh / 2, color=INK, sw=1.9))

    # зовнішній контур кута — pid_t
    p.append(fitbox(angle_x, oy, angle_w, bh,
                    "pid_t angle\n(зовнішній: кут)", size=12,
                    fill="#eaf0fd", stroke=NEG, bold=True))

    # затиск завдання ±RATE_MAX
    p.append(arrow(angle_x + angle_w, oy + bh / 2, clamp_x, oy + bh / 2, color=INK, sw=1.9))
    p.append(fitbox(clamp_x, oy + 6, clamp_w, bh - 12,
                    "затиск\n±RATE_MAX", size=11,
                    fill="#f4f6f8", stroke=LINE))

    # внутрішній контур швидкості — pid_t
    p.append(arrow(clamp_x + clamp_w, oy + bh / 2, rate_x, oy + bh / 2, color=INK, sw=1.9))
    p.append(text((clamp_x + clamp_w + rate_x) / 2, oy + bh / 2 - 8,
                  "бажана", size=9.5, color=MUTED))
    p.append(text((clamp_x + clamp_w + rate_x) / 2, oy + bh / 2 + 4,
                  "швидк.", size=9.5, color=MUTED))
    p.append(fitbox(rate_x, oy, rate_w, bh,
                    "pid_t rate\n(внутрішній: швидк.)", size=12,
                    fill="#eafaf0", stroke=FIELD, bold=True))

    # мотори / мікс
    p.append(arrow(rate_x + rate_w, oy + bh / 2, mot_x, oy + bh / 2, color=INK, sw=1.9))
    p.append(fitbox(mot_x, oy + 6, mot_w, bh - 12,
                    "мотор-мікс\n(стеля тяги)", size=11,
                    fill="#fdf6e3", stroke=INK))

    # ── ключова стрілка: насичення знизу вгору (freeze_i) ──
    yb = oy + bh + 66           # рівень нижньої шини сигналу
    rate_cx = rate_x + rate_w / 2
    angle_cx = angle_x + angle_w / 2
    # з-під внутрішнього контуру вниз
    p.append(line(rate_cx, oy + bh, rate_cx, yb, color=POS, sw=2.2))
    # вліво до-під зовнішнього
    p.append(line(rate_cx, yb, angle_cx, yb, color=POS, sw=2.2))
    # вгору в зовнішній контур
    p.append(arrow(angle_cx, yb, angle_cx, oy + bh, color=POS, sw=2.2))
    p.append(text((angle_cx + rate_cx) / 2, yb + 20,
                  "inner.saturated → angle_pid.freeze_i", size=11.5,
                  color=POS, bold=True))
    p.append(text((angle_cx + rate_cx) / 2, yb + 38,
                  "внутрішній у стелі → морозимо інтеграл зовнішнього", size=10,
                  color=MUTED))

    # підпис-розшифровка кольору блоків
    p.append(text(W / 2, H - 14,
                  "обидва блоки — та сама структура pid_t, лише різні коефіцієнти й межі",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "cascade-pid-struct.svg"), W, H, *p,
           title="Каскад із двох pid_t: насичення тече знизу вгору")


if __name__ == "__main__":
    fig_windup()
    fig_derivative_kick()
    fig_bandwidth_separation()
    fig_discrete_pid()
    fig_two_targets()
    fig_cascade_pid_struct()
    print("OK: detailed figures written to", OUT)
