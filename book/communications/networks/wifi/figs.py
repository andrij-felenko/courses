# -*- coding: utf-8 -*-
"""Фігури до теми «Wi-Fi».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Інфраструктурний режим: усе через точку доступу ──────────────────────
def fig_infra():
    """Зірка, а не сітка: клієнти не говорять напряму, кожен кадр іде через AP.
    Видно подвійну роль точки доступу — арбітр радіоефіру й міст у дріт."""
    W, H = 760, 410
    f = [text(W / 2, 30, "Інфраструктурний режим: усі розмови йдуть через AP", size=17, bold=True)]

    # точка доступу — центр
    apx, apy = W / 2, 175
    f.append(rect(apx - 95, apy - 38, 190, 76, fill="#fff7e6", stroke=POS, sw=1.8))
    f.append(text(apx, apy - 8, "Точка доступу", size=14, bold=True, color=POS))
    f.append(text(apx, apy + 12, "(AP) — роутер", size=11, color=MUTED))
    f.append(text(apx, apy + 30, 'SSID: "MyHome"', size=11, color=INK))

    # три клієнти внизу
    clients = [(150, 330, "Телефон"), (W / 2, 360, "Ноутбук"), (610, 330, "ESP32")]
    for cx, cy, nm in clients:
        f.append(circle(cx, cy, 32, fill="#eef3ff", stroke=NEG, sw=1.8))
        f.append(text(cx, cy + 5, nm, size=11, bold=True, color=NEG))
        # радіолінк клієнт ↔ AP
        f.append(line(cx, cy - 30, apx, apy + 40, color=NEG, sw=1.4, dash="5 4"))
    f.append(text(W / 2, 250, "радіо (Wi-Fi)", size=11, italic=True, color=NEG))

    # вихід у дріт / інтернет — праворуч від AP
    f.append(arrow(apx + 95, apy, 700, apy, color=FIELD, sw=2))
    f.append(fitbox(620, apy - 26, 120, 52, "дріт →\nінтернет", size=12,
                    fill="#eafaf0", stroke=FIELD, sw=1.3, bold=True))

    f.append(text(W / 2, 392, "Клієнти не спілкуються напряму: AP — і арбітр ефіру, і міст у дротову мережу.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "infra.svg"), W, H, *f)


# ── 2. Як приєднатися: скан → автентифікація → асоціація → IP ───────────────
def fig_joining():
    """Чотири кроки приєднання як конвеєр. Ключова думка фінального блоку:
    лише після видачі IP пристрій по-справжньому «в мережі»."""
    W, H = 780, 300
    f = [text(W / 2, 30, "Приєднання до Wi-Fi: чотири кроки до «в мережі»", size=17, bold=True)]

    steps = [
        ("1. Скан", "хто в ефірі?\nслухаю SSID", NEG, "#eef3ff"),
        ("2. Автентифікація", "доводжу пароль\n(WPA2/WPA3)", POS, "#fdecea"),
        ("3. Асоціація", "AP приймає\nмене в мережу", MUTED, "#f4f6f8"),
        ("4. IP-адреса", "роутер видає IP\n(DHCP)", FIELD, "#eafaf0"),
    ]
    n = len(steps)
    bw, gap = 150, 32
    x0 = (W - (n * bw + (n - 1) * gap)) / 2
    cy = 150
    for i, (title, body, col, fill) in enumerate(steps):
        x = x0 + i * (bw + gap)
        f.append(rect(x, cy - 46, bw, 92, fill=fill, stroke=col, sw=1.7))
        f.append(text(x + bw / 2, cy - 22, title, size=13, bold=True, color=col))
        f.append(mtext(x + bw / 2, cy + 2, body.split("\n"), size=11, color=INK, lh=1.4))
        if i < n - 1:
            f.append(arrow(x + bw, cy, x + bw + gap, cy, color=LINE, sw=1.8))

    f.append(text(W / 2, 252, "Доки немає IP — пристрій ще НЕ в мережі: саме видача адреси завершує приєднання.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "joining.svg"), W, H, *f)


# ── 3. Два режими чіпа: STA проти AP ────────────────────────────────────────
def fig_sta_ap():
    """Один чіп — по обидва боки Wi-Fi. Зліва приєднується (STA), справа сам
    тримає мережу (AP). Стрілки показують, хто до кого заходить."""
    W, H = 760, 360
    f = [text(W / 2, 30, "ESP32 по обидва боки Wi-Fi: STA проти AP", size=17, bold=True)]

    # ── STA (ліворуч) ──
    f.append(rect(40, 70, 320, 250, fill=BG, stroke=NEG, sw=1.6))
    f.append(text(200, 96, "STA — клієнт (station)", size=14, bold=True, color=NEG))
    # чужа AP вгорі, ESP знизу заходить до неї
    f.append(rect(120, 120, 160, 48, fill="#fff7e6", stroke=POS, sw=1.5))
    f.append(text(200, 149, "чужа AP (роутер)", size=11, color=POS))
    f.append(circle(200, 268, 30, fill="#eef3ff", stroke=NEG, sw=1.8))
    f.append(text(200, 272, "ESP32", size=11, bold=True, color=NEG))
    f.append(arrow(200, 238, 200, 172, color=NEG, sw=1.8))
    f.append(text(248, 210, "заходжу", size=10, italic=True, color=MUTED, anchor="start"))

    # ── AP (праворуч) ──
    f.append(rect(400, 70, 320, 250, fill=BG, stroke=POS, sw=1.6))
    f.append(text(560, 96, "AP — точка доступу", size=14, bold=True, color=POS))
    # ESP вгорі сам мережа, телефон знизу заходить до нього
    f.append(circle(560, 150, 30, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(560, 154, "ESP32", size=11, bold=True, color=POS))
    f.append(rect(480, 248, 160, 48, fill="#eef3ff", stroke=NEG, sw=1.5))
    f.append(text(560, 277, "телефон заходить", size=11, color=NEG))
    f.append(arrow(560, 248, 560, 184, color=NEG, sw=1.8))

    f.append(text(W / 2, 344, "STA — щоб вийти в інтернет; AP — щоб віддати дані напряму. ESP32 уміє й обидва разом (AP+STA).",
                  size=11, italic=True, color=MUTED))
    render(os.path.join(IMG, "sta-ap.svg"), W, H, *f)


# ── 4. IP-адреси й DHCP ─────────────────────────────────────────────────────
def fig_ip_dhcp():
    """Роутер як роздавач адрес: тримає .1 (шлюз) і автоматично видає кожному
    клієнту вільну адресу зі свого діапазону. Видно, звідки береться IP."""
    W, H = 760, 360
    f = [text(W / 2, 30, "DHCP: роутер сам роздає IP-адреси", size=17, bold=True)]

    # роутер ліворуч
    f.append(rect(50, 130, 190, 100, fill="#fff7e6", stroke=POS, sw=1.8))
    f.append(text(145, 162, "Роутер (DHCP)", size=13, bold=True, color=POS))
    f.append(text(145, 184, "192.168.1.1", size=12, color=INK))
    f.append(text(145, 204, "= шлюз в інтернет", size=10, italic=True, color=MUTED))

    # клієнти праворуч з виданими адресами
    rows = [(120, "Телефон", "192.168.1.10"),
            (180, "Ноутбук", "192.168.1.11"),
            (240, "ESP32", "192.168.1.12")]
    for yy, nm, ip in rows:
        f.append(arrow(240, 180, 470, yy, color=FIELD, sw=1.6))
        f.append(rect(470, yy - 20, 240, 40, fill="#eafaf0", stroke=FIELD, sw=1.4))
        f.append(text(540, yy + 5, nm, size=11, bold=True, color=INK))
        f.append(text(648, yy + 5, ip, size=11, color=FIELD))
    f.append(text(355, 110, "«ось твоя адреса»", size=11, italic=True, color=FIELD))

    f.append(text(W / 2, 312, "Адреса ВИДАЄТЬСЯ при приєднанні — тож може й помінятися; де треба стала, задають фіксований IP.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "ip-dhcp.svg"), W, H, *f)


# ── 5. Дві адреси: MAC (залізна) і IP (мережева) ────────────────────────────
def fig_mac_ip():
    """Два різні рівні на одному пристрої: MAC випалена в радіо назавжди,
    IP видана цією мережею і тимчасова. Аналогія ім'я ↔ адреса проживання."""
    W, H = 760, 340
    f = [text(W / 2, 30, "Дві адреси пристрою: MAC і IP — різні рівні", size=17, bold=True)]

    # MAC — ліворуч
    f.append(rect(50, 80, 320, 180, fill="#fdecea", stroke=POS, sw=1.7))
    f.append(text(210, 108, "MAC — апаратна", size=14, bold=True, color=POS))
    f.append(fitbox(80, 124, 260, 34, "A4:CF:12:9B:5E:07", size=14, fill=BG, stroke=POS, sw=1.2))
    f.append(mtext(210, 188, ["• випалена виробником у радіо",
                              "• унікальна, не міняється",
                              "• «паспорт заліза» — хто це"],
                   size=11, color=INK, lh=1.6))

    # IP — праворуч
    f.append(rect(390, 80, 320, 180, fill="#eafaf0", stroke=FIELD, sw=1.7))
    f.append(text(550, 108, "IP — мережева", size=14, bold=True, color=FIELD))
    f.append(fitbox(440, 124, 220, 34, "192.168.1.12", size=14, fill=BG, stroke=FIELD, sw=1.2))
    f.append(mtext(550, 188, ["• видана цією мережею",
                              "• може змінюватися",
                              "• «де він зараз» у мережі"],
                   size=11, color=INK, lh=1.6))

    f.append(text(W / 2, 300, "MAC — як ім'я людини (дане раз); IP — як її поточна адреса проживання (з переїздом міняється).",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "mac-ip.svg"), W, H, *f)


