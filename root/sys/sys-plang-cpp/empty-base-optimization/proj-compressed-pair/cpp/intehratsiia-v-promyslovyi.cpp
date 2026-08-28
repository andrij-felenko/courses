template <typename T, typename Deleter = std::default_delete<T>>
class optimal_unique_ptr {
    modern::compressed_pair<T*, Deleter> storage_;

public:
    constexpr optimal_unique_ptr() noexcept
        : storage_(nullptr, Deleter{}) {}

    constexpr explicit optimal_unique_ptr(T* ptr) noexcept
        : storage_(ptr, Deleter{}) {}

    constexpr optimal_unique_ptr(T* ptr, Deleter d) noexcept
        : storage_(ptr, std::move(d)) {}

    ~optimal_unique_ptr() {
        if (get()) {
            get_deleter()(get());
        }
    }

    // Заборона операцій копіювання для гарантії виключного володіння
    optimal_unique_ptr(const optimal_unique_ptr&) = delete;
    optimal_unique_ptr& operator=(const optimal_unique_ptr&) = delete;

    // Переміщувальний конструктор
    constexpr optimal_unique_ptr(optimal_unique_ptr&& other) noexcept
        : storage_(other.release(), std::move(other.get_deleter())) {}

    // Переміщувальний оператор присвоєння
    constexpr optimal_unique_ptr& operator=(optimal_unique_ptr&& other) noexcept {
        if (this != &other) {
            reset(other.release());
            get_deleter() = std::move(other.get_deleter());
        }
        return *this;
    }

    [[nodiscard]] constexpr T* get() const noexcept {
        return storage_.first();
    }

    [[nodiscard]] constexpr Deleter& get_deleter() noexcept {
        return storage_.second();
    }

    [[nodiscard]] constexpr const Deleter& get_deleter() const noexcept {
        return storage_.second();
    }

    constexpr T* release() noexcept {
        T* old_ptr = storage_.first();
        storage_.first() = nullptr;
        return old_ptr;
    }

    constexpr void reset(T* new_ptr = nullptr) noexcept {
        T* old_ptr = storage_.first();
        storage_.first() = new_ptr;
        if (old_ptr) {
            get_deleter()(old_ptr);
        }
    }

    [[nodiscard]] constexpr T& operator*() const noexcept {
        return *get();
    }

    [[nodiscard]] constexpr T* operator->() const noexcept {
        return get();
    }

    [[nodiscard]] constexpr explicit operator bool() const noexcept {
        return get() != nullptr;
    }
};
