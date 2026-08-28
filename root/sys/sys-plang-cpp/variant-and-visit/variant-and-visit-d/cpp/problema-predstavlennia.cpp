// Мова C++: аналог C-структури з тегом, але без автоматичних деструкторів
#include <iostream>
#include <string>

enum class ValueType { Int, Double, String };

struct CppTaggedUnion {
    ValueType type;
    union {
        int i_val;
        double d_val;
        const char* s_val;
    } data;
};

void print_cpp_value(const CppTaggedUnion& val) {
    if (val.type == ValueType::Int) {
        std::cout << "Int: " << val.data.i_val << "\n";
    } else if (val.type == ValueType::Double) {
        std::cout << "Double: " << val.data.d_val << "\n";
    } else if (val.type == ValueType::String) {
        std::cout << "String: " << val.data.s_val << "\n";
    }
}
