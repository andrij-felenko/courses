#ifndef __EXECVE_EVENT_H
#define __EXECVE_EVENT_H

#define TASK_COMM_LEN 16

struct execve_event {
    unsigned int pid;           /* Ідентифікатор нового процесу (PID) */
    unsigned int ppid;          /* Ідентифікатор батьківського процесу (PPID) */
    unsigned long long boot_time_ns; /* Часова мітка від старту системи у наносекундах */
    char comm[TASK_COMM_LEN];   /* Скорочена назва виконуваного файла */
};

#endif /* __EXECVE_EVENT_H */
