#include <iostream>
#include <vector>
#include <cmath>
#include <map>

// Структура для збереження стану
struct State {
    long long m;
    long long d;
    
    // Оператор порівняння для використання State як ключа у std::map
    bool operator<(const State& other) const {
        if (m != other.m) return m < other.m;
        return d < other.d;
    }
};

// Функція для розкладу (m + sqrt(D)) / d
void calculateContinuedFraction(long long D, long long m_start = 0, long long d_start = 1) {
    long long sqrt_D = std::floor(std::sqrt(D));
    
    // Перевірка, чи є D точним квадратом
    if (sqrt_D * sqrt_D == D) {
        std::cout << "Помилка: D є точним квадратом, корінь раціональний." << std::endl;
        return;
    }

    long long m = m_start;
    long long d = d_start;
    
    std::vector<long long> a_seq;
    std::map<State, int> history; // Зберігає стан і його індекс у послідовності
    
    int step = 0;
    int period_start = -1;

    while (true) {
        State current_state = {m, d};
        
        // Перевіряємо, чи ми вже бачили цей стан
        if (history.find(current_state) != history.end()) {
            period_start = history[current_state];
            break;
        }
        
        history[current_state] = step;
        
        // Крок 1: обчислюємо цілу частину a
        long long a = (m + sqrt_D) / d;
        a_seq.push_back(a);
        
        // Крок 2 та 3: оновлюємо m та d
        m = a * d - m;
        d = (D - m * m) / d;
        
        step++;
    }

    // Виведення результату
    std::cout << "Ланцюговий дріб для sqrt(" << D << "): [";
    std::cout << a_seq[0] << "; ";
    
    for (int i = 1; i < a_seq.size(); ++i) {
        if (i == period_start) {
            std::cout << "(";
        }
        std::cout << a_seq[i];
        if (i < a_seq.size() - 1) {
            std::cout << ", ";
        }
    }
    std::cout << ")]" << std::endl;
    
    std::cout << "[Періодичність раціональних двійкових дробів](root:math-number-theory/binary-period-length): " << a_seq.size() - period_start << std::endl;
}

int main() {
    // Тестуємо для sqrt(2)
    calculateContinuedFraction(2);
    // Тестуємо для sqrt(7)
    calculateContinuedFraction(7);
    
    return 0;
}
