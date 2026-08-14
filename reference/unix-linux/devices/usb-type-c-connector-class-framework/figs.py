import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
try:
    from svgkit import *
except ImportError:
    print("WARNING: svgkit not found")
    sys.exit(1)

def draw_architecture():
    w, h = 900, 480
    frags = []

    # Title / Boundary Box: Hardware Layer
    frags.append(rect(20, 20, 860, 90, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(40, 45, "Апаратний рівень (Hardware & Physical Layer)", size=14, bold=True, anchor="start", color=INK))
    
    b_phy, w_phy, _ = textbox(150, 75, "Type-C PHY / CC Lines\n(CC1, CC2, VCONN)", size=12, fill="#e2e8f0", bold=True)
    frags.append(b_phy)
    
    b_switch, w_switch, _ = textbox(400, 75, "Type-C Switch & Mux\n(Orientation & DP/USB3)", size=12, fill="#e2e8f0", bold=True)
    frags.append(b_switch)

    b_chip, w_chip, _ = textbox(700, 75, "TCPCI / EC Controller\n(I2C / ACPI UCSI)", size=12, fill="#e2e8f0", bold=True)
    frags.append(b_chip)

    # Driver & Subsystem Layer
    frags.append(rect(20, 130, 860, 190, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(40, 155, "Ядерні драйвери та фреймворк (Kernel Subsystem & Drivers)", size=14, bold=True, anchor="start", color=INK))

    b_tcpci, w_tcpci, _ = textbox(150, 205, "TCPCI / UCSI Driver\n(drivers/usb/typec/tcpm/)", size=12, fill="#dbeafe", bold=True)
    frags.append(b_tcpci)

    b_tcpm, w_tcpm, _ = textbox(420, 205, "TCPM (Port Manager)\n& PD State Machine", size=12, fill="#bfdbfe", bold=True)
    frags.append(b_tcpm)

    b_core, w_core, _ = textbox(700, 205, "Type-C Class Core\n(drivers/usb/typec/core.c)", size=12, fill="#93c5fd", bold=True)
    frags.append(b_core)

    b_muxdev, w_muxdev, _ = textbox(250, 280, "Type-C Switch / Mux / Retimer\n(drivers/usb/typec/mux.c)", size=12, fill="#dbeafe", bold=True)
    frags.append(b_muxdev)

    b_role, w_role, _ = textbox(600, 280, "USB Role Switch Framework\n(drivers/usb/roles/)", size=12, fill="#dbeafe", bold=True)
    frags.append(b_role)

    # Upper Subsystems & Userspace
    frags.append(rect(20, 340, 860, 120, fill="#ffffff", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(40, 365, "Суміжні підсистеми та простір користувача (Subsystems & Userspace)", size=14, bold=True, anchor="start", color=INK))

    b_sysfs, w_sysfs, _ = textbox(160, 410, "Sysfs Interface\n/sys/class/typec/\n/sys/class/usb_power_delivery/", size=11, fill="#fef3c7", bold=True)
    frags.append(b_sysfs)

    b_usbcore, w_usbcore, _ = textbox(400, 410, "USB Host / Gadget Core\n(xHCI / UDC Driver)", size=11, fill="#e0e7ff", bold=True)
    frags.append(b_usbcore)

    b_drm, w_drm, _ = textbox(620, 410, "DRM DisplayPort AltMode\n(dp_altmode driver)", size=11, fill="#e0e7ff", bold=True)
    frags.append(b_drm)

    b_psy, w_psy, _ = textbox(790, 410, "Power Supply Class\n(Charger / Psy)", size=11, fill="#e0e7ff", bold=True)
    frags.append(b_psy)

    # Arrows
    frags.append(arrow(150, 95, 150, 185))
    frags.append(arrow(700, 95, 700, 185))
    frags.append(arrow(220, 205, 350, 205))
    frags.append(arrow(490, 205, 630, 205))
    frags.append(arrow(700, 230, 700, 385))
    frags.append(arrow(420, 230, 250, 260))
    frags.append(arrow(420, 230, 600, 260))
    frags.append(arrow(600, 305, 400, 385))
    frags.append(arrow(250, 305, 620, 385))
    frags.append(arrow(700, 230, 160, 385))
    frags.append(arrow(700, 230, 790, 385))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "typec-architecture.svg"), w, h, *frags, title="Архітектура фреймворку USB Type-C у Linux")

def draw_sysfs_hierarchy():
    w, h = 880, 420
    frags = []

    # Root nodes
    b_root1, w_r1, _ = textbox(250, 40, "/sys/class/typec/", size=13, fill="#dbeafe", bold=True)
    frags.append(b_root1)

    b_root2, w_r2, _ = textbox(650, 40, "/sys/class/usb_power_delivery/", size=13, fill="#fef3c7", bold=True)
    frags.append(b_root2)

    # Type-C level 1
    b_p0, w_p0, _ = textbox(140, 120, "port0\n(struct typec_port)", size=12, fill="#eff6ff", bold=True)
    frags.append(b_p0)

    b_p1, w_p1, _ = textbox(360, 120, "port1\n(struct typec_port)", size=12, fill="#eff6ff", bold=True)
    frags.append(b_p1)

    # Type-C level 2 under port0
    b_attr, w_attr, _ = textbox(80, 230, "Attributes:\ndata_role\npower_role\nvconn_role\nport_type", size=10, fill="#ffffff")
    frags.append(b_attr)

    b_partner, w_part, _ = textbox(210, 230, "port0-partner\n(struct typec_partner)\nidentity / SVIDs", size=11, fill="#e0e7ff", bold=True)
    frags.append(b_partner)

    b_cable, w_cable, _ = textbox(360, 230, "port0-cable\n(struct typec_cable)\nplug / e-Marker", size=11, fill="#e0e7ff", bold=True)
    frags.append(b_cable)

    # Altmode child under partner
    b_alt, w_alt, _ = textbox(210, 340, "port0-partner.0\n(struct typec_altmode)\nsvid: 0014 (DP)", size=10, fill="#f1f5f9", bold=True)
    frags.append(b_alt)

    # PD hierarchy under usb_power_delivery
    b_pd0, w_pd0, _ = textbox(650, 120, "pd0 (USB PD Device)", size=12, fill="#fffbeb", bold=True)
    frags.append(b_pd0)

    b_src, w_src, _ = textbox(570, 230, "source-capabilities/\n1:fixed (5V/3A)\n2:fixed (9V/3A)\n3:fixed (20V/3.25A)", size=10, fill="#ffffff")
    frags.append(b_src)

    b_snk, w_snk, _ = textbox(730, 230, "sink-capabilities/\n1:fixed (5V/3A)\n2:pps (3.3V-11V/3A)", size=10, fill="#ffffff")
    frags.append(b_snk)

    # Connections
    frags.append(arrow(250, 60, 140, 100))
    frags.append(arrow(250, 60, 360, 100))
    
    frags.append(arrow(140, 140, 80, 205))
    frags.append(arrow(140, 140, 210, 205))
    frags.append(arrow(140, 140, 360, 205))

    frags.append(arrow(210, 255, 210, 320))

    frags.append(arrow(650, 60, 650, 100))
    frags.append(arrow(650, 140, 570, 205))
    frags.append(arrow(650, 140, 730, 205))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "sysfs-hierarchy.svg"), w, h, *frags, title="Ієрархія файлових об'єктів sysfs для Type-C та Power Delivery")

