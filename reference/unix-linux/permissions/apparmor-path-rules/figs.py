import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "img")

def render_vfs_path_resolution():
    svg = """<svg viewBox="0 0 820 380" width="820" height="380" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #1e293b; }
    .box-title { font-family: sans-serif; font-size: 14px; font-weight: bold; fill: #0f172a; }
    .label { font-family: sans-serif; font-size: 12px; fill: #334155; }
    .code { font-family: monospace; font-size: 12px; fill: #0284c7; font-weight: bold; }
    .arrow { stroke: #475569; stroke-width: 2; marker-end: url(#arrowhead); }
    .bg-user { fill: #eff6ff; stroke: #3b82f6; stroke-width: 1.5; rx: 6; }
    .bg-vfs { fill: #f0fdf4; stroke: #22c55e; stroke-width: 1.5; rx: 6; }
    .bg-lsm { fill: #fefce8; stroke: #eab308; stroke-width: 1.5; rx: 6; }
    .bg-decision { fill: #fef2f2; stroke: #ef4444; stroke-width: 1.5; rx: 6; }
  </style>

  <defs>
    <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#475569" />
    </marker>
  </defs>

  <!-- Title -->
  <text x="410" y="30" class="title" text-anchor="middle">Відновлення шляху у VFS та перевірка LSM-хуком AppArmor</text>

  <!-- User Space -->
  <rect x="20" y="60" width="180" height="280" class="bg-user" />
  <text x="110" y="85" class="box-title" text-anchor="middle">User Space</text>
  
  <rect x="35" y="110" width="150" height="60" fill="#ffffff" stroke="#93c5fd" rx="4" />
  <text x="110" y="132" class="label" text-anchor="middle">Процес (Nginx)</text>
  <text x="110" y="152" class="code" text-anchor="middle">openat("/var/log/...")</text>

  <rect x="35" y="240" width="150" height="70" fill="#ffffff" stroke="#93c5fd" rx="4" />
  <text x="110" y="262" class="label" text-anchor="middle">Результат виклику</text>
  <text x="110" y="282" class="code" text-anchor="middle">fd &gt;= 0 / -EACCES</text>

  <!-- Kernel VFS -->
  <rect x="230" y="60" width="230" height="280" class="bg-vfs" />
  <text x="345" y="85" class="box-title" text-anchor="middle">Kernel VFS Layer</text>

  <rect x="250" y="110" width="190" height="50" fill="#ffffff" stroke="#86efac" rx="4" />
  <text x="345" y="130" class="label" text-anchor="middle">Syscall Handler</text>
  <text x="345" y="148" class="code" text-anchor="middle">do_sys_openat2()</text>

  <rect x="250" y="180" width="190" height="70" fill="#ffffff" stroke="#86efac" rx="4" />
  <text x="345" y="200" class="label" text-anchor="middle">Path Resolution</text>
  <text x="345" y="220" class="code" text-anchor="middle">d_path(struct path*)</text>
  <text x="345" y="238" class="label" text-anchor="middle" font-size="10">dentry + vfsmount</text>

  <!-- AppArmor LSM -->
  <rect x="490" y="60" width="180" height="280" class="bg-lsm" />
  <text x="580" y="85" class="box-title" text-anchor="middle">AppArmor LSM</text>

  <rect x="505" y="110" width="150" height="50" fill="#ffffff" stroke="#fde047" rx="4" />
  <text x="580" y="130" class="label" text-anchor="middle">LSM Hook</text>
  <text x="580" y="148" class="code" text-anchor="middle">security_file_open</text>

  <rect x="505" y="180" width="150" height="70" fill="#ffffff" stroke="#fde047" rx="4" />
  <text x="580" y="200" class="label" text-anchor="middle">DFA Matcher</text>
  <text x="580" y="220" class="code" text-anchor="middle">aa_dfa_match()</text>
  <text x="580" y="238" class="label" text-anchor="middle" font-size="10">O(N) string walk</text>

  <!-- Decision -->
  <rect x="690" y="60" width="110" height="280" class="bg-decision" />
  <text x="745" y="85" class="box-title" text-anchor="middle">Рішення</text>

  <rect x="700" y="120" width="90" height="40" fill="#dcfce7" stroke="#16a34a" rx="4" />
  <text x="745" y="145" class="label" text-anchor="middle" font-weight="bold" fill="#15803d">ALLOW (0)</text>

  <rect x="700" y="200" width="90" height="40" fill="#fee2e2" stroke="#dc2626" rx="4" />
  <text x="745" y="225" class="label" text-anchor="middle" font-weight="bold" fill="#b91c1c">DENY (-13)</text>

  <!-- Connectors -->
  <line x1="185" y1="140" x2="250" y2="140" class="arrow" />
  <line x1="345" y1="160" x2="345" y2="180" class="arrow" />
  <line x1="440" y1="215" x2="505" y2="215" class="arrow" />
  <line x1="580" y1="160" x2="580" y2="180" class="arrow" />
  <line x1="655" y1="195" x2="700" y2="140" class="arrow" />
  <line x1="655" y1="225" x2="700" y2="220" class="arrow" />
</svg>"""
    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, "apparmor-vfs-path-resolution.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("Wrote:", out_path)

