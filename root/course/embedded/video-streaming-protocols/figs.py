# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Протоколи відеострімінгу».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: голий UDP проти RTP ───────────────────────────────────────────
# Ідея: UDP кладе шматок відео у конверт без підпису — приймач не знає ні
# порядку, ні часу. RTP додає рівно дві речі: НОМЕР (відновити порядок,
# побачити втрату) і МІТКУ ЧАСУ (коли показати). Це й перетворює купу
# датаграм на ПОТІК.
def fig_raw_vs_rtp():
    W, H = 940, 430
    P = []
    P.append(text(W / 2, 30, "Голий UDP проти RTP: дві речі, що роблять потік",
                  size=17, bold=True))

    # ── зверху: голий UDP-датаграм ──
    P.append(text(W / 2, 70, "UDP сам по собі: лише шматок байтів",
                  size=13.5, bold=True, color=POS))
    ux, uy, uw, uh = 120, 88, W - 240, 52
    P.append(rect(ux, uy, 150, uh, fill="#eef2f7", stroke=MUTED))
    P.append(text(ux + 75, uy + uh / 2 + 5, "UDP-заголовок", size=11.5, color=MUTED))
    P.append(rect(ux + 150, uy, uw - 150, uh, fill="#fdecea", stroke=POS))
    P.append(text(ux + 150 + (uw - 150) / 2, uy + uh / 2 + 5,
                  "шматок стисненого відео (байти)", size=12, color=POS, bold=True))
    P.append(text(W / 2, uy + uh + 26,
                  "приймач питає: котрий це шматок? раніше чи пізніше? коли показати? — невідомо",
                  size=11.5, color=MUTED, italic=True))

    # стрілка «додаємо підпис»
    P.append(arrow(W / 2, uy + uh + 44, W / 2, uy + uh + 78, color=FIELD))
    P.append(text(W / 2 + 12, uy + uh + 66, "RTP додає підпис над байтами",
                  size=11.5, color=FIELD, anchor="start", bold=True))

    # ── знизу: RTP-пакет ──
    ry = uy + uh + 96
    P.append(text(W / 2, ry, "RTP поверх UDP: номер + мітка часу + тип",
                  size=13.5, bold=True, color=FIELD))
    rx, rw, rh = 120, W - 240, 56
    ry2 = ry + 16
    # сегменти заголовка RTP
    segs = [
        ("UDP", 90, "#eef2f7", MUTED),
        ("SEQ\n№ пакета", 120, "#e9f7ef", FIELD),
        ("TIMESTAMP\nколи показати", 150, "#e9f7ef", FIELD),
        ("PT\nкодек", 80, "#eef2f7", INK),
    ]
    x = rx
    for lab, w, fill, col in segs:
        P.append(rect(x, ry2, w, rh, fill=fill, stroke=col))
        P.append(mtext(x + w / 2, ry2 + rh / 2 - 2, lab, size=10.5, color=col, bold=True))
        x += w
    # корисні дані
    P.append(rect(x, ry2, rx + rw - x, rh, fill="#fdecea", stroke=POS))
    P.append(text(x + (rx + rw - x) / 2, ry2 + rh / 2 + 5,
                  "той самий шматок відео", size=11.5, color=POS, bold=True))

    P.append(text(W / 2, ry2 + rh + 30,
                  "номер → відновити порядок і помітити втрату · "
                  "мітка часу → показати кадр у свій момент",
                  size=12, color=INK))
    render("img/raw-vs-rtp.svg", W, H, *P)


