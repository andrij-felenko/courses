// C++: Універсальний шаблонний декорувальник ключа для std::sort
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <concepts>

template <typename T, typename KeyExtractor>
void stable_sort_via_decoration(std::vector<T>& vec, KeyExtractor key_extractor) {
    using KeyType = std::invoke_result_t<KeyExtractor, const T&>;

    struct Decorated {
        T value;
        KeyType key;
        size_t original_index;
    };

    std::vector<Decorated> decorated;
    decorated.reserve(vec.size());

    // 1. Декоруємо елементи індексами
    for (size_t i = 0; i < vec.size(); ++i) {
        decorated.push_back({vec[i], key_extractor(vec[i]), i});
    }

    // 2. Сортуємо нестійким std::sort з двопарамним компаратором
    std::sort(decorated.begin(), decorated.end(), [](const Decorated& a, const Decorated& b) {
        if (a.key != b.key) {
            return a.key < b.key;
        }
        return a.original_index < b.original_index; // Гарантія стійкості!
    });

    // 3. Відновлюємо оригінальний вектор
    for (size_t i = 0; i < vec.size(); ++i) {
        vec[i] = std::move(decorated[i].value);
    }
}

struct Product {
    int category_id;
    std::string name;
    double price;
};

int main() {
    std::vector<Product> products = {
        {1, "Ноутбук", 1200.0},
        {2, "Мишка А", 25.0},
        {1, "Клавіатура", 80.0},
        {2, "Мишка Б", 25.0},
        {1, "Монітор", 300.0}
    };

    std::cout << "=== Вхідні товари ===\n";
    for (const auto& p : products) {
        std::cout << "Категорія: " << p.category_id << " | " << p.name << " ($" << p.price << ")\n";
    }

    // Сортуємо за категорією, зберігаючи вхідний порядок товарів всередині категорії
    stable_sort_via_decoration(products, [](const Product& p) {
        return p.category_id;
    });

    std::cout << "\n=== Після декорованого стійкого сортування за категорією ===\n";
    for (const auto& p : products) {
        std::cout << "Категорія: " << p.category_id << " | " << p.name << " ($" << p.price << ")\n";
    }

    return 0;
}
