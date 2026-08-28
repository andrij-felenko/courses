/* АНТИПАТЕРН: активне опитування, що спалює 100% ядра процесора */
while (1) {
    ssize_t n = read(sockfd, buf, sizeof(buf));
    if (n > 0) {
        process_data(buf, (size_t)n);
        break;
    }
    if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
        /* даних немає, продовжуємо неперервно крутити цикл */
        continue;
    }
    break; /* помилка або закриття сокета */
}
