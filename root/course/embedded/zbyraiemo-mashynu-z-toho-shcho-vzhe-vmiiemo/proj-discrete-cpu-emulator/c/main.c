#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MEMORY_SIZE 65536
#define MMIO_GPIO_OUT 0x8000
#define MMIO_GPIO_IN  0x8001

/* Опкоди інструкцій нашої ISA */
enum Opcode {
    OP_NOP           = 0x00,
    OP_LOAD_IMM_ACC  = 0x01,
    OP_LOAD_IMM_R0   = 0x02,
    OP_LOAD_MEM_ACC  = 0x10,
    OP_STORE_MEM_ACC = 0x20,
    OP_ADD_ACC_R0    = 0x30,
    OP_SUB_ACC_R0    = 0x31,
    OP_AND_ACC_R0    = 0x32,
    OP_XOR_ACC_R0    = 0x33,
    OP_JMP           = 0x40,
    OP_JZ            = 0x41,
    OP_HALT          = 0xFF
};

/* Стан процесорного ядра */
typedef struct {
    uint16_t pc;
    uint8_t  ir;
    uint8_t  acc;
    uint8_t  r0;
    bool     flag_z;
    bool     flag_c;
    bool     halted;
} CpuState;

/* Фізична пам'ять та стан периферійного заліза */
static uint8_t g_memory[MEMORY_SIZE];
static uint8_t g_gpio_out_latch = 0x00;
static uint8_t g_gpio_in_pins   = 0x01; /* кнопка відпущена (підтяжка до 1) */

/* Імітація системної шини та адресного дешифратора (Address Decoding) */
static uint8_t bus_read(uint16_t addr) {
    if (addr == MMIO_GPIO_IN) {
        printf("  [BUS RD] Читання MMIO 0x%04X (GPIO IN) = 0x%02X\n", addr, g_gpio_in_pins);
        return g_gpio_in_pins;
    }
    if (addr == MMIO_GPIO_OUT) {
        return g_gpio_out_latch;
    }
    return g_memory[addr];
}

static void bus_write(uint16_t addr, uint8_t data) {
    if (addr == MMIO_GPIO_OUT) {
        g_gpio_out_latch = data;
        bool led_state = (data & 0x01) != 0;
        printf("  [BUS WR] Запис MMIO 0x%04X (GPIO OUT) = 0x%02X -> Світлодіод: %s\n",
               addr, data, led_state ? "УВІМКНЕНО (3.3 В)" : "ВИМКНЕНО (0 В)");
        return;
    }
    if (addr < 0x4000) {
        printf("  [BUS ERROR] Спроба запису в ROM за адресою 0x%04X!\n", addr);
        return;
    }
    g_memory[addr] = data;
}

/* Оновлення прапорців стану АЛП */
static void update_flags_alu(CpuState *cpu, uint16_t raw_result) {
    cpu->acc = (uint8_t)(raw_result & 0xFF);
    cpu->flag_z = (cpu->acc == 0);
    cpu->flag_c = (raw_result > 0xFF);
}

