TouchButton btn(4, HIGH);   // SIG на D4, активний у 1 (заводський режим)

void setup() {
    btn.begin();
    pinMode(LED_BUILTIN, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    btn.update();                       // рушій драйвера, кожен прохід

    if (btn.pressed())  Serial.println("торкнулися");
    if (btn.released()) {
        Serial.print("відпустили, тримали (мс): ");
        Serial.println(btn.heldMs());   // скільки трималися — корисно для довгого натиску
    }
    digitalWrite(LED_BUILTIN, btn.held());   // світло, поки палець на пластинці

    // ... тут може крутитися будь-яка інша робота: драйвер нічого не блокує
}
