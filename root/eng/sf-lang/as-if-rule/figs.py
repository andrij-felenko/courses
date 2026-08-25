# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODE_BG = "#0f1b14"
CODE_FG = "#eaf6ee"
ASM_BG  = "#13202a"
ASM_FG  = "#7fe0a0"


def codebox(x, y, w, h, s, fg=CODE_FG, bg=CODE_BG, size=12):
    """Темна рамка з одним моноширинним рядком, вирівняним ліворуч."""
    out = rect(x, y, w, h, fill=bg, stroke="#0a120d", sw=1.4, rx=8)
    out += ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', monospace" '
            'font-size="%d" fill="%s" text-anchor="start" font-weight="700">%s</text>'
            % (x + 14, y + h / 2 + size * 0.35, size, fg, esc(s)))
    return out


# ── fence: що ОГОРОДЖЕНЕ (спостережуване, чіпати не можна) vs вільне всередині ──
# Ідея теми: правило «ніби» проводить огорожу. Зовні — те, що видно світові
# (volatile, ввід-вивід, факт і порядок завершення): недоторканне. Всередині —
# внутрішня кухня (регістр/пам'ять, порядок незалежних дій, мертвий код):
# переписуй як хоч. Це серце статті, окреме від «один результат — багато виходів».

def fig_fence():
    W, H = 780, 420
    p = []
    # зовнішня рамка — «що бачить світ»
    p.append(rect(30, 60, W - 60, H - 100, fill="#eef4ff", stroke=NEG, sw=2.2, rx=16))
    p.append(text(W / 2, 84, "СПОСТЕРЕЖУВАНА ПОВЕДІНКА — чіпати НЕ можна", size=13, color=NEG, bold=True))
    obs = [
        "доступи до volatile-комірок",
        "ввід-вивід (файли, порти, консоль)",
        "факт і порядок завершення програми",
    ]
    oy = 112
    for it in obs:
        p.append(fitbox(56, oy, 300, 40, it, size=11, fill=BG, stroke=NEG, sw=1.4, color=INK))
        oy += 50
    # внутрішня рамка — «внутрішня кухня»
    ix, iy, iw, ih = 400, 108, 340, 220
    p.append(rect(ix, iy, iw, ih, fill="#eef6ef", stroke=FIELD, sw=2, rx=14))
    p.append(text(ix + iw / 2, iy + 22, "внутрішня кухня — вільно переписати", size=12, color=FIELD, bold=True))
    free = [
        "тримати змінну в регістрі чи в пам'яті",
        "порядок незалежних обчислень",
        "викинути мертвий код і зайві читання",
        "порахувати сталі наперед, злити цикли",
    ]
    fy = iy + 44
    for it in free:
        p.append(text(ix + 18, fy + 4, "• " + it, size=10.5, color=INK, anchor="start"))
        fy += 30
    p.append(text(W / 2, H - 22,
                  "рівність лише на огорожі: що видно ззовні — збігається; як усередині — байдуже",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "fence.svg"), W, H, *p,
           title="Правило «ніби»: огорожа спостережуваного")


# ── two-machines: абстрактна машина (текст) ↔ реальна (кремній), збіг у точках ─
# Ідея: код описує ідеальну «абстрактну машину» крок за кроком; реальна машина
# мусить збігтися з нею ЛИШЕ у точках спостереження (позначках ▮), а між ними —
# робить що завгодно. Показує, ЧОМУ проміжні стани не гарантовані.

