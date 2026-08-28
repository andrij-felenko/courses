# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def polygon(pts, fill=FILL, stroke=LINE, sw=1.5):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, stroke, sw)


# ── Figure 1: Three-tier rule execution hierarchy ──────────────────────────────

def fig_three_tier_hierarchy():
    W, H = 940, 520
    p = []

    # Title & canvas background
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Tiers layout
    tiers = [
        ("Хмарний бекенд (Cloud Backend)", 
         "Затримка: 100–1000+ мс  |  Надійність зв'язку: Best-effort (залежність від WAN)",
         "• Необмежені ресурси CPU/RAM/NVMe, довгострокові часові ряди (TimescaleDB, ClickHouse)\n• Глобальна міжоб'єктна аналітика, машинне навчання (ML), оптимізація за тарифами\n• Зручне версіонування бізнес-правил без втручання в локальну мережу",
         "#f0f4ff", "#3b82f6", 40),
        
        ("Локальний хаб / Шлюз (Local Gateway / Hub)", 
         "Затримка: 10–50 мс  |  Надійність зв'язку: LAN / Zigbee / Thread (працює без Інтернету)",
         "• Крос-девайсна автоматизація (Home Assistant, Edge IPC на Linux/OpenWrt)\n• Агрегація датчиків різних брендів, сценарне освітлення, кімнатний клімат-контроль\n• Локальна історія станів, розклади (cron, схід сонця), захист від падіння WAN",
         "#f0fdf4", "#16a34a", 195),
        
        ("Край / Мікроконтролер пристрою (Edge MCU)", 
         "Затримка: < 1 мс (жорсткий реал-тайм)  |  Надійність зв'язку: 100% автономність",
         "• Жорсткі інваріанти безпеки: захист від перегріву, сухий хід, струмовий захист, e-stop\n• Табличні автомати станів у статичній пам'яті (без malloc), нульовий джиттер (<10 мкс)\n• Пряме керування апаратними ключами, таймерами, АЦП, повна незалежність від мережі",
         "#fef2f2", "#dc2626", 350),
    ]

    for title, subtitle, bullets, fill_c, stroke_c, y in tiers:
        # Tier card
        p.append(rect(40, y, 620, 130, fill=fill_c, stroke=stroke_c, sw=1.8, rx=6))
        p.append(text(55, y + 24, title, size=14, color=stroke_c, anchor="start", bold=True))
        p.append(text(55, y + 44, subtitle, size=11, color=MUTED, anchor="start", italic=True))
        p.append(mtext(55, y + 68, bullets, size=11, color=INK, anchor="start", lh=1.35))

    # Right side: Data flow and contract indicators
    rx_box = 680
    
    # Downward arrow: Desired State & Leases
    p.append(rect(rx_box, 40, 220, 200, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=6))
    p.append(text(rx_box + 110, 65, "Потік завдань униз", size=12, color="#1e293b", bold=True))
    p.append(mtext(rx_box + 110, 88, "• Бажаний стан (Desired State)\n• Цільові уставки (Setpoints)\n• Оренда керування (Lease TTL)\n• Політики оптимізації", size=10.5, color=MUTED, lh=1.3))
    p.append(line(rx_box + 110, 155, rx_box + 110, 215, color="#2563eb", sw=2.5))
    p.append(polygon([(rx_box + 104, 210), (rx_box + 116, 210), (rx_box + 110, 223)], fill="#2563eb", stroke="#2563eb"))

    # Upward arrow: Reported State & Telemetry
    p.append(rect(rx_box, 270, 220, 210, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=6))
    p.append(text(rx_box + 110, 295, "Потік фактів угору", size=12, color="#1e293b", bold=True))
    p.append(mtext(rx_box + 110, 318, "• Фактичний стан (Reported)\n• Дані сенсорів і телеметрія\n• Аварійні спрацьовування\n• Підтвердження команд (ACK)", size=10.5, color=MUTED, lh=1.3))
    p.append(line(rx_box + 110, 455, rx_box + 110, 395, color="#16a34a", sw=2.5))
    p.append(polygon([(rx_box + 104, 400), (rx_box + 116, 400), (rx_box + 110, 387)], fill="#16a34a", stroke="#16a34a"))

    render(os.path.join(OUT, "three-tier-rule-hierarchy.svg"), W, H, *p,
           title="Трирівнева ієрархія виконання правил: Edge MCU, Local Hub та Cloud")


