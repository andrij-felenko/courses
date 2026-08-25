# ⚙️ Практична реалізація: порівняльний аналіз стратегій пейджингу

Ця практична вставка містить робочу реалізацію чотирьох алгоритмів заміни сторінок кешу: FIFO, LRU, рандомізованого алгоритму Маркера (Marker Algorithm) та ідеального офлайнового оптимуму Бєладі (OPT). Код розроблений мовами C++ та Python у вигляді інтерактивного стенду симуляції для вимірювання реальної ефективності онлайнових алгоритмів проти теоретичних меж.

## Структура симулятора кешу

Для порівняльного аналізу реалізовано чотири стратегії:
1. **FIFO (First-In, First-Out)**: черга на базі кільцевого буфера або списку. Вивантажує найстарішу за часом завантаження сторінку.
2. **LRU (Least Recently Used)**: двозв'язний список плюс хеш-мапа для пошуку за O(1). При кожному зверненні сторінка переміщується в початок списку; при вивантаженні видаляється елемент з хвоста.
3. **Marker Algorithm (Рандомізований маркер Фіата)**: робота розбивається на фази. Кожна сторінка має біт маркування (marked). При влучанні або завантаженні біт встановлюється в true. Якщо при промаху всі сторінки в кеші виявляються замаркованими, починається нова фаза (усі біти скидаються в false). Для вивантаження випадковим чином обирається одна з незамаркованих (unmarked) сторінок.
4. **Bélády OPT (Офлайновий пророк)**: сканує послідовність запитів наперед і вивантажує сторінку, до якої наступне звернення станеться найпізніше в майбутньому.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <list>
#include <unordered_map>
#include <unordered_set>
#include <random>
#include <algorithm>
#include <iomanip>

// 1. Алгоритм FIFO
class FIFOCache {
    size_t capacity;
    std::list<int> queue;
    std::unordered_set<int> in_cache;
    size_t misses = 0;

public:
    explicit FIFOCache(size_t cap) : capacity(cap) {}

    void access(int page) {
        if (in_cache.find(page) != in_cache.end()) {
            return; // Hit
        }
        misses++;
        if (queue.size() == capacity) {
            int evicted = queue.front();
            queue.pop_front();
            in_cache.erase(evicted);
        }
        queue.push_back(page);
        in_cache.insert(page);
    }

    size_t getMisses() const { return misses; }
};

// 2. Алгоритм LRU (O(1) на кожне звернення)
class LRUCache {
    size_t capacity;
    std::list<int> items; // head = найновіші, tail = найдавніші
    std::unordered_map<int, std::list<int>::iterator> cache_map;
    size_t misses = 0;

public:
    explicit LRUCache(size_t cap) : capacity(cap) {}

    void access(int page) {
        auto it = cache_map.find(page);
        if (it != cache_map.end()) {
            // Hit: переміщуємо в початок
            items.erase(it->second);
            items.push_front(page);
            cache_map[page] = items.begin();
            return;
        }
        misses++;
        if (items.size() == capacity) {
            int evicted = items.back();
            items.pop_back();
            cache_map.erase(evicted);
        }
        items.push_front(page);
        cache_map[page] = items.begin();
    }

    size_t getMisses() const { return misses; }
};

// 3. Рандомізований алгоритм Маркера (Marker Algorithm)
class MarkerCache {
    size_t capacity;
    std::unordered_set<int> cache;
    std::unordered_set<int> marked;
    std::mt19937 rng;
    size_t misses = 0;

public:
    MarkerCache(size_t cap, uint32_t seed = 42) : capacity(cap), rng(seed) {}