def render_dfa_matching():
    svg = """<svg viewBox="0 0 820 260" width="820" height="260" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #1e293b; }
    .node { fill: #ffffff; stroke: #2563eb; stroke-width: 2; }
    .node-accept { fill: #dcfce7; stroke: #16a34a; stroke-width: 2.5; }
    .node-text { font-family: sans-serif; font-size: 13px; font-weight: bold; fill: #1e293b; }
    .edge { stroke: #64748b; stroke-width: 1.8; marker-end: url(#arrow); }
    .edge-label { font-family: monospace; font-size: 13px; fill: #d97706; font-weight: bold; }
    .perm-label { font-family: sans-serif; font-size: 11px; fill: #15803d; font-weight: bold; }
  </style>

  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#64748b" />
    </marker>
  </defs>

  <text x="410" y="30" class="title" text-anchor="middle">Обхід скінченного автомата (DFA) для маски /var/log/** r</text>

  <!-- Node 0: Root -->
  <circle cx="70" cy="130" r="28" class="node" />
  <text x="70" y="135" class="node-text" text-anchor="middle">S0</text>
  <text x="70" y="175" font-family="sans-serif" font-size="11" fill="#64748b" text-anchor="middle">Start</text>

  <!-- Node 1: /var -->
  <circle cx="230" cy="130" r="28" class="node" />
  <text x="230" y="135" class="node-text" text-anchor="middle">S1</text>
  <text x="230" y="175" font-family="sans-serif" font-size="11" fill="#64748b" text-anchor="middle">/var</text>

  <!-- Node 2: /var/log -->
  <circle cx="410" cy="130" r="28" class="node" />
  <text x="410" y="135" class="node-text" text-anchor="middle">S2</text>
  <text x="410" y="175" font-family="sans-serif" font-size="11" fill="#64748b" text-anchor="middle">/var/log</text>

  <!-- Node 3: /var/log/** -->
  <circle cx="610" cy="130" r="28" class="node-accept" />
  <circle cx="610" cy="130" r="23" fill="none" stroke="#16a34a" stroke-width="1.5" />
  <text x="610" y="135" class="node-text" text-anchor="middle">S3</text>
  <text x="610" y="175" class="perm-label" text-anchor="middle">ACCEPT [r]</text>

  <!-- Transitions -->
  <line x1="98" y1="130" x2="202" y2="130" class="edge" />
  <text x="150" y="120" class="edge-label" text-anchor="middle">"/var/"</text>

  <line x1="258" y1="130" x2="382" y2="130" class="edge" />
  <text x="320" y="120" class="edge-label" text-anchor="middle">"log/"</text>

  <line x1="438" y1="130" x2="582" y2="130" class="edge" />
  <text x="510" y="120" class="edge-label" text-anchor="middle">"**"</text>

  <!-- Self loop on S3 -->
  <path d="M 600,103 C 580,60 640,60 620,103" fill="none" class="edge" />
  <text x="610" y="52" class="edge-label" text-anchor="middle">any char</text>
</svg>"""
    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, "apparmor-dfa-matching.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("Wrote:", out_path)

if __name__ == "__main__":
    render_vfs_path_resolution()
    render_dfa_matching()
