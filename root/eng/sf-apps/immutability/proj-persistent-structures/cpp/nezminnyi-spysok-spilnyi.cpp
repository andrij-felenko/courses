#include <memory>

// Незмінний вузол списку. Обидва поля const — після народження вузол застиг.
template <typename T>
struct Node {
    const T                     value;
    const std::shared_ptr<Node> next;   // хвіст — спільний, може бути в кількох списках

    Node(T v, std::shared_ptr<Node> n)
        : value(std::move(v)), next(std::move(n)) {}
};

template <typename T>
using List = std::shared_ptr<Node<T>>;   // список — це просто вказівник на голову (або nullptr)

// "Додати в голову": один новий вузол перед спільним хвостом. Стара голова недоторкана.
template <typename T>
List<T> prepend(T v, List<T> tail) {
    return std::make_shared<Node<T>>(std::move(v), std::move(tail));
}
