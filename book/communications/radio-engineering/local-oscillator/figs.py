# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра відповідно до стилю курсу
RF   = "#8e44ad"   # ВЧ-сигнал (фіолетовий)
LO   = FIELD       # Гетеродин (зелений)
IF   = POS         # Проміжна частота (червоний)
SPUR = NEG         # Побічні випромінювання / завади (червоний/рожевий)
NOISE= "#d35400"   # Фазовий шум (помаранчевий)
BLOCK= "#c0392b"   # Завада / блокер (темно-червоний)

def tri(cx, base_y, half_w, h, color, sw=2.4, fill=None):
    """Трикутний «горбик» спектра з центром cx, основою на base_y."""
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (cx - half_w, base_y, cx, base_y - h, cx + half_w, base_y)
    f = fill if fill else "none"
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (pts, f, color, sw))

def tick(x, base_y, lbl, color=MUTED, up=False):
    dy = -6 if up else 18
    return (line(x, base_y - 4, x, base_y + 4, color=MUTED, sw=1.2) +
            text(x, base_y + dy, lbl, size=12, color=color))

# ── Фігура 1: Спектральна чистота гетеродина ────────────────────────────────
def fig_lo_spectral_purity():
    W, H = 760, 360
    ax, ay = 60, 260
    axw = 640
    p = []

    # Вісь частоти
    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(arrow(ax + axw - 22, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(text(ax + axw + 8, ay + 5, "f", size=15, color=INK, italic=True, anchor="start"))

    # Вісь амплітуди (дБн/Гц)
    p.append(line(ax, ay, ax, ay - 210, color=INK, sw=1.6))
    p.append(arrow(ax, ay - 190, ax, ay - 210, color=INK, sw=1.6))
    p.append(text(ax - 10, ay - 218, "P (дБм)", size=13, color=INK, bold=True, anchor="middle"))

    f_lo = ax + 300

    # Ідеальна лінія (пунктир)
    p.append(line(f_lo, ay, f_lo, ay - 175, color=MUTED, sw=1.2, dash="4 3"))
    p.append(text(f_lo + 8, ay - 170, "ідеальний гетеродин (дельта-функція)", size=11, color=MUTED, anchor="start"))

    # Реальний спектр — пік гетеродина з фазовим шумом ("спідниця")
    noise_path = (
        f"M {ax + 80} {ay - 12} "
        f"Q {f_lo - 120} {ay - 18}, {f_lo - 40} {ay - 65} "
        f"Q {f_lo - 15} {ay - 110}, {f_lo} {ay - 175} "
        f"Q {f_lo + 15} {ay - 110}, {f_lo + 40} {ay - 65} "
        f"Q {f_lo + 120} {ay - 18}, {ax + 520} {ay - 12}"
    )
    fill_path = noise_path + f" L {ax + 520} {ay} L {ax + 80} {ay} Z"
    p.append(f'<path d="{fill_path}" fill="#fbeee6" stroke="none"/>')
    p.append(f'<path d="{noise_path}" fill="none" stroke="{NOISE}" stroke-width="2.5"/>')

    # Основний пік f_LO
    p.append(tick(f_lo, ay, "f_LO", color=LO))
    p.append(text(f_lo, ay - 185, "f_LO (несуча)", size=13, color=LO, bold=True))

    # Гармоніка 2*f_LO
    f_2lo = ax + 540
    p.append(line(f_2lo, ay, f_2lo, ay - 70, color=LO, sw=2.0))
    p.append(arrow(f_2lo, ay - 55, f_2lo, ay - 72, color=LO, sw=2.0))
    p.append(tick(f_2lo, ay, "2·f_LO", color=LO))
    p.append(text(f_2lo, ay - 80, "2-га гармоніка", size=11, color=LO))

    # Побічна завада (Spur)
    f_spur = f_lo + 110
    p.append(line(f_spur, ay, f_spur, ay - 85, color=SPUR, sw=2.0))
    p.append(arrow(f_spur, ay - 70, f_spur, ay - 87, color=SPUR, sw=2.0))
    p.append(text(f_spur + 6, ay - 92, "Spur (супутна завада)", size=11, color=SPUR, bold=True, anchor="start"))

    # Вимірювання фазового шуму L(Δf) на відбудові Δf
    f_off = f_lo + 70
    p.append(line(f_lo, ay + 28, f_off, ay + 28, color=INK, sw=1.2))
    p.append(arrow(f_lo + 20, ay + 28, f_lo, ay + 28, color=INK, sw=1.2))
    p.append(arrow(f_off - 20, ay + 28, f_off, ay + 28, color=INK, sw=1.2))
    p.append(text((f_lo + f_off) / 2, ay + 44, "відбудова Δf", size=11, color=INK))

    p.append(line(f_off, ay, f_off, ay - 44, color=NOISE, sw=1.2, dash="3 3"))
    p.append(circle(f_off, ay - 44, 4, fill=NOISE, stroke="none"))
    p.append(text(f_off + 10, ay - 44, "L(Δf) [дБн/Гц]", size=12, color=NOISE, bold=True, anchor="start"))

    # Підпис пояснення
    b, bw, bh = textbox(ax + 20, 48,
                        "Спектральна чистота гетеродина визначається трикутником:\n"
                        "1) Рівнем несучої  2) Фазовим шумом L(Δf)  3) Побічними піками (spurs)",
                        size=12, color=INK, fill=BG, stroke=MUTED, min_w=450)
    p.append(b)

    render(os.path.join(OUT, "lo-spectral-purity.svg"), W, H, *p,
           title="Спектральна чистота реального гетеродина")

# ── Фігура 2: Взаємне змішування (Reciprocal Mixing) ────────────────────────
def fig_reciprocal_mixing():
    W, H = 760, 340
    p = []

    # ЛІВИЙ ГРАФІК: ВЧ спектр
    ax1, ay1 = 50, 240
    axw1 = 310

    p.append(text(ax1 + 140, 36, "ВЧ Ефір (до змішувача)", size=13, color=INK, bold=True))
    p.append(line(ax1, ay1, ax1 + axw1, ay1, color=INK, sw=1.4))
    p.append(arrow(ax1 + axw1 - 18, ay1, ax1 + axw1, ay1, color=INK, sw=1.4))
    p.append(text(ax1 + axw1 + 6, ay1 + 4, "f", size=13, color=INK, italic=True))

    f_rf1 = ax1 + 60
    f_blk = ax1 + 170
    f_lo1 = ax1 + 250

    # Слабкий корисний сигнал f_RF
    p.append(tri(f_rf1, ay1, 14, 30, RF, fill="#f3e8fb"))
    p.append(tick(f_rf1, ay1, "f_RF", color=RF))
    p.append(text(f_rf1, ay1 - 38, "слабкий", size=10.5, color=RF))

    # Потужна завада f_blocker
    p.append(tri(f_blk, ay1, 16, 110, BLOCK, fill="#fadbd8"))
    p.append(tick(f_blk, ay1, "f_завади", color=BLOCK))
    p.append(text(f_blk, ay1 - 118, "сильна завада", size=11, color=BLOCK, bold=True))

    # Гетеродин із фазовим шумом f_LO
    noise_p1 = f"M {f_lo1 - 90} {ay1 - 5} Q {f_lo1 - 25} {ay1 - 30}, {f_lo1} {ay1 - 120} Q {f_lo1 + 25} {ay1 - 30}, {f_lo1 + 50} {ay1 - 5}"
    p.append(f'<path d="{noise_p1}" fill="none" stroke="{NOISE}" stroke-width="2.0"/>')
    p.append(line(f_lo1, ay1, f_lo1, ay1 - 120, color=LO, sw=2.5))
    p.append(tick(f_lo1, ay1, "f_LO", color=LO))
    p.append(text(f_lo1, ay1 - 130, "f_LO", size=11, color=LO, bold=True))

    # Стрілка переносу
    p.append('<path d="M 375 160 Q 400 120 425 160" fill="none" stroke="%s" stroke-width="2.0" marker-end="url(#arrow)"/>' % INK)
    p.append(text(400, 115, "змішування", size=12, color=INK, bold=True))

    # ПРАВИЙ ГРАФІК: Вихід змішувача на ПЧ
    ax2, ay2 = 440, 240
    axw2 = 290

    p.append(text(ax2 + 130, 36, "Вихід ПЧ (після змішувача)", size=13, color=INK, bold=True))
    p.append(line(ax2, ay2, ax2 + axw2, ay2, color=INK, sw=1.4))
    p.append(arrow(ax2 + axw2 - 18, ay2, ax2 + axw2, ay2, color=INK, sw=1.4))
    p.append(text(ax2 + axw2 + 6, ay2 + 4, "f", size=13, color=INK, italic=True))

    f_if = ax2 + 100

    # Шумове підніжжя від взаємного змішування
    noise_if = f"M {f_if - 70} {ay2 - 4} Q {f_if - 20} {ay2 - 25}, {f_if} {ay2 - 40} Q {f_if + 20} {ay2 - 25}, {f_if + 70} {ay2 - 4}"
    p.append(f'<path d="{noise_if} L {f_if + 70} {ay2} L {f_if - 70} {ay2} Z" fill="#fbeee6" stroke="none"/>')
    p.append(f'<path d="{noise_if}" fill="none" stroke="{NOISE}" stroke-width="2.0"/>')

    # Сигнал на ПЧ усередині шуму
    p.append(tri(f_if, ay2, 14, 30, IF, fill="#fdecea"))
    p.append(tick(f_if, ay2, "f_IF", color=IF))

    p.append(text(f_if, ay2 - 52, "сигнал затоплено", size=11, color=BLOCK, bold=True))
    p.append(text(f_if, ay2 - 68, "шумом завади!", size=11, color=BLOCK, bold=True))

    b, bw, bh = textbox(60, 270,
                        "Взаємне змішування: сильна завада поруч перемножується з шумом гетеродина\n"
                        "і створює шумову «подушку» точно на частоті ПЧ, повністю маскуючи слабкий сигнал.",
                        size=12, color=INK, fill=BG, stroke=MUTED, min_w=640)
    p.append(b)

    render(os.path.join(OUT, "reciprocal-mixing.svg"), W, H, *p,
           title="Механізм взаємного змішування фазового шуму")

# ── Фігура 3: Архітектура гетеродина на ФАПЧ (PLL Synthesizer) ─────────────
def fig_pll_lo_architecture():
    W, H = 760, 280
    cy = 120
    p = []

    def block(x, y, w, h, lbl, sub, col=INK, fill=FILL):
        out = rect(x, y, w, h, fill=fill, stroke=col, sw=2.0, rx=6)
        out += text(x + w / 2, y + h / 2 - 6, lbl, size=12.5, color=col, bold=True)
        if sub:
            out += text(x + w / 2, y + h / 2 + 12, sub, size=10.5, color=MUTED)
        return out

    # 1. TCXO
    p.append(block(40, cy - 26, 90, 52, "TCXO", "опора f_ref", col="#27ae60", fill="#eafaf1"))

    p.append(line(130, cy, 170, cy, color=INK, sw=1.8))
    p.append(arrow(150, cy, 170, cy, color=INK, sw=1.8))

    # 2. PFD
    p.append(block(170, cy - 26, 85, 52, "PFD", "дектор фази", col=INK, fill=FILL))

    p.append(line(255, cy, 295, cy, color=INK, sw=1.8))
    p.append(arrow(275, cy, 295, cy, color=INK, sw=1.8))
    p.append(text(275, cy - 10, "I_out", size=10, color=MUTED))

    # 3. Loop Filter
    p.append(block(295, cy - 26, 95, 52, "Петлевий", "фільтр ФНЧ", col="#d35400", fill="#fbeee6"))

    p.append(line(390, cy, 430, cy, color=INK, sw=1.8))
    p.append(arrow(410, cy, 430, cy, color=INK, sw=1.8))
    p.append(text(410, cy - 10, "V_tune", size=10, color=MUTED))

    # 4. VCO
    p.append(block(430, cy - 26, 90, 52, "VCO", "генератор", col=LO, fill="#eafaf0"))

    p.append(line(520, cy, 620, cy, color=LO, sw=2.5))
    p.append(arrow(600, cy, 620, cy, color=LO, sw=2.5))

    # Буферний підсилювач
    p.append(block(620, cy - 26, 90, 52, "Буфер RF", "до змішувача", col=RF, fill="#f3e8fb"))
    p.append(line(710, cy, 740, cy, color=RF, sw=2))
    p.append(arrow(730, cy, 740, cy, color=RF, sw=2))
    p.append(text(725, cy - 10, "f_LO", size=12, color=RF, bold=True))

    # Зворотний зв'язок
    p.append(line(560, cy, 560, cy + 90, color=INK, sw=1.8))
    p.append(line(560, cy + 90, 480, cy + 90, color=INK, sw=1.8))
    p.append(arrow(500, cy + 90, 480, cy + 90, color=INK, sw=1.8))

    # 5. Дільник N
    p.append(block(360, cy + 64, 120, 52, "Дільник ÷N", "N = INT + F/M", col="#8e44ad", fill="#f4ecf7"))

    p.append(line(360, cy + 90, 212, cy + 90, color=INK, sw=1.8))
    p.append(line(212, cy + 90, 212, cy + 26, color=INK, sw=1.8))
    p.append(arrow(212, cy + 40, 212, cy + 26, color=INK, sw=1.8))
    p.append(text(212, cy + 104, "f_LO / N", size=10.5, color=MUTED))

    p.append(text(380, 252, "Кільце ФАПЧ фіксує частоту VCO: f_LO = N · f_ref. Зворотний зв'язок підтримує високу стабільність.", size=12, color=INK))

    render(os.path.join(OUT, "pll-lo-architecture.svg"), W, H, *p,
           title="Архітектура гетеродина на основі кільця ФАПЧ (PLL)")

# ── Фігура 4: Квадратурне формування LO (0° та 90°) ─────────────────────────
def fig_iq_quadrature_generation():
    W, H = 760, 320
    p = []

    # ЛІВА СХЕМА
    p.append(rect(40, 40, 320, 220, fill="#fcfcfc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(200, 62, "А) Дільник на 2 (на тригерах)", size=13, color=INK, bold=True))

    p.append(line(60, 140, 110, 140, color=LO, sw=2.0))
    p.append(arrow(95, 140, 110, 140, color=LO, sw=2.0))
    p.append(text(85, 126, "2·f_LO", size=11, color=LO, bold=True))

    p.append(rect(110, 100, 120, 80, fill="#eafaf0", stroke=LO, sw=2.0, rx=4))
    p.append(text(170, 134, "D-тригери", size=12, color=LO, bold=True))
    p.append(text(170, 152, "дільник ÷2", size=10.5, color=MUTED))

    p.append(line(230, 122, 330, 122, color=RF, sw=2.0))
    p.append(arrow(310, 122, 330, 122, color=RF, sw=2.0))
    p.append(text(340, 126, "LO_I (0°)", size=12, color=RF, bold=True, anchor="start"))

    p.append(line(230, 158, 330, 158, color=IF, sw=2.0))
    p.append(arrow(310, 158, 330, 158, color=IF, sw=2.0))
    p.append(text(340, 162, "LO_Q (90°)", size=12, color=IF, bold=True, anchor="start"))

    p.append(text(200, 235, "Точний фазовий зсув 90°;\nпотребує частоти генератора 2·f_LO", size=11, color=MUTED))

    # ПРАВА СХЕМА
    p.append(rect(400, 40, 320, 220, fill="#fcfcfc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(560, 62, "Б) Поліфазний RC-фільтр", size=13, color=INK, bold=True))

    p.append(line(420, 140, 470, 140, color=LO, sw=2.0))
    p.append(arrow(455, 140, 470, 140, color=LO, sw=2.0))
    p.append(text(445, 126, "f_LO", size=11, color=LO, bold=True))

    p.append(rect(470, 100, 120, 80, fill="#fbeee6", stroke="#d35400", sw=2.0, rx=4))
    p.append(text(530, 134, "Polyphase", size=12, color="#d35400", bold=True))
    p.append(text(530, 152, "RC-міст", size=10.5, color=MUTED))

    p.append(line(590, 122, 690, 122, color=RF, sw=2.0))
    p.append(arrow(670, 122, 690, 122, color=RF, sw=2.0))
    p.append(text(700, 126, "LO_I (0°)", size=12, color=RF, bold=True, anchor="start"))

    p.append(line(590, 158, 690, 158, color=IF, sw=2.0))
    p.append(arrow(670, 158, 690, 158, color=IF, sw=2.0))
    p.append(text(700, 162, "LO_Q (90°)", size=12, color=IF, bold=True, anchor="start"))

    p.append(text(560, 235, "Працює на базовій частоті f_LO;\nвтрати амплітуди та чутливість до RC", size=11, color=MUTED))

    p.append(text(380, 295, "Гетеродин Zero-IF / I-Q приймачів має видавати дві синусоїди з квадрируванням (зсув 90°).", size=12, color=INK))

    render(os.path.join(OUT, "iq-quadrature-generation.svg"), W, H, *p,
           title="Способи формування квадратурного гетеродина 0° та 90°")

if __name__ == "__main__":
    fig_lo_spectral_purity()
    fig_reciprocal_mixing()
    fig_pll_lo_architecture()
    fig_iq_quadrature_generation()
    print("OK: figures generated in", OUT)
