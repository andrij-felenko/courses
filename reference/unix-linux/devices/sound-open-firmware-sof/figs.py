import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def render_svg():
    frags = []
    
    # Kernel Space
    frags.append(rect(50, 50, 300, 200, fill="#e8f4f8"))
    frags.append(text(200, 70, "Linux Kernel (ALSA SoC)", size=16, bold=True))
    
    frags.append(textbox(130, 110, "snd_sof (Platform)")[0])
    frags.append(textbox(270, 110, "Machine Driver")[0])
    frags.append(textbox(270, 170, "Codec Driver")[0])
    frags.append(textbox(130, 170, "IPC / Mailbox", fill="#fff2cc")[0])
    
    # DSP Space
    frags.append(rect(450, 50, 300, 200, fill="#e2efda"))
    frags.append(text(600, 70, "DSP (Sound Open Firmware)", size=16, bold=True))
    
    frags.append(textbox(530, 110, "Zephyr RTOS")[0])
    frags.append(textbox(530, 170, "IPC Server", fill="#fff2cc")[0])
    frags.append(textbox(670, 130, "Audio Pipeline\n(EQ, SRC, Mix)", fill="#f8cbad")[0])
    
    # Connections
    frags.append(arrow(180, 170, 480, 170))
    frags.append(text(330, 160, "IPC Messages"))
    
    frags.append(arrow(670, 170, 670, 260))
    frags.append(textbox(670, 290, "I2S / HDA Codec", fill="#d9d9d9")[0])
    
    filepath = os.path.join(os.path.dirname(__file__), "sof-arch.svg")
    render(filepath, 800, 400, *frags, title="SOF Architecture Diagram")

if __name__ == '__main__':
    render_svg()
