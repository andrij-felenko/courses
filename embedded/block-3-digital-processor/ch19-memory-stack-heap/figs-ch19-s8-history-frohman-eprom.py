# -*- coding: utf-8 -*-
"""
Генератор SVG для 📜-історії до теми §3.6.8 — «Дов Фроман і EPROM (1971):
пам'ять із кварцовим віконцем під ультрафіолет».

Окремий від головного figs.py (його НЕ чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/. Стиль (AUTHORING §9) — спільні допоміжні функції скопійовано
з figs.py розділу, щоб вигляд був єдиний: білий фон, «1» червоний, «0» синій,
поле зелене, стрілки через marker, sans-serif.

Чотири фігури, кожна несе вагу (§9):
  fig-19-8h-1-famos   комірка FAMOS: ізольований плавучий затвор, лавинна
                      інжекція заряду й зсув порога (механізм запису/читання
                      саме EPROM — те, що Фроман зробив практичним)
  fig-19-8h-2-cycle   повний цикл життя біта: чисто → запис (заряд усередині)
                      → УЛЬТРАФІОЛЕТ крізь КВАРЦОВЕ ВІКОНЦЕ стирає весь чип →
                      знову чисто; серце «віконця під ультрафіолет»
  fig-19-8h-3-flow    чому стирання все змінило: цикл «прошив → знайшов баг →
                      стер → прошив знову» проти однораз. масок ROM
  fig-19-8h-4-lineage родовід плавучого затвора (колективна атрибуція §10):
                      Канг і Це (1967, ідея) → Фроман / FAMOS / 1702 (1971,
                      робочий чип) → EEPROM → Flash (§3.6.8)
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
AMBER = "#caa24a"
VIOLET = "#7b3fb0"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aViolet" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{VIOLET}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", VIOLET: "aViolet", AMBER: "aAmber"}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def polygon(points, fill="none", stroke=INK, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n'


def electron(cx, cy, r=4.6):
    """Маленький електрон: синій кружечок зі знаком «−»."""
    s = circle(cx, cy, r, BLUE, BLUE, 0)
    s += line(cx - r * 0.5, cy, cx + r * 0.5, cy, "#ffffff", 1.4)
    return s


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═══════════ Рис. 3.6.8i.1 — комірка FAMOS: плавучий затвор і лавинна інжекція ═══
def fig_famos():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 32, "Комірка FAMOS: те, що зробив практичним Фроман",
              20, INK, "middle", "bold")
    s += text(W / 2, 54, "плавучий затвор замкнено в ізоляторі; заряд у ньому зсуває поріг транзистора — і це й кодує біт",
              12, GREY, "middle", style="italic")

    # ── один спільний кремнієвий стек, два стани поруч ──
    def cell(ox, charged, title, sub, bitcol, bit):
        cw = 300
        # підкладка p-Si
        s_ = rect(ox, 320, cw, 70, "#eef1f5", INK, 1.8, 0)
        s_ += text(ox + cw / 2, 360, "підкладка (p-Si)", 12, GREY, "middle")
        # витік / стік (n+)
        s_ += rect(ox + 18, 300, 70, 24, "#dfe7f5", BLUE, 1.6, 0)
        s_ += text(ox + 53, 317, "витік", 9.5, BLUE, "middle", "bold")
        s_ += rect(ox + cw - 88, 300, 70, 24, "#dfe7f5", BLUE, 1.6, 0)
        s_ += text(ox + cw - 53, 317, "стік", 9.5, BLUE, "middle", "bold")
        # тонкий оксид
        s_ += rect(ox + 88, 286, cw - 176, 14, "#f3ecd6", AMBER, 1.4, 0)
        s_ += text(ox + cw / 2, 297, "тонкий оксид", 8.5, "#8a7320", "middle")
        # плавучий затвор (ізольований з усіх боків)
        fgfill = "#fbe2df" if charged else "#ffffff"
        s_ += rect(ox + 96, 250, cw - 192, 26, fgfill, RED, 2.4, 4)
        s_ += text(ox + cw / 2, 267, "плавучий затвор", 11, RED, "middle", "bold")
        # ізолятор над плавучим
        s_ += rect(ox + 96, 236, cw - 192, 14, "#f3ecd6", AMBER, 1.2, 0)
        # керівний затвор
        s_ += rect(ox + 96, 210, cw - 192, 26, "#e9e9e9", INK, 1.8, 4)
        s_ += text(ox + cw / 2, 227, "керівний затвор", 11, INK, "middle", "bold")
        # заряд усередині плавучого
        if charged:
            for i in range(6):
                s_ += electron(ox + 118 + i * 16, 263)
            s_ += text(ox + cw / 2, 196, "заряд ЗАМКНЕНО", 11, BLUE, "middle", "bold")
        else:
            s_ += text(ox + cw / 2, 196, "заряду немає", 11, GREY, "middle", style="italic")
        # підпис стану
        s_ += text(ox + cw / 2, 418, title, 14, INK, "middle", "bold")
        s_ += text(ox + cw / 2, 437, sub, 10.5, GREY, "middle")
        # який біт читається
        s_ += rect(ox + cw / 2 - 70, 452, 140, 34, "#ffffff", bitcol, 2, 6)
        s_ += text(ox + cw / 2, 475, bit, 13, bitcol, "middle", "bold")
        return s_

    s += cell(70, True, "Запрограмовано", "високий поріг → не вмикається",
              BLUE, "читаємо «0»")
    s += cell(540, False, "Чисто (стерто)", "низький поріг → вмикається легко",
              RED, "читаємо «1»")

    # ── лавинна інжекція: як заряд потрапляє всередину (ліва комірка) ──
    s += text(220, 118, "ЗАПИС: лавинна інжекція", 13, GREEN, "middle", "bold")
    s += text(220, 136, "сильне поле розганяє електрони — гарячі електрони",
              10, GREY, "middle")
    s += text(220, 150, "перестрибують крізь оксид у пастку плавучого затвора",
              10, GREY, "middle")
    s += arrow(220, 158, 220, 246, GREEN, 2.4)
    for i in range(3):
        s += electron(206 + i * 14, 178)

    # підпис методу
    s += text(220, 506, "(саме лавинну інжекцію крізь товстий оксид", 9.5, "#6f6f6f", "middle", style="italic")
    s += text(220, 520, "Фроман зробив надійною — звідси назва FAMOS)", 9.5, "#6f6f6f", "middle", style="italic")

    # ── читання (права комірка) ──
    s += text(690, 118, "ЧИТАННЯ: дивимось на поріг", 13, INK, "middle", "bold")
    s += text(690, 136, "пробуємо ввімкнути транзистор —", 10, GREY, "middle")
    s += text(690, 150, "відкрився чи ні, те й каже біт усередині", 10, GREY, "middle")
    s += text(690, 506, "читання заряду НЕ чіпає → біт тримається роками,", 9.5, "#6f6f6f", "middle", style="italic")
    s += text(690, 520, "поки його не стерти (нелетка пам'ять, §3.6.8)", 9.5, "#6f6f6f", "middle", style="italic")

    save("fig-19-8h-1-famos.svg", s)


# ═══════════ Рис. 3.6.8i.2 — цикл життя біта: запис → УФ крізь віконце → чисто ═══
def fig_cycle():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 32, "Серце EPROM: записати електрикою, стерти — ультрафіолетом крізь кварцове віконце",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "записати можна окремі біти; стерти — лише ВЕСЬ чип одразу, спалахом УФ-світла, що скидає весь замкнений заряд",
              11.5, GREY, "middle", style="italic")

    cy = 150
    bw, bh = 150, 96

    # ── стан 1: чистий чип ──
    x1 = 60
    s += rect(x1, cy, bw, bh, "#f4f7f4", GREEN, 2, 10)
    s += text(x1 + bw / 2, cy + 24, "Чистий чип", 13, GREEN, "middle", "bold")
    s += text(x1 + bw / 2, cy + 44, "усі плавучі затвори", 9.5, GREY, "middle")
    s += text(x1 + bw / 2, cy + 58, "порожні", 9.5, GREY, "middle")
    s += text(x1 + bw / 2, cy + 80, "усі біти = 1", 11, RED, "middle", "bold")

    # ── стрілка: запис ──
    s += arrow(x1 + bw, cy + bh / 2, x1 + bw + 90, cy + bh / 2, INK, 2.4)
    s += text(x1 + bw + 45, cy + bh / 2 - 12, "ЗАПИС", 11, INK, "middle", "bold")
    s += text(x1 + bw + 45, cy + bh / 2 + 22, "висока", 9, GREY, "middle")
    s += text(x1 + bw + 45, cy + bh / 2 + 35, "напруга", 9, GREY, "middle")

    # ── стан 2: запрограмований ──
    x2 = x1 + bw + 90
    s += rect(x2, cy, bw, bh, "#f7f9fc", BLUE, 2, 10)
    s += text(x2 + bw / 2, cy + 24, "Запрограмовано", 13, BLUE, "middle", "bold")
    s += text(x2 + bw / 2, cy + 44, "у потрібні комірки", 9.5, GREY, "middle")
    s += text(x2 + bw / 2, cy + 58, "вкладено заряд", 9.5, GREY, "middle")
    s += text(x2 + bw / 2, cy + 80, "є й 0, і 1 — це програма", 9.5, INK, "middle", "bold")

    # ── стрілка вниз: працює в схемі ──
    s += arrow(x2 + bw / 2, cy + bh, x2 + bw / 2, cy + bh + 52, GREEN, 2.2)
    s += text(x2 + bw / 2 + 8, cy + bh + 32, "процесор читає код", 10, GREEN, "start", "bold")
    s += rect(x2 - 14, cy + bh + 60, bw + 28, 40, "#f4f7f4", GREEN, 1.6, 8)
    s += text(x2 + bw / 2, cy + bh + 85, "тримає дані роками без живлення (нелетка)",
              9.5, INK, "middle")

    # ── стрілка: стирання (УФ) ──
    s += arrow(x2 + bw, cy + bh / 2, x2 + bw + 96, cy + bh / 2, VIOLET, 2.6)
    s += text(x2 + bw + 48, cy + bh / 2 - 12, "СТИРАННЯ", 11, VIOLET, "middle", "bold")
    s += text(x2 + bw + 48, cy + bh / 2 + 22, "~20 хв УФ", 9, GREY, "middle")

    # ── стан 3: УФ крізь кварцове віконце ──
    x3 = x2 + bw + 96
    pw = 210
    s += rect(x3, cy - 6, pw, bh + 12, "#faf6fd", VIOLET, 2.2, 10)
    s += text(x3 + pw / 2, cy + 18, "Кварцове віконце + УФ-лампа", 11.5, VIOLET, "middle", "bold")
    # корпус чипа з прозорим віконцем
    chip_x, chip_y = x3 + 26, cy + 40
    s += rect(chip_x, chip_y, pw - 52, 40, "#e9e2ef", INK, 1.8, 4)
    s += circle(chip_x + (pw - 52) / 2, chip_y + 20, 13, "#ffffff", VIOLET, 2)
    s += text(chip_x + (pw - 52) / 2, chip_y + 24, "кварц", 8, VIOLET, "middle", "bold")
    # промені УФ згори
    for i in range(5):
        rx = chip_x + 18 + i * ((pw - 52 - 36) / 4)
        s += arrow(rx, cy + 2, rx, chip_y - 2, VIOLET, 1.8)
    s += text(x3 + pw / 2, cy - 14, "ультрафіолет", 9.5, VIOLET, "middle", "bold")
    s += text(x3 + pw / 2, cy + bh + 4, "світло вибиває заряд — увесь чип знову чистий",
              9, GREY, "middle", style="italic")

    # ── повернення до стану 1 ──
    s += arrow(x3 + pw / 2, cy + bh + 16, x3 + pw / 2, cy + bh + 70, VIOLET, 2)
    s += arrow(x3 + pw / 2, cy + bh + 70, x1 + bw / 2, cy + bh + 70, VIOLET, 2)
    s += line(x1 + bw / 2, cy + bh + 70, x1 + bw / 2, cy + bh, VIOLET, 2, dash="5,4")
    s += arrow(x1 + bw / 2, cy + bh + 6, x1 + bw / 2, cy + bh, VIOLET, 2)
    s += text((x1 + bw / 2 + x3 + pw / 2) / 2, cy + bh + 64,
              "знову чисто → можна прошивати наново", 10, VIOLET, "middle", "bold")

    # нижня плашка-висновок
    s += rect(60, 392, W - 120, 60, "#faf6fd", VIOLET, 1.8, 10)
    s += text(W / 2, 416, "Уперше пам'ять-ROM стала БАГАТОРАЗОВОЮ: помилку в програмі можна було стерти й перепрошити той самий чип.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 438, "Асиметрія назавжди: запис — точковий і електричний; стирання — грубе, оптичне, лише цілим чипом. Цей слід дожив до Flash.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-8h-2-cycle.svg", s)


# ═══════════ Рис. 3.6.8i.3 — чому стирання змінило розробку: цикл проти масок ══
def fig_flow():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 32, "Чому віконце змінило інженерію: ітерація замість «один постріл»",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "до EPROM прошивку «впікали» в чип масками на фабриці — помилка означала новий чип і тижні чекання",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: маскова ROM (старий світ) ──
    lx = 90
    s += text(lx + 130, 92, "Маскова ROM (до EPROM)", 13.5, RED, "middle", "bold")
    steps_old = [
        ("написати програму", INK),
        ("замовити маски на фабриці", GREY),
        ("чекати тижні, платити дорого", GREY),
        ("отримати чипи з «вкарбованим» кодом", INK),
        ("знайшли баг? усе — на смітник,", RED),
        ("починай спочатку", RED),
    ]
    yy = 116
    for i, (t, c) in enumerate(steps_old):
        s += rect(lx, yy, 260, 30, "#fdf4f4" if c == RED else "#f6f6f6",
                  RED if c == RED else GREY, 1.4, 6)
        s += text(lx + 130, yy + 20, t, 10.5, c, "middle",
                  "bold" if c == RED else "normal")
        if i < len(steps_old) - 1:
            s += arrow(lx + 130, yy + 30, lx + 130, yy + 38, GREY, 1.6)
        yy += 44
    # петля болю назад нагору
    s += polyline([(lx, yy - 44 + 15), (lx - 26, yy - 44 + 15),
                   (lx - 26, 116 + 15), (lx, 116 + 15)], RED, 2, dash="5,4")
    s += arrow(lx - 4, 116 + 15, lx + 4, 116 + 15, RED, 2)
    s += text(lx - 30, (116 + yy - 44) / 2 + 15, "новий", 9, RED, "end", "bold")
    s += text(lx - 30, (116 + yy - 44) / 2 + 27, "цикл", 9, RED, "end", "bold")
    s += text(lx + 130, yy + 6, "дорого й повільно помилятися", 10, RED, "middle", style="italic")

    # ── праворуч: EPROM (новий світ) ──
    rx = 590
    s += text(rx + 130, 92, "EPROM (із віконцем)", 13.5, GREEN, "middle", "bold")
    steps_new = [
        ("прошити чип у себе на столі", INK),
        ("спробувати в схемі", INK),
        ("знайшли баг — виправити код", AMBER),
        ("стерти УФ за 20 хв", VIOLET),
        ("прошити той самий чип знову", GREEN),
    ]
    yy = 116
    boxes = []
    for i, (t, c) in enumerate(steps_new):
        bg = "#faf6fd" if c == VIOLET else ("#f4f7f4" if c == GREEN else "#f6f6f6")
        s += rect(rx, yy, 260, 30, bg, c if c in (GREEN, VIOLET, AMBER) else GREY, 1.5, 6)
        s += text(rx + 130, yy + 20, t, 10.5, c, "middle",
                  "bold" if c in (GREEN, VIOLET, AMBER) else "normal")
        boxes.append(yy)
        if i < len(steps_new) - 1:
            s += arrow(rx + 130, yy + 30, rx + 130, yy + 38, GREY, 1.6)
        yy += 44
    # швидка петля назад (дешева)
    s += polyline([(rx + 260, boxes[-1] + 15), (rx + 286, boxes[-1] + 15),
                   (rx + 286, boxes[0] + 15), (rx + 260, boxes[0] + 15)],
                  GREEN, 2.2)
    s += arrow(rx + 264, boxes[0] + 15, rx + 256, boxes[0] + 15, GREEN, 2.2)
    s += text(rx + 290, (boxes[0] + boxes[-1]) / 2 + 15, "хвилини,", 9, GREEN, "start", "bold")
    s += text(rx + 290, (boxes[0] + boxes[-1]) / 2 + 27, "безкоштовно", 9, GREEN, "start", "bold")
    s += text(rx + 130, yy + 6, "дешево й швидко помилятися = швидше вчитися", 10, GREEN, "middle", style="italic")

    # стрілка-перехід посередині
    s += arrow(lx + 260 + 14, 250, rx - 14, 250, INK, 2.6)
    s += text((lx + 260 + rx) / 2, 238, "EPROM", 12, INK, "middle", "bold")

    # нижня плашка
    s += rect(60, 404, W - 120, 52, "#f4f7f4", GREEN, 1.8, 10)
    s += text(W / 2, 428, "EPROM перетворила прошивку на те, що можна правити ітераціями — і саме це пришвидшило весь ранній світ мікропроцесорів.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 448, "Чип з віконцем став робочим інструментом інженера: «прошити → спробувати → стерти → прошити знову».",
              10.5, GREY, "middle", style="italic")
    save("fig-19-8h-3-flow.svg", s)


# ═══════════ Рис. 3.6.8i.4 — родовід плавучого затвора (колективна атрибуція) ═══
def fig_lineage():
    W, H = 960, 430
    s = header(W, H)
    s += text(W / 2, 32, "Родовід плавучого затвора: ідея, перший чип, спадкоємці",
              19, INK, "middle", "bold")
    s += text(W / 2, 54, "EPROM не виник із порожнечі — це ланка довшого ланцюга, де кожен крок додав своє (колективна історія, не один герой)",
              11.5, GREY, "middle", style="italic")

    cy = 150
    bw, bh = 200, 120

    nodes = [
        (60, "#f7f9fc", BLUE, "1967 — ідея",
         "Канг і Це (Bell Labs)",
         ["плавучий затвор як", "комірка пам'яті —", "на папері; робочого", "чипа ще немає"]),
        (290, "#fdf4f4", RED, "1971 — перший чип",
         "Дов Фроман (Intel)",
         ["FAMOS + Intel 1702:", "робоча EPROM 2 Кбіт;", "стирання УФ крізь", "кварцове віконце"]),
        (520, "#f4f7f4", GREEN, "кінець 1970-х",
         "EEPROM",
         ["стирання вже", "ЕЛЕКТРИКОЮ, не УФ;", "віконце зникає,", "можна по байту"]),
        (750, "#fff8e8", AMBER, "1980-ті →",
         "Flash",
         ["той самий принцип,", "стирання блоками,", "дешево й щільно —", "у вашому МК (§3.6.8)"]),
    ]
    for x, fill, col, when, who, lines in nodes:
        s += rect(x, cy, bw, bh, fill, col, 2.2, 12)
        s += text(x + bw / 2, cy + 24, when, 12.5, col, "middle", "bold")
        s += text(x + bw / 2, cy + 44, who, 12, INK, "middle", "bold")
        for j, ln in enumerate(lines):
            s += text(x + bw / 2, cy + 64 + j * 14.5, ln, 9.8, GREY, "middle")

    # стрілки між вузлами
    for x in [60, 290, 520]:
        s += arrow(x + bw, cy + bh / 2, x + bw + 30, cy + bh / 2, INK, 2.4)

    # що саме додав кожен крок (під стрілками)
    adds = [
        (250, "ідея → залізо"),
        (480, "УФ → струм"),
        (710, "байт → блоки,\nдешевше"),
    ]
    for x, t in adds:
        parts = t.split("\n")
        for k, p in enumerate(parts):
            s += text(x, cy + bh / 2 - 10 + k * 13, p, 9, INK, "middle", "bold")

    # підкреслення тези внизу
    s += rect(60, cy + bh + 36, W - 120, 64, "#f7f9fc", BLUE, 1.8, 10)
    s += text(W / 2, cy + bh + 60,
              "Теза §10: велике — то праця багатьох. Концепцію дали Канг і Це; робочу, придатну пам'ять із віконцем — Фроман;",
              11.5, INK, "middle", "bold")
    s += text(W / 2, cy + bh + 82,
              "далі EEPROM прибрав віконце, а Flash здешевив усе. EPROM — серединна, але вирішальна ланка: перша, що справді запрацювала.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-8h-4-lineage.svg", s)


if __name__ == "__main__":
    fig_famos()
    fig_cycle()
    fig_flow()
    fig_lineage()
    print("done.")
