# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# локальні відтінки під єдину палітру svgkit
AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"


# ── cause-chain: ланцюг FMEA причина → режим → наслідок ───────────────────────
# Ідея: FMEA читає відмову як причинно-наслідковий ланцюг. Причина (чому щось
# зламалось) → режим відмови (ЯК воно проявилось у компонента) → наслідок (що
# відчув користувач/система). Тяжкість живе на кінці-наслідку, а не біля причини.
# Інстинкт інженера — думати від компонента; FMEA змушує думати від наслідку.

def fig_cause_chain():
    W, H = 840, 360
    p = []
    p.append(text(W / 2, 40, "відмова як ланцюг: причина → режим → наслідок", size=15, color=INK, bold=True))

    bw, bh, by = 232, 96, 92
    xs = [28, 304, 580]
    cols = [
        (GREENBG, FIELD, "ПРИЧИНА", "чому зламалось",
         "холодна пайка на виводі;\nпросіла напруга живлення"),
        (AMBERBG, AMBER, "РЕЖИМ ВІДМОВИ", "ЯК це бачить компонент",
         "давач I²C не відповідає\n(шина зависла на low)"),
        (REDBG, POS, "НАСЛІДОК", "що відчула система",
         "висота «застигла» —\nдрон тримає газ і б'ється"),
    ]
    for x, (fill, col, head, sub, body) in zip(xs, cols):
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(x + bw / 2, by + 24, head, size=12.5, color=tagcol, bold=True))
        p.append(text(x + bw / 2, by + 40, sub, size=9.2, color=MUTED, italic=True))
        for j, ln in enumerate(body.split("\n")):
            p.append(text(x + bw / 2, by + 60 + j * 15, ln, size=9.4, color=INK))
    p.append(arrow(xs[0] + bw + 6, by + bh / 2, xs[1] - 6, by + bh / 2, color=INK, sw=2.4))
    p.append(arrow(xs[1] + bw + 6, by + bh / 2, xs[2] - 6, by + bh / 2, color=INK, sw=2.4))

    # де живе тяжкість
    p.append(rect(xs[2], by + bh + 18, bw, 34, fill=BG, stroke=POS, sw=1.6, rx=8))
    p.append(text(xs[2] + bw / 2, by + bh + 39, "тяжкість міряють ТУТ", size=11, color=POS, bold=True))

    # інстинкт проти FMEA
    p.append(rect(40, 268, 760, 64, fill=FILL, stroke=MUTED, sw=1.4, rx=10))
    p.append(text(W / 2, 290, "інстинкт інженера читає ланцюг зліва направо (від деталі);", size=10.6, color=INK))
    p.append(text(W / 2, 310, "FMEA змушує читати справа наліво — спершу «чим це загрожує», потім «звідки прийде»", size=10.6, color=INK, bold=True))
    render(os.path.join(OUT, "cause-chain.svg"), W, H, *p,
           title="Ланцюг FMEA: причина, режим відмови, наслідок")


# ── s-o-d: три осі ризику й пастка перемноження ──────────────────────────────
# Ідея: FMEA важить кожен режим трьома незалежними числами 1..10 — Тяжкість
# (наскільки боляче), Імовірність (як часто причина), Виявність (наскільки легко
# спіймати ВЧАСНО; 10 = майже не спіймати). Класичний RPN = S·O·D зводить їх в одне
# число — і це пастка: два однакові добутки приховують дуже різну небезпеку.

