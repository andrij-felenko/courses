#include "main.h"

extern I2C_HandleTypeDef hi2c1;

#define PCA_ADDR      (0x40 << 1)  // HAL чекає 8-бітну адресу — 7-бітну зсуваємо
#define REG_MODE1     0x00
#define REG_PRESCALE  0xFE
#define REG_LED0_ON_L 0x06         // далі — по 4 регістри на канал

static void pca_write(uint8_t reg, uint8_t val) {
  HAL_I2C_Mem_Write(&hi2c1, PCA_ADDR, reg, I2C_MEMADD_SIZE_8BIT, &val, 1, 100);
}

static void pca_set_freq(int hz) {
  // дільник = round(25 МГц / (4096 · f)) − 1; для 50 Гц це 121
  uint8_t prescale = (uint8_t)(25000000.0 / (4096.0 * hz) + 0.5) - 1;
  pca_write(REG_MODE1, 0x10);      // SLEEP: дільник міняють лише зі сплячим генератором
  pca_write(REG_PRESCALE, prescale);
  pca_write(REG_MODE1, 0x00);      // прокинутись
  HAL_Delay(1);                    // ≥500 мкс на розгін генератора
  pca_write(REG_MODE1, 0xA0);      // RESTART + автоінкремент регістрів
}

static void servo_us(uint8_t ch, int us) {
  if (us < 1000) us = 1000;                        // тримаємось безпечних меж SG90
  if (us > 2000) us = 2000;
  uint16_t off = (uint16_t)(us * 4096 / 20000);    // ≈ 4.88 мкс на крок
  uint8_t p[4] = { 0, 0, off & 0xFF, off >> 8 };   // ON_L, ON_H, OFF_L, OFF_H
  HAL_I2C_Mem_Write(&hi2c1, PCA_ADDR, REG_LED0_ON_L + 4 * ch,
                    I2C_MEMADD_SIZE_8BIT, p, 4, 100);   // автоінкремент допише решту
}

int main(void) {
  HAL_Init(); SystemClock_Config();
  MX_GPIO_Init(); MX_I2C1_Init();

  pca_set_freq(50);                // 50 Гц на ВСІ 16 каналів одразу
  servo_us(0, 1500); servo_us(1, 1500); servo_us(2, 1500);   // три серва по нейтралі

  while (1) {                      // махнути каналом 0, решта стоять
    servo_us(0, 1000); HAL_Delay(800);
    servo_us(0, 2000); HAL_Delay(800);
  }
}
