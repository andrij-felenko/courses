int main() {
    // Створюємо чергу місткістю 5 елементів
    BoundedQueue<int> queue(5);

    std::vector<std::thread> producers;
    std::vector<std::thread> consumers;

    // Запуск 2 потоків-виробників
    for (int p = 0; p < 2; ++p) {
        producers.emplace_back([&queue, p]() {
            for (int i = 0; i < 10; ++i) {
                int item = p * 100 + i;
                if (queue.push(item)) {
                    std::cout << "[Producer " << p << "] Pushed: " << item << "\n";
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
            }
        });
    }

    // Запуск 3 потоків-споживачів
    for (int c = 0; c < 3; ++c) {
        consumers.emplace_back([&queue, c]() {
            while (true) {
                auto item = queue.pop();
                if (!item.has_value()) {
                    std::cout << "[Consumer " << c << "] Signal shutdown received. Exit.\n";
                    break;
                }
                std::cout << "[Consumer " << c << "] Popped: " << *item << "\n";
                std::this_thread::sleep_for(std::chrono::milliseconds(35));
            }
        });
    }

    // Очікуємо завершення роботи виробників
    for (auto& t : producers) {
        t.join();
    }

    // Ініціюємо чисте завершення черги
    queue.shutdown();

    // Очікуємо завершення роботи споживачів
    for (auto& t : consumers) {
        t.join();
    }

    std::cout << "Усі потоки успішно завершили роботу.\n";
    return 0;
}
