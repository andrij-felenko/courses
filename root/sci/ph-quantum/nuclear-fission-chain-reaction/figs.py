# -*- coding: utf-8 -*-
import sys
import os

# Four parent levels up to reach scripts/ in workspace root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_fission_barrier():
    """Малює графік потенціальної енергії ядра як функції деформації."""
    w, h = 860, 480
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%" style="background:#ffffff;">' % (w, h),
        '<defs>',
        '<marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>',
        '</marker>',
        '</defs>'
    ]
    
    # Заголовок (y = 20)
    tb, tw, th = textbox(w/2, 20, "Потенціальний бар'єр поділу та деформація ядра", size=14, bold=True, fill="#ffffff", stroke="#ffffff")
    out.append(tb)

    # Схематичні малюнки форми ядра під заголовком (y = 55)
    ox, oy = 140, 400

    out.append(circle(ox + 100, 55, 13, fill="#fff3e0", stroke="#e65100", sw=1.5))
    tb_s1, _, _ = textbox(ox + 100, 78, "Сфера", size=9, fill="#ffffff", stroke="#ffffff", pad=1)
    out.append(tb_s1)

    out.append(f'<ellipse cx="{ox+180}" cy="55" rx="19" ry="11" fill="#fff3e0" stroke="#e65100" stroke-width="1.5"/>')
    tb_s2, _, _ = textbox(ox + 180, 78, "Еліпсоїд", size=9, fill="#ffffff", stroke="#ffffff", pad=1)
    out.append(tb_s2)

    out.append(circle(ox + 250, 55, 9, fill="#fff3e0", stroke="#e65100", sw=1.5))
    out.append(circle(ox + 267, 55, 9, fill="#fff3e0", stroke="#e65100", sw=1.5))
    tb_s3, _, _ = textbox(ox + 258, 78, "Перетяжка", size=9, fill="#ffffff", stroke="#ffffff", pad=1)
    out.append(tb_s3)

    out.append(circle(ox + 370, 55, 8, fill="#ffe0b2", stroke="#e65100", sw=1.5))
    out.append(circle(ox + 391, 55, 10, fill="#ffe0b2", stroke="#e65100", sw=1.5))
    tb_s4, _, _ = textbox(ox + 380, 78, "Уламки + n", size=9, fill="#ffffff", stroke="#ffffff", pad=1)
    out.append(tb_s4)

    # Вісі координат
    out.append(line(ox, oy, ox + 660, oy, color=INK, sw=1.8))
    out.append(arrow(ox, oy, ox, 100, color=INK, sw=1.8))
    out.append(text(ox + 660, oy + 28, "Деформація ядра r (подовження)", size=11, anchor="end", italic=True))
    out.append(text(ox + 10, 105, "Потенціальна енергія V(r) [МеВ]", size=11, anchor="start", italic=True))

    # Лінія нульової енергії
    out.append(line(ox, oy - 100, ox + 660, oy - 100, color=MUTED, sw=1, dash="4,4"))
    out.append(text(ox - 10, oy - 96, "0", size=11, color=MUTED, anchor="end"))

    # Крива потенціальної енергії V(r)
    # R_0 = ox+130 (y = oy-210 = 190)
    # Saddle = ox+230 (y = oy-260 = 140)
    path_d = (
        f"M {ox} {oy-100} "
        f"C {ox+50} {oy-100}, {ox+70} {oy-210}, {ox+130} {oy-210} "
        f"C {ox+180} {oy-210}, {ox+180} {oy-260}, {ox+230} {oy-260} "
        f"C {ox+290} {oy-260}, {ox+330} {oy-170}, {ox+380} {oy-120} "
        f"C {ox+440} {oy-50}, {ox+530} {oy-30}, {ox+620} {oy-20}"
    )
    out.append(f'<path d="{path_d}" fill="none" stroke="{POS}" stroke-width="3"/>')

    # Пунктири точок
    out.append(line(ox + 130, oy - 210, ox + 130, oy - 15, color=MUTED, sw=1, dash="3,3"))
    tb_r0, _, _ = textbox(ox + 130, oy + 18, "r₀ (основний стан)", size=9, fill="#ffffff", stroke="#ffffff", pad=1)
    out.append(tb_r0)

    out.append(line(ox + 230, oy - 260, ox + 230, oy - 15, color=MUTED, sw=1, dash="3,3"))
    tb_rs, _, _ = textbox(ox + 230, oy + 18, "r_saddle (вершина)", size=9, fill="#ffffff", stroke="#ffffff", pad=1)
    out.append(tb_rs)

    # Бар'єр поділу E_b (розміщено лівіше x=175, y=oy-235 = 165, не перетинаючи червону криву)
    out.append(arrow(ox + 175, oy - 210, ox + 175, oy - 260, color=NEG, sw=1.5))
    out.append(arrow(ox + 175, oy - 260, ox + 175, oy - 210, color=NEG, sw=1.5))
    tb_eb, _, _ = textbox(ox + 175, oy - 280, "E_b ≈ 5.8 МеВ", size=10, bold=True, fill="#e8f0fe", stroke=NEG, pad=3)
    out.append(tb_eb)

    # Рівні збудження E_exc (праворуч від вершини x > 300)
    out.append(line(ox + 40, oy - 290, ox + 210, oy - 290, color=FIELD, sw=2, dash="5,3"))
    tb_u235, _, _ = textbox(ox + 440, oy - 290, "E_exc(²³⁶U*) ≈ 6.5 МеВ > E_b (теплові n)", size=10, bold=True, fill="#e6f4ea", stroke=FIELD, pad=3)
    out.append(tb_u235)

    out.append(line(ox + 40, oy - 225, ox + 150, oy - 225, color=POS, sw=2, dash="5,3"))
    tb_u238, _, _ = textbox(ox + 440, oy - 225, "E_exc(²³⁹U*) ≈ 4.8 МеВ < E_b (потрібні швидкі n)", size=10, bold=True, fill="#fce8e6", stroke=POS, pad=3)
    out.append(tb_u238)

    # Точка розриву та виділена енергія Q
    out.append(line(ox + 380, oy - 120, ox + 380, oy - 15, color=MUTED, sw=1, dash="3,3"))
    tb_rsc, _, _ = textbox(ox + 380, oy + 18, "r_scission (розрив)", size=9, fill="#ffffff", stroke="#ffffff", pad=1)
    out.append(tb_rsc)

    out.append(arrow(ox + 540, oy - 125, ox + 540, oy - 98, color=FIELD, sw=1.8))
    tb_q, _, _ = textbox(ox + 540, oy - 75, "Виділена енергія\nQ ≈ 200 МеВ", size=10, bold=True, fill="#e6f4ea", stroke=FIELD, pad=4)
    out.append(tb_q)
    out.append(arrow(ox + 540, oy - 52, ox + 540, oy - 25, color=FIELD, sw=1.8))

    out.append('</svg>')
    return "\n".join(out)

