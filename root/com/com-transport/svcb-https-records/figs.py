# -*- coding: utf-8 -*-
"""Фігури до теми «Записи SVCB і HTTPS: параметри служби в одній відповіді DNS»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef3fb"
WARM = "#fdf3e6"
COOL = "#eef8f1"
ALERT = "#fdf2f2"


def box(cx, cy, s, size=12, fill=FILL, bold=False, stroke=LINE, sw=1.5):
    body, w, h = textbox(cx, cy, s, size=size, fill=fill, bold=bold, stroke=stroke, sw=sw)
    return body, w / 2.0, h / 2.0


# ─────────────────────────────────────────────────────────────────────────────
# 1. Порівняння встановлення з'єднання: традиційний стек vs HTTPS Resource Record
# ─────────────────────────────────────────────────────────────────────────────
def fig_connection_flow_comparison():
    W, H = 1040, 700
    f = []

    f.append(text(40, 35, "Порівняння встановлення з'єднання: традиційний HTTP-стек проти HTTPS RR (RFC 9460)",
                  size=14, color=INK, anchor="start", bold=True))

    # Верхня панель: Традиційний шлях (3–4 RTT)
    f.append(rect(30, 55, 980, 285, fill=WARM, stroke="#e6d3b3", sw=1.2, rx=8))
    f.append(text(50, 80, "Традиційний шлях (без HTTPS-запису): 4 RTT до першого шифрованого HTTP/3-запиту",
                  size=12, color=POS, anchor="start", bold=True))

    trad_steps = [
        (140, 150, "1. DNS A / AAAA\n(198.51.100.1)\n1 RTT", "#ffffff"),
        (370, 150, "2. TCP SYN (порт 80)\n+ HTTP 301 Redirect\nна https:// (1 RTT)", "#ffffff"),
        (630, 150, "3. TCP (443) + TLS 1.3\n(відкритий SNI)\n+ HTTP/2 GET (1 RTT)", "#ffffff"),
        (890, 150, "4. Alt-Svc: h3=\":443\"\nЛише НАСТУПНЕ\nз'єднання — QUIC!", ALERT),
    ]

    for cx, cy, label, fill_col in trad_steps:
        b, qw, qh = box(cx, cy, label, size=11, fill=fill_col, stroke="#d97706")
        f.append(b)

    f.append(arrow(215, 150, 285, 150, color="#b45309"))
    f.append(arrow(455, 150, 525, 150, color="#b45309"))
    f.append(arrow(735, 150, 805, 150, color="#b45309"))

    f.append(fitbox(50, 230, 940, 90,
                    "Наслідки старого підходу:\n"
                    "• 3-4 повних кругових затримки (RTT) до завантаження першого байта захищеного контенту.\n"
                    "• Небезпечний незашифрований трафік на порт 80 (можливість перехоплення й підміни редиректу).\n"
                    "• Відкритий SNI (Server Name Indication) у TLS ClientHello видає домен мережевим посередникам.",
                    size=11, fill="#ffffff", stroke="#d97706"))

    # Нижня панель: Шлях з HTTPS RR (1 RTT)
    f.append(rect(30, 360, 980, 310, fill=COOL, stroke="#bbf7d0", sw=1.2, rx=8))
    f.append(text(50, 385, "Оптимізований шлях з HTTPS Resource Record (Type 65): 1 RTT до захищеного HTTP/3",
                  size=12, color=FIELD, anchor="start", bold=True))

    opt_steps = [
        (250, 460, "1. Паралельний DNS:\nHTTPS (Type 65) + A/AAAA\nВідповідь: h3, port 443, ipv4/6hint, ECH\n(1 RTT DNS)", "#ffffff"),
        (760, 460, "2. Прямий запуск QUIC (UDP 443):\nШифрування SNI через ECHConfigList\n+ Handshake + HTTP/3 Request\n(1 RTT з'єднання)", "#ffffff"),
    ]

    for cx, cy, label, fill_col in opt_steps:
        b, qw, qh = box(cx, cy, label, size=11, fill=fill_col, stroke=FIELD)
        f.append(b)

    f.append(arrow(435, 460, 575, 460, color=FIELD, sw=2.2))
    f.append(text(505, 445, "Одразу QUIC + ECH", size=11, color=FIELD, bold=True))

    f.append(fitbox(50, 545, 940, 105,
                    "Переваги нового підходу:\n"
                    "• Економія 2-3 кругових затримок (RTT) під час першого відвідування веб-сайту.\n"
                    "• Схема оновлюється до https:// без запиту на відкритий порт 80 (усунення діри перехоплення).\n"
                    "• Підтримка HTTP/3 QUIC виявляється миттєво з DNS без заголовка Alt-Svc.\n"
                    "• SNI повністю зашифровано через ECH (Encrypted Client Hello) — приватність домену захищена.",
                    size=11, fill="#ffffff", stroke=FIELD))

    render(os.path.join(OUT, 'connection-flow-comparison.svg'), W, H, *f,
           title="Порівняння встановлення з'єднання: традиційний стек проти HTTPS RR")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Структура запису SVCB / HTTPS на дроті (Wire Format)
# ─────────────────────────────────────────────────────────────────────────────
def fig_svcb_record_structure():
    W, H = 1040, 620
    f = []

    f.append(text(40, 35, "Структура записів SVCB (Type 64) та HTTPS (Type 65) у бінарному форматі DNS (RDATA)",
                  size=14, color=INK, anchor="start", bold=True))

    # Загальний заголовок RDATA
    f.append(rect(30, 55, 980, 115, fill=SOFT, stroke="#93c5fd", sw=1.2, rx=8))
    f.append(text(50, 80, "Поля фіксованого заголовка RDATA запису SVCB / HTTPS (RFC 9460):",
                  size=12, color=NEG, anchor="start", bold=True))

    f.append(fitbox(50, 95, 260, 55, "SvcPriority (2 байти, uint16)\n0 = AliasMode, >0 = ServiceMode",
                    size=11, fill="#ffffff", stroke="#3b82f6", bold=True))
    f.append(fitbox(340, 95, 360, 55, "TargetName (змінна довжина, DNS Name)\nДоменне ім'я вузла (або '.' для query name)",
                    size=11, fill="#ffffff", stroke="#3b82f6", bold=True))
    f.append(fitbox(730, 95, 260, 55, "SvcParams (0 або більше байтів)\nСписок пар Key-Value (TLV)",
                    size=11, fill="#ffffff", stroke="#3b82f6", bold=True))

    # Розгалуження на два режими
    # Ліворуч: AliasMode
    f.append(rect(30, 190, 475, 405, fill=WARM, stroke="#fcd34d", sw=1.2, rx=8))
    f.append(text(50, 215, "Режим псевдоніма: AliasMode (SvcPriority = 0)", size=12, color="#b45309", anchor="start", bold=True))
    f.append(fitbox(50, 230, 435, 110,
                    "Формат запису:\n"
                    "example.com.  IN  HTTPS  0  svc.cdn.net.\n\n"
                    "• SvcPriority = 0 вмикає режим перенаправлення (аліасингу).\n"
                    "• TargetName вказує на канонічне ім'я служби.\n"
                    "• SvcParams заборонені (RDATA не містить параметрів).",
                    size=11, fill="#ffffff", stroke="#d97706"))
    f.append(fitbox(50, 355, 435, 220,
                    "Як працює резолвер:\n"
                    "1. Клієнт запитує HTTPS для apex-домену example.com.\n"
                    "2. Сервер повертає пріоритет 0 і ціль svc.cdn.net.\n"
                    "3. Резолвер повторює запит HTTPS для svc.cdn.net.\n"
                    "4. Отримує кінцеві параметри служби (ServiceMode).\n\n"
                    "Головне призначення: заміна CNAME на вершині зони (Apex),\n"
                    "де звичайний CNAME заборонений стандартом DNS (RFC 1034).",
                    size=11, fill="#ffffff", stroke="#d97706"))

    # Праворуч: ServiceMode
    f.append(rect(535, 190, 475, 405, fill=COOL, stroke="#86efac", sw=1.2, rx=8))
    f.append(text(555, 215, "Режим параметрів: ServiceMode (SvcPriority > 0)", size=12, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(555, 230, 435, 110,
                    "Формат запису:\n"
                    "example.com.  IN  HTTPS  1  .  alpn=\"h3,h2\" ipv4hint=198.51.100.1\n\n"
                    "• SvcPriority > 0 (1..65535) вказує на пріоритет ендпоінта.\n"
                    "• TargetName = '.' означає «використовуй те саме ім'я».\n"
                    "• SvcParams містить TLV-блоки конфігурації з'єднання.",
                    size=11, fill="#ffffff", stroke=FIELD))

    f.append(fitbox(555, 355, 435, 220,
                    "Стандартні ключі параметрів SvcParams (TLV):\n"
                    "• Key 0 (mandatory): критичні ключі, обов'язкові для клієнта.\n"
                    "• Key 1 (alpn): список підтримуваних протоколів (h3, h2).\n"
                    "• Key 2 (no-default-alpn): заборона відкату до HTTP/1.1.\n"
                    "• Key 3 (port): нестандартний порт служби (наприклад 8443).\n"
                    "• Key 4 (ipv4hint): список IPv4 адрес для швидкого старту.\n"
                    "• Key 5 (ech): відкритий ключ ECHConfigList для TLS.\n"
                    "• Key 6 (ipv6hint): список IPv6 адрес для Happy Eyeballs.",
                    size=11, fill="#ffffff", stroke=FIELD))

    render(os.path.join(OUT, 'svcb-record-structure.svg'), W, H, *f,
           title="Структура записів SVCB та HTTPS у бінарному форматі DNS")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Розв'язання дилеми CNAME на Apex-домені
# ─────────────────────────────────────────────────────────────────────────────
def fig_apex_alias_resolution():
    W, H = 1040, 580
    f = []

    f.append(text(40, 35, "Розв'язання проблеми CNAME на вершині зони (Apex) через HTTPS AliasMode",
                  size=14, color=INK, anchor="start", bold=True))

    # Ліва колонка: Чому ламається CNAME на apex
    f.append(rect(30, 55, 475, 495, fill=ALERT, stroke="#fca5a5", sw=1.2, rx=8))
    f.append(text(50, 80, "Тупик CNAME на вершині зони (RFC 1034 §3.6.2)", size=12, color=POS, anchor="start", bold=True))

    f.append(fitbox(50, 95, 435, 120,
                    "Обов'язкові записи Apex-домену example.com:\n"
                    "• SOA (Start of Authority) — параметри зони\n"
                    "• NS (Name Server) — авторитетні сервери зони\n"
                    "• MX, TXT, DNSKEY... — пошта, підписи тощо",
                    size=11, fill="#ffffff", stroke=POS))

    f.append(fitbox(50, 230, 435, 110,
                    "Залізне правило CNAME:\n"
                    "«Якщо для вузла є CNAME, ЖОДЕН інший тип запису\n"
                    "не може існувати для цього самого імені».\n\n"
                    "CNAME витісняє все, включаючи SOA та NS!",
                    size=11, fill="#ffffff", stroke=POS, bold=True))

    f.append(fitbox(50, 355, 435, 175,
                    "Наслідки для CDN:\n"
                    "• Не можна делегувати apex (example.com) на CDN через CNAME.\n"
                    "• Провайдери винайшли «костилі»: CNAME flattening, ANAME, ALIAS.\n"
                    "• «Костилі» ламають DNSSEC (підпис руйнується авторитетним сервером)\n"
                    "  та гео-роутинг (сервер резолвить IP замість клієнта).",
                    size=11, fill="#ffffff", stroke=POS))

    # Права колонка: Як HTTPS AliasMode розв'язує задачу
    f.append(rect(535, 55, 475, 495, fill=COOL, stroke="#86efac", sw=1.2, rx=8))
    f.append(text(555, 80, "Чисте рішення: HTTPS AliasMode (RFC 9460)", size=12, color=FIELD, anchor="start", bold=True))

    f.append(fitbox(555, 95, 435, 120,
                    "Зона example.com залишається абсолютно валідною:\n"
                    "example.com.  IN  SOA    ns1.example.com. ...\n"
                    "example.com.  IN  NS     ns1.example.com.\n"
                    "example.com.  IN  HTTPS  0  customer.cdn-provider.net.",
                    size=11, fill="#ffffff", stroke=FIELD))

    f.append(fitbox(555, 230, 435, 110,
                    "Правило сумісності SVCB/HTTPS:\n"
                    "«Запис HTTPS (Type 65) із SvcPriority = 0 є звичайним\n"
                    "типом даних і вільно співіснує з SOA, NS, MX, DNSKEY».\n\n"
                    "Ніякого конфлікту на рівні протоколу DNS!",
                    size=11, fill="#ffffff", stroke=FIELD, bold=True))

    f.append(fitbox(555, 355, 435, 175,
                    "Переваги AliasMode:\n"
                    "• Працює безпосередньо в протоколі DNS без пропрієтарних хаків.\n"
                    "• Повністю сумісний з DNSSEC: запис HTTPS 0 підписується RRSIG зони apex.\n"
                    "• Клієнт або рекурсивний резолвер сам резолвить IP цілі CDN з урахуванням\n"
                    "  власної підмережі (EDNS Client Subnet) для оптимальної доставки контенту.",
                    size=11, fill="#ffffff", stroke=FIELD))

    render(os.path.join(OUT, 'apex-alias-resolution.svg'), W, H, *f,
           title="Розв'язання проблеми CNAME на вершині зони через HTTPS AliasMode")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Захист конфіденційності SNI через ECH у записі HTTPS
# ─────────────────────────────────────────────────────────────────────────────
def fig_ech_privacy_flow():
    W, H = 1040, 600
    f = []

    f.append(text(40, 35, "Захист конфіденційності імені хоста (SNI) через Encrypted Client Hello (ECH)",
                  size=14, color=INK, anchor="start", bold=True))

    # Схема кроків
    # Крок 1: DNS запит через DoH
    f.append(rect(30, 55, 980, 115, fill=SOFT, stroke="#93c5fd", sw=1.2, rx=8))
    f.append(text(50, 80, "Крок 1: Захищений DNS-запит (DoH / DoT) отримує ECHConfig", size=12, color=NEG, anchor="start", bold=True))
    f.append(fitbox(50, 95, 940, 60,
                    "Клієнт запитує HTTPS-запис для private.example.com через зашифрований DoH-канал.\n"
                    "Відповідь: HTTPS 1 . alpn=\"h3,h2\" ech=\"AEn+...\" (містить публічний ключ шифрування сервера HPKE).",
                    size=11, fill="#ffffff", stroke="#3b82f6"))

    # Крок 2: Розщеплення ClientHello
    f.append(rect(30, 185, 980, 245, fill=WARM, stroke="#fcd34d", sw=1.2, rx=8))
    f.append(text(50, 210, "Крок 2: Формування розщепленого TLS 1.3 ClientHello (ClientHelloOuter + ClientHelloInner)",
                  size=12, color="#b45309", anchor="start", bold=True))

    # Внутрішнє і зовнішнє привітання
    f.append(fitbox(50, 225, 445, 185,
                    "ClientHelloOuter (Відкрита обгортка):\n"
                    "• Видима всім спостерігачам у мережі.\n"
                    "• SNI = «public-cdn.com» (покривне/фасадне ім'я CDN).\n"
                    "• Містить розширення encrypted_client_hello\n"
                    "  із зашифрованим корисним навантаженням.\n\n"
                    "Мережевий провайдер чи цензор бачить лише public-cdn.com!",
                    size=11, fill="#ffffff", stroke="#d97706"))

    f.append(fitbox(545, 225, 445, 185,
                    "ClientHelloInner (Зашифроване ядро):\n"
                    "• Зашифровано публічним ключем сервера (HPKE).\n"
                    "• Справжній SNI = «private.example.com».\n"
                    "• Внутрішній ALPN, криптографічні параметри,\n"
                    "  сесійні квитки та розширення.\n\n"
                    "Розшифрувати може ТІЛЬКИ кінцевий веб-сервер або CDN!",
                    size=11, fill=COOL, stroke=FIELD, bold=True))

    # Крок 3: Результат для безпеки
    f.append(rect(30, 445, 980, 125, fill=COOL, stroke="#86efac", sw=1.2, rx=8))
    f.append(text(50, 470, "Крок 3: Результат — повне приховування метаданих користувача", size=12, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(50, 485, 940, 70,
                    "• Усунено останній відкритий витік ідентифікатора веб-сайту в протоколі TLS 1.3.\n"
                    "• Шпигуни, інтернет-провайдери та транзитні оператори не можуть відстежувати конкретні сайти користувача.\n"
                    "• Блокування та цензура за іменем окремого домену стають неможливими без блокування всього CDN.",
                    size=11, fill="#ffffff", stroke=FIELD))

    render(os.path.join(OUT, 'ech-privacy-flow.svg'), W, H, *f,
           title="Захист конфіденційності SNI через ECH у записі HTTPS")


def main():
    fig_connection_flow_comparison()
    fig_svcb_record_structure()
    fig_apex_alias_resolution()
    fig_ech_privacy_flow()
    print("Всі 4 фігури згенеровано успішно.")


if __name__ == '__main__':
    main()
