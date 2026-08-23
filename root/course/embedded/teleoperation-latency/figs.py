# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Телекерування: затримки, відеоканал, втрата лінка».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: контур телекерування наземної платформи ───────────────────────
# Ідея: оператор — не «пульт → ровер», а ЗАМКНЕНА петля: очима по відеоканалу
# вниз, руками по каналу керування вгору. Ключова відмінність від коптера —
# безпечний стан ровера є СТАТИЧНИМ (стоп), тож обрив не падає з неба.
def fig_teleop_loop():
    W, H = 940, 430
    P = []
    P.append(text(W / 2, 30, "Телекерування — замкнена петля через дві радіолінії",
                  size=17, bold=True))

    # оператор (ліворуч) і ровер (праворуч)
    op_cx, rv_cx, cy = 165, W - 175, 210
    fr, w, h = textbox(op_cx, cy, "ОПЕРАТОР\nочі + руки\n(на землі)",
                       size=13.5, bold=True, fill="#eef2f7", stroke=INK, min_w=150)
    P.append(fr)
    fr, w, h = textbox(rv_cx, cy, "РОВЕР\nкамера + колеса\n(у полі)",
                       size=13.5, bold=True, fill="#e9f7ef", stroke=FIELD, min_w=150)
    P.append(fr)

    # верхня дуга — керування (вгору, від оператора до ровера)
    up_y = 108
    P.append(arrow(op_cx + 70, up_y, rv_cx - 70, up_y, color=POS, sw=2.2))
    fr, w, h = textbox((op_cx + rv_cx) / 2, up_y - 30,
                       "КЕРУВАННЯ ↑  стік → колеса   (мала затримка, часто, без ретраїв)",
                       size=12, color=POS, bold=True, fill="#fdecea", stroke=POS)
    P.append(fr)

    # нижня дуга — відео (вниз, від ровера до оператора)
    dn_y = 312
    P.append(arrow(rv_cx - 70, dn_y, op_cx + 70, dn_y, color=NEG, sw=2.2))
    fr, w, h = textbox((op_cx + rv_cx) / 2, dn_y + 30,
                       "ВІДЕО ↓  картина з камери → очі   (кодек + буфер → лаг)",
                       size=12, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG)
    P.append(fr)

    # замикання: очі → мозок → руки
    P.append(text((op_cx + rv_cx) / 2, cy - 6, "петля\nдія → бачу → корегую", size=12.5,
                  color=MUTED))
    P.append(text((op_cx + rv_cx) / 2, cy + 30, "затримка будь-де в колі\nрозхитує керування",
                  size=11.5, color=MUTED))

    # виноска: наземне ≠ повітряне
    fr, w, h = textbox(W / 2, H - 30,
                       "Відмінність від коптера: безпечний стан ровера — СТОЯТИ. "
                       "Обрив ⇒ гальмуй і чекай; апарат не падає.",
                       size=12.5, bold=True, fill="#e9f7ef", stroke=FIELD)
    P.append(fr)

    render("img/teleop-loop.svg", W, H, *P)


