void keypad_begin(void)
{
    // Рядки — входи з ВНУТРІШНЬОЮ підтяжкою: спокій = HIGH, натиск потягне в LOW.
    for (uint8_t i = 0; i < 4; i++)
        pinMode(ROW_PIN[i], INPUT_PULLUP);

    // Стовпці — виходи, і в СПОКОЇ тримаємо їх HIGH (неактивні).
    // Активним стовпець стане лише на мить свого скану (виставимо LOW).
    for (uint8_t j = 0; j < 4; j++) {
        pinMode(COL_PIN[j], OUTPUT);
        digitalWrite(COL_PIN[j], HIGH);   // неактивний стовпець = HIGH
    }
}
