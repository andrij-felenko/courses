curl_multi_setopt(multi, CURLMOPT_SOCKETFUNCTION, on_socket);
curl_multi_setopt(multi, CURLMOPT_TIMERFUNCTION, on_timer);
curl_multi_add_handle(multi, easy);

int running = 0;
curl_multi_socket_action(multi, CURL_SOCKET_TIMEOUT, 0, &running);   // перший поштовх

for (;;) {
    struct epoll_event evs[64];
    int n = epoll_wait(ep, evs, 64, -1);      // −1: спимо, доки не станеться НІЧОГО
    for (int i = 0; i < n; i++) {
        int fd = evs[i].data.fd;
        if (fd == tfd) {
            uint64_t ticks;
            read(tfd, &ticks, sizeof ticks);
            curl_multi_socket_action(multi, CURL_SOCKET_TIMEOUT, 0, &running);
        } else if (fd == ui_fd) {
            pump_ui();                        // одна ітерація циклу господаря
        } else {
            int mask = ((evs[i].events & EPOLLIN)  ? CURL_CSELECT_IN  : 0)
                     | ((evs[i].events & EPOLLOUT) ? CURL_CSELECT_OUT : 0)
                     | ((evs[i].events & EPOLLERR) ? CURL_CSELECT_ERR : 0);
            curl_multi_socket_action(multi, fd, mask, &running);
        }
    }
    reap_finished();
}