def fig_sod():
    W, H = 840, 410
    p = []
    p.append(text(W / 2, 38, "три осі ризику — і пастка одного числа", size=15, color=INK, bold=True))

    axes = [
        ("S — Тяжкість", "наскільки боляче,\nякщо станеться", "наслідок", FIELD, GREENBG),
        ("O — Імовірність", "як часто\nз'являється причина", "причина", NEG, BLUEBG),
        ("D — Виявність", "чи спіймаємо ВЧАСНО\n(10 = майже ні)", "контроль", AMBER, AMBERBG),
    ]
    bw, bh, by = 244, 92, 70
    xs = [28, 298, 568]
    for x, (head, sub, where, col, fill) in zip(xs, axes):
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(x + bw / 2, by + 25, head, size=12.5, color=tagcol, bold=True))
        for j, ln in enumerate(sub.split("\n")):
            p.append(text(x + bw / 2, by + 45 + j * 15, ln, size=9.6, color=INK))
        p.append(text(x + bw / 2, by + 82, "1…10", size=10.5, color=tagcol, bold=True))

    # пастка RPN
    ty = 214
    p.append(rect(40, ty, 760, 150, fill=REDBG, stroke=POS, sw=1.8, rx=12))
    p.append(text(W / 2, ty + 26, "пастка: RPN = S · O · D зводить три осі в одне число", size=12.5, color=POS, bold=True))

    # два приклади з однаковим добутком
    cw = 340
    lx, rx2 = 70, W - 70 - cw
    p.append(rect(lx, ty + 42, cw, 92, fill=BG, stroke=POS, sw=1.4, rx=8))
    p.append(text(lx + cw / 2, ty + 64, "відмова гальм, рідкісна, невидима", size=10.6, color=INK, bold=True))
    p.append(text(lx + cw / 2, ty + 86, "S=10 · O=2 · D=9", size=11, color=INK))
    p.append(text(lx + cw / 2, ty + 108, "RPN = 180", size=13, color=POS, bold=True))
    p.append(text(lx + cw / 2, ty + 126, "уб'є з одного разу", size=9.4, color=POS, italic=True))

    p.append(rect(rx2, ty + 42, cw, 92, fill=BG, stroke=NEG, sw=1.4, rx=8))
    p.append(text(rx2 + cw / 2, ty + 64, "косметичний дефект, частий", size=10.6, color=INK, bold=True))
    p.append(text(rx2 + cw / 2, ty + 86, "S=3 · O=6 · D=10", size=11, color=INK))
    p.append(text(rx2 + cw / 2, ty + 108, "RPN = 180", size=13, color=NEG, bold=True))
    p.append(text(rx2 + cw / 2, ty + 126, "дрібниця, лиш дратує", size=9.4, color=NEG, italic=True))

    p.append(text(W / 2, H - 8, "однаковий RPN — протилежна небезпека; тому тяжкість важать ПЕРШОЮ, а не множать наосліп",
                  size=10.6, color=MUTED, italic=True))
    render(os.path.join(OUT, "s-o-d.svg"), W, H, *p,
           title="")


# ── worksheet: рядок FMEA → реальні контрзаходи у прошивці ────────────────────
# Ідея: кожен рядок таблиці FMEA — не папір, а замовлення на код. Режим відмови з
# його S·O·D перетворюється на конкретний захист у прошивці: range-check збиває
# Виявність, watchdog ловить зависання, резерв давача знижує Тяжкість наслідку.

