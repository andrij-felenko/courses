#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm> // для std::sort

// 1. Швидке модульне піднесення до степеня (a^b mod m) за O(log b)
// Використання __uint128_t запобігає переповненню під час множення двох 64-бітних чисел.
uint64_t power_mod(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base = base % mod;
    while (exp > 0) {
        // Якщо поточний біт експоненти одиничний, множимо результат на поточну базу
        if (exp % 2 == 1) {
            res = (uint64_t)(((__uint128_t)res * base) % mod); 
        }
        // Підносимо базу в квадрат для наступного кроку
        base = (uint64_t)(((__uint128_t)base * base) % mod);
        exp /= 2; // Зсуваємо експоненту вправо
    }
    return res;
}

// 2. Обчислення найбільшого спільного дільника (НСД) класичним алгоритмом Евкліда
uint64_t gcd(uint64_t a, uint64_t b) {
    while (b) {
        a %= b;
        std::swap(a, b);
    }
    return a;
}

// 3. Обчислення функції Ейлера φ(n) за допомогою простої факторизації
// Використовує формулу: φ(n) = n * (1 - 1/p1) * (1 - 1/p2) ...
uint64_t euler_totient(uint64_t n) {
    uint64_t result = n;
    for (uint64_t i = 2; i * i <= n; i++) {
        // Якщо i є простим дільником n
        if (n % i == 0) {
            // Видаляємо всі входження цього дільника
            while (n % i == 0) {
                n /= i;
            }
            // Застосовуємо частину формули Ейлера
            result -= result / i;
        }
    }
    // Якщо після всього залишився простий множник, більший за sqrt(початкового n)
    if (n > 1) {
        result -= result / n;
    }
    return result;
}

// 4. Ефективний пошук усіх дільників числа (для числа φ(m))
std::vector<uint64_t> get_divisors(uint64_t n) {
    std::vector<uint64_t> divs;
    for (uint64_t i = 1; i * i <= n; i++) {
        if (n % i == 0) {
            divs.push_back(i); // Додаємо дільник i
            if (i * i != n) {
                divs.push_back(n / i); // Одразу додаємо симетричний дільник n/i
            }
        }
    }
    // Сортуємо масив, щоб перевіряти від найменшого дільника
    std::sort(divs.begin(), divs.end());
    return divs;
}

// 5. Головна оркеструюча функція пошуку порядку
uint64_t multiplicative_order(uint64_t a, uint64_t m) {
    // Якщо числа не взаємно прості, порядку не існує (мультиплікативна група не охоплює a)
    if (gcd(a, m) != 1) return 0; 
    
    // Крок А: знаходимо φ(m)
    uint64_t phi = euler_totient(m);
    
    // Крок Б: знаходимо всі можливі кандидати на порядок (дільники φ(m))
    std::vector<uint64_t> divs = get_divisors(phi);
    
    // Крок В: перевіряємо кандидати по зростанню
    for (uint64_t d : divs) {
        // Якщо a^d ≡ 1 (mod m), то d і є мультиплікативним порядком
        if (power_mod(a, d, m) == 1) {
            return d; 
        }
    }
    // За Теоремою Ейлера, цикл має закритися максимум на φ(m)
    return phi;
}

// Демонстрація роботи калькулятора
int main() {
    // Тестуємо для m = 13, a = 3 (Порядок = 3)
    uint64_t a = 3;
    uint64_t m = 13;
    
    uint64_t order = multiplicative_order(a, m);
    if (order == 0) {
        std::cout << "Порядок не існує, числа " << a << " та " << m << " не взаємно прості.\n";
    } else {
        std::cout << "Мультиплікативний порядок ord_" << m << "(" << a << ") = " << order << "\n";
    }
    
    // Тестуємо для великого складеного числа
    uint64_t a_big = 7;
    uint64_t m_big = 1000000007; // Відоме велике просте число
    std::cout << "Мультиплікативний порядок ord_" << m_big << "(" << a_big << ") = " 
              << multiplicative_order(a_big, m_big) << "\n";
              
    return 0;
}
