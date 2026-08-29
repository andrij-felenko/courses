/* main.c — прошивки для емульованого ядра й запуск сценаріїв.
 *
 * Обидва образи асембльовано руками, стовпчиком байтів: наша ISA настільки
 * мала, що окремий асемблер тут був би довшим за саму програму. Ціна ручного
 * асемблювання — адреси переходів, які треба рахувати самому, тому кожен
 * образ проходить перевірку міток перед запуском.
 */
#include <stddef.h>
#include <stdio.h>

#include "bus.h"
#include "cpu.h"
#include "isa.h"

#define LO(addr) (uint8_t)((addr) & 0x00FFu)
#define HI(addr) (uint8_t)(((addr) >> 8) & 0x00FFu)

#define MAX_STEPS 200uL

/* --- Сценарій 1: прошивка з покрокового розбору ------------------------
 * Блимає світлодіодом через MMIO, віднімає й кладе результат у SRAM.
 */
static const uint8_t k_demo_firmware[] = {
    /* 0x0000 */ OP_LOAD_IMM_R0,   0x01,                  /* R0 = 1            */
    /* 0x0002 */ OP_LOAD_IMM_ACC,  0x01,                  /* ACC = 1           */
    /* 0x0004 */ OP_STORE_MEM_ACC, LO(0x8000), HI(0x8000),/* світлодіод УВІМК. */
    /* 0x0007 */ OP_LOAD_IMM_ACC,  0x00,                  /* ACC = 0           */
    /* 0x0009 */ OP_STORE_MEM_ACC, LO(0x8000), HI(0x8000),/* світлодіод ВИМК.  */
    /* 0x000C */ OP_LOAD_IMM_ACC,  0x03,                  /* ACC = 3           */
    /* 0x000E */ OP_SUB_ACC_R0,                           /* ACC = 3 - 1 = 2   */
    /* 0x000F */ OP_STORE_MEM_ACC, LO(0x4000), HI(0x4000),/* SRAM[0x4000] = 2  */
    /* 0x0012 */ OP_HALT
};

/* --- Сценарій 2: опитування кнопки та нештатні звернення до шини -------
 * Ядро крутиться в циклі опитування порту вводу, доки кнопка не продавить
 * підтяжку, вмикає світлодіод, а далі навмисно чіпає всі гострі кути карти
 * адрес: переповнення суматора, запис у ROM, фантомну адресу й порожнечу.
 */
#define LBL_POLL   0x0002u
#define LBL_LED_ON 0x000Cu

static const uint8_t k_edge_firmware[] = {
    /* 0x0000 */ OP_LOAD_IMM_R0,   0x01,                          /* маска біта 0 */
    /* 0x0002 */ OP_LOAD_MEM_ACC,  LO(0x8001), HI(0x8001),        /* читаємо GPIO_IN */
    /* 0x0005 */ OP_AND_ACC_R0,                                   /* лишаємо біт кнопки */
    /* 0x0006 */ OP_JZ,            LO(LBL_LED_ON), HI(LBL_LED_ON),/* 0 -> натиснуто */
    /* 0x0009 */ OP_JMP,           LO(LBL_POLL),   HI(LBL_POLL),  /* ні -> опитуємо далі */

    /* 0x000C */ OP_LOAD_IMM_ACC,  0x01,
    /* 0x000E */ OP_STORE_MEM_ACC, LO(0x8000), HI(0x8000),        /* світлодіод УВІМК. */

    /* 0x0011 */ OP_LOAD_IMM_ACC,  0xFF,
    /* 0x0013 */ OP_ADD_ACC_R0,                                   /* 0xFF+1: ACC=0x00, C=1 */
    /* 0x0014 */ OP_STORE_MEM_ACC, LO(0x4001), HI(0x4001),        /* SRAM[0x4001] = 0x00 */

    /* 0x0017 */ OP_XOR_ACC_R0,                                   /* ACC = 0x00 ^ 0x01 = 1 */
    /* 0x0018 */ OP_STORE_MEM_ACC, LO(0x0010), HI(0x0010),        /* запис у ROM -> помилка */

    /* 0x001B */ OP_LOAD_MEM_ACC,  LO(0x8003), HI(0x8003),        /* фантом GPIO_IN */
    /* 0x001E */ OP_LOAD_MEM_ACC,  LO(0xC000), HI(0xC000),        /* порожнеча -> 0xFF */
    /* 0x0021 */ OP_STORE_MEM_ACC, LO(0x4002), HI(0x4002),        /* SRAM[0x4002] = 0xFF */
    /* 0x0024 */ OP_HALT
};

