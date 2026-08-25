import sys
import os

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts'))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if os.path.abspath('scripts') not in sys.path:
    sys.path.insert(0, os.path.abspath('scripts'))

from svgkit import render, rect, text, textbox, arrow, line, INK

def tpm_architecture():
    out = []
    
    # Canvas Header / Background
    out.append(rect(0, 0, 640, 540, fill="#ffffff", stroke="#ffffff", rx=0))
    out.append(text(320, 35, "Архітектура TPM2 Software Stack (TSS2) у Linux", size=20, bold=True, anchor="middle"))
    
    # --- User Space Box ---
    out.append(rect(40, 55, 560, 275, fill="#f4f8fb", rx=8, stroke="#b3d4e0", sw=1.5))
    out.append(text(60, 80, "User Space", size=15, bold=True, color="#1a365d", anchor="start"))
    
    # Applications
    app_box, _, _ = textbox(320, 115, "Застосунки: tpm2-tools, OpenSSL tpm2-provider, systemd-cryptenroll, SSH", size=12, pad=8, fill="#e8f5e9", stroke="#4caf50", bold=True)
    out.append(app_box)
    
    # High-level API (FAPI)
    fapi_box, _, _ = textbox(180, 180, "FAPI\n(High-Level Feature API)", size=12, pad=8, fill="#fffde7", stroke="#fbc02d")
    out.append(fapi_box)
    
    # Mid-level API (ESAPI & SAPI)
    esapi_box, _, _ = textbox(180, 245, "ESAPI\n(Enhanced System API)", size=12, pad=8, fill="#fff8e1", stroke="#ffa000")
    out.append(esapi_box)
    
    sapi_box, _, _ = textbox(460, 245, "SYS / SAPI\n(Direct Binary System API)", size=12, pad=8, fill="#fff8e1", stroke="#ffa000")
    out.append(sapi_box)
    
    # Abstraction Layer (TCTI)
    tcti_box, _, _ = textbox(320, 300, "TCTI (TPM Command Transmission Interface)", size=12, pad=8, fill="#ffe0b2", stroke="#fb8c00", bold=True)
    out.append(tcti_box)
    
    # --- Kernel Space Box ---
    out.append(rect(40, 350, 560, 95, fill="#f9fbe7", rx=8, stroke="#cddc39", sw=1.5))
    out.append(text(60, 375, "Kernel Space", size=15, bold=True, color="#33691e", anchor="start"))
    
    # Resource Manager & Character Device
    rm_box, _, _ = textbox(180, 410, "/dev/tpmrm0\n(In-Kernel Resource Manager)", size=11, pad=6, fill="#f3e5f5", stroke="#ab47bc")
    out.append(rm_box)
    
    dev_box, _, _ = textbox(460, 410, "/dev/tpm0\n(Direct Character Device)", size=11, pad=6, fill="#f3e5f5", stroke="#ab47bc")
    out.append(dev_box)
    
    # --- Hardware Layer ---
    hw_box, _, _ = textbox(320, 490, "Апаратний чип TPM 2.0 / fTPM (NVRAM, PCR, TRNG, Crypto Engine)", size=12, pad=10, fill="#ffe0b2", stroke="#e65100", bold=True)
    out.append(hw_box)
    
    # Connecting lines / arrows
    out.append(arrow(320, 135, 180, 160, color="#555555", sw=1.2))
    out.append(arrow(430, 135, 460, 225, color="#555555", sw=1.2))
    out.append(arrow(390, 135, 262, 242, color="#555555", sw=1.2))
    out.append(arrow(180, 200, 180, 225, color="#555555", sw=1.2))
    out.append(arrow(180, 265, 280, 288, color="#555555", sw=1.2))
    out.append(arrow(460, 265, 360, 288, color="#555555", sw=1.2))
    
    out.append(arrow(280, 315, 180, 392, color="#555555", sw=1.2))
    out.append(arrow(360, 315, 460, 392, color="#555555", sw=1.2))
    out.append(arrow(180, 428, 260, 472, color="#555555", sw=1.2))
    out.append(arrow(460, 428, 380, 472, color="#555555", sw=1.2))
    
    return "\n".join(out)

if __name__ == "__main__":
    IMG = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(IMG, exist_ok=True)
    render(os.path.join(IMG, 'tpm2-tss-architecture.svg'), 640, 540, tpm_architecture())
