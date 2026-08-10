# ⚙️ Практика: реалізація кільця консистентного хешування

Теорія консистентного хешування стає зрозумілою на 100%, коли її втілено в робочий код. Головна операційна задача — побудувати структури даних для кільця, які дозволяють:
1. **Додавати фізичний вузол** із `V` віртуальними вузлами за час `O(V log M)`, де `M = N·V` — загальна кількість vnodes на кільці.
2. **Вилучати фізичний вузол** та всі його vnodes за `O(V log M)`.
3. **Шукати вузол-наступник для ключа** (за годинниковою стрілкою) за логарифмічний час `O(log M)` за допомогою двійкового пошуку.

Нижче наведено повноцінні, готові до використання реалізації кільця консистентного хешування мовами **C++** (з використанням `std::map` та алгоритму FNV-1a) та **Python** (з використанням `bisect` та `hashlib`).

:::tabs
```cpp
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
```
```py
import hashlib
import bisect
from typing import Dict, List, Optional

class ConsistentHashRing:
    def __init__(self, num_vnodes: int = 100):
        """
        Ініціалізація кільця консистентного хешування.
        :param num_vnodes: Кількість віртуальних вузлів на кожен фізичний сервер.
        """
        self.num_vnodes = num_vnodes
        self.ring: Dict[int, str] = {}         # vnode_hash -> physical_node_id
        self.sorted_keys: List[int] = []        # Впорядкований список хешів vnodes
        self.physical_nodes: set = set()

    def _hash(self, key: str) -> int:
        """32-бітний хеш на основі MD5 для рівномірного розсіювання."""
        md5_hex = hashlib.md5(key.encode('utf-8')).hexdigest()
        # Беремо перші 8 шістнадцяткових символів (32 біти)
        return int(md5_hex[:8], 16)

    def add_node(self, node_id: str) -> None:
        """Додає фізичний вузол із створенням V віртуальних вузлів."""
        if node_id in self.physical_nodes:
            return
        self.physical_nodes.add(node_id)

        for i in range(self.num_vnodes):
            vnode_key = f"{node_id}#vnode{i}"
            vnode_hash = self._hash(vnode_key)
            self.ring[vnode_hash] = node_id
            bisect.insort(self.sorted_keys, vnode_hash)

    def remove_node(self, node_id: str) -> None:
        """Вилучає фізичний вузол та всі його vnodes з кільця."""
        if node_id not in self.physical_nodes:
            return
        self.physical_nodes.remove(node_id)

        for i in range(self.num_vnodes):
            vnode_key = f"{node_id}#vnode{i}"
            vnode_hash = self._hash(vnode_key)
            if vnode_hash in self.ring:
                del self.ring[vnode_hash]
                idx = bisect.bisect_left(self.sorted_keys, vnode_hash)
                if idx < len(self.sorted_keys) and self.sorted_keys[idx] == vnode_hash:
                    del self.sorted_keys[idx]

    def get_node(self, key: str) -> Optional[str]:
        """
        Знаходить відповідальний вузол для заданого ключа.
        Шукає найближчий vnode за годинниковою стрілкою за O(log M).
        """
        if not self.ring:
            return None

        key_hash = self._hash(key)
        # Двійковий пошук першого vnode_hash >= key_hash
        idx = bisect.bisect_left(self.sorted_keys, key_hash)

        # Замикання кільця (wrap-around)
        if idx == len(self.sorted_keys):
            idx = 0

        target_vnode_hash = self.sorted_keys[idx]
        return self.ring[target_vnode_hash]


# Демонстраційна програма
if __name__ == "__main__":
    # Створюємо кільце з 150 vnodes на сервер
    ch = ConsistentHashRing(num_vnodes=150)

    # 1. Додаємо 3 сервери
    servers = ["Node-Alpha", "Node-Beta", "Node-Gamma"]
    for s in servers:
        ch.add_node(s)

    print(f"Кільце створено: {len(servers)} серверів, {len(ch.sorted_keys)} vnodes.")

    # 2. Розподіляємо 10,000 ключів
    num_keys = 10000
    initial_mapping = {}
    stats: Dict[str, int] = {s: 0 for s in servers}

    for i in range(num_keys):
        key = f"cache_key_user_{i}"
        node = ch.get_node(key)
        initial_mapping[key] = node
        stats[node] += 1

    print("\n--- Початковий розподіл навантаження ---")
    for s, count in stats.items():
        print(f"{s}: {count} ключів ({count / num_keys * 100:.2f}%)")

    # 3. Додаємо 4-й сервер Node-Delta
    print("\n>>> Додаємо новий сервер Node-Delta...")
    ch.add_node("Node-Delta")

    remapped_keys = 0
    new_stats: Dict[str, int] = {s: 0 for s in servers + ["Node-Delta"]}

    for key, old_node in initial_mapping.items():
        new_node = ch.get_node(key)
        new_stats[new_node] += 1
        if new_node != old_node:
            remapped_keys += 1

    print("\n--- Розподіл після додавання Node-Delta ---")
    for s, count in new_stats.items():
        print(f"{s}: {count} ключів ({count / num_keys * 100:.2f}%)")

    print(f"\nРебалансовано ключів: {remapped_keys} з {num_keys} ({remapped_keys / num_keys * 100:.2f}%)")
    print(f"Теоретичний мінімум 1/(N+1) = 1/4 = 25.0%")
```
:::

## Аналіз складности та тонкощі реалізації

### 1. Двійковий пошук за `O(log M)`
У реалізації на C++ контейнер `std::map` впорядковує ключі у вигляді червоно-чорного дерева. Метод `ring_.lower_bound(key_hash)` виконує двійковий пошук за час `O(log M)`, де `M = N·V`. 

У Python масив `sorted_keys` підтримується у відсортованому стані. Функція `bisect.bisect_left` знаходить потрібний індекс за `O(log M)`. Вставка `bisect.insort` при додаванні вузла займає `O(M)` через зсув елементів списку в пам'яті, проте операції додавання/вилучення серверів відбуваються рідко, тоді як пошук ключа `get_node` виконується мільйони разів на секунду й працює за `O(log M)`.

### 2. Замикання кільця (Wrap-around)
Кільцевий характер простору вимагає обробки граничного випадку: якщо `key_hash` виявився більшим за хеш **найостаннішого** vnode на кільці (`idx == len(sorted_keys)` в Python або `it == ring_.end()` у C++), пошук не повинен повертати помилку! У такому разі алгоритм робить один крок «через нуль» і повертає **найперший** vnode на кільці (`ring_.begin()` або `sorted_keys[0]`).

### 3. Хеш-функція
Для консистентного хешування важливо використовувати швидкі некриптографічні хеш-функції з високою якістю перемішування бітів (наприклад, MurmurHash3, FNV-1a або xxHash). Використання важких криптографічних хешів (SHA-256) є надлишковим і створює непотрібні витрати CPU на кожному запиті.
