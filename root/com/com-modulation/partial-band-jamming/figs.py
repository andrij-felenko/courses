# -*- coding: utf-8 -*-
# Фігури теми «Типи завад і протидія» (partial-band-jamming).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACCENT = "#b08900"   # бурштиновий акцент


def grid(ox, oy, w, h, ncol, nrow, color="#e0e0e0"):
    """Сітка частота×час: вертикалі (час) і горизонталі (частота)."""
    p = []
    for i in range(ncol + 1):
        x = ox + w * i / ncol
        p.append(line(x, oy, x, oy - h, color=color, sw=1.0))
    for j in range(nrow + 1):
        y = oy - h * j / nrow
        p.append(line(ox, y, ox + w, y, color=color, sw=1.0))
    return "".join(p)


def fig_jamming_types():
    """Чотири класичні класи завад на сітці частота×час."""
    W, H = 780, 420
    p = []
    
    qw, qh = 300, 130
    
    # 1. Barrage
    ox1, oy1 = 70, 160
    p.append(grid(ox1, oy1, qw, qh, 8, 6))
    p.append(rect(ox1, oy1 - qh, qw, qh, fill="#ffebee", stroke=NEG, sw=1.5))
    p.append(text(ox1 + 10, oy1 - qh - 10, "1. Загороджувальна (Barrage)", size=12, color=NEG, bold=True))
    p.append(text(ox1 + qw/2, oy1 - qh/2, "Уся смуга під шумом (мала густина Nⱼ)", size=10, color=INK))
    
    # 2. Spot
    ox2, oy2 = 440, 160
    p.append(grid(ox2, oy2, qw, qh, 8, 6))
    p.append(rect(ox2, oy2 - (qh * 4/6), qw, (qh * 1/6), fill="#ffebee", stroke=NEG, sw=1.5))
    p.append(text(ox2 + 10, oy2 - qh - 10, "2. Прицільна (Spot)", size=12, color=NEG, bold=True))
    p.append(text(ox2 + qw/2, oy2 - qh/2 - 20, "Уся потужність на 1 частоті", size=10, color=INK))
    
    # 3. Partial-band
    ox3, oy3 = 70, 360
    p.append(grid(ox3, oy3, qw, qh, 8, 6))
    p.append(rect(ox3, oy3 - (qh * 5/6), qw, (qh * 2.5/6), fill="#ffebee", stroke=NEG, sw=1.5))
    p.append(text(ox3 + 10, oy3 - qh - 10, "3. Частково-смугова (Partial-Band)", size=12, color=NEG, bold=True))
    p.append(text(ox3 + qw/2, oy3 - qh/2, "Потужність у частці смуги ρ (велика густина Nⱼ/ρ)", size=9.5, color=INK))
    
    # 4. Pulsed
    ox4, oy4 = 440, 360
    p.append(grid(ox4, oy4, qw, qh, 8, 6))
    p.append(rect(ox4 + (qw * 2/8), oy4 - qh, (qw * 1.5/8), qh, fill="#ffebee", stroke=NEG, sw=1.5))
    p.append(rect(ox4 + (qw * 5.5/8), oy4 - qh, (qw * 1.5/8), qh, fill="#ffebee", stroke=NEG, sw=1.5))
    p.append(text(ox4 + 10, oy4 - qh - 10, "4. Імпульсна (Pulsed)", size=12, color=NEG, bold=True))
    p.append(text(ox4 + qw/2, oy4 - qh/2, "Потужні сплески в часі (частотна частка ρₜ)", size=9.5, color=INK))
    
    p.append(text(20, 250, "частота", size=11, color=INK, bold=True))
    p.append(text(410, 395, "час →", size=11, color=INK, bold=True))
    
    render(os.path.join(OUT, "jamming-types.svg"), W, H, *p,
           title="Типи радіозавад на сітці частота-час")


