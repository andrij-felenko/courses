# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: ілюзія vs реальність ────────────────────────────────────────
def fig_illusion():
    W, H = 760, 430
    f = []
    f.append(text(W/2, 26, "Що бачить програма — і що є насправді", size=17, bold=True))

    # Дві ілюзорні колонки
    def virt(x, name, color):
        top = 60
        f.append(text(x+55, top-8, name, size=13, bold=True, color=color))
        f.append(rect(x, top, 110, 300, fill="#f8fafc", stroke=color, sw=1.8))
        labels = ["код", "дані", "…", "стек"]
        n = len(labels)
        seg = 300 / n
        for i, lb in enumerate(labels):
            yy = top + i*seg
            if i: f.append(line(x, yy, x+110, yy, color="#d0d5db", sw=1))
            f.append(text(x+55, yy+seg/2+4, lb, size=12, color=MUTED))
        f.append(text(x+55, top+300+18, "0 … велика адреса", size=10, color=MUTED))

    virt(60,  "Програма A", NEG)
    virt(200, "Програма B", FIELD)
    f.append(text(130, 388, "кожна бачить рівний власний простір", size=11, color=INK))

    # Реальна фізична пам'ять + диск праворуч
    px = 470
    f.append(text(px+90, 52, "Фізична RAM (мала, спільна)", size=12, bold=True))
    f.append(rect(px, 60, 180, 210, fill="#ffffff", stroke=INK, sw=1.8))
    # Розкидані кадри-фрейми з підписами, чиї вони
    frames = [(NEG,"A"),(FIELD,"B"),(NEG,"A"),(None,""),(FIELD,"B"),
              (NEG,"A"),(None,""),(FIELD,"B"),(None,""),(NEG,"A")]
    fh = 210/len(frames)
    for i,(c,who) in enumerate(frames):
        yy = 60 + i*fh
        fill = "#f4f6f8" if c is None else ("#eaf0fd" if c==NEG else "#e7f6ee")
        f.append(rect(px+6, yy+2, 168, fh-4, fill=fill,
                      stroke=(c or "#c8ccd2"), sw=1.2, rx=3))
        if who:
            f.append(text(px+16, yy+fh/2+4, who, size=11, bold=True, color=c))
        else:
            f.append(text(px+90, yy+fh/2+4, "вільно", size=9, color=MUTED))

    # Диск (swap)
    f.append(rect(px, 300, 180, 70, fill="#fbfbfd", stroke=MUTED, sw=1.5))
    f.append(text(px+90, 322, "Диск (swap)", size=12, bold=True, color=MUTED))
    f.append(text(px+90, 344, "виселені сторінки A і B", size=10, color=MUTED))
    f.append(text(px+90, 388, "насправді — упереміш, дещо на диску", size=11, color=INK))

    # Стрілки-мапування (кілька)
    f.append(arrow(172, 130, px-2, 90, color=NEG, sw=1.4))
    f.append(arrow(312, 170, px-2, 210, color=FIELD, sw=1.4))
    f.append(arrow(172, 300, px-2, 330, color=NEG, sw=1.4))
    f.append(text(390, 250, "мапування", size=11, italic=True, color=INK))

    render(os.path.join(IMG, "illusion.svg"), W, H, *f)


