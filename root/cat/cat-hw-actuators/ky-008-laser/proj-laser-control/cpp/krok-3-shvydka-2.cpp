// ESP32: несуча 38 кГц робиться апаратно (LEDC), процесор вільний
const uint8_t  LASER    = 4;
const uint32_t CARRIER  = 38000;   // Гц
const uint8_t  RES_BITS = 8;       // 8-бітна роздільність шпаруватості

void carrierBegin() {
    ledcAttach(LASER, CARRIER, RES_BITS);   // core 3.x: пін, частота, біти
    ledcWrite(LASER, 0);                     // 0 = несучої нема (промінь темний)
}

void carrierMark()  { ledcWrite(LASER, 128); }  // ~50% -> несуча в ефірі («мітка»)
void carrierSpace() { ledcWrite(LASER, 0);   }   // 0% -> тиша («пауза»)