# ── Фігура 2: буфер джитера ─────────────────────────────────────────────────
# Ідея: пакети приходять нерівно й не по порядку (джитер мережі); буфер їх
# ПРИДЕРЖУЄ й ПЕРЕСОРТОВУЄ за номером, а плеєр забирає РІВНО, кадр за кадром.
# Глибина буфера = головна ручка: глибше — плавніше, але більша затримка.
def fig_jitter_buffer():
    W, H = 940, 460
    P = []
    P.append(text(W / 2, 30, "Буфер джитера: нерівний прихід → рівний показ",
                  size=17, bold=True))

    cx = W / 2
    # три смуги: прихід з мережі → буфер → показ
    y_in = 95
    y_buf = 235
    y_out = 360

    # ── вхід: пакети нерівно в часі й не по порядку ──
    P.append(text(120, y_in - 22, "прихід із мережі", size=12.5, bold=True, anchor="start"))
    P.append(line(120, y_in, W - 60, y_in, color="#d0d5dd", sw=1.2))
    # позиції в часі (нерівні) і номери (переплутані: 3 перед 2)
    arrivals = [(150, "1"), (235, "3"), (300, "2"), (430, "4"),
                (470, "5"), (610, "7"), (650, "6"), (790, "8")]
    for x, n in arrivals:
        col = POS if n in ("3", "7") else NEG   # ті, що випередили сусіда
        P.append(circle(x, y_in, 12, fill="#eaf0fd" if col == NEG else "#fdecea", stroke=col, sw=2))
        P.append(text(x, y_in + 4, n, size=11, color=col, bold=True))
    P.append(text(W - 60, y_in + 24, "нерівні проміжки, 3 перед 2, 7 перед 6 →",
                  size=11, color=MUTED, anchor="end"))

    # ── буфер: коробка, що збирає й сортує ──
    bw, bh = 360, 64
    bx = cx - bw / 2
    P.append(rect(bx, y_buf - bh / 2, bw, bh, fill="#e9f7ef", stroke=FIELD, sw=2))
    for i in range(6):
        sx = bx + 30 + i * (bw - 60) / 5
        P.append(circle(sx, y_buf, 12, fill=BG, stroke=FIELD, sw=1.6))
        P.append(text(sx, y_buf + 4, str(i + 1), size=11, color=FIELD, bold=True))
    P.append(text(cx, y_buf - bh / 2 - 12, "БУФЕР: придержати кілька кадрів і поставити за номером",
                  size=12, color=FIELD, bold=True))
    P.append(arrow(cx, y_in + 16, cx, y_buf - bh / 2 - 4, color=MUTED))

    # ── вихід: рівний показ ──
    P.append(text(120, y_out - 22, "показ на екрані", size=12.5, bold=True, anchor="start"))
    P.append(line(120, y_out, W - 60, y_out, color="#d0d5dd", sw=1.2))
    for i in range(8):
        x = 175 + i * 78          # РІВНІ проміжки
        P.append(circle(x, y_out, 12, fill="#e9f7ef", stroke=FIELD, sw=2))
        P.append(text(x, y_out + 4, str(i + 1), size=11, color=FIELD, bold=True))
    P.append(arrow(cx, y_buf + bh / 2 + 4, cx, y_out - 16, color=FIELD))
    P.append(text(W - 60, y_out + 24, "по порядку, рівним кроком",
                  size=11, color=FIELD, anchor="end", bold=True))

    P.append(text(cx, H - 18,
                  "глибший буфер → плавніше, та більша затримка — це головна ручка живого відео",
                  size=12, color=INK))
    render("img/jitter-buffer.svg", W, H, *P)


# ── Фігура 3: спектр протоколів за затримкою ────────────────────────────────
# Ідея: вибір протоколу = вибір місця на осі «затримка ↔ охоплення». Зліва
# інтерактивні (WebRTC/SRT/RTP) — мілісекунди, точка-точка; справа сегментні
# по HTTP (HLS/DASH) — секунди, зате через будь-який інтернет на мільйони.
def fig_latency_spectrum():
    W, H = 960, 430
    P = []
    P.append(text(W / 2, 30, "Карта протоколів за наскрізною затримкою (glass-to-glass)",
                  size=17, bold=True))

    ax_y = 250
    x0, x1 = 70, W - 70
    P.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2))
    P.append(arrow(x1 - 4, ax_y, x1 + 8, ax_y, color=INK))
    P.append(text(x0, ax_y + 50, "↓ затримка · ↑ керованість/двобічність",
                  size=11.5, color=MUTED, anchor="start"))
    P.append(text(x1, ax_y + 50, "↑ затримка · ↑ охоплення/масштаб",
                  size=11.5, color=MUTED, anchor="end"))

    # позначки шкали
    ticks = [(x0 + 40, "<0.1 с"), (x0 + 250, "0.1–0.5 с"),
             ((x0 + x1) / 2 + 60, "1–3 с"), (x1 - 90, "5–30 с")]
    for tx, lab in ticks:
        P.append(line(tx, ax_y - 6, tx, ax_y + 6, color=INK, sw=1.6))
        P.append(text(tx, ax_y + 24, lab, size=11, color=MUTED))

    # картки протоколів над віссю
    cards = [
        (x0 + 60, "WebRTC", "відеодзвінок,\nкерування наживо", FIELD, "#e9f7ef"),
        (x0 + 250, "SRT / RTP·RTSP", "контрибуція,\nкамери, дрон-лінк", NEG, "#eaf0fd"),
        ((x0 + x1) / 2 + 70, "LL-HLS\nLL-DASH", "інтерактивне\nмовлення", INK, "#eef2f7"),
        (x1 - 100, "HLS / DASH\nRTMP→CDN", "VOD і мовлення\nна мільйони", POS, "#fdecea"),
    ]
    for tx, name, use, col, fill in cards:
        fr, w, h = textbox(tx, ax_y - 95, name, size=12.5, bold=True,
                           color=col, fill=fill, stroke=col, min_w=120)
        P.append(fr)
        P.append(arrow(tx, ax_y - 95 + h / 2, tx, ax_y - 6, color=col))
        P.append(mtext(tx, ax_y - 95 - h / 2 - 24, use, size=10.5, color=MUTED))

    P.append(text(W / 2, H - 18,
                  "що менша затримка, то ближче «точка-точка»; що більше охоплення, "
                  "то товщі буфери й сегменти",
                  size=12, color=INK))
    render("img/latency-spectrum.svg", W, H, *P)