# ── Фігура 2: переклад адреси (VPN+offset → PPN+offset) ────────────────────
def fig_translate():
    W, H = 760, 320
    f = []
    f.append(text(W/2, 26, "Переклад однієї адреси: чіпаємо лише номер сторінки", size=17, bold=True))

    # Віртуальна адреса
    vx, vy = 40, 70
    f.append(text(vx+140, vy-12, "Віртуальна адреса", size=12, bold=True, color=NEG))
    f.append(rect(vx, vy, 180, 46, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(rect(vx+120, vy, 60, 46, fill="#ffffff", stroke=NEG, sw=1.5))
    f.append(text(vx+60, vy+29, "VPN", size=14, bold=True, color=NEG))
    f.append(text(vx+150, vy+29, "зсув", size=12, color=INK))
    f.append(text(vx+60, vy+64, "яка сторінка", size=10, color=MUTED))
    f.append(text(vx+150, vy+64, "місце в ній", size=10, color=MUTED))

    # Таблиця сторінок
    tx, ty = 300, 60
    f.append(text(tx+90, ty-12, "Таблиця сторінок", size=12, bold=True))
    rows = [("0","→ фрейм 7"),("1","→ на диску"),("2","→ фрейм 3"),("3","→ фрейм 9")]
    rh = 34
    for i,(k,v) in enumerate(rows):
        yy = ty + i*rh
        hl = (i == 2)
        f.append(rect(tx, yy, 180, rh, fill=("#e7f6ee" if hl else "#f8fafc"),
                      stroke=(FIELD if hl else "#c8ccd2"), sw=(1.8 if hl else 1)))
        f.append(text(tx+20, yy+rh/2+4, k, size=12, bold=True))
        f.append(text(tx+115, yy+rh/2+4, v, size=12,
                      color=(FIELD if hl else INK)))
    # стрілка VPN -> таблиця
    f.append(arrow(vx+60, vy+46, tx+30, ty+2*rh+4, color=NEG, sw=1.6))
    f.append(text(vx+120, vy+120, "VPN індексує рядок", size=10, italic=True, color=MUTED))

    # Фізична адреса
    fx, fy = 560, 70
    f.append(text(fx+90, fy-12, "Фізична адреса", size=12, bold=True, color=FIELD))
    f.append(rect(fx, fy, 160, 46, fill="#e7f6ee", stroke=FIELD, sw=1.8))
    f.append(rect(fx+100, fy, 60, 46, fill="#ffffff", stroke=FIELD, sw=1.5))
    f.append(text(fx+50, fy+29, "фрейм 3", size=12, bold=True, color=FIELD))
    f.append(text(fx+130, fy+29, "зсув", size=12, color=INK))
    # стрілка таблиця -> фрейм
    f.append(arrow(tx+180, ty+2*rh+rh/2, fx-2, fy+23, color=FIELD, sw=1.6))
    # зсув без змін
    f.append(arrow(vx+150, vy+46, fx+130, fy, color=MUTED, sw=1.4, ))
    f.append(text(390, 250, "зсув переходить без змін — усередині сторінки все впритул",
                  size=11, italic=True, color=INK))

    render(os.path.join(IMG, "translate.svg"), W, H, *f)


# ── Фігура 3: збій сторінки (page fault) ───────────────────────────────────
def fig_fault():
    W, H = 720, 350
    f = []
    f.append(text(W/2, 26, "Збій сторінки: доступ до того, чого немає в RAM", size=17, bold=True))

    steps = [
        ("1", "Програма читає\nадресу на сторінці,\nякої немає в RAM", "#eaf0fd", NEG),
        ("2", "Залізо бачить\n«немає» → перериває\nпрограму (trap)", "#fdecea", POS),
        ("3", "Ядро ОС бере\nсторінку з диска\nу вільний фрейм", "#f8fafc", INK),
        ("4", "Править таблицю,\nповторює ту саму\nінструкцію — тепер влучає", "#e7f6ee", FIELD),
    ]
    bw, bh = 150, 110
    gap = (W - 4*bw) / 5
    y = 90
    xs = []
    for i,(n, txt, fill, col) in enumerate(steps):
        x = gap + i*(bw+gap)
        xs.append(x)
        f.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.8))
        f.append(circle(x+18, y+18, 12, fill="#ffffff", stroke=col, sw=1.6))
        f.append(text(x+18, y+22, n, size=13, bold=True, color=col))
        f.append(mtext(x+bw/2, y+52, txt, size=11, color=INK))
    for i in range(3):
        x1 = xs[i]+bw
        x2 = xs[i+1]
        f.append(arrow(x1, y+bh/2, x2, y+bh/2, color=LINE, sw=1.8))

    f.append(text(W/2, y+bh+50,
                  "Програма нічого не помічає — лише невеличку затримку.",
                  size=12, color=INK))
    f.append(text(W/2, y+bh+72,
                  "Для неї сторінка «завжди була на місці». Це і є ілюзія суцільної пам'яті.",
                  size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, "fault.svg"), W, H, *f)


# ── Фігура (історія): дві віхи народження віртуальної пам'яті ───────────────
def fig_atlas_denning():
    W, H = 780, 400
    f = []
    f.append(text(W/2, 26, "Дві віхи: залізо навчилося ілюзії — потім ми зрозуміли її межу",
                  size=16, bold=True))

    # Часова вісь
    ax0, ax1, ay = 70, W-40, 120
    f.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    f.append(arrow(ax1-2, ay, ax1+2, ay, color=INK, sw=2))
    for yr, xf in [("1962", 0.16), ("1968", 0.62)]:
        x = ax0 + (ax1-ax0)*xf
        f.append(line(x, ay-6, x, ay+6, color=INK, sw=2))
        f.append(text(x, ay-14, yr, size=14, bold=True))

    # Ліворуч: Атлас 1962 — реалізація
    x1 = ax0 + (ax1-ax0)*0.16
    b1 = fitbox(x1-140, ay+30, 280, 118,
                "«Атлас» / one-level store\n"
                "Манчестер + Ferranti, Кілберн\n"
                "перша АПАРАТНА підкачка з барабана\n"
                "прибрала ручні overlay",
                size=12, fill="#e7f6ee", stroke=FIELD, sw=1.8)
    f.append(b1)
    f.append(text(x1, ay+30+118+20, "залізо дало ілюзію", size=12, italic=True, color=FIELD))

    # Праворуч: Деннінг 1968 — теорія
    x2 = ax0 + (ax1-ax0)*0.62
    b2 = fitbox(x2-150, ay+30, 300, 118,
                "Пітер Деннінг\n"
                "робочий набір + локальність\n"
                "пояснив пробуксовування (thrashing):\n"
                "робочий набір переріс RAM",
                size=12, fill="#eaf0fd", stroke=NEG, sw=1.8)
    f.append(b2)
    f.append(text(x2, ay+30+118+20, "теорія пояснила межу", size=12, italic=True, color=NEG))

    # Стрілка причинного зв'язку між ними
    f.append(arrow(x1+140, ay+30+59, x2-150, ay+30+59, color=MUTED, sw=1.6))
    f.append(text((x1+x2)/2, ay+30+59-10, "шість років потому", size=10, italic=True, color=MUTED))

    render(os.path.join(IMG, "atlas-denning.svg"), W, H, *f)


if __name__ == "__main__":
    fig_illusion()
    fig_translate()
    fig_fault()
    fig_atlas_denning()
    print("figs done")
