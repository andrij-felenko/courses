/* Пріоритет потоку переривання, у назві якого є needle («eth0», «xhci»).
 * Потоки ядра видно в /proc як звичайні задачі, тож sched_getparam працює. */
static int irq_thread_prio(const char *needle)
{
    DIR *d = opendir("/proc");
    struct dirent *e;
    char path[64], comm[128];
    int found = -1;

    if (!d) return -1;
    while ((e = readdir(d)) != NULL) {
        FILE *f;
        if (e->d_name[0] < '0' || e->d_name[0] > '9') continue;
        snprintf(path, sizeof path, "/proc/%s/comm", e->d_name);
        if (!(f = fopen(path, "r"))) continue;
        if (fgets(comm, sizeof comm, f) && strncmp(comm, "irq/", 4) == 0
                                        && strstr(comm, needle) != NULL) {
            pid_t pid = (pid_t)strtol(e->d_name, NULL, 10);
            struct sched_param p;
            if (sched_getscheduler(pid) == SCHED_FIFO && sched_getparam(pid, &p) == 0)
                found = p.sched_priority;
        }
        fclose(f);
    }
    closedir(d);
    return found;                 /* −1: ядро без RT або переривання не в потоці */
}
