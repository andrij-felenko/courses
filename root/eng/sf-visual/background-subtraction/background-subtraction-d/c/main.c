#include <arm_acle.h>
#include <stdint.h>

/* Паралельне віднімання 4 пікселів за 1 такт */
void subtract_simd_4px(const uint8_t *frame_ptr, const uint8_t *bg_ptr, 
                       uint8_t *mask_ptr, uint8_t threshold) {
    /* Завантажуємо 4 пікселі кадру та 4 пікселі фону в 32-бітні регістри */
    uint32_t f4 = *(const uint32_t *)frame_ptr;
    uint32_t b4 = *(const uint32_t *)bg_ptr;

    /* Беззнакове насичене віднімання: max(0, f - b) */
    uint32_t diff1 = __UQSUB8(f4, b4);
    /* Беззнакове насичене віднімання у зворотний бік: max(0, b - f) */
    uint32_t diff2 = __UQSUB8(b4, f4);
    /* Попіксельне АБО дає точний модуль різниці |f - b| */
    uint32_t abs_diff = diff1 | diff2;

    /* Порівняння з порогом для 4 пікселів */
    uint32_t thresh4 = (threshold << 24) | (threshold << 16) | (threshold << 8) | threshold;
    /* Якщо abs_diff >= thresh4, біти GE (Greater-Equal) встановлюються в регістрі APSR */
    __USUB8(abs_diff, thresh4);
    uint32_t mask4 = __SEL(0xFFFFFFFF, 0x00000000);

    *(uint32_t *)mask_ptr = mask4;
}
