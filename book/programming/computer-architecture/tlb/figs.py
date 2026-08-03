# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── translate: віртуальна адреса → таблиця в RAM → фізична ─────────────────────
# Ідея: адреса ділиться на номер сторінки (VPN) + зсув; VPN індексує таблицю
# сторінок у ПОВІЛЬНІЙ RAM, звідти беремо номер фрейму (PPN); зсув переходить
# без змін. Головна думка: сам переклад коштує звернення в пам'ять.

def fig_translate():
    W, H = 740, 360
    p = []
    y0 = 90
    cw = 44

    # віртуальна адреса
    p.append(text(60, y0 - 14, "віртуальна адреса", size=11.5, color=INK, bold=True, anchor="start"))
    for i in range(8):
        x = 60 + i * cw
        vpn = (i < 5)
        p.append(rect(x, y0, cw - 4, 34, fill=("#eef4ff" if vpn else "#eafaf0"),
                      stroke=(NEG if vpn else FIELD), sw=1.4, rx=3))
    p.append(text(60 + 2.5 * cw, y0 + 54, "номер сторінки (VPN)", size=10, color=NEG, anchor="middle", bold=True))
    p.append(text(60 + 6.5 * cw, y0 + 54, "зсув", size=10, color=FIELD, anchor="middle", bold=True))

    # таблиця сторінок у RAM
    tx, ty = 250, 175
    p.append(rect(tx - 12, ty - 20, 200, 150, fill="#fdf4f4", stroke=INK, sw=1.4, rx=8))
    p.append(text(tx + 88, ty - 2, "таблиця сторінок", size=11, color=INK, bold=True))
    p.append(text(tx + 88, ty + 12, "(у повільній RAM)", size=9, color=MUTED))
    rows = ["VPN 0 → фрейм 7", "VPN 1 → фрейм 3", "VPN 2 → фрейм 9", "…"]
    for k, r in enumerate(rows):
        yy = ty + 30 + k * 22
        hot = (k == 2)
        p.append(rect(tx, yy, 176, 19, fill=("#fde9e7" if hot else FILL),
                      stroke=(POS if hot else LINE), sw=(1.6 if hot else 0.9), rx=3))
        p.append(text(tx + 88, yy + 14, r, size=9.5, color=INK))

    # VPN → таблиця
    p.append(arrow(60 + 2.5 * cw, y0 + 36, tx + 88, ty - 22, color=NEG, sw=1.8))
    p.append(text(60 + 2.5 * cw + 40, y0 + 92, "індексує", size=9, color=NEG, anchor="middle"))

    # фізична адреса
    px, py = 505, y0
    fw = 28
    p.append(text(px, py - 14, "фізична адреса", size=11.5, color=INK, bold=True, anchor="start"))
    for i in range(8):
        x = px + i * fw
        ppn = (i < 5)
        p.append(rect(x, py, fw - 3, 34, fill=("#fde9e7" if ppn else "#eafaf0"),
                      stroke=(POS if ppn else FIELD), sw=1.4, rx=3))
    p.append(text(px + 2.5 * fw, py + 54, "номер фрейму (PPN)", size=10, color=POS, anchor="middle", bold=True))
    p.append(text(px + 6.5 * fw, py + 54, "зсув", size=10, color=FIELD, anchor="middle", bold=True))

    # таблиця → PPN
    p.append(arrow(tx + 176, ty + 30 + 2 * 22 + 9, px + 2.5 * fw, py + 36, color=POS, sw=1.8))

    # зсув переходить без змін
    p.append(arrow(60 + 6.5 * cw, y0 + 36, px + 6.5 * fw, py + 36, color=FIELD, sw=1.6))
    p.append(text((60 + 6.5 * cw + px + 6.5 * fw) / 2, y0 + 150, "зсув — без змін", size=9.5, color=FIELD, anchor="middle"))

    render(os.path.join(OUT, "translate.svg"), W, H, *p,
           title="Переклад адреси: номер сторінки шукаємо в таблиці, зсув лишаємо")


