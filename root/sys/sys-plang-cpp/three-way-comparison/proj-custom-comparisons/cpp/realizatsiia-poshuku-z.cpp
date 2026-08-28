#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <ranges>

struct CompactProduct {
    uint32_t    sku_code{0};
    double      price{0.0};
    std::string title;

    // Стандартне впорядкування за SKU
    auto operator<=>(const CompactProduct& other) const = default;
};

void run_projected_binary_search() {
    std::vector<CompactProduct> catalog = {
        {1010, 19.99, "USB Cable"},
        {1020, 49.50, "Power Adapter"},
        {1030, 99.00, "Wireless Mouse"},
        {1040, 150.0, "Mechanical Keyboard"}
    };

    // 1. Пошук за цілочисельним SKU без створення об'єкта CompactProduct!
    // Покажчик &CompactProduct::sku_code слугує проекцією, а компаратор за замовчуванням
    // використовує тричленне порівняння для uint32_t.
    uint32_t target_sku = 1030;
    auto it = std::ranges::lower_bound(catalog, target_sku, {}, &CompactProduct::sku_code);

    if (it != catalog.end() && it->sku_code == target_sku) {
        std::cout << "Знайдено товар: " << it->title << ", ціна: " << it->price << "\n";
    }

    // 2. Двійковий пошук за діапазоном цін
    double target_price = 49.50;
    bool exists = std::ranges::binary_search(catalog, target_price, {}, &CompactProduct::price);
    std::cout << "Товар із ціною 49.50 існує: " << std::boolalpha << exists << "\n";
}
