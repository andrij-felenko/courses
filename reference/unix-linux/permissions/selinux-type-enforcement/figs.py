import os

def render():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    # ----------------------------------------------------
    # Figure 1: selinux-te.svg
    # ----------------------------------------------------
    svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 420" width="800" height="420">
  <style>
    .bg { fill: #fcfcfd; }
    .box-subject { fill: #eef2ff; stroke: #6366f1; stroke-width: 2; rx: 8px; }
    .box-object { fill: #f0fdf4; stroke: #22c55e; stroke-width: 2; rx: 8px; }
    .box-policy { fill: #fff7ed; stroke: #f97316; stroke-width: 2; rx: 8px; }
    .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 18px; font-weight: bold; fill: #0f172a; }
    .heading { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 15px; font-weight: bold; fill: #1e293b; }
    .subtext { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; fill: #475569; }
    .code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 12px; fill: #9a3412; }
    .label-blue { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; font-weight: bold; fill: #4338ca; }
    .label-orange { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; font-weight: bold; fill: #c2410c; }
    .label-green { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; font-weight: bold; fill: #15803d; }
    .arrow { fill: none; stroke-width: 2.5; marker-end: url(#arrowhead); }
    .arrow-blue { stroke: #6366f1; }
    .arrow-orange { stroke: #f97316; stroke-dasharray: 6,4; }
    .arrow-green { stroke: #22c55e; }
  </style>

  <defs>
    <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <polygon points="0 0, 8 4, 0 8" fill="#475569" />
    </marker>
  </defs>

  <rect width="800" height="420" class="bg"/>

  <text x="400" y="32" class="title" text-anchor="middle">Модель SELinux Type Enforcement (TE)</text>

  <!-- Subject Box -->
  <rect x="40" y="70" width="220" height="120" class="box-subject"/>
  <text x="150" y="98" class="heading" text-anchor="middle">Суб'єкт (Процес)</text>
  <text x="150" y="125" class="subtext" text-anchor="middle">PID: 1420 (httpd)</text>
  <text x="150" y="148" class="label-blue" text-anchor="middle">Домен: httpd_t</text>
  <text x="150" y="170" class="subtext" text-anchor="middle">Контекст: system_u:...:s0</text>

  <!-- Object Box -->
  <rect x="540" y="70" width="220" height="120" class="box-object"/>
  <text x="650" y="98" class="heading" text-anchor="middle">Об'єкт (Файл)</text>
  <text x="650" y="125" class="subtext" text-anchor="middle">Шлях: /var/www/index.html</text>
  <text x="650" y="148" class="label-green" text-anchor="middle">Тип: httpd_sys_content_t</text>
  <text x="650" y="170" class="subtext" text-anchor="middle">Клас: file</text>

  <!-- Access Request Arrow -->
  <path d="M 260 130 L 530 130" class="arrow arrow-blue"/>
  <text x="400" y="118" class="label-blue" text-anchor="middle">Виклик VFS open() [read, getattr]</text>

  <!-- Policy Engine Box -->
  <rect x="230" y="250" width="340" height="130" class="box-policy"/>
  <text x="400" y="278" class="heading" text-anchor="middle">Політика безпеки (TE Rule Base)</text>
  <text x="400" y="305" class="code" text-anchor="middle">allow httpd_t httpd_sys_content_t : file</text>
  <text x="400" y="325" class="code" text-anchor="middle">{ read getattr ioctl lock };</text>
  <text x="400" y="358" class="label-orange" text-anchor="middle">Рішення: доступ дозволено (повернено 0)</text>

  <!-- Policy Check Lines -->
  <path d="M 150 190 L 150 315 L 220 315" class="arrow arrow-orange"/>
  <path d="M 650 190 L 650 315 L 580 315" class="arrow arrow-orange"/>

</svg>"""

    filepath1 = os.path.join(img_dir, "selinux-te.svg")
    with open(filepath1, "w", encoding="utf-8") as f:
        f.write(svg1)
    print(f"Generated {filepath1}")

    # ----------------------------------------------------
    # Figure 2: avc-lookup-path.svg
    # ----------------------------------------------------
    svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 460" width="820" height="460">
  <style>
    .bg { fill: #f8fafc; }
    .box-hook { fill: #f1f5f9; stroke: #64748b; stroke-width: 2; rx: 6px; }
    .box-avc { fill: #eff6ff; stroke: #3b82f6; stroke-width: 2; rx: 6px; }
    .box-secserver { fill: #fef3c7; stroke: #d97706; stroke-width: 2; rx: 6px; }
    .box-audit { fill: #fef2f2; stroke: #ef4444; stroke-width: 2; rx: 6px; }
    .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 18px; font-weight: bold; fill: #0f172a; }
    .heading { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; fill: #1e293b; }
    .subtext { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; fill: #475569; }
    .code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 11px; fill: #7c2d12; }
    .label-fast { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; fill: #15803d; }
    .label-slow { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; fill: #b45309; }
    .label-deny { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; fill: #dc2626; }
    .arrow { fill: none; stroke-width: 2; marker-end: url(#arrowhead2); }
    .arrow-green { stroke: #16a34a; }
    .arrow-amber { stroke: #d97706; }
    .arrow-red { stroke: #dc2626; stroke-dasharray: 4,4; }
  </style>

  <defs>
    <marker id="arrowhead2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <polygon points="0 0, 8 4, 0 8" fill="#475569" />
    </marker>
  </defs>

  <rect width="820" height="460" class="bg"/>

  <text x="410" y="32" class="title" text-anchor="middle">Шлях виконання avc_has_perm() та кешування AVC</text>

  <!-- Step 1: LSM Hook -->
  <rect x="30" y="70" width="210" height="110" class="box-hook"/>
  <text x="135" y="98" class="heading" text-anchor="middle">1. LSM Hook у ядрі</text>
  <text x="135" y="122" class="code" text-anchor="middle">selinux_file_open()</text>
  <text x="135" y="145" class="subtext" text-anchor="middle">Отримання SID суб'єкта</text>
  <text x="135" y="165" class="subtext" text-anchor="middle">та SID об'єкта</text>

  <!-- Step 2: AVC Cache Lookup -->
  <rect x="300" y="70" width="220" height="140" class="box-avc"/>
  <text x="410" y="98" class="heading" text-anchor="middle">2. Access Vector Cache</text>
  <text x="410" y="122" class="code" text-anchor="middle">avc_has_perm(ssid, tsid...)</text>
  <text x="410" y="148" class="subtext" text-anchor="middle">Хеш-пошук запису AVC</text>
  <text x="410" y="170" class="label-fast" text-anchor="middle">Cache Hit (типовий шлях)</text>
  <text x="410" y="190" class="subtext" text-anchor="middle">Швидка бітова маска</text>

  <!-- Hook to AVC Arrow -->
  <path d="M 240 125 L 290 125" class="arrow"/>

  <!-- Fast Path Return Arrow -->
  <path d="M 410 210 L 410 400 L 135 400 L 135 190" class="arrow arrow-green"/>
  <text x="270" y="420" class="label-fast" text-anchor="middle">Повернення результату доступу (0 або -EACCES)</text>

  <!-- Step 3: Security Server (Cache Miss) -->
  <rect x="570" y="70" width="220" height="140" class="box-secserver"/>
  <text x="680" y="98" class="heading" text-anchor="middle">3. Security Server</text>
  <text x="680" y="122" class="code" text-anchor="middle">security_compute_av()</text>
  <text x="680" y="148" class="subtext" text-anchor="middle">Повільний обчислювач</text>
  <text x="680" y="170" class="label-slow" text-anchor="middle">Cache Miss</text>
  <text x="680" y="190" class="subtext" text-anchor="middle">Обчислення вектора &amp; запис у AVC</text>

  <!-- AVC to Security Server Arrow -->
  <path d="M 520 125 L 560 125" class="arrow arrow-amber"/>

  <!-- Security Server back to AVC Arrow -->
  <path d="M 570 160 L 530 160" class="arrow arrow-amber"/>

  <!-- Step 4: Audit Logging -->
  <rect x="420" y="270" width="370" height="110" class="box-audit"/>
  <text x="605" y="298" class="heading" text-anchor="middle">4. Логування аудит-подій (AVC Denial)</text>
  <text x="605" y="322" class="code" text-anchor="middle">type=AVC msg=audit(...): avc: denied</text>
  <text x="605" y="344" class="subtext" text-anchor="middle">Запис у /var/log/audit/audit.log</text>
  <text x="605" y="364" class="label-deny" text-anchor="middle">якщо дозвіл не наданий і немає правила dontaudit</text>

  <!-- AVC/SecServer to Audit Arrow -->
  <path d="M 470 210 L 470 260" class="arrow arrow-red"/>

</svg>"""

    filepath2 = os.path.join(img_dir, "avc-lookup-path.svg")
    with open(filepath2, "w", encoding="utf-8") as f:
        f.write(svg2)
    print(f"Generated {filepath2}")

if __name__ == "__main__":
    render()
