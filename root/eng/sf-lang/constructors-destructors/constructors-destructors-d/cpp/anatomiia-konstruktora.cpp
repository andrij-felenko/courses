#include <string>
#include <vector>

class BadBuffer {
    std::string name_;
    std::vector<int> data_;
public:
    // Помилковий підхід: подвійна робота
    BadBuffer(const std::string& name, const std::vector<int>& data) {
        name_ = name;  // 1. Спочатку name_ ініціалізовано конструктором за замовчуванням
                       // 2. Потім викликано оператор operator=(const std::string&)
        data_ = data;  // 1. Спочатку data_ виділив порожній вектор
                       // 2. Потім викликано operator=(const std::vector<int>&)
    }
};

class GoodBuffer {
    std::string name_;
    std::vector<int> data_;
public:
    // Правильний підхід: пряма ініціалізація в списку ініціалізації
    GoodBuffer(std::string name, std::vector<int> data)
        : name_(std::move(name)), data_(std::move(data)) {
        // Поля створюються одразу з потрібними даними через конструктори переміщення.
        // Тіло конструктора порожнє, жодних зайвих алокацій чи очищень.
    }
};
