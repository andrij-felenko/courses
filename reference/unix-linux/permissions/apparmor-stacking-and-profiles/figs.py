import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, "img")

def generate_apparmor_stacking():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 450" width="100%" height="100%">
  <defs>
    <style>
      .bg-main { fill: #f8f9fa; stroke: #cbd5e1; stroke-width: 2; rx: 12; }
      .bg-host { fill: #eff6ff; stroke: #3b82f6; stroke-width: 2; rx: 10; }
      .bg-ns { fill: #f0fdf4; stroke: #22c55e; stroke-width: 2; rx: 8; }
      .bg-profile { fill: #fffbeb; stroke: #f59e0b; stroke-width: 1.5; rx: 6; }
      .bg-stack { fill: #fef2f2; stroke: #ef4444; stroke-width: 2; rx: 6; }
      .title-main { font-family: system-ui, -apple-system, sans-serif; font-size: 16px; font-weight: 700; fill: #0f172a; }
      .title-sub { font-family: system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 600; fill: #1e3a8a; }
      .title-ns { font-family: system-ui, -apple-system, sans-serif; font-size: 13px; font-weight: 600; fill: #14532d; }
      .txt-body { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; fill: #334155; }
      .txt-code { font-family: ui-monospace, SFMono-Regular, monospace; font-size: 11px; fill: #b91c1c; font-weight: 600; }
    </style>
  </defs>
  <g transform="translate(0, 0)">
    <!-- Root Host OS -->
    <rect x="20" y="20" width="860" height="410" class="bg-main" />
    <text x="40" y="48" class="title-main">Хостове середовище Linux (AppArmor Root Namespace: default)</text>

    <!-- Host Container Engine Profile -->
    <rect x="40" y="70" width="820" height="340" class="bg-host" />
    <text x="60" y="96" class="title-sub">Профіль контейнерного рушія хоста: docker-default / lxc-container-default</text>
    <text x="60" y="118" class="txt-body">Обмежує небезпечні файлові системи (/proc, /sys), моунти та capability системних викликів</text>

    <!-- Nested AppArmor Namespace -->
    <rect x="60" y="135" width="780" height="255" class="bg-ns" />
    <text x="80" y="160" class="title-ns">Вкладений простір імен AppArmor: :container-ns-1://</text>
    <text x="80" y="180" class="txt-body">Повна ізоляція внутрішніх профілів контейнера від глобального простору хоста</text>

    <!-- Profile A inside NS -->
    <rect x="80" y="198" width="360" height="175" class="bg-profile" />
    <text x="95" y="222" class="title-sub">Внутрішній профіль: usr.sbin.nginx</text>
    <text x="95" y="246" class="txt-body">Дозволяє лише /etc/nginx, /var/log/nginx</text>
    <text x="95" y="268" class="txt-body">Забороняє виконання файлів у /tmp</text>
    
    <!-- Stack A result -->
    <rect x="95" y="290" width="330" height="68" class="bg-stack" />
    <text x="105" y="314" class="txt-body">Підсумкова активна мітка ядра:</text>
    <text x="105" y="340" class="txt-code">docker-default //&amp; :container-ns-1://usr.sbin.nginx</text>

    <!-- Profile B inside NS -->
    <rect x="460" y="198" width="360" height="175" class="bg-profile" />
    <text x="475" y="222" class="title-sub">Внутрішній профіль: usr.sbin.mysqld</text>
    <text x="475" y="246" class="txt-body">Дозволяє лише /var/lib/mysql, /etc/mysql</text>
    <text x="475" y="268" class="txt-body">Забороняє мережевий доступ поза портом 3306</text>

    <!-- Stack B result -->
    <rect x="475" y="290" width="330" height="68" class="bg-stack" />
    <text x="485" y="314" class="txt-body">Підсумкова активна мітка ядра:</text>
    <text x="485" y="340" class="txt-code">docker-default //&amp; :container-ns-1://usr.sbin.mysqld</text>
  </g>
</svg>
"""
    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, "apparmor-stacking.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {out_path}")

def generate_apparmor_label_intersection():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 420" width="100%" height="100%">
  <defs>
    <style>
      .txt-title { font-family: system-ui, -apple-system, sans-serif; font-size: 15px; font-weight: 700; fill: #0f172a; }
      .txt-sub { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; fill: #475569; }
      .txt-core { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: 700; fill: #991b1b; }
      .lbl-set { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: 600; }
    </style>
  </defs>
  <g transform="translate(0, 0)">
    <!-- Title -->
    <text x="30" y="30" class="txt-title">Перетин множин дозволів при стекуванні 3 профілів (Permitted Intersection)</text>
    <text x="30" y="52" class="txt-sub">Операція дозволяється ядрам лише якщо вона належить центральній області перетину</text>

    <!-- Circle 1: Host Profile -->
    <circle cx="310" cy="220" r="120" fill="#3b82f6" fill-opacity="0.18" stroke="#2563eb" stroke-width="2" />
    <text x="200" y="90" class="lbl-set" fill="#1d4ed8">Permitted(P_host)</text>

    <!-- Circle 2: Namespace Container Profile -->
    <circle cx="510" cy="220" r="120" fill="#22c55e" fill-opacity="0.18" stroke="#16a34a" stroke-width="2" />
    <text x="530" y="90" class="lbl-set" fill="#15803d">Permitted(P_container)</text>

    <!-- Circle 3: Service Internal Profile -->
    <circle cx="410" cy="265" r="105" fill="#eab308" fill-opacity="0.2" stroke="#ca8a04" stroke-width="2" />
    <text x="360" y="395" class="lbl-set" fill="#a16207">Permitted(P_service)</text>

    <!-- Core Intersection Highlight -->
    <path d="M 410,180 A 120,120 0 0,1 465,220 A 105,105 0 0,1 410,290 A 120,120 0 0,1 355,220 A 105,105 0 0,1 410,180 Z" 
          fill="#ef4444" fill-opacity="0.55" stroke="#b91c1c" stroke-width="2" />

    <!-- Annotation for Core inside center of intersection -->
    <text x="360" y="226" class="txt-core">Permitted(Stack)</text>
    <text x="355" y="246" class="txt-sub" fill="#7f1d1d">P_host ∩ P_ct ∩ P_srv</text>

    <!-- Outside Denied indicators -->
    <text x="30" y="220" class="txt-sub" fill="#dc2626">Denied: Заборонено в P_host</text>
    <text x="650" y="220" class="txt-sub" fill="#dc2626">Denied: Заборонено в P_container</text>
  </g>
</svg>
"""
    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, "apparmor-label-intersection.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {out_path}")

if __name__ == '__main__':
    generate_apparmor_stacking()
    generate_apparmor_label_intersection()
