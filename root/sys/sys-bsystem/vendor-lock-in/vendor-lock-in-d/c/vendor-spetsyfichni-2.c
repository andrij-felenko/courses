/* Діалект GCC / Clang (C) */
__attribute__((section(".ramfunc"), noinline)) void Flash_EraseSector(uint32_t address);

/* Розміщення за конкретною адресою робиться через секцію лінкера */
__attribute__((section(".shared_ram"))) uint32_t SharedBuffer[256];

struct __attribute__((packed)) TelemetryPacket {
    uint8_t  id;
    uint32_t timestamp;
};
