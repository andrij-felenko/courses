#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

// ── 1. Семантичний контракт абстракції приймача телеметрії ────────────

// Контракт приймача: будь-який транспорт реалізує операцію запису байтів
typedef struct telemetry_sink telemetry_sink_t;

struct telemetry_sink {
    // Поліморфна операція запису
    bool (*write_bytes)(telemetry_sink_t* self, const uint8_t* data, size_t len);
};

// ── 2. Бізнес-логіка: оперує сутностями завдання через абстракцію ──────

typedef struct {
    int32_t lat_deg_e7;
    int32_t lon_deg_e7;
    int32_t alt_mm;
    uint32_t timestamp_ms;
} nav_data_t;

// Формування та відправка пакета не знає нічого про UART, сокети чи пам'ять
bool send_nav_packet(telemetry_sink_t* sink, const nav_data_t* nav) {
    if (!sink || !nav) return false;

    uint8_t packet[24];
    packet[0] = 0xAA; // Преамбула кадру
    packet[1] = 0x55;
    packet[2] = sizeof(nav_data_t); // Довжина корисного навантаження (16 байт)

    memcpy(&packet[3], nav, sizeof(nav_data_t));

    // Розрахунок простої контрольної суми XOR
    uint8_t crc = 0;
    for (size_t i = 0; i < 3 + sizeof(nav_data_t); ++i) {
        crc ^= packet[i];
    }
    packet[3 + sizeof(nav_data_t)] = crc;

    // Відправка через абстрактну межу
    return sink->write_bytes(sink, packet, sizeof(packet));
}

// ── 3. Конкретні реалізації під капотом межі ──────────────────────────

// Реалізація 1: Кільцевий буфер пам'яті (Blackbox)
#define BLACKBOX_CAPACITY 512

typedef struct {
    telemetry_sink_t base; // Базовий інтерфейс
    uint8_t storage[BLACKBOX_CAPACITY];
    size_t head;
    size_t count;
} blackbox_sink_t;

static bool blackbox_write(telemetry_sink_t* base, const uint8_t* data, size_t len) {
    blackbox_sink_t* self = (blackbox_sink_t*)base;
    if (self->count + len > BLACKBOX_CAPACITY) {
        return false; // Захист інваріанта ємності буфера
    }
    for (size_t i = 0; i < len; ++i) {
        self->storage[self->head] = data[i];
        self->head = (self->head + 1) % BLACKBOX_CAPACITY;
    }
    self->count += len;
    return true;
}

void blackbox_init(blackbox_sink_t* bb) {
    bb->base.write_bytes = blackbox_write;
    bb->head = 0;
    bb->count = 0;
}

// Реалізація 2: Апаратний UART (запис у регістр)
typedef struct {
    telemetry_sink_t base;
    volatile uint32_t* uart_dr; // Вказівник на апаратний регістр даних
    volatile uint32_t* uart_sr; // Вказівник на регістр статусу
} uart_sink_t;

static bool uart_write(telemetry_sink_t* base, const uint8_t* data, size_t len) {
    uart_sink_t* self = (uart_sink_t*)base;
    for (size_t i = 0; i < len; ++i) {
        // Очікування готовності передавача (імітація біта TXE)
        while (!(*(self->uart_sr) & 0x80)) {
            // Очікування звільнення апаратного буфера
        }
        *(self->uart_dr) = data[i];
    }
    return true;
}

void uart_sink_init(uart_sink_t* us, volatile uint32_t* dr, volatile uint32_t* sr) {
    us->base.write_bytes = uart_write;
    us->uart_dr = dr;
    us->uart_sr = sr;
}
