# 1. Перегляд усіх прикріплених TC програм на мережевих інтерфейсах
bpftool net show

# 2. Зняття розпарсеного байт-коду BPF (xlated) після перевіряльника BPF Verifier
bpftool prog dump xlated id <PROG_ID>

# 3. Зняття реальних машинного коду x86_64 після JIT-компіляції
bpftool prog dump jited id <PROG_ID>

# 4. Дамп вмісту конкретної BPF карти
bpftool map dump id <MAP_ID>
