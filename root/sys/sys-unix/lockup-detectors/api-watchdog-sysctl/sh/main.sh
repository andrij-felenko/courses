# Зняти стек викликів (Call Trace) активних процесів на всіх ядрах CPU через NMI IPI:
echo l > /proc/sysrq-trigger

# Вивести список усіх задач у системі та їхній стан (R, S, D, Z) зі стеком викликів:
echo t > /proc/sysrq-trigger

# Вивести список усіх блокувань (locks), утримуваних процесами (вимагає CONFIG_LOCKDEP):
echo d > /proc/sysrq-trigger

# Примусово ініціювати фатальну паніку ядра для отримання дампа vmcore:
echo c > /proc/sysrq-trigger
