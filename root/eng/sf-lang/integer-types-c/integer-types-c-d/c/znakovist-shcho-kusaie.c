#include <stdint.h>
#include <stdio.h>

int main(void) {
    int idx = -1;                 // знакове: помилковий/«ще не знайдено» індекс
    char buf[10];

    // намір: «якщо idx у межах масиву» — але sizeof беззнаковий!
    if (idx < sizeof(buf)) {      // idx стає беззнаковим → 0xFFFFFFFF
        printf("idx у межах\n");  // НЕ надрукується: 4294967295 < 10 хибне
    } else {
        printf("idx поза межами\n");  // саме ця гілка — хоч намір був інший
    }
    return 0;
}
