import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
try:
    import svgkit
except ImportError:
    # Заглушка, якщо svgkit немає
    class SvgKitMock:
        def __init__(self):
            pass
        def create_doc(self, w, h):
            return "<svg width='{}' height='{}'></svg>".format(w, h)
        def save(self, doc, path):
            with open(path, 'w') as f:
                f.write(doc)
    svgkit = SvgKitMock()

def render():
    out_dir = os.path.dirname(__file__)
    
    # Схема LSM архітектури
    doc1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500">
    <rect width="100%" height="100%" fill="#ffffff" />
    <g font-family="sans-serif" font-size="14">
        <rect x="50" y="50" width="700" height="150" fill="#e3f2fd" stroke="#1e88e5" stroke-width="2" rx="10" />
        <text x="400" y="80" text-anchor="middle" font-size="18" font-weight="bold">User Space</text>
        
        <rect x="200" y="100" width="150" height="60" fill="#bbdefb" stroke="#1976d2" stroke-width="2" rx="5" />
        <text x="275" y="135" text-anchor="middle">Application Process</text>
        
        <!-- Syscall barrier -->
        <line x1="50" y1="200" x2="750" y2="200" stroke="#000" stroke-width="3" stroke-dasharray="10,10" />
        <text x="100" y="220" fill="#666">System Call Interface</text>
        
        <rect x="50" y="230" width="700" height="250" fill="#f5f5f5" stroke="#9e9e9e" stroke-width="2" rx="10" />
        <text x="400" y="260" text-anchor="middle" font-size="18" font-weight="bold">Kernel Space</text>
        
        <rect x="200" y="280" width="150" height="60" fill="#c8e6c9" stroke="#388e3c" stroke-width="2" rx="5" />
        <text x="275" y="315" text-anchor="middle">VFS / Subsystem</text>
        
        <!-- Arrow down -->
        <path d="M 275 160 L 275 280" stroke="#000" stroke-width="2" marker-end="url(#arrow)" />
        
        <rect x="450" y="280" width="200" height="60" fill="#fff9c4" stroke="#fbc02d" stroke-width="2" rx="5" />
        <text x="550" y="305" text-anchor="middle" font-weight="bold">LSM Hooks</text>
        <text x="550" y="325" text-anchor="middle" font-size="12">(security_hook_heads)</text>
        
        <!-- Arrow right -->
        <path d="M 350 310 L 450 310" stroke="#000" stroke-width="2" marker-end="url(#arrow)" />
        <text x="400" y="300" text-anchor="middle" font-size="12">Hook Call</text>
        
        <rect x="450" y="380" width="200" height="80" fill="#ffe0b2" stroke="#f57c00" stroke-width="2" rx="5" />
        <text x="550" y="405" text-anchor="middle" font-weight="bold">Security Modules</text>
        <text x="550" y="425" text-anchor="middle" font-size="12">SELinux, AppArmor,</text>
        <text x="550" y="445" text-anchor="middle" font-size="12">Smack, BPF-LSM</text>
        
        <!-- Arrow down to modules -->
        <path d="M 550 340 L 550 380" stroke="#000" stroke-width="2" marker-end="url(#arrow)" />
    </g>
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#000" />
        </marker>
    </defs>
    </svg>"""
    
    with open(os.path.join(out_dir, "lsm_architecture.svg"), 'w', encoding='utf-8') as f:
        f.write(doc1)
        
    # Схема LSM Stacking
    doc2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">
    <rect width="100%" height="100%" fill="#ffffff" />
    <g font-family="sans-serif" font-size="14">
        <text x="400" y="40" text-anchor="middle" font-size="20" font-weight="bold">LSM Stacking (Call Chain)</text>
        
        <rect x="50" y="100" width="150" height="60" fill="#e3f2fd" stroke="#1e88e5" stroke-width="2" rx="5" />
        <text x="125" y="135" text-anchor="middle">security_file_open()</text>
        
        <path d="M 200 130 L 250 130" stroke="#000" stroke-width="2" marker-end="url(#arrow)" />
        
        <rect x="250" y="100" width="120" height="200" fill="#fff9c4" stroke="#fbc02d" stroke-width="2" rx="5" />
        <text x="310" y="130" text-anchor="middle" font-weight="bold">Yama</text>
        <text x="310" y="160" text-anchor="middle">Return 0</text>
        
        <path d="M 370 130 L 420 130" stroke="#000" stroke-width="2" marker-end="url(#arrow)" />
        
        <rect x="420" y="100" width="120" height="200" fill="#c8e6c9" stroke="#388e3c" stroke-width="2" rx="5" />
        <text x="480" y="130" text-anchor="middle" font-weight="bold">AppArmor</text>
        <text x="480" y="160" text-anchor="middle">Return 0</text>
        
        <path d="M 540 130 L 590 130" stroke="#000" stroke-width="2" marker-end="url(#arrow)" />
        
        <rect x="590" y="100" width="120" height="200" fill="#ffccbc" stroke="#d84315" stroke-width="2" rx="5" />
        <text x="650" y="130" text-anchor="middle" font-weight="bold">BPF-LSM</text>
        <text x="650" y="160" text-anchor="middle" fill="#d32f2f">Return -EACCES</text>
        
        <!-- Error path -->
        <path d="M 650 300 L 650 350 L 125 350 L 125 160" stroke="#d32f2f" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrow-red)" fill="none" />
        <text x="387" y="340" text-anchor="middle" fill="#d32f2f">Early return on error (Short-circuit)</text>
    </g>
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#000" />
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#d32f2f" />
        </marker>
    </defs>
    </svg>"""
    
    with open(os.path.join(out_dir, "lsm_stacking.svg"), 'w', encoding='utf-8') as f:
        f.write(doc2)

if __name__ == "__main__":
    render()
