#pragma once

// Куча, яка вміє назвати найбільший суцільний блок.
//
// Реалізована як std::pmr::memory_resource: контейнери й рядки прошивки
// беруть її як звичайний розподільник (std::pmr::vector, std::pmr::string),
// а підсистема аудиту питає в неї не лише «скільки вільно», а й «який
// найбільший неперервний шматок» — саме на цьому питанні гине довгопрацюючий
// пристрій, коли вільної пам'яті ще вдосталь, а суцільної вже немає.

#include "budget/flags.hpp"

#include <cstddef>
#include <memory_resource>
#include <span>

namespace budget {

class FragmentAwareResource final : public std::pmr::memory_resource {
public:
    struct Stats {
        std::size_t capacity{0};
        std::size_t used{0};
        std::size_t free_total{0};
        std::size_t largest_free{0};
        std::size_t free_blocks{0};   // кількість розривів у вільному просторі
        std::size_t failures{0};      // відмови у виділенні
        double      fragmentation{0}; // 1 - largest/free
    };

    // Арена має пережити розподільник; менша за заголовок арена неприйнятна.
    explicit FragmentAwareResource(std::span<std::byte> arena);

    FragmentAwareResource(const FragmentAwareResource&) = delete;
    FragmentAwareResource& operator=(const FragmentAwareResource&) = delete;

    [[nodiscard]] Stats stats() const noexcept;

    [[nodiscard]] Budget audit(std::size_t min_free_bytes,
                               std::size_t min_largest_bytes) const noexcept;

protected:
    void* do_allocate(std::size_t bytes, std::size_t alignment) override;
    void  do_deallocate(void* ptr, std::size_t bytes,
                        std::size_t alignment) noexcept override;
    [[nodiscard]] bool do_is_equal(
        const std::pmr::memory_resource& other) const noexcept override;

private:
    struct Block {
        Block*      next;
        Block*      prev;
        std::size_t size; // корисний розмір без заголовка
        bool        used;
    };

    static constexpr std::size_t kAlign = alignof(std::max_align_t);

    [[nodiscard]] static constexpr std::size_t align_up(std::size_t value) noexcept
    {
        return (value + kAlign - 1) & ~(kAlign - 1);
    }

    [[nodiscard]] static constexpr std::size_t header_size() noexcept
    {
        return align_up(sizeof(Block));
    }

    [[nodiscard]] bool owns(const Block* block) const noexcept;

    Block*      head_{nullptr};
    std::size_t capacity_{0};
    std::size_t used_{0};
    std::size_t failures_{0};
};

} // namespace budget
