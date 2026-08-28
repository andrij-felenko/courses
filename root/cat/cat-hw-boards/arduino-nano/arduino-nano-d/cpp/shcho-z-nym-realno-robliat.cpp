// Класичний "blink": вбудований світлодіод на D13 моргає раз на секунду.
void setup() {
    pinMode(LED_BUILTIN, OUTPUT);   // LED_BUILTIN == 13 на Nano
}

void loop() {
    digitalWrite(LED_BUILTIN, HIGH);  // засвітити
    delay(500);                       // почекати 0.5 с
    digitalWrite(LED_BUILTIN, LOW);   // згасити
    delay(500);
}
