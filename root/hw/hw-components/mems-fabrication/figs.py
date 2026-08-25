# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *
os.makedirs("img", exist_ok=True)

def fig_bulk_vs_surface():
    W, H = 940, 440
    parts = []
    pw, gap, x0, top_y = 280, 25, 25, 65
    # 1. Bulk
    x1 = x0
    parts.append(rect(x1, top_y, pw, 295, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x1 + pw / 2, top_y + 24, "Об’ємна (Bulk)", size=15, bold=True, color=INK))
    parts.append(text(x1 + pw / 2, top_y + 44, "вирізання в масиві підкладки", size=11, color=MUTED))
    parts.append(rect(x1 + 20, top_y + 70, pw - 40, 180, fill="#dce4ec", stroke=INK, sw=1.5, rx=2))
    parts.append(text(x1 + pw / 2, top_y + 235, "Монокристалічний Si (300–500 мкм)", size=10, color=MUTED))
    v_poly = f"{x1+65},{top_y+70} {x1+95},{top_y+160} {x1+185},{top_y+160} {x1+215},{top_y+70}"
    parts.append(f"<polygon points='{v_poly}' fill='#ffffff' stroke='{POS}' stroke-width='1.8'/>")
    parts.append(text(x1 + pw / 2, top_y + 115, "Травлення KOH", size=11, bold=True, color=POS))
    parts.append(text(x1 + pw / 2, top_y + 132, "кути {111} під 54.74°", size=10, color=POS))
    parts.append(line(x1 + 95, top_y + 160, x1 + 185, top_y + 160, color=FIELD, sw=3))
    parts.append(text(x1 + pw / 2, top_y + 180, "Тонка мембрана (10–20 мкм)", size=10, bold=True, color=FIELD))
    box1, _, _ = textbox(x1 + pw / 2, top_y + 270, "Масивні порожнини й мембрани\nВелика маса, але велика площа", size=10, pad=6, fill="#ffffff")
    parts.append(box1)
    # 2. Surface
    x2 = x0 + pw + gap
    parts.append(rect(x2, top_y, pw, 295, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x2 + pw / 2, top_y + 24, "Поверхнева (Surface)", size=15, bold=True, color=INK))
    parts.append(text(x2 + pw / 2, top_y + 44, "нарощування та жертва на пласті", size=11, color=MUTED))
    parts.append(rect(x2 + 20, top_y + 170, pw - 40, 80, fill="#dce4ec", stroke=INK, sw=1.5, rx=2))
    parts.append(text(x2 + pw / 2, top_y + 235, "Пасивна підкладка Si", size=10, color=MUTED))
    parts.append(rect(x2 + 20, top_y + 160, pw - 40, 10, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=0))
    parts.append(rect(x2 + 40, top_y + 120, 25, 40, fill="#cfe0f5", stroke=NEG, sw=1.5, rx=1))
    parts.append(rect(x2 + pw - 65, top_y + 120, 25, 40, fill="#cfe0f5", stroke=NEG, sw=1.5, rx=1))
    parts.append(rect(x2 + 40, top_y + 110, pw - 80, 15, fill="#cfe0f5", stroke=NEG, sw=1.8, rx=2))
    parts.append(text(x2 + pw / 2, top_y + 98, "Полікремній Poly-Si (2–4 мкм)", size=10, bold=True, color=NEG))
    parts.append(line(x2 + 65, top_y + 140, x2 + pw - 65, top_y + 140, color=POS, sw=1.2, dash="3,3"))
    parts.append(text(x2 + pw / 2, top_y + 148, "Розчинений жертовний SiO₂", size=10, color=POS))
    box2, _, _ = textbox(x2 + pw / 2, top_y + 270, "Тонкі балки, гребінці, пружини\nКомпактно, але ризик стикції", size=10, pad=6, fill="#ffffff")
    parts.append(box2)
    # 3. SOI MEMS
    x3 = x0 + (pw + gap) * 2
    parts.append(rect(x3, top_y, pw, 295, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x3 + pw / 2, top_y + 24, "Технологія SOI MEMS", size=15, bold=True, color=INK))
    parts.append(text(x3 + pw / 2, top_y + 44, "монокристал + глибоке DRIE", size=11, color=MUTED))
    parts.append(rect(x3 + 20, top_y + 175, pw - 40, 75, fill="#dce4ec", stroke=INK, sw=1.5, rx=2))
    parts.append(text(x3 + pw / 2, top_y + 235, "Handle Wafer Si (400 мкм)", size=10, color=MUTED))
    parts.append(rect(x3 + 20, top_y + 160, 45, 15, fill="#fed7aa", stroke="#ea580c", sw=1.2, rx=0))
    parts.append(rect(x3 + pw - 65, top_y + 160, 45, 15, fill="#fed7aa", stroke="#ea580c", sw=1.2, rx=0))
    parts.append(text(x3 + pw / 2, top_y + 169, "Витравлений BOX (SiO₂)", size=10, color="#ea580c"))
    parts.append(rect(x3 + 20, top_y + 85, 45, 75, fill="#bbf7d0", stroke=FIELD, sw=1.5, rx=1))
    parts.append(rect(x3 + pw - 65, top_y + 85, 45, 75, fill="#bbf7d0", stroke=FIELD, sw=1.5, rx=1))
    parts.append(rect(x3 + 80, top_y + 85, pw - 160, 65, fill="#bbf7d0", stroke=FIELD, sw=1.8, rx=2))
    parts.append(text(x3 + pw / 2, top_y + 118, "Товстий Si (20–100 мкм)", size=11, bold=True, color=FIELD))
    parts.append(text(x3 + pw / 2, top_y + 134, "Вертикальні стінки DRIE", size=10, color=FIELD))
    box3, _, _ = textbox(x3 + pw / 2, top_y + 270, "Ідеальний монокристал + маса\nВисока добротність Q і точність", size=10, pad=6, fill="#ffffff")
    parts.append(box3)
    box_foot, _, _ = textbox(W / 2, H - 35, "MEMS поєднує об’ємне травлення підкладки, поверхневі жертви та товстий кремній на ізоляторі (SOI)", size=12, pad=10, fill=FILL)
    parts.append(box_foot)
    render("img/bulk-vs-surface.svg", W, H, *parts, title="Три парадигми виготовлення MEMS-структур")

