// Сучасний підхід C++20 (Concepts)
template<typename T>
requires std::integral<T> && (!std::same_as<T, bool>)
T square(T val) {
    return val * val;
}

// Або скорочений синтаксис (Terse Syntax):
auto square(std::integral auto val) {
    return val * val;
}
