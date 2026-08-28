#include <cstddef>
#include <new>
#include <utility>
#include <memory>
#include <string>
#include <iostream>
#include <cstdint>
#include <stdexcept>

template <typename T, std::size_t Capacity>
class ObjectPool {
public:
    ObjectPool() : free_head_(nullptr) {
        // Формуємо однозв'язний список вільних слотів усередині статичного масиву
        for (std::size_t i = 0; i < Capacity; ++i) {
            auto* node = reinterpret_cast<FreeNode*>(&storage_[i]);
            node->next = free_head_;
            free_head_ = node;
        }
    }

    // Забороняємо копіювання пулу (він володіє унікальним буфером)
    ObjectPool(const ObjectPool&) = delete;
    ObjectPool& operator=(const ObjectPool&) = delete;

    ~ObjectPool() {
        // Пул звільняє саму пам'ять (storage_ знищується автоматично).
        // Усі активні об'єкти мали бути знищені клієнтом перед смертю пулу.
    }

    template <typename... Args>
    T* create(Args&&... args) {
        if (!free_head_) {
            return nullptr; // Пул повністю вичерпано
        }

        // 1. Вилучаємо перший вільний слот із голови списку (O(1))
        FreeNode* node = free_head_;
        free_head_ = node->next;
        void* raw_memory = static_cast<void*>(node);

        // 2. Фаза народження: placement new викликає конструктор T на сирій адресі
        try {
            return ::new (raw_memory) T(std::forward<Args>(args)...);
        } catch (...) {
            // Гарантія безпеки винятків: якщо конструктор T викинув виняток,
            // повертаємо сирий слот назад у список, щоб уникнути витоку пам'яті
            node->next = free_head_;
            free_head_ = node;
            throw;
        }
    }

    void destroy(T* obj) noexcept {
        if (!obj) return;

        // 1. Фаза смерті: явний виклик деструктора (звільняє внутрішні ресурси T)
        std::destroy_at(obj); // Еквівалент obj->~T() у C++17/20

        // 2. Повернення слота сирої пам'яті назад у вільний список (O(1), без виклику free)
        auto* node = reinterpret_cast<FreeNode*>(obj);
        node->next = free_head_;
        free_head_ = node;
    }

    // RAII-делетер для безпечного автоматичного повернення об'єкта в пул
    struct Deleter {
        ObjectPool* pool;
        void operator()(T* ptr) const noexcept {
            if (pool) pool->destroy(ptr);
        }
    };
    using UniquePtr = std::unique_ptr<T, Deleter>;

    template <typename... Args>
    UniquePtr acquire(Args&&... args) {
        T* raw = create(std::forward<Args>(args)...);
        if (!raw) {
            throw std::bad_alloc();
        }
        return UniquePtr(raw, Deleter{this});
    }

    std::size_t capacity() const noexcept { return Capacity; }

private:
    union FreeNode {
        FreeNode* next;
        // Гарантуємо правильне вирівнювання та розмір під тип T
        alignas(alignof(T)) std::byte data[sizeof(T)];
    };

    // Суцільний масив сирої пам'яті без виклику конструкторів T під час старту
    alignas(alignof(T)) FreeNode storage_[Capacity];
    FreeNode* free_head_;
};

// Демонстраційний клас із внутрішніми динамічними ресурсами
class Session {
public:
    Session(uint64_t id, std::string token)
        : id_(id), token_(std::move(token)) {
        std::cout << "  [+] Session #" << id_ << " створено (токен: " << token_ << ")\n";
    }

    ~Session() {
        std::cout << "  [-] Session #" << id_ << " знищено (пам'ять токена звільнено)\n";
    }

    void ping() const {
        std::cout << "  [*] Session #" << id_ << " активна\n";
    }

private:
    uint64_t id_;
    std::string token_;
};

int main() {
    ObjectPool<Session, 2> pool;

    std::cout << "1. Створення об'єктів у пулі через RAII acquire:\n";
    {
        auto s1 = pool.acquire(101ULL, "tok_auth_abc");
        auto s2 = pool.acquire(102ULL, "tok_auth_xyz");

        s1->ping();
        s2->ping();

        std::cout << "2. Вихід із внутрішньої області видимості:\n";
    } // s1 і s2 виходять зі scope: деструктори Session викликаються автоматично,
      // а слоти повертаються назад у free_head_ пулу

    std::cout << "3. Повторне використання слотів без жодної алокації в купі:\n";
    auto s3 = pool.acquire(103ULL, "tok_auth_reused");
    s3->ping();

    return 0;
}
