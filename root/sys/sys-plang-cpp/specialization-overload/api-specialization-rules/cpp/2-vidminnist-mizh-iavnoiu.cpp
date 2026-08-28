template<typename T>
struct DataHolder {
    void compute() {}
};

// 1. ЯВНА ІНСТАНЦІАЦІЯ (Explicit Instantiation Definition):
// Змушує компілятор згенерувати код для DataHolder<int> за правилами ПЕРВИННОГО шаблону.
// Зверніть увагу: після template немає кутових дужок <>!
template struct DataHolder<int>;

// 2. ДЕКЛАРАЦІЯ ЯВНОЇ ІНСТАНЦІАЦІЇ (C++11 extern template):
// Забороняє компілятору генерувати код у поточній одиниці трансляції (економія часу збірки).
extern template struct DataHolder<int>;

// 3. ЯВНА СПЕЦІАЛІЗАЦІЯ (Explicit Specialization):
// Повністю ЗАМІЩУЄ первинний шаблон альтернативним користувацьким кодом.
// Обов'язково починається з template<>!
template<>
struct DataHolder<double> {
    void custom_algorithm() {}
};
