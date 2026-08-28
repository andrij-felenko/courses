#include <string>
#include <string_view>

// Функція повертає посилання на один із двох переданих аргументів
template <typename T>
const T& custom_min(const T& a [[clang::lifetimebound]], 
                    const T& b [[clang::lifetimebound]]) {
    return (b < a) ? b : a;
}

// Конструктор в'ювера, що запозичує буфер у контейнера
template <typename T>
class MySpan {
    const T* data_;
    size_t size_;
public:
    template <typename Container>
    MySpan(const Container& c [[clang::lifetimebound]])
        : data_(c.data()), size_(c.size()) {}
};
