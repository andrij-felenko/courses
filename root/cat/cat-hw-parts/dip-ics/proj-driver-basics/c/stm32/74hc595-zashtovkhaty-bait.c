// 74HC595: виставляємо один байт на 8 виходів, зсуваючи біти вручну.
// DS(14)→PA5, SHCP(11)→PA6, STCP(12)→PA7 — усі три як GPIO_Output push-pull.
// OE(13)→GND, MR(10)→+3V3, Vcc(16)→+3V3, GND(8)→спільна.
#define SR_PORT  GPIOA
#define DATA     GPIO_PIN_5    // → DS
#define CLOCK    GPIO_PIN_6    // → SHCP
#define LATCH    GPIO_PIN_7    // → STCP

static void ShiftOut(uint8_t value) {            // зі старшого біта
  for (int i = 7; i >= 0; i--) {
    HAL_GPIO_WritePin(SR_PORT, DATA,
                      ((value >> i) & 1) ? GPIO_PIN_SET : GPIO_PIN_RESET);   // виставили біт
    HAL_GPIO_WritePin(SR_PORT, CLOCK, GPIO_PIN_SET);      // клацнули такт
    HAL_GPIO_WritePin(SR_PORT, CLOCK, GPIO_PIN_RESET);
  }
}

static void WriteByte(uint8_t value) {
  HAL_GPIO_WritePin(SR_PORT, LATCH, GPIO_PIN_RESET);      // закриваємо засувку
  ShiftOut(value);                                        // 8 тактів: заштовхали 8 бітів
  HAL_GPIO_WritePin(SR_PORT, LATCH, GPIO_PIN_SET);        // фронт засувки → усі 8 виходів разом
}

int main(void) {
  HAL_Init();  SystemClock_Config();  MX_GPIO_Init();

  while (1) {
    // «біжуча одиниця»: по черзі запалюємо кожен вихід
    for (int i = 0; i < 8; i++) {
      WriteByte(1 << i);
      HAL_Delay(120);
    }
  }
}
