const uint8_t ROWS = 4, COLS = 4;
const uint8_t rowPin[ROWS] = {9, 8, 7, 6};   // R1..R4
const uint8_t colPin[COLS] = {5, 4, 3, 2};   // C1..C4

// що надруковано на клавіатурі: [рядок][стовпець]
const char keymap[ROWS][COLS] = {
    {'1','2','3','A'},
    {'4','5','6','B'},
    {'7','8','9','C'},
    {'*','0','#','D'}
};

void setup() {
    for (uint8_t r = 0; r < ROWS; r++)
        pinMode(rowPin[r], INPUT_PULLUP);    // рядки: у спокої «1»
    for (uint8_t c = 0; c < COLS; c++)
        pinMode(colPin[c], INPUT);           // стовпці поки відпущені у вхід (Z)
    Serial.begin(9600);
}

char scanOnce() {
    for (uint8_t c = 0; c < COLS; c++) {
        pinMode(colPin[c], OUTPUT);          // цей стовпець беремо виходом
        digitalWrite(colPin[c], LOW);        // і жену його в «0»
        for (uint8_t r = 0; r < ROWS; r++) {
            if (digitalRead(rowPin[r]) == LOW) {   // рядок упав → тут клавіша
                pinMode(colPin[c], INPUT);   // повертаємо стовпець у Z
                return keymap[r][c];
            }
        }
        pinMode(colPin[c], INPUT);           // не знайшли — відпускаємо назад у Z
    }
    return 0;                                 // нічого не натиснуто
}

void loop() {
    static char prev = 0;
    char k = scanOnce();
    if (k && k != prev) {                     // ловимо МОМЕНТ натискання, не утримання
        Serial.print("клавіша: ");
        Serial.println(k);
    }
    prev = k;
    delay(20);                                // грубий антидеренч + не молотимо марно
}
