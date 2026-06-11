# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 4.3 — «Постійні дані: Flash-розділи, NVS і файлові системи» (Модуль 4).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; стрілки через marker; sans-serif.
Підписи нумеруються посекційно (Рис. 4.3.S.N); для історії до розділу — секція 0 (Рис. 4.3.0.N).
Імена файлів: fig-r03-S-N-<slug>.svg.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
LRED = "#fbecec"
LBLUE = "#e9eefb"
LGRN = "#eef6ef"
LAMB = "#fff6e0"
METAL = "#9a9aa0"
GOLD = "#caa24a"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" '
        f'markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" '
        f'markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" '
        f'markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" '
        f'markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" '
        f'markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


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


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def blk(x, y, w, h, label, sub="", fill="#ffffff", stroke=INK, lcol=INK):
    o = rect(x, y, w, h, fill, stroke, 1.8, 6)
    if sub:
        o += text(x + w / 2, y + h / 2 - 3, label, 12.5, lcol, "middle", "bold")
        o += text(x + w / 2, y + h / 2 + 13, sub, 10, GREY, "middle")
    else:
        o += text(x + w / 2, y + h / 2 + 4, label, 12.5, lcol, "middle", "bold")
    return o


def blk2(x, y, w, h, label, sublines, fill="#ffffff", stroke=INK, lcol=INK):
    o = rect(x, y, w, h, fill, stroke, 1.8, 8)
    o += text(x + w / 2, y + 24, label, 12.5, lcol, "middle", "bold")
    for i, ln in enumerate(sublines):
        o += text(x + w / 2, y + 42 + i * 15, ln, 9.6, GREY, "middle")
    return o


def _tint(col):
    return {RED: LRED, GREEN: LGRN, BLUE: LBLUE, GOLD: LAMB}.get(col, "#eef0f5")


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 4.3.0.1 — пам'ять до Flash: прогалина, яку він закрив ────────────────
def fig01_memory_gap():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Пам'ять до Flash: кожна щось та й не вміла", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "усім бракувало одного — швидко стиратися й переписуватися електрично, дешево й щільно",
              11, GREY, "middle", style="italic")
    cols = [("властивість", 70), ("RAM", 330), ("ROM", 450), ("EPROM", 580), ("EEPROM", 710), ("FLASH", 850)]
    for nm, x in cols:
        s += text(x, 96, nm, 10.5, (GREEN if nm == "FLASH" else INK), "middle" if x != 70 else "start", "bold")
    s += line(50, 106, 900, 106, FAINT, 1.4)
    rows = [
        ("пам'ятає без живлення?", ["ні", "так", "так", "так", "так"]),
        ("можна переписати?", ["так", "ні", "УФ-стирання", "побайтово", "блоками, електрично"]),
        ("щільна / дешева?", ["—", "так", "так", "ні (дорога)", "так"]),
        ("зручна в роботі?", ["так", "—", "ні (виймати, УФ)", "так, та повільна", "так"]),
    ]
    xs = [330, 450, 580, 710, 850]
    for i, (prop, vals) in enumerate(rows):
        y = 134 + i * 50
        s += rect(50, y - 20, 850, 42, "#fcfcfc" if i % 2 == 0 else "#f5f7fb", FAINT, 1, 6)
        s += text(70, y + 5, prop, 10, INK, "start")
        for x, v in zip(xs, vals):
            good = v in ("так", "блоками, електрично")
            col = GREEN if (x == 850) else (INK if good else GREY)
            s += text(x, y + 5, v, 9 if len(v) > 6 else 10, col, "middle", "bold" if x == 850 else "normal")
    s += rect(660, 344, 240, 56, LGRN, GREEN, 1.6, 10)
    s += text(780, 366, "Flash закрив прогалину:", 10.5, GREEN, "middle", "bold")
    s += text(780, 384, "як EEPROM, але дешевий і щільний", 9.3, INK, "middle")
    save("fig-r03-0-1-memory-gap.svg", s)


# ── Рис. 4.3.0.2 — NOR (1984) проти NAND (1987) ──────────────────────────────
def fig02_nor_nand():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 32, "Два різновиди Flash: NOR (1984) і NAND (1987)", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "обидва від Масуоки в Toshiba — і обидва досі визначають увесь ландшафт пам'яті",
              11, GREY, "middle", style="italic")
    s += rect(60, 90, 360, 250, "#f4f7fb", BLUE, 2, 12)
    s += text(240, 116, "NOR (1984)", 14, BLUE, "middle", "bold")
    for i, t in enumerate(["довільний доступ до байта", "швидке читання", "виконання коду «на місці» (XIP)",
                           "→ програмна пам'ять чипів"]):
        s += text(82, 150 + i * 38, "• " + t, 10.5, INK, "start")
    s += text(240, 320, "Flash вашого ESP32 — цього роду", 9.3, BLUE, "middle", style="italic")
    s += rect(500, 90, 360, 250, "#fbfdfb", GREEN, 2, 12)
    s += text(680, 116, "NAND (1987)", 14, GREEN, "middle", "bold")
    for i, t in enumerate(["доступ блоками, не байтом", "набагато щільніша й дешевша", "ідеальна під великі обсяги",
                           "→ SD-картки, флешки, SSD"]):
        s += text(522, 150 + i * 38, "• " + t, 10.5, INK, "start")
    s += text(680, 320, "те, на чому лежать ваші файли", 9.3, GREEN, "middle", style="italic")
    s += rect(160, 356, 600, 44, LAMB, GOLD, 1.4, 10)
    s += text(460, 380, "NOR — щоб виконувати код; NAND — щоб зберігати гори даних. Поділ живий донині.",
              10, INK, "middle", "bold")
    save("fig-r03-0-2-nor-nand.svg", s)


# ── Рис. 4.3.0.3 — хто винайшов і хто зібрав плоди ───────────────────────────
def fig03_credit():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Винайшли в Toshiba — а слава й гроші розійшлися", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "класична історія: інженер створив проривну річ, а визнання прийшло криво й пізно",
              11, GREY, "middle", style="italic")
    s += blk2(60, 110, 250, 110, "Toshiba (Японія)", ["Фудзіо Масуока — винахідник;", "Сьодзі Аріідзумі назвав «flash»;",
                                                       "компанія скупо віддячила"], fill=LGRN, stroke=GREEN, lcol=GREEN)
    s += blk2(360, 110, 250, 110, "Intel (США)", ["підхопила NOR-flash і першою", "агресивно її комерціалізувала",
                                                   "(чип на 256 Кбіт, 1988)"], fill=LBLUE, stroke=BLUE, lcol=BLUE)
    s += blk2(660, 110, 200, 110, "Масуока згодом", ["судився з Toshiba за", "винагороду; став", "професором (Тохоку)"],
              fill=LRED, stroke=RED, lcol=RED)
    s += arrow(310, 150, 360, 150, INK, 2)
    s += arrow(610, 165, 660, 165, INK, 2)
    s += rect(110, 250, 700, 64, "#fbfbfb", GREY, 1.4, 10)
    s += text(460, 274, "Чесно: винахід — Масуоки й Аріідзумі (Toshiba); масовий ринок розкрутили й інші.",
              10.5, INK, "middle", "bold")
    s += text(460, 294, "Назвати справжнього автора — не дрібниця, а точність, якої вимагає інженерна культура.",
              9.8, GREY, "middle")
    s += text(460, 340, "Той самий візерунок «винайшов тут — нагороду деінде» ми вже бачили не раз.",
              9.5, GREY, "middle", style="italic")
    save("fig-r03-0-3-credit.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §4.3.1 — Навіщо зберігати: конфігурація, калібрування, логи
# ─────────────────────────────────────────────────────────────────────────────

def fig11_volatile_loss():
    W, H = 920, 416
    s = header(W, H)
    s += text(W / 2, 32, "Чому без постійного сховища пристрій безпорадний", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "SRAM забуває все при вимкненні — та не все можна втрачати", 11, GREY, "middle", style="italic")
    s += rect(60, 86, 340, 300, "#fbfdfb", GREEN, 2, 12)
    s += text(230, 112, "До вимкнення (у SRAM)", 12, GREEN, "middle", "bold")
    items = [("поточне значення 21.7°", "transient", GREY), ("Wi-Fi пароль", "конфіг", RED),
             ("поправка давача −0.4°", "калібрування", RED), ("журнал помилок", "лог", RED)]
    for i, (t, tag, c) in enumerate(items):
        y = 148 + i * 56
        s += text(82, y, "• " + t, 10.5, INK, "start")
        s += text(94, y + 17, "(" + tag + ")", 9, c, "start", "bold")
    s += text(460, 196, "⚡", 30, RED, "middle")
    s += text(460, 228, "вимк / увімк", 9.5, RED, "middle", "bold")
    s += arrow(405, 208, 515, 208, RED, 2.4)
    s += rect(520, 86, 340, 300, "#fffafa", RED, 2, 12)
    s += text(690, 112, "Після ввімкнення", 12, RED, "middle", "bold")
    after = [("поточне — пораховано наново", "ок, не шкода", GREEN), ("Wi-Fi пароль — ЗНИК", "знову вводити", RED),
             ("поправка — ЗНИКЛА", "давач бреше", RED), ("журнал — ПОРОЖНІЙ", "нема діагнозу", RED)]
    for i, (t, note, c) in enumerate(after):
        y = 148 + i * 56
        s += text(542, y, "• " + t, 10, INK, "start")
        s += text(554, y + 17, "→ " + note, 9, c, "start", "bold")
    save("fig-r03-1-1-volatile-loss.svg", s)


def fig12_three_kinds():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Три роди постійних даних", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "що зберігаємо й чому — конфігурація, калібрування, логи", 11, GREY, "middle", style="italic")
    cards = [
        (36, "Конфігурація", BLUE, ["налаштування пристрою", "напр.: Wi-Fi, ім'я, режим", "пише — юзер, зрідка",
                                    "читає — часто", "втрата → переналаштувати"]),
        (342, "Калібрування", GREEN, ["поправки САМЕ цього", "екземпляра (offset/gain)", "пише — раз (завод/setup)",
                                      "читає — постійно", "втрата → давач бреше"]),
        (648, "Логи", GOLD, ["запис подій у часі", "помилки, виміри, історія", "пише — дописує часто",
                             "читає — для діагнозу", "втрата → нема «чорної скриньки»"]),
    ]
    for x, title, c, lines in cards:
        s += rect(x, 88, 270, 296, "#fcfcfc", c, 2, 12)
        s += text(x + 135, 118, title, 14, c, "middle", "bold")
        s += line(x + 24, 130, x + 246, 130, c, 1.3)
        for i, ln in enumerate(lines):
            s += text(x + 22, 160 + i * 44, "• " + ln, 10, INK, "start")
    save("fig-r03-1-2-three-kinds.svg", s)


def fig13_write_read():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Чому їм потрібні різні сховища: пишуть і читають по-різному", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "частота запису й читання та зростання — ось що вирішує вибір механізму", 11, GREY, "middle", style="italic")
    cols = [("рід даних", 70), ("як часто ПИШЕ", 360), ("як часто ЧИТАЄ", 560), ("росте?", 760)]
    for nm, x in cols:
        s += text(x, 104, nm, 10.5, INK, "middle" if x != 70 else "start", "bold")
    s += line(50, 114, 850, 114, FAINT, 1.4)
    rows = [
        ("Калібрування", "раз (write-once)", "постійно", "ні (дрібне)", GREEN),
        ("Конфігурація", "зрідка", "часто", "ні (мале)", BLUE),
        ("Логи", "часто (дописує)", "зрідка", "ТАК, весь час", GOLD),
    ]
    for i, (nm, w, r, g, c) in enumerate(rows):
        y = 138 + i * 64
        s += rect(50, y, 800, 54, _tint(c), c, 1.6, 10)
        s += text(70, y + 32, nm, 12.5, c, "start", "bold")
        s += text(360, y + 32, w, 10, INK, "middle")
        s += text(560, y + 32, r, 10, INK, "middle")
        s += text(760, y + 32, g, 10, (RED if "ТАК" in g else INK), "middle", "bold" if "ТАК" in g else "normal")
    s += rect(120, 344, 660, 40, LAMB, GOLD, 1.4, 10)
    s += text(450, 368, "Звідси й різні сховища: дрібне «ключ–значення» — одне, журнал, що росте, — інше.",
              10, INK, "middle", "bold")
    save("fig-r03-1-3-write-read.svg", s)


def fig14_where_goes():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Куди що лягає (попередній погляд на розділ)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "форма даних диктує сховище — деталі попереду в темах розділу", 11, GREY, "middle", style="italic")
    s += blk2(70, 110, 240, 80, "Конфігурація", ["дрібні налаштування"], fill=LBLUE, stroke=BLUE, lcol=BLUE)
    s += blk2(70, 210, 240, 80, "Калібрування", ["кілька чисел-поправок"], fill=LGRN, stroke=GREEN, lcol=GREEN)
    s += arrow(310, 150, 470, 178, INK, 2)
    s += arrow(310, 250, 470, 200, INK, 2)
    s += blk2(470, 150, 360, 80, "NVS — сховище «ключ–значення»", ["мале, швидке, надійне (§4.3.5)"],
              fill=LAMB, stroke=GOLD, lcol="#8a6d1a")
    s += blk2(70, 300, 240, 46, "Логи / великі дані", [], fill="#fff3e0", stroke=GOLD, lcol="#8a6d1a")
    s += arrow(310, 322, 470, 290, INK, 2)
    s += blk2(470, 256, 360, 88, "Файлова система / кільцевий лог", ["LittleFS, SD-картка (§4.3.6),", "кільце у Flash"],
              fill="#fbfbfb", stroke=GREY, lcol=INK)
    save("fig-r03-1-4-where-goes.svg", s)


def fig15_thermostat():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Приклад: термостат — що зберігати, а що ні", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "переживати вимкнення мусить не все — лише те, чого не відновити заново", 11, GREY, "middle", style="italic")
    s += rect(330, 92, 260, 70, "#f4f7fb", INK, 2, 12)
    s += text(460, 122, "Термостат", 13, INK, "middle", "bold")
    s += text(460, 142, "що тримати в голові?", 9.5, GREY, "middle")
    s += text(250, 200, "ЗБЕРЕГТИ (переживає вимкнення):", 10.5, GREEN, "start", "bold")
    for i, (t, tag, c, x) in enumerate([("задана t° = 22°", "конфіг", BLUE, 0), ("поправка давача −0.4°", "калібрування", GREEN, 0),
                                        ("журнал збоїв", "лог", GOLD, 0)]):
        y = 226 + i * 34
        s += circle(266, y - 4, 6, _tint(c), c, 1.6)
        s += text(284, y, t, 10.5, INK, "start")
        s += text(560, y, "(" + tag + ")", 9, c, "start", "bold")
    s += rect(250, 332, 420, 50, LRED, RED, 1.4, 10)
    s += text(460, 354, "НЕ зберігати: поточна t° = 21.7° — її щоразу", 10, INK, "middle", "bold")
    s += text(460, 372, "міряють наново, тож тримати її у Flash нема сенсу.", 9.5, GREY, "middle")
    save("fig-r03-1-5-thermostat.svg", s)