# ── Фігура 2: бюджет наскрізної затримки (дві доріжки) ───────────────────────
# Ідея: і «скло-до-скла» (відео), і «стік-до-колеса» (керування) — це СУМА
# ланок. Показуємо стеком, щоб видно було, яка ланка найтовща (буфер!).
def fig_latency_budget():
    W, H = 940, 470
    P = []
    P.append(text(W / 2, 30, "Наскрізна затримка — це сума ланок ланцюга",
                  size=17, bold=True))

    x0 = 150            # ліва межа доріжок
    x1 = W - 40
    scale = (x1 - x0) / 120.0   # px на 1 мс, шкала до ~120 мс

    # --- доріжка ВІДЕО (скло-до-скла) ---
    def track(y, label, segs, total_lbl):
        pp = []
        pp.append(text(x0 - 12, y + 15, label, size=12.5, bold=True, anchor="end"))
        x = x0
        for name, ms, col in segs:
            wpx = ms * scale
            pp.append(rect(x, y, wpx, 30, fill=col, stroke=INK, sw=1.2, rx=3))
            if wpx > 34:
                pp.append(text(x + wpx / 2, y + 20, "%d" % ms, size=11.5, color="#ffffff", bold=True))
            x += wpx
        pp.append(text(x + 8, y + 20, total_lbl, size=12, bold=True, anchor="start"))
        return pp, x

    vy = 92
    vsegs = [("захоп.", 12, "#5b7aa8"), ("кодек", 10, "#5b7aa8"),
             ("канал", 8, "#8e44ad"), ("БУФЕР", 20, "#c0392b")]
    pp, vend = track(vy, "ВІДЕО ↓", vsegs, "= 50 мс «скло-до-скла»")
    P.extend(pp)

    cy = 152
    csegs = [("зчит.стіка", 3, "#5b7aa8"), ("радіо RC", 6, "#8e44ad"),
             ("цикл FC", 3, "#27ae60"), ("реакція колеса", 8, "#27ae60")]
    pp, cend = track(cy, "КЕРУВАННЯ ↑", csegs, "= 20 мс «стік-до-колеса»")
    P.extend(pp)

    # легенда сегментів
    ly = 210
    leg = [("обчислення на кінцях", "#5b7aa8"), ("політ по радіо", "#8e44ad"),
           ("контролер / механіка", "#27ae60"), ("буфер приймача", "#c0392b")]
    lx = x0
    for name, col in leg:
        P.append(rect(lx, ly, 16, 16, fill=col, stroke=INK, sw=1, rx=3))
        P.append(text(lx + 22, ly + 13, name, size=11.5, anchor="start"))
        lx += text_width(name, 11.5) + 60

    # висновок: найтовща ланка — буфер; радіо найзмінніше
    fr, w, h = textbox(W * 0.30, 300,
                       "Найтовща ланка відео —\nБУФЕР приймача.\nМенший буфер ⇒ менший лаг,\nале більше смиків.",
                       size=12, fill="#fdecea", stroke=POS, bold=True)
    P.append(fr)
    fr, w, h = textbox(W * 0.70, 300,
                       "Найпідступніша —\nРАДІО: у завадах ретраї,\nі затримка СТРИБАЄ.\nБюджет рахуй по гіршому.",
                       size=12, fill="#f2ecf7", stroke="#8e44ad", bold=True)
    P.append(fr)

    fr, w, h = textbox(W / 2, H - 34,
                       "Порог відчуття: керування ровером терпить більше за коптер, "
                       "та понад ~200–300 мс «наосліп» уже небезпечно.",
                       size=12.5, bold=True, fill="#eef2f7", stroke=INK)
    P.append(fr)

    render("img/latency-budget.svg", W, H, *P)


