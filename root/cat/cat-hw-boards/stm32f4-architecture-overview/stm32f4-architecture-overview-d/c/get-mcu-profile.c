// C: Перевірка можливостей обраної моделі STM32F4 та вибір відповідних областей пам'яті
#include "stm32f4xx.h"
#include <stdbool.h>

typedef struct {
    uint32_t sample_buffer_size;
    bool has_ccm_support;
    bool has_sdram_support;
} McuCapabilityProfile;

McuCapabilityProfile get_mcu_profile(void) {
    McuCapabilityProfile profile = {0};
    profile.sample_buffer_size = 1024;

#if defined(STM32F407xx) || defined(STM32F429xx)
    // Кристали F407/F429 мають пам'ять CCM SRAM за адресою 0x10000000
    profile.has_ccm_support = true;
#else
    profile.has_ccm_support = false;
#endif

#if defined(STM32F429xx) || defined(STM32F469xx)
    // Графічні серії F429/F469 підтримують зовнішню SDRAM через FMC
    profile.has_sdram_support = true;
#else
    profile.has_sdram_support = false;
#endif

    return profile;
}