# ── walk: влучання в TLB проти проходу по таблиці ─────────────────────────────
# Ідея: два шляхи для однієї адреси. Влучання — коротка стрілка ядро→TLB→готово.
# Промах — довгий похід ядро→кілька рівнів таблиці в RAM→назад. Контраст ціни.

def fig_walk():
    W, H = 740, 400
    p = []

    # ядро
    p.append(rect(40, 170, 90, 60, fill="#eafaf0", stroke=INK, sw=1.8))
    p.append(text(85, 196, "ядро", size=13, color=INK, bold=True))
    p.append(text(85, 214, "потрібна адреса", size=9, color=MUTED))

    # TLB
    tx, ty = 210, 90
    p.append(rect(tx, ty, 150, 70, fill="#eef4ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(tx + 75, ty + 26, "TLB", size=14, color=NEG, bold=True))
    p.append(text(tx + 75, ty + 44, "кеш перекладів", size=9.5, color=INK))
    p.append(text(tx + 75, ty + 58, "~1 такт", size=9, color=FIELD, bold=True))

    # влучання: ядро → TLB → готово
    p.append(arrow(133, 185, tx - 6, ty + 55, color=FIELD, sw=2.2))
    p.append(text(150, 150, "влучання: ~1 такт", size=11, color=FIELD, anchor="start", bold=True))
    p.append(arrow(tx + 150 + 6, ty + 35, tx + 240, ty + 35, color=FIELD, sw=2.0))
    p.append(text(tx + 245, ty + 32, "фізична адреса —", size=10, color=INK, anchor="start"))
    p.append(text(tx + 245, ty + 46, "далі до кешу/пам'яті", size=9, color=MUTED, anchor="start"))

    # прохід по таблиці (miss): кілька рівнів у RAM
    wx, wy = 210, 250
    p.append(text(wx - 6, wy - 14, "промах → прохід по таблиці (page walk):", size=11,
                  color=POS, anchor="start", bold=True))
    levels = ["рівень 1", "рівень 2", "рівень 3", "рівень 4"]
    bw = 108
    for k, lv in enumerate(levels):
        x = wx + k * (bw + 12)
        p.append(rect(x, wy, bw, 46, fill="#fdf4f4", stroke=POS, sw=1.4, rx=6))
        p.append(text(x + bw / 2, wy + 20, lv, size=10, color=INK, bold=True))
        p.append(text(x + bw / 2, wy + 36, "читання RAM", size=9, color=MUTED))
        if k < len(levels) - 1:
            p.append(arrow(x + bw + 2, wy + 23, x + bw + 10, wy + 23, color=POS, sw=1.8))
    # ядро → walk
    p.append(arrow(85, 232, wx + 20, wy - 4, color=POS, sw=1.6))
    p.append(text(wx + 2 * (bw + 12), wy + 66, "кожен рівень — окреме звернення в повільну RAM → десятки тактів",
                  size=9.5, color=INK, anchor="middle"))
    # результат промаху кладеться в TLB
    p.append(arrow(wx + 3 * (bw + 12) + bw / 2, wy - 4, tx + 100, ty + 70 + 4, color=MUTED, sw=1.4))
    p.append(text(tx + 175, ty + 92, "знайдений переклад осідає в TLB", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "walk.svg"), W, H, *p,
           title="Влучання в TLB — один такт; промах — похід по таблиці на десятки тактів")


# ── entry: будова запису TLB і асоціативний пошук ─────────────────────────────
# Ідея: TLB — маленька таблиця, кожен запис = тег(VPN)+PPN+прапорці+ASID.
# Пошук — паралельне порівняння тега з усіма записами водночас (асоціативність).

def fig_entry():
    W, H = 740, 380
    p = []

    # запит: VPN
    p.append(rect(60, 60, 120, 40, fill="#eef4ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(120, 78, "шуканий VPN", size=10.5, color=INK, bold=True))
    p.append(text(120, 94, "+ ASID", size=9, color=MUTED))

    # набір записів TLB
    ex, ey = 260, 70
    rowh = 40
    cols = [("VPN (тег)", 92, "#eef4ff", NEG),
            ("PPN (фрейм)", 96, "#fde9e7", POS),
            ("прапорці", 84, "#eafaf0", FIELD),
            ("ASID", 60, "#f0f1f3", MUTED)]
    # заголовки
    cx = ex
    for name, w, fill, col in cols:
        p.append(text(cx + w / 2, ey - 10, name, size=9.5, color=col, bold=True))
        cx += w + 6
    # рядки
    for r in range(4):
        cx = ex
        y = ey + r * (rowh + 4)
        hot = (r == 1)
        for name, w, fill, col in cols:
            p.append(rect(cx, y, w, rowh, fill=(fill if not hot else fill),
                          stroke=(INK if hot else LINE), sw=(2.0 if hot else 0.9), rx=4))
            cx += w + 6
        if hot:
            p.append(text(ex + (92 + 96 + 84 + 60 + 3 * 6) + 14, y + 25, "збіг!", size=11,
                          color=INK, bold=True, anchor="start"))

    # стрілки паралельного порівняння: запит до кожного рядка одночасно
    for r in range(4):
        y = ey + r * (rowh + 4) + rowh / 2
        p.append(arrow(182, 82, ex - 6, y, color=NEG, sw=1.2))
    p.append(text(120, 130, "порівняти", size=9.5, color=NEG, anchor="middle"))
    p.append(text(120, 144, "з усіма", size=9.5, color=NEG, anchor="middle"))
    p.append(text(120, 158, "водночас", size=9.5, color=NEG, anchor="middle"))

    # пояснення знизу
    b = fitbox(ex, ey + 4 * (rowh + 4) + 16, 400, 56,
               "Записів мало (десятки) — тож усі теги можна порівняти з запитом за один такт\n"
               "(повністю асоціативний пошук). Прапорці: чинний, права доступу, «брудний».",
               size=10, fill=FILL, stroke=LINE, color=INK)
    p.append(b)

    render(os.path.join(OUT, "entry.svg"), W, H, *p,
           title="Запис TLB: тег VPN → фрейм PPN, прапорці й мітка простору (ASID)")


# ── coverage: обхват TLB (reach) ──────────────────────────────────────────────
# Ідея: TLB покриває лише N сторінок водночас. Робочий набір, що влазить у це
# вікно, — суцільні влучання; більший — постійні промахи (thrashing).

def fig_coverage():
    W, H = 720, 340
    p = []

    # формула обхвату
    p.append(text(W / 2, 66, "обхват TLB  =  записів × розмір сторінки  ≈  64 × 4 КБ  =  256 КБ",
                  size=13, color=INK, bold=True))

    # дві смужки робочого набору
    def band(y0, used_frac, label, sub, good):
        out = []
        bx, bw, bh = 90, 540, 40
        out.append(rect(bx, y0, bw, bh, fill="#f0f1f3", stroke=LINE, sw=1.0, rx=4))
        # вікно обхвату TLB
        winw = bw * 0.42
        out.append(rect(bx, y0, winw, bh, fill=("#eafaf0" if good else "#eef4ff"),
                        stroke=(FIELD if good else NEG), sw=1.6, rx=4))
        out.append(text(bx + winw / 2, y0 + 26, "вікно TLB (256 КБ)", size=9.5,
                        color=(FIELD if good else NEG), bold=True))
        # робочий набір
        wsw = bw * used_frac
        out.append(line(bx, y0 - 8, bx + wsw, y0 - 8, color=(FIELD if good else POS), sw=3))
        out.append(text(bx + wsw / 2, y0 - 14, label, size=10,
                        color=(FIELD if good else POS), bold=True, anchor="middle"))
        out.append(text(bx + bw + 12, y0 + 26, sub, size=9.5,
                        color=(FIELD if good else POS), anchor="start", bold=True))
        return out

    p += band(130, 0.35, "робочий набір (< обхвату)",
              "суцільні влучання", good=True)
    p += band(240, 0.95, "робочий набір (> обхвату)",
              "постійні промахи", good=False)

    render(os.path.join(OUT, "coverage.svg"), W, H, *p,
           title="Обхват TLB: скільки пам'яті покрито без промахів залежить від набору")


# ── atlas-par: асоціативний склад Atlas (1962), 32 регістри адрес сторінок ────
# Ідея (для вставки hist-atlas): шуканий номер сторінки лягає воднораз на всі
# регістри; той, у кого ця сторінка, відгукується збігом; його позиція дає
# номер блоку осердя, до якого дописують «рядкові» біти зсуву → справжня адреса.
# Це прямий прообраз сучасного TLB: паралельний пошук за вмістом.

def fig_atlas_par():
    W, H = 720, 400
    p = []

    # шуканий номер сторінки
    p.append(rect(50, 150, 130, 46, fill="#eef4ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(115, 170, "шуканий номер", size=10.5, color=INK, bold=True))
    p.append(text(115, 186, "сторінки", size=10.5, color=INK, bold=True))

    # стовпчик 32 регістрів (показуємо кілька + «…»)
    ex, ey = 280, 70
    rowh, gap = 30, 6
    labels = ["блок 0:  стор. 17", "блок 1:  стор.  5",
              "блок 2:  стор. 42", "…  (усього 32)",
              "блок 31: стор.  9"]
    hot = 2
    for r, lab in enumerate(labels):
        y = ey + r * (rowh + gap)
        is_hot = (r == hot)
        p.append(rect(ex, y, 190, rowh, fill=("#fde9e7" if is_hot else FILL),
                      stroke=(INK if is_hot else LINE), sw=(2.0 if is_hot else 0.9), rx=4))
        p.append(text(ex + 95, y + 20, lab, size=10, color=INK,
                      bold=is_hot))
        # стрілка «порівняти» до кожного регістра — паралельно
        if lab.startswith("блок"):
            p.append(arrow(182, 173, ex - 6, y + rowh / 2, color=NEG, sw=1.1))

    p.append(text(115, 214, "порівняти з усіма", size=9.5, color=NEG, anchor="middle"))
    p.append(text(115, 228, "32 регістрами", size=9.5, color=NEG, anchor="middle"))
    p.append(text(115, 242, "водночас", size=9.5, color=NEG, anchor="middle"))

    # відгук збігу → номер блоку осердя
    yhot = ey + hot * (rowh + gap) + rowh / 2
    p.append(text(ex + 205, yhot - 6, "збіг!", size=11, color=INK, bold=True, anchor="start"))
    p.append(arrow(ex + 190 + 4, yhot, ex + 270, yhot, color=POS, sw=2.0))

    # складання справжньої адреси: номер блоку (5 біт) + рядок (зсув)
    bx, by = ex + 300, yhot - 22
    p.append(rect(bx, by, 60, 40, fill="#fde9e7", stroke=POS, sw=1.6, rx=4))
    p.append(text(bx + 30, by + 17, "блок", size=9.5, color=POS, bold=True))
    p.append(text(bx + 30, by + 31, "5 біт", size=9, color=MUTED))
    p.append(rect(bx + 62, by, 62, 40, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(bx + 62 + 31, by + 17, "рядок", size=9.5, color=FIELD, bold=True))
    p.append(text(bx + 62 + 31, by + 31, "зсув", size=9, color=MUTED))
    p.append(text(bx + 62, by + 58, "справжня адреса в осерді", size=9.5, color=INK, anchor="middle", bold=True))

    # пояснення знизу
    p.append(fitbox(ex, ey + 5 * (rowh + gap) + 16, 410, 40,
                    "32 регістри — по одному на блок осердя; питаємо «у кого ця сторінка?»\n"
                    "Асоціативний склад — прямий прообраз сьогоднішнього TLB.",
                    size=9.5, fill=FILL, stroke=LINE, color=INK))

    render(os.path.join(OUT, "atlas-par.svg"), W, H, *p,
           title="Асоціативний склад Atlas: 32 регістри, паралельний пошук сторінки")


if __name__ == "__main__":
    fig_translate()
    fig_walk()
    fig_entry()
    fig_coverage()
    fig_atlas_par()
    print("figs: готово")
