#include <stdint.h>

// Генерація наступного числа з тією самою кількістю одиничних бітів (Gosper's Hack)
uint64_t next_combination(uint64_t x) {
    uint64_t smallest = x & -x;             // виділити молодший встановлений біт
    uint64_t ripple = x + smallest;         // викликати перенос через групу одиниць
    uint64_t ones = x ^ ripple;             // знайти змінені біти
    ones = (ones >> 2) / smallest;          // вирівняти молодші одиниці праворуч
    return ripple | ones;
}
