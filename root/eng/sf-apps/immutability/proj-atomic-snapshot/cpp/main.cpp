#include <atomic>
#include <memory>
#include <string>
#include <unordered_map>

class RoutingTable {
    using Table = std::unordered_map<std::string, std::string>;
    // комірка: атомарний shared_ptr на НЕЗМІННИЙ знімок (const Table)
    std::atomic<std::shared_ptr<const Table>> ref{std::make_shared<const Table>()};

public:
    // ЧИТАЧ: shared_ptr тримає знімок живим, читаємо без замка
    std::string route(const std::string& prefix) const {
        std::shared_ptr<const Table> snap = ref.load();   // атомарний load + утримання знімка
        auto it = snap->find(prefix);
        return it == snap->end() ? std::string{} : it->second;
    }

    // ПИСАР: копіюй-зміни-CAS; при провалі prev оновлюється сам
    void put(const std::string& prefix, const std::string& nextHop) {
        std::shared_ptr<const Table> prev = ref.load();
        std::shared_ptr<const Table> next;
        do {
            auto draft = std::make_shared<Table>(*prev);  // мутабельна копія знімка
            (*draft)[prefix] = nextHop;
            next = std::move(draft);                       // shared_ptr<Table> → shared_ptr<const Table>
        } while (!ref.compare_exchange_weak(prev, next));  // збіг → prev = поточне, ще коло
    }
};
