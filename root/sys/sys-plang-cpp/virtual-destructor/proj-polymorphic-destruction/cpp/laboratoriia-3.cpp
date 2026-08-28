#include <iostream>
#include <cstddef>
#include <vector>
#include <cassert>

// Модель пулу пам'яті з корзинами для різних розмірів
class SimpleSegregatedAllocator {
    static constexpr std::size_t BIN_SMALL = 8;
    static constexpr std::size_t BIN_LARGE = 128;

    std::vector<void*> free_list_small;
    std::vector<void*> free_list_large;

public:
    void* allocate(std::size_t size) {
        if (size <= BIN_SMALL) {
            std::cout << "[ALLOC] Виділено з пулу SMALL (" << size << " байтів)\n";
            return ::operator new(BIN_SMALL);
        }
        std::cout << "[ALLOC] Виділено з пулу LARGE (" << size << " байтів)\n";
        return ::operator new(BIN_LARGE);
    }

    void deallocate(void* ptr, std::size_t size) {
        if (size <= BIN_SMALL) {
            std::cout << "[FREE]  Повернено в пул SMALL (" << size << " байтів) <-- ПОМИЛКА ДЕАЛОКАЦІЇ!\n";
            free_list_small.push_back(ptr);
        } else {
            std::cout << "[FREE]  Повернено в пул LARGE (" << size << " байтів)\n";
            free_list_large.push_back(ptr);
        }
    }
};

static SimpleSegregatedAllocator g_pool;

struct BaseNode {
    // Невіртуальний деструктор
    ~BaseNode() = default;

    static void* operator new(std::size_t sz) {
        return g_pool.allocate(sz);
    }
    static void operator delete(void* ptr, std::size_t sz) noexcept {
        g_pool.deallocate(ptr, sz);
    }
};

struct BigDataNode : public BaseNode {
    char raw_payload[120]{}; // Робить об'єкт великим (120 байтів)
    ~BigDataNode() = default;
};

int main() {
    std::cout << "=== Тест деалокації з точним розміром ===\n";
    std::cout << "sizeof(BaseNode):    " << sizeof(BaseNode) << " байтів\n";
    std::cout << "sizeof(BigDataNode): " << sizeof(BigDataNode) << " байтів\n\n";

    BaseNode* node = new BigDataNode();
    delete node; // Поліморфне видалення

    return 0;
}