def fig16_lifecycle():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Коли що пишуть і читають — за все життя пристрою", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "у кожного роду даних — свій момент запису, а читають їх у роботі", 11, GREY, "middle", style="italic")
    y = 150
    s += line(70, y, 870, y, INK, 2.4)
    stages = [(150, "Завод", "калібрування ✍", GREEN), (370, "Перший запуск", "конфіг ✍", BLUE),
              (590, "Робота", "усе читають; лог ✍", GOLD), (820, "Збій / сервіс", "лог читають", RED)]
    for x, nm, what, c in stages:
        s += circle(x, y, 6, c, c, 0)
        s += line(x, y - 6, x, y - 34, c, 1.4)
        s += rect(x - 95, y - 86, 190, 50, _tint(c), c, 1.6, 8)
        s += text(x, y - 64, nm, 11.5, c, "middle", "bold")
        s += text(x, y - 47, what, 9.3, INK, "middle")
    s += rect(150, 220, 640, 56, "#fbfbfb", GREY, 1.4, 10)
    s += text(470, 244, "Калібрування пишуть РАЗ (на заводі), конфіг — при налаштуванні,", 10, INK, "middle", "bold")
    s += text(470, 263, "лог дописують у роботі. А читають їх усі — поки пристрій живе.", 9.8, GREY, "middle")
    save("fig-r03-1-6-lifecycle.svg", s)


def _bits(x, y, bits, col=INK, cw=30, ch=34):
    o = ""
    for i, b in enumerate(bits):
        cx = x + i * (cw + 4)
        on = (b == 0)
        o += rect(cx, y, cw, ch, _tint(col) if on and col != INK else "#ffffff", col, 1.4, 3)
        o += text(cx + cw / 2, y + ch * 0.68, str(b), 14, col, "middle", "bold")
    return o


# ─────────────────────────────────────────────────────────────────────────────
#  §4.3.2 — Flash зсередини: сторінки, сектори, стирання перед записом
# ─────────────────────────────────────────────────────────────────────────────

def fig21_erase_write():
    W, H = 920, 412
    s = header(W, H)
    s += text(W / 2, 32, "Головне правило Flash: спершу стерти, тоді писати", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "запис уміє лише гасити біти (1→0); підняти 0→1 можна тільки стиранням",
              11, GREY, "middle", style="italic")
    s += text(80, 108, "1. Стерто — усі одиниці (0xFF):", 11, GREEN, "start", "bold")
    s += _bits(80, 120, [1, 1, 1, 1, 1, 1, 1, 1], GREEN)
    s += text(80, 196, "2. Записали 0x52 — погасили частину бітів у 0:", 11, BLUE, "start", "bold")
    s += _bits(80, 208, [0, 1, 0, 1, 0, 0, 1, 0], BLUE)
    s += text(360, 226, "← запис рухає біти ЛИШЕ в один бік: 1→0", 10, GREY, "start")
    s += text(80, 290, "3. Хочемо 0x53? Треба підняти біт 0→1 — запис НЕ вміє:", 11, RED, "start", "bold")
    s += _bits(80, 302, [0, 1, 0, 1, 0, 0, 1, 1], RED)
    s += text(360, 320, "← цей біт 0→1 неможливий без стирання", 10, RED, "start", "bold")
    s += rect(360, 110, 500, 64, LGRN, GREEN, 1.6, 10)
    s += text(610, 134, "Запис: тільки 1→0 (гасити).", 11, INK, "middle", "bold")
    s += text(610, 154, "Стирання: усе назад у 1 — і лише цілим сектором.", 10, GREY, "middle")
    save("fig-r03-2-1-erase-write.svg", s)


def fig22_granularity():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Асиметрія: писати дрібно, стирати гуртом", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "запис — по сторінці (~256 Б); стирання — лише цілим сектором (~4 КБ)",
              11, GREY, "middle", style="italic")
    s += rect(80, 100, 760, 150, "#fbfdff", INK, 2.2, 12)
    s += text(100, 122, "Сектор (~4 КБ) = багато сторінок", 11, INK, "start", "bold")
    for i in range(16):
        x = 100 + i * 46
        fill = LGRN if i == 5 else "#ffffff"
        st = GREEN if i == 5 else FAINT
        s += rect(x, 140, 42, 90, fill, st, 1.6 if i == 5 else 1, 4)
    s += text(100 + 5 * 46 + 21, 188, "↓", 14, GREEN, "middle", "bold")
    s += text(100 + 5 * 46 + 21, 256, "пишемо сюди", 8.3, GREEN, "middle", "bold")
    s += text(100 + 5 * 46 + 21, 268, "(1 сторінка)", 8.3, GREEN, "middle")
    s += arrow(300, 300, 300, 252, GREEN, 2)
    s += text(300, 318, "ЗАПИС торкається однієї сторінки", 10, GREEN, "middle", "bold")
    s += arrow(640, 300, 640, 252, RED, 2)
    s += text(640, 318, "СТИРАННЯ змітає весь сектор", 10, RED, "middle", "bold")
    s += text(640, 334, "(усі 16 сторінок одразу)", 9, RED, "middle")
    save("fig-r03-2-2-granularity.svg", s)


def fig23_hierarchy():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Одиниці Flash: від байта до блоку", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "орієнтовні розміри для типового NOR-Flash; у NAND вони більші", 11, GREY, "middle", style="italic")
    rows = [
        ("Байт / слово", "1–4 Б", "найдрібніше, чим оперуєш", GREY),
        ("Сторінка (page)", "~256 Б", "найменша одиниця ЗАПИСУ", BLUE),
        ("Сектор (sector)", "~4 КБ", "найменша одиниця СТИРАННЯ", GREEN),
        ("Блок (block)", "~64 КБ", "більший блок стирання", GOLD),
    ]
    for i, (nm, sz, note, c) in enumerate(rows):
        y = 96 + i * 68
        w = 360 + i * 130
        s += rect((W - w) / 2, y, w, 54, _tint(c), c, 1.8, 10)
        s += text(W / 2, y + 23, nm + "  ·  " + sz, 12.5, c, "middle", "bold")
        s += text(W / 2, y + 42, note, 9.6, INK, "middle")
    s += text(W / 2, 384, "Пишеш сторінками, стираєш секторами — і саме звідси всі примхи поводження з Flash.",
              10, INK, "middle", "bold")
    save("fig-r03-2-3-hierarchy.svg", s)


def fig24_update_one_byte():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Скільки коштує змінити ОДИН байт", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "не можна просто перезаписати — доводиться переписати цілий сектор",
              11, GREY, "middle", style="italic")
    steps = [
        ("1", "Прочитати весь сектор у RAM", "усі 4 КБ", BLUE),
        ("2", "Змінити потрібний байт у RAM", "1 байт", GREEN),
        ("3", "СТЕРТИ сектор у Flash", "усе → 0xFF", RED),
        ("4", "Записати сектор назад", "4 КБ із правкою", BLUE),
    ]
    for i, (n, t, d, c) in enumerate(steps):
        y = 92 + i * 66
        s += circle(110, y + 22, 17, _tint(c), c, 2)
        s += text(110, y + 27, n, 14, c, "middle", "bold")
        s += rect(150, y, 600, 46, _tint(c), c, 1.6, 10)
        s += text(172, y + 22, t, 12, c, "start", "bold")
        s += text(172, y + 39, d, 9.3, INK, "start")
        if i < 3:
            s += arrow(110, y + 39, 110, y + 66, INK, 1.8)
    s += rect(150, 360, 600, 34, LRED, RED, 1.4, 8)
    s += text(450, 382, "Змінити 1 байт = переписати 4096. Ще й небезпечно: вимкнення між 3 і 4 = втрата сектора.",
              9.5, INK, "middle", "bold")
    save("fig-r03-2-4-update-one-byte.svg", s)


def fig25_clear_only():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 32, "Хитрість зі стирання-в-один-бік: дописувати без стирання", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "поки в сторінці лишаються одиниці, можна гасити нові біти — і це безкоштовно",
              11, GREY, "middle", style="italic")
    s += rect(70, 100, 780, 140, "#fbfdff", INK, 2, 12)
    s += text(90, 124, "Стерта сторінка (усе 1) — пишемо записи один за одним, гасячи біти:", 10, INK, "start")
    recs = [("запис A", LGRN, GREEN), ("A — недійсний", LRED, RED), ("запис B", LGRN, GREEN),
            ("запис C", LGRN, GREEN), ("вільно (усе 1)", "#ffffff", FAINT)]
    x = 96
    for t, fill, st in recs:
        w = 150 if t != "вільно (усе 1)" else 160
        s += rect(x, 150, w, 56, fill, st, 1.6, 6)
        s += text(x + w / 2, 182, t, 9.8, (st if st != FAINT else GREY), "middle", "bold")
        x += w + 8
    s += text(90, 226, "«недійсний» = погасили ще один біт-прапорець (1→0), стирати не довелося.", 9.3, GREY, "start")
    s += rect(120, 268, 680, 92, LAMB, GOLD, 1.6, 10)
    s += text(460, 292, "Звідси два прийоми, що ховаються в NVS і логах:", 11, "#8a6d1a", "middle", "bold")
    s += text(460, 314, "• новий запис — ДОПИСати в незаймане місце (а не переписувати старе);", 10, INK, "middle")
    s += text(460, 333, "• скасувати старий — погасити його прапорець; стерти лише коли сторінка повна.", 10, INK, "middle")
    s += text(460, 351, "Так стирання — рідкісне, а отже й знос менший (§4.3.3, §4.3.5).", 9.3, GREY, "middle")
    save("fig-r03-2-5-clear-only.svg", s)


def fig26_why_managers():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Чому майже ніхто не пише у Flash напряму", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "сирі правила легко порушити — тож за вас із ними воює готовий менеджер",
              11, GREY, "middle", style="italic")
    s += rect(60, 96, 360, 200, "#fffafa", RED, 2, 12)
    s += text(240, 122, "Напряму (сирий Flash)", 12, RED, "middle", "bold")
    for i, t in enumerate(["сам стирай перед записом", "сам читай-стирай-переписуй сектор",
                           "сам стеж за зносом", "сам рятуйся від вимкнення", "→ легко зіпсувати дані"]):
        s += text(82, 154 + i * 28, "• " + t, 10, (RED if i == 4 else INK), "start", "bold" if i == 4 else "normal")
    s += rect(480, 96, 360, 200, "#fbfdfb", GREEN, 2, 12)
    s += text(660, 122, "Через NVS / файлову систему", 11.5, GREEN, "middle", "bold")
    for i, t in enumerate(["просто set(\"ключ\", значення)", "менеджер сам робить весь танець",
                           "сам розкладає знос", "сам береже від збоїв", "→ надійно й просто"]):
        s += text(502, 154 + i * 28, "• " + t, 10, (GREEN if i == 4 else INK), "start", "bold" if i == 4 else "normal")
    s += arrow(420, 196, 480, 196, INK, 2.4)
    save("fig-r03-2-6-why-managers.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §4.3.3 — Зношування комірок і wear leveling
# ─────────────────────────────────────────────────────────────────────────────

def fig31_why_wear():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Чому комірки Flash зношуються", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "кожне стирання й запис прогонить електрони крізь ізолятор — і потроху псує його",
              11, GREY, "middle", style="italic")
    import math
    states = [("Свіжа комірка", "ізолятор цілий,", "заряд тримається роками", GREEN, 170, 0),
              ("Після тисяч циклів", "ізолятор потерто,", "заряд починає текти", GOLD, 460, 5),
              ("Вичерпана", "заряд не тримається —", "біт ненадійний", RED, 750, 12)]
    for nm, l1, l2, c, x, dmg in states:
        s += circle(x, 176, 46, _tint(c), c, 2.4)
        for k in range(dmg):
            a = k * 2.399
            r = 30 * (k / max(1, dmg)) ** 0.5
            s += circle(x + r * math.cos(a), 176 + r * math.sin(a), 2.2, c, c, 0)
        s += text(x, 256, nm, 12, c, "middle", "bold")
        s += text(x, 276, l1, 9.5, INK, "middle")
        s += text(x, 292, l2, 9.5, GREY, "middle")
    s += arrow(228, 176, 402, 176, INK, 2)
    s += text(315, 164, "тунелювання", 8.5, GREY, "middle")
    s += arrow(518, 176, 692, 176, INK, 2)
    s += text(605, 164, "× тисячі циклів", 8.5, GREY, "middle")
    s += rect(150, 326, 620, 52, LAMB, GOLD, 1.4, 10)
    s += text(460, 349, "Кожен цикл «стерти-записати» трохи руйнує ізоляцію затвора.", 10, INK, "middle", "bold")
    s += text(460, 368, "Звідси — скінченна кількість циклів, яку звуть endurance.", 9.5, GREY, "middle")
    save("fig-r03-3-1-why-wear.svg", s)


def fig32_endurance():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Скільки циклів витримує комірка (endurance)", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "орієнтовно, на один СЕКТОР (одиницю стирання) — і число це скінченне",
              11, GREY, "middle", style="italic")
    rows = [
        ("NOR-Flash (код у чипі)", "~100 000 циклів", "багато, та не безкінечно", GREEN),
        ("NAND (картки, SSD)", "~10 000 – 100 000", "менше, бо щільніша", BLUE),
        ("Багатобітові комірки (MLC/TLC)", "одиниці тисяч", "ще менше: біт у бік щільності", GOLD),
        ("FRAM (для лічильників)", "~10¹² і більше", "практично без зносу (§4.3.3)", RED),
    ]
    for i, (nm, num, note, c) in enumerate(rows):
        y = 92 + i * 60
        s += rect(60, y, 780, 50, _tint(c), c, 1.6, 10)
        s += text(80, y + 30, nm, 11.5, c, "start", "bold")
        s += text(470, y + 30, num, 12, INK, "middle", "bold")
        s += text(700, y + 30, note, 9, GREY, "middle")
    s += text(W / 2, 348, "Число — на сектор: стер сектор 100 000 разів — і він починає збоїти.", 9.6, INK, "middle", "bold")
    save("fig-r03-3-2-endurance.svg", s)


def _flash_grid(x0, y0, cols, rows, wear, cw=30, gap=4):
    o = ""
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            w = wear.get(i, 0)
            if w >= 3:
                fill, st = LRED, RED
            elif w == 2:
                fill, st = LAMB, GOLD
            elif w == 1:
                fill, st = LGRN, GREEN
            else:
                fill, st = "#ffffff", FAINT
            o += rect(x0 + c * (cw + gap), y0 + r * (cw + gap), cw, cw, fill, st, 1.2, 3)
    return o


def fig33_hotspot():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Пастка: завжди писати в той самий сектор", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "оновлюєш дані «на місці» — і вбиваєш ОДИН сектор, поки решта чипа незаймана",
              11, GREY, "middle", style="italic")
    wear = {15: 4}
    s += _flash_grid(120, 110, 8, 5, wear)
    s += arrow(120 + 7 * 34 + 15, 96, 120 + 7 * 34 + 15, 108, RED, 2)
    s += text(120 + 7 * 34 + 15, 90, "сюди щоразу", 8.5, RED, "middle", "bold")
    s += rect(560, 130, 300, 170, "#fffafa", RED, 1.8, 12)
    s += text(710, 158, "Що стається:", 11.5, RED, "middle", "bold")
    for i, t in enumerate(["• цей сектор стерто 100 000 разів", "• він почав збоїти — дані гинуть",
                           "• а 39 сусідів — як нові", "• чіп «помер» на 1/40 ресурсу"]):
        s += text(580, 188 + i * 26, t, 10, INK, "start")
    s += text(W / 2, 380, "Класичний приклад — лічильник, що його оновлюють у тому самому місці.", 9.6, INK, "middle", "bold")
    save("fig-r03-3-3-hotspot.svg", s)


def fig34_wear_leveling():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Wear leveling: розкласти знос рівно по всіх секторах", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "не довбати один сектор, а писати по черзі в усі — тоді чіп служить у рази довше",
              11, GREY, "middle", style="italic")
    s += text(240, 96, "Без вирівнювання", 11, RED, "middle", "bold")
    s += _flash_grid(110, 110, 8, 4, {15: 4})
    s += text(240, 270, "один зношений, решта марнує", 9, GREY, "middle")
    s += text(670, 96, "З вирівнюванням", 11, GREEN, "middle", "bold")
    even = {i: 1 for i in range(32)}
    s += _flash_grid(540, 110, 8, 4, even)
    s += text(670, 270, "усі зношені рівномірно й потроху", 9, GREY, "middle")
    s += rect(150, 300, 600, 76, LGRN, GREEN, 1.6, 10)
    s += text(450, 324, "Замість переписувати той самий сектор — пишемо в наступний вільний,", 10, INK, "middle", "bold")
    s += text(450, 343, "а старий лишаємо «застарілим». Знос лягає на всі сектори порівну —", 10, INK, "middle")
    s += text(450, 361, "і ресурс чипа множиться на їхню кількість.", 10, GREY, "middle")
    save("fig-r03-3-4-wear-leveling.svg", s)


