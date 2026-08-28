// 74HC595 → ULN2003: регістр адресує канали, масив тягне їхній струм.
// Q0..Q6 регістра → IN1..IN7 масиву. COM(9) масиву → +V навантаження.
// Кожен «1» у байті → відповідний вихід ULN2003 стягує своє навантаження в −.
static void SetChannels(uint8_t mask) {    // біт i маски → канал (i+1) масиву
  HAL_GPIO_WritePin(SR_PORT, LATCH, GPIO_PIN_RESET);
  ShiftOut(mask);
  HAL_GPIO_WritePin(SR_PORT, LATCH, GPIO_PIN_SET);
}

int main(void) {
  HAL_Init();  SystemClock_Config();  MX_GPIO_Init();

  while (1) {
    SetChannels(0b00000011);  HAL_Delay(1000);   // канали 1 і 2 (напр. два реле)
    SetChannels(0b01001000);  HAL_Delay(1000);   // канали 4 і 7
    SetChannels(0b00000000);  HAL_Delay(1000);   // усе вимкнули
  }
}
