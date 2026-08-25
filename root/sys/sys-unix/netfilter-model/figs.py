# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/ directory from reference/unix-linux/networking/netfilter-model
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

def generate_netfilter_hooks():
    w, h = 1160, 520
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Шлях пакета крізь 5 хуків Netfilter, маршрутизацію та таблиці", size=16, bold=True))

    # Ingress Network (x=75, y=200)
    b_ing, _, _ = textbox(75, 200, "Мережа\n(Ingress)", size=12, pad=10, fill="#e8f4f8", stroke="#2980b9", bold=True)
    frags.append(b_ing)

    # PREROUTING Hook box (x=260, y=200)
    b_pre, _, _ = textbox(260, 200, "1. PREROUTING\nraw → conntrack → mangle → nat (DNAT)", size=11, pad=10, fill="#fef9e7", stroke="#f39c12", bold=True)
    frags.append(b_pre)
    frags.append(arrow(135, 200, 155, 200))

    # Inbound Routing Decision (x=480, y=200)
    b_rt_in, _, _ = textbox(480, 200, "Рішення про маршрутизацію\n(Локальний / Транзит?)", size=10, pad=10, fill="#f39c12", stroke="#d35400", color="#ffffff", bold=True)
    frags.append(b_rt_in)
    frags.append(arrow(365, 200, 385, 200))

    # INPUT Hook box (Upper path: x=480, y=80)
    b_in, _, _ = textbox(480, 80, "2. INPUT\nmangle → filter → security → nat", size=11, pad=10, fill="#eafaf1", stroke="#27ae60", bold=True)
    frags.append(b_in)
    frags.append(arrow(480, 155, 480, 115))

    # Local Process (x=800, y=80)
    b_proc, _, _ = textbox(800, 80, "Сокет / Локальний процес\n(Прийом / Генерація пакетів)", size=11, pad=10, fill="#ebf5fb", stroke="#2980b9", bold=True)
    frags.append(b_proc)
    frags.append(arrow(585, 80, 680, 80))

    # FORWARD Hook box (Middle path: x=800, y=200)
    b_fwd, _, _ = textbox(800, 200, "3. FORWARD\nmangle → filter → security", size=11, pad=10, fill="#fef9e7", stroke="#d35400", bold=True)
    frags.append(b_fwd)
    frags.append(arrow(575, 200, 700, 200))

    # OUTPUT Hook box (x=480, y=340)
    b_out, _, _ = textbox(480, 340, "4. OUTPUT\nraw → conntrack → mangle → nat → filter → security", size=11, pad=10, fill="#fdedec", stroke="#c0392b", bold=True)
    frags.append(b_out)
    
    # Arrow from Local Process down to OUTPUT via clean gap at x=640
    frags.append(line(800, 125, 640, 125))
    frags.append(line(640, 125, 640, 340))
    frags.append(arrow(640, 340, 625, 340))

    # Outbound Routing Decision (x=480, y=450)
    b_rt_out, _, _ = textbox(480, 450, "Перевірка маршруту\n(після можливого DNAT в OUTPUT)", size=10, pad=10, fill="#eaafc8", stroke="#8e44ad", bold=True)
    frags.append(b_rt_out)
    frags.append(arrow(480, 375, 480, 420))

    # POSTROUTING Hook box (x=1000, y=290)
    b_post, _, _ = textbox(1000, 290, "5. POSTROUTING\nmangle → nat (SNAT / MASQ)", size=11, pad=10, fill="#fef9e7", stroke="#f39c12", bold=True)
    frags.append(b_post)

    # FORWARD to POSTROUTING
    frags.append(arrow(900, 200, 1000, 250))
    # Outbound Routing to POSTROUTING
    frags.append(arrow(600, 450, 1000, 330))

    # Egress Network (x=1000, y=450)
    b_egr, _, _ = textbox(1000, 450, "Мережа\n(Egress)", size=12, pad=10, fill="#e8f4f8", stroke="#2980b9", bold=True)
    frags.append(b_egr)
    frags.append(arrow(1000, 330, 1000, 415))

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, "netfilter-hooks.svg"), w, h, *frags)

def generate_conntrack_state_machine():
    w, h = 880, 440
    frags = []

    frags.append(text(w / 2, 28, "Автомат станів з'єднань у підсистемі nf_conntrack", size=16, bold=True))

    # Entry point
    frags.append(text(60, 140, "Пакет з мережі", size=11, color=MUTED))
    frags.append(arrow(110, 140, 150, 140))

    # NEW State
    b_new, _, _ = textbox(250, 140, "NEW\nПерший бачений пакет\nЗапис у ct_hash", size=11, pad=12, fill="#e8f8f5", stroke="#1abc9c", bold=True)
    frags.append(b_new)

    # ESTABLISHED State
    b_est, _, _ = textbox(570, 140, "ESTABLISHED\nЗворотна відповідь отримана\n(Inverted Tuple)", size=11, pad=12, fill="#ebf5fb", stroke="#3498db", bold=True)
    frags.append(b_est)
    frags.append(arrow(340, 140, 465, 140))
    frags.append(text(400, 125, "Зворотний пакет", size=10, color=LINE))

    # UNTRACKED State
    b_untracked, _, _ = textbox(770, 290, "UNTRACKED\nПравило NOTRACK у raw\nОбхід conntrack", size=11, pad=12, fill="#f2f4f4", stroke="#7f8c8d", bold=True)
    frags.append(b_untracked)

    # Arrow to UNTRACKED from Entry
    frags.append(line(60, 160, 60, 390))
    frags.append(line(60, 390, 770, 390))
    frags.append(arrow(770, 390, 770, 340))
    frags.append(text(410, 375, "Правило NOTRACK у таблиці raw", size=10, color=POS))

    # RELATED State
    b_rel, _, _ = textbox(570, 290, "RELATED\nАсоційоване з'єднання\n(ICMP Error / FTP Data)", size=11, pad=12, fill="#f4ecf7", stroke="#8e44ad", bold=True)
    frags.append(b_rel)
    frags.append(arrow(570, 200, 570, 230))

    # INVALID State
    b_inv, _, _ = textbox(250, 290, "INVALID\nХибні прапорці TCP / поза вікном\nDROP правила", size=11, pad=12, fill="#fdedec", stroke="#e74c3c", bold=True)
    frags.append(b_inv)
    frags.append(arrow(250, 200, 250, 230))

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, "conntrack-state-machine.svg"), w, h, *frags)

if __name__ == "__main__":
    generate_netfilter_hooks()
    generate_conntrack_state_machine()
    print("Figures generated successfully.")
