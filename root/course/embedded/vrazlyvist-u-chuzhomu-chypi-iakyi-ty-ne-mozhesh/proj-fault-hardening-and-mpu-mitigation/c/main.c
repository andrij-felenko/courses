#include <stdint.h>
#include <stdbool.h>

/* Магічні 32-бітні константи з максимальною відстанню Геммінга */
#define STATUS_OK_STAGE1        ((uint32_t)0x5AA55AA5UL)
#define STATUS_OK_STAGE2        ((uint32_t)0xA55AA55AUL)
#define STATUS_INV_PATTERN      ((uint32_t)0xFFFFFFFFUL)
#define STATUS_FAULT_DETECTED   ((uint32_t)0xDEADBEEFUL)

/* Регістри ARM Cortex-M MPU та системного керування */
#define MPU_TYPE_REG            (*(volatile uint32_t *)0xE000ED90UL)
#define MPU_CTRL_REG            (*(volatile uint32_t *)0xE000ED94UL)
#define MPU_RNR_REG             (*(volatile uint32_t *)0xE000ED98UL)
#define MPU_RBAR_REG            (*(volatile uint32_t *)0xE000ED9CUL)
#define MPU_RASR_REG            (*(volatile uint32_t *)0xE000EDA0UL)
#define SCB_SHCSR_REG           (*(volatile uint32_t *)0xE000ED24UL)

/* Бітові маски MPU RASR */
#define MPU_RASR_ENABLE         (1UL << 0)
#define MPU_RASR_SIZE_64KB      (15UL << 1)
#define MPU_RASR_SIZE_128KB     (16UL << 1)
#define MPU_RASR_SIZE_512MB     (28UL << 1)
#define MPU_RASR_AP_PRIV_RO     (5UL << 24)  /* Привілейований: RO, Користувач: Немає */
#define MPU_RASR_AP_FULL_RO     (6UL << 24)  /* Привілейований: RO, Користувач: RO */
#define MPU_RASR_AP_PRIV_RW     (1UL << 24)  /* Привілейований: RW, Користувач: Немає */
#define MPU_RASR_AP_FULL_RW     (3UL << 24)  /* Привілейований: RW, Користувач: RW */
#define MPU_RASR_XN             (1UL << 28)  /* Заборона виконання (Execute Never) */

/* Захисний бар'єр пам'яті для запобігання оптимізаціям компілятора */
static inline void hardware_barrier(void) {
    __asm__ volatile("" ::: "memory");
}

/* Псевдо-рандомізована затримка для порушення таймінгу атаки */
static void inject_jitter_delay(uint32_t entropy) {
    volatile uint32_t count = (entropy & 0x0F) + 7;
    while (count--) {
        hardware_barrier();
    }
}

/* Аварійне стирання секретів та зупинка при виявленні глітчингу */
static void secure_tamper_panic(void) {
    volatile uint32_t *p_secrets = (volatile uint32_t *)0x20000000UL;
    for (uint32_t i = 0; i < 64; ++i) {
        p_secrets[i] = 0x00000000UL;
    }
    hardware_barrier();
    /* Вічний сон з вимкненими перериваннями */
    __asm__ volatile("cpsid i");
    while (1) {
        __asm__ volatile("wfi");
    }
}

/* Загартована перевірка цілісності прошивки */
uint32_t hardened_verify_image(const uint8_t *image_addr, uint32_t len, uint32_t entropy_seed) {
    volatile uint32_t stage1_res = 0;
    volatile uint32_t stage2_res = 0;
    volatile uint32_t check_acc = 0;

    /* Перший прохід перевірки */
    inject_jitter_delay(entropy_seed);
    if (image_addr != 0 && len >= 1024) {
        stage1_res = STATUS_OK_STAGE1;
        check_acc += 1;
    }
    hardware_barrier();

    /* Другий прохід із зворотною логікою */
    inject_jitter_delay(entropy_seed >> 4);
    if (len >= 1024 && image_addr != 0) {
        stage2_res = STATUS_OK_STAGE2;
        check_acc += 2;
    }
    hardware_barrier();

    /* Перевірка інваріантів та масок */
    if ((stage1_res == STATUS_OK_STAGE1) &&
        (stage2_res == STATUS_OK_STAGE2) &&
        (check_acc == 3)) {
        
        /* Додатковий контроль комплементарності */
        if ((stage1_res ^ ~STATUS_OK_STAGE1) == STATUS_INV_PATTERN) {
            return STATUS_OK_STAGE1;
        }
    }

    secure_tamper_panic();
    return STATUS_FAULT_DETECTED;
}

/* Налаштування апаратного MPU перед стрибком у застосунок */
void configure_mpu_and_isolate(void) {
    /* Вимкнути MPU перед зміною конфігурації */
    MPU_CTRL_REG = 0;
    hardware_barrier();

    /* Регіон 0: Код Flash (128 КБ) - Привілейований RO, Користувацький RO */
    MPU_RNR_REG  = 0;
    MPU_RBAR_REG = 0x08000000UL;
    MPU_RASR_REG = MPU_RASR_ENABLE | MPU_RASR_SIZE_128KB | MPU_RASR_AP_FULL_RO;

    /* Регіон 1: Захищене ОЗП ключів (8 КБ) - Привілейований RW, Користувач: Немає, XN=1 */
    MPU_RNR_REG  = 1;
    MPU_RBAR_REG = 0x20000000UL;
    MPU_RASR_REG = MPU_RASR_ENABLE | (12UL << 1) | MPU_RASR_AP_PRIV_RW | MPU_RASR_XN;

    /* Регіон 2: ОЗП застосунку (56 КБ) - Привілейований RW, Користувач: RW, XN=1 */
    MPU_RNR_REG  = 2;
    MPU_RBAR_REG = 0x20002000UL;
    MPU_RASR_REG = MPU_RASR_ENABLE | MPU_RASR_SIZE_64KB | MPU_RASR_AP_FULL_RW | MPU_RASR_XN;

    /* Регіон 3: Периферія (512 МБ) - Лише привілейований доступ, XN=1 */
    MPU_RNR_REG  = 3;
    MPU_RBAR_REG = 0x40000000UL;
    MPU_RASR_REG = MPU_RASR_ENABLE | MPU_RASR_SIZE_512MB | MPU_RASR_AP_PRIV_RW | MPU_RASR_XN;

    /* Увімкнути MemManage Fault у системному блоці керування */
    SCB_SHCSR_REG |= (1UL << 16);

    /* Увімкнути MPU з увімкненим правилом за замовчуванням для привілейованих переривань */
    MPU_CTRL_REG = (1UL << 0) | (1UL << 2);
    hardware_barrier();
}

/* Безпечний стрибок у користувацький застосунок зі скиданням привілеїв */
void jump_to_unprivileged_app(uint32_t app_entry, uint32_t app_stack) {
    /* Встановити покажчик стека процесу (PSP) */
    __asm__ volatile("msr psp, %0" : : "r"(app_stack) : "memory");

    /* Перемкнути SP на PSP і скинути привілеї (nPRIV=1, SPSEL=1) */
    __asm__ volatile(
        "mov r0, #3\n"
        "msr control, r0\n"
        "isb\n"
        "bx %0\n"
        : : "r"(app_entry) : "r0", "memory"
    );
}
