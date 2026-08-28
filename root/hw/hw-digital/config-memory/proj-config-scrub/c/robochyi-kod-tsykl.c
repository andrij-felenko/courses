#include <stdint.h>
#include <stdbool.h>

// Скільки 32-бітних слів в одному кадрі конфігурації (залежить від чипа;
// у сучасних FPGA — кількадесят слів + кілька слів на ECC/вирівнювання).
#define FRAME_WORDS      101u

// Скільки всього кадрів у конфігураційній пам'яті цього пристрою.
// Реально — багато тисяч; тут число умовне для прикладу.
#define FRAME_COUNT      25000u

// ── Драйвер порту конфігурації (реалізується під конкретний чип) ────────────
// Нижчий шар: керує внутрішнім портом доступу до конфігурації.
extern void     cfg_read_frame (uint32_t frame_addr, uint32_t *dst); // зчитати кадр назад
extern void     cfg_write_frame(uint32_t frame_addr, const uint32_t *src); // переписати кадр
extern uint16_t cfg_frame_ecc  (uint32_t frame_addr); // синдром ECC цього кадру від апаратури
extern uint32_t cfg_global_crc (void);                // поточний глобальний CRC усієї памʼяті
