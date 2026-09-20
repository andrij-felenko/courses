#include <stdio.h>
#include <unistd.h>
#include "radio_rssi.h"

int main(void) {
    radio_module_t radio_433;
    radio_module_t radio_24;
    
    printf("Ініціалізація радіомодулів...\n");
    
    if (!radio_init(&radio_433, FREQ_433_MHZ, 1)) {
        fprintf(stderr, "Помилка ініціалізації модуля 433 МГц\n");
        return 1;
    }
    
    if (!radio_init(&radio_24, FREQ_2400_MHZ, 2)) {
        fprintf(stderr, "Помилка ініціалізації модуля 2.4 ГГц\n");
        radio_close(&radio_433);
        return 1;
    }
    
    printf("Початок зчитування показників антен SMA...\n");
    printf("Натисніть Ctrl+C для виходу.\n\n");
    
    for (int i = 0; i < 10; ++i) { // Обмежений цикл для прикладу
        int8_t rssi_433 = 0;
        int8_t rssi_24 = 0;
        
        if (radio_read_rssi(&radio_433, &rssi_433) == 0) {
            printf("[433 MHz] RSSI: %4d dBm", rssi_433);
            if (rssi_433 > -60) printf(" (Відмінний сигнал)\n");
            else if (rssi_433 > -80) printf(" (Хороший сигнал)\n");
            else printf(" (Слабкий сигнал)\n");
        } else {
            printf("[433 MHz] Помилка зчитування\n");
        }
        
        if (radio_read_rssi(&radio_24, &rssi_24) == 0) {
            printf("[2.4 GHz] RSSI: %4d dBm", rssi_24);
            if (rssi_24 > -65) printf(" (Відмінний сигнал)\n");
            else if (rssi_24 > -85) printf(" (Хороший сигнал)\n");
            else printf(" (Слабкий сигнал)\n");
        } else {
            printf("[2.4 GHz] Помилка зчитування\n");
        }
        
        printf("---\n");
        sleep(1); // Затримка 1 секунда між зчитуваннями
    }
    
    // Коректне завершення
    radio_close(&radio_433);
    radio_close(&radio_24);
    
    return 0;
}
