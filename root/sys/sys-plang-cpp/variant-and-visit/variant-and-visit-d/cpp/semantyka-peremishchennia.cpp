#include <variant>
#include <vector>
#include <iostream>

struct FastMove {
    std::vector<int> data;
    FastMove(size_t sz) : data(sz, 42) {}
    
    // Явно вказаний noexcept переміщувальний конструктор
    FastMove(FastMove&&) noexcept = default;
    FastMove& operator=(FastMove&&) noexcept = default;
};

int main() {
    std::variant<int, FastMove> v1 = FastMove(1000000);
    
    // O(1) переміщення: буфер вектора передається за 1 крок без виділення пам'яті
    std::variant<int, FastMove> v2 = std::move(v1);
    
    std::cout << "Переміщення завершено успішно без виділення пам'яті у купі.\n";
}
