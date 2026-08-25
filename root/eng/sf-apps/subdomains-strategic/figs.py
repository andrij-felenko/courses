# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_quadrants():
    """Три піддомени за двома осями: цінність для бізнесу (гориз.) і складність предмета (верт.)."""
    W, H = 760, 560
    # Поле осей
    ox, oy = 120, 90          # верхній-лівий кут поля
    ax_w, ax_h = 560, 380     # розмір поля
    bx, by = ox, oy + ax_h    # нижній-лівий (початок осей)

    parts = []
    # Осі зі стрілками
    parts.append(arrow(bx, by, bx + ax_w + 30, by, color=MUTED, sw=1.8))          # X →
    parts.append(arrow(bx, by, bx, oy - 30, color=MUTED, sw=1.8))                  # Y ↑
    # Підписи осей
    parts.append(text(bx + ax_w / 2 + 15, by + 46, "стратегічна цінність для бізнесу →",
                      size=14, color=MUTED, bold=True))
    # Вертикальний підпис осі Y
    parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="14" fill="%s" '
                 'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">'
                 '%s</text>' % (ox - 52, oy + ax_h / 2, FONT, MUTED,
                                ox - 52, oy + ax_h / 2, esc("складність предмета ↑")))

    # Три плитки-піддомени, кожна в своєму місці поля
    # ЯДРО — правий верх (висока цінність, висока складність)
    parts.append(fitbox(bx + 340, oy + 24, 200, 118,
                        "ЯДРО (core)\n\nнаші найкращі люди\nглибокий DDD\nніколи не віддавати",
                        size=14, fill="#fdecea", stroke=POS, sw=2.2, bold=False))
    parts.append(text(bx + 340 + 100, oy + 24 - 10, "перевага + унікальне",
                      size=12, color=POS, bold=True))

    # ДОПОМІЖНЕ — середина (середня цінність, середня складність)
    parts.append(fitbox(bx + 150, oy + 168, 190, 104,
                        "ДОПОМІЖНЕ (supporting)\n\nпишемо самі, в міру\nготового немає",
                        size=13, fill=FILL, stroke=LINE, sw=1.8))
    parts.append(text(bx + 150 + 95, oy + 168 - 10, "потрібне, та не унікальне",
                      size=12, color=MUTED, bold=True))

    # ЗАГАЛЬНЕ — низ, широке по цінності (низька цінність попри будь-яку складність)
    parts.append(fitbox(bx + 24, oy + 300, 210, 96,
                        "ЗАГАЛЬНЕ (generic)\n\nберемо готове\nне пишемо свого",
                        size=13, fill="#eaf0fd", stroke=NEG, sw=1.8))
    parts.append(text(bx + 24 + 105, oy + 300 - 10, "однакове в усіх, вже вирішене",
                      size=12, color=NEG, bold=True))

    render(os.path.join(IMG, 'subdomain-quadrants.svg'), W, H, *parts,
           title="Сорт піддомену — за цінністю, не за складністю коду")


def fig_boundaries():
    """Три сорти піддоменів → різні межі в коді; на стику ядра із загальним — ACL."""
    W, H = 820, 400
    parts = []

    yc = 210          # центр по вертикалі для блоків
    bh = 150          # висота блоків

    # ДОПОМІЖНЕ — ліворуч, звичайна рамка
    sx, sw_ = 40, 190
    parts.append(fitbox(sx, yc - bh / 2, sw_, bh,
                        "ДОПОМІЖНИЙ\nпіддомен\n\nпишемо самі,\nпростіше",
                        size=14, fill=FILL, stroke=LINE, sw=1.6))

    # ЯДРО — центр, товста рамка
    cx, cw = 300, 220
    parts.append(fitbox(cx, yc - bh / 2, cw, bh,
                        "ЯДРО\n\nвласна багата\nмодель,\nсвоя мова",
                        size=15, fill="#fdecea", stroke=POS, sw=3.2))

    # ACL — вузький блок на стику ядра із загальним
    ax, aw = cx + cw + 26, 44
    parts.append(fitbox(ax, yc - bh / 2, aw, bh, "A\nC\nL",
                        size=15, fill="#fff7e6", stroke="#b7791f", sw=1.8, bold=True))
    parts.append(text(ax + aw / 2, yc - bh / 2 - 12, "перекладач",
                      size=12, color="#b7791f", bold=True))

    # ЗАГАЛЬНЕ — праворуч, тонка рамка (пунктир — чуже)
    gx, gw = ax + aw + 26, 200
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="#eaf0fd" '
                 'stroke="%s" stroke-width="1.2" stroke-dasharray="6 4"/>'
                 % (gx, yc - bh / 2, gw, bh, NEG))
    parts.append(mtext(gx + gw / 2, yc - 24,
                       ["ЗАГАЛЬНИЙ", "піддомен", "", "готовий сервіс", "за чужим API"],
                       size=14, color=INK))

    # Стрілка з загального через ACL у ядро — напрямок перекладу «чуже → поняття ядра»
    parts.append(arrow(ax, yc, cx + cw + 2, yc, color="#b7791f", sw=2.0))
    parts.append(arrow(gx - 2, yc, ax + aw + 2, yc, color=NEG, sw=1.6))
    # Підпис напрямку — у вільному просторі під блоками, а не в тісному зазорі
    parts.append(text(W / 2, H - 24,
                      "чужий формат тече в ядро лише через перекладач — уже як поняття ядра",
                      size=13, color=MUTED))

    render(os.path.join(IMG, 'subdomain-boundaries.svg'), W, H, *parts,
           title="Розкрій креслить межі: товсту навколо ядра, тонку над чужим")


