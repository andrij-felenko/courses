# ⚙️ Робочий клас Fixed Point на C++

Розуміння формату з фіксованою крапкою найлегше закріпити на практиці, написавши власну мініатюрну реалізацію на C++. Ми створимо шаблонний клас `FixedPoint`, який під капотом зберігає значення як звичайне ціле число (наприклад, 32-бітне `int32_t`), але абстрагує для користувача всі операції з дробовою частиною. Наш формат розділятиме 32 біти на 16 бітів для цілої частини та 16 бітів для дробової (формат Q16.16).

## Структура та конвертація

Головна ідея в тому, що користувач ініціалізує об'єкт звичайним дробовим числом типу `float`, а клас одразу зсуває крапку праворуч (множить на 2¹⁶). Всі внутрішні математичні операції робляться виключно з цілими числами, а коли користувачу потрібен результат, значення знову трансформується у `float` шляхом ділення.

```cpp
#include <cstdint>
#include <iostream>

template <typename BaseType = int32_t, int FractionalBits = 16>
class FixedPoint {
private:
    BaseType raw_value;
    
    // Коефіцієнт зсуву 2^16 (для 16 бітів це 65536)
    static constexpr BaseType SCALE = 1 << FractionalBits;

public:
    // 1. Конструктори
    FixedPoint() : raw_value(0) {}
    
    // Приймаємо float і зсуваємо вліво (множимо на SCALE)
    explicit FixedPoint(float f) : raw_value(static_cast<BaseType>(f * SCALE)) {}

    // Конструктор від "сирого" цілого значення для внутрішніх операцій
    static FixedPoint fromRaw(BaseType raw) {
        FixedPoint fp;
        fp.raw_value = raw;
        return fp;
    }

    // 2. Зворотна конвертація для виводу
    float toFloat() const {
        return static_cast<float>(raw_value) / SCALE;
    }

    // 3. Додавання та віднімання
    // Додавання і віднімання не потребують зсувів, адже крапка в обох операндах фіксована
    FixedPoint operator+(const FixedPoint& other) const {
        return FixedPoint::fromRaw(this->raw_value + other.raw_value);
    }

    FixedPoint operator-(const FixedPoint& other) const {
        return FixedPoint::fromRaw(this->raw_value - other.raw_value);
    }

    // 4. Множення
    // При множенні (X * SCALE) * (Y * SCALE) отримуємо X * Y * SCALE^2.
    // Тому результат треба один раз поділити на SCALE (зсунути вправо).
    // Щоб уникнути переповнення, перед множенням переводимо в 64 біти.
    FixedPoint operator*(const FixedPoint& other) const {
        int64_t temp = static_cast<int64_t>(this->raw_value) * other.raw_value;
        return FixedPoint::fromRaw(static_cast<BaseType>(temp >> FractionalBits));
    }

    // 5. Ділення
    // (X * SCALE) / (Y * SCALE) = X / Y (ми губимо масштаб SCALE повністю!).
    // Щоб зберегти формат, ділене треба спочатку домножити на SCALE.
    FixedPoint operator/(const FixedPoint& other) const {
        int64_t temp = (static_cast<int64_t>(this->raw_value) << FractionalBits);
        return FixedPoint::fromRaw(static_cast<BaseType>(temp / other.raw_value));
    }
};

int main() {
    // Демонстрація роботи
    FixedPoint<int32_t, 16> a(10.5f);
    FixedPoint<int32_t, 16> b(2.25f);
    
    auto sum = a + b;
    auto diff = a - b;
    auto mult = a * b;
    auto div = a / b;

    std::cout << "A: " << a.toFloat() << ", B: " << b.toFloat() << "\n";
    std::cout << "Sum: " << sum.toFloat() << " (Expected 12.75)\n";
    std::cout << "Diff: " << diff.toFloat() << " (Expected 8.25)\n";
    std::cout << "Mult: " << mult.toFloat() << " (Expected 23.625)\n";
    std::cout << "Div: " << div.toFloat() << " (Expected 4.666...)\n";

    return 0;
}
```

## Розбір ключових механізмів

Цей приклад складається з п'яти класичних компонентів, притаманних будь-якому рушію Fixed Point:

1. **Конструювання.** `float` домножується на константу масштабу `SCALE` (2¹⁶ = 65536) і конвертується в ціле число. 10.5 стає 688128.
2. **Конвертація назад.** Ціле число ділиться на 65536, повертаючи дробове значення, зрозуміле людині.
3. **Лінійні операції (+, -).** Виконуються як звичайне додавання цілих чисел. Жодних прихованих накладних витрат процесора.
4. **Множення.** Це найнебезпечніше місце. При множенні Q16.16 на Q16.16 ми отримуємо результат формату Q32.32, який уже не влазить у 32 біти. Тому проміжний результат ми мусимо помістити у 64-бітний `int64_t`. Після множення ми зсуваємо його вправо на 16 позицій `>> FractionalBits`, повертаючи крапку на її законне місце.
5. **Ділення.** Коли ми ділимо `raw_value` на `other.raw_value`, ми ділимо масштаб на масштаб, повністю знищуючи дробову частину і залишаючи лише голі цілі одиниці. Тому ми спершу зсуваємо ділене вліво (піднімаємо його в розрядності `<< FractionalBits` у 64-бітному регістрі), а лише потім ділимо.

Така реалізація є надзвичайно швидкою і використовується в ігрових рушіях на старих консолях (наприклад, PS1 або GBA, де взагалі немає апаратного FPU), а також у сучасних вбудованих системах на базі дешевих мікроконтролерів Cortex-M0 для обробки сигналів давачів.
