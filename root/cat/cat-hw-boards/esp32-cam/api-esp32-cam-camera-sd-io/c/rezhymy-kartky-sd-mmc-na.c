#include "SD_MMC.h"

static bool sdcard_start(void) {
    //                         точка монтування,  1-біт-режим
    if (!SD_MMC.begin("/sdcard", true)) {
        Serial.println("microSD не змонтувалася");
        return false;
    }
    // Перевіримо, що картка справді вставлена, а не «просто змонтувалося».
    uint8_t type = SD_MMC.cardType();
    if (type == CARD_NONE) {
        Serial.println("Картки в гнізді немає");
        return false;
    }
    return true;
}
