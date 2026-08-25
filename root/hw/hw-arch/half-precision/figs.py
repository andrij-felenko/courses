# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори полів
C_SIGN = "#8e44ad"   # знак — фіолетовий
C_EXP  = "#c0392b"   # порядок — гарячий (діапазон)
C_MAN  = "#2457d6"   # мантиса — холодний (точність)


def field(x, y, w, h, label, sub, fill, big=15, small=11):
    """Кольорове поле бітів із двома підписами."""
    out = rect(x, y, w, h, fill=fill, stroke=INK, sw=1.4, rx=4)
    out += text(x + w / 2, y + h / 2 - 2, label, size=big, color="#ffffff", bold=True)
    if sub:
        out += text(x + w / 2, y + h / 2 + small + 2, sub, size=small, color="#f0f0f0")
    return out


# ── Фігура 1: три розкладки бітів у масштабі ────────────────────────────────
def fig_layouts():
    W, H = 760, 340
    bit = 16.5            # ширина одного біта в пікселях
    x0 = 140
    rows = [
        ("float32", 1, 8, 23, "32 біти"),
        ("float16", 1, 5, 10, "16 бітів"),
        ("bfloat16", 1, 8, 7, "16 бітів"),
    ]
    frags = []
    y = 70
    rh = 56
    gap = 30
    # шкала бітів згори
    frags.append(text(x0 - 8, 52, "старший біт", size=11, color=MUTED, anchor="end"))
    for name, s, e, m, total in rows:
        # мітка формату
        frags.append(text(x0 - 12, y + rh / 2 + 5, name, size=15, color=INK, anchor="end", bold=True))
        x = x0
        ws = s * bit
        frags.append(field(x, y, ws, rh, "S", "знак", C_SIGN, big=13, small=10)); x += ws
        we = e * bit
        frags.append(field(x, y, we, rh, "порядок", "%d б" % e, C_EXP)); x += we
        wm = m * bit
        frags.append(field(x, y, wm, rh, "мантиса", "%d б" % m, C_MAN)); x += wm
        frags.append(text(x + 12, y + rh / 2 + 5, total, size=12, color=MUTED, anchor="start"))
        y += rh + gap
    # підпис-висновок унизу
    note = ("float16 різав порядок (8→5) → менший діапазон; "
            "bfloat16 різав мантису (23→7) → діапазон як у float32")
    frags.append(text(W / 2, H - 16, note, size=11.5, color=INK))
    render(os.path.join(IMG, "layouts.svg"), W, H, *frags,
           title="Той самий 16-бітний бюджет — поділений двома різними способами")


# ── Фігура 2: діапазон vs точність (компроміс) ──────────────────────────────
def fig_tradeoff():
    W, H = 720, 360
    frags = []
    # осі
    ax, ay = 90, 300         # початок осей
    aw, ah = 560, 230
    frags.append(arrow(ax, ay, ax + aw, ay, color=INK, sw=1.8))          # X — діапазон
    frags.append(arrow(ax, ay, ax, ay - ah, color=INK, sw=1.8))          # Y — точність
    frags.append(text(ax + aw / 2, ay + 34, "діапазон (де живе порядок) →", size=12.5, color=INK, bold=True))
    frags.append(text(ax - 20, ay - ah / 2, "↑ точність (мантиса)", size=12.5, color=INK, bold=True,
                      anchor="middle"))
    # маркери форматів: (x_frac, y_frac, назва, колір, підпис)
    pts = [
        (0.95, 0.90, "float32", INK, "24 біти точності · ±3.4·10³⁸"),
        (0.30, 0.55, "float16", C_MAN, "11 бітів · ±65 504"),
        (0.95, 0.32, "bfloat16", C_EXP, "8 бітів · ±3.4·10³⁸"),
    ]
    for xf, yf, name, col, sub in pts:
        px = ax + xf * aw
        py = ay - yf * ah
        frags.append(circle(px, py, 8, fill=col, stroke=INK, sw=1.5))
        frags.append(text(px, py - 16, name, size=14, color=col, bold=True))
        frags.append(text(px, py + 24, sub, size=10.5, color=MUTED))
    # пунктир: float32 і bfloat16 на однаковому «діапазоні»
    frags.append(line(ax + 0.95 * aw, ay - 0.90 * ah, ax + 0.95 * aw, ay - 0.32 * ah,
                      color=MUTED, sw=1.2, dash="4 4"))
    frags.append(text(ax + 0.95 * aw + 8, ay - 0.61 * ah, "той самий\nдіапазон",
                      size=10, color=MUTED, anchor="start"))
    # пунктир: float16 і bfloat16 займають ту саму кількість бітів (16)
    frags.append(text(W / 2, H - 12,
                      "float16 і bfloat16 — обидва 16 бітів; один купує точність, другий — діапазон",
                      size=11.5, color=INK))
    render(os.path.join(IMG, "tradeoff.svg"), W, H, *frags,
           title="Що обміняли: float16 бере точність, bfloat16 — діапазон")


