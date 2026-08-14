# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_netlink_architecture():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'netlink-architecture.svg')

    w, h = 820, 480
    frags = []

    # Title
    frags.append(text(w / 2, 26, "Архітектура підсистеми Netlink у ядрі Linux", size=18, bold=True, color=INK))

    # User Space Box
    frags.append(rect(20, 45, 780, 150, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(40, 65, "Простір користувача (User Space)", size=14, bold=True, color=MUTED, anchor="start"))

    # User processes
    b1 = fitbox(40, 80, 230, 95, "iproute2 / NetworkManager\n[AF_NETLINK, NETLINK_ROUTE]\nPID / nl_pid = 1024", size=13, fill="#e0f2fe", stroke="#0284c7")
    b2 = fitbox(295, 80, 230, 95, "udevd (Device Manager)\n[AF_NETLINK, UEVENT]\nGroup: 1 (uevent)", size=13, fill="#fef3c7", stroke="#d97706")
    b3 = fitbox(550, 80, 230, 95, "nftables / hostapd\n[NETLINK_NETFILTER / GENERIC]\nGeneric Family Resolve", size=13, fill="#f3e8ff", stroke="#7e22ce")
    frags.extend([b1, b2, b3])

    # System Call Boundary
    frags.append(line(20, 215, 220, 215, color="#ef4444", sw=2, dash="6,4"))
    frags.append(fitbox(410, 203, 360, 24, "Межа системних викликів (socket / bind / sendmsg)", size=11, fill="#ffffff", stroke="#ef4444", color="#ef4444", bold=True))
    frags.append(line(600, 215, 800, 215, color="#ef4444", sw=2, dash="6,4"))

    # Kernel Space Box
    frags.append(rect(20, 245, 780, 220, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(40, 265, "Простір ядра (Kernel Space)", size=14, bold=True, color=INK, anchor="start"))

    # Netlink Core
    b_core = fitbox(40, 280, 740, 50, "Ядро Netlink (netlink_kernel_create / netlink_unicast / netlink_broadcast)\nЧерги sk_buff · Таблиця портів nl_pid · Мультикаст-групи", size=13, fill="#dcfce7", stroke="#15803d", bold=True)
    frags.append(b_core)

    # Kernel Subsystems
    k1 = fitbox(40, 360, 175, 75, "NETLINK_ROUTE\n(rtnetlink)\nМаршрути, IP, dev", size=12, fill="#ffffff", stroke=LINE)
    k2 = fitbox(230, 360, 175, 75, "NETLINK_KOBJECT\n(uevent)\nПодії пристроїв", size=12, fill="#ffffff", stroke=LINE)
    k3 = fitbox(420, 360, 175, 75, "NETLINK_NETFILTER\n(nftables)\nПравила ФС", size=12, fill="#ffffff", stroke=LINE)
    k4 = fitbox(610, 360, 170, 75, "NETLINK_GENERIC\n(genl / nl80211)\nДинамічні сімейства", size=12, fill="#ffffff", stroke=LINE)
    frags.extend([k1, k2, k3, k4])

    # Inter-layer Arrows
    frags.append(arrow(155, 175, 155, 280, color="#0284c7", sw=2))
    frags.append(arrow(410, 175, 410, 280, color="#d97706", sw=2))
    frags.append(arrow(665, 175, 665, 280, color="#7e22ce", sw=2))

    # Core to Subsystem arrows
    frags.append(arrow(127, 330, 127, 360, color=LINE, sw=1.5))
    frags.append(arrow(317, 330, 317, 360, color=LINE, sw=1.5))
    frags.append(arrow(507, 330, 507, 360, color=LINE, sw=1.5))
    frags.append(arrow(695, 330, 695, 360, color=LINE, sw=1.5))

    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")

def generate_netlink_frame_structure():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    out_path = os.path.join(img_dir, 'netlink-frame-structure.svg')

    w, h = 840, 460
    frags = []

    frags.append(text(w / 2, 26, "Структура двійкового пакета Netlink та TLV-атрибутів", size=18, bold=True, color=INK))

    # Outer Frame Box
    frags.append(rect(20, 50, 800, 390, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(40, 70, "Дійтаграма Netlink (Загальна довжина = nlmsg_len, вирівнювання 4 байти)", size=13, bold=True, color=MUTED, anchor="start"))

    # Section 1: Standard Netlink Header (nlmsghdr)
    h_box = rect(40, 85, 760, 95, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=6)
    frags.append(h_box)
    frags.append(text(60, 103, "Заголовок повідомлення: struct nlmsghdr (16 байтів)", size=13, bold=True, color="#1e40af", anchor="start"))

    # 4 fields breakdown
    f1 = fitbox(55, 117, 170, 50, "nlmsg_len (32 біти)\nПовна довжина пакета", size=11, fill="#ffffff", stroke="#93c5fd")
    f2 = fitbox(238, 117, 170, 50, "nlmsg_type (16 бітів)\nТип (RTM_*, NLMSG_*)", size=11, fill="#ffffff", stroke="#93c5fd")
    f3 = fitbox(421, 117, 170, 50, "nlmsg_flags (16 бітів)\nREQUEST / DUMP / ACK", size=11, fill="#ffffff", stroke="#93c5fd")
    f4_corr = fitbox(604, 117, 180, 50, "nlmsg_seq (32b) / nlmsg_pid\nSeq num та Port ID", size=11, fill="#ffffff", stroke="#93c5fd")
    frags.extend([f1, f2, f3, f4_corr])

    # Section 2: Subsystem Header (Payload prefix)
    p_box = rect(40, 190, 760, 65, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6)
    frags.append(p_box)
    frags.append(text(60, 208, "Специфічний заголовок підсистеми (наприклад, struct ifinfomsg для rtnetlink / struct genlmsghdr)", size=12, bold=True, color="#15803d", anchor="start"))
    p_fields = fitbox(55, 217, 730, 30, "ifi_family (8b) | ifi_type (16b) | ifi_index (32b) | ifi_flags (32b) | ifi_change (32b)", size=11, fill="#ffffff", stroke="#86efac")
    frags.append(p_fields)

    # Section 3: TLV Attributes (nlattr / rtattr)
    t_box = rect(40, 265, 760, 160, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=6)
    frags.append(t_box)
    frags.append(text(60, 283, "Послідовність TLV-атрибутів (Type-Length-Value: struct nlattr / struct rtattr)", size=13, bold=True, color="#c2410c", anchor="start"))

    # TLV 1
    tlv1 = rect(55, 295, 350, 115, fill="#ffffff", stroke="#fdba74", sw=1.2, rx=4)
    frags.append(tlv1)
    frags.append(text(65, 313, "Атрибут 1: IFLA_IFNAME", size=12, bold=True, color="#c2410c", anchor="start"))
    t1_h = fitbox(65, 323, 330, 35, "nla_len (16b) = 9 | nla_type (16b) = IFLA_IFNAME", size=10, fill="#ffedd5", stroke="#f97316")
    t1_d = fitbox(65, 363, 330, 35, "Дані: \"eth0\\0\" (5 байтів) + 3 байти вирівнювання (Pad)", size=10, fill="#fef2f2", stroke="#fca5a5")
    frags.extend([t1_h, t1_d])

    # TLV 2 (Nested)
    tlv2 = rect(425, 295, 360, 115, fill="#ffffff", stroke="#fdba74", sw=1.2, rx=4)
    frags.append(tlv2)
    frags.append(text(435, 313, "Атрибут 2: IFLA_LINKINFO (NLA_F_NESTED)", size=12, bold=True, color="#c2410c", anchor="start"))
    t2_h = fitbox(435, 323, 340, 35, "nla_len (16b) | nla_type = IFLA_LINKINFO | NLA_F_NESTED", size=10, fill="#ffedd5", stroke="#f97316")
    t2_d = fitbox(435, 363, 340, 35, "Вкладені атрибути: IFLA_INFO_KIND -> \"vlan\"", size=10, fill="#f0fdf4", stroke="#86efac")
    frags.extend([t2_h, t2_d])

    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")

def generate_netlink_multipart_stream():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    out_path = os.path.join(img_dir, 'netlink-multipart-stream.svg')

    w, h = 820, 440
    frags = []

    frags.append(text(w / 2, 26, "Потік повідомлень дампа (NLM_F_DUMP) та асинхронного мультикасту", size=18, bold=True, color=INK))

    # Columns: User Space Process (Left) vs Kernel Netlink Core (Right)
    frags.append(rect(20, 50, 240, 370, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(140, 72, "Простір користувача", size=14, bold=True, color=INK))

    frags.append(rect(560, 50, 240, 370, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(680, 72, "Ядро Linux (Netlink)", size=14, bold=True, color=INK))

    # Flow arrows and message boxes
    # Step 1: Send Request DUMP
    frags.append(arrow(260, 110, 560, 110, color="#0284c7", sw=2))
    frags.append(fitbox(280, 95, 260, 30, "1. sendmsg(): RTM_GETLINK [DUMP]", size=11, fill="#e0f2fe", stroke="#0284c7"))

    # Step 2: Kernel response part 1
    frags.append(arrow(560, 160, 260, 160, color="#16a34a", sw=2))
    frags.append(fitbox(280, 145, 260, 30, "2. recvmsg(): RTM_NEWLINK (eth0)", size=11, fill="#dcfce7", stroke="#16a34a"))

    # Step 3: Kernel response part 2
    frags.append(arrow(560, 210, 260, 210, color="#16a34a", sw=2))
    frags.append(fitbox(280, 195, 260, 30, "3. recvmsg(): RTM_NEWLINK (wlan0)", size=11, fill="#dcfce7", stroke="#16a34a"))

    # Step 4: Kernel response DONE
    frags.append(arrow(560, 260, 260, 260, color="#2563eb", sw=2))
    frags.append(fitbox(280, 245, 260, 30, "4. recvmsg(): NLMSG_DONE", size=11, fill="#dbeafe", stroke="#2563eb"))

    # Step 5: Async Multicast Event (Kernel push)
    frags.append(line(20, 310, 800, 310, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(410, 303, "Асинхронний мультикаст-канал (RTMGRP_LINK)", size=11, bold=True, color=MUTED))

    frags.append(arrow(560, 355, 260, 355, color="#d97706", sw=2))
    frags.append(fitbox(280, 340, 260, 30, "5. Мультикаст: RTM_NEWLINK (Link UP)", size=11, fill="#fef3c7", stroke="#d97706"))

    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_netlink_architecture()
    generate_netlink_frame_structure()
    generate_netlink_multipart_stream()
