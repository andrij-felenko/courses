#include <vector>
#include <cstdint>
#include <cstring>
#include <string>
#include <type_traits>
#include <iostream>

template<typename> inline constexpr bool dependent_false_v = false;

// Допоміжний трейт для виявлення контейнерів std::vector
template<typename> struct is_vector : std::false_type {};
template<typename T, typename Alloc> 
struct is_vector<std::vector<T, Alloc>> : std::true_type {};

class BinaryStreamWriter {
public:
    template<typename T>
    void write(const T& value) {
        using CleanType = std::decay_t<T>;

        if constexpr (std::is_trivially_copyable_v<CleanType> && !std::is_pointer_v<CleanType>) {
            // Шлях 1: Пряме копіювання байтів пам'яті для POD-типів
            const auto* byte_ptr = reinterpret_cast<const uint8_t*>(&value);
            buffer_.insert(buffer_.end(), byte_ptr, byte_ptr + sizeof(CleanType));
        } else if constexpr (std::is_same_v<CleanType, std::string>) {
            // Шлях 2: Рядки серіалізуються як довжина (uint32_t) + символи
            auto length = static_cast<uint32_t>(value.size());
            write(length);
            buffer_.insert(buffer_.end(), value.data(), value.data() + length);
        } else if constexpr (is_vector<CleanType>::value) {
            // Шлях 3: Вектори серіалізуються рекурсивно
            auto count = static_cast<uint32_t>(value.size());
            write(count);
            for (const auto& element : value) {
                write(element);
            }
        } else {
            static_assert(dependent_false_v<CleanType>, 
                          "Тип не підтримує двійкову серіалізацію!");
        }
    }

    [[nodiscard]] const std::vector<uint8_t>& get_buffer() const noexcept {
        return buffer_;
    }

    [[nodiscard]] std::size_t size_bytes() const noexcept {
        return buffer_.size();
    }

private:
    std::vector<uint8_t> buffer_;
};
