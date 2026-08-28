int fd = open("doc", O_RDONLY);

struct sigaction sa = { 0 };
sa.sa_sigaction = on_break;              /* void on_break(int, siginfo_t *, void *) */
sa.sa_flags = SA_SIGINFO;
sigaction(SIGRTMIN, &sa, NULL);

fcntl(fd, F_SETSIG, SIGRTMIN);           /* черга й si_fd замість голого SIGIO */

if (fcntl(fd, F_SETLEASE, F_WRLCK) == -1)
    perror("F_SETLEASE");                /* F_SETOWN не потрібен: ядро вже */
                                         /* призначило власником нашу групу потоків */
