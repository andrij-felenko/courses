import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)

SVG_MAIN = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="800" height="400" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#2c3e50" />
    </marker>
  </defs>

  <!-- Background -->
  <rect width="800" height="400" fill="#fafafa" rx="8" />

  <!-- Windows App Box -->
  <rect x="30" y="40" width="210" height="320" rx="10" fill="#eef2f7" stroke="#34495e" stroke-width="2" />
  <text x="135" y="75" font-family="sans-serif" font-size="16" font-weight="bold" fill="#2c3e50" text-anchor="middle">Windows-застосунок</text>
  <text x="135" y="95" font-family="sans-serif" font-size="12" fill="#7f8c8d" text-anchor="middle">(Game / Engine)</text>

  <rect x="45" y="130" width="180" height="60" rx="6" fill="#ffffff" stroke="#2980b9" stroke-width="1.5" />
  <text x="135" y="155" font-family="sans-serif" font-size="13" font-weight="bold" fill="#2980b9" text-anchor="middle">WaitForMultipleObjects</text>
  <text x="135" y="175" font-family="sans-serif" font-size="11" fill="#7f8c8d" text-anchor="middle">(count, handles, wait_all)</text>

  <!-- Translation Arrow -->
  <path d="M 240 160 L 290 160" stroke="#2c3e50" stroke-width="2" fill="none" marker-end="url(#arrow)" />
  <text x="265" y="150" font-family="sans-serif" font-size="11" font-weight="bold" fill="#e67e22" text-anchor="middle">Wine / Proton</text>
  <text x="265" y="175" font-family="sans-serif" font-size="10" fill="#7f8c8d" text-anchor="middle">fsync layer</text>

  <!-- Userspace Futex Array Box -->
  <rect x="300" y="40" width="210" height="320" rx="10" fill="#fef9e7" stroke="#d35400" stroke-width="2" />
  <text x="405" y="75" font-family="sans-serif" font-size="16" font-weight="bold" fill="#d35400" text-anchor="middle">Простір користувача</text>

  <rect x="315" y="110" width="180" height="40" rx="5" fill="#ffffff" stroke="#f39c12" stroke-width="1.5" />
  <text x="405" y="135" font-family="sans-serif" font-size="12" font-weight="bold" fill="#d35400" text-anchor="middle">struct futex_waitv[N]</text>

  <rect x="320" y="170" width="80" height="35" rx="4" fill="#fdebd0" stroke="#e67e22" stroke-width="1" />
  <text x="360" y="192" font-family="sans-serif" font-size="11" fill="#7f8c8d" text-anchor="middle">uaddr1 (32b)</text>

  <rect x="410" y="170" width="80" height="35" rx="4" fill="#fdebd0" stroke="#e67e22" stroke-width="1" />
  <text x="450" y="192" font-family="sans-serif" font-size="11" fill="#7f8c8d" text-anchor="middle">uaddr2 (32b)</text>

  <text x="405" y="230" font-family="sans-serif" font-size="13" font-weight="bold" fill="#d35400" text-anchor="middle">sys_futex_waitv(...)</text>

  <!-- Syscall Arrow -->
  <path d="M 510 160 L 550 160" stroke="#2c3e50" stroke-width="2" fill="none" marker-end="url(#arrow)" />
  <text x="530" y="150" font-family="sans-serif" font-size="10" font-weight="bold" fill="#27ae60" text-anchor="middle">syscall</text>

  <!-- Kernel Space Box -->
  <rect x="560" y="40" width="210" height="320" rx="10" fill="#eaafaf" fill-opacity="0.2" stroke="#27ae60" stroke-width="2" />
  <text x="665" y="75" font-family="sans-serif" font-size="16" font-weight="bold" fill="#27ae60" text-anchor="middle">Ядро Linux (5.16+)</text>

  <rect x="575" y="110" width="180" height="40" rx="5" fill="#ffffff" stroke="#27ae60" stroke-width="1.5" />
  <text x="665" y="135" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1e8449" text-anchor="middle">futex_key → hash bucket</text>

  <rect x="575" y="170" width="180" height="50" rx="5" fill="#ffffff" stroke="#27ae60" stroke-width="1.5" />
  <text x="665" y="192" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1e8449" text-anchor="middle">futex_q enqueue</text>
  <text x="665" y="208" font-family="sans-serif" font-size="10" fill="#7f8c8d" text-anchor="middle">(hash bucket spinlocks)</text>

  <rect x="575" y="240" width="180" height="40" rx="5" fill="#d5f5e3" stroke="#27ae60" stroke-width="1.5" />
  <text x="665" y="265" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1e8449" text-anchor="middle">schedule() [SLEEP]</text>

  <!-- Wakeup notification -->
  <path d="M 665 290 L 665 330" stroke="#c0392b" stroke-width="2" stroke-dasharray="4,4" fill="none" marker-end="url(#arrow)" />
  <text x="665" y="348" font-family="sans-serif" font-size="11" font-weight="bold" fill="#c0392b" text-anchor="middle">FUTEX_WAKE → wakeup index</text>