# ── 6. З IP відкривається весь інтернет ─────────────────────────────────────
def fig_internet():
    """Ланцюг від копійчаного чіпа до хмари: радіо → AP/шлюз → інтернет →
    сервер. Думка — для мережі ESP32 просто ще один вузол із IP."""
    W, H = 780, 280
    f = [text(W / 2, 30, "З IP-адресою маленький чіп дістає весь інтернет", size=17, bold=True)]

    nodes = [("ESP32", "192.168.1.12", "#eef3ff", NEG),
             ("Роутер", "шлюз", "#fff7e6", POS),
             ("Інтернет", "маршрути, DNS", "#f4f6f8", MUTED),
             ("Сервер / хмара", "час, оновлення,\nкоманди", "#eafaf0", FIELD)]
    n = len(nodes)
    bw, gap = 150, 40
    x0 = (W - (n * bw + (n - 1) * gap)) / 2
    cy = 150
    for i, (title, sub, fill, col) in enumerate(nodes):
        x = x0 + i * (bw + gap)
        f.append(rect(x, cy - 40, bw, 80, fill=fill, stroke=col, sw=1.7))
        f.append(text(x + bw / 2, cy - 14, title, size=13, bold=True, color=col))
        f.append(mtext(x + bw / 2, cy + 6, sub.split("\n"), size=10, color=INK, lh=1.35))
        if i < n - 1:
            f.append(arrow(x + bw, cy, x + bw + gap, cy, color=LINE, sw=1.8))

    f.append(text(W / 2, 232, "Уся складність інтернету працює так само, як для ноутбука: ESP32 — просто ще один вузол із IP.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "internet.svg"), W, H, *f)


# ── 7. IP : порт = адреса послуги ───────────────────────────────────────────
def fig_ipport():
    """Чому IP замало: на одному пристрої багато служб. IP веде до будинку,
    порт — до потрібної квартири. Колонка усталених портів робить ідею живою."""
    W, H = 760, 380
    f = [text(W / 2, 30, "IP : порт — повна адреса конкретної послуги", size=17, bold=True)]

    # будинок = пристрій
    f.append(rect(60, 80, 300, 250, fill="#eef3ff", stroke=NEG, sw=1.8))
    f.append(text(210, 108, "Пристрій  192.168.1.12", size=13, bold=True, color=NEG))
    f.append(text(210, 128, "(будинок)", size=11, italic=True, color=MUTED))
    # квартири-порти
    ports = [("80", "веб (HTTP)"),
             ("443", "захищений веб"),
             ("1883", "MQTT"),
             ("22", "віддалений вхід")]
    for i, (p, nm) in enumerate(ports):
        yy = 150 + i * 42
        f.append(rect(82, yy, 256, 34, fill=BG, stroke=MUTED, sw=1.2))
        f.append(text(118, yy + 22, ":" + p, size=13, bold=True, color=FIELD))
        f.append(text(320, yy + 22, nm, size=11, color=INK, anchor="end"))

    # повна адреса праворуч
    f.append(fitbox(420, 150, 280, 60, "повна адреса служби:\n192.168.1.12 : 1883",
                    size=14, fill="#eafaf0", stroke=FIELD, sw=1.5, bold=True))
    f.append(mtext(560, 240, ["IP → ЯКИЙ пристрій", "порт → ЯКА служба на ньому"],
                   size=12, color=INK, lh=1.5))

    f.append(text(W / 2, 360, "IP — це будинок, порт — квартира в ньому; щоб дістатися служби, треба знати і те, і те.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "ip-port.svg"), W, H, *f)


if __name__ == "__main__":
    fig_infra()
    fig_joining()
    fig_sta_ap()
    fig_ip_dhcp()
    fig_mac_ip()
    fig_internet()
    fig_ipport()
    print("OK: 7 figures ->", IMG)
