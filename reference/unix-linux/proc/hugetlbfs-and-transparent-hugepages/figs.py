# -*- coding: utf-8 -*-
import os
import sys

# Path to scripts/ directory from reference/unix-linux/proc/hugetlbfs-and-transparent-hugepages
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "scripts"
    ),
)
from svgkit import (
    FILL,
    INK,
    LINE,
    MUTED,
    NEG,
    POS,
    arrow,
    fitbox,
    line,
    mtext,
    rect,
    render,
    text,
    textbox,
)


def make_tlb_walk_comparison():
    path = os.path.join(os.path.dirname(__file__), "img", "tlb-walk-comparison.svg")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    w, h = 880, 420

    frags = []

    # Title banner / Section headers
    frags.append(
        fitbox(
            30,
            40,
            390,
            40,
            "Стандартна сторінка 4 КіБ (4-рівневе дерево)",
            size=14,
            bold=True,
            fill="#eaf0fd",
            stroke=NEG,
        )
    )
    frags.append(
        fitbox(
            460,
            40,
            390,
            40,
            "Велика сторінка 2 МіБ (3-рівневе дерево з PSE)",
            size=14,
            bold=True,
            fill="#fdecea",
            stroke=POS,
        )
    )

    # 4 KiB walk steps (Left column)
    steps_4k = [
        ("CR3", "Корінь PGD"),
        ("PGD (L4)", "Page Global Dir"),
        ("P4D / PUD (L3)", "Page Upper Dir"),
        ("PMD (L2)", "Page Middle Dir"),
        ("PTE (L1)", "Page Table Entry"),
        ("Фізична сторінка", "4 КіБ фрейм у RAM"),
    ]

    y_start = 100
    box_w = 170
    box_h = 42

    for i, (title, desc) in enumerate(steps_4k):
        cy = y_start + i * 50
        fill_c = "#ffffff" if i < 5 else "#eaf0fd"
        stroke_c = NEG if i == 5 else LINE
        frags.append(
            fitbox(
                50,
                cy,
                box_w,
                box_h,
                f"{title}\n({desc})",
                size=11,
                fill=fill_c,
                stroke=stroke_c,
            )
        )

        # Arrow down
        if i < len(steps_4k) - 1:
            frags.append(
                arrow(
                    50 + box_w / 2,
                    cy + box_h,
                    50 + box_w / 2,
                    cy + 50,
                    color=NEG,
                    sw=1.5,
                )
            )

    # Annotations for 4K walk
    frags.append(
        fitbox(
            240,
            150,
            170,
            90,
            "TLB Miss overhead:\n• 4 звернення до RAM\n• 262 144 записи / ГіБ\n• Висока затримка MMU",
            size=11,
            fill="#f4f6f8",
            stroke=MUTED,
        )
    )

    # 2 MiB walk steps (Right column)
    steps_2m = [
        ("CR3", "Корінь PGD"),
        ("PGD (L4)", "Page Global Dir"),
        ("P4D / PUD (L3)", "Page Upper Dir"),
        ("PMD (L2 + PSE)", "Page Size Extension"),
        ("Фізичний блок", "2 МіБ суцільний RAM"),
    ]

    for i, (title, desc) in enumerate(steps_2m):
        step_index = i if i < 4 else 5
        cy = y_start + step_index * 50
        fill_c = (
            "#fdecea"
            if i == 3
            else ("#ffffff" if i < 4 else "#fdecea")
        )
        stroke_c = POS if i >= 3 else LINE
        bold_flag = True if i == 3 else False
        frags.append(
            fitbox(
                480,
                cy,
                box_w,
                box_h,
                f"{title}\n({desc})",
                size=11,
                fill=fill_c,
                stroke=stroke_c,
                bold=bold_flag,
            )
        )

        # Arrow down
        if i < len(steps_2m) - 1:
            next_step_index = (i + 1) if (i + 1) < 4 else 5
            next_cy = y_start + next_step_index * 50
            frags.append(
                arrow(
                    480 + box_w / 2,
                    cy + box_h,
                    480 + box_w / 2,
                    next_cy,
                    color=POS,
                    sw=1.5,
                )
            )

    # Bypass arrow showing PTE skipped
    frags.append(
        line(
            480 + box_w,
            y_start + 3 * 50 + box_h / 2,
            670,
            y_start + 3 * 50 + box_h / 2,
            color=POS,
            sw=1.5,
            dash="4,3",
        )
    )
    frags.append(
        text(
            675,
            y_start + 3 * 50 + box_h / 2 + 4,
            "Обхід PTE пропущено (PSE=1)",
            size=11,
            color=POS,
            bold=True,
            anchor="start",
        )
    )

    # Annotations for 2M walk
    frags.append(
        fitbox(
            670,
            150,
            180,
            90,
            "TLB Hit переваги:\n• Лише 3 звернення до RAM\n• 512 записів / ГіБ\n• Економія пам'яті PMD",
            size=11,
            fill="#fdecea",
            stroke=POS,
        )
    )

    render(path, w, h, *frags)


