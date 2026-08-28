// Головний потік стартує на Ядрі 0 (Вузол 0)
std::vector<DataRecord> shared_table(100'000'000);

// Ініціалізація даних одним циклом у головному потоці:
for (auto& record : shared_table) {
    record.init(); // <-- ТУТ ВІДБУВАЄТЬСЯ ПЕРШИЙ ДОТИК!
}

// Запуск 64 робочих потоків на всіх ядрах Вузла 0 та Вузла 1:
start_worker_threads(shared_table);
