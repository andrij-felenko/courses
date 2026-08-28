#include <stdio.h>
#include <string.h>

extern ADC_HandleTypeDef  hadc1;
extern UART_HandleTypeDef huart2;

static light_sensor_t sensor;

static void say(const char *s) {
  HAL_UART_Transmit(&huart2, (uint8_t *)s, strlen(s), HAL_MAX_DELAY);
}

int main(void) {
  HAL_Init();  SystemClock_Config();
  MX_GPIO_Init();  MX_ADC1_Init();  MX_USART2_UART_Init();

  light_begin(&sensor, &hadc1, 4095, 0.2f, 30, 45);   // 12-бітний АЦП
  say("Калібрування: 5 с крутіть освітлення...\r\n");
  light_calibrate(&sensor, 5);

  char line[48];
  for (;;) {
    light_update(&sensor);              // оновити фільтр
    uint8_t pct = light_percent(&sensor);
    bool dark = light_is_dark(&sensor);
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin,       // світлодіод плати в темряві
                      dark ? GPIO_PIN_SET : GPIO_PIN_RESET);
    snprintf(line, sizeof line, "яскравість %u %%  %s\r\n", pct, dark ? "ТЕМНО" : "світло");
    say(line);
    HAL_Delay(50);
  }
}
