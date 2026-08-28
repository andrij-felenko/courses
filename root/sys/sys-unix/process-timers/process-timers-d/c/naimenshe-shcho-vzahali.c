static void on_alarm(int signo) { (void)signo; }   /* лише розбудити read() */

struct sigaction sa = { .sa_handler = on_alarm };  /* БЕЗ SA_RESTART */
sigemptyset(&sa.sa_mask);
sigaction(SIGALRM, &sa, NULL);

alarm(5);
ssize_t n = read(fd, buf, sizeof buf);
int err = errno;
alarm(0);                                          /* скасувати, якщо встигли */
if (n < 0 && err == EINTR) { /* минуло п'ять секунд */ }
