#include <future>
#include <thread>
#include <iostream>

void async_worker(std::promise<int> p) {
    try {
        // Фонове обчислення
        int result = 100 + 200;
        p.set_value(result); // Запис значення
    } catch (...) {
        p.set_exception(std::current_exception()); // Запис винятку
    }
}

int main() {
    std::promise<int> p;
    std::future<int> f = p.get_future(); // Отримання зчитувального кінця

    std::thread t(async_worker, std::move(p)); // promise є move-only!
    
    std::cout << "Результат з фонового потоку: " << f.get() << std::endl;
    t.join();
}
