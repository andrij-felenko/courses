// чекати дані на двох сокетах одразу, не блокуючись на жодному
fd_set rd;
FD_ZERO(&rd);
FD_SET(sock_a, &rd);
FD_SET(sock_b, &rd);
int maxfd = (sock_a > sock_b ? sock_a : sock_b) + 1;

struct timeval tv = { .tv_sec = 5, .tv_usec = 0 };   // прокинутись хоч раз на 5 с
int r = select(maxfd, &rd, NULL, NULL, &tv);
if (r > 0) {
    if (FD_ISSET(sock_a, &rd)) { /* на A є дані — читаємо тільки A */ }
    if (FD_ISSET(sock_b, &rd)) { /* на B є дані — читаємо тільки B */ }
}