# ── Фігура 3: східчастий failsafe за пропущеними серцебиттями ────────────────
# Ідея: обрив лінка — не «біт зв'язку є / нема», а СХІДЦІ у часі: поки мовчання
# коротке — тримай курс; довше — стоп; ще довше — активна безпечна дія.
def fig_failsafe_ladder():
    W, H = 1040, 440
    P = []
    P.append(text(W / 2, 30, "Втрата лінка — східчастий failsafe за тишею в ефірі",
                  size=17, bold=True))

    # вісь часу від останнього доброго пакета
    ax_y = 150
    ax_x0, ax_x1 = 80, W - 70
    P.append(line(ax_x0, ax_y, ax_x1, ax_y, color=MUTED, sw=1.5))
    P.append(text(ax_x0, ax_y + 40, "останній\nдобрий пакет", size=11, color=MUTED))
    P.append(text(ax_x1, ax_y - 12, "тиша в ефірі →", size=12, color=MUTED, anchor="end"))

    # пороги: t0 (норма), 0.2с (hold), 1с (safe-stop), 5с (rtb)
    def tick(frac, label, col):
        x = ax_x0 + frac * (ax_x1 - ax_x0 - 20)
        P.append(line(x, ax_y - 10, x, ax_y + 10, color=col, sw=2))
        P.append(text(x, ax_y - 18, label, size=11.5, color=col, bold=True))
        return x

    x_hold = tick(0.18, "0.2 с", POS)
    x_stop = tick(0.44, "1 с", POS)
    x_rtb = tick(0.70, "5 с", NEG)

    # стани як рамки під порогами — рівномірно по чотирьох чвертях осі
    def state(cx, txt, col, fill):
        fr, w, h = textbox(cx, ax_y + 95, txt, size=12, color=col, bold=True,
                           fill=fill, stroke=col)
        P.append(fr)

    span = ax_x1 - ax_x0
    state(ax_x0 + 0.10 * span, "NORMAL\nвиконуй\nкоманди", FIELD, "#e9f7ef")
    state(ax_x0 + 0.34 * span, "HOLD\nтримай курс,\nне гальмуй різко", "#b8860b", "#fdf6e3")
    state(ax_x0 + 0.60 * span, "SAFE-STOP\nплавно стій,\nсирена/маяк", POS, "#fdecea")
    state(ax_x0 + 0.84 * span, "RTB / чекай\n(за політикою)", NEG, "#eaf0fd")

    # серцебиття, що обривається
    for i, fr in enumerate([0.02, 0.08, 0.14]):
        x = ax_x0 + fr * (ax_x1 - ax_x0 - 20)
        P.append(line(x, ax_y, x, ax_y - 26, color=FIELD, sw=2))
        P.append(circle(x, ax_y - 30, 3, fill=FIELD, stroke=FIELD))
    for fr in [0.24, 0.30, 0.36, 0.42]:
        x = ax_x0 + fr * (ax_x1 - ax_x0 - 20)
        P.append(text(x, ax_y - 22, "✕", size=13, color=POS, bold=True))

    # висновок
    fr, w, h = textbox(W / 2, H - 38,
                       "Пороги — з ПОРЯДКОМ реакції: коротка тиша не мусить смикати кермо, довга — мусить зупинити.\n"
                       "Кожен поріг задає розробник під конкретну платформу й місію.",
                       size=12.5, bold=True, fill="#eef2f7", stroke=INK)
    P.append(fr)

    render("img/failsafe-ladder.svg", W, H, *P)


# ── Фігура 4 (вставка hist): «індивідуалізація» телеавтомата Тесли ───────────
# Ідея: перше інженерне питання телекерування — не «як передати», а «ЧИЙ голос
# слухати». Приймач човна 1898 р. відгукується лише на власні періоди (як на
# ім'я); чужий передавач/завада не вмикають нічого. Це прапрадід heartbeat/
# failsafe: «не мій сигнал → нічого не роби».
def fig_individualization():
    W, H = 1000, 440
    P = []
    P.append(text(W / 2, 30, "Телеавтомат 1898: човен слухає лише СВОГО — «як на власне ім'я»",
                  size=16, bold=True))

    # човен-приймач праворуч
    bx, by = W - 195, 215
    fr, w, h = textbox(bx, by, "ЧОВЕН-ТЕЛЕАВТОМАТ\nприймач на СВОЇ періоди\n(когерер + реле)",
                       size=12.5, bold=True, fill="#e9f7ef", stroke=FIELD, min_w=230)
    bx_left = bx - w / 2
    P.append(fr)

    # свій оператор (згори-ліворуч) — резонанс → команда виконується
    ox, oy = 165, 118
    fr, w, h = textbox(ox, oy, "СВІЙ ОПЕРАТОР\nті самі періоди",
                       size=12.5, bold=True, fill="#eef2f7", stroke=NEG, min_w=180)
    P.append(fr)
    P.append(arrow(ox + w / 2 + 4, oy + 22, bx_left - 8, by - 28, color=FIELD, sw=2.4))
    fr, w, h = textbox(W / 2 - 30, 150,
                       "збіг → РЕЛЕ СПРАЦЮВАЛО\nкермо / хід",
                       size=11.5, bold=True, color=FIELD, fill="#e9f7ef", stroke=FIELD)
    P.append(fr)

    # чужий/завада (знизу-ліворуч) — інші періоди → нічого
    jx, jy = 165, 322
    fr, w, h = textbox(jx, jy, "ЧУЖИЙ ПЕРЕДАВАЧ\nгроза, іскра, крик із залу",
                       size=12.5, bold=True, fill="#eef2f7", stroke=POS, min_w=180)
    P.append(fr)
    P.append(arrow(jx + w / 2 + 4, jy - 22, bx_left - 8, by + 28, color=POS, sw=2.2))
    fr, w, h = textbox(W / 2 - 30, 290,
                       "інші періоди → РЕЛЕ МОВЧИТЬ\nжодної дії",
                       size=11.5, bold=True, color=POS, fill="#fdecea", stroke=POS)
    P.append(fr)

    fr, w, h = textbox(W / 2, H - 30,
                       "Прапрадід сучасного failsafe: «не мій сигнал — нічого не роблю».\n"
                       "Телекерування народилося як питання ДОВІРИ до команди, а не швидкості.",
                       size=12, bold=True, fill="#eef2f7", stroke=INK)
    P.append(fr)

    render("img/individualization.svg", W, H, *P)


