#include <vector>
#include <functional>

void setup_distributed_workspace(const std::vector<std::string>& node_dirs) {
    // Вектор анонімних охоронців для відкату динамічної кількості дій
    std::vector<ScopeGuard<std::function<void()>>> rollbacks;
    rollbacks.reserve(node_dirs.size());

    // Якщо функція перерветься винятком на 5-му вузлі,
    // деструктор вектора знищить усі збережені охоронці,
    // які автоматично відкотять перші 4 вузли!
    auto all_guard = make_scope_guard([&rollbacks] noexcept {
        // Очищення у зворотному порядку (LIFO)
        for (auto it = rollbacks.rbegin(); it != rollbacks.rend(); ++it) {
            // деструктор кожного елемента виконає збережену дію
        }
    });

    for (const auto& dir : node_dirs) {
        fs::create_directories(dir);
        rollbacks.emplace_back(make_scope_guard([dir] noexcept {
            std::error_code ec;
            fs::remove_all(dir, ec);
        }));
    }

    // Додаткові операції ініціалізації
    // initialize_network_mesh(node_dirs);

    // Успіх: скасовуємо відкат усіх створених каталогів
    for (auto& g : rollbacks) {
        g.dismiss();
    }
    all_guard.dismiss();
}
