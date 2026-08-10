# ⚙️ Генератор таблиць істинності (Truth Table Generator)

Обчислення повних таблиць істинності для пропозиційних формул спирається на перебір `2^N` векторів станів вхідних змінних для верифікації тавтологій та логічної еквівалентності.

## Постановка інженерної задачі та інтуїція рішення
У логіці висловлювань (пропозиційній логіці) будь-яка формула, побудована з N унікальних змінних, має точно 2^N можливих комбінацій істинносних значень (True/False). Інженерна мета — створити ефективний обчислювальний рушій, який перебирає всі ці 2^N станів і для кожного оцінює значення формули. Оскільки N рідко перевищує 32 у базових задачах (зазвичай 3–10), ми можемо використати побітові операції над цілими числами для генерації станів, де кожен біт числа від 0 до (2^N - 1) репрезентує значення окремої логічної змінної.

Вхідними даними є пропозиційна формула у вигляді абстрактного синтаксичного дерева (AST), яке ми обходимо рекурсивно для кожної з 2^N конфігурацій. Вихідними даними є згенерована таблиця, що відображає набір значень змінних та фінальний результат формули.

## Логічна архітектура та алгоритм бітового обходу
Рішення спирається на те, що ціле число (наприклад, 32-бітне `uint32_t`) може природним чином інкапсулювати стан до 32 логічних змінних. 
1. Визначаємо кількість унікальних змінних N.
2. Ініціалізуємо цикл від `mask = 0` до `mask = (1 << N) - 1`.
3. У кожній ітерації `mask` містить конфігурацію змінних: якщо i-тий біт дорівнює 1, то i-та змінна істинна (True), інакше — хибна (False).
4. Передаємо поточну конфігурацію у функцію оцінки AST, яка рекурсивно або ітеративно (якщо використовується зворотна польська нотація) обчислює результат.
5. Зберігаємо або виводимо результат для поточного рядка таблиці істинності.

Цей підхід мінімізує накладні витрати на виділення пам'яті (ніяких масивів булевих значень, лише регістри процесора).

## Повний робочий код на C++

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <unordered_map>

// Базовий клас для вузлів абстрактного синтаксичного дерева (AST)
class ASTNode {
public:
    virtual ~ASTNode() = default;
    // Метод evaluate приймає поточну бітову маску стану та мапу індексів змінних
    virtual bool evaluate(uint32_t stateMask, const std::unordered_map<std::string, int>& varIndices) const = 0;
};

// Вузол змінної (наприклад, "A", "B")
class VarNode : public ASTNode {
    std::string name;
public:
    explicit VarNode(std::string n) : name(std::move(n)) {}
    bool evaluate(uint32_t stateMask, const std::unordered_map<std::string, int>& varIndices) const override {
        // Знаходимо індекс змінної (0, 1, 2...)
        auto it = varIndices.find(name);
        if (it == varIndices.end()) return false; // Запобіжник (edge case)
        
        int bitIndex = it->second;
        // Витягуємо значення i-го біта з маски
        return (stateMask & (1 << bitIndex)) != 0;
    }
};

// Вузол логічного "І" (AND)
class AndNode : public ASTNode {
    std::unique_ptr<ASTNode> left, right;
public:
    AndNode(std::unique_ptr<ASTNode> l, std::unique_ptr<ASTNode> r) 
        : left(std::move(l)), right(std::move(r)) {}
        
    bool evaluate(uint32_t stateMask, const std::unordered_map<std::string, int>& varIndices) const override {
        return left->evaluate(stateMask, varIndices) && right->evaluate(stateMask, varIndices);
    }
};

// Вузол логічного "АБО" (OR)
class OrNode : public ASTNode {
    std::unique_ptr<ASTNode> left, right;
public:
    OrNode(std::unique_ptr<ASTNode> l, std::unique_ptr<ASTNode> r) 
        : left(std::move(l)), right(std::move(r)) {}
        
