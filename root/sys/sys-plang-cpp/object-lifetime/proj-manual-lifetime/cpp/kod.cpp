#include <cstddef>      // std::byte, std::size_t
#include <memory>       // std::destroy_at
#include <new>          // розміщувальний new, std::launder
#include <stdexcept>
#include <utility>

template <class T, std::size_t N>
class StaticVector {
public:
    StaticVector() noexcept = default;
    ~StaticVector() { clear(); }

    StaticVector(const StaticVector&)            = delete;   // чому — нижче
    StaticVector& operator=(const StaticVector&) = delete;

    std::size_t size() const noexcept { return size_; }
    static constexpr std::size_t capacity() noexcept { return N; }

    template <class... Args>
    T& emplace_back(Args&&... args) {
        if (size_ == N)
            throw std::length_error("StaticVector: місткість вичерпано");

        T* p = ::new (raw(size_)) T(std::forward<Args>(args)...);  // 1. час життя почався
        ++size_;                                                   // 2. і лише тепер він наш
        return *p;
    }

    void pop_back() noexcept {
        --size_;                       // спершу знімаємо з обліку
        std::destroy_at(at(size_));    // потім закінчуємо час життя; байти лишаються
    }

    void clear() noexcept {
        while (size_ != 0) pop_back();  // зворотний порядок — як у блоці
    }

    template <class It>
    void append(It first, It last);

    T&       operator[](std::size_t i)       noexcept { return *at(i); }
    const T& operator[](std::size_t i) const noexcept { return *at(i); }

private:
    void* raw(std::size_t i) noexcept { return buf_ + i * sizeof(T); }

    T* at(std::size_t i) noexcept {
        return std::launder(reinterpret_cast<T*>(buf_ + i * sizeof(T)));
    }
    const T* at(std::size_t i) const noexcept {
        return std::launder(reinterpret_cast<const T*>(buf_ + i * sizeof(T)));
    }

    alignas(T) std::byte buf_[N * sizeof(T)];
    std::size_t size_ = 0;
};