/* Один повний цикл Fetch-Decode-Execute */
static void cpu_step(CpuState *cpu) {
    if (cpu->halted) return;

    /* 1. ФАЗА ВИБІРКИ (FETCH) */
    uint16_t current_pc = cpu->pc;
    cpu->ir = bus_read(cpu->pc++);

    printf("TICK | PC:0x%04X | IR:0x%02X | ACC:0x%02X | R0:0x%02X | Z:%d C:%d\n",
           current_pc, cpu->ir, cpu->acc, cpu->r0, cpu->flag_z, cpu->flag_c);

    /* 2. ФАЗА ДЕКОДУВАННЯ ТА ВИКОНАННЯ (DECODE & EXECUTE) */
    switch (cpu->ir) {
        case OP_NOP:
            break;

        case OP_LOAD_IMM_ACC:
            cpu->acc = bus_read(cpu->pc++);
            break;

        case OP_LOAD_IMM_R0:
            cpu->r0 = bus_read(cpu->pc++);
            break;

        case OP_LOAD_MEM_ACC: {
            uint8_t lo = bus_read(cpu->pc++);
            uint8_t hi = bus_read(cpu->pc++);
            uint16_t addr = (uint16_t)(lo | (hi << 8));
            cpu->acc = bus_read(addr);
            break;
        }

        case OP_STORE_MEM_ACC: {
            uint8_t lo = bus_read(cpu->pc++);
            uint8_t hi = bus_read(cpu->pc++);
            uint16_t addr = (uint16_t)(lo | (hi << 8));
            bus_write(addr, cpu->acc);
            break;
        }

        case OP_ADD_ACC_R0: {
            uint16_t res = (uint16_t)cpu->acc + (uint16_t)cpu->r0;
            update_flags_alu(cpu, res);
            break;
        }

        case OP_SUB_ACC_R0: {
            uint16_t res = (uint16_t)cpu->acc - (uint16_t)cpu->r0;
            update_flags_alu(cpu, res);
            break;
        }

        case OP_AND_ACC_R0:
            cpu->acc &= cpu->r0;
            cpu->flag_z = (cpu->acc == 0);
            break;

        case OP_XOR_ACC_R0:
            cpu->acc ^= cpu->r0;
            cpu->flag_z = (cpu->acc == 0);
            break;

        case OP_JMP: {
            uint8_t lo = bus_read(cpu->pc++);
            uint8_t hi = bus_read(cpu->pc++);
            cpu->pc = (uint16_t)(lo | (hi << 8));
            break;
        }

        case OP_JZ: {
            uint8_t lo = bus_read(cpu->pc++);
            uint8_t hi = bus_read(cpu->pc++);
            if (cpu->flag_z) {
                cpu->pc = (uint16_t)(lo | (hi << 8));
                printf("  [BRANCH TAKEN] Стрибок на адресу 0x%04X (Z=1)\n", cpu->pc);
            }
            break;
        }

        case OP_HALT:
            cpu->halted = true;
            printf("  [CPU] Сигнал HALT отримано. Ядро зупинено.\n");
            break;

        default:
            printf("  [CPU ERROR] Невідомий опкод 0x%02X за адресою 0x%04X!\n", cpu->ir, current_pc);
            cpu->halted = true;
            break;
    }
}

int main(void) {
    memset(g_memory, 0, sizeof(g_memory));

    /* Записуємо тестову бінарну прошивку в ROM (з адреси 0x0000):
       Програма двічі блимає світлодіодом через MMIO, обчислює різницю і записує в RAM. */
    uint8_t firmware[] = {
        /* 0x0000: Ініціалізація лічильника циклів: R0 = 1 */
        OP_LOAD_IMM_R0, 0x01,
        
        /* 0x0002: Увімкнути світлодіод (ACC = 0x01 -> MMIO 0x8000) */
        OP_LOAD_IMM_ACC, 0x01,
        OP_STORE_MEM_ACC, 0x00, 0x80,

        /* 0x0007: Вимкнути світлодіод (ACC = 0x00 -> MMIO 0x8000) */
        OP_LOAD_IMM_ACC, 0x00,
        OP_STORE_MEM_ACC, 0x00, 0x80,

        /* 0x000C: Зберегти поточний лічильник у RAM [0x4000] */
        OP_LOAD_IMM_ACC, 0x03,
        OP_SUB_ACC_R0,               /* ACC = 3 - 1 = 2 */
        OP_STORE_MEM_ACC, 0x00, 0x40,/* RAM[0x4000] = 2 */

        /* 0x0013: Зупинка */
        OP_HALT
    };

    memcpy(g_memory, firmware, sizeof(firmware));

    /* Ініціалізація процесора (Power-On Reset) */
    CpuState cpu = {
        .pc = 0x0000,
        .ir = 0x00,
        .acc = 0x00,
        .r0 = 0x00,
        .flag_z = false,
        .flag_c = false,
        .halted = false
    };

    printf("=== СТАРТ ЕМУЛЯЦІЇ ПРОЦЕСОРА (RESET PC=0x0000) ===\n\n");
    while (!cpu.halted) {
        cpu_step(&cpu);
    }
    printf("\n=== ЕМУЛЯЦІЮ ЗАВЕРШЕНО ===\n");
    printf("Фінальний стан RAM[0x4000] = 0x%02X\n", g_memory[0x4000]);
    printf("Фінальний стан GPIO Latch = 0x%02X\n", g_gpio_out_latch);

    return 0;
}
