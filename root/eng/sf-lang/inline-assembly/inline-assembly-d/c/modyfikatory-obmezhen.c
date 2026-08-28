/* НЕБЕЗПЕЧНО: помилка через відсутність раннього клірингу */
uint32_t broken_combine(uint32_t a, uint32_t b) {
    uint32_t result;
    __asm__ (
        "movl %1, %0\n\t"   /* Якщо %0 та %2 в одному регістрі, %2 затерто! */
        "addl %2, %0"
        : "=r" (result)     /* ДЕФЕКТ: компілятор може призначити result та b регістр %eax */
        : "r" (a), "r" (b)
    );
    return result;
}

/* БЕЗПЕЧНО: модифікатор & забороняє спільне використання регістрів */
uint32_t safe_combine(uint32_t a, uint32_t b) {
    uint32_t result;
    __asm__ (
        "movl %1, %0\n\t"
        "addl %2, %0"
        : "=&r" (result)    /* ВИПРАВЛЕНО: result гарантовано отримає унікальний регістр */
        : "r" (a), "r" (b)
    );
    return result;
}