# ── Фігура 5 (вставка hist): родовід поняття «телеоператор» ──────────────────
# Ідея: одна ідея — «людина керує машиною крізь відстань» — проросла трьома
# гілками під різні небезпеки: радіо (не бачу), скло (не торкнуся), вакуум
# (не дотягнусь). Слово «телеоператор» закріпив звіт NASA SP-5047 (1967).
def fig_teleop_lineage():
    W, H = 1020, 430
    P = []
    P.append(text(W / 2, 30, "Одна ідея, три небезпеки: як народилося слово «телеоператор»",
                  size=16, bold=True))

    ax_y = 118
    ax_x0, ax_x1 = 70, W - 60
    P.append(line(ax_x0, ax_y, ax_x1, ax_y, color=MUTED, sw=1.6))
    P.append(text(ax_x1, ax_y - 12, "час →", size=12, color=MUTED, anchor="end"))

    def milestone(frac, year, col):
        x = ax_x0 + frac * (ax_x1 - ax_x0 - 20)
        P.append(circle(x, ax_y, 5, fill=col, stroke=col))
        P.append(line(x, ax_y - 8, x, ax_y - 26, color=col, sw=1.6))
        P.append(text(x, ax_y - 32, year, size=13, bold=True, color=col))
        return x

    x1 = milestone(0.04, "1898", FIELD)
    x2 = milestone(0.40, "1949–54", NEG)
    x3 = milestone(0.66, "1967", POS)
    x4 = milestone(0.93, "нині", INK)

    def card(cx, title, body, col, fill):
        fr, w, h = textbox(cx, ax_y + 110, "%s\n%s" % (title, body),
                           size=11.5, bold=True, color=col, fill=fill, stroke=col, min_w=170)
        P.append(fr)

    card(x1, "ТЕСЛА: човен по радіо",
         "«не бачу очима»\nвідповідь — телеавтомат", FIELD, "#e9f7ef")
    card(x2, "ҐОРЦ: маніпулятор за склом",
         "«не торкнуся руками»\nруки-копії крізь свинець", NEG, "#eaf0fd")
    card(x3, "NASA SP-5047",
         "звіт Джонсена й Корлісса\nзакріпив термін teleoperator", POS, "#fdecea")
    card(x4, "наземні / повітряні\nапарати",
         "камера + лінк + failsafe\nта сама петля, ширша", INK, "#eef2f7")

    fr, w, h = textbox(W / 2, H - 28,
                       "Спільне в усіх трьох — людина в петлі крізь відстань і те саме питання: "
                       "що робить машина, коли зв'язок обірвано.",
                       size=12, bold=True, fill="#e9f7ef", stroke=FIELD)
    P.append(fr)

    render("img/teleop-lineage.svg", W, H, *P)


if __name__ == "__main__":
    fig_teleop_loop()
    fig_latency_budget()
    fig_failsafe_ladder()
    fig_individualization()
    fig_teleop_lineage()
    print("OK: 5 figures -> img/")
