/* TIM3_CH1 у режимі PWM, налаштований так, щоб один тік лічильника = 1 мкс,
   а період = 20 000 тіків: Prescaler = f_таймера/1 МГц − 1, ARR = 20000 − 1.
   Тоді регістр порівняння CCR1 і є ширина імпульсу в мікросекундах. */
#include "main.h"

extern TIM_HandleTypeDef htim3;

static void servo_write_us(uint16_t us) {
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, us);   // CCR1 = мкс напряму
}

static void servo_write_deg(int deg) {                // градусів у залізі нема
  servo_write_us(1000 + deg * (2000 - 1000) / 180);
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_TIM3_Init();
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);           // пустити генерацію 50 Гц

  while (1) {
    servo_write_deg(0);   HAL_Delay(1000);            // одне крайнє
    servo_write_deg(90);  HAL_Delay(1000);            // нейтраль
    servo_write_deg(180); HAL_Delay(1000);            // інше крайнє
  }
}
