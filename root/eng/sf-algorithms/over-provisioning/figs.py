# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Геометричне проти лінійного розширення ──────────────────────────────
def fig_growth_strategies():
    W, H = 940, 480
    p = []
    n = 16
    
    # вартість додатка (сплески копіювання)
    geom_costs = [1, 2, 3, 1, 5, 1, 1, 1, 9, 1, 1, 1, 1, 1, 1, 1]
    line_costs = [i + 1 for i in range(n)]
    vmax = 16.0

    def panel(px, title, costs, spikes, summary, scolor):
        out = []
        pw, ph = 420.0, 310.0
        py = 56.0
        out.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
        out.append(text(px + pw / 2, py + 26, title, size=14, color=INK, bold=True))
        ax, ay = px + 44, py + ph - 52
        gw, gh = pw - 72, ph - 96
        
        out.append(line(ax, ay, ax + gw, ay, color=INK, sw=1.3))
        bw = gw / n * 0.65
        step = gw / n
        for i, c in enumerate(costs):
            bx = ax + step * (i + 0.5) - bw / 2
            bh = gh * c / vmax
            spike = (i + 1) in spikes
            col = POS if spike else "#9fb3c8"
            fill = "#fdecea" if spike else "#e8eef5"
            out.append(rect(bx, ay - bh, bw, bh, fill=fill, stroke=col, sw=1.4, rx=2))
            if spike:
                out.append(text(bx + bw / 2, ay - bh - 7, str(c), size=11, color=POS, bold=True))
        out.append(text(ax + gw / 2, ay + 22, "послідовні вставки (N) →", size=11.5, color=MUTED))
        
        b, _, _ = textbox(px + pw / 2, py + ph + 34, summary, size=12.5, pad=9,
                          fill="#eef7f0" if scolor == FIELD else "#fdecea",
                          stroke=scolor, color=INK, bold=True)
        out.append(b)
        return out

    p.extend(panel(24, "Геометричне зростання (місткість × 2)", geom_costs, {2, 3, 5, 9},
                   "сума копіювань ≈ 2N  →  амортизовано O(1)", FIELD))
    p.extend(panel(496, "Лінійне зростання (місткість + K)", line_costs, set(range(1, n + 1)),
                   "сума копіювань ≈ N²/2  →  середньо O(N)", POS))

    render(os.path.join(OUT, "growth-strategies.svg"), W, H, *p,
           title="Порівняння геометричного та лінійного виділення пам'яті")


# ── Фіг. 2: Перевикористання пам'яті алокатором (1.5 проти 2.0) ───────────────
def fig_memory_reuse_allocator():
    W, H = 920, 500
    p = []

    def panel(cy, title, freed_blocks, req, fits, note):
        out = []
        total = sum(freed_blocks)
        span = max(total, req)
        gx, gw = 170.0, 580.0
        unit = gw / span
        rowh = 32.0
        yF = cy
        yR = cy + rowh + 20
        
        out.append(text(gx - 20, cy - 12, title, size=13.5, color=INK, anchor="start", bold=True))
        
        # звільнені блоки
        x = gx
        for b in freed_blocks:
            w = b * unit
            out.append(rect(x, yF, w, rowh, fill="#e3e8ee", stroke="#aab4c0", sw=1.1, rx=2))
            x += w
        out.append(text(gx - 14, yF + rowh / 2 + 4, "звільнено", size=11, color=MUTED, anchor="end"))
        out.append(text(gx + total * unit / 2, yF + rowh / 2 + 5,
                        "сума = %d" % total, size=12.5, color=INK, bold=True))
        
        bx = gx + total * unit
        out.append(line(bx, yF - 6, bx, yR + rowh + 6, color=INK, sw=1.4, dash="5 4"))
        
        rw = req * unit
        col = FIELD if fits else POS
        tint = "#eef7f0" if fits else "#fdecea"
        out.append(rect(gx, yR, rw, rowh, fill=tint, stroke=col, sw=1.8, rx=2))
        out.append(text(gx + rw / 2, yR + rowh / 2 + 5, "новий запит = %d" % req, size=12.5, color=col, bold=True))
        out.append(text(gx - 14, yR + rowh / 2 + 4, "запит", size=11, color=MUTED, anchor="end"))
        
        out.append(text(gx + gw + 14, yR + rowh / 2 + 5,
                        ("влазить у діру" if fits else "не влазить у діру"),
                        size=12.5, color=col, anchor="start", bold=True))
        
        out.append(fitbox(gx, yR + rowh + 16, gw, 26, note, size=12,
                          fill=tint, stroke=col, color=INK, bold=True))
        return out

    p.extend(panel(64, "Коефіцієнт росту α = 2.0 (звільнені блоки 1, 2, 4)",
                   [1, 2, 4], 16, False,
                   "сума звільненого 7 < 16: новий блок НЕ лягає у звільнені комірки (фрагментація)"))
    p.extend(panel(274, "Коефіцієнт росту α = 1.5 (звільнені блоки 1, 2, 3, 4, 6, 9, 13)",
                   [1, 2, 3, 4, 6, 9, 13], 28, True,
                   "сума звільненого 38 ≥ 28: новий блок лягає у звільнені комірки (пам'ять перевикористовується)"))

    p.append(fitbox(50, 444, W - 100, 38,
                    "Поріг перевикористання: α ≤ φ = (1+√5)/2 ≈ 1.618.  При α = 1.5 алокатор може повторно використати звільнені блоки.",
                    size=12, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK))

    render(os.path.join(OUT, "memory-reuse-allocator.svg"), W, H, *p,
           title="Перевикористання пам'яті алокатором для різних факторів росту")


