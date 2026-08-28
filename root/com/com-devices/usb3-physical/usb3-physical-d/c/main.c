#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

// Бітові маски регістру стану порту xHCI PORTSC
#define PORTSC_CCS         (1U << 0)   // Current Connect Status (наявність зв'язку)
#define PORTSC_PED         (1U << 1)   // Port Enabled/Disabled
#define PORTSC_PLS_MASK    (0xFU << 5) // Port Link State Mask
#define PORTSC_SPEED_MASK  (0xFU << 10)// Port Speed Mask

// Стани кінцевого автомата LTSSM
typedef enum {
    LTSSM_U0            = 0, // Робочий активний стан передачі даних
    LTSSM_U1            = 1, // Енергозбереження (швидкий вихід)
    LTSSM_U2            = 2, // Енергозбереження (повільний вихід)
    LTSSM_U3            = 3, // Стан сну (Suspend)
    LTSSM_SS_DISABLED   = 4, // SuperSpeed вимкнено
    LTSSM_RX_DETECT     = 5, // Виявлення приймача через RC-заряд
    LTSSM_SS_INACTIVE   = 6, // Неактивний стан
    LTSSM_POLLING       = 7, // Тренування лінії (LFPS + екземпляри TS1/TS2)
    LTSSM_RECOVERY      = 8, // Відновлення синхронізації
    LTSSM_HOT_RESET     = 9, // Гаряче скидання
    LTSSM_COMPLIANCE    = 10,// Тестовий режим перевірки стандартів
    LTSSM_LOOPBACK      = 11 // Режим зворотного замикання петлі
} ltssm_state_t;

// Структура для опису стану порту
typedef struct {
    bool is_connected;
    bool is_enabled;
    ltssm_state_t link_state;
    uint8_t speed_id;
} port_status_t;

// Декодування сирого значення регістру PORTSC
port_status_t decode_portsc(uint32_t portsc_raw) {
    port_status_t status;
    status.is_connected = (portsc_raw & PORTSC_CCS) != 0;
    status.is_enabled   = (portsc_raw & PORTSC_PED) != 0;
    status.link_state   = (ltssm_state_t)((portsc_raw & PORTSC_PLS_MASK) >> 5);
    status.speed_id     = (uint8_t)((portsc_raw & PORTSC_SPEED_MASK) >> 10);
    return status;
}

// Друк текстового опису стану
void print_port_diagnostics(const port_status_t *st) {
    printf("SuperSpeed Port Status:\n");
    printf("  Physical Connection : %s\n", st->is_connected ? "Attached" : "Open");
    printf("  Port Enabled        : %s\n", st->is_enabled ? "Yes" : "No");
    
    const char *state_str = "Unknown";
    switch (st->link_state) {
        case LTSSM_U0:          state_str = "U0 (Active SuperSpeed)"; break;
        case LTSSM_RX_DETECT:   state_str = "Rx.Detect (Testing RC charge)"; break;
        case LTSSM_POLLING:     state_str = "Polling (LFPS link training)"; break;
        case LTSSM_RECOVERY:    state_str = "Recovery (Resynchronizing)"; break;
        case LTSSM_U3:          state_str = "U3 (Suspended)"; break;
        default:                state_str = "Other LTSSM State"; break;
    }
    printf("  LTSSM Link State    : %s\n", state_str);
    printf("  Speed Protocol ID   : %u (4 = Gen1 5Gbps, 5 = Gen2 10Gbps)\n", st->speed_id);
}

int main(void) {
    // Приклад емуляції значення PORTSC при підключеному USB 3.0 Gen 1 пристрої у стані U0
    // CCS=1, PED=1, PLS=0 (U0), Speed=4 (SuperSpeed 5 Gbps)
    uint32_t simulated_portsc = 0x00001023;
    
    port_status_t status = decode_portsc(simulated_portsc);
    print_port_diagnostics(&status);
    
    return 0;
}
