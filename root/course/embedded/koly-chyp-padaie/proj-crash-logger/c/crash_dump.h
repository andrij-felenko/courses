// Аварійний дамп у секції .noinit: пережити програмне скидання й дочекатися,
// поки після перезапуску його прочитає main().
#ifndef CRASH_DUMP_H
#define CRASH_DUMP_H

#include <stdbool.h>
#include <stdint.h>

// Базовий кадр, який апаратура Cortex-M кладе на стек при вході у виняток.
typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;  // адреса повернення в перерваний код
    uint32_t pc;  // інструкція, на якій усе зламалося
    uint32_t psr;
} cortex_frame_t;

// Що ядро встигло зробити з контекстом FPU на момент винятку.
typedef enum {
    FPU_FRAME_NONE = 0,   // базовий кадр, FPU не використовувався
    FPU_FRAME_SAVED = 1,  // розширений кадр, S0-S15 реально лежать у стеку
    FPU_FRAME_LAZY = 2    // місце під S0-S15 виділено, але ще не заповнене
} fpu_frame_state_t;

typedef struct {
    uint32_t magic;
    uint32_t crash_count;  // копія лічильника на момент падіння
    uint32_t hfsr;
    uint32_t cfsr;
    uint32_t mmfar;
    uint32_t bfar;
    uint32_t shcsr;
    uint32_t exc_return;
    uint32_t fpu_state;  // fpu_frame_state_t
    uint32_t fpscr;
    uint32_t s[16];
    cortex_frame_t frame;
    uint32_t crc;  // мусить лишатися ОСТАННІМ полем: CRC рахується до нього
} crash_dump_t;

// Викликає лише аварійний обробник. fpu_block — покажчик на розширену частину
// кадру або NULL; s[] і fpscr заповнюються тільки коли state == FPU_FRAME_SAVED.
void crash_dump_store(const cortex_frame_t *frame,
                      uint32_t exc_return,
                      fpu_frame_state_t fpu_state,
                      const uint32_t *fpu_block);

// Копіює валідний дамп у out і гасить маркер, щоб той самий звіт не друкувався
// на кожному наступному старті. false — дампу немає або CRC не збіглася.
bool crash_dump_take(crash_dump_t *out);

// Лічильник ЖИВЕ ОКРЕМО від дампу: скидання по сторожовому таймеру дамп не
// лишає взагалі, а порахувати такий перезапуск усе одно треба.
uint32_t crash_dump_consecutive(void);
void crash_dump_clear_counter(void);

// Порахувати аварійний перезапуск, який дампу не лишив (скидання по сторожовому
// таймеру, просадка живлення). crash_dump_store() кличе це сама.
uint32_t crash_dump_bump_counter(void);

#endif // CRASH_DUMP_H
