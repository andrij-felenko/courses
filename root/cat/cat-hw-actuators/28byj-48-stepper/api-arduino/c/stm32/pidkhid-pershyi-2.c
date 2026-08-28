static void release_coils(void) {
  for (int i = 0; i < 4; i++)
    HAL_GPIO_WritePin(IN[i].port, IN[i].pin, GPIO_PIN_RESET);
}

int main(void) {
  HAL_Init(); SystemClock_Config(); MX_GPIO_Init();
  while (1) {
    stepper_step(STEPS_PER_REV, 3);
    release_coils();             // погасили обмотки — мотор охолов, струм не тече
    HAL_Delay(2000);
  }
}
