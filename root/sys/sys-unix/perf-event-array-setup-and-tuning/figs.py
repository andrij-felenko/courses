import os

def render():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">
    <defs>
        <style>
            .kernel { fill: #f0f0f0; stroke: #333; stroke-width: 2; }
            .user { fill: #e0f7fa; stroke: #006064; stroke-width: 2; }
            .buffer { fill: #fff9c4; stroke: #f57f17; stroke-width: 2; }
            .text { font-family: sans-serif; font-size: 14px; fill: #333; }
            .title { font-family: sans-serif; font-size: 18px; font-weight: bold; }
            .arrow { stroke: #333; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
        </style>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
        </marker>
    </defs>

    <!-- Kernel Space -->
    <rect x="50" y="200" width="700" height="180" class="kernel" rx="10" />
    <text x="60" y="225" class="title">Kernel Space</text>

    <!-- CPU Cores -->
    <rect x="100" y="250" width="150" height="100" class="buffer" rx="5" />
    <text x="120" y="280" class="text" font-weight="bold">CPU 0</text>
    <text x="120" y="300" class="text">eBPF Program</text>
    <text x="120" y="320" class="text">bpf_perf_event_output()</text>

    <rect x="325" y="250" width="150" height="100" class="buffer" rx="5" />
    <text x="345" y="280" class="text" font-weight="bold">CPU 1</text>
    <text x="345" y="300" class="text">eBPF Program</text>
    <text x="345" y="320" class="text">bpf_perf_event_output()</text>

    <rect x="550" y="250" width="150" height="100" class="buffer" rx="5" />
    <text x="570" y="280" class="text" font-weight="bold">CPU N</text>
    <text x="570" y="300" class="text">eBPF Program</text>
    <text x="570" y="320" class="text">bpf_perf_event_output()</text>

    <!-- Perf Event Arrays (Ring Buffers) -->
    <rect x="100" y="150" width="150" height="30" fill="#ffecb3" stroke="#ffb300" stroke-width="2" />
    <text x="110" y="170" class="text">Ring Buffer (CPU 0)</text>

    <rect x="325" y="150" width="150" height="30" fill="#ffecb3" stroke="#ffb300" stroke-width="2" />
    <text x="335" y="170" class="text">Ring Buffer (CPU 1)</text>

    <rect x="550" y="150" width="150" height="30" fill="#ffecb3" stroke="#ffb300" stroke-width="2" />
    <text x="560" y="170" class="text">Ring Buffer (CPU N)</text>

    <!-- User Space -->
    <rect x="50" y="20" width="700" height="100" class="user" rx="10" />
    <text x="60" y="45" class="title">User Space</text>

    <!-- Libbpf Poller -->
    <rect x="250" y="50" width="300" height="50" fill="#bbdefb" stroke="#1976d2" stroke-width="2" rx="5" />
    <text x="270" y="80" class="text" font-weight="bold">libbpf: perf_buffer__poll() (epoll)</text>

    <!-- Arrows -->
    <path d="M 175 250 L 175 180" class="arrow" />
    <path d="M 400 250 L 400 180" class="arrow" />
    <path d="M 625 250 L 625 180" class="arrow" />

    <path d="M 175 150 L 250 85" class="arrow" />
    <path d="M 400 150 L 400 100" class="arrow" />
    <path d="M 625 150 L 550 85" class="arrow" />
</svg>
"""
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    with open(os.path.join(img_dir, "perf-event-array.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)

if __name__ == "__main__":
    render()
