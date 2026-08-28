#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FRAM_SPI_CMD_WREN   0x06
#define FRAM_SPI_CMD_WRITE  0x02
#define FRAM_SPI_CMD_READ   0x03

#define FRAM_SLOT_A_ADDR    0x0100
#define FRAM_SLOT_B_ADDR    0x0200
#define SYSTEM_MAGIC_HEADER 0x504F5752UL // "POWR"

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint64_t sequence_id;
    uint64_t timestamp_ms;
    int32_t  actuator_position_steps;
    int16_t  calibrated_zero_offset;
    float    last_bus_voltage;
    float    ambient_temperature;
    uint8_t  system_state_flags;
    uint8_t  reserved_padding[3];
    uint32_t crc32;
} SystemSnapshotRecord;

// Апаратні абстракції платформи
extern void bsp_spi_fram_select(void);
extern void bsp_spi_fram_deselect(void);
extern void bsp_spi_transmit(const uint8_t *data, uint16_t length);
extern void bsp_spi_receive(uint8_t *buffer, uint16_t length);
extern void bsp_emergency_shutdown_heavy_peripherals(void);
extern uint32_t bsp_calculate_hardware_crc32(const uint8_t *data, size_t length);
extern uint64_t bsp_get_system_time_ms(void);

static volatile bool g_power_loss_in_progress = false;
static uint64_t g_current_sequence_id = 0;

void fram_send_write_enable(void) {
    uint8_t cmd = FRAM_SPI_CMD_WREN;
    bsp_spi_fram_select();
    bsp_spi_transmit(&cmd, 1);
    bsp_spi_fram_deselect();
}

void fram_write_record(uint16_t address, const SystemSnapshotRecord *record) {
    uint8_t header[3];
    header[0] = FRAM_SPI_CMD_WRITE;
    header[1] = (uint8_t)(address >> 8);
    header[2] = (uint8_t)(address & 0xFF);

    fram_send_write_enable();

    bsp_spi_fram_select();
    bsp_spi_transmit(header, sizeof(header));
    bsp_spi_transmit((const uint8_t *)record, sizeof(SystemSnapshotRecord));
    bsp_spi_fram_deselect();
}

// Високопріоритетний обробник переривання PFI від компаратора живлення
void __attribute__((interrupt)) PFI_PowerFail_IRQHandler(void) {
    if (g_power_loss_in_progress) {
        return;
    }
    g_power_loss_in_progress = true;

    // 1. Аварійне відключення потужних споживачів струму
    bsp_emergency_shutdown_heavy_peripherals();

    // 2. Складання моментального знімка стану апаратури
    SystemSnapshotRecord snapshot;
    snapshot.magic = SYSTEM_MAGIC_HEADER;
    snapshot.sequence_id = ++g_current_sequence_id;
    snapshot.timestamp_ms = bsp_get_system_time_ms();
    snapshot.actuator_position_steps = 142850;
    snapshot.calibrated_zero_offset = -12;
    snapshot.last_bus_voltage = 10.74f;
    snapshot.ambient_temperature = 42.5f;
    snapshot.system_state_flags = 0x81; // Прапорці: Екстрена зупинка + Дані свіжі

    // Обчислення CRC32 без самого поля контрольної суми
    size_t payload_bytes = sizeof(SystemSnapshotRecord) - sizeof(uint32_t);
    snapshot.crc32 = bsp_calculate_hardware_crc32((const uint8_t *)&snapshot, payload_bytes);

    // 3. Запис у черговий слот Ping-Pong (чергування A/B за парністю sequence_id)
    uint16_t target_slot_addr = (snapshot.sequence_id & 1ULL) ? FRAM_SLOT_A_ADDR : FRAM_SLOT_B_ADDR;
    fram_write_record(target_slot_addr, &snapshot);

    // 4. Перехід мікроконтролера в режим сну до остаточного знеструмлення
    while (1) {
        __asm volatile("wfi");
    }
}