# ── Фігура 3: bfloat16 = старша половина float32 ────────────────────────────
def fig_truncate():
    W, H = 720, 300
    frags = []
    bit = 17.0
    x0 = 90
    # float32 згори — 32 клітинки
    y1 = 80
    rh = 48
    frags.append(text(x0 - 12, y1 + rh / 2 + 5, "float32", size=14, color=INK, anchor="end", bold=True))
    x = x0
    # знак+порядок+9 мантиси = старші 16
    top_s, top_e, top_m = 1, 8, 7
    ws = top_s * bit
    frags.append(field(x, y1, ws, rh, "S", "", C_SIGN, big=12)); x += ws
    we = top_e * bit
    frags.append(field(x, y1, we, rh, "порядок", "8", C_EXP)); x += we
    wm_top = top_m * bit
    frags.append(field(x, y1, wm_top, rh, "мант.", "7", C_MAN)); x += wm_top
    x_split = x
    # решта 16 бітів мантиси — сірі, «відрізаються»
    wm_rest = 16 * bit
    frags.append(rect(x, y1, wm_rest, rh, fill="#e5e7eb", stroke=MUTED, sw=1.2, rx=4))
    frags.append(text(x + wm_rest / 2, y1 + rh / 2 + 5, "решта мантиси (16 бітів) — відкидаємо",
                      size=11, color=MUTED))
    x_end = x + wm_rest
    # лінія розрізу
    frags.append(line(x_split, y1 - 14, x_split, y1 + rh + 60, color=POS, sw=2.2, dash="6 4"))
    frags.append(text(x_split, y1 - 20, "розріз", size=11.5, color=POS, bold=True))
    # стрілки вниз від старших 16 до bfloat16
    y2 = y1 + rh + 90
    frags.append(text(x0 - 12, y2 + rh / 2 + 5, "bfloat16", size=14, color=INK, anchor="end", bold=True))
    x = x0
    frags.append(field(x, y2, ws, rh, "S", "", C_SIGN, big=12)); x += ws
    frags.append(field(x, y2, we, rh, "порядок", "8", C_EXP)); x += we
    frags.append(field(x, y2, wm_top, rh, "мант.", "7", C_MAN)); x += wm_top
    # стрілка «беремо старшу половину»
    frags.append(arrow((x0 + x_split) / 2, y1 + rh + 6, (x0 + x_split) / 2, y2 - 6, color=INK, sw=1.8))
    frags.append(text((x0 + x_split) / 2 + 8, (y1 + rh + y2) / 2 + 4,
                      "беремо старші 16 бітів", size=11, color=INK, anchor="start"))
    frags.append(text(W / 2, H - 14,
                      "Перетворення float32 → bfloat16 — це просто «взяти старшу половину слова»",
                      size=11.5, color=INK))
    render(os.path.join(IMG, "truncate.svg"), W, H, *frags,
           title="Чому bfloat16 дешевий: це верхні 16 бітів float32")


