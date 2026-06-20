# -*- coding: utf-8 -*-
"""Фігури до теми «Тензорезистори».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Першопричина: розтяг → довший і тонший провідник → більший опір ────────
def fig_principle():
    W, H = 760, 340
    f = [text(W / 2, 28, "Чому опір росте під розтягом: R = ρ·L / A", size=16, bold=True)]

    # --- спокій ---
    yb = 110
    f.append(text(150, yb - 34, "у спокої", size=13, bold=True, color=MUTED))
    # дріт: товстий короткий брусок
    f.append(rect(70, yb - 14, 160, 28, fill="#eef3f9", stroke=LINE, sw=1.8))
    f.append(text(150, yb + 6, "L", size=14, bold=True, italic=True))
    # розміри
    f.append(line(70, yb + 28, 230, yb + 28, color=MUTED, sw=1))
    f.append(text(150, yb + 44, "довжина L", size=11, color=MUTED))
    f.append(line(56, yb - 14, 56, yb + 14, color=MUTED, sw=1))
    f.append(text(34, yb + 4, "A", size=11, color=MUTED))
    f.append(text(300, yb + 5, "R₀ = ρ·L / A", size=14, bold=True))

    # --- під розтягом ---
    yt = 230
    f.append(text(150, yt - 38, "під розтягом", size=13, bold=True, color=POS))
    # стрілки тягнуть у боки
    f.append(arrow(58, yt, 28, yt, color=POS))
    f.append(arrow(252, yt, 282, yt, color=POS))
    # дріт: довший і ВИЖЕ тонший
    f.append(rect(64, yt - 9, 182, 18, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(155, yt + 5, "L + ΔL", size=13, bold=True, italic=True, color=POS))
    f.append(line(64, yt + 22, 246, yt + 22, color=POS, sw=1))
    f.append(text(155, yt + 38, "довша → опір ↑", size=11, color=POS))
    f.append(text(150, yt - 20, "тонша (A↓) → опір ↑", size=11, color=POS))
    f.append(text(300, yt + 5, "R = ρ·(L+ΔL) / (A−ΔA)  >  R₀", size=14, bold=True, color=POS))

    # правий стовпчик: три внески
    bx = 520
    f.append(text(bx + 95, 78, "три причини зростання R", size=12, bold=True))
    b1 = fitbox(bx, 92, 190, 40, "довша L", size=12, bold=True, fill="#fdecea", stroke=POS)
    b2 = fitbox(bx, 138, 190, 40, "менший переріз A", size=12, bold=True, fill="#fdecea", stroke=POS)
    b3 = fitbox(bx, 184, 190, 40, "змінений ρ (п'єзорезистивність)",
                size=11, bold=True, fill="#fff3e0", stroke="#b8860b")
    f += [b1, b2, b3]
    f.append(text(bx + 95, 246, "перші дві — геометрія;", size=11, color=MUTED))
    f.append(text(bx + 95, 262, "третя — сама фізика металу", size=11, color=MUTED))

    render(os.path.join(IMG, 'principle.svg'), W, H, *f)


# ── 2. Коефіцієнт тензочутливості: метал ≈ 2 проти напівпровідника ≈ 100–200 ──
def fig_gauge_factor():
    W, H = 760, 360
    f = [text(W / 2, 28, "Коефіцієнт тензочутливості: GF = (ΔR/R) / ε", size=16, bold=True)]

    # фольгова змійка ліворуч (упізнаваний візерунок тензорезистора)
    f.append(text(150, 70, "фольгова змійка", size=12, bold=True))
    ox, oy = 60, 88
    f.append(rect(ox - 6, oy - 6, 190, 96, fill="#fafafa", stroke=MUTED, sw=1, rx=4))
    # горизонтальні доріжки + з'єднання — «гармошка»
    rows = [oy + 8 + i * 14 for i in range(6)]
    for i, ry in enumerate(rows):
        f.append(line(ox + 6, ry, ox + 160, ry, color="#b8860b", sw=3))
        if i < len(rows) - 1:
            xend = ox + 160 if i % 2 == 0 else ox + 6
            f.append(line(xend, ry, xend, rows[i + 1], color="#b8860b", sw=3))
    # вісь чутливості (вздовж доріжок)
    f.append(arrow(ox + 20, oy + 96, ox + 120, oy + 96, color=POS))
    f.append(text(ox + 75, oy + 112, "вісь деформації", size=10, color=POS))
    f.append(text(150, 220, "довгі доріжки вздовж осі,", size=10, color=MUTED))
    f.append(text(150, 234, "короткі повороти — упоперек:", size=10, color=MUTED))
    f.append(text(150, 248, "майже весь опір «слухає» одну вісь", size=10, color=MUTED))

    # порівняння стовпчиками праворуч
    base_y = 270
    f.append(text(540, 64, "наскільки сильний відгук", size=12, bold=True))
    # метал GF≈2
    f.append(rect(380, base_y - 40, 90, 40, fill="#eef3f9", stroke=NEG, sw=2))
    f.append(text(425, base_y - 16, "GF ≈ 2", size=13, bold=True, color=NEG))
    f.append(text(425, base_y + 18, "метал", size=12, bold=True))
    f.append(text(425, base_y + 34, "лінійний, стабільний", size=10, color=MUTED))
    # напівпровідник GF≈100..200
    f.append(rect(520, base_y - 190, 90, 190, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(565, base_y - 168, "GF ≈", size=13, bold=True, color=POS))
    f.append(text(565, base_y - 150, "100–200", size=13, bold=True, color=POS))
    f.append(text(565, base_y + 18, "кремній", size=12, bold=True))
    f.append(text(565, base_y + 34, "чутливий, але", size=10, color=MUTED))
    f.append(text(565, base_y + 47, "нелінійний і «пливе»", size=10, color=MUTED))
    # вісь
    f.append(line(360, base_y, 660, base_y, color=LINE, sw=1.2))

    render(os.path.join(IMG, 'gauge-factor.svg'), W, H, *f)


# ── 3. Чому міст: крихітна ΔR тоне; різниця плечей її витягує ──────────────────
def fig_bridge():
    W, H = 780, 360
    f = [text(W / 2, 26, "Крихітна ΔR ≈ 0.2 % — її витягує різниця, а не абсолют", size=15, bold=True)]

    # ЛІВОРУЧ: одиночний резистор — велике R, мала зміна
    f.append(text(180, 64, "одиночний R: зміна тоне", size=12, bold=True))
    # «стовп» опору: великий блок + тонка шапочка ΔR
    bx, by, bw = 120, 90, 120
    f.append(rect(bx, by + 130, bw, 70, fill="#eef3f9", stroke=LINE, sw=1.5))
    f.append(text(bx + bw / 2, by + 170, "R = 350 Ω", size=13, bold=True))
    f.append(rect(bx, by + 124, bw, 6, fill=POS, stroke=POS, sw=1))
    f.append(arrow(bx + bw + 22, by + 127, bx + bw + 2, by + 127, color=POS))
    f.append(text(bx + bw + 70, by + 131, "ΔR ≈ 0.7 Ω", size=12, bold=True, color=POS))
    f.append(text(180, by + 224, "0.7 Ω у 350 Ω — губиться", size=11, color=MUTED))
    f.append(text(180, by + 240, "у дрейфі та шумі", size=11, color=MUTED))

    # ПРАВОРУЧ: міст Вітстона — ромб
    cx, cy, s = 580, 175, 95
    top = (cx, cy - s); bot = (cx, cy + s); lft = (cx - s, cy); rgt = (cx + s, cy)
    f.append(text(cx, 64, "міст Вітстона: читаємо різницю", size=12, bold=True))
    for a, b in [(top, rgt), (rgt, bot), (bot, lft), (lft, top)]:
        f.append(line(a[0], a[1], b[0], b[1], color=LINE, sw=2))
    # плечі-резистори (маленькі прямокутники на сторонах)
    def arm(p, q, label, active=False):
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        col = POS if active else LINE
        fill = "#fdecea" if active else "#eef3f9"
        return (rect(mx - 16, my - 11, 32, 22, fill=fill, stroke=col, sw=1.8) +
                text(mx, my + 5, label, size=11, bold=True, color=col))
    f.append(arm(top, lft, "R", False))
    f.append(arm(top, rgt, "R", False))
    f.append(arm(lft, bot, "R", False))
    f.append(arm(rgt, bot, "R+ΔR", True))
    # збудження вгорі/внизу
    f.append(text(cx, top[1] - 12, "V_зб", size=12, bold=True, color=POS))
    f.append(plus(cx, top[1] - 2, 8))
    f.append(text(cx, bot[1] + 22, "GND", size=11, color=MUTED))
    # вихід — діагональ
    f.append(text(lft[0] - 30, lft[1] + 4, "○", size=14, color=NEG))
    f.append(text(rgt[0] + 30, rgt[1] + 4, "○", size=14, color=NEG))
    f.append(text(cx, cy - 4, "V_вих", size=12, bold=True, color=NEG))
    f.append(text(cx, cy + 14, "(різниця)", size=10, color=MUTED))
    f.append(text(cx, bot[1] + 60, "у спокої V_вих = 0;", size=11, color=MUTED))
    f.append(text(cx, bot[1] + 76, "тільки ΔR його зрушує", size=11, color=MUTED))

    render(os.path.join(IMG, 'bridge.svg'), W, H, *f)


# ── 4. Температурна компенсація: обидва плечі пливуть разом → різниця гасить ───
def fig_temp_comp():
    W, H = 760, 350
    f = [text(W / 2, 26, "Температура зсуває обидва плечі однаково — різниця її гасить", size=15, bold=True)]

    # ліворуч: один давач — температура додається до сили
    f.append(text(175, 62, "один давач", size=12, bold=True))
    f.append(rect(70, 84, 210, 44, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(175, 111, "ΔR = (сила) + (нагрів)", size=12, bold=True, color=POS))
    f.append(text(175, 150, "нагрів підмішується у вимір —", size=11, color=MUTED))
    f.append(text(175, 166, "не відрізнити силу від тепла", size=11, color=MUTED))
    f.append(text(175, 188, "✗ показ «пливе» з температурою", size=11, color=POS, bold=True))

    # праворуч: робочий + «німий» (dummy) давач
    f.append(text(560, 62, "робочий + «німий» давач поряд", size=12, bold=True))
    # робочий
    f.append(rect(430, 84, 110, 40, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(485, 100, "робочий", size=11, bold=True))
    f.append(text(485, 116, "сила + нагрів", size=10, color=MUTED))
    # німий
    f.append(rect(560, 84, 110, 40, fill="#eef3f9", stroke=NEG, sw=1.8))
    f.append(text(615, 100, "«німий»", size=11, bold=True))
    f.append(text(615, 116, "тільки нагрів", size=10, color=MUTED))
    # обидва в одному кліматі
    f.append(rect(420, 74, 260, 60, fill="none", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(550, 150, "та сама температура", size=11, color=FIELD, bold=True))

    # віднімання
    f.append(text(550, 196, "міст бере різницю плечей:", size=11, color=MUTED))
    f.append(rect(420, 208, 260, 40, fill="#eafaf1", stroke=FIELD, sw=1.8))
    f.append(text(550, 226, "(сила+нагрів) − (нагрів) = сила", size=12, bold=True, color=INK))
    f.append(text(550, 270, "✓ нагрів скоротився — лишилась сила", size=11, color=FIELD, bold=True))

    # підпис унизу спільний
    f.append(text(W / 2, 322, "той самий трюк гасить і дрейф живлення: спільне V_зб пливе в обох плечах",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, 'temp-compensation.svg'), W, H, *f)


# ── 5. Вивід: міст = два дільники; різниця → точна формула з нелінійністю ──────
def fig_bridge_derivation():
    W, H = 780, 430
    f = [text(W / 2, 26, "Вивід V_вих: різниця двох дільників", size=16, bold=True)]

    # ромб моста з підписаними плечами R1..R4
    cx, cy, s = 210, 200, 110
    top = (cx, cy - s); bot = (cx, cy + s); lft = (cx - s, cy); rgt = (cx + s, cy)
    for a, b in [(top, rgt), (rgt, bot), (bot, lft), (lft, top)]:
        f.append(line(a[0], a[1], b[0], b[1], color=LINE, sw=2))

    def arm(p, q, label, active=False):
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        col = POS if active else LINE
        fill = "#fdecea" if active else "#eef3f9"
        return (rect(mx - 22, my - 12, 44, 24, fill=fill, stroke=col, sw=1.8) +
                text(mx, my + 5, label, size=12, bold=True, color=col))

    # ліва пара R1(верх)/R2(низ); права пара R3(верх)/R4(низ)
    f.append(arm(top, lft, "R₁", False))
    f.append(arm(lft, bot, "R₂", False))
    f.append(arm(top, rgt, "R₃", False))
    f.append(arm(rgt, bot, "R₄", False))

    # живлення зверху, земля знизу
    f.append(plus(cx, top[1] - 4, 8))
    f.append(text(cx, top[1] - 20, "V_зб", size=12, bold=True, color=POS))
    f.append(text(cx, bot[1] + 24, "GND", size=11, color=MUTED))
    # вузли A та B
    f.append(circle(lft[0], lft[1], 4, fill=NEG, stroke=NEG))
    f.append(text(lft[0] - 16, lft[1] + 4, "A", size=13, bold=True, color=NEG))
    f.append(circle(rgt[0], rgt[1], 4, fill=NEG, stroke=NEG))
    f.append(text(rgt[0] + 16, rgt[1] + 4, "B", size=13, bold=True, color=NEG))
    f.append(text(cx, cy + 4, "V_вих = V_A − V_B", size=12, bold=True, color=NEG))
    f.append(text(cx, cy + 22, "(різниця)", size=10, color=MUTED))

    # права колонка: два дільники → загальна формула
    bx = 420
    f.append(text(bx + 165, 70, "кожна половина — дільник напруги", size=12, bold=True))
    f.append(fitbox(bx, 84, 330, 34, "V_A = V_зб · R₂ / (R₁ + R₂)",
                    size=13, fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(bx, 124, 330, 34, "V_B = V_зб · R₄ / (R₃ + R₄)",
                    size=13, fill="#eaf0fd", stroke=NEG))
    f.append(text(bx + 165, 184, "віднімаємо — точна формула моста:", size=12, bold=True))
    f.append(fitbox(bx, 198, 330, 56,
                    "V_вих     R₂·R₃ − R₁·R₄\n──── = ──────────────\nV_зб    (R₁+R₂)(R₃+R₄)",
                    size=13, fill="#f4f6f8", stroke=LINE))
    f.append(text(bx + 165, 280, "у спокої R₁·R₄ = R₂·R₃ → V_вих = 0", size=11, color=MUTED))

    # нижня смуга: чвертьміст → лінійна частина + нелінійний доважок
    f.append(rect(40, 320, W - 80, 92, fill="#fffaf0", stroke="#b8860b", sw=1.4, rx=8))
    f.append(text(W / 2, 342, "чвертьміст (активне лише R₁ = R+ΔR, решта = R):",
                  size=12, bold=True))
    f.append(text(W / 2, 372, "V_вих / V_зб =  (1/4)·(ΔR/R)  ·  1 / (1 + ½·ΔR/R)",
                  size=14, bold=True))
    f.append(text(255, 398, "лінійний відгук", size=11, color=FIELD, bold=True))
    f.append(text(560, 398, "нелінійний доважок (звідси похибка)", size=11, color=POS, bold=True))

    render(os.path.join(IMG, 'bridge-derivation.svg'), W, H, *f)


# ── 6. Чверть / напів / повний міст: множник ×1 / ×2 / ×4 і лінійність ─────────
def fig_bridge_configs():
    W, H = 800, 430
    f = [text(W / 2, 26, "Скільки плечей активні: множник ×1 / ×2 / ×4", size=16, bold=True)]

    def small_bridge(cx, cy, s, arms, caption, mult, linear, note):
        """arms = (a1,a2,a3,a4) для R1,R2,R3,R4: '+' розтяг, '-' стиск, '0' сталий."""
        out = []
        top = (cx, cy - s); bot = (cx, cy + s); lft = (cx - s, cy); rgt = (cx + s, cy)
        for a, b in [(top, rgt), (rgt, bot), (bot, lft), (lft, top)]:
            out.append(line(a[0], a[1], b[0], b[1], color=LINE, sw=1.8))
        sides = [(top, lft), (lft, bot), (top, rgt), (rgt, bot)]  # R1,R2,R3,R4
        for (p, q), tag in zip(sides, arms):
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            if tag == "+":
                col, fill, lab = POS, "#fdecea", "+"
            elif tag == "-":
                col, fill, lab = NEG, "#eaf0fd", "−"
            else:
                col, fill, lab = LINE, "#eef3f9", "R"
            out.append(rect(mx - 13, my - 10, 26, 20, fill=fill, stroke=col, sw=1.6))
            out.append(text(mx, my + 5, lab, size=12, bold=True, color=col))
        out.append(plus(cx, top[1] - 2, 6))
        out.append(text(cx, bot[1] + 16, "GND", size=9, color=MUTED))
        out.append(text(cx - s - 10, cy + 4, "○", size=11, color=NEG))
        out.append(text(cx + s + 10, cy + 4, "○", size=11, color=NEG))
        # підписи під мостом
        out.append(text(cx, cy + s + 40, caption, size=13, bold=True))
        out.append(text(cx, cy + s + 62, mult, size=15, bold=True, color=POS))
        lc = FIELD if linear else "#b8860b"
        out.append(text(cx, cy + s + 84, linear, size=11, bold=True, color=lc) if False else
                   text(cx, cy + s + 84, "лінійність: " + note, size=10, color=lc))
        return out

    s = 58
    y = 150
    # чвертьміст: одне активне плече
    f += small_bridge(150, y, s, ("+", "0", "0", "0"),
                      "чвертьміст", "×1",
                      None, "нелінійний")
    # напівміст: два плеча назустріч (+ і −)
    f += small_bridge(400, y, s, ("+", "-", "0", "0"),
                      "напівміст", "×2",
                      None, "лінійний*")
    # повний міст: усі чотири, парами назустріч
    f += small_bridge(650, y, s, ("+", "-", "-", "+"),
                      "повний міст", "×4",
                      None, "лінійний")

    # легенда
    ly = 360
    f.append(rect(40, ly, W - 80, 56, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=8))
    f.append(text(110, ly + 22, "+ розтяг (R↑)", size=11, bold=True, color=POS))
    f.append(text(110, ly + 42, "− стиск (R↓)", size=11, bold=True, color=NEG))
    f.append(text(330, ly + 22, "R сталий опір (компенсаційне / «німе» плече)",
                  size=11, color=MUTED))
    f.append(text(330, ly + 42, "* напівміст лінійний, лише коли пара змінюється строго +ΔR / −ΔR",
                  size=10, color="#b8860b"))
    f.append(text(640, ly + 32, "більше активних плечей →\nсильніший і чесніший сигнал",
                  size=10, color=INK) if False else
             mtext(660, ly + 22, ["більше активних плечей →", "сильніший і чесніший сигнал"],
                   size=10, color=INK))

    render(os.path.join(IMG, 'bridge-configs.svg'), W, H, *f)


if __name__ == "__main__":
    fig_principle()
    fig_gauge_factor()
    fig_bridge()
    fig_temp_comp()
    fig_bridge_derivation()
    fig_bridge_configs()
    print("OK: 6 фігур у", IMG)
