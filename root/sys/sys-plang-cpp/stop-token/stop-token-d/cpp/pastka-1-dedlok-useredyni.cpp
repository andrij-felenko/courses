// ❌ ПОМИЛКА: Самодедлок
std::mutex state_mutex;

void bad_worker(std::stop_token st) {
    std::stop_callback cb(st, [&] {
        std::lock_guard lock(state_mutex); // ДЕДЛОК, якщо викликач request_stop() уже захопив state_mutex!
        cleanup();
    });

    std::lock_guard lock(state_mutex);
    // Робота з даними...
}
