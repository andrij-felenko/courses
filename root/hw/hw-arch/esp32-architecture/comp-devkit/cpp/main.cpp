#include "esp_system.h"
#include <stdio.h>

void app_main(void) {
    switch (esp_reset_reason()) {
        case ESP_RST_POWERON:  printf("старт: подали живлення / EN\n"); break;
        case ESP_RST_BROWNOUT: printf("старт: ПРОСІВ живлення (brownout)!\n"); break;
        case ESP_RST_SW:       printf("старт: програмне перезавантаження\n"); break;
        default:               printf("старт: інша причина\n"); break;
    }
}