def fig_package_tree():
    """Дерево модулів системи перевізника: ядро / допоміжне / загальне за різними межами."""
    W, H = 960, 620
    parts = []

    # Корінь
    root_cx, root_y = W / 2, 70
    parts.append(fitbox(root_cx - 90, root_y, 180, 40, "courier/  (застосунок)",
                        size=14, fill=FILL, stroke=LINE, sw=1.8, bold=True))

    # Три гілки — колонки
    col_y = 180          # верх колонок
    core_x = 320         # ліва межа колонки «ядро»
    supp_x = 40          # ліва межа колонки «допоміжне»
    gen_x = 690          # ліва межа колонки «загальне»

    # Лінії від кореня до заголовків колонок
    for cx in (core_x + 130, supp_x + 95, gen_x + 130):
        parts.append(line(root_cx, root_y + 40, cx, col_y - 8, color=MUTED, sw=1.4))

    # ── ЯДРО: власна багата модель (товста рамка, вкладені файли) ──
    core_w = 260
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="#fdecea" '
                 'stroke="%s" stroke-width="3.0"/>' % (core_x, col_y, core_w, 210, POS))
    parts.append(text(core_x + core_w / 2, col_y + 26, "ЯДРО — routing/", size=15, color=POS, bold=True))
    parts.append(text(core_x + core_w / 2, col_y + 46, "власна багата модель", size=12, color=MUTED))
    core_items = ["domain/Shipment.ts", "domain/Route.ts", "domain/RoutePlanner.ts  (порт)",
                  "app/PlanRoutesService.ts", "infra/OrToolsPlanner.ts  (адаптер+ACL)",
                  "infra/GreedyPlanner.ts  (дублер)"]
    iy = col_y + 70
    for it in core_items:
        parts.append(text(core_x + 16, iy, it, size=12.5, color=INK, anchor="start"))
        iy += 22

    # ── ДОПОМІЖНЕ: звичайна рамка ──
    supp_w = 200
    parts.append(rect(supp_x, col_y, supp_w, 148, fill=FILL, stroke=LINE, sw=1.6, rx=8))
    parts.append(text(supp_x + supp_w / 2, col_y + 26, "ДОПОМІЖНЕ — fleet/", size=13.5, color=INK, bold=True))
    parts.append(text(supp_x + supp_w / 2, col_y + 45, "пишемо самі, простіше", size=11.5, color=MUTED))
    supp_items = ["domain/Vehicle.ts", "app/FleetService.ts", "infra/VehicleRepo.ts"]
    iy = col_y + 72
    for it in supp_items:
        parts.append(text(supp_x + 14, iy, it, size=12.5, color=INK, anchor="start"))
        iy += 22

    # ── ЗАГАЛЬНЕ: тонка пунктирна рамка (чуже) ──
    gen_w = 260
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="#eaf0fd" '
                 'stroke="%s" stroke-width="1.3" stroke-dasharray="6 4"/>'
                 % (gen_x, col_y, gen_w, 210, NEG))
    parts.append(text(gen_x + gen_w / 2, col_y + 26, "ЗАГАЛЬНЕ — за портами", size=13.5, color=NEG, bold=True))
    parts.append(text(gen_x + gen_w / 2, col_y + 45, "тонкий інтерфейс + готове", size=11.5, color=MUTED))
    gen_items = ["notify/EmailSender.ts  (порт)", "notify/SendgridSender.ts", "",
                 "auth/  →  Auth0 (готове)", "search/  →  Elastic (готове)"]
    iy = col_y + 72
    for it in gen_items:
        if it:
            parts.append(text(gen_x + 16, iy, it, size=12.5, color=INK, anchor="start"))
        iy += 22

    # Підпис-легенда під колонками
    parts.append(text(W / 2, H - 26,
                      "товста рамка — своя модель · тонка пунктирна — чуже за портом · порт = інтерфейс на межі",
                      size=12.5, color=MUTED))

    render(os.path.join(IMG, 'courier-package-tree.svg'), W, H, *parts,
           title="Від трьох сортів піддоменів — до дерева пакетів перевізника")


