import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
import svgkit

def draw_arch():
    out = []
    out.append(svgkit.rect(0, 0, 500, 400, fill="#ffffff", stroke="none"))
    out.append(svgkit.text(250, 30, "Архітектура Plan 9 та протоколу 9P (v9fs)", bold=True, size=16, anchor="middle"))
    
    out.append(svgkit.rect(50, 70, 180, 100, fill="#e3f2fd", stroke="#1565c0", sw=2))
    out.append(svgkit.text(140, 100, "Client (Linux VFS / WSL2)", bold=True, size=12, anchor="middle"))
    out.append(svgkit.text(140, 130, "v9fs Kernel Driver", size=11, anchor="middle"))
    
    out.append(svgkit.rect(270, 70, 180, 100, fill="#fff3e0", stroke="#e65100", sw=2))
    out.append(svgkit.text(360, 100, "Server (Plan 9 / QEMU)", bold=True, size=12, anchor="middle"))
    out.append(svgkit.text(360, 130, "9P Export Daemon", size=11, anchor="middle"))
    
    out.append(svgkit.arrow(230, 120, 270, 120))
    out.append(svgkit.text(250, 110, "9P2000.L (RPC)", size=10, anchor="middle"))
    
    out.append(svgkit.rect(50, 230, 400, 120, fill="#f3e5f5", stroke="#6a1b9a", sw=2))
    out.append(svgkit.text(250, 260, "Операції протоколу 9P", bold=True, size=13, anchor="middle"))
    out.append(svgkit.text(250, 290, "Tversion/Rversion · Tattach/Rattach · Twalk/Rwalk", size=11, anchor="middle"))
    out.append(svgkit.text(250, 315, "Tread/Rread · Twrite/Rwrite · Tclunk/Rclunk", size=11, anchor="middle"))
    
    return out

def render():
    frags = draw_arch()
    out_path = os.path.join(os.path.dirname(__file__), "plan9_arch.svg")
    svgkit.render(out_path, 500, 400, *frags)

if __name__ == "__main__":
    render()