    void access(int page) {
        if (cache.find(page) != cache.end()) {
            marked.insert(page);
            return; // Hit
        }

        misses++;
        if (cache.size() == capacity) {
            // Перевіряємо, чи всі замарковані (кінець фази)
            if (marked.size() == capacity) {
                marked.clear(); // Скидання фази
            }

            // Знаходимо всі незамарковані сторінки в кеші
            std::vector<int> unmarked;
            for (int p : cache) {
                if (marked.find(p) == marked.end()) {
                    unmarked.push_back(p);
                }
            }

            // Вибираємо випадкову незамарковану сторінку для вивантаження
            std::uniform_int_axis<size_t> dist(0, unmarked.size() - 1);
            std::uniform_int_distribution<size_t> d(0, unmarked.size() - 1);
            int evicted = unmarked[d(rng)];

            cache.erase(evicted);
        }

        cache.insert(page);
        marked.insert(page);
    }

    size_t getMisses() const { return misses; }
};

// 4. Ідеальний Офлайновий Алгоритм Бєладі (OPT)
class BeladyOPT {
    size_t capacity;

public:
    explicit BeladyOPT(size_t cap) : capacity(cap) {}

    size_t simulate(const std::vector<int>& stream) {
        std::unordered_set<int> cache;
        size_t misses = 0;

        for (size_t i = 0; i < stream.size(); ++i) {
            int page = stream[i];
            if (cache.find(page) != cache.end()) {
                continue; // Hit
            }

            misses++;
            if (cache.size() == capacity) {
                // Шукаємо сторінку у кеші, яка знадобиться найпізніше в майбутньому
                int page_to_evict = -1;
                size_t farthest_next_use = 0;

                for (int cached_page : cache) {
                    size_t next_use = stream.size() + 1; // За замовчуванням не знадобиться
                    for (size_t j = i + 1; j < stream.size(); ++j) {
                        if (stream[j] == cached_page) {
                            next_use = j;
                            break;
                        }
                    }
                    if (next_use > farthest_next_use) {
                        farthest_next_use = next_use;
                        page_to_evict = cached_page;
                    }
                }
                cache.erase(page_to_evict);
            }
            cache.insert(page);
        }
        return misses;
    }
};

int main() {
    const size_t CACHE_SIZE = 4;
    // Потік запитів із локальністю та декількома промахами
    std::vector<int> stream = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5, 3, 2, 1, 4, 5};

    FIFOCache fifo(CACHE_SIZE);
    LRUCache lru(CACHE_SIZE);
    MarkerCache marker(CACHE_SIZE, 12345);
    BeladyOPT opt(CACHE_SIZE);

    for (int page : stream) {
        fifo.access(page);
        lru.access(page);
        marker.access(page);
    }

    size_t opt_misses = opt.simulate(stream);

    std::cout << "--- Симуляція кешування (Розмір кешу k = " << CACHE_SIZE << ") ---\n";
    std::cout << "Всього запитів: " << stream.size() << "\n\n";
    std::cout << std::left << std::setw(18) << "Алгоритм" 
              << std::setw(15) << "Промахи" 
              << "Співвідношення до OPT\n";
    std::cout << "-----------------------------------------------------\n";
    std::cout << std::setw(18) << "OPT (Бєладі)" << std::setw(15) << opt_misses << "1.00 (Бенчмарк)\n";
    std::cout << std::setw(18) << "LRU" << std::setw(15) << lru.getMisses() 
              << std::fixed << std::setprecision(2) << (double)lru.getMisses() / opt_misses << "\n";
    std::cout << std::setw(18) << "FIFO" << std::setw(15) << fifo.getMisses() 
              << (double)fifo.getMisses() / opt_misses << "\n";
    std::cout << std::setw(18) << "Marker (Random)" << std::setw(15) << marker.getMisses() 
              << (double)marker.getMisses() / opt_misses << "\n";

    return 0;
}
```
```py
import random
from collections import deque

class FIFOCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.queue = deque()
        self.in_cache = set()
        self.misses = 0

    def access(self, page: int):
        if page in self.in_cache:
            return  # Hit
        self.misses += 1
        if len(self.queue) == self.capacity:
            evicted = self.queue.popleft()
            self.in_cache.remove(evicted)
        self.queue.append(page)
        self.in_cache.add(page)

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # page -> None (зберігає порядок вставки в Python 3.7+)
        self.misses = 0

    def access(self, page: int):
        if page in self.cache:
            # Move to end (most recent)
            del self.cache[page]
            self.cache[page] = None
            return  # Hit
        self.misses += 1
        if len(self.cache) == self.capacity:
            # Evict first item (least recent)
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[page] = None

