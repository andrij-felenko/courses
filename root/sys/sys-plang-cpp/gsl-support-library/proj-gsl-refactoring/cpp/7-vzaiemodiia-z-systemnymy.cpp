// Адаптер системного сокета POSIX до типобезпечного GSL-пайплайну
void on_socket_data_received(int socket_fd, gsl::not_null<ILogger*> logger) {
    std::array<gsl::byte, 4096> socket_buffer{};
    
    // Системний виклик на межі введення
    ssize_t bytes_read = ::recv(socket_fd, socket_buffer.data(), socket_buffer.size(), 0);
    if (bytes_read <= 0) {
        return; // З'єднання закрито або помилка
    }

    // Миттєве створення безпечного зрізу з точним розміром фактично отриманих даних
    auto received_span = gsl::make_span(socket_buffer.data(), gsl::narrow<std::ptrdiff_t>(bytes_read));

    // Передача у верифікований конвеєр обробки
    auto record = SafeTelemetryDecoder::decode_packet(received_span, logger);
    if (record) {
        process_telemetry(*record);
    }
}
