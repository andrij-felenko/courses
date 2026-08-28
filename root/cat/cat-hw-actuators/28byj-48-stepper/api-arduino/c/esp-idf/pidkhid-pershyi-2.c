static void release_coils(void) {
  for (int i = 0; i < 4; i++) gpio_set_level(PINS[i], 0);
}

void app_main(void) {
  stepper_init();
  while (1) {
    stepper_step(STEPS_PER_REV, 3000);
    release_coils();             // погасили обмотки — мотор охолов, струм не тече
    vTaskDelay(pdMS_TO_TICKS(2000));
  }
}