def draw_pd_negotiation():
    w, h = 860, 440
    frags = []

    # Vertical lifelines
    frags.append(line(160, 60, 160, 400, color="#94a3b8", sw=1.5, dash="4 4"))
    frags.append(line(430, 60, 430, 400, color="#94a3b8", sw=1.5, dash="4 4"))
    frags.append(line(700, 60, 700, 400, color="#94a3b8", sw=1.5, dash="4 4"))

    # Lifeline Headers
    bx1, _, _ = textbox(160, 40, "Джерело живлення\n(Source / Power Adapter)", size=12, fill="#dbeafe", bold=True)
    frags.append(bx1)
    bx2, _, _ = textbox(430, 40, "Лінія CC (BMC)\n/ TCPM Драйвер", size=12, fill="#e2e8f0", bold=True)
    frags.append(bx2)
    bx3, _, _ = textbox(700, 40, "Споживач живлення\n(Sink / Linux Host)", size=12, fill="#fef3c7", bold=True)
    frags.append(bx3)

    # Timeline events & messages
    # 1. Attachment & VBUS Default 5V
    frags.append(arrow(160, 100, 700, 100, color="#2563eb", sw=1.8))
    frags.append(text(430, 90, "Фізичне підключення + VBUS Default (5V vSafe5V)", size=11, color="#1e40af", bold=True))

    # 2. Source Capabilities PDOs
    frags.append(arrow(160, 160, 700, 160, color="#059669", sw=1.8))
    frags.append(text(430, 150, "Source_Capabilities (PDO: 5V/3A, 9V/3A, 20V/3.25A 65W)", size=11, color="#065f46", bold=True))

    # 3. Request RDO
    frags.append(arrow(700, 220, 160, 220, color="#d97706", sw=1.8))
    frags.append(text(430, 210, "Request (RDO: Вибір 20V / 3.25A 65W Profile)", size=11, color="#92400e", bold=True))

    # 4. Accept
    frags.append(arrow(160, 280, 700, 280, color="#059669", sw=1.8))
    frags.append(text(430, 270, "Accept (Підтвердження джерела)", size=11, color="#065f46", bold=True))

    # 5. Power transition & PS_RDY
    frags.append(rect(100, 310, 120, 35, fill="#fee2e2", stroke="#ef4444", sw=1, rx=4))
    frags.append(text(160, 327, "Переключення VBUS на 20V", size=10, color="#991b1b", bold=True))

    frags.append(arrow(160, 370, 700, 370, color="#2563eb", sw=1.8))
    frags.append(text(430, 360, "PS_RDY (Power Supply Ready — 20V підведено)", size=11, color="#1e40af", bold=True))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "pd-negotiation-flow.svg"), w, h, *frags, title="Протокол узгодження Power Delivery (BMC повідомлення)")

