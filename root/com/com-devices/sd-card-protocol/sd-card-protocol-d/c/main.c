#include <stdint.h>
#include <stdbool.h>

// Приклад відправлення 48-бітної команди SD та прийому відповіді R1
typedef struct {
    uint8_t cmd_idx;
    uint32_t argument;
    uint32_t response_r1;
} sd_cmd_transaction_t;

extern void hal_sd_send_cmd_48bit(uint8_t idx, uint32_t arg);
extern bool hal_sd_wait_r1_response(uint32_t *r1_out, uint32_t timeout_ms);
extern bool hal_sd_poll_dat0_busy(uint32_t timeout_ms);

bool sd_execute_block_write(uint32_t sector_addr, const uint8_t data_512b[512]) {
    uint32_t r1_status = 0;

    // 1. Відправлення CMD24 (WRITE_BLOCK)
    hal_sd_send_cmd_48bit(24, sector_addr);
    if (!hal_sd_wait_r1_response(&r1_status, 100)) {
        return false; // Таймаут очікування відповіді на команду
    }

    // 2. Перевірка прапорців помилок у Card Status R1
    if (r1_status & 0xFFD98008) {
        return false; // Апаратна помилка карти або захист від запису
    }

    // 3. Передача 512 байтів даних по лініях DAT0..DAT3 з апаратним CRC16
    // (Апаратний контролер автоматично надсилає Start bit, 512B, CRC16, Stop bit)
    
    // 4. Опитування лінії DAT0 до зняття сигналу Busy (повернення в High)
    if (!hal_sd_poll_dat0_busy(500)) {
        return false; // Таймаут запису у фізичні комірки Flash
    }

    return true;
}
