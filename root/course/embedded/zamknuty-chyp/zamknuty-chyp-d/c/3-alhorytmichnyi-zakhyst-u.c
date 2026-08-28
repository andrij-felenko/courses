// Захищена перевірка стану безпеки з подвійним комплементарним кодуванням на C
#include <stdint.h>
#include <stdbool.h>

#define SEC_STATE_LOCKED    0x5AA55AA5U
#define SEC_STATE_INV_LOCK  0xA55AA55AU

volatile uint32_t g_security_marker     = SEC_STATE_LOCKED;
volatile uint32_t g_security_marker_inv = SEC_STATE_INV_LOCK;

void tamper_safe_reaction(void);

bool verify_security_integrity(void) {
    // Подвійна перевірка значення та його бітового доповнення
    if ((g_security_marker != SEC_STATE_LOCKED) || 
        (g_security_marker_inv != SEC_STATE_INV_LOCK) ||
        ((g_security_marker ^ g_security_marker_inv) != 0xFFFFFFFFU)) {
        
        // Збій цілісності або успішний глітч: запускаємо захисну реакцію
        tamper_safe_reaction();
        return false;
    }
    return true;
}