def fig35_math():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Порахуймо строк служби", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "вирівнювання зносу множить ресурс на кількість секторів — і це величезна різниця",
              11, GREY, "middle", style="italic")
    s += rect(180, 86, 540, 46, LAMB, GOLD, 1.4, 10)
    s += text(450, 114, "строк = endurance × сектори ÷ записів за добу", 13, INK, "middle", "bold")
    rows = [
        ("Без вирівнювання (1 сектор)", "100 000 ÷ (10/добу)", "≈ 27 років… для 1 байта", GOLD),
        ("…але всі записи в нього:", "при 10 записах/хв", "≈ кілька місяців — і смерть", RED),
        ("З вирівнюванням (×256 секторів)", "100 000 × 256 ÷ записи", "роки навіть під шквалом", GREEN),
    ]
    for i, (nm, calc, res, c) in enumerate(rows):
        y = 156 + i * 56
        s += rect(80, y, 740, 46, _tint(c), c, 1.4, 8)
        s += text(100, y + 28, nm, 10.5, c, "start", "bold")
        s += text(430, y + 28, calc, 10, INK, "middle")
        s += text(700, y + 28, res, 9.5, c, "middle", "bold")
    s += text(W / 2, 348, "Висновок: частота записів вирішує все. Рідше пишеш — довше живе, хоч скільки секторів.",
              9.6, INK, "middle", "bold")
    save("fig-r03-3-5-math.svg", s)


def fig36_practical():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Як не вбити Flash: правила на щодень", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "знос — тиха смерть; кілька звичок рятують пам'ять на роки",
              11, GREY, "middle", style="italic")
    s += rect(60, 90, 380, 240, "#fffafa", RED, 2, 12)
    s += text(250, 116, "НЕ роби", 12.5, RED, "middle", "bold")
    for i, t in enumerate(["оновлювати дані «на місці»", "писати у Flash щосекунди", "вести лічильник у тому ж байті",
                           "лити логи без обмежень", "ігнорувати endurance"]):
        s += text(82, 148 + i * 34, "✗ " + t, 10.5, INK, "start")
    s += rect(460, 90, 380, 240, "#fbfdfb", GREEN, 2, 12)
    s += text(650, 116, "Роби", 12.5, GREEN, "middle", "bold")
    for i, t in enumerate(["довір NVS / ФС вирівнювання", "тримай гаряче в RAM, скидай зрідка",
                           "групуй і відкладай записи", "обмеж лог кільцем (§4.3.1)", "для лічильників — FRAM (§4.3.3)"]):
        s += text(482, 148 + i * 34, "✓ " + t, 10.5, INK, "start")
    save("fig-r03-3-6-practical.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §4.3.4 — Таблиця розділів (partition table) ESP32
# ─────────────────────────────────────────────────────────────────────────────

def fig41_why_partition():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 32, "Flash — не один моноліт, а карта названих ділянок", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "на одному чипі живуть завантажувач, ваш додаток, NVS, файли, OTA-слоти — кожному своя зона",
              10.3, GREY, "middle", style="italic")
    x0, total, y, h = 60, 800, 120, 80
    parts = [("Завантажувач", 80, METAL), ("Таблиця", 56, GOLD), ("NVS", 78, BLUE),
             ("Додаток", 226, RED), ("OTA-слот", 196, RED), ("Файлова сист.", 164, GREEN)]
    x = x0
    for nm, w, c in parts:
        s += rect(x, y, w, h, _tint(c), c, 1.6, 4)
        s += text(x + w / 2, y + h / 2 + 4, nm, 9.5 if w > 90 else 8.0, c, "middle", "bold")
        x += w
    s += text(x0, y - 10, "0x0", 8.5, GREY, "start")
    s += text(x0 + total, y - 10, "кінець Flash", 8.5, GREY, "end")
    s += rect(150, 228, 620, 84, LAMB, GOLD, 1.4, 10)
    s += text(460, 252, "Хто знає, де що лежить? Маленька ТАБЛИЦЯ РОЗДІЛІВ на початку Flash —", 10, INK, "middle", "bold")
    s += text(460, 272, "карта, що каже: ось тут завантажувач, тут ваш додаток, тут NVS, тут файли.", 9.8, GREY, "middle")
    s += text(460, 292, "Без неї чіп не знав би навіть, звідки запускати вашу програму.", 9.3, GREY, "middle")
    save("fig-r03-4-1-why-partition.svg", s)


def fig42_table():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Таблиця розділів: маленький список-карта", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "кожен рядок описує одну ділянку; завантажувач читає її першою, щоб знайти додаток",
              10.5, GREY, "middle", style="italic")
    cols = [("ім'я", 90), ("тип", 300), ("зсув (offset)", 470), ("розмір", 660)]
    for nm, x in cols:
        s += text(x, 100, nm, 10.5, INK, "start" if x == 90 else "middle", "bold")
    s += line(60, 110, 840, 110, FAINT, 1.4)
    rows = [
        ("nvs", "data · nvs", "0x9000", "24 КБ", BLUE),
        ("otadata", "data · ota", "0xF000", "8 КБ", GOLD),
        ("factory", "app · factory", "0x10000", "1 МБ", RED),
        ("storage", "data · spiffs", "0x110000", "решта", GREEN),
    ]
    for i, (nm, typ, off, sz, c) in enumerate(rows):
        y = 130 + i * 50
        s += rect(60, y, 780, 42, _tint(c), c, 1.4, 8)
        s += text(80, y + 26, nm, 11.5, c, "start", "bold")
        s += text(300, y + 26, typ, 10.5, INK, "middle")
        s += text(470, y + 26, off, 10.5, INK, "middle")
        s += text(660, y + 26, sz, 10.5, INK, "middle")
    s += text(W / 2, 360, "Чотири числа на рядок — ім'я, тип, де починається, скільки займає. І це вся «магія».",
              9.6, INK, "middle", "bold")
    save("fig-r03-4-2-table.svg", s)


def fig43_layout():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 32, "Типова розкладка Flash на ESP32", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "від нульової адреси вгору: службове, далі ваш додаток, далі дані", 11, GREY, "middle", style="italic")
    items = [
        ("Завантажувач (bootloader)", "0x1000", METAL),
        ("Таблиця розділів", "0x8000", GOLD),
        ("NVS — налаштування", "0x9000", BLUE),
        ("otadata — який слот активний", "0xF000", GOLD),
        ("Додаток (factory / ota_0)", "0x10000", RED),
        ("Файлова система (LittleFS/SPIFFS)", "…", GREEN),
    ]
    y = 92
    for nm, off, c in items:
        s += rect(180, y, 520, 44, _tint(c), c, 1.6, 8)
        s += text(196, y + 27, nm, 11, c, "start", "bold")
        s += text(120, y + 27, off, 9.5, GREY, "end")
        y += 50
    s += text(80, 100, "0x0", 9, GREY, "start")
    s += arrow(96, 110, 96, 380, GREY, 1.6)
    s += text(86, 250, "адреси ↑", 8.5, GREY, "middle")
    s += text(W / 2, 404, "Службове — на дні; ваш додаток — на 0x10000; дані ростуть угору до кінця чипа.",
              9.6, INK, "middle", "bold")
    save("fig-r03-4-3-layout.svg", s)


def fig44_types():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Два роди розділів: app і data", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "одні тримають код, що його запускає завантажувач; інші — дані", 11, GREY, "middle", style="italic")
    s += rect(60, 90, 380, 230, "#fffafa", RED, 2, 12)
    s += text(250, 116, "app — код для запуску", 12.5, RED, "middle", "bold")
    for i, (st, d) in enumerate([("factory", "основна прошивка"), ("ota_0", "перший OTA-слот"),
                                 ("ota_1", "другий OTA-слот"), ("→", "завантажувач обирає, що пускати")]):
        s += text(82, 152 + i * 38, st, 11, RED, "start", "bold")
        s += text(200, 152 + i * 38, d, 9.8, INK, "start")
    s += rect(460, 90, 380, 230, "#fbfdfb", GREEN, 2, 12)
    s += text(650, 116, "data — дані", 12.5, GREEN, "middle", "bold")
    for i, (st, d) in enumerate([("nvs", "ключ–значення (§4.3.5)"), ("spiffs/littlefs", "файлова система (§4.3.6)"),
                                 ("ota", "лічильник активного слота"), ("phy", "калібрування радіо")]):
        s += text(482, 152 + i * 38, st, 11, GREEN, "start", "bold")
        s += text(610, 152 + i * 38, d, 9.5, INK, "start")
    save("fig-r03-4-4-types.svg", s)


def fig45_alignment():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 32, "Чому розділи «клацають» на межі секторів", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "межа розділу мусить збігатися з межею сектора — бо стирання йде секторами (§4.3.2)",
              10.5, GREY, "middle", style="italic")
    x0, y, cw = 90, 130, 70
    for i in range(10):
        s += rect(x0 + i * cw, y, cw - 2, 70, "#fbfbff", FAINT, 1, 3)
        s += text(x0 + i * cw + cw / 2, y + 90, hex(i * 0x1000), 8, GREY, "middle")
    s += text(x0 + 5 * cw, y - 14, "сектори по 4 КБ →", 9.5, GREY, "middle")
    # розділ, що лягає рівно по секторах
    s += rect(x0 + 2 * cw, y - 4, 3 * cw - 2, 78, "none", GREEN, 2.4, 5)
    s += text(x0 + 3.5 * cw, y + 38, "розділ — рівно по секторах ✓", 9.5, GREEN, "middle", "bold")
    s += rect(120, 250, 660, 76, LAMB, GOLD, 1.4, 10)
    s += text(450, 274, "Розділ не може починатися чи кінчатися посеред сектора:", 10.5, INK, "middle", "bold")
    s += text(450, 294, "інакше, стираючи один розділ, зачепив би сусідній. Тому межі вирівнюють на 4 КБ", 9.8, GREY, "middle")
    s += text(450, 312, "(а app-розділи — навіть на 64 КБ).", 9.8, GREY, "middle")
    save("fig-r03-4-5-alignment.svg", s)


def fig46_custom():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Своя таблиця: з CSV — у двійкову карту", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "розкладку описують текстом, а збірка перетворює її на табличку у Flash",
              11, GREY, "middle", style="italic")
    s += rect(60, 96, 360, 150, "#fbfbff", INK, 1.8, 10)
    s += text(240, 120, "partitions.csv (текст)", 10.5, INK, "middle", "bold")
    code = ["nvs,     data, nvs,   0x9000,  24K", "otadata, data, ota,   0xF000,  8K",
            "factory, app,  factory,0x10000, 1M", "storage, data, spiffs,,        1M"]
    for i, ln in enumerate(code):
        s += text(78, 148 + i * 22, ln, 8.6, INK, "start")
    s += arrow(420, 170, 500, 170, INK, 2.4)
    s += text(460, 160, "збірка", 8.5, INK, "middle")
    s += rect(500, 130, 340, 80, LAMB, GOLD, 1.8, 10)
    s += text(670, 158, "двійкова таблиця у Flash", 11, "#8a6d1a", "middle", "bold")
    s += text(670, 180, "(її й читає завантажувач)", 9.3, GREY, "middle")
    s += rect(120, 268, 660, 92, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 292, "Коли правлять CSV самотужки:", 11, INK, "middle", "bold")
    s += text(450, 312, "• додаток виріс і не влазить у свій розділ;", 9.8, INK, "middle")
    s += text(450, 330, "• треба два OTA-слоти під оновлення (§4.3.8);", 9.8, INK, "middle")
    s += text(450, 348, "• треба більше місця під файлову систему.", 9.8, INK, "middle")
    save("fig-r03-4-6-custom.svg", s)


# ── Рис. 4.3.5.1 — NVS як словник «ключ → значення» ──────────────────────────
def fig51_keyvalue():
    W, H = 880, 392
    s = header(W, H)
    s += text(W / 2, 32, "NVS — маленький словник «ключ → значення» на Flash", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "зберігаєш пару «ім'я → значення», читаєш її назад навіть після вимкнення живлення",
              11, GREY, "middle", style="italic")
    bx, by, bw, bh = 140, 86, 600, 244
    s += rect(bx, by, bw, bh, "#fbfbff", INK, 1.8, 12)
    s += text(bx + bw / 2, by + 24, "розділ  nvs  (data)", 11, GREY, "middle", "bold")
    rows = [("wifi_ssid", '"Home_5G"', "рядок", GREEN),
            ("boot_count", "42", "ціле", BLUE),
            ("volume", "7", "ціле", BLUE),
            ("calib", "⟨13 байтів⟩", "blob", GOLD)]
    y = by + 58
    for k, v, t, col in rows:
        s += text(bx + 70, y + 6, k, 13, INK, "start", "bold")
        s += arrow(bx + 230, y, bx + 300, y, GREY, 1.8)
        s += rect(bx + 310, y - 20, 210, 38, _tint(col), col, 1.6, 7)
        s += text(bx + 415, y + 6, v, 13, col, "middle", "bold")
        s += text(bx + 548, y + 5, t, 10, GREY, "start")
        y += 50
    s += text(W / 2, by + bh + 38, "ключ — коротке ім'я; значення — число, рядок або кілька «сирих» байтів",
              11, INK, "middle")
    save("fig-r03-5-1-keyvalue.svg", s)


# ── Рис. 4.3.5.2 — простори імен ─────────────────────────────────────────────
def fig52_namespace():
    W, H = 880, 348
    s = header(W, H)
    s += text(W / 2, 32, "Простори імен: щоб ключі не плуталися", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "однакове ім'я в різних просторах — це геть різні значення",
              11, GREY, "middle", style="italic")

    def ns(x, name, keys, col):
        o = rect(x, 96, 290, 150, _tint(col), col, 2, 12)
        o += text(x + 145, 122, "простір  «" + name + "»", 12.5, col, "middle", "bold")
        for i, (k, v) in enumerate(keys):
            o += text(x + 36, 158 + i * 30, k, 12, INK, "start")
            o += text(x + 250, 158 + i * 30, v, 12, INK, "end", "bold")
        return o

    s += ns(110, "wifi", [("ssid", '"Home"'), ("retries", "3")], BLUE)
    s += ns(480, "app", [("volume", "7"), ("retries", "5")], GREEN)
    s += text(W / 2, 296, "повне ім'я = простір + ключ", 12, INK, "middle", "bold")
    s += text(W / 2, 320, "тому  wifi/retries = 3  і  app/retries = 5  спокійно живуть поряд і не плутаються",
              10.5, GREY, "middle")
    save("fig-r03-5-2-namespace.svg", s)


# ── Рис. 4.3.5.3 — типи значень ──────────────────────────────────────────────
def fig53_types():
    W, H = 880, 300
    s = header(W, H)
    s += text(W / 2, 32, "Що вміщає значення: число, рядок або «сирі» байти", 19, INK, "middle", "bold")
    cards = [(70, BLUE, "ціле", "boot_count = 42", "цілі різного розміру (8…64 біти)"),
             (320, GREEN, "рядок", 'ssid = "Home_5G"', "текст довільної довжини"),
             (570, GOLD, "blob", "calib = 13 байтів", "будь-які байти: структура, ключ")]
    for x, col, t, ex, sub in cards:
        s += rect(x, 92, 240, 150, _tint(col), col, 2, 12)
        s += text(x + 120, 124, t, 14, col, "middle", "bold")
        s += text(x + 120, 162, ex, 12.5, INK, "middle", "bold")
        s += text(x + 120, 200, sub, 9.8, GREY, "middle")
    s += text(W / 2, 276, "одне сховище — три роди значень; кожне лежить під своїм ключем",
              11, INK, "middle")
    save("fig-r03-5-3-types.svg", s)


