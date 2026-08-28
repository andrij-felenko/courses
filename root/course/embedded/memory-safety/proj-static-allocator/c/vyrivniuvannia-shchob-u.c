#include <stdalign.h>

// Найсуворіше вирівнювання, потрібне будь-якому скалярному типу на платформі.
// max_align_t гарантує, що в блок можна безпечно покласти що завгодно.
#define POOL_ALIGN   (alignof(max_align_t))

// Округлення розміру вгору до кратного вирівнюванню (a — степінь двійки).
#define ALIGN_UP(x, a)  (((x) + ((a) - 1)) & ~((size_t)(a) - 1))

#define POOL_BLOCKS    32
#define POOL_USER_SZ   64                                  // що просить користувач
#define POOL_BLOCK_SZ  ALIGN_UP(POOL_USER_SZ, POOL_ALIGN)  // реальний розмір блоку

// alignas на масиві → вирівняний початок; кратний розмір → вирівняні всі блоки.
static alignas(POOL_ALIGN) uint8_t pool_mem[POOL_BLOCKS][POOL_BLOCK_SZ];
