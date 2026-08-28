// C++: Двопрохідне сортування таблиці через std::stable_sort
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <iomanip>

struct CityRecord {
    std::string country;
    std::string city;
    int population;
};

void print_table(std::string_view title, const std::vector<CityRecord>& records) {
    std::cout << "--- " << title << " ---\n";
    for (const auto& r : records) {
        std::cout << "  " << std::left << std::setw(12) << r.country
                  << " | " << std::setw(12) << r.city
                  << " | Населення: " << r.population << "\n";
    }
    std::cout << "\n";
}

int main() {
    std::vector<CityRecord> data = {
        {"Україна", "Львів",  720000},
        {"Польща",  "Краків", 780000},
        {"Україна", "Київ",   2950000},
        {"Польща",  "Варшава",1790000},
        {"Україна", "Одеса",  1010000}
    };

    print_table("Вхідна таблиця", data);

    // Крок 1: Сортуємо за другорядною колонкою (Місто)
    std::stable_sort(data.begin(), data.end(), [](const CityRecord& a, const CityRecord& b) {
        return a.city < b.city;
    });
    print_table("Крок 1: Після std::stable_sort за Містом", data);

    // Крок 2: Сортуємо за головною колонкою (Країна)
    std::stable_sort(data.begin(), data.end(), [](const CityRecord& a, const CityRecord& b) {
        return a.country < b.country;
    });
    print_table("Крок 2: Після std::stable_sort за Країною (Міста впорядковані!)", data);

    return 0;
}
