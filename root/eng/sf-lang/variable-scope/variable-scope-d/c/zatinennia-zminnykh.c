#include <stdio.h>

int val = 100; // [A] Глобальна змінна

int main(void) {
    int val = 200; // [B] Затінює глобальну [A]
    printf("Local val = %d\n", val); // 200

    {
        int val = 300; // [C] Затінює локальну [B]
        printf("Inner block val = %d\n", val); // 300
    }

    printf("Back to local val = %d\n", val); // 200
    return 0;
}