def generate_fission_yield():
    """Малює двохгорбий розподіл мас уламків поділу 235U."""
    w, h = 860, 480
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%" style="background:#ffffff;">',
        '<defs>',
        '<marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>',
        '</marker>',
        '</defs>'
    ]
    out[0] = out[0] % (w, h)

    tb, _, _ = textbox(w/2, 20, "Масовий вихід уламків поділу ²³⁵U тепловими нейтронами", size=14, bold=True, fill="#ffffff", stroke="#ffffff")
    out.append(tb)

    ox, oy = 140, 400
    out.append(line(ox, oy, ox + 660, oy, color=INK, sw=1.8))
    out.append(arrow(ox, oy, ox, 70, color=INK, sw=1.8))
    out.append(text(ox + 660, oy + 28, "Масове число уламка A", size=11, anchor="end", italic=True))
    out.append(text(ox + 10, 65, "Вихід уламків Y(A) [%]", size=11, anchor="start", italic=True))

    y_levels = [
        (oy - 50, "0.001%"),
        (oy - 120, "0.01%"),
        (oy - 190, "0.1%"),
        (oy - 260, "1.0%"),
        (oy - 310, "7.0%")
    ]
    for y_pos, lbl in y_levels:
        out.append(line(ox, y_pos, ox + 660, y_pos, color="#e0e0e0", sw=1, dash="3,3"))
        out.append(text(ox - 10, y_pos + 4, lbl, size=10, color=MUTED, anchor="end"))

    x_ticks = [
        (70, ox + 60),
        (95, ox + 195),
        (118, ox + 310),
        (138, ox + 415),
        (160, ox + 530)
    ]
    for val, x_pos in x_ticks:
        out.append(line(x_pos, oy, x_pos, oy + 6, color=INK, sw=1.5))
        tb_t, _, _ = textbox(x_pos, oy + 16, str(val), size=10, fill="#ffffff", stroke="#ffffff", pad=1)
        out.append(tb_t)

    path_d = (
        f"M {ox+30} {oy-20} "
        f"C {ox+80} {oy-40}, {ox+120} {oy-180}, {ox+170} {oy-300} "
        f"C {ox+195} {oy-320}, {ox+210} {oy-300}, {ox+230} {oy-220} "
        f"C {ox+260} {oy-120}, {ox+290} {oy-110}, {ox+310} {oy-105} "
        f"C {ox+330} {oy-110}, {ox+370} {oy-220}, {ox+400} {oy-300} "
        f"C {ox+415} {oy-320}, {ox+435} {oy-300}, {ox+470} {oy-180} "
        f"C {ox+510} {oy-50}, {ox+540} {oy-20}, {ox+580} {oy-10}"
    )
    out.append(f'<path d="{path_d}" fill="none" stroke="{NEG}" stroke-width="3"/>')

    path_fill = path_d + f" L {ox+580} {oy} L {ox+30} {oy} Z"
    out.append(f'<path d="{path_fill}" fill="{NEG}" fill-opacity="0.08"/>')

    # Заголовок піків рознесено на y = 50 (без накладання на заголовок малюнка)
    tb1, _, _ = textbox(ox + 180, 50, "Легкова група\nA ≈ 95 (⁹⁵Sr, ⁹⁹Mo)", size=9, bold=True, fill="#e8f0fe", stroke=NEG, pad=2)
    out.append(tb1)

    tb2, _, _ = textbox(ox + 440, 50, "Важкова група\nA ≈ 138 (¹³⁷I, ¹³⁹Ba, ¹⁴⁴Ce)", size=9, bold=True, fill="#e8f0fe", stroke=NEG, pad=2)
    out.append(tb2)

    # Пунктирні лінії оболонок (без перетину плашок)
    out.append(line(ox + 195, oy - 300, ox + 195, oy - 265, color=FIELD, sw=1.2, dash="4,4"))
    out.append(line(ox + 195, oy - 230, ox + 195, oy - 15, color=FIELD, sw=1.2, dash="4,4"))
    tb_m1, _, _ = textbox(ox + 195, oy - 247, "Оболонка N=50", size=9, bold=True, fill="#e6f4ea", stroke=FIELD, pad=2)
    out.append(tb_m1)

    out.append(line(ox + 415, oy - 300, ox + 415, oy - 265, color=FIELD, sw=1.2, dash="4,4"))
    out.append(line(ox + 415, oy - 230, ox + 415, oy - 15, color=FIELD, sw=1.2, dash="4,4"))
    tb_m2, _, _ = textbox(ox + 415, oy - 247, "Оболонка N=82", size=9, bold=True, fill="#e6f4ea", stroke=FIELD, pad=2)
    out.append(tb_m2)

    out.append(circle(ox + 310, oy - 105, 4, fill=POS, stroke=POS, sw=1))
    tb_sym, _, _ = textbox(ox + 310, oy - 65, "Симетричний поділ\nA = 118 (в 600 разів рідше)", size=9, fill="#fce8e6", stroke=POS, pad=3)
    out.append(tb_sym)

    out.append('</svg>')
    return "\n".join(out)

