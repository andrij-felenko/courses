#include <iostream>

class DynamicArray {
    int capacity_;
public:
    // Без explicit: компілятор дозволяє неявне перетворення int -> DynamicArray
    // explicit DynamicArray(int capacity) : capacity_(capacity) {}
    DynamicArray(int capacity) : capacity_(capacity) {}

    int capacity() const { return capacity_; }
};

void print_array(const DynamicArray& arr) {
    std::cout << "Array capacity: " << arr.capacity() << "\n";
}

int main() {
    // Несподівана поведінка: випадкова передача числа неявно конструює масив на 100 елементів!
    print_array(100); // Скомпілюється і створить тимчасовий об'єкт DynamicArray(100)
    return 0;
}
