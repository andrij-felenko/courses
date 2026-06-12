# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для історичної вставки до теми 2.9.1
«Епоха Databook-ів» (Розділ 2.9, Модуль 2).

Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс fig-r09-1h-…), щоб не перетинатися з головним figs.py розділу
та з іншими вставками.
Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
SUN   = "#e0a32e"
PAPER = "#f3e6c4"   # колір старого паперу/обкладинки
DISC  = "#cfe0ef"   # CD-ROM
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREY: "aGrey", GREEN: "aGreen"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _book(x, baseY, w, h, spine, label, sub, year, fill, ink=INK):
    """Малює корінець «книги»-databook-а на полиці: прямокутник + товщина."""
    s = ""
    depth = 9
    # бокова грань (товщина тому)
    s += (f'<polygon points="{x:.1f},{baseY - h:.1f} {x + depth:.1f},{baseY - h - depth:.1f} '
          f'{x + depth:.1f},{baseY - depth:.1f} {x:.1f},{baseY:.1f}" '
          f'fill="#d9c79b" stroke="{ink}" stroke-width="1.4"/>\n')
    # верхня грань
    s += (f'<polygon points="{x:.1f},{baseY - h:.1f} {x + depth:.1f},{baseY - h - depth:.1f} '
          f'{x + w + depth:.1f},{baseY - h - depth:.1f} {x + w:.1f},{baseY - h:.1f}" '
          f'fill="#e7d9b3" stroke="{ink}" stroke-width="1.4"/>\n')
    # лицьова обкладинка
    s += rect(x, baseY - h, w, h, fill, ink, 1.6, 2)
    # «корінцева» смужка-етикетка
    s += rect(x + 6, baseY - h + 8, w - 12, 22, "#ffffff", ink, 1.1, 2)
    s += text(x + w / 2, baseY - h + 23, label, 11, ink, "middle", "bold")
    s += text(x + w / 2, baseY - h / 2 + 6, sub, 9, ink, "middle")
    s += text(x + w / 2, baseY + 17, year, 9.5, GREY, "middle", "bold")
    return s


# ── Рис. 2.9.1h.1 — від паперового тому до PDF: як стискався «паспорт» ────────
def fig_era():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 30, "Як «паспорт компонента» стискався: від полиці databook-ів до файлу", 15.5, INK, "middle", "bold")

    baseY = 300
    # полиця
    s += line(60, baseY + 4, W - 60, baseY + 4, INK, 2.4)

    # 1) RCA Receiving Tube Manual — товстий том ери ламп
    s += _book(95, baseY, 96, 150, 14, "RCA RC-30", "Receiving Tube Manual", "1933–1975", PAPER)
    # 2) TI TTL Data Book — «жовтогаряча» цеглина ери TTL
    s += _book(235, baseY, 104, 168, 14, "TI · TTL", "Data Book for Design Eng.", "1973 →", "#f2b733")
    # підпис до кольору обкладинки (обережно — «(перевірити)»)
    s += text(287, baseY - 178, "колір — жовто-", 8.5, GREY, "middle", style="italic")
    s += text(287, baseY - 168, "жовтогарячий (перевірити)", 8.5, GREY, "middle", style="italic")

    # 3) CD-ROM — диск із даташитами 1990-х
    cx, cy = 470, baseY - 70
    s += circle(cx, cy, 56, DISC, INK, 1.6)
    s += circle(cx, cy, 16, "#ffffff", INK, 1.4)
    s += circle(cx, cy, 5, FAINT, GREY, 1)
    s += text(cx, cy - 24, "CD-ROM", 11, INK, "middle", "bold")
    s += text(cx, cy + 34, "«вся бібліотека", 8.5, INK, "middle")
    s += text(cx, cy + 45, "на одному диску»", 8.5, INK, "middle")
    s += text(cx, baseY + 17, "1990-ті", 9.5, GREY, "middle", "bold")

    # 4) PDF-файл — сьогодні (зв'язок із темою 2.9.1: Ctrl+F)
    fx, fy, fw, fh = 600, baseY - 150, 96, 130
    s += rect(fx, fy, fw, fh, "#ffffff", INK, 1.8, 4)
    # «загнутий ріжок»
    s += (f'<polygon points="{fx + fw - 22:.1f},{fy:.1f} {fx + fw:.1f},{fy + 22:.1f} '
          f'{fx + fw - 22:.1f},{fy + 22:.1f}" fill="{FAINT}" stroke="{INK}" stroke-width="1.4"/>\n')
    s += text(fx + 14, fy + 44, "PDF", 14, RED, "start", "bold")
    for i, yy in enumerate((62, 74, 86, 98, 110)):
        ww = fw - 26 if i % 2 == 0 else fw - 46
        s += line(fx + 12, fy + yy, fx + 12 + ww, fy + yy, FAINT, 3)
    s += text(fx + fw / 2, baseY + 17, "сьогодні", 9.5, GREY, "middle", "bold")
    # лупа Ctrl+F
    lx, ly = fx + fw + 6, fy + 96
    s += circle(lx, ly, 12, "none", GREEN, 2.4)
    s += line(lx + 8, ly + 8, lx + 20, ly + 20, GREEN, 2.8)
    s += text(fx + fw + 30, fy + 70, "Ctrl+F", 10, GREEN, "start", "bold")
    s += text(fx + fw + 30, fy + 84, "знайде рядок", 8.5, GREEN, "start")
    s += text(fx + fw + 30, fy + 98, "за секунду", 8.5, GREEN, "start")

    # стрілки «спадкоємності» по верху
    ay = 86
    for (x1, x2) in ((191, 235), (339, 414), (526, 600)):
        s += arrow(x1, ay, x2, ay, GREY, 2.2)
    s += text((191 + 235) / 2, ay - 8, "лампа → чип", 8, GREY, "middle")
    s += text((339 + 414) / 2, ay - 8, "том → диск", 8, GREY, "middle")
    s += text((526 + 600) / 2, ay - 8, "диск → файл", 8, GREY, "middle")

    # нижній висновок
    s += text(W / 2, H - 16,
              "Документ не зник — він став доступним для пошуку: те, що колись займало метри полиць, тепер уміщається у файл.",
              9.5, GREY, "middle", style="italic")
    save("fig-r09-1h-1-databook-era.svg", s)


if __name__ == "__main__":
    fig_era()
    print("OK — фігуру історичної вставки 2.9.1h згенеровано в", OUT)