def fig_worksheet():
    W, H = 840, 430
    p = []
    p.append(text(W / 2, 38, "рядок FMEA — це замовлення на код", size=15, color=INK, bold=True))

    # верх: рядок таблиці
    cols = [("Режим", 250), ("Наслідок", 210), ("S·O·D", 110)]
    x0, ry, rh = 40, 64, 56
    cx = x0
    p.append(rect(x0, ry, 570, rh, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=8))
    p.append(line(x0 + 250, ry, x0 + 250, ry + rh, color=AMBER, sw=1.2))
    p.append(line(x0 + 460, ry, x0 + 460, ry + rh, color=AMBER, sw=1.2))
    p.append(text(x0 + 125, ry + 24, "давач висоти завис", size=10.6, color=INK, bold=True))
    p.append(text(x0 + 125, ry + 42, "(I²C не відповідає)", size=9.2, color=MUTED))
    p.append(text(x0 + 355, ry + 24, "втрата керування", size=10.6, color=INK, bold=True))
    p.append(text(x0 + 355, ry + 42, "висотою → падіння", size=9.2, color=MUTED))
    p.append(text(x0 + 515, ry + 24, "9 · 3 · 8", size=12, color=POS, bold=True))
    p.append(text(x0 + 515, ry + 42, "RPN 216", size=9.6, color=POS))

    # три стрілки вниз до контрзаходів
    mids = [x0 + 110, x0 + 355, x0 + 515]
    fixes = [
        (28, "знизити D — ВИЯВНІСТЬ",
         "перевірка діапазону + тайм-аут шини:\nчитання поза [−500..9000] м або\nмовчання > 50 мс → прапор «давач дохлий»",
         FIELD, GREENBG, "if(!ok||alt<-500||alt>9000) fault=1;"),
        (320, "знизити S — ТЯЖКІСТЬ",
         "резерв: барометр + GPS-висота;\nвідмова одного не валить керування —\nперемикач бере справний",
         NEG, BLUEBG, "alt = fault ? alt_baro : alt_lidar;"),
        (575, "тримати O під оком",
         "watchdog: якщо цикл керування\nне «погодував» сторожа вчасно —\nконтрольований перезапуск",
         POS, REDBG, "esp_task_wdt_reset();"),
    ]
    fy = 168
    for x, head, body, col, fill, code in fixes:
        tagcol = AMBERTX if col == AMBER else col
        fw = 244
        p.append(rect(x, fy, fw, 150, fill=fill, stroke=col, sw=1.8, rx=10))
        p.append(text(x + fw / 2, fy + 24, head, size=10.8, color=tagcol, bold=True))
        for j, ln in enumerate(body.split("\n")):
            p.append(text(x + fw / 2, fy + 44 + j * 15, ln, size=8.9, color=INK))
        p.append(rect(x + 10, fy + 112, fw - 20, 28, fill=BG, stroke=col, sw=1.1, rx=5))
        p.append(text(x + fw / 2, fy + 130, code, size=8.4, color=INK))
    # стрілки від рядка до боксів
    p.append(arrow(mids[0], ry + rh, fixes[0][0] + 122, fy, color=FIELD, sw=2))
    p.append(arrow(mids[1], ry + rh, fixes[1][0] + 122, fy, color=NEG, sw=2))
    p.append(arrow(mids[2], ry + rh, fixes[2][0] + 122, fy, color=POS, sw=2))

    p.append(text(W / 2, H - 14, "кожне з трьох чисел б'ється своїм кодом — таблиця стає переліком оборонних рубежів прошивки",
                  size=10.6, color=MUTED, italic=True))
    render(os.path.join(OUT, "worksheet.svg"), W, H, *p,
           title="")


# ── timeline: історія FMEA від військових через NASA до автозаводів ───────────
# Ідея вставки hist-mil-nasa: метод старший за програмування й народився не в
# NASA. Військові 1949 (MIL-P-1629, з критичністю в назві) → NASA 1966 відточила
# під «Аполлон», пожежа 1967 зробила надійність наріжним каменем → заміна
# MIL-P-1629 на MIL-STD-1629 у 1974 збіглася з гучністю космосу → звідси МІФ про
# авторство NASA → автозаводи (Ford 1970-ті, AIAG 1993) дали числа S-O-D і RPN →
# гармонізація AIAG-VDA 2019 прибрала RPN заради Action Priority (тяжкість першою),
# тобто повернула критичність, з якої метод починав 1949-го.

