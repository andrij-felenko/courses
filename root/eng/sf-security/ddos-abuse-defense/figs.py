# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. ddos-asymmetry-stack: Асиметрія ресурсів при DDoS ──────────────────────
def fig_ddos_asymmetry_stack():
    W, H = 760, 320
    p = []

    # Заголовок панелі зловмисника
    p.append(rect(30, 35, 330, 260, fill="#fdf2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(195, 62, "Атакувальник (Мінімальні витрати)", size=13, color=POS, bold=True))

    p.append(rect(45, 85, 300, 48, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(195, 103, "L3/L4: Спуфінг IP та ампліфікація", size=11, color=INK, bold=True))
    p.append(text(195, 121, "Генерація сирих пакетів, 0 байт стану", size=10, color=MUTED))

    p.append(rect(45, 145, 300, 48, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(195, 163, "L4: SYN / UDP / ICMP флуд", size=11, color=INK, bold=True))
    p.append(text(195, 181, "1 відправлений пакет = 0 RAM у клієнта", size=10, color=MUTED))

    p.append(rect(45, 205, 300, 75, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(195, 224, "L7: Асиметричні запити (Slowloris / SQL)", size=11, color=INK, bold=True))
    p.append(text(195, 243, "1 повільний HTTP-запит (100 байт)", size=10, color=MUTED))
    p.append(text(195, 262, "Ботнет із тисяч IoT-пристроїв", size=10, color=POS, bold=True))

    # Стрілка протистояння
    p.append(arrow(370, 165, 395, 165, color=LINE, sw=2.2))

    # Заголовок панелі сервера
    p.append(rect(405, 35, 325, 260, fill="#f0f7ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(567, 62, "Сервер-жертва (Колосальні витрати)", size=13, color=NEG, bold=True))

    p.append(rect(420, 85, 295, 48, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(567, 103, "L3/L4: Аллокація sk_buff та conntrack", size=11, color=INK, bold=True))
    p.append(text(567, 121, "Переривання ksoftirqd, забиття каналу", size=10, color=MUTED))

    p.append(rect(420, 145, 295, 48, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(567, 163, "L4: Черга SYN-беклого (struct sock)", size=11, color=INK, bold=True))
    p.append(text(567, 181, "Вичерпання пам'яті таблиці з'єднань", size=10, color=MUTED))

    p.append(rect(420, 205, 295, 75, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(567, 224, "L7: Вичерпання пулу потоків та CPU", size=11, color=INK, bold=True))
    p.append(text(567, 243, "Блокування воркерів (Apache, DB Locks)", size=10, color=MUTED))
    p.append(text(567, 262, "TLS-рукостискання: 1-2 мс CPU на сесію", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "ddos-asymmetry-stack.svg"), W, H, *p,
           title="Асиметрія ресурсів та вектори вичерпання системи при DDoS")


# ── 2. syn-cookie-handshake: Безстанкове встановлення з'єднання ───────────────
def fig_syn_cookie_handshake():
    W, H = 760, 360
    p = []

    # Клієнт
    p.append(rect(40, 30, 160, 45, fill="#ffffff", stroke=INK, sw=1.8, rx=6))
    p.append(text(120, 57, "Клієнт (або Ботнет)", size=12, color=INK, bold=True))

    # Сервер
    p.append(rect(560, 30, 160, 45, fill="#ffffff", stroke=INK, sw=1.8, rx=6))
    p.append(text(640, 57, "Сервер із SYN Cookies", size=12, color=INK, bold=True))

    # Вертикальні лінії життя
    p.append(line(120, 75, 120, 340, color=LINE, sw=1.5, dash="4,3"))
    p.append(line(640, 75, 640, 340, color=LINE, sw=1.5, dash="4,3"))

    # 1. Пакет SYN
    p.append(arrow(120, 105, 640, 105, color=POS, sw=2.0))
    p.append(text(380, 97, "1. TCP SYN (seq = client_isn, mss = 1460)", size=11, color=POS, bold=True))

    # Блок обчислення cookie на сервері
    p.append(rect(480, 125, 250, 70, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(605, 143, "СТАН НЕ ЗБЕРІГАЄТЬСЯ В RAM!", size=10, color=FIELD, bold=True))
    p.append(text(605, 161, "Cookie = [ t (3b) | m (3b) | MAC (26b) ]", size=10, color=INK, bold=True))
    p.append(text(605, 179, "MAC = Hash(src, dst, port, t, secret)", size=9, color=MUTED))

    # 2. Пакет SYN-ACK
    p.append(arrow(640, 215, 120, 215, color=FIELD, sw=2.0))
    p.append(text(380, 207, "2. TCP SYN-ACK (seq = Cookie, ack = client_isn + 1)", size=11, color=FIELD, bold=True))

    # Якщо це підроблений спуфінг - зв'язок обривається (ACK не прийде)
    p.append(text(210, 245, "Спуфінг: ACK ніколи не надійде → нуль витоку пам'яті сервера", size=9, color=MUTED, bold=True))

    # 3. Пакет ACK від легітимного клієнта
    p.append(arrow(120, 275, 640, 275, color=NEG, sw=2.0))
    p.append(text(380, 267, "3. TCP ACK (seq = client_isn + 1, ack = Cookie + 1)", size=11, color=NEG, bold=True))

    # Блок перевірки cookie
    p.append(rect(480, 290, 250, 50, fill="#eef6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(605, 308, "Звірка MAC над (ack - 1) та часом t", size=10, color=NEG, bold=True))
    p.append(text(605, 326, "Створення struct sock лише зараз!", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "syn-cookie-handshake.svg"), W, H, *p,
           title="Безстанкове встановлення TCP-з'єднання за допомогою SYN Cookies")


# ── 3. anycast-scrubbing-pipeline: Конвеєр центру очищення трафіку ───────────
def fig_anycast_scrubbing_pipeline():
    W, H = 760, 310
    p = []

    # Вхідний трафік (Брудний)
    p.append(rect(20, 110, 100, 75, fill="#fdf2f2", stroke=POS, sw=1.8, rx=6))
    p.append(text(70, 137, "Вхідний", size=12, color=POS, bold=True))
    p.append(text(70, 155, "трафік", size=12, color=POS, bold=True))
    p.append(text(70, 172, "(DDoS + Легіт)", size=9, color=MUTED))

    # Стрілка до Anycast Edge
    p.append(arrow(120, 147, 150, 147, color=LINE, sw=2.0))

    # Етап 1: Anycast Edge & BGP Flowspec
    p.append(rect(150, 85, 125, 125, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    p.append(text(212, 107, "Етап 1: Anycast", size=11, color=INK, bold=True))
    p.append(text(212, 125, "Гео-розсіювання", size=10, color=MUTED))
    p.append(text(212, 147, "BGP Flowspec", size=10, color=FIELD, bold=True))
    p.append(text(212, 165, "Апаратний ACL", size=10, color=MUTED))
    p.append(text(212, 183, "RTBH блокування", size=9, color=POS))

    # Стрілка до XDP
    p.append(arrow(275, 147, 305, 147, color=LINE, sw=2.0))

    # Етап 2: XDP & Stateless Scrubber
    p.append(rect(305, 85, 130, 125, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    p.append(text(370, 107, "Етап 2: XDP eBPF", size=11, color=INK, bold=True))
    p.append(text(370, 125, "Безстанковий шар", size=10, color=MUTED))
    p.append(text(370, 147, "XDP_DROP (25Mpps)", size=10, color=POS, bold=True))
    p.append(text(370, 165, "SYN Proxy / Cookies", size=10, color=FIELD, bold=True))
    p.append(text(370, 183, "DNS / TCP челендж", size=9, color=MUTED))

    # Стрілка до L7 WAF
    p.append(arrow(435, 147, 465, 147, color=LINE, sw=2.0))

    # Етап 3: L7 WAF & Rate Limiting
    p.append(rect(465, 85, 130, 125, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    p.append(text(530, 107, "Етап 3: L7 WAF", size=11, color=INK, bold=True))
    p.append(text(530, 125, "Семантичний шар", size=10, color=MUTED))
    p.append(text(530, 147, "TLS термінація", size=10, color=NEG, bold=True))
    p.append(text(530, 165, "JS / PoW челенджі", size=10, color=FIELD, bold=True))
    p.append(text(530, 183, "Rate Limiting / JA4", size=9, color=MUTED))

    # Стрілка до Origin через GRE тунель
    p.append(arrow(595, 147, 630, 147, color=FIELD, sw=2.2))
    p.append(text(612, 138, "GRE / MPLS", size=9, color=FIELD, bold=True))

    # Origin Server (Цільовий бекенд)
    p.append(rect(630, 110, 110, 75, fill="#eaf8f0", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(685, 137, "Оригінальний", size=11, color=FIELD, bold=True))
    p.append(text(685, 155, "сервер", size=11, color=FIELD, bold=True))
    p.append(text(685, 172, "(Очищений трафік)", size=9, color=INK))

    # Підписи під шарами
    p.append(rect(150, 225, 445, 55, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(372, 246, "Багатоешелонована фільтрація: відсікання 99.9% сміття на ранніх рівнях", size=10, color=INK, bold=True))
    p.append(text(372, 266, "L3/L4 скидається без залучення CPU бекенда; важкий L7 інспектується вибірково", size=9, color=MUTED))

    render(os.path.join(OUT, "anycast-scrubbing-pipeline.svg"), W, H, *p,
           title="Архітектура центру очищення та конвеєр фільтрації трафіку")


if __name__ == "__main__":
    fig_ddos_asymmetry_stack()
    fig_syn_cookie_handshake()
    fig_anycast_scrubbing_pipeline()
    print("All figures generated successfully.")