# ── Рис. 4.3.5.4 — цикл користування ─────────────────────────────────────────
def fig54_cycle():
    W, H = 900, 304
    s = header(W, H)
    s += text(W / 2, 32, "Як цим користуються: відкрити → читати/писати → закріпити", 18, INK, "middle", "bold")
    steps = [(40, "open(\"app\")", "відкрити простір", "#fbfbff", INK),
             (260, "get / set", "прочитати чи задати ключ", "#fbfbff", INK),
             (480, "commit()", "записати у Flash", LAMB, GOLD),
             (700, "close()", "відпустити сховище", "#fbfbff", INK)]
    for x, lab, sub, fill, col in steps:
        s += rect(x, 110, 170, 76, fill, col, 2, 10)
        s += text(x + 85, 142, lab, 13, col if col != INK else INK, "middle", "bold")
        s += text(x + 85, 166, sub, 9.4, GREY, "middle")
    for x in (210, 430, 650):
        s += arrow(x, 148, x + 50, 148, GREY, 2.2)
    s += text(W / 2, 232, "до commit зміни живуть у RAM; саме commit робить їх постійними —",
              11, INK, "middle")
    s += text(W / 2, 254, "забудеш його, і після перезавантаження побачиш старе значення",
              10.5, GREY, "middle")
    save("fig-r03-5-4-cycle.svg", s)


# ── Рис. 4.3.5.5 — оновлення дописуванням ────────────────────────────────────
def fig55_append():
    W, H = 900, 372
    s = header(W, H)
    s += text(W / 2, 32, "Чому NVS переживає збій і береже Flash", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "оновлення ключа не стирає старе на місці, а дописує новий запис у кінець",
              11, GREY, "middle", style="italic")
    x0, y, cw = 70, 110, 150
    cells = [("count=1", "стале", RED), ("count=2", "стале", RED),
             ("count=3", "чинне", GREEN), ("вільно", "", FAINT), ("вільно", "", FAINT)]
    for i, (lab, mark, col) in enumerate(cells):
        x = x0 + i * cw
        fill = _tint(col) if col in (RED, GREEN) else "#fcfcfc"
        s += rect(x, y, cw - 8, 64, fill, col if col != FAINT else FAINT, 1.8, 6)
        s += text(x + (cw - 8) / 2, y + 30, lab, 12, INK if col != FAINT else GREY, "middle", "bold")
        if mark:
            mk = "✗ " + mark if col == RED else "✔ " + mark
            s += text(x + (cw - 8) / 2, y + 50, mk, 9.5, col, "middle")
    s += text(x0, y - 12, "сторінка nvs (один сектор) →", 9.5, GREY, "start")
    s += arrow(x0 + 3 * cw + 4, y + 84, x0 + 3 * cw + 4, y + 100, GREEN, 2)
    s += text(x0 + 3 * cw + 4, y + 116, "новий запис дописується сюди", 9.5, GREEN, "middle", "bold")
    s += rect(80, 250, 740, 104, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 274, "Два наслідки цього простого трюку:", 11, INK, "middle", "bold")
    s += text(450, 296, "• старе значення лише позначається застарілим, не переписується на місці —",
              10, INK, "middle")
    s += text(450, 313, "тому збій під час запису не псує попереднє (згадайте erase-before-write, §4.3.2);",
              10, GREY, "middle")
    s += text(450, 333, "• записи лягають по черзі в різні місця — а це й є розмазування зносу (§4.3.3).",
              10, INK, "middle")
    save("fig-r03-5-5-append.svg", s)


# ── Рис. 4.3.5.6 — NVS проти файлової системи ────────────────────────────────
def fig56_vs_fs():
    W, H = 880, 336
    s = header(W, H)
    s += text(W / 2, 32, "NVS чи файлова система? За розміром і формою даних", 18, INK, "middle", "bold")
    s += rect(70, 84, 340, 168, LGRN, GREEN, 2, 12)
    s += text(240, 112, "NVS — дрібні налаштування", 12.5, GREEN, "middle", "bold")
    for i, t in enumerate(["• ssid, пароль, гучність", "• лічильники, прапорці", "• калібрування датчика"]):
        s += text(96, 144 + i * 26, t, 11, INK, "start")
    s += text(240, 234, "одиниці–сотні байтів, десятки ключів", 9.6, GREY, "middle", style="italic")
    s += rect(470, 84, 340, 168, LBLUE, BLUE, 2, 12)
    s += text(640, 112, "Файлова система — великі дані", 12.5, BLUE, "middle", "bold")
    for i, t in enumerate(["• журнали подій", "• картинки, звуки", "• веб-сторінки, таблиці"]):
        s += text(496, 144 + i * 26, t, 11, INK, "start")
    s += text(640, 234, "кілобайти–мегабайти, ростуть із часом", 9.6, GREY, "middle", style="italic")
    s += text(W / 2, 296, "правило: маленьке й «налаштування» → NVS; велике й «файл» → файлова система (§4.3.6)",
              11, INK, "middle", "bold")
    save("fig-r03-5-6-vs-fs.svg", s)


# ── Рис. 4.3.6.1 — файлова система як дерево іменованих файлів ─────────────────
def fig61_tree():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 32, "Файлова система: іменовані файли в теках", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "великі дані лягають у файли — названі грудки, що ростуть; теки їх групують",
              11, GREY, "middle", style="italic")
    x = 220
    rows = [(96, "/", "корінь", INK, False),
            (134, "log.txt", "журнал, що росте", GREEN, True),
            (168, "config.json", "налаштування у файлі", GREEN, True),
            (202, "photo.jpg", "40 КБ", GREEN, True),
            (236, "web/", "тека", BLUE, True),
            (270, "index.html", "сторінка", GREEN, True),
            (304, "style.css", "стилі", GREEN, True)]
    for y, name, sub, col, indent in rows:
        ix = x + (40 if indent else 0)
        ix2 = ix + (40 if name in ("index.html", "style.css") else 0)
        s += text(ix2, y, ("├─ " if indent else "") + name, 14, col, "start",
                  "bold" if not indent else "normal")
        s += text(620, y, sub, 10.5, GREY, "start")
    # vertical tree spine
    s += line(x + 8, 124, x + 8, 250, FAINT, 1.4)
    s += line(x + 48, 260, x + 48, 300, FAINT, 1.4)
    s += rect(150, 330, 580, 0, FAINT, FAINT, 0)
    s += text(W / 2, 348, "кожен файл — названа грудка, що росте; над файлами: створити, читати, дописати, стерти",
              10.5, INK, "middle")
    save("fig-r03-6-1-tree.svg", s)


# ── Рис. 4.3.6.2 — імена → блоки Flash ───────────────────────────────────────
def fig62_namemap():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 32, "Що робить файлова система: імена → блоки Flash", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "ти бачиш файл на ім'я; вона тримає карту, де його шматки лежать фізично",
              11, GREY, "middle", style="italic")
    # two file names
    s += blk(70, 110, 150, 40, "log.txt", "", LGRN, GREEN, GREEN)
    s += blk(70, 200, 150, 40, "photo.jpg", "", LBLUE, BLUE, BLUE)
    # flash strip
    x0, y, cw = 320, 150, 52
    owners = [None, GREEN, GREEN, None, BLUE, GREEN, None, BLUE, BLUE, None]
    for i, o in enumerate(owners):
        x = x0 + i * cw
        fill = _tint(o) if o else "#fcfcfc"
        col = o if o else FAINT
        s += rect(x, y, cw - 5, 50, fill, col, 1.6, 5)
        s += text(x + (cw - 5) / 2, y + 30, str(i), 11, INK if o else GREY, "middle")
    s += text(x0 + 5 * cw, y - 14, "Flash, поділений на блоки →", 9.5, GREY, "middle")
    s += arrow(225, 124, 312, 150, GREEN, 1.8)
    s += text(270, 120, "блоки 1,2,5", 8.6, GREEN, "middle")
    s += arrow(225, 214, 312, 205, BLUE, 1.8)
    s += text(270, 232, "блоки 4,7,8", 8.6, BLUE, "middle")
    s += rect(150, 270, 600, 48, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 290, "Файлова система веде дві речі: карту «ім'я → його блоки»",
              10.5, INK, "middle", "bold")
    s += text(450, 308, "і список вільних блоків — щоб знати, куди класти нові дані.", 10, GREY, "middle")
    save("fig-r03-6-2-namemap.svg", s)


# ── Рис. 4.3.6.3 — чому ПК-файлова система не годиться ────────────────────────
def fig63_flash_aware():
    W, H = 900, 348
    s = header(W, H)
    s += text(W / 2, 32, "Чому файлову систему з ПК не можна брати як є", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "на Flash діють erase-before-write (§4.3.2) і знос (§4.3.3) — це міняє правила",
              10.5, GREY, "middle", style="italic")
    # bad row
    s += rect(60, 80, 780, 110, LRED, RED, 1.8, 10)
    s += text(80, 108, "ПК-стиль (як FAT): службову таблицю переписують НА ТОМУ Ж МІСЦІ",
              12, RED, "start", "bold")
    x0 = 100
    for i in range(8):
        h = 40 if i != 3 else 40
        col = RED if i == 3 else FAINT
        s += rect(x0 + i * 64, 132, 56, 40, LRED if i == 3 else "#fcfcfc", col, 1.6, 4)
    s += text(x0 + 3 * 64 + 28, 156, "✗", 16, RED, "middle", "bold")
    s += text(x0 + 3 * 64 + 28, 186, "той самий блок б'ється раз у раз — швидкий хот-спот",
              9, RED, "middle")
    # good row
    s += rect(60, 210, 780, 118, LGRN, GREEN, 1.8, 10)
    s += text(80, 238, "Flash-свідома (LittleFS): нове пише КОПІЄЮ в чисте місце",
              12, GREEN, "start", "bold")
    for i in range(8):
        mark = i in (1, 4, 6)
        s += rect(x0 + i * 64, 262, 56, 40, LGRN if mark else "#fcfcfc",
                  GREEN if mark else FAINT, 1.6, 4)
        if mark:
            s += text(x0 + i * 64 + 28, 286, "✓", 14, GREEN, "middle", "bold")
    s += text(x0 + 3.5 * 64, 318, "записи розходяться по чипу — знос розмазується, збій не псує старе",
              9, GREEN, "middle")
    save("fig-r03-6-3-flash-aware.svg", s)


# ── Рис. 4.3.6.4 — SPIFFS проти LittleFS ─────────────────────────────────────
def fig64_spiffs_littlefs():
    W, H = 880, 320
    s = header(W, H)
    s += text(W / 2, 32, "Дві файлові системи на чипі: SPIFFS і LittleFS", 18, INK, "middle", "bold")
    s += rect(70, 76, 340, 200, "#f4f4f4", GREY, 1.8, 12)
    s += text(240, 104, "SPIFFS — старіша", 13, GREY, "middle", "bold")
    for i, t in enumerate(["• плоска: без справжніх тек", "• не захищена від втрати живлення",
                            "• повільна, коли майже повна", "• поступово виходить з ужитку"]):
        s += text(96, 138 + i * 30, t, 10.8, INK, "start")
    s += rect(470, 76, 340, 200, LGRN, GREEN, 2, 12)
    s += text(640, 104, "LittleFS — сучасна", 13, GREEN, "middle", "bold")
    for i, t in enumerate(["• справжні теки", "• стійка до втрати живлення",
                           "• рівномірний знос, швидша", "• вибір для нових проєктів"]):
        s += text(496, 138 + i * 30, t, 10.8, INK, "start")
    s += text(W / 2, 300, "Для нового пристрою беріть LittleFS; SPIFFS лишився хіба для старих проєктів.",
              11, INK, "middle", "bold")
    save("fig-r03-6-4-spiffs-littlefs.svg", s)


# ── Рис. 4.3.6.5 — SD-картка ─────────────────────────────────────────────────
def fig65_sd_card():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 32, "SD-картка: зовнішнє сховище на гігабайти", 19, INK, "middle", "bold")
    # ESP32 box
    s += blk(80, 130, 150, 90, "ESP32", "", LBLUE, BLUE, BLUE)
    # SD card shape (rect with clipped corner)
    sx, sy = 560, 110
    s += ('<path d="M{a},{b} L{c},{b} L{c},{d} L{a},{d} L{a},{e} L{f},{b} Z" '
          'fill="{fl}" stroke="{st}" stroke-width="2"/>\n').format(
        a=sx, b=sy, c=sx + 150, d=sy + 130, e=sy + 24, f=sx + 24, fl=LAMB, st=GOLD)
    s += text(sx + 87, sy + 70, "SD", 20, "#8a6d1a", "middle", "bold")
    # SPI wires
    for i, (lab, yy) in enumerate([("CS", 150), ("SCK", 172), ("MOSI", 194), ("MISO", 216)]):
        s += line(230, yy, 560, yy, GREY, 1.6)
        s += text(395, yy - 5, lab, 8.6, GREY, "middle")
    s += text(395, 130, "4 дроти SPI", 10, INK, "middle", "bold")
    s += rect(120, 262, 660, 64, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 284, "Гігабайти (а не МБ), виймається й читається на ПК, має власний контролер",
              10.3, INK, "middle")
    s += text(450, 304, "і вирівнювання зносу всередині; зазвичай форматована у FAT — заради сумісності.",
              10, GREY, "middle")
    save("fig-r03-6-5-sd-card.svg", s)


# ── Рис. 4.3.6.6 — що куди класти ────────────────────────────────────────────
def fig66_decision():
    W, H = 900, 332
    s = header(W, H)
    s += text(W / 2, 32, "Що куди класти: NVS, LittleFS чи SD-картка", 18, INK, "middle", "bold")
    lanes = [(GREEN, "Дрібні налаштування", "байти, десятки ключів", "→ NVS  (§4.3.5)",
              "ssid, гучність, лічильник"),
             (BLUE, "Внутрішні файли", "КБ–МБ, незнімні", "→ LittleFS на Flash",
              "журнал, веб-сторінка, звук"),
             (GOLD, "Великі чи знімні дані", "МБ–ГБ, виймаються", "→ SD-картка + FAT",
              "відео, тривалий лог, дамп")]
    y = 86
    for col, title, size, dest, ex in lanes:
        s += rect(80, y, 740, 68, _tint(col), col, 1.8, 10)
        s += text(104, y + 28, title, 12.5, col, "start", "bold")
        s += text(104, y + 50, size, 9.8, GREY, "start")
        s += text(420, y + 30, ex, 10, INK, "start")
        s += text(800, y + 40, dest, 11.5, col, "end", "bold")
        y += 80
    save("fig-r03-6-6-decision.svg", s)


# ── Рис. 4.3.7.1 — небезпечне вікно запису ───────────────────────────────────
def fig71_window():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 32, "Найнебезпечніша мить: збій посеред запису", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "запис не миттєвий — поки він триває, дані в проміжному, нецілому стані",
              11, GREY, "middle", style="italic")
    # timeline
    y = 150
    s += line(70, y, 830, y, INK, 2)
    s += blk(110, y - 26, 200, 52, "стерти сектор", "", LBLUE, BLUE, BLUE)
    s += blk(360, y - 26, 200, 52, "записати байти", "", LBLUE, BLUE, BLUE)
    s += blk(630, y - 26, 150, 52, "готово", "", LGRN, GREEN, GREEN)
    s += arrow(310, y, 360, y, GREY, 2)
    s += arrow(560, y, 630, y, GREY, 2)
    # danger window
    s += rect(110, y - 40, 450, 80, "none", RED, 2, 8)
    s += text(335, y - 50, "небезпечне вікно", 11, RED, "middle", "bold")
    s += text(335, y + 70, "гасне струм тут → ні старого, ні нового значення", 11, RED, "middle", "bold")
    save("fig-r03-7-1-window.svg", s)


