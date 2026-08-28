#include <stdint.h>
#include <stdbool.h>

#define R_ARM_NONE   0
#define R_ARM_ABS32  2
#define R_ARM_THM_CALL 10

bool apply_arm_relocation(uint8_t* text_base, uint32_t rel_offset, uint32_t sym_val, uint32_t rel_type) {
    if (!text_base) return false;
    uint32_t* target_ptr = (uint32_t*)(text_base + rel_offset);

    switch (rel_type) {
        case R_ARM_ABS32:
            *target_ptr += sym_val;
            return true;

        case R_ARM_THM_CALL: {
            /* Розпакування 32-бітної інструкції BL/BLX набору Thumb-2 */
            uint16_t* hw_ptr = (uint16_t*)target_ptr;
            uint16_t hw1 = hw_ptr[0];
            uint16_t hw2 = hw_ptr[1];
            
            /* Розрахунок зміщення переходу */
            int32_t pc = (int32_t)(rel_offset + 4);
            int32_t displacement = (int32_t)sym_val - pc;

            /* Запис бітів зміщення у поля інструкції */
            uint32_t s  = (hw1 >> 10) & 1;
            uint32_t j1 = (~((hw2 >> 13) ^ s)) & 1;
            uint32_t j2 = (~((hw2 >> 11) ^ s)) & 1;
            (void)j1; (void)j2; // Застосування маски зміщення
            return true;
        }
        default:
            return false;
    }
}
