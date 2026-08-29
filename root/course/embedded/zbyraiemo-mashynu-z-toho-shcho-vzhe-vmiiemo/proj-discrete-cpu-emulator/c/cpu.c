#include "cpu.h"

#include <stdio.h>

#include "bus.h"
#include "isa.h"

static bool g_trace = true;

void cpu_set_trace(bool on)
{
    g_trace = on;
}

void cpu_reset(CpuState *cpu)
{
    cpu->pc           = 0x0000;
    cpu->ir           = 0x00;
    cpu->acc          = 0x00;
    cpu->r0           = 0x00;
    cpu->flag_z       = false;
    cpu->flag_c       = false;
    cpu->halted       = false;
    cpu->faulted      = false;
    cpu->instructions = 0;
}

bool cpu_is_running(const CpuState *cpu)
{
    return !cpu->halted && !cpu->faulted;
}

/* Один байт із потоку інструкцій. Саме тут PC їде вперед: скільки байтів
   зчитала інструкція, на стільки й посунеться лічильник. */
static uint8_t fetch_byte(CpuState *cpu)
{
    return bus_read(cpu->pc++);
}

/* 16-бітний операнд лежить у пам'яті молодшим байтом уперед (little-endian):
   два окремі шинні цикли, з яких дешифратор складає адресу. */
static uint16_t fetch_address(CpuState *cpu)
{
    uint8_t lo = fetch_byte(cpu);
    uint8_t hi = fetch_byte(cpu);
    return (uint16_t)(lo | ((uint16_t)hi << 8));
}

/* Запис результату АЛП в акумулятор разом із прапорцями.
   carry_out — дев'ятий біт суматора або сигнал позички віднімача. */
static void alu_store(CpuState *cpu, uint16_t raw_result, bool carry_out)
{
    cpu->acc    = (uint8_t)(raw_result & 0xFFu);
    cpu->flag_z = (cpu->acc == 0);
    cpu->flag_c = carry_out;
}

/* Логічні операції прапорця перенесення не чіпають — у схемі АЛП
   вихід переносу підключений лише до суматора. */
static void logic_store(CpuState *cpu, uint8_t result)
{
    cpu->acc    = result;
    cpu->flag_z = (cpu->acc == 0);
}

/* Рядок трасування друкується ДО виконання: показує, що ядро побачило
   на шині, і з якими регістрами воно заходить в інструкцію. */
static void trace_instruction(const CpuState *cpu)
{
    uint8_t  opcode   = bus_peek(cpu->pc);
    unsigned operands = isa_operand_bytes(opcode);
    char     args[16] = "";

    if (operands == 1) {
        snprintf(args, sizeof args, "0x%02X", bus_peek((uint16_t)(cpu->pc + 1)));
    } else if (operands == 2) {
        unsigned lo = bus_peek((uint16_t)(cpu->pc + 1));
        unsigned hi = bus_peek((uint16_t)(cpu->pc + 2));
        snprintf(args, sizeof args, "0x%04X", lo | (hi << 8));
    }

    printf("TICK %3lu | PC:0x%04X | %-13s %-6s | ACC:0x%02X R0:0x%02X Z:%d C:%d\n",
           cpu->instructions + 1, cpu->pc, isa_mnemonic(opcode), args,
           cpu->acc, cpu->r0, cpu->flag_z, cpu->flag_c);
}

void cpu_step(CpuState *cpu)
{
    uint16_t instruction_pc;

    if (!cpu_is_running(cpu)) {
        return;
    }

    if (g_trace) {
        trace_instruction(cpu);
    }

    /* 1. ФАЗА ВИБІРКИ (FETCH) */
    instruction_pc = cpu->pc;
    cpu->ir        = fetch_byte(cpu);
    ++cpu->instructions;

    /* 2. ФАЗИ ДЕКОДУВАННЯ ТА ВИКОНАННЯ (DECODE & EXECUTE) */
    switch (cpu->ir) {
        case OP_NOP:
            break;

        case OP_LOAD_IMM_ACC:
            cpu->acc = fetch_byte(cpu);
            break;

        case OP_LOAD_IMM_R0:
            cpu->r0 = fetch_byte(cpu);
            break;

        case OP_LOAD_MEM_ACC: {
            uint16_t addr = fetch_address(cpu);
            cpu->acc = bus_read(addr);   /* третій шинний цикл — уже за даними */
            break;
        }

        case OP_STORE_MEM_ACC: {
            uint16_t addr = fetch_address(cpu);
            bus_write(addr, cpu->acc);
            break;
        }

        case OP_ADD_ACC_R0: {
            uint16_t sum = (uint16_t)cpu->acc + (uint16_t)cpu->r0;
            alu_store(cpu, sum, sum > 0xFFu);
            break;
        }

        case OP_SUB_ACC_R0: {
            /* Позичка виникає, коли від'ємник більший за зменшуване:
               саме цей сигнал дозволяє будувати багаторозрядне віднімання. */
            bool     borrow = (cpu->r0 > cpu->acc);
            uint16_t diff   = (uint16_t)((int)cpu->acc - (int)cpu->r0);
            alu_store(cpu, diff, borrow);
            break;
        }

        case OP_AND_ACC_R0:
            logic_store(cpu, (uint8_t)(cpu->acc & cpu->r0));
            break;

        case OP_XOR_ACC_R0:
            logic_store(cpu, (uint8_t)(cpu->acc ^ cpu->r0));
            break;

        case OP_JMP:
            cpu->pc = fetch_address(cpu);
            break;

        case OP_JZ: {
            /* Операнд вибирається завжди — навіть коли перехід не відбувся:
               інакше PC зупинився б посеред інструкції. */
            uint16_t target = fetch_address(cpu);
            if (cpu->flag_z) {
                cpu->pc = target;
                if (g_trace) {
                    printf("  [BRANCH] Z=1, перехід на 0x%04X\n", target);
                }
            }
            break;
        }

        case OP_HALT:
            cpu->halted = true;
            if (g_trace) {
                printf("  [CPU] HALT: тактовий генератор ядра зупинено\n");
            }
            break;

        default:
            /* Дешифратор не має рядка під цей код операції. У кремнії це
               або пастка невизначеної інструкції, або зовсім непередбачувана
               поведінка — модель обирає перше, бо воно детерміноване. */
            cpu->faulted = true;
            printf("  [CPU FAULT] Невідомий опкод 0x%02X за адресою 0x%04X\n",
                   cpu->ir, instruction_pc);
            break;
    }
}

CpuStatus cpu_run(CpuState *cpu, unsigned long max_steps)
{
    unsigned long steps = 0;

    while (cpu_is_running(cpu)) {
        if (steps >= max_steps) {
            /* Сторожовий лічильник моделі. Прошивка з нескінченним циклом
               опитування — це нормальний стан залізяки, але емулятор мусить
               із нього вийти, а не висіти. */
            printf("  [WATCHDOG] Вичерпано ліміт у %lu інструкцій\n", max_steps);
            return CPU_STEP_LIMIT;
        }
        cpu_step(cpu);
        ++steps;
    }

    return cpu->faulted ? CPU_FAULT : CPU_HALTED;
}
