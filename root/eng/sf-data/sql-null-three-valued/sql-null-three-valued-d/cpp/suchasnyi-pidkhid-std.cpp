#include <iostream>
#include <optional>
#include <string>

struct EmployeeRecord {
    int id;
    std::string name;
    std::optional<double> salary;     /* Відповідає NULL у колонці salary */
    std::optional<std::string> phone;  /* Відповідає NULL у колонці phone */
};

void print_employee(const EmployeeRecord& emp) {
    std::cout << "Співробітник: " << emp.name;
    if (emp.salary.has_value()) {
        std::cout << ", Зарплата: " << *emp.salary << " грн\n";
    } else {
        std::cout << ", Зарплата: [НЕ ВКАЗАНО]\n";
    }
}
