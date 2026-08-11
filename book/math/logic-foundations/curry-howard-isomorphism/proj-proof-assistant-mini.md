# Створення мінімального асистента доведень на C++17

### 1. Вступ та цілі

Спираючись на ізоморфізм Каррі — Говарда, ми можемо створити власного мініатюрного асистента доведень (proof assistant). Мета цього проєкту — написати на C++17 програму, яка розпізнає логічні формули (як типи) та перевіряє, чи є наданий лямбда-вираз правильним доведенням (правильною програмою). Ми реалізуємо перевірку типів для просто типізованого лямбда-числення (STLC), що еквівалентно інтуїціоністській пропозиційній логіці.

### 2. Архітектура (AST та Type Checker)

Наш асистент складатиметься з двох основних частин:
1. **Абстрактне синтаксичне дерево (AST):** Структури даних для представлення логічних висловлювань (Типів) та доведень (Термів).
2. **Перевіряльник типів (Type Checker):** Алгоритм, який рекурсивно проходить по AST терма і виводить його тип, звіряючи його з очікуваним типом. 

Для представлення абстрактних структур ми ідеально застосуємо можливості C++17, зокрема `std::variant`, який дозволяє елегантно і безпечно реалізувати алгебраїчні типи даних (суми типів).

### 3. Базова реалізація

Спочатку визначимо типи (логічні формули). Типом може бути або базова змінна (наприклад, "A"), або імплікація двох типів (A → B).

```cpp
#include <iostream>
#include <string>
#include <variant>
#include <memory>
#include <map>
#include <stdexcept>

// Оголошення структур для AST Типів
struct BaseType;
struct ArrowType;

using Type = std::variant<BaseType, std::shared_ptr<ArrowType>>;

struct BaseType {
    std::string name;
};

struct ArrowType {
    Type from;
    Type to;
};

// Допоміжна функція для друку типів
void printType(const Type& t) {
    if (auto* b = std::get_if<BaseType>(&t)) {
        std::cout << b->name;
    } else if (auto* a = std::get_if<std::shared_ptr<ArrowType>>(&t)) {
        std::cout << "(";
        printType((*a)->from);
        std::cout << " -> ";
        printType((*a)->to);
        std::cout << ")";
    }
}
```

Далі визначимо терми (програми/доведення). Це змінні, лямбда-абстракції (введення імплікації) та застосування функцій (Modus Ponens).

```cpp
struct VarTerm;
struct AbsTerm;
struct AppTerm;

using Term = std::variant<VarTerm, std::shared_ptr<AbsTerm>, std::shared_ptr<AppTerm>>;

struct VarTerm {
    std::string name;
};

struct AbsTerm {
    std::string paramName;
    Type paramType;
    Term body;
};

struct AppTerm {
    Term func;
    Term arg;
};
```

Основа нашого асистента — це контекст (набір відомих гіпотез) та функція перевірки типів (Type Checker). Ми використаємо `std::map` для зберігання контексту `Gamma`.

```cpp
using Context = std::map<std::string, Type>;

// Функція для порівняння типів на еквівалентність
bool typesEqual(const Type& t1, const Type& t2) {
    if (t1.index() != t2.index()) return false;
    if (auto* b1 = std::get_if<BaseType>(&t1)) {
        return b1->name == std::get<BaseType>(t2).name;
    } else {
        auto a1 = std::get<std::shared_ptr<ArrowType>>(t1);
        auto a2 = std::get<std::shared_ptr<ArrowType>>(t2);
        return typesEqual(a1->from, a2->from) && typesEqual(a1->to, a2->to);
    }
}

// Головна функція виведення типів
Type typeCheck(const Term& term, Context ctx) {
    if (auto* v = std::get_if<VarTerm>(&term)) {
        if (ctx.find(v->name) != ctx.end()) {
            return ctx[v->name];
        }
        throw std::runtime_error("Невідома гіпотеза: " + v->name);
    } 
    else if (auto* abs = std::get_if<std::shared_ptr<AbsTerm>>(&term)) {
        // Додаємо гіпотезу в контекст
        Context newCtx = ctx;
        newCtx[(*abs)->paramName] = (*abs)->paramType;
        Type bodyType = typeCheck((*abs)->body, newCtx);
        return std::make_shared<ArrowType>(ArrowType{(*abs)->paramType, bodyType});
    } 
    else if (auto* app = std::get_if<std::shared_ptr<AppTerm>>(&term)) {
        Type funcType = typeCheck((*app)->func, ctx);
        Type argType = typeCheck((*app)->arg, ctx);
        
        if (auto* arrow = std::get_if<std::shared_ptr<ArrowType>>(&funcType)) {
            if (typesEqual((*arrow)->from, argType)) {
                return (*arrow)->to;
            } else {
                throw std::runtime_error("Невідповідність типів при застосуванні Modus Ponens");
            }
        }
        throw std::runtime_error("Спроба застосувати не-імплікацію");
    }
    throw std::runtime_error("Невідомий терм");
}
```

### 4. Збирання та тестування

Протестуємо наш перевіряльник на простому законі ідентичності (A → A), доведенням якого є лямбда-функція `λx:A. x`.

```cpp
int main() {
    Type A = BaseType{"A"};
    
    // Терм: λx:A. x
    Term id = std::make_shared<AbsTerm>(AbsTerm{
        "x", A, VarTerm{"x"}
    });

    try {
        Context emptyCtx;
        Type t = typeCheck(id, emptyCtx);
        std::cout << "Доведення коректне! Доведена теорема: ";
        printType(t); // Виведе (A -> A)
        std::cout << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Помилка доведення: " << e.what() << std::endl;
    }

    return 0;
}
```

Щоб зібрати програму, збережіть її у файл `proof_assistant.cpp` та скомпілюйте за допомогою компілятора з підтримкою C++17:
`g++ -std=c++17 -O2 proof_assistant.cpp -o proof_assistant`

### 5. Можливі розширення

Цей асистент є мінімалістичним, але він розкриває саму суть верифікації за Каррі — Говардом. Щоб перетворити його на потужніший інструмент, можна додати:
- **Кон'юнкцію та диз'юнкцію:** Додати підтримку пар (Pairs) та об'єднань (Variants) у синтаксис.
- **Парсер:** Реалізувати лексер та парсер, щоб вводити теореми та доведення текстом, замість конструювання AST вручну в коді.
- **Поліморфізм:** Додати підтримку систем типів вищого порядку (наприклад, System F) для можливості формулювати узагальнені теореми.
