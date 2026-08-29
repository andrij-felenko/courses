/* crash_log.h — журнал причин рестарту в пам'яті, яка переживає скидання.
 *
 * Виріб ніколи не перезавантажується мовчки: кожен старт лишає в журналі
 * причину, лічильник завантажень і, якщо то був збій, контекст падіння. */
#ifndef CRASH_LOG_H
#define CRASH_LOG_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef enum {
    RESET_CAUSE_UNKNOWN = 0,
    RESET_CAUSE_POWER_ON,   /* холодний старт: живлення щойно подано */
    RESET_CAUSE_PIN,        /* зовнішній NRST — кнопка або програматор */
    RESET_CAUSE_BROWN_OUT,  /* просідання живлення нижче порога BOR */
    RESET_CAUSE_SOFTWARE,   /* нас перезапустила сама прошивка */
    RESET_CAUSE_IWDG,       /* незалежний сторож: логіка зависла */
    RESET_CAUSE_WWDG,       /* віконний сторож */
    RESET_CAUSE_LOW_POWER   /* збій виходу зі standby */
} reset_cause_t;

typedef enum {
    PANIC_NONE = 0,
    PANIC_HARDFAULT,       /* апаратний виняток ядра */
    PANIC_ASSERTION,       /* порушений інваріант прошивки */
    PANIC_SENSOR_TIMEOUT,  /* давач не відповів у відведений час */
    PANIC_BUS_STUCK,       /* шина не звільнилася після відновлення */
    PANIC_LOOP_TOO_FAST,   /* цикл крутиться швидше за вікно сторожа */
    PANIC_BROWN_OUT        /* монітор живлення побачив просідання */
} panic_reason_t;

/* Контекст місця падіння: те, що інженер шукає в дампі найперше. */
typedef struct {
    uint32_t pc;   /* лічильник команд у мить збою */
    uint32_t lr;   /* адреса повернення — хто викликав */
    uint32_t sp;   /* покажчик стека */
    uint32_t cfsr; /* конфігурований регістр стану збою ядра */
} fault_context_t;

typedef struct {
    uint32_t magic;
    uint32_t boot_count;         /* скільки разів пристрій стартував узагалі */
    uint32_t fault_count;        /* скільки з них — після аварії */
    uint32_t safe_state_entries; /* скільки разів гасили силові каскади */
    uint32_t reset_cause;        /* reset_cause_t поточного старту */
    uint32_t raw_rcc_csr;        /* сирий регістр — на випадок нової ревізії кремнію */
    uint32_t panic_reason;       /* panic_reason_t останньої аварії */
    fault_context_t fault;
    uint32_t uptime_ms;          /* скільки прожили до аварії */
    uint16_t crc;
    uint16_t reserved;
} crash_log_t;

/* Виконати на самому початку старту, до ініціалізації периферії.
 * Читає й очищає прапорці RCC_CSR, перевіряє цілісність журналу
 * (пам'ять могла деградувати під час просідання) і повертає причину. */
reset_cause_t crash_log_begin_boot(void);

/* Записати аварію. Викликається з обробника збою вже після того,
 * як силові каскади знеструмлено. */
void crash_log_record_panic(panic_reason_t reason, const fault_context_t *ctx);

void crash_log_note_safe_state(void);
void crash_log_note_uptime(uint32_t ms);

const crash_log_t *crash_log_get(void);

/* Чи журнал пережив рестарт цілим. Порожній журнал після холодного
 * старту — теж цілий: його щойно створили заново. */
bool crash_log_is_intact(void);

/* Один рядок телеметрії у ASCII. Повертає довжину без завершального нуля. */
size_t crash_log_render(char *buf, size_t cap);

const char *reset_cause_name(reset_cause_t cause);
const char *panic_reason_name(panic_reason_t reason);

#endif /* CRASH_LOG_H */