def fig_two_machines():
    W, H = 800, 340
    p = []
    ax0, ax1 = 70, 730
    # верхня доріжка — абстрактна машина (як написано)
    yA = 110
    p.append(text(ax0 - 6, yA - 34, "абстрактна машина (як каже текст) — усі кроки по черзі",
                  size=11, color=NEG, anchor="start", bold=True))
    p.append(line(ax0, yA, ax1, yA, color=NEG, sw=2))
    for i in range(7):
        cx = ax0 + (ax1 - ax0) * i / 6
        p.append(circle(cx, yA, 5, fill="#eef4ff", stroke=NEG, sw=1.6))
    # нижня доріжка — реальна машина (що виконує кремній)
    yR = 250
    p.append(text(ax0 - 6, yR + 40, "реальна машина (кремній) — свій шлях між точками",
                  size=11, color=FIELD, anchor="start", bold=True))
    p.append(line(ax0, yR, ax1, yR, color=FIELD, sw=2))
    # точки спостереження — три штуки, де доріжки ОБОВ'ЯЗКОВО збігаються
    obs_frac = [1.0 / 6, 3.0 / 6, 5.0 / 6]
    for f in obs_frac:
        cx = ax0 + (ax1 - ax0) * f
        p.append(line(cx, yA, cx, yR, color=INK, sw=1.6, dash="5 4"))
        p.append(rect(cx - 7, yA - 10, 14, 20, fill=INK, stroke=INK, sw=1, rx=2))
        p.append(rect(cx - 7, yR - 10, 14, 20, fill=INK, stroke=INK, sw=1, rx=2))
    p.append(text((ax0 + ax1) / 2, (yA + yR) / 2,
                  "збіг ОБОВ'ЯЗКОВИЙ лише тут  →  точки спостереження (volatile / ввід-вивід)",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, H - 16,
                  "між точками реальна машина вільна: проміжні стани текст НЕ обіцяє",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "two-machines.svg"), W, H, *p,
           title="Дві машини збігаються лише в точках спостереження")


# ── trap: та сама причина ламає МК — зникла затримка й «закешоване» читання ────
# Ідея: два практичні випадки, де «невидиме» правило прибирає задумане. Ліворуч —
# джерело, праворуч — що лишилось; знизу — рятунок volatile робить доступ видимим.

def fig_trap():
    W, H = 800, 380
    p = []
    p.append(text(250, 74, "як написано", size=11, color=INK, bold=True))
    p.append(text(600, 74, "що згенеровано (-O2)", size=11, color=INK, bold=True))
    rows = [
        ("Затримка порожнім циклом",
         "for(i=0;i<9999;i++);", "(зникло)", "тіло нічого не змінює → мертве", POS, "#fdecea"),
        ("Читання регістра-порту",
         "while(!(REG & RDY));", "прочитав раз, крутить далі", "REG «не міняється» у коді", POS, "#fdecea"),
    ]
    y = 92
    for tag, src, dst, note, col, fill in rows:
        p.append(text(40, y + 26, tag, size=10, color=col, anchor="start", bold=True))
        p.append(codebox(240, y, 240, 42, src, size=11))
        p.append(arrow(486, y + 21, 536, y + 21, color=col, sw=2.4))
        p.append(codebox(544, y, 220, 42, dst, size=10, bg=ASM_BG, fg=ASM_FG))
        p.append(text(544, y + 60, note, size=9, color=MUTED, anchor="start"))
        y += 96
    # рятунок
    p.append(rect(60, 300, W - 120, 60, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=12))
    p.append(mtext(W / 2, 322,
                   ["Це не баг компілятора — код не оголосив ці доступи спостережуваними.",
                    "volatile переводить доступ через огорожу — і правило «ніби» його вже не чіпає."],
                   size=10.5, color=INK))
    render(os.path.join(OUT, "trap.svg"), W, H, *p,
           title="Той самий закон прибирає задумане на МК")


# ── barrier: компіляторний бар'єр порядку (asm volatile("" ::: "memory")) ──────
# Ідея вставки-proj: без бар'єра компілятор вільний перемежати записи буфера й
# запис старту DMA; бар'єр проводить межу порядку (0 інструкцій) — усі записи
# буфера ВИЩЕ, старт НИЖЧЕ. Показує, ЧОМУ це огорожа порядку, а не гальмо.

