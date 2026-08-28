// Символи з лінкер-скрипта: межі секцій у RAM та джерело .data у Flash.
extern unsigned _sdata, _edata, _sidata;   // .data: куди, докуди, звідки (Flash)
extern unsigned _sbss,  _ebss;             // .bss:  нулі від _sbss до _ebss
extern int main(void);                     // точка входу застосунку

void Reset_Handler(void) {                 // сидить за вектором скидання
    // 1) копіюємо ініціалізовані глобальні змінні з Flash у RAM
    unsigned *src = &_sidata, *dst = &_sdata;
    while (dst < &_edata) *dst++ = *src++;

    // 2) обнуляємо .bss (усе, що має початок 0)
    for (dst = &_sbss; dst < &_ebss; ) *dst++ = 0;

    // 3) вказівник стека на цій архітектурі вже виставив сам процесор
    //    із першого слова таблиці векторів — тому далі можна викликати функції

    main();                                // 4) аж тепер змінні правильні — у застосунок
    for (;;) { }                           // main() не повертається; страхувальний цикл
}
