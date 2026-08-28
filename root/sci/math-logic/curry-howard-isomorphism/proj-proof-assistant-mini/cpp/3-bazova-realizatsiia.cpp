#include <iostream>
#include <string>
#include <variant>
#include <memory>
#include <map>
#include <stdexcept>

// Оголошення структур для AST Типів
struct BaseType;
struct ArrowType;

using Type = std::variant<BaseType, std::shared_ptr<ArrowType>>;

struct BaseType {
    std::string name;
};

struct ArrowType {
    Type from;
    Type to;
};

// Допоміжна функція для друку типів
void printType(const Type& t) {
    if (auto* b = std::get_if<BaseType>(&t)) {
        std::cout << b->name;
    } else if (auto* a = std::get_if<std::shared_ptr<ArrowType>>(&t)) {
        std::cout << "(";
        printType((*a)->from);
        std::cout << " -> ";
        printType((*a)->to);
        std::cout << ")";
    }
}
