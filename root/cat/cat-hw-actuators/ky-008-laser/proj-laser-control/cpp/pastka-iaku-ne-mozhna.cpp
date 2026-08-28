// Лазер через npn-ключ: GPIO лише керує базою, струм діода йде повз вивід
//
//   5V ──[ модуль KY-008: + і S на живлення/резистор+діод ]── колектор
//   GPIO ──[ 1 кОм ]── база npn (2N2222/BC337)
//   емітер ── GND
//
// (для варіанта Б: S модуля -> колектор ключа, а не прямо на GPIO)

const uint8_t LASER_GATE = 4;   // GPIO -> резистор -> база транзистора

void setup() {
    pinMode(LASER_GATE, OUTPUT);
    digitalWrite(LASER_GATE, LOW);   // база закрита -> лазер темний
}

void laserOn()  { digitalWrite(LASER_GATE, HIGH); } // відмикаємо базу -> струм тече
void laserOff() { digitalWrite(LASER_GATE, LOW);  }
