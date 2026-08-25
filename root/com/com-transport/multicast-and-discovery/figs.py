# -*- coding: utf-8 -*-
"""Фігури до теми «Багатоадресна розсилка й виявлення вузлів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"    # тепле виділення


# ── 1. Групова IP-адреса → MAC: 28 бітів стискаються до 23 ───────────────────
# Ідея: п'ять бітів відкидають, тому 32 різні групи дістають одну апаратну адресу.
def fig_mac_mapping():
    W, H = 880, 430
    f = [text(W / 2, 28, "Групова адреса в апаратній адресі: 23 біти замість 28", size=15, bold=True)]

    lx, rx = 210, 660          # центри двох прикладів

    for cx, ip, hexs, bits in (
            (lx, "224.1.2.3",   "E0 . 01 . 02 . 03", "0000 0001 · 0000 0010 · 0000 0011"),
            (rx, "239.129.2.3", "EF . 81 . 02 . 03", "1000 0001 · 0000 0010 · 0000 0011")):
        body, w, h = textbox(cx, 82, [ip, hexs], size=13, pad=12,
                             fill="#f7f9fc", stroke=NEG, sw=1.8, bold=False)
        f.append(body)
        f.append(text(cx, 128, "молодші 24 біти адреси", size=10.5, color=MUTED))
        f.append(text(cx, 150, bits, size=11.5, color=INK))

    f.append(text(rx, 172, "цей біт в апаратну адресу не потрапляє", size=10, color=POS))

    # маска
    f.append(fitbox(285, 208, 310, 46, "лишити 23 молодші біти:  & 0x7F.FF.FF",
                    size=12.5, fill="#fffdf0", stroke=AMBER, sw=1.8))

    f.append(arrow(lx, 186, 320, 206, color=LINE, sw=1.8))
    f.append(arrow(rx, 186, 560, 206, color=LINE, sw=1.8))
    f.append(arrow(440, 256, 440, 288, color=LINE, sw=1.8))

    body, w, h = textbox(440, 318, ["MAC  01:00:5E:01:02:03",
                                    "однакова для обох груп"],
                         size=13.5, pad=13, fill="#f2fbf5", stroke=FIELD, sw=2.0, bold=True)
    f.append(body)

    f.append(text(W / 2, 382, "28 значущих бітів адреси групи → 23 біти апаратної адреси",
                  size=11, color=MUTED, italic=True))
    f.append(text(W / 2, 404, "тому 2⁵ = 32 різні групи мережева карта не розрізняє — відбирає вже ядро",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "mac-mapping.svg"), W, H, *f)


# ── 2. Комутатор без підглядання IGMP і з ним ────────────────────────────────
# Ідея: без підглядання груповий кадр заливає всі порти (тобто це широкомовлення),
# з підгляданням комутатор доставляє лише тим портам, що звітували про членство.
def fig_igmp_snooping():
    W, H = 880, 400
    f = [text(W / 2, 28, "Комутатор і груповий кадр: підглядання IGMP вмикає адресність",
              size=15, bold=True)]

    def panel(px, title, joined, tone, notes):
        pw = 400
        g = [rect(px, 50, pw, 300, fill="#fcfcfd", stroke=MUTED, sw=1.4, rx=10)]
        cx = px + pw / 2
        g.append(text(cx, 76, title, size=12.5, color=tone, bold=True))
        g.append(text(cx, 100, "кадр групи 239.1.2.3", size=10.5, color=MUTED))
        g.append(arrow(cx, 108, cx, 130, color=LINE, sw=1.8))
        g.append(fitbox(cx - 90, 134, 180, 38, "комутатор", size=12.5,
                        fill="#f4f6f8", stroke=LINE, sw=1.8))

        hw, gap = 74, 12
        total = 4 * hw + 3 * gap
        x0 = px + (pw - total) / 2
        for i, name in enumerate("ABCD"):
            hx = x0 + i * (hw + gap)
            inside = name in joined
            col = FIELD if inside else MUTED
            g.append(fitbox(hx, 246, hw, 52,
                            [name, "у групі" if inside else "не в групі"],
                            size=11, fill="#f7fbf8" if inside else "#f8f8f8",
                            stroke=col, sw=1.6, color=col))
            if name in tone_targets(joined, title):
                g.append(arrow(cx, 174, hx + hw / 2, 242, color=tone, sw=1.7))

        g.append(text(cx, 322, notes[0], size=10.5, color=MUTED, italic=True))
        g.append(text(cx, 340, notes[1], size=10.5, color=MUTED, italic=True))
        return g

    def tone_targets(joined, title):
        # ліва панель — кадр іде в усі порти; права — лише передплатникам
        return "ABCD" if "без" in title else joined

    f += panel(24, "без підглядання IGMP", "BD", POS,
               ("кадр іде в усі порти — як широкомовний",
                "два вузли з чотирьох платять процесором даремно"))
    f += panel(456, "з підгляданням IGMP", "BD", FIELD,
               ("комутатор запам'ятав порти, що звітували про членство",
                "кадр дістають лише передплатники групи"))
    render(os.path.join(IMG, "igmp-snooping.svg"), W, H, *f)


# ── 3. Дві дзеркальні схеми виявлення ────────────────────────────────────────
# Ідея: запит-відповідь тихий у спокої, але сліпий до зникнень; оголошення
# бачить зникнення саме, зате постійно шумить. Форма панелей навмисно однакова.
def fig_discovery_patterns():
    W, H = 880, 400
    f = [text(W / 2, 28, "Два способи дізнатися, хто в мережі", size=15, bold=True)]

    def panel(px, title, left_label, rows, notes):
        pw = 400
        g = [rect(px, 50, pw, 300, fill="#fcfcfd", stroke=MUTED, sw=1.4, rx=10)]
        cx = px + pw / 2
        g.append(text(cx, 76, title, size=12.5, color=NEG, bold=True))
        g.append(fitbox(px + 26, 92, 130, 36, left_label, size=11.5,
                        fill="#f7f9fc", stroke=NEG, sw=1.6))
        g.append(fitbox(px + 244, 92, 130, 36, "вузли A і B", size=11.5,
                        fill="#f2fbf5", stroke=FIELD, sw=1.6))
        ax_l, ax_r = px + 40, px + 360
        for (y, label, to_right, col) in rows:
            g.append(text(cx, y - 14, label, size=11, color=col))
            if to_right:
                g.append(arrow(ax_l, y, ax_r, y, color=col, sw=1.9))
            else:
                g.append(arrow(ax_r, y, ax_l, y, color=col, sw=1.9))
        g.append(text(cx, 316, notes[0], size=10.5, color=MUTED, italic=True))
        g.append(text(cx, 334, notes[1], size=10.5, color=MUTED, italic=True))
        return g

    f += panel(24, "запит і відповідь", "новачок",
               [(172, "запит у групу: хто надає цю службу?", True, NEG),
                (228, "відповідь A — одноадресно новачкові", False, FIELD),
                (284, "відповідь B — одноадресно новачкові", False, FIELD)],
               ("у спокої мережа мовчить, старт — за одну затримку",
                "зникнення вузла не помітить ніхто, доки не спитають"))

    f += panel(456, "оголошення", "новачок слухає",
               [(172, "A: я тут, адреса й порт, дійсно 120 с", False, FIELD),
                (228, "B: я тут, адреса й порт, дійсно 120 с", False, FIELD),
                (284, "повтор кожні 30 с — інакше запис протухне", False, MUTED)],
               ("новачок нічого не питає — лише слухає",
                "зникнення видно само: запис не оновили, він помер"))
    render(os.path.join(IMG, "discovery-patterns.svg"), W, H, *f)


# ── 4. Шторм відповідей і два способи його вгамувати ─────────────────────────
# Ідея: одночасні відповіді глушать одна одну; випадкове вікно піднімає стелю,
# а придушення вже відомих відповідей прибирає більшість пакетів узагалі.
def fig_response_storm():
    W, H = 880, 420
    f = [text(W / 2, 28, "Відповіді на один запит: чому потрібні вікно й придушення",
              size=15, bold=True)]

    X0, PX_MS = 250, 4.0        # 0 мс на x=250, 4 px на мілісекунду (0…150 мс)
    ROWS = (110, 210, 310)

    def bar(t_ms, axis, col, h=40):
        return rect(X0 + t_ms * PX_MS, axis - h, 3, h, fill=col, stroke=col, sw=0.6, rx=1)

    # рядок 1 — усі одночасно
    axis = ROWS[0] + 30
    f.append(fitbox(24, ROWS[0] - 24, 200, 48, ["усі відповідають", "одразу"],
                    size=11.5, fill="#fdf3f2", stroke=POS, sw=1.6, color=POS))
    for i in range(30):
        f.append(bar(i * 0.15, axis, POS))
    f.append(line(X0, axis, X0 + 150 * PX_MS, axis, color=LINE, sw=1.4))
    f.append(text(330, axis - 22, "зіткнення в ефірі — відповіді втрачено назавжди",
                  size=11, color=POS, anchor="start"))

    # рядок 2 — випадкове вікно 20–120 мс
    axis = ROWS[1] + 30
    f.append(fitbox(24, ROWS[1] - 24, 200, 48, ["випадкова затримка", "20–120 мс"],
                    size=11.5, fill="#fffdf0", stroke=AMBER, sw=1.6, color=AMBER))
    f.append(rect(X0 + 20 * PX_MS, axis - 46, 100 * PX_MS, 46,
                  fill="#fff9e0", stroke="#e6d8a0", sw=1.0, rx=3))
    spread = [21, 24, 28, 31, 35, 38, 42, 45, 49, 53, 57, 61, 64, 68, 72,
              75, 79, 83, 86, 90, 93, 97, 100, 104, 107, 110, 113, 116, 118, 119]
    for t in spread:
        f.append(bar(t, axis, AMBER))
    f.append(line(X0, axis, X0 + 150 * PX_MS, axis, color=LINE, sw=1.4))
    f.append(text(X0 + 70 * PX_MS, axis - 58, "вікно вміщує ≈ 165 відповідей по 0.6 мс",
                  size=11, color=MUTED))

    # рядок 3 — придушення вже відомого
    axis = ROWS[2] + 30
    f.append(fitbox(24, ROWS[2] - 24, 200, 48, ["придушення", "вже відомих"],
                    size=11.5, fill="#f2fbf5", stroke=FIELD, sw=1.6, color=FIELD))
    for t in (26, 58, 95, 117):
        f.append(bar(t, axis, FIELD))
    f.append(line(X0, axis, X0 + 150 * PX_MS, axis, color=LINE, sw=1.4))
    f.append(text(X0 + 75 * PX_MS, axis - 52, "відповідають лише ті, кого питальник ще не знає",
                  size=11, color=MUTED))

    for t in (0, 50, 100, 150):
        f.append(line(X0 + t * PX_MS, axis, X0 + t * PX_MS, axis + 6, color=MUTED, sw=1.2))
        f.append(text(X0 + t * PX_MS, axis + 22, "%d мс" % t, size=10.5, color=MUTED))

    f.append(text(W / 2, 396, "кожна риска — одна відповідь, що займає ефір на ≈ 0.6 мс",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "response-storm.svg"), W, H, *f)


# ── 5. Хто платить за доставку (для оглядової версії) ────────────────────────
# Ідея: широкомовний кадр розбирають усі вузли сегмента, і частина з них робить
# цю роботу даремно; груповий кадр дістають лише ті, хто оголосив, що слухає.
def fig_who_pays():
    W, H = 880, 395
    f = [text(W / 2, 28, "Хто платить за доставку: широкомовна й багатоадресна розсилка",
              size=15, bold=True)]

    def panel(px, title, tone, gets, labels, notes):
        pw = 400
        g = [rect(px, 50, pw, 290, fill="#fcfcfd", stroke=MUTED, sw=1.4, rx=10)]
        cx = px + pw / 2
        g.append(text(cx, 76, title, size=12.5, color=tone, bold=True))
        g.append(fitbox(cx - 75, 88, 150, 34, "відправник", size=11.5,
                        fill="#f7f9fc", stroke=NEG, sw=1.6))
        g.append(arrow(cx, 122, cx, 141, color=LINE, sw=1.8))
        g.append(fitbox(cx - 85, 143, 170, 34, "комутатор", size=11.5,
                        fill="#f4f6f8", stroke=LINE, sw=1.6))

        hw, gap = 76, 10
        total = 4 * hw + 3 * gap
        x0 = px + (pw - total) / 2
        for i, name in enumerate("ABCD"):
            hx = x0 + i * (hw + gap)
            inside = name in gets
            col = tone if inside else MUTED
            g.append(fitbox(hx, 228, hw, 58, [name, labels[name]], size=11,
                            fill="#fdf6f5" if (inside and tone is POS) else
                                 ("#f2fbf5" if inside else "#f8f8f8"),
                            stroke=col, sw=1.6, color=col))
            if inside:
                g.append(arrow(cx, 179, hx + hw / 2, 224, color=tone, sw=1.7))

        g.append(text(cx, 308, notes[0], size=10.5, color=MUTED, italic=True))
        g.append(text(cx, 326, notes[1], size=10.5, color=MUTED, italic=True))
        return g

    f += panel(24, "широкомовна: платять усі", POS, "ABCD",
               {"A": "потрібно", "B": "дарма", "C": "потрібно", "D": "дарма"},
               ("кадр приймають і розбирають усі чотири вузли",
                "двоє з них витрачають процесор на чужі дані"))
    f += panel(456, "багатоадресна: платять передплатники", FIELD, "AC",
               {"A": "у групі", "B": "не бачить", "C": "у групі", "D": "не бачить"},
               ("кадр іде лише тим, хто оголосив, що слухає групу",
                "решта про нього навіть не дізнається"))

    f.append(text(W / 2, 370,
                  "різниця не в тому, скільки надіслано, а в тому, скільки вузлів мусять це розібрати",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "who-pays.svg"), W, H, *f)


# ── 6. Опції на шляху відправлення і на шляху приймання (до вставки api) ─────
# Ідея: кожна опція діє на СВОЄМУ поверсі, і два шляхи не симетричні —
# звідси плутанина «поставив LOOP, а не допомогло».
def fig_sockopt_map():
    W, H = 960, 580
    f = [text(W / 2, 30, "Де саме діє кожна опція: шлях відправлення і шлях приймання",
              size=15, bold=True)]

    f.append(rect(20, 52, 434, 492, fill="#fcfcfd", stroke=MUTED, sw=1.4, rx=10))
    f.append(rect(486, 52, 454, 492, fill="#fcfcfd", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(237, 78, "шлях відправлення", size=13, color=NEG, bold=True))
    f.append(text(713, 78, "шлях приймання", size=13, color=FIELD, bold=True))

    def column(cx, bw, rows, tone):
        g, y = [], 96
        for i, (head, note, kind) in enumerate(rows):
            fill = {"end": "#f7f9fc", "opt": "#ffffff", "call": "#fffdf0"}[kind]
            stroke = {"end": MUTED, "opt": tone, "call": AMBER}[kind]
            g.append(fitbox(cx - bw / 2, y, bw, 44, [head, note], size=12,
                            fill=fill, stroke=stroke, sw=1.7))
            if i < len(rows) - 1:
                g.append(arrow(cx, y + 47, cx, y + 61, color=LINE, sw=1.7))
            y += 64
        return g

    f += column(237, 388, [
        ("sendto(fd, …, 239.1.2.3:5000)", "застосунок віддає датаграму", "call"),
        ("IP_MULTICAST_IF", "з якого інтерфейсу вона вийде", "opt"),
        ("IP_MULTICAST_TTL", "скільки маршрутизаторів переживе (типово 1)", "opt"),
        ("IP_MULTICAST_LOOP", "чи лишити копію собі (типово так)", "opt"),
        ("кадр у мережу", "приєднання для відправлення не потрібне", "end"),
    ], NEG)

    f.append(text(237, 432, "приєднання тут не бере участі взагалі —", size=11,
                  color=MUTED, italic=True))
    f.append(text(237, 452, "слати в групу вільно кожному, хто знає адресу", size=11,
                  color=MUTED, italic=True))
    f.append(text(237, 480, "у Winsock LOOP керує приймальним боком,", size=11,
                  color=POS, italic=True))
    f.append(text(237, 500, "а не відправним — дзеркально до POSIX", size=11,
                  color=POS, italic=True))

    f += column(713, 408, [
        ("кадр на 01:00:5E:01:02:03", "апаратний фільтр картки", "end"),
        ("IP_ADD_MEMBERSHIP", "чи слухає ядро цю групу на цьому інтерфейсі", "opt"),
        ("bind(адреса : порт)", "фільтр за адресою призначення", "call"),
        ("SO_REUSEADDR / SO_REUSEPORT", "скільки сокетів дістануть копію", "opt"),
        ("IP_MULTICAST_ALL (лише Linux)", "чи віддавати ще й чужі групи", "opt"),
        ("recvmsg + IP_PKTINFO", "куди саме прийшло: група й інтерфейс", "call"),
        ("застосунок", "датаграма нарешті в буфері", "end"),
    ], FIELD)

    f.append(text(W / 2, 564,
                  "опція, поставлена не на тому поверсі, не дає ні помилки, ні ефекту",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "sockopt-map.svg"), W, H, *f)


# ── 7. Чим у кожній структурі названо інтерфейс (до вставки api) ─────────────
# Ідея: історія API — це поступова відмова називати інтерфейс його адресою.
def fig_mreq_structs():
    W, H = 1000, 400
    f = [text(W / 2, 30, "Чотири структури приєднання: чим у кожній названо інтерфейс",
              size=15, bold=True)]

    cols = [
        (14, "struct ip_mreq", "POSIX · усюди, зокрема Winsock і lwIP",
         [("imr_multiaddr", "адреса групи"),
          ("imr_interface", "АДРЕСА інтерфейсу")],
         "інтерфейс — адресою", POS),
        (262, "struct ip_mreqn", "Linux 2.2+ · FreeBSD",
         [("imr_multiaddr", "адреса групи"),
          ("imr_address", "адреса, можна 0.0.0.0"),
          ("imr_ifindex", "ІНДЕКС, має перевагу")],
         "індексом, адреса — запасна", FIELD),
        (510, "struct ipv6_mreq", "RFC 3493 · увесь IPv6",
         [("ipv6mr_multiaddr", "адреса групи"),
          ("ipv6mr_interface", "ІНДЕКС, 0 = обере ядро")],
         "лише індексом", FIELD),
        (758, "struct group_req", "RFC 3678 · обидві версії",
         [("gr_interface", "ІНДЕКС"),
          ("gr_group", "sockaddr_storage: v4 або v6")],
         "індексом, адреса будь-яка", FIELD),
    ]

    for x, name, plat, fields, verdict, tone in cols:
        bw = 228
        f.append(rect(x, 58, bw, 236, fill="#ffffff", stroke=MUTED, sw=1.4, rx=8))
        f.append(fitbox(x + 8, 66, bw - 16, 44, [name, plat], size=12,
                        fill="#f7f9fc", stroke=tone, sw=1.6))
        y = 138
        for fname, meaning in fields:
            f.append(text(x + 14, y, fname, size=11.5, color=INK, anchor="start", bold=True))
            f.append(text(x + 14, y + 17, meaning, size=10, color=MUTED, anchor="start"))
            y += 42
        f.append(fitbox(x + 8, 248, bw - 16, 36, verdict, size=11,
                        fill="#fdf6f5" if tone is POS else "#f2fbf5",
                        stroke=tone, sw=1.6, color=tone))

    f.append(text(W / 2, 330,
                  "адресою інтерфейс називають лише в найстарішій формі — і саме там назва неоднозначна:",
                  size=11.5, color=MUTED, italic=True))
    f.append(text(W / 2, 352,
                  "адреса ще не видана DHCP, змінилася або повторюється на двох інтерфейсах — і приєднання йде не туди",
                  size=11.5, color=MUTED, italic=True))
    f.append(text(W / 2, 378,
                  "тому нові API просять індекс: він у інтерфейсу є завжди й один",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "mreq-structs.svg"), W, H, *f)


# ── 8. Форма служби виявлення: один сокет, один цикл (до вставки proj) ───────
# Ідея: уся програма — приєднання на кожному інтерфейсі плюс poll до найближчого строку.
def fig_daemon_loop():
    W, H = 960, 555
    f = [text(W / 2, 28, "Служба виявлення: один сокет, один цикл, три строки",
              size=15, bold=True)]

    MX, MW = 160, 440          # головна колонка
    RX, RW = 640, 292          # права колонка пояснень

    f.append(fitbox(MX, 60, MW, 66,
                    ["1 · getifaddrs(): перебрати інтерфейси",
                     "IP_ADD_MEMBERSHIP на КОЖНОМУ (imr_ifindex ≠ 0)"],
                    size=13, fill="#f7f9fc", stroke=NEG, sw=1.8))
    f.append(fitbox(MX, 160, MW, 66,
                    ["2 · один сокет UDP: bind 0.0.0.0:7711",
                     "SO_REUSEADDR · IP_PKTINFO · IP_MULTICAST_TTL 1"],
                    size=13, fill="#f7f9fc", stroke=NEG, sw=1.8))
    f.append(fitbox(MX, 260, MW, 66,
                    ["3 · poll(sock, найближчий строк − зараз)"],
                    size=13.5, fill="#fffdf0", stroke=AMBER, sw=1.8, bold=True))

    # праворуч від кроку 1 — інтерфейси, кожен зі своєю групою
    for i, s in enumerate(("eth0 · ifindex 2",
                           "wlan0 · ifindex 3",
                           "docker0 · ifindex 4 — теж група")):
        f.append(fitbox(RX, 46 + i * 40, RW, 32, s, size=12,
                        fill=FILL, stroke=MUTED, sw=1.3))
    f.append(arrow(MX + MW + 6, 92, RX - 6, 92, color=LINE, sw=1.7))

    # праворуч від кроку 3 — з чого складається строк
    f.append(fitbox(RX, 250, RW, 104,
                    ["строк = найменший із трьох:",
                     "· наступне оголошення   40 с ±20 %",
                     "· відкладена відповідь   20–120 мс",
                     "· найближче протухання   120 с"],
                    size=12, fill="#fffdf0", stroke=AMBER, sw=1.6))
    f.append(arrow(MX + MW + 6, 300, RX - 6, 300, color=LINE, sw=1.7))

    f.append(fitbox(100, 380, 250, 74,
                    ["прийшов пакет", "recvmsg + IP_PKTINFO → ifindex",
                     "оновити таблицю сусідів"],
                    size=12, fill="#eef4ff", stroke=NEG, sw=1.6))
    f.append(fitbox(410, 380, 250, 74,
                    ["минув строк", "оголосити · відповісти",
                     "вичистити протухле"],
                    size=12, fill="#fdf0ee", stroke=POS, sw=1.6))

    f.append(arrow(MX + MW / 2 - 80, 328, 225, 376, color=LINE, sw=1.7))
    f.append(arrow(MX + MW / 2 + 80, 328, 535, 376, color=LINE, sw=1.7))

    # повернення в цикл: обходимо ліворуч, нічого не перетинаючи
    f.append(line(225, 454, 225, 505, color=MUTED, sw=1.6))
    f.append(line(535, 454, 535, 505, color=MUTED, sw=1.6))
    f.append(line(60, 505, 535, 505, color=MUTED, sw=1.6))
    f.append(line(60, 505, 60, 293, color=MUTED, sw=1.6))
    f.append(arrow(60, 293, MX - 6, 293, color=MUTED, sw=1.6))

    f.append(text(300, 530,
                  "поки в мережі тихо — програма спить у poll і не витрачає нічого",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "daemon-loop.svg"), W, H, *f)


# ── 9. Життя запису в таблиці сусідів (до вставки proj) ──────────────────────
# Ідея: вікна життя перекриваються, тому втрата пакета нічого не коштує,
# а справжнє зникнення видно рівно через час життя запису.
def fig_record_life():
    W, H = 980, 470
    X0, SC, TMAX = 80, 4.85, 172

    def X(t):
        return X0 + t * SC

    f = [text(W / 2, 28, "Життя запису в чужій таблиці: вікна перекриваються, смерть — за строком",
              size=15, bold=True)]

    def axis(y):
        g = [line(X(0), y, X(TMAX), y, color=MUTED, sw=1.4)]
        for t in (0, 40, 80, 120, 160):
            g.append(line(X(t), y, X(t), y + 6, color=MUTED, sw=1.4))
            g.append(text(X(t), y + 20, "%d с" % t, size=10.5, color=MUTED))
        return g

    # ── смуга 1: вузол живий ────────────────────────────────────────────────
    Y1 = 148
    f.append(text(X0, 74, "вузол живий: кожне оголошення відкриває нове вікно на 120 с",
                  size=13, bold=True, anchor="start"))
    f += axis(Y1)
    for t, lost in ((0, False), (37, False), (79, True), (118, False), (155, False)):
        col = POS if lost else NEG
        f.append(line(X(t), Y1 - 32, X(t), Y1, color=col, sw=2.2,
                      dash="4 3" if lost else None))
        f.append(circle(X(t), Y1 - 36, 5, fill=col, stroke=col, sw=1.2))
    f.append(text(X(79), Y1 - 48, "загублене", size=10.5, color=POS))

    for i, (a, b) in enumerate(((0, 120), (37, 157), (118, TMAX), (155, TMAX))):
        yy = Y1 + 36 + i * 14
        f.append(line(X(a), yy, X(b), yy, color=NEG, sw=3.2))
        f.append(circle(X(a), yy, 3.2, fill=NEG, stroke=NEG, sw=1))
    f.append(text(X0, Y1 + 96,
                  "три оголошення за час життя: щоб запис помер, мусять зникнути три поспіль",
                  size=11.5, color=INK, italic=True, anchor="start"))

    # ── смуга 2: вузол зник ─────────────────────────────────────────────────
    Y2 = 330
    f.append(text(X0, 274, "вузол зник після 40-ї секунди: запис доживає рівно свій строк",
                  size=13, bold=True, anchor="start"))
    f += axis(Y2)
    for t in (0, 40):
        f.append(line(X(t), Y2 - 32, X(t), Y2, color=NEG, sw=2.2))
        f.append(circle(X(t), Y2 - 36, 5, fill=NEG, stroke=NEG, sw=1.2))
    f.append(line(X(40), Y2 + 36, X(160), Y2 + 36, color=NEG, sw=3.2))
    f.append(circle(X(40), Y2 + 36, 3.2, fill=NEG, stroke=NEG, sw=1))

    for t in (136, 142, 148, 154):
        f.append(arrow(X(t), Y2 - 10, X(t), Y2 - 34, color=AMBER, sw=1.6))
    f.append(text(X(145), Y2 + 62, "перепити: 80 / 85 / 90 / 95 % життя",
                  size=11, color=AMBER))

    f.append(line(X(160), Y2 - 44, X(160), Y2 + 10, color=POS, sw=2.6))
    f.append(text(X(160), Y2 - 54, "викинуто", size=11, color=POS, bold=True))

    f.append(text(X0, Y2 + 96,
                  "затримка виявлення зникнення = час життя запису; прощальний пакет скорочує її до нуля",
                  size=11.5, color=INK, italic=True, anchor="start"))
    render(os.path.join(IMG, "record-life.svg"), W, H, *f)


# ── 10. Дві доріжки одного винаходу (до вставки hist) ───────────────────────
# Ідея: спільний корінь 1985–1989 розходиться на гілку «між доменами», що
# доходить до офіційного «застаріле», і гілку «в сегменті», що доживає донині.
def fig_hist_timeline():
    W, H = 940, 780
    f = [text(W / 2, 32, "Дві долі одного винаходу: від 1985 до 2020 року",
              size=15, bold=True)]

    # легенда
    for lx, col, lab in ((205, NEG, "спільний корінь"),
                         (475, POS, "між доменами — згасає"),
                         (760, FIELD, "у сегменті — живе")):
        f.append(circle(lx - 92, 66, 6, fill="#ffffff", stroke=col, sw=2.4))
        f.append(text(lx + 6, 70, lab, size=11, color=MUTED))

    SPINE = 158
    rows = [
        ("1985", NEG,   "RFC 966: адреса називає групу, а не машину (Deering, Cheriton, Стенфорд)"),
        ("1986", NEG,   "RFC 988: з'являється IGMP — вузол оголошує членство вголос"),
        ("1988", POS,   "DVMRP (RFC 1075): маршрутизація груп зі статусом Experimental"),
        ("1989", NEG,   "RFC 1112 → STD 5: стандарт для вузлів, відображення на 01:00:5E"),
        ("1992", POS,   "MBone: тунелі поверх інтернету, звук із IETF у Сан-Дієго на ~20 майданчиків"),
        ("1996", POS,   "RTP (RFC 1889): транспорт медіа, народжений на MBone"),
        ("1998", FIELD, "RFC 2365: смуга 239/8 — далі межі організації не йде"),
        ("1999", FIELD, "SSDP: чернетка Microsoft і HP; протухне, але піде в UPnP"),
        ("2002", FIELD, "Apple Rendezvous у складі Mac OS X 10.2"),
        ("2003", POS,   "MSDP (RFC 3618): клей між доменами, статус Experimental назавжди"),
        ("2005", FIELD, "перейменування на Bonjour після позову TIBCO"),
        ("2006", POS,   "SSM (RFC 4607): канал у 232/8 мусить назвати відправника"),
        ("2013", FIELD, "RFC 6762 і RFC 6763: mDNS і DNS-SD нарешті стандарт"),
        ("2015", POS,   "AMT (RFC 7450): знову тунель — як у MBone двадцять три роки перед тим"),
        ("2020", POS,   "RFC 8815 (BCP 229): міждоменний ASM визнано застарілим"),
    ]

    y0, step = 122, 38
    f.insert(1, line(SPINE, y0 - 22, SPINE, y0 + (len(rows) - 1) * step + 22,
                     color="#c9ced6", sw=2.4))

    tint = {NEG: "#f2f5fd", POS: "#fdf3f2", FIELD: "#f1faf4"}
    for i, (year, col, what) in enumerate(rows):
        cy = y0 + i * step
        f.append(text(96, cy + 5, year, size=12.5, bold=True, color=col))
        f.append(circle(SPINE, cy, 6.5, fill="#ffffff", stroke=col, sw=2.4))
        f.append(fitbox(184, cy - 15, 716, 30, what, size=11.5,
                        fill=tint[col], stroke=col, sw=1.4))

    f.append(text(W / 2, y0 + len(rows) * step + 24,
                  "спільний корінь один, а долі різні: між провайдерами — експеримент за експериментом,",
                  size=11, color=MUTED, italic=True))
    f.append(text(W / 2, y0 + len(rows) * step + 44,
                  "у межах сегмента — мільйони пристроїв, що працюють просто зараз",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


# ── 11. У чиєму залізі осідає стан (до вставки hist) ─────────────────────────
# Ідея: суперечку багатоадресність↔CDN вирішив не обсяг трафіку, а те,
# хто мусить тримати стан і хто за нього платить.
def fig_hist_where_state_lives():
    W, H = 980, 470
    f = [text(W / 2, 30, "Де осідає стан: дерево груп проти копії на краю",
              size=15, bold=True)]

    def receivers(cx, ys, col):
        g = []
        for dx, lab in ((-105, "A"), (-35, "B"), (35, "C"), (105, "D")):
            g.append(circle(cx + dx, ys, 15, fill="#ffffff", stroke=col, sw=1.8))
            g.append(text(cx + dx, ys + 5, lab, size=12, color=col, bold=True))
        return g

    # ── ліва панель: багатоадресність ──
    L = 250
    f.append(fitbox(40, 56, 420, 34,
                    "багатоадресність: стан у кожному маршрутизаторі дерева",
                    size=12.5, fill="#fdf3f2", stroke=POS, sw=1.8, bold=True))

    body, w, h = textbox(L, 122, "джерело", size=12, pad=11,
                         fill=FILL, stroke=LINE, sw=1.6)
    f.append(body)
    f.append(arrow(L, 122 + h / 2, L, 168, color=LINE, sw=1.7))

    for rx, ry, bx in ((L, 190, L + 74), (L - 78, 268, L - 152), (L + 78, 268, L + 152)):
        f.append(circle(rx, ry, 20, fill="#ffffff", stroke=POS, sw=2))
        f.append(text(rx, ry + 5, "R", size=13, color=POS, bold=True))
        f.append(text(bx, ry + 4, "(S,G)", size=10.5, color=POS))
    f.append(arrow(L - 12, 208, L - 66, 250, color=POS, sw=1.7))
    f.append(arrow(L + 12, 208, L + 66, 250, color=POS, sw=1.7))
    for rx in (L - 78, L + 78):
        f.append(arrow(rx - 8, 286, rx - 28, 324, color=POS, sw=1.5))
        f.append(arrow(rx + 8, 286, rx + 28, 324, color=POS, sw=1.5))
    f += receivers(L, 344, POS)

    f.append(text(L, 388, "запис про групу тримає кожен вузол дерева,", size=11,
                  color=MUTED, italic=True))
    f.append(text(L, 408, "і тримає його той, кому цей потік нічого не приносить",
                  size=11, color=MUTED, italic=True))

    # ── права панель: одноадресні потоки з кешем на краю ──
    R = 730
    f.append(fitbox(520, 56, 420, 34,
                    "CDN і одноадресні потоки: стан лише на краю",
                    size=12.5, fill="#f1faf4", stroke=FIELD, sw=1.8, bold=True))

    body, w, h = textbox(R, 122, "джерело", size=12, pad=11,
                         fill=FILL, stroke=LINE, sw=1.6)
    f.append(body)
    f.append(arrow(R, 122 + h / 2, R, 176, color=LINE, sw=1.7))

    f.append(fitbox(545, 180, 370, 44,
                    "мережа посередині: звичайні пакети, жодного запису",
                    size=11.5, fill="#f7f9fc", stroke="#c9ced6", sw=1.6))
    f.append(arrow(R, 224, R, 250, color=LINE, sw=1.7))

    body, w, h = textbox(R, 274, ["копія на краю", "стан тільки тут"], size=11.5,
                         pad=11, fill="#f1faf4", stroke=FIELD, sw=2, bold=True)
    f.append(body)
    for dx in (-105, -35, 35, 105):
        f.append(arrow(R + dx * 0.5, 274 + h / 2, R + dx, 324, color=FIELD, sw=1.5))
    f += receivers(R, 344, FIELD)

    f.append(text(R, 388, "мережа посередині про потік не знає нічого,", size=11,
                  color=MUTED, italic=True))
    f.append(text(R, 408, "а стан і рахунок лежать в одних руках", size=11,
                  color=MUTED, italic=True))

    f.append(text(W / 2, 446,
                  "суперечку вирішив не обсяг байтів по дроту, а те, у чиєму залізі осідає стан",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "hist-where-state-lives.svg"), W, H, *f)


if __name__ == "__main__":
    fig_who_pays()
    fig_mac_mapping()
    fig_igmp_snooping()
    fig_discovery_patterns()
    fig_response_storm()
    fig_sockopt_map()
    fig_mreq_structs()
    fig_daemon_loop()
    fig_record_life()
    fig_hist_timeline()
    fig_hist_where_state_lives()
    print("готово:", ", ".join(sorted(os.listdir(IMG))))
