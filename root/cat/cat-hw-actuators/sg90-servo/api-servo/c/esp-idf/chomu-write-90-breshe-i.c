// LEDC знає лише кроки лічильника, тож servo_write_us() з попереднього
// прикладу — і є весь «прямий» рівень: жодних кутів між вами й імпульсом.
void app_main(void) {
  servo_init();
  while (1) {
    servo_write_us(1000);   vTaskDelay(pdMS_TO_TICKS(1000));  // одне крайнє
    servo_write_us(1500);   vTaskDelay(pdMS_TO_TICKS(1000));  // справжня нейтраль
    servo_write_us(2000);   vTaskDelay(pdMS_TO_TICKS(1000));  // інше крайнє
  }
}
