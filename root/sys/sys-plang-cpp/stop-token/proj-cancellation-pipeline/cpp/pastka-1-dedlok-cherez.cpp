// ❌ АНТИПАТЕРН: Ризик взаємного блокування (Deadlock)
std::mutex data_mutex;

void risky_operation(std::stop_token st) {
    std::stop_callback cb(st, [&] {
        std::lock_guard lock(data_mutex); // ДЕДЛОК, якщо викликач request_stop() уже тримає data_mutex!
        cleanup_resources();
    });

    std::lock_guard lock(data_mutex);
    // Якщо в цей момент інший потік викликає request_stop(), виникає класичний ABBA-дедлок.
}
