#include <cstdint>
#include <span>
#include <vector>
#include <string_view>
#include <memory>

namespace sys {

class bloom_filter {
public:
    // Конструктор створює фільтр на основі очікуваної ємності n та бажаної помилки p
    explicit bloom_filter(std::size_t expected_elements, double false_positive_rate);
    
    // Заборона копіювання задля уникнення важких алокацій
    bloom_filter(const bloom_filter&) = delete;
    bloom_filter& operator=(const bloom_filter&) = delete;

    // Підтримка семантики переміщення
    bloom_filter(bloom_filter&&) noexcept = default;
    bloom_filter& operator=(bloom_filter&&) noexcept = default;
    ~bloom_filter() noexcept = default;

    // Вставка байтових ключів та рядкових представлень
    void add(std::span<const std::uint8_t> key) noexcept;
    void add(std::string_view key) noexcept;
    
    // Перевірка наявності ключів у фільтрі
    [[nodiscard]] bool contains(std::span<const std::uint8_t> key) const noexcept;
    [[nodiscard]] bool contains(std::string_view key) const noexcept;

    // Очищення структури та отримання метрик
    void clear() noexcept;
    [[nodiscard]] std::size_t size_in_bytes() const noexcept;
    [[nodiscard]] std::size_t element_count() const noexcept;
    [[nodiscard]] double current_false_positive_rate() const noexcept;

private:
    std::size_t num_bits_;
    std::size_t k_;
    std::size_t count_{0};
    std::vector<std::uint8_t> bits_;
};

} // namespace sys