def fig_request_flow():
    """Шлях виклику планування маршрутів крізь шари: сервіс ядра → порти → адаптери/ACL → чуже."""
    W, H = 880, 460
    parts = []

    yb = 120             # верх ряду блоків
    bh = 96
    # Сервіс застосунку ядра
    s_x, s_w = 40, 190
    parts.append(fitbox(s_x, yb, s_w, bh, "PlanRoutesService\n(застосунок ядра)\nмова: Shipment, Route",
                        size=13, fill="#fdecea", stroke=POS, sw=2.6))

    # Порт RoutePlanner (інтерфейс)
    p1_x, p1_w = 300, 150
    parts.append(fitbox(p1_x, yb, p1_w, bh, "порт\nRoutePlanner\n(інтерфейс)",
                        size=13, fill=FILL, stroke=INK, sw=2.0, bold=False))

    # Адаптер + ACL до OR-Tools
    a1_x, a1_w = 520, 160
    parts.append(fitbox(a1_x, yb, a1_w, bh, "OrToolsPlanner\nадаптер + ACL\nперекладає туди й назад",
                        size=12.5, fill="#fff7e6", stroke="#b7791f", sw=2.0))

    # Чужий рушій
    e1_x, e1_w = 730, 120
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="#eaf0fd" '
                 'stroke="%s" stroke-width="1.3" stroke-dasharray="6 4"/>'
                 % (e1_x, yb, e1_w, bh, NEG))
    parts.append(mtext(e1_x + e1_w / 2, yb + bh / 2 - 8,
                       ["OR-Tools", "(готовий", "розв'язувач)"], size=12.5, color=INK))

    # Стрілки ряду
    parts.append(arrow(s_x + s_w + 4, yb + bh / 2, p1_x - 4, yb + bh / 2, color=INK, sw=1.8))
    parts.append(arrow(p1_x + p1_w + 4, yb + bh / 2, a1_x - 4, yb + bh / 2, color="#b7791f", sw=1.8))
    parts.append(arrow(a1_x + a1_w + 4, yb + bh / 2, e1_x - 4, yb + bh / 2, color=NEG, sw=1.6))

    # Підписи над стрілками
    parts.append(text((s_x + s_w + p1_x) / 2 + 2, yb - 10, "кличе інтерфейс", size=11.5, color=MUTED))
    parts.append(text((a1_x + a1_w + e1_x) / 2, yb - 10, "чужий формат", size=11.5, color=MUTED))

    # Друга гілка того самого порту — тестовий дублер (нижче)
    yb2 = yb + bh + 70
    a2_x, a2_w = 520, 160
    parts.append(fitbox(a2_x, yb2, a2_w, bh, "GreedyPlanner\nпростий дублер\nдля тестів / дешевого тарифу",
                        size=12, fill=FILL, stroke=LINE, sw=1.6))
    # Пунктир від порту вниз до дублера
    parts.append(line(p1_x + p1_w / 2, yb + bh, p1_x + p1_w / 2, yb2 + bh / 2, color=MUTED, sw=1.4, dash="5 4"))
    parts.append(arrow(p1_x + p1_w / 2, yb2 + bh / 2, a2_x - 4, yb2 + bh / 2, color=MUTED, sw=1.4))
    parts.append(text(p1_x + p1_w / 2 + 92, yb2 - 12, "той самий порт — інша реалізація", size=11.5, color=MUTED))

    # Вертикальна пунктирна межа «своє | чуже» між портом і адаптером
    div_x = (p1_x + p1_w + a1_x) / 2
    parts.append(line(div_x, yb - 34, div_x, yb2 + bh + 14, color=MUTED, sw=1.2, dash="4 5"))
    parts.append(text(div_x - 60, yb - 44, "своє (ядро)", size=11.5, color=POS, bold=True, anchor="middle"))
    parts.append(text(div_x + 70, yb - 44, "межа зі світом", size=11.5, color=NEG, bold=True, anchor="middle"))

    parts.append(text(W / 2, H - 20,
                      "ядро знає лише порт; чуже живе за адаптером; ACL пускає всередину тільки поняття ядра",
                      size=12.5, color=MUTED))

    render(os.path.join(IMG, 'courier-request-flow.svg'), W, H, *parts,
           title="Виклик планувальника: ядро → порт → адаптер/ACL → чужий рушій")


