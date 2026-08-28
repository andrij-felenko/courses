void setup() {
    pinMode(PIN_DIN,  OUTPUT);
    pinMode(PIN_CLK,  OUTPUT);
    pinMode(PIN_LOAD, OUTPUT);
    max7219init();
    drawSmiley();
    max7219show();     // надіслали кадр — і він стоїть сам, чип його розгортає
}

void loop() {
    // Нічого крутити не треба: MAX7219 сам тримає й розгортає картинку.
    // Щоб змінити зображення — перепиши frame[] і виклич max7219show() ще раз.
}
