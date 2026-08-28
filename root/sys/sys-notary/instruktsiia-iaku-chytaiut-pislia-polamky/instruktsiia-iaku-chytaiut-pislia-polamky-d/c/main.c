#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    FAULT_NONE = 0,
    FAULT_SUPPLY_UNDERVOLTAGE = 1,  /* 1 спалах: Напруга живлення < 18 В */
    FAULT_RS485_NO_TERMINATION = 2, /* 2 спалахи: Відсутня термінація шини */
    FAULT_SENSOR_OPEN_CIRCUIT  = 3, /* 3 спалахи: Обрив лінії вимірювального моста */
    FAULT_CONFIG_CRC_MISMATCH  = 4  /* 4 спалахи: Пошкоджено конфігурацію в EEPROM */
} FaultCode;

typedef struct {
    FaultCode code;
    const char *symptom;
    const char *probable_cause;
    const char *corrective_action;
} FaultDescriptor;

static const FaultDescriptor FAULT_TABLE[] = {
    {
        FAULT_SUPPLY_UNDERVOLTAGE,
        "STATUS LED блимає 1 раз кожні 2 секунди",
        "Напруга живлення впала нижче 18 В під навантаженням",
        "Перевірити перетин кабелю живлення та вихідну напругу блока 24 В DC"
    },
    {
        FAULT_RS485_NO_TERMINATION,
        "STATUS LED блимає 2 рази кожні 2 секунди",
        "Опір знеструмленої лінії RS-485 відрізняється від 60 Ом (немає термінатора)",
        "Увімкнути DIP-перемикач TERM 120R на першому та останньому вузлах шини"
    },
    {
        FAULT_SENSOR_OPEN_CIRCUIT,
        "STATUS LED блимає 3 рази кожні 2 секунди",
        "Струм у петлі 4-20 мА становить 0.0 мА (обрив сигнального кабелю)",
        "Перевірити цілісність лінії від клемника SENSOR+ до первинного перетворювача"
    },
    {
        FAULT_CONFIG_CRC_MISMATCH,
        "STATUS LED блимає 4 рази кожні 2 секунди",
        "Контрольна сума CRC32 налаштувань у пам'яті FRAM не збігається",
        "Скинути прилад до заводських налаштувань утримуванням кнопки RESET 10 с"
    }
};

#define FAULT_TABLE_SIZE (sizeof(FAULT_TABLE) / sizeof(FAULT_TABLE[0]))

const FaultDescriptor* get_fault_descriptor(FaultCode code) {
    for (size_t i = 0; i < FAULT_TABLE_SIZE; ++i) {
        if (FAULT_TABLE[i].code == code) {
            return &FAULT_TABLE[i];
        }
    }
    return NULL;
}

FaultCode run_post_diagnostics(float v_supply, float bus_resistance_ohms, bool sensor_connected, bool crc_valid) {
    if (v_supply < 18.0f) {
        return FAULT_SUPPLY_UNDERVOLTAGE;
    }
    if (bus_resistance_ohms < 45.0f || bus_resistance_ohms > 75.0f) {
        return FAULT_RS485_NO_TERMINATION;
    }
    if (!sensor_connected) {
        return FAULT_SENSOR_OPEN_CIRCUIT;
    }
    if (!crc_valid) {
        return FAULT_CONFIG_CRC_MISMATCH;
    }
    return FAULT_NONE;
}

void print_troubleshooting_guide(FaultCode code) {
    const FaultDescriptor *desc = get_fault_descriptor(code);
    if (!desc) {
        printf("[ДІАГНОСТИКА]: Система працює в штатному режимі (OK).\n");
        return;
    }

    printf("\n=======================================================\n");
    printf("АВАРІЙНИЙ ПРОТОКОЛ ЛОКАЛІЗАЦІЇ НЕСПРАВНОСТІ (КОД #%d)\n", desc->code);
    printf("=======================================================\n");
    printf("[СИМПТОМ]     : %s\n", desc->symptom);
    printf("[ПРИЧИНА]     : %s\n", desc->probable_cause);
    printf("[ІНСТРУКЦІЯ]  : %s\n", desc->corrective_action);
    printf("=======================================================\n");
}

int main(void) {
    printf("Ініціалізація системи та виконання процедури POST...\n");

    /* Симуляція відмови: просідання напруги до 16.2 В */
    FaultCode active_fault = run_post_diagnostics(16.2f, 60.0f, true, true);
    print_troubleshooting_guide(active_fault);

    return 0;
}
