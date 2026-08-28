static void poke(int fd)      { char c = '!'; (void)!write(fd, &c, 1); }
static void wait_poke(int fd) { char c;       (void)!read(fd, &c, 1);  }

static void case_fork(void)
{
    int up[2], down[2];
    if (pipe(up) || pipe(down)) { perror("pipe"); exit(1); }

    int fd = fresh(0);
    write(fd, "AAAAA", 5);
    fflush(NULL);                    /* інакше буфер stdio подвоїться */

    pid_t kid = fork();
    if (kid == 0) {
        close(up[0]); close(down[1]);
        write(fd, "BBBBB", 5);       /* та сама позиція: 5 → 10 */
        poke(up[1]);                 /* «я записав» */
        wait_poke(down[0]);          /* чекаю, доки мене зміряють */
        _exit(0);
    }
    close(up[1]); close(down[0]);
    wait_poke(up[0]);

    witness("fork", getpid(), fd, kid, fd);

    poke(down[1]);
    waitpid(kid, NULL, 0);
    close(up[0]); close(down[1]); close(fd);
}
