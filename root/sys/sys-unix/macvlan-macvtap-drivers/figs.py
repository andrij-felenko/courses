import sys
import os

# Add scripts dir (4 levels up from topic dir: reference/unix-linux/networking/macvlan-macvtap-drivers)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_figures():
    topic_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(topic_dir, "img")
    os.makedirs(img_dir, exist_ok=True)

    # 1. macvlan-vs-bridge.svg
    w1, h1 = 850, 420
    
    c1 = rect(30, 50, 380, 340, fill="#f8f9fa", stroke="#495057", sw=1.5, rx=8)
    t1 = text(220, 75, "Традиційний Linux Bridge", size=15, bold=True, color=INK)
    
    b_nic = textbox(220, 340, "Фізичний NIC (eth0)", size=12, fill="#e9ecef", stroke=LINE)[0]
    b_bridge = textbox(220, 240, "Linux Bridge (br0)\n[FDB Lookup + Netfilter hooks]", size=12, fill="#ffe3e3", stroke="#c0392b")[0]
    b_c1 = textbox(130, 130, "Контейнер 1\n(veth0)", size=12, fill="#e7f5ff", stroke="#1971c2")[0]
    b_c2 = textbox(310, 130, "Контейнер 2\n(veth1)", size=12, fill="#e7f5ff", stroke="#1971c2")[0]
    
    a1 = arrow(220, 315, 220, 275)
    a2 = arrow(180, 205, 130, 160)
    a3 = arrow(260, 205, 310, 160)

    c2 = rect(440, 50, 380, 340, fill="#f8f9fa", stroke="#495057", sw=1.5, rx=8)
    t2 = text(630, 75, "Архітектура Macvlan", size=15, bold=True, color=INK)
    
    m_nic = textbox(630, 340, "Фізичний NIC (eth0)\n[rx_handler: macvlan_handle_frame]", size=12, fill="#e9ecef", stroke=LINE)[0]
    m_demux = textbox(630, 240, "Демультиплексор Macvlan\n[Пряме зіставлення MAC]", size=12, fill="#d3f9d8", stroke="#2b8a3e")[0]
    m_c1 = textbox(540, 130, "Контейнер 1\nmacvlan0 (MAC A)", size=12, fill="#e7f5ff", stroke="#1971c2")[0]
    m_c2 = textbox(720, 130, "Контейнер 2\nmacvlan1 (MAC B)", size=12, fill="#e7f5ff", stroke="#1971c2")[0]

    ma1 = arrow(630, 315, 630, 275)
    ma2 = arrow(590, 205, 540, 160)
    ma3 = arrow(670, 205, 720, 160)

    p1 = os.path.join(img_dir, "macvlan-vs-bridge.svg")
    render(p1, w1, h1, c1, t1, b_nic, b_bridge, b_c1, b_c2, a1, a2, a3,
           c2, t2, m_nic, m_demux, m_c1, m_c2, ma1, ma2, ma3,
           title="Порівняння обробки пакетів: Linux Bridge та Macvlan")

    # 2. macvlan-modes.svg
    w2, h2 = 900, 460
    
    mb1 = rect(30, 60, 400, 175, fill="#f1f3f5", stroke="#495057", sw=1.5, rx=6)
    mt1 = text(230, 85, "1. Режим Bridge (прямий L2 комутатор)", size=14, bold=True, color="#2b8a3e")
    e1_a = textbox(110, 150, "macvlan0\n(MAC A)", size=11, fill="#e7f5ff", stroke="#1971c2")[0]
    e1_b = textbox(350, 150, "macvlan1\n(MAC B)", size=11, fill="#e7f5ff", stroke="#1971c2")[0]
    arr_br = arrow(165, 150, 295, 150, color="#2b8a3e", sw=2)
    txt_br = text(230, 135, "Внутрішній обмін L2", size=10, color="#2b8a3e")

    mb2 = rect(470, 60, 400, 175, fill="#f1f3f5", stroke="#495057", sw=1.5, rx=6)
    mt2 = text(670, 85, "2. Режим VEPA (IEEE 802.1Qbg)", size=14, bold=True, color="#e67e22")
    e2_a = textbox(550, 170, "macvlan0", size=11, fill="#e7f5ff", stroke="#1971c2")[0]
    e2_b = textbox(790, 170, "macvlan1", size=11, fill="#e7f5ff", stroke="#1971c2")[0]
    sw_box = textbox(670, 110, "Зовнішній Switch\n[Hairpin / Reflective Relay]", size=10, fill="#fff3bf", stroke="#f59f00")[0]
    arr_v1 = arrow(580, 150, 620, 125, color="#e67e22")
    arr_v2 = arrow(720, 125, 760, 150, color="#e67e22")

    mb3 = rect(30, 255, 400, 175, fill="#f1f3f5", stroke="#495057", sw=1.5, rx=6)
    mt3 = text(230, 280, "3. Режим Private (Повна ізоляція)", size=14, bold=True, color="#c0392b")
    e3_a = textbox(110, 345, "macvlan0", size=11, fill="#e7f5ff", stroke="#1971c2")[0]
    e3_b = textbox(350, 345, "macvlan1", size=11, fill="#e7f5ff", stroke="#1971c2")[0]
    drop_box = textbox(230, 345, "DROP\n(блоковано)", size=11, fill="#ffe3e3", stroke="#c0392b")[0]
    arr_p1 = arrow(165, 345, 185, 345, color="#c0392b")
    arr_p2 = arrow(275, 345, 295, 345, color="#c0392b")

    mb4 = rect(470, 255, 400, 175, fill="#f1f3f5", stroke="#495057", sw=1.5, rx=6)
    mt4 = text(670, 280, "4. Режим Passthrough (Ексклюзивний)", size=14, bold=True, color="#1971c2")
    e4_a = textbox(670, 335, "macvlan0\n(1:1 до eth0 / SR-IOV VF)", size=11, fill="#d0ebff", stroke="#1971c2")[0]
    e4_nic = textbox(670, 395, "Фізичний NIC / VF", size=11, fill="#e9ecef", stroke=LINE)[0]
    arr_pass = arrow(670, 375, 670, 360, color="#1971c2")

    p2 = os.path.join(img_dir, "macvlan-modes.svg")
    render(p2, w2, h2, mb1, mt1, e1_a, e1_b, arr_br, txt_br,
           mb2, mt2, e2_a, e2_b, sw_box, arr_v1, arr_v2,
           mb3, mt3, e3_a, e3_b, drop_box, arr_p1, arr_p2,
           mb4, mt4, e4_a, e4_nic, arr_pass,
           title="Режими роботи драйвера Macvlan")

    # 3. macvtap-arch.svg
    w3, h3 = 850, 400
    
    us_bg = rect(30, 50, 790, 140, fill="#f8f9fa", stroke="#ced4da", sw=1, rx=6)
    us_lbl = text(80, 75, "User Space", size=13, bold=True, color="#495057")
    qemu_box = textbox(425, 120, "Процес QEMU / KVM\n[Гостьова ОС / virtio-net драйвер]", size=12, fill="#e7f5ff", stroke="#1971c2")[0]

    b_line = line(30, 200, 820, 200, color="#adb5bd", sw=2, dash="6 4")
    b_lbl = text(120, 215, "Межа ядра (Kernel Boundary)", size=10, italic=True, color="#6c757d")

    ks_bg = rect(30, 230, 790, 140, fill="#f1f3f5", stroke="#ced4da", sw=1, rx=6)
    ks_lbl = text(85, 255, "Kernel Space", size=13, bold=True, color="#495057")
    
    dev_tap = textbox(250, 300, "Символьний пристрій\n/dev/tapX (chrdev)", size=12, fill="#fff3bf", stroke="#f59f00")[0]
    macvtap_drv = textbox(470, 300, "Драйвер Macvtap\n(macvlan core)", size=12, fill="#d3f9d8", stroke="#2b8a3e")[0]
    phys_nic = textbox(690, 300, "Фізичний NIC\n(eth0)", size=12, fill="#e9ecef", stroke=LINE)[0]

    arr_fd = arrow(375, 155, 280, 275, color="#f59f00", sw=2)
    txt_fd = text(310, 210, "read()/write() FD", size=10, color="#f59f00", bold=True)
    
    arr_tap_drv = arrow(325, 300, 400, 300, color="#2b8a3e", sw=2)
    arr_drv_nic = arrow(540, 300, 625, 300, color="#2b8a3e", sw=2)

    p3 = os.path.join(img_dir, "macvtap-arch.svg")
    render(p3, w3, h3, us_bg, us_lbl, qemu_box, b_line, b_lbl, ks_bg, ks_lbl,
           dev_tap, macvtap_drv, phys_nic, arr_fd, txt_fd, arr_tap_drv, arr_drv_nic,
           title="Архітектура Macvtap: прямоточний зв'язок QEMU із мережевою картою")

    print("Figures rendered successfully.")

if __name__ == '__main__':
    build_figures()
