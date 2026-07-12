# -*- coding: utf-8 -*-
"""Фігури до кроку «DH перетинає межу машини».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER   = "#b8860b"   # бурштиновий — «застаріле / здогад»
AMBERBG = "#fff8e8"
AMBERST = "#c9a93b"
FAINTG  = "#f2f9f4"    # ледь-зелений фон «дому»
FAINT   = "#f4f6f8"


def xmark(cx, cy, r=9, color=POS, sw=2.6):
    """Хрестик «розірвано» двома лініями (не текстом — щоб не було накладань)."""
    return (line(cx - r, cy - r, cx + r, cy + r, color=color, sw=sw) +
            line(cx - r, cy + r, cx + r, cy - r, color=color, sw=sw))


def drect(x, y, w, h, stroke=LINE, sw=1.5, rx=6, dash="6,6"):
    """Пунктирний прямокутник без заливки (rect зі svgkit dash не має)."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
            'fill="none" stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>'
            % (x, y, w, h, rx, stroke, sw, dash))


# ───────── Фіг. 1: той самий шов — нова фізика ─────────
def fig_seam_boundary():
    W, H = 1000, 440
    f = []
    f.append(line(500, 62, 500, 372, color="#e5e7eb", sw=1))

    # ── ЛІВА: один процес ──
    f.append(text(270, 78, "Один процес", size=15, bold=True, color=FIELD))
    f.append(fitbox(70, 154, 150, 60, "логіка хаба", size=13, bold=True))
    f.append(arrow(220, 184, 250, 184, color=FIELD, sw=2.2))
    # шов-порт як зелена планка
    f.append(rect(258, 152, 12, 64, fill="#eafaf0", stroke=FIELD, sw=2))
    f.append(text(264, 234, "порт", size=11, bold=True, color=FIELD))
    f.append(arrow(270, 184, 300, 184, color=FIELD, sw=2.2))
    f.append(fitbox(304, 154, 160, 60, "хмара-порт\n(у тім самім процесі)", size=12))
    f.append(fitbox(80, 320, 360, 44,
                    "виклик функції · все-або-нічого · дешево",
                    size=12, fill=FAINTG, stroke=FIELD, color=INK, bold=True, sw=1.6))

    # ── ПРАВА: дві машини ──
    f.append(text(748, 78, "Дві машини", size=15, bold=True, color=INK))
    f.append(fitbox(524, 154, 150, 60, "логіка хаба", size=13, bold=True))
    f.append(arrow(674, 184, 704, 184, color=INK, sw=2.2))
    # той самий порт — та сама форма
    f.append(rect(712, 152, 12, 64, fill="#eafaf0", stroke=FIELD, sw=2))
    f.append(text(718, 234, "порт", size=11, bold=True, color=FIELD))
    # межа машини
    f.append(line(760, 118, 760, 300, color=MUTED, sw=1.4, dash="5,6"))
    f.append(text(760, 110, "межа машини", size=11, color=MUTED, italic=True))
    # перетин межі — червоним, бо небезпечно
    f.append(arrow(724, 184, 800, 184, color=POS, sw=2.3))
    f.append(fitbox(806, 154, 150, 60, "хмара\n(інша машина)", size=12,
                    stroke=POS, color=POS, bold=True))
    f.append(fitbox(520, 320, 440, 44,
                    "за портом тепер: таймаут · повтор · ключ · часткова відмова",
                    size=12, fill=AMBERBG, stroke=AMBERST, color=INK, bold=True, sw=1.6))

    # нижній банер
    f.append(fitbox(250, 388, 500, 40,
                    "Той самий шов. За ним — уже не пам'ять, а мережа.",
                    size=15, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))

    render(os.path.join(IMG, "seam-boundary.svg"), W, H, *f,
           title="Перенести межу — не пересунути шов, а змінити фізику за ним")


# ───────── Фіг. 2: дві течії крізь одну межу ─────────
def fig_two_paths():
    W, H = 1000, 430
    f = []
    # межа машини — короткими насічками, щоб не перетинати підписи течій
    f.append(line(500, 96, 500, 138, color=MUTED, sw=1.4, dash="5,6"))
    f.append(line(500, 240, 500, 264, color=MUTED, sw=1.4, dash="5,6"))
    f.append(text(500, 88, "межа машини", size=11, color=MUTED, italic=True))
    # сторони
    f.append(rect(60, 112, 380, 240, fill=FAINTG, stroke=FIELD, sw=1.6, rx=12))
    f.append(text(250, 106, "ДІМ — хаб + пристрої", size=14, bold=True, color=FIELD))
    f.append(rect(560, 112, 380, 240, fill=FAINT, stroke=LINE, sw=1.4, rx=12))
    f.append(text(750, 106, "ХМАРА", size=14, bold=True, color=INK))

    # КОМАНДА: хмара → хаб (згори), червоним
    f.append(text(500, 150, "КОМАНДА   зачини / відчини", size=13, bold=True, color=POS))
    f.append(arrow(830, 176, 168, 176, color=POS, sw=2.4))
    f.append(fitbox(176, 196, 648, 36,
                    "бюджет часу · ключ ідемпотентності · доставка «фактично раз»",
                    size=12, fill=AMBERBG, stroke=AMBERST, color=INK, bold=True, sw=1.5))

    # ЗВІТ: хаб → хмара (знизу), синім
    f.append(text(500, 276, "ЗВІТ   температура, стан замка", size=13, bold=True, color=NEG))
    f.append(arrow(168, 302, 830, 302, color=NEG, sw=2.4))
    f.append(fitbox(150, 320, 700, 36,
                    "«щонайменше раз» · дедуп за ключем · терпить переупорядкування · буфер, поки хмара мовчить",
                    size=11, fill="#eaf0fd", stroke=NEG, color=INK, bold=True, sw=1.5))

    render(os.path.join(IMG, "two-paths.svg"), W, H, *f,
           title="Одна межа — дві течії з протилежною поставою")


