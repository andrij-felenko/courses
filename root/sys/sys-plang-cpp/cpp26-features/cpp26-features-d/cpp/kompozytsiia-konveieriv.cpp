#include <execution>
#include <iostream>
#include <string>

void execute_async_task() {
    namespace ex = std::execution;

    // Створюємо пул потоків для важких фонових обчислень
    ex::run_loop background_loop;
    auto scheduler = background_loop.get_scheduler();

    // Описуємо конвеєр обробки даних
    auto work_pipeline = 
        ex::schedule(scheduler)
        | ex::then([]() {
            // Виконується на фоновому планувальнику
            return 42 * 100;
        })
        | ex::then([](int calculated_value) {
            // Перетворення результату
            return std::string("Результат обчислення: ") + std::to_string(calculated_value);
        });

    // Синхронно очікуємо результат виконання
    auto [final_string] = std::this_thread::sync_wait(std::move(work_pipeline)).value();
    std::cout << final_string << std::endl;
}
