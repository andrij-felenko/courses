#include <concepts>

template <typename T>
concept Printable = requires(T a) {
    { std::cout << a } -> std::same_as<std::ostream&>;
};

// Функція інстанціюється лише для типів, що задовольняють концепт
void print_element(Printable auto const& item) {
    std::cout << item << '\n';
}
