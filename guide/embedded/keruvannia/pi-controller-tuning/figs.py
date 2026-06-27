# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


# ── Спільна модель замкненого ПІ-контуру (для відгуків на стрибок) ─────────────
# Простий об'єкт першого порядку з невеликим запізненням, дискретний інтегратор.
def pi_step(kp, ki, T=10.0, N=600, tau=0.7, lag=0.18, u0=0.0, sat=None):
    """Повертає список (t, y) — відгук виходу на одиничний стрибок завдання r=1.
    tau — стала об'єкта, lag — мертвий час (с), u0 — стале навантаження."""
    dt = T / N
    y = 0.0
    integ = 0.0
    hist = [0.0] * (int(lag / dt) + 1)
    out = []
    for i in range(N + 1):
        t = i * dt
        r = 1.0
        e = r - y
        integ += e * dt
        u = kp * e + ki * integ
        if sat is not None:
            u = max(-sat, min(sat, u))
        hist.append(u)
        u_eff = hist.pop(0)              # вплив доходить із запізненням
        # об'єкт 1-го порядку: dy/dt = (-y + u_eff - u0)/tau
        y += dt * (-y + u_eff - u0) / tau
        out.append((t, y))
    return out


def axes(ox, oy, top, Ax, target_y, label_t="час", band=None, p=None):
    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.5))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.5))
    p.append(text(ox + Ax + 4, oy + 16, label_t, size=11, color=MUTED, anchor="end"))
    p.append(line(ox, target_y, ox + Ax, target_y, color=MUTED, sw=1.4, dash="6 4"))
    p.append(text(ox + Ax + 4, target_y - 4, "завдання", size=10, color=MUTED, anchor="start"))


# ── 1. Дві ручки: площина Kp–Ki ───────────────────────────────────────────────