# ── Рис. 4.3.7.2 — розірваний запис ──────────────────────────────────────────
def fig72_torn():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 32, "«Розірваний» запис: півстарого, півнового", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "недописане — гірше за просто втрачене: пристрій прочитає сміття",
              11, GREY, "middle", style="italic")
    # good row: lost update
    s += rect(60, 84, 360, 90, LGRN, GREEN, 1.8, 10)
    s += text(240, 110, "Втратив оновлення", 12, GREEN, "middle", "bold")
    s += text(240, 138, "лишилось старе, ціле значення", 10, INK, "middle")
    s += text(240, 160, "✓ пристрій працює далі", 11, GREEN, "middle", "bold")
    # bad row: torn
    s += rect(480, 84, 360, 90, LRED, RED, 1.8, 10)
    s += text(660, 110, "Розірваний запис", 12, RED, "middle", "bold")
    # half-half cell
    s += rect(560, 124, 100, 26, _tint(GREEN), GREEN, 1.4, 3)
    s += rect(660, 124, 100, 26, _tint(RED), RED, 1.4, 3)
    s += text(610, 142, "нове", 9.5, GREEN, "middle")
    s += text(710, 142, "старе", 9.5, RED, "middle")
    s += text(660, 166, "✗ читається як сміття", 11, RED, "middle", "bold")
    s += rect(120, 210, 660, 86, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 236, "Мета цілості: уникнути саме «розірваного» стану.", 12, INK, "middle", "bold")
    s += text(450, 260, "Краще чесно лишитися зі старим значенням, ніж із напівновим,", 10.5, GREY, "middle")
    s += text(450, 280, "яке неможливо ні прочитати, ні довіряти йому.", 10.5, GREY, "middle")
    save("fig-r03-7-2-torn.svg", s)


# ── Рис. 4.3.7.3 — атомарність ───────────────────────────────────────────────
def fig73_atomic():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 32, "Рятунок 1: усе або нічого (атомарність)", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "пиши нове ПОРЯД зі старим, а тоді одним крихітним кроком перемкни «чинне»",
              10.5, GREY, "middle", style="italic")
    y = 130
    s += blk2(60, y, 180, 70, "старе ціле", ["чинне зараз"], LGRN, GREEN, GREEN)
    s += arrow(240, y + 35, 300, y + 35, GREY, 2)
    s += text(270, y + 24, "пишемо", 8.5, GREY, "middle")
    s += blk2(300, y, 220, 70, "старе + нове поряд", ["обидва на чипі"], "#fbfbff", INK, INK)
    s += arrow(520, y + 35, 580, y + 35, RED, 2.4)
    s += text(550, y + 24, "1 крок", 8.5, RED, "middle")
    s += blk2(580, y, 180, 70, "нове чинне", ["перемкнуто"], LGRN, GREEN, GREEN)
    s += text(550, y + 90, "↑ точка фіксації", 10, RED, "middle", "bold")
    s += rect(120, 252, 660, 64, LAMB, GOLD, 1.4, 10)
    s += text(450, 276, "Гасне струм ДО перемикача — лишається старе; ПІСЛЯ — нове.", 11, INK, "middle", "bold")
    s += text(450, 298, "Проміжного стану нема: сам перемикач — одна крихітна, неподільна дія.", 10, GREY, "middle")
    save("fig-r03-7-3-atomic.svg", s)


# ── Рис. 4.3.7.4 — контрольна сума ───────────────────────────────────────────
def fig74_checksum():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 32, "Рятунок 2: контрольна сума — чи цілий запис?", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "до даних кладуть коротке «контрольне число»; не зійшлося — запис розірваний",
              10.5, GREY, "middle", style="italic")
    # write side
    s += text(180, 96, "Коли пишемо:", 12, INK, "middle", "bold")
    s += rect(70, 110, 150, 44, _tint(BLUE), BLUE, 1.6, 6)
    s += text(145, 137, "дані", 12, BLUE, "middle", "bold")
    s += rect(230, 110, 70, 44, LAMB, GOLD, 1.6, 6)
    s += text(265, 137, "AB", 12, "#8a6d1a", "middle", "bold")
    s += text(185, 176, "порахували суму з даних → поклали поряд", 9.5, GREY, "middle")
    # read side
    s += text(640, 96, "Коли читаємо:", 12, INK, "middle", "bold")
    s += text(560, 130, "рахуємо суму знову:", 10, INK, "start")
    s += text(560, 154, "збіг (AB = AB) →", 10, GREEN, "start")
    s += text(720, 154, "цілий ✓", 11, GREEN, "start", "bold")
    s += text(560, 178, "розбіжність (7F ≠ AB) →", 10, RED, "start")
    s += text(745, 178, "розірваний ✗", 11, RED, "start", "bold")
    s += line(450, 96, 450, 196, FAINT, 1.4)
    s += rect(120, 222, 660, 90, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 248, "Сума не лагодить дані — вона їх викриває.", 12, INK, "middle", "bold")
    s += text(450, 272, "Помітивши розірваний запис, сховище відкидає його", 10.5, GREY, "middle")
    s += text(450, 292, "й повертається до попередньої, цілої копії.", 10.5, GREY, "middle")
    save("fig-r03-7-4-checksum.svg", s)


# ── Рис. 4.3.7.5 — два слоти + версія + сума ──────────────────────────────────
def fig75_double_slot():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 32, "Надійний конфіг: два слоти + версія + сума", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "пишемо в старіший слот; уцілілий другий завжди лишається запасом",
              11, GREY, "middle", style="italic")
    s += rect(90, 92, 320, 96, LGRN, GREEN, 2, 12)
    s += text(250, 120, "Слот A", 13, GREEN, "middle", "bold")
    s += text(250, 146, "версія 7   сума ✓", 12, INK, "middle")
    s += text(250, 170, "(пишемо сюди → стане версією 9)", 9.3, GREY, "middle")
    s += rect(490, 92, 320, 96, LGRN, GREEN, 2, 12)
    s += text(650, 120, "Слот B", 13, GREEN, "middle", "bold")
    s += text(650, 146, "версія 8   сума ✓", 12, INK, "middle")
    s += text(650, 170, "(цілий запас на час запису A)", 9.3, GREY, "middle")
    s += rect(120, 214, 660, 100, LAMB, GOLD, 1.4, 10)
    s += text(450, 240, "При старті: бери слот із найбільшою версією, що проходить суму.",
              11.5, INK, "middle", "bold")
    s += text(450, 264, "Поки пишемо A, цілий B чекає; не дописали A (збій) — його версія чи",
              10, GREY, "middle")
    s += text(450, 282, "сума підкажуть «не довіряй», і пристрій спокійно візьме B.", 10, GREY, "middle")
    s += text(450, 304, "Хоч би коли обірвалось живлення — лишається щонайменше одна ціла копія.",
              10, GREEN, "middle", "bold")
    save("fig-r03-7-5-double-slot.svg", s)


# ── Рис. 4.3.7.6 — хто це робить за вас ──────────────────────────────────────
def fig76_who_does_it():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 32, "Хто дбає про цілість за вас", 19, INK, "middle", "bold")
    cols = [(GREEN, "NVS", "✓ робить сам", ["маркер цілості", "оновлення дописуванням"]),
            (GREEN, "LittleFS", "✓ робить сам", ["copy-on-write", "один крок-перемикач"]),
            (RED, "«голий» Flash", "ви — самі", ["атомарність + сума", "слоти й версії — на вас"])]
    x = 70
    for col, name, badge, items in cols:
        s += rect(x, 84, 250, 150, _tint(col), col, 1.8, 12)
        s += text(x + 125, 114, name, 14, col, "middle", "bold")
        s += text(x + 125, 138, badge, 11, INK, "middle", "bold")
        for i, it in enumerate(items):
            s += text(x + 125, 168 + i * 24, it, 10, GREY, "middle")
        x += 270
    s += text(W / 2, 272, "Користуєшся NVS чи LittleFS — майже все це вже зроблено всередині.",
              11.5, INK, "middle", "bold")
    save("fig-r03-7-6-who-does-it.svg", s)


# ── Рис. 4.3.8.1 — не можна писати прошивку поверх себе ───────────────────────
def fig81_no_overwrite():
    W, H = 900, 312
    s = header(W, H)
    s += text(W / 2, 32, "Чому прошивку не можна писати поверх себе", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "вона виконується просто зараз — переписати її = впасти посеред власного кроку",
              10.5, GREY, "middle", style="italic")
    s += rect(310, 110, 280, 80, LGRN, GREEN, 2, 12)
    s += text(450, 142, "поточна прошивка", 13, GREEN, "middle", "bold")
    s += text(450, 166, "▶ виконується зараз", 10.5, INK, "middle")
    s += arrow(180, 150, 305, 150, RED, 2.6)
    s += text(180, 134, "пишемо нове", 10, RED, "middle", "bold")
    s += text(660, 150, "✗", 30, RED, "middle", "bold")
    s += text(660, 186, "= «цеглина»", 10, RED, "middle", "bold")
    s += rect(150, 226, 600, 64, LAMB, GOLD, 1.4, 10)
    s += text(450, 250, "Потрібне ДРУГЕ місце: писати новий образ туди,", 11.5, INK, "middle", "bold")
    s += text(450, 272, "не чіпаючи того, що зараз працює.", 10.5, GREY, "middle")
    save("fig-r03-8-1-no-overwrite.svg", s)


# ── Рис. 4.3.8.2 — два слоти ota_0 / ota_1 ───────────────────────────────────
def fig82_two_slots():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 32, "Два слоти для прошивки: ota_0 і ota_1", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "один працює, у другий тим часом пишемо новий образ",
              11, GREY, "middle", style="italic")
    s += rect(90, 96, 320, 110, LGRN, GREEN, 2.2, 12)
    s += text(250, 128, "ota_0", 15, GREEN, "middle", "bold")
    s += text(250, 154, "ПРАЦЮЄ зараз", 12, INK, "middle", "bold")
    s += text(250, 180, "поточна прошивка — недоторкана", 9.5, GREY, "middle")
    s += ('<rect x="490" y="96" width="320" height="110" rx="12" fill="{f}" '
          'stroke="{st}" stroke-width="2.2" stroke-dasharray="7 5"/>\n').format(f=LBLUE, st=BLUE)
    s += text(650, 128, "ota_1", 15, BLUE, "middle", "bold")
    s += text(650, 154, "вільний слот", 12, INK, "middle", "bold")
    s += text(650, 180, "сюди лягає новий образ", 9.5, GREY, "middle")
    s += arrow(415, 151, 488, 151, BLUE, 2.4)
    s += text(452, 138, "новий", 8.6, BLUE, "middle")
    s += text(W / 2, 246, "Поки пишемо в ota_1, ota_0 спокійно виконується далі —", 11, INK, "middle", "bold")
    s += text(W / 2, 268, "збій під час запису не чіпає робочої прошивки.", 10.5, GREY, "middle")
    save("fig-r03-8-2-two-slots.svg", s)


# ── Рис. 4.3.8.3 — перемикач otadata ─────────────────────────────────────────
def fig83_otadata():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 32, "Перемикач завантаження: крихітна otadata", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "маленький розділ, що каже завантажувачу, з якого слота стартувати",
              11, GREY, "middle", style="italic")
    s += blk(70, 120, 140, 56, "завантажувач", "", LBLUE, BLUE, BLUE)
    s += arrow(210, 148, 270, 148, GREY, 2)
    s += rect(270, 116, 150, 64, LAMB, GOLD, 1.8, 10)
    s += text(345, 140, "otadata", 12, "#8a6d1a", "middle", "bold")
    s += text(345, 162, "«старт зі слота 1»", 9.5, GREY, "middle")
    s += arrow(420, 148, 480, 148, GREY, 2)
    s += blk(480, 120, 150, 56, "ota_1", "новий образ", LGRN, GREEN, GREEN)
    # steps
    s += rect(120, 214, 660, 100, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 238, "Порядок — як атомарний перемикач із §4.3.7:", 11.5, INK, "middle", "bold")
    s += text(450, 262, "1) записати новий образ у вільний слот ПОВНІСТЮ;  2) перевірити його;",
              10, GREY, "middle")
    s += text(450, 282, "3) аж тоді перемкнути otadata на цей слот — одним коротким кроком.",
              10, GREY, "middle")
    s += text(450, 304, "Збій до кроку 3 → стартує старий слот; після → новий. Без «напівоновлення».",
              10, GREEN, "middle", "bold")
    save("fig-r03-8-3-otadata.svg", s)


# ── Рис. 4.3.8.4 — пробний запуск і відкат ───────────────────────────────────
def fig84_trial_rollback():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 32, "Перше вмикання: випробування й відкат", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "новий образ стартує «на випробуванні»; не підтвердив себе — повертаємось до старого",
              10.3, GREY, "middle", style="italic")
    s += blk2(360, 92, 180, 64, "новий образ", ["стартує (пробний)"], LBLUE, BLUE, BLUE)
    # good branch
    s += arrow(450, 156, 250, 210, GREEN, 2.2)
    s += rect(70, 214, 360, 100, LGRN, GREEN, 1.8, 10)
    s += text(250, 240, "працює й каже «я в нормі»", 11.5, GREEN, "middle", "bold")
    s += text(250, 264, "otadata закріплює новий слот", 10, INK, "middle")
    s += text(250, 290, "✓ оновлення вдалося", 11, GREEN, "middle", "bold")
    # bad branch
    s += arrow(450, 156, 650, 210, GOLD, 2.2)
    s += rect(470, 214, 360, 100, LAMB, GOLD, 1.8, 10)
    s += text(650, 240, "падає / зациклюється / мовчить", 11, "#8a6d1a", "middle", "bold")
    s += text(650, 264, "завантажувач вертає старий слот", 10, INK, "middle")
    s += text(650, 290, "✓ відкат — пристрій живий", 11, "#8a6d1a", "middle", "bold")
    save("fig-r03-8-4-trial-rollback.svg", s)


# ── Рис. 4.3.8.5 — ціна: місце ───────────────────────────────────────────────
def fig85_cost():
    W, H = 900, 290
    s = header(W, H)
    s += text(W / 2, 32, "Ціна безпечних оновлень: місце", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "два повні слоти — отже, прошивка вміщається щонайбільше у половину місця під код",
              10.3, GREY, "middle", style="italic")
    s += text(140, 110, "область під код:", 11, INK, "start", "bold")
    s += rect(140, 124, 300, 54, LGRN, GREEN, 1.8, 6)
    s += text(290, 156, "ota_0  (половина)", 11.5, GREEN, "middle", "bold")
    s += rect(450, 124, 300, 54, LBLUE, BLUE, 1.8, 6)
    s += text(600, 156, "ota_1  (половина)", 11.5, BLUE, "middle", "bold")
    s += rect(150, 210, 600, 64, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 234, "За надійне оновлення платять половиною місця під код (§4.3.4).",
              11, INK, "middle", "bold")
    s += text(450, 256, "Тому, плануючи Flash, одразу закладайте місце під ДВА образи.", 10, GREY, "middle")
    save("fig-r03-8-5-cost.svg", s)


