#include "radio_rssi.h"
#include <stdlib.h>
#include <time.h>

bool radio_init(radio_module_t* radio, radio_frequency_t freq, int hw_id) {
    if (!radio) return false;
    
    // Імітація ініціалізації апаратного забезпечення
    radio->freq = freq;
    radio->hardware_id = hw_id;
    radio->initialized = true;
    
    // Для імітації випадкового RSSI
    srand((unsigned int)time(NULL) ^ hw_id);
    
    return true;
}

int radio_read_rssi(const radio_module_t* radio, int8_t* rssi_out) {
    if (!radio || !radio->initialized || !rssi_out) {
        return -1; // Помилка: невірні параметри або не ініціалізовано
    }
    
    // Імітація зчитування RSSI через SPI/I2C/UART
    // Зазвичай RSSI вимірюється у від'ємних значеннях (від -100 до -30 дБм)
    // 433 МГц часто пробиває далі (менше згасання), 2.4 ГГц швидше згасає
    
    int base_rssi = (radio->freq == FREQ_433_MHZ) ? -65 : -75;
    
    // Додаємо трохи шуму для реалістичності
    int noise = (rand() % 15) - 7;
    
    *rssi_out = (int8_t)(base_rssi + noise);
    
    return 0; // Успіх
}

void radio_close(radio_module_t* radio) {
    if (radio) {
        // Імітація вимкнення та звільнення ресурсів
        radio->initialized = false;
    }
}
