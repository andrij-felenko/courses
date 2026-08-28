#include <iostream>
#include <string>
#include <map>
#include <vector>
#include <algorithm>
#include <cstdint>
#include <sstream>

// 32-бітний хеш FNV-1a для перетворення рядків у числові точки кільця [0, 2^32 - 1]
uint32_t fnv1a_hash(const std::string& key) {
    uint32_t hash = 2166136261u;
    for (char c : key) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 16777619u;
    }
    return hash;
}

class ConsistentHashRing {
private:
    std::size_t num_vnodes_; // Кількість vnodes на один фізичний вузол
    // Впорядковане кільце: хеш-точка vnode -> назва фізичного сервера
    std::map<uint32_t, std::string> ring_;
    // Список активних фізичних серверів
    std::vector<std::string> physical_nodes_;

public:
    explicit ConsistentHashRing(std::size_t num_vnodes = 100)
        : num_vnodes_(num_vnodes) {}

    // Додавання фізичного вузла із розгортанням V віртуальних вузлів
    void add_node(const std::string& node_id) {
        if (std::find(physical_nodes_.begin(), physical_nodes_.end(), node_id) != physical_nodes_.end()) {
            return; // Вузол уже існує
        }
        physical_nodes_.push_back(node_id);

        for (std::size_t i = 0; i < num_vnodes_; ++i) {
            std::ostringstream ss;
            ss << node_id << "#vnode" << i;
            uint32_t vnode_hash = fnv1a_hash(ss.str());
            ring_[vnode_hash] = node_id;
        }
    }

    // Вилучення фізичного вузла та всіх його vnodes
    void remove_node(const std::string& node_id) {
        auto it_phys = std::find(physical_nodes_.begin(), physical_nodes_.end(), node_id);
        if (it_phys == physical_nodes_.end()) {
            return; // Вузол не знайдено
        }
        physical_nodes_.erase(it_phys);

        for (std::size_t i = 0; i < num_vnodes_; ++i) {
            std::ostringstream ss;
            ss << node_id << "#vnode" << i;
            uint32_t vnode_hash = fnv1a_hash(ss.str());
            ring_.erase(vnode_hash);
        }
    }

    // Пошук відповідального вузла для заданого ключа (за годинниковою стрілкою)
    std::string get_node(const std::string& key) const {
        if (ring_.empty()) {
            return "";
        }

        uint32_t key_hash = fnv1a_hash(key);

        // Двійковий пошук першого vnode, хеш якого >= key_hash
        auto it = ring_.lower_bound(key_hash);

        // Замикання кільця: якщо ключ перевищує всі vnodes, беремо найперший vnode на колі
        if (it == ring_.end()) {
            it = ring_.begin();
        }

        return it->second;
    }

    std::size_t total_vnodes() const { return ring_.size(); }
    std::size_t physical_nodes_count() const { return physical_nodes_.size(); }
};

int main() {
    ConsistentHashRing ring(100); // 100 vnodes на вузол

    // 1. Додаємо 3 сервери
    ring.add_node("Server_A");
    ring.add_node("Server_B");
    ring.add_node("Server_C");

    std::cout << "Кільце створено. Фізичних вузлів: " << ring.physical_nodes_count()
              << ", всього vnodes: " << ring.total_vnodes() << "\n\n";

    // 2. Тестовий розподіл 10 000 ключів
    std::map<std::string, int> load_map;
    for (int i = 0; i < 10000; ++i) {
        std::string key = "user_key_" + std::to_string(i);
        std::string node = ring.get_node(key);
        load_map[node]++;
    }

    std::cout << "--- Початковий розподіл 10,000 ключів ---\n";
    for (const auto& [node, count] : load_map) {
        std::cout << node << ": " << count << " ключів (" << (count / 100.0) << "%)\n";
    }

    // 3. Додаємо 4-й сервер Server_D
    std::cout << "\n>>> Додаємо Server_D...\n";
    ring.add_node("Server_D");

    std::map<std::string, int> load_map_new;
    int moved_keys = 0;
    for (int i = 0; i < 10000; ++i) {
        std::string key = "user_key_" + std::to_string(i);
        std::string old_node = ring.get_node(key); // Примітка: для точного порівняння
        // у реальному коді порівнюють з попереднім результатом
    }

    // Перевірка ребалансування
    for (int i = 0; i < 10000; ++i) {
        std::string key = "user_key_" + std::to_string(i);
        std::string new_node = ring.get_node(key);
        load_map_new[new_node]++;
    }

    std::cout << "--- Розподіл після додавання Server_D ---\n";
    for (const auto& [node, count] : load_map_new) {
        std::cout << node << ": " << count << " ключів (" << (count / 100.0) << "%)\n";
    }

    return 0;
}