# ───────── Фіг. 3: межу проводять так, щоб важливе лишилось удома ─────────
def fig_vital_loop():
    W, H = 1000, 430
    f = []
    # ДІМ
    f.append(rect(56, 92, 560, 296, fill=FAINTG, stroke=FIELD, sw=1.8, rx=14))
    f.append(text(336, 82, "ДІМ", size=16, bold=True, color=FIELD))

    # життєвий контур: кнопка → хаб → замок (усе всередині)
    f.append(fitbox(90, 150, 150, 56, "кнопка\nна стіні", size=13, bold=True,
                    fill="#eafaf0", stroke=FIELD, color=INK))
    f.append(fitbox(300, 150, 130, 56, "хаб", size=14, bold=True,
                    fill="#eafaf0", stroke=FIELD, color=INK))
    f.append(fitbox(478, 150, 120, 56, "замок", size=14, bold=True,
                    fill="#eafaf0", stroke=FIELD, color=INK))
    f.append(arrow(240, 178, 298, 178, color=FIELD, sw=2.3))
    f.append(arrow(430, 178, 476, 178, color=FIELD, sw=2.3))
    # рамка контуру
    f.append(drect(74, 132, 542, 96, stroke=FIELD, sw=1.5, rx=10, dash="6,6"))
    f.append(text(336, 250, "контур замикається без мережі",
                  size=12.5, bold=True, color=FIELD))

    # межа машини
    f.append(line(650, 96, 650, 388, color=MUTED, sw=1.4, dash="5,6"))
    f.append(text(650, 88, "межа машини", size=11, color=MUTED, italic=True))

    # хмара за межею — збагачення, яке можна втратити
    f.append(fitbox(724, 150, 200, 60, "хмара", size=14, bold=True))
    f.append(mtext(824, 236, ["збагачення,", "не залежність"], size=11, color=MUTED))
    # тонкий, розривний зв'язок від замка до хмари, проведений НИЖЧЕ вузлів і підпису
    f.append(line(538, 206, 538, 330, color=MUTED, sw=1.6))
    f.append(line(538, 330, 724, 330, color=MUTED, sw=1.6))
    f.append(line(724, 330, 724, 212, color=MUTED, sw=1.6))
    f.append(xmark(650, 330))

    f.append(fitbox(230, 392, 540, 34,
                    "Хмара впала? Контур удома все одно замикається.",
                    size=14, fill=FILL, stroke=INK, color=INK, bold=True, sw=1.8))

    render(os.path.join(IMG, "vital-loop.svg"), W, H, *f,
           title="Межу проводять так, щоб важливе лишилось на одному боці")


# ───────── Фіг. 4: один стан став трьома, що розходяться ─────────
def fig_desired_reported():
    W, H = 1000, 430
    f = []
    # межа машини — сегментами, щоб не перетнути підписи звірки
    f.append(line(440, 110, 440, 158, color=MUTED, sw=1.4, dash="5,6"))
    f.append(line(440, 178, 440, 256, color=MUTED, sw=1.4, dash="5,6"))
    f.append(line(440, 282, 440, 336, color=MUTED, sw=1.4, dash="5,6"))
    f.append(text(440, 102, "межа машини", size=11, color=MUTED, italic=True))

    # У ДОМІ — джерело правди
    f.append(text(210, 128, "У ДОМІ — джерело правди", size=13, bold=True, color=FIELD))
    f.append(fitbox(80, 150, 260, 90, "справжній стан\nЗАЧИНЕНО", size=14, bold=True,
                    fill="#eafaf0", stroke=FIELD, color=INK, sw=2))

    # У ХМАРІ — два здогади
    f.append(text(720, 118, "У ХМАРІ — два здогади", size=13, bold=True, color=INK))
    f.append(fitbox(560, 138, 360, 60, "бажаний (desired):  ЗАЧИНЕНО",
                    size=13, bold=True, fill=FAINT, stroke=LINE, color=INK))
    f.append(fitbox(560, 214, 360, 60, "востаннє почутий (reported):\nВІДЧИНЕНО о 10:02",
                    size=12.5, bold=True, fill=AMBERBG, stroke=AMBERST, color=INK))

    # звірка у фоні — дві стрілки
    f.append(text(500, 168, "надсилай бажаний, доки не збіжеться", size=11,
                  color=MUTED, italic=True))
    f.append(arrow(556, 180, 344, 192, color=MUTED, sw=1.7))
    f.append(arrow(344, 226, 556, 244, color=MUTED, sw=1.7))
    f.append(text(500, 268, "перечитуй справжній", size=11, color=MUTED, italic=True))

    f.append(fitbox(120, 350, 760, 40,
                    "Хмара не тримає правду — вона тримає бажане й востаннє почуте; збігаються вони у фоні, не миттєво.",
                    size=12.5, fill=FILL, stroke=INK, color=INK, bold=True, sw=1.8))
    f.append(text(830, 316, "→ зерно твіна дому", size=11, color=FIELD, italic=True))

    render(os.path.join(IMG, "desired-reported.svg"), W, H, *f,
           title="Один стан на одній машині — три стани на двох")


