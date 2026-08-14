import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "img")

def render_domain_tree():
    svg = """<svg viewBox="0 0 860 440" width="860" height="440" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #0f172a; }
    .box-kernel { fill: #f1f5f9; stroke: #475569; stroke-width: 1.5; rx: 6; }
    .box-domain { fill: #e0f2fe; stroke: #0284c7; stroke-width: 1.5; rx: 6; }
    .box-enforce { fill: #dcfce7; stroke: #16a34a; stroke-width: 1.5; rx: 6; }
    .box-learn { fill: #fef9c3; stroke: #ca8a04; stroke-width: 1.5; rx: 6; }
    .text-title { font-family: monospace; font-size: 13px; font-weight: bold; fill: #0f172a; }
    .text-sub { font-family: sans-serif; font-size: 11px; fill: #475569; }
    .text-mode { font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #15803d; }
    .text-mode-learn { font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #a16207; }
    .arrow { stroke: #64748b; stroke-width: 1.8; marker-end: url(#arrowhead); }
    .arrow-text { font-family: monospace; font-size: 11px; fill: #2563eb; font-weight: bold; }
  </style>

  <defs>
    <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#64748b" />
    </marker>
  </defs>

  <!-- Title -->
  <text x="430" y="28" class="title" text-anchor="middle">Ієрархічне дерево доменів TOMOYO Linux (Domain Tree)</text>

  <!-- Node 0: Root Kernel -->
  <rect x="330" y="55" width="200" height="50" class="box-kernel" />
  <text x="430" y="76" class="text-title" text-anchor="middle">&lt;kernel&gt;</text>
  <text x="430" y="93" class="text-sub" text-anchor="middle">Ядро під час завантаження</text>

  <!-- Node 1: init -->
  <rect x="310" y="145" width="240" height="55" class="box-domain" />
  <text x="430" y="167" class="text-title" text-anchor="middle">&lt;kernel&gt; /sbin/init</text>
  <text x="430" y="186" class="text-sub" text-anchor="middle">Процес PID 1 (systemd)</text>

  <!-- Node 2a: sshd -->
  <rect x="50" y="255" width="340" height="60" class="box-enforce" />
  <text x="220" y="277" class="text-title" text-anchor="middle">&lt;kernel&gt; /sbin/init /usr/sbin/sshd</text>
  <text x="220" y="294" class="text-sub" text-anchor="middle">SSH Daemon (Демон авторизації)</text>
  <text x="220" y="307" class="text-mode" text-anchor="middle">Profile 3: Enforcing Mode</text>

  <!-- Node 2b: nginx -->
  <rect x="470" y="255" width="340" height="60" class="box-learn" />
  <text x="640" y="277" class="text-title" text-anchor="middle">&lt;kernel&gt; /sbin/init /usr/sbin/nginx</text>
  <text x="640" y="294" class="text-sub" text-anchor="middle">Nginx Web Server</text>
  <text x="640" y="307" class="text-mode-learn" text-anchor="middle">Profile 1: Learning Mode</text>

  <!-- Node 3: sshd -> bash -->
  <rect x="30" y="365" width="380" height="60" class="box-enforce" />
  <text x="220" y="387" class="text-title" text-anchor="middle">... /usr/sbin/sshd /bin/bash</text>
  <text x="220" y="404" class="text-sub" text-anchor="middle">Користувацька оболонка SSH-сесії</text>
  <text x="220" y="417" class="text-mode" text-anchor="middle">Profile 3: Enforcing Mode</text>

  <!-- Connectors -->
  <!-- kernel -> init -->
  <line x1="430" y1="105" x2="430" y2="145" class="arrow" />
  <text x="510" y="128" class="arrow-text" text-anchor="middle">execve("/sbin/init")</text>

  <!-- init -> sshd -->
  <line x1="370" y1="200" x2="220" y2="255" class="arrow" />
  <text x="250" y="224" class="arrow-text" text-anchor="middle">execve("/usr/sbin/sshd")</text>

  <!-- init -> nginx -->
  <line x1="490" y1="200" x2="640" y2="255" class="arrow" />
  <text x="610" y="224" class="arrow-text" text-anchor="middle">execve("/usr/sbin/nginx")</text>

  <!-- sshd -> bash -->
  <line x1="220" y1="315" x2="220" y2="365" class="arrow" />
  <text x="300" y="343" class="arrow-text" text-anchor="middle">execve("/bin/bash")</text>
</svg>"""
    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, "tomoyo-domain-tree.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("Wrote:", out_path)