def fig_barrier():
    W, H = 820, 400
    p = []
    colB = NEG          # записи буфера (звичайна RAM)
    colS = POS          # запис старту (volatile-регістр)
    colW = W / 2 - 30   # ширина кожної колонки

    def slot(x, y, label, col, fill):
        return fitbox(x, y, colW - 20, 26, label, size=10.5,
                      fill=fill, stroke=col, sw=1.4, color=INK)

    # ── ЛІВОРУЧ: без бар'єра — доступи перемежані ──
    lx = 40
    p.append(text(lx + colW / 2, 66, "без бар'єра", size=12, color=INK, bold=True))
    p.append(text(lx + colW / 2, 84, "компілятор вільний тасувати", size=9.5, color=MUTED))
    seqL = [
        ("buf[0] = …", colB, "#eaf0fd"),
        ("DMA_START = 1", colS, "#fdecea"),   # старт «прослизнув» уперед!
        ("buf[1] = …", colB, "#eaf0fd"),
        ("buf[2] = …", colB, "#eaf0fd"),
    ]
    y = 100
    for lab, col, fill in seqL:
        p.append(slot(lx, y, lab, col, fill))
        y += 34
    p.append(text(lx + colW / 2, y + 14, "старт міг піти по недописаному буфері",
                  size=9.5, color=POS, bold=True))

    # ── ПРАВОРУЧ: з бар'єром — межа проведена ──
    rx = W / 2 + 20
    p.append(text(rx + colW / 2, 66, "з бар'єром", size=12, color=INK, bold=True))
    p.append(text(rx + colW / 2, 84, 'asm volatile("" ::: "memory")', size=9.5, color=FIELD, bold=True))
    seqR_top = [("buf[0] = …", colB, "#eaf0fd"),
                ("buf[1] = …", colB, "#eaf0fd"),
                ("buf[2] = …", colB, "#eaf0fd")]
    y = 100
    for lab, col, fill in seqR_top:
        p.append(slot(rx, y, lab, col, fill))
        y += 34
    # межа порядку — 0 інструкцій
    p.append(line(rx - 6, y + 4, rx + colW + 6, y + 4, color=FIELD, sw=2.4, dash="7 4"))
    p.append(text(rx + colW / 2, y + 20, "── межа порядку · 0 інструкцій ──",
                  size=9.5, color=FIELD, bold=True))
    p.append(slot(rx, y + 30, "DMA_START = 1", colS, "#fdecea"))
    p.append(text(rx + colW / 2, y + 78, "усі записи буфера завершені ДО старту",
                  size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "barrier.svg"), W, H, *p,
           title="Компіляторний бар'єр проводить межу порядку")


# ── hist-abstract-machine: еталонна абстрактна машина ↔ багато реальних ────────
# Ідея вставки-hist: знахідка комітету. Угорі — вигадана абстрактна машина зі
# стандарту (єдиний еталон); унизу — кілька несхожих реальних реалізацій, кожна
# своєю дорогою. Збіг вимагається ЛИШЕ на видимому результаті (стрілки сходяться
# в одну «межу спостережуваного»). Показує, ЧОМУ це мирить переносність і волю.

def fig_abstract_machine():
    W, H = 820, 430
    p = []
    # ── еталон: абстрактна машина (лише на папері) ──
    ex, ey, ew, eh = W / 2 - 175, 62, 350, 74
    p.append(rect(ex, ey, ew, eh, fill="#eef4ff", stroke=NEG, sw=2.4, rx=14))
    p.append(text(W / 2, ey + 24, "АБСТРАКТНА МАШИНА зі стандарту", size=12.5, color=NEG, bold=True))
    p.append(text(W / 2, ey + 44, "кожен крок чесно й по черзі", size=10, color=INK))
    p.append(text(W / 2, ey + 61, "існує лише на папері — еталон", size=9.5, color=MUTED, italic=True))

    # ── три несхожі реальні реалізації ──
    ry = 250
    reals = [
        (90,  "реалізація A", "багато регістрів,\nрахує сталі наперед", NEG, "#eaf0fd"),
        (335, "реалізація B", "мало регістрів,\nсвій порядок дій",     POS, "#fdecea"),
        (580, "реалізація C", "інший кремній,\nвикидає мертве",         FIELD, "#eef6ef"),
    ]
    rw = 150
    for rxp, tag, note, col, fill in reals:
        p.append(rect(rxp, ry, rw, 66, fill=fill, stroke=col, sw=1.8, rx=12))
        p.append(text(rxp + rw / 2, ry + 22, tag, size=11, color=col, bold=True))
        p.append(mtext(rxp + rw / 2, ry + 40, note.split("\n"), size=9, color=INK))
        # стрілка від еталона вниз до кожної реалізації
        p.append(arrow(W / 2, ey + eh + 2, rxp + rw / 2, ry - 4, color=MUTED, sw=1.6))

    # ── межа спостережуваного: збіг ЛИШЕ тут ──
    by = ry + 92
    p.append(rect(70, by, W - 140, 40, fill=BG, stroke=INK, sw=2, rx=10))
    p.append(text(W / 2, by + 25,
                  "МЕЖА СПОСТЕРЕЖУВАНОГО — тут результат КОЖНОЇ реалізації = еталон",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, H - 14,
                  "дорога вільна · збігтися має лише те, що перетинає межу",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "hist-abstract-machine.svg"), W, H, *p,
           title="Знахідка комітету: один еталон, багато реальних доріг")


