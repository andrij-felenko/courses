import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def render():
    out_dir = os.path.dirname(__file__)
    
    # 1. ACPI Tables Hierarchy
    # Using svgkit functions that return SVG fragment strings
    frags1 = []
    frags1.append(svgkit.rect(200, 20, 200, 50, fill="#ddeeff", stroke="#336699", rx=5))
    frags1.append(svgkit.text(300, 45, "RSDP", bold=True, size=16))
    frags1.append(svgkit.text(300, 60, "(Root System Description Pointer)", size=10))
    
    frags1.append(svgkit.arrow(300, 70, 300, 100, color="#336699"))
    
    frags1.append(svgkit.rect(200, 100, 200, 50, fill="#ddeeff", stroke="#336699", rx=5))
    frags1.append(svgkit.text(300, 125, "RSDT / XSDT", bold=True, size=16))
    
    frags1.append(svgkit.arrow(200, 150, 100, 200, color="#336699"))
    frags1.append(svgkit.arrow(300, 150, 300, 200, color="#336699"))
    frags1.append(svgkit.arrow(400, 150, 500, 200, color="#336699"))
    
    frags1.append(svgkit.rect(50, 200, 100, 50, fill="#eeffdd", stroke="#339933", rx=5))
    frags1.append(svgkit.text(100, 230, "FADT", bold=True, size=16))
    
    frags1.append(svgkit.rect(250, 200, 100, 50, fill="#eeffdd", stroke="#339933", rx=5))
    frags1.append(svgkit.text(300, 230, "SSDTs", bold=True, size=16))
    
    frags1.append(svgkit.rect(450, 200, 100, 50, fill="#eeffdd", stroke="#339933", rx=5))
    frags1.append(svgkit.text(500, 230, "MADT", bold=True, size=16))
    
    frags1.append(svgkit.arrow(100, 250, 100, 300, color="#336699"))
    
    frags1.append(svgkit.rect(50, 300, 100, 50, fill="#ffeecc", stroke="#cc6600", rx=5))
    frags1.append(svgkit.text(100, 330, "DSDT", bold=True, size=16))
    
    svgkit.render(os.path.join(out_dir, "acpi_tables.svg"), 600, 400, *frags1, title="ACPI Tables Hierarchy")
    
    # 2. ACPI Namespace
    frags2 = []
    frags2.append(svgkit.circle(300, 40, 20, fill="#ddeeff", stroke="#336699"))
    frags2.append(svgkit.text(300, 45, "\\", bold=True, size=20))
    
    frags2.append(svgkit.line(300, 60, 150, 120, color="#336699"))
    frags2.append(svgkit.line(300, 60, 300, 120, color="#336699"))
    frags2.append(svgkit.line(300, 60, 450, 120, color="#336699"))
    
    frags2.append(svgkit.rect(100, 120, 100, 40, fill="#eeffdd", stroke="#339933", rx=5))
    frags2.append(svgkit.text(150, 145, "_PR", bold=True, size=16))
    
    frags2.append(svgkit.rect(250, 120, 100, 40, fill="#eeffdd", stroke="#339933", rx=5))
    frags2.append(svgkit.text(300, 145, "_SB", bold=True, size=16))
    
    frags2.append(svgkit.rect(400, 120, 100, 40, fill="#eeffdd", stroke="#339933", rx=5))
    frags2.append(svgkit.text(450, 145, "_TZ", bold=True, size=16))
    
    frags2.append(svgkit.line(300, 160, 250, 220, color="#336699"))
    frags2.append(svgkit.line(300, 160, 350, 220, color="#336699"))
    
    frags2.append(svgkit.rect(200, 220, 100, 40, fill="#ffeecc", stroke="#cc6600", rx=5))
    frags2.append(svgkit.text(250, 245, "PCI0", bold=True, size=16))
    
    frags2.append(svgkit.rect(310, 220, 100, 40, fill="#ffeecc", stroke="#cc6600", rx=5))
    frags2.append(svgkit.text(360, 245, "USB0", bold=True, size=16))
    
    svgkit.render(os.path.join(out_dir, "acpi_namespace.svg"), 600, 400, *frags2, title="ACPI Namespace")

if __name__ == "__main__":
    render()