# ───────── Фіг. 5 (до вставки-проєкту): хронологія тесту з тишею ─────────
def fig_silence_test():
    W, H = 1000, 510
    f = []

    def xi(i):                       # індекс натискання 1..20 → x
        return 120 + (i - 1) / 19.0 * 780

    x5, x15 = xi(5), xi(15)

    # ── Доріжка A: життєвий контур ──
    f.append(text(112, 62, "Життєвий контур:  кнопка → замок",
                  size=14, bold=True, color=FIELD, anchor="start"))
    f.append(line(120, 88, 900, 88, color="#e5e7eb", sw=1.4))
    for i in range(1, 21):
        x = xi(i)
        f.append(line(x, 80, x, 96, color=FIELD, sw=3))
    f.append(text(112, 116,
                  "усі 20 натискань локальні й миттєві — жодне не торкається мережі",
                  size=12, italic=True, color=MUTED, anchor="start"))

    # ── Доріжка B: канал до хмари ──
    f.append(text(112, 150, "Хмара (канал зв'язку)", size=14, bold=True, color=INK, anchor="start"))
    f.append(rect(120, 160, x5 - 120, 30, fill="#eafaf0", stroke=FIELD, sw=1.4))
    f.append(rect(x5, 160, x15 - x5, 30, fill=AMBERBG, stroke=AMBERST, sw=1.6))
    f.append(rect(x15, 160, 900 - x15, 30, fill="#eafaf0", stroke=FIELD, sw=1.4))
    f.append(text((x5 + x15) / 2, 180, "ХМАРА МОВЧИТЬ", size=13, bold=True, color=INK))
    f.append(text((120 + x5) / 2, 180, "онлайн", size=11, color=FIELD))
    f.append(text((x15 + 900) / 2, 180, "онлайн", size=11, color=FIELD))
    f.append(text(x5, 210, "впала (5)", size=11, color=POS))
    f.append(text(x15, 210, "зв'язок вернувся (15)", size=11, color=FIELD))

    # ── Доріжка C: глибина буфера ──
    f.append(text(112, 244, "Буфер звітів (скільки чекає доставки)",
                  size=14, bold=True, color=INK, anchor="start"))
    base_y = 356
    f.append(line(120, base_y, 900, base_y, color="#e5e7eb", sw=1.4))
    depth = {5: 1, 6: 2, 7: 3, 8: 4, 9: 5, 10: 6, 11: 7, 12: 8, 13: 9, 14: 10,
             15: 8, 16: 5, 17: 3, 18: 1}
    for i in range(1, 21):
        d = depth.get(i, 0)
        if d == 0:
            continue
        x = xi(i)
        h = d * 8
        f.append(rect(x - 9, base_y - h, 18, h, fill=AMBERBG, stroke=AMBERST, sw=1.2, rx=2))
    f.append(text(112, 378,
                  "росте, поки хмара мовчить; долітає й порожніє, коли зв'язок вернувся",
                  size=12, italic=True, color=MUTED, anchor="start"))

    # ── Плашка про дедуп (два рядки — щоб шрифт не тиснуло нижче читаного) ──
    f.append(fitbox(150, 396, 700, 56,
                    ["Один звіт дійшов двічі (першу доставку застосовано, ACK загубився → хаб повторив) —",
                     "хмара впізнала дубль за власною міткою часу й застосувала його РІВНО раз."],
                    size=12, fill=FILL, stroke=AMBERST, color=INK, sw=1.4))

    # ── Підсумок ──
    f.append(fitbox(150, 462, 700, 38,
                    "Контур удома не здригнувся · звіти долетіли фактично раз, щойно зв'язок вернувся",
                    size=13, fill="#eafaf0", stroke=FIELD, color=INK, bold=True, sw=1.8))

    render(os.path.join(IMG, "silence-test.svg"), W, H, *f,
           title="Хронологія тесту: тиша хмари, буфер, дедуп")


if __name__ == "__main__":
    fig_seam_boundary()
    fig_two_paths()
    fig_vital_loop()
    fig_desired_reported()
    fig_silence_test()
    print("OK: seam-boundary.svg, two-paths.svg, vital-loop.svg, desired-reported.svg, silence-test.svg")
