#include "emergency_fw_header.h"

/* Функція верифікації лічильника та спалювання eFuse після валідації */
bool commit_emergency_security_version(const emergency_fw_header_t *header) {
    if (!header) {
        return false;
    }

    uint32_t hardware_efuse_ver = hw_efuse_read_security_version();
    
    /* Якщо прошивка має менший лічильник, запуск суворо заборонено */
    if (header->security_counter < hardware_efuse_ver) {
        return false;
    }

    /* Якщо лічильник образу вищий, виконуємо одноразове апаратне спалювання */
    if (header->security_counter > hardware_efuse_ver) {
        if (!hw_efuse_burn_security_version(header->security_counter)) {
            /* Помилка програмування OTP є критичною відмовою безпеки */
            return false;
        }
    }

    return true;
}
