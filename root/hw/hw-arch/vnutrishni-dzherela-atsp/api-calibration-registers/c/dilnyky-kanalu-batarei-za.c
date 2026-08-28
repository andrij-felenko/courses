/* Коефіцієнти внутрішнього дільника VBAT для різних архітектур */
#if defined(STM32F4) || defined(STM32F2)
    #define MCU_VBAT_DIVIDER_RATIO      (2U)  /* Дільник 1/2: V_ADC = VBAT / 2 */
#elif defined(STM32G0) || defined(STM32G4) || defined(STM32L4) || defined(STM32WB)
    #define MCU_VBAT_DIVIDER_RATIO      (3U)  /* Дільник 1/3: V_ADC = VBAT / 3 */
#elif defined(STM32H7) || defined(STM32H5) || defined(STM32U5)
    #define MCU_VBAT_DIVIDER_RATIO      (4U)  /* Дільник 1/4: V_ADC = VBAT / 4 */
#else
    #define MCU_VBAT_DIVIDER_RATIO      (3U)  /* За замовчуванням для сучасних MCU */
#endif
