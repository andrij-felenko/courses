#include <future>
#include <iostream>

int calculate_heavy_sum(int a, int b) {
    return a + b;
}

void run_async_task() {
    // Автоматичне асинхронне виконання у фоновому потоці
    std::future<int> fut = std::async(std::launch::async, calculate_heavy_sum, 10, 20);
    
    // Блокуюче отримання результату
    int result = fut.get();
    std::cout << "Async result: " << result << "\n";
}
