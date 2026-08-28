#include <iostream>

void dispatch(int value) {
    std::cout << "Виклик цілочисельної функції: " << value << "\n";
}

void dispatch(double* ptr) {
    std::cout << "Виклик функції для покажчика\n";
}

int main() {
    // dispatch(NULL); // ПОМИЛКА: неоднозначність! NULL у старих стандартах розгортався в 0
    dispatch(nullptr); // ПРАВИЛЬНО: nullptr має власний тип std::nullptr_t
    return 0;
}
