#include <cinttypes>

int main() {
    InvalidationEngine engine;

    // Реєструємо кешовані сторінки
    engine.set("/product/42", "MacBook Pro M3", std::chrono::seconds(300),
               {"item:42", "brand:apple", "cat:laptops"});
    engine.set("/product/99", "iPhone 15", std::chrono::seconds(300),
               {"item:99", "brand:apple", "cat:phones"});
    engine.set("/catalog/laptops", "List of 20 Laptops", std::chrono::seconds(300),
               {"cat:laptops", "page:1"});

    std::cout << "1. Інвалідація товару #42 за тегом 'item:42'...\n";
    size_t purged = engine.purge_tag("item:42");
    std::cout << "   Очищено ключів: " << purged << " (очікується 1: /product/42)\n";

    std::cout << "2. Інвалідація бренду 'brand:apple'...\n";
    purged = engine.purge_tag("brand:apple");
    std::cout << "   Очищено ключів: " << purged << " (очікується 1: /product/99)\n";

    std::cout << "3. Тестування Generation Bumping...\n";
    std::string k1 = engine.make_versioned_key("tenant_10", "settings");
    std::cout << "   Ключ до скидання: " << k1 << "\n";
    engine.bump_generation("tenant_10");
    std::string k2 = engine.make_versioned_key("tenant_10", "settings");
    std::cout << "   Ключ після O(1) скидання: " << k2 << "\n";

    return 0;
}
