#include <pthread.h>
#include <stdio.h>

static pthread_once_t init_flag = PTHREAD_ONCE_INIT;

void init_hardware_driver(void) {
    printf("Ініціалізація апаратного драйвера (POSIX C)...\n");
}

void process_request(void) {
    pthread_once(&init_flag, init_hardware_driver);
    /* Безпечна робота з ініціалізованим обладнанням */
}
