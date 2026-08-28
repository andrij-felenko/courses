pid_t pid = fork();
if (pid == 0) {
    close(m);                    /* ведучий кінець дитині не потрібен */
    setsid();                    /* новий сеанс: старого керуючого термінала більше немає */
    ioctl(s, TIOCSCTTY, 0);      /* цей термінал — керуючий для нового сеансу */
    dup2(s, 0);
    dup2(s, 1);
    dup2(s, 2);
    if (s > 2) close(s);
    execl("/bin/bash", "bash", "-i", NULL);
    _exit(127);
}
