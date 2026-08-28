# bpftrace - Однорядковий скрипт динамічного трасування

# 1. Kprobe: перехоплення входу у функцію ядра do_sys_openat2
bpftrace -e 'kprobe:do_sys_openat2 { printf("PID %d (%s) відкриває: %s\n", pid, comm, str(arg1)); }'

# 2. Uprobe: перехоплення виклику readline у бінарнику /bin/bash
bpftrace -e 'uprobe:/bin/bash:readline { printf("Bash (PID %d) очікує ввід\n", pid); }'

# 3. Uretprobe: перехоплення результату повернення з readline (команда користувача)
bpftrace -e 'uretprobe:/bin/bash:readline { printf("Введено команду: %s\n", str(retval)); }'