def fig_bosch_drie_cycle():
    W, H = 940, 420
    parts = []
    pw, gap, x0, top_y = 210, 20, 20, 65
    # 1. SF6
    x = x0
    parts.append(rect(x, top_y, pw, 280, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x + pw / 2, top_y + 24, "1. Травлення SF₆", size=14, bold=True, color=POS))
    parts.append(text(x + pw / 2, top_y + 42, "радикали F* їдять кремній", size=10, color=MUTED))
    parts.append(rect(x + 20, top_y + 60, 45, 20, fill="#cbd5e1", stroke=INK, sw=1.2, rx=1))
    parts.append(rect(x + pw - 65, top_y + 60, 45, 20, fill="#cbd5e1", stroke=INK, sw=1.2, rx=1))
    parts.append(text(x + 42, top_y + 74, "Маска", size=9, bold=True))
    parts.append(text(x + pw - 42, top_y + 74, "Маска", size=9, bold=True))
    parts.append(rect(x + 20, top_y + 80, pw - 40, 130, fill="#dce4ec", stroke=INK, sw=1.5, rx=0))
    path_etch = f"M {x+65},{top_y+80} Q {x+pw/2},{top_y+130} {x+pw-65},{top_y+80} Z"
    parts.append(f"<path d='{path_etch}' fill='#ffffff' stroke='{POS}' stroke-width='1.5'/>")
    parts.append(text(x + pw / 2, top_y + 105, "Ізотропна", size=11, bold=True, color=POS))
    parts.append(text(x + pw / 2, top_y + 120, "виїмка (F*)", size=10, color=POS))
    box1, _, _ = textbox(x + pw / 2, top_y + 240, "Плазма SF₆\nХімічне травлення Si\nЧас: 1–3 с", size=10, pad=6, fill="#ffffff")
    parts.append(box1)
    parts.append(arrow(x + pw + 3, top_y + 140, x + pw + gap - 3, top_y + 140, color=INK, sw=1.6))
    # 2. C4F8
    x = x0 + pw + gap
    parts.append(rect(x, top_y, pw, 280, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x + pw / 2, top_y + 24, "2. Пасивація C₄F₈", size=14, bold=True, color=NEG))
    parts.append(text(x + pw / 2, top_y + 42, "осадження тефлонової плівки", size=10, color=MUTED))
    parts.append(rect(x + 20, top_y + 60, 45, 20, fill="#cbd5e1", stroke=INK, sw=1.2, rx=1))
    parts.append(rect(x + pw - 65, top_y + 60, 45, 20, fill="#cbd5e1", stroke=INK, sw=1.2, rx=1))
    parts.append(rect(x + 20, top_y + 80, pw - 40, 130, fill="#dce4ec", stroke=INK, sw=1.5, rx=0))
    parts.append(f"<path d='{path_etch.replace(str(x0), str(x))}' fill='#ffffff' stroke='{MUTED}' stroke-width='1'/>")
    path_poly = f"M {x+20},{top_y+60} L {x+65},{top_y+60} L {x+65},{top_y+80} Q {x+pw/2},{top_y+130} {x+pw-65},{top_y+80} L {x+pw-65},{top_y+60} L {x+pw-20},{top_y+60}"
    parts.append(f"<path d='{path_poly}' fill='none' stroke='{FIELD}' stroke-width='3'/>")
    parts.append(text(x + pw / 2, top_y + 105, "Полімер (CF₂)ₙ", size=11, bold=True, color=FIELD))
    parts.append(text(x + pw / 2, top_y + 120, "захищає все", size=10, color=FIELD))
    box2, _, _ = textbox(x + pw / 2, top_y + 240, "Плазма C₄F₈\nСуцільна плівка (CF₂)ₙ\nЧас: 1–2 с", size=10, pad=6, fill="#ffffff")
    parts.append(box2)
    parts.append(arrow(x + pw + 3, top_y + 140, x + pw + gap - 3, top_y + 140, color=INK, sw=1.6))
    # 3. Directional Ion
    x = x0 + (pw + gap) * 2
    parts.append(rect(x, top_y, pw, 280, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x + pw / 2, top_y + 24, "3. Іонне розкриття", size=14, bold=True, color="#ea580c"))
    parts.append(text(x + pw / 2, top_y + 42, "вертикальні іони б’ють у дно", size=10, color=MUTED))
    parts.append(rect(x + 20, top_y + 60, 45, 20, fill="#cbd5e1", stroke=INK, sw=1.2, rx=1))
    parts.append(rect(x + pw - 65, top_y + 60, 45, 20, fill="#cbd5e1", stroke=INK, sw=1.2, rx=1))
    parts.append(rect(x + 20, top_y + 80, pw - 40, 130, fill="#dce4ec", stroke=INK, sw=1.5, rx=0))
    parts.append(f"<path d='{path_etch.replace(str(x0), str(x))}' fill='#ffffff' stroke='{MUTED}' stroke-width='1'/>")
    parts.append(f"<path d='M {x+65},{top_y+80} Q {x+75},{top_y+115} {x+90},{top_y+125}' fill='none' stroke='{FIELD}' stroke-width='3'/>")
    parts.append(f"<path d='M {x+pw-65},{top_y+80} Q {x+pw-75},{top_y+115} {x+pw-90},{top_y+125}' fill='none' stroke='{FIELD}' stroke-width='3'/>")
    for ix in [x + 95, x + pw / 2, x + pw - 95]:
        parts.append(arrow(ix, top_y + 65, ix, top_y + 115, color="#ea580c", sw=1.4))
    parts.append(text(x + pw / 2, top_y + 145, "Дно очищено!", size=11, bold=True, color="#ea580c"))
    box3, _, _ = textbox(x + pw / 2, top_y + 240, "Іони здирають дно\nСтінки лишаються вкриті\nПерехід до кроку 1", size=10, pad=6, fill="#ffffff")
    parts.append(box3)
    parts.append(arrow(x + pw + 3, top_y + 140, x + pw + gap - 3, top_y + 140, color=INK, sw=1.6))
    # 4. DRIE Result
    x = x0 + (pw + gap) * 3
    parts.append(rect(x, top_y, pw, 280, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x + pw / 2, top_y + 24, "Результат: DRIE", size=14, bold=True, color=INK))
    parts.append(text(x + pw / 2, top_y + 42, "глибока вертикальна траншея", size=10, color=MUTED))
    parts.append(rect(x + 20, top_y + 60, 45, 20, fill="#cbd5e1", stroke=INK, sw=1.2, rx=1))
    parts.append(rect(x + pw - 65, top_y + 60, 45, 20, fill="#cbd5e1", stroke=INK, sw=1.2, rx=1))
    parts.append(rect(x + 20, top_y + 80, pw - 40, 130, fill="#dce4ec", stroke=INK, sw=1.5, rx=0))
    trench_path = (f"M {x+65},{top_y+80} "
                   f"Q {x+70},{top_y+95} {x+65},{top_y+110} "
                   f"Q {x+70},{top_y+125} {x+65},{top_y+140} "
                   f"Q {x+70},{top_y+155} {x+65},{top_y+170} "
                   f"L {x+pw-65},{top_y+170} "
                   f"Q {x+pw-70},{top_y+155} {x+pw-65},{top_y+140} "
                   f"Q {x+pw-70},{top_y+125} {x+pw-65},{top_y+110} "
                   f"Q {x+pw-70},{top_y+95} {x+pw-65},{top_y+80} Z")
    parts.append(f"<path d='{trench_path}' fill='#ffffff' stroke='{POS}' stroke-width='1.8'/>")
    parts.append(text(x + pw / 2, top_y + 115, "Аспект > 50:1", size=11, bold=True, color=POS))
    parts.append(text(x + pw / 2, top_y + 132, "Хвилястість стінок", size=9, color=MUTED))
    parts.append(text(x + pw / 2, top_y + 146, "(scalloping 50–200 нм)", size=9, color=MUTED))
    box4, _, _ = textbox(x + pw / 2, top_y + 240, "Сотні циклів\nГлибина 10–500 мкм\nПрямовисні стінки 90°", size=10, pad=6, fill="#ffffff")
    parts.append(box4)
    box_foot, _, _ = textbox(W / 2, H - 35, "Процес Bosch чергує травлення SF₆ і пасивацію C₄F₈, забезпечуючи високе співвідношення глибини до ширини", size=12, pad=10, fill=FILL)
    parts.append(box_foot)
    render("img/bosch-drie-cycle.svg", W, H, *parts, title="Процес Bosch: циклічне глибоке реактивне іонне травлення (DRIE)")

