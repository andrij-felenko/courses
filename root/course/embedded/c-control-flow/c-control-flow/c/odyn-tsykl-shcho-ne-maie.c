int main(void) {
    hardware_init();               // один раз: тактування, GPIO, периферія

    while (1) {                    // 1 — завжди істина, тож це «крутитися вічно»
        int temp = read_temp();    // зчитати входи
        if (temp > LIMIT) {        // вирішити
            fan_on();              // подіяти
        } else {
            fan_off();
        }
    }
    // сюди виконання не доходить ніколи
}
