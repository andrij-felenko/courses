std::map<int, std::string> active_tasks;
std::map<int, std::string> completed_tasks;

// Вилучаємо вузол без деалокації пам'яті:
auto node = active_tasks.extract(101);
if (!node.empty()) {
    node.key() = 202; // Зміна ключа без перестворення елемента
    completed_tasks.insert(std::move(node)); // Вставка без виділення вузла!
}

// Пряме злиття двох асоціативних контейнерів:
completed_tasks.merge(active_tasks);