def generate_neutron_cycle():
    """Малює баланс нейтронного циклу та формулу чотирьох співмножників."""
    w, h = 860, 480
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%" style="background:#ffffff;">',
        '<defs>',
        '<marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>',
        '</marker>',
        '</defs>'
    ]
    out[0] = out[0] % (w, h)

    tb, _, _ = textbox(w/2, 22, "Нейтронний цикл реактора та формула чотирьох співмножників k_inf = η · f · p · ε", size=14, bold=True, fill="#ffffff", stroke="#ffffff")
    out.append(tb)

    tb1, _, _ = textbox(200, 110, "1000 теплових нейтронів\nпоглинаються у паливі", size=10, bold=True, fill="#e8f0fe", stroke=NEG, pad=5)
    out.append(tb1)

    out.append(arrow(300, 110, 390, 110, color=INK, sw=2))
    tb_l1, _, _ = textbox(345, 82, "× η (вихід 2.08)", size=9, bold=True, fill="#e8f0fe", stroke=NEG, pad=2)
    out.append(tb_l1)

    tb2, _, _ = textbox(510, 110, "2080 швидких нейтронів\nвід поділу ²³⁵U", size=10, bold=True, fill="#fff3e0", stroke="#e65100", pad=5)
    out.append(tb2)

    out.append(arrow(510, 145, 510, 230, color=INK, sw=2))
    tb_l2, _, _ = textbox(595, 185, "× ε (швидке розмноження ≈ 1.03)", size=9, bold=True, fill="#fff3e0", stroke="#e65100", pad=2)
    out.append(tb_l2)

    tb3, _, _ = textbox(510, 265, "2142 швидких нейтронів\nперед уповільненням", size=10, bold=True, fill="#fff3e0", stroke="#e65100", pad=5)
    out.append(tb3)

    out.append(arrow(400, 265, 300, 265, color=INK, sw=2))
    tb_l3, _, _ = textbox(350, 235, "× p (уникнення резонансів ≈ 0.88)", size=9, bold=True, fill="#e6f4ea", stroke=FIELD, pad=2)
    out.append(tb_l3)

    out.append(arrow(510, 300, 510, 375, color=POS, sw=1.5))
    tb_fll, _, _ = textbox(510, 400, "Виток швидких нейтронів (1 - P_FNL)", size=9, fill="#ffffff", stroke="#ffffff", pad=1)
    out.append(tb_fll)

    tb4, _, _ = textbox(200, 265, "1885 епітеплових нейтронів\nстають тепловими", size=10, bold=True, fill="#e6f4ea", stroke=FIELD, pad=5)
    out.append(tb4)

    out.append(arrow(200, 230, 200, 145, color=INK, sw=2))
    tb_l4, _, _ = textbox(115, 185, "× f (використання ≈ 0.53)", size=9, bold=True, fill="#e8f0fe", stroke=NEG, pad=2)
    out.append(tb_l4)

    out.append(arrow(200, 300, 200, 375, color=POS, sw=1.5))
    tb_tll, _, _ = textbox(200, 400, "Виток теплових нейтронів (1 - P_TNL)", size=9, fill="#ffffff", stroke="#ffffff", pad=1)
    out.append(tb_tll)

    tb_eq, _, _ = textbox(w/2, 445, "k_eff = k_inf · P_FNL · P_TNL = (η · f · p · ε) · P_FNL · P_TNL = 1.000 (стаціонар)", size=10, bold=True, fill="#f4f6f8", stroke=INK, pad=5)
    out.append(tb_eq)

    out.append('</svg>')
    return "\n".join(out)

def main():
    target_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(target_dir, exist_ok=True)
    
    files = {
        'fission-barrier-potential.svg': generate_fission_barrier(),
        'fission-yield-curve.svg': generate_fission_yield(),
        'chain-reaction-neutron-cycle.svg': generate_neutron_cycle()
    }
    
    for filename, content in files.items():
        filepath = os.path.join(target_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == '__main__':
    main()
