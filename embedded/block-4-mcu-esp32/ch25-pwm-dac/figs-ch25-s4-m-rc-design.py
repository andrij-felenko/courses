# -*- coding: utf-8 -*-
"""
Фігури до вставки ch25-s4-m-rc-design.md
«Проєктування RC-фільтра для ШІМ: зріз, пульсація в мВ, час встановлення»

Вивід → ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Палітра з figs.py (узгоджена) ──────────────────────────────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK_L = "#1b1b1b"   # локальний INK, щоб не плутати з svgkit.INK
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fff6e0"
GOLD  = "#caa24a"
FONT_L = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _hdr(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK_L}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def _ftr():
    return "</svg>\n"


def _ln(x1, y1, x2, y2, color=INK_L, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def _arr(x1, y1, x2, y2, color=INK_L, w=2):
    mid = {"aInk": INK_L, RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}
    m = "aRed" if color == RED else ("aBlue" if color == BLUE else
        ("aGreen" if color == GREEN else "aInk"))
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


def _txt(x, y, s, size=14, color=INK_L, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT_L}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def _box(x, y, w, h, fill="none", stroke=INK_L, sw=1.6, rx=6):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def _poly(pts, color=INK_L, w=2):
    joined = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{joined}" fill="none" stroke="{color}" '
            f'stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>\n')


def _save(name, body):
    body += _ftr()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.7.4m.1 — Пульсація по шкалі шпаруватості (парабола з LSB-лінією)
# ─────────────────────────────────────────────────────────────────────────────
def fig_4m1_ripple_vs_duty():
    """
    Показує Vpp = U·D·(1−D)/(f·R·C) як функцію D:
    парабола 0→0→0 з піком ~500 мВ на D=50%.
    Параметри: U=3.3 В, f=5 кГц, R=10 кОм, C=33 нФ.
    Горизонтальна пунктирна лінія = 1 LSB для 8-бітного ЦАП (3300/256 ≈ 12.9 мВ).
    """
    W, H = 880, 420

    # Фізичні параметри
    U = 3.3          # В
    f = 5000.0       # Гц
    R = 10_000.0     # Ом
    C = 33e-9        # Ф
    RC = R * C       # 330 мкс

    # Vpp(max) при D=0.5 = U/(4·f·RC) = 3.3/(4·5000·3.3e-4) = 0.5 В = 500 мВ
    def vpp_mv(D):
        return U * D * (1 - D) / (f * RC) * 1000  # мВ

    vpp_max = vpp_mv(0.5)   # ≈ 500 мВ
    lsb_mv  = U / 256 * 1000  # ≈ 12.9 мВ

    # Координати графіка
    ox, oy_bottom = 100, 340   # початок осей
    ax_w, ax_h = 700, 260      # ширина і висота осі

    # Масштаб: 0…600 мВ → ax_h пікселів
    y_max_mv = 600.0
    def mv_to_y(mv):
        return oy_bottom - (mv / y_max_mv) * ax_h

    s = _hdr(W, H)

    # ── заголовок ──────────────────────────────────────────────────────────
    s += _txt(W / 2, 30, "Пульсація ШІМ-ЦАП залежить від шпаруватості", 17, INK_L, "middle", "bold")
    s += _txt(W / 2, 50, "Vpp = U·D·(1−D)/(f·R·C) — парабола з піком на D = 50%", 10.5, GREY, "middle", style="italic")

    # ── осі ────────────────────────────────────────────────────────────────
    # Y-вісь
    s += _arr(ox, oy_bottom + 10, ox, oy_bottom - ax_h - 20, INK_L, 2)
    s += _txt(ox - 6, oy_bottom - ax_h - 22, "Vpp, мВ", 10.5, INK_L, "end", "bold")

    # X-вісь
    s += _arr(ox - 10, oy_bottom, ox + ax_w + 20, oy_bottom, INK_L, 2)
    s += _txt(ox + ax_w + 22, oy_bottom + 4, "D, %", 10.5, INK_L, "start", "bold")

    # ── мітки Y ────────────────────────────────────────────────────────────
    for mv_tick in [100, 200, 300, 400, 500]:
        yy = mv_to_y(mv_tick)
        s += _ln(ox - 6, yy, ox + ax_w, yy, FAINT, 1.2, "3,3")
        s += _txt(ox - 10, yy + 4, str(mv_tick), 10, GREY, "end")

    # ── мітки X ────────────────────────────────────────────────────────────
    for d_pct in range(0, 101, 10):
        xx = ox + (d_pct / 100) * ax_w
        s += _ln(xx, oy_bottom, xx, oy_bottom + 5, INK_L, 1.4)
        if d_pct % 20 == 0:
            s += _txt(xx, oy_bottom + 18, f"{d_pct}", 10, GREY, "middle")

    # ── парабола Vpp(D) ─────────────────────────────────────────────────────
    N = 100
    pts = []
    for i in range(N + 1):
        D = i / N
        xx = ox + D * ax_w
        yy = mv_to_y(vpp_mv(D))
        pts.append((xx, yy))
    s += _poly(pts, RED, 2.8)

    # ── лінія LSB ──────────────────────────────────────────────────────────
    y_lsb = mv_to_y(lsb_mv)
    s += _ln(ox, y_lsb, ox + ax_w, y_lsb, GREEN, 1.8, "8,5")

    # ── підписи на графіку ─────────────────────────────────────────────────
    # пік параболи: виносна лінія
    x_peak = ox + 0.5 * ax_w
    y_peak = mv_to_y(vpp_max)
    s += _ln(x_peak, y_peak, x_peak, y_peak - 36, RED, 1.4, "4,3")
    s += _box(x_peak - 60, y_peak - 68, 120, 28, FAINT, RED, 1.2, 6)
    s += _txt(x_peak, y_peak - 49, "пік: ≈ 500 мВ", 10.5, RED, "middle", "bold")

    # лінія LSB — підпис праворуч
    s += _box(ox + ax_w - 120, y_lsb - 16, 118, 22, "#f0faf2", GREEN, 1.2, 5)
    s += _txt(ox + ax_w - 62, y_lsb - 2, f"1 LSB ≈ {lsb_mv:.0f} мВ (8 біт)", 9.5, GREEN, "middle", "bold")

    # де брижа > LSB — виносний текст
    # Vpp > LSB коли D·(1-D) > lsb_mv/(1000*(U/(f·R·C)))
    # Шукаємо D при якому Vpp = lsb_mv
    # D*(1-D) = lsb_mv/1000 / (U/(f*RC)) = lsb_mv*f*RC/(1000*U)
    k = lsb_mv / 1000 * f * RC / U  # ≈ 0.00064
    # D^2 - D + k = 0 → D = (1 ± sqrt(1-4k))/2
    disc = 1 - 4 * k
    if disc > 0:
        d_lo = (1 - math.sqrt(disc)) / 2
        d_hi = (1 + math.sqrt(disc)) / 2
        # зона де Vpp > LSB: між d_lo і d_hi (майже весь діапазон)
        x_lo = ox + d_lo * ax_w
        x_hi = ox + d_hi * ax_w
        s += _ln(x_lo, y_lsb, x_lo, oy_bottom, GREEN, 1, "3,3")
        s += _ln(x_hi, y_lsb, x_hi, oy_bottom, GREEN, 1, "3,3")
        # заштрихована зона — де брижа перевищує 1 LSB (просто горизонтальний підпис)
        s += _txt((x_lo + x_hi) / 2, y_lsb - 22, "брижа > 1 LSB: зайві біти ШІМ марні", 9, GREEN, "middle")

    # ── підпис прикладу (під графіком) ──────────────────────────────────────
    s += _box(80, 365, 720, 40, LAMB, GOLD, 1.4, 8)
    s += _txt(W / 2, 381, "U = 3.3 В, f = 5 кГц, R = 10 кОм, C = 33 нФ  →  RC = 330 мкс.", 10, INK_L, "middle", "bold")
    s += _txt(W / 2, 397, "Пульсація НЕ стала по шкалі — проєктуй фільтр на найгіршу точку (50%).", 9.5, GREY, "middle")

    _save("fig-25-4m-1-ripple-vs-duty.svg", s)


if __name__ == "__main__":
    fig_4m1_ripple_vs_duty()
    print("done.")
