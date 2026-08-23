# -*- coding: utf-8 -*-
"""Фігури до теми «Капстон, крок 3: сервісні межі, обчислювальні платформи та топологія вузлів».
Запуск: python figs.py  → створює SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ───────── Фіг. 1: Топологія вузлів та сервісні межі PayFlow ─────────
def fig_service_boundaries_topology():
    W, H = 940, 480
    f = [text(W / 2, 28, "Декомпозиція PayFlow: Від доменних контекстів до топології обчислювальних вузлів", size=16, bold=True)]

    # 1. API Edge Layer
    f.append(rect(30, 50, 880, 70, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=6))
    f.append(text(45, 72, "API Edge & Gateway Layer", size=12, bold=True, color="#1b4f72", anchor="start"))
    f.append(text(45, 88, "Stateless Node Pool (TLS termination, Rate Limiting, WAF, OAuth2 Validation)", size=10, color=MUTED, anchor="start"))

    f.append(rect(520, 62, 170, 44, fill="#ffffff", stroke="#2980b9", sw=1.2, rx=4))
    f.append(text(605, 81, "Edge Router Node 1", size=10, bold=True, color=INK))
    f.append(text(605, 95, "Envoy / NGINX", size=9, color=MUTED))

    f.append(rect(710, 62, 170, 44, fill="#ffffff", stroke="#2980b9", sw=1.2, rx=4))
    f.append(text(795, 81, "Edge Router Node 2", size=10, bold=True, color=INK))
    f.append(text(795, 95, "Envoy / NGINX", size=9, color=MUTED))

    # Connectors Edge -> Services
    f.append(arrow(220, 120, 220, 155, color="#2980b9", sw=1.5))
    f.append(arrow(470, 120, 470, 155, color="#2980b9", sw=1.5))
    f.append(arrow(720, 120, 720, 155, color="#2980b9", sw=1.5))

    # 2. Core Compute Boundary (Payment Workers & Ledger)
    # Payment Core
    f.append(rect(30, 160, 380, 180, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=6))
    f.append(text(45, 182, "Payment Core Cluster (Sync Worker Nodes)", size=12, bold=True, color="#7e5109", anchor="start"))
    f.append(text(45, 198, "High-Throughput Stateful/Stateless Execution", size=10, color=MUTED, anchor="start"))

    f.append(rect(45, 215, 165, 55, fill="#ffffff", stroke="#f39c12", sw=1.0, rx=4))
    f.append(text(127, 235, "Authorize Service", size=10, bold=True, color=INK))
    f.append(text(127, 252, "gRPC / C++ Core", size=9, color=MUTED))

    f.append(rect(225, 215, 165, 55, fill="#ffffff", stroke="#f39c12", sw=1.0, rx=4))
    f.append(text(307, 235, "Saga Orchestrator", size=10, bold=True, color=INK))
    f.append(text(307, 252, "Go / State Machine", size=9, color=MUTED))

    f.append(rect(45, 280, 345, 45, fill="#fff8e7", stroke="#d68910", sw=1.0, rx=4))
    f.append(text(217, 298, "Ephemeral Redis Cache & Lock Pool", size=10, bold=True, color="#7e5109"))
    f.append(text(217, 313, "Idempotency keys, Hot balances", size=9, color=MUTED))

    # Ledger Dedicated Node
    f.append(rect(430, 160, 240, 180, fill="#fadbd8", stroke="#e74c3c", sw=1.5, rx=6))
    f.append(text(445, 182, "Ledger Financial Node", size=12, bold=True, color="#78281f", anchor="start"))
    f.append(text(445, 198, "Strict ACID & Double-Entry", size=10, color=MUTED, anchor="start"))

    f.append(rect(445, 215, 210, 55, fill="#ffffff", stroke="#e74c3c", sw=1.0, rx=4))
    f.append(text(550, 235, "Ledger Engine API", size=10, bold=True, color=INK))
    f.append(text(550, 252, "gRPC Strict Isolation", size=9, color=MUTED))

    f.append(rect(445, 280, 210, 45, fill="#fdf2f2", stroke="#c0392b", sw=1.0, rx=4))
    f.append(text(550, 298, "PostgreSQL Dedicated DB", size=10, bold=True, color="#78281f"))
    f.append(text(550, 313, "Append-only Ledger Entries", size=9, color=MUTED))

    # Async Outbox & Webhook Node
    f.append(rect(690, 160, 220, 180, fill="#e8f8f5", stroke="#16a085", sw=1.5, rx=6))
    f.append(text(705, 182, "Webhook & Outbox Pool", size=12, bold=True, color="#0e6251", anchor="start"))
    f.append(text(705, 198, "Event Fan-out & Retries", size=10, color=MUTED, anchor="start"))

    f.append(rect(705, 215, 190, 55, fill="#ffffff", stroke="#16a085", sw=1.0, rx=4))
    f.append(text(800, 235, "Outbox Processor", size=10, bold=True, color=INK))
    f.append(text(800, 252, "Kafka Consumer / Go", size=9, color=MUTED))

    f.append(rect(705, 280, 190, 45, fill="#e8f8f5", stroke="#117864", sw=1.0, rx=4))
    f.append(text(800, 298, "Webhook Dispatcher", size=10, bold=True, color="#0e6251"))
    f.append(text(800, 313, "Backoff & Signer Node", size=9, color=MUTED))

    # Internal Bus / gRPC arrows
    f.append(arrow(410, 242, 445, 242, color="#e74c3c", sw=1.8))
    f.append(text(427, 232, "gRPC", size=9, bold=True, color="#c0392b"))

    f.append(arrow(655, 242, 705, 242, color="#16a085", sw=1.8))
    f.append(text(680, 232, "Events", size=9, bold=True, color="#117864"))

    # 3. Platform Identity & Tenancy Services (Bottom Layer)
    f.append(rect(30, 360, 880, 90, fill="#f4ecf7", stroke="#8e44ad", sw=1.5, rx=6))
    f.append(text(45, 382, "Platform Supporting Services (Tenancy, Identity, Time/Cron)", size=12, bold=True, color="#4a235a", anchor="start"))

    f.append(rect(60, 395, 240, 42, fill="#ffffff", stroke="#8e44ad", sw=1.0, rx=4))
    f.append(text(180, 412, "Identity Node (AuthN/AuthZ)", size=10, bold=True, color=INK))
    f.append(text(180, 426, "OAuth2 / JWT Scope Validator", size=9, color=MUTED))

    f.append(rect(350, 395, 240, 42, fill="#ffffff", stroke="#8e44ad", sw=1.0, rx=4))
    f.append(text(470, 412, "Tenant & Billing Engine", size=10, bold=True, color=INK))
    f.append(text(470, 426, "Tier limits, Metering & Entitlements", size=9, color=MUTED))

    f.append(rect(640, 395, 240, 42, fill="#ffffff", stroke="#8e44ad", sw=1.0, rx=4))
    f.append(text(760, 412, "Time & Distributed Scheduler", size=10, bold=True, color=INK))
    f.append(text(760, 426, "Temporal / Recurring Cron", size=9, color=MUTED))

    render(os.path.join(IMG, "service-boundaries-topology.svg"), W, H, *f)


# ───────── Фіг. 2: Послідовність Saga та Transactional Outbox ─────────
def fig_saga_outbox_flow():
    W, H = 920, 440
    f = [text(W / 2, 28, "Розподілена Saga та Transactional Outbox при обробці платежу PayFlow", size=16, bold=True)]

    # Columns
    cols = [
        {"x": 70, "name": "Клієнт (Merchant)"},
        {"x": 230, "name": "API Gateway"},
        {"x": 400, "name": "Saga Orchestrator"},
        {"x": 570, "name": "Ledger Node"},
        {"x": 730, "name": "Outbox & Broker"},
        {"x": 860, "name": "Webhook Worker"}
    ]

    for c in cols:
        f.append(line(c["x"], 60, c["x"], 390, color="#bdc3c7", sw=1.0, dash="4,4"))
        f.append(rect(c["x"] - 55, 50, 110, 28, fill="#2c3e50", stroke="none", rx=4))
        f.append(text(c["x"], 68, c["name"], size=9.5, bold=True, color="#ffffff"))

    # Sequence steps
    # 1. POST /v1/charges
    f.append(arrow(70, 100, 230, 100, color="#2980b9", sw=1.5))
    f.append(text(150, 93, "1. POST /v1/charges", size=9, bold=True, color="#1b4f72"))

    # 2. Check auth & Route
    f.append(arrow(230, 130, 400, 130, color="#2980b9", sw=1.5))
    f.append(text(315, 123, "2. Execute Charge Saga", size=9, color=INK))

    # 3. Reserve & Write Ledger
    f.append(arrow(400, 160, 570, 160, color="#c0392b", sw=1.5))
    f.append(text(485, 153, "3. gRPC: RecordTransaction()", size=9, bold=True, color="#78281f"))

    # 4. DB Transaction: Ledger Entry + Outbox Row
    f.append(rect(520, 185, 100, 40, fill="#fadbd8", stroke="#e74c3c", sw=1.0, rx=3))
    f.append(text(570, 199, "BEGIN ACID TX", size=9, bold=True, color="#78281f"))
    f.append(text(570, 214, "+ Insert Outbox", size=9, color=MUTED))

    # 5. Ack to Orchestrator
    f.append(line(570, 245, 400, 245, color="#27ae60", sw=1.5, dash="3,3"))
    f.append(text(485, 238, "4. TX Committed OK", size=9, color="#1e8449"))

    # 6. Response to Merchant
    f.append(line(400, 275, 70, 275, color="#27ae60", sw=1.5, dash="3,3"))
    f.append(text(235, 268, "5. 201 Created (charge_id, status=pending)", size=9, bold=True, color="#1e8449"))

    # Async Outbox Polling & Webhook Async Flow
    f.append(line(50, 305, 870, 305, color="#e67e22", sw=1.0, dash="2,2"))
    f.append(text(460, 300, "Асинхронний контур сповіщень (Outbox & Webhooks)", size=9, bold=True, color="#d35400"))

    # 7. CDC / Poller reads Outbox
    f.append(arrow(570, 335, 730, 335, color="#e67e22", sw=1.5))
    f.append(text(650, 328, "6. Read Outbox Event", size=9, color="#d35400"))

    # 8. Publish to Broker -> Webhook Worker
    f.append(arrow(730, 365, 860, 365, color="#16a085", sw=1.5))
    f.append(text(795, 358, "7. Kafka: charge.succeeded", size=9, color="#0e6251"))

    # 9. Deliver Webhook
    f.append(arrow(860, 395, 70, 395, color="#8e44ad", sw=1.5))
    f.append(text(465, 388, "8. POST Merchant Webhook URL (signed HMAC-SHA256)", size=9, bold=True, color="#4a235a"))

    render(os.path.join(IMG, "saga-outbox-flow.svg"), W, H, *f)


# ───────── Фіг. 3: Архітектурна взаємодія 5 критичних вузлів ─────────
def fig_critical_nodes_architecture():
    W, H = 940, 440
    f = [text(W / 2, 28, "Взаємодія п'яти критичних обчислювальних вузлів платформи PayFlow", size=16, bold=True)]

    # Central Core Node
    cx, cy = 470, 230
    f.append(rect(cx - 110, cy - 50, 220, 100, fill="#fef9e7", stroke="#f39c12", sw=2.0, rx=8))
    f.append(text(cx, cy - 25, "1. Payment Core Node", size=12, bold=True, color="#7e5109"))
    f.append(text(cx, cy - 8, "Saga & Transaction Flow", size=10, color=INK))
    f.append(text(cx, cy + 12, "Idempotency & State Machine", size=9, color=MUTED))
    f.append(text(cx, cy + 28, "Orchestration & Validation", size=9, color=MUTED, italic=True))

    # Top-Left: Identity Node
    ix, iy = 150, 100
    f.append(rect(ix - 100, iy - 40, 200, 80, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=6))
    f.append(text(ix, iy - 18, "2. Identity & Access Node", size=11, bold=True, color="#1b4f72"))
    f.append(text(ix, iy + 2, "OAuth2 Token Validation", size=9.5, color=INK))
    f.append(text(ix, iy + 20, "mTLS / Scope Checker", size=9, color=MUTED))

    # Top-Left arrow & text: line from (ix+100, iy) = (250, 100) to (cx-110, cy-20) = (360, 210)
    f.append(arrow(250, 110, 360, 195, color="#2980b9", sw=1.5))
    f.append(text(275, 135, "Verify JWT & Scopes", size=9, color="#1b4f72", bold=True))

    # Top-Right: Ledger Node
    lx, ly = 790, 100
    f.append(rect(lx - 100, ly - 40, 200, 80, fill="#fadbd8", stroke="#e74c3c", sw=1.5, rx=6))
    f.append(text(lx, ly - 18, "3. Money & Ledger Node", size=11, bold=True, color="#78281f"))
    f.append(text(lx, ly + 2, "Double-Entry Accounting", size=9.5, color=INK))
    f.append(text(lx, ly + 20, "ACID Invariants & Reconcile", size=9, color=MUTED))

    # Top-Right arrow & text: line from (cx+110, cy-20) = (580, 210) to (lx-100, ly+10) = (690, 110)
    f.append(arrow(580, 195, 690, 110, color="#e74c3c", sw=1.5))
    f.append(text(665, 135, "gRPC Strict ACID Write", size=9, color="#78281f", bold=True))

    # Bottom-Left: Tenancy & Metering Node
    tx, ty = 150, 360
    f.append(rect(tx - 100, ty - 40, 200, 80, fill="#f4ecf7", stroke="#8e44ad", sw=1.5, rx=6))
    f.append(text(tx, ty - 18, "4. Tenancy & Billing Node", size=11, bold=True, color="#4a235a"))
    f.append(text(tx, ty + 2, "Quota & Rate Enforcement", size=9.5, color=INK))
    f.append(text(tx, ty + 20, "Usage Metering & Tier Limits", size=9, color=MUTED))

    # Bottom-Left arrow & text: line from (cx-110, cy+20) = (360, 250) to (tx+100, ty-10) = (250, 350)
    f.append(arrow(360, 250, 250, 335, color="#8e44ad", sw=1.5))
    f.append(text(325, 315, "Check Limits & Metering", size=9, color="#4a235a", bold=True))

    # Bottom-Right: Webhook & Outbox Node
    wx, wy = 790, 360
    f.append(rect(wx - 100, wy - 40, 200, 80, fill="#e8f8f5", stroke="#16a085", sw=1.5, rx=6))
    f.append(text(wx, wy - 18, "5. Webhook Dispatcher Node", size=11, bold=True, color="#0e6251"))
    f.append(text(wx, wy + 2, "Outbox Consumer & Retry", size=9.5, color=INK))
    f.append(text(wx, wy + 20, "HMAC Signer & Fan-Out", size=9, color=MUTED))

    # Bottom-Right arrow & text: line from (cx+110, cy+20) = (580, 250) to (wx-100, wy-10) = (690, 350)
    f.append(arrow(580, 250, 690, 335, color="#16a085", sw=1.5))
    f.append(text(615, 315, "Outbox Event Stream", size=9, color="#0e6251", bold=True))

    # Auxiliary Time Node (Center Top)
    f.append(rect(cx - 90, 50, 180, 45, fill="#fcf3cf", stroke="#f1c40f", sw=1.2, rx=4))
    f.append(text(cx, 67, "Time & Scheduler Node", size=10, bold=True, color="#7d6608"))
    f.append(text(cx, 82, "Monotonic Clocks & Temporal Cron", size=9, color=MUTED))

    f.append(arrow(cx, 95, cx, cy - 50, color="#f1c40f", sw=1.2))

    render(os.path.join(IMG, "critical-nodes-architecture.svg"), W, H, *f)


if __name__ == "__main__":
    fig_service_boundaries_topology()
    fig_saga_outbox_flow()
    fig_critical_nodes_architecture()
    print("Всі фігури успішно згенеровано у ./img/")
