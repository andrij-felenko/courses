std::promise<void> ready_promise;
std::future<void> ready_future = ready_promise.get_future();

std::thread t([p = std::move(ready_promise)]() mutable {
    // Виконання довгої ініціалізації
    p.set_value(); // Запис без аргументів
});

ready_future.wait(); // Блокуюче очікування сигналу готовності
std::cout << "Ініціалізацію завершено!" << std::endl;
t.join();
