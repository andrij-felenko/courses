template<typename Container>
void clear_resource(Container& c) {
    if constexpr (requires { c.clear(); }) {
        c.clear(); // Інстанціюється лише якщо метод дійсно існує
    } else if constexpr (requires { c.reset(); }) {
        c.reset(); // Інстанціюється лише для типів з методом reset()
    } else {
        c = Container{}; // Резервний шлях для простих структур
    }
}