    bool evaluate(uint32_t stateMask, const std::unordered_map<std::string, int>& varIndices) const override {
        return left->evaluate(stateMask, varIndices) || right->evaluate(stateMask, varIndices);
    }
};

// Функція генерації та виводу таблиці істинності
void generateTruthTable(const ASTNode& root, const std::vector<std::string>& vars) {
    int numVars = vars.size();
    if (numVars > 31) {
        std::cerr << "Переповнення: підтримується до 31 змінної." << std::endl;
        return;
    }

    std::unordered_map<std::string, int> varIndices;
    for (int i = 0; i < numVars; ++i) {
        varIndices[vars[i]] = i;
        std::cout << vars[i] << "\t";
    }
    std::cout << "| Result\n";
    std::cout << std::string(numVars * 8 + 10, '-') << "\n";

    // Перебираємо всі 2^N комбінацій
    uint32_t totalCombinations = 1 << numVars;
    for (uint32_t stateMask = 0; stateMask < totalCombinations; ++stateMask) {
        // Вивід значень змінних
        for (int i = 0; i < numVars; ++i) {
            bool val = (stateMask & (1 << i)) != 0;
            std::cout << (val ? "T" : "F") << "\t";
        }
        
        // Оцінка формули
        bool result = root.evaluate(stateMask, varIndices);
        std::cout << "| " << (result ? "T" : "F") << "\n";
    }
}

int main() {
    // Конструюємо AST для формули: (A AND B) OR A
    std::vector<std::string> vars = {"A", "B"};
    
    auto a1 = std::make_unique<VarNode>("A");
    auto b1 = std::make_unique<VarNode>("B");
    auto andNode = std::make_unique<AndNode>(std::move(a1), std::move(b1));
    
    auto a2 = std::make_unique<VarNode>("A");
    auto root = std::make_unique<OrNode>(std::move(andNode), std::move(a2));

    generateTruthTable(*root, vars);
    return 0;
}
```

## Построчний аналіз, пам'ять та керування ресурсами
У коді ми використовуємо сучасні C++ розумні вказівники `std::unique_ptr` для конструювання абстрактного синтаксичного дерева. Це гарантує, що при знищенні кореневого вузла все дерево буде рекурсивно і безпечно видалене з купи (heap), запобігаючи витокам пам'яті (memory leaks).

Основна магія відбувається у циклі `for (uint32_t stateMask = 0; stateMask < totalCombinations; ++stateMask)`. Ми не виділяємо нові масиви або вектори для зберігання станів; натомість ми передаємо одне ціле число `stateMask` по значенню на кожен рівень рекурсії. Метод `evaluate` класу `VarNode` використовує швидку побітову операцію `(stateMask & (1 << bitIndex)) != 0`, щоб миттєво визначити стан змінної. Це вирішує проблему накладних витрат на пам'ять та мінімізує промахи кешу (cache misses).

Ми також додали перевірку переповнення `if (numVars > 31)`. Оскільки `1 << 32` на 32-бітних регістрах спричиняє невизначену поведінку (Undefined Behavior) і може переповнити `uint32_t`, ми зупиняємо виконання, якщо користувач вимагає занадто багато змінних.

## Вхідні та вихідні дані і оцінка складності (I/O)
Приклад виконання для формули `(A AND B) OR A`:
```text
A       B       | Result
--------------------------
F       F       | F
T       F       | T
F       T       | F
T       T       | T
```

**Оцінка складності:**
- **Часова складність:** O(2^N * M), де N — кількість змінних, а M — кількість вузлів у AST. Ми обходимо дерево розміру M рівно 2^N разів. Зростання експоненційне, тому цей метод підходить лише для N <= 25-30.
- **Просторова складність:** O(M) для зберігання AST, плюс O(N) для глибини стеку викликів під час рекурсивної оцінки. Самі стани не споживають додаткової пам'яті, що робить просторову складність дуже низькою (майже O(1) додаткової пам'яті під час виконання).
