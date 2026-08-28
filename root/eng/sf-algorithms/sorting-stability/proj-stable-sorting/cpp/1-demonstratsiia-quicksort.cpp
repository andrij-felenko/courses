// C++: Ідіоматична порівняльна демонстрація std::sort vs std::stable_sort
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <iomanip>

struct Student {
    int grade;
    std::string name;
    int original_index;
};

void print_students(std::string_view label, const std::vector<Student>& students) {
    std::cout << "=== " << label << " ===\n";
    for (size_t i = 0; i < students.size(); ++i) {
        std::cout << "  [" << i << "] Оцінка: " << students[i].grade
                  << " | Ім'я: " << std::left << std::setw(12) << students[i].name
                  << " (orig_idx: " << students[i].original_index << ")\n";
    }
    std::cout << "\n";
}

int main() {
    const std::vector<Student> original = {
        {5, "Авраменко", 0},
        {4, "Бондаренко", 1},
        {5, "Василенко", 2},
        {4, "Грищенко", 3},
        {5, "Дмитренко", 4}
    };

    print_students("Вихідний масив (відсортований за прізвищем)", original);

    // 1. Нестійке сортування std::sort (Introsort)
    auto std_sorted = original;
    std::sort(std_sorted.begin(), std_sorted.end(), [](const Student& a, const Student& b) {
        return a.grade > b.grade; // За спаданням оцінки
    });
    print_students("Після std::sort (Нестійке)", std_sorted);

    // 2. Стійке сортування std::stable_sort (Adaptive Merge Sort)
    auto stable_sorted = original;
    std::stable_sort(stable_sorted.begin(), stable_sorted.end(), [](const Student& a, const Student& b) {
        return a.grade > b.grade; // За спаданням оцінки
    });
    print_students("Після std::stable_sort (Стійке)", stable_sorted);

    return 0;
}
