const int PIN_EN = 9;    // EN (KEY) модуля → ця ніжка МК
const int PIN_BT_POWER = 8;  // керує живленням модуля (через транзистор), опційно

void enterATMode() {
    pinMode(PIN_EN, OUTPUT);
    digitalWrite(PIN_EN, HIGH);      // EN високо — ЩЕ ДО подачі живлення модулю
    // якщо живлення керується ніжкою — тут його вмикаємо ПІСЛЯ підняття EN:
    pinMode(PIN_BT_POWER, OUTPUT);
    digitalWrite(PIN_BT_POWER, LOW); // на мить знеструмити…
    delay(100);
    digitalWrite(PIN_BT_POWER, HIGH);// …і подати знову — модуль стартує вже в AT
    delay(500);                      // дати модулю прокинутись
    btSerial.begin(38400);           // КОМАНДНА швидкість HC-05, не 9600!
}
