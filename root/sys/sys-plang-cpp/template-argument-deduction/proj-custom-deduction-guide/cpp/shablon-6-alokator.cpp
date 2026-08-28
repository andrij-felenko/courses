#include <memory>
#include <string>
#include <string_view>
#include <mutex>
#include <type_traits>
#include <iostream>

template<
    typename Key, 
    typename Value, 
    typename Alloc = std::allocator<std::pair<const Key, Value>>
>
class ThreadSafeCache {
public:
    using key_type = Key;
    using mapped_type = Value;
    using allocator_type = Alloc;

    // Конструктор за замовчуванням
    explicit ThreadSafeCache(const Alloc& alloc = Alloc{})
        : m_alloc(alloc) {}

    // Конструктор з ініціалізацією першого запису
    ThreadSafeCache(Key key, Value val, const Alloc& alloc = Alloc{})
        : m_last_key(std::move(key)), m_last_value(std::move(val)), m_alloc(alloc) {}

    // Метод оновлення: type_identity_t блокує виведення Value з другого аргументу,
    // дозволяючи неявне приведення типів аргументу до вже відомого типу Value
    void update_value(const Key& key, std::type_identity_t<Value> val) {
        std::lock_guard<std::mutex> lock(m_mutex);
        m_last_key = key;
        m_last_value = std::move(val);
    }

    void dump_state() const {
        std::lock_guard<std::mutex> lock(m_mutex);
        std::cout << "[Cache State] Ключ: " << m_last_key 
                  << ", Значення: " << m_last_value << '\n';
    }

private:
    Key m_last_key{};
    Value m_last_value{};
    Alloc m_alloc{};
    mutable std::mutex m_mutex{};
};

// -----------------------------------------------------------------------------
// Керівне правило виведення (Deduction Guide)
// -----------------------------------------------------------------------------

template<
    typename Key, 
    typename Value, 
    typename Alloc = std::allocator<std::pair<const std::decay_t<Key>, std::decay_t<Value>>>>
ThreadSafeCache(Key&&, Value&&, Alloc = Alloc{}) 
    -> ThreadSafeCache<std::decay_t<Key>, std::decay_t<Value>, Alloc>;
