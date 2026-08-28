// 1. Створюємо packaged_task над лямбдою
std::packaged_task<int(int, int)> task([](int a, int b) {
    return a + b;
});

// 2. Витягуємо future для отримання результату
std::future<int> fut = task.get_future();

// 3. Виконуємо задачу (можна у поточному потоці, іншому потоці чи пулі)
task(10, 20);

// 4. Отримуємо результат
std::cout << "Результат: " << fut.get() << std::endl; // Виведе 30
