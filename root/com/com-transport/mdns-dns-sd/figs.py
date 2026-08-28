# -*- coding: utf-8 -*-
"""Фігури до теми «mDNS і DNS-SD: імена та служби без сервера»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef3fb"
WARM = "#fdf3e6"
COOL = "#eef8f1"
ALERT = "#fdecea"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Три опори ZeroConf: Адресація, Розв'язання імен, Виявлення служб
# ─────────────────────────────────────────────────────────────────────────────
def fig_zeroconf_pillars():
    W, H = 1000, 560
    f = []

    f.append(text(500, 32, "Три опори архітектури Zero-Configuration Networking",
                  size=16, color=INK, anchor="middle", bold=True))

    pillars = [
        (40, SOFT, "1. Адресація (Link-Local)",
         "IPv4: 169.254.0.0/16 (RFC 3927)\nIPv6: fe80::/10 (RFC 4862)\n\n• Зондування: ARP Probe / DAD\n• Анонс: ARP Announcement\n• Захист: Defending\n\nПристрій сам обирає IP\nбез DHCP-сервера",
         "#2457d6"),
        (360, WARM, "2. Імена (Multicast DNS)",
         "mDNS (RFC 6762)\nГрупа: 224.0.0.251:5353\nIPv6: [ff02::fb]:5353\n\n• Домен верхнього рівня .local\n• Зондування імен хостів\n• Tie-breaking при колізіях\n\nЗв'язок mydevice.local <-> IP\nбез центрального DNS",
         "#d97706"),
        (680, COOL, "3. Служби (DNS-SD)",
         "DNS-Based Discovery (RFC 6763)\nСемантика DNS-записів:\n\n• PTR: пошук екземплярів типу\n• SRV: цільовий хост і порт\n• TXT: параметри (key=value)\n\nПошук «принтер», «веб-інтерфейс»\nбез попередньої конфігурації",
         "#16a34a"),
    ]

    for px, tone, head, desc, accent in pillars:
        f.append(rect(px, 65, 280, 400, fill=tone, stroke="#cbd5e1", sw=1.5, rx=10))
        f.append(rect(px + 10, 75, 260, 36, fill="#ffffff", stroke=accent, sw=1.5, rx=6))
        f.append(text(px + 140, 98, head, size=13, color=accent, anchor="middle", bold=True))
        
        lines = desc.split("\n")
        cur_y = 135
        for ln in lines:
            if ln.startswith("•"):
                f.append(text(px + 20, cur_y, ln, size=11, color=INK, anchor="start", bold=True))
            elif ln.startswith("IPv") or ln.startswith("mDNS") or ln.startswith("DNS-Based") or ln.startswith("Група:"):
                f.append(text(px + 20, cur_y, ln, size=11, color=MUTED, anchor="start", bold=False))
            elif ln == "":
                cur_y += 6
                continue
            else:
                f.append(text(px + 20, cur_y, ln, size=11, color=INK, anchor="start", bold=False))
            cur_y += 20

    summary = "Результат: пристрій увімкнено в мережу — він дістає IP, публікує ім'я і відкриває служби за 0 секунд конфігурації"
    f.append(fitbox(40, 485, 920, 52, summary, size=12, bold=True, fill="#ffffff", stroke="#94a3b8"))

    render(os.path.join(OUT, "zeroconf-three-pillars.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Структура mDNS-повідомлення та спеціальні біти (QU/QM, Cache-Flush)
# ─────────────────────────────────────────────────────────────────────────────
def fig_mdns_packet():
    W, H = 1040, 600
    f = []

    f.append(text(520, 30, "Анатомія mDNS: розширення формату RFC 1035",
                  size=15, color=INK, anchor="middle", bold=True))

    # Заголовок DNS
    f.append(rect(40, 55, 960, 110, fill=SOFT, stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(55, 78, "Заголовок DNS (12 байтів)", size=13, color=INK, anchor="start", bold=True))
    f.append(text(55, 98, "ID = 0 (у групових mDNS-відповідях кореляція йде за іменем, а не за ID транзакції)", size=11, color=MUTED, anchor="start"))
    f.append(text(55, 118, "Прапорці: QR (0=Query, 1=Response), AA=1 (Authoritative Answer у всіх mDNS відповідях), TC=0, RD=0", size=11, color=MUTED, anchor="start"))
    f.append(text(55, 138, "Лічильники: QDCOUNT (питання), ANCOUNT (відповіді), NSCOUNT (Authority), ARCOUNT (Additional)", size=11, color=MUTED, anchor="start"))

    # Секція Question
    f.append(rect(40, 180, 960, 175, fill=WARM, stroke="#d97706", sw=1.5, rx=8))
    f.append(text(55, 205, "Секція запитання (Question Section)", size=13, color="#b45309", anchor="start", bold=True))
    f.append(text(55, 230, "QNAME: послідовність DNS-міток (наприклад, \x04_http\x04_tcp\x05local\x00)", size=11, color=INK, anchor="start"))
    f.append(text(55, 252, "QTYPE: PTR (12), SRV (33), TXT (16), A (1), AAAA (28), ANY (255)", size=11, color=INK, anchor="start"))

    f.append(rect(55, 268, 930, 72, fill="#ffffff", stroke="#d97706", sw=1.2, rx=6))
    f.append(text(70, 290, "QCLASS: клас запиту + спеціальний біт одноадресної відповіді (QU/QM)", size=12, color="#b45309", anchor="start", bold=True))
    f.append(text(70, 310, "• Старший біт 0x8000 = 1 (QU): Unicast Response — респондер має відповісти на прямий UDP-порт запитувача", size=11, color=INK, anchor="start"))
    f.append(text(70, 328, "• Старший біт 0x8000 = 0 (QM): Multicast Response — відповідь надсилається в групу 224.0.0.251:5353 для всіх", size=11, color=INK, anchor="start"))

    # Секція Resource Record
    f.append(rect(40, 370, 960, 205, fill=COOL, stroke="#16a34a", sw=1.5, rx=8))
    f.append(text(55, 395, "Секція запису ресурсів (Answer / Authority / Additional RR)", size=13, color="#15803d", anchor="start", bold=True))
    f.append(text(55, 420, "NAME (доменне ім'я зі стисненням 0xC000) | TYPE (2 байти) | TTL (4 байти) | RDLENGTH | RDATA", size=11, color=INK, anchor="start"))

    f.append(rect(55, 435, 930, 125, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=6))
    f.append(text(70, 458, "CLASS: клас запису + біт очищення кешу (Cache-Flush Bit)", size=12, color="#15803d", anchor="start", bold=True))
    f.append(text(70, 480, "• Старший біт 0x8000 = 1 (Cache-Flush): Унікальний запис (Unique Record — SRV, TXT, A, AAAA).", size=11, color=INK, anchor="start"))
    f.append(text(90, 498, "Клієнт повинен скинути всі попередні записи цього типу для даного імені та замінити їх новим.", size=11, color=MUTED, anchor="start"))
    f.append(text(70, 520, "• Старший біт 0x8000 = 0: Спільний запис (Shared Record — PTR).", size=11, color=INK, anchor="start"))
    f.append(text(90, 538, "Клієнт додає цей запис до списку відомих екземплярів служби без витирання інших пристроїв.", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "mdns-packet-structure.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Ієрархія резолвінгу DNS-SD (PTR -> SRV + TXT -> A / AAAA)
# ─────────────────────────────────────────────────────────────────────────────
def fig_dnssd_hierarchy():
    W, H = 1040, 620
    f = []

    f.append(text(520, 30, "Триступеневий резолвінг DNS-SD (RFC 6763)",
                  size=15, color=INK, anchor="middle", bold=True))

    steps = [
        (55, SOFT, "1. Пошук екземплярів служби (Запит PTR)",
         "Запит: PTR _http._tcp.local\n"
         "Відповідь PTR: «Датчик Вітальні._http._tcp.local» (Shared Record)\n"
         "Результат: клієнт бачить зрозумілу людині назву служби",
         "#2457d6"),
        (225, WARM, "2. Отримання хоста, порту та метаданих (Запит SRV + TXT)",
         "Запит SRV & TXT: «Датчик Вітальні._http._tcp.local»\n"
         "Відповідь SRV: Priority=0, Weight=0, Port=80, Target=sensor-node.local\n"
         "Відповідь TXT: txtvers=1, model=BME280, path=/api/v1, id=0x4A12\n"
         "Результат: відомі мережевий порт, параметри та канонічне ім'я хоста",
         "#d97706"),
        (415, COOL, "3. Розв'язання імені хоста в IP-адресу (Запит A / AAAA)",
         "Запит A: sensor-node.local\n"
         "Відповідь A: 192.168.1.120 (IPv4 Link-Local: 169.254.88.14)\n"
         "Відповідь AAAA: fe80::208:22ff:fe8a:4b01 (IPv6 Link-Local)\n"
         "Результат: клієнт має IP:PORT для негайного встановлення TCP-з'єднання",
         "#16a34a"),
    ]

    for py, tone, head, desc, accent in steps:
        f.append(rect(40, py, 960, 145, fill=tone, stroke="#cbd5e1", sw=1.5, rx=8))
        f.append(rect(50, py + 10, 940, 28, fill="#ffffff", stroke=accent, sw=1.2, rx=4))
        f.append(text(65, py + 29, head, size=12, color=accent, anchor="start", bold=True))

        lines = desc.split("\n")
        cur_y = py + 58
        for ln in lines:
            if ln.startswith("Запит:"):
                f.append(text(65, cur_y, ln, size=11, color=INK, anchor="start", bold=True))
            elif ln.startswith("Відповідь"):
                f.append(text(65, cur_y, ln, size=11, color="#1e293b", anchor="start", bold=False))
            elif ln.startswith("Результат:"):
                f.append(text(65, cur_y, ln, size=11, color=accent, anchor="start", bold=True))
            cur_y += 20

    opt_box = "Оптимізація DNS-SD: респондер пакує PTR (Answer), SRV+TXT (Authority/Additional) та A/AAAA (Additional) в одну UDP-відповідь!"
    f.append(fitbox(40, 570, 960, 40, opt_box, size=11, bold=True, fill="#ffffff", stroke="#64748b"))

    render(os.path.join(OUT, "dns-sd-lookup-hierarchy.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Часова діаграма зондування (Probing), анонсування (Announcing) та захисту (Defending)
# ─────────────────────────────────────────────────────────────────────────────
def fig_probing_announcing():
    W, H = 1040, 580
    f = []

    f.append(text(520, 28, "Життєвий цикл імені mDNS: Probing -> Announcing -> Defending",
                  size=15, color=INK, anchor="middle", bold=True))

    # Фаза 1: Probing
    f.append(rect(40, 50, 300, 450, fill=ALERT, stroke="#dc2626", sw=1.5, rx=8))
    f.append(text(190, 75, "Фаза 1: Зондування (Probing)", size=13, color="#b91c1c", anchor="middle", bold=True))
    f.append(text(55, 105, "Мета: перевірити відсутність дублів", size=11, color=INK, anchor="start"))
    f.append(text(55, 130, "• 3 запити mDNS ANY з бітом QM", size=11, color=INK, anchor="start"))
    f.append(text(55, 150, "• Інтервал між спробами: 250 мс", size=11, color=INK, anchor="start"))
    f.append(text(55, 170, "• Свої пропоновані записи кладуться", size=11, color=INK, anchor="start"))
    f.append(text(65, 188, "в секцію Authority (NSCOUNT > 0)", size=11, color=MUTED, anchor="start"))
    f.append(text(55, 220, "Колізія (Tie-breaking):", size=11, color="#b91c1c", anchor="start", bold=True))
    f.append(text(55, 240, "• При одночасному зондуванні", size=11, color=INK, anchor="start"))
    f.append(text(65, 258, "порівнюються байти RDATA", size=11, color=INK, anchor="start"))
    f.append(text(55, 280, "• Більший запис перемагає;", size=11, color=INK, anchor="start"))
    f.append(text(65, 298, "той, хто програв, перейменовується:", size=11, color=INK, anchor="start"))
    f.append(text(65, 318, "myhost.local -> myhost-2.local", size=11, color=MUTED, anchor="start"))
    f.append(text(55, 330, "Якщо прийшла чужа відповідь:", size=11, color="#b91c1c", anchor="start", bold=True))
    f.append(text(55, 350, "• Негайне скидання лічильника", size=11, color=INK, anchor="start"))
    f.append(text(55, 370, "• Зміна імені та новий Probe", size=11, color=INK, anchor="start"))

    # Фаза 2: Announcing
    f.append(rect(370, 50, 300, 450, fill=WARM, stroke="#d97706", sw=1.5, rx=8))
    f.append(text(520, 75, "Фаза 2: Оголошення (Announcing)", size=13, color="#b45309", anchor="middle", bold=True))
    f.append(text(385, 105, "Мета: наповнити кеші сусідів", size=11, color=INK, anchor="start"))
    f.append(text(385, 130, "• Якщо 250 мс після 3-го Probe", size=11, color=INK, anchor="start"))
    f.append(text(395, 148, "не було заперечень — ім'я захоплено", size=11, color=INK, anchor="start"))
    f.append(text(385, 180, "• Надсилаються 2 групові відповіді", size=11, color=INK, anchor="start"))
    f.append(text(395, 198, "з інтервалом у 1 секунду", size=11, color=INK, anchor="start"))
    f.append(text(385, 230, "• Біт Cache-Flush = 1 для унікальних", size=11, color=INK, anchor="start"))
    f.append(text(395, 248, "записів (A, AAAA, SRV, TXT)", size=11, color=MUTED, anchor="start"))
    f.append(text(385, 280, "• Значення TTL у повідомленні:", size=11, color=INK, anchor="start"))
    f.append(text(395, 298, "Хост (A/AAAA): 120 секунд", size=11, color=MUTED, anchor="start"))
    f.append(text(395, 318, "Служби (PTR/SRV/TXT): 4500 секунд", size=11, color=MUTED, anchor="start"))
    f.append(text(385, 350, "Сусіди оновлюють свої mDNS-кеші", size=11, color="#b45309", anchor="start", bold=True))

    # Фаза 3: Defending
    f.append(rect(700, 50, 300, 450, fill=COOL, stroke="#16a34a", sw=1.5, rx=8))
    f.append(text(850, 75, "Фаза 3: Захист і Робота (Defending)", size=13, color="#15803d", anchor="middle", bold=True))
    f.append(text(715, 105, "Мета: обробка запитів та захист", size=11, color=INK, anchor="start"))
    f.append(text(715, 130, "• Прослуховування 224.0.0.251:5353", size=11, color=INK, anchor="start"))
    f.append(text(715, 150, "• Відповідь на запити інших вузлів", size=11, color=INK, anchor="start"))
    f.append(text(715, 180, "Захист імені від новачків:", size=11, color="#15803d", anchor="start", bold=True))
    f.append(text(715, 200, "• Якщо чужий вузол надсилає Probe", size=11, color=INK, anchor="start"))
    f.append(text(725, 218, "на наше ім'я — миттєво шлемо", size=11, color=INK, anchor="start"))
    f.append(text(725, 238, "Authoritative Response з TTL", size=11, color=INK, anchor="start"))
    f.append(text(715, 270, "• Новачок бачить нашу відповідь", size=11, color=INK, anchor="start"))
    f.append(text(725, 288, "і відступає на інше ім'я", size=11, color=MUTED, anchor="start"))
    f.append(text(715, 320, "Обмеження шторму захисту:", size=11, color="#15803d", anchor="start", bold=True))
    f.append(text(715, 340, "• Не більше 1 пакета захисту на 1 с", size=11, color=INK, anchor="start"))

    f.append(fitbox(40, 515, 960, 48,
                    "Правило стійкості: вузол ніколи не відповідає на власні зонди та суворо дотримується інтервалів Probing/Announcing",
                    size=12, bold=True, fill="#ffffff", stroke="#94a3b8"))

    render(os.path.join(OUT, "probing-and-announcing.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Оптимізація трафіку: Known-Answer Suppression, Random Delay та Good-bye
# ─────────────────────────────────────────────────────────────────────────────
def fig_suppression_goodbye():
    W, H = 1040, 600
    f = []

    f.append(text(520, 28, "Контроль трафіку в mDNS: захист від мультикаст-штормів",
                  size=15, color=INK, anchor="middle", bold=True))

    mechanisms = [
        (50, SOFT, "1. Придушення відомих відповідей (Known-Answer Suppression)",
         "Проблема: якщо 20 пристроїв питають про одну службу, ефір заб'ється однаковими відповідями.\n"
         "Механізм: запитувач вкладає в секцію Answer запита свої вже відомі записи та їхній залишковий TTL.\n"
         "Респондер: якщо клієнт уже має дійсний запис із залишком TTL > 50% від номіналу — респондер МОВЧИТЬ.",
         "#2457d6"),
        (220, WARM, "2. Випадкова затримка та дублікати (Random Response Delay & Duplicate Suppression)",
         "Проблема: на запит PTR _http._tcp.local 100 веб-серверів одночасно надішлють UDP-пакети (колізія).\n"
         "Механізм: кожен респондер для спільних записів обирає випадкову затримку від 20 до 120 мс.\n"
         "Дублікати: якщо респондер почув чужу відповідь з тими самими даними раніше свого таймера — його відповідь СКАСОВУЄТЬСЯ.",
         "#d97706"),
        (390, COOL, "3. Оголошення про вихід (Good-bye Announcement)",
         "Проблема: вимкнений пристрій «зависає» в кешах клієнтів на 75 хвилин (TTL за замовчуванням).\n"
         "Механізм: при плановому вимкненні вузол надсилає фінальний пакет mDNS із TTL = 0 для всіх своїх записів.\n"
         "Результат: усі клієнти в мережі миттєво видаляють службу зі списків доступних пристроїв без тайм-аутів.",
         "#16a34a"),
    ]

    for py, tone, head, desc, accent in mechanisms:
        f.append(rect(40, py, 960, 150, fill=tone, stroke="#cbd5e1", sw=1.5, rx=8))
        f.append(rect(50, py + 10, 940, 28, fill="#ffffff", stroke=accent, sw=1.2, rx=4))
        f.append(text(65, py + 29, head, size=12, color=accent, anchor="start", bold=True))

        lines = desc.split("\n")
        cur_y = py + 58
        for ln in lines:
            if ln.startswith("Проблема:"):
                f.append(text(65, cur_y, ln, size=11, color="#b91c1c", anchor="start", bold=False))
            elif ln.startswith("Механізм:"):
                f.append(text(65, cur_y, ln, size=11, color=INK, anchor="start", bold=False))
            elif ln.startswith("Респондер:") or ln.startswith("Дублікати:") or ln.startswith("Результат:"):
                f.append(text(65, cur_y, ln, size=11, color=accent, anchor="start", bold=True))
            cur_y += 22

    f.append(fitbox(40, 550, 960, 38,
                    "Комбінація цих трьох механізмів скорочує обсяг мультикаст-трафіку в типовій локальній мережі на 95–99%",
                    size=12, bold=True, fill="#ffffff", stroke="#94a3b8"))

    render(os.path.join(OUT, "suppression-and-goodbye.svg"), W, H, *f)


def main():
    fig_zeroconf_pillars()
    fig_mdns_packet()
    fig_dnssd_hierarchy()
    fig_probing_announcing()
    fig_suppression_goodbye()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
