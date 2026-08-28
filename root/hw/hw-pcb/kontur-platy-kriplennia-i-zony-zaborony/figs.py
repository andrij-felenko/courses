# -*- coding: utf-8 -*-
"""Фігури для теми kontur-platy-kriplennia-i-zony-zaborony (контур плати, кріплення й зони заборони).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова гама
COPPER      = "#b5763a"
COPPER_FILL = "#fdf3e7"
BOARD_EDGE  = "#1e293b"
BOARD_BG    = "#f1f5f9"
KEEPOUT_CMP = "#ef4444"  # Червоний: Component Keepout
KEEPOUT_RT  = "#d97706"  # Помаранчевий: Route Keepout
KEEPOUT_CU  = "#8b5cf6"  # Фіолетовий: Copper Keepout
RAIL_COL    = "#64748b"  # Сірий: конвеєр / рейки
TOOL_COL    = "#0ea5e9"  # Блакитний: інструмент / фреза


# ── 1. Контур плати та різновиди зон заборони (Keepout Zones) ──────────────────
def fig_board_outline_keepouts():
    W, H = 860, 560
    frags = []

    # Тло креслення
    frags.append(rect(10, 10, 840, 540, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(430, 32, "Контур плати (Edge.Cuts) та розподіл механічних і топологічних зон заборони",
                      size=13, color=INK, bold=True))

    # Контур плати (Edge.Cuts)
    bx, by, bw, bh = 30, 55, 530, 380
    frags.append(rect(bx, by, bw, bh, fill=BOARD_BG, stroke=BOARD_EDGE, sw=2.2, rx=8))
    frags.append(text(bx + 85, by + 36, "Друкована плата (FR-4)", size=11, color="#475569", bold=True))

    # Внутрішній фрезерований паз / виріз (Internal Cutout / Slot)
    sx, sy, sw_cut, sh_cut = bx + 200, by + 190, 95, 55
    frags.append(rect(sx, sy, sw_cut, sh_cut, fill="#ffffff", stroke=BOARD_EDGE, sw=2.0, rx=6))
    frags.append(text(sx + 47, sy + 24, "Виріз у платі", size=10, color=BOARD_EDGE, bold=True))
    frags.append(text(sx + 47, sy + 40, "R_кута >= 1.0 мм", size=9, color=MUTED))

    # 1.1 Конвеєрні технологічні поля (SMT Rail Keepout) по верхньому і нижньому краю
    frags.append(rect(bx, by, bw, 22, fill="#fee2e2", stroke=KEEPOUT_CMP, sw=1.2, rx=0))
    frags.append(text(bx + bw/2, by + 15, "Технологічне поле конвеєра SMT (Rail Keepout 4.0 мм)", size=10, color=KEEPOUT_CMP, bold=True))

    frags.append(rect(bx, by + bh - 22, bw, 22, fill="#fee2e2", stroke=KEEPOUT_CMP, sw=1.2, rx=0))
    frags.append(text(bx + bw/2, by + bh - 8, "Нижня зона затискачів автоматичної лінії (Rail Keepout 4.0 мм)", size=10, color=KEEPOUT_CMP, bold=True))

    # 1.2 Кріпильний отвір з зоною заборони компонентів і міді (Mounting Hole & Keepout)
    hx, hy = bx + 45, by + 75
    frags.append(circle(hx, hy, 28, fill="#fef2f2", stroke=KEEPOUT_CMP, sw=1.2))
    frags.append(circle(hx, hy, 18, fill="#f3e8ff", stroke=KEEPOUT_CU, sw=1.2))
    frags.append(circle(hx, hy, 12, fill="#e2e8f0", stroke="#475569", sw=1.5))
    frags.append(circle(hx, hy, 6, fill="#ffffff", stroke=BOARD_EDGE, sw=1.5))
    frags.append(text(hx, hy + 3, "M3", size=9, color=BOARD_EDGE, bold=True))

    frags.append(line(hx + 22, hy - 18, hx + 55, hy - 25, color=KEEPOUT_CMP, sw=1.0))
    frags.append(text(hx + 105, hy - 25, "Зона головки гвинта", size=9, color=KEEPOUT_CMP, bold=True))

    # 1.3 Зона радіатора (Heatsink & Route Keepout)
    hs_x, hs_y, hs_w, hs_h = bx + 190, by + 50, 115, 95
    frags.append(rect(hs_x, hs_y, hs_w, hs_h, fill="#fffbeb", stroke=KEEPOUT_RT, sw=1.5, rx=3))
    # Ребра радіатора у верхній третині, щоб не перетинати напис
    for rx_pos in range(hs_x + 10, hs_x + hs_w - 5, 14):
        frags.append(line(rx_pos, hs_y + 6, rx_pos, hs_y + 26, color="#d97706", sw=1.8))
    frags.append(text(hs_x + hs_w/2, hs_y + 44, "Радіатор TO-220", size=10, color="#b45309", bold=True))
    frags.append(text(hs_x + hs_w/2, hs_y + 62, "Route Keepout", size=10, color=KEEPOUT_RT, bold=True))
    frags.append(text(hs_x + hs_w/2, hs_y + 78, "(ризик стирання маски)", size=9, color=MUTED))

    # 1.4 Зона котушки індуктивності (Power Inductor & Copper Keepout)
    ind_x, ind_y, ind_w, ind_h = bx + 35, by + 190, 120, 85
    frags.append(rect(ind_x, ind_y, ind_w, ind_h, fill="#f5f3ff", stroke=KEEPOUT_CU, sw=1.5, rx=4))
    # Символ котушки/сердечника
    frags.append(circle(ind_x + ind_w/2, ind_y + 24, 14, fill="#ddd6fe", stroke=KEEPOUT_CU, sw=1.2))
    frags.append(text(ind_x + ind_w/2, ind_y + 27, "L1", size=10, color=KEEPOUT_CU, bold=True))
    frags.append(text(ind_x + ind_w/2, ind_y + 54, "Copper Keepout", size=10, color=KEEPOUT_CU, bold=True))
    frags.append(text(ind_x + ind_w/2, ind_y + 70, "(струми Фуко й ЕРС)", size=9, color=MUTED))

    # 1.5 Зона друкованої антени (RF Antenna Keepout)
    ant_x, ant_y, ant_w, ant_h = bx + 380, by + 45, 125, 120
    frags.append(rect(ant_x, ant_y, ant_w, ant_h, fill="#fdf4ff", stroke="#c026d3", sw=1.5, rx=3))
    # Зигзаг / меандр антени
    frags.append(line(ant_x + 20, ant_y + 70, ant_x + 20, ant_y + 20, color=COPPER, sw=2.2))
    frags.append(line(ant_x + 20, ant_y + 20, ant_x + 45, ant_y + 20, color=COPPER, sw=2.2))
    frags.append(line(ant_x + 45, ant_y + 20, ant_x + 45, ant_y + 60, color=COPPER, sw=2.2))
    frags.append(line(ant_x + 45, ant_y + 60, ant_x + 70, ant_y + 60, color=COPPER, sw=2.2))
    frags.append(line(ant_x + 70, ant_y + 60, ant_x + 70, ant_y + 20, color=COPPER, sw=2.2))
    frags.append(line(ant_x + 70, ant_y + 20, ant_x + 105, ant_y + 20, color=COPPER, sw=2.2))
    frags.append(text(ant_x + ant_w/2, ant_y + 88, "2.4 GHz антена", size=10, color="#a21caf", bold=True))
    frags.append(text(ant_x + ant_w/2, ant_y + 104, "All-Layer Keepout", size=9, color="#a21caf"))

    # 1.6 Внутрішній кут: Dogbone (кісточка) фрезерування
    dbg_x, dbg_y, dbg_w, dbg_h = bx + 365, by + 230, 140, 100
    frags.append(rect(dbg_x, dbg_y, dbg_w, dbg_h, fill="#e0f2fe", stroke=TOOL_COL, sw=1.5, rx=2))
    # Прямокутний виріз всередині
    frags.append(rect(dbg_x + 20, dbg_y + 20, 60, 75, fill=BOARD_BG, stroke=BOARD_EDGE, sw=1.5))
    # Свердління у кутку для прямокутної посадки
    frags.append(circle(dbg_x + 20, dbg_y + 20, 8, fill="#bae6fd", stroke=TOOL_COL, sw=1.5))
    frags.append(text(dbg_x + 85, dbg_y + 45, "Dogbone", size=10, color="#0369a1", bold=True))
    frags.append(text(dbg_x + 85, dbg_y + 62, "розвантаження", size=9, color=MUTED))
    frags.append(text(dbg_x + 85, dbg_y + 76, "кута плати", size=9, color=MUTED))

    # Права панель: Легенда та правила
    lx, ly = 580, 55
    frags.append(rect(lx, ly, 250, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(lx + 125, ly + 25, "Класифікація Keepout", size=12, color=INK, bold=True))

    items = [
        ("Component Keepout", "Червона зона: заборона деталей біля країв, гвинтів та високої напруги.", KEEPOUT_CMP, "#fee2e2"),
        ("Route Keepout", "Помаранчева зона: заборона сигналів під радіаторами, реле та антенами.", KEEPOUT_RT, "#fffbeb"),
        ("Copper Keepout", "Фіолетова зона: повна вирізка міді під дроселями, трансформаторами й антенами.", KEEPOUT_CU, "#f5f3ff"),
        ("Mechanical / Dogbone", "Блакитна зона: радіуси фрези R >= 1.0 мм та кутові отвори під прямий кут.", TOOL_COL, "#e0f2fe")
    ]

    cur_y = ly + 40
    for title_it, desc_it, border_c, bg_c in items:
        frags.append(rect(lx + 10, cur_y, 230, 74, fill=bg_c, stroke=border_c, sw=1.0, rx=4))
        frags.append(text(lx + 18, cur_y + 18, title_it, size=10, color=border_c, bold=True, anchor="start"))
        lines = [desc_it[:35], desc_it[35:70], desc_it[70:]] if len(desc_it) > 35 else [desc_it]
        lines = [ln.strip() for ln in lines if ln.strip()]
        frags.append(mtext(lx + 18, cur_y + 34, lines, size=9, color="#334155", anchor="start", lh=1.3))
        cur_y += 82

    # Інженерна примітка внизу
    b_bot, _, _ = textbox(430, 495,
                          ["Контур плати в шарі Edge.Cuts є замкненим геометричним полігоном із номінальною товщиною лінії.",
                           "Порушення меж Keepout призводить до механічного пошкодження приладу, здирання маски або зриву ВЧ-узгодження."],
                          size=10, fill="#f0fdf4", stroke=FIELD, pad=6)
    frags.append(b_bot)

    render(os.path.join(OUT, "board-outline-keepouts.svg"), W, H, *frags,
           title="Типи зон заборони (Keepout) на контурі друкованої плати")


# ── 2. Панелізація та методи розділення: V-Score проти Mouse Bites ──────────────
def fig_panelization_depaneling():
    W, H = 860, 530
    frags = []

    frags.append(rect(10, 10, 840, 510, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(430, 32, "Механіка панелізації: скрайбування (V-Score) та перфораційні перемички (Mouse Bites)",
                      size=13, color=INK, bold=True))

    # ── Ліва колонка: V-Score (Скрайбування) ──
    x0, y0 = 30, 55
    w_col = 385
    frags.append(rect(x0, y0, w_col, 400, fill="#fafaf9", stroke="#d6d3d1", sw=1.2, rx=6))
    frags.append(text(x0 + w_col/2, y0 + 24, "1. Скрайбування (V-Score Cut)", size=12, color=POS, bold=True))

    # Переріз плати зі скрайбувальними канавками
    py = y0 + 45
    # Верхня і нижня плати (переріз FR-4)
    frags.append(rect(x0 + 30, py + 20, 130, 60, fill="#e7e5e4", stroke="#78716c", sw=1.5))
    frags.append(rect(x0 + 225, py + 20, 130, 60, fill="#e7e5e4", stroke="#78716c", sw=1.5))

    # Залишковий перешийок (Web) посередині
    frags.append(rect(x0 + 160, py + 38, 65, 24, fill="#a8a29e", stroke="#57534e", sw=1.2))

    # Ножі скрайбера (V-подібні леза зверху і знизу)
    frags.append(line(x0 + 160, py + 20, x0 + 192, py + 38, color=POS, sw=1.8))
    frags.append(line(x0 + 225, py + 20, x0 + 192, py + 38, color=POS, sw=1.8))
    frags.append(line(x0 + 160, py + 80, x0 + 192, py + 62, color=POS, sw=1.8))
    frags.append(line(x0 + 225, py + 80, x0 + 192, py + 62, color=POS, sw=1.8))

    frags.append(text(x0 + 95, py + 55, "Плата A", size=10, color=INK, bold=True))
    frags.append(text(x0 + 290, py + 55, "Плата B", size=10, color=INK, bold=True))

    # Розмірні написи кута і товщини перешийка
    frags.append(text(x0 + 192, py + 12, "Кут 30°..45°", size=9, color=POS, bold=True))
    frags.append(text(x0 + 192, py + 53, "t = T/3", size=9, color="#ffffff", bold=True))

    # Деформація та тріщини в MLCC при ламанні
    my = py + 95
    frags.append(rect(x0 + 15, my, w_col - 30, 245, fill="#ffffff", stroke="#e7e5e4", sw=1.0, rx=4))
    frags.append(text(x0 + w_col/2, my + 20, "Механічне напруження керамічних конденсаторів (MLCC)", size=10, color="#991b1b", bold=True))

    # Погана орієнтація MLCC (перпендикулярно до лінії зламу)
    frags.append(line(x0 + 35, my + 45, x0 + 35, my + 130, color=POS, sw=2.0, dash="4,3"))
    frags.append(text(x0 + 35, my + 38, "V-Score", size=9, color=POS, bold=True))

    # Конденсатор перпендикулярно
    frags.append(rect(x0 + 55, my + 60, 48, 22, fill="#fca5a5", stroke=POS, sw=1.5, rx=2))
    frags.append(text(x0 + 79, my + 75, "MLCC", size=9, color="#7f1d1d", bold=True))
    frags.append(text(x0 + 79, my + 100, "НЕБЕЗПЕЧНО", size=9, color=POS, bold=True))
    frags.append(text(x0 + 79, my + 115, "Згин ламає кристал", size=9, color=MUTED))

    # Безпечна орієнтація MLCC (паралельно і на відстані >= 3.0 мм)
    frags.append(rect(x0 + 165, my + 55, 22, 48, fill="#bbf7d0", stroke=FIELD, sw=1.5, rx=2))
    frags.append(text(x0 + 176, my + 82, "MLCC", size=9, color="#14532d", bold=True))
    frags.append(text(x0 + 265, my + 72, "БЕЗПЕЧНО: d >= 3.0 мм", size=9, color=FIELD, bold=True))
    frags.append(text(x0 + 265, my + 90, "Орієнтація вздовж лінії", size=9, color="#166534"))

    frags.append(mtext(x0 + w_col/2, my + 170,
                       ["V-Score застосовується лише для прямих наскрізних ліній від краю до краю.",
                        "Залишковий перешийок: 0.45..0.55 мм для плати 1.6 мм.",
                        "Депанелізація згинанням створює критичні розтягуючі деформації."],
                       size=9, color="#44403c", lh=1.35))

    # ── Права колонка: Mouse Bites (Перфораційні перемички) ──
    x1 = 445
    frags.append(rect(x1, y0, w_col, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(x1 + w_col/2, y0 + 24, "2. Перфорація (Mouse Bites / Break-Tabs)", size=12, color=TOOL_COL, bold=True))

    # Топологія перемички Mouse Bites з фрезерованим пазом
    mb_y = y0 + 45
    frags.append(rect(x1 + 15, mb_y, w_col - 30, 160, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=4))

    # Тіло плати (зліва) та технологічна рамка панелі (справа)
    frags.append(rect(x1 + 30, mb_y + 15, 105, 130, fill=BOARD_BG, stroke=BOARD_EDGE, sw=1.5))
    frags.append(text(x1 + 82, mb_y + 80, "Плата", size=11, color=INK, bold=True))

    frags.append(rect(x1 + 240, mb_y + 15, 105, 130, fill="#e2e8f0", stroke="#64748b", sw=1.5))
    frags.append(text(x1 + 292, mb_y + 80, "Рамка панелі", size=10, color=MUTED, bold=True))

    # Фрезерований паз між ними (Routing Channel шириною 2.0 мм)
    frags.append(rect(x1 + 135, mb_y + 15, 105, 40, fill="#f1f5f9", stroke="#94a3b8", sw=1.0))
    frags.append(rect(x1 + 135, mb_y + 105, 105, 40, fill="#f1f5f9", stroke="#94a3b8", sw=1.0))
    frags.append(text(x1 + 187, mb_y + 38, "Паз фрези 2.0 мм", size=9, color="#64748b"))
    frags.append(text(x1 + 187, mb_y + 128, "Паз фрези 2.0 мм", size=9, color="#64748b"))

    # Тіло самої перемички (Tab завширшки 4.0 мм)
    frags.append(rect(x1 + 135, mb_y + 55, 105, 50, fill=BOARD_BG, stroke=BOARD_EDGE, sw=1.5))

    # Отвори перфорації (Mouse Bites), втоплені всередину контуру плати
    hole_x = x1 + 132
    for dy_h in [61, 73, 85, 97]:
        frags.append(circle(hole_x, mb_y + dy_h, 3.5, fill="#ffffff", stroke="#0f172a", sw=1.2))
    frags.append(line(hole_x, mb_y + 55, hole_x, mb_y + 105, color=POS, sw=1.2, dash="2,2"))

    frags.append(text(x1 + 187, mb_y + 75, "Перемичка 4.0 мм", size=9, color=TOOL_COL, bold=True))
    frags.append(text(x1 + 187, mb_y + 90, "5 отворів d=0.6 мм", size=9, color=MUTED))

    # Пояснення втопленого контуру (Захист від виступаючих задирок)
    by_info = mb_y + 175
    frags.append(rect(x1 + 15, by_info, w_col - 30, 160, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=4))
    frags.append(text(x1 + w_col/2, by_info + 20, "Втоплена перфорація (Recessed Mouse Bites)", size=10, color=TOOL_COL, bold=True))

    frags.append(mtext(x1 + w_col/2, by_info + 48,
                       ["При виламуванні склотекстоліт утворює гострі задирки (burrs).",
                        "Зміщення лінії перфорації на 0.3..0.5 мм всередину контуру",
                        "гарантує, що зламаний край не виступатиме за габарит плати",
                        "і не заклинить плату під час монтажу у корпус."],
                       size=9, color="#334155", lh=1.4))

    # Загальний підсумок знизу
    b_bot, _, _ = textbox(430, 485,
                          ["V-Score забезпечує швидке та жорстке розділення прямокутних плат, але вимагає захисту компонентів від згину.",
                           "Mouse Bites дозволяють формувати довільні криволінійні контури та складні вирізи з мінімальним ударним навантаженням."],
                          size=9.5, fill="#f0fdf4", stroke=FIELD, pad=6)
    frags.append(b_bot)

    render(os.path.join(OUT, "panelization-depaneling.svg"), W, H, *frags,
           title="Порівняння методів розділення панелей: V-Score проти Mouse Bites")


def main():
    fig_board_outline_keepouts()
    fig_panelization_depaneling()
    print("Всі фігури для kontur-platy-kriplennia-i-zony-zaborony згенеровано успішно.")


if __name__ == "__main__":
    main()
