import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def render():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. ACPI Tables Hierarchy
    frags1 = []
    # Title is added by render if specified
    
    # RSDP
    frags1.append(svgkit.fitbox(240, 50, 220, 50, "RSDP\n(Root System Description Pointer)", size=13, bold=True, fill="#e8f4fc", stroke="#2457d6"))
    frags1.append(svgkit.arrow(350, 100, 350, 130, color="#2457d6"))
    
    # RSDT / XSDT
    frags1.append(svgkit.fitbox(240, 130, 220, 50, "RSDT / XSDT\n(Root / Extended Description Table)", size=13, bold=True, fill="#e8f4fc", stroke="#2457d6"))
    
    # Arrows to static tables
    frags1.append(svgkit.arrow(270, 180, 110, 230, color="#333333"))
    frags1.append(svgkit.arrow(320, 180, 260, 230, color="#333333"))
    frags1.append(svgkit.arrow(380, 180, 420, 230, color="#333333"))
    frags1.append(svgkit.arrow(430, 180, 580, 230, color="#333333"))
    
    # Static tables
    frags1.append(svgkit.fitbox(40, 230, 140, 50, "FADT\n(Fixed ACPI Desc)", size=12, bold=True, fill="#eafaf1", stroke="#27ae60"))
    frags1.append(svgkit.fitbox(195, 230, 130, 50, "SSDTs\n(Secondary SDT)", size=12, bold=True, fill="#fef9e7", stroke="#d35400"))
    frags1.append(svgkit.fitbox(350, 230, 140, 50, "MADT\n(Multiple APIC Desc)", size=12, bold=True, fill="#eafaf1", stroke="#27ae60"))
    frags1.append(svgkit.fitbox(515, 230, 130, 50, "MCFG\n(PCIe MMCONFIG)", size=12, bold=True, fill="#eafaf1", stroke="#27ae60"))
    
    # FADT pointers
    frags1.append(svgkit.arrow(90, 280, 90, 330, color="#27ae60"))
    frags1.append(svgkit.arrow(130, 280, 220, 330, color="#27ae60"))
    
    # Dynamic tables from FADT
    frags1.append(svgkit.fitbox(20, 330, 140, 50, "DSDT\n(AML Bytecode)", size=12, bold=True, fill="#fef9e7", stroke="#d35400"))
    frags1.append(svgkit.fitbox(180, 330, 130, 50, "FACS\n(Firmware ACPI Ctrl)", size=12, bold=True, fill="#eafaf1", stroke="#27ae60"))
    
    svgkit.render(os.path.join(out_dir, "acpi-tables.svg"), 680, 420, *frags1, title="Ієрархія статичних та динамічних таблиць ACPI")
    
    # 2. ACPI Namespace
    frags2 = []
    
    # Root
    frags2.append(svgkit.fitbox(320, 45, 60, 40, "\\ (Root)", size=14, bold=True, fill="#e8f4fc", stroke="#2457d6"))
    
    # Lines from Root to top-level branches
    frags2.append(svgkit.line(330, 85, 110, 130, color="#6b7280"))
    frags2.append(svgkit.line(345, 85, 260, 130, color="#6b7280"))
    frags2.append(svgkit.line(355, 85, 410, 130, color="#6b7280"))
    frags2.append(svgkit.line(370, 85, 560, 130, color="#6b7280"))
    
    # Top-level nodes
    frags2.append(svgkit.fitbox(50, 130, 120, 45, "\\_SB\n(System Bus)", size=12, bold=True, fill="#eafaf1", stroke="#27ae60"))
    frags2.append(svgkit.fitbox(200, 130, 120, 45, "\\_PR\n(Processors)", size=12, bold=True, fill="#eafaf1", stroke="#27ae60"))
    frags2.append(svgkit.fitbox(350, 130, 120, 45, "\\_TZ\n(Thermal Zones)", size=12, bold=True, fill="#eafaf1", stroke="#27ae60"))
    frags2.append(svgkit.fitbox(500, 130, 120, 45, "\\_GPE\n(Events)", size=12, bold=True, fill="#eafaf1", stroke="#27ae60"))
    
    # Lines from \_SB to devices
    frags2.append(svgkit.line(90, 175, 90, 220, color="#6b7280"))
    frags2.append(svgkit.line(130, 175, 240, 220, color="#6b7280"))
    
    # Devices under \_SB
    frags2.append(svgkit.fitbox(30, 220, 120, 45, "PCI0\n(PCI Root Bridge)", size=11, bold=True, fill="#fef9e7", stroke="#d35400"))
    frags2.append(svgkit.fitbox(180, 220, 120, 45, "EC0\n(Embedded Ctrl)", size=11, bold=True, fill="#fef9e7", stroke="#d35400"))
    
    # Lines from PCI0 to functions/methods
    frags2.append(svgkit.line(70, 265, 70, 310, color="#6b7280"))
    frags2.append(svgkit.line(110, 265, 200, 310, color="#6b7280"))
    
    # Under PCI0
    frags2.append(svgkit.fitbox(10, 310, 120, 50, "PEGP (GPU)\n_HID: PNP0A08\n_STA, _PS3", size=10, fill="#ffffff", stroke="#333333"))
    frags2.append(svgkit.fitbox(145, 310, 120, 50, "SAT0 (SATA)\n_ADR: 0x001F0002\n_STA, _INI", size=10, fill="#ffffff", stroke="#333333"))
    
    # Under \_PR
    frags2.append(svgkit.line(260, 175, 260, 310, color="#6b7280"))
    frags2.append(svgkit.fitbox(280, 310, 120, 50, "CPU0\n_HID: ACPI0007\n_PDC, _PTC", size=10, fill="#ffffff", stroke="#333333"))

    # Under \_TZ
    frags2.append(svgkit.line(410, 175, 410, 310, color="#6b7280"))
    frags2.append(svgkit.fitbox(415, 310, 115, 50, "TZ00\n_TMP, _CRT, _PSV\n_AC0 (Fan)", size=10, fill="#ffffff", stroke="#333333"))

    # Under \_GPE
    frags2.append(svgkit.line(560, 175, 560, 310, color="#6b7280"))
    frags2.append(svgkit.fitbox(545, 310, 115, 50, "_L1D (Lid Event)\n_E06 (PowerBtn)\nAML Handlers", size=10, fill="#ffffff", stroke="#333333"))

    svgkit.render(os.path.join(out_dir, "acpi-namespace.svg"), 680, 400, *frags2, title="Ієрархія простору імен ACPI (ACPI Namespace Tree)")

if __name__ == "__main__":
    render()
