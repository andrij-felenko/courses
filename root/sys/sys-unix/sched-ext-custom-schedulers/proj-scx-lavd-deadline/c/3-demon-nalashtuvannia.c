// C Реалізація налаштування топології
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    PROFILE_GAMING,
    PROFILE_BATTERY
} lavd_profile_t;

void set_lavd_profile(lavd_profile_t profile) {
    if (profile == PROFILE_GAMING) {
        printf("[LAVD C] Режим GAMING: ігрові потоки закріплено за L3 domain.\n");
    } else {
        printf("[LAVD C] Режим BATTERY: активувати ущільнення ядер.\n");
    }
}

int main(void) {
    set_lavd_profile(PROFILE_GAMING);
    return 0;
}
