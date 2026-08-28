#include <stdint.h>

// Отримання індексу символу з поля r_info
#define ELF64_R_SYM(i)    ((uint32_t)((i) >> 32))

// Отримання типу релокації з поля r_info
#define ELF64_R_TYPE(i)   ((uint32_t)((i) & 0xffffffffL))

// Утворення значення r_info з індексу символу s та типу t
#define ELF64_R_INFO(s,t) ((((uint64_t)(s)) << 32) + ((uint32_t)(t)))
