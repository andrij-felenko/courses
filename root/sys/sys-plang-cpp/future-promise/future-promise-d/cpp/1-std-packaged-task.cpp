#include <future>
#include <thread>
#include <iostream>

int calculate_sum(int a, int b) {
    return a + b;
}

int main() {
    // Обгортаємо функцію calculate_sum
    std::packaged_task<int(int, int)> task(calculate_sum);
    
    // Отримуємо future до виконання задач!
    std::future<int> res = task.get_future();

    // Запускаємо задачу в окремому потоці
    std::thread t(std::move(task), 10, 20);

    std::cout << "Результат packaged_task: " << res.get() << std::endl;
    t.join();
}
