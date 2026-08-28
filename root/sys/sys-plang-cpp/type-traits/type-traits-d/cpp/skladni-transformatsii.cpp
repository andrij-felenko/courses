// 1. Посилання на const-число:
using T1 = std::decay_t<const int&>;       // Перетворюється на int

// 2. Статичний масив символів:
using T2 = std::decay_t<const char[12]>;   // Перетворюється на const char*

// 3. Сигнатура функції:
using T3 = std::decay_t<void(int)>;        // Перетворюється на void(*)(int)

// 4. Вказівник на const-дані (const під вказівником не є топовим, тому залишається):
using T4 = std::decay_t<const int* const>; // Перетворюється на const int*
