# Перелік УСІХ мап у ядрі; у зафіксованих поруч видно рядок pinned зі шляхом
bpftool map list

# Дамп елементів мапи, зафіксованої у bpffs
bpftool map dump pinned /sys/fs/bpf/my_map

# Перегляд деталей програми eBPF за її зафіксованим шляхом
bpftool prog show pinned /sys/fs/bpf/my_prog

# Фіксація вже завантаженої програми за її глобальним ID
bpftool prog pin id 42 /sys/fs/bpf/my_pinned_prog