def fig_surface_micromachining_release():
    W, H = 940, 440
    parts = []
    pw, gap, x0, top_y = 210, 20, 20, 65
    # 1. Sacrificial
    x = x0
    parts.append(rect(x, top_y, pw, 300, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x + pw / 2, top_y + 24, "1. Жертовний SiO₂", size=14, bold=True, color=INK))
    parts.append(text(x + pw / 2, top_y + 42, "оксид + вікна під якорі", size=10, color=MUTED))
    parts.append(rect(x + 20, top_y + 160, pw - 40, 60, fill="#dce4ec", stroke=INK, sw=1.5, rx=0))
    parts.append(text(x + pw / 2, top_y + 200, "Підкладка кремнію", size=10, color=MUTED))
    parts.append(rect(x + 20, top_y + 152, pw - 40, 8, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=0))
    parts.append(rect(x + 55, top_y + 128, pw - 75, 24, fill="#fed7aa", stroke="#ea580c", sw=1.2, rx=0))
    parts.append(text(x + pw / 2 + 10, top_y + 144, "Жертовний оксид (SiO₂)", size=9, bold=True, color="#ea580c"))
    parts.append(line(x + 55, top_y + 128, x + 55, top_y + 152, color=POS, sw=1.5, dash="2,2"))
    parts.append(text(x + 36, top_y + 120, "Якір", size=10, bold=True, color=POS))
    box1, _, _ = textbox(x + pw / 2, top_y + 255, "LPCVD осадження SiO₂ (1–3 мкм)\nФотолітографія й RIE отворів\nпід опорні якорі", size=10, pad=6, fill="#ffffff")
    parts.append(box1)
    parts.append(arrow(x + pw + 3, top_y + 140, x + pw + gap - 3, top_y + 140, color=INK, sw=1.6))
    # 2. Structural Poly-Si
    x = x0 + pw + gap
    parts.append(rect(x, top_y, pw, 300, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x + pw / 2, top_y + 24, "2. Структурний Poly-Si", size=14, bold=True, color=NEG))
    parts.append(text(x + pw / 2, top_y + 42, "нарощування балки й отворів", size=10, color=MUTED))
    parts.append(rect(x + 20, top_y + 160, pw - 40, 60, fill="#dce4ec", stroke=INK, sw=1.5, rx=0))
    parts.append(rect(x + 20, top_y + 152, pw - 40, 8, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=0))
    parts.append(rect(x + 55, top_y + 128, pw - 75, 24, fill="#fed7aa", stroke="#ea580c", sw=1.2, rx=0))
    parts.append(rect(x + 25, top_y + 110, 30, 42, fill="#cfe0f5", stroke=NEG, sw=1.5, rx=1))
    parts.append(rect(x + 55, top_y + 110, pw - 80, 18, fill="#cfe0f5", stroke=NEG, sw=1.5, rx=1))
    parts.append(text(x + pw / 2 + 15, top_y + 102, "Балка Poly-Si", size=10, bold=True, color=NEG))
    for hx in [x + 95, x + 130, x + 165]:
        parts.append(rect(hx, top_y + 110, 8, 18, fill="#ffffff", stroke=NEG, sw=1.2, rx=0))
    parts.append(text(x + pw / 2 + 15, top_y + 88, "Отвори перфорації", size=9, color=MUTED))
    box2, _, _ = textbox(x + pw / 2, top_y + 255, "LPCVD Poly-Si (2–4 мкм)\nЛегування фосфором + відпал\nТравлення геометрії та отворів", size=10, pad=6, fill="#ffffff")
    parts.append(box2)
    parts.append(arrow(x + pw + 3, top_y + 140, x + pw + gap - 3, top_y + 140, color=INK, sw=1.6))
    # 3. HF Release
    x = x0 + (pw + gap) * 2
    parts.append(rect(x, top_y, pw, 300, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x + pw / 2, top_y + 24, "3. Розчинення в HF", size=14, bold=True, color=POS))
    parts.append(text(x + pw / 2, top_y + 42, "вивільнення балки кислотою", size=10, color=MUTED))
    parts.append(rect(x + 20, top_y + 160, pw - 40, 60, fill="#dce4ec", stroke=INK, sw=1.5, rx=0))
    parts.append(rect(x + 20, top_y + 152, pw - 40, 8, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=0))
    parts.append(rect(x + 25, top_y + 110, 30, 42, fill="#cfe0f5", stroke=NEG, sw=1.5, rx=1))
    parts.append(rect(x + 55, top_y + 110, pw - 80, 18, fill="#cfe0f5", stroke=NEG, sw=1.5, rx=1))
    parts.append(rect(x + 55, top_y + 128, pw - 75, 24, fill="#eff6ff", stroke=POS, sw=1.2, rx=0))
    parts.append(text(x + pw / 2 + 10, top_y + 144, "Рідкий розчин HF", size=9, bold=True, color=POS))
    box3, _, _ = textbox(x + pw / 2, top_y + 255, "Селективне травлення HF:SiO₂\nСелективність > 10000:1 до Si\nОксид повністю видалено", size=10, pad=6, fill="#ffffff")
    parts.append(box3)
    parts.append(arrow(x + pw + 3, top_y + 140, x + pw + gap - 3, top_y + 140, color=INK, sw=1.6))
    # 4. Stiction
    x = x0 + (pw + gap) * 3
    parts.append(rect(x, top_y, pw, 300, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x + pw / 2, top_y + 24, "4. Сушіння: Стикція!", size=14, bold=True, color=POS))
    parts.append(text(x + pw / 2, top_y + 42, "капілярний колапс vs CPD", size=10, color=MUTED))
    parts.append(rect(x + 20, top_y + 160, pw - 40, 60, fill="#dce4ec", stroke=INK, sw=1.5, rx=0))
    parts.append(rect(x + 20, top_y + 152, pw - 40, 8, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=0))
    parts.append(rect(x + 25, top_y + 110, 30, 42, fill="#cfe0f5", stroke=NEG, sw=1.5, rx=1))
    stick_poly = f"M {x+55},{top_y+110} Q {x+110},{top_y+110} {x+140},{top_y+134} L {x+pw-25},{top_y+134} L {x+pw-25},{top_y+152} L {x+140},{top_y+152} Q {x+110},{top_y+128} {x+55},{top_y+128} Z"
    parts.append(f"<path d='{stick_poly}' fill='#fee2e2' stroke='{POS}' stroke-width='1.6'/>")
    parts.append(text(x + pw - 50, top_y + 120, "Прилипання!", size=10, bold=True, color=POS))
    parts.append(text(x + pw - 50, top_y + 144, "F_капілярна", size=9, color=POS))
    box4, _, _ = textbox(x + pw / 2, top_y + 255, "Водне сушіння → прилипання\nПорятунок: надкритичне CO₂\n(CPD) або газоподібний HF", size=10, pad=6, fill="#ffffff")
    parts.append(box4)
    box_foot, _, _ = textbox(W / 2, H - 35, "Вивільнення рухомих деталей вимагає боротьби з капілярним злипанням (стикцією) за допомогою надкритичного сушіння", size=12, pad=10, fill=FILL)
    parts.append(box_foot)
    render("img/surface-micromachining-release.svg", W, H, *parts, title="Поверхнева мікрообробка: нанесення, перфорація, витравлення жертви та загроза стикції")

