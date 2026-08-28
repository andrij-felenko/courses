// Той самий 74HC595, але байт жене апаратний SPI — швидко.
// DS(14)→MOSI (PA7), SHCP(11)→SCK (PA5), STCP(12)→PA4 (засувка вручну, NSS не вживаємо).
// SPI1 у CubeMX: Master, дані 8 біт, MSB First, CPOL=Low, CPHA=1 Edge — це режим 0.
extern SPI_HandleTypeDef hspi1;

#define LATCH_PORT GPIOA
#define LATCH_PIN  GPIO_PIN_4

static void WriteByte(uint8_t value) {
  HAL_GPIO_WritePin(LATCH_PORT, LATCH_PIN, GPIO_PIN_RESET);
  HAL_SPI_Transmit(&hspi1, &value, 1, HAL_MAX_DELAY);   // весь байт одним апаратним пострілом
  HAL_GPIO_WritePin(LATCH_PORT, LATCH_PIN, GPIO_PIN_SET);
}

int main(void) {
  HAL_Init();  SystemClock_Config();  MX_GPIO_Init();  MX_SPI1_Init();

  while (1) {
    WriteByte(0b10101010);   HAL_Delay(300);   // ввімкнули парні виходи
    WriteByte(0b01010101);   HAL_Delay(300);   // непарні
  }
}
