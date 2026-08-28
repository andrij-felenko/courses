// Допоміжна функція для імітації складного розрахунку
long long compute_sum(int id, const std::vector<int>& data) {
    std::cout << "[Потік " << std::this_thread::get_id() 
              << "] Початок обробки задачі #" << id << std::endl;
    
    // Імітуємо обчислювальне навантаження
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    long long sum = std::accumulate(data.begin(), data.end(), 0LL);
    
    std::cout << "[Потік " << std::this_thread::get_id() 
              << "] Завершення задачі #" << id << " -> Сума = " << sum << std::endl;
    return sum;
}

// Функція, яка кидає виняток під час виконання
double risky_division(double a, double b) {
    if (b == 0.0) {
        throw std::invalid_argument("Ділення на нуль у фоновому потоці!");
    }
    return a / b;
}

int main() {
    std::cout << "=== Старт демонстрації TaskExecutor ===" << std::endl;

    // Створюємо пул із 4 робочих потоків
    TaskExecutor pool(4);

    // 1. Надсилаємо групу обчислювальних задач
    std::vector<int> numbers(100000, 1); // Вектор з 100 000 одиниць
    std::vector<std::future<long long>> futures;

    for (int i = 1; i <= 8; ++i) {
        futures.push_back(pool.enqueue(compute_sum, i, std::cref(numbers)));
    }

    // 2. Надсилаємо задачу з потенційним винятком
    auto err_future = pool.enqueue(risky_division, 10.0, 0.0);

    // 3. Збираємо результати паралельних обчислень
    long long total_sum = 0;
    for (size_t i = 0; i < futures.size(); ++i) {
        // fut.get() чекає завершення конкретної задачі
        total_sum += futures[i].get();
    }

    std::cout << "\n[Головний потік] Усі обчислення завершено. Загальна сума = " 
              << total_sum << std::endl;

    // 4. Перевіряємо обробку винятку
    try {
        double res = err_future.get();
        std::cout << "Результат ділення: " << res << std::endl;
    } catch (const std::exception& e) {
        std::cout << "\n[Головний потік] Успішно перехоплено виняток з пулу: " 
                  << e.what() << std::endl;
    }

    std::cout << "=== Завершення демонстрації ===" << std::endl;
    return 0;
}
