#include "ahct_buffer.h"

int main(void) {
    ahct_buffer_t buffer;

    /* 1. Ініціалізація апаратного забезпечення та захисного стану буфера (OE = High -> Z-стан) */
    ahct_buffer_init(&buffer);

    /* Симуляція затримки ініціалізації системи / стабілізації живлення 5V/3.3V */
    for (volatile int i = 0; i < 1000; i++) {
        /* Очікування */
    }

    /* 2. Безпечне увімкнення буфера 74AHCT (OE = Low) після завершення налаштувань */
    ahct_buffer_enable(&buffer);

    /* 3. Робочий цикл: верифікація сигналів короткими імпульсами */
    for (int cycle = 0; cycle < 10; cycle++) {
        ahct_buffer_verify_signal(&buffer);
        
        for (volatile int d = 0; d < 500; d++) {
            /* Пауза між імпульсами */
        }
    }

    /* 4. Вимкнення буфера перед завершенням роботи або переходом у сон */
    ahct_buffer_disable(&buffer);

    while (1) {
        /* Нескінченний цикл у безпечному стані */
    }

    return 0;
}
