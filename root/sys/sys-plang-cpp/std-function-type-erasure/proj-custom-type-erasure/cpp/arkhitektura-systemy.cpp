#include <iostream>
#include <utility>
#include <new>
#include <type_traits>
#include <cstddef>
#include <cassert>
#include <string>

template <typename Signature>
class custom_function;

template <typename R, typename... Args>
class custom_function<R(Args...)> {
private:
    static constexpr std::size_t SBO_SIZE = 24;

    // Внутрішній розрівняний буфер для збереження малогабаритних функторів
    alignas(std::max_align_t) mutable char storage_[SBO_SIZE];

    // Вказівники на функції диспатчеризації (Ручний Vtable)
    using invoker_t   = R (*)(const void* storage, Args&&... args);
    using destroyer_t = void (*)(void* storage);
    using relocator_t = void (*)(void* dst_storage, void* src_storage);

    invoker_t   invoker_{nullptr};
    destroyer_t destroyer_{nullptr};
    relocator_t relocator_{nullptr};

    // Перевірка: чи вміщується тип F у буфер SBO?
    template <typename F>
    static constexpr bool fits_in_sbo = (sizeof(F) <= SBO_SIZE) && 
                                        (alignof(F) <= alignof(std::max_align_t)) &&
                                        std::is_nothrow_move_constructible_v<F>;

public:
    // 1. Порожній конструктор
    custom_function() noexcept = default;
    custom_function(std::nullptr_t) noexcept {}

    // 2. Шаблонний конструктор для довільного Callable F
    template <typename F, 
              typename = std::enable_if_t<!std::is_same_v<std::decay_t<F>, custom_function>>>
    custom_function(F&& f) {
        using DecayedF = std::decay_t<F>;

        if constexpr (fits_in_sbo<DecayedF>) {
            // Розміщення всередині SBO-буфера через placement new
            new (storage_) DecayedF(std::forward<F>(f));

            invoker_ = [](const void* storage, Args&&... args) -> R {
                auto* fn = reinterpret_cast<const DecayedF*>(storage);
                return (*fn)(std::forward<Args>(args)...);
            };

            destroyer_ = [](void* storage) {
                auto* fn = reinterpret_cast<DecayedF*>(storage);
                fn->~DecayedF();
            };

            relocator_ = [](void* dst, void* src) {
                auto* src_fn = reinterpret_cast<DecayedF*>(src);
                new (dst) DecayedF(std::move(*src_fn));
                src_fn->~DecayedF();
            };
        } else {
            // Виділення пам'яті у купі для великого об'єкта
            DecayedF* heap_ptr = new DecayedF(std::forward<F>(f));
            *reinterpret_cast<DecayedF**>(storage_) = heap_ptr;

            invoker_ = [](const void* storage, Args&&... args) -> R {
                auto* heap_ptr = *reinterpret_cast<DecayedF* const*>(storage);
                return (*heap_ptr)(std::forward<Args>(args)...);
            };

            destroyer_ = [](void* storage) {
                auto* heap_ptr = *reinterpret_cast<DecayedF**>(storage);
                delete heap_ptr;
            };

            relocator_ = [](void* dst, void* src) {
                *reinterpret_cast<DecayedF**>(dst) = *reinterpret_cast<DecayedF**>(src);
                *reinterpret_cast<DecayedF**>(src) = nullptr;
            };
        }
    }

    // 3. Деструктор
    ~custom_function() {
        reset();
    }

    // 4. Переміщуючий конструктор
    custom_function(custom_function&& other) noexcept {
        move_from(std::move(other));
    }

    // 5. Переміщуючий оператор присвоєння
    custom_function& operator=(custom_function&& other) noexcept {
        if (this != &other) {
            reset();
            move_from(std::move(other));
        }
        return *this;
    }

    // Заборона копіювання для простоти розбору
    custom_function(const custom_function&) = delete;
    custom_function& operator=(const custom_function&) = delete;

    // 6. Оператор виклику
    R operator()(Args... args) const {
        if (!invoker_) {
            throw std::runtime_error("Bad custom_function call: empty object");
        }
        return invoker_(storage_, std::forward<Args>(args)...);
    }

    // 7. Оператор bool
    explicit operator bool() const noexcept {
        return invoker_ != nullptr;
    }

private:
    void reset() noexcept {
        if (destroyer_) {
            destroyer_(storage_);
            destroyer_ = nullptr;
            invoker_ = nullptr;
            relocator_ = nullptr;
        }
    }

    void move_from(custom_function&& other) noexcept {
        invoker_ = other.invoker_;
        destroyer_ = other.destroyer_;
        relocator_ = other.relocator_;

        if (other.relocator_) {
            other.relocator_(storage_, other.storage_);
            other.invoker_ = nullptr;
            other.destroyer_ = nullptr;
            other.relocator_ = nullptr;
        }
    }
};

// --- Демонстраційне використання custom_function ---

void global_print(int x) {
    std::cout << "[Global Function] Value: " << x << '\n';
}

int main() {
    // 1. Збереження сирої глобальної функції (SBO)
    custom_function<void(int)> fn1 = global_print;
    fn1(42);

    // 2. Збереження малої лямбди (SBO active: sizeof <= 24 bytes)
    int capture_val = 10;
    custom_function<void(int)> fn2 = [capture_val](int x) {
        std::cout << "[Small Lambda SBO] Capture: " << capture_val << ", Arg: " << x << '\n';
    };
    fn2(100);

    // 3. Збереження великої лямбди (Heap active: sizeof > 24 bytes)
    std::string large_str1 = "Extremely Large Header String Data Number 1";
    std::string large_str2 = "Extremely Large Header String Data Number 2";
    std::string large_str3 = "Extremely Large Header String Data Number 3";

    custom_function<void(int)> fn3 = [large_str1, large_str2, large_str3](int x) {
        std::cout << "[Large Lambda Heap] Combined size: " 
                  << (large_str1.size() + large_str2.size() + large_str3.size()) 
                  << ", Arg: " << x << '\n';
    };
    fn3(500);

    // 4. Переміщення об'єкта
    custom_function<void(int)> fn4 = std::move(fn3);
    assert(!fn3); // fn3 тепер порожній
    fn4(999);     // fn4 працює коректно
}
