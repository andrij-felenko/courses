auto on_socket_closed = [](uv_handle_t* handle) {
    // Пам'ять дозволено звільняти ЛИШЕ всередині close-колбека!
    std::cout << "Дескриптор успішно видалено з ядра, звільняємо пам'ять.
";
    delete reinterpret_cast<uv_tcp_t*>(handle);
};

void safe_close_client(uv_tcp_t* client) {
    // 1. Повідомляємо libuv про необхідність закриття
    uv_close(reinterpret_cast<uv_handle_t*>(client), on_socket_closed);
}
