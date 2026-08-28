#include <iostream>
#include <vector>
#include <algorithm>
#include <iterator>

int main() {
    // Зчитування масиву цілих чисел прямо з консольного вводу до кінця файлу (EOF)
    std::cout << "Введіть числа (Ctrl+D / Ctrl+Z для завершення): ";
    std::istream_iterator<int> cin_it(std::cin);
    std::istream_iterator<int> eos; // Конструктор за замовчуванням створює вартовий кінця потоку

    std::vector<int> numbers(cin_it, eos); // Заповнення вектора з потоку!

    // Друк елементів через ostream_iterator з розділювачем пробілом
    std::cout << "Прочитані числа: ";
    std::copy(numbers.begin(), numbers.end(), std::ostream_iterator<int>(std::cout, " "));
    std::cout << "\n";
}
