import sys
import os

# Додамо шлях до scripts/ для імпорту svgkit, якщо він існує
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

import svgkit   # заглушки тут немає навмисно: зламаний імпорт має падати ГОЛОСНО,
                # інакше фігури тихо перестають з'являтися, а прогін виглядає успішним


def render():
    d = svgkit.Drawing(size=(800, 400), viewBox="0 0 800 400")
    
    # Background
    d.add(str(svgkit.Rect((0, 0), (800, 400), fill="#ffffff")))
    
    # Title
    d.add(str(svgkit.Text("Netfilter Conntrack Tuple Example", (400, 30), text_anchor="middle", font_size="24", font_family="Arial", font_weight="bold")))
    
    # Client box
    d.add(str(svgkit.Rect((50, 100), (150, 200), fill="#e0f7fa", stroke="#006064", stroke_width="2", rx="10")))
    d.add(str(svgkit.Text("Client", (125, 140), text_anchor="middle", font_size="18", font_family="Arial", font_weight="bold")))
    d.add(str(svgkit.Text("192.168.1.100", (125, 170), text_anchor="middle", font_size="14", font_family="Arial")))
    d.add(str(svgkit.Text("Port: 50000", (125, 190), text_anchor="middle", font_size="14", font_family="Arial")))
    
    # Server box
    d.add(str(svgkit.Rect((600, 100), (150, 200), fill="#fce4ec", stroke="#880e4f", stroke_width="2", rx="10")))
    d.add(str(svgkit.Text("Server", (675, 140), text_anchor="middle", font_size="18", font_family="Arial", font_weight="bold")))
    d.add(str(svgkit.Text("8.8.8.8", (675, 170), text_anchor="middle", font_size="14", font_family="Arial")))
    d.add(str(svgkit.Text("Port: 80", (675, 190), text_anchor="middle", font_size="14", font_family="Arial")))
    
    # Conntrack box (middle)
    d.add(str(svgkit.Rect((275, 100), (250, 200), fill="#fff3e0", stroke="#e65100", stroke_width="2", rx="10", stroke_dasharray="5,5")))
    d.add(str(svgkit.Text("nf_conntrack", (400, 130), text_anchor="middle", font_size="18", font_family="Arial", font_weight="bold")))
    
    # ORIGINAL tuple
    d.add(str(svgkit.Text("ORIGINAL Tuple", (400, 160), text_anchor="middle", font_size="14", font_family="Arial", font_weight="bold", fill="#1565c0")))
    d.add(str(svgkit.Text("SRC:192.168.1.100 DST:8.8.8.8", (400, 180), text_anchor="middle", font_size="12", font_family="Courier")))
    d.add(str(svgkit.Text("SP:50000 DP:80 PROTO:TCP", (400, 195), text_anchor="middle", font_size="12", font_family="Courier")))
    
    # REPLY tuple
    d.add(str(svgkit.Text("REPLY Tuple", (400, 230), text_anchor="middle", font_size="14", font_family="Arial", font_weight="bold", fill="#c62828")))
    d.add(str(svgkit.Text("SRC:8.8.8.8 DST:192.168.1.100", (400, 250), text_anchor="middle", font_size="12", font_family="Courier")))
    d.add(str(svgkit.Text("SP:80 DP:50000 PROTO:TCP", (400, 265), text_anchor="middle", font_size="12", font_family="Courier")))
    
    # Arrows
    # Original direction
    d.add(str(svgkit.Line((200, 170), (275, 170), stroke="#1565c0", stroke_width="3", marker_end="url(#arrow-blue)")))
    d.add(str(svgkit.Line((525, 170), (600, 170), stroke="#1565c0", stroke_width="3", marker_end="url(#arrow-blue)")))
    # Reply direction
    d.add(str(svgkit.Line((600, 240), (525, 240), stroke="#c62828", stroke_width="3", marker_end="url(#arrow-red)")))
    d.add(str(svgkit.Line((275, 240), (200, 240), stroke="#c62828", stroke_width="3", marker_end="url(#arrow-red)")))
    
    # Add markers for arrows manually since svgkit wrapper is minimal
    d.elements.insert(0, '''
    <defs>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#1565c0" />
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#c62828" />
        </marker>
    </defs>
    ''')
    
    d.save(os.path.join(os.path.dirname(__file__), 'conntrack-architecture.svg'))

if __name__ == '__main__':
    render()
