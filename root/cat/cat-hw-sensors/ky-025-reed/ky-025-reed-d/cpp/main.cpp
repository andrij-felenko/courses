const uint8_t REED = 2;    // D0 давача
const uint8_t LED  = 13;   // вбудований світлодіод

bool wasNear = false;      // попередній стан, щоб ловити саме перехід

void setup() {
    pinMode(REED, INPUT);  // на платі вже є підтяжка Rp — зовнішня не потрібна
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    // магніт дає низький рівень → інвертуємо, щоб near=true означало «магніт поруч»
    bool near = (digitalRead(REED) == LOW);

    digitalWrite(LED, near ? HIGH : LOW);

    if (near && !wasNear) Serial.println("магніт піднесено");
    if (!near && wasNear) Serial.println("магніт прибрано");
    wasNear = near;

    delay(20);            // грубе згладжування деренчання контакту
}
