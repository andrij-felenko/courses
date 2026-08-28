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
