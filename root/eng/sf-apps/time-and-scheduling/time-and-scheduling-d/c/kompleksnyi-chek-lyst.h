/* Прив'язка до виділеного ізольованого ядра (C) */
cpu_set_t cpuset;
CPU_ZERO(&cpuset);
CPU_SET(2, &cpuset);
pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

/* Встановлення політики SCHED_FIFO */
struct sched_param param;
param.sched_priority = 99; /* Найвищий пріоритет RT */
sched_setscheduler(0, SCHED_FIFO, &param);
