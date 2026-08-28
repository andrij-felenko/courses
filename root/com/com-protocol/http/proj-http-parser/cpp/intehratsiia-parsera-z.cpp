// Приклад неблокуючого обробника сокета
void handle_client_read(int client_fd, ConnectionContext& conn, HttpStreamingParser& parser) {
    while (true) {
        ssize_t bytes_read = read(client_fd, conn.buffer + conn.bytes_in_buffer,
                                  sizeof(conn.buffer) - conn.bytes_in_buffer);
        
        if (bytes_read < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                // Усі доступні на цей момент байти з ядра вичитано
                break;
            }
            // Мережева помилка з'єднання
            close_connection(client_fd, conn);
            return;
        }
        
        if (bytes_read == 0) {
            // Клієнт закрив TCP-з'єднання (отримано FIN)
            close_connection(client_fd, conn);
            return;
        }
        
        conn.bytes_in_buffer += bytes_read;
        std::string_view stream_view(conn.buffer, conn.bytes_in_buffer);
        
        HttpRequestView request;
        ParseResult result = parser.parse(stream_view, request);
        
        if (result == ParseResult::COMPLETE) {
            // Запит успішно зібрано — викликаємо маршрутизатор
            dispatch_http_request(client_fd, request);
            parser.reset();
            conn.reset_buffer();
            break;
        } else if (result == ParseResult::NEED_MORE_DATA) {
            // Очікуємо наступної події EPOLLIN від epoll_wait
            break;
        } else {
            // Синтаксична помилка або атака Smuggling — негайно відповідаємо 400
            send_http_error(client_fd, 400, "Bad Request");
            close_connection(client_fd, conn);
            return;
        }
    }
}
