/* НАЇВНИЙ АНТИПАТЕРН: активне опитування в циклі (Busy Polling) */
while (running) {
    for (int i = 0; i < num_clients; ++i) {
        ssize_t n = read(client_fds[i], buf, sizeof(buf));
        if (n > 0) {
            handle_data(client_fds[i], buf, n);
        } else if (n == -1 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            continue; /* Даних немає — переходимо до наступного */
        }
    }
}
