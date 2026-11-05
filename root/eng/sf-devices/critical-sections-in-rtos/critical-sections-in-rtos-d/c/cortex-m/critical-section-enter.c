#include <stdint.h>
#include <stdbool.h>

/* Визначення порогу маскування BASEPRI (пріоритети 5-15 маскуються, 0-4 активні) */
#define SYSTEM_MAX_SYSCALL_PRIORITY 0x50

/* Бар'єр компілятора: запобігає перевпорядкуванню інструкцій оптимізатором */
#define COMPILER_BARRIER() __asm__ volatile ("" ::: "memory")

/* Апаратне маскування переривань із збереженням попереднього стану BASEPRI */
static inline uint32_t critical_section_enter(void) {
    uint32_t prev_basepri;
    
    COMPILER_BARRIER();
    
    /* Зчитування поточного значення регістра BASEPRI ядра ARM Cortex-M */
    __asm__ volatile ("mrs %0, basepri" : "=r" (prev_basepri));
    
    /* Запис нового порогу маскування переривань */
    __asm__ volatile ("msr basepri, %0" :: "r" (SYSTEM_MAX_SYSCALL_PRIORITY) : "memory");
    
    /* Апаратні бар'єри: очікування завершення шинних операцій та скидання конвеєра */
    __asm__ volatile ("dsb 0xF" ::: "memory");
    __asm__ volatile ("isb 0xF" ::: "memory");
    
    COMPILER_BARRIER();
    return prev_basepri;
}

/* Відновлення попереднього стану маски переривань */
static inline void critical_section_exit(uint32_t prev_basepri) {
    COMPILER_BARRIER();
    
    /* Гарантія завершення всіх попередніх операцій запису в пам'ять */
    __asm__ volatile ("dsb 0xF" ::: "memory");
    
    /* Відновлення збереженого стану регістра BASEPRI */
    __asm__ volatile ("msr basepri, %0" :: "r" (prev_basepri) : "memory");
    __asm__ volatile ("isb 0xF" ::: "memory");
    
    COMPILER_BARRIER();
}

/* Структура високочастотного вимірювального вузла */
typedef struct {
    int32_t raw_accelerometer[3];
    uint32_t timestamp_ticks;
    uint32_t sequence_id;
    bool is_valid;
} telemetry_payload_t;

static volatile telemetry_payload_t g_shared_telemetry;

/* Швидке отримання знімка даних без затримки високопріоритетних переривань */
bool telemetry_get_snapshot_fast(telemetry_payload_t *out_snapshot) {
    if (!out_snapshot) {
        return false;
    }

    /* Вхід у критичну секцію з локальним збереженням маски */
    uint32_t saved_mask = critical_section_enter();

    /* Мінімальне атомарне копіювання даних (триває кілька тактів) */
    out_snapshot->raw_accelerometer[0] = g_shared_telemetry.raw_accelerometer[0];
    out_snapshot->raw_accelerometer[1] = g_shared_telemetry.raw_accelerometer[1];
    out_snapshot->raw_accelerometer[2] = g_shared_telemetry.raw_accelerometer[2];
    out_snapshot->timestamp_ticks      = g_shared_telemetry.timestamp_ticks;
    out_snapshot->sequence_id          = g_shared_telemetry.sequence_id;
    out_snapshot->is_valid             = g_shared_telemetry.is_valid;

    /* Негайне відновлення переривань */
    critical_section_exit(saved_mask);

    /* Вся важка математична обробка, калібрування та перевірка виконується ПОЗА секцією */
    return out_snapshot->is_valid;
}

/* Оновлення даних з контексту переривання датчика */
void telemetry_update_from_isr(int32_t x, int32_t y, int32_t z, uint32_t ticks) {
    uint32_t saved_mask = critical_section_enter();

    g_shared_telemetry.raw_accelerometer[0] = x;
    g_shared_telemetry.raw_accelerometer[1] = y;
    g_shared_telemetry.raw_accelerometer[2] = z;
    g_shared_telemetry.timestamp_ticks = ticks;
    g_shared_telemetry.sequence_id++;
    g_shared_telemetry.is_valid = true;

    critical_section_exit(saved_mask);
}