class MarkerCache:
    def __init__(self, capacity: int, seed: int = 42):
        self.capacity = capacity
        self.cache = set()
        self.marked = set()
        self.rng = random.Random(seed)
        self.misses = 0

    def access(self, page: int):
        if page in self.cache:
            self.marked.add(page)
            return  # Hit
        self.misses += 1
        if len(self.cache) == self.capacity:
            if len(self.marked) == self.capacity:
                self.marked.clear()  # Скидання фази
            unmarked = list(self.cache - self.marked)
            evicted = self.rng.choice(unmarked)
            self.cache.remove(evicted)
        self.cache.add(page)
        self.marked.add(page)

class BeladyOPT:
    def __init__(self, capacity: int):
        self.capacity = capacity

    def simulate(self, stream: list[int]) -> int:
        cache = set()
        misses = 0
        for i, page in enumerate(stream):
            if page in cache:
                continue
            misses += 1
            if len(cache) == self.capacity:
                # Знаходимо сторінку з найдальшим майбутнім використанням
                farthest_page = None
                farthest_idx = -1
                for cached_page in cache:
                    try:
                        next_idx = stream.index(cached_page, i + 1)
                    except ValueError:
                        next_idx = float('inf')
                    if next_idx > farthest_idx:
                        farthest_idx = next_idx
                        farthest_page = cached_page
                cache.remove(farthest_page)
            cache.insert = cache.add(page)
        return misses

if __name__ == "__main__":
    CACHE_SIZE = 4
    stream = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5, 3, 2, 1, 4, 5]

    fifo = FIFOCache(CACHE_SIZE)
    lru = LRUCache(CACHE_SIZE)
    marker = MarkerCache(CACHE_SIZE, 12345)
    opt = BeladyOPT(CACHE_SIZE)

    for p in stream:
        fifo.access(p)
        lru.access(p)
        marker.access(p)

    opt_misses = opt.simulate(stream)

    print(f"--- Результати симуляції (k = {CACHE_SIZE}) ---")
    print(f"{'Алгоритм':<18} | {'Промахи':<10} | {'Ratio (ALG/OPT)'}")
    print("-" * 45)
    print(f"{'OPT (Бєладі)':<18} | {opt_misses:<10} | 1.00")
    print(f"{'LRU':<18} | {lru.misses:<10} | {lru.misses / opt_misses:.2f}")
    print(f"{'FIFO':<18} | {fifo.misses:<10} | {fifo.misses / opt_misses:.2f}")
    print(f"{'Marker (Random)':<18} | {marker.misses:<10} | {marker.misses / opt_misses:.2f}")
```
:::

---

## Аналіз результатів та підводні камені

Запускаючи симуляцію на реальних профілях виконання (а не на синтетичному найгіршому випадку супротивника), можна зробити важливі спостереження:

1. **Локальність посилань (Locality of Reference)**: Реальні програми майже ніколи не генерують зациклені послідовності з k + 1 сторінок. Завдяки часовій локальності (повторне використання змінних та циклів), алгоритм LRU демонструє відношення промахів (ALG/OPT) на рівні 1.1–1.5, що набагато краще за песимістичне теоретичне k.
2. **Аномалія Бєладі у FIFO**: Алгоритм FIFO піддається так званій аномалії Бєладі — збільшення розміру кешу k для FIFO в деяких випадках призводить до **зростання** кількості промахів! LRU та Marker є стековими алгоритмами (stack algorithms) і вільні від цього недоліку.
3. **Практична перевага алгоритму Маркера**: Маркерний алгоритм поєднує низьку складність реалізації та логарифмічну теоретичну гарантію O(ln k), що робить його привабливим для розподілених кешів у мережевих сховищах (наприклад, у Memcached та Redis під час вивантаження за вибіркою).
