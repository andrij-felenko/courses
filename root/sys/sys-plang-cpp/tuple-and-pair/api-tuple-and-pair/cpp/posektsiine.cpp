#include <utility>
#include <tuple>
#include <string>
#include <vector>

// Передавання аргументів у конструктори складних типів усередині пари
std::pair<std::string, std::vector<int>> p(
    std::piecewise_construct,
    std::forward_as_tuple(5, 'a'),       // Конструює string("aaaaa")
    std::forward_as_tuple(10, 42)        // Конструює vector з 10 елементами 42
);