# ── Figure 2: Responsibility partitioning matrix ──────────────────────────────

def fig_responsibility_partitioning():
    W, H = 940, 480
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Header
    p.append(text(W / 2, 38, "Матриця розподілу відповідальності та піраміда довіри", size=15, color=INK, bold=True))
    p.append(text(W / 2, 58, "Вищий рівень пропонує мету, нижчий рівень забезпечує інваріанти безпеки", size=11, color=MUTED, italic=True))

    # 3 Layers representation
    layers = [
        ("Рівень 2: Глобальна оптимізація та аналітика (Cloud)",
         "Недетерміноване планування",
         "• Прогнозування теплової інерції будинку за погодою на 24 години\n• Оптимізація заряду батарей за погодинним тарифом електроенергії\n• Предиктивне виявлення зносу ТЕНів і підшипників насоса за трендами",
         "Втрата зв'язку: робота за останнім збереженим добовим графіком",
         "#eff6ff", "#3b82f6", 80),
        
        ("Рівень 1: Автоматизація комфорту та крос-девайси (Local Hub)",
         "М'який реальний час (10–50 мс)",
         "• Підтримання температури в кімнаті за розкладом і датчиками присутності\n• Узгодження роботи 5 кімнатних термостатів із загальним котлом/насосом\n• Сценарії «Ніч», «Нікого немає вдома», плавне підсвічування сходів",
         "Втрата зв'язку: перехід термостатів на локальні базові уставки (20 °C)",
         "#f0fdf4", "#16a34a", 205),
        
        ("Рівень 0: Критичні інваріанти безпеки (Edge MCU)",
         "Жорсткий реальний час (< 1 мс)",
         "• Захист від закипання котла: негайне знеструмлення при T > 85 °C\n• Захист від сухого ходу: вимкнення ТЕНа при падінні протоку < 1.5 л/хв\n• Апаратне блокування одночасного ввімкнення фаз реверсу моторів",
         "Абсолютний пріоритет: інваріант не може бути скасований зверху",
         "#fef2f2", "#dc2626", 330),
    ]

    for title, timing, desc, fault_behavior, fill_c, stroke_c, y in layers:
        p.append(rect(35, y, 870, 110, fill=fill_c, stroke=stroke_c, sw=1.8, rx=6))
        
        # Left badge
        p.append(text(50, y + 24, title, size=13, color=stroke_c, anchor="start", bold=True))
        p.append(text(50, y + 42, timing, size=10.5, color=MUTED, anchor="start", italic=True))
        
        # Middle bullets
        p.append(mtext(460, y + 24, desc, size=10.5, color=INK, anchor="start", lh=1.3))
        
        # Bottom fault note
        p.append(text(50, y + 94, fault_behavior, size=10.5, color=stroke_c if "Абсолютний" in fault_behavior else MUTED, anchor="start", bold=("Абсолютний" in fault_behavior)))

    render(os.path.join(OUT, "responsibility-partitioning-matrix.svg"), W, H, *p,
           title="Розподіл відповідальності між Edge, Local Hub та Cloud")


# ── Figure 3: Lease / Heartbeat Synchronization ────────────────────────────────

