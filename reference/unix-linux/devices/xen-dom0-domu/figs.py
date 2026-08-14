import os
import sys

# Add scripts folder to sys.path (4 levels up from topic dir)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")

def generate_xen_arch():
    w, h = 860, 480
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    elements.append(text(w/2, 28, "Архітектура гіпервізора Xen: розділення доменів та рівні привілеїв", size=18, bold=True))
    
    # Dom0 Container (Left Box: x=40 to 360)
    elements.append(rect(40, 55, 320, 200, fill="#e8f4f8", stroke="#2980b9", sw=1.5, rx=8))
    elements.append(text(200, 78, "Domain 0 (Dom0 — привілейований)", size=13, bold=True, color="#1b4f72"))
    
    box_tools, _, _ = textbox(115, 130, "Toolstack\n(xl, xenstored)", size=10, pad=5, fill="#ffffff", stroke="#2980b9")
    box_backend, _, _ = textbox(285, 130, "Backend Drivers\n(blkback, netback)", size=10, pad=5, fill="#ffffff", stroke="#2980b9")
    box_dom0_kernel, _, _ = textbox(200, 205, "Ядро Linux Dom0 (Native Drivers)", size=11, pad=6, fill="#ffffff", stroke="#2980b9", bold=True)
    
    elements.append(box_tools)
    elements.append(box_backend)
    elements.append(box_dom0_kernel)
    
    # Inter-domain communication box (Middle Gap: x=360 to 500)
    box_inter, _, _ = textbox(430, 130, "I/O Ring &\nEvent Channel", size=10, pad=4, fill="#fdf2e9", stroke="#d35400", bold=True)
    elements.append(box_inter)
    
    # DomU Container (Right Box: x=500 to 820)
    elements.append(rect(500, 55, 320, 200, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=8))
    elements.append(text(660, 78, "Domain U (DomU — гостьова ОС)", size=13, bold=True, color="#145a32"))
    
    box_app, _, _ = textbox(575, 130, "User Apps\n(Ring 3)", size=10, pad=5, fill="#ffffff", stroke="#27ae60")
    box_frontend, _, _ = textbox(745, 130, "Frontend Drivers\n(blkfront, netfront)", size=10, pad=5, fill="#ffffff", stroke="#27ae60")
    box_domu_kernel, _, _ = textbox(660, 205, "Гостьове ядро ОС (PV / HVM / PVH)", size=11, pad=6, fill="#ffffff", stroke="#27ae60", bold=True)
    
    elements.append(box_app)
    elements.append(box_frontend)
    elements.append(box_domu_kernel)
    
    # Arrows between frontend/backend and inter-domain box in gap
    elements.append(arrow(500, 130, 480, 130, color="#d35400", sw=1.5))
    elements.append(arrow(380, 130, 360, 130, color="#d35400", sw=1.5))
    
    # Hypervisor Layer (Xen Microkernel - Ring -1)
    elements.append(rect(40, 280, 780, 100, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=8))
    elements.append(text(w/2, 303, "Гіпервізор Xen (Microkernel / Ring -1)", size=15, bold=True, color="#7e5109"))
    
    box_sched, _, _ = textbox(140, 345, "CPU Scheduler\n(Credit2)", size=11, pad=6, fill="#ffffff", stroke="#f39c12")
    box_mmu, _, _ = textbox(340, 345, "MMU & Grant Tables\n(P2M / M2P)", size=11, pad=6, fill="#ffffff", stroke="#f39c12")
    box_evt, _, _ = textbox(540, 345, "Event Channel\nController", size=11, pad=6, fill="#ffffff", stroke="#f39c12")
    box_hyp, _, _ = textbox(720, 345, "Hypercall Handler\n(VMCALL / Traps)", size=11, pad=6, fill="#ffffff", stroke="#f39c12")
    
    elements.append(box_sched)
    elements.append(box_mmu)
    elements.append(box_evt)
    elements.append(box_hyp)
    
    # Hypercalls / Upcalls arrows between Domains and Hypervisor
    elements.append(arrow(200, 240, 200, 280, color=LINE, sw=1.5))
    elements.append(text(140, 262, "sysctl/domctl", size=10, italic=True, color=MUTED))
    
    elements.append(arrow(660, 240, 660, 280, color=LINE, sw=1.5))
    elements.append(text(730, 262, "hypercall/upcall", size=10, italic=True, color=MUTED))
    
    # Hardware Layer
    elements.append(rect(40, 405, 780, 55, fill="#ebedef", stroke="#7f8c8d", sw=1.5, rx=6))
    elements.append(text(w/2, 438, "Фізичне обладнання (CPU, RAM, PCI Express, Network, Storage)", size=13, bold=True, color="#2c3e50"))
    
    elements.append(arrow(430, 380, 430, 405, color=LINE, sw=1.5))
    
    body = "".join(elements)
    
    os.makedirs(IMG_DIR, exist_ok=True)
    with open(os.path.join(IMG_DIR, "xen-arch.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">\n'
                f'<defs>\n'
                f'  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
                f'    <path d="M 0 1 L 10 5 L 0 9 z" fill="{LINE}"/>\n'
                f'  </marker>\n'
                f'</defs>\n'
                f'{body}\n</svg>')

def generate_xen_gnttab():
    w, h = 880, 450
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    elements.append(text(w/2, 28, "Механізм Grant Tables та Event Channels (Zero-Copy I/O)", size=18, bold=True))
    
    # DomU Box (Left)
    elements.append(rect(30, 60, 230, 350, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=8))
    elements.append(text(145, 85, "DomU (Frontend)", size=14, bold=True, color="#145a32"))
    
    box_domu_page, _, _ = textbox(145, 140, "Сторінка даних ОЗП\n(MFN X, PFN Y)", size=11, pad=6, fill="#ffffff", stroke="#27ae60")
    box_gref_issue, _, _ = textbox(145, 230, "Створення Grant Ref\n(gref 42, domid 0,\nGTF_permit_access)", size=10, pad=6, fill="#ffffff", stroke="#27ae60")
    box_evt_send, _, _ = textbox(145, 340, "Надсилання події\n(EVTCHNOP_send)", size=11, pad=6, fill="#ffffff", stroke="#27ae60")
    
    elements.append(box_domu_page)
    elements.append(box_gref_issue)
    elements.append(box_evt_send)
    
    # Hypervisor Grant Table (Middle)
    elements.append(rect(300, 60, 280, 350, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=8))
    elements.append(text(440, 85, "Гіпервізор Xen: Grant Table", size=14, bold=True, color="#7e5109"))
    
    box_entry, _, _ = textbox(440, 180, "Grant Entry #42:\n• domid: 0 (Dom0)\n• frame: MFN X\n• flags: GTF_permit_access", size=10, pad=8, fill="#ffffff", stroke="#f39c12", bold=True)
    box_evt_ctrl, _, _ = textbox(440, 340, "Event Channel Controller:\nВстановлення pending bit\nта віртуальний upcall", size=10, pad=6, fill="#ffffff", stroke="#f39c12")
    
    elements.append(box_entry)
    elements.append(box_evt_ctrl)
    
    # Dom0 Box (Right)
    elements.append(rect(620, 60, 230, 350, fill="#e8f4f8", stroke="#2980b9", sw=1.5, rx=8))
    elements.append(text(735, 85, "Dom0 (Backend)", size=14, bold=True, color="#1b4f72"))
    
    box_gnt_map, _, _ = textbox(735, 140, "GNTTABOP_map_grant_ref\n(Запит мапування gref 42)", size=10, pad=6, fill="#ffffff", stroke="#2980b9")
    box_dom0_mem, _, _ = textbox(735, 230, "Прямий доступ до\nMFN X (Zero-Copy)\nдля диска/мережі", size=10, pad=6, fill="#ffffff", stroke="#2980b9", bold=True)
    box_evt_recv, _, _ = textbox(735, 340, "Обробка Upcall IRQ\n(xen_evtchn_do_upcall)", size=10, pad=6, fill="#ffffff", stroke="#2980b9")
    
    elements.append(box_gnt_map)
    elements.append(box_dom0_mem)
    elements.append(box_evt_recv)
    
    # Arrows and labels
    elements.append(arrow(145, 170, 145, 195, color=LINE, sw=1.5))
    elements.append(arrow(220, 210, 310, 180, color=LINE, sw=1.5))
    elements.append(arrow(640, 140, 560, 170, color=LINE, sw=1.5))
    elements.append(arrow(560, 190, 640, 220, color="#27ae60", sw=2))
    elements.append(arrow(220, 340, 300, 340, color="#d35400", sw=2))
    elements.append(arrow(580, 340, 620, 340, color="#d35400", sw=2))
    
    body = "".join(elements)
    
    os.makedirs(IMG_DIR, exist_ok=True)
    with open(os.path.join(IMG_DIR, "xen-gnttab.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">\n'
                f'<defs>\n'
                f'  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
                f'    <path d="M 0 1 L 10 5 L 0 9 z" fill="{LINE}"/>\n'
                f'  </marker>\n'
                f'</defs>\n'
                f'{body}\n</svg>')

def render():
    generate_xen_arch()
    generate_xen_gnttab()

if __name__ == "__main__":
    render()
