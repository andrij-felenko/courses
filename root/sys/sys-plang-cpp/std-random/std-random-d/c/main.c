#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Старий C-підхід (з присутнім Modulo Bias та небезпекою глобального стану)
int roll_dice_c(void) {
    // 1. Поганий посів через час у секундах (time_t)
    // Якщо програма перезапускається двічі за секунду, послідовність буде тотожною
    // 2. Modulo bias при діленні на 6
    return (rand() % 6) + 1;
}

int main(void) {
    // Ініціалізація глобального стану LCG
    srand((unsigned int)time(NULL));

    for (int i = 0; i < 5; ++i) {
        printf("C Dice Roll: %d\n", roll_dice_c());
    }
    return 0;
}