def fig_lease_heartbeat_sync():
    W, H = 940, 500
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Timelines
    x_hub = 220
    x_mcu = 700
    y_top = 70
    y_bot = 450

    # Actors
    p.append(rect(x_hub - 80, y_top - 35, 160, 30, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=4))
    p.append(text(x_hub, y_top - 15, "Local Hub (Python)", size=12, color="#16a34a", bold=True))
    
    p.append(rect(x_mcu - 80, y_top - 35, 160, 30, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=4))
    p.append(text(x_mcu, y_top - 15, "Edge MCU (C / C++)", size=12, color="#dc2626", bold=True))

    # Lifelines
    p.append(line(x_hub, y_top, x_hub, y_bot, color="#cbd5e1", sw=1.5, dash="4,4"))
    p.append(line(x_mcu, y_top, x_mcu, y_bot, color="#cbd5e1", sw=1.5, dash="4,4"))

    # Step 1: Normal command with Lease
    y1 = 100
    p.append(line(x_hub, y1, x_mcu, y1 + 20, color="#2563eb", sw=1.8))
    p.append(polygon([(x_mcu - 8, y1 + 14), (x_mcu - 8, y1 + 26), (x_mcu, y1 + 20)], fill="#2563eb", stroke="#2563eb"))
    p.append(text((x_hub + x_mcu) / 2, y1 + 6, "Target State: ON, Power: 2.5 kW, Lease TTL: 5000 ms", size=10.5, color="#1e40af", bold=True))

    y1_ack = 140
    p.append(line(x_mcu, y1_ack, x_hub, y1_ack + 20, color="#16a34a", sw=1.8))
    p.append(polygon([(x_hub + 8, y1_ack + 14), (x_hub + 8, y1_ack + 26), (x_hub, y1_ack + 20)], fill="#16a34a", stroke="#16a34a"))
    p.append(text((x_hub + x_mcu) / 2, y1_ack + 6, "ACK + Reported State (T_water=62°C, Flow=4.2 L/min, Relay=ON)", size=10.5, color="#166534"))

    # Step 2: Periodic Heartbeat renewing Lease
    y2 = 190
    p.append(line(x_hub, y2, x_mcu, y2 + 20, color="#2563eb", sw=1.8))
    p.append(polygon([(x_mcu - 8, y2 + 14), (x_mcu - 8, y2 + 26), (x_mcu, y2 + 20)], fill="#2563eb", stroke="#2563eb"))
    p.append(text((x_hub + x_mcu) / 2, y2 + 6, "Heartbeat / Renew Lease TTL: 5000 ms", size=10.5, color="#1e40af"))

    # Step 3: Network partition / Hub crash
    y_cut = 245
    p.append(rect(100, y_cut, 740, 26, fill="#fee2e2", stroke="#ef4444", sw=1, rx=4))
    p.append(text(W / 2, y_cut + 17, "ЗБІЙ ЗВ'ЯЗКУ: падіння Wi-Fi / зависання операційної системи Local Hub", size=11, color="#b91c1c", bold=True))

    # Step 4: MCU counts down and triggers Fallback
    y3 = 310
    p.append(rect(x_mcu + 15, y3 - 15, 200, 50, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=4))
    p.append(text(x_mcu + 115, y3 + 6, "Таймаут оренди сплив (5000 ms)", size=10.5, color="#dc2626", bold=True))
    p.append(text(x_mcu + 115, y3 + 24, "Перехід у FALLBACK_SAFE_MODE", size=10, color="#991b1b"))

    # Step 5: Safe state executed locally
    y4 = 380
    p.append(rect(x_mcu - 140, y4, 280, 45, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=4))
    p.append(text(x_mcu, y4 + 18, "Локальний інваріант: ТЕН = OFF", size=11, color="#b91c1c", bold=True))
    p.append(text(x_mcu, y4 + 34, "Помпа = ON (циркуляція для охолодження)", size=10, color="#7f1d1d"))

    render(os.path.join(OUT, "lease-heartbeat-sync.svg"), W, H, *p,
           title="Синхронізація станів за моделлю оренди керування (Lease TTL) та перехід у Failsafe")


if __name__ == "__main__":
    fig_three_tier_hierarchy()
    fig_responsibility_partitioning()
    fig_lease_heartbeat_sync()
    print("All figures generated successfully.")
