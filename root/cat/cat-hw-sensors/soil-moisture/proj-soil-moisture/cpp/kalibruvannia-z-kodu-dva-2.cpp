#include <EEPROM.h>

const uint8_t BTN = 3;            // кнопка калібрування (інша нога — на GND)
int rawDry = 730, rawWet = 300;

void saveCalib() {                // кладемо обидва краї в EEPROM
    EEPROM.put(0, rawDry);
    EEPROM.put(sizeof(rawDry), rawWet);
}
void loadCalib() {                // дістаємо при старті
    EEPROM.get(0, rawDry);
    EEPROM.get(sizeof(rawDry), rawWet);
    if (rawDry <= rawWet) { rawDry = 730; rawWet = 300; }  // порожня EEPROM → дефолти
}

// у setup(): loadCalib();  pinMode(BTN, INPUT_PULLUP);
// у loop(), коли натиснуто кнопку і щуп у повітрі:
//   rawDry = median9(); saveCalib();
// коли натиснуто і щуп у воді:
//   rawWet = median9(); saveCalib();
