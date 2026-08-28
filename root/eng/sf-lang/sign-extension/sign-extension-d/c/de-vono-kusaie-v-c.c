#include <stdio.h>

int main(void) {
    char c = 0xFF;            // якщо char знаковий — це −1, а не 255

    if (c == 0xFF)           // 0xFF тут — int 255; c розшириться до int −1
        printf("рівні\n");   // на знаковому char НЕ надрукується!
    else
        printf("не рівні: c = %d\n", c);   // виведе: не рівні: c = −1

    return 0;
}
