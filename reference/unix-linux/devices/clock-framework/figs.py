import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
try:
    from svgkit import *
except ImportError:
    print("WARNING: svgkit not found, using a dummy")
    sys.exit(0)

def draw_clock_tree():
    w, h = 800, 400
    
    frags = []
    
    # Oscillator
    bx_osc, bw_osc, bh_osc = textbox(100, 200, "Кварцовий\nрезонатор\n(OSC)", bold=True, fill="#e8f4f8")
    frags.append(bx_osc)
    
    # PLL
    bx_pll, bw_pll, bh_pll = textbox(250, 100, "PLL (x24)\nСистемний\nгодинник", bold=True, fill="#fdecea")
    frags.append(bx_pll)
    
    # Divider
    bx_div, bw_div, bh_div = textbox(400, 100, "Дільник\n(/2)", bold=True, fill="#eaf0fd")
    frags.append(bx_div)
    
    # Gate
    bx_gate, bw_gate, bh_gate = textbox(550, 100, "Gate\n(UART0)", bold=True)
    frags.append(bx_gate)
    
    # Peripheral
    bx_per, bw_per, bh_per = textbox(700, 100, "UART0\nКонтролер", bold=True, fill="#fff2cc")
    frags.append(bx_per)
    
    # Mux
    bx_mux, bw_mux, bh_mux = textbox(400, 300, "Мультиплексор\n(RTC)", bold=True, fill="#eaf0fd")
    frags.append(bx_mux)
    
    bx_rtc, bw_rtc, bh_rtc = textbox(700, 300, "RTC\nМодуль", bold=True, fill="#fff2cc")
    frags.append(bx_rtc)
    
    bx_osc32, bw_osc32, bh_osc32 = textbox(250, 300, "Кварц\n32.768 кГц", bold=True, fill="#e8f4f8")
    frags.append(bx_osc32)
    
    # Lines
    frags.append(arrow(100 + bw_osc/2, 200, 250 - bw_pll/2, 100))
    frags.append(arrow(100 + bw_osc/2, 200, 400 - bw_mux/2, 280)) # To MUX input 1
    frags.append(arrow(250 + bw_osc32/2, 300, 400 - bw_mux/2, 320)) # To MUX input 2
    
    frags.append(arrow(250 + bw_pll/2, 100, 400 - bw_div/2, 100))
    frags.append(arrow(400 + bw_div/2, 100, 550 - bw_gate/2, 100))
    frags.append(arrow(550 + bw_gate/2, 100, 700 - bw_per/2, 100))
    
    frags.append(arrow(400 + bw_mux/2, 300, 700 - bw_rtc/2, 300))
    
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "clock-tree.svg"), w, h, *frags, title="Дерево тактування (Clock Tree)")

if __name__ == "__main__":
    draw_clock_tree()
    print("SVG generated.")