# ── hist-agreement-point: точки згоди на осі виконання ─────────────────────────
# Ідея вставки-hist: образ «agreement point» з Rationale. Вісь — плин виконання;
# на точках згоди (volatile/ввід-вивід) реальне значення = абстрактне; між ними
# реальна машина вільна. Ліворуч sum живе в регістрі, праворуч volatile-запис
# дає обов'язкову згоду. Показує ДЕ саме звірка з еталоном.

def fig_agreement_point():
    W, H = 820, 340
    p = []
    ax0, ax1 = 70, 750
    yE = 118   # еталон (абстрактна машина)
    yR = 250   # реальна машина

    p.append(text(ax0 - 4, yE - 30, "абстрактна машина (еталон)", size=10.5, color=NEG, anchor="start", bold=True))
    p.append(line(ax0, yE, ax1, yE, color=NEG, sw=2))
    p.append(text(ax0 - 4, yR + 42, "реальна машина (кремній)", size=10.5, color=FIELD, anchor="start", bold=True))
    p.append(line(ax0, yR, ax1, yR, color=FIELD, sw=2))

    # дві точки згоди
    pts = [(1.0 / 4, "volatile-запис", POS), (3.0 / 4, "ввід-вивід", POS)]
    for f, lab, col in pts:
        cx = ax0 + (ax1 - ax0) * f
        p.append(line(cx, yE - 12, cx, yR + 12, color=INK, sw=1.8, dash="5 4"))
        p.append(circle(cx, yE, 6, fill="#eef4ff", stroke=NEG, sw=2))
        p.append(circle(cx, yR, 6, fill="#eef6ef", stroke=FIELD, sw=2))
        p.append(text(cx, yR + 30, "точка згоди", size=9.5, color=INK, bold=True))
        p.append(text(cx, yE - 18, lab, size=9.5, color=col, bold=True))

    # підпис вільного відрізка (між лівим краєм і першою точкою)
    midL = (ax0 + (ax0 + (ax1 - ax0) * 0.25)) / 2
    p.append(text(midL, (yE + yR) / 2 - 4, "sum — лише в регістрі", size=9.5, color=MUTED, italic=True))
    p.append(text(midL, (yE + yR) / 2 + 12, "(нікому не видно)", size=9, color=MUTED, italic=True))
    # підпис вільного відрізка між точками
    midM = ax0 + (ax1 - ax0) * 0.5
    p.append(text(midM, (yE + yR) / 2 + 4, "реальна машина вільна: свій порядок, свої регістри",
                  size=9.5, color=MUTED, italic=True))

    p.append(text(W / 2, H - 14,
                  "на точках згоди значення реальної машини = значення еталона; між ними — власний шлях",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "hist-agreement-point.svg"), W, H, *p,
           title="Точка згоди: де реальна машина звіряється з еталоном")


if __name__ == "__main__":
    fig_fence()
    fig_two_machines()
    fig_trap()
    fig_barrier()
    fig_abstract_machine()
    fig_agreement_point()
    print("OK: figures written to", OUT)
