# Практична реалізація: симуляція відносності моделей

Щоб краще відчути парадокс Сколема на практиці, ми можемо написати невеликий симулятор на мові C++17. Наша мета — показати, як зовнішній код може маніпулювати моделлю, яка «не бачить» певної бієкції, незважаючи на те, що обидві множини (область визначення і значень) належать цій моделі. 

Ми створимо об'єктну структуру, що моделює крихітний фрагмент всесвіту множин. У нашій симуляції 5 базових компонентів:
1. `Set` — базовий інтерфейс для множин.
2. `Model` — контейнер, що містить доступні об'єкти (наш зліченний всесвіт M).
3. `N_Set` — множина уявних «натуральних чисел».
4. `P_Set` — множина уявних «підмножин» (яка вважається незліченною всередині моделі).
5. `Function` — об'єкт бієкції, який ми можемо додавати або вилучати з моделі.

## Код симулятора

```cpp
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
```

## Як це працює

У нашому коді `Model M` символізує ту саму зліченну модель з парадоксу Сколема. Вона містить множини N та P(N), але ми спеціально не поклали в неї об'єкт `Function` (бієкцію). Тому, коли `M` аналізує саму себе через метод `evaluate_cardinality()`, вона приходить до висновку, що між N та P(N) неможливо встановити відповідність. Для `M` множина P(N) виглядає абсолютно незліченною.

Натомість мета-модель `V` символізує зовнішнього математика. Вона містить ті ж самі множини N та P(N), але має і об'єкт `bijection`. Мета-модель «бачить», що множину P(N) насправді можна перерахувати, тому для неї P(N) є зліченною. 

Цей простий код на C++17 ідеально ілюструє суть відносності Сколема. Незліченність — це не внутрішня, жорстко зафіксована властивість об'єкта `P_Set`. Це просто констатація факту *відсутності* певного об'єкта (бієкції) у конкретному списку (векторі `universe` конкретної моделі). Додайте цей об'єкт у масив — і «незліченна» множина миттєво стане «зліченною».
