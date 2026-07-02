# -*- coding: utf-8 -*-
# Фігури для вставки proj-echo-picking.md (окремий файл, щоб не заважати
# паралельному письму основного figs.py тієї ж теми). Вивід — той самий ./img/.
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── proj-echo-gate: спадний поріг (STC) + бланкування + вимога тривалості ──────
# Ідея proj-вставки: показати весь «ворота відлуння» в часі. Після імпульсу —
# бланкування (глуха зона дзвону), далі СПАДНИЙ поріг STC. Три відлуння:
# хвіст дзвону (нижче порогу — відкинуто), бокове дзеркальне (коротке — не
# пройшло вимоги тривалості), справжнє (перше, що і вище порогу, і досить довге).
def fig_echo_gate():
    W, H = 880, 420
    p = []
    ax, ay = 70, 300           # початок і рівень «нуля» осі часу
    aw = W - 150
    p.append(line(ax, ay, ax + aw, ay, color=INK, sw=1.6))
    p.append(text(ax + aw, ay + 20, "час польоту", size=11, italic=True))
    p.append(text(ax - 8, ay - 150, "амплітуда", size=11, anchor="end", italic=True))

    # межа бланкування
    blank_x = ax + 120
    p.append(rect(ax, ay - 175, blank_x - ax, 175, fill="#fdecea", stroke="none", rx=3))
    p.append(line(blank_x, ay - 175, blank_x, ay, color=POS, sw=1.2, dash="4 4"))
    p.append(text((ax + blank_x) / 2, ay - 158, "бланкування", size=11, color=POS, bold=True))
    p.append(text((ax + blank_x) / 2, ay - 143, "(дзвін — глухо)", size=10, color=POS))

    # спадний поріг STC: від високого одразу після бланка до низького вдалині
    thr_x0, thr_y0 = blank_x, ay - 150
    thr_x1, thr_y1 = ax + aw - 10, ay - 34
    p.append(line(thr_x0, thr_y0, thr_x1, thr_y1, color=NEG, sw=2.2))
    p.append(text(thr_x1, thr_y1 - 10, "спадний поріг (STC)", size=11, color=NEG,
                  anchor="end", bold=True))

    def burst(cx, peak_h, half_w, col, ncyc=6):
        out = []
        for i in range(-ncyc, ncyc + 1):
            x = cx + i * (half_w / ncyc)
            env = peak_h * math.exp(-(i / (ncyc * 0.6)) ** 2)
            sign = 1 if i % 2 == 0 else -1
            out.append(line(x, ay, x, ay - sign * env, color=col, sw=1.8))
        return out

    # 1) хвіст власного дзвону одразу за бланком — але НИЖЧЕ порогу
    tail_x = blank_x + 28
    p += burst(tail_x, 26, 20, MUTED, ncyc=5)
    p.append(text(tail_x, ay + 18, "хвіст дзвону", size=10, color=MUTED))
    p.append(text(tail_x, ay + 32, "нижче порогу ✗", size=9, color=MUTED))

    # 2) бокове дзеркальне — сильне, але КОРОТКЕ (не пройде вимоги тривалості)
    mir_x = blank_x + 155
    p += burst(mir_x, 96, 9, POS, ncyc=3)
    p.append(text(mir_x, ay - 112, "бокове дзеркальне", size=10, color=POS, bold=True))
    p.append(text(mir_x, ay + 18, "закоротке ✗", size=10, color=POS))

    # 3) справжнє відлуння — вище спадного порогу і ДОСИТЬ ДОВГЕ
    real_x = blank_x + 335
    p += burst(real_x, 84, 30, FIELD, ncyc=8)
    p.append(text(real_x, ay - 98, "справжня ціль ✓", size=11, color=FIELD, bold=True))
    # позначка тривалості над сплеском справжнього
    p.append(line(real_x - 30, ay - 92, real_x + 30, ay - 92, color=FIELD, sw=1.2))
    p.append(text(real_x, ay - 78, "тривалість ≥ N", size=9, color=FIELD))
    # стрілка «перше, що пройшло всі перевірки»
    p.append(arrow(real_x, ay + 46, real_x, ay + 10, color=FIELD, sw=1.6))
    p.append(text(real_x, ay + 62, "перше, що пройшло ВСІ перевірки → d = v·t/2",
                  size=10, color=FIELD, bold=True))

    p.append(text(W / 2, H - 14,
                  "ворота відлуння: бланкувати дзвін · тримати поріг спадним · вимагати мінімальної тривалості — і брати перше вціліле",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "proj-echo-gate.svg"), W, H, *p,
           title="Вибір справжнього відлуння: бланк + спадний поріг + тривалість")


# ── proj-median-reject: медіана кількох вимірів викидає поодинокий стрибок ─────
# Ідея: навіть після воріт один вимір зрідка стрибає (шумовий викид, чужий пінг).
# Медіана з N вимірів стійка: щоб зрушити її, треба зіпсувати БІЛЬШЕ половини.
def fig_median_reject():
    W, H = 860, 380
    p = []
    ax, ay = 70, 250
    aw = W - 150
    p.append(line(ax, ay, ax + aw, ay, color=INK, sw=1.6))
    p.append(text(ax + aw, ay + 20, "виміряна відстань", size=11, italic=True))

    # «істинна» зона
    true_x = ax + 210
    band = 40
    p.append(rect(true_x - band, ay - 150, 2 * band, 150, fill="#eafaf0", stroke="none", rx=3))
    p.append(line(true_x, ay - 150, true_x, ay, color=FIELD, sw=1.2, dash="5 4"))
    p.append(text(true_x, ay - 158, "справжня відстань", size=11, color=FIELD, bold=True))

    # п'ять вимірів: чотири близькі, один дикий стрибок праворуч
    vals = [true_x - 22, true_x + 8, true_x - 6, true_x + 20, ax + aw - 60]
    labs = ["d₁", "d₂", "d₃", "d₄", "d₅ (викид)"]
    for x, lab in zip(vals, labs):
        col = POS if "викид" in lab else NEG
        p.append(circle(x, ay - 20, 7, fill="#fff", stroke=col, sw=2))
        p.append(text(x, ay - 34, lab, size=10, color=col, bold=("викид" in lab)))
        p.append(line(x, ay - 8, x, ay, color=col, sw=1.2))

    # середнє — тягнеться до викиду
    mean_x = sum(vals) / len(vals)
    p.append(line(mean_x, ay - 118, mean_x, ay, color=POS, sw=2.0, dash="3 3"))
    p.append(text(mean_x, ay - 124, "середнє — з'їхало до викиду ✗", size=10, color=POS, bold=True))

    # медіана — середній за рангом, лишається в зоні
    smid = sorted(vals)[len(vals) // 2]
    p.append(line(smid, ay - 88, smid, ay, color=FIELD, sw=2.4))
    p.append(text(smid, ay - 94, "медіана — стоїть на місці ✓", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, H - 40,
                  "медіана зсунеться лише тоді, коли зіпсовано БІЛЬШЕ половини вимірів (поріг злому 50 %)",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, H - 16,
                  "один дикий стрибок (чужий пінг, шумовий викид) середнє тягне, а медіану — ні; тому беруть медіану кількох пінгів",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "proj-median-reject.svg"), W, H, *p,
           title="Медіана кількох пінгів викидає поодинокий стрибок")


if __name__ == "__main__":
    fig_echo_gate()
    fig_median_reject()
    print("OK: proj figures written to", OUT)
