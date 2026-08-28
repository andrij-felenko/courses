std::vector<int> vec = {10, 20, 30};

// 1. Звичайний ітератор
auto it = vec.begin(); 
*it = 15; // OK
++it;    // OK

// 2. Константний ітератор (const_iterator)
std::vector<int>::const_iterator cit = vec.cbegin(); 
// *cit = 25; // ✗ Помилка компіляції: спроба модифікувати const даних
++cit;        // ✓ OK: ітератор вільно рухається

// 3. Константний об'єкт ітератора
const auto const_it = vec.begin();
*const_it = 99; // ✓ OK: вміст змінювати можна
// ++const_it;  // ✗ Помилка компіляції: сам ітератор є const
