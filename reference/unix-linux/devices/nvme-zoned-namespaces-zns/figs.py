import sys
import os

# Add the scripts directory to the path so we can import svgkit
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts'))
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import svgkit

def render():
    """
    Renders the Zone State Machine diagram for NVMe ZNS.
    Outputs an SVG file in the current directory.
    """
    # Create an SVG drawing
    # Assuming svgkit.Drawing exists and takes width/height
    try:
        svg = svgkit.Drawing(width=800, height=600)
    except AttributeError:
        # Fallback if svgkit interface is slightly different in the project
        print("Could not initialize svgkit.Drawing. Ensure svgkit.py is correctly set up.")
        return

    # Background
    svg.rect(0, 0, 800, 600, fill="#f8f9fa")

    # Title
    svg.text("NVMe ZNS: Zone State Machine", x=400, y=40, font_size=24, font_weight="bold", text_anchor="middle")

    # Define State Boxes (x, y, width, height, text)
    states = {
        "Empty": (350, 100, 100, 50),
        "Implicit Open": (150, 250, 140, 50),
        "Explicit Open": (510, 250, 140, 50),
        "Closed": (350, 350, 100, 50),
        "Full": (350, 450, 100, 50),
        "Read Only": (650, 450, 100, 50),
        "Offline": (100, 450, 100, 50)
    }

    # Draw states
    for name, (x, y, w, h) in states.items():
        rx, ry = 10, 10 # Rounded corners
        svg.rect(x, y, w, h, rx=rx, ry=ry, fill="#ffffff", stroke="#343a40", stroke_width=2)
        # Assuming svg.text uses center anchor by default or we can center it
        text_x = x + w / 2
        text_y = y + h / 2 + 5
        svg.text(name, x=text_x, y=text_y, font_size=16, text_anchor="middle")

    # Define transitions (start_node, end_node, label, control_points)
    # Simple straight lines or paths could be drawn depending on svgkit capabilities
    # We will use simple lines here and add arrows manually or assume svgkit has an arrow function
    
    def draw_arrow(start_x, start_y, end_x, end_y, label=""):
        svg.line(start_x, start_y, end_x, end_y, stroke="#007bff", stroke_width=2)
        # Mocking an arrowhead with a small circle for simplicity
        svg.circle(end_x, end_y, r=4, fill="#007bff")
        
        # Label
        lx = (start_x + end_x) / 2
        ly = (start_y + end_y) / 2 - 10
        svg.text(label, x=lx, y=ly, font_size=12, fill="#495057", text_anchor="middle")

    # Draw Transitions
    
    # Empty -> Implicit Open (Write)
    draw_arrow(states["Empty"][0], states["Empty"][1] + 25, 
               states["Implicit Open"][0] + 70, states["Implicit Open"][1], "Write")
    
    # Empty -> Explicit Open (Zone Open)
    draw_arrow(states["Empty"][0] + 100, states["Empty"][1] + 25, 
               states["Explicit Open"][0] + 70, states["Explicit Open"][1], "Zone Open")

    # Implicit Open -> Closed (Zone Close / internal)
    draw_arrow(states["Implicit Open"][0] + 140, states["Implicit Open"][1] + 25, 
               states["Closed"][0], states["Closed"][1] + 25, "Close")
               
    # Explicit Open -> Closed (Zone Close)
    draw_arrow(states["Explicit Open"][0], states["Explicit Open"][1] + 25, 
               states["Closed"][0] + 100, states["Closed"][1] + 25, "Zone Close")

    # Closed -> Implicit Open (Write)
    draw_arrow(states["Closed"][0], states["Closed"][1], 
               states["Implicit Open"][0] + 140, states["Implicit Open"][1] + 50, "Write")
               
    # Closed -> Explicit Open (Zone Open)
    draw_arrow(states["Closed"][0] + 100, states["Closed"][1], 
               states["Explicit Open"][0], states["Explicit Open"][1] + 50, "Zone Open")

    # Implicit/Explicit Open/Closed -> Full (Write boundary / Zone Finish)
    draw_arrow(states["Closed"][0] + 50, states["Closed"][1] + 50, 
               states["Full"][0] + 50, states["Full"][1], "Finish / Full")

    # Any -> Empty (Zone Reset)
    # Drawing one prominent reset line from Full to Empty
    svg.line(states["Full"][0] - 50, states["Full"][1] + 25, 
             50, states["Full"][1] + 25, stroke="#dc3545", stroke_width=2, stroke_dasharray="5,5")
    svg.line(50, states["Full"][1] + 25, 50, states["Empty"][1] + 25, stroke="#dc3545", stroke_width=2, stroke_dasharray="5,5")
    svg.line(50, states["Empty"][1] + 25, states["Empty"][0], states["Empty"][1] + 25, stroke="#dc3545", stroke_width=2, stroke_dasharray="5,5")
    svg.circle(states["Empty"][0], states["Empty"][1] + 25, r=4, fill="#dc3545")
    svg.text("Zone Reset", x=50, y=300, font_size=12, fill="#dc3545", text_anchor="middle", transform="rotate(-90 50,300)")

    # Save SVG
    output_path = os.path.join(os.path.dirname(__file__), "zone_state_machine.svg")
    try:
        svg.save(output_path)
        print(f"Rendered {output_path}")
    except AttributeError:
        # Fallback to write string representation if save is missing
        with open(output_path, "w") as f:
            f.write(str(svg))
        print(f"Rendered {output_path} (via str())")

if __name__ == '__main__':
    render()