# ── Рис. 4.3.8.6 — та сама ідея, інший масштаб ───────────────────────────────
def fig86_same_idea():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 32, "Та сама ідея, інший масштаб", 19, INK, "middle", "bold")
    s += rect(70, 80, 760, 70, LGRN, GREEN, 1.8, 10)
    s += text(96, 110, "Конфіг:", 12, GREEN, "start", "bold")
    s += text(96, 132, "два маленькі слоти + перемикач (номер версії)", 10.5, INK, "start")
    s += text(810, 119, "§4.3.7", 10.5, GREY, "end")
    s += rect(70, 162, 760, 70, LBLUE, BLUE, 1.8, 10)
    s += text(96, 192, "Прошивка:", 12, BLUE, "start", "bold")
    s += text(96, 214, "два великі слоти + перемикач (otadata)", 10.5, INK, "start")
    s += text(810, 201, "тут", 10.5, GREY, "end")
    s += text(W / 2, 268, "Один прийом: пиши нове поряд → перемкни одним кроком → май запас на відкат.",
              11, INK, "middle", "bold")
    save("fig-r03-8-6-same-idea.svg", s)


# ── Рис. 4.3.9.1 — дві загрози, два щити ──────────────────────────────────────
def fig91_two_threats():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 32, "Дві різні загрози — два різні щити", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "одна про справжність прошивки, друга — про таємність даних; їх не плутають",
              10.3, GREY, "middle", style="italic")
    s += rect(60, 84, 360, 192, LRED, RED, 2, 12)
    s += text(240, 112, "Підміна прошивки", 13, RED, "middle", "bold")
    s += text(240, 138, "зловмисник заливає свій код", 10, INK, "middle")
    s += rect(110, 158, 260, 44, "#fff", RED, 1.6, 8)
    s += text(240, 186, "щит: SECURE BOOT", 12, RED, "middle", "bold")
    s += text(240, 226, "перевіряє, чи прошивка НАША,", 10, GREY, "middle")
    s += text(240, 246, "і не дає стартувати чужій", 10, GREY, "middle")
    s += rect(480, 84, 360, 192, LBLUE, BLUE, 2, 12)
    s += text(660, 112, "Підглядання даних", 13, BLUE, "middle", "bold")
    s += text(660, 138, "зловмисник читає вміст Flash", 10, INK, "middle")
    s += rect(530, 158, 260, 44, "#fff", BLUE, 1.6, 8)
    s += text(660, 186, "щит: ШИФРУВАННЯ FLASH", 11.5, BLUE, "middle", "bold")
    s += text(660, 226, "робить вміст нечитним для", 10, GREY, "middle")
    s += text(660, 246, "будь-кого без ключа в чипі", 10, GREY, "middle")
    save("fig-r03-9-1-two-threats.svg", s)


# ── Рис. 4.3.9.2 — цифровий підпис ───────────────────────────────────────────
def fig92_signature():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 32, "Цифровий підпис: «це справді наше?»", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "виробник підписує таємним ключем; пристрій звіряє відкритим, зашитим у нього",
              10.3, GREY, "middle", style="italic")
    # maker
    s += rect(60, 88, 300, 120, "#fbfbff", INK, 1.8, 10)
    s += text(210, 112, "виробник", 12, INK, "middle", "bold")
    s += text(210, 140, "прошивка + таємний ключ", 10, GREY, "middle")
    s += blk(110, 154, 200, 40, "підписаний образ", "", LAMB, GOLD, "#8a6d1a")
    # arrow
    s += arrow(360, 150, 480, 150, GREY, 2.4)
    s += text(420, 138, "віддаємо", 8.6, GREY, "middle")
    # device
    s += rect(480, 88, 360, 120, "#fbfbff", INK, 1.8, 10)
    s += text(660, 112, "пристрій", 12, INK, "middle", "bold")
    s += text(660, 138, "звіряє відкритим ключем (зашитий)", 9.6, GREY, "middle")
    s += text(560, 176, "збіг → наше ✓", 11, GREEN, "middle", "bold")
    s += text(760, 176, "ні → чуже ✗", 11, RED, "middle", "bold")
    s += rect(120, 236, 660, 80, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 260, "Як печатка: підробити не може ніхто, упізнати — може кожен.", 11, INK, "middle", "bold")
    s += text(450, 284, "Сума (§4.3.7) ловить випадкове псування; підпис — навмисну підміну.",
              10, GREY, "middle")
    save("fig-r03-9-2-signature.svg", s)


# ── Рис. 4.3.9.3 — ланцюг довіри ─────────────────────────────────────────────
def fig93_chain():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 32, "Ланцюг довіри: кожна ланка ручається за наступну", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "незмінний корінь у чипі вивіряє завантажувач, той — ваш додаток",
              10.5, GREY, "middle", style="italic")
    s += rect(50, 110, 220, 90, LAMB, GOLD, 2, 12)
    s += text(160, 138, "🔒 корінь у чипі", 12.5, "#8a6d1a", "middle", "bold")
    s += text(160, 162, "перепалені запобіжники", 9.3, GREY, "middle")
    s += text(160, 182, "НЕЗМІННИЙ", 10, RED, "middle", "bold")
    s += blk2(350, 110, 190, 90, "завантажувач", ["підписаний"], LGRN, GREEN, GREEN)
    s += blk2(620, 110, 190, 90, "ваш додаток", ["підписаний"], LGRN, GREEN, GREEN)
    s += arrow(270, 155, 348, 155, INK, 2.2)
    s += text(309, 142, "вивіряє", 8.6, INK, "middle")
    s += arrow(540, 155, 618, 155, INK, 2.2)
    s += text(579, 142, "вивіряє", 8.6, INK, "middle")
    s += text(W / 2, 240, "Кожна ланка перевіряє підпис наступної, перш ніж передати їй керування.",
              11, INK, "middle", "bold")
    s += text(W / 2, 262, "Усе тримається на корені, якого не підмінити, — це «якір довіри».", 10.3, GREY, "middle")
    save("fig-r03-9-3-chain.svg", s)


# ── Рис. 4.3.9.4 — secure boot ───────────────────────────────────────────────
def fig94_secure_boot():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 32, "Secure boot: стартує лише наше", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "при кожному вмиканні чип проходить ланцюг і звіряє підписи",
              11, GREY, "middle", style="italic")
    s += blk(330, 92, 240, 54, "вмикання → перевірка ланцюга", "", LBLUE, BLUE, BLUE)
    # good
    s += arrow(420, 146, 250, 196, GREEN, 2.2)
    s += rect(70, 200, 360, 92, LGRN, GREEN, 1.8, 10)
    s += text(250, 228, "усе сходиться", 12, GREEN, "middle", "bold")
    s += text(250, 252, "підписи правильні", 10, INK, "middle")
    s += text(250, 276, "✓ запуск", 12, GREEN, "middle", "bold")
    # bad
    s += arrow(480, 146, 650, 196, RED, 2.2)
    s += rect(470, 200, 360, 92, LRED, RED, 1.8, 10)
    s += text(650, 228, "щось підмінили", 12, RED, "middle", "bold")
    s += text(650, 252, "підпис не сходиться", 10, INK, "middle")
    s += text(650, 276, "✗ відмова стартувати", 11.5, RED, "middle", "bold")
    save("fig-r03-9-4-secure-boot.svg", s)


# ── Рис. 4.3.9.5 — шифрування Flash ──────────────────────────────────────────
def fig95_flash_enc():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 32, "Шифрування Flash: секрети лишаються нечитними", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "вміст зберігається переплутаним; ключ замкнений у чипі й назовні не виходить",
              10.3, GREY, "middle", style="italic")
    # flash gibberish
    s += rect(70, 96, 360, 120, "#f4f4f4", GREY, 1.8, 10)
    s += text(250, 120, "Flash (як його видно ззовні)", 10.5, INK, "middle", "bold")
    import_garble = ["9F 3A C1 70 E2 88 4B", "A0 1D FF 5C 39 B7 02", "6E D4 91 28 AC 7F 50"]
    for i, ln in enumerate(import_garble):
        s += text(250, 150 + i * 22, ln, 11, GREY, "middle")
    s += text(250, 230, "висмикнув і прочитав → нісенітниця ✗", 10, RED, "middle", "bold")
    # chip with key
    s += rect(520, 96, 320, 120, LAMB, GOLD, 2, 12)
    s += text(680, 122, "🔒 чип", 13, "#8a6d1a", "middle", "bold")
    s += text(680, 150, "ключ замкнений усередині", 10, INK, "middle")
    s += text(680, 174, "на льоту розшифровує для CPU", 9.6, GREY, "middle")
    s += text(680, 200, "ключ ніколи не покидає чип", 9.6, GREEN, "middle", "bold")
    s += rect(150, 250, 600, 56, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 274, "Захищає вкладені ключі, ваш код і особисті дані:", 11, INK, "middle", "bold")
    s += text(450, 294, "навіть фізичний доступ до чипа не віддає їхній зміст.", 10, GREY, "middle")
    save("fig-r03-9-5-flash-enc.svg", s)


# ── Рис. 4.3.9.6 — ціна й обережність ────────────────────────────────────────
def fig96_caution():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 32, "Ціна й обережність: двері в один бік", 19, INK, "middle", "bold")
    items = [(RED, "Запобіжники — назавжди", "перепалив — назад не повернеш"),
             (GOLD, "Ключ — це все", "втратив чи виказав — лихо"),
             (BLUE, "Плата за швидкість", "трохи складніше й повільніше")]
    x = 70
    for col, t, sub in items:
        s += rect(x, 84, 250, 110, _tint(col), col, 1.8, 12)
        s += text(x + 125, 122, t, 12, col, "middle", "bold")
        s += text(x + 125, 152, sub, 9.6, INK, "middle")
        x += 270
    s += rect(120, 222, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(450, 246, "Хобі-проєкт — зазвичай вимкнено; серійний виріб — увімкнено, але обережно.",
              11, INK, "middle", "bold")
    s += text(450, 266, "Це інструмент для готового продукту, а не для першого мигтіння світлодіода.",
              9.8, GREY, "middle")
    save("fig-r03-9-6-caution.svg", s)


# ── Рис. 4.3.6c.1 — що на платі SD-модуля ────────────────────────────────────
def fig6c1_block():
    W, H = 880, 300
    s = header(W, H)
    s += text(W / 2, 32, "SD-модуль: що на платі", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "тримач картки + (для 5-вольтових плат) зсув рівнів і стабілізатор 3.3 В",
              10.5, GREY, "middle", style="italic")
    s += rect(60, 80, 600, 150, "#fbfbff", INK, 1.8, 12)
    s += text(360, 102, "модуль microSD", 11, GREY, "middle", "bold")
    s += blk2(80, 120, 150, 90, "тримач", ["картки microSD"], LBLUE, BLUE, BLUE)
    s += blk2(255, 120, 160, 90, "зсув рівнів", ["5 В ↔ 3.3 В"], LAMB, GOLD, "#8a6d1a")
    s += blk2(440, 120, 160, 90, "стабілізатор", ["3.3 В"], LGRN, GREEN, GREEN)
    s += arrow(230, 165, 253, 165, GREY, 1.8)
    s += arrow(415, 165, 438, 165, GREY, 1.8)
    # pins out
    s += line(660, 155, 700, 155, GREY, 1.6)
    s += text(770, 130, "6 виводів:", 10.5, INK, "middle", "bold")
    s += text(770, 150, "VCC · GND", 10, GREY, "middle")
    s += text(770, 168, "CS · SCK", 10, GREY, "middle")
    s += text(770, 186, "MOSI · MISO", 10, GREY, "middle")
    s += text(W / 2, 264, "ESP32 уже 3.3-вольтовий — часто зсув і не потрібен; його несуть модулі під 5-вольтовий Arduino.",
              10.3, INK, "middle")
    save("fig-r03-6c-1-block.svg", s)


# ── Рис. 4.3.6c.2 — підключення до ESP32 ─────────────────────────────────────
def fig6c2_wiring():
    W, H = 880, 320
    s = header(W, H)
    s += text(W / 2, 32, "Підключення SD-модуля до ESP32 по SPI", 18, INK, "middle", "bold")
    s += blk2(70, 110, 150, 130, "ESP32", ["3.3 В"], LBLUE, BLUE, BLUE)
    s += blk2(660, 110, 150, 130, "SD-модуль", [""], LAMB, GOLD, "#8a6d1a")
    wires = [("VCC", "3.3 В (або 5 В на модуль зі стабілізатором)", GREEN),
             ("GND", "спільна земля", INK),
             ("CS", "будь-який вільний GPIO", BLUE),
             ("SCK", "тактова лінія SPI", GREY),
             ("MOSI", "дані до картки", GREY),
             ("MISO", "дані від картки", GREY)]
    for i, (lab, note, col) in enumerate(wires):
        y = 122 + i * 22
        s += line(220, y, 660, y, col, 1.6)
        s += text(440, y - 4, lab, 9.2, col, "middle", "bold")
        s += text(440, y + 12, note, 8.0, GREY, "middle")
    s += rect(150, 268, 600, 44, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 292, "Шина SPI спільна для багатьох пристроїв — але кожному потрібен свій окремий CS.",
              10, INK, "middle", "bold")
    save("fig-r03-6c-2-wiring.svg", s)


# ── Рис. 4.3.3c.1 — FRAM проти Flash ─────────────────────────────────────────
def fig3c1_vs_flash():
    W, H = 880, 320
    s = header(W, H)
    s += text(W / 2, 32, "FRAM проти Flash: чим бере", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "та сама незникність, але пише як RAM і майже не зношується",
              11, GREY, "middle", style="italic")
    s += rect(70, 84, 340, 180, LGRN, GREEN, 2, 12)
    s += text(240, 112, "FRAM", 14, GREEN, "middle", "bold")
    for i, t in enumerate(["• пише побайтово, без стирання", "• знос практично нескінченний",
                           "• швидко й ощадливо", "— мало місця (КБ), дорожче"]):
        col = RED if t.startswith("—") else INK
        s += text(96, 144 + i * 28, t, 11, col, "start")
    s += rect(470, 84, 340, 180, LBLUE, BLUE, 2, 12)
    s += text(640, 112, "Flash", 14, BLUE, "middle", "bold")
    for i, t in enumerate(["• стирає блоками перед записом", "• зношується (~10⁴–10⁵)",
                           "• багато місця (МБ), дешево", "— бережи від частих записів"]):
        col = RED if t.startswith("—") else INK
        s += text(496, 144 + i * 28, t, 11, col, "start")
    s += text(W / 2, 296, "FRAM — туди, де пишуть ДУЖЕ часто; Flash — туди, де треба БАГАТО місця.",
              11, INK, "middle", "bold")
    save("fig-r03-3c-1-vs-flash.svg", s)


# ── Рис. 4.3.3c.2 — FRAM-модуль на I²C ───────────────────────────────────────
def fig3c2_wiring():
    W, H = 880, 300
    s = header(W, H)
    s += text(W / 2, 32, "FRAM-модуль (MB85-клас) на I²C до ESP32", 18, INK, "middle", "bold")
    s += blk2(80, 110, 150, 120, "ESP32", ["3.3 В"], LBLUE, BLUE, BLUE)
    s += blk2(650, 110, 160, 120, "FRAM", ["MB85RC"], LGRN, GREEN, GREEN)
    wires = [("SDA", "лінія даних I²C", BLUE),
             ("SCL", "лінія такту I²C", BLUE),
             ("VCC", "живлення 3.3 В", GREEN),
             ("GND", "спільна земля", INK)]
    for i, (lab, note, col) in enumerate(wires):
        y = 128 + i * 26
        s += line(230, y, 650, y, col, 1.6)
        s += text(440, y - 5, lab, 9.4, col, "middle", "bold")
        s += text(440, y + 11, note, 8.2, GREY, "middle")
    s += rect(150, 250, 600, 42, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 275, "Дві лінії I²C — і готово. Ніжки A0–A2 задають адресу, WP захищає від запису.",
              10, INK, "middle", "bold")
    save("fig-r03-3c-2-wiring.svg", s)


# ── Рис. 4.3.1a.1 — кільцевий лог ────────────────────────────────────────────
def fig1a1_ring():
    W, H = 880, 330
    s = header(W, H)
    s += text(W / 2, 32, "Кільцевий лог: пишемо по колу", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "журнал тече сектором за сектором; дійшов до краю — вертається на початок",
              10.5, GREY, "middle", style="italic")
    x0, y, cw, h = 70, 140, 122, 74
    cells = [("s0", "старі записи", FAINT, "#fcfcfc"),
             ("s1", "старі записи", FAINT, "#fcfcfc"),
             ("s2", "голова: пишемо сюди", GREEN, LGRN),
             ("s3", "стерти наперед", GOLD, LAMB),
             ("s4", "найдавніше", RED, LRED),
             ("s5", "старі записи", FAINT, "#fcfcfc")]
    for i, (name, note, col, fill) in enumerate(cells):
        x = x0 + i * cw
        dash = ' stroke-dasharray="6 4"' if name == "s3" else ""
        s += (f'<rect x="{x}" y="{y}" width="{cw-8}" height="{h}" rx="6" fill="{fill}" '
              f'stroke="{col}" stroke-width="2"{dash}/>\n')
        s += text(x + (cw - 8) / 2, y + 26, name, 12, col if col != FAINT else GREY, "middle", "bold")
        s += text(x + (cw - 8) / 2, y + 48, note, 8.4, INK if col != FAINT else GREY, "middle")
    # head arrow
    hx = x0 + 2 * cw + (cw - 8) / 2
    s += arrow(hx, y - 26, hx, y - 4, GREEN, 2.2)
    s += text(hx, y - 32, "голова", 9, GREEN, "middle", "bold")
    # wrap arrow from s5 back to s0
    sx = x0 + 5 * cw + (cw - 8)
    s += ('<path d="M{a},{b} C {a2},{c} {d},{c} {e},{b2}" fill="none" stroke="{col}" '
          'stroke-width="2" marker-end="url(#aBlue)"/>\n').format(
        a=sx - 4, b=y + h + 6, a2=sx + 30, c=y + h + 48, d=x0 - 20, e=x0 + 6, b2=y + h + 6, col=BLUE)
    s += text(W / 2, y + h + 44, "по колу: з кінця — знову на початок", 10, BLUE, "middle", "bold")
    s += text(W / 2, 300, "Пишемо в голову; сектор попереду стираємо наперед; найдавніше затирається. "
                          "Записи лягають у всі сектори по черзі — знос розмазується сам (§4.3.3).",
              9.6, INK, "middle")
    save("fig-r03-1a-1-ring.svg", s)


# ── Рис. 4.3.1a.2 — запис і відновлення ──────────────────────────────────────
def fig1a2_record():
    W, H = 880, 300
    s = header(W, H)
    s += text(W / 2, 32, "Один запис і відновлення при старті", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "номер по порядку дає лад, мітка цілості відсіює обірване",
              10.5, GREY, "middle", style="italic")
    # record format

    def rec(x, y, num, body, ok):
        col = GREEN if ok else RED
        o = rect(x, y, 90, 40, "#eef3ff", BLUE, 1.6, 6) + text(x + 45, y + 25, "№ " + num, 11, BLUE, "middle", "bold")
        o += rect(x + 90, y, 200, 40, "#fbfbff", INK, 1.6, 0) + text(x + 190, y + 25, body, 10, INK, "middle")
        o += rect(x + 290, y, 110, 40, _tint(col), col, 1.6, 6)
        o += text(x + 345, y + 25, ("✓ цілий" if ok else "✗ обірваний"), 10, col, "middle", "bold")
        return o

    s += text(150, 96, "Формат запису:", 11, INK, "start", "bold")
    s += rec(150, 108, "105", "…подія…", True)
    s += rec(150, 158, "106", "…поді—", False)
    s += text(600, 96, "При старті:", 11, INK, "start", "bold")
    s += text(600, 124, "• знайти найбільший № з доброю міткою", 9.6, INK, "start")
    s += text(620, 146, "→ це найновіший запис", 9.6, GREEN, "start", "bold")
    s += text(600, 172, "• обірвані (хибна мітка) — пропустити", 9.6, RED, "start")
    s += line(560, 96, 560, 188, FAINT, 1.4)
    s += rect(150, 222, 580, 56, "#fbfbfb", GREY, 1.4, 10)
    s += text(440, 246, "Мітка цілості — той самий прийом, що й у §4.3.7: збій під час запису", 9.8, INK, "middle")
    s += text(440, 266, "лишає останній запис обірваним, і відновлення спокійно його відкидає.", 9.8, GREY, "middle")
    save("fig-r03-1a-2-record.svg", s)


# ── Рис. 4.3.4a.1 — анатомія CSV ─────────────────────────────────────────────
def fig4a1_csv():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 32, "CSV таблиці розділів: п'ять стовпців у рядку", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "людина пише цей текст; збірка перетворює його на двійкову таблицю у Flash",
              10.3, GREY, "middle", style="italic")
    cols = ["name", "type", "subtype", "offset", "size"]
    cx = [120, 250, 360, 500, 640]
    s += rect(70, 84, 760, 132, "#fbfbff", INK, 1.6, 8)
    for c, x in zip(cols, cx):
        s += text(x, 106, c, 12, BLUE, "middle", "bold")
    rows = [("nvs", "data", "nvs", "0x9000", "0x4000"),
            ("factory", "app", "factory", "0x10000", "0x100000"),
            ("ota_0", "app", "ota_0", "0x110000", "0x100000")]
    for r, row in enumerate(rows):
        y = 134 + r * 26
        for v, x in zip(row, cx):
            s += text(x, y, v, 11, INK, "middle")
    notes = [("name", "як ти її звеш"), ("type", "app (код) чи data"),
             ("subtype", "nvs / ota / factory / spiffs…"),
             ("offset", "де починається (порожньо = одразу за попередньою)"),
             ("size", "скільки байтів (можна в K чи M)")]
    y = 250
    for i, (c, note) in enumerate(notes):
        s += text(90, y + i * 16, "• " + c + " — " + note, 9.6, INK, "start")
    save("fig-r03-4a-1-csv.svg", s)


