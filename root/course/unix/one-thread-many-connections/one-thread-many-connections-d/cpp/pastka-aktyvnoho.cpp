// НАЇВНИЙ АНТИПАТЕРН: активне опитування в циклі (Busy Polling)
while (running) {
    for (int fd : client_fds) {
        ssize_t n = ::read(fd, buf.data(), buf.size());
        if (n > 0) {
            handle_data(fd, std::span(buf.data(), static_cast<size_t>(n)));
        } else if (n == -1 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            continue; // Даних немає — переходимо до наступного
        }
    }
}
