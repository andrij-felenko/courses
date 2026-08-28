while (true) {
    ssize_t count = ::read(fd, buf.data(), buf.size());
    if (count > 0) {
        process_data(std::span(buf.data(), static_cast<size_t>(count)));
    } else if (count == -1) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            break; // Усі наявні дані вичитано повністю!
        }
        handle_error(fd);
        break;
    } else if (count == 0) {
        close_connection(fd); // Клієнт закрив з'єднання
        break;
    }
}