# ── Рис. 4.3.4a.2 — як складаються зсуви ─────────────────────────────────────
def fig4a2_offsets():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Як складаються зсуви: кожен = попередній + його розмір", 17, INK, "middle", "bold")
    s += text(W / 2, 54, "межі кратні 4 КБ (0x1000), а app-розділи — 64 КБ (0x10000)",
              10.5, GREY, "middle", style="italic")
    # bottom-up stacked map
    parts = [("nvs", "0x9000", "0x4000", BLUE),
             ("otadata", "0xd000", "0x2000", BLUE),
             ("phy", "0xf000", "0x1000", BLUE),
             ("factory (app)", "0x10000", "0x100000", GREEN),
             ("ota_0 (app)", "0x110000", "0x100000", GREEN),
             ("ota_1 (app)", "0x210000", "0x100000", GREEN)]
    x, w = 120, 300
    yb, hh = 320, 38
    for i, (name, off, size, col) in enumerate(parts):
        y = yb - i * (hh + 4)
        s += rect(x, y, w, hh, _tint(col), col, 1.6, 5)
        s += text(x + 12, y + 24, name, 11, col, "start", "bold")
        s += text(x + w - 12, y + 24, "розмір " + size, 9.3, GREY, "end")
        s += text(x - 12, y + 24, off, 10, INK, "end")
    s += text(x - 12, yb + 34, "зсув", 9, GREY, "end", "bold")
    # arithmetic on the right
    ax = 480
    s += text(ax, 100, "Зсув кожної = зсув + розмір попередньої:", 11, INK, "start", "bold")
    calc = ["0x9000 + 0x4000 = 0xd000   → otadata",
            "0xd000 + 0x2000 = 0xf000   → phy",
            "0xf000 + 0x1000 = 0x10000  → factory",
            "0x10000 + 0x100000 = 0x110000 → ota_0",
            "0x110000 + 0x100000 = 0x210000 → ota_1"]
    for i, ln in enumerate(calc):
        s += text(ax, 128 + i * 24, ln, 9.6, INK, "start")
    s += rect(ax, 262, 360, 70, "#fbfbfb", GREY, 1.4, 10)
    s += text(ax + 180, 286, "Порожній offset збірка заповнює сама —", 9.6, INK, "middle")
    s += text(ax + 180, 304, "кладе розділ одразу за попереднім.", 9.6, GREY, "middle")
    s += text(ax + 180, 322, "Сума всіх розділів ≤ обсяг Flash.", 9.6, RED, "middle", "bold")
    save("fig-r03-4a-2-offsets.svg", s)


# ── Рис. 4.3.5a.1 — сторінки й записи NVS ────────────────────────────────────
def fig5a1_pages():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "NVS зсередини: сторінки й записи", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "розділ ділиться на сторінки; оновлення дописує новий запис, старий гасить",
              10.3, GREY, "middle", style="italic")
    # partition -> pages
    s += rect(60, 80, 360, 70, "#fbfbff", INK, 1.6, 8)
    s += text(240, 100, "розділ nvs", 10, GREY, "middle", "bold")
    s += blk(74, 112, 100, 30, "сторінка", "активна", LGRN, GREEN, GREEN)
    s += blk(184, 112, 100, 30, "сторінка", "повна", LAMB, GOLD, "#8a6d1a")
    s += blk(294, 112, 110, 30, "сторінка", "вільна", "#f4f4f4", GREY, GREY)
    s += arrow(240, 152, 240, 176, GREY, 1.8)
    s += text(560, 100, "сторінка = один сектор (4 КБ),", 9.6, INK, "middle")
    s += text(560, 118, "усередині — низка записів по 32 байти", 9.6, GREY, "middle")
    # zoom: entries in active page
    x0, y, cw = 70, 190, 150
    cells = [("wifi_ssid", "✓ записано", GREEN, LGRN),
             ("volume=7", "✗ застаріло", RED, LRED),
             ("volume=8", "✓ записано", GREEN, LGRN),
             ("вільно", "", GREY, "#fcfcfc"),
             ("вільно", "", GREY, "#fcfcfc")]
    for i, (lab, st, col, fill) in enumerate(cells):
        x = x0 + i * cw
        s += rect(x, y, cw - 8, 56, fill, col, 1.6, 6)
        s += text(x + (cw - 8) / 2, y + 24, lab, 11, INK if col != GREY else GREY, "middle", "bold")
        if st:
            s += text(x + (cw - 8) / 2, y + 44, st, 9, col, "middle")
    s += text(x0, y - 8, "активна сторінка зблизька →", 9, GREY, "start")
    s += text(x0 + 2 * cw + 60, y + 78, "↑ оновили volume: новий запис дописано, старий — застарілий",
              9.2, INK, "start")
    # bit-state trick
    s += rect(70, 300, 760, 48, LAMB, GOLD, 1.4, 10)
    s += text(450, 322, "Стан запису — 2 біти: 11 (порожньо) → 10 (записано) → 00 (застаріло).", 10, INK, "middle", "bold")
    s += text(450, 340, "Перехід лише гасить біти 1→0 — а це Flash уміє без стирання (§4.3.2).", 9.3, GREY, "middle")
    save("fig-r03-5a-1-pages.svg", s)


