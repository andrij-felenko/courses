// ПОМИЛКА: використання system_clock для дедлайну
auto start = std::chrono::system_clock::now();
auto timeout = std::chrono::seconds(30);

while (!resource_ready()) {
    auto now = std::chrono::system_clock::now();
    if (now - start >= timeout) {
        handle_timeout_failure();
        break;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
}
