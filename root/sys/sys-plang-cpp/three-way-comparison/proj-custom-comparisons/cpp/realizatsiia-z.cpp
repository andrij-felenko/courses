#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <compare>
#include <cstdint>

struct BaseEntity {
    uint64_t entity_id{0};

    // Базовий оператор для ізольованого порівняння ідентифікаторів
    friend constexpr auto operator<=>(const BaseEntity&, const BaseEntity&) = default;
};

class Employee : public BaseEntity {
public:
    // Розташування полів оптимізовано для щільності пакування в пам'яті
    std::string last_name;
    std::string first_name;
    uint32_t    department_id{0};
    uint16_t    seniority_years{0};
    uint8_t     access_level{0};

    Employee(uint64_t id, std::string last, std::string first,
             uint32_t dept, uint16_t seniority, uint8_t access)
        : BaseEntity{id},
          last_name(std::move(last)),
          first_name(std::move(first)),
          department_id(dept),
          seniority_years(seniority),
          access_level(access) {}

    // 1. Оптимізована швидка рівність: унікальний первинний ключ гарантує тотожність
    bool operator==(const Employee& other) const noexcept {
        return entity_id == other.entity_id;
    }

    // 2. Власне тричленне впорядкування за бізнес-пріоритетами
    std::strong_ordering operator<=>(const Employee& other) const noexcept {
        // Крок 1: Групування за відділом (за зростанням номера)
        if (auto cmp = department_id <=> other.department_id; cmp != 0) {
            return cmp;
        }

        // Крок 2: Сортування за стажем (за спаданням: більший стаж іде раніше)
        if (auto cmp = other.seniority_years <=> seniority_years; cmp != 0) {
            return cmp;
        }

        // Крок 3: Алфавітне впорядкування за прізвищем
        if (auto cmp = last_name <=> other.last_name; cmp != 0) {
            return cmp;
        }

        // Крок 4: Алфавітне впорядкування за ім'ям
        if (auto cmp = first_name <=> other.first_name; cmp != 0) {
            return cmp;
        }

        // Крок 5: Остаточний тайбрейкер за унікальним ID
        return entity_id <=> other.entity_id;
    }
};
