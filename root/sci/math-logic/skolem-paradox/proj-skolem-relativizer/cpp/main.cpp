#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <algorithm>

// 1. Базовий клас для всіх об'єктів у нашому "всесвіті"
class Set {
public:
    virtual ~Set() = default;
    virtual std::string name() const = 0;
};

// 3. Множина "натуральних чисел"
class N_Set : public Set {
public:
    std::string name() const override { return "N (натуральні числа)"; }
};

// 4. Множина "підмножин", яка грає роль P(N)
class P_Set : public Set {
public:
    std::string name() const override { return "P(N) (підмножини)"; }
};

// 5. Бієкція між N та P(N)
class Function : public Set {
public:
    std::string name() const override { return "f: N <-> P(N) (бієкція)"; }
};

// 2. Модель M, яка містить певний набір множин
class Model {
private:
    std::string model_name;
    std::vector<std::shared_ptr<Set>> universe;

public:
    Model(std::string name) : model_name(name) {}

    void add_element(std::shared_ptr<Set> element) {
        universe.push_back(element);
    }

    bool contains_bijection() const {
        for (const auto& elem : universe) {
            // Перевіряємо, чи є серед елементів об'єкт класу Function
            if (dynamic_cast<Function*>(elem.get()) != nullptr) {
                return true;
            }
        }
        return false;
    }

    void evaluate_cardinality() const {
        std::cout << "Аналіз всередині моделі [" << model_name << "]:\n";
        if (contains_bijection()) {
            std::cout << "  -> Знайдено бієкцію. P(N) є ЗЛІЧЕННОЮ в цій моделі.\n";
        } else {
            std::cout << "  -> Бієкції не знайдено. P(N) є НЕЗЛІЧЕННОЮ в цій моделі.\n";
        }
    }
};

int main() {
    auto n_set = std::make_shared<N_Set>();
    auto p_set = std::make_shared<P_Set>();
    auto bijection = std::make_shared<Function>();

    // Створюємо "бідну" модель M (як у парадоксі Сколема)
    Model M("Зліченна модель Сколема M");
    M.add_element(n_set);
    M.add_element(p_set);
    // Зверніть увагу: ми НЕ додаємо bijection в M

    // Створюємо "багату" зовнішню мета-модель V
    Model V("Зовнішній всесвіт V");
    V.add_element(n_set);
    V.add_element(p_set);
    V.add_element(bijection); // Додаємо бієкцію!

    std::cout << "--- Симуляція парадоксу Сколема ---\n\n";
    
    M.evaluate_cardinality();
    std::cout << "\n";
    V.evaluate_cardinality();

    return 0;
}
