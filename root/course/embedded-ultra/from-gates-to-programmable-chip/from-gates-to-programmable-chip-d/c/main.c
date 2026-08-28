#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t r[8];       /* 8 регістрів R0-R7 (R0 == 0) */
    uint16_t pc;         /* Лічильник команд */
    bool z, n, c, v;     /* Прапорці стану АЛП */
    bool halted;
    uint16_t rom[256];   /* Пам'ять інструкцій */
    uint16_t ram[256];   /* Пам'ять даних */
} Core16;

void core_execute_cycle(Core16 *core) {
    if (core->halted) return;

    /* 1. Fetch */
    uint16_t instr = core->rom[core->pc++];

    /* 2. Decode */
    uint8_t op  = (instr >> 12) & 0x0F;
    uint8_t rd  = (instr >> 9)  & 0x07;
    uint8_t rs1 = (instr >> 6)  & 0x07;
    uint8_t rs2 = (instr >> 3)  & 0x07;

    /* 3. Execute / Write-back */
    if (op == 0x1) { /* ADD Rd, Rs1, Rs2 */
        uint32_t a = core->r[rs1];
        uint32_t b = core->r[rs2];
        uint32_t sum = a + b;
        uint16_t res = (uint16_t)sum;

        if (rd != 0) core->r[rd] = res;

        core->z = (res == 0);
        core->n = (res & 0x8000) != 0;
        core->c = (sum > 0xFFFF);
        core->v = (!((a ^ b) & 0x8000) && ((a ^ sum) & 0x8000));
    } else if (op == 0xF) { /* HLT */
        core->halted = true;
    }

    core->r[0] = 0; /* R0 апаратно заземлений */
}
