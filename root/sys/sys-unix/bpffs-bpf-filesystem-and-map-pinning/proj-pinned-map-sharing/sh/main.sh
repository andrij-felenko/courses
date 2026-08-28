# 1. Список усіх мап у ядрі з відображенням зафіксованих шляхів
sudo bpftool map list

# Приклад виводу:
# 27: hash  name shared_stats  flags 0x0
#     key 4B  value 8B  max_entries 1024  memlock …B
#     pinned /sys/fs/bpf/shared_stats_map

# 2. Дамп усього вмісту зафіксованої мапи
sudo bpftool map dump pinned /sys/fs/bpf/shared_stats_map

# Приклад виводу:
# key: 2a 00 00 00  value: dc 05 00 00 00 00 00 00
# Found 1 element
