#pragma once

#include <concepts>
#include <cstddef>
#include <new>
#include <type_traits>
#include <utility>

namespace at {

/* Колбек із замиканням, але без купи.

   std::function тут неприйнятний: він має право виділити пам'ять, а рушій
   живе в мікроконтролері, де фрагментація за роки безперервної роботи —
   гарантована відмова. Тому замикання лежить у власному масиві байтів, а
   що не влізло — не збереться (static_assert у конструкторі).

   Тип рухомий, але не копійовний — як std::move_only_function. */
template <typename Signature, std::size_t Capacity>
class InplaceFunction;

template <typename R, typename... Args, std::size_t Capacity>
class InplaceFunction<R(Args...), Capacity> {
public:
    InplaceFunction() noexcept = default;

    template <typename F>
        requires(!std::same_as<std::decay_t<F>, InplaceFunction>) &&
                std::invocable<std::decay_t<F>&, Args...>
    InplaceFunction(F&& callable) noexcept
    {
        using Decayed = std::decay_t<F>;
        static_assert(sizeof(Decayed) <= Capacity,
                      "замикання не влазить: зменште захоплення або підніміть Capacity");
        static_assert(alignof(Decayed) <= alignof(std::max_align_t));
        static_assert(std::is_nothrow_move_constructible_v<Decayed>);

        ::new (static_cast<void*>(storage_)) Decayed(std::forward<F>(callable));
        vtable_ = &kVTable<Decayed>;
    }

    InplaceFunction(const InplaceFunction&) = delete;
    InplaceFunction& operator=(const InplaceFunction&) = delete;

    InplaceFunction(InplaceFunction&& other) noexcept
    {
        if (other.vtable_ != nullptr) {
            other.vtable_->move(storage_, other.storage_);
            vtable_ = std::exchange(other.vtable_, nullptr);
        }
    }

    InplaceFunction& operator=(InplaceFunction&& other) noexcept
    {
        if (this != &other) {
            reset();
            if (other.vtable_ != nullptr) {
                other.vtable_->move(storage_, other.storage_);
                vtable_ = std::exchange(other.vtable_, nullptr);
            }
        }
        return *this;
    }

    ~InplaceFunction() { reset(); }

    void reset() noexcept
    {
        if (vtable_ != nullptr) {
            vtable_->destroy(storage_);
            vtable_ = nullptr;
        }
    }

    [[nodiscard]] explicit operator bool() const noexcept { return vtable_ != nullptr; }

    R operator()(Args... args)
    {
        return vtable_->invoke(storage_, std::forward<Args>(args)...);
    }

private:
    struct VTable {
        R (*invoke)(void*, Args&&...);
        void (*move)(void* dst, void* src);
        void (*destroy)(void*);
    };

    template <typename Decayed>
    static constexpr VTable kVTable{
        [](void* self, Args&&... args) -> R {
            return (*static_cast<Decayed*>(self))(std::forward<Args>(args)...);
        },
        [](void* dst, void* src) {
            ::new (dst) Decayed(std::move(*static_cast<Decayed*>(src)));
            static_cast<Decayed*>(src)->~Decayed();
        },
        [](void* self) { static_cast<Decayed*>(self)->~Decayed(); },
    };

    alignas(std::max_align_t) std::byte storage_[Capacity]{};
    const VTable* vtable_{nullptr};
};

}  // namespace at
