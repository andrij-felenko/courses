/* Дескриптор 3 буває і слухачем, і вже прийнятим з'єднанням. */
static int is_listening(int fd)
{
    int val = 0;
    socklen_t len = sizeof val;

    if (getsockopt(fd, SOL_SOCKET, SO_ACCEPTCONN, &val, &len) < 0)
        return 0;
    return val;
}

    /* у main, одразу після listen_fds(): */
    if (n == 1 && !is_listening(LISTEN_FDS_START)) {
        echo(LISTEN_FDS_START);      /* нам дали саме з'єднання */
        return 0;
    }