# ── Фігура 4: чому відкидання зміщує вниз, а округлення — ні ─────────────────
def fig_bias():
    W, H = 720, 340
    frags = []
    ax = 90
    aw = 540
    y = 160
    # числова вісь між двома сусідніми представними значеннями bfloat16
    frags.append(line(ax, y, ax + aw, y, color=INK, sw=2))
    frags.append(circle(ax, y, 6, fill=C_MAN, stroke=INK, sw=1.5))
    frags.append(circle(ax + aw, y, 6, fill=C_MAN, stroke=INK, sw=1.5))
    frags.append(text(ax, y - 16, "нижча сходинка", size=12, color=C_MAN, bold=True))
    frags.append(text(ax + aw, y - 16, "вища сходинка", size=12, color=C_MAN, bold=True))
    # межа «до кого ближче» — рівно посередині
    xm = ax + aw / 2
    frags.append(line(xm, y - 34, xm, y + 34, color=MUTED, sw=1.4, dash="5 4"))
    frags.append(text(xm, y + 50, "рівно посередині", size=10.5, color=MUTED))
    # приклад-точка: правіше середини (ближче до вищої)
    xp = ax + aw * 0.62
    frags.append(circle(xp, y, 7, fill="#ffffff", stroke=INK, sw=2))
    frags.append(text(xp, y - 44, "справжнє float32", size=11, color=INK, bold=True))
    frags.append(line(xp, y - 34, xp, y - 8, color=INK, sw=1.2))
    # відкидання: тягне ВЛІВО (вниз) завжди
    frags.append(arrow(xp - 6, y + 74, ax + 12, y + 74, color=POS, sw=2))
    frags.append(text((ax + xp) / 2, y + 92, "ВІДКИДАННЯ → завжди вниз",
                      size=11.5, color=POS, bold=True))
    # округлення: до найближчої — тут праворуч
    frags.append(arrow(xp + 6, y - 74, ax + aw - 12, y - 74, color=FIELD, sw=2))
    frags.append(text((xp + ax + aw) / 2, y - 82, "ОКРУГЛЕННЯ → до найближчої",
                      size=11.5, color=FIELD, bold=True))
    frags.append(text(W / 2, H - 14,
                      "Відкидання завжди зсуває до нижчої сходинки → сума мільйона чисел «сповзає» вниз",
                      size=11.5, color=INK))
    render(os.path.join(IMG, "bias.svg"), W, H, *frags,
           title="Чому грубе відкидання дає систематичну похибку")


# ── Фігура 5: трюк round-to-nearest-even через додавання зміщення ────────────
def fig_rte():
    W, H = 720, 350
    frags = []
    bit = 15.0
    x0 = 78
    rh = 40
    w_keep = 16 * bit
    w_drop = 16 * bit
    x_lsb = x0 + w_keep
    # рядок 1: біти float32, поділені на «лишаємо 16» | «відкидаємо 16»
    y1 = 74
    frags.append(text(x0 - 10, y1 + rh / 2 + 5, "float32", size=13, color=INK, anchor="end", bold=True))
    frags.append(rect(x0, y1, w_keep, rh, fill="#dbe4ff", stroke=C_MAN, sw=1.4))
    frags.append(text(x0 + w_keep / 2, y1 + rh / 2 + 5, "старші 16 — лишаємо", size=11, color=INK))
    frags.append(rect(x_lsb, y1, w_drop, rh, fill="#fdecea", stroke=POS, sw=1.4))
    frags.append(text(x_lsb + w_drop / 2, y1 + rh / 2 + 5, "молодші 16 — на округлення", size=11, color=POS))
    frags.append(text(x_lsb, y1 - 10, "межа розрізу", size=10.5, color=MUTED))
    # рядок 2: що додаємо — 0x7FFF + LSB збереженого поля
    y2 = 168
    frags.append(text(x0 - 10, y2 + rh / 2 + 5, "+ зміщення", size=13, color=FIELD, anchor="end", bold=True))
    frags.append(rect(x0, y2, w_keep, rh, fill="#eafaf1", stroke=FIELD, sw=1.4))
    frags.append(text(x0 + w_keep / 2, y2 + rh / 2 + 5, "0…0 + (LSB поля вище)", size=11, color=FIELD))
    frags.append(rect(x_lsb, y2, w_drop, rh, fill="#eafaf1", stroke=FIELD, sw=1.4))
    frags.append(text(x_lsb + w_drop / 2, y2 + rh / 2 + 5, "0x7FFF", size=12, color=FIELD, bold=True))
    # стрілка «переніс піднімає старше поле, лише коли треба»
    frags.append(arrow(x_lsb, y2 - 6, x_lsb, y1 + rh + 6, color=INK, sw=1.8))
    frags.append(text(x_lsb + 10, (y1 + rh + y2) / 2 + 4,
                      "переніс піднімає біт лише коли треба вгору", size=10.5,
                      color=INK, anchor="start"))
    # підсумок унизу — три випадки
    frags.append(fitbox(x0, 255, W - 2 * x0, 66,
                        "нижче половини → переніс не дійде → лишиться нижня сходинка\n"
                        "вище половини → переніс дійде → підніметься до вищої\n"
                        "рівно половина → додавання LSB штовхає до ПАРНОЇ сходинки",
                        size=11.5, fill="#f8f9fa", stroke=MUTED))
    render(os.path.join(IMG, "rte.svg"), W, H, *frags,
           title="Трюк round-to-nearest-even: одне додавання замість гілок")


if __name__ == "__main__":
    fig_layouts()
    fig_tradeoff()
    fig_truncate()
    fig_bias()
    fig_rte()
    print("figures written")