def fig_two_knobs():
    W, H = 720, 360
    ox, oy = 90, 300
    Ax, Ay = 540, 240
    p = []

    # осі: Kp (горизонталь), Ki (вертикаль)
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - Ay, color=INK, sw=1.6))
    p.append(text(ox + Ax - 6, oy + 22, "Kp  (сила, швидкодія) →", size=12, color=INK, anchor="end", bold=True))
    p.append(text(ox - 16, oy - Ay + 4, "Ki", size=12, color=INK, anchor="end", bold=True))
    p.append(text(ox - 16, oy - Ay + 20, "(↑)", size=10, color=MUTED, anchor="end"))

    # межа стійкості: за нею контур розгойдується (велике Kp АБО велике Ki)
    # крива, що відсікає верхній-правий кут
    pts = []
    for i in range(101):
        fx = i / 100.0
        x = ox + fx * Ax
        # межа: чим більший Kp, тим менший допустимий Ki (і навпаки)
        fy = 0.92 - 0.78 * fx ** 1.6
        fy = max(0.06, fy)
        y = oy - fy * Ay
        pts.append((x, y))
    p.append(polyline(pts, color=POS, sw=2.4))
    p.append(text(ox + Ax * 0.5, oy - Ay * 0.5 - 84, "межа стійкості", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(ox + Ax * 0.52, oy - Ay * 0.5 - 68, "(розгойдування)", size=9.5, color=POS, anchor="start"))

    # область занизько (мляво) — лівий-нижній кут
    p.append(text(ox + Ax * 0.14, oy - Ay * 0.16, "мляво:", size=10.5, color=FIELD, anchor="start", bold=True))
    p.append(text(ox + Ax * 0.14, oy - Ay * 0.16 + 15, "повільно й довго", size=9.5, color=MUTED, anchor="start"))
    p.append(text(ox + Ax * 0.14, oy - Ay * 0.16 + 28, "повзе до завдання", size=9.5, color=MUTED, anchor="start"))

    # добра точка — посередині, під межею
    gx, gy = ox + Ax * 0.42, oy - Ay * 0.40
    p.append(circle(gx, gy, 6, fill=NEG, stroke=NEG))
    p.append(text(gx + 10, gy - 6, "добрий набір", size=11, color=NEG, anchor="start", bold=True))
    p.append(text(gx + 10, gy + 9, "швидко, точно, без дзвону", size=9.5, color=MUTED, anchor="start"))

    # стрілка-діагональ компромісу
    p.append(line(ox + Ax * 0.16, oy - Ay * 0.12, gx - 8, gy + 6, color=MUTED, sw=1.4, dash="4 4"))

    # підпис про взаємодію
    p.append(text(ox + Ax * 0.70, oy - Ay * 0.86, "велике Kp + велике Ki", size=9.5, color=POS, anchor="middle"))
    p.append(text(ox + Ax * 0.70, oy - Ay * 0.86 + 13, "разом → розгойдування", size=9.5, color=POS, anchor="middle"))

    render(os.path.join(OUT, "two-knobs.svg"), W, H, *p,
           title="Налаштування ПІ — це пошук пари (Kp, Ki) під межею стійкості")


# ── 2. Зіглер–Ніколс: ПІ мусить відступити сильніше за ПІД ─────────────────────

def fig_zn_pi_vs_pid():
    W, H = 720, 330
    ox, oy = 80, 250
    top, Ax = 60, 560
    target = 110
    p = []
    axes(ox, oy, top, Ax, target, p=p)

    # ПІД (Kp=0.6Ku, швидкий I, є D) — швидко й чисто; апроксимуємо як спритний відгук
    def curve(kp, ki, color, sw, dash=None, dy=0.0):
        data = pi_step(kp, ki, T=10.0, N=560, tau=0.7, lag=0.16)
        pts = [(ox + (t / 10.0) * Ax, oy - (target - oy) * (-y) + dy) for (t, y) in data]
        # масштаб: y=1 → рівень target
        pts = [(ox + (t / 10.0) * Ax, oy + (target - oy) * y) for (t, y) in data]
        p.append(polyline(pts, color=color, sw=sw, dash=dash))

    # ПІ за ЗН: нижчий Kp, повільніший інтеграл → млявіший вихід
    curve(2.0, 1.1, FIELD, 2.6)                    # ПІ (ZN): помірний
    # ПІД за ЗН: вищий Kp + швидший I (плюс D, тут спрощено вищим Kp/Ki) → швидше
    curve(3.2, 2.3, NEG, 2.6, dash="7 4")          # ПІД (ZN): спритніший

    # легенда
    p.append(line(ox + Ax - 210, top + 8, ox + Ax - 180, top + 8, color=FIELD, sw=2.6))
    p.append(text(ox + Ax - 174, top + 12, "ПІ за ЗН: Kp = 0.45·Ku", size=10.5, color=FIELD, anchor="start", bold=True))
    p.append(line(ox + Ax - 210, top + 28, ox + Ax - 180, top + 28, color=NEG, sw=2.6, dash="7 4"))
    p.append(text(ox + Ax - 174, top + 32, "ПІД за ЗН: Kp = 0.6·Ku", size=10.5, color=NEG, anchor="start", bold=True))

    p.append(text(ox + Ax * 0.5, oy + 34,
                  "без похідної доводиться брати менший Kp і повільніший інтеграл — ПІ виходить статечнішим",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "zn-pi-vs-pid.svg"), W, H, *p,
           title="Та сама межа Ku, але ПІ відступає від неї далі, ніж ПІД")


# ── 3. Удар-тест: крива розгону → модель (K, τ, θ) ─────────────────────────────

def fig_bump_test():
    W, H = 720, 380
    p = []
    ox = 90
    Ax = 560
    # дві смуги: вгорі вплив u (стрибок), внизу вихід y (S-крива)
    oy_u = 120
    oy_y = 330
    Hu = 60
    Hy = 150

    # ── панель впливу u ──
    p.append(arrow(ox, oy_u, ox + Ax + 10, oy_u, color=MUTED, sw=1.3))
    p.append(text(ox + Ax + 12, oy_u + 14, "час", size=10, color=MUTED, anchor="end"))
    t_step = 0.18 * Ax
    p.append(line(ox, oy_u, ox + t_step, oy_u, color=INK, sw=2.4))
    p.append(line(ox + t_step, oy_u, ox + t_step, oy_u - Hu, color=INK, sw=2.4))
    p.append(line(ox + t_step, oy_u - Hu, ox + Ax, oy_u - Hu, color=INK, sw=2.4))
    p.append(text(ox - 8, oy_u - Hu / 2, "вплив u", size=10.5, color=INK, anchor="end", bold=True))
    # величина стрибка Δu
    p.append(line(ox + t_step - 26, oy_u, ox + t_step - 26, oy_u - Hu, color=FIELD, sw=1.4))
    p.append(text(ox + t_step - 30, oy_u - Hu / 2, "Δu", size=10, color=FIELD, anchor="end", bold=True))

    # ── панель виходу y: мертвий час, тоді експонента до плато ──
    p.append(arrow(ox, oy_y, ox + Ax + 10, oy_y, color=MUTED, sw=1.3))
    p.append(text(ox + Ax + 12, oy_y + 14, "час", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 8, oy_y - Hy / 2, "вихід y", size=10.5, color=INK, anchor="end", bold=True))

    dead = 0.10 * Ax                       # мертвий час θ (після стрибка)
    x_dead_end = ox + t_step + dead
    tau_px = 0.26 * Ax                      # стала часу τ
    plateau = oy_y - Hy
    pts = []
    N = 300
    for i in range(N + 1):
        x = ox + (i / N) * Ax
        if x <= x_dead_end:
            y = oy_y
        else:
            tt = (x - x_dead_end) / tau_px
            y = oy_y - Hy * (1 - math.exp(-tt))
        pts.append((x, y))
    p.append(polyline(pts, color=NEG, sw=2.6))

    # плато ΔPV
    p.append(line(ox, plateau, ox + Ax, plateau, color=MUTED, sw=1.2, dash="5 4"))
    p.append(line(ox + Ax - 26, oy_y, ox + Ax - 26, plateau, color=POS, sw=1.4))
    p.append(text(ox + Ax - 30, (oy_y + plateau) / 2, "ΔPV", size=10, color=POS, anchor="end", bold=True))

    # мертвий час θ (від стрибка до старту руху)
    p.append(line(ox + t_step, oy_y + 6, x_dead_end, oy_y + 6, color=FIELD, sw=1.6))
    p.append(text((ox + t_step + x_dead_end) / 2, oy_y + 22, "θ — мертвий час", size=10, color=FIELD, bold=True))
    p.append(line(ox + t_step, oy_y, ox + t_step, oy_y + 10, color=FIELD, sw=1.2))
    p.append(line(x_dead_end, oy_y, x_dead_end, oy_y + 10, color=FIELD, sw=1.2))

    # стала часу τ: до рівня 63 % від плато
    y63 = oy_y - 0.632 * Hy
    x63 = x_dead_end + tau_px
    p.append(line(ox, y63, x63, y63, color=INK, sw=1.0, dash="2 3"))
    p.append(line(x63, oy_y, x63, y63, color=INK, sw=1.0, dash="2 3"))
    p.append(text(x63 + 4, y63 + 14, "63 %", size=9, color=INK, anchor="start"))
    p.append(line(x_dead_end, oy_y - Hy - 8, x63, oy_y - Hy - 8, color=INK, sw=1.4))
    p.append(text((x_dead_end + x63) / 2, oy_y - Hy - 12, "τ — стала часу", size=10, color=INK, bold=True))

    # формула підсилення
    p.append(text(ox + Ax * 0.5, oy_y + 46, "підсилення об'єкта  K = ΔPV / Δu", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "bump-test.svg"), W, H, *p,
           title="Удар-тест: один стрибок впливу дає модель об'єкта (K, τ, θ)")


# ── 4. Одна ручка λ: від статечного до різкого ────────────────────────────────

def fig_lambda_knob():
    W, H = 720, 330
    ox, oy = 80, 250
    top, Ax = 60, 560
    target = 105
    p = []
    axes(ox, oy, top, Ax, target, p=p)

    def curve(kp, ki, color, sw, dash=None):
        data = pi_step(kp, ki, T=10.0, N=560, tau=0.7, lag=0.16)
        pts = [(ox + (t / 10.0) * Ax, oy + (target - oy) * y) for (t, y) in data]
        p.append(polyline(pts, color=color, sw=sw, dash=dash))

    # великий λ → повільний, дуже стійкий (малий Kp, малий Ki)
    curve(1.0, 0.45, FIELD, 2.4)
    # середній λ
    curve(1.9, 1.1, NEG, 2.4)
    # малий λ → швидкий, ближче до дзвону (великий Kp, великий Ki)
    curve(3.4, 2.6, POS, 2.4)

    # підписи
    p.append(text(ox + Ax * 0.86, oy - 86, "малий λ", size=10.5, color=POS, anchor="middle", bold=True))
    p.append(text(ox + Ax * 0.86, oy - 72, "швидко, різкіше", size=9, color=POS, anchor="middle"))
    p.append(text(ox + Ax * 0.86, oy - 20, "великий λ", size=10.5, color=FIELD, anchor="middle", bold=True))
    p.append(text(ox + Ax * 0.86, oy - 6, "повільно, дуже стійко", size=9, color=FIELD, anchor="middle"))

    p.append(text(ox + Ax * 0.40, oy + 34,
                  "λ — бажана стала часу замкненого контуру: одна ручка крутить швидкодію проти запасу",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "lambda-knob.svg"), W, H, *p,
           title="Одна ручка λ задає весь компроміс «швидко проти стійко»")


if __name__ == "__main__":
    fig_two_knobs()
    fig_zn_pi_vs_pid()
    fig_bump_test()
    fig_lambda_knob()
    print("OK: figures written to", OUT)
