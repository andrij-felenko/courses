// Переведення сокета в неблокуючий режим
int flags = ::fcntl(sock_fd, F_GETFL, 0);
::fcntl(sock_fd, F_SETFL, flags | O_NONBLOCK);

// Реєстрація дескриптора в epoll
int epoll_fd = ::epoll_create1(0);
struct epoll_event ev{};
ev.events = EPOLLIN | EPOLLET; // Edge-triggered режим
ev.data.fd = sock_fd;
::epoll_ctl(epoll_fd, EPOLL_CTL_ADD, sock_fd, &ev);
