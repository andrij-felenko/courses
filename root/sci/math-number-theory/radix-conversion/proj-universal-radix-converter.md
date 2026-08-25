# Універсальний конвертер систем числення (C++17)

Для закріплення розуміння алгоритмів Горнера та послідовного ділення/множення, створимо консольну програму на C++, здатну переводити довільні числа (зокрема й дробові) між будь-якими базами від 2 до 36.

## Структура програми

Архітектура нашого конвертера складається з п'яти ключових компонентів:
1. `val(char c)` — мапер символу в числове значення.
2. `chr(int v)` — зворотний мапер числа в символ.
3. `to_decimal()` — зчитує рядок у базі B1 і перетворює його в дробове число (типу `double`) за схемою Горнера.
4. `from_decimal()` — перетворює `double` у рядок бази B2 за допомогою ділення (для цілої) та множення (для дробової частини).
5. `main()` — обробка вводу-виводу.

## Код конвертера

```cpp
#include <iostream>
#include <string>
#include <cmath>
#include <algorithm>

using namespace std;

// 1. Мапер символу в значення (0-9, A-Z)
int val(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'Z') return c - 'A' + 10;
    if (c >= 'a' && c <= 'z') return c - 'a' + 10;
    return 0;
}

// 2. Мапер значення в символ
char chr(int v) {
    if (v >= 0 && v <= 9) return (char)(v + '0');
    return (char)(v - 10 + 'A');
}

// 3. Переведення з бази B1 у десяткову систему (Схема Горнера)
double to_decimal(const string& str, int b1) {
    size_t dot_pos = str.find('.');
    string int_part = (dot_pos == string::npos) ? str : str.substr(0, dot_pos);
    string frac_part = (dot_pos == string::npos) ? "" : str.substr(dot_pos + 1);

    double result = 0;
    
    // Схема Горнера для цілої частини
    for (char c : int_part) {
        result = result * b1 + val(c);
    }
    
    // Схема Горнера для дробової частини (рахуємо справа наліво або з від'ємними ступенями)
    double frac_val = 0;
    double divisor = b1;
    for (char c : frac_part) {
        frac_val += val(c) / divisor;
        divisor *= b1;
    }
    
    return result + frac_val;
}

// 4. Переведення з десяткової в базу B2
string from_decimal(double num, int b2, int precision = 5) {
    long long int_part = (long long)num;
    double frac_part = num - int_part;
    
    string int_str = "";
    
    // Метод послідовного ділення (для цілої частини)
    if (int_part == 0) {
        int_str = "0";
    } else {
        while (int_part > 0) {
            int rem = int_part % b2;
            int_str += chr(rem);
            int_part /= b2;
        }
        reverse(int_str.begin(), int_str.end());
    }
    
    // Метод послідовного множення (для дробової частини)
    string frac_str = "";
    while (frac_part > 0 && precision > 0) {
        frac_part *= b2;
        int digit = (int)frac_part;
        frac_str += chr(digit);
        frac_part -= digit;
        precision--;
    }
    
    if (frac_str.empty()) {
        return int_str;
    }
    return int_str + "." + frac_str;
}

// 5. Точка входу
int main() {
    string number;
    int b1, b2;
    
    cout << "Уведіть число, базову систему та цільову систему (напр., 1A.8 16 2):\n> ";
    if (cin >> number >> b1 >> b2) {
        if (b1 < 2 || b1 > 36 || b2 < 2 || b2 > 36) {
            cout << "Помилка: системи числення мають бути в діапазоні 2..36\n";
            return 1;
        }
        
        double dec_val = to_decimal(number, b1);
        string result = from_decimal(dec_val, b2, 10);
        
        cout << "Результат: " << result << "\n";
    }
    
    return 0;
}
```

## Розбір особливостей

1. **Дробова частина у `to_decimal`:** Замість класичного `val(c) * b1^(-i)`, ми тримаємо акумулятор `divisor`, який щокроку множиться на `b1`. Це захищає від використання дорогої функції `pow()` і зберігає принцип Горнера.
2. **Точність `precision`:** Метод послідовного множення може призвести до нескінченного циклу, оскільки деякі числа (наприклад, 0,1 в десятковій) не мають скінченного представлення у двійковій системі. Ми штучно обмежуємо кількість ітерацій змінною `precision`.
3. **Обмеження `double`:** Скрипт чудово підходить для навчання, але тип `double` має ліміт точності (близько 15-17 значущих десяткових цифр). Для криптографії чи великих баз даних конвертери пишуть з використанням бібліотек довгої арифметики (BigInt), де ділення та множення застосовують до масивів байтів, а не примітивів.
