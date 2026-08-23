# -*- coding: utf-8 -*-
"""Фігури до кроку «Поллінг проти колбека/вебхука для результату»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#dfe9fb"
GREEN_FILL = "#eafaf0"
GRAY_FILL = "#eceef1"
YELLOW_FILL = "#fff8e6"
RED_FILL = "#fdecea"


def fig_pull_vs_push():
    """Дві доріжки над часом: поллінг — багато порожніх опитувань + затримка; вебхук — один push."""
    W, H = 1240, 690
    frags = []
    frags.append(text(W / 2, 34,
                      "Як забрати результат: тягнути (поллінг) проти штовхати (вебхук)",
                      size=17, bold=True, color=INK))

    # ═══════════ ВЕРХ — ПОЛЛІНГ ═══════════
    frags.append(text(W / 2, 74,
                      "ПОЛЛІНГ (pull) — викликач сам раз за разом питає «готово?»",
                      size=14, bold=True, color=INK))
    y_s, y_c = 152, 258
    frags.append(text(84, y_s + 4, "сервер", size=12, bold=True, color=MUTED, anchor="end"))
    frags.append(text(84, y_c + 4, "викликач", size=12, bold=True, color=MUTED, anchor="end"))
    frags.append(line(150, y_s, 1090, y_s, color=MUTED, sw=1, dash="3,5"))
    frags.append(line(150, y_c, 1090, y_c, color=MUTED, sw=1, dash="3,5"))

    ticks = [210, 355, 500, 645, 790, 935]
    answers = ["ні", "ні", "ні", "ні", "ні", "ТАК ✓"]
    x_ready = 862  # результат готовий між 790 і 935
    for x, a in zip(ticks, answers):
        done = a.startswith("ТАК")
        col = FIELD if done else POS
        frags.append(arrow(x, y_c - 15, x, y_s + 15, color=INK, sw=1.5))
        frags.append(circle(x, y_c, 4, fill=BG, stroke=INK, sw=1.4))
        frags.append(text(x, y_s - 16, a, size=12, bold=done, color=col))
    frags.append(text(ticks[0], y_c + 26, "GET", size=10, color=MUTED))
    frags.append(text((ticks[0] + ticks[-1]) / 2, y_c + 44,
                      "викликач опитує кожні T = 5 с — переважно чує «ще ні»",
                      size=12, color=MUTED))

    # момент готовності + змарнована затримка до наступного тику
    frags.append(line(x_ready, y_s - 34, x_ready, y_c + 10, color=FIELD, sw=1.4, dash="4,4"))
    frags.append(text(x_ready, y_s - 42, "результат готовий тут", size=11, bold=True, color=FIELD))
    frags.append(line(x_ready, y_c - 30, 935, y_c - 30, color=POS, sw=1.4))
    frags.append(text((x_ready + 935) / 2, y_c - 38, "змарнована затримка", size=10, bold=True, color=POS))

    frags.append(text(W / 2, 322,
                      "Більшість опитувань вертає «ще ні»; результат, готовий одразу по тику, чекає до наступного — зайва затримка ≈ T/2.",
                      size=13, color=MUTED))

    # ═══════════ НИЗ — ВЕБХУК ═══════════
    frags.append(line(60, 360, W - 60, 360, color=MUTED, sw=1, dash="6,6"))
    frags.append(text(W / 2, 398,
                      "ВЕБХУК (push) — викликач лишив адресу й пішов; сервер штовхає результат раз",
                      size=14, bold=True, color=INK))
    y_s2, y_c2 = 476, 582
    frags.append(text(84, y_s2 + 4, "сервер", size=12, bold=True, color=MUTED, anchor="end"))
    frags.append(text(84, y_c2 + 4, "викликач", size=12, bold=True, color=MUTED, anchor="end"))
    frags.append(line(150, y_s2, 222, y_s2, color=MUTED, sw=1, dash="3,5"))
    frags.append(line(870, y_s2, 1090, y_s2, color=MUTED, sw=1, dash="3,5"))
    # робота у фоні на сервері
    frags.append(fitbox(230, y_s2 - 17, 632, 34, "робота у фоні — оновлюємо прошивку",
                        size=12, fill=YELLOW_FILL, stroke=MUTED))
    # викликач присутній лише на старті, далі відсутній
    frags.append(line(150, y_c2, 210, y_c2, color=MUTED, sw=1, dash="3,5"))
    frags.append(arrow(210, y_c2 - 15, 210, y_s2 + 15, color=INK, sw=1.6))
    frags.append(text(210, y_c2 + 26, "запуск: 202 {jobId}", size=11, color=INK))
    frags.append(text(540, y_c2 + 8, "викликач відсутній — не опитує, ресурси вільні",
                      size=12, italic=True, color=MUTED))

    # той самий момент готовності
    frags.append(line(x_ready, y_s2 - 34, x_ready, y_c2 + 12, color=FIELD, sw=1.4, dash="4,4"))
    frags.append(arrow(x_ready, y_s2 + 15, x_ready, y_c2 - 15, color=FIELD, sw=2.2))
    frags.append(text(x_ready, y_s2 - 42, "POST «готово ✓»", size=12, bold=True, color=FIELD))
    frags.append(text(x_ready + 10, (y_s2 + y_c2) / 2, "штовхає раз", size=11,
                      bold=True, color=FIELD, anchor="start"))

    # ціна вебхука — праворуч
    cost, _, _ = textbox(1050, y_c2, "ціна: публічна адреса\n+ підпис + живий приймач",
                         size=11, bold=True, fill=RED_FILL, stroke=POS, sw=1.5, min_w=220)
    frags.append(cost)

    frags.append(text(W / 2, 662,
                      "Єдиний виклик у мить готовності: нуль порожніх запитів і майже без затримки — якщо є куди доставити.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "pull-vs-push.svg"), W, H, *frags,
           title="Тягнути (поллінг) проти штовхати (вебхук)")


def _wall(frags, x, y0, y1, w=22, gap=None):
    """Вертикальна стіна NAT/файрвол зі штрихуванням.
    gap=(gy0,gy1) — пропустити штрихування в цій смузі (там сидить інша позначка, напр. ×)."""
    frags.append(rect(x - w / 2, y0, w, y1 - y0, fill=GRAY_FILL, stroke=MUTED, sw=1.4, rx=3))
    yy = y0 + 10
    while yy < y1 - 4:
        if gap and gap[0] - 8 <= yy <= gap[1] + 8:
            yy += 12
            continue
        frags.append(line(x - w / 2 + 2, yy, x + w / 2 - 2, yy - 8, color=MUTED, sw=1))
        yy += 12


def fig_reachability():
    """Хто ініціює з'єднання: вихідний поллінг проходить крізь NAT, вхідний вебхук — ні."""
    W, H = 1220, 600
    frags = []
    frags.append(text(W / 2, 36, "Справжня вісь — хто до кого може дотягтися",
                      size=17, bold=True, color=INK))

    wall_x = 600
    _wall(frags, wall_x, 118, 470, gap=(361, 383))
    frags.append(text(wall_x, 104, "NAT / файрвол", size=13, bold=True, color=MUTED))

    caller, _, _ = textbox(228, 250, "ВИКЛИКАЧ\nтелефон · браузер · сервіс за файрволом",
                           size=13, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.9, min_w=310)
    frags.append(caller)
    server, _, _ = textbox(982, 250, "СЕРВЕР DH", size=14, bold=True,
                           fill=GREEN_FILL, stroke=FIELD, sw=1.9, min_w=220)
    frags.append(server)

    # поллінг — вихідне, проходить (зелене)
    frags.append(arrow(392, 208, 872, 208, color=FIELD, sw=2.4))
    frags.append(text(wall_x, 192, "поллінг: вихідне з'єднання проходить завжди",
                      size=12, bold=True, color=FIELD))
    frags.append(text(982, 300, "лишається простим —", size=11, color=MUTED))
    frags.append(text(982, 316, "тільки відповідає на статус", size=11, color=MUTED))

    # вебхук — вхідне, блокує стіна (червоне)
    frags.append(arrow(872, 372, wall_x + 16, 372, color=POS, sw=2.4))
    frags.append(circle(wall_x, 372, 11, fill=RED_FILL, stroke=POS, sw=2.4))
    frags.append(text(wall_x, 377, "✕", size=15, bold=True, color=POS))
    frags.append(text(772, 356, "вебхук: вхідне для викликача", size=12, bold=True, color=POS))
    frags.append(text(700, 398, "NAT/файрвол блокує", size=11, color=POS))
    frags.append(mtext(228, 336,
                       ["щоб прийняти POST, викликач мусить сам", "стати сервером: публічна адреса,",
                        "автентифікація, живий приймач"],
                       size=11, color=MUTED))

    frags.append(text(W / 2, 528,
                      "Вихідні дзвінки проходять звідусіль → поллінг доступний завжди. Вебхук жадає, щоб викликач сам був досяжним ззовні.",
                      size=13, bold=True, color=INK))
    frags.append(text(W / 2, 556,
                      "Та сама розвилка, що в залізі: процесор опитує пристрій сам — чи пристрій піднімає лінію переривання.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "reachability.svg"), W, H, *frags, title=None)


def fig_decision_hybrid():
    """Дві питальні осі → поллінг/вебхук; зрілий дефолт — обидва."""
    W, H = 1240, 600
    frags = []
    frags.append(text(W / 2, 34,
                      "Як обирати: спершу «хто викликач», тоді «хто чекає» — і зазвичай обидва",
                      size=16, bold=True, color=INK))

    frags.append(line(632, 132, 632, 346, color=MUTED, sw=1, dash="5,6"))

    def axis(cx, header, rows):
        h, _, _ = textbox(cx, 96, header, size=14, bold=True,
                          fill=YELLOW_FILL, stroke=INK, sw=1.8, min_w=540)
        frags.append(h)
        for (yc, left, out, fill, stroke) in rows:
            frags.append(fitbox(cx - 275, yc - 27, 210, 54, left, size=12,
                                fill=GRAY_FILL, stroke=MUTED))
            frags.append(arrow(cx - 62, yc, cx - 8, yc, color=INK, sw=1.8))
            frags.append(fitbox(cx + 2, yc - 27, 268, 54, out, size=13, bold=True,
                                fill=fill, stroke=stroke))

    axis(348, "Питання 1 — ХТО ВИКЛИКАЧ?", [
        (188, "за NAT, без\nпублічної адреси", "ПОЛЛІНГ", GREEN_FILL, FIELD),
        (286, "публічний\nзагартований сервер", "ВЕБХУК", BLUE_FILL, NEG),
    ])
    axis(948, "Питання 2 — ХТО ЧЕКАЄ?", [
        (188, "людина в екрані\nзараз", "тримати лінію /\nчасто опитувати", GREEN_FILL, FIELD),
        (286, "бекенд,\nможе спати", "ВЕБХУК", BLUE_FILL, NEG),
    ])

    hyb, _, _ = textbox(W / 2, 428,
                        "Зрілий дефолт — ОБИДВА: вебхук для швидкого шляху + поллінг/звірка як страхувальна сітка,\n"
                        "бо вебхуки таки губляться (приймач полежав, проксі відкинув, фільтр спрацював).",
                        size=13, bold=True, fill=RED_FILL, stroke=POS, sw=1.8, min_w=1140)
    frags.append(hyb)
    frags.append(text(W / 2, 520,
                      "Досяжність відсіює більшість випадків; на серйозних інтеграціях push і pull живуть разом — швидкість плюс гарантія.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "decision-hybrid.svg"), W, H, *frags, title=None)


def fig_lineage_timeline():
    """Родовід «тягнути ⇄ штовхати»: сім віх за сім десятиліть — push угорі, pull унизу."""
    W, H = 1420, 600
    frags = []
    frags.append(text(W / 2, 36,
                      "Родовід «тягнути ⇄ штовхати»: та сама розвилка через сім десятиліть",
                      size=17, bold=True, color=INK))

    ax_y = 300
    frags.append(line(70, ax_y, 1350, ax_y, color=MUTED, sw=1.5))
    frags.append(text(80, 96, "↑ ШТОВХАТИ (push) — пристрій / сервер сам ініціює зв'язок",
                      size=13, bold=True, color=POS, anchor="start"))
    frags.append(text(80, 528, "↓ ТЯГНУТИ (pull) — викликач опитує сам, коли захоче",
                      size=13, bold=True, color=NEG, anchor="start"))

    ticks = [110, 310, 510, 710, 910, 1110, 1310]
    miles = [
        ("down", BLUE_FILL, NEG,   ["поч. 1950-х", "залізо в циклі", "опитує пристрій"]),
        ("up",   RED_FILL,  POS,   ["1954–56", "переривання:", "DYSEAC · 1103A"]),
        ("down", BLUE_FILL, NEG,   ["1999 → 2005", "XHR, тоді AJAX —", "браузер опитує"]),
        ("mid",  YELLOW_FILL, MUTED, ["2006 · Comet", "висячий GET —", "тримати лінію"]),
        ("up",   RED_FILL,  POS,   ["2007", "«webhook»", "дістає ім'я"]),
        ("up",   RED_FILL,  POS,   ["2010–12", "GitHub, Stripe —", "вебхуки масові"]),
        ("down", BLUE_FILL, NEG,   ["2020-ті", "звірка вертає", "поллінг як сітку"]),
    ]
    bw, bh = 190, 92
    up_cy, down_cy = 160, 448
    for x, (side, fill, stroke, lines) in zip(ticks, miles):
        if side == "up":
            cy = up_cy
            frags.append(line(x, ax_y, x, cy + bh / 2, color=MUTED, sw=1.2))
        elif side == "down":
            cy = down_cy
            frags.append(line(x, ax_y, x, cy - bh / 2, color=MUTED, sw=1.2))
        else:
            cy = ax_y
        frags.append(circle(x, ax_y, 5, fill=BG, stroke=INK, sw=1.6))
        frags.append(fitbox(x - bw / 2, cy - bh / 2, bw, bh, "\n".join(lines),
                            size=13, bold=True, fill=fill, stroke=stroke, sw=1.8))

    # маятник назад: пік штовхання (2010–12) → повернення тягнути (2020-ті)
    frags.append(line(1110, up_cy + bh / 2, 1310, down_cy - bh / 2,
                      color=POS, sw=2.2, dash="6,5"))
    frags.append(mtext(1170, 296, ["маятник", "хитнувся", "назад"],
                       size=12, color=POS, bold=True))

    frags.append(text(W / 2, 566,
                      "Розвилку перерішують щоепохи — і зріла відповідь врешті тримає обидва боки: "
                      "push заради швидкості, pull заради певності.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "lineage-timeline.svg"), W, H, *frags, title=None)


# ─────────────────────────────────────────────────────────────────────────────
#  Фігури проєкту proj-dh-result-delivery
# ─────────────────────────────────────────────────────────────────────────────
def fig_delivery_map():
    """Складена система на два боки: телефон тягне статус; DH підписує й штовхає
    вебхук із повтором у DLQ; партнер звіряє підпис, дедупить в inbox, застосовує
    раз; звірка-сітка добирає проґавлений вебхук крізь той самий inbox."""
    W, H = 1340, 760
    frags = []
    frags.append(text(W / 2, 34, "Доставка результату DH на два боки — складена система",
                      size=17, bold=True, color=INK))

    # три панелі-актори
    frags.append(rect(48, 128, 236, 566, fill=BG, stroke=NEG, sw=1.8, rx=10))
    frags.append(rect(556, 128, 268, 566, fill="#f6faf7", stroke=FIELD, sw=1.8, rx=10))
    frags.append(rect(1058, 128, 234, 566, fill=BG, stroke=NEG, sw=1.8, rx=10))
    frags.append(text(166, 158, "МОБІЛЬНИЙ ЗАСТОСУНОК", size=12, bold=True, color=NEG))
    frags.append(text(166, 178, "за NAT · без адреси", size=11, color=MUTED))
    frags.append(text(690, 158, "СЕРВЕР DH", size=14, bold=True, color=FIELD))
    frags.append(text(1175, 158, "ПАРТНЕР", size=12, bold=True, color=NEG))
    frags.append(text(1175, 178, "хмара монтажника", size=11, color=MUTED))

    # DH-нутрощі
    frags.append(fitbox(578, 220, 224, 52, "(а) GET /jobs/{id}\nстатус — дешеве читання",
                        size=12, bold=True, fill=GREEN_FILL, stroke=FIELD))
    frags.append(fitbox(578, 352, 224, 56, "(в) done → підписати\n+ POST + повтор → DLQ",
                        size=12, bold=True, fill=YELLOW_FILL, stroke=MUTED))
    frags.append(fitbox(604, 596, 172, 44, "стан задач\n(job store)", size=11,
                        fill=GRAY_FILL, stroke=MUTED))

    # партнер-нутрощі
    frags.append(fitbox(1076, 220, 200, 46, "(г) звірити підпис\n(HMAC, сталий час)",
                        size=11, bold=True, fill=BLUE_FILL, stroke=NEG))
    frags.append(fitbox(1076, 300, 200, 40, "inbox: дедуп за event-id", size=11,
                        fill=GRAY_FILL, stroke=MUTED))
    frags.append(fitbox(1076, 372, 200, 46, "застосувати РАЗ\n(в 1 транзакції)", size=11,
                        bold=True, fill=GREEN_FILL, stroke=FIELD))
    frags.append(fitbox(1076, 486, 200, 46, "(ґ) звірка-сітка\nдобирає проґавлене", size=11,
                        bold=True, fill=YELLOW_FILL, stroke=MUTED))

    # ── БАНД A: поллінг (телефон ↔ DH) ──
    _wall(frags, 316, 214, 296)
    frags.append(text(316, 204, "NAT", size=10, bold=True, color=MUTED))
    frags.append(arrow(288, 244, 574, 244, color=FIELD, sw=2.0))
    frags.append(text(430, 234, "GET /jobs (поллінг)", size=11, bold=True, color=FIELD))
    frags.append(arrow(574, 272, 288, 272, color=INK, sw=1.6))
    frags.append(text(430, 288, "status: done / failed", size=11, color=MUTED))
    frags.append(fitbox(70, 316, 192, 44, "(б) бюджет часу\n+ відступ + джитер", size=11,
                        bold=True, fill=BLUE_FILL, stroke=NEG))

    # ── БАНД B: підписаний вебхук (DH → партнер), його втрата, і DLQ ──
    frags.append(arrow(826, 243, 1072, 243, color=INK, sw=2.2))
    frags.append(text(940, 232, "(в) POST  t.body + dh-signature", size=11, bold=True, color=INK))
    # проґавлений вебхук — червоний пунктир, перекреслений (нижче основної стрілки)
    frags.append(line(826, 300, 980, 300, color=POS, sw=1.4, dash="6,5"))
    frags.append(text(890, 292, "інколи губиться", size=10, color=POS))
    frags.append(circle(946, 300, 9, fill=RED_FILL, stroke=POS, sw=1.8))
    frags.append(text(946, 305, "✕", size=12, bold=True, color=POS))
    # гілка в мертву чергу (з-під відправника DH вниз)
    frags.append(arrow(690, 412, 690, 626, color=POS, sw=1.8))
    frags.append(fitbox(590, 630, 200, 48, "МЕРТВА ЧЕРГА\nвичерпав повтори → на розбір",
                        size=11, bold=True, fill=RED_FILL, stroke=POS, sw=1.6))

    # ── БАНД C: звірка (партнер → DH), pull ──
    frags.append(arrow(1054, 500, 826, 520, color=FIELD, sw=2.0))
    frags.append(text(940, 494, "(ґ) GET done since… (звірка)", size=11, bold=True, color=FIELD))
    frags.append(text(940, 540, "тягне те, що вебхук проґавив", size=10, color=MUTED))

    frags.append(text(W / 2, 726,
                      "Один результат — один event-id: і вебхук, і звірка несуть той самий ключ, "
                      "тож inbox дедупить їх разом і застосування стається рівно раз.",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, "delivery-map.svg"), W, H, *frags, title=None)


def fig_receiver_flow():
    """Порядок у приймачі: довіра (підпис) → свіжість (час) → дедуп (inbox) →
    застосування раз. Кожна перевірка або пропускає далі, або відсіює вбік."""
    W, H = 900, 812
    frags = []
    frags.append(text(W / 2, 34, "Ідемпотентний приймач: незмінний порядок перевірок",
                      size=16, bold=True, color=INK))

    cx = 372          # головна колонка
    rx = 686          # колонка відсіву
    frags.append(fitbox(cx - 150, 62, 300, 44, "POST /dh/webhook надійшов\n(сирі байти + заголовок)",
                        size=12, bold=True, fill=GRAY_FILL, stroke=MUTED))

    def stepbox(y, s, fill=BG, stroke=INK):
        frags.append(fitbox(cx - 150, y, 300, 56, s, size=12, bold=True, fill=fill, stroke=stroke))

    def reject(y, s):
        frags.append(arrow(cx + 152, y + 28, rx - 118, y + 28, color=POS, sw=1.8))
        frags.append(fitbox(rx - 116, y + 2, 236, 52, s, size=11, bold=True,
                            fill=RED_FILL, stroke=POS, sw=1.6))

    def down(y0, y1, lbl="так"):
        frags.append(arrow(cx, y0, cx, y1, color=FIELD, sw=1.8))
        frags.append(text(cx + 16, (y0 + y1) / 2 + 4, lbl, size=11, bold=True, color=FIELD,
                          anchor="start"))

    down(106, 138)
    stepbox(138, "1 · Підпис збігся?\nHMAC(t·тіло) у СТАЛИЙ час")
    reject(138, "401 — геть\nце не від DH")
    down(194, 250, "так")

    stepbox(250, "2 · Час свіжий?\n|тепер − t| ≤ 5 хв")
    reject(250, "400 — застарілий\nзахист від переграння")
    down(306, 362, "так")

    stepbox(362, "3 · event-id уже в inbox?")
    frags.append(arrow(cx + 152, 390, rx - 118, 390, color=MUTED, sw=1.8))
    frags.append(fitbox(rx - 116, 364, 236, 54, "ACK 200 — нічого\nне робимо (повтор\nпроковтнули тихо)",
                        size=11, bold=True, fill=GRAY_FILL, stroke=MUTED))
    frags.append(text(rx + 2, 356, "так", size=11, bold=True, color=MUTED))
    down(418, 476, "ні — свіжа")

    frags.append(fitbox(cx - 170, 476, 340, 60,
                        "INSERT event-id + застосувати ефект\nВ ОДНІЙ транзакції — або разом, або ніяк",
                        size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.7))
    frags.append(arrow(cx, 536, cx, 588, color=FIELD, sw=1.8))
    frags.append(fitbox(cx - 130, 588, 260, 42, "ACK 200 — після коміту", size=12, bold=True,
                        fill=BG, stroke=FIELD))

    frags.append(fitbox(20, 150, 172, 150,
                        "порядок\nнезмінний:\n\nдовіра →\nсвіжість →\nдедуп →\nраз",
                        size=12, bold=True, fill="#fbfbfc", stroke=MUTED))
    frags.append(text(W / 2, 690,
                      "Спершу — чи вірити взагалі; тоді — чи не бачили це вже; і лише тоді — застосувати.",
                      size=12, color=MUTED))
    frags.append(text(W / 2, 714,
                      "Дедуп і ефект живуть в одній транзакції, тож повтор ніколи не подвоїть дію.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "receiver-flow.svg"), W, H, *frags, title=None)


def fig_sender_retry_dlq():
    """Відправник: підпис → серія POST з експоненційним джитер-відступом; 2xx завершує,
    вичерпані спроби падають у мертву чергу — не в нікуди."""
    W, H = 1220, 470
    frags = []
    frags.append(text(W / 2, 34, "Відправник вебхука: підписати, повторювати з відступом, "
                                 "врешті — у мертву чергу", size=15, bold=True, color=INK))

    frags.append(fitbox(40, 150, 168, 56, "задача done →\nподія {id стабільний}",
                        size=12, bold=True, fill=GREEN_FILL, stroke=FIELD))
    frags.append(arrow(210, 178, 262, 178, color=INK, sw=1.8))
    frags.append(fitbox(264, 152, 150, 52, "підпис\nHMAC(t·тіло)", size=12, bold=True,
                        fill=YELLOW_FILL, stroke=MUTED))
    frags.append(arrow(416, 178, 462, 178, color=INK, sw=1.8))

    # вісь часу спроб
    axis_y = 300
    frags.append(line(468, axis_y, 812, axis_y, color=MUTED, sw=1.4))
    frags.append(text(468, axis_y + 26, "час →", size=11, color=MUTED, anchor="start"))

    ticks = [486, 548, 636, 740]      # проміжки ростуть (експонента)
    wlab = ["w₀", "w₁", "w₂"]
    for i, x in enumerate(ticks):
        frags.append(arrow(x, axis_y, x, 210, color=POS, sw=1.8))
        frags.append(text(x, 202, "POST", size=11, bold=True, color=INK))
        frags.append(text(x, 190, "✗", size=12, bold=True, color=POS))
        frags.append(circle(x, axis_y, 4, fill=BG, stroke=INK, sw=1.4))
        frags.append(text(x, axis_y + 20, "спроба %d" % i, size=10, color=MUTED))
        if i < len(ticks) - 1:
            nx = ticks[i + 1]
            frags.append(line(x + 8, axis_y - 40, nx - 8, axis_y - 40, color=NEG, sw=1.3))
            frags.append(text((x + nx) / 2, axis_y - 46, wlab[i], size=11, bold=True, color=NEG))

    # розвилка результату після серії спроб
    fork = 812
    frags.append(arrow(fork, axis_y, fork, 152, color=FIELD, sw=1.8))
    frags.append(fitbox(fork - 90, 110, 176, 40, "будь-яка 2xx → готово",
                        size=11, bold=True, fill=GREEN_FILL, stroke=FIELD))
    frags.append(arrow(fork, axis_y, 900, axis_y, color=POS, sw=2.0))
    frags.append(fitbox(902, axis_y - 32, 292, 64,
                        "МЕРТВА ЧЕРГА\nвичерпав N спроб — на розбір,\nне загублено",
                        size=11, bold=True, fill=RED_FILL, stroke=POS, sw=1.6))

    frags.append(text(W / 2, 372,
                      "Вікно wᵢ = min(cap, base·2ᶦ) росте вдвічі; пауза = random(0, wᵢ) — повний джитер.",
                      size=11, color=MUTED))
    frags.append(text(W / 2, 400,
                      "4xx (крім 429) обриває повтори одразу — повторення його не полагодить; "
                      "id той самий на КОЖЕН POST, тож дубль приймач дедупне.",
                      size=12, color=INK))
    frags.append(text(W / 2, 428,
                      "Повний джитер (AWS, Marc Brooker): пауза рівномірна в усьому вікні — відправники не б'ють синхронно.",
                      size=11, color=MUTED))

    render(os.path.join(IMG, "sender-retry-dlq.svg"), W, H, *frags, title=None)


# ─────────────────────────────────────────────────────────────────────────────
#  Фігури вставки math-polling-economics
# ─────────────────────────────────────────────────────────────────────────────
def _poly(pts, color=INK, sw=2.4, fill="none", dash=None):
    d = " ".join(("M" if i == 0 else "L") + " %.1f %.1f" % (x, y) for i, (x, y) in enumerate(pts))
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, color, sw, da)


def fig_math_latency_load():
    """Закон збереження поллінга: затримка × навантаження = N/2 — гіпербола."""
    W, H = 1180, 650
    N = 10000.0
    frags = []
    frags.append(text(W / 2, 34, "Закон збереження поллінга: затримка × навантаження = N/2",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 74, "затримка × навантаження = N/2 = 5000 — стала, хоч би яке T",
                      size=13, bold=True, color=NEG))
    x0, x1 = 180, 1055
    y0, y1 = 548, 118
    LOADMAX, LATMAX = 11000.0, 5.6

    def X(load): return x0 + load / LOADMAX * (x1 - x0)
    def Y(lat): return y0 - lat / LATMAX * (y0 - y1)

    frags.append(line(x0, y0, x1, y0, color=INK, sw=1.6))
    frags.append(line(x0, y0, x0, y1, color=INK, sw=1.6))
    for lv in [2000, 4000, 6000, 8000, 10000]:
        frags.append(line(X(lv), y0, X(lv), y0 + 6, color=INK, sw=1.2))
        frags.append(text(X(lv), y0 + 22, str(lv), size=11, color=MUTED))
    for lv in [1, 2, 3, 4, 5]:
        frags.append(line(x0 - 6, Y(lv), x0, Y(lv), color=INK, sw=1.2))
        frags.append(text(x0 - 14, Y(lv) + 4, str(lv), size=11, color=MUTED, anchor="end"))
    frags.append(text((x0 + x1) / 2, y0 + 44, "сукупне навантаження (запитів/с) = N / T",
                      size=12, bold=True, color=INK))
    frags.append(text(x0 + 6, y1 - 12, "зайва затримка (с) = T / 2", size=12, bold=True,
                      color=INK, anchor="start"))

    pts = []
    T = 0.92
    while T <= 11.3:
        load, lat = N / T, T / 2
        if load <= LOADMAX and lat <= LATMAX:
            pts.append((X(load), Y(lat)))
        T += 0.04
    frags.append(_poly(pts, color=NEG, sw=2.8))

    frags.append(arrow(X(2000) + 10, Y(2.5) - 2, X(10000) - 8, Y(0.5) + 4, color=MUTED, sw=1.5))
    frags.append(text(X(6600), Y(3.6),
                      "↓T: ковзаєш уздовж кривої — одне легшає рівно настільки, наскільки важчає інше",
                      size=11, italic=True, color=MUTED))

    for (load, lat, lab, below) in [(2000, 2.5, "T = 5 с", True), (10000, 0.5, "T = 1 с", False)]:
        frags.append(circle(X(load), Y(lat), 6, fill=BG, stroke=POS, sw=2.4))
        frags.append(text(X(load), Y(lat) - 16, lab, size=12, bold=True, color=POS))
        frags.append(text(X(load), Y(lat) + (26 if below else -30),
                          "(%d/с, %.1f с)" % (load, lat), size=10, color=MUTED))

    frags.append(text(X(1500), Y(0.7), "✕", size=17, bold=True, color=POS))
    frags.append(mtext(X(1500) + 130, Y(0.7) - 4,
                       ["бажане: і дешево, і швидко —", "крива в цей кут не заходить"],
                       size=11, color=POS))
    render(os.path.join(IMG, "math-latency-load.svg"), W, H, *frags, title=None)


def fig_math_herd_jitter():
    """Стадо і джитер: те саме середнє N/T, різний пік."""
    import random
    random.seed(7)
    W, H = 1200, 645
    frags = []
    frags.append(text(W / 2, 34, "Стадо і джитер: те саме середнє N/T, різний пік",
                      size=17, bold=True, color=INK))
    xL, xR = 185, 1055
    mean_h = 26

    ay = 268
    frags.append(text(xL - 5, 88, "У ФАЗІ — усі викликачі опитують синхронно",
                      size=14, bold=True, color=POS, anchor="start"))
    frags.append(line(xL, ay, xR, ay, color=INK, sw=1.6))
    frags.append(line(xL, ay - mean_h, xR, ay - mean_h, color=FIELD, sw=1.4, dash="5,5"))
    frags.append(text(xR + 8, ay - mean_h + 4, "середнє N/T", size=10, color=FIELD, anchor="start"))
    spikes = [xL + 90, xL + 270, xL + 450, xL + 630, xL + 810]
    for sx in spikes:
        frags.append(rect(sx - 13, ay - 150, 26, 150, fill=RED_FILL, stroke=POS, sw=1.8, rx=2))
    frags.append(text(spikes[0], ay - 160, "пік = N", size=12, bold=True, color=POS))
    frags.append(text((spikes[1] + spikes[2]) / 2, ay - 78, "усі разом", size=11, color=POS))
    frags.append(text((spikes[2] + spikes[3]) / 2, ay + 22,
                      "між тиками — простій: 0 запитів", size=11, color=MUTED))
    frags.append(text(xL - 5, ay + 42, "кожні T секунд", size=10, italic=True,
                      color=MUTED, anchor="start"))

    by = 558
    frags.append(text(xL - 5, 372, "З ДЖИТЕРОМ — кожен зсунув фазу випадково",
                      size=14, bold=True, color=NEG, anchor="start"))
    frags.append(line(xL, by, xR, by, color=INK, sw=1.6))
    frags.append(line(xL, by - mean_h, xR, by - mean_h, color=FIELD, sw=1.4, dash="5,5"))
    frags.append(text(xR + 8, by - mean_h + 4, "середнє N/T", size=10, color=FIELD, anchor="start"))
    nb = 46
    for i in range(nb):
        bx = xL + 12 + i * (xR - xL - 24) / (nb - 1)
        h = mean_h + random.uniform(-7, 8)
        frags.append(rect(bx - 4, by - h, 8, h, fill=BLUE_FILL, stroke=NEG, sw=1.0, rx=1))
    frags.append(text((xL + xR) / 2, by - 66, "рівний потік ≈ N/T,  брижі лише ~√N",
                      size=12, bold=True, color=NEG))
    frags.append(text(W / 2, 616,
                      "Джитер не міняє середнього — він розмазує фази рівномірно на [0,T): пік осідає з N майже до середнього.",
                      size=12, color=INK))
    render(os.path.join(IMG, "math-herd-jitter.svg"), W, H, *frags, title=None)


def fig_math_breakeven():
    """Беззбитковість: поллінг (пласко f·q) проти push (i + E·d), крапка E*."""
    W, H = 1180, 640
    frags = []
    frags.append(text(W / 2, 34, "Беззбитковість: коли pull дорожчає за push",
                      size=17, bold=True, color=INK))
    x0, x1 = 180, 1035
    y0, y1 = 545, 120
    EMAX, CMAX = 0.5, 0.6
    q, f, d, i = 1.0, 0.2, 1.0, 0.02

    def X(E): return x0 + E / EMAX * (x1 - x0)
    def Y(c): return y0 - c / CMAX * (y0 - y1)

    Estar = (f * q - i) / d
    frags.append(rect(X(0), y1, X(Estar) - X(0), y0 - y1, fill="#eef7f0", stroke=BG, sw=0, rx=0))
    frags.append(rect(X(Estar), y1, X(EMAX) - X(Estar), y0 - y1, fill="#eef2fc", stroke=BG, sw=0, rx=0))
    frags.append(line(x0, y0, x1, y0, color=INK, sw=1.6))
    frags.append(line(x0, y0, x0, y1, color=INK, sw=1.6))
    frags.append(text((x0 + x1) / 2, y0 + 40, "частота змін E (подій/с на спостерігача)",
                      size=12, bold=True, color=INK))
    frags.append(text(x0 + 6, y1 - 12, "вартість / с  (одиниці)", size=12, bold=True,
                      color=INK, anchor="start"))

    frags.append(_poly([(X(0), Y(f * q)), (X(EMAX), Y(f * q))], color=NEG, sw=2.8))
    frags.append(text(X(0.40), Y(f * q) - 12, "ПОЛЛІНГ: f·q — не залежить від E",
                      size=12, bold=True, color=NEG))
    frags.append(_poly([(X(0), Y(i)), (X(EMAX), Y(i + EMAX * d))], color=POS, sw=2.8))
    frags.append(text(X(0.30), Y(i + 0.30 * d) + 20, "PUSH: i + E·d", size=12, bold=True, color=POS))

    frags.append(line(X(Estar), y0, X(Estar), Y(f * q), color=MUTED, sw=1.3, dash="5,5"))
    frags.append(circle(X(Estar), Y(f * q), 6, fill=BG, stroke=INK, sw=2.2))
    frags.append(text(X(Estar), Y(f * q) - 16, "E* ≈ f·(q/d)", size=12, bold=True, color=INK))

    frags.append(mtext(X(0.075), Y(0.44), ["push дешевший", "→ ВЕБХУК"],
                       size=12, bold=True, color=FIELD))
    frags.append(mtext(X(0.365), Y(0.52), ["поллінг дешевший", "(коалесує) → ПОЛЛІНГ"],
                       size=12, bold=True, color=NEG))
    frags.append(circle(X(0.012), Y(i + 0.012 * d), 5, fill=POS, stroke=POS, sw=1.5))
    frags.append(mtext(X(0.03), Y(0.30), ["DH прошивка: ~1 подія", "на ~18 опитувань —",
                                          "глибоко в зоні push"], size=10, color=POS, anchor="start"))
    render(os.path.join(IMG, "math-breakeven.svg"), W, H, *frags, title=None)


if __name__ == "__main__":
    fig_pull_vs_push()
    fig_reachability()
    fig_decision_hybrid()
    fig_lineage_timeline()
    fig_delivery_map()
    fig_receiver_flow()
    fig_sender_retry_dlq()
    fig_math_latency_load()
    fig_math_herd_jitter()
    fig_math_breakeven()
    print("OK: pull-vs-push, reachability, decision-hybrid, lineage-timeline, "
          "delivery-map, receiver-flow, sender-retry-dlq, "
          "math-latency-load, math-herd-jitter, math-breakeven")