# ── Фігура 4 (вставка hist-rtp): вавилон форматів → спільний RTP ─────────────
# Ідея: до RTP кожен інструмент MBone (vat, nv, vic) ліпив СВІЙ заголовок
# поверх UDP — і вони не розуміли одне одного. AVT-група IETF побачила, що
# під сподом усім потрібні ТІ САМІ три поля, і винесла їх у ОДИН спільний
# заголовок — RTP. Звідси сумісність: різні кодеки, той самий конверт.
def fig_babel_to_rtp():
    W, H = 940, 470
    P = []
    P.append(text(W / 2, 30, "До RTP — вавилон форматів; після — один спільний заголовок",
                  size=16.5, bold=True))

    # ── зверху: три інструменти, кожен зі своїм НЕсумісним заголовком ──
    P.append(text(W / 2, 64, "Кожен інструмент MBone ліпив СВІЙ заголовок поверх UDP",
                  size=12.5, bold=True, color=POS))
    tools = [
        (160, "vat (звук)", "свій лічильник\nсвоя мітка часу", POS, "#fdecea"),
        (W / 2, "nv (відео)", "інакший лічильник\nінакша мітка", POS, "#fdecea"),
        (W - 160, "vic (відео)", "ще третій\nформат полів", POS, "#fdecea"),
    ]
    ty = 84
    for tx, name, body, col, fill in tools:
        fr, w, h = textbox(tx, ty + 34, body, size=10.5, color=MUTED,
                           fill=fill, stroke=col, min_w=150)
        P.append(fr)
        P.append(text(tx, ty + 6, name, size=12, color=col, bold=True))
    # хрести «не розуміють одне одного»
    P.append(text(W / 2, ty + 96, "✗ не розуміють одне одного: ні шлюзу, ні спільного плеєра ✗",
                  size=11.5, color=POS, italic=True))

    # стрілка вниз: AVT-група винесла спільне
    P.append(arrow(W / 2, ty + 110, W / 2, ty + 150, color=FIELD, sw=2.2))
    P.append(text(W / 2 + 14, ty + 134,
                  "AVT-група IETF: під сподом потрібні ТІ САМІ три поля → винести в один",
                  size=11, color=FIELD, anchor="start", bold=True))

    # ── знизу: один спільний RTP-заголовок ──
    ry = ty + 176
    P.append(text(W / 2, ry, "RTP (RFC 1889, 1996 → RFC 3550, 2003): один заголовок на всіх",
                  size=12.5, bold=True, color=FIELD))
    bx, by, bw, bh = 120, ry + 16, W - 240, 58
    segs = [
        ("UDP", 90, "#eef2f7", MUTED),
        ("SEQ\nномер: порядок,\nвтрата", 165, "#e9f7ef", FIELD),
        ("TIMESTAMP\nмітка: коли\nпоказати", 175, "#e9f7ef", FIELD),
        ("PT\nякий\nкодек", 95, "#eef2f7", INK),
    ]
    x = bx
    for lab, w, fill, col in segs:
        P.append(rect(x, by, w, bh, fill=fill, stroke=col))
        P.append(mtext(x + w / 2, by + bh / 2 - 8, lab, size=9.5, color=col, bold=True))
        x += w
    P.append(rect(x, by, bx + bw - x, bh, fill="#fdecea", stroke=POS))
    P.append(mtext(x + (bx + bw - x) / 2, by + bh / 2 - 2,
                   "будь-який\nкодек", size=10.5, color=POS, bold=True))

    P.append(text(W / 2, by + bh + 28,
                  "три поля незмінні — навантаження будь-яке: vat, H.264, Opus, JPEG…  "
                  "тепер усі шлюзи й плеєри розуміють один одного",
                  size=11.5, color=INK))
    render("img/babel-to-rtp.svg", W, H, *P)


