#include <iostream>
#include <vector>
#include <functional>
#include <string>
#include <algorithm>

// 3. Клас еквівалентності: просто вектор елементів
template<typename T>
using EquivalenceClass = std::vector<T>;

// 4. Фактор-множина: вектор класів еквівалентності
template<typename T>
using QuotientSet = std::vector<EquivalenceClass<T>>;

// 5. Алгоритм розбиття
template<typename T>
QuotientSet<T> build_quotient_set(
    const std::vector<T>& domain, // 1. Базова множина
    const std::function<bool(const T&, const T&)>& is_equivalent // 2. Предикат еквівалентності
) {
    QuotientSet<T> quotient;
    
    for (const auto& element : domain) {
        bool placed = false;
        
        // Шукаємо існуючий клас, до якого належить поточний елемент
        for (auto& eq_class : quotient) {
            // Беремо представника класу (завжди перший елемент)
            if (is_equivalent(eq_class.front(), element)) {
                eq_class.push_back(element);
                placed = true;
                break;
            }
        }
        
        // Якщо елемент не підійшов до жодного класу, створюємо новий
        if (!placed) {
            quotient.push_back({element});
        }
    }
    
    return quotient;
}

// Приклад використання
struct Student {
    std::string name;
    int group_number;
};

int main() {
    // 1. Базова множина
    std::vector<Student> students = {
        {"Олексій", 101}, {"Марія", 102}, {"Іван", 101},
        {"Олена", 103}, {"Дмитро", 102}, {"Анна", 101}
    };
    
    // 2. Предикат еквівалентності: два студенти в одній групі
    auto same_group = [](const Student& a, const Student& b) {
        return a.group_number == b.group_number;
    };
    
    // Побудова фактор-множини
    QuotientSet<Student> q_set = build_quotient_set(students, same_group);
    
    // Вивід результатів
    for (size_t i = 0; i < q_set.size(); ++i) {
        std::cout << "Клас " << i + 1 << " (Група " << q_set[i].front().group_number << "):\n";
        for (const auto& student : q_set[i]) {
            std::cout << "  - " << student.name << "\n";
        }
    }
    
    return 0;
}