def make_hugetlbfs_vs_thp_architecture():
    path = os.path.join(
        os.path.dirname(__file__), "img", "hugetlbfs-vs-thp-architecture.svg"
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    w, h = 880, 460

    frags = []

    # Title / Header boxes
    frags.append(
        fitbox(
            30,
            20,
            390,
            40,
            "Явні великі сторінки: hugetlbfs",
            size=14,
            bold=True,
            fill="#fdecea",
            stroke=POS,
        )
    )
    frags.append(
        fitbox(
            460,
            20,
            390,
            40,
            "Прозорі великі сторінки: THP",
            size=14,
            bold=True,
            fill="#eaf0fd",
            stroke=NEG,
        )
    )

    # Hugetlbfs side (Left)
    frags.append(
        fitbox(
            40,
            80,
            370,
            70,
            "Статична резервація пам'яті\n(/proc/sys/vm/nr_hugepages)\nВиділення суцільних блоків при старті ядра",
            size=11,
            fill="#ffffff",
            stroke=LINE,
        )
    )
    frags.append(
        arrow(225, 150, 225, 180, color=POS, sw=1.5)
    )

    frags.append(
        fitbox(
            40,
            180,
            370,
            70,
            "Спеціалізована ФС hugetlbfs\n(mount -t hugetlbfs nodev /dev/hugepages)\nІзольований пул сторінок поза Buddy-аллокатором",
            size=11,
            fill="#ffffff",
            stroke=LINE,
        )
    )
    frags.append(
        arrow(225, 250, 225, 280, color=POS, sw=1.5)
    )

    frags.append(
        fitbox(
            40,
            280,
            370,
            70,
            "Явний доступ з простору користувача\nmmap(MAP_HUGETLB) / shmget(SHM_HUGETLB)\nГарантований доступ, без свопінгу",
            size=11,
            fill="#fdecea",
            stroke=POS,
            bold=True,
        )
    )

    # Advantages / Disadvantages box for Hugetlbfs
    frags.append(
        fitbox(
            40,
            370,
            370,
            70,
            "Плюси: Нульові затримки виділення, без сплитів\nМінуси: Негнучкість, неможливість свопінгу",
            size=11,
            fill="#f4f6f8",
            stroke=MUTED,
        )
    )

    # THP side (Right)
    frags.append(
        fitbox(
            470,
            80,
            370,
            70,
            "Динамічний Buddy Allocator (Order-9)\nВиділення 2 МіБ сторінок 'на ходу'\nПолітики: always / madvise / never",
            size=11,
            fill="#ffffff",
            stroke=LINE,
        )
    )
    frags.append(
        arrow(655, 150, 655, 180, color=NEG, sw=1.5)
    )

    frags.append(
        fitbox(
            470,
            180,
            370,
            70,
            "Фоновий демон khugepaged & Compaction\nСканування RAM, згортання 512×4K у 2 МіБ\nДинамічний сплит при munmap/mprotect",
            size=11,
            fill="#ffffff",
            stroke=LINE,
        )
    )
    frags.append(
        arrow(655, 250, 655, 280, color=NEG, sw=1.5)
    )

    frags.append(
        fitbox(
            470,
            280,
            370,
            70,
            "Прозоре виділення для програм\nЗзвичайний malloc / mmap + madvise(MADV_HUGEPAGE)\nАвтоматичне керування в ядрі",
            size=11,
            fill="#eaf0fd",
            stroke=NEG,
            bold=True,
        )
    )

    # Advantages / Disadvantages box for THP
    frags.append(
        fitbox(
            470,
            370,
            370,
            70,
            "Плюси: Прозорість, універсальність, свопінг\nМінуси: Затримки дефрагментації, Memory Bloat",
            size=11,
            fill="#f4f6f8",
            stroke=MUTED,
        )
    )

    render(path, w, h, *frags)


if __name__ == "__main__":
    make_tlb_walk_comparison()
    make_hugetlbfs_vs_thp_architecture()
    print("Figures generated successfully.")