/* Самоперевірка ручного асемблювання: якщо в образ вставили чи забрали байт,
   мітки переходів «поїдуть», і програма стрибне в середину іншої інструкції.
   Дешевше зловити це тут, ніж ловити химерну поведінку в трасуванні. */
static bool edge_firmware_labels_ok(void)
{
    if (sizeof k_edge_firmware <= LBL_LED_ON) {
        fprintf(stderr, "[ASM] Образ коротший за мітку LED_ON\n");
        return false;
    }
    if (k_edge_firmware[LBL_POLL] != OP_LOAD_MEM_ACC) {
        fprintf(stderr, "[ASM] Мітка POLL (0x%04X) не вказує на LOAD_MEM_ACC\n", LBL_POLL);
        return false;
    }
    if (k_edge_firmware[LBL_LED_ON] != OP_LOAD_IMM_ACC) {
        fprintf(stderr, "[ASM] Мітка LED_ON (0x%04X) не вказує на LOAD_IMM_ACC\n", LBL_LED_ON);
        return false;
    }
    return true;
}

static const char *status_text(CpuStatus status)
{
    switch (status) {
        case CPU_HALTED:     return "зупинено інструкцією HALT";
        case CPU_FAULT:      return "ПАСТКА: невідома інструкція";
        case CPU_STEP_LIMIT: return "ПЕРЕРВАНО сторожовим лічильником";
        default:             return "невідомо";
    }
}

static CpuStatus run_scenario(const char *title,
                              const uint8_t *image,
                              size_t         length,
                              unsigned       button_press_after)
{
    CpuState  cpu;
    CpuStatus status;

    printf("\n=== %s ===\n", title);

    bus_init();
    bus_set_button_press_after(button_press_after);
    if (!bus_load_rom(image, length)) {
        return CPU_FAULT;
    }

    cpu_reset(&cpu);
    printf("[RESET] PC=0x%04X, %zu байтів прошивки в ROM\n\n", cpu.pc, length);

    status = cpu_run(&cpu, MAX_STEPS);

    printf("\n--- Підсумок: %s ---\n", status_text(status));
    printf("Інструкцій виконано : %lu\n", cpu.instructions);
    printf("Шинних циклів       : %lu\n", bus_cycles());
    printf("Помилок шини        : %u\n", bus_error_count());
    printf("Прапорці            : Z=%d C=%d\n", cpu.flag_z, cpu.flag_c);
    printf("GPIO_OUT (засувка)  : 0x%02X\n", bus_gpio_out_latch());
    printf("SRAM[0x4000..0x4002]: 0x%02X 0x%02X 0x%02X\n",
           bus_peek(0x4000), bus_peek(0x4001), bus_peek(0x4002));

    return status;
}

int main(void)
{
    CpuStatus demo;
    CpuStatus edge;

    bus_set_trace(true);
    cpu_set_trace(true);

    demo = run_scenario("СЦЕНАРІЙ 1: блимання світлодіодом і запис у SRAM",
                        k_demo_firmware, sizeof k_demo_firmware, BUTTON_NEVER);

    if (!edge_firmware_labels_ok()) {
        return 1;
    }

    /* Кнопку натискають після третього опитування: до того цикл опитування
       крутиться вхолосту, як і на справжній платі. */
    edge = run_scenario("СЦЕНАРІЙ 2: кнопка, переповнення та гострі кути карти адрес",
                        k_edge_firmware, sizeof k_edge_firmware, 3u);

    return (demo == CPU_HALTED && edge == CPU_HALTED) ? 0 : 1;
}