# ── Фігура 5 (вставка hist-srt): дорога SRT від болю до стандарту ────────────
# Ідея: контрибуцію наприкінці 2000-х везли дорого (супутник/виділена лінія);
# UDT (Юньхун Ґу, 2001) дав надійний повтор поверх UDP — для ФАЙЛІВ; Haivision
# переставила механіку на живий потік: IBC 2013 (фішка кодерів Makito) →
# NAB 2017 (відкриття коду + SRT Alliance) → 2018 (ліцензія MPL). Мета —
# чистий потік крізь звичайний інтернет без супутникового фургона.
def fig_srt_timeline():
    W, H = 960, 470
    P = []
    P.append(text(W / 2, 30, "Дорога SRT: від дорогої контрибуції до спільного стандарту",
                  size=16.5, bold=True))

    # ── лівий блок: дороге роздвоєння кінця 2000-х ──
    fr, w, h = textbox(150, 120, "супутник АБО\nвиділена лінія\n— надійно, та\nзахмарна ціна",
                       size=11, color=POS, fill="#fdecea", stroke=POS, min_w=170)
    P.append(fr)
    P.append(text(150, 120 - h / 2 - 12, "біль кінця 2000-х", size=11.5, color=POS, bold=True))

    # ── вісь часу ──
    ax_y = 250
    x0, x1 = 70, W - 70
    P.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2))
    P.append(arrow(x1 - 4, ax_y, x1 + 8, ax_y, color=INK))
    P.append(text(x1, ax_y + 86, "час →", size=11.5, color=MUTED, anchor="end"))

    # віхи на осі: (x, рік, заголовок, тіло, колір, заливка, низ?)
    miles = [
        (x0 + 80,  "2001", "UDT",
         "Юньхун Ґу:\nнадійний повтор\nповерх UDP —\nдля файлів", NEG, "#eaf0fd", True),
        (x0 + 300, "2013", "IBC: демо",
         "фішка кодерів\nMakito — потік\nкрізь інтернет", FIELD, "#e9f7ef", False),
        (x0 + 520, "2017", "NAB: відкриття",
         "код вільний +\nSRT Alliance\n(Haivision, Wowza)", FIELD, "#e9f7ef", True),
        (x0 + 720, "2018", "MPL",
         "перехід на\nліцензію Mozilla\n(ще ширше)", NEG, "#eaf0fd", False),
    ]
    for tx, yr, name, body, col, fill, below in miles:
        P.append(circle(tx, ax_y, 7, fill=col, stroke=col))
        P.append(text(tx, ax_y - 12 if not below else ax_y + 22, yr,
                      size=12, color=INK, bold=True))
        cy = ax_y - 92 if not below else ax_y + 96
        fr, w, h = textbox(tx, cy, body, size=10, color=MUTED,
                           fill=fill, stroke=col, min_w=130)
        P.append(fr)
        lab_y = cy - h / 2 - 8 if not below else cy + h / 2 + 16
        P.append(text(tx, lab_y, name, size=11.5, color=col, bold=True))
        # тонка з'єднувальна лінія від краю картки до точки на осі
        if not below:
            P.append(line(tx, cy + h / 2, tx, ax_y - 7, color=col, sw=1.2))
        else:
            P.append(line(tx, ax_y + 7, tx, cy - h / 2, color=col, sw=1.2))

    # ── правий блок: мета ──
    fr, w, h = textbox(W - 150, 380, "чистий потік\nкрізь звичайний\nінтернет — без\nсупутникового\nфургона",
                       size=11, color=FIELD, fill="#e9f7ef", stroke=FIELD, min_w=170)
    P.append(fr)
    P.append(text(W - 150, 380 - h / 2 - 12, "мета SRT", size=11.5, color=FIELD, bold=True))

    P.append(text(W / 2, H - 16,
                  "механіку повтору дала наука (UDT) — Haivision переставила її на "
                  "годинник реального часу",
                  size=11.5, color=INK))
    render("img/srt-timeline.svg", W, H, *P)


