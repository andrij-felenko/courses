#pragma once
/*
 * fixed_pool.hpp — блоковий пул фіксованого розміру на C++20.
 *
 * Той самий вбудований список вільних блоків, що й у C, але типізований:
 * пул сам конструює об'єкт на місці й віддає unique_ptr, чий видаляч
 * повертає блок назад. Забути pool_free тут просто ніде.
 */
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <new>
#include <span>
#include <tuple>
#include <type_traits>
#include <utility>

namespace nofree {

template <typename T, std::size_t N>
class FixedPool {
    static_assert(N > 0u, "Пул без блоків не має сенсу");
    static_assert(sizeof(T) >= sizeof(void *), "Блок мусить умістити вузол списку вільних");
    static_assert(alignof(T) >= alignof(void *), "Вирівнювання типу мусить покривати вказівник");

public:
    FixedPool() noexcept { build_free_list(); }

    FixedPool(const FixedPool &)            = delete;
    FixedPool &operator=(const FixedPool &) = delete;

    /* Видаляч знає свій пул, тож unique_ptr повертає блок туди, звідки взяв. */
    struct Deleter {
        FixedPool *pool{nullptr};
        void operator()(T *object) const noexcept {
            if (pool != nullptr) {
                pool->destroy(object);
            }
        }
    };
    using UniquePtr = std::unique_ptr<T, Deleter>;

    /* Вимога nothrow-конструктора не примха: якби конструктор кинув виняток
       посеред placement new, блок лишився б поза списком вільних — тобто
       витік, від якого ми й тікали. Прошивка так чи так збирається без
       винятків, тож умову перевіряє компілятор. */
    template <typename... Args>
        requires std::is_nothrow_constructible_v<T, Args...>
    [[nodiscard]] UniquePtr make(Args &&...args) noexcept {
        void *raw = acquire();
        if (raw == nullptr) {
            return UniquePtr{nullptr, Deleter{this}};   /* пул вичерпано */
        }
        return UniquePtr{::new (raw) T(std::forward<Args>(args)...), Deleter{this}};
    }

    void destroy(T *object) noexcept {
        if (object == nullptr) {
            return;
        }
        object->~T();
        release(object);
    }

    [[nodiscard]] bool owns(const T *object) const noexcept {
        return in_storage(reinterpret_cast<const std::byte *>(object));
    }

    [[nodiscard]] std::size_t capacity() const noexcept      { return N; }
    [[nodiscard]] std::size_t available() const noexcept     { return free_count_; }
    [[nodiscard]] std::size_t min_available() const noexcept { return min_free_count_; }

private:
    struct Node {
        Node *next;
    };

    alignas(T) std::byte storage_[N * sizeof(T)]{};
    Node       *free_list_{nullptr};
    std::size_t free_count_{N};
    std::size_t min_free_count_{N};

    void build_free_list() noexcept {
        free_list_ = nullptr;
        for (std::size_t i = N; i-- > 0u;) {
            auto *node = reinterpret_cast<Node *>(&storage_[i * sizeof(T)]);
            node->next = free_list_;
            free_list_ = node;
        }
    }

    [[nodiscard]] bool in_storage(const std::byte *p) const noexcept {
        const auto *begin = static_cast<const std::byte *>(storage_);
        const auto *end   = begin + (N * sizeof(T));
        if (p < begin || p >= end) {
            return false;
        }
        return (static_cast<std::size_t>(p - begin) % sizeof(T)) == 0u;
    }

    [[nodiscard]] void *acquire() noexcept {
        if (free_list_ == nullptr) {
            return nullptr;
        }
        Node *node = free_list_;
        free_list_ = node->next;
        --free_count_;
        min_free_count_ = std::min(min_free_count_, free_count_);
        return static_cast<void *>(node);
    }

