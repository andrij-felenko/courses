#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <memory>
#include <expected>
#include <concepts>

namespace sys::bloom {

// Типізовані коди помилок системного рівня
enum class Error : int32_t {
    InvalidArguments = -1,
    OutOfMemory      = -2,
    CorruptedData    = -3,
    IoError          = -4
};

// Параметри створення фільтра Блума
struct Config {
    size_t expected_entries{1'000'000};
    double target_fp_rate{0.01};
    uint32_t seed{0x9e3779b9};
    bool cache_aligned{true};
};

class BloomFilter {
public:
    // Безпечний фабричний метод створення екземпляра
    static std::expected<BloomFilter, Error> create(const Config& cfg) noexcept;

    // Конструктори переміщення (Move semantics)
    BloomFilter(BloomFilter&&) noexcept = default;
    BloomFilter& operator=(BloomFilter&&) noexcept = default;

    // Заборона копіювання для запобігання дублювання великих масивів пам'яті
    BloomFilter(const BloomFilter&) = delete;
    BloomFilter& operator=(const BloomFilter&) = delete;

    ~BloomFilter() = default;

    // Запис елементів довільних типів даних
    void add(std::span<const std::byte> key) noexcept;
    void add(std::string_view key) noexcept;
    void add(uint64_t key) noexcept;

    // Перевірка належності ключів (константний неблокуючий доступ)
    [[nodiscard]] bool contains(std::span<const std::byte> key) const noexcept;
    [[nodiscard]] bool contains(std::string_view key) const noexcept;
    [[nodiscard]] bool contains(uint64_t key) const noexcept;

    // Очищення вмісту бітового масиву
    void clear() noexcept;

    // Інформаційні методи стану
    [[nodiscard]] size_t memory_bytes() const noexcept;
    [[nodiscard]] size_t bit_capacity() const noexcept;
    [[nodiscard]] uint32_t hash_count() const noexcept;

    // Двійкова серіалізація та відновлення стану
    [[nodiscard]] size_t serialized_size() const noexcept;
    std::expected<void, Error> serialize(std::span<std::byte> destination) const noexcept;
    static std::expected<BloomFilter, Error> deserialize(std::span<const std::byte> source) noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
    explicit BloomFilter(std::unique_ptr<Impl> impl) noexcept;
};

} // namespace sys::bloom
