import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

try:
    import svgkit
except ImportError:
    svgkit = None

def render():
    if not svgkit: return
    frags1 = [
        svgkit.rect(10, 10, 580, 380, fill="#f0f0f0", stroke="#ccc"),
        svgkit.text(300, 50, "Multipath TCP Architecture", size=20, anchor="middle", bold=True)
    ]
    out1 = os.path.join(os.path.dirname(__file__), "mptcp-arch.svg")
    svgkit.render(out1, 600, 400, *frags1)

    frags2 = [
        svgkit.rect(10, 10, 580, 380, fill="#e0f0e0", stroke="#ccc"),
        svgkit.text(300, 50, "MP_CAPABLE and MP_JOIN Process", size=20, anchor="middle", bold=True)
    ]
    out2 = os.path.join(os.path.dirname(__file__), "mptcp-handshake.svg")
    svgkit.render(out2, 600, 400, *frags2)

if __name__ == '__main__':
    render()
