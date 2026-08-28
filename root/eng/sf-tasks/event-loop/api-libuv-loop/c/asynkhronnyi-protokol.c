static void on_socket_closed(uv_handle_t *handle) {
    // Пам'ять дозволено звільняти ЛИШЕ всередині close-колбека!
    printf("Дескриптор успішно видалено з ядра, звільняємо пам'ять.
");
    free(handle);
}

void safe_close_client(uv_tcp_t *client) {
    // 1. Повідомляємо libuv про необхідність закриття
    uv_close((uv_handle_t*)client, on_socket_closed);
}
