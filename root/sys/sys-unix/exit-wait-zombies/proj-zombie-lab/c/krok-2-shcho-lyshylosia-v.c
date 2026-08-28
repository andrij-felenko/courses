static void proc_report(pid_t pid)
{
    char path[64], buf[8192];
    ssize_t n;

    snprintf(path, sizeof path, "/proc/%d/cmdline", (int)pid);
    n = slurp(path, buf, sizeof buf);
    printf("cmdline: %zd байтів\n", n);          /* 0 — тому ps і пише <defunct> */

    snprintf(path, sizeof path, "/proc/%d/maps", (int)pid);
    n = slurp(path, buf, sizeof buf);
    printf("maps:    %zd байтів\n", n);          /* 0 — відображень немає */

    snprintf(path, sizeof path, "/proc/%d/statm", (int)pid);
    slurp(path, buf, sizeof buf);
    printf("statm:   %s", buf);                  /* 0 0 0 0 0 0 0 */

    int vm_lines = 0;
    snprintf(path, sizeof path, "/proc/%d/status", (int)pid);
    slurp(path, buf, sizeof buf);
    for (char *l = strtok(buf, "\n"); l; l = strtok(NULL, "\n")) {
        if (!strncmp(l, "Vm", 2)) { vm_lines++; continue; }
        if (!strncmp(l, "State:", 6) || !strncmp(l, "PPid:", 5) ||
            !strncmp(l, "Threads:", 8))
            printf("status:  %s\n", l);
    }
    printf("status:  рядків Vm*: %d\n", vm_lines);

    /* поля stat після дужки: state ppid pgrp session tty tpgid flags
       minflt cminflt majflt cmajflt utime stime … */
    snprintf(path, sizeof path, "/proc/%d/stat", (int)pid);
    slurp(path, buf, sizeof buf);
    char *p = strrchr(buf, ')');
    char st; long ppid; unsigned long ut = 0, kt = 0;
    if (p && sscanf(p + 2, "%c %ld %*d %*d %*d %*d %*u %*lu %*lu %*lu %*lu %lu %lu",
                    &st, &ppid, &ut, &kt) == 4)
        printf("stat:    стан %c, батько %ld, utime %lu, stime %lu (тиків по 1/%ld с)\n",
               st, ppid, ut, kt, sysconf(_SC_CLK_TCK));
}
