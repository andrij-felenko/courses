/* cpu.h — процесорне ядро: регістри й трифазний цикл Fetch-Decode-Execute. */
#ifndef CPU_H
#define CPU_H

#include <stdbool.h>
#include <stdint.h>

/* Стан процесорного ядра. Кожне поле — це фізичний регістр на кристалі. */
typedef struct {
    uint16_t pc;        /* лічильник команд */
    uint8_t  ir;        /* регістр інструкцій: тримає опкод, поки він декодується */
    uint8_t  acc;       /* акумулятор */
    uint8_t  r0;        /* допоміжний регістр загального призначення */
    bool     flag_z;    /* результат АЛП дорівнює нулю */
    bool     flag_c;    /* перенесення (ADD) або позичка (SUB) */
    bool     halted;    /* тактовий генератор ядра зупинено інструкцією HALT */
    bool     faulted;   /* пастка: невідомий опкод */
    unsigned long instructions;
} CpuState;

typedef enum {
    CPU_HALTED,      /* дійшли до HALT — штатне завершення */
    CPU_FAULT,       /* ядро впало в пастку */
    CPU_STEP_LIMIT   /* сторожовий лічильник: програма не збирається зупинятися */
} CpuStatus;

/* Апаратне скидання (Power-On Reset): PC = 0x0000, регістри й прапорці в нулі. */
void cpu_reset(CpuState *cpu);

/* Рівно один повний цикл Fetch-Decode-Execute. */
void cpu_step(CpuState *cpu);

/* Крутить ядро, доки воно не стане або доки не вичерпається ліміт кроків. */
CpuStatus cpu_run(CpuState *cpu, unsigned long max_steps);

/* Чи ядро ще виконує код. */
bool cpu_is_running(const CpuState *cpu);

/* Чи друкувати трасування кожної інструкції. */
void cpu_set_trace(bool on);

#endif /* CPU_H */