# ── Фіг. 3: Коефіцієнт заповнення хеш-таблиці ──────────────────────────────────
def fig_hash_table_load_factor():
    W, H = 880, 460
    p = []
    
    x0, y0 = 100.0, 70.0
    pw, ph = 640.0, 310.0
    
    p.append(rect(x0, y0, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=8))
    
    # Зелена зона безпечного надлишкового виділення
    p.append(rect(x0, y0, pw * 0.70, ph, fill="#eef7f0", stroke="none"))
    p.append(text(x0 + pw * 0.35, y0 + 30, "Зона оптимального Over-provisioning (α ≤ 0.7)",
                  size=12.5, color=FIELD, bold=True))
    
    # Червона зона колізійного колапсу
    p.append(rect(x0 + pw * 0.70, y0, pw * 0.30, ph, fill="#fdecea", stroke="none"))
    p.append(text(x0 + pw * 0.85, y0 + 30, "Деградація O(N)", size=12.5, color=POS, bold=True))
    
    # Пунктир рехашингу
    p.append(line(x0 + pw * 0.70, y0, x0 + pw * 0.70, y0 + ph, color=POS, sw=1.8, dash="5 4"))
    p.append(text(x0 + pw * 0.70 - 8, y0 + ph - 20, "Поріг рехашингу α_max = 0.70",
                  size=11.5, color=POS, bold=True, anchor="end"))
    
    # Вісі
    p.append(line(x0, y0 + ph, x0 + pw, y0 + ph, color=INK, sw=1.4))
    p.append(line(x0, y0, x0, y0 + ph, color=INK, sw=1.4))
    
    # Кількість проб = 1 / (1 - alpha)
    pts = []
    for step in range(95):
        alpha = step / 100.0
        probes = 1.0 / (1.0 - alpha) if alpha < 0.95 else 20.0
        cx = x0 + alpha * pw
        cy = y0 + ph - (probes / 10.0) * ph
        cy = max(cy, y0 + 10)
        pts.append(f"{cx:.1f},{cy:.1f}")
        
    p.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{POS}" stroke-width="2.8"/>')
    
    # Позначки Y
    for v in [1, 2, 4, 6, 8, 10]:
        yy = y0 + ph - (v / 10.0) * ph
        p.append(line(x0 - 4, yy, x0, yy, color=INK, sw=1))
        p.append(text(x0 - 10, yy + 4, str(v), size=11, color=MUTED, anchor="end"))
    p.append(text(x0 - 48, y0 + ph / 2, "Середня кількість проб", size=11.5, color=INK, anchor="middle", bold=True))
    
    # Позначки X
    for a in [0.0, 0.2, 0.4, 0.6, 0.7, 0.8, 0.9]:
        xx = x0 + a * pw
        p.append(line(xx, y0 + ph, xx, y0 + ph + 4, color=INK, sw=1))
        p.append(text(xx, y0 + ph + 20, f"{a:.1f}", size=11, color=MUTED))
    p.append(text(x0 + pw / 2, y0 + ph + 44, "Коефіцієнт заповнення (Load Factor α = N / M) →", size=12, color=INK, bold=True))

    p.append(fitbox(x0, y0 + ph + 60, pw, 26,
                    "Надлишковий резерв комірок (M > N) утримує пошук та вставку в межах O(1)",
                    size=12, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "hash-table-load-factor.svg"), W, H, *p,
           title="Залежність середньої кількості проб у хеш-таблиці від коефіцієнта заповнення")


# ── Фіг. 4: Гістерезис деалокації пам'яті (Anti-thrashing) ─────────────────────
def fig_hysteresis_loop():
    W, H = 940, 500
    p = []
    
    pw, ph = 840.0, 340.0
    px, py = 50.0, 60.0
    
    p.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    
    # Стан 1: Місткість C
    b1, _, _ = textbox(px + 180, py + 170, "Місткість = C\n(Заповнення: N елементів)", size=13, pad=12,
                       fill="#eef7f0", stroke=FIELD, color=INK, bold=True)
    p.append(b1)
    
    # Стан 2: Місткість 2C (після розширення)
    b2, _, _ = textbox(px + 660, py + 170, "Місткість = 2C\n(Розширення при N == C)", size=13, pad=12,
                       fill="#eaf0fd", stroke=NEG, color=INK, bold=True)
    p.append(b2)
    
    # Верхня стрілка розширення N == C
    p.append(arrow(px + 300, py + 140, px + 540, py + 140, color=POS, sw=2.2))
    p.append(text(px + 420, py + 120, "Вставка (push): N сягає C  →  Розширення вдвічі (× 2)",
                  size=12, color=POS, bold=True))
    
    # Нижня стрілка стиснення N <= C/4
    p.append(arrow(px + 540, py + 220, px + 300, py + 220, color=FIELD, sw=2.2))
    p.append(text(px + 420, py + 246, "Вилучення (pop): N падає до C/4  →  Стиснення вдвічі (÷ 2)",
                  size=12, color=FIELD, bold=True))
    
    # Зона гістерезису між C/4 та C
    p.append(rect(px + 260, py + 280, 320, 34, fill="#fff6e6", stroke="#e08a1e", sw=1.3, rx=6))
    p.append(text(px + 420, py + 300, "Буферна зона гістерезису (захист від Anti-Thrashing)",
                  size=12, color=INK, bold=True))

    p.append(fitbox(px + 40, py + ph + 24, pw - 80, 32,
                    "Гістерезис запобігає частим реалокаціям при почерговому додаванні та видаленні елементів на межі місткості",
                    size=12.5, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "hysteresis-loop.svg"), W, H, *p,
           title="Схема гістерезисного керування місткістю")


if __name__ == "__main__":
    fig_growth_strategies()
    fig_memory_reuse_allocator()
    fig_hash_table_load_factor()
    fig_hysteresis_loop()
    print("OK figs")
