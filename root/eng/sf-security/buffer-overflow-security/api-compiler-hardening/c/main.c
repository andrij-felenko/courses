#include <sys/prctl.h>
#include <stdio.h>

#ifndef PR_SET_SHADOW_STACK_STATUS
#define PR_SET_SHADOW_STACK_STATUS 75
#define PR_GET_SHADOW_STACK_STATUS 74
#define PR_LOCK_SHADOW_STACK_STATUS 76
#define PR_SHADOW_STACK_ENABLE     (1UL << 0)
#define PR_SHADOW_STACK_WRITE      (1UL << 1)
#endif

int configure_shadow_stack(void) {
    // Примусова активація апаратного тіньового стека для поточного процесу
    if (prctl(PR_SET_SHADOW_STACK_STATUS, PR_SHADOW_STACK_ENABLE, 0, 0, 0) != 0) {
        perror("Помилка: процесор або ядро не підтримують Intel CET");
        return -1;
    }

    // Блокування подальшої зміни статусу для захисту від вимкнення зловмисником
    if (prctl(PR_LOCK_SHADOW_STACK_STATUS, PR_SHADOW_STACK_ENABLE, 0, 0, 0) != 0) {
        perror("Помилка блокування конфігурації Shadow Stack");
        return -1;
    }

    return 0;
}
