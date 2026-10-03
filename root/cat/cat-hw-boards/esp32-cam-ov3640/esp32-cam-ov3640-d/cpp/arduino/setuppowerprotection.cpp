#include "esp_camera.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

void setupPowerProtection() {
  Serial.begin(115200);
  
  // Діагностика причини скидання після стрибка струму
  esp_reset_reason_t reset_reason = esp_reset_reason();
  if (reset_reason == ESP_RST_BROWNOUT) {
    Serial.println("УВАГА: Виявлено перезавантаження через просідання напруги!");
  }

  // Конфігурація живлення перед ініціалізацією камери
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 1); // Увімкнення розширеного контролю живлення
}
