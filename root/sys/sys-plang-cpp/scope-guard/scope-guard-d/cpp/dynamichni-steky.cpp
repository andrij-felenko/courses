#include <vector>
#include <functional>
#include <scope>

void process_batch_items(const std::vector<Item>& items, Storage& storage) {
    std::vector<std::function<void()>> rollbacks;
    rollbacks.reserve(items.size());

    // Якщо будь-який елемент дасть збій — відкочуємо всі попередні у зворотному порядку
    std::scope_fail batch_guard = [&rollbacks] noexcept {
        for (auto it = rollbacks.rbegin(); it != rollbacks.rend(); ++it) {
            try {
                (*it)();
            } catch (...) {
                // ігноруємо вторинні помилки у деструкторі
            }
        }
    };

    for (const auto& item : items) {
        storage.insert(item);
        rollbacks.push_back([&storage, id = item.id()] {
            storage.remove(id);
        });
    }

    // Усі елементи вставлено успішно — деструктор batch_guard не спрацює
}
