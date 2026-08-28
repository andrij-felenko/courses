// Нижній ключ: затвор жене драйвер із роздільними входами ON/OFF.
// R_off_fast — малий резистор вимкнення (різкий фронт);
// R_off_slow — більший, увімкнений паралельно ключем GPIO для м'якого фронту.
// Прошивка лише ОБИРАЄ передачу; саме гасіння робить апаратний кламп.

#define GATE_ON_PORT    GPIOA
#define GATE_ON_PIN     GPIO_PIN_8     // вхід драйвера «ввімкнути»
#define GATE_OFF_PORT   GPIOA
#define GATE_OFF_PIN    GPIO_PIN_9     // вхід драйвера «вимкнути»
#define ROFF_SEL_PORT   GPIOB
#define ROFF_SEL_PIN    GPIO_PIN_0     // 0 = лише R_off_fast; 1 = + R_off_slow

typedef enum { EDGE_FAST, EDGE_SOFT } edge_mode_t;

static void gate_set_edge(edge_mode_t m) {
    // R_off_slow підмикаємо ДО того, як даємо команду вимкнення,
    // інакше зміна передачі посеред фронту дасть стрибок.
    HAL_GPIO_WritePin(ROFF_SEL_PORT, ROFF_SEL_PIN,
                      (m == EDGE_SOFT) ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

static void gate_on(void) {
    HAL_GPIO_WritePin(GATE_OFF_PORT, GATE_OFF_PIN, GPIO_PIN_RESET); // зняти OFF
    HAL_GPIO_WritePin(GATE_ON_PORT,  GATE_ON_PIN,  GPIO_PIN_SET);   // дати ON
}

static void gate_off(edge_mode_t m) {
    gate_set_edge(m);                                               // обрати передачу
    HAL_GPIO_WritePin(GATE_ON_PORT,  GATE_ON_PIN,  GPIO_PIN_RESET); // зняти ON
    HAL_GPIO_WritePin(GATE_OFF_PORT, GATE_OFF_PIN, GPIO_PIN_SET);   // дати OFF
}
