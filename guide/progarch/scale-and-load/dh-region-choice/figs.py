# -*- coding: utf-8 -*-
"""Фігури до теми «Компакт-вибір планета DH»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_dh_global_topology():
    """Глобальна мультирегіональна топологія платформи Digital Homes."""
    W, H = 1000, 520
    frags = []

    # Загальний рамковий контекст
    frags.append(rect(15, 15, 970, 490, fill="#f9fafb", stroke="#d1d5db", sw=1.2, rx=8))
    frags.append(text(35, 42, "Глобальна мультирегіональна топологія платформи Digital Homes", size=14, bold=True, color=INK, anchor="start"))
    frags.append(text(35, 62, "Розділення глобального реєстру адресації (Global Directory) та локалізованих комірок даних (Home Datacenter Pinning)", size=11, color=MUTED, anchor="start"))

    # 1. Edge / Anycast шар (Верхній блок)
    frags.append(rect(35, 85, 930, 80, fill="#eef2ff", stroke="#6366f1", sw=1.2, rx=6))
    frags.append(text(50, 110, "Край планети: BGP Anycast & Edge PoPs (Cloudflare / Global Accelerator)", size=12, bold=True, color="#3730a3", anchor="start"))
    
    b_edge1, _, _ = textbox(250, 135, "Anycast PoP (Європа)\nL4/L7 Ingestion", size=11, fill="#ffffff", stroke="#818cf8", sw=1.0)
    b_edge2, _, _ = textbox(500, 135, "Anycast PoP (США)\nL4/L7 Ingestion", size=11, fill="#ffffff", stroke="#818cf8", sw=1.0)
    b_edge3, _, _ = textbox(750, 135, "Anycast PoP (Азія)\nL4/L7 Ingestion", size=11, fill="#ffffff", stroke="#818cf8", sw=1.0)
    frags.extend([b_edge1, b_edge2, b_edge3])

    # 2. Global Directory (Центральний координатор)
    b_gdir, _, _ = textbox(500, 225, "Global Home Directory (CockroachDB / Spanner)\nГлобальний реєстр: home_id -> Primary Region DC & Encryption Keys\nСинхронний мультирегіональний кворум (Raft / Paxos)", size=11, fill="#fef3c7", stroke="#d97706", sw=1.5, bold=True)
    frags.append(b_gdir)

    # 3. Регіональні дата-центри (Нижній шар)
    # Регіон ЄС
    frags.append(rect(35, 290, 290, 195, fill="#ffffff", stroke="#93c5fd", sw=1.5, rx=6))
    frags.append(text(180, 312, "Регіон EU-Central-1 (Франкфурт)", size=12, bold=True, color="#1e40af"))
    b_eu_cell, _, _ = textbox(180, 360, "Home Data Cell EU\n* Local PostgreSQL (home_state)\n* MQTT / gRPC Ingestion\n* GDPR Isolation Layer", size=10, fill="#eff6ff", stroke="#3b82f6", sw=1.0)
    b_eu_store, _, _ = textbox(180, 440, "S3 Video / Telemetry Store\n(EU Data Residency Locked)", size=10, fill="#f4f6f8", stroke=MUTED, sw=1.0)
    frags.extend([b_eu_cell, b_eu_store])

    # Регіон США
    frags.append(rect(355, 290, 290, 195, fill="#ffffff", stroke="#93c5fd", sw=1.5, rx=6))
    frags.append(text(500, 312, "Регіон US-East-1 (Вірджинія)", size=12, bold=True, color="#1e40af"))
    b_us_cell, _, _ = textbox(500, 360, "Home Data Cell US\n* Local PostgreSQL (home_state)\n* MQTT / gRPC Ingestion\n* CCPA Isolation Layer", size=10, fill="#eff6ff", stroke="#3b82f6", sw=1.0)
    b_us_store, _, _ = textbox(500, 440, "S3 Video / Telemetry Store\n(US Local Storage)", size=10, fill="#f4f6f8", stroke=MUTED, sw=1.0)
    frags.extend([b_us_cell, b_us_store])

    # Регіон Азія
    frags.append(rect(675, 290, 290, 195, fill="#ffffff", stroke="#93c5fd", sw=1.5, rx=6))
    frags.append(text(820, 312, "Регіон AP-East-1 (Сінгапур)", size=12, bold=True, color="#1e40af"))
    b_ap_cell, _, _ = textbox(820, 360, "Home Data Cell AP\n* Local PostgreSQL (home_state)\n* MQTT / gRPC Ingestion\n* AP-AC Isolation Layer", size=10, fill="#eff6ff", stroke="#3b82f6", sw=1.0)
    b_ap_store, _, _ = textbox(820, 440, "S3 Video / Telemetry Store\n(AP Local Storage)", size=10, fill="#f4f6f8", stroke=MUTED, sw=1.0)
    frags.extend([b_ap_cell, b_ap_store])

    # Стрілки зв'язку
    frags.append(arrow(250, 165, 180, 290, color="#6366f1", sw=1.5))
    frags.append(arrow(500, 165, 500, 205, color="#6366f1", sw=1.5))
    frags.append(arrow(750, 165, 820, 290, color="#6366f1", sw=1.5))

    frags.append(line(500, 245, 180, 290, color="#d97706", sw=1.2, dash="3,3"))
    frags.append(line(500, 245, 500, 290, color="#d97706", sw=1.2, dash="3,3"))
    frags.append(line(500, 245, 820, 290, color="#d97706", sw=1.2, dash="3,3"))

    render(os.path.join(IMG, "dh-global-topology.svg"), W, H, *frags)


def fig_georouting_resolution_flow():
    """Послідовність георутингу та визначення Home Datacenter для хаба DH."""
    W, H = 1000, 460
    frags = []

    frags.append(rect(15, 15, 970, 430, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=8))
    frags.append(text(35, 42, "Маршрутизація з'єднання хаба DH до локалізованого дата-центру", size=14, bold=True, color=INK, anchor="start"))

    # Крок 1: Хаб ініціює підключення
    b1, _, _ = textbox(110, 140, "1. Хаб DH (Париж)\nConnect to:\nconnect.digitalhomes.io", size=10, fill="#eef2ff", stroke="#4f46e5", sw=1.5)
    frags.append(b1)

    # Крок 2: Anycast Edge PoP
    b2, _, _ = textbox(330, 140, "2. Edge Anycast PoP\n(Франкфурт Edge)\nТермінація TLS 1.3\nПеревірка mTLS cert", size=10, fill="#f0fdf4", stroke="#16a34a", sw=1.5)
    frags.append(b2)

    # Крок 3: Global Directory Query
    b3, _, _ = textbox(570, 140, "3. Global Directory\nLookup home_id=8841\n-> Target: EU-Central-1\n-> Active Shard: Cell-04", size=10, fill="#fef3c7", stroke="#d97706", sw=1.5)
    frags.append(b3)

    # Крок 4: Home Datacenter Target
    b4, _, _ = textbox(850, 140, "4. Home Datacenter\n(EU-Central-1)\nDirect gRPC Stream to\nIngest Gateway Cell-04", size=10, fill="#eff6ff", stroke="#2563eb", sw=1.5, bold=True)
    frags.append(b4)

    # Стрілки основного потоку
    frags.append(arrow(190, 140, 250, 140, color=LINE, sw=2.0))
    frags.append(text(220, 125, "BGP Anycast", size=10, color=MUTED))

    frags.append(arrow(410, 140, 490, 140, color=LINE, sw=2.0))
    frags.append(text(450, 125, "Fast Lookup", size=10, color=MUTED))

    frags.append(arrow(650, 140, 770, 140, color=FIELD, sw=2.0))
    frags.append(text(710, 125, "Internal Backbone", size=10, color=FIELD, bold=True))

    # Нижній блок: Резервний шлях під час аварії
    frags.append(rect(35, 240, 930, 180, fill="#fff5f5", stroke="#f87171", sw=1.2, rx=6))
    frags.append(text(50, 265, "Резервний шлях при аварії дата-центру (Region Failover):", size=12, bold=True, color="#991b1b", anchor="start"))

    b_fail1, _, _ = textbox(200, 340, "Аварія EU-Central-1\n(Network Isolation)", size=10, fill="#fee2e2", stroke="#dc2626", sw=1.5)
    b_fail2, _, _ = textbox(500, 340, "Directory Health Gate\nВиявляє падіння DC,\nперемикає прапор на DR", size=10, fill="#ffffff", stroke="#dc2626", sw=1.2)
    b_fail3, _, _ = textbox(800, 340, "DR Target DC\n(US-East-1 Warm Standby)\nПрийом телеметрії в R/O", size=10, fill="#fef2f2", stroke="#b91c1c", sw=1.5)
    frags.extend([b_fail1, b_fail2, b_fail3])

    frags.append(arrow(300, 340, 390, 340, color="#dc2626", sw=1.8))
    frags.append(arrow(610, 340, 700, 340, color="#dc2626", sw=1.8))

    render(os.path.join(IMG, "georouting-resolution-flow.svg"), W, H, *frags)


def fig_cross_region_replication_matrix():
    """Матриця компенсацій CAP/PACELC для доменів Digital Homes."""
    W, H = 1000, 480
    frags = []

    frags.append(rect(15, 15, 970, 450, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=8))
    frags.append(text(35, 42, "Матриця CAP / PACELC: Топологія узгодженості за підсистемами DH", size=14, bold=True, color=INK, anchor="start"))

    # Осі
    frags.append(line(120, 400, 930, 400, color=LINE, sw=2.0))
    frags.append(line(120, 400, 120, 80, color=LINE, sw=2.0))

    frags.append(text(525, 435, "Накладні витрати мережевої затримки (Cross-Region Latency Trade-off)", size=12, bold=True, color=INK))
    frags.append(text(130, 65, "Вимоги до строгості узгодженості (Consistency Level)", size=11, bold=True, color=INK, anchor="start"))

    # Сектори
    # 1. Глобальна узгодженість (Верхній лівий)
    frags.append(rect(140, 90, 360, 140, fill="#fef3c7", stroke="#f59e0b", sw=1.2, rx=6))
    frags.append(text(320, 115, "1. Глобальний IAM та Ключі", size=12, bold=True, color="#b45309"))
    frags.append(mtext(155, 140, ["• Модель: PC/EC (Strong Consistency)", "• Синхронний мультирегіональний Raft", "• Затримка запису: 120-250 ms (крос-DC)", "• Інваріант: унікальність акаунтів"], size=10, color=INK, anchor="start"))

    # 2. Локалізований стан дому (Верхній правий / центр)
    frags.append(rect(530, 90, 380, 140, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(720, 115, "2. Оперативний Стан Дому (Home State)", size=12, bold=True, color="#1d4ed8"))
    frags.append(mtext(545, 140, ["• Модель: PA/EL (Primary Region Pinning)", "• Локальний запис у Primary DC (8-15 ms)", "• Асинхронна реплікація в DR регіон", "• Інваріант: миттєве керування пристроями"], size=10, color=INK, anchor="start"))

    # 3. Телеметрія та часові ряди (Нижній правий)
    frags.append(rect(530, 250, 380, 130, fill="#f0fdf4", stroke="#16a34a", sw=1.2, rx=6))
    frags.append(text(720, 275, "3. Телеметрія датчиків та Медіа", size=12, bold=True, color="#15803d"))
    frags.append(mtext(545, 298, ["• Модель: Eventual Consistency", "• Пакетний асинхронний експорт", "• Затримка: секунди / хвилини", "• Інваріант: втрата метрики некритична"], size=10, color=INK, anchor="start"))

    # 4. Локальна автономія хаба (Нижній лівий)
    frags.append(rect(140, 250, 360, 130, fill="#eef2ff", stroke="#6366f1", sw=1.5, rx=6))
    frags.append(text(320, 275, "4. Автономний режим Хаба (LAN Edge)", size=12, bold=True, color="#4338ca"))
    frags.append(mtext(155, 298, ["• Модель: Offline-First Autonomy", "• Обробка подій без хмари (0 ms)", "• Синхронний зв'язок по Zigbee/LAN", "• Інваріант: безпека при обриві WAN"], size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "cross-region-replication-matrix.svg"), W, H, *frags)


def fig_region_failover_sequence():
    """Алгоритм евакуації регіону DH під час катастрофічного збою дата-центру."""
    W, H = 1000, 500
    frags = []

    frags.append(rect(15, 15, 970, 470, fill="#fdfdfd", stroke="#d1d5db", sw=1.2, rx=8))
    frags.append(text(35, 42, "Послідовність аварійної евакуації регіону (Disaster Evacuation Protocol)", size=14, bold=True, color=INK, anchor="start"))

    # 5 фаз евакуації
    phases = [
        ("Фаза 1: Детекція", "Heartbeat Gate виявляє\nвтрату зв'язку з DC-1\n(3x 5s probe fails)", "#fee2e2", "#dc2626"),
        ("Фаза 2: Фенсинг", "Fencing Token revocation:\nблокування нових записів\nу пошкоджений DC-1", "#fef3c7", "#d97706"),
        ("Фаза 3: Перемикання", "Global Directory оновлює\nPrimary Region прапор:\nDC-1 -> DC-2", "#e0e7ff", "#4338ca"),
        ("Фаза 4: Read-Only", "DC-2 приймає трафік у R/O\nпоки доганяє асинхронні\nWAL логи реплікації", "#ecfdf5", "#047857"),
        ("Фаза 5: Full Active", "Підтвердження RPO=0 / RTO<30s.\nПовне відновлення запису\nу резервному DC-2", "#dbeafe", "#1d4ed8")
    ]

    x_start = 35
    w_box = 172
    gap = 21

    for i, (title, desc, bg, border) in enumerate(phases):
        x = x_start + i * (w_box + gap)
        frags.append(rect(x, 90, w_box, 360, fill=bg, stroke=border, sw=1.5, rx=6))
        frags.append(text(x + w_box/2, 120, title, size=11, bold=True, color=border))
        
        # Степи у фазі
        b_step, _, _ = textbox(x + w_box/2, 230, desc, size=9.5, pad=6, min_w=150, fill="#ffffff", stroke=border, sw=1.0)
        frags.append(b_step)

        if i < 4:
            frags.append(arrow(x + w_box + 2, 230, x + w_box + gap - 2, 230, color=border, sw=2.0))

    render(os.path.join(IMG, "region-failover-sequence.svg"), W, H, *frags)


def main():
    fig_dh_global_topology()
    fig_georouting_resolution_flow()
    fig_cross_region_replication_matrix()
    fig_region_failover_sequence()
    print("Всі 4 фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
