#include <functional>
#include <iostream>
#include <cassert>

int multiply(int a, int b) { return a * b; }

int main() {
    std::function<int(int, int)> fn = multiply;

    // Перевірка типу через target_type()
    if (fn.target_type() == typeid(int(*)(int, int))) {
        std::cout << "Target is a raw function pointer!\n";
    }

    // Отримання сирого покажчика через target<T>()
    using RawFnPtr = int(*)(int, int);
    RawFnPtr* raw_ptr = fn.target<RawFnPtr>();
    assert(raw_ptr != nullptr && *raw_ptr == multiply);
}
