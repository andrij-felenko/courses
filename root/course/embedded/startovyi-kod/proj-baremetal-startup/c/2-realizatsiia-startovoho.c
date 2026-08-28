#include <stdint.h>
#include <stddef.h>

/* Символи адресних меж, експортовані лінкером */
extern uint32_t _estack;
extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;

/* Межі таблиці виклику конструкторів C++ */
extern void (*__init_array_start[])(void);
extern void (*__init_array_end[])(void);

/* Прототипи системних функцій */
int main(void);
void Reset_Handler(void);
void Default_Handler(void);

/* Оголошення системних винятків зі слабким зв'язком */
void NMI_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void MemManage_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void BusFault_Handler(void)   __attribute__((weak, alias("Default_Handler")));
void UsageFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SVC_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler(void)     __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void)    __attribute__((weak, alias("Default_Handler")));

/* Системне налаштування тактування за замовчуванням */
void SystemInit(void) __attribute__((weak));
void SystemInit(void) {
    /* Базова заглушка: користувач може перевизначити у власному файлі */
}

/* Увімкнення математичного співпроцесора FPU (Cortex-M4/M7/M33) */
static inline void enable_fpu(void) {
    volatile uint32_t *scb_cpacr = (volatile uint32_t *)0xE000ED88UL;
    /* Надання повного доступу (Full Access) до блоків CP10 та CP11: біти 20..23 = 0b1111 */
    *scb_cpacr |= (0xFUL << 20);
    __asm volatile("dsb\n\tisb" ::: "memory");
}

/* Ініціалізація глобальних об'єктів C++ */
static inline void init_cpp_runtime(void) {
    size_t count = (size_t)(__init_array_end - __init_array_start);
    for (size_t i = 0; i < count; ++i) {
        if (__init_array_start[i] != NULL) {
            __init_array_start[i]();
        }
    }
}

/* Головна точка входу після апаратного скидання */
void Reset_Handler(void) {
    /* 1. Копіювання початкових значень .data з Flash у RAM */
    uint32_t *p_src = &_sidata;
    uint32_t *p_dst = &_sdata;
    while (p_dst < &_edata) {
        *p_dst++ = *p_src++;
    }

    /* 2. Занулення пам'яті секції .bss у RAM */
    uint32_t *p_bss = &_sbss;
    while (p_bss < &_ebss) {
        *p_bss++ = 0;
    }

    /* 3. Апаратне налаштування: FPU та тактування */
    enable_fpu();
    SystemInit();

    /* 4. Виклик C++ конструкторів */
    init_cpp_runtime();

    /* 5. Передача керування у прикладну програму */
    (void)main();

    /* 6. Безпечний сон процесора, якщо main() випадково завершив роботу */
    while (1) {
        __asm volatile("wfi");
    }
}

/* Обробник непередбачених або невизначених переривань */
void Default_Handler(void) {
    /* Апаратна точка зупину для захоплення під налагоджувачем GDB */
    __asm volatile("bkpt #0");
    while (1) {
    }
}

/* Векторна таблиця, розташована у секції .isr_vector */
__attribute__((section(".isr_vector"), used))
void (* const g_pfnVectors[])(void) = {
    (void (*)(void))(&_estack), /* 0x00: Initial SP */
    Reset_Handler,              /* 0x04: Reset Handler */
    NMI_Handler,                /* 0x08: NMI */
    HardFault_Handler,          /* 0x0C: HardFault */
    MemManage_Handler,          /* 0x10: MemManage */
    BusFault_Handler,           /* 0x14: BusFault */
    UsageFault_Handler,         /* 0x18: UsageFault */
    0, 0, 0, 0,                 /* 0x1C..0x28: Reserved */
    SVC_Handler,                /* 0x2C: SVCall */
    0,                          /* 0x30: Debug Monitor */
    0,                          /* 0x34: Reserved */
    PendSV_Handler,             /* 0x38: PendSV */
    SysTick_Handler,            /* 0x3C: SysTick */
};