def fig_lineage():
    """Дистиляція визріває у два кроки: Еванс (два названі полюси + безіменна
    сіра зона) → Вернон (три симетрично названі сорти). Стрілка «доназвано середній»."""
    W, H = 920, 470
    parts = []

    # Дві панелі: ліворуч Еванс-2003, праворуч Вернон-2013/2016.
    # Широкий зазор (160px) між панелями — щоб підпис стрілки «середній член» стояв вільно.
    lx = 40           # ліва панель, лівий край
    pw = 340          # ширина панелі
    rx = 540          # права панель, лівий край (зазор 380→540)
    ptop = 96         # верх панелей
    ph = 320          # висота панелей

    # Рамки-панелі
    parts.append(rect(lx, ptop, pw, ph, fill=BG, stroke=MUTED, sw=1.4, rx=10))
    parts.append(rect(rx, ptop, pw, ph, fill=BG, stroke=MUTED, sw=1.4, rx=10))

    # Заголовки панелей (над рамками, з запасом)
    parts.append(text(lx + pw / 2, ptop - 34, "Еванс · 2003 · «синя книжка»",
                      size=15, color=INK, bold=True))
    parts.append(text(lx + pw / 2, ptop - 14,
                      "Частина IV · розділ 15 «Distillation»", size=12, color=MUTED))
    parts.append(text(rx + pw / 2, ptop - 34, "Вернон · 2013 і 2016",
                      size=15, color=INK, bold=True))
    parts.append(text(rx + pw / 2, ptop - 14,
                      "«Implementing DDD» · «DDD Distilled»", size=12, color=MUTED))

    cell_w = pw - 48
    # ── Ліва панель: два названі полюси + безіменна сіра зона ──────────────
    cx_l = lx + 24
    parts.append(fitbox(cx_l, ptop + 26, cell_w, 74,
                        "ЯДРОВА ОБЛАСТЬ (core domain)\nнайцінніша фракція — у неї найкращі сили",
                        size=13, fill="#fdecea", stroke=POS, sw=2.2))
    # середина: безіменна сіра зона (пунктир, приглушено)
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="#f0f1f3" '
                 'stroke="%s" stroke-width="1.4" stroke-dasharray="5 4"/>'
                 % (cx_l, ptop + 118, cell_w, 74, MUTED))
    parts.append(mtext(cx_l + cell_w / 2, ptop + 148,
                       ["сіра зона без власного імені", "(«і не ядро, і не готове»)"],
                       size=13, color=MUTED))
    parts.append(fitbox(cx_l, ptop + 210, cell_w, 74,
                        "ЗАГАЛЬНІ ПІДДОМЕНИ (generic)\nвідкинута фракція — беремо готове",
                        size=13, fill="#eaf0fd", stroke=NEG, sw=2.2))

    # ── Права панель: три симетрично названі сорти ────────────────────────
    cx_r = rx + 24
    parts.append(fitbox(cx_r, ptop + 26, cell_w, 74,
                        "ЯДРОВИЙ (core)\nунікальне — найкращі сили",
                        size=13, fill="#fdecea", stroke=POS, sw=2.2))
    parts.append(fitbox(cx_r, ptop + 118, cell_w, 74,
                        "ДОПОМІЖНИЙ (supporting)\nне ядро й не загальне — пишемо самі",
                        size=13, fill=FILL, stroke=LINE, sw=2.0))
    parts.append(fitbox(cx_r, ptop + 210, cell_w, 74,
                        "ЗАГАЛЬНИЙ (generic)\nвже вирішене — купуємо",
                        size=13, fill="#eaf0fd", stroke=NEG, sw=2.2))

    # ── Стрілка «доназвано середній член»: від сірої зони до «допоміжне» ──
    y_mid = ptop + 118 + 37
    parts.append(arrow(lx + pw + 6, y_mid, rx - 6, y_mid, color="#b7791f", sw=2.4))
    parts.append(text((lx + pw + rx) / 2, y_mid - 16, "доназвано",
                      size=13, color="#b7791f", bold=True))
    parts.append(text((lx + pw + rx) / 2, y_mid + 24, "середній член",
                      size=13, color="#b7791f", bold=True))

    # Підпис-висновок унизу, у вільному просторі
    parts.append(text(W / 2, H - 20,
                      "ідея «відділити ядро» — від Еванса; чиста тріада з трьох імен — від наступників",
                      size=13, color=MUTED))

    render(os.path.join(IMG, 'distillation-lineage.svg'), W, H, *parts,
           title="Дистиляція визріває у два кроки: два полюси → три названі сорти")


if __name__ == '__main__':
    fig_quadrants()
    fig_boundaries()
    fig_package_tree()
    fig_request_flow()
    fig_lineage()
    print("figs done")
