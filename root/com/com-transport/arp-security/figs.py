# -*- coding: utf-8 -*-
"""Фігури до теми «Безпека ARP: отруєння кешу та захист».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Механіка отруєння ARP-кешу та MitM-перехоплення ─────────────────────
def fig_arp_cache_poisoning():
    """Схема повнодуплексного отруєння ARP-кешу (Full-duplex ARP Poisoning).
    Атакувальник шле підроблені ARP-відповіді жертві та шлюзу,
    перехоплюючи весь трафік в обох напрямках."""
    W, H = 820, 480
    f = [text(W / 2, 28, "Механіка отруєння ARP-кешу та MitM-перехоплення", size=16, bold=True)]

    # Жертва (Host A) ліворуч зверху
    ha = rect(30, 60, 220, 165, fill="#eef3ff", stroke=NEG, sw=1.5)
    f.append(ha)
    f.append(text(140, 85, "Жертва (Вузол A)", size=13, bold=True, color=NEG))
    f.append(fitbox(45, 100, 190, 24, "IP: 192.168.1.50", size=11, fill=BG, stroke=NEG, sw=1.0))
    f.append(fitbox(45, 128, 190, 24, "MAC: AA:AA:AA:AA:AA:AA", size=10, fill=BG, stroke=NEG, sw=1.0))
    f.append(rect(45, 160, 190, 52, fill="#fdecea", stroke=POS, sw=1.0))
    f.append(text(140, 178, "Отруєний ARP-кеш A:", size=10, bold=True, color=POS))
    f.append(text(140, 198, "192.168.1.1 → MM:MM:.. (Атака)", size=9, bold=True, color=POS))

    # Шлюз (Gateway G) праворуч зверху
    hg = rect(570, 60, 220, 165, fill="#eafaf0", stroke=FIELD, sw=1.5)
    f.append(hg)
    f.append(text(680, 85, "Шлюз за замовчуванням (G)", size=13, bold=True, color=FIELD))
    f.append(fitbox(585, 100, 190, 24, "IP: 192.168.1.1", size=11, fill=BG, stroke=FIELD, sw=1.0))
    f.append(fitbox(585, 128, 190, 24, "MAC: GG:GG:GG:GG:GG:GG", size=10, fill=BG, stroke=FIELD, sw=1.0))
    f.append(rect(585, 160, 190, 52, fill="#fdecea", stroke=POS, sw=1.0))
    f.append(text(680, 178, "Отруєний ARP-кеш G:", size=10, bold=True, color=POS))
    f.append(text(680, 198, "192.168.1.50 → MM:MM:.. (Атака)", size=9, bold=True, color=POS))

    # Комутатор (Switch) посередині
    sw_box, sw_w, sw_h = textbox(W / 2, 140, "Комутатор L2\n(Комутація за MAC)", size=11, bold=True,
                                 fill="#f4f6f8", stroke=LINE, min_w=140)
    f.append(sw_box)

    # Атакувальник (Attacker M) знизу
    hm = rect(260, 290, 300, 145, fill="#fdecea", stroke=POS, sw=1.8)
    f.append(hm)
    f.append(text(410, 314, "Атакувальник (Вузол M)", size=14, bold=True, color=POS))
    f.append(fitbox(275, 328, 270, 24, "IP: 192.168.1.100 | MAC: MM:MM:MM:MM:MM:MM", size=10, fill=BG, stroke=POS, sw=1.0))
    f.append(fitbox(275, 356, 270, 32, "IP Forwarding = 1 (Ядро пересилає трафік)\nАналіз / Зміна / Sniffing / SSL Strip", size=9, fill="#fff3e0", stroke=POS, sw=1.0))
    f.append(text(410, 412, "Шле фальшиві ARP Reply кожні 2 с", size=10, bold=True, color=POS))

    # Стрілки фальшивих відповідей ARP (Червоні пунктирні)
    f.append(arrow(340, 290, 170, 230, color=POS, sw=1.8))
    f.append(textbox(215, 255, "ARP Reply (Факт 1):\n192.168.1.1 is at MM:MM", size=9,
                     fill="#fff0f0", stroke=POS, min_w=135)[0])

    f.append(arrow(480, 290, 650, 230, color=POS, sw=1.8))
    f.append(textbox(605, 255, "ARP Reply (Факт 2):\n192.168.1.50 is at MM:MM", size=9,
                     fill="#fff0f0", stroke=POS, min_w=135)[0])

    # Стрілки перехопленого трафіку (Синя і зелена суцільні)
    f.append(arrow(255, 110, 335, 125, color=NEG, sw=2.0))
    f.append(arrow(340, 155, 380, 285, color=NEG, sw=2.0))
    f.append(text(285, 95, "Вихідний трафік A → G", size=9, bold=True, color=NEG))

    f.append(arrow(440, 285, 470, 160, color=FIELD, sw=2.0))
    f.append(arrow(485, 125, 565, 110, color=FIELD, sw=2.0))
    f.append(text(540, 95, "Зворотний трафік G → A", size=9, bold=True, color=FIELD))

    f.append(text(W / 2, 460, "Атакувальник стає прозорим посередником (MitM): обидві сторони надсилають кадри на його MAC.",
                  size=11, italic=True, color=MUTED))
    render(os.path.join(IMG, "arp-cache-poisoning.svg"), W, H, *f)


# ── 2. Безстанове оновлення (Gratuitous ARP) ────────────────────────────────
def fig_gratuitous_arp():
    """Порівняння: легітимне використання Gratuitous ARP (Failover/VRRP)
    проти несанкціонованого отруєння кешів без запиту."""
    W, H = 820, 440
    f = [text(W / 2, 28, "Gratuitous ARP: легітимне перемикання vs отруєння", size=16, bold=True)]

    # Ліва колонка: Легітимний відмовостійкий кластер (VRRP)
    b_leg = rect(30, 60, 365, 335, fill="#f8fafc", stroke=FIELD, sw=1.5)
    f.append(b_leg)
    f.append(text(212, 85, "Легітимний випадок (VRRP / Failover)", size=13, bold=True, color=FIELD))

    m_box, _, _ = textbox(212, 130, "Основний шлюз Master впав!\nРезервний Backup стає Master", size=10,
                          fill="#eafaf0", stroke=FIELD, min_w=280)
    f.append(m_box)

    f.append(fitbox(55, 175, 315, 45, "GARP Broadcast (Opcode=2 / Reply):\nSender IP: 192.168.1.1 (VIP) | Sender MAC: BB:BB\nTarget IP: 192.168.1.1 | Target MAC: FF:FF", size=9, fill=BG, stroke=FIELD, sw=1.2))

    f.append(arrow(212, 225, 212, 260, color=FIELD, sw=1.6))

    res_leg, _, _ = textbox(212, 310, "Результат для підмережі:\n1. Комутатор перевчає MAC-таблицю на новий порт\n2. Хости оновлюють рядок VIP у кеші без перерви зв'язку\n(Час збіжності < 1 секунди)", size=10, fill="#ffffff", stroke=FIELD, min_w=320)
    f.append(res_leg)

    # Права колонка: Зловмисне безстанове отруєння
    b_att = rect(425, 60, 365, 335, fill="#f8fafc", stroke=POS, sw=1.5)
    f.append(b_att)
    f.append(text(607, 85, "Зловмисна експлуатація (Poisoning)", size=13, bold=True, color=POS))

    a_box, _, _ = textbox(607, 130, "Атакувальник підключається до VLAN\nі генерує незапитаний GARP", size=10,
                          fill="#fdecea", stroke=POS, min_w=280)
    f.append(a_box)

    f.append(fitbox(450, 175, 315, 45, "Підроблений GARP (Broadcast / Unicast):\nSender IP: 192.168.1.1 (VIP) | Sender MAC: MM:MM\nTarget IP: 192.168.1.1 | Target MAC: FF:FF", size=9, fill=BG, stroke=POS, sw=1.2))

    f.append(arrow(607, 225, 607, 260, color=POS, sw=1.6))

    res_att, _, _ = textbox(607, 310, "Вразливість безстановості (Stateless):\n1. Хости не перевіряють, чи робили вони запит\n2. Будь-який отриманий GARP перезаписує кеш\n3. Трафік шлюзу захоплено зловмисником", size=10, fill="#ffffff", stroke=POS, min_w=320)
    f.append(res_att)

    f.append(text(W / 2, 420, "Протокол ARP не розрізняє благородне оновлення IP кластера та вороже перехоплення.",
                  size=11, italic=True, color=MUTED))
    render(os.path.join(IMG, "gratuitous-arp-mechanism.svg"), W, H, *f)


# ── 3. Захист на комутаторі: DAI + DHCP Snooping ───────────────────────────
def fig_dai_dhcp_snooping():
    """Архітектура Dynamic ARP Inspection (DAI):
    перевірка ARP-пакетів на недовірених портах за базою DHCP Snooping Binding."""
    W, H = 820, 470
    f = [text(W / 2, 28, "Захист на рівні комутатора: Dynamic ARP Inspection (DAI)", size=16, bold=True)]

    # Вхідний кадр ліворуч
    f.append(rect(30, 60, 210, 110, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(135, 82, "Недовірений порт (Untrusted)", size=11, bold=True, color=POS))
    f.append(fitbox(40, 95, 190, 65, "Вхідний ARP-пакет:\nEth Src: MM:MM:MM:MM:MM:MM\nARP Sender MAC: MM:MM:..\nARP Sender IP: 192.168.1.1", size=9, fill=BG, stroke=POS, sw=1.0))

    # Стрілка входу в комутатор
    f.append(arrow(240, 115, 290, 115, color=LINE, sw=1.8))

    # Ядро комутатора (DAI Engine)
    f.append(rect(295, 55, 495, 365, fill="#f8fafc", stroke=NEG, sw=1.8))
    f.append(text(542, 80, "Комутатор L2: Блок перевірки Dynamic ARP Inspection", size=13, bold=True, color=NEG))

    # Етап 1: Валідація заголовків
    f.append(fitbox(315, 98, 455, 36, "Крок 1. Перевірка цілісності (DAI Validation):\nEth Src MAC == ARP Sender MAC? (Захист від підміни заголовка L2)", size=10, fill="#eef3ff", stroke=NEG, sw=1.1))

    # База даних DHCP Snooping
    f.append(rect(315, 145, 455, 105, fill="#eafaf0", stroke=FIELD, sw=1.4))
    f.append(text(542, 165, "Крок 2. Зіставлення з DHCP Snooping Binding Table", size=11, bold=True, color=FIELD))
    f.append(fitbox(325, 178, 435, 62, "Таблиця прив'язок комутатора (Lease Database):\nMAC: AA:AA:.. → IP: 192.168.1.50 | Port: Fa0/1 | VLAN: 10\nMAC: GG:GG:.. → IP: 192.168.1.1  | Port: Gi0/1 (Trusted) | Static ARP ACL", size=9, fill=BG, stroke=FIELD, sw=1.0))

    # Розгалуження рішення
    f.append(arrow(542, 255, 542, 280, color=LINE, sw=1.5))

    # Гілка 1: Відхилено (Порушення)
    f.append(rect(315, 285, 215, 115, fill="#fdecea", stroke=POS, sw=1.4))
    f.append(text(422, 305, "Невідповідність (Denied)", size=11, bold=True, color=POS))
    f.append(fitbox(325, 315, 195, 75, "1. Пакет скидається (DROP)\n2. Syslog: %SW_DAI-4-DENY\n3. Лічильник rate-limit +1\n(Перевищення → errdisable)", size=9, fill=BG, stroke=POS, sw=1.0))

    # Гілка 2: Дозволено (Valid)
    f.append(rect(555, 285, 215, 115, fill="#eafaf0", stroke=FIELD, sw=1.4))
    f.append(text(662, 305, "Валідний (Permitted)", size=11, bold=True, color=FIELD))
    f.append(fitbox(565, 315, 195, 75, "1. ARP комутується далі\n2. MAC-таблиця оновлюється\n3. Довірені порти (Trunk/Uplink)\nпроходять без перевірок", size=9, fill=BG, stroke=FIELD, sw=1.0))

    f.append(arrow(470, 275, 422, 285, color=POS, sw=1.4))
    f.append(arrow(610, 275, 662, 285, color=FIELD, sw=1.4))

    f.append(text(W / 2, 448, "DAI апаратно фільтрує фальшиві ARP на недовірених портах, використовуючи таблицю легітимних IP-MAC.",
                  size=11, italic=True, color=MUTED))
    render(os.path.join(IMG, "dai-dhcp-snooping-validation.svg"), W, H, *f)


if __name__ == "__main__":
    fig_arp_cache_poisoning()
    fig_gratuitous_arp()
    fig_dai_dhcp_snooping()
    print("Всі фігури згенеровано успішно.")