# ── Фігура 6 (вставка hist-webrtc): переїзд живого зв'язку в браузер ─────────
# Ідея: до WebRTC браузер сам не вмів живий зв'язок — тягнув сторонній плагін
# (Flash/NPAPI), закритий і дірявий. WebRTC переніс той самий рушій ВСЕРЕДИНУ
# браузера й відкрив його; Google зібрав фундамент із двох покупок 2010-го
# (відео VP8 від On2, живий звук і подавлення луни від GIPS).
def fig_hist_webrtc_shift():
    W, H = 960, 480
    P = []
    P.append(text(W / 2, 30, "Як живий зв'язок переїхав із плагіна в сам браузер",
                  size=17, bold=True))

    midx = W / 2
    P.append(line(midx, 60, midx, H - 70, color="#d0d5dd", sw=1.4, dash="4 6"))

    # ── ЛІВОРУЧ: світ до WebRTC ──
    lx = 60
    P.append(text(lx + 175, 66, "ДО: реальний час крізь плагін",
                  size=13.5, bold=True, color=POS))
    P.append(rect(lx, 92, 350, 66, fill="#eef2f7", stroke=MUTED, sw=1.8))
    P.append(text(lx + 175, 118, "браузер", size=13, bold=True, color=INK))
    P.append(text(lx + 175, 138, "сам не вміє ні камери, ні кодека, ні мережі",
                  size=9.5, color=MUTED))
    P.append(arrow(lx + 175, 192, lx + 175, 160, color=POS))
    P.append(rect(lx + 35, 192, 280, 100, fill="#fdecea", stroke=POS, sw=2))
    P.append(text(lx + 175, 214, "сторонній ПЛАГІН", size=12.5, bold=True, color=POS))
    P.append(text(lx + 175, 232, "Flash / NPAPI · Silverlight · Java", size=10, color=INK))
    P.append(mtext(lx + 175, 254,
                   "камера · кодек · мережа — усе тут\nзакрито · діряво · несумісно",
                   size=9.5, color=MUTED, lh=1.35))
    for i, m in enumerate(["скачай і встанови", "дірка в безпеці", "не на телефонах"]):
        P.append(text(lx + 8, 322 + i * 22, "× " + m, size=10.5, color=POS,
                      anchor="start", bold=True))

    # ── ПРАВОРУЧ: WebRTC ──
    rx = midx + 60
    P.append(text(rx + 175, 66, "WebRTC: рушій усередині браузера",
                  size=13.5, bold=True, color=FIELD))
    # два куплені шматки зверху
    P.append(rect(rx, 88, 168, 64, fill="#e9f7ef", stroke=FIELD, sw=1.8))
    P.append(text(rx + 84, 108, "On2 → VP8", size=11.5, bold=True, color=FIELD))
    P.append(text(rx + 84, 125, "відкрите відео", size=9, color=MUTED))
    P.append(text(rx + 84, 141, "(куплено 2010)", size=9, color=MUTED))
    P.append(rect(rx + 182, 88, 168, 64, fill="#e9f7ef", stroke=FIELD, sw=1.8))
    P.append(text(rx + 266, 108, "GIPS", size=11.5, bold=True, color=FIELD))
    P.append(text(rx + 266, 125, "живий звук, луна", size=9, color=MUTED))
    P.append(text(rx + 266, 141, "(куплено 2010)", size=9, color=MUTED))
    P.append(arrow(rx + 84, 152, rx + 150, 196, color=FIELD))
    P.append(arrow(rx + 266, 152, rx + 200, 196, color=FIELD))
    # браузер з вмонтованим рушієм
    P.append(rect(rx, 196, 350, 96, fill="#eef2f7", stroke=FIELD, sw=2.2))
    P.append(text(rx + 175, 218, "браузер", size=12.5, bold=True, color=INK))
    P.append(rect(rx + 35, 230, 280, 50, fill="#e9f7ef", stroke=FIELD, sw=1.6))
    P.append(text(rx + 175, 250, "WebRTC — вбудований рушій", size=11, bold=True, color=FIELD))
    P.append(text(rx + 175, 268, "відкритий (BSD), той самий у всіх браузерах",
                  size=9, color=MUTED))
    for i, m in enumerate(["без жодних втичок", "шифрування завжди", "скрізь, і на телефоні"]):
        P.append(text(rx + 8, 322 + i * 22, "✓ " + m, size=10.5, color=FIELD,
                      anchor="start", bold=True))

    P.append(text(W / 2, H - 28,
                  "Google скупив фундамент і вмонтував його в браузер — "
                  "«подзвонити» стало звичайною веб-дією",
                  size=12, color=INK))
    render("img/hist-webrtc-shift.svg", W, H, *P)