def draw_mux_routing():
    w, h = 880, 380
    frags = []

    # Connector & Orientation Switch
    b_conn, w_conn, _ = textbox(120, 190, "Роз'єм Type-C\n(24-Pin Receptacle)", size=12, fill="#e2e8f0", bold=True)
    frags.append(b_conn)

    b_sw, w_sw, _ = textbox(320, 190, "Orientation Switch\n(typec_switch)\nПеревертання CC1/CC2", size=11, fill="#dbeafe", bold=True)
    frags.append(b_sw)

    # Multiplexer & Retimer
    b_ret, w_ret, _ = textbox(520, 190, "Signal Retimer\n(typec_retimer)\nКомпенсація втрат", size=11, fill="#e0e7ff", bold=True)
    frags.append(b_ret)

    b_mux, w_mux, _ = textbox(720, 190, "Crossbar Mux\n(typec_mux)\nРозподіл сигналів", size=11, fill="#fef3c7", bold=True)
    frags.append(b_mux)

    # End targets
    b_usb, w_usb, _ = textbox(720, 70, "xHCI USB 3.2 Host Controller\n(2x SuperSpeed Lanes)", size=11, fill="#dcfce7", bold=True)
    frags.append(b_usb)

    b_dp, w_dp, _ = textbox(720, 310, "DRM DisplayPort PHY\n(4x/2x DP Lanes)", size=11, fill="#dcfce7", bold=True)
    frags.append(b_dp)

    # Role Switch for USB 2.0
    b_usb2, w_u2, _ = textbox(320, 70, "USB Role Switch\n(struct usb_role_switch)\nD+/D- to Host/UDC", size=11, fill="#f3e8ff", bold=True)
    frags.append(b_usb2)

    # Arrows
    frags.append(arrow(120, 150, 320, 95))
    frags.append(arrow(120, 190, 320, 190))
    frags.append(arrow(320, 190, 520, 190))
    frags.append(arrow(520, 190, 720, 190))

    frags.append(arrow(720, 160, 720, 100))
    frags.append(arrow(720, 220, 720, 285))
    frags.append(arrow(320, 70, 720, 70))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "mux-retimer-switch-path.svg"), w, h, *frags, title="Фізична та логічна коммутація сигналів Type-C Switch, Mux та Retimer")

if __name__ == "__main__":
    draw_architecture()
    draw_sysfs_hierarchy()
    draw_pd_negotiation()
    draw_mux_routing()
    print("All SVG figures generated successfully.")
