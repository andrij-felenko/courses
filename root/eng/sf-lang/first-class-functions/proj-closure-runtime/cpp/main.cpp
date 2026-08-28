#include <iostream>
#include <memory>
#include <utility>
#include <new>

/* =========================================================================
 * Реалізація універсального контейнера замикання (Type Erasure + SBO)
 * Оптимізація малого буфера (SBO): змінні <= 24 байтів не йдуть на купу.
 * ========================================================================= */

template <typename Signature>
class CustomFunction;

template <typename Ret, typename... Args>
class CustomFunction<Ret(Args...)> {
private:
    struct IConcept {
        virtual ~IConcept() = default;
        virtual Ret invoke(Args... args) = 0;
        virtual void move_to(void *dest) noexcept = 0;
    };

    template <typename Callable>
    struct Model final : IConcept {
        Callable callable;

        explicit Model(Callable &&c) : callable(std::forward<Callable>(c)) {}

        Ret invoke(Args... args) override {
            return callable(std::forward<Args>(args)...);
        }

        void move_to(void *dest) noexcept override {
            new (dest) Model(std::move(*this));
        }
    };

    static constexpr size_t SBO_SIZE = 24;
    alignas(max_align_t) char storage_[SBO_SIZE];
    IConcept *concept_ptr_{nullptr};
    bool is_small_{false};

    void clear() noexcept {
        if (concept_ptr_) {
            if (is_small_) {
                concept_ptr_->~IConcept();
            } else {
                delete concept_ptr_;
            }
            concept_ptr_ = nullptr;
        }
    }

public:
    CustomFunction() noexcept = default;

    template <typename F>
    CustomFunction(F &&callable) {
        using ModelType = Model<std::decay_t<F>>;
        if constexpr (sizeof(ModelType) <= SBO_SIZE && alignof(ModelType) <= alignof(max_align_t)) {
            concept_ptr_ = new (storage_) ModelType(std::forward<F>(callable));
            is_small_ = true;
        } else {
            concept_ptr_ = new ModelType(std::forward<F>(callable));
            is_small_ = false;
        }
    }

    ~CustomFunction() noexcept {
        clear();
    }

    CustomFunction(CustomFunction &&other) noexcept {
        if (other.is_small_ && other.concept_ptr_) {
            other.concept_ptr_->move_to(storage_);
            concept_ptr_ = reinterpret_cast<IConcept *>(storage_);
            is_small_ = true;
            other.clear();
        } else {
            concept_ptr_ = other.concept_ptr_;
            is_small_ = other.is_small_;
            other.concept_ptr_ = nullptr;
        }
    }

    CustomFunction &operator=(CustomFunction &&other) noexcept {
        if (this != &other) {
            clear();
            if (other.is_small_ && other.concept_ptr_) {
                other.concept_ptr_->move_to(storage_);
                concept_ptr_ = reinterpret_cast<IConcept *>(storage_);
                is_small_ = true;
                other.clear();
            } else {
                concept_ptr_ = other.concept_ptr_;
                is_small_ = other.is_small_;
                other.concept_ptr_ = nullptr;
            }
        }
        return *this;
    }

    CustomFunction(const CustomFunction &) = delete;
    CustomFunction &operator=(const CustomFunction &) = delete;

    Ret operator()(Args... args) const {
        if (!concept_ptr_) {
            throw std::bad_alloc();
        }
        return concept_ptr_->invoke(std::forward<Args>(args)...);
    }
};

/* =========================================================================
 * Використання: Фабрика та виклики
 * ========================================================================= */

CustomFunction<int(int)> make_accumulator(int initial_val, int multiplier) {
    // Лямбда-вираз автоматично генерує анонімний клас із полями
    return [current_sum = initial_val, multiplier](int val) mutable -> int {
        current_sum += val * multiplier;
        return current_sum;
    };
}

int main() {
    auto acc1 = make_accumulator(10, 1);
    auto acc2 = make_accumulator(0, 10);

    std::cout << "acc1(5)  -> " << acc1(5) << " (очікувано: 15)\n";
    std::cout << "acc1(3)  -> " << acc1(3) << " (очікувано: 18)\n";

    std::cout << "acc2(2)  -> " << acc2(2) << " (очікувано: 20)\n";
    std::cout << "acc2(4)  -> " << acc2(4) << " (очікувано: 60)\n";

    std::cout << "acc1(2)  -> " << acc1(2) << " (очікувано: 20)\n";
    return 0;
}