def render_vfs_path_hooks():
    svg = """<svg viewBox="0 0 860 380" width="860" height="380" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #0f172a; }
    .box-title { font-family: sans-serif; font-size: 14px; font-weight: bold; fill: #0f172a; }
    .label { font-family: sans-serif; font-size: 12px; fill: #334155; }
    .code { font-family: monospace; font-size: 11px; fill: #0284c7; font-weight: bold; }
    .arrow { stroke: #475569; stroke-width: 1.8; marker-end: url(#arrowhead); }
    .bg-user { fill: #eff6ff; stroke: #3b82f6; stroke-width: 1.5; rx: 6; }
    .bg-vfs { fill: #f0fdf4; stroke: #22c55e; stroke-width: 1.5; rx: 6; }
    .bg-lsm { fill: #fefce8; stroke: #eab308; stroke-width: 1.5; rx: 6; }
    .bg-decision { fill: #fcf6bd; stroke: #d97706; stroke-width: 1.5; rx: 6; }
  </style>

  <defs>
    <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#475569" />
    </marker>
  </defs>

  <!-- Title -->
  <text x="430" y="28" class="title" text-anchor="middle">Відновлення канонічного шляху VFS та перевірка хуками TOMOYO LSM</text>

  <!-- User Space -->
  <rect x="20" y="55" width="180" height="290" class="bg-user" />
  <text x="110" y="80" class="box-title" text-anchor="middle">User Space</text>
  
  <rect x="35" y="105" width="150" height="65" fill="#ffffff" stroke="#93c5fd" rx="4" />
  <text x="110" y="126" class="label" text-anchor="middle">Процес домену</text>
  <text x="110" y="143" class="code" text-anchor="middle">openat(dfd, path)</text>
  <text x="110" y="158" class="label" font-size="10" text-anchor="middle">UID=0 або UID=1000</text>

  <rect x="35" y="245" width="150" height="75" fill="#ffffff" stroke="#93c5fd" rx="4" />
  <text x="110" y="267" class="label" text-anchor="middle">Результат системного</text>
  <text x="110" y="283" class="label" text-anchor="middle">виклику</text>
  <text x="110" y="302" class="code" text-anchor="middle">fd &gt;= 0 / -EACCES</text>

  <!-- Kernel VFS Layer -->
  <rect x="230" y="55" width="220" height="290" class="bg-vfs" />
  <text x="340" y="80" class="box-title" text-anchor="middle">Kernel VFS Layer</text>

  <rect x="245" y="105" width="190" height="55" fill="#ffffff" stroke="#86efac" rx="4" />
  <text x="340" y="126" class="label" text-anchor="middle">Обробник виклику</text>
  <text x="340" y="146" class="code" text-anchor="middle">do_sys_openat2()</text>

  <rect x="245" y="185" width="190" height="75" fill="#ffffff" stroke="#86efac" rx="4" />
  <text x="340" y="206" class="label" text-anchor="middle">Розлучення VFS-структур</text>
  <text x="340" y="224" class="code" text-anchor="middle">struct path { dentry, mnt }</text>
  <text x="340" y="244" class="code" text-anchor="middle">tomoyo_realpath()</text>

  <!-- TOMOYO LSM Engine -->
  <rect x="480" y="55" width="200" height="290" class="bg-lsm" />
  <text x="580" y="80" class="box-title" text-anchor="middle">TOMOYO LSM Engine</text>

  <rect x="495" y="105" width="170" height="55" fill="#ffffff" stroke="#fde047" rx="4" />
  <text x="580" y="126" class="label" text-anchor="middle">LSM Hook VFS</text>
  <text x="580" y="146" class="code" text-anchor="middle">security_path_open()</text>

  <rect x="495" y="185" width="170" height="75" fill="#ffffff" stroke="#fde047" rx="4" />
  <text x="580" y="206" class="label" text-anchor="middle">Зіставлення з доменом</text>
  <text x="580" y="224" class="code" text-anchor="middle">tomoyo_path_perm()</text>
  <text x="580" y="244" class="label" font-size="10" text-anchor="middle">Match pattern in domain</text>

  <!-- Decision -->
  <rect x="710" y="55" width="130" height="290" class="bg-decision" />
  <text x="775" y="80" class="box-title" text-anchor="middle">Режим / Дія</text>

  <rect x="720" y="100" width="110" height="40" fill="#dcfce7" stroke="#16a34a" rx="4" />
  <text x="775" y="124" class="label" text-anchor="middle" font-weight="bold" fill="#15803d">ALLOW (0)</text>

  <rect x="720" y="150" width="110" height="40" fill="#fef9c3" stroke="#ca8a04" rx="4" />
  <text x="775" y="174" class="label" text-anchor="middle" font-weight="bold" fill="#854d0e">LEARN (+rule)</text>

  <rect x="720" y="200" width="110" height="40" fill="#ffedd5" stroke="#ea580c" rx="4" />
  <text x="775" y="224" class="label" text-anchor="middle" font-weight="bold" fill="#9a3412">AUDIT (log)</text>

  <rect x="720" y="250" width="110" height="40" fill="#fee2e2" stroke="#dc2626" rx="4" />
  <text x="775" y="274" class="label" text-anchor="middle" font-weight="bold" fill="#b91c1c">DENY (-EACCES)</text>

  <!-- Connectors -->
  <line x1="185" y1="135" x2="245" y2="135" class="arrow" />
  <line x1="340" y1="160" x2="340" y2="185" class="arrow" />
  <line x1="435" y1="220" x2="495" y2="220" class="arrow" />
  <line x1="580" y1="160" x2="580" y2="185" class="arrow" />
  <line x1="665" y1="220" x2="720" y2="120" class="arrow" />
  <line x1="665" y1="220" x2="720" y2="170" class="arrow" />
  <line x1="665" y1="220" x2="720" y2="220" class="arrow" />
  <line x1="665" y1="220" x2="720" y2="270" class="arrow" />
  <line x1="720" y1="270" x2="185" y2="280" class="arrow" stroke-dasharray="4,4" />
</svg>"""
    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, "tomoyo-vfs-path-hooks.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("Wrote:", out_path)

if __name__ == "__main__":
    render_domain_tree()
    render_vfs_path_hooks()