# ── Фігура 7 (вставка hist-webrtc): 10 років від коду до стандарту ───────────
# Ідея: реалізація випередила стандарт на роки. 2010 — покупки, 2011 —
# відкритий код і перший чорновик, 2013 — перший міжбраузерний дзвінок,
# 2014 — мир про кодек, 2017 — кандидат, 2021 — офіційна Рекомендація.
# Стандарт тут фініш, а не старт: робочий код возив дзвінки задовго до штампа.
def fig_hist_webrtc_timeline():
    W, H = 980, 360
    P = []
    P.append(text(W / 2, 30, "Десять років: від відкритого коду до затвердженого стандарту",
                  size=16.5, bold=True))

    x0, x1 = 80, 900
    y = 175
    P.append(line(x0, y, x1, y, color="#8a8a8a", sw=2.2))
    P.append('<path d="M%.1f %.1f l-10 6 l0 -12 z" fill="#8a8a8a"/>' % (x1, y))

    # віхи: (частка, рік, заголовок, тіло, колір, напрямок: -1 зверху / +1 знизу)
    miles = [
        (0.02, "2010", "Два покупки",
         "Google скуповує фундамент:\nвідео VP8 (On2) + звук (GIPS)", FIELD, -1),
        (0.22, "2011", "Відкритий код",
         "WebRTC під BSD;\nперший чорновик W3C", NEG, +1),
        (0.42, "2013", "Перший дзвінок",
         "міжбраузерний:\nChrome ↔ Firefox", INK, -1),
        (0.60, "2014", "Мир про кодек",
         "обов'язкові ОБИДВА:\nVP8 і H.264", "#b8860b", +1),
        (0.78, "2017", "Кандидат",
         "майже готово:\nCandidate Recommendation", NEG, -1),
        (0.98, "2021", "Стандарт",
         "Рекомендація W3C\n+ стандарти IETF (RFC)", POS, +1),
    ]
    for (t, yr, head, body, col, d) in miles:
        x = x0 + (x1 - x0) * t
        P.append(circle(x, y, 7, fill=BG, stroke=col, sw=2.6))
        if d < 0:
            P.append(line(x, y - 8, x, y - 30, color=col, sw=1.4))
            P.append(text(x, y - 58, yr, size=13, bold=True, color=col))
            P.append(text(x, y - 42, head, size=10.5, bold=True, color=INK))
            P.append(mtext(x, y - 98, body, size=9, color=MUTED, lh=1.35))
        else:
            P.append(line(x, y + 8, x, y + 30, color=col, sw=1.4))
            P.append(text(x, y + 46, yr, size=13, bold=True, color=col))
            P.append(text(x, y + 62, head, size=10.5, bold=True, color=INK))
            P.append(mtext(x, y + 80, body, size=9, color=MUTED, lh=1.35))

    P.append(text(W / 2, H - 14,
                  "робочий код возив дзвінки роками до офіційного штампа — "
                  "стандарт тут фініш, а не старт",
                  size=11.5, color=INK))
    render("img/hist-webrtc-timeline.svg", W, H, *P)


