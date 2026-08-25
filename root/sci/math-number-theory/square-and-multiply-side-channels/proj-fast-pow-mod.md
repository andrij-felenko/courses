# Проєкт: Швидке модульне піднесення до степеня на C++

У цьому проєкті ми реалізуємо алгоритм Square-and-multiply на мові C++ (стандарт C++17). Для того, щоб код був універсальним, ми створимо функцію для стандартних 64-бітних чисел (`uint64_t`), а також покажемо структуру для абстрактного класу великих чисел (`BigInt`). 

Структура проєкту складатиметься з 5 логічних компонентів, що гарантує легкість розширення та тестування.

### 1. Інтерфейси (Headers)

Спочатку визначимо декларацію нашої основної функції. Ми будемо використовувати шаблон (template), щоб алгоритм міг працювати з будь-якими цілочисельними типами, які підтримують операції множення, ділення по модулю та бітові зсуви.

```cpp
#pragma once
#include <cstdint>
#include <stdexcept>

namespace MathLib {
    // Шаблонна функція для швидкого піднесення до степеня
    template <typename T>
    T pow_mod(T base, T exponent, T mod);
}
```

### 2. Утиліти (Безпечне множення)

Коли ми перемножуємо два 64-бітні числа, результат може займати до 128 бітів. Якщо ми використовуємо звичайне множення `(a * b) % m`, може статися арифметичне переповнення. Щоб цього уникнути для `uint64_t`, ми можемо використати розширені типи компілятора, наприклад `__uint128_t` (доступно у GCC та Clang).

```cpp
namespace MathLib {
    namespace Utils {
        inline uint64_t mul_mod(uint64_t a, uint64_t b, uint64_t m) {
            // Використовуємо 128-бітну арифметику для уникнення переповнення
            return static_cast<uint64_t>((static_cast<__uint128_t>(a) * b) % m);
        }
    }
}
```

### 3. Основна логіка алгоритму

Тепер реалізуємо класичний метод "справа наліво" (Right-to-Left). Він чудово лягає на цикли `while` та побітові операції.

```cpp
#include "pow_mod.h"

namespace MathLib {
    // Спеціалізація для uint64_t
    template <>
    uint64_t pow_mod<uint64_t>(uint64_t base, uint64_t exponent, uint64_t mod) {
        if (mod == 0) {
            throw std::invalid_argument("Modulo cannot be zero");
        }
        if (mod == 1) {
            return 0; // Будь-яке число mod 1 дорівнює 0
        }

        uint64_t result = 1;
        base = base % mod;

        while (exponent > 0) {
            // Перевіряємо наймолодший біт (еквівалент exponent % 2 == 1)
            if (exponent & 1) {
                result = Utils::mul_mod(result, base, mod);
            }
            
            // Піднесення основи до квадрата
            base = Utils::mul_mod(base, base, mod);
            
            // Зсуваємо показник на 1 біт вправо (еквівалент exponent / 2)
            exponent >>= 1;
        }

        return result;
    }
}
```

### 4. Робота з BigInt

Для криптографії `uint64_t` замало. Якщо ви маєте власний клас `BigInt` (або використовуєте бібліотеку GMP), шаблонна функція потребує лише наявності перевантажених операторів. Приклад обгортки для `BigInt`:

```cpp
class BigInt {
public:
    // ... імплементація конструкторів та зберігання даних ...
    
    BigInt operator*(const BigInt& other) const;
    BigInt operator%(const BigInt& mod) const;
    BigInt& operator>>=(size_t shift);
    bool is_odd() const;
    bool is_zero() const;
};

// Алгоритм виглядатиме ідентично завдяки перевантаженню
BigInt pow_mod_big(BigInt base, BigInt exponent, BigInt mod) {
    BigInt result = BigInt(1);
    base = base % mod;
    
    while (!exponent.is_zero()) {
        if (exponent.is_odd()) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exponent >>= 1;
    }
    return result;
}
```

### 5. Тести (Unit tests)

Закінчимо простою перевіркою коректності нашої реалізації.

```cpp
#include <iostream>
#include <cassert>

using namespace MathLib;

void test_pow_mod() {
    // 3^13 mod 17 = 12
    assert(pow_mod<uint64_t>(3, 13, 17) == 12);
    
    // 2^10 mod 1000 = 24
    assert(pow_mod<uint64_t>(2, 10, 1000) == 24);
    
    // 5^0 mod 7 = 1
    assert(pow_mod<uint64_t>(5, 0, 7) == 1);
    
    // Великі числа (менше 64 біт, але легко переповнюються без __uint128_t)
    uint64_t large_base = 1000000007;
    uint64_t large_exp = 999999999;
    uint64_t mod = 1000000009;
    assert(pow_mod<uint64_t>(large_base, large_exp, mod) > 0);
    
    std::cout << "All pow_mod tests passed!" << std::endl;
}

int main() {
    test_pow_mod();
    return 0;
}
```

Цей 5-компонентний підхід забезпечує надійність, типобезпечність та легкість міграції коду до промислових проєктів із використанням справжніх довгої арифметики.
