#include <iostream>
#include <numeric>
#include <vector>
#include <algorithm>

// 1. Функція обчислення найбільшого спільного дільника
int gcd(int a, int b) {
    while (b) {
        a %= b;
        std::swap(a, b);
    }
    return a;
}

// 2. Обчислення a^b (mod n)
int power_mod(int base, int exp, int mod) {
    int res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (res * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return res;
}

// 3. Знаходження порядку елемента a в (Z/nZ)*
int find_element_order(int a, int n, int phi) {
    // Порядок повинен бути дільником phi(n) (теорема Лагранжа)
    int order = phi;
    for (int i = 1; i * i <= phi; ++i) {
        if (phi % i == 0) {
            // Перевіряємо i
            if (power_mod(a, i, n) == 1) {
                order = std::min(order, i);
            }
            // Перевіряємо phi/i
            if (power_mod(a, phi / i, n) == 1) {
                order = std::min(order, phi / i);
            }
        }
    }
    return order;
}

// 4. Головна логіка аналізатора
void analyze_group(int n) {
    std::vector<int> elements;
    
    // Знаходимо всі оборотні елементи
    for (int i = 1; i < n; ++i) {
        if (gcd(i, n) == 1) {
            elements.push_back(i);
        }
    }
    
    int phi = elements.size();
    std::cout << "Аналіз мультиплікативної групи (Z/" << n << "Z)*\n";
    std::cout << "Порядок групи (phi(" << n << ")): " << phi << "\n";
    std::cout << "Елементи: ";
    for (int e : elements) std::cout << e << " ";
    std::cout << "\n\n";
    
    // Аналізуємо порядки
    int max_order = 0;
    std::vector<int> generators;
    
    std::cout << "Порядки елементів:\n";
    for (int e : elements) {
        int order = find_element_order(e, n, phi);
        std::cout << e << "^" << order << " = 1\n";
        max_order = std::max(max_order, order);
        if (order == phi) {
            generators.push_back(e);
        }
    }
    
    std::cout << "\nМаксимальний порядок елемента: " << max_order << "\n";
    
    if (!generators.empty()) {
        std::cout << "Група є циклічною!\nПервісні корені: ";
        for (int g : generators) std::cout << g << " ";
        std::cout << "\n";
    } else {
        std::cout << "Група НЕ є циклічною (максимальний порядок < phi(" << n << ")).\n";
    }
}

// 5. Точка входу
int main() {
    int n;
    std::cout << "Введіть модуль n: ";
    if (std::cin >> n && n > 1) {
        analyze_group(n);
    } else {
        std::cout << "Помилка вводу. Модуль має бути цілим числом > 1.\n";
    }
    return 0;
}
