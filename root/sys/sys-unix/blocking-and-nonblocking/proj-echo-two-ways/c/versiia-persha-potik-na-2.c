int main(void)
{
    signal(SIGPIPE, SIG_IGN);     /* інакше запис у закритий сокет уб'є процес */

    int ls = socket(AF_INET, SOCK_STREAM, 0);
    if (ls < 0) { perror("socket"); return 1; }

    int one = 1;
    setsockopt(ls, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);

    struct sockaddr_in a;
    memset(&a, 0, sizeof a);
    a.sin_family      = AF_INET;
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    a.sin_port        = htons(PORT);

    if (bind(ls, (struct sockaddr *)&a, sizeof a) < 0) { perror("bind");   return 1; }
    if (listen(ls, 128) < 0)                           { perror("listen"); return 1; }

    for (;;) {
        int fd = accept(ls, NULL, NULL);       /* тут потік спить, поки нема клієнта */
        if (fd < 0) {
            if (errno == EINTR) continue;
            perror("accept");
            break;
        }
        pthread_t t;
        if (pthread_create(&t, NULL, serve, (void *)(intptr_t)fd) != 0) {
            close(fd);                          /* потоки скінчилися — відмовляємо */
            continue;
        }
        pthread_detach(t);
    }
    return 0;
}
