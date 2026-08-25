import os
import sys

# Ensure img directory exists
os.makedirs('img', exist_ok=True)

svg_id_mapping = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 420" width="100%" height="100%">
  <defs>
    <style>
      .bg { fill: #ffffff; }
      .box-host { fill: #f1f5f9; stroke: #64748b; stroke-width: 2; rx: 8px; }
      .box-ns { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 8px; }
      .box-helper { fill: #fef3c7; stroke: #d97706; stroke-width: 2; rx: 6px; }
      .title { font-family: system-ui, -apple-system, sans-serif; font-size: 18px; font-weight: bold; fill: #0f172a; }
      .subtitle { font-family: system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: bold; fill: #334155; }
      .text-main { font-family: system-ui, -apple-system, sans-serif; font-size: 13px; fill: #1e293b; }
      .text-sub { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; fill: #475569; font-style: italic; }
      .text-code { font-family: monospace; font-size: 12px; fill: #0f172a; font-weight: bold; }
      .arrow { stroke: #2563eb; stroke-width: 2; marker-end: url(#arrowhead); fill: none; }
      .arrow-orange { stroke: #d97706; stroke-width: 2; stroke-dasharray: 4 4; marker-end: url(#arrowhead-orange); fill: none; }
    </style>
    <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#2563eb" />
    </marker>
    <marker id="arrowhead-orange" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#d97706" />
    </marker>
  </defs>

  <rect width="850" height="420" class="bg" />

  <!-- Host Namespace Box -->
  <rect x="30" y="40" width="370" height="340" class="box-host" />
  <text x="215" y="70" class="subtitle" text-anchor="middle">Хостовий User Namespace (init_user_ns)</text>

  <rect x="50" y="95" width="330" height="70" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" rx="4" />
  <text x="65" y="120" class="text-main">Непривілейований користувач: <tspan class="text-code">alice</tspan></text>
  <text x="65" y="145" class="text-main">Хостовий UID: <tspan class="text-code">1000</tspan></text>

  <rect x="50" y="185" width="330" height="85" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" rx="4" />
  <text x="65" y="208" class="text-main">Делегований пул у <tspan class="text-code">/etc/subuid</tspan>:</text>
  <text x="65" y="230" class="text-code">alice:100000:65536</text>
  <text x="65" y="252" class="text-sub">(UIDs 100000..165535 виділено alice)</text>

  <rect x="50" y="290" width="330" height="70" class="box-helper" />
  <text x="215" y="315" class="subtitle" text-anchor="middle">Setuid Helper: newuidmap</text>
  <text x="215" y="340" class="text-sub" text-anchor="middle">Записує в /proc/[pid]/uid_map від імені root</text>

  <!-- Container Namespace Box -->
  <rect x="450" y="40" width="370" height="340" class="box-ns" />
  <text x="635" y="70" class="subtitle" text-anchor="middle">Контейнерний User Namespace</text>

  <rect x="470" y="95" width="330" height="70" fill="#ffffff" stroke="#93c5fd" stroke-width="1" rx="4" />
  <text x="485" y="120" class="text-main">Внутрішній Root: <tspan class="text-code">root (UID 0)</tspan></text>
  <text x="485" y="145" class="text-main">Повні привілеї всередині контейнера</text>

  <rect x="470" y="185" width="330" height="175" fill="#ffffff" stroke="#93c5fd" stroke-width="1" rx="4" />
  <text x="485" y="210" class="text-main">Таблиця відображення (<tspan class="text-code">uid_map</tspan>):</text>
  <text x="485" y="240" class="text-code">0      1000       1</text>
  <text x="485" y="260" class="text-sub">→ UID 0 (root) ↔ UID 1000 (alice)</text>
  <text x="485" y="295" class="text-code">1      100000     65536</text>
  <text x="485" y="315" class="text-sub">→ UID 1..65536 ↔ UID 100000..165535</text>

  <!-- Mapping Arrows -->
  <path d="M 380 130 L 470 130" class="arrow" />
  <path d="M 380 230 L 470 290" class="arrow" />
  <path d="M 215 290 L 215 270" class="arrow-orange" />
</svg>
"""

svg_stack_architecture = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 560" width="100%" height="100%">
  <defs>
    <style>
      .bg { fill: #ffffff; }
      .layer-bg { fill: #f8fafc; stroke: #cbd5e1; stroke-width: 1.5; rx: 8px; }
      .box-comp { fill: #ffffff; stroke: #64748b; stroke-width: 1.5; rx: 6px; }
      .box-net { fill: #f0fdf4; stroke: #16a34a; stroke-width: 1.5; rx: 6px; }
      .box-fs { fill: #fff7ed; stroke: #ea580c; stroke-width: 1.5; rx: 6px; }
      .box-cpu { fill: #faf5ff; stroke: #9333ea; stroke-width: 1.5; rx: 6px; }
      .title { font-family: system-ui, -apple-system, sans-serif; font-size: 15px; font-weight: bold; fill: #0f172a; }
      .subtitle { font-family: system-ui, -apple-system, sans-serif; font-size: 13px; font-weight: bold; fill: #334155; }
      .text-main { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; fill: #1e293b; }
      .text-sub { font-family: system-ui, -apple-system, sans-serif; font-size: 11px; fill: #64748b; }
      .arrow { stroke: #475569; stroke-width: 1.5; marker-end: url(#arr); fill: none; }
    </style>
    <marker id="arr" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#475569" />
    </marker>
  </defs>

  <rect width="850" height="560" class="bg" />

  <!-- Management Layer -->
  <rect x="30" y="20" width="790" height="105" class="layer-bg" />
  <text x="50" y="48" class="title">Рівень оркестрації (User Space / UID 1000)</text>
  <rect x="50" y="65" width="230" height="45" class="box-comp" />
  <text x="165" y="92" class="text-main" text-anchor="middle">Podman CLI / Rootless Docker</text>

  <rect x="310" y="65" width="230" height="45" class="box-comp" />
  <text x="425" y="92" class="text-main" text-anchor="middle">RootlessKit / Conmon</text>

  <rect x="570" y="65" width="230" height="45" class="box-comp" />
  <text x="685" y="92" class="text-main" text-anchor="middle">OCI Runtime (crun / runc)</text>

  <!-- Subsystems Layer -->
  <rect x="30" y="155" width="790" height="210" class="layer-bg" />
  <text x="50" y="182" class="title">Підсистеми обслуговування</text>

  <!-- Storage -->
  <rect x="50" y="210" width="230" height="140" class="box-fs" />
  <text x="165" y="235" class="subtitle" text-anchor="middle">Файлова система</text>
  <text x="65" y="265" class="text-main">• fuse-overlayfs (FUSE)</text>
  <text x="65" y="290" class="text-main">• Native OverlayFS (userxattr)</text>
  <text x="65" y="315" class="text-sub">Зсув UID/GID при записі</text>

  <!-- Network -->
  <rect x="310" y="210" width="230" height="140" class="box-net" />
  <text x="425" y="235" class="subtitle" text-anchor="middle">Мережевий стек</text>
  <text x="325" y="265" class="text-main">• slirp4netns (Userspace TCP)</text>
  <text x="325" y="290" class="text-main">• pasta (Socket Pass-Through)</text>
  <text x="325" y="315" class="text-sub">TAP-інтерфейс без CAP_NET_ADMIN</text>

  <!-- Resources -->
  <rect x="570" y="210" width="230" height="140" class="box-cpu" />
  <text x="685" y="235" class="subtitle" text-anchor="middle">Контроль ресурсів</text>
  <text x="585" y="265" class="text-main">• Cgroups v2 (Unified Hierarchy)</text>
  <text x="585" y="290" class="text-main">• Systemd User Session</text>
  <text x="585" y="315" class="text-sub">user.slice / dbus delegation</text>

  <!-- Kernel Layer -->
  <rect x="30" y="395" width="790" height="145" class="layer-bg" style="fill: #f1f5f9; stroke: #475569;" />
  <text x="50" y="425" class="title">Ядро Linux (Kernel &amp; Namespaces)</text>
  <text x="60" y="455" class="text-main">User Namespaces (CLONE_NEWUSER) | Net Namespaces (CLONE_NEWNET) | Mount Namespaces (CLONE_NEWNS)</text>
  <text x="60" y="485" class="text-main">VFS &amp; Subuid Validation (newuidmap / newgidmap) | Seccomp-BPF &amp; LSM Hooks</text>

  <!-- Connectors starting from bottom edge of layer 1 boxes to top edge of layer 2 boxes -->
  <path d="M 165 200 L 165 210" class="arrow" />
  <path d="M 425 200 L 425 210" class="arrow" />
  <path d="M 685 200 L 685 210" class="arrow" />

  <!-- Connectors between layer 2 and layer 3 -->
  <path d="M 165 350 L 165 395" class="arrow" />
  <path d="M 425 350 L 425 395" class="arrow" />
  <path d="M 685 350 L 685 395" class="arrow" />
</svg>
"""

with open('img/rootless-id-mapping.svg', 'w', encoding='utf-8') as f:
    f.write(svg_id_mapping)

with open('img/rootless-stack-architecture.svg', 'w', encoding='utf-8') as f:
    f.write(svg_stack_architecture)

print("SVGs generated successfully.")
