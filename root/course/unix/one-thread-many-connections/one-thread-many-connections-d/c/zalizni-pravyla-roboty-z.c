while (1) {
    ssize_t count = read(fd, buf, sizeof(buf));
    if (count > 0) {
        process_data(buf, count);
    } else if (count == -1) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            break; /* Усі наявні дані вичитано повністю! */
        }
        handle_error(fd);
        break;
    } else if (count == 0) {
        close_connection(fd); /* Клієнт закрив з'єднання */
        break;
    }
}