def fig_wafer_bonding_types():
    W, H = 940, 430
    parts = []
    pw, gap, x0, top_y = 280, 25, 25, 65
    # 1. Anodic
    x1 = x0
    parts.append(rect(x1, top_y, pw, 285, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x1 + pw / 2, top_y + 24, "Анодне з’єднання", size=15, bold=True, color=INK))
    parts.append(text(x1 + pw / 2, top_y + 42, "кремній + боросилікатне скло", size=11, color=MUTED))
    parts.append(rect(x1 + 25, top_y + 65, pw - 50, 45, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=2))
    parts.append(text(x1 + pw / 2, top_y + 92, "Скло Pyrex / Borofloat", size=11, bold=True, color="#0284c7"))
    parts.append(rect(x1 + pw / 2 - 30, top_y + 55, 60, 10, fill="#e2e8f0", stroke=INK, sw=1, rx=1))
    parts.append(text(x1 + pw / 2, top_y + 63, "Катод (−)", size=9, bold=True, color=NEG))
    parts.append(arrow(x1 + 60, top_y + 98, x1 + 60, top_y + 75, color=NEG, sw=1.4))
    parts.append(arrow(x1 + pw - 60, top_y + 98, x1 + pw - 60, top_y + 75, color=NEG, sw=1.4))
    parts.append(text(x1 + pw / 2, top_y + 120, "Міграція Na⁺ → шар збіднення O²⁻", size=9, color=POS))
    parts.append(line(x1 + 25, top_y + 110, x1 + pw - 25, top_y + 110, color=POS, sw=2.5))
    parts.append(rect(x1 + 25, top_y + 110, pw - 50, 45, fill="#dce4ec", stroke=INK, sw=1.5, rx=2))
    parts.append(text(x1 + pw / 2, top_y + 138, "Кремній Si (Анод +)", size=11, bold=True, color=INK))
    box1, _, _ = textbox(x1 + pw / 2, top_y + 215, "T = 300–450 °C, V = 500–1200 В\nЕлектростатичний притиск\nМіцний ковалентний зв’язок Si-O-Si", size=10, pad=8, fill="#ffffff")
    parts.append(box1)
    # 2. Eutectic
    x2 = x0 + pw + gap
    parts.append(rect(x2, top_y, pw, 285, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x2 + pw / 2, top_y + 24, "Евтектичне з’єднання", size=15, bold=True, color=INK))
    parts.append(text(x2 + pw / 2, top_y + 42, "через проміжний сплав Au-Si / Al-Ge", size=11, color=MUTED))
    parts.append(rect(x2 + 25, top_y + 65, pw - 50, 45, fill="#dce4ec", stroke=INK, sw=1.5, rx=2))
    parts.append(text(x2 + pw / 2, top_y + 92, "Кремнієва кришка (Cap)", size=11, bold=True, color=INK))
    parts.append(rect(x2 + 25, top_y + 110, pw - 50, 10, fill="#fef08a", stroke="#ca8a04", sw=1.8, rx=1))
    parts.append(text(x2 + pw / 2, top_y + 118, "Рідка евтектика Au-Si (363 °C)", size=9, bold=True, color="#854d0e"))
    parts.append(rect(x2 + 25, top_y + 120, pw - 50, 45, fill="#dce4ec", stroke=INK, sw=1.5, rx=2))
    parts.append(text(x2 + pw / 2, top_y + 148, "Нижня пластина з MEMS", size=11, bold=True, color=INK))
    box2, _, _ = textbox(x2 + pw / 2, top_y + 215, "Au-Si (363 °C), Al-Ge (419 °C)\nРідка фаза розчиняє оксиди\nГерметичний струмопровідний шов", size=10, pad=8, fill="#ffffff")
    parts.append(box2)
    # 3. Direct Fusion
    x3 = x0 + (pw + gap) * 2
    parts.append(rect(x3, top_y, pw, 285, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(x3 + pw / 2, top_y + 24, "Пряме зрощування (Fusion)", size=15, bold=True, color=INK))
    parts.append(text(x3 + pw / 2, top_y + 42, "атомний контакт Si-Si / Si-SiO₂", size=11, color=MUTED))
    parts.append(rect(x3 + 25, top_y + 65, pw - 50, 45, fill="#dce4ec", stroke=INK, sw=1.5, rx=2))
    parts.append(text(x3 + pw / 2, top_y + 92, "Пластина Si (гідрофільна)", size=11, bold=True, color=INK))
    parts.append(line(x3 + 25, top_y + 110, x3 + pw - 25, top_y + 110, color=FIELD, sw=2.5))
    parts.append(text(x3 + pw / 2, top_y + 104, "Si-OH + HO-Si → Si-O-Si + H₂O", size=9, bold=True, color=FIELD))
    parts.append(rect(x3 + 25, top_y + 110, pw - 50, 45, fill="#dce4ec", stroke=INK, sw=1.5, rx=2))
    parts.append(text(x3 + pw / 2, top_y + 138, "Пластина Si з оксидом SiO₂", size=11, bold=True, color=INK))
    box3, _, _ = textbox(x3 + pw / 2, top_y + 215, "Хімічна активація поверхні\nВодневі зв’язки при кімнатній T\nВисокотемпературний відпал >1000 °C", size=10, pad=8, fill="#ffffff")
    parts.append(box3)
    box_foot, _, _ = textbox(W / 2, H - 35, "З’єднання пластин формує закриті порожнини, захищає структури та дозволяє створювати багатошарові сенсори", size=12, pad=10, fill=FILL)
    parts.append(box_foot)
    render("img/wafer-bonding-types.svg", W, H, *parts, title="Основні технології з’єднання пластин (Wafer Bonding)")

def fig_wafer_level_packaging():
    W, H = 940, 450
    parts = []
    cx = W / 2
    top_y = 65
    parts.append(rect(150, top_y + 10, 640, 70, fill="#cbd5e1", stroke=INK, sw=1.8, rx=4))
    parts.append(text(cx, top_y + 35, "Кремнієва кришка (Cap Wafer)", size=13, bold=True, color=INK))
    parts.append(rect(230, top_y + 60, 480, 110, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=2))
    parts.append(text(cx, top_y + 85, "Герметична вакуумна порожнина (P < 0.01 мбар)", size=12, bold=True, color=NEG))
    parts.append(rect(340, top_y + 60, 260, 10, fill="#fca5a5", stroke=POS, sw=1.5, rx=1))
    parts.append(text(cx, top_y + 55, "Плівковий геттер NEG (Ti-Zr-V поглинає залишковий газ)", size=10, bold=True, color=POS))
    parts.append(rect(180, top_y + 80, 50, 90, fill="#fef08a", stroke="#ca8a04", sw=1.8, rx=2))
    parts.append(text(205, top_y + 130, "Шов", size=10, bold=True, color="#854d0e"))
    parts.append(rect(710, top_y + 80, 50, 90, fill="#fef08a", stroke="#ca8a04", sw=1.8, rx=2))
    parts.append(text(735, top_y + 130, "Шов", size=10, bold=True, color="#854d0e"))
    parts.append(rect(310, top_y + 120, 320, 25, fill="#bbf7d0", stroke=FIELD, sw=1.8, rx=2))
    parts.append(text(cx, top_y + 137, "Рухомий резонансний елемент (висока добротність Q)", size=11, bold=True, color=FIELD))
    parts.append(rect(270, top_y + 115, 40, 35, fill="#cfe0f5", stroke=NEG, sw=1.5, rx=1))
    parts.append(rect(630, top_y + 115, 40, 35, fill="#cfe0f5", stroke=NEG, sw=1.5, rx=1))
    parts.append(rect(150, top_y + 170, 640, 80, fill="#dce4ec", stroke=INK, sw=1.8, rx=4))
    parts.append(text(cx, top_y + 205, "Основна пластина із сенсором (Device Wafer)", size=13, bold=True, color=INK))
    parts.append(rect(240, top_y + 170, 25, 80, fill="#fdba74", stroke="#ea580c", sw=1.5, rx=1))
    parts.append(rect(675, top_y + 170, 25, 80, fill="#fdba74", stroke="#ea580c", sw=1.5, rx=1))
    parts.append(text(252, top_y + 215, "TSV", size=9, bold=True, color="#9a3412"))
    parts.append(text(687, top_y + 215, "TSV", size=9, bold=True, color="#9a3412"))
    parts.append(circle(252, top_y + 265, 12, fill="#94a3b8", stroke=INK, sw=1.5))
    parts.append(circle(687, top_y + 265, 12, fill="#94a3b8", stroke=INK, sw=1.5))
    parts.append(text(cx, top_y + 268, "BGA контакти до друкованої плати", size=11, color=MUTED))
    box_l, _, _ = textbox(160, top_y + 325, "Геттер (NEG)\nАктивується при з’єднанні (350 °C)\nХемосорбує H₂, O₂, CO, N₂\nПідтримує вакуум роками", size=10, pad=8, fill="#ffffff")
    parts.append(box_l)
    box_r, _, _ = textbox(780, top_y + 325, "Герметизація на рівні пластини (WLP)\nЗахищає механіку від розпилювання\nВиведення сигналів через TSV\nМонтаж напряму на плату", size=10, pad=8, fill="#ffffff")
    parts.append(box_r)
    box_foot, _, _ = textbox(cx, H - 30, "Корпусування на рівні пластини (WLP) створює надійну вакуумну капсулу для рухомої мікромеханіки", size=12, pad=10, fill=FILL)
    parts.append(box_foot)
    render("img/wafer-level-packaging.svg", W, H, *parts, title="Вакуумне корпусування MEMS на рівні пластини (Wafer-Level Packaging)")

def main():
    fig_bulk_vs_surface()
    fig_bosch_drie_cycle()
    fig_surface_micromachining_release()
    fig_wafer_bonding_types()
    fig_wafer_level_packaging()
    print("All 5 figures generated successfully.")

if __name__ == "__main__":
    main()
