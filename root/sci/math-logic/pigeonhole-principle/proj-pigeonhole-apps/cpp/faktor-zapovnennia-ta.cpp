#include <iostream>
#include <vector>
#include <optional>

class LinearProbingHashTable {
    struct Entry {
        int key;
        int value;
        bool occupied{false};
    };

    std::vector<Entry> entries_;
    size_t count_{0};

public:
    explicit LinearProbingHashTable(size_t capacity) : entries_(capacity) {}

    bool insert(int key, int value, size_t& collision_count) {
        if (count_ >= entries_.size()) {
            // За принципом Діріхле таблиця повна — вставка неможлива без розширення
            return false;
        }

        size_t hash = static_cast<size_t>(key) % entries_.size();
        size_t idx = hash;
        collision_count = 0;

        while (entries_[idx].occupied) {
            if (entries_[idx].key == key) {
                entries_[idx].value = value;
                return true;
            }
            collision_count++;
            idx = (idx + 1) % entries_.size();
        }

        entries_[idx] = {key, value, true};
        count_++;
        return true;
    }

    [[nodiscard]] size_t size() const { return count_; }
    [[nodiscard]] size_t capacity() const { return entries_.size(); }
};

int main() {
    const size_t capacity = 5;
    LinearProbingHashTable ht(capacity);

    std::cout << "=== Хеш-таблиця з відкритою адресацією (M = " << capacity << ") ===\n";
    const std::vector<int> keys = { 10, 15, 20, 25, 30, 35 };

    for (size_t i = 0; i < keys.size(); ++i) {
        size_t collisions = 0;
        if (ht.insert(keys[i], static_cast<int>(i + 1) * 100, collisions)) {
            std::cout << "Ключ " << keys[i] << " додано (колізій: " << collisions 
                      << "). Заповнення: " << ht.size() << "/" << ht.capacity() << "\n";
        } else {
            std::cout << "Ключ " << keys[i] << " ВІДХИЛЕНО: спрацювала межа Діріхле! ("
                      << ht.size() << "/" << ht.capacity() << ")\n";
        }
    }
    return 0;
}