    void release(void *raw) noexcept {
        /* Остання лінія оборони: свій видаляч дає лише правильні адреси, але
           destroy() публічний, і туди може прилетіти будь-що. */
        if (!in_storage(static_cast<const std::byte *>(raw)) || free_count_ >= N) {
            return;
        }
        auto *node = reinterpret_cast<Node *>(raw);
        node->next = free_list_;
        free_list_ = node;
        ++free_count_;
    }
};

/* ------------------------------------------------------------------ */
/*  Каскад пулів: кілька градацій розміру сирого блоку                  */
/* ------------------------------------------------------------------ */

template <std::size_t BlockSize, std::size_t Count>
class RawPool {
    struct Node {
        Node *next;
    };
    static constexpr std::size_t align_v = alignof(std::max_align_t);
    static constexpr std::size_t rounded = ((BlockSize + align_v - 1u) / align_v) * align_v;

public:
    static constexpr std::size_t block_size  = rounded < sizeof(Node) ? sizeof(Node) : rounded;
    static constexpr std::size_t block_count = Count;

    RawPool() noexcept { build_free_list(); }

    RawPool(const RawPool &)            = delete;
    RawPool &operator=(const RawPool &) = delete;

    [[nodiscard]] std::span<std::byte> allocate() noexcept {
        if (free_list_ == nullptr) {
            return {};
        }
        Node *node = free_list_;
        free_list_ = node->next;
        --free_count_;
        min_free_count_ = std::min(min_free_count_, free_count_);
        return std::span<std::byte>{reinterpret_cast<std::byte *>(node), block_size};
    }

    bool deallocate(std::span<std::byte> block) noexcept {
        if (block.size() != block_size || !owns(block.data()) || free_count_ >= Count) {
            return false;
        }
        auto *node = reinterpret_cast<Node *>(block.data());
        node->next = free_list_;
        free_list_ = node;
        ++free_count_;
        return true;
    }

    [[nodiscard]] bool owns(const std::byte *p) const noexcept {
        const auto *begin = static_cast<const std::byte *>(storage_);
        const auto *end   = begin + sizeof(storage_);
        if (p < begin || p >= end) {
            return false;
        }
        return (static_cast<std::size_t>(p - begin) % block_size) == 0u;
    }

    [[nodiscard]] std::size_t available() const noexcept     { return free_count_; }
    [[nodiscard]] std::size_t min_available() const noexcept { return min_free_count_; }

private:
    alignas(std::max_align_t) std::byte storage_[block_size * Count]{};
    Node       *free_list_{nullptr};
    std::size_t free_count_{Count};
    std::size_t min_free_count_{Count};

    void build_free_list() noexcept {
        free_list_ = nullptr;
        for (std::size_t i = Count; i-- > 0u;) {
            auto *node = reinterpret_cast<Node *>(&storage_[i * block_size]);
            node->next = free_list_;
            free_list_ = node;
        }
    }
};

template <class... Pools>
class PoolSet {
    static_assert(sizeof...(Pools) > 0u, "Каскад без жодного класу порожній");

    static constexpr bool ascending = [] {
        constexpr std::size_t sizes[] = {Pools::block_size...};
        for (std::size_t i = 1u; i < sizeof...(Pools); ++i) {
            if (sizes[i] <= sizes[i - 1u]) {
                return false;
            }
        }
        return true;
    }();
    static_assert(ascending, "Класи пулів мусять іти за зростанням розміру блоку");

public:
    /* Клас добирається розгорткою на етапі компіляції: у машинному коді
       лишається ланцюжок порівнянь із константами, а не цикл пошуку. */
    [[nodiscard]] std::span<std::byte> allocate(std::size_t bytes) noexcept {
        std::span<std::byte> result{};
        if (bytes == 0u) {
            return result;
        }
        std::apply(
            [&](auto &...pool) {
                auto attempt = [&](auto &candidate) noexcept {
                    using Pool = std::remove_reference_t<decltype(candidate)>;
                    if (Pool::block_size < bytes) {
                        return false;          /* клас замалий — беремо наступний */
                    }
                    /* Свій клас знайдено. Якщо він порожній, у старший НЕ
                       падаємо: чужий бюджет не наш ресурс. */
                    result = candidate.allocate();
                    return true;
                };
                (void)(attempt(pool) || ...);
            },
            pools_);
        return result;
    }

    bool deallocate(std::span<std::byte> block) noexcept {
        if (block.empty()) {
            return false;
        }
        bool done = false;
        std::apply(
            [&](auto &...pool) {
                (void)((pool.owns(block.data()) ? (done = pool.deallocate(block), true)
                                                : false) ||
                       ...);
            },
            pools_);
        return done;
    }

private:
    std::tuple<Pools...> pools_{};
};

}  // namespace nofree
