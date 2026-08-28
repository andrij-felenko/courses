#include <iostream>
#include <numeric>
#include <vector>

// Структура для зберігання знайденої Піфагорової трійки
struct PythagoreanTriple {
    long long a;
    long long b;
    long long c;
};

// Головна функція генерації трійок з обмеженням на гіпотенузу
std::vector<PythagoreanTriple> generatePrimitiveTriples(long long max_c) {
    std::vector<PythagoreanTriple> triples;
    
    // Зовнішній цикл: перебираємо m. 
    // Оскільки c = m^2 + n^2, верхня межа для m - це квадратний корінь з max_c.
    for (long long m = 2; m * m <= max_c; ++m) {
        
        // Внутрішній цикл: перебираємо n від 1 до m-1 (інваріант m > n > 0)
        for (long long n = 1; n < m; ++n) {
            
            // Інваріант парності: m та n повинні мати різну парність.
            // Якщо остачі від ділення на 2 однакові, пропускаємо ітерацію.
            if ((m % 2) == (n % 2)) {
                continue;
            }
            
            // Інваріант взаємної простоти: найбільший спільний дільник має бути 1.
            if (std::gcd(m, n) != 1) {
                continue;
            }
            
            // Обчислення сторін a, b, c за параметричними формулами методу хорди
            long long a = m * m - n * n;
            long long b = 2 * m * n;
            long long c = m * m + n * n;
            
            // Запобіжник: хоча m*m <= max_c, сума m^2 + n^2 може вийти за межу.
            if (c > max_c) {
                break; // Оскільки n зростає, наступні c теж будуть більшими, тому break.
            }
            
            // Усі перевірки пройдено, додаємо нову примітивну трійку до результату
            triples.push_back({a, b, c});
        }
    }
    return triples;
}

int main() {
    // Встановлюємо межу гіпотенузи
    long long max_hypotenuse = 100;
    
    // Викликаємо алгоритм генерації
    auto triples = generatePrimitiveTriples(max_hypotenuse);
    
    // Виводимо всі знайдені примітивні трійки на екран
    std::cout << "Примітивні Піфагорові трійки з гіпотенузою до " << max_hypotenuse << ":\n";
    for (const auto& t : triples) {
        std::cout << "(" << t.a << ", " << t.b << ", " << t.c << ")\n";
    }
    
    return 0;
}
