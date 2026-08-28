std::packaged_task<int()> task([] { return rand() % 100; });

auto fut1 = task.get_future();
task(); // Перший запуск
int res1 = fut1.get();

task.reset(); // Скидаємо стан і створюємо новий future!
auto fut2 = task.get_future();
task(); // Другий запуск
int res2 = fut2.get();
