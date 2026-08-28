exec::task<void> handle_client(scheduler auto sch, socket_handle sock) {
    // Асинхронно перемикаємося на цільовий планувальник
    co_await std::execution::schedule(sch);

    // Очікуємо на завершення сендера без блокування системного потоку
    auto header = co_await async_read_header(sock);
    auto payload = co_await async_read_payload(sock, header.length);

    co_await async_process_data(payload);
}
