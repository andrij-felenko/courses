const uint8_t  SOL_PIN     = 5;
const uint32_t MAX_ON_MS   = 3000;   // ГРАНИЦЯ: довше 3 с під струмом не тримаємо НІКОЛИ

bool     solOn    = false;
uint32_t solStart = 0;

void solenoidOn() {                  // «тримати ввімкненим» (напр. утримувати засувку)
    if (!solOn) {                    // фіксуємо мить старту лише на першому вмиканні
        digitalWrite(SOL_PIN, HIGH);
        solStart = millis();
        solOn    = true;
    }
}

void solenoidOff() {
    digitalWrite(SOL_PIN, LOW);
    solOn = false;
}

void solenoidUpdate() {              // страхувальник: рубає струм, якщо тримають задовго
    if (solOn && (millis() - solStart >= MAX_ON_MS)) {
        solenoidOff();               // стеля вичерпана — гасимо примусово
        // тут доречно підняти прапорець помилки / моргнути світлодіодом:
        // хтось тримає соленоїд надто довго — це майже завжди баг логіки
    }
}
