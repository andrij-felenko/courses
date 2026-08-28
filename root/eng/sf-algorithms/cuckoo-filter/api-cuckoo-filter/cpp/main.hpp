#include <cstddef>
#include <cstdint>
#include <string_view>
#include <optional>
#include <concepts>

template <
    typename KeyType = std::string_view,
    size_t BucketSize = 4,
    size_t FingerprintBits = 8,
    size_t MaxKicks = 500
>
class cuckoo_filter {
public:
    using key_type = KeyType;
    using fingerprint_type = std::conditional_t<
        (FingerprintBits <= 8), uint8_t,
        std::conditional_t<(FingerprintBits <= 16), uint16_t, uint32_t>
    >;

    explicit cuckoo_filter(size_t expected_capacity, double target_fpr = 0.01);
    ~cuckoo_filter() = default;

    cuckoo_filter(const cuckoo_filter &) = default;
    cuckoo_filter &operator=(const cuckoo_filter &) = default;
    cuckoo_filter(cuckoo_filter &&) noexcept = default;
    cuckoo_filter &operator=(cuckoo_filter &&) noexcept = default;

    /* Вставка ключа (повертає true у разі успіху, false при переповненні) */
    [[nodiscard]] bool insert(const KeyType &key);

    /* Перевірка належності (константний час, без блокувань) */
    [[nodiscard]] bool contains(const KeyType &key) const noexcept;

    /* Видалення одного екземпляра ключа */
    [[nodiscard]] bool erase(const KeyType &key) noexcept;

    /* Отримання метрик стану структури */
    [[nodiscard]] size_t size() const noexcept;
    [[nodiscard]] size_t capacity() const noexcept;
    [[nodiscard]] double load_factor() const noexcept;
    [[nodiscard]] size_t memory_bytes() const noexcept;

    /* Очищення фільтра */
    void clear() noexcept;
};
