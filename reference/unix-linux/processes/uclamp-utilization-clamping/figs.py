import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

def draw_uclamp_concept():
    w, h = 860, 440
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>']

    out.append(text(w/2, 28, "Модифікація сигналу утилізації PELT за допомогою uclamp", size=16, bold=True))

    ox, oy = 90, 370
    graph_w, graph_h = 680, 270

    # Axes
    out.append(line(ox, oy, ox + graph_w, oy, color=LINE, sw=1.8))
    out.append(line(ox, oy, ox, oy - graph_h, color=LINE, sw=1.8))

    # Y label at top left
    out.append(text(ox + 180, oy - graph_h - 15, "Утилізація (util_avg, 0..1024)", size=12, anchor="end", color=INK, bold=True))

    # Y ticks
    out.append(text(ox - 10, oy, "0", size=11, anchor="end", color=MUTED))
    out.append(text(ox - 10, oy - graph_h * 0.25, "256", size=11, anchor="end", color=MUTED))
    out.append(text(ox - 10, oy - graph_h * 0.5, "512", size=11, anchor="end", color=MUTED))
    out.append(text(ox - 10, oy - graph_h * 0.75, "768", size=11, anchor="end", color=MUTED))
    out.append(text(ox - 10, oy - graph_h, "1024", size=11, anchor="end", color=MUTED))

    # X label
    out.append(text(ox + graph_w / 2, oy + 42, "Час (мс)", size=12, anchor="middle", color=INK, bold=True))

    # Clamp thresholds
    y_min = oy - (384 / 1024.0) * graph_h  # uclamp.min = 384
    y_max = oy - (768 / 1024.0) * graph_h  # uclamp.max = 768

    # Draw uclamp.min line
    out.append(line(ox, y_min, ox + graph_w, y_min, color=FIELD, sw=2, dash="6,4"))
    box_min, _, _ = textbox(ox + graph_w - 90, y_min - 16, "uclamp.min = 384", size=11, fill="#e8f8f0", stroke=FIELD, pad=4)
    out.append(box_min)

    # Draw uclamp.max line
    out.append(line(ox, y_max, ox + graph_w, y_max, color=POS, sw=2, dash="6,4"))
    box_max, _, _ = textbox(ox + graph_w - 90, y_max + 16, "uclamp.max = 768", size=11, fill="#fdedec", stroke=POS, pad=4)
    out.append(box_max)

    # Raw PELT curve (Blue dash)
    pelt_points = [
        (ox, oy),
        (ox + 80, oy - (100/1024.0)*graph_h),
        (ox + 180, oy - (400/1024.0)*graph_h),
        (ox + 300, oy - (950/1024.0)*graph_h),
        (ox + 420, oy - (900/1024.0)*graph_h),
        (ox + 500, oy - (150/1024.0)*graph_h),
        (ox + 580, oy - (50/1024.0)*graph_h),
        (ox + graph_w, oy)
    ]
    path_pelt = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pelt_points)
    out.append(f'<path d="{path_pelt}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="4,4"/>')

    # Effective Clamped curve
    clamped_points = [
        (ox, y_min),
        (ox + 80, y_min),
        (ox + 180, oy - (400/1024.0)*graph_h),
        (ox + 300, y_max),
        (ox + 420, y_max),
        (ox + 500, y_min),
        (ox + 580, y_min),
        (ox + graph_w, y_min)
    ]
    path_clamped = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in clamped_points)
    out.append(f'<path d="{path_clamped}" fill="none" stroke="{INK}" stroke-width="3"/>')

    # Legend at top right
    leg1, _, _ = textbox(ox + 350, oy - graph_h - 15, "--- Сирий сигнал PELT (util_avg)", size=11, fill="#eef2fd", stroke=NEG, pad=4)
    leg2, _, _ = textbox(ox + 570, oy - graph_h - 15, "— Ефективний сигнал util_effective", size=11, fill="#ffffff", stroke=INK, pad=4)
    out.append(leg1)
    out.append(leg2)

    # Callouts moved away from curve intersections
    c1, _, _ = textbox(ox + 130, y_min - 35, "Floor Boost: утилізація підтягнута до min", size=10, fill="#e8f8f0", stroke=FIELD, pad=4)
    c2, _, _ = textbox(ox + 360, y_max - 35, "Ceiling Cap: утилізація затиснута до max", size=10, fill="#fdedec", stroke=POS, pad=4)
    out.append(c1)
    out.append(c2)

    out.append('</svg>')
    return "\n".join(out)

