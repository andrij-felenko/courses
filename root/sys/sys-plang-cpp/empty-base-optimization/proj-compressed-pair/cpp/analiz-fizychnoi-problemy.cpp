#include <iostream>
#include <memory>
#include <cstddef>

template <typename T, typename Deleter = std::default_delete<T>>
class naive_unique_ptr {
    T* ptr_{nullptr};
    Deleter deleter_{};

public:
    explicit naive_unique_ptr(T* p = nullptr, Deleter d = Deleter{})
        : ptr_{p}, deleter_{d} {}

    ~naive_unique_ptr() {
        if (ptr_) {
            deleter_(ptr_);
        }
    }

    T* get() const noexcept { return ptr_; }
};
