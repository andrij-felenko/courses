const uint8_t REED   = 2;        // D0 давача
const int     ACTIVE = LOW;      // ← активний рівень вашої плати (з розвідки)

const uint32_t DEBOUNCE_MS = 30; // «мертвий час» після краю: коротший сплеск — брязкіт

uint32_t counter   = 0;          // накопичені події
bool     was_near  = false;      // попередній стан геркона (для виявлення краю)
uint32_t t_edge    = 0;          // коли востаннє прийняли зміну стану

void setup() {
    pinMode(REED, INPUT);
    Serial.begin(9600);
    was_near = (digitalRead(REED) == ACTIVE);
    Serial.println("Лічильник геркона готовий.");
}

void loop() {
    bool near = (digitalRead(REED) == ACTIVE);
    uint32_t now = millis();

    // Реагуємо лише на ЗМІНУ стану і лише якщо від минулої зміни минув мертвий час.
    if (near != was_near && (now - t_edge) >= DEBOUNCE_MS) {
        t_edge   = now;
        was_near = near;

        if (near) {                       // край саме «нема → є» — це нова подія
            counter++;
            Serial.print("клац! всього: ");
            Serial.println(counter);
        }
    }
}