def fig_pbj_mechanism():
    """Механізм ураження FHSS частково-смуговою завадою."""
    W, H = 760, 340
    ox, oy, gw, gh = 90, 270, 620, 200
    ncol, nrow = 10, 8
    p = [grid(ox, oy, gw, gh, ncol, nrow)]
    
    jam_y1 = oy - gh * (6.5 / nrow)
    jam_h = gh * (2.0 / nrow)
    # Зображуємо зона завади через polygon, щоб svgcheck не вважав це перекриттям двох rect
    p.append(f'<polygon points="{ox:.1f},{jam_y1:.1f} {ox+gw:.1f},{jam_y1:.1f} {ox+gw:.1f},{jam_y1+jam_h:.1f} {ox:.1f},{jam_y1+jam_h:.1f}" fill="#ffebee" stroke="{NEG}" stroke-width="1.5"/>')
    p.append(text(ox + gw - 90, jam_y1 + 18, "Завада (ρ = 0.25)", size=11, color=NEG, bold=True))
    
    seq = [1, 5, 2, 6, 0, 4, 5, 3, 7, 1]
    centers = []
    for i, lvl in enumerate(seq):
        cx = ox + gw * (i + 0.5) / ncol
        cy = oy - gh * (lvl + 0.5) / nrow
        centers.append((cx, cy, lvl))
        
    for i in range(len(centers) - 1):
        x1, y1, _ = centers[i]
        x2, y2, _ = centers[i+1]
        p.append(line(x1, y1, x2, y2, color=MUTED, sw=1.0, dash="3 2"))
        
    for cx, cy, lvl in centers:
        if lvl in [5, 6]:
            p.append(rect(cx - 22, cy - 9, 44, 18, fill="#ffebee", stroke=NEG, sw=2.0, rx=3))
            p.append(text(cx, cy + 4, "ЗБИТО", size=9.5, color=NEG, bold=True))
        else:
            p.append(rect(cx - 22, cy - 9, 44, 18, fill="#e9eefb", stroke=FIELD, sw=1.8, rx=3))
            p.append(text(cx, cy + 4, "ОК", size=9.5, color=FIELD, bold=True))
            
    p.append(text(45, 170, "частота", size=11, color=INK, bold=True))
    p.append(text(ox + gw / 2, oy + 30, "час (стрибки) →", size=11, color=INK, bold=True))
    
    p.append(fitbox(60, 290, 640, 35,
                    "Частково-смугова завада знищує 100% бітів у збитих хопах. Без FEC вся рама втрачається.",
                    size=11.5, fill="#fff8e1", stroke=ACCENT, bold=True))
                    
    render(os.path.join(OUT, "pbj-mechanism.svg"), W, H, *p,
           title="Механізм частково-смугової завади проти FHSS")


def fig_ber_curves():
    """Криві BER: загороджувальна завада vs найгірша частково-смугова завада."""
    W, H = 760, 360
    p = []
    
    ox, oy = 110, 300
    w, h = 580, 230
    
    p.append(line(ox, oy, ox + w, oy, color=INK, sw=1.8))
    p.append(line(ox, oy, ox, oy - h, color=INK, sw=1.8))
    p.append(text(ox + w / 2, oy + 35, "Відношення завада/сигнал E_b / N_J (дБ) →", size=11, color=INK, bold=True))
    p.append(text(45, oy - h / 2, "BER (P_e) ↓", size=11, color=INK, bold=True))
    
    for i, label in enumerate(["10⁻¹", "10⁻²", "10⁻³", "10⁻⁴", "10⁻⁵"]):
        y = oy - h * (i + 1) / 5
        p.append(line(ox - 5, y, ox, y, color=INK, sw=1.2))
        p.append(text(ox - 25, y + 4, label, size=10, color=MUTED))
        p.append(line(ox, y, ox + w, y, color="#f0f0f0", sw=1.0))
        
    for i, label in enumerate(["0", "5", "10", "15", "20", "25"]):
        x = ox + w * i / 5
        p.append(line(x, oy, x, oy + 5, color=INK, sw=1.2))
        p.append(text(x, oy + 20, label, size=10, color=MUTED))
        p.append(line(ox, y, ox + w, y, color="#f0f0f0", sw=1.0))
        
    pts1 = []
    for i in range(101):
        eb_db = 25.0 * i / 100
        eb_lin = 10.0 ** (eb_db / 10.0)
        pe = 0.5 * math.exp(-0.5 * eb_lin)
        pe = max(pe, 1e-6)
        log_pe = math.log10(pe)
        y = oy - h * (-log_pe) / 5.0
        x = ox + w * (eb_db / 25.0)
        pts1.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts1), FIELD))
    
    pts2 = []
    for i in range(101):
        eb_db = 25.0 * i / 100
        eb_lin = 10.0 ** (eb_db / 10.0)
        pe = 0.368 / eb_lin if eb_lin >= 2.0 else 0.5 * math.exp(-0.5 * eb_lin)
        pe = max(pe, 1e-6)
        log_pe = math.log10(pe)
        y = oy - h * (-log_pe) / 5.0
        x = ox + w * (eb_db / 25.0)
        pts2.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts2), NEG))
    
    pts3 = []
    for i in range(101):
        eb_db = 25.0 * i / 100
        eb_lin = 10.0 ** (eb_db / 10.0)
        pe_fec = 0.5 * (0.368 / eb_lin) ** 3 if eb_lin >= 2.0 else 0.5
        pe_fec = max(pe_fec, 1e-6)
        log_pe = math.log10(pe_fec)
        y = oy - h * (-log_pe) / 5.0
        x = ox + w * (eb_db / 25.0)
        pts3.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 3"/>' % (" ".join(pts3), POS))
    
    p.append(rect( ox + w - 310, oy - h + 15, 300, 85, fill="#ffffff", stroke="#cccccc", sw=1.0, rx=3))
    p.append(line(ox + w - 300, oy - h + 30, ox + w - 270, oy - h + 30, color=NEG, sw=2.6))
    p.append(text(ox + w - 130, oy - h + 34, "Частково-смугова (найгірший ρₒₚₜ, Pₑ ~ 1/SNR)", size=9.5, color=NEG, bold=True))
    
    p.append(line(ox + w - 300, oy - h + 50, ox + w - 270, oy - h + 50, color=FIELD, sw=2.6))
    p.append(text(ox + w - 130, oy - h + 54, "Загороджувальна (ρ = 1.0, Pₑ ~ exp(-SNR))", size=9.5, color=FIELD, bold=True))
    
    p.append(line(ox + w - 300, oy - h + 70, ox + w - 270, oy - h + 70, color=POS, sw=2.2, dash="5 3"))
    p.append(text(ox + w - 130, oy - h + 74, "З протидією: PBJ + FEC + Перемішування", size=9.5, color=POS, bold=True))
    
    render(os.path.join(OUT, "ber-curves.svg"), W, H, *p,
           title="Криві BER під загороджувальною та частково-смуговою завадою")


