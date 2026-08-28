#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Апаратні дефайни регістрів STM32 (або CMSIS заголовки)
#define FLASH_BACKUP_ADDR     0x0803F800U  // Останній сектор Flash (2 КБ)
#define MAGIC_RECORD_VALID    0x504C5031U  // ASCII 'PLP1'
#define MAGIC_RECORD_CORRUPT  0xDEADBEEFU

// Структура критичного стану системи (має бути кратна 8 байтам для Flash)
typedef struct __attribute__((aligned(8))) {
    uint32_t magic;              // Маркер валідності (пишеться ОСТАННІМ)
    uint32_t sequence_id;        // Монотонний лічильник знеструмлень
    uint32_t system_uptime_sec;  // Час напрацювання приладу
    int32_t  actuator_position;  // Поточна координата механізму
    float    calibrated_offset;  // Останнє калібрування
    uint32_t error_flags;        // Прапорці діагностики
    uint32_t payload_checksum;   // CRC32 попередніх полів
    uint32_t reserved_padding;   // Вирівнювання до 64-бітного слова
} EmergencyState;

static volatile EmergencyState g_live_state;
static volatile bool g_power_fail_active = false;

// Прототипи апаратних функцій платформи
void hardware_shed_auxiliary_power(void);
void flash_unlock_registers(void);
void flash_lock_registers(void);
bool flash_program_double_word(uint32_t addr, uint64_t data);
uint32_t hardware_crc32(const uint8_t *data, size_t length);

// ── 1. Обробник переривання раннього попередження (NMI / EXTI) ─────────────
void NMI_Handler(void)
{
    // 1. Апаратне скидання споживання (Load Shedding) - перші 5 мікросекунд
    // Вимикаємо ключ навантаження (радіо, підсвічування, сенсори)
    hardware_shed_auxiliary_power();

    // 2. Блокування повторного входу
    if (g_power_fail_active) {
        while (1) { __asm volatile("wfi"); }
    }
    g_power_fail_active = true;

    // 3. Підготовка даних стану в RAM
    EmergencyState save_copy;
    save_copy.sequence_id       = g_live_state.sequence_id + 1;
    save_copy.system_uptime_sec = g_live_state.system_uptime_sec;
    save_copy.actuator_position = g_live_state.actuator_position;
    save_copy.calibrated_offset = g_live_state.calibrated_offset;
    save_copy.error_flags       = g_live_state.error_flags;
    save_copy.reserved_padding  = 0xAA55AA55U;

    // 4. Розрахунок контрольної суми
    save_copy.payload_checksum = hardware_crc32(
        (const uint8_t *)&save_copy.sequence_id,
        sizeof(EmergencyState) - (2 * sizeof(uint32_t))
    );

    // 5. Запис даних у Flash (Сектор попередньо стертий у фоні!)
    flash_unlock_registers();

    const uint64_t *payload_words = (const uint64_t *)((uint8_t *)&save_copy + 8);
    size_t num_double_words = (sizeof(EmergencyState) - 8) / 8;
    uint32_t target_addr = FLASH_BACKUP_ADDR + 8;

    bool write_ok = true;
    for (size_t i = 0; i < num_double_words; ++i) {
        if (!flash_program_double_word(target_addr, payload_words[i])) {
            write_ok = false;
            break;
        }
        target_addr += 8;
    }

    // 6. АТОМАРНИЙ ФІНАЛ: Запис валідного Magic-маркера останнім словом
    if (write_ok) {
        uint64_t header_word = ((uint64_t)save_copy.sequence_id << 32) | MAGIC_RECORD_VALID;
        flash_program_double_word(FLASH_BACKUP_ADDR, header_word);
    }

    flash_lock_registers();

    // 7. Безпечне паркування: очікування апаратного BOR у глибокому сні
    while (1) {
        __asm volatile("wfi");
    }
}

// ── 2. Відновлення стану під час завантаження системи ───────────────────────
bool restore_state_on_startup(EmergencyState *out_state)
{
    const volatile EmergencyState *stored = (const EmergencyState *)FLASH_BACKUP_ADDR;

    // Перевірка маркера завершеності транзакції
    if (stored->magic != MAGIC_RECORD_VALID) {
        return false; // Запис був обірваний або Flash порожня
    }

    // Перевірка цілісності даних через CRC32
    uint32_t calc_crc = hardware_crc32(
        (const uint8_t *)&stored->sequence_id,
        sizeof(EmergencyState) - (2 * sizeof(uint32_t))
    );

    if (calc_crc != stored->payload_checksum) {
        return false; // Дані пошкоджені
    }

    // Дані цілісні - копіюємо в активний стан
    memcpy(out_state, (const void *)stored, sizeof(EmergencyState));
    return true;
}