def draw_uclamp_buckets():
    w, h = 820, 360
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>']

    out.append(text(w/2, 25, "Структура uclamp_buckets у черзі виконання (Runqueue rq)", size=16, bold=True))

    tb1, _, _ = textbox(150, 68, "Task A\nuclamp_min = 150\n(Bucket 0)", size=11, fill="#eef2fd", stroke=NEG)
    tb2, _, _ = textbox(410, 68, "Task B\nuclamp_min = 550\n(Bucket 2)", size=11, fill="#e8f8f0", stroke=FIELD)
    tb3, _, _ = textbox(670, 68, "Task C\nuclamp_min = 512\n(Bucket 2)", size=11, fill="#fff8e7", stroke="#f39c12")
    out.append(tb1)
    out.append(tb2)
    out.append(tb3)

    out.append(text(w/2, 125, "Масив бакетів черги: rq->uclamp[UCLAMP_MIN].bucket[5]", size=12, bold=True))

    out.append(line(150, 135, 125, 165, color=NEG, sw=1.5, dash="3,3"))
    out.append(line(410, 135, 440, 165, color=FIELD, sw=1.5, dash="3,3"))
    out.append(line(670, 135, 460, 165, color="#f39c12", sw=1.5, dash="3,3"))

    bucket_ranges = ["0: [0..20%]", "1: [21..40%]", "2: [41..60%]", "3: [61..80%]", "4: [81..100%]"]
    counts = ["count = 1", "count = 0", "count = 2", "count = 0", "count = 0"]
    colors = [FILL, FILL, "#e8f8f0", FILL, FILL]

    bw = 138
    start_x = 55
    for i in range(5):
        bx = start_x + i * (bw + 10)
        by = 165
        r_box = rect(bx, by, bw, 70, fill=colors[i], stroke=LINE, sw=1.5)
        out.append(r_box)
        out.append(text(bx + bw/2, by + 22, f"Bucket {bucket_ranges[i]}", size=11, bold=True))
        out.append(text(bx + bw/2, by + 48, counts[i], size=12, color=FIELD if i==2 else INK, bold=(i==2)))

    res_box, _, _ = textbox(w/2, 290, "O(1) Пошук максимуму: сканування від Bucket 4 до 0\nНайвищий активний бакет = Bucket 2 → Effective rq uclamp_min = max(Task B, Task C) = 550", size=12, fill="#f4f6f8", stroke=LINE, pad=10, bold=True)
    out.append(res_box)

    out.append('</svg>')
    return "\n".join(out)

def draw_uclamp_eas_schedutil():
    w, h = 820, 380
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>']

    out.append(text(w/2, 28, "Розповсюдження утилізації uclamp в ядрі Linux", size=16, bold=True))

    box_sys, _, _ = textbox(210, 80, "sched_setattr(2)\nsched_util_min / max", size=12, fill="#eef2fd", stroke=NEG)
    box_cg, _, _ = textbox(610, 80, "Cgroups v2 (cpu)\ncpu.uclamp.min / max", size=12, fill="#e8f8f0", stroke=FIELD)
    out.append(box_sys)
    out.append(box_cg)

    out.append(line(210, 110, 350, 155, color=LINE, sw=1.5))
    out.append(line(610, 110, 470, 155, color=LINE, sw=1.5))

    box_eff, _, _ = textbox(410, 175, "uclamp_eff_value()\neffective_util = clamp(PELT, uclamp_min, uclamp_max)", size=12, fill="#ffffff", stroke=INK, pad=10, bold=True)
    out.append(box_eff)

    out.append(line(330, 205, 220, 255, color=LINE, sw=1.5))
    out.append(line(490, 205, 600, 255, color=LINE, sw=1.5))

    box_su, _, _ = textbox(220, 290, "schedutil Governor\nfreq = freq_next(util_effective)\n→ CPPC / MSR / DVFS Hardware", size=11, fill="#fff8e7", stroke="#f39c12", pad=8)
    out.append(box_su)

    box_eas, _, _ = textbox(600, 290, "EAS (Energy Aware Scheduling)\nfind_energy_efficient_cpu()\n→ LITTLE vs MID vs BIG Core Selection", size=11, fill="#fdedec", stroke=POS, pad=8)
    out.append(box_eas)

    out.append('</svg>')
    return "\n".join(out)

def render():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    with open(os.path.join(img_dir, "uclamp-concept.svg"), "w", encoding="utf-8") as f:
        f.write(draw_uclamp_concept())

    with open(os.path.join(img_dir, "uclamp-buckets.svg"), "w", encoding="utf-8") as f:
        f.write(draw_uclamp_buckets())

    with open(os.path.join(img_dir, "uclamp-eas-schedutil.svg"), "w", encoding="utf-8") as f:
        f.write(draw_uclamp_eas_schedutil())

    print("Figures generated successfully.")

if __name__ == "__main__":
    render()
