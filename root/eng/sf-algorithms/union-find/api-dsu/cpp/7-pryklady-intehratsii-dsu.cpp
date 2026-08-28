#include "disjoint_set_union.hpp"
#include <iostream>
#include <exception>

int main() {
    try {
        algo::DisjointSetUnion dsu(100);

        bool merged = dsu.unite(10, 20);
        std::cout << "Об'єднання 10 та 20: " << (merged ? "успішне" : "вже були в еквівалентному класі") << '\n';

        std::cout << "Зв'язані 10 та 20: " << std::boolalpha << dsu.connected(10, 20) << '\n';
        std::cout << "Розмір класу 10: " << dsu.set_size(10) << '\n';
        std::cout << "Кількість компонент: " << dsu.num_sets() << '\n';

    } catch (const std::out_of_range& e) {
        std::cerr << "Некоректний індекс вузла: " << e.what() << '\n';
        return EXIT_FAILURE;
    } catch (const std::exception& e) {
        std::cerr << "Системна помилка: " << e.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