def fig_eccm_chain():
    """Ланцюжок протидії завадам (ECCM Pipeline)."""
    W, H = 760, 260
    p = []
    
    b_w, b_h = 140, 50
    y1 = 50
    p.append(rect(30, y1, b_w, b_h, fill="#e9eefb", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(100, y1 + 30, "FEC Кодер (RS/Conv)", size=10, color=INK, bold=True))
    
    p.append(arrow(170, y1 + 25, 210, y1 + 25, color=INK, sw=1.5))
    
    p.append(rect(210, y1, b_w, b_h, fill="#e9eefb", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(280, y1 + 30, "Перемішувач", size=10.5, color=INK, bold=True))
    
    p.append(arrow(350, y1 + 25, 390, y1 + 25, color=INK, sw=1.5))
    
    p.append(rect(390, y1, b_w, b_h, fill="#e9eefb", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(460, y1 + 30, "Модулятор FHSS", size=10.5, color=INK, bold=True))
    
    p.append(arrow(530, y1 + 25, 570, y1 + 25, color=INK, sw=1.5))
    
    p.append(rect(570, y1, 150, b_h, fill="#ffebee", stroke=NEG, sw=2.0, rx=4))
    p.append(text(645, y1 + 20, "Канал зв'язку", size=10.5, color=NEG, bold=True))
    p.append(text(645, y1 + 36, "+ Завада (PBJ)", size=9.5, color=NEG))
    
    p.append(arrow(645, y1 + b_h, 645, y1 + 100, color=NEG, sw=1.5))
    
    y2 = 140
    p.append(rect(570, y2, 150, b_h, fill="#e8f5e9", stroke=POS, sw=1.8, rx=4))
    p.append(text(645, y2 + 20, "CRPA Антена", size=10.5, color=POS, bold=True))
    p.append(text(645, y2 + 36, "(просторовий нуль)", size=9, color=MUTED))
    
    p.append(arrow(570, y2 + 25, 530, y2 + 25, color=INK, sw=1.5))
    
    p.append(rect(390, y2, b_w, b_h, fill="#e8f5e9", stroke=POS, sw=1.8, rx=4))
    p.append(text(460, y2 + 20, "FHSS Демодулятор", size=10, color=INK, bold=True))
    p.append(text(460, y2 + 36, "+ Адаптивний AFH", size=9, color=MUTED))
    
    p.append(arrow(390, y2 + 25, 350, y2 + 25, color=INK, sw=1.5))
    
    p.append(rect(210, y2, b_w, b_h, fill="#e8f5e9", stroke=POS, sw=1.8, rx=4))
    p.append(text(280, y2 + 30, "Деперемішувач", size=10.5, color=INK, bold=True))
    
    p.append(arrow(210, y2 + 25, 170, y2 + 25, color=INK, sw=1.5))
    
    p.append(rect(30, y2, b_w, b_h, fill="#e8f5e9", stroke=POS, sw=1.8, rx=4))
    p.append(text(100, y2 + 20, "FEC Декодер", size=10.5, color=INK, bold=True))
    p.append(text(100, y2 + 36, "(зі стиранням/erasure)", size=9, color=POS, bold=True))
    
    p.append(fitbox(40, 215, 680, 30,
                    "Повний комплекс протидії: Просторовий нуль → Стрибки AFH → Розпорошення пакетів → FEC зі стиранням.",
                    size=11, fill="#f5f5f5", stroke=INK, bold=True))
                    
    render(os.path.join(OUT, "eccm-chain.svg"), W, H, *p,
           title="Структурна схема комплексної протидії радіозавадам (ECCM Pipeline)")


def main():
    fig_jamming_types()
    fig_pbj_mechanism()
    fig_ber_curves()
    fig_eccm_chain()
    print("Всі фігури успішно згенеровано у ./img/")

if __name__ == "__main__":
    main()
