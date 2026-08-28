auto f = std::async(std::launch::deferred, []() {
    std::cout << "Обчислення виконується синхронно!" << std::endl;
    return 42;
});

// Виклик wait_for поверне deferred, НЕ запускаючи обчислення!
auto status = f.wait_for(0ms); // status == std::future_status::deferred

// Лише явний виклик get() або wait() спровокує виконання у поточному потоці
int res = f.get(); // Виконується лямбда у поточному потоці