def fig_timeline():
    W, H = 880, 470
    p = []
    p.append(text(W / 2, 34, "сімдесят років FMEA: флот → космос → автозавод", size=15, color=INK, bold=True))

    # вісь часу
    ax_y = 92
    p.append(line(40, ax_y, W - 40, ax_y, color=INK, sw=2.2))
    p.append(arrow(W - 60, ax_y, W - 38, ax_y, color=INK, sw=2.2))

    # три ери — підкладки-смуги
    eras = [
        (40, 250, GREENBG, FIELD, "ВІЙСЬКОВІ"),
        (300, 250, BLUEBG, NEG, "КОСМОС (NASA)"),
        (560, 280, AMBERBG, AMBER, "АВТОЗАВОДИ"),
    ]
    band_y, band_h = 108, 250
    for x, w, fill, col, name in eras:
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, band_y, w, band_h, fill=fill, stroke=col, sw=1.4, rx=10))
        p.append(text(x + w / 2, band_y + 20, name, size=11.5, color=tagcol, bold=True))

    # віхи на лінії часу: точка + рік (опис — у картках нижче)
    dots = [
        (110, "1949", FIELD),
        (360, "1966", NEG),
        (470, "1967", POS),
        (650, "1970-ті", AMBER),
        (770, "1993", AMBER),
    ]
    for x, yr, col in dots:
        tagcol = AMBERTX if col == AMBER else col
        p.append(circle(x, ax_y, 5.5, fill=col, stroke=BG, sw=1.6))
        p.append(text(x, ax_y - 12, yr, size=11, color=tagcol, bold=True))
    # картки-описи в смугах (рівні висоти, щоб не наповзали)
    cards = [
        (52, 138, 226, "MIL-P-1629", "військова процедура;\nFME·C·A — з КРИТИЧНІСТЮ\nвже в самій назві", FIELD, GREENBG),
        (312, 138, 226, "FMECA «Аполлон» 1966", "NASA не винайшла —\nвідточила суворість для\nпілотованого космосу", NEG, BLUEBG),
        (312, 232, 226, "пожежа 1967", "Ґріссом·Вайт·Чаффі;\nнадійність стала\nнаріжним каменем", POS, REDBG),
        (572, 138, 256, "Ford після Pinto, 1970-ті", "метод іде в масове\nвиробництво; слідом —\nуся автоіндустрія", AMBER, BG),
        (572, 232, 256, "AIAG 1993", "числа S·O·D і\nRPN = S·O·D як\nголовний показник", AMBER, BG),
    ]
    for x, y, w, head, body, col, fill in cards:
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, y, w, 84, fill=fill, stroke=col, sw=1.5, rx=8))
        p.append(text(x + w / 2, y + 20, head, size=10.4, color=tagcol, bold=True))
        for j, ln in enumerate(body.split("\n")):
            p.append(text(x + w / 2, y + 40 + j * 14, ln, size=8.8, color=INK))

    # підсвічений розрив-міф: 1974 заміна стандарту ⇒ хибна атрибуція NASA
    gy = band_y + band_h + 16
    p.append(rect(40, gy, 470, 62, fill=REDBG, stroke=POS, sw=1.8, rx=10))
    p.append(text(40 + 235, gy + 20, "1974: MIL-P-1629 → MIL-STD-1629", size=10.8, color=POS, bold=True))
    p.append(text(40 + 235, gy + 39, "старе військове коріння зникло з-під імені, а космос був на слуху →",
                  size=9.2, color=INK))
    p.append(text(40 + 235, gy + 53, "звідси живучий МІФ: «FMEA винайшла NASA» (насправді — ні)",
                  size=9.2, color=POS, italic=True))

    # фінальний поворот: 2019 повертає критичність
    p.append(rect(528, gy, W - 40 - 528, 62, fill=GREENBG, stroke=FIELD, sw=1.8, rx=10))
    cx2 = 528 + (W - 40 - 528) / 2
    p.append(text(cx2, gy + 20, "2019: AIAG-VDA → Action Priority", size=10.8, color=FIELD, bold=True))
    p.append(text(cx2, gy + 39, "RPN прибрано; тяжкість важать ПЕРШОЮ —", size=9.2, color=INK))
    p.append(text(cx2, gy + 53, "критичність 1949-го повернулася на трон", size=9.2, color=FIELD, italic=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p, title="")


if __name__ == "__main__":
    fig_cause_chain()
    fig_sod()
    fig_worksheet()
    fig_timeline()
    print("OK: figures written to", OUT)
