import sys
import os

# Шлях до scripts/ для імпорту svgkit
script_dir = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.abspath(os.path.join(script_dir, '../../../../scripts'))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from svgkit import *

def build_img_dir():
    img_dir = os.path.join(script_dir, 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def fig1_architecture(img_dir):
    w, h = 880, 520
    frags = []
    
    # Заголовок
    frags.append(text(w / 2, 28, "Загальна архітектура eBPF у ядрі Linux", size=18, bold=True))

    # User Space Box
    frags.append(rect(30, 50, 820, 180, fill="#f0f7ff", stroke="#2457d6", sw=1.5, rx=8))
    frags.append(text(140, 75, "Простір користувача (User Space)", size=14, bold=True, color="#2457d6"))

    b1, w1, h1 = textbox(150, 140, "C-код eBPF\n(Clang / LLVM)", size=12, pad=10, fill="#ffffff", stroke="#2457d6")
    b2, w2, h2 = textbox(410, 140, "eBPF Bytecode\n(.o ELF-файл)", size=12, pad=10, fill="#ffffff", stroke="#2457d6")
    b3, w3, h3 = textbox(700, 140, "Агент / Loader\n(libbpf / C / C++)", size=12, pad=10, fill="#ffffff", stroke="#2457d6")
    
    frags.extend([b1, b2, b3])
    frags.append(arrow(150 + w1/2 + 5, 140, 410 - w2/2 - 5, 140, color="#2457d6"))
    frags.append(arrow(410 + w2/2 + 5, 140, 700 - w3/2 - 5, 140, color="#2457d6"))

    # Syscall arrow down
    frags.append(arrow(700, 140 + h3/2 + 5, 700, 275 - 5, color="#c0392b", sw=2.0))
    frags.append(text(765, 215, "sys_bpf()\nBPF_PROG_LOAD", size=11, color="#c0392b", bold=True))

    # Kernel Space Box
    frags.append(rect(30, 250, 820, 250, fill="#f2fbf5", stroke="#27ae60", sw=1.5, rx=8))
    frags.append(text(130, 275, "Простір ядра (Kernel Space)", size=14, bold=True, color="#27ae60"))

    k1, wk1, hk1 = textbox(700, 325, "Верифікатор (Verifier)\nПеревірка безпеки & CFG", size=12, pad=12, fill="#ffffff", stroke="#27ae60")
    k2, wk2, hk2 = textbox(440, 325, "JIT-компілятор\nТрансляція в x86/ARM code", size=12, pad=12, fill="#ffffff", stroke="#27ae60")
    k3, wk3, hk3 = textbox(150, 325, "Нативна програма\neBPF у ядрі", size=12, pad=12, fill="#ffffff", stroke="#27ae60")

    frags.extend([k1, k2, k3])
    frags.append(arrow(700 - wk1/2 - 8, 325, 440 + wk2/2 + 8, 325, color="#27ae60"))
    frags.append(arrow(440 - wk2/2 - 8, 325, 150 + wk3/2 + 8, 325, color="#27ae60"))

    # Hooks & Maps
    hk_box, whk, hhk = textbox(150, 445, "Ядерні точки (Hooks)\n(kprobes, tracepoints, XDP)", size=12, pad=10, fill="#e8f8f0", stroke="#27ae60")
    map_box, wmp, hmp = textbox(570, 445, "BPF Maps / Ring Buffer\n(Спільна пам'ять)", size=12, pad=10, fill="#fef9e7", stroke="#d35400")

    frags.extend([hk_box, map_box])
    frags.append(arrow(150, 325 + hk3/2 + 5, 150, 445 - hhk/2 - 5, color="#27ae60"))
    frags.append(arrow(150 + whk/2 + 5, 445, 570 - wmp/2 - 5, 445, color="#27ae60"))
    
    # Map read/write arrow going up to User loader (at x=700) or b2
    frags.append(arrow(570, 445 - hmp/2 - 5, 700 - 30, 140 + h3/2 + 5, color="#d35400", sw=1.8))
    frags.append(text(585, 235, "mmap / lookup\nevent stream", size=11, color="#d35400", bold=True))

    out_path = os.path.join(img_dir, 'ebpf-architecture.svg')
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")

def fig2_verifier_flow(img_dir):
    w, h = 840, 460
    frags = []

    frags.append(text(w / 2, 28, "Конвеєр перевірки програми Верифікатором eBPF", size=18, bold=True))

    s1, w1, h1 = textbox(110, 120, "1. BPF Bytecode\n(Інструкції програми)", size=12, pad=10, fill="#f4f6f8", stroke="#1a1a1a")
    s2, w2, h2 = textbox(300, 120, "2. Аналіз CFG\n(Перевірка циклів & unreachable)", size=12, pad=10, fill="#eaaa00", stroke="#b8860b")
    s3, w3, h3 = textbox(520, 120, "3. Трекінг станів\n(Регістри R0-R10 & стек)", size=12, pad=10, fill="#eaaa00", stroke="#b8860b")
    s4, w4, h4 = textbox(730, 120, "4. Безпека пам'яті\n(Null & Bounds check)", size=12, pad=10, fill="#eaaa00", stroke="#b8860b")

    frags.extend([s1, s2, s3, s4])
    frags.append(arrow(110 + w1/2 + 5, 120, 300 - w2/2 - 5, 120, color="#1a1a1a"))
    frags.append(arrow(300 + w2/2 + 5, 120, 520 - w3/2 - 5, 120, color="#b8860b"))
    frags.append(arrow(520 + w3/2 + 5, 120, 730 - w4/2 - 5, 120, color="#b8860b"))

    # Decision path
    frags.append(arrow(730, 120 + h4/2 + 5, 730, 240 - 5, color="#1a1a1a"))

    # Result boxes
    res_pass, wp, hp = textbox(520, 320, "Схвалено (PASS)\nПриєднати до Hook & JIT", size=13, pad=12, fill="#e8f8f0", stroke="#27ae60", bold=True)
    res_fail, wf, hf = textbox(730, 320, "Відхилено (FAIL)\nEINVAL + Verifier Log", size=13, pad=12, fill="#fdecea", stroke="#c0392b", bold=True)

    frags.extend([res_pass, res_fail])

    frags.append(arrow(730, 240, 520 + wp/2 + 5, 320 - hp/2, color="#27ae60", sw=2.0))
    text_pass = text(610, 245, "Гарантовано безпечно", size=11, color="#27ae60", bold=True)
    frags.append(text_pass)

    frags.append(arrow(730, 240, 730, 320 - hf/2 - 5, color="#c0392b", sw=2.0))
    text_fail = text(765, 275, "Порушення правил", size=11, color="#c0392b", bold=True)
    frags.append(text_fail)

    # Explanation summary box
    summary_box, ws, hs = textbox(240, 320, "Перевірки верифікатора:\n• Скінченність виконання (bounded loops)\n• Валідність вказівників (kernel vs map)\n• Відсутність неініціалізованих змінних\n• Ліміт інструкцій та захист від Spectre", size=12, pad=12, fill="#ffffff", stroke="#2457d6")
    frags.append(summary_box)

    out_path = os.path.join(img_dir, 'ebpf-verifier-flow.svg')
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")

def fig3_maps_and_ringbuf(img_dir):
    w, h = 840, 460
    frags = []

    frags.append(text(w / 2, 28, "Обмін даними через BPF Ring Buffer та BPF Hash Map", size=18, bold=True))

    # Kernel eBPF prog
    prog_b, wp, hp = textbox(150, 110, "eBPF Program\n(Контекст переривання / Hook)", size=13, pad=12, fill="#e8f8f0", stroke="#27ae60", bold=True)
    frags.append(prog_b)

    # Map 1: Hash Map
    hmap_b, wh, hh = textbox(450, 110, "BPF_MAP_TYPE_HASH\n[Key: PID] -> [Value: Counter]", size=12, pad=12, fill="#fef9e7", stroke="#d35400")
    frags.append(hmap_b)

    frags.append(arrow(150 + wp/2 + 5, 110, 450 - wh/2 - 5, 110, color="#d35400"))
    frags.append(text(290, 95, "bpf_map_lookup_elem()", size=11, color="#d35400"))

    # Map 2: Ring Buffer
    ring_b, wr, hr = textbox(450, 270, "BPF_MAP_TYPE_RINGBUF\n(Lock-free кільцевий буфер подій)\nProducer Pos ---> Consumer Pos", size=12, pad=14, fill="#eaf0fd", stroke="#2457d6")
    frags.append(ring_b)

    frags.append(arrow(150, 110 + hp/2 + 5, 450 - wr/2 - 5, 270, color="#2457d6", sw=1.8))
    frags.append(text(230, 210, "bpf_ringbuf_reserve()\nbpf_ringbuf_submit()", size=11, color="#2457d6"))

    # Userspace collector
    user_b, wu, hu = textbox(730, 190, "User Space Process\n(libbpf poll loop)", size=13, pad=12, fill="#ffffff", stroke="#1a1a1a", bold=True)
    frags.append(user_b)

    # Arrow from ringbuf to userspace via mmap
    frags.append(arrow(450 + wr/2 + 5, 270, 730 - wu/2 - 5, 190 + hu/4, color="#2457d6", sw=2.0))
    frags.append(text(590, 215, "mmap() + poll()", size=11, color="#2457d6", bold=True))

    # Arrow from hash map to userspace
    frags.append(arrow(450 + wh/2 + 5, 110, 730 - wu/2 - 5, 190 - hu/4, color="#d35400", sw=1.8))
    frags.append(text(600, 105, "bpf_map_lookup_elem()", size=11, color="#d35400"))

    # Annotation at bottom
    note_b, wn, hn = textbox(420, 400, "Перевага Ring Buffer над Perf Buffer: спільна пам'ять для всіх CPU,\nвпорядкованість подій за часом і відсутність втрат при сплесках навантаження.", size=11, pad=10, fill="#f4f6f8", stroke="#6b7280")
    frags.append(note_b)

    out_path = os.path.join(img_dir, 'ebpf-maps-and-ringbuf.svg')
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")

def main():
    img_dir = build_img_dir()
    fig1_architecture(img_dir)
    fig2_verifier_flow(img_dir)
    fig3_maps_and_ringbuf(img_dir)

if __name__ == '__main__':
    main()