# ── Фігура 8 (вставка proj-adaptive-bitrate): петля зворотного зв'язку ───────
# Ідея: це КОНТУР керування. Приймач міряє втрати й джитер, раз на інтервал
# шле звіт (як RTCP RR); контролер на джерелі за простим правилом рахує НОВИЙ
# цільовий бітрейт; енкодер під нього перебудовується; потік знову їде в канал
# — і коло замикається. Без зворотної стрілки це не керування, а відкритий цикл.
def fig_abr_loop():
    W, H = 960, 440
    P = []
    P.append(text(W / 2, 30, "Адаптивний бітрейт — це замкнений контур керування",
                  size=17, bold=True))

    # чотири вузли по кутах: ліворуч джерело(енкодер)+контролер, праворуч канал+приймач
    boxes = [
        (185, 150, "ЕНКОДЕР  (джерело)", "стискає кадри\nпід цільовий бітрейт", FIELD, "#e9f7ef"),
        (185, 310, "КОНТРОЛЕР бітрейту", "правило: крок угору /\nвниз із гістерезисом", NEG, "#eaf0fd"),
        (W - 185, 150, "КАНАЛ (радіо, мережа)", "губить пакети, додає\nджитер, вужчає на ходу", POS, "#fdecea"),
        (W - 185, 310, "ПРИЙМАЧ  (плеєр)", "лічить втрати й джитер\nза номерами RTP", INK, "#eef2f7"),
    ]
    for cx, by, head, body, col, fill in boxes:
        fr, w, h = textbox(cx, by + 24, body, size=10.5, color=MUTED,
                           fill=fill, stroke=col, sw=1.8, min_w=230)
        P.append(fr)
        P.append(text(cx, by - 6, head, size=12, color=col, bold=True))

    # стрілки по колу за годинниковою
    P.append(arrow(185 + 118, 150 + 12, W - 185 - 118, 150 + 12, color=FIELD, sw=2.4))
    P.append(text(W / 2, 150 - 2, "потік відео (RTP по UDP) →",
                  size=11.5, color=FIELD, bold=True))

    P.append(arrow(W - 185, 150 + 56, W - 185, 310 - 52, color=POS, sw=2.2))
    P.append(mtext(W - 185 + 14, 222, "пакети\nдоходять\n(чи ні)", size=10,
                   color=POS, anchor="start"))

    P.append(arrow(W - 185 - 118, 310 + 12, 185 + 118, 310 + 12, color=NEG, sw=2.4))
    P.append(text(W / 2, 310 + 34,
                  "← звіт про якість (втрати %, джитер) — раз на ~1 с, як RTCP RR",
                  size=11.5, color=NEG, bold=True))

    P.append(arrow(185, 310 - 52, 185, 150 + 56, color=NEG, sw=2.2))
    P.append(mtext(185 - 14, 222, "нова\nцільова\nшвидкість", size=10,
                   color=NEG, anchor="end"))

    P.append(text(W / 2, H - 16,
                  "коло замкнене: канал псується → приймач скаржиться → контролер гасить "
                  "бітрейт → потік пролазить вужчим каналом",
                  size=11.5, color=INK))
    render("img/abr-loop.svg", W, H, *P)


# ── Фігура 9 (вставка proj-adaptive-bitrate): сходи рішення з гістерезисом ────
# Ідея: одного порога мало — на ньому контролер торохтить вгору-вниз. Треба
# ДВА пороги (мертва зона): нижче UP — обережно вгору (×1.05), вище DOWN —
# різко вниз (×(1−0.5p)), між ними — НЕ чіпати. Це рівно правило GCC (втрати
# <2% росте, 2–10% тримає, >10% падає) — деадбенд гасить осциляцію.
def fig_hysteresis_ladder():
    W, H = 940, 450
    P = []
    P.append(text(W / 2, 30, "Гістерезис: дві межі й мертва зона замість однієї",
                  size=17, bold=True))

    ax_x = 250
    y_top, y_bot = 84, 372
    P.append(line(ax_x, y_bot, ax_x, y_top - 10, color=INK, sw=2))
    P.append(arrow(ax_x, y_top, ax_x, y_top - 18, color=INK))
    P.append(text(ax_x, y_top - 26, "втрати, %", size=11.5, color=MUTED))
    P.append(text(ax_x, y_bot + 22, "0%", size=11, color=MUTED))

    y_up_thr = y_bot - 74    # поріг UP (2%)
    y_dn_thr = y_top + 74    # поріг DOWN (10%)
    bw = 340
    bx = ax_x + 20
    # зона РОСТУ (низькі втрати)
    P.append(rect(bx, y_up_thr, bw, y_bot - y_up_thr, fill="#e9f7ef", stroke=FIELD, sw=1.6))
    P.append(mtext(bx + bw / 2, (y_up_thr + y_bot) / 2 - 8,
                   "втрати < 2%  →  крок ВГОРУ  ×1.05\nканал вільний — обережно піднімаємо",
                   size=11, color=FIELD, bold=True))
    # МЕРТВА зона (середина)
    P.append(rect(bx, y_dn_thr, bw, y_up_thr - y_dn_thr, fill="#eef2f7", stroke=MUTED, sw=1.6))
    P.append(mtext(bx + bw / 2, (y_dn_thr + y_up_thr) / 2 - 8,
                   "2% ≤ втрати ≤ 10%  →  ТРИМАТИ\nмертва зона: НЕ чіпати бітрейт",
                   size=11, color=INK, bold=True))
    # зона ПАДІННЯ (високі втрати)
    P.append(rect(bx, y_top, bw, y_dn_thr - y_top, fill="#fdecea", stroke=POS, sw=1.6))
    P.append(mtext(bx + bw / 2, (y_top + y_dn_thr) / 2 - 8,
                   "втрати > 10%  →  крок ВНИЗ  ×(1 − 0.5·p)\nканал захлинається — різко скидаємо",
                   size=11, color=POS, bold=True))

    # позначки порогів на осі
    P.append(line(ax_x - 6, y_up_thr, ax_x + 6, y_up_thr, color=FIELD, sw=2))
    P.append(text(ax_x - 10, y_up_thr + 4, "2%  (UP)", size=10.5, color=FIELD,
                  anchor="end", bold=True))
    P.append(line(ax_x - 6, y_dn_thr, ax_x + 6, y_dn_thr, color=POS, sw=2))
    P.append(text(ax_x - 10, y_dn_thr + 4, "10% (DOWN)", size=10.5, color=POS,
                  anchor="end", bold=True))

    P.append(text(W / 2, H - 16,
                  "це правило Google Congestion Control: проміжок між порогами вгору й вниз "
                  "і є те, що не дає контролеру торохтіти",
                  size=11.5, color=INK))
    render("img/hysteresis-ladder.svg", W, H, *P)


