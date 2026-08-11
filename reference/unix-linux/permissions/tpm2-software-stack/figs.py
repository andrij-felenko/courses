import sys
import os
sys.path.insert(0, os.path.abspath('../../../../scripts'))

from svgkit import render, rect, text

def tpm_architecture():
    out = []
    
    # Фон
    out.append(rect(0, 0, 600, 500, fill="#ffffff", rx=8))
    out.append(text(300, 40, "TPM2 Software Stack (TSS2)", size=24, bold=True, anchor="middle"))
    
    # User Space
    out.append(rect(50, 70, 500, 250, fill="#e8f4f8", rx=4, stroke="#b3d4e0", sw=2))
    out.append(text(60, 90, "User Space", size=16, bold=True, color="#333333", anchor="start"))
    
    # Apps
    out.append(rect(100, 110, 400, 40, fill="#dcedc8", rx=4, stroke="#8bc34a", sw=2))
    out.append(text(300, 135, "Applications (tpm2-tools, OpenSSL engine, etc.)", size=14, anchor="middle"))
    
    # FAPI
    out.append(rect(100, 170, 180, 40, fill="#fff9c4", rx=4, stroke="#fbc02d", sw=2))
    out.append(text(190, 195, "FAPI (Feature API)", size=14, anchor="middle"))
    
    # ESAPI
    out.append(rect(100, 230, 180, 40, fill="#fff9c4", rx=4, stroke="#fbc02d", sw=2))
    out.append(text(190, 255, "ESAPI (Enhanced System)", size=14, anchor="middle"))
    
    # SAPI (SYS)
    out.append(rect(320, 230, 180, 40, fill="#fff9c4", rx=4, stroke="#fbc02d", sw=2))
    out.append(text(410, 255, "SAPI (System API)", size=14, anchor="middle"))
    
    # TCTI
    out.append(rect(100, 290, 400, 40, fill="#ffe0b2", rx=4, stroke="#fb8c00", sw=2))
    out.append(text(300, 315, "TCTI (Command Transmission Interface)", size=14, anchor="middle"))
    
    # Kernel Space
    out.append(rect(50, 350, 500, 120, fill="#f0f4c3", rx=4, stroke="#cddc39", sw=2))
    out.append(text(60, 370, "Kernel Space", size=16, bold=True, color="#333333", anchor="start"))
    
    # TPM Resource Manager
    out.append(rect(100, 390, 180, 40, fill="#e1bee7", rx=4, stroke="#9c27b0", sw=2))
    out.append(text(190, 415, "/dev/tpmrm0 (RM)", size=14, anchor="middle"))
    
    # Direct TPM Device
    out.append(rect(320, 390, 180, 40, fill="#e1bee7", rx=4, stroke="#9c27b0", sw=2))
    out.append(text(410, 415, "/dev/tpm0", size=14, anchor="middle"))
    
    return "\n".join(out)

if __name__ == "__main__":
    render(os.path.join(IMG, 'tpm2-tss-architecture.svg'), 600, 500, tpm_architecture())
