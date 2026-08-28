// АНТИПАТЕРН: активне опитування, що спалює 100% ядра процесора
while (true) {
    ssize_t n = ::read(sockfd, buf.data(), buf.size());
    if (n > 0) {
        process_data(std::span(buf.data(), static_cast<size_t>(n)));
        break;
    }
    if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
        // даних немає, продовжуємо неперервно крутити цикл
        continue;
    }
    break; // помилка або закриття сокета
}