# ── Фігура 10 (вставка proj-adaptive-bitrate): осциляція проти стійкості ──────
# Ідея: контролер без гістерезису (один поріг, симетричні кроки) входить у
# автоколивання — якість стрибає пилкою, глядач бачить миготіння. З мертвою
# зоною й асиметрією (швидко вниз, повільно вгору) бітрейт сідає на стабільну
# поличку трохи нижче ємності каналу. Та сама ємність — два світи.
def fig_oscillation_vs_stable():
    import math
    W, H = 960, 430
    P = []
    P.append(text(W / 2, 30, "Без гістерезису — пилка; з гістерезисом — стабільна поличка",
                  size=16.5, bold=True))

    x0, x1 = 95, W - 60
    cap_y = 145
    P.append(line(x0, cap_y, x1, cap_y, color=MUTED, sw=1.4, dash="7 5"))
    P.append(text(x1, cap_y - 8, "ємність каналу", size=11, color=MUTED, anchor="end"))

    base_y = 362
    P.append(line(x0, base_y, x1, base_y, color=INK, sw=1.6))
    P.append(arrow(x1 - 4, base_y, x1 + 8, base_y, color=INK))
    P.append(text(x1, base_y + 22, "час →", size=11, color=MUTED, anchor="end"))
    P.append(text(x0 - 10, (cap_y + base_y) / 2, "бітрейт", size=11, color=MUTED,
                  anchor="end"))

    # ── ЧЕРВОНА крива: осциляція (пилка навколо ємності) ──
    pts_osc = []
    for i in range(0, 80):
        x = x0 + i * (x1 - x0) / 79.0
        phase = (i % 16)
        if phase < 8:
            y = cap_y + 70 - phase * 15
        else:
            y = cap_y + 70 - (16 - phase) * 15
        pts_osc.append((x, y))
    poly = " ".join("%.1f,%.1f" % (x, y) for x, y in pts_osc)
    P.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (poly, POS))
    P.append(text(x0 + 8, cap_y + 86, "без гістерезису: автоколивання",
                  size=11.5, color=POS, bold=True, anchor="start"))

    # ── ЗЕЛЕНА крива: стійко сідає під ємність і тримається ──
    pts_st = []
    for i in range(0, 80):
        x = x0 + i * (x1 - x0) / 79.0
        if i < 22:
            y = base_y - 30 - i * 5.2
        elif i < 30:
            y = cap_y + 24 + (i - 22) * 2.2
        else:
            y = cap_y + 40 + 4 * math.sin(i / 6.0)
        pts_st.append((x, y))
    poly2 = " ".join("%.1f,%.1f" % (x, y) for x, y in pts_st)
    P.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (poly2, FIELD))
    P.append(text(x1 - 10, cap_y + 60, "з гістерезисом: стабільна поличка під ємністю",
                  size=11.5, color=FIELD, bold=True, anchor="end"))

    P.append(text(W / 2, H - 14,
                  "та сама ємність каналу — два світи: пилка миготить глядачеві, "
                  "поличка дає рівну якість із запасом",
                  size=11.5, color=INK))
    render("img/oscillation-vs-stable.svg", W, H, *P)


if __name__ == "__main__":
    fig_raw_vs_rtp()
    fig_jitter_buffer()
    fig_latency_spectrum()
    fig_babel_to_rtp()
    fig_srt_timeline()
    fig_hist_webrtc_shift()
    fig_hist_webrtc_timeline()
    fig_abr_loop()
    fig_hysteresis_ladder()
    fig_oscillation_vs_stable()
    print("OK: 10 figures -> img/")
