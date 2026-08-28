#include <future>
#include <vector>
#include <thread>
#include <iostream>

void worker_task(int id, std::shared_future<std::string> config_future) {
    // Усі потоки чекають на один і той самий future!
    std::string config = config_future.get(); // Повертає const std::string&
    std::cout << "Потік " << id << " отримав конфіг: " << config << std::endl;
}

int main() {
    std::promise<std::string> p;
    // Трансформуємо std::future у std::shared_future через f.share()
    std::shared_future<std::string> sf = p.get_future().share();

    std::vector<std::thread> workers;
    for (int i = 0; i < 4; ++i) {
        // Копіюємо shared_future у кожен потік!
        workers.emplace_back(worker_task, i, sf);
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    p.set_value("DB_HOST=localhost;PORT=5432;"); // Сповіщаємо всі потоки одразу

    for (auto& w : workers) {
        w.join();
    }
}
