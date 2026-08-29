#pragma once
/*
 * memory_arena.hpp — двостороння лінійна арена на C++20.
 *
 * Нижній курсор росте вгору (дані кадру), верхній — вниз (чернетки).
 * Індивідуального звільнення немає; замість нього RAII-мітка Scope, яка
 * відкочує курсор на виході з області за будь-якого шляху виходу.
 */
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <new>
#include <optional>
#include <span>
#include <type_traits>
#include <utility>

namespace nofree {

template <std::size_t Capacity>
class MemoryArena {
    static_assert(Capacity > 0u, "Арена нульової місткості безглузда");

public:
    MemoryArena() noexcept = default;

    MemoryArena(const MemoryArena &)            = delete;
    MemoryArena &operator=(const MemoryArena &) = delete;

    /* Мітка нижнього курсора. Деструктор відкочує арену навіть тоді, коли
       функція вийшла з середини десятка гілок обробки помилок. */
    class Scope {
    public:
        explicit Scope(MemoryArena &arena) noexcept : arena_{arena}, saved_{arena.lower_} {}
        ~Scope() noexcept { arena_.lower_ = saved_; }

        Scope(const Scope &)            = delete;
        Scope &operator=(const Scope &) = delete;

    private:
        MemoryArena &arena_;
        std::size_t  saved_;
    };

    /* Те саме для верхнього курсора: чернетки живуть лише всередині області. */
    class ScratchScope {
    public:
        explicit ScratchScope(MemoryArena &arena) noexcept : arena_{arena}, saved_{arena.upper_} {}
        ~ScratchScope() noexcept { arena_.upper_ = saved_; }

        ScratchScope(const ScratchScope &)            = delete;
        ScratchScope &operator=(const ScratchScope &) = delete;

    private:
        MemoryArena &arena_;
        std::size_t  saved_;
    };

    [[nodiscard]] Scope        scope() noexcept         { return Scope{*this}; }
    [[nodiscard]] ScratchScope scratch_scope() noexcept { return ScratchScope{*this}; }

    /* Арена скидається одним записом і деструкторів не кличе — отже, у ній
       живуть лише тривіально руйновні типи. Це не обмеження реалізації, а
       чесно виражений контракт: інакше пропуск деструктора був би витоком
       ресурсу, якого пам'ять не бачить. */
    template <typename T, typename... Args>
        requires std::is_trivially_destructible_v<T> &&
                 std::is_nothrow_constructible_v<T, Args...>
    [[nodiscard]] T *create(Args &&...args) noexcept {
        void *raw = allocate_low(sizeof(T), alignof(T));
        if (raw == nullptr) {
            return nullptr;
        }
        return ::new (raw) T(std::forward<Args>(args)...);
    }

    /* Порожній span неможливо відрізнити від запиту на нуль елементів, тому
       відмова повертається окремим станом, а не «порожнім результатом». */
    template <typename T>
        requires std::is_trivially_destructible_v<T> &&
                 std::is_nothrow_default_constructible_v<T>
    [[nodiscard]] std::optional<std::span<T>> create_span(std::size_t count) noexcept {
        return make_span<T>(count, /*scratch=*/false);
    }

    template <typename T>
        requires std::is_trivially_destructible_v<T> &&
                 std::is_nothrow_default_constructible_v<T>
    [[nodiscard]] std::optional<std::span<T>> scratch_span(std::size_t count) noexcept {
        return make_span<T>(count, /*scratch=*/true);
    }

    void reset() noexcept {
        lower_ = 0u;
        upper_ = Capacity;
        /* peak_ лишаємо: це підсумок за весь час, він іде у звіт бюджету. */
    }

    [[nodiscard]] std::size_t used_bytes() const noexcept {
        return lower_ + (Capacity - upper_);
    }
    [[nodiscard]] std::size_t remaining_bytes() const noexcept { return upper_ - lower_; }
    [[nodiscard]] std::size_t peak_bytes() const noexcept      { return peak_; }
    [[nodiscard]] static constexpr std::size_t capacity_bytes() noexcept { return Capacity; }

private:
    alignas(std::max_align_t) std::byte buffer_[Capacity]{};
    std::size_t lower_{0u};
    std::size_t upper_{Capacity};
    std::size_t peak_{0u};

    void note_peak() noexcept { peak_ = std::max(peak_, used_bytes()); }

    template <typename T>
    [[nodiscard]] std::optional<std::span<T>> make_span(std::size_t count, bool scratch) noexcept {
        if (count == 0u || count > (Capacity / sizeof(T))) {
            return std::nullopt;         /* заразом ловимо переповнення множення */
        }
        void *raw = scratch ? allocate_high(sizeof(T) * count, alignof(T))
                            : allocate_low(sizeof(T) * count, alignof(T));
        if (raw == nullptr) {
            return std::nullopt;
        }
        T *array = static_cast<T *>(raw);
        for (std::size_t i = 0u; i < count; ++i) {
            ::new (static_cast<void *>(&array[i])) T();
        }
        return std::span<T>{array, count};
    }

    [[nodiscard]] void *allocate_low(std::size_t size, std::size_t alignment) noexcept {
        const auto base    = reinterpret_cast<std::uintptr_t>(buffer_);
        const auto cursor  = base + lower_;
        const auto aligned = (cursor + (alignment - 1u)) & ~static_cast<std::uintptr_t>(alignment - 1u);
        const auto limit   = base + upper_;   /* межа — верхній курсор, не кінець буфера */

        if (aligned < cursor || aligned > limit || size > static_cast<std::size_t>(limit - aligned)) {
            return nullptr;
        }
        lower_ = static_cast<std::size_t>(aligned - base) + size;
        note_peak();
        return reinterpret_cast<void *>(aligned);
    }

    [[nodiscard]] void *allocate_high(std::size_t size, std::size_t alignment) noexcept {
        if (size > upper_) {
            return nullptr;
        }
        const auto base = reinterpret_cast<std::uintptr_t>(buffer_);
        const auto top  = base + upper_;
        /* Верхній курсор іде вниз, тож адресу вирівнюємо ВНИЗ. */
        const auto cand = (top - size) & ~static_cast<std::uintptr_t>(alignment - 1u);

        if (cand < base + lower_) {
            return nullptr;               /* курсори зустрілися */
        }
        upper_ = static_cast<std::size_t>(cand - base);
        note_peak();
        return reinterpret_cast<void *>(cand);
    }
};

}  // namespace nofree
