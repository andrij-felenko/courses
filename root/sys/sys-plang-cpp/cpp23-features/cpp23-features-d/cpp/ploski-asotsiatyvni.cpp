#include <flat_map>
#include <print>

void benchmark_map() {
    std::flat_map<int, std::string> accounts;

    accounts.insert({1024, "Адміністратор"});
    accounts.insert({2048, "Оператор"});
    accounts.insert({512, "Гість"});

    // Пошук за O(log N) через двійковий пошук у кеш-локальному векторі
    if (auto it = accounts.find(1024); it != accounts.end()) {
        std::println("Знайдено: {}", it->second);
    }
}
