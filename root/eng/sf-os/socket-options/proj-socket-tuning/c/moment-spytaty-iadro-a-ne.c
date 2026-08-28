static int is_connected(int fd)
{
    struct sockaddr_storage ss;
    socklen_t len = sizeof ss;
    return getpeername(fd, (struct sockaddr *)&ss, &len) == 0;
}

static int is_listening(int fd)
{
    int v = 0;
    socklen_t len = sizeof v;
    if (getsockopt(fd, SOL_SOCKET, SO_ACCEPTCONN, &v, &len) < 0) return 0;
    return v != 0;
}
