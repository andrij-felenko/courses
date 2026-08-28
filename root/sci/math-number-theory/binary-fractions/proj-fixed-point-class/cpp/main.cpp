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
