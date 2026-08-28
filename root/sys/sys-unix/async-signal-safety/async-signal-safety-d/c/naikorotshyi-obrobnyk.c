static int wake_fd = -1;          /* кінець каналу на запис, неблокуючий */

static void on_signal(int signo)
{
    int saved = errno;                        /* чужий errno — під захист */
    unsigned char b = (unsigned char) signo;  /* який саме сигнал прийшов */

    (void) write(wake_fd, &b, 1);             /* один виклик зі списку     */

    errno = saved;                            /* повернути як було         */
}
