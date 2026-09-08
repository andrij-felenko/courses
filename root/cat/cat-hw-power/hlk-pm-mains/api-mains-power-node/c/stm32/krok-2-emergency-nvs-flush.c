/* ============================================================================
   krok-2-emergency-nvs-flush.c — STM32 HAL: аварійний скид навантаження та Flash
   ========================================================================== */

#include "stm32f4xx_hal.h"
#include <string_view>

#define RELAY_PIN       GPIO_PIN_1
#define RELAY_PORT      GPIOA
#define FLASH_USER_SECTOR_ADDR  0x080E0000  // Сектор 11 (Flash STM32F4)

typedef struct {
    uint32_t switch_count;
    uint32_t active_energy;
    uint32_t checksum;
} emergency_backup_t;

// Викликається негайно в перші 15 мс після зникнення змінного струму 220 В
void mains_emergency_shutdown(const emergency_backup_t *data) {
    // 1. Знеструмлюємо котушку реле для зменшення навантаження на HLK-PM
    HAL_GPIO_WritePin(RELAY_PORT, RELAY_PIN, GPIO_PIN_RESET);

    // 2. Зупиняємо периферію (таймери ШІМ, DMA, АЦП), зменшуючи споживання ядра
    HAL_TIM_Base_Stop_IT(&htim2);
    HAL_ADC_Stop(&hadc1);

    // 3. Екстрений запис у Flash-пам'ять до падіння VDD нижче порогу скиду BOR
    HAL_FLASH_Unlock();
    
    // Запис критичних слів
    uint32_t *src = (uint32_t *)data;
    uint32_t dst = FLASH_USER_SECTOR_ADDR;
    for (int i = 0; i < (sizeof(emergency_backup_t) / 4); i++) {
        HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, dst, src[i]);
        dst += 4;
    }
    
    HAL_FLASH_Lock();

    // 4. Переводимо мікроконтролер у режим Standby / Stop
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
}