# ── Рис. 4.3.5a.2 — збирання сміття ──────────────────────────────────────────
def fig5a2_gc():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 32, "Збирання сміття: повернути місце від застарілого", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "чинні записи переносять на чисту сторінку, стару — стирають цілком",
              10.5, GREY, "middle", style="italic")
    # full page
    s += rect(70, 96, 230, 150, LAMB, GOLD, 1.8, 10)
    s += text(185, 118, "повна сторінка", 11, "#8a6d1a", "middle", "bold")
    marks = ["✓", "✗", "✗", "✓", "✗", "✓"]
    for i, mk in enumerate(marks):
        col = GREEN if mk == "✓" else RED
        s += rect(92 + (i % 3) * 70, 132 + (i // 3) * 44, 60, 36, _tint(col), col, 1.4, 5)
        s += text(122 + (i % 3) * 70, 155 + (i // 3) * 44, mk, 13, col, "middle", "bold")
    s += text(185, 236, "багато застарілих (✗)", 9, GREY, "middle")
    s += arrow(305, 170, 380, 170, INK, 2.4)
    s += text(343, 158, "перенести", 8.6, INK, "middle")
    s += text(343, 184, "лише ✓", 8.6, GREEN, "middle")
    # fresh page
    s += rect(390, 96, 230, 150, LGRN, GREEN, 1.8, 10)
    s += text(505, 118, "чиста сторінка", 11, GREEN, "middle", "bold")
    for i in range(3):
        s += rect(415 + i * 66, 140, 56, 36, _tint(GREEN), GREEN, 1.4, 5)
        s += text(443 + i * 66, 163, "✓", 13, GREEN, "middle", "bold")
    s += text(505, 210, "тільки чинні записи", 9, GREY, "middle")
    s += arrow(625, 170, 690, 170, RED, 2.2)
    s += rect(695, 120, 150, 100, "#f4f4f4", GREY, 1.6, 10)
    s += text(770, 165, "стару —", 10.5, INK, "middle")
    s += text(770, 184, "стерти", 11, RED, "middle", "bold")
    s += text(W / 2, 296, "Так повертають місце, з'їдене застарілими, а заразом розмазують знос по сторінках (§4.3.3).",
              10, INK, "middle", "bold")
    save("fig-r03-5a-2-gc.svg", s)


# ── Рис. 4.3.7a.1 — два слоти конфігу ────────────────────────────────────────
def fig7a1_slots():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 32, "Два слоти конфігу: версія + дані + сума", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "пишемо в старіший слот; новіший лишається цілим запасом",
              11, GREY, "middle", style="italic")

    def slot(x, name, ver, col):
        o = rect(x, 92, 330, 80, _tint(col), col, 2, 10)
        o += text(x + 16, 118, name, 12.5, col, "start", "bold")
        for j, (lab, w) in enumerate([("версія " + ver, 96), ("дані", 120), ("сума ✓", 80)]):
            pass
        o += rect(x + 16, 130, 90, 30, "#fff", col, 1.4, 5) + text(x + 61, 150, "версія " + ver, 9.6, col, "middle", "bold")
        o += rect(x + 116, 130, 120, 30, "#fff", INK, 1.4, 5) + text(x + 176, 150, "дані", 9.6, INK, "middle")
        o += rect(x + 246, 130, 70, 30, "#fff", GREEN, 1.4, 5) + text(x + 281, 150, "сума ✓", 9.2, GREEN, "middle", "bold")
        return o

    s += slot(70, "Слот A  (старіший)", "7", BLUE)
    s += slot(500, "Слот B  (новіший)", "8", GREEN)
    s += arrow(235, 192, 235, 214, RED, 2.2)
    s += text(235, 208, "пишемо сюди → стане версією 9", 9.4, RED, "middle", "bold")
    s += rect(120, 232, 660, 72, LAMB, GOLD, 1.4, 10)
    s += text(450, 256, "При старті: узяти слот із найбільшою версією, що проходить суму.", 11, INK, "middle", "bold")
    s += text(450, 278, "Поки пишемо A, цілий B чекає запасом; не дописали A — беремо B.", 10, GREY, "middle")
    s += text(450, 296, "Хоч би коли впало живлення — лишається щонайменше одна добра копія.", 9.6, GREEN, "middle", "bold")
    save("fig-r03-7a-1-slots.svg", s)


# ── Рис. 4.3.7a.2 — порядок запису ───────────────────────────────────────────
def fig7a2_order():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 32, "Порядок запису: підпис версії — ОСТАННІМ", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "саме останній запис «робить слот дійсним» — це і є точка фіксації",
              10.5, GREY, "middle", style="italic")
    steps = [("1", "стерти слот", BLUE, "звільнити сектор"),
             ("2", "записати дані", BLUE, "payload цілком"),
             ("3", "записати {версія, сума}", RED, "ОСТАННІМ — фіксація")]
    x = 70
    for n, lab, col, sub in steps:
        s += rect(x, 92, 250, 78, _tint(col), col, 1.8, 10)
        s += text(x + 28, 122, n, 16, col, "middle", "bold")
        s += text(x + 145, 118, lab, 11.5, INK, "middle", "bold")
        s += text(x + 145, 142, sub, 9.2, col if col == RED else GREY, "middle", "bold" if col == RED else "normal")
        if n != "3":
            s += arrow(x + 250, 131, x + 290, 131, GREY, 2)
        x += 290
    s += rect(70, 200, 760, 104, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 226, "Чому останнім? Бо доти, доки {версія, сума} не лягли, слот «недійсний».", 11, INK, "middle", "bold")
    s += text(450, 250, "• збій ДО кроку 3 → слот без дійсного заголовка → беремо інший слот;", 10, INK, "middle")
    s += text(450, 270, "• збій ПІСЛЯ кроку 3 → слот цілий і найновіший → беремо його.", 10, INK, "middle")
    s += text(450, 292, "Один останній запис — той самий атомарний перемикач із §4.3.7.", 9.6, GREEN, "middle", "bold")
    save("fig-r03-7a-2-order.svg", s)


# ── Рис. 4.3.3m.1 — три важелі строку служби ─────────────────────────────────
def fig3m1_levers():
    W, H = 880, 320
    s = header(W, H)
    s += text(W / 2, 32, "Скільки протягне Flash: три важелі", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "строк служби росте з ресурсом, із вирівнюванням — і падає з частотою записів",
              10.3, GREY, "middle", style="italic")
    # equation
    s += rect(250, 92, 380, 70, "#fbfbff", INK, 1.8, 12)
    s += text(310, 138, "T", 26, INK, "middle", "bold")
    s += text(345, 138, "=", 22, GREY, "middle")
    s += text(430, 122, "E · N", 20, GREEN, "middle", "bold")
    s += line(390, 132, 470, 132, INK, 1.6)
    s += text(430, 154, "u", 20, RED, "middle", "bold")
    s += text(560, 138, "(днів)", 12, GREY, "middle")
    # levers
    levs = [(GREEN, "E", "ресурс: циклів стирання на сектор (напр. 100 000)"),
            (GREEN, "N", "вирівнювання: скільки секторів ділять знос"),
            (RED, "u", "частота: стирань на день (більша — гірше)"),
            (INK, "T", "строк служби, що з цього виходить")]
    y = 196
    for col, sym, txt in levs:
        s += text(120, y, sym, 14, col, "middle", "bold")
        s += text(150, y, "— " + txt, 11, INK, "start")
        y += 28
    s += text(W / 2, 312, "Побільшити E чи N — або поменшити u — і строк служби росте.", 10.5, INK, "middle", "bold")
    save("fig-r03-3m-1-levers.svg", s)


# ── Рис. 4.3.3m.2 — той самий лічильник, три долі ────────────────────────────
def fig3m2_example():
    W, H = 880, 320
    s = header(W, H)
    s += text(W / 2, 32, "Той самий лічильник, три долі", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "E = 100 000 циклів; міняємо лише вирівнювання й частоту",
              11, GREY, "middle", style="italic")
    rows = [("1 сектор · кожні 10 с", "≈ 12 днів", RED, 80, "✗ помирає за два тижні"),
            ("20 секторів · кожні 10 с", "≈ 230 днів", GOLD, 230, "вирівнювання × 20"),
            ("20 секторів · щогодини", "≈ 200+ років", GREEN, 560, "✓ рідше + вирівнювання")]
    y = 96
    for lab, res, col, bw, note in rows:
        s += text(70, y + 22, lab, 11, INK, "start", "bold")
        s += rect(330, y + 6, bw, 30, _tint(col), col, 1.6, 5)
        s += text(330 + bw + 10, y + 27, res, 12, col, "start", "bold")
        s += text(70, y + 40, note, 9, GREY, "start")
        y += 64
    s += rect(120, 292, 0, 0, FAINT, FAINT, 0)
    s += text(W / 2, 306, "Два головні важелі: вирівнювання (× секторів) і рідші записи (÷ частоту).",
              10.5, INK, "middle", "bold")
    save("fig-r03-3m-2-example.svg", s)


# ── Рис. 4.3.9m.1 — хеш як відбиток ──────────────────────────────────────────
def fig9m1_hash():
    W, H = 880, 310
    s = header(W, H)
    s += text(W / 2, 32, "Хеш: короткий відбиток будь-яких даних", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "з даних будь-якого розміру — коротке число сталої довжини",
              11, GREY, "middle", style="italic")
    s += rect(70, 90, 230, 70, LBLUE, BLUE, 1.8, 10)
    s += text(185, 120, "дані", 13, BLUE, "middle", "bold")
    s += text(185, 142, "(будь-який розмір)", 9.5, GREY, "middle")
    s += arrow(300, 125, 380, 125, INK, 2.4)
    s += text(340, 113, "Hash", 10, INK, "middle", "bold")
    s += rect(380, 100, 200, 50, LAMB, GOLD, 1.8, 8)
    s += text(480, 130, "7A3F…  (короткий)", 11.5, "#8a6d1a", "middle", "bold")
    # one-bit change
    s += text(70, 196, "Зміна навіть на біт → геть інший відбиток:", 10.5, INK, "start", "bold")
    s += text(90, 220, "\"привіт\"", 11, INK, "start")
    s += text(300, 220, "→  7A3F C18D …", 11, GREEN, "start", "bold")
    s += text(90, 242, "\"привіт.\"", 11, INK, "start")
    s += text(300, 242, "→  C19B 04E7 …  (одна крапка!)", 11, RED, "start", "bold")
    s += rect(70, 264, 740, 34, "#fbfbfb", GREY, 1.4, 8)
    s += text(440, 285, "Однобічна (з відбитка не відновити дані) і без колізій (двоє різних з тим самим відбитком — практично неможливо).",
              9.2, INK, "middle")
    save("fig-r03-9m-1-hash.svg", s)


# ── Рис. 4.3.9m.2 — підпис і перевірка ───────────────────────────────────────
def fig9m2_sign():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 32, "Підпис і перевірка: хеш + пара ключів", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "тільки таємний ключ міг підписати; будь-хто з відкритим — перевірити",
              10.3, GREY, "middle", style="italic")
    # maker side
    s += rect(60, 84, 360, 110, "#fbfbff", INK, 1.6, 10)
    s += text(240, 106, "у виробника", 11, INK, "middle", "bold")
    s += text(80, 134, "дані → Hash → h", 11, INK, "start")
    s += text(80, 162, "h → Sign(таємний ключ) → підпис", 11, GOLD, "start", "bold")
    # device side
    s += rect(480, 84, 360, 110, "#fbfbff", INK, 1.6, 10)
    s += text(660, 106, "на пристрої", 11, INK, "middle", "bold")
    s += text(500, 134, "дані → Hash → h′", 11, INK, "start")
    s += text(500, 162, "підпис → Verify(відкритий) → h", 11, BLUE, "start", "bold")
    s += arrow(420, 139, 480, 139, GREY, 2.2)
    s += text(450, 127, "віддаємо", 8, GREY, "middle")
    # compare
    s += rect(300, 220, 300, 60, LGRN, GREEN, 1.8, 10)
    s += text(450, 246, "порівняти  h  vs  h′", 13, GREEN, "middle", "bold")
    s += text(450, 268, "збіг → справжнє ✓     ні → підробка ✗", 10, INK, "middle")
    s += text(W / 2, 308, "Підмінити дані й лишити підпис чинним не можна: інший хеш не зійдеться,",
              10, GREY, "middle")
    s += text(W / 2, 326, "а поставити новий підпис без таємного ключа — годі.", 10, GREY, "middle")
    save("fig-r03-9m-2-sign.svg", s)


# ── Рис. 4.3.6i.1 — ланцюг кластерів ─────────────────────────────────────────
def fig6i1_chain():
    W, H = 880, 340
    s = header(W, H)
    s += text(W / 2, 32, "Чому «таблиця розміщення»: ланцюг кластерів", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "для кожного кластера таблиця каже, де НАСТУПНИЙ шматок файлу",
              10.5, GREY, "middle", style="italic")
    # disk clusters (scattered), file uses 2,3,7
    x0, y, cw = 70, 90, 70
    used = {2: GREEN, 3: GREEN, 7: GREEN}
    for i in range(10):
        x = x0 + i * cw
        col = used.get(i, FAINT)
        fill = _tint(col) if i in used else "#fcfcfc"
        s += rect(x, y, cw - 8, 44, fill, col, 1.6, 5)
        s += text(x + (cw - 8) / 2, y + 28, str(i), 11, INK if i in used else GREY, "middle", "bold")
    s += text(x0, y - 10, "кластери на диску →", 9, GREY, "start")
    s += text(x0 + 9 * cw + 30, y + 28, "файл «лист.txt» — у 2, 3, 7", 9.5, GREEN, "end", "bold")
    # table
    s += text(150, 176, "Таблиця (FAT):", 12, INK, "start", "bold")
    chain = [("кластер 2", "→ 3"), ("кластер 3", "→ 7"), ("кластер 7", "→ кінець")]
    for i, (a, b) in enumerate(chain):
        x = 150 + i * 230
        s += rect(x, 190, 200, 44, LBLUE, BLUE, 1.6, 6)
        s += text(x + 70, 217, a, 11, INK, "middle", "bold")
        s += text(x + 160, 217, b, 11, BLUE, "middle", "bold")
        if i < 2:
            s += arrow(x + 200, 212, x + 230, 212, GREY, 2)
    s += rect(120, 268, 640, 56, "#fbfbfb", GREY, 1.4, 10)
    s += text(440, 292, "Файл лежить клаптями, а таблиця зчіплює їх у ланцюг: 2 → 3 → 7 → кінець.", 10.5, INK, "middle", "bold")
    s += text(440, 312, "Ось ця «таблиця розміщення файлів» і дала системі назву FAT.", 9.8, GREY, "middle")
    save("fig-r03-6i-1-chain.svg", s)


# ── Рис. 4.3.6i.2 — шлях FAT у часі ──────────────────────────────────────────
def fig6i2_timeline():
    W, H = 920, 260
    s = header(W, H)
    s += text(W / 2, 32, "Шлях FAT: від терміналу 1977-го до вашої картки", 18, INK, "middle", "bold")
    s += line(70, 150, 850, 150, INK, 2)
    marks = [(120, "1977–78", "Марк Макдональд,", "Microsoft — FAT8", BLUE),
             (300, "1980", "Тім Патерсон, SCP", "— FAT12 → 86-DOS", GREEN),
             (470, "1984", "FAT16", "(більші диски)", INK),
             (620, "1996", "FAT32", "(Windows 95)", INK),
             (800, "сьогодні", "USB, SD,", "картки фото", GOLD)]
    for x, yr, a, b, col in marks:
        s += circle(x, 150, 6, col, col, 1)
        s += text(x, 130, yr, 10.5, col, "middle", "bold")
        s += text(x, 178, a, 9, INK, "middle")
        s += text(x, 194, b, 9, GREY, "middle")
    s += text(W / 2, 236, "Ідея — Макдональда (1977), шлях у DOS — Патерсона (1980); далі вона лише ширшала.",
              10, INK, "middle", "bold")
    save("fig-r03-6i-2-timeline.svg", s)


# ── Рис. 4.3.6i.3 — FAT усюди ────────────────────────────────────────────────
def fig6i3_everywhere():
    W, H = 880, 250
    s = header(W, H)
    s += text(W / 2, 32, "FAT живе всюди, де носій виймається", 19, INK, "middle", "bold")
    items = [("дискета", "1980-ті"), ("USB-флешка", "2000-ні"),
             ("SD-картка", "скрізь"), ("картка фотоапарата", "донині")]
    x = 70
    for name, era in items:
        s += rect(x, 86, 180, 90, LAMB, GOLD, 1.8, 12)
        s += text(x + 90, 122, name, 12, "#8a6d1a", "middle", "bold")
        s += text(x + 90, 146, era, 9.5, GREY, "middle")
        s += text(x + 90, 166, "FAT", 11, INK, "middle", "bold")
        x += 200
    s += text(W / 2, 212, "Проста й усім зрозуміла — тому стала спільною мовою знімних носіїв.",
              11, INK, "middle", "bold")
    s += text(W / 2, 232, "SD-стандарт навіть прямо наказує форматувати картки у FAT.", 9.8, GREY, "middle")
    save("fig-r03-6i-3-everywhere.svg", s)


if __name__ == "__main__":
    fig01_memory_gap()
    fig02_nor_nand()
    fig03_credit()
    # §4.3.1 Навіщо зберігати
    fig11_volatile_loss()
    fig12_three_kinds()
    fig13_write_read()
    fig14_where_goes()
    fig15_thermostat()
    fig16_lifecycle()
    # §4.3.2 Flash зсередини
    fig21_erase_write()
    fig22_granularity()
    fig23_hierarchy()
    fig24_update_one_byte()
    fig25_clear_only()
    fig26_why_managers()
    # §4.3.3 Знос і wear leveling
    fig31_why_wear()
    fig32_endurance()
    fig33_hotspot()
    fig34_wear_leveling()
    fig35_math()
    fig36_practical()
    # §4.3.4 Таблиця розділів
    fig41_why_partition()
    fig42_table()
    fig43_layout()
    fig44_types()
    fig45_alignment()
    fig46_custom()
    # §4.3.5 NVS — сховище «ключ–значення»
    fig51_keyvalue()
    fig52_namespace()
    fig53_types()
    fig54_cycle()
    fig55_append()
    fig56_vs_fs()
    # §4.3.6 Файлові системи на Flash; SD-картка
    fig61_tree()
    fig62_namemap()
    fig63_flash_aware()
    fig64_spiffs_littlefs()
    fig65_sd_card()
    fig66_decision()
    # §4.3.7 Цілісність: втрата живлення посеред запису
    fig71_window()
    fig72_torn()
    fig73_atomic()
    fig74_checksum()
    fig75_double_slot()
    fig76_who_does_it()
    # §4.3.8 Два OTA-слоти: механіка подвійного образу
    fig81_no_overwrite()
    fig82_two_slots()
    fig83_otadata()
    fig84_trial_rollback()
    fig85_cost()
    fig86_same_idea()
    # §4.3.9 Secure boot і шифрування Flash
    fig91_two_threats()
    fig92_signature()
    fig93_chain()
    fig94_secure_boot()
    fig95_flash_enc()
    fig96_caution()
    # 🔌 вставка до 4.3.6 — SD-модуль
    fig6c1_block()
    fig6c2_wiring()
    # 🔌 вставка до 4.3.3 — FRAM
    fig3c1_vs_flash()
    fig3c2_wiring()
    # ⚙️ вставка до 4.3.1 — кільцевий лог
    fig1a1_ring()
    fig1a2_record()
    # ⚙️ вставка до 4.3.4 — власна таблиця розділів
    fig4a1_csv()
    fig4a2_offsets()
    # ⚙️ вставка до 4.3.5 — NVS зсередини
    fig5a1_pages()
    fig5a2_gc()
    # ⚙️ вставка до 4.3.7 — атомарне оновлення конфігу
    fig7a1_slots()
    fig7a2_order()
    # 🧮 вставка до 4.3.3 — арифметика ресурсу
    fig3m1_levers()
    fig3m2_example()
    # 🧮 вставка до 4.3.9 — хеш і цифровий підпис
    fig9m1_hash()
    fig9m2_sign()
    # 📜 історія до 4.3.6 — FAT
    fig6i1_chain()
    fig6i2_timeline()
    fig6i3_everywhere()
    print("OK - figures for Section 4.3 (4.3.1..4.3.9 + s6c s3c s1a s4a s5a s7a s3m s9m s6i) generated in", OUT)
