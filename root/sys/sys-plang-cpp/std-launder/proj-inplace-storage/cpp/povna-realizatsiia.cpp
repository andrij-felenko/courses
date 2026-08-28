#include <new>
#include <utility>
#include <type_traits>
#include <stdexcept>
#include <iostream>

template <typename T>
class InPlaceOptional {
    // Гарантуємо правильний розмір і вирівнювання сховища
    alignas(T) std::byte storage_[sizeof(T)];
    bool engaged_ = false;

    // Внутрішній допоміжний метод для отримання вказівника
    T* as_ptr() noexcept {
        return std::launder(reinterpret_cast<T*>(storage_));
    }

    const T* as_ptr() const noexcept {
        return std::launder(reinterpret_cast<const T*>(storage_));
    }

    void destroy_internal() noexcept {
        if (engaged_) {
            as_ptr()->~T();
            engaged_ = false;
        }
    }

public:
    // 1. Конструктор за замовчуванням: порожнє сховище
    constexpr InPlaceOptional() noexcept = default;

    // 2. Конструювання зі значенням
    template <typename... Args>
    explicit InPlaceOptional(std::in_place_t, Args&&... args) {
        ::new (static_cast<void*>(storage_)) T(std::forward<Args>(args)...);
        engaged_ = true;
    }

    // 3. Деструктор
    ~InPlaceOptional() {
        destroy_internal();
    }

    // 4. Заборона або реалізація копіювання/переміщення
    InPlaceOptional(const InPlaceOptional& other) {
        if (other.engaged_) {
            ::new (static_cast<void*>(storage_)) T(*other.as_ptr());
            engaged_ = true;
        }
    }

    InPlaceOptional(InPlaceOptional&& other) noexcept(std::is_nothrow_move_constructible_v<T>) {
        if (other.engaged_) {
            ::new (static_cast<void*>(storage_)) T(std::move(*other.as_ptr()));
            engaged_ = true;
        }
    }

    // 5. Метод emplace для створення/перестворення значення
    template <typename... Args>
    T& emplace(Args&&... args) {
        // Якщо значення вже було, спочатку знищуємо старе
        destroy_internal();

        // Створюємо новий об'єкт
        T* created_ptr = ::new (static_cast<void*>(storage_)) T(std::forward<Args>(args)...);
        engaged_ = true;
        
        // Повертаємо посилання на новостворений об'єкт
        return *created_ptr;
    }

    // 6. Очищення сховища
    void reset() noexcept {
        destroy_internal();
    }

    // 7. Перевірка наявності значення
    [[nodiscard]] constexpr bool has_value() const noexcept {
        return engaged_;
    }

    [[nodiscard]] explicit constexpr operator bool() const noexcept {
        return engaged_;
    }

    // 8. Доступ до значення
    [[nodiscard]] T& value() & {
        if (!engaged_) {
            throw std::runtime_error("InPlaceOptional::value(): bad access");
        }
        return *as_ptr();
    }

    [[nodiscard]] const T& value() const& {
        if (!engaged_) {
            throw std::runtime_error("InPlaceOptional::value(): bad access");
        }
        return *as_ptr();
    }

    [[nodiscard]] T& operator*() & noexcept {
        return *as_ptr();
    }

    [[nodiscard]] const T& operator*() const& noexcept {
        return *as_ptr();
    }

    [[nodiscard]] T* operator->() noexcept {
        return as_ptr();
    }

    [[nodiscard]] const T* operator->() const noexcept {
        return as_ptr();
    }
};
