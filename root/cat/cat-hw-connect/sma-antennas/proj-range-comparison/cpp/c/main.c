#include "radio.h"
#include <stdio.h>
#include <unistd.h>

int main(void) {
    RadioModule radio = {-1};
    
    if (radio_init(&radio, "/dev/spidev0.0") != 0) {
        printf("Помилка ініціалізації радіомодуля.\n");
        return 1;
    }
    
    printf("Радіомодуль ініціалізовано. Початок зчитування RSSI...\n");
    
    for (int i = 0; i < 5; ++i) {
        int8_t rssi = 0;
        if (radio_get_rssi(&radio, &rssi) == 0) {
            printf("Якість зв'язку (RSSI): %d дБм\n", rssi);
        } else {
            printf("Помилка зчитування RSSI.\n");
        }
        sleep(1);
    }
    
    radio_close(&radio);
    return 0;
}
