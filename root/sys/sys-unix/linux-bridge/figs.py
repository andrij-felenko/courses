# -*- coding: utf-8 -*-
import sys
import os

# Add scripts dir (4 levels up from reference/unix-linux/networking/linux-bridge)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_figures():
    topic_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(topic_dir, "img")
    os.makedirs(img_dir, exist_ok=True)

    # ─────────────────────────────────────────────────────────────────────────
    # 1. bridge-architecture.svg (920x540)
    # Архітектура підсистеми Linux Bridge у ядрі
    # ─────────────────────────────────────────────────────────────────────────
    w1, h1 = 920, 540

    # User Space container
    c_user = rect(30, 20, 860, 85, fill="#f8f9fa", stroke="#adb5bd", sw=1.5, rx=8)
    t_user = text(460, 42, "Простір користувача (User Space / Контейнери / ВМ)", size=13, bold=True, color="#495057")
    b_vm = textbox(160, 75, "KVM / QEMU (ВМ)\n[/dev/net/tun fd]", size=10.5, fill="#e7f5ff", stroke="#1971c2")[0]
    b_ct1 = textbox(460, 75, "Контейнер (netns)\n[eth0 (veth peer)]", size=10.5, fill="#e7f5ff", stroke="#1971c2")[0]
    b_ctl = textbox(760, 75, "Керування (iproute2)\n[bridge / ip link / mstpd]", size=10.5, fill="#fff3bf", stroke="#f59f00")[0]

    # Ports layer in kernel
    b_p1 = textbox(160, 160, "net_bridge_port\n(tap0)", size=10.5, fill="#d0ebff", stroke="#1971c2")[0]
    b_p2 = textbox(460, 160, "net_bridge_port\n(veth0)", size=10.5, fill="#d0ebff", stroke="#1971c2")[0]
    b_p3 = textbox(760, 160, "net_bridge_port\n(eth0 port)", size=10.5, fill="#d0ebff", stroke="#1971c2")[0]

    # Kernel Bridge Core
    c_br = rect(30, 220, 860, 200, fill="#eef2f7", stroke="#2c3e50", sw=1.5, rx=8)
    t_br = text(460, 245, "Програмний комутатор ядра: net_bridge (br0)", size=13, bold=True, color="#2c3e50")

    b_fdb = textbox(170, 305, "Таблиця FDB (Forwarding DB)\n[MAC + VID -> Port / Local]\n[Aging Timer: 300 s]", size=10, fill="#ffffff", stroke="#2980b9")[0]
    b_vlan = textbox(460, 305, "VLAN Filtering Engine\n[PVID, Ingress/Egress Filter]\n[IEEE 802.1Q Tag Handling]", size=10, fill="#ffffff", stroke="#27ae60")[0]
    b_stp = textbox(750, 305, "STP / RSTP State Machine\n[Blocking/Learning/Forwarding]\n[BPDU Processing & Snooping]", size=10, fill="#ffffff", stroke="#d35400")[0]

    b_nf = textbox(460, 380, "Підсистема фільтрації: ebtables / nftables bridge (опційно br_netfilter)", size=10.5, fill="#fff5f5", stroke="#e03131")[0]

    # Physical NIC / Switchdev hardware
    b_hw = textbox(760, 485, "Фізичний мережевий адаптер (PHY / MAC / Switchdev ASIC)", size=10.5, fill="#e9ecef", stroke="#495057")[0]

    # Arrows
    a_vm = arrow(160, 95, 160, 135, color="#1971c2", sw=1.5)
    a_ct = arrow(460, 95, 460, 135, color="#1971c2", sw=1.5)
    a_ctl = arrow(760, 95, 760, 135, color="#f59f00", sw=1.5)

    a_p1_br = arrow(160, 185, 160, 220, color="#2c3e50", sw=1.5)
    a_p2_br = arrow(460, 185, 460, 220, color="#2c3e50", sw=1.5)
    a_p3_br = arrow(760, 185, 760, 220, color="#2c3e50", sw=1.5)

    a_hw = arrow(760, 420, 760, 460, color="#495057", sw=1.5)

    p1 = os.path.join(img_dir, "bridge-architecture.svg")
    render(p1, w1, h1,
           c_user, t_user, b_vm, b_ct1, b_ctl,
           b_p1, b_p2, b_p3,
           c_br, t_br, b_fdb, b_vlan, b_stp, b_nf,
           b_hw,
           a_vm, a_ct, a_ctl, a_p1_br, a_p2_br, a_p3_br, a_hw,
           title="Архітектура підсистеми Linux Bridge у ядрі")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. bridge-rx-forwarding.svg (940x520)
    # Алгоритм обробки та комутації вхідного кадру (RX Path)
    # ─────────────────────────────────────────────────────────────────────────
    w2, h2 = 940, 520

    b_rx_in = textbox(470, 35, "Вхідний Ethernet-кадр (sk_buff)\n[Драйвер NIC / netif_receive_skb() -> rx_handler]", size=11, fill="#e7f5ff", stroke="#1971c2")[0]

    b_stp_chk = textbox(470, 105, "Перевірка стану порту STP (br_handle_frame)\n[Порт у стані DISABLED чи BLOCKING?]", size=11, fill="#fff3bf", stroke="#f59f00")[0]

    b_drop = textbox(130, 105, "Скидання кадру\n(Drop skb)", size=11, fill="#ffe3e3", stroke="#c0392b")[0]
    
    b_learn = textbox(470, 175, "MAC Learning: оновлення FDB (br_fdb_update)\n[Запис {Src MAC, VID} -> Вхідний порт, скидання Aging timer]", size=10.5, fill="#d3f9d8", stroke="#2b8a3e")[0]

    b_fdb_look = textbox(470, 250, "Пошук адреси призначення (br_fdb_find_rcu)\n[Аналіз Dst MAC та VLAN Filtering]", size=11, fill="#f1f3f5", stroke="#343a40")[0]

    # Three branches
    b_local = textbox(170, 345, "Гілка 1: Локальний стек\n(Dst MAC = MAC моста)\n[br_pass_frame_up()]\n-> L3 IP Stack хоста", size=10.5, fill="#e7f5ff", stroke="#1971c2")[0]

    b_ucast = textbox(470, 345, "Гілка 2: Відомий Unicast\n(Dst MAC знайдено в FDB)\n[br_forward() -> Вихідний порт]\n-> dev_queue_xmit()", size=10.5, fill="#d3f9d8", stroke="#2b8a3e")[0]

    b_flood = textbox(770, 345, "Гілка 3: Flooding\n(Broadcast / Невідомий Unicast)\n[br_flood()]\n-> Реплікація на всі порти крім вхідного", size=10.5, fill="#fff3bf", stroke="#d35400")[0]

    # Netfilter egress / xmit
    b_xmit = textbox(470, 460, "Вихідний інтерфейс призначення (Egress port queue / Switchdev offload)", size=11, fill="#e9ecef", stroke="#495057")[0]

    # Connectors
    a_r1 = arrow(470, 58, 470, 83)
    a_drop = arrow(300, 105, 185, 105, color="#c0392b")
    a_r2 = arrow(470, 127, 470, 153)
    a_r3 = arrow(470, 197, 470, 228)

    a_b1 = arrow(360, 265, 230, 310, color="#1971c2")
    a_b2 = arrow(470, 272, 470, 310, color="#2b8a3e")
    a_b3 = arrow(580, 265, 710, 310, color="#d35400")

    a_out2 = arrow(470, 385, 470, 440, color="#2b8a3e")
    a_out3 = arrow(770, 385, 590, 445, color="#d35400")

    p2 = os.path.join(img_dir, "bridge-rx-forwarding.svg")
    render(p2, w2, h2,
           b_rx_in, b_stp_chk, b_drop, b_learn, b_fdb_look,
           b_local, b_ucast, b_flood, b_xmit,
           a_r1, a_drop, a_r2, a_r3, a_b1, a_b2, a_b3, a_out2, a_out3,
           title="Алгоритм комутації та маршрут кадру в Linux Bridge (RX Path)")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. bridge-vlan-filtering.svg (920x460)
    # Механізм VLAN Filtering (PVID, Tagged, Untagged)
    # ─────────────────────────────────────────────────────────────────────────
    w3, h3 = 920, 460

    c_box = rect(30, 30, 860, 400, fill="#f8f9fa", stroke="#495057", sw=1.5, rx=8)
    t_vtitle = text(460, 58, "Комутація з фільтрацією VLAN (VLAN-Aware Linux Bridge)", size=14, bold=True, color=INK)

    # Ingress port (Access Port, PVID=10)
    b_acc_in = textbox(170, 130, "Access Порт 1 (eth1)\n[PVID: 10, Untagged]\nВхід: Нетегований кадр", size=10.5, fill="#e7f5ff", stroke="#1971c2")[0]

    b_pvid_act = textbox(170, 220, "Присвоєння внутрішнього VID:\nВхідний кадр класифікується як VLAN 10", size=10, fill="#d0ebff", stroke="#1971c2")[0]

    # Core Bridge FDB
    b_vlan_fdb = textbox(460, 220, "Таблиця FDB моста (VLAN-Aware)\n[MAC A, VID 10 -> Port 1]\n[MAC B, VID 10 -> Port 2]\n[MAC C, VID 20 -> Port 3]\nІзоляція: VID 10 не бачить VID 20!", size=11, fill="#ffffff", stroke="#2b8a3e")[0]

    # Egress Port 2 (Access Port VID=10)
    b_acc_out = textbox(750, 130, "Access Порт 2 (eth2)\n[VID: 10, Egress Untagged]\nВихід: Зняття тегу 802.1Q", size=10.5, fill="#d3f9d8", stroke="#2b8a3e")[0]

    # Egress Port 3 (Trunk Port VID=10, 20)
    b_trunk_out = textbox(750, 320, "Trunk Порт 3 (eth3)\n[VID: 10, 20 Tagged]\nВихід: Кадр із заголовком 802.1Q VID=10", size=10.5, fill="#fff3bf", stroke="#f59f00")[0]

    # Connectors
    a_v1 = arrow(170, 165, 170, 195, color="#1971c2")
    a_v2 = arrow(275, 220, 335, 220, color="#1971c2")
    
    a_v3 = arrow(585, 200, 645, 150, color="#2b8a3e")
    a_v4 = arrow(585, 240, 645, 300, color="#f59f00")

    p3 = os.path.join(img_dir, "bridge-vlan-filtering.svg")
    render(p3, w3, h3,
           c_box, t_vtitle,
           b_acc_in, b_pvid_act, b_vlan_fdb, b_acc_out, b_trunk_out,
           a_v1, a_v2, a_v3, a_v4,
           title="Робота VLAN Filtering: обробка PVID, Tagged та Untagged портів")

    # ─────────────────────────────────────────────────────────────────────────
    # 4. bridge-netfilter-flow.svg (920x460)
    # Перетин L2 Bridge та L3 Netfilter (br_netfilter)
    # ─────────────────────────────────────────────────────────────────────────
    w4, h4 = 920, 460

    c_nf_box = rect(30, 30, 860, 400, fill="#fdfdfe", stroke="#495057", sw=1.5, rx=8)
    t_nf_title = text(460, 58, "Шлях транзитного L2-кадру через підсистему Netfilter (br_netfilter)", size=14, bold=True, color=INK)

    b_nf_rx = textbox(150, 140, "Вхідний кадр на порті\n(NF_BR_PRE_ROUTING)", size=11, fill="#e7f5ff", stroke="#1971c2")[0]

    b_br_nf = textbox(460, 140, "Модуль br_netfilter (L2->L3 Bridge-NF)\n[net.bridge.bridge-nf-call-iptables = 1]\nВиклик L3 iptables PREROUTING над L2 кадром", size=10.5, fill="#fff5f5", stroke="#e03131")[0]

    b_fdb_dec = textbox(770, 140, "Рішення про комутацію\n(FDB lookup / br_forward)", size=11, fill="#ffffff", stroke="#2c3e50")[0]

    b_nf_fwd = textbox(770, 280, "L3 iptables FORWARD\n[Перевірка правил між L2-портами]\n(NF_BR_FORWARD)", size=10.5, fill="#fff5f5", stroke="#e03131")[0]

    b_nf_post = textbox(460, 280, "L3 iptables POSTROUTING\n[NF_BR_POST_ROUTING]", size=10.5, fill="#fff5f5", stroke="#e03131")[0]

    b_nf_tx = textbox(150, 280, "Вихідний порт (Egress)\n[dev_queue_xmit()]", size=11, fill="#d3f9d8", stroke="#2b8a3e")[0]

    b_warn = textbox(460, 380, "Застереження: перехоплення L2-трафіку модулем br_netfilter може спотворювати L3 NAT та ламати CNI", size=10, fill="#fff3bf", stroke="#f59f00")[0]

    # Arrows
    a_n1 = arrow(230, 140, 310, 140)
    a_n2 = arrow(610, 140, 680, 140)
    a_n3 = arrow(770, 175, 770, 245)
    a_n4 = arrow(680, 280, 550, 280)
    a_n5 = arrow(370, 280, 225, 280)

    p4 = os.path.join(img_dir, "bridge-netfilter-flow.svg")
    render(p4, w4, h4,
           c_nf_box, t_nf_title,
           b_nf_rx, b_br_nf, b_fdb_dec, b_nf_fwd, b_nf_post, b_nf_tx, b_warn,
           a_n1, a_n2, a_n3, a_n4, a_n5,
           title="Взаємодія Linux Bridge та Netfilter через br_netfilter")

if __name__ == "__main__":
    build_figures()
