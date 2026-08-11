import sys
import os

def render(name, content):
    with open(name, "w", encoding="utf-8") as f:
        f.write(content)

svg_osnoise = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400">
  <rect width="100%" height="100%" fill="#f4f4f4"/>
  <text x="400" y="50" font-size="24" text-anchor="middle" fill="#333">Трасування OS Noise</text>
  
  <line x1="50" y1="100" x2="750" y2="100" stroke="#888" stroke-width="2"/>
  <line x1="50" y1="200" x2="750" y2="200" stroke="#888" stroke-width="2"/>
  <line x1="50" y1="300" x2="750" y2="300" stroke="#888" stroke-width="2"/>
  
  <text x="40" y="105" font-size="14" text-anchor="end" fill="#555">CPU 0</text>
  <text x="40" y="205" font-size="14" text-anchor="end" fill="#555">CPU 1</text>
  <text x="40" y="305" font-size="14" text-anchor="end" fill="#555">CPU 2</text>
  
  <rect x="100" y="80" width="100" height="40" fill="#4caf50" rx="4"/>
  <rect x="250" y="80" width="20" height="40" fill="#f44336" rx="4"/> <!-- Noise -->
  <rect x="300" y="80" width="400" height="40" fill="#4caf50" rx="4"/>

  <rect x="100" y="180" width="200" height="40" fill="#4caf50" rx="4"/>
  <rect x="350" y="180" width="30" height="40" fill="#ff9800" rx="4"/> <!-- IRQ -->
  <rect x="420" y="180" width="250" height="40" fill="#4caf50" rx="4"/>
  
  <rect x="100" y="280" width="300" height="40" fill="#4caf50" rx="4"/>
  <rect x="450" y="280" width="10" height="40" fill="#e91e63" rx="4"/> <!-- NMI/SMI -->
  <rect x="500" y="280" width="200" height="40" fill="#4caf50" rx="4"/>
  
  <text x="260" y="70" font-size="12" fill="#d32f2f" text-anchor="middle">Переривання</text>
  <text x="365" y="170" font-size="12" fill="#e65100" text-anchor="middle">SoftIRQ</text>
  <text x="455" y="270" font-size="12" fill="#c2185b" text-anchor="middle">NMI/SMI</text>
</svg>
"""

svg_timerlat = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="400" y="40" font-size="24" text-anchor="middle" fill="#333">timerlat: Вимірювання затримки таймера</text>
  
  <!-- Осі -->
  <line x1="100" y1="300" x2="700" y2="300" stroke="#000" stroke-width="2"/>
  <line x1="100" y1="300" x2="100" y2="100" stroke="#000" stroke-width="2"/>
  
  <text x="400" y="340" font-size="16" text-anchor="middle" fill="#000">Час (мкс)</text>
  
  <!-- Цільовий час -->
  <line x1="300" y1="300" x2="300" y2="150" stroke="#f44336" stroke-width="2" stroke-dasharray="5,5"/>
  <text x="300" y="140" font-size="14" fill="#d32f2f" text-anchor="middle">Очікуваний час</text>
  
  <!-- Фактичний час -->
  <line x1="500" y1="300" x2="500" y2="180" stroke="#4caf50" stroke-width="2"/>
  <text x="500" y="170" font-size="14" fill="#388e3c" text-anchor="middle">Фактичний виклик</text>
  
  <!-- Затримка -->
  <line x1="300" y1="250" x2="500" y2="250" stroke="#2196f3" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="400" y="240" font-size="14" fill="#1976d2" text-anchor="middle">Затримка (Latency)</text>
  
</svg>
"""

def main():
    render(os.path.join(IMG, 'osnoise.svg'), svg_osnoise)
    render(os.path.join(IMG, 'timerlat.svg'), svg_timerlat)
    print("SVGs generated successfully.")

if __name__ == "__main__":
    main()
