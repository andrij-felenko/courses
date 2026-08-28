#include "cmsis_gcc.h"   // SCB_CleanDCache_by_Addr / SCB_InvalidateDCache_by_Addr

// Продюсер: заповнив слот у кешованій DPRAM — і мусить вигнати його в пам'ять,
// ІНАКШЕ сусід прочитає з реальної пам'яті старе сміття.
static inline void publish_slot(slot_t volatile *s)
{
    SCB_CleanDCache_by_Addr((uint32_t *)s, sizeof(slot_t));  // моя копія → пам'ять
}

// Споживач: перш ніж читати слот, викинути свою копію лінії,
// щоб читання пішло в пам'ять і дістало те, що сусід щойно записав.
static inline void refresh_slot(slot_t volatile *s)
{
    SCB_InvalidateDCache_by_Addr((uint32_t *)s, sizeof(slot_t));  // з пам'яті наново
}
