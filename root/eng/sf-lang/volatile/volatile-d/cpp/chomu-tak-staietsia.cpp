volatile bool pressed = false;        // спільна з ISR → volatile

void IRAM_ATTR onButton() {           // обробник переривання GPIO
    pressed = true;                   // запис у пам'ять
}

void waitForPress() {
    pressed = false;
    while (!pressed) {                // чекаємо натискання
        // компілятор бачить: усередині циклу pressed ніхто не пише
    }
}