</svg>
"""

SVG_HIST = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="800" height="360" viewBox="0 0 800 360" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow2" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#2c3e50" />
    </marker>
  </defs>

  <rect width="800" height="360" fill="#fafafa" rx="8" />

  <!-- Timeline Title -->
  <text x="400" y="35" font-family="sans-serif" font-size="16" font-weight="bold" fill="#2c3e50" text-anchor="middle">Еволюція емуляції синхронізації Windows у Linux</text>

  <!-- Step 1: wineserver -->
  <rect x="30" y="70" width="160" height="230" rx="8" fill="#ebedef" stroke="#7f8c8d" stroke-width="1.5" />
  <text x="110" y="95" font-family="sans-serif" font-size="14" font-weight="bold" fill="#2c3e50" text-anchor="middle">1. wineserver</text>
  <rect x="42" y="115" width="136" height="40" rx="4" fill="#ffffff" stroke="#95a5a6" />
  <text x="110" y="140" font-family="sans-serif" font-size="11" fill="#34495e" text-anchor="middle">IPC daemon</text>
  <text x="110" y="180" font-family="sans-serif" font-size="11" fill="#7f8c8d" text-anchor="middle">• Сокети / Pipe</text>
  <text x="110" y="200" font-family="sans-serif" font-size="11" fill="#7f8c8d" text-anchor="middle">• Перемикання контексту</text>
  <text x="110" y="220" font-family="sans-serif" font-size="11" fill="#c0392b" text-anchor="middle">• Повільний шлях</text>

  <!-- Step 2: esync -->
  <rect x="220" y="70" width="160" height="230" rx="8" fill="#e8f8f5" stroke="#1abc9c" stroke-width="1.5" />
  <text x="300" y="95" font-family="sans-serif" font-size="14" font-weight="bold" fill="#16a085" text-anchor="middle">2. esync</text>
  <rect x="232" y="115" width="136" height="40" rx="4" fill="#ffffff" stroke="#1abc9c" />
  <text x="300" y="140" font-family="sans-serif" font-size="11" fill="#16a085" text-anchor="middle">eventfd() + epoll</text>
  <text x="300" y="180" font-family="sans-serif" font-size="11" fill="#7f8c8d" text-anchor="middle">• Пряме очікування VFS</text>
  <text x="300" y="200" font-family="sans-serif" font-size="11" fill="#c0392b" text-anchor="middle">• Виснаження FD</text>
  <text x="300" y="220" font-family="sans-serif" font-size="11" fill="#c0392b" text-anchor="middle">• Оверхед sys_write</text>

  <!-- Step 3: fsync -->
  <rect x="410" y="70" width="160" height="230" rx="8" fill="#fef9e7" stroke="#f39c12" stroke-width="1.5" />
  <text x="490" y="95" font-family="sans-serif" font-size="14" font-weight="bold" fill="#d35400" text-anchor="middle">3. fsync (futex)</text>
  <rect x="422" y="115" width="136" height="40" rx="4" fill="#ffffff" stroke="#f39c12" />
  <text x="490" y="140" font-family="sans-serif" font-size="11" fill="#d35400" text-anchor="middle">Single futex_wait</text>
  <text x="490" y="180" font-family="sans-serif" font-size="11" fill="#7f8c8d" text-anchor="middle">• Fast-path у userspace</text>
  <text x="490" y="200" font-family="sans-serif" font-size="11" fill="#c0392b" text-anchor="middle">• Multi-wait = fallback</text>
  <text x="490" y="220" font-family="sans-serif" font-size="11" fill="#7f8c8d" text-anchor="middle">• Без виснаження FD</text>

  <!-- Step 4: futex2 -->
  <rect x="600" y="70" width="170" height="230" rx="8" fill="#eaf2f8" stroke="#2980b9" stroke-width="2" />
  <text x="685" y="95" font-family="sans-serif" font-size="14" font-weight="bold" fill="#2980b9" text-anchor="middle">4. futex_waitv</text>
  <rect x="612" y="115" width="146" height="40" rx="4" fill="#ffffff" stroke="#2980b9" />
  <text x="685" y="140" font-family="sans-serif" font-size="11" font-weight="bold" fill="#2980b9" text-anchor="middle">sys_futex_waitv()</text>
  <text x="685" y="180" font-family="sans-serif" font-size="11" fill="#27ae60" text-anchor="middle">• Нативний Multi-wait</text>
  <text x="685" y="200" font-family="sans-serif" font-size="11" fill="#27ae60" text-anchor="middle">• Мінімальна затримка</text>
  <text x="685" y="220" font-family="sans-serif" font-size="11" fill="#27ae60" text-anchor="middle">• Ядро Linux 5.16+</text>

  <!-- Connecting arrows -->
  <path d="M 190 185 L 220 185" stroke="#2c3e50" stroke-width="1.5" fill="none" marker-end="url(#arrow2)" />
  <path d="M 380 185 L 410 185" stroke="#2c3e50" stroke-width="1.5" fill="none" marker-end="url(#arrow2)" />
  <path d="M 570 185 L 600 185" stroke="#2c3e50" stroke-width="1.5" fill="none" marker-end="url(#arrow2)" />
</svg>
"""

def render():
    main_path = os.path.join(OUT_DIR, "futex2-waitv-syscall-d.svg")
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(SVG_MAIN)
    print(f"Generated {main_path}")

    hist_path = os.path.join(OUT_DIR, "hist-sync-evolution.svg")
    with open(hist_path, "w", encoding="utf-8") as f:
        f.write(SVG_HIST)
    print(f"Generated {hist_path}")

if __name__ == "__main__":
    render()
