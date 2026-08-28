/*
 * Реалізація на Arduino (з використанням прямих регістрів таймера та АЦП)
 * Демонстрація апаратного запуску на платах з ядром SAMD21 / STM32
 */

#define SAMPLE_RATE_HZ 50000
#define BUFFER_SIZE    512

volatile uint16_t adc_buffer[BUFFER_SIZE];
volatile bool buffer_ready = false;

void setupHardwareTimerTrigger() {
    /* 
     * Пряме конфігурування апаратного таймера та АЦП без використання повільного analogRead()
     * Таймер генерує строб вибірки безпосередньо в логіку АЦП через систему подій EVSYS.
     */
#if defined(ARDUINO_ARCH_SAMD)
    PM->APBCMASK.reg |= PM_APBCMASK_EVSYS | PM_APBCMASK_ADC | PM_APBCMASK_TC5;
    
    // Комутація виходу TC5 на подію старту АЦП
    EVSYS->USER.reg = EVSYS_USER_CHANNEL(1) | EVSYS_USER_USER(EVSYS_ID_USER_ADC_START);
    EVSYS->CHANNEL.reg = EVSYS_CHANNEL_CHANNEL(0) | EVSYS_CHANNEL_PATH_SYNCHRONOUS | EVSYS_CHANNEL_EVGEN(EVSYS_ID_GEN_TC5_OVF);

    // Увімкнення апаратного тригера в АЦП
    ADC->EVCTRL.reg |= ADC_EVCTRL_STARTEI;
#endif
}

void setup() {
    Serial.begin(115200);
    setupHardwareTimerTrigger();
}

void loop() {
    if (buffer_ready) {
        buffer_ready = false;
        // Обробка блоку відліків без програмного тремтіння тактування
    }
}
