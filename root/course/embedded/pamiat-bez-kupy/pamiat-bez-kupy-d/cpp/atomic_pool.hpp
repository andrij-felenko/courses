#pragma once
/*
 * atomic_pool.hpp — блоковий пул, що не вимикає переривань.
 *
 * На ARMv7-M/ARMv8-M compare_exchange лягає на пару LDREX/STREX. Затримка
 * реакції на переривання не зростає: конфлікт коштує лише повторного кола.
 */
#include <atomic>
#include <cstddef>
#include <memory>
#include <new>
#include <type_traits>
#include <utility>

namespace nofree {

template <typename T, std::size_t N>
class AtomicFixedPool {
    static_assert(N > 0u, "Пул без блоків не має сенсу");
    static_assert(sizeof(T) >= sizeof(void *), "Блок мусить умістити вузол списку вільних");
    static_assert(alignof(T) >= alignof(void *), "Вирівнювання типу мусить покривати вказівник");

    struct Node {
        Node *next;
    };
    static_assert(std::atomic<Node *>::is_always_lock_free,
                  "Без апаратної пари LDREX/STREX атомарний пул сенсу не має");

public:
    AtomicFixedPool() noexcept {
        Node *head = nullptr;
        for (std::size_t i = N; i-- > 0u;) {
            auto *node = reinterpret_cast<Node *>(&storage_[i * sizeof(T)]);
            node->next = head;
            head       = node;
        }
        head_.store(head, std::memory_order_relaxed);
    }

    AtomicFixedPool(const AtomicFixedPool &)            = delete;
    AtomicFixedPool &operator=(const AtomicFixedPool &) = delete;

    struct Deleter {
        AtomicFixedPool *pool{nullptr};
        void operator()(T *object) const noexcept {
            if (pool != nullptr) {
                pool->destroy(object);
            }
        }
    };
    using UniquePtr = std::unique_ptr<T, Deleter>;

    template <typename... Args>
        requires std::is_nothrow_constructible_v<T, Args...>
    [[nodiscard]] UniquePtr make(Args &&...args) noexcept {
        void *raw = acquire();
        if (raw == nullptr) {
            return UniquePtr{nullptr, Deleter{this}};
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

    [[nodiscard]] std::size_t available() const noexcept {
        return free_count_.load(std::memory_order_relaxed);
    }
    [[nodiscard]] std::size_t min_available() const noexcept {
        return min_free_count_.load(std::memory_order_relaxed);
    }

private:
    alignas(T) std::byte storage_[N * sizeof(T)]{};
    std::atomic<Node *>      head_{nullptr};
    std::atomic<std::size_t> free_count_{N};
    std::atomic<std::size_t> min_free_count_{N};

    [[nodiscard]] void *acquire() noexcept {
        Node *head = head_.load(std::memory_order_relaxed);
        while (head != nullptr) {
            Node *next = head->next;
            /* acquire на успіху: дані блоку, які писав попередній власник,
               мусять стати видимими нам після захоплення голови. */
            if (head_.compare_exchange_weak(head, next,
                                            std::memory_order_acquire,
                                            std::memory_order_relaxed)) {
                note_taken();
                return static_cast<void *>(head);
            }
        }
        return nullptr;                    /* пул вичерпано */
    }

    void release(void *raw) noexcept {
        const auto *p     = static_cast<const std::byte *>(raw);
        const auto *begin = static_cast<const std::byte *>(storage_);
        const auto *end   = begin + (N * sizeof(T));
        if (p < begin || p >= end || (static_cast<std::size_t>(p - begin) % sizeof(T)) != 0u) {
            return;                        /* чужа адреса — ланцюжок не чіпаємо */
        }

        auto *node = reinterpret_cast<Node *>(raw);
        Node *head = head_.load(std::memory_order_relaxed);
        do {
            node->next = head;
        } while (!head_.compare_exchange_weak(head, node,
                                              std::memory_order_release,
                                              std::memory_order_relaxed));
        free_count_.fetch_add(1u, std::memory_order_relaxed);
    }

    void note_taken() noexcept {
        const std::size_t left = free_count_.fetch_sub(1u, std::memory_order_relaxed) - 1u;
        /* Водяний знак опускаємо циклом порівняння-обміну: простий if затер
           би нижчий мінімум, записаний іншим потоком між читанням і записом. */
        std::size_t seen = min_free_count_.load(std::memory_order_relaxed);
        while (left < seen &&
               !min_free_count_.compare_exchange_weak(seen, left,
                                                      std::memory_order_relaxed,
                                                      std::memory_order_relaxed)) {
        }
    }
};

/*
 * Про ABA. Поки ми тримаємо прочитану голову, переривання встигає зняти два
 * блоки й повернути перший: голова знову та сама, а next уже інший. На
 * Cortex-M цього не буває — вхід у виняток і повернення з нього скидають
 * монітор ексклюзивності, тож наш STREX гарантовано дасть збій і коло
 * повториться. На багатоядерній машині зі справжнім CAS такої гарантії
 * немає: там до вказівника чіпляють лічильник поколінь.
 */

}  // namespace nofree
