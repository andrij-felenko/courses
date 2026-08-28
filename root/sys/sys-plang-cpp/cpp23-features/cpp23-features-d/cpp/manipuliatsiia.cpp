#include <flat_map>
#include <algorithm>

void bulk_update(std::flat_map<int, double>& prices) {
    // Вилучення векторів
    auto [keys, values] = std::move(prices).extract();

    // Масове оновлення всіх значень за один векторний прохід
    for (auto& val : values) {
        val *= 1.20; // Додавання ПДВ
    }

    // Повернення векторів у плоску мапу
    prices.replace(std::move(keys), std::move(values));
}
